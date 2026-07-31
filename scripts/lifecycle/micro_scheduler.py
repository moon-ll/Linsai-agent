#!/usr/bin/env python3
"""生命周期 cron 全局微调度器（v6.7.12）。

目标：
- 将 researcher 拆分为 4 个连贯子任务后，确保子任务间隔短、不分散在多个小时。
- 全局每 5 分钟只执行一个任务，避免并发过载。
- 优先完成已开始的工作链（critic -> gap_identify -> lit_search -> lit_read -> lit_note -> writer -> monitor）。
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from common import file_lock, now_utc
from paths import PROJECT_ROOT

from .constants import (
    HERMES_PROFILE,
    JOB_STATUS_DONE,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    MICRO_SCHEDULER_NAME,
    MICRO_SCHEDULER_SCHEDULE,
    STALE_RUNNING_SECONDS,
    STEP_CRITIC,
    STEP_GAP_IDENTIFY,
    STEP_LIT_NOTE,
    STEP_LIT_READ,
    STEP_LIT_SEARCH,
    STEP_MONITOR,
    STEP_WRITER,
)
from .utils import _is_stale, _make_job_id

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


# 步骤在链中的顺序，用于优先级排序（数字越小越优先继续）
_CHAIN_ORDER = {
    STEP_CRITIC: 0,
    STEP_GAP_IDENTIFY: 1,
    STEP_LIT_SEARCH: 2,
    STEP_LIT_READ: 3,
    STEP_LIT_NOTE: 4,
    STEP_WRITER: 5,
    STEP_MONITOR: 6,
    "researcher": 3,  # 兼容旧 researcher job
}


def _refresh_stale_jobs(self, proposal_id: str) -> None:
    """检查并标记 proposal 内超时的 running job。"""
    jobs = self._get_jobs(proposal_id)
    changed = False
    for job in jobs:
        if job.get("status") == JOB_STATUS_RUNNING and _is_stale(job):
            if _log:
                _log.warning(
                    f"[{proposal_id}] job {job['job_id']} 运行超 {STALE_RUNNING_SECONDS}s，标记失败"
                )
            job["status"] = "failed"
            job["finished_at"] = now_utc()
            job["last_error"] = "运行超时/进程僵死"
            job["attempts"] = job.get("attempts", 0) + 1
            changed = True
    if changed:
        self._save_jobs(proposal_id, jobs)


def _job_priority_key(self, proposal_id: str, job: Dict[str, Any]) -> tuple:
    """返回 job 的优先级排序键（越小越优先）。

    优先级规则：
    1. 依赖链中前置任务刚刚完成的（即该 job 是链的下一步）优先
    2. 步骤在标准链中越靠前优先（先跑完已有链）
    3. 创建/调度越早优先
    4. 同一 proposal 内按 job 在列表中的顺序
    """
    jobs = self._get_jobs(proposal_id)
    job_index = {j["job_id"]: i for i, j in enumerate(jobs)}

    deps = job.get("depends_on", [])
    # 检查依赖是否刚刚完成（done 且在最近一个任务周期内完成）
    deps_just_done = all(
        any(
            d == j["job_id"] and j.get("status") == JOB_STATUS_DONE
            for j in jobs
        )
        for d in deps
    )

    step = job.get("step", "")
    chain_order = _CHAIN_ORDER.get(step, 99)

    # 创建时间：使用 scheduled_at 或 started_at 或空字符串
    scheduled_at = job.get("scheduled_at") or job.get("started_at") or ""

    # 是否链下一步：是(0) > 否(1)
    chain_next = 0 if deps_just_done else 1

    return (chain_next, chain_order, scheduled_at, job_index.get(job["job_id"], 9999))


def _list_ready_jobs(self) -> List[Dict[str, Any]]:
    """扫描所有 optimizing proposal，返回所有依赖满足且 pending 的 job。"""
    ready: List[Dict[str, Any]] = []
    try:
        optimizing = self.list_by_status("optimizing")
    except Exception:
        optimizing = []

    for prop in optimizing:
        proposal_id = prop["proposal_id"]
        try:
            self._refresh_stale_jobs(proposal_id)
            self.sync_checkpoint(proposal_id)
            jobs = self._get_jobs(proposal_id)

            done_ids = {j["job_id"] for j in jobs if j.get("status") == JOB_STATUS_DONE}
            running = [j for j in jobs if j.get("status") == JOB_STATUS_RUNNING]
            if running:
                continue  # 该 proposal 有任务在跑，跳过

            for job in jobs:
                if job.get("status") != JOB_STATUS_PENDING:
                    continue
                deps = job.get("depends_on", [])
                if all(d in done_ids for d in deps):
                    ready.append({
                        "proposal_id": proposal_id,
                        "job": job,
                        "priority": self._job_priority_key(proposal_id, job),
                    })
        except Exception as e:
            if _log:
                _log.warning(f"[micro-scheduler] 扫描 {proposal_id} 失败: {e}")
            continue

    # 按优先级排序
    ready.sort(key=lambda x: x["priority"])
    return ready


def run_micro_scheduler(self, max_jobs: int = 1, time_limit_s: int = 240) -> Dict[str, Any]:
    """全局微调度器入口：执行一个或多个 pending job。

    Args:
        max_jobs: 本次调用最多执行几个 job（默认 1，配合 5 分钟 cron 实现全局节流）
        time_limit_s: 总时间上限，防止单批次执行过久
    """
    if _log:
        _log.info("=== 微调度器启动 ===")

    started_at = time.time()
    executed: List[Dict[str, Any]] = []

    # 全局锁：确保同一时刻只有一个微调度器实例在运行
    with file_lock("lifecycle-micro-scheduler"):
        for _ in range(max_jobs):
            if time.time() - started_at > time_limit_s:
                if _log:
                    _log.info("微调度器达到时间上限，退出")
                break

            ready = self._list_ready_jobs()
            if not ready:
                if _log:
                    _log.info("微调度器：无待执行 job")
                break

            item = ready[0]
            proposal_id = item["proposal_id"]
            job = item["job"]

            # 单个 proposal 锁，避免与旧 worker 冲突
            with file_lock(f"proposal-{proposal_id}"):
                # 重新检查该 job 是否仍 ready（锁内）
                jobs = self._get_jobs(proposal_id)
                refreshed = next((j for j in jobs if j["job_id"] == job["job_id"]), None)
                if not refreshed or refreshed.get("status") != JOB_STATUS_PENDING:
                    continue
                done_ids = {j["job_id"] for j in jobs if j.get("status") == JOB_STATUS_DONE}
                if not all(d in done_ids for d in refreshed.get("depends_on", [])):
                    continue

                result = self.execute_job(refreshed)
                executed.append({
                    "proposal_id": proposal_id,
                    "job_id": refreshed["job_id"],
                    "step": refreshed.get("step"),
                    "success": result.get("success"),
                    "error": result.get("error", "")[:200],
                })

    summary = {
        "success": True,
        "executed_count": len(executed),
        "executed": executed,
        "elapsed_s": round(time.time() - started_at, 2),
        "at": now_utc(),
    }
    if _log:
        _log.info(f"微调度器完成: 执行 {len(executed)} 个 job")
    return summary


def schedule_micro_scheduler(self) -> Dict[str, Any]:
    """创建或更新全局微调度器 cron（每 5 分钟一次）。"""
    import hermes_bridge as hb

    self._write_generic_wrappers()

    # 先清理旧的微调度器（避免重复）
    existing = self.list_lifecycle_crons()
    for cron in existing:
        if cron.get("name") == MICRO_SCHEDULER_NAME:
            hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)

    script_content = f"""#!/bin/bash
set -e
cd {PROJECT_ROOT}
python3 scripts/proposal_lifecycle.py --micro-scheduler
"""
    from .utils import _write_wrapper_script
    script_path = _write_wrapper_script("lc_micro_scheduler.sh", script_content)

    result = hb.cron_create_no_agent(
        script_name=script_path.name,
        name=MICRO_SCHEDULER_NAME,
        schedule=MICRO_SCHEDULER_SCHEDULE,
        workdir=str(PROJECT_ROOT),
        profile=HERMES_PROFILE,
    )
    return result


def remove_micro_scheduler(self) -> Dict[str, Any]:
    """删除全局微调度器 cron。"""
    import hermes_bridge as hb

    removed = []
    for cron in self.list_lifecycle_crons():
        if cron.get("name") == MICRO_SCHEDULER_NAME:
            res = hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
            if res.get("success"):
                removed.append(cron.get("name"))
    return {"success": True, "removed": removed}


def pause_old_worker_crons(self) -> Dict[str, Any]:
    """暂停所有 lc-worker-* cron（迁移到微调度器时使用）。"""
    import hermes_bridge as hb

    paused = []
    for cron in self.list_lifecycle_crons():
        name = cron.get("name", "")
        if name.startswith("lc-worker-"):
            res = hb.cron_control(cron.get("id"), "pause", profile=HERMES_PROFILE)
            if res.get("success"):
                paused.append(name)
    return {"success": True, "paused": paused}
