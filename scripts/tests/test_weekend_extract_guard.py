#!/usr/bin/env python3
"""
test_weekend_extract_guard.py — 周末输出萃取缺键守卫回归测试（v6.9.79）

背景：2026-08-29 14:40 BJ output_extract_daily_knowledge 终态失败于
KeyError('title')——LLM 返回的 concepts/papers 条目缺 title 键（people
缺 name 同型），weekend_pipeline/output_jobs.py 与 knowledge_output.py
均裸取 item["title"]，单条缺键拖垮整批萃取，weekly_report 依赖链阻塞。

覆盖：
    1. weekend_pipeline._extract_daily_knowledge：缺键/非 dict/空串条目
       跳过并计数，有效条目正常写入
    2. knowledge_output.process_daily_sources：同型守卫（CLI --daily 路径）
    3. _item_title 助手边界（None/字符串/空串/带空白）

注意：本测试不调用 LLM、零文件系统副作用（全部 stub）。
"""

import sys
import types
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


_BAD_PAYLOAD = {
    "concepts": [
        {"summary": "缺 title 的概念", "source_path": "knowledge/wiki/reviews/briefing-x.md"},
        {"title": "  有效概念  ", "summary": "s", "source_path": "knowledge/wiki/reviews/briefing-x.md"},
        "not-a-dict",
    ],
    "methods": [
        {"title": "", "summary": "空 title", "source_path": "knowledge/wiki/reviews/briefing-x.md"},
        {"title": "有效方法", "summary": "s", "source_path": "knowledge/wiki/reviews/briefing-x.md"},
    ],
    "people": [
        {"affiliation": "缺 name", "source_path": "knowledge/wiki/reviews/briefing-x.md"},
        {"name": "有效学者", "affiliation": "a", "source_path": "knowledge/wiki/reviews/briefing-x.md"},
    ],
    "papers": [
        {"authors": "缺 title 的论文", "source_path": "knowledge/wiki/reviews/briefing-x.md"},
        {"title": "有效论文", "authors": "a", "source_path": "knowledge/wiki/reviews/briefing-x.md"},
    ],
    "unverified_claims": [],
}
# 无效条目：concepts 2（缺键 + 非 dict）+ methods 1（空串）+ people 1 + papers 1 = 5
_EXPECTED_SKIPPED = 5
_EXPECTED_WRITTEN = 4

_FAKE_SOURCES = {
    "sources": [
        {"type": "briefing", "path": "knowledge/wiki/reviews/briefing-x.md", "text": "正文"},
    ]
}


class WeekendExtractGuardTests(TestSuite):
    def __init__(self):
        super().__init__("周末输出萃取缺键守卫测试（v6.9.79）")

    # ------------------------------------------------------------------
    # 4. _write_wiki_page sources 读侧归一（同页第二次命中不再 TypeError）
    # ------------------------------------------------------------------

    def _test_write_page_sources_normalize(self):
        import tempfile
        import weekend_pipeline.output_jobs as oj

        tmp = Path(tempfile.mkdtemp(prefix="linsai_extract_guard_"))
        orig_consts = {
            "PROJECT_ROOT": oj.PROJECT_ROOT,
            "KB_ROOT": oj.KB_ROOT, "KB_CONCEPTS_DIR": oj.KB_CONCEPTS_DIR,
            "KB_METHODS_DIR": oj.KB_METHODS_DIR, "KB_PEOPLE_DIR": oj.KB_PEOPLE_DIR,
            "KB_PAPERS_DIR": oj.KB_PAPERS_DIR, "KB_REVIEWS_DIR": oj.KB_REVIEWS_DIR,
        }
        orig_kb_mod = sys.modules.get("knowledge_base")
        try:
            kb_root = tmp / "knowledge" / "wiki"
            for name in orig_consts:
                setattr(oj, name, tmp if name == "PROJECT_ROOT" else kb_root / name.replace("KB_", "").replace("_DIR", "").lower())
            oj.KB_ROOT = kb_root
            # facade 注入失败（sys.modules 置 None → ImportError）→ 走 fallback 直写
            sys.modules["knowledge_base"] = None

            src = [{"title": "s1", "source_type": "briefing"}]
            r1 = oj._write_wiki_page("concept", "归一测试概念", "第一段", src, oj.RELIABILITY_RELIABLE)
            self.assert_true(r1.get("success") is True, "首次写入建页成功", f"r1={r1}")

            # 第二次命中同页：朴素 frontmatter 解析下 sources 为空串，
            # 修复前 str + list 抛 TypeError（16:35 BJ 实证）
            r2 = oj._write_wiki_page("concept", "归一测试概念", "第二段", src, oj.RELIABILITY_RELIABLE)
            self.assert_true(r2.get("success") is True, "同页第二次追加不再 TypeError", f"r2={r2}")

            page = (kb_root / "concepts" / "归一测试概念.md")
            if not page.exists():
                # safe_filename 可能对中文做转写，兜底找目录内唯一文件
                cands = list((kb_root / "concepts").glob("*.md"))
                page = cands[0] if cands else page
            text = page.read_text(encoding="utf-8") if page.exists() else ""
            self.assert_true("第一段" in text and "第二段" in text, "两次正文均保留", f"len={len(text)}")
        except Exception as e:
            self.assert_true(False, "sources 归一测试异常", f"{type(e).__name__}: {e}")
        finally:
            for k, v in orig_consts.items():
                setattr(oj, k, v)
            if orig_kb_mod is not None:
                sys.modules["knowledge_base"] = orig_kb_mod
            else:
                sys.modules.pop("knowledge_base", None)
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def run_tests(self):
        self._test_output_jobs_guard()
        self._test_knowledge_output_guard()
        self._test_helper_edges()
        self._test_write_page_sources_normalize()

    # ------------------------------------------------------------------
    # 1. weekend_pipeline._extract_daily_knowledge（cron 实际失败路径）
    # ------------------------------------------------------------------

    def _test_output_jobs_guard(self):
        import weekend_pipeline.output_jobs as oj

        written = []
        saved = {}
        orig = {
            "load_json": oj.load_json,
            "is_llm_available": oj.is_llm_available,
            "_llm_json": oj._llm_json,
            "_write_wiki_page": oj._write_wiki_page,
            "save_json": oj.save_json,
        }
        orig_kb = sys.modules.get("knowledge_base")

        try:
            oj.load_json = lambda path, default=None: dict(_FAKE_SOURCES)
            oj.is_llm_available = lambda: True
            oj._llm_json = lambda system, user, timeout=120: dict(_BAD_PAYLOAD)

            def _fake_write(kind, title, body, sources, reliability):
                written.append((kind, title))
                return {"success": True, "path": f"{kind}/{title}"}

            oj._write_wiki_page = _fake_write
            oj.save_json = lambda path, data: saved.setdefault(str(path), data)

            # kb 存根：阻断 check_similar_concepts 的真实索引访问
            fake_kb = types.ModuleType("knowledge_base")
            fake_kb.check_similar_concepts = lambda *a, **k: []
            sys.modules["knowledge_base"] = fake_kb

            result = oj._extract_daily_knowledge(dry_run=False)

            self.assert_true(
                result.get("success") is True,
                "daily萃取缺键不再抛 KeyError",
                f"result={result}",
            )
            self.assert_eq(
                result.get("skipped_invalid"), _EXPECTED_SKIPPED,
                "daily萃取缺键跳过计数正确",
            )
            self.assert_eq(
                len(written), _EXPECTED_WRITTEN,
                "daily萃取有效条目正常写入",
            )
            kinds = [k for k, _ in written]
            self.assert_true(
                kinds == ["concept", "method", "person", "paper"],
                "daily萃取四类各写入一条",
                f"kinds={kinds}",
            )
            titles = [t for _, t in written]
            self.assert_true(
                "有效概念" in titles and "有效方法" in titles and "有效学者" in titles and "有效论文" in titles,
                "daily萃取 title 去空白后写入",
                f"titles={titles}",
            )
        finally:
            for k, v in orig.items():
                setattr(oj, k, v)
            if orig_kb is not None:
                sys.modules["knowledge_base"] = orig_kb
            else:
                sys.modules.pop("knowledge_base", None)

    # ------------------------------------------------------------------
    # 2. knowledge_output.process_daily_sources（CLI --daily 同型路径）
    # ------------------------------------------------------------------

    def _test_knowledge_output_guard(self):
        import json as _json
        import knowledge_output as ko

        written = []
        orig = {
            "_collect_daily_sources": ko._collect_daily_sources,
            "is_llm_available": ko.is_llm_available,
            "llm_complete": ko.llm_complete,
            "_write_wiki_page": ko._write_wiki_page,
            "load_json": ko.load_json,
            "save_json": ko.save_json,
        }

        try:
            ko._collect_daily_sources = lambda days=7: [dict(_FAKE_SOURCES["sources"][0])]
            ko.is_llm_available = lambda: True
            ko.llm_complete = lambda system, user, timeout=150, prefer=None: (
                True, _json.dumps(_BAD_PAYLOAD), {},
            )

            def _fake_write(kind, title, body, sources, reliability):
                written.append((kind, title))
                return {"success": True, "path": f"{kind}/{title}"}

            ko._write_wiki_page = _fake_write
            ko.load_json = lambda path, default=None: {"claims": []}
            ko.save_json = lambda path, data: None

            result = ko.process_daily_sources(dry_run=False)

            self.assert_true(
                result.get("success") is True,
                "CLI daily 萃取缺键不再抛 KeyError",
                f"result={result}",
            )
            self.assert_eq(
                result.get("skipped_invalid"), _EXPECTED_SKIPPED,
                "CLI daily 萃取缺键跳过计数正确",
            )
            self.assert_eq(
                len(written), _EXPECTED_WRITTEN,
                "CLI daily 萃取有效条目正常写入",
            )
        finally:
            for k, v in orig.items():
                setattr(ko, k, v)

    # ------------------------------------------------------------------
    # 3. _item_title 助手边界（覆盖归档萃取循环的同一守卫）
    # ------------------------------------------------------------------

    def _test_helper_edges(self):
        import weekend_pipeline.output_jobs as oj

        self.assert_eq(oj._item_title(None), "", "None 条目返回空串")
        self.assert_eq(oj._item_title("裸字符串"), "", "非 dict 条目返回空串")
        self.assert_eq(oj._item_title({}), "", "空 dict 返回空串")
        self.assert_eq(oj._item_title({"title": "   "}), "", "纯空白 title 返回空串")
        self.assert_eq(oj._item_title({"title": " x "}), "x", "title 去除首尾空白")
        self.assert_eq(oj._item_title({"name": "张三"}, "name"), "张三", "name 键正常取值")
        self.assert_eq(oj._item_title({"title": 123}), "123", "非字符串 title 强转")


if __name__ == "__main__":
    suite = WeekendExtractGuardTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    failed = [r for r in suite.results if not r.passed]
    print(f"完成：通过 {len(suite.results) - len(failed)}，失败 {len(failed)}")
    for r in failed:
        print(f"  ✗ {r.name}: {r.msg}")
    sys.exit(1 if failed else 0)
