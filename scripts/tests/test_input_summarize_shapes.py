#!/usr/bin/env python3
"""
test_input_summarize_shapes.py — summarize 产物形状收敛测试

历史：
    v6.9.12 summarize 的 system prompt 要求"输出合法 JSON 数组"而
    user 模板要求对象，严格模型（glm-5.3 实测 08-15）按 system 返回
    [{...}]；旧代码仅对 dict 回填 source_id/path/tier，数组形状裸
    append 且照标 processed——首跑 30/30 条 malformed，cluster_assign
    全量崩溃（'list' object has no attribute 'get'），条目又因
    processed_sources 标记失去重试资格。v6.9.13 引入
    _coerce_summary_data 归一化（数组取首个 dict；不可收敛计
    failed_llm 不标 processed），并统一 prompt 为对象输出。

注意：
    本测试不调用 hermes/LLM。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test_runner import TestSuite

from weekend_pipeline.input_jobs import _coerce_summary_data


class SummarizeShapeTests(TestSuite):
    def __init__(self):
        super().__init__("summarize 产物形状收敛测试（v6.9.13）")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        paper = {"source_id": "arxiv-1234", "title": "T1", "path": "p1", "tier": 1}

        # 1. 数组包对象（glm-5.3 实测形状）→ 收敛为 dict 并回填溯源字段
        out = _coerce_summary_data(
            [{"title": "T1", "summary": "s", "keywords": ["k"]}], paper
        )
        self.assert_true(isinstance(out, dict), "数组形状应收敛为 dict")
        self.assert_eq(out.get("source_id"), "arxiv-1234", "必须回填 source_id")
        self.assert_eq(out.get("path"), "p1", "必须回填 path")
        self.assert_eq(out.get("tier"), 1, "必须回填 tier")
        self.assert_eq(out.get("keywords"), ["k"], "keywords 应保留")

        # 2. 纯 dict → 原样通过并回填；keywords 缺省补空列表；title 缺省回退
        out2 = _coerce_summary_data({"summary": "s2"}, paper)
        self.assert_true(out2 is not None, "dict 形状应通过")
        self.assert_eq(out2.get("source_id"), "arxiv-1234", "dict 也须回填 source_id")
        self.assert_eq(out2.get("keywords"), [], "keywords 缺省应为空列表")
        self.assert_eq(out2.get("title"), "T1", "title 缺省应回退论文标题")

        # 3. 无法收敛 → None（计入 failed_llm，不标 processed，保留重试资格）
        self.assert_true(_coerce_summary_data("not json", paper) is None, "字符串应返回 None")
        self.assert_true(_coerce_summary_data([1, 2], paper) is None, "无 dict 元素的数组应返回 None")
        self.assert_true(_coerce_summary_data([], paper) is None, "空数组应返回 None")
        self.assert_true(_coerce_summary_data(None, paper) is None, "None 应返回 None")

        # 4. 数组含多个 dict → 取首个 dict 元素
        out3 = _coerce_summary_data([{"summary": "first"}, {"summary": "second"}], paper)
        self.assert_true(out3 is not None and out3.get("summary") == "first", "多数组取首个 dict")


if __name__ == "__main__":
    suite = SummarizeShapeTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    s = suite.summary()
    print(f"通过 {s['passed']}/{s['passed'] + s['failed']}")
    sys.exit(1 if s["failed"] else 0)
