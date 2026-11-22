#!/usr/bin/env python3
"""
test_learning_cycle_dispatch.py — 学习周期源分发回归测试（v6.8.45 修复）

覆盖：
    - run_learning_cycle 对 v6.8.42 多源学术检索（openalex 等）的分发
    - 含 arXiv ID 的多源论文复用 distill_arxiv_paper
    - 仅 DOI 的期刊论文走元数据蒸馏并落盘 wiki/papers/doi-*.md
    - wikipedia 词条（默认源，历史缺口）复用 web 蒸馏
    - 未知 source 仍落入 failed（不误吞）

背景：
    v6.8.42 将 openalex 纳入 discover_learning_opportunities 默认源，但
    run_learning_cycle 的分发器未同步，多源论文全部落入
    `unknown source: openalex` 失败分支，学习周期内无法进入知识库。

原则：
    纯单元测试——不调 LLM、不联网；蒸馏/KB/成本函数全部打桩，
    在 create_isolated_env() 隔离目录内运行，零污染。
"""

import importlib
import sys
import types
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root


class LearningCycleDispatchTests(TestSuite):
    def __init__(self):
        super().__init__("学习周期源分发测试")
        self.tmp_root = None
        self.le = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in ["learning_engine"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        self.le = importlib.import_module("learning_engine")
        patch_module_root("learning_engine", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            import shutil
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        for mod_name in ["learning_engine"]:
            sys.modules.pop(mod_name, None)

    def _run_cycle(self, opportunities):
        """构造最小可跑的学习周期：ef/蒸馏/KB/成本全部打桩，返回 result。"""
        calls = {"arxiv": [], "content": [], "saved": [], "web": []}

        stub_ef = types.SimpleNamespace(
            discover_learning_opportunities=lambda **kw: list(opportunities)
        )
        self.le._import_ef = lambda: stub_ef
        self.le.check_cost_limit = lambda: (True, "")
        self.le._record_cost = lambda *a, **k: None

        def fake_distill_arxiv(paper, cost_tracker=None, ensure_pdf=True):
            calls["arxiv"].append(paper.get("arxiv_id", ""))
            return f"wiki/papers/{paper.get('arxiv_id', '')}.md"

        def fake_distill_content(source_type, source_data, cost_tracker=None):
            calls["content"].append(source_type)
            return ("---\ntitle: stub\n---\n# stub", [], {})

        def fake_distill_web(web_data, cost_tracker=None):
            calls["web"].append(web_data.get("title", ""))
            return "wiki/concepts/stub.md"

        stub_kb = types.SimpleNamespace(
            save_distilled_wiki=lambda rel, text, raw_rel_path=None: calls["saved"].append(rel),
            log_growth=lambda *a, **k: None,
        )
        self.le._import_kb = lambda: stub_kb
        self.le._integrate_concept = lambda *a, **k: None

        self.le.distill_arxiv_paper = fake_distill_arxiv
        self.le.distill_content = fake_distill_content
        self.le.distill_web_search = fake_distill_web

        result = self.le.run_learning_cycle(query="test", sources=["openalex"], max_items=3)
        return result, calls

    def _test_openalex_with_arxiv_id_uses_arxiv_distill(self):
        """openalex 论文含 arXiv ID → 复用 arXiv 蒸馏路径。"""
        ops = [{"source": "openalex", "arxiv_id": "2401.00001",
                "title": "P1", "doi": "10.1/x", "_score": {"overall": 0.9}}]
        result, calls = self._run_cycle(ops)
        self.assert_eq(result["created"], ["wiki/papers/2401.00001.md"],
                       f"应经 arXiv 蒸馏入库（实际 {result}）")
        self.assert_eq(calls["arxiv"], ["2401.00001"], "arXiv 蒸馏被调用")
        self.assert_eq(result["failed"], [],
                       f"不应出现 unknown source 失败（实际 {result['failed']}）")

    def _test_openalex_doi_only_lands_in_papers(self):
        """v6.8.45 核心回归：仅 DOI 的 openalex 期刊论文不再落入 unknown source。"""
        ops = [{"source": "openalex", "arxiv_id": "",
                "doi": "10.1038/s41567-018-0315-5",
                "title": "Solid-state HHG", "_score": {"overall": 0.88}}]
        result, calls = self._run_cycle(ops)
        self.assert_eq(len(result["created"]), 1,
                       f"DOI 期刊论文应入库（实际 {result}）")
        self.assert_true(result["created"] and "doi-10-1038-s41567-018-0315-5" in result["created"][0],
                         f"落盘路径应含 DOI slug（实际 {result['created']}）")
        self.assert_eq(result["failed"], [],
                       f"不应有失败（实际 {result['failed']}）")
        self.assert_eq(calls["content"], ["arxiv_paper"],
                       "仅 DOI 时复用 arxiv_paper 蒸馏 prompt")

    def _test_wikipedia_source_dispatches_to_web_distill(self):
        """wikipedia 词条（默认源，历史缺口）复用 web 蒸馏。"""
        ops = [{"source": "wikipedia", "title": "High harmonic generation",
                "url": "https://en.wikipedia.org/wiki/HHG",
                "_score": {"overall": 0.7}}]
        result, calls = self._run_cycle(ops)
        self.assert_eq(result["created"], ["wiki/concepts/stub.md"],
                       f"wikipedia 应经 web 蒸馏入库（实际 {result}）")
        self.assert_eq(result["failed"], [],
                       f"不应有失败（实际 {result['failed']}）")

    def _test_unknown_source_still_fails(self):
        """控制组：真正未知的 source 仍落入 failed，不被误吞。"""
        ops = [{"source": "foobar", "title": "X", "_score": {"overall": 0.5}}]
        result, calls = self._run_cycle(ops)
        self.assert_eq(result["created"], [], "未知 source 不应产出")
        self.assert_true(any("unknown source: foobar" in f for f in result["failed"]),
                         f"未知 source 应记入 failed（实际 {result['failed']}）")

    def run_tests(self):
        self._test_openalex_with_arxiv_id_uses_arxiv_distill()
        self._test_openalex_doi_only_lands_in_papers()
        self._test_wikipedia_source_dispatches_to_web_distill()
        self._test_unknown_source_still_fails()
