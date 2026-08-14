#!/usr/bin/env python3
"""
test_heartbeat_kanban_merge.py — repair 心跳互查绑定与看板合并写回归测试

验证 v6.9.1 两个修复:

1. _check_monitor_heartbeat 绑定缺失（v6.8.50 引入函数但漏绑到
   LifecycleCronController，run_repair 每 6h 调用 self._check_monitor_heartbeat
   触发 AttributeError，机制自上线以来从未生效。
   日志实证: 2026-08-15T00:00:52Z
   "[repair] monitor 心跳互查异常: 'LifecycleCronController' object has no
    attribute '_check_monitor_heartbeat'"）

2. _update_kanban 整文件替换剥离其他写入方的键——工作时段内微调度器每 5 分钟
   重写 system-kanban.json，alerts（monitor 告警区）、hourly_monitor（心跳
   时间戳）、kb_metrics（趋势雷达/覆盖率）全部丢失，直到下一次整点 monitor
   合并写才恢复。v6.9.1 改为合并写（先读现有再覆盖自有键）。

验证点:
    - LifecycleCronController 类上存在 _check_monitor_heartbeat 属性
    - 心跳新鲜（<=2h）返回 None；心跳丢失（>2h）返回告警并落盘看板 alerts
    - dry_run=True 时不落盘
    - _update_kanban 写入后 alerts/kb_metrics/hourly_monitor 键存活
"""

import sys
import json
import shutil
import importlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock

from test_runner import TestSuite, create_isolated_env, patch_module_root


def _utc_iso(dt: datetime) -> str:
    """UTC ISO 格式（Z 结尾），与 now_utc() 输出一致。"""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class HeartbeatKanbanMergeTests(TestSuite):
    def __init__(self):
        super().__init__("心跳互查绑定与看板合并写测试")
        self.tmp_root = None
        self.orch = None
        self.ms = None
        self.ctrl_mod = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for sub in ["drafts", "optimizing", "pending_review", "archived", "memory"]:
            (self.tmp_root / "research_proposals" / sub).mkdir(parents=True, exist_ok=True) \
                if sub != "memory" else (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)

        # 强制重新导入，避免模块级常量指向真实工作区
        for mod_name in list(sys.modules.keys()):
            if mod_name == "lifecycle" or mod_name.startswith("lifecycle.") \
                    or mod_name in ["paths", "common", "proposal_lifecycle",
                                    "proposal_sections", "hermes_bridge"]:
                del sys.modules[mod_name]

        self.orch = importlib.import_module("lifecycle.orchestrator")
        self.ms = importlib.import_module("lifecycle.micro_scheduler")
        self.ctrl_mod = importlib.import_module("lifecycle.controller")

        for mod in ("lifecycle.orchestrator", "lifecycle.micro_scheduler",
                    "lifecycle.controller", "paths", "common"):
            patch_module_root(mod, self.tmp_root)
        import paths
        paths.PROJECT_ROOT = self.tmp_root

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ── 工具 ──

    def _kanban_path(self) -> Path:
        return self.tmp_root / "memory" / "system-kanban.json"

    def _write_kanban(self, data: dict) -> None:
        self._kanban_path().write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_kanban(self) -> dict:
        return json.loads(self._kanban_path().read_text(encoding="utf-8"))

    # ── 修复 1：心跳互查绑定 ──

    def _test_heartbeat_bound_to_controller(self):
        """LifecycleCronController 类上必须存在 _check_monitor_heartbeat。

        回归点：v6.8.50 在 orchestrator 定义了函数但漏绑到 controller 类，
        run_repair 内 self 调用每 6h 抛 AttributeError。
        """
        cls = self.ctrl_mod.LifecycleCronController
        self.assert_true(
            hasattr(cls, "_check_monitor_heartbeat"),
            "类绑定存在",
            "LifecycleCronController 缺少 _check_monitor_heartbeat 绑定（v6.9.1 修复项）",
        )

    def _test_heartbeat_fresh_returns_none(self):
        """心跳新鲜（1 分钟前）→ 返回 None 不告警。"""
        self._write_kanban({
            "hourly_monitor": {"timestamp": _utc_iso(datetime.now(timezone.utc) - timedelta(minutes=1))},
        })
        mock_self = MagicMock()
        result = self.orch._check_monitor_heartbeat(mock_self, dry_run=True)
        self.assert_eq(result, None, "新鲜心跳返回 None")

    def _test_heartbeat_stale_alerts_and_persists(self):
        """心跳丢失 3h → 返回告警；dry_run=False 落盘看板 alerts。"""
        self._write_kanban({
            "hourly_monitor": {"timestamp": _utc_iso(datetime.now(timezone.utc) - timedelta(hours=3))},
        })
        mock_self = MagicMock()
        result = self.orch._check_monitor_heartbeat(mock_self, dry_run=False)

        self.assert_true(result is not None, "丢失心跳返回告警")
        self.assert_eq(result.get("type"), "monitor_heartbeat_lost", "告警类型")
        kanban = self._read_kanban()
        keys = [a.get("key") for a in kanban.get("alerts", [])]
        self.assert_in("monitor_heartbeat_lost::", keys, "告警已落盘看板 alerts")

        # 重复触发 → 复用已有条目并累加 count（去重语义）
        result2 = self.orch._check_monitor_heartbeat(mock_self, dry_run=False)
        self.assert_true(result2 is not None, "再次触发仍返回告警")
        kanban2 = self._read_kanban()
        entry = next(a for a in kanban2.get("alerts", [])
                     if a.get("key") == "monitor_heartbeat_lost::")
        self.assert_eq(entry.get("count"), 2, "重复触发 count 累加")

    def _test_heartbeat_dry_run_no_persist(self):
        """dry_run=True → 返回告警但不落盘。"""
        self._write_kanban({
            "hourly_monitor": {"timestamp": _utc_iso(datetime.now(timezone.utc) - timedelta(hours=5))},
        })
        mock_self = MagicMock()
        result = self.orch._check_monitor_heartbeat(mock_self, dry_run=True)
        self.assert_true(result is not None, "dry_run 仍返回告警对象")
        kanban = self._read_kanban()
        self.assert_eq(kanban.get("alerts"), None, "dry_run 不落盘 alerts")

    def _test_heartbeat_never_run_returns_none(self):
        """看板无 hourly_monitor 记录 → 不重复告警（交给 monitor 自身 cron 检查）。"""
        self._write_kanban({"updated_at": _utc_iso(datetime.now(timezone.utc))})
        mock_self = MagicMock()
        result = self.orch._check_monitor_heartbeat(mock_self, dry_run=False)
        self.assert_eq(result, None, "从未运行过返回 None")

    # ── 修复 2：看板合并写 ──

    def _make_mock_controller(self, pid: str):
        ctrl = MagicMock()
        ctrl._get_proposal_state.return_value = {
            "optimization_rounds": 0,
            "last_score": 0.0,
            "status": "optimizing",
        }
        ctrl._get_jobs.return_value = []
        ctrl._is_proposal_stuck.return_value = False
        ctrl._list_ready_jobs_for_proposal.return_value = []
        return ctrl

    def _test_kanban_merge_preserves_foreign_keys(self):
        """_update_kanban 后 alerts/kb_metrics/hourly_monitor 键必须存活。"""
        self._write_kanban({
            "alerts": [{"key": "stuck:demo", "level": "medium", "message": "demo",
                        "first_seen": "2026-08-14T00:00:00Z", "count": 1,
                        "last_seen": "2026-08-14T00:00:00Z", "resolved_at": None}],
            "hourly_monitor": {"timestamp": _utc_iso(datetime.now(timezone.utc))},
            "kb_metrics": {"coverage_pct": 66.7, "trends_rising": [{"keyword": "moiré", "freq": 9}],
                           "trends_updated_at": "2026-08-14T12:40:00Z"},
        })

        ctrl = self._make_mock_controller("test-alpha-20260101")
        self.ms._update_kanban(
            slot_info=(0, ("00:30", "03:30")),
            focus_pid="test-alpha-20260101",
            optimizing=[{"proposal_id": "test-alpha-20260101"}],
            executed=[],
            self=ctrl,
        )

        kanban = self._read_kanban()
        self.assert_true("alerts" in kanban, "alerts 键存活",
                         "微调度器写入剥离了 monitor 告警区（v6.9.1 修复项）")
        self.assert_true("kb_metrics" in kanban, "kb_metrics 键存活",
                         "微调度器写入剥离了 KB 指标（趋势雷达/覆盖率持久化失效根因）")
        self.assert_true("hourly_monitor" in kanban, "hourly_monitor 键存活",
                         "微调度器写入剥离了 monitor 心跳时间戳")
        self.assert_eq(kanban.get("current", {}).get("focus_proposal"),
                       "test-alpha-20260101", "自有键正常更新")

    def _test_kanban_merge_overwrites_own_keys(self):
        """合并写不得残留自有键的旧值（current/proposals 以本次写入为准）。"""
        self._write_kanban({
            "current": {"focus_proposal": "test-old-20260101", "stale_key": True},
        })
        ctrl = self._make_mock_controller("test-new-20260101")
        self.ms._update_kanban(
            slot_info=(1, ("04:00", "08:00")),
            focus_pid="test-new-20260101",
            optimizing=[{"proposal_id": "test-new-20260101"}],
            executed=[],
            self=ctrl,
        )
        kanban = self._read_kanban()
        self.assert_eq(kanban.get("current", {}).get("focus_proposal"),
                       "test-new-20260101", "自有键被新值覆盖")
        self.assert_eq(kanban.get("current", {}).get("slot"), "04:00-08:00", "时段写入正确")

    def _test_kanban_first_write_still_works(self):
        """看板不存在时首次写入不应报错（合并读返回空 dict 直接落盘）。"""
        ctrl = self._make_mock_controller("test-beta-20260101")

        def _call():
            self.ms._update_kanban(
                slot_info=None,
                focus_pid=None,
                optimizing=[],
                executed=[],
                self=ctrl,
            )

        self.assert_no_exception(_call, "首次写入无异常")
        kanban = self._read_kanban()
        self.assert_true("updated_at" in kanban, "首次写入产生看板结构")

    def run_tests(self):
        self._test_heartbeat_bound_to_controller()
        self._test_heartbeat_fresh_returns_none()
        self._test_heartbeat_stale_alerts_and_persists()
        self._test_heartbeat_dry_run_no_persist()
        self._test_heartbeat_never_run_returns_none()
        self._test_kanban_merge_preserves_foreign_keys()
        self._test_kanban_merge_overwrites_own_keys()
        self._test_kanban_first_write_still_works()
