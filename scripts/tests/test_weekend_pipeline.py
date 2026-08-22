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
import json
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
        self.assert_eq(len(result.get("jobs", [])), 6, "input 阶段 6 个 job（v6.9.12 知识簇链路）")

        result2 = p.sync_stage_jobs("input")
        self.assert_eq(result2.get("added"), 0, "重复 sync 不新增")
        self.assert_eq(len(p.list_jobs(stage="input")), 6, "input job 数量保持 6")

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

        # 模拟：collect 已完成，summarize 失败，cluster_assign 等待 summarize
        jobs[0]["status"] = "done"  # input_collect_sources
        jobs[1]["status"] = "failed"  # input_summarize_new_papers
        jobs[1]["attempts"] = 1
        jobs[1]["repair_attempts"] = 0
        p._save()

        from weekend_pipeline.executor import pick_next_job
        job = pick_next_job(p.state, stage="input")

        # pick_next_job 应发现 summarize 是 failed 且阻塞 cluster_assign → 重置为 pending
        self.assert_true(job is not None, "应返回一个 job")
        self.assert_eq(job["job_id"], "input_summarize_new_papers", "应返回被修复的 failed 依赖")
        self.assert_eq(job["status"], "pending", "被修复的 job 应为 pending")
        self.assert_eq(job["repair_attempts"], 1, "repair_attempts 应 +1")

        # 验证 cluster_assign 的依赖现在满足
        ca = next(j for j in p.state.get("jobs", []) if j["job_id"] == "input_cluster_assign")
        self.assert_eq(ca["status"], "pending", "cluster_assign 仍为 pending")

    def _test_sync_refreshes_stale_depends_on(self):
        """v6.9.13 回归：链路重构后 sync 必须刷新旧 state 的 depends_on。

        场景（08-15 实测死锁）：v6.9.12 部署前 state 里
        input_compose_ideas.depends_on=["input_deep_read"]，废弃清理删掉
        input_deep_read 后该依赖永远无法满足 → compose 永久 pending、
        input 阶段永无终态。
        """
        p = self._make_pipeline()
        # 预置旧链路形状 state（模拟 v6.9.12 之前的周末遗留）
        p.state["jobs"] = [
            {
                "job_id": "input_collect_sources", "stage": "input", "step": "collect",
                "status": "done", "depends_on": [], "attempts": 0,
                "finished_at": "2026-08-15T11:54:36Z",
                "artifact": "memory/weekend-input/sources-{date}.json",
            },
            {
                "job_id": "input_deep_read", "stage": "input", "step": "deep_read",
                "status": "done", "depends_on": ["input_retrieve_supplementary"],
                "attempts": 0, "finished_at": "2026-08-15T10:00:00Z",
            },
            {
                "job_id": "input_compose_ideas", "stage": "input", "step": "compose",
                "status": "pending", "depends_on": ["input_deep_read"],
                "attempts": 0, "artifact": "memory/weekend-input/ideas-{date}.json",
            },
        ]
        p._save()

        p.sync_stage_jobs("input")
        jobs = p.list_jobs(stage="input")
        job_ids = {j["job_id"] for j in jobs}

        # 废弃 job 已清理
        self.assert_true("input_deep_read" not in job_ids, "废弃 job input_deep_read 应被清理")
        # 依赖已刷新为当前模板链
        compose = next(j for j in jobs if j["job_id"] == "input_compose_ideas")
        self.assert_eq(
            compose.get("depends_on"), ["input_topic_match"],
            "旧 state 的 depends_on 应被模板刷新（否则永久死锁）",
        )

        # 全链 done 后 compose 可被挑选（死锁解除）
        for j in jobs:
            if j["job_id"] != "input_compose_ideas":
                j["status"] = "done"
        p._save()
        from weekend_pipeline.executor import pick_next_job
        job = pick_next_job(p.state, stage="input")
        self.assert_true(job is not None, "compose 不应因旧依赖死锁")
        self.assert_eq(job["job_id"], "input_compose_ideas", "前序全 done 后应挑中 compose")

    def _test_dependencies_satisfied_strict_missing_dep(self):
        """v6.9.13 回归：依赖 job 缺失时保持严格阻塞（不放行）。

        放行会在"代码已更新、state 未 sync"窗口期让 compose 被提前
        挑中并以空路由落地（丢整周路由）；死锁的正确解法是
        sync_stage_jobs 的依赖刷新（见上一用例）。
        """
        from weekend_pipeline.executor import dependencies_satisfied
        state = {"jobs": [{"job_id": "a", "status": "done"}]}
        # "ghost" 不存在于 state：仍阻塞（严格语义，等待 sync 刷新依赖）
        self.assert_true(
            not dependencies_satisfied({"depends_on": ["a", "ghost"]}, state),
            "缺失依赖必须保持阻塞，防止 sync 前被提前挑中",
        )
        # 存在且已完成：满足
        self.assert_true(
            dependencies_satisfied({"depends_on": ["a"]}, state),
            "已完成的依赖应满足",
        )
        # 存在但未完成：阻塞
        state2 = {"jobs": [{"job_id": "a", "status": "done"}, {"job_id": "b", "status": "pending"}]}
        self.assert_true(
            not dependencies_satisfied({"depends_on": ["b"]}, state2),
            "存在且未完成的依赖仍应阻塞",
        )

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

    def _test_kb_health_field_fallback_in_weekly_report(self):
        """验证 output 周报生成时兼容 kb.get_kb_health() 的字段名（wiki_count/raw_count）。

        背景：kb_index.get_kb_health() 实际返回字段是 wiki_count / raw_count /
        hermes_wiki_count，而旧版输出报告渲染时读 total_pages / by_type，导致
        "知识库共 0 页" 显示错误。修复后应能正确合计显示 wiki + raw 数量。
        """
        # 在隔离环境中写入一份 kb-health-weekly.json（沿用 kb.get_kb_health 实际字段）
        cache_dir = self.tmp_root / "knowledge" / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        health_report = {
            "checked_at": "2026-08-09T12:00:00Z",
            "health": {
                "indexed": True,
                "raw_count": 226,
                "wiki_count": 153,
                "hermes_wiki_count": 12,
                "chunks": 4658,
            },
            "derived_overdue": [],
            "derived_overdue_count": 0,
        }
        (cache_dir / "kb-health-weekly.json").write_text(
            json.dumps(health_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # 调用 run_output_generate_weekly_report 生成报告
        import weekend_pipeline.output_jobs as oj_mod
        from weekend_pipeline.constants import WEEKEND_OUTPUT_DIR
        from weekend_pipeline import constants as wp_const

        # 把 HEALTH_REPORT_PATH 和 WEEKEND_OUTPUT_DIR 都指向隔离环境
        orig_health_path = oj_mod.HEALTH_REPORT_PATH
        orig_output_dir = wp_const.WEEKEND_OUTPUT_DIR
        oj_mod.HEALTH_REPORT_PATH = cache_dir / "kb-health-weekly.json"
        # 隔离目录下的 memory/weekend-output
        isolated_output_dir = self.tmp_root / "memory" / "weekend-output"
        isolated_output_dir.mkdir(parents=True, exist_ok=True)
        wp_const.WEEKEND_OUTPUT_DIR = isolated_output_dir
        # output_jobs.py 顶层也导入了该常量，所以需要同步 patch 模块命名空间
        oj_mod.WEEKEND_OUTPUT_DIR = isolated_output_dir
        try:
            state = {
                "jobs": [
                    {
                        "job_id": "output_kb_health_check",
                        "stage": "output",
                        "step": "health",
                        "status": "done",
                        "result": {
                            "report": {
                                "derived_overdue_count": 2,
                                "health": {
                                    "raw_count": 226,
                                    "wiki_count": 153,
                                    "hermes_wiki_count": 12,
                                },
                            }
                        },
                    }
                ]
            }
            result = oj_mod.run_output_generate_weekly_report(
                state, {}, dry_run=False
            )
            self.assert_true(result.get("success"), "周报生成成功", result)

            # 找到生成的报告并校验关键内容
            report_files = sorted(isolated_output_dir.glob("weekend-output-report-*.md"))
            self.assert_true(len(report_files) > 0, "应生成周报文件")
            content = report_files[-1].read_text(encoding="utf-8")

            # 总页数 = 226 + 153 + 12 = 391
            self.assert_in("知识库共 391 页", content, "应合计 wiki+raw+hermes_wiki 并显示非零")
            # by_type fallback 应包含 wiki/raw 明细
            self.assert_in("wiki: 153 页", content, "应列出 wiki 明细")
            self.assert_in("raw: 226 页", content, "应列出 raw 明细")
        finally:
            oj_mod.HEALTH_REPORT_PATH = orig_health_path
            wp_const.WEEKEND_OUTPUT_DIR = orig_output_dir
            oj_mod.WEEKEND_OUTPUT_DIR = orig_output_dir

    def _test_reset_stage_uses_own_recency_not_global_updated_at(self):
        """v6.8.53: 跨周重置应以阶段自身最近完成时间为准，而非全局 updated_at。

        运行时缺陷（已证实）：input job 08-01 全部 done 后，周六 output/reflection
        （及 weekend-worker 每 20 分钟）先跑刷新全局 updated_at → input 的跨周
        重置永不触发 → weekend_input 变 no-op 却标记成功，研究设想停摆两周。

        v6.9.38: 跨周口径从滚动 144h 改自然周锚点后，本用例注入固定时钟
        （周六 09:00，即入口 cron 实际触发时刻），消除旧版"8 天前"构造在
        不同星期跑测试时的行为漂移。
        """
        from datetime import datetime, timezone, timedelta

        # 冻结到周六 09:00 本地（入口 cron 时刻）：用 subclass 替换模块级 datetime
        real_dt = self.wp_mod.pipeline.datetime

        class _FrozenDT(real_dt):
            @classmethod
            def now(cls, tz=None):
                base = datetime(2026, 8, 22, 1, 0, 0, tzinfo=timezone.utc)  # 09:00 本地
                return base if tz is not None else base.astimezone()
        self.wp_mod.pipeline.datetime = _FrozenDT
        try:
            p = self._make_pipeline()
            p.sync_stage_jobs("input")
            eight_days_ago = (
                datetime(2026, 8, 14, 3, 0, 0, tzinfo=timezone.utc)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            for job in p.list_jobs(stage="input"):
                job["status"] = "done"
                job["finished_at"] = eight_days_ago
            p._save()

            # 全局 updated_at 被 output/reflection 刷新为"刚刚"（模拟同日其他阶段先跑）
            p.state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            p._save()

            p2 = self._make_pipeline()  # 重新加载状态
            p2.sync_stage_jobs("input")
            pending_count = sum(
                1 for j in p2.list_jobs(stage="input") if j.get("status") == "pending"
            )
            self.assert_eq(
                pending_count, 6,
                "全局 updated_at 新鲜但 input 自身完成早于本周六锚点 → 应重置全部 job",
            )
        finally:
            self.wp_mod.pipeline.datetime = real_dt

    def _test_reset_stage_not_triggered_within_week(self):
        """v6.9.38: 本周末内刚完成 → 不重置（同周末幂等）。

        旧版语义为"滚动 2 天内不重置"，与自然周锚点口径冲突（周六跑测试时
        2 天前 = 上周四，按新口径属上周应重置——这正是修复目标：上周完成
        本周入口应重跑）。改用本周末内（周六 00:30 本地）完成构造，并注入
        固定时钟消除星期依赖。
        """
        from datetime import datetime, timezone

        real_dt = self.wp_mod.pipeline.datetime

        class _FrozenDT(real_dt):
            @classmethod
            def now(cls, tz=None):
                base = datetime(2026, 8, 22, 4, 0, 0, tzinfo=timezone.utc)  # 12:00 本地
                return base if tz is not None else base.astimezone()
        self.wp_mod.pipeline.datetime = _FrozenDT
        try:
            p = self._make_pipeline()
            p.sync_stage_jobs("input")
            # 周六 00:30 本地（= 前一日 16:30 UTC），晚于锚点周六 00:00 本地
            within_weekend = "2026-08-21T16:30:00Z"
            date_str = "2026-08-21"  # 产物校验按 finished_at 的 UTC 日期定位
            # v6.9.7: 产物校验三阶段通用化后，input 的 done job 也会按
            # finished_at 日期检查产物。补齐当日产物文件，保持本测试
            # "同周末不重置"的语义（产物齐全 → 不触发产物重置）。
            artifacts = [
                "sources", "summaries", "clusters-week", "distilled-clusters",
                "routes", "ideas",
            ]
            input_dir = self.tmp_root / "memory" / "weekend-input"
            input_dir.mkdir(parents=True, exist_ok=True)
            for name in artifacts:
                (input_dir / f"{name}-{date_str}.json").write_text("{}", encoding="utf-8")

            for job in p.list_jobs(stage="input"):
                job["status"] = "done"
                job["finished_at"] = within_weekend
            p._save()

            p2 = self._make_pipeline()
            p2.sync_stage_jobs("input")
            done_count = sum(
                1 for j in p2.list_jobs(stage="input") if j.get("status") == "done"
            )
            self.assert_eq(done_count, 6, "本周末内完成且产物齐全 → 不应重置")
        finally:
            self.wp_mod.pipeline.datetime = real_dt

    def _test_weekend_stage_catchup(self):
        """v6.9.19: 入口 cron 错过的周末阶段由 repair 补 sync（决策 + 接线）。

        背景：跨周重置只发生在入口 cron 的 sync_stage_jobs 里——08-16
        实测反思入口 cron（周日 09:00）撞上系统卡死窗口失败，20 分钟
        worker 只推进 pending job 不触发重置，本周反思整段空缺。
        """
        from datetime import datetime
        from lifecycle.orchestrator import _weekend_catchup_decisions, _weekend_stage_catchup

        # --- 决策：周日中午，三阶段上周完成（本周末零活动）→ 全超期
        state = {"jobs": [
            {"stage": "input", "started_at": "2026-08-08T01:00:00Z",
             "finished_at": "2026-08-08T02:00:00Z", "status": "done"},
            {"stage": "output", "started_at": "2026-08-08T06:00:00Z",
             "finished_at": "2026-08-08T06:06:00Z", "status": "done"},
            {"stage": "reflection", "started_at": "2026-08-02T01:00:00Z",
             "finished_at": "2026-08-08T09:05:00Z", "status": "done"},
        ]}
        d = _weekend_catchup_decisions(state, datetime(2026, 8, 16, 12, 0))
        self.assert_eq(d, {"input": True, "output": True, "reflection": True},
                       "周日中午全零活动 → 三阶段全部超期")

        # --- 决策：周六中午 → 仅 input（09:00 窗口已过）超期
        d = _weekend_catchup_decisions(state, datetime(2026, 8, 15, 12, 0))
        self.assert_eq(d, {"input": True, "output": False, "reflection": False},
                       "周六中午只有 input 窗口已过")

        # --- 决策：本周末已有活动 → 不重复触发
        state_active = {"jobs": [
            {"stage": "input", "started_at": "2026-08-15T01:30:00Z",
             "finished_at": "2026-08-15T05:47:00Z", "status": "done"},
        ]}
        d = _weekend_catchup_decisions(state_active, datetime(2026, 8, 16, 12, 0))
        self.assert_true(d.get("input") is False, "本周末已跑的阶段不应补跑")
        self.assert_true(d.get("reflection") is True, "零活动阶段仍应补跑")

        # --- 接线：超期阶段实际调用 sync（monkeypatch 计数）
        class _FakePipeline:
            def __init__(self):
                self.state = state  # 全零活动状态
                self.state_path = None
                self.synced = []
            def sync_stage_jobs(self, stage):
                self.synced.append(stage)
                return {"success": True}

        fake = _FakePipeline()
        # v6.9.34: 注入固定时钟（周日中午，与上方决策用例一致）——真实时钟
        # 下周六凌晨 00:00-09:30 运行时三阶段入口窗口均未过，decisions 全
        # False，接线断言必然失败（08-22 00h 健康检查实证 959/961）
        caught = _weekend_stage_catchup(
            dry_run=False, pipeline=fake, now_local=datetime(2026, 8, 16, 12, 0))
        self.assert_eq(sorted(fake.synced), ["input", "output", "reflection"],
                       "三个超期阶段都应补 sync")
        self.assert_eq(len(caught), 3, "补跑记录应为 3 条")

        # --- 接线：dry-run 不落任何 sync
        fake2 = _FakePipeline()
        _weekend_stage_catchup(
            dry_run=True, pipeline=fake2, now_local=datetime(2026, 8, 16, 12, 0))
        self.assert_eq(fake2.synced, [], "dry-run 不应执行 sync")

    def run_tests(self):
        self._test_sync_stage_jobs_idempotent()
        self._test_dependency_order()
        self._test_pick_next_job_respects_deps()
        self._test_run_next_dry_run_no_writes()
        self._test_repair_stale_and_failed()
        self._test_pick_next_job_retries_blocking_deps()
        self._test_sync_refreshes_stale_depends_on()
        self._test_dependencies_satisfied_strict_missing_dep()
        self._test_output_stage_creates_archived_extract_jobs()
        self._test_verify_artifacts_resets_missing_output()
        self._test_kb_health_field_fallback_in_weekly_report()
        self._test_reset_stage_uses_own_recency_not_global_updated_at()
        self._test_reset_stage_not_triggered_within_week()
        self._test_weekend_stage_catchup()
