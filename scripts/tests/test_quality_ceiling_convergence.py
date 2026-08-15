#!/usr/bin/env python3
"""
test_quality_ceiling_convergence.py — 质量天花板收敛检测回归测试（v6.9.16）

覆盖 _check_done 收敛/下降分支的边界：
    1. 稳定收敛：窗口内 4 轮全部 ≥0.80 且每轮提升 <2% → done=True（晋级）
    2. 骤降防误晋级：前 3 轮 ≥0.80 但当前轮骤降（0.85→0.18 类伪分数污染）
       → 不得按"质量收敛"晋级 pending_review（v6.9.16 修复点）
    3. 小幅跌破：前 3 轮 ≥0.80、当前轮 0.79 → 不触发收敛
    4. 连续 3 轮下降 → 走下降分支 done=True + 暂停警告（不被收敛分支截胡）

触发场景来源：2026-08-16 04h 体检发现 general-quantum-geometry 尾部
[0.84, 0.86, 0.85, 0.77] 距误晋级仅差一个浮点步长（0.86-0.84=0.020000…
不满足 <0.02），且 key-transient 尾部 4×0.81 已满足收敛条件待轮末触发。

注意：
    本测试不调用 hermes/LLM，仅验证达标判定的数据逻辑。

用法示例：
    python3 scripts/tests/test_quality_ceiling_convergence.py
"""

import sys
import importlib

from test_runner import TestSuite, create_isolated_env


class QualityCeilingConvergenceTests(TestSuite):
    def __init__(self):
        super().__init__("质量天花板收敛检测测试")
        self.tmp_root = None
        self._comp = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in [
            "proposal_lifecycle.completion",
            "proposal_lifecycle",
            "proposal_sections",
        ]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.completion")
        from proposal_lifecycle.completion import CompletionMixin

        # 最小实例：mock 状态读写，不触发 LLM / 日志
        class _StateHolder:
            def __init__(self):
                self._state = {}

            def _get_proposal_state(self, proposal_id):
                return self._state

            def _set_proposal_state(self, proposal_id, state):
                self._state = state
                return True

        class _FakeComp(CompletionMixin, _StateHolder):
            def __init__(self):
                _StateHolder.__init__(self)

        self._comp = _FakeComp()

    def teardown(self):
        pass

    def run_tests(self):
        comp = self._comp
        threshold = {"min_overall_score": 0.80}
        sections = ["rationale", "content", "scheme", "full_review", "references"]

        def _state(scores):
            comp._state = {
                "status": "optimizing",
                "score_history": [{"score": s} for s in scores],
                "last_score": scores[-1],
                "section_passes": {k: False for k in sections},
                "optimization_rounds": len(scores),
                "monitor_history": [],
                "open_critical_issues": [],
            }

        # ---------- 1. 稳定收敛：4×0.81 平台 → done=True ----------
        _state([0.78, 0.81, 0.81, 0.81, 0.81])
        res = comp._check_done("p1", threshold)
        self.assert_eq(res["done"], True, "窗口内 4 轮全 ≥0.80 且提升 <2% → 收敛晋级")
        self.assert_in("质量收敛", res["reason"], "收敛晋级 reason 标注质量收敛")

        # ---------- 2. 骤降防误晋级（v6.9.16 修复点） ----------
        # 前 3 轮 [0.83, 0.84, 0.85] ≥0.80 且相邻提升均 <2%，当前轮 0.18
        # （伪分数污染/真实回退）→ 修复前会以"质量收敛"晋级，修复后继续优化
        _state([0.75, 0.83, 0.84, 0.85, 0.18])
        res2 = comp._check_done("p1", threshold)
        self.assert_eq(res2["done"], False, "3 轮高位后当前轮骤降 → 不按收敛晋级")

        # ---------- 3. 小幅跌破：当前轮 0.79 → 不触发收敛 ----------
        _state([0.75, 0.82, 0.83, 0.82, 0.79])
        res3 = comp._check_done("p1", threshold)
        self.assert_eq(res3["done"], False, "当前轮跌破 0.80 → 不触发收敛")

        # ---------- 4. 连续 3 轮下降 → 下降分支暂停（不被收敛截胡） ----------
        # 修复前该序列命中收敛分支（前 3 轮 ≥0.80 且 deltas 全 <2%），
        # 修复后落入下降分支：done=True + 暂停语义 + 质量警告
        _state([0.85, 0.84, 0.82, 0.60])
        res4 = comp._check_done("p1", threshold)
        self.assert_eq(res4["done"], True, "连续 3 轮下降 → 触发暂停")
        self.assert_in("质量下降", res4.get("quality_warning") or "", "下降分支附质量警告")
        self.assert_in("暂停", res4["reason"], "下降分支 reason 为暂停语义")


if __name__ == "__main__":
    import time
    suite = QualityCeilingConvergenceTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report
    print_report([suite])
