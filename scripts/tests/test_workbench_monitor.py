# -*- coding: utf-8 -*-
"""workbench_monitor 备份新鲜度检查回归测试（v8.0.28）。

覆盖动机：cron 对账只校验 lc-daily-backup job 存在性，2026-11 保留窗内
11-14/11-16 两天实际缺 *-auto.zip 包而监控全绿——job 在 ≠ 产物在。
本测试用临时备份目录 + mtime 打桩验证分级告警：
  目录缺失 / 无 auto 包 → high；>54h → high；>30h → medium；新鲜 → 无告警。

零 LLM / 零 hermes / 零真实 backups 目录触碰。
"""
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from workbench_monitor import (  # noqa: E402
    BACKUP_CRITICAL_HOURS,
    BACKUP_WARN_HOURS,
    check_backups,
)


def _make_auto_zip(root: Path, name: str, age_hours: float = 0.0) -> Path:
    """在 root 下造一个 *-auto.zip 并把 mtime 拨回 age_hours 小时前。"""
    root.mkdir(parents=True, exist_ok=True)
    p = root / name
    p.write_text("stub", encoding="utf-8")
    ts = time.time() - age_hours * 3600.0
    os.utime(p, (ts, ts))
    return p


class TestCheckBackups(unittest.TestCase):
    """check_backups 分级告警：fresh→[]、30-54h→medium、>54h→high。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "backups"
        self.addCleanup(self._tmp.cleanup)

    def test_fresh_backup_no_issue(self):
        _make_auto_zip(self.root, "2026-11-20T05-00-00Z-auto.zip", age_hours=10)
        self.assertEqual(check_backups(self.root), [])

    def test_stale_one_cycle_medium(self):
        _make_auto_zip(self.root, "2026-11-18T05-00-00Z-auto.zip",
                       age_hours=BACKUP_WARN_HOURS + 6)
        issues = check_backups(self.root)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["severity"], "medium")
        self.assertIn("-auto.zip", issues[0]["issue"])

    def test_stale_two_cycles_high(self):
        _make_auto_zip(self.root, "2026-11-17T05-00-00Z-auto.zip",
                       age_hours=BACKUP_CRITICAL_HOURS + 6)
        issues = check_backups(self.root)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["severity"], "high")

    def test_missing_dir_high(self):
        issues = check_backups(self.root)  # 目录未创建
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["severity"], "high")

    def test_no_auto_zip_high(self):
        # 只有专项/partial 包 → 不算每日自动备份，high
        _make_auto_zip(self.root, "2026-11-20T06-00-00Z-manual-partial.zip")
        issues = check_backups(self.root)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["severity"], "high")

    def test_latest_auto_wins(self):
        # 新旧 auto 并存：以最新 mtime 为准，新鲜 → 无告警
        _make_auto_zip(self.root, "2026-11-17T05-00-00Z-auto.zip",
                       age_hours=BACKUP_CRITICAL_HOURS + 12)
        _make_auto_zip(self.root, "2026-11-20T05-00-00Z-auto.zip", age_hours=8)
        self.assertEqual(check_backups(self.root), [])

    def test_threshold_ordering(self):
        self.assertLess(BACKUP_WARN_HOURS, BACKUP_CRITICAL_HOURS)


if __name__ == "__main__":
    unittest.main()
