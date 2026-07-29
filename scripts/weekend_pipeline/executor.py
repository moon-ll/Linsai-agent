#!/usr/bin/env python3
"""任务执行器：挑选、执行、重试。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from common import now_utc

from .constants import (
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    MAX_JOB_ATTEMPTS,
    STALE_RUNNING_SECONDS,
    STAGES,
)
from .state import find_job, save_pipeline_state, update_job

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


def _dt_from_iso(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def is_stale(job: Dict[str, Any], stale_seconds: int = STALE_RUNNING_SECONDS) -> bool:
    """判断 running 任务是否已超时。"""
    if job.get("status") != JOB_STATUS_RUNNING:
        return False
    started = _dt_from_iso(job.get("started_at", ""))
    if not started:
        return True
    return (datetime.now(timezone.utc) - started).total_seconds() > stale_seconds


def dependencies_satisfied(job: Dict[str, Any], state: Dict[str, Any]) -> bool:
    """判断任务依赖是否全部完成。"""
    done_ids = {j.get("job_id") for j in state.get("jobs", []) if j.get("status") == JOB_STATUS_DONE}
    for dep in job.get("depends_on", []):
        if dep not in done_ids:
            return False
    return True


def pick_next_job(state: Dict[str, Any], stage: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """挑选下一个可执行的 pending 任务。

    先处理 stale running 任务，然后返回第一个依赖满足且 pending 的任务。
    """
    jobs = state.get("jobs", [])

    # 处理 stale running：只处理一个，避免单次扫描过多
    for job in jobs:
        if is_stale(job):
            if _log:
                _log.warning(f"[weekend_pipeline] job {job['job_id']} 运行超 {STALE_RUNNING_SECONDS}s，标记失败")
            update_job(state, job["job_id"], JOB_STATUS_FAILED, "运行超时/进程僵死")
            break

    # 重载后挑选
    jobs = state.get("jobs", [])
    running = [j for j in jobs if j.get("status") == JOB_STATUS_RUNNING]
    if running:
        return None

    for job in jobs:
        if job.get("status") != JOB_STATUS_PENDING:
            continue
        if stage and job.get("stage") != stage:
            continue
        if dependencies_satisfied(job, state):
            return job
    return None


def reset_failed_job(job: Dict[str, Any]) -> None:
    """重置失败任务为 pending（用于重试）。"""
    job["status"] = JOB_STATUS_PENDING
    job["started_at"] = ""
    job["finished_at"] = ""
    job["last_error"] = ""


def execute_job(
    state: Dict[str, Any],
    job: Dict[str, Any],
    handlers: Dict[str, Callable[[Dict[str, Any], Dict[str, Any], bool], Dict[str, Any]]],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """执行单个任务。"""
    job_id = job["job_id"]
    step = job.get("step", "")
    handler = handlers.get(step)

    if not handler:
        error = f"未找到 step={step} 的执行器"
        update_job(state, job_id, JOB_STATUS_FAILED, error)
        return {"success": False, "error": error, "job_id": job_id}

    update_job(state, job_id, JOB_STATUS_RUNNING)
    try:
        result = handler(state, job, dry_run=dry_run)
        success = bool(result.get("success")) if isinstance(result, dict) else True
        if success:
            update_job(state, job_id, JOB_STATUS_DONE, result=result)
        else:
            error = result.get("error", "未知错误") if isinstance(result, dict) else "执行失败"
            update_job(state, job_id, JOB_STATUS_FAILED, error, result=result)
        return {"success": success, "job_id": job_id, "result": result}
    except Exception as e:
        if _log:
            _log.exception(f"[weekend_pipeline] 执行任务 {job_id} 失败")
        update_job(state, job_id, JOB_STATUS_FAILED, str(e))
        return {"success": False, "job_id": job_id, "error": str(e)}


def run_pending_jobs(
    state: Dict[str, Any],
    handlers: Dict[str, Callable[[Dict[str, Any], Dict[str, Any], bool], Dict[str, Any]]],
    stage: Optional[str] = None,
    dry_run: bool = False,
    max_jobs: Optional[int] = None,
) -> Dict[str, Any]:
    """顺序执行所有 pending 任务。"""
    results = []
    count = 0
    while True:
        if max_jobs is not None and count >= max_jobs:
            break
        job = pick_next_job(state, stage=stage)
        if not job:
            break
        result = execute_job(state, job, handlers, dry_run=dry_run)
        results.append(result)
        count += 1
        if not result.get("success"):
            # 失败即停止该阶段，等待 repair 重试
            break
    return {"success": True, "executed": count, "results": results}


def repair_stale_and_failed(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """扫描并修复 stale running / 可重试 failed 任务。"""
    repaired = []
    for job in state.get("jobs", []):
        if is_stale(job):
            update_job(state, job["job_id"], JOB_STATUS_FAILED, "运行超时/进程僵死")
            repaired.append({"job_id": job["job_id"], "action": "stale -> failed"})
        elif job.get("status") == JOB_STATUS_FAILED and job.get("attempts", 0) < MAX_JOB_ATTEMPTS:
            reset_failed_job(job)
            repaired.append({"job_id": job["job_id"], "action": "retry", "attempts": job.get("attempts", 0)})
    return repaired
