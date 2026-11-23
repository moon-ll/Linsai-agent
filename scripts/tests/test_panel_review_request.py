#!/usr/bin/env python3
"""平台期转评审团分层策略测试（v6.10.14 + v7.1.8）。

覆盖：
- 平台带检测（0.70-0.85 连续 4 轮 |Δ|<2%）→ panel_review_requested；
- v7.1.8 r3 触发（不依赖分数窗口）→ panel_review_requested；
- 调度跳过；人工队列 panel_request 类型；clear_panel_request 恢复；
- v7.1.8 panel_review_completed_for_round 标志 + reset_panel_cycle 解除。

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_panel_review_request.py
"""

import sys
import tempfile
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


def _is_platform_window(scores):
    """复刻 completion 的平台带判定（纯函数化便于单测）。"""
    if len(scores) < 4:
        return False
    if not all(0.70 <= s < 0.85 for s in scores[-4:]):
        return False
    w = scores[-4:]
    return all(abs(w[i + 1] - w[i]) < 0.02 for i in range(3))


class PanelReviewRequestTests(TestSuite):
    def __init__(self):
        super().__init__("平台期转评审团测试（v6.10.14）")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        # ── 1. 平台带判定口径 ─────────────────────────────────
        self.assert_true(_is_platform_window([0.72, 0.73, 0.72, 0.71]),
                         "主平台带连续 4 轮微幅波动应命中")
        self.assert_true(not _is_platform_window([0.60, 0.65, 0.70, 0.74]),
                         "爬坡型（逐轮 +0.04-0.05）不应命中")
        self.assert_true(not _is_platform_window([0.72, 0.73, 0.72, 0.66]),
                         "末轮跌破 0.70 不应命中")
        self.assert_true(not _is_platform_window([0.86, 0.86, 0.85, 0.86]),
                         "≥0.85 高位平台属收敛/次优检测管辖，不属本带")
        self.assert_true(not _is_platform_window([0.72, 0.73, 0.72]),
                         "不足 4 轮不命中")
        self.assert_true(not _is_platform_window([0.72, 0.75, 0.72, 0.73]),
                         "单轮 Δ=0.03 超阈不命中")

        # ── 2. 检测源码锚点（completion.py 存在检测块）────────
        src = (_SCRIPTS_DIR / "proposal_lifecycle" / "completion.py").read_text(encoding="utf-8")
        self.assert_true("panel_review_requested" in src and "PANEL_FLOOR" in src,
                         "completion 应含平台期检测块")

        # ── 3. 调度过滤（list_by_status + _focus_proposal_for_slot）──
        from proposal_lifecycle.transitions import TransitionsMixin  # noqa: F401
        ms_src = (_SCRIPTS_DIR / "lifecycle" / "micro_scheduler.py").read_text(encoding="utf-8")
        self.assert_true("panel_review_requested" in ms_src,
                         "调度器应过滤平台期课题")
        tr_src = (_SCRIPTS_DIR / "proposal_lifecycle" / "transitions.py").read_text(encoding="utf-8")
        self.assert_true("panel_review_requested" in tr_src,
                         "list_by_status 应携带标志字段")

        # ── 4. 人工队列 panel_request 聚合 ─────────────────────
        from human_queue import collect_human_queue
        proposals = {
            "p-panel": {
                "status": "optimizing", "title": "平台课题", "last_score": 0.72,
                "panel_review_requested": True,
                "panel_review_reason": "主平台带：连续4轮 0.70-0.85",
            },
            "p-normal": {"status": "optimizing", "title": "正常", "last_score": 0.5},
        }
        hq = collect_human_queue(proposals=proposals)
        panel = [i for i in hq["items"] if i["type"] == "panel_request"]
        self.assert_eq(len(panel), 1, "平台期课题应入队 panel_request")
        self.assert_eq(panel[0]["proposal_id"], "p-panel", "提案 ID")
        self.assert_true("评审团" in panel[0]["suggested_action"], "建议动作应指向评审团")
        self.assert_eq(hq["summary"].get("panel_request"), 1, "summary 计数")

        # 普通课题不受影响
        hq2 = collect_human_queue(proposals={"p-normal": proposals["p-normal"]})
        self.assert_eq(
            sum(1 for i in hq2["items"] if i["type"] == "panel_request"), 0,
            "非平台课题不应入 panel_request")

        # ── 5. clear_panel_request 恢复（继承 CronMixin 真实实现）──
        from proposal_lifecycle.cron import CronMixin

        class _FakeLC(CronMixin):
            _store = {"p-x": {
                "status": "optimizing",
                "panel_review_requested": True,
                "panel_review_reason": "主平台带",
            }}
            def _get_proposal_state(self, pid):
                return dict(self._store.get(pid) or {})
            def _set_proposal_state(self, pid, st):
                self._store[pid] = st

        fake = _FakeLC()
        r = fake.clear_panel_request("p-x", reason="评审团已完成修改")
        self.assert_true(r.get("success"), "清除应成功")
        st = fake._store["p-x"]
        self.assert_true(not st.get("panel_review_requested"), "标志应清除")
        self.assert_true("panel_review_cleared_at" in st, "应记录清除时间")
        r2 = fake.clear_panel_request("p-x")
        self.assert_true(r2.get("success") and "无评审团请求需清除" in str(r2.get("message", "")),
                         "重复清除幂等")

        # ── 6. v6.10.15: waiting_hours 驱动催办 ────────────────
        from datetime import datetime, timezone, timedelta
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=80)).strftime("%Y-%m-%dT%H:%M:%SZ")
        proposals3 = {
            "p-panel-old": {
                "status": "optimizing", "title": "久等课题", "last_score": 0.74,
                "panel_review_requested": True,
                "panel_requested_at": old_ts,
                "panel_review_reason": "主平台带",
            },
        }
        hq3 = collect_human_queue(proposals=proposals3)
        p3 = [i for i in hq3["items"] if i["type"] == "panel_request"][0]
        self.assert_true(p3.get("waiting_hours") is not None and p3["waiting_hours"] >= 79,
                         "waiting_hours 应按 panel_requested_at 起算")
        self.assert_true(p3.get("escalate"), "超 72h 应 escalate 触发催办")

        # ── 7. v6.10.15: 反思任务 panel_plan 注册 ──────────────
        from weekend_pipeline.jobs import stage_job_templates
        steps = [t.get("step") for t in stage_job_templates("reflection")]
        self.assert_true("panel_plan" in steps, "反思任务应含 panel_plan")

        # ── 8. v6.10.15: monitor 催办标签 ─────────────────────
        mon_src = (_SCRIPTS_DIR / "lifecycle_monitor.py").read_text(encoding="utf-8")
        self.assert_true('"panel_request": "评审团"' in mon_src,
                         "monitor 催办标签应含评审团")

        # ── 9. v7.1.8: r3 强制触发评审团（不依赖分数窗口）──────
        comp_src = (_SCRIPTS_DIR / "proposal_lifecycle" / "completion.py").read_text(encoding="utf-8")
        self.assert_true("_PANEL_R3_TRIGGER = 3" in comp_src,
                         "completion 应含 r3 触发阈值常量")
        self.assert_true("r3 完成触发评审团" in comp_src or "r3 触发评审团" in comp_src,
                         "completion 应含 r3 触发逻辑块")

        # r3 触发语义：rounds>=3 + 未请求过 + 未完成过 → 设标志
        from proposal_lifecycle.cron import CronMixin

        class _FakeLC_r3(CronMixin):
            _store = {}
            def _get_proposal_state(self, pid):
                return dict(self._store.get(pid) or {})
            def _set_proposal_state(self, pid, st):
                self._store[pid] = st

        fake = _FakeLC_r3()

        # 场景 A: rounds=3, score_history=[0.65]（不在平台带）→ 仍触发
        fake._store["p-r3"] = {
            "status": "optimizing",
            "optimization_rounds": 3,
            "last_score": 0.65,
            "score_history": [{"score": 0.65, "round": 3}],
        }
        # 直接调用 completion 的 _check_done 不现实（依赖完整状态）；
        # 此处验证纯逻辑：r3 触发判定条件（rounds>=3 + 无 panel_review_requested + 无 panel_review_completed_for_round）
        ps = fake._get_proposal_state("p-r3")
        rounds = ps.get("optimization_rounds", 0)
        triggered = (
            rounds >= 3
            and not ps.get("panel_review_requested")
            and not ps.get("panel_review_completed_for_round")
        )
        self.assert_true(triggered, "r=3 课题应满足触发条件")

        # 场景 B: 同一课题已请求过 → 不重复触发
        ps_after = {
            "status": "optimizing",
            "optimization_rounds": 3,
            "last_score": 0.65,
            "panel_review_requested": True,
        }
        triggered2 = (
            ps_after.get("optimization_rounds", 0) >= 3
            and not ps_after.get("panel_review_requested")
            and not ps_after.get("panel_review_completed_for_round")
        )
        self.assert_true(not triggered2, "已 panel_review_requested 不应重复触发")

        # 场景 C: 已 panel_review_completed_for_round → 本周期不再触发
        ps_done = {
            "status": "optimizing",
            "optimization_rounds": 3,
            "last_score": 0.65,
            "panel_review_completed_for_round": 3,
        }
        triggered3 = (
            ps_done.get("optimization_rounds", 0) >= 3
            and not ps_done.get("panel_review_requested")
            and not ps_done.get("panel_review_completed_for_round")
        )
        self.assert_true(not triggered3, "已完成评审的课题本周期不应再触发")

        # 场景 D: rounds<3 不触发
        ps_r1 = {"optimization_rounds": 1}
        triggered4 = (
            ps_r1.get("optimization_rounds", 0) >= 3
            and not ps_r1.get("panel_review_requested")
            and not ps_r1.get("panel_review_completed_for_round")
        )
        self.assert_true(not triggered4, "rounds<3 不触发评审团")

        # ── 10. v7.1.8: clear_panel_request 标记本轮已完成──────
        fake2 = _FakeLC_r3()
        fake2._store["p-clr"] = {
            "status": "optimizing",
            "optimization_rounds": 4,
            "panel_review_requested": True,
        }
        r = fake2.clear_panel_request("p-clr", reason="评审团已完成")
        self.assert_true(r.get("success"), "clear_panel_request 应成功")
        st = fake2._store["p-clr"]
        self.assert_true("panel_review_completed_for_round" in st,
                         "clear 应标记本轮已完成")
        self.assert_eq(st["panel_review_completed_for_round"], 4,
                       "记录的是清除时的 rounds")
        self.assert_true(not st.get("panel_review_requested"), "标志应清除")

        # ── 11. v7.1.8: reset_panel_cycle 解除下一轮再触发 ──
        r2 = fake2.reset_panel_cycle("p-clr", reason="新一轮评审周期")
        self.assert_true(r2.get("success"), "reset_panel_cycle 应成功")
        st2 = fake2._store["p-clr"]
        self.assert_true("panel_review_completed_for_round" not in st2,
                         "reset 应清掉本轮已完成标记")
        # 此时 rounds=4 >= 3，无 panel_review_requested → 又满足触发
        retrigger = (
            st2.get("optimization_rounds", 0) >= 3
            and not st2.get("panel_review_requested")
            and not st2.get("panel_review_completed_for_round")
        )
        self.assert_true(retrigger, "reset 后下一轮评审周期应可再次触发")

        # ── 12. v7.1.8: 新进 optimizing 课题优先窗口（源码锚点）──
        ms_src = (_SCRIPTS_DIR / "lifecycle" / "micro_scheduler.py").read_text(encoding="utf-8")
        self.assert_true("_NEW_PROPOSAL_PRIORITY_WINDOW" in ms_src,
                         "调度器应含新课题优先窗口常量")
        self.assert_true("_check_r1_start_failures" in ms_src,
                         "调度器应含 r1 启动失败检测")
        self.assert_true("R1_START_TIMEOUT_HOURS = 24" in ms_src,
                         "r1 启动超时阈值应为 24h")

        # ── 13. v7.1.8: 新课题优先窗口逻辑（单元级）──────
        def _new_priority_split(pids, rounds_map, window=3):
            """复刻 _focus_proposal_for_slot 的优先窗口切分逻辑。"""
            new_pri, regular = [], []
            for pid in pids:
                if rounds_map.get(pid, 0) == 0:
                    new_pri.append(pid)
                else:
                    regular.append(pid)
            w = new_pri[:window]
            rest = new_pri[window:] + regular
            return w + rest

        # 3 个 r=0 课题插队到头部
        reordered = _new_priority_split(
            ["r3-a", "r3-b", "new-c", "r1-x", "new-a", "new-b"],
            {"r3-a": 3, "r3-b": 3, "new-c": 0, "r1-x": 1, "new-a": 0, "new-b": 0},
        )
        head = reordered[:3]
        self.assert_true(set(head) == {"new-c", "new-a", "new-b"},
                         f"新进 r=0 课题应优先 {head}")
        # window=3 限制，超过则加入 regular
        self.assert_true("r3-a" in reordered[3:], "rounds>0 课题排在优先窗口后")

        # 仅 1 个新进 + 全部 rounds>0 → 队列不变
        reordered2 = _new_priority_split(
            ["r3-a", "r3-b", "new-a"],
            {"r3-a": 3, "r3-b": 3, "new-a": 0},
        )
        self.assert_true(reordered2[0] == "new-a", "新进课题在头部")


def main() -> None:
    suite = PanelReviewRequestTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
