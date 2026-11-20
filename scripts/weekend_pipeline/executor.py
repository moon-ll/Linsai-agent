#!/usr/bin/env python3
"""任务执行器：挑选、执行、重试。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from common import now_utc

from .constants import (
    AUTO_UNLOCK_COOLDOWN_HOURS,
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


def should_auto_unlock_failed(
    job: Dict[str, Any],
    now: Optional[datetime] = None,
    cooldown_hours: float = AUTO_UNLOCK_COOLDOWN_HOURS,
) -> bool:
    """判断「修复系统已放弃」的 failed job 是否应自动解锁重跑。

    v7.2.46 新增。背景（10-26 04h 健康检查 P0-2 实测）：
        `repair_attempts` 是**单向计数器**——`reset_failed_job` 只做
        `+= 1`，全库无任何路径能把它归零。于是当 job 的失败根因是
        代码缺陷（而非瞬时超时）且该缺陷已被修复后，job 仍然永久卡在
        failed：
          - `repair_stale_and_failed` 条件 `repair_attempts < MAX_JOB_ATTEMPTS`
            在 repair_attempts=3 时为假 → 不重试
          - `_resolve_blocking_deps` 同一条件 → 下游 pending 全部阻塞
          - `_reset_stage_for_new_week` 跨周重置只清 status/attempts，
            **不清 repair_attempts** → 跨周重跑仍带 3 → 再次失败
        实测后果：周末反思链 `reflection_kb_merge_duplicates`（BUG-10
        `int` title 崩溃，代码已于 v7.2.45 修复）在 10-25 02:20 失败后
        repair_attempts 打满 3/3，下游
        `reflection_proposal_calibration` → `reflection_link_deep_review`
        → `reflection_kb_taxonomy_apply` → `reflection_panel_plan`
        四个 job 永久 pending，跨周重置在 10-26 不触发（最新 finished_at
        2026-10-25T02:20:35Z 晚于周六锚点），即便 10-31 触发也不清
        repair_attempts → **反思链永久死锁**。

    与 `lifecycle.utils.should_auto_unlock` 同构的逃生阀策略（v6.8.54
    为 proposal 级 job 引入，本函数为 weekend_pipeline job 引入）：
        1. status == failed 且 repair_attempts >= MAX_JOB_ATTEMPTS
           （修复系统已明确放弃；attempts 是否达上限不作为门槛，
           与 v6.9.49 的死角修复同口径）
        2. auto_unlock_count < 1（每个 job 终生至多自动解锁一次，
           防止坏输入导致无限重试循环）
        3. 最近一次失败距今超过 cooldown_hours（默认 24h，给根因修复
           留出落地时间）

    满足条件时解锁：status → pending、attempts → 0、清空
    started_at/finished_at/last_error、auto_unlock_count += 1。
    """
    try:
        if job.get("status") != JOB_STATUS_FAILED:
            return False
        if int(job.get("repair_attempts", 0)) < MAX_JOB_ATTEMPTS:
            return False
        if int(job.get("auto_unlock_count", 0)) >= 1:
            return False
        finished = str(job.get("finished_at") or "")
        if not finished:
            return False
        fin_dt = datetime.fromisoformat(finished.replace("Z", "+00:00"))
        now = now or datetime.now(timezone.utc)
        age_h = (now - fin_dt).total_seconds() / 3600.0
        if age_h < cooldown_hours:
            return False
        return True
    except Exception:
        return False


def auto_unlock_failed_job(job: Dict[str, Any]) -> None:
    """解锁一个已达修复上限的 failed job（调用前须过 should_auto_unlock_failed）。

    解锁时把 repair_attempts 归零——这是「单向计数器」缺陷的正解：
    根因已修复后，该 job 应获得完整的新一轮重试配额，而不是永久
    被上一轮的失败史锁死。auto_unlock_count 保证终生只解锁一次。
    """
    job["status"] = JOB_STATUS_PENDING
    job["attempts"] = 0
    job["repair_attempts"] = 0
    job["started_at"] = ""
    job["finished_at"] = ""
    job["last_error"] = ""
    job["auto_unlock_count"] = int(job.get("auto_unlock_count", 0)) + 1
    hist = job.get("error_history") or []
    hist.append({
        "at": now_utc(),
        "error": "自动解锁(v7.2.46): 修复系统已放弃且失败超 "
                 f"{AUTO_UNLOCK_COOLDOWN_HOURS:g}h，根因修复后重置重跑"
                 f"（第{job['auto_unlock_count']}次/上限1）",
        "attempts": 0,
    })
    job["error_history"] = hist[-10:]


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

    v7.2.46：新增自动解锁分支——依赖失败已达修复上限
    （repair_attempts >= MAX_JOB_ATTEMPTS）且失败超 24h 时，
    走 should_auto_unlock_failed 逃生阀（与 proposal 级
    lifecycle.utils.should_auto_unlock 同构），避免「根因已修复但
    job 永久卡死致下游全部 pending」的终态（10-26 04h 健康检查
    P0-2 实测：周末反思链四 job 永久阻塞）。

    Returns:
        修复的依赖数量。
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
                elif should_auto_unlock_failed(dep_job):
                    auto_unlock_failed_job(dep_job)
                    resolved += 1
                    if _log:
                        _log.info(
                            f"[weekend_pipeline] 依赖链自动解锁(v7.2.46): {dep_id} "
                            f"(failed→pending, repair_attempts 已达上限 "
                            f"{MAX_JOB_ATTEMPTS}，失败超 "
                            f"{AUTO_UNLOCK_COOLDOWN_HOURS:g}h)"
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
    """扫描并修复 stale running / 可重试 failed 任务。

    v7.2.46：新增自动解锁分支——failed job 的 repair_attempts 已达
    MAX_JOB_ATTEMPTS 且失败超 24h 时，走 should_auto_unlock_failed
    逃生阀并归零 repair_attempts（根因已修复后应获得完整新一轮配额）。
    """
    repaired = []
    for job in state.get("jobs", []):
        if is_stale(job):
            update_job(state, job["job_id"], JOB_STATUS_FAILED, "运行超时/进程僵死")
            repaired.append({"job_id": job["job_id"], "action": "stale -> failed"})
        elif job.get("status") == JOB_STATUS_FAILED and job.get("repair_attempts", 0) < MAX_JOB_ATTEMPTS:
            reset_failed_job(job)
            repaired.append({"job_id": job["job_id"], "action": "retry", "repair_attempts": job.get("repair_attempts", 0)})
        elif job.get("status") == JOB_STATUS_FAILED and should_auto_unlock_failed(job):
            auto_unlock_failed_job(job)
            repaired.append({"job_id": job["job_id"], "action": "auto_unlock (v7.2.46)"})
    return repaired
