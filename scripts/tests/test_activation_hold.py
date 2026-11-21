#!/usr/bin/env python3
"""test_activation_hold.py — 立项 hold 裁决闭环测试（v7.3.10）

背景：
    2026-11-03 用户裁决三个 ZCode 新课题草案（phonon-hhg / vortex-oam-hhg /
    chiral-hhg）全部 hold——8 个 optimizing 课题未满足双通道晋级且机时紧张。
    要求：hold 决定写回队列可查，但不再按 72h 催办；重评门（反思链验证 +
    质量回升）满足后才重新提交激活。

覆盖：
    1. hold 草案 → type=activate_hold，escalate 恒 False（即使等待 200h）
    2. 未裁决草案 → type=activate，超 72h 正常 escalate
    3. summary 分别计数 activate / activate_hold，escalated 只含后者
    4. hold 项携带裁决理由与两项重评门条件

注意：不读真实生命周期文件，proposals 注入；四类磁盘派生来源打空桩。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import human_queue  # noqa: E402
from test_runner import TestSuite  # noqa: E402


class ActivationHoldTests(TestSuite):
    def __init__(self):
        super().__init__("立项 hold 裁决闭环")
        self._orig = {}

    def setup(self):
        # 隔离磁盘派生来源，避免真实 weekend-input / 调度建议掺杂计数
        for fn_name in (
            "_pending_strategy_suggestions",
            "_pending_cluster_reviews",
            "_pending_input_broken",
            # v7.3.28: quota_review 持久源同样读生产文件，测试须打桩隔离
            "_pending_quota_reviews",
        ):
            self._orig[fn_name] = getattr(human_queue, fn_name)
            setattr(human_queue, fn_name, lambda now, *a, **k: [])

    def teardown(self):
        for fn_name, fn in self._orig.items():
            setattr(human_queue, fn_name, fn)
        self._orig = {}

    @staticmethod
    def _draft(**extra):
        p = {
            "title": "测试草案",
            "status": "drafts",
            "created_at": "2026-10-25T00:00:00Z",
            "idea_dossier": {"recommendation": "activate"},
        }
        p.update(extra)
        return p

    def run_tests(self):
        self._test_hold_draft_never_escalates()
        self._test_normal_draft_still_escalates()
        self._test_summary_counts_hold_separately()

    def _test_hold_draft_never_escalates(self):
        """已裁决 hold 的草案即使等待 200h 也不催办，且记录进入队列。"""
        proposals = {
            "p-hold": self._draft(
                activation_decision={
                    "decision": "hold",
                    "reason": "机时不足",
                    "reactivation_gate": {
                        "all_required": True,
                        "conditions": [
                            {"key": "reflection_chain_v7_2_107_verified", "status": "pending"},
                            {"key": "quality_recovery", "status": "pending"},
                        ],
                    },
                }
            )
        }
        result = human_queue.collect_human_queue(
            proposals=proposals, escalate_after_h=72
        )
        items = result["items"]
        self.assert_eq(len(items), 1, "hold 草案仍应保留一条可查记录")
        item = items[0]
        self.assert_eq(item["type"], "activate_hold", "类型应为 activate_hold")
        self.assert_true(item["waiting_hours"] >= 72, "夹具等待时长应超过催办线")
        self.assert_eq(item["escalate"], False, "hold 项不得催办")
        self.assert_eq(item["decision_reason"], "机时不足", "应携带裁决理由")
        self.assert_eq(
            len(item["reactivation_gate"]["conditions"]), 2, "应携带两项重评门"
        )

    def _test_normal_draft_still_escalates(self):
        """未裁决草案保持原行为：等待 80h 触发催办。"""
        proposals = {"p-new": self._draft()}
        result = human_queue.collect_human_queue(
            proposals=proposals, escalate_after_h=72
        )
        item = result["items"][0]
        self.assert_eq(item["type"], "activate", "未裁决草案类型不变")
        self.assert_eq(item["escalate"], True, "超过 72h 应催办")
        self.assert_eq(item["recommendation"], "activate", "预审建议应保留")

    def _test_summary_counts_hold_separately(self):
        """summary 分开计数，escalated 只含仍需人工的项。"""
        proposals = {
            "p-hold": self._draft(
                activation_decision={
                    "decision": "hold",
                    "reason": "r",
                    "reactivation_gate": {"conditions": []},
                }
            ),
            "p-new": self._draft(),
        }
        result = human_queue.collect_human_queue(
            proposals=proposals, escalate_after_h=72
        )
        s = result["summary"]
        self.assert_eq(s["total"], 2, "total 应含两类")
        self.assert_eq(s["activate"], 1, "activate 计数只含未裁决项")
        self.assert_eq(s["activate_hold"], 1, "activate_hold 单独计数")
        self.assert_eq(
            len([i for i in result["items"] if i.get("escalate")]), 1,
            "催办列表只应包含未裁决草案",
        )


if __name__ == "__main__":
    import time

    from test_runner import print_report

    suite = ActivationHoldTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    print_report([suite])
