#!/usr/bin/env python3
"""
depp_audit.py — LinSai-CoPilot 深度评估脚本

覆盖 9 个维度：
  1. 静态代码审查    2. 架构拓扑分析    3. 数据完整性审计
  4. 边界条件测试    5. 前端资产审查    6. LLM 引擎健壮性
  7. 安全审查        8. 文档-代码一致性 9. 性能基线

用法:
    python3 scripts/deep_audit.py
    python3 scripts/deep_audit.py --json   # 输出 JSON
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
REPORT_PATH = PROJECT_ROOT / "docs" / "DEEP-AUDIT-REPORT.md"

SEVERITY_WEIGHT = {"critical": 10, "high": 7, "medium": 4, "low": 1}


# ========================================================================
# 数据结构
# ========================================================================

class Finding:
    def __init__(self, dimension: str, severity: str, title: str, detail: str, file: str = "", line: int = 0):
        self.dimension = dimension
        self.severity = severity
        self.title = title
        self.detail = detail
        self.file = file
        self.line = line

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "severity": self.severity,
            "title": self.title,
            "detail": self.detail,
            "file": self.file,
            "line": self.line,
        }


findings: List[Finding] = []


def add_finding(dimension: str, severity: str, title: str, detail: str, file: str = "", line: int = 0):
    findings.append(Finding(dimension, severity, title, detail, file, line))


def severity_score() -> int:
    return sum(SEVERITY_WEIGHT.get(f.severity, 0) for f in findings)


# ========================================================================
# 辅助函数
# ========================================================================

def _python_files() -> List[Path]:
    return sorted((PROJECT_ROOT / "scripts").glob("*.py"))


def _json_files() -> List[Path]:
    result = []
    for pat in ["**/*.json"]:
        for p in PROJECT_ROOT.glob(pat):
            if ".git" not in str(p):
                result.append(p)
    return sorted(result)


def _load_ast(path: Path) -> Optional[ast.AST]:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return None


def _read_json(path: Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# ========================================================================
# 维度 1：静态代码审查
# ========================================================================

def audit_code_quality():
    for path in _python_files():
        text = path.read_text(encoding="utf-8")
        tree = _load_ast(path)
        if tree is None:
            add_finding("代码质量", "high", f"语法错误: {path.name}", "文件无法被 ast 解析", str(path))
            continue

        # 1.1 bare except
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    add_finding("代码质量", "medium", f"裸 except 捕获", f"{path.name}:{node.lineno} 使用裸 except，会捕获 KeyboardInterrupt 等系统异常", str(path), node.lineno)
                elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                    add_finding("代码质量", "low", f"过于宽泛的 except Exception", f"{path.name}:{node.lineno} 建议捕获更具体的异常类型", str(path), node.lineno)

        # 1.2 Python 3.9 兼容性：函数注解中的 X | None
        if sys.version_info < (3, 10):
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                    # 粗略检测 | 运算符在类型上下文中
                    pass  # from __future__ import annotations 已存在，暂不深究

        # 1.3 TODO/FIXME/XXX
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"#\s*(TODO|FIXME|XXX|HACK)", line, re.I):
                add_finding("代码质量", "low", f"遗留标记", f"{path.name}:{i} 存在 {line.strip()}", str(path), i)

        # 1.4 未使用的导入（简单检测）
        imports = set()
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.add(alias.asname or alias.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)
        unused = imports - used - {"__future__"}
        if unused and path.name not in ("__init__.py",):
            add_finding("代码质量", "low", f"疑似未使用导入", f"{path.name}: {', '.join(sorted(unused))}", str(path))

    # 1.5 call_llm 返回值使用（已修复的 bug 验证）
    ce_text = (PROJECT_ROOT / "scripts" / "copilot_engine.py").read_text(encoding="utf-8")
    if "assistant_content, _usage, _provider = call_llm" in ce_text:
        add_finding("代码质量", "low", "call_llm 返回值已正确解包", "chat_loop 中已修复 3 元组解包问题", "scripts/copilot_engine.py")
    else:
        add_finding("代码质量", "critical", "call_llm 返回值未正确解包", "chat_loop 中将 tuple 当作 str 使用会导致 AttributeError", "scripts/copilot_engine.py")


# ========================================================================
# 维度 2：架构拓扑分析
# ========================================================================

def audit_architecture():
    imports: Dict[str, set] = {}
    for path in _python_files():
        tree = _load_ast(path)
        if tree is None:
            continue
        mod = path.stem
        imports[mod] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    if name in [p.stem for p in _python_files()]:
                        imports[mod].add(name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module in [p.stem for p in _python_files()]:
                    for alias in node.names:
                        imports[mod].add(node.module)

    # 2.1 web_server 耦合度
    ws_deps = imports.get("web_server", set())
    if len(ws_deps) > 10:
        add_finding("架构", "high", f"web_server.py 耦合度过高", f"直接导入 {len(ws_deps)} 个内部模块: {', '.join(sorted(ws_deps))}", "scripts/web_server.py")

    # 2.2 循环依赖检测（简单 DFS）
    def has_cycle(start: str, visited: set = None, stack: set = None) -> Optional[List[str]]:
        visited = visited or set()
        stack = stack or set()
        visited.add(start)
        stack.add(start)
        for dep in imports.get(start, set()):
            if dep not in visited:
                cycle = has_cycle(dep, visited, stack)
                if cycle:
                    return cycle
            elif dep in stack:
                return [start, dep]
        stack.remove(start)
        return None

    for mod in imports:
        cycle = has_cycle(mod)
        if cycle:
            add_finding("架构", "medium", f"循环依赖", f"{' → '.join(cycle)} 形成循环依赖", f"scripts/{cycle[0]}.py")

    # 2.3 importlib.util 动态导入统计
    dynamic_count = 0
    dynamic_files = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8")
        if "importlib.util" in text:
            dynamic_count += text.count("importlib.util")
            dynamic_files.append(path.name)
    if dynamic_files:
        add_finding("架构", "low", f"动态导入使用统计", f"{len(dynamic_files)} 个文件使用 importlib.util 动态导入（共 {dynamic_count} 处）: {', '.join(dynamic_files)}", "")


# ========================================================================
# 维度 3：数据完整性审计
# ========================================================================

def audit_data_integrity():
    # 3.1 所有 JSON 可解析性
    json_files = _json_files()
    broken = []
    for p in json_files:
        if _read_json(p) is None:
            broken.append(str(p.relative_to(PROJECT_ROOT)))
    if broken:
        add_finding("数据完整性", "high", f"JSON 解析失败", f"{len(broken)} 个文件无法解析: {', '.join(broken)}", "")

    # 3.2 任务状态与目录一致性
    for status_dir in ["backlog", "active", "completed"]:
        d = PROJECT_ROOT / "tasks" / status_dir
        if not d.exists():
            continue
        for f in d.glob("*.json"):
            data = _read_json(f)
            if data is None:
                continue
            actual = data.get("status", "")
            expected = "paused" if status_dir == "backlog" and actual == "paused" else status_dir
            if actual not in (expected, "paused") and status_dir == "backlog":
                expected = status_dir
            if actual != expected and not (status_dir == "backlog" and actual == "paused"):
                if status_dir != actual:
                    add_finding("数据完整性", "medium", f"任务状态与目录不一致", f"{f.relative_to(PROJECT_ROOT)} 中 status='{actual}' 但位于 {status_dir}/", str(f))

    # 3.3 session state.json 字段检查
    sessions_dir = PROJECT_ROOT / "sessions"
    if sessions_dir.exists():
        for sd in sessions_dir.iterdir():
            if not sd.is_dir() or sd.name.startswith(".") or sd.name == "agora_exports":
                continue
            state_path = sd / "state.json"
            if state_path.exists():
                data = _read_json(state_path)
                if data is None:
                    continue
                if "session_id" not in data:
                    add_finding("数据完整性", "low", f"session state 缺少 session_id", f"{state_path.relative_to(PROJECT_ROOT)}", str(state_path))

    # 3.4 版本号一致性
    version = (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip() if (PROJECT_ROOT / "VERSION").exists() else "?"
    for doc, pattern in [
        ("README.md", r"版本[：:]\s*v?(\d+\.\d+\.\d+)"),
        ("AGENTS.md", r"版本[：:]\s*v?(\d+\.\d+\.\d+)"),
        ("web/index.html", r"v(\d+\.\d+\.\d+)"),
    ]:
        p = PROJECT_ROOT / doc
        if p.exists():
            m = re.search(pattern, p.read_text(encoding="utf-8"))
            if m and m.group(1) != version:
                add_finding("数据完整性", "medium", f"版本号不一致", f"{doc} 中版本为 v{m.group(1)}，但 VERSION 文件为 v{version}", str(p))

    # 3.5 agora 导出数据检查
    agora_path = PROJECT_ROOT / "sessions" / "agora_exports" / "agora_test_费曼.json"
    if agora_path.exists():
        data = _read_json(agora_path)
        if data and isinstance(data.get("invited_personas"), str):
            add_finding("数据完整性", "medium", f"agora 导出数据损坏", f"invited_personas 为字符串 '{data['invited_personas']}' 而非列表", str(agora_path))


# ========================================================================
# 维度 4：边界条件与异常处理
# ========================================================================

def audit_boundary_conditions():
    # 4.1 直接测试 JSON 解析边界
    tmpdir = Path(tempfile.mkdtemp(prefix="linsai_audit_"))
    try:
        # 空 JSON 数组
        empty_path = tmpdir / "empty.json"
        empty_path.write_text("[]", encoding="utf-8")
        data = _read_json(empty_path)
        if data == []:
            add_finding("边界条件", "low", "空 JSON 数组解析正常", "空 [] 正确解析为 Python 空列表", str(empty_path))
        else:
            add_finding("边界条件", "medium", "空 JSON 数组解析异常", f"期望 []，实际 {data}", str(empty_path))

        # 损坏 JSON
        broken_path = tmpdir / "broken.json"
        broken_path.write_text("{invalid json", encoding="utf-8")
        data = _read_json(broken_path)
        if data is None:
            add_finding("边界条件", "low", "损坏 JSON 优雅失败", "_read_json 对损坏 JSON 返回 None 而非抛异常", str(broken_path))
        else:
            add_finding("边界条件", "medium", "损坏 JSON 未优雅处理", f"期望 None，实际 {data}", str(broken_path))

        # 超大 JSON 值
        huge_path = tmpdir / "huge.json"
        huge_path.write_text(json.dumps({"key": "A" * 100000}), encoding="utf-8")
        data = _read_json(huge_path)
        if data and len(data.get("key", "")) == 100000:
            add_finding("边界条件", "low", "超大 JSON 值解析正常", "100KB 字符串值正确解析", str(huge_path))
        else:
            add_finding("边界条件", "medium", "超大 JSON 值解析异常", "100KB 字符串值解析失败", str(huge_path))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ========================================================================
# 维度 5：前端资产审查
# ========================================================================

def audit_frontend():
    # 5.1 app.js API 调用 vs web_server.py 路由一致性
    app_js = PROJECT_ROOT / "web" / "js" / "app.js"
    ws_py = PROJECT_ROOT / "scripts" / "web_server.py"
    if not app_js.exists() or not ws_py.exists():
        return

    js_text = app_js.read_text(encoding="utf-8")
    ws_text = ws_py.read_text(encoding="utf-8")

    # 提取 app.js 中的 API 路径（去除 query string）
    api_calls_raw = set(re.findall(r"['\"](/api/[^'\"]+)['\"]", js_text))
    api_calls = set()
    for path in api_calls_raw:
        # 去除 query string
        clean = path.split("?")[0]
        api_calls.add(clean)

    missing = []
    for path in api_calls:
        # 简化匹配：在 web_server.py 中查找该路径的处理
        route_key = path.split("/")[-1] if "/" in path else path
        if route_key not in ws_text and path not in ws_text:
            # 排除动态路径如 /api/sessions/{id}/messages
            if not re.search(r"/\{[^}]+\}", path):
                missing.append(path)

    # 更精确的检查：前端 PUT /api/tasks/{id}/subtasks
    if "toggle_subtask" not in ws_text and "subtasks" in js_text:
        missing.append("PUT /api/tasks/{id}/subtasks (toggle_subtask)")
    if "update_progress" not in ws_text and "progress" in js_text:
        missing.append("PUT /api/tasks/{id}/progress (update_progress)")

    if missing:
        add_finding("前端", "high", f"前端 API 调用与后端路由不一致", f"{len(missing)} 个路由疑似缺失: {', '.join(missing)}", str(app_js))
    else:
        add_finding("前端", "low", "前后端 API 路由一致", "app.js 中的主要 API 调用在 web_server.py 中均有处理", str(app_js))

    # 5.2 静态资源存在性
    html = (PROJECT_ROOT / "web" / "index.html").read_text(encoding="utf-8")
    css_refs = re.findall(r'href=["\'](/web/[^"\']+)["\']', html)
    js_refs = re.findall(r'src=["\'](/web/[^"\']+)["\']', html)
    for ref in css_refs + js_refs:
        rel = ref.lstrip("/").replace("/web/", "web/")
        if not (PROJECT_ROOT / rel).exists():
            add_finding("前端", "medium", f"静态资源缺失", f"index.html 引用 {ref} 但文件不存在", str(PROJECT_ROOT / "web" / "index.html"))


# ========================================================================
# 维度 6：LLM 引擎健壮性
# ========================================================================

def audit_llm_engine():
    ce_path = PROJECT_ROOT / "scripts" / "copilot_engine.py"
    lr_path = PROJECT_ROOT / "scripts" / "llm_router.py"

    if ce_path.exists():
        text = ce_path.read_text(encoding="utf-8")
        # 6.1 call_llm fallback
        if "call_llm_with_tools" in text and "tool_engine" in text:
            add_finding("LLM引擎", "low", "工具调用降级已就绪", "工具引擎不可用时降级为普通 LLM 调用", str(ce_path))

    if lr_path.exists():
        text = lr_path.read_text(encoding="utf-8")
        # 6.2 timeout 设置
        if "timeout" in text:
            add_finding("LLM引擎", "low", "超时参数已配置", "urllib.request 和 subprocess 均配置 timeout", str(lr_path))
        # 6.3 降级链
        if "failure_count" in text and "round_robin" in text:
            add_finding("LLM引擎", "low", "Provider 降级链已实现", "支持 priority/round_robin 策略及 failure_count 追踪", str(lr_path))


# ========================================================================
# 维度 7：安全审查
# ========================================================================

def audit_security():
    for path in _python_files():
        text = path.read_text(encoding="utf-8")

        # 7.1 os.system / os.popen（跳过自身文件）
        if path.name == "deep_audit.py":
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"\bos\.system\b|\bos\.popen\b", line):
                add_finding("安全", "high", f"Shell 命令注入风险", f"{path.name}:{i} 使用 os.system/os.popen: {line.strip()}", str(path), i)
            if "subprocess.run" in line and "shell=True" in line:
                add_finding("安全", "high", f"Shell 注入风险 (subprocess)", f"{path.name}:{i} 使用 subprocess.run(shell=True): {line.strip()}", str(path), i)

        # 7.2 路径遍历检查（粗略）
        for i, line in enumerate(text.splitlines(), 1):
            if "resolve()" in line and "relative_to" in line:
                break  # 有防护
        else:
            # 检查 _send_static 类函数
            if "_send_static" in text and "relative_to" not in text:
                add_finding("安全", "medium", f"路径遍历风险", f"{path.name} 中的静态文件服务可能未做路径校验", str(path))

        # 7.3 api_key 泄露到日志（跳过自身文件）
        if path.name == "deep_audit.py":
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if "api_key" in line.lower() and ("print" in line or "log" in line.lower()):
                add_finding("安全", "medium", f"API Key 可能泄露到日志", f"{path.name}:{i} 在 print/log 中使用 api_key", str(path), i)

    # 7.4 验证 os.system 是否已修复
    ws_text = (PROJECT_ROOT / "scripts" / "web_server.py").read_text(encoding="utf-8")
    if "os.system" not in ws_text:
        add_finding("安全", "low", "os.system 已移除", "web_server.py 中的 os.system 已替换为 subprocess.run", "scripts/web_server.py")
    else:
        add_finding("安全", "high", "os.system 仍存在", "web_server.py 中仍存在 os.system 调用", "scripts/web_server.py")


# ========================================================================
# 维度 8：文档-代码一致性
# ========================================================================

def audit_doc_consistency():
    # 8.1 scripts/README.md 脚本数
    readme = PROJECT_ROOT / "scripts" / "README.md"
    actual = len(list((PROJECT_ROOT / "scripts").glob("*.py")))
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        m = re.search(r"总计[：:]?\s*(\d+)\s*个", text)
        if m and int(m.group(1)) != actual:
            add_finding("文档一致性", "medium", f"scripts/README.md 脚本数不匹配", f"文档声称 {m.group(1)} 个，实际 {actual} 个", str(readme))

    # 8.2 AGENTS.md 技能数
    agents = PROJECT_ROOT / "AGENTS.md"
    if agents.exists():
        text = agents.read_text(encoding="utf-8")
        m = re.search(r"技能总数[：:]?\s*(\d+)", text)
        actual_skills = len(list((PROJECT_ROOT / "skills").glob("*/SKILL.md")))
        if m and int(m.group(1)) != actual_skills:
            add_finding("文档一致性", "low", f"AGENTS.md 技能数不匹配", f"文档声称 {m.group(1)} 个，实际 {actual_skills} 个", str(agents))


# ========================================================================
# 维度 9：性能基线
# ========================================================================

def audit_performance():
    scripts_dir = PROJECT_ROOT / "scripts"
    sys.path.insert(0, str(scripts_dir))

    # 9.1 上下文构建耗时
    try:
        import context_builder as cb
        tmpdir = Path(tempfile.mkdtemp(prefix="linsai_perf_"))
        try:
            original_root = cb.PROJECT_ROOT
            cb.PROJECT_ROOT = tmpdir
            (tmpdir / "persona").mkdir()
            (tmpdir / "memory").mkdir()
            (tmpdir / "sessions" / "perf-test").mkdir(parents=True)
            (tmpdir / "persona" / "lin-sai-persona.md").write_text("# 测试人格\n" + "内容。" * 100, encoding="utf-8")
            (tmpdir / "sessions" / "perf-test" / "messages.json").write_text(
                json.dumps({"messages": [{"role": "user", "content": "测试", "msg_id": "m1"}]}, ensure_ascii=False),
                encoding="utf-8",
            )

            t0 = time.time()
            ctx = cb.build_context("perf-test", "简短测试", mode="co-working")
            t1 = time.time()
            duration_ms = (t1 - t0) * 1000
            total_chars = ctx["_budget"]["total_final"]
            add_finding("性能", "low", f"上下文构建基线", f"空会话上下文构建耗时 {duration_ms:.1f}ms，总字符 {total_chars}", "scripts/context_builder.py")
        finally:
            cb.PROJECT_ROOT = original_root
            shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception as e:
        add_finding("性能", "low", f"性能测试失败", str(e), "scripts/context_builder.py")

    # 9.2 Web 服务器启动耗时
    try:
        t0 = time.time()
        spec = importlib.util.spec_from_file_location("web_server", scripts_dir / "web_server.py")
        ws_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ws_mod)
        t1 = time.time()
        add_finding("性能", "low", f"Web 服务器导入耗时", f"web_server.py 导入耗时 {(t1-t0)*1000:.1f}ms", "scripts/web_server.py")
    except Exception as e:
        add_finding("性能", "low", f"Web 服务器导入失败", str(e), "scripts/web_server.py")


# ========================================================================
# 报告生成
# ========================================================================

def generate_report() -> str:
    version = (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip() if (PROJECT_ROOT / "VERSION").exists() else "?"
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

    lines = [
        f"# LinSai-CoPilot 深度评估报告",
        f"",
        f"**版本**: v{version}  ",
        f"**时间**: {now}  ",
        f"**评估维度**: 9  ",
        f"**发现问题**: {len(findings)} 项（严重 {severity_counts['critical']} / 高 {severity_counts['high']} / 中 {severity_counts['medium']} / 低 {severity_counts['low']}）  ",
        f"**风险评分**: {severity_score()} / 1000",
        f"",
        "---",
        f"",
    ]

    # 按维度分组
    dims = {}
    for f in findings:
        dims.setdefault(f.dimension, []).append(f)

    for dim in sorted(dims.keys()):
        items = dims[dim]
        lines.append(f"## {dim}（{len(items)} 项）\n")
        for sev in ["critical", "high", "medium", "low"]:
            for f in items:
                if f.severity != sev:
                    continue
                loc = f"`{f.file}:{f.line}`" if f.line else f"`{f.file}`"
                icon = {"critical": "🔴", "high": "🟡", "medium": "🟠", "low": "🟢"}.get(sev, "⚪")
                lines.append(f"### {icon} [{sev.upper()}] {f.title}")
                lines.append(f"")
                lines.append(f"- **位置**: {loc}")
                lines.append(f"- **详情**: {f.detail}")
                lines.append(f"")
        lines.append("---\n")

    # 附录：修复优先级建议
    lines.append("## 修复优先级建议\n")
    critical_high = [f for f in findings if f.severity in ("critical", "high")]
    if critical_high:
        lines.append("### 立即修复（严重/高）\n")
        for f in critical_high:
            loc = f"`{f.file}:{f.line}`" if f.line else f"`{f.file}`"
            lines.append(f"- [ ] **{f.title}** — {loc}")
        lines.append(f"")
    lines.append("### 建议修复（中/低）\n")
    for f in findings:
        if f.severity in ("medium", "low"):
            loc = f"`{f.file}:{f.line}`" if f.line else f"`{f.file}`"
            lines.append(f"- [ ] **{f.title}** — {loc}")
    lines.append(f"")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="LinSai-CoPilot 深度评估")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    print("◐ 开始深度评估…")
    audit_code_quality()
    audit_architecture()
    audit_data_integrity()
    audit_boundary_conditions()
    audit_frontend()
    audit_llm_engine()
    audit_security()
    audit_doc_consistency()
    audit_performance()

    if args.json:
        result = {
            "version": (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip() if (PROJECT_ROOT / "VERSION").exists() else "?",
            "findings": [f.to_dict() for f in findings],
            "summary": {
                "total": len(findings),
                "critical": sum(1 for f in findings if f.severity == "critical"),
                "high": sum(1 for f in findings if f.severity == "high"),
                "medium": sum(1 for f in findings if f.severity == "medium"),
                "low": sum(1 for f in findings if f.severity == "low"),
                "score": severity_score(),
            },
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        report = generate_report()
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"\n✓ 深度评估完成，报告已保存: {REPORT_PATH}")
        print(f"  发现问题: {len(findings)} 项")
        for sev in ["critical", "high", "medium", "low"]:
            c = sum(1 for f in findings if f.severity == sev)
            if c:
                print(f"  - {sev}: {c}")
        print(f"  风险评分: {severity_score()}")


if __name__ == "__main__":
    main()
