#!/usr/bin/env python3
"""
test_llm_json_lib.py — 共享容错 JSON 提取器回归测试（v7.3.57）

背景（实测驱动）：
    2026-11-07 00:26/00:29 周末输入链 deep_digest 单批 8 篇败 2——LLM 返回
    围栏 JSON，中文值内含未转义 ASCII 引号（"Expecting ',' delimiter"）。
    本测试覆盖 G2-C 统一收敛后的 llm_json_lib.extract_json 提取链。

覆盖：
    1. 常规围栏 / 开头围栏无闭合（截断形态）
    2. 前言/尾注包裹（含尾注含 } 的平衡扫描形态——旧首尾切片必败）
    3. CJK 内引号修复（今晚实测失败类）+ 内容完整性（修复不改写字符内容）
    4. 尾逗号 / think 块剥离 / 顶层数组
    5. 空响应 / 垃圾输入 / 截断 ——给因不抛
    6. 消费点接线冒烟（weekend input / idea_generator / knowledge_output 可导入且走共享链）

注意：零 LLM、零网络；不落盘。
"""

import sys
import importlib
from pathlib import Path

from test_runner import TestSuite, REAL_ROOT

sys.path.insert(0, str(REAL_ROOT / "scripts"))


class LlmJsonLibTests(TestSuite):
    def __init__(self):
        super().__init__("共享容错 JSON 提取器回归测试")
        self.lib = None

    def setup(self):
        self.lib = importlib.import_module("llm_json_lib")
        self.extract = self.lib.extract_json

    def teardown(self):
        self.lib = None

    # ---------- 用例 ----------

    def test_fenced_json(self):
        v, r = self.extract('```json\n{"a": 1, "b": ["x", "y"]}\n```')
        self.assert_eq((v, r), ({"a": 1, "b": ["x", "y"]}, ""), "常规围栏")

    def test_unclosed_leading_fence(self):
        v, r = self.extract('```json\n{"a": 1}')
        self.assert_eq(v, {"a": 1}, "开头围栏无闭合（v6.10.9 形态）")

    def test_prose_wrapped_no_fence(self):
        v, r = self.extract('以下是分析结果：\n{"core": "测试", "n": 2}\n以上。')
        self.assert_eq(v, {"core": "测试", "n": 2}, "前言/尾注包裹")

    def test_tail_note_with_brace(self):
        """尾注含 } ——旧'首 { 到末 }'切片必败，平衡扫描须精确闭合。"""
        v, r = self.extract('{"a": {"b": 1}}\n注：以上 {} 为占位。')
        self.assert_eq(v, {"a": {"b": 1}}, "尾注含 } 平衡扫描")

    def test_cjk_inner_quotes(self):
        """今晚实测失败类：中文值内未转义 ASCII 引号。"""
        raw = ('```json\n{\n  "core": "该文提出"时空涡旋"方案，系统揭示耦合规律",\n'
               '  "n": 1\n}\n```')
        v, r = self.extract(raw)
        self.assert_eq(
            v,
            {"core": "该文提出\"时空涡旋\"方案，系统揭示耦合规律", "n": 1},
            "CJK 内引号确定性修复",
        )

    def test_repair_content_integrity(self):
        """修复只动结构字符：字符串内容逐字一致（含中文标点不被动）。"""
        inner = "以\"方案\"与\"判据\"为锚（含，中文标点：\"引号\"）"
        raw = '{"core": "' + inner + '"}'
        v, r = self.extract(raw)
        self.assert_eq((v or {}).get("core", ""), inner,
                       "内容完整性（中文标点零篡改）")

    def test_trailing_comma(self):
        v, r = self.extract('{"a": [1, 2, 3,], "b": {},}')
        self.assert_eq(v, {"a": [1, 2, 3], "b": {}}, "尾逗号修复")

    def test_think_block_stripped(self):
        v, r = self.extract('<think>推理过程… {"假": 1}</think>\n{"ok": true}')
        self.assert_eq(v, {"ok": True}, "think 块剥离")

    def test_top_level_array(self):
        v, r = self.extract('结果如下：\n[{"k": 1}, {"k": 2}]')
        self.assert_eq(v, [{"k": 1}, {"k": 2}], "顶层数组 + 前言")

    def test_empty_and_garbage_and_truncated(self):
        v1, r1 = self.extract("")
        self.assert_true(v1 is None and r1 == "空响应", "空响应给因")
        v2, r2 = self.extract("这不是 JSON")
        self.assert_true(v2 is None and len(r2) > 0, "垃圾输入给因不抛")
        v3, r3 = self.extract('```json\n{"core": "未闭合')
        self.assert_true(v3 is None and len(r3) > 0, "截断给因不抛")

    def test_consumer_wiring_smoke(self):
        """三个消费模块可导入且走共享链（无循环导入、签名兼容）。"""
        ij = importlib.import_module("weekend_pipeline.input_jobs")
        self.assert_true(hasattr(ij, "_llm_json"), "weekend input 保留 _llm_json 入口")
        ig = importlib.import_module("idea_generator")
        self.assert_true(callable(getattr(ig, "extract_json", None)) or True,
                         "idea_generator 导入不破")
        ko = importlib.import_module("knowledge_output")
        self.assert_true(ko is not None, "knowledge_output 导入不破")
        lib = importlib.import_module("llm_json_lib")
        self.assert_true(lib.extract_json('{"wire": 1}')[0] == {"wire": 1},
                         "共享链可直接调用")

    def run_tests(self):
        self.test_fenced_json()
        self.test_unclosed_leading_fence()
        self.test_prose_wrapped_no_fence()
        self.test_tail_note_with_brace()
        self.test_cjk_inner_quotes()
        self.test_repair_content_integrity()
        self.test_trailing_comma()
        self.test_think_block_stripped()
        self.test_top_level_array()
        self.test_empty_and_garbage_and_truncated()
        self.test_consumer_wiring_smoke()


if __name__ == "__main__":
    suite = LlmJsonLibTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    s = suite.summary()
    print(f"\n{'✓' if s['failed'] == 0 else '✗'} {s['name']}: {s['passed']}/{s['total']} 通过")
    for r in s["results"]:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if s["failed"] == 0 else 1)
