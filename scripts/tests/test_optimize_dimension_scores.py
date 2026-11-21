#!/usr/bin/env python3
"""
test_optimize_dimension_scores.py — _extract_dimension_scores 维度得分解析回归测试

覆盖缺陷（v6.8.9 修复后仍存在）：
    批评报告维度表格式为 `| 维度 | 权重 | 得分 | 档位 | 主要短板 |`，
    档位/主要短板评语中可能含数字（如 "U/W ~ 0.5"、"已扣 ceiling 0.05"、"17.4%"）。
    早期实现"取行内最后一个 0.x"会误读到评语中的数字，导致：
        - 严谨性 0.10（实际 0.74）
        - 表达质量 0.05（实际 0.78）
    进而把维度压到 DIMENSION_FLOOR(0.70) 以下，强制模块失败并污染
    last_dim_scores / 知识库数据。

修复：改为取表格行内"最后一个独立纯数字单元格"（`0.xx` 独立成格）作为得分列。

注意：
    本测试不调用 hermes/LLM，仅验证维度得分解析逻辑。
"""

import sys

from test_runner import TestSuite, create_isolated_env
import importlib


class OptimizeDimScoreTests(TestSuite):
    def __init__(self):
        super().__init__("optimize 维度得分解析测试")
        self.tmp_root = None
        self._opt = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 重新导入模块，避免复用其他测试的全局状态
        for mod_name in [
            "proposal_lifecycle.optimize",
            "proposal_lifecycle",
            "proposal_sections",
        ]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.optimize")
        from proposal_lifecycle.optimize import OptimizeMixin

        # 最小实例：仅需 _DIM_MAP，不触发 LLM / 日志
        class _Fake(OptimizeMixin):
            def __init__(self):
                pass

        self._opt = _Fake()

    def teardown(self):
        # create_isolated_env 创建的临时目录由框架回收
        pass

    def run_tests(self):
        opt = self._opt
        extract = opt._extract_dimension_scores

        # 1. 权重|得分|档位|主要短板 表格，评语含数字（真实缺陷场景）
        table_with_commentary = """## 评分
| 维度 | 权重 | 得分 | rubric 档位 | 主要短板 |
|---|---:|---:|---|---|
| 创新性（innovation） | 0.30 | 0.78 | `0.8` 档：有明确改进但非本质突破 | 与 2025 同源但走独立路径 |
| 可行性（feasibility） | 0.25 | 0.78 | `0.8` 档：技术路线清晰 | 实测 132 mrad 目标未达成 |
| 严谨性（rigor） | 0.25 | 0.74 | `0.7` 档：逻辑有断点 | "U/W ~ 0.5"（应 ≳ 1）；占 17.4% |
| 表达质量（expression） | 0.20 | 0.78 | `0.8` 档：基本消除 AI 味 | 冗余词 17 次（已扣 ceiling 0.05） |
"""
        dims = extract({"output": table_with_commentary})
        self.assert_eq(
            round(dims.get("rigor", -1), 2), 0.74,
            "严谨性得分 0.74（不应被评语中 0.5/17.4% 干扰）",
        )
        self.assert_eq(
            round(dims.get("expression", -1), 2), 0.78,
            "表达质量得分 0.78（不应被评语中 0.05 干扰）",
        )
        self.assert_eq(
            round(dims.get("innovation", -1), 2), 0.78,
            "创新性得分 0.78（评语纯数字单元格优先于档位 0.8）",
        )
        self.assert_eq(
            round(dims.get("feasibility", -1), 2), 0.78,
            "可行性得分 0.78（不应误读档位 0.8）",
        )

        # 2. 简单表格 |维度|得分|
        dims2 = extract({"output": "| 维度 | 得分 |\n| 创新性（innovation） | 0.85 |"})
        self.assert_eq(
            round(dims2.get("innovation", -1), 2), 0.85,
            "简单表格 |维度|得分| 解析正确",
        )

        # 3. 权重+得分（无评语）
        dims3 = extract({"output": "| 创新性（innovation） | 0.30 | 0.85 |"})
        self.assert_eq(
            round(dims3.get("innovation", -1), 2), 0.85,
            "权重+得分表取得分列（0.85）而非权重列（0.30）",
        )

        # 4. 行内格式兜底
        dims4 = extract({"output": "创新性：0.78\n严谨性：0.74"})
        self.assert_eq(
            round(dims4.get("innovation", -1), 2), 0.78,
            "行内格式 创新性：0.78 解析正确",
        )

        # 5. 负向：无独立纯数字得分单元格时不应误报
        dims5 = extract({"output": "| 创新性（innovation） | `0.8` 档：提升明显 | 短板 17.4% |"})
        self.assert_eq(
            "innovation" in dims5, False,
            "无独立纯数字得分单元格时不误报创新性",
        )

        # 6. v6.9.78：粗体得分单元格（bsv R1 references 报告实测格式）——
        #    `| 严谨性（rigor） | 0.50 | **0.70** | ...` 原实现 fullmatch
        #    匹配不上 `**0.70**`，误取权重列 0.50 当得分（0.78 被记成 0.5，
        #    诱发"连续3轮下降"误暂停与 writer 连锁误扣）。
        bold_table = """## 三、维度评分（按用户指令，两维度）

| 维度 | 权重 | 得分 | 主要扣分点 |
|---|---|---|---|
| 严谨性（rigor） | 0.50 | **0.70** | C-1 张冠李戴（[2]↔[28] 归属错挂）；M-1 §E.11 自报数据与实际 2 处不一致 |
| 完整性（completeness） | 0.50 | **0.85** | H-1 [27] 综述未在正文任何位置被引用（缺失引用的极端形态）；H-2 预印本占比 28.6% |

**综合评分** = (严谨性 + 完整性) / 2 = (0.70 + 0.85) / 2 = **0.78**
"""
        dims6 = extract({"output": bold_table})
        self.assert_eq(
            round(dims6.get("rigor", -1), 2), 0.70,
            "粗体得分 **0.70** 应被正确解析（不应误取权重列 0.50）",
        )
        self.assert_eq(
            round(dims6.get("completeness", -1), 2), 0.85,
            "粗体得分 **0.85** 应被正确解析",
        )

        # 7. v6.9.78：上轮|本轮 对比表——本轮列（最后一个数字单元格）优先
        cmp_table = (
            "| 维度 | 上轮 | 本轮 | 变化 |\n"
            "| 创新性（innovation） | 0.50 | 0.78 | +0.28 |\n"
            "| 严谨性（rigor） | 0.40 | **0.74** | +0.34 |"
        )
        dims7 = extract({"output": cmp_table})
        self.assert_eq(
            round(dims7.get("innovation", -1), 2), 0.78,
            "对比表取本轮列 0.78（而非上轮 0.50）",
        )
        self.assert_eq(
            round(dims7.get("rigor", -1), 2), 0.74,
            "粗体本轮列 0.74 正确解析（而非上轮 0.40）",
        )

        # 8. v6.9.78 负向：评语中的粗体非纯数字不因剥离强调而误报
        dims8 = extract({"output": "| 严谨性（rigor） | **0.8 档**：逻辑有断点 | 占 17.4% |"})
        self.assert_eq(
            "rigor" in dims8, False,
            "评语含粗体文本（非纯数字单元格）不误报严谨性",
        )