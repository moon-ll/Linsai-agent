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
from typing import Any, Dict, Tuple

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
    """加载 weekend-jobs 状态（调用方需自行加锁）。"""
    if WEEKEND_JOBS_PATH.exists():
        try:
            return load_json(WEEKEND_JOBS_PATH, default={"jobs": {}})
        except Exception:
            pass
    return {"jobs": {}}


def _save_weekend_jobs(data: Dict[str, Any]) -> None:
    """保存 weekend-jobs 状态（调用方需自行加锁）。"""
    WEEKEND_JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now_utc()
    save_json(WEEKEND_JOBS_PATH, data)


def _update_job_status(job_key: str, status: str, error: str = "",
                       started_at: str = "", finished_at: str = "") -> None:
    with file_lock("weekend-jobs"):
        data = _load_weekend_jobs()
        job = data.setdefault("jobs", {}).setdefault(job_key, {})
        job["status"] = status
        job["last_error"] = error[:500]
        if status == JOB_STATUS_RUNNING:
            job["started_at"] = now_utc()
        if status in (JOB_STATUS_DONE, JOB_STATUS_FAILED):
            # 阶段级 done 以子 job 真实起止为准（11-08 实证：入口 tick 见阶段
            # 已完成即用 now 落盘，导致 finished_at 比末个 job 晚半小时，
            # 并与 reconcile 的时间戳校正来回互振）。
            if started_at:
                job["started_at"] = started_at
            job["finished_at"] = finished_at or now_utc()
        if status == JOB_STATUS_FAILED:
            job["attempts"] = job.get("attempts", 0) + 1
        _save_weekend_jobs(data)


def _stage_time_span(pipeline, stage: str) -> Tuple[str, str]:
    """阶段内全部 done job 的真实起止时间（无可用值时返回空串）。"""
    stage_jobs = [j for j in pipeline.list_jobs(stage=stage)
                  if j.get("stage") == stage and j.get("status") == JOB_STATUS_DONE]
    starts = [j.get("started_at") for j in stage_jobs if j.get("started_at")]
    fins = [j.get("finished_at") for j in stage_jobs if j.get("finished_at")]
    return (min(starts) if starts else "", max(fins) if fins else "")


def _stage_actually_done(pipeline, stage: str) -> bool:
    """检查 weekend-pipeline 中某阶段是否全部 job 都已完成。"""
    stage_jobs = [j for j in pipeline.list_jobs(stage=stage) if j.get("stage") == stage]
    if not stage_jobs:
        return False
    return all(j.get("status") == JOB_STATUS_DONE for j in stage_jobs)


def run_input_task(dry_run: bool = False) -> Dict[str, Any]:
    """运行周末输入任务。

    v6.7.7: 委托给 WeekendPipeline input 阶段，同时保持 weekend-jobs.json 状态兼容。
    v6.10.16: dry-run 零落盘语义补全——预览模式不再写 weekend-jobs.json
    （旧版 RUNNING/FAILED 终态照写），也不再触发 sync_stage_jobs 的
    自愈重置（产物缺失级联重置会把磁盘 done job 落盘回 pending）。
    """
    from weekend_pipeline import WeekendPipeline
    pipeline = WeekendPipeline()
    if not dry_run:
        _update_job_status(WEEKEND_JOB_INPUT, JOB_STATUS_RUNNING)
    try:
        if not dry_run:
            pipeline.sync_stage_jobs("input")
        result = pipeline.run_stage("input", dry_run=dry_run)
        if _stage_actually_done(pipeline, "input"):
            if not dry_run:
                st, fin = _stage_time_span(pipeline, "input")
                _update_job_status(WEEKEND_JOB_INPUT, JOB_STATUS_DONE,
                                   started_at=st, finished_at=fin)
        else:
            stage_status = pipeline.state.get("stage_status", {}).get("input", "unknown")
            if dry_run:
                result["note"] = f"dry-run 未落盘：磁盘阶段状态为 {stage_status}，待执行 job 保持原状"
            else:
                _update_job_status(WEEKEND_JOB_INPUT, JOB_STATUS_FAILED, f"阶段未全部完成: {stage_status}")
                result["success"] = False
                result["error"] = f"阶段未全部完成: {stage_status}"
        return result
    except Exception as e:
        if not dry_run:
            _update_job_status(WEEKEND_JOB_INPUT, JOB_STATUS_FAILED, str(e))
        _log_warn(f"周末输入任务失败: {e}")
        return {"success": False, "error": str(e), "dry_run": dry_run}


def run_output_task(dry_run: bool = False) -> Dict[str, Any]:
    """运行周末输出任务。

    v6.7.7: 委托给 WeekendPipeline output 阶段，同时保持 weekend-jobs.json 状态兼容。
    v6.10.16: dry-run 零落盘语义补全（同 run_input_task；09-14 实证：
    --output --dry-run 曾把 weekend_output 误标 failed + attempts+1，
    并触发产物缺失级联重置把 output/sync 落盘回 pending）。
    """
    from weekend_pipeline import WeekendPipeline
    pipeline = WeekendPipeline()
    if not dry_run:
        _update_job_status(WEEKEND_JOB_OUTPUT, JOB_STATUS_RUNNING)
    try:
        if not dry_run:
            pipeline.sync_stage_jobs("output")
        result = pipeline.run_stage("output", dry_run=dry_run)
        if _stage_actually_done(pipeline, "output"):
            if not dry_run:
                st, fin = _stage_time_span(pipeline, "output")
                _update_job_status(WEEKEND_JOB_OUTPUT, JOB_STATUS_DONE,
                                   started_at=st, finished_at=fin)
        else:
            stage_status = pipeline.state.get("stage_status", {}).get("output", "unknown")
            if dry_run:
                result["note"] = f"dry-run 未落盘：磁盘阶段状态为 {stage_status}，待执行 job 保持原状"
            else:
                _update_job_status(WEEKEND_JOB_OUTPUT, JOB_STATUS_FAILED, f"阶段未全部完成: {stage_status}")
                result["success"] = False
                result["error"] = f"阶段未全部完成: {stage_status}"
        return result
    except Exception as e:
        if not dry_run:
            _update_job_status(WEEKEND_JOB_OUTPUT, JOB_STATUS_FAILED, str(e))
        _log_warn(f"周末输出任务失败: {e}")
        return {"success": False, "error": str(e), "dry_run": dry_run}


def run_reflection_task(dry_run: bool = False) -> Dict[str, Any]:
    """运行周末反思任务。

    v6.7.7: 委托给 WeekendPipeline reflection 阶段，同时保持 weekend-jobs.json 状态兼容。
    v6.10.16: dry-run 零落盘语义补全（同 run_input_task）。
    """
    from weekend_pipeline import WeekendPipeline
    pipeline = WeekendPipeline()
    if not dry_run:
        _update_job_status(WEEKEND_JOB_REFLECTION, JOB_STATUS_RUNNING)
    try:
        if not dry_run:
            pipeline.sync_stage_jobs("reflection")
        result = pipeline.run_stage("reflection", dry_run=dry_run)
        if _stage_actually_done(pipeline, "reflection"):
            if not dry_run:
                st, fin = _stage_time_span(pipeline, "reflection")
                _update_job_status(WEEKEND_JOB_REFLECTION, JOB_STATUS_DONE,
                                   started_at=st, finished_at=fin)
        else:
            stage_status = pipeline.state.get("stage_status", {}).get("reflection", "unknown")
            if dry_run:
                result["note"] = f"dry-run 未落盘：磁盘阶段状态为 {stage_status}，待执行 job 保持原状"
            else:
                _update_job_status(WEEKEND_JOB_REFLECTION, JOB_STATUS_FAILED, f"阶段未全部完成: {stage_status}")
                result["success"] = False
                result["error"] = f"阶段未全部完成: {stage_status}"
        return result
    except Exception as e:
        if not dry_run:
            _update_job_status(WEEKEND_JOB_REFLECTION, JOB_STATUS_FAILED, str(e))
        _log_warn(f"周末反思任务失败: {e}")
        return {"success": False, "error": str(e), "dry_run": dry_run}


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


def reconcile_weekend_jobs(dry_run: bool = False) -> Dict[str, Any]:
    """以 weekend-pipeline.json（权威）对齐 weekend-jobs.json（兼容层）。

    v6.9.77 背景：周六 output 阶段的 stage job 由 pipeline 自身推进
    （stage cron/worker/repair 补跑），不经本编排器的 run_output_task
    时，weekend-jobs.json 的对应条目停留在陈旧状态（08-30 实证：
    pipeline 三段全 done，兼容层 weekend_output 仍记 pending，
    started_at 为空，误导读者与 repair 扫描）。本函数读取权威阶段
    状态修正兼容层，幂等可重复执行。

    Returns:
        各阶段对齐结果
    """
    from weekend_pipeline import WeekendPipeline
    pipeline = WeekendPipeline()
    changes: Dict[str, Any] = {}
    stage_map = {
        "input": WEEKEND_JOB_INPUT,
        "output": WEEKEND_JOB_OUTPUT,
        "reflection": WEEKEND_JOB_REFLECTION,
    }
    with file_lock("weekend-jobs"):
        data = _load_weekend_jobs()
        for stage, job_key in stage_map.items():
            stage_jobs = [
                j for j in pipeline.list_jobs(stage=stage)
                if j.get("stage") == stage
            ]
            if not stage_jobs:
                continue
            done_cnt = sum(1 for j in stage_jobs if j.get("status") == "done")
            failed_cnt = sum(1 for j in stage_jobs if j.get("status") == "failed")
            last_fin = max(
                (j.get("finished_at", "") for j in stage_jobs
                 if j.get("finished_at")), default="")
            if done_cnt == len(stage_jobs):
                target, err = JOB_STATUS_DONE, ""
            elif failed_cnt > 0:
                target, err = JOB_STATUS_FAILED, f"{failed_cnt} 个 job 失败"
            elif done_cnt > 0:
                target, err = "running", ""
            else:
                target, err = JOB_STATUS_PENDING, ""
            cur = data.get("jobs", {}).get(job_key, {})
            # 仅有状态变化才重写会漏掉时间戳漂移：阶段在两轮之间被标 done 后，
            # 新一轮 job 继续推进，done→done 不再触发写入，finished_at 会永久
            # 停留在旧轮次（11-08 实证：input 标 done@21:30Z，实际末个 job
            # 00:40Z 才完成）。故 done 且末个 job 更新时也纳入变更。
            fin_drift = (target == JOB_STATUS_DONE and last_fin
                         and cur.get("finished_at") != last_fin)
            # 变更记录必须在 dry-run 下也生成，否则预览恒返回空
            # （11-08 实证：--reconcile --dry-run 永远看不到将要发生的漂移）
            if cur.get("status") != target or fin_drift:
                if cur.get("status") != target:
                    changes[job_key] = {"from": cur.get("status", "?"), "to": target}
                if target == JOB_STATUS_DONE and last_fin:
                    old_fin = cur.get("finished_at")
                    if old_fin != last_fin:
                        changes.setdefault(job_key, {
                            "from": target, "to": target,
                        })["finished_at"] = {"from": old_fin, "to": last_fin}
                if not dry_run:
                    cur["status"] = target
                    cur["last_error"] = err
                    if target == JOB_STATUS_DONE and last_fin:
                        cur["finished_at"] = last_fin
                    data.setdefault("jobs", {})[job_key] = cur
        if not dry_run and changes:
            _save_weekend_jobs(data)
    return {"changed": changes, "dry_run": dry_run}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="周末总控编排器")
    parser.add_argument("--input", action="store_true", help="运行输入任务")
    parser.add_argument("--output", action="store_true", help="运行输出任务")
    parser.add_argument("--reflection", action="store_true", help="运行反思任务")
    parser.add_argument("--weekly", action="store_true", help="按当前日期自动执行对应任务")
    parser.add_argument("--reconcile", action="store_true",
                        help="以 weekend-pipeline.json 对齐 weekend-jobs.json 状态（v6.9.77）")
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
    elif args.reconcile:
        result = reconcile_weekend_jobs(dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
