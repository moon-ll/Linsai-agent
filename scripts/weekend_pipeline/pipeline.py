#!/usr/bin/env python3
"""WeekendPipeline 主类。"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from common import now_utc
from proposal_lifecycle import ProposalLifecycle

from .constants import (
    JOB_STATUS_DONE,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    STAGE_INPUT,
    STAGE_OUTPUT,
    STAGE_REFLECTION,
    STAGES,
)
from .executor import execute_job, pick_next_job, repair_stale_and_failed, run_pending_jobs
from .jobs import stage_job_templates
from .state import (
    ensure_pipeline_state,
    find_job,
    find_jobs_by_stage,
    get_stage_status,
    load_pipeline_state,
    save_pipeline_state,
    set_stage_status,
    update_job,
)

# job 执行器注册
from . import input_jobs, output_jobs, reflection_jobs

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


class WeekendPipeline:
    """周末任务流水线：将 input/output/reflection 拆分为小 checkpoint job。"""

    def __init__(self, state_path: Optional[Any] = None) -> None:
        self.state_path = state_path
        self.state = load_pipeline_state(state_path)
        self.handlers: Dict[str, Callable[[Dict[str, Any], Dict[str, Any], bool], Dict[str, Any]]] = {}
        self._register_handlers()

    def _save(self) -> None:
        save_pipeline_state(self.state, self.state_path)

    def _register_handlers(self) -> None:
        self.handlers = {
            # input (按 step 注册)
            "collect": input_jobs.run_input_collect,
            "summarize": input_jobs.run_input_summarize,
            "analyze": input_jobs.run_input_gap_analysis,
            "select": input_jobs.run_input_direction_select,
            "retrieve": input_jobs.run_input_retrieve_supplementary,
            "deep_read": input_jobs.run_input_deep_read,
            "compose": input_jobs.run_input_compose,
            # output (按 step 注册；collect step 与 input/reflection 冲突，按 job_id 注册)
            "sync": output_jobs.run_output_sync_proposals,
            "extract": output_jobs.run_output_extract,
            "health": output_jobs.run_output_kb_health,
            "weekly_report": output_jobs.run_output_generate_weekly_report,
            "output_collect_daily_sources": output_jobs.run_output_collect_daily_sources,
            # reflection (report/recommend 按 step；collect/analyze 与 input 冲突，按 job_id 注册)
            "report": reflection_jobs.run_reflection_report,
            "recommend": reflection_jobs.run_reflection_recommend,
            "reflection_collect_state": reflection_jobs.run_reflection_collect_state,
            "reflection_analyze_patterns": reflection_jobs.run_reflection_analyze_patterns,
        }

    def sync_stage_jobs(self, stage: str) -> Dict[str, Any]:
        """幂等地为指定阶段创建任务。"""
        if stage not in STAGES:
            raise ValueError(f"未知阶段: {stage}")

        existing_ids = {j.get("job_id") for j in self.state.get("jobs", [])}
        archived_ids: List[str] = []
        if stage == STAGE_OUTPUT:
            try:
                archived_ids = [p["proposal_id"] for p in ProposalLifecycle().list_by_status("archived")]
            except Exception as e:
                if _log:
                    _log.warning(f"获取 archived proposals 失败: {e}")

        templates = stage_job_templates(stage, archived_proposal_ids=archived_ids)
        added = []
        for t in templates:
            if t["job_id"] not in existing_ids:
                self.state.setdefault("jobs", []).append(t)
                added.append(t["job_id"])

        set_stage_status(self.state, stage, JOB_STATUS_PENDING)
        self._save()
        return {"success": True, "stage": stage, "added": len(added), "jobs": added}

    def run_next(self, stage: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """执行下一个 pending 且依赖满足的任务。"""
        job = pick_next_job(self.state, stage=stage)
        if not job:
            return {"success": True, "message": "没有可执行任务", "executed": 0}

        result = execute_job(self.state, job, self.handlers, dry_run=dry_run)
        self._save()
        return {"success": result.get("success"), "job_id": job["job_id"], "result": result, "executed": 1}

    def run_stage(self, stage: str, dry_run: bool = False) -> Dict[str, Any]:
        """顺序执行阶段内所有 pending 任务。"""
        if stage not in STAGES:
            raise ValueError(f"未知阶段: {stage}")

        set_stage_status(self.state, stage, JOB_STATUS_RUNNING)
        self._save()

        result = run_pending_jobs(self.state, self.handlers, stage=stage, dry_run=dry_run)

        # 更新阶段状态：若该阶段全部 done，则标记 done
        stage_jobs = find_jobs_by_stage(self.state, stage)
        if stage_jobs and all(j.get("status") == JOB_STATUS_DONE for j in stage_jobs):
            set_stage_status(self.state, stage, JOB_STATUS_DONE)
        elif any(j.get("status") == JOB_STATUS_FAILED for j in stage_jobs):
            set_stage_status(self.state, stage, JOB_STATUS_FAILED)
        else:
            set_stage_status(self.state, stage, JOB_STATUS_PENDING)
        self._save()

        return {"success": True, "stage": stage, "dry_run": dry_run, **result}

    def list_jobs(self, stage: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出任务。"""
        jobs = self.state.get("jobs", [])
        if stage:
            jobs = [j for j in jobs if j.get("stage") == stage]
        return jobs

    def repair(self) -> Dict[str, Any]:
        """修复 stale/failed 任务。"""
        repaired = repair_stale_and_failed(self.state)
        self._save()
        return {"success": True, "repaired": repaired, "at": now_utc()}

    def ensure_all_stages(self) -> Dict[str, Any]:
        """确保三个阶段任务都存在。"""
        results = {}
        for s in STAGES:
            results[s] = self.sync_stage_jobs(s)
        return results


def get_pipeline(state_path: Optional[Any] = None) -> WeekendPipeline:
    return WeekendPipeline(state_path=state_path)
