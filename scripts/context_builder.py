#!/usr/bin/env python3
"""上下文构建器：组装人格注入 + 记忆 + 会话历史 + 当前输入

用法:
    from context_builder import build_context
    ctx = build_context("20260508-固体HHG", "帮我看看光路设计", mode="co-working")
    print(f"system: {len(ctx['system_prompt'])}, messages: {len(ctx['messages'])}")
"""

import json
import logging
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from common import now_utc as _now_utc, load_json
from paths import PROJECT_ROOT

_log = logging.getLogger(__name__)

# 预算与截断配置
DEFAULT_BUDGETS = {"system": 8000, "memory": 6000, "context": 4000, "history": 10000, "input": 2000, "skills": 2000, "knowledge": 1200, "project": 2000}
DEFAULT_TOTAL, EMERGENCY_TOTAL = 30000, 50000
TRUNCATION_ORDER = ["history", "memory", "skills", "knowledge", "context", "project", "system"]
MIN_KEEP = {"system": 2000, "memory": 0, "context": 0, "history": 0, "skills": 0, "knowledge": 0, "input": None, "project": 0}


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _mode_instr(mode: str, now: str) -> str:
    descs = {
        "co-working": "并肩工作模式。追问物理假设，先画整体框图再进细节，用经验支撑建议。",
        "deep-talk": "深度对话模式。从自身经历找锚点，不直接给建议，提供元认知引导。",
        "quick-check": "快速验证模式。简洁直接，给出是/否加关键问题，不展开长篇大论。",
        "proactive": "主动感知模式。温和主动，引用过往对话，尊重用户边界。",
    }
    desc = descs.get(mode, descs["co-working"])
    return f"\n\n---\n【当前交互模式】{mode}\n【实时时间】{now}\n\n【模式说明】\n{desc}\n\n注意：你的知识截至2026年。"


def _read_persona() -> str:
    return _load_text(PROJECT_ROOT / "persona" / "lin-sai-persona.md")


# 尝试导入 memory_manager 的智能检索（如可用）
from common import lazy_load as _lazy_load

_try_memory_manager = _lazy_load("memory_manager")
_try_skill_manager = _lazy_load("skill_manager")
_try_knowledge_base = _lazy_load("knowledge_base")
_try_project_context = _lazy_load("project_context")  # v3.5: 课题上下文注入
_try_project_kb = _lazy_load("project_kb")  # v3.5.1: 课题知识库统一检索


def _read_profile() -> str:
    d = load_json(PROJECT_ROOT / "memory" / "user-profile.json", default={})
    parts = []
    if d.get("research_field"):
        parts.append(f"用户研究领域：{d['research_field']}")
    if d.get("known_skills"):
        parts.append(f"已知技能：{', '.join(str(s) for s in d['known_skills'])}")
    if d.get("preferences"):
        parts.append(f"偏好：{json.dumps(d['preferences'], ensure_ascii=False)}")
    h = d.get("interaction_history", {})
    if h:
        parts.append(f"交互历史：累计 {h.get('total_sessions', 0)} 次会话")
    return "\n".join(parts)


def _read_lt_mem() -> str:
    """读取长期记忆片段（Phase 2: 返回实际内容而非计数）。"""
    d = load_json(PROJECT_ROOT / "memory" / "long-term-memory.json", default={})
    snippets = d.get("snippets", [])
    if not snippets:
        return ""

    # 按时间倒序，取最近 10 条
    recent = sorted(snippets, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
    parts = [f"[长期记忆] 共 {len(snippets)} 条记忆片段，显示最近 {len(recent)} 条："]
    for s in recent:
        summary = s.get("summary", "")
        if summary:
            parts.append(f"  • {summary}")
    return "\n".join(parts)


def _read_work_ctx() -> str:
    """读取工作上下文（Phase 2: 过滤过期任务）。"""
    from datetime import date
    d = load_json(PROJECT_ROOT / "memory" / "working-context.json", default={})
    parts = []
    today = date.today()

    # 过滤过期项目：deadline 已过或状态为 completed/archived
    projects = d.get("active_projects", [])
    valid_projects = []
    for p in projects:
        status = p.get("status", "")
        if status in ("completed", "archived"):
            continue
        deadlines = p.get("deadlines", [])
        if deadlines:
            # 如果所有 deadline 都已过，过滤掉
            from datetime import datetime
            try:
                latest = max(datetime.fromisoformat(dl).date() for dl in deadlines if dl)
                if latest < today:
                    continue  # 已逾期且无未来 deadline
            except (ValueError, TypeError):
                pass  # 日期格式错误，保留
        valid_projects.append(p.get("name", ""))

    if valid_projects:
        parts.append(f"进行中项目：{', '.join(v for v in valid_projects if v)}")

    # 过滤过期待决策
    pending = d.get("pending_decisions", [])
    valid_pending = []
    for pd_ in pending:
        dl = pd_.get("deadline", "")
        if dl:
            try:
                from datetime import datetime
                if datetime.fromisoformat(dl).date() < today:
                    continue  # 已逾期
            except (ValueError, TypeError):
                pass
        valid_pending.append(pd_.get("topic", ""))

    if valid_pending:
        parts.append(f"待决策事项：{len(valid_pending)} 项")
    if d.get("key_insights"):
        parts.append(f"关键洞察：{len(d['key_insights'])} 项")
    return "\n".join(parts)


def _read_relevant_memories(session_id: str, user_input: str) -> dict:
    """使用 memory_manager 获取相关记忆，如不可用则回退到直接读取文件。"""
    if _try_memory_manager is not None:
        try:
            return _try_memory_manager.get_relevant_memories(session_id, user_input)
        except Exception as e:
            _log.debug("memory_manager 检索失败，回退到直接读取: %s", e)
    # 回退：直接读取文件
    return {
        "profile_summary": _read_profile(),
        "work_context_summary": _read_work_ctx(),
        "related_snippets": _read_lt_mem(),
    }


def _read_history(session_id: str):
    d = load_json(PROJECT_ROOT / "sessions" / session_id / "messages.json")
    if isinstance(d, list):
        return [{"role": m["role"], "content": m["content"]} for m in d if m.get("role") and m.get("content")]
    return [{"role": m["role"], "content": m["content"]} for m in d.get("messages", []) if m.get("role") and m.get("content")]


def _read_session_project_id(session_id: str) -> str:
    """v3.5: 读取会话关联的课题ID（从 state.json）。"""
    state = load_json(PROJECT_ROOT / "sessions" / session_id / "state.json", default={})
    return state.get("project_id", "") if isinstance(state, dict) else ""


def _truncate_history(msgs, budget):
    total = sum(len(m["content"]) for m in msgs)
    if total <= budget:
        return msgs
    eff = max(0, budget - 120)
    kept, kept_len = [], 0
    for m in reversed(msgs):
        l = len(m["content"])
        if kept_len + l <= eff:
            kept.insert(0, m)
            kept_len += l
        else:
            break
    skipped = len(msgs) - len(kept)
    if skipped:
        kept.insert(0, {"role": "system", "content": f"[会话摘要] 本会话已有 {len(msgs)} 条消息，此前 {skipped} 条已折叠。继续当前讨论……"})
    return kept


def _truncate_text(text, budget):
    if len(text) <= budget:
        return text
    return text[: budget - 3] + "..." if budget > 10 else text[:budget]


def _projected(actuals, budgets):
    return sum(actuals[l] if MIN_KEEP.get(l) is None else min(actuals[l], budgets[l]) for l in actuals)


def _allocate(actuals, bases, total):
    budgets = dict(bases)
    pool = sum(max(0, budgets[l] - actuals[l]) for l in actuals)
    overs = {l: actuals[l] - budgets[l] for l in actuals if actuals[l] > budgets[l]}
    to = sum(overs.values())
    if pool > 0 and to > 0:
        dist = 0
        for l, o in overs.items():
            add = int(pool * o / to)
            budgets[l] += add
            dist += add
        if (rem := pool - dist) > 0 and "system" in overs:
            budgets["system"] += rem
    proj = _projected(actuals, budgets)
    if proj > total:
        excess = proj - total
        for l in TRUNCATION_ORDER:
            if l not in actuals or MIN_KEEP.get(l) is None:
                continue
            cap = min(actuals[l], budgets[l])
            can = max(0, cap - MIN_KEEP[l])
            if can >= excess:
                budgets[l] = cap - excess
                break
            budgets[l] = cap - can
            excess -= can
    return budgets


def _is_small_talk(text: str) -> bool:
    """v3.4: 检测是否为问候/闲聊/极短输入。"""
    text = text.strip()
    if not text or len(text) < 8:
        return True
    patterns = [
        r"^(你好|您好|嗨|哈喽|hello|hi|hey|在吗|在不在|忙吗|有空吗)",
        r"^(谢谢|感谢|多谢|thanks|thank you)",
        r"^(再见|拜拜|bye|晚安|早安|早上好|晚上好)",
        r"^(嗯|哦|好|好的|ok|OK|行|收到)",
    ]
    for p in patterns:
        if re.match(p, text, re.I):
            return True
    return False


def _build_persona_anchor() -> str:
    """v3.4: 构建人格锚点 — 林赛的当前状态摘要。

    从记忆文件提取用户研究方向、活跃项目、最近记忆片段，
    让林赛在"你好"时能说"上次你提到固体HHG相位匹配，进展如何？"
    而不是机械回复"有什么可以帮你的"。
    """
    parts = []

    # 用户研究领域 + 偏好
    profile = load_json(PROJECT_ROOT / "memory" / "user-profile.json", {})
    research_fields = profile.get("research_field", [])
    if research_fields:
        parts.append(f"用户研究方向: {', '.join(research_fields[:5])}")
    prefs = profile.get("preferences", {})
    if isinstance(prefs, dict):
        general = prefs.get("general", "")
        if general:
            parts.append(f"用户偏好: {general[:200]}")

    # 活跃项目
    ctx = load_json(PROJECT_ROOT / "memory" / "working-context.json", {})
    projects = ctx.get("active_projects", [])
    active = [p.get("name", "") for p in projects if p.get("status") == "active"][:3]
    if active:
        parts.append(f"进行中项目: {'; '.join(active)}")

    # 最近记忆片段（取最新 3 条，去重）
    ltm = load_json(PROJECT_ROOT / "memory" / "long-term-memory.json", {})
    snippets = ltm.get("snippets", [])
    recent = snippets[-6:] if snippets else []  # 多取一些用于去重
    if recent:
        seen = set()
        snippet_texts = []
        for s in reversed(recent):  # 从最新开始
            text = s.get("summary", "")[:100]
            if text and text not in seen:
                seen.add(text)
                snippet_texts.append(text)
            if len(snippet_texts) >= 3:
                break
        if snippet_texts:
            parts.append(f"最近记忆: {' | '.join(snippet_texts)}")

    if not parts:
        return ""

    anchor = "\n".join(parts)
    return (
        f"\n\n[人格锚点 — 当前状态]\n{anchor}\n\n"
        f"注意：用户发来了简短消息。请基于上述记忆自然地开启对话，"
        "不要机械回复「有什么可以帮你的」。可以提及最近的工作或记忆，"
        "让用户感受到你「记得」之前的交流。保持简洁，一两句即可。"
    )


def build_context(session_id, user_input, mode="co-working", emergency=False):
    """构建完整的 LLM 调用上下文。

    返回:
        dict，包含 system_prompt、messages 和内部预算明细 _budget
    """
    now = _now_utc()
    system_raw = _read_persona() + _mode_instr(mode, now)

    # v3.4: 浅输入人格锚定 — 问候/闲聊时注入记忆锚点，跳过无关检索
    is_small = _is_small_talk(user_input)
    if is_small:
        persona_anchor = _build_persona_anchor()
        if persona_anchor:
            system_raw += persona_anchor

    rel = _read_relevant_memories(session_id, user_input)
    profile = rel.get("profile_summary", "")
    lt = rel.get("related_snippets", "")
    memory_raw = "\n".join(p for p in (profile, lt) if p)
    context_raw = rel.get("work_context_summary", "")

    # 技能上下文注入（浅输入时跳过）
    skills_raw = ""
    if _try_skill_manager is not None and not is_small:
        try:
            skills_raw = _try_skill_manager.get_matched_context(user_input)
        except Exception as e:
            _log.debug("技能匹配失败，跳过技能注入: %s", e)

    # 知识库检索注入（增强版：搜索结果 + 关联知识 + 缺失概念检测）
    # v3.4: 接入 should_search_knowledge() 智能判断；命中埋点供前端引用展示
    knowledge_raw = ""
    missing_concepts = []
    kb_hits = []  # v3.4: 知识库命中埋点
    should_search = not is_small
    if should_search and _try_knowledge_base is not None:
        try:
            # v3.4: 使用 should_search_knowledge 精细化判断
            if hasattr(_try_knowledge_base, "should_search_knowledge"):
                should_search = _try_knowledge_base.should_search_knowledge(user_input, mode)
        except Exception as e:
            _log.debug("should_search_knowledge 判断失败，保持默认 True: %s", e)  # 判断失败时保持默认 True
    if should_search and _try_knowledge_base is not None:
        try:
            # 优先使用增强上下文（含图谱关联）
            if hasattr(_try_knowledge_base, "get_enriched_context"):
                enriched = _try_knowledge_base.get_enriched_context(user_input, top_k=2)
                results = enriched.get("results", [])
                related = enriched.get("related", [])
                missing_concepts = enriched.get("missing_concepts", [])

                parts = []
                for r in results:
                    src_icon = "📚" if r.get("source") == "raw" else "📝"
                    stage = r.get("growth_stage", "")
                    stage_tag = f" [{stage}]" if stage else ""
                    title = r.get('title', r.get('doc', '未知'))
                    parts.append(f"{src_icon}【知识库{stage_tag}: {title}】\n{r['text'][:400]}")
                    # v3.4: 记录命中条目
                    kb_hits.append({
                        "title": title,
                        "source": r.get("source", ""),
                        "stage": stage,
                        "score": r.get("score", 0),
                        "doc": r.get("doc", ""),
                    })

                # 添加图谱关联知识（轻量）
                if related:
                    parts.append("\n【关联知识】")
                    for rel in related[:2]:
                        rel_title = rel.get('title', '')
                        parts.append(f"  → {rel_title}（{rel['relation']}）: {rel['text'][:200]}")
                        kb_hits.append({
                            "title": rel_title,
                            "source": "graph",
                            "stage": "",
                            "score": 0,
                            "relation": rel.get("relation", ""),
                        })

                knowledge_raw = "\n\n".join(parts)

                # 如果检测到缺失概念，添加林赛的"认知边界"提示
                # 这体现知识库作为"林赛的可靠知识来源"而非"记忆负担"
                if missing_concepts:
                    missing_str = "、".join(missing_concepts[:3])
                    knowledge_raw += f"\n\n[林赛的认知边界] 你提到的 '{missing_str}' 在我的知识库中还没有系统的研究笔记。如果你愿意，我们可以一起把它记录下来，成为我知识体系的一部分。"
            else:
                # 回退到基础搜索
                results = _try_knowledge_base.search(user_input, top_k=2)
                if results:
                    parts = []
                    for r in results:
                        title = r.get('title', r.get('doc', '未知'))
                        parts.append(f"【知识库: {title}】\n{r['text'][:400]}")
                        kb_hits.append({
                            "title": title,
                            "source": r.get("source", ""),
                            "stage": r.get("growth_stage", ""),
                            "score": r.get("score", 0),
                            "doc": r.get("doc", ""),
                        })
                    knowledge_raw = "\n\n".join(parts)
        except Exception as e:
            _log.debug("知识库检索失败，跳过知识注入: %s", e)

    # v3.5: 课题上下文注入 — 会话关联课题时自动注入课题记忆+知识库概览
    project_ctx_raw = ""
    project_id = _read_session_project_id(session_id)
    if project_id and _try_project_context is not None:
        try:
            project_ctx_raw = _try_project_context.build_project_context(project_id, include_kb=True)
        except Exception as e:
            _log.debug("课题上下文构建失败，跳过课题注入: %s", e)

    # v3.5: @课题知识库 语法解析 — 用户输入中引用其他课题知识库
    at_refs_raw = ""
    if _try_project_context is not None:
        try:
            resolved_text, refs = _try_project_context.resolve_at_references(
                user_input, current_project_id=project_id
            )
            if refs:
                parts = []
                for r in refs:
                    title = r.get("title", "")
                    snippet = r.get("snippet", "")[:300]
                    src = r.get("project_id", "")
                    parts.append(f"📚【{src}】{title}: {snippet}")
                    kb_hits.append({
                        "title": title,
                        "source": "project_kb",
                        "stage": "",
                        "score": r.get("score", 0),
                        "doc": r.get("path", ""),
                    })
                at_refs_raw = "\n".join(parts)
        except Exception as e:
            _log.debug("@课题知识库解析失败，跳过跨课题引用: %s", e)

    # v3.5.1: 课题知识库统一检索 — 同时检索课题KB，合并到 kb_hits
    project_kb_results = []
    if project_id and _try_project_kb is not None and not is_small:
        try:
            pkb_results = _try_project_kb.search(project_id, user_input)
            for r in pkb_results[:5]:  # 最多取5条
                project_kb_results.append({
                    "title": r.get("title", ""),
                    "source": "project_kb",
                    "stage": r.get("layer", ""),
                    "score": min(r.get("score", 0) * 0.9, 1.0),  # 略降权，避免淹没全局库
                    "doc": r.get("path", ""),
                    "snippet": r.get("snippet", ""),
                })
                kb_hits.append({
                    "title": r.get("title", ""),
                    "source": "project_kb",
                    "stage": r.get("layer", ""),
                    "score": min(r.get("score", 0) * 0.9, 1.0),
                    "doc": r.get("path", ""),
                })
        except Exception as e:
            _log.debug("课题知识库统一检索失败，跳过: %s", e)

    history_msgs = _read_history(session_id)
    input_raw = user_input

    actuals = {
        "system": len(system_raw),
        "memory": len(memory_raw),
        "context": len(context_raw),
        "skills": len(skills_raw),
        "knowledge": len(knowledge_raw),
        "history": sum(len(m["content"]) for m in history_msgs),
        "input": len(input_raw),
        "project": len(project_ctx_raw) + len(at_refs_raw) + sum(len(r.get("snippet", "")) for r in project_kb_results),  # v3.5.1
    }
    total = EMERGENCY_TOTAL if emergency else DEFAULT_TOTAL
    budgets = _allocate(actuals, dict(DEFAULT_BUDGETS), total)

    system_final = _truncate_text(system_raw, budgets["system"])
    memory_final = _truncate_text(memory_raw, budgets["memory"])
    context_final = _truncate_text(context_raw, budgets["context"])
    skills_final = _truncate_text(skills_raw, budgets["skills"])
    knowledge_final = _truncate_text(knowledge_raw, budgets["knowledge"])
    history_final = _truncate_history(history_msgs, budgets["history"])
    input_final = input_raw
    # v3.5: 课题上下文截断（合并 project_ctx + at_refs，上限 2000）
    project_combined = "\n\n".join(p for p in (project_ctx_raw, at_refs_raw) if p)
    project_final = _truncate_text(project_combined, 2000)

    if len(input_final) > DEFAULT_BUDGETS["input"]:
        print(f"⚠ 当前输入长度 ({len(input_final)}) 超过建议预算 ({DEFAULT_BUDGETS['input']})")

    system_prompt = system_final
    if memory_final.strip():
        system_prompt += f"\n\n[长期记忆]\n{memory_final}"
    if context_final.strip():
        system_prompt += f"\n\n[工作上下文]\n{context_final}"
    if skills_final.strip():
        system_prompt += f"\n\n[技能上下文]\n{skills_final}"
    if knowledge_final.strip():
        system_prompt += f"\n\n[相关知识]\n{knowledge_final}"
    # v3.5.1: 课题知识库检索结果注入
    if project_kb_results:
        pkb_parts = []
        for r in project_kb_results:
            if r["score"] >= 0.4:
                pkb_parts.append(f"[PKB] {r['title']} [{r['stage']}]: {r.get('snippet', '')[:200]}")
        if pkb_parts:
            system_prompt += f"\n\n[课题知识库]\n" + "\n".join(pkb_parts)
    if project_final.strip():  # v3.5: 课题上下文注入
        system_prompt += f"\n\n[课题上下文]\n{project_final}"

    messages = [{"role": m["role"], "content": m["content"]} for m in history_final]
    messages.append({"role": "user", "content": input_final})

    result = {"system_prompt": system_prompt, "messages": messages}
    result["_budget"] = {
        "total_budget": total,
        "emergency": emergency,
        "allocations": {
            "system": {"budget": budgets["system"], "actual": actuals["system"], "final": len(system_final)},
            "memory": {"budget": budgets["memory"], "actual": actuals["memory"], "final": len(memory_final)},
            "context": {"budget": budgets["context"], "actual": actuals["context"], "final": len(context_final)},
            "skills": {"budget": budgets["skills"], "actual": actuals["skills"], "final": len(skills_final)},
            "knowledge": {"budget": budgets["knowledge"], "actual": actuals["knowledge"], "final": len(knowledge_final)},
            "history": {"budget": budgets["history"], "actual": actuals["history"], "final": sum(len(m["content"]) for m in history_final)},
            "input": {"budget": budgets["input"], "actual": actuals["input"], "final": len(input_final)},
            "project": {"budget": 2000, "actual": actuals["project"], "final": len(project_final)},
        },
        "total_final": len(system_prompt) + sum(len(m["content"]) for m in messages),
    }
    # v3.4: 知识库命中埋点 — 供前端展示引用来源
    result["kb_hits"] = kb_hits
    result["is_small_talk"] = is_small
    result["project_id"] = project_id  # v3.5: 课题关联（空串表示无课题）
    return result


if __name__ == "__main__":
    tmpdir = Path(tempfile.mkdtemp(prefix="linsai_test_"))
    try:
        (tmpdir / "persona").mkdir()
        (tmpdir / "memory").mkdir()
        (tmpdir / "sessions" / "20260508-自检会话").mkdir(parents=True)
        src = PROJECT_ROOT / "persona" / "lin-sai-persona.md"
        dst = tmpdir / "persona" / "lin-sai-persona.md"
        shutil.copy(src, dst) if src.exists() else dst.write_text("# 测试人格\n", encoding="utf-8")

        test_msgs = {
            "session_id": "20260508-自检会话",
            "messages": [
                {"msg_id": "msg_001", "role": "user", "content": "你好林赛，我想讨论固体HHG实验方案。", "timestamp": "2026-05-08T09:00:00Z", "mode": "co-working"},
                {"msg_id": "msg_002", "role": "assistant", "content": "你好。固体HHG是个有潜力的方向。你现在的驱动光源参数是什么？", "timestamp": "2026-05-08T09:01:00Z", "mode": "co-working"},
                {"msg_id": "msg_003", "role": "user", "content": "我们用的是800nm，3mJ，1kHz。晶体是MgO:LiNbO3。", "timestamp": "2026-05-08T09:02:00Z", "mode": "co-working"},
            ],
        }
        with open(tmpdir / "sessions" / "20260508-自检会话" / "messages.json", "w", encoding="utf-8") as f:
            json.dump(test_msgs, f, ensure_ascii=False, indent=2)

        import context_builder as cb
        original_root = cb.PROJECT_ROOT
        cb.PROJECT_ROOT = tmpdir

        print("=" * 50)
        print("LinSai-CoPilot 上下文构建器自检")
        print("=" * 50)

        # 1. 默认模式
        print("\n◐ 测试默认模式 (预算 30000)...")
        ctx = cb.build_context("20260508-自检会话", "帮我看看这个光路设计有没有遗漏", mode="co-working")
        total = ctx["_budget"]["total_final"]
        print(f"  system_prompt: {len(ctx['system_prompt'])}, messages: {len(ctx['messages'])}, 总字符: {total}")
        print("  ✓ 默认模式通过" if total <= 30000 else f"  ✗ 超出 {total - 30000}")
        for layer, info in ctx["_budget"]["allocations"].items():
            print(f"    {layer:8s}: 预算={info['budget']:6d}, 实际={info['actual']:6d}, 最终={info['final']:6d}")

        # 2. 紧急模式
        print("\n◐ 测试紧急模式 (预算 50000)...")
        ctx2 = cb.build_context("20260508-自检会话", "详细推导固体HHG微观模型", mode="deep-talk", emergency=True)
        t2 = ctx2["_budget"]["total_final"]
        print(f"  总字符: {t2}")
        print("  ✓ 紧急模式通过" if t2 <= 50000 else f"  ✗ 超出 {t2 - 50000}")

        # 3. 超长输入
        print("\n◐ 测试超长输入警告...")
        cb.build_context("20260508-自检会话", "A" * 5000, mode="quick-check")

        # 4. 空会话
        print("\n◐ 测试空会话...")
        es = "20260508-空会话"
        (tmpdir / "sessions" / es).mkdir(exist_ok=True)
        with open(tmpdir / "sessions" / es / "messages.json", "w", encoding="utf-8") as f:
            json.dump({"session_id": es, "messages": []}, f, ensure_ascii=False, indent=2)
        ctx4 = cb.build_context(es, "简短测试", mode="quick-check")
        print(f"  messages: {len(ctx4['messages'])}, ✓ 空会话正常")

        # 5. 历史压缩
        print("\n◐ 测试会话历史压缩...")
        (tmpdir / "persona" / "lin-sai-persona.md").write_text("# 超长人格\n" + "填充。" * 8000, encoding="utf-8")
        up = {"research_field": "强场物理", "known_skills": ["Python", "光学"] * 50, "preferences": {"style": "详细"}, "interaction_history": {"total_sessions": 20}}
        with open(tmpdir / "memory" / "user-profile.json", "w", encoding="utf-8") as f:
            json.dump(up, f, ensure_ascii=False, indent=2)
        wc = {"active_projects": [{"name": f"项目{i}", "status": "active"} for i in range(200)], "pending_decisions": ["d"] * 100}
        with open(tmpdir / "memory" / "working-context.json", "w", encoding="utf-8") as f:
            json.dump(wc, f, ensure_ascii=False, indent=2)
        lm = {"session_id": "20260508-长会话", "messages": []}
        for i in range(50):
            lm["messages"].append({"msg_id": f"msg_{i:03d}", "role": "user" if i % 2 == 0 else "assistant", "content": f"第{i+1}条消息填充。" * 30, "timestamp": "2026-05-08T09:00:00Z", "mode": "co-working"})
        (tmpdir / "sessions" / "20260508-长会话").mkdir(exist_ok=True)
        with open(tmpdir / "sessions" / "20260508-长会话" / "messages.json", "w", encoding="utf-8") as f:
            json.dump(lm, f, ensure_ascii=False, indent=2)
        ctx5 = cb.build_context("20260508-长会话", "继续讨论", mode="co-working")
        h = ctx5["_budget"]["allocations"]["history"]
        print(f"  历史实际: {h['actual']}, 最终: {h['final']}")
        fm = ctx5["messages"][0]
        print("  ✓ 已压缩" if fm["role"] == "system" and "会话摘要" in fm["content"] else "  ⚠ 未压缩")

        # 6. 压力测试
        print("\n◐ 压力测试...")
        wc = {"active_projects": [{"name": f"项目{i}", "status": "active"} for i in range(100)], "pending_decisions": ["d"] * 50, "key_insights": ["i"] * 50}
        with open(tmpdir / "memory" / "working-context.json", "w", encoding="utf-8") as f:
            json.dump(wc, f, ensure_ascii=False, indent=2)
        ctx6 = cb.build_context("20260508-长会话", "压力测试", mode="co-working")
        t6 = ctx6["_budget"]["total_final"]
        print(f"  总字符: {t6}")
        print("  ✓ 压力测试通过" if t6 <= 30000 else f"  ✗ 超出 {t6 - 30000}")
        for layer, info in ctx6["_budget"]["allocations"].items():
            print(f"    {layer:8s}: 预算={info['budget']:6d}, 实际={info['actual']:6d}, 最终={info['final']:6d}")

        print("\n" + "=" * 50 + "\n自检完成\n" + "=" * 50)
        cb.PROJECT_ROOT = original_root
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
