#!/usr/bin/env python3
"""
test_cluster_sim_channel.py — 输入端相似度通道 v2 回归（v7.3.1）

覆盖范围：
    ① 文本归一：arXiv ID / 年份 / LaTeX 下标 / 化学式 / 缩写与全称同义映射；
    ② 领域泛词抑制：仅共享泛词（强场物理 / 非线性光学）不应形成连接；
    ③ 字段加权：标题权重（0.35）高于摘要（0.20）；
    ④ 开关回滚：LINSAI_CLUSTER_SIM=v1 恢复旧口径（0.5/0.25/0.25）；
    ⑤ 成团门槛不变：0.15 + 3 成员下，同主题三条可成团、泛词三条不成团。

用法：
    python3 scripts/self_test.py --module   # 随全量模块回归执行
"""

import os
import sys
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from test_runner import TestSuite  # noqa: E402

from weekend_pipeline import clusters as C  # noqa: E402


def _item(title, keywords=None, summary="", sid="s1"):
    return {
        "source_id": sid,
        "title": title,
        "keywords": keywords or [],
        "summary": summary,
        "path": "",
    }


class ClusterSimChannelTests(TestSuite):
    def __init__(self):
        super().__init__("相似度通道 v2（v7.3.1）")

    def setup(self):
        self._saved = os.environ.get(C.SIM_CHANNEL_ENV)

    def teardown(self):
        if self._saved is None:
            os.environ.pop(C.SIM_CHANNEL_ENV, None)
        else:
            os.environ[C.SIM_CHANNEL_ENV] = self._saved

    def _set(self, value):
        os.environ[C.SIM_CHANNEL_ENV] = value

    # ── 归一 ──────────────────────────────────────────────────────────
    def _test_arxiv_and_year_normalized(self):
        a = _item("Quantum interference in high harmonic generation from monolayer WS2")
        b = _item("Quantum interference in high harmonic generation from monolayer WS2 (arXiv:2503.04335) (2025)")
        c = _item("Quantum interference in high harmonic generation from bulk GaSe")
        self._set(C.SIM_CHANNEL_V2)
        sim = C.item_similarity(a, b)
        sim_c = C.item_similarity(a, c)
        # v7.3.18：标题通道分母按原始并集（不因泛词抑制缩水），同题同文
        # 约 0.21；断言改为"高且高于同族不同材料对照"，直接验证归一化。
        self.assert_true(sim >= 0.20 and sim > sim_c, "arXiv ID/年份后缀不影响相似度",
                         f"sim={sim:.3f} vs 对照 {sim_c:.3f}")

    def _test_chem_formula_normalized(self):
        a = _item("Strain- and potential-controlled tunneling in monolayer MoS$_2$")
        b = _item("Strain- and potential-controlled tunneling in monolayer MoS₂")
        self._set(C.SIM_CHANNEL_V2)
        ta, tb = C._tokens_v2(a["title"]), C._tokens_v2(b["title"])
        self.assert_true("mos2" in ta and "mos2" in tb, "LaTeX/Unicode 下标化学式归一到 mos2",
                         f"ta={sorted(ta)} tb={sorted(tb)}")
        sim = C.item_similarity(a, b)
        self.assert_true(sim >= 0.30, "等价化学式标题相似度", f"sim={sim:.3f}")

    def _test_abbrev_and_fullname_synonym(self):
        a = _item("High harmonic generation in monolayer MoS2")
        b = _item("HHG in monolayer MoS2")
        self._set(C.SIM_CHANNEL_V2)
        ta, tb = C._tokens_v2(a["title"]), C._tokens_v2(b["title"])
        self.assert_true("hhg" in ta and "hhg" in tb, "全称与缩写映射到同一 hhg 词",
                         f"ta={sorted(ta)} tb={sorted(tb)}")

    def _test_cn_synonym_families_merge(self):
        ta = C._tokens_v2("固态高次谐波产生机制")
        tb = C._tokens_v2("高次谐波")
        self.assert_true(ta and tb and ta >= tb, "固态高次谐波/高次谐波产生归一到同一词元",
                         f"ta={sorted(ta)} tb={sorted(tb)}")

    # ── 泛词抑制 / 字段加权 ──────────────────────────────────────────
    def _test_generic_keywords_do_not_link(self):
        a = _item("Terahertz spectroscopy of perovskite thin films",
                  ["强场物理", "非线性光学", "二维材料"], "钙钛矿薄膜的时域光谱测量。")
        b = _item("Molecular dynamics of water interfaces",
                  ["强场物理", "非线性光学", "二维材料"], "水界面的分子动力学模拟。")
        self._set(C.SIM_CHANNEL_V2)
        v2 = C.item_similarity(a, b)
        self.assert_true(v2 < C.FORM_CLUSTER_SIM_THRESHOLD,
                         "仅共享领域泛词不形成连接", f"v2={v2:.3f}")
        self._set(C.SIM_CHANNEL_V1)
        v1 = C.item_similarity(a, b)
        self.assert_true(v1 >= 0.15, "旧口径下泛词共享会误连（对照）", f"v1={v1:.3f}")

    def _test_specific_keywords_still_link(self):
        a = _item("Rainbow RABBITT of neon", ["rabbitt", "氖原子", "阿秒延迟"])
        b = _item("Circular RABBITT delay retrieval", ["rabbitt", "圆偏振", "阿秒延迟"])
        self._set(C.SIM_CHANNEL_V2)
        self.assert_true(C.item_similarity(a, b) >= 0.15,
                         "具体主题词仍能形成连接", f"sim={C.item_similarity(a, b):.3f}")

    def _test_title_weight_above_summary(self):
        # 标题相同、摘要不同 → 分应高于"摘要相同、标题不同"
        title_shared = (
            _item("RABBITT spectroscopy of neon", ["rabbitt"], "甲摘要内容。"),
            _item("RABBITT spectroscopy of neon", ["rabbitt"], "乙摘要内容。"),
        )
        summary_shared = (
            _item("Altermagnet spin splitting", ["abc"], "共享的摘要正文 2-gram 内容。"),
            _item("Perovskite solar cells", ["abc"], "共享的摘要正文 2-gram 内容。"),
        )
        self._set(C.SIM_CHANNEL_V2)
        a = C.item_similarity(*title_shared)
        b = C.item_similarity(*summary_shared)
        self.assert_true(a > b, "标题通道权重高于摘要通道", f"title={a:.3f} summary={b:.3f}")

    # ── 开关回滚 ─────────────────────────────────────────────────────
    def _test_switch_rollback_v1_formula(self):
        a = _item("RABBITT spectroscopy of neon", ["rabbitt", "氖原子"], "阿秒延迟测量。")
        b = _item("RABBITT spectroscopy of argon", ["rabbitt", "氩原子"], "阿秒延迟测量。")
        self._set(C.SIM_CHANNEL_V1)
        legacy = (
            0.5 * C._overlap(C.kw_set(a["keywords"]), C.kw_set(b["keywords"]))
            + 0.25 * C._jaccard(C._tokenize(a["title"]), C._tokenize(b["title"]))
            + 0.25 * C._jaccard(C._tokenize(a["summary"][:C.SUMMARY_TEXT_LIMIT]),
                                C._tokenize(b["summary"][:C.SUMMARY_TEXT_LIMIT]))
        )
        self.assert_true(abs(C.item_similarity(a, b) - legacy) < 1e-9,
                         "v1 开关精确恢复旧口径", f"got={C.item_similarity(a, b):.4f} legacy={legacy:.4f}")

    # ── 成团门槛（0.15 / 3 成员，不得改动）───────────────────────────
    def _test_three_specific_orphans_form_cluster(self):
        self._set(C.SIM_CHANNEL_V2)
        orphans = [
            _item("Rainbow RABBITT as a probe of coherent electron dynamics in neon",
                  ["rabbitt", "氖原子", "阿秒延迟", "相干电子动力学"], sid="a"),
            _item("Continuous rainbow RABBITT investigation of attosecond delays in neon",
                  ["rabbitt", "氖原子", "阿秒延迟", "连续谱相位"], sid="b"),
            _item("Circular RABBITT in neon: delay retrieval under threshold",
                  ["rabbitt", "氖原子", "阿秒延迟", "圆偏振"], sid="c"),
        ]
        registry = {"clusters": [], "orphans": orphans}
        formed = C.form_new_clusters(registry)
        self.assert_true(len(formed) == 1, "同主题三条成 1 簇", f"formed={len(formed)}")
        if formed:
            self.assert_true(len(formed[0]["member_source_ids"]) == 3,
                             "簇成员 3 篇", f"members={formed[0]['member_source_ids']}")

    def _test_generic_only_orphans_do_not_form(self):
        self._set(C.SIM_CHANNEL_V2)
        orphans = [
            _item("Terahertz spectroscopy of perovskite films", ["强场物理", "非线性光学"], sid="a"),
            _item("Molecular dynamics of water interfaces", ["强场物理", "二维材料"], sid="b"),
            _item("Bayesian inference for phase diagrams", ["非线性光学", "二维材料"], sid="c"),
        ]
        registry = {"clusters": [], "orphans": orphans}
        formed = C.form_new_clusters(registry)
        self.assert_true(len(formed) == 0, "仅泛词共享不成团", f"formed={len(formed)}")
        self.assert_true(len(registry["orphans"]) == 3, "孤儿不丢失", f"orphans={len(registry['orphans'])}")

    def _test_generic_filter_does_not_shrink_denominator(self):
        """泛词抑制只减分子不缩分母：仅 1 个具体词巧合不得过线（v7.3.18）。"""
        self._set(C.SIM_CHANNEL_V2)
        item = _item("量子度规的光学测量",
                     ["量子度规", "berry曲率", "反演", "光学", "测量", "压缩感知", "层析"],
                     "量子度规反演。")
        cluster = {
            "cluster_id": "c1", "title": "Berry 曲率谱学",
            "keywords": ["berry曲率", "高次谐波", "谱学", "量子几何"],
            "summary": "研究 Berry 曲率在高次谐波谱学中的读出与反演。",
            "member_source_ids": [], "member_summaries": [],
        }
        sim = C.summary_similarity(item, cluster)
        self.assert_true(sim < 0.15, "仅共享 1 个具体词不应过 0.15（分母未缩水）", f"sim={sim:.3f}")

    def run_tests(self):
        self._test_arxiv_and_year_normalized()
        self._test_chem_formula_normalized()
        self._test_abbrev_and_fullname_synonym()
        self._test_cn_synonym_families_merge()
        self._test_generic_keywords_do_not_link()
        self._test_specific_keywords_still_link()
        self._test_title_weight_above_summary()
        self._test_generic_filter_does_not_shrink_denominator()
        self._test_switch_rollback_v1_formula()
        self._test_three_specific_orphans_form_cluster()
        self._test_generic_only_orphans_do_not_form()


if __name__ == "__main__":
    suite = ClusterSimChannelTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    failed = [r for r in suite.results if not r.passed]
    for r in suite.results:
        print(("✓" if r.passed else "✗"), r.name, r.msg)
    sys.exit(1 if failed else 0)
