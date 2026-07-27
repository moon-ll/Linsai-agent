#!/usr/bin/env python3
"""orchestrator.py — 林赛总控核心（v6.7）

四大能力统一入口：
1. compute_dashboard() — 跨 profile 仪表盘
2. analyze_failures() — 失败模式分析
3. suggest_strategies() — 调度策略建议
4. monitor_pipeline() — Pipeline 状态机监控

用法:
    from orchestrator import compute_dashboard
    result = compute_dashboard(window_hours=24)
    print(result['profiles']['writer']['status'])
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc, load_json
from paths import PROJECT_ROOT, MEMORY_DIR, RESEARCH_PROPOSALS_DIR

# 子模块导入
from profile_health import compute_profile_health
from failure_analyzer import analyze_failures
from strategy_optimizer import suggest_strategies


# ============================================================
# 1. 跨 profile 仪表盘（4 区合一）
# ============================================================

def compute_dashboard(window_hours: int = 24) -> Dict[str, Any]:
    """总仪表盘 = profile 健康度 + 失败分析 + 策略建议 + 链路质量。"""
    return {
        "profiles": compute_profile_health(window_hours=window_hours),
        "failures": analyze_failures(window_hours=window_hours),
        "strategies": suggest_strategies(window_hours=max(window_hours, 168)),
        "pipeline_quality": monitor_pipeline(),
        "computed_at": now_utc(),
    }


# ============================================================
# 2. Pipeline 状态机监控
# ============================================================

def _score_artifact(file_path: Path) -> Dict[str, Any]:
    """评估单个产物的质量。

    评分维度：
    - 存在性（0/1）
    - 大小（0/1, ≥2000 字节 = 1）
    - 章节完整度（0/1）
    - 引用占位符数量（0/1, ≥10 = 1）
    """
    if not file_path.exists():
        return {"exists": False, "size": 0, "score": 0.0, "issues": ["文件不存在"]}

    size = file_path.stat().st_size
    score = 0.0
    issues: List[str] = []

    if size >= 2000:
        score += 0.4
    elif size >= 500:
        score += 0.2
    else:
        issues.append(f"文件过小（{size} 字节）")

    if size > 100:
        try:
            content = file_path.read_text(encoding="utf-8")
            # 章节完整度：## 一、立项依据 / ## 二、研究内容 / ## 三、研究方案
            sections = re.findall(r"##\s+[一二三四五六七八九十]+[、\.]", content)
            if len(sections) >= 3:
                score += 0.3
            else:
                issues.append(f"章节不完整（仅 {len(sections)} 个）")
            # 引用占位符
            cites = re.findall(r"\[CITE:[\w\-]+\]", content)
            if len(cites) >= 10:
                score += 0.3
            elif len(cites) > 0:
                score += 0.1
                issues.append(f"引用占位符较少（{len(cites)} 个）")
            else:
                issues.append("无引用占位符")
        except Exception:
            issues.append("文件读取失败")

    return {
        "exists": True,
        "size": size,
        "score": round(score, 3),
        "issues": issues,
    }


def monitor_pipeline(proposal_id: Optional[str] = None) -> Dict[str, Any]:
    """监控 pipeline-runner 的产物质量。

    6 阶段产物：
    - 01_direction/direction-calibration.md
    - 02_literature/literature-report.md
    - 02_topic/gap-report.md
    - 03_question/question-framework.md
    - 04_proposal/proposal-draft.md
    - 05_review/review-report.md

    Args:
        proposal_id: 指定 proposal，为 None 则扫描所有

    Returns:
        {
          'proposals': [
            {proposal_id, stages: [{stage, quality, issues}], overall_quality, growth_actions},
            ...
          ]
        }
    """
    out: Dict[str, Any] = {"proposals": [], "growth_actions_total": 0, "computed_at": now_utc()}

    if proposal_id:
        candidates = [proposal_id]
    else:
        # 扫描所有 proposal 目录
        candidates = []
        if RESEARCH_PROPOSALS_DIR.exists():
            for stage_dir in RESEARCH_PROPOSALS_DIR.iterdir():
                if stage_dir.is_dir() and not stage_dir.name.startswith("_") and not stage_dir.name.startswith("."):
                    for prop_dir in stage_dir.iterdir():
                        if prop_dir.is_dir():
                            candidates.append(prop_dir.name)

    stage_paths = [
        ("01_direction", "方向校准", "01_direction/direction-calibration.md"),
        ("02_literature", "文献调研", "02_literature/literature-report.md"),
        ("02_topic", "缺口分析", "02_topic/gap-report.md"),
        ("03_question", "科学问题", "03_question/question-framework.md"),
        ("04_proposal", "申请书", "04_proposal/proposal-draft.md"),
        ("05_review", "自检报告", "05_review/review-report.md"),
    ]

    for pid in candidates:
        # 找到 prop_dir
        prop_dir = None
        for stage_dir in ["pending_review", "optimizing", "drafts", "archived"]:
            d = RESEARCH_PROPOSALS_DIR / stage_dir / pid
            if d.exists():
                prop_dir = d
                break
        if not prop_dir:
            continue

        stages: List[Dict[str, Any]] = []
        growth_actions: List[Dict[str, Any]] = []
        for stage_key, stage_label, rel_path in stage_paths:
            f = prop_dir / rel_path
            quality = _score_artifact(f)
            entry = {
                "stage": stage_key,
                "label": stage_label,
                "path": str(f.relative_to(PROJECT_ROOT)),
                **quality,
            }
            stages.append(entry)
            if quality["score"] > 0 and quality["score"] < 0.6 and quality["issues"]:
                growth_actions.append({
                    "stage": stage_key,
                    "label": stage_label,
                    "action": "auto_retry",
                    "reason": f"质量 {quality['score']} < 0.6，issues: {', '.join(quality['issues'][:2])}",
                })

        overall = sum(s["score"] for s in stages) / max(1, len(stages))
        out["proposals"].append({
            "proposal_id": pid,
            "stages": stages,
            "overall_quality": round(overall, 3),
            "growth_actions": growth_actions,
        })
        out["growth_actions_total"] += len(growth_actions)

    return out


# ============================================================
# 3. 应用策略（人工确认后调用）
# ============================================================

TUNING_LOG_PATH = MEMORY_DIR / "tuning-log.json"


def apply_strategies(
    new_strategies: Dict[str, Any],
    confirmed_by: str = "human",
) -> Dict[str, Any]:
    """应用新策略（运行时 monkey patch + 持久化记录）。

    Args:
        new_strategies: {stagger_seconds, max_rounds, ...}
        confirmed_by: 确认人

    Returns:
        {applied, log_entry}
    """
    import proposal_lifecycle as pl

    # 记录前值
    old = {
        "stagger_seconds": pl.DEFAULT_STAGGER_SECONDS,
        "max_rounds": pl.DEFAULT_MAX_ROUNDS,
        "score_threshold": pl.DEFAULT_SCORE_THRESHOLD,
        "no_improvement_limit": pl.DEFAULT_NO_IMPROVEMENT_LIMIT,
    }

    # 应用（monkey patch）
    applied: Dict[str, Any] = {}
    if "stagger_seconds" in new_strategies:
        pl.DEFAULT_STAGGER_SECONDS = int(new_strategies["stagger_seconds"])
        applied["stagger_seconds"] = pl.DEFAULT_STAGGER_SECONDS
    if "max_rounds" in new_strategies:
        pl.DEFAULT_MAX_ROUNDS = int(new_strategies["max_rounds"])
        applied["max_rounds"] = pl.DEFAULT_MAX_ROUNDS
    if "score_threshold" in new_strategies:
        pl.DEFAULT_SCORE_THRESHOLD = float(new_strategies["score_threshold"])
        applied["score_threshold"] = pl.DEFAULT_SCORE_THRESHOLD
    if "no_improvement_limit" in new_strategies:
        pl.DEFAULT_NO_IMPROVEMENT_LIMIT = int(new_strategies["no_improvement_limit"])
        applied["no_improvement_limit"] = pl.DEFAULT_NO_IMPROVEMENT_LIMIT

    # 记录到 tuning-log.json
    log_entry = {
        "at": now_utc(),
        "confirmed_by": confirmed_by,
        "old": old,
        "new": applied,
    }
    history = []
    if TUNING_LOG_PATH.exists():
        try:
            history = load_json(TUNING_LOG_PATH)
        except Exception:
            pass
    if not isinstance(history, list):
        history = []
    history.append(log_entry)
    # 只保留最近 50 条
    history = history[-50:]

    from common import save_json
    TUNING_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_json(TUNING_LOG_PATH, history)

    return {
        "applied": applied,
        "log_entry": log_entry,
    }


# ============================================================
# 自检
# ============================================================

def _self_check() -> None:
    print("=== orchestrator._self_check ===")
    print("--- compute_dashboard ---")
    d = compute_dashboard(window_hours=24)
    assert "profiles" in d and "failures" in d and "strategies" in d and "pipeline_quality" in d
    print(f"  profiles: {len(d['profiles']['profiles'])} 个")
    print(f"  failures patterns: {len(d['failures']['patterns'])} 个")
    print(f"  strategies reasons: {len(d['strategies']['reasons'])} 条")
    print(f"  pipeline proposals: {len(d['pipeline_quality']['proposals'])} 个")
    print()
    print("--- monitor_pipeline ---")
    mp = monitor_pipeline()
    assert "proposals" in mp
    print(f"  监控 {len(mp['proposals'])} 个 proposal")
    for p in mp["proposals"][:2]:
        print(f"  - {p['proposal_id'][:40]}: overall={p['overall_quality']}, actions={len(p['growth_actions'])}")
    print()
    print("--- apply_strategies ---")
    r = apply_strategies({"stagger_seconds": 120}, confirmed_by="self_check")
    assert r["applied"]["stagger_seconds"] == 120
    print(f"  applied: {r['applied']}")
    # 还原
    import proposal_lifecycle as pl
    pl.DEFAULT_STAGGER_SECONDS = 90
    print("=== 通过 ===")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        _self_check()
    elif len(sys.argv) > 1 and sys.argv[1] == "--dashboard":
        d = compute_dashboard()
        print(json.dumps(d, ensure_ascii=False, indent=2)[:5000])
    else:
        d = compute_dashboard()
        print(json.dumps(d, ensure_ascii=False, indent=2)[:3000])
