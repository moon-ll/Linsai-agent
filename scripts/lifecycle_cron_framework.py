#!/usr/bin/env python3
"""生命周期 cron 小型化与自修复框架（v6.7.5）。

把原来大而全的单一每日编排 cron 拆成：
- 每日编排 cron（只负责生成 checkpoint 与确保 worker cron 存在）
- 每个 optimizing proposal 一个 worker cron（每次只执行下一个 pending 小步骤）
- 全局修复 cron（每 6 小时扫描 stuck/failed checkpoint，自动重试并告警）

每个小步骤仍是 writer/critic/researcher 等 hermes profile 调用，
但通过 checkpoint 持久化，单点失败不会污染 lifecycle，repair 可自动恢复。

用法：
    python3 scripts/proposal_lifecycle.py --setup-cron-v2
    python3 scripts/proposal_lifecycle.py --orchestrate
    python3 scripts/proposal_lifecycle.py --worker-step <proposal_id>
    python3 scripts/proposal_lifecycle.py --repair
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time as _time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

# 从 proposal_lifecycle 导入基类与常量
from proposal_lifecycle import (
    ProposalLifecycle,
    PROPOSAL_SECTIONS,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_NO_IMPROVEMENT_LIMIT,
)

import hermes_bridge as hb

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

HERMES_SCRIPTS_DIR = Path.home() / ".hermes" / "scripts"
HERMES_PROFILE = "linsai"  # cron 统一挂在 linsai profile，便于 hermes_bridge 读取

# worker / repair / orchestrate 的默认 cron 表达式
DEFAULT_ORCHESTRATE_SCHEDULE = "55 8 * * *"
DEFAULT_WORKER_INTERVAL = "*/20 * * * *"
DEFAULT_REPAIR_SCHEDULE = "0 */6 * * *"

# checkpoint 状态
JOB_STATUS_PENDING = "pending"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_DONE = "done"
JOB_STATUS_FAILED = "failed"

# 步骤类型
STEP_CRITIC = "critic"
STEP_RESEARCHER = "researcher"
STEP_WRITER = "writer"

# stale 阈值：running 超过该秒数视为死锁
STALE_RUNNING_SECONDS = 3600

# 最大自动重试次数
MAX_JOB_ATTEMPTS = 3


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _ensure_hermes_scripts_dir() -> Path:
    HERMES_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    return HERMES_SCRIPTS_DIR


def _write_wrapper_script(name: str, content: str) -> Path:
    """把包装脚本写入 ~/.hermes/scripts/，并返回路径。"""
    _ensure_hermes_scripts_dir()
    path = HERMES_SCRIPTS_DIR / name
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)
    return path


def _dt_from_iso(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        # 兼容末尾带 Z 的 ISO
        v = value.replace("Z", "+00:00")
        return datetime.fromisoformat(v)
    except Exception:
        return None


def _is_stale(job: Dict[str, Any], stale_seconds: int = STALE_RUNNING_SECONDS) -> bool:
    if job.get("status") != JOB_STATUS_RUNNING:
        return False
    started = _dt_from_iso(job.get("started_at", ""))
    if not started:
        return True
    return (datetime.now(timezone.utc) - started).total_seconds() > stale_seconds


def _section_for_round(round_num: int) -> Dict[str, str]:
    """根据轮次确定聚焦章节（与 ProposalLifecycle.optimize_cycle 一致）。"""
    cycle = (round_num - 1) % (len(PROPOSAL_SECTIONS) + 1)
    if cycle < len(PROPOSAL_SECTIONS):
        return PROPOSAL_SECTIONS[cycle]
    return {"key": "full_review", "title": "整体一致性审查", "cn": "整体一致性", "desc": "跨章节衔接与一致性"}


def _make_job_id(proposal_id: str, round_num: int, section_key: str, step: str) -> str:
    return f"{proposal_id}-r{round_num}-{section_key}-{step}"


def _make_cron_name(job: Dict[str, Any]) -> str:
    """hermes cron 名称（短，便于 list 识别）。"""
    pid = job.get("proposal_id", "unknown")[:24]
    return f"lc-{pid}-r{job.get('round', 0)}-{job.get('section_key', 'x')}-{job.get('step', 'x')}"


def _short_uuid() -> str:
    return uuid.uuid4().hex[:8]


# ---------------------------------------------------------------------------
# CronController
# ---------------------------------------------------------------------------


class LifecycleCronController(ProposalLifecycle):
    """在 ProposalLifecycle 之上增加 checkpoint + cron 小型化调度能力。"""

    # ------------------------------------------------------------------
    # 包装脚本管理
    # ------------------------------------------------------------------

    def _write_generic_wrappers(self) -> Dict[str, Path]:
        """生成 orchestrate / repair / worker 三类通用包装脚本。"""
        project = str(PROJECT_ROOT)
        orchestrate = """#!/bin/bash
set -e
cd {project}
python3 scripts/proposal_lifecycle.py --orchestrate
""".format(project=project)

        repair = """#!/bin/bash
set -e
cd {project}
python3 scripts/proposal_lifecycle.py --repair
""".format(project=project)

        worker = """#!/bin/bash
set -e
cd {project}
SCRIPT_NAME=$(basename "$0")
PID="${{SCRIPT_NAME#lc_worker_}}"
PID="${{PID%.sh}}"
python3 scripts/proposal_lifecycle.py --worker-step "$PID"
""".format(project=project)

        return {
            "orchestrate": _write_wrapper_script("lc_orchestrate.sh", orchestrate),
            "repair": _write_wrapper_script("lc_repair.sh", repair),
            "worker": _write_wrapper_script("lc_worker.sh", worker),
        }

    def _worker_script_for_proposal(self, proposal_id: str) -> Path:
        """为具体 proposal 复制 worker 包装脚本（脚本名携带 proposal_id）。"""
        self._write_generic_wrappers()
        script_name = f"lc_worker_{proposal_id}.sh"
        target = HERMES_SCRIPTS_DIR / script_name
        source = HERMES_SCRIPTS_DIR / "lc_worker.sh"
        if not source.exists():
            self._write_generic_wrappers()
        shutil.copy2(source, target)
        target.chmod(0o755)
        return target

    # ------------------------------------------------------------------
    # Checkpoint 管理
    # ------------------------------------------------------------------

    def _get_jobs(self, proposal_id: str) -> List[Dict[str, Any]]:
        state = self._get_proposal_state(proposal_id)
        if not state:
            return []
        return state.get("pipeline_jobs", [])

    def _save_jobs(self, proposal_id: str, jobs: List[Dict[str, Any]]) -> bool:
        state = self._load_state()
        if proposal_id not in state.get("proposals", {}):
            return False
        state["proposals"][proposal_id]["pipeline_jobs"] = jobs
        state["proposals"][proposal_id]["updated_at"] = now_utc()
        self._save_state(state)
        return True

    def _job_by_id(self, jobs: List[Dict[str, Any]], job_id: str) -> Optional[Dict[str, Any]]:
        for j in jobs:
            if j.get("job_id") == job_id:
                return j
        return None

    def _build_next_round_jobs(
        self,
        proposal_id: str,
        round_num: int,
        section: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """为下一轮生成 critic + writer 两个基础 job。"""
        section_key = section["key"]
        critic_id = _make_job_id(proposal_id, round_num, section_key, STEP_CRITIC)
        writer_id = _make_job_id(proposal_id, round_num, section_key, STEP_WRITER)
        return [
            {
                "job_id": critic_id,
                "proposal_id": proposal_id,
                "step": STEP_CRITIC,
                "section_key": section_key,
                "round": round_num,
                "status": JOB_STATUS_PENDING,
                "depends_on": [],
                "attempts": 0,
                "scheduled_at": "",
                "started_at": "",
                "finished_at": "",
                "last_error": "",
                "cron_job_id": "",
            },
            {
                "job_id": writer_id,
                "proposal_id": proposal_id,
                "step": STEP_WRITER,
                "section_key": section_key,
                "round": round_num,
                "status": JOB_STATUS_PENDING,
                "depends_on": [critic_id],
                "attempts": 0,
                "scheduled_at": "",
                "started_at": "",
                "finished_at": "",
                "last_error": "",
                "cron_job_id": "",
            },
        ]

    def sync_checkpoint(self, proposal_id: str) -> Dict[str, Any]:
        """为指定 proposal 补齐下一轮的 checkpoint。幂等。"""
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal 未注册"}

        if prop_state.get("status") != "optimizing":
            return {"success": True, "reason": "不在优化中，无需 checkpoint", "added": 0}

        jobs = self._get_jobs(proposal_id)
        current_round = prop_state.get("optimization_rounds", 0)
        next_round = current_round + 1

        # 如果已经达到最大轮数或已达标，不需要新 checkpoint
        # （writer 完成后会负责 transition）
        if current_round >= DEFAULT_MAX_ROUNDS:
            return {"success": True, "reason": "已达最大轮数", "added": 0}

        section = _section_for_round(next_round)
        needed = self._build_next_round_jobs(proposal_id, next_round, section)

        added = 0
        for job in needed:
            if not self._job_by_id(jobs, job["job_id"]):
                jobs.append(job)
                added += 1

        if added:
            self._save_jobs(proposal_id, jobs)

        return {"success": True, "proposal_id": proposal_id, "next_round": next_round, "added": added}

    # ------------------------------------------------------------------
    # 单步执行
    # ------------------------------------------------------------------

    def pick_next_job(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """挑选下一个可执行的 pending job（同一 proposal 串行）。"""
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state or prop_state.get("status") != "optimizing":
            return None

        jobs = self._get_jobs(proposal_id)
        if not jobs:
            return None

        # 若有 running 任务，先检查是否 stale
        for job in jobs:
            if job.get("status") == JOB_STATUS_RUNNING and _is_stale(job):
                if _log:
                    _log.warning(f"[{proposal_id}] job {job['job_id']} 运行超 {STALE_RUNNING_SECONDS}s，标记失败")
                job["status"] = JOB_STATUS_FAILED
                job["finished_at"] = now_utc()
                job["last_error"] = "运行超时/进程僵死"
                job["attempts"] = job.get("attempts", 0) + 1
                self._save_jobs(proposal_id, jobs)
                break  # 只处理一个 stale，让下次调用继续

        # 重新加载，找第一个依赖满足且 pending 的 job
        jobs = self._get_jobs(proposal_id)
        done_ids = {j["job_id"] for j in jobs if j.get("status") == JOB_STATUS_DONE}
        running = [j for j in jobs if j.get("status") == JOB_STATUS_RUNNING]
        if running:
            return None  # 串行：有任务在跑就等待

        for job in jobs:
            if job.get("status") != JOB_STATUS_PENDING:
                continue
            deps = job.get("depends_on", [])
            if all(d in done_ids for d in deps):
                return job
        return None

    def _update_job(self, proposal_id: str, job: Dict[str, Any], status: str, error: str = "") -> None:
        jobs = self._get_jobs(proposal_id)
        existing = self._job_by_id(jobs, job["job_id"])
        if not existing:
            return
        existing["status"] = status
        existing["finished_at"] = now_utc() if status in (JOB_STATUS_DONE, JOB_STATUS_FAILED) else ""
        if status == JOB_STATUS_RUNNING:
            existing["started_at"] = now_utc()
        if error:
            existing["last_error"] = error[:500]
        if status == JOB_STATUS_FAILED:
            existing["attempts"] = existing.get("attempts", 0) + 1
        self._save_jobs(proposal_id, jobs)

    def _read_critic_report(self, prop_dir: Path, round_num: int) -> Dict[str, Any]:
        """读取指定轮次的 critic 报告并解析分数。"""
        report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
        if not report_path.exists():
            return {"output": "", "score": 0.0, "dim_scores": {}, "issues": []}
        text = report_path.read_text(encoding="utf-8")
        file_result = {"output": text}
        return {
            "output": text,
            "score": self._extract_score(file_result),
            "dim_scores": self._extract_dimension_scores(file_result),
            "issues": self._extract_issues(file_result),
        }

    def _run_critic_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
        """执行 critic 步骤，并在需要时插入 researcher job。"""
        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}

        prop_state = self._get_proposal_state(proposal_id)
        project_type = prop_state.get("project_type", "general")
        round_num = job["round"]
        section = _section_for_round(round_num)
        focus_section = section if section["key"] != "full_review" else None
        is_full_review = section["key"] == "full_review"

        result = self._run_critic(
            proposal_id, prop_dir, project_type, round_num, 300,
            focus_section=focus_section, is_full_review=is_full_review,
        )
        if not result.get("success"):
            return {"success": False, "error": result.get("error", "critic 失败")}

        # 等待报告落盘
        report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
        if not (report_path.exists() and report_path.stat().st_size > 100):
            self._wait_for_critic_report(report_path, timeout=30)

        # 解析报告，决定是否需要 researcher
        report = self._read_critic_report(prop_dir, round_num)
        if report["dim_scores"].get("rigor", 1.0) < 0.70 or self._has_lit_gap({"output": report["output"]}):
            self._insert_researcher_job(proposal_id, round_num, section["key"])

        return {"success": True, "score": report["score"]}

    def _insert_researcher_job(self, proposal_id: str, round_num: int, section_key: str) -> None:
        """在 critic 与 writer 之间插入 researcher job。幂等。"""
        jobs = self._get_jobs(proposal_id)
        writer_id = _make_job_id(proposal_id, round_num, section_key, STEP_WRITER)
        researcher_id = _make_job_id(proposal_id, round_num, section_key, STEP_RESEARCHER)
        if self._job_by_id(jobs, researcher_id):
            return
        # 找到 writer job，把 researcher 插入它前面
        writer_idx = None
        for i, j in enumerate(jobs):
            if j["job_id"] == writer_id:
                writer_idx = i
                break
        researcher_job = {
            "job_id": researcher_id,
            "proposal_id": proposal_id,
            "step": STEP_RESEARCHER,
            "section_key": section_key,
            "round": round_num,
            "status": JOB_STATUS_PENDING,
            "depends_on": [_make_job_id(proposal_id, round_num, section_key, STEP_CRITIC)],
            "attempts": 0,
            "scheduled_at": "",
            "started_at": "",
            "finished_at": "",
            "last_error": "",
            "cron_job_id": "",
        }
        if writer_idx is not None:
            jobs.insert(writer_idx, researcher_job)
            # writer 依赖 researcher
            jobs[writer_idx + 1]["depends_on"].append(researcher_id)
            # 去重
            jobs[writer_idx + 1]["depends_on"] = list(dict.fromkeys(jobs[writer_idx + 1]["depends_on"]))
        else:
            jobs.append(researcher_job)
        self._save_jobs(proposal_id, jobs)

    def _run_researcher_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}
        round_num = job["round"]
        section = _section_for_round(round_num)
        focus_section = section if section["key"] != "full_review" else None
        report = self._read_critic_report(prop_dir, round_num)
        critic_result = {"output": report["output"], "success": True}
        lit = self._run_researcher_targeted(
            proposal_id, prop_dir, critic_result, focus_section, timeout=300
        )
        return {"success": bool(lit), "lit_path": lit}

    def _run_writer_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
        """执行 writer 并更新 lifecycle 状态（轮次、分数、section_passes）。"""
        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}

        prop_state = self._get_proposal_state(proposal_id)
        project_type = prop_state.get("project_type", "general")
        round_num = job["round"]
        section = _section_for_round(round_num)
        section_key = section["key"]
        focus_section = section if section_key != "full_review" else None
        is_full_review = section_key == "full_review"
        threshold = self._get_quality_threshold(project_type)

        # 读取本轮 critic 报告
        report = self._read_critic_report(prop_dir, round_num)
        dim_scores = report["dim_scores"]
        weakest_dim = self._get_weakest_dimension(dim_scores)

        # 构造 lit_supplement：使用本 proposal 下 targeted-research 目录最新文件
        lit_supplement = ""
        targeted_dir = prop_dir / "02_literature" / "targeted-research"
        if targeted_dir.exists():
            lit_files = sorted(targeted_dir.glob("lit-gap-*.md"), reverse=True)
            if lit_files:
                lit_supplement = (
                    f"\n【文献补充（researcher 定向检索）】\n"
                    f"请参考 {lit_files[0]} 中的新文献，在修订时引用。\n"
                )

        writer_result = self._run_writer_optimize(
            proposal_id, prop_dir, project_type,
            critic_result={"output": report["output"]},
            timeout=600,
            weakest_dim=weakest_dim,
            dim_scores=dim_scores,
            focus_section=focus_section,
            is_full_review=is_full_review,
            lit_supplement=lit_supplement,
        )
        if not writer_result.get("success"):
            return {"success": False, "error": writer_result.get("error", "writer 失败")}

        # 重新读取报告计算分数（writer 不应修改 critic 报告）
        report = self._read_critic_report(prop_dir, round_num)
        score_after = report["score"]
        dim_scores = report["dim_scores"]
        weakest_dim = self._get_weakest_dimension(dim_scores)
        issues = report["issues"]

        min_score = threshold.get("min_overall_score", 0.80)
        weak_dims = [k for k, floor in self.DIMENSION_FLOOR.items() if k in dim_scores and dim_scores[k] < floor]
        section_passed = score_after >= min_score and len(weak_dims) == 0

        score_before = prop_state.get("last_score", 0.0)

        # 更新 proposal 状态
        prop_state = self._get_proposal_state(proposal_id)
        prop_state["optimization_rounds"] = round_num
        prop_state["last_score"] = score_after
        prop_state["last_dim_scores"] = dim_scores
        section_passes = prop_state.get("section_passes", {})
        section_passes[section_key] = section_passed
        prop_state["section_passes"] = section_passes
        prop_state["score_history"].append({
            "round": round_num,
            "score": score_after,
            "dim_scores": dim_scores,
            "weakest_dim": weakest_dim,
            "focus_section": section_key,
            "section_passed": section_passed,
            "issues_count": len(issues),
            "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
            "at": now_utc(),
        })
        prop_state["updated_at"] = now_utc()
        self._set_proposal_state(proposal_id, prop_state)

        try:
            self.update_proposal_brief(proposal_id)
        except Exception:
            pass

        # 检查是否达标并流转
        done_result = self._check_done(proposal_id, threshold)
        if done_result["done"]:
            self.transition(proposal_id, "pending_review", reason=done_result["reason"])

        return {
            "success": True,
            "round": round_num,
            "score_before": score_before,
            "score_after": score_after,
            "done": done_result["done"],
            "reason": done_result["reason"],
        }

    def execute_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """执行一个 checkpoint job（不获取锁，调用方负责锁）。"""
        proposal_id = job["proposal_id"]
        step = job["step"]
        if _log:
            _log.info(f"[{proposal_id}] 执行 job {job['job_id']} ({step})")

        self._update_job(proposal_id, job, JOB_STATUS_RUNNING)

        try:
            if step == STEP_CRITIC:
                result = self._run_critic_step(proposal_id, job)
            elif step == STEP_RESEARCHER:
                result = self._run_researcher_step(proposal_id, job)
            elif step == STEP_WRITER:
                result = self._run_writer_step(proposal_id, job)
            else:
                result = {"success": False, "error": f"未知步骤 {step}"}
        except Exception as e:
            result = {"success": False, "error": str(e)}

        if result.get("success"):
            self._update_job(proposal_id, job, JOB_STATUS_DONE)
            # writer 完成后可能需要为下一轮生成 checkpoint
            if step == STEP_WRITER:
                self.sync_checkpoint(proposal_id)
        else:
            self._update_job(proposal_id, job, JOB_STATUS_FAILED, result.get("error", ""))

        if _log:
            _log.info(
                f"[{proposal_id}] job {job['job_id']} 完成: "
                f"success={result.get('success')} error={result.get('error', '')[:80]}"
            )
        return result

    def execute_next_job(self, proposal_id: str) -> Dict[str, Any]:
        """worker 入口：加锁、挑选并执行下一个 job。"""
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal 未注册"}
        if prop_state.get("status") != "optimizing":
            return {"success": False, "error": f"proposal 不在优化中（当前: {prop_state['status']}）"}

        # 先补齐 checkpoint
        self.sync_checkpoint(proposal_id)

        with file_lock(f"proposal-{proposal_id}"):
            job = self.pick_next_job(proposal_id)
            if not job:
                return {"success": True, "reason": "无待执行 job", "executed": False}
            result = self.execute_job(job)
            result["executed"] = True
            result["job_id"] = job["job_id"]
            return result

    # ------------------------------------------------------------------
    # 调度层
    # ------------------------------------------------------------------

    def _lifecycle_cron_prefix(self) -> str:
        return "lc-"

    def list_lifecycle_crons(self) -> List[Dict[str, Any]]:
        """列出当前 hermes 中所有 lc- 开头的 cron job。"""
        jobs = hb.cron_list_profile(HERMES_PROFILE)
        return [j for j in jobs if j.get("name", "").startswith(self._lifecycle_cron_prefix())]

    def schedule_worker(self, proposal_id: str, interval: str = DEFAULT_WORKER_INTERVAL) -> Dict[str, Any]:
        """为 proposal 创建/更新 worker cron。幂等（按名称去重）。"""
        script_path = self._worker_script_for_proposal(proposal_id)
        name = f"lc-worker-{proposal_id}"
        # 先检查是否已存在 active
        existing = self.list_lifecycle_crons()
        for job in existing:
            if job.get("name") == name and job.get("status") == "active":
                return {"success": True, "message": "worker 已存在", "cron_job_id": job.get("id")}

        result = hb.cron_create_no_agent(
            script_name=script_path.name,
            name=name,
            schedule=interval,
            workdir=str(PROJECT_ROOT),
            profile=HERMES_PROFILE,
        )
        return result

    def remove_worker(self, proposal_id: str) -> Dict[str, Any]:
        name = f"lc-worker-{proposal_id}"
        existing = self.list_lifecycle_crons()
        for job in existing:
            if job.get("name") == name:
                return hb.cron_delete(job.get("id"), profile=HERMES_PROFILE)
        return {"success": True, "message": "worker 不存在"}

    def run_orchestrator(self) -> Dict[str, Any]:
        """每日编排：生成 checkpoint + 确保每个 optimizing proposal 有 worker。"""
        if _log:
            _log.info("=== 每日编排器（v2）启动 ===")

        health_before = self.run_health_check()
        target_proposals = self.match_proposals_with_brief()

        optimizing = self.list_by_status("optimizing")
        # 文献匹配只是优先级提示，v2 仍保证所有 optimizing 都有 worker
        results = []
        workers_created = 0
        checkpoints_added = 0

        for prop in optimizing:
            pid = prop["proposal_id"]
            try:
                cp = self.sync_checkpoint(pid)
                checkpoints_added += cp.get("added", 0)
                wr = self.schedule_worker(pid)
                if wr.get("cron_job_id"):
                    workers_created += 1
                results.append({
                    "proposal_id": pid,
                    "checkpoint": cp,
                    "worker": wr,
                    "priority": pid in target_proposals,
                })
            except Exception as e:
                if _log:
                    _log.error(f"[orchestrate] {pid} 处理失败: {e}")
                results.append({"proposal_id": pid, "error": str(e)})

        health_after = self.run_health_check()

        summary = {
            "orchestrated_at": now_utc(),
            "optimizing_count": len(optimizing),
            "target_count": len(target_proposals),
            "workers_created": workers_created,
            "checkpoints_added": checkpoints_added,
            "health_before": {"healthy": health_before["healthy"], "alerts": len(health_before["alerts"])},
            "health_after": {"healthy": health_after["healthy"], "alerts": len(health_after["alerts"])},
            "results": results,
        }
        if _log:
            _log.info(
                f"每日编排器完成: optimizing={len(optimizing)} "
                f"workers={workers_created} checkpoints_added={checkpoints_added}"
            )
        return summary

    def run_repair(self, dry_run: bool = False) -> Dict[str, Any]:
        """修复 cron：扫描 stuck/failed checkpoint 与缺失 worker。"""
        if _log:
            _log.info(f"=== 修复扫描（dry_run={dry_run}）===")

        optimizing = self.list_by_status("optimizing")
        lifecycle_crons = self.list_lifecycle_crons()
        active_worker_names = {
            j["name"] for j in lifecycle_crons
            if j.get("name", "").startswith("lc-worker-") and j.get("status") == "active"
        }

        repaired = []
        for prop in optimizing:
            pid = prop["proposal_id"]
            item = {"proposal_id": pid, "actions": []}
            try:
                # 1. 同步 checkpoint
                if not dry_run:
                    self.sync_checkpoint(pid)

                # 2. 检查 worker cron 是否存在且 active
                worker_name = f"lc-worker-{pid}"
                if worker_name not in active_worker_names:
                    if not dry_run:
                        self.schedule_worker(pid)
                        item["actions"].append(" recreated worker cron")
                    else:
                        item["actions"].append(" missing worker cron (dry-run)")

                # 3. 处理 stuck / failed jobs
                jobs = self._get_jobs(pid)
                for job in jobs:
                    if _is_stale(job):
                        if not dry_run:
                            self._update_job(pid, job, JOB_STATUS_FAILED, "运行超时/进程僵死")
                        item["actions"].append(f" stale job {job['job_id']} -> failed")
                    elif job.get("status") == JOB_STATUS_FAILED and job.get("attempts", 0) < MAX_JOB_ATTEMPTS:
                        # 重置为 pending，worker 下次会重试
                        if not dry_run:
                            job["status"] = JOB_STATUS_PENDING
                            job["started_at"] = ""
                            job["finished_at"] = ""
                            job["last_error"] = ""
                            self._save_jobs(pid, jobs)
                        item["actions"].append(f" retry job {job['job_id']} (attempt {job.get('attempts', 0)})")
                    elif job.get("status") == JOB_STATUS_FAILED and job.get("attempts", 0) >= MAX_JOB_ATTEMPTS:
                        item["actions"].append(f" job {job['job_id']} 超过重试次数，需人工介入")
                        # 记录到 cron_failures 供 health_check 告警
                        if not dry_run:
                            self._record_cron_failure(pid, f"{job['job_id']}: {job.get('last_error', '')}")
            except Exception as e:
                item["actions"].append(f" error: {e}")
            repaired.append(item)

        # 4. 清理已不在 optimizing 状态的 worker cron
        optimizing_ids = {p["proposal_id"] for p in optimizing}
        for cron in lifecycle_crons:
            name = cron.get("name", "")
            if name.startswith("lc-worker-"):
                pid = name[len("lc-worker-"):]
                if pid not in optimizing_ids:
                    if not dry_run:
                        hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
                    repaired.append({"proposal_id": pid, "actions": ["removed stale worker cron"]})

        return {"success": True, "dry_run": dry_run, "repaired": repaired, "at": now_utc()}

    # ------------------------------------------------------------------
    # 安装 / 卸载
    # ------------------------------------------------------------------

    def setup_cron_framework(
        self,
        orchestrate_schedule: str = DEFAULT_ORCHESTRATE_SCHEDULE,
        worker_interval: str = DEFAULT_WORKER_INTERVAL,
        repair_schedule: str = DEFAULT_REPAIR_SCHEDULE,
    ) -> Dict[str, Any]:
        """安装 v2 cron 框架：删除旧单一 cron，创建 orchestrate + repair + workers。"""
        self._write_generic_wrappers()

        # 删除旧的大 cron（兼容 v6.7.4 及之前）
        old_names = ["每日提案系统编排", "每日编排"]
        removed = []
        for cron in hb.cron_list_profile(HERMES_PROFILE):
            if cron.get("name") in old_names:
                hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
                removed.append(cron.get("name"))

        # orchestrate cron
        orch = hb.cron_create_no_agent(
            script_name="lc_orchestrate.sh",
            name="lc-daily-orchestrate",
            schedule=orchestrate_schedule,
            workdir=str(PROJECT_ROOT),
            profile=HERMES_PROFILE,
        )

        # repair cron
        rep = hb.cron_create_no_agent(
            script_name="lc_repair.sh",
            name="lc-repair",
            schedule=repair_schedule,
            workdir=str(PROJECT_ROOT),
            profile=HERMES_PROFILE,
        )

        # 立即执行一次 orchestrate，确保当天 worker 就位
        orch_now = self.run_orchestrator()

        return {
            "success": orch.get("success") and rep.get("success"),
            "removed_old": removed,
            "orchestrate": orch,
            "repair": rep,
            "first_orchestrate": orch_now,
        }

    def teardown_cron_framework(self) -> Dict[str, Any]:
        """卸载所有 lc- 开头的 lifecycle cron。"""
        removed = []
        for cron in self.list_lifecycle_crons():
            res = hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
            if res.get("success"):
                removed.append(cron.get("name"))
        return {"success": True, "removed": removed}


# ---------------------------------------------------------------------------
# 便捷入口（供测试/import）
# ---------------------------------------------------------------------------


def get_controller() -> LifecycleCronController:
    return LifecycleCronController()
