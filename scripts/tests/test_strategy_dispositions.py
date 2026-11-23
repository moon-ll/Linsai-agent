#!/usr/bin/env python3
"""test_strategy_dispositions.py — 策略裁决账本回归测试（v7.2.43）。

覆盖：
    1. 裁决后聚合不再复活（此前 3 次复发的根因：run_human_queue 重建
       快照覆盖 status/resolution 字段）
    2. suggested 值变化时重新入队（防陈旧裁决永久压制新建议）
    3. record_strategy_disposition 写入即清聚合缓存

零 LLM：strategy_optimizer 以 stub 模块注入。
"""

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from test_runner import TestSuite, create_isolated_env

REAL_ROOT = SCRIPTS_DIR.parent


class StrategyDispositionTests(TestSuite):
    def __init__(self):
        super().__init__("策略裁决账本测试（v7.2.43）")
        self.tmp_root = None
        self._saved = {}

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "memory" / "config").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "memory" / ".cache").mkdir(parents=True, exist_ok=True)

        for k in list(sys.modules):
            if k in ("human_queue", "strategy_optimizer"):
                self._saved[k] = sys.modules.pop(k)

        sys.path.insert(0, str(REAL_ROOT / "scripts"))
        import human_queue
        human_queue.MEMORY_DIR = self.tmp_root / "memory"
        human_queue.HUMAN_QUEUE_PATH = self.tmp_root / "memory" / "human-queue.json"
        human_queue._STRATEGY_CACHE = self.tmp_root / "memory" / ".cache" / "hq-strategy-cache.json"
        human_queue._STRATEGY_DISPOSITIONS_PATH = (
            self.tmp_root / "memory" / "config" / "strategy-dispositions.json")
        self._hq = human_queue

        # stub strategy_optimizer：固定建议 critic_timeout 300→450
        mod = type(sys)("strategy_optimizer")
        mod.AUTO_APPLY_KEYS = []
        mod.suggest_strategies = lambda: {
            "current": {"critic_timeout": 300},
            "suggested": {"critic_timeout": 450},
            "risk": "medium",
        }
        sys.modules["strategy_optimizer"] = mod
        # 清缓存保证每次聚合重算
        try:
            human_queue._STRATEGY_CACHE.unlink()
        except FileNotFoundError:
            pass

    def teardown(self):
        sys.modules.pop("strategy_optimizer", None)
        sys.modules.pop("human_queue", None)
        for k, v in self._saved.items():
            sys.modules[k] = v
        import shutil
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        self._test_disposition_suppresses_revival()
        self._test_new_suggested_value_reenters()
        self._test_record_clears_cache()

    def _test_disposition_suppresses_revival(self):
        """裁决后多次聚合均不复活（核心回归：防第 4 次复活）。"""
        hq = self._hq
        from datetime import datetime, timezone
        now = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)

        ok = hq.record_strategy_disposition(
            "critic_timeout", "auto_resolved",
            resolution="建议已过期：实际 timeout 已是 1200-1500s",
            suggested=450)
        self.assert_true(ok, "裁决写入成功")

        items1 = hq._pending_strategy_suggestions(now)
        self.assert_eq(
            len([i for i in items1 if i.get("proposal_id") == "global:strategy:critic_timeout"]),
            0, "裁决后聚合不再入队")

        # 二次聚合（模拟 monitor 下一次 tick 重建快照）仍不复活
        try:
            hq._STRATEGY_CACHE.unlink()
        except FileNotFoundError:
            pass
        items2 = hq._pending_strategy_suggestions(now)
        self.assert_eq(
            len([i for i in items2 if i.get("proposal_id") == "global:strategy:critic_timeout"]),
            0, "第二次聚合仍不复活（此前 3 次复发的场景）")

    def _test_new_suggested_value_reenters(self):
        """建议值变化 → 重新入队（防陈旧裁决永久压制）。"""
        hq = self._hq
        from datetime import datetime, timezone
        now = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)
        hq.record_strategy_disposition("critic_timeout", "rejected",
                                       resolution="旧的 450 不要", suggested=450)
        # strategy_optimizer 建议变为 600
        sys.modules["strategy_optimizer"].suggest_strategies = lambda: {
            "current": {"critic_timeout": 300},
            "suggested": {"critic_timeout": 600},
            "risk": "medium",
        }
        try:
            hq._STRATEGY_CACHE.unlink()
        except FileNotFoundError:
            pass
        items = hq._pending_strategy_suggestions(now)
        matches = [i for i in items if i.get("proposal_id") == "global:strategy:critic_timeout"]
        self.assert_eq(len(matches), 1, "新建议值重新入队")
        self.assert_eq(matches[0].get("suggested"), 600, "入队的是新值 600")

    def _test_record_clears_cache(self):
        """record_strategy_disposition 成功后立即失效聚合缓存。"""
        hq = self._hq
        hq._STRATEGY_CACHE.parent.mkdir(parents=True, exist_ok=True)
        hq._STRATEGY_CACHE.write_text(
            json.dumps({"at": "2099-01-01T00:00:00Z", "items": [{"stale": True}]}),
            encoding="utf-8")
        hq.record_strategy_disposition("writer_timeout", "applied",
                                       resolution="测试", suggested=900)
        self.assert_true(
            not hq._STRATEGY_CACHE.exists(),
            "裁决写入后聚合缓存被清除")


if __name__ == "__main__":
    import time
    suite = StrategyDispositionTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report
    print_report([suite])
    sys.exit(0 if suite.summary()["failed"] == 0 else 1)
