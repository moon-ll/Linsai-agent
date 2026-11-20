#!/usr/bin/env python3
"""
test_kb_proposal_reorg.py — 知识库提案整理（MOC 更新）单元测试

覆盖：
    - MOC.md 幂等性：连续多次运行不重复追加内容（v6.8.5 缺陷回归）
    - MOC.md 保留手工维护章节（课题相关概念/相关方法/相关团队/课题论文/外部链接）
    - 标签提取：跳过 brief 通用 H1「课题说明」

注意：
    本测试不调用 hermes/LLM，仅验证文件整理逻辑。
"""

import sys
import shutil
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root
import importlib


class KBProposalReorgTests(TestSuite):
    def __init__(self):
        super().__init__("知识库提案整理测试")
        self.tmp_root = None
        self.reorg_mod = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        nsfc_dir = self.tmp_root / "knowledge" / "wiki" / "projects" / "NSFC-强场超快"
        nsfc_dir.mkdir(parents=True, exist_ok=True)
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        # 最小 lifecycle 状态
        lifecycle_path = self.tmp_root / "research_proposals" / "_lifecycle.json"
        lifecycle_path.write_text(
            '{"proposals": {"general-test-kb-20260101": {"status": "optimizing", "project_type": "general", "optimization_rounds": 1, "last_score": 0.65}}}',
            encoding="utf-8",
        )

        # proposal 最小文件
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / "general-test-kb-20260101"
        prop_dir.mkdir(parents=True, exist_ok=True)
        (prop_dir / "00_proposal-brief.md").write_text(
            "# 课题说明\n\n**课题名称**：测试课题\n",
            encoding="utf-8",
        )
        (prop_dir / "04_proposal").mkdir(parents=True, exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text("# draft\n", encoding="utf-8")

        # MOC.md 初始内容：模拟 v6.8.5 缺陷产生的重复块（污染状态）
        dup_block = (
            "# NSFC 强场超快课题知识地图\n\n"
            "> 本页是 NSFC 强场超快光学课题的知识入口，聚合课题相关概念、方法、人物和论文。\n\n"
            "## 申请书与优化报告\n\n"
            "| 课题 | 状态 | 轮次 | 分数 | 版本 | 报告 |\n"
            "|------|------|------|------|------|------|\n"
            "| 课题说明 | 优化中 | 第1轮 | 0.65 | [版本](versions/x.md) | [报告](reports/x.md) |\n\n"
        )
        manual_sections = (
            "## 🔬 课题相关概念\n\n"
            "- [[固体高次谐波]] — 课题核心研究对象\n\n"
            "## 🛠️ 相关方法\n\n"
            "- [[TDSE求解器]] — 理论计算核心\n\n"
            "## 👤 相关团队\n\n"
            "- [[Ghimire-Reis]] — 固体 HHG 开创\n\n"
            "## 📄 课题论文\n\n"
            "- arXiv:2503.08052\n\n"
            "## 🔗 外部链接\n\n"
            "- 外部链接占位\n"
        )
        (nsfc_dir / "MOC.md").write_text(dup_block * 3 + manual_sections, encoding="utf-8")

        # 强制重新导入并 patch 根目录到隔离环境
        if "kb_proposal_reorg" in sys.modules:
            del sys.modules["kb_proposal_reorg"]
        self.reorg_mod = importlib.import_module("kb_proposal_reorg")
        patch_module_root("kb_proposal_reorg", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _moc_path(self) -> Path:
        return self.tmp_root / "knowledge" / "wiki" / "projects" / "NSFC-强场超快" / "MOC.md"

    def _test_moc_no_duplication(self):
        reorg = self.reorg_mod.KBProposalReorg(dry_run=False)
        reorg.run()
        content = self._moc_path().read_text(encoding="utf-8")
        self.assert_eq(
            content.count("本页是 NSFC 强场超快光学课题的知识入口"),
            1,
            "MOC 引言行仅出现一次（不重复追加）",
        )
        self.assert_eq(
            content.count("## 申请书与优化报告"),
            1,
            "申请书与优化报告表格仅一份",
        )

    def _test_moc_idempotent(self):
        moc_path = self._moc_path()
        reorg = self.reorg_mod.KBProposalReorg(dry_run=False)
        reorg.run()
        size_first = moc_path.stat().st_size
        reorg.run()
        size_second = moc_path.stat().st_size
        self.assert_eq(size_second, size_first, "连续两次运行 MOC.md 大小不变（幂等）")

    def _test_moc_manual_sections_preserved(self):
        reorg = self.reorg_mod.KBProposalReorg(dry_run=False)
        reorg.run()
        content = self._moc_path().read_text(encoding="utf-8")
        for kw in ["课题相关概念", "相关方法", "相关团队", "课题论文", "外部链接", "固体高次谐波", "TDSE求解器"]:
            self.assert_in(kw, content, f"手工章节保留: {kw}")

    def _test_label_skips_generic_title(self):
        label = self.reorg_mod._extract_label(
            "general-test-kb-20260101", "# 课题说明\n\n**课题名称**：测试课题\n"
        )
        self.assert_true(label != "课题说明", "标签跳过通用标题「课题说明」")
        self.assert_eq(label, "test-kb", "标签回退到 ID 推断")

    def run_tests(self):
        self._test_moc_no_duplication()
        self._test_moc_idempotent()
        self._test_moc_manual_sections_preserved()
        self._test_label_skips_generic_title()