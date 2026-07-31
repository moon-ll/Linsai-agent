#!/usr/bin/env python3
"""生命周期 cron 框架编排与修复。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import hermes_bridge as hb
from common import now_utc

from proposal_lifecycle import DEFAULT_MAX_ROUNDS

from .constants import (
    HERMES_PROFILE,
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    MAX_JOB_ATTEMPTS,
    STEP_CRITIC,
    STEP_MONITOR,
    STEP_WRITER,
    WEEKEND_JOBS,
)
from .utils import _is_stale, _is_weekend, _load_weekend_jobs, _make_job_id, _save_weekend_jobs

from weekend_pipeline.state import load_pipeline_state, save_pipeline_state
from weekend_pipeline.executor import repair_stale_and_failed as repair_weekend_pipeline

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


def _compute_actual_round(self, proposal_id: str, jobs: List[Dict[str, Any]]) -> int:
    """v6.8.0: 根据已完成的 job 计算实际闭环轮次，修复 optimization_rounds 滞后。

    从当前 optimization_rounds+1 开始向上扫描，若某轮全部 25 个 job 都 done，
    则认为该轮已闭环。返回应推进到的轮次。
    """
    prop_state = self._get_proposal_state(proposal_id)
    current_round = prop_state.get("optimization_rounds", 0) if prop_state else 0
    if not jobs:
        return current_round

    actual = current_round
    round_num = current_round + 1
    # 安全上限：避免无限制扫描
    while round_num <= current_round + 20:
        expected_jobs = self._build_full_round_jobs(proposal_id, round_num)
        expected_ids = {j["job_id"] for j in expected_jobs}
        statuses = {
            job["job_id"]: job.get("status")
            for job in jobs
            if job["job_id"] in expected_ids
        }
        if len(statuses) == len(expected_ids) and all(s == JOB_STATUS_DONE for s in statuses.values()):
            actual = round_num
            round_num += 1
        else:
            break
    return actual


def sync_checkpoint(self, proposal_id: str) -> Dict[str, Any]:
    """为指定 proposal 补齐下一轮的 checkpoint。幂等。

    v6.7.12: 新增对 optimization_rounds 滞后的自动修复。
    当负反馈告警被清除后，pipeline_jobs 中可能已有更高轮次完成，
    但 optimization_rounds 未推进，导致无法生成新 checkpoint。
    """
    prop_state = self._get_proposal_state(proposal_id)
    if not prop_state:
        return {"success": False, "error": "proposal 未注册"}

    if prop_state.get("status") != "optimizing":
        return {"success": True, "reason": "不在优化中，无需 checkpoint", "added": 0}

    jobs = self._get_jobs(proposal_id)

    # v6.7.12: 修复 optimization_rounds 滞后
    actual_round = self._compute_actual_round(proposal_id, jobs)
    current_round = prop_state.get("optimization_rounds", 0)
    round_advanced = False
    if actual_round > current_round:
        prop_state["optimization_rounds"] = actual_round
        current_round = actual_round
        round_advanced = True
        if _log:
            _log.info(f"[{proposal_id}] checkpoint 修复: optimization_rounds 推进到 {actual_round}")
        self._set_proposal_state(proposal_id, prop_state)
        # 重新加载 jobs（_set_proposal_state 可能并发修改）
        jobs = self._get_jobs(proposal_id)

    next_round = current_round + 1

    # 如果已经达到最大轮数或已达标，不需要新 checkpoint
    # （writer 完成后会负责 transition）
    if current_round >= DEFAULT_MAX_ROUNDS:
        return {"success": True, "reason": "已达最大轮数", "added": 0, "round_advanced": round_advanced}

    needed = self._build_full_round_jobs(proposal_id, next_round)

    added = 0
    for job in needed:
        if not self._job_by_id(jobs, job["job_id"]):
            jobs.append(job)
            added += 1

    if added:
        self._save_jobs(proposal_id, jobs)

    return {
        "success": True,
        "proposal_id": proposal_id,
        "next_round": next_round,
        "added": added,
        "round_advanced": round_advanced,
    }


def run_orchestrator(self) -> Dict[str, Any]:
    """每日编排（v6.7.12）：生成 checkpoint + 确保全局微调度器就位。

    v6.7.12 起不再为每个 proposal 创建独立 worker，而是使用单一全局
    微调度器每 5 分钟扫描并执行一个最优先的 pending job。
    """
    if _log:
        _log.info("=== 每日编排器（v6.7.12）启动 ===")

    health_before = self.run_health_check()
    target_proposals = self.match_proposals_with_brief()

    optimizing = self.list_by_status("optimizing")
    results = []
    checkpoints_added = 0

    for prop in optimizing:
        pid = prop["proposal_id"]
        try:
            cp = self.sync_checkpoint(pid)
            checkpoints_added += cp.get("added", 0)
            results.append({
                "proposal_id": pid,
                "checkpoint": cp,
                "priority": pid in target_proposals,
            })
        except Exception as e:
            if _log:
                _log.error(f"[orchestrate] {pid} 处理失败: {e}")
            results.append({"proposal_id": pid, "error": str(e)})

    # 确保全局微调度器存在
    scheduler_ok = True
    scheduler_msg = "微调度器已存在"
    try:
        existing = {
            c.get("name") for c in self.list_lifecycle_crons()
            if c.get("status") == "active"
        }
        if "lc-micro-scheduler" not in existing:
            res = self.schedule_micro_scheduler()
            scheduler_ok = res.get("success", False)
            scheduler_msg = res.get("message", "unknown")
    except Exception as e:
        scheduler_ok = False
        scheduler_msg = str(e)

    # 暂停旧的 per-proposal worker，避免与微调度器并发
    try:
        pause_res = self.pause_old_worker_crons()
        paused_workers = pause_res.get("paused", [])
    except Exception as e:
        paused_workers = []
        if _log:
            _log.warning(f"[orchestrate] 暂停旧 worker 失败: {e}")

    health_after = self.run_health_check()

    summary = {
        "orchestrated_at": now_utc(),
        "optimizing_count": len(optimizing),
        "target_count": len(target_proposals),
        "checkpoints_added": checkpoints_added,
        "scheduler_ok": scheduler_ok,
        "scheduler_message": scheduler_msg,
        "paused_workers": paused_workers,
        "health_before": {"healthy": health_before["healthy"], "alerts": len(health_before["alerts"])},
        "health_after": {"healthy": health_after["healthy"], "alerts": len(health_after["alerts"])},
        "results": results,
    }
    if _log:
        _log.info(
            f"每日编排器完成: optimizing={len(optimizing)} "
            f"checkpoints_added={checkpoints_added} "
            f"scheduler_ok={scheduler_ok} paused_workers={len(paused_workers)}"
        )
    return summary

def run_repair(self, dry_run: bool = False) -> Dict[str, Any]:
    """修复 cron：扫描 stuck/failed checkpoint 与缺失 worker。

    v6.7.7: 区分工作日与周末。
    - 工作日：扫描 optimizing proposal worker jobs。
    - 周末：扫描 weekend_input/output/reflection 任务状态，并修复周末 cron。
    """
    if _log:
        _log.info(f"=== 修复扫描（dry_run={dry_run}, weekend={_is_weekend()}）===")

    lifecycle_crons = self.list_lifecycle_crons()

    # 周末模式：扫描周末任务
    if _is_weekend():
        return self._run_weekend_repair(dry_run=dry_run, lifecycle_crons=lifecycle_crons)

    # 工作日模式（v6.7.12）：确保微调度器 + 清理旧 worker + 修复 jobs
    optimizing = self.list_by_status("optimizing")

    # 1. 确保全局微调度器存在
    scheduler_action = ""
    active_names = {c.get("name") for c in lifecycle_crons if c.get("status") == "active"}
    if "lc-micro-scheduler" not in active_names:
        if not dry_run:
            res = self.schedule_micro_scheduler()
            scheduler_action = f"created micro-scheduler: {res.get('message', '')}"
        else:
            scheduler_action = "missing micro-scheduler (dry-run)"
    else:
        scheduler_action = "micro-scheduler ok"

    repaired = [{"proposal_id": "_scheduler", "actions": [scheduler_action]}]

    # 2. 清理已不在 optimizing 状态或多余的 lc-worker-* cron
    optimizing_ids = {p["proposal_id"] for p in optimizing}
    removed_workers = []
    for cron in lifecycle_crons:
        name = cron.get("name", "")
        if name.startswith("lc-worker-"):
            pid = name[len("lc-worker-"):]
            if pid not in optimizing_ids:
                if not dry_run:
                    hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
                removed_workers.append(name)
    if removed_workers:
        repaired.append({"proposal_id": "_workers", "actions": [f"removed stale workers: {removed_workers}"]})

    # 3. 修复每个 optimizing proposal 的 checkpoint 和 stuck/failed jobs
    for prop in optimizing:
        pid = prop["proposal_id"]
        item = {"proposal_id": pid, "actions": []}
        try:
            if not dry_run:
                self.sync_checkpoint(pid)

            jobs = self._get_jobs(pid)
            for job in jobs:
                if _is_stale(job):
                    if not dry_run:
                        self._update_job(pid, job, JOB_STATUS_FAILED, "运行超时/进程僵死")
                    item["actions"].append(f" stale job {job['job_id']} -> failed")
                elif job.get("status") == JOB_STATUS_FAILED:
                    repair_attempts = job.get("repair_attempts", 0)
                    if repair_attempts < MAX_JOB_ATTEMPTS:
                        if not dry_run:
                            job["status"] = JOB_STATUS_PENDING
                            job["started_at"] = ""
                            job["finished_at"] = ""
                            job["last_error"] = ""
                            job["attempts"] = 0
                            job["repair_attempts"] = repair_attempts + 1
                            self._save_jobs(pid, jobs)
                        item["actions"].append(
                            f" retry job {job['job_id']} (repair_attempt {repair_attempts + 1}/{MAX_JOB_ATTEMPTS})"
                        )
                    else:
                        item["actions"].append(f" job {job['job_id']} 超过修复重试次数，需人工介入")
                        if not dry_run:
                            self._record_cron_failure(pid, f"{job['job_id']}: {job.get('last_error', '')}")
        except Exception as e:
            item["actions"].append(f" error: {e}")
        repaired.append(item)

    return {"success": True, "dry_run": dry_run, "repaired": repaired, "at": now_utc()}

def _run_weekend_repair(
    self,
    dry_run: bool = False,
    lifecycle_crons: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """周末专用修复：扫描输入/输出/反思任务状态，并确保周末 cron 存在。"""
    if lifecycle_crons is None:
        lifecycle_crons = self.list_lifecycle_crons()

    active_names = {j.get("name") for j in lifecycle_crons if j.get("status") == "active"}
    weekend_jobs = _load_weekend_jobs()
    repaired = []

    for job_key in WEEKEND_JOBS:
        job_state = weekend_jobs.get("jobs", {}).get(job_key, {})
        actions = []

        # 1. 检查任务是否 stuck
        if _is_stale(job_state):
            actions.append(f" stale {job_key} -> failed")
            if not dry_run:
                job_state["status"] = JOB_STATUS_FAILED
                job_state["finished_at"] = now_utc()
                job_state["last_error"] = "运行超时/进程僵死"
                job_state["attempts"] = job_state.get("attempts", 0) + 1
                weekend_jobs.setdefault("jobs", {})[job_key] = job_state

        # 2. 检查 failed 重试
        elif job_state.get("status") == JOB_STATUS_FAILED and job_state.get("attempts", 0) < MAX_JOB_ATTEMPTS:
            actions.append(f" retry {job_key} (attempt {job_state.get('attempts', 0)})")
            if not dry_run:
                job_state["status"] = JOB_STATUS_PENDING
                job_state["started_at"] = ""
                job_state["finished_at"] = ""
                job_state["last_error"] = ""
                weekend_jobs.setdefault("jobs", {})[job_key] = job_state

        elif job_state.get("status") == JOB_STATUS_FAILED and job_state.get("attempts", 0) >= MAX_JOB_ATTEMPTS:
            actions.append(f" {job_key} 超过重试次数，需人工介入")

        # 3. 确保对应 cron 存在（仅检查，不立即创建；setup_weekend_crontab 负责安装）
        cron_name = f"lc-weekend-{job_key.replace('_', '-')}"
        if cron_name not in active_names:
            actions.append(f" missing cron {cron_name}")

        repaired.append({"job": job_key, "actions": actions, "status": job_state.get("status", "unknown")})

    if not dry_run:
        _save_weekend_jobs(weekend_jobs)

    # v6.7.7: 同时扫描 weekend-pipeline.json 的 checkpoint job
    pipeline_repaired = []
    try:
        pipeline_state = load_pipeline_state()
        pipeline_repaired = repair_weekend_pipeline(pipeline_state)
        if not dry_run:
            save_pipeline_state(pipeline_state)
    except Exception as e:
        if _log:
            _log.warning(f"扫描 weekend-pipeline.json 失败: {e}")

    return {
        "success": True,
        "dry_run": dry_run,
        "mode": "weekend",
        "repaired": repaired,
        "pipeline_repaired": pipeline_repaired,
        "at": now_utc(),
    }

def run_health_check(self) -> Dict[str, Any]:
    """委托给 ProposalLifecycle 的健康检查。"""
    from proposal_lifecycle import ProposalLifecycle
    return ProposalLifecycle.run_health_check(self)
