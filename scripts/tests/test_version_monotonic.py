#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_version_monotonic — VERSION 单调性守门（healthcheck 焦点④，v7.2.92 落地）

背景：ZCode 与管线并行写入 CHANGELOG 导致 v7.2.77-82 六对撞号（2026-11-01 发现，
以 v7.2.92 映射注记消歧）。本守门防再发：
    1. CHANGELOG 版本标题全局唯一（同版本号+同日期）
    2. VERSION 文件值与 CHANGELOG 最新条目一致（v7.2.96 补实现——此前仅
       docstring 声明未落地，致 4f07fdff 把 VERSION 回写 7.2.82 也绿灯）
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
VERSION = ROOT / "VERSION"


def _latest_changelog_version() -> str:
    t = CHANGELOG.read_text(encoding="utf-8")
    m = re.search(r"^## (v[\d.]+) - ", t, re.M)
    return m.group(1) if m else ""


class TestVersionMonotonic(unittest.TestCase):
    def test_changelog_versions_unique_recent(self):
        """同版本号+同日期才算撞号（历史遗留同号不同日期不报）。"""
        t = CHANGELOG.read_text(encoding="utf-8")
        keys = [f"{m.group(1)}@{m.group(2)}"
                for m in re.finditer(r"^## (v[\d.]+) - (20\d\d-\d\d-\d\d)", t, re.M)]
        dups = sorted(k for k in set(keys) if keys.count(k) > 1)
        # 已知存量豁免：v7.0.1@09-26 为 9 月历史存量（同号异日不在此列，待专项清理）
        KNOWN = {"v7.0.1@2026-09-26"}
        fresh = [k for k in dups if k not in KNOWN]
        self.assertEqual(fresh, [], f"CHANGELOG 新增撞号: {fresh}（存量 {dups}）")

    def test_version_file_format(self):
        cur = VERSION.read_text(encoding="utf-8").strip()
        self.assertRegex(cur, r"^\d+\.\d+\.\d+$", "VERSION 应为 x.y.z 纯格式")

    def test_version_matches_latest_entry(self):
        """VERSION 文件值必须等于 CHANGELOG 最新条目（v7.2.96 补落地）。

        v7.2.94 曾声明此断言但未实现——4f07fdff 编辑历史条目时把 VERSION
        回写 7.2.82（对 94 是倒退）而守门仍绿。本断言封堵该漏洞。
        """
        cur = VERSION.read_text(encoding="utf-8").strip()
        latest = _latest_changelog_version()
        self.assertTrue(latest, "CHANGELOG 应存在至少一个版本条目")
        self.assertEqual(
            f"v{cur}", latest,
            f"VERSION({cur}) 与 CHANGELOG 最新条目({latest})不一致"
            "——并行写入撞号或版本回退")

    def test_version_not_below_max_changelog_version(self):
        """VERSION 不得低于 CHANGELOG 中已出现的最大版本号（v7.3.13 补落地）。

        `test_version_matches_latest_entry` 只比对「文件首条」——当 CHANGELOG
        首条不是全库最大号时（并行会话把新条目追加到首条之下、或把大版本号
        条目排在后面），该断言照样绿。

        2026-11-04 实测：CHANGELOG 首条 v7.3.10，但第 3 条是 v7.3.12；
        commit 58633c9d 的 VERSION 被回写 7.2.98（前一 commit 7c35527e
        已是 7.3.11）→ 版本回退 11 个 patch 号，守门全绿未拦截。
        本断言封堵该漏洞：VERSION 必须 >= 全库最大版本号。
        """
        cur = VERSION.read_text(encoding="utf-8").strip()
        cur_tuple = tuple(int(x) for x in cur.split("."))
        t = CHANGELOG.read_text(encoding="utf-8")
        versions = [
            tuple(int(x) for x in m.group(1)[1:].split("."))
            for m in re.finditer(r"^## (v[\d.]+) - ", t, re.M)
        ]
        self.assertTrue(versions, "CHANGELOG 应存在至少一个版本条目")
        max_v = max(versions)
        self.assertGreaterEqual(
            cur_tuple, max_v,
            f"VERSION({cur}) 低于 CHANGELOG 中已出现的最大版本号 "
            f"v{'.'.join(str(x) for x in max_v)}——版本回退"
            "（并行写入把新条目排在首条之下时，"
            "test_version_matches_latest_entry 无法拦截）")


if __name__ == "__main__":
    unittest.main()
