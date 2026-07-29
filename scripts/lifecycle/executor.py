#!/usr/bin/env python3
"""生命周期 cron 框架单步执行器。"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import file_lock, now_utc

from .constants import (
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    STALE_RUNNING_SECONDS,
    STEP_CRITIC,
    STEP_MONITOR,
    STEP_RESEARCHER,
    STEP_WRITER,
)
from .utils import _is_stale, _make_job_id, _section_for_round

try:
    from adversarial_governance import AdversarialGovernance
except Exception:
    AdversarialGovernance = None  # type: ignore[misc,assignment]

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


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
        proposal_id, prop_dir, project_type, round_num, 900,
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
        proposal_id, prop_dir, critic_result, focus_section, timeout=900
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

    # v6.7.6: writer 修改前备份当前申请书，供 monitor 比对
    proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
    backup_path = prop_dir / "04_proposal" / f"proposal-draft-r{round_num - 1}.md"
    if proposal_path.exists() and proposal_path.stat().st_size > 100:
        try:
            shutil.copy2(str(proposal_path), str(backup_path))
        except Exception:
            pass

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
        timeout=900,
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

    # 更新 proposal 状态（writer 只记录本轮输出质量，不推进轮次；轮次在 monitor 收尾后推进）
    prop_state = self._get_proposal_state(proposal_id)
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

    # v6.7.6: 达标判定与流转移至 monitor 步骤，由 monitor 综合评估后决定
    return {
        "success": True,
        "round": round_num,
        "score_before": score_before,
        "score_after": score_after,
        "section_passed": section_passed,
    }

def _run_monitor_step(self, proposal_id: str, job: Dict[str, Any]) -> Dict[str, Any]:
    """执行 monitor（全局监察）步骤：评分、奖惩、达标判定、流转。

    v6.7.6: monitor 作为每轮 writer-critic 之后的收尾步骤，独立评估质量，
    更新 agent 分数，检测负反馈，最终决定是否达标并移入 pending_review。
    """
    if AdversarialGovernance is None:
        if _log:
            _log.warning(f"[{proposal_id}] adversarial_governance 未加载，monitor 跳过")
        # 降级处理：虽未启用监察模块，仍推进轮次，避免链路僵死
        prop_state = self._get_proposal_state(proposal_id)
        if prop_state:
            prop_state["optimization_rounds"] = max(
                prop_state.get("optimization_rounds", 0), round_num
            )
            prop_state["last_monitor_assessment"] = "adversarial_governance 未加载，monitor 跳过"
            prop_state["updated_at"] = now_utc()
            self._set_proposal_state(proposal_id, prop_state)
        return {"success": True, "skipped": True, "reason": "adversarial_governance 未加载"}

    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    prop_state = self._get_proposal_state(proposal_id)
    if not prop_state:
        return {"success": False, "error": "proposal 状态不存在"}

    project_type = prop_state.get("project_type", "general")
    round_num = job["round"]
    section_key = job["section_key"]
    section = _section_for_round(round_num)
    section_name = section.get("cn", section_key)

    score_after = prop_state.get("last_score", 0.0)
    dim_scores = prop_state.get("last_dim_scores", {})

    # 找上一轮的 score 作为 score_before
    score_before = 0.0
    score_history = prop_state.get("score_history", [])
    for h in reversed(score_history[:-1]):
        if h.get("round") < round_num:
            score_before = h.get("score", 0.0)
            break

    # 找 writer 修改前的备份文件作为 prev_draft
    prev_draft_path = prop_dir / "04_proposal" / f"proposal-draft-r{round_num - 1}.md"
    if not prev_draft_path.exists():
        prev_draft_path = None

    ag = AdversarialGovernance()
    monitor_result = ag.run_monitor_step(
        proposal_id=proposal_id,
        prop_dir=prop_dir,
        project_type=project_type,
        round_num=round_num,
        section_key=section_key,
        section_name=section_name,
        score_before=score_before,
        score_after=score_after,
        dim_scores=dim_scores,
        prev_draft_path=prev_draft_path,
    )

    if not monitor_result.get("success"):
        return {
            "success": False,
            "error": monitor_result.get("error", "monitor 调用失败"),
            "monitor_result": monitor_result,
        }

    deltas = ag.apply_monitor_result(
        proposal_id=proposal_id,
        round_num=round_num,
        section_key=section_key,
        score_before=score_before,
        score_after=score_after,
        dim_scores=dim_scores,
        monitor_result=monitor_result,
        proposal_state=prop_state,
    )

    prop_state = ag.record_monitor_history(
        proposal_state=prop_state,
        round_num=round_num,
        section_key=section_key,
        score_before=score_before,
        score_after=score_after,
        monitor_result=monitor_result,
        deltas=deltas,
    )

    # 本轮完整闭环结束，推进轮次（负反馈告警时除外）
    if not prop_state.get("negative_feedback_alert"):
        prop_state["optimization_rounds"] = max(
            prop_state.get("optimization_rounds", 0), round_num
        )

    # 写入 monitor 简要摘要到 proposal 状态
    prop_state["last_monitor_at"] = now_utc()
    prop_state["last_monitor_score"] = monitor_result.get("monitor_independent_score", score_after)
    prop_state["last_monitor_assessment"] = monitor_result.get("overall_assessment", "")[:300]
    self._set_proposal_state(proposal_id, prop_state)

    # 负反馈告警：不流转，等待人工介入
    if prop_state.get("negative_feedback_alert"):
        reasons = prop_state.get("negative_feedback_reasons", [])
        if _log:
            _log.warning(
                f"[{proposal_id}] 触发负反馈告警: {', '.join(reasons)}; "
                f"暂停自动流转，等待人工清除"
            )
        return {
            "success": True,
            "negative_feedback_alert": True,
            "reasons": reasons,
            "writer_delta": deltas.get("writer_delta"),
            "critic_delta": deltas.get("critic_delta"),
            "monitor_score": monitor_result.get("monitor_independent_score"),
        }

    # 未触发负反馈：检查是否达标并流转
    threshold = self._get_quality_threshold(project_type)
    done_result = self._check_done(proposal_id, threshold)
    if done_result["done"]:
        transition_result = self.transition(
            proposal_id, "pending_review", reason=done_result["reason"]
        )
        return {
            "success": True,
            "done": True,
            "reason": done_result["reason"],
            "transition": transition_result,
            "writer_delta": deltas.get("writer_delta"),
            "critic_delta": deltas.get("critic_delta"),
            "monitor_score": monitor_result.get("monitor_independent_score"),
        }

    return {
        "success": True,
        "done": False,
        "reason": done_result.get("reason", "未达标"),
        "writer_delta": deltas.get("writer_delta"),
        "critic_delta": deltas.get("critic_delta"),
        "monitor_score": monitor_result.get("monitor_independent_score"),
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
        elif step == STEP_MONITOR:
            result = self._run_monitor_step(proposal_id, job)
        else:
            result = {"success": False, "error": f"未知步骤 {step}"}
    except Exception as e:
        result = {"success": False, "error": str(e)}

    if result.get("success"):
        self._update_job(proposal_id, job, JOB_STATUS_DONE)
        # monitor 是每轮完整闭环的收尾步骤；只有 monitor 成功后，
        # 才推进 optimization_rounds 并生成下一轮 checkpoint。
        if step == STEP_MONITOR and not result.get("negative_feedback_alert"):
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
