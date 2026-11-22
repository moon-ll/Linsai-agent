#!/usr/bin/env python3
"""test_a_gate_raw_score.py — A 通道收分口径拆分测试（v7.3.41）

背景：
    A 通道（5 模块各自 ≥0.90）此前读取 cap 后综合分，而 overall_ceiling
    按表达质量（含"无 AI 写作痕迹"）把总分封顶到 ≤0.85，导致科学质量被
    文风一票否决、通道实质不可达。v7.3.41 把判定分（cap 前四维加权）与
    展示分（cap 后综合）拆开，开关 LINSAI_A_GATE_RAW_SCORE 默认 on。

覆盖：
    1. 开关默认值与关闭值解析
    2. 同一组四维分数：有/无 ceiling 下 A 判定结果不同
    3. 关闭开关可复现旧口径（gate = display）
    4. 总评展示分仍受 ceiling 约束（display 保留 cap 后值）
    5. 缺 score_raw 时回落 display；2 维口径（references/method_manual）不取 raw
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from proposal_lifecycle.a_gate import (  # noqa: E402
    A_GATE_RAW_ENV,
    calibers,
    gate_score,
    module_gate_score,
    raw_gate_enabled,
    section_gate_passed,
)
from test_runner import TestSuite  # noqa: E402


class AGateRawScoreTests(TestSuite):
    def __init__(self):
        super().__init__("A 通道原始分口径")

    def run_tests(self):
        self._switch_default_on()
        self._ceiling_changes_verdict()
        self._switch_rollback()
        self._display_remains_capped()
        self._missing_raw_falls_back()
        self._two_dim_sections_ignore_raw()
        self._module_gate_uses_latest_raw()

    def _switch_default_on(self):
        self.assert_true(raw_gate_enabled({}), "未设置开关应默认开启")
        for off in ("0", "false", "off", "no"):
            self.assert_eq(raw_gate_enabled({A_GATE_RAW_ENV: off}), False,
                           f"开关值 {off} 应关闭")

    def _ceiling_changes_verdict(self):
        """同一组四维分数：cap 后 0.85 不过，cap 前 0.90 过。"""
        capped, raw = 0.85, 0.90
        self.assert_eq(section_gate_passed(capped, raw, 0.90, enabled=True), True,
                       "原始分口径下 0.90 应通过 A 门")
        self.assert_eq(section_gate_passed(capped, raw, 0.90, enabled=False), False,
                       "旧口径下 cap 后 0.85 不应通过 A 门")

    def _switch_rollback(self):
        self.assert_eq(gate_score(0.85, 0.90, enabled=False), 0.85,
                       "关闭开关后判定分应等于旧口径 cap 后分")

    def _display_remains_capped(self):
        c = calibers(0.85, 0.90, enabled=True)
        self.assert_eq(c["display"], 0.85, "总评展示分必须保留 ceiling cap")
        self.assert_eq(c["gate"], 0.90, "判定分应取 cap 前原始分")
        self.assert_eq(c["caliber"], "raw", "口径标记应为 raw")

    def _missing_raw_falls_back(self):
        c = calibers(0.80, None, enabled=True)
        self.assert_eq(c["gate"], 0.80, "缺 score_raw 时判定分回落 display")
        self.assert_eq(c["caliber"], "display", "口径标记应为 display")

    def _two_dim_sections_ignore_raw(self):
        hist = [
            {"focus_section": "references", "score": 0.87, "score_raw": 0.95,
             "caliber": "references_2d", "round": 3,
             "dim_scores": {"rigor": 0.9, "completeness": 0.84}},
            {"focus_section": "method_manual", "score": 0.89, "score_raw": 0.93,
             "caliber": "section_4d", "round": 2,
             "dim_scores": {"readiness": 0.9, "rigor": 0.88}},
        ]
        mg_ref = module_gate_score(hist, "references", enabled=True)
        mg_man = module_gate_score(hist, "method_manual", enabled=True)
        self.assert_eq(mg_ref["gate"], 0.87, "references 2 维口径不得取四维 raw 占位值")
        self.assert_eq(mg_man["gate"], 0.89, "method_manual 2 维口径不得取四维 raw 占位值")

    def _module_gate_uses_latest_raw(self):
        hist = [
            {"focus_section": "scheme", "score": 0.84, "score_raw": 0.91,
             "caliber": "section_4d", "round": 2, "dim_scores": {"innovation": 0.92}},
            {"focus_section": "scheme", "score": 0.85, "score_raw": 0.90,
             "caliber": "section_4d", "round": 3, "dim_scores": {"innovation": 0.90}},
        ]
        mg = module_gate_score(hist, "scheme", enabled=True)
        self.assert_eq(mg["found"], True, "应找到最近一条 scheme 记录")
        self.assert_eq(mg["round"], 3, "应取最近轮次")
        self.assert_eq(mg["gate"], 0.90, "判定分应为该轮 raw")
        off = module_gate_score(hist, "scheme", enabled=False)
        self.assert_eq(off["gate"], 0.85, "关闭开关应回到 cap 后分")


if __name__ == "__main__":
    suite = AGateRawScoreTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    s = suite.summary()
    print(f"{s['name']}：通过 {s['passed']}/{s['total']}")
    for r in s["results"]:
        if not r.passed:
            print(f"  ✗ {r.name} | {r.msg}")
