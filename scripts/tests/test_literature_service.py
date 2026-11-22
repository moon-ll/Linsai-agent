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

    def _test_ingest_doi_paper_without_arxiv_id(self):
        """v6.8.43 核心回归：无 arXiv ID 的期刊论文（OpenAlex/Crossref 来源）
        以 DOI 为标识也能入库，不再被静默丢弃。

        触发场景：多源学术检索引入 OpenAlex 期刊论文，无 arxiv_id，
        原实现 `if not arxiv_id: continue` 直接跳过，期刊文献进不了知识库。
        """
        papers = [
            {"doi": "10.1038/s41567-018-0315-5",
             "title": "Solid-state high harmonic generation in crystals",
             "year": "2019", "authors": "Ghimire & Reis",
             "score": 0.88, "tldr": "晶体高次谐波综述",
             "source": "openalex", "is_new": True},
        ]
        result = self.svc._ingest_new_papers(
            papers, source="pipeline", proposal_id="test-proposal-doi"
        )
        self.assert_eq(result.get("ingested"), 1,
                       f"DOI 期刊论文应入库（实际 {result}）")
        self.assert_eq(result.get("failed"), 0,
                       f"不应有失败（实际 {result}）")
        raw_dir = self.lit_svc_mod.RAW_DIR / "papers"
        written = list(raw_dir.glob("*doi-10-1038-s41567-018-0315-5*.md"))
        self.assert_eq(len(written), 1,
                       f"按 DOI 命名的文件应落盘（实际 {len(written)}）")
        if written:
            content = written[0].read_text(encoding="utf-8")
            self.assert_true("doi" in content,
                             f"frontmatter 应含 doi 字段（实际 {content[:300]!r}）")
            self.assert_true("10.1038/s41567-018-0315-5" in content,
                             f"DOI 值应写入（实际 {content[:300]!r}）")
            self.assert_true("s41567-018-0315-5" in content,
                             f"DOI 链接应写入正文（实际 {content[:300]!r}）")

    def _test_ingest_paper_with_neither_id(self):
        """既无 arXiv ID 也无 DOI 的论文应跳过，不污染知识库。"""
        papers = [
            {"title": "No identifier paper", "year": "2024",
             "authors": "X", "score": 0.5, "is_new": True},
        ]
        result = self.svc._ingest_new_papers(
            papers, source="pipeline", proposal_id="test-proposal-none"
        )
        self.assert_eq(result.get("ingested"), 0,
                       f"无标识论文不能入库（实际 {result}）")
        self.assert_eq(result.get("skipped"), 0,
                       f"无标识论文应直接 continue 不计数（实际 {result}）")

    def _test_ingest_doi_stuffed_in_arxiv_id_field(self):
        """v6.9.47 核心回归：researcher 把期刊 DOI 塞进 arxiv_id 字段时，
        不再因 identifier 含 "/" 导致 raw/papers 写入 ENOENT。

        触发场景（08-24 11:06 attosecond r2 lit_search 实证）：中文期刊
        论文无 arXiv 预印本，researcher agent 返回
        {"arxiv_id": "10.1088/1674-1056/ae3474", ...}——旧实现该形态绕过
        arxiv 校验（_extract_arxiv_id 兜底原样返回）与 DOI 清洗，slug 保留
        "/" 使 write_text 抛 [Errno 2]，10 篇论文丢 8 篇（failed=8）且
        lit_read/lit_note 后续全部空转。修复后归一化移入 doi_clean。
        """
        papers = [
            {"arxiv_id": "10.1088/1674-1056/ae3474",
             "title": "Autocorrelation-based CNN for noisy attosecond streaking traces",
             "year": "2026", "authors": "Zhu et al.",
             "score": 0.9, "tldr": "CNN 反演阿秒条纹轨迹", "is_new": True},
        ]
        result = self.svc._ingest_new_papers(
            papers, source="pipeline", proposal_id="test-proposal-doi-in-arxiv"
        )
        self.assert_eq(result.get("ingested"), 1,
                       f"DOI-in-arxiv_id 论文应入库（实际 {result}）")
        self.assert_eq(result.get("failed"), 0,
                       f"不应有失败（实际 {result}）")
        raw_dir = self.lit_svc_mod.RAW_DIR / "papers"
        written = list(raw_dir.glob("*doi-10-1088-1674-1056-ae3474*.md"))
        self.assert_eq(len(written), 1,
                       f"按 DOI slug 命名（无斜杠）的文件应落盘（实际 {len(written)}）")
        if written:
            content = written[0].read_text(encoding="utf-8")
            self.assert_true("10.1088/1674-1056/ae3474" in content,
                             f"DOI 值应写入文件（实际 {content[:300]!r}）")

    def _test_link_to_proposal_preserves_frontmatter_and_body(self):
        """v7.3.6 核心回归：link_to_proposal 不得清空 frontmatter 与正文。

        触发场景（11-03 16h 健康检查实证）：executor 对抗评审路径调用
        link_to_proposal() 关联论文到课题。旧实现取 existing.get("meta", {})
        与 existing.get("content", "")，而 get_wiki_page 实际返回键为
        "frontmatter"/"body" → 恒取空值。回写时 kw_build 用默认模板重建整页：
        created 被重置为当前时间、source_raw 被清空、tags/growth_stage/
        confidence 全部退化为默认值、正文被清空。

        实测影响（11-03 12:55 批量）：wiki/papers 158 个页面 working tree
        被改写，其中 13 页 source_raw 变空 → 蒸馏覆盖率 100%→95.4%、
        missing_notes 0→98，溯源链断裂；且 created 重置使 #12 研究趋势雷达
        的 mtime/created 双口径判据失效。
        """
        import kb_wiki
        from kb_text import parse_frontmatter

        # 隔离 wiki 目录（门面 save_wiki_page 走 KNOWLEDGE_DIR）
        tmp_kb = self.tmp_root / "knowledge"
        wiki_papers = tmp_kb / "wiki" / "papers"
        wiki_papers.mkdir(parents=True, exist_ok=True)
        page = wiki_papers / "2609.20990.md"
        orig_fm = {
            "title": "Singular high-harmonic transport above a quantum threshold",
            "type": "papers",
            "created": "2026-09-21T15:00:37Z",
            "updated": "2026-11-01T04:55:12Z",
            "tags": ["deepxiv-论文库", "深度解析"],
            "source_raw": "papers/2026-2609.20990-x.md",
            "growth_stage": "growing",
            "confidence": 0.8,
            "read_status": "deep-read",
            "used_by_proposals": [],
        }
        orig_body = "# BODY 原文\n\n这是深读笔记正文，不应被清空。\n"
        page.write_text(
            "---\n" + "\n".join(f'{k}: {v!r}' for k, v in orig_fm.items()) + "\n---\n\n" + orig_body,
            encoding="utf-8",
        )

        old_kd = kb_wiki.KNOWLEDGE_DIR
        old_wd = kb_wiki.WIKI_DIR
        old_wpc = self.lit_svc_mod.WIKI_PAPERS_DIR
        try:
            kb_wiki.KNOWLEDGE_DIR = tmp_kb
            kb_wiki.WIKI_DIR = tmp_kb / "wiki"
            self.lit_svc_mod.WIKI_PAPERS_DIR = wiki_papers

            ok = self.svc.link_to_proposal(
                "2609.20990", "general-ssh-weyl-20260920",
                citation_location="adversarial-review",
            )
            self.assert_true(ok, "link_to_proposal 应返回 True")

            after = page.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(after)

            self.assert_eq(fm.get("created"), orig_fm["created"],
                           f"created 不得被重置（实际 {fm.get('created')!r}）")
            self.assert_eq(fm.get("source_raw"), orig_fm["source_raw"],
                           f"source_raw 不得被清空（实际 {fm.get('source_raw')!r}）")
            self.assert_eq(fm.get("tags"), orig_fm["tags"],
                           f"tags 不得丢失（实际 {fm.get('tags')!r}）")
            self.assert_eq(fm.get("growth_stage"), orig_fm["growth_stage"],
                           f"growth_stage 不得退化（实际 {fm.get('growth_stage')!r}）")
            self.assert_eq(fm.get("read_status"), "deep-read",
                           f"read_status 不得丢失（实际 {fm.get('read_status')!r}）")
            self.assert_eq(fm.get("title"), orig_fm["title"],
                           f"title 不得退化为裸 arXiv ID（实际 {fm.get('title')!r}）")
            self.assert_true(
                "general-ssh-weyl-20260920" in (fm.get("used_by_proposals") or []),
                f"used_by_proposals 应追加课题 ID（实际 {fm.get('used_by_proposals')!r}）",
            )
            self.assert_true("这是深读笔记正文，不应被清空。" in body,
                             f"正文不得被清空（实际 body 长度 {len(body)}）")
        finally:
            kb_wiki.KNOWLEDGE_DIR = old_kd
            kb_wiki.WIKI_DIR = old_wd
            self.lit_svc_mod.WIKI_PAPERS_DIR = old_wpc

    def _test_read_cache_hit_reads_frontmatter_read_status(self):
        """v7.3.6 回归：read() 缓存命中判定须读 frontmatter.read_status。

        旧实现取 existing_note.get("read_status")（顶层），实际该字段位于
        frontmatter 内 → 恒为 "unread" → 已深读论文被误判未读并重复派发
        深度阅读（浪费 hermes 调用 + 覆盖既有笔记）。
        """
        import kb_wiki

        tmp_kb = self.tmp_root / "knowledge_read"
        wiki_papers = tmp_kb / "wiki" / "papers"
        wiki_papers.mkdir(parents=True, exist_ok=True)
        (wiki_papers / "2506.14665.md").write_text(
            '---\ntitle: "Deep read paper"\ntype: "papers"\n'
            'read_status: "deep-read"\ncreated: "2026-09-01T00:00:00Z"\n---\n\n'
            "# 已深读正文\n",
            encoding="utf-8",
        )

        old_kd = kb_wiki.KNOWLEDGE_DIR
        old_wd = kb_wiki.WIKI_DIR
        old_wpc = self.lit_svc_mod.WIKI_PAPERS_DIR
        try:
            kb_wiki.KNOWLEDGE_DIR = tmp_kb
            kb_wiki.WIKI_DIR = tmp_kb / "wiki"
            self.lit_svc_mod.WIKI_PAPERS_DIR = wiki_papers

            res = self.svc.read("2506.14665", proposal_id=None)
            self.assert_eq(res.get("cached"), True,
                           f"已深读论文应命中缓存（实际 {res.get('cached')!r}）")
            self.assert_eq(res.get("read_status"), "deep-read",
                           f"read_status 应为 deep-read（实际 {res.get('read_status')!r}）")
            self.assert_true("已深读正文" in (res.get("content") or ""),
                             f"缓存命中应返回既有正文（实际 {res.get('content')!r}）")
        finally:
            kb_wiki.KNOWLEDGE_DIR = old_kd
            kb_wiki.WIKI_DIR = old_wd
            self.lit_svc_mod.WIKI_PAPERS_DIR = old_wpc

    def _test_link_to_proposal_normalizes_string_citations(self):
        """v7.3.6 回归：proposals_citations 为字符串形态时不得抛 AttributeError。

        触发场景（11-03 19:55 生产实证）：kb_text.build_frontmatter 对 dict 值
        走 else 分支做 str() 序列化 → proposals_citations 被写成
        "{'pid': ['adversarial-review']}"；parse_frontmatter 不反解 → 取回是 str。
        link_to_proposal 旧实现只判 isinstance(citations, list) 不判 str →
        citations.get(...) 抛 AttributeError: 'str' object has no attribute
        'get' → lit_note 步骤整体失败，attempts 打满 3 终态卡死
        （berry r2 content-lit_note 实测）。

        修复：_normalize_citations 把 str 形态经 ast.literal_eval 归一为 dict。
        """
        import kb_wiki
        from kb_text import parse_frontmatter

        tmp_kb = self.tmp_root / "knowledge_cite"
        wiki_papers = tmp_kb / "wiki" / "papers"
        wiki_papers.mkdir(parents=True, exist_ok=True)
        page = wiki_papers / "2605.20067.md"
        # 复刻生产现场的字符串形态 frontmatter
        page.write_text(
            '---\ntitle: "2605.20067"\ntype: "papers"\n'
            'created: "2026-10-05T12:30:59Z"\n'
            'updated: "2026-10-05T18:55:02Z"\n'
            'tags: []\nsource_raw: ""\ngrowth_stage: "seedling"\n'
            'confidence: 0.5\narxiv_id: "2605.20067"\n'
            'used_by_proposals: ["general-quantum-geometry-inversion-20260726"]\n'
            'proposals_citations: "{\'general-quantum-geometry-inversion-20260726\': '
            '[\'adversarial-review\']}"\n---\n\n# 正文\n',
            encoding="utf-8",
        )

        old_kd = kb_wiki.KNOWLEDGE_DIR
        old_wd = kb_wiki.WIKI_DIR
        old_wpc = self.lit_svc_mod.WIKI_PAPERS_DIR
        try:
            kb_wiki.KNOWLEDGE_DIR = tmp_kb
            kb_wiki.WIKI_DIR = tmp_kb / "wiki"
            self.lit_svc_mod.WIKI_PAPERS_DIR = wiki_papers

            ok = self.svc.link_to_proposal(
                "2605.20067", "general-berry-mnps3-rashba-20260816",
                citation_location="adversarial-review",
            )
            self.assert_true(ok, "字符串 citations 形态不得导致 link_to_proposal 失败")

            fm, _body = parse_frontmatter(page.read_text(encoding="utf-8"))
            used_by = fm.get("used_by_proposals") or []
            self.assert_true("general-berry-mnps3-rashba-20260816" in used_by,
                             f"新课题应追加到 used_by_proposals（实际 {used_by!r}）")
            self.assert_true("general-quantum-geometry-inversion-20260726" in used_by,
                             f"原课题引用不得丢失（实际 {used_by!r}）")
            # 字符串形态归一后，两条课题的 citation 都应保留
            cites = fm.get("proposals_citations")
            self.assert_true(isinstance(cites, str),
                             f"写回仍是字符串形态（frontmatter 序列化所致，实际 {cites!r}）")
            self.assert_true("general-berry-mnps3-rashba-20260816" in cites,
                             f"新课题 citation 应保留（实际 {cites!r}）")
            self.assert_true("general-quantum-geometry-inversion-20260726" in cites,
                             f"原课题 citation 不得丢失（实际 {cites!r}）")
        finally:
            kb_wiki.KNOWLEDGE_DIR = old_kd
            kb_wiki.WIKI_DIR = old_wd
            self.lit_svc_mod.WIKI_PAPERS_DIR = old_wpc

    def _test_normalize_citations_shapes(self):
        """v7.3.6 单元：_normalize_citations 对各形态的归一行为。"""
        norm = self.lit_svc_mod._normalize_citations
        self.assert_eq(norm({"a": ["x"]}), {"a": ["x"]}, "dict 原样返回")
        self.assert_eq(norm("{'a': ['x']}"), {"a": ["x"]}, "str 经 literal_eval 还原")
        self.assert_eq(norm("not a dict"), {}, "不可解析的 str 归为空 dict")
        self.assert_eq(norm(None), {}, "None 归为空 dict")
        self.assert_eq(norm(["a"]), {}, "list 归为空 dict")
        self.assert_eq(norm(123), {}, "其它类型归为空 dict")

    def _test_normalize_citations_shapes(self):
        """v7.3.6 单元：_normalize_citations 对各形态的归一行为。"""
        norm = self.lit_svc_mod._normalize_citations
        self.assert_eq(norm({"a": ["x"]}), {"a": ["x"]}, "dict 原样返回")
        self.assert_eq(norm("{'a': ['x']}"), {"a": ["x"]}, "str 经 literal_eval 还原")
        self.assert_eq(norm("not a dict"), {}, "不可解析的 str 归为空 dict")
        self.assert_eq(norm(None), {}, "None 归为空 dict")
        self.assert_eq(norm(["a"]), {}, "list 归为空 dict")
        self.assert_eq(norm(123), {}, "其它类型归为空 dict")

    def _test_wiki_paper_candidates_naming_generations(self):
        """v7.3.12（BUG-38）单元：_wiki_paper_candidates 覆盖多代命名。

        wiki/papers/ 实际存在 4 代命名并存（裸 id 代 / 下划线 slug 代 /
        点号 slug 代 / 裸 id+slug 代）。旧实现只认裸 id 代 → 下划线 slug 代
        的论文判「页面不存在」。
        """
        import kb_wiki

        tmp_kb = self.tmp_root / "knowledge_cand"
        wiki_papers = tmp_kb / "wiki" / "papers"
        wiki_papers.mkdir(parents=True, exist_ok=True)
        for name in [
            "2407.15253.md",
            "2024-2407_15253-keldysh-tuning.md",
            "2024-2407.15253-dot-variant.md",
            "2503.11432-attosecond-review.md",
        ]:
            (wiki_papers / name).write_text(
                f'---\ntitle: "{name}"\ntype: "papers"\n---\n\n正文\n',
                encoding="utf-8",
            )

        old_kd = kb_wiki.KNOWLEDGE_DIR
        old_wd = kb_wiki.WIKI_DIR
        old_wpc = self.lit_svc_mod.WIKI_PAPERS_DIR
        try:
            kb_wiki.KNOWLEDGE_DIR = tmp_kb
            kb_wiki.WIKI_DIR = tmp_kb / "wiki"
            self.lit_svc_mod.WIKI_PAPERS_DIR = wiki_papers

            cands = self.lit_svc_mod._wiki_paper_candidates("2407.15253")
            names = [p.name for p in cands]
            self.assert_true("2407.15253.md" in names,
                             f"裸 id 代应命中（实际 {names}）")
            self.assert_true("2024-2407_15253-keldysh-tuning.md" in names,
                             f"下划线 slug 代应命中（实际 {names}）")
            self.assert_true("2024-2407.15253-dot-variant.md" in names,
                             f"点号 slug 代应命中（实际 {names}）")
            self.assert_eq(names[0], "2407.15253.md",
                           "裸 id 代应排首位（link_to_proposal 的写回目标）")

            cands2 = self.lit_svc_mod._wiki_paper_candidates("2503.11432")
            self.assert_true(
                "2503.11432-attosecond-review.md" in [p.name for p in cands2],
                f"裸 id+slug 代应命中（实际 {[p.name for p in cands2]}）",
            )

            # 不存在的 id → 空列表
            self.assert_eq(self.lit_svc_mod._wiki_paper_candidates("9999.99999"), [],
                           "不存在的 id 应返回空列表")
        finally:
            kb_wiki.KNOWLEDGE_DIR = old_kd
            kb_wiki.WIKI_DIR = old_wd
            self.lit_svc_mod.WIKI_PAPERS_DIR = old_wpc

    def _test_link_to_proposal_finds_underscore_slug_page(self):
        """v7.3.12（BUG-38）回归：论文页仅以下划线 slug 代命名时须能关联。

        触发场景（11-04 02:46 生产实证）：houston r2 lit_note 批量关联 34 篇，
        其中 5 篇（2503.02469 / 2402.15375 / 2411.06509 / 2503.14360 /
        1502.07183）在 KB 中确实存在（仅下划线 slug 代），却全部报
        「论文 wiki 页面不存在」→ link_to_proposal 返回 False →
        used_by_proposals / proposals_citations 永不落盘，论文与课题的
        引用关系在知识库中断链。

        旧实现只查 `WIKI_PAPERS_DIR / f"{arxiv_id}.md"`，命中不了 slug 代。
        """
        import kb_wiki
        from kb_text import parse_frontmatter

        tmp_kb = self.tmp_root / "knowledge_bug38"
        wiki_papers = tmp_kb / "wiki" / "papers"
        wiki_papers.mkdir(parents=True, exist_ok=True)
        slug_page = wiki_papers / "2025-2503_02469-theory-of-photocurrent.md"
        slug_page.write_text(
            '---\ntitle: "Theory of Photocurrent and HHG"\ntype: "papers"\n'
            'created: "2026-08-29T05:09:27Z"\nupdated: "2026-08-29T05:09:27Z"\n'
            'tags: ["literature"]\nsource_raw: "2025-2503.02469-theory.md"\n'
            'growth_stage: "mature"\nconfidence: 0.8\n'
            'used_by_proposals: ["general-moire-strong-field-probe-20260726"]\n'
            'arxiv_id: "2503.02469"\n---\n\n# 林赛的理解\n\n这是一段实质的深读笔记正文。\n',
            encoding="utf-8",
        )

        old_kd = kb_wiki.KNOWLEDGE_DIR
        old_wd = kb_wiki.WIKI_DIR
        old_wpc = self.lit_svc_mod.WIKI_PAPERS_DIR
        try:
            kb_wiki.KNOWLEDGE_DIR = tmp_kb
            kb_wiki.WIKI_DIR = tmp_kb / "wiki"
            self.lit_svc_mod.WIKI_PAPERS_DIR = wiki_papers

            ok = self.svc.link_to_proposal(
                "2503.02469", "general-houston-kronig-penney-landau-zener-20261004",
                citation_location="adversarial-review",
            )
            self.assert_true(ok, "下划线 slug 代论文页应能关联成功")

            fm, body = parse_frontmatter(slug_page.read_text(encoding="utf-8"))
            used_by = fm.get("used_by_proposals") or []
            self.assert_true(
                "general-houston-kronig-penney-landau-zener-20261004" in used_by,
                f"新课题应追加到 used_by_proposals（实际 {used_by!r}）",
            )
            self.assert_true(
                "general-moire-strong-field-probe-20260726" in used_by,
                f"原课题引用不得丢失（实际 {used_by!r}）",
            )
            self.assert_eq(fm.get("created"), "2026-08-29T05:09:27Z",
                           "created 不得被重置")
            self.assert_eq(fm.get("source_raw"), "2025-2503.02469-theory.md",
                           "source_raw 不得被清空")
            self.assert_true("林赛的理解" in body,
                             f"正文不得被清空（实际 body 长度 {len(body)}）")

            # 关键：不得在裸 id 名下新建重复页
            self.assert_true(not (wiki_papers / "2503.02469.md").exists(),
                             "不得在裸 id 名下新建重复页面")
        finally:
            kb_wiki.KNOWLEDGE_DIR = old_kd
            kb_wiki.WIKI_DIR = old_wd
            self.lit_svc_mod.WIKI_PAPERS_DIR = old_wpc

    def _test_read_cache_hit_resolves_underscore_slug_page(self):
        """v7.3.12（BUG-38）回归：read() 缓存命中须解析 slug 代并回写关联。

        下划线 slug 代页面的 read_status 位于 frontmatter 内；若解析不到，
        已深读论文被误判为「未读」→ 重复派发深度阅读（浪费 hermes 调用）
        且 used_by_proposals 永不落盘。
        """
        import kb_wiki
        from kb_text import parse_frontmatter

        tmp_kb = self.tmp_root / "knowledge_bug38_read"
        wiki_papers = tmp_kb / "wiki" / "papers"
        wiki_papers.mkdir(parents=True, exist_ok=True)
        slug_page = wiki_papers / "2024-2407_15253-keldysh-tuning.md"
        slug_page.write_text(
            '---\ntitle: "Keldysh tuning"\ntype: "papers"\n'
            'read_status: "deep-read"\ncreated: "2026-08-29T05:09:27Z"\n'
            'arxiv_id: "2407.15253"\n---\n\n# 已深读正文\n\n实质内容。\n',
            encoding="utf-8",
        )

        old_kd = kb_wiki.KNOWLEDGE_DIR
        old_wd = kb_wiki.WIKI_DIR
        old_wpc = self.lit_svc_mod.WIKI_PAPERS_DIR
        try:
            kb_wiki.KNOWLEDGE_DIR = tmp_kb
            kb_wiki.WIKI_DIR = tmp_kb / "wiki"
            self.lit_svc_mod.WIKI_PAPERS_DIR = wiki_papers

            res = self.svc.read("2407.15253", proposal_id=None)
            self.assert_eq(res.get("cached"), True,
                           f"下划线 slug 代已深读页应命中缓存（实际 {res.get('cached')!r}）")
            self.assert_eq(res.get("read_status"), "deep-read",
                           f"read_status 应为 deep-read（实际 {res.get('read_status')!r}）")
            self.assert_true("已深读正文" in (res.get("content") or ""),
                             f"缓存命中应返回既有正文（实际 {res.get('content')!r}）")

            # 带 proposal_id 时，关联须回写到 slug 代页面（而非新建裸 id 页）
            res2 = self.svc.read(
                "2407.15253", proposal_id="general-bsv-driven-hhg-quantum-20260726"
            )
            self.assert_eq(res2.get("cached"), True, "再次读应仍命中缓存")
            fm, _ = parse_frontmatter(slug_page.read_text(encoding="utf-8"))
            used_by = fm.get("used_by_proposals") or []
            self.assert_true(
                "general-bsv-driven-hhg-quantum-20260726" in used_by,
                f"关联课题应回写到 slug 代页面（实际 {used_by!r}）",
            )
            self.assert_true(not (wiki_papers / "2407.15253.md").exists(),
                             "不得在裸 id 名下新建重复页面")
        finally:
            kb_wiki.KNOWLEDGE_DIR = old_kd
            kb_wiki.WIKI_DIR = old_wd
            self.lit_svc_mod.WIKI_PAPERS_DIR = old_wpc

    def _test_wiki_paper_candidates_flat_id_generation(self):
        """v7.3.13（BUG-39）单元：_wiki_paper_candidates 覆盖「去点 slug 代」。

        wiki/papers/ 存在第五代命名：id 的 `.` 被**整体删除**而非替换为 `_`
        （`2407.03189` → `240703189`），文件名为 `2024-240703189-<slug>.md`。
        v7.3.12 的 4 个 pattern（裸 id / 下划线 / 点号 / 裸 id 前缀）
        全部匹配不到该形态 → 这 59 篇论文对 literature_service 依旧不可达。

        实测全库：59 篇去点 slug 代中 25 篇无裸 id 对应页（无法靠回退裸 id
        救回），其中 14 篇是真实主内容页。
        """
        import kb_wiki

        tmp_kb = self.tmp_root / "knowledge_cand_flat"
        wiki_papers = tmp_kb / "wiki" / "papers"
        wiki_papers.mkdir(parents=True, exist_ok=True)
        for name in [
            "2024-240703189-origin-of-anomalous-magnetotransport.md",
            "2025-251011666-leaky-wave-antennas.md",
        ]:
            (wiki_papers / name).write_text(
                f'---\ntitle: "{name}"\ntype: "papers"\n---\n\n正文\n',
                encoding="utf-8",
            )

        old_kd = kb_wiki.KNOWLEDGE_DIR
        old_wd = kb_wiki.WIKI_DIR
        old_wpc = self.lit_svc_mod.WIKI_PAPERS_DIR
        try:
            kb_wiki.KNOWLEDGE_DIR = tmp_kb
            kb_wiki.WIKI_DIR = tmp_kb / "wiki"
            self.lit_svc_mod.WIKI_PAPERS_DIR = wiki_papers

            names = [
                p.name for p in self.lit_svc_mod._wiki_paper_candidates("2407.03189")
            ]
            self.assert_true(
                "2024-240703189-origin-of-anomalous-magnetotransport.md" in names,
                f"去点 slug 代应命中（实际 {names}）",
            )
            names2 = [
                p.name for p in self.lit_svc_mod._wiki_paper_candidates("2510.11666")
            ]
            self.assert_true(
                "2025-251011666-leaky-wave-antennas.md" in names2,
                f"去点 slug 代应命中（实际 {names2}）",
            )
        finally:
            kb_wiki.KNOWLEDGE_DIR = old_kd
            kb_wiki.WIKI_DIR = old_wd
            self.lit_svc_mod.WIKI_PAPERS_DIR = old_wpc

    def _test_link_to_proposal_finds_flat_id_slug_page(self):
        """v7.3.13（BUG-39）回归：去点 slug 代论文页须能关联成功。

        触发场景：论文页仅以「去点 slug 代」命名（`2024-240703189-*.md`），
        `link_to_proposal("2407.03189", ...)` 旧实现 4 个 pattern 全落空
        → 返回 False → used_by_proposals 永不落盘 → 引用关系断链。
        """
        import kb_wiki
        from kb_text import parse_frontmatter

        tmp_kb = self.tmp_root / "knowledge_bug39"
        wiki_papers = tmp_kb / "wiki" / "papers"
        wiki_papers.mkdir(parents=True, exist_ok=True)
        slug_page = wiki_papers / "2024-240703189-origin-of-anomalous-magnetotransport.md"
        slug_page.write_text(
            '---\ntitle: "去点 slug 代论文"\ntype: "papers"\n'
            'arxiv_id: "2407.03189"\nread_status: "deep-read"\n'
            "used_by_proposals: []\n---\n\n已深读正文\n",
            encoding="utf-8",
        )

        old_kd = kb_wiki.KNOWLEDGE_DIR
        old_wd = kb_wiki.WIKI_DIR
        old_wpc = self.lit_svc_mod.WIKI_PAPERS_DIR
        try:
            kb_wiki.KNOWLEDGE_DIR = tmp_kb
            kb_wiki.WIKI_DIR = tmp_kb / "wiki"
            self.lit_svc_mod.WIKI_PAPERS_DIR = wiki_papers

            ok = self.svc.link_to_proposal(
                "2407.03189", "general-bsv-driven-hhg-quantum-20260726"
            )
            self.assert_eq(ok, True, "去点 slug 代论文页应能关联成功")
            fm, _ = parse_frontmatter(slug_page.read_text(encoding="utf-8"))
            used_by = fm.get("used_by_proposals") or []
            self.assert_true(
                "general-bsv-driven-hhg-quantum-20260726" in used_by,
                f"关联课题应回写到去点 slug 代页面（实际 {used_by!r}）",
            )
            self.assert_true(not (wiki_papers / "2407.03189.md").exists(),
                             "不得在裸 id 名下新建重复页面")
        finally:
            kb_wiki.KNOWLEDGE_DIR = old_kd
            kb_wiki.WIKI_DIR = old_wd
            self.lit_svc_mod.WIKI_PAPERS_DIR = old_wpc

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
        self._test_ingest_doi_paper_without_arxiv_id()
        self._test_ingest_paper_with_neither_id()
        self._test_ingest_doi_stuffed_in_arxiv_id_field()
        self._test_link_to_proposal_preserves_frontmatter_and_body()
        self._test_read_cache_hit_reads_frontmatter_read_status()
        self._test_link_to_proposal_normalizes_string_citations()
        self._test_normalize_citations_shapes()
        self._test_wiki_paper_candidates_naming_generations()
        self._test_link_to_proposal_finds_underscore_slug_page()
        self._test_read_cache_hit_resolves_underscore_slug_page()
        self._test_wiki_paper_candidates_flat_id_generation()
        self._test_link_to_proposal_finds_flat_id_slug_page()
