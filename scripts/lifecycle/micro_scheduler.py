#!/usr/bin/env python3
"""生命周期 cron 全局微调度器（v6.8.0）。

目标：
- 工作日按 4 个时段轮流聚焦单个 proposal。
- 每个时段只执行当前聚焦 proposal 的 pending job。
- 同一 proposal 的 researcher 4 子任务可在时段内连贯完成。
- 全局每 5 分钟只执行一个任务，避免并发过载。

时段定义（可配置）：
    00:30-03:30, 04:00-08:00, 08:30-12:30, 18:30-22:30
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import file_lock, load_json, now_utc, save_json
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


# 默认聚焦时段（本地时间）。可通过 memory/config/schedules/focus-slots.json 覆盖。
DEFAULT_FOCUS_SLOTS: List[Tuple[str, str]] = [
    ("00:30", "03:30"),
    ("04:00", "08:00"),
    ("08:30", "12:30"),
    ("18:30", "22:30"),
]

# 聚焦状态持久化路径
FOCUS_STATE_PATH = PROJECT_ROOT / "memory" / "lifecycle-focus.json"

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


def _load_focus_slots() -> List[Tuple[str, str]]:
    """加载聚焦时段配置，失败时使用默认值。"""
    config_path = PROJECT_ROOT / "memory" / "config" / "schedules" / "focus-slots.json"
    if not config_path.exists():
        return DEFAULT_FOCUS_SLOTS
    try:
        data = load_json(config_path, default={})
        slots = data.get("slots")
        if isinstance(slots, list) and len(slots) > 0:
            return [(str(s[0]), str(s[1])) for s in slots]
    except Exception:
        pass
    return DEFAULT_FOCUS_SLOTS


def _parse_hm(value: str) -> Tuple[int, int]:
    """解析 HH:MM 为 (hour, minute)。"""
    h, m = value.split(":")
    return int(h), int(m)


def _minutes_since_midnight(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute


def _current_focus_slot() -> Optional[Tuple[int, Tuple[str, str]]]:
    """返回当前所处的时段索引和时段定义；不在任何时段内返回 None。"""
    now = datetime.now()
    now_min = _minutes_since_midnight(now)
    slots = _load_focus_slots()
    for idx, (start, end) in enumerate(slots):
        sh, sm = _parse_hm(start)
        eh, em = _parse_hm(end)
        start_min = sh * 60 + sm
        end_min = eh * 60 + em
        if start_min <= now_min <= end_min:
            return idx, (start, end)
    return None


def _load_focus_state() -> Dict[str, Any]:
    """加载聚焦轮询状态。"""
    FOCUS_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return load_json(FOCUS_STATE_PATH, default={
        "last_slot_index": -1,
        "last_proposal_index": 0,
        "focus_history": [],
    })


def _save_focus_state(state: Dict[str, Any]) -> None:
    """保存聚焦轮询状态。"""
    FOCUS_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_utc()
    save_json(FOCUS_STATE_PATH, state)


def _is_round_complete(jobs: List[Dict[str, Any]], proposal_id: str, round_num: int) -> bool:
    """检查 proposal 的指定 round 是否全部 job 都 done。"""
    round_jobs = [j for j in jobs if j.get("round") == round_num]
    if not round_jobs:
        return False
    return all(j.get("status") == JOB_STATUS_DONE for j in round_jobs)


def _focus_proposal_for_slot(
    self,
    slot_index: int,
    optimizing: List[Dict[str, Any]],
) -> Optional[str]:
    """确定当前时段应聚焦的 proposal。

    规则：
    - 按轮询顺序选择下一个 proposal。
    - 若上一个时段聚焦的 proposal 本轮未完成，继续聚焦它。
    - 若已完成，则推进到下一个 proposal。
    """
    if not optimizing:
        return None

    state = _load_focus_state()
    last_slot_index = state.get("last_slot_index", -1)
    last_proposal_index = state.get("last_proposal_index", 0)

    # 当前时段与上一时段不同，可能需要切换 proposal
    if slot_index != last_slot_index:
        # 检查上一时段聚焦的 proposal 是否已完成本轮
        prev_index = last_proposal_index % len(optimizing)
        prev_pid = optimizing[prev_index]["proposal_id"]
        try:
            prev_jobs = self._get_jobs(prev_pid)
            prev_state = self._get_proposal_state(prev_pid)
            current_round = prev_state.get("optimization_rounds", 0) + 1
            if not _is_round_complete(prev_jobs, prev_pid, current_round):
                # 未完成，继续聚焦上一个
                state["last_slot_index"] = slot_index
                _save_focus_state(state)
                return prev_pid
        except Exception:
            pass
        # 已完成，推进到下一个
        next_index = (last_proposal_index + 1) % len(optimizing)
        state["last_slot_index"] = slot_index
        state["last_proposal_index"] = next_index
        _save_focus_state(state)
    else:
        # 同一时段内，保持当前聚焦
        next_index = last_proposal_index % len(optimizing)

    pid = optimizing[next_index]["proposal_id"]

    # 记录历史
    history = state.get("focus_history", [])
    history.append({
        "slot_index": slot_index,
        "slot_start": _load_focus_slots()[slot_index][0],
        "proposal_id": pid,
        "at": now_utc(),
    })
    state["focus_history"] = history[-50:]  # 只保留最近 50 条
    _save_focus_state(state)

    return pid


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
    """返回 job 的优先级排序键（越小越优先）。"""
    jobs = self._get_jobs(proposal_id)
    job_index = {j["job_id"]: i for i, j in enumerate(jobs)}

    deps = job.get("depends_on", [])
    deps_just_done = all(
        any(d == j["job_id"] and j.get("status") == JOB_STATUS_DONE for j in jobs)
        for d in deps
    )

    step = job.get("step", "")
    chain_order = _CHAIN_ORDER.get(step, 99)
    scheduled_at = job.get("scheduled_at") or job.get("started_at") or ""
    chain_next = 0 if deps_just_done else 1

    return (chain_next, chain_order, scheduled_at, job_index.get(job["job_id"], 9999))


def _list_ready_jobs_for_proposal(
    self,
    proposal_id: str,
) -> List[Dict[str, Any]]:
    """扫描指定 proposal，返回所有依赖满足且 pending 的 job。"""
    ready: List[Dict[str, Any]] = []
    try:
        self._refresh_stale_jobs(proposal_id)
        self.sync_checkpoint(proposal_id)
        jobs = self._get_jobs(proposal_id)

        done_ids = {j["job_id"] for j in jobs if j.get("status") == JOB_STATUS_DONE}
        running = [j for j in jobs if j.get("status") == JOB_STATUS_RUNNING]
        if running:
            return []

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

    ready.sort(key=lambda x: x["priority"])
    return ready


def run_micro_scheduler(self, max_jobs: int = 1, time_limit_s: int = 240) -> Dict[str, Any]:
    """v6.8.0 全局微调度器入口：时段聚焦 + 单任务节流。"""
    if _log:
        _log.info("=== 微调度器启动 ===")

    started_at = time.time()
    executed: List[Dict[str, Any]] = []

    # 1. 时段检查
    slot_info = _current_focus_slot()
    if slot_info is None:
        msg = "当前不在工作时段内，跳过"
        if _log:
            _log.info(msg)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg}

    slot_index, (slot_start, slot_end) = slot_info
    if _log:
        _log.info(f"当前时段: {slot_start}-{slot_end} (#{slot_index})")

    # 2. 获取 optimizing proposal 列表
    try:
        optimizing = self.list_by_status("optimizing")
    except Exception:
        optimizing = []

    if not optimizing:
        msg = "optimizing 区为空"
        if _log:
            _log.info(msg)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg}

    # 3. 选择聚焦 proposal
    focus_pid = self._focus_proposal_for_slot(slot_index, optimizing)
    if not focus_pid:
        msg = "无法确定聚焦 proposal"
        if _log:
            _log.info(msg)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg}

    if _log:
        _log.info(f"聚焦 proposal: {focus_pid}")

    # 4. 检查聚焦 proposal 本轮是否已完成
    prop_state = self._get_proposal_state(focus_pid)
    current_round = prop_state.get("optimization_rounds", 0) + 1 if prop_state else 1
    jobs = self._get_jobs(focus_pid)
    if _is_round_complete(jobs, focus_pid, current_round):
        msg = f"{focus_pid} 本轮已完成，时段空闲"
        if _log:
            _log.info(msg)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg}

    # 5. 只执行聚焦 proposal 的 pending job
    with file_lock("lifecycle-micro-scheduler"):
        for _ in range(max_jobs):
            if time.time() - started_at > time_limit_s:
                if _log:
                    _log.info("微调度器达到时间上限，退出")
                break

            ready = self._list_ready_jobs_for_proposal(focus_pid)
            if not ready:
                if _log:
                    _log.info(f"微调度器：{focus_pid} 无待执行 job")
                break

            item = ready[0]
            proposal_id = item["proposal_id"]
            job = item["job"]

            with file_lock(f"proposal-{proposal_id}"):
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
        "focus_proposal": focus_pid,
        "slot_index": slot_index,
        "slot": f"{slot_start}-{slot_end}",
        "elapsed_s": round(time.time() - started_at, 2),
        "at": now_utc(),
    }
    if _log:
        _log.info(f"微调度器完成: 执行 {len(executed)} 个 job, 聚焦 {focus_pid}")
    return summary


def schedule_micro_scheduler(self) -> Dict[str, Any]:
    """创建或更新全局微调度器 cron（每 5 分钟一次）。"""
    import hermes_bridge as hb

    self._write_generic_wrappers()

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


def get_current_focus(self) -> Dict[str, Any]:
    """v6.8.0: 查询当前微调度器聚焦 proposal 与下一 pending job（只读，不执行）。"""
    slot_info = _current_focus_slot()
    if slot_info is None:
        return {"in_slot": False, "focus_proposal": None, "next_job": None}

    slot_index, (slot_start, slot_end) = slot_info
    try:
        optimizing = self.list_by_status("optimizing")
    except Exception:
        optimizing = []

    if not optimizing:
        return {"in_slot": True, "focus_proposal": None, "next_job": None, "slot": f"{slot_start}-{slot_end}"}

    focus_pid = self._focus_proposal_for_slot(slot_index, optimizing)
    next_job = None
    if focus_pid:
        ready = self._list_ready_jobs_for_proposal(focus_pid)
        if ready:
            job = ready[0]["job"]
            next_job = {
                "proposal_id": focus_pid,
                "job_id": job.get("job_id"),
                "step": job.get("step"),
                "section_key": job.get("section_key"),
                "round": job.get("round"),
            }

    return {
        "in_slot": True,
        "slot_index": slot_index,
        "slot": f"{slot_start}-{slot_end}",
        "focus_proposal": focus_pid,
        "next_job": next_job,
    }
