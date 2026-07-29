#!/usr/bin/env python3
"""反思阶段 job 执行器。"""

from __future__ import annotations

from typing import Any, Dict

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


# ---------------------------------------------------------------------------
# Job handlers
# ---------------------------------------------------------------------------


def run_reflection_report(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """生成反思报告（合并 collect/analyze/report 三个子步骤的结果）。"""
    _ensure_reflection_dir()

    try:
        from orchestrator import compute_dashboard
        from failure_analyzer import analyze_failures
        from strategy_optimizer import suggest_strategies
    except Exception as e:
        return {"success": False, "error": f"无法导入反思依赖: {e}"}

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

    report = {
        "generated_at": now_utc(),
        "dashboard": dashboard,
        "failure_patterns": failures,
        "strategy_suggestions": strategies,
        "proposal_progress": progress,
        "pipeline_state_summary": pipeline_state_summary,
        "next_actions": [
            "查看 dashboard 中的红色告警",
            "review pending_review 课题",
            "确认 expansion-candidates.json 中的扩展建议",
            "检查 weekend-pipeline.json 是否有 failed 任务",
        ],
    }

    date_str = now_utc()[:10]
    if not dry_run:
        save_json(WEEKEND_REFLECTION_DIR / f"weekend-reflection-{date_str}.json", report)

    return {"success": True, "report": report, "dry_run": dry_run}


def run_reflection_recommend(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """生成并保存具体 next actions。"""
    _ensure_reflection_dir()

    report_path = WEEKEND_REFLECTION_DIR / f"weekend-reflection-{now_utc()[:10]}.json"
    report = load_json(report_path, default={})

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

    actions_data = {
        "generated_at": now_utc(),
        "actions": actions,
        "based_on_report": report.get("generated_at", ""),
    }

    if not dry_run:
        save_json(WEEKEND_REFLECTION_DIR / f"weekend-actions-{now_utc()[:10]}.json", actions_data)

    return {"success": True, "actions_count": len(actions), "dry_run": dry_run}
