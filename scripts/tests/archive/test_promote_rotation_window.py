#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_promote_rotation_window.py — 人工提升工具的轮转双键一致性回归（v7.2.71）

覆盖缺陷 BUG-28：v7.2.66 引入轮转 WIP 硬窗口后，`_sync_queue` 双键维护
轮转名单：

    queue_full = 完整候补名单（全部 optimizing 课题）
    queue      = 前 MAX_ROTATION_WIP 个（WIP 硬窗口）

而 `promote_proposal_to_focus.py`（monitor 告警文案的**处置建议**指向它）
仍只读只写 `queue`：

- **场景 A**：WIP 窗口外的候补课题（`queue_tail_warn` 告警正是指向它们）
  根本不在 `queue` 里 → 提升被拒（"proposal 不在 queue 中"），
  人工**无法干预轮转**。
- **场景 B**：窗口内课题提升后只改了 `queue`，下一个 tick 的 `_sync_queue`
  以 `queue_full` 为准重建 `queue` → **人工提升被静默还原**。

v7.2.70 修了 monitor 侧（改读 `queue_full`），但 promote 侧未修 →
告警文案指向的处置手段本身是失效的。

本套件以 TestSuite 风格编写（纳入 `self_test --module` 全量回归），覆盖：
    1. `rotation_queue` helper 双键读写一致性（单一真相源）
    2. 场景 A：WIP 窗口外候补课题可被提升（不再被拒）
    3. 场景 B：提升后经 `_sync_queue` 重建不被还原（下一个 tick 保持）
    4. 提升后 `last_proposal_id` 指向被提升课题（聚焦选择的真实依据）
    5. 兼容回退：无 `queue_full` 键时回退旧 `queue` 键
    6. 真实链路：提升 → `_focus_proposal_for_slot` 实际聚焦被提升课题
"""

import importlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test_runner import TestSuite

PID_A = "general-alpha-20260101"
PID_B = "general-beta-20260101"
PID_C = "general-gamma-20260101"
PID_D = "general-delta-20260101"

# v7.2.105（BUG-34）：promote 与 monitor 读轮转名单时按「真实课题白名单」
# 过滤非法成员，白名单来源是 `_lifecycle.json` 的 proposals 集合。本套件
# 的夹具 id 不是真实课题 → 必须登记进隔离环境的 `_lifecycle.json`，
# 否则 promote 会把它们全部剔除 → 「proposal 不在轮转名单中」→
# 提升被拒，断言全部失真。登记后过滤对本套件是恒等变换，断言意图
# （窗口外候补可提升 / 双键同步 / 旧形态回退）完整保留。
FIXTURE_IDS = [PID_A, PID_B, PID_C, PID_D]


class PromoteRotationWindowTests(TestSuite):
    def __init__(self):
        super().__init__("人工提升工具的轮转双键一致性测试（v7.2.71 BUG-28）")
        self.tmp_root = None
        self.rq = None
        self.ms = None
        self.promote_mod = None
        self._focus_path = None

    # ── 夹具 ──────────────────────────────────────────────

    def setup(self):
        self.tmp_root = Path(tempfile.mkdtemp(prefix="linsai_promote_window_"))
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / sub).mkdir(parents=True, exist_ok=True)
        mem = self.tmp_root / "memory"
        mem.mkdir(parents=True, exist_ok=True)
        self._focus_path = mem / "lifecycle-focus.json"

        # 登记夹具 id 为「已知课题」（隔离环境，真实数据零接触）——
        # v7.2.105 白名单过滤需要，否则夹具 id 被判非法成员全部剔除。
        (self.tmp_root / "research_proposals" / "_lifecycle.json").write_text(
            json.dumps({
                "proposals": {pid: {"status": "optimizing"} for pid in FIXTURE_IDS},
                "updated_at": "2026-11-02T00:00:00Z",
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # rotation_queue 是零依赖独立模块，可直接导入
        for mod_name in ("rotation_queue",):
            sys.modules.pop(mod_name, None)
        self.rq = importlib.import_module("rotation_queue")

        # micro_scheduler 需隔离（指向 tmp_root）
        for mod_name in list(sys.modules.keys()):
            if "micro_scheduler" in mod_name or mod_name in ("lifecycle", "paths", "common"):
                del sys.modules[mod_name]
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        self.ms = importlib.import_module("lifecycle.micro_scheduler")
        self.ms.FOCUS_STATE_PATH = self._focus_path
        import paths
        paths.PROJECT_ROOT = self.tmp_root

        # promote 模块（含 CLI 入口函数）
        sys.modules.pop("promote_proposal_to_focus", None)
        self.promote_mod = importlib.import_module("promote_proposal_to_focus")
        self.promote_mod.FOCUS_PATH = self._focus_path
        # v7.2.105：promote 模块自带 PROJECT_ROOT 常量（模块级绑定），
        # `paths.PROJECT_ROOT = tmp_root` 改不到它 → 白名单仍会读真实
        # `_lifecycle.json` → 隔离夹具 id 全被剔除。显式改绑本模块。
        self.promote_mod.PROJECT_ROOT = self.tmp_root

    def teardown(self):
        for mod_name in ("promote_proposal_to_focus", "rotation_queue"):
            sys.modules.pop(mod_name, None)
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_focus(self, state: dict):
        self._focus_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_focus(self) -> dict:
        return json.loads(self._focus_path.read_text(encoding="utf-8"))

    def _state(self, full=None, window=None, last_pid=None):
        """构造 v7.2.66 生产形态的 focus 状态（双键）。"""
        full = full if full is not None else [PID_A, PID_B, PID_C, PID_D]
        window = window if window is not None else full[: self.rq.MAX_ROTATION_WIP]
        return {
            "queue": list(window),
            "queue_full": list(full),
            "last_proposal_id": last_pid or full[0],
            "last_proposal_index": 0,
            "last_slot_index": 0,
            "last_day_key": "2026-10-31",
            "focus_history": [],
        }

    # ── 用例 ──────────────────────────────────────────────

    def run_tests(self):
        # 1. helper：双键读写一致性（单一真相源）
        st = {"queue": ["a", "b"], "queue_full": ["a", "b", "c", "d"]}
        self.assert_eq(
            self.rq.get_rotation_queue(st), ["a", "b", "c", "d"],
            "get_rotation_queue 应返回完整候补名单",
            "只读 queue 会漏掉 WIP 窗口外候补（BUG-28 场景 A 根因）",
        )
        self.assert_eq(
            len(st["queue"]), 2,
            "读不应改写状态",
            "get_rotation_queue 必须是只读操作",
        )
        self.rq.set_rotation_queue(st, ["c", "a", "b", "d"])
        self.assert_eq(
            st["queue_full"], ["c", "a", "b", "d"],
            "set_rotation_queue 应写 queue_full 全量新序",
            "只写 queue 会被下一个 tick 的 _sync_queue 还原（BUG-28 场景 B 根因）",
        )
        self.assert_eq(
            st["queue"], ["c", "a", "b"],
            "set_rotation_queue 应同步写 WIP 窗口 queue",
            f"窗口应取前 MAX_ROTATION_WIP={self.rq.MAX_ROTATION_WIP} 个",
        )

        # 2. 场景 A：WIP 窗口外候补课题可被提升（不再被拒）
        #    PID_D 在 queue_full[3]，不在 queue（窗口 = 前 3 个）
        self._write_focus(self._state())
        rc = self.promote_mod.cmd_promote(PID_D, "hc-test-window-candidate")
        st = self._read_focus()
        self.assert_eq(
            rc, 0,
            "WIP 窗口外候补课题应可被提升",
            "monitor 的 queue_tail_warn 处置建议正是指向这类课题，"
            "拒绝提升等于告警文案指向的处置手段失效",
        )
        self.assert_eq(
            st["queue_full"][0], PID_D,
            "提升后 queue_full 队首应为被提升课题",
            "只改 queue 不改 queue_full 会被下一个 tick 还原",
        )
        self.assert_eq(
            st["queue"][0], PID_D,
            "提升后 WIP 窗口队首应为被提升课题",
            "窗口未同步改写则被提升课题仍不在窗口内",
        )

        # 3. 场景 B：提升后经 _sync_queue 重建不被还原（下一个 tick 保持）
        self._write_focus(self._state())
        self.promote_mod.cmd_promote(PID_D, "hc-test-survive-tick")
        st = self._read_focus()
        # 模拟下一个 tick：_sync_queue 以 queue_full 为准重建 queue
        state = dict(st)
        optimizing = [{"proposal_id": p} for p in state["queue_full"]]
        self.ms._sync_queue(state, optimizing)
        self.assert_eq(
            state["queue"][0], PID_D,
            "提升后经 _sync_queue 重建仍应保持队首",
            "被还原即说明人工提升被静默丢弃（BUG-28 场景 B）",
        )
        self.assert_eq(
            state["queue_full"][0], PID_D,
            "重建后 queue_full 队首仍应为被提升课题",
            "queue_full 不应被重建改变",
        )

        # 4. 提升后 last_proposal_id 指向被提升课题（聚焦选择的真实依据）
        self._write_focus(self._state())
        self.promote_mod.cmd_promote(PID_C, "hc-test-last-id")
        st = self._read_focus()
        self.assert_eq(
            st.get("last_proposal_id"), PID_C,
            "提升后 last_proposal_id 应指向被提升课题",
            "下一 tick 的 _rebalance_index 按 last_proposal_id 定位，"
            "不改则聚焦仍在旧课题上",
        )

        # 5. 兼容回退：无 queue_full 键时回退旧 queue 键
        legacy = {
            "queue": [PID_A, PID_B],
            "last_proposal_id": PID_A,
            "last_proposal_index": 0,
            "last_slot_index": 0,
            "focus_history": [],
        }
        self._write_focus(legacy)
        rc = self.promote_mod.cmd_promote(PID_B, "hc-test-legacy")
        st = self._read_focus()
        self.assert_eq(
            rc, 0,
            "无 queue_full 键的旧数据形态仍可提升",
            "v7.2.66 之前的数据必须兼容",
        )
        self.assert_eq(
            st["queue_full"][0], PID_B,
            "旧形态提升后应补写 queue_full",
            "补写后双键一致，避免下一 tick 再次还原",
        )

        # 6. 真实链路：提升 → _focus_proposal_for_slot 实际聚焦被提升课题
        self._write_focus(self._state())
        self.promote_mod.cmd_promote(PID_D, "hc-test-focus-chain")
        ctrl = MagicMock()
        ctrl._get_proposal_state.side_effect = lambda pid: {"optimization_rounds": 1}
        ctrl._get_jobs.side_effect = lambda pid: []
        optimizing = [{"proposal_id": p} for p in [PID_A, PID_B, PID_C, PID_D]]
        focus = self.ms._focus_proposal_for_slot(ctrl, slot_index=1, optimizing=optimizing)
        self.assert_eq(
            focus, PID_D,
            "提升后下一个 tick 应实际聚焦被提升课题",
            "提升只改队列不改 last_proposal_id 时，聚焦仍在旧课题上"
            "（人工干预轮转的实际目标未达成）",
        )


if __name__ == "__main__":
    sys.exit(0)
