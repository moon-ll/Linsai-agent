#!/usr/bin/env python3
"""
test_optimize_sections.py — optimize.py ProposalSections 路径正确性测试

覆盖缺陷：
    optimize.py 的 _run_critic / _run_writer 中 ProposalSections(prop_dir)
    误用顶层 proposal 目录而非 prop_dir/"04_proposal"，导致 section_exists()
    检查到空的顶层 sections/ 目录，full_review 模式下 critic 读不到任何申请书内容。

验证点：
    - ProposalSections(prop_dir/"04_proposal") 能正确检测已有章节
    - ProposalSections(prop_dir) 错误路径下 section_exists 全部返回 False（回归守护）
    - full_review 模式的 files_to_read 列表非空

注意：
    本测试不调用 hermes/LLM，仅验证路径解析与章节检测逻辑。
"""

import sys
import shutil
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, REAL_ROOT
import importlib


class OptimizeSectionsTests(TestSuite):
    def __init__(self):
        super().__init__("optimize 章节路径正确性测试")
        self.tmp_root = None
        self.prop_dir = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        pid = "general-test-path-20260101"
        self.prop_dir = self.tmp_root / "research_proposals" / "optimizing" / pid

        # 创建正确的章节目录结构（04_proposal/sections/ 含真实内容）
        sections_dir = self.prop_dir / "04_proposal" / "sections"
        sections_dir.mkdir(parents=True, exist_ok=True)
        for key, title in [
            ("rationale", "（一）立项依据"),
            ("content", "（二）研究内容"),
            ("scheme", "（三）研究方案"),
            ("full_review", "整体一致性审查"),
            ("references", "参考文献检验"),
        ]:
            (sections_dir / f"{key}.md").write_text(
                f"## {title}\n\n这是 {title} 的测试内容，确保超过 50 字符阈值以便 section_exists 返回 True。\n",
                encoding="utf-8",
            )

        # 同时创建顶层的空 sections/ 目录（模拟 bug 现场的历史残留）
        top_sections = self.prop_dir / "sections"
        top_sections.mkdir(parents=True, exist_ok=True)
        for key in ["rationale", "content", "scheme", "full_review", "references"]:
            (top_sections / f"{key}.md").write_text("", encoding="utf-8")

        # 导入 proposal_sections 模块
        for mod_name in ["proposal_sections"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        importlib.import_module("proposal_sections")

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        from proposal_sections import ProposalSections, PROPOSAL_SECTIONS

        # 测试 1: 正确路径下所有章节可见
        sections_right = ProposalSections(self.prop_dir / "04_proposal")
        all_exist_right = all(
            sections_right.section_exists(s["key"]) for s in PROPOSAL_SECTIONS
        )
        self.assert_true(
            all_exist_right,
            "正确路径(04_proposal)下所有章节可见",
            "section_exists 应对 04_proposal/sections/ 下所有章节返回 True",
        )

        # 测试 2: 错误路径下所有章节不可见（回归守护）
        sections_wrong = ProposalSections(self.prop_dir)
        all_missing_wrong = not any(
            sections_wrong.section_exists(s["key"]) for s in PROPOSAL_SECTIONS
        )
        self.assert_true(
            all_missing_wrong,
            "错误路径(顶层)下章节不可见(回归守护)",
            "顶层空 sections/ 不应被误认为有效章节",
        )

        # 测试 3: full_review 模式 files_to_read 非空
        files_right = [
            str(self.prop_dir / "04_proposal" / "sections" / f"{s['key']}.md")
            for s in PROPOSAL_SECTIONS
            if sections_right.section_exists(s["key"])
        ]
        self.assert_eq(
            len(files_right), 5,
            "正确路径下 full_review files_to_read 含 5 个文件",
        )

        # 测试 4: 错误路径下 files_to_read 为空（重现 bug 行为）
        files_wrong = [
            str(self.prop_dir / "04_proposal" / "sections" / f"{s['key']}.md")
            for s in PROPOSAL_SECTIONS
            if sections_wrong.section_exists(s["key"])
        ]
        self.assert_eq(
            len(files_wrong), 0,
            "错误路径下 full_review files_to_read 为空(bug 重现)",
        )

        # 测试 5: assemble_draft 写入正确路径
        sections_right.assemble_draft()
        draft_path = self.prop_dir / "04_proposal" / "proposal-draft.md"
        self.assert_true(
            draft_path.exists() and len(draft_path.read_text(encoding="utf-8")) > 100,
            "assemble_draft 写入 04_proposal/proposal-draft.md",
        )
