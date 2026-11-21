# -*- coding: utf-8 -*-
"""snapshot_bridge 决策逻辑回归测试（v8.0.44）。

覆盖动机：main 历史被 4.2GB 遗留 PDF 阻断期间，异地恢复点由 snapshot
分支承担；refresh 决策错了会造成假新鲜（恢复点实际过期）或重复推送。
纯逻辑单测（不碰网络、不碰真实仓库对象）：
  远程缺失/不可解析 → 刷新；树一致 → 跳过；树漂移 → 刷新。

零 LLM / 零 hermes / 零网络。
"""
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from snapshot_bridge import resolve_remote_tree, should_refresh  # noqa: E402


class TestShouldRefresh(unittest.TestCase):
    def test_missing_remote_refreshes(self):
        self.assertTrue(should_refresh("tree-a", None))

    def test_same_tree_skips(self):
        self.assertFalse(should_refresh("tree-a", "tree-a"))

    def test_drifted_tree_refreshes(self):
        self.assertTrue(should_refresh("tree-b", "tree-a"))


class TestResolveRemoteTree(unittest.TestCase):
    """离线可验的坏输入路径：垃圾 SHA 解析失败 → None（保守判刷新）。"""

    def test_garbage_commit_returns_none(self):
        self.assertIsNone(resolve_remote_tree("not-a-commit"))

    def test_none_commit_returns_none(self):
        self.assertIsNone(resolve_remote_tree(None))


if __name__ == "__main__":
    unittest.main()
