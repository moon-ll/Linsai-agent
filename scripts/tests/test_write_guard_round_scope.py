#!/usr/bin/env python3
"""BUG-47 回归测试：write_guard 同轮报告误伤 + method_manual 路径错位。

背景（2026-11-06 08h 健康检查发现，v7.3.50 修复）：
v7.3.48 引入的 write_guard 落盘钩子有两个缺陷：

1. **同轮报告误伤**——`mark_stale_reports` 不区分轮次，凡存证哈希与当前
   正文不符即改名 `*.stale-<ts>.md`。但 writer 落盘后正文哈希**必然**与
   本轮 critic 报告的存证哈希不同（writer 的职责就是改正文）→ 本轮刚
   产出、正被后续 critic/写后复检消费的 `critic-round-N-{section}.md`
   被当场改名。而 `executor._read_critic_report` 按精确名读盘 → 读到空
   → score=0.0 / dim_scores={} → 该章节后续质量门全部失真。
   实测（chiral round-5）：writer 落盘一次即把 `critic-round-5-content.md`
   与 `critic-round-3-content.md` 一并改名 → `_read_critic_report(round=5)`
   返回 score=0.0；修复后同场景返回 score=0.79 / dim_scores 4 维齐全。

2. **method_manual 路径错位**——`method_manual` 是第六评审模块，产物在
   `03_method/method-manual.md`（唯一真相源），**不在** `04_proposal/sections/`。
   旧实现对所有 section_key 一律拼 `sections/{key}.md` → 对 method_manual
   恒指向不存在路径 → `mark_stale_reports` 恒 checked=0（静默失效），
   `record_section_write` 恒记录空 sha256。

本测试覆盖：
- 同轮报告不被改名（current_round 生效）
- 历史轮次报告仍被正确标记 stale（判定能力未被削弱）
- current_round 未传时保持旧行为（CLI 手工查询路径）
- 派生文件（postfix / pre-l101 / .bak）不被误判
- method_manual 落到 03_method/ 且哈希非空
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lifecycle.write_guard import (
    _section_file,
    _sha256,
    mark_stale_reports,
    record_section_write,
)


class TestWriteGuardRoundScope(unittest.TestCase):
    """BUG-47 回归：同轮报告保护 + method_manual 路径。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.prop = Path(self._td.name) / "prop"
        (self.prop / "04_proposal" / "sections").mkdir(parents=True)
        (self.prop / "03_method").mkdir(parents=True)
        (self.prop / "05_review").mkdir(parents=True)
        self.section = self.prop / "04_proposal" / "sections" / "content.md"
        self.section.write_text("正文 A", encoding="utf-8")

    def tearDown(self):
        self._td.cleanup()

    def _make_report(self, round_num, sha, name=None):
        """造一份带存证哈希的 critic 报告，返回其路径。"""
        fname = name or f"critic-round-{round_num}-content.md"
        rp = self.prop / "05_review" / fname
        rp.write_text(
            f"<!-- round-{round_num}-sha256 -->\n- 评前 sha256：`{sha}`\n",
            encoding="utf-8")
        return rp

    # ── 缺陷 1：同轮报告误伤 ────────────────────────────────────────
    def test_current_round_report_not_renamed(self):
        """本轮报告（round == current_round）不得被改名。"""
        sha = _sha256(self.section)
        rp = self._make_report(5, sha)
        # writer 落盘 → 正文哈希变化（与本轮报告存证不再一致）
        self.section.write_text("正文 B（writer 改后）", encoding="utf-8")
        cur = _sha256(self.section)

        res = mark_stale_reports(self.prop, "content", cur, current_round=5)

        self.assertTrue(rp.exists(), "本轮报告被误改名")
        self.assertIn("critic-round-5-content.md", res["skipped_current_round"])
        self.assertEqual(res["stale"], [], "本轮报告不应进入 stale 列表")

    def test_historic_round_report_still_marked_stale(self):
        """历史轮次报告（round < current_round）仍应被标记 stale（判定能力不削弱）。"""
        sha = _sha256(self.section)
        old = self._make_report(3, sha)
        cur_report = self._make_report(5, sha)
        self.section.write_text("正文 B（writer 改后）", encoding="utf-8")
        cur = _sha256(self.section)

        res = mark_stale_reports(self.prop, "content", cur, current_round=5)

        self.assertEqual(len(res["stale"]), 1, "历史轮报告应被标记 stale")
        self.assertFalse(old.exists(), "历史轮报告应被改名")
        self.assertTrue((self.prop / "05_review" / res["stale"][0]).exists())
        self.assertTrue(cur_report.exists(), "本轮报告必须保持原名")

    def test_current_round_absent_keeps_legacy_behavior(self):
        """current_round 未传时保持旧行为（全量比对），供 CLI 手工查询。"""
        sha = _sha256(self.section)
        rp = self._make_report(4, sha)
        self.section.write_text("正文 B", encoding="utf-8")
        cur = _sha256(self.section)

        res = mark_stale_reports(self.prop, "content", cur)

        self.assertEqual(len(res["stale"]), 1)
        self.assertFalse(rp.exists())

    def test_derived_files_not_treated_as_round_reports(self):
        """派生文件（postfix / pre-l101 / .bak）不得被当作轮次报告改名。"""
        sha = _sha256(self.section)
        derived = self._make_report(3, sha, name="critic-round-3-content-postfix.md")
        keep = self._make_report(3, sha, name="critic-round-3-content.pre-l101.md")
        self.section.write_text("正文 B", encoding="utf-8")
        cur = _sha256(self.section)

        res = mark_stale_reports(self.prop, "content", cur, current_round=5)

        self.assertEqual(res["stale"], [], "派生文件不应被改名")
        self.assertTrue(derived.exists())
        self.assertTrue(keep.exists())

    def test_same_hash_report_kept(self):
        """存证哈希与当前正文一致 → 不改名（同一版本）。"""
        sha = _sha256(self.section)
        rp = self._make_report(3, sha)
        res = mark_stale_reports(self.prop, "content", sha, current_round=5)
        self.assertEqual(res["stale"], [])
        self.assertTrue(rp.exists())

    # ── 缺陷 2：method_manual 路径错位 ──────────────────────────────
    def test_method_manual_path_points_to_03_method(self):
        """method_manual 的产物路径是 03_method/method-manual.md。"""
        p = _section_file(self.prop, "method_manual")
        self.assertEqual(p.name, "method-manual.md")
        self.assertEqual(p.parent.name, "03_method")

    def test_method_manual_records_real_sha(self):
        """method_manual 写入登记须记录到非空 sha256（修复前恒为空串）。"""
        manual = self.prop / "03_method" / "method-manual.md"
        manual.write_text("# 手册正文\n\n参数：k = 5\n", encoding="utf-8")
        rec = record_section_write(self.prop, "method_manual", "job:j1")
        self.assertEqual(len(rec["sha256"]), 64, "method_manual sha256 不应为空")
        self.assertEqual(rec["sha256"], _sha256(manual))

    def test_method_manual_stale_check_reaches_reports(self):
        """method_manual 的 stale 复核须真正命中报告（修复前恒 checked=0）。"""
        manual = self.prop / "03_method" / "method-manual.md"
        manual.write_text("手册 A", encoding="utf-8")
        sha = _sha256(manual)
        rp = self.prop / "05_review" / "critic-round-1-method_manual.md"
        rp.write_text("- 评前 sha256：`" + sha + "`\n", encoding="utf-8")

        # 手册内容变化 → 存证不再一致 → 历史轮报告应被标记 stale
        manual.write_text("手册 B（writer 改后）", encoding="utf-8")
        cur = _sha256(manual)
        res = mark_stale_reports(self.prop, "method_manual", cur, current_round=2)

        self.assertEqual(res["checked"], 1, "method_manual stale 复核未生效")
        self.assertEqual(len(res["stale"]), 1)
        self.assertTrue(rp.exists() is False)


if __name__ == "__main__":
    unittest.main()
