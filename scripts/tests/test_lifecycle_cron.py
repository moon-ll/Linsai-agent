#!/usr/bin/env python3
"""
test_lifecycle_cron.py — 生命周期 cron 框架单元测试

覆盖：
    - checkpoint 生成（sync_checkpoint）
    - 下一 job 挑选（pick_next_job）
    - 幂等性（重复 sync 不重复创建）
    - researcher job 动态插入
    - stale running 修复
    - 依赖未满足时不执行

注意：
    本测试不调用 hermes/LLM，仅验证 checkpoint 状态机逻辑。
"""

import sys
import shutil
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT
import importlib


class LifecycleCronTests(TestSuite):
    def __init__(self):
        super().__init__("生命周期 cron 框架测试")
        self.tmp_root = None
        self.pl = None
        self.ctrl = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 需要 research_proposals 目录
        (self.tmp_root / "research_proposals").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "research_proposals" / "drafts").mkdir(exist_ok=True)
        (self.tmp_root / "research_proposals" / "optimizing").mkdir(exist_ok=True)
        (self.tmp_root / "research_proposals" / "pending_review").mkdir(exist_ok=True)
        (self.tmp_root / "research_proposals" / "archived").mkdir(exist_ok=True)

        # 复制 nsfc-standards.json（阈值配置）
        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")

        # 强制重新导入，避免污染
        for mod_name in ["proposal_lifecycle", "lifecycle_cron_framework"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        self.pl = importlib.import_module("proposal_lifecycle")
        self.ctrl = importlib.import_module("lifecycle_cron_framework")

        patch_module_root("proposal_lifecycle", self.tmp_root)
        patch_module_root("lifecycle_cron_framework", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_controller(self) -> "LifecycleCronController":
        return self.ctrl.LifecycleCronController()

    def _register_proposal(self, controller, pid: str, status: str = "optimizing"):
        controller.register(pid, project_type="general")
        if status != "drafts":
            controller.transition(pid, status)
        # 创建最小文件结构
        prop_dir = controller.root / status / pid
        prop_dir.mkdir(parents=True, exist_ok=True)
        (prop_dir / "00_proposal-brief.md").write_text(f"# {pid}\n\ntest proposal", encoding="utf-8")
        (prop_dir / "04_proposal").mkdir(exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text("# draft\n", encoding="utf-8")

    def _test_checkpoint_generation(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260101"
        self._register_proposal(c, pid, "optimizing")

        result = c.sync_checkpoint(pid)
        self.assert_true(result.get("success"), "sync_checkpoint 成功", result)
        self.assert_eq(result.get("added"), 3, "round 1 生成 3 个 job")

        jobs = c._get_jobs(pid)
        self.assert_eq(len(jobs), 3, "checkpoint 列表长度")
        self.assert_eq(jobs[0]["step"], "critic", "第一个 job 是 critic")
        self.assert_eq(jobs[1]["step"], "writer", "第二个 job 是 writer")
        self.assert_eq(jobs[2]["step"], "monitor", "第三个 job 是 monitor")
        self.assert_eq(jobs[0]["section_key"], "rationale", "round 1 聚焦立项依据")

    def _test_pick_next_job(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260102"
        self._register_proposal(c, pid, "optimizing")
        c.sync_checkpoint(pid)

        job = c.pick_next_job(pid)
        self.assert_true(job is not None, "有 pending job")
        self.assert_eq(job["step"], "critic", "下一个 job 是 critic")

    def _test_idempotent_sync(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260103"
        self._register_proposal(c, pid, "optimizing")
        c.sync_checkpoint(pid)
        result = c.sync_checkpoint(pid)
        self.assert_eq(result.get("added"), 0, "重复 sync 不新增")
        self.assert_eq(len(c._get_jobs(pid)), 3, "job 数量保持 3")

    def _test_dependency_respected(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260104"
        self._register_proposal(c, pid, "optimizing")
        c.sync_checkpoint(pid)

        # 模拟 critic 直接失败，writer 不应被 pick
        jobs = c._get_jobs(pid)
        jobs[0]["status"] = "failed"
        jobs[0]["attempts"] = 1
        c._save_jobs(pid, jobs)

        job = c.pick_next_job(pid)
        self.assert_true(job is None, "依赖未满足时无可用 job")

    def _test_researcher_insertion(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260105"
        self._register_proposal(c, pid, "optimizing")
        c.sync_checkpoint(pid)

        # 直接插入 researcher 流水线（模拟 critic 完成后的行为）
        c._insert_researcher_pipeline(pid, 1, "rationale")
        jobs = c._get_jobs(pid)
        self.assert_eq(len(jobs), 7, "插入 researcher 流水线后共 7 个 job")
        self.assert_eq(jobs[0]["step"], "critic", "第 1 个 job 是 critic")
        self.assert_eq(jobs[1]["step"], "gap_identify", "第 2 个 job 是 gap_identify")
        self.assert_eq(jobs[2]["step"], "lit_search", "第 3 个 job 是 lit_search")
        self.assert_eq(jobs[3]["step"], "lit_read", "第 4 个 job 是 lit_read")
        self.assert_eq(jobs[4]["step"], "lit_note", "第 5 个 job 是 lit_note")
        self.assert_eq(jobs[5]["step"], "writer", "第 6 个 job 是 writer")
        self.assert_eq(jobs[6]["step"], "monitor", "第 7 个 job 是 monitor")
        self.assert_in(jobs[4]["job_id"], jobs[5]["depends_on"], "writer 依赖 lit_note")

    def _test_stale_running_repair(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260106"
        self._register_proposal(c, pid, "optimizing")
        c.sync_checkpoint(pid)

        # 把 critic job 标记为 running 且 started_at 很久以前
        old_time = "2026-01-01T00:00:00Z"
        jobs = c._get_jobs(pid)
        jobs[0]["status"] = "running"
        jobs[0]["started_at"] = old_time
        c._save_jobs(pid, jobs)

        # pick_next_job 内部应先把 stale running 置为 failed
        job = c.pick_next_job(pid)
        self.assert_true(job is None, "stale job 被重置后当前无可用 job")
        jobs = c._get_jobs(pid)
        self.assert_eq(jobs[0]["status"], "failed", "stale running 变成 failed")
        self.assert_eq(jobs[0].get("attempts", 0), 1, "失败次数 +1")

    def _test_max_rounds_no_new_jobs(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260107"
        self._register_proposal(c, pid, "optimizing")
        # 设置已经达到最大轮数
        state = c._load_state()
        state["proposals"][pid]["optimization_rounds"] = 10
        c._save_state(state)

        result = c.sync_checkpoint(pid)
        self.assert_eq(result.get("added"), 0, "达到最大轮数不生成新 job")

    def _test_non_optimizing_no_jobs(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260108"
        self._register_proposal(c, pid, "drafts")
        result = c.sync_checkpoint(pid)
        self.assert_eq(result.get("added"), 0, "drafts 不生成 checkpoint")

    def _test_worker_minute_stagger(self):
        c = self._make_controller()
        pids = [
            "general-stagger-a-20260101",
            "general-stagger-b-20260101",
            "general-stagger-c-20260101",
            "general-stagger-d-20260101",
            "general-stagger-e-20260101",
        ]
        minutes = set()
        for pid in pids:
            self._register_proposal(c, pid, "optimizing")
            minute = c._compute_worker_minute(pid)
            minutes.add(minute)
            # 持久化后重建应保持一致
            self.assert_eq(c._compute_worker_minute(pid), minute, f"{pid} worker_minute 已持久化")
        # 多个 worker 应错开（至少存在 3 个不同分钟）
        self.assert_true(len(minutes) >= 3, f"worker 分钟错开，实际 {len(minutes)} 个不同值: {sorted(minutes)}")

    def run_tests(self):
        self._test_checkpoint_generation()
        self._test_pick_next_job()
        self._test_idempotent_sync()
        self._test_dependency_respected()
        self._test_researcher_insertion()
        self._test_stale_running_repair()
        self._test_max_rounds_no_new_jobs()
        self._test_non_optimizing_no_jobs()
        self._test_worker_minute_stagger()
