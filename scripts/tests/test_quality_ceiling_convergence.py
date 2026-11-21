#!/usr/bin/env python3
"""
test_quality_ceiling_convergence.py — 质量天花板收敛检测回归测试（v6.9.16 / v6.9.27）

覆盖 _check_done 收敛/下降分支的边界：
    1. 稳定收敛：窗口内 4 轮全部 ≥0.85 且每轮提升 <2% → done=True（晋级）
    2. 骤降防误晋级：前 3 轮 ≥0.85 但当前轮骤降（0.88→0.18 类伪分数污染）
       → 不得按"质量收敛"晋级 pending_review（v6.9.16 修复点）
    3. 小幅跌破：前 3 轮 ≥0.85、当前轮 0.84 → 不触发收敛
    4. 连续 3 轮下降 → 走下降分支 done=True + 暂停警告（不被收敛分支截胡）

v6.9.27：收敛线随达标线整体上调（0.80→0.85），测试数据同步上移。

触发场景来源：2026-08-16 04h 体检发现 general-quantum-geometry 尾部
[0.84, 0.86, 0.85, 0.77] 距误晋级仅差一个浮点步长（0.86-0.84=0.020000…
不满足 <0.02），且 key-transient 尾部 4×0.81 已满足收敛条件待轮末触发。

注意：
    本测试不调用 hermes/LLM，仅验证达标判定的数据逻辑。

用法示例：
    python3 scripts/tests/test_quality_ceiling_convergence.py
"""

import copy
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

        # 最小实例：mock 状态读写，不触发 LLM / 日志。
        # v6.9.59 修复回归：mock 升级为生产语义——_get_proposal_state
        # 每次从"磁盘"新读（common.load_json 无缓存、返回新 dict），
        # _set_proposal_state 才落盘。此前 mock 返回同一 dict 引用，
        # 恰好掩盖了次优平台 quality_warning not-done 路径不落盘的丢写
        # 缺陷（v6.9.57 引入，v6.9.59 修复）。
        class _StateHolder:
            def __init__(self):
                self._disk = {}
                self.set_calls = []

            def _get_proposal_state(self, proposal_id):
                return copy.deepcopy(self._disk.get(proposal_id))

            def _set_proposal_state(self, proposal_id, state):
                self._disk[proposal_id] = copy.deepcopy(state)
                self.set_calls.append(proposal_id)
                return True

        class _FakeComp(CompletionMixin, _StateHolder):
            def __init__(self):
                _StateHolder.__init__(self)

        self._comp = _FakeComp()

    def teardown(self):
        pass

    def run_tests(self):
        comp = self._comp
        threshold = {"min_overall_score": 0.85}
        sections = ["rationale", "content", "scheme", "full_review", "references"]

        def _state(scores):
            comp._set_proposal_state("p1", {
                "status": "optimizing",
                "score_history": [{"score": s} for s in scores],
                "last_score": scores[-1],
                "section_passes": {k: False for k in sections},
                "optimization_rounds": len(scores),
                "monitor_history": [],
                "open_critical_issues": [],
            })

        # ---------- 1. 稳定收敛：4×0.86 平台 → 降级为人工信号（v6.10.3 F3） ----------
        # 用户裁决 2026-09-09：晋级条件偏松，收敛通道不再作为自动晋级口。
        # 修复前 done=True 自动晋级；修复后只挂 quality_warning（含"质量收敛"）
        # 并显式落盘，落穿到后续路径（本序列无提升/下降/最大轮数均不满足
        # → done=False，继续优化等待人工评估）。
        _state([0.83, 0.86, 0.86, 0.86, 0.86])
        res = comp._check_done("p1", threshold)
        self.assert_eq(res["done"], False, "收敛平台不再自动晋级（人工验收为主）")
        self.assert_in("p1", comp.set_calls, "收敛警告应显式落盘")
        conv_warned = comp._get_proposal_state("p1").get("quality_warning") or ""
        self.assert_in("质量收敛", conv_warned, "收敛应写 quality_warning 供人工评估")
        self.assert_in("人工评估", conv_warned, "warning 应建议人工评估")

        # ---------- 2. 骤降防误晋级（v6.9.16 修复点） ----------
        # 前 3 轮 [0.86, 0.87, 0.88] ≥0.85 且相邻提升均 <2%，当前轮 0.18
        # （伪分数污染/真实回退）→ 修复前会以"质量收敛"晋级，修复后继续优化
        _state([0.78, 0.86, 0.87, 0.88, 0.18])
        res2 = comp._check_done("p1", threshold)
        self.assert_eq(res2["done"], False, "3 轮高位后当前轮骤降 → 不按收敛晋级")

        # ---------- 3. 小幅跌破：当前轮 0.84 → 不触发收敛 ----------
        _state([0.78, 0.86, 0.87, 0.86, 0.84])
        res3 = comp._check_done("p1", threshold)
        self.assert_eq(res3["done"], False, "当前轮跌破 0.85 → 不触发收敛")

        # ---------- 4. 连续 3 轮下降 → 下降分支暂停（不被收敛截胡） ----------
        # 修复前该序列命中收敛分支（前 3 轮 ≥0.85 且 deltas 全 <2%），
        # 修复后落入下降分支：done=True + 暂停语义 + 质量警告
        _state([0.90, 0.89, 0.88, 0.87, 0.60])
        res4 = comp._check_done("p1", threshold)
        self.assert_eq(res4["done"], True, "连续 3 轮下降 → 触发暂停")
        self.assert_in("质量下降", res4.get("quality_warning") or "", "下降分支附质量警告")
        self.assert_in("暂停", res4["reason"], "下降分支 reason 为暂停语义")

        # ---------- 5. 次优平台（v6.9.57）：0.80-0.85 平台 → 不晋级 +
        # quality_warning 写入 state 供人工评估 ----------
        # 背景：收敛线 0.85 与程序化天花板（AI 检测 cap 0.85 / 锚点差距明显
        # cap 0.84）结构性冲突，全量 32 轮实测 max 0.81，收敛分支零触发。
        _state([0.79, 0.81, 0.82, 0.82, 0.82])
        res5 = comp._check_done("p1", threshold)
        self.assert_eq(res5["done"], False, "0.80-0.85 平台不自动晋级（人工验收为主）")
        # v6.9.59 修复回归：not-done 路径必须显式落盘——mock 为磁盘新读
        # 语义后，重读可见才算真正写入（修复前只改内存副本即丢失）。
        self.assert_in(
            "p1", comp.set_calls, "次优平台警告应显式落盘（not-done 路径）")
        warned = comp._get_proposal_state("p1").get("quality_warning") or ""
        self.assert_in("次优平台", warned, "次优平台应写 quality_warning 供人工评估")
        self.assert_in("人工评估", warned, "warning 应建议人工评估")

        # ---------- 6. 次优平台不误伤：窗口含 <0.80 轮次 → 不标记 ----------
        _state([0.78, 0.82, 0.82, 0.82])
        st6 = comp._get_proposal_state("p1")
        st6["quality_warning"] = None
        comp._set_proposal_state("p1", st6)
        comp._check_done("p1", threshold)
        warned6 = comp._get_proposal_state("p1").get("quality_warning") or ""
        self.assert_true(
            "次优平台" not in warned6,
            "窗口内有 <0.80 轮次（还在正常爬升通道）不应标记次优平台")

        # ---------- 7. references 异口径不触发虚假下降（v6.9.78） ----------
        # 背景：references 轮为 2 维专用口径（rigor/completeness 均值），
        # 与章节 4 维加权分不可比。实测 bsv pass4：0.75→0.67→0.66→0.50[refs]
        # 被误判"连续3轮质量下降"暂停流转（0.50 还是解析缺陷产物，真实 0.78）。
        # 修复后 references 条目不参与连续性窗口。
        _state([0.75, 0.67, 0.66, 0.50])
        st7 = comp._get_proposal_state("p1")
        st7["score_history"] = [
            {"score": 0.75, "focus_section": "content"},
            {"score": 0.67, "focus_section": "scheme"},
            {"score": 0.66, "focus_section": "full_review"},
            {"score": 0.50, "focus_section": "references"},
        ]
        st7["last_score"] = 0.50
        comp._set_proposal_state("p1", st7)
        res7 = comp._check_done("p1", threshold)
        self.assert_eq(
            res7["done"], False,
            "references 异口径低分不应构成连续下降（bsv 实测误暂停场景）")

        # 7.2 对照组：同为章节口径的真实连续下降仍应触发暂停
        _state([0.75, 0.67, 0.66, 0.60])
        st72 = comp._get_proposal_state("p1")
        st72["score_history"] = [
            {"score": 0.75, "focus_section": "content"},
            {"score": 0.67, "focus_section": "scheme"},
            {"score": 0.66, "focus_section": "full_review"},
            {"score": 0.60, "focus_section": "rationale"},
        ]
        comp._set_proposal_state("p1", st72)
        res72 = comp._check_done("p1", threshold)
        self.assert_eq(
            res72["done"], True,
            "章节口径连续 3 轮下降仍应触发暂停（修复不放松真实检测）")


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
