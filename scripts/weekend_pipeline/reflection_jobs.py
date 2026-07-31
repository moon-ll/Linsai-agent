#!/usr/bin/env python3
"""反思阶段 job 执行器。"""

from __future__ import annotations

from typing import Any, Dict, List

from common import load_json, now_utc, save_json
from paths import PROJECT_ROOT
from proposal_lifecycle import ProposalLifecycle

from .constants import WEEKEND_REFLECTION_DIR

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


def _ensure_reflection_dir() -> None:
    WEEKEND_REFLECTION_DIR.mkdir(parents=True, exist_ok=True)


def _date_str() -> str:
    return now_utc()[:10]


def _collected_state_path() -> Any:
    return WEEKEND_REFLECTION_DIR / f"collected-state-{_date_str()}.json"


def _analyzed_patterns_path() -> Any:
    return WEEKEND_REFLECTION_DIR / f"analyzed-patterns-{_date_str()}.json"


def _reflection_report_path() -> Any:
    return WEEKEND_REFLECTION_DIR / f"weekend-reflection-{_date_str()}.json"


# ---------------------------------------------------------------------------
# 数据收集
# ---------------------------------------------------------------------------


def _collect_raw_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """收集反思所需的全部原始状态。"""
    try:
        from orchestrator import compute_dashboard
        from failure_analyzer import analyze_failures
        from strategy_optimizer import suggest_strategies
    except Exception as e:
        return {"error": f"无法导入反思依赖: {e}"}

    try:
        dashboard = compute_dashboard()
    except Exception as e:
        dashboard = {"error": str(e)}

    try:
        failures = analyze_failures(window_hours=168)
    except Exception as e:
        failures = {"error": str(e)}

    try:
        strategies = suggest_strategies(window_hours=168)
    except Exception as e:
        strategies = {"error": str(e)}

    try:
        lc = ProposalLifecycle()
        progress = lc.list_by_status()
    except Exception as e:
        progress = []

    pipeline_state_summary = {
        "total_jobs": len(state.get("jobs", [])),
        "done": sum(1 for j in state.get("jobs", []) if j.get("status") == "done"),
        "failed": sum(1 for j in state.get("jobs", []) if j.get("status") == "failed"),
        "pending": sum(1 for j in state.get("jobs", []) if j.get("status") == "pending"),
        "stage_status": state.get("stage_status", {}),
    }

    # v6.8.0: 按新 5 模块统计各 proposal 的模块完成状态
    module_status_summary = {}
    try:
        from proposal_sections import PROPOSAL_SECTIONS
        module_keys = [s["key"] for s in PROPOSAL_SECTIONS]
        for p in progress:
            if not isinstance(p, dict):
                continue
            pid = p.get("proposal_id", "")
            pstate = lc._get_proposal_state(pid) if pid else {}
            jobs = pstate.get("pipeline_jobs", [])
            module_status_summary[pid] = {}
            for key in module_keys:
                section_jobs = [j for j in jobs if j.get("section_key") == key]
                if not section_jobs:
                    module_status_summary[pid][key] = "not_started"
                elif all(j.get("status") == "done" for j in section_jobs):
                    module_status_summary[pid][key] = "done"
                elif any(j.get("status") == "failed" for j in section_jobs):
                    module_status_summary[pid][key] = "failed"
                else:
                    module_status_summary[pid][key] = "in_progress"
    except Exception:
        module_status_summary = {"error": "无法统计模块状态"}

    return {
        "collected_at": now_utc(),
        "dashboard": dashboard,
        "failure_patterns": failures,
        "strategy_suggestions": strategies,
        "proposal_progress": progress,
        "pipeline_state_summary": pipeline_state_summary,
        "module_status_summary": module_status_summary,
    }


def run_reflection_collect_state(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """收集原始状态并落盘，供后续 analyze/report 使用。"""
    _ensure_reflection_dir()
    collected = _collect_raw_state(state)
    if "error" in collected:
        return {"success": False, "error": collected["error"]}

    if not dry_run:
        save_json(_collected_state_path(), collected)

    return {"success": True, "collected_at": collected.get("collected_at"), "dry_run": dry_run}


# ---------------------------------------------------------------------------
# 模式分析
# ---------------------------------------------------------------------------


def _analyze_collected_state(collected: Dict[str, Any]) -> Dict[str, Any]:
    """对收集到的状态进行轻量级模式分析（无需 LLM）。"""
    patterns: List[Dict[str, Any]] = []
    next_actions: List[str] = []

    dashboard = collected.get("dashboard") or {}
    if isinstance(dashboard, dict):
        alerts = dashboard.get("alerts") or []
        if alerts:
            error_alerts = [a for a in alerts if isinstance(a, dict) and a.get("level") == "error"]
            if error_alerts:
                patterns.append({
                    "type": "alert",
                    "severity": "error",
                    "count": len(error_alerts),
                    "description": f"当前有 {len(error_alerts)} 个错误级告警",
                })
                next_actions.append("查看 dashboard 中的红色告警")

    failures = collected.get("failure_patterns") or {}
    if isinstance(failures, dict):
        top_patterns = failures.get("patterns") or []
        if top_patterns:
            patterns.append({
                "type": "failure_pattern",
                "count": len(top_patterns),
                "description": f"最近一周发现 {len(top_patterns)} 类失败模式",
            })
            next_actions.append("review failure_analyzer 给出的前 3 类失败模式")

    progress = collected.get("proposal_progress") or []
    if isinstance(progress, list):
        pending_review = [p for p in progress if isinstance(p, dict) and p.get("status") == "pending_review"]
        optimizing = [p for p in progress if isinstance(p, dict) and p.get("status") == "optimizing"]
        stuck = [p for p in progress if isinstance(p, dict) and p.get("negative_feedback_alert")]
        if pending_review:
            patterns.append({"type": "proposal", "status": "pending_review", "count": len(pending_review)})
            next_actions.append("review pending_review 课题")
        if optimizing:
            patterns.append({"type": "proposal", "status": "optimizing", "count": len(optimizing)})
        if stuck:
            patterns.append({"type": "proposal", "status": "negative_feedback", "count": len(stuck)})
            next_actions.append("处理触发负反馈告警的课题")

    pipeline_summary = collected.get("pipeline_state_summary") or {}
    failed_jobs = pipeline_summary.get("failed", 0)
    if failed_jobs:
        patterns.append({"type": "weekend_pipeline", "status": "failed", "count": failed_jobs})
        next_actions.append("检查 weekend-pipeline.json 是否有 failed 任务")

    if not next_actions:
        next_actions.append("链路运转平稳，继续观察")

    return {
        "analyzed_at": now_utc(),
        "patterns": patterns,
        "next_actions": next_actions,
    }


def run_reflection_analyze_patterns(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """读取收集的状态，分析模式并落盘。"""
    _ensure_reflection_dir()
    collected = load_json(_collected_state_path(), default={})
    if not collected:
        # 兜底：若未找到已收集状态，现场收集
        collected = _collect_raw_state(state)
        if "error" in collected:
            return {"success": False, "error": collected["error"]}
        if not dry_run:
            save_json(_collected_state_path(), collected)

    analyzed = _analyze_collected_state(collected)

    if not dry_run:
        save_json(_analyzed_patterns_path(), analyzed)

    return {"success": True, "patterns_count": len(analyzed.get("patterns", [])), "dry_run": dry_run}


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------


def run_reflection_report(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """生成反思报告。优先使用已分析的模式，否则现场计算。"""
    _ensure_reflection_dir()

    analyzed = load_json(_analyzed_patterns_path(), default={})
    if not analyzed:
        # 兜底：若前面小任务未生成，现场完成收集+分析
        collected = _collect_raw_state(state)
        if "error" in collected:
            return {"success": False, "error": collected["error"]}
        analyzed = _analyze_collected_state(collected)

    collected = load_json(_collected_state_path(), default={})

    report = {
        "generated_at": now_utc(),
        "dashboard": collected.get("dashboard", {}),
        "failure_patterns": collected.get("failure_patterns", {}),
        "strategy_suggestions": collected.get("strategy_suggestions", {}),
        "proposal_progress": collected.get("proposal_progress", []),
        "pipeline_state_summary": collected.get("pipeline_state_summary", {}),
        "module_status_summary": collected.get("module_status_summary", {}),
        "patterns": analyzed.get("patterns", []),
        "next_actions": analyzed.get("next_actions", []),
    }

    if not dry_run:
        save_json(_reflection_report_path(), report)

    return {"success": True, "report": report, "dry_run": dry_run}


# ---------------------------------------------------------------------------
# 行动建议
# ---------------------------------------------------------------------------


def run_reflection_recommend(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """生成并保存具体 next actions。"""
    _ensure_reflection_dir()

    report = load_json(_reflection_report_path(), default={})

    actions = []
    failed_jobs = [j for j in state.get("jobs", []) if j.get("status") == "failed"]
    if failed_jobs:
        actions.append({
            "type": "repair",
            "description": f"有 {len(failed_jobs)} 个 weekend pipeline job 失败，建议运行 repair",
            "job_ids": [j["job_id"] for j in failed_jobs],
        })

    # 基于 proposal 进度生成建议
    try:
        lc = ProposalLifecycle()
        pending_review = lc.list_by_status("pending_review")
        if pending_review:
            actions.append({
                "type": "review",
                "description": f"有 {len(pending_review)} 个课题待校验",
                "proposal_ids": [p["proposal_id"] for p in pending_review],
            })
    except Exception:
        pass

    # 从反思报告中继承建议
    for action_text in report.get("next_actions", []):
        actions.append({
            "type": "report_suggestion",
            "description": action_text,
        })

    actions_data = {
        "generated_at": now_utc(),
        "actions": actions,
        "based_on_report": report.get("generated_at", ""),
    }

    if not dry_run:
        save_json(WEEKEND_REFLECTION_DIR / f"weekend-actions-{_date_str()}.json", actions_data)

    return {"success": True, "actions_count": len(actions), "dry_run": dry_run}
