#!/usr/bin/env python3
"""生命周期 cron 框架编排与修复。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import hermes_bridge as hb
from common import now_utc

from proposal_lifecycle import DEFAULT_MAX_ROUNDS

from .constants import (
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    MAX_JOB_ATTEMPTS,
    WEEKEND_JOBS,
)
from .utils import _is_stale, _is_weekend, _load_weekend_jobs, _make_job_id, _save_weekend_jobs, _section_for_round

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


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

    # 工作日模式：扫描 optimizing proposal worker jobs
    optimizing = self.list_by_status("optimizing")
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

            # 2. 检查 worker cron 是否存在且 active，并校验 schedule 是否为周中
            worker_name = f"lc-worker-{pid}"
            if worker_name not in active_worker_names:
                if not dry_run:
                    self.schedule_worker(pid)
                    item["actions"].append(" recreated worker cron")
                else:
                    item["actions"].append(" missing worker cron (dry-run)")
            else:
                expected_minute = self._compute_worker_minute(pid)
                expected_schedule = f"{expected_minute} * * * 1-5"
                existing = next(
                    (j for j in lifecycle_crons if j.get("name") == worker_name), None
                )
                current_schedule = existing.get("schedule", "") if existing else ""
                if current_schedule and current_schedule != expected_schedule:
                    if not dry_run:
                        hb.cron_delete(existing.get("id"), profile=HERMES_PROFILE)
                        self.schedule_worker(pid)
                    item["actions"].append(
                        f" updated worker schedule {current_schedule} -> {expected_schedule}"
                    )

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

    return {"success": True, "dry_run": dry_run, "mode": "weekend", "repaired": repaired, "at": now_utc()}

def run_health_check(self) -> Dict[str, Any]:
    """委托给 ProposalLifecycle 的健康检查。"""
    from proposal_lifecycle import ProposalLifecycle
    return ProposalLifecycle.run_health_check(self)
