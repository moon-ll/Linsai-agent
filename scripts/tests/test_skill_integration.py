#!/usr/bin/env python3
"""
test_skill_integration.py — 桌面技能整合回归测试（v6.10.31）

覆盖两个整合点：
    1. research-proposal 六模块模板 → idea_generator：
       prompt 注入（route/validation/comparison + 禁止模糊表述）
       与 LLM 输出形状防御（_coerce_idea_fields）
    2. academic-literature-search → external_fetcher：
       search_academic 并发聚合（monkeypatch 离线验证）/ year_from
       年份过滤 / BibTeX 与 RIS 引用格式输出

v7.0.0 适配（skill 架构迭代，用户裁决 2026-09-25）：六模块方法论
（字段质量定义/禁止模糊表述反例）已收敛至 .hermes/skills/
research-proposal/SKILL.md 三节，idea_generator 经 skill_loader
inject_block 注入。整合点 1 的 prompt 断言相应拆分：JSON 输出契约
（字段名 + comparison 子结构）仍断言 prompt 内容；方法论注入改为
源码级 inject_block 调用断言（隔离环境 PROJECT_ROOT 被打桩，
skill 注入块 fail-open 可能为空串，不能对 prompt 内容断言方法论）。

零 LLM、零网络（检索源全部打桩），运行于隔离临时目录。
"""

import sys
import shutil
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


class SkillIntegrationTests(TestSuite):
    def __init__(self):
        super().__init__("桌面技能整合测试（v6.10.31）")
        self.tmp_root = None

    def setup(self):
        self.tmp_root = create_isolated_env()

        for mod_name in list(sys.modules.keys()):
            if mod_name in ("idea_generator", "external_fetcher", "paths") \
                    or mod_name.startswith("proposal_lifecycle") \
                    or mod_name.startswith("weekend_pipeline"):
                del sys.modules[mod_name]

        import paths
        self._orig_project_root = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root

        patch_module_root("idea_generator", self.tmp_root)
        patch_module_root("external_fetcher", self.tmp_root)
        patch_module_root("proposal_lifecycle", self.tmp_root)
        patch_module_root("weekend_pipeline", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    # ------------------------------------------------------------------
    # 整合点 1：research-proposal 六模块模板 → idea_generator
    # ------------------------------------------------------------------

    def _test_idea_prompt_contains_six_modules(self):
        """自动生成 prompt 注入六模块模板关键要素（v7.0.0 适配）。

        JSON 输出契约（字段名 + comparison 子结构）断言 prompt 内容；
        方法论（字段质量定义/禁止模糊表述反例）已收敛至
        .hermes/skills/research-proposal/SKILL.md，改为源码级
        inject_block 调用断言（见文件头部 v7.0.0 适配说明）。
        """
        import idea_generator as ig

        prompt = ig._build_idea_prompt(
            {"briefings": [], "papers": [], }, [])
        # route/validation/comparison 三个新字段（JSON 输出契约）
        self.assert_in("route:", prompt, "技术路线分步字段")
        self.assert_in("validation:", prompt, "验证方案字段")
        self.assert_in("comparison:", prompt, "与参考工作的区别字段")
        # 对比表四要素（comparison 子结构，_coerce_idea_fields 解析契约）
        self.assert_in("increment", prompt, "增量贡献")
        self.assert_in("boundary", prompt, "边界界定")
        self.assert_in("depends", prompt, "依赖关系")
        self.assert_in("core_refs", prompt, "核心对比文献")
        # v7.0.0: 六模块方法论经 skill_loader 注入（源码级防误删守卫）
        ig_src = (_SCRIPTS_DIR / "idea_generator.py").read_text(encoding="utf-8")
        self.assert_in("inject_block", ig_src,
                       "六模块方法论应经 skill_loader.inject_block 注入")
        self.assert_in('"research-proposal"', ig_src,
                       "注入 skill 应为 research-proposal")
        self.assert_in("三、课题设想六模块", ig_src,
                       "应注入课题设想六模块节")

    def _test_coerce_route_string_to_list(self):
        """route 形状防御：整段字符串 → 拆分为条目；垃圾值 → 空列表。"""
        import idea_generator as ig

        idea = ig._coerce_idea_fields({
            "route": "步骤一：基于TDDFT计算能带\n步骤二：时间分辨HHG光谱测量\n步骤三：对比验证",
        })
        self.assert_eq(len(idea["route"]), 3, "整段 route 应拆成 3 步")
        self.assert_in("TDDFT", idea["route"][0], "步骤内容保留")
        self.assert_eq(idea["route"][2], "对比验证", "4 字短步骤不应被误滤（v6.10.34）")

        idea2 = ig._coerce_idea_fields({"route": 42})
        self.assert_eq(idea2["route"], [], "非字符串/非列表 → 空列表")

    def _test_coerce_comparison_shape_defense(self):
        """comparison 形状防御：缺子键补空、截断上限、垃圾输入兜底。"""
        import idea_generator as ig

        # 正常输入：保留四要素
        idea = ig._coerce_idea_fields({
            "comparison": {
                "core_refs": ["Rana et al. 2022"],
                "table": [{"dimension": "体系", "existing": "石墨烯", "ours": "TMDC异质结"}],
                "increment": ["首次扩展到非中心对称体系"],
                "boundary": ["不涉及超快结构相变"],
                "depends": ["边带观测方法"],
            },
        })
        comp = idea["comparison"]
        self.assert_eq(comp["core_refs"], ["Rana et al. 2022"], "core_refs 保留")
        self.assert_eq(comp["table"][0]["ours"], "TMDC异质结", "对比表内容保留")
        self.assert_eq(len(comp["increment"]), 1, "increment 保留")

        # 垃圾输入：全部兜底为空结构（不抛异常）
        idea2 = ig._coerce_idea_fields({"comparison": "不是字典"})
        comp2 = idea2["comparison"]
        self.assert_eq(comp2["core_refs"], [], "垃圾 comparison → 空结构")
        self.assert_eq(comp2["table"], [], "垃圾 comparison → 空 table")

        # 缺字段：补空默认
        idea3 = ig._coerce_idea_fields({})
        self.assert_eq(idea3["comparison"]["increment"], [], "缺失字段补空")
        self.assert_eq(idea3["validation"], "", "validation 缺失补空串")

    def _test_dossier_renders_comparison_section(self):
        """立项决策包渲染六模块增量章节（技术路线/区别对比表）。"""
        import json
        import idea_generator as ig

        idea = {
            "title": "强场调控交变磁自旋劈裂",
            "keywords": ["强场", "交变磁"],
            "background": "背景文本",
            "route": ["步骤一：TDDFT 计算", "步骤二：HHG 测量验证"],
            "validation": "对比无泵浦对照组排除热效应",
            "comparison": {
                "core_refs": ["文献A"],
                "table": [{"dimension": "调控手段", "existing": "静态应变", "ours": "强场THz"}],
                "increment": ["首次强场动态调控"],
                "boundary": ["不涉及室温器件化"],
                "depends": ["应变工程先验"],
            },
        }
        # 种 lifecycle：drafts 阶段 + 课题目录，dossier 才会落盘
        prop_dir = self.tmp_root / "research_proposals" / "drafts" / "general-test-skill-20260921"
        prop_dir.mkdir(parents=True, exist_ok=True)
        state_path = self.tmp_root / "research_proposals" / "_lifecycle.json"
        state_path.write_text(json.dumps({
            "proposals": {"general-test-skill-20260921": {
                "status": "drafts", "title": idea["title"]}},
        }, ensure_ascii=False), encoding="utf-8")

        ig.generate_idea_dossier(idea, [], "general-test-skill-20260921")
        md = prop_dir / "00_idea-dossier.md"
        self.assert_true(md.exists(), "dossier 应落盘")
        text = md.read_text(encoding="utf-8")
        self.assert_in("## 技术路线", text, "dossier 应含技术路线章节")
        self.assert_in("TDDFT 计算", text, "技术路线步骤渲染")
        self.assert_in("## 验证方案", text, "dossier 应含验证方案章节")
        self.assert_in("## 与参考工作的区别", text, "dossier 应含区别章节")
        self.assert_in("首次强场动态调控", text, "增量贡献渲染")
        self.assert_in("| 调控手段 |", text, "对比表渲染")

    # ------------------------------------------------------------------
    # 整合点 2：academic-literature-search → external_fetcher
    # ------------------------------------------------------------------

    def _test_paper_year_fallback(self):
        """年份口径：year 字段优先，缺失从 date 前 4 位回退。"""
        import external_fetcher as ef

        self.assert_eq(ef._paper_year({"year": 2024}), 2024, "year 字段")
        self.assert_eq(ef._paper_year({"date": "2015-03-01"}), 2015, "date 回退")
        self.assert_eq(ef._paper_year({}), 0, "均无返回 0")

    def _test_format_bibtex_ris(self):
        """BibTeX/RIS 输出格式与空列表兜底。"""
        import external_fetcher as ef

        fixture = [
            {"title": "Solid-state HHG", "authors": ["Alice Zhang", "Bob Li"],
             "venue": "Nat. Phys.", "year": 2024, "doi": "10.1038/x",
             "url": "https://doi.org/10.1038/x"},
            {"title": "Old theory", "authors": [], "date": "2015-01-01"},
        ]
        bib = ef.format_bibtex(fixture)
        self.assert_eq(bib.count("@article{"), 2, "BibTeX 两条目")
        self.assert_in("author = {Alice Zhang and Bob Li}", bib, "作者 and 连接")
        self.assert_in("author = {Unknown}", bib, "无作者兜底 Unknown")
        self.assert_in("year = {2015}", bib, "date 回退年份")
        self.assert_in("zhang20241", bib, "key=首作者姓+年+序号")

        ris = ef.format_ris(fixture)
        self.assert_eq(ris.count("TY  - JOUR"), 2, "RIS 两条目")
        self.assert_in("AU  - Alice Zhang", ris, "RIS 作者行")
        self.assert_in("PY  - 2015", ris, "RIS 年份")
        self.assert_in("ER  - ", ris, "RIS 结束标记")

        self.assert_eq(ef.format_bibtex([]), "", "空列表 BibTeX")
        self.assert_eq(ef.format_ris([]), "", "空列表 RIS")

    def _test_search_academic_offline(self):
        """并发聚合（离线打桩）：去重合并/单源失败容错/year_from 过滤。"""
        import external_fetcher as ef

        src_a = [
            {"source": "openalex", "title": "HHG in solids", "doi": "10.1/x",
             "year": 2024, "citation_count": 50, "authors": ["A"], "venue": "NP"},
            {"source": "openalex", "title": "Old HHG", "doi": "10.1/y",
             "year": 2015, "citation_count": 99, "authors": ["B"]},
        ]
        src_b = [
            {"source": "arxiv", "title": "HHG in solids (dupe)", "doi": "10.1/x",
             "year": 2024, "citation_count": 10, "authors": ["C"], "abstract": "补全字段"},
            {"source": "arxiv", "title": "Fresh HHG", "arxiv_id": "2509.11111",
             "year": 2025, "citation_count": 5, "authors": ["D"]},
        ]

        orig = (ef.fetch_openalex, ef.fetch_arxiv,
                ef.fetch_semantic_scholar, ef.fetch_pubmed)

        def _boom(query, max_results=5, **kw):
            raise RuntimeError("模拟单源故障")

        ef.fetch_openalex = lambda query, max_results=5, **kw: list(src_a)
        ef.fetch_arxiv = lambda query, max_results=5, **kw: list(src_b)
        ef.fetch_semantic_scholar = _boom  # 单源失败不应拖垮整体
        try:
            merged = ef.search_academic("hhg", max_results=5,
                                        sources=("openalex", "arxiv", "semantic_scholar"))
            # 去重：10.1/x 两条合并为一条
            dois = [m.get("doi") for m in merged if m.get("doi")]
            self.assert_eq(dois.count("10.1/x"), 1, "DOI 去重合并")
            # 字段补全：arxiv 侧 abstract 补进 openalex 条目
            dupe = next(m for m in merged if m.get("doi") == "10.1/x")
            self.assert_eq(dupe.get("abstract"), "补全字段", "重复条目字段补全")
            self.assert_eq(dupe.get("citation_count"), 50, "去重保留首见来源分数字段")
            self.assert_true(len(merged) == 3, f"3 条独立结果（实际 {len(merged)}）")
            # 排序：citation 降序（99 → 50 → 5）
            self.assert_eq(merged[0]["doi"], "10.1/y", "按引用数降序")

            # year_from 过滤：2015 条目被裁掉
            kept = ef.search_academic("hhg", max_results=5,
                                      sources=("openalex", "arxiv"), year_from=2020)
            years = [m.get("year") for m in kept]
            self.assert_true(all(y >= 2020 for y in years), f"年份全部 ≥2020（实际 {years}）")
            self.assert_eq(len(kept), 2, "2015 条目被过滤")
        finally:
            (ef.fetch_openalex, ef.fetch_arxiv,
             ef.fetch_semantic_scholar, ef.fetch_pubmed) = orig

    def _test_multi_source_search_config(self):
        """优化链路检索配置：references 轮限近 3 年，其余章节不限年。"""
        from proposal_lifecycle.optimize import (
            _multi_source_search_config, _MULTI_SOURCE_SOURCES,
        )
        from datetime import datetime, timezone

        self.assert_in("semantic_scholar", _MULTI_SOURCE_SOURCES, "源扩展含 S2")

        # references 轮：三源 + 近 3 年过滤
        srcs, yf = _multi_source_search_config({"key": "references", "title": "参考文献"})
        self.assert_eq(srcs, _MULTI_SOURCE_SOURCES, "references 轮源清单")
        self.assert_eq(yf, datetime.now(timezone.utc).year - 3,
                       "references 轮 year_from = 当前年 - 3")

        # 其他章节：不限年（经典文献可入）
        srcs2, yf2 = _multi_source_search_config({"key": "rationale", "title": "立项依据"})
        self.assert_true(yf2 is None, "rationale 轮不限年（机制溯源需经典文献）")

        # full_review 轮：限近 3 年（references 轮无 lit_search job，
        # full_review 检索是 references 时效补充的实际载体）
        _, yf_fr = _multi_source_search_config({"key": "full_review", "title": "整篇"})
        self.assert_eq(yf_fr, datetime.now(timezone.utc).year - 3,
                       "full_review 轮同样限近 3 年（v6.10.35）")

        # 无聚焦（整篇轮）：不限年
        srcs3, yf3 = _multi_source_search_config(None)
        self.assert_true(yf3 is None, "整篇轮不限年")
        self.assert_eq(srcs3, _MULTI_SOURCE_SOURCES, "整篇轮源清单一致")

    def _test_enrich_idea_six_modules(self):
        """compose new 路由六模块补全：LLM 正常/失败/垃圾输出三态。"""
        from weekend_pipeline import input_jobs

        base_idea = {"title": "强场调控交变磁自旋劈裂", "background": "背景",
                     "keywords": ["强场"]}
        cluster = {"title": "同上", "summary": "知识卡综合文本" * 10,
                   "research_gap": "缺动态调控",
                   "open_questions": ["Q1"],
                   "member_summaries": [{"title": "文献A"}, {"title": "文献B"}]}

        orig_llm = input_jobs._llm_json
        orig_avail = input_jobs.is_llm_available

        # ① LLM 正常：三字段注入 + 清洗生效
        input_jobs.is_llm_available = lambda: True
        input_jobs._llm_json = lambda *a, **kw: {
            "route": "步骤一：TDDFT 计算\n步骤二：HHG 测量\n步骤三：对比验证",
            "validation": "对照组排除热效应",
            "comparison": {"core_refs": ["文献A"], "increment": ["首次动态调控"],
                           "table": [{"dimension": "调控", "existing": "静态",
                                      "ours": "强场THz"}]},
        }
        try:
            enriched = input_jobs._enrich_idea_six_modules(dict(base_idea), cluster)
            self.assert_eq(len(enriched["route"]), 3, "route 字符串应拆成 3 步")
            self.assert_in("TDDFT", enriched["route"][0], "route 步骤内容保留")
            self.assert_eq(enriched["validation"], "对照组排除热效应", "validation 注入")
            self.assert_eq(enriched["comparison"]["core_refs"], ["文献A"],
                           "comparison 注入并清洗")
            self.assert_eq(enriched["title"], base_idea["title"],
                           "已有 title 不被重写（防漂移）")

            # ② LLM 失败（None）：原 idea 返回不阻塞
            input_jobs._llm_json = lambda *a, **kw: None
            degraded = input_jobs._enrich_idea_six_modules(dict(base_idea), cluster)
            self.assert_eq(degraded, base_idea, "LLM 失败应原样返回（降级不阻塞）")

            # ③ LLM 垃圾输出（非 dict）：原样返回
            input_jobs._llm_json = lambda *a, **kw: ["数组形状"]
            garbage = input_jobs._enrich_idea_six_modules(dict(base_idea), cluster)
            self.assert_eq(garbage, base_idea, "非 dict 输出应原样返回")

            # ④ LLM 不可用：直接原样返回
            input_jobs.is_llm_available = lambda: False
            unavailable = input_jobs._enrich_idea_six_modules(dict(base_idea), cluster)
            self.assert_eq(unavailable, base_idea, "LLM 不可用应原样返回")
        finally:
            input_jobs._llm_json = orig_llm
            input_jobs.is_llm_available = orig_avail

    def _test_register_title_fallback(self):
        """注册课题 title 落 state + brief 占位回退（v6.10.36）。

        09-20 批 7 个新课题 brief 全部"（待生成）"——drafts 阶段无申请
        书，_extract_proposal_title 只能从旧 brief 提到占位串。
        """
        from proposal_lifecycle import ProposalLifecycle

        lc = ProposalLifecycle()
        reg = lc.register(
            proposal_id="general-title-test-20260921",
            project_type="general", source="auto_idea",
            title="结构压缩调控固态高次谐波的截止能量增强",
        )
        self.assert_true(reg.get("success"), "注册应成功", str(reg))

        # state 存了可读标题
        st = lc._get_proposal_state("general-title-test-20260921")
        self.assert_eq(st.get("title"), "结构压缩调控固态高次谐波的截止能量增强",
                       "title 应落 state")

        # brief 课题名称来自 state 回退（非"（待生成）"）
        brief = (self.tmp_root / "research_proposals" / "drafts"
                 / "general-title-test-20260921" / "00_proposal-brief.md").read_text(encoding="utf-8")
        self.assert_in("结构压缩调控固态高次谐波的截止能量增强", brief,
                       "brief 应显示可读标题")

        # register_from_idea 路径也传 title
        reg2 = lc.register_from_idea({
            "title": "强场调控交变磁自旋劈裂与高次谐波读出",
            "keywords": ["strong-field", "altermagnet", "hhg"],
            "background": "bg", "gap": "g", "content": [], "approach": "a",
            "innovations": ["i"], "sources": [], "reliability": "derived",
        }, project_type="general")
        self.assert_true(reg2.get("success"), "register_from_idea 应成功", str(reg2))
        st2 = lc._get_proposal_state(reg2.get("proposal_id", ""))
        self.assert_eq(st2.get("title"), "强场调控交变磁自旋劈裂与高次谐波读出",
                       "register_from_idea 的 title 应落 state")

    def _test_v704_wiring_guards(self):
        """v7.0.4 接线守卫：monitor/panel/kb_distill 的 skill 注入防误删。

        源码级断言（仿 test_mechanism_hardening 守卫模式）——隔离环境
        PROJECT_ROOT 被打桩，运行时注入块可能为空，故守卫源码引用而非
        运行时效果。绑定表归位守卫：hermes_pipeline 不再自带 STAGE_SKILLS。
        """
        from pathlib import Path as _P
        scripts = _P(__file__).parent.parent

        monitor_src = (scripts / "adversarial" / "monitor.py").read_text(encoding="utf-8")
        self.assert_true(
            'inject_block' in monitor_src and '"quality-review"' in monitor_src,
            "monitor.py 应注入 quality-review skill（串通检测/评审纪律）",
        )
        panel_src = (scripts / "panel_review.py").read_text(encoding="utf-8")
        self.assert_true(
            'inject_block' in panel_src and '_role_skill_block' in panel_src,
            "panel_review.py 应按角色注入 skill（_role_skill_block）",
        )
        kb_src = (scripts / "kb_distill.py").read_text(encoding="utf-8")
        self.assert_true(
            'inject_block' in kb_src and '"literature-reading"' in kb_src,
            "kb_distill.py 应注入 literature-reading skill（五要素标准）",
        )
        hp_src = (scripts / "hermes_pipeline.py").read_text(encoding="utf-8")
        self.assert_true(
            "STAGE_SKILLS: " not in hp_src and "get_stage_skills" in hp_src,
            "hermes_pipeline 应经 get_stage_skills 消费绑定表（不再自带表）",
        )
        loader_src = (scripts / "skill_loader.py").read_text(encoding="utf-8")
        self.assert_true(
            "PIPELINE_STAGE_SKILLS" in loader_src,
            "skill_loader 应含 PIPELINE_STAGE_SKILLS 绑定表",
        )
        # v7.0.5 方法学整理链接线守卫
        kb_src2 = (scripts / "kb_distill.py").read_text(encoding="utf-8")
        self.assert_true(
            '"五、方法学整理"' in kb_src2,
            "kb_distill 应注入 literature-reading 五节（方法卡标准）",
        )
        self.assert_true(
            "方法卡格式详述" in kb_src2,
            "蒸馏 prompt 应要求方法密度高的论文按方法卡格式提取",
        )
        ex_src = (scripts / "lifecycle" / "executor.py").read_text(encoding="utf-8")
        self.assert_true(
            "参数溯源" in ex_src and "wiki/methods" in ex_src,
            "update_method_manual 应吸收 KB 方法页（v7.2.11 两阶段：阶段1 source_hint 规划 + 阶段2 参数溯源并入）",
        )
        lr_skill = (scripts.parent / ".hermes" / "skills" / "literature-reading"
                    / "SKILL.md").read_text(encoding="utf-8")
        self.assert_true(
            "方法卡四要素" in lr_skill and "五、方法学整理" in lr_skill,
            "literature-reading 应含五节方法学整理（方法卡标准）",
        )
        mm_skill = (scripts.parent / ".hermes" / "skills" / "method-manual"
                    / "SKILL.md").read_text(encoding="utf-8")
        self.assert_true(
            "外部方法吸收" in mm_skill,
            "method-manual 一节应含外部方法吸收纪律（第 6 条）",
        )

        # 真相源收敛守卫：standards JSON 文字规范已收缩为指针
        import json as _json
        std = _json.loads((scripts.parent / "memory" / "nsfc-standards.json").read_text(encoding="utf-8"))
        ws = std.get("general_principles", {}).get("writing_style_rules", {})
        self.assert_true(
            "core" not in ws and "_source" in ws and "anti_ai_patterns" in ws,
            "writing_style_rules 应为指针 + anti_ai_patterns（文字规范单一真相源=skill）",
        )

    def run_tests(self):
        self._test_v704_wiring_guards()
        self._test_idea_prompt_contains_six_modules()
        self._test_coerce_route_string_to_list()
        self._test_coerce_comparison_shape_defense()
        self._test_dossier_renders_comparison_section()
        self._test_paper_year_fallback()
        self._test_format_bibtex_ris()
        self._test_search_academic_offline()
        self._test_multi_source_search_config()
        self._test_enrich_idea_six_modules()
        self._test_register_title_fallback()


if __name__ == "__main__":
    suite = SkillIntegrationTests()
    suite.setup()
    try:
        suite.run_tests()
        s = suite.summary()
        for r in s.get("results", []):
            if not r.passed:
                print(f"✗ {r.name} | {r.msg}")
        print(f"通过 {s['passed']}/{s['total']}")
        sys.exit(0 if s.get("failed", 1) == 0 else 1)
    finally:
        suite.teardown()
