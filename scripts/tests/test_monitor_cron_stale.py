#!/usr/bin/env python3
"""
test_monitor_cron_stale.py — lifecycle_monitor cron 陈旧检测修复测试（v6.8.34）

覆盖缺陷：
    lifecycle_monitor._check_cron_status 读取 cron 的 last_run_at 键，
    但 hermes_bridge.cron_list_profile 实际返回 last_run 键，导致
    last_run 恒为空 → 所有关键 cron 被误报"从未执行"（cron_stale 假告警）。

    同时，固定 2h 陈旧阈值对每日(24h)/每6h 调度的 cron 恒误报，
    改为按各 cron 自身调度间隔估算阈值（至少 2h）。

修复：
    1. last_run = c.get("last_run") or c.get("last_run_at", "")
    2. 新增 _estimate_cron_interval() 估算调度间隔，threshold = max(2h, 2*interval)

注意：
    本测试不调用 hermes/LLM，仅验证 cron 陈旧判定逻辑。
"""

import sys
import importlib
from datetime import datetime, timezone

from test_runner import TestSuite


class MonitorCronStaleTests(TestSuite):
    def __init__(self):
        super().__init__("monitor cron 陈旧检测修复测试")
        self.monitor = None

    def setup(self):
        # 强制重新导入 lifecycle_monitor，避免缓存污染
        for mod_name in list(sys.modules.keys()):
            if mod_name == "lifecycle_monitor":
                del sys.modules[mod_name]
        self.monitor = importlib.import_module("lifecycle_monitor")

    def _make_cron(self, name, schedule, last_run, created_at):
        return {
            "name": name,
            "schedule": schedule,
            "last_run": last_run,
            "last_run_at": last_run,  # 兼容旧字段
            "created_at": created_at,
            "id": "test-id",
        }

    def run_tests(self):
        # ================================================================
        # 测试 1: _estimate_cron_interval 对三种关键调度返回正确间隔
        # ================================================================
        self.assert_eq(
            self.monitor._estimate_cron_interval("*/15 * * * 1-5"),
            900,
            "每15分钟调度 → 900s",
        )
        self.assert_eq(
            self.monitor._estimate_cron_interval("0 */6 * * *"),
            21600,
            "每6小时调度 → 21600s",
        )
        self.assert_eq(
            self.monitor._estimate_cron_interval("55 8 * * *"),
            86400,
            "每日固定时间调度 → 86400s",
        )
        # 无法解析时回退到保守阈值
        self.assert_eq(
            self.monitor._estimate_cron_interval("not-a-cron"),
            self.monitor.CRON_STALE_THRESHOLD,
            "非法表达式回退到 CRON_STALE_THRESHOLD",
        )

        # ================================================================
        # 测试 2: 键名修复——last_run 有值时不再误报"从未执行"
        # 场景：所有关键 cron 都在正常调度内运行（last_run 近、next 正常），
        #       _check_cron_status 应返回 None（无 cron_stale 告警）。
        # ================================================================
        now = datetime.now(timezone.utc)
        iso = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # 必需前缀齐全（含 weekend + kb-sync），避免 _check_cron_status 先触发 cron_missing
        # v7.2.12 修复（周末专属缺陷）：micro-scheduler 调度须与 cron_manifest
        # 登记值一致（v7.2.1 漂移检测比对 manifest），旧代码按星期动态构造
        # "*/15 * * * 6,0" 在周末触发 cron_drift 假失败。周末场景的正确语义：
        # micro-scheduler 本就不在周末调度（weekend-worker 接管），陈旧判定
        # 走 v6.9.2 星期域免检分支——测试 4 改用全周覆盖的 lc-hourly-monitor。
        from lifecycle.constants import MICRO_SCHEDULER_SCHEDULE
        micro_sched = MICRO_SCHEDULER_SCHEDULE

        def _full_set(overrides):
            # v6.9.98: 周末输入链多轮化——首轮 + 锚点轮 + 夜间轮全部入册，
            # 与 cron_manifest 清单一致（否则拓扑对账报 missing）
            from lifecycle.constants import (
                DEFAULT_WEEKEND_INPUT_SCHEDULE,
                PANEL_REVIEW_CRON_NAME,
                DEFAULT_PANEL_REVIEW_SCHEDULE,
                WEEKEND_INPUT_ANCHOR_CRONS,
                WEEKEND_INPUT_CRON_NAME,
                WEEKEND_INPUT_NIGHT_CRONS,
            )
            base = {
                "lc-micro-scheduler": micro_sched,
                "lc-side-worker": "2-59/5 * * * 1-5",  # v7.3.55 并行试点 side-worker 入册（防拓扑对账误报）
                "lc-repair": "0 */12 * * *",
                "lc-daily-orchestrate": "55 8 * * *",
                "lc-hourly-monitor": "0 * * * *",
                "lc-prompt-optimize": "0 14 * * *",
                # v6.9.99（T2）: lc-retrospective 撤出清单（复盘移入周日反思链），
                # 新增周末收尾汇总与周日蒸馏小批
                "lc-kb-sync": "40 12 * * *",
                "lc-kb-distill": "50 12 * * *",
                "lc-kb-distill-pm": "50 18 * * *",
                "lc-kb-distill-night": "50 2 * * *",  # v7.1.5 凌晨追赶档
                "lc-daily-sync": "0 23 * * *",  # v6.9.5 新增，纳入拓扑清单
                "lc-self-optimize": "30 16 * * *",  # v7.2.65 自迭代窗口入册
                "lc-kb-distill-sunday": "0 20 * * 0",  # v6.9.99（T2）
                "lc-daily-backup": "0 13 * * *",  # v6.9.54 新增，纳入拓扑清单
                "lc-weekend-summary": "0 22 * * 0",  # v6.9.99（T2）
                # v7.2.57: 评审团宿主入册（否则拓扑对账报 missing）
                PANEL_REVIEW_CRON_NAME: DEFAULT_PANEL_REVIEW_SCHEDULE,
                WEEKEND_INPUT_CRON_NAME: DEFAULT_WEEKEND_INPUT_SCHEDULE,
            }
            for _n, _s in list(WEEKEND_INPUT_ANCHOR_CRONS) + list(WEEKEND_INPUT_NIGHT_CRONS):
                base[_n] = _s
            crons = []
            for name, sched in base.items():
                lr = overrides.get(name, iso(now))
                crons.append(self._make_cron(name, sched, lr, "2026-08-01T00:00:00Z"))
            return crons

        crons = _full_set({})

        # 打桩 hermes_bridge.cron_list_profile
        import hermes_bridge as hb
        orig = hb.cron_list_profile
        hb.cron_list_profile = lambda profile="linsai": crons
        try:
            result = self.monitor._check_cron_status()
        finally:
            hb.cron_list_profile = orig

        self.assert_true(
            result is None,
            "所有 cron 正常运行时不应产生 cron_stale 告警",
            f"实际结果: {result}",
        )

        # ================================================================
        # 测试 3: 每日 cron 即使 9h 未运行也不应误报（调度感知阈值）
        # 场景：lc-daily-orchestrate 上次运行 9h 前（每日调度，正常），
        #       旧 2h 阈值会误报；修复后阈值=48h，不应告警。
        # ================================================================
        nine_h_ago = now - __import__("datetime").timedelta(hours=9)
        crons_daily = _full_set({"lc-daily-orchestrate": iso(nine_h_ago)})
        hb.cron_list_profile = lambda profile="linsai": crons_daily
        try:
            result = self.monitor._check_cron_status()
        finally:
            hb.cron_list_profile = orig

        self.assert_true(
            result is None,
            "每日 cron 9h 未运行属正常，不应误报 cron_stale",
            f"实际结果: {result}",
        )

        # ================================================================
        # 测试 4: 真正停滞的 cron（远超调度间隔）应被标记
        # v7.2.12: 陈旧监视名单只有 micro-scheduler/daily-orchestrate/repair
        # 三个前缀；micro-scheduler 的 "1-5" 调度在周末命中 v6.9.2 星期域
        # 免检分支——两种结果都是正确语义，按当天断言：
        #   工作日 → 3h 未运行应告警（threshold=max(2h,2*15min)=2h）
        #   周末   → 免检分支生效返回 None（不误报）
        # ================================================================
        three_h_ago = now - __import__("datetime").timedelta(hours=3)
        crons_stuck = _full_set({"lc-micro-scheduler": iso(three_h_ago)})
        hb.cron_list_profile = lambda profile="linsai": crons_stuck
        try:
            result = self.monitor._check_cron_status()
        finally:
            hb.cron_list_profile = orig

        today_wd = datetime.now().date().weekday()
        if today_wd < 5:
            self.assert_true(
                result is not None and result.get("type") == "cron_stale",
                "工作日：每15分钟 cron 3h 未运行应触发 cron_stale 告警",
                f"实际结果: {result}",
            )
        else:
            self.assert_true(
                result is None,
                "周末：工作日-only cron 走 v6.9.2 星期域免检分支，不应误报",
                f"实际结果: {result}",
            )


if __name__ == "__main__":
    suite = MonitorCronStaleTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        pass
    s = suite.summary()
    print(f"\n{'✓' if s['failed'] == 0 else '✗'} {s['name']}: {s['passed']}/{s['total']} 通过")
    for r in s["results"]:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if s["failed"] == 0 else 1)
