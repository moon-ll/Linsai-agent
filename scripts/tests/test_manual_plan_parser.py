#!/usr/bin/env python3
"""_parse_manual_plan 容错强化回归测试（v7.3.45）。

背景：moire 手册 writer 3 连败卡死课题——模型输出前导推理 + JSON
（串内含裸换行/尾逗号/围栏缺失）时旧解析器直接放弃。本测试固化
各类真实输出形态的解析行为。
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lifecycle import executor as _executor  # noqa: E402


def _parse(text):
    # executor 为 mixin 模块（函数带 self 形参），_parse_manual_plan 不依赖状态
    return _executor._parse_manual_plan(None, text)


class TestParseManualPlan(unittest.TestCase):
    def test_clean_fenced_json(self):
        text = '```json\n{"actions": [{"action": "add", "section": "§3D.9 协议", "detail": "补扫描协议", "source_hint": ""}]}\n```'
        r = _parse(text)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["action"], "add")
        self.assertEqual(r[0]["section"], "§3D.9 协议")

    def test_reasoning_prefix_with_fenced_json(self):
        """moire 实测形态：前导推理 + Final plan + 围栏 JSON。"""
        text = (
            "Good. Now I have suitable source hints. Final plan:\n\n```json\n"
            '{"actions": [\n'
            ' {"action": "add", "section": "§3D.9 靶标 A 恢复时间分段扫描协议（5 ps–10 ns）", '
            '"detail": "补齐分段扫描", "source_hint": "momentum-methods"},\n'
            ' {"action": "revise", "section": "§3F.7 靶标 A 双通道读出协议", '
            '"detail": "口径对齐", "source_hint": ""}\n'
            "]}\n```\n"
            "希望这个计划符合要求。"
        )
        r = _parse(text)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0]["section"], "§3D.9 靶标 A 恢复时间分段扫描协议（5 ps–10 ns）")
        self.assertEqual(r[1]["action"], "revise")

    def test_raw_newline_inside_string(self):
        """字符串字面量含裸换行（LLM 手写 JSON 常见）→ 修复通道。"""
        text = (
            '计划如下：\n{"actions": [{"action": "revise", "section": "§2A 机理", '
            '"detail": "第一行\n第二行\t制表", "source_hint": ""}]}'
        )
        r = _parse(text)
        self.assertEqual(len(r), 1)
        self.assertIn("第二行", r[0]["detail"])

    def test_trailing_comma(self):
        text = '```json\n{"actions": [{"action": "add", "section": "§X", "detail": "d", "source_hint": "",},]}\n```'
        r = _parse(text)
        self.assertEqual(len(r), 1)

    def test_unclosed_fence(self):
        """围栏未闭合（输出截断）→ 全文平衡扫描兜底。"""
        text = (
            "Final plan:\n\n```json\n"
            '{"actions": [{"action": "add", "section": "§3D.9 协议", "detail": "d", "source_hint": ""}]}'
        )
        r = _parse(text)
        self.assertEqual(len(r), 1)

    def test_nested_braces_not_truncated(self):
        """嵌套对象不得被非贪婪匹配截断（旧 `\{.*?\}` 缺陷形态）。"""
        text = (
            '```json\n{"actions": [{"action": "merge", "section": "§A", "detail": "含{花括号}文本", "source_hint": ""}, '
            '{"action": "compress", "section": "§B", "detail": "压缩", "source_hint": ""}]}\n```'
        )
        r = _parse(text)
        self.assertEqual(len(r), 2)

    def test_field_salvage_fallback(self):
        """JSON 整体不可解析但字段文本在场 → 逐字段打捞。"""
        text = (
            'Final plan:\n{"actions": [ {"action": "add", "section": "§3D.9 分段扫描", '
            '"detail": "含 "引号" 未转义导致整体非法", "source_hint": ""} ]} 说明文字'
        )
        r = _parse(text)
        self.assertIsNotNone(r)
        self.assertEqual(r[0]["action"], "add")
        self.assertEqual(r[0]["section"], "§3D.9 分段扫描")

    def test_empty_plan_is_valid(self):
        """合法空计划（actions: []）→ 空列表而非 None。"""
        r = _parse('```json\n{"actions": []}\n```')
        self.assertEqual(r, [])

    def test_garbage_returns_none(self):
        self.assertIsNone(_parse(""))
        self.assertIsNone(_parse("没有任何 JSON 的普通文本"))
        self.assertIsNone(_parse(None))


if __name__ == "__main__":
    unittest.main()
