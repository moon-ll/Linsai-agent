#!/usr/bin/env python3
"""子代理调用系统 — 林赛的工具执行引擎。

用途：
    解析 LLM 输出中的工具调用指令，安全执行，返回结果。
    支持文件读写、数值计算、任务创建、知识库查询。

用法示例：
    >>> from tool_engine import parse_tool_calls, execute_tool_calls, inject_tools_prompt
    >>> text = "@@tool:calc\\n{\\"expression\\": \\"2+2\\"}\\n@@end@@"
    >>> calls = parse_tool_calls(text)
    >>> results = execute_tool_calls(calls)

规范：
    - 仅使用 Python 3 标准库
    - 所有文件操作有严格路径白名单
    - calc 使用 ast.parse 白名单，禁止系统调用
"""

import ast
import json
import os
import re
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


# ---------------------------------------------------------------------------
# 工具注册表
# ---------------------------------------------------------------------------

_TOOL_REGISTRY: Dict[str, tuple] = {
    "file_read": (tool_file_read, ["path"]),
    "file_write": (tool_file_write, ["path", "content"]),
    "calc": (tool_calc, ["expression"]),
    "task_create": (tool_task_create, ["title", "due_date", "priority", "description"]),
    "knowledge_query": (tool_knowledge_query, ["query"]),
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
你可以在回复中使用以下工具来协助完成任务。当需要时，按以下格式输出工具调用：

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

规则：
- 小问题直接回答，不需要调用工具
- 复杂问题先分解，再决定是否需要工具辅助
- 数值计算优先使用 calc，不要心算
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

    print("✓ 自检通过")
