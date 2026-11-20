#!/usr/bin/env python3
"""
test_weekend_crossweek_perjob.py — 跨周重置 per-job 口径回归测试（v7.2.107）

背景（2026-11-02 16h 健康检查 v75 轮 BUG-36 实测）：

    `WeekendPipeline._reset_stage_for_new_week` 旧实现取**阶段内全部 job
    的 max(finished_at)** 作为唯一锚点比较——只要阶段内任意一个 job 在
    本周末内完成过，整个阶段就判为「未跨周」，所有 job 保持 done，
    阶段静默 no-op。

    生产实测（reflection 阶段 11 个 job）：
        · 5 个主链 job（health_check / collect_state / analyze_patterns /
          generate_report / recommend_actions）finished_at 停在 2026-10-25 01:00Z
        · 6 个维护链 job（kb_deep_health / kb_merge_duplicates /
          proposal_calibration / link_deep_review / kb_taxonomy_apply /
          panel_plan）在 10-30 16:21~18:00 被手工重跑
        → max(finished_at) = 2026-10-30T18:00:14Z → 本地 10-31 02:00:14
        → ≥ 锚点 2026-10-31 00:00(+08:00) → 判「未跨周」
        → 11-01 09:00 的 reflection 入口 cron 触发 ok，主链 5 个 job 从未重跑
        → 唯一写 health_updated_at 的 reflection_recommend_actions 不再执行
        → KB 健康评分永久停在 2026-10-25T01:00:25Z（数据流转异常）

    修复分两层（v7.2.107，2026-11-02 20h 健康检查 v75 轮补正）：
        ① 阶段级真跨周闸门——必须存在**可解析**且早于锚点的 finished_at，
           否则不认定跨周（保住 v6.9.38 契约：脏时间戳 / 无完成记录 →
           安全 no-op；同时避免 repair 重试后的 pending job 被误当跨周）；
        ② per-job 口径重置——真跨周时逐 job 判定，早于锚点的 job 与
           无完成记录的 job 一并重置，本周末内完成过的 job 保持原状。

本测试覆盖：
    1. 部分 job 被手工重跑 → 其余跨周 job 仍被重置（BUG-36 主场景）
    2. 全部 job 均在本周末内完成 → 不重置（同周末幂等，回归护栏）
    3. 全部 job 跨周 → 全部重置（与旧口径一致，回归护栏）
    4. 从未完成（无 finished_at）的 job 单独存在 → 不构成跨周证据（R2）
    5. 时间戳不可解析 → 安全 no-op（v6.9.38 契约，R1）
    6. 全阶段无跨周证据 → 不重置 + input_round 不被误归 1（R2）
    7. 真跨周 → 未完成 job 一并重置 + repair_attempts 归零（v7.2.46）
    8. 重置语义护栏：repair_attempts / attempts / result 一并清零
    9. 反向断言：本周末内完成过的 job **不得**被重置（防过度重置）

    ⚠ v7.2.107 首版（未提交）缺 ① 层闸门，引入两个回归：
       R1 脏时间戳被保守重置 → 违反 v6.9.38 已提交契约；
       R2 repair 重试后的 pending job 被当跨周 → repair_attempts 清零
          → 修复上限守卫失效 + input_round 误归 1（113 → 1）。
       本套件已按两层语义重写断言。

注意：本测试不调用 LLM，运行于隔离临时目录，零生产副作用。
"""

import importlib
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT

# 业务时区（北京时间），与生产锚点口径一致
TZ8 = timezone(timedelta(hours=8))


class WeekendCrossweekPerJobTests(TestSuite):
    def __init__(self):
        super().__init__("跨周重置 per-job 口径测试（v7.2.107 BUG-36）")
        self.tmp_root = None
        self.wp_mod = None

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

        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("weekend_pipeline") or mod_name.startswith("proposal_lifecycle"):
                del sys.modules[mod_name]

        import paths
        self._orig_project_root = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root

        self.wp_mod = importlib.import_module("weekend_pipeline")
        patch_module_root("weekend_pipeline", self.tmp_root)
        patch_module_root("proposal_lifecycle", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    # ------------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------------

    def _freeze_now(self, y, m, d, hour, minute=0):
        """把 pipeline.datetime.now 冻结到指定本地时刻（Asia/Shanghai +8）。"""
        import weekend_pipeline.pipeline as pl

        class FakeDT(datetime):
            _frozen = datetime(y, m, d, hour, minute, 0, tzinfo=timezone.utc) - timedelta(hours=8)

            @classmethod
            def now(cls, tz=None):
                return cls._frozen.astimezone() if tz is None else cls._frozen.astimezone(tz)

        pl.datetime = FakeDT

    def _unfreeze(self):
        import weekend_pipeline.pipeline as pl
        pl.datetime = _REAL_DATETIME

    def _make_pipeline(self):
        from weekend_pipeline.pipeline import WeekendPipeline
        return WeekendPipeline(state_path=self.tmp_root / "memory" / "weekend-pipeline.json")

    def _state_with_jobs(self, jobs):
        return {
            "jobs": jobs,
            "stage_status": {},
            "updated_at": "2026-11-01T00:00:00Z",
        }

    def _job(self, job_id, finished_at, status="done", **extra):
        job = {
            "job_id": job_id,
            "stage": "reflection",
            "step": job_id.replace("reflection_", ""),
            "status": status,
            "attempts": 0,
            "started_at": finished_at,
            "finished_at": finished_at,
            "last_error": "",
            "depends_on": [],
        }
        job.update(extra)
        return job

    # ------------------------------------------------------------------
    # 用例
    # ------------------------------------------------------------------

    def _test_partial_rerun_does_not_mask_others(self):
        """BUG-36 主场景：部分 job 手工重跑 → 其余跨周 job 仍须重置。

        复刻生产数据形态：5 个主链 job 停在 10-25，6 个维护链 job 在
        10-30 手工重跑（越过 10-31 锚点）。旧 max 口径判「未跨周」→
        全部保持 done；per-job 口径下 5 个主链 job 应被重置。
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"

        main_chain = [
            "reflection_health_check", "reflection_collect_state",
            "reflection_analyze_patterns", "reflection_generate_report",
            "reflection_recommend_actions",
        ]
        maint_chain = [
            "reflection_kb_deep_health", "reflection_kb_merge_duplicates",
            "reflection_proposal_calibration", "reflection_link_deep_review",
            "reflection_kb_taxonomy_apply", "reflection_panel_plan",
        ]
        jobs = []
        for jid in main_chain:
            jobs.append(self._job(jid, "2026-10-25T01:00:25Z"))
        for i, jid in enumerate(maint_chain):
            # 10-30 16:21 ~ 18:00 手工重跑（本地 10-31 00:21 ~ 02:00）
            jobs.append(self._job(jid, f"2026-10-30T1{6 + i // 3}:2{1 + i}:00Z"))
        p.state = self._state_with_jobs(jobs)

        # 冻结到 11-01 09:00 本地（reflection 入口 cron 实际触发时刻）
        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n = p._reset_stage_for_new_week("reflection")
        finally:
            self._unfreeze()

        self.assert_eq(n, len(main_chain),
                       "per-job 口径下仅重置 5 个跨周主链 job（维护链保持 done）")

        after = {j["job_id"]: j for j in p.state["jobs"]}
        for jid in main_chain:
            self.assert_eq(after[jid]["status"], "pending",
                           f"{jid}（10-25 完成，早于锚点）应被重置为 pending")
            self.assert_eq(after[jid]["finished_at"], "",
                           f"{jid} 重置后应清空 finished_at")
        for jid in maint_chain:
            self.assert_eq(after[jid]["status"], "done",
                           f"{jid}（10-30 手工重跑，本周末内完成）不得被重置")

    def _test_all_within_weekend_not_reset(self):
        """回归护栏：全部 job 均在本周末内完成 → 不重置（同周末幂等）。"""
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        # 11-01 09:00 本地，锚点 = 10-31 00:00；10-31 06:00 本地完成 → 在锚点后
        p.state = self._state_with_jobs([
            self._job("reflection_health_check", "2026-10-30T22:00:00Z"),
            self._job("reflection_recommend_actions", "2026-10-30T22:00:00Z"),
        ])

        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n = p._reset_stage_for_new_week("reflection")
        finally:
            self._unfreeze()

        self.assert_eq(n, 0, "全部 job 本周末内完成 → 不应重置")
        self.assert_eq(p.state["jobs"][0]["status"], "done", "状态应保持 done")

    def _test_all_stale_reset(self):
        """回归护栏：全部 job 均跨周 → 全部重置（与旧口径一致）。"""
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        p.state = self._state_with_jobs([
            self._job("reflection_health_check", "2026-10-20T01:00:00Z"),
            self._job("reflection_recommend_actions", "2026-10-21T01:00:00Z"),
        ])

        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n = p._reset_stage_for_new_week("reflection")
        finally:
            self._unfreeze()

        self.assert_eq(n, 2, "全部 job 跨周 → 应全部重置")

    def _test_never_finished_job_reset(self):
        """从未完成（无 finished_at）的 job 本身**不**构成跨周证据（R2）。

        v7.2.107 首版把「无 finished_at」当作跨周证据 → 引入回归 R2
        （repair 重试后的 pending job 被误重置 → repair_attempts 清零 →
        修复上限守卫失效；input 阶段 input_round 被误归 1）。

        修正后：阶段级闸门要求存在**可解析**且早于锚点的 finished_at。
        此处唯一另一个 job 完成于 10-31（锚点之后）→ 无跨周证据 → 不重置。
        「真跨周时未完成 job 一并重置」由
        _test_true_cross_week_resets_unfinished_jobs 覆盖。
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        p.state = self._state_with_jobs([
            self._job("reflection_health_check", "", status="pending"),
            self._job("reflection_recommend_actions", "2026-10-31T06:00:00Z"),
        ])

        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n = p._reset_stage_for_new_week("reflection")
        finally:
            self._unfreeze()

        self.assert_eq(n, 0, "无跨周证据 → 从未完成的 job 也不得被重置（R2）")
        self.assert_eq(p.state["jobs"][0]["status"], "pending", "状态应保持 pending")

    def _test_unparsable_timestamp_reset(self):
        """finished_at 不可解析 → 安全 no-op（v6.9.38 契约，R1 修复）。

        v7.2.107 首版把「时间戳不可解析」当作「未完成 → 需重置」，
        违反 v6.9.38 已提交契约（test_mechanism_hardening 断言
        「时间戳异常应安全返回 0」）→ 引入回归 R1。

        修正后：阶段级真跨周闸门要求存在**可解析**且早于锚点的
        finished_at。全部 job 时间戳都脏 → 无跨周证据 → return 0。
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        p.state = self._state_with_jobs([
            self._job("reflection_health_check", "not-a-timestamp"),
            self._job("reflection_recommend_actions", "2026-11-01T06:00:00Z"),
        ])

        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n = p._reset_stage_for_new_week("reflection")
        finally:
            self._unfreeze()

        self.assert_eq(n, 0, "时间戳脏数据不得触发重置（v6.9.38 契约，R1）")
        self.assert_eq(p.state["jobs"][0]["status"], "done", "脏时间戳 job 状态应保持")

    def _test_no_cross_week_evidence_no_reset(self):
        """R2 修复：全阶段无跨周证据（pending job 无 finished_at）→ 不重置。

        repair 重试会把 failed job 重置为 pending 并**清空 finished_at**
        （executor.reset_failed_job）。这类 job 不是「跨周」——若被当作
        跨周重置，repair_attempts 会被清零 → 「修复上限」守卫失效
        → job 无限重试。

        同时验证 input 阶段：input_round 不得被误归 1
        （实测 round 113 → 1，last_summaries_path 被清）。
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        jobs = [
            self._job("reflection_health_check", "2026-11-01T12:00:00Z"),
            self._job("reflection_recommend_actions", "", status="pending",
                      repair_attempts=3),
        ]
        p.state = self._state_with_jobs(jobs)

        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n = p._reset_stage_for_new_week("reflection")
        finally:
            self._unfreeze()

        self.assert_eq(n, 0, "无跨周证据时不得重置任何 job（R2）")
        after = {j["job_id"]: j for j in p.state["jobs"]}
        self.assert_eq(after["reflection_recommend_actions"]["repair_attempts"], 3,
                       "repair_attempts 不得被清零（否则修复上限守卫失效）")
        self.assert_eq(after["reflection_recommend_actions"]["status"], "pending",
                       "pending job 状态不应改变")

        # input 阶段：input_round 不得被误归 1
        p2 = WeekendPipeline.__new__(WeekendPipeline)
        p2.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        p2.state = self._state_with_jobs([
            self._job("input_collect_sources", "2026-11-01T12:00:00Z", stage="input"),
            self._job("input_compose_ideas", "", status="pending", stage="input",
                      repair_attempts=3),
        ])
        p2.state["input_round"] = {
            "round": 113,
            "last_summaries_path": "memory/weekend-input/summaries-2026-11-01-r113.json",
        }

        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n2 = p2._reset_stage_for_new_week("input")
        finally:
            self._unfreeze()

        self.assert_eq(n2, 0, "input 阶段无跨周证据 → 不重置（R2）")
        ir = p2.state.get("input_round", {})
        self.assert_eq(ir.get("round"), 113, "input_round 不得被误归 1（R2）")
        self.assert_true(ir.get("last_summaries_path"),
                         "本轮产物指针不得被清空（R2）")

    def _test_true_cross_week_resets_unfinished_jobs(self):
        """真跨周时，未完成的 job 一并重置（v7.2.46 语义：清 repair_attempts）。

        这是 ①② 两层闸门下的正确行为：阶段存在可解析的跨周证据
        （某 job 早于锚点）时，其余「无完成记录」的 job 应一并重置，
        否则新一周它们永远不会被 worker 挑起。
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        p.state = self._state_with_jobs([
            self._job("reflection_health_check", "2026-10-25T01:00:25Z"),
            self._job("reflection_recommend_actions", "", status="pending",
                      repair_attempts=3),
        ])

        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n = p._reset_stage_for_new_week("reflection")
        finally:
            self._unfreeze()

        self.assert_eq(n, 2, "真跨周 → 早于锚点的 job 与未完成 job 一并重置")
        after = {j["job_id"]: j for j in p.state["jobs"]}
        self.assert_eq(after["reflection_recommend_actions"]["repair_attempts"], 0,
                       "真跨周时 repair_attempts 必须归零（v7.2.46 语义）")

    def _test_reset_clears_repair_counters(self):
        """重置语义护栏：repair_attempts / attempts / result 一并清零。"""
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        p.state = self._state_with_jobs([
            self._job("reflection_health_check", "2026-10-25T01:00:25Z",
                      status="failed", attempts=2, repair_attempts=3,
                      result={"ok": 1}),
        ])

        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n = p._reset_stage_for_new_week("reflection")
        finally:
            self._unfreeze()

        self.assert_eq(n, 1, "跨周 job 应被重置")
        job = p.state["jobs"][0]
        self.assert_eq(job["status"], "pending", "status=pending")
        self.assert_eq(job["attempts"], 0, "attempts 清零")
        self.assert_eq(job["repair_attempts"], 0, "repair_attempts 清零")
        self.assert_true("result" not in job, "result 应清除")

    def _test_input_round_back_to_one(self):
        """input 阶段跨周重置仍把轮次归 1（v6.9.98 语义不变）。"""
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline.__new__(WeekendPipeline)
        p.state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        p.state = self._state_with_jobs([
            self._job("input_collect_sources", "2026-10-25T01:00:00Z", stage="input"),
        ])
        p.state["input_round"] = {
            "round": 4,
            "last_summaries_path": "memory/weekend-input/summaries-2026-10-18-r3.json",
        }

        self._freeze_now(2026, 11, 1, 9, 0)
        try:
            n = p._reset_stage_for_new_week("input")
        finally:
            self._unfreeze()

        self.assert_eq(n, 1, "input 跨周 job 应被重置")
        ir = p.state.get("input_round", {})
        self.assert_eq(ir.get("round"), 1, "跨周重置后 round 归 1")
        self.assert_eq(ir.get("last_summaries_path"), "", "清除上周末产物指针")

    # ------------------------------------------------------------------
    # 调度
    # ------------------------------------------------------------------

    def run_tests(self):
        # 独立运行（__main__）时 test_runner 不调 setup，此处自建隔离环境
        if self.tmp_root is None:
            self.setup()
            self._owns_tmp = True
        try:
            self._test_partial_rerun_does_not_mask_others()
            self._test_all_within_weekend_not_reset()
            self._test_all_stale_reset()
            self._test_never_finished_job_reset()
            self._test_unparsable_timestamp_reset()
            self._test_no_cross_week_evidence_no_reset()
            self._test_true_cross_week_resets_unfinished_jobs()
            self._test_reset_clears_repair_counters()
            self._test_input_round_back_to_one()
        finally:
            if getattr(self, "_owns_tmp", False):
                self.teardown()
                self.tmp_root = None
                self._owns_tmp = False


_REAL_DATETIME = datetime


if __name__ == "__main__":
    import sys

    from test_runner import print_report

    suite = WeekendCrossweekPerJobTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    print_report([suite])
    summary = suite.summary()
    sys.exit(0 if summary["failed"] == 0 else 1)
