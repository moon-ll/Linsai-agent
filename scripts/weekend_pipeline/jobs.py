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
    INPUT_DEEP_DIGEST_JOB_ID,
    JOB_STATUS_PENDING,
    STAGE_INPUT,
    STAGE_OUTPUT,
    STAGE_REFLECTION,
    STEP_ANALYZE,
    STEP_CLUSTER_ASSIGN,
    STEP_CLUSTER_DISTILL,
    STEP_COLLECT,
    STEP_COMPOSE,
    STEP_DEEP_DIGEST,
    STEP_EXTRACT,
    STEP_HEALTH,
    STEP_KB_DEEP_HEALTH,
    STEP_KB_MERGE,
    STEP_KB_TAXONOMY_APPLY,
    STEP_LINK_DEEP_REVIEW,
    STEP_METHODS_SETTLE,
    STEP_PANEL_PLAN,
    STEP_PROPOSAL_CALIBRATION,
    STEP_RECOMMEND,
    STEP_REPORT,
    STEP_RETRIEVE,
    STEP_SELECT,
    STEP_SYNC,
    STEP_TOPIC_MATCH,
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
    """输入阶段任务模板。

    v6.9.12 知识簇链路（取代旧 gap→select→retrieve→deep_read 四步）：
    collect → deep_digest → cluster_assign（增量归簇，零 LLM）→
    cluster_distill（簇内提炼知识卡）→ topic_match（簇 vs 全阶段课题
    路由）→ compose（路由落地：new 注册 / merge 融合 / expansion
    信息源挂载）。

    v6.9.98 多轮化：summarize 升级为 deep_digest（结构化深读，单轮
    10 篇、全文输入），产物带轮次号 summaries-{date}-r{round}.json
    （{round} 以 job 自身 round 字段格式化，由轮次接力维护）；整轮
    六步走完后由 rounds.should_open_next_round 判定是否开新轮。

    旧 job（gap_analysis/direction_select/retrieve_supplementary/
    deep_read/summarize）由 pipeline.sync_stage_jobs 的废弃清单清理
    state 残留。
    """
    _in = "memory/weekend-input"
    jobs = [
        _base_job("input_collect_sources", STAGE_INPUT, STEP_COLLECT, [],
                  artifact=f"{_in}/sources-{{date}}.json"),
        _base_job(INPUT_DEEP_DIGEST_JOB_ID, STAGE_INPUT, STEP_DEEP_DIGEST,
                  ["input_collect_sources"],
                  artifact=f"{_in}/summaries-{{date}}-r{{round}}.json"),
        _base_job("input_cluster_assign", STAGE_INPUT, STEP_CLUSTER_ASSIGN,
                  [INPUT_DEEP_DIGEST_JOB_ID],
                  artifact=f"{_in}/clusters-week-{{date}}.json"),
        _base_job("input_cluster_distill", STAGE_INPUT, STEP_CLUSTER_DISTILL,
                  ["input_cluster_assign"],
                  artifact=f"{_in}/distilled-clusters-{{date}}.json"),
        # v6.10.0（T3）：方法学专题沉淀——deep_digest 的 method_leads 归组
        # 融合进方法页（词表 + 按需回原文定位）；空 leads 也落空产物
        _base_job("input_methods_settle", STAGE_INPUT, STEP_METHODS_SETTLE,
                  ["input_cluster_distill"],
                  artifact=f"{_in}/methods-settle-{{date}}-r{{round}}.json"),
        _base_job("input_topic_match", STAGE_INPUT, STEP_TOPIC_MATCH,
                  ["input_methods_settle"],
                  artifact=f"{_in}/routes-{{date}}.json"),
        _base_job("input_compose_ideas", STAGE_INPUT, STEP_COMPOSE,
                  ["input_topic_match"],
                  artifact=f"{_in}/ideas-{{date}}.json"),
    ]
    return jobs


# v6.9.12: input 阶段废弃 job（知识簇链路取代），sync 时清理 state 残留
# v6.9.98: input_summarize_new_papers 加入废弃清单（deep_digest 取代）
DEPRECATED_INPUT_JOBS = {
    "input_gap_analysis",
    "input_direction_select",
    "input_retrieve_supplementary",
    "input_deep_read",
    "input_summarize_new_papers",
}


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
            artifact="knowledge/wiki/projects/NSFC-强场超快/proposals-index.md",
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

    v6.9.99 周末维护链（T2）：链尾新增三个 job（挂在 kb_merge 之后
    的平行分支，不阻塞既有 recommend 主链）——
    ① proposal_calibration：全部 optimizing 课题零 LLM 程序化校准
       （引用对账 + 范本指标），high 问题写入 06_feedback 注入下轮
       critic/writer prompt；产物声明为聚合报告（"done 必有产物"，
       每课题另有 calibration-{date}.md 明细）。
    ② link_deep_review：复用 retrospective.run_retrospective 的结构化
       周报（含策略建议预生成），报告落反思目录 link-deep-review-{date}.md
       （取代已撤除的周一 15:00 lc-retrospective cron）。
    ③ kb_taxonomy_apply：kb_taxonomy 候选分类执行（先备份再 apply，
       刷新 matched_paths；无候选写空产物文件保持不变式）。
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
        # v6.9.99（T2）维护链三连：calibration → deep_review → taxonomy_apply
        _base_job("reflection_proposal_calibration", STAGE_REFLECTION,
                  STEP_PROPOSAL_CALIBRATION,
                  ["reflection_kb_merge_duplicates"],
                  artifact=f"{_rf}/proposal-calibration-{{date}}.md"),
        _base_job("reflection_link_deep_review", STAGE_REFLECTION,
                  STEP_LINK_DEEP_REVIEW,
                  ["reflection_proposal_calibration"],
                  artifact=f"{_rf}/link-deep-review-{{date}}.md"),
        _base_job("reflection_kb_taxonomy_apply", STAGE_REFLECTION,
                  STEP_KB_TAXONOMY_APPLY,
                  ["reflection_link_deep_review"],
                  artifact=f"{_rf}/kb-taxonomy-apply-{{date}}.md"),
        # v6.10.15: 评审团执行计划——平台期课题（panel_request）周盘点，
        # 分层策略的执行推动环节（队列→催办→周计划→人工评审团）
        _base_job("reflection_panel_plan", STAGE_REFLECTION,
                  STEP_PANEL_PLAN,
                  ["reflection_kb_taxonomy_apply"],
                  artifact=f"{_rf}/panel-review-plan-{{date}}.md"),
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
