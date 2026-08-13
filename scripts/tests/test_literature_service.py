#!/usr/bin/env python3
"""
test_literature_service.py — LiteratureService 解析器单元测试（v6.8.3 修复）

覆盖：
    - _parse_researcher_output JSON 数组解析（主路径）
    - _try_parse_json: 自然语言中含 [ 字符时不阻断后续 JSON 提取
    - _try_parse_pipe_or_table: 管道符 / Markdown 表格格式
    - _try_parse_natural_language: 兜底 arxiv_id 提取
    - _needs_metadata 标记正确
    - kb_text.build_frontmatter 对 list[dict] 不抛 unhashable type
    - _ingest_new_papers 返回 {ingested, failed, skipped} 计数

原则：
    本测试为**纯单元测试**——不调用 LLM API、不发起任何网络请求、不写入
    真实 knowledge/ 数据域，全部在 create_isolated_env() 隔离目录内运行。

历史：
    v6.8.32 移除了原 _test_lit_read_wiki_persistence / _test_link_to_proposal_after_read
    两个用例。根因：literature_service.py 的 WIKI_PAPERS_DIR / RAW_PAPERS_DIR 是
    模块级常量，import 时即绑定真实 knowledge/ 绝对路径，patch_module_root() 无法
    覆盖已绑定常量。这两个用例调用 svc.read() 会发起真实 arxiv 网络请求，并直接
    写入（甚至销毁性覆盖）真实 knowledge/wiki/papers/ 下的深度阅读笔记，违背
    AGENTS.md「测试零污染」与「knowledge 为共享只读域」两条铁律。如需回归
    read()/link_to_proposal() 的端到端链路，应改用注入假 fetcher + monkeypatch
    路径常量的方式，确保隔离。
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

    # ─────────────────────────────────────────────
    # v6.8.20 健康检查回归：kb_text.build_frontmatter 对 list[dict] 元素
    # 抛 unhashable type，导致 _ingest_new_papers 静默失败。
    # ─────────────────────────────────────────────
    def _test_build_frontmatter_string_list_preserves_old_behavior(self):
        """字符串列表（hashable）走原 dedup 路径，输出 ["a","b"] 形式。"""
        from kb_text import build_frontmatter
        text = build_frontmatter({"tags": ["a", "b", "a", "c"]})
        # 旧行为：去重保留顺序 → ["a", "b", "c"]
        self.assert_true('tags: ["a", "b", "c"]' in text,
                         f"字符串列表去重（实际 {text!r}）")

    def _test_build_frontmatter_dict_list_no_unhashable(self):
        """dict 列表（unhashable）不应抛 TypeError；改走 JSON 序列化兜底。

        触发场景：v6.8.20 健康检查（4h 窗口）发现
        `LiteratureService._ingest_new_papers` 把 status_history（List[Dict]）
        传给 `build_frontmatter`，后者 set.add(dict) → unhashable type，
        全部 10 篇论文静默失败，错误日志被 except 吞掉，外层仍报"新入库 10 篇"。
        """
        from kb_text import build_frontmatter
        fm = {
            "title": "Test",
            "status_history": [
                {"status": "pool", "at": "2026-08-10T12:00:00Z", "by": "literature_service"},
                {"status": "reading", "at": "2026-08-11T12:00:00Z", "by": "literature_service"},
            ],
        }
        # 不应抛 TypeError
        text = None
        try:
            text = build_frontmatter(fm)
        except TypeError as e:
            self.assert_true(False, f"build_frontmatter 不应抛 TypeError: {e}")
        # 兜底路径输出合法 JSON 数组，且元素保持顺序
        self.assert_true(text is not None, "build_frontmatter 返回字符串")
        self.assert_true('"status": "pool"' in text, f"首条 status 保留（实际 {text!r}）")
        self.assert_true('"status": "reading"' in text, f"次条 status 保留（实际 {text!r}）")
        # 顺序：pool 必须在 reading 之前
        pool_idx = text.find('"status": "pool"')
        reading_idx = text.find('"status": "reading"')
        self.assert_true(
            0 <= pool_idx < reading_idx,
            f"列表元素保序（pool 在 reading 之前），实际 {text!r}",
        )

    def _test_build_frontmatter_mixed_list_falls_back_to_json(self):
        """含 dict 与可哈希元素的混合列表，走 JSON 兜底（保守行为）。"""
        from kb_text import build_frontmatter
        text = build_frontmatter({"mixed": ["a", {"k": 1}, "b"]})
        self.assert_true('"a"' in text, f"含 dict 时整体 JSON 序列化（实际 {text!r}）")
        self.assert_true('"k": 1' in text, f"dict 元素被保留（实际 {text!r}）")

    def _test_ingest_new_papers_returns_counts(self):
        """_ingest_new_papers 返回 {ingested, failed, skipped} 计数。

        修复前返回 None，外层 executor.py 用 len(new_papers) 虚报入库数。
        """
        papers = [
            {"arxiv_id": "2401.00001", "title": "Paper A", "year": "2024",
             "authors": "X", "score": 0.8, "tldr": "tldr A",
             "is_new": True},
            {"arxiv_id": "2401.00002", "title": "Paper B", "year": "2024",
             "authors": "Y", "score": 0.7, "tldr": "tldr B",
             "is_new": True},
        ]
        result = self.svc._ingest_new_papers(papers, source="pipeline", proposal_id="test-proposal")
        self.assert_true(isinstance(result, dict),
                         f"返回 dict 而非 None（实际 {type(result).__name__}）")
        self.assert_eq(result.get("ingested"), 2,
                       f"2 篇应成功入库（实际 {result}）")
        self.assert_eq(result.get("failed"), 0,
                       f"0 篇失败（实际 {result}）")
        self.assert_eq(result.get("skipped"), 0,
                       f"0 篇跳过（实际 {result}）")

    def _test_ingest_new_papers_handles_unhashable_dict_list(self):
        """v6.8.20 核心回归：_ingest_new_papers 在 status_history 含 dict 时
        不抛 unhashable type，能成功把论文写入 KB。

        注意：本用例写入的是 create_isolated_env() 临时目录下的 RAW_DIR/papers
        （经 patch_module_root 重定向），不触及真实 knowledge/ 数据域。
        """
        papers = [
            {"arxiv_id": "2401.99999", "title": "Regression Test Paper",
             "year": "2024", "authors": "Test Author", "score": 0.85,
             "tldr": "确保 build_frontmatter 不被 dict 列表击穿",
             "is_new": True},
        ]
        # 在修复前会抛 TypeError（unhashable type: 'dict'）并被内部 except 吞掉，
        # 导致 ingested=0 / failed=1；修复后应全部入库。
        result = self.svc._ingest_new_papers(
            papers, source="pipeline", proposal_id="test-proposal-unhashable"
        )
        self.assert_eq(result.get("ingested"), 1,
                       f"含 status_history[dict] 的论文应正常入库（实际 {result}）")
        self.assert_eq(result.get("failed"), 0,
                       f"不应有失败（实际 {result}）")
        # 验证文件确实落盘（隔离目录内）
        raw_dir = self.lit_svc_mod.RAW_DIR / "papers"
        written = list(raw_dir.glob("*2401.99999*.md"))
        self.assert_eq(len(written), 1, f"KB 中应找到 1 个文件（实际 {len(written)}）")
        if written:
            content = written[0].read_text(encoding="utf-8")
            self.assert_true('"status": "pool"' in content,
                             f"status_history 字段已写入文件（实际 {content[:300]!r}）")

    def run_tests(self):
        self._test_json_array_clean()
        self._test_json_array_with_markdown_fence()
        self._test_json_after_natural_language_bracket()
        self._test_pipe_format()
        self._test_natural_language_fallback()
        self._test_empty_text()
        self._test_json_empty_array()
        self._test_build_frontmatter_string_list_preserves_old_behavior()
        self._test_build_frontmatter_dict_list_no_unhashable()
        self._test_build_frontmatter_mixed_list_falls_back_to_json()
        self._test_ingest_new_papers_returns_counts()
        self._test_ingest_new_papers_handles_unhashable_dict_list()
