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
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

from .constants import (
    HERMES_PROFILE,
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    MAX_JOB_ATTEMPTS,
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
    STEP_UPDATE_VISION,
    STEP_UPDATE_METHOD_MANUAL,
)
from .utils import _is_stale, _make_job_id

# 看板文件路径
KANBAN_PATH = PROJECT_ROOT / "memory" / "system-kanban.json"

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
        "last_proposal_id": "",
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


def _get_current_day_key() -> str:
    """返回当前日期键（YYYY-MM-DD），用于跨天轮转追踪。"""
    return datetime.now().strftime("%Y-%m-%d")


def _auto_retry_failed_jobs(self, proposal_id: str) -> int:
    """扫描 proposal 的 failed job，若 attempts < MAX_JOB_ATTEMPTS 则重置为 pending。

    返回重置的 job 数量。
    """
    jobs = self._get_jobs(proposal_id)
    if not jobs:
        return 0
    changed = False
    retry_count = 0
    for job in jobs:
        if job.get("status") == JOB_STATUS_FAILED:
            attempts = job.get("attempts", 0)
            if attempts < MAX_JOB_ATTEMPTS:
                job["status"] = JOB_STATUS_PENDING
                job["attempts"] = attempts + 1
                job["last_error"] = ""
                job["repair_attempts"] = job.get("repair_attempts", 0) + 1
                retry_count += 1
                changed = True
                if _log:
                    _log.info(
                        f"[{proposal_id}] 自动重试 job {job['job_id']} "
                        f"(attempt {attempts + 1}/{MAX_JOB_ATTEMPTS})"
                    )
    if changed:
        self._save_jobs(proposal_id, jobs)
    return retry_count


def _is_proposal_stuck(self, proposal_id: str) -> bool:
    """检查 proposal 是否被卡住（有 failed job 且达到最大重试次数）。"""
    jobs = self._get_jobs(proposal_id)
    if not jobs:
        return False
    for job in jobs:
        if job.get("status") == JOB_STATUS_FAILED:
            attempts = job.get("attempts", 0)
            if attempts >= MAX_JOB_ATTEMPTS:
                return True
    return False


def _has_any_ready_or_failed_job(self, proposal_id: str) -> bool:
    """检查 proposal 是否有待执行或可重试的 job（用于判断是否还有工作可做）。"""
    jobs = self._get_jobs(proposal_id)
    for job in jobs:
        status = job.get("status", "")
        if status in (JOB_STATUS_PENDING, JOB_STATUS_FAILED):
            return True
    return False


def _generate_round_report(self, proposal_id: str, round_num: int) -> Optional[str]:
    """为指定 proposal 的 round 生成优化报告，保存到 proposal 目录。

    返回报告文件路径，若无需生成则返回 None。
    """
    prop_dir = self._find_proposal_dir(proposal_id)
    if not prop_dir:
        return None
    prop_state = self._get_proposal_state(proposal_id)
    if not prop_state:
        return None

    # 收集本轮评分历史
    score_history = prop_state.get("score_history", [])
    round_scores = [h for h in score_history if h.get("round") == round_num]

    # 收集本轮执行统计
    jobs = self._get_jobs(proposal_id)
    round_jobs = [j for j in jobs if j.get("round") == round_num]
    total_jobs = len(round_jobs)
    done_jobs = sum(1 for j in round_jobs if j.get("status") == JOB_STATUS_DONE)
    failed_jobs = sum(1 for j in round_jobs if j.get("status") == JOB_STATUS_FAILED)
    elapsed_total = 0.0
    for j in round_jobs:
        started = j.get("started_at", "")
        finished = j.get("finished_at", "")
        if started and finished:
            try:
                st = datetime.fromisoformat(started.replace("Z", "+00:00"))
                ft = datetime.fromisoformat(finished.replace("Z", "+00:00"))
                elapsed_total += (ft - st).total_seconds()
            except Exception:
                pass

    # 计算分数变化
    final_score = prop_state.get("last_score", 0.0)
    prev_scores = [h for h in score_history if h.get("round", 0) < round_num]
    prev_score = prev_scores[-1]["score"] if prev_scores else 0.0

    report_lines = [
        f"# 优化报告：{proposal_id}",
        f"",
        f"## 概述",
        f"- **轮次**: 第 {round_num} 轮",
        f"- **完成时间**: {now_utc()}",
        f"- **状态**: {'✓ 完成' if done_jobs == total_jobs else '◐ 进行中'}"
        f" ({done_jobs}/{total_jobs} job 完成)",
        f"- **失败 job**: {failed_jobs}",
        f"- **总耗时**: {elapsed_total:.0f}s",
        f"",
        f"## 评分变化",
        f"| 指标 | 上一轮 | 本轮 | 变化 |",
        f"|------|--------|------|------|",
    ]

    # 维度评分
    if round_scores:
        latest = round_scores[-1]
        dim_scores = latest.get("dim_scores", {})
        prev_dim = prev_scores[-1].get("dim_scores", {}) if prev_scores else {}
        for dim, score in dim_scores.items():
            prev = prev_dim.get(dim, 0.0)
            delta = score - prev
            delta_str = f"+{delta:.2f}" if delta > 0 else f"{delta:.2f}"
            report_lines.append(f"| {dim} | {prev:.2f} | {score:.2f} | {delta_str} |")

    report_lines.extend([
        f"| **总分** | **{prev_score:.2f}** | **{final_score:.2f}** | **{final_score - prev_score:+.2f}** |",
        f"",
        f"## 执行详情",
    ])

    # 按模块分组
    section_map = {}
    for j in round_jobs:
        sk = j.get("section_key", "unknown")
        if sk not in section_map:
            section_map[sk] = []
        section_map[sk].append(j)

    for sk, sjobs in section_map.items():
        report_lines.append(f"### {sk}")
        report_lines.append(f"| Job | 状态 | 耗时 | 错误 |")
        report_lines.append(f"|-----|------|------|------|")
        for j in sjobs:
            step = j.get("step", "?")
            status = j.get("status", "?")
            started = j.get("started_at", "")
            finished = j.get("finished_at", "")
            elapsed = ""
            if started and finished:
                try:
                    st = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    ft = datetime.fromisoformat(finished.replace("Z", "+00:00"))
                    elapsed = f"{(ft - st).total_seconds():.0f}s"
                except Exception:
                    pass
            err = (j.get("last_error", "") or "")[:60]
            report_lines.append(f"| {step} | {status} | {elapsed} | {err} |")

    # 弱维度分析
    if round_scores:
        latest = round_scores[-1]
        weakest = latest.get("weakest_dim", "无")
        high_issues = latest.get("high_issues", 0)
        report_lines.extend([
            f"",
            f"## 问题分析",
            f"- **最弱维度**: {weakest}",
            f"- **高优先级问题**: {high_issues} 个",
            f"- **总问题数**: {latest.get('issues_count', 0)} 个",
        ])

    report_dir = prop_dir / "05_review"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"optimization-report-round-{round_num}.md"

    # 避免重复生成
    if report_path.exists():
        return str(report_path)

    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    return str(report_path)


def _update_kanban(
    slot_info: Optional[Tuple[int, Tuple[str, str]]],
    focus_pid: Optional[str],
    optimizing: List[Dict[str, Any]],
    executed: List[Dict[str, Any]],
    self,
) -> None:
    """更新系统看板文件（memory/system-kanban.json），同步微调度器状态。"""
    now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now = now_utc()

    # 收集所有 optimizing proposal 的当前状态
    proposals_status = []
    for prop in optimizing:
        pid = prop["proposal_id"]
        prop_state = self._get_proposal_state(pid)
        jobs = self._get_jobs(pid)
        round_num = prop_state.get("optimization_rounds", 0) + 1 if prop_state else 1
        score = prop_state.get("last_score", 0.0) if prop_state else 0.0
        failed = sum(1 for j in jobs if j.get("status") == JOB_STATUS_FAILED)
        pending = sum(1 for j in jobs if j.get("status") == JOB_STATUS_PENDING)
        done = sum(1 for j in jobs if j.get("status") == JOB_STATUS_DONE)
        total = len(jobs)
        stuck = _is_proposal_stuck(self, pid)

        next_job = None
        if not stuck:
            ready = self._list_ready_jobs_for_proposal(pid)
            if ready:
                j = ready[0]["job"]
                next_job = f"{j.get('step')}/{j.get('section_key')}"

        proposals_status.append({
            "proposal_id": pid,
            "round": round_num,
            "score": round(score, 2),
            "jobs": f"{done}/{total}",
            "failed": failed,
            "pending": pending,
            "stuck": stuck,
            "next_job": next_job,
        })

    # 读取现有看板，保留历史记录
    existing = load_json(KANBAN_PATH, default={})
    history = existing.get("execution_history", [])
    if executed:
        for e in executed:
            history.append({
                "at": now,
                "proposal_id": e.get("proposal_id"),
                "job_id": e.get("job_id"),
                "step": e.get("step"),
                "success": e.get("success"),
                "error": (e.get("error") or "")[:100],
            })

    # 最多保留 200 条历史记录
    history = history[-200:]

    kanban = {
        "updated_at": now,
        "updated_at_local": now_local,
        "current": {
            "in_slot": slot_info is not None,
            "slot_index": slot_info[0] if slot_info else None,
            "slot": f"{slot_info[1][0]}-{slot_info[1][1]}" if slot_info else None,
            "focus_proposal": focus_pid,
            "proposals_in_optimizing": len(optimizing),
        },
        "proposals": proposals_status,
        "execution_history": history,
        "day_key": _get_current_day_key(),
    }
    try:
        KANBAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_json(KANBAN_PATH, kanban)
    except Exception as e:
        if _log:
            _log.warning(f"更新看板失败: {e}")


def _rebalance_index(
    state: Dict[str, Any],
    optimizing: List[Dict[str, Any]],
) -> int:
    """根据 last_proposal_id 重新校准 last_proposal_index。

    当 optimizing 列表跨周发生变化（新增/删除 proposal）时，
    确保轮转位置正确：
    - 若 last_proposal_id 在列表中，找到其索引。
    - 若不在列表中，保持 last_proposal_index（列表缩短时回绕）。
    - 若索引超出范围，回绕到 0。
    """
    last_id = state.get("last_proposal_id", "")
    last_index = state.get("last_proposal_index", 0)
    n = len(optimizing)
    if n == 0:
        return 0

    # 优先通过 last_proposal_id 定位
    if last_id:
        for i, prop in enumerate(optimizing):
            if prop.get("proposal_id") == last_id:
                if i != last_index:
                    state["last_proposal_index"] = i
                return i

    # last_proposal_id 不在列表中（被归档等），检查索引是否有效
    if last_index >= n:
        state["last_proposal_index"] = 0
        return 0
    return last_index


def _focus_proposal_for_slot(
    self,
    slot_index: int,
    optimizing: List[Dict[str, Any]],
) -> Optional[str]:
    """确定当前时段应聚焦的 proposal。

    规则（v6.8.1）：
    - 跨天/跨周时通过 last_proposal_id 重新校准轮转位置。
    - 先自动重试所有 failed job（attempts < MAX_JOB_ATTEMPTS）。
    - 若上一个时段聚焦的 proposal 本轮未完成，继续聚焦它。
    - 若已完成或卡住（达到最大重试次数），则推进到下一个 proposal。
    - 跳过被卡住的 proposal（failed job 达到最大重试次数）。
    """
    if not optimizing:
        return None

    state = _load_focus_state()
    last_slot_index = state.get("last_slot_index", -1)
    last_proposal_index = state.get("last_proposal_index", 0)
    last_day_key = state.get("last_day_key", "")

    # 跨天保持轮转位置
    current_day = _get_current_day_key()
    if current_day != last_day_key:
        state["last_day_key"] = current_day
        _save_focus_state(state)

    # 跨周重新平衡：用 last_proposal_id 校准索引
    last_proposal_index = _rebalance_index(state, optimizing)
    last_slot_index = state.get("last_slot_index", -1)

    # 当前时段与上一时段不同，可能需要切换 proposal
    if slot_index != last_slot_index:
        # 先自动重试上一个 proposal 的 failed job
        prev_index = last_proposal_index % len(optimizing)
        prev_pid = optimizing[prev_index]["proposal_id"]
        try:
            retried = _auto_retry_failed_jobs(self, prev_pid)
            if retried > 0 and _log:
                _log.info(f"[{prev_pid}] 自动重试了 {retried} 个 failed job")
        except Exception:
            pass

        # 检查上一时段聚焦的 proposal 是否已完成本轮或卡住
        try:
            prev_jobs = self._get_jobs(prev_pid)
            prev_state = self._get_proposal_state(prev_pid)
            current_round = prev_state.get("optimization_rounds", 0) + 1 if prev_state else 1
            stuck = _is_proposal_stuck(self, prev_pid)
            if not stuck and not _is_round_complete(prev_jobs, prev_pid, current_round):
                # 未完成也未卡住，继续聚焦上一个
                state["last_slot_index"] = slot_index
                state["last_proposal_id"] = prev_pid
                _save_focus_state(state)
                return prev_pid
        except Exception:
            pass
        # 已完成或卡住，推进到下一个
        next_index = (last_proposal_index + 1) % len(optimizing)
        state["last_slot_index"] = slot_index
        state["last_proposal_index"] = next_index
        state["last_proposal_id"] = optimizing[next_index]["proposal_id"]
        _save_focus_state(state)
    else:
        # 同一时段内，保持当前聚焦
        next_index = last_proposal_index % len(optimizing)

    # 检查选中的 proposal 是否卡住，若卡住则跳过
    pid = optimizing[next_index]["proposal_id"]
    if _is_proposal_stuck(self, pid):
        if _log:
            _log.warning(f"[{pid}] 被卡住（达到最大重试次数），跳过到下一个")
        next_index = (next_index + 1) % len(optimizing)
        state["last_proposal_index"] = next_index
        state["last_proposal_id"] = optimizing[next_index]["proposal_id"]
        _save_focus_state(state)
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
    """扫描指定 proposal，返回所有依赖满足且 pending 的 job。

    自动重试 failed job（attempts < MAX_JOB_ATTEMPTS）。
    """
    ready: List[Dict[str, Any]] = []
    try:
        self._refresh_stale_jobs(proposal_id)
        self.sync_checkpoint(proposal_id)
        # 自动重试 failed job
        _auto_retry_failed_jobs(self, proposal_id)
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
    """v6.8.1 全局微调度器入口：时段聚焦 + 单任务节流 + 自动重试 + 看板 + 报告。"""
    if _log:
        _log.info("=== 微调度器启动 ===")

    started_at = time.time()
    executed: List[Dict[str, Any]] = []
    generated_reports: List[str] = []

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
        _update_kanban(slot_info, None, [], [], self)
        if _log:
            _log.info(msg)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg}

    # 3. 选择聚焦 proposal
    focus_pid = self._focus_proposal_for_slot(slot_index, optimizing)
    if not focus_pid:
        msg = "无法确定聚焦 proposal"
        _update_kanban(slot_info, None, optimizing, [], self)
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
        # 生成优化报告
        report_path = _generate_round_report(self, focus_pid, current_round)
        if report_path:
            generated_reports.append(report_path)
        _update_kanban(slot_info, focus_pid, optimizing, [], self)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg,
                "generated_reports": generated_reports}

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

                # 如果执行成功，检查本轮是否已完成，生成优化报告
                if result.get("success"):
                    post_jobs = self._get_jobs(proposal_id)
                    post_round = prop_state.get("optimization_rounds", 0) + 1 if prop_state else 1
                    if _is_round_complete(post_jobs, proposal_id, post_round):
                        report_path = _generate_round_report(self, proposal_id, post_round)
                        if report_path:
                            generated_reports.append(report_path)
                            if _log:
                                _log.info(f"已生成优化报告: {report_path}")

    summary = {
        "success": True,
        "executed_count": len(executed),
        "executed": executed,
        "focus_proposal": focus_pid,
        "slot_index": slot_index,
        "slot": f"{slot_start}-{slot_end}",
        "elapsed_s": round(time.time() - started_at, 2),
        "at": now_utc(),
        "generated_reports": generated_reports,
    }

    # 更新看板
    _update_kanban(slot_info, focus_pid, optimizing, executed, self)

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
