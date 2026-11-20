#!/usr/bin/env python3
"""生命周期 cron 全局微调度器（v6.8.0）。

目标：
- 工作日按 4 个时段轮流聚焦单个 proposal。
- 每个时段只执行当前聚焦 proposal 的 pending job。
- 同一 proposal 的 researcher 4 子任务可在时段内连贯完成。
- 全局每 15 分钟只执行一个任务，避免并发过载。

时段定义（可配置）：
    00:30-03:30, 04:00-08:00, 08:30-12:30, 18:30-22:30
"""

from __future__ import annotations

import os
import time
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

from .constants import (
    HERMES_PROFILE,
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    MAX_JOB_ATTEMPTS,
    MAX_SOFT_STUCK_SLOTS,
    MICRO_SCHEDULER_NAME,
    MICRO_SCHEDULER_SCHEDULE,
    STALE_RUNNING_SECONDS,
    STEP_CRITIC,
    STEP_GAP_IDENTIFY,
    STEP_IDEA_REVIEW,
    STEP_LIT_NOTE,
    STEP_LIT_READ,
    STEP_LIT_SEARCH,
    STEP_MONITOR,
    STEP_WRITER,
    STEP_UPDATE_VISION,
    STEP_UPDATE_METHOD_MANUAL,
)
from .utils import _is_stale, _make_job_id

# v7.2.71: 轮转双键的跨模块单一真相源（独立零依赖模块，避免 import
# lifecycle 包时连带拉起 proposal_lifecycle 全链）
from rotation_queue import (
    MAX_ROTATION_WIP,
    ROTATION_QUEUE_FULL_KEY,
    ROTATION_QUEUE_KEY,
    get_rotation_queue,
    sanitize_rotation_queue,
    set_rotation_queue,
)

def _section_mean_score(prop_state: Dict[str, Any], round_num: int) -> Optional[float]:
    """v6.10.27: 轮次章节 4 维口径均值（排除 references 2 维收尾分）。

    每轮步骤序固定 references 收尾，score_history 末条与 last_score 通常是
    2 维专用口径（rigor/completeness），与章节 4 维加权分不可比（实测
    attosecond r5 章节均值 0.77 vs references 收尾 0.665）。取均值前先按
    caliber 过滤；caliber 缺失的历史条目标记后按 focus_section 兜底，
    与周报 sec 系列、completion 逃生阀同口径。返回 None 表示该轮无章节分。
    """
    entries = [
        h for h in (prop_state.get("score_history") or [])
        if h.get("round") == round_num
        and (h.get("caliber") == "section_4d"
             or (not h.get("caliber") and h.get("focus_section") != "references"))
    ]
    vals = []
    for h in entries:
        try:
            vals.append(float(h.get("score", 0.0)))
        except (TypeError, ValueError):
            continue
    if not vals:
        return None
    return sum(vals) / len(vals)


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

# v7.1.8: r1 启动失败告警缓存路径——新进 optimizing 课题 24h 内未完成首个
# job 时触发告警（飞书/lifecycle_monitor）。复用 lifecycle_monitor 的
# 告警缓存结构，独立于 lc-micro-scheduler 健康检查。
R1_START_ALERT_PATH = PROJECT_ROOT / "memory" / "r1-start-alerts.json"
R1_START_TIMEOUT_HOURS = 24  # r1 启动失败超时阈值
R1_START_ALERT_DEDUP_HOURS = 6  # 同课题告警去重窗口

# 步骤在链中的顺序，用于优先级排序（数字越小越优先继续）
# v6.8.3-fix13: 加入 STEP_UPDATE_VISION / STEP_UPDATE_METHOD_MANUAL，
# 否则它们的优先级默认为 99（最低），会被下一轮的 critic（优先级 0）抢占，
# 导致本轮 derived job 滞后执行，轮次完成检测和报告生成时机异常。
_CHAIN_ORDER = {
    STEP_IDEA_REVIEW: -1,  # v6.8.26: 研究设想评审最先执行
    STEP_CRITIC: 0,
    STEP_GAP_IDENTIFY: 1,
    STEP_LIT_SEARCH: 2,
    STEP_LIT_READ: 3,
    STEP_LIT_NOTE: 4,
    STEP_WRITER: 5,
    STEP_MONITOR: 6,
    STEP_UPDATE_VISION: 7,
    STEP_UPDATE_METHOD_MANUAL: 8,
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

    v7.2.105（BUG-34）：剔除轮转名单中的**非法成员**（测试夹具占位 id
    等）。原实现只按「是否在 optimizing 名单中」过滤，而占位 id 永远不
    在名单中——但夹具污染期间 optimizing 名单可能整体为空（无课题
    在 optimizing 阶段），此时 `if not queue: queue = opt_ids` 分支不
    触发，污染项永久留存 → 真实课题 queue_index 恒为 -1 →
    monitor 误判 blocked（真停滞）+ promote 人工提升被拒。
    """
    opt_ids = [p["proposal_id"] for p in optimizing]
    # v7.2.66: 冻结过滤（定案 4）——scheduler_frozen 的课题不参与轮转
    # （pull-based：解冻只需清标志，_sync_queue 下个 tick 自动召回）
    frozen = {p["proposal_id"] for p in optimizing if p.get("scheduler_frozen")}
    queue = get_rotation_queue(state)

    # v7.2.105（BUG-34）：先剔除非法成员（测试夹具占位 id 等）。
    # 白名单 = 真实课题 id 集合（_lifecycle.json 的 proposals）∪ 当前
    # optimizing 名单；读不到时 sanitize 退化为形态判定（fail-open）。
    known = _known_proposal_ids()
    if known is not None:
        known = known | set(opt_ids)
    queue, dropped = sanitize_rotation_queue(queue, known)
    if dropped and _log:
        _log.warning(
            f"[scheduler] 轮转名单剔除 {len(dropped)} 个非法成员"
            f"（疑似测试夹具污染）：{dropped[:5]}"
        )

    # 移除已不在 optimizing 中（或已冻结）的 proposal
    queue = [pid for pid in queue if pid in opt_ids and pid not in frozen]

    # 追加新增 proposal
    for pid in opt_ids:
        if pid not in queue and pid not in frozen:
            queue.append(pid)

    # 若 queue 为空则用 optimizing 初始化
    if not queue:
        queue = [pid for pid in opt_ids if pid not in frozen]

    # v7.2.66: WIP 硬窗口（定案 4）——轮转只看前 MAX_ROTATION_WIP 个，
    # 其余在 queue_full 中候补；成员晋级/归档/冻结后窗口自动下移。
    # 治的是 10 课题全冷轮转（5.5 天/课题才轮到 + 每轮轮转税 25-35%）。
    # v7.2.71: 经 set_rotation_queue 统一写双键（人工提升也走同一路径）。
    set_rotation_queue(state, queue)
    return state[ROTATION_QUEUE_KEY]


def _move_to_queue_end(state: Dict[str, Any], proposal_id: str) -> None:
    """将完成的 proposal 移动到队列末尾（v7.2.66: 窗口与候补单同步轮转）。"""
    for key in ("queue", "queue_full"):
        queue = state.get(key, [])
        if proposal_id in queue:
            queue.remove(proposal_id)
            queue.append(proposal_id)
        state[key] = queue


def _known_proposal_ids() -> Optional[set]:
    """读真实课题 id 集合（白名单），读不到返回 None（退化为形态判定）。"""
    try:
        path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
        data = load_json(path, default={})
        props = data.get("proposals") or {}
        if not props:
            return None
        return set(props.keys())
    except Exception:
        return None


def _repair_focus_queue(extra_ids: Optional[Iterable[str]] = None) -> Optional[List[str]]:
    """修复轮转名单中的非法成员（v7.2.105 / BUG-34）。

    为什么需要独立的修复入口：`_sync_queue` 的清理只发生在
    `_focus_proposal_for_slot` / `_rebalance_index` 路径上，而这两处都在
    `run_micro_scheduler` 的「optimizing 区为空」早退**之后**。当全部课题
    都推进到 pending_review / archived（optimizing 为空）时，`_sync_queue`
    永不执行 → 污染项永久留存 → ① 所有真实课题 queue_index 恒为 -1 →
    monitor 误判 blocked（真停滞）误发 stalled 告警；② promote 人工提升
    报「proposal 不在轮转名单中」→ 人工干预入口堵死。

    本函数在每个 tick 的最早期无条件执行（不依赖 optimizing 是否为空），
    只剔除非法成员（形态非法且不在真实课题白名单中），不改动真实课题的
    相对顺序。返回被剔除的成员列表（无则 None）。

    `extra_ids`（当前 optimizing 名单）并入白名单，堵住「课题已进轮转
    名单但 `_lifecycle.json` 尚未同步」的时序窗口——自愈会**写回**过滤后
    的名单，一旦误杀真实课题即等于把它永久移出轮转（静默饿死）。
    白名单读不到时（known=None）不并入 extra_ids：那会退化为「只有
    extra_ids 合法」的窄白名单，误杀面反而更大；此时走形态判定的
    fail-open 路径即可（真实课题 id 形态必然合规）。
    """
    try:
        state = _load_focus_state()
        known = _known_proposal_ids()
        if known is not None and extra_ids:
            known = known | set(extra_ids)
        changed = False
        dropped_total: List[str] = []
        for key in (ROTATION_QUEUE_KEY, ROTATION_QUEUE_FULL_KEY):
            raw = state.get(key) or []
            if not raw:
                continue
            kept, dropped = sanitize_rotation_queue(raw, known)
            if dropped:
                dropped_total.extend(dropped)
                state[key] = kept
                changed = True
        if changed:
            _save_focus_state(state)
            if _log:
                _log.warning(
                    f"[scheduler] 轮转名单剔除 {len(dropped_total)} 个非法成员"
                    f"（疑似测试夹具污染）：{dropped_total[:5]}"
                )
        return dropped_total or None
    except Exception as e:
        if _log:
            _log.warning(f"[scheduler] 轮转名单修复失败: {e}")
        return None


def _continuous_rotate_after_round(state: Dict[str, Any], focus_pid: str,
                                   current_round: int) -> Optional[str]:
    """v7.2.17: 完成一轮即连续轮转（替代 v6.8.20 的 slot_done 空转）。

    根因：slot_done 空转是 4 时段短窗（3-5h）时代设计；v6.9.87 不间断
    长窗（00:00-13:00）后代价放大——10-07 实证：课题 00:20 完成轮次后
    空转 12.7h，9 课题闲置、5 课题饿 48h+。且 run 主流程的 slot_done
    短路检查在 v6.9.90「窗口内完成即切换」之前 return，两套机制冲突。

    行为：快照对齐（_last_round_seen 防下次切入误切）+ 移队尾 +
    指向队头；返回下一课题 pid（无切换返回 None）。不写任何
    slot_X_done 标记（跨时段消费逻辑保留兼容旧残留）。
    """
    state.setdefault("_last_round_seen", {})[focus_pid] = current_round
    _move_to_queue_end(state, focus_pid)
    queue = state.get("queue", [])
    nxt = queue[0] if queue else None
    if nxt and nxt != focus_pid:
        for _i, _p in enumerate(queue):
            if _p == nxt:
                state["last_proposal_index"] = _i
                break
        state["last_proposal_id"] = nxt
        return nxt
    return None


def _count_consecutive_slots(state: Dict[str, Any], proposal_id: str) -> int:
    """统计 proposal_id 在聚焦历史中已连续聚焦几个不同时段。

    从最近一条往回数，统计连续相同 proposal_id 的不同 slot_index 数量。
    """
    history = state.get("focus_history", [])
    if not history:
        return 0

    seen_slots = set()
    count = 0
    for h in reversed(history):
        if h.get("proposal_id") == proposal_id:
            slot_idx = h.get("slot_index", -1)
            if slot_idx not in seen_slots:
                seen_slots.add(slot_idx)
                count += 1
        else:
            break
    return count


def _current_round_done_count(jobs: List[Dict[str, Any]], round_num: int) -> int:
    """统计指定轮次已完成 job 数（v6.9.39 软卡死推进信号）。

    软卡死判定此前只看 optimization_rounds（整轮完成才 +1）——一轮
    25-30 job 在 critic/writer 超时上限升至 1200s 后需 2-4 个时段才能
    完成，超过 MAX_SOFT_STUCK_SLOTS=2 个时段后即使 job 每时段都在
    实质推进（26/29、90% 进度）也会被判"轮次无推进"强制让出焦点
    （08-23 实证 quantum-geometry r1 26/29、berry r2 12/25 均被误切）。
    本函数提供 job 级进展信号：done 计数增加即视为推进。
    """
    return sum(
        1 for j in jobs
        if isinstance(j, dict)
        and j.get("round") == round_num
        and j.get("status") == JOB_STATUS_DONE
    )



def _manual_product_ok(prop_dir, round_jobs) -> bool:
    """v7.3.0: 手册产物检查——本轮含手册模块 job 时，手册须超过占位体积。

    prop_dir 为 proposal 的 04_proposal 目录（手册在其兄弟 03_method/）。
    本轮无手册 job（旧格式轮次/跳过轮）时恒 True。
    """
    if not any(j.get("section_key") == "method_manual" for j in round_jobs):
        return True
    from .constants import MANUAL_MIN_BYTES
    manual_path = prop_dir.parent / "03_method" / "method-manual.md"
    return manual_path.exists() and manual_path.stat().st_size >= MANUAL_MIN_BYTES


def _is_round_complete(jobs: List[Dict[str, Any]], proposal_id: str, round_num: int) -> bool:
    """检查 proposal 的指定 round 是否全部完成（含 derived）。

    双重检查：
    1. 标签检查：pipeline_jobs 中该轮所有 job 的 status == done
    2. 产物检查：04_proposal/sections/ 下所有必需章节文件存在且非空
    两者都通过才判定完成，避免 job 标记 done 但产物缺失的假阳性。

    注意：本函数保留"全量完成"语义，已不再用于轮转让出门槛（轮转改用
    _is_core_round_complete），仅供历史兼容与全量收尾验证调用。
    """
    round_jobs = [j for j in jobs if j.get("round") == round_num]
    if not round_jobs:
        return False

    # 标签检查：所有 job 都 done
    all_done = all(j.get("status") == JOB_STATUS_DONE for j in round_jobs)
    if not all_done:
        return False

    # 产物检查：sections 目录下所有必需章节文件存在且非空
    try:
        from pathlib import Path
        prop_dir = Path(__file__).parent.parent.parent / "research_proposals" / "optimizing" / proposal_id / "04_proposal"
        required_sections = ["rationale.md", "content.md", "scheme.md", "full_review.md", "references.md"]
        for sec in required_sections:
            sec_path = prop_dir / "sections" / sec
            if not sec_path.exists() or sec_path.stat().st_size < 50:
                return False
        # v7.3.0: 本轮含手册模块 job 时，手册产物须超过占位体积
        if not _manual_product_ok(prop_dir, round_jobs):
            return False
    except Exception:
        # 产物检查出错时保守返回 False
        return False

    return True


# v7.2.10: 轮转让出门槛改用核心完成判定——derived 类 job
# （update_vision / update_method_manual）不算核心，每轮派发后会留 2-4
# 个尾巴积压在所有课题。旧 _is_round_complete 要求"全部 done"才让出，
# 导致 N 个课题都卡在末尾 derived 上、像 N 个课题同时处于"中间状态"，
# 违反循环队列"完成一轮即让出"的契约。
#
# _is_core_round_complete 只看核心步骤（writer / critic / gap_identify /
# lit_search / lit_read / lit_note / monitor / idea_review）——这些直接
# 贡献申请书内容或章节评审，必须做完本轮才可让出。derived（2 类）由
# 下一轮头部消化（_focus_proposal_for_slot 重入时优先派发剩余 derived）。
_CORE_ROUND_STEPS = frozenset({
    STEP_WRITER,
    STEP_CRITIC,
    STEP_GAP_IDENTIFY,
    STEP_LIT_SEARCH,
    STEP_LIT_READ,
    STEP_LIT_NOTE,
    STEP_MONITOR,
    STEP_IDEA_REVIEW,
})


def _is_core_round_complete(jobs: List[Dict[str, Any]], proposal_id: str, round_num: int) -> bool:
    """v7.2.10: 检查 proposal 指定轮次的**核心**步骤是否全部完成。

    与 _is_round_complete 的区别：本函数排除 derived 类 job
    （update_vision / update_method_manual）。这些 job 每轮追加、运行
    成本低、不直接影响申请书章节内容，放到下一轮头部消化不影响主链路
    质量，但能让所有课题立即让出焦点，避免 N 个课题同时卡"中间状态"。

    双重检查：
    1. 标签检查：本轮所有核心 step 的 status == done
       （若该轮没有任何核心 step，视为未完成，避免新进课题被误判）
    2. 产物检查：04_proposal/sections/ 下 5 个必需章节文件存在且非空

    返回 True 时调度器应让出焦点；返回 False 时本课题继续持有焦点。
    """
    round_jobs = [j for j in jobs if j.get("round") == round_num]
    if not round_jobs:
        return False

    # 核心 job 子集
    core_jobs = [j for j in round_jobs if j.get("step") in _CORE_ROUND_STEPS]
    if not core_jobs:
        # 该轮没有任何核心 step（极端：新进课题尚未派生核心任务），
        # 保守返回 False，让调度器继续推进派生链路
        return False

    # 标签检查：所有核心 job 都 done
    all_done = all(j.get("status") == JOB_STATUS_DONE for j in core_jobs)
    if not all_done:
        return False

    # 产物检查：sections 目录下所有必需章节文件存在且非空
    try:
        from pathlib import Path
        prop_dir = Path(__file__).parent.parent.parent / "research_proposals" / "optimizing" / proposal_id / "04_proposal"
        required_sections = ["rationale.md", "content.md", "scheme.md", "full_review.md", "references.md"]
        for sec in required_sections:
            sec_path = prop_dir / "sections" / sec
            if not sec_path.exists() or sec_path.stat().st_size < 50:
                return False
        # v7.3.0: 本轮含手册模块 job 时，手册产物须超过占位体积
        if not _manual_product_ok(prop_dir, round_jobs):
            return False
    except Exception:
        # 产物检查出错时保守返回 False
        return False

    return True


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
                # v6.8.27: 保留 last_error 记录最后一次失败原因（修复前会清空，
                # 导致 references-writer 14:35:29Z 超时失败后错误上下文丢失，
                # 下次失败时无法追溯是"超时"还是其他原因）。改为在 error_history
                # 追加历史，last_error 仅在下次执行成功后才清空。
                err = job.get("last_error", "")
                if err:
                    hist = job.get("error_history") or []
                    hist.append({"at": now_utc(), "error": err[:500], "attempts": attempts})
                    job["error_history"] = hist[-10:]  # 只保留最近 10 条
                job["status"] = JOB_STATUS_PENDING
                job["attempts"] = attempts + 1
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
            repair_attempts = job.get("repair_attempts", 0)
            # 注意：orchestrator repair 会把 attempts 重置为 0（见 orchestrator.py
            # _run_repair 的 failed→pending 重置逻辑），因此单看 attempts 无法
            # 识别"已被修复系统放弃"的 job——它会因 attempts 被反复清零而永远
            # 低于 MAX_JOB_ATTEMPTS。repair_attempts 单调递增，达到 MAX_JOB_ATTEMPTS
            # 表示修复系统已明确放弃该 job。两者任一达标即视为卡死，避免反复
            # 失败的 job 永远占用时段焦点、饿死其余 proposal。
            if (attempts >= MAX_JOB_ATTEMPTS or repair_attempts >= MAX_JOB_ATTEMPTS) \
               and job.get("job_id") in pending_deps:
                return True
    return False


def _check_r1_start_failures(self) -> List[Dict[str, Any]]:
    """v7.1.8: r1 启动失败检测——新进 optimizing 课题 24h 内未完成首个
    job 时告警。覆盖看板 r1 0/25 启动失败的诊断盲区（实证 2026-09-27
    quantum-geometry/ssh-weyl/mos2 三课题进入 optimizing 后 0 推进，
    pending jobs 挂 24h+ 无任何告警/健康监控）。

    返回待告警的 proposal 列表（含告警键、去重后是否真告警）。
    """
    alerts: List[Dict[str, Any]] = []
    try:
        optimizing = self.list_by_status("optimizing")
    except Exception:
        return alerts

    # 读取告警缓存（去重）
    cache: Dict[str, Any] = {}
    try:
        R1_START_ALERT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with file_lock("r1-start-alerts"):
            cache = load_json(R1_START_ALERT_PATH, default={"alerts": {}})
    except Exception:
        cache = {"alerts": {}}

    now = now_utc()
    now_dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
    new_cache = dict(cache.get("alerts", {}))

    for prop in optimizing:
        pid = prop["proposal_id"]
        try:
            ps = self._get_proposal_state(pid)
            if not ps:
                continue
            rounds = ps.get("optimization_rounds", 0)
            # 仅检测 r=0 课题
            if rounds > 0:
                # 已推进，清理旧告警记录
                new_cache.pop(pid, None)
                continue

            # 计算距 initialized_at/created_at 的小时数
            initialized_at = ps.get("initialized_at") or ps.get("created_at", "")
            if not initialized_at:
                continue
            try:
                init_dt = datetime.fromisoformat(initialized_at.replace("Z", "+00:00"))
            except Exception:
                continue
            elapsed_h = (now_dt - init_dt).total_seconds() / 3600.0
            if elapsed_h < R1_START_TIMEOUT_HOURS:
                continue

            # 检查是否真没完成任何 job
            jobs = self._get_jobs(pid)
            has_done = any(j.get("status") == JOB_STATUS_DONE for j in jobs)
            if has_done:
                new_cache.pop(pid, None)
                continue

            # 真告警——查 dedup
            last_sent = new_cache.get(pid, {}).get("last_sent", "")
            dedup_skip = False
            if last_sent:
                try:
                    last_dt = datetime.fromisoformat(last_sent.replace("Z", "+00:00"))
                    if (now_dt - last_dt).total_seconds() < R1_START_ALERT_DEDUP_HOURS * 3600:
                        dedup_skip = True
                except Exception:
                    pass

            if dedup_skip:
                continue

            # 写入告警
            new_cache[pid] = {
                "last_sent": now,
                "elapsed_hours": round(elapsed_h, 1),
                "jobs_total": len(jobs),
                "jobs_pending": sum(1 for j in jobs if j.get("status") == JOB_STATUS_PENDING),
                "last_score": ps.get("last_score", 0.0),
            }
            alerts.append({
                "proposal_id": pid,
                "elapsed_hours": round(elapsed_h, 1),
                "jobs_pending": sum(1 for j in jobs if j.get("status") == JOB_STATUS_PENDING),
            })
        except Exception as e:
            if _log:
                _log.debug(f"[r1-start] {pid} 检测异常: {e}")

    # 持久化
    try:
        with file_lock("r1-start-alerts"):
            save_json(R1_START_ALERT_PATH, {"alerts": new_cache})
    except Exception:
        pass

    if alerts and _log:
        _log.warning(
            f"[r1-start] 检测到 {len(alerts)} 个 r1 启动失败课题（>={R1_START_TIMEOUT_HOURS}h）"
        )
    return alerts


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


def _sync_proposal_to_kb(proposal_id: str) -> None:
    """轮次完成后自动同步 proposal 到知识库（v6.8.5）。

    调用 proposal_kb_sync.sync_proposal() 刷新 proposals/ 页面，
    调用 kb_proposal_reorg 刷新 versions/ 和 reports/ 页面。
    同步失败不影响主流程，仅记录日志。

    v7.3.70：测试模式下直接跳过。kb_proposal_reorg 以子进程执行，不继承
    patch_module_root 的隔离根，会把真实 knowledge/wiki/projects 的
    versions/reports 全量重写（实测 2026-11-08 全量回归把 30 个真实课题页
    的 created/updated 改成测试时刻），故测试进程内一律零写入。
    """
    if os.environ.get("LINSAI_TEST_MODE") == "1":
        return
    try:
        import proposal_kb_sync as pks
        sync = pks.ProposalKbSync()
        sync.sync_proposal(proposal_id)
        if _log:
            _log.info(f"[kb-sync] proposal 同步完成: {proposal_id}")
    except Exception as e:
        if _log:
            _log.warning(f"[kb-sync] proposal 同步失败: {e}")

    try:
        import subprocess as _sp
        import sys as _sys
        _script_dir = Path(__file__).resolve().parent.parent
        _sp.run(
            [_sys.executable, str(_script_dir / "kb_proposal_reorg.py"), "--apply"],
            capture_output=True, text=True, timeout=60,
        )
        if _log:
            _log.info(f"[kb-sync] versions/reports 同步完成: {proposal_id}")
    except Exception as e:
        if _log:
            _log.warning(f"[kb-sync] versions/reports 同步失败: {e}")


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
    # v6.10.27: 轮次总分取章节 4 维均值（排除 references 2 维收尾分），
    # 与周报 sec 系列同口径。旧逻辑取 round_scores[-1]——每轮 references
    # 收尾，末条 2 维分被当整篇分读（如 attosecond r5 章节均值 0.77 vs
    # references 收尾 0.665），报告与看板同轮分数互对不上。
    sec_mean = _section_mean_score(prop_state, round_num)
    latest = None
    if sec_mean is not None:
        sec_entries = [
            h for h in round_scores
            if h.get("caliber") == "section_4d"
            or (not h.get("caliber") and h.get("focus_section") != "references")
        ]
        latest = sec_entries[-1] if sec_entries else None
        final_score = sec_mean
        dim_scores = latest.get("dim_scores", {}) if latest else {}
    else:
        latest = round_scores[-1] if round_scores else None
        final_score = latest.get("score", 0.0) if latest else prop_state.get("last_score", 0.0)
        dim_scores = latest.get("dim_scores", {}) if latest else {}
    # references 2 维收尾分单独展示（与章节分不可比，不入总分）
    ref_entry = None
    for h in reversed(round_scores):
        if h.get("focus_section") == "references" or h.get("caliber") == "references_2d":
            ref_entry = h
            break
    ref_score = ref_entry.get("score", 0.0) if ref_entry else None
    prev_entry = None
    if latest is not None:
        for h in reversed(score_history):
            if h.get("round") == round_num:
                continue
            if h.get("caliber") == "section_4d" \
                    or (not h.get("caliber") and h.get("focus_section") != "references"):
                prev_entry = h
                break
    # 上一轮总分同样用其章节 4 维均值，保证前后可比
    prev_mean = _section_mean_score(prop_state, round_num - 1)
    prev_score = prev_mean if prev_mean is not None else (
        prev_entry.get("score", 0.0) if prev_entry else 0.0
    )
    prev_dim = prev_entry.get("dim_scores", {}) if prev_entry else {}

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

    # 维度评分（复用前面同源的 dim_scores / prev_dim）
    if dim_scores:
        for dim, score in dim_scores.items():
            prev = prev_dim.get(dim, 0.0)
            delta = score - prev
            delta_str = f"+{delta:.2f}" if delta > 0 else f"{delta:.2f}"
            report_lines.append(f"| {dim} | {prev:.2f} | {score:.2f} | {delta_str} |")

    ref_line = ""
    if ref_score is not None:
        ref_line = (
            f"| **引用审校（2维口径）** | — | **{ref_score:.2f}** | — |"
        )
    report_lines.extend([
        f"| **总分（4维章节均值）** | **{prev_score:.2f}** | **{final_score:.2f}** | **{final_score - prev_score:+.2f}** |",
        ref_line,
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

    # 弱维度分析（复用前面同源的 latest）
    if latest:
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

    v6.9.60 晋级完整性门：达标 ≠ 可晋级——本轮 job（含 update_vision/
    update_method_manual 等 derived job）必须全部 done。08-26 实证 bsv
    带 2 个 pending derived job 晋级 pending_review，造成流转不完整
    （同构于"生命周期边界信任状态"缺陷）。存在非 done job 时本次
    暂缓（记日志），下个 tick 自然重试；failed 由 repair/自动解锁
    兜底后仍可晋级，不死锁。
    """
    try:
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return None
        threshold = self._get_quality_threshold(prop_state.get("project_type", "general"))
        done_result = self._check_done(proposal_id, threshold)
        if done_result.get("done"):
            # 晋级完整性门：本轮存在非 done job → 暂缓
            current_round = prop_state.get("optimization_rounds", 0) + 1
            try:
                jobs = self._get_jobs(proposal_id)
            except Exception:
                jobs = []
            round_jobs = [j for j in jobs if j.get("round") == current_round]
            undone = [
                j for j in round_jobs
                if j.get("status") not in (JOB_STATUS_DONE,)
            ]
            if round_jobs and undone:
                if _log:
                    _log.info(
                        f"[{proposal_id}] 达标但本轮尚有 {len(undone)} 个非 done "
                        f"job（如 {undone[0].get('step')}），暂缓晋级待补齐"
                    )
                return None
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
                # v6.9.38: 审核退回/归零轮次后重开——已完成任务拉回 active。
                # 旧实现只处理 backlog→active，completed 任务（整轮完成时
                # 被标完成并移入 completed/ 目录）在课题被退回重跑同轮次时
                # 永远停在 completed，任务面板显示与实际 job 进度脱节
                # （08-22 实测 key-transient r1 job 6/25 但任务 completed）。
                # task_manager 状态机本就允许 completed→active 且自动搬移
                # 文件目录，此处只是补上缺失的调用分支。
                elif not round_complete and task.get("status") == "completed":
                    tm.transition_task(existing_task_id, "active")
                    if _log:
                        _log.info(
                            f"[task-sync] 课题轮次未完成但任务已标 completed，"
                            f"拉回 active: {existing_task_id}"
                        )
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
        # v6.10.27: 看板得分取章节 4 维均值（排除 references 2 维收尾分），
        # 与周报/优化报告同口径。旧逻辑读 last_score——每轮 references
        # 收尾时被 2 维分覆盖（如 attosecond r6 收尾 0.835 vs 章节均值
        # 0.80），看板数字与真实整篇质量脱节。当前轮次尚无章节分时回退
        # 最近完成轮次的章节均值，再兜底 last_score。
        _sec = _section_mean_score(prop_state, round_num) if prop_state else None
        if _sec is None and prop_state:
            _sec = _section_mean_score(prop_state, round_num - 1)
        score = _sec if _sec is not None else (
            prop_state.get("last_score", 0.0) if prop_state else 0.0
        )
        # v7.2.30: 4 维字典——看板 score 扩展为 {innovation, feasibility,
        # rigor, expression}（section_4d 口径） + 综合分（兼容旧值）
        # + high_issues 计数。直接从最新一条 section_4d history 读 dim_scores。
        # 这与评审团三维（rigor/completeness/expression）+ critic 4 维（innovation
        # /feasibility/rigor/expression）口径一致。0.78 平台带下数字与质量脱钩
        # 即可终结——直接看 4 维瓶颈。
        _score_dims = None
        _high_issues = 0
        _weakest_dim = None
        if prop_state:
            sh = prop_state.get("score_history", [])
            # 找最新 section_4d 非 partial 条目
            for h in reversed(sh):
                if h.get("caliber") == "section_4d" and not h.get("dims_partial"):
                    ds = h.get("dim_scores", {})
                    if ds:
                        _score_dims = ds
                        _high_issues = h.get("high_issues", 0)
                        _weakest_dim = h.get("weakest_dim")
                    break
        # v6.8.3-fix8: 只统计当前轮次的 job，避免跨轮累积导致看板数字膨胀
        round_jobs = [j for j in jobs if j.get("round") == round_num]
        failed = sum(1 for j in round_jobs if j.get("status") == JOB_STATUS_FAILED)
        pending = sum(1 for j in round_jobs if j.get("status") == JOB_STATUS_PENDING)
        done = sum(1 for j in round_jobs if j.get("status") == JOB_STATUS_DONE)
        total = len(round_jobs)
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
            "score_dims": _score_dims,  # v7.2.30: 4 维字典（可空）
            "weakest_dim": _weakest_dim,  # v7.2.30: 最弱维度
            "high_issues": _high_issues,  # v7.2.30: 未解决 high 问题数
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
        # v6.9.1: 合并写——先读入现有看板再覆盖自有键，保留其他写入方的数据
        # （lifecycle_monitor 的 alerts/hourly_monitor、sync_engine 的 kb_metrics）。
        # 原实现整文件替换，工作时段内每 15 分钟剥离一次告警与 KB 指标，
        # 导致告警面板数据闪断、趋势雷达/覆盖率持久化失效、心跳时间戳丢失。
        merged = load_json(KANBAN_PATH, default={})
        if isinstance(merged, dict) and merged:
            merged.update(kanban)
            kanban = merged
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

    # v6.10.14: 平台期课题转评审团——panel_review_requested 的课题不再
    # 参与自动轮转（末端空转止损，机时让给爬坡型课题），人工清除标志后恢复
    _before = len(optimizing)
    optimizing = [
        p for p in optimizing
        if not (p.get("panel_review_requested") if isinstance(p, dict) else False)
    ]
    if _before != len(optimizing) and _log:
        _log.info(
            f"[scheduler] { _before - len(optimizing)} 个平台期课题已转评审团，本轮跳过自动轮转"
        )
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

    # v7.1.8: 新进 optimizing 课题优先窗口——rounds=0 的课题获 3 时段
    # 强制优先聚焦，防止新进课题被高 round 课题持焦点饿死（看板
    # 实证 2026-09-27：quantum-geometry/ssh-weyl/mos2 三个 r=0 课题
    # 进入 optimizing 后 0 推进，pending jobs 一直挂 24h+ 不被调度）。
    # 窗口过期后按常规队列轮转。
    _NEW_PROPOSAL_PRIORITY_WINDOW = 3  # 3 个时段（每个时段跨多个 tick）
    _new_priority = []
    _regular = []
    for pid in queue:
        try:
            ps = self._get_proposal_state(pid)
            _rounds = ps.get("optimization_rounds", 0) if ps else 0
        except Exception:
            _rounds = 0
        # rounds=0 且 score_history 空 = 全新课题，未推进过任何轮次
        if _rounds == 0:
            _new_priority.append(pid)
        else:
            _regular.append(pid)
    # 新进课题优先插队到队列头部（最多 N 个），剩余按原顺序接续
    if _new_priority:
        _w = _new_priority[:_NEW_PROPOSAL_PRIORITY_WINDOW]
        _rest = _new_priority[_NEW_PROPOSAL_PRIORITY_WINDOW:] + _regular
        queue = _w + _rest
        if _log:
            _log.info(
                f"[scheduler] 新课题优先窗口：{len(_w)} 个 r=0 课题"
                f"({', '.join(_w[:3])}{'...' if len(_w) > 3 else ''})，"
                f"本轮优先聚焦"
            )

    # 当前时段与上一时段不同，可能需要切换 proposal
    if slot_index != last_slot_index:
        # v6.8.20: 清除上一时段的 slot_done 标记
        # v6.9.31 修复: 必须先读取再清除——旧实现先 pop 后在下方 L1028
        # 读同一个内存 dict，标记永远读不到，"轮次中途完成→下一时段轮转"
        # 信号形同虚设。聚焦课题每推进一轮即重置软卡死计数，可无限持有
        # 焦点，饿死队列其余课题（08-21 实证：bsv 停滞 87.7h、berry 46.9h，
        # order-param r6 于 slot 2 中途完成后 slot 3 仍持有焦点）。
        prev_done_key = f"slot_{last_slot_index}_done"
        prev_slot_done_flag = bool(state.get(prev_done_key))
        if prev_done_key in state:
            state.pop(prev_done_key, None)

        # 先自动重试上一个 proposal 的 failed job
        prev_pid = queue[last_proposal_index % len(queue)]
        try:
            retried = _auto_retry_failed_jobs(self, prev_pid)
            if retried > 0 and _log:
                _log.info(f"[{prev_pid}] 自动重试了 {retried} 个 failed job")
        except Exception:
            pass

        # 检查上一时段聚焦的 proposal 是否应让出时段
        try:
            prev_jobs = self._get_jobs(prev_pid)
            prev_state = self._get_proposal_state(prev_pid)
            completed_rounds = prev_state.get("optimization_rounds", 0) if prev_state else 0

            # v6.8.20: 优先检查 slot_done 标记——如果上一时段标记为已完成，
            # 说明轮次在中途就完成了，应该轮转到下一个课题
            # v6.9.31: 读 pop 前捕获的 flag（键已在本函数开头清除）
            if prev_slot_done_flag:
                round_done = True
            else:
                # v6.9.51: 每完成一轮强制切换——记录各课题上次被检查时的
                # completed_rounds，一旦发现轮次增加（上一时段完成了一轮），
                # 立即让出焦点，防止单课题无限持有焦点饿死队列其余课题
                # （08-25/26 实证：attosecond 连续 2 天持焦点，5 课题 stalled）。
                last_seen = state.setdefault("_last_round_seen", {})
                last_round = last_seen.get(prev_pid)
                if last_round is not None and completed_rounds > last_round:
                    round_done = True
                    if _log:
                        _log.info(
                            f"[{prev_pid}] 上一时段完成第 {completed_rounds} 轮，"
                            f"强制让出焦点（每完成一轮即切换）"
                        )
                else:
                    # 让出时段的条件：
                    # 进行中的轮次的全部任务已完成（产物+标签双检查通过）。
                    # 卡住（stuck）不由微调度器处理，交给 repair 和健康检查发现并修复，
                    # 修复后微调度器继续推进，保证每轮优化的连续性。
                    # v7.2.10: 改用 _is_core_round_complete——derived 类（update_vision /
                    # update_method_manual）不算核心，避免 N 个课题同时卡末尾 derived，
                    # 违反"完成一轮即让出"的循环队列契约。derived 由下一轮头部消化。
                    current_round = completed_rounds + 1
                    round_done = _is_core_round_complete(prev_jobs, prev_pid, current_round)
                # 更新快照：记录 prev_pid 当前轮次（无论是否让出）
                last_seen[prev_pid] = completed_rounds
                state["_last_round_seen"] = last_seen
                _save_focus_state(state)

            if not round_done:
                # 当前轮未完成：若 prev_pid 未卡死，继续聚焦（保证轮次连续性）；
                # 若 prev_pid 已卡死（关键 job failed 且修复系统已放弃），此处若
                # early return 会绕过下方第 988 行的 _is_proposal_stuck 兜底，导致
                # 死锁 proposal 永久占用焦点、饿死其余 proposal。故卡死时不返回，
                # 落入下方 move_to_queue_end 让出时段给下一个 proposal。
                if not _is_proposal_stuck(self, prev_pid):
                    # v6.8.10: 软卡死检测 — 连续 ≥MAX_SOFT_STUCK_SLOTS 个时段
                    # 轮次无推进（failed job 不阻塞 pending 但又不完成，灰色地带）。
                    # 此时不卡死不返回，强制让出给下一个 proposal，避免永久占用焦点。
                    # v6.9.39: 推进信号从"rounds 计数变化"细化为"rounds 变化 OR
                    # 当前轮 done 数增加"——一轮 25-30 job 需 2-4 个时段，旧信号
                    # 下超 2 个时段必误判让出（08-23 实证 26/29、12/25 被切）。
                    # tracked 记录格式 {pid: {"round": N, "done": M}}，兼容旧 int。
                    consecutive = _count_consecutive_slots(state, prev_pid)
                    if consecutive >= MAX_SOFT_STUCK_SLOTS:
                        tracked = state.setdefault("_round_when_focused", {})
                        prev_tracked = tracked.get(prev_pid, completed_rounds)
                        # 旧格式 int → 迁移为 dict（done 置 None 表示无基线）
                        if isinstance(prev_tracked, int):
                            prev_tracked = {"round": prev_tracked, "done": None}
                        cur_round = completed_rounds + 1
                        cur_done = _current_round_done_count(prev_jobs, cur_round)
                        rec_round = prev_tracked.get("round")
                        rec_done = prev_tracked.get("done")
                        # rec_done is None（旧 int 迁移的首个时段）：无 done 基线
                        # 无法判定，视为有推进以建立基线——最多少切一次，且
                        # 软卡死在后续时段（done 不变）仍会兜底让出。
                        has_progress = (
                            rec_round != completed_rounds
                            or rec_done is None
                            or cur_done > rec_done
                        )
                        if not has_progress:
                            # 连续 N 个时段 rounds 与 done 数均无变化 → 真软卡死
                            if _log:
                                _log.warning(
                                    f"[{prev_pid}] 连续 {consecutive} 个时段"
                                    f"轮次无推进（rounds={completed_rounds}，"
                                    f"done={cur_done} 不变），触发软卡死让出焦点"
                                )
                            # 清除跟踪记录，让出焦点
                            tracked.pop(prev_pid, None)
                            state["_round_when_focused"] = tracked
                            _save_focus_state(state)
                            # 不 return，落入下方 move_to_queue_end
                        else:
                            # 有进展（轮次推进或 job 级推进），更新基线继续聚焦
                            tracked[prev_pid] = {
                                "round": completed_rounds,
                                "done": cur_done,
                            }
                            state["_round_when_focused"] = tracked
                            _save_focus_state(state)
                            state["last_slot_index"] = slot_index
                            state["last_proposal_id"] = prev_pid
                            _save_focus_state(state)
                            return prev_pid
                    else:
                        # 连续聚集 < N 个时段，记录初始基线（round + done 快照）
                        tracked = state.setdefault("_round_when_focused", {})
                        if prev_pid not in tracked or isinstance(tracked.get(prev_pid), int):
                            tracked[prev_pid] = {
                                "round": completed_rounds,
                                "done": _current_round_done_count(
                                    prev_jobs, completed_rounds + 1),
                            }
                        state["_round_when_focused"] = tracked
                        _save_focus_state(state)
                        state["last_slot_index"] = slot_index
                        state["last_proposal_id"] = prev_pid
                        _save_focus_state(state)
                        return prev_pid
        except Exception as e:
            # v6.9.39: 异常不再静默落入让出路径——旧实现 except pass 后直接
            # 执行 _move_to_queue_end，任何 IO/解析异常都变成误切换课题。
            # 改为保守"继续聚焦当前课题"：软卡死（连续 N 时段无推进）与
            # _is_proposal_stuck 会在后续时段兜底，不会死锁焦点。
            if _log:
                _log.warning(
                    f"[micro-scheduler] 让出判定异常（保守继续聚焦 {prev_pid}）: {e}"
                )
            state["last_slot_index"] = slot_index
            state["last_proposal_id"] = prev_pid
            _save_focus_state(state)
            return prev_pid
        # 当前轮已完成：移动到队列末尾，推进到下一个
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
        # v6.9.90: 窗口内轮完成即切换（不间断调度适配）
        # v6.9.51 的"每完成一轮强制切换"原先只在 slot 边界分支执行；
        # v6.9.87 改为不间断长窗（工作日 00:00-13:00 同一 slot）后，该
        # 判定整个窗口不再触发——09-03 实证：qg 连续霸占焦点 9 小时
        # 连跑 r3-r6 三轮而零切换，其余 7 课题零执行。窗口内每次 tick
        # 都检查：轮次快照落后于实际 rounds（上一轮已完成）即让出。
        if pid:
            _ps = self._get_proposal_state(pid)
            _cur = _ps.get("optimization_rounds", 0) if _ps else 0
            _seen = state.get("_last_round_seen", {}).get(pid)
            if _seen is not None and _cur > _seen:
                if _log:
                    _log.info(
                        f"[{pid}] 窗口内完成第 {_cur} 轮，让出焦点"
                        f"（不间断调度：每完成一轮即切换）"
                    )
                # 让出时快照对齐（与 slot 边界分支 L1117 语义一致），
                # 防止下次切入时旧快照触发误切
                state.setdefault("_last_round_seen", {})[pid] = _cur
                _move_to_queue_end(state, pid)
                queue = state.get("queue", [])
                nxt = queue[0] if queue else None
                if nxt and nxt != pid:
                    for _i, _p in enumerate(queue):
                        if _p == nxt:
                            state["last_proposal_index"] = _i
                            break
                    state["last_proposal_id"] = nxt
                    _save_focus_state(state)
                    pid = nxt
        # v6.8.19: 确保 state 与当前聚焦课题同步
        # 注意：不更新 last_slot_index——它记录的是"上次切换时段时的 slot"，
        # 用于下次判断 slot_index != last_slot_index（时段是否切换）。
        # 如果在这里更新 last_slot_index，会导致时段切换检测失效。
        state["last_proposal_id"] = pid

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

    # v6.9.51: 聚焦课题轮次快照——首次聚焦时记录基线，
    # 供"每完成一轮强制切换"判定使用
    last_seen = state.setdefault("_last_round_seen", {})
    if pid not in last_seen:
        pid_state = self._get_proposal_state(pid)
        last_seen[pid] = pid_state.get("optimization_rounds", 0) if pid_state else 0
        state["_last_round_seen"] = last_seen
        _save_focus_state(state)

    # 记录历史
    # v6.9.31 加固: 同一 (slot, proposal) 只记一条——旧实现每 15 分钟 tick
    # 追加一条，50 条上限仅覆盖约一个时段，_count_consecutive_slots 在
    # 时段切换时几乎恒为 1，软卡死防线（MAX_SOFT_STUCK_SLOTS）对满时段
    # 失效。去重后 50 条可覆盖约 50 次时段切换，计数语义不变
    # （该函数只统计连续同课题的不同 slot_index 数）。
    history = state.get("focus_history", [])
    last_entry = history[-1] if history else None
    if (
        not last_entry
        or last_entry.get("slot_index") != slot_index
        or last_entry.get("proposal_id") != pid
    ):
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
    """返回 job 的优先级排序键（越小越优先）。

    v6.8.3-fix13: 优先级键加入 round 作为第一维度，
    确保当前轮次的 job（如 derived）总是优先于下一轮的 job（如 critic）。
    否则 _CHAIN_ORDER 中 critic=0 < update_vision=7，下一轮 critic 会抢占
    当前轮次 derived job 的执行时机，导致轮次永远无法完成。
    """
    jobs = self._get_jobs(proposal_id)
    job_index = {j["job_id"]: i for i, j in enumerate(jobs)}

    deps = job.get("depends_on", [])
    deps_just_done = all(
        any(d == j["job_id"] and j.get("status") == JOB_STATUS_DONE for j in jobs)
        for d in deps
    )

    round_num = job.get("round", 0)
    step = job.get("step", "")
    chain_order = _CHAIN_ORDER.get(step, 99)
    scheduled_at = job.get("scheduled_at") or job.get("started_at") or ""
    chain_next = 0 if deps_just_done else 1

    return (round_num, chain_next, chain_order, scheduled_at, job_index.get(job["job_id"], 9999))


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

    # 1. 获取 optimizing proposal 列表
    try:
        optimizing = self.list_by_status("optimizing")
    except Exception as e:
        if _log:
            _log.warning(f"[micro-scheduler] 获取 optimizing 列表失败: {e}")
        optimizing = []

    # 2. 全局 stale job 清理（无论是否在工作时段内都执行，防止 stuck job 跨时段滞留）
    # v6.8.3-fix9: 原来在时段检查之后，导致时段结束后 running job 无法被回收
    for p in optimizing:
        pid = p.get("proposal_id", "")
        if pid:
            try:
                self._refresh_stale_jobs(pid)
            except Exception as e:
                if _log:
                    _log.warning(f"[micro-scheduler] stale 清理 {pid} 失败: {e}")

    # 2.1 轮转名单自愈（v7.2.105 / BUG-34）——无条件执行，位于
    # 「optimizing 区为空」早退之前。轮转名单被测试夹具污染时，
    # optimizing 为空就永远不会走到 _sync_queue → 污染永久留存 →
    # 真实课题 queue_index 恒为 -1（monitor 误判真停滞）+
    # promote 人工提升被拒。此处按真实课题白名单剔除非法成员。
    # 并入当前 optimizing 名单：避免「课题已进轮转名单但 _lifecycle.json
    # 尚未同步」的时序窗口内被误杀（自愈会写回名单，误杀即永久饿死）。
    try:
        _repair_focus_queue(
            extra_ids=[p.get("proposal_id", "") for p in optimizing if p.get("proposal_id")]
        )
    except Exception as e:
        if _log:
            _log.warning(f"[micro-scheduler] 轮转名单自愈异常: {e}")

    # v7.1.8: r1 启动失败检测——新进 optimizing 课题 24h 内未完成首个
    # job 时告警（飞书/lifecycle_monitor 通路）。轻量、零 LLM，每个
    # tick 都跑但有 6h 去重窗口。
    try:
        r1_alerts = self._check_r1_start_failures()
        if r1_alerts and _log:
            _alert_ids = ", ".join(a["proposal_id"].split("-2026")[0][:30] for a in r1_alerts[:5])
            _log.warning(
                f"[micro-scheduler] r1 启动失败告警：{len(r1_alerts)} 个课题"
                f"超过 {R1_START_TIMEOUT_HOURS}h 0 推进——{_alert_ids}"
            )
    except Exception as e:
        if _log:
            _log.debug(f"[micro-scheduler] r1 启动失败检测异常: {e}")

    # 3. 时段检查（stale 清理已完成，非工作时段只跳过执行不跳过维护）
    slot_info = _current_focus_slot()
    if slot_info is None:
        msg = "当前不在工作时段内，跳过执行（stale 清理已完成）"
        if _log:
            _log.info(msg)
        # v6.9.21: 空档期也刷新看板 current（合并写，只改 current + 时间戳）。
        # 背景：08-14→08-17 gateway 挂死期间 current 冻结在 08-14 22:30 的
        # slot=18:30-22:30/in_slot=true，hourly-monitor 不覆盖该字段，
        # 恢复后空档期也不刷新，看板/控制台误读为"时段内"。
        try:
            merged = load_json(KANBAN_PATH, default={})
            if isinstance(merged, dict) and merged:
                cur = merged.get("current") or {}
                cur["in_slot"] = False
                cur["slot_index"] = None
                cur["slot"] = None
                merged["current"] = cur
                merged["updated_at"] = now_utc()
                merged["updated_at_local"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_json(KANBAN_PATH, merged)
        except Exception as e:
            if _log:
                _log.warning(f"空档期刷新看板 current 失败: {e}")
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg, "skip_reason": "out_of_slot"}

    slot_index, (slot_start, slot_end) = slot_info
    if _log:
        _log.info(f"当前时段: {slot_start}-{slot_end} (#{slot_index})")

    if not optimizing:
        msg = "optimizing 区为空"
        _update_kanban(slot_info, None, [], [], self)
        if _log:
            _log.info(msg)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg, "skip_reason": "no_optimizing"}

    # 4. 选择聚焦 proposal
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
    # v6.8.20: 本时段已完成轮次则标记，后续同一时段 cron 空转到时段结束
    focus_state = _load_focus_state()
    slot_done_key = f"slot_{slot_index}_done"
    if focus_state.get(slot_done_key):
        msg = f"{focus_pid} 本时段已完成轮次，空转到时段结束"
        if _log:
            _log.info(msg)
        _update_kanban(slot_info, focus_pid, optimizing, [], self)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg,
                "skip_reason": "slot_already_done"}

    prop_state = self._get_proposal_state(focus_pid)
    current_round = prop_state.get("optimization_rounds", 0) + 1 if prop_state else 1
    jobs = self._get_jobs(focus_pid)
    # v7.2.10: 改用 core round complete——核心 done 即递增 rounds，让
    # 课题让出焦点。derived 尾巴留给下轮头部消化，不再阻塞轮转。
    if _is_core_round_complete(jobs, focus_pid, current_round):
        msg = f"{focus_pid} 本轮核心已完成，时段空闲（derived 留待下轮头部消化）"
        if _log:
            _log.info(msg)
        # 递增 optimization_rounds（微调度器路径）
        if prop_state:
            prop_state["optimization_rounds"] = current_round
            self._set_proposal_state(focus_pid, prop_state)
        # v6.8.21: 归档已完成轮次的 job——只保留当前轮+上一轮（用于对比）
        from .utils import archive_old_round_jobs
        archive_old_round_jobs(focus_pid, current_round)
        # 生成优化报告
        report_path = _generate_round_report(self, focus_pid, current_round)
        if report_path:
            generated_reports.append(report_path)
        # v7.2.66: 首轮完成 → 大纲检查点入待人工队列（仅一次）
        if current_round == 1:
            try:
                _ps = self._get_proposal_state(focus_pid) or {}
                if not _ps.get("outline_checkpoint_sent"):
                    _ps["outline_checkpoint_sent"] = True
                    self._set_proposal_state(focus_pid, _ps)
            except Exception:
                pass
        # v6.8.33: 轮次已完成分支同样同步知识库（与 :1383 的 job 执行路径对齐，补 GAP）
        _sync_proposal_to_kb(focus_pid)
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
            # v7.2.17: 达标移除后立即指向队头，下一 tick 连续轮转
            # （原 slot_done 空转为 4 时段短窗设计，长窗下浪费整个时段）
            nxt = queue[0] if queue else None
            if nxt:
                for _i, _p in enumerate(queue):
                    if _p == nxt:
                        state["last_proposal_index"] = _i
                        break
                state["last_proposal_id"] = nxt
            _save_focus_state(state)
        else:
            # v7.2.17（用户裁决「1-2-3」修复 1）: 完成一轮即连续轮转——
            # 移队尾 + 指向队头，下一 tick 立即聚焦下一课题，不再空转
            # 到时段边界。详见 _continuous_rotate_after_round 文档。
            state = _load_focus_state()
            nxt = _continuous_rotate_after_round(state, focus_pid, current_round)
            if nxt and _log:
                _log.info(
                    f"[{focus_pid}] 本轮完成，连续轮转切换至 {nxt}"
                    f"（不再空转到时段边界）"
                )
            _save_focus_state(state)
        _update_kanban(slot_info, focus_pid, optimizing, [], self)
        return {"success": True, "executed_count": 0, "executed": [], "reason": msg,
                "skip_reason": "round_complete", "transitioned": transition_result is not None,
                "generated_reports": generated_reports}

    # 5. 只执行聚焦 proposal 的 pending job
    # v6.8.50: API 配额熔断检查——熔断 open 期间不派发（防 429 空转烧配额），
    # probing 只放行一个试探 job。详见 scripts/circuit_breaker.py
    try:
        from circuit_breaker import allow_dispatch as cb_allow_dispatch
        if not cb_allow_dispatch():
            msg = "API 熔断器 open/probing 中，本次跳过派发（冷却 1h 后自动试探恢复）"
            if _log:
                _log.warning(f"[micro-scheduler] {msg}")
            _update_kanban(slot_info, focus_pid, optimizing, [], self)
            return {"success": True, "executed_count": 0, "executed": [], "reason": msg,
                    "skip_reason": "circuit_open"}
    except ImportError:
        cb_allow_dispatch = None
    except Exception as e:
        # 熔断器自身故障不应阻塞调度（防御的防御）
        if _log:
            _log.warning(f"[micro-scheduler] 熔断器状态读取异常，按正常派发: {e}")
        cb_allow_dispatch = None

    # v7.2.66: 短步分级派发——实测 44% 的 job 运行 <60s（lit_note p50=1s、
    # gap_identify 15s、lit_search 46s）却独占整个 tick；v7.1.7 的 15 分钟
    # tick 下每轮 1.75h 机时摊成 6.5h 墙钟（占空比 27%，吞吐腰斩第一因）。
    # 现 cron 回 5 分钟 + 短步不占长步名额：长步（critic/writer 主链）每
    # tick 仍至多 max_jobs 个，短步在剩余时间窗内连续消化（防失控上限 5）。
    SHORT_SCHEDULER_STEPS = {"lit_note", "gap_identify", "lit_search", "update_vision"}
    long_done = 0
    jobs_done = 0
    _spin_guard = 0
    with file_lock("lifecycle-micro-scheduler"):
        while long_done < max_jobs and jobs_done < max_jobs + 5:
            if _spin_guard > 20:
                break
            _spin_guard += 1
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
                # v7.3.48: 写锁跳过不计入执行名额，也不改 job 状态
                if result.get("skipped") == "write_lock_held":
                    if _log:
                        _log.warning(
                            f"[micro-scheduler] 跳过 {proposal_id}/{refreshed.get('step')}: "
                            f"{result.get('error', '')}"
                        )
                    executed.append({
                        "proposal_id": proposal_id,
                        "job_id": refreshed["job_id"],
                        "step": refreshed.get("step"),
                        "success": False,
                        "skipped": "write_lock_held",
                        "error": result.get("error", "")[:200],
                    })
                    break
                # v7.2.66 分级计数：短步不占长步名额
                jobs_done += 1
                if (refreshed.get("step") or "") not in SHORT_SCHEDULER_STEPS:
                    long_done += 1

                # v6.8.50: 回报熔断器——连续 api_error 触发熔断后立即停止本轮派发
                # v6.9.66: 按 step 传 job_kind——长输出主链（critic/writer/
                # monitor 等）的"空输出+触顶超时"计入熔断（配额限流特征，
                # 429 文本检测对此失明），短输出 job 不计入也不清零长链计数。
                if cb_allow_dispatch is not None:
                    try:
                        from circuit_breaker import (
                            record_job_result as cb_record,
                            LONG_OUTPUT_STEPS,
                        )
                        _step = refreshed.get("step", "")
                        _kind = "long" if _step in LONG_OUTPUT_STEPS else "short"
                        # v6.9.76: 传 step——critic/monitor（zai 主模型步骤）
                        # 的长超时分桶计数，异供应商 writer 成功不清零
                        cb_st = cb_record(result.get("success", False),
                                          result.get("error", ""),
                                          job_kind=_kind,
                                          step=_step)
                        # v6.9.68: 模型逃生状态可视——主模型静默挂起时调度
                        # 不停、hermes 调用强制备用模型；escape->open
                        # （主备全挂）时同样停止本轮派发
                        if cb_st.get("escape_active") and _log:
                            _log.warning(
                                f"[micro-scheduler] 模型逃生激活中：hermes 调用"
                                f"强制备用模型，调度照常（job "
                                f"{refreshed.get('step')} success={result.get('success')}）"
                            )
                        if cb_st.get("state") == "open" and not result.get("success"):
                            if _log:
                                _log.warning(
                                    f"[micro-scheduler] API 熔断已开启"
                                    f"（api_error 连续 {cb_st.get('consecutive_api_errors')}"
                                    f"/长输出超时连续 {cb_st.get('consecutive_long_timeouts')}），本轮停止派发"
                                )
                            executed.append({
                                "proposal_id": proposal_id,
                                "job_id": refreshed["job_id"],
                                "step": refreshed.get("step"),
                                "success": result.get("success"),
                                "error": result.get("error", "")[:200],
                            })
                            break
                    except Exception as e:
                        if _log:
                            _log.warning(f"[micro-scheduler] 熔断器回报异常（忽略）: {e}")

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
                    # 注：此处保留 _is_round_complete（全量完成）而非 _is_core_round_complete，
                    # 因为后面紧跟 _check_and_transition（v6.9.60 晋级完整性门）——晋级
                    # pending_review 必须保证所有 job（含 derived）已消化。v7.2.10
                    # core round 改法只放宽轮转让出门槛，不影响晋级完整性。
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
                        # v6.8.5: 轮次完成后自动同步到知识库，无需等周末
                        _sync_proposal_to_kb(proposal_id)
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
                        # v6.8.3-fix12: 轮次完成后必须 break，否则循环继续会触发
                        # sync_checkpoint 创建下一轮 job，导致同一时段内启动新一轮，
                        # 违反设计原则：时段内聚焦课题完成一轮后应让出焦点给下一个课题。
                        if _log:
                            _log.info(
                                f"[{proposal_id}] 第 {post_round} 轮完成，"
                                f"让出当前时段剩余时间"
                            )
                        break

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
    """创建或更新全局微调度器 cron（每 15 分钟一次）。"""
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
