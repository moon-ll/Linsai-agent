#!/usr/bin/env python3
"""test_deep_read_long_authors — deep_read_pipeline 头读窗口回归（v6.9.77）。

背景：v6.9.75 修复了 kb_distill gate2 的 500B 头读窗口（agent_rejected
位于 title/authors 之后，30+ 作者论文偏移 660B+ 溢出），但同日新增的
deep_read_pipeline._raw_frontmatter 仍用 1200B 窗口——kb_importer 字段序
中 score_agent 同样位于 title/authors 之后，35+ 作者大协作组论文（物理
领域百人作者常见）偏移可超 1200B，导致 score_agent≥8 的高分论文被误判
为摘要级、漏出深度阅读队列。本套件锁定 8192B 窗口行为。

用法：python3 scripts/tests/test_deep_read_long_authors.py
规范：仅标准库；临时目录自建自清，零污染。
"""
import sys
import tempfile
from pathlib import Path

TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(TESTS_DIR.parent))

from test_runner import TestSuite


def _make_raw(authors: str, score_agent: int = 9) -> str:
    """按 kb_importer 真实字段序构造 raw md（title→authors→…→score_agent）。"""
    return (
        "---\n"
        'title: "Large collaboration high score paper"\n'
        'arxiv_id: "2504.00003"\n'
        f'authors: "{authors}"\n'
        'year: "2026"\n'
        'tags: ["deepxiv-论文库"]\n'
        'source: "hermes-简报"\n'
        'imported_at: "2026-08-29T00:00:00Z"\n'
        "score_deepxiv: 0.7\n"
        f"score_agent: {score_agent}\n"
        'agent_note: "高度相关"\n'
        "agent_rejected: false\n"
        "---\n正文"
    )


class DeepReadLongAuthorsTests(TestSuite):
    """大作者论文的 score_agent 不得因头读窗口截断而漏检。"""

    def __init__(self):
        super().__init__("deep_read 大作者头读窗口回归")

    def run_tests(self):
        import deep_read_pipeline

        # 1) 40 作者（score_agent 偏移 ~1800B，超旧 1200B 窗口）→ 必须进 deep
        authors40 = ", ".join(
            f"F. M. Author-With-Longname van der Berg {i:03d}" for i in range(40))
        content40 = _make_raw(authors40)
        if not self.assert_true(
                content40.index("score_agent:") > 1200,
                "用例自检：40 作者偏移应在旧 1200B 窗口外",
                f"实际偏移 {content40.index('score_agent:')}"):
            return
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "2026-2504.00003-large-collab.md"
            raw.write_text(content40, encoding="utf-8")
            fm = deep_read_pipeline._raw_frontmatter(raw)
            if not self.assert_true(
                    fm.get("score_agent") == 9.0,
                    "40 作者论文 score_agent 可见（不被窗口截断）",
                    f"解析结果 {fm}"):
                return
            sel = deep_read_pipeline.select_candidates(Path(td))
            self.assert_true(
                len(sel["deep"]) == 1 and len(sel["abstract_level"]) == 0,
                "高分大作者论文进 deep 队列",
                f"deep={len(sel['deep'])} abstract={len(sel['abstract_level'])}")

        # 2) 100 作者（偏移 ~3400B）→ 仍必须命中
        authors100 = ", ".join(
            f"Some Very Long Author Name {i:03d}" for i in range(100))
        content100 = _make_raw(authors100)
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "2026-2505.00004-hundred-authors.md"
            raw.write_text(content100, encoding="utf-8")
            fm = deep_read_pipeline._raw_frontmatter(raw)
            self.assert_true(
                fm.get("score_agent") == 9.0,
                "100 作者论文 score_agent 可见",
                f"解析结果 {fm}")

        # 3) 短作者低分论文仍走摘要级（窗口放宽不改变分流语义）
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "2026-2506.00005-small-team.md"
            raw.write_text(_make_raw("Alice, Bob, Carol", score_agent=5),
                           encoding="utf-8")
            sel = deep_read_pipeline.select_candidates(Path(td))
            self.assert_true(
                len(sel["deep"]) == 0 and len(sel["abstract_level"]) == 1,
                "短作者低分论文仍为摘要级",
                f"deep={len(sel['deep'])} abstract={len(sel['abstract_level'])}")

        # 4) agent_rejected 超窗口时同样必须可见（可见性口径与 gate2 对齐）
        content_rej = content40.replace("agent_rejected: false",
                                        "agent_rejected: true")
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "2026-2507.00006-rejected-big.md"
            raw.write_text(content_rej, encoding="utf-8")
            fm = deep_read_pipeline._raw_frontmatter(raw)
            self.assert_true(
                fm.get("agent_rejected") is True,
                "超窗口 agent_rejected 可见",
                f"解析结果 {fm}")


if __name__ == "__main__":
    suite = DeepReadLongAuthorsTests()
    suite.run_tests()
    s = suite.summary()
    print(f"{s['name']}: {'✓ 全过' if s['failed'] == 0 else '✗ 有失败'} "
          f"({s['passed']}/{s['passed'] + s['failed']})")
    for r in suite.results:
        if not r.passed:
            print(f"  ✗ {r.name}: {r.message}")
