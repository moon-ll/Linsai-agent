#!/usr/bin/env python3
"""
test_token_redundancy_fix.py — v6.10.41 token 冗余修复回归测试

背景（09-23 token 消耗暴涨排查，工作日 agent loop 调用 230-270 次/天，
为 8 月底的 2-3 倍）。本套件验证四处冗余修复：

    1. 空缺口短路：gap_identify 产出 0 关键词时 lit_search 不派任何
       LLM 会话（旧链路白跑 agent loop + 多源默认词捞泛域老文 +
       lit_read 烧 5 会话，单次 ≈6 会话浪费）；
    2. 排除清单截断：lit_search prompt 不再全量注入全部本地论文 ID
       （实测 1408 个 ≈16.5K 字符/次），改为总量提示 + 80 个采样；
    3. 已通过章节跳过：section_passes=True 的正文章节常规轮不再重跑
       6-job 对抗链（每 3 轮强制复检轮全量构建），依赖链自动重接；
    4. lit_read 合并单会话：5 篇论文一次会话按 "## <arXiv ID>" 分节
       输出，缺失/截断篇目降级单篇直读（旧实现逐篇 5 个独立会话）。

零 LLM、零真实数据域写入（隔离目录 + 模块 patch）。
"""

import sys
import json
import shutil
import importlib
from pathlib import Path
from unittest.mock import MagicMock, patch

from test_runner import TestSuite, create_isolated_env, patch_module_root


class TokenRedundancyFixTests(TestSuite):
    def __init__(self):
        super().__init__("token 冗余修复回归（v6.10.41）")
        self.tmp_root = None
        self.ctrl_mod = None
        self.exec_mod = None

    # ------------------------------------------------------------------
    # 环境
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "research_proposals" / "optimizing").mkdir(parents=True, exist_ok=True)
        for mod_name in list(sys.modules.keys()):
            if mod_name in ("proposal_lifecycle", "lifecycle_cron_framework",
                            "lifecycle", "lifecycle.executor", "lifecycle.controller",
                            "hermes_memory", "literature_service", "external_fetcher",
                            "paths", "common"):
                del sys.modules[mod_name]
        self.ctrl_mod = importlib.import_module("lifecycle_cron_framework")
        patch_module_root("proposal_lifecycle", self.tmp_root)
        patch_module_root("lifecycle_cron_framework", self.tmp_root)
        self.exec_mod = importlib.import_module("lifecycle.executor")

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _register(self, pid):
        """注册并流转一个 optimizing 课题，返回 controller。"""
        c = self.ctrl_mod.LifecycleCronController()
        c.register(pid, project_type="general")
        c.transition(pid, "optimizing")
        prop_dir = c.root / "optimizing" / pid
        prop_dir.mkdir(parents=True, exist_ok=True)
        (prop_dir / "04_proposal").mkdir(exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text("# draft\n", encoding="utf-8")
        return c, prop_dir

    # ------------------------------------------------------------------
    # 1. 空缺口短路
    # ------------------------------------------------------------------

    def _test_empty_gap_short_circuit(self):
        pid = "general-shortcircuit-20260101"
        c, prop_dir = self._register(pid)
        gap_dir = prop_dir / "02_literature" / "gap-analysis"
        gap_dir.mkdir(parents=True, exist_ok=True)
        (gap_dir / "gap-analysis-r100.json").write_text(
            json.dumps({"section": "scheme", "gaps": []}, ensure_ascii=False),
            encoding="utf-8",
        )

        import hermes_memory
        agent_called = []

        def _spy_agent(*a, **kw):
            agent_called.append(1)
            return {"success": False, "output": "", "error": "不应被调用", "elapsed_s": 0}

        # v7.2.69 修复（BUG-26）：patch 目标改为 executor 模块自身
        # （见 _test_lit_read_merged_session 处的说明：v7.2.2 把这两个符号
        # 提升到 executor 模块级，patch hermes_memory 不再影响 executor）。
        with patch.object(self.exec_mod, "_run_hermes_agent", _spy_agent), \
             patch.object(self.exec_mod, "_write_memory", lambda *a, **kw: True):
            result = self.exec_mod._run_lit_search_step(
                c, pid, {"round": 8, "section_key": "scheme"})

        self.assert_true(
            result.get("success") is True, "空缺口短路应 success=True",
            f"实际 {result}")
        self.assert_eq(
            result.get("method"), "short_circuit", "短路路径 method 标记")
        self.assert_eq(
            len(agent_called), 0, "空缺口不得派发任何 agent loop 会话")
        lit_file = Path(result.get("result_path", ""))
        self.assert_true(
            lit_file.exists(), "短路应落盘空 lit-gap 文件（供 lit_read 章节匹配后跳过）")
        if lit_file.exists():
            text = lit_file.read_text(encoding="utf-8")
            self.assert_in("## 章节\nscheme", text, "空报告须带章节标记")
            self.assert_in("无文献缺口", text, "空报告须标注未检索原因")

    # ------------------------------------------------------------------
    # 2. 排除清单截断
    # ------------------------------------------------------------------

    def _test_exclude_prompt_capped(self):
        pid = "general-exclude-cap-20260101"
        c, prop_dir = self._register(pid)
        gap_dir = prop_dir / "02_literature" / "gap-analysis"
        gap_dir.mkdir(parents=True, exist_ok=True)
        (gap_dir / "gap-analysis-r101.json").write_text(
            json.dumps({
                "section": "content",
                "gaps": [{"search_keywords": ["berry curvature hhg", "solid hhg"]}],
            }, ensure_ascii=False),
            encoding="utf-8",
        )

        import hermes_memory
        import literature_service
        import external_fetcher

        _fake_ids = {f"24{i:03d}.01{i:04d}": {} for i in range(300)}
        captured = {}

        def _capture_agent(profile, prompt, timeout=300):
            captured["prompt"] = prompt
            return {"success": True, "output": "[]", "error": "", "elapsed_s": 1.0}

        fake_svc = MagicMock()
        fake_svc._scan_local_raw_papers.return_value = _fake_ids
        fake_svc._get_exclude_ids.return_value = set()
        fake_svc._parse_researcher_output.return_value = []

        # v7.2.69 修复（BUG-26）：patch 目标改为 executor 模块自身
        # （见 _test_lit_read_merged_session 处的说明：v7.2.2 把这两个符号
        # 提升到 executor 模块级，patch hermes_memory 不再影响 executor）。
        with patch.object(self.exec_mod, "_run_hermes_agent", _capture_agent), \
             patch.object(self.exec_mod, "_write_memory", lambda *a, **kw: True), \
             patch.object(literature_service, "LiteratureService", MagicMock(return_value=fake_svc)), \
             patch.object(external_fetcher, "search_academic", lambda *a, **kw: []):
            result = self.exec_mod._run_lit_search_step(
                c, pid, {"round": 8, "section_key": "content"})

        self.assert_true(
            result.get("success") is True, "排除清单截断路径应正常 success")
        prompt = captured.get("prompt", "")
        self.assert_in(
            "程序化执行", prompt, "截断清单应说明完整去重由系统程序化执行")
        self.assert_in(
            "300 篇", prompt, "应提示总量（300 篇）")
        # 300 个 ID 不应全量注入：采样 80 个 + 说明文字，总 prompt 受控
        injected_ids = sum(1 for i in range(300) if f"24{i:03d}.01{i:04d}" in prompt)
        self.assert_true(
            injected_ids <= 80, f"注入 ID 数应 ≤80，实际 {injected_ids}")
        self.assert_true(
            len(prompt) < 6000, f"prompt 总长应受控（<6000 字符），实际 {len(prompt)}")

    # ------------------------------------------------------------------
    # 3. 已通过章节跳过
    # ------------------------------------------------------------------

    def _test_section_skip_in_round_jobs(self):
        pid = "general-section-skip-20260101"
        c, _ = self._register(pid)
        st = c._get_proposal_state(pid)
        st["optimization_rounds"] = 7
        st["idea_review_passed"] = True
        st["section_passes"] = {"rationale": True, "content": False, "scheme": True}
        c._set_proposal_state(pid, st)

        # 常规轮（8 % 3 != 0）：rationale/scheme 跳过，content 全链保留
        jobs8 = c._build_full_round_jobs(pid, 8)
        steps_by_section = {}
        for j in jobs8:
            steps_by_section.setdefault(j["section_key"], []).append(j["step"])
        self.assert_true(
            "rationale" not in steps_by_section, "r8 常规轮应跳过已通过的 rationale")
        self.assert_true(
            "scheme" not in steps_by_section, "r8 常规轮应跳过已通过的 scheme")
        self.assert_eq(
            sorted(steps_by_section.get("content", [])),
            ["critic", "gap_identify", "lit_note", "lit_read", "lit_search", "writer"],
            "未通过的 content 应保留完整 6-job 对抗链")
        self.assert_true(
            "full_review" in steps_by_section and "monitor" in steps_by_section,
            "full_review/references/monitor/derived 不受章节跳过影响")
        # 依赖重接：full_review critic 依赖 content 的 writer
        content_writer = next(
            (j["job_id"] for j in jobs8
             if j["section_key"] == "content" and j["step"] == "writer"), "")
        full_critic = next(
            (j for j in jobs8 if j["section_key"] == "full_review" and j["step"] == "critic"), {})
        self.assert_in(
            content_writer, full_critic.get("depends_on", []),
            "跳过章节后 full_review critic 应依赖最近未跳过章节的 writer")

        # 全部通过的常规轮：3 章节全跳，full_review critic 回落无依赖（无 idea_review）
        st["section_passes"] = {"rationale": True, "content": True, "scheme": True}
        c._set_proposal_state(pid, st)
        jobs9 = c._build_full_round_jobs(pid, 10)  # 10 % 3 != 0
        for sec in ("rationale", "content", "scheme"):
            self.assert_true(
                sec not in {j["section_key"] for j in jobs9},
                f"r10 应跳过已通过的 {sec}")
        full_critic10 = next(
            (j for j in jobs9 if j["section_key"] == "full_review" and j["step"] == "critic"), {})
        self.assert_eq(
            full_critic10.get("depends_on", []), [],
            "全跳过且无 idea_review 时 full_review critic 依赖应为空")

        # 强制复检轮（9 % 3 == 0）：全量构建（v7.3.0 起 26 job：手册链入列，
        # derived update_method_manual 撤除——18+2+2+2+1+1）
        jobs_recheck = c._build_full_round_jobs(pid, 9)
        recheck_sections = {j["section_key"] for j in jobs_recheck}
        for sec in ("rationale", "content", "scheme"):
            self.assert_in(
                sec, recheck_sections, f"r9 复检轮应全量构建 {sec}")
        self.assert_in(
            "method_manual", recheck_sections, "r9 复检轮应全量构建手册链（v7.3.0）")
        self.assert_eq(
            len(jobs_recheck), 26, "复检轮应构建完整 26 job（v7.3.0）")

    # ------------------------------------------------------------------
    # 4. lit_read 合并单会话
    # ------------------------------------------------------------------

    def _test_lit_read_merged_session(self):
        pid = "general-litread-merge-20260101"
        c, prop_dir = self._register(pid)
        td = prop_dir / "02_literature" / "targeted-research"
        td.mkdir(parents=True, exist_ok=True)
        (td / "lit-gap-200.json.md").write_text(
            "# 定向文献检索报告\n## 章节\ncontent\n## 检索结果\n"
            "- 2403.19535 | 论文A\n- 1805.03806 | 论文B\n",
            encoding="utf-8",
        )

        import hermes_memory
        import literature_service

        agent_calls = []
        long_note = "### 研究问题\n" + "这是一段足够长的笔记内容。" * 20
        merged_output = (
            f"## 2403.19535\n\n{long_note}\n\n"
            "## 1805.03806\n\n短"
        )

        def _merged_agent(profile, prompt, timeout=300):
            agent_calls.append(prompt)
            return {"success": True, "output": merged_output, "error": "", "elapsed_s": 60.0}

        fake_svc = MagicMock()
        fake_svc._get_wiki_paper_note.return_value = None
        fake_svc._save_wiki_paper_note.return_value = True
        fake_svc._update_read_status.return_value = True
        fake_svc.read.return_value = {"content": "降级直读内容" * 10}

        # v7.2.69 修复（BUG-26）：patch 目标改为 executor 模块自身——
        # v7.2.2 把 _run_hermes_agent/_write_memory 提升到 executor 模块级
        # （from hermes_memory import ... 一次性绑定），此后 patch hermes_memory
        # 模块属性不再影响 executor 内的引用 → mock 失效 → 真实 agent loop
        # 被派发（每次 360s 超时）→ 4 条断言全败。patch 被调用方模块而非
        # 定义方模块才生效。
        with patch.object(self.exec_mod, "_run_hermes_agent", _merged_agent), \
             patch.object(self.exec_mod, "_write_memory", lambda *a, **kw: True), \
             patch.object(literature_service, "LiteratureService", MagicMock(return_value=fake_svc)):
            result = self.exec_mod._run_lit_read_step(
                c, pid, {"round": 8, "section_key": "content"})

        self.assert_true(
            result.get("success") is True, "合并会话路径应 success")
        self.assert_eq(
            len(agent_calls), 1, "5 篇以内应只派 1 个合并会话（旧实现逐篇 5 个）")
        self.assert_eq(
            result.get("read_count"), 2,
            "1 篇会话笔记 + 1 篇降级直读，共 2 篇")
        notes_path = Path(result.get("notes_path", ""))
        self.assert_true(notes_path.exists(), "reading-notes 应落盘")
        if notes_path.exists():
            notes = notes_path.read_text(encoding="utf-8")
            self.assert_in("## 2403.19535", notes, "会话笔记应含有效篇目")
            self.assert_in("## 1805.03806", notes, "截断篇目应经降级直读补齐")
        # 会话笔记写入 wiki，降级篇目由 read 自行处理
        self.assert_eq(
            fake_svc._save_wiki_paper_note.call_count, 1,
            "仅会话产出的有效篇目写 wiki 笔记")

    def run_tests(self):
        self._test_empty_gap_short_circuit()
        self._test_exclude_prompt_capped()
        self._test_section_skip_in_round_jobs()
        self._test_lit_read_merged_session()
