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

        # v6.9.18: 方向词表隔离（防 scope 过滤读真实仓库文件；夹具论文
        # 一律含 hhg/高次谐波 以命中词表）
        _write_json(self.tmp_root / "memory" / "weekend-input" / "scope-terms.json",
                    {"terms": ["hhg", "高次谐波"]})

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
            {"source_id": "paper:2501.00001", "type": "paper", "title": "HHG distilled", "text": "已提炼 HHG"},
            {"source_id": "paper:2501.00002", "type": "paper", "title": "HHG new", "text": "新论文 HHG"},
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
            {"source_id": "paper:x", "type": "paper", "title": "HHG paper", "text": "HHG 高次谐波研究内容"}]
        src_mod.collect_briefings = lambda days=7, state=None: [
            {"source_id": "briefing:x", "type": "briefing", "text": "今日精选 arXiv 论文若干条，" + "固体高次谐波研究进展条目。" * 30}]
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
        """成簇门槛 3 篇（v6.9.18：两篇凑数簇是 08-16 实测乱聚主源）。"""
        from weekend_pipeline import clusters as cl

        registry = {"clusters": [], "orphans": []}
        cl.assign_summaries([
            self._mk_summary("paper:a", "attosecond HHG in solids", ["attosecond", "HHG", "solid"]),
            self._mk_summary("paper:b", "solid-state harmonic cutoff", ["HHG", "solid", "cutoff"]),
        ], registry)
        formed = cl.form_new_clusters(registry)
        self.assert_eq(len(formed), 0, "两篇相似不成簇（MIN_CLUSTER_MEMBERS=3）")
        self.assert_eq(len(registry["orphans"]), 2, "应留在 orphans 等凑第三篇")

        cl.assign_summaries([
            self._mk_summary("paper:c", "harmonic generation solid dynamics", ["HHG", "solid", "dynamics"]),
        ], registry)
        formed = cl.form_new_clusters(registry)
        self.assert_eq(len(formed), 1, "第三篇到位应成 1 簇")
        self.assert_eq(len(formed[0]["member_source_ids"]), 3, "簇成员应为 3")
        # v6.9.18: 簇标题来自团内共享关键词，不再是种子论文标题
        self.assert_true(
            "hhg" in formed[0]["title"].lower() or "solid" in formed[0]["title"].lower(),
            f"簇标题应含共享关键词: {formed[0]['title']}",
        )

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
            self._mk_summary("paper:c", "solid harmonic dynamics", ["HHG", "solid", "harmonic", "dynamics"]),
        ], registry)
        formed = cl.form_new_clusters(registry)
        self.assert_eq(len(formed), 0, "与已有簇过近的团不应开新簇")
        self.assert_eq(len(registry["orphans"]), 3, "团员应退回 orphans")

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
        """活跃课题高置信 → merge；archived 高置信 → expansion；弱簇 → defer；达标簇 → new（v6.9.18 门槛）。"""
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
            # v6.9.18: 达标簇——3 成员 + LLM 知识卡 + 方向相关 + 不重叠 → new
            {"cluster_id": "cl_d", "title": "squeezed light driven HHG photon statistics",
             "keywords": ["squeezed", "hhg", "photon", "statistics"], "summary": "squeezed HHG quantum optics",
             "member_source_ids": ["paper:d1", "paper:d2", "paper:d3"], "member_summaries": [],
             "distilled_by": "llm", "status": "open", "linked_proposal_id": None,
             "created_at": "2026-08-01T00:00:00Z", "updated_at": "2026-08-10T00:00:00Z"},
        ], "orphans": []}

        from weekend_pipeline import clusters as cl
        cl.CLUSTERS_PATH = self.tmp_root / "memory" / "weekend-input" / "clusters.json"
        cl.save_clusters(registry)

        # LLM 不可用 → 纯 Jaccard 路径（new 回退也要过门槛）
        input_jobs.is_llm_available = lambda: False

        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        result = input_jobs.run_input_topic_match(state={}, job={})
        self.assert_true(result.get("success"), "topic_match 应成功", str(result))

        routes = json.loads((WEEKEND_INPUT_DIR / f"routes-{input_jobs.now_utc()[:10]}.json").read_text(encoding="utf-8"))["routes"]
        by_id = {r["cluster_id"]: r for r in routes}
        self.assert_eq(by_id["cl_a"]["action"], "merge", "活跃课题高置信应 merge")
        self.assert_eq(by_id["cl_a"]["target_id"], "general-active-20260101", "目标课题 id")
        self.assert_eq(by_id["cl_b"]["action"], "expansion", "archived 高置信应 expansion")
        self.assert_eq(by_id["cl_c"]["action"], "defer", "无成员弱簇应 defer（不再泛滥 new）")
        self.assert_eq(by_id["cl_d"]["action"], "new", "达标簇（3 成员+LLM 卡+方向相关）应 new")

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

    # ------------------------------------------------------------------
    # 故障防线：LLM 全挂不空转
    # ------------------------------------------------------------------

    def _test_summarize_llm_failure_not_silent(self):
        """有新料但 LLM 全挂 → success=False 且不标记已处理（防空转 done）。"""
        from weekend_pipeline import input_jobs, sources as src_mod

        # 伪造 collect：2 篇新料
        orig = (src_mod.collect_paper_pool, src_mod.collect_briefings,
                src_mod.collect_captures, src_mod.collect_reference_notes,
                src_mod.collect_kb_concepts_and_methods,
                input_jobs.is_llm_available, input_jobs._llm_json)
        src_mod.collect_paper_pool = lambda limit=20, state=None: [
            {"source_id": "paper:p1", "type": "paper", "title": "HHG 论文一", "text": "论文一 HHG", "tier": 1},
            {"source_id": "paper:p2", "type": "paper", "title": "HHG 论文二", "text": "论文二 HHG", "tier": 1},
        ]
        src_mod.collect_briefings = lambda days=7, state=None: []
        src_mod.collect_captures = lambda limit=10: []
        src_mod.collect_reference_notes = lambda: []
        src_mod.collect_kb_concepts_and_methods = lambda state=None: {}

        # LLM 可用但全部调用失败
        input_jobs.is_llm_available = lambda: True
        input_jobs._llm_json = lambda system, user, timeout=120: None

        try:
            state = {"processed_sources": {}}
            result = input_jobs.run_input_summarize(state=state, job={})

            self.assert_true(not result.get("success"), "LLM 全挂应返回 success=False")
            self.assert_true(
                not any(sid.startswith("paper:") for sid in state["processed_sources"]),
                "失败来源不得标记已处理（保数据待重试）",
            )
        finally:
            (src_mod.collect_paper_pool, src_mod.collect_briefings,
             src_mod.collect_captures, src_mod.collect_reference_notes,
             src_mod.collect_kb_concepts_and_methods,
             input_jobs.is_llm_available, input_jobs._llm_json) = orig

    # ------------------------------------------------------------------
    # v6.9.14: GLM 主模型路由（weekend_input 任务标签）
    # ------------------------------------------------------------------

    def _test_weekend_input_prefers_glm(self):
        """weekend_input 标签应把 glm/glm-fallback 提到队首，其余顺序不变。"""
        import llm_router

        prefs = llm_router.TASK_PROVIDER_PREFS
        self.assert_eq(
            prefs.get("weekend_input"), ("glm", "glm-fallback"),
            "weekend_input 标签应注册 GLM 偏好",
        )

        # 模拟全局优先级链：minimax(1) → minimax-fallback(2) → glm(3) → glm-fallback(4)
        chain = [
            llm_router.LLMProvider({"name": "minimax", "type": "api", "priority": 1,
                                    "base_url": "http://x", "api_key": "k", "model": "m"}),
            llm_router.LLMProvider({"name": "minimax-fallback", "type": "api", "priority": 2,
                                    "base_url": "http://x", "api_key": "k", "model": "m"}),
            llm_router.LLMProvider({"name": "glm", "type": "api", "priority": 3,
                                    "base_url": "http://x", "api_key": "k", "model": "glm-5.3"}),
            llm_router.LLMProvider({"name": "glm-fallback", "type": "api", "priority": 4,
                                    "base_url": "http://x", "api_key": "k", "model": "glm-5.2"}),
        ]
        ordered = llm_router._apply_task_preference(list(chain), "weekend_input")
        self.assert_eq(ordered[0].name, "glm", "weekend_input 主模型应为 glm")
        self.assert_eq(
            [p.name for p in ordered], ["glm", "minimax", "minimax-fallback", "glm-fallback"],
            "偏好重排应保持其余相对顺序（稳定排序）",
        )
        # 未注册标签原样返回
        self.assert_eq(
            [p.name for p in llm_router._apply_task_preference(list(chain), "no-such-tag")],
            [p.name for p in chain],
            "未注册标签不应改变顺序",
        )

    def _test_llm_json_passes_prefer_tag(self):
        """_llm_json 默认传 prefer=weekend_input；显式 None 恢复全局策略。"""
        from weekend_pipeline import input_jobs

        captured = {}
        orig = (input_jobs.is_llm_available, input_jobs.llm_complete)

        def fake_llm_complete(system, user, timeout=60, prefer=None):
            captured["prefer"] = prefer
            return True, '{"ok": 1}', {}

        input_jobs.is_llm_available = lambda: True
        input_jobs.llm_complete = fake_llm_complete

        try:
            input_jobs._llm_json("s", "u")
            self.assert_eq(captured.get("prefer"), "weekend_input", "默认应传 weekend_input 标签")

            input_jobs._llm_json("s", "u", prefer=None)
            self.assert_true(captured.get("prefer") is None, "显式 None 应恢复全局策略")
        finally:
            (input_jobs.is_llm_available, input_jobs.llm_complete) = orig

    # ------------------------------------------------------------------
    # v6.9.14: 关键词归一化 + overlap 相似度（聚类稀疏词表校准）
    # ------------------------------------------------------------------

    def _test_keyword_normalization(self):
        """括注同义词应归一为同一集合成员；摄取时去重截断。"""
        from weekend_pipeline.clusters import norm_keyword, kw_set
        from weekend_pipeline import input_jobs

        self.assert_eq(norm_keyword("高次谐波产生 (HHG)"), "高次谐波产生", "英文括注应剥离")
        self.assert_eq(norm_keyword("二次谐波产生（SHG）"), "二次谐波产生", "中文括注应剥离")
        self.assert_eq(norm_keyword("  Berry Phase "), "berry phase", "应去空白转小写")
        self.assert_eq(
            len(kw_set(["高次谐波产生", "高次谐波产生 (HHG)", "强场物理"])),
            2, "同义不同形应去重为 2 个",
        )

        # 摄取归一化：_coerce_summary_data 应清洗 LLM 输出的关键词
        paper = {"source_id": "paper:n1", "title": "t", "path": "p", "tier": 1}
        data = input_jobs._coerce_summary_data(
            {"title": "t", "summary": "s",
             "keywords": ["高次谐波产生 (HHG)", "高次谐波产生", "强场物理", ""]},
            paper,
        )
        self.assert_eq(data["keywords"], ["高次谐波产生", "强场物理"], "摄取关键词应归一去空去重")

    def _test_sparse_overlap_forms_cluster(self):
        """稀疏关键词（共享 2/5）在 overlap 口径下成簇，Jaccard 口径不成。

        08-15 实测标定：5 词关键词摘要 435 对最高 Jaccard 0.161 < 0.30
        成簇阈值，簇零形成。overlap（|∩|/min）对短集合公平——本用例
        共享 2 个核心词 + 标题共享 2 token，组合分应过 0.30。
        """
        from weekend_pipeline import clusters as cl

        # Jaccard 口径：2/8 并集 * 0.7 + 标题 2/6 * 0.3 = 0.275 < 0.30
        # overlap 口径：2/5 较小集 * 0.7 + 标题 0.333 * 0.3 ≈ 0.38 ≥ 0.30
        registry = {"clusters": [], "orphans": []}
        cl.assign_summaries([
            self._mk_summary(
                "paper:a", "high harmonic generation solids",
                ["固态高次谐波", "强场物理", "偶次谐波", "反演对称性破缺", "非平衡稳态"]),
            self._mk_summary(
                "paper:b", "harmonic generation solid state",
                ["固态高次谐波", "强场物理", "晶体对称性", "weyl 节点", "berry 相位"]),
            self._mk_summary(
                "paper:c", "harmonic solids ultrafast",
                ["固态高次谐波", "强场物理", "超快探测", "载流子动力学", "能带拓扑"]),
        ], registry)
        self.assert_eq(len(registry["orphans"]), 3, "三篇均应先挂 orphans")
        formed = cl.form_new_clusters(registry)
        self.assert_eq(len(formed), 1, "共享 2 核心词+领域标签应成簇（overlap 口径 + 3 成员门槛）")
        if formed:
            self.assert_true(
                {"固态高次谐波", "强场物理"}.issubset(set(formed[0]["keywords"])),
                "簇关键词应含归一化后的共享领域词",
            )

    def _test_enrich_appends_without_crash(self):
        """enrich_from_idea 对已有内容的课题不崩溃（registration re 导入回归）。

        08-15 实测：registration.py 使用 re 未导入，compose 的 merge 路由
        落地时在 _sentence_similarity 处 NameError 中断。此前测试的目标
        课题文件均为空/不存在，早退于去重路径之前，未覆盖该分支。
        """
        from proposal_lifecycle import ProposalLifecycle

        self._seed_lifecycle({
            "general-live-20260101": {"status": "optimizing",
                "title": "quantum hhg theory", "text": "quantum description high harmonic"},
        })
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / "general-live-20260101"
        (prop_dir / "01_direction").mkdir(parents=True, exist_ok=True)
        (prop_dir / "01_direction" / "direction-calibration.md").write_text(
            "# 方向校准\n\n已有研究背景句子超过十个字符长度，用于触发句子相似度计算路径。\n",
            encoding="utf-8",
        )
        # v6.9.16 修复：enrich_from_idea 还会向 02_topic / 03_question / 04_proposal 追加，
        # 生产课题必有完整阶段骨架，夹具此前只建 01_direction 导致
        # _deduplicate_append open("a") FileNotFoundError，整套件被静默吞掉。
        for stage in ("02_topic", "03_question", "04_proposal"):
            (prop_dir / stage).mkdir(parents=True, exist_ok=True)

        lc = ProposalLifecycle()
        idea = {
            "title": "全量子 HHG 描述",
            "background": "全新背景内容：高次谐波产生的全量子理论描述甲乙丙丁。",
            "gap": "电子离子辐射场纠缠的测量诱导效应尚缺统一刻画。",
            "content": ["纠缠动力学刻画", "测量诱导退相干"],
            "innovations": ["全量子三步模型"],
            "sources": [],
            "reliability": "derived",
        }
        result = lc.enrich_from_idea("general-live-20260101", idea)
        self.assert_true(result.get("success"), "enrich 应成功", str(result))

        # 重复注入同一 idea → 句级去重生效，仍成功且不重复追加
        again = lc.enrich_from_idea("general-live-20260101", idea)
        self.assert_true(again.get("success"), "重复 enrich 应成功", str(again))
        content = (prop_dir / "01_direction" / "direction-calibration.md").read_text(encoding="utf-8")
        self.assert_eq(
            content.count("周末输入补充"), 1, "同 idea 重复注入应去重为一次",
        )

    def _test_register_generates_valid_id(self):
        """register_from_idea → generate_proposal_id 全链不崩溃（naming 导入回归）。

        08-16 实测：naming.py 使用 LIFECYCLE_STAGES 未导入，compose 的
        new 路由（课题注册）在 ID 生成处 NameError 中断。既有测试未走
        register_from_idea 的 ID 生成分支（需真实 state 目录）。
        """
        from proposal_lifecycle import ProposalLifecycle

        self._seed_lifecycle({})
        lc = ProposalLifecycle()
        idea = {
            "title": "二维材料非线性霍尔效应",
            "background": "背景内容甲乙丙丁戊己庚辛。",
            "gap": "现有手段无法分辨内禀与外禀贡献。",
            "content": ["非线性霍尔系数测量", "对称性调控"],
            "innovations": ["温度依赖分离方案"],
            "sources": [],
            "reliability": "derived",
        }
        r = lc.register_from_idea(idea, project_type="general")
        self.assert_true(r.get("success"), "注册应成功", str(r))
        pid = r.get("proposal_id", "")
        self.assert_true(pid.startswith("general-"), f"ID 应带类型前缀: {pid}")
        # ID 符合命名规则（类型-名称-日期）
        import re as _re
        self.assert_true(
            _re.match(r"^general-[a-z0-9-]+-\d{8}$", pid),
            f"ID 应符合命名规则: {pid}",
        )

    def _test_register_cn_title_falls_back_to_keywords(self):
        """中文标题注册：取名回退到 keywords 英文词（v6.9.16 命名回归）。

        08-16 批处理实测：46+ 纯中文标题课题经 safe_filename+ASCII
        过滤后取空，回退 "new-idea-N" 占位名。修复后应从 idea.keywords
        取英文词组合命名。
        """
        from proposal_lifecycle import ProposalLifecycle

        self._seed_lifecycle({})
        lc = ProposalLifecycle()
        idea = {
            "title": "维格纳晶体非线性光学响应",
            "background": "背景内容甲乙丙丁。",
            "gap": "高温相变动力学缺乏统一图像。",
            "content": ["时间分辨测量"],
            "innovations": ["非平衡诊断"],
            "sources": [],
            "keywords": ["维格纳晶体", "Wigner Crystal", "THz", "非线性光学"],
            "reliability": "derived",
        }
        r = lc.register_from_idea(idea, project_type="general")
        self.assert_true(r.get("success"), "注册应成功", str(r))
        pid = r.get("proposal_id", "")
        # keywords 英文词按序拼接：wigner-crystal-thz
        self.assert_true(
            "wigner-crystal-thz" in pid,
            f"中文标题应回退到 keywords 英文词命名: {pid}",
        )
        self.assert_true(
            "new-idea" not in pid, f"不应回退占位名: {pid}",
        )

    # ------------------------------------------------------------------
    # v6.9.18 输入链路重构回归
    # ------------------------------------------------------------------

    def _test_cluster_ids_unique(self):
        """同批创建大量簇时 ID 不碰撞（旧 id(object()) seed 高频复用）。"""
        from weekend_pipeline import clusters as cl

        ids = set()
        for round_i in range(50):
            registry = {"clusters": [], "orphans": []}
            # 三组主题关键词完全不相交 → 各自成簇
            for g, base in enumerate(["hhg", "attosecond", "wigner"]):
                cl.assign_summaries([
                    self._mk_summary(f"paper:{round_i}-{g}-{k}", f"{base} study {k}",
                                     [base, f"{base}core"])
                    for k in range(3)
                ], registry)
            formed = cl.form_new_clusters(registry)
            for c in formed:
                ids.add(c["cluster_id"])
        # 每轮 3 簇（组间关键词不重叠，不会互相查重合并）
        self.assert_eq(len(ids), 150, f"50 轮 × 3 簇 ID 应全部唯一，实际 {len(ids)}")

    def _test_cn_2gram_title_similarity(self):
        """中文标题 2-gram 相似度生效（旧整句切分口径对中文恒近 0）。

        item_similarity 的标题分量权重 0.3，无关键词时总分上限 0.3；
        同主题中文标题共享 6 个 2-gram（jaccard≈0.35 → 总分≈0.10），
        无关标题 2-gram 零交集（总分 0）。
        """
        from weekend_pipeline import clusters as cl

        a = {"title": "固体高次谐波的产生机制研究", "keywords": []}
        b = {"title": "固体高次谐波的探测新方案", "keywords": []}
        c = {"title": "无线通信波束成形优化", "keywords": []}
        sim_ab = cl.item_similarity(a, b)
        sim_ac = cl.item_similarity(a, c)
        self.assert_true(sim_ab > 0.09, f"同主题中文标题相似度应显著: {sim_ab:.3f}")
        self.assert_true(sim_ac < 0.01, f"无关中文标题相似度应近 0: {sim_ac:.3f}")

    def _test_scope_and_ops_filters(self):
        """方向词表过滤跨领域论文；运维简报过滤空/运维内容。"""
        from weekend_pipeline import sources as src

        # scope_hit：领域内命中、领域外不命中
        self.assert_true(src.scope_hit("HHG in ZnO semiconductors", ["高次谐波", "hhg"]) == "hhg",
                         "HHG 论文应命中词表")
        self.assert_true(
            src.scope_hit("High harmonic generation in ZnO", ["高次谐波", "hhg", "high harmonic"]) == "high harmonic",
            "全称论文应命中多词词表")
        self.assert_true(src.scope_hit("6G sub-THz leaky wave antenna beamforming", ["高次谐波", "hhg", "high harmonic"]) is None,
                         "6G 通信论文不应命中")
        # _is_ops_briefing：空简报/运维标题/正常学术简报
        self.assert_true(src._is_ops_briefing("research_briefing", "短"), "过短简报应过滤")
        self.assert_true(
            src._is_ops_briefing("briefing-x", "hermes-briefing 每日简报空记录：cron 自动运行" + "与个人知识库运维" * 20),
            "运维简报应过滤")
        self.assert_true(
            not src._is_ops_briefing("briefing-y", ("今日精选论文：arXiv:2508.12345 固体高次谐波新进展。" * 30)),
            "含 arXiv 条目的学术简报不应过滤")

    def _test_new_quota_caps_weekly_registrations(self):
        """周配额：3 个达标簇仅 2 个 new，第 3 个 defer（08-16 泛滥根治）。"""
        from weekend_pipeline import input_jobs

        self._seed_lifecycle({
            "general-active-20260101": {"status": "optimizing",
                "title": "twisted moiré high harmonic", "text": "moire HHG solids"},
        })
        clusters = []
        # 三个主题均含 hhg（命中 setup 写入的方向词表），主题词互不重叠
        for i, theme in enumerate(["squeezed hhg photon", "berry hhg curvature", "floquet hhg engineering"]):
            clusters.append({
                "cluster_id": f"cl_q{i}", "title": f"{theme} physics",
                "keywords": theme.split() + [f"extra{i}"], "summary": f"{theme} summary",
                "member_source_ids": [f"paper:q{i}-{k}" for k in range(3)],
                "member_summaries": [], "distilled_by": "llm", "status": "open",
                "linked_proposal_id": None,
                "created_at": "2026-08-01T00:00:00Z", "updated_at": "2026-08-10T00:00:00Z",
            })
        from weekend_pipeline import clusters as cl
        cl.CLUSTERS_PATH = self.tmp_root / "memory" / "weekend-input" / "clusters.json"
        cl.save_clusters({"clusters": clusters, "orphans": []})

        input_jobs.is_llm_available = lambda: False
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        result = input_jobs.run_input_topic_match(state={}, job={})
        self.assert_true(result.get("success"), str(result))
        routes = json.loads((WEEKEND_INPUT_DIR / f"routes-{input_jobs.now_utc()[:10]}.json").read_text(encoding="utf-8"))["routes"]
        new_count = sum(1 for r in routes if r["action"] == "new")
        defer_count = sum(1 for r in routes if r["action"] == "defer")
        self.assert_eq(new_count, input_jobs.NEW_WEEKLY_QUOTA, f"new 数应等于周配额 {input_jobs.NEW_WEEKLY_QUOTA}")
        self.assert_eq(defer_count, 1, "超额达标簇应 defer 等下周")

    def _test_distill_marks_distilled_by(self):
        """cluster_distill 标记知识卡来源（llm/fallback），new 门槛依据。"""
        from weekend_pipeline import input_jobs

        from weekend_pipeline import clusters as cl
        registry = {"clusters": [{
            "cluster_id": "cl_x", "title": "test cluster", "keywords": ["hhg"],
            "summary": "", "member_source_ids": ["paper:x1", "paper:x2"],
            "member_summaries": [
                {"source_id": "paper:x1", "title": "t1", "summary": "s1", "keywords": []},
                {"source_id": "paper:x2", "title": "t2", "summary": "s2", "keywords": []},
            ],
            "status": "open", "linked_proposal_id": None,
            "created_at": "2026-08-01T00:00:00Z", "updated_at": input_jobs.now_utc(),
        }], "orphans": []}
        cl.CLUSTERS_PATH = self.tmp_root / "memory" / "weekend-input" / "clusters.json"
        cl.save_clusters(registry)

        # LLM 成功路径
        input_jobs.is_llm_available = lambda: True
        input_jobs._llm_json = lambda system, user, timeout=120: {
            "title": "T", "summary": "综合摘要" * 30, "open_questions": ["q1"]}
        result = input_jobs.run_input_cluster_distill(state={}, job={})
        self.assert_true(result.get("success"), str(result))
        data = cl.load_clusters()
        self.assert_eq(data["clusters"][0].get("distilled_by"), "llm", "LLM 卡应标 llm")

        # LLM 失败降级路径
        registry["clusters"][0]["summary"] = ""
        registry["clusters"][0]["distilled_by"] = None
        del registry["clusters"][0]["distilled_by"]
        registry["clusters"][0]["updated_at"] = input_jobs.now_utc()
        cl.save_clusters(registry)
        input_jobs._llm_json = lambda system, user, timeout=120: None
        result = input_jobs.run_input_cluster_distill(state={}, job={})
        self.assert_true(result.get("success"), str(result))
        data = cl.load_clusters()
        self.assert_eq(data["clusters"][0].get("distilled_by"), "fallback", "降级拼接应标 fallback")

    def _test_supplementary_cross_week_members(self):
        """信息源挂载用簇内 member_summaries（跨周成员可挂载）。"""
        from weekend_pipeline import input_jobs
        from proposal_lifecycle import ProposalLifecycle

        self._seed_lifecycle({
            "general-live-20260101": {"status": "optimizing", "title": "t", "text": "t"},
        })
        # 簇成员是上周的：不在当天 summary_index 里
        cluster = {
            "cluster_id": "cl_old", "member_source_ids": ["paper:old1", "paper:old2"],
            "member_summaries": [
                {"source_id": "paper:old1", "title": "上周论文一", "summary": "s1", "keywords": [], "path": "knowledge/raw/papers/a.md"},
                {"source_id": "paper:old2", "title": "上周论文二", "summary": "s2", "keywords": [], "path": "knowledge/raw/papers/b.md"},
            ],
        }
        ok = input_jobs._write_supplementary_sources(
            "general-live-20260101", cluster, summary_index={})
        self.assert_true(ok, "跨周成员挂载应成功（08-16 实测旧实现必失败）")
        out = (self.tmp_root / "research_proposals" / "optimizing" / "general-live-20260101"
               / "02_literature" / f"supplementary-sources-{input_jobs.now_utc()[:10]}.json")
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assert_eq(len(data["entries"]), 2, "两条跨周成员均应挂载")
        self.assert_eq(data["entries"][0]["path"], "knowledge/raw/papers/a.md", "成员自带 path 应保留")

    def _test_merge_follower_grouping(self):
        """同目标课题的相似簇分组：主簇注入，其余只挂信息源。"""
        from weekend_pipeline import input_jobs

        cluster_index = {
            "cl_big": {"cluster_id": "cl_big", "title": "hhg", "keywords": ["hhg", "solid", "quantum"],
                       "member_source_ids": ["a", "b", "c", "d"]},
            "cl_small": {"cluster_id": "cl_small", "title": "hhg variant", "keywords": ["hhg", "solid", "quantum"],
                         "member_source_ids": ["e", "f"]},
            "cl_far": {"cluster_id": "cl_far", "title": "wigner crystal", "keywords": ["wigner", "crystal"],
                       "member_source_ids": ["g", "h", "i"]},
        }
        routes = [
            {"cluster_id": "cl_big", "action": "merge", "target_id": "p1"},
            {"cluster_id": "cl_small", "action": "merge", "target_id": "p1"},
            {"cluster_id": "cl_far", "action": "merge", "target_id": "p2"},
        ]
        leader = input_jobs._group_merge_routes(routes, cluster_index)
        self.assert_eq(leader.get("cl_big"), "cl_big", "大簇应为主簇")
        self.assert_eq(leader.get("cl_small"), "cl_big", "相似小簇应归并到主簇")
        self.assert_eq(leader.get("cl_far"), "cl_far", "不同主题簇不归并")

    def _test_enrich_heading_carries_cluster_tag(self):
        """enrich 注入标题带簇 ID——同课题多簇注入不因标题去重裸奔。"""
        from proposal_lifecycle import ProposalLifecycle

        # 独立课题 id：避免与 enrich_appends 等用例共享文件（套件内
        # tmp_root 只建一次，文件跨用例累积）
        self._seed_lifecycle({
            "general-heading-20260101": {"status": "optimizing", "title": "quantum hhg", "text": "t"},
        })
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / "general-heading-20260101"
        for stage in ("01_direction", "02_topic", "03_question", "04_proposal"):
            (prop_dir / stage).mkdir(parents=True, exist_ok=True)
        lc = ProposalLifecycle()
        for cid, bg in (("cl_m1", "背景内容甲"), ("cl_m2", "背景内容乙")):
            lc.enrich_from_idea("general-heading-20260101", {
                "title": f"主题 {cid}", "background": f"{bg}" + "独特背景描述。" * 5,
                "gap": "空白" + cid, "content": ["c"], "innovations": ["i"],
                "sources": [], "cluster_id": cid, "reliability": "derived",
            })
        text = (prop_dir / "01_direction" / "direction-calibration.md").read_text(encoding="utf-8")
        self.assert_in("cl_m1", text, "第一簇标题段应保留簇 ID")
        self.assert_in("cl_m2", text, "第二簇标题段应保留簇 ID")
        self.assert_eq(text.count("## 周末输入补充"), 2, "两个簇应各有一个注入标题")

    def _test_register_from_idea_writes_dossier(self):
        """register_from_idea 生成立项决策包（新课题进 activate 人工队列的依据）。"""
        from proposal_lifecycle import ProposalLifecycle

        self._seed_lifecycle({
            "general-live-20260101": {"status": "optimizing",
                "title": "quantum hhg theory", "text": "quantum high harmonic"},
        })
        lc = ProposalLifecycle()
        result = lc.register_from_idea({
            "title": "Wigner Crystal nonlinear optics",
            "background": "维格纳晶体非线性光学响应背景。", "gap": "高温相变缺乏统一图像。",
            "content": ["时间分辨测量"], "innovations": ["非平衡诊断"],
            "sources": [], "keywords": ["wigner crystal", "THz"],
            "reliability": "derived",
        }, project_type="general")
        self.assert_true(result.get("success"), "注册应成功", str(result))
        prop_dir = self.tmp_root / "research_proposals" / "drafts" / result["proposal_id"]
        dossier = prop_dir / "00_idea-dossier.md"
        self.assert_true(dossier.exists(), "立项决策包应生成")
        dt = dossier.read_text(encoding="utf-8")
        self.assert_in("激活建议", dt, "决策包应含激活建议")
        self.assert_in("新颖性", dt, "决策包应含新颖性对比")

    def _test_ops_cluster_routes_defer(self):
        """运维簇（简报/cron 元数据）路由前置 defer，不进课题路由。

        08-16 复跑实测：运维簇知识卡含个别领域词可过方向关，LLM 仲裁
        无 reject 选项只能判 new → 注册了 general-hermes-briefing 课题。
        """
        from weekend_pipeline import input_jobs

        # 纯函数判据
        ops = {"title": "hermes-briefing 每日简报自动化系统与空白对话记忆",
               "keywords": ["cron 自动运行", "每日简报", "知识管理"]}
        academic = {"title": "二维材料中交变磁性磁态的自旋-能谷耦合",
                    "keywords": ["交变磁性", "自旋能谷耦合", "滑移调控"]}
        self.assert_true(input_jobs._is_ops_cluster(ops), "运维簇应被识别")
        self.assert_true(not input_jobs._is_ops_cluster(academic), "学术簇不应误判")

        # 路由端到端：运维簇 defer
        self._seed_lifecycle({
            "general-active-20260101": {"status": "optimizing",
                "title": "twisted moiré high harmonic", "text": "moire HHG solids"},
        })
        from weekend_pipeline import clusters as cl
        cl.CLUSTERS_PATH = self.tmp_root / "memory" / "weekend-input" / "clusters.json"
        cl.save_clusters({"clusters": [
            {"cluster_id": "cl_ops", "title": "每日简报、无用户交互、对话记忆",
             "keywords": ["cron 自动任务", "hermes-briefing", "每日简报"],
             "summary": "系统运维元数据，含一条高次谐波讨论",
             "member_source_ids": [f"paper:o{k}" for k in range(11)],
             "member_summaries": [], "distilled_by": "llm", "status": "open",
             "linked_proposal_id": None,
             "created_at": "2026-08-01T00:00:00Z", "updated_at": "2026-08-10T00:00:00Z"},
        ], "orphans": []})
        input_jobs.is_llm_available = lambda: True
        input_jobs._llm_json = lambda system, user, timeout=90: {"action": "new", "target_id": None, "reason": "x"}
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        result = input_jobs.run_input_topic_match(state={}, job={})
        self.assert_true(result.get("success"), str(result))
        routes = json.loads((WEEKEND_INPUT_DIR / f"routes-{input_jobs.now_utc()[:10]}.json").read_text(encoding="utf-8"))["routes"]
        self.assert_eq(routes[0]["action"], "defer", "运维簇应 defer（即使 LLM 判 new）")

    def _test_new_gate_requires_core_theme(self):
        """v6.9.22 核心范式强制关：纯静态凝聚态簇不开新课题。

        背景：08-16 注册的 berry-mnps3 课题（准静态滑移器件化，无强场/
        超快维度）即从此漏洞通过方向关。修复后 new 门槛要求簇文本命中
        "强场操控"或"HHG/超快光谱测量"范式词，仅命中材料/物态语境词
        （自旋/能谷/交变磁）不够格，只能 merge/expansion 或 defer。
        """
        from weekend_pipeline import sources as src
        from weekend_pipeline import input_jobs

        # core_theme_hit 单元判据
        self.assert_true(src.core_theme_hit("strong-field high harmonic generation in solids") is not None,
                         "强场 HHG 应命中核心范式")
        self.assert_true(src.core_theme_hit("time-resolved magnon dynamics with pump-probe") is not None,
                         "时间分辨泵浦探测应命中核心范式")
        self.assert_true(src.core_theme_hit("强场太赫兹驱动层间滑移切换磁序") is not None,
                         "强场 THz 操控应命中核心范式")
        self.assert_true(src.core_theme_hit("field-free spin orbit torque switching") is None,
                         "field-free 静态自旋学不应命中")
        self.assert_true(src.core_theme_hit("altermagnetic spin splitting first principles") is None,
                         "纯静态第一性原理不应命中")

        # _new_gates：纯静态簇拒 new（berry-mnps3 复现）
        static_cluster = {
            "cluster_id": "cl_static", "title": "二维方形晶格交变磁性自旋-能谷耦合与滑移调控",
            "keywords": ["mnps3", "rashba", "berry curvature", "交变磁性", "自旋能谷耦合", "滑移工程"],
            "summary": "基于第一性原理计算与自旋-Laue对称性分析，研究层间滑移对非相对论性"
                       "自旋劈裂的可逆调控，为自旋-能谷多功能器件提供对称性设计原理。",
            "member_source_ids": ["paper:a1", "paper:a2", "paper:a3"],
            "distilled_by": "llm",
        }
        ok, reason = input_jobs._new_gates(static_cluster, [], ["交变磁", "自旋", "能谷", "berry"], 2)
        self.assert_true(not ok, "纯静态凝聚态簇不应过 new 门槛")
        self.assert_true("核心范式" in reason, f"拒因应指向核心范式: {reason}")

        # 同簇嫁接强场超快维度后方向关放行
        sf_cluster = dict(static_cluster)
        sf_cluster["title"] = "强场太赫兹驱动滑移模式切换交变磁自旋劈裂与高次谐波读出"
        sf_cluster["keywords"] = static_cluster["keywords"] + ["强场", "thz", "pump-probe", "高次谐波"]
        ok2, reason2 = input_jobs._new_gates(sf_cluster, [], ["交变磁", "自旋", "能谷", "强场", "高次谐波"], 2)
        self.assert_true(ok2, f"嫁接强场超快维度后应过五关: {reason2}")

        # load_scope_terms 不再从课题标题自动补词（同义反复漂移引擎移除）
        orig_path = src.SCOPE_TERMS_PATH
        try:
            src.SCOPE_TERMS_PATH = self.tmp_root / "memory" / "weekend-input" / "scope-terms.json"
            self._seed_lifecycle({
                "general-weird-20260101": {"status": "optimizing",
                    "title": "weirdtopicxyz static device engineering", "text": ""},
            })
            terms = src.load_scope_terms(persist=False)
            self.assert_true("weirdtopicxyz" not in terms,
                             "课题标题词不应自动进入方向词表（v6.9.22 移除同义反复扩充）")
        finally:
            src.SCOPE_TERMS_PATH = orig_path

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
        self._test_summarize_llm_failure_not_silent()
        self._test_weekend_input_prefers_glm()
        self._test_llm_json_passes_prefer_tag()
        self._test_keyword_normalization()
        self._test_sparse_overlap_forms_cluster()
        self._test_enrich_appends_without_crash()
        self._test_register_generates_valid_id()
        self._test_register_cn_title_falls_back_to_keywords()
        # v6.9.18 输入链路重构回归
        self._test_cluster_ids_unique()
        self._test_cn_2gram_title_similarity()
        self._test_scope_and_ops_filters()
        self._test_new_quota_caps_weekly_registrations()
        self._test_distill_marks_distilled_by()
        self._test_supplementary_cross_week_members()
        self._test_merge_follower_grouping()
        self._test_enrich_heading_carries_cluster_tag()
        self._test_register_from_idea_writes_dossier()
        self._test_ops_cluster_routes_defer()
        self._test_new_gate_requires_core_theme()
