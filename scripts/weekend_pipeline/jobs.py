#!/usr/bin/env python3
"""周末任务模板与依赖图定义。

v6.9.7: _base_job 新增 artifact 声明性字段——有确定性产物路径的 job
在模板中声明产物（PROJECT_ROOT 相对路径，支持 {date} 占位符），
_verify_artifacts 据此做三阶段通用的"假 done"检测（dry-run 残留、
产物被误删等）。无确定性产物的 job（如萃取写动态 wiki 页）不声明，
自然跳过校验。
"""

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
    STEP_KB_DEEP_HEALTH,
    STEP_KB_MERGE,
    STEP_RECOMMEND,
    STEP_REPORT,
    STEP_RETRIEVE,
    STEP_SELECT,
    STEP_SUMMARIZE,
    STEP_SYNC,
    STEP_WEEKLY_REPORT,
)


def _base_job(
    job_id: str,
    stage: str,
    step: str,
    depends_on: List[str],
    artifact: str = "",
) -> Dict[str, Any]:
    job = {
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
    if artifact:
        # 声明式产物：PROJECT_ROOT 相对路径，{date} 以该 job 自身
        # finished_at 日期格式化（晚于执行日检查时不会日期错位）
        job["artifact"] = artifact
    return job


# ---------------------------------------------------------------------------
# Input stage jobs
# ---------------------------------------------------------------------------


def input_stage_jobs() -> List[Dict[str, Any]]:
    """输入阶段任务模板。"""
    _in = "memory/weekend-input"
    jobs = [
        _base_job("input_collect_sources", STAGE_INPUT, STEP_COLLECT, [],
                  artifact=f"{_in}/sources-{{date}}.json"),
        _base_job("input_summarize_new_papers", STAGE_INPUT, STEP_SUMMARIZE,
                  ["input_collect_sources"],
                  artifact=f"{_in}/summaries-{{date}}.json"),
        _base_job("input_gap_analysis", STAGE_INPUT, STEP_ANALYZE,
                  ["input_summarize_new_papers"],
                  artifact=f"{_in}/directions-{{date}}.json"),
        _base_job("input_direction_select", STAGE_INPUT, STEP_SELECT,
                  ["input_gap_analysis"],
                  artifact=f"{_in}/decisions-{{date}}.json"),
        _base_job("input_retrieve_supplementary", STAGE_INPUT, STEP_RETRIEVE,
                  ["input_direction_select"],
                  artifact=f"{_in}/supplementary-{{date}}.json"),
        _base_job("input_deep_read", STAGE_INPUT, STEP_DEEP_READ,
                  ["input_retrieve_supplementary"],
                  artifact=f"{_in}/deep-read-{{date}}.json"),
        _base_job("input_compose_ideas", STAGE_INPUT, STEP_COMPOSE,
                  ["input_deep_read"],
                  artifact=f"{_in}/ideas-{{date}}.json"),
    ]
    return jobs


# ---------------------------------------------------------------------------
# Output stage jobs
# ---------------------------------------------------------------------------


def output_stage_jobs(archived_proposal_ids: List[str]) -> List[Dict[str, Any]]:
    """输出阶段任务模板。

    每个已归档 proposal 生成一个独立的萃取任务。
    extract 类 job 产物为动态 wiki 页（无确定性路径），不声明 artifact。
    """
    jobs = [
        _base_job(
            "output_sync_proposals_to_kb", STAGE_OUTPUT, STEP_SYNC, [],
            artifact="knowledge/wiki/projects/NSFC-强场超快/proposals/proposals-index.md",
        ),
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
        _base_job(
            "output_collect_daily_sources", STAGE_OUTPUT, STEP_COLLECT, [],
            artifact="memory/weekend-output/daily-sources-{date}.json",
        ),
        _base_job(
            "output_extract_daily_knowledge",
            STAGE_OUTPUT,
            STEP_EXTRACT,
            ["output_collect_daily_sources"],
        ),
        _base_job(
            "output_kb_health_check", STAGE_OUTPUT, STEP_HEALTH, [],
            artifact="knowledge/.cache/kb-health-weekly.json",
        ),
        _base_job(
            "output_generate_weekly_report",
            STAGE_OUTPUT,
            STEP_WEEKLY_REPORT,
            [
                "output_sync_proposals_to_kb",
                "output_extract_daily_knowledge",
                "output_kb_health_check",
            ],
            artifact="memory/weekend-output/weekend-output-report-{date}.md",
        ),
    ])

    return jobs


# ---------------------------------------------------------------------------
# Reflection stage jobs
# ---------------------------------------------------------------------------


def reflection_stage_jobs() -> List[Dict[str, Any]]:
    """反思阶段任务模板。

    v6.9.6 新增知识库深度维护；v6.9.7 起 deep_health 与 merge 拆分为
    独立 step（handler 二元组注册要求同阶段同 step 唯一）。
    merge_duplicates 产物为知识库文件变化（无确定性路径），不声明 artifact。
    """
    _rf = "memory/weekend-reflection"
    return [
        _base_job("reflection_health_check", STAGE_REFLECTION, STEP_HEALTH, [],
                  artifact=f"{_rf}/reflection-health-{{date}}.json"),
        # ① 深度健康检查：重复概念检测 + derived 过期降级 + 图谱孤儿清理
        #    （kb_health_weekend / kb_maintenance 均为"能力在、编排无"，v6.9.6 补接线）
        _base_job("reflection_kb_deep_health", STAGE_REFLECTION, STEP_KB_DEEP_HEALTH, [],
                  artifact=f"{_rf}/kb-deep-health-{{date}}.json"),
        # ② 去重合并执行器：同名/近义页 LLM 辅助融合，周限 5 对控成本
        _base_job(
            "reflection_kb_merge_duplicates",
            STAGE_REFLECTION,
            STEP_KB_MERGE,
            ["reflection_kb_deep_health"],
        ),
        _base_job("reflection_collect_state", STAGE_REFLECTION, STEP_COLLECT,
                  ["reflection_health_check"],
                  artifact=f"{_rf}/collected-state-{{date}}.json"),
        _base_job("reflection_analyze_patterns", STAGE_REFLECTION, STEP_ANALYZE,
                  ["reflection_collect_state"],
                  artifact=f"{_rf}/analyzed-patterns-{{date}}.json"),
        _base_job("reflection_generate_report", STAGE_REFLECTION, STEP_REPORT,
                  ["reflection_analyze_patterns"],
                  artifact=f"{_rf}/weekend-reflection-{{date}}.json"),
        _base_job("reflection_recommend_actions", STAGE_REFLECTION, STEP_RECOMMEND,
                  ["reflection_generate_report"],
                  artifact=f"{_rf}/weekend-actions-{{date}}.json"),
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
