#!/usr/bin/env python3
"""
test_weekend_orchestrator_dryrun.py — 周末编排器 dry-run 零落盘回归测试（v6.10.16）

背景（09-14 实证）：
    weekend_orchestrator 的 run_*_task 声称透传 dry_run，但
    _update_job_status（写 weekend-jobs.json 的 RUNNING/FAILED/DONE
    终态）与 pipeline.sync_stage_jobs（含产物缺失级联重置，会把磁盘
    done job 落盘回 pending）不受 dry_run 保护——`--output --dry-run`
    曾把 weekend_output 误标 failed + attempts+1，并触发 output/sync
    与 weekly_report 级联重置。

覆盖：
    1. dry-run 全 done 阶段：两个状态文件零写入、不触发 sync
    2. dry-run 未完成阶段：不误标 failed，返回 note 提示
    3. 真实执行（非 dry-run）：sync 正常触发、weekend-jobs.json 正常
       推进 done（保证修复未破坏真实链路）
    4. 异常路径：dry-run 不写 failed；非 dry-run 照写（原语义保持）

注意：
    不调用 LLM：WeekendPipeline 经 wrapper 注入，run_stage/sync_stage_jobs
    全部 stub；运行于隔离临时目录。
"""

import json
import shutil
import sys
import importlib

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT

# 预构造的 output 阶段 job 模板（artifact 故意指向不存在的文件，
# 重现旧 bug 的产物缺失级联重置路径）
_DONE_OUTPUT_JOBS = [
    {
        "job_id": "output_sync_proposals_to_kb",
        "stage": "output", "step": "sync", "status": "done",
        "depends_on": [], "attempts": 0, "scheduled_at": "",
        "started_at": "2026-09-12T06:01:02Z",
        "finished_at": "2026-09-12T06:01:03Z", "last_error": "",
        "created_at": "2026-07-29T06:03:33Z",
        "artifact": "knowledge/wiki/projects/NSFC-强场超快/proposals/proposals-index.md",
    },
    {
        "job_id": "output_collect", "stage": "output", "step": "collect",
        "status": "done", "depends_on": [], "attempts": 0,
        "started_at": "2026-09-12T06:01:03Z",
        "finished_at": "2026-09-12T06:01:03Z", "last_error": "",
        "created_at": "2026-07-29T06:03:33Z",
    },
    {
        "job_id": "output_extract_daily_knowledge", "stage": "output",
        "step": "extract", "status": "done",
        "depends_on": ["output_sync_proposals_to_kb"], "attempts": 0,
        "started_at": "2026-09-12T06:01:03Z",
        "finished_at": "2026-09-12T06:01:44Z", "last_error": "",
        "created_at": "2026-07-29T06:03:33Z",
    },
    {
        "job_id": "output_kb_health_check", "stage": "output", "step": "health",
        "status": "done",
        "depends_on": ["output_extract_daily_knowledge"], "attempts": 0,
        "started_at": "2026-09-12T06:01:44Z",
        "finished_at": "2026-09-12T06:01:46Z", "last_error": "",
        "created_at": "2026-07-29T06:03:33Z",
    },
    {
        "job_id": "output_generate_weekly_report", "stage": "output",
        "step": "weekly_report", "status": "done",
        "depends_on": ["output_sync_proposals_to_kb",
                       "output_extract_daily_knowledge", "output_kb_health_check"],
        "attempts": 0,
        "started_at": "2026-09-12T06:01:46Z",
        "finished_at": "2026-09-12T06:01:46Z", "last_error": "",
        "created_at": "2026-07-29T06:03:33Z",
        "artifact": "memory/weekend-output/weekend-output-report-{date}.md",
    },
]

_DONE_WEEKEND_JOBS = {
    "jobs": {
        "weekend_input": {"status": "done", "last_run": "",
                          "started_at": "2026-09-13T11:30:16Z",
                          "finished_at": "2026-09-13T11:30:16Z",
                          "last_error": "", "attempts": 5},
        "weekend_output": {"status": "done", "last_run": "",
                           "started_at": "2026-09-12T06:00:59Z",
                           "finished_at": "2026-09-12T06:01:46Z",
                           "last_error": "", "attempts": 2},
        "weekend_reflection": {"status": "done", "last_run": "",
                               "started_at": "2026-09-13T01:00:44Z",
                               "finished_at": "2026-09-13T01:03:30Z",
                               "last_error": "", "attempts": 4},
    },
    "updated_at": "2026-09-13T11:30:16Z",
}


class _StubPipeline:
    """wrapper：包装真实 WeekendPipeline，stub 掉会触碰 LLM/复杂逻辑的部分。

    - sync_stage_jobs：不落盘，只累计类级计数（函数内部创建的实例也可观测）
    - run_stage：返回可注入的固定结果（默认 executed=0 成功），可注入异常
    - state / list_jobs：透传真实状态（_stage_actually_done 需要真实读）
    """

    sync_calls_total = 0  # 类级计数器：跨实例累计 sync 触发次数

    def __init__(self, state_path=None):
        from weekend_pipeline.pipeline import WeekendPipeline
        self._real = WeekendPipeline(state_path=state_path) if state_path else WeekendPipeline()
        self.stage_result = {"success": True, "stage": "output",
                             "dry_run": True, "executed": 0, "results": []}
        self.raise_on_run = False

    @property
    def state(self):
        return self._real.state

    def list_jobs(self, stage=None):
        return self._real.list_jobs(stage=stage)

    def sync_stage_jobs(self, stage):
        _StubPipeline.sync_calls_total += 1
        return {"success": True, "stage": stage, "added": 0}

    def run_stage(self, stage, dry_run=False):
        if self.raise_on_run:
            raise RuntimeError("注入的执行失败")
        result = dict(self.stage_result)
        result["stage"] = stage
        result["dry_run"] = dry_run
        return result


class WeekendOrchestratorDryRunTests(TestSuite):
    def __init__(self):
        super().__init__("周末编排器 dry-run 零落盘回归（v6.10.16）")
        self.tmp_root = None
        self._saved_impl = None

    # ------------------------------------------------------------------
    # 隔离环境
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")

        # weekend_orchestrator 的 WEEKEND_JOBS_PATH 是 import 时按
        # PROJECT_ROOT 求值的模块常量——必须先清缓存、打补丁、再 import
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("weekend_pipeline") or mod_name.startswith("proposal_lifecycle") \
                    or mod_name == "weekend_orchestrator":
                del sys.modules[mod_name]

        import paths
        self._orig_project_root = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root

        import proposal_lifecycle.constants as plc
        plc.PROJECT_ROOT = self.tmp_root
        plc.PROPOSALS_ROOT = self.tmp_root / "research_proposals"

        importlib.import_module("weekend_pipeline")
        patch_module_root("weekend_pipeline", self.tmp_root)
        patch_module_root("proposal_lifecycle", self.tmp_root)

        self.orch = importlib.import_module("weekend_orchestrator")

        # 用 wrapper 替换 weekend_pipeline.WeekendPipeline（run_*_task
        # 函数体内 from weekend_pipeline import WeekendPipeline 动态取属性）
        import weekend_pipeline
        self._saved_impl = weekend_pipeline.WeekendPipeline
        weekend_pipeline.WeekendPipeline = _StubPipeline

    def teardown(self):
        import weekend_pipeline
        if self._saved_impl is not None:
            weekend_pipeline.WeekendPipeline = self._saved_impl
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root
        # 套件间模块卫生：清掉绑定临时根的模块缓存
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("weekend_pipeline") or mod_name.startswith("proposal_lifecycle") \
                    or mod_name == "weekend_orchestrator":
                del sys.modules[mod_name]

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------

    def _pipeline_path(self):
        return self.tmp_root / "memory" / "weekend-pipeline.json"

    def _jobs_path(self):
        return self.tmp_root / "memory" / "weekend-jobs.json"

    def _seed_state(self, jobs=None, stage_status="done"):
        """预构造磁盘状态：output 阶段全 done（或注入 pending）。"""
        seed_jobs = json.loads(json.dumps(_DONE_OUTPUT_JOBS))
        if jobs:
            for patch_job in jobs:
                for j in seed_jobs:
                    if j["job_id"] == patch_job["job_id"]:
                        j.update(patch_job)
        state = {
            "jobs": seed_jobs,
            "stage_status": {"input": "done", "output": stage_status, "reflection": "done"},
            "updated_at": "2026-09-13T14:20:40Z",
            "processed_sources": {},
        }
        self._pipeline_path().write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        self._jobs_path().write_text(
            json.dumps(_DONE_WEEKEND_JOBS, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_json(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # 用例
    # ------------------------------------------------------------------

    def run_tests(self):
        self._test_dry_run_all_done_writes_nothing()
        self._test_dry_run_incomplete_stage_no_fail_mark()
        self._test_dry_run_skips_sync_and_status_writes()
        self._test_real_run_updates_status_normally()
        self._test_exception_path_semantics()
        self._test_reconcile_aligns_finished_at_on_done_drift()

    def _test_dry_run_all_done_writes_nothing(self):
        """dry-run（全 done 阶段）：两个状态文件零写入，不触发 sync。"""
        self._seed_state()
        before_pipeline = self._pipeline_path().read_text(encoding="utf-8")
        before_jobs = self._jobs_path().read_text(encoding="utf-8")

        result = self.orch.run_output_task(dry_run=True)

        self.assert_true(result.get("success"), "dry-run 返回成功", result)
        self.assert_eq(
            self._pipeline_path().read_text(encoding="utf-8"), before_pipeline,
            "P0: dry-run 不得改写 weekend-pipeline.json（旧 bug：产物缺失级联重置 done→pending）",
        )
        self.assert_eq(
            self._jobs_path().read_text(encoding="utf-8"), before_jobs,
            "P0: dry-run 不得改写 weekend-jobs.json（旧 bug：误标 failed + attempts+1）",
        )
        # wrapper 透传：run_output_task 内部实例化的就是 _StubPipeline
        # sync 调用计数通过返回结果无从直接断言，改由下面专门用例覆盖

    def _test_dry_run_incomplete_stage_no_fail_mark(self):
        """dry-run（阶段未完成）：不误标 failed，返回 note 说明。"""
        self._seed_state(
            jobs=[{"job_id": "output_sync_proposals_to_kb", "status": "pending"}],
            stage_status="pending",
        )
        before_jobs = self._jobs_path().read_text(encoding="utf-8")

        result = self.orch.run_output_task(dry_run=True)

        self.assert_true(result.get("success"),
                         "dry-run 预览不得把 success 改 False（磁盘状态非其责任）", result)
        self.assert_true("note" in result, "未完成阶段 dry-run 返回 note 提示", result)
        self.assert_eq(
            self._jobs_path().read_text(encoding="utf-8"), before_jobs,
            "dry-run 未完成阶段也不写 weekend-jobs.json（旧 bug：误标 failed）",
        )

    def _test_dry_run_skips_sync_and_status_writes(self):
        """dry-run 不触发 sync_stage_jobs；非 dry-run 照常触发（类级计数）。"""
        self._seed_state()
        _StubPipeline.sync_calls_total = 0

        result = self.orch.run_output_task(dry_run=True)
        self.assert_true(result.get("success"), "dry-run 成功", result)
        self.assert_eq(_StubPipeline.sync_calls_total, 0,
                       "dry-run 不得触发 sync_stage_jobs（产物自愈重置属于真实执行行为）")

        result2 = self.orch.run_output_task(dry_run=False)
        self.assert_true(result2.get("success"), "真实执行成功", result2)
        self.assert_eq(_StubPipeline.sync_calls_total, 1,
                       "非 dry-run 正常触发一次 sync_stage_jobs")

    def _test_real_run_updates_status_normally(self):
        """非 dry-run：sync 正常触发、weekend-jobs.json 正常推进（回归保护）。"""
        self._seed_state()
        result = self.orch.run_output_task(dry_run=False)

        self.assert_true(result.get("success"), "真实执行成功", result)
        jobs = self._read_json(self._jobs_path())
        out = jobs.get("jobs", {}).get("weekend_output", {})
        self.assert_eq(out.get("status"), "done",
                       "真实执行后 weekend_output=done（阶段全 done → DONE 写入）")
        self.assert_eq(out.get("started_at"), "2026-09-12T06:01:02Z",
                       "阶段级 started_at 取子 job 最早开始时间（非入口 tick 的 now）")
        self.assert_eq(out.get("finished_at"), "2026-09-12T06:01:46Z",
                       "阶段级 finished_at 取子 job 最晚完成时间（非入口 tick 的 now）")
        self.assert_true(jobs.get("updated_at", "") > "2026-09-13T11:30:16Z",
                         "weekend-jobs.json 的 updated_at 已刷新")

    def _test_exception_path_semantics(self):
        """异常路径：dry-run 不写 failed；非 dry-run 照写 failed（原语义保持）。"""
        # dry-run：不落盘
        self._seed_state()
        before_jobs = self._jobs_path().read_text(encoding="utf-8")
        import weekend_pipeline

        class _Boom(_StubPipeline):
            def __init__(self, state_path=None):
                super().__init__(state_path)
                self.raise_on_run = True

        weekend_pipeline.WeekendPipeline = _Boom
        try:
            result = self.orch.run_output_task(dry_run=True)
            self.assert_true(not result.get("success"), "异常时 success=False", result)
            self.assert_eq(result.get("dry_run"), True, "返回体标注 dry_run")
            self.assert_eq(
                self._jobs_path().read_text(encoding="utf-8"), before_jobs,
                "dry-run 异常路径也不写 weekend-jobs.json",
            )

            # 非 dry-run：照写 failed（原语义）
            result2 = self.orch.run_output_task(dry_run=False)
            self.assert_true(not result2.get("success"), "真实执行异常 success=False")
            jobs = self._read_json(self._jobs_path())
            out = jobs.get("jobs", {}).get("weekend_output", {})
            self.assert_eq(out.get("status"), "failed",
                           "真实执行异常照写 failed（原语义保持）")
            self.assert_eq(out.get("attempts"), 3,
                           "attempts 2→3（failed 计数 +1，原语义保持）")
        finally:
            weekend_pipeline.WeekendPipeline = self._saved_impl

    def _test_reconcile_aligns_finished_at_on_done_drift(self):
        """对齐层：done→done 时若末个 job 时间戳更新，finished_at 必须跟随。

        陈旧场景（11-08 实证）：阶段在两轮之间被标 done，新一轮 job 继续
        推进；旧实现只在状态变化时写回，finished_at 永久停在旧轮次。
        """
        self._seed_state()
        jobs_data = self._read_json(self._jobs_path())
        jobs_data["jobs"]["weekend_output"]["finished_at"] = "2026-09-12T06:00:00Z"
        self._jobs_path().write_text(
            json.dumps(jobs_data, ensure_ascii=False, indent=2), encoding="utf-8")

        # dry-run 不改写，但变更预览必须非空（否则预览恒为空、看不出漂移）
        before = self._jobs_path().read_text(encoding="utf-8")
        dry = self.orch.reconcile_weekend_jobs(dry_run=True)
        self.assert_eq(self._jobs_path().read_text(encoding="utf-8"), before,
                       "dry-run 不得修正时间戳")
        self.assert_eq(dry.get("changed", {}).get("weekend_output", {})
                       .get("finished_at", {}).get("to"), "2026-09-12T06:01:46Z",
                       "dry-run 预览标注将要修正的 finished_at")

        # 真实执行：finished_at 对齐到 output 末个 job 的 06:01:46Z，状态仍 done
        result = self.orch.reconcile_weekend_jobs(dry_run=False)
        jobs = self._read_json(self._jobs_path())
        out = jobs.get("jobs", {}).get("weekend_output", {})
        self.assert_eq(out.get("finished_at"), "2026-09-12T06:01:46Z",
                       "done 阶段 finish 时间戳跟随后续 job 更新")
        self.assert_eq(out.get("status"), "done", "状态仍为 done")
        self.assert_eq(result.get("changed", {}).get("weekend_output", {})
                       .get("finished_at", {}).get("to"), "2026-09-12T06:01:46Z",
                       "变更记录标注 finished_at 修正")


if __name__ == "__main__":
    suite = WeekendOrchestratorDryRunTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    import test_runner
    test_runner.print_report([suite])
    sys.exit(0 if suite.summary()["failed"] == 0 else 1)
