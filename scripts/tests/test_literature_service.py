#!/usr/bin/env python3
"""
test_literature_service.py — LiteratureService 解析器单元测试（v6.8.3 修复）

覆盖：
    - _parse_researcher_output JSON 数组解析（主路径）
    - _try_parse_json: 自然语言中含 [ 字符时不阻断后续 JSON 提取
    - _try_parse_pipe_or_table: 管道符 / Markdown 表格格式
    - _try_parse_natural_language: 兜底 arxiv_id 提取
    - _needs_metadata 标记正确

注意：
    本测试不调用 LLM API，仅验证解析逻辑。
"""

import sys
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT
import importlib


class LiteratureServiceParserTests(TestSuite):
    def __init__(self):
        super().__init__("LiteratureService 解析器测试")
        self.tmp_root = None
        self.lit_svc_mod = None
        self.svc = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in ["literature_service"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        self.lit_svc_mod = importlib.import_module("literature_service")
        patch_module_root("literature_service", self.tmp_root)
        self.svc = self.lit_svc_mod.LiteratureService()

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            import shutil
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _test_json_array_clean(self):
        """纯 JSON 数组能被正确解析。"""
        text = '[{"arxiv_id": "2401.12345", "title": "HHG in Solids", "authors": "Zhang et al.", "year": "2024", "score": 0.9, "tldr": "摘要"}]'
        papers = self.svc._parse_researcher_output(text)
        self.assert_eq(len(papers), 1, "解析 1 篇论文")
        self.assert_eq(papers[0]["arxiv_id"], "2401.12345", "arxiv_id 正确")
        self.assert_eq(papers[0]["title"], "HHG in Solids", "title 正确")

    def _test_json_array_with_markdown_fence(self):
        """带 markdown 代码块标记的 JSON 数组能被正确解析。"""
        text = '```json\n[{"arxiv_id": "2402.67890", "title": "Berry Phase", "authors": "Li et al.", "year": "2024", "score": 0.85, "tldr": "贝里相位"}]\n```'
        papers = self.svc._parse_researcher_output(text)
        self.assert_eq(len(papers), 1, "去围栏后解析 1 篇论文")
        self.assert_eq(papers[0]["arxiv_id"], "2402.67890", "arxiv_id 正确")

    def _test_json_after_natural_language_bracket(self):
        """v6.8.3 修复: 自然语言中包含 [ 字符时，不阻断后续 JSON 数组提取。

        此前 _try_parse_json 遇到第一个 [ 后无条件 break，
        如果第一个 [ 不是 JSON 数组起始（如"搜索了[关键词]"），
        则后续真正的 JSON 数组无法被提取，论文降级为低质量自然语言提取。
        """
        text = (
            "我搜索了[以下关键词]，找到如下论文：\n"
            '[{"arxiv_id": "2403.15337", "title": "Nonlinear optics", "authors": "Wang et al.", "year": "2024", "score": 0.9, "tldr": "非线性光学新进展"}]'
        )
        papers = self.svc._parse_researcher_output(text)
        self.assert_true(len(papers) >= 1, f"应至少解析 1 篇论文（实际 {len(papers)}）")
        if papers:
            # JSON 解析成功时 title 应是完整标题，而非 "(需补充元数据)"
            self.assert_eq(papers[0]["title"], "Nonlinear optics",
                           f"JSON 路径提取到完整标题（实际 title={papers[0]['title']!r}）")

    def _test_pipe_format(self):
        """管道符格式解析。"""
        text = "- 2401.11111 | First Paper | Author A | 2024 | 0.8 | Good paper\n- 2402.22222 | Second Paper | Author B | 2024 | 0.7 | Another paper"
        papers = self.svc._parse_researcher_output(text)
        self.assert_eq(len(papers), 2, "管道符格式解析 2 篇")
        self.assert_eq(papers[0]["arxiv_id"], "2401.11111", "第一篇 arxiv_id")
        self.assert_eq(papers[1]["arxiv_id"], "2402.22222", "第二篇 arxiv_id")

    def _test_natural_language_fallback(self):
        """兜底自然语言提取：只返回 arxiv_id，标记 _needs_metadata。"""
        text = "我找到了一些论文，比如 arXiv:2401.99999 和 2402.88888，但格式不太规范。"
        papers = self.svc._parse_researcher_output(text)
        self.assert_eq(len(papers), 2, "兜底提取 2 个 arxiv_id")
        if papers:
            self.assert_true(papers[0].get("_needs_metadata", False), "兜底条目标记 _needs_metadata")

    def _test_empty_text(self):
        """空文本返回空列表。"""
        papers = self.svc._parse_researcher_output("")
        self.assert_eq(len(papers), 0, "空文本返回空列表")
        papers2 = self.svc._parse_researcher_output("   \n  ")
        self.assert_eq(len(papers2), 0, "纯空白返回空列表")

    def _test_json_empty_array(self):
        """空 JSON 数组返回空列表。"""
        papers = self.svc._parse_researcher_output("[]")
        self.assert_eq(len(papers), 0, "空 JSON 数组返回空列表")

    def run_tests(self):
        self._test_json_array_clean()
        self._test_json_array_with_markdown_fence()
        self._test_json_after_natural_language_bracket()
        self._test_pipe_format()
        self._test_natural_language_fallback()
        self._test_empty_text()
        self._test_json_empty_array()
