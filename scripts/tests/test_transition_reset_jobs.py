#!/usr/bin/env python3
"""
test_transition_reset_jobs.py — 审核退回清理旧轮次残留 job 回归测试（v6.9.24）

背景：
    pending_review → optimizing 审核退回时归零 optimization_rounds，
    但此前不清理 pipeline_jobs，退回前生命周期的 done/pending job 全部残留。
    后果链（实测 bsv 2026-08-18 快照：r7 done×29 + r8 done×23/pending×2）：
    1) _compute_actual_round 按"整轮 25 job 全 done"向上扫描，会消耗
       旧 done 轮次直接跳轮：新 r6 完成后一次性推到 r8=DEFAULT_MAX_ROUNDS，
       真实 r7/r8 两轮被跳过，提前触顶流转 pending_review；
    2) sync_checkpoint 按 job_id 去重建链（orchestrator.py:214），
       新 r7/r8 链因旧 job 同名 done 而永不创建；
    3) 高轮次 pending 残留（如 r8-derived）在轮末空窗会被误调度。

覆盖：
    - 审核退回归零轮次时，pipeline_jobs 全量归档并清空
    - 归档文件 _lifecycle_archive.json 保留旧 job（产出即资产）
    - 普通流转（optimizing → pending_review）不动 pipeline_jobs
    - legacy dict 形态 pipeline_jobs 同样清理
    - 退回清空后 _compute_actual_round 不跳轮

注意：
    本测试不调用 hermes/LLM，仅验证状态机。
    lifecycle.utils 为进程内共享模块，LIFECYCLE_ARCHIVE_PATH 的 patch
    在 teardown 中恢复，避免污染后续套件。
"""

import sys
import json
import shutil
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT
import importlib


class TransitionResetJobsTests(TestSuite):
    def __init__(self):
        super().__init__("审核退回清理残留 job 测试")
        self.tmp_root = None
        self.ctrl = None
        self._lu = None
        self._orig_archive_path = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "research_proposals").mkdir(parents=True, exist_ok=True)
        for subdir in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / subdir).mkdir(exist_ok=True)

        for mod_name in ("proposal_lifecycle", "lifecycle_cron_framework"):
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        importlib.import_module("proposal_lifecycle")
        self.ctrl = importlib.import_module("lifecycle_cron_framework")

        patch_module_root("proposal_lifecycle", self.tmp_root)
        patch_module_root("lifecycle_cron_framework", self.tmp_root)

        # 归档路径定向隔离目录（teardown 恢复，防跨套件泄漏）
        import lifecycle.utils as lu
        self._lu = lu
        self._orig_archive_path = lu.LIFECYCLE_ARCHIVE_PATH
        lu.LIFECYCLE_ARCHIVE_PATH = (
            self.tmp_root / "research_proposals" / "_lifecycle_archive.json"
        )

    def teardown(self):
        if self._lu is not None and self._orig_archive_path is not None:
            self._lu.LIFECYCLE_ARCHIVE_PATH = self._orig_archive_path
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_controller(self):
        return self.ctrl.LifecycleCronController()

    def _make_proposal_at_pending_review(self, controller, pid):
        """注册并流转到 pending_review（文件结构随目录整体移动）。"""
        controller.register(pid, project_type="general")
        controller.transition(pid, "optimizing")
        prop_dir = controller.root / "optimizing" / pid
        prop_dir.mkdir(parents=True, exist_ok=True)
        (prop_dir / "00_proposal-brief.md").write_text(f"# {pid}\n\ntest", encoding="utf-8")
        (prop_dir / "04_proposal").mkdir(exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text("# draft\n", encoding="utf-8")
        controller.transition(pid, "pending_review")

    def _stale_jobs(self, pid):
        def mk(round_num, section, step, status):
            return {
                "job_id": f"{pid}-r{round_num}-{section}-{step}",
                "proposal_id": pid,
                "step": step,
                "section_key": section,
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

        # 模拟 bsv 快照：r7 全 done + r8 大部分 done + derived pending
        return [
            mk(7, "rationale", "critic", "done"),
            mk(7, "content", "writer", "done"),
            mk(8, "monitor", "monitor", "done"),
            mk(8, "derived", "update_vision", "pending"),
            mk(8, "derived", "update_method_manual", "pending"),
        ]

    def _archived_ids(self):
        archive_path = self.tmp_root / "research_proposals" / "_lifecycle_archive.json"
        if not archive_path.exists():
            return set()
        archive = json.loads(archive_path.read_text(encoding="utf-8"))
        return {j.get("job_id") for j in archive.get("jobs", [])}

    # ── 测试用例 ──

    def _test_review_return_clears_stale_jobs(self):
        """审核退回归零轮次时，残留 job 应全量归档并清空 pipeline_jobs。"""
        c = self._make_controller()
        pid = "general-reset-jobs-20260101"
        self._make_proposal_at_pending_review(c, pid)
        c._save_jobs(pid, self._stale_jobs(pid))

        result = c.transition(pid, "optimizing", reason="人工审核退回(major_revision)")
        self.assert_true(result.get("success"), "审核退回流转应成功")

        prop_state = c._get_proposal_state(pid)
        self.assert_eq(prop_state.get("optimization_rounds"), 0, "轮次应归零")
        self.assert_eq(prop_state.get("pipeline_jobs"), [], "pipeline_jobs 应清空（防跳轮/误调度）")

        archived_ids = self._archived_ids()
        for j in self._stale_jobs(pid):
            self.assert_true(
                j["job_id"] in archived_ids,
                f"旧 job 应进归档: {j['job_id']}",
            )

    def _test_review_return_consumes_no_round_after_reset(self):
        """退回清空后，_compute_actual_round 不得消耗旧 done 轮次跳轮。"""
        c = self._make_controller()
        pid = "general-reset-scan-20260102"
        self._make_proposal_at_pending_review(c, pid)
        c.transition(pid, "optimizing", reason="人工审核退回(major_revision)")

        # 新 r1 链由 sync_checkpoint 建立，模拟 r1 全部完成
        c.sync_checkpoint(pid)
        jobs = c._get_jobs(pid)
        for j in jobs:
            j["status"] = "done"
        c._save_jobs(pid, jobs)

        actual = c._compute_actual_round(pid, c._get_jobs(pid))
        self.assert_eq(actual, 1, "退回清空旧 job 后，actual_round 只能到 1，不得跳轮")

    def _test_plain_transition_keeps_jobs(self):
        """普通流转（optimizing → pending_review）不应清空 pipeline_jobs。"""
        c = self._make_controller()
        pid = "general-keep-jobs-20260103"
        c.register(pid, project_type="general")
        c.transition(pid, "optimizing")
        prop_dir = c.root / "optimizing" / pid
        prop_dir.mkdir(parents=True, exist_ok=True)
        (prop_dir / "00_proposal-brief.md").write_text(f"# {pid}\n\ntest", encoding="utf-8")
        (prop_dir / "04_proposal").mkdir(exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text("# draft\n", encoding="utf-8")

        stale = self._stale_jobs(pid)
        c._save_jobs(pid, stale)
        result = c.transition(pid, "pending_review", reason="测试晋级")
        self.assert_true(result.get("success"), "普通流转应成功")
        jobs_after = c._get_jobs(pid)
        self.assert_eq(len(jobs_after), len(stale), "普通流转不应清理 pipeline_jobs")

    def _test_dict_pipeline_jobs_compat(self):
        """legacy dict 形态 pipeline_jobs 同样应被归档清空。"""
        c = self._make_controller()
        pid = "general-reset-dict-20260104"
        self._make_proposal_at_pending_review(c, pid)
        stale = self._stale_jobs(pid)
        prop_state = c._get_proposal_state(pid)
        prop_state["pipeline_jobs"] = {j["job_id"]: j for j in stale}
        c._set_proposal_state(pid, prop_state)

        result = c.transition(pid, "optimizing", reason="人工审核退回(major_revision)")
        self.assert_true(result.get("success"), "dict 形态流转应成功")
        after = c._get_proposal_state(pid)
        self.assert_eq(after.get("pipeline_jobs"), [], "dict 形态 pipeline_jobs 应清空")
        archived_ids = self._archived_ids()
        self.assert_true(
            stale[0]["job_id"] in archived_ids,
            "dict 形态旧 job 应进归档",
        )


    # ── 执行器：反射调用全部 _test_* 用例（防止基类 NotImplementedError 静默吞） ──

    def run_tests(self):
        for name in sorted(dir(self)):
            if name.startswith("_test_"):
                getattr(self, name)()


if __name__ == "__main__":
    suite = TransitionResetJobsTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    s = suite.summary()
    print(f"通过 {s['passed']} / 失败 {s['failed']}")
    sys.exit(1 if s["failed"] else 0)
