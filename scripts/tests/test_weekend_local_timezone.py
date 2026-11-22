#!/usr/bin/env python3
"""
test_weekend_local_timezone.py — _is_weekend 本地时区口径回归测试（v6.9.44）

背景：_is_weekend 此前用 UTC weekday 判定周末，与业务时区北京时间
（UTC+8）偏差 8 小时。08-24（周一）实测：00:00/06:03 两次 lc-repair
修复扫描 weekend=True（UTC 仍处周日），走周末分支跳过 failed job
重试，前一晚 4 个 attempts=3 failed job 零重试，最早拖到 12:00
repair 才自愈——每周一凌晨固定损失 6-12h 自愈时效。反向 BJ 周六
00:00-08:00（UTC 周五）被误判为工作日，周末阶段补跑窗口错失。

修复：改用本地时间 weekday（与微调度器 cron `*/15 * * * 1-5` 的
本地求值、_weekend_stage_catchup 的 local datetime.now() 同口径）。

用法示例：
    python3 scripts/tests/test_weekend_local_timezone.py
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test_runner import TestSuite

from lifecycle.utils import _is_weekend

BJ = timezone(timedelta(hours=8))
UTC = timezone.utc


class WeekendLocalTimezoneTests(TestSuite):
    """1：周末判定按本地业务时区（北京时间）求值。"""

    def __init__(self):
        super().__init__("周末判定本地时区口径测试（v6.9.44）")

    def run_tests(self):
        # ================================================================
        # 1.1 误判窗口回归：BJ 周一凌晨（UTC 周日）必须是工作日
        #     实测事故时刻：2026-08-24（周一）00:00:59 / 06:03:24 BJ
        # ================================================================
        self.assert_true(
            _is_weekend(datetime(2026, 8, 24, 0, 0, 59, tzinfo=BJ)) is False,
            "BJ 周一 00:00:59（UTC 周日 16:00）应为工作日",
        )
        self.assert_true(
            _is_weekend(datetime(2026, 8, 24, 6, 3, 24, tzinfo=BJ)) is False,
            "BJ 周一 06:03:24（UTC 周日 22:03）应为工作日",
        )
        self.assert_true(
            _is_weekend(datetime(2026, 8, 24, 7, 59, 59, tzinfo=BJ)) is False,
            "BJ 周一 07:59:59（UTC 周日 23:59）应为工作日（窗口边界）",
        )

        # ================================================================
        # 1.2 反向误判窗口：BJ 周六凌晨（UTC 周五）必须是周末
        # ================================================================
        self.assert_true(
            _is_weekend(datetime(2026, 8, 22, 0, 0, 59, tzinfo=BJ)) is True,
            "BJ 周六 00:00:59（UTC 周五 16:00）应为周末",
        )
        self.assert_true(
            _is_weekend(datetime(2026, 8, 22, 7, 59, 59, tzinfo=BJ)) is True,
            "BJ 周六 07:59:59（UTC 周五 23:59）应为周末（窗口边界）",
        )

        # ================================================================
        # 1.3 既有正确区间不回归：周日全天 / 工作日白天
        # ================================================================
        self.assert_true(
            _is_weekend(datetime(2026, 8, 23, 12, 0, 0, tzinfo=BJ)) is True,
            "BJ 周日 12:00 应为周末",
        )
        self.assert_true(
            _is_weekend(datetime(2026, 8, 23, 23, 59, 59, tzinfo=BJ)) is True,
            "BJ 周日 23:59:59 应为周末",
        )
        self.assert_true(
            _is_weekend(datetime(2026, 8, 24, 9, 0, 0, tzinfo=BJ)) is False,
            "BJ 周一 09:00 应为工作日",
        )
        self.assert_true(
            _is_weekend(datetime(2026, 8, 21, 12, 0, 0, tzinfo=BJ)) is False,
            "BJ 周五 12:00 应为工作日",
        )

        # ================================================================
        # 1.4 同一时刻 UTC 与 BJ 表达的一致性：aware datetime 语义
        #     （修复后判定只看本地日历日，两口径描述同一瞬间应同答案）
        # ================================================================
        inst_bj = datetime(2026, 8, 24, 6, 3, 24, tzinfo=BJ)
        inst_utc = inst_bj.astimezone(UTC)
        self.assert_true(
            _is_weekend(inst_bj) == _is_weekend(inst_utc),
            "同一瞬间的 BJ/UTC 两种 aware 表达应给出一致判定",
        )

        # ================================================================
        # 1.5 无参调用可用（run_repair 现网路径）：返回 bool
        # ================================================================
        result = _is_weekend()
        self.assert_true(isinstance(result, bool), "无参调用应返回 bool")


if __name__ == "__main__":
    import unittest
    suite = WeekendLocalTimezoneTests()
    suite.setup()
    try:
        suite.run_tests()
        print("✓ test_weekend_local_timezone 全部通过")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        raise
    finally:
        suite.teardown()
