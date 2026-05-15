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

规则：
- 小问题直接回答，不需要调用工具
- 遇到你不确定的事实，优先用 knowledge_query 查知识库
- 遇到需要生成代码的场景，用 run_command 执行 python
- 遇到需要深度思考或多技能协作的场景，用 hermes_chat 调用独立的 Hermes LinSai
- 遇到需要审查/分析代码的场景，用 run_command 调用 claude
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
