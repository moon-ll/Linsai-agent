#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_rotation_queue_pollution.py — 轮转名单污染防护回归（v7.2.105 BUG-34）

覆盖缺陷 BUG-34：历史版本 `scripts/tests/test_stall_classify.py` 的夹具直接
写真实 `memory/lifecycle-focus.json`（写入 `filler-0` / `test-queue-parser`
等占位 id），且异常路径下 `_restore_queue()` 未还原 → 生产轮转名单被测试
夹具整体顶替。

污染在生产上的三处实际危害（2026-11-02 04h 轮实测）：

  1. **monitor 误判真停滞**：真实课题的 `queue_index` 恒为 -1 →
     `_classify_stall_kind` 分支 5 判 `blocked`（上游调度未接管）→
     误发 stalled 真停滞告警。实测 3 个在监课题全被判 blocked。
  2. **人工干预入口堵死**：`promote_proposal_to_focus.py apply` 报
     「✗ proposal 不在轮转名单中」→ 人工无法干预轮转（实测复现）。
  3. **污染永不消退**：`_sync_queue` 的清理只在
     `_focus_proposal_for_slot` / `_rebalance_index` 路径上，而这两处都在
     `run_micro_scheduler` 的「optimizing 区为空」早退**之后** → 全部课题
     推进到 pending_review 后污染永久留存。

本套件以 TestSuite 风格编写（纳入 `self_test --module` 全量回归），覆盖：

    1. `sanitize_rotation_queue` 剔除测试夹具占位 id、保留真实课题
    2. 白名单权威性：形态合法的假 id 同样被剔除
    3. fail-open 降级：白名单不可用时按形态判定，不误杀真实课题
    4. `micro_scheduler._repair_focus_queue` 无条件自愈（不依赖 optimizing）
    5. monitor 读路径按同一口径过滤（污染态下不再误判 blocked）
    6. promote 读路径按同一口径过滤（污染态下不再拒真实课题）
    7. `_sync_queue` 写入路径剔除污染项
"""

import importlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test_runner import TestSuite, patch_module_root

PID_A = "general-alpha-20260101"
PID_B = "general-beta-20260101"
PID_C = "general-gamma-20260101"

# 真实污染样本（2026-11-02 04h 实测生产值）
POLLUTED = [
    "filler-0", "filler-1", "filler-2", "test-queue-parser",
    "filler-4", "filler-5", "filler-6", "filler-7",
]


class RotationQueuePollutionTests(TestSuite):
    def __init__(self):
        super().__init__("轮转名单污染防护测试（v7.2.105 BUG-34）")
        self.tmp_root = None
        self.rq = None
        self.ms = None
        self.promote_mod = None
        self.lm = None
        self._focus_path = None
        self._lc_path = None

    # ── 夹具 ──────────────────────────────────────────────

    def setup(self):
        self.tmp_root = Path(tempfile.mkdtemp(prefix="linsai_rot_pollution_"))
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / sub).mkdir(parents=True, exist_ok=True)
        mem = self.tmp_root / "memory"
        mem.mkdir(parents=True, exist_ok=True)
        self._focus_path = mem / "lifecycle-focus.json"
        self._lc_path = self.tmp_root / "research_proposals" / "_lifecycle.json"

        # 真实课题登记（白名单来源）
        self._lc_path.write_text(json.dumps({
            "proposals": {
                PID_A: {"status": "optimizing"},
                PID_B: {"status": "optimizing"},
                PID_C: {"status": "pending_review"},
            },
            "updated_at": "2026-11-02T00:00:00Z",
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        for mod_name in ("rotation_queue",):
            sys.modules.pop(mod_name, None)
        self.rq = importlib.import_module("rotation_queue")

        for mod_name in list(sys.modules.keys()):
            if "micro_scheduler" in mod_name or mod_name in ("lifecycle", "paths", "common"):
                del sys.modules[mod_name]
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        self.ms = importlib.import_module("lifecycle.micro_scheduler")
        # patch_module_root 同时改写模块级 PROJECT_ROOT 与派生路径常量
        # （micro_scheduler 的 FOCUS_STATE_PATH 是模块级绝对常量，
        #  仅 patch paths.PROJECT_ROOT 不生效——_known_proposal_ids 读的是
        #  模块内的 PROJECT_ROOT）。
        patch_module_root("lifecycle.micro_scheduler", self.tmp_root)
        self.ms.FOCUS_STATE_PATH = self._focus_path
        import paths
        paths.PROJECT_ROOT = self.tmp_root

        sys.modules.pop("promote_proposal_to_focus", None)
        self.promote_mod = importlib.import_module("promote_proposal_to_focus")
        self.promote_mod.FOCUS_PATH = self._focus_path
        patch_module_root("promote_proposal_to_focus", self.tmp_root)
        self.promote_mod.FOCUS_PATH = self._focus_path

        sys.modules.pop("lifecycle_monitor", None)
        self.lm = importlib.import_module("lifecycle_monitor")
        patch_module_root("lifecycle_monitor", self.tmp_root)

    def teardown(self):
        for mod_name in ("promote_proposal_to_focus", "rotation_queue", "lifecycle_monitor"):
            sys.modules.pop(mod_name, None)
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_focus(self, state: dict):
        self._focus_path.parent.mkdir(parents=True, exist_ok=True)
        self._focus_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_focus(self) -> dict:
        return json.loads(self._focus_path.read_text(encoding="utf-8"))

    def _polluted_state(self, last_pid=None):
        return {
            "queue": list(POLLUTED),
            "queue_full": list(POLLUTED),
            "last_proposal_id": last_pid or POLLUTED[0],
            "last_proposal_index": 0,
            "last_slot_index": 0,
            "focus_history": [],
        }

    # ── 用例 ──────────────────────────────────────────────

    def run_tests(self):
        # 1. sanitize 剔除夹具占位 id，保留真实课题
        kept, dropped = self.rq.sanitize_rotation_queue(
            POLLUTED + [PID_A], {PID_A, PID_B, PID_C})
        self.assert_eq(kept, [PID_A], "应只保留真实课题")
        self.assert_eq(len(dropped), len(POLLUTED),
                       f"应剔除 {len(POLLUTED)} 个夹具占位 id")

        # 2. 白名单权威：形态合法的假 id 同样被剔除
        #    （宽松的「白名单 OR 形态」判定会把它留下 → 虚增 queue_total）
        fake = "general-test-alpha-20260101"
        kept2, dropped2 = self.rq.sanitize_rotation_queue([fake], {PID_A})
        self.assert_eq(kept2, [], "形态合法但不在白名单的 id 应被剔除")
        self.assert_eq(dropped2, [fake], "应报告剔除了该假 id")

        # 3. fail-open 降级：白名单不可用（None）→ 退化为形态判定
        kept3, dropped3 = self.rq.sanitize_rotation_queue(POLLUTED + [PID_A], None)
        self.assert_in(PID_A, kept3, "白名单不可用时真实课题不应被误杀")
        self.assert_eq(len(dropped3), len(POLLUTED),
                       "形态判定应剔除全部无日期后缀的占位 id")

        # 4. _repair_focus_queue 无条件自愈（optimizing 为空也执行）
        self._write_focus(self._polluted_state())
        dropped4 = self.ms._repair_focus_queue()
        self.assert_true(dropped4 is not None and len(dropped4) > 0,
                         "自愈应返回被剔除的成员列表",
                         f"dropped={dropped4}")
        after4 = self._read_focus()
        self.assert_eq(after4.get("queue_full"), [], "自愈后 queue_full 应清空夹具")
        self.assert_eq(after4.get("queue"), [], "自愈后 queue 应清空夹具")

        # 4b. 自愈幂等：再次调用无变化
        dropped4b = self.ms._repair_focus_queue()
        self.assert_true(dropped4b is None, "自愈应幂等（第二次无剔除）",
                         f"dropped={dropped4b}")

        # 4c. 自愈保留真实课题（不误杀）
        self._write_focus({
            "queue": POLLUTED[:3] + [PID_A],
            "queue_full": POLLUTED + [PID_A, PID_B],
            "last_proposal_id": PID_A,
            "last_proposal_index": 0,
        })
        self.ms._repair_focus_queue()
        after4c = self._read_focus()
        self.assert_eq(after4c.get("queue_full"), [PID_A, PID_B],
                       "自愈后应只保留真实课题且保持顺序")

        # 5. monitor 读路径：混合名单（真实课题 + 夹具）下真实课题仍可定位
        #    这是真停滞误判的触发场景：pollution 混入后，真实 optimizing
        #    课题的 queue_index 变 -1 → _classify_stall_kind 判 blocked。
        self._write_focus({
            "queue": POLLUTED[:2] + [PID_A],
            "queue_full": POLLUTED + [PID_A, PID_B],
            "last_proposal_id": PID_A,
            "last_proposal_index": 0,
        })
        idx, total = self.lm._get_proposal_queue_position(PID_A)
        self.assert_true(idx >= 0,
                         "混合名单下白名单内课题应能定位（不应被误判不在队列）",
                         f"idx={idx} total={total}")
        self.assert_eq(total, 2, "剔除夹具后 queue_total 应为真实课题数（2）")

        # 5b. 全污染名单（真实课题完全不在名单中）→ -1 是正确语义
        #     （此时课题确实不在轮转名单里；monitor 的「不在队列」判定
        #      依赖的是真实成员关系，不是夹具污染）
        self._write_focus(self._polluted_state())
        idx5b, total5b = self.lm._get_proposal_queue_position(PID_A)
        self.assert_eq(idx5b, -1, "真实课题确实不在名单中时返回 -1")
        self.assert_eq(total5b, 0, "夹具全部剔除后 queue_total 为 0")

        # 6. promote 读路径：混合名单下不再拒真实课题
        #    （污染态下旧实现报「✗ proposal 不在轮转名单中」→ 人工干预入口堵死）
        self._write_focus({
            "queue": POLLUTED[:2] + [PID_A],
            "queue_full": POLLUTED + [PID_A, PID_B],
            "last_proposal_id": PID_A,
            "last_proposal_index": 0,
        })
        rc = self.promote_mod.cmd_promote(PID_A, "regression")
        self.assert_eq(rc, 0, "promote 不应再拒白名单内课题")
        after6 = self._read_focus()
        self.assert_eq(after6.get("queue_full")[0], PID_A,
                       "promote 后真实课题应位于队首")
        self.assert_eq(sorted(after6.get("queue_full")), sorted([PID_A, PID_B]),
                       "promote 后名单应只含真实课题")

        # 7. _sync_queue 写入路径剔除污染项
        state = self._polluted_state()
        optimizing = [{"proposal_id": PID_A}, {"proposal_id": PID_B}]
        self.ms._sync_queue(state, optimizing)
        self.assert_eq(state.get("queue_full"), [PID_A, PID_B],
                       "_sync_queue 应剔除夹具占位 id")
        self.assert_eq(state.get("queue"), [PID_A, PID_B],
                       "_sync_queue 应写入 WIP 窗口")


if __name__ == "__main__":
    suite = RotationQueuePollutionTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    passed = sum(1 for r in suite.results if r.passed)
    for r in suite.results:
        print(f"  {'✓' if r.passed else '✗'} {r.name}" +
              ("" if r.passed else f" — {r.msg}"))
    print(f"\n{passed}/{len(suite.results)} 通过")
    raise SystemExit(0 if passed == len(suite.results) else 1)
