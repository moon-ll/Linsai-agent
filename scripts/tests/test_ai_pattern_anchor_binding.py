#!/usr/bin/env python3
"""
test_ai_pattern_anchor_binding.py — v6.9.25 两条闭环回归测试

覆盖：
    B. 程序化 AI 检测接入 prompt_optimizer 数据源
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


class AiPatternSourceTests(TestSuite):
    """B：prompt_optimizer 的 ai_pattern_analysis 数据源。"""

    def __init__(self):
        super().__init__("AI 检测数据源接入测试（v6.9.25-B）")
        self.tmp_root = None
        self.po = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "research_proposals").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / ".hermes" / "profiles" / "writer").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / ".hermes" / "profiles" / "writer" / "SOUL.md").write_text(
            "# writer SOUL\n", encoding="utf-8")

        for mod_name in ["prompt_optimizer"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        self.po = importlib.import_module("prompt_optimizer")
        patch_module_root("prompt_optimizer", self.tmp_root)
        self.po.HERMES_PROFILES_DIR = self.tmp_root / ".hermes" / "profiles"
        self.po.SUGGESTIONS_PATH = self.tmp_root / "memory" / "prompt-suggestions.json"

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_lifecycle(self, proposals: dict) -> None:
        (self.tmp_root / "research_proposals" / "_lifecycle.json").write_text(
            json.dumps({"proposals": proposals}, ensure_ascii=False, indent=2),
            encoding="utf-8")

    def run_tests(self):
        po = self.po

        # 1. 聚合：超长句 2 轮、自引用 2 轮 → 2 条 hint；冗余修饰词 1 轮 → 不出
        self._write_lifecycle({
            "prop-a": {"score_history": [
                {"round": 1, "at": _utc(1),
                 "ai_top_issues": ["超长句(>120字)：38处，扣0.76", "冗余修饰词超标：29次（阈值12），扣0.17"]},
                {"round": 2, "at": _utc(0.5),
                 "ai_top_issues": ["超长句(>120字)：25处，扣0.50"]},
            ]},
            "prop-b": {"score_history": [
                {"round": 4, "at": _utc(2),
                 "ai_top_issues": ["自引用泛滥：46次（阈值10/15），扣0.10"]},
                {"round": 5, "at": _utc(1),
                 "ai_top_issues": ["自引用泛滥：13次（阈值10/15），扣0.05"]},
            ]},
        })
        hints = po._collect_ai_pattern_hints()
        keys = {h["pattern_key"] for h in hints}
        self.assert_true("writer:ai:long_sentences" in keys, "超长句 2 轮证据应生成 hint")
        self.assert_true("writer:ai:self_reference" in keys, "自引用 2 轮证据应生成 hint")
        self.assert_true(
            "writer:ai:redundant_modifiers" not in keys,
            "单轮证据（<min_evidence=2）不应生成 hint")
        ls = next(h for h in hints if h["pattern_key"] == "writer:ai:long_sentences")
        self.assert_eq(ls["evidence_count"], 2, "超长句证据计数应为 2")
        self.assert_true("120 字" in ls["instruction"], "指令应写明 120 字检测阈值")

        # 2. 窗口过滤：20 天前的证据不入
        self._write_lifecycle({
            "prop-old": {"score_history": [
                {"round": 1, "at": _utc(20),
                 "ai_top_issues": ["超长句(>120字)：99处，扣1.98"]},
                {"round": 2, "at": _utc(19),
                 "ai_top_issues": ["超长句(>120字)：88处，扣1.76"]},
            ]},
        })
        self.assert_eq(po._collect_ai_pattern_hints(), [], "窗口外证据不应生成 hint")

        # 3. 建议生成：ai_pattern_analysis 来源进入 _generate_suggestions，
        #    且 auto 段标记内嵌 pattern_re（回收依据）
        self._write_lifecycle({
            "prop-a": {"score_history": [
                {"round": r, "at": _utc(1),
                 "ai_top_issues": ["超长句(>120字)：30处，扣0.60"]}
                for r in (1, 2)
            ]},
        })
        suggestions = po._generate_suggestions([], [], [], {"writer": [
            self.tmp_root / ".hermes" / "profiles" / "writer" / "SOUL.md"]})
        ai_sugs = [s for s in suggestions if s["source"] == "ai_pattern_analysis"]
        self.assert_true(len(ai_sugs) >= 1, "应生成 ai_pattern_analysis 建议")
        self.assert_true(
            "auto-opt:start" in ai_sugs[0]["content"],
            "建议内容应包裹 auto 段标记（回收锚点）")
        self.assert_eq(
            ai_sugs[0]["pattern_re"], "超长句",
            "pattern_re 应为可匹配检测字符串的关键词")

        # 4. 范本守门：全部 AI 检测指令不被 BENCHMARK_GUARD_RULES 拦截
        for rule in po.AI_PATTERN_RULES:
            reason = po._benchmark_conflict_guard({"content": rule["instruction"]})
            self.assert_eq(reason, None, f"指令 {rule['key']} 不应被范本守门拦截")

        # 5. 污染源清理：内联 pattern library 不再含"总字数≥4000"低标准
        inline = po._inline_pattern_library()
        blob = json.dumps(inline, ensure_ascii=False)
        self.assert_true("4000 字" not in blob, "内联库不应再含 4000 字低标准文案")


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
    for cls in (AiPatternSourceTests, AnchorBindingTests):
        s = cls()
        s.setup()
        s.run_tests()
        s.teardown()
        suites.append(s)
    print_report(suites)


if __name__ == "__main__":
    main()
