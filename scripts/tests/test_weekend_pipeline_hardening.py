#!/usr/bin/env python3
"""
test_weekend_pipeline_hardening.py — 周末流水线架构加固回归测试（v6.9.7）

覆盖五项改进：
    1. P0: dry-run 零落盘（run_next / run_stage 均不持久化状态）
    2. P1a: 声明式 artifact 字段完整性 + 产物校验三阶段通用化
       + finished_at 日期错位防误判 + 旧 state 字段级合并
    3. P1b: handler 注册 (stage, step) 二元组完整性（防漏注册/孤儿注册）
    4. P2a: processed_sources 滚动裁剪（旧记录删除、旧格式保留）
    5. P2b: file_lock 非阻塞模式 + run_next 锁忙温和退出 + run_stage
       per-job 粒度锁的功能等价性

注意：
    本测试不调用 LLM，handler 全部使用 stub，运行于隔离临时目录。
"""

import sys
import shutil
import importlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


def _utc_stamped(days_ago: int = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _fake_handler(state, job, dry_run=False):
    """stub handler：恒成功，零副作用。"""
    return {"success": True, "job_id": job.get("job_id", ""), "stub": True}


class WeekendPipelineHardeningTests(TestSuite):
    def __init__(self):
        super().__init__("周末流水线架构加固测试（v6.9.7）")
        self.tmp_root = None

    # ------------------------------------------------------------------
    # 隔离环境（与 test_weekend_pipeline.py 相同机制）
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")

        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("weekend_pipeline") or mod_name.startswith("proposal_lifecycle"):
                del sys.modules[mod_name]

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
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    def _make_pipeline(self):
        from weekend_pipeline.pipeline import WeekendPipeline
        return WeekendPipeline(state_path=self.tmp_root / "memory" / "weekend-pipeline.json")

    def _stub_handlers(self, p):
        """用 stub 替换 input 阶段 handlers（二元组注册）。"""
        return {
            (j["stage"], j["step"]): _fake_handler
            for j in p.list_jobs(stage="input")
        }

    # ------------------------------------------------------------------
    # P0: dry-run 零落盘
    # ------------------------------------------------------------------

    def _test_run_next_dry_run_persists_nothing(self):
        """run_next(dry_run=True) 执行后，磁盘状态必须保持 pending。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        p.handlers = self._stub_handlers(p)

        result = p.run_next(stage="input", dry_run=True)
        self.assert_true(result.get("success"), "dry-run run_next 成功", result)
        self.assert_eq(result.get("executed"), 1, "执行 1 个 job（内存中）")

        p2 = self._make_pipeline()
        first = p2.list_jobs(stage="input")[0]
        self.assert_eq(
            first.get("status"), "pending",
            "P0: dry-run 不得落盘假 done（磁盘应仍为 pending）",
        )
        self.assert_eq(
            p2.state.get("stage_status", {}).get("input"), "pending",
            "dry-run 不得改写 stage_status",
        )

    def _test_run_stage_dry_run_persists_nothing(self):
        """run_stage(dry_run=True) 全程不落盘（含 stage_status）。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        p.handlers = self._stub_handlers(p)

        result = p.run_stage("input", dry_run=True)
        self.assert_eq(result.get("executed"), 7, "dry-run run_stage 预览 7 个 job")

        p2 = self._make_pipeline()
        statuses = {j.get("status") for j in p2.list_jobs(stage="input")}
        self.assert_eq(
            statuses, {"pending"},
            "P0: run_stage dry-run 后磁盘全部 job 仍 pending",
        )
        self.assert_eq(
            p2.state.get("stage_status", {}).get("input"), "pending",
            "run_stage dry-run 不得将 stage_status 写为 running",
        )

    # ------------------------------------------------------------------
    # P1a: 声明式 artifact
    # ------------------------------------------------------------------

    def _test_artifact_declarations_complete(self):
        """模板产物声明覆盖度：input 7/7、reflection 6/7、output 4/5。"""
        from weekend_pipeline.jobs import stage_job_templates

        input_jobs = stage_job_templates("input")
        self.assert_eq(len(input_jobs), 7, "input 7 个 job")
        missing = [j["job_id"] for j in input_jobs if not j.get("artifact")]
        self.assert_eq(
            missing, [], f"input 全部 job 应声明 artifact（缺失: {missing}）",
        )

        reflection = stage_job_templates("reflection")
        declared = [j["job_id"] for j in reflection if j.get("artifact")]
        self.assert_eq(len(declared), 6, "reflection 应有 6 个 job 声明 artifact")
        merge = next(
            j for j in reflection if j["job_id"] == "reflection_kb_merge_duplicates"
        )
        self.assert_true(
            not merge.get("artifact"),
            "merge_duplicates 无确定性产物路径，应不声明（校验自然跳过）",
        )

        output = stage_job_templates("output", [])
        declared_out = [j for j in output if j.get("artifact")]
        self.assert_eq(len(declared_out), 4, "output 基础 job 应有 4 个声明 artifact")

    def _test_verify_artifacts_input_stage(self):
        """产物校验三阶段通用：input 假 done（无产物）→ sync 后重置。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        from weekend_pipeline.constants import JOB_STATUS_DONE
        today = _utc_stamped(0)
        for job in p.list_jobs(stage="input"):
            job["status"] = JOB_STATUS_DONE
            job["finished_at"] = today
        p._save()

        p2 = self._make_pipeline()
        p2.sync_stage_jobs("input")
        done_count = sum(
            1 for j in p2.list_jobs(stage="input") if j.get("status") == "done"
        )
        self.assert_eq(
            done_count, 0,
            "P1a: input 假 done（产物缺失）应被三阶段通用校验重置",
        )

    def _test_verify_artifacts_uses_finished_at_date(self):
        """{date} 以 job 自身 finished_at 格式化：昨天 done + 昨天产物在 → 不误重置。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        from weekend_pipeline.constants import JOB_STATUS_DONE
        yesterday = _utc_stamped(1)
        for job in p.list_jobs(stage="input"):
            job["status"] = JOB_STATUS_DONE
            job["finished_at"] = yesterday
        p._save()

        # 只创建 collect 的昨日产物；其余 6 个 job 产物缺失
        input_dir = self.tmp_root / "memory" / "weekend-input"
        input_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / f"sources-{yesterday[:10]}.json").write_text("{}", encoding="utf-8")

        p2 = self._make_pipeline()
        p2.sync_stage_jobs("input")
        jobs = {j["job_id"]: j.get("status") for j in p2.list_jobs(stage="input")}
        self.assert_eq(
            jobs.get("input_collect_sources"), "done",
            "P1a: 产物按 finished_at（昨日）定位且存在 → 不应误重置",
        )
        self.assert_eq(
            jobs.get("input_summarize_new_papers"), "pending",
            "产物缺失的 job 应重置",
        )
        self.assert_eq(
            jobs.get("input_compose_ideas"), "pending",
            "下游依赖应级联重置",
        )

    def _test_sync_backfills_artifact_field(self):
        """字段级合并：旧 state（无 artifact 字段）sync 后自动补齐。"""
        from weekend_pipeline.jobs import stage_job_templates
        from common import save_json

        # 构造旧格式 state：模板副本剥掉 artifact 字段
        legacy_jobs = []
        for t in stage_job_templates("input"):
            legacy = {k: v for k, v in t.items() if k != "artifact"}
            legacy_jobs.append(legacy)
        state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        save_json(state_path, {"jobs": legacy_jobs, "stage_status": {}})

        p = self._make_pipeline()
        result = p.sync_stage_jobs("input")
        self.assert_eq(result.get("added"), 0, "旧 job 已存在，不重复新增")

        jobs = p.list_jobs(stage="input")
        missing = [j["job_id"] for j in jobs if not j.get("artifact")]
        self.assert_eq(
            missing, [],
            "P1a: sync 应向旧 state job 补齐 artifact 声明（零迁移）",
        )

    # ------------------------------------------------------------------
    # P1b: handler 二元组注册
    # ------------------------------------------------------------------

    def _test_handler_registry_covers_all_templates(self):
        """每个模板 (stage, step) 均有 handler 注册；无孤儿注册。"""
        from weekend_pipeline.jobs import stage_job_templates

        p = self._make_pipeline()
        templates = (
            stage_job_templates("input")
            + stage_job_templates("output", [])
            + stage_job_templates("reflection")
        )
        missing = [
            j["job_id"] for j in templates
            if (j["stage"], j["step"]) not in p.handlers
        ]
        self.assert_eq(
            missing, [],
            f"P1b: 存在未注册 handler 的模板（缺失: {missing}）",
        )

        template_keys = {(j["stage"], j["step"]) for j in templates}
        orphans = [k for k in p.handlers if k not in template_keys]
        self.assert_eq(
            orphans, [],
            f"P1b: 存在孤儿 handler 注册（无对应模板: {orphans}）",
        )

        # 二元组隔离验证：同名 step 跨阶段各自独立
        self.assert_true(
            ("input", "collect") in p.handlers and ("output", "collect") in p.handlers,
            "同名 step collect 在 input/output 阶段应各自独立注册",
        )

    # ------------------------------------------------------------------
    # P2a: processed_sources 滚动裁剪
    # ------------------------------------------------------------------

    def _test_trim_processed_sources(self):
        from weekend_pipeline.state import trim_processed_sources

        state = {
            "processed_sources": {
                "src-old": {"hash": "a", "processed_at": _utc_stamped(35)},
                "src-recent": {"hash": "b", "processed_at": _utc_stamped(3)},
                "src-legacy": "plainhash",  # 旧格式（纯字符串）
                "src-edge": {"hash": "d"},  # 新格式但缺 processed_at
            }
        }
        removed = trim_processed_sources(state)
        self.assert_eq(removed, 1, "P2a: 仅 1 条过期记录被裁剪")
        self.assert_true(
            "src-old" not in state["processed_sources"], "35 天前记录应删除",
        )
        self.assert_true(
            "src-recent" in state["processed_sources"], "3 天前记录应保留",
        )
        self.assert_true(
            "src-legacy" in state["processed_sources"],
            "旧格式（无时间戳）应保留不误删",
        )
        self.assert_true(
            "src-edge" in state["processed_sources"],
            "缺 processed_at 的记录视为无法判定年龄，保留",
        )

    # ------------------------------------------------------------------
    # P2b: 锁粒度与温和退出
    # ------------------------------------------------------------------

    def _test_file_lock_nonblocking_raises_timeout(self):
        from common import file_lock

        with file_lock("hardening-test-lock"):
            raised = False
            try:
                with file_lock("hardening-test-lock", blocking=False):
                    pass
            except TimeoutError:
                raised = True
            self.assert_true(
                raised, "P2b: 非阻塞抢锁失败应抛 TimeoutError",
            )

    def _test_run_next_exits_gracefully_on_busy_lock(self):
        """锁被占时 run_next 温和退出（skipped=lock_busy），不阻塞不报错。"""
        from common import file_lock

        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        p.handlers = self._stub_handlers(p)

        with file_lock("weekend-pipeline"):
            result = p.run_next(stage="input")
        self.assert_eq(
            result.get("skipped"), "lock_busy",
            "P2b: 锁忙时应温和退出并标记 skipped=lock_busy",
        )
        self.assert_eq(result.get("executed"), 0, "锁忙时不应执行任何 job")
        self.assert_true(result.get("success"), "锁忙退出本身不算失败")

        p2 = self._make_pipeline()
        first = p2.list_jobs(stage="input")[0]
        self.assert_eq(
            first.get("status"), "pending", "锁忙退出不得改动磁盘状态",
        )

    def _test_run_stage_per_job_lock_functional(self):
        """per-job 粒度锁下 run_stage 功能等价：7 个 job 依次全部 done。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        p.handlers = self._stub_handlers(p)

        result = p.run_stage("input")
        self.assert_eq(result.get("executed"), 7, "P2b: per-job 锁下仍应跑完 7 个 job")
        self.assert_eq(len(result.get("results", [])), 7, "每个 job 有独立结果")

        p2 = self._make_pipeline()
        statuses = {j.get("status") for j in p2.list_jobs(stage="input")}
        self.assert_eq(statuses, {"done"}, "全部 job 落盘为 done")
        self.assert_eq(
            p2.state.get("stage_status", {}).get("input"), "done",
            "阶段终态应为 done",
        )

    def run_tests(self):
        self._test_run_next_dry_run_persists_nothing()
        self._test_run_stage_dry_run_persists_nothing()
        self._test_artifact_declarations_complete()
        self._test_verify_artifacts_input_stage()
        self._test_verify_artifacts_uses_finished_at_date()
        self._test_sync_backfills_artifact_field()
        self._test_handler_registry_covers_all_templates()
        self._test_trim_processed_sources()
        self._test_file_lock_nonblocking_raises_timeout()
        self._test_run_next_exits_gracefully_on_busy_lock()
        self._test_run_stage_per_job_lock_functional()


if __name__ == "__main__":
    suite = WeekendPipelineHardeningTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    import test_runner
    test_runner.print_summary([suite])
    sys.exit(0 if suite.failed == 0 else 1)
