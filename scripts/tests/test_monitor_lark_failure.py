#!/usr/bin/env python3
"""
test_monitor_lark_failure.py — lifecycle_monitor 告警"自我吞掉"回归测试（v6.8.17）

覆盖缺陷：
    lifecycle_monitor.py 在异常通知路径中先调用 _mark_notified 再调用
    _send_feishu。当 lark-cli 不可用（hermes context 未绑定 / 飞书认证失败 /
    exit != 0）时：
      1. _send_feishu 返回 False（仅记录 warning）
      2. 但 _mark_notified 已经把 alert_key 写入 monitor-alert-cache.json，
         并设置 last_sent=now_utc()
      3. 下次（同 4h ALERT_DEDUP_WINDOW 内）监控检测到相同 anomaly 时，
         _should_notify 返回 False，不再尝试发送
      4. 用户在 4h+ 时间内完全收不到该异常告警，直到窗口过期

    实际触发场景：2026-08-09 01:00:02 monitor 报"lark-cli 发送失败
    (exit=3): ... not bound to it"，但 monitor-alert-cache 仍被标记。

修复：
    lifecycle_monitor.py run_monitor 只在 _send_feishu 返回 True 时才调用
    _mark_notified，确保告警"未送达"时不会占用去重窗口。

注意：
    本测试不调用真实 lark-cli，不连飞书，只验证 monitor 的告警去重语义。
    直接调用 run_monitor 的"通知路径"，桩化 _send_feishu。
"""

import json
import sys
import shutil
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env


class MonitorLarkFailureTests(TestSuite):
    def __init__(self):
        super().__init__("monitor lark 失败告警去重测试")
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
        # v6.8.53: 隔离健康感知层——_check_health_signals 经 health_sensor 读
        # 真实 KB/熔断数据，真实 conn(0.45)<0.50 会额外产生告警，使
        # notified_count=1 的断言漂移为 2（flake）。本套件聚焦通知去重语义。
        self.monitor._check_health_signals = lambda: None
        # v6.9.82: 固定为非静默时段——夜间静默（22:00-08:00）会拦截发送与
        # notified 计数，若不桩化，本套件在真实夜间运行时 notified_count=1
        # 与"发送成功后标记"断言会随时钟漂移。静默语义由
        # test_monitor_quiet_hours.py 专职覆盖。
        self.monitor._in_quiet_hours = lambda: False

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _read_cache(self) -> dict:
        if not self.monitor.ALERT_CACHE_PATH.exists():
            return {"alerts": {}}
        with open(self.monitor.ALERT_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _stub_proposal_check(self, anomalies: list, stats: list):
        """桩化 _check_proposals 和 _check_cron_status / _check_zero_progress
        让 run_monitor 只走到"通知发送"路径。"""
        # v7.3.44: _check_proposals 增加 dry_run 形参（发现即消化机制）
        self.monitor._check_proposals = lambda dry_run=False: (stats, anomalies)
        self.monitor._check_cron_status = lambda: None
        self.monitor._check_zero_progress = lambda stats: None
        # v6.9.68 补桩：健康信号/负反馈自愈/人工队列同样读真实数据——
        # 实测真实 human_queue 的 bsv 催办（>72h）泄漏进本测试致
        # notified_count 期望 1 实际 2。单元测试只测通知路径本身。
        self.monitor._check_health_signals = lambda: None
        self.monitor._auto_heal_negative_feedback = lambda: []
        self.monitor._run_human_queue_step = lambda: None
        # v7.3.44 补桩：r1 启动告警（v7.1.8）与评审团请求（v7.2.0）
        # 同样读真实 memory 数据——11-05 实测 5 个 r=0 课题排队超 24h
        # 泄漏进本测试致 notified_count 期望 1 实际 6，且 r1 检查的
        # 去重写回会污染真实 memory/r1-start-alerts.json。
        self.monitor._check_r1_start_failures = lambda: []
        self.monitor._check_new_panel_requests = lambda: []
        # 桩化 _update_kanban 和 get_current_focus（避免依赖真实数据）
        self.monitor._update_kanban = lambda stats, focus: None
        self.monitor.get_current_focus = lambda: None

    def run_tests(self):
        # ================================================================
        # 测试 1（核心回归）: lark 失败时不应该标记告警为已通知
        # ================================================================
        # 桩化 monitor 内部函数，走"通知发送"路径
        anomalies = [{
            "type": "stalled",
            "proposal_id": "test-prop",
            "job_id": "",
            "hours": 99,
            "done": 0,
            "total": 25,
            "message": "测试告警：课题 test-prop 停滞 99h",
        }]
        stats = [{"proposal_id": "test-prop", "done": 0, "failed": 0, "pending": 25, "running": 0}]
        self._stub_proposal_check(anomalies, stats)
        # 桩化 _send_feishu：返回 False（模拟 lark-cli 失败）
        self.monitor._send_feishu = lambda title, content: False

        # 直接调用 run_monitor 的通知路径（绕过 dry_run，因为我们要真触发）
        # run_monitor 在 anomalies 不为空且 not dry_run 时才发送。
        # 桩化 dry_run=False 以走真实路径
        result = self.monitor.run_monitor(dry_run=False)
        cache = self._read_cache()
        alert_key = "stalled:test-prop:"

        self.assert_true(
            alert_key not in cache.get("alerts", {}),
            "lark 发送失败时不应标记告警为已通知（避免 4h 去重窗口吞掉真实告警）",
            f"实际 alerts: {cache.get('alerts', {})}",
        )
        self.assert_eq(
            result.get("notified_count"),
            1,
            "notified_count 仍应记录本次尝试（供监控调试）",
        )

        # ================================================================
        # 测试 2（核心回归）: lark 成功时必须标记告警为已通知
        # ================================================================
        # 清空 cache
        with open(self.monitor.ALERT_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({"alerts": {}}, f)

        # 桩化 _send_feishu：返回 True（模拟成功）
        self.monitor._send_feishu = lambda title, content: True
        self.monitor.run_monitor(dry_run=False)
        cache = self._read_cache()

        self.assert_true(
            alert_key in cache.get("alerts", {}),
            "lark 发送成功时必须标记告警为已通知（保证去重生效）",
            f"实际 alerts: {cache.get('alerts', {})}",
        )

        # ================================================================
        # 测试 3（端到端）: 失败 → 成功 的完整链路
        # ================================================================
        # 清空 cache
        with open(self.monitor.ALERT_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({"alerts": {}}, f)

        # 第一次：lark 失败
        self.monitor._send_feishu = lambda title, content: False
        self.monitor.run_monitor(dry_run=False)
        cache_after_first = self._read_cache()

        # 第二次：lark 成功（同一 anomaly key）
        self.monitor._send_feishu = lambda title, content: True
        self.monitor.run_monitor(dry_run=False)
        cache_after_second = self._read_cache()

        self.assert_true(
            alert_key not in cache_after_first.get("alerts", {}),
            "第一次失败后 cache 不应包含告警 key",
            f"实际: {cache_after_first.get('alerts', {})}",
        )
        self.assert_true(
            alert_key in cache_after_second.get("alerts", {}),
            "第二次成功后 cache 必须包含告警 key",
            f"实际: {cache_after_second.get('alerts', {})}",
        )

        # ================================================================
        # 测试 4（反证）: 失败后 _should_notify 应返回 True
        # 修复的核心价值：告警不被自我吞掉，下次仍能尝试发送
        # ================================================================
        # 清空 cache
        with open(self.monitor.ALERT_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump({"alerts": {}}, f)

        # lark 失败
        self.monitor._send_feishu = lambda title, content: False
        self.monitor.run_monitor(dry_run=False)

        can_notify_again = self.monitor._should_notify(alert_key)
        self.assert_true(
            can_notify_again,
            "失败后告警应能再次触发发送（不被自我吞掉）",
            f"_should_notify 返回: {can_notify_again}",
        )

        # ================================================================
        # 测试 5（新增）: _resolve_lark_cli 在插件升级（1.0.3→1.0.4）后
        # 仍能解析到实际已安装的 lark-cli，避免硬编码路径静默失效
        # ================================================================
        fake_plugin = self.tmp_root / "lark_plugin"
        fake_plugin.mkdir(parents=True, exist_ok=True)
        for ver in ("1.0.3", "1.0.4"):
            (fake_plugin / ver / "bin").mkdir(parents=True, exist_ok=True)
            (fake_plugin / ver / "bin" / "lark-cli").write_text("", encoding="utf-8")

        orig_dir = self.monitor._LARK_PLUGIN_DIR
        self.monitor._LARK_PLUGIN_DIR = fake_plugin
        try:
            resolved = self.monitor._resolve_lark_cli()
        finally:
            self.monitor._LARK_PLUGIN_DIR = orig_dir
        self.assert_true(
            resolved.endswith("/1.0.4/bin/lark-cli"),
            "插件升级(1.0.3→1.0.4)后 _resolve_lark_cli 应解析到最高已安装版本",
            f"实际: {resolved}",
        )


if __name__ == "__main__":
    suite = MonitorLarkFailureTests()
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
    sys.exit(0 if s["failed"] == 0 else 1)