#!/usr/bin/env python3
"""周末总控编排器（v6.7.7）。

按顺序调度周末任务：
    - 周六 9:00  --input      研究设想自动发现
    - 周六 14:00 --output     归档知识萃取 + 日常可靠知识写入 + KB 健康
    - 周日 9:00  --reflection 链路反思与优化建议

同时维护 weekend_jobs 状态文件（memory/weekend-jobs.json），供 repair cron 扫描。

用法：
    python3 scripts/weekend_orchestrator.py --input
    python3 scripts/weekend_orchestrator.py --output
    python3 scripts/weekend_orchestrator.py --reflection
    python3 scripts/weekend_orchestrator.py --weekly    # 按当前日期执行对应任务
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

try:
    from logger import get_logger
    _log = get_logger("weekend_orchestrator")
except Exception:
    _log = None

# 周末任务状态文件（与 lifecycle_cron_framework 共用）
WEEKEND_JOBS_PATH = PROJECT_ROOT / "memory" / "weekend-jobs.json"

WEEKEND_JOB_INPUT = "weekend_input"
WEEKEND_JOB_OUTPUT = "weekend_output"
WEEKEND_JOB_REFLECTION = "weekend_reflection"

JOB_STATUS_PENDING = "pending"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_DONE = "done"
JOB_STATUS_FAILED = "failed"


def _log_info(msg: str) -> None:
    if _log:
        _log.info(msg)


def _log_warn(msg: str) -> None:
    if _log:
        _log.warning(msg)


def _load_weekend_jobs() -> Dict[str, Any]:
    with file_lock("weekend-jobs"):
        if WEEKEND_JOBS_PATH.exists():
            try:
                return load_json(WEEKEND_JOBS_PATH, default={"jobs": {}})
            except Exception:
                pass
    return {"jobs": {}}


def _save_weekend_jobs(data: Dict[str, Any]) -> None:
    with file_lock("weekend-jobs"):
        WEEKEND_JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
        data["updated_at"] = now_utc()
        save_json(WEEKEND_JOBS_PATH, data)


def _update_job_status(job_key: str, status: str, error: str = "") -> None:
    with file_lock("weekend-jobs"):
        data = _load_weekend_jobs()
        job = data.setdefault("jobs", {}).setdefault(job_key, {})
        job["status"] = status
        job["last_error"] = error[:500]
        if status == JOB_STATUS_RUNNING:
            job["started_at"] = now_utc()
        if status in (JOB_STATUS_DONE, JOB_STATUS_FAILED):
            job["finished_at"] = now_utc()
        if status == JOB_STATUS_FAILED:
            job["attempts"] = job.get("attempts", 0) + 1
        _save_weekend_jobs(data)


def run_input_task(dry_run: bool = False) -> Dict[str, Any]:
    """运行周末输入任务。

    v6.7.7: 委托给 WeekendPipeline input 阶段，同时保持 weekend-jobs.json 状态兼容。
    """
    from weekend_pipeline import WeekendPipeline
    pipeline = WeekendPipeline()
    _update_job_status(WEEKEND_JOB_INPUT, JOB_STATUS_RUNNING)
    try:
        pipeline.sync_stage_jobs("input")
        result = pipeline.run_stage("input", dry_run=dry_run)
        _update_job_status(WEEKEND_JOB_INPUT, JOB_STATUS_DONE)
        return result
    except Exception as e:
        _update_job_status(WEEKEND_JOB_INPUT, JOB_STATUS_FAILED, str(e))
        _log_warn(f"周末输入任务失败: {e}")
        return {"success": False, "error": str(e)}


def run_output_task(dry_run: bool = False) -> Dict[str, Any]:
    """运行周末输出任务。

    v6.7.7: 委托给 WeekendPipeline output 阶段，同时保持 weekend-jobs.json 状态兼容。
    """
    from weekend_pipeline import WeekendPipeline
    pipeline = WeekendPipeline()
    _update_job_status(WEEKEND_JOB_OUTPUT, JOB_STATUS_RUNNING)
    try:
        pipeline.sync_stage_jobs("output")
        result = pipeline.run_stage("output", dry_run=dry_run)
        _update_job_status(WEEKEND_JOB_OUTPUT, JOB_STATUS_DONE)
        return result
    except Exception as e:
        _update_job_status(WEEKEND_JOB_OUTPUT, JOB_STATUS_FAILED, str(e))
        _log_warn(f"周末输出任务失败: {e}")
        return {"success": False, "error": str(e)}


def run_reflection_task(dry_run: bool = False) -> Dict[str, Any]:
    """运行周末反思任务。

    v6.7.7: 委托给 WeekendPipeline reflection 阶段，同时保持 weekend-jobs.json 状态兼容。
    """
    from weekend_pipeline import WeekendPipeline
    pipeline = WeekendPipeline()
    _update_job_status(WEEKEND_JOB_REFLECTION, JOB_STATUS_RUNNING)
    try:
        pipeline.sync_stage_jobs("reflection")
        result = pipeline.run_stage("reflection", dry_run=dry_run)
        _update_job_status(WEEKEND_JOB_REFLECTION, JOB_STATUS_DONE)
        return result
    except Exception as e:
        _update_job_status(WEEKEND_JOB_REFLECTION, JOB_STATUS_FAILED, str(e))
        _log_warn(f"周末反思任务失败: {e}")
        return {"success": False, "error": str(e)}


def run_weekly_mode(dry_run: bool = False) -> Dict[str, Any]:
    """根据当前日期自动执行对应的周末任务。"""
    weekday = datetime.now(timezone.utc).weekday()
    # 周六=5, 周日=6
    if weekday == 5:
        return {
            "mode": "saturday",
            "input": run_input_task(dry_run=dry_run),
            "output": run_output_task(dry_run=dry_run),
        }
    elif weekday == 6:
        return {
            "mode": "sunday",
            "reflection": run_reflection_task(dry_run=dry_run),
        }
    else:
        return {"mode": "weekday", "message": "今天不是周末，跳过周末任务"}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="周末总控编排器")
    parser.add_argument("--input", action="store_true", help="运行输入任务")
    parser.add_argument("--output", action="store_true", help="运行输出任务")
    parser.add_argument("--reflection", action="store_true", help="运行反思任务")
    parser.add_argument("--weekly", action="store_true", help="按当前日期自动执行对应任务")
    parser.add_argument("--dry-run", action="store_true", help="只预览不写入")
    args = parser.parse_args()

    result = {}
    if args.input:
        result = run_input_task(dry_run=args.dry_run)
    elif args.output:
        result = run_output_task(dry_run=args.dry_run)
    elif args.reflection:
        result = run_reflection_task(dry_run=args.dry_run)
    elif args.weekly:
        result = run_weekly_mode(dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
