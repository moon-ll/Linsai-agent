#!/usr/bin/env python3
"""retrospective.py — 定期复盘分析工具（v6.8 林赛协作引擎）

综合分析 debug journal、system kanban、agent scores、tuning log，
从问题聚类、修复有效性、Agent 表现趋势、系统健康趋势等维度输出结构化复盘报告。

数据源:
- memory/debug-journal.json — debug 条目（问题、修复、标签）【历史死源：2026-09-02 后零新增】
- memory/system-kanban.json — 执行历史与失败记录
- memory/agent-scores.json — writer/critic 分数与奖惩记录
- memory/tuning-log.json — 已有调优记录
- memory/weekend-reflection/ — 周末反思产出（patterns、next_actions、健康报告）
- memory/weekend-input/ — 周末输入端产出（ideas、decisions、directions）
- 【v7.2.62 活数据源】memory/usage/step-usage-YYYY-MM.jsonl — LLM 调用账本（月分片 JSONL）
- 【v7.2.62 活数据源】research_proposals/_lifecycle.json — 课题评分/未决问题/轮次时间戳
- 【v7.2.62 活数据源】CHANGELOG.md — 版本头 + BUG-Nn 编号（BUG 速率口径）
- 【v7.2.62 活数据源】memory/system-kanban.json — execution_history（机时经济学）

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
import tempfile
import time
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
WEEKEND_REFLECTION_DIR = MEMORY_DIR / "weekend-reflection"
WEEKEND_INPUT_DIR = MEMORY_DIR / "weekend-input"

# v7.2.62 活账本数据源（retrospective 活数据源重建）
USAGE_DIR = MEMORY_DIR / "usage"
LIFECYCLE_PATH = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
CHANGELOG_PATH = PROJECT_ROOT / "CHANGELOG.md"

# v7.2.62 活账本阈值（超限触发 ⚠ 并生成行动建议）
LIVE_THRESHOLD_CALL_FAIL_PCT = 15.0   # 调用失败率 > 15% → ⚠
LIVE_THRESHOLD_BUG_PER_DAY = 0.5      # BUG 修复速率 > 0.5 个/天 → ⚠
LIVE_THRESHOLD_WHACK_PCT = 30.0       # 打地鼠率 > 30% → ⚠
LIVE_THRESHOLD_CAP_SHAVE = 0.02       # cap 平均削幅 > 0.02 → ⚠


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


def _load_weekend_reflections(cutoff: Optional[datetime]) -> Dict[str, Any]:
    """加载周末反思产出，整合最近的分析结果。

    读取 weekend-reflection/ 目录下的：
    - weekend-reflection-*.json（反思报告，含 patterns + next_actions）
    - analyzed-patterns-*.json（模式分析）
    - collected-state-*.json（收集的原始状态）
    - reflection-health-*.json（健康检查快照）

    以及 weekend-input/ 目录下的：
    - ideas-*.json / decisions-*.json / directions-*.json
    """
    result: Dict[str, Any] = {
        "patterns": [],
        "next_actions": [],
        "health_snapshots": [],
        "ideas": [],
        "decisions": [],
        "directions": [],
        "latest_report": None,
    }

    # 加载反思报告
    if WEEKEND_REFLECTION_DIR.exists():
        for f in sorted(WEEKEND_REFLECTION_DIR.glob("weekend-reflection-*.json"), reverse=True):
            try:
                data = _load_json(f)
                ts = _parse_timestamp(data.get("generated_at", ""))
                if cutoff and ts and ts < cutoff:
                    continue
                # 只保留最新一份完整报告
                if result["latest_report"] is None:
                    result["latest_report"] = data
                # 合并 patterns 和 next_actions
                for p in data.get("patterns", []):
                    result["patterns"].append(p)
                for a in data.get("next_actions", []):
                    result["next_actions"].append(a)
            except Exception:
                continue

        # 健康快照
        for f in sorted(WEEKEND_REFLECTION_DIR.glob("reflection-health-*.json"), reverse=True)[:5]:
            try:
                data = _load_json(f)
                ts = _parse_timestamp(data.get("checked_at", ""))
                if cutoff and ts and ts < cutoff:
                    continue
                result["health_snapshots"].append({
                    "checked_at": data.get("checked_at", ""),
                    "status": data.get("status", ""),
                    "alerts": data.get("alerts", {}),
                    "optimizing": data.get("proposals", {}).get("optimizing", 0),
                    "failed_jobs": data.get("pipeline_failed_jobs", 0),
                })
            except Exception:
                continue

    # 加载输入端产出
    if WEEKEND_INPUT_DIR.exists():
        for pattern, key in [
            ("ideas-*.json", "ideas"),
            ("decisions-*.json", "decisions"),
            ("directions-*.json", "directions"),
        ]:
            for f in sorted(WEEKEND_INPUT_DIR.glob(pattern), reverse=True)[:3]:
                try:
                    data = _load_json(f)
                    ts = _parse_timestamp(data.get("generated_at", ""))
                    if cutoff and ts and ts < cutoff:
                        continue
                    actions = data.get("actions", [])
                    if isinstance(actions, list):
                        result[key].extend(actions[:10])  # 每份最多取 10 条
                except Exception:
                    continue

    return result


def _analyze_weekend_reflections(reflections: Dict[str, Any]) -> Dict[str, Any]:
    """分析周末反思产出，提取可操作的洞察。"""
    analysis: Dict[str, Any] = {
        "pattern_count": len(reflections.get("patterns", [])),
        "action_count": len(reflections.get("next_actions", [])),
        "top_patterns": [],
        "actionable_items": [],
        "ideas_count": len(reflections.get("ideas", [])),
        "decisions_count": len(reflections.get("decisions", [])),
        "directions_count": len(reflections.get("directions", [])),
        "health_trend": [],
    }

    # 模式重要性排序
    patterns = reflections.get("patterns", [])
    sorted_patterns = sorted(
        patterns,
        key=lambda p: p.get("severity", "").lower() in ("critical", "high"),
        reverse=True,
    )
    analysis["top_patterns"] = sorted_patterns[:5]

    # 可执行的行动建议
    for action in reflections.get("next_actions", []):
        if isinstance(action, str):
            analysis["actionable_items"].append(action)
        elif isinstance(action, dict):
            analysis["actionable_items"].append(action.get("description", str(action)))

    # 健康趋势
    for snap in reflections.get("health_snapshots", []):
        analysis["health_trend"].append(snap)

    # 最新报告概要
    latest = reflections.get("latest_report")
    if latest:
        analysis["latest_report_at"] = latest.get("generated_at", "")

    return analysis


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


# ─────────────────────────────────────────────
# 活账本分析（v7.2.62）
#
# 背景：原三个数据源中 memory/debug-journal.json 已死（2026-09-02 后零新增），
# 连续数周报告输出「debug 条目总数：0」。本模块改读四类活数据源：
#   1. memory/usage/step-usage-YYYY-MM.jsonl — LLM 调用账本（月分片 JSONL，
#      实测字段：ts/kind/name/provider/model/success/error/elapsed_s 等）
#   2. research_proposals/_lifecycle.json — 课题生命周期（score_history /
#      open_critical_issues；score_raw、recurrence_count 为 v7.2.62 新字段）
#   3. CHANGELOG.md — 版本头 `## vX.Y.Z - 日期 描述` + BUG-Nn 编号
#   4. memory/system-kanban.json — execution_history
# 全部计算确定性零 LLM，缺字段/缺文件 fail-open（返回带 warning 的空结构）。
# ─────────────────────────────────────────────

# CHANGELOG 版本头：## v7.2.62 - 2026-10-30 描述文字
_CHANGELOG_VERSION_RE = re.compile(r"^##\s+v\d+(?:\.\d+)+\s+-\s+(\d{4}-\d{2}-\d{2})\s*(.*)$")
# BUG 编号：BUG-24（正文与版本头均可能出现）
_BUG_ID_RE = re.compile(r"BUG-(\d+)")


def _classify_usage_error(error: str) -> str:
    """把 step_usage 的 error 文本归一为短类别（超时/限流/服务端/客户端/原文截断）。

    实测失败样本：
    - '✗ minimax: The read operation timed out' → 超时
    - '✗ minimax: API HTTP 429: {...rate_limit_error...}' → HTTP 429 限流
    - '✗ minimax: API HTTP 529: {...overloaded_error...}' → HTTP 5xx 服务端
    - '✗ glm: API 返回空 content（finish_...' → API 空响应（实测 TOP 失败模式，218 次/7 天）
    - 'hermes agent 超时（30s）' → 超时
    """
    e = (error or "").strip()
    if not e:
        return "未知错误"
    if "timed out" in e or "超时" in e:
        return "超时"
    if "HTTP 429" in e or "rate_limit" in e:
        return "HTTP 429 限流"
    if "HTTP 5" in e:
        return "HTTP 5xx 服务端"
    if "HTTP 4" in e:
        return "HTTP 4xx 客户端"
    if "空 content" in e or "empty" in e.lower():
        return "API 空响应"
    return e[:30] + "…" if len(e) > 30 else e


def _step_usage_month_files(usage_dir: Path, now: datetime) -> List[Path]:
    """当月 + 上月的 step_usage 分片路径（按 now 推导，供测试注入固定时间）。"""
    files = []
    for offset in (0, 1):
        month = now - timedelta(days=31 * offset)
        files.append(usage_dir / f"step-usage-{month.strftime('%Y-%m')}.jsonl")
    return files


def _analyze_call_health(
    usage_dir: Path, cutoff: Optional[datetime], now: datetime
) -> Tuple[Dict, List[str]]:
    """调用健康：当月+上月 step_usage JSONL 流式逐行统计。

    返回 (指标, warnings)。字段口径按实测 JSONL（kind/name 组合充当 step 标签，
    账本无独立 step 字段）。坏行计数跳过，不中断。
    """
    warnings: List[str] = []
    total = failed = timeout_count = parse_errors = 0
    fail_counter: Counter = Counter()
    files_read: List[str] = []

    for path in _step_usage_month_files(usage_dir, now):
        if not path.exists():
            continue
        files_read.append(path.name)
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except Exception:
                        parse_errors += 1
                        continue
                    if not isinstance(entry, dict):
                        parse_errors += 1
                        continue
                    ts = _parse_timestamp(str(entry.get("ts", "")))
                    if cutoff is not None and (ts is None or ts < cutoff):
                        continue
                    total += 1
                    if not entry.get("success", True):
                        failed += 1
                        step_label = f"{entry.get('kind', 'unknown')}:{entry.get('name', 'unknown')}"
                        err_cls = _classify_usage_error(str(entry.get("error", "")))
                        if err_cls == "超时":
                            timeout_count += 1
                        fail_counter[(step_label, err_cls)] += 1
        except Exception as exc:
            warnings.append(f"step_usage 分片读取失败 {path.name}：{exc}")

    if not files_read:
        warnings.append(f"step_usage 当月/上月分片均不存在（{usage_dir}）")
    if parse_errors:
        warnings.append(f"step_usage 有 {parse_errors} 行无法解析（已跳过）")

    top_failures = [
        {"step": k[0], "error": k[1], "count": v}
        for k, v in fail_counter.most_common(3)
    ]
    rate = round(failed / total * 100, 1) if total else 0.0
    return {
        "files_read": files_read,
        "total_calls": total,
        "failed_calls": failed,
        "failure_rate": rate,
        "top_failures": top_failures,
        "timeout_failures": timeout_count,
    }, warnings


def _analyze_bug_velocity(
    changelog_path: Path, cutoff: Optional[datetime], period_days: int
) -> Tuple[Dict, List[str]]:
    """BUG 速率：解析 CHANGELOG 版本头 + BUG-Nn 编号。

    口径（确定性，CHANGELOG 为唯一线索源）：
    - 修复 = 某版本头同时含 'BUG-N' 与 '修复'（CHANGELOG 倒序，取最新满足者）；
    - 引入线索 = BUG-N 在 CHANGELOG 任意位置（含更早版本正文）的最早出现日期；
    - 引入-修复间隔可考 = 引入线索与修复日期均存在且间隔 ≥ 0 天。
    """
    warnings: List[str] = []
    bug_first_seen: Dict[str, datetime] = {}
    bug_fixed_at: Dict[str, datetime] = {}
    versions_total = 0
    versions_in_period = 0

    if not changelog_path.exists():
        warnings.append(f"CHANGELOG 不存在：{changelog_path}")
    else:
        v_date: Optional[datetime] = None  # 当前行所属版本日期（正文提及归属用）
        try:
            with changelog_path.open("r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    m = _CHANGELOG_VERSION_RE.match(stripped)
                    if m:
                        versions_total += 1
                        try:
                            v_date = datetime.strptime(
                                m.group(1), "%Y-%m-%d"
                            ).replace(tzinfo=timezone.utc)
                        except ValueError:
                            v_date = None
                        if v_date is not None and (cutoff is None or v_date >= cutoff):
                            versions_in_period += 1
                        header_rest = m.group(2)
                        if v_date is not None:
                            for bug_id in _BUG_ID_RE.findall(header_rest):
                                if bug_id not in bug_first_seen or (
                                    v_date < bug_first_seen[bug_id]
                                ):
                                    bug_first_seen[bug_id] = v_date
                                if "修复" in header_rest and bug_id not in bug_fixed_at:
                                    bug_fixed_at[bug_id] = v_date
                        continue
                    # 版本正文内的 BUG 提及也算引入线索（需归属当前版本日期）
                    if m is None:
                        # 用最近的版本日期归属（首个版本头之前的行忽略）
                        for bug_id in _BUG_ID_RE.findall(stripped):
                            if bug_id in bug_first_seen:
                                if v_date is not None and v_date < bug_first_seen[bug_id]:
                                    bug_first_seen[bug_id] = v_date
                            else:
                                if v_date is not None:
                                    bug_first_seen[bug_id] = v_date
        except Exception as exc:
            warnings.append(f"CHANGELOG 读取失败：{exc}")

    fixed_in_period = {
        b: d for b, d in bug_fixed_at.items() if cutoff is None or d >= cutoff
    }
    intervals: List[Tuple[str, int]] = []
    for bug_id, fix_d in fixed_in_period.items():
        seen_d = bug_first_seen.get(bug_id)
        if seen_d is not None and fix_d >= seen_d:
            intervals.append((bug_id, (fix_d - seen_d).days))

    velocity = (
        round(len(fixed_in_period) / period_days, 3) if period_days > 0 else 0.0
    )
    avg_interval = (
        round(sum(i for _, i in intervals) / len(intervals), 1) if intervals else None
    )
    return {
        "bugs_fixed_in_period": len(fixed_in_period),
        "bug_ids": sorted(fixed_in_period.keys(), key=lambda x: int(x)),
        "bug_velocity_per_day": velocity,
        "interval_known": len(intervals),
        "avg_interval_days": avg_interval,
        "interval_details": [
            {"bug": b, "days": d} for b, d in sorted(intervals, key=lambda x: -x[1])[:5]
        ],
        "versions_in_period": versions_in_period,
        "versions_total": versions_total,
    }, warnings


def _analyze_whack_a_mole(lifecycle: Dict) -> Dict:
    """打地鼠率：open_critical_issues 中 recurrence_count≥1 的条目占比。

    recurrence_count 为 v7.2.62 新字段，历史条目缺失时按 0 处理并在 note 注明
    「该指标自 v7.2.62 起累积」（全量口径，不分周期——issue 无时间戳字段）。
    """
    total = recurrent = missing_field = 0
    recurrences: List[Dict] = []
    for pid, p in lifecycle.get("proposals", {}).items():
        if not isinstance(p, dict):
            continue
        for issue in p.get("open_critical_issues", []) or []:
            if not isinstance(issue, dict):
                continue
            total += 1
            if "recurrence_count" not in issue:
                missing_field += 1
            try:
                rc = int(issue.get("recurrence_count", 0) or 0)
            except (TypeError, ValueError):
                rc = 0
            if rc >= 1:
                recurrent += 1
                desc = str(issue.get("description", "")).strip().replace("\n", " ")
                if len(desc) > 48:
                    desc = desc[:48] + "…"
                recurrences.append({
                    "proposal": pid,
                    "description": desc or f"{pid} 未命名问题",
                    "count": rc,
                })
    recurrences.sort(key=lambda x: -x["count"])
    rate = round(recurrent / total * 100, 1) if total else 0.0
    note = ""
    if missing_field > 0:
        note = (
            f"该指标自 v7.2.62 起累积：{missing_field} 条历史条目无 "
            f"recurrence_count 字段，按 0 处理"
        )
    return {
        "total_issues": total,
        "recurrent_issues": recurrent,
        "rate_pct": rate,
        "top_recurrences": recurrences[:3],
        "missing_field_count": missing_field,
        "note": note,
    }


def _is_num(v: Any) -> bool:
    """数值判定（排除 bool——bool 是 int 子类）。"""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _analyze_cap_shaving(lifecycle: Dict) -> Dict:
    """cap 削幅：score_history 中含 score_raw 字段条目的封顶削减统计。

    削幅定义 = score_raw − score（原始分高于封顶后得分，正值表示被削）。
    贴顶分布 = score 恰为 0.75/0.80/0.85（容差 1e-6）的条数。
    无 score_raw 的条目（v7.2.62 前历史）跳过并注明覆盖率。全量口径。
    """
    total_entries = eligible = capped = 0
    shave_sum = 0.0
    cap_hits = {"0.75": 0, "0.80": 0, "0.85": 0}

    for p in lifecycle.get("proposals", {}).values():
        if not isinstance(p, dict):
            continue
        for s in p.get("score_history", []) or []:
            if not isinstance(s, dict):
                continue
            total_entries += 1
            raw = s.get("score_raw")
            score = s.get("score")
            if not _is_num(raw) or not _is_num(score):
                continue
            eligible += 1
            shave = float(raw) - float(score)
            shave_sum += shave
            if shave > 1e-9 or s.get("cap_applied") is True:
                capped += 1
            for cv in (0.75, 0.80, 0.85):
                if abs(float(score) - cv) < 1e-6:
                    cap_hits[f"{cv:.2f}"] += 1

    avg_shave = round(shave_sum / eligible, 4) if eligible else 0.0
    capped_ratio = round(capped / eligible * 100, 1) if eligible else 0.0
    coverage = round(eligible / total_entries * 100, 1) if total_entries else 0.0
    note = ""
    if eligible == 0 and total_entries > 0:
        note = (
            f"score_history 共 {total_entries} 条均无 score_raw 字段"
            f"（v7.2.62 新字段，等待生产者写入），本指标暂不可考"
        )
    return {
        "total_score_history": total_entries,
        "eligible": eligible,
        "coverage_pct": coverage,
        "avg_shave": avg_shave,
        "capped_count": capped,
        "capped_ratio_pct": capped_ratio,
        "cap_hits": cap_hits,
        "note": note,
    }


def _analyze_machine_hours(
    lifecycle: Dict, kanban: Dict, cutoff: Optional[datetime], period_days: int
) -> Dict:
    """机时经济学：周期内新增评分轮次 / 活跃课题数 / 日均轮次（+看板执行事件）。"""
    rounds = 0
    active_pids = set()
    for pid, p in lifecycle.get("proposals", {}).items():
        if not isinstance(p, dict):
            continue
        for s in p.get("score_history", []) or []:
            if not isinstance(s, dict):
                continue
            at = _parse_timestamp(str(s.get("at", "")))
            if at is None:
                continue
            if cutoff is not None and at < cutoff:
                continue
            rounds += 1
            active_pids.add(pid)

    kanban_events = 0
    kanban_pids = set()
    for h in kanban.get("execution_history", []) or []:
        if not isinstance(h, dict):
            continue
        at = _parse_timestamp(str(h.get("at", "")))
        if at is None:
            continue
        if cutoff is not None and at < cutoff:
            continue
        kanban_events += 1
        pid = h.get("proposal_id", "")
        if pid:
            kanban_pids.add(pid)

    daily = round(rounds / period_days, 2) if period_days > 0 else 0.0
    return {
        "rounds_in_period": rounds,
        "active_proposals": len(active_pids),
        "daily_rounds": daily,
        "kanban_exec_events": kanban_events,
        "kanban_active_proposals": len(kanban_pids),
    }


def _load_lifecycle(lifecycle_path: Path, warnings: List[str]) -> Dict:
    """加载 _lifecycle.json（约 1.9MB）。

    实测该文件由多个 worker cron 并发原子替换写入，读取时存在瞬时不一致窗口
    （本机 2026-10-30 实测偶发 JSONDecodeError，重读即成功），故解析失败时
    短暂重试 3 次，仍失败则 fail-open 返回空 dict 并记 warning。
    """
    if not lifecycle_path.exists():
        warnings.append(f"_lifecycle.json 不存在：{lifecycle_path}")
        return {}
    for attempt in range(3):
        try:
            return json.loads(lifecycle_path.read_text(encoding="utf-8"))
        except Exception:
            if attempt < 2:
                time.sleep(0.1)
                continue
    warnings.append("_lifecycle.json 解析失败（并发写入窗口或格式异常），生命周期侧指标降级")
    return {}


def _empty_call_health() -> Dict:
    return {
        "files_read": [],
        "total_calls": 0,
        "failed_calls": 0,
        "failure_rate": 0.0,
        "top_failures": [],
        "timeout_failures": 0,
    }


def _empty_bug_velocity() -> Dict:
    return {
        "bugs_fixed_in_period": 0,
        "bug_ids": [],
        "bug_velocity_per_day": 0.0,
        "interval_known": 0,
        "avg_interval_days": None,
        "interval_details": [],
        "versions_in_period": 0,
        "versions_total": 0,
    }


def _evaluate_live_thresholds(live: Dict) -> List[Dict]:
    """阈值判定（四项）：失败率>15%、bug>0.5/天、打地鼠>30%、cap 削幅>0.02 → ⚠。

    每项附 advice 文本，供 _generate_action_suggestions 生成具体动作建议。
    """
    ch = live.get("call_health", {}) or {}
    top = ch.get("top_failures", [])
    top_str = (
        "、".join(f"{t['step']}（{t['error']}）×{t['count']}" for t in top[:3]) or "无失败记录"
    )
    bv = live.get("bug_velocity", {}) or {}
    wa = live.get("whack_a_mole", {}) or {}
    wa_top = wa.get("top_recurrences", [])
    wa_top_str = (
        "、".join(f"{r['description']}（×{r['count']}）" for r in wa_top[:3]) or "无复发记录"
    )
    cs = live.get("cap_shaving", {}) or {}

    rate = ch.get("failure_rate", 0.0) or 0.0
    velocity = bv.get("bug_velocity_per_day", 0.0) or 0.0
    whack = wa.get("rate_pct", 0.0) or 0.0
    shave = cs.get("avg_shave", 0.0) or 0.0

    return [
        {
            "key": "call_fail_rate",
            "label": "调用失败率",
            "value": f"{rate}%",
            "value_num": rate,
            "threshold": "> 15%",
            "warn": bool(rate > LIVE_THRESHOLD_CALL_FAIL_PCT),
            "advice": (
                f"step_usage 失败 TOP3：{top_str}；超时类失败 "
                f"{ch.get('timeout_failures', 0)} 次。建议核查 llm_gateway 降级链与"
                f"超时/重试参数，优先处理高频失败组合。"
            ),
        },
        {
            "key": "bug_velocity",
            "label": "BUG 修复速率",
            "value": f"{velocity}/天",
            "value_num": velocity,
            "threshold": "> 0.5/天",
            "warn": bool(velocity > LIVE_THRESHOLD_BUG_PER_DAY),
            "advice": (
                f"近 {live.get('period_days', 0)} 天修复 "
                f"{bv.get('bugs_fixed_in_period', 0)} 个 BUG（引入-修复间隔可考 "
                f"{bv.get('interval_known', 0)} 个）。修复速率超阈值通常意味着近期"
                f"改动引入回归潮，建议放慢合入节奏并补针对性回归测试。"
            ),
        },
        {
            "key": "whack_rate",
            "label": "打地鼠率",
            "value": f"{whack}%",
            "value_num": whack,
            "threshold": "> 30%",
            "warn": bool(whack > LIVE_THRESHOLD_WHACK_PCT),
            "advice": (
                f"open_critical_issues 复发 {wa.get('recurrent_issues', 0)}/"
                f"{wa.get('total_issues', 0)}，复发 TOP：{wa_top_str}。"
                f"按轮修复未触根因，建议对高频复发问题升级为系统性整改。"
            ),
        },
        {
            "key": "cap_shave",
            "label": "cap 平均削幅",
            "value": f"{shave:+.4f}",
            "value_num": shave,
            "threshold": "> 0.02",
            "warn": bool(shave > LIVE_THRESHOLD_CAP_SHAVE),
            "advice": (
                f"可考条目 {cs.get('eligible', 0)}/{cs.get('total_score_history', 0)}"
                f"（覆盖率 {cs.get('coverage_pct', 0)}%），被 cap 占比 "
                f"{cs.get('capped_ratio_pct', 0)}%。削幅偏大说明评审原始分与封顶值"
                f"差距扩大，建议核查 critic 评分锚点是否漂移。"
            ),
        },
    ]


def _analyze_live_ledgers(
    period_days: int,
    usage_dir: Optional[Path] = None,
    lifecycle_path: Optional[Path] = None,
    changelog_path: Optional[Path] = None,
    kanban_path: Optional[Path] = None,
    now: Optional[datetime] = None,
) -> Dict:
    """活账本分析（v7.2.62，确定性零 LLM）：五组指标 + 阈值判定。

    指标组：
      ① call_health  调用健康（当月+上月 step_usage JSONL 流式）
      ② bug_velocity BUG 速率（CHANGELOG 版本头 + BUG-Nn）
      ③ whack_a_mole 打地鼠率（open_critical_issues recurrence_count）
      ④ cap_shaving  cap 削幅（score_history score_raw）
      ⑤ machine_hours 机时经济学（score_history.at + kanban execution_history）

    Args:
        period_days: 统计窗口天数；usage_dir/lifecycle_path/changelog_path/
            kanban_path/now 均可注入（测试用 tempfile 构造迷你数据），缺省读真实路径。

    Returns:
        带 warnings 的完整指标 dict；任一子源缺失/损坏均 fail-open 降级，绝不抛异常。
    """
    now = now or datetime.now(timezone.utc)
    usage_dir = usage_dir or USAGE_DIR
    lifecycle_path = lifecycle_path or LIFECYCLE_PATH
    changelog_path = changelog_path or CHANGELOG_PATH
    kanban_path = kanban_path or SYSTEM_KANBAN_PATH
    cutoff = now - timedelta(days=period_days) if period_days and period_days > 0 else None

    result: Dict[str, Any] = {
        "version": "v7.2.62",
        "period_days": period_days,
        "cutoff": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ") if cutoff else "",
        "warnings": [],
    }

    # ① 调用健康
    try:
        call_health, w = _analyze_call_health(usage_dir, cutoff, now)
        result["call_health"] = call_health
        result["warnings"].extend(w)
    except Exception as exc:
        result["call_health"] = _empty_call_health()
        result["warnings"].append(f"调用健康分析异常：{exc}")

    # ② BUG 速率
    try:
        bug, w = _analyze_bug_velocity(changelog_path, cutoff, period_days)
        result["bug_velocity"] = bug
        result["warnings"].extend(w)
    except Exception as exc:
        result["bug_velocity"] = _empty_bug_velocity()
        result["warnings"].append(f"BUG 速率分析异常：{exc}")

    # ③④⑤ 生命周期侧（共用一次加载）
    lifecycle = _load_lifecycle(lifecycle_path, result["warnings"])
    try:
        result["whack_a_mole"] = _analyze_whack_a_mole(lifecycle)
    except Exception as exc:
        result["whack_a_mole"] = {
            "total_issues": 0, "recurrent_issues": 0, "rate_pct": 0.0,
            "top_recurrences": [], "missing_field_count": 0, "note": "",
        }
        result["warnings"].append(f"打地鼠率分析异常：{exc}")
    try:
        result["cap_shaving"] = _analyze_cap_shaving(lifecycle)
    except Exception as exc:
        result["cap_shaving"] = {
            "total_score_history": 0, "eligible": 0, "coverage_pct": 0.0,
            "avg_shave": 0.0, "capped_count": 0, "capped_ratio_pct": 0.0,
            "cap_hits": {"0.75": 0, "0.80": 0, "0.85": 0}, "note": "",
        }
        result["warnings"].append(f"cap 削幅分析异常：{exc}")

    kanban = _load_json(kanban_path, {}) if kanban_path.exists() else {}
    if not kanban:
        result["warnings"].append(f"system-kanban.json 缺失或为空：{kanban_path}")
    try:
        result["machine_hours"] = _analyze_machine_hours(lifecycle, kanban, cutoff, period_days)
    except Exception as exc:
        result["machine_hours"] = {
            "rounds_in_period": 0, "active_proposals": 0, "daily_rounds": 0.0,
            "kanban_exec_events": 0, "kanban_active_proposals": 0,
        }
        result["warnings"].append(f"机时经济学分析异常：{exc}")

    # 阈值判定（供格式化与建议生成共用）
    result["thresholds"] = _evaluate_live_thresholds(result)
    return result


def _format_live_section(live: Dict) -> List[str]:
    """输出「## 活账本指标（v7.2.62）」markdown 小节（每指标一行结论 + 阈值判断）。"""
    lines = ["## 活账本指标（v7.2.62）", ""]
    if not live:
        lines.append("活账本数据不可用。")
        lines.append("")
        return lines

    lines.append(
        "> 数据源：memory/usage/step-usage-*.jsonl + research_proposals/_lifecycle.json"
        " + CHANGELOG.md + system-kanban.json（确定性零 LLM）"
    )
    lines.append("")

    warn_by_key = {c["key"]: c["warn"] for c in live.get("thresholds", [])}

    def _mark(key: str) -> str:
        return "⚠" if warn_by_key.get(key) else "✓"

    # ① 调用健康
    ch = live.get("call_health", {}) or {}
    lines.append(
        f"- **调用健康** {_mark('call_fail_rate')}：总调用 {ch.get('total_calls', 0)} 次 | "
        f"失败 {ch.get('failed_calls', 0)} 次 | 失败率 {ch.get('failure_rate', 0)}%"
        f"（阈值 >15%）| 超时类失败 {ch.get('timeout_failures', 0)} 次"
    )
    top = ch.get("top_failures", [])
    if top:
        top_str = "；".join(f"{t['step']}（{t['error']}）×{t['count']}" for t in top)
        lines.append(f"  - 失败 TOP3：{top_str}")

    # ② BUG 速率
    bv = live.get("bug_velocity", {}) or {}
    interval_str = (
        f" | 平均间隔 {bv.get('avg_interval_days')} 天" if bv.get("avg_interval_days") is not None else ""
    )
    lines.append(
        f"- **BUG 速率** {_mark('bug_velocity')}：近 {live.get('period_days', 0)} 天修复 "
        f"{bv.get('bugs_fixed_in_period', 0)} 个（{bv.get('bug_velocity_per_day', 0)}/天，"
        f"阈值 >0.5/天）| 引入-修复间隔可考 {bv.get('interval_known', 0)} 个{interval_str} | "
        f"同期发版 {bv.get('versions_in_period', 0)} 个"
    )

    # ③ 打地鼠率
    wa = live.get("whack_a_mole", {}) or {}
    wa_line = (
        f"- **打地鼠率** {_mark('whack_rate')}：复发条目 "
        f"{wa.get('recurrent_issues', 0)}/{wa.get('total_issues', 0)} = "
        f"{wa.get('rate_pct', 0)}%（阈值 >30%，全量口径）"
    )
    if wa.get("note"):
        wa_line += f" | 注：{wa['note']}"
    lines.append(wa_line)
    top_r = wa.get("top_recurrences", [])
    if top_r:
        lines.append(
            "  - 复发 TOP3："
            + "；".join(f"{r['description']}（×{r['count']}）" for r in top_r)
        )

    # ④ cap 削幅
    cs = live.get("cap_shaving", {}) or {}
    hits = cs.get("cap_hits", {}) or {}
    cs_line = (
        f"- **cap 削幅** {_mark('cap_shave')}：可考条目 {cs.get('eligible', 0)}/"
        f"{cs.get('total_score_history', 0)}（覆盖率 {cs.get('coverage_pct', 0)}%）| "
        f"平均削幅 {cs.get('avg_shave', 0.0):+.4f}（score_raw−score，阈值 >0.02）| "
        f"被 cap 占比 {cs.get('capped_ratio_pct', 0)}% | 贴顶分布 "
        f"0.75×{hits.get('0.75', 0)} / 0.80×{hits.get('0.80', 0)} / 0.85×{hits.get('0.85', 0)}"
    )
    if cs.get("note"):
        cs_line += f" | 注：{cs['note']}"
    lines.append(cs_line)

    # ⑤ 机时经济学（无阈值，仅观测）
    mh = live.get("machine_hours", {}) or {}
    lines.append(
        f"- **机时经济学**：周期内新增评分轮次 {mh.get('rounds_in_period', 0)} | "
        f"活跃课题 {mh.get('active_proposals', 0)} 个 | "
        f"日均轮次 {mh.get('daily_rounds', 0)} | "
        f"看板执行事件 {mh.get('kanban_exec_events', 0)} 条"
        f"（覆盖 {mh.get('kanban_active_proposals', 0)} 课题）"
    )

    warnings = live.get("warnings", [])
    if warnings:
        lines.append("")
        lines.append("**数据源告警**：")
        for w in warnings:
            lines.append(f"- ⚠ {w}")

    lines.append("")
    return lines


def _generate_action_suggestions(
    clustering: Dict,
    fix_eff: Dict,
    agent_trends: Dict,
    health: Dict,
    live: Optional[Dict] = None,
) -> List[Dict]:
    """基于以上分析生成具体的行动建议。

    v7.2.62：新增 live 参数（活账本指标），每个触发 ⚠ 阈值的指标
    生成一条具体动作建议（格式与既有建议条目对齐）。
    """
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

    # 6. 活账本阈值建议（v7.2.62）：每个触发 ⚠ 的指标生成一条具体动作
    if live:
        for check in live.get("thresholds", []):
            if not check.get("warn"):
                continue
            suggestions.append({
                "priority": "high",
                "type": "活账本治理",
                "category": check.get("label", "活账本指标"),
                "description": (
                    f"活账本指标「{check.get('label')}」= {check.get('value')}"
                    f"（阈值 {check.get('threshold')}）触发 ⚠。"
                    f"{check.get('advice', '建议结合活账本小节明细定位根因。')}"
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
    weekend_analysis: Optional[Dict] = None,
    live: Optional[Dict] = None,
) -> str:
    """格式化 Markdown 复盘报告。

    v7.2.62：新增 live 参数（活账本指标），在「1. 问题聚类」之后
    插入「## 活账本指标（v7.2.62）」小节（编号小节保持原序不动）。
    """
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

    # ── 活账本指标（v7.2.62，插在问题聚类之后）──
    if live is not None:
        lines.extend(_format_live_section(live))

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

    # ── 6. 周末反思整合 ──
    lines.append("## 6. 周末反思整合")
    lines.append("")
    if weekend_analysis and (
        weekend_analysis.get("pattern_count", 0) > 0
        or weekend_analysis.get("action_count", 0) > 0
        or weekend_analysis.get("latest_report_at")
        or len(weekend_analysis.get("health_trend", [])) > 0
    ):
        wa = weekend_analysis
        if wa.get("latest_report_at"):
            lines.append(f"**最近反思报告**：{wa['latest_report_at']}")
        lines.append("")
        lines.append(
            f"- **模式识别**：{wa.get('pattern_count', 0)} 个 | "
            f"**行动建议**：{wa.get('action_count', 0)} 条"
        )
        lines.append(
            f"- **输入端产出**：ideas {wa.get('ideas_count', 0)} / "
            f"decisions {wa.get('decisions_count', 0)} / "
            f"directions {wa.get('directions_count', 0)}"
        )
        lines.append("")

        # Top patterns
        top_patterns = wa.get("top_patterns", [])
        if top_patterns:
            lines.append("### 反思发现的关键模式")
            lines.append("")
            for p in top_patterns:
                if isinstance(p, dict):
                    severity = p.get("severity", "")
                    label = p.get("label", p.get("pattern", "未知"))
                    lines.append(f"- [{severity.upper()}] {label}")
                else:
                    lines.append(f"- {p}")
            lines.append("")

        # 健康趋势
        health_trend = wa.get("health_trend", [])
        if health_trend:
            lines.append("### 反思健康快照")
            lines.append("")
            lines.append("| 检查时间 | 状态 | 错误 | 警告 | 优化中 | 失败Job |")
            lines.append("|----------|------|------|------|--------|---------|")
            for snap in health_trend:
                alerts = snap.get("alerts", {})
                lines.append(
                    f"| {snap.get('checked_at', '')} | "
                    f"{snap.get('status', '')} | "
                    f"{alerts.get('error', 0)} | "
                    f"{alerts.get('warning', 0)} | "
                    f"{snap.get('optimizing', 0)} | "
                    f"{snap.get('failed_jobs', 0)} |"
                )
            lines.append("")
    else:
        lines.append("当前周期内无周末反思产出。")
        lines.append("")

    # ── 7. 行动建议 ──
    lines.append("## 7. 行动建议")
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

def run_retrospective(period_str: str = "7d", output_path: Optional[Path] = None) -> Path:
    """执行复盘分析，生成报告文件。

    Args:
        period_str: 时间周期（'7d'/'1d'/'all'）
        output_path: 输出路径（v6.9.99 新增，供周末维护链
            reflection_link_deep_review job 复用本函数时把报告落到
            memory/weekend-reflection/link-deep-review-{date}.md；
            缺省保持旧行为 memory/retrospective-{date}.md）

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

    # 加载周末反思产出
    weekend_reflections = _load_weekend_reflections(cutoff)
    weekend_analysis = _analyze_weekend_reflections(weekend_reflections)

    # 执行分析
    clustering = _analyze_problem_clustering(entries, cutoff)
    fix_eff = _analyze_fix_effectiveness(entries, exec_history, cutoff)
    agent_trends = _analyze_agent_trends(agent_scores, cutoff)
    health = _analyze_system_health(exec_history, cutoff)

    # v7.2.62 活账本分析：死数据源（debug-journal 停更）之外的实时指标
    m_pd = re.match(r"^(\d+)d$", period_str)
    period_days = int(m_pd.group(1)) if m_pd else 3650  # 'all'/异常值按 10 年窗口
    live = _analyze_live_ledgers(period_days)

    suggestions = _generate_action_suggestions(clustering, fix_eff, agent_trends, health, live)

    # 合并周末反思的行动建议
    for item in weekend_analysis.get("actionable_items", []):
        suggestions.append({
            "priority": "medium",
            "type": "weekend_reflection",
            "category": "周末反思",
            "description": item,
        })

    # 生成报告
    report_md = _format_report(
        period_str, cutoff, clustering, fix_eff,
        agent_trends, health, suggestions, tuning_log,
        weekend_analysis, live,
    )

    # v7.3.61（批次 D·目标 3）：阶段级 WoW 回归检测节——per-step 失败率/
    # 时延周环比 + 确定性回归告警，落盘 stage-weekly-<date>.json。
    # fail-open：检测故障不影响复盘报告主体。
    try:
        from stage_weekly_report import run_and_persist as _stage_report
        _rep, _md = _stage_report()
        report_md = report_md.rstrip("\n") + "\n\n---\n\n" + _md + "\n"
    except Exception as _exc:  # noqa: BLE001
        report_md = report_md.rstrip("\n") + (
            f"\n\n---\n\n## 阶段级 WoW 回归检测\n\n- ⚠ 检测故障（fail-open）：{_exc}\n")

    # 写入文件
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = output_path or (MEMORY_DIR / f"retrospective-{today}.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_md, encoding="utf-8")

    print(f"✓ 复盘报告已生成：{output_path}")
    print(f"  时间窗口：{'全部数据' if cutoff is None else cutoff.strftime('%Y-%m-%d')} 至今")
    print(f"  debug 条目：{clustering['total_filtered']}")
    print(f"  执行任务数：{health['total_jobs']}")
    print(f"  成功率：{health['success_rate']}%")
    print(
        f"  活账本：调用 {live.get('call_health', {}).get('total_calls', 0)} 次"
        f"（失败率 {live.get('call_health', {}).get('failure_rate', 0)}%）| "
        f"BUG {live.get('bug_velocity', {}).get('bug_velocity_per_day', 0)}/天 | "
        f"打地鼠率 {live.get('whack_a_mole', {}).get('rate_pct', 0)}% | "
        f"cap 削幅 {live.get('cap_shaving', {}).get('avg_shave', 0.0):+.4f} | "
        f"周期轮次 {live.get('machine_hours', {}).get('rounds_in_period', 0)}"
    )
    print(f"  行动建议：{len(suggestions)} 条")

    # v6.9.0 R5: 复盘时自动应用低风险策略建议（白名单 + 单向 + 去重）
    try:
        from strategy_optimizer import auto_apply_low_risk

        auto_result = auto_apply_low_risk()
        if auto_result.get("applied"):
            for c in auto_result["changes"]:
                print(
                    f"  自动应用（低风险）：{c['key']} {c['current']} → {c['suggested']}"
                )
                # 追记到报告，保证审计可见
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(
                        f"\n> v6.9.0 自动调优：{c['key']} {c['current']} → "
                        f"{c['suggested']}（confirmed_by=auto:low-risk）\n"
                    )
        else:
            print(f"  低风险自动应用：{auto_result.get('reason', '跳过')}")
    except Exception as exc:
        print(f"  ⚠ 低风险自动应用失败：{exc}")

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

    # 6. 报告生成测试（v7.2.62 起携带活账本小节）
    live = _analyze_live_ledgers(7)
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
        None,
        live,
    )
    assert "# 复盘报告" in report_md
    assert "## 1. 问题聚类" in report_md
    assert "## 活账本指标（v7.2.62）" in report_md
    assert "## 6. 周末反思整合" in report_md
    assert "## 7. 行动建议" in report_md
    # 小节插入位置：问题聚类之后、修复有效性之前
    assert (report_md.index("## 1. 问题聚类")
            < report_md.index("## 活账本指标（v7.2.62）")
            < report_md.index("## 2. 修复有效性"))
    print("  ✓ 报告格式正确（7 个章节 + 活账本小节完整）")

    # 7. 活账本分析测试（v7.2.62，tempfile 迷你数据覆盖各分支）
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        now_fixed = datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc)

        usage_dir = tdp / "usage"
        usage_dir.mkdir()
        rows = [
            {"ts": "2026-10-28T00:00:00Z", "kind": "llm_router", "name": "minimax",
             "success": True, "error": ""},
            {"ts": "2026-10-28T01:00:00Z", "kind": "llm_router", "name": "minimax",
             "success": False, "error": "✗ minimax: The read operation timed out"},
            {"ts": "2026-10-28T02:00:00Z", "kind": "llm_router", "name": "glm",
             "success": False, "error": "✗ glm: API HTTP 429: rate_limit_error"},
            # 周期外条目（cutoff 2026-10-23）应被过滤
            {"ts": "2026-09-05T00:00:00Z", "kind": "llm_router", "name": "glm",
             "success": False, "error": "✗ glm: 老失败"},
            "这不是 JSON 的坏行",
        ]
        oct_lines = "\n".join(
            json.dumps(r, ensure_ascii=False) if isinstance(r, dict) else r for r in rows
        ) + "\n"
        (usage_dir / "step-usage-2026-10.jsonl").write_text(oct_lines, encoding="utf-8")
        (usage_dir / "step-usage-2026-09.jsonl").write_text(
            json.dumps({"ts": "2026-09-05T00:00:00Z", "kind": "llm_router",
                        "name": "glm", "success": True}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        lifecycle = {"proposals": {
            "p1": {
                "score_history": [
                    {"round": 1, "score": 0.75, "score_raw": 0.80,
                     "at": "2026-10-29T00:00:00Z"},
                    {"round": 2, "score": 0.79, "at": "2026-10-29T06:00:00Z"},
                ],
                "open_critical_issues": [
                    {"severity": "high", "description": "复发问题甲", "recurrence_count": 3},
                    {"severity": "medium", "description": "历史问题乙"},
                ],
            },
        }}
        (tdp / "_lifecycle.json").write_text(
            json.dumps(lifecycle, ensure_ascii=False), encoding="utf-8")
        (tdp / "CHANGELOG.md").write_text(
            "# 变更记录\n\n## v7.2.62 - 2026-10-29 BUG-9 修复：演示修复头\n\n"
            "## v7.2.61 - 2026-10-20 隐患记录\n\n正文提到 BUG-9 的引入线索。\n",
            encoding="utf-8",
        )
        (tdp / "kanban.json").write_text(json.dumps(
            {"execution_history": [
                {"at": "2026-10-29T08:00:00Z", "proposal_id": "p1",
                 "step": "writer", "success": True},
            ]}, ensure_ascii=False), encoding="utf-8")

        live_mini = _analyze_live_ledgers(
            7, usage_dir=usage_dir, lifecycle_path=tdp / "_lifecycle.json",
            changelog_path=tdp / "CHANGELOG.md", kanban_path=tdp / "kanban.json",
            now=now_fixed,
        )
        ch = live_mini["call_health"]
        assert ch["total_calls"] == 3, f"周期内调用数应为 3，实际 {ch['total_calls']}"
        assert ch["failed_calls"] == 2
        assert ch["timeout_failures"] == 1
        assert ch["top_failures"][0]["error"] == "超时"
        bv = live_mini["bug_velocity"]
        assert bv["bugs_fixed_in_period"] == 1
        assert bv["interval_known"] == 1, "BUG-9 首见 10-20、修复 10-29，间隔应可考"
        wa = live_mini["whack_a_mole"]
        assert wa["total_issues"] == 2 and wa["recurrent_issues"] == 1
        assert wa["missing_field_count"] == 1 and "v7.2.62" in wa["note"]
        cs = live_mini["cap_shaving"]
        assert cs["eligible"] == 1 and abs(cs["avg_shave"] - 0.05) < 1e-9
        assert cs["cap_hits"]["0.75"] == 1
        mh = live_mini["machine_hours"]
        assert mh["rounds_in_period"] == 2 and mh["active_proposals"] == 1
        assert mh["kanban_exec_events"] == 1
        # 阈值触发：失败率 66.7%>15% 与打地鼠 50%>30% 应为 ⚠
        warn_keys = {c["key"] for c in live_mini["thresholds"] if c["warn"]}
        assert "call_fail_rate" in warn_keys and "whack_rate" in warn_keys
        sec = _format_live_section(live_mini)
        assert any(l.startswith("## 活账本指标（v7.2.62）") for l in sec)
        assert any("⚠" in l for l in sec)
        print("  ✓ 活账本分析正常（迷你数据五组指标 + 阈值分支覆盖）")

        # 8. 活账本缺文件 fail-open：绝不崩溃，返回 warnings
        live_missing = _analyze_live_ledgers(
            7, usage_dir=tdp / "nope-usage", lifecycle_path=tdp / "nope-lc.json",
            changelog_path=tdp / "nope-cl.md", kanban_path=tdp / "nope-kb.json",
            now=now_fixed,
        )
        assert live_missing["warnings"], "缺文件场景必须产生 warnings"
        assert live_missing["call_health"]["total_calls"] == 0
        assert live_missing["whack_a_mole"]["total_issues"] == 0
        assert _format_live_section(live_missing), "缺文件时格式化小节仍应可输出"
        print("  ✓ 活账本缺文件 fail-open 正常")

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
