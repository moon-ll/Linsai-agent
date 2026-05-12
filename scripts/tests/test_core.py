#!/usr/bin/env python3
"""
test_core.py — 核心模块单元测试

覆盖：
    - session_manager: 创建、追加、列出、加载
    - knowledge_base: 搜索、别名、智能触发、健康度
    - skill_manager: 列出、匹配、搜索、配置
    - task_manager: 创建、流转、列出
    - memory_manager: 画像更新、片段搜索
    - context_builder: 上下文构建（预算控制）
"""

import sys
import json
from pathlib import Path

# 框架
from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT, TestResult

# 各模块需在隔离环境中导入
import importlib


class CoreModuleTests(TestSuite):
    def __init__(self):
        super().__init__("核心模块单元测试")
        self.tmp_root = None
        self.sm = None  # session_manager
        self.kb = None  # knowledge_base
        self.skm = None  # skill_manager
        self.tm = None  # task_manager
        self.mm = None  # memory_manager
        self.cb = None  # context_builder

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 强制重新导入各模块（确保拿到未污染版本）
        for mod_name in ["session_manager", "knowledge_base", "skill_manager",
                         "task_manager", "memory_manager", "context_builder"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        self.sm = importlib.import_module("session_manager")
        self.kb = importlib.import_module("knowledge_base")
        self.skm = importlib.import_module("skill_manager")
        self.tm = importlib.import_module("task_manager")
        self.mm = importlib.import_module("memory_manager")
        self.cb = importlib.import_module("context_builder")

        # Monkey-patch 根目录
        for mod in [self.sm, self.kb, self.skm, self.tm, self.mm, self.cb]:
            patch_module_root(mod.__name__, self.tmp_root)
        # task_manager 额外缓存变量
        self.tm.TASKS_DIR = self.tmp_root / "tasks"
        self.tm.STATUS_DIRS = {
            "backlog": self.tm.TASKS_DIR / "backlog",
            "active": self.tm.TASKS_DIR / "active",
            "completed": self.tm.TASKS_DIR / "completed",
            "paused": self.tm.TASKS_DIR / "backlog",
        }

    def teardown(self):
        import shutil
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ------------------------------------------------------------------
    # session_manager
    # ------------------------------------------------------------------
    def _test_session_crud(self):
        sid, sdir = self.sm.create_session("固体HHG实验", "co-working")
        self.assert_true(sid.startswith("2026") or sid.startswith("202"), "会话ID格式", f"sid={sid}")
        self.assert_true((self.tmp_root / "sessions" / sid).exists(), "会话目录创建")

        msg = self.sm.append_message(sid, "user", "激光波长 800nm")
        self.assert_eq(msg["role"], "user", "消息角色")
        self.assert_in("激光波长", msg["content"], "消息内容")

        msgs, state = self.sm.load_session(sid)
        self.assert_true(len(msgs) >= 1, "加载消息数")
        self.assert_eq(state["mode"], "co-working", "会话模式")

        sessions = self.sm.list_sessions("active")
        self.assert_true(len(sessions) >= 1, "列出活跃会话")
        self.assert_true(any(s["session_id"] == sid for s in sessions), "列表包含新会话")

    # ------------------------------------------------------------------
    # knowledge_base（只读测试，使用真实索引）
    # ------------------------------------------------------------------
    def _test_kb_search(self):
        # 使用真实数据（只读）
        patch_module_root("knowledge_base", REAL_ROOT)
        kb = importlib.import_module("knowledge_base")
        results = kb.search("HHG", top_k=3)
        self.assert_true(isinstance(results, list), "搜索返回列表")

    def _test_kb_aliases(self):
        patch_module_root("knowledge_base", REAL_ROOT)
        kb = importlib.import_module("knowledge_base")
        expanded = kb._expand_query_with_aliases("高次谐波产生")
        self.assert_in("高次谐波产生", expanded, "别名展开 高次谐波产生")

    def _test_kb_trigger(self):
        patch_module_root("knowledge_base", REAL_ROOT)
        kb = importlib.import_module("knowledge_base")
        self.assert_true(kb.should_search_knowledge("查一下固体HHG的知识", "co-working"), "明确查询触发")
        self.assert_true(not kb.should_search_knowledge("你好", "co-working"), "闲聊不触发")

    def _test_kb_health(self):
        patch_module_root("knowledge_base", REAL_ROOT)
        kb = importlib.import_module("knowledge_base")
        health = kb.get_kb_health()
        self.assert_in("indexed", health, "健康度包含索引状态")

    # ------------------------------------------------------------------
    # skill_manager（只读，使用真实 skills 目录）
    # ------------------------------------------------------------------
    def _test_skill_list(self):
        patch_module_root("skill_manager", REAL_ROOT)
        skm = importlib.import_module("skill_manager")
        skm.reload_skills()
        skills = skm.list_skills()
        self.assert_true(len(skills) >= 7, f"技能数量≥7 (实际{len(skills)})")
        names = [s["name"] for s in skills]
        self.assert_in("math-derivation", names, "math-derivation 存在")
        self.assert_in("literature-distill", names, "literature-distill 存在")

    def _test_skill_match(self):
        patch_module_root("skill_manager", REAL_ROOT)
        skm = importlib.import_module("skill_manager")
        skm.reload_skills()
        matched = skm.match_skills("帮我推导薛定谔方程")
        self.assert_in("math-derivation", matched, "推导触发 math-derivation")

    def _test_skill_config(self):
        patch_module_root("skill_manager", REAL_ROOT)
        skm = importlib.import_module("skill_manager")
        cfg = skm.get_skill_config()
        self.assert_in("mode", cfg, "配置含 mode")
        self.assert_in("active_skills", cfg, "配置含 active_skills")

    # ------------------------------------------------------------------
    # task_manager（隔离环境）
    # ------------------------------------------------------------------
    def _test_task_crud(self):
        task_id, task_path = self.tm.create_task("测试任务-光路设计", priority="high", category="experiment")
        self.assert_true(task_id.startswith("TASK-"), "任务ID格式")
        tid = task_id

        fetched = self.tm.get_task(tid)
        self.assert_eq(fetched["title"], "测试任务-光路设计", "任务标题")

        # 状态流转: backlog -> active -> completed
        ok1 = self.tm.transition_task(tid, "active")
        self.assert_true(ok1, "任务激活流转")
        ok2 = self.tm.transition_task(tid, "completed")
        self.assert_true(ok2, "任务完成流转")
        completed = self.tm.list_tasks("completed")
        self.assert_true(any(t["task_id"] == tid for t in completed), "任务在 completed 列表")

        # 清理
        deleted = self.tm.delete_task(tid)
        self.assert_true(deleted, "任务删除成功")

    # ------------------------------------------------------------------
    # memory_manager（隔离环境）
    # ------------------------------------------------------------------
    def _test_memory_profile(self):
        # 先创建会话以提供 session_id
        sid, _ = self.sm.create_session("记忆测试", "co-working")
        profile = self.mm.update_user_profile(sid)
        self.assert_in("interaction_history", profile, "画像结构")

    def _test_memory_snippet(self):
        sid, _ = self.sm.create_session("片段测试", "co-working")
        self.mm.create_snippet("固体HHG", "固体高次谐波产生基础", sid, 3)
        snippets = self.mm.search_snippets("固体HHG", limit=5)
        self.assert_true(len(snippets) >= 1, "片段搜索返回")

    # ------------------------------------------------------------------
    # context_builder（隔离环境，但需要 persona）
    # ------------------------------------------------------------------
    def _test_context_budget(self):
        # 复制 persona 到隔离环境
        import shutil
        persona_src = REAL_ROOT / "persona" / "lin-sai-persona.md"
        if persona_src.exists():
            shutil.copy(persona_src, self.tmp_root / "persona" / "lin-sai-persona.md")
        sid, _ = self.sm.create_session("上下文测试", "co-working")
        self.sm.append_message(sid, "user", "激光波长 800nm，强度 1e14 W/cm2")
        ctx = self.cb.build_context(sid, "帮我设计光路", mode="co-working")
        self.assert_true(isinstance(ctx, dict), "上下文为字典")
        sys_prompt = ctx.get("system_prompt", "")
        self.assert_true(isinstance(sys_prompt, str), "system_prompt 为字符串")
        self.assert_true(len(sys_prompt) <= 50000, f"上下文预算控制 ({len(sys_prompt)} chars)")
        self.assert_in("林赛", sys_prompt, "上下文含人格锚点")

    # ------------------------------------------------------------------
    # copilot_engine（关键回归：detect_llm_cli 曾遍历 dict 键导致 TypeError）
    # ------------------------------------------------------------------
    def _test_copilot_engine_cli(self):
        ce = importlib.import_module("copilot_engine")
        try:
            result = ce.detect_llm_cli()
            self.assert_true(result is None or isinstance(result, tuple), "detect_llm_cli 返回类型", f"返回 {type(result)}")
            if result is not None:
                self.assert_true(len(result) == 2, "detect_llm_cli 返回二元组", f"长度={len(result)}")
                self.assert_true(all(isinstance(x, str) for x in result), "detect_llm_cli 返回字符串元组")
        except TypeError as e:
            self.assert_true(False, "detect_llm_cli 不抛 TypeError", str(e))

    # ------------------------------------------------------------------
    def run_tests(self):
        print(f"\n▶ {self.name}")
        tests = [
            self._test_session_crud,
            self._test_kb_search,
            self._test_kb_aliases,
            self._test_kb_trigger,
            self._test_kb_health,
            self._test_skill_list,
            self._test_skill_match,
            self._test_skill_config,
            self._test_task_crud,
            self._test_memory_profile,
            self._test_memory_snippet,
            self._test_context_budget,
            self._test_copilot_engine_cli,
        ]
        for t in tests:
            try:
                t()
            except Exception as e:
                self.results.append(
                    TestResult(t.__name__, False, 0.0, f"{type(e).__name__}: {e}")
                )
