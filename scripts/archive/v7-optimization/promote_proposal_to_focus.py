#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v7.2.5: promote_proposal_to_focus

聚焦工具：把指定 proposal 提到 lifecycle-focus queue 的头部，
让下一次 micro_scheduler tick 立即优先处理它。

实战回归：berry-mnps3-rashba r6-rationale-writer 9-25 失败后 queue 第 9 位
（10 个里倒数第二），r6 后续 20 个 pending job 累计 4+ 天未触发。
监控只能告警 stalled，无法干预轮转。

用法：
  python3 scripts/promote_proposal_to_focus.py dry-run
  python3 scripts/promote_proposal_to_focus.py apply --proposal <id>
  python3 scripts/promote_proposal_to_focus.py apply --proposal <id> --reason '优先处理 R6 待补'

v7.2.71 修复（BUG-28）：v7.2.66 引入轮转 WIP 硬窗口后，`_sync_queue` 双键
维护轮转名单（`queue_full` = 完整候补名单 / `queue` = 前 3 个），而本脚本
只读只写 `queue`：

- 场景 A：WIP 窗口外的候补课题（monitor 的 queue_tail_warn 处置建议正是
  指向它们）根本不在 `queue` 里 → 提升被拒，人工无法干预轮转。
- 场景 B：窗口内课题提升后只改了 `queue`，下一个 tick 的 `_sync_queue`
  以 `queue_full` 为准重建 `queue` → 人工提升被静默还原。

修复：经 `lifecycle.utils.get_rotation_queue` / `set_rotation_queue` 统一
读写双键，并同步校准 `last_proposal_id`（聚焦选择的真实依据）。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FOCUS_PATH = PROJECT_ROOT / "memory" / "lifecycle-focus.json"


def _short(pid: str) -> str:
    """课题 id 缩写（去掉通用前缀与日期后缀）。"""
    for token in ("general-", "-20260726", "-20260727", "-20260816",
                  "-20260822", "-20260905", "-20260920", "-20261004"):
        pid = pid.replace(token, "")
    return pid


def _known_proposal_ids():
    """读真实课题 id 集合（轮转名单白名单），读不到返回 None。"""
    try:
        from common import load_json
        path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
        data = load_json(path, default={})
        props = data.get("proposals") or {}
        if not props:
            return None
        return set(props.keys())
    except Exception:
        return None


def cmd_dry_run() -> int:
    if not FOCUS_PATH.exists():
        print(f"✗ lifecycle-focus.json 不存在: {FOCUS_PATH}")
        return 1
    state = json.loads(FOCUS_PATH.read_text(encoding="utf-8"))
    # v7.2.71: 显示完整候补名单（queue_full），并标出 WIP 窗口成员
    # v7.2.105（BUG-34）：过滤非法成员后展示，避免污染态下人工看到
    # 一整屏测试占位 id 而误以为生产数据已损坏。
    from rotation_queue import MAX_ROTATION_WIP, get_rotation_queue, sanitize_rotation_queue

    queue = get_rotation_queue(state)
    queue, dropped = sanitize_rotation_queue(queue, _known_proposal_ids())
    if dropped:
        print(f"⚠ 轮转名单含 {len(dropped)} 个非法成员（疑似测试夹具污染），已剔除: {dropped[:5]}")
    window = set(state.get("queue") or []) & set(queue)
    last_pid = state.get("last_proposal_id", "")
    print(f"=== 当前轮转名单（{len(queue)} 个，WIP 窗口 {MAX_ROTATION_WIP}）===")
    for i, pid in enumerate(queue):
        marker = "← last" if pid == last_pid else ""
        wip = "[窗口]" if pid in window else "[候补]"
        print(f"  [{i:2d}] {wip} {_short(pid)} {marker}")
    return 0


def cmd_promote(proposal_id: str, reason: str) -> int:
    if not FOCUS_PATH.exists():
        print(f"✗ lifecycle-focus.json 不存在: {FOCUS_PATH}")
        return 1
    state = json.loads(FOCUS_PATH.read_text(encoding="utf-8"))
    # v7.2.71: 读完整候补名单（含 WIP 窗口外候补），不再只读 `queue`
    # v7.2.105（BUG-34）：剔除名单中的非法成员（测试夹具占位 id 等）——
    # 污染期间名单整体被占位 id 顶替 → 真实课题「不在轮转名单中」→
    # 人工干预唯一入口被彻底堵死。过滤后同时把污染项从落盘名单中
    # 移除（写回前修复，等价于 _sync_queue 的自愈）。
    from rotation_queue import get_rotation_queue, sanitize_rotation_queue, set_rotation_queue

    queue = get_rotation_queue(state)
    queue, dropped = sanitize_rotation_queue(queue, _known_proposal_ids())
    if dropped:
        print(f"⚠ 轮转名单含 {len(dropped)} 个非法成员（疑似测试夹具污染），已剔除: {dropped[:5]}")
    if proposal_id not in queue:
        print(f"✗ proposal 不在轮转名单中: {proposal_id}")
        print(f"   当前名单: {[_short(p) for p in queue]}")
        return 1

    # 移动到队首（完整名单与 WIP 窗口同步改写）
    new_order = [proposal_id] + [q for q in queue if q != proposal_id]
    set_rotation_queue(state, new_order)

    # v7.2.71: 聚焦选择的真实依据是 last_proposal_id（下一个 tick 走
    # `_rebalance_index` → 按 last_proposal_id 在队列中定位），
    # 只改 last_proposal_index 不足以让下一个 tick 聚焦被提升的课题。
    state["last_proposal_id"] = proposal_id
    state["last_proposal_index"] = 0

    # 记录 promote 审计
    from common import now_utc  # noqa
    state["promote_history"] = state.get("promote_history", [])
    state["promote_history"].append({
        "proposal_id": proposal_id,
        "reason": reason[:200],
        "at": now_utc(),
        "by": "v7.2.5 promote_proposal_to_focus",
    })
    state["promote_history"] = state["promote_history"][-20:]  # 保留最近 20 条

    # 写回
    from common import save_json  # noqa
    save_json(FOCUS_PATH, state)
    short = _short(proposal_id)
    print(f"✓ {short} 已提升到队首")
    print(f"  新轮转顺序：")
    for i, pid in enumerate(new_order[:5]):
        marker = "← 目标" if pid == proposal_id else ""
        print(f"    [{i:2d}] {_short(pid)} {marker}")
    print(f"\n下次 micro-scheduler tick 会聚焦 {short}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="v7.2.5: 把 proposal 提到 queue 头部优先聚焦")
    sub = parser.add_subparsers(dest="cmd")

    p_dry = sub.add_parser("dry-run", help="只查看当前 queue 顺序")
    p_dry.set_defaults(func=lambda a: cmd_dry_run())

    p_apply = sub.add_parser("apply", help="把 proposal 提升到 queue[0]")
    p_apply.add_argument("--proposal", required=True, help="proposal_id")
    p_apply.add_argument("--reason", default="manual_promote", help="提升原因")
    p_apply.set_defaults(func=lambda a: cmd_promote(a.proposal, a.reason))

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())