#!/usr/bin/env python3
"""
test_lifecycle_cron.py — 生命周期 cron 框架单元测试（v6.8.0）

覆盖：
    - 完整一轮 checkpoint 生成（25 个 job）
    - 下一 job 挑选（pick_next_job）
    - 幂等性（重复 sync 不重复创建）
    - 依赖未满足时不执行
    - 时段聚焦选择
    - stale running 修复

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
        # v6.8.26: round 1 生成 26 个 job；v7.3.0 起为 27（手册 critic+writer 入链、
        # derived update_method_manual 撤除：26 常规 + 1 idea_review）
        self.assert_eq(result.get("added"), 27, "round 1 生成 27 个 job（含 idea_review + 手册链）")

        jobs = c._get_jobs(pid)
        self.assert_eq(len(jobs), 27, "checkpoint 列表长度")
        # v6.8.26: 第一个 job 是 idea_review
        self.assert_eq(jobs[0]["step"], "idea_review", "第一个 job 是 idea_review")
        self.assert_eq(jobs[0]["section_key"], "idea_review", "idea_review section_key")
        # 第二个 job 是 rationale critic
        self.assert_eq(jobs[1]["step"], "critic", "第二个 job 是 critic")
        self.assert_eq(jobs[1]["section_key"], "rationale", "第二个模块是 rationale")
        # v7.3.0: 手册链在 references 之后（jobs[23]/[24]），monitor 依赖手册 writer
        self.assert_eq(jobs[23]["step"], "critic", "第 24 个 job 是手册 critic")
        self.assert_eq(jobs[23]["section_key"], "method_manual", "手册 critic section_key")
        self.assert_eq(jobs[24]["step"], "writer", "第 25 个 job 是手册 writer")
        self.assert_eq(jobs[24]["section_key"], "method_manual", "手册 writer section_key")
        self.assert_eq(jobs[25]["step"], "monitor", "倒数第二个 job 是 monitor")
        self.assert_eq(jobs[25]["depends_on"], [jobs[24]["job_id"]], "monitor 依赖手册 writer")
        self.assert_eq(jobs[26]["step"], "update_vision", "最后一个 job 是 update_vision")

    def _test_pick_next_job(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260102"
        self._register_proposal(c, pid, "optimizing")
        c.sync_checkpoint(pid)

        job = c.pick_next_job(pid)
        self.assert_true(job is not None, "有 pending job")
        # v6.8.26: 第一个 job 是 idea_review（无依赖）
        self.assert_eq(job["step"], "idea_review", "下一个 job 是 idea_review")

    def _test_idempotent_sync(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260103"
        self._register_proposal(c, pid, "optimizing")
        c.sync_checkpoint(pid)
        result = c.sync_checkpoint(pid)
        self.assert_eq(result.get("added"), 0, "重复 sync 不新增")
        # v6.8.26: job 数量保持不变；v7.3.0 起为 27（手册链）
        self.assert_eq(len(c._get_jobs(pid)), 27, "job 数量保持 27")

    def _test_dependency_respected(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260104"
        self._register_proposal(c, pid, "optimizing")
        c.sync_checkpoint(pid)

        # v6.8.26: 模拟 idea_review 失败，rationale critic 不应被 pick
        jobs = c._get_jobs(pid)
        jobs[0]["status"] = "failed"  # idea_review
        jobs[0]["attempts"] = 1
        c._save_jobs(pid, jobs)

        job = c.pick_next_job(pid)
        self.assert_true(job is None, "idea_review 失败后无可用 job（critic 依赖未满足）")

    def _test_chain_dependency(self):
        c = self._make_controller()
        pid = "general-test-hhg-20260105"
        self._register_proposal(c, pid, "optimizing")
        c.sync_checkpoint(pid)

        jobs = c._get_jobs(pid)
        # rationale writer 依赖 critic 和 lit_note
        writer = next(j for j in jobs if j["section_key"] == "rationale" and j["step"] == "writer")
        critic_id = f"{pid}-r1-rationale-critic"
        note_id = f"{pid}-r1-rationale-lit_note"
        self.assert_in(critic_id, writer["depends_on"], "writer 依赖 critic")
        self.assert_in(note_id, writer["depends_on"], "writer 依赖 lit_note")

        # content critic 依赖 rationale writer
        content_critic = next(j for j in jobs if j["section_key"] == "content" and j["step"] == "critic")
        self.assert_in(writer["job_id"], content_critic["depends_on"], "content critic 依赖 rationale writer")

        # v6.8.26: rationale critic 依赖 idea_review
        rationale_critic = next(j for j in jobs if j["section_key"] == "rationale" and j["step"] == "critic")
        idea_review_id = f"{pid}-r1-idea_review-idea_review"
        self.assert_in(idea_review_id, rationale_critic["depends_on"], "rationale critic 依赖 idea_review")

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

    def _test_max_rounds_override_honored(self):
        """v7.2.40（BUG-7）: sync_checkpoint 的轮次上限必须读 max_rounds_override。

        缺陷现场（2026-10-22 健康检查定位）：order-param rounds=8 /
        override=12 / 81 job 全 done / 0 pending / status 永远 optimizing，
        stalled 告警累计 306 轮。根因是 sync_checkpoint 硬编码
        DEFAULT_MAX_ROUNDS(8) 拒绝建轮，而 completion.py 的完成度检测
        认 override=12 继续判"未达上限"——两头互锁形成永久阱死。
        """
        c = self._make_controller()
        pid = "general-test-override-20260109"
        self._register_proposal(c, pid, "optimizing")

        state = c._get_proposal_state(pid)
        state["optimization_rounds"] = 8  # 已达 DEFAULT_MAX_ROUNDS
        state["max_rounds_override"] = 12  # 人工加宽（v6.9.92 语义）
        c._set_proposal_state(pid, state)

        result = c.sync_checkpoint(pid)
        # override 生效 → 允许建 r9（added > 0 即解锁）
        self.assert_true(
            result.get("added", 0) > 0,
            "override=12 时 r8 仍应建下一轮（BUG-7 修复点）",
            result,
        )
        jobs = c._get_jobs(pid)
        self.assert_true(
            any(j.get("round") == 9 for j in jobs),
            "生成 round 9 的 job",
            [j.get("round") for j in jobs[:3]],
        )

        # 反向断言：撤掉 override 后必须回到"拒绝建轮"，确认用例真实
        # 有效（否则上一步可能因任何原因恒真 → 自证绿）
        state2 = c._get_proposal_state(pid)
        state2["optimization_rounds"] = 8
        state2["max_rounds_override"] = 0
        c._set_proposal_state(pid, state2)
        c._save_jobs(pid, [])
        result2 = c.sync_checkpoint(pid)
        self.assert_eq(
            result2.get("added"), 0,
            "无 override 时 r8 仍拒绝建轮（默认上限 8 未被放宽）",
        )

        # override 恰好等于当前轮次 → 仍然拒绝（边界）
        state3 = c._get_proposal_state(pid)
        state3["optimization_rounds"] = 12
        state3["max_rounds_override"] = 12
        c._set_proposal_state(pid, state3)
        c._save_jobs(pid, [])
        result3 = c.sync_checkpoint(pid)
        self.assert_eq(
            result3.get("added"), 0,
            "override 恰好等于当前轮次时拒绝建轮（边界不越界）",
        )

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

    def _test_mark_degradation_persists(self):
        """v6.8.3 修复: _mark_degradation 使用 _set_proposal_state（非不存在的 _save_proposal_state）。
        验证降级事件被正确持久化到 proposal_state。"""
        c = self._make_controller()
        pid = "general-degrade-test-20260101"
        self._register_proposal(c, pid, "optimizing")

        # 调用 _mark_degradation（此前因方法名错误会静默失败）
        c._mark_degradation(pid, "gap_identify", "agent_loop_failed→llm_direct")

        # 验证 degradation_events 已持久化
        state = c._get_proposal_state(pid)
        events = state.get("degradation_events", [])
        self.assert_eq(len(events), 1, "降级事件已记录")
        self.assert_eq(events[0]["step"], "gap_identify", "步骤名正确")
        self.assert_eq(events[0]["detail"], "agent_loop_failed→llm_direct", "详情正确")

        # 验证多次调用会追加（且保留最近 20 条）
        for i in range(25):
            c._mark_degradation(pid, "lit_search", f"detail_{i}")
        state = c._get_proposal_state(pid)
        events = state.get("degradation_events", [])
        self.assert_eq(len(events), 20, "降级事件保留最近 20 条")

    def _test_quality_warning_persists(self):
        """v6.8.3 修复: _check_done 逃生阀质量警告通过 _set_proposal_state 持久化（非崩溃的 _save_proposal_state）。
        验证逃生阀触发且分数低于达标线时，quality_warning 被写入 proposal_state。"""
        c = self._make_controller()
        pid = "general-quality-warn-20260101"
        self._register_proposal(c, pid, "optimizing")

        # 模拟达到最大轮数 + 低分数场景（条件3 逃生阀）
        state = c._get_proposal_state(pid)
        state["optimization_rounds"] = 10  # 超过 DEFAULT_MAX_ROUNDS(8)
        state["last_score"] = 0.50  # 低于达标线
        state["section_passes"] = {s: False for s in c.REQUIRED_SECTIONS}
        c._set_proposal_state(pid, state)

        threshold = c._get_quality_threshold("general")
        done_result = c._check_done(pid, threshold)

        # 逃生阀应触发
        self.assert_true(done_result["done"], "逃生阀触发 done=True")
        # 分数低于达标线应有质量警告
        warning = done_result.get("quality_warning")
        self.assert_true(warning is not None and warning != "", "低分数逃生阀附加 quality_warning")

    def _test_critic_timeout_report_salvage(self):
        """v7.3.75: critic 超时但报告已完整落盘 → 按成功结算，避免整轮重跑。"""
        c = self._make_controller()
        pid = "general-salvage-20260101"
        self._register_proposal(c, pid, "optimizing")
        prop_dir = c.root / "optimizing" / pid
        rp = prop_dir / "05_review" / "critic-round-1-method_manual.md"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(
            "# 对抗评审报告（第 1 轮 · method_manual 开工就绪度）\n\n"
            "## 问题清单\n\n[critical]｜⑧｜G.1.2｜引文错挂｜全册反查改挂\n\n"
            "## 对抗结论\n\n本轮 1 个问题（critical:1），不建议通过。\n\n"
            "## 评分\n创新性：N/A\n严谨性：0.72\n就绪度：0.85\n综合评分：0.79\n",
            encoding="utf-8",
        )
        self.assert_true(
            c._salvage_critic_report(rp, {"_run_started_at": "2020-01-01T00:00:00Z"}),
            "报告在本次开工后完整落盘 → 捞回成功",
        )
        self.assert_true(
            not c._salvage_critic_report(rp, {"_run_started_at": "2030-01-01T00:00:00Z"}),
            "报告早于本次开工 → 不捞回（避免旧报告冒充本轮）",
        )
        rp.write_text("x" * 200, encoding="utf-8")
        self.assert_true(
            not c._salvage_critic_report(rp, {"_run_started_at": "2020-01-01T00:00:00Z"}),
            "无评分块 → 不捞回",
        )

    def run_tests(self):
        self._test_checkpoint_generation()
        self._test_pick_next_job()
        self._test_idempotent_sync()
        self._test_dependency_respected()
        self._test_chain_dependency()
        self._test_stale_running_repair()
        self._test_max_rounds_no_new_jobs()
        self._test_max_rounds_override_honored()
        self._test_non_optimizing_no_jobs()
        self._test_worker_minute_stagger()
        self._test_mark_degradation_persists()
        self._test_quality_warning_persists()
        self._test_critic_timeout_report_salvage()
