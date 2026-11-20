#!/usr/bin/env python3
"""
test_extract_score_formula_guard.py — _extract_score 公式行误回解析防御测试

覆盖缺陷（v7.2.8 修复，由健康检查发现）：

    critic 在评分档位依据小节会写出公式推演
    「综合评分：0.35×0.84＋0.29×0.80＋0.24×0.70＋0.12×0.76＝0.785 → 0.79」，
    原实现 re.search 取第一个匹配会把权重值 0.35 误当成综合分，
    污染 score_history 与下游 alert（moire r8 full_review 09-30 02:39 BJT
    误提 0.35，实际 0.79；触发 monitor score_drop 告警）。

修复：在候选中检测「综合评分：x.xx」后紧跟 × * + ＝ = → 等算术/推导字符，
跳过该候选，取下一个干净候选；若所有 pattern 均被公式污染，回退加权维度计算。

注意：本测试不调用 hermes/LLM，仅验证 _extract_score 解析逻辑。
"""

import sys

from test_runner import TestSuite, create_isolated_env
import importlib


class ExtractScoreFormulaGuardTests(TestSuite):
    def __init__(self):
        super().__init__("_extract_score 公式行防御测试")
        self.tmp_root = None
        self._opt = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 重新导入模块，避免复用其他测试的全局状态
        for mod_name in [
            "proposal_lifecycle.optimize",
            "proposal_lifecycle",
        ]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.optimize")
        from proposal_lifecycle.optimize import OptimizeMixin

        # 最小实例：仅需 _extract_score，不触发 LLM / 日志
        class _Fake(OptimizeMixin):
            def __init__(self):
                pass

        self._opt = _Fake()
        return True

    def teardown(self):
        return True

    def _call(self, output: str) -> float:
        return self._opt._extract_score({"output": output})

    def run_tests(self):
        opt = self._opt
        extract = self._call

        # 1. moire r8 full_review 真实案例（健康检查发现）
        moire_real = (
            "评分档位依据（rubric 对照）：\n"
            "综合评分：0.35×0.84＋0.29×0.80＋0.24×0.70＋0.12×0.76＝0.785 → 0.79\n"
            "\n"
            "## 评分\n"
            "创新性：0.84\n"
            "可行性：0.80\n"
            "严谨性：0.70\n"
            "表达质量：0.76\n"
            "综合评分：0.79\n"
        )
        s = extract(moire_real)
        self.assert_eq(round(s, 2), 0.79,
                       "moire r8 full_review 真实案例应取 0.79 而非 0.35")

        # 2. 正常行尾综合分
        normal = "## 评分\n创新性：0.84\n综合评分：0.79\n"
        s = extract(normal)
        self.assert_eq(round(s, 2), 0.79, "正常行尾综合评分应取 0.79")

        # 3. 公式带 → 推导
        formula_arrow = (
            "## 评分档位依据\n"
            "综合评分：0.65×0.84＋0.35×0.80＋0.25×0.70＋0.20×0.76＝0.78 → 0.78\n"
            "## 评分\n综合评分：0.78\n"
        )
        s = extract(formula_arrow)
        self.assert_eq(round(s, 2), 0.78, "公式带 → 推导应跳过第一候选取第二")

        # 4. 仅公式行无干净候选 + 充足长度 → 回退加权维度（0.30*0.84 + 0.25*0.80 + 0.25*0.70 + 0.20*0.76 = 0.779）
        # 输出需 >300 字符以触发 _extract_dimension_scores 的 min_output_len 防线（v6.8.50）
        _long_padding = (
            "项目立足固体高次谐波产生的反演诊断方法学空白，沿 Berry 曲率反演/Ghimire-ZnO 范式/"
            "TDDFT 核时估算三条主线展开论证。本节补充锚点对比与篇幅边界说明。"
            "本节从方法学沿革/边界设定/锚点对比/叙述弹性四个维度展开论述，"
            "重点审视跨章节指标口径一致性与全原胞 TDDFT 核时三口径互斥问题，"
            "并对原胞原子数 11000/6200/12400 三口径给出同口径折算方案。"
            "（填充文本以超过 300 字符防线）"
        )
        formula_only = (
            "## 评分档位依据\n"
            "综合评分：0.65×0.84＋0.35×0.80＋0.25×0.70＋0.20×0.76＝0.78\n"
            "## 评分\n"
            f"{_long_padding}\n"
            "创新性：0.84\n可行性：0.80\n严谨性：0.70\n表达质量：0.76\n"
        )
        s = extract(formula_only)
        self.assert_eq(round(s, 2), 0.78, "无干净候选应回退加权维度 ~0.78")

        # 5. GLM-5.2 简化输出格式
        glm_format = "综合分：0.85\n"
        s = extract(glm_format)
        self.assert_eq(round(s, 2), 0.85, "综合分：0.85 简化格式应取 0.85")

        # 6. overall_score 英文格式
        en_format = "overall_score: 0.78\n"
        s = extract(en_format)
        self.assert_eq(round(s, 2), 0.78, "overall_score 英文格式应取 0.78")

        # 7. 空输出
        s = extract("")
        self.assert_eq(round(s, 2), 0.0, "空输出应回退 0.0")

        # 8. 评分 0.35× 权重误匹配（确认 × 字符防护生效）
        weight_only = (
            "## 评分档位\n"
            "综合评分：0.35×0.84\n"  # 这是公式头，无干净候选
            "创新性：0.84\n综合评分：0.85\n"
        )
        s = extract(weight_only)
        self.assert_eq(round(s, 2), 0.85, "公式头 + 行尾干净候选应取行尾 0.85")


def main():
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    suite = ExtractScoreFormulaGuardTests()
    suite.setup()
    suite.run_tests()
    print(suite.summary())


if __name__ == "__main__":
    main()