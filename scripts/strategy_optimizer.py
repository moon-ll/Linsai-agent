#!/usr/bin/env python3
"""strategy_optimizer.py — 调度策略自调优（v6.7 林赛总控能力·子模块）

基于历史数据自动给出调度参数建议：
- stagger_seconds（错峰间隔）
- max_rounds（单 proposal 最大轮数）
- score_threshold（达标分数）
- no_improvement_limit（连续无提升上限）
- critic/writer timeout

建议规则：
- 高频率派活 + 长耗时 → 增加 stagger
- 成功率低 + 多超时 → 增加 timeout
- 评分整体偏低 → 降低 threshold 或调整权重
- 评分整体偏高 → 提高 threshold

默认**仅建议**，不自动应用。人工通过 Web API `POST /api/orchestrator/strategies/apply` 确认。

用法:
    from strategy_optimizer import suggest_strategies
    result = suggest_strategies(window_hours=168)
    print(result['current'])
    print(result['suggested'])
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc, load_json
from paths import PROJECT_ROOT, LOGS_DIR


def _get_current_strategies() -> Dict[str, Any]:
    """从 proposal_lifecycle 读取当前默认策略。"""
    try:
        import proposal_lifecycle as pl
        return {
            "stagger_seconds": pl.DEFAULT_STAGGER_SECONDS,
            "max_rounds": pl.DEFAULT_MAX_ROUNDS,
            "score_threshold": pl.DEFAULT_SCORE_THRESHOLD,
            "no_improvement_limit": pl.DEFAULT_NO_IMPROVEMENT_LIMIT,
            "critic_timeout": 300,
            "writer_timeout": 600,
        }
    except Exception as e:
        return {"error": str(e)}


def _analyze_recent_activity(window_hours: int = 168) -> Dict[str, Any]:
    """分析最近 N 天的派活活动。"""
    log_file = LOGS_DIR / "linsai.log"
    if not log_file.exists():
        return {}

    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    daily_dispatch: Dict[str, int] = defaultdict(int)
    daily_duration_sum: Dict[str, float] = defaultdict(float)
    daily_duration_count: Dict[str, int] = defaultdict(int)
    daily_timeout: Dict[str, int] = defaultdict(int)
    total_success = 0
    total_fail = 0

    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = re.search(r"\[(\d{4}-\d{2}-\d{2})T(\d{2}):", line)
                if not m:
                    continue
                try:
                    at = datetime.fromisoformat(m.group(1) + "T" + m.group(2) + ":00:00+00:00")
                except Exception:
                    continue
                if at < cutoff:
                    continue
                date_key = m.group(1)
                if "对抗轮" in line or "critic 评审" in line or "writer 优化" in line:
                    daily_dispatch[date_key] += 1
                if "elapsed" in line:
                    m2 = re.search(r"elapsed[=:\s]+(\d+)", line)
                    if m2:
                        daily_duration_sum[date_key] += int(m2.group(1))
                        daily_duration_count[date_key] += 1
                if "超时" in line or "timeout" in line.lower():
                    daily_timeout[date_key] += 1
                if "[ERROR]" in line:
                    total_fail += 1
                elif "[INFO]" in line and "成功" in line:
                    total_success += 1
    except Exception:
        pass

    days = max(1, len(daily_dispatch))
    avg_dispatch_per_day = sum(daily_dispatch.values()) / days
    avg_duration = (
        sum(daily_duration_sum.values()) / sum(daily_duration_count.values())
        if daily_duration_count else 0
    )
    total_timeout = sum(daily_timeout.values())

    return {
        "days": days,
        "avg_dispatch_per_day": round(avg_dispatch_per_day, 1),
        "avg_duration_s": round(avg_duration, 1),
        "total_timeout": total_timeout,
        "total_success": total_success,
        "total_fail": total_fail,
        "success_rate": round(total_success / (total_success + total_fail), 3) if (total_success + total_fail) > 0 else None,
    }


def _analyze_score_distribution(window_hours: int = 168) -> Dict[str, Any]:
    """从 _lifecycle.json 分析最近评分分布。"""
    lifecycle_file = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    if not lifecycle_file.exists():
        return {"avg_score": 0, "max_score": 0, "pass_rate": 0, "samples": 0}

    try:
        data = load_json(lifecycle_file)
        scores: List[float] = []
        passes = 0
        for s in data.get("proposals", {}).values():
            for h in s.get("score_history", []):
                sc = h.get("score", 0)
                if sc > 0:
                    scores.append(sc)
                    if h.get("section_passed"):
                        passes += 1
        if not scores:
            return {"avg_score": 0, "max_score": 0, "pass_rate": 0, "samples": 0}
        return {
            "avg_score": round(sum(scores) / len(scores), 3),
            "max_score": max(scores),
            "min_score": min(scores),
            "pass_rate": round(passes / len(scores), 3),
            "samples": len(scores),
        }
    except Exception:
        return {}


def suggest_strategies(window_hours: int = 168) -> Dict[str, Any]:
    """基于历史数据生成策略建议。

    Args:
        window_hours: 时间窗（小时），默认 7 天

    Returns:
        {
          'current': {stagger_seconds, max_rounds, ...},
          'suggested': {stagger_seconds, max_rounds, ...},
          'reason': str,
          'risk': 'low' | 'medium' | 'high',
          'activity': {days, avg_dispatch_per_day, ...},
          'score_stats': {avg_score, max_score, ...},
          'computed_at': ISO
        }
    """
    current = _get_current_strategies()
    activity = _analyze_recent_activity(window_hours)
    score_stats = _analyze_score_distribution(window_hours)

    suggested = dict(current)  # 浅拷贝
    reasons: List[str] = []

    # 规则 1：高频率派活 + 平均耗时超过 stagger 间隔过多
    if activity.get("avg_dispatch_per_day", 0) > 5 and activity.get("avg_duration_s", 0) > 500:
        new_stagger = current["stagger_seconds"] + 30
        suggested["stagger_seconds"] = new_stagger
        reasons.append(
            f"过去 {activity['days']} 天平均每天派活 {activity['avg_dispatch_per_day']} 次，"
            f"平均耗时 {activity['avg_duration_s']}s，建议 stagger 从 "
            f"{current['stagger_seconds']}s → {new_stagger}s 以错峰避让"
        )

    # 规则 2：超时频繁
    if activity.get("total_timeout", 0) > 5:
        new_critic_timeout = int(current["critic_timeout"] * 1.5)
        new_writer_timeout = int(current["writer_timeout"] * 1.5)
        suggested["critic_timeout"] = new_critic_timeout
        suggested["writer_timeout"] = new_writer_timeout
        reasons.append(
            f"过去 {window_hours//24} 天超时 {activity['total_timeout']} 次，"
            f"建议 critic timeout {current['critic_timeout']}s → {new_critic_timeout}s，"
            f"writer timeout {current['writer_timeout']}s → {new_writer_timeout}s"
        )

    # 规则 3：成功率低
    if activity.get("success_rate") is not None and activity["success_rate"] < 0.6:
        new_max = max(3, current["max_rounds"] - 2)
        suggested["max_rounds"] = new_max
        reasons.append(
            f"成功率仅 {activity['success_rate']*100:.0f}%，"
            f"建议 max_rounds {current['max_rounds']} → {new_max}，避免重复无效轮次消耗限额"
        )

    # 规则 4：评分整体偏低
    if score_stats.get("avg_score", 0) > 0 and score_stats["avg_score"] < 0.3:
        new_threshold = max(0.5, current["score_threshold"] - 0.05)
        suggested["score_threshold"] = round(new_threshold, 2)
        reasons.append(
            f"平均分 {score_stats['avg_score']}，"
            f"若阈值过严会导致大量'无提升退出'，建议 threshold "
            f"{current['score_threshold']} → {new_threshold}"
        )

    # 规则 5：评分整体偏高
    if score_stats.get("avg_score", 0) > 0.7:
        new_threshold = min(0.9, current["score_threshold"] + 0.05)
        suggested["score_threshold"] = round(new_threshold, 2)
        reasons.append(
            f"平均分 {score_stats['avg_score']} 偏高，"
            f"建议 threshold {current['score_threshold']} → {new_threshold} 提升质量门槛"
        )

    # 风险评估
    risk = "low"
    if len(reasons) >= 3:
        risk = "high"
    elif len(reasons) >= 1:
        risk = "medium"

    return {
        "current": current,
        "suggested": suggested,
        "reasons": reasons,
        "risk": risk,
        "activity": activity,
        "score_stats": score_stats,
        "computed_at": now_utc(),
    }


# ============================================================
# v6.9.0 R5: 低风险策略自动应用
# ============================================================

TUNING_LOG_PATH = PROJECT_ROOT / "memory" / "tuning-log.json"

AUTO_APPLY_DEDUP_DAYS = 7
"""同一参数 7 天内已应用过则跳过（防止震荡）。"""

AUTO_APPLY_MAX_PER_RUN = 2
"""单次自动应用至多改 2 个参数（小步快跑，便于归因）。"""

AUTO_APPLY_KEYS = ("stagger_seconds", "score_threshold")
"""可自动应用的参数白名单。

分级依据：
  - stagger_seconds：仅影响派活节奏，风险最低，任何方向可自动
  - score_threshold：只允许提高（收紧质量门槛更保守；降低可能放进
    低质课题，必须人工确认）
  - max_rounds / no_improvement_limit：双向都有争议，永不自动
  - critic/writer timeout：建议值由 v6.8.52 超时分级（lifecycle/constants）
    承载，apply_strategies 不支持，保持人工
"""


def _recently_applied_keys(
    tuning_log: List[Dict[str, Any]],
    now: Optional[datetime] = None,
    days: int = AUTO_APPLY_DEDUP_DAYS,
) -> set:
    """最近 N 天内（含人工与自动）已应用过的参数键集合。"""
    now = now or datetime.now(timezone.utc)
    recent: set = set()
    for entry in tuning_log or []:
        try:
            at = datetime.fromisoformat(str(entry.get("at", "")).replace("Z", "+00:00"))
        except Exception:
            continue
        if (now - at).total_seconds() > days * 86400:
            continue
        new = entry.get("new")
        if isinstance(new, dict):
            recent.update(new.keys())
    return recent


def select_auto_appliable(
    current: Dict[str, Any],
    suggested: Dict[str, Any],
    tuning_log: List[Dict[str, Any]],
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """纯函数：从建议中筛出可安全自动应用的参数变更。"""
    recent = _recently_applied_keys(tuning_log, now)
    changes: List[Dict[str, Any]] = []
    for key in AUTO_APPLY_KEYS:
        cur = current.get(key)
        sug = suggested.get(key)
        if cur is None or sug is None or sug == cur:
            continue
        if key in recent:
            continue
        if key == "score_threshold" and float(sug) < float(cur):
            continue  # 降门槛必须人工确认
        changes.append({"key": key, "current": cur, "suggested": sug})
        if len(changes) >= AUTO_APPLY_MAX_PER_RUN:
            break
    return changes


def auto_apply_low_risk(result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """自动应用低风险策略建议（经 orchestrator.apply_strategies 落盘）。

    纪律：白名单 + 单向规则（threshold 只升不降）+ 7 天去重 + 单次上限，
    tuning-log 中 confirmed_by 标记为 auto:low-risk 可审计、可回滚。
    """
    result = result or suggest_strategies()
    if result.get("error") or not result.get("reasons"):
        return {"applied": False, "reason": "no_suggestions", "risk": result.get("risk")}

    tuning_log = []
    if TUNING_LOG_PATH.exists():
        try:
            tuning_log = load_json(TUNING_LOG_PATH) or []
        except Exception:
            tuning_log = []
    changes = select_auto_appliable(
        result["current"], result["suggested"], tuning_log
    )
    if not changes:
        return {"applied": False, "reason": "no_safe_changes", "risk": result.get("risk")}

    try:
        # 延迟导入避免 orchestrator ↔ strategy_optimizer 循环
        from orchestrator import apply_strategies

        patch = {c["key"]: c["suggested"] for c in changes}
        apply_result = apply_strategies(patch, confirmed_by="auto:low-risk")
    except Exception as exc:
        return {"applied": False, "reason": f"apply_failed: {exc}", "changes": changes}

    return {
        "applied": True,
        "changes": changes,
        "apply_result": apply_result,
    }


def _self_check() -> None:
    """自检。"""
    print("=== strategy_optimizer._self_check ===")
    result = suggest_strategies(window_hours=168)
    assert "current" in result
    assert "suggested" in result
    print(f"  current: {result['current']}")
    print(f"  suggested: {result['suggested']}")
    print(f"  reasons: {len(result['reasons'])} 条")
    print(f"  risk: {result['risk']}")
    for r in result["reasons"][:3]:
        print(f"  - {r[:80]}")

    # v6.9.0 R5: 安全筛选规则自检
    from datetime import datetime, timedelta, timezone as _tz

    now = datetime(2026, 8, 14, tzinfo=_tz.utc)
    cur = {"stagger_seconds": 60, "score_threshold": 0.9, "max_rounds": 8}
    # 门槛下调被拒；stagger 变化放行
    sug = {"stagger_seconds": 90, "score_threshold": 0.85, "max_rounds": 6}
    changes = select_auto_appliable(cur, sug, [], now=now)
    assert [c["key"] for c in changes] == ["stagger_seconds"], changes
    # 门槛上调放行
    sug2 = {"stagger_seconds": 60, "score_threshold": 0.95}
    changes2 = select_auto_appliable(cur, sug2, [], now=now)
    assert [c["key"] for c in changes2] == ["score_threshold"], changes2
    # 7 天去重：stagger 刚应用过 → 跳过
    log = [{"at": (now - timedelta(days=1)).isoformat(), "new": {"stagger_seconds": 90}}]
    changes3 = select_auto_appliable(cur, sug, log, now=now)
    assert changes3 == [], changes3
    # 8 天前的记录不再拦截
    log2 = [{"at": (now - timedelta(days=8)).isoformat(), "new": {"stagger_seconds": 90}}]
    changes4 = select_auto_appliable(cur, sug, log2, now=now)
    assert [c["key"] for c in changes4] == ["stagger_seconds"], changes4
    print("=== 通过 ===")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        _self_check()
    else:
        result = suggest_strategies()
        print(json.dumps(result, ensure_ascii=False, indent=2))
