#!/usr/bin/env python3
"""负反馈全局回升解除测试（v6.10.5）。

背景：负反馈条件"writer/critic 全局分数低于 50"使用跨课题共享的全局
agent 分数——任一课题的惨烈对抗把全局分拖破 50 会连锁触发其他健康课题
的告警（2026-09-09 实测：qgi 把 writer 拖到 45.6，mos2/order-parameter/
key-transient 被连坐冻结流转）。且自动清除额度（每课题 1 次 24h 冷却）
早已耗尽的课题只能等人工。

v6.10.5 修复：lifecycle/utils.global_recovery_clear_plan 提供回升感知
解除计划；lifecycle_monitor._auto_heal_negative_feedback 在 24h 冷却
路径前接入（不占额度、不降级 idea_review_required）。

用法：
    python3 scripts/tests/test_negative_feedback_global_recovery.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test_runner import (  # noqa: E402
    TestSuite, create_isolated_env, patch_module_root,
)


class NegativeFeedbackGlobalRecoveryTest(TestSuite):
    """全局回升解除计划的判定矩阵 + scoring 复位清理。"""

    def __init__(self):
        super().__init__("负反馈全局回升解除测试")
        self._plan = None
        self._floor = None
        self._scoring = None
        self.tmp_root = None
        self._orig_project_root = None

    def setup(self):
        # v6.10.33: 补齐隔离——旧 setup 只调 create_isolated_env() 未接收返回值
        # 且未重定向 proposal_lifecycle 根路径，第 10 节的
        # ProposalLifecycle()._load_state()/_save_state() 直写真实生产
        # research_proposals/_lifecycle.json（test-proposal-clear-nfa 残留
        # 生产 optimizing 队列，09-21 实测被微调度器聚焦派发 2 个 job）。
        self.tmp_root = create_isolated_env()
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("proposal_lifecycle") or mod_name in ("paths",):
                del sys.modules[mod_name]

        import paths
        self._orig_project_root = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root

        import proposal_lifecycle.constants as plc
        plc.PROJECT_ROOT = self.tmp_root
        plc.PROPOSALS_ROOT = self.tmp_root / "research_proposals"
        patch_module_root("proposal_lifecycle", self.tmp_root)

        from lifecycle.utils import (
            NEG_FEEDBACK_GLOBAL_FLOOR,
            global_recovery_clear_plan,
        )
        from adversarial import scoring as scoring_mod

        self._plan = global_recovery_clear_plan
        self._floor = NEG_FEEDBACK_GLOBAL_FLOOR
        self._scoring = scoring_mod

    def teardown(self):
        # 恢复真实根路径（防后续套件沿用隔离值）
        if self._orig_project_root is not None:
            import paths
            paths.PROJECT_ROOT = self._orig_project_root
        if self.tmp_root and self.tmp_root.exists():
            import shutil
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _alert_state(self, reasons, **extra):
        state = {
            "status": "optimizing",
            "negative_feedback_alert": True,
            "negative_feedback_reasons": list(reasons),
        }
        state.update(extra)
        return state

    def run_tests(self):
        plan = self._plan
        floor = self._floor
        scores_recovered = {"writer": {"score": 62.0}, "critic": {"score": 148.0}}
        scores_low = {"writer": {"score": 45.6}, "critic": {"score": 148.0}}

        # ---------- 1. 仅全局原因 + 分数回升 → clear ----------
        st = self._alert_state(["writer 全局分数低于 50"])
        res = plan(st, scores_recovered)
        self.assert_eq(res.get("action"), "clear", "仅连坐原因且 writer 已回升 → 解除")

        # ---------- 2. 全局 + 自身原因混合 + 回升 → trim ----------
        st2 = self._alert_state([
            "monitor 独立分数连续 3 轮下降",
            "writer 全局分数低于 50",
        ])
        res2 = plan(st2, scores_recovered)
        self.assert_eq(res2.get("action"), "trim", "混合原因回升 → 裁剪保留自身原因")
        self.assert_eq(
            res2.get("remaining"),
            ["monitor 独立分数连续 3 轮下降"],
            "trim 后仅剩课题自身原因",
        )

        # ---------- 3. 全局原因未回升 → 维持现状 ----------
        st3 = self._alert_state(["writer 全局分数低于 50"])
        res3 = plan(st3, scores_low)
        self.assert_true(res3 is None, "writer 仍 <50 → 不解除（连坐未恢复）")

        # ---------- 4. 无全局原因（纯课题自身）→ 不走回升路径 ----------
        st4 = self._alert_state(["monitor 独立分数连续 3 轮下降"])
        res4 = plan(st4, scores_recovered)
        self.assert_true(res4 is None, "纯自身原因不适用回升解除")

        # ---------- 5. 无告警 / 空 reasons → None ----------
        res5 = plan({"negative_feedback_alert": False, "negative_feedback_reasons": ["writer 全局分数低于 50"]}, scores_recovered)
        self.assert_true(res5 is None, "无告警不处理")
        res5b = plan(self._alert_state([]), scores_recovered)
        self.assert_true(res5b is None, "空 reasons 不处理")

        # ---------- 6. critic 全局原因同样适用 ----------
        st6 = self._alert_state(["critic 全局分数低于 50"])
        res6 = plan(st6, scores_recovered)
        self.assert_eq(res6.get("action"), "clear", "critic 回升同样解除")

        # ---------- 7. 分数读不到（缺键）→ 视为未恢复 ----------
        res7 = plan(self._alert_state(["writer 全局分数低于 50"]), {})
        self.assert_true(res7 is None, "无分数数据 → 保守不解除")

        # ---------- 8. 阈值边界：恰好 50 → 恢复 ----------
        res8 = plan(
            self._alert_state(["writer 全局分数低于 50"]),
            {"writer": {"score": float(floor)}},
        )
        self.assert_eq(res8.get("action"), "clear", "恰好回到阈值即恢复")

        # ---------- 9. scoring 复位清理残留 reasons + nfa_at（v6.10.5 G3 + v6.10.25） ----------
        from common import now_utc

        prop_state = {
            "monitor_history": [],
            "negative_feedback_alert": True,
            "negative_feedback_reasons": ["writer 全局分数低于 50"],  # 历史残留
            "negative_feedback_at": now_utc(),  # 历史残留时间戳
        }
        # 空历史 + agent 分健康 → check_negative_feedback 返回 False
        alert, reasons = self._scoring.check_negative_feedback(
            prop_state, agent_scores=scores_recovered
        )
        self.assert_true(not alert, "健康状态不复位告警逻辑本身（前置条件）")
        # record_monitor_round 走完整写入路径验证复位清理
        deltas = {
            "writer_delta": 1.0,
            "critic_delta": 1.0,
            "monitor_independent_score": 0.8,
            "high_issues_after": 0,
        }
        monitor_result = {
            "monitor_independent_score": 0.8,
            "collusion_risk": "none",
            "overall_assessment": "ok",
        }
        updated = self._scoring.record_monitor_history(
            prop_state, 1, "content", 0.7, 0.8, monitor_result,
            deltas, scores_recovered,
        )
        self.assert_true(
            not updated.get("negative_feedback_alert"),
            "健康轮次后 alert 应复位",
        )
        self.assert_eq(
            updated.get("negative_feedback_reasons"),
            [],
            "alert 复位时 reasons 应清空（不再残留历史原因）",
        )
        self.assert_true(
            "negative_feedback_at" not in updated,
            "alert 复位时应同步清除 negative_feedback_at（v6.10.25 方向 A，避免冷却按旧时刻判定 / waiting 虚高）",
        )

        # ---------- 10. cron.clear_negative_feedback 同步清除 nfa_at（v6.10.25） ----------
        from proposal_lifecycle import ProposalLifecycle

        lc = ProposalLifecycle()
        pid = "test-proposal-clear-nfa"
        original_state = {
            "status": "optimizing",
            "negative_feedback_alert": True,
            "negative_feedback_reasons": ["monitor 独立分数连续 3 轮下降"],
            "negative_feedback_at": now_utc(),
            "negative_feedback_auto_clear_count": 1,
        }
        # 清除前先注册（ProposalLifecycle 需要 state 可读写）
        state = lc._load_state()
        state.setdefault("proposals", {})[pid] = original_state
        lc._save_state(state)
        res = lc.clear_negative_feedback(pid, reason="test")
        self.assert_true(res.get("success"), "人工清除应成功")
        cleared = (lc._load_state()["proposals"] or {}).get(pid) or {}
        self.assert_true(
            "negative_feedback_at" not in cleared,
            "人工清除告警时应同步清除 negative_feedback_at，供后续再次触发时从真实时刻重新起算冷却（v6.10.25 方向 A）",
        )


if __name__ == "__main__":
    import time

    suite = NegativeFeedbackGlobalRecoveryTest()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report

    print_report([suite])
