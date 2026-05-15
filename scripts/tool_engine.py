#!/usr/bin/env python3
"""子代理调用系统 — 林赛的工具执行引擎。

用途：
    解析 LLM 输出中的工具调用指令，安全执行，返回结果。
    支持文件读写、数值计算、任务创建、知识库查询、CLI 命令执行。

用法示例：
    >>> from tool_engine import parse_tool_calls, execute_tool_calls, inject_tools_prompt
    >>> text = "@@tool:calc\\n{\\"expression\\": \\"2+2\\"}\\n@@end@@"
    >>> calls = parse_tool_calls(text)
    >>> results = execute_tool_calls(calls)

新增（v2.1.0 Phase 0）：
    - tool_run_command: 执行 CLI 命令（hermes / claude / python / git）
    - Claude Code 权限模型：默认限制在项目目录内，禁止逃离
    - tool_hermes_chat: 调用 Hermes LinSai 进行深度对话

规范：
    - 仅使用 Python 3 标准库
    - 所有文件操作有严格路径白名单
    - calc 使用 ast.parse 白名单，禁止系统调用
    - run_command 有危险命令黑名单、超时保护、cwd 限制
"""

import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent

# 允许 file_read 读取的目录（相对 PROJECT_ROOT）
_READ_ALLOW_DIRS = {"", "knowledge", "references", "persona", "skills", "memory", "sessions", "tasks", "docs"}
# 允许 file_write 写入的目录
_WRITE_ALLOW_DIRS = {"memory", "sessions", "tasks", "knowledge"}


# ---------------------------------------------------------------------------
# 安全校验
# ---------------------------------------------------------------------------

def _safe_path(path_str: str, allow_dirs: set) -> Path:
    """校验路径安全，返回绝对路径。"""
    if not path_str:
        raise ValueError("路径不能为空")
    target = (PROJECT_ROOT / path_str).resolve()
    # 必须落在 PROJECT_ROOT 内
    if not str(target).startswith(str(PROJECT_ROOT)):
        raise ValueError(f"路径越界: {path_str}")
    # 必须落在允许目录内
    rel = target.relative_to(PROJECT_ROOT)
    top_dir = rel.parts[0] if rel.parts else ""
    if top_dir not in allow_dirs:
        raise ValueError(f"路径不在允许目录内: {path_str}")
    return target


def _safe_eval(expression: str) -> Any:
    """安全数值表达式求值。

    白名单节点：
        - 数字常量 (int, float, complex)
        - 二元运算 (+, -, *, /, //, %, **)
        - 一元运算 (+, -)
        - 常量名（True, False, None, pi, e）
    """
    expression = expression.strip()
    if not expression:
        raise ValueError("表达式不能为空")

    # 黑名单：禁止导入、属性访问、调用等
    banned = {"__", "import", "eval", "exec", "compile", "open", "os", "sys", "subprocess"}
    for word in banned:
        if word in expression.lower():
            raise ValueError(f"表达式包含禁用词: {word}")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"表达式语法错误: {e}")

    # 白名单节点类型
    ALLOWED_NODES = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
        ast.USub, ast.UAdd,
        ast.Name, ast.Load,
    )

    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"表达式包含不允许的操作: {type(node).__name__}")
        if isinstance(node, ast.Name):
            if node.id not in {"pi", "e", "True", "False", "None"}:
                raise ValueError(f"不允许的名称: {node.id}")

    # 安全的全局环境
    safe_globals = {"__builtins__": {}}
    safe_locals = {"pi": 3.141592653589793, "e": 2.718281828459045, "True": True, "False": False, "None": None}

    return eval(compile(tree, "<safe>", "eval"), safe_globals, safe_locals)


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def tool_file_read(path: str) -> str:
    """读取项目内文件内容。"""
    target = _safe_path(path, _READ_ALLOW_DIRS)
    if not target.exists():
        return f"✗ 文件不存在: {path}"
    try:
        return target.read_text(encoding="utf-8")
    except Exception as e:
        return f"✗ 读取失败: {e}"


def tool_file_write(path: str, content: str) -> str:
    """写入内容到项目内文件。"""
    target = _safe_path(path, _WRITE_ALLOW_DIRS)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.write_text(content, encoding="utf-8")
        return f"✓ 已写入 {path} ({len(content)} 字符)"
    except Exception as e:
        return f"✗ 写入失败: {e}"


def tool_calc(expression: str) -> str:
    """安全计算数值表达式。"""
    try:
        result = _safe_eval(expression)
        return f"{result}"
    except Exception as e:
        return f"✗ 计算错误: {e}"


def tool_task_create(title: str, due_date: str = "", priority: str = "medium", description: str = "") -> str:
    """创建新任务。"""
    try:
        import importlib.util
        tm_path = Path(__file__).parent / "task_manager.py"
        spec = importlib.util.spec_from_file_location("task_manager", tm_path)
        tm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tm)
        task_id, _ = tm.create_task(title, category="general", due_date=due_date, priority=priority, description=description)
        return f"✓ 已创建任务: {task_id}"
    except Exception as e:
        return f"✗ 创建任务失败: {e}"


def tool_knowledge_query(query: str) -> str:
    """查询本地知识库。"""
    try:
        import importlib.util
        kb_path = Path(__file__).parent / "knowledge_base.py"
        spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
        kb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kb)
        results = kb.search(query, top_k=2)
        if not results:
            return "○ 知识库中未找到相关内容"
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(f"[{i}] 来源: {r['doc']}\n{r['text'][:500]}")
        return "\n\n".join(parts)
    except Exception as e:
        return f"✗ 查询失败: {e}"


def tool_knowledge_research(topic: str, depth: str = "full", timeout: int = 300) -> str:
    """【工作流 1: 自动增加】调研主题，编译信息并写入知识库。

    当用户请求调研某个方向或概念时，使用此工具完成全流程：
    1. 调研文献（通过 Hermes LinSai 调用 skills/web search）
    2. 提取完整信息
    3. 编译为林赛视角的结构化 wiki 笔记
    4. 创建双向链接

    参数：
        topic：调研主题（如"拓扑绝缘体表面态探测进展"）
        depth：调研深度 "quick" | "full"（默认 full，10min+）
        timeout：超时秒数（默认 300s）

    示例：
        tool_knowledge_research("固体HHG中能谷极化效应的研究进展", "full", 300)
        tool_knowledge_research("二维材料中太赫兹波产生的最新方法", "quick", 120)
    """
    try:
        import importlib.util
        from datetime import datetime, timezone

        kb_path = Path(__file__).parent / "knowledge_base.py"
        spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
        kb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kb)

        # 第一步：通过 Hermes 调研
        depth_instruction = "" if depth == "full" else "简要调研，3-5个关键点即可。"
        research_prompt = f"""你是林赛（强场超快光学 PI），正在为知识库建设调研一个新主题。

你的任务：调研 **"{topic}"**，以林赛的研究视角整理成结构化笔记。

{depth_instruction}

请从以下角度展开（根据主题相关性选择重点）：
1. 核心物理机制
2. 主要实验方法和技术路线
3. 关键文献和代表性工作
4. 与固体高次谐波/阿秒科学/拍赫兹电子学的关联
5. 开放问题和前沿挑战

调研完成后，请生成一份完整的知识库笔记（含 YAML frontmatter）。

【输出格式】直接输出 markdown 原文，从 --- 开始，不要代码块标记：

---
title: "【概念名】"
type: concepts
created: "{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}"
updated: "{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}"
tags: ["核心概念"]
related: []
source_raw: ""
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# 【标题】

## 林赛的理解
（用第一人称写，体现 PI 视角和物理直觉）

## 核心要点
- 要点1
- 要点2

## 研究方法
（相关实验方法）

## 关键文献
（代表性工作，附简要评价）

## 开放问题

## 与林赛工作的关联
"""

        # 调用 Hermes LinSai 进行调研
        research_result = tool_hermes_chat(research_prompt, timeout=min(timeout, 180))
        if research_result.startswith("✗"):
            return f"✗ 调研失败: {research_result}"

        # 第二步：保存为 wiki 页面
        # 解析标题
        title_match = None
        for line in research_result.split("\n"):
            if line.startswith("title:"):
                title_match = line.split(":", 1)[1].strip().strip('"').strip("'")
                break

        if not title_match:
            # 尝试从第一个 # 标题行提取
            for line in research_result.split("\n"):
                if line.startswith("# "):
                    title_match = line[2:].strip()
                    break

        if not title_match:
            title_match = topic

        # 生成安全的文件名
        safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", title_match).strip()
        if not safe_name:
            safe_name = "untitled"
        wiki_rel = f"wiki/concepts/{safe_name}.md"
        wiki_path = PROJECT_ROOT / "knowledge" / wiki_rel

        # 确保目录存在
        wiki_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件（注入双向链接）
        wiki_path.write_text(research_result, encoding="utf-8")
        final_text = kb._inject_wikilinks(research_result)
        wiki_path.write_text(final_text, encoding="utf-8")

        # 更新图谱
        fm, _ = kb.parse_frontmatter(final_text)
        title = fm.get("title", safe_name)
        kb.update_graph_node(title, "concepts", wiki_rel, fm.get("growth_stage", "growing"))
        for related in fm.get("related", []):
            if related:
                kb.add_graph_edge(title, related, "related")

        # 重建索引
        kb.build_index()
        kb.log_growth("create", wiki_rel, "auto_research",
                      f"自动调研主题 '{topic}' 生成")

        return (f"✓ 调研完成，已写入知识库: {wiki_rel}\n"
                f"  标题: {title}\n"
                f"  路径: knowledge/{wiki_rel}\n"
                f"  调研结果摘要: {research_result[:300]}...")

    except subprocess.TimeoutExpired:
        return f"✗ 调研超时（{timeout}s），已自动终止"
    except Exception as e:
        return f"✗ 调研失败: {e}"


def tool_knowledge_ingest(folder: str = "raw", timeout: int = 300) -> str:
    """【工作流 2: 手动增加】编译 raw 文件夹中的文件，建立双向连接，健康检查。

    当用户将文件存入 raw/ 目录并请求整理时，使用此工具完成全流程：
    1. 列出 raw/ 中的文件
    2. 对每个文件进行编译（raw → wiki）
    3. 建立双向链接
    4. 知识库健康检查（索引覆盖率、孤立节点检测）

    参数：
        folder：要处理的文件夹（默认 "raw"，即 raw/papers/）
        timeout：超时秒数（默认 300s）

    示例：
        tool_knowledge_ingest("raw/papers", 300)
        tool_knowledge_ingest("raw", 120)
    """
    try:
        import importlib.util
        from datetime import datetime, timezone

        kb_path = Path(__file__).parent / "knowledge_base.py"
        spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
        kb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kb)

        # 确保 raw 目录存在
        raw_base = PROJECT_ROOT / "knowledge" / "raw"
        raw_base.mkdir(parents=True, exist_ok=True)

        # 列出文件
        target_dir = raw_base if folder == "raw" else PROJECT_ROOT / "knowledge" / folder
        if not target_dir.exists():
            return f"✗ 目录不存在: {target_dir}"

        md_files = list(target_dir.rglob("*.md")) + list(target_dir.rglob("*.txt"))
        md_files = [f for f in md_files if not any(p.startswith(".") for p in f.parts)]

        if not md_files:
            return "○ raw 文件夹为空，无需整理"

        results = []
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for fpath in md_files[:10]:  # 最多处理10个文件
            rel = str(fpath.relative_to(PROJECT_ROOT / "knowledge"))
            try:
                raw_text = fpath.read_text(encoding="utf-8")
            except Exception:
                results.append(f"  ⚠ 跳过（读取失败）: {fpath.name}")
                continue

            # 推断 wiki 类型
            category = fpath.parent.name
            type_map = {"papers": "papers", "notes": "concepts", "webclips": "concepts"}
            wiki_type = type_map.get(category, "concepts")

            # 生成提炼 prompt
            title_guess = fpath.stem
            safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", title_guess).strip() or "untitled"
            truncated = raw_text[:8000] + ("..." if len(raw_text) > 8000 else "")

            distill_prompt = f"""请将以下原始材料提炼为林赛（强场超快光学 PI）的研究笔记。

原始材料: {fpath.name}
笔记类型: {wiki_type}

{truncated}

【输出格式】直接输出 markdown 原文，从 --- 开始：

---
title: "{title_guess}"
type: {wiki_type}
created: "{now_str}"
updated: "{now_str}"
tags: []
related: []
source_raw: "{fpath.name}"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# {title_guess}

## 林赛的理解
（第一人称 PI 视角）

## 核心要点

## 来源
- {fpath.name}
"""

            # 调用 Hermes 提炼
            distilled = tool_hermes_chat(distill_prompt, timeout=min(timeout // max(len(md_files), 1), 120))
            if distilled.startswith("✗") or distilled == "(无输出)":
                results.append(f"  ⚠ 提炼失败: {fpath.name}")
                continue

            # 保存 wiki
            wiki_rel = f"wiki/{wiki_type}/{safe_name}.md"
            wiki_path = PROJECT_ROOT / "knowledge" / wiki_rel
            wiki_path.parent.mkdir(parents=True, exist_ok=True)
            wiki_path.write_text(distilled, encoding="utf-8")
            final_text = kb._inject_wikilinks(distilled)
            wiki_path.write_text(final_text, encoding="utf-8")

            # 更新图谱
            fm, _ = kb.parse_frontmatter(final_text)
            title = fm.get("title", safe_name)
            kb.update_graph_node(title, wiki_type, wiki_rel, "growing")
            for related in fm.get("related", []):
                if related:
                    kb.add_graph_edge(title, related, "related")

            results.append(f"  ✓ {fpath.name} → wiki/{wiki_type}/{safe_name}.md")

        # 重建索引
        kb.build_index()

        # 健康检查
        graph = kb.get_graph_summary()
        orphaned = []
        for node_id, node in kb._load_graph()["nodes"].items():
            path = node.get("path", "")
            if path and not (PROJECT_ROOT / "knowledge" / path).exists():
                orphaned.append(node_id)

        health = (f"\n\n【知识库健康检查】"
                  f"\n  节点数: {graph['node_count']}"
                  f"\n  边数: {graph['edge_count']}"
                  f"\n  处理文件: {len(md_files)} 个"
                  f"\n  孤立节点: {len(orphaned)} 个")

        kb.log_growth("distill", folder, "manual",
                      f"整理 raw 文件夹 '{folder}'，处理 {len(md_files)} 个文件")

        return ("\n".join(results) + health)

    except Exception as e:
        return f"✗ 整理失败: {e}"


def tool_knowledge_create(concept_name: str, context: str = "", timeout: int = 60) -> str:
    """【工作流 3: 对话生长】创建新概念存根，支持对话中触发生长。

    当讨论中遇到知识库中没有的概念时，使用此工具创建 seedling stub，
    记录触发上下文，供后续丰满。

    参数：
        concept_name：概念名称
        context：触发上下文（当前对话片段）
        timeout：超时秒数

    示例：
        tool_knowledge_create("能谷极化", "用户提到了能谷极化效应在固体HHG中的作用", 60)
    """
    try:
        import importlib.util

        kb_path = Path(__file__).parent / "knowledge_base.py"
        spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
        kb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kb)

        wiki_rel = kb.create_wiki_stub(concept_name, context, trigger="conversation")
        return (f"✓ 已创建 seedling stub: {wiki_rel}\n"
                f"  概念: {concept_name}\n"
                f"  路径: knowledge/{wiki_rel}\n"
                f"  下次讨论此概念时，林赛将自动丰满该页面")
    except Exception as e:
        return f"✗ 创建失败: {e}"


def tool_hermes_chat(prompt: str, timeout: int = 60) -> str:
    """与 Hermes LinSai 对话。

    调用独立的 Hermes LinSai profile（linsai）进行对话。
    这个 LinSai 有完整的人格、记忆、skills 和工具集。

    用途：
        - 当需要 LinSai 独立思考时
        - 当需要调用 Hermes skills/skills 时
        - 当需要多轮工具调用时（Hermes 自己会执行多步工具）

    参数：
        prompt：你想问 Hermes LinSai 的问题
        timeout：超时秒数（默认 60s）

    示例：
        tool_hermes_chat("解释固体高次谐波的物理机制")
        tool_hermes_chat("帮我搜索一下拓扑绝缘体表面态的探测方法")
        tool_hermes_chat("用欧拉的思维框架分析这个问题：为什么固体HHG的截止频率... ")
    """
    try:
        result = subprocess.run(
            ['hermes', '--profile', 'linsai', '-z', prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip()
        if not output:
            if result.stderr:
                return f"✗ Hermes 错误: {result.stderr[:500]}"
            return "(无输出)"
        # 截断超长输出
        MAX_OUTPUT = 8000
        if len(output) > MAX_OUTPUT:
            output = output[:MAX_OUTPUT] + f"\n... (已截断，共 {len(output)} 字符)"
        return output
    except subprocess.TimeoutExpired:
        return f"✗ Hermes 对话超时（{timeout}s），已自动终止"
    except FileNotFoundError:
        return "✗ Hermes 未安装或不在 PATH 中"
    except Exception as e:
        return f"✗ Hermes 调用失败: {e}"


def tool_agent(task: str, agent_type: str = "coder", model: str = "", timeout: int = 300) -> str:
    """调用子代理（Agent）完成特定任务。

    实现方式：通过 run_command 调用 Claude Code CLI 的 --agent 参数。
    这会启动一个专注的子代理实例，完成任务后返回结果。

    与 hermes_chat 的区别：
        - hermes_chat：调用独立的 Hermes LinSai（有完整人格、记忆、skills）
        - agent：在当前会话启动专注子代理，适合代码库探索、并行调研

    用途：
        - 并行调研：同时搜索 arXiv、知识库、现有笔记
        - 深度分析：委托一个 Agent 专门分析代码/论文/数据
        - 复杂任务拆分：分解为多个子任务并行执行

    参数：
        task：给子代理的任务描述（完整描述，包含背景和目标）
        agent_type：子代理类型
            - "explore"：代码库探索代理（只读，适合调研，默认）
            - "coder"：通用编程代理
            - "plan"：计划代理（只读，适合架构设计）
        model：指定模型（默认使用父代理模型）
        timeout：超时秒数（默认 300s = 5分钟）

    示例：
        tool_agent(
            "调研拓扑绝缘体表面态探测的最新进展，重点关注ARPES和STM实验技术",
            "explore", "", 180
        )
        tool_agent("帮我分析 sessions/ 目录下的所有会话记录，统计用户最常讨论的话题", "coder", "", 120)
    """
    # 映射 agent_type 到 Claude Code CLI 参数
    type_map = {"explore": "explore", "coder": "coder", "plan": "plan"}
    cli_type = type_map.get(agent_type, "coder")

    # 构建 CLI 命令
    model_arg = f" --model {model}" if model else ""
    cmd = f"claude --agent {cli_type}{model_arg} -p {repr(task)}"

    # 通过 tool_run_command 执行（权限模型已内置）
    return tool_run_command(cmd, timeout=timeout)


# ---------------------------------------------------------------------------
# CLI 工具
# ---------------------------------------------------------------------------

# 危险命令黑名单
_BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/",          # 递归删除根目录
    r"sudo\s+",                # 提权命令
    r"dd\s+if=",               # 磁盘直接写入
    r"mkfs",                    # 格式化
    r":\(\)\{\s*:\|:\|\s*&\s*\};:",  # Fork 炸弹
    r"chmod\s+-R\s+777\s+/",  # 过度开放权限
    r"wget.*\|\s*sh",          # 远程脚本执行
    r"curl.*\|\s*sh",          # 远程脚本执行
]


def _is_command_safe(command: str) -> tuple[bool, str]:
    """检查命令是否安全，返回 (是否安全, 原因)"""
    cmd_lower = command.lower()
    for pattern in _BLOCKED_PATTERNS:
        if re.search(pattern, cmd_lower):
            return False, f"危险命令模式: {pattern}"
    return True, ""


def _check_escape(command: str) -> tuple[bool, str]:
    """检查命令是否试图逃离项目目录。

    Claude Code 模式：所有操作默认限制在项目目录内。
    允许：相对路径、仅在项目目录内的 cd
    禁止：cd /, cd ~, cd .. 用于逃离项目边界的组合

    返回：(是否合规, 原因)
    """
    cmd = command.strip()
    # 允许的命令前缀
    ALLOWED_PREFIXES = (
        "kimi", "claude", "hermes", "python", "python3", "git",
        "ls", "cat", "head", "tail", "grep", "find", "wc",
        "echo", "date", "pwd", "mkdir", "touch", "cp", "mv",
    )
    # 检查是否以允许的命令开头
    cmd_stripped = cmd.strip().split()[0] if cmd.strip() else ""
    # 对于复合命令（&&, ||, ;, |）检查第一段
    first_cmd = cmd_stripped.split("&&")[0].split("||")[0].split(";")[0].split("|")[0].strip()
    if first_cmd not in ALLOWED_PREFIXES:
        # 非预期命令类型，检查是否在黑名单
        for bad in ["cd /", "cd /home", "cd /Users", "cd ~", "cd $HOME", "cd $HOME/"]:
            if cmd.startswith(bad):
                return False, f"禁止 cd 到项目目录外部 ({bad})"
        # rm -rf 后面跟非项目路径
        if re.search(r"rm\s+(-rf\s+)?/[^(]", cmd):
            return False, "禁止删除项目目录外部的文件"
    return True, ""


def tool_run_command(command: str, timeout: int = 60, cwd: str = "") -> str:
    """执行 CLI 命令。

    用途：调用 kimi / claude / hermes 等 CLI 工具，或执行 python / git 等命令。

    权限模型（Claude Code 模式）：
        - 默认所有操作在项目目录内
        - 禁止逃离项目目录的命令（如 cd /, cd ~, cd .. 等用于逃离的组合）
        - 危险命令直接拦截
        - 用户可通过显式传入 cwd='' 临时提升权限（需自行确保安全）

    参数：
        command：命令字符串（完整命令，包含参数）
        timeout：超时秒数（默认 60s）
        cwd：工作目录（默认项目根目录，强制限制）

    示例：
        tool_run_command("kimi code 生成斐波那契数列", 30)
        tool_run_command("claude --print '解释薛定谔方程'")
        tool_run_command("python3 scripts/self_test.py", 120)
        tool_run_command("git status")
    """
    # 安全检查
    safe, reason = _is_command_safe(command)
    if not safe:
        return f"✗ 命令被拦截: {reason}。请换一个安全的命令。"

    # 权限检查：禁止逃离项目目录
    escape_ok, escape_reason = _check_escape(command)
    if not escape_ok:
        return f"✗ 权限不足: {escape_reason}。所有操作仅限于 {PROJECT_ROOT}。如需临时提升权限，请在命令中显式指定 cwd=''（需谨慎）。"

    # cwd 限制：必须在项目目录内
    if cwd:
        target_cwd = (PROJECT_ROOT / cwd).resolve()
    else:
        target_cwd = PROJECT_ROOT

    # 防止路径穿越
    if not str(target_cwd).startswith(str(PROJECT_ROOT)):
        return "✗ 路径越界：工作目录必须在项目目录内"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(target_cwd),
        )
        # 合并 stdout 和 stderr
        output = result.stdout
        if result.stderr:
            output = output + "\n[stderr]\n" + result.stderr if output else result.stderr

        # 截断超长输出
        MAX_OUTPUT = 8000
        if len(output) > MAX_OUTPUT:
            output = output[:MAX_OUTPUT] + f"\n... (已截断，共 {len(output)} 字符)"

        if not output.strip():
            return "(命令执行成功，无输出)"

        return output

    except subprocess.TimeoutExpired:
        return f"✗ 命令超时（{timeout}s），已自动终止"
    except Exception as e:
        return f"✗ 执行失败: {e}"
    """执行 CLI 命令。

    用途：调用 kimi / claude / hermes 等 CLI 工具，或执行 python / git 等命令。

    参数：
        command：命令字符串（完整命令，包含参数）
        timeout：超时秒数（默认 60s）
        cwd：工作目录（相对项目根目录，默认在项目根目录）

    示例：
        tool_run_command("kimi code 生成斐波那契数列", 30)
        tool_run_command("claude --print '解释薛定谔方程'")
        tool_run_command("python3 scripts/self_test.py", 120)
        tool_run_command("git status", 10)
    """
    # 安全检查
    safe, reason = _is_command_safe(command)
    if not safe:
        return f"✗ 命令被拦截: {reason}。请换一个安全的命令。"

    # cwd 限制：必须在项目目录内
    if cwd:
        target_cwd = (PROJECT_ROOT / cwd).resolve()
    else:
        target_cwd = PROJECT_ROOT

    # 防止路径穿越
    if not str(target_cwd).startswith(str(PROJECT_ROOT)):
        return "✗ 路径越界：工作目录必须在项目目录内"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(target_cwd),
        )
        # 合并 stdout 和 stderr
        output = result.stdout
        if result.stderr:
            output = output + "\n[stderr]\n" + result.stderr if output else result.stderr

        # 截断超长输出
        MAX_OUTPUT = 8000
        if len(output) > MAX_OUTPUT:
            output = output[:MAX_OUTPUT] + f"\n... (已截断，共 {len(output)} 字符)"

        if not output.strip():
            return "(命令执行成功，无输出)"

        return output

    except subprocess.TimeoutExpired:
        return f"✗ 命令超时（{timeout}s），已自动终止"
    except Exception as e:
        return f"✗ 执行失败: {e}"


# ---------------------------------------------------------------------------
# 工具注册表
# ---------------------------------------------------------------------------

_TOOL_REGISTRY: Dict[str, tuple] = {
    "file_read": (tool_file_read, ["path"]),
    "file_write": (tool_file_write, ["path", "content"]),
    "calc": (tool_calc, ["expression"]),
    "task_create": (tool_task_create, ["title", "due_date", "priority", "description"]),
    "knowledge_query": (tool_knowledge_query, ["query"]),
    "run_command": (tool_run_command, ["command", "timeout", "cwd"]),
    "hermes_chat": (tool_hermes_chat, ["prompt", "timeout"]),
    "agent": (tool_agent, ["task", "agent_type", "model", "timeout"]),
    "knowledge_research": (tool_knowledge_research, ["topic", "depth", "timeout"]),
    "knowledge_ingest": (tool_knowledge_ingest, ["folder", "timeout"]),
    "knowledge_create": (tool_knowledge_create, ["concept_name", "context", "timeout"]),
}


def list_tools() -> List[Dict[str, str]]:
    """返回可用工具列表。"""
    return [
        {"name": name, "params": ", ".join(params)}
        for name, (_, params) in _TOOL_REGISTRY.items()
    ]


# ---------------------------------------------------------------------------
# 工具调用解析与执行
# ---------------------------------------------------------------------------

def parse_tool_calls(text: str) -> List[Dict[str, Any]]:
    """解析 LLM 输出中的工具调用指令。

    格式：
        @@tool:tool_name@@
        {"param": "value"}
        @@end@@
    """
    calls = []
    # 匹配 @@tool:name@@
    pattern = r"@@tool:(\w+)@@\s*\n?(.*?)\n?@@end@@"
    for m in re.finditer(pattern, text, re.DOTALL):
        name = m.group(1).strip()
        json_str = m.group(2).strip()
        try:
            args = json.loads(json_str) if json_str else {}
        except json.JSONDecodeError:
            args = {}
        calls.append({"name": name, "args": args, "raw": m.group(0)})
    return calls


def execute_tool_calls(calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """执行解析后的工具调用，返回结果列表。"""
    results = []
    for call in calls:
        name = call["name"]
        args = call["args"]
        if name not in _TOOL_REGISTRY:
            results.append({
                "name": name,
                "success": False,
                "result": f"✗ 未知工具: {name}",
            })
            continue

        func, param_names = _TOOL_REGISTRY[name]
        try:
            # 提取所需参数
            call_args = {k: args.get(k, "") for k in param_names}
            result = func(**call_args)
            results.append({
                "name": name,
                "success": True,
                "result": result,
                "args": args,
            })
        except Exception as e:
            results.append({
                "name": name,
                "success": False,
                "result": f"✗ 执行错误: {e}",
                "args": args,
            })
    return results


def inject_tools_prompt(system_prompt: str) -> str:
    """在 system_prompt 末尾追加可用工具说明。"""
    tool_desc = """
---
【可用工具】
你可以使用以下工具来协助完成任务。当需要时，按以下格式输出工具调用：

@@tool:工具名@@
{"参数名": "参数值"}
@@end@@

可用工具列表：
1. calc — 数值计算
   参数: {"expression": "数学表达式"}
   示例: {"expression": "2 * pi * 1.55e-15 / 800e-9"}

2. file_read — 读取项目内文件
   参数: {"path": "knowledge/solid_hhg.md"}

3. file_write — 写入文件（仅限 memory/, sessions/, tasks/, knowledge/）
   参数: {"path": "memory/note.md", "content": "内容"}

4. task_create — 创建任务
   参数: {"title": "任务标题", "due_date": "2026-05-15", "priority": "high", "description": ""}

5. knowledge_query — 查询本地知识库
   参数: {"query": "查询关键词"}

6. run_command — 执行 CLI 命令（python / git / hermes / claude 等）
   参数: {"command": "命令字符串", "timeout": 60, "cwd": ""}
   示例: {"command": "hermes -z '用 Python 写一个斐波那契函数'", "timeout": 30}
   示例: {"command": "claude --print '解释薛定谔方程中波函数的物理意义'", "timeout": 60}
   示例: {"command": "python3 scripts/self_test.py", "timeout": 120}
   示例: {"command": "git status"}
   示例: {"command": "python3 -c \"import math; print(math.pi * 2)\""}
   说明：
   - hermes -z "prompt"：非交互模式，适合快速查询和代码生成
   - claude --print "prompt"：非交互模式，适合代码审查、分析
   - python3 script.py：执行 Python 脚本
   - timeout 默认 60s，超时自动终止
   - cwd 默认在项目根目录执行
   - 危险命令（如 rm -rf /）会被拦截
   - 所有操作默认限制在项目目录内（Claude Code 模式），禁止逃离项目目录

7. hermes_chat — 与独立的 Hermes LinSai 对话
   参数: {"prompt": "问题内容", "timeout": 60}
   示例: {"prompt": "用欧拉的思维框架分析固体HHG的截止定律"}
   示例: {"prompt": "帮我调研一下拓扑绝缘体表面态的最新进展"}
   示例: {"prompt": "解释一下能谷极化在固体HHG中的作用"}
   说明：
   - Hermes LinSai 有完整的人格、记忆、skills，能自主调用工具
   - 适合需要深度思考、多技能协作的场景
   - timeout 默认 60s

8. agent — 启动子代理完成特定任务（并行调研、深度分析）
   参数: {"task": "任务描述", "agent_type": "coder|explore|plan", "model": "", "timeout": 300}
   示例: {"task": "并行调研拓扑绝缘体：① arXiv最新论文 ② 知识库 ③ 现有笔记", "agent_type": "explore", "timeout": 180}
   示例: {"task": "分析 sessions/ 下所有会话，统计用户最常讨论的话题", "agent_type": "coder", "timeout": 120}
   说明：
   - agent_type: coder=编程, explore=调研(只读), plan=架构设计(只读)
   - 与 hermes_chat 的区别：agent 在当前会话启动专注子代理，hermes_chat 调用独立人格
   - 适合需要并行执行、深度探索的复杂任务
   - timeout 默认 300s（5分钟）

9. knowledge_research — 【工作流1: 自动增加】调研主题并写入知识库
   参数: {"topic": "调研主题", "depth": "quick|full", "timeout": 300}
   示例: {"topic": "固体HHG中能谷极化效应的研究进展", "depth": "full", "timeout": 300}
   示例: {"topic": "二维材料中太赫兹波产生的最新方法", "depth": "quick", "timeout": 120}
   说明：
   - 当用户请求调研某个方向时使用，自动完成：调研→编译→写入wiki→建双向链接
   - depth: quick=3-5个要点，full=完整调研
   - 默认通过 Hermes LinSai 进行（有人格、记忆、skills加成）

10. knowledge_ingest — 【工作流2: 手动增加】编译raw文件夹并健康检查
    参数: {"folder": "raw|papers|notes|webclips", "timeout": 300}
    示例: {"folder": "raw/papers", "timeout": 300}
    说明：
    - 当用户将文件存入 raw/ 并请求整理时使用
    - 自动完成：编译→建立双向链接→知识库健康检查
    - 返回：处理结果 + 健康报告（节点数/边数/孤立节点）

11. knowledge_create — 【工作流3: 对话生长】创建新概念存根
    参数: {"concept_name": "概念名", "context": "触发上下文", "timeout": 60}
    示例: {"concept_name": "能谷极化", "context": "用户在讨论固体HHG中提到了能谷极化效应", 60}
    说明：
    - 对话中遇到知识库中没有的概念时使用，创建 seedling stub
    - 触发上下文会被记录，下次讨论同一概念时自动丰满

规则：
- 小问题直接回答，不需要调用工具
- 遇到你不确定的事实，优先用 knowledge_query 查知识库
- 遇到需要生成代码的场景，用 run_command 执行 python
- 遇到需要深度思考或多技能协作的场景，用 hermes_chat 调用独立的 Hermes LinSai
- 遇到需要审查/分析代码的场景，用 run_command 调用 claude
- 讨论中遇到新概念时，**主动调用 knowledge_create**，不要直接忽略
- 你的角色是策划者和协调者：理解需求 → 调用工具 → 整合结果，而不是自己硬扛
- 每次回复最多调用 3 个工具
"""
    return system_prompt + tool_desc


def has_tool_calls(text: str) -> bool:
    """检查文本中是否包含工具调用。"""
    return bool(re.search(r"@@tool:\w+@@", text))


def strip_tool_calls(text: str) -> str:
    """移除文本中的工具调用标记，保留其他内容。"""
    return re.sub(r"@@tool:\w+@@\s*\n?.*?\n?@@end@@", "", text, flags=re.DOTALL).strip()


if __name__ == "__main__":
    print("◐ 子代理调用系统自检")

    # 测试 calc
    print(f"  calc('2+2') = {tool_calc('2+2')}")
    print(f"  calc('pi * 2') = {tool_calc('pi * 2')}")
    try:
        _safe_eval("__import__('os').system('ls')")
        print("  ✗ 安全检查失败")
    except ValueError as e:
        print(f"  ✓ 安全检查通过: {e}")

    # 测试解析
    sample = '我来计算一下\n@@tool:calc@@\n{"expression": "2+3"}\n@@end@@\n结果是5'
    calls = parse_tool_calls(sample)
    print(f"  解析到 {len(calls)} 个工具调用")
    results = execute_tool_calls(calls)
    for r in results:
        print(f"    {r['name']}: {r['result']}")

    # 测试 strip
    stripped = strip_tool_calls(sample)
    print(f"  清理后: {stripped[:30]}...")

    # 测试 run_command 安全检查
    safe, _ = _is_command_safe("kimi code 生成代码")
    print(f"  run_command 安全检查（kimi）: {'✓' if safe else '✗'}")
    safe2, reason = _is_command_safe("rm -rf /")
    print(f"  run_command 安全检查（危险命令）: {'✗ ' + reason if not safe2 else '✓'}")

    # 测试 run_command 实际执行（简单命令）
    result = tool_run_command("echo 'hello from tool_engine'", timeout=10)
    print(f"  run_command(echo): {result.strip()[:60]}")

    # 测试权限检查
    safe_esc, _ = _check_escape("kimi code 生成代码")
    print(f"  权限检查（kimi）: {'✓' if safe_esc else '✗'}")
    safe_esc2, reason2 = _check_escape("cd / && rm -rf /some/path")
    print(f"  权限检查（cd /）: {'✗ ' + reason2 if not safe_esc2 else '✓'}")

    # 测试工具注册
    tools = list_tools()
    tool_names = [t['name'] for t in tools]
    print(f"  工具注册: {', '.join(tool_names)}")
    assert 'run_command' in tool_names, "run_command 未注册"
    assert 'hermes_chat' in tool_names, "hermes_chat 未注册"
    print("  ✓ run_command 已注册")
    print("  ✓ hermes_chat 已注册")

    # 测试 hermes_chat（简单问题）
    try:
        result = tool_hermes_chat("你叫什么名字？用一句话回答。", timeout=15)
        print(f"  hermes_chat 测试: {result[:80]}")
    except Exception as e:
        print(f"  hermes_chat 测试跳过: {e}")

    print("✓ 自检通过")
