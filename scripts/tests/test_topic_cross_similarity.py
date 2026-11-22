# -*- coding: utf-8 -*-
"""topic_cross_similarity.build_matrix 回归测试（v8.0.34）。

覆盖：同文 hard、异文 normal、空文本对跳过、对数与降序、阈值分级序。
零 LLM / 零 state 触碰（纯函数直测）。
"""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from topic_cross_similarity import (  # noqa: E402
    LEVEL_HARD,
    LEVEL_HIGH,
    build_matrix,
)


class TestBuildMatrix(unittest.TestCase):

    def test_identical_texts_hard(self):
        items = [{"id": "a", "text": "固体高次谐波产生与拓扑边界态探测"},
                 {"id": "b", "text": "固体高次谐波产生与拓扑边界态探测"}]
        pairs = build_matrix(items)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["score"], 1.0)
        self.assertEqual(pairs[0]["level"], "hard")

    def test_disjoint_texts_normal(self):
        items = [{"id": "a", "text": "阿秒条纹技术量子相位测量"},
                 {"id": "b", "text": "莫尔超晶格扭转角度依赖调控"}]
        pairs = build_matrix(items)
        self.assertEqual(len(pairs), 1)
        self.assertLess(pairs[0]["score"], LEVEL_HIGH)
        self.assertEqual(pairs[0]["level"], "normal")

    def test_empty_text_pair_skipped(self):
        items = [{"id": "a", "text": ""},
                 {"id": "b", "text": "某方向研究"}]
        self.assertEqual(build_matrix(items), [])

    def test_pair_count_and_desc_order(self):
        items = [{"id": f"t{i}", "text": f"方向{i}的研究路径"} for i in range(5)]
        pairs = build_matrix(items)
        self.assertEqual(len(pairs), 5 * 4 // 2)
        scores = [p["score"] for p in pairs]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_threshold_ordering(self):
        self.assertLess(LEVEL_HIGH, LEVEL_HARD)


if __name__ == "__main__":
    unittest.main()
