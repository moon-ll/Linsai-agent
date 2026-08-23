#!/usr/bin/env python3
"""
test_pass_history.py — 遍次隔离与退回对比报告回归测试（v6.9.41）

覆盖两个修复点：
    1. P0: 审核退回时 score_history 按遍次归档（transitions.py 集成守卫）
       - 退回分支必须调用 archive_pass_history（源码级守卫）
       - 归档/切分/FIFO 细节由模块自检覆盖，此处测 transitions 集成数据流
    2. P1: 退回对比报告（generate_return_comparison）
       - 两遍数据 → 生成含轨迹/天花板/卡点对比的报告
       - 只有一遍 → 不生成（返回 None）
       - 天花板未动 + 通过无增长 + 卡点未变 → 输出"未产生边际效果"诊断

背景：退回清零 rounds/job 但不清 score_history，多遍数据混叠（08-23
实测 5 个课题 2-4 个历史遍混在同一数组），轨迹分析全建立在污染数据上。
数据迁移后真相：四课题均触顶 0.84-0.86 被否决，第 2/3 遍天花板完全相同
——反馈注入零边际效果的实证。

用法示例：
    python3 scripts/tests/test_pass_history.py
"""

import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test_runner import TestSuite

from proposal_lifecycle.pass_history import (
    archive_pass_history,
    generate_return_comparison,
    migrate_overlaid_history,
)


def _entry(round_no, score, at, weakest=None, passed=False, section=None):
    e = {"round": round_no, "score": score, "at": at}
    if weakest:
        e["weakest_dim"] = weakest
    if section:
        e["focus_section"] = section
        e["section_passed"] = passed
    return e


class PassHistoryTests(TestSuite):
    """1：遍次归档 + 对比报告 + 迁移。"""

    def __init__(self):
        super().__init__("遍次隔离与退回对比测试（v6.9.41）")
        self.tmp = None

    def setup(self):
        self.tmp = Path(tempfile.mkdtemp())

    def teardown(self):
        if self.tmp and self.tmp.exists():
            shutil.rmtree(self.tmp, ignore_errors=True)

    def run_tests(self):
        # ================================================================
        # 1.1 退回→归档→再退回：两遍数据完整隔离
        # ================================================================
        st = {"pass_number": 1, "score_history": [
            _entry(1, 0.7, "2026-08-01T00:00:00Z", weakest="novelty"),
            _entry(2, 0.8, "2026-08-02T00:00:00Z", weakest="novelty", passed=True, section="rationale"),
        ]}
        n1 = archive_pass_history(st, reason="满8轮")
        self.assert_eq(n1, 2, "第一遍归档 2 条")

        # 第二遍跑出 2 条后又被退回
        st["score_history"] = [
            _entry(1, 0.75, "2026-08-20T00:00:00Z", weakest="novelty"),
            _entry(2, 0.8, "2026-08-21T00:00:00Z", weakest="rigor"),
        ]
        n2 = archive_pass_history(st, reason="人工审核退回(major_revision)")
        self.assert_eq(n2, 2, "第二遍归档 2 条")
        self.assert_eq(st["pass_number"], 3, "退回两次后开启第 3 遍")
        self.assert_eq(len(st["score_history_archive"]), 2, "归档两遍")
        self.assert_eq(st["score_history"], [], "当前历史已清空")

        # ================================================================
        # 1.2 对比报告：两遍数据 → 生成并含关键判定
        # ================================================================
        report = generate_return_comparison("test-prop", st, self.tmp)
        self.assert_true(report is not None, "有上一遍时应生成报告")
        content = Path(report).read_text(encoding="utf-8")
        self.assert_true("第 2 遍 vs 第 1 遍" in content, "报告标题含遍次对比")
        self.assert_true("r1:0.75 → r2:0.80" in content, "本遍轨迹正确")
        self.assert_true("0.80 → 0.80（未移动）" in content, "天花板对比正确")
        self.assert_true("novelty" in content, "卡点维度出现在报告")
        self.assert_true("对抗通过数无增长" in content, "通过无增长的判定输出")

        # ================================================================
        # 1.3 对比报告：天花板未动+卡点未变 → 边际效果诊断
        # ================================================================
        self.assert_true("未产生边际效果" in content,
                         "天花板未动+无增长+卡点未变应输出边际效果诊断")

        # ================================================================
        # 1.4 只有一遍 → 不生成报告
        # ================================================================
        st_one = {"pass_number": 2, "score_history": [],
                  "score_history_archive": [{"pass": 1, "returned_at": "t", "reason": "", "entries": [_entry(1, 0.7, "t")]}]}
        r_none = generate_return_comparison("test-prop", st_one, self.tmp)
        self.assert_true(r_none is None, "只有一遍历史时不应生成报告")

        # ================================================================
        # 1.5 迁移：退回时间切分混叠数据（存量修复语义）
        # ================================================================
        st_m = {
            "transition_history": [
                {"from": "optimizing", "to": "pending_review", "at": "2026-08-01T00:00:00Z", "reason": "满8轮"},
                {"from": "pending_review", "to": "optimizing", "at": "2026-08-02T00:00:00Z", "reason": "退回1"},
                {"from": "optimizing", "to": "pending_review", "at": "2026-08-10T00:00:00Z", "reason": "满8轮"},
                {"from": "pending_review", "to": "optimizing", "at": "2026-08-11T00:00:00Z", "reason": "退回2"},
            ],
            "score_history": [
                _entry(1, 0.7, "2026-07-28T00:00:00Z"),   # 第 1 遍
                _entry(1, 0.72, "2026-08-03T00:00:00Z"),   # 第 2 遍
                _entry(2, 0.86, "2026-08-08T00:00:00Z"),   # 第 2 遍
                _entry(1, 0.73, "2026-08-20T00:00:00Z"),   # 第 3 遍（当前）
            ],
        }
        n_m = migrate_overlaid_history(st_m)
        self.assert_eq(n_m, 2, "两个退回点切出 2 个历史遍")
        self.assert_eq(len(st_m["score_history"]), 1, "当前遍只剩 1 条")
        self.assert_eq(st_m["pass_number"], 3, "迁移后 pass_number=3")
        # 幂等
        self.assert_eq(migrate_overlaid_history(st_m), 0, "已迁移再次调用跳过")

        # ================================================================
        # 1.6 transitions.py 集成守卫：退回分支必须接线归档与报告
        # ================================================================
        src = Path(__file__).parent.parent / "proposal_lifecycle" / "transitions.py"
        text = src.read_text(encoding="utf-8")
        self.assert_true(
            "from proposal_lifecycle.pass_history import" in text,
            "退回分支应导入 pass_history",
        )
        self.assert_true(
            "archive_pass_history(prop_state, reason=reason)" in text,
            "退回时应调用 archive_pass_history",
        )
        self.assert_true(
            "generate_return_comparison(" in text,
            "退回时应调用对比报告生成",
        )
        # 归档调用必须在 _set_proposal_state 之前（状态落盘含归档结果）
        idx_archive = text.find("archive_pass_history(prop_state, reason=reason)")
        idx_save = text.find("self._set_proposal_state(proposal_id, prop_state)")
        self.assert_true(
            0 < idx_archive < idx_save,
            "归档须在状态落盘前执行（否则归档丢失）",
        )


def main():
    from test_runner import print_report

    suites = []
    for cls in (PassHistoryTests,):
        s = cls()
        s.setup()
        s.run_tests()
        s.teardown()
        suites.append(s)
    print_report(suites)


if __name__ == "__main__":
    main()
