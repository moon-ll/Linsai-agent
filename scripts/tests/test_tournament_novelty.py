#!/usr/bin/env python3
"""
test_tournament_novelty.py — 锦标赛制新颖性闸门回归测试（v7.2.67）

背景：Jaccard 词袋相似度无区分度（「结构压缩调控 HHG」vs「MoS₂ HHG
调控」= 0.01、order↔new 同题 65-70% 未检出）。topic_match 的 new 动作
与 idea_generator 的 recommend_activation 新增 pairwise LLM 锦标赛终审
（三判：同质/正交/互补）。

覆盖点（全部 mock LLM，零真实调用）：
    1. 同质 → new 降级 merge（merge_target 正确；archived 同质 → expansion）
    2. 正交/互补 → new 放行（全链路 + 单元）
    3. LLM 失败 / verdict 非法 → fail-open 回退旧 Jaccard 判定 + 留 warning
    4. Jaccard 预筛：≥ 0.50 直接判同质降级 merge，不调 LLM
    5. idea_generator.recommend_activation_tournament 三档语义
       （hold 线不调 LLM / 同质降级 merge考察 / 全正交 activate）
"""

import importlib
import json
import shutil
import sys
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class _WarnLog:
    """测试用假 logger：收集 warning 供断言。"""

    def __init__(self):
        self.warnings = []

    def warning(self, msg):
        self.warnings.append(str(msg))

    def info(self, msg):
        pass


class TournamentNoveltyTests(TestSuite):
    def __init__(self):
        super().__init__("锦标赛制新颖性闸门测试（v7.2.67）")
        self.tmp_root = None

    # ------------------------------------------------------------------
    # 隔离环境
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        _write_json(self.tmp_root / "memory" / "weekend-input" / "scope-terms.json",
                    {"terms": ["hhg", "高次谐波"]})

        # 清模块缓存后在隔离根下重载（路径常量按 paths.PROJECT_ROOT 绑定）
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
        # v8.0.0: weekend_bridge 读 topic_pipeline.constants.TOPICS_ROOT，同样要隔离
        patch_module_root("topic_pipeline.constants", self.tmp_root)

        from weekend_pipeline import input_jobs
        self.ij = input_jobs
        # 保存待 mock 的模块属性
        self._orig = (
            input_jobs.is_llm_available,
            input_jobs._llm_json,
            input_jobs._llm_arbitrate_cluster,
            input_jobs._tournament_pairwise_verdict,
            input_jobs._log,
        )

    def teardown(self):
        if hasattr(self, "ij") and self._orig:
            (self.ij.is_llm_available, self.ij._llm_json,
             self.ij._llm_arbitrate_cluster, self.ij._tournament_pairwise_verdict,
             self.ij._log) = self._orig
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    def _restore_llm_mocks(self):
        (self.ij.is_llm_available, self.ij._llm_json,
         self.ij._llm_arbitrate_cluster, self.ij._tournament_pairwise_verdict,
         self.ij._log) = self._orig

    # ------------------------------------------------------------------
    # 夹具
    # ------------------------------------------------------------------

    PROPOSALS_BASE = [
        {"proposal_id": "general-p1-20260101", "status": "optimizing",
         "title": "twisted moire lattice light control",
         "text": "moire superlattice engineering light emission in twisted semiconductors"},
        {"proposal_id": "general-p2-20260102", "status": "optimizing",
         "title": "cavity polariton condensation",
         "text": "polariton Bose condensation driven by cavity photons in microcavity"},
    ]

    def _mk_cluster(self, **overrides) -> dict:
        """达标簇（过七关 + LLM 仲裁判 new 后进锦标赛）。"""
        base = {
            "cluster_id": "cl_tour",
            "title": "structural compression driven high harmonic response in layered crystals",
            "keywords": ["structural", "compression", "harmonic", "response", "crystal"],
            "summary": "lattice constant modulation controls HHG yield in layered materials",
            "research_gap": "层间压缩对固体高次谐波产额的调控机制缺乏系统研究",
            "member_source_ids": ["paper:d1", "paper:d2", "paper:d3"],
            "member_summaries": [
                {"title": "Paper Alpha strain HHG"}, {"title": "Paper Beta lattice"},
                {"title": "Paper Gamma compression"}],
            "distilled_by": "llm", "status": "open", "linked_proposal_id": None,
            "created_at": "2026-10-01T00:00:00Z", "updated_at": "2026-10-08T00:00:00Z",
        }
        base.update(overrides)
        return base

    def _seed_lifecycle(self, proposals: dict) -> None:
        _write_json(self.tmp_root / "research_proposals" / "_lifecycle.json",
                    {"proposals": proposals})
        for pid, meta in proposals.items():
            stage_dir = self.tmp_root / "research_proposals" / meta["status"] / pid
            (stage_dir / "00_proposal-brief.md").parent.mkdir(parents=True, exist_ok=True)
            (stage_dir / "00_proposal-brief.md").write_text(
                f"# {meta.get('title', pid)}\n\n{meta.get('text', '')}", encoding="utf-8")

    def _seed_clusters(self, clusters: list) -> None:
        from weekend_pipeline import clusters as cl
        cl.CLUSTERS_PATH = self.tmp_root / "memory" / "weekend-input" / "clusters.json"
        cl.save_clusters({"clusters": clusters, "orphans": []})

    def _read_routes(self) -> dict:
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        path = WEEKEND_INPUT_DIR / f"routes-{self.ij.now_utc()[:10]}.json"
        return {r["cluster_id"]: r for r in
                json.loads(path.read_text(encoding="utf-8"))["routes"]}

    def _mock_full_chain_new_path(self, pairwise_results):
        """全链路 mock：LLM 仲裁恒判 new，pairwise 按课题 id 返回三判结果。

        pairwise_results: {proposal_id: verdict_dict 或 None(失败)}
        返回 pairwise 调用计数器 dict。
        """
        calls = {"pairwise": 0}

        def fake_pairwise(candidate_text, proposal_id, proposal_text, timeout=90):
            calls["pairwise"] += 1
            return pairwise_results.get(proposal_id)

        self.ij.is_llm_available = lambda: True
        self.ij._llm_arbitrate_cluster = lambda cluster, scored: ("new", None, "LLM 仲裁判新")
        self.ij._tournament_pairwise_verdict = fake_pairwise
        return calls

    # ------------------------------------------------------------------
    # 用例 1：同质 → new 降级 merge（merge_target 正确）
    # ------------------------------------------------------------------

    def _test_homogeneous_downgrades_to_merge(self):
        self._seed_lifecycle({p["proposal_id"]: {"status": p["status"], "title": p["title"],
                                                  "text": p["text"]}
                              for p in self.PROPOSALS_BASE})
        self._seed_clusters([self._mk_cluster()])
        self._mock_full_chain_new_path({
            "general-p1-20260101": {"verdict": "同质", "reason": "同为晶格调控 HHG 产额，评审自撞"},
            "general-p2-20260102": {"verdict": "正交", "reason": "体系不同"},
        })
        try:
            result = self.ij.run_input_topic_match(state={}, job={})
            self.assert_true(result.get("success"), "topic_match 应成功", str(result))
            route = self._read_routes()["cl_tour"]
            self.assert_eq(route["action"], "merge", "锦标赛判同质应降级 merge")
            self.assert_eq(route["target_id"], "general-p1-20260101", "目标课题应为判同质的 P1")
            self.assert_eq(route.get("merge_target"), "general-p1-20260101",
                           "merge_target 标注应指向同质课题")
            self.assert_in("锦标赛", route["reason"], f"reason 应标注锦标赛来源: {route['reason']}")
            self.assert_in("同质", route["reason"], "reason 应含判词")
        finally:
            self._restore_llm_mocks()

    # ------------------------------------------------------------------
    # 用例 2：全部正交/互补 → new 放行（全链路）
    # ------------------------------------------------------------------

    def _test_orthogonal_passes_new(self):
        self._seed_lifecycle({p["proposal_id"]: {"status": p["status"], "title": p["title"],
                                                  "text": p["text"]}
                              for p in self.PROPOSALS_BASE})
        self._seed_clusters([self._mk_cluster()])
        self._mock_full_chain_new_path({
            "general-p1-20260101": {"verdict": "正交", "reason": "机制不同"},
            "general-p2-20260102": {"verdict": "互补", "reason": "可挂文献但独立成立"},
        })
        try:
            result = self.ij.run_input_topic_match(state={}, job={})
            self.assert_true(result.get("success"), "topic_match 应成功", str(result))
            route = self._read_routes()["cl_tour"]
            self.assert_eq(route["action"], "new", "全正交/互补应放行 new")
            self.assert_eq(route.get("target_id"), None, "new 不应有目标课题")
            self.assert_in("锦标赛", route["reason"], f"reason 应记录锦标赛终审: {route['reason']}")
            self.assert_in("七关全过", route["reason"], "七关门槛文案应保留")
        finally:
            self._restore_llm_mocks()

    # ------------------------------------------------------------------
    # 用例 3：LLM 调用失败 → 回退 Jaccard 判定 + 留 warning
    # ------------------------------------------------------------------

    def _test_llm_failure_falls_back_jaccard(self):
        self._seed_lifecycle({p["proposal_id"]: {"status": p["status"], "title": p["title"],
                                                  "text": p["text"]}
                              for p in self.PROPOSALS_BASE})
        self._seed_clusters([self._mk_cluster()])
        fake_log = _WarnLog()
        self.ij.is_llm_available = lambda: True
        self.ij._llm_arbitrate_cluster = lambda cluster, scored: ("new", None, "LLM 仲裁判新")
        self.ij._log = fake_log
        # pairwise 底层 LLM 全挂（_llm_json 返回 None）
        self.ij._llm_json = lambda system, user, timeout=120, prefer="weekend_input": None
        try:
            result = self.ij.run_input_topic_match(state={}, job={})
            self.assert_true(result.get("success"), "fail-open 不应阻塞流水线", str(result))
            route = self._read_routes()["cl_tour"]
            # 旧 Jaccard 判定：top 候选全部 < 0.50 → 不重叠 → 放行 new
            self.assert_eq(route["action"], "new", "LLM 失败应回退 Jaccard 判定（全 < 0.50 → new）")
            self.assert_in("回退", route["reason"], f"reason 应标注回退: {route['reason']}")
            self.assert_true(
                any("锦标赛" in w for w in fake_log.warnings),
                f"仲裁失败应留 warning，实际: {fake_log.warnings}")
        finally:
            self._restore_llm_mocks()

    # ------------------------------------------------------------------
    # 用例 4：LLM 不可用 → 单元级回退 + warning
    # ------------------------------------------------------------------

    def _test_llm_unavailable_fallback_unit(self):
        fake_log = _WarnLog()
        self.ij.is_llm_available = lambda: False
        self.ij._log = fake_log
        try:
            action, target, reason = self.ij._tournament_novelty_gate(
                self._mk_cluster(), self.PROPOSALS_BASE)
            self.assert_eq(action, "new", "LLM 不可用应回退 Jaccard（全 < 0.50 → 放行 new）")
            self.assert_eq(target, None, "回退放行不应有降级目标")
            self.assert_in("回退", reason, f"reason 应标注回退: {reason}")
            self.assert_true(
                any("不可用" in w for w in fake_log.warnings),
                f"LLM 不可用应留 warning，实际: {fake_log.warnings}")
        finally:
            self._restore_llm_mocks()

    # ------------------------------------------------------------------
    # 用例 5：Jaccard 预筛 ≥ 0.50 → 不调 LLM 直接 merge（单元级）
    # ------------------------------------------------------------------

    def _test_jaccard_prescreen_skips_llm(self):
        calls = {"pairwise": 0}

        def fake_pairwise(candidate_text, proposal_id, proposal_text, timeout=90):
            calls["pairwise"] += 1
            return {"verdict": "正交", "reason": "不应被调用"}

        # 同质课颊文本与簇几乎同词表 → Jaccard ≥ 0.50
        dup = {"proposal_id": "general-dup-20260103", "status": "optimizing",
               "title": "structural compression driven high harmonic response layered crystals",
               "text": "structural compression harmonic response crystal lattice HHG layered materials"}
        self.ij.is_llm_available = lambda: True
        self.ij._tournament_pairwise_verdict = fake_pairwise
        try:
            action, target, reason = self.ij._tournament_novelty_gate(
                self._mk_cluster(), self.PROPOSALS_BASE + [dup])
            self.assert_eq(action, "merge", "Jaccard ≥ 0.50 预筛应直接判同质降级 merge")
            self.assert_eq(target, "general-dup-20260103", "降级目标应为最高分课题")
            self.assert_in("预筛", reason, f"reason 应标注预筛未调 LLM: {reason}")
            self.assert_eq(calls["pairwise"], 0, "预筛命中时不应发起任何 pairwise LLM 调用")
        finally:
            self._restore_llm_mocks()

    # ------------------------------------------------------------------
    # 用例 6：verdict 非法（非三值）→ 视为失败 fail-open
    # ------------------------------------------------------------------

    def _test_invalid_verdict_rejected(self):
        self.ij.is_llm_available = lambda: True
        self.ij._llm_json = lambda system, user, timeout=120, prefer="weekend_input": {
            "verdict": "差不多", "reason": "非法判词"}
        try:
            verdict = self.ij._tournament_pairwise_verdict(
                "cluster text", "general-p1-20260101", "proposal text")
            self.assert_eq(verdict, None, "非三值 verdict 应被拒绝（返回 None 走 fail-open）")

            action, target, reason = self.ij._tournament_novelty_gate(
                self._mk_cluster(), self.PROPOSALS_BASE)
            self.assert_eq(action, "new", "全部非法输出应回退 Jaccard 判定放行 new")
            self.assert_in("回退", reason, f"reason 应标注回退: {reason}")
        finally:
            self._restore_llm_mocks()

    # ------------------------------------------------------------------
    # 用例 7：同质课题为 archived → 全链路降级 expansion（保持既有语义）
    # ------------------------------------------------------------------

    def _test_archived_homogeneous_routes_expansion(self):
        proposals = [
            # 同题不同术语（Jaccard < 0.35，同质性只能靠 LLM 锦标赛识别）
            {"proposal_id": "general-arch-20260104", "status": "archived",
             "title": "strain engineering attosecond response",
             "text": "strain tuning nonlinear light emission in deformed solid state systems"},
            {"proposal_id": "general-p2-20260102", "status": "optimizing",
             "title": "cavity polariton condensation",
             "text": "polariton Bose condensation driven by cavity photons in microcavity"},
        ]
        self._seed_lifecycle({p["proposal_id"]: {"status": p["status"], "title": p["title"],
                                                  "text": p["text"]} for p in proposals})
        self._seed_clusters([self._mk_cluster()])
        self._mock_full_chain_new_path({
            "general-arch-20260104": {"verdict": "同质", "reason": "同为晶格常数调控谐波产额"},
            "general-p2-20260102": {"verdict": "正交", "reason": "体系不同"},
        })
        try:
            result = self.ij.run_input_topic_match(state={}, job={})
            self.assert_true(result.get("success"), "topic_match 应成功", str(result))
            route = self._read_routes()["cl_tour"]
            self.assert_eq(route["action"], "expansion",
                           "同质课题为 archived 时降级应走 expansion（文献挂载）")
            self.assert_eq(route["target_id"], "general-arch-20260104", "目标课题 id")
        finally:
            self._restore_llm_mocks()

    # ------------------------------------------------------------------
    # 用例 8-10：idea_generator.recommend_activation_tournament 三档语义
    # ------------------------------------------------------------------

    def _mk_comparisons(self, top_sim: float) -> list:
        return [
            {"proposal_id": "general-p1-20260101", "status": "optimizing",
             "title": "twisted moire lattice light control", "brief": "moire engineering",
             "similarity": top_sim},
            {"proposal_id": "general-p2-20260102", "status": "optimizing",
             "title": "cavity polariton condensation", "brief": "polariton physics",
             "similarity": 0.10},
        ]

    def _mk_idea(self) -> dict:
        return {"title": "structural compression HHG control",
                "background": "lattice compression tunes high harmonic yield in layered crystals",
                "keywords": ["structural", "compression", "harmonic"]}

    def _test_recommend_hold_skips_llm(self):
        import idea_generator as ig
        calls = {"pairwise": 0}

        def fake_pairwise(candidate_text, proposal_id, proposal_text, timeout=90):
            calls["pairwise"] += 1
            return {"verdict": "正交", "reason": "x"}

        self.ij.is_llm_available = lambda: True
        self.ij._tournament_pairwise_verdict = fake_pairwise
        try:
            rec, reason, target = ig.recommend_activation_tournament(
                self._mk_idea(), self._mk_comparisons(0.72))
            self.assert_eq(rec, "hold", "≥ hold 线应保持 hold（数值硬线）")
            self.assert_eq(target, None, "hold 不产生锦标赛目标")
            self.assert_eq(calls["pairwise"], 0, "hold 线以上不应调 LLM")
        finally:
            self._restore_llm_mocks()

    def _test_recommend_homogeneous_downgrades_merge(self):
        import idea_generator as ig
        self.ij.is_llm_available = lambda: True
        self.ij._tournament_pairwise_verdict = lambda c, pid, ptext, timeout=90: (
            {"verdict": "同质", "reason": "同为压缩调控 HHG"} if pid == "general-p1-20260101"
            else {"verdict": "正交", "reason": "不同体系"})
        try:
            rec, reason, target = ig.recommend_activation_tournament(
                self._mk_idea(), self._mk_comparisons(0.20))
            self.assert_eq(rec, "merge考察", "锦标赛判同质应把 activate 降级 merge考察")
            self.assert_eq(target, "general-p1-20260101", "tournament_target 应为同质课题")
            self.assert_in("同质", reason, f"reason 应含判词: {reason}")
        finally:
            self._restore_llm_mocks()

    def _test_recommend_orthogonal_activates_and_fallback(self):
        import idea_generator as ig
        self.ij.is_llm_available = lambda: True
        self.ij._tournament_pairwise_verdict = lambda c, pid, ptext, timeout=90: (
            {"verdict": "互补", "reason": "可挂文献但独立成立"})
        try:
            # 全互补 + 数值档 < novel 线 → activate
            rec, reason, target = ig.recommend_activation_tournament(
                self._mk_idea(), self._mk_comparisons(0.20))
            self.assert_eq(rec, "activate", "全正交/互补且数值档达标应 activate")
            self.assert_eq(target, None, "activate 无降级目标")
        finally:
            self._restore_llm_mocks()

        # LLM 全挂 → 回退纯数值档：0.40 ∈ [0.35, 0.50) → merge考察
        self.ij.is_llm_available = lambda: True
        self.ij._llm_json = lambda system, user, timeout=120, prefer="weekend_input": None
        try:
            rec, reason, target = ig.recommend_activation_tournament(
                self._mk_idea(), self._mk_comparisons(0.40))
            self.assert_eq(rec, "merge考察", "LLM 失败应回退纯数值档（0.40 → merge考察）")
            self.assert_eq(target, None, "回退路径无锦标赛目标")
            self.assert_in("0.40", reason, f"回退 reason 应含数值: {reason}")
        finally:
            self._restore_llm_mocks()

    # ------------------------------------------------------------------
    # 用例 11：pairwise prompt 契约（两侧 600 字截断 + 三判定义 + 单对单调用）
    # ------------------------------------------------------------------

    def _test_pairwise_prompt_contract(self):
        captured = {}

        def fake_llm_json(system, user, timeout=120, prefer="weekend_input"):
            captured["system"] = system
            captured["user"] = user
            captured["timeout"] = timeout
            return {"verdict": "正交", "reason": "ok"}

        self.ij.is_llm_available = lambda: True
        self.ij._llm_json = fake_llm_json
        try:
            long_text = "x" * 2000
            verdict = self.ij._tournament_pairwise_verdict(
                long_text, "general-p1-20260101", long_text)
            self.assert_eq(verdict["verdict"], "正交", "合法 verdict 应被解析")
            for term in ("同质", "正交", "互补", "三值之一"):
                self.assert_in(term, captured["system"], f"system prompt 应含三判定义「{term}」")
            self.assert_in("general-p1-20260101", captured["user"], "user 应含现有课题 id")
            self.assert_true(len(captured["user"]) < 1600,
                             f"两侧各截 600 字应控制 prompt 长度: {len(captured['user'])}")
            self.assert_eq(captured["timeout"], 90, "单对调用超时 90s")
        finally:
            self._restore_llm_mocks()

    def run_tests(self):
        self._test_homogeneous_downgrades_to_merge()
        self._test_orthogonal_passes_new()
        self._test_llm_failure_falls_back_jaccard()
        self._test_llm_unavailable_fallback_unit()
        self._test_jaccard_prescreen_skips_llm()
        self._test_invalid_verdict_rejected()
        self._test_archived_homogeneous_routes_expansion()
        self._test_recommend_hold_skips_llm()
        self._test_recommend_homogeneous_downgrades_merge()
        self._test_recommend_orthogonal_activates_and_fallback()
        self._test_pairwise_prompt_contract()


if __name__ == "__main__":
    suite = TournamentNoveltyTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    passed = sum(1 for r in suite.results if r.passed)
    print(f"\n通过 {passed}/{len(suite.results)}")
    for r in suite.results:
        mark = "✓" if r.passed else "✗"
        print(f"  {mark} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if passed == len(suite.results) else 1)
