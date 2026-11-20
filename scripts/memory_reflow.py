#!/usr/bin/env python3
"""
memory_reflow.py — 认知回流引擎（v3.4 核心）

用途：
    从 hermes 会话中提炼用户决策/偏好/观点，写入林赛记忆系统。
    打通"hermes 产出 → 林赛记忆"的认知回流通道。

    让林赛"记得你"——下次对话能说"上次你决定把 T1-T4 作为共性方向"。

用法：
    from scripts.memory_reflow import reflow_all, cold_start
    reflow_all()       # 同步新会话的记忆提炼
    cold_start()       # 回溯全部已同步会话，一次性填充记忆

    # CLI 直接运行
    python scripts/memory_reflow.py --cold-start   # 冷启动
    python scripts/memory_reflow.py --reflow       # 增量提炼
    python scripts/memory_reflow.py --status       # 查看记忆状态
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc as _now_utc, save_json as _write_json, load_json as _read_json

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
_MEMORY_DIR = _PROJECT_ROOT / "memory"
_HERMES_SESSIONS = Path.home() / ".hermes" / "profiles" / "linsai" / "sessions"
_SYNC_STATE = _MEMORY_DIR / "sync-state.json"
_USER_PROFILE = _MEMORY_DIR / "user-profile.json"
_WORKING_CONTEXT = _MEMORY_DIR / "working-context.json"
_LONG_TERM_MEMORY = _MEMORY_DIR / "long-term-memory.json"
_NSFC_DECISIONS = _MEMORY_DIR / "nsfc-decisions.json"
_PAPER_FEEDBACK = _MEMORY_DIR / "paper-feedback.json"
_REFLOW_STATE = _MEMORY_DIR / "reflow-state.json"

# 决策/偏好/观点的正则模式
_DECISION_PATTERNS = [
    r"(?:我决定|决定|选择|确定)(.{5,80})",
    r"(?:我觉得|我认为|我的看法)(.{5,80})",
    r"(?:优先级最高|最重要的是|核心是)(.{5,60})",
    r"(?:方向是|路线是|策略是)(.{5,60})",
]

_RESEARCH_KEYWORDS = [
    "高次谐波", "HHG", "固体HHG", "阿秒", "attosecond", "拓扑绝缘体",
    "相位匹配", "三步模型", "Lewenstein", "水窗口", "谷电子学",
    "量子几何", "贝里曲率", "超快", "强场",
]


# ---------------------------------------------------------------------------
# 记忆文件读写
# ---------------------------------------------------------------------------
def _load_profile() -> dict:
    return _read_json(_USER_PROFILE, {
        "communication_style": {},
        "interaction_history": {},
        "research_field": [],
        "known_skills": [],
        "preferences": {},
        "_confidence": {},
    })


def _save_profile(profile: dict) -> None:
    profile["last_updated"] = _now_utc()
    _write_json(_USER_PROFILE, profile)


def _load_working_context() -> dict:
    return _read_json(_WORKING_CONTEXT, {
        "active_projects": [],
        "pending_decisions": [],
        "key_insights": [],
    })


def _save_working_context(ctx: dict) -> None:
    ctx["last_updated"] = _now_utc()
    _write_json(_WORKING_CONTEXT, ctx)


def _load_long_term_memory() -> dict:
    return _read_json(_LONG_TERM_MEMORY, {
        "session_summaries": [],
        "snippets_index": [],
        "snippets": [],
    })


def _save_long_term_memory(ltm: dict) -> None:
    _write_json(_LONG_TERM_MEMORY, ltm)


def _load_reflow_state() -> dict:
    return _read_json(_REFLOW_STATE, {
        "reflowed_sessions": [],
        "last_reflow": None,
        "stats": {"snippets_extracted": 0, "decisions_extracted": 0, "preferences_extracted": 0},
    })


def _save_reflow_state(state: dict) -> None:
    state["last_reflow"] = _now_utc()
    _write_json(_REFLOW_STATE, state)


# ---------------------------------------------------------------------------
# Hermes 会话扫描与提炼
# ---------------------------------------------------------------------------
def _scan_hermes_session(session_path: Path) -> dict | None:
    """扫描单个 hermes 会话，提取记忆-worthy 内容。"""
    try:
        data = json.loads(session_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    messages = data.get("messages", [])
    if not messages:
        return None

    session_id = data.get("session_id", session_path.stem)
    platform = data.get("platform", "unknown")
    session_start = data.get("session_start", "")

    extracted = {
        "session_id": session_id,
        "platform": platform,
        "session_start": session_start,
        "memory_calls": [],       # memory 工具调用 → 用户偏好/事实
        "skill_calls": [],        # skill_manage 调用 → 技能变更
        "user_decisions": [],     # 用户消息中的决策/观点
        "compaction_goals": [],   # CONTEXT COMPACTION 中的目标/约束
        "research_signals": [],   # 研究方向关键词
        "user_messages_count": 0,
        "assistant_messages_count": 0,
    }

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        # 统计消息数
        if role == "user":
            extracted["user_messages_count"] += 1
        elif role == "assistant":
            extracted["assistant_messages_count"] += 1

        # 提取 memory 工具调用
        tool_calls = msg.get("tool_calls", [])
        for tc in tool_calls:
            func = tc.get("function", {})
            func_name = func.get("name", "")
            try:
                args = json.loads(func.get("arguments", "{}"))
            except Exception:
                args = {}

            if func_name == "memory":
                extracted["memory_calls"].append({
                    "action": args.get("action", ""),
                    "target": args.get("target", ""),
                    "content": args.get("content", "")[:500],
                    "key": args.get("key", ""),
                })
            elif func_name == "skill_manage":
                extracted["skill_calls"].append({
                    "action": args.get("action", ""),
                    "name": args.get("name", ""),
                })

        # 提取用户决策/观点
        if role == "user" and content and not content.startswith("[CONTEXT COMPACTION"):
            for pattern in _DECISION_PATTERNS:
                matches = re.findall(pattern, content)
                for match in matches:
                    text = match.strip()
                    if len(text) >= 5:
                        extracted["user_decisions"].append(text[:200])

            # 检测研究方向关键词
            for kw in _RESEARCH_KEYWORDS:
                if kw.lower() in content.lower():
                    if kw not in extracted["research_signals"]:
                        extracted["research_signals"].append(kw)

        # 提取 CONTEXT COMPACTION 中的目标和约束
        if role == "user" and content and "CONTEXT COMPACTION" in content:
            goals = re.findall(r"## (?:Active Task|Goal|Constraints & Preferences)\n(.+?)(?:\n##|\Z)", content, re.DOTALL)
            for g in goals:
                g = g.strip()[:500]
                if g:
                    extracted["compaction_goals"].append(g)

    # 过滤空结果
    has_content = (
        extracted["memory_calls"] or
        extracted["skill_calls"] or
        extracted["user_decisions"] or
        extracted["compaction_goals"] or
        extracted["research_signals"]
    )
    if not has_content:
        return None

    return extracted


def _apply_extraction(extraction: dict, profile: dict, ctx: dict, ltm: dict) -> dict:
    """将提取结果应用到记忆文件，返回变更统计。"""
    stats = {"snippets": 0, "decisions": 0, "preferences": 0, "skills": 0, "research": 0}
    session_id = extraction["session_id"]
    ts = extraction.get("session_start", _now_utc())

    # 1. memory 工具调用 → snippets + preferences
    # v4.0: 提取已有 snippet 的内容前缀集合，用于去重
    existing_snippet_keys = set()
    for s in ltm.get("snippets", []):
        text = s.get("summary", s.get("content", ""))
        if text:
            existing_snippet_keys.add(text[:60].strip().lower())

    for mc in extraction["memory_calls"]:
        content = mc.get("content", "").strip()
        if not content:
            continue
        # v4.0: 质量过滤 — 跳过过短的碎片
        if len(content) < 20:
            continue
        action = mc.get("action", "")
        target = mc.get("target", "")

        # v4.0: 去重检查 — 内容前60字符与已有 snippet 相似则跳过
        dedup_key = content[:60].strip().lower()
        if dedup_key in existing_snippet_keys:
            continue  # 已有相似内容，跳过
        existing_snippet_keys.add(dedup_key)

        # 写入 snippets
        snippet_id = f"reflow_{session_id}_{len(ltm['snippets'])}"
        ltm["snippets"].append({
            "id": snippet_id,
            "trigger": f"hermes:{action}:{target}",
            "summary": content[:300],
            "source": f"hermes:{session_id}",
            "importance": "high" if action == "add" else "medium",
            "timestamp": ts,
        })
        ltm["snippets_index"].append({
            "id": snippet_id,
            "trigger": f"hermes:{action}:{target}",
            "importance": "high" if action == "add" else "medium",
            "timestamp": ts,
        })
        stats["snippets"] += 1

        # 如果是用户偏好，写入 profile
        if target == "user" and action in ("add", "replace"):
            prefs = profile.setdefault("preferences", {})
            if isinstance(prefs, dict):
                key = mc.get("key", "") or "general"
                prefs[key] = content[:500]
                stats["preferences"] += 1

    # 2. skill_manage 调用 → known_skills
    for sc in extraction["skill_calls"]:
        skill_name = sc.get("name", "").strip()
        if not skill_name:
            continue
        skills = profile.setdefault("known_skills", [])
        if sc.get("action") in ("create", "patch", "edit") and skill_name not in skills:
            skills.append(skill_name)
            stats["skills"] += 1

    # 3. 用户决策 → pending_decisions + snippets
    # v4.0: 已有决策去重集合
    existing_decision_keys = set()
    for d in ctx.get("pending_decisions", []):
        t = d.get("topic", "")
        if t:
            existing_decision_keys.add(t[:40].strip().lower())

    for decision in extraction["user_decisions"][:5]:  # 每会话最多5条
        # 质量过滤：排除碎片化文本
        decision = decision.strip().rstrip("：:，,。.**")
        if len(decision) < 8:
            continue
        # v4.0: 去重检查
        dec_key = decision[:40].strip().lower()
        if dec_key in existing_decision_keys or dec_key in existing_snippet_keys:
            continue
        existing_decision_keys.add(dec_key)
        existing_snippet_keys.add(dec_key)
        # 写入 snippets
        snippet_id = f"decision_{session_id}_{len(ltm['snippets'])}"
        ltm["snippets"].append({
            "id": snippet_id,
            "trigger": "user_decision",
            "summary": decision,
            "source": f"hermes:{session_id}",
            "importance": "high",
            "timestamp": ts,
        })
        ltm["snippets_index"].append({
            "id": snippet_id,
            "trigger": "user_decision",
            "importance": "high",
            "timestamp": ts,
        })
        stats["snippets"] += 1
        stats["decisions"] += 1

        # 写入 pending_decisions（避免重复）
        existing_topics = [d.get("topic", "") for d in ctx.get("pending_decisions", [])]
        if decision[:50] not in existing_topics:
            ctx.setdefault("pending_decisions", []).append({
                "topic": decision[:100],
                "context": f"来源: hermes 会话 {session_id}",
                "deadline": "",
            })

    # 4. 研究方向关键词 → research_field
    for kw in extraction["research_signals"]:
        rf = profile.setdefault("research_field", [])
        if kw not in rf:
            rf.append(kw)
            stats["research"] += 1

    # 5. CONTEXT COMPACTION 目标 → key_insights
    for goal in extraction["compaction_goals"][:2]:
        insights = ctx.setdefault("key_insights", [])
        insight_text = goal[:200]
        if not any(i.get("text", "") == insight_text for i in insights):
            insights.append({
                "text": insight_text,
                "source": f"hermes:{session_id}",
                "timestamp": ts,
            })

    return stats


def _merge_paper_feedback(profile: dict) -> int:
    """从 paper-feedback.json 提取用户研究偏好。"""
    feedback = _read_json(_PAPER_FEEDBACK, [])
    if not feedback:
        return 0

    interested_count = sum(1 for f in feedback if f.get("action") == "interested")
    later_count = sum(1 for f in feedback if f.get("action") == "later")

    prefs = profile.setdefault("preferences", {})
    if isinstance(prefs, dict):
        prefs["paper_interests"] = {
            "interested_count": interested_count,
            "later_count": later_count,
            "total_feedback": len(feedback),
        }

    return len(feedback)


def _merge_nsfc_decisions(ctx: dict) -> int:
    """从 nsfc-decisions.json 提取 NSFC 决策。"""
    decisions = _read_json(_NSFC_DECISIONS, {})
    if not decisions:
        return 0

    pending = ctx.setdefault("pending_decisions", [])
    existing_topics = [d.get("topic", "") for d in pending]

    count = 0
    for dec_id, dec_data in decisions.items():
        status = dec_data.get("status", "")
        topic = f"NSFC 论文决策 {dec_id}: {status}"
        if topic not in existing_topics:
            pending.append({
                "topic": topic,
                "context": f"NSFC 论文去留决策，状态: {status}",
                "deadline": "",
            })
            count += 1

    return count


# ---------------------------------------------------------------------------
# 公共 API
# ---------------------------------------------------------------------------
def reflow_all(max_count: int = 50) -> dict:
    """增量提炼：扫描新的 hermes 会话，提取记忆。"""
    reflow_state = _load_reflow_state()
    reflowed = set(reflow_state.get("reflowed_sessions", []))

    profile = _load_profile()
    ctx = _load_working_context()
    ltm = _load_long_term_memory()

    # 合并已有的结构化决策数据
    _merge_paper_feedback(profile)
    _merge_nsfc_decisions(ctx)

    # 扫描 hermes 会话
    if not _HERMES_SESSIONS.exists():
        return {"error": "hermes 会话目录不存在", "scanned": 0}

    session_files = sorted(
        _HERMES_SESSIONS.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    total_stats = {"snippets": 0, "decisions": 0, "preferences": 0, "skills": 0, "research": 0}
    processed = 0
    skipped = 0

    for sf in session_files[:max_count]:
        stem = sf.stem
        if stem in reflowed:
            skipped += 1
            continue

        extraction = _scan_hermes_session(sf)
        if extraction is None:
            reflowed.add(stem)
            skipped += 1
            continue

        stats = _apply_extraction(extraction, profile, ctx, ltm)
        for k, v in stats.items():
            total_stats[k] = total_stats.get(k, 0) + v

        reflowed.add(stem)
        processed += 1

    # 更新交互历史
    hist = profile.setdefault("interaction_history", {})
    hist["hermes_sessions_reflowed"] = len(reflowed)

    # 保存
    _save_profile(profile)
    _save_working_context(ctx)
    _save_long_term_memory(ltm)

    reflow_state["reflowed_sessions"] = list(reflowed)[:500]
    reflow_state["stats"]["snippets_extracted"] += total_stats["snippets"]
    reflow_state["stats"]["decisions_extracted"] += total_stats["decisions"]
    reflow_state["stats"]["preferences_extracted"] += total_stats["preferences"]
    _save_reflow_state(reflow_state)

    return {
        "processed": processed,
        "skipped": skipped,
        "stats": total_stats,
        "total_snippets": len(ltm.get("snippets", [])),
        "total_research_fields": len(profile.get("research_field", [])),
    }


def cold_start() -> dict:
    """冷启动：回溯全部已同步会话，一次性填充记忆。"""
    # 重置 reflow 状态以处理全部会话
    reflow_state = _load_reflow_state()
    reflow_state["reflowed_sessions"] = []
    _save_reflow_state(reflow_state)

    # 处理全部会话（上限 200）
    return reflow_all(max_count=200)


def get_memory_status() -> dict:
    """获取当前记忆系统状态摘要。"""
    profile = _load_profile()
    ctx = _load_working_context()
    ltm = _load_long_term_memory()
    reflow_state = _load_reflow_state()

    return {
        "user_profile": {
            "research_field": profile.get("research_field", []),
            "known_skills": profile.get("known_skills", []),
            "preferences_keys": list(profile.get("preferences", {}).keys()) if isinstance(profile.get("preferences"), dict) else [],
            "interaction_history": profile.get("interaction_history", {}),
        },
        "working_context": {
            "active_projects": len(ctx.get("active_projects", [])),
            "pending_decisions": len(ctx.get("pending_decisions", [])),
            "key_insights": len(ctx.get("key_insights", [])),
        },
        "long_term_memory": {
            "session_summaries": len(ltm.get("session_summaries", [])),
            "snippets": len(ltm.get("snippets", [])),
        },
        "reflow": {
            "reflowed_sessions": len(reflow_state.get("reflowed_sessions", [])),
            "last_reflow": reflow_state.get("last_reflow"),
            "stats": reflow_state.get("stats", {}),
        },
    }


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def _self_check() -> None:
    """自检：验证记忆回流链路完整性。"""
    print("=" * 50)
    print("◐ memory_reflow 自检")
    print("=" * 50)

    print("\n[1/5] 检查记忆文件目录...")
    print(f"  memory 目录: {'✓' if _MEMORY_DIR.exists() else '✗'}")
    print(f"  user-profile.json: {'✓' if _USER_PROFILE.exists() else '○ 待创建'}")
    print(f"  working-context.json: {'✓' if _WORKING_CONTEXT.exists() else '○ 待创建'}")
    print(f"  long-term-memory.json: {'✓' if _LONG_TERM_MEMORY.exists() else '○ 待创建'}")

    print("\n[2/5] 检查 hermes 数据源...")
    print(f"  hermes sessions: {'✓' if _HERMES_SESSIONS.exists() else '✗ 未找到'}")
    if _HERMES_SESSIONS.exists():
        count = len(list(_HERMES_SESSIONS.glob("*.json")))
        print(f"  会话文件数: {count}")

    print("\n[3/5] 检查结构化决策数据...")
    print(f"  nsfc-decisions.json: {'✓' if _NSFC_DECISIONS.exists() else '○ 无'}")
    print(f"  paper-feedback.json: {'✓' if _PAPER_FEEDBACK.exists() else '○ 无'}")

    print("\n[4/5] 检查记忆状态...")
    status = get_memory_status()
    print(f"  研究领域: {len(status['user_profile']['research_field'])} 个")
    print(f"  已知技能: {len(status['user_profile']['known_skills'])} 个")
    print(f"  记忆片段: {status['long_term_memory']['snippets']} 条")
    print(f"  已提炼会话: {status['reflow']['reflowed_sessions']} 个")

    print("\n[5/5] 模块函数完整性...")
    funcs = [_scan_hermes_session, _apply_extraction, reflow_all, cold_start, get_memory_status]
    print(f"  核心函数: {'✓' if all(callable(f) for f in funcs) else '✗'}")

    print("\n" + "=" * 50)
    print("✓ memory_reflow 自检完成")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="认知回流引擎")
    parser.add_argument("--cold-start", action="store_true", help="冷启动：回溯全部会话")
    parser.add_argument("--reflow", action="store_true", help="增量提炼新会话")
    parser.add_argument("--status", action="store_true", help="查看记忆状态")
    parser.add_argument("--self-check", action="store_true", help="自检：验证链路完整性")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    elif args.cold_start:
        print("🔄 记忆冷启动中...")
        result = cold_start()
        print(f"✅ 冷启动完成：处理 {result['processed']} 个会话")
        print(f"   提取片段: {result['stats']['snippets']}")
        print(f"   用户决策: {result['stats']['decisions']}")
        print(f"   研究方向: {result['stats']['research']}")
        print(f"   总片段数: {result['total_snippets']}")
        print(f"   研究领域: {result['total_research_fields']}")
    elif args.reflow:
        print("🔄 增量提炼中...")
        result = reflow_all()
        print(f"✅ 增量提炼完成：处理 {result['processed']} 个新会话")
        print(f"   提取片段: {result['stats']['snippets']}")
        print(f"   总片段数: {result['total_snippets']}")
    elif args.status:
        status = get_memory_status()
        print("📊 记忆系统状态")
        print(f"   研究领域: {status['user_profile']['research_field']}")
        print(f"   已知技能: {status['user_profile']['known_skills']}")
        print(f"   偏好键: {status['user_profile']['preferences_keys']}")
        print(f"   待决策: {status['working_context']['pending_decisions']}")
        print(f"   关键洞察: {status['working_context']['key_insights']}")
        print(f"   记忆片段: {status['long_term_memory']['snippets']}")
        print(f"   已提炼会话: {status['reflow']['reflowed_sessions']}")
        print(f"   上次提炼: {status['reflow']['last_reflow']}")
    else:
        parser.print_help()
