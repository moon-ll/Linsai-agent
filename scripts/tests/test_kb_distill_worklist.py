#!/usr/bin/env python3
"""
test_kb_distill_worklist.py — 蒸馏 ZCode worklist 双通道回归测试（v7.2.28）

覆盖：
    - 工作清单目标构造（digest_hint 分层判定 / arxiv_id 提取 / batch 截断）
    - ZCode 落盘正文合成（source_raw 纯文件名 + digest_level 注入契约）
    - write_distilled_page 入口校验（raw 不存在 / 正文为空，零磁盘写入）
    - CLI --emit-worklist 参数存在性

注意：
    仅验证纯逻辑，不触发 LLM；worklist 落盘路径以 monkeypatch 重定向，
    不污染生产 memory/。
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from test_runner import TestSuite, create_isolated_env


class KbDistillWorklistTests(TestSuite):
    def __init__(self):
        super().__init__("kb_distill ZCode worklist 双通道测试")
        self.tmp_root = None

    def setup(self):
        self.tmp_root = create_isolated_env()

    def teardown(self):
        pass

    def run_tests(self):
        import kb_distill

        # 1) digest_hint 分层判定：has_fulltext + arxiv_id → fulltext
        raw_full = self.tmp_root / "raw" / "papers" / "2024-2402.12764-x.md"
        raw_full.parent.mkdir(parents=True, exist_ok=True)
        raw_full.write_text(
            "---\ntitle: t\narxiv_id: \"2402.12764\"\n"
            "has_fulltext: true\n---\n\n摘要内容", encoding="utf-8")
        hint, aid = kb_distill._raw_digest_hint(raw_full)
        self.assert_eq(hint, "fulltext", "has_fulltext → fulltext 精读档")
        self.assert_eq(aid, "2402.12764", "arxiv_id 提取")

        # 2) 摘要级：无 has_fulltext 标记 → abstract
        raw_abs = self.tmp_root / "raw" / "papers" / "2025-doi-paper.md"
        raw_abs.write_text(
            "---\ntitle: t\narxiv_id: \"\"\n---\n\n摘要", encoding="utf-8")
        hint2, aid2 = kb_distill._raw_digest_hint(raw_abs)
        self.assert_eq(hint2, "abstract", "无全文标记 → abstract 摘要档")
        self.assert_eq(aid2, "", "无 arxiv_id → 空串")

        # 3) 不存在的文件 → 温和降级 abstract（不抛异常）
        hint3, _ = kb_distill._raw_digest_hint(
            self.tmp_root / "raw" / "papers" / "ghost.md")
        self.assert_eq(hint3, "abstract", "读失败 → abstract 降级")

        # 4) ZCode 落盘合成契约：source_raw 纯文件名 + digest_level
        composed = kb_distill._compose_distilled_page(
            "# 标题\n\n## 林赛的理解\n正文一两句。", "2024-x.md", "fulltext")
        self.assert_true('source_raw: "2024-x.md"' in composed,
                         "source_raw 纯文件名注入")
        self.assert_true('digest_level: "fulltext"' in composed,
                         "digest_level 注入")

        # 5) digest_level 已有 → 不重复注入
        pre = ("---\nsource_raw: \"a.md\"\ndigest_level: \"abstract\"\n"
               "type: papers\n---\n\n正文")
        self.assert_eq(kb_distill._compose_distilled_page(
            pre, "a.md", "abstract").count("digest_level:"), 1,
            "digest_level 幂等不重复")

        # 6) write_distilled_page 入口校验（KNOWLEDGE_DIR 重定向，零生产写入）
        def fake_pending(limit=None):
            out = [raw_full, raw_abs]
            return out[:limit] if limit is not None else out

        from knowledge_base import KNOWLEDGE_DIR as _ORIG_KB_DIR
        orig = kb_distill.pending_distill_list
        kb_distill.pending_distill_list = fake_pending
        kb_distill.KNOWLEDGE_DIR = self.tmp_root
        try:
            r1 = kb_distill.write_distilled_page(
                "ghost-not-exist.md", "正文", "abstract")
            self.assert_true(not r1["success"], "raw 不存在 → 拒绝")
            self.assert_true("不存在" in r1.get("error", ""), "错误信息可读")

            r2 = kb_distill.write_distilled_page("2024-2402.12764-x.md",
                                                 "   \n", "abstract")
            self.assert_true(not r2["success"], "正文为空 → 拒绝")
            self.assert_true("正文为空" in r2.get("error", ""), "空正文错误信息")

            # 7) build_worklist_targets batch 截断 + 字段齐备
            targets = kb_distill.build_worklist_targets(batch=1)
            self.assert_eq(len(targets), 1, "batch=1 截断生效")
            self.assert_true(
                all(k in targets[0] for k in
                    ("raw_name", "raw_rel", "digest_hint", "arxiv_id", "mtime")),
                "目标字段齐备")
            self.assert_eq(targets[0]["digest_hint"], "fulltext",
                           "目标携带 digest_hint")
            full = kb_distill.build_worklist_targets(batch=0)
            self.assert_eq(len(full), 2, "batch=0 全量")
        finally:
            kb_distill.pending_distill_list = orig
            kb_distill.KNOWLEDGE_DIR = _ORIG_KB_DIR

        # 8) CLI 参数存在
        src = (PROJECT_ROOT / "scripts" / "kb_distill.py").read_text(
            encoding="utf-8")
        self.assert_true("--emit-worklist" in src, "CLI --emit-worklist 已接线")


if __name__ == "__main__":
    import time
    suite = KbDistillWorklistTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report
    print_report([suite])
