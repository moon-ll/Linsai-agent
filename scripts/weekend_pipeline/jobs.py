#!/usr/bin/env python3
"""周末任务模板与依赖图定义。"""

from __future__ import annotations

from typing import Any, Dict, List

from common import now_utc

from .constants import (
    JOB_STATUS_PENDING,
    STAGE_INPUT,
    STAGE_OUTPUT,
    STAGE_REFLECTION,
    STEP_ANALYZE,
    STEP_COLLECT,
    STEP_COMPOSE,
    STEP_DEEP_READ,
    STEP_EXTRACT,
    STEP_HEALTH,
    STEP_RECOMMEND,
    STEP_REPORT,
    STEP_RETRIEVE,
    STEP_SELECT,
    STEP_SUMMARIZE,
    STEP_SYNC,
    STEP_WEEKLY_REPORT,
)


def _base_job(job_id: str, stage: str, step: str, depends_on: List[str]) -> Dict[str, Any]:
    return {
        "job_id": job_id,
        "stage": stage,
        "step": step,
        "status": JOB_STATUS_PENDING,
        "depends_on": list(depends_on),
        "attempts": 0,
        "scheduled_at": "",
        "started_at": "",
        "finished_at": "",
        "last_error": "",
        "result": {},
        "created_at": now_utc(),
    }


# ---------------------------------------------------------------------------
# Input stage jobs
# ---------------------------------------------------------------------------


def input_stage_jobs() -> List[Dict[str, Any]]:
    """输入阶段任务模板。"""
    jobs = [
        _base_job("input_collect_sources", STAGE_INPUT, STEP_COLLECT, []),
        _base_job("input_summarize_new_papers", STAGE_INPUT, STEP_SUMMARIZE, ["input_collect_sources"]),
        _base_job("input_gap_analysis", STAGE_INPUT, STEP_ANALYZE, ["input_summarize_new_papers"]),
        _base_job("input_direction_select", STAGE_INPUT, STEP_SELECT, ["input_gap_analysis"]),
        _base_job("input_retrieve_supplementary", STAGE_INPUT, STEP_RETRIEVE, ["input_direction_select"]),
        _base_job("input_deep_read", STAGE_INPUT, STEP_DEEP_READ, ["input_retrieve_supplementary"]),
        _base_job("input_compose_ideas", STAGE_INPUT, STEP_COMPOSE, ["input_deep_read"]),
    ]
    return jobs


# ---------------------------------------------------------------------------
# Output stage jobs
# ---------------------------------------------------------------------------


def output_stage_jobs(archived_proposal_ids: List[str]) -> List[Dict[str, Any]]:
    """输出阶段任务模板。

    每个已归档 proposal 生成一个独立的萃取任务。
    """
    jobs = [
        _base_job("output_sync_proposals_to_kb", STAGE_OUTPUT, STEP_SYNC, []),
    ]

    for pid in archived_proposal_ids:
        safe_pid = "".join(c for c in pid if c.isalnum() or c in "-_")
        jobs.append(
            _base_job(
                f"output_extract_archived_proposal_{safe_pid}",
                STAGE_OUTPUT,
                STEP_EXTRACT,
                ["output_sync_proposals_to_kb"],
            )
        )

    jobs.extend([
        _base_job("output_collect_daily_sources", STAGE_OUTPUT, STEP_COLLECT, []),
        _base_job(
            "output_extract_daily_knowledge",
            STAGE_OUTPUT,
            STEP_EXTRACT,
            ["output_collect_daily_sources"],
        ),
        _base_job("output_kb_health_check", STAGE_OUTPUT, STEP_HEALTH, []),
        _base_job(
            "output_generate_weekly_report",
            STAGE_OUTPUT,
            STEP_WEEKLY_REPORT,
            [
                "output_sync_proposals_to_kb",
                "output_extract_daily_knowledge",
                "output_kb_health_check",
            ],
        ),
    ])

    return jobs


# ---------------------------------------------------------------------------
# Reflection stage jobs
# ---------------------------------------------------------------------------


def reflection_stage_jobs() -> List[Dict[str, Any]]:
    """反思阶段任务模板。"""
    return [
        _base_job("reflection_collect_state", STAGE_REFLECTION, STEP_COLLECT, []),
        _base_job("reflection_analyze_patterns", STAGE_REFLECTION, STEP_ANALYZE, ["reflection_collect_state"]),
        _base_job("reflection_generate_report", STAGE_REFLECTION, STEP_REPORT, ["reflection_analyze_patterns"]),
        _base_job("reflection_recommend_actions", STAGE_REFLECTION, STEP_RECOMMEND, ["reflection_generate_report"]),
    ]


# ---------------------------------------------------------------------------
# Stage dispatcher
# ---------------------------------------------------------------------------


def stage_job_templates(stage: str, archived_proposal_ids: List[str] | None = None) -> List[Dict[str, Any]]:
    """返回指定阶段的任务模板。"""
    if stage == STAGE_INPUT:
        return input_stage_jobs()
    if stage == STAGE_OUTPUT:
        return output_stage_jobs(archived_proposal_ids or [])
    if stage == STAGE_REFLECTION:
        return reflection_stage_jobs()
    raise ValueError(f"未知阶段: {stage}")


def job_display_name(job: Dict[str, Any]) -> str:
    """生成任务的可读名称。"""
    return job.get("job_id", "unknown")
