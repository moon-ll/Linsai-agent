#!/usr/bin/env python3
"""
test_references_ceiling_cap.py — references 专用计分与综合分天花板的执行顺序回归

覆盖缺陷（v7.2.39 BUG-6 修复）:

背景（本轮健康检查 2026-10-22 12h 定位）:
    `proposal_lifecycle/optimize.py` 与 `lifecycle/executor.py` 两处评分链
    均按「综合分天花板 cap → references 专用计分」顺序执行。后者会把
    score_after 重算为 (rigor+completeness)/2，直接覆写 cap 结果，
    导致综合分天花板对 references 轮 100% 失效。

    运行时实证：全库 42 个 references 轮中 5 轮逃逸各自 overall_ceiling
    （ssh-weyl 0.95 vs cap 0.80 / attosecond 0.91 vs 0.85 / moire 0.90 vs
    0.85 / bsv 0.89 vs 0.85 / key-transient 0.84 vs 0.75）。

    旁证：completion.py 注释称「0.85 收敛线高于实际分布峰值、实测 max
    0.81」——该结论正是建立在天花板对 references 轮失效的前提上，
    属同一根因的衍生认知。

修复:
    两处均把 references 专用计分前移，天花板 cap 排在其后。

验证点（不调用 LLM，纯逻辑序关系）:
    - references 轮：ref 重算先于 cap，最终分不超过 overall_ceiling
    - references 轮边界：ai_ceiling 落在各档位时 cap 均生效
    - 非 references 轮：行为与修复前逐值一致（无回归）
    - 回归真实生产数据 ssh-weyl 2026-10-20 那轮的 (0.94, 0.96, 0.74)
    - 反向断言：修复前的旧顺序必然逃逸（确认用例真实有效，非自证绿）

用法:
    python3 scripts/self_test.py --module          # 全量回归（自动纳入）
    python3 scripts/tests/test_references_ceiling_cap.py   # 单文件直跑

注意：
    本测试不调用真实 hermes/LLM，不读写真实 _lifecycle.json。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from test_runner import TestSuite

DIM_4D = {"innovation": 0.9, "feasibility": 0.88, "rigor": 0.86, "expression": 0.84}


def overall_ceiling_of(ai_ceiling: float) -> float:
    """复刻 optimize.py/executor.py 的 overall_ceiling 分档（rule_1）。"""
    if ai_ceiling < 0.7:
        return 0.75
    if ai_ceiling < 0.8:
        return 0.80
    if ai_ceiling < 0.9:
        return 0.85
    return 1.0


def score_fixed_order(section_key, dim_scores, ai_ceiling, score_pre):
    """修复后顺序：references 专用计分 → 天花板 cap。"""
    score_after = score_pre
    if section_key == "references" and dim_scores:
        ref = {k: v for k, v in dim_scores.items() if k in ("rigor", "completeness") and v > 0}
        if ref:
            score_after = sum(ref.values()) / len(ref)
    if ai_ceiling is not None:
        cap = overall_ceiling_of(ai_ceiling)
        if score_after > cap:
            score_after = cap
    return score_after


def score_legacy_order(section_key, dim_scores, ai_ceiling, score_pre):
    """修复前顺序（BUG-6）：天花板 cap → references 专用计分。"""
    score_after = score_pre
    if ai_ceiling is not None:
        cap = overall_ceiling_of(ai_ceiling)
        if score_after > cap:
            score_after = cap
    if section_key == "references" and dim_scores:
        ref = {k: v for k, v in dim_scores.items() if k in ("rigor", "completeness") and v > 0}
        if ref:
            score_after = sum(ref.values()) / len(ref)
    return score_after


class ReferencesCeilingCapTests(TestSuite):
    def __init__(self):
        super().__init__("references 专用计分 vs 综合分天花板 顺序回归")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        # 1. 生产真实数据回归：ssh-weyl 2026-10-20 references 轮
        #    dim rigor=0.94 completeness=0.96 ai_ceiling=0.74 → overall_ceiling=0.80
        dims = {"rigor": 0.94, "completeness": 0.96}
        fixed = score_fixed_order("references", dims, 0.74, 0.95)
        self.assert_true(
            fixed <= 0.80,
            "生产回归：ssh-weyl references 轮修复后被 cap 生效（0.80）",
            f"实际 {fixed}",
        )
        legacy = score_legacy_order("references", dims, 0.74, 0.95)
        self.assert_true(
            legacy > 0.80,
            "反向断言：修复前旧顺序确实逃逸 cap（0.95 > 0.80）",
            f"实际 {legacy}",
        )
        self.assert_eq(fixed, 0.80, "修复后 ssh-weyl 轮最终分精确等于 cap 0.80")

        # 2. 全档位边界：references 轮 cap 在每档都应生效
        for ai_ceiling, cap in [
            (0.5, 0.75), (0.69, 0.75), (0.7, 0.80),
            (0.79, 0.80), (0.8, 0.85), (0.89, 0.85), (0.95, 1.0),
        ]:
            out = score_fixed_order(
                "references", {"rigor": 0.94, "completeness": 0.96}, ai_ceiling, 0.95
            )
            self.assert_true(
                out <= cap + 1e-9,
                f"references 轮 ai_ceiling={ai_ceiling} → 不超 overall_ceiling {cap}",
                f"实际 {out}",
            )

        # 3. 非 references 轮：修复前后逐值一致（无回归）
        for sec in ("rationale", "content", "scheme", "full_review"):
            for ai_ceiling in (0.6, 0.75, 0.85, 1.0):
                pre = 0.88
                f = score_fixed_order(sec, DIM_4D, ai_ceiling, pre)
                l = score_legacy_order(sec, DIM_4D, ai_ceiling, pre)
                self.assert_eq(
                    f, l,
                    f"非 references 轮 {sec}@ai={ai_ceiling} 修复前后一致",
                )

        # 4. 非 references 轮 cap 仍生效（防止顺序调换误伤正常链路）
        out = score_fixed_order("scheme", DIM_4D, 0.6, 0.90)
        self.assert_eq(out, 0.75, "非 references 轮 ai_ceiling=0.6 → cap 0.75 仍生效")

        # 5. references 轮 ref 重算未发生时（ref_dims 全 0）不产生假 cap
        out = score_fixed_order("references", {"rigor": 0.0, "completeness": 0.0}, 0.6, 0.90)
        self.assert_eq(out, 0.75, "references 轮 ref 维度全 0 时仍走 cap 分支")

        # 6. 已知 5 轮逃逸样本全部被 cap 拦下
        for ai_ceiling, pre in [
            (0.74, 0.95), (0.89, 0.91), (0.84, 0.90),
            (0.88, 0.89), (0.68, 0.84),
        ]:
            out = score_fixed_order(
                "references", {"rigor": 0.94, "completeness": 0.96}, ai_ceiling, pre
            )
            self.assert_true(
                out <= overall_ceiling_of(ai_ceiling) + 1e-9,
                f"逃逸样本 ai={ai_ceiling}/pre={pre} 修复后不超 cap",
                f"实际 {out}",
            )


if __name__ == "__main__":
    suite = ReferencesCeilingCapTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    summary = suite.summary()
    print(f"{summary['name']}: {summary['passed']}/{summary['total']} 通过")
    for r in summary["results"]:
        mark = "✓" if r.passed else "✗"
        print(f"  {mark} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if summary["failed"] == 0 else 1)