#!/usr/bin/env python3
"""
test_proposal_kb_sync.py — Proposal 知识库同步单元测试

覆盖：
    - 同步单个 proposal 生成知识库 markdown
    - 同步所有 proposal 生成索引
    - dry-run 不写入文件

注意：
    本测试不调用 hermes/LLM，仅验证文件同步逻辑。
"""

import sys
import shutil
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT
import importlib


class ProposalKbSyncTests(TestSuite):
    def __init__(self):
        super().__init__("Proposal 知识库同步测试")
        self.tmp_root = None
        self.sync_mod = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 创建 knowledge/wiki/projects/NSFC-强场超快 与 research_proposals 结构
        nsfc_dir = self.tmp_root / "knowledge" / "wiki" / "projects" / "NSFC-强场超快"
        nsfc_dir.mkdir(parents=True, exist_ok=True)
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        # 写入最小 lifecycle 状态
        lifecycle_path = self.tmp_root / "research_proposals" / "_lifecycle.json"
        lifecycle_path.write_text(
            '{"proposals": {"general-test-kb-20260101": {"status": "optimizing", "project_type": "general", "optimization_rounds": 1, "last_score": 0.65}}}',
            encoding="utf-8",
        )

        # 创建 proposal 最小文件
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / "general-test-kb-20260101"
        prop_dir.mkdir(parents=True, exist_ok=True)
        (prop_dir / "00_proposal-brief.md").write_text(
            "# 课题说明\n\n**课题名称**：测试课题\n**项目类型**：面上项目\n",
            encoding="utf-8",
        )
        (prop_dir / "04_proposal").mkdir(parents=True, exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text("# draft\n", encoding="utf-8")

        # 强制重新导入
        for mod_name in ["proposal_kb_sync"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        self.sync_mod = importlib.import_module("proposal_kb_sync")
        patch_module_root("proposal_kb_sync", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _test_sync_single(self):
        sync = self.sync_mod.ProposalKbSync()
        result = sync.sync_proposal("general-test-kb-20260101")
        self.assert_true(result.get("success"), "单个同步成功")
        kb_path = self.tmp_root / "knowledge" / "wiki" / "projects" / "NSFC-强场超快" / "proposals" / "general-test-kb-20260101.md"
        self.assert_true(kb_path.exists(), "知识库 markdown 已生成")
        content = kb_path.read_text(encoding="utf-8")
        self.assert_in("测试课题", content, "标题写入知识库")
        self.assert_in("优化中", content, "状态写入知识库")

    def _test_sync_all_creates_index(self):
        sync = self.sync_mod.ProposalKbSync()
        result = sync.sync_all()
        self.assert_true(result.get("success"), "全量同步成功")
        self.assert_eq(result.get("synced_count"), 1, "同步 1 个 proposal")
        index_path = self.tmp_root / "knowledge" / "wiki" / "projects" / "NSFC-强场超快" / "proposals-index.md"
        self.assert_true(index_path.exists(), "索引文件已生成")
        content = index_path.read_text(encoding="utf-8")
        self.assert_in("general-test-kb-20260101", content, "索引包含 proposal")

    def _test_dry_run_no_write(self):
        sync = self.sync_mod.ProposalKbSync()
        kb_path = self.tmp_root / "knowledge" / "wiki" / "projects" / "NSFC-强场超快" / "proposals" / "general-test-kb-20260101.md"
        index_path = self.tmp_root / "knowledge" / "wiki" / "projects" / "NSFC-强场超快" / "proposals-index.md"
        # 确保干净：先删除可能存在的文件
        if kb_path.exists():
            kb_path.unlink()
        if index_path.exists():
            index_path.unlink()
        result = sync.sync_all(dry_run=True)
        self.assert_true(result.get("success"), "dry-run 返回成功")
        self.assert_true(not kb_path.exists(), "dry-run 不生成 markdown")
        self.assert_true(not index_path.exists(), "dry-run 不生成索引")

    def run_tests(self):
        self._test_sync_single()
        self._test_sync_all_creates_index()
        self._test_dry_run_no_write()
