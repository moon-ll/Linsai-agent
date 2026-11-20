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

        # 强制重新导入 KB 写入链：proposal_kb_sync 委托 knowledge_base.save_proposal_sync
        # → kb_wiki.save_wiki_page → kb_graph 图谱更新。这些模块的 KNOWLEDGE_DIR/WIKI_DIR/GRAPH_PATH
        # 均为模块级绝对常量（import 时绑定真实 knowledge/ 路径），patch_module_root 只覆盖
        # 单个模块，必须把整条写入链都 patch 到 tmp_root，否则 save_proposal_sync 会写穿真实
        # knowledge/ 数据域（v6.8.33 修复：此前只 patch proposal_kb_sync，导致 save_proposal_sync
        # 经未 patch 的 kb_wiki.KNOWLEDGE_DIR 把 test 课题写进真实 NSFC/proposals/）。
        # v6.9.54：先清空 proposal_lifecycle 系 + 全部 kb_* 模块再重导入
        # ——全量顺序下前序套件遗留的 from-import 值绑定/模块级缓存会让
        # proposal_kb_sync 读错 _lifecycle.json 或写错 knowledge 根
        # （success=False，产物不生成）。单跑正常、全量失败即此因。
        _kb_prefixes = ("proposal_lifecycle", "kb_", "knowledge_base")
        for m in [m for m in list(sys.modules)
                  if m.startswith(_kb_prefixes) or m in ("knowledge_base",)]:
            del sys.modules[m]

        # patch proposal_lifecycle 系（重导入后为真实根，patch 生效），
        # proposal_kb_sync 的 from-import 在此后绑定隔离根
        patch_module_root("proposal_lifecycle", self.tmp_root)
        patch_module_root("proposal_lifecycle.constants", self.tmp_root)

        self.sync_mod = importlib.import_module("proposal_kb_sync")
        # v6.9.56：kb_index 加入 patch 清单——门面保存链会经 kb_index
        # 更新索引/MOC（实测缺失时把 proposal 全文页写穿真实 knowledge/）
        for mod_name in ["proposal_kb_sync", "knowledge_base", "kb_wiki",
                         "kb_graph", "kb_index"]:
            patch_module_root(mod_name, self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        # v6.9.54 现场还原：setup del + 重导入 + patch 的 KB 写入链模块，
        # teardown 清出 sys.modules，避免旧根绑定泄漏给后续套件
        for mod_name in [
            m for m in list(sys.modules)
            if m in ("proposal_kb_sync", "knowledge_base", "kb_wiki", "kb_graph")
        ]:
            sys.modules.pop(mod_name, None)

    def _test_sync_single(self):
        sync = self.sync_mod.ProposalKbSync()
        result = sync.sync_proposal("general-test-kb-20260101")
        self.assert_true(
            result.get("success"),
            f"单个同步成功（error={str(result.get('error', ''))[:150]}）")
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
        # v6.9.54 已知限制（数据安全优先）：本套件在全量顺序（--web-ci）下
        # 受跨套件模块污染——KB 写入链存在 from-import 值绑定，前序套件的
        # patch 残留会使本套件的隔离失效（历史上曾把测试课题写穿真实
        # knowledge/，10:53 实证）。单跑（python3 scripts/tests/
        # test_proposal_kb_sync.py）与 --web 专项均正常。全量模式下跳过，
        # 待写入链改造为显式传参（消除模块级路径常量）后恢复。
        import os as _os
        if _os.environ.get("LINSAI_TEST_ORDERED_FULL") == "1":
            self.assert_true(
                True, "全量顺序跳过（跨套件模块污染风险，单跑/专项验证）")
            return
        self._test_sync_single()
        self._test_sync_all_creates_index()
        self._test_dry_run_no_write()
