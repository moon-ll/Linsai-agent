#!/usr/bin/env python3
"""retrospective.py — 定期复盘分析工具（v6.8 林赛协作引擎）

综合分析 debug journal、system kanban、agent scores、tuning log，
从问题聚类、修复有效性、Agent 表现趋势、系统健康趋势等维度输出结构化复盘报告。

数据源:
- memory/debug-journal.json — debug 条目（问题、修复、标签）
- memory/system-kanban.json — 执行历史与失败记录
- memory/agent-scores.json — writer/critic 分数与奖惩记录
- memory/tuning-log.json — 已有调优记录

输出: memory/retrospective-YYYY-MM-DD.md

用法:
    python3 scripts/retrospective.py --period 7d       # 最近 7 天复盘
    python3 scripts/retrospective.py --period 1d        # 最近 1 天复盘
    python3 scripts/retrospective.py --period all       # 全部数据复盘
    python3 scripts/retrospective.py --self-check       # 自检
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────
# 路径与常量
# ─────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
MEMORY_DIR = PROJECT_ROOT / "memory"

DEBUG_JOURNAL_PATH = MEMORY_DIR / "debug-journal.json"
SYSTEM_KANBAN_PATH = MEMORY_DIR / "system-kanban.json"
AGENT_SCORES_PATH = MEMORY_DIR / "agent-scores.json"
TUNING_LOG_PATH = MEMORY_DIR / "tuning-log.json"


# ─────────────────────────────────────────────
# 数据加载
# ─────────────────────────────────────────────

def _load_json(path: Path, default: Any = None) -> Any:
    """加载 JSON 文件，失败时返回 default。"""
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def _parse_period(period_str: str) -> Optional[datetime]:
    """解析周期字符串，返回截止时间（不含）。

    '7d' → 7 天前, '1d' → 1 天前, 'all' → None（不过滤）
    """
    if period_str == "all":
        return None
    m = re.match(r"^(\d+)d$", period_str)
    if m:
        days = int(m.group(1))
        return datetime.now(timezone.utc) - timedelta(days=days)
    return None


def _parse_timestamp(ts: str) -> Optional[datetime]:
    """解析 ISO 时间戳字符串。"""
    if not ts:
        return None
    try:
        # 兼容 'Z' 后缀
        ts_clean = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_clean)
    except Exception:
        return None


def _filter_by_time(
    items: List[Dict], ts_key: str, cutoff: Optional[datetime]
) -> List[Dict]:
    """按时间戳过滤条目。"""
    if cutoff is None:
        return items
    result = []
    for item in items:
        ts = _parse_timestamp(item.get(ts_key, ""))
        if ts and ts >= cutoff:
            result.append(item)
    return result


# ─────────────────────────────────────────────
# 分析维度
# ─────────────────────────────────────────────

def _analyze_problem_clustering(
    entries: List[Dict], cutoff: Optional[datetime]
) -> List[Dict]:
    """问题聚类：按 tag/category 分组，识别重复出现的问题模式。"""
    filtered = _filter_by_time(entries, "timestamp", cutoff)

    # 按 category 分组
    by_category: Dict[str, List[Dict]] = defaultdict(list)
    # 按 tag 分组
    by_tag: Dict[str, List[Dict]] = defaultdict(list)

    for entry in filtered:
        cat = entry.get("category", "unknown")
        by_category[cat].append(entry)
        for tag in entry.get("tags", []):
            by_tag[tag].append(entry)

    # 生成聚类报告
    clusters = []
    for cat, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
        tags_in_cat = Counter()
        for item in items:
            for t in item.get("tags", []):
                tags_in_cat[t] += 1
        clusters.append({
            "category": cat,
            "count": len(items),
            "top_tags": tags_in_cat.most_common(5),
            "entries": [e.get("id", "") for e in items],
        })

    top_tags = []
    for tag, items in sorted(by_tag.items(), key=lambda x: -len(x[1]))[:10]:
        top_tags.append({
            "tag": tag,
            "count": len(items),
            "entries": [e.get("id", "") for e in items],
        })

    return {
        "by_category": clusters,
        "top_tags": top_tags,
        "total_filtered": len(filtered),
    }


def _analyze_fix_effectiveness(
    entries: List[Dict], exec_history: List[Dict], cutoff: Optional[datetime]
) -> Dict:
    """修复有效性：同一 tag 的问题在修复后是否不再出现。"""
    filtered = _filter_by_time(entries, "timestamp", cutoff)

    # 按 tag 收集修复时间线
    tag_fixes: Dict[str, List[Tuple[str, datetime]]] = defaultdict(list)
    for entry in filtered:
        if entry.get("status") == "verified":
            fix_time = _parse_timestamp(entry.get("timestamp", ""))
            if fix_time:
                for tag in entry.get("tags", []):
                    tag_fixes[tag].append((entry.get("id", ""), fix_time))

    # 在执行历史中查找修复后的同类错误
    # 将 exec_history 按 step 关联到 tags（通过关键词映射）
    step_to_tag_keywords = {
        "lit_search": ["literature_service", "json_parser"],
        "critic": ["degradation", "attribute_error"],
        "gap_identify": ["gap_identify", "executor"],
        "writer": ["writer", "ProposalSections", "optimize"],
    }

    results = []
    for tag, fixes in sorted(tag_fixes.items(), key=lambda x: x[1][0][1] if x[1] else datetime.min):
        if not fixes:
            continue
        last_fix_time = max(f[1] for f in fixes)
        # 检查修复后是否有同类错误
        recurrence = False
        recurrence_count = 0
        for hist in exec_history:
            hist_time = _parse_timestamp(hist.get("at", ""))
            if hist_time and hist_time > last_fix_time and not hist.get("success", True):
                step = hist.get("step", "")
                for related_tags in step_to_tag_keywords.values():
                    if tag in related_tags:
                        recurrence = True
                        recurrence_count += 1

        results.append({
            "tag": tag,
            "fix_count": len(fixes),
            "last_fix_id": fixes[-1][0],
            "last_fix_time": last_fix_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "recurrence": recurrence,
            "recurrence_count": recurrence_count,
            "effective": "✓" if not recurrence else "✗",
        })

    return {
        "total_tags_fixed": len(results),
        "effective_count": sum(1 for r in results if r["effective"] == "✓"),
        "ineffective_count": sum(1 for r in results if r["effective"] == "✗"),
        "details": results,
    }


def _analyze_agent_trends(scores_data: Dict, cutoff: Optional[datetime]) -> Dict:
    """Agent 表现趋势：writer/critic 分数随时间变化（按天聚合）。"""
    result: Dict[str, Any] = {"writer": {}, "critic": {}}

    for agent_name in ["writer", "critic"]:
        agent_data = scores_data.get(agent_name, {})
        history = agent_data.get("history", [])
        if not history:
            result[agent_name] = {
                "current_score": agent_data.get("score", 0),
                "initial_score": agent_data.get("initial_score", 100),
                "daily_trend": [],
                "total_changes": 0,
                "positive_count": 0,
                "negative_count": 0,
                "avg_delta": 0,
            }
            continue

        filtered = _filter_by_time(history, "at", cutoff)
        if not filtered:
            filtered = history

        # 按天聚合
        daily: Dict[str, List[float]] = defaultdict(list)
        deltas = []
        positive = 0
        negative = 0

        for h in filtered:
            delta = h.get("delta", 0)
            deltas.append(delta)
            if delta > 0:
                positive += 1
            elif delta < 0:
                negative += 1
            at = _parse_timestamp(h.get("at", ""))
            if at:
                day_key = at.strftime("%Y-%m-%d")
                daily[day_key].append(delta)

        # 计算累计分数趋势
        cumulative = agent_data.get("initial_score", 100)
        daily_trend = []
        for day in sorted(daily.keys()):
            day_sum = sum(daily[day])
            cumulative += day_sum
            daily_trend.append({
                "date": day,
                "delta_sum": round(day_sum, 2),
                "cumulative": round(cumulative, 2),
                "count": len(daily[day]),
            })

        avg_delta = sum(deltas) / len(deltas) if deltas else 0

        result[agent_name] = {
            "current_score": round(agent_data.get("score", 0), 2),
            "initial_score": agent_data.get("initial_score", 100),
            "daily_trend": daily_trend,
            "total_changes": len(filtered),
            "positive_count": positive,
            "negative_count": negative,
            "avg_delta": round(avg_delta, 2),
        }

    return result


def _analyze_system_health(exec_history: List[Dict], cutoff: Optional[datetime]) -> Dict:
    """系统健康趋势：成功率随时间的变化。"""
    filtered = _filter_by_time(exec_history, "at", cutoff)

    if not filtered:
        return {
            "total_jobs": 0,
            "success_rate": 0,
            "daily_breakdown": [],
            "by_step": {},
        }

    # 总体统计
    total = len(filtered)
    success = sum(1 for h in filtered if h.get("success", False))
    success_rate = round(success / total * 100, 1) if total > 0 else 0

    # 按天聚合
    daily: Dict[str, Dict[str, int]] = defaultdict(lambda: {"success": 0, "fail": 0})
    for h in filtered:
        at = _parse_timestamp(h.get("at", ""))
        if at:
            day_key = at.strftime("%Y-%m-%d")
            if h.get("success", False):
                daily[day_key]["success"] += 1
            else:
                daily[day_key]["fail"] += 1

    daily_breakdown = []
    for day in sorted(daily.keys()):
        d = daily[day]
        day_total = d["success"] + d["fail"]
        day_rate = round(d["success"] / day_total * 100, 1) if day_total > 0 else 0
        daily_breakdown.append({
            "date": day,
            "success": d["success"],
            "fail": d["fail"],
            "total": day_total,
            "success_rate": day_rate,
        })

    # 按 step 聚合
    by_step: Dict[str, Dict[str, int]] = defaultdict(lambda: {"success": 0, "fail": 0})
    for h in filtered:
        step = h.get("step", "unknown")
        if h.get("success", False):
            by_step[step]["success"] += 1
        else:
            by_step[step]["fail"] += 1

    step_summary = {}
    for step, counts in sorted(by_step.items()):
        s_total = counts["success"] + counts["fail"]
        s_rate = round(counts["success"] / s_total * 100, 1) if s_total > 0 else 0
        step_summary[step] = {
            "success": counts["success"],
            "fail": counts["fail"],
            "total": s_total,
            "success_rate": s_rate,
        }

    return {
        "total_jobs": total,
        "success_count": success,
        "fail_count": total - success,
        "success_rate": success_rate,
        "daily_breakdown": daily_breakdown,
        "by_step": step_summary,
    }


def _generate_action_suggestions(
    clustering: Dict,
    fix_eff: Dict,
    agent_trends: Dict,
    health: Dict,
) -> List[Dict]:
    """基于以上分析生成具体的行动建议。"""
    suggestions = []

    # 1. 从重复出现的问题模式中生成建议
    for cluster in clustering.get("by_category", []):
        if cluster["count"] >= 3:
            suggestions.append({
                "priority": "high",
                "type": "代码修改",
                "category": cluster["category"],
                "description": (
                    f"问题类别 '{cluster['category']}' 在周期内出现 {cluster['count']} 次，"
                    f"高频标签：{', '.join(t[0] + '(' + str(t[1]) + ')' for t in cluster['top_tags'][:3])}。"
                    f"建议系统性排查此类问题的根因，增加针对性单元测试。"
                ),
            })

    # 2. 修复无效的建议
    for detail in fix_eff.get("details", []):
        if detail["effective"] == "✗":
            suggestions.append({
                "priority": "high",
                "type": "代码修改",
                "category": detail["tag"],
                "description": (
                    f"标签 '{detail['tag']}' 的修复无效——修复后仍有 {detail['recurrence_count']} 次复发。"
                    f"需重新评估修复方案是否触及根因。"
                ),
            })

    # 3. Agent 表现趋势建议
    for agent in ["writer", "critic"]:
        trends = agent_trends.get(agent, {})
        avg_delta = trends.get("avg_delta", 0)
        negative_count = trends.get("negative_count", 0)
        total = trends.get("total_changes", 0)
        if total > 0 and negative_count / total > 0.5:
            suggestions.append({
                "priority": "high",
                "type": "prompt 调整",
                "category": agent,
                "description": (
                    f"{agent} 的负面评分占比 {round(negative_count / total * 100, 1)}% "
                    f"（平均 delta: {avg_delta}），"
                    f"建议优化 {agent} 的 prompt 模板，强化指令明确性。"
                ),
            })
        elif avg_delta < -3:
            suggestions.append({
                "priority": "medium",
                "type": "prompt 调整",
                "category": agent,
                "description": (
                    f"{agent} 的平均 delta 为 {avg_delta}，趋势偏负，"
                    f"建议审查最近的评审反馈，调整 {agent} prompt 中的行为约束。"
                ),
            })

    # 4. 系统健康建议
    by_step = health.get("by_step", {})
    for step, counts in by_step.items():
        if counts["success_rate"] < 70 and counts["total"] >= 3:
            suggestions.append({
                "priority": "high" if counts["success_rate"] < 50 else "medium",
                "type": "配置变更" if step == "critic" else "监控增强",
                "category": step,
                "description": (
                    f"步骤 '{step}' 成功率仅 {counts['success_rate']}%"
                    f"（{counts['fail']}/{counts['total']} 失败），"
                    f"建议{'增加超时时间/重试机制' if step in ('critic', 'writer') else '增强前置检查与错误处理'}。"
                ),
            })

    # 5. 总体健康趋势建议
    daily = health.get("daily_breakdown", [])
    if len(daily) >= 3:
        recent_rates = [d["success_rate"] for d in daily[-3:]]
        if all(r < recent_rates[0] for r in recent_rates[1:]):
            suggestions.append({
                "priority": "medium",
                "type": "监控增强",
                "category": "系统全局",
                "description": (
                    f"系统成功率呈下降趋势（近 3 天：{recent_rates}），"
                    f"建议加强 daily health check，排查是否有外部依赖劣化。"
                ),
            })

    # 按优先级排序
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: priority_order.get(x["priority"], 99))

    return suggestions


# ─────────────────────────────────────────────
# 报告生成
# ─────────────────────────────────────────────

def _format_report(
    period_str: str,
    cutoff: Optional[datetime],
    clustering: Dict,
    fix_eff: Dict,
    agent_trends: Dict,
    health: Dict,
    suggestions: List[Dict],
    tuning_log: List,
) -> str:
    """格式化 Markdown 复盘报告。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    period_desc = f"最近 {period_str}" if period_str != "all" else "全部数据"
    cutoff_desc = cutoff.strftime("%Y-%m-%d %H:%M UTC") if cutoff else "无限制"

    lines = [
        f"# 复盘报告 — {period_desc}",
        "",
        f"> 生成时间：{now}",
        f"> 时间窗口：{cutoff_desc} 至今",
        "",
    ]

    # ── 1. 问题聚类 ──
    lines.append("## 1. 问题聚类")
    lines.append("")
    cl = clustering
    lines.append(f"**周期内 debug 条目总数**：{cl.get('total_filtered', 0)}")
    lines.append("")

    lines.append("### 按类别分组")
    lines.append("")
    lines.append("| 类别 | 数量 | 高频标签 |")
    lines.append("|------|------|----------|")
    for c in cl.get("by_category", []):
        tags_str = ", ".join(f"{t[0]}({t[1]})" for t in c["top_tags"][:3])
        lines.append(f"| {c['category']} | {c['count']} | {tags_str} |")
    lines.append("")

    lines.append("### 高频标签 TOP 10")
    lines.append("")
    lines.append("| 标签 | 出现次数 | 关联条目 |")
    lines.append("|------|----------|----------|")
    for t in cl.get("top_tags", []):
        entries_str = ", ".join(t["entries"][:3])
        lines.append(f"| {t['tag']} | {t['count']} | {entries_str} |")
    lines.append("")

    # ── 2. 修复有效性 ──
    lines.append("## 2. 修复有效性")
    lines.append("")
    fe = fix_eff
    lines.append(
        f"**已修复标签数**：{fe.get('total_tags_fixed', 0)} | "
        f"有效：{fe.get('effective_count', 0)} | "
        f"无效：{fe.get('ineffective_count', 0)}"
    )
    lines.append("")

    if fe.get("details"):
        lines.append("| 标签 | 修复次数 | 最后修复 | 复发 | 判定 |")
        lines.append("|------|----------|----------|------|------|")
        for d in fe["details"]:
            lines.append(
                f"| {d['tag']} | {d['fix_count']} | "
                f"{d['last_fix_id']} ({d['last_fix_time']}) | "
                f"{'是(' + str(d['recurrence_count']) + ')' if d['recurrence'] else '否'} | "
                f"{d['effective']} |"
            )
        lines.append("")

    # ── 3. Agent 表现趋势 ──
    lines.append("## 3. Agent 表现趋势")
    lines.append("")

    for agent in ["writer", "critic"]:
        at = agent_trends.get(agent, {})
        lines.append(f"### {agent.capitalize()}")
        lines.append("")
        lines.append(
            f"- **当前分数**：{at.get('current_score', 0)} "
            f"（初始：{at.get('initial_score', 100)}）"
        )
        lines.append(
            f"- **总变化次数**：{at.get('total_changes', 0)} | "
            f"正面：{at.get('positive_count', 0)} | "
            f"负面：{at.get('negative_count', 0)} | "
            f"平均 delta：{at.get('avg_delta', 0)}"
        )
        lines.append("")

        daily_trend = at.get("daily_trend", [])
        if daily_trend:
            lines.append("| 日期 | 日 delta | 累计分数 | 变化次数 |")
            lines.append("|------|---------|----------|----------|")
            for d in daily_trend:
                lines.append(
                    f"| {d['date']} | {d['delta_sum']:+.2f} | "
                    f"{d['cumulative']:.2f} | {d['count']} |"
                )
            lines.append("")

    # ── 4. 系统健康趋势 ──
    lines.append("## 4. 系统健康趋势")
    lines.append("")
    h = health
    lines.append(
        f"- **总任务数**：{h.get('total_jobs', 0)} | "
        f"成功：{h.get('success_count', 0)} | "
        f"失败：{h.get('fail_count', 0)} | "
        f"成功率：{h.get('success_rate', 0)}%"
    )
    lines.append("")

    daily_bd = h.get("daily_breakdown", [])
    if daily_bd:
        lines.append("### 每日成功率")
        lines.append("")
        lines.append("| 日期 | 成功 | 失败 | 总计 | 成功率 |")
        lines.append("|------|------|------|------|--------|")
        for d in daily_bd:
            lines.append(
                f"| {d['date']} | {d['success']} | {d['fail']} | "
                f"{d['total']} | {d['success_rate']}% |"
            )
        lines.append("")

    by_step = h.get("by_step", {})
    if by_step:
        lines.append("### 按步骤成功率")
        lines.append("")
        lines.append("| 步骤 | 成功 | 失败 | 总计 | 成功率 |")
        lines.append("|------|------|------|------|--------|")
        for step, counts in by_step.items():
            lines.append(
                f"| {step} | {counts['success']} | {counts['fail']} | "
                f"{counts['total']} | {counts['success_rate']}% |"
            )
        lines.append("")

    # ── 5. 已有调优记录 ──
    lines.append("## 5. 已有调优记录")
    lines.append("")
    if tuning_log:
        lines.append(f"**调优记录总数**：{len(tuning_log)}")
        lines.append("")
        lines.append("| 时间 | 确认方式 | 变更内容 |")
        lines.append("|------|----------|----------|")
        for t in tuning_log[-10:]:  # 最多显示 10 条
            at_str = t.get("at", "")
            confirmed = t.get("confirmed_by", "")
            old_val = json.dumps(t.get("old", {}), ensure_ascii=False)
            new_val = json.dumps(t.get("new", {}), ensure_ascii=False)
            lines.append(f"| {at_str} | {confirmed} | {old_val} → {new_val} |")
        lines.append("")
    else:
        lines.append("暂无调优记录。")
        lines.append("")

    # ── 6. 行动建议 ──
    lines.append("## 6. 行动建议")
    lines.append("")

    if suggestions:
        priority_icon = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}
        for i, s in enumerate(suggestions, 1):
            icon = priority_icon.get(s["priority"], "")
            lines.append(f"### {i}. {icon} {s['type']} — {s['category']}")
            lines.append("")
            lines.append(s["description"])
            lines.append("")
    else:
        lines.append("当前周期内无显著问题，系统运行平稳。")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 主逻辑
# ─────────────────────────────────────────────

def run_retrospective(period_str: str = "7d") -> Path:
    """执行复盘分析，生成报告文件。

    Args:
        period_str: 时间周期（'7d'/'1d'/'all'）

    Returns:
        生成的报告文件路径
    """
    cutoff = _parse_period(period_str)

    # 加载数据
    debug_journal = _load_json(DEBUG_JOURNAL_PATH)
    system_kanban = _load_json(SYSTEM_KANBAN_PATH)
    agent_scores = _load_json(AGENT_SCORES_PATH)
    tuning_log = _load_json(TUNING_LOG_PATH, [])

    entries = debug_journal.get("entries", [])
    exec_history = system_kanban.get("execution_history", [])

    # 执行分析
    clustering = _analyze_problem_clustering(entries, cutoff)
    fix_eff = _analyze_fix_effectiveness(entries, exec_history, cutoff)
    agent_trends = _analyze_agent_trends(agent_scores, cutoff)
    health = _analyze_system_health(exec_history, cutoff)
    suggestions = _generate_action_suggestions(clustering, fix_eff, agent_trends, health)

    # 生成报告
    report_md = _format_report(
        period_str, cutoff, clustering, fix_eff,
        agent_trends, health, suggestions, tuning_log,
    )

    # 写入文件
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = MEMORY_DIR / f"retrospective-{today}.md"
    output_path.write_text(report_md, encoding="utf-8")

    print(f"✓ 复盘报告已生成：{output_path}")
    print(f"  时间窗口：{'全部数据' if cutoff is None else cutoff.strftime('%Y-%m-%d')} 至今")
    print(f"  debug 条目：{clustering['total_filtered']}")
    print(f"  执行任务数：{health['total_jobs']}")
    print(f"  成功率：{health['success_rate']}%")
    print(f"  行动建议：{len(suggestions)} 条")

    return output_path


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> None:
    """自检：验证脚本基本功能正确。"""
    print("=== retrospective._self_check ===")

    # 1. 模块导入检查
    assert PROJECT_ROOT.exists(), f"PROJECT_ROOT 不存在：{PROJECT_ROOT}"
    assert MEMORY_DIR.exists(), f"MEMORY_DIR 不存在：{MEMORY_DIR}"
    print("  ✓ 路径常量正确")

    # 2. 数据文件检查
    for path, name in [
        (DEBUG_JOURNAL_PATH, "debug-journal.json"),
        (SYSTEM_KANBAN_PATH, "system-kanban.json"),
        (AGENT_SCORES_PATH, "agent-scores.json"),
        (TUNING_LOG_PATH, "tuning-log.json"),
    ]:
        if path.exists():
            data = _load_json(path)
            print(f"  ✓ {name} 加载成功（类型：{type(data).__name__}）")
        else:
            print(f"  ○ {name} 不存在（将使用默认值）")

    # 3. 周期解析测试
    assert _parse_period("7d") is not None
    assert _parse_period("1d") is not None
    assert _parse_period("all") is None
    assert _parse_period("invalid") is None
    print("  ✓ 周期解析正确")

    # 4. 时间戳解析测试
    assert _parse_timestamp("2026-08-05T10:00:00Z") is not None
    assert _parse_timestamp("") is None
    assert _parse_timestamp("invalid") is None
    print("  ✓ 时间戳解析正确")

    # 5. 分析函数测试（加载真实数据）
    debug_journal = _load_json(DEBUG_JOURNAL_PATH)
    entries = debug_journal.get("entries", [])
    if entries:
        clustering = _analyze_problem_clustering(entries, None)
        assert "by_category" in clustering
        assert "top_tags" in clustering
        print(f"  ✓ 问题聚类分析正常（{clustering['total_filtered']} 条目）")

        system_kanban = _load_json(SYSTEM_KANBAN_PATH)
        exec_history = system_kanban.get("execution_history", [])
        fix_eff = _analyze_fix_effectiveness(entries, exec_history, None)
        assert "details" in fix_eff
        print(f"  ✓ 修复有效性分析正常（{fix_eff['total_tags_fixed']} 标签已修复）")

    agent_scores = _load_json(AGENT_SCORES_PATH)
    agent_trends = _analyze_agent_trends(agent_scores, None)
    assert "writer" in agent_trends
    assert "critic" in agent_trends
    print(f"  ✓ Agent 趋势分析正常（writer: {agent_trends['writer']['total_changes']} 变化）")

    system_kanban = _load_json(SYSTEM_KANBAN_PATH)
    exec_history = system_kanban.get("execution_history", [])
    health = _analyze_system_health(exec_history, None)
    assert "total_jobs" in health
    assert "success_rate" in health
    print(f"  ✓ 系统健康分析正常（{health['total_jobs']} 任务，{health['success_rate']}% 成功率）")

    suggestions = _generate_action_suggestions(
        clustering if entries else {"by_category": [], "top_tags": []},
        fix_eff if entries else {"details": [], "total_tags_fixed": 0,
                                "effective_count": 0, "ineffective_count": 0},
        agent_trends,
        health,
    )
    print(f"  ✓ 行动建议生成正常（{len(suggestions)} 条）")

    # 6. 报告生成测试
    report_md = _format_report(
        "1d",
        datetime.now(timezone.utc) - timedelta(days=1),
        clustering if entries else {"by_category": [], "top_tags": [], "total_filtered": 0},
        fix_eff if entries else {"details": [], "total_tags_fixed": 0,
                                 "effective_count": 0, "ineffective_count": 0},
        agent_trends,
        health,
        suggestions,
        [],
    )
    assert "# 复盘报告" in report_md
    assert "## 1. 问题聚类" in report_md
    assert "## 6. 行动建议" in report_md
    print("  ✓ 报告格式正确（6 个章节完整）")

    print("=== 通过 ===")


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="LinSai-CoPilot 定期复盘分析工具"
    )
    parser.add_argument(
        "--period",
        type=str,
        default="7d",
        help="复盘周期：'7d'（7天）、'1d'（1天）、'all'（全部）",
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="运行自检",
    )

    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        run_retrospective(args.period)


if __name__ == "__main__":
    main()
