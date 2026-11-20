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
    - v3.5 课题模块链路: project_manager / unit_manager / project_kb /
      project_memory / project_context / project_workflow 全链路隔离测试
    - llm_router: 模块导入、router 对象、provider 列表、配置加载
    - tool_engine: 工具注册表完整性、file_read/file_write、calc、run_command 安全检查
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
        # v6.8.53: 增加 "paths"——lifecycle 系列套件（test_auto_retry 等）直接
        # patch paths.PROJECT_ROOT = tmp 且无 teardown 恢复；若不重载，skill_manager
        # 重新 import 时 from paths import PROJECT_ROOT 拿到残留 tmp 路径，
        # SKILLS_DIR 固化到空 tmp → 技能数 0（web-ci 全量模式下 test_core 排在
        # 这些套件之后，4 项技能测试失败）。重载后 paths 总是从 __file__ 推导
        # 出真实根，后续 patch_module_root 才能正确替换。
        for mod_name in ["session_manager", "knowledge_base", "skill_manager",
                         "task_manager", "memory_manager", "context_builder",
                         "paths"]:
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
        self.assert_true(isinstance(results, dict), "搜索返回字典")
        self.assert_in("results", results, "搜索结果含 results 字段")
        self.assert_in("total", results, "搜索结果含 total 字段")

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


# ---------------------------------------------------------------------------
# v3.5 课题模块链路测试（隔离环境）
# ---------------------------------------------------------------------------
class LLMRouterTests(TestSuite):
    """llm_router 模块导入、router 对象、provider 列表、配置加载测试。"""

    def __init__(self):
        super().__init__("LLM 路由器测试")
        self.lr = None

    def setup(self):
        # 重新导入以确保干净状态（不 patch 路径，仅做只读检查）
        if "llm_router" in sys.modules:
            del sys.modules["llm_router"]
        self.lr = importlib.import_module("llm_router")

    def run_tests(self):
        print(f"\n▶ {self.name}")
        try:
            self._test_router()
        except Exception as e:
            self.results.append(
                TestResult("_test_router", False, 0.0, f"{type(e).__name__}: {e}")
            )

    def _test_router(self):
        # 1. 模块导入正常
        self.assert_true(self.lr is not None, "llm_router 模块导入")
        # 2. router 对象存在
        self.assert_true(hasattr(self.lr, "router"), "router 对象存在")
        # 3. providers 是列表
        self.assert_true(
            isinstance(self.lr.router.providers, list),
            "router.providers 是列表",
        )
        # 4. get_status 返回字典
        status = self.lr.router.get_status()
        self.assert_true(isinstance(status, dict), "get_status 返回字典")
        # 5. status 含 providers 键
        self.assert_in("providers", status, "status 含 providers 键")


# ---------------------------------------------------------------------------
# 工具引擎测试（隔离环境）
# ---------------------------------------------------------------------------
class ToolEngineTests(TestSuite):
    """tool_engine 工具注册表完整性、file_read/file_write、calc、run_command 安全检查。"""

    def __init__(self):
        super().__init__("工具引擎测试")
        self.tmp_root = None
        self.te = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        if "tool_engine" in sys.modules:
            del sys.modules["tool_engine"]
        self.te = importlib.import_module("tool_engine")
        # patch PROJECT_ROOT 到隔离环境（必须 resolve，否则 _safe_path 的
        # startswith 校验在 macOS 符号链接 /var→/private/var 下会路径越界）
        self.te.PROJECT_ROOT = self.tmp_root.resolve()

    def teardown(self):
        import shutil
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        print(f"\n▶ {self.name}")
        try:
            self._test_tools()
        except Exception as e:
            self.results.append(
                TestResult("_test_tools", False, 0.0, f"{type(e).__name__}: {e}")
            )

    def _test_tools(self):
        # 1-4. 工具注册表完整性
        registry = self.te._TOOL_REGISTRY
        self.assert_in("file_read", registry, "注册表含 file_read")
        self.assert_in("file_write", registry, "注册表含 file_write")
        self.assert_in("calc", registry, "注册表含 calc")
        self.assert_in("run_command", registry, "注册表含 run_command")
        # 5. calc 工具
        result = self.te.tool_calc("2 + 3")
        self.assert_eq(result, "5", "calc 计算 2+3")
        # 6-7. file_write / file_read 往返
        wres = self.te.tool_file_write("memory/test_tool.txt", "hello 林赛")
        self.assert_in("✓", wres, "file_write 成功")
        rres = self.te.tool_file_read("memory/test_tool.txt")
        self.assert_in("hello 林赛", rres, "file_read 读回内容")
        # 8. 危险命令拦截
        safe, reason = self.te._is_command_safe("rm -rf /")
        self.assert_true(not safe, "危险命令 rm -rf / 被拦截", reason)


# ---------------------------------------------------------------------------
# kb_* 子模块单元测试（隔离环境）
# ---------------------------------------------------------------------------
class KbSubmoduleTests(TestSuite):
    """kb_text / kb_graph / kb_health 子模块单元测试。

    测试 v3.5.5 拆分后的子模块核心功能：
        - kb_text: 分词、frontmatter 解析/生成
        - kb_graph: 图节点 CRUD、关联概念遍历
        - kb_health: 健康度计算、连通性、孤儿节点
    使用临时目录隔离，patch 路径常量并注入门面依赖桩。
    """

    def __init__(self):
        super().__init__("kb_* 子模块单元测试")
        self.tmp_root = None
        self.kbt = None  # kb_text
        self.kbg = None  # kb_graph
        self.kbh = None  # kb_health
        self._orig = {}  # 保存原始值用于恢复

    def setup(self):
        self.tmp_root = create_isolated_env()
        kb_dir = self.tmp_root / "knowledge"
        # 清除 create_isolated_env 复制的真实数据文件，确保空白起点
        for fname in ["graph.json", "aliases.json", "index.json", "growth-log.json"]:
            f = kb_dir / fname
            if f.exists():
                f.unlink()
        # 创建子模块所需的目录结构
        for sub in ["wiki/concepts", "wiki/methods", "wiki/people",
                     "wiki/papers", "wiki/projects",
                     "raw/papers", "raw/notes", "raw/webclips",
                     "captures"]:
            (kb_dir / sub).mkdir(parents=True, exist_ok=True)

        # 导入子模块
        import kb_text, kb_graph, kb_index, kb_wiki, kb_health
        self.kbt = kb_text
        self.kbg = kb_graph
        self.kbh = kb_health

        # —— patch kb_graph 路径 ——
        self._orig["kb_graph.GRAPH_PATH"] = kb_graph.GRAPH_PATH
        self._orig["kb_graph.ALIASES_PATH"] = kb_graph.ALIASES_PATH
        kb_graph.GRAPH_PATH = kb_dir / "graph.json"
        kb_graph.ALIASES_PATH = kb_dir / "aliases.json"

        # —— patch kb_index 路径 ——
        self._orig["kb_index.INDEX_PATH"] = kb_index.INDEX_PATH
        self._orig["kb_index.KNOWLEDGE_DIR"] = kb_index.KNOWLEDGE_DIR
        self._orig["kb_index.RAW_DIR"] = kb_index.RAW_DIR
        self._orig["kb_index.WIKI_DIR"] = kb_index.WIKI_DIR
        kb_index.INDEX_PATH = kb_dir / "index.json"
        kb_index.KNOWLEDGE_DIR = kb_dir
        kb_index.RAW_DIR = kb_dir / "raw"
        kb_index.WIKI_DIR = kb_dir / "wiki"

        # —— patch kb_wiki 路径 ——
        self._orig["kb_wiki.KNOWLEDGE_DIR"] = kb_wiki.KNOWLEDGE_DIR
        self._orig["kb_wiki.WIKI_DIR"] = kb_wiki.WIKI_DIR
        kb_wiki.KNOWLEDGE_DIR = kb_dir
        kb_wiki.WIKI_DIR = kb_dir / "wiki"

        # —— patch kb_health 路径 ——
        self._orig["kb_health.KNOWLEDGE_DIR"] = kb_health.KNOWLEDGE_DIR
        kb_health.KNOWLEDGE_DIR = kb_dir

        # —— 注入门面依赖桩（kb_index）——
        self._orig["kb_index._ensure_dirs"] = kb_index._ensure_dirs
        self._orig["kb_index.log_growth"] = kb_index.log_growth
        self._orig["kb_index._load_aliases"] = kb_index._load_aliases
        self._orig["kb_index._log"] = kb_index._log

        def _stub_ensure_dirs():
            for d in [kb_dir / "raw" / "papers", kb_dir / "raw" / "notes",
                      kb_dir / "raw" / "webclips"]:
                d.mkdir(parents=True, exist_ok=True)
            for t in ["concepts", "methods", "people", "papers", "projects"]:
                (kb_dir / "wiki" / t).mkdir(parents=True, exist_ok=True)

        kb_index._ensure_dirs = _stub_ensure_dirs
        kb_index.log_growth = lambda *a, **kw: None
        kb_index._load_aliases = lambda: {}
        kb_index._log = None

        # —— 注入门面依赖桩（kb_wiki）——
        self._orig["kb_wiki._ensure_dirs"] = kb_wiki._ensure_dirs
        self._orig["kb_wiki.log_growth"] = kb_wiki.log_growth
        self._orig["kb_wiki._log"] = kb_wiki._log
        kb_wiki._ensure_dirs = _stub_ensure_dirs
        kb_wiki.log_growth = lambda *a, **kw: None
        kb_wiki._log = None

        # —— 注入门面依赖桩（kb_health）——
        self._orig["kb_health.get_growth_candidates"] = kb_health.get_growth_candidates
        self._orig["kb_health.get_growth_log"] = kb_health.get_growth_log
        kb_health.get_growth_candidates = lambda: []
        kb_health.get_growth_log = lambda limit=50, target=None: []

    def teardown(self):
        # 恢复所有 patch 的值
        import kb_graph, kb_index, kb_wiki, kb_health
        kb_graph.GRAPH_PATH = self._orig["kb_graph.GRAPH_PATH"]
        kb_graph.ALIASES_PATH = self._orig["kb_graph.ALIASES_PATH"]
        kb_index.INDEX_PATH = self._orig["kb_index.INDEX_PATH"]
        kb_index.KNOWLEDGE_DIR = self._orig["kb_index.KNOWLEDGE_DIR"]
        kb_index.RAW_DIR = self._orig["kb_index.RAW_DIR"]
        kb_index.WIKI_DIR = self._orig["kb_index.WIKI_DIR"]
        kb_index._ensure_dirs = self._orig["kb_index._ensure_dirs"]
        kb_index.log_growth = self._orig["kb_index.log_growth"]
        kb_index._load_aliases = self._orig["kb_index._load_aliases"]
        kb_index._log = self._orig["kb_index._log"]
        kb_wiki.KNOWLEDGE_DIR = self._orig["kb_wiki.KNOWLEDGE_DIR"]
        kb_wiki.WIKI_DIR = self._orig["kb_wiki.WIKI_DIR"]
        kb_wiki._ensure_dirs = self._orig["kb_wiki._ensure_dirs"]
        kb_wiki.log_growth = self._orig["kb_wiki.log_growth"]
        kb_wiki._log = self._orig["kb_wiki._log"]
        kb_health.KNOWLEDGE_DIR = self._orig["kb_health.KNOWLEDGE_DIR"]
        kb_health.get_growth_candidates = self._orig["kb_health.get_growth_candidates"]
        kb_health.get_growth_log = self._orig["kb_health.get_growth_log"]
        # 清理临时目录
        import shutil
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        print(f"\n▶ {self.name}")
        try:
            self._test_kb_text()
            self._test_kb_graph()
            self._test_kb_health()
            self._test_kb_graph_defensive()
        except Exception as e:
            self.results.append(
                TestResult("_kb_submodule", False, 0.0, f"{type(e).__name__}: {e}")
            )

    # ------------------------------------------------------------------
    # kb_text：分词 + frontmatter
    # ------------------------------------------------------------------
    def _test_kb_text(self):
        # 1. 分词：中英文混合
        tokens = self.kbt._tokenize("固体高次谐波 HHG")
        self.assert_true(
            any("高次" in t for t in tokens) and "hhg" in tokens,
            "kb_text 分词中英文混合",
        )
        # 2. frontmatter 解析
        fm, body = self.kbt.parse_frontmatter(
            '---\ntitle: "测试"\nconfidence: 0.9\ngrowth_stage: "mature"\n---\n正文'
        )
        self.assert_eq(fm.get("title"), "测试", "kb_text frontmatter 解析 title")
        self.assert_eq(fm.get("growth_stage"), "mature", "kb_text frontmatter 解析 stage")

    # ------------------------------------------------------------------
    # kb_graph：节点 CRUD + 关联遍历
    # ------------------------------------------------------------------
    def _test_kb_graph(self):
        # 3. 节点创建 + 边添加
        self.kbg.update_graph_node("概念X", "concepts", "wiki/concepts/概念X.md", "growing")
        self.kbg.update_graph_node("概念Y", "concepts", "wiki/concepts/概念Y.md", "mature")
        self.kbg.add_graph_edge("概念X", "概念Y", "related")
        graph = self.kbg._load_graph()
        self.assert_true(
            "概念X" in graph["nodes"] and "概念Y" in graph["nodes"],
            "kb_graph 节点创建",
        )
        # 4. 关联概念遍历
        related = self.kbg.get_related_concepts("概念X", depth=1)
        self.assert_true(
            len(related) >= 1 and related[0]["title"] == "概念Y",
            "kb_graph 关联遍历",
        )
        # 5. 节点删除（级联清理边）
        self.kbg._remove_graph_node("概念Y")
        graph = self.kbg._load_graph()
        self.assert_true(
            "概念Y" not in graph["nodes"] and len(graph["edges"]) == 0,
            "kb_graph 节点删除+边清理",
        )

    # ------------------------------------------------------------------
    # kb_health：健康度计算
    # ------------------------------------------------------------------
    def _test_kb_health(self):
        import json
        kb_dir = self.tmp_root / "knowledge"

        # 准备图谱数据：2 节点连通 + 1 孤儿
        graph_data = {
            "nodes": {
                "节点A": {"type": "concepts", "path": "wiki/concepts/节点A.md", "growth_stage": "mature"},
                "节点B": {"type": "concepts", "path": "wiki/concepts/节点B.md", "growth_stage": "growing"},
                "孤儿节点": {"type": "concepts", "path": "wiki/concepts/不存在.md", "growth_stage": "seedling"},
            },
            "edges": [{"from": "节点A", "to": "节点B", "relation": "related"}],
        }
        self.kbg._save_graph(graph_data)
        # 创建对应的 wiki 文件（节点A、B 存在，孤儿不存在）
        for name in ["节点A", "节点B"]:
            (kb_dir / "wiki" / "concepts" / f"{name}.md").write_text(
                f'---\ntitle: "{name}"\ntype: "concepts"\n---\n内容', encoding="utf-8")
        # 准备索引数据
        import kb_index
        kb_index._cms.save_json(kb_dir / "index.json", {
            "documents": {"wiki/concepts/节点A.md": {"source": "wiki"}},
            "inverted": {}, "idf": {}, "doc_count": 1,
            "built_at": "2026-06-28T00:00:00Z",
            "graph_summary": {"node_count": 3, "edge_count": 1, "growth_stages": {}},
        })

        # 6. 孤儿节点计数
        orphans = self.kbh._count_graph_orphans()
        self.assert_eq(orphans, 1, "kb_health 孤儿节点计数")
        # 7. 图谱连通性
        conn = self.kbh._compute_graph_connectivity()
        self.assert_true(
            isinstance(conn, float) and 0.6 <= conn <= 0.7,
            "kb_health 连通性计算",
        )
        # 8. 综合健康度
        health = self.kbh.get_kb_health()
        self.assert_eq(health.get("graph_nodes"), 3, "kb_health 综合节点数")

    # ------------------------------------------------------------------
    # kb_graph 防御性检查（v6.10.39）：拒绝污染 title 写入图谱
    # ------------------------------------------------------------------
    def _test_kb_graph_defensive(self):
        # 9. 正常 title 仍可写入（基线）
        good_title = "正常标题v61039"
        self.kbg.update_graph_node(good_title, "concepts", "wiki/concepts/test-正常.md", "seedling")
        graph = self.kbg._load_graph()
        self.assert_true(good_title in graph["nodes"], "kb_graph 正常 title 写入通过")
        # 清理
        self.kbg._remove_graph_node(good_title)
        # 10. 连续 3 个反斜杠的污染 title 应被拒绝
        bad_title = "[" + "\\\\\\\\\\\\" * 50 + "污染节点" + "\\\\\\\\\\\\" * 50 + "]"
        self.kbg.update_graph_node(bad_title, "projects", "wiki/projects/污染.md", "mature")
        graph = self.kbg._load_graph()
        self.assert_true(bad_title not in graph["nodes"], "kb_graph 连续反斜杠污染 title 被拒绝")


# ---------------------------------------------------------------------------
# 安全与原子写入测试（v3.5.7）
# ---------------------------------------------------------------------------
class SecurityTests(TestSuite):
    """安全相关单元测试：_safe_join 路径遍历防护、save_json 原子写入。

    覆盖：
        - _safe_join 正常拼接（返回路径在 base 目录内）
        - _safe_join 路径遍历拦截（../../etc/passwd 抛 ValueError）
        - _safe_join 空路径处理
        - common.save_json 原子写入（写入后文件存在且内容正确）
        - common.save_json 覆盖写入（旧内容被新内容替换）

    导入方式（按规范）：from web_base import _safe_join；import common
    """

    def __init__(self):
        super().__init__("安全与原子写入测试")
        self.tmp_root = None
        self._safe_join = None
        self.common = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 按规范使用 from web_base import _safe_join 和 import common
        from web_base import _safe_join
        import common
        self._safe_join = _safe_join
        self.common = common

    def teardown(self):
        import shutil
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        print(f"\n▶ {self.name}")
        tests = [
            self._test_safe_join_normal,
            self._test_safe_join_traversal,
            self._test_safe_join_empty,
            self._test_save_json_atomic,
            self._test_save_json_overwrite,
        ]
        for t in tests:
            try:
                t()
            except Exception as e:
                self.results.append(
                    TestResult(t.__name__, False, 0.0, f"{type(e).__name__}: {e}")
                )

    # ------------------------------------------------------------------
    # _safe_join：正常拼接
    # ------------------------------------------------------------------
    def _test_safe_join_normal(self):
        base = self.tmp_root / "knowledge"
        base.mkdir(parents=True, exist_ok=True)
        result = self._safe_join(base, "wiki", "concept.md")
        # 返回的路径应在 base 目录内
        self.assert_true(
            str(result).startswith(str(base.resolve())),
            "_safe_join 正常拼接在 base 内",
        )

    # ------------------------------------------------------------------
    # _safe_join：路径遍历拦截
    # ------------------------------------------------------------------
    def _test_safe_join_traversal(self):
        base = self.tmp_root / "knowledge"
        base.mkdir(parents=True, exist_ok=True)
        raised = False
        try:
            self._safe_join(base, "../../etc/passwd")
        except ValueError:
            raised = True
        self.assert_true(raised, "_safe_join 拦截路径遍历 ../../etc/passwd")

    # ------------------------------------------------------------------
    # _safe_join：空路径处理
    # ------------------------------------------------------------------
    def _test_safe_join_empty(self):
        base = self.tmp_root / "data"
        base.mkdir(parents=True, exist_ok=True)
        result = self._safe_join(base)
        self.assert_eq(
            result.resolve(), base.resolve(), "_safe_join 空路径等于 base"
        )

    # ------------------------------------------------------------------
    # common.save_json：原子写入
    # ------------------------------------------------------------------
    def _test_save_json_atomic(self):
        import json
        target = self.tmp_root / "out" / "atomic.json"
        self.common.save_json(target, {"name": "林赛", "value": 42})
        self.assert_true(target.exists(), "save_json 原子写入后文件存在")
        loaded = json.loads(target.read_text(encoding="utf-8"))
        self.assert_eq(loaded.get("name"), "林赛", "save_json 内容正确 name")
        self.assert_eq(loaded.get("value"), 42, "save_json 内容正确 value")

    # ------------------------------------------------------------------
    # common.save_json：覆盖写入
    # ------------------------------------------------------------------
    def _test_save_json_overwrite(self):
        import json
        target = self.tmp_root / "out2" / "overwrite.json"
        self.common.save_json(target, {"version": 1, "old": True})
        self.common.save_json(target, {"version": 2})
        loaded = json.loads(target.read_text(encoding="utf-8"))
        self.assert_eq(loaded.get("version"), 2, "save_json 覆盖写入新内容")
        self.assert_true("old" not in loaded, "save_json 覆盖后旧字段已清除")


# ---------------------------------------------------------------------------
# v3.7 文献简报双向同步测试（隔离环境）
# ---------------------------------------------------------------------------
class BriefingSyncTests(TestSuite):
    """briefing_sync 双向同步引擎（v5.0 item-status.json schema）。

    v5.0 变更：
        - 委托 state_sync 读写 item-status.json，不再维护独立 HERMES_STATUS_PATH
        - 状态映射基于 9 级状态枚举，而非时间戳字段推断
        - 待同步队列仅由写入异常触发（新论文自动注册，不再"不在工作流"）
    """

    def __init__(self):
        super().__init__("文献简报双向同步测试")
        self.tmp_root = None
        self.bsync = None
        self.pp = None
        self.ss = None  # state_sync

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 重新导入模块（含 state_sync，确保拿到未污染版本）
        for mod_name in ["briefing_sync", "paper_pool", "state_sync", "common"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        self.bsync = importlib.import_module("briefing_sync")
        self.pp = importlib.import_module("paper_pool")
        self.ss = importlib.import_module("state_sync")
        # patch 路径到隔离环境
        patch_module_root("paper_pool", self.tmp_root)
        self.pp.POOL_PATH = self.tmp_root / "memory" / "paper-pool.json"
        # patch briefing_sync 的同步状态路径
        self.bsync.SYNC_STATE_PATH = self.tmp_root / "memory" / "sync-state.json"
        # patch state_sync 的 item-status.json 路径（v5.0 核心：委托读写）
        self.ss.ITEM_STATUS_PATH = self.tmp_root / "item-status.json"

    def teardown(self):
        import shutil
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        print(f"\n▶ {self.name}")
        try:
            self._test_can_upgrade()
        except Exception as e:
            self.results.append(TestResult("_test_can_upgrade", False, 0.0, f"{type(e).__name__}: {e}"))
        try:
            self._test_sync_to_hermes()
        except Exception as e:
            self.results.append(TestResult("_test_sync_to_hermes", False, 0.0, f"{type(e).__name__}: {e}"))
        try:
            self._test_new_paper_register()
        except Exception as e:
            self.results.append(TestResult("_test_new_paper_register", False, 0.0, f"{type(e).__name__}: {e}"))
        try:
            self._test_pending_queue()
        except Exception as e:
            self.results.append(TestResult("_test_pending_queue", False, 0.0, f"{type(e).__name__}: {e}"))
        try:
            self._test_flush_pending()
        except Exception as e:
            self.results.append(TestResult("_test_flush_pending", False, 0.0, f"{type(e).__name__}: {e}"))
        try:
            self._test_sync_from_hermes()
        except Exception as e:
            self.results.append(TestResult("_test_sync_from_hermes", False, 0.0, f"{type(e).__name__}: {e}"))
        try:
            self._test_get_paper_status()
        except Exception as e:
            self.results.append(TestResult("_test_get_paper_status", False, 0.0, f"{type(e).__name__}: {e}"))

    def _test_can_upgrade(self):
        """状态升级判断：只升不降。"""
        self.assert_true(self.bsync._can_upgrade("unseen", "viewed"), "unseen→viewed 可升级")
        self.assert_true(self.bsync._can_upgrade("unseen", "archived"), "unseen→archived 可升级")
        self.assert_true(self.bsync._can_upgrade("viewed", "archived"), "viewed→archived 可升级")
        self.assert_true(not self.bsync._can_upgrade("archived", "viewed"), "archived→viewed 不可降级")
        self.assert_true(not self.bsync._can_upgrade("viewed", "viewed"), "同级不可升级")
        self.assert_true(not self.bsync._can_upgrade("archived", "unseen"), "archived→unseen 不可降级")

    def _test_sync_to_hermes(self):
        """反向同步：CoPilot archived → item-status.json status=archived。"""
        # 先在 paper-pool 中添加论文（提供元数据）
        self.pp._save({"2403.15337": {
            "status": "viewed",
            "title": "测试论文",
            "direction": "固体HHG",
            "added_at": "2026-07-02T00:00:00Z",
        }})

        # 反向同步 archived（action=discuss_done → 统一状态 archived）
        result = self.bsync.sync_to_hermes("2403.15337", "archived", "discuss_done")
        self.assert_true(result.get("success"), "反向同步 archived 成功")

        # 验证 item-status.json 已更新
        info = self.ss.get_item_info("2403.15337")
        self.assert_true(info is not None, "item-status.json 已注册论文")
        self.assert_eq(info.get("status"), "archived", "统一状态为 archived")
        self.assert_eq(info.get("updated_by"), "copilot", "更新者为 copilot")
        self.assert_eq(info.get("title"), "测试论文", "元数据 title 已填入")
        self.assert_true(len(info.get("history", [])) >= 1, "history 有记录")

    def _test_new_paper_register(self):
        """反向同步：新论文（不在 item-status 中）→ 自动注册。"""
        # 9999.88888 不在 item-status.json 中
        result = self.bsync.sync_to_hermes("9999.88888", "viewed", "interested")
        self.assert_true(result.get("success"), "新论文同步成功（自动注册）")

        # 验证 item-status.json 已注册
        info = self.ss.get_item_info("9999.88888")
        self.assert_true(info is not None, "新论文已注册")
        self.assert_eq(info.get("status"), "interested", "统一状态为 interested")
        self.assert_true(info.get("first_seen") is not None, "first_seen 已设置")

    def _test_pending_queue(self):
        """_add_to_pending 记入待同步队列。"""
        # 直接添加一条 pending 记录（模拟写入异常场景）
        self.bsync._add_to_pending("8888.12345", "viewed", "later", "模拟写入失败")

        # 验证待同步队列
        state = self.bsync._load_sync_state()
        pending = state.get("reverse_sync_pending", [])
        self.assert_true(len(pending) >= 1, "待同步队列有记录")
        self.assert_eq(pending[-1].get("arxiv_id"), "8888.12345", "队列记录 arxiv_id")
        self.assert_eq(pending[-1].get("action"), "later", "队列记录 action")

    def _test_flush_pending(self):
        """flush_pending_reverse 重试成功。"""
        # 确保有一条 pending 记录（上一个测试添加的 8888.12345）
        # item-status.json 路径可写，重试应成功
        flush_result = self.bsync.flush_pending_reverse()
        self.assert_true(flush_result.get("flushed", 0) >= 1, "flush 重试至少 1 条成功")

        # 验证 item-status.json 已更新（8888.12345 → viewed）
        info = self.ss.get_item_info("8888.12345")
        self.assert_true(info is not None, "flush 后论文已注册")
        self.assert_eq(info.get("status"), "viewed", "flush 后状态为 viewed")

        # 再次 flush 应无待同步项
        flush_result2 = self.bsync.flush_pending_reverse()
        self.assert_eq(flush_result2.get("flushed", -1), 0, "再次 flush 无新增")

    def _test_sync_from_hermes(self):
        """正向同步：item-status.json 读取 + 水位标记更新。

        v6.8.14 重构：paper-pool.json 已废弃，sync_from_hermes() 不再
        写入 paper-pool.json，只更新同步水位标记（reverse_sync_watermark）。
        """
        # 在 item-status.json 中添加一篇论文（模拟 hermes 已归档）
        self.ss.update_item_status("1111.22222", "archived", updated_by="hermes-cron",
                                   title="正向同步测试", direction="测试")

        # 执行正向同步
        result = self.bsync.sync_from_hermes()
        self.assert_true(result.get("synced", 0) >= 1, "正向同步至少 1 篇")

        # 验证同步水位已更新（取代旧的 paper-pool 状态升级检查）
        state = self.bsync._load_sync_state()
        self.assert_true(
            state.get("reverse_sync_watermark", "") != "",
            "同步水位已更新"
        )

        # 再次同步应返回相同数量（幂等——无新增数据）
        result2 = self.bsync.sync_from_hermes()
        self.assert_eq(
            result2.get("synced", -1), result.get("synced", -2),
            "再次同步数量不变（幂等）"
        )

    def _test_get_paper_status(self):
        """paper_pool.get_paper_status 查询。"""
        # 不存在的论文返回 None
        status = self.pp.get_paper_status("nonexist.00000")
        self.assert_true(status is None, "不存在的论文返回 None")

        # 已存在的论文返回状态
        self.pp._save({"2403.99999": {
            "status": "archived",
            "title": "已归档论文",
            "added_at": "2026-07-02T00:00:00Z",
        }})
        status = self.pp.get_paper_status("2403.99999")
        self.assert_eq(status, "archived", "已存在论文返回正确状态")
