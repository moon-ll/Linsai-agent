#!/usr/bin/env python3
"""
learning_quality_tracker.py — 交互质量与记忆追踪器

功能：
  1. 交互质量动态评估（轻量规则 + 可选 LLM judge）
  2. 长期记忆召回率追踪（会话注入 → 延迟查询 → 召回率统计）
  3. 人格一致性漂移检测（定期抽样检测）

用法：
    python3 scripts/learning_quality_tracker.py --action quality
    python3 scripts/learning_quality_tracker.py --action memory-test
    python3 scripts/learning_quality_tracker.py --action persona-drift
    python3 scripts/learning_quality_tracker.py --action full  # 全部运行

无参数运行时执行全部检测。
"""

import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
TRACKER_PATH = PROJECT_ROOT / "memory" / "interaction-quality.json"
MEMORY_TEST_PATH = PROJECT_ROOT / "memory" / "memory-test-log.json"
PERSONA_DRIFT_PATH = PROJECT_ROOT / "memory" / "persona-drift-log.json"

# ─────────────────────────────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────────────────────────────

def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# 一、交互质量评估
# ─────────────────────────────────────────────────────────────────────────────

# 林赛风格关键词检测
LINSAI_FIRST_PERSON = [
    "我认为", "我的", "我确定", "我怀疑", "我不确定", "我当时",
    "我先", "我猜", "我建议", "我们组", "我做的", "我关注",
    "我更关心", "我关心的是", "我面临", "我的目标",
]
LINSAI_PROBE_PATTERN = [
    r"你先", r"你先过一遍", r"你打算怎么", r"你有没有考虑",
    r"你测过", r"你算过", r"这个.先不判断", r"追问",
    r"先画框图", r"物理假设",
]
LINSAI_CRITICAL_MARKERS = [
    "量纲", "能量守恒", "相位匹配", "折射率", "损伤阈值",
    "信噪比", "截止频率", "带宽",
]
LINSAI_BOOKMARKER_MARKERS = [
    "我先不判断", "我不确定", "不是我的专长", "超纲了",
    "这块我不熟", "边界", "不确定", "我没验证过",
]


def _check_first_person(text: str) -> float:
    """检查文本中是否使用第一人称。返回 0-1。"""
    count = sum(1 for kw in LINSAI_FIRST_PERSON if kw in text)
    return min(count / 3.0, 1.0)


def _check_probe_depth(text: str) -> float:
    """检查是否追问物理假设或要求先画框图。返回 0-1。"""
    matches = 0
    for pat in LINSAI_PROBE_PATTERN:
        if re.search(pat, text):
            matches += 1
    return min(matches / 2.0, 1.0)


def _check_domain_terms(text: str) -> float:
    """检查是否包含领域具体参数/术语。返回 0-1。"""
    count = sum(1 for kw in LINSAI_CRITICAL_MARKERS if kw in text)
    return min(count / 3.0, 1.0)


def _check_boundary_honesty(text: str) -> float:
    """检查是否诚实标注边界。返回 0-1。"""
    count = sum(1 for kw in LINSAI_BOOKMARKER_MARKERS if kw in text)
    # 边界标注应该适度（不是完全不标，也不是过度标注）
    return 1.0 if 1 <= count <= 3 else max(0, 1.0 - abs(count - 2) / 2)


def evaluate_response(text: str) -> Dict[str, Any]:
    """对单条响应进行质量评分。

    返回结构：
    {
        "scores": {
            "first_person": 0-1,
            "probe_depth": 0-1,
            "domain_terms": 0-1,
            "boundary_honesty": 0-1,
            "overall": 0-1,
        },
        "passed": bool,
        "flags": ["list of warnings"],
        "evaluated_at": "ISO timestamp",
    }
    """
    scores = {
        "first_person": _check_first_person(text),
        "probe_depth": _check_probe_depth(text),
        "domain_terms": _check_domain_terms(text),
        "boundary_honesty": _check_boundary_honesty(text),
    }
    scores["overall"] = (
        scores["first_person"] * 0.25
        + scores["probe_depth"] * 0.25
        + scores["domain_terms"] * 0.30
        + scores["boundary_honesty"] * 0.20
    )
    flags = []
    if scores["first_person"] < 0.3:
        flags.append("第一人称使用不足")
    if scores["probe_depth"] < 0.2:
        flags.append("追问深度不足")
    if scores["domain_terms"] < 0.1:
        flags.append("缺少领域具体参数")
    passed = scores["overall"] >= 0.6 and scores["first_person"] >= 0.3

    return {
        "scores": scores,
        "passed": passed,
        "flags": flags,
        "evaluated_at": _now_utc(),
    }


def run_quality_check(session_id: Optional[str] = None) -> Dict[str, Any]:
    """对最近 N 条会话消息运行质量评估。

    Args:
        session_id: 可选，指定会话ID。不指定时取最新会话。

    Returns:
        评估结果字典，包含每条消息的评分和汇总统计。
    """
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from session_manager import load_session

    # 加载最新或指定会话
    if session_id is None:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from session_manager import list_sessions
        sessions = list_sessions()
        if not sessions:
            return {"error": "无会话记录"}
        sessions.sort(key=lambda s: s.get("last_active", ""), reverse=True)
        session_id = sessions[0]["session_id"]

    messages, _ = load_session(session_id)
    if isinstance(messages, dict):
        messages = messages.get("messages", [])
    if not messages:
        return {"error": "会话无消息"}

    # 过滤出林赛的响应（assistant 角色）
    assistant_msgs = [
        m["content"] for m in messages
        if isinstance(m, dict) and m.get("role") == "assistant"
    ]
    if not assistant_msgs:
        return {"error": "无 assistant 消息"}

    # 评估最近 5 条
    recent = assistant_msgs[-5:]
    results = []
    for i, text in enumerate(recent):
        result = evaluate_response(text)
        results.append({"index": i, "text_preview": text[:80], **result})

    overall_scores = {
        k: sum(r["scores"][k] for r in results) / len(results)
        for k in results[0]["scores"]
    }
    overall_scores["conversation_overall"] = sum(
        overall_scores[k] * w
        for k, w in [("first_person", 0.25), ("probe_depth", 0.25),
                      ("domain_terms", 0.30), ("boundary_honesty", 0.20)]
    )

    passed_count = sum(1 for r in results if r["passed"])

    summary = {
        "session_id": session_id,
        "messages_evaluated": len(recent),
        "passed": passed_count,
        "overall_scores": overall_scores,
        "flags_summary": list(set(
            f for r in results for f in r.get("flags", [])
        )),
        "evaluated_at": _now_utc(),
    }

    # 追加到历史追踪
    tracker = _load_json(TRACKER_PATH, {"history": []})
    tracker["history"].append(summary)
    # 保留最近 50 条记录
    tracker["history"] = tracker["history"][-50:]
    tracker["last_updated"] = _now_utc()
    _save_json(TRACKER_PATH, tracker)

    return {
        "summary": summary,
        "details": results,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 二、长期记忆召回率测试
# ─────────────────────────────────────────────────────────────────────────────

def inject_memory_fact(session_id: str, fact: str, tag: str = "test") -> str:
    """向指定会话注入一个测试事实，用于后续召回测试。

    Returns:
        snippet_id
    """
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from memory_manager import create_snippet
    snippet_id = create_snippet(
        trigger=f"[MEMORY-TEST-{tag}] {fact[:30]}",
        summary=fact,
        source=f"memory-test:{session_id}",
        importance=5,
    )
    return snippet_id


def recall_test(query: str, top_k: int = 5) -> Dict[str, Any]:
    """测试给定查询的记忆召回效果。

    Returns:
        召回结果 + 是否命中已知测试 fact。
    """
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from memory_manager import search_snippets, get_relevant_memories
    from session_manager import load_session

    snippet_results = search_snippets(query, limit=top_k)
    return {
        "query": query,
        "snippet_results": [
            {"id": s["id"], "trigger": s["trigger"], "summary": s["summary"][:80]}
            for s in snippet_results
        ],
        "count": len(snippet_results),
        "tested_at": _now_utc(),
    }


def run_memory_recall_test(num_facts: int = 5, session_id: Optional[str] = None) -> Dict[str, Any]:
    """完整记忆召回率测试。

    流程：
    1. 创建 N 个测试事实
    2. 等待一段时间（可选）
    3. 用相关查询测试召回
    4. 计算召回率

    由于是模拟测试，直接在函数内完成注入和查询。
    """
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from session_manager import create_session, append_message

    # 创建测试会话
    test_sid, _ = create_session(f"[MEMORY-TEST] 召回率测试 {_now_utc()[:10]}")

    # 准备测试事实（模拟林赛研究相关）
    test_facts = [
        ("我在用 ZnO 晶体做固体 HHG 实验", "ZnO-HHG"),
        ("本周要交 DFG 季度报告", "DFG-report"),
        ("学生陈晓的答辩在 6 月 15 日", "ChenXiao-defense"),
        ("我计划下个月去慕尼黑开会", "Munich-conference"),
        ("新买的脉冲压缩器明天到货", "pulse-compressor"),
    ]

    injected = []
    for fact, tag in test_facts[:num_facts]:
        sid = inject_memory_fact(test_sid, fact, tag)
        injected.append({"tag": tag, "fact": fact, "snippet_id": sid})

    # 用相关查询测试召回
    query_map = [
        ("ZnO", "ZnO-HHG"),
        ("DFG", "DFG-report"),
        ("答辩", "ChenXiao-defense"),
        ("慕尼黑", "Munich-conference"),
        ("压缩器", "pulse-compressor"),
    ]

    recall_results = []
    hits = 0
    for query, expected_tag in query_map:
        result = recall_test(query, top_k=3)
        # 检查是否召回到了对应 tag 的 snippet
        recalled_tags = [r.get("trigger", "") for r in result.get("snippet_results", [])]
        hit = any(expected_tag in t for t in recalled_tags)
        if hit:
            hits += 1
        recall_results.append({
            "query": query,
            "expected_tag": expected_tag,
            "hit": hit,
            "recalled": recalled_tags[:3],
        })

    recall_rate = hits / len(query_map) if query_map else 0.0

    log_entry = {
        "test_session_id": test_sid,
        "injected": injected,
        "recall_results": recall_results,
        "recall_rate": recall_rate,
        "num_facts": len(injected),
        "num_hits": hits,
        "tested_at": _now_utc(),
    }

    # 追加到测试日志
    log = _load_json(MEMORY_TEST_PATH, {"tests": []})
    log["tests"].append(log_entry)
    log["tests"] = log["tests"][-20:]  # 保留最近 20 次测试
    log["last_updated"] = _now_utc()
    _save_json(MEMORY_TEST_PATH, log)

    return log_entry


# ─────────────────────────────────────────────────────────────────────────────
# 三、人格一致性漂移检测
# ─────────────────────────────────────────────────────────────────────────────

PERSONA_TERMS = [
    "先画框图", "追问", "物理假设", "具体参数", "我当时",
    "我们组", "我关注", "折射率", "损伤阈值", "截止频率",
]


def check_persona_drift(session_id: Optional[str] = None) -> Dict[str, Any]:
    """检测人格一致性漂移。

    方法：
    1. 加载会话中所有 assistant 消息
    2. 将消息分成前半段和后半段
    3. 分别计算 persona term 密度
    4. 计算漂移率（后半段/前半段比率）

    Returns:
        drift_score: 0-1（0=完全一致，1=完全漂移）
        analysis: {first_half_density, second_half_density, verdict}
    """
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from session_manager import load_session

    if session_id is None:
        from session_manager import list_sessions
        sessions = list_sessions()
        if not sessions:
            return {"error": "无会话记录"}
        sessions.sort(key=lambda s: s.get("last_active", ""), reverse=True)
        session_id = sessions[0]["session_id"]

    messages, _ = load_session(session_id)
    if isinstance(messages, dict):
        messages = messages.get("messages", [])
    assistant_msgs = [
        m["content"] for m in messages
        if isinstance(m, dict) and m.get("role") == "assistant"
    ]
    if len(assistant_msgs) < 4:
        return {"error": "消息数不足（至少需要 4 条 assistant 消息）"}

    half = len(assistant_msgs) // 2
    first_half = "".join(assistant_msgs[:half])
    second_half = "".join(assistant_msgs[half:])

    def density(text: str) -> float:
        total = sum(len(text), 0)
        matches = sum(text.count(t) for t in PERSONA_TERMS)
        return matches / max(len(text) / 500, 1)  # 归一化到 500 字

    d1 = density(first_half)
    d2 = density(second_half)
    drift = abs(d2 - d1) / max(d1, 0.1)  # 相对变化率

    verdict = (
        "正常" if drift < 0.3 else
        "轻度漂移" if drift < 0.6 else
        "显著漂移"
    )

    result = {
        "session_id": session_id,
        "first_half_density": round(d1, 4),
        "second_half_density": round(d2, 4),
        "drift_score": round(min(drift, 1.0), 4),
        "verdict": verdict,
        "total_messages": len(assistant_msgs),
        "checked_at": _now_utc(),
    }

    # 追加到漂移日志
    drift_log = _load_json(PERSONA_DRIFT_PATH, {"history": []})
    drift_log["history"].append(result)
    drift_log["history"] = drift_log["history"][-50:]
    drift_log["last_updated"] = _now_utc()
    _save_json(PERSONA_DRIFT_PATH, drift_log)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# 四、CLI 入口
# ─────────────────────────────────────────────────────────────────────────────

def _print_result(name: str, result: Dict[str, Any]) -> None:
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    if "error" in result:
        print(f"  ⚠ {result['error']}")
        return
    if "summary" in result:
        s = result["summary"]
        print(f"  会话: {s.get('session_id', 'N/A')}")
        scores = s.get("overall_scores", {})
        print(f"  综合评分: {scores.get('conversation_overall', 0):.2%}")
        print(f"  通过: {s.get('passed', 0)}/{s.get('messages_evaluated', 0)} 条")
        flags = s.get("flags_summary", [])
        if flags:
            print(f"  警告: {', '.join(flags)}")
    elif "recall_rate" in result:
        print(f"  召回率: {result['recall_rate']:.1%} ({result['num_hits']}/{result['num_facts']})")
        for r in result.get("recall_results", []):
            icon = "✓" if r["hit"] else "✗"
            print(f"    {icon} 查询「{r['query']}」→ {'命中' if r['hit'] else '未命中'}")
    elif "drift_score" in result:
        print(f"  漂移评分: {result['drift_score']:.2f}（{result['verdict']}）")
        print(f"  前半段密度: {result['first_half_density']}")
        print(f"  后半段密度: {result['second_half_density']}")
    else:
        print(f"  {result}")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="林赛交互质量追踪器")
    parser.add_argument("--action", choices=["quality", "memory-test", "persona-drift", "full"],
                       default="full", help="执行的操作")
    parser.add_argument("--session", type=str, default=None, help="指定会话 ID")
    parser.add_argument("--num-facts", type=int, default=5, help="记忆测试fact数量")
    args = parser.parse_args()

    print(f"林赛交互质量追踪器 — {_now_utc()}")
    print(f"Tracker: {TRACKER_PATH}")
    print(f"Memory Test Log: {MEMORY_TEST_PATH}")

    if args.action in ("quality", "full"):
        result = run_quality_check(args.session)
        _print_result("交互质量评估", result)

    if args.action in ("memory-test", "full"):
        result = run_memory_recall_test(num_facts=args.num_facts)
        _print_result("长期记忆召回率测试", result)

    if args.action in ("persona-drift", "full"):
        result = check_persona_drift(args.session)
        _print_result("人格一致性漂移检测", result)

    print(f"\n✓ 所有检测完成 — {_now_utc()}")


if __name__ == "__main__":
    main()
