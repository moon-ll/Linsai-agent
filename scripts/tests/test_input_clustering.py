#!/usr/bin/env python3
"""
test_input_clustering.py — 知识簇链路回归测试（v6.9.12）

覆盖四点设计需求的落地：
    1. 源甄别：已提炼论文排除 + tier 分层（聚类质量来源）
    2. 聚类提炼：增量归簇（沿已有类融入）+ 单篇不成簇 + orphans 生命周期
    3. 课题判断：全阶段课题匹配 + archived → expansion / 活跃 → merge
    4. 防冗余：新簇查重（与 linked/closed 簇过近不开新簇）

注意：不调用 LLM（topic_match 的 LLM 仲裁路径用 stub 或走 Jaccard
回退分支），运行于隔离临时目录。
"""

import sys
import json
import shutil
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class InputClusteringTests(TestSuite):
    def __init__(self):
        super().__init__("知识簇链路测试（v6.9.12）")
        self.tmp_root = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            _write_json(self.tmp_root / "memory" / "nsfc-standards.json",
                        json.loads(standards_src.read_text(encoding="utf-8")))

        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("weekend_pipeline") or mod_name.startswith("proposal_lifecycle"):
                del sys.modules[mod_name]

        import paths
        self._orig_project_root = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root

        import proposal_lifecycle.constants as plc
        plc.PROJECT_ROOT = self.tmp_root
        plc.PROPOSALS_ROOT = self.tmp_root / "research_proposals"

        self.wp_mod = importlib.import_module("weekend_pipeline")
        patch_module_root("weekend_pipeline", self.tmp_root)
        patch_module_root("proposal_lifecycle", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    # ------------------------------------------------------------------
    # 需求 1：源甄别
    # ------------------------------------------------------------------

    def _test_distilled_papers_excluded(self):
        """已蒸馏成 wiki 页的论文不再作为聚类源。"""
        from weekend_pipeline import sources as src_mod

        wiki_dir = self.tmp_root / "knowledge" / "wiki" / "papers"
        _write_json
        (wiki_dir / "2501.00001.md").parent.mkdir(parents=True, exist_ok=True)
        (wiki_dir / "2501.00001.md").write_text(
            '---\ntitle: "A"\ntype: "papers"\narxiv_id: "2501.00001"\n---\n正文', encoding="utf-8")

        ids = src_mod.distilled_paper_ids()
        self.assert_true("2501.00001" in ids, "wiki 页 stem 应进已提炼集合")

        # collect_all_sources 排除路径
        orig_pool = src_mod.collect_paper_pool
        src_mod.collect_paper_pool = lambda limit=20, state=None: [
            {"source_id": "paper:2501.00001", "type": "paper", "text": "已提炼"},
            {"source_id": "paper:2501.00002", "type": "paper", "text": "新论文"},
        ]
        src_mod.collect_briefings = lambda days=7, state=None: []
        src_mod.collect_captures = lambda limit=10: []
        src_mod.collect_reference_notes = lambda: []
        src_mod.collect_kb_concepts_and_methods = lambda state=None: {}
        try:
            result = src_mod.collect_all_sources(state=None)
            sids = [s["source_id"] for s in result["papers"]]
            self.assert_in("paper:2501.00002", sids, "未提炼论文应保留")
            self.assert_true("paper:2501.00001" not in sids, "已提炼论文应被排除")
            self.assert_eq(result.get("distilled_excluded"), 1, "排除计数应正确")
        finally:
            src_mod.collect_paper_pool = orig_pool

    def _test_source_tiers_assigned(self):
        """tier 分层：paper=1 / briefing=2 / capture=3 / note=3。"""
        from weekend_pipeline import sources as src_mod

        src_mod.collect_paper_pool = lambda limit=20, state=None: [
            {"source_id": "paper:x", "type": "paper", "text": "t"}]
        src_mod.collect_briefings = lambda days=7, state=None: [
            {"source_id": "briefing:x", "type": "briefing", "text": "t"}]
        src_mod.collect_captures = lambda limit=10: [
            {"source_id": "capture:x", "type": "capture", "text": "t"}]
        src_mod.collect_reference_notes = lambda: [
            {"source_id": "note:x", "type": "note", "text": "t"}]
        src_mod.collect_kb_concepts_and_methods = lambda state=None: {}

        result = src_mod.collect_all_sources(state=None)
        tiers = {s["source_id"].split(":")[0]: s.get("tier") for s in
                 result["papers"] + result["briefings"] + result["captures"] + result["reference_notes"]}
        self.assert_eq(tiers.get("paper"), 1, "paper 应为 tier 1")
        self.assert_eq(tiers.get("briefing"), 2, "briefing 应为 tier 2")
        self.assert_eq(tiers.get("capture"), 3, "capture 应为 tier 3")
        self.assert_eq(tiers.get("note"), 3, "note 应为 tier 3")

    # ------------------------------------------------------------------
    # 需求 2+4：增量归簇 + 防冗余
    # ------------------------------------------------------------------

    def _mk_summary(self, sid: str, title: str, keywords) -> dict:
        return {"source_id": sid, "title": title, "summary": f"{title} 摘要", "keywords": keywords}

    def _test_incremental_assign_to_existing_cluster(self):
        """新摘要与已有 open 簇相似 → 沿已有类融入（不开新簇）。"""
        from weekend_pipeline import clusters as cl

        registry = {"clusters": [{
            "cluster_id": "cl_exist", "title": "twisted moiré HHG",
            "keywords": ["moire", "HHG", "twisted", "harmonic"],
            "summary": "", "member_source_ids": ["paper:a"],
            "member_summaries": [], "status": "open",
            "linked_proposal_id": None, "created_at": "2026-08-01T00:00:00Z",
            "updated_at": "2026-08-01T00:00:00Z",
        }], "orphans": []}

        new_items = [
            self._mk_summary("paper:b", "moiré harmonic generation", ["moire", "HHG", "harmonic"]),
            self._mk_summary("paper:c", "topological superconductor", ["topological", "superconductor"]),
        ]
        result = cl.assign_summaries(new_items, registry)

        self.assert_eq(len(result["assigned"]), 1, "相似条目应归入已有簇")
        self.assert_eq(result["assigned"][0]["cluster_id"], "cl_exist", "应归入 cl_exist")
        cluster = registry["clusters"][0]
        self.assert_in("paper:b", cluster["member_source_ids"], "成员应追加")
        self.assert_eq(len(registry["clusters"]), 1, "不应新开簇")
        self.assert_eq(len(registry["orphans"]), 1, "不相似条目应挂 orphan")
        self.assert_eq(registry["orphans"][0]["source_id"], "paper:c", "orphan 应为 paper:c")

    def _test_single_item_does_not_form_cluster(self):
        """单篇不成簇（防冗余：避免每篇文献各开一个类）。"""
        from weekend_pipeline import clusters as cl

        registry = {"clusters": [], "orphans": []}
        cl.assign_summaries(
            [self._mk_summary("paper:x", "lone topic", ["lone"])], registry)
        formed = cl.form_new_clusters(registry)
        self.assert_eq(len(formed), 0, "单篇不成簇")
        self.assert_eq(len(registry["orphans"]), 1, "应保留在 orphans")

    def _test_two_similar_items_form_cluster(self):
        """两篇相似 orphan → 成新簇。"""
        from weekend_pipeline import clusters as cl

        registry = {"clusters": [], "orphans": []}
        cl.assign_summaries([
            self._mk_summary("paper:a", "attosecond HHG in solids", ["attosecond", "HHG", "solid"]),
            self._mk_summary("paper:b", "solid-state harmonic cutoff", ["HHG", "solid", "cutoff"]),
        ], registry)
        formed = cl.form_new_clusters(registry)
        self.assert_eq(len(formed), 1, "两篇相似应成 1 簇")
        self.assert_eq(len(formed[0]["member_source_ids"]), 2, "簇成员应为 2")

    def _test_new_cluster_dedup_against_existing(self):
        """新团与已有簇过近 → 不开新簇（防换皮重开）。"""
        from weekend_pipeline import clusters as cl

        registry = {"clusters": [{
            "cluster_id": "cl_old", "title": "HHG in solids",
            "keywords": ["HHG", "solid", "harmonic", "cutoff"],
            "summary": "", "member_source_ids": [], "member_summaries": [],
            "status": "linked", "linked_proposal_id": "p1",
            "created_at": "2026-07-01T00:00:00Z", "updated_at": "2026-07-01T00:00:00Z",
        }], "orphans": []}
        cl.assign_summaries([
            self._mk_summary("paper:a", "HHG solid cutoff extension", ["HHG", "solid", "cutoff", "extension"]),
            self._mk_summary("paper:b", "harmonic solid phase", ["HHG", "solid", "harmonic", "phase"]),
        ], registry)
        formed = cl.form_new_clusters(registry)
        self.assert_eq(len(formed), 0, "与已有簇过近的团不应开新簇")
        self.assert_eq(len(registry["orphans"]), 2, "团员应退回 orphans")

    def _test_stale_cluster_closed(self):
        """open 簇 4 周无更新 → closed（不再吸收新成员）。"""
        from weekend_pipeline import clusters as cl

        registry = {"clusters": [{
            "cluster_id": "cl_stale", "title": "old", "keywords": ["old"],
            "summary": "", "member_source_ids": [], "member_summaries": [],
            "status": "open", "linked_proposal_id": None,
            "created_at": "2026-06-01T00:00:00Z", "updated_at": "2026-06-01T00:00:00Z",
        }], "orphans": []}
        closed = cl.close_stale_clusters(registry)
        self.assert_eq(closed, 1, "陈旧簇应被关闭")
        self.assert_eq(registry["clusters"][0]["status"], "closed", "状态应为 closed")

        # closed 簇不吸收新成员
        result = cl.assign_summaries(
            [self._mk_summary("paper:n", "old topic", ["old"])], registry)
        self.assert_eq(len(result["assigned"]), 0, "closed 簇不应吸收成员")

    # ------------------------------------------------------------------
    # 需求 3：课题判断（全阶段）
    # ------------------------------------------------------------------

    def _seed_lifecycle(self, proposals: dict) -> None:
        _write_json(self.tmp_root / "research_proposals" / "_lifecycle.json",
                    {"proposals": proposals})
        for pid, meta in proposals.items():
            stage_dir = self.tmp_root / "research_proposals" / meta["status"] / pid
            (stage_dir / "00_proposal-brief.md").parent.mkdir(parents=True, exist_ok=True)
            (stage_dir / "00_proposal-brief.md").write_text(
                f"# {meta.get('title', pid)}\n\n{meta.get('text', '')}", encoding="utf-8")

    def _test_topic_match_all_stages(self):
        """活跃课题高置信 → merge；archived 高置信 → expansion；无匹配 → LLM 不可用回退 new。"""
        from weekend_pipeline import input_jobs

        self._seed_lifecycle({
            "general-active-20260101": {"status": "optimizing",
                "title": "twisted moiré high harmonic",
                "text": "moire HHG twisted harmonic generation in solids"},
            "general-arch-20260102": {"status": "archived",
                "title": "attosecond dynamics solid",
                "text": "attosecond electron dynamics in solid state materials"},
        })

        registry = {"clusters": [
            {"cluster_id": "cl_a", "title": "twisted moiré harmonic generation",
             "keywords": ["moire", "HHG", "twisted", "harmonic"], "summary": "moire HHG",
             "member_source_ids": [], "member_summaries": [], "status": "open",
             "linked_proposal_id": None, "created_at": "2026-08-01T00:00:00Z",
             "updated_at": "2026-08-10T00:00:00Z"},
            {"cluster_id": "cl_b", "title": "attosecond electron dynamics",
             "keywords": ["attosecond", "dynamics", "solid", "electron"], "summary": "attosecond dynamics",
             "member_source_ids": [], "member_summaries": [], "status": "open",
             "linked_proposal_id": None, "created_at": "2026-08-01T00:00:00Z",
             "updated_at": "2026-08-10T00:00:00Z"},
            {"cluster_id": "cl_c", "title": "quantum error correction codes",
             "keywords": ["quantum", "error", "correction", "codes"], "summary": "QEC",
             "member_source_ids": [], "member_summaries": [], "status": "open",
             "linked_proposal_id": None, "created_at": "2026-08-01T00:00:00Z",
             "updated_at": "2026-08-10T00:00:00Z"},
        ], "orphans": []}

        from weekend_pipeline import clusters as cl
        cl.CLUSTERS_PATH = self.tmp_root / "memory" / "weekend-input" / "clusters.json"
        cl.save_clusters(registry)

        # LLM 不可用 → 纯 Jaccard 路径
        input_jobs.is_llm_available = lambda: False

        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        result = input_jobs.run_input_topic_match(state={}, job={})
        self.assert_true(result.get("success"), "topic_match 应成功", str(result))

        routes = json.loads((WEEKEND_INPUT_DIR / f"routes-{input_jobs.now_utc()[:10]}.json").read_text(encoding="utf-8"))["routes"]
        by_id = {r["cluster_id"]: r for r in routes}
        self.assert_eq(by_id["cl_a"]["action"], "merge", "活跃课题高置信应 merge")
        self.assert_eq(by_id["cl_a"]["target_id"], "general-active-20260101", "目标课题 id")
        self.assert_eq(by_id["cl_b"]["action"], "expansion", "archived 高置信应 expansion")
        self.assert_eq(by_id["cl_c"]["action"], "new", "无匹配应 new（LLM 不可用回退）")

    # ------------------------------------------------------------------
    # 链路结构：job 模板与废弃清理
    # ------------------------------------------------------------------

    def _test_job_template_chain(self):
        """新链 6 个 job、依赖顺序正确、废弃 job 从 state 清理。"""
        from weekend_pipeline.pipeline import WeekendPipeline
        from weekend_pipeline.constants import STAGE_INPUT

        p = WeekendPipeline(state_path=self.tmp_root / "memory" / "weekend-pipeline.json")
        # 预置旧 job 残留
        p.state.setdefault("jobs", []).append({
            "job_id": "input_gap_analysis", "stage": "input", "step": "analyze",
            "status": "done", "depends_on": [], "attempts": 1,
            "result": {}, "created_at": "2026-08-01T00:00:00Z", "finished_at": "2026-08-14T00:00:00Z",
        })
        p.sync_stage_jobs(STAGE_INPUT)

        ids = [j["job_id"] for j in p.list_jobs(stage="input")]
        expected = [
            "input_collect_sources", "input_summarize_new_papers",
            "input_cluster_assign", "input_cluster_distill",
            "input_topic_match", "input_compose_ideas",
        ]
        self.assert_eq(ids, expected, "input 链应为知识簇 6 job")
        self.assert_true("input_gap_analysis" not in ids, "废弃 job 应被清理")

        # handler 注册完整性：每个 (stage, step) 都有 handler
        for j in p.list_jobs(stage="input"):
            key = (j["stage"], j["step"])
            self.assert_in(key, p.handlers, f"{j['job_id']} 应有注册 handler")

    def run_tests(self):
        self._test_distilled_papers_excluded()
        self._test_source_tiers_assigned()
        self._test_incremental_assign_to_existing_cluster()
        self._test_single_item_does_not_form_cluster()
        self._test_two_similar_items_form_cluster()
        self._test_new_cluster_dedup_against_existing()
        self._test_stale_cluster_closed()
        self._test_topic_match_all_stages()
        self._test_job_template_chain()
