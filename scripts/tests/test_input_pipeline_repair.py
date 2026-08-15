#!/usr/bin/env python3
"""
test_input_pipeline_repair.py — 周末输入端三项修复回归测试（v6.9.10）

背景：input 链"成功空转"——7 个 job 全 done 但产物全空（ideas 连续全零），
熔断防线从未告警，stage_status 卡 pending。三项修复：

    1. collect_all_sources 不再预标记 papers/briefings/captures/
       reference_notes 为已处理（保留 kb 类标记），summarize 的
       new_paper_sources 过滤恢复有效
    2. input_pipeline_broken 熔断检测改扫 weekend-input/ideas-*.json
       产物文件族（最近 2 个文件均空即告警），不受每周空跑刷新影响
    3. run_next 逐 job 推进后补阶段终态汇总，stage_status 不再卡 pending

注意：本测试不调用 LLM，运行于隔离临时目录。
"""

import sys
import shutil
import json
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class InputPipelineRepairTests(TestSuite):
    def __init__(self):
        super().__init__("周末输入端三项修复测试（v6.9.10）")
        self.tmp_root = None

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

    # ------------------------------------------------------------------
    # 修复 1：collect_all_sources 停止预标记文献类来源
    # ------------------------------------------------------------------

    def _patch_collectors(self, sources_mod):
        """用固定来源替换各收集器，隔离真实 KB/文件系统。用完须 _restore_collectors。"""
        self._collector_backup = {
            "collect_briefings": sources_mod.collect_briefings,
            "collect_paper_pool": sources_mod.collect_paper_pool,
            "collect_captures": sources_mod.collect_captures,
            "collect_reference_notes": sources_mod.collect_reference_notes,
            "collect_kb_concepts_and_methods": sources_mod.collect_kb_concepts_and_methods,
        }
        sources_mod.collect_briefings = lambda days=7, state=None: [
            {"source_id": "briefing:b1", "type": "briefing", "text": "简报甲"}
        ]
        sources_mod.collect_paper_pool = lambda limit=20, state=None: [
            {"source_id": "paper:p1", "type": "paper", "text": "论文甲"}
        ]
        sources_mod.collect_captures = lambda limit=10: [
            {"source_id": "capture:c1", "type": "capture", "text": "捕获甲"}
        ]
        sources_mod.collect_reference_notes = lambda: [
            {"source_id": "note:n1", "type": "note", "text": "笔记甲"}
        ]
        sources_mod.collect_kb_concepts_and_methods = lambda state=None: {
            "concepts": [
                {"source_id": "kb:concepts:wiki/x.md", "type": "kb_concepts", "text": "概念甲"}
            ]
        }

    def _restore_collectors(self, sources_mod):
        """恢复被 _patch_collectors 替换的原始收集器（防用例间污染）。"""
        backup = getattr(self, "_collector_backup", None)
        if not backup:
            return
        for name, fn in backup.items():
            setattr(sources_mod, name, fn)

    def _test_collect_does_not_premark_literature_sources(self):
        """文献类来源收集后不得进入 processed_sources（旧版即此处饿死 summarize）。"""
        from weekend_pipeline import sources as src_mod
        self._patch_collectors(src_mod)
        try:
            state = {}
            result = src_mod.collect_all_sources(state=state)

            processed = state.get("processed_sources", {})
            for sid in ["briefing:b1", "paper:p1", "capture:c1", "note:n1"]:
                self.assert_true(
                    sid not in processed,
                    f"{sid} 不应被收集即标记",
                    f"收集阶段即标记 {sid}，summarize 过滤将恒为空",
                )

            self.assert_true("kb:concepts:wiki/x.md" in processed, "kb 来源应保留标记（gap_analysis 数据通路）")

            new = src_mod.new_paper_sources(result, state)
            self.assert_eq(len(new), 2, "新料过滤应恢复有效（briefing+paper）",
                           f"实际 {len(new)} 条，预期 2 条")
        finally:
            self._restore_collectors(src_mod)

    def _test_summarize_filter_recovers_after_kb_roundtrip(self):
        """标记职责在消费方：摘要成功后标记，未摘要的下次仍视为新料。"""
        from weekend_pipeline import sources as src_mod
        self._patch_collectors(src_mod)
        try:
            state = {}
            result = src_mod.collect_all_sources(state=state)

            # 消费方摘要成功后标记第一条
            first = src_mod.new_paper_sources(result, state)[0]
            src_mod.mark_source_processed(first["source_id"], first["text"], state)

            remaining = src_mod.new_paper_sources(result, state)
            self.assert_eq(len(remaining), 1, "已消费 1 条后应剩 1 条新料")
            self.assert_true(remaining[0]["source_id"] != first["source_id"], "剩余新料不应是已消费条目")
        finally:
            self._restore_collectors(src_mod)

    # ------------------------------------------------------------------
    # v6.9.11: 补课语义——未处理来源豁免时间窗口/数量上限
    # ------------------------------------------------------------------

    def _touch(self, path: Path, days_ago: int) -> None:
        import os
        import time
        old = time.time() - days_ago * 86400
        os.utime(path, (old, old))

    def _test_briefing_backlog_exempt_from_window(self):
        """旧简报未处理 → 豁免 7 天窗口收进；已处理 → 窗口外跳过。"""
        from weekend_pipeline import sources as src_mod

        tmp_dir = self.tmp_root / "reviews"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        old_f = tmp_dir / "briefing-old.md"
        new_f = tmp_dir / "briefing-new.md"
        old_f.write_text("# 旧简报", encoding="utf-8")
        new_f.write_text("# 新简报", encoding="utf-8")
        self._touch(old_f, days_ago=30)
        self._touch(new_f, days_ago=1)

        orig_dirs = (src_mod.BRIEFING_DIR, src_mod.HERMES_BRIEFINGS_DIR)
        src_mod.BRIEFING_DIR = tmp_dir
        src_mod.HERMES_BRIEFINGS_DIR = self.tmp_root / "no-such-dir"
        try:
            # 场景 1：state 为空 dict（全部未处理）→ 新旧都收（补课）
            got = src_mod.collect_briefings(days=7, state={})
            self.assert_eq(len(got), 2, "未处理的旧简报应豁免窗口（补课收进）",
                           f"实际收 {len(got)} 条")

            # 场景 2：旧简报已处理 → 窗口外跳过，只收新的
            state = {}
            src_mod.mark_source_processed(
                src_mod._make_source_id("briefing", old_f), "# 旧简报", state)
            got2 = src_mod.collect_briefings(days=7, state=state)
            self.assert_eq(len(got2), 1, "已处理的旧简报应被窗口过滤")
            self.assert_true(got2[0]["path"].endswith("briefing-new.md"), "应只收新简报")

            # 场景 3：state=None（无标记能力）→ 保持旧窗口语义
            got3 = src_mod.collect_briefings(days=7, state=None)
            self.assert_eq(len(got3), 1, "state=None 时旧简报仍按窗口过滤")
        finally:
            src_mod.BRIEFING_DIR, src_mod.HERMES_BRIEFINGS_DIR = orig_dirs

    def _test_paper_pool_backlog_exempt_from_limit(self):
        """未处理论文全收（豁免 mtime 前 N 截断）；已处理的受 limit 约束。"""
        from weekend_pipeline import sources as src_mod

        tmp_dir = self.tmp_root / "papers"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        for i in range(25):
            f = tmp_dir / f"2401.000{i:02d}.md"
            f.write_text(f"---\ntitle: 论文{i}\nabstract: 摘要{i}\n---\n正文", encoding="utf-8")
            self._touch(f, days_ago=30)  # 全部旧文件（mtime 排序之外的场景）

        orig_dirs = (src_mod.RAW_PAPERS_DIR, src_mod.HERMES_BRIEFINGS_PAPERS_DIR)
        src_mod.RAW_PAPERS_DIR = tmp_dir
        src_mod.HERMES_BRIEFINGS_PAPERS_DIR = self.tmp_root / "no-such-dir"
        try:
            # 场景 1：全部未处理 → 25 条全收（旧实现 [:20] 只收 20）
            got = src_mod.collect_paper_pool(limit=20, state={})
            self.assert_eq(len(got), 25, "未处理论文应全量收进（补课）",
                           f"实际收 {len(got)} 条")

            # 场景 2：其中 10 条已处理 → 已处理计数不挤占，未处理 15 条仍在
            state = {}
            for s in got[:10]:
                src_mod.mark_source_processed(s["source_id"], s["text"], state)
            got2 = src_mod.collect_paper_pool(limit=3, state=state)
            self.assert_eq(len(got2), 25, "已处理 10 条 + 未处理 15 条，limit=3 时全部可达")

            # 场景 3：state=None → 旧语义（前 limit 条）
            got3 = src_mod.collect_paper_pool(limit=5, state=None)
            self.assert_eq(len(got3), 5, "state=None 时保持前 N 截断语义")
        finally:
            src_mod.RAW_PAPERS_DIR, src_mod.HERMES_BRIEFINGS_PAPERS_DIR = orig_dirs

    # ------------------------------------------------------------------
    # 修复 2：熔断检测扫 ideas 产物文件族
    # ------------------------------------------------------------------

    def _run_breaker_check(self):
        import lifecycle_monitor as lm
        self._lm_mod = lm
        self._orig_lm_root = lm.PROJECT_ROOT
        lm.PROJECT_ROOT = self.tmp_root
        try:
            _, anomalies = lm._check_proposals()
        finally:
            lm.PROJECT_ROOT = self._orig_lm_root
        return anomalies

    def _clean_ideas(self):
        """清除上一用例残留的 ideas 产物（套件级 setup，用例需自清理）。"""
        ideas_dir = self.tmp_root / "memory" / "weekend-input"
        if ideas_dir.exists():
            for f in ideas_dir.glob("ideas-*.json"):
                f.unlink()

    def _test_breaker_fires_on_two_empty_idea_files(self):
        """最近 2 个 ideas 文件均为空 → input_pipeline_broken 告警。"""
        self._clean_ideas()
        ideas_dir = self.tmp_root / "memory" / "weekend-input"
        _write_json(ideas_dir / "ideas-2026-08-14.json", {"ideas": []})
        _write_json(ideas_dir / "ideas-2026-08-15.json", {"ideas": []})

        anomalies = self._run_breaker_check()
        hit = [a for a in anomalies if a.get("type") == "input_pipeline_broken"]
        self.assert_true(bool(hit), "连续 2 次零设想应触发熔断告警",
                         f"anomalies: {anomalies}")
        if hit:
            self.assert_true("08-14" in hit[0]["message"], "告警消息应含文件日期")

    def _test_breaker_silent_when_recent_ideas_nonzero(self):
        """最近一次产出非零 → 不告警。"""
        self._clean_ideas()
        ideas_dir = self.tmp_root / "memory" / "weekend-input"
        _write_json(ideas_dir / "ideas-2026-08-14.json", {"ideas": []})
        _write_json(ideas_dir / "ideas-2026-08-15.json",
                    {"ideas": [{"title": "t", "gap": "g"}]})

        anomalies = self._run_breaker_check()
        hit = [a for a in anomalies if a.get("type") == "input_pipeline_broken"]
        self.assert_true(not hit, "最近一次非零不应触发熔断")

    def _test_breaker_silent_with_single_idea_file(self):
        """仅 1 个产物文件（数据不足）→ 不告警。"""
        self._clean_ideas()
        ideas_dir = self.tmp_root / "memory" / "weekend-input"
        _write_json(ideas_dir / "ideas-2026-08-15.json", {"ideas": []})

        anomalies = self._run_breaker_check()
        hit = [a for a in anomalies if a.get("type") == "input_pipeline_broken"]
        self.assert_true(not hit, "单文件不应触发熔断")

    def _test_breaker_treats_corrupt_file_as_empty(self):
        """产物文件损坏按 0 计（防线宁误报不漏报）。"""
        self._clean_ideas()
        ideas_dir = self.tmp_root / "memory" / "weekend-input"
        _write_json(ideas_dir / "ideas-2026-08-14.json", {"ideas": []})
        (ideas_dir / "ideas-2026-08-15.json").write_text("{not json", encoding="utf-8")

        anomalies = self._run_breaker_check()
        hit = [a for a in anomalies if a.get("type") == "input_pipeline_broken"]
        self.assert_true(bool(hit), "损坏文件 + 空文件应触发熔断")

    # ------------------------------------------------------------------
    # 修复 3：run_next 补阶段终态汇总
    # ------------------------------------------------------------------

    def _make_pipeline(self):
        from weekend_pipeline.pipeline import WeekendPipeline
        return WeekendPipeline(state_path=self.tmp_root / "memory" / "weekend-pipeline.json")

    def _stub_handlers(self, p):
        def _fake_handler(state, job, dry_run=False):
            return {"success": True, "job_id": job.get("job_id", ""), "stub": True}
        return {(j["stage"], j["step"]): _fake_handler for j in p.list_jobs(stage="input")}

    def _test_run_next_finalizes_stage_done(self):
        """worker 用 run_next 推完整阶段后 stage_status 应为 done（旧版卡 pending）。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        p.handlers = self._stub_handlers(p)

        for _ in range(20):
            r = p.run_next(stage="input")
            if r.get("executed", 0) == 0:
                break

        from weekend_pipeline.state import load_pipeline_state
        final = load_pipeline_state(p.state_path)
        self.assert_eq(final.get("stage_status", {}).get("input"), "done",
                       "run_next 推完阶段后 stage_status 应翻 done",
                       f"实际: {final.get('stage_status')}")

    def _test_run_next_keeps_pending_mid_stage(self):
        """阶段未推完时 stage_status 不得提前翻 done。"""
        p = self._make_pipeline()
        p.sync_stage_jobs("input")
        p.handlers = self._stub_handlers(p)

        p.run_next(stage="input")  # 只推 1 个 job

        from weekend_pipeline.state import load_pipeline_state
        mid = load_pipeline_state(p.state_path)
        self.assert_true(
            mid.get("stage_status", {}).get("input") != "done",
            "仅推 1 个 job 不应翻 done",
        )

    def run_tests(self):
        self._test_collect_does_not_premark_literature_sources()
        self._test_summarize_filter_recovers_after_kb_roundtrip()
        self._test_briefing_backlog_exempt_from_window()
        self._test_paper_pool_backlog_exempt_from_limit()
        self._test_breaker_fires_on_two_empty_idea_files()
        self._test_breaker_silent_when_recent_ideas_nonzero()
        self._test_breaker_silent_with_single_idea_file()
        self._test_breaker_treats_corrupt_file_as_empty()
        self._test_run_next_finalizes_stage_done()
        self._test_run_next_keeps_pending_mid_stage()
