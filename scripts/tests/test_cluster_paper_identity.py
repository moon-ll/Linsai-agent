#!/usr/bin/env python3
"""
test_cluster_paper_identity.py — 论文级去重 + 超大簇二级拆分回归（v7.3.21）

覆盖范围（对应用户裁决 决定 2 / 决定 3）：
    ① 论文身份键：DOI > arXiv ID（含 `2404_05830` 下划线写法）> 归一化标题；
    ② 3 条记录 / 2 篇唯一论文 → 不成团（门槛按唯一论文计数）；
    ③ 3 篇唯一论文 → 正常成团，unique_paper_count=3；
    ④ 去重开关 LINSAI_CLUSTER_DEDUP_PAPERS=off → 回退记录计数（可回滚）；
    ⑤ 超大簇拆分：>20 唯一论文的连通分量切成 2 片，每片 ≥3 篇唯一；
    ⑥ 拆分开关 LINSAI_CLUSTER_SPLIT=off → 不拆分（1 簇 24 篇）；
    ⑦ 跨领域标记：方向命中率 <0.6 且 ≥8 篇 → cross_domain=True（保留不删）；
    ⑧ 注册门槛 _new_gates 优先读 unique_paper_count。

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

_SHARED_KW = [
    "harmonic emission", "wannier interpolation", "interband coherence", "periodic gauge",
]
_SUM_BASE = (
    "本文在周期性规范下采用 Wannier 插值构建带分辨的布洛赫态，系统比较了带间相干与晶体动量"
    "选择对谐波发射的贡献，并定量分解了退相干时间对发射强度的影响，给出了可复现的数值流程。"
)


def _item(sid, title, keywords=None, summary=""):
    return {
        "source_id": sid,
        "title": title,
        "keywords": list(keywords or []),
        "summary": summary,
        "path": "",
    }


def _zno(i, sid=None):
    return _item(
        sid or f"paper:2023-a{i:02d}",
        f"High harmonic generation and interband coherence in wurtzite ZnO valence band sample a{i}",
        ["zno", "wurtzite", "valence band", "高次谐波"] + _SHARED_KW,
        _SUM_BASE + f"研究对象为纤锌矿 ZnO 的价带样品 a{i}，取向为 c 轴，观测高次谐波发射。",
    )


def _weyl(i, sid=None):
    return _item(
        sid or f"paper:2024-b{i:02d}",
        f"Chiral anomaly signatures in Weyl semimetal Berry curvature sample b{i}",
        ["weyl", "chiral anomaly", "berry curvature"] + _SHARED_KW,
        _SUM_BASE + f"研究对象为 Weyl 半金属的手征反常样品 b{i}，磁场沿 x 轴。",
    )


def _pinn(i):
    return _item(
        f"paper:2025-p{i:02d}",
        f"Physics-informed neural networks for PDE inverse problems in finance sample p{i}",
        [
            "physics-informed neural networks", "inverse problems",
            "partial differential equations", "financial derivative pricing",
            "operator learning", "boundary conditions",
        ],
        "本文用物理信息神经网络求解偏微分方程反问题，并将其用于金融衍生品定价，"
        "比较了算子学习与边界约束对收敛速度的影响。",
    )


class ClusterPaperIdentityTests(TestSuite):
    def __init__(self):
        super().__init__("论文级去重 + 超大簇拆分（v7.3.21）")

    def setup(self):
        self._saved = {
            k: os.environ.get(k) for k in (
                C.PAPER_DEDUP_ENV, C.LARGE_CLUSTER_SPLIT_ENV, C.SIM_CHANNEL_ENV,
                C.ORPHAN_DEDUP_ENV, C.ORPHAN_AGING_ENV,
            )
        }

    def teardown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    # ── 论文身份键 ────────────────────────────────────────────────────
    def _test_paper_key_arxiv_variants(self):
        self.assert_eq(
            C.paper_key(_item("paper:2023-2310.17007-high-harmonic", "x")),
            "arxiv:2310.17007", "带日期前缀的 arXiv 写法归一")
        self.assert_eq(
            C.paper_key(_item("paper:2024-2404_05830-spin-high-harmonic", "x")),
            "arxiv:2404.05830", "下划线 arXiv 写法归一为点号")
        self.assert_eq(
            C.paper_key(_item("paper:2506.22860", "x")),
            "arxiv:2506.22860", "纯 arXiv ID 直接命中")

    def _test_paper_key_doi_priority(self):
        a = _item("paper:2023-2310.17007-publisher", "Harmonic emission in ZnO",
                  [], "x")
        a["doi"] = "10.1103/PhysRevLett.126.123456"
        self.assert_eq(C.paper_key(a), "doi:10.1103/physrevlett.126.123456",
                       "DOI 优先于 arXiv ID")
        # 真实语料的 DOI slug（10-1103-…）无法解析，靠同名标题归并
        arxiv_rec = _item("paper:2023-2310.17007-high-harmonic-zno",
                          "High harmonic generation in wurtzite ZnO")
        doi_rec = _item("paper:2026-doi-10-1103-84vm-tvzm-high-harmonic-zno",
                        "High harmonic generation in wurtzite ZnO")
        self.assert_eq(len(C._unique_papers([arxiv_rec, doi_rec])), 1,
                       "arXiv 记录与 DOI slug 记录同名 → 归并为 1 篇")

    def _test_paper_key_title_normalized(self):
        a = _item("paper:x", "Harmonic Emission in Wurtzite ZnO: A Wannier Study")
        b = _item("paper:y", "harmonic emission in wurtzite zno (2024): a wannier study")
        self.assert_eq(len(C._unique_papers([a, b])), 1,
                       "同标题仅标点/大小写/年份不同 → 同一论文")
        c = _item("paper:z", "Chiral anomaly in Weyl semimetals")
        self.assert_true(C.paper_key(a) != C.paper_key(c), "不同标题 → 不同论文键")
        # 无标题无 ID → 退回 source_id，两条记录不被错并
        self.assert_true(
            C.paper_key(_item("paper:q", "")) != C.paper_key(_item("paper:r", "")),
            "无信息记录按 source_id 区分")

    # ── 决定 2：唯一论文计数 ──────────────────────────────────────────
    def _test_three_records_two_unique_not_formed(self):
        """3 条记录 / 2 篇唯一论文 → 不得成团（决定 2 核心用例）。"""
        dup = [
            _item("paper:2023-2310.17007-harmonic-emission-in-zno",
                  "Harmonic emission and interband coherence in wurtzite ZnO valence band",
                  ["zno", "wurtzite", "valence band"] + _SHARED_KW, _SUM_BASE),
            _item("paper:2310.17007",
                  "Harmonic emission in wurtzite ZnO: publisher version",
                  ["zno", "wurtzite", "valence band"] + _SHARED_KW, _SUM_BASE),
            _zno(2),
        ]
        self.assert_eq(len(C._unique_papers(dup)), 2, "三条记录只应算 2 篇唯一论文")
        registry = {"clusters": [], "orphans": list(dup)}
        formed = C.form_new_clusters(registry)
        self.assert_eq(len(formed), 0, "2 篇唯一 < 3 成员门槛，不得成团")
        self.assert_eq(len(registry["orphans"]), 3, "团员退回 orphans，不静默丢失")

    def _test_three_unique_formed(self):
        registry = {"clusters": [], "orphans": [_zno(0), _zno(1), _zno(2)]}
        formed = C.form_new_clusters(registry)
        self.assert_eq(len(formed), 1, "3 篇唯一论文应成团")
        self.assert_eq(formed[0]["unique_paper_count"], 3, "unique_paper_count 应为 3")
        self.assert_eq(formed[0]["duplicate_record_count"], 0, "无重复记录")

    def _test_dedup_switch_off_record_counting(self):
        dup = [
            _item("paper:2023-2310.17007-harmonic-emission-in-zno",
                  "Harmonic emission and interband coherence in wurtzite ZnO valence band",
                  ["zno", "wurtzite", "valence band"] + _SHARED_KW, _SUM_BASE),
            _item("paper:2310.17007",
                  "Harmonic emission in wurtzite ZnO: publisher version",
                  ["zno", "wurtzite", "valence band"] + _SHARED_KW, _SUM_BASE),
            _zno(2),
        ]
        os.environ[C.PAPER_DEDUP_ENV] = "off"
        try:
            registry = {"clusters": [], "orphans": list(dup)}
            formed = C.form_new_clusters(registry)
            self.assert_eq(len(formed), 1, "开关 off 回退记录计数（3 记录成立）")
            self.assert_eq(formed[0]["unique_paper_count"], 3,
                           "off 口径下按记录数计")
        finally:
            os.environ.pop(C.PAPER_DEDUP_ENV, None)

    def _test_new_gate_prefers_unique_paper_count(self):
        from weekend_pipeline.input_jobs import _new_gates
        cluster = {
            "member_summaries": [{"title": "A paper"}, {"title": "B paper"},
                                 {"title": "C paper"}],
            "member_source_ids": ["s1", "s2", "s3"],
            "unique_paper_count": 2,
            "distilled_by": "llm",
            "title": "强场 高次谐波", "keywords": ["强场物理"], "summary": "",
            "research_gap": "存在缺口",
        }
        ok, reason = _new_gates(cluster, [], ["强场"], 2)
        self.assert_eq(ok, False, "注册门槛应按唯一论文数拒绝 2 篇簇")
        self.assert_true("独立成员 2" in reason, "理由应报唯一论文 2 < 3")
        cluster["unique_paper_count"] = 3
        ok2, reason2 = _new_gates(cluster, [], ["强场"], 2)
        self.assert_true("独立成员" not in reason2, "3 篇唯一时成员关应通过")

    # ── 决定 3：超大簇二级拆分 ────────────────────────────────────────
    def _test_large_group_split(self):
        group = [_zno(i) for i in range(12)] + [_weyl(i) for i in range(12)]
        self.assert_eq(len(C._unique_papers(group)), 24, "构造 24 篇唯一论文")
        parts = C._split_large_group(group)
        self.assert_eq(len(parts), 2, "24 篇应拆成 2 片")
        for p in parts:
            self.assert_true(len(C._unique_papers(p)) >= C.MIN_CLUSTER_MEMBERS,
                             "每片须 ≥3 篇唯一论文")

    def _test_split_switch_on_off(self):
        group = [_zno(i) for i in range(12)] + [_weyl(i) for i in range(12)]
        os.environ.pop(C.LARGE_CLUSTER_SPLIT_ENV, None)
        registry = {"clusters": [], "orphans": list(group)}
        formed = C.form_new_clusters(registry)
        self.assert_eq(len(formed), 2, "拆分开：1 个超大类切成 2 个候选簇")
        self.assert_eq(sum(c["unique_paper_count"] for c in formed), 24, "论文不丢")

        os.environ[C.LARGE_CLUSTER_SPLIT_ENV] = "off"
        try:
            registry2 = {"clusters": [], "orphans": list(group)}
            formed2 = C.form_new_clusters(registry2)
            self.assert_eq(len(formed2), 1, "拆分关：不拆分，仍为 1 个簇")
            self.assert_eq(formed2[0]["unique_paper_count"], 24, "整簇 24 篇")
        finally:
            os.environ.pop(C.LARGE_CLUSTER_SPLIT_ENV, None)

    def _test_cross_domain_marked_not_dropped(self):
        """跨领域大簇保留并打 cross_domain 标记（交 LLM 仲裁，不删）。"""
        registry = {"clusters": [], "orphans": [_pinn(i) for i in range(9)]}
        formed = C.form_new_clusters(registry)
        self.assert_eq(len(formed), 1, "跨领域簇应保留成团")
        self.assert_eq(formed[0]["cross_domain"], True,
                       "方向命中率低且 ≥8 篇 → cross_domain=True")
        self.assert_true(formed[0]["direction_hit_ratio"] is not None,
                         "方向命中率应落盘供仲裁参考")

    def _test_strong_field_cluster_not_cross_domain(self):
        registry = {"clusters": [], "orphans": [_zno(i) for i in range(12)]}
        formed = C.form_new_clusters(registry)
        self.assert_eq(len(formed), 1, "同主题簇正常成团")
        self.assert_eq(formed[0]["cross_domain"], False,
                       "方向命中率高 → 不打跨领域标记")

    # ── 裁决 1：跨领域簇立题取料按成员级过滤 ───────────────────────────
    def _test_cross_domain_member_filter(self):
        """跨领域成员（金融/PINN）不得进入设想证据链。"""
        cluster = {
            "cross_domain": True,
            "unique_paper_count": 9,
            "member_summaries": [_pinn(i) for i in range(6)] + [_zno(i) for i in range(3)],
        }
        kept = C.idea_evidence_members(cluster)
        self.assert_eq(len(kept), 3, "只应保留 3 条核心范式成员")
        self.assert_true(all("harmonic generation" in m["title"] for m in kept),
                         "保留项应为强场/HHG 成员")
        self.assert_true(all("finance" not in m["title"] for m in kept),
                         "金融/PINN 成员应被排除")
        self.assert_eq(C.evidence_paper_count(cluster), 3, "过滤后唯一论文数为 3")

    def _test_filtered_below_three_not_new(self):
        """过滤后 <3 篇唯一 → 不立题，降级补充文献池。"""
        from weekend_pipeline.input_jobs import _new_gates
        cluster = {
            "cross_domain": True,
            "unique_paper_count": 8,
            "member_summaries": [_pinn(i) for i in range(6)] + [_zno(0), _zno(1)],
            "distilled_by": "llm", "title": "强场 高次谐波",
            "keywords": ["强场物理"], "summary": "", "research_gap": "存在缺口",
        }
        self.assert_eq(C.evidence_paper_count(cluster), 2, "过滤后仅 2 篇唯一")
        ok, reason = _new_gates(cluster, [], ["强场"], 2)
        self.assert_eq(ok, False, "过滤后 2 篇不得立题")
        self.assert_true("补充文献池" in reason, "理由应报降级补充文献池")

    def _test_normal_cluster_unfiltered(self):
        """正常簇不受影响：不因个别成员未命中核心范式而丢料。"""
        from weekend_pipeline.input_jobs import _new_gates
        cluster = {
            "cross_domain": False,
            "unique_paper_count": 9,
            "member_summaries": [_pinn(i) for i in range(6)] + [_zno(i) for i in range(3)],
            "distilled_by": "llm", "title": "强场 高次谐波",
            "keywords": ["强场物理"], "summary": "", "research_gap": "存在缺口",
        }
        self.assert_eq(len(C.idea_evidence_members(cluster)), 9,
                       "正常簇成员原样保留")
        ok, reason = _new_gates(cluster, [], ["强场"], 2)
        self.assert_true("补充文献池" not in reason, "正常簇不应触发补充文献池降级")

    def _test_filtered_dedup_counts_unique(self):
        """过滤后的论文仍按唯一论文计数（同文双记录不凑数）。"""
        dup_hhg = [
            _item("paper:2023-2310.17007-hhg-zno",
                  "High harmonic generation in bulk ZnO sample h0",
                  ["高次谐波", "zno"], _SUM_BASE),
            _item("paper:2310.17007",
                  "High harmonic generation in bulk ZnO sample h0 publisher",
                  ["高次谐波", "zno"], _SUM_BASE),
        ]
        cluster = {
            "cross_domain": True, "unique_paper_count": 8,
            "member_summaries": [_pinn(i) for i in range(6)] + dup_hhg,
        }
        self.assert_eq(C.evidence_paper_count(cluster), 1,
                       "两条同文记录只算 1 篇，证据链不足 3 篇")

    # ── 孤儿池身份去重（v7.3.23 决定 5b-1）───────────────────────────
    def _test_orphan_pool_dedup(self):
        thin = _item("paper:2508.16166", "High harmonic generation in wurtzite ZnO")
        rich = _item("paper:2026-2508.16166-high-harmonic-zno",
                     "High harmonic generation in wurtzite ZnO",
                     ["zno", "高次谐波"], _SUM_BASE + "观测高次谐波发射。")
        other = _item("paper:2604.12602", "Attosecond beamline for XUV pump probe",
                      ["attosecond"], _SUM_BASE)
        reg = {"clusters": [], "orphans": [thin, rich, other]}
        removed = C.dedup_orphans(reg)
        self.assert_eq(removed, 1, "两条同 arXiv 记录归并 1 条")
        self.assert_eq(len(reg["orphans"]), 2, "孤儿池 3 → 2 条唯一")
        kept = [o for o in reg["orphans"] if "2508.16166" in o["source_id"]][0]
        self.assert_eq(kept["source_id"], rich["source_id"],
                       "保留信息更丰的代表（有摘要/关键词）")
        self.assert_eq(C.dedup_orphans(reg), 0, "重复调用幂等，第二次移除 0 条")

    def _test_orphan_dedup_switch_off(self):
        os.environ[C.ORPHAN_DEDUP_ENV] = "off"
        try:
            thin = _item("paper:2508.16166", "High harmonic generation in wurtzite ZnO")
            rich = _item("paper:2026-2508.16166-high-harmonic-zno",
                         "High harmonic generation in wurtzite ZnO",
                         ["zno"], _SUM_BASE)
            reg = {"clusters": [], "orphans": [thin, rich]}
            self.assert_eq(C.dedup_orphans(reg), 0, "开关 off 时不去重")
            self.assert_eq(len(reg["orphans"]), 2, "开关 off 保留两条记录")
        finally:
            os.environ.pop(C.ORPHAN_DEDUP_ENV, None)

    def _test_anonymous_orphans_not_merged(self):
        a = {"source_id": "", "title": "", "keywords": [], "summary": "甲"}
        b = {"source_id": "", "title": "", "keywords": [], "summary": "乙"}
        c = {"source_id": "", "title": "", "keywords": [], "summary": "丙"}
        reg = {"clusters": [], "orphans": [a, b, c]}
        self.assert_eq(C.dedup_orphans(reg), 0, "无标识匿名记录不得互并（v7.3.24）")
        self.assert_eq(len(reg["orphans"]), 3, "三条匿名孤儿原样保留")

    # ── 决定 7：同标题不同 arXiv 分开处理（v7.3.25）───────────────────
    def _test_year_typo_merge_with_review_mark(self):
        """年份前缀笔误（编号相同）→ 归并并打 needs_review 便于回溯。"""
        a = _item("paper:2508.16422", "High harmonic generation in wurtzite ZnO")
        b = _item("paper:2608.16422", "High harmonic generation in wurtzite ZnO")
        reg = {"clusters": [], "orphans": [a, b]}
        self.assert_eq(C.dedup_orphans(reg), 1, "同编号仅年份不同 → 归并 1 条")
        kept = reg["orphans"][0]
        self.assert_eq(kept.get("needs_review"), True, "被并记录打 needs_review 回溯标记")
        self.assert_true(
            any("2608.16422" in s for s in kept.get("merged_source_ids") or []),
            "merged_source_ids 留存被并原始编号",
        )

    def _test_different_ids_not_merged(self):
        """标题相同但 arXiv 编号本身不同（非笔误）→ 不得自动归并。"""
        a = _item("paper:2307.14693", "Deep learning retrieval of high harmonic spectra")
        b = _item("paper:2104.07366", "Deep learning retrieval of high harmonic spectra")
        reg = {"clusters": [], "orphans": [a, b]}
        self.assert_eq(C.dedup_orphans(reg), 0, "编号不同且无共同 DOI → 不自动合并")
        self.assert_eq(len(reg["orphans"]), 2, "两条记录保留供人工判断")

    # ── 决定 8：孤儿老化三段式（v7.3.25）───────────────────────────────
    @staticmethod
    def _aged(item, days):
        from datetime import datetime, timedelta, timezone
        t = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        return {**item, "first_seen": t}

    def _test_orphan_aging_downweight_not_excluded(self):
        """第一段：>60 天降权递减但不排除（高龄强相似仍能成团）。"""
        self.assert_eq(C.orphan_weight(self._aged(_zno(0), 30)), 1.0,
                       "≤60 天不降权")
        mid = C.orphan_weight(self._aged(_zno(0), 120))
        self.assert_true(C.ORPHAN_WEIGHT_FLOOR <= mid < 1.0,
                         "60–180 天区间权重在 [0.85,1) 内线性递减")
        self.assert_eq(C.orphan_weight(self._aged(_zno(0), 200)),
                       C.ORPHAN_WEIGHT_FLOOR, ">180 天维持下限，不归零")
        # 年龄回写可观测（先于聚团执行，聚团会消费孤儿）
        age_reg = {"clusters": [], "orphans": [
            self._aged(_zno(0), 100), self._aged(_zno(1), 100),
            self._aged(_zno(2), 100),
        ]}
        self.assert_eq(C.stamp_orphan_ages(age_reg), 3,
                       ">60 天记录数回写（downweighted）")
        self.assert_true(all("orphan_age_days" in o for o in age_reg["orphans"]),
                         "每条孤儿落 orphan_age_days")
        # 降权≠排除：100 天高龄、相似度足够强的三篇仍正常成团
        reg = {"clusters": [], "orphans": [
            self._aged(_zno(0), 100), self._aged(_zno(1), 100),
            self._aged(_zno(2), 100),
        ]}
        self.assert_eq(len(C.form_new_clusters(reg)), 1,
                       "高龄孤儿强相似仍成团（未排除）")

    def _test_orphan_archive_not_deleted(self):
        """第二段：>180 天移出聚团池并归档，不删除。"""
        old = self._aged(_item("paper:old-hhg", "Old orphan in strong field"), 200)
        fresh = self._aged(_item("paper:fresh", "Fresh orphan"), 10)
        reg = {"clusters": [], "orphans": [old, fresh]}
        self.assert_eq(C.archive_aged_orphans(reg), 1, ">180 天归档 1 条")
        self.assert_eq(len(reg["orphans"]), 1, "归档后不再占孤儿池")
        pool = reg.get("supplementary_pool") or []
        self.assert_eq(len(pool), 1, "归档不删除（移入补充池）")
        self.assert_eq(pool[0].get("archive_reason"), "age>180d", "归档原因落盘")
        self.assert_eq(pool[0].get("title"), "Old orphan in strong field",
                       "记录内容完整保留")
        self.assert_true("archived_at" in pool[0], "归档时间落盘")

    def _test_archived_pool_still_searchable(self):
        """归档后仍可被按需检索。"""
        hhg = self._aged(_item("paper:argon-hhg",
                               "Argon gas high harmonic generation spectroscopy"), 200)
        fin = self._aged(_item("paper:finance",
                               "Option pricing with implied volatility surface"), 200)
        reg = {"clusters": [], "orphans": [], "supplementary_pool": [hhg, fin]}
        hits = C.search_supplementary_pool(reg, "high harmonic generation argon")
        self.assert_true(bool(hits), "归档条目可被检索命中")
        self.assert_eq(hits[0]["source_id"], "paper:argon-hhg", "命中最相关归档条目")

    def _test_orphan_aging_switch_off(self):
        """开关 off 可回滚：不降权、不归档、不回写年龄。"""
        os.environ[C.ORPHAN_AGING_ENV] = "off"
        try:
            reg = {"clusters": [], "orphans": [self._aged(_zno(0), 200)]}
            self.assert_eq(C.orphan_weight(reg["orphans"][0]), 1.0, "off 不降权")
            self.assert_eq(C.archive_aged_orphans(reg), 0, "off 不归档")
            self.assert_eq(C.stamp_orphan_ages(reg), 0, "off 不回写年龄")
        finally:
            os.environ.pop(C.ORPHAN_AGING_ENV, None)

    def _test_confirmed_pair_merged_newer_metadata(self):
        """人工确认同篇多版本（2011.11079 / 1906.12135）→ 并、保留较新版本、needs_review。"""
        old = _item("paper:2019-1906.12135-low-frequency-and-moire-floquet-engineering-a-review",
                    "Low-frequency and Moiré Floquet engineering: a review",
                    ["review"], "旧版摘要")
        new = _item("paper:2020-2011.11079-low-frequency-and-moire-floquet-engineering-a-review",
                    "Low-frequency and Moiré Floquet engineering: a review",
                    ["floquet"], "新版摘要")
        reg = {"clusters": [], "orphans": [old, new]}
        self.assert_eq(C.dedup_orphans(reg), 1, "确认白名单对允许跨编号归并")
        kept = reg["orphans"][0]
        self.assert_true("2011.11079" in kept["source_id"], "保留较新版本的元数据")
        self.assert_eq(kept.get("needs_review"), True, "确认归并同样打 needs_review")
        self.assert_true(
            any("1906.12135" in s for s in kept.get("merged_source_ids") or []),
            "旧版本 source_id 留存可回溯",
        )

    def _test_confirmed_pair_nonzero_index(self):
        """回归：确认对所在组在原索引中不从 0 开始（旧实现在此路径 IndexError）。"""
        noise = [
            _item("paper:2024-9999.00001-unrelated-noise-one", "Unrelated noise paper one"),
            _item("paper:2024-9999.00002-unrelated-noise-two", "Unrelated noise paper two"),
        ]
        old = _item("paper:2019-1906.12135-low-frequency-and-moire-floquet-engineering-a-review",
                    "Low-frequency and Moiré Floquet engineering: a review",
                    ["review"], "旧版摘要")
        new = _item("paper:2020-2011.11079-low-frequency-and-moire-floquet-engineering-a-review",
                    "Low-frequency and Moiré Floquet engineering: a review",
                    ["floquet"], "新版摘要")
        # 目标组原索引为 2、3（非 0 起始）——旧实现 ids[i] 会越界
        reg = {"clusters": [], "orphans": noise + [old, new]}
        self.assert_eq(C.dedup_orphans(reg), 1, "非 0 起始仍可归并确认对")
        self.assert_eq(len(reg["orphans"]), 3, "仅移除被并旧版，噪声保留")
        kept = next(o for o in reg["orphans"] if "2011.11079" in str(o.get("source_id")))
        self.assert_eq(C.paper_key(kept), C.paper_key(new),
                       "代表取自全局列表中的较新版本（非错位项）")
        self.assert_eq(kept.get("needs_review"), True, "确认归并打 needs_review")
        self.assert_true(
            any("1906.12135" in s for s in kept.get("merged_source_ids") or []),
            "旧版本进入 merged_source_ids",
        )

    def _test_different_ids_nonzero_index_not_merged(self):
        """反向回归：同样的非 0 起始布局，未入白名单的编号不同组仍不归并。"""
        noise = [
            _item("paper:2024-9999.00001-unrelated-noise-one", "Unrelated noise paper one"),
            _item("paper:2024-9999.00002-unrelated-noise-two", "Unrelated noise paper two"),
        ]
        a = _item("paper:2023-2307.14693-deep-learning-retrieval-of-hhg-spectra",
                  "Deep learning retrieval of high harmonic spectra")
        b = _item("paper:2021-2104.07366-deep-learning-retrieval-of-hhg-spectra",
                  "Deep learning retrieval of high harmonic spectra")
        reg = {"clusters": [], "orphans": noise + [a, b]}
        self.assert_eq(C.dedup_orphans(reg), 0, "非白名单编号不同组不归并")
        self.assert_eq(len(reg["orphans"]), 4, "四条记录全部保留")
        self.assert_true(all(not o.get("needs_review") for o in reg["orphans"]),
                         "未归并组不打 needs_review")

    def run_tests(self):
        self._test_paper_key_arxiv_variants()
        self._test_paper_key_doi_priority()
        self._test_paper_key_title_normalized()
        self._test_three_records_two_unique_not_formed()
        self._test_three_unique_formed()
        self._test_dedup_switch_off_record_counting()
        self._test_new_gate_prefers_unique_paper_count()
        self._test_large_group_split()
        self._test_split_switch_on_off()
        self._test_cross_domain_marked_not_dropped()
        self._test_strong_field_cluster_not_cross_domain()
        self._test_cross_domain_member_filter()
        self._test_filtered_below_three_not_new()
        self._test_normal_cluster_unfiltered()
        self._test_filtered_dedup_counts_unique()
        self._test_orphan_pool_dedup()
        self._test_orphan_dedup_switch_off()
        self._test_anonymous_orphans_not_merged()
        self._test_year_typo_merge_with_review_mark()
        self._test_different_ids_not_merged()
        self._test_confirmed_pair_merged_newer_metadata()
        self._test_confirmed_pair_nonzero_index()
        self._test_different_ids_nonzero_index_not_merged()
        self._test_orphan_aging_downweight_not_excluded()
        self._test_orphan_archive_not_deleted()
        self._test_archived_pool_still_searchable()
        self._test_orphan_aging_switch_off()


if __name__ == "__main__":
    suite = ClusterPaperIdentityTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    failed = [r for r in suite.results if not r.passed]
    for r in suite.results:
        print(("✓" if r.passed else "✗"), r.name, r.msg)
    sys.exit(1 if failed else 0)

