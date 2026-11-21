#!/usr/bin/env python3
"""
test_monitor_kanban_local.py — lifecycle_monitor 看板本地时间戳测试（v6.8.3-fix10）

覆盖缺陷：
    lifecycle_monitor.py 的 _update_kanban 在每小時监控被触发时，
    只更新 updated_at（UTC）与 hourly_monitor 字段，但忘记同步刷新
    updated_at_local 字段。结果：
    - micro_scheduler 在非工作时隙内不会调用 _update_kanban，
      因此 updated_at_local 会停滞在上次 micro_scheduler 执行时间。
    - 用户运行 `proposal_lifecycle.py --kanban` 时，
      CLI 从 updated_at_local 字段读取"更新时间"，呈现一个远早于真实时间
      的陈旧值，误判链路静默。

修复：
    lifecycle_monitor.py _update_kanban 同时写入 updated_at_local，
    保证两字段同步，使用户看到的"更新时间"始终反映最近一次写入。

注意：
    本测试不调用 hermes/LLM，仅验证看板写入/读取逻辑。
"""

import json
import sys
import shutil
import importlib
import re
from datetime import datetime, timezone
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root


class MonitorKanbanLocalTests(TestSuite):
    def __init__(self):
        super().__init__("monitor 看板本地时间戳测试")
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

        # 隔离 KANBAN_PATH 指向 tmp_root/memory/system-kanban.json
        self.monitor.KANBAN_PATH = self.tmp_root / "memory" / "system-kanban.json"
        self.monitor.ALERT_CACHE_PATH = self.tmp_root / "memory" / "monitor-alert-cache.json"

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _read_kanban(self) -> dict:
        with open(self.monitor.KANBAN_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _seed_kanban(self, fields: dict):
        """种下初始看板内容（含陈旧的 updated_at_local）。"""
        self.monitor.KANBAN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.monitor.KANBAN_PATH, "w", encoding="utf-8") as f:
            json.dump(fields, f, ensure_ascii=False, indent=2)

    def _match_local(self, value: str) -> bool:
        """验证 value 是合法 'YYYY-MM-DD HH:MM:SS' 格式。"""
        return bool(re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", value))

    def run_tests(self):
        # ================================================================
        # 测试 1（核心回归）: monitor._update_kanban 必须同步刷新 updated_at_local
        # 场景：看板里写有陈旧的 12:30:57；现在调一次 _update_kanban，
        #       要求两个字段都被刷成"现在"。
        # ================================================================
        self._seed_kanban({
            "updated_at": "2026-08-05T04:30:57Z",
            "updated_at_local": "2026-08-05 12:30:57",
            "current": {"slot": "08:30-12:30"},
            "proposals": [],
        })

        stats = [
            {"proposal_id": "test-a", "done": 10, "failed": 0, "pending": 5, "running": 0},
        ]
        self.monitor._update_kanban(stats, None)
        kanban = self._read_kanban()

        # 1) updated_at 必须是合法 UTC ISO（不强制等于 now_utc，因为两个调用
        #    之间差几毫秒；只要非空、是 Z-suffix 即可）
        self.assert_true(
            isinstance(kanban.get("updated_at"), str) and kanban["updated_at"].endswith("Z"),
            "updated_at 应是 UTC ISO 字符串",
            f"实际值: {kanban.get('updated_at')!r}",
        )

        # 2) updated_at_local 必须被刷新，不再是陈旧的 12:30:57
        local_after = kanban.get("updated_at_local")
        self.assert_true(
            local_after != "2026-08-05 12:30:57",
            "updated_at_local 必须不再停留在陈旧值 12:30:57",
            f"实际值: {local_after!r}",
        )

        # 3) updated_at_local 必须是合法 'YYYY-MM-DD HH:MM:SS' 格式
        self.assert_true(
            self._match_local(local_after or ""),
            "updated_at_local 必须是合法日期时间格式",
            f"实际值: {local_after!r}",
        )

        # 4) hourly_monitor.timestamp 必须存在且 = updated_at 同一时刻
        self.assert_eq(
            kanban.get("hourly_monitor", {}).get("timestamp"),
            kanban.get("updated_at"),
            "hourly_monitor.timestamp 应与 updated_at 同时刻",
        )

        # ================================================================
        # 测试 2: 即使看板文件原本没有 updated_at_local 字段（历史数据缺失），
        #          monitor._update_kanban 也应正确补上
        # ================================================================
        self._seed_kanban({
            "updated_at": "2026-08-05T04:30:57Z",
            # 不写 updated_at_local —— 模拟文件损坏/老版本遗留
            "current": {"slot": "08:30-12:30"},
            "proposals": [],
        })

        self.monitor._update_kanban(
            [{"proposal_id": "x", "done": 1, "failed": 0, "pending": 0, "running": 0}],
            None,
        )
        kanban = self._read_kanban()
        self.assert_true(
            kanban.get("updated_at_local") is not None
            and self._match_local(kanban["updated_at_local"]),
            "updated_at_local 缺失时也应被补上",
            f"实际值: {kanban.get('updated_at_local')!r}",
        )

        # ================================================================
        # 测试 3: monitor._update_kanban 不会破坏 scheduler 的格式
        # （这是原始 docstring 承诺，必须保留）
        # ================================================================
        existing_complex = {
            "updated_at": "2026-08-05T04:30:57Z",
            "updated_at_local": "2026-08-05 12:30:57",
            "current": {
                "in_slot": False,
                "slot_index": None,
                "slot": "08:30-12:30",
                "focus_proposal": "general-moire-strong-field-probe-20260726",
                "proposals_in_optimizing": 5,
            },
            "proposals": [
                {
                    "proposal_id": "general-moire-strong-field-probe-20260726",
                    "round": 6,
                    "score": 0.66,
                    "jobs": "24/29",
                    "failed": 0,
                    "pending": 4,
                    "stuck": False,
                    "next_job": None,
                },
            ],
            "execution_history": [
                {"at": "2026-08-05T03:35:25Z", "proposal_id": "p1", "job_id": "j1",
                 "step": "writer", "success": True, "error": ""},
            ],
            "day_key": "2026-08-05",
            "task_sync": {"enabled": True, "stats": {}, "mapping_count": 0},
        }
        self._seed_kanban(existing_complex)

        stats = [
            {"proposal_id": "general-moire-strong-field-probe-20260726",
             "done": 94, "failed": 1, "pending": 71, "running": 0},
        ]
        focus_info = {
            "proposal_id": "general-moire-strong-field-probe-20260726",
            "slot": "08:30-12:30",
            "next_job": "critic/references",
        }
        self.monitor._update_kanban(stats, focus_info)
        kanban = self._read_kanban()

        # scheduler 写入的字段必须保留
        self.assert_eq(
            kanban.get("current", {}).get("focus_proposal"),
            "general-moire-strong-field-probe-20260726",
            "monitor.update_kanban 应保留 scheduler 写入的 current.focus_proposal",
        )
        self.assert_eq(
            len(kanban.get("execution_history", [])),
            1,
            "execution_history 应保留 scheduler 写入的历史记录",
        )
        self.assert_eq(
            kanban.get("day_key"),
            "2026-08-05",
            "day_key 字段应被保留",
        )

        # monitor 新增的字段应存在
        self.assert_true(
            kanban.get("hourly_monitor", {}).get("total_done") == 94,
            "monitor 写入的 hourly_monitor.total_done 应等于 94",
            f"实际值: {kanban.get('hourly_monitor')}",
        )
        self.assert_eq(
            kanban.get("monitor_focus"),
            focus_info,
            "monitor_focus 字段应被正确写入",
        )

        # updated_at_local 必须被刷新
        self.assert_true(
            kanban.get("updated_at_local") != "2026-08-05 12:30:57",
            "updated_at_local 必须刷新",
            f"实际值: {kanban.get('updated_at_local')!r}",
        )


if __name__ == "__main__":
    suite = MonitorKanbanLocalTests()
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
