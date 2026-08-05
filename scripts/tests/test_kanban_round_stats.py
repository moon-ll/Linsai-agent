#!/usr/bin/env python3
"""
test_kanban_round_stats.py — 看板轮次统计隔离测试

验证 _update_kanban 中 proposals_status 的 jobs/done/pending/failed/total
只统计当前轮次（round_num），不跨轮累积。

缺陷描述：
    micro_scheduler._update_kanban 第 750-756 行，统计 done/pending/failed/total
    时遍历了 pipeline_jobs 中所有轮次的 job，而非仅当前进行中的轮次。
    导致看板显示如 "50/62" 而实际单轮只有 25-33 个 job。

验证点：
    - 单轮 25 job 全部 done → 看板应显示 25/25
    - 两轮共存（r5 全 done + r6 进行中）→ 看板只显示 r6 数据
    - 动态注入后单轮 33 job → 看板显示 33/33 而非跨轮累积
"""

import sys
import json
import shutil
import importlib
from pathlib import Path
from unittest.mock import MagicMock

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT

# ── 辅助函数 ──

def _make_job(pid, round_num, section_key, step, status="pending"):
    """构造单个 pipeline job 字典。"""
    return {
        "job_id": f"{pid}-r{round_num}-{section_key}-{step}",
        "proposal_id": pid,
        "step": step,
        "section_key": section_key,
        "round": round_num,
        "status": status,
        "depends_on": [],
        "attempts": 0,
        "scheduled_at": "",
        "started_at": "",
        "finished_at": "",
        "last_error": "",
        "cron_job_id": "",
    }


def _build_standard_round(pid, round_num):
    """生成标准 25-job 一轮（3 模块 × 6 步 + full_review 2 + references 2 + monitor 1 + derived 2）。"""
    jobs = []
    sections_6step = ["rationale", "content", "scheme"]
    steps_6 = ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]

    for sec in sections_6step:
        for step in steps_6:
            jobs.append(_make_job(pid, round_num, sec, step))

    for step in ["critic", "writer"]:
        jobs.append(_make_job(pid, round_num, "full_review", step))
        jobs.append(_make_job(pid, round_num, "references", step))

    jobs.append(_make_job(pid, round_num, "monitor", "monitor"))
    jobs.append(_make_job(pid, round_num, "derived", "update_vision"))
    jobs.append(_make_job(pid, round_num, "derived", "update_method_manual"))

    assert len(jobs) == 25, f"标准一轮应为 25 job，实际 {len(jobs)}"
    return jobs


class KanbanRoundStatsTests(TestSuite):
    def __init__(self):
        super().__init__("看板轮次统计隔离测试")
        self.tmp_root = None
        self.ms = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / sub).mkdir(parents=True, exist_ok=True)

        # 强制重新导入
        for mod_name in list(sys.modules.keys()):
            if "micro_scheduler" in mod_name or mod_name in [
                "lifecycle", "paths", "common", "proposal_lifecycle",
                "proposal_sections",
            ]:
                del sys.modules[mod_name]

        self.ms = importlib.import_module("lifecycle.micro_scheduler")
        patch_module_root("lifecycle.micro_scheduler", self.tmp_root)
        import paths
        paths.PROJECT_ROOT = self.tmp_root

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_mock_controller(self, pid, jobs, opt_rounds=0, score=0.0):
        """创建模拟控制器。
        
        Args:
            pid: proposal ID
            jobs: pipeline_jobs 列表
            opt_rounds: optimization_rounds 值
            score: last_score 值
        """
        ctrl = MagicMock()
        ctrl._get_proposal_state.return_value = {
            "optimization_rounds": opt_rounds,
            "last_score": score,
            "status": "optimizing",
        }
        ctrl._get_jobs.return_value = jobs
        ctrl._is_proposal_stuck.return_value = False
        ctrl._list_ready_jobs_for_proposal.return_value = []
        return ctrl

    def _call_update_kanban(self, ctrl, pid, jobs, opt_rounds=0):
        """直接调用 _update_kanban 并返回 proposals_status。
        
        由于 _update_kanban 是在函数内部构建 proposals_status 然后写文件，
        我们通过读取写入的 KANBAN_PATH 来验证结果。
        """
        optimizing = [{"proposal_id": pid}]
        executed = []

        # 调用 _update_kanban（它是微调度器模块的顶层函数）
        self.ms._update_kanban(
            slot_info=(0, ("00:30", "03:30")),
            focus_pid=pid,
            optimizing=optimizing,
            executed=executed,
            self=ctrl,
        )

        # 读取看板文件
        kanban_path = self.tmp_root / "memory" / "system-kanban.json"
        if kanban_path.exists():
            data = json.loads(kanban_path.read_text(encoding="utf-8"))
            proposals = data.get("proposals", [])
            if proposals:
                return proposals[0]
        return None

    # ── 测试用例 ──

    def _test_single_round_all_done(self):
        """单轮 25 job 全部 done，看板应显示 25/25。"""
        pid = "test-alpha-20260101"
        jobs = _build_standard_round(pid, 1)
        for j in jobs:
            j["status"] = "done"

        ctrl = self._make_mock_controller(pid, jobs, opt_rounds=0)
        result = self._call_update_kanban(ctrl, pid, jobs, opt_rounds=0)

        self.assert_true(result is not None, "看板结果存在")
        self.assert_eq(result["jobs"], "25/25", "单轮全部 done 时显示 25/25")
        self.assert_eq(result["pending"], 0, "pending 为 0")
        self.assert_eq(result["failed"], 0, "failed 为 0")

    def _test_single_round_partial(self):
        """单轮 25 job，10 done 15 pending，看板应显示 10/25。"""
        pid = "test-beta-20260101"
        jobs = _build_standard_round(pid, 1)
        for j in jobs[:10]:
            j["status"] = "done"
        for j in jobs[10:]:
            j["status"] = "pending"

        ctrl = self._make_mock_controller(pid, jobs, opt_rounds=0)
        result = self._call_update_kanban(ctrl, pid, jobs, opt_rounds=0)

        self.assert_true(result is not None, "看板结果存在")
        self.assert_eq(result["jobs"], "10/25", "部分完成时显示 10/25")
        self.assert_eq(result["pending"], 15, "pending 为 15")

    def _test_two_rounds_not_accumulated(self):
        """两轮共存（r5 全 done + r6 进行中），看板只显示 r6 数据。

        这是核心修复验证：修复前会显示 40/50（r5 的 25 + r6 的 25 累加），
        修复后应只显示 r6 的数据。
        """
        pid = "test-gamma-20260101"
        # r5: 全部 done（25 个）
        r5_jobs = _build_standard_round(pid, 5)
        for j in r5_jobs:
            j["status"] = "done"
        # r6: 5 done, 20 pending（25 个）
        r6_jobs = _build_standard_round(pid, 6)
        for j in r6_jobs[:5]:
            j["status"] = "done"
        for j in r6_jobs[5:]:
            j["status"] = "pending"

        all_jobs = r5_jobs + r6_jobs  # 共 50 个

        ctrl = self._make_mock_controller(pid, all_jobs, opt_rounds=5)
        result = self._call_update_kanban(ctrl, pid, all_jobs, opt_rounds=5)

        self.assert_true(result is not None, "看板结果存在")
        self.assert_eq(result["jobs"], "5/25", "跨轮不累积：只显示 r6 的 5/25")
        self.assert_eq(result["pending"], 20, "pending 只统计 r6 的 20")

    def _test_dynamic_injection_33_jobs(self):
        """动态注入后单轮 33 job（full_review+references 各 +4），看板显示 33/33。"""
        pid = "test-delta-20260101"
        jobs = _build_standard_round(pid, 3)

        # 模拟 full_review 注入 4 个 researcher 子任务
        for step in ["gap_identify", "lit_search", "lit_read", "lit_note"]:
            jobs.append(_make_job(pid, 3, "full_review", step))

        # 模拟 references 注入 4 个 researcher 子任务
        for step in ["gap_identify", "lit_search", "lit_read", "lit_note"]:
            jobs.append(_make_job(pid, 3, "references", step))

        # 25 + 8 = 33
        self.assert_eq(len(jobs), 33, "动态注入后单轮 33 job")

        for j in jobs:
            j["status"] = "done"

        ctrl = self._make_mock_controller(pid, jobs, opt_rounds=2)
        result = self._call_update_kanban(ctrl, pid, jobs, opt_rounds=2)

        self.assert_true(result is not None, "看板结果存在")
        self.assert_eq(result["jobs"], "33/33", "动态注入后显示 33/33")

    def _test_dynamic_injection_with_old_round(self):
        """动态注入 33 job + 旧轮残留 25 job，看板只显示当前轮 33 个。

        最极端的真实场景：quantum-geometry 有 r6(33) + r7(29) 共 62 job。
        """
        pid = "test-epsilon-20260101"
        # r6: 33 个（含动态注入），全 done
        r6_base = _build_standard_round(pid, 6)
        for step in ["gap_identify", "lit_search", "lit_read", "lit_note"]:
            r6_base.append(_make_job(pid, 6, "full_review", step))
            r6_base.append(_make_job(pid, 6, "references", step))
        for j in r6_base:
            j["status"] = "done"
        self.assert_eq(len(r6_base), 33, "r6 含动态注入 33 job")

        # r7: 29 个（仅 full_review 注入），部分进行中
        r7_base = _build_standard_round(pid, 7)
        for step in ["gap_identify", "lit_search", "lit_read", "lit_note"]:
            r7_base.append(_make_job(pid, 7, "full_review", step))
        for j in r7_base[:15]:
            j["status"] = "done"
        for j in r7_base[15:]:
            j["status"] = "pending"
        self.assert_eq(len(r7_base), 29, "r7 含动态注入 29 job")

        all_jobs = r6_base + r7_base  # 共 62

        ctrl = self._make_mock_controller(pid, all_jobs, opt_rounds=6)
        result = self._call_update_kanban(ctrl, pid, all_jobs, opt_rounds=6)

        self.assert_true(result is not None, "看板结果存在")
        # 应只显示 r7: 15/29
        self.assert_eq(result["jobs"], "15/29", "跨轮+动态注入：只显示当前轮 r7 的 15/29")
        self.assert_eq(result["pending"], 14, "pending 只统计 r7 的 14")

    def _test_no_jobs(self):
        """无 job 时看板应显示 0/0 而不崩溃。"""
        pid = "test-zeta-20260101"
        ctrl = self._make_mock_controller(pid, [], opt_rounds=0)
        result = self._call_update_kanban(ctrl, pid, [], opt_rounds=0)

        self.assert_true(result is not None, "看板结果存在")
        self.assert_eq(result["jobs"], "0/0", "无 job 时显示 0/0")

    def _test_failed_count_isolated(self):
        """failed 计数只统计当前轮次。"""
        pid = "test-eta-20260101"
        # r3: 2 failed
        r3_jobs = _build_standard_round(pid, 3)
        for j in r3_jobs[:2]:
            j["status"] = "failed"
        for j in r3_jobs[2:10]:
            j["status"] = "done"
        for j in r3_jobs[10:]:
            j["status"] = "pending"

        # r2: 5 failed（不应被计入）
        r2_jobs = _build_standard_round(pid, 2)
        for j in r2_jobs[:5]:
            j["status"] = "failed"
        for j in r2_jobs[5:]:
            j["status"] = "done"

        all_jobs = r2_jobs + r3_jobs

        ctrl = self._make_mock_controller(pid, all_jobs, opt_rounds=2)
        result = self._call_update_kanban(ctrl, pid, all_jobs, opt_rounds=2)

        self.assert_true(result is not None, "看板结果存在")
        self.assert_eq(result["failed"], 2, "failed 只统计当前轮 r3 的 2 个")

    def run_tests(self):
        self._test_single_round_all_done()
        self._test_single_round_partial()
        self._test_two_rounds_not_accumulated()
        self._test_dynamic_injection_33_jobs()
        self._test_dynamic_injection_with_old_round()
        self._test_no_jobs()
        self._test_failed_count_isolated()


if __name__ == "__main__":
    from test_runner import print_report

    suite = KanbanRoundStatsTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    print_report([suite])
