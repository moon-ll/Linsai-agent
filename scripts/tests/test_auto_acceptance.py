#!/usr/bin/env python3
"""智能化与自动化测试（v6.9.0）。

背景（2026-08-14 智能化评估）：目标是"人只在关键节点做验收，且验收
有智能辅助"。本套件验证六项自动化机制的判定规则不被回归破坏：

  R1 验收决策包：预审规则（approve/attention/reject）+ 一键采纳守卫 + diff 摘要
  R2 负反馈自愈：24h 冷却 + 单次上限 + 无时间戳保守不清除
  R3 最佳轮次回退：连续下降 + 距最佳幅度 + 单次上限 + 文件回退
  R4 立项决策包：激活建议三档 + 可行性启发式
  R5 策略自动应用：白名单 + 门槛单向 + 7 天去重 + 单次上限
  R6 待人工队列：聚合 + 降噪（自动清除未用尽不进队列）+ 72h 催办

运行：python3 scripts/self_test.py --module（自动纳入）
"""

import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from test_runner import TestSuite, create_isolated_env, patch_module_root


def _base_score_history(rounds=5, score=0.88):
    """构造 5 模块全通过的 score_history。"""
    sections = ["rationale", "content", "scheme", "full_review", "references"]
    return [
        {"round": i + 1, "focus_section": s, "score": score, "section_passed": True}
        for i, s in enumerate(sections[:rounds])
    ]


# ============================================================
# R1: 验收决策包
# ============================================================


class ReviewDossierTests(TestSuite):
    """决策包预审规则与一键采纳守卫。"""

    def __init__(self):
        super().__init__("验收决策包预审")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from review_dossier import (
            APPROVE_SCORE_GATE,
            VERDICT_APPROVE,
            VERDICT_ATTENTION,
            VERDICT_REJECT,
            can_adopt_pre_review,
            compute_pre_review,
            generate_review_dossier,
            last_entry_per_section,
            summarize_draft_diff,
        )

        base = {
            "score_history": _base_score_history(),
            "open_critical_issues": [],
            "last_monitor_score": 0.88,
            "optimization_rounds": 5,
        }

        # ── 用例 1：全通过 + 高分 + 无问题 → approve_lean ──
        pre = compute_pre_review(base)
        self.assert_eq(pre["verdict"], VERDICT_APPROVE, "5/5 通过且 0.88 应建议通过")
        self.assert_eq(pre["metrics"]["passed_modules"], 5, "模块计数应为 5")

        # ── 用例 2：高危未解决 → reject_lean（优先级最高） ──
        bad = dict(base)
        bad["open_critical_issues"] = [{"severity": "high"}, {"severity": "medium"}]
        pre = compute_pre_review(bad)
        self.assert_eq(pre["verdict"], VERDICT_REJECT, "高危问题应优先建议退回")
        self.assert_eq(pre["metrics"]["high_issues"], 1, "高危计数应为 1")

        # ── 用例 3：仅 2 模块（真实 bsv 案例）→ reject_lean ──
        few = dict(base)
        few["score_history"] = _base_score_history(rounds=2)
        self.assert_eq(
            compute_pre_review(few)["verdict"], VERDICT_REJECT, "2/5 模块应建议退回"
        )

        # ── 用例 4：逃生阀质量警告 → attention（人看警告后裁量） ──
        warn = dict(base)
        warn["quality_warning"] = "达到最大轮数8（已通过2/5模块）"
        self.assert_eq(
            compute_pre_review(warn)["verdict"], VERDICT_ATTENTION, "质量警告应转人工裁量"
        )

        # ── 用例 5：低分 → reject_lean ──
        low = dict(base)
        low["last_monitor_score"] = 0.70
        self.assert_eq(
            compute_pre_review(low)["verdict"], VERDICT_REJECT, "0.70 低于退回线应建议退回"
        )

        # ── 用例 6：已解决的 issue 不计入 ──
        resolved = dict(base)
        resolved["open_critical_issues"] = [{"severity": "high", "round_resolved": 4}]
        pre = compute_pre_review(resolved)
        self.assert_eq(
            pre["metrics"]["unresolved_issues"], 0, "已解决问题不应计入未解决"
        )

        # ── 用例 7：一键采纳守卫（分数门槛） ──
        self.assert_eq(
            can_adopt_pre_review(
                {"pre_review_verdict": VERDICT_APPROVE, "last_score": APPROVE_SCORE_GATE}
            ),
            True,
            "approve_lean + 0.85 应允许采纳",
        )
        self.assert_eq(
            can_adopt_pre_review(
                {"pre_review_verdict": VERDICT_APPROVE, "last_score": 0.84}
            ),
            False,
            "低于门槛不应允许采纳",
        )
        self.assert_eq(can_adopt_pre_review(None), False, "无决策包不应允许采纳")
        self.assert_eq(
            can_adopt_pre_review(
                {"pre_review_verdict": VERDICT_ATTENTION, "last_score": 0.95}
            ),
            False,
            "attention 预审不应允许采纳",
        )

        # ── 用例 8：模块取最近一次轮次记录 ──
        sm = last_entry_per_section(
            [
                {"round": 1, "focus_section": "rationale", "score": 0.6, "section_passed": False},
                {"round": 3, "focus_section": "rationale", "score": 0.8, "section_passed": True},
            ]
        )
        self.assert_eq(
            sm["rationale"]["round"], 3, "同模块应取最近一次记录"
        )

        # ── 用例 9：diff 摘要 + 端到端生成（临时目录） ──
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pid = "t-dossier"
            pdir = root / "optimizing" / pid / "04_proposal"
            pdir.mkdir(parents=True)
            (pdir / "proposal-draft-r1.md").write_text(
                "旧内容行\n" * 10, encoding="utf-8"
            )
            (pdir / "proposal-draft.md").write_text(
                "新内容行\n" * 14, encoding="utf-8"
            )
            diff = summarize_draft_diff(root / "optimizing" / pid)
            self.assert_eq(diff["added_lines"], 14, "新增行数应为 14")
            self.assert_eq(diff["removed_lines"], 10, "删除行数应为 10")

            state = {"proposals": {pid: dict(base, title="决策包端到端")}}
            from common import save_json

            save_json(root / "_lifecycle.json", state)
            result = generate_review_dossier(pid, proposals_root=root, update_state=False)
            self.assert_eq(result.get("success"), True, "端到端生成应成功")
            self.assert_eq(result["can_adopt"], True, "该状态应可一键采纳")
            md = (root / "optimizing" / pid / "05_review" / "review-dossier.md")
            self.assert_eq(md.exists(), True, "决策包 md 应写入 05_review")
            text = md.read_text(encoding="utf-8")
            self.assert_in("建议通过", text, "md 应包含预审结论")
            self.assert_in("参考文献", text, "md 应包含模块表")

        # ── 用例 10：diff 无备份 → None（不抛异常） ──
        self.assert_eq(summarize_draft_diff(None), None, "无目录应返回 None")


# ============================================================
# R2: 负反馈自愈
# ============================================================


class NegativeFeedbackHealTests(TestSuite):
    """负反馈告警 24h 冷却自动清除策略。"""

    def __init__(self):
        super().__init__("负反馈自愈策略")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from lifecycle.utils import should_auto_clear_negative_feedback

        now = datetime.now(timezone.utc)
        base = {
            "status": "optimizing",
            "negative_feedback_alert": True,
            "negative_feedback_reasons": ["维度分下降"],
        }

        def _at(hours_ago):
            return (now - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # ── 用例 1：冷却期满 → 清除 ──
        self.assert_eq(
            should_auto_clear_negative_feedback(dict(base, negative_feedback_at=_at(25)), now),
            True,
            "25h 前触发应自动清除",
        )
        # ── 用例 2：冷却期内 → 不清除（给根因修复留时间） ──
        self.assert_eq(
            should_auto_clear_negative_feedback(dict(base, negative_feedback_at=_at(10)), now),
            False,
            "10h 前触发不应清除",
        )
        # ── 用例 3：无告警 → False ──
        self.assert_eq(
            should_auto_clear_negative_feedback(
                {"negative_feedback_alert": False, "negative_feedback_at": _at(100)}, now
            ),
            False,
            "无告警不应清除",
        )
        # ── 用例 4：单次上限 ──
        self.assert_eq(
            should_auto_clear_negative_feedback(
                dict(base, negative_feedback_at=_at(100),
                     negative_feedback_auto_clear_count=1),
                now,
            ),
            False,
            "已自动清除过一次不应再清除",
        )
        # ── 用例 5：遗留数据无时间戳 → 保守不清除（monitor 补戳后起算） ──
        self.assert_eq(
            should_auto_clear_negative_feedback(dict(base), now),
            False,
            "无时间戳应保守返回 False",
        )
        # ── 用例 6：坏时间戳安全 ──
        self.assert_eq(
            should_auto_clear_negative_feedback(
                dict(base, negative_feedback_at="garbage"), now
            ),
            False,
            "坏时间戳应安全返回 False",
        )


# ============================================================
# R2b: auto-heal 降级标志副作用隔离（v6.9.36）
# ============================================================


class DemoteFlagSurvivalTests(TestSuite):
    """v6.9.36 回归：idea_review_required 不被比较路径无声消费。

    背景（08-21 order-param 实证）：负反馈 auto-heal 清除告警后设置
    idea_review_required=True 退回研究设想评审；但 _compute_actual_round
    把 _build_full_round_jobs 当纯比较函数调用，后者的清标志副作用把
    标志提前烧掉——真正建轮时拿不到标志，round 7 未前置 idea_review，
    降级链在最后一环断裂。修复：比较前快照、比较后恢复。
    """

    def __init__(self):
        super().__init__("降级标志副作用隔离")
        self.tmp_root = None
        self.ctrl_mod = None

    def setup(self):
        import importlib

        self.tmp_root = create_isolated_env()
        (self.tmp_root / "research_proposals" / "optimizing").mkdir(parents=True, exist_ok=True)
        for mod_name in ("proposal_lifecycle", "lifecycle_cron_framework"):
            sys.modules.pop(mod_name, None)
        self.ctrl_mod = importlib.import_module("lifecycle_cron_framework")
        patch_module_root("proposal_lifecycle", self.tmp_root)
        patch_module_root("lifecycle_cron_framework", self.tmp_root)

    def teardown(self):
        import shutil

        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _register(self, pid):
        c = self.ctrl_mod.LifecycleCronController()
        c.register(pid, project_type="general")
        c.transition(pid, "optimizing")
        prop_dir = c.root / "optimizing" / pid
        prop_dir.mkdir(parents=True, exist_ok=True)
        (prop_dir / "00_proposal-brief.md").write_text(f"# {pid}\n", encoding="utf-8")
        (prop_dir / "04_proposal").mkdir(exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text("# draft\n", encoding="utf-8")
        return c

    def run_tests(self):
        pid = "general-demote-fix-20260101"
        c = self._register(pid)

        # 前置：round 1 已闭环 + idea_review 已通过 → round 2 全链不含 idea_review
        st = c._get_proposal_state(pid)
        st["optimization_rounds"] = 1
        st["idea_review_passed"] = True
        c._set_proposal_state(pid, st)
        c.sync_checkpoint(pid)
        jobs = c._get_jobs(pid)
        self.assert_eq(
            len([j for j in jobs if j["step"] == "idea_review"]), 0,
            "前置：无降级标志时 round 2 不含 idea_review",
        )
        for j in jobs:
            j["status"] = "done"
        c._save_jobs(pid, jobs)

        # 模拟 auto-heal：轮次闭环后设置降级标志
        st = c._get_proposal_state(pid)
        st["idea_review_required"] = True
        c._set_proposal_state(pid, st)

        # ── 用例 1：_compute_actual_round 比较路径不消费降级标志 ──
        c._compute_actual_round(pid, c._get_jobs(pid))
        st = c._get_proposal_state(pid)
        self.assert_eq(
            st.get("idea_review_required"), True,
            "_compute_actual_round 不应消费 idea_review_required（v6.9.36 修复）",
        )

        # ── 用例 2：sync_checkpoint 真正建轮时降级生效（回补 idea_review job）──
        c.sync_checkpoint(pid)
        jobs2 = c._get_jobs(pid)
        idea_jobs = [j for j in jobs2 if j["step"] == "idea_review"]
        self.assert_eq(
            len(idea_jobs) >= 1, True,
            "降级标志在场时 sync_checkpoint 应回补 idea_review job",
        )
        st = c._get_proposal_state(pid)
        self.assert_eq(
            st.get("idea_review_required"), False,
            "回补 job 落盘后标志才允许被消费",
        )


# ============================================================
# R3: 最佳轮次回退
# ============================================================


class AutoRollbackTests(TestSuite):
    """连续下降自动回退最佳轮次草稿。"""

    def __init__(self):
        super().__init__("最佳轮次自动回退")

    def setup(self):
        pass

    def teardown(self):
        pass

    def _history(self, scores):
        return [
            {"round": i + 1, "focus_section": "rationale", "score": s}
            for i, s in enumerate(scores)
        ]

    def run_tests(self):
        from lifecycle.utils import perform_auto_rollback, should_auto_rollback

        # ── 用例 1：两连降 + 距最佳超幅度 → 触发 ──
        plan = should_auto_rollback(
            {"score_history": self._history([0.80, 0.86, 0.90, 0.84, 0.78])}
        )
        self.assert_eq(plan is not None, True, "两连降应触发回退")
        self.assert_eq(plan["best_round"], 3, "最佳轮应为 R3")
        self.assert_eq(plan["best_score"], 0.90, "最佳分应为 0.90")

        # ── 用例 2：最新就是最佳 → 不回退 ──
        self.assert_eq(
            should_auto_rollback({"score_history": self._history([0.80, 0.75, 0.86])}),
            None,
            "最新轮最佳时无可回退",
        )
        # ── 用例 3：距最佳不足幅度（天花板波动）→ 不回退 ──
        self.assert_eq(
            should_auto_rollback({"score_history": self._history([0.88, 0.90, 0.89])}),
            None,
            "0.89 距 0.90 不足幅度不应回退",
        )
        # ── 用例 4：非连续下降 → 不回退 ──
        self.assert_eq(
            should_auto_rollback({"score_history": self._history([0.80, 0.75, 0.78])}),
            None,
            "未构成两连降不应回退",
        )
        # ── 用例 5：单次上限 ──
        self.assert_eq(
            should_auto_rollback(
                {"score_history": self._history([0.80, 0.86, 0.90, 0.84, 0.78]),
                 "auto_rollback_count": 1}
            ),
            None,
            "已回退过一次不应再回退",
        )
        # ── 用例 6：历史不足 → None ──
        self.assert_eq(
            should_auto_rollback({"score_history": self._history([0.9, 0.8])}),
            None,
            "少于 3 轮不应回退",
        )

        # ── 用例 7：文件回退端到端（临时目录） ──
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pid = "t-rollback"
            pdir = root / "optimizing" / pid / "04_proposal"
            pdir.mkdir(parents=True)
            (pdir / "proposal-draft-r3.md").write_text("最佳版本", encoding="utf-8")
            (pdir / "proposal-draft.md").write_text("退化版本", encoding="utf-8")

            prop_state = {
                "score_history": self._history([0.80, 0.86, 0.90, 0.84, 0.78])
            }
            plan = should_auto_rollback(prop_state)
            res = perform_auto_rollback(pid, prop_state, plan, root=root)
            self.assert_eq(res.get("success"), True, "回退应成功")
            self.assert_eq(
                (pdir / "proposal-draft.md").read_text(encoding="utf-8"),
                "最佳版本",
                "草稿应恢复为最佳轮内容",
            )
            self.assert_eq(
                (pdir / "proposal-draft-pre-rollback.md").read_text(encoding="utf-8"),
                "退化版本",
                "回退前草稿应另存保全",
            )
            self.assert_eq(prop_state["auto_rollback_count"], 1, "回退计数应为 1")
            self.assert_eq(prop_state["rolled_back_to_round"], 3, "回退目标轮应为 3")
            self.assert_eq(len(prop_state["rollback_history"]), 1, "应有回退历史")

            # 备份缺失 → 失败不抛异常
            (pdir / "proposal-draft-r3.md").unlink()
            res2 = perform_auto_rollback(pid, prop_state, plan, root=root)
            self.assert_eq(res2.get("success"), False, "备份缺失应失败")


# ============================================================
# R4: 立项决策包
# ============================================================


class IdeaDossierTests(TestSuite):
    """激活建议三档与可行性启发式。"""

    def __init__(self):
        super().__init__("立项决策包建议")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from idea_generator import _feasibility_hint, recommend_activation

        # ── 用例 1-3：三档建议 ──
        rec, _ = recommend_activation(0.72)
        self.assert_eq(rec, "hold", "0.72 高度重叠应建议搁置")
        rec, _ = recommend_activation(0.40)
        self.assert_eq(rec, "merge考察", "0.40 应建议融合考察")
        rec, _ = recommend_activation(0.10)
        self.assert_eq(rec, "activate", "0.10 新颖应建议激活")

        # ── 用例 4-6：可行性启发式 ──
        self.assert_eq(
            _feasibility_hint("搭建激光实验测量样品")["mode"],
            "实验导向",
            "实验关键词应识别实验导向",
        )
        self.assert_eq(
            _feasibility_hint("理论推导与数值模拟")["mode"],
            "理论导向",
            "理论关键词应识别理论导向",
        )
        self.assert_eq(
            _feasibility_hint("理论建模指导实验测量")["mode"],
            "理实结合",
            "双范式应识别理实结合",
        )


# ============================================================
# R5: 策略自动应用
# ============================================================


class StrategyAutoApplyTests(TestSuite):
    """低风险策略自动应用筛选规则。"""

    def __init__(self):
        super().__init__("策略自动应用规则")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from strategy_optimizer import select_auto_appliable

        now = datetime(2026, 8, 14, tzinfo=timezone.utc)
        cur = {"stagger_seconds": 60, "score_threshold": 0.9, "max_rounds": 8}

        # ── 用例 1：门槛下调被拒（单向规则） ──
        sug = {"stagger_seconds": 90, "score_threshold": 0.85}
        keys = [c["key"] for c in select_auto_appliable(cur, sug, [], now=now)]
        self.assert_eq(keys, ["stagger_seconds"], "门槛下调必须被拒")

        # ── 用例 2：门槛上调放行 ──
        sug = {"stagger_seconds": 60, "score_threshold": 0.95}
        keys = [c["key"] for c in select_auto_appliable(cur, sug, [], now=now)]
        self.assert_eq(keys, ["score_threshold"], "门槛上调应放行")

        # ── 用例 3：max_rounds 永不自动（白名单外） ──
        sug = {"max_rounds": 6, "score_threshold": 0.85}
        keys = [c["key"] for c in select_auto_appliable(cur, sug, [], now=now)]
        self.assert_eq(keys, [], "白名单外参数不应自动应用")

        # ── 用例 4：7 天去重 ──
        log = [
            {"at": (now - timedelta(days=1)).isoformat(),
             "new": {"stagger_seconds": 90}}
        ]
        sug = {"stagger_seconds": 90}
        self.assert_eq(
            select_auto_appliable(cur, sug, log, now=now),
            [],
            "7 天内已应用应去重跳过",
        )
        # ── 用例 5：超 7 天不拦截 ──
        log_old = [
            {"at": (now - timedelta(days=8)).isoformat(),
             "new": {"stagger_seconds": 90}}
        ]
        self.assert_eq(
            len(select_auto_appliable(cur, sug, log_old, now=now)),
            1,
            "8 天前应用不应拦截",
        )
        # ── 用例 6：无变化不产生条目 ──
        self.assert_eq(
            select_auto_appliable(cur, {"stagger_seconds": 60}, [], now=now),
            [],
            "值未变化不应应用",
        )


# ============================================================
# R6: 待人工队列
# ============================================================


class HumanQueueTests(TestSuite):
    """队列聚合、降噪与催办阈值。"""

    def __init__(self):
        super().__init__("待人工队列聚合")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from human_queue import collect_human_queue

        now = datetime(2026, 8, 14, 12, 0, tzinfo=timezone.utc)

        def _iso(hours_ago):
            return (now - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")

        proposals = {
            # 待审 80h（催办）+ 预审 reject_lean
            "p-review": {
                "status": "pending_review",
                "title": "久等课题",
                "transition_history": [
                    {"to": "pending_review", "at": _iso(80)}
                ],
                "review_dossier": {
                    "pre_review_verdict": "reject_lean",
                    "can_adopt": False,
                },
            },
            # drafts 30h（不催办）
            "p-draft": {
                "status": "drafts",
                "title": "新设想",
                "created_at": _iso(30),
                "idea_dossier": {"recommendation": "activate"},
            },
            # 负反馈冷却中（自动清除未用尽）→ 降噪不入队
            "p-neg": {
                "status": "optimizing",
                "negative_feedback_alert": True,
                "negative_feedback_at": _iso(30),
                "negative_feedback_auto_clear_count": 0,
            },
            # 负反馈自动清除已用尽 → 入队
            "p-neg2": {
                "status": "optimizing",
                "negative_feedback_alert": True,
                "negative_feedback_at": _iso(50),
                "negative_feedback_auto_clear_count": 1,
                "negative_feedback_reasons": ["维度分停滞"],
            },
            # 正常优化 → 不入队
            "p-ok": {"status": "optimizing"},
            # 已归档 → 不入队
            "p-done": {"status": "archived"},
        }

        result = collect_human_queue(proposals=proposals, now=now)
        ids = {i["proposal_id"] for i in result["items"]}
        self.assert_eq(
            ids, {"p-review", "p-draft", "p-neg2"}, "应只聚合等人事项（冷却中负反馈降噪）"
        )
        self.assert_eq(result["summary"]["total"], 3, "总数应为 3")
        self.assert_eq(result["summary"]["escalated"], 1, "仅 80h 项催办")

        review = next(i for i in result["items"] if i["proposal_id"] == "p-review")
        self.assert_eq(review["escalate"], True, "80h 应触发催办")
        self.assert_eq(review["waiting_hours"], 80.0, "等待时长应为 80h")
        self.assert_in("退回", review["suggested_action"], "reject_lean 建议应含退回")
        self.assert_eq(review["can_adopt"], False, "reject 不可一键采纳")

        draft = next(i for i in result["items"] if i["proposal_id"] == "p-draft")
        self.assert_eq(draft["escalate"], False, "30h 不应催办")
        self.assert_in("activate", draft["suggested_action"], "建议应含激活")

        neg = next(i for i in result["items"] if i["proposal_id"] == "p-neg2")
        self.assert_in("人工清除", neg["suggested_action"], "用尽后建议人工清除")


if __name__ == "__main__":
    total_fail = 0
    for cls in (
        ReviewDossierTests,
        NegativeFeedbackHealTests,
        AutoRollbackTests,
        IdeaDossierTests,
        StrategyAutoApplyTests,
        HumanQueueTests,
    ):
        suite = cls()
        suite.setup()
        suite.run_tests()
        suite.teardown()
        ok = sum(1 for r in suite.results if r.passed)
        total_fail += len(suite.results) - ok
        print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if total_fail else 0)
