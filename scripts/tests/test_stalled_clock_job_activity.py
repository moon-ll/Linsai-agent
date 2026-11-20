#!/usr/bin/env python3
"""
test_stalled_clock_job_activity.py — 停滞课题检测时钟口径回归测试

历史：
    v6.8.16 引入停滞检测；v6.8.27 放宽 done==0 要求。但停滞时钟一直
    读 proposal 的 updated_at——该字段会被 repair 重置 / cron 失败记录
    （_record_cron_failed）/ stale 清理等非执行写入刷新，掩盖真实停滞。
    08-21 实证：bsv 课题 updated_at 距 26.1h（48h 阈值未到），而最后一
    个 job 完成于 87.7h 前，停滞告警永不触发。v6.9.31 改为取任一 job 的
    finished_at/started_at 最大值作为停滞时钟，无 job 时间戳时回退
    updated_at。

注意：
    本测试不调用 hermes/LLM，桩化 ProposalLifecycle 与 get_controller。
"""

import sys
import json
import shutil
import importlib
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from test_runner import TestSuite, create_isolated_env


def _ts(hours_ago: float) -> str:
    t = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


class StalledClockTests(TestSuite):
    def __init__(self):
        super().__init__("停滞检测时钟口径测试")
        self.tmp_root = None
        self.monitor = None
        self._orig = {}

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)

        for mod_name in list(sys.modules.keys()):
            if mod_name == "lifecycle_monitor":
                del sys.modules[mod_name]

        self.monitor = importlib.import_module("lifecycle_monitor")
        self._orig_root = self.monitor.PROJECT_ROOT
        self.monitor.PROJECT_ROOT = self.tmp_root
        self.monitor.KANBAN_PATH = self.tmp_root / "memory" / "system-kanban.json"
        self.monitor.ALERT_CACHE_PATH = (
            self.tmp_root / "memory" / "monitor-alert-cache.json"
        )

        # 桩化 _check_proposals 的内部依赖（函数内 import，须打模块属性）
        import proposal_lifecycle
        import lifecycle.controller as lc

        self._orig = {
            "pl": proposal_lifecycle.ProposalLifecycle,
            "ctrl": lc.get_controller,
        }

    def teardown(self):
        import proposal_lifecycle
        import lifecycle.controller as lc

        proposal_lifecycle.ProposalLifecycle = self._orig["pl"]
        lc.get_controller = self._orig["ctrl"]
        if self._orig_root is not None:
            self.monitor.PROJECT_ROOT = self._orig_root
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _install_fixture(self, proposal: dict, jobs: list):
        """安装桩：list_by_status 返回单个 proposal，_get_jobs 返回 jobs。"""
        import proposal_lifecycle
        import lifecycle.controller as lc

        class _FakePL:
            def list_by_status(self, status):
                return [proposal] if status == "optimizing" else []

        proposal_lifecycle.ProposalLifecycle = _FakePL

        ctrl = MagicMock()
        ctrl._get_jobs.side_effect = lambda pid: jobs
        lc.get_controller = lambda: ctrl

    def _stalled_anomalies(self):
        _, anomalies = self.monitor._check_proposals()
        return [a for a in anomalies if a.get("type") == "stalled"]

    def run_tests(self):
        pid = "general-stall-fixture-20260821"

        # ── 用例 1（核心回归）：job 停滞 110h、updated_at 仅 26h → 必须告警 ──
        # 旧口径读 updated_at（26h < 48h）漏报；新口径读 job 级最后活动。
        # v6.10.13 净工时口径：扣除窗口内周末小时；87h 实际仅 47h 净工时
        # 不触发，故锚点 110h（净工时 ≈70h）保证任一运行日均成立。
        self._install_fixture(
            proposal={"proposal_id": pid, "optimization_rounds": 0,
                      "last_score": 0.5, "updated_at": _ts(26)},
            jobs=[
                {"job_id": f"{pid}-r1-critic", "status": "done",
                 "finished_at": _ts(110), "started_at": _ts(111)},
                {"job_id": f"{pid}-r1-writer", "status": "pending",
                 "finished_at": "", "started_at": ""},
            ],
        )
        hits = self._stalled_anomalies()
        self.assert_eq(len(hits), 1, "job 停滞 110h（updated_at 被 26h 前的非执行写入刷新）应触发 stalled")
        if hits:
            self.assert_true(
                hits[0].get("hours", 0) >= 80,
                "停滞时长应以 job 级最后活动计算（约 110h）",
                f"实际 hours={hits[0].get('hours')}，疑似仍按 updated_at 口径",
            )

        # ── 用例 2：job 活跃（2h 前）→ 不告警（正常运行）──
        self._install_fixture(
            proposal={"proposal_id": pid, "optimization_rounds": 0,
                      "last_score": 0.5, "updated_at": _ts(2)},
            jobs=[
                {"job_id": f"{pid}-r1-critic", "status": "done",
                 "finished_at": _ts(2), "started_at": _ts(3)},
                {"job_id": f"{pid}-r1-writer", "status": "pending",
                 "finished_at": "", "started_at": ""},
            ],
        )
        self.assert_eq(
            len(self._stalled_anomalies()), 0,
            "job 2h 前仍在完成（等待轮转聚焦）不应告警",
        )

        # ── 用例 3：无 job 时间戳 → 回退 updated_at（净工时 >48h）应告警 ──
        # v6.10.13: 140h 前距今扣除周末豁免后净工时 ~92h > 48h（周末无关
        # 时间锚点，任何运行日均成立）
        self._install_fixture(
            proposal={"proposal_id": pid, "optimization_rounds": 0,
                      "last_score": 0.5, "updated_at": _ts(140)},
            jobs=[
                {"job_id": f"{pid}-r1-critic", "status": "done",
                 "finished_at": "", "started_at": ""},
                {"job_id": f"{pid}-r1-writer", "status": "pending",
                 "finished_at": "", "started_at": ""},
            ],
        )
        self.assert_eq(
            len(self._stalled_anomalies()), 1,
            "无 job 时间戳时应回退 updated_at（净工时 92h > 48h 触发）",
        )
        anomalies = self._stalled_anomalies()
        self.assert_true(
            anomalies and "净工时" in anomalies[0].get("message", ""),
            "v6.10.13 告警消息应含净工时口径",
        )

        # ── 用例 4：job 停滞但无 pending → 不告警（轮次已收尾）──
        self._install_fixture(
            proposal={"proposal_id": pid, "optimization_rounds": 0,
                      "last_score": 0.5, "updated_at": _ts(26)},
            jobs=[
                {"job_id": f"{pid}-r1-critic", "status": "done",
                 "finished_at": _ts(110), "started_at": _ts(111)},
            ],
        )
        self.assert_eq(
            len(self._stalled_anomalies()), 0,
            "无 pending job（等待轮转或已收尾）不应告警",
        )


if __name__ == "__main__":
    suite = StalledClockTests()
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
