#!/usr/bin/env python3
"""
test_micro_scheduler_rotation.py — 微调度器轮转逻辑回归测试

覆盖缺陷：
    fix4 (v6.8.3) 在 _focus_proposal_for_slot 的让出检查中使用了
    completed_rounds（已完成轮次）而非 completed_rounds+1（进行中轮次），
    导致已完成 ≥1 轮的 proposal 在下一轮进行中被误判为"本轮完成"而提前
    让出时段，中断连续聚焦，严重拖慢多轮优化速度。

验证点：
    - optimization_rounds=1 且 round 2 未完成 → 不应让出（继续聚焦同一 proposal）
    - optimization_rounds=1 且 round 2 完成 → 应让出（切换到下一个）
    - optimization_rounds=0 且 round 1 未完成 → 不应让出

注意：
    本测试不调用 hermes/LLM，通过 monkeypatch _is_round_complete 控制轮次
    完成状态，聚焦验证轮次编号选择逻辑（即 bug 根源）。
"""

import sys
import json
import shutil
import importlib
from pathlib import Path
from unittest.mock import MagicMock

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


class MicroSchedulerRotationTests(TestSuite):
    def __init__(self):
        super().__init__("微调度器轮转逻辑回归测试")
        self.tmp_root = None
        self.ms = None
        self._orig_is_round_complete = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 创建 research_proposals 目录结构
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / sub).mkdir(parents=True, exist_ok=True)

        # 强制重新导入 micro_scheduler
        for mod_name in list(sys.modules.keys()):
            if "micro_scheduler" in mod_name or mod_name in ["lifecycle", "paths", "common"]:
                del sys.modules[mod_name]

        self.ms = importlib.import_module("lifecycle.micro_scheduler")
        patch_module_root("lifecycle.micro_scheduler", self.tmp_root)
        # 确保 paths.PROJECT_ROOT 也指向隔离目录
        import paths
        paths.PROJECT_ROOT = self.tmp_root

    def teardown(self):
        # 恢复 monkeypatch
        if self._orig_is_round_complete is not None:
            self.ms._is_round_complete = self._orig_is_round_complete
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_focus_state(self, queue, last_proposal_id, last_slot_index):
        """写入隔离环境的聚焦状态文件。"""
        state = {
            "queue": queue,
            "last_proposal_id": last_proposal_id,
            "last_slot_index": last_slot_index,
            "last_proposal_index": 0,
            "last_day_key": "2026-08-05",
            "focus_history": [],
        }
        focus_path = self.tmp_root / "memory" / "lifecycle-focus.json"
        focus_path.parent.mkdir(parents=True, exist_ok=True)
        focus_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _make_mock_controller(self, prop_states):
        """创建模拟控制器，prop_states = {pid: {"optimization_rounds": N}}"""
        ctrl = MagicMock()
        ctrl._get_proposal_state.side_effect = lambda pid: prop_states.get(pid, {})
        ctrl._get_jobs.side_effect = lambda pid: []  # 空任务列表，避免副作用
        return ctrl

    def _patch_round_complete(self, round_results):
        """Monkeypatch _is_round_complete，round_results = {round_num: bool}。
        记录被查询的 round_num 以便断言。"""
        self._orig_is_round_complete = self.ms._is_round_complete
        queried_rounds = []

        def fake_is_round_complete(jobs, proposal_id, round_num):
            queried_rounds.append(round_num)
            return round_results.get(round_num, False)

        self.ms._is_round_complete = fake_is_round_complete
        return queried_rounds

    def run_tests(self):
        pid_a = "general-test-alpha-20260101"
        pid_b = "general-test-beta-20260101"

        # ================================================================
        # 测试 1（核心回归）: optimization_rounds=1, round 2 未完成 → 不应让出
        # bug 现场: 旧代码检查 round 1（已完成）→ 误判 done → 让出
        # 修复后: 检查 round 2（进行中）→ 未完成 → 继续聚焦
        # ================================================================
        self._write_focus_state(
            queue=[pid_a, pid_b],
            last_proposal_id=pid_a,
            last_slot_index=0,
        )
        ctrl = self._make_mock_controller({pid_a: {"optimization_rounds": 1}})
        queried = self._patch_round_complete({1: True, 2: False})

        optimizing = [{"proposal_id": pid_a}, {"proposal_id": pid_b}]
        result = self.ms._focus_proposal_for_slot(ctrl, slot_index=1, optimizing=optimizing)

        self.assert_eq(
            result, pid_a,
            "rounds=1 且 round 2 未完成时应继续聚焦同一 proposal",
            "已完成 1 轮后进行中的第 2 轮未完成，不应让出时段",
        )
        self.assert_true(
            2 in queried,
            "让出检查应查询 round 2（进行中轮次）",
            f"应检查 completed_rounds+1=2，实际查询了 rounds={queried}",
        )

        # ================================================================
        # 测试 2: optimization_rounds=1, round 2 也完成 → 应让出
        # ================================================================
        self._write_focus_state(
            queue=[pid_a, pid_b],
            last_proposal_id=pid_a,
            last_slot_index=0,
        )
        ctrl2 = self._make_mock_controller({pid_a: {"optimization_rounds": 1}})
        queried2 = self._patch_round_complete({1: True, 2: True})

        result2 = self.ms._focus_proposal_for_slot(ctrl2, slot_index=1, optimizing=optimizing)

        self.assert_eq(
            result2, pid_b,
            "rounds=1 且 round 2 也完成时应切换到下一个 proposal",
            "进行中的第 2 轮已完成，应让出时段并聚焦队列下一个",
        )

        # ================================================================
        # 测试 3: optimization_rounds=0, round 1 未完成 → 不应让出
        # ================================================================
        self._write_focus_state(
            queue=[pid_a, pid_b],
            last_proposal_id=pid_a,
            last_slot_index=0,
        )
        ctrl3 = self._make_mock_controller({pid_a: {"optimization_rounds": 0}})
        queried3 = self._patch_round_complete({1: False})

        result3 = self.ms._focus_proposal_for_slot(ctrl3, slot_index=1, optimizing=optimizing)

        self.assert_eq(
            result3, pid_a,
            "rounds=0 且 round 1 未完成时应继续聚焦",
            "首轮未完成，不应让出时段",
        )
        self.assert_true(
            1 in queried3,
            "让出检查应查询 round 1（首轮）",
            f"应检查 completed_rounds+1=1，实际查询了 rounds={queried3}",
        )

        # ================================================================
        # 测试 4（bug 守护）: 确保不让出时查询的是 completed_rounds+1 而非 completed_rounds
        # 当 rounds=2 时，应检查 round 3，而非 round 2
        # ================================================================
        self._write_focus_state(
            queue=[pid_a, pid_b],
            last_proposal_id=pid_a,
            last_slot_index=0,
        )
        ctrl4 = self._make_mock_controller({pid_a: {"optimization_rounds": 2}})
        queried4 = self._patch_round_complete({2: True, 3: False})

        result4 = self.ms._focus_proposal_for_slot(ctrl4, slot_index=1, optimizing=optimizing)

        self.assert_eq(
            result4, pid_a,
            "rounds=2 且 round 3 未完成时应继续聚焦",
            "已完成 2 轮后进行中的第 3 轮未完成，不应让出",
        )
        self.assert_true(
            3 in queried4 and 2 not in queried4,
            "rounds=2 时应查询 round 3 而非 round 2",
            f"应检查 round 3（进行中），不应检查 round 2（已完成），实际={queried4}",
        )


if __name__ == "__main__":
    suite = MicroSchedulerRotationTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    s = suite.summary()
    print(f"\n{'✓' if s['failed'] == 0 else '✗'} {s['name']}: {s['passed']}/{s['total']} 通过")
    for r in s["results"]:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if s["failed"] == 0 else 1)
