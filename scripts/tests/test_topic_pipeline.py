# -*- coding: utf-8 -*-
"""topic_pipeline（v8 课题启动包管线）回归测试。

覆盖：注册与新颖性硬门、单遍深研（含 mock hermes runner）、B4 组装、
验收自检 A1-A4/G1-G2、阶段流转（questions→kickoff→ready→active→archive）、
否决台账、v7 迁移、周末链桥接、每日调度。

零 LLM / 零 hermes：runner 用 mock 写产物；数据域重定向到临时目录。
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from topic_pipeline import (  # noqa: E402
    acceptance,
    assemble,
    constants,
    daily,
    deep_research,
    migration,
    registration,
    similarity,
    state as tstate,
    weekend_bridge,
)


class TopicPipelineBase(unittest.TestCase):
    """公共基座：临时数据域 + 迁移 LEGACY_ROOT 打桩。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "research_topics"
        self.root.mkdir(parents=True)
        self._orig_root = constants.TOPICS_ROOT
        self._orig_legacy = migration.LEGACY_ROOT
        constants.TOPICS_ROOT = self.root
        migration.LEGACY_ROOT = Path(self._tmp.name) / "legacy_proposals"
        migration.LEGACY_ROOT.mkdir(parents=True)
        for s in ("drafts", "optimizing", "pending_review", "archived"):
            (migration.LEGACY_ROOT / s).mkdir()
        self.addCleanup(self._teardown)

    def _teardown(self):
        constants.TOPICS_ROOT = self._orig_root
        migration.LEGACY_ROOT = self._orig_legacy
        self._tmp.cleanup()

    # ------------------------------------------------ mock hermes runner
    def _mock_runner(self, topic_id: str, content_scale: int = 1):
        """写产物型 runner：按 profile 写深研产物，满足验收口径。

        tdir 在调用时解析（模拟真实 hermes 从 prompt 读目录——目录可能在
        questions→kickoff 晋级时被搬移）。
        """

        def runner(profile: str, prompt: str, timeout: int = 900):
            tdir = Path(tstate.topic_dir(topic_id))
            bg = tdir / "01_background"
            pr = tdir / "02_problem"
            sc = tdir / "03_scheme"
            ref = tdir / "04_references"
            if profile == "researcher":
                bg.mkdir(parents=True, exist_ok=True)
                (bg / "literature-map.md").write_text(
                    "## 领域地图\n固体 HHG 走向 [[固体HHG]] 与 [[贝里曲率]] 应用。\n"
                    + "".join(f"### 文献 N{i} (20{25 + i % 2})\n要点 [[知识页{i}]] 数值 1.2 eV。\n\n"
                              for i in range(8)) * content_scale,
                    encoding="utf-8")
                for i in range(8):
                    (bg / f"note-{i}.md").write_text(
                        f"笔记 {i}：arXiv:26{i:02d}.12345（2026 年）关键结论。[[知识页{i}]]\n" * 3,
                        encoding="utf-8")
            elif profile == "analyst":
                pr.mkdir(parents=True, exist_ok=True)
                (pr / "problem.md").write_text(
                    "## 问题一句话陈述\n\n能否在实验上分离贝里曲率偶极贡献。\n\n"
                    "## 新颖性对照（差异点）\n\n1. 与既有工作差异一\n2. 差异二\n3. 差异三\n\n"
                    "## 可检验判据\n\n- [V] 谐波圆二色性符号翻转\n- [P] 判据阈值 0.1\n- [D] 待标定\n",
                    encoding="utf-8")
            elif profile == "writer":
                sc.mkdir(parents=True, exist_ok=True)
                ref.mkdir(parents=True, exist_ok=True)
                (sc / "scheme.md").write_text(
                    "".join(
                        f"## S{i} 步骤{i}\n方法：{m}。\n输入：样本。\n输出：数据。\n"
                        f"判据：信噪比 > 3。\n工作量：{i} 周。\n\n"
                        for i, m in enumerate(["样品表征", "光路搭建", "谐波采集", "数据分析"], 1))
                    + "## 里程碑\n\n## 首月路线\n先做 S1。\n\n## 风险与备选\nfallback 换样品。\n",
                    encoding="utf-8")
                (ref / "references.bib").write_text(
                    "@article{refA2026,\n  title={Demo A},\n  year={2026},\n  source: [[知识页0]]\n}\n"
                    "@article{refB2026,\n  title={Demo B},\n  year={2026},\n  source: raw/papers/demo-b.md\n}\n",
                    encoding="utf-8")
            return {"success": True, "output": "ok", "error": "", "elapsed_s": 0.1}

        return runner

    def _register(self, title="贝里曲率偶极谐波探测", slug="berry-dipole-probe", problem=None, **kw):
        return registration.register_question(
            title=title, problem=problem or "非中心对称固体中偶极贡献能否分离", source="test",
            slug=slug, knowledge_card="测试知识卡", related=[], **kw)


class TestRegistration(TopicPipelineBase):
    def test_register_basic_and_board(self):
        res = self._register()
        self.assertTrue(res["registered"])
        tid = res["topic_id"]
        self.assertTrue((self.root / "questions" / tid / "topic-card.md").exists())
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["stage"], "questions")
        self.assertIn("related", data["topics"][tid])  # G2 显式 related 字段

    def test_novelty_gate_blocks_duplicate(self):
        r1 = self._register()
        self.assertTrue(r1["registered"])
        # 同题重复注册（无 force）应被 0.50 硬门拦截
        r2 = registration.register_question(
            title="贝里曲率偶极谐波探测", problem="非中心对称固体中偶极贡献能否分离",
            source="test", slug="berry-dipole-probe-dup")
        self.assertFalse(r2["registered"])
        self.assertIn("新颖性不过", r2["reason"])

    def test_id_collision_appends_seq(self):
        r1 = self._register()
        # 同 slug 不同问题（相似度低于 0.50 门），触发 ID 序号顺延
        r2 = registration.register_question(
            title="层间滑移费米子的红外响应", problem="滑移费米子能否产生可调红外偶极响应",
            source="test", slug="berry-dipole-probe")
        self.assertTrue(r2["registered"], r2.get("reason"))
        self.assertNotEqual(r1["topic_id"], r2["topic_id"])
        self.assertTrue(r2["topic_id"].endswith("-02"))

    def test_similarity_reasonable(self):
        self.assertGreater(similarity.jaccard_similarity("固体高次谐波调控", ["固体高次谐波产生机制"]), 0.2)
        self.assertLess(similarity.jaccard_similarity("拓扑声学", ["量子计算纠错"]), 0.2)


class TestDeepDiveAndAcceptance(TopicPipelineBase):
    def _tid(self):
        res = self._register()
        assert res["registered"]
        return res["topic_id"]

    def test_full_pipeline_questions_to_ready(self):
        tid = self._tid()
        runner = self._mock_runner(tid)
        dive = deep_research.deep_dive(tid, runner=runner)
        self.assertTrue(dive["success"], dive)
        # questions → kickoff 晋级
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["stage"], "kickoff")
        asm = assemble.assemble_report(tid)
        self.assertTrue(asm["success"])
        self.assertFalse(asm["over_limit"])
        chk = acceptance.check_topic(tid)
        v = chk["verdict"]
        self.assertTrue(v["passed"], "缺口: " + "; ".join(v["gaps"]))
        # 自检全过 → ready
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["stage"], "ready")

    def test_gap_on_runner_failure_and_repair(self):
        tid = self._tid()
        calls = {"n": 0}

        def failing_runner(profile, prompt, timeout=900):
            calls["n"] += 1
            return {"success": False, "output": "", "error": "API 错误特征命中: 余额不足", "elapsed_s": 0.1}

        dive = deep_research.deep_dive(tid, runner=failing_runner)
        self.assertFalse(dive["success"])
        self.assertEqual(dive["gaps"], ["background"])
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["gap_repair_counts"]["background"], 1)
        # 补齐模式：成功 runner 只跑缺的步
        dive2 = deep_research.deep_dive(tid, runner=self._mock_runner(tid))
        self.assertTrue(dive2["success"])
        skipped = [s for s in dive2["steps_run"] if s.get("skipped")]
        self.assertEqual(len(skipped), 0)  # background 失败无产物，不跳过
        # 但 background 之后 problem/scheme 尚未跑，dive2 应续跑完
        self.assertEqual([s["step"] for s in dive2["steps_run"]],
                         ["background", "problem", "scheme"])

    def test_timeout_with_verified_artifact_not_a_gap(self):
        """v8.0.6 任务1反向用例：runner 超时但产物过验 → 不计缺口、继续下一步。

        复现 attosecond 11-18 实况：background 1800s 超时（success=false），
        却已产出 49,917 字节 literature-map.md（verify.ok=true）。旧代码仍记
        gaps=["background"] 并 break——本用例在旧代码下必然失败。
        """
        tid = self._tid()
        bg_called = {"n": 0}

        def timeout_runner(profile, prompt, timeout=900):
            if profile == "researcher":
                bg_called["n"] += 1
                tdir = Path(tstate.topic_dir(tid))
                bg = tdir / "01_background"
                bg.mkdir(parents=True, exist_ok=True)
                # 同构产物：真实超时留下的 literature-map（≥50 字节）
                (bg / "literature-map.md").write_text(
                    "## 领域地图\n超时前已落盘的检索骨架。\n" * 5, encoding="utf-8")
                return {"success": False, "output": "", "error": "hermes agent 超时（1800s）",
                        "elapsed_s": 1800.32}
            return self._mock_runner(tid)(profile, prompt, timeout=timeout)

        dive = deep_research.deep_dive(tid, runner=timeout_runner)
        self.assertEqual(dive["gaps"], [], "产物过验的超时步不得计入缺口")
        self.assertTrue(dive["success"])
        steps = [s["step"] for s in dive["steps_run"]]
        self.assertEqual(steps, ["background", "problem", "scheme"],
                         "background 过验后必须继续执行后续步骤")
        note = dive["steps_run"][0].get("note", "")
        self.assertIn("产物已过验", note)
        # 缺口计数不增长（attosecond 已 2 次，再计 1 次即 needs_human 停摆）
        data = tstate.load_state()
        self.assertNotIn("background", data["topics"][tid].get("gap_repair_counts", {}))
        self.assertFalse(data["topics"][tid].get("needs_human", False))
        # 重跑不重复执行已过验的步（产物存在即跳过）
        dive2 = deep_research.deep_dive(tid, runner=timeout_runner)
        self.assertEqual([s["step"] for s in dive2["steps_run"] if s.get("skipped")],
                         ["background", "problem", "scheme"])
        self.assertEqual(bg_called["n"], 1)

    def test_migration_draft_scheme_forces_rewrite(self):
        """v8.0.6 任务2反向用例：迁移稿 scheme 不算完成 → B3 强制重写。

        旧代码只校验「产物存在且 ≥50 字节」，迁移稿（steps=0）被跳过，
        A3 永挂——本用例在旧代码下 scheme 不会被执行。
        """
        tid = self._tid()
        # 模拟 migration.py 迁移产物：scheme-source.md + 迁移稿头 + 无 S 步
        tdir = Path(tstate.topic_dir(tid))
        sc = tdir / "03_scheme"
        sc.mkdir(parents=True, exist_ok=True)
        (sc / "scheme-source.md").write_text("# v7 方案章节\n\n正文。\n", encoding="utf-8")
        (sc / "kb-methods-pack.md").write_text("# 方法素材包（迁移挂载）\n\n方法：演示。\n", encoding="utf-8")
        (sc / "scheme.md").write_text(
            "# 方案分解（v7 迁移稿）\n\n> 迁移自 research_proposals/optimizing/x/04_proposal/"
            "sections/scheme.md；步骤编号/首月路线/判据格式待深研改写为 S1..Sn 口径。\n\n"
            "### 1. 总体技术路线\n\n散文式旧章节，无 S1..Sn 步骤节。\n", encoding="utf-8")
        # 三个特征逐一自检（识别逻辑本身）
        self.assertTrue(deep_research._scheme_is_migration_draft(tdir))  # source 存在
        (sc / "scheme-source.md").unlink()
        self.assertTrue(deep_research._scheme_is_migration_draft(tdir))  # 头部声明
        (sc / "scheme.md").write_text("# 方案分解\n\n无迁移声明但零步骤。\n", encoding="utf-8")
        self.assertTrue(deep_research._scheme_is_migration_draft(tdir))  # steps=0
        # 正式 scheme（S1..Sn）不判迁移稿
        proper = self._tmp.name + "/proper"
        Path(proper).mkdir(parents=True)
        (Path(proper) / "scheme.md").write_text(
            "## S1 步骤一\n判据：信噪比 > 3。\n\n## S2 步骤二\n判据：误差 < 5%。\n",
            encoding="utf-8")
        self.assertFalse(deep_research._scheme_is_migration_draft(Path(proper)))
        # 深研行为：scheme 必须被执行（不被跳过），writer 重写后 A3 可过
        calls = []

        def tracking_runner(profile, prompt, timeout=900):
            calls.append(profile)
            return self._mock_runner(tid)(profile, prompt, timeout=timeout)

        dive = deep_research.deep_dive(tid, runner=tracking_runner)
        self.assertIn("writer", calls, "迁移稿必须触发 B3 重写（writer profile）")
        # scheme 迁移稿不得以「产物已存在」跳过
        skipped = [s for s in dive["steps_run"] if s.get("skipped")]
        self.assertEqual([s["step"] for s in skipped], [],
                         "scheme 迁移稿不得跳过（background/problem 本就无产物需执行）")
        rewritten = [s for s in dive["steps_run"] if s.get("step") == "scheme"]
        self.assertTrue(rewritten and rewritten[0].get("verify", {}).get("ok"))
        chk = acceptance.check_topic(tid)
        a3 = next(r for r in chk["verdict"]["results"] if r["code"] == "A3")
        self.assertTrue(a3["passed"], "B3 重写后 A3 应转 pass")
        self.assertGreaterEqual(a3["evidence"]["steps"], 3)

    def test_check_gaps_cleared_on_pass(self):
        """v8.0.7 反向用例：先失败后过检，check_gaps 必须随晋级清零。

        旧代码晋级路径只清 deep_dive_gaps/needs_human，check_gaps 残留旧
        缺口字样（与 kickoff-check.json passed=true 矛盾，queue_head 会把它
        当缺口续研）——本用例在旧代码下必然失败。
        """
        tid = self._tid()
        # 先制造一次失败自检（无产物 → A1/A3/A4/G2 记缺口）
        chk0 = acceptance.check_topic(tid)
        self.assertFalse(chk0["verdict"]["passed"])
        data = tstate.load_state()
        self.assertTrue(data["topics"][tid].get("check_gaps"))
        # 补齐产物后过检晋级
        deep_research.deep_dive(tid, runner=self._mock_runner(tid))
        assemble.assemble_report(tid)
        chk = acceptance.check_topic(tid)
        self.assertTrue(chk["verdict"]["passed"], chk["verdict"]["gaps"])
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["stage"], "ready")
        self.assertEqual(data["topics"][tid].get("check_gaps"), [],
                         "晋级后 check_gaps 必须清零（与 kickoff-check.json 一致）")
        self.assertEqual(data["topics"][tid].get("deep_dive_gaps"), [])
        self.assertFalse(data["topics"][tid].get("needs_human", False))
        # 清理后不再被 queue_head 选中（kickoff 缺口续研口径）
        self.assertEqual([i["topic_id"] for i in daily.queue_head(10) if i["topic_id"] == tid], [])

    def test_check_gaps_cleared_on_ready_recheck(self):
        """v8.0.15 反向用例：已晋级 ready 的课题复检全过也必须清残留缺口标记。

        bsv 实例：晋级前已 in ready，过检路径只对 kickoff 生效，旧 check_gaps
        长期残留、与 kickoff-check.json passed=true 矛盾——本用例在旧代码下失败。
        """
        tid = self._tid()
        deep_research.deep_dive(tid, runner=self._mock_runner(tid))
        assemble.assemble_report(tid)
        self.assertTrue(acceptance.check_topic(tid)["verdict"]["passed"])
        self.assertEqual(tstate.load_state()["topics"][tid]["stage"], "ready")
        # 模拟残留：手工写入旧缺口字样
        with tstate.state_lock():
            d = tstate.load_state()
            tstate.upsert_topic(d, tid, {"check_gaps": ["报告 wikilink 0 < 5"]})
            tstate.save_state(d)
        # 复检全过 → 残留必须清零
        self.assertTrue(acceptance.check_topic(tid)["verdict"]["passed"])
        self.assertEqual(tstate.load_state()["topics"][tid].get("check_gaps"), [])

    def test_acceptance_fails_without_artifacts(self):

        tid = self._tid()
        chk = acceptance.check_topic(tid)
        self.assertFalse(chk["verdict"]["passed"])
        codes = {r["code"] for r in chk["verdict"]["results"] if not r["passed"]}
        self.assertIn("A1", codes)
        self.assertIn("G2", codes)

    def test_human_nodes_activate_reject_archive(self):
        tid = self._tid()
        runner = self._mock_runner(tid)
        deep_research.deep_dive(tid, runner=runner)
        assemble.assemble_report(tid)
        acceptance.check_topic(tid)
        # activate ready → active
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["stage"], "ready")
        with tstate.state_lock():
            d = tstate.load_state()
            tstate.set_stage(d, tid, "active", "测试启动")
            tstate.save_state(d)
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["stage"], "active")
        # reject questions 候选
        r2 = self._register(title="另一个问题候选", slug="another-q", problem="完全不同的另一个问题")
        with tstate.state_lock():
            d = tstate.load_state()
            tstate.reject_topic(d, r2["topic_id"], "测试否决")
            tstate.save_state(d)
        data = tstate.load_state()
        self.assertNotIn(r2["topic_id"], data["topics"])
        self.assertEqual(data["rejected"][r2["topic_id"]]["reason"], "测试否决")


class TestAssembleG1(TopicPipelineBase):
    def test_over_limit_shrinks_to_cap(self):
        tid_res = self._register()
        tid = tid_res["topic_id"]
        runner = self._mock_runner(tid, content_scale=40)  # 制造超长产物
        deep_research.deep_dive(tid, runner=runner)
        asm = assemble.assemble_report(tid)
        self.assertTrue(asm["success"])
        self.assertFalse(asm["over_limit"], f"报告 {asm['report_chars']} 超限未收缩")
        self.assertLessEqual(asm["report_chars"], constants.G1_REPORT_MAX_CHARS)


class TestMigration(TopicPipelineBase):
    def _mk_legacy(self, pid: str, stage: str, with_sections: bool = True):
        d = migration.LEGACY_ROOT / stage / pid
        d.mkdir(parents=True)
        (d / "00_research_idea.md").write_text(
            "# 研究设想\n\n## 核心科学问题\n\n莫尔平带载流子的轨道磁矩能否测量？\n\n"
            "## 研究背景\n\n背景内容。\n", encoding="utf-8")
        (d / "00_proposal-brief.md").write_text(
            f"# 课题卡\n\n- 课题名称: {pid}\n- 当前状态: v7 {stage}\n", encoding="utf-8")
        lit = d / "02_literature"
        lit.mkdir()
        (lit / "reading-notes.md").write_text("## 阅读笔记\n文献一 (2026-01) [[固体HHG]]。\n" * 3,
                                              encoding="utf-8")
        if with_sections:
            sec = d / "04_proposal" / "sections"
            sec.mkdir(parents=True)
            (sec / "rationale.md").write_text("# 立项依据\n\n依据内容。\n", encoding="utf-8")
            (sec / "scheme.md").write_text("# 研究方案\n\n步骤内容。\n", encoding="utf-8")
            (sec / "references.md").write_text("# 参考文献\n\n[1] Demo 2026。\n", encoding="utf-8")
        return d

    def test_migrate_all_stages(self):
        self._mk_legacy("general-moire-orbital-20260726", "optimizing")
        self._mk_legacy("general-bsv-hhg-20260726", "pending_review")
        self._mk_legacy("general-quantum-geometry-20260726", "archived", with_sections=False)
        report = migration.migrate_v7(dry_run=False)
        self.assertEqual(report["count"], 3)
        by_stage = {r["topic_id"]: r["stage_v8"] for r in report["results"]}
        self.assertEqual(by_stage["general-moire-orbital-20260726"], "kickoff")
        self.assertEqual(by_stage["general-bsv-hhg-20260726"], "ready")
        self.assertEqual(by_stage["general-quantum-geometry-20260726"], "archive")
        # 新域文件齐备
        tdir = self.root / "kickoff" / "general-moire-orbital-20260726"
        for rel in ("topic-card.md", "topic-report.md", "02_problem/problem.md",
                    "02_problem/idea-source.md", "03_scheme/scheme.md",
                    "04_references/references-source.md", "01_background/reading-notes.md"):
            self.assertTrue((tdir / rel).exists(), f"缺 {rel}")
        # 状态登记 + migrated_from
        data = tstate.load_state()
        rec = data["topics"]["general-moire-orbital-20260726"]
        self.assertEqual(rec["migrated_from"], "research_proposals/optimizing/general-moire-orbital-20260726")
        self.assertIn("related", rec)
        # 迁移报告落审计目录
        audit = self.root / "_audit" / "v8-migration-report.json"
        self.assertTrue(audit.exists())
        # legacy 保留原位 + README 标注
        self.assertTrue((migration.LEGACY_ROOT / "optimizing" / "general-moire-orbital-20260726").exists())
        self.assertTrue((migration.LEGACY_ROOT / "README-v7-LEGACY.md").exists())

    def test_migrate_dry_run_no_writes(self):
        self._mk_legacy("general-dry-run-20260726", "optimizing")
        report = migration.migrate_v7(dry_run=True)
        self.assertEqual(report["count"], 1)
        self.assertFalse((self.root / "kickoff" / "general-dry-run-20260726").exists())
        self.assertFalse((self.root / "_topics.json").exists())


class TestWeekendBridge(TopicPipelineBase):
    def test_register_from_idea(self):
        idea = {
            "title": "转角 TMD 平带的轨道磁性",
            "background": "知识簇综合：多篇文献指向平带磁性。",
            "gap": "轨道磁矩响应的测量空白",
            "keywords": ["moire", "orbital magnetism"],
            "cluster_id": "cl_20260816_a21e61",
            "sources": [{"title": "Paper A", "source_type": "weekend_cluster"}],
        }
        res = weekend_bridge.register_from_idea_v8(idea)
        self.assertTrue(res["registered"])
        self.assertEqual(res["proposal_id"], res["topic_id"])
        card = (self.root / "questions" / res["topic_id"] / "topic-card.md").read_text(encoding="utf-8")
        self.assertIn("weekend_cluster:cl_20260816_a21e61", card)
        self.assertIn("知识簇综合", card)

    def test_enrich_and_supplementary(self):
        res = self._register(title="已有课题", slug="existing-topic")
        tid = res["topic_id"]
        # 登记 related 字段（G2 口径）
        with tstate.state_lock():
            d = tstate.load_state()
            tstate.upsert_topic(d, tid, {"related": []})
            tstate.save_state(d)
        idea = {"title": "融入", "background": "簇知识", "gap": "g", "cluster_id": "cl_x",
                "sources": [{"title": "P1"}]}
        er = weekend_bridge.enrich_from_idea_v8(tid, idea)
        self.assertTrue(er["success"])
        bg = tstate.topic_dir(tid) / "01_background"
        self.assertTrue(list(bg.glob("knowledge-card-*.md")))
        ok = weekend_bridge.write_supplementary_sources_v8(
            tid, {"member_summaries": [{"source_id": "s1", "title": "P1", "summary": "摘要"}]},
            {"s1": {"title": "P1", "summary": "摘要", "path": "p.md"}})
        self.assertTrue(ok)
        self.assertTrue(list(bg.glob("supplementary-sources-*.json")))
        # 不存在的课题 → False
        self.assertFalse(weekend_bridge.write_supplementary_sources_v8("nope", {}, {}))


class TestDaily(TopicPipelineBase):
    def test_daily_processes_queue(self):
        r = self._register()
        tid = r["topic_id"]
        runner = self._mock_runner(tid)
        # daily 模块用全局 runner 注入
        res = daily.run_daily(runner=runner)
        self.assertTrue(res["success"], res)
        self.assertEqual(res["processed"], 1)
        data = tstate.load_state()
        self.assertIn(data["topics"][tid]["stage"], ("kickoff", "ready"))

    def test_daily_empty_queue(self):
        res = daily.run_daily()
        self.assertTrue(res["success"])
        self.assertIn("队列为空", res["skipped"])

    def test_daily_quota_respected(self):
        problems = ["轨道磁矩响应的测量方案", "声子散射谱的中子测量", "双层转角体系的输运计算"]
        first_tid = None
        for i, prob in enumerate(problems):
            res = self._register(title=f"候选问题之{prob[:6]}", slug=f"quota-cand-{chr(97 + i)}", problem=prob)
            if i == 0:
                first_tid = res["topic_id"]
        # v8.0.2 修复：原硬编码 ...20261116 日期后缀，跨日即 TypeError
        # （topic_dir 返回 None）——时间敏感用例改用注册返回的真实 tid
        runner = self._mock_runner(first_tid)
        res = daily.run_daily(runner=runner)
        self.assertEqual(res["quota"], constants.DEFAULT_DAILY_QUOTA)
        self.assertEqual(res["processed"], 1)


if __name__ == "__main__":
    unittest.main()


class TestDailyKickoffGapPickup(TopicPipelineBase):
    """v8.0.0 补：kickoff 缺口课题纳入每日续研队列（迁移课题自动补齐路径）。"""

    def test_kickoff_gap_topic_picked_when_no_questions(self):
        tid_res = self._register()
        tid = tid_res["topic_id"]
        runner = self._mock_runner(tid)
        deep_research.deep_dive(tid, runner=runner)
        assemble.assemble_report(tid)
        # 人为制造缺口：删掉 method pack → check 记录缺口
        pack = Path(tstate.topic_dir(tid)) / "03_scheme" / "kb-methods-pack.md"
        pack.unlink()
        acceptance.check_topic(tid)
        data = tstate.load_state()
        self.assertTrue(data["topics"][tid].get("check_gaps"))
        self.assertEqual(data["topics"][tid]["stage"], "kickoff")
        # 队列应取到该 kickoff 缺口课题（questions 为空）
        q = daily.queue_head(2)
        self.assertEqual([x["topic_id"] for x in q], [tid])

    def test_kickoff_without_gap_not_picked(self):
        # 无缺口的 kickoff（材料齐全但不晋级——例如 G2 差一条且 related 缺失被人工补上）
        tid_res = self._register()
        tid = tid_res["topic_id"]
        with tstate.state_lock():
            d = tstate.load_state()
            tstate.set_stage(d, tid, "kickoff", "测试")
            tstate.upsert_topic(d, tid, {"deep_dive_gaps": [], "check_gaps": []})
            tstate.save_state(d)
        self.assertEqual(daily.queue_head(3), [])


class TestTransitionInvariant(TopicPipelineBase):
    """v8.0.1 补：「阶段即目录」不变量——所有流转必须物理搬移目录。"""

    def _to_ready(self):
        tid_res = self._register()
        tid = tid_res["topic_id"]
        deep_research.deep_dive(tid, runner=self._mock_runner(tid))
        assemble.assemble_report(tid)
        chk = acceptance.check_topic(tid)
        self.assertTrue(chk["verdict"]["passed"], chk["verdict"]["gaps"])
        return tid

    def test_check_promotion_moves_dir_to_ready(self):
        tid = self._to_ready()
        self.assertTrue((self.root / "ready" / tid).exists(),
                        "自检晋级后目录应物理搬到 ready/")
        self.assertFalse((self.root / "kickoff" / tid).exists())

    def test_activate_moves_dir_to_active(self):
        tid = self._to_ready()
        moved = tstate.transition(tid, "active", "测试启动")
        self.assertEqual(moved["from"], "ready")
        self.assertTrue((self.root / "active" / tid).exists())
        self.assertFalse((self.root / "ready" / tid).exists())
        data = tstate.load_state()
        self.assertEqual(data["topics"][tid]["stage"], "active")

    def test_archive_moves_dir(self):
        tid = self._to_ready()
        tstate.transition(tid, "active", "测试")
        tstate.transition(tid, "archive", "测试归档")
        self.assertTrue((self.root / "archive" / tid).exists())
        self.assertFalse((self.root / "active" / tid).exists())

    def test_reject_moves_any_stage_dir_to_ledger(self):
        tid = self._to_ready()
        with tstate.state_lock():
            d = tstate.load_state()
            tstate.reject_topic(d, tid, "测试否决")
            tstate.save_state(d)
        moved = tstate.move_to_rejected(tid)
        self.assertTrue(moved and Path(moved).exists())
        self.assertTrue((self.root / "_rejected-questions" / tid).exists())
        self.assertFalse((self.root / "ready" / tid).exists())

    def test_transition_rejects_unknown_topic_and_stage(self):
        with self.assertRaises(KeyError):
            tstate.transition("general-nope-20260101", "active")
        with self.assertRaises(ValueError):
            tstate.transition(self._register()["topic_id"], "bogus-stage")

    def test_migration_backfills_novelty(self):
        self._mk_legacy_two() if hasattr(self, "_mk_legacy_two") else None
        d1 = migration.LEGACY_ROOT / "optimizing" / "general-mo-a-20260101"
        d1.mkdir(parents=True)
        (d1 / "00_research_idea.md").write_text("# 设想\n\n## 核心科学问题\n\n莫尔平带轨道磁矩测量。\n", encoding="utf-8")
        d2 = migration.LEGACY_ROOT / "optimizing" / "general-mo-b-20260101"
        d2.mkdir(parents=True)
        (d2 / "00_research_idea.md").write_text("# 设想\n\n## 核心科学问题\n\n声子谱中子散射测量方案。\n", encoding="utf-8")
        report = migration.migrate_v7(dry_run=False)
        data = tstate.load_state()
        for tid in ("general-mo-a-20260101", "general-mo-b-20260101"):
            nov = data["topics"][tid].get("novelty") or {}
            self.assertIn("max_score", nov, f"{tid} 缺新颖性回填")
            self.assertLess(nov["max_score"], 1.0, "相似度对照须排除自身")
