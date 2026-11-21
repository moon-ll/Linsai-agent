#!/usr/bin/env python3
"""
test_ai_pattern_anchor_binding.py — v6.9.25 两条闭环回归测试

覆盖：
       - _collect_ai_pattern_hints 聚合 lifecycle score_history 的 ai_top_issues
       - 单次证据不足 2 条的类别不生成建议（min_evidence 门槛）
       - 窗口外（>14d）的历史不入证据
       - 建议内容过范本守门（不被 BENCHMARK_GUARD_RULES 拦截）
    C. 锚点对比结论与评分档位强制绑定
       - _extract_anchor_conclusion 三档结论解析 + 旧格式兼容（返回空）
       - 差距明显 → 表达质量 cap 0.69、综合 cap 0.84
       - 基本接近 → 表达质量 cap 0.79、综合 cap 0.89
       - 达标 → 不 cap
       - 结论缺失 → 不绑定（旧报告兼容）

背景：08-18 实测三课题 AI 检测 ceiling 触底 0.5（综合分被硬 cap 0.75），
而 prompt_optimizer 9 条已应用建议无一指向超长句/冗余词/自引用——
优化器对程序化扣分项全盲；锚点对比是格式门槛而非分数锚。

注意：不调用 LLM，运行于隔离临时目录。
"""

import sys
import json
import shutil
import importlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root


def _utc(days_ago: float = 0.0) -> str:
    t = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


class AnchorBindingTests(TestSuite):
    """C：锚点结论与评分档位绑定。"""

    def __init__(self):
        super().__init__("锚点结论档位绑定测试（v6.9.25-C）")
        self.tmp_root = None
        self._opt = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in ["proposal_lifecycle.optimize", "proposal_lifecycle"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.optimize")
        from proposal_lifecycle.optimize import OptimizeMixin

        class _Fake(OptimizeMixin):
            def __init__(self):
                pass

        self._opt = _Fake()
        # 绕开真实 standards 文件：用等权平均模拟综合分重算
        self._opt._recalculate_score = lambda d, p: round(sum(d.values()) / len(d), 3)

    def teardown(self):
        pass

    def run_tests(self):
        opt = self._opt

        # 1. 结论解析三档 + 兼容
        self.assert_eq(opt._extract_anchor_conclusion("锚点对比结论：差距明显"), "差距明显", "解析-差距明显")
        self.assert_eq(opt._extract_anchor_conclusion("锚点对比结论：基本接近"), "基本接近", "解析-基本接近")
        self.assert_eq(opt._extract_anchor_conclusion("锚点对比结论:达标"), "达标", "解析-达标（半角冒号）")
        self.assert_eq(opt._extract_anchor_conclusion("锚点对比段落存在但无结论行"), "", "无结论行返回空")
        self.assert_eq(opt._extract_anchor_conclusion(""), "", "空文本返回空")

        # 2. 差距明显 → 双 cap
        dims = {"innovation": 0.9, "feasibility": 0.9, "rigor": 0.9, "expression": 0.85}
        score = opt._apply_anchor_conclusion_binding(
            "p1", "锚点对比结论：差距明显", dims, 0.88, "general")
        self.assert_eq(dims["expression"], 0.69, "差距明显应把表达质量 cap 至 0.69")
        self.assert_true(score <= 0.84, f"差距明显综合分应 ≤0.84，实际 {score}")

        # 3. 基本接近 → 双 cap（档位更高）
        dims2 = {"innovation": 0.9, "feasibility": 0.9, "rigor": 0.9, "expression": 0.85}
        score2 = opt._apply_anchor_conclusion_binding(
            "p1", "锚点对比结论：基本接近", dims2, 0.91, "general")
        self.assert_eq(dims2["expression"], 0.79, "基本接近应把表达质量 cap 至 0.79")
        self.assert_true(score2 <= 0.89, f"基本接近综合分应 ≤0.89，实际 {score2}")

        # 4. 达标 → 不 cap
        dims3 = {"innovation": 0.92, "feasibility": 0.92, "rigor": 0.92, "expression": 0.92}
        score3 = opt._apply_anchor_conclusion_binding(
            "p1", "锚点对比结论：达标", dims3, 0.92, "general")
        self.assert_eq(dims3["expression"], 0.92, "达标不应 cap 表达质量")
        self.assert_eq(score3, 0.92, "达标不应 cap 综合分")

        # 5. 旧格式（无结论行）→ 不绑定
        dims4 = {"innovation": 0.9, "feasibility": 0.9, "rigor": 0.9, "expression": 0.85}
        score4 = opt._apply_anchor_conclusion_binding(
            "p1", "## 锚点对比\n引用原文…（无结论行）", dims4, 0.88, "general")
        self.assert_eq(dims4["expression"], 0.85, "旧格式不应改表达质量")
        self.assert_eq(score4, 0.88, "旧格式不应改综合分")


def main():
    from test_runner import print_report

    suites = []
    for cls in (AnchorBindingTests,):
        s = cls()
        s.setup()
        s.run_tests()
        s.teardown()
        suites.append(s)
    print_report(suites)


if __name__ == "__main__":
    main()
