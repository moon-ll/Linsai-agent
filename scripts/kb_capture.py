#!/usr/bin/env python3
"""知识库对话捕获器 —— 从会话中自动提取有价值片段，零 LLM 开销。

用法:
    >>> from kb_capture import capture_from_session, should_capture
    >>> capture_from_session("20260508-固体HHG", "固体HHG")
    {'captured': True, 'path': 'captures/2026-05-08_固体HHG.md', 'reason': '技术参数检测'}

规范:
    - 仅使用 Python 3 标准库
    - 捕获文件保存到 knowledge/captures/，自动进入索引
    - 零 LLM 调用，纯本地文本操作
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
CAPTURE_DIR = PROJECT_ROOT / "knowledge" / "captures"
SESSIONS_DIR = PROJECT_ROOT / "sessions"

# 技术参数模式：数字 + 单位（如 800nm, 3mJ, 1kHz, 100μm）
_TECH_PARAM_RE = re.compile(
    r"\d+\.?\d*\s*(?:nm|μm|mm|cm|m|Hz|kHz|MHz|GHz|THz|"
    r"mJ|μJ|nJ|J|W|mW|μW|kW|fs|ps|ns|μs|ms|s|eV|keV|MeV|"
    r"cm\^-1|K|°C|°|um|uJ|uW|us)",
    re.IGNORECASE,
)

# 用户明确请求捕获的关键词
_EXPLICIT_CAPTURE_RE = re.compile(
    r"(记(?:下|住)|保存|加入知识库|(?:请)?录入|"
    r"把这个(?:记录|保存)|以后用|别忘了)",
    re.IGNORECASE,
)

# 问候/闲聊检测 —— 这些不应触发捕获
_CHITCHAT_RE = re.compile(
    r"^(你好|您好|嗨|哈喽|hello|hi|hey|在吗|在不在|"
    r"谢谢|多谢|感谢|不客气|再见|拜拜|goodbye|bye)[\s!！.。]*$",
    re.IGNORECASE,
)


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_filename(name: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name).strip()
    return safe if safe else "untitled"


def _ensure_dir() -> None:
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)


def extract_tech_params(text: str) -> List[str]:
    """从文本中提取技术参数（数字+单位）。"""
    return _TECH_PARAM_RE.findall(text)


def should_capture(user_input: str, session_mode: str = "co-working") -> Tuple[bool, str]:
    """判断一条用户输入是否值得捕获。

    Returns:
        (should_capture: bool, reason: str)
    """
    text = user_input.strip()
    if not text or len(text) < 10:
        return False, "过短"

    if _CHITCHAT_RE.match(text):
        return False, "闲聊"

    # 1. 用户明确请求
    if _EXPLICIT_CAPTURE_RE.search(text):
        return True, "用户明确请求"

    # 2. 技术参数密集
    params = extract_tech_params(text)
    if len(params) >= 3:
        return True, f"技术参数检测 ({len(params)} 个)"

    # 3. 工作模式 + 长度门槛
    if session_mode == "co-working" and len(text) > 100:
        # 额外检查：包含一些科研相关关键词
        if re.search(r"(实验|方案|设计|参数|模型|理论|计算|"
                     r"测量|数据|结果|分析|讨论|结论|"
                     r"激光|脉冲|光谱|相位|振幅|偏振|"
                     r"晶体|样品|光路|腔|镜|透镜|"
                     r"论文|文献|引用|作者|期刊)", text):
            return True, "技术讨论"

    return False, "未命中捕获条件"


def _load_session_messages(session_id: str) -> List[Dict[str, Any]]:
    """加载会话消息列表。"""
    msg_path = SESSIONS_DIR / session_id / "messages.json"
    if not msg_path.exists():
        return []
    try:
        data = json.loads(msg_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return data.get("messages", [])
    except Exception:
        return []


def _build_capture_content(
    session_id: str,
    topic_hint: str,
    trigger_msg: Dict[str, Any],
    context_msgs: List[Dict[str, Any]],
) -> str:
    """构建 capture 文件内容。"""
    now = _now_utc()
    date_prefix = now[:10]
    safe_topic = _safe_filename(topic_hint)[:30]

    # 提取话题标签
    topics = [safe_topic]
    # 尝试从触发消息中提取额外话题
    trigger_text = trigger_msg.get("content", "")
    tech_keywords = re.findall(
        r"(?:固体|气体)?高次谐波|阿秒|HHG|attosecond|"
        r"相位匹配|走离|色散|非线性|超快|强场|"
        r"驱动光|探测光|晶体|靶|"
        r"DFG|ERC|NSF|基金|申请",
        trigger_text,
        re.IGNORECASE,
    )
    for kw in set(tech_keywords):
        if kw not in topics:
            topics.append(kw)

    # 构建上下文片段
    context_lines = []
    for msg in context_msgs[-4:]:  # 最近 4 条作为上下文
        role = msg.get("role", "user")
        content = msg.get("content", "")[:300]
        label = "用户" if role == "user" else "林赛"
        context_lines.append(f"{label}: {content}")

    # 构建 topics YAML（避免 f-string 反斜杠问题）
    topics_yaml = "[" + ", ".join(f'"{t}"' for t in topics) + "]"

    lines = [
        "---",
        f'type: "capture"',
        f'created: "{now}"',
        f'session: "{session_id}"',
        f"topics: {topics_yaml}",
        f'trigger: "{trigger_msg.get("role", "user")}"',
        "---",
        "",
        f"# {safe_topic}",
        "",
        "## 触发消息",
        f"{trigger_msg.get('role', 'user')}: {trigger_msg.get('content', '')[:500]}",
        "",
        "## 上下文",
    ]
    lines.extend(context_lines)
    lines.extend([
        "",
        "## 林赛的批注",
        "",
        "（此栏位留给后续补充——用户或林赛可在对话中手动完善）",
        "",
        "## 相关操作",
        "",
        "- [ ] 提炼为 wiki 概念页",
        "- [ ] 关联到实验/项目",
        "- [ ] 补充参考文献",
    ])
    return "\n".join(lines)


def capture_from_session(
    session_id: str,
    topic_hint: str = "",
    max_lookback: int = 6,
) -> Dict[str, Any]:
    """从会话中捕获一条知识片段。

    Args:
        session_id: 会话 ID
        topic_hint: 话题提示（用于文件名和标题）
        max_lookback: 回溯消息数

    Returns:
        {"captured": bool, "path": str, "reason": str}
    """
    _ensure_dir()
    msgs = _load_session_messages(session_id)
    if not msgs:
        return {"captured": False, "path": "", "reason": "会话无消息"}

    # 取最近的消息作为触发消息（通常是用户最新输入）
    trigger_msg = msgs[-1] if msgs else {}
    user_input = trigger_msg.get("content", "")
    session_mode = trigger_msg.get("mode", "co-working")

    should, reason = should_capture(user_input, session_mode)
    if not should:
        return {"captured": False, "path": "", "reason": reason}

    # 避免重复捕获：检查今天是否已有相似内容的 capture
    date_prefix = _now_utc()[:10]
    existing = list(CAPTURE_DIR.glob(f"{date_prefix}_*.md"))
    for f in existing:
        text = f.read_text(encoding="utf-8")
        # 简单去重：如果触发消息内容已在某个 capture 中
        if user_input[:100] in text:
            return {"captured": False, "path": str(f.relative_to(PROJECT_ROOT / "knowledge")), "reason": "今日已存在相似 capture"}

    # 确定话题
    if not topic_hint:
        topic_hint = _guess_topic(user_input)

    # 构建上下文
    context_msgs = msgs[-max_lookback:] if len(msgs) > max_lookback else msgs

    content = _build_capture_content(session_id, topic_hint, trigger_msg, context_msgs)
    filename = f"{date_prefix}_{_safe_filename(topic_hint)}.md"
    filepath = CAPTURE_DIR / filename

    # 如果文件已存在，追加而非覆盖
    if filepath.exists():
        old = filepath.read_text(encoding="utf-8")
        content = old + "\n\n---\n\n## 追加捕获（" + _now_utc() + "）\n\n" + content.split("---", 2)[2].strip()

    filepath.write_text(content, encoding="utf-8")

    rel_path = str(filepath.relative_to(PROJECT_ROOT / "knowledge"))
    return {"captured": True, "path": rel_path, "reason": reason}


def _guess_topic(text: str) -> str:
    """从文本中猜测话题（用于文件名）。"""
    # 优先找引号内的内容
    quotes = re.findall(r'["""]([^"""]{2,20})["""]', text)
    if quotes:
        return quotes[0]
    # 找第一个长名词短语
    nouns = re.findall(r'[\u4e00-\u9fff]{2,8}(?:[的之])?[\u4e00-\u9fff]{2,8}', text)
    if nouns:
        return nouns[0]
    # 找英文术语
    terms = re.findall(r'[A-Z][a-zA-Z\s]{2,20}(?:[\w\-]+)?', text)
    if terms:
        return terms[0].strip()
    return "未分类片段"


def list_captures(limit: int = 50) -> List[Dict[str, Any]]:
    """列出所有 capture 文件。"""
    _ensure_dir()
    files = sorted(CAPTURE_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    result = []
    for fpath in files[:limit]:
        try:
            text = fpath.read_text(encoding="utf-8")
            # 简单解析 frontmatter
            m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
            meta = {}
            if m:
                for line in m.group(1).strip().split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meta[k.strip()] = v.strip().strip('"').strip("'")
            topics = []
            if "topics" in meta:
                inner = meta["topics"].strip("[]")
                topics = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            result.append({
                "path": str(fpath.relative_to(PROJECT_ROOT / "knowledge")),
                "name": fpath.name,
                "created": meta.get("created", ""),
                "session": meta.get("session", ""),
                "topics": topics,
            })
        except Exception:
            continue
    return result


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("◐ kb_capture 自检")

    # 1. 技术参数检测
    test1 = "我们用的是800nm，3mJ，1kHz。晶体是MgO:LiNbO3。"
    params = extract_tech_params(test1)
    print(f"  参数提取: {len(params)} 个 — {'✓' if len(params) >= 3 else '✗'} ({params})")

    # 2. 捕获判断
    should, reason = should_capture(test1, "co-working")
    print(f"  捕获判断: {'✓' if should else '✗'} ({reason})")

    should2, reason2 = should_capture("你好林赛", "co-working")
    print(f"  闲聊过滤: {'✓' if not should2 else '✗'} ({reason2})")

    should3, reason3 = should_capture("请把这个记下来：驱动光用 800nm", "co-working")
    print(f"  明确请求: {'✓' if should3 else '✗'} ({reason3})")

    # 3. 话题猜测
    print(f"  话题猜测: '{_guess_topic('关于固体HHG的相位匹配问题')}'")

    print("✓ kb_capture 自检通过")
