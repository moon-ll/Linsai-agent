#!/usr/bin/env python3
"""上下文构建器：组装人格注入 + 记忆 + 会话历史 + 当前输入

用法:
    from context_builder import build_context
    ctx = build_context("20260508-固体HHG", "帮我看看光路设计", mode="co-working")
    print(f"system: {len(ctx['system_prompt'])}, messages: {len(ctx['messages'])}")
"""

import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# 预算与截断配置
DEFAULT_BUDGETS = {"system": 8000, "memory": 6000, "context": 4000, "history": 10000, "input": 2000, "skills": 2000, "knowledge": 1200}
DEFAULT_TOTAL, EMERGENCY_TOTAL = 30000, 50000
TRUNCATION_ORDER = ["history", "memory", "skills", "knowledge", "context", "system"]
MIN_KEEP = {"system": 2000, "memory": 0, "context": 0, "history": 0, "skills": 0, "knowledge": 0, "input": None}


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_json(path: Path, default=None):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
_try_memory_manager = None
try:
    import importlib.util
    _mm_path = Path(__file__).parent / "memory_manager.py"
    if _mm_path.exists():
        _spec = importlib.util.spec_from_file_location("memory_manager", _mm_path)
        _mm_mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mm_mod)
        _try_memory_manager = _mm_mod
except Exception:
    pass


# 尝试导入 skill_manager
_try_skill_manager = None
try:
    import importlib.util
    _sm_path = Path(__file__).parent / "skill_manager.py"
    if _sm_path.exists():
        _spec = importlib.util.spec_from_file_location("skill_manager", _sm_path)
        _sm_mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_sm_mod)
        _try_skill_manager = _sm_mod
except Exception:
    pass


# 尝试导入 knowledge_base
_try_knowledge_base = None
try:
    import importlib.util
    _kb_path = Path(__file__).parent / "knowledge_base.py"
    if _kb_path.exists():
        _spec = importlib.util.spec_from_file_location("knowledge_base", _kb_path)
        _kb_mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_kb_mod)
        _try_knowledge_base = _kb_mod
except Exception:
    pass


def _read_profile() -> str:
    d = _load_json(PROJECT_ROOT / "memory" / "user-profile.json", default={})
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
    d = _load_json(PROJECT_ROOT / "memory" / "long-term-memory.json", default={})
    s = d.get("snippets", [])
    return f"[长期记忆] 共 {len(s)} 条记忆片段" if s else ""


def _read_work_ctx() -> str:
    d = _load_json(PROJECT_ROOT / "memory" / "working-context.json", default={})
    parts = []
    p = d.get("active_projects", [])
    if p:
        parts.append(f"进行中项目：{', '.join(x.get('name', '') for x in p if x.get('name'))}")
    if d.get("pending_decisions"):
        parts.append(f"待决策事项：{len(d['pending_decisions'])} 项")
    if d.get("key_insights"):
        parts.append(f"关键洞察：{len(d['key_insights'])} 项")
    return "\n".join(parts)


def _read_relevant_memories(session_id: str, user_input: str) -> dict:
    """使用 memory_manager 获取相关记忆，如不可用则回退到直接读取文件。"""
    if _try_memory_manager is not None:
        try:
            return _try_memory_manager.get_relevant_memories(session_id, user_input)
        except Exception:
            pass
    # 回退：直接读取文件
    return {
        "profile_summary": _read_profile(),
        "work_context_summary": _read_work_ctx(),
        "related_snippets": _read_lt_mem(),
    }


def _read_history(session_id: str):
    d = _load_json(PROJECT_ROOT / "sessions" / session_id / "messages.json")
    if isinstance(d, list):
        return [{"role": m["role"], "content": m["content"]} for m in d if m.get("role") and m.get("content")]
    return [{"role": m["role"], "content": m["content"]} for m in d.get("messages", []) if m.get("role") and m.get("content")]


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


def build_context(session_id, user_input, mode="co-working", emergency=False):
    """构建完整的 LLM 调用上下文。

    返回:
        dict，包含 system_prompt、messages 和内部预算明细 _budget
    """
    now = _now_utc()
    system_raw = _read_persona() + _mode_instr(mode, now)
    rel = _read_relevant_memories(session_id, user_input)
    profile = rel.get("profile_summary", "")
    lt = rel.get("related_snippets", "")
    memory_raw = "\n".join(p for p in (profile, lt) if p)
    context_raw = rel.get("work_context_summary", "")

    # 技能上下文注入
    skills_raw = ""
    if _try_skill_manager is not None:
        try:
            skills_raw = _try_skill_manager.get_matched_context(user_input)
        except Exception:
            pass

    # 知识库检索注入（增强版：搜索结果 + 关联知识 + 缺失概念检测）
    knowledge_raw = ""
    missing_concepts = []
    if _try_knowledge_base is not None:
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
                    parts.append(f"{src_icon}【知识库{stage_tag}: {r.get('title', r['doc'])}】\n{r['text'][:400]}")

                # 添加图谱关联知识（轻量）
                if related:
                    parts.append("\n【关联知识】")
                    for rel in related[:2]:
                        parts.append(f"  → {rel['title']}（{rel['relation']}）: {rel['text'][:200]}")

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
                    parts = [f"【知识库: {r['doc']}】\n{r['text'][:400]}" for r in results]
                    knowledge_raw = "\n\n".join(parts)
        except Exception:
            pass

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
        },
        "total_final": len(system_prompt) + sum(len(m["content"]) for m in messages),
    }
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
