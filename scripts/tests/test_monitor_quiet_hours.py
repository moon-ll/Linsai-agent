#!/usr/bin/env python3
"""
test_monitor_quiet_hours.py — lifecycle_monitor 夜间静默窗口拦截回归测试（v6.9.82）

覆盖缺陷：
    v6.9.68 引入夜间静默（22:00-08:00 只入缓存不发送，次日工作时段
    补发），但 run_monitor 通知路径的实现只把 `quiet` 用于拦截
    `notified` 计数，`_send_feishu` 的实际发送未被拦截：

      1. 静默窗口内只要某告警 key 通过 _should_notify 去重（新异常或
         24h 冷却到期），_send_feishu 照常执行
      2. 用户在深夜收到飞书告警，与设计相悖
      3. 发送成功后 _mark_notified 消耗 24h 冷却，次日工作时段也
         不会补发——"次日补发"语义同时失效
      4. notified_count=0 与"发送成功"日志并存，观测口径自相矛盾

    实际触发场景（logs/linsai.log.2026-08-30 / linsai.log 实证）：
    08-30 22:00:37、23:00:47、08-31 00:00:56、03:00:26、07:00:04
    共 5 次静默窗口内"飞书通知发送成功"，均紧跟"只入缓存不发送通知"。

修复：
    run_monitor 在 `not quiet and _send_feishu(...)` 同时满足时才发送
    与标记。静默窗口内不发送、不标记，次日首个非静默运行经
    _should_notify 自然补发同批异常。

注意：
    本测试不调用真实 lark-cli，桩化 _in_quiet_hours / _send_feishu，
    只验证通知门控语义。
"""

import json
import sys
import shutil
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env


class MonitorQuietHoursTests(TestSuite):
    def __init__(self):
        super().__init__("monitor 夜间静默窗口拦截测试")
        self.tmp_root = None
        self.monitor = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)

        # 强制重新导入 lifecycle_monitor，避免缓存污染
        for mod_name in list(sys.modules.keys()):
            if mod_name == "lifecycle_monitor":
                del sys.modules[mod_name]

        self.monitor = importlib.import_module("lifecycle_monitor")

        # 隔离路径
        self.monitor.KANBAN_PATH = self.tmp_root / "memory" / "system-kanban.json"
        self.monitor.ALERT_CACHE_PATH = self.tmp_root / "memory" / "monitor-alert-cache.json"

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _read_cache(self) -> dict:
        if not self.monitor.ALERT_CACHE_PATH.exists():
            return {"alerts": {}}
        with open(self.monitor.ALERT_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _reset_cache(self):
        with open(self.monitor.ALERT_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({"alerts": {}}, f)

    def _stub_monitor(self):
        """桩化数据读取层，让 run_monitor 只走到通知发送路径。"""
        anomalies = [{
            "type": "stalled",
            "proposal_id": "test-prop",
            "job_id": "",
            "hours": 99,
            "done": 0,
            "total": 25,
            "message": "测试告警：课题 test-prop 停滞 99h",
        }]
        stats = [{"proposal_id": "test-prop", "done": 0, "failed": 0,
                  "pending": 25, "running": 0}]
        # v7.3.44: _check_proposals 增加 dry_run 形参（发现即消化机制）；
        # 同步补桩 r1 启动告警/评审团请求（读真实 memory 数据会泄漏进单测）
        self.monitor._check_proposals = lambda dry_run=False: (stats, anomalies)
        self.monitor._check_cron_status = lambda: None
        self.monitor._check_zero_progress = lambda stats: None
        self.monitor._check_health_signals = lambda: None
        self.monitor._auto_heal_negative_feedback = lambda: []
        self.monitor._run_human_queue_step = lambda: None
        self.monitor._check_r1_start_failures = lambda: []
        self.monitor._check_new_panel_requests = lambda: []
        self.monitor._update_kanban = lambda stats, focus: None
        self.monitor.get_current_focus = lambda: None

    def run_tests(self):
        alert_key = "stalled:test-prop:"

        # ================================================================
        # 测试 1（核心回归）: 静默窗口内不得调用 _send_feishu
        # ================================================================
        self._stub_monitor()
        self._reset_cache()
        self.monitor._in_quiet_hours = lambda: True
        send_calls = []
        self.monitor._send_feishu = lambda title, content: (
            send_calls.append(title), True)[1]

        result = self.monitor.run_monitor(dry_run=False)
        cache = self._read_cache()

        self.assert_true(
            len(send_calls) == 0,
            "静默窗口内不应调用 _send_feishu（v6.9.82 前会深夜真实发送）",
            f"实际调用 {len(send_calls)} 次",
        )
        self.assert_true(
            alert_key not in cache.get("alerts", {}),
            "静默窗口内不应标记告警为已通知（否则消耗 24h 冷却，次日不补发）",
            f"实际 alerts: {cache.get('alerts', {})}",
        )
        self.assert_eq(
            result.get("notified_count"),
            0,
            "静默窗口内 notified_count 应为 0（与不发送一致）",
        )

        # ================================================================
        # 测试 2（核心回归）: 静默窗口内 _should_notify 仍为 True，
        # 保证次日首个非静默运行能自然补发
        # ================================================================
        can_notify_next_day = self.monitor._should_notify(alert_key)
        self.assert_true(
            can_notify_next_day,
            "静默窗口跳过后告警应仍可通知（次日工作时段补发的语义基础）",
            f"_should_notify 返回: {can_notify_next_day}",
        )

        # ================================================================
        # 测试 3（核心回归）: 同批异常在次日非静默运行中补发成功
        # 失败→静默→非静默 的完整链路
        # ================================================================
        self.monitor._in_quiet_hours = lambda: False
        result2 = self.monitor.run_monitor(dry_run=False)
        cache2 = self._read_cache()

        self.assert_true(
            len(send_calls) == 1,
            "非静默运行应补发静默窗口内积累的异常",
            f"实际调用 {len(send_calls)} 次",
        )
        self.assert_true(
            alert_key in cache2.get("alerts", {}),
            "补发成功后必须标记告警为已通知（保证去重生效）",
            f"实际 alerts: {cache2.get('alerts', {})}",
        )
        self.assert_eq(
            result2.get("notified_count"),
            1,
            "非静默补发后 notified_count 应为 1",
        )

        # ================================================================
        # 测试 4（非静默基线）: 工作时段行为不变——发送+标记
        # ================================================================
        self._reset_cache()
        send_calls.clear()
        result3 = self.monitor.run_monitor(dry_run=False)
        cache3 = self._read_cache()

        self.assert_true(
            len(send_calls) == 1,
            "非静默窗口应正常发送告警",
            f"实际调用 {len(send_calls)} 次",
        )
        self.assert_true(
            alert_key in cache3.get("alerts", {}),
            "非静默发送成功后应标记已通知",
            f"实际 alerts: {cache3.get('alerts', {})}",
        )
        self.assert_eq(
            result3.get("notified_count"),
            1,
            "非静默发送后 notified_count 应为 1",
        )

        # ================================================================
        # 测试 5（dry-run 基线）: dry_run 永不发送（原有语义不回归）
        # ================================================================
        self._reset_cache()
        send_calls.clear()
        result4 = self.monitor.run_monitor(dry_run=True)
        cache4 = self._read_cache()

        self.assert_true(
            len(send_calls) == 0,
            "dry_run 不应发送通知",
            f"实际调用 {len(send_calls)} 次",
        )
        self.assert_true(
            alert_key not in cache4.get("alerts", {}),
            "dry_run 不应标记已通知",
            f"实际 alerts: {cache4.get('alerts', {})}",
        )
        self.assert_eq(
            result4.get("notified_count"),
            0,
            "dry_run 的 notified_count 应为 0",
        )


if __name__ == "__main__":
    suite = MonitorQuietHoursTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    s = suite.summary()
    print(f"\n{'✓' if s['failed'] == 0 else '✗'} {s['name']}: {s['passed']}/{s['total']} 通过")
    for r in s["results"]:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if s['failed'] == 0 else 1)
