#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轮转队列双键的跨模块单一真相源（v7.2.71）。

**为什么是独立模块**：`lifecycle/` 是一个包，导入任意子模块（如
`lifecycle.utils`）都会先执行 `lifecycle/__init__.py`，而后者 `from
.controller import ...` 会连带拉起 `proposal_lifecycle` 全链。人工干预
工具（如 `promote_proposal_to_focus.py`）只需要「读/写轮转名单」这一
件事，不该为此付出全链导入代价，也不该在模块内各自实现双键逻辑
（v7.2.66 双键化后各模块各读各的，正是 BUG-28 的根因）。

**双键语义**（v7.2.66 起 `micro_scheduler._sync_queue` 双键维护）：

- `queue_full` = 完整候补名单（全部 optimizing 课题）
- `queue`      = 前 `MAX_ROTATION_WIP` 个（WIP 硬窗口），其余候补等待
  「成员晋级/归档/冻结后窗口自动下移」的 pull-based 推进

**跨模块消费者必须经 `get_rotation_queue()` / `set_rotation_queue()`**，
不要直接读写 `queue` 键——只读 `queue` 会漏掉窗口外候补（被当成
「不在队列中」），只写 `queue` 会被下一个 tick 的 `_sync_queue`
以 `queue_full` 为准的重建静默还原。

用法：
    from rotation_queue import get_rotation_queue, set_rotation_queue
    order = get_rotation_queue(state)          # 完整名单
    set_rotation_queue(state, [pid] + rest)    # 双键同步改写
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple

# 轮转 WIP 硬窗口（v7.2.66 定案 4）。v7.2.71 从 micro_scheduler 上移至此，
# 使跨模块消费者（monitor / promote）可引用同一常量。
MAX_ROTATION_WIP = 3

# 轮转队列双键名
ROTATION_QUEUE_KEY = "queue"
ROTATION_QUEUE_FULL_KEY = "queue_full"

# v7.2.105（BUG-34）：轮转名单成员合法性校验——真实 proposal_id 形态。
#
# 根因：历史版本 `scripts/tests/test_stall_classify.py` 的夹具直接写真实
# `memory/lifecycle-focus.json`（写入 `filler-0` / `test-queue-parser` 等
# 占位 id），且异常路径下 `_restore_queue()` 未还原 → 生产轮转名单被
# 测试夹具整体顶替。污染后果：
#   1. `_sync_queue` 的「移除已不在 optimizing 中的 proposal」按 id 精确
#      比对，夹具 id 永远匹配不上 → 污染项永远留存；
#   2. 所有真实 optimizing 课题的 `queue_index` 变成 -1 →
#      `lifecycle_monitor._classify_stall_kind` 判为 blocked（真停滞）→
#      误发 stalled 告警（实测 3 个在监课题全被判 blocked）；
#   3. `promote_proposal_to_focus.py apply`（人工干预唯一入口）报
#      「✗ proposal 不在轮转名单中」→ 人工无法干预轮转。
#
# 修复分两层：
#   ① 本模块提供 `is_valid_proposal_id()` + `sanitize_rotation_queue()`，
#      供写入方（_sync_queue / promote）在落盘前剔除非法成员；
#   ② `lifecycle_monitor` 与 `promote` 读取时按同一口径过滤，fail-open
#      （判定依据不足时不误杀真实课题）。
#
# 真实 proposal_id 形态：`<project_type>-<slug>-<YYYYMMDD>`，其中
# project_type 取自 `proposal_lifecycle.constants.PROJECT_TYPES`
# （general / key_transient / ...）。占位 id 形态为 `filler-N` /
# `test-xxx` / `general-test-xxx-20260101` 等，均因不含合法日期后缀
# 或项目类型前缀不匹配而被剔除。
_PROPOSAL_ID_DATE_RE = re.compile(r"-\d{8}$")


def is_valid_proposal_id(pid: str, known_ids: Optional[Set[str]] = None) -> bool:
    """判定一个 id 是否可作为轮转名单成员。

    两级判定（**白名单优先且权威**）：
      1. **白名单**：`known_ids` 非空时以其为准——只有真实课题 id 才合法。
         这是生产口径的权威依据（轮转名单成员必然来自 `_lifecycle.json`
         的 proposals 集合）。
      2. **形态**：白名单不可用（读不到 / 为空）时退化为形态判定——
         `<project_type>-<slug>-<YYYYMMDD>`（含 `-` 前缀 + 8 位日期后缀）。
         形态判定是 fail-open 的降级路径，宁可放过形态可疑项也不误杀
         真实课题。

    为什么白名单要权威而非「白名单 OR 形态」：生产污染若混入**形态合法**
    的假 id（如 `general-test-alpha-20260101`），宽松的 OR 判定会把它
    留在名单里，虚增 queue_total 并稀释队尾判定。真实课题永不误杀的
    保证来自白名单本身（真实课题必然在 `_lifecycle.json` 中），而非形态。
    """
    if not pid or not isinstance(pid, str):
        return False
    if known_ids:
        return pid in known_ids
    # 白名单不可用 → 形态判定（fail-open 降级）
    if not _PROPOSAL_ID_DATE_RE.search(pid):
        return False
    prefix = pid.rsplit("-", 1)[0]
    return "-" in prefix


def sanitize_rotation_queue(
    order: List[str],
    known_ids: Optional[Set[str]] = None,
) -> Tuple[List[str], List[str]]:
    """过滤轮转名单中的非法成员。

    返回 `(合法成员列表, 被剔除的成员列表)`。顺序保持不变。
    """
    kept: List[str] = []
    dropped: List[str] = []
    for pid in order or []:
        if is_valid_proposal_id(pid, known_ids):
            kept.append(pid)
        else:
            dropped.append(pid)
    return kept, dropped


def get_rotation_queue(state: Dict[str, Any]) -> List[str]:
    """取轮转**完整**候补名单。

    优先读 `queue_full`（完整名单）；无该键时回退旧 `queue` 键
    （兼容 v7.2.66 之前的数据形态）。
    """
    full = state.get(ROTATION_QUEUE_FULL_KEY) or []
    if full:
        return list(full)
    return list(state.get(ROTATION_QUEUE_KEY) or [])


def set_rotation_queue(state: Dict[str, Any], order: List[str]) -> None:
    """按给定顺序重写轮转双键（`queue_full` 全量 + `queue` WIP 窗口）。

    人工提升（promote）等需要改写轮转顺序的调用方必须经此函数，
    否则只改一个键会被下一个 tick 的 `_sync_queue` 还原。
    """
    state[ROTATION_QUEUE_FULL_KEY] = list(order)
    state[ROTATION_QUEUE_KEY] = list(order[:MAX_ROTATION_WIP])


def _self_check() -> None:
    """自检：双键读写一致性 + 非法成员过滤（v7.2.105）。"""
    state = {"queue": ["a", "b"], "queue_full": ["a", "b", "c", "d"]}
    assert get_rotation_queue(state) == ["a", "b", "c", "d"], "应读完整名单"
    assert len(state["queue"]) == 2, "读不应改写"

    set_rotation_queue(state, ["c", "a", "b", "d"])
    assert state["queue_full"] == ["c", "a", "b", "d"], "queue_full 应为全量新序"
    assert state["queue"] == ["c", "a", "b"], "queue 应为窗口前 N 个"

    legacy = {"queue": ["x", "y"]}
    assert get_rotation_queue(legacy) == ["x", "y"], "无 queue_full 时回退旧键"

    # v7.2.105：非法成员过滤
    real = "general-bsv-driven-hhg-quantum-20260726"
    polluted = ["filler-0", "filler-1", "test-queue-parser", real]
    kept, dropped = sanitize_rotation_queue(polluted)
    assert kept == [real], f"应只保留真实课题: {kept}"
    assert dropped == ["filler-0", "filler-1", "test-queue-parser"], f"应剔除 3 个占位: {dropped}"
    # 白名单优先：不在 opt_ids 但在 known_ids 里 → 合法
    kept2, _ = sanitize_rotation_queue(["zzz"], {real})
    assert kept2 == [], "known_ids 不含 zzz 时应剔除"
    kept3, _ = sanitize_rotation_queue([real], set())
    assert kept3 == [real], "形态合法的真实课题不应被剔除"

    print("✓ rotation_queue 自检通过")


if __name__ == "__main__":
    _self_check()
