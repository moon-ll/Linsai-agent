#!/usr/bin/env python3
"""
memory_manager.py — 记忆管理器

用途：读写、索引、压缩 LinSai-CoPilot 的长期记忆数据。
用法示例：
    >>> from scripts.memory_manager import update_user_profile, create_snippet
    >>> update_user_profile("20260508-固体HHG")
    >>> sid = create_snippet("量子纠缠", "用户发现纠缠态对HHG有增强", "session_001")
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from session_manager import load_session
except ImportError as _import_err:
    print(f"✗ 无法导入 session_manager: {_import_err}")
    sys.exit(1)


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _mem_dir() -> Path:
    d = _PROJECT_ROOT / "memory"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _snip_dir() -> Path:
    d = _mem_dir() / "snippets"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sess_dir() -> Path:
    d = _PROJECT_ROOT / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_json(path: Path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default if default is not None else {}


def _extract_matches(texts: list[str], patterns: list[str]) -> list[str]:
    results = []
    for p in patterns:
        for t in texts:
            for m in re.finditer(p, t):
                results.append(m.group(1).strip())
    return results


def update_user_profile(session_id: str) -> dict:
    """分析指定会话的内容，提取用户特征，增量更新 memory/user-profile.json。"""
    try:
        messages, state = load_session(session_id)
    except Exception as exc:
        print(f"✗ 加载会话失败: {exc}")
        raise
    user_contents = [m["content"] for m in messages if m.get("role") == "user"]
    profile_path = _mem_dir() / "user-profile.json"
    profile = _load_json(profile_path, {})
    confidence = profile.get("_confidence", {})

    # 研究领域 — 按精确度优先级排序，避免宽泛关键词误匹配
    RESEARCH_PATTERNS = [
        # 最精确：完整短语 + 明确分隔符
        r"(?:研究方向|研究领域|研究课题)\s*(?:是|为|[:：])\s*([^。，；\n]{2,30}?)(?:的|。|$)",
        r"我的(?:方向|领域|课题)\s*(?:是|为|[:：])\s*([^。，；\n]{2,30}?)(?:的|。|$)",
        # 中等：动词 + 领域 + 自然边界
        r"(?:我在做|我是做|我研究|我搞|我做|从事)\s*([^。，；\n]{2,30}?)(?:的(?:研究|工作|方向|领域)|方面|方向|领域|课题|。|$)",
        r"主要(?:做|研究|搞)\s*([^。，；\n]{2,30}?)(?:的|方面|方向|领域|课题|。|$)",
        # 兜底："在...领域"、"做...的"
        r"在\s*([^。，；\n]{2,30}?)\s*领域",
        r"(?:做|研究)\s*([^。，；\n]{2,30}?)(?:的|。|$)",
    ]
    research = None
    for p in RESEARCH_PATTERNS:
        for t in user_contents:
            m = re.search(p, t)
            if m:
                research = m.group(1).strip()
                # 清理常见后缀噪音
                research = re.sub(r"^(一个|一些|点|些)\s*", "", research)
                research = re.sub(r"\s+(相关|方面|方向|领域)$", "", research)
                if len(research) >= 2:
                    break
        if research and len(research) >= 2:
            break
    if research:
        old = profile.get("research_field")
        if old and old != research:
            confidence["research_field"] = confidence.get("research_field", 0.5) * 0.9
        else:
            confidence["research_field"] = min(confidence.get("research_field", 0.5) + 0.1, 1.0)
        profile["research_field"] = research

    # 已知技能
    skills_raw = _extract_matches(user_contents, [r"(?:我会|我擅长|我用过)\s*([^。，\n]{2,40})"])
    skills = set()
    for s in skills_raw:
        for part in re.split(r"[、,和/与&]+", s):
            part = part.strip()
            if len(part) >= 1:
                skills.add(part)
    # 技能归一化：去除子串重复（如保留"MATLAB编程"而去除"MATLAB"）
    def _dedup_skills(skill_set: set) -> set:
        sorted_by_len = sorted(skill_set, key=len, reverse=True)
        result = set()
        for s in sorted_by_len:
            # 仅当s被更长的技能包含且长度差≤3时才跳过（避免误删如Java/JavaScript）
            if any(s != other and s in other and (len(other) - len(s)) <= 3 for other in result):
                continue
            result.add(s)
        return result
    skills = _dedup_skills(skills)
    if skills:
        old_skills = set(profile.get("known_skills", []))
        profile["known_skills"] = sorted(_dedup_skills(old_skills | skills))
        confidence["known_skills"] = min(confidence.get("known_skills", 0.5) + 0.05 * len(skills), 1.0)

    # 偏好
    prefs_raw = _extract_matches(user_contents, [r"(?:我喜欢|我习惯|我倾向于)\s*([^。，\n]{2,60})"])
    preferences = profile.get("preferences", {})
    for pr in prefs_raw:
        if "早上" in pr or "morning" in pr:
            preferences["work_time"] = "morning"
        elif "晚上" in pr or "night" in pr:
            preferences["work_time"] = "night"
        else:
            preferences[f"pref_{len(preferences)+1}"] = pr
    if prefs_raw:
        profile["preferences"] = preferences
        confidence["preferences"] = min(confidence.get("preferences", 0.5) + 0.05, 1.0)

    # 沟通风格与交互历史
    total_len = sum(len(c) for c in user_contents)
    avg_len = total_len // len(user_contents) if user_contents else 0
    uses_formulas = any("$" in c or "```" in c or "`" in c for c in user_contents)
    profile["communication_style"] = {"avg_input_length": avg_len, "uses_formulas": uses_formulas}
    hist = profile.get("interaction_history", {})
    hist["total_sessions"] = hist.get("total_sessions", 0) + 1
    hist["total_messages"] = hist.get("total_messages", 0) + len(messages)
    profile["interaction_history"] = hist
    profile["last_updated"] = _now_utc()
    profile["_confidence"] = confidence
    _write_json(profile_path, profile)
    print(f"✓ 用户画像已更新: {profile_path.name}")
    return profile


def update_working_context(session_id: str) -> dict:
    """从会话中提取项目和决策信息，更新 memory/working-context.json。"""
    try:
        messages, state = load_session(session_id)
    except Exception as exc:
        print(f"✗ 加载会话失败: {exc}")
        raise
    all_contents = [m["content"] for m in messages]
    ctx_path = _mem_dir() / "working-context.json"
    ctx = _load_json(ctx_path, {"active_projects": [], "pending_decisions": [], "key_insights": []})

    proj_raw = _extract_matches(all_contents, [
        r"(?:我在做|我正在做|我是做|我在搞|我在研究)\s*([^。，\n]{2,40}?)(?:的(?:项目|课题)|项目|课题|。|$)",
        r"(?:项目|课题)\s*[：:]\s*([^。，\n]{2,40})",
    ])
    existing = {x.get("name", "") for x in ctx.get("active_projects", [])}
    for p in proj_raw:
        if p and p not in existing:
            ctx.setdefault("active_projects", []).append({"name": p, "status": "active", "last_mentioned": _now_utc()})

    dec_raw = _extract_matches(all_contents, [r"(?:还没决定|在考虑|不确定)\s*[，,]?\s*([^。，\n]{2,60})"])
    existing_dec = {x.get("topic", "") for x in ctx.get("pending_decisions", [])}
    for d in dec_raw:
        if d and d not in existing_dec:
            ctx.setdefault("pending_decisions", []).append({"topic": d, "context": "", "deadline": ""})

    ins_raw = _extract_matches(all_contents, [r"(?:我发现|结论是|重要的是)\s*[，,]?\s*([^。，\n]{2,80})"])
    existing_ins = {x.get("insight", "") for x in ctx.get("key_insights", [])}
    for i in ins_raw:
        if i and i not in existing_ins:
            ctx.setdefault("key_insights", []).append({"insight": i, "source_session": session_id, "timestamp": _now_utc()})

    ctx["last_updated"] = _now_utc()
    _write_json(ctx_path, ctx)
    print(f"✓ 工作上下文已更新: {ctx_path.name}")
    return ctx


def ensure_long_term_memory() -> dict:
    """确保 memory/long-term-memory.json 存在并返回其内容。"""
    path = _mem_dir() / "long-term-memory.json"
    default = {"session_summaries": [], "snippets_index": [], "snippets": []}
    if path.exists():
        data = _load_json(path, default)
        for k in default:
            data.setdefault(k, default[k])
        _write_json(path, data)
        return data
    _write_json(path, default)
    print(f"✓ 长期记忆文件已初始化: {path.name}")
    return default


def create_snippet(trigger: str, summary: str, source: str, importance: int = 3) -> str:
    """创建记忆片段到 memory/snippets/ 目录。返回 snippet_id。"""
    if not 1 <= importance <= 5:
        raise ValueError("importance 必须在 1-5 之间")
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    safe = re.sub(r"[^\w\u4e00-\u9fff]+", "-", trigger.strip())[:20].strip("-") or "snippet"
    filename = f"{ts}-{safe}.md"
    sid = f"snippet_{ts}"
    path = _snip_dir() / filename
    fm = {"id": sid, "trigger": trigger, "source": source, "importance": importance, "created_at": _now_utc()}
    yaml = ["---"] + [f"{k}: {v}" for k, v in fm.items()] + ["---"]
    path.write_text("\n".join(yaml) + f"\n\n{summary}\n", encoding="utf-8")
    ltm = ensure_long_term_memory()
    ltm["snippets_index"].append({"id": sid, "trigger": trigger, "summary": summary, "source": source, "timestamp": _now_utc(), "importance": importance})
    ltm.setdefault("snippets", []).append({"id": sid, "trigger": trigger, "summary": summary})
    _write_json(_mem_dir() / "long-term-memory.json", ltm)
    print(f"✓ 记忆片段已创建: {filename}")
    return sid


def search_snippets(query: str, limit: int = 5) -> list[dict]:
    """关键词搜索记忆片段。返回匹配片段列表，按importance倒序。"""
    q = query.lower()
    results = []
    for path in _snip_dir().glob("*.md"):
        text = path.read_text(encoding="utf-8")
        low = text.lower()
        if q not in low:
            continue
        weight = 1
        if "---" in low:
            parts = low.split("---", 2)
            if len(parts) >= 2 and q in parts[1]:
                weight = 3
        sid_m = re.search(r"^id:\s*(.+)$", text, re.M)
        trigger_m = re.search(r"^trigger:\s*(.+)$", text, re.M)
        source_m = re.search(r"^source:\s*(.+)$", text, re.M)
        ts_m = re.search(r"^created_at:\s*(.+)$", text, re.M)
        imp_m = re.search(r"^importance:\s*(\d+)$", text, re.M)
        summary = ""
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                summary = parts[2].strip()
        results.append({
            "id": sid_m.group(1).strip() if sid_m else "",
            "trigger": trigger_m.group(1).strip() if trigger_m else "",
            "summary": summary,
            "source": source_m.group(1).strip() if source_m else "",
            "timestamp": ts_m.group(1).strip() if ts_m else "",
            "importance": int(imp_m.group(1)) if imp_m else 3,
            "weight": weight,
        })
    results.sort(key=lambda x: (-x["importance"], -x["weight"]))
    return results[:limit]


def cleanup_expired_snippets(days: int = 90) -> int:
    """清理超过days天未被引用的记忆片段，返回删除数量。"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    count = 0
    ltm = ensure_long_term_memory()
    new_index = []
    kept_snippets = []
    for path in list(_snip_dir().glob("*.md")):
        text = path.read_text(encoding="utf-8")
        sid_m = re.search(r"^id:\s*(.+)$", text, re.M)
        sid = sid_m.group(1).strip() if sid_m else ""
        created_m = re.search(r"^created_at:\s*(.+)$", text, re.M)
        created_str = created_m.group(1).strip() if created_m else ""
        created = None
        if created_str:
            try:
                created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            except ValueError:
                pass
        if created and created < cutoff:
            path.unlink()
            count += 1
            continue
        entry = next((x for x in ltm.get("snippets_index", []) if x.get("id") == sid), None)
        if entry:
            new_index.append(entry)
        s_entry = next((x for x in ltm.get("snippets", []) if x.get("id") == sid), None)
        if s_entry:
            kept_snippets.append(s_entry)
    ltm["snippets_index"] = new_index
    ltm["snippets"] = kept_snippets
    _write_json(_mem_dir() / "long-term-memory.json", ltm)
    print(f"✓ 清理完成，删除 {count} 个过期片段")
    return count


def generate_session_summary(session_id: str) -> str:
    """为指定会话生成结构化摘要。返回摘要文本。"""
    session_dir = _sess_dir() / session_id
    if not session_dir.exists():
        raise FileNotFoundError(f"会话不存在: {session_id}")
    messages, state = load_session(session_id)
    topic = state.get("topic", session_id)
    if len(messages) <= 5:
        lines = [f"## 会话摘要: {session_id}", f"**主题**: {topic}", f"**模式**: {state.get('mode', '')}", ""]
        for m in messages:
            role = "用户" if m.get("role") == "user" else "林赛"
            lines.append(f"- **{role}**: {m.get('content', '')[:200]}")
        summary = "\n".join(lines)
    else:
        history_text = "\n".join(f"{'用户' if m.get('role') == 'user' else '林赛'}: {m.get('content', '')}" for m in messages[-20:])
        system_prompt = "你是会话摘要助手。请为以下对话生成结构化摘要。"
        user_prompt = f"请为以下对话生成结构化摘要，包含：主题、关键决策、待办事项、情感基调。\n\n对话历史:\n{history_text}\n\n请以 Markdown 格式输出摘要。"
        try:
            from copilot_engine import call_llm
            summary = call_llm(system_prompt, [{"role": "user", "content": user_prompt}], timeout=60)
        except Exception as exc:
            print(f"⚠ LLM 调用失败，使用简化摘要: {exc}")
            summary = "\n".join(f"{'用户' if m.get('role') == 'user' else '林赛'}: {m.get('content', '')[:120]}" for m in messages)
    summary_path = session_dir / "summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"✓ 会话摘要已生成: {summary_path.name}")
    ltm = ensure_long_term_memory()
    entry = {"session_id": session_id, "topic": topic, "summary": summary[:500], "key_decisions": [], "timestamp": _now_utc()}
    for i, s in enumerate(ltm.get("session_summaries", [])):
        if s.get("session_id") == session_id:
            ltm["session_summaries"][i] = entry
            break
    else:
        ltm["session_summaries"].append(entry)
    _write_json(_mem_dir() / "long-term-memory.json", ltm)
    print(f"✓ 长期记忆索引已更新")
    return summary


def get_relevant_memories(session_id: str, user_input: str) -> dict:
    """返回与用户输入相关的记忆摘要，供context_builder注入Prompt。"""
    profile = _load_json(_mem_dir() / "user-profile.json", {})
    work_ctx = _load_json(_mem_dir() / "working-context.json", {})
    parts = []
    if profile.get("research_field"):
        parts.append(f"用户是{profile['research_field']}研究者")
    if profile.get("known_skills"):
        parts.append(f"擅长{', '.join(str(s) for s in profile['known_skills'][:3])}")
    if profile.get("preferences"):
        prefs = list(profile["preferences"].items())[:2]
        parts.append(f"偏好{', '.join(f'{k}={v}' for k, v in prefs)}")
    profile_summary = "，".join(parts) if parts else "暂无用户画像"
    if len(profile_summary) > 200:
        profile_summary = profile_summary[:197] + "..."
    wparts = []
    projects = work_ctx.get("active_projects", [])
    if projects:
        wparts.append(f"进行中项目：{', '.join(p.get('name', '') for p in projects[:3] if p.get('name'))}")
    decisions = work_ctx.get("pending_decisions", [])
    if decisions:
        wparts.append(f"待决策：{', '.join(d.get('topic', '') for d in decisions[:2] if d.get('topic'))}")
    work_context_summary = "；".join(wparts) if wparts else "暂无工作上下文"
    if len(work_context_summary) > 300:
        work_context_summary = work_context_summary[:297] + "..."
    snippets = search_snippets(user_input, limit=5)
    sparts = [f"{i+1}. {s.get('trigger', '')}: {s.get('summary', '')[:80]}" for i, s in enumerate(snippets[:3])]
    related_snippets = "\n".join(sparts) if sparts else "无相关记忆片段"
    if len(related_snippets) > 500:
        related_snippets = related_snippets[:497] + "..."
    return {"profile_summary": profile_summary, "work_context_summary": work_context_summary, "related_snippets": related_snippets}


if __name__ == "__main__":
    print("=" * 50 + "\n◐ 开始 memory_manager 自检\n" + "=" * 50)
    from session_manager import create_session, append_message

    print("\n[1/8] 创建测试会话...")
    sid, _ = create_session("记忆管理自检", mode="co-working")
    append_message(sid, "user", "你好林赛，我的研究方向是固体高次谐波。我擅长Python和MATLAB。我喜欢早上工作。")
    append_message(sid, "assistant", "早上好。固体HHG很有潜力，你用的驱动参数是什么？")
    append_message(sid, "user", "我在做量子轨迹分析项目，还没决定用什么数值方法。我发现高阶谐波对相位很敏感。")
    append_message(sid, "assistant", "这很重要。你可以先试试谱方法。")

    print("\n[2/8] 更新用户画像...")
    profile = update_user_profile(sid)
    assert profile.get("research_field") == "固体高次谐波"
    assert "Python" in profile.get("known_skills", [])
    assert profile.get("preferences", {}).get("work_time") == "morning"
    print(f"   研究领域: {profile.get('research_field')}, 技能: {profile.get('known_skills')}, 偏好: {profile.get('preferences')}")

    print("\n[3/8] 更新工作上下文...")
    wctx = update_working_context(sid)
    assert any("量子轨迹分析" in p.get("name", "") for p in wctx.get("active_projects", []))
    assert any("数值方法" in d.get("topic", "") for d in wctx.get("pending_decisions", []))
    print(f"   项目: {[p['name'] for p in wctx.get('active_projects', [])]}, 待决策: {[d['topic'] for d in wctx.get('pending_decisions', [])]}")

    print("\n[4/8] 创建测试记忆片段...")
    s1 = create_snippet("相位敏感性", "用户发现HHG对驱动相位高度敏感", sid, importance=4)
    s2 = create_snippet("量子轨迹", "使用量子轨迹方法分析固体HHG", sid, importance=3)
    s3 = create_snippet("Python脚本", "用户习惯用Python处理实验数据", sid, importance=2)
    assert len(list(_snip_dir().glob("*.md"))) >= 3
    print(f"   创建片段: {s1}, {s2}, {s3}")

    print("\n[5/8] 搜索记忆片段...")
    results = search_snippets("相位", limit=3)
    assert len(results) >= 1 and any("相位" in r.get("trigger", "") for r in results)
    print(f"   搜索'相位'返回 {len(results)} 个结果: {', '.join(r['trigger'] for r in results)}")

    print("\n[6/8] 生成会话摘要...")
    summary = generate_session_summary(sid)
    assert (_sess_dir() / sid / "summary.md").exists()
    print(f"   摘要长度: {len(summary)} 字符")

    print("\n[7/8] 获取相关记忆...")
    mem = get_relevant_memories(sid, "固体HHG实验方案")
    assert "profile_summary" in mem
    print(f"   画像: {mem['profile_summary'][:60]}...")
    print(f"   工作: {mem['work_context_summary'][:60]}...")
    print(f"   片段: {mem['related_snippets'][:60]}...")

    print("\n[8/8] 清理过期片段...")
    old_time = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d%H%M%S%f")
    old_created = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    old_file = _snip_dir() / f"{old_time}-过期片段.md"
    old_file.write_text(f"---\nid: snippet_old\ntrigger: 过期\nsource: test\nimportance: 1\ncreated_at: {old_created}\n---\n\n这是过期测试片段\n", encoding="utf-8")
    deleted = cleanup_expired_snippets(days=0)
    assert deleted >= 1 and not old_file.exists()
    print(f"   删除 {deleted} 个过期片段")

    print("\n[清理] 删除测试数据...")
    test_session_dir = _sess_dir() / sid
    if test_session_dir.exists():
        shutil.rmtree(test_session_dir)
        print(f"   已删除测试会话: {sid}")
    for f in _snip_dir().glob("*.md"):
        if any(k in f.name for k in ["相位", "轨迹", "Python"]):
            f.unlink()
            print(f"   已删除测试片段: {f.name}")
    for fname in ["user-profile.json", "working-context.json", "long-term-memory.json"]:
        fpath = _mem_dir() / fname
        if fpath.exists():
            fpath.unlink()
            print(f"   已重置 {fname}")

    print("\n" + "=" * 50 + "\n✓ 所有自检项目通过\n" + "=" * 50)
