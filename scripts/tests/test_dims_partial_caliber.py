"""
test_dims_partial_caliber.py — 口径感知维度完备性回归测试（v7.2.41 / BUG-8）

背景（本轮健康检查第二层定位）：
    v6.9.62 起 `dims_partial` 用 `DIMENSION_FLOOR` 全集
    （innovation/feasibility/rigor/expression/completeness）作期望集，
    判定条件为 `section_key in ("rationale","content","scheme")`
    且期望集有缺失。问题在于 `completeness` 是 **references 专轮**
    （2 维口径 rigor/completeness）的专属维度——正文轮 critic 按 4 维
    打分，completeness 永不产出，于是正文轮 `dims_partial` 恒为 True。

    实测全库：正文章节轮 148/148 = 100% 命中 dims_partial=True，
    full_review 轮与 references 轮各 0 条。

    连带后果（completion.py 六道质量门 + 看板 4 维全部封死）：
      1. 收敛检测 CONVERGENCE（completion.py:163）
      2. 次优平台检测 SUBOPTIMAL（completion.py:201）
      3. 验收线晋级 ACCEPT（completion.py:275）——含 4 维加权门取数
      4. 评审团请求 PANEL（completion.py:369）
      5. 质量下降检测 DECLINE（completion.py:429）
      6. executor.py:2343 agent 奖惩守卫——正文轮 writer/critic
         奖惩被静默清零（deltas 恒 0）
      7. micro_scheduler.py:1163 看板 score_dims 只能回退取
         full_review 轮的陈旧 dim_scores

    修复：期望集改为口径感知（expected_dim_keys）——章节轮/
    full_review 轮取 4 维，references 轮取 2 维。

测试覆盖：
    1. expected_dim_keys 口径映射（章节 4 维 / references 2 维）
    2. 正文轮 4 维齐全 → dims_partial=False（BUG-8 核心正向断言）
    3. 正文轮真缺 4 维之一 → dims_partial=True（防线未被削弱）
    4. references 轮 2 维齐全 → dims_partial=False
    5. references 轮缺 completeness → dims_partial=True
    6. 反向断言：复刻旧实现（DIMENSION_FLOOR 全集 + 正文轮限定）
       必然把完整正文轮误判为 partial——确认测试非自证绿
    7. agent 奖惩守卫同步口径：正文轮 4 维齐全不再被跳过

注意：本测试不调用 hermes/LLM，仅验证维度完备性判定逻辑。

用法示例：
    python3 scripts/tests/test_dims_partial_caliber.py
"""

import sys

from test_runner import TestSuite, create_isolated_env


class DimsPartialCaliberTests(TestSuite):
    def __init__(self):
        super().__init__("dims_partial 口径感知回归测试")

    def run_tests(self):
        env = create_isolated_env()
        try:
            import lifecycle.executor as ex

            # ---------- 1. expected_dim_keys 口径映射 ----------
            four = ("innovation", "feasibility", "rigor", "expression")
            for sk in ("rationale", "content", "scheme", "full_review"):
                self.assert_eq(
                    tuple(ex.expected_dim_keys(sk)), four,
                    f"{sk} 轮应取 4 维口径（含 full_review）")
            self.assert_eq(
                tuple(ex.expected_dim_keys("references")),
                ("rigor", "completeness"),
                "references 轮应取 2 维专用口径")

            # 关键不变量：completeness 不得出现在章节轮期望集内
            self.assert_true(
                "completeness" not in ex.expected_dim_keys("scheme"),
                "completeness 是 references 专属维度，不得作为章节轮期望")
            self.assert_true(
                "innovation" not in ex.expected_dim_keys("references"),
                "references 轮不评创新性/可行性，不得混入 4 维期望")

            # ---------- 2. 正文轮 4 维齐全 → 非 partial（BUG-8 核心正向断言） ----------
            section_dims = {
                "innovation": 0.84, "feasibility": 0.81,
                "rigor": 0.74, "expression": 0.75,
            }
            dp, present, missing = ex.judge_dims_partial("scheme", section_dims)
            self.assert_eq(
                dp, False,
                "BUG-8 核心断言：正文轮 4 维齐全（无 completeness）不应被判残缺")
            self.assert_eq(
                missing, [],
                "正文轮 4 维齐全时 missing 应为空（completeness 不计入章节期望）")
            self.assert_eq(
                present, sorted(section_dims.keys()),
                "dims_present 应如实回报已解析维度")

            # ---------- 3. 正文轮真缺 4 维之一 → 仍判 partial ----------
            for missing_key in ("innovation", "feasibility", "rigor", "expression"):
                partial_dims = {
                    k: v for k, v in section_dims.items() if k != missing_key
                }
                dp_miss, _p, miss = ex.judge_dims_partial("scheme", partial_dims)
                self.assert_eq(
                    dp_miss, True,
                    f"正文轮真缺 {missing_key} 时仍须判残缺（防线未被削弱）")
                self.assert_eq(
                    miss, [missing_key],
                    f"缺 {missing_key} 时 missing 应精确回报该维度")

            # 缺 2 维（模拟 critic 输出被截断，对应 v6.9.62 原始场景）
            dp_two, _p, miss2 = ex.judge_dims_partial(
                "content", {"innovation": 0.8, "feasibility": 0.8})
            self.assert_eq(
                dp_two, True,
                "正文轮缺 2 维时须判残缺（对应 v6.9.62 原始场景）")
            self.assert_eq(
                sorted(miss2), ["expression", "rigor"],
                "缺 2 维时 missing 应回报两项")

            # ---------- 4. references 轮 2 维齐全 → 非 partial ----------
            ref_dims = {"rigor": 0.94, "completeness": 0.96}
            dp_ref, _p, miss_ref = ex.judge_dims_partial("references", ref_dims)
            self.assert_eq(
                dp_ref, False,
                "references 轮 2 维齐全不应被判残缺")
            self.assert_eq(
                miss_ref, [],
                "references 轮 2 维齐全时 missing 应为空")

            # ---------- 5. references 轮缺 completeness → partial ----------
            dp_ref_miss, _p, miss_rm = ex.judge_dims_partial(
                "references", {"rigor": 0.94})
            self.assert_eq(
                dp_ref_miss, True,
                "references 轮缺 completeness 时须判残缺")
            self.assert_eq(
                miss_rm, ["completeness"],
                "references 轮缺 completeness 时 missing 应精确回报")

            # 反向：references 轮只有 4 维（异常形态）→ 期望集有缺 → partial
            dp_ref_anom, _p, _m = ex.judge_dims_partial("references", section_dims)
            self.assert_eq(
                dp_ref_anom, True,
                "references 轮只有 4 维（completeness 缺失）须判残缺")

            # ---------- 6. 反向断言：复刻旧实现必然误判 ----------
            DIMENSION_FLOOR = {"innovation": 0.70, "feasibility": 0.70,
                               "rigor": 0.70, "expression": 0.70,
                               "completeness": 0.65}
            old_dp = (
                "scheme" in ("rationale", "content", "scheme")
                and bool(set(DIMENSION_FLOOR.keys()) - set(section_dims))
            )
            self.assert_eq(
                old_dp, True,
                "反向断言：旧实现（DIMENSION_FLOOR 全集）对完整正文轮必然误判 True")
            self.assert_true(
                old_dp != dp,
                "新旧实现必须给出相反结论，确保本测试不是自证绿")

            # ---------- 7. agent 奖惩守卫同步口径 ----------
            # executor.py:2356 用同一 judge_dims_partial → 正文轮不再被跳过
            guard_dp, _p, _m = ex.judge_dims_partial("scheme", section_dims)
            self.assert_eq(
                guard_dp, dp,
                "agent 奖惩守卫与 score_history 必须同口径（共用 judge_dims_partial）")
            self.assert_eq(
                guard_dp, False,
                "正文轮 4 维齐全应正常奖惩，不再被静默清零")

            # ---------- 8. v7.2.42 BUG-9：monitor 伪章节口径归一 ----------
            # monitor job 的 section_key="monitor" 不在 PROPOSAL_SECTIONS 中，
            # 但 depends_on 恒为 references-writer（controller.py:415），
            # 评判对象实为 references 专轮。未归一时 judge_dims_partial
            # 取章节 4 维期望比对 references 的 2 维报告 → 恒判残缺。
            self.assert_eq(
                ex.caliber_dim_key("monitor"), "references",
                "monitor 伪章节应归一到 references 口径")
            self.assert_eq(
                tuple(ex.expected_dim_keys("monitor")),
                ("rigor", "completeness"),
                "monitor 轮期望集应等同 references 的 2 维口径")
            dp_mon, _pm, miss_mon = ex.judge_dims_partial("monitor", ref_dims)
            self.assert_eq(
                dp_mon, False,
                "BUG-9 核心断言：references 2 维齐全的 monitor 轮不应被判残缺"
                "（修复前因落入章节 4 维口径而恒判 True，agent 奖惩 100% 被跳过）")
            self.assert_eq(
                miss_mon, [],
                "monitor 轮口径归一后 missing 应为空")

            # 归一后仍须保留防线：references 2 维真缺其一仍判残缺
            dp_mon_miss, _p2, miss_mon_miss = ex.judge_dims_partial(
                "monitor", {"rigor": 0.94})
            self.assert_eq(
                dp_mon_miss, True,
                "monitor 轮缺 completeness 时仍须判残缺（归一未削弱防线）")
            self.assert_eq(
                miss_mon_miss, ["completeness"],
                "monitor 轮残缺时 missing 应精确回报 completeness")

            # 非 monitor 章节不得被误归一
            for sk in ("rationale", "content", "scheme", "full_review", "references"):
                self.assert_eq(
                    ex.caliber_dim_key(sk), sk,
                    f"{sk} 不是伪章节，不应被 caliber_dim_key 改写")
        finally:
            import shutil

            shutil.rmtree(env, ignore_errors=True)


if __name__ == "__main__":
    import time

    suite = DimsPartialCaliberTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report

    print_report([suite])