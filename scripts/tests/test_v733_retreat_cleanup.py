#!/usr/bin/env python3
"""
test_v733_retreat_cleanup.py — 退回跨遍残留清理（v7.3.3）单测

背景（实测 2026-11-03，v7.3.0 全课题退回升级轮）：
    ① quality_warning 残留上一遍逃生阀文案（旧 5 模块口径），误导决策包；
    ② negative_feedback_alert 带旧遍原因进入新遍（moire/bsv 陈账）；
    ③ monitor_history 不随退回清空，check_negative_feedback 用 [-3:] 连续
      性判定把旧遍尾部与新遍拼接出"连续 3 轮下降"伪信号（attosecond/
      ssh-weyl 退回后首个 monitor 步即触发）。

验证点：
    1. transition 退回：旧遍警告滤除、守卫行保留、负反馈清除、
       monitor_history_pass_start 写入
    2. check_negative_feedback 边界切片：旧遍 3 连降 + 新遍 1 条 → 不触发；
       新遍内 3 连降 → 触发
    3. 数据修复语义与生产 transition 一致
"""

import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from test_runner import TestSuite


class RetreatCleanupTests(TestSuite):
    """v7.3.3: 退回跨遍残留清理测试。"""

    def __init__(self):
        super().__init__("退回跨遍清理测试")

    def setup(self):
        pass

    def teardown(self):
        pass

    # ===== 纯函数部分：check_negative_feedback 边界 =====

    def test_boundary_slices_pass_history(self):
        """场景1: 旧遍 3 连降 + 新遍 1 条 → 不触发下降告警。"""
        from adversarial.scoring import check_negative_feedback
        st = {
            "monitor_history_pass_start": 3,
            "monitor_history": [
                {"monitor_independent_score": 0.9, "at": "2026-11-01T00:00:00Z"},
                {"monitor_independent_score": 0.85, "at": "2026-11-01T05:00:00Z"},
                {"monitor_independent_score": 0.8, "at": "2026-11-02T00:00:00Z"},
                # 本遍起点（退回后首个 monitor）
                {"monitor_independent_score": 0.88, "at": "2026-11-03T02:00:00Z"},
            ],
        }
        triggered, reasons = check_negative_feedback(st, {})
        self.assert_true(not triggered, "旧遍 3 连降 + 新遍 1 条不应触发")
        self.assert_true(
            all("连续" not in r for r in reasons), f"不应含连续性原因: {reasons}")

    def test_boundary_ignores_stale_boundary_index(self):
        """场景2: 起点=全部历史（无新条目）→ 不触发。"""
        from adversarial.scoring import check_negative_feedback
        st = {
            "monitor_history_pass_start": 3,
            "monitor_history": [
                {"monitor_independent_score": 0.9},
                {"monitor_independent_score": 0.85},
                {"monitor_independent_score": 0.8},
            ],
        }
        triggered, _ = check_negative_feedback(st, {})
        self.assert_true(not triggered, "本遍无条目不应触发")

    def test_in_pass_decline_still_triggers(self):
        """场景3: 新遍内真实 3 连降 → 照常触发（修复不掩盖真信号）。"""
        from adversarial.scoring import check_negative_feedback
        st = {
            "monitor_history_pass_start": 1,
            "monitor_history": [
                {"monitor_independent_score": 0.95, "at": "2026-11-02T00:00:00Z"},
                {"monitor_independent_score": 0.9},
                {"monitor_independent_score": 0.85},
                {"monitor_independent_score": 0.8},
            ],
        }
        triggered, reasons = check_negative_feedback(st, {})
        self.assert_true(triggered, "本遍内 3 连降应触发")
        self.assert_true(
            any("monitor" in r for r in reasons), f"应含 monitor 下降原因: {reasons}")

    def test_missing_boundary_backward_compatible(self):
        """场景4: 无边界字段（旧数据）→ 全量历史，行为不变。"""
        from adversarial.scoring import check_negative_feedback
        st = {
            "monitor_history": [
                {"monitor_independent_score": 0.9},
                {"monitor_independent_score": 0.85},
                {"monitor_independent_score": 0.8},
            ],
        }
        triggered, _ = check_negative_feedback(st, {})
        self.assert_true(triggered, "旧数据（无边界）应保持原行为")

    # ===== transition 集成部分（源码级断言 + 纯逻辑复演） =====

    def test_transition_cleanup_wired(self):
        """场景5: transition 退回路径含 v7.3.3 清理块（源码级接线）。"""
        src = (_SCRIPTS / "proposal_lifecycle" / "transitions.py").read_text(
            encoding="utf-8")
        self.assert_true(
            "monitor_history_pass_start" in src, "退回路径应写 monitor 起点")
        self.assert_true(
            "negative_feedback_cleared_reason" in src, "退回路径应清负反馈")
        self.assert_true(
            '_GUARD_PREFIXES = ("KB引用", "6章节缺")' in src,
            "退回路径应保留守卫类警告前缀")

    def test_cleanup_semantics_reference(self):
        """场景6: 清理语义参照实现——守卫行保留 + 逃生阀行滤除。"""
        GUARD = ("KB引用", "6章节缺")
        old_qw = "\n".join([
            "⚠ 质量警告: 达到最大轮数8，整篇有效分0.86（monitor独立评分）低于达标线0.90。",
            "KB引用 0/0（wikilink 守卫 v7.2.30 fail）：下轮 writer 必须引用",
            "6章节缺 产出定位（structure_guard v7.2.30 fail）",
        ])
        kept = [ln for ln in old_qw.splitlines()
                if ln.strip() and ln.strip().startswith(GUARD)]
        self.assert_eq(len(kept), 2, "守卫行保留 2 条")
        self.assert_true(
            all("最大轮数" not in ln for ln in kept), "逃生阀行应滤除")

    def test_cleared_field_list_typed(self):
        """场景7（v7.3.78）: negative_feedback_cleared 规范类型 list——
        v7.3.3 旧实现写 bool True 与 clear_negative_feedback 的 append
        冲突（实测 2026-11-11 attosecond 人工清除 AttributeError 崩溃），
        退回清理写入侧与清除入口两侧均须做非 list 归一。"""
        trans_src = (_SCRIPTS / "proposal_lifecycle" / "transitions.py").read_text(
            encoding="utf-8")
        self.assert_true(
            "isinstance(_cleared_history, list)" in trans_src,
            "退回清理应将遗留 bool 归一为 list 再追加")
        cron_src = (_SCRIPTS / "proposal_lifecycle" / "cron.py").read_text(
            encoding="utf-8")
        self.assert_true(
            "isinstance(cleared_history, list)" in cron_src,
            "clear_negative_feedback 应防御非 list 遗留类型")
        self.assert_true(
            "negative_feedback_cleared\"] = True" not in trans_src,
            "退回清理不应再写入 bool 类型")

    def test_cleared_legacy_bool_normalize(self):
        """场景8（v7.3.78）: 遗留 bool True → 归一 list → 追加条目，
        形状与 registration.py 注册口径一致（[-10:] 截断）。"""
        legacy = True  # v7.3.3 旧实现写入的 bool 遗留态
        history = legacy if isinstance(legacy, list) else []
        history.append({
            "cleared_at": "2026-11-11T00:00:00Z",
            "previous_reasons": ["writer/critic 本地分数连续 3 轮双降"],
            "reason": "v7.3.3 退回自动清除（跨遍状态清理）",
        })
        normalized = history[-10:]
        self.assert_true(isinstance(normalized, list), "归一后应为 list")
        self.assert_eq(len(normalized), 1, "bool 无历史条目，归一后恰 1 条")
        self.assert_eq(normalized[0]["reason"][:7], "v7.3.3 ",
                       "条目 reason 应标注退回清理来源")

    def run_tests(self):
        self.test_boundary_slices_pass_history()
        self.test_boundary_ignores_stale_boundary_index()
        self.test_in_pass_decline_still_triggers()
        self.test_missing_boundary_backward_compatible()
        self.test_transition_cleanup_wired()
        self.test_cleanup_semantics_reference()
        self.test_cleared_field_list_typed()
        self.test_cleared_legacy_bool_normalize()


if __name__ == "__main__":
    suite = RetreatCleanupTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    total = len(suite.results)
    passed = sum(1 for r in suite.results if r.passed)
    failed = [r for r in suite.results if not r.passed]
    print(f"\n=== {suite.name} ===")
    print(f"通过 {passed}/{total}")
    for r in failed:
        print(f"  ✗ {r.name}: {r.msg}")
    sys.exit(1 if failed else 0)
