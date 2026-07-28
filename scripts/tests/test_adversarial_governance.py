#!/usr/bin/env python3
"""
test_adversarial_governance.py — 对抗评审奖惩与监察机制单元测试

覆盖：
    - agent 分数初始化与持久化
    - writer/critic 禁止清单规则层检测
    - 规则层 delta 计算
    - monitor 结果应用与分数更新
    - monitor history 记录与负反馈检测
    - 负反馈告警清除

注意：
    本测试不调用 hermes/LLM，仅验证规则层与状态机逻辑。
"""

import sys
import shutil
import json
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT
import importlib


class AdversarialGovernanceTests(TestSuite):
    def __init__(self):
        super().__init__("对抗评审奖惩机制测试")
        self.tmp_root = None
        self.ag_mod = None
        self.pl = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 需要 research_proposals 目录与 nsfc-standards
        (self.tmp_root / "research_proposals").mkdir(parents=True, exist_ok=True)
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(exist_ok=True)

        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")

        # 强制重新导入
        for mod_name in ["adversarial_governance", "proposal_lifecycle"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        self.ag_mod = importlib.import_module("adversarial_governance")
        self.pl = importlib.import_module("proposal_lifecycle")

        patch_module_root("adversarial_governance", self.tmp_root)
        patch_module_root("proposal_lifecycle", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_ag(self):
        return self.ag_mod.AdversarialGovernance()

    def _test_initial_scores(self):
        ag = self._make_ag()
        scores = ag.load_agent_scores()
        self.assert_eq(scores["writer"]["score"], 100, "writer 初始分数为 100")
        self.assert_eq(scores["critic"]["score"], 100, "critic 初始分数为 100")
        self.assert_true((self.tmp_root / "memory" / "agent-scores.json").exists(),
                         "agent-scores.json 已创建")

    def _test_writer_placeholder_detection(self):
        ag = self._make_ag()
        text = "本项目具有重要意义，[待填]内容将在后续补充。"
        violations = ag.detect_writer_prohibitions(text, "", "")
        types = [v["type"] for v in violations]
        self.assert_in("placeholder", types, "检测到占位符违规")

    def _test_writer_template_rigidity(self):
        ag = self._make_ag()
        text = (
            "具有重要的科学意义。具有重要的理论意义。具有重要的应用价值。"
            "本项目拟开展。本项目拟研究。旨在解决。综上所述。"
        )
        violations = ag.detect_writer_prohibitions(text, "", "")
        types = [v["type"] for v in violations]
        self.assert_in("template_rigidity", types, "检测到模板僵化")

    def _test_writer_surface_change(self):
        ag = self._make_ag()
        prev = "a b c d e f g h i j k l m n o p q r s t u v w x y z " * 5
        curr = prev + " "  # 几乎相同
        violations = ag.detect_writer_prohibitions(curr, prev, "")
        types = [v["type"] for v in violations]
        self.assert_in("surface_change", types, "检测到表面修改")

    def _test_critic_lazy_review(self):
        ag = self._make_ag()
        short_report = "总体还可以。"
        violations = ag.detect_critic_prohibitions(short_report, {}, 0.50)
        types = [v["type"] for v in violations]
        self.assert_in("lazy_review", types, "检测到消极评审")

    def _test_critic_rigid_scoring(self):
        ag = self._make_ag()
        report = "创新性：0.70\n可行性：0.70\n严谨性：0.70\n完整性：0.70\n"
        violations = ag.detect_critic_prohibitions(report, {
            "innovation": 0.70, "feasibility": 0.70, "rigor": 0.70, "completeness": 0.70
        }, 0.70)
        types = [v["type"] for v in violations]
        self.assert_in("rigid_scoring", types, "检测到僵化评分")

    def _test_critic_score_content_mismatch(self):
        ag = self._make_ag()
        report = "综合评分：0.85\n- [high] 问题1\n- [high] 问题2\n- [high] 问题3\n"
        violations = ag.detect_critic_prohibitions(report, {}, 0.85)
        types = [v["type"] for v in violations]
        self.assert_in("score_content_mismatch", types, "检测到评分与内容矛盾")

    def _test_rule_deltas_progress(self):
        ag = self._make_ag()
        writer_delta, critic_delta = ag.compute_rule_deltas(
            monitor_score=0.80,
            prev_monitor_score=0.70,
            critic_score=0.78,
            writer_violations=[],
            critic_violations=[],
            high_issues_before=3,
            high_issues_after=1,
        )
        self.assert_true(writer_delta > 0, "writer 取得进步应加分")
        self.assert_true(critic_delta > 0, "critic 校准且质量提升应加分")

    def _test_rule_deltas_penalty(self):
        ag = self._make_ag()
        writer_delta, critic_delta = ag.compute_rule_deltas(
            monitor_score=0.65,
            prev_monitor_score=0.70,
            critic_score=0.85,
            writer_violations=["placeholder"],
            critic_violations=["lazy_review"],
            high_issues_before=1,
            high_issues_after=3,
        )
        self.assert_true(writer_delta < 0, "writer 退步+违规应扣分")
        self.assert_true(critic_delta < 0, "critic 严重失准+违规应扣分")

    def _test_apply_monitor_result_updates_scores(self):
        ag = self._make_ag()
        monitor_result = {
            "success": True,
            "monitor_independent_score": 0.82,
            "writer_prohibitions": [],
            "critic_prohibitions": [],
            "writer_suggested_delta": 5,
            "critic_suggested_delta": 3,
            "collusion_risk": "none",
            "negative_feedback": False,
            "overall_assessment": "质量提升",
            "raw_output": "",
        }
        prop_state = {"monitor_history": []}
        deltas = ag.apply_monitor_result(
            proposal_id="general-test-20260101",
            round_num=1,
            section_key="rationale",
            score_before=0.70,
            score_after=0.80,
            dim_scores={"innovation": 0.8, "feasibility": 0.8, "rigor": 0.8, "completeness": 0.8},
            monitor_result=monitor_result,
            proposal_state=prop_state,
        )
        self.assert_true(deltas["writer_delta"] > 0, "writer 应加分")
        self.assert_true(deltas["critic_delta"] > 0, "critic 应加分")

        scores = ag.load_agent_scores()
        self.assert_true(scores["writer"]["score"] > 100, "writer 全局分数上升")
        self.assert_true(scores["critic"]["score"] > 100, "critic 全局分数上升")

    def _test_collusion_penalty(self):
        ag = self._make_ag()
        monitor_result = {
            "success": True,
            "monitor_independent_score": 0.50,
            "writer_prohibitions": [],
            "critic_prohibitions": [],
            "writer_suggested_delta": 10,
            "critic_suggested_delta": 10,
            "collusion_risk": "high",
            "negative_feedback": False,
            "overall_assessment": "疑似串通",
            "raw_output": "",
        }
        prop_state = {"monitor_history": []}
        deltas = ag.apply_monitor_result(
            proposal_id="general-test-20260101",
            round_num=1,
            section_key="rationale",
            score_before=0.70,
            score_after=0.95,
            dim_scores={},
            monitor_result=monitor_result,
            proposal_state=prop_state,
        )
        self.assert_true(deltas["writer_delta"] < 0, "串通时 writer 应被惩罚")
        self.assert_true(deltas["critic_delta"] < 0, "串通时 critic 应被惩罚")

    def _test_negative_feedback_detection(self):
        ag = self._make_ag()
        prop_state = {"monitor_history": [
            {"monitor_independent_score": 0.70, "local_writer_score": 95, "local_critic_score": 95, "collusion_risk": "none"},
            {"monitor_independent_score": 0.65, "local_writer_score": 90, "local_critic_score": 90, "collusion_risk": "none"},
            {"monitor_independent_score": 0.60, "local_writer_score": 85, "local_critic_score": 85, "collusion_risk": "none"},
        ]}
        alert, reasons = ag.check_negative_feedback(prop_state)
        self.assert_true(alert, "连续分数下降应触发负反馈")
        self.assert_true(any("monitor" in r for r in reasons), "原因包含 monitor 分数下降")

    def _test_record_monitor_history(self):
        ag = self._make_ag()
        prop_state = {"monitor_history": []}
        monitor_result = {
            "writer_prohibitions": [], "critic_prohibitions": [],
            "collusion_risk": "none", "negative_feedback": False,
            "overall_assessment": "ok",
        }
        deltas = {"writer_delta": 5, "critic_delta": 3, "monitor_independent_score": 0.80, "high_issues_after": 1}
        new_state = ag.record_monitor_history(
            prop_state, 1, "rationale", 0.70, 0.80, monitor_result, deltas
        )
        self.assert_eq(len(new_state["monitor_history"]), 1, "记录了一条历史")
        self.assert_eq(new_state["monitor_history"][0]["local_writer_score"], 105, "本地 writer 分数累加")
        self.assert_eq(new_state["monitor_history"][0]["local_critic_score"], 103, "本地 critic 分数累加")

    def _test_clear_negative_feedback(self):
        lc = self.pl.ProposalLifecycle()
        pid = "general-clear-nf-20260101"
        lc.register(pid, project_type="general")
        state = lc._get_proposal_state(pid)
        state["negative_feedback_alert"] = True
        state["negative_feedback_reasons"] = ["分数连续下降"]
        lc._set_proposal_state(pid, state)

        result = lc.clear_negative_feedback(pid, reason="测试清除")
        self.assert_true(result.get("success"), "清除成功")
        new_state = lc._get_proposal_state(pid)
        self.assert_eq(new_state.get("negative_feedback_alert"), False, "告警已清除")
        self.assert_eq(len(new_state.get("negative_feedback_reasons", [])), 0, "原因已清空")
        self.assert_eq(len(new_state.get("negative_feedback_cleared", [])), 1, "清除历史已记录")

    def run_tests(self):
        self._test_initial_scores()
        self._test_writer_placeholder_detection()
        self._test_writer_template_rigidity()
        self._test_writer_surface_change()
        self._test_critic_lazy_review()
        self._test_critic_rigid_scoring()
        self._test_critic_score_content_mismatch()
        self._test_rule_deltas_progress()
        self._test_rule_deltas_penalty()
        self._test_apply_monitor_result_updates_scores()
        self._test_collusion_penalty()
        self._test_negative_feedback_detection()
        self._test_record_monitor_history()
        self._test_clear_negative_feedback()
