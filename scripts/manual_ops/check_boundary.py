#!/usr/bin/env python3
"""研究管线边界违规检测脚本。

检查 12 个管线模块是否违反 AGENTS.md §6 定义的边界规则：
  1. 导入边界：管线模块不导入 CoPilot 核心模块
  2. 写入边界：管线模块的文件写入以 research_proposals/ 为根
  3. API 命名：管线路由使用 /api/pipeline/ 前缀
  4. KB 只读：管线模块不调用 KB 写入函数

用法:
    python3 scripts/check_boundary.py           # 检查全部
    python3 scripts/check_boundary.py --verbose  # 显示详细违规
    python3 scripts/check_boundary.py --json     # JSON 输出
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPTS_DIR.parent

# ── 管线模块清单（14 个 Python + 1 个 JS）──
PIPELINE_PY_MODULES = {
    "artifact_manager", "lineage_tracker", "taste_engine",
    "pipeline_orchestrator", "gap_analyzer", "citation_manager",
    "topic_generator", "question_architect", "proposal_inspector",
    "proposal_writer", "web_routes_pipeline",
    "methodology_manual", "agent_team",
}

# ── 禁止管线模块导入的 CoPilot 核心模块 ──
FORBIDDEN_IMPORTS = {
    "session_manager", "copilot_engine", "context_builder",
    "memory_manager", "proactive_engine", "llm_router",
    "learning_engine", "skill_manager", "slash_commands",
    "tool_engine", "sync_engine", "briefing_sync",
    "agora_bridge", "hermes_bridge",
}

# ── 允许的导入（共享基础设施 + 管线内部 + 只读依赖）──
ALLOWED_IMPORTS = {
    # 共享基础设施
    "common", "paths",
    # 管线内部
    *PIPELINE_PY_MODULES,
    # 只读依赖（有显式注释说明只读用途）
    "kb_index", "kb_wiki", "kb_graph", "kb_text", "kb_health",
    "paper_pool",
    # 标准库
    "os", "sys", "json", "re", "math", "hashlib", "difflib",
    "tempfile", "pathlib", "datetime", "contextlib", "collections",
    "importlib", "typing", "functools", "itertools", "hashlib",
    "textwrap", "io", "base64", "urllib", "http", "socketserver",
    "threading", "queue", "time", "subprocess", "shutil", "glob",
    "abc", "enum", "dataclasses", "string", "operator",
}

# ── KB 写入函数（管线模块禁止调用）──
KB_WRITE_FUNCTIONS = {
    "save_wiki_page", "delete_wiki_page", "create_wiki_stub",
    "update_graph_node", "add_graph_edge", "_remove_graph_node",
    "build_index",  # 重建索引算写入
    "log_growth",   # 生长日志算写入
    "_ensure_dirs",  # 目录初始化算写入
}


def check_imports(file_path: Path) -> list[dict]:
    """检查模块的导入语句是否越界。"""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return [{"file": str(file_path.name), "type": "read_error", "detail": "无法读取文件"}]

    # 匹配 from X import / import X
    for match in re.finditer(r'^\s*(?:from\s+(\w+)\s+import|import\s+(\w+))', content, re.MULTILINE):
        module_name = match.group(1) or match.group(2)
        if not module_name:
            continue

        # 跳过标准库和允许的模块
        if module_name in ALLOWED_IMPORTS:
            continue

        # 检查是否是禁止的核心模块
        if module_name in FORBIDDEN_IMPORTS:
            line_num = content[:match.start()].count('\n') + 1
            violations.append({
                "file": file_path.name,
                "type": "forbidden_import",
                "line": line_num,
                "detail": f"禁止导入 CoPilot 核心模块: {module_name}",
            })

    return violations


def check_writes(file_path: Path) -> list[dict]:
    """检查模块的文件写入路径是否以 research_proposals/ 为根。"""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return []

    # 查找 write_text / save_json / open(.*,"w") 调用
    # 排除临时文件（tempfile）和 _self_check 中的临时目录
    write_patterns = [
        (r'\.write_text\s*\(', "write_text"),
        (r'save_json\s*\(', "save_json"),
        (r'open\s*\([^)]*["\']w', "open_write"),
    ]

    for pattern, write_type in write_patterns:
        for match in re.finditer(pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            # 获取该行上下文
            lines = content.split('\n')
            context = '\n'.join(lines[max(0, line_num-2):line_num+1])

            # 跳过 _self_check 函数中的写入（测试允许临时写入）
            if '_self_check' in context or 'tmp' in context.lower():
                continue

            # 检查路径是否包含 research_proposals 或 proposal_dir
            if 'research_proposals' in context or 'proposal_dir' in context:
                continue

            # 检查是否是临时文件
            if 'tempfile' in context or 'tmp_path' in context or '.tmp' in context:
                continue

            violations.append({
                "file": file_path.name,
                "type": "write_outside_proposal",
                "line": line_num,
                "detail": f"写入操作可能不在 research_proposals/ 下: {write_type}",
                "context": context.strip()[:120],
            })

    return violations


def check_kb_writes(file_path: Path) -> list[dict]:
    """检查管线模块是否调用了 KB 写入函数。"""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return []

    for func_name in KB_WRITE_FUNCTIONS:
        # 查找函数调用（排除注释行）
        for match in re.finditer(rf'(?<!#)\b{re.escape(func_name)}\s*\(', content):
            line_num = content[:match.start()].count('\n') + 1
            line = content.split('\n')[line_num - 1].strip()

            # 跳过注释
            if line.startswith('#'):
                continue

            # 跳过定义（def func_name）
            if f'def {func_name}' in line:
                continue

            violations.append({
                "file": file_path.name,
                "type": "kb_write_call",
                "line": line_num,
                "detail": f"调用了 KB 写入函数: {func_name}()",
            })

    return violations


def check_api_prefix(file_path: Path) -> list[dict]:
    """检查 Web 路由是否使用 /api/pipeline/ 前缀。"""
    violations = []
    if file_path.name != "web_routes_pipeline.py":
        return []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return []

    # 查找路由定义中的路径
    for match in re.finditer(r'["\']/api/(?!pipeline/)(\w+)/', content):
        line_num = content[:match.start()].count('\n') + 1
        path = match.group(0)
        violations.append({
            "file": file_path.name,
            "type": "api_prefix_violation",
            "line": line_num,
            "detail": f"管线路由未使用 /api/pipeline/ 前缀: {path}",
        })

    return violations


def run_check(verbose: bool = False, json_output: bool = False) -> dict:
    """执行全部边界检查。"""
    all_violations = []

    for module_name in PIPELINE_PY_MODULES:
        file_path = _SCRIPTS_DIR / f"{module_name}.py"
        if not file_path.exists():
            all_violations.append({
                "file": f"{module_name}.py",
                "type": "file_missing",
                "detail": "管线模块文件不存在",
            })
            continue

        all_violations.extend(check_imports(file_path))
        all_violations.extend(check_writes(file_path))
        all_violations.extend(check_kb_writes(file_path))
        all_violations.extend(check_api_prefix(file_path))

    # 按严重程度分类
    forbidden = [v for v in all_violations if v["type"] == "forbidden_import"]
    kb_writes = [v for v in all_violations if v["type"] == "kb_write_call"]
    api_prefix = [v for v in all_violations if v["type"] == "api_prefix_violation"]
    write_paths = [v for v in all_violations if v["type"] == "write_outside_proposal"]

    result = {
        "total_violations": len(all_violations),
        "critical": len(forbidden) + len(kb_writes) + len(api_prefix),
        "warning": len(write_paths),
        "details": {
            "forbidden_imports": forbidden,
            "kb_write_calls": kb_writes,
            "api_prefix_violations": api_prefix,
            "write_path_warnings": write_paths,
        },
        "passed": len(forbidden) == 0 and len(kb_writes) == 0 and len(api_prefix) == 0,
    }

    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    # 控制台输出
    print("=" * 60)
    print("研究管线边界违规检测")
    print("=" * 60)
    print()

    if not all_violations:
        print("✓ 未检测到任何边界违规")
        print()
        print(f"  已检查 {len(PIPELINE_PY_MODULES)} 个管线模块")
        print(f"  检查项: 导入边界 / 写入路径 / KB只读 / API前缀")
        return result

    if forbidden:
        print(f"✗ 严重违规 — 禁止导入 CoPilot 核心模块（{len(forbidden)} 处）:")
        for v in forbidden:
            print(f"  {v['file']}:{v['line']} — {v['detail']}")
            if verbose and 'context' in v:
                print(f"    上下文: {v['context']}")
        print()

    if kb_writes:
        print(f"✗ 严重违规 — 调用 KB 写入函数（{len(kb_writes)} 处）:")
        for v in kb_writes:
            print(f"  {v['file']}:{v['line']} — {v['detail']}")
        print()

    if api_prefix:
        print(f"✗ 严重违规 — API 前缀违规（{len(api_prefix)} 处）:")
        for v in api_prefix:
            print(f"  {v['file']}:{v['line']} — {v['detail']}")
        print()

    if write_paths:
        print(f"⚠ 警告 — 写入路径可能越界（{len(write_paths)} 处）:")
        for v in write_paths:
            print(f"  {v['file']}:{v['line']} — {v['detail']}")
            if verbose and 'context' in v:
                print(f"    上下文: {v['context']}")
        print()

    print("-" * 60)
    if result["passed"]:
        print(f"✓ 边界检查通过（{len(write_paths)} 条警告可忽略）")
    else:
        print(f"✗ 边界检查未通过: {result['critical']} 处严重违规")
    print("=" * 60)

    return result


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    json_out = "--json" in sys.argv
    result = run_check(verbose=verbose, json_output=json_out)
    sys.exit(0 if result["passed"] else 1)
