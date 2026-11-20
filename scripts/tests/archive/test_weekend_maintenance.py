#!/usr/bin/env python3
"""
test_weekend_maintenance.py — 周末维护链（T2，v6.9.99）回归测试

覆盖：
    1. 反思链尾三个新 job 的模板注册（依赖链 + artifact 声明）与
       handler 二元组注册
    2. proposal_calibration 引用对账核心逻辑（隔离目录构造假课题）：
       - 数学区间豁免（$T\\in[50,300]$ 不计为引用，T1 评审教训）
       - frontmatter 编号豁免
       - 引用超界 / 死条目>3 / 占位符 → high
    3. 反馈注入闭环：high → feedback-{N+1}-raw.md 落盘 +
       human_feedback_count 递增；无 high → 只落校准报告不动 count
    4. link_deep_review 复用 retrospective（stub 验证 output_path 指向
       反思目录 + 命名；dry-run 不调用）
    5. kb_taxonomy_apply 空候选写空产物（"done 必有产物"不变式）+
       有候选时调用 apply
    6. cron 清单变更：lc-retrospective 撤出、lc-weekend-summary /
       lc-kb-distill-sunday 登记且参与对账
    7. weekend_summary 收尾汇总（构造数据 → 计数与落盘）

注意：
    本测试不调用 LLM / hermes，运行于隔离临时目录，时钟注入。
"""

import sys
import json
import shutil
import importlib
from datetime import datetime
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


def _refs_md(n: int) -> str:
    lines = ["## 参考文献", ""]
    for i in range(1, n + 1):
        lines.append(f"[{i}] Author{i} A. Title{i}. *Journal* **{i}**(1), 1-9 (2026). DOI: 10.1000/x{i}.")
    return "\n".join(lines) + "\n"


def _make_proposal(root: Path, pid: str, sections: dict, feedback_count: int = 0,
                   register: bool = True):
    """在隔离目录构造假课题（sections 为 {文件名: 正文}）。"""
    prop_dir = root / "research_proposals" / "optimizing" / pid
    sec_dir = prop_dir / "04_proposal" / "sections"
    sec_dir.mkdir(parents=True, exist_ok=True)
    for name, text in sections.items():
        (sec_dir / name).write_text(text, encoding="utf-8")
    if register:
        lc_path = root / "research_proposals" / "_lifecycle.json"
        data = {"proposals": {}}
        if lc_path.exists():
            try:
                data = json.loads(lc_path.read_text(encoding="utf-8"))
            except Exception:
                data = {"proposals": {}}
        data.setdefault("proposals", {})[pid] = {
            "status": "optimizing",
            "project_type": "general",
            "human_feedback_count": feedback_count,
        }
        lc_path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                           encoding="utf-8")
    return prop_dir


class WeekendMaintenanceTests(TestSuite):
    def __init__(self):
        super().__init__("周末维护链测试（T2，v6.9.99）")
        self.tmp_root = None
        self.wp_mod = None

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

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    def _make_pipeline(self):
        from weekend_pipeline.pipeline import WeekendPipeline
        return WeekendPipeline(state_path=self.tmp_root / "memory" / "weekend-pipeline.json")

    # ------------------------------------------------------------------
    # 1. job 模板与 handler 注册
    # ------------------------------------------------------------------

    def _test_reflection_tail_jobs_registered(self):
        p = self._make_pipeline()
        result = p.sync_stage_jobs("reflection")
        self.assert_true(result.get("success"), "sync reflection 成功", result)
        jobs = {j["job_id"]: j for j in p.list_jobs(stage="reflection")}
        for jid in ["reflection_proposal_calibration",
                    "reflection_link_deep_review",
                    "reflection_kb_taxonomy_apply"]:
            self.assert_in(jid, jobs, f"反思链应包含 {jid}")
        self.assert_eq(
            jobs["reflection_proposal_calibration"].get("depends_on"),
            ["reflection_kb_merge_duplicates"],
            "calibration 依赖 kb_merge_duplicates",
        )
        self.assert_eq(
            jobs["reflection_link_deep_review"].get("depends_on"),
            ["reflection_proposal_calibration"],
            "deep_review 依赖 calibration",
        )
        self.assert_eq(
            jobs["reflection_kb_taxonomy_apply"].get("depends_on"),
            ["reflection_link_deep_review"],
            "taxonomy_apply 依赖 deep_review",
        )
        for jid in ["reflection_proposal_calibration",
                    "reflection_link_deep_review",
                    "reflection_kb_taxonomy_apply"]:
            self.assert_true(bool(jobs[jid].get("artifact")),
                            f"{jid} 应声明 artifact（done 必有产物）")

        # handler 二元组注册（防漏注册 → executor 找不到 handler）
        handlers = p.handlers
        self.assert_in(("reflection", "proposal_calibration"), handlers,
                       "handler (reflection, proposal_calibration) 已注册")
        self.assert_in(("reflection", "link_deep_review"), handlers,
                       "handler (reflection, link_deep_review) 已注册")
        self.assert_in(("reflection", "kb_taxonomy_apply"), handlers,
                       "handler (reflection, kb_taxonomy_apply) 已注册")

    def _test_output_sync_artifact_matches_producer(self):
        """output sync job 的 artifact 必须指向 proposal_kb_sync 实际写盘路径。

        回归 v7.3.73：声明为 proposals/proposals-index.md，实际索引写在
        proposals-index.md（父目录），导致每轮 _verify_artifacts 误判产物
        缺失并级联重置 sync 及其下游 extract 作业。
        """
        from weekend_pipeline.jobs import output_stage_jobs
        from proposal_kb_sync import INDEX_FILENAME

        job = output_stage_jobs([])[0]
        self.assert_eq(
            job.get("artifact"),
            f"knowledge/wiki/projects/NSFC-强场超快/{INDEX_FILENAME}",
            "sync job artifact 与 proposal_kb_sync 写盘路径一致",
        )

    def _test_sync_refreshes_stale_artifact_declaration(self):
        """旧 state 中的错误 artifact 应被模板刷新（v7.3.73）。

        回归：合并原为"为空才补"，旧 state 已存有错误路径时永不覆盖，
        _verify_artifacts 每轮误判产物缺失并级联重置 sync/extract。
        """
        p = self._make_pipeline()
        p.sync_stage_jobs("output")
        jid = "output_sync_proposals_to_kb"
        jobs = {j["job_id"]: j for j in p.list_jobs(stage="output")}
        self.assert_true(jid in jobs, "output sync job 已注册")
        before_status = jobs[jid].get("status")
        jobs[jid]["artifact"] = "knowledge/wiki/projects/NSFC-强场超快/proposals/proposals-index.md"
        p._save_unlocked()

        p.sync_stage_jobs("output")
        after = {j["job_id"]: j for j in p.list_jobs(stage="output")}
        from weekend_pipeline.jobs import output_stage_jobs
        self.assert_eq(
            after[jid]["artifact"],
            output_stage_jobs([])[0]["artifact"],
            "再次 sync 后旧 artifact 被模板刷新",
        )
        self.assert_eq(after[jid].get("status"), before_status,
                       "刷新 artifact 不影响运行时状态")

    def _test_maintenance_jobs_do_not_block_recommend(self):
        """维护链挂在 kb_merge 分支，recommend 主链不被新依赖阻塞。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("reflection")
        jobs = {j["job_id"]: j for j in p.list_jobs(stage="reflection")}
        self.assert_eq(
            jobs["reflection_recommend_actions"].get("depends_on"),
            ["reflection_generate_report"],
            "recommend 依赖保持不变（维护链为平行分支）",
        )

    # ------------------------------------------------------------------
    # 2. 引用对账核心逻辑（calibrate_proposal 纯函数级）
    # ------------------------------------------------------------------

    def _test_math_interval_and_frontmatter_exempt(self):
        """数学区间 $T\\in[50,300]$ 与 frontmatter/代码块编号不计为引用。"""
        from weekend_pipeline.maintenance_jobs import calibrate_proposal
        content = (
            "---\n"
            "title: frontmatter 里的编号 [9] 不算引用\n"
            "---\n"
            "\n"
            "在 $T\\in[50,300]$ K 的温区内，已有实验报道 [1]；"
            "理论预言见 [2,3]。代码块里的下标同样豁免：\n"
            "```python\n"
            "arr[77] = f[42]  # 代码下标不算引用\n"
            "```\n"
        )
        prop_dir = _make_proposal(self.tmp_root, "calib-math-exempt", {
            "rationale.md": "立项依据正文，引用 [1]。",
            "content.md": content,
            "references.md": _refs_md(3),
        })
        result = calibrate_proposal(prop_dir)
        stats = result["stats"]
        self.assert_eq(stats["citation_max"], 3,
                       f"最大引用编号应为 3（数学/代码/frontmatter 豁免），实际 {stats}")
        high = [i for i in result["issues"] if i["level"] == "high"]
        self.assert_eq(len(high), 0, f"不应有 high 问题（实际 {high}）")

    def _test_out_of_range_dead_entries_placeholder(self):
        """引用超界 / 死条目>3 / 占位符 → high 级问题。"""
        from weekend_pipeline.maintenance_jobs import calibrate_proposal
        prop_dir = _make_proposal(self.tmp_root, "calib-dirty", {
            "rationale.md": "立项依据。该方向已有奠基工作 [CITE: 待补充]。本课题聚焦此处。",
            "content.md": "研究内容基于 [1,2] 展开，并参考了最新综述 [33]。",
            "references.md": _refs_md(20),
        })
        result = calibrate_proposal(prop_dir)
        types = {i["type"] for i in result["issues"] if i["level"] == "high"}
        self.assert_in("引用超界", types, f"[33] 超界应判 high（实际 {types}）")
        self.assert_in("死条目过多", types, "18 条死条目（>3）应判 high")
        self.assert_in("占位符残留", types, "[CITE: 待补充] 应判 high")
        self.assert_true(result["stats"]["high"] >= 3, "high 合计应 ≥ 3")

    def _test_clean_proposal_no_high(self):
        """无 high 课题：编号齐全、无占位符 → 仅可能存在 low/medium。"""
        from weekend_pipeline.maintenance_jobs import calibrate_proposal
        body = "本课题围绕方向展开。" + "".join(
            f"第{i}段论证引用 [{i}]。" for i in range(1, 4))
        prop_dir = _make_proposal(self.tmp_root, "calib-clean", {
            "rationale.md": body,
            "content.md": body,
            "references.md": _refs_md(3),
        })
        result = calibrate_proposal(prop_dir)
        high = [i for i in result["issues"] if i["level"] == "high"]
        self.assert_eq(len(high), 0, f"clean 课题不应有 high（实际 {high}）")

    def _test_subject_mixed_counted(self):
        """主语混用（本课题/我们 同现）被计数并产出 low 问题。"""
        from weekend_pipeline.maintenance_jobs import calibrate_proposal
        prop_dir = _make_proposal(self.tmp_root, "calib-subject", {
            "rationale.md": "本课题提出新方案；我们在实验中验证了它。引用 [1] [2] [3]。",
            "references.md": _refs_md(3),
        })
        result = calibrate_proposal(prop_dir)
        self.assert_true(result["stats"]["subject_benketi"] >= 1, "本课题计数 ≥1")
        self.assert_true(result["stats"]["subject_women"] >= 1, "我们计数 ≥1")
        types = {i["type"] for i in result["issues"]}
        self.assert_in("主语混用", types, "主语混用应产出问题项")

    # ------------------------------------------------------------------
    # 3. 反馈注入闭环（handler 级，覆盖 _lifecycle.json 递增）
    # ------------------------------------------------------------------

    def _reset_lifecycle(self, entries: dict):
        """重写 _lifecycle.json（handler 级用例彼此隔离，避免纯函数用例
        注册的课题泄漏进 handler 的 optimizing 扫描）。"""
        (self.tmp_root / "research_proposals" / "_lifecycle.json").write_text(
            json.dumps({"proposals": entries}, ensure_ascii=False, indent=2),
            encoding="utf-8")

    def _test_calibration_injects_on_high(self):
        from weekend_pipeline import maintenance_jobs as mj
        _make_proposal(self.tmp_root, "inj-high", {
            "rationale.md": "依据。占位符 [CITE: x] 出现。",
            "content.md": "引用 [33] 超界。",
            "references.md": _refs_md(20),
        }, feedback_count=2, register=False)
        self._reset_lifecycle({"inj-high": {
            "status": "optimizing", "project_type": "general",
            "human_feedback_count": 2,
        }})
        result = mj.run_reflection_proposal_calibration({}, {})
        self.assert_true(result.get("success"), "handler 执行成功", result)
        self.assert_eq(result.get("proposals"), 1, "识别 1 个 optimizing 课题")
        self.assert_true(result.get("high_total", 0) >= 1, "存在 high 问题")
        self.assert_eq(result.get("injected"), ["inj-high"], "high 课题被注入")

        fb_dir = self.tmp_root / "research_proposals" / "optimizing" / "inj-high" / "06_feedback"
        raw = fb_dir / "feedback-3-raw.md"
        self.assert_true(raw.exists(), "feedback-3-raw.md（N+1）应落盘")
        text = raw.read_text(encoding="utf-8")
        self.assert_in("周末校准自动反馈", text, "反馈正文含校准标识")
        calib_files = list(fb_dir.glob("calibration-*.md"))
        self.assert_true(len(calib_files) == 1, "校准报告已落盘")

        # human_feedback_count 2 → 3（注入通道生效前提）
        lc_data = json.loads(
            (self.tmp_root / "research_proposals" / "_lifecycle.json").read_text(encoding="utf-8"))
        self.assert_eq(lc_data["proposals"]["inj-high"].get("human_feedback_count"), 3,
                       "human_feedback_count 应递增到 3")

        # 聚合产物（job artifact 不变式）
        from weekend_pipeline.constants import WEEKEND_REFLECTION_DIR
        agg = list((WEEKEND_REFLECTION_DIR).glob("proposal-calibration-*.md"))
        self.assert_eq(len(agg), 1, "聚合校准汇总应落盘")

        # 注入通道可读性：load_review_feedback_for_optimization 非空
        from proposal_lifecycle.feedback_archive import load_review_feedback_for_optimization
        prop_state = lc_data["proposals"]["inj-high"]
        injected = load_review_feedback_for_optimization(prop_state, "inj-high")
        self.assert_true("周末校准自动反馈" in injected,
                         f"注入通道应读到校准反馈（实际前 80 字：{injected[:80]!r}）")

    def _test_calibration_no_high_keeps_count(self):
        """无 high 问题：只落校准报告，human_feedback_count 不变（防反馈通胀）。"""
        from weekend_pipeline import maintenance_jobs as mj
        _make_proposal(self.tmp_root, "inj-clean", {
            "rationale.md": "本课题引用 [1] [2] [3] 展开。",
            "references.md": _refs_md(3),
        }, feedback_count=1, register=False)
        self._reset_lifecycle({"inj-clean": {
            "status": "optimizing", "project_type": "general",
            "human_feedback_count": 1,
        }})
        result = mj.run_reflection_proposal_calibration({}, {})
        self.assert_true(result.get("success"), "handler 执行成功", result)
        self.assert_eq(result.get("high_total"), 0, "无 high 问题")
        self.assert_eq(result.get("injected"), [], "不应注入")

        lc_data = json.loads(
            (self.tmp_root / "research_proposals" / "_lifecycle.json").read_text(encoding="utf-8"))
        self.assert_eq(lc_data["proposals"]["inj-clean"].get("human_feedback_count"), 1,
                       "无 high 时 count 保持 1")
        fb_dir = self.tmp_root / "research_proposals" / "optimizing" / "inj-clean" / "06_feedback"
        self.assert_true(not (fb_dir / "feedback-2-raw.md").exists(),
                         "不应生成 feedback-2-raw.md")
        self.assert_eq(len(list(fb_dir.glob("calibration-*.md"))), 1,
                       "校准报告仍应落盘")

    def _test_calibration_dry_run_zero_writes(self):
        from weekend_pipeline import maintenance_jobs as mj
        _make_proposal(self.tmp_root, "inj-dry", {
            "rationale.md": "占位符 [CITE: x]。",
            "references.md": _refs_md(2),
        }, feedback_count=0, register=False)
        self._reset_lifecycle({"inj-dry": {
            "status": "optimizing", "project_type": "general",
            "human_feedback_count": 0,
        }})
        result = mj.run_reflection_proposal_calibration({}, {}, dry_run=True)
        self.assert_true(result.get("success"), "dry-run 成功", result)
        self.assert_true(result.get("dry_run"), "结果标记 dry_run")
        fb_dir = self.tmp_root / "research_proposals" / "optimizing" / "inj-dry" / "06_feedback"
        self.assert_true(not fb_dir.exists() or not any(fb_dir.iterdir()),
                         "dry-run 不落任何校准/反馈文件")
        lc_data = json.loads(
            (self.tmp_root / "research_proposals" / "_lifecycle.json").read_text(encoding="utf-8"))
        self.assert_eq(lc_data["proposals"]["inj-dry"].get("human_feedback_count"), 0,
                       "dry-run 不动 count")

    # ------------------------------------------------------------------
    # 4. link_deep_review 复用 retrospective
    # ------------------------------------------------------------------

    def _test_deep_review_wiring(self):
        """handler 调 run_retrospective 并把报告指向反思目录；dry-run 跳过。"""
        from weekend_pipeline import maintenance_jobs as mj
        from weekend_pipeline.constants import WEEKEND_REFLECTION_DIR
        import retrospective

        calls = []

        def _fake_run(period_str="7d", output_path=None):
            calls.append((period_str, output_path))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("# 复盘报告（stub）\n", encoding="utf-8")
            return output_path

        orig = retrospective.run_retrospective
        retrospective.run_retrospective = _fake_run
        try:
            res = mj.run_reflection_link_deep_review({}, {})
            self.assert_true(res.get("success"), "deep_review 成功", res)
            self.assert_eq(len(calls), 1, "run_retrospective 被调用 1 次")
            period, out = calls[0]
            self.assert_eq(period, "7d", "周期 7d")
            self.assert_true(out.parent == WEEKEND_REFLECTION_DIR,
                             f"报告应落反思目录（实际 {out.parent}）")
            self.assert_true(out.name.startswith("link-deep-review-"),
                             f"报告命名 link-deep-review-{{date}}.md（实际 {out.name}）")

            # dry-run：不调用、不写盘
            calls.clear()
            res2 = mj.run_reflection_link_deep_review({}, {}, dry_run=True)
            self.assert_true(res2.get("success"), "dry-run 成功")
            self.assert_true(res2.get("dry_run"), "dry_run 标记")
            self.assert_eq(len(calls), 0, "dry-run 不调用 run_retrospective")
        finally:
            retrospective.run_retrospective = orig

    # ------------------------------------------------------------------
    # 5. kb_taxonomy_apply
    # ------------------------------------------------------------------

    def _test_taxonomy_apply_empty_candidates(self):
        """无候选 → 写空产物文件（done 必有产物），不写 categories.json。"""
        from weekend_pipeline import maintenance_jobs as mj
        from weekend_pipeline.constants import WEEKEND_REFLECTION_DIR
        import kb_taxonomy

        orig_propose = kb_taxonomy.propose_categories
        orig_apply = kb_taxonomy.apply_categories
        kb_taxonomy.propose_categories = lambda *a, **kw: []
        apply_calls = []
        kb_taxonomy.apply_categories = lambda cands: apply_calls.append(cands) or {}
        try:
            res = mj.run_reflection_kb_taxonomy_apply({}, {})
            self.assert_true(res.get("success"), "空候选 handler 成功", res)
            self.assert_eq(res.get("candidates"), 0, "候选 0")
            self.assert_eq(len(apply_calls), 0, "空候选不调用 apply")
            artifacts = list(WEEKEND_REFLECTION_DIR.glob("kb-taxonomy-apply-*.md"))
            self.assert_eq(len(artifacts), 1, "空产物文件已落盘（不变式）")
            text = artifacts[0].read_text(encoding="utf-8")
            self.assert_in("无候选", text, "空产物应说明无候选而非失败")
        finally:
            kb_taxonomy.propose_categories = orig_propose
            kb_taxonomy.apply_categories = orig_apply

    def _test_taxonomy_apply_with_candidates(self):
        from weekend_pipeline import maintenance_jobs as mj
        from weekend_pipeline.constants import WEEKEND_REFLECTION_DIR
        import kb_taxonomy

        cands = [{"name": "新分类", "keywords": ["k"], "pages": 6, "reason": "tag 出现 6 次"}]
        orig_propose = kb_taxonomy.propose_categories
        orig_apply = kb_taxonomy.apply_categories
        apply_calls = []
        kb_taxonomy.propose_categories = lambda *a, **kw: cands
        kb_taxonomy.apply_categories = (
            lambda c: apply_calls.append(c) or {"success": True, "added": 1, "total": 2})
        try:
            res = mj.run_reflection_kb_taxonomy_apply({}, {})
            self.assert_true(res.get("success"), "有候选 handler 成功", res)
            self.assert_eq(len(apply_calls), 1, "apply_categories 被调用 1 次")
            self.assert_eq(apply_calls[0], cands, "apply 收到候选清单")
            artifacts = list(WEEKEND_REFLECTION_DIR.glob("kb-taxonomy-apply-*.md"))
            self.assert_eq(len(artifacts), 1, "执行报告已落盘")
            self.assert_in("新增 1", artifacts[0].read_text(encoding="utf-8"),
                           "报告含新增数量")
        finally:
            kb_taxonomy.propose_categories = orig_propose
            kb_taxonomy.apply_categories = orig_apply

    def _test_taxonomy_apply_dry_run_no_writes(self):
        from weekend_pipeline import maintenance_jobs as mj
        from weekend_pipeline.constants import WEEKEND_REFLECTION_DIR
        import kb_taxonomy

        # 清掉前序用例的产物（同一套件共享反思目录）
        for f in WEEKEND_REFLECTION_DIR.glob("kb-taxonomy-apply-*.md"):
            f.unlink()

        orig_propose = kb_taxonomy.propose_categories
        orig_apply = kb_taxonomy.apply_categories
        kb_taxonomy.propose_categories = lambda *a, **kw: []
        kb_taxonomy.apply_categories = lambda c: {"success": True, "added": 0, "total": 0}
        try:
            res = mj.run_reflection_kb_taxonomy_apply({}, {}, dry_run=True)
            self.assert_true(res.get("success"), "dry-run 成功")
            self.assert_eq(
                list(WEEKEND_REFLECTION_DIR.glob("kb-taxonomy-apply-*.md")), [],
                "dry-run 不落产物文件")
        finally:
            kb_taxonomy.propose_categories = orig_propose
            kb_taxonomy.apply_categories = orig_apply

    # ------------------------------------------------------------------
    # 6. cron 清单变更
    # ------------------------------------------------------------------

    def _test_cron_manifest_t2(self):
        from lifecycle.cron_manifest import CRON_MANIFEST, validate_cron_topology
        self.assert_true("lc-retrospective" not in CRON_MANIFEST,
                         "lc-retrospective 应撤出清单（复盘移入周日反思链）")
        self.assert_eq(CRON_MANIFEST.get("lc-weekend-summary", {}).get("schedule"),
                       "0 22 * * 0", "lc-weekend-summary 周日 22:00")
        self.assert_eq(CRON_MANIFEST.get("lc-kb-distill-sunday", {}).get("schedule"),
                       "0 20 * * 0", "lc-kb-distill-sunday 周日 20:00")

        # 缺失检出：清单生成的基础集去掉 summary → missing
        ok_crons = [{"name": n, "schedule": (s.get("schedule") or "0 9 * * 1")}
                    for n, s in CRON_MANIFEST.items()]
        self.assert_eq(validate_cron_topology(ok_crons), [], "清单一致拓扑零问题")
        miss = [c for c in ok_crons
                if c["name"] not in ("lc-weekend-summary", "lc-kb-distill-sunday")]
        kinds = {i["kind"] for i in validate_cron_topology(miss)}
        self.assert_eq(kinds, {"missing"}, "新 cron 缺失应被检出且仅报 missing")

    # ------------------------------------------------------------------
    # 7. weekend_summary 收尾汇总
    # ------------------------------------------------------------------

    def _test_summary_collect_and_write(self):
        import weekend_summary as ws
        dates = ["2026-09-05", "2026-09-06"]
        winput = self.tmp_root / "memory" / "weekend-input"
        winput.mkdir(parents=True, exist_ok=True)
        (winput / "summaries-2026-09-05-r1.json").write_text(
            json.dumps({"summaries": [{}, {}, {}, {}, {}]}), encoding="utf-8")
        (winput / "summaries-2026-09-06-r2.json").write_text(
            json.dumps({"summaries": [{}, {}]}), encoding="utf-8")
        (winput / "summaries-2026-09-05.json").write_text(
            json.dumps({"summaries": [{}, {}, {}, {}, {}]}), encoding="utf-8")  # 旧名不重复计
        (winput / "clusters-week-2026-09-05.json").write_text(
            json.dumps({"new_clusters": [{}, {}]}), encoding="utf-8")
        (winput / "routes-2026-09-06.json").write_text(
            json.dumps({"routes": [{"action": "new"}, {"action": "merge"}]}), encoding="utf-8")

        digest = ws.collect_digest_stats(self.tmp_root, dates)
        self.assert_eq(digest, {"rounds": 2, "papers": 7}, "轮次/篇数（旧名快照不重复计）")
        clusters = ws.collect_cluster_stats(self.tmp_root, dates)
        self.assert_eq(clusters["new_clusters"], 2, "新成簇 2")
        routes = ws.collect_route_stats(self.tmp_root, dates)
        self.assert_eq(routes["actions"].get("new"), 1, "new 路由 1 条")

        # pipeline state 口径的校准统计
        pipe = self.tmp_root / "memory" / "weekend-pipeline.json"
        pipe.write_text(json.dumps({"jobs": [{
            "job_id": "reflection_proposal_calibration", "status": "done",
            "result": {"success": True, "high_total": 3, "injected": ["a", "b"]},
        }]}, ensure_ascii=False), encoding="utf-8")
        cal = ws.collect_calibration_stats(self.tmp_root, dates)
        self.assert_eq(cal["high_total"], 3, "high 数读自 pipeline state")
        self.assert_eq(cal["injected_count"], 2, "注入课题数读自 pipeline state")

        res = ws.generate_summary(root=self.tmp_root,
                                  now=datetime(2026, 9, 6, 22, 0, 0),
                                  write=True)
        self.assert_true(res.get("success"), "汇总生成成功")
        out = self.tmp_root / "memory" / "weekend-summary-2026-09-06.md"
        self.assert_true(out.exists(), "汇总文件已落盘")
        text = out.read_text(encoding="utf-8")
        self.assert_in("消化轮次：2 轮", text, "汇总含轮次")
        self.assert_in("校准 high 问题：3 个", text, "汇总含校准 high 数")
        self.assert_in("new=1", text, "汇总含路由分布")

    def _test_summary_caliber_marker_fallback(self):
        """pipeline state 无结果时回退扫描 calibration marker。"""
        import weekend_summary as ws
        # 清掉前一用例写入的 pipeline state（口径切换为回退源），
        # 并清理 handler 用例留下的校准报告（同目录会被 glob 扫到）
        pipe = self.tmp_root / "memory" / "weekend-pipeline.json"
        if pipe.exists():
            pipe.unlink()
        for f in (self.tmp_root / "research_proposals" / "optimizing").glob(
                "*/06_feedback/calibration-*.md"):
            f.unlink()
        fb = self.tmp_root / "research_proposals" / "optimizing" / "p9" / "06_feedback"
        fb.mkdir(parents=True, exist_ok=True)
        (fb / "calibration-2026-09-06.md").write_text(
            "# x\n\n<!-- calibration: {\"proposal_id\": \"p9\", "
            "\"high\": 4, \"issues\": 7, \"date\": \"2026-09-06\"} -->\n",
            encoding="utf-8")
        cal = ws.collect_calibration_stats(self.tmp_root, ["2026-09-05", "2026-09-06"])
        self.assert_eq(cal["high_total"], 4, "回退源解析 high=4")
        self.assert_eq(cal["source"], "calibration-reports", "口径标记为报告回退")

    def run_tests(self):
        self._test_reflection_tail_jobs_registered()
        self._test_output_sync_artifact_matches_producer()
        self._test_sync_refreshes_stale_artifact_declaration()
        self._test_maintenance_jobs_do_not_block_recommend()
        self._test_math_interval_and_frontmatter_exempt()
        self._test_out_of_range_dead_entries_placeholder()
        self._test_clean_proposal_no_high()
        self._test_subject_mixed_counted()
        self._test_calibration_injects_on_high()
        self._test_calibration_no_high_keeps_count()
        self._test_calibration_dry_run_zero_writes()
        self._test_deep_review_wiring()
        self._test_taxonomy_apply_empty_candidates()
        self._test_taxonomy_apply_with_candidates()
        self._test_taxonomy_apply_dry_run_no_writes()
        self._test_cron_manifest_t2()
        self._test_summary_collect_and_write()
        self._test_summary_caliber_marker_fallback()


if __name__ == "__main__":
    from test_runner import print_report
    suite = WeekendMaintenanceTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    print_report([suite])
    summary = suite.summary()
    sys.exit(0 if summary["failed"] == 0 else 1)
