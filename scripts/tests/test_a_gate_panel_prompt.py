#!/usr/bin/env python3
"""test_a_gate_panel_prompt.py — A 通道析取提醒测试（v7.3.42）

用户裁决：A 不再要求"5 模块全高"。任一模块判定分 ≥0.85 且该册无未解决
critical/high → 写一条"建议专家评审"提醒；不晋级、不改 lifecycle 状态、
不影响 B 通道。开关 LINSAI_A_GATE_PANEL_PROMPT 默认 on。

覆盖：
    1. 命中 → 队列字段写入（模块 + 分数 + 报告路径）
    2. 有 critical → 不提示
    3. 有 high → 不提示
    4. 无模块 ≥0.85 → 不提示
    5. 开关关闭 → 零写入
    6. 多模块达标 → 取最高分模块
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from proposal_lifecycle.a_gate import (  # noqa: E402
    PANEL_PROMPT_ENV,
    evaluate_panel_prompt,
    panel_prompt_enabled,
)
from proposal_lifecycle.completion import CompletionMixin  # noqa: E402
from test_runner import TestSuite  # noqa: E402

SECTIONS = ["rationale", "content", "scheme", "full_review", "references",
            "method_manual"]


def _state(scores, critical=()):
    hist = []
    for i, (sec, sc) in enumerate(scores.items(), start=1):
        hist.append({"round": 1, "focus_section": sec, "score": sc,
                     "caliber": "section_4d"})
    return {
        "status": "optimizing",
        "score_history": hist,
        "last_score": 0.86,
        "section_passes": {},
        "optimization_rounds": 1,
        "monitor_history": [],
        "open_critical_issues": list(critical),
    }


class _Stub(CompletionMixin):
    REQUIRED_SECTIONS = SECTIONS

    def __init__(self, state):
        self._state = state
        self.writes = 0

    def _get_proposal_state(self, pid):
        return self._state

    def _set_proposal_state(self, pid, st):
        self._state.update(st)
        self.writes += 1


class AGatePanelPromptTests(TestSuite):
    def __init__(self):
        super().__init__("A 通道析取提醒")

    def run_tests(self):
        self._switch_default()
        self._hit_writes_queue()
        self._critical_blocks()
        self._high_blocks()
        self._no_module_blocks()
        self._switch_off_zero_write()
        self._picks_highest_module()
        self._stale_request_withdrawn()
        self._valid_request_kept()

    def _stale_request_withdrawn(self):
        st = _state({"rationale": 0.80, "content": 0.78, "scheme": 0.77,
                     "full_review": 0.79, "references": 0.78,
                     "method_manual": 0.87})
        # 该模块后续一轮评审回落到 0.75，旧 0.87 提醒已失效
        st["score_history"].append({"round": 2, "focus_section": "method_manual",
                                    "score": 0.75, "caliber": "manual_2d"})
        st["a_gate_panel_request"] = {"module": "method_manual", "score": 0.87,
                                      "round": 1, "proposal_id": "p1"}
        _Stub(st)._check_done("p1", {"min_overall_score": 0.85})
        self.assert_eq(st.get("a_gate_panel_request"), None,
                       "条件失效（分数回落）应撤回陈旧提醒")

    def _valid_request_kept(self):
        st = _state({"rationale": 0.86, "content": 0.80, "scheme": 0.79,
                     "full_review": 0.81, "references": 0.80,
                     "method_manual": 0.78})
        _Stub(st)._check_done("p1", {"min_overall_score": 0.85})
        hint = st.get("a_gate_panel_request") or {}
        self.assert_eq(hint.get("module"), "rationale", "条件仍满足应保留提醒")
        self.assert_eq(hint.get("score"), 0.86, "提醒分数不应被改写")

    def _switch_default(self):
        self.assert_true(panel_prompt_enabled({}), "未设置开关应默认开启")
        self.assert_eq(panel_prompt_enabled({PANEL_PROMPT_ENV: "0"}), False,
                       "开关 0 应关闭")

    def _hit_writes_queue(self):
        st = _state({"rationale": 0.86, "content": 0.80, "scheme": 0.79,
                     "full_review": 0.81, "references": 0.80,
                     "method_manual": 0.78})
        stub = _Stub(st)
        res = stub._check_done("p1", {"min_overall_score": 0.85})
        hint = st.get("a_gate_panel_request") or {}
        self.assert_eq(hint.get("module"), "rationale", "命中模块应写入队列")
        self.assert_eq(hint.get("score"), 0.86, "命中分数应写入队列")
        self.assert_true(bool(hint.get("report_path")), "队列条目应指向评审报告路径")
        self.assert_true(not res.get("done"), "A 通道不再自动晋级")
        self.assert_true(stub.writes >= 1, "命中应落盘一次")

    def _critical_blocks(self):
        st = _state({"rationale": 0.88, "content": 0.81, "scheme": 0.80,
                     "full_review": 0.82, "references": 0.80,
                     "method_manual": 0.79},
                    critical=[{"severity": "critical", "round_resolved": None}])
        self.assert_eq(evaluate_panel_prompt(st, SECTIONS, enabled=True), None,
                       "有 critical 不应提示")
        _Stub(st)._check_done("p1", {"min_overall_score": 0.85})
        self.assert_eq(st.get("a_gate_panel_request"), None,
                       "有 critical 不应写入队列")

    def _high_blocks(self):
        st = _state({"rationale": 0.90, "content": 0.81, "scheme": 0.80,
                     "full_review": 0.82, "references": 0.80,
                     "method_manual": 0.79},
                    critical=[{"severity": "high", "round_resolved": None}])
        self.assert_eq(evaluate_panel_prompt(st, SECTIONS, enabled=True), None,
                       "有 high 不应提示")

    def _no_module_blocks(self):
        st = _state({"rationale": 0.84, "content": 0.80, "scheme": 0.79,
                     "full_review": 0.81, "references": 0.80,
                     "method_manual": 0.78})
        self.assert_eq(evaluate_panel_prompt(st, SECTIONS, enabled=True), None,
                       "无模块 ≥0.85 不应提示")

    def _switch_off_zero_write(self):
        st = _state({"rationale": 0.90, "content": 0.81, "scheme": 0.80,
                     "full_review": 0.82, "references": 0.80,
                     "method_manual": 0.79})
        old = os.environ.get(PANEL_PROMPT_ENV)
        os.environ[PANEL_PROMPT_ENV] = "0"
        try:
            _Stub(st)._check_done("p1", {"min_overall_score": 0.85})
        finally:
            if old is None:
                os.environ.pop(PANEL_PROMPT_ENV, None)
            else:
                os.environ[PANEL_PROMPT_ENV] = old
        self.assert_eq(st.get("a_gate_panel_request"), None,
                       "开关关闭应零写入")

    def _picks_highest_module(self):
        st = _state({"rationale": 0.86, "content": 0.89, "scheme": 0.80,
                     "full_review": 0.82, "references": 0.80,
                     "method_manual": 0.79})
        hint = evaluate_panel_prompt(st, SECTIONS, enabled=True)
        self.assert_eq(hint.get("module"), "content", "应取最高分模块")


if __name__ == "__main__":
    suite = AGatePanelPromptTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    s = suite.summary()
    print(f"{s['name']}：通过 {s['passed']}/{s['total']}")
    for r in s["results"]:
        if not r.passed:
            print(f"  ✗ {r.name} | {r.msg}")
