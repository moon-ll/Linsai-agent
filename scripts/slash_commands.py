#!/usr/bin/env python3
"""斜杠命令系统 —— LinSai-CoPilot 的统一命令入口。

用法：
    在 chat_loop 中，收到用户输入后，先检查是否以 "/" 开头。
    如果是，交给 slash_dispatch() 处理。

    from slash_commands import slash_dispatch
    result = slash_dispatch(user_input, session_id)
    if result is not None:
        print(result)  # 命令已处理
        continue       # 不走 LLM

命令格式：
    /<command> [args...]          — 斜杠命令
    /<command>:<arg1>:<arg2>     — 冒号分隔参数
    /<command> <arg1> <arg2>     — 空格分隔参数

命令列表（可用 /help 或 /list 查看）：

  /research <topic> [depth]    调研主题并写入知识库（knowledge_research）
  /ingest [folder]             编译 raw 文件夹（knowledge_ingest）
  /check                       知识库健康检查
  /skill [name]                列出或激活思维视角（skill）
  /skill:perspective           列出所有可用视角
  /mode <mode>                 切换交互模式（co-working|deep-talk|quick-check）
  /read <file>                 读取项目内文件
  /session                     列出所有会话
  /help                        显示此帮助
  /list                        以列表格式显示所有命令

版本：v1.0
"""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent


# ─────────────────────────────────────────────
# 命令处理器类型
# ─────────────────────────────────────────────

# ActionHandler: 执行 Python 代码，返回字符串输出（打印到终端）
ActionHandler = Callable[["ParsedCommand", str], Optional[str]]
# SkillHandler: 激活思维视角，返回 skill prompt 片段供注入
SkillHandler = Callable[["ParsedCommand", str], Optional[str]]


class ParsedCommand:
    """解析后的命令对象。"""
    def __init__(self, raw: str, cmd: str, args: List[str], rest: str):
        self.raw = raw
        self.cmd = cmd          # 命令名（如 "research", "ingest"）
        self.args = args        # 解析后的参数列表
        self.rest = rest       # 原始参数字符串


# ─────────────────────────────────────────────
# Skills 加载器
# ─────────────────────────────────────────────

def _load_project_skills() -> List[Dict[str, str]]:
    """从 ~/.claude/skills/ 加载所有 perspective skills。"""
    skill_dir = Path.home() / ".claude" / "skills"
    if not skill_dir.exists():
        return []
    skills = []
    for d in sorted(skill_dir.iterdir()):
        if not d.is_dir():
            continue
        skill_file = d / "SKILL.md"
        if not skill_file.exists():
            continue
        try:
            text = skill_file.read_text(encoding="utf-8")
            lines = text.strip().split("\n")
            name = d.name.replace("-", " ").replace("_", " ")

            # 尝试从 YAML frontmatter 中提取 description
            desc = ""
            if lines and lines[0].strip() == "---":
                # 在 frontmatter 中找 description 字段
                fm_end = 1
                for i in range(1, min(len(lines), 50)):
                    if lines[i].strip() == "---":
                        fm_end = i
                        break
                fm_block = "\n".join(lines[1:fm_end])
                m = re.search(r'description:\s*\|?\s*\n?([^\n]+(?:\n[^\n]+)*)', fm_block)
                if m:
                    desc = m.group(1).strip().replace("\n", " ")

            # 如果 frontmatter 中没有，扫描正文找第一段非标题内容
            if not desc:
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("---"):
                        desc = line
                        break

            desc = desc[:120] + "..." if len(desc) > 120 else desc
            if not desc:
                desc = f"思维视角：{name}"
            skills.append({
                "name": name,
                "dir": d.name,
                "description": desc,
                "path": str(skill_file),
            })
        except Exception:
            continue
    return skills


# ─────────────────────────────────────────────
# Skill 处理器
# ─────────────────────────────────────────────

def _load_skill_prompt(skill_dir_name: str) -> Optional[str]:
    """加载指定 skill 的完整 prompt。"""
    skill_file = Path.home() / ".claude" / "skills" / skill_dir_name / "SKILL.md"
    if not skill_file.exists():
        return None
    try:
        return skill_file.read_text(encoding="utf-8")
    except Exception:
        return None


# ─────────────────────────────────────────────
# 知识库命令处理器（复用 tool_engine 的实现）
# ─────────────────────────────────────────────

def _ensure_kb_module():
    """延迟加载 knowledge_base 模块。"""
    kb_path = PROJECT_ROOT / "scripts" / "knowledge_base.py"
    spec = importlib.util.spec_from_file_location("knowledge_base", str(kb_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ensure_tool_module():
    """延迟加载 tool_engine 模块。"""
    te_path = PROJECT_ROOT / "scripts" / "tool_engine.py"
    spec = importlib.util.spec_from_file_location("tool_engine", str(te_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─────────────────────────────────────────────
# 命令处理器
# ─────────────────────────────────────────────

def _handle_research(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """处理 /research <topic> [depth]"""
    topic = " ".join(pc.args) if pc.args else ""
    if not topic:
        return "✗ 缺少参数：/research <主题> [quick|full]\n  示例：/research 拓扑绝缘体表面态 full"

    depth = "full"
    if pc.args and pc.args[-1] in ("quick", "full"):
        depth = pc.args[-1]
        topic = " ".join(pc.args[:-1])

    te = _ensure_tool_module()
    result = te.tool_knowledge_research(topic, depth, timeout=300)
    return f"\n{result}\n"


def _handle_ingest(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """处理 /ingest [folder]"""
    folder = pc.args[0] if pc.args else "raw"
    te = _ensure_tool_module()
    result = te.tool_knowledge_ingest(folder, timeout=300)
    return f"\n{result}\n"


def _handle_check(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """处理 /check —— 知识库健康检查。"""
    kb = _ensure_kb_module()
    graph = kb.get_graph_summary()
    orphaned = []
    for node_id, node in kb._load_graph()["nodes"].items():
        path = node.get("path", "")
        if path and not (PROJECT_ROOT / "knowledge" / path).exists():
            orphaned.append(node_id)

    index_doc_count = 0
    idx_path = PROJECT_ROOT / "knowledge" / "index.json"
    if idx_path.exists():
        try:
            index_doc_count = len(json.loads(idx_path.read_text(encoding="utf-8")).get("documents", {}))
        except Exception:
            pass

    growth_entries = []
    gl_path = PROJECT_ROOT / "knowledge" / "growth-log.json"
    if gl_path.exists():
        try:
            growth_entries = json.loads(gl_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    raw_files = []
    raw_dir = PROJECT_ROOT / "knowledge" / "raw"
    if raw_dir.exists():
        for f in raw_dir.rglob("*"):
            if f.is_file() and not any(p.startswith(".") for p in f.parts):
                raw_files.append(str(f.relative_to(raw_dir)))

    wiki_pages = []
    wiki_dir = PROJECT_ROOT / "knowledge" / "wiki"
    if wiki_dir.exists():
        for f in wiki_dir.rglob("*.md"):
            if not any(p.startswith(".") for p in f.parts):
                wiki_pages.append(str(f.relative_to(wiki_dir)))

    lines = [
        "",
        "【知识库健康检查】",
        f"  图谱节点: {graph['node_count']}",
        f"  图谱边数: {graph['edge_count']}",
        f"  索引文档: {index_doc_count}",
        f"  wiki 页面: {len(wiki_pages)}",
        f"  raw 文件: {len(raw_files)}",
        f"  孤立节点: {len(orphaned)} 个  {'✓ 无' if not orphaned else '⚠ ' + ', '.join(orphaned[:3])}",
        f"  生长日志: {len(growth_entries)} 条",
    ]
    if orphaned:
        lines.append(f"  建议：运行 /ingest 将孤立节点接入，或手动清理")
    lines.append("")
    return "\n".join(lines)


def _handle_skill(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """处理 /skill [name] 和 /skill:xxx"""
    # /skill 或 /skill list — 列出所有 skills
    if not pc.args or pc.args[0] in ("list", "ls"):
        skills = _load_project_skills()
        if not skills:
            return "\n○ 暂无可用的 perspective skills\n"
        lines = ["", "【可用思维视角 (Perspective Skills)】", ""]
        for s in skills:
            lines.append(f"  /skill:{s['dir']}")
            lines.append(f"    {s['description']}")
            lines.append("")
        lines.append("  用法：/skill:<name>  激活该视角进行讨论")
        lines.append("        /skill        列出所有视角")
        lines.append("")
        return "\n".join(lines)

    # /skill:xxx — 查找并激活 skill
    skill_name = pc.args[0]
    skills = _load_project_skills()
    matched = None
    for s in skills:
        # 支持前缀匹配
        if s["dir"].startswith(skill_name) or skill_name in s["dir"]:
            if matched is None:
                matched = s
            else:
                # 多于一个匹配，提示歧义
                return (f"\n⚠ 多个匹配的 skill，请明确选择：\n"
                        f"  /skill:{matched['dir']}  — {matched['description'][:60]}\n"
                        f"  /skill:{s['dir']}  — {s['description'][:60]}\n")

    if matched is None:
        return f"\n✗ 未找到 skill: {skill_name}\n  运行 /skill 列出所有可用视角\n"

    # 激活 skill
    prompt = _load_skill_prompt(matched["dir"])
    if not prompt:
        return f"\n✗ 无法加载 skill: {matched['dir']}\n"

    # 将 skill prompt 注入到 session state
    _inject_skill_to_session(session_id, matched["dir"], matched["name"], prompt)
    return (f"\n✓ 已激活思维视角：{matched['name']}\n"
            f"  本次会话将使用该视角进行讨论\n"
            f"  使用 /skill:{matched['dir']} 再次确认当前视角\n")


def _inject_skill_to_session(session_id: str, skill_dir: str, skill_name: str, prompt: str):
    """将激活的 skill 注入到 session state。"""
    state_path = PROJECT_ROOT / "sessions" / session_id / "state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    state["active_skill"] = {
        "name": skill_name,
        "dir": skill_dir,
        "prompt": prompt[:500],  # 只存前500字，避免 state.json 过大
    }
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _handle_mode(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """处理 /mode <mode>"""
    valid_modes = {"co-working", "deep-talk", "quick-check", "proactive"}
    m = pc.args[0] if pc.args else ""
    if m not in valid_modes:
        return (f"\n✗ 无效模式: {m}\n"
                f"  可用模式: {', '.join(sorted(valid_modes))}\n"
                f"  示例：/mode co-working\n")
    state_path = PROJECT_ROOT / "sessions" / session_id / "state.json"
    state = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    state["mode"] = m
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"\n✓ 模式已切换为: {m}\n"


def _handle_read(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """处理 /read <file>"""
    if not pc.args:
        return "\n✗ 缺少参数：/read <文件路径>\n  示例：/read persona/lin-sai-persona.md\n"
    path_str = pc.args[0]
    file_path = PROJECT_ROOT / path_str
    # 防止路径穿越
    try:
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(PROJECT_ROOT)):
            return f"\n✗ 路径越界（仅限项目目录内）\n"
    except Exception:
        return f"\n✗ 路径无效\n"
    if not file_path.exists():
        return f"\n✗ 文件不存在: {path_str}\n"
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        preview = "\n".join(lines[:100])
        if len(lines) > 100:
            preview += f"\n...（共 {len(lines)} 行）"
        return f"\n【{path_str}】\n{preview}\n"
    except Exception as e:
        return f"\n✗ 读取失败: {e}\n"


def _handle_summary(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """处理 /summary —— 显示当前会话摘要。"""
    try:
        msgs, st = load_session(session_id)
        duration = "未知"
        try:
            started = datetime.fromisoformat(
                st.get("started_at", "").replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)
            delta = now - started
            duration = f"{int(delta.total_seconds() // 60)} 分钟"
        except Exception:
            pass
        active_skill = None
        try:
            active_skill = inject_active_skill_prompt("", session_id)
        except Exception:
            pass
        skill_info = ""
        if active_skill and len(active_skill.strip()) > 10:
            # 提取 skill name
            import re
            m = re.search(r"【激活视角】([^\n]+)", active_skill)
            skill_info = f"\n  激活视角: {m.group(1) if m else '未知'}" if m else ""
        lines = [
            "",
            "【会话摘要】",
            f"  主题: {st.get('topic', '')}",
            f"  模式: {st.get('mode', '')}",
            f"  消息数: {len(msgs)}",
            f"  已进行: {duration}",
            f"  会话ID: {session_id}",
            skill_info,
            "",
        ]
        return "\n".join(lines)
    except Exception as exc:
        return f"\n✗ 获取摘要失败: {exc}\n"


def _handle_session(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """处理 /session —— 列出所有会话。"""
    sessions_dir = PROJECT_ROOT / "sessions"
    if not sessions_dir.exists():
        return "\n○ 无会话记录\n"
    sessions = sorted([d for d in sessions_dir.iterdir() if d.is_dir() and not d.name.startswith(".")],
                      key=lambda d: d.stat().st_mtime, reverse=True)
    if not sessions:
        return "\n○ 无会话记录\n"
    lines = ["", "【会话列表】", ""]
    for d in sessions[:20]:
        is_current = "(当前)" if d.name == session_id else ""
        state_file = d / "state.json"
        topic = ""
        if state_file.exists():
            try:
                topic = json.loads(state_file.read_text(encoding="utf-8")).get("topic", "")
            except Exception:
                pass
        msg_file = d / "messages.json"
        msg_count = 0
        if msg_file.exists():
            try:
                msgs = json.loads(msg_file.read_text(encoding="utf-8"))
                if isinstance(msgs, list):
                    msg_count = len(msgs)
                else:
                    msg_count = len(msgs.get("messages", []))
            except Exception:
                pass
        lines.append(f"  {d.name}  {is_current}")
        if topic:
            lines.append(f"    主题: {topic}")
        lines.append(f"    消息: {msg_count} 条")
        lines.append("")
    return "\n".join(lines) + "\n"


# ─────────────────────────────────────────────
# 命令注册表
# ─────────────────────────────────────────────

_COMMAND_REGISTRY: Dict[str, Dict[str, Any]] = {
    "help": {
        "description": "显示帮助信息",
        "usage": "/help",
        "aliases": ["?"],
        "handler": lambda pc, sid: _cmd_help(pc, sid),
    },
    "list": {
        "description": "列出所有斜杠命令",
        "usage": "/list",
        "aliases": [],
        "handler": lambda pc, sid: _cmd_list(pc, sid),
    },
    "research": {
        "description": "调研主题并写入知识库",
        "usage": "/research <主题> [quick|full]",
        "aliases": ["调研", "研究"],
        "handler": _handle_research,
    },
    "ingest": {
        "description": "编译 raw 文件夹并健康检查",
        "usage": "/ingest [folder]",
        "aliases": ["整理", "编译"],
        "handler": _handle_ingest,
    },
    "check": {
        "description": "知识库健康检查",
        "usage": "/check",
        "aliases": ["健康", "检查"],
        "handler": _handle_check,
    },
    "skill": {
        "description": "列出或激活思维视角",
        "usage": "/skill [name] 或 /skill:<视角名>",
        "aliases": [],
        "handler": _handle_skill,
    },
    "mode": {
        "description": "切换交互模式",
        "usage": "/mode <co-working|deep-talk|quick-check|proactive>",
        "aliases": [],
        "handler": _handle_mode,
    },
    "read": {
        "description": "读取项目内文件",
        "usage": "/read <文件路径>",
        "aliases": ["cat", "查看"],
        "handler": _handle_read,
    },
    "session": {
        "description": "列出所有会话",
        "usage": "/session",
        "aliases": ["sessions"],
        "handler": _handle_session,
    },
}


def _cmd_help(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """显示帮助。"""
    lines = [
        "",
        "【LinSai 斜杠命令】",
        "",
        "  /research <主题> [quick|full]  调研主题并写入知识库",
        "  /ingest [folder]               编译 raw 文件夹并健康检查",
        "  /check                         知识库健康检查",
        "  /skill [name]                  列出或激活思维视角",
        "  /mode <mode>                   切换交互模式",
        "  /read <文件>                   读取项目内文件",
        "  /session                       列出所有会话",
        "  /list                          以列表格式显示所有命令",
        "  /help                          显示此帮助",
        "",
        "  使用 /skill  查看所有可用思维视角",
        "  示例：/research 拓扑绝缘体 full",
        "  示例：/ingest raw/papers",
        "  示例：/skill:bragg-perspective",
        "",
    ]
    return "\n".join(lines)


def _cmd_list(pc: ParsedCommand, session_id: str) -> Optional[str]:
    """以 Claude Code 风格列出所有命令。"""
    lines = ["", "【LinSai Commands】", ""]
    for cmd, info in sorted(_COMMAND_REGISTRY.items()):
        desc = info["description"]
        usage = info["usage"].replace(f"/{cmd} ", f"/{cmd} ")
        lines.append(f"  /{cmd:<12} {usage}")
        lines.append(f"  {desc}")
        lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# 核心解析与分发
# ─────────────────────────────────────────────

def parse_slash_command(raw: str) -> Optional[ParsedCommand]:
    """解析斜杠命令字符串。

    格式支持：
        /research 拓扑绝缘体 full
        /research:拓扑绝缘体:full
        /ingest raw/papers
        /skill
        /skill:bragg-perspective

    Returns:
        ParsedCommand 对象，或 None（不是斜杠命令）
    """
    raw = raw.strip()
    if not raw.startswith("/"):
        return None

    # 去掉开头的 /
    body = raw[1:]

    # 优先按冒号分割（/research:topic:depth 格式）
    if ":" in body:
        parts = body.split(":")
        cmd = parts[0].strip()
        args = [p.strip() for p in parts[1:] if p.strip()]
        rest = ":".join(parts[1:])
    else:
        # 按空格分割
        parts = body.split(None, 1)
        cmd = parts[0].strip()
        args = parts[1].strip().split() if len(parts) > 1 else []
        rest = " ".join(args)

    return ParsedCommand(raw=raw, cmd=cmd.lower(), args=args, rest=rest)


def _resolve_alias(cmd: str) -> str:
    """解析命令别名。"""
    for name, info in _COMMAND_REGISTRY.items():
        if cmd == name:
            return name
        if cmd in info.get("aliases", []):
            return name
    return cmd


def slash_dispatch(raw: str, session_id: str) -> Optional[str]:
    """将斜杠命令分发给对应处理器。

    Args:
        raw: 用户原始输入（以 "/" 开头）
        session_id: 当前会话 ID

    Returns:
        处理结果字符串，或 None（不是有效命令）
        返回 None 时，调用方应将此输入交给 LLM 处理
    """
    pc = parse_slash_command(raw)
    if pc is None:
        return None  # 不是斜杠命令，交给 LLM

    # 解析别名
    resolved = _resolve_alias(pc.cmd)
    if resolved not in _COMMAND_REGISTRY:
        # 未知命令，尝试 /skill:xxx 风格的 skill 激活
        # 如果命令以 skill: 开头但被当作命令名处理
        if pc.cmd.startswith("skill:"):
            pc.args = [pc.cmd[6:]] + pc.args
            pc.cmd = "skill"
            resolved = "skill"
        else:
            return (f"\n✗ 未知命令: /{pc.cmd}\n"
                    f"  运行 /list 或 /help 查看所有命令\n")

    handler = _COMMAND_REGISTRY[resolved]["handler"]
    try:
        result = handler(pc, session_id)
        return result
    except Exception as e:
        return f"\n✗ 命令执行失败: /{pc.cmd}\n  错误: {e}\n"


# ─────────────────────────────────────────────
# 供 context_builder 调用的接口
# ─────────────────────────────────────────────

def get_active_skill(session_id: str) -> Optional[Dict[str, str]]:
    """获取当前会话激活的 skill。"""
    state_path = PROJECT_ROOT / "sessions" / session_id / "state.json"
    if not state_path.exists():
        return None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        return state.get("active_skill")
    except Exception:
        return None


def inject_active_skill_prompt(system_prompt: str, session_id: str) -> str:
    """如果当前会话激活了 skill，将其注入 system_prompt。"""
    skill = get_active_skill(session_id)
    if not skill:
        return system_prompt
    prompt = skill.get("prompt", "")
    if not prompt:
        return system_prompt
    return system_prompt + f"\n\n---\n【激活视角】{skill['name']}\n{prompt[:800]}\n---"


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("◐ 斜杠命令系统自检")
    print()

    # 测试解析
    test_cases = [
        "/research 拓扑绝缘体",
        "/research:拓扑绝缘体:quick",
        "/ingest raw/papers",
        "/check",
        "/skill",
        "/skill:bragg",
        "/help",
        "/list",
        "/mode co-working",
        "/read VERSION",
        "/session",
    ]

    for raw in test_cases:
        pc = parse_slash_command(raw)
        if pc:
            print(f"  ✓ {raw:<40} → cmd={pc.cmd}, args={pc.args}")
        else:
            print(f"  ✗ {raw:<40} → 未能解析")

    print()
    print("  /list 输出示例：")
    print(slash_dispatch("/list", "test-session")[:500])

    print()
    print("  /skill 输出示例：")
    print(slash_dispatch("/skill", "test-session")[:500])

    print()
    print("✓ 自检通过")
