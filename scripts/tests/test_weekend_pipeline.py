#!/usr/bin/env python3
"""
test_weekend_pipeline.py — 周末任务流水线单元测试

覆盖：
    - 阶段任务幂等创建
    - 依赖解析与下一任务挑选
    - dry-run 执行不写入
    - repair 重置 stale/failed 任务

注意：
    本测试不调用 hermes/LLM，使用隔离临时目录。
"""

import sys
import shutil
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT
import importlib


class WeekendPipelineTests(TestSuite):
    def __init__(self):
        super().__init__("周末任务流水线测试")
        self.tmp_root = None
        self.wp_mod = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 创建 research_proposals 结构
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        # 复制 nsfc-standards.json（proposal_lifecycle 需要）
        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")

        # 强制重新导入，确保隔离目录生效
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("weekend_pipeline") or mod_name.startswith("proposal_lifecycle"):
                del sys.modules[mod_name]

        # 先 patch paths，再重新导入 proposal_lifecycle
        import paths
        self._orig_project_root = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root

        import proposal_lifecycle.constants as plc
        plc.PROJECT_ROOT = self.tmp_root
        plc.PROPOSALS_ROOT = self.tmp_root / "research_proposals"

        self.wp_mod = importlib.import_module("weekend_pipeline")
        patch_module_root("weekend_pipeline", self.tmp_root)
        patch_module_root("proposal_lifecycle", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        # 恢复 paths.PROJECT_ROOT
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    def _make_pipeline(self):
        from weekend_pipeline.pipeline import WeekendPipeline
        return WeekendPipeline(state_path=self.tmp_root / "memory" / "weekend-pipeline.json")

    def _test_sync_stage_jobs_idempotent(self):
        p = self._make_pipeline()
        result = p.sync_stage_jobs("input")
        self.assert_true(result.get("success"), "sync input 成功", result)
        self.assert_eq(len(result.get("jobs", [])), 7, "input 阶段 7 个 job")

        result2 = p.sync_stage_jobs("input")
        self.assert_eq(result2.get("added"), 0, "重复 sync 不新增")
        self.assert_eq(len(p.list_jobs(stage="input")), 7, "input job 数量保持 7")

    def _test_dependency_order(self):
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        jobs = p.list_jobs(stage="input")
        collect = next(j for j in jobs if j["job_id"] == "input_collect_sources")
        summarize = next(j for j in jobs if j["job_id"] == "input_summarize_new_papers")
        self.assert_in("input_collect_sources", summarize.get("depends_on", []), "summarize 依赖 collect")
        self.assert_eq(collect.get("depends_on"), [], "collect 无依赖")

    def _test_pick_next_job_respects_deps(self):
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        from weekend_pipeline.executor import pick_next_job
        job = pick_next_job(p.state, stage="input")
        self.assert_true(job is not None, "有 pending job")
        self.assert_eq(job["job_id"], "input_collect_sources", "第一个是 collect")

    def _test_run_next_dry_run_no_writes(self):
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        result = p.run_next(stage="input", dry_run=True)
        self.assert_true(result.get("success"), "dry-run run_next 成功", result)
        self.assert_eq(result.get("executed"), 1, "执行 1 个 job")
        # 不应写入 memory/weekend-input
        input_dir = self.tmp_root / "memory" / "weekend-input"
        self.assert_true(not input_dir.exists() or not any(input_dir.iterdir()), "dry-run 不写入 input 产物")

    def _test_repair_stale_and_failed(self):
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        jobs = p.list_jobs(stage="input")
        jobs[0]["status"] = "running"
        jobs[0]["started_at"] = "2026-01-01T00:00:00Z"
        jobs[1]["status"] = "failed"
        jobs[1]["attempts"] = 1
        p._save()

        repaired = p.repair()
        self.assert_true(repaired.get("success"), "repair 成功")
        jobs_after = p.list_jobs(stage="input")
        self.assert_eq(jobs_after[0]["status"], "failed", "stale running 变成 failed")
        self.assert_eq(jobs_after[1]["status"], "pending", "failed 重置为 pending")

    def _test_pick_next_job_retries_blocking_deps(self):
        """验证 pick_next_job 自动修复阻塞 pending 的 failed 依赖。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        jobs = p.list_jobs(stage="input")

        # 模拟：collect 已完成，summarize 失败，gap_analysis 等待 summarize
        jobs[0]["status"] = "done"  # input_collect_sources
        jobs[1]["status"] = "failed"  # input_summarize_new_papers
        jobs[1]["attempts"] = 1
        jobs[1]["repair_attempts"] = 0
        p._save()

        from weekend_pipeline.executor import pick_next_job
        job = pick_next_job(p.state, stage="input")

        # pick_next_job 应发现 summarize 是 failed 且阻塞 gap_analysis → 重置为 pending
        self.assert_true(job is not None, "应返回一个 job")
        self.assert_eq(job["job_id"], "input_summarize_new_papers", "应返回被修复的 failed 依赖")
        self.assert_eq(job["status"], "pending", "被修复的 job 应为 pending")
        self.assert_eq(job["repair_attempts"], 1, "repair_attempts 应 +1")

        # 验证 gap_analysis 的依赖现在满足
        gap = next(j for j in p.state.get("jobs", []) if j["job_id"] == "input_gap_analysis")
        self.assert_eq(gap["status"], "pending", "gap_analysis 仍为 pending")

    def _test_output_stage_creates_archived_extract_jobs(self):
        p = self._make_pipeline()
        # 创建最小 archived proposal
        prop_dir = self.tmp_root / "research_proposals" / "archived" / "general-test-archived-20260101"
        prop_dir.mkdir(parents=True, exist_ok=True)
        (prop_dir / "00_proposal-brief.md").write_text("# 测试归档课题\n\n**课题名称**：测试\n", encoding="utf-8")
        (prop_dir / "04_proposal").mkdir(exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text("# draft\n", encoding="utf-8")

        # 写入 lifecycle 状态
        lifecycle_path = self.tmp_root / "research_proposals" / "_lifecycle.json"
        lifecycle_path.write_text(
            '{"proposals": {"general-test-archived-20260101": {"status": "archived", "project_type": "general"}}}',
            encoding="utf-8",
        )

        result = p.sync_stage_jobs("output")
        self.assert_true(result.get("success"), "sync output 成功")
        job_ids = [j["job_id"] for j in p.list_jobs(stage="output")]
        self.assert_in("output_sync_proposals_to_kb", job_ids, "output 包含 sync job")
        self.assert_in("output_extract_archived_proposal_general-test-archived-20260101", job_ids, "output 包含 archived extract job")

    def _test_verify_artifacts_resets_missing_output(self):
        """验证 output 阶段产物缺失时自动重置 job 为 pending。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("output")

        # 模拟 dry-run 残留：所有 output job 标记 done，但无产物文件
        for job in p.list_jobs(stage="output"):
            job["status"] = "done"
            job["result"] = {"dry_run": True, "success": True}
        p._save()

        # 再次 sync — 应触发产物检测，重置为 pending
        p.sync_stage_jobs("output")
        jobs_after = p.list_jobs(stage="output")
        done_count = sum(1 for j in jobs_after if j.get("status") == "done")
        pending_count = sum(1 for j in jobs_after if j.get("status") == "pending")

        self.assert_true(pending_count > 0, f"应有 job 被重置为 pending（当前 {pending_count} 个）")
        # 有 artifact_map 条目的 job 及其下游应全部重置
        self.assert_eq(done_count, 0, f"所有 output job 都应重置为 pending（当前 {done_count} 个 done）")

    def run_tests(self):
        self._test_sync_stage_jobs_idempotent()
        self._test_dependency_order()
        self._test_pick_next_job_respects_deps()
        self._test_run_next_dry_run_no_writes()
        self._test_repair_stale_and_failed()
        self._test_pick_next_job_retries_blocking_deps()
        self._test_output_stage_creates_archived_extract_jobs()
        self._test_verify_artifacts_resets_missing_output()
