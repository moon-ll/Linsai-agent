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
    """判断任务依赖是否全部完成。

    v6.9.13: 保持严格语义——依赖必须位于 done 集合，缺失的依赖（模板
    已删除，如 v6.9.12 废弃的 input_deep_read）按不满足处理。死锁由
    sync_stage_jobs 的依赖刷新解除，不在此处放行：若放行，"代码已
    更新、state 未 sync"的窗口期内 compose 会被提前挑中，以空路由
    落地并标 done，丢失整周路由结果。
    """
    done_ids = {j.get("job_id") for j in state.get("jobs", []) if j.get("status") == JOB_STATUS_DONE}
    for dep in job.get("depends_on", []):
        if dep not in done_ids:
            return False
    return True


def _resolve_blocking_deps(state: Dict[str, Any], stage: Optional[str] = None) -> int:
    """修复阻塞 pending 任务的 failed 依赖。

    扫描所有 pending 任务，若其 depends_on 中的某个依赖是 failed 状态
    且 repair_attempts < MAX_JOB_ATTEMPTS，则立即重置为 pending。
    确保"失败不跳过，必须先重试成功"的严格顺序语义。

    返回修复的依赖数量。
    """
    jobs = state.get("jobs", [])
    resolved = 0

    for job in jobs:
        if job.get("status") != JOB_STATUS_PENDING:
            continue
        if stage and job.get("stage") != stage:
            continue
        for dep_id in job.get("depends_on", []):
            dep_job = find_job(state, dep_id)
            if dep_job and dep_job.get("status") == JOB_STATUS_FAILED:
                repair_attempts = dep_job.get("repair_attempts", 0)
                if repair_attempts < MAX_JOB_ATTEMPTS:
                    reset_failed_job(dep_job)
                    resolved += 1
                    if _log:
                        _log.info(
                            f"[weekend_pipeline] 依赖链修复: {dep_id} (failed→pending, "
                            f"repair_attempt {repair_attempts + 1}/{MAX_JOB_ATTEMPTS})"
                        )
    return resolved


def pick_next_job(state: Dict[str, Any], stage: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """挑选下一个可执行的 pending 任务。

    先处理 stale running 任务，然后修复阻塞 pending 任务的 failed 依赖，
    最后返回第一个依赖满足且 pending 的任务。
    """
    jobs = state.get("jobs", [])

    # 处理 stale running：只处理一个，避免单次扫描过多
    for job in jobs:
        if is_stale(job):
            if _log:
                _log.warning(f"[weekend_pipeline] job {job['job_id']} 运行超 {STALE_RUNNING_SECONDS}s，标记失败")
            update_job(state, job["job_id"], JOB_STATUS_FAILED, "运行超时/进程僵死")
            break

    # 重载后，先修复阻塞 pending 任务的 failed 依赖
    jobs = state.get("jobs", [])
    running = [j for j in jobs if j.get("status") == JOB_STATUS_RUNNING]
    if running:
        return None

    _resolve_blocking_deps(state, stage)

    # 挑选第一个 pending 且依赖满足的任务
    jobs = state.get("jobs", [])
    for job in jobs:
        if job.get("status") != JOB_STATUS_PENDING:
            continue
        if stage and job.get("stage") != stage:
            continue
        if dependencies_satisfied(job, state):
            return job
    return None


def reset_failed_job(job: Dict[str, Any]) -> None:
    """重置失败任务为 pending（用于重试）。

    重置 attempts 给下一轮执行机会；新增 repair_attempts 记录修复轮次，
    防止无限重试。
    """
    job["status"] = JOB_STATUS_PENDING
    job["started_at"] = ""
    job["finished_at"] = ""
    job["last_error"] = ""
    job["attempts"] = 0
    job["repair_attempts"] = job.get("repair_attempts", 0) + 1


def execute_job(
    state: Dict[str, Any],
    job: Dict[str, Any],
    handlers: Dict[tuple, Callable[[Dict[str, Any], Dict[str, Any], bool], Dict[str, Any]]],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """执行单个任务。

    v6.9.7: handler 注册 key 统一为 (stage, step) 二元组，消灭旧版
    "job_id 优先、step 回退"的双命名空间——同名 step 跨阶段不再有
    静默错绑风险。同阶段需要多 handler 的场景必须拆分为不同 step
    （如 reflection 阶段的 kb_deep_health 与 kb_merge）。
    """
    job_id = job["job_id"]
    stage = job.get("stage", "")
    step = job.get("step", "")
    handler = handlers.get((stage, step))

    if not handler:
        error = f"未找到 handler: stage={stage} step={step} (job_id={job_id})"
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
        elif job.get("status") == JOB_STATUS_FAILED and job.get("repair_attempts", 0) < MAX_JOB_ATTEMPTS:
            reset_failed_job(job)
            repaired.append({"job_id": job["job_id"], "action": "retry", "repair_attempts": job.get("repair_attempts", 0)})
    return repaired
