#!/usr/bin/env python3
"""
test_weekend_input_rounds.py — 周末输入链多轮化回归测试（v6.9.98 T1）

覆盖：
    1. deep_digest 深读替代浅摘要：
       - 产物带轮次号 summaries-{date}-r{round}.json；首轮兼容旧名
         summaries-{date}.json 同步写（外部兼容快照）
       - 单轮批量上限 10 篇、全文输入（无 [:1200] 截断）
       - 结构化字段（core/mechanism/method_leads/proposal_links/keywords）
         收敛 + summary 兼容回填 + 关键词归一化
       - 故障防线：LLM 全挂 → success=False 不落产物不标已处理
    2. 轮次接力（rounds.py，时间全部注入）：
       - 接力四门槛（六步全完成 / 剩余源 ≥1 / 冷却 90 分钟 / 周末窗口）
       - 周日 23:59 窗口闭合、工作日不开轮
       - 重置动作（round+1 / attempts 保留 / prev_round_finished_at）
       - run_next 路径端到端开轮并挑中 collect；dry-run 零落盘不开轮
       - 跨周重置 round 归 1
    3. cluster_distill 每轮簇上限 3（原周限 8 语义变更）
    4. _verify_artifacts 的 {round} 占位符（轮次产物按 job.round 定位）

注意：
    本测试不调用 LLM（_llm_json 全部 stub），运行于隔离临时目录。
"""

import sys
import importlib
from datetime import datetime, timezone
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fake_papers(count: int, text_len: int = 1500):
    return [
        {
            "source_id": f"paper:p{i}",
            "type": "paper",
            "title": f"HHG 论文 {i}",
            "text": ("x" * text_len) + f"·尾部标记{i}·",
            "path": f"knowledge/raw/papers/p{i}.md",
            "tier": 1,
        }
        for i in range(1, count + 1)
    ]


def _digest_llm_ok(system, user, timeout=90):
    """stub：返回结构化深读 JSON（模拟 GLM 输出，含括注关键词）。"""
    return {
        "core": "本文提出 X 方法。实现了 Y 提升。揭示了 Z 机制。",
        "mechanism": "机制要点：强场驱动下电子隧穿与再复合。",
        "method_leads": [{"name": "TDDFT", "note": "含时密度泛函新参数化"}],
        "proposal_links": [{"topic": "强场HHG", "note": "与在跑课题方向直接相关"}],
        "keywords": ["高次谐波 (HHG)", "强场物理", "k1", "k2"],
    }


class WeekendInputRoundsTests(TestSuite):
    def __init__(self):
        super().__init__("周末输入链多轮化测试（v6.9.98）")
        self.tmp_root = None

    # ------------------------------------------------------------------
    # 隔离环境（与 test_weekend_pipeline_hardening.py 相同机制）
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            import shutil
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
            import shutil
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    def _make_pipeline(self):
        from weekend_pipeline.pipeline import WeekendPipeline
        return WeekendPipeline(state_path=self.tmp_root / "memory" / "weekend-pipeline.json")

    def _patch_digest_env(self, papers, llm=_digest_llm_ok, llm_available=True):
        """stub 掉 deep_digest 的外部依赖（collect/LLM/课题清单）。"""
        from weekend_pipeline import input_jobs

        saved = (
            input_jobs.collect_all_sources,
            input_jobs.new_paper_sources,
            input_jobs.is_llm_available,
            input_jobs._llm_json,
            input_jobs._load_all_stage_proposals,
        )
        input_jobs.collect_all_sources = lambda **kw: {
            "papers": papers, "briefings": [], "collected_at": _utc_now_str(),
        }
        input_jobs.new_paper_sources = lambda sources, state: papers
        input_jobs.is_llm_available = lambda: llm_available
        input_jobs._llm_json = llm
        input_jobs._load_all_stage_proposals = lambda: [
            {"proposal_id": "p-active", "title": "强场 HHG 课题", "text": ""},
        ]
        return saved

    def _restore_digest_env(self, saved):
        from weekend_pipeline import input_jobs
        (input_jobs.collect_all_sources,
         input_jobs.new_paper_sources,
         input_jobs.is_llm_available,
         input_jobs._llm_json,
         input_jobs._load_all_stage_proposals) = saved

    def _clean_today_summaries(self):
        """清理当天 summaries-* 产物（同一隔离目录内用例间防污染）。"""
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        if WEEKEND_INPUT_DIR.exists():
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            for f in WEEKEND_INPUT_DIR.glob(f"summaries-{date_str}*.json"):
                f.unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # 1. deep_digest 产物与兼容
    # ------------------------------------------------------------------

    def _test_deep_digest_round1_artifacts_and_legacy_alias(self):
        """首轮产物带 -r1 且同步写旧名（外部兼容），字段结构齐全。"""
        from weekend_pipeline import input_jobs
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR

        papers = _fake_papers(2)
        saved = self._patch_digest_env(papers)
        try:
            state = {"processed_sources": {}}
            result = input_jobs.run_input_deep_digest(state=state, job={})

            self.assert_true(result.get("success"), "deep_digest 成功", str(result))
            self.assert_eq(result.get("digested"), 2, "深读 2 篇")
            self.assert_eq(result.get("remaining_sources"), 0, "剩余源 0")
            self.assert_eq(result.get("round"), 1, "首轮 round=1")

            date_str = input_jobs.now_utc()[:10]
            r1 = WEEKEND_INPUT_DIR / f"summaries-{date_str}-r1.json"
            legacy = WEEKEND_INPUT_DIR / f"summaries-{date_str}.json"
            self.assert_true(r1.exists(), "轮次产物 summaries-{date}-r1.json 应落盘")
            self.assert_true(legacy.exists(), "首轮应兼容写旧名 summaries-{date}.json")

            import json
            data = json.loads(r1.read_text(encoding="utf-8"))
            self.assert_eq(len(data.get("summaries", [])), 2, "r1 产物含 2 条深读")
            first = data["summaries"][0]
            self.assert_in("core", first, "结构化字段 core")
            self.assert_in("mechanism", first, "结构化字段 mechanism")
            self.assert_in("method_leads", first, "结构化字段 method_leads")
            self.assert_in("proposal_links", first, "结构化字段 proposal_links")
            self.assert_in("keywords", first, "结构化字段 keywords")
            self.assert_eq(first.get("summary"), first.get("core"), "summary 应由 core 回填（下游兼容）")
            self.assert_eq(first.get("source_id"), "paper:p1", "溯源字段 source_id")
            self.assert_eq(first.get("tier"), 1, "溯源字段 tier")
            self.assert_true(
                all("(hhg)" not in k for k in first.get("keywords", [])),
                "关键词应去括注归一化（高次谐波 (HHG) → 高次谐波）",
            )

            ir = state.get("input_round", {})
            self.assert_eq(ir.get("round"), 1, "state 记录 round=1")
            self.assert_in("-r1.json", str(ir.get("last_summaries_path", "")),
                           "state 记录本轮产物路径")
            self.assert_eq(len(state.get("processed_sources", {})), 2, "成功深读的源标记已处理")
        finally:
            self._restore_digest_env(saved)

    def _test_deep_digest_round2_batch_cap_and_no_legacy(self):
        """r2 只写轮次文件；13 篇源单轮批量 10、剩余 3。"""
        from weekend_pipeline import input_jobs
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR

        self._clean_today_summaries()
        papers = _fake_papers(13)
        saved = self._patch_digest_env(papers)
        try:
            state = {"processed_sources": {}, "input_round": {"round": 2}}
            result = input_jobs.run_input_deep_digest(state=state, job={})

            self.assert_true(result.get("success"), "r2 deep_digest 成功", str(result))
            self.assert_eq(result.get("digested"), 10, "单轮批量上限 10 篇")
            self.assert_eq(result.get("remaining_sources"), 3, "剩余 3 篇（接力依据）")
            self.assert_eq(result.get("round"), 2, "round=2")

            date_str = input_jobs.now_utc()[:10]
            r2 = WEEKEND_INPUT_DIR / f"summaries-{date_str}-r2.json"
            legacy = WEEKEND_INPUT_DIR / f"summaries-{date_str}.json"
            self.assert_true(r2.exists(), "r2 产物应落盘")
            self.assert_true(not legacy.exists(), "非首轮不再写旧名（避免覆盖 r1 兼容快照）")
        finally:
            self._restore_digest_env(saved)

    def _test_deep_digest_full_text_no_truncation(self):
        """输入为简报卡全文：prompt 不再 [:1200] 截断。"""
        from weekend_pipeline import input_jobs

        papers = _fake_papers(1, text_len=2000)
        captured = {}

        def _capture_llm(system, user, timeout=90):
            captured["user"] = user
            return _digest_llm_ok(system, user, timeout)

        saved = self._patch_digest_env(papers, llm=_capture_llm)
        try:
            state = {"processed_sources": {}}
            input_jobs.run_input_deep_digest(state=state, job={})
            user = captured.get("user", "")
            self.assert_in("·尾部标记1·", user, "全文尾部内容应进入 prompt（旧 [:1200] 截断则丢失）")
        finally:
            self._restore_digest_env(saved)

    def _test_deep_digest_all_fail_not_done(self):
        """LLM 全挂 → success=False，不落产物、不标已处理（防线保留）。"""
        from weekend_pipeline import input_jobs
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR

        self._clean_today_summaries()
        papers = _fake_papers(2)
        saved = self._patch_digest_env(papers, llm=lambda s, u, timeout=90: None)
        try:
            state = {"processed_sources": {}}
            result = input_jobs.run_input_deep_digest(state=state, job={})
            self.assert_true(not result.get("success"), "全失败应 success=False")
            date_str = input_jobs.now_utc()[:10]
            self.assert_true(
                not (WEEKEND_INPUT_DIR / f"summaries-{date_str}-r1.json").exists(),
                "全失败不落产物",
            )
            self.assert_eq(len(state.get("processed_sources", {})), 0, "失败源不得标记已处理")
        finally:
            self._restore_digest_env(saved)

    # ------------------------------------------------------------------
    # 2. 轮次接力判定（纯函数，时间注入）
    # ------------------------------------------------------------------

    def _done_state(self, remaining: int, finished: str = "2026-09-05T05:30:00Z"):
        """构造 r1 六步全 done 的 pipeline state。"""
        jobs = []
        for jid in ("input_collect_sources", "input_deep_digest_papers",
                    "input_cluster_assign", "input_cluster_distill",
                    "input_topic_match", "input_compose_ideas"):
            job = {"job_id": jid, "stage": "input", "status": "done",
                   "finished_at": finished, "attempts": 0}
            if jid == "input_deep_digest_papers":
                job["result"] = {"remaining_sources": remaining}
            jobs.append(job)
        return {"jobs": jobs, "stage_status": {"input": "done"},
                "input_round": {"round": 1}}

    def _test_input_window_closed(self):
        """周末窗口开合：周六开 / 周日 23:00 开 / 周日 23:59 闭 / 工作日闭。"""
        from weekend_pipeline.rounds import input_window_closed
        sat = datetime(2026, 9, 5, 4, 0, 0, tzinfo=timezone.utc)     # 北京 周六 12:00
        self.assert_true(not input_window_closed(sat), "周六窗口开")
        sun_early = datetime(2026, 9, 6, 15, 0, 0, tzinfo=timezone.utc)  # 北京 周日 23:00
        self.assert_true(not input_window_closed(sun_early), "周日 23:00 窗口仍开")
        sun_late = datetime(2026, 9, 6, 15, 59, 30, tzinfo=timezone.utc)  # 北京 周日 23:59:30
        self.assert_true(input_window_closed(sun_late), "周日 23:59 后窗口闭合")
        mon = datetime(2026, 9, 7, 4, 0, 0, tzinfo=timezone.utc)     # 北京 周一
        self.assert_true(input_window_closed(mon), "工作日不开轮")

    def _test_should_open_next_round_gates(self):
        """接力四门槛：冷却 / 源尽 / 未完成 / 窗口。"""
        from weekend_pipeline.rounds import should_open_next_round
        sat_after_cooldown = datetime(2026, 9, 5, 7, 30, 0, tzinfo=timezone.utc)  # 距 05:30 完成 2h

        ok, _ = should_open_next_round(self._done_state(5), now=sat_after_cooldown)
        self.assert_true(ok, "全 done + 剩余 5 + 冷却满 + 周六 → 开轮")

        ok, reason = should_open_next_round(self._done_state(5), now=datetime(2026, 9, 5, 6, 0, 0, tzinfo=timezone.utc))
        self.assert_true(not ok, "冷却 30 分钟未满 → 不开轮")
        self.assert_in("冷却", reason, "不开轮原因应说明冷却")

        ok, _ = should_open_next_round(self._done_state(0), now=sat_after_cooldown)
        self.assert_true(not ok, "源尽（剩余 0）→ 不开轮，stage 终态 done")

        running = self._done_state(5)
        running["jobs"][3]["status"] = "pending"
        ok, _ = should_open_next_round(running, now=sat_after_cooldown)
        self.assert_true(not ok, "六步未全完成 → 不开轮")

        no_record = self._done_state(5)
        for j in no_record["jobs"]:
            if j["job_id"] == "input_deep_digest_papers":
                del j["result"]
        ok, _ = should_open_next_round(no_record, now=sat_after_cooldown)
        self.assert_true(not ok, "无 remaining_sources 记录（旧 state）→ 保守不开轮")

        sun_late = datetime(2026, 9, 6, 15, 59, 30, tzinfo=timezone.utc)
        ok, _ = should_open_next_round(
            self._done_state(5, finished="2026-09-06T05:30:00Z"), now=sun_late)
        self.assert_true(not ok, "周日 23:59 后 → 窗口闭合不开轮")

    def _test_reset_keeps_attempts_and_records_prev(self):
        """重置动作：round+1 / attempts 保留 / prev_round_finished_at / stage pending。"""
        from weekend_pipeline.rounds import reset_input_for_new_round
        state = self._done_state(5)
        state["jobs"][1]["attempts"] = 2      # deep_digest 有失败史
        state["jobs"][4]["attempts"] = 1

        new_round = reset_input_for_new_round(state)
        self.assert_eq(new_round, 2, "重置后 round=2")
        self.assert_true(
            all(j["status"] == "pending" for j in state["jobs"]),
            "input job 全部重置 pending",
        )
        self.assert_eq(state["jobs"][1].get("attempts"), 2, "attempts 应保留（失败史不抹除）")
        self.assert_eq(state["jobs"][4].get("attempts"), 1, "attempts 应保留")
        self.assert_eq(state["input_round"].get("round"), 2, "state round=2")
        self.assert_eq(state["input_round"].get("prev_round_finished_at"),
                       "2026-09-05T05:30:00Z", "记录上轮完成时间")
        self.assert_eq(state["input_round"].get("last_summaries_path"), "",
                       "清除上轮产物指针（防误读）")
        self.assert_eq(state["stage_status"].get("input"), "pending", "stage_status 回 pending")
        self.assert_true(
            all(j.get("round") == 2 for j in state["jobs"]),
            "各 job 打 round 标（{round} 产物校验的格式化来源）",
        )

    # ------------------------------------------------------------------
    # 3. run_next 集成（weekend worker */20 tick 主路径）
    # ------------------------------------------------------------------

    def _freeze_rounds_clock(self, frozen_utc: datetime):
        """冻结 rounds 模块时钟（aware），返回还原函数。"""
        import weekend_pipeline.rounds as rounds_mod
        real_dt = rounds_mod.datetime

        class _FrozenDT(real_dt):
            @classmethod
            def now(cls, tz=None):
                return frozen_utc if tz is not None else frozen_utc.astimezone()

        rounds_mod.datetime = _FrozenDT
        return lambda: setattr(rounds_mod, "datetime", real_dt)

    def _test_run_next_opens_round_and_picks_collect(self):
        """端到端：冷却满开 r2 并挑中 collect（stub handler）。"""
        # 冻结到周六 15:30 北京（07:30Z，距 05:30Z 完成 2h > 90 分钟冷却，窗口开）
        restore = self._freeze_rounds_clock(datetime(2026, 9, 5, 7, 30, 0, tzinfo=timezone.utc))
        try:
            p = self._make_pipeline()
            p.sync_stage_jobs("input")
            # 构造 r1 六步全 done 的磁盘状态（保留模板结构字段）
            for j in p.state.get("jobs", []):
                if j.get("stage") != "input":
                    continue
                j["status"] = "done"
                j["finished_at"] = "2026-09-05T05:30:00Z"
                if j["job_id"] == "input_deep_digest_papers":
                    j["result"] = {"remaining_sources": 5, "digested": 10, "round": 1}
            p.state["input_round"] = {"round": 1}
            p.state["stage_status"]["input"] = "done"
            p._save()

            p2 = self._make_pipeline()
            p2.handlers = {
                (j["stage"], j["step"]): lambda s, jb, dry_run=False: {"success": True}
                for j in p2.list_jobs(stage="input")
            }
            result = p2.run_next(stage="input")
            self.assert_eq(result.get("opened_input_round"), 2, "run_next 应开第 2 轮")
            self.assert_eq(result.get("job_id"), "input_collect_sources",
                           "开轮后应挑中新轮 collect")

            p3 = self._make_pipeline()
            jobs = {j["job_id"]: j for j in p3.list_jobs(stage="input")}
            self.assert_eq(p3.state.get("input_round", {}).get("round"), 2, "磁盘 round=2")
            self.assert_eq(jobs["input_collect_sources"].get("status"), "done",
                           "collect 已被 stub 执行为 done")
            self.assert_eq(jobs["input_deep_digest_papers"].get("status"), "pending",
                           "新轮 deep_digest 待执行")
            self.assert_eq(jobs["input_deep_digest_papers"].get("round"), 2,
                           "job round 标更新为 2")
        finally:
            restore()

    def _test_run_next_no_round_when_exhausted(self):
        """源尽：不开轮，无任务可执行（stage 保持终态 done）。"""
        restore = self._freeze_rounds_clock(datetime(2026, 9, 5, 6, 0, 0, tzinfo=timezone.utc))
        try:
            p = self._make_pipeline()
            p.sync_stage_jobs("input")
            for j in p.state.get("jobs", []):
                if j.get("stage") != "input":
                    continue
                j["status"] = "done"
                j["finished_at"] = "2026-09-05T05:30:00Z"
                if j["job_id"] == "input_deep_digest_papers":
                    j["result"] = {"remaining_sources": 0, "digested": 10}
            p.state["input_round"] = {"round": 1}
            p.state["stage_status"]["input"] = "done"
            p._save()

            p2 = self._make_pipeline()
            result = p2.run_next(stage="input")
            self.assert_true("opened_input_round" not in result, "源尽不开轮")
            self.assert_eq(result.get("executed"), 0, "无任务可执行")
        finally:
            restore()

    def _test_run_next_dry_run_does_not_open_round(self):
        """dry-run 零落盘：不执行接力（磁盘 job 仍 done、round 仍 1）。"""
        restore = self._freeze_rounds_clock(datetime(2026, 9, 5, 6, 0, 0, tzinfo=timezone.utc))
        try:
            p = self._make_pipeline()
            p.sync_stage_jobs("input")
            for j in p.state.get("jobs", []):
                if j.get("stage") != "input":
                    continue
                j["status"] = "done"
                j["finished_at"] = "2026-09-05T05:30:00Z"
                if j["job_id"] == "input_deep_digest_papers":
                    j["result"] = {"remaining_sources": 5, "digested": 10}
            p.state["input_round"] = {"round": 1}
            p.state["stage_status"]["input"] = "done"
            p._save()

            p2 = self._make_pipeline()
            p2.run_next(stage="input", dry_run=True)

            p3 = self._make_pipeline()
            self.assert_eq(p3.state.get("input_round", {}).get("round"), 1,
                           "dry-run 不得开轮（磁盘 round 仍 1）")
            statuses = {j.get("status") for j in p3.list_jobs(stage="input")}
            self.assert_eq(statuses, {"done"}, "dry-run 不得重置磁盘 job")
        finally:
            restore()

    def _test_crossweek_reset_round_back_to_1(self):
        """跨周重置（自然周锚点）后 round 归 1。"""
        import weekend_pipeline.pipeline as pipe_mod
        real_dt = pipe_mod.datetime

        class _FrozenDT(real_dt):
            @classmethod
            def now(cls, tz=None):
                # 周六 09:00 本地（入口 cron 时刻），2026-08-22 为周六
                base = datetime(2026, 8, 22, 1, 0, 0, tzinfo=timezone.utc)
                return base if tz is not None else base.astimezone()

        pipe_mod.datetime = _FrozenDT
        try:
            p = self._make_pipeline()
            p.sync_stage_jobs("input")
            for j in p.state.get("jobs", []):
                if j.get("stage") != "input":
                    continue
                j["status"] = "done"
                j["finished_at"] = "2026-08-14T03:00:00Z"  # 上上周（早于本周六锚点）
            p.state["input_round"] = {"round": 4, "last_summaries_path": "memory/weekend-input/summaries-2026-08-15-r3.json"}
            p._save()

            p2 = self._make_pipeline()
            p2.sync_stage_jobs("input")
            ir = p2.state.get("input_round", {})
            self.assert_eq(ir.get("round"), 1, "跨周重置后 round 归 1")
            self.assert_eq(ir.get("last_summaries_path"), "", "清除上周末产物指针")
            pending = sum(1 for j in p2.list_jobs(stage="input") if j.get("status") == "pending")
            self.assert_eq(pending, 7, "跨周重置全部 job 回 pending（v6.10.0 七步）")
        finally:
            pipe_mod.datetime = real_dt

    # ------------------------------------------------------------------
    # 4. cluster_distill 每轮上限 + {round} 产物校验
    # ------------------------------------------------------------------

    def _test_cluster_distill_round_cap(self):
        """每轮簇上限 3（v6.9.98 语义：原周限 8 → 每轮 ≤3）。"""
        from weekend_pipeline import clusters as cl, input_jobs
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        import json

        now_str = _utc_now_str()
        fresh = [
            {"cluster_id": f"cl_{i}", "title": f"簇 {i}", "keywords": ["hhg"],
             "summary": "", "member_source_ids": [f"paper:a{i}", f"paper:b{i}", f"paper:c{i}"],
             "member_summaries": [], "status": "open", "updated_at": now_str}
            for i in range(5)
        ]
        registry = {"clusters": fresh, "orphans": []}

        saved = (
            cl.load_clusters, cl.open_clusters_with_fresh_members, cl.save_clusters,
            input_jobs._llm_json, input_jobs.is_llm_available,
        )
        cl.load_clusters = lambda path=None: registry
        cl.open_clusters_with_fresh_members = lambda reg, week_start: fresh
        cl.save_clusters = lambda reg, path=None: None
        input_jobs.is_llm_available = lambda: True
        input_jobs._llm_json = lambda s, u, timeout=120: {
            "title": "t", "summary": "综合摘要" * 20, "open_questions": ["q"],
        }
        try:
            result = input_jobs.run_input_cluster_distill(state={}, job={})
            self.assert_eq(result.get("distilled"), 3, "5 个 fresh 簇只提炼 3 个（每轮上限）")
            out = WEEKEND_INPUT_DIR / f"distilled-clusters-{input_jobs.now_utc()[:10]}.json"
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assert_eq(len(data.get("clusters", [])), 3, "产物文件只含 3 簇")
        finally:
            (cl.load_clusters, cl.open_clusters_with_fresh_members, cl.save_clusters,
             input_jobs._llm_json, input_jobs.is_llm_available) = saved

    def _test_verify_artifacts_round_placeholder(self):
        """deep_digest 产物按 job.round 定位：r2 缺 r2 文件 → 重置；补齐 → 不重置。"""
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR

        self._clean_today_summaries()
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        digest = next(j for j in p.state.get("jobs", [])
                      if j["job_id"] == "input_deep_digest_papers")
        digest["status"] = "done"
        digest["finished_at"] = _utc_now_str()
        digest["round"] = 2
        p._save()

        # 只有 r1 文件（无 r2）→ 产物缺失 → 重置
        WEEKEND_INPUT_DIR.mkdir(parents=True, exist_ok=True)
        (WEEKEND_INPUT_DIR / f"summaries-{date_str}-r1.json").write_text("{}", encoding="utf-8")
        p2 = self._make_pipeline()
        p2.sync_stage_jobs("input")
        digest2 = next(j for j in p2.state.get("jobs", [])
                       if j["job_id"] == "input_deep_digest_papers")
        self.assert_eq(digest2.get("status"), "pending",
                       "round=2 缺 r2 产物应重置（{round} 按 job.round 格式化）")

        # 补齐 r2 产物 → 不重置
        digest2["status"] = "done"
        digest2["finished_at"] = _utc_now_str()
        digest2["round"] = 2
        p2._save()
        (WEEKEND_INPUT_DIR / f"summaries-{date_str}-r2.json").write_text("{}", encoding="utf-8")
        p3 = self._make_pipeline()
        p3.sync_stage_jobs("input")
        digest3 = next(j for j in p3.state.get("jobs", [])
                       if j["job_id"] == "input_deep_digest_papers")
        self.assert_eq(digest3.get("status"), "done", "r2 产物存在时不应误重置")

    def run_tests(self):
        self._test_deep_digest_round1_artifacts_and_legacy_alias()
        self._test_deep_digest_round2_batch_cap_and_no_legacy()
        self._test_deep_digest_full_text_no_truncation()
        self._test_deep_digest_all_fail_not_done()
        self._test_input_window_closed()
        self._test_should_open_next_round_gates()
        self._test_reset_keeps_attempts_and_records_prev()
        self._test_run_next_opens_round_and_picks_collect()
        self._test_run_next_no_round_when_exhausted()
        self._test_run_next_dry_run_does_not_open_round()
        self._test_crossweek_reset_round_back_to_1()
        self._test_cluster_distill_round_cap()
        self._test_verify_artifacts_round_placeholder()


if __name__ == "__main__":
    suite = WeekendInputRoundsTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    import test_runner
    test_runner.print_report([suite])
    sys.exit(0 if suite.summary()["failed"] == 0 else 1)
