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

from test_runner import TestSuite, create_isolated_env, patch_module_root, patch_kb_sync_noop, REAL_ROOT


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
        patch_kb_sync_noop(self.ms)  # 拦截 KB 同步，避免测试写穿真实 knowledge/
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

        # ================================================================
        # 测试 5（修复 A 守护）: _is_proposal_stuck 应识别 repair_attempts 达标
        # bug 现场: orchestrator repair 会把 attempts 重置为 0（orchestrator.py
        # _run_repair 的 failed→pending 重置），导致只看 attempts 的旧逻辑永远
        # 判不出 stuck；修复后必须同时检查单调递增的 repair_attempts。
        # ================================================================
        mock_ctrl5 = MagicMock()
        # failed job 的 attempts 已被 repair 清零，但 repair_attempts 已达上限
        mock_ctrl5._get_jobs.return_value = [
            {"job_id": "r1-critic", "status": "failed", "attempts": 0, "repair_attempts": self.ms.MAX_JOB_ATTEMPTS},
            {"job_id": "r1-writer", "status": "pending", "depends_on": ["r1-critic"]},
        ]
        stuck5 = self.ms._is_proposal_stuck(mock_ctrl5, pid_a)
        self.assert_true(
            stuck5,
            "repair_attempts 达标的 failed job 应判定 proposal 卡死",
            "attempts 被 repair 清零后，须靠 repair_attempts 才能识别修复系统已放弃的 job",
        )

        # ================================================================
        # 测试 6（修复 B 守护）: 进行中轮次未完成但 proposal 卡死时应让出焦点
        # bug 现场: round_done=false 时的 early return 绕过下方 _is_proposal_stuck
        # 兜底，卡死 proposal 永久占用时段焦点、饿死其余 proposal；修复后卡死时
        # 应切换到队列下一个 proposal。
        # ================================================================
        self._write_focus_state(
            queue=[pid_a, pid_b],
            last_proposal_id=pid_a,
            last_slot_index=0,
        )
        ctrl6 = self._make_mock_controller({pid_a: {"optimization_rounds": 1}})
        self._patch_round_complete({2: False})  # round 2 未完成

        orig_stuck = self.ms._is_proposal_stuck
        self.ms._is_proposal_stuck = lambda c, pid: pid == pid_a  # 仅 pid_a 卡死
        try:
            result6 = self.ms._focus_proposal_for_slot(ctrl6, slot_index=1, optimizing=optimizing)
        finally:
            self.ms._is_proposal_stuck = orig_stuck

        self.assert_eq(
            result6, pid_b,
            "进行中轮次未完成但卡死时应让出焦点",
            "卡死 proposal 不应永久占用时段，应切换到队列下一个",
        )

        # ================================================================
        # 测试 7（v6.8.19 修复守护）: 同一时段内连续调用，
        # state["last_proposal_id"] 必须与本次返回的 pid 同步，
        # 否则下次 _rebalance_index 会用旧值校准队列索引，
        # 表现为同一时段内每 5 分钟轮换一个 proposal，
        # 5 个 optimizing 课题永远跑不完一轮（focus_history 实证见
        # 2026-08-09 23:05 ~ 2026-08-10 00:00 的 60+ 条 5min 轮换记录）。
        # ================================================================
        # 模拟场景：上一次聚焦 pid_a，但 state 中 last_proposal_id
        # 因某次路径未走保存分支而保持空串 / 错值。
        self._write_focus_state(
            queue=[pid_a, pid_b],
            last_proposal_id="",  # 状态漂移：被清空
            last_slot_index=1,    # 与本次 slot 相同 → 走时段内保持分支
        )
        ctrl7 = self._make_mock_controller({pid_a: {"optimization_rounds": 0}})
        # round 1 未完成 → 走到时段内保持分支
        self._patch_round_complete({1: False})

        result7 = self.ms._focus_proposal_for_slot(
            ctrl7, slot_index=1, optimizing=optimizing
        )
        self.assert_eq(
            result7, pid_a,
            "时段内连续调用应继续聚焦 pid_a",
            "state.last_proposal_id 漂移时，else 分支必须按 queue 正确选择并同步状态",
        )

        # 关键守护：本次调用必须把 state.last_proposal_id 写回 pid_a，
        # 否则下一次 tick 仍会读到空串，_rebalance_index 重置到队首 → 漂移
        focus_path = self.tmp_root / "memory" / "lifecycle-focus.json"
        import json as _json
        persisted = _json.loads(focus_path.read_text(encoding="utf-8"))
        self.assert_eq(
            persisted.get("last_proposal_id"), pid_a,
            "state.last_proposal_id 必须与本次返回的 pid 同步",
            "v6.8.19: else 分支需同步写回 last_proposal_id，否则下次 rebalance 漂移",
        )
        self.assert_eq(
            persisted.get("last_slot_index"), 1,
            "state.last_slot_index 必须与本次 slot_index 同步",
            "v6.8.19: else 分支需同步写回 last_slot_index，保持时段时间锚点",
        )

        # ================================================================
        # 测试 8（v6.9.31 修复守护）: slot_done 标记必须能驱动轮转
        # bug 现场: 时段切换时先 pop slot_{i}_done 再读同一个内存 dict，
        # "上一时段中途完成轮次"信号永远读不到（round_done 恒走
        # _is_round_complete 分支）；聚焦课题每推进一轮即重置软卡死
        # 计数，可无限持有焦点，饿死队列其余课题（08-21 实证：bsv 停滞
        # 87.7h / berry 46.9h，order-param r6 中途完成后仍持有 slot 3）。
        # ================================================================
        self._write_focus_state(
            queue=[pid_a, pid_b],
            last_proposal_id=pid_a,
            last_slot_index=0,
        )
        # pid_a 的 round 1 在 slot 0 中途完成 → slot_0_done 已置位
        focus_path = self.tmp_root / "memory" / "lifecycle-focus.json"
        state8 = json.loads(focus_path.read_text(encoding="utf-8"))
        state8["slot_0_done"] = True
        focus_path.write_text(json.dumps(state8, ensure_ascii=False), encoding="utf-8")

        ctrl8 = self._make_mock_controller({pid_a: {"optimization_rounds": 1}})
        self._patch_round_complete({2: False})  # 新轮次 round 2 未完成

        result8 = self.ms._focus_proposal_for_slot(ctrl8, slot_index=1, optimizing=optimizing)
        self.assert_eq(
            result8, pid_b,
            "上一时段 slot_done 置位时应轮转到队列下一个",
            "轮次中途完成后（slot_done=True），下一时段必须让出焦点，"
            "否则聚焦课题无限持有时段、饿死队列",
        )
        # 守护：flag 消费后必须清除，防止跨时段残留误判
        persisted8 = json.loads(focus_path.read_text(encoding="utf-8"))
        self.assert_true(
            "slot_0_done" not in persisted8,
            "slot_done 标记消费后应清除",
            "标记残留会导致下一时段切换时重复让出",
        )

        # ================================================================
        # 测试 9（v6.9.31 加固守护）: focus_history 去重——同一 (slot,
        # proposal) 只记一条，50 条上限应覆盖多次时段切换而非约一个时段
        # bug 现场: 每 5 分钟 tick 追加一条，满时段约 49 条冲掉前一时段
        # 全部记录，_count_consecutive_slots 在时段切换时恒为 1，
        # MAX_SOFT_STUCK_SLOTS=2 软卡死防线对满时段失效。
        # ================================================================
        self._write_focus_state(
            queue=[pid_a, pid_b],
            last_proposal_id=pid_a,
            last_slot_index=0,
        )
        ctrl9 = self._make_mock_controller({pid_a: {"optimization_rounds": 0}})
        self._patch_round_complete({1: False})  # round 1 未完成且无推进

        # 同一时段连续调用 20 次（模拟 5 分钟 tick）
        for _ in range(20):
            self.ms._focus_proposal_for_slot(ctrl9, slot_index=0, optimizing=optimizing)
        persisted9 = json.loads(focus_path.read_text(encoding="utf-8"))
        self.assert_eq(
            len(persisted9.get("focus_history", [])), 1,
            "同一 (slot, proposal) 的 20 次 tick 只应记录 1 条",
            "去重失败会让 50 条上限退化为约一个时段的窗口",
        )
        # 切换到 slot 1（仍聚焦 pid_a），再 20 次 tick → 2 条
        for _ in range(20):
            self.ms._focus_proposal_for_slot(ctrl9, slot_index=1, optimizing=optimizing)
        persisted9b = json.loads(focus_path.read_text(encoding="utf-8"))
        self.assert_eq(
            len(persisted9b.get("focus_history", [])), 2,
            "跨时段同课题应各记 1 条",
            "时段切换记录缺失会破坏 _count_consecutive_slots 计数",
        )
        # 两个时段无推进 → 软卡死应触发让出（历史去重后仍正确计数）
        result9 = self.ms._focus_proposal_for_slot(ctrl9, slot_index=2, optimizing=optimizing)
        self.assert_eq(
            result9, pid_b,
            "连续 2 个时段轮次无推进应触发软卡死让出",
            "去重后 _count_consecutive_slots 须保持原计数语义",
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
