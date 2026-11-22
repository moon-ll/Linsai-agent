#!/usr/bin/env python3
"""
test_weekend_methods.py — 方法学专题模块（T3，v6.10.0）回归测试

覆盖：
    1. methods_settle job 结构注册（七步链 + 依赖链 + artifact + handler）
    2. 词表归组（词表优先 / 同类宽松合并 ≥2 跨 2 源建页 / 散条 unmatched）
    3. txt 定位窗口（假 txt 验证命中与窗口边界 / 行对齐 / 无命中空串 /
       arxiv 点号→下划线映射）
    4. settle 端到端（隔离目录）：
       - LLM 融合路径：专区写入 + frontmatter（updated_at/settled_count/
         growth_stage 晋升/confidence 随一手原文证据 +0.1）+ 产物 json
       - LLM 失败降级：附录式追加 + fallback 标记 + success 不受影响
       - 空 leads：空产物文件（"done 必有产物"不变式）
       - dry-run：零落盘
    5. 注入端（optimize.py）：
       - _load_methods_reference_block：命中方法页含【方法学专题参考】
         块 / 开关关闭空串 / 摘要截断 max_chars / 页数上限
       - _run_writer_optimize 组装：scheme 聚焦轮 prompt 含注入块，
         rationale 轮不含；开关关后不含
       - _run_critic 组装：scheme 轮含方法页核对提示（仅一行不注入全文）

注意：
    本测试不调用 LLM / hermes（_llm_json 与 _run_hermes 全 stub），
    运行于隔离临时目录，时钟注入。
"""

import sys
import json
import shutil
import importlib
from datetime import datetime, timezone
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


def _utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fake_txt(body_len: int = 4000) -> str:
    """构造假 PDF 提取 txt：背景段 + Methods 章节（含 TDSE 命中行）。"""
    filler = "background filler text for the paper " * (body_len // 40)
    return (
        filler + "\n"
        + "Introduction. Some context about HHG.\n" + filler + "\n"
        + "II. METHODS\n"
        + "We solve the TDSE using the split-operator approach with a "
        + "mask function absorber. Grid spacing dr = 0.1 a.u., intensity "
        + "1e14 W/cm2, wavelength 800 nm.\n"
        + filler + "\nResults follow.\n" + filler
    )


class WeekendMethodsTests(TestSuite):
    def __init__(self):
        super().__init__("方法学专题模块测试（T3，v6.10.0）")
        self.tmp_root = None
        self.wp_mod = None

    # ------------------------------------------------------------------
    # 隔离环境
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")

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
        # kb 子模块常量隔离（方法页写入路径；patch_module_root 可重入还原）
        patch_module_root("kb_wiki", self.tmp_root)
        patch_module_root("kb_graph", self.tmp_root)
        patch_module_root("knowledge_base", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    # ------------------------------------------------------------------
    # 公共构造
    # ------------------------------------------------------------------

    def _write_lexicon(self):
        """写假词表（TDSE 求解器 + RABBITT 两词条）。"""
        lex = {
            "entries": [
                {"slug": "tdse-solver", "page": "TDSE求解器.md",
                 "aliases": ["TDSE", "split-operator"], "zh": ["含时薛定谔"]},
                {"slug": "rabbitt", "page": "RABBITT.md",
                 "aliases": ["RABBITT"], "zh": []},
            ],
            "generated_at": _utc_now_str(), "source": "test",
        }
        cfg_dir = self.tmp_root / "memory" / "config"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        (cfg_dir / "methods-lexicon.json").write_text(
            json.dumps(lex, ensure_ascii=False, indent=2), encoding="utf-8")
        return lex

    def _write_seedling_page(self):
        """构造既有 seedling 方法页。"""
        methods_dir = self.tmp_root / "knowledge" / "wiki" / "methods"
        methods_dir.mkdir(parents=True, exist_ok=True)
        page = (
            "---\n"
            'title: "TDSE求解器"\n'
            'type: "methods"\n'
            'created: "2026-06-17T12:40:33Z"\n'
            'growth_stage: "seedling"\n'
            "confidence: 0.5\n"
            "---\n\n"
            "# TDSE 求解器\n\n含时薛定谔方程数值求解。\n"
        )
        (methods_dir / "TDSE求解器.md").write_text(page, encoding="utf-8")

    def _write_fake_txt(self):
        cache = self.tmp_root / "knowledge" / "raw" / "pdfs" / "_text_cache"
        cache.mkdir(parents=True, exist_ok=True)
        (cache / "0707_4192.txt").write_text(_fake_txt(), encoding="utf-8")

    def _write_summaries(self, with_leads=True):
        """写本轮 summaries 产物 + state 指针，返回 state dict。"""
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        date_str = _utc_today()
        summaries = []
        if with_leads:
            summaries = [
                {"source_id": "paper:2007-0707.4192-improved",
                 "title": "改进 Lewenstein 模型", "tier": 1,
                 "summary": "core", "method_leads": [
                     {"name": "TDSE", "note": "分裂算符求解器新收敛判据"},
                     {"name": "含时薛定谔方程求解", "note": "中文名同页归组"},
                 ]},
                {"source_id": "paper:2007-0707.4228-rabitt",
                 "title": "RABBITT vs FROG", "tier": 1,
                 "summary": "core", "method_leads": [
                     {"name": "RABBITT 测量", "note": "边带振荡相位提取"},
                 ]},
                {"source_id": "paper:2026-s41567-x", "title": "期刊论文", "tier": 1,
                 "summary": "core", "method_leads": [
                     {"name": "Floquet-Bloch能带工程", "note": "缀饰带隙"},
                 ]},
            ]
        path = WEEKEND_INPUT_DIR / f"summaries-{date_str}-r1.json"
        WEEKEND_INPUT_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(
            {"summaries": summaries, "round": 1, "generated_at": _utc_now_str()},
            ensure_ascii=False, indent=2), encoding="utf-8")
        return {"input_round": {"round": 1, "last_summaries_path":
                f"memory/weekend-input/summaries-{date_str}-r1.json"}}

    def _stub_llm(self, merge_result):
        """stub input_jobs._llm_json 与 llm_gateway.is_llm_available。"""
        from weekend_pipeline import input_jobs
        import llm_gateway
        saved = (input_jobs._llm_json, llm_gateway.is_llm_available)
        input_jobs._llm_json = (
            lambda s, u, timeout=120, prefer="weekend_input": merge_result)
        llm_gateway.is_llm_available = lambda: merge_result is not None
        return saved

    def _restore_llm(self, saved):
        from weekend_pipeline import input_jobs
        import llm_gateway
        input_jobs._llm_json, llm_gateway.is_llm_available = saved

    _MERGE_OK = {
        "principle": "TDSE 数值求解是 HHG 理论的 ground truth（SAE+分裂算符）。",
        "params": [{"name": "grid spacing", "value": "0.1 a.u.",
                    "source": "paper:2007-0707.4192-improved"}],
        "boundary": "单活性电子近似；维度上升成本急剧增加。",
        "works": ["2007-0707.4192-improved-lewenstein-model-for-high-order-harmonic-generation"],
    }

    # ------------------------------------------------------------------
    # 1. job 结构注册
    # ------------------------------------------------------------------

    def _test_job_registered_in_seven_step_chain(self):
        from weekend_pipeline.pipeline import WeekendPipeline
        from weekend_pipeline.constants import STAGE_INPUT
        p = WeekendPipeline(state_path=self.tmp_root / "memory" / "weekend-pipeline.json")
        p.sync_stage_jobs(STAGE_INPUT)
        jobs = {j["job_id"]: j for j in p.list_jobs(stage="input")}
        for jid in ["input_methods_settle"]:
            self.assert_in(jid, jobs, f"input 链应包含 {jid}")
        self.assert_eq(
            jobs["input_methods_settle"].get("depends_on"),
            ["input_cluster_distill"],
            "methods_settle 依赖 cluster_distill",
        )
        self.assert_eq(
            jobs["input_topic_match"].get("depends_on"),
            ["input_methods_settle"],
            "topic_match 依赖刷新为 methods_settle",
        )
        self.assert_eq(
            jobs["input_methods_settle"].get("artifact"),
            "memory/weekend-input/methods-settle-{date}-r{round}.json",
            "artifact 声明（轮次产物）",
        )
        self.assert_in(
            (STAGE_INPUT, "methods_settle"), p.handlers,
            "handler 二元组应注册")
        # 链序：methods_settle 位于 cluster_distill 之后、topic_match 之前
        ids = [j["job_id"] for j in p.list_jobs(stage="input")]
        self.assert_true(
            ids.index("input_cluster_distill") < ids.index("input_methods_settle")
            < ids.index("input_topic_match"),
            "链序：distill → settle → match",
        )

    # ------------------------------------------------------------------
    # 2. 词表归组
    # ------------------------------------------------------------------

    def _test_group_leads_lexicon_and_new_page(self):
        from weekend_pipeline.methods_jobs import group_leads
        lex = self._write_lexicon()["entries"]
        summaries = [
            {"source_id": "paper:a", "title": "A", "tier": 1, "method_leads": [
                {"name": "TDSE", "note": "n1"}]},
            {"source_id": "paper:b", "title": "B", "tier": 1, "method_leads": [
                {"name": "含时薛定谔方程求解", "note": "n2"},
                {"name": "量子轨迹模型", "note": "散条1"}]},
            {"source_id": "paper:c", "title": "C", "tier": 1, "method_leads": [
                {"name": "RABBITT", "note": "n3"},
                {"name": "量子轨迹分析", "note": "散条2"}]},
        ]
        groups, unmatched = group_leads(summaries, lex)
        by_page = {g["page"]: g for g in groups}
        self.assert_eq(len(by_page["TDSE求解器.md"]["leads"]), 2,
                       "TDSE 与中文名应归同页")
        self.assert_eq(by_page["TDSE求解器.md"]["create"], False, "既有页不新建")
        self.assert_eq(len(by_page["RABBITT.md"]["leads"]), 1, "RABBITT 归组")
        # 同类宽松合并："量子轨迹模型"与"量子轨迹分析"相似度 ≥0.6 跨 2 源 → 建页
        created = [g for g in groups if g["create"]]
        self.assert_eq(len(created), 1, "同类 ≥2 跨 2 源应建 1 个新页组")
        self.assert_eq(len(created[0]["leads"]), 2, "新页组含 2 条同类线索")

    def _test_group_leads_strict_threshold(self):
        """同类仅 1 条或同源 2 条 → 不建页（宁缺毋滥）。"""
        from weekend_pipeline.methods_jobs import group_leads
        lex = self._write_lexicon()["entries"]
        summaries = [
            {"source_id": "paper:a", "title": "A", "tier": 1, "method_leads": [
                {"name": "孤独特方法", "note": "单条"},
                {"name": "同源双条法", "note": "同源1"},
                {"name": "同源双条法变体", "note": "同源2"},
            ]},
        ]
        groups, unmatched = group_leads(summaries, lex)
        created = [g for g in groups if g["create"]]
        self.assert_eq(len(created), 0, "单条/同源不达门槛不建页")
        self.assert_eq(len(unmatched), 3, "三条全部 unmatched")

    # ------------------------------------------------------------------
    # 3. txt 定位窗口（假 txt）
    # ------------------------------------------------------------------

    def _test_txt_window_hit_and_boundary(self):
        from weekend_pipeline.methods_jobs import (
            locate_txt_window, TXT_WINDOW_CHARS,
        )
        txt = _fake_txt(body_len=20000)
        win = locate_txt_window(txt, ["TDSE"])
        self.assert_in("TDSE", win, "窗口应含 TDSE 命中行")
        self.assert_in("split-operator", win, "窗口应含命中行上下文")
        self.assert_in("0.1 a.u.", win, "参数符号行应落入窗口")
        self.assert_true(len(win) <= TXT_WINDOW_CHARS * 2 + 16,
                         "窗口总长受 2×封顶", f"len={len(win)}")
        # 行对齐：窗口每一行都应是原文完整行
        for line in win.split("\n"):
            if line and line != "……":
                self.assert_in(line, txt, f"窗口行应来自原文完整行: {line[:30]}")
        # 无方法词 + 有 Methods 章节标题 → 仍定位章节
        win2 = locate_txt_window(txt, ["不存在的词xyz"])
        self.assert_in("METHODS", win2.upper(), "章节标题应独立触发定位")
        # 无任何命中 → 空串
        self.assert_eq(locate_txt_window("纯背景文本 " * 100, ["不存在词"]), "",
                       "无任何命中返回空串")

    def _test_arxiv_mapping_dot_to_underscore(self):
        from weekend_pipeline.methods_jobs import (
            arxiv_id_from_source, txt_cache_path,
        )
        self._write_fake_txt()
        self.assert_eq(arxiv_id_from_source("paper:2007-0707.4192-improved"),
                       "0707.4192", "长 stem 提取 arxiv id")
        p = txt_cache_path("paper:2007-0707.4192-improved")
        self.assert_true(p is not None and p.name == "0707_4192.txt",
                         "点号应换下划线映射 txt")
        self.assert_true(p is not None and p.exists(), "假 txt 应命中")
        self.assert_true(txt_cache_path("paper:2026-s41567-x") is None,
                         "非 arxiv 期刊源无 txt（DOI 入库）")
        self.assert_true(txt_cache_path("paper:9999.9999-none") is None,
                         "txt 不存在返回 None")

    # ------------------------------------------------------------------
    # 4. settle 端到端（隔离目录）
    # ------------------------------------------------------------------

    def _test_settle_llm_merge_end_to_end(self):
        from weekend_pipeline import methods_jobs as mj
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR

        self._write_lexicon()
        self._write_seedling_page()
        self._write_fake_txt()
        state = self._write_summaries(with_leads=True)
        saved = self._stub_llm(dict(self._MERGE_OK))
        try:
            result = mj.run_input_methods_settle(state=state, job={})
            self.assert_true(result.get("success"), "settle 应成功", str(result))
            self.assert_eq(result.get("round"), 1, "轮次号 1")
            self.assert_true(result.get("txt_windows", 0) >= 1,
                             "TDSE 源应回原文定位")

            # 方法页验证
            page = mj.read_method_page("TDSE求解器.md")
            fm = page["frontmatter"]
            self.assert_eq(fm.get("settled_count"), 1, "settled_count=1")
            self.assert_eq(fm.get("growth_stage"), "seedling", "1 次仍 seedling")
            self.assert_eq(fm.get("confidence"), 0.6,
                           "一手原文证据 +0.1（0.5→0.6）")
            self.assert_true(fm.get("updated_at", "") >= "2026-",
                             "frontmatter updated_at 已更新")
            self.assert_in(mj.SETTLE_BLOCK_BEGIN, page["body"], "正文含专区标记")
            self.assert_in("ground truth", page["body"], "LLM 原理已并入")
            self.assert_in("| grid spacing | 0.1 a.u. |", page["body"],
                           "参数表已并入（数值+出处）")
            self.assert_in("含时薛定谔方程数值求解", page["body"],
                           "专区外既有正文保留")
            self.assert_in("回原文", page["body"], "证据日志含回原文标记")
            self.assert_true("fallback" not in page["body"], "非降级无 fallback 标记")

            # 产物 json
            out = WEEKEND_INPUT_DIR / f"methods-settle-{_utc_today()}-r1.json"
            self.assert_true(out.exists(), "产物文件应落盘")
            data = json.loads(out.read_text(encoding="utf-8"))
            tdse = next(p for p in data["pages"] if p["page"] == "TDSE求解器.md")
            self.assert_eq(tdse["merged_leads"], 2, "产物记录每页融合条数")
            self.assert_eq(tdse["txt_windows"], 2,
                           "产物记录回原文次数（每条 lead 独立定位一次）")
            self.assert_eq(tdse["fallback"], False, "产物 fallback 标记")
        finally:
            self._restore_llm(saved)

    def _test_settle_growth_promotion_and_repeat(self):
        """第二轮 settle：settled=2 → growing；专区替换不叠加。"""
        from weekend_pipeline import methods_jobs as mj
        self._write_lexicon()
        self._write_seedling_page()
        self._write_fake_txt()
        state = self._write_summaries(with_leads=True)
        saved = self._stub_llm(dict(self._MERGE_OK))
        try:
            mj.run_input_methods_settle(state=state, job={})
            result2 = mj.run_input_methods_settle(state=state, job={})
            self.assert_true(result2.get("success"), "第二轮 settle 成功")
            page = mj.read_method_page("TDSE求解器.md")
            self.assert_eq(page["frontmatter"].get("settled_count"), 2, "settled=2")
            self.assert_eq(page["frontmatter"].get("growth_stage"), "growing",
                           "settled ≥2 → growing（需求 sprout 对齐现有体系）")
            self.assert_eq(page["body"].count(mj.SETTLE_BLOCK_BEGIN), 1,
                           "专区标记唯一（替换不叠加）")
            self.assert_eq(page["body"].count("ground truth"), 1,
                           "LLM 原理替换不重复")
        finally:
            self._restore_llm(saved)

    def _test_settle_llm_failure_fallback_append(self):
        from weekend_pipeline import methods_jobs as mj
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        self._write_lexicon()
        self._write_seedling_page()
        self._write_fake_txt()
        state = self._write_summaries(with_leads=True)
        saved = self._stub_llm(None)  # LLM 不可用/失败
        try:
            result = mj.run_input_methods_settle(state=state, job={})
            self.assert_true(result.get("success"),
                             "LLM 失败降级不应失败整链", str(result))
            self.assert_eq(result.get("fallback_pages"), 2,
                           "TDSE + RABBITT 两页均 fallback")
            page = mj.read_method_page("TDSE求解器.md")
            self.assert_in("fallback", page["body"], "页内应标注 fallback")
            self.assert_in("含时薛定谔方程数值求解", page["body"],
                           "降级保留既有正文")
            self.assert_in("待融合线索", page["body"],
                           "降级附录式追加 lead 线索")
            out = WEEKEND_INPUT_DIR / f"methods-settle-{_utc_today()}-r1.json"
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assert_true(
                all(p.get("fallback") for p in data["pages"] if p["page"] == "TDSE求解器.md"),
                "产物记录 fallback 标记")
        finally:
            self._restore_llm(saved)

    def _test_settle_empty_leads_writes_empty_artifact(self):
        from weekend_pipeline import methods_jobs as mj
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        self._write_lexicon()
        state = self._write_summaries(with_leads=False)
        result = mj.run_input_methods_settle(state=state, job={})
        self.assert_true(result.get("success"), "空 leads 应成功", str(result))
        self.assert_eq(result.get("pages"), 0, "零页融合")
        out = WEEKEND_INPUT_DIR / f"methods-settle-{_utc_today()}-r1.json"
        self.assert_true(out.exists(), "空产物文件应落盘（done 必有产物）")
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assert_eq(data.get("pages"), [], "产物 pages 为空数组")

    def _test_settle_dry_run_zero_writes(self):
        from weekend_pipeline import methods_jobs as mj
        from weekend_pipeline.constants import WEEKEND_INPUT_DIR
        # 用例间防污染：清掉前序用例落盘的产物/方法页/词表
        for f in WEEKEND_INPUT_DIR.glob(f"methods-settle-{_utc_today()}*.json"):
            f.unlink(missing_ok=True)
        methods_dir = self.tmp_root / "knowledge" / "wiki" / "methods"
        if methods_dir.exists():
            shutil.rmtree(methods_dir, ignore_errors=True)
        lex = self.tmp_root / "memory" / "config" / "methods-lexicon.json"
        lex.unlink(missing_ok=True)

        state = self._write_summaries(with_leads=True)
        result = mj.run_input_methods_settle(state=state, job={}, dry_run=True)
        self.assert_true(result.get("success"), "dry-run 成功")
        self.assert_true(result.get("dry_run"), "dry-run 标记")
        self.assert_true(
            not (WEEKEND_INPUT_DIR / f"methods-settle-{_utc_today()}-r1.json").exists(),
            "dry-run 不落产物")
        self.assert_true(
            not (self.tmp_root / "knowledge" / "wiki" / "methods").exists()
            or not any((self.tmp_root / "knowledge" / "wiki" / "methods").iterdir()),
            "dry-run 不写方法页")
        self.assert_true(
            not lex.exists(),
            "dry-run 词表生成不落盘（persist=False）")

    # ------------------------------------------------------------------
    # 5. 注入端（optimize.py）
    # ------------------------------------------------------------------

    def _make_inject_env(self, enabled=True, max_pages=3, max_chars=400):
        """构造注入端环境：课题 + 方法页（含专区）+ 词表/开关。"""
        from proposal_sections import PROPOSAL_SECTIONS
        pid = "general-test-methods-20260906"
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / pid
        sec_dir = prop_dir / "04_proposal" / "sections"
        sec_dir.mkdir(parents=True, exist_ok=True)
        (sec_dir / "scheme.md").write_text(
            "# 研究方案\n\n用 TDSE 求解器与瞬态吸收光谱开展研究。\n", encoding="utf-8")
        (prop_dir / "00_research_idea.md").write_text(
            "# 课题设想\n\n方向：强场超快光学，TDSE 数值模拟与阿秒条纹测量。\n",
            encoding="utf-8")
        lc_path = self.tmp_root / "research_proposals" / "_lifecycle.json"
        lc_path.write_text(json.dumps({"proposals": {pid: {
            "status": "optimizing", "project_type": "general",
            "title": "TDSE 模拟驱动的强场 HHG 课题",
        }}}, ensure_ascii=False, indent=2), encoding="utf-8")

        # 方法页（含 settle 专区）
        methods_dir = self.tmp_root / "knowledge" / "wiki" / "methods"
        methods_dir.mkdir(parents=True, exist_ok=True)
        (methods_dir / "TDSE求解器.md").write_text(
            "---\n"
            'title: "TDSE求解器"\ntype: "methods"\n'
            'growth_stage: "growing"\nconfidence: 0.7\n---\n\n'
            "<!-- methods-settle:v1 -->\n\n"
            "## 原理\n\nTDSE 数值求解是 HHG 理论的 ground truth。\n\n"
            "## 参数表\n\n| 参数 | 数值 | 出处 |\n| --- | --- | --- |\n"
            "| grid spacing | 0.1 a.u. | paper:2007-0707.4192 |\n\n"
            "## 代表作\n\n- 2007-0707.4192-improved-lewenstein\n\n"
            "<!-- /methods-settle:v1 -->\n\n"
            "# TDSE 求解器\n\n旧正文补充说明。\n",
            encoding="utf-8")
        (methods_dir / "VMI.md").write_text(
            "---\ntitle: \"VMI\"\ntype: \"methods\"\n---\n\n# VMI\n\n速度映射成像。\n",
            encoding="utf-8")

        # 词表 + 开关
        cfg_dir = self.tmp_root / "memory" / "config"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        (cfg_dir / "methods-lexicon.json").write_text(json.dumps({
            "entries": [
                {"slug": "tdse-solver", "page": "TDSE求解器.md",
                 "aliases": ["TDSE"], "zh": ["含时薛定谔"]},
                {"slug": "vmi", "page": "VMI.md",
                 "aliases": ["VMI", "velocity map imaging"], "zh": ["速度映射"]},
            ]}, ensure_ascii=False), encoding="utf-8")
        (cfg_dir / "methods-inject.json").write_text(json.dumps({
            "enabled": enabled, "max_pages": max_pages, "max_chars": max_chars,
        }, ensure_ascii=False), encoding="utf-8")

        scheme = next(s for s in PROPOSAL_SECTIONS if s["key"] == "scheme")
        rationale = next(s for s in PROPOSAL_SECTIONS if s["key"] == "rationale")
        return pid, prop_dir, scheme, rationale

    def _test_reference_block_construction(self):
        from proposal_lifecycle import ProposalLifecycle
        import proposal_lifecycle.optimize as opt_mod
        pid, prop_dir, _scheme, _r = self._make_inject_env()
        lc = ProposalLifecycle()
        block = opt_mod._load_methods_reference_block(lc, pid, prop_dir)
        self.assert_in("【方法学专题参考", block, "注入块标题")
        self.assert_in("TDSE求解器", block, "命中方法页进入注入块")
        self.assert_in("0.1 a.u.", block, "参数表数值进入注入块")
        self.assert_in("标注来源文献", block, "引用规范说明")
        self.assert_true("旧正文补充说明" not in block, "专区外正文不进入注入块（只取结构化专区）")

    def _test_reference_block_disabled(self):
        from proposal_lifecycle import ProposalLifecycle
        import proposal_lifecycle.optimize as opt_mod
        pid, prop_dir, _s, _r = self._make_inject_env(enabled=False)
        lc = ProposalLifecycle()
        block = opt_mod._load_methods_reference_block(lc, pid, prop_dir)
        self.assert_eq(block, "", "开关关闭应返回空串")

    def _test_reference_block_budget_caps(self):
        from proposal_lifecycle import ProposalLifecycle
        import proposal_lifecycle.optimize as opt_mod
        # max_chars 截断：设为 60 字符，专区摘要应被截断
        pid, prop_dir, _s, _r = self._make_inject_env(max_chars=60)
        lc = ProposalLifecycle()
        block = opt_mod._load_methods_reference_block(lc, pid, prop_dir)
        self.assert_true(len(block) < 60 * 3 + 200,
                         "每页摘要受 max_chars 截断", f"len={len(block)}")

    def _test_reference_block_no_hit(self):
        """课题文本与词表零交集 → 空串（不硬塞无关方法）。"""
        from proposal_lifecycle import ProposalLifecycle
        import proposal_lifecycle.optimize as opt_mod
        pid, prop_dir, _s, _r = self._make_inject_env()
        # 改写课题文本为无关方向
        lc_path = self.tmp_root / "research_proposals" / "_lifecycle.json"
        data = json.loads(lc_path.read_text(encoding="utf-8"))
        data["proposals"][pid]["title"] = "完全无关的考古学课题"
        lc_path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                           encoding="utf-8")
        (prop_dir / "00_research_idea.md").write_text(
            "青铜器铸造工艺研究。\n", encoding="utf-8")
        lc = ProposalLifecycle()
        block = opt_mod._load_methods_reference_block(lc, pid, prop_dir)
        self.assert_eq(block, "", "零命中课题不注入")

    def _test_writer_prompt_injection_with_switch(self):
        """_run_writer_optimize 组装：scheme 轮含注入块；rationale 轮与
        开关关时不含（stub _run_hermes 捕获 prompt）。"""
        from proposal_lifecycle import ProposalLifecycle
        pid, prop_dir, scheme, rationale = self._make_inject_env()
        captured = {}

        def _fake_hermes(profile, prompt, timeout):
            captured["profile"] = profile
            captured["prompt"] = prompt
            return {"success": False, "error": "stub"}

        lc = ProposalLifecycle()
        lc._run_hermes = _fake_hermes
        lc._run_writer_optimize(pid, prop_dir, "general", {}, 60,
                                focus_section=scheme)
        self.assert_in("【方法学专题参考", captured.get("prompt", ""),
                       "scheme 聚焦轮 writer prompt 应含方法学参考块")
        self.assert_in("TDSE求解器", captured.get("prompt", ""), "块内含方法页")
        self.assert_eq(captured.get("profile"), "writer", "profile 为 writer")

        captured.clear()
        lc._run_writer_optimize(pid, prop_dir, "general", {}, 60,
                                focus_section=rationale)
        self.assert_true("【方法学专题参考" not in captured.get("prompt", ""),
                           "rationale 轮不注入方法学参考")

        # 开关关闭后 scheme 轮也不注入
        cfg = self.tmp_root / "memory" / "config" / "methods-inject.json"
        cfg.write_text(json.dumps({"enabled": False, "max_pages": 3, "max_chars": 400},
                                  ensure_ascii=False), encoding="utf-8")
        captured.clear()
        lc._run_writer_optimize(pid, prop_dir, "general", {}, 60,
                                focus_section=scheme)
        self.assert_true("【方法学专题参考" not in captured.get("prompt", ""),
                           "开关关闭后 scheme 轮不注入")

    def _test_critic_prompt_hint(self):
        """_run_critic 组装：scheme 轮含方法页核对提示（仅提示路径，
        不注入全文）；rationale 轮不含。"""
        from proposal_lifecycle import ProposalLifecycle
        pid, prop_dir, scheme, rationale = self._make_inject_env()
        captured = {}

        def _fake_hermes(profile, prompt, timeout):
            captured["prompt"] = prompt
            return {"success": False, "error": "stub"}

        lc = ProposalLifecycle()
        lc._run_hermes = _fake_hermes
        lc._run_critic(pid, prop_dir, "general", 1, 60, focus_section=scheme)
        self.assert_in("方法学参考核对", captured.get("prompt", ""),
                       "scheme 轮 critic prompt 应含方法页提示")
        self.assert_in("knowledge/wiki/methods", captured.get("prompt", ""),
                       "提示应给出方法页路径")
        self.assert_true("ground truth" not in captured.get("prompt", ""),
                           "critic 不注入方法页全文")

        captured.clear()
        lc._run_critic(pid, prop_dir, "general", 1, 60, focus_section=rationale)
        self.assert_true("方法学参考核对" not in captured.get("prompt", ""),
                           "rationale 轮 critic 不含方法页提示")

    def run_tests(self):
        self._test_job_registered_in_seven_step_chain()
        self._test_group_leads_lexicon_and_new_page()
        self._test_group_leads_strict_threshold()
        self._test_txt_window_hit_and_boundary()
        self._test_arxiv_mapping_dot_to_underscore()
        self._test_settle_llm_merge_end_to_end()
        self._test_settle_growth_promotion_and_repeat()
        self._test_settle_llm_failure_fallback_append()
        self._test_settle_empty_leads_writes_empty_artifact()
        self._test_settle_dry_run_zero_writes()
        self._test_reference_block_construction()
        self._test_reference_block_disabled()
        self._test_reference_block_budget_caps()
        self._test_reference_block_no_hit()
        self._test_writer_prompt_injection_with_switch()
        self._test_critic_prompt_hint()


if __name__ == "__main__":
    suite = WeekendMethodsTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    import test_runner
    test_runner.print_report([suite])
    sys.exit(0 if suite.summary()["failed"] == 0 else 1)
