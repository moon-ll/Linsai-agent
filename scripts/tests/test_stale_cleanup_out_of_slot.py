#!/usr/bin/env python3
"""
test_stale_cleanup_out_of_slot.py — 跨时段 stale job 回收测试

验证缺陷 fix9 (v6.8.3):
    run_micro_scheduler 原来"时段检查 → return"在 stale 清理之前，
    导致不在工作时段时 running job 无法被回收。
    一个 references-critic job 在时段末尾启动，时段结束后
    卡在 running 状态超过 95 分钟，直到下一个时段才开始处理。

验证点：
    1. 不在工作时段内（_current_focus_slot 返回 None）时，
       _refresh_stale_jobs 仍然被调用，超时 running job 被标记 failed
    2. stale 清理返回 out_of_slot，但 job 状态已变更
    3. 多个 proposal 的 stale job 都被清理
    4. 正常 pending job 不受影响（只清理 running+stale）
"""

import sys
import json
import shutil
import importlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from test_runner import TestSuite, create_isolated_env, patch_module_root, patch_kb_sync_noop


def _make_job(pid, round_num, section_key, step, status="pending",
              started_at="", attempts=0):
    """构造单个 pipeline job 字典。"""
    return {
        "job_id": f"{pid}-r{round_num}-{section_key}-{step}",
        "proposal_id": pid,
        "step": step,
        "section_key": section_key,
        "round": round_num,
        "status": status,
        "depends_on": [],
        "attempts": attempts,
        "scheduled_at": "",
        "started_at": started_at,
        "finished_at": "",
        "last_error": "",
        "cron_job_id": "",
    }


class StaleCleanupOutOfSlotTests(TestSuite):
    def __init__(self):
        super().__init__("跨时段 stale job 回收测试")
        self.tmp_root = None
        self.ms = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / sub).mkdir(parents=True, exist_ok=True)

        for mod_name in list(sys.modules.keys()):
            if "micro_scheduler" in mod_name or mod_name in [
                "lifecycle", "paths", "common", "proposal_lifecycle",
                "proposal_sections",
            ]:
                del sys.modules[mod_name]

        self.ms = importlib.import_module("lifecycle.micro_scheduler")
        patch_module_root("lifecycle.micro_scheduler", self.tmp_root)
        patch_kb_sync_noop(self.ms)  # 拦截 KB 同步，避免测试写穿真实 knowledge/
        import paths
        paths.PROJECT_ROOT = self.tmp_root

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_stale_timestamp(self, hours_ago=2):
        """生成 hours_ago 小时前的 UTC ISO 时间戳。"""
        past = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        return past.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _make_mock_controller(self, proposals_config):
        """创建模拟控制器。

        Args:
            proposals_config: {
                pid: {
                    "jobs": [...],
                    "optimization_rounds": N,
                }
            }
        """
        ctrl = MagicMock()

        def _get_jobs(pid):
            return proposals_config.get(pid, {}).get("jobs", [])

        saved_jobs = {}

        def _save_jobs(pid, jobs):
            saved_jobs[pid] = jobs
            proposals_config[pid]["jobs"] = jobs
            return True

        def _get_proposal_state(pid):
            return proposals_config.get(pid, {})

        ctrl._get_jobs.side_effect = _get_jobs
        ctrl._save_jobs.side_effect = _save_jobs
        ctrl._get_proposal_state.side_effect = _get_proposal_state
        ctrl._is_proposal_stuck.return_value = False
        ctrl._list_ready_jobs_for_proposal.return_value = []
        ctrl._focus_proposal_for_slot.return_value = None
        ctrl._load_state.return_value = {"proposals": {}}
        ctrl._save_state.return_value = True
        ctrl.list_by_status.return_value = [
            {"proposal_id": pid} for pid in proposals_config
        ]

        # 绑定真实 _refresh_stale_jobs 到 mock controller
        # 否则 MagicMock 会吞掉 stale 检查逻辑，测试无法验证修复
        ctrl._refresh_stale_jobs = lambda pid: self.ms._refresh_stale_jobs(ctrl, pid)

        ctrl._saved_jobs = saved_jobs
        return ctrl

    def run_tests(self):
        pid_a = "general-test-alpha-20260101"
        pid_b = "general-test-beta-20260101"

        # ================================================================
        # 测试 1（核心回归）: 不在时段内时 stale running job 仍被回收
        # bug 现场: run_micro_scheduler 因 slot_info=None 直接 return，
        #          不执行 _refresh_stale_jobs，running job 永远卡住
        # ================================================================
        stale_ts = self._make_stale_timestamp(2)  # 2 小时前，远超 3600s 阈值
        jobs_a = [
            _make_job(pid_a, 1, "references", "critic", status="running",
                      started_at=stale_ts),
            _make_job(pid_a, 1, "references", "writer", status="pending"),
        ]
        ctrl = self._make_mock_controller({
            pid_a: {"jobs": jobs_a, "optimization_rounds": 0},
        })

        # 模拟不在工作时段
        with patch.object(self.ms, "_current_focus_slot", return_value=None):
            result = self.ms.run_micro_scheduler(ctrl, max_jobs=1)

        self.assert_eq(
            result.get("skip_reason"), "out_of_slot",
            "不在时段内应返回 out_of_slot",
            "stale 清理后仍应返回 out_of_slot 表示跳过执行",
        )

        # 验证 _refresh_stale_jobs 被调用了（ctrl._save_jobs 被触发）
        updated_jobs = ctrl._saved_jobs.get(pid_a, [])
        stale_job = next((j for j in updated_jobs if j["step"] == "critic"), None)
        self.assert_true(
            stale_job is not None and stale_job["status"] == "failed",
            "不在时段内时 stale running job 应被标记为 failed",
            f"期望 critic job 被标记 failed，实际 status={stale_job['status'] if stale_job else 'NOT FOUND'}",
        )
        self.assert_eq(
            stale_job.get("attempts", 0), 1,
            "stale 回收应递增 attempts 到 1",
        )

        # ================================================================
        # 测试 2: 多个 proposal 的 stale job 都被清理
        # ================================================================
        stale_ts2 = self._make_stale_timestamp(3)
        jobs_a2 = [
            _make_job(pid_a, 1, "references", "critic", status="running",
                      started_at=stale_ts2),
        ]
        jobs_b = [
            _make_job(pid_b, 1, "full_review", "critic", status="running",
                      started_at=stale_ts2),
        ]
        ctrl2 = self._make_mock_controller({
            pid_a: {"jobs": jobs_a2, "optimization_rounds": 0},
            pid_b: {"jobs": jobs_b, "optimization_rounds": 0},
        })

        with patch.object(self.ms, "_current_focus_slot", return_value=None):
            self.ms.run_micro_scheduler(ctrl2, max_jobs=1)

        saved_a = ctrl2._saved_jobs.get(pid_a, [])
        saved_b = ctrl2._saved_jobs.get(pid_b, [])
        failed_a = [j for j in saved_a if j["status"] == "failed"]
        failed_b = [j for j in saved_b if j["status"] == "failed"]

        self.assert_eq(len(failed_a), 1, f"proposal A 应有 1 个 stale job 被回收")
        self.assert_eq(len(failed_b), 1, f"proposal B 应有 1 个 stale job 被回收")

        # ================================================================
        # 测试 3: 正常 pending job 不受 stale 清理影响
        # ================================================================
        stale_ts3 = self._make_stale_timestamp(2)
        jobs_a3 = [
            _make_job(pid_a, 1, "references", "critic", status="running",
                      started_at=stale_ts3),
            _make_job(pid_a, 1, "references", "writer", status="pending"),
            _make_job(pid_a, 1, "monitor", "monitor", status="pending"),
        ]
        ctrl3 = self._make_mock_controller({
            pid_a: {"jobs": jobs_a3, "optimization_rounds": 0},
        })

        with patch.object(self.ms, "_current_focus_slot", return_value=None):
            self.ms.run_micro_scheduler(ctrl3, max_jobs=1)

        updated = ctrl3._saved_jobs.get(pid_a, [])
        statuses = {j["step"]: j["status"] for j in updated}
        self.assert_eq(
            statuses.get("critic"), "failed",
            "running+stale 的 critic 应被标记 failed",
        )
        self.assert_eq(
            statuses.get("writer"), "pending",
            "pending 的 writer 不应被 stale 清理影响",
        )
        self.assert_eq(
            statuses.get("monitor"), "pending",
            "pending 的 monitor 不应被 stale 清理影响",
        )

        # ================================================================
        # 测试 4: running 但未超时的 job 不被误杀
        # ================================================================
        recent_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        jobs_a4 = [
            _make_job(pid_a, 1, "references", "critic", status="running",
                      started_at=recent_ts),
        ]
        ctrl4 = self._make_mock_controller({
            pid_a: {"jobs": jobs_a4, "optimization_rounds": 0},
        })

        with patch.object(self.ms, "_current_focus_slot", return_value=None):
            self.ms.run_micro_scheduler(ctrl4, max_jobs=1)

        # _save_jobs 不应被调用（没有 stale job 需要更新）
        self.assert_true(
            pid_a not in ctrl4._saved_jobs,
            "running 但未超时的 job 不应触发 _save_jobs",
        )


if __name__ == "__main__":
    suite = StaleCleanupOutOfSlotTests()
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
