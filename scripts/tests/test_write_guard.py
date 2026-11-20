#!/usr/bin/env python3
"""write_guard 单元测试：写锁跳过、10 分钟双写冲突、旧报告 stale 标记。"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lifecycle.write_guard import (
    check_write_lock,
    mark_stale_reports,
    record_section_write,
    _sha256,
)


class TestWriteGuard(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.prop = Path(self._td.name) / "prop"
        (self.prop / "04_proposal" / "sections").mkdir(parents=True)
        (self.prop / "05_review").mkdir(parents=True)
        self.section = self.prop / "04_proposal" / "sections" / "content.md"
        self.section.write_text("正文 A", encoding="utf-8")

    def tearDown(self):
        self._td.cleanup()

    def test_lock_absent_allows(self):
        ok, _ = check_write_lock(self.prop, "job:j1")
        self.assertTrue(ok)

    def test_lock_other_holder_blocks(self):
        (self.prop / ".write-lock").write_text(
            "- 持有者：TraeCode 会话（本会话唯一 writer/critic）\n", encoding="utf-8")
        ok, why = check_write_lock(self.prop, "job:j1")
        self.assertFalse(ok)
        self.assertIn("写锁存在", why)
        ok2, _ = check_write_lock(self.prop, "TraeCode 会话")
        self.assertTrue(ok2)

    def test_two_writers_within_window_conflict(self):
        r1 = record_section_write(self.prop, "content", "job:j1")
        self.assertFalse(r1["conflict"])
        r2 = record_section_write(self.prop, "content", "job:j2")
        self.assertTrue(r2["conflict"])
        self.assertEqual(r2["recent_writers"], 2)

    def test_stale_report_renamed_not_overwritten(self):
        sha = _sha256(self.section)
        report = self.prop / "05_review" / "critic-round-4-content.md"
        report.write_text(
            "<!-- round-4-sha256 -->\n- 评前 sha256：`" + sha + "`\n", encoding="utf-8")
        self.assertEqual(mark_stale_reports(self.prop, "content")["stale"], [])
        self.section.write_text("正文 B", encoding="utf-8")
        res = mark_stale_reports(self.prop, "content")
        self.assertEqual(len(res["stale"]), 1)
        self.assertFalse(report.exists())
        self.assertTrue((self.prop / "05_review" / res["stale"][0]).exists())


if __name__ == "__main__":
    unittest.main()
