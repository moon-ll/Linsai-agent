# -*- coding: utf-8 -*-
"""learning_engine._ensure_arxiv_pdf_link 回归测试（v8.0.31）。

背景：蒸馏 prompt 自带 PDF 链接但 LLM 输出方差下可能不回显，E2E 曾把该
方差误判为链路失败（arXiv PDF 链接 ✗，实测 3 篇真实生产页 0 命中）。
修复：落盘前确定性补齐来源链接；本测试覆盖幂等/追加位置/来源节缺省/
abs 形式豁免/空 ID 直通五个分支。

零 LLM / 零联网 / 零落盘。
"""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from learning_engine import _ensure_arxiv_pdf_link  # noqa: E402

ID = "0806.1474"


class TestEnsureArxivPdfLink(unittest.TestCase):

    def test_appends_to_source_section_end(self):
        text = "---\ntitle: t\n---\n\n# 笔记\n\n## 来源\n- 检索时间：X\n"
        out = _ensure_arxiv_pdf_link(text, ID)
        self.assertIn(f"arxiv.org/pdf/{ID}", out)
        # 追加在来源节末尾（文末）
        self.assertTrue(out.rstrip("\n").endswith(f"- [arXiv PDF](https://arxiv.org/pdf/{ID})"))
        self.assertIn("## 来源", out)

    def test_appends_before_next_section(self):
        text = "## 来源\n- 旧条目\n\n## 开放问题\n- q\n"
        out = _ensure_arxiv_pdf_link(text, ID)
        src_pos = out.index("## 来源")
        link_pos = out.index("arxiv.org/pdf/")
        next_pos = out.index("## 开放问题")
        self.assertLess(src_pos, link_pos < next_pos, "链接应落在来源节内、下一节前")

    def test_idempotent_pdf_form(self):
        text = f"## 来源\n- [arXiv](https://arxiv.org/pdf/{ID})\n"
        self.assertEqual(_ensure_arxiv_pdf_link(text, ID), text)

    def test_idempotent_abs_form(self):
        # prompt 模板用的是 paper url（可能是 abs 形式）——豁免不重复补
        text = f"## 来源\n- 原文：https://arxiv.org/abs/{ID}\n"
        self.assertEqual(_ensure_arxiv_pdf_link(text, ID), text)

    def test_creates_missing_source_section(self):
        text = "# 笔记正文\n\n## 核心要点\n- x\n"
        out = _ensure_arxiv_pdf_link(text, ID)
        self.assertIn("## 来源", out)
        self.assertIn(f"arxiv.org/pdf/{ID}", out)

    def test_empty_id_passthrough(self):
        text = "# 笔记\n"
        self.assertEqual(_ensure_arxiv_pdf_link(text, ""), text)

    def test_trailing_newline_preserved(self):
        text = "## 来源\n- a\n"
        out = _ensure_arxiv_pdf_link(text, ID)
        self.assertTrue(out.endswith("\n"))
        text_no_nl = "## 来源\n- a"
        out2 = _ensure_arxiv_pdf_link(text_no_nl, ID)
        self.assertFalse(out2.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
