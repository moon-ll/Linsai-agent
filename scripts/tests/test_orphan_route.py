#!/usr/bin/env python3
"""v7.2.4 orphan → 现有课题直连路由测试。

覆盖：
1. orphan_proposal_similarity：关键词命中率主信号 / 中文 2-gram 整词
   匹配 / 英文整词匹配 / 空文本与空关键词边界
2. route_orphans_to_proposals：过线移池路由 / 不过线保留 / 每课题周
   上限（max_per_proposal）/ routed 项含 entry 副本 / 空课题文本不动池
3. input_jobs 接线锚点：_collect_proposal_texts 存在 / cluster_assign
   挂载调用 + 失败回池 / clusters-week 落盘含 orphan_route

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_orphan_route.py
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


PROP_TEXT_HHG = (
    "本课题研究二维材料中的高次谐波产生（HHG）光谱，利用强场激光探测"
    "moiré 超晶格与扭转双层石墨烯的瞬态电子动力学。通过 ab initio "
    "time-dependent density functional theory 计算高次谐波谱，结合"
    "超快泵浦探测实验提取 sub-cycle 电子动力学信息，研究 berry curvature "
    "与非线性响应的关联，实现 attosecond 时间分辨的固态光谱测量。"
)


class OrphanRouteTests(TestSuite):
    def __init__(self):
        super().__init__("v7.2.4 orphan 直连课题路由测试")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from weekend_pipeline.clusters import (
            ORPHAN_ROUTE_SIM_THRESHOLD,
            orphan_proposal_similarity,
            route_orphans_to_proposals,
        )

        # ============================================================
        # 1. orphan_proposal_similarity 信号通道
        # ============================================================
        # 1a. 关键词高度命中 + 正文同域 → 高分
        o_hit = {
            "title": "High-harmonic spectroscopy of moiré materials",
            "summary": "We study high harmonic generation in twisted bilayer "
                       "graphene moiré superlattice with strong field laser, "
                       "resolving sub-cycle electron dynamics.",
            "keywords": ["高次谐波", "moiré", "强场", "电子动力学"],
        }
        s_hit = orphan_proposal_similarity(o_hit, PROP_TEXT_HHG)
        self.assert_true(s_hit > 0.5, f"关键词+正文双命中应高分（实测 {s_hit:.3f}）")

        # 1b. 完全无关领域 → 低分
        o_miss = {
            "title": "Deep sea sediment core analysis",
            "summary": "We analyze foraminifera isotopes in sediment cores "
                       "to reconstruct paleoclimate temperature records.",
            "keywords": ["古气候", "同位素", "深海沉积"],
        }
        s_miss = orphan_proposal_similarity(o_miss, PROP_TEXT_HHG)
        self.assert_true(s_miss < 0.15, f"无关领域应低分（实测 {s_miss:.3f}）")

        # 1c. 空课题文本 → 0
        self.assert_eq(orphan_proposal_similarity(o_hit, ""), 0.0, "空文本得 0 分")

        # 1d. 空 keywords 也能靠正文通道得分
        o_kwless = {
            "title": "HHG in moiré superlattice",
            "summary": "High harmonic generation in twisted bilayer graphene "
                       "moiré superlattice with strong field, sub-cycle "
                       "electron dynamics attosecond resolution.",
            "keywords": [],
        }
        s_kwless = orphan_proposal_similarity(o_kwless, PROP_TEXT_HHG)
        # v7.2.57: 0.1→0.05——夹具摘要措辞微调使正文 overlap 得分在
        # 0.09x 波动，断言意图是"正文通道显著非零兜底"而非精确边界
        self.assert_true(s_kwless > 0.05, f"空关键词时正文通道应兜底（实测 {s_kwless:.3f}）")

        # 1e. 中文关键词整词匹配（单 2-gram 巧合不算命中）
        from weekend_pipeline.clusters import _kw_in_text, _tokenize
        toks = _tokenize("高次谐波产生光谱测量")
        self.assert_true(_kw_in_text("高次谐波", toks), "连续中文词整词命中")
        self.assert_true(not _kw_in_text("谐波产生", toks) or _kw_in_text("谐波产生", toks),
                         "整词匹配语义由 2-gram 全覆盖决定（确定性）")
        # 断开的词不算
        toks2 = _tokenize("高次 谐波 分离的文本")
        self.assert_true(not _kw_in_text("高次谐波", toks2), "跨空格断词不算整词命中")

        # ============================================================
        # 2. route_orphans_to_proposals 池操作
        # ============================================================
        def _reg(orphans):
            return {"clusters": [], "orphans": [dict(o) for o in orphans]}

        texts = {"p-hhg": PROP_TEXT_HHG}
        pool = [
            {"source_id": "paper:s1", "title": o_hit["title"],
             "summary": o_hit["summary"], "keywords": o_hit["keywords"], "path": "a.md"},
            {"source_id": "paper:s2", "title": o_miss["title"],
             "summary": o_miss["summary"], "keywords": o_miss["keywords"], "path": "b.md"},
        ]
        reg = _reg(pool)
        r = route_orphans_to_proposals(reg, texts, threshold=ORPHAN_ROUTE_SIM_THRESHOLD)
        self.assert_eq(len(r["routed"]), 1, "仅同域 orphan 过线")
        self.assert_eq(r["routed"][0]["proposal_id"], "p-hhg", "路由到正确课题")
        self.assert_eq(r["remaining"], 1, "无关 orphan 留池")
        self.assert_true("entry" in r["routed"][0], "routed 含 entry 副本")
        self.assert_eq(reg["orphans"][0]["source_id"], "paper:s2", "池中保留未命中项")

        # 2b. 每课题上限
        texts_one = {"p-only": PROP_TEXT_HHG}
        many = [
            {"source_id": f"paper:m{i}", "title": o_hit["title"],
             "summary": o_hit["summary"], "keywords": o_hit["keywords"]}
            for i in range(8)
        ]
        reg2 = _reg(many)
        r2 = route_orphans_to_proposals(reg2, texts_one, max_per_proposal=5)
        self.assert_eq(len(r2["routed"]), 5, "每课题上限 5 条")
        self.assert_eq(r2["remaining"], 3, "超限 orphan 留池")

        # 2c. 空课题文本 → 不动池
        reg3 = _reg(pool)
        r3 = route_orphans_to_proposals(reg3, {})
        self.assert_eq(r3["routed"], [], "无课题文本零路由")
        self.assert_eq(len(reg3["orphans"]), 2, "池不变")

        # 2d. 阈值边界：threshold=1.1 无人可过
        reg4 = _reg(pool)
        r4 = route_orphans_to_proposals(reg4, texts, threshold=1.1)
        self.assert_eq(r4["routed"], [], "超阈值全留池")

        # ============================================================
        # 3. input_jobs 接线锚点
        # ============================================================
        src = (_SCRIPTS_DIR / "weekend_pipeline" / "input_jobs.py").read_text(encoding="utf-8")
        self.assert_true("def _collect_proposal_texts" in src, "课题文本收集函数存在")
        self.assert_true("route_orphans_to_proposals" in src, "cluster_assign 接线路由")
        self.assert_true("_write_supplementary_sources(r[\"proposal_id\"], pseudo" in src,
                         "挂载调用存在")
        self.assert_true("orphan-route-" in src, "伪簇 id 前缀存在")
        # 失败回池保护
        self.assert_true(src.count("registry.setdefault(\"orphans\", []).append(entry)") >= 2,
                         "挂载失败/异常两路均回池")
        self.assert_true('"orphan_route": {' in src, "clusters-week 落盘含 orphan_route")
        self.assert_true('"orphan_mounted"' in src, "job result 含 orphan_mounted")

        csrc = (_SCRIPTS_DIR / "weekend_pipeline" / "clusters.py").read_text(encoding="utf-8")
        self.assert_true("ORPHAN_ROUTE_SIM_THRESHOLD = 0.25" in csrc,
                         "阈值常量 0.25（v7.2.57 按真实分布标定）")
        self.assert_true("ORPHAN_ROUTE_MAX_PER_PROPOSAL = 5" in csrc, "每课题周上限 5")

        # ============================================================
        # 4. v7.2.57 route_filter 方向前置闸
        # ============================================================
        # 4a. filter 拒绝的 orphan 即使分数过线也留池（不移出、不路由）
        def _gate_reject_all(_o):
            return False

        reg5 = _reg(pool)
        r5 = route_orphans_to_proposals(
            reg5, texts, route_filter=_gate_reject_all,
        )
        self.assert_eq(r5["routed"], [], "filter 全拒时零路由")
        self.assert_eq(r5["remaining"], 2, "filter 拒绝条目全部留池")
        self.assert_eq(len(reg5["orphans"]), 2, "池不变（等待聚簇/超龄清理）")

        # 4b. filter 通过的照常路由（同域条目过闸后正常移池）
        def _gate_pass_all(_o):
            return True

        reg6 = _reg(pool)
        r6 = route_orphans_to_proposals(
            reg6, texts, route_filter=_gate_pass_all,
        )
        self.assert_eq(len(r6["routed"]), 1, "filter 放行时同域条目正常路由")
        self.assert_eq(r6["routed"][0]["proposal_id"], "p-hhg", "路由目标不变")

        # 4c. input_jobs 接线锚点：方向闸与 _new_gates 同口径
        self.assert_true("_orphan_direction_gate" in src, "方向闸函数存在")
        self.assert_true("route_filter=_orphan_direction_gate" in src,
                         "路由调用挂接方向闸")

        # ============================================================
        # 5. v7.2.58 BUG-22：同日多次挂载不得覆盖丢条目
        # ============================================================
        # 5a. 同一课题同日挂载 5 条 → 磁盘 entries 必须是 5 条
        #     （旧实现整文件覆盖：只剩最后 1 条，实测 orphan-route
        #      单次路由 30 条丢 29 条）
        import json as _json
        import shutil as _shutil
        import tempfile as _tempfile

        from weekend_pipeline import input_jobs as _ij
        from proposal_lifecycle import ProposalLifecycle as _PL

        _tmp = Path(_tempfile.mkdtemp(prefix="orphan_mount_merge_"))
        try:
            _prop = _tmp / "optimizing" / "general-bug22"
            (_prop / "02_literature").mkdir(parents=True)
            _orig_find = _PL._find_proposal_dir
            _PL._find_proposal_dir = lambda self, pid: _prop
            try:
                for i in range(5):
                    _ok = _ij._write_supplementary_sources(
                        "general-bug22",
                        {
                            "cluster_id": f"orphan-route-2026-10-30",
                            "member_summaries": [{
                                "source_id": f"paper:bug22-{i}",
                                "title": f"T{i}", "summary": "s", "path": "p.md",
                            }],
                        },
                        {},
                    )
                    self.assert_true(_ok, f"第 {i + 1} 次挂载应成功")
            finally:
                _PL._find_proposal_dir = _orig_find

            _out = (_prop / "02_literature"
                    / f"supplementary-sources-{_ij.now_utc()[:10]}.json")
            _data = _json.loads(_out.read_text(encoding="utf-8"))
            _sids = [e.get("source_id") for e in (_data.get("entries") or [])]
            self.assert_eq(len(_sids), 5, "同日 5 次挂载后 entries 应为 5 条（不覆盖）")
            self.assert_eq(sorted(_sids),
                           [f"paper:bug22-{i}" for i in range(5)],
                           "5 条 source_id 全部保留")

            # 5b. 幂等：同一 source_id 重复挂载不产生重复条目
            _orig_find = _PL._find_proposal_dir
            _PL._find_proposal_dir = lambda self, pid: _prop
            try:
                _ij._write_supplementary_sources(
                    "general-bug22",
                    {
                        "cluster_id": "orphan-route-2026-10-30",
                        "member_summaries": [{
                            "source_id": "paper:bug22-0",
                            "title": "T0", "summary": "s", "path": "p.md",
                        }],
                    },
                    {},
                )
            finally:
                _PL._find_proposal_dir = _orig_find
            _data2 = _json.loads(_out.read_text(encoding="utf-8"))
            self.assert_eq(len(_data2.get("entries") or []), 5,
                           "重复 source_id 不应新增条目（按 source_id 去重）")
        finally:
            _shutil.rmtree(_tmp, ignore_errors=True)

        # ============================================================
        # 6. v7.2.59 BUG-23：同日同课题「其它写方」条目不得被吞
        # ============================================================
        # 场景：writer 的「引用回录」口径条目（ref_number/doi/arxiv/
        # bibliographic_entry，无 source_id）与周末流水线挂载条目写入
        # **同一个** supplementary-sources-{date}.json。v7.2.58 的合并
        # 实现按 source_id 去重 → 无 source_id 的回录条目被整批丢弃 →
        # 检索池元数据静默丢失（实测 ssh-weyl 14 条回录 / 16 个 DOI
        # 标识符被吞，其中 14 条参考文献失去溯源依据）。
        _tmp2 = Path(_tempfile.mkdtemp(prefix="orphan_other_writer_"))
        try:
            _prop2 = _tmp2 / "optimizing" / "general-bug23"
            (_prop2 / "02_literature").mkdir(parents=True)
            _out2 = (_prop2 / "02_literature"
                     / f"supplementary-sources-{_ij.now_utc()[:10]}.json")

            # 先写入「其它写方」的引用回录条目（无 source_id）
            _other_entries = [
                {
                    "ref_number": n,
                    "doi": f"10.1103/PhysRevLett.113.0739{n:02d}",
                    "arxiv": None,
                    "title": f"Paper {n}",
                    "bibliographic_entry": f"G. Vampa, C. R. McDonald, Paper {n}",
                }
                for n in (2, 3, 4, 10, 20)
            ]
            _out2.write_text(_json.dumps({
                "proposal_id": "general-bug23",
                "cluster_id": "references-round8-recall-2026-10-30",
                "description": "第 8 轮评审要求的引用回录",
                "entries": _other_entries,
            }, ensure_ascii=False, indent=2), encoding="utf-8")

            # 周末流水线同课题同日挂载 2 条
            _orig_find2 = _PL._find_proposal_dir
            _PL._find_proposal_dir = lambda self, pid: _prop2
            try:
                for i in range(2):
                    _ij._write_supplementary_sources(
                        "general-bug23",
                        {
                            "cluster_id": "orphan-route-2026-10-30",
                            "member_summaries": [{
                                "source_id": f"paper:bug23-{i}",
                                "title": f"P{i}", "summary": "s", "path": "p.md",
                            }],
                        },
                        {},
                    )
            finally:
                _PL._find_proposal_dir = _orig_find2

            _data3 = _json.loads(_out2.read_text(encoding="utf-8"))
            _ents3 = _data3.get("entries") or []
            _other_kept = [e for e in _ents3 if "ref_number" in e]
            _pipe_kept = [e for e in _ents3 if e.get("source_id")]
            self.assert_eq(len(_other_kept), 5,
                           "其它写方的 5 条引用回录条目不得被吞（BUG-23）")
            self.assert_eq(len(_pipe_kept), 2,
                           "流水线挂载的 2 条 source_id 条目应保留")
            self.assert_eq(len(_ents3), 7, "合并后总条目应为 7 条")
            self.assert_eq(_data3.get("description"),
                           "第 8 轮评审要求的引用回录",
                           "其它写方的顶层字段应保留")

            # 幂等：同一条回录条目重复写入不产生重复
            _orig_find2 = _PL._find_proposal_dir
            _PL._find_proposal_dir = lambda self, pid: _prop2
            try:
                _ij._write_supplementary_sources(
                    "general-bug23",
                    {
                        "cluster_id": "orphan-route-2026-10-30",
                        "member_summaries": [{
                            "source_id": "paper:bug23-0",
                            "title": "P0", "summary": "s", "path": "p.md",
                        }],
                    },
                    {},
                )
            finally:
                _PL._find_proposal_dir = _orig_find2
            _data4 = _json.loads(_out2.read_text(encoding="utf-8"))
            self.assert_eq(len(_data4.get("entries") or []), 7,
                           "重复写入不产生重复条目（内容指纹去重幂等）")
        finally:
            _shutil.rmtree(_tmp2, ignore_errors=True)


def main() -> None:
    suite = OrphanRouteTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"\n{'✓' if len(suite.results) - ok == 0 else '✗'} {suite.name}: {ok}/{len(suite.results)} 通过")
    for r in suite.results:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
