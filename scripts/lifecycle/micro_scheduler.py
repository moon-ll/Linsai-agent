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

# 生命周期任务映射（lifecycle job → task_manager task）
LIFECYCLE_TASK_MAP_PATH = PROJECT_ROOT / "memory" / "lifecycle-task-map.json"

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
    """加载聚焦轮询状态（加锁）。"""
    FOCUS_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with file_lock("lifecycle-focus-state"):
        return load_json(FOCUS_STATE_PATH, default={
            "last_slot_index": -1,
            "last_proposal_index": 0,
            "last_proposal_id": "",
            "queue": [],
            "focus_history": [],
        })


def _save_focus_state(state: Dict[str, Any]) -> None:
    """保存聚焦轮询状态（加锁）。"""
    FOCUS_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = now_utc()
    with file_lock("lifecycle-focus-state"):
        save_json(FOCUS_STATE_PATH, state)


def _sync_queue(state: Dict[str, Any], optimizing: List[Dict[str, Any]]) -> List[str]:
    """同步队列与 optimizing 列表。

    规则：
    - 从 queue 中移除不在 optimizing 中的 proposal。
    - 将 optimizing 中新增的 proposal 追加到 queue 末尾。
    - 保持 queue 中已有的顺序。
    - 若 queue 为空，用 optimizing 顺序初始化。
    """
    opt_ids = [p["proposal_id"] for p in optimizing]
    queue = state.get("queue", [])

    # 移除已不在 optimizing 中的 proposal
    queue = [pid for pid in queue if pid in opt_ids]

    # 追加新增 proposal
    for pid in opt_ids:
        if pid not in queue:
            queue.append(pid)

    # 若 queue 为空则用 optimizing 初始化
    if not queue:
        queue = list(opt_ids)

    state["queue"] = queue
    return queue


def _move_to_queue_end(state: Dict[str, Any], proposal_id: str) -> None:
    """将完成的 proposal 移动到队列末尾。"""
    queue = state.get("queue", [])
    if proposal_id in queue:
        queue.remove(proposal_id)
        queue.append(proposal_id)
    state["queue"] = queue


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
    """扫描 proposal 的 failed job，只重试阻塞 pending 任务的 failed 依赖。

    若某个 failed job 被 pending 任务的 depends_on 引用，才重置为 pending。
    避免无差别重试所有 failed job，减少无意义执行。
    返回重置的 job 数量。
    """
    jobs = self._get_jobs(proposal_id)
    if not jobs:
        return 0

    # 收集所有 pending job 的依赖集合
    pending_deps: set = set()
    for job in jobs:
        if job.get("status") == JOB_STATUS_PENDING:
            for dep in job.get("depends_on", []):
                pending_deps.add(dep)

    changed = False
    retry_count = 0
    for job in jobs:
        if job.get("status") == JOB_STATUS_FAILED and job.get("job_id") in pending_deps:
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
                        f"[{proposal_id}] 依赖链重试 job {job['job_id']} "
                        f"(attempt {attempts + 1}/{MAX_JOB_ATTEMPTS})"
                    )
    if changed:
        self._save_jobs(proposal_id, jobs)
    return retry_count


def _is_proposal_stuck(self, proposal_id: str) -> bool:
    """检查 proposal 是否被卡住。

    仅当有 failed job 达到最大重试次数，且该 job 阻塞了某个 pending 任务时，
    才视为卡住。孤立 orphaned failed job 不阻塞进度。
    """
    jobs = self._get_jobs(proposal_id)
    if not jobs:
        return False

    # 收集 pending 任务的依赖集合
    pending_deps: set = set()
    for job in jobs:
        if job.get("status") == JOB_STATUS_PENDING:
            for dep in job.get("depends_on", []):
                pending_deps.add(dep)

    for job in jobs:
        if job.get("status") == JOB_STATUS_FAILED:
            attempts = job.get("attempts", 0)
            if attempts >= MAX_JOB_ATTEMPTS and job.get("job_id") in pending_deps:
                return True
    return False


def _has_any_ready_or_failed_job(self, proposal_id: str) -> bool:
    """检查 proposal 是否有待执行或可重试的 job。

    只计入 pending job 和阻塞 pending 任务的 failed job。
    孤立 orphaned failed job 不计入，避免误判为"还有工作可做"。
    """
    jobs = self._get_jobs(proposal_id)
    if not jobs:
        return False

    pending_deps: set = set()
    for job in jobs:
        if job.get("status") == JOB_STATUS_PENDING:
            pending_deps.add(job["job_id"])
            for dep in job.get("depends_on", []):
                pending_deps.add(dep)

    for job in jobs:
        status = job.get("status", "")
        if status == JOB_STATUS_PENDING:
            return True
        if status == JOB_STATUS_FAILED and job.get("job_id") in pending_deps:
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


def _check_and_transition(self, proposal_id: str) -> Optional[Dict[str, Any]]:
    """检查 proposal 是否达标，若达标则 transition 到 pending_review。

    在生成优化报告后调用。
    返回 transition 结果，若未达标返回 None。
    """
    try:
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return None
        threshold = self._get_quality_threshold(prop_state.get("project_type", "general"))
        done_result = self._check_done(proposal_id, threshold)
        if done_result.get("done"):
            if _log:
                _log.info(
                    f"[{proposal_id}] 达标，流转到 pending_review: {done_result['reason']}"
                )
            transition_result = self.transition(
                proposal_id, "pending_review", reason=done_result["reason"]
            )
            return {
                "done": True,
                "reason": done_result["reason"],
                "transition": transition_result,
            }
    except Exception as e:
        if _log:
            _log.warning(f"[{proposal_id}] 达标检查失败: {e}")
    return None


# ---------------------------------------------------------------------------
# 任务系统集成（lifecycle → task_manager）
# ---------------------------------------------------------------------------

_LIFECYCLE_TASK_CACHE: Optional[Dict[str, str]] = None


def _load_lifecycle_task_map() -> Dict[str, str]:
    """加载生命周期任务映射（惰性加载 + 缓存）。"""
    global _LIFECYCLE_TASK_CACHE
    if _LIFECYCLE_TASK_CACHE is None:
        LIFECYCLE_TASK_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        _LIFECYCLE_TASK_CACHE = load_json(LIFECYCLE_TASK_MAP_PATH, default={})
    return _LIFECYCLE_TASK_CACHE


def _save_lifecycle_task_map() -> None:
    """持久化生命周期任务映射。"""
    global _LIFECYCLE_TASK_CACHE
    if _LIFECYCLE_TASK_CACHE is not None:
        LIFECYCLE_TASK_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        with file_lock("lifecycle-task-map"):
            save_json(LIFECYCLE_TASK_MAP_PATH, _LIFECYCLE_TASK_CACHE)


def _get_lifecycle_task_id(proposal_id: str, round_num: int) -> Optional[str]:
    """从映射中获取 lifecycle 任务 ID。"""
    mapping = _load_lifecycle_task_map()
    return mapping.get(f"{proposal_id}:r{round_num}")


def _set_lifecycle_task_id(proposal_id: str, round_num: int, task_id: str) -> None:
    """在映射中记录 lifecycle 任务 ID。"""
    mapping = _load_lifecycle_task_map()
    mapping[f"{proposal_id}:r{round_num}"] = task_id
    _save_lifecycle_task_map()


def _sync_lifecycle_to_task_manager(self) -> Dict[str, Any]:
    """同步生命周期状态到 task_manager 任务系统。

    为每个 optimizing proposal 的当前 round 创建/更新任务，
    让用户可以在 Web 任务面板看到生命周期优化进度。
    """
    try:
        import task_manager as tm
    except ImportError:
        return {"synced": 0, "error": "task_manager 不可用"}

    try:
        # 同步 pending_review 和 archived 的已完成任务
        synced_all = []
        for status_name in ("optimizing", "pending_review", "archived"):
            try:
                proposals = self.list_by_status(status_name)
            except Exception as e:
                if _log:
                    _log.warning(f"[task-sync] 获取 {status_name} 列表失败: {e}")
                continue
            if not proposals:
                if _log:
                    _log.info(f"[task-sync] {status_name} 区为空，跳过")
                continue
            for prop in proposals:
                pid = prop["proposal_id"]
                result = _sync_single_proposal_to_task(self, tm, pid, status_name)
                if result:
                    synced_all.append(result)

        if _log:
            _log.info(f"[task-sync] 完成: 同步 {len(synced_all)} 个 proposal")
        return {"synced": len(synced_all), "details": synced_all}
    except Exception as e:
        if _log:
            _log.warning(f"[task-sync] 同步失败: {e}")
        return {"synced": 0, "error": str(e)}


def _sync_single_proposal_to_task(
    self, tm: Any, proposal_id: str, status_name: str,
) -> Optional[Dict[str, Any]]:
    """同步单个 proposal 到 task_manager。"""
    prop_state = self._get_proposal_state(proposal_id)
    if not prop_state:
        return None

    current_round = prop_state.get("optimization_rounds", 0) + 1
    jobs = self._get_jobs(proposal_id)
    round_jobs = [j for j in jobs if j.get("round") == current_round]
    total = len(round_jobs)
    done = sum(1 for j in round_jobs if j.get("status") == JOB_STATUS_DONE)
    failed = sum(1 for j in round_jobs if j.get("status") == JOB_STATUS_FAILED)
    progress = int(done / total * 100) if total > 0 else 0
    round_complete = total > 0 and done == total

    # 检查是否已有 task
    existing_task_id = _get_lifecycle_task_id(proposal_id, current_round)

    # 若 proposal 已不在 optimizing 中，检查是否有未完成的 task
    is_optimizing = status_name == "optimizing"

    title = f"「优化」{proposal_id} 第{current_round}轮"
    desc_lines = [
        f"生命周期自动优化任务",
        f"Proposal: {proposal_id}",
        f"轮次: {current_round}",
        f"状态: {'优化中' if is_optimizing else status_name}",
        f"进度: {done}/{total} job 完成 ({failed} 失败)",
    ]
    if round_jobs:
        # 按模块分组
        sections = {}
        for j in round_jobs:
            sk = j.get("section_key", "unknown")
            if sk not in sections:
                sections[sk] = {"done": 0, "total": 0}
            sections[sk]["total"] += 1
            if j.get("status") == JOB_STATUS_DONE:
                sections[sk]["done"] += 1
        desc_lines.append("")
        desc_lines.append("模块进度:")
        for sk, st in sections.items():
            desc_lines.append(f"  {sk}: {st['done']}/{st['total']}")
    description = "\n".join(desc_lines)

    if existing_task_id:
        # 更新已有任务
        try:
            task = tm.get_task(existing_task_id)
        except Exception:
            task = None

        if task:
            try:
                tm.update_task(existing_task_id, progress=progress, description=description)
                if round_complete and task.get("status") != "completed":
                    tm.transition_task(existing_task_id, "completed")
                elif not round_complete and task.get("status") == "backlog":
                    tm.transition_task(existing_task_id, "active")
                return {
                    "proposal_id": proposal_id,
                    "round": current_round,
                    "action": "updated",
                    "task_id": existing_task_id,
                    "progress": progress,
                }
            except Exception as e:
                if _log:
                    _log.warning(f"[task-sync] 更新任务 {existing_task_id} 失败: {e}")
                return None

    # 创建新任务
    try:
        score = prop_state.get("last_score", 0.0)
        project_name = proposal_id[:20]
        task_id, path = tm.create_task(
            title=title,
            category="research",
            priority="medium",
            description=description,
            project=project_name,
            assignee="hermes",
        )
        # 记录映射
        _set_lifecycle_task_id(proposal_id, current_round, task_id)

        # 如果已经开始执行，设为 active
        if round_complete or done > 0:
            tm.transition_task(task_id, "active")
        if round_complete:
            tm.transition_task(task_id, "completed")
        else:
            tm.update_progress(task_id, progress)

        if _log:
            _log.info(f"[task-sync] 创建任务 {task_id} 用于 {proposal_id} r{current_round}")
        return {
            "proposal_id": proposal_id,
            "round": current_round,
            "action": "created",
            "task_id": task_id,
            "progress": progress,
        }
    except Exception as e:
        if _log:
            _log.warning(f"[task-sync] 创建任务失败: {e}")
        return None


def _sync_previous_rounds_to_task_manager(self) -> Dict[str, Any]:
    """同步历史轮次（已完成但未创建 task 的轮次）到 task_manager。

    在首次启用集成时，补全之前已完成轮次的任务记录。
    """
    try:
        import task_manager as tm
    except ImportError:
        return {"synced": 0}

    synced = []
    for status_name in ("optimizing", "pending_review", "archived"):
        try:
            proposals = self.list_by_status(status_name)
        except Exception as e:
            if _log:
                _log.warning(f"[task-sync-history] 获取 {status_name} 列表失败: {e}")
            continue
        if not proposals:
            if _log:
                _log.info(f"[task-sync-history] {status_name} 区为空，跳过")
            continue
        for prop in proposals:
            pid = prop["proposal_id"]
            prop_state = self._get_proposal_state(pid)
            if not prop_state:
                continue
            rounds_done = prop_state.get("optimization_rounds", 0)
            for r in range(1, rounds_done + 1):
                if _get_lifecycle_task_id(pid, r) is not None:
                    continue  # 已有映射
                # 创建已完成的历史任务
                title = f"「优化」{pid} 第{r}轮"
                description = (
                    f"生命周期自动优化任务（历史同步）\n"
                    f"Proposal: {pid}\n"
                    f"轮次: {r}\n状态: 已完成"
                )
                project_name = pid[:20]
                try:
                    task_id, path = tm.create_task(
                        title=title, category="research", priority="medium",
                        description=description, project=project_name,
                        assignee="hermes",
                    )
                    _set_lifecycle_task_id(pid, r, task_id)
                    # backlog → active → completed 两步流转
                    tm.transition_task(task_id, "active")
                    tm.transition_task(task_id, "completed")
                    synced.append({"proposal_id": pid, "round": r, "task_id": task_id})
                except Exception as e:
                    if _log:
                        _log.warning(f"[task-sync] 创建历史任务 {pid} r{r} 失败: {e}")
                    continue
    return {"synced": len(synced), "details": synced}


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

        # 查询 task_manager 中对应的任务状态
        task_status = None
        task_progress = 0
        task_id_val = _get_lifecycle_task_id(pid, round_num)
        if task_id_val:
            try:
                import task_manager as _tm
                try:
                    task = _tm.get_task(task_id_val)
                    if task:
                        task_status = task.get("status", "unknown")
                        task_progress = task.get("progress", 0)
                except Exception:
                    pass
            except ImportError:
                pass

        proposals_status.append({
            "proposal_id": pid,
            "round": round_num,
            "score": round(score, 2),
            "jobs": f"{done}/{total}",
            "failed": failed,
            "pending": pending,
            "stuck": stuck,
            "next_job": next_job,
            "task_id": task_id_val,
            "task_status": task_status,
            "task_progress": task_progress,
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

    # 收集 task_manager 全局统计
    task_stats = {}
    try:
        import task_manager as _tm
        try:
            all_tasks = _tm.list_tasks()
            task_stats = {
                "total": len(all_tasks),
                "backlog": sum(1 for t in all_tasks if t.get("status") == "backlog"),
                "active": sum(1 for t in all_tasks if t.get("status") == "active"),
                "completed": sum(1 for t in all_tasks if t.get("status") == "completed"),
                "lifecycle_tasks": sum(1 for t in all_tasks
                                       if t.get("title", "").startswith("「优化」")),
            }
        except Exception:
            pass
    except ImportError:
        pass

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
        "task_sync": {
            "enabled": True,
            "stats": task_stats,
            "mapping_count": len(_load_lifecycle_task_map()),
        },
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
    - 先同步队列（移除已归档的，追加新增的）。
    - 若 last_proposal_id 在队列中，找到其索引。
    - 若不在队列中，重置索引到队列头部。
    - 若索引超出范围，回绕到 0。
    """
    queue = _sync_queue(state, optimizing)

    last_id = state.get("last_proposal_id", "")
    last_index = state.get("last_proposal_index", 0)
    n = len(queue)
    if n == 0:
        return 0

    # 优先通过 last_proposal_id 在队列中定位
    if last_id:
        for i, pid in enumerate(queue):
            if pid == last_id:
                if i != last_index:
                    state["last_proposal_index"] = i
                return i

    # last_proposal_id 不在队列中（被归档），重置到队列头部
    state["last_proposal_index"] = 0
    return 0


def _focus_proposal_for_slot(
    self,
    slot_index: int,
    optimizing: List[Dict[str, Any]],
) -> Optional[str]:
    """确定当前时段应聚焦的 proposal（v6.8.2 循环队列）。

    规则：
    - 使用循环队列管理课题轮转。
    - 跨天保持队列不变，跨周同步队列（移除已归档，追加新增）。
    - 若上一个时段聚焦的 proposal 本轮未完成，继续聚焦它。
    - 若已完成或卡住，将其移动到队列末尾，聚焦下一个。
    - 跳过被卡住的 proposal。
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

    # 同步队列并重新校准索引
    queue = _sync_queue(state, optimizing)
    last_proposal_index = _rebalance_index(state, optimizing)
    last_slot_index = state.get("last_slot_index", -1)

    # 当前时段与上一时段不同，可能需要切换 proposal
    if slot_index != last_slot_index:
        # 先自动重试上一个 proposal 的 failed job
        prev_pid = queue[last_proposal_index % len(queue)]
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
        # 已完成或卡住：移动到队列末尾，推进到下一个
        _move_to_queue_end(state, prev_pid)
        queue = state.get("queue", [])
        # 找到 prev_pid 移尾后的新队列中，下一个应聚焦的 proposal
        # prev_pid 已被移尾，所以下一个就是队列头
        next_pid = queue[0] if queue else None
        if next_pid is None:
            return None
        # 找出 next_pid 的索引
        next_index = 0
        for i, pid in enumerate(queue):
            if pid == next_pid:
                next_index = i
                break
        state["last_slot_index"] = slot_index
        state["last_proposal_index"] = next_index
        state["last_proposal_id"] = next_pid
        _save_focus_state(state)
        pid = next_pid
    else:
        # 同一时段内，保持当前聚焦
        pid = queue[last_proposal_index % len(queue)]

    # 检查选中的 proposal 是否卡住，若卡住则跳过
    if _is_proposal_stuck(self, pid):
        if _log:
            _log.warning(f"[{pid}] 被卡住（达到最大重试次数），跳过到下一个")
        _move_to_queue_end(state, pid)
        queue = state.get("queue", [])
        next_pid = queue[0] if queue else None
        if next_pid is None:
            return None
        next_index = 0
        for i, p in enumerate(queue):
            if p == next_pid:
                next_index = i
                break
        state["last_proposal_index"] = next_index
        state["last_proposal_id"] = next_pid
        _save_focus_state(state)
        pid = next_pid

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
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg, "skip_reason": "out_of_slot"}

    slot_index, (slot_start, slot_end) = slot_info
    if _log:
        _log.info(f"当前时段: {slot_start}-{slot_end} (#{slot_index})")

    # 2. 获取 optimizing proposal 列表
    try:
        optimizing = self.list_by_status("optimizing")
    except Exception as e:
        if _log:
            _log.warning(f"[micro-scheduler] 获取 optimizing 列表失败: {e}")
        optimizing = []

    if not optimizing:
        msg = "optimizing 区为空"
        _update_kanban(slot_info, None, [], [], self)
        if _log:
            _log.info(msg)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg, "skip_reason": "no_optimizing"}

    # 3. 选择聚焦 proposal
    focus_pid = self._focus_proposal_for_slot(slot_index, optimizing)
    if not focus_pid:
        msg = "无法确定聚焦 proposal"
        _update_kanban(slot_info, None, optimizing, [], self)
        if _log:
            _log.info(msg)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg, "skip_reason": "no_focus"}

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
        # 递增 optimization_rounds（微调度器路径）
        if prop_state:
            prop_state["optimization_rounds"] = current_round
            self._set_proposal_state(focus_pid, prop_state)
        # 生成优化报告
        report_path = _generate_round_report(self, focus_pid, current_round)
        if report_path:
            generated_reports.append(report_path)
        # 检查是否达标，达标则 transition 到 pending_review
        transition_result = _check_and_transition(self, focus_pid)
        if transition_result:
            if _log:
                _log.info(
                    f"[{focus_pid}] 达标已流转到 pending_review: {transition_result['reason']}"
                )
            # 达标后从队列中移除（不再在 optimizing 中）
            state = _load_focus_state()
            queue = state.get("queue", [])
            if focus_pid in queue:
                queue.remove(focus_pid)
            state["queue"] = queue
            _save_focus_state(state)
        else:
            # 未达标但本轮完成，移动到队列末尾
            state = _load_focus_state()
            _move_to_queue_end(state, focus_pid)
            _save_focus_state(state)
        _update_kanban(slot_info, focus_pid, optimizing, [], self)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg,
                "skip_reason": "round_complete", "transitioned": transition_result is not None,
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
                    # 刷新 prop_state，避免使用过时数据
                    post_prop_state = self._get_proposal_state(proposal_id)
                    post_round = post_prop_state.get("optimization_rounds", 0) + 1 if post_prop_state else 1
                    if _is_round_complete(post_jobs, proposal_id, post_round):
                        # 递增 optimization_rounds（微调度器路径）
                        if post_prop_state:
                            post_prop_state["optimization_rounds"] = post_round
                            self._set_proposal_state(proposal_id, post_prop_state)
                        report_path = _generate_round_report(self, proposal_id, post_round)
                        if report_path:
                            generated_reports.append(report_path)
                            if _log:
                                _log.info(f"已生成优化报告: {report_path}")
                        # 检查是否达标，达标则 transition 到 pending_review
                        transition_result = _check_and_transition(self, proposal_id)
                        if transition_result:
                            if _log:
                                _log.info(
                                    f"[{proposal_id}] 达标已流转到 pending_review"
                                )
                            # 达标后从队列中移除
                            state = _load_focus_state()
                            queue = state.get("queue", [])
                            if proposal_id in queue:
                                queue.remove(proposal_id)
                            state["queue"] = queue
                            _save_focus_state(state)
                        else:
                            # 未达标但本轮完成，移动到队列末尾
                            state = _load_focus_state()
                            _move_to_queue_end(state, proposal_id)
                            _save_focus_state(state)

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

    # 同步生命周期状态到 task_manager 任务系统
    try:
        task_sync_result = _sync_lifecycle_to_task_manager(self)
        if task_sync_result.get("synced", 0) > 0:
            summary["task_sync"] = task_sync_result
            if _log:
                _log.info(f"[task-sync] 同步了 {task_sync_result['synced']} 个任务")
    except Exception as e:
        if _log:
            _log.warning(f"[task-sync] 同步异常: {e}")

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
