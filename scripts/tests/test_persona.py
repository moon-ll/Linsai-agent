#!/usr/bin/env python3
"""
test_persona.py — 人格一致性抽检

不调用 LLM，仅做静态检查和规则校验：
    1. 人格注入文件结构完整性
    2. 关键锚点不可缺失
    3. 能力边界声明完整性
    4. 表达 DNA 特征存在性
    5. AI 协作哲学存在性
    6. 反模式清单完整性
"""

import re
from pathlib import Path
from test_runner import TestSuite, REAL_ROOT, TestResult


PERSONA_PATH = REAL_ROOT / "persona" / "lin-sai-persona.md"


class PersonaConsistencyTests(TestSuite):
    def __init__(self):
        super().__init__("人格一致性抽检")
        self.text = ""

    def setup(self):
        if PERSONA_PATH.exists():
            self.text = PERSONA_PATH.read_text(encoding="utf-8")
        else:
            self.text = ""

    def teardown(self):
        pass

    # ------------------------------------------------------------------
    def _test_persona_exists(self):
        self.assert_true(PERSONA_PATH.exists(), "人格注入文件存在",
                         f"缺失: {PERSONA_PATH}")

    def _test_anchors(self):
        """检查不可更改的人格锚点"""
        anchors = [
            ("林赛", "姓名锚点"),
            ("1995", "出生年份"),
            ("林建国", "父亲姓名"),
            ("What I cannot create", "核心信条"),
            ("认知驱动", "人格维度"),
            ("2026", "时间冻结"),
            ("强场超快光学", "研究领域"),
            ("固体高次谐波", "研究方向"),
        ]
        for keyword, label in anchors:
            self.assert_in(keyword, self.text, f"锚点-{label}")

    def _test_structure_sections(self):
        """检查主要章节存在"""
        sections = [
            "身份卡",
            "核心心智模型",
            "决策启发式",
            "表达DNA",
            "工作模式",
            "AI协作哲学",
            "价值层级",
            "能力边界",
            "CoPilot 交互原则",
            "绝对禁止",
            "子代理调用",
        ]
        for sec in sections:
            self.assert_in(sec, self.text, f"章节-{sec}")

    def _test_ai_collaboration(self):
        """AI 协作哲学细节"""
        self.assert_in("能力分工", self.text, "AI协作-能力分工")
        self.assert_in("Prompt策略", self.text, "AI协作-Prompt策略")
        self.assert_in("质量控制", self.text, "AI协作-质量控制")

    def _test_express_dna(self):
        """表达 DNA 特征"""
        self.assert_in("短句主导", self.text, "表达DNA-短句")
        self.assert_in("物理隐喻", self.text, "表达DNA-隐喻")

    def _test_anti_patterns(self):
        """反模式清单"""
        anti = [
            "堆砌物理术语",
            "标准答案",
            "假装知道所有答案",
            "空洞的鼓励",
        ]
        for a in anti:
            self.assert_in(a, self.text, f"反模式-{a}")

    def _test_boundaries(self):
        """能力边界声明"""
        self.assert_in("擅长的", self.text, "边界-擅长")
        self.assert_in("不擅长的", self.text, "边界-不擅长")
        self.assert_in("必须人工核实", self.text, "边界-核实")

    def _test_length_reasonable(self):
        """文件长度合理（不应过短）"""
        chars = len(self.text)
        self.assert_true(chars > 5000, f"人格文件长度充足 ({chars} chars)",
                         f"实际仅 {chars} 字符，可能内容缺失")

    def _test_no_placeholder(self):
        """检查无占位符残留"""
        bad = ["TODO", "FIXME", "占位符", "待补充"]
        for b in bad:
            if b.lower() in self.text.lower():
                self.results.append(TestResult(f"占位符检查-{b}", False, 0.0,
                                               f"发现残留占位符: {b}"))
            else:
                self.results.append(TestResult(f"占位符检查-{b}", True, 0.0, ""))

        # XXX 单独处理：排除 persona 中 "下周要交XXX" 这类示例用法
        if "XXX" in self.text:
            lines_with_xxx = [line for line in self.text.splitlines() if "XXX" in line]
            # 若仅出现在已知示例中，不算占位符
            is_placeholder = any("下周要交" not in line for line in lines_with_xxx)
            self.results.append(TestResult(
                "占位符检查-XXX",
                not is_placeholder,
                0.0,
                "发现残留占位符: XXX" if is_placeholder else ""
            ))
        else:
            self.results.append(TestResult("占位符检查-XXX", True, 0.0, ""))

    def run_tests(self):
        print(f"\n▶ {self.name}")
        tests = [
            self._test_persona_exists,
            self._test_anchors,
            self._test_structure_sections,
            self._test_ai_collaboration,
            self._test_express_dna,
            self._test_anti_patterns,
            self._test_boundaries,
            self._test_length_reasonable,
            self._test_no_placeholder,
        ]
        for t in tests:
            try:
                t()
            except Exception as e:
                self.results.append(
                    TestResult(t.__name__, False, 0.0, f"{type(e).__name__}: {e}")
                )
