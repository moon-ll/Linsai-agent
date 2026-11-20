#!/usr/bin/env python3
"""test_human_queue_branch_masking.py — 人工队列分支掩蔽回归测试（v7.3.43）

BUG-45：human_queue.collect_human_queue 的 4 个 optimizing 分支
（outline_review / panel_review_requested / a_gate_panel_request /
negative_feedback_alert）共用同一条 if/elif 链，而 outline_review 的条件
（optimization_rounds>=1 and not outline_confirmed and not
outline_checkpoint_sent）对所有已完成课题恒真（生产 14 课题中 7 个
rounds>=1，outline_checkpoint_sent 全库为 None）→ outline_review 恒
优先命中 → 后三类分支永久不可达。v7.3.42 新增的 a_gate_panel_request
因此永远无法出现在人工队列里。

修复：outline_review 移出 elif 链改为独立判定，四类提醒可并存。

覆盖：
    1. a_gate 提醒不再被 outline_review 掩蔽
    2. panel_review_requested 不再被掩蔽
    3. negative_feedback_alert 不再被掩蔽
    4. outline_review 本身仍在（不回归丢失）
    5. outline_confirmed=True → outline_review 消失，a_gate 保留
    6. outline_checkpoint_sent=True → outline_review 消失，a_gate 保留
    7. rounds=0 → 无 outline_review（仅 a_gate）
    8. summary 计数与 items 一致
    9. drafts 状态不受影响

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_human_queue_branch_masking.py
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from human_queue import collect_human_queue  # noqa: E402
from test_runner import TestSuite  # noqa: E402

_AG = {
    "module": "references",
    "score": 0.89,
    "round": 2,
    "report_path": "05_review/critic-round-2-references.md",
    "created_at": "2026-11-05T12:30:00Z",
}


def _opt(**over):
    """构造一个 optimizing 课题状态（默认 rounds=2 且未发过大纲检查点）。"""
    ps = {
        "status": "optimizing",
        "title": "掩蔽回归课题",
        "optimization_rounds": 2,
        "outline_checkpoint_sent": None,
        "outline_confirmed": None,
        "panel_review_requested": False,
        "a_gate_panel_request": None,
        "negative_feedback_alert": False,
        "updated_at": "2026-11-05T12:00:00Z",
    }
    ps.update(over)
    return ps


def _types(proposals):
    res = collect_human_queue(proposals=proposals)
    return res, sorted(i["type"] for i in res["items"] if i.get("proposal_id") == "p1")


class HumanQueueBranchMaskingTests(TestSuite):
    def __init__(self):
        super().__init__("人工队列分支掩蔽回归（v7.3.43 / BUG-45）")

    def run_tests(self):
        self._a_gate_not_masked()
        self._panel_not_masked()
        self._negative_feedback_not_masked()
        self._outline_still_present()
        self._confirmed_suppresses_outline_only()
        self._checkpoint_sent_suppresses_outline_only()
        self._rounds_zero_no_outline()
        self._summary_consistent()
        self._drafts_unaffected()

    def _a_gate_not_masked(self):
        """BUG-45 主场景：a_gate 提醒必须能进队列（不被 outline_review 吃掉）"""
        res, types = _types({"p1": _opt(a_gate_panel_request=dict(_AG))})
        self.assert_in("panel_request", types,
                       "a_gate_panel_request 应产出 panel_request 条目")
        a_items = [i for i in res["items"] if i.get("source") == "a_gate"]
        self.assert_eq(len(a_items), 1, "a_gate 来源条目应恰好 1 条")
        if a_items:
            self.assert_eq(a_items[0]["hit_module"], "references", "命中模块应写入")
            self.assert_eq(a_items[0]["hit_score"], 0.89, "命中分数应写入")

    def _panel_not_masked(self):
        """平台期 panel_review_requested 不再被 outline_review 掩蔽"""
        _, types = _types({"p1": _opt(panel_review_requested=True)})
        self.assert_in("panel_request", types,
                       "平台期课题应产出 panel_request 条目")

    def _negative_feedback_not_masked(self):
        """负反馈提醒不再被 outline_review 掩蔽"""
        ps = _opt(negative_feedback_alert=True,
                  negative_feedback_auto_clear_count=1,
                  negative_feedback_at="2026-11-05T12:00:00Z",
                  negative_feedback_reasons=["跨章口径不一致"])
        _, types = _types({"p1": ps})
        self.assert_in("negative_feedback", types,
                       "负反馈告警应产出 negative_feedback 条目")

    def _outline_still_present(self):
        """修复不能把 outline_review 本身弄丢"""
        _, types = _types({"p1": _opt()})
        self.assert_in("outline_review", types,
                       "首轮完成且未确认时仍应出现 outline_review")

    def _confirmed_suppresses_outline_only(self):
        """outline_confirmed=True → 大纲条目消失，a_gate 保留"""
        _, types = _types({"p1": _opt(outline_confirmed=True,
                                      a_gate_panel_request=dict(_AG))})
        self.assert_true("outline_review" not in types,
                         "outline_confirmed=True 不应再出 outline_review")
        self.assert_in("panel_request", types, "a_gate 提醒应保留")

    def _checkpoint_sent_suppresses_outline_only(self):
        """outline_checkpoint_sent=True → 大纲条目消失，a_gate 保留"""
        _, types = _types({"p1": _opt(outline_checkpoint_sent=True,
                                      a_gate_panel_request=dict(_AG))})
        self.assert_true("outline_review" not in types,
                         "已发过大纲检查点不应再出 outline_review")
        self.assert_in("panel_request", types, "a_gate 提醒应保留")

    def _rounds_zero_no_outline(self):
        """rounds=0 → 无 outline_review（a_gate 仍可独立入队）"""
        _, types = _types({"p1": _opt(optimization_rounds=0,
                                      a_gate_panel_request=dict(_AG))})
        self.assert_true("outline_review" not in types,
                         "未完成首轮不应出 outline_review")
        self.assert_in("panel_request", types, "a_gate 提醒应保留")

    def _summary_consistent(self):
        """summary 计数与 items 一致（多类型并存时计数不得漏）"""
        res, types = _types({"p1": _opt(a_gate_panel_request=dict(_AG))})
        self.assert_eq(res["summary"]["outline_review"],
                       types.count("outline_review"), "outline_review 计数一致")
        self.assert_eq(res["summary"]["panel_request"],
                       types.count("panel_request"), "panel_request 计数一致")
        self.assert_eq(res["summary"]["total"], len(res["items"]),
                       "total 应等于 items 长度")

    def _drafts_unaffected(self):
        """drafts 分支不受本次改动影响"""
        res, types = _types({"p1": {
            "status": "drafts", "title": "草案课题",
            "created_at": "2026-11-05T12:00:00Z",
        }})
        self.assert_in("activate", types, "drafts 课题仍应出 activate 条目")
        self.assert_true("outline_review" not in types,
                         "drafts 不应出 outline_review")


if __name__ == "__main__":
    suite = HumanQueueBranchMaskingTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    s = suite.summary()
    print(f"{s['name']}：通过 {s['passed']}/{s['total']}")
    for r in s["results"]:
        if not r.passed:
            print(f"  ✗ {r.name} | {r.msg}")
