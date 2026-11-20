# -*- coding: utf-8 -*-
"""harness_metrics 六路采集回归测试（v8.0.41）。

覆盖动机：48h 主动推进期半点轮以本脚本为数据入口，采集口径错了
会把优化轮引向假问题。用临时目录 + 打桩验证核心计算：
课题漏斗（含状态漂移）、step_usage 24h 跨月窗口聚合、告警推导、
备份年龄、fail-open（坏源不炸整体）。

零 LLM / 零 hermes / 零真实数据目录触碰。
"""
import json
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from harness_metrics import (  # noqa: E402
    BACKUP_CRITICAL_HOURS,
    DISTILL_BACKLOG_LIMIT,
    collect_backup,
    collect_step_usage,
    collect_topics,
    derive_alerts,
)


def _utc(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class TestCollectTopics(unittest.TestCase):
    """课题漏斗：fs 计数为真相源，索引 stage 漂移要报。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_fs_counts_and_drift(self):
        for dom, ids in (
            ("ready", ["topic-a", "topic-b"]),
            ("active", ["topic-c"]),
            ("archive", ["old-1"]),
        ):
            (self.root / "research_topics" / dom).mkdir(parents=True, exist_ok=True)
            for tid in ids:
                (self.root / "research_topics" / dom / tid).mkdir()
        # 索引说 topic-a 在 ready（目录在，无漂移），topic-x 索引 active 但目录缺失（漂移）
        (self.root / "research_topics" / "_topics.json").write_text(
            json.dumps(
                {
                    "topics": {
                        "topic-a": {"stage": "ready", "updated_at": "2026-11-20T00:00:00Z"},
                        "topic-x": {"stage": "active", "updated_at": "2026-11-19T00:00:00Z"},
                    },
                    "rejected": [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        t = collect_topics(self.root)
        self.assertEqual(t["fs_counts"]["ready"], 2)
        self.assertEqual(t["fs_counts"]["active"], 1)
        self.assertEqual(t["fs_counts"]["archive"], 1)
        self.assertEqual(t["stage_drift"], ["topic-x: 索引=active 目录缺失"])
        self.assertEqual(t["ready_count"], 1)
        self.assertIsNotNone(t["ready_oldest_days"])


class TestCollectStepUsage(unittest.TestCase):
    """step_usage 24h 跨月窗口聚合与坏行跳过。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.usage = Path(self._tmp.name) / "usage"
        self.usage.mkdir(parents=True)
        self.addCleanup(self._tmp.cleanup)

    def _line(self, ts: str, success: bool = True, tokens: int = 10) -> str:
        return json.dumps(
            {
                "ts": ts, "kind": "hermes", "name": "researcher",
                "success": success, "elapsed_s": 2.5,
                "prompt_tokens": tokens, "completion_tokens": tokens,
                "tokens_estimated": False,
            },
            ensure_ascii=False,
        )

    def test_window_and_month_boundary(self):
        now = datetime(2026, 12, 1, 6, 0, 0, tzinfo=timezone.utc)
        in_window = [
            (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            (now - timedelta(hours=23)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            (now - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"),  # 边界含
        ]
        out_window = [
            (now - timedelta(hours=25)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            (now - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        ]
        # 跨月：now=12-01 06:00，25h 前落在 11-30，属于上月分片
        nov = self.usage / "step-usage-2026-11.jsonl"
        dec = self.usage / "step-usage-2026-12.jsonl"
        dec.write_text("\n".join([self._line(t) for t in in_window]) + "\n", encoding="utf-8")
        nov.write_text("\n".join([self._line(t) for t in out_window]) + "\nnot-json\n", encoding="utf-8")
        su = collect_step_usage(self.usage, hours=24.0, now=now)
        self.assertEqual(su["calls"], 3)
        self.assertEqual(su["success"], 3)
        self.assertEqual(su["success_rate"], 1.0)
        self.assertEqual(su["tokens_total"], 60)
        self.assertEqual(su["malformed_lines_skipped"], 1)
        self.assertEqual(su["by_kind"].get("hermes"), 3)

    def test_failure_counting(self):
        now = datetime(2026, 11, 20, 12, 0, 0, tzinfo=timezone.utc)
        shard = self.usage / "step-usage-2026-11.jsonl"
        shard.write_text(
            "\n".join(
                [
                    self._line((now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"), success=True),
                    self._line((now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"), success=False),
                ]
            ),
            encoding="utf-8",
        )
        su = collect_step_usage(self.usage, hours=24.0, now=now)
        self.assertEqual(su["failed"], 1)
        self.assertEqual(su["success_rate"], 0.5)


class TestCollectBackup(unittest.TestCase):
    """备份年龄：新鲜/缺失/分级的原料计算。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _make_zip(self, name: str, age_hours: float) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        p = self.root / name
        p.write_text("stub", encoding="utf-8")
        ts = time.time() - age_hours * 3600.0
        os.utime(p, (ts, ts))
        return p

    def test_latest_age(self):
        self._make_zip("2026-11-19T05-00-00Z-auto.zip", age_hours=40)
        p = self._make_zip("2026-11-20T05-00-00Z-auto.zip", age_hours=10)
        b = collect_backup(self.root)
        self.assertEqual(b["latest"], p.name)
        self.assertAlmostEqual(b["age_hours"], 10, delta=0.2)
        self.assertEqual(b["count"], 2)

    def test_missing_dir(self):
        b = collect_backup(self.root / "nope")
        self.assertIsNone(b["latest"])
        self.assertIn("issue", b)


class TestDeriveAlerts(unittest.TestCase):
    """告警推导：push 提示 / 蒸馏积压 / 成功率地板 / 干净快照零告警。"""

    def test_push_alert(self):
        alerts = derive_alerts({"git": {"ahead": 878, "behind": 0}})
        self.assertTrue(any("push" in a for a in alerts))

    def test_distill_backlog(self):
        alerts = derive_alerts({"git": {}, "kb": {"distill_remaining": DISTILL_BACKLOG_LIMIT + 1}})
        self.assertTrue(any("蒸馏积压" in a for a in alerts))

    def test_success_rate_floor(self):
        snap = {"git": {}, "step_usage_24h": {"calls": 10, "success_rate": 0.5}}
        self.assertTrue(any("成功率" in a for a in derive_alerts(snap)))
        snap_ok = {"git": {}, "step_usage_24h": {"calls": 10, "success_rate": 1.0}}
        self.assertFalse(any("成功率" in a for a in derive_alerts(snap_ok)))

    def test_incidents_48h_alert(self):
        snap = {"git": {}, "cron": {"incidents_recent_48h": 2, "incidents_total": 20}}
        self.assertTrue(any("incidents" in a for a in derive_alerts(snap)))
        snap_old = {"git": {}, "cron": {"incidents_recent_48h": 0, "incidents_total": 20}}
        self.assertFalse(any("incidents" in a for a in derive_alerts(snap_old)))

    def test_clean_snapshot_no_alert(self):
        snap = {
            "git": {"ahead": 0, "behind": 0},
            "topics": {},
            "backup": {"age_hours": 5.0},
            "kb": {"distill_remaining": 100, "methods_backfill_pending": 0},
            "cron": {"incidents_recent_48h": 0, "incidents_total": 20, "paused": []},
            "step_usage_24h": {"calls": 3, "success_rate": None},
        }
        self.assertEqual(derive_alerts(snap), [])


if __name__ == "__main__":
    unittest.main()
