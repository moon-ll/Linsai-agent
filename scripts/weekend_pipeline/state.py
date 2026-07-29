#!/usr/bin/env python3
"""周末任务流水线状态管理。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

from .constants import (
    JOB_STATUS_PENDING,
    PIPELINE_STATE_PATH,
    STAGES,
)

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


def load_pipeline_state(path: Optional[Path] = None) -> Dict[str, Any]:
    """加载周末流水线状态。"""
    path = path or PIPELINE_STATE_PATH
    data = load_json(path, default={})
    if "jobs" not in data:
        data["jobs"] = []
    if "processed_sources" not in data:
        data["processed_sources"] = {}
    if "stage_status" not in data:
        data["stage_status"] = {s: JOB_STATUS_PENDING for s in STAGES}
    return data


def save_pipeline_state(data: Dict[str, Any], path: Optional[Path] = None) -> None:
    """原子保存周末流水线状态。"""
    path = path or PIPELINE_STATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now_utc()
    with file_lock("weekend-pipeline"):
        save_json(path, data)


def ensure_pipeline_state(path: Optional[Path] = None) -> Dict[str, Any]:
    """确保状态文件存在并返回状态。"""
    path = path or PIPELINE_STATE_PATH
    if not path.exists():
        data = load_pipeline_state(path)
        save_pipeline_state(data, path)
        return data
    return load_pipeline_state(path)


def source_hash(content: str) -> str:
    """计算来源内容哈希。"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def is_source_processed(source_id: str, content: str, state: Dict[str, Any]) -> bool:
    """判断来源是否已处理过（依据 source_id 与内容哈希）。"""
    processed = state.get("processed_sources", {})
    record = processed.get(source_id)
    if not record:
        return False
    expected_hash = source_hash(content)
    if isinstance(record, dict):
        return record.get("hash") == expected_hash
    # 兼容旧格式：仅存储字符串
    return record == expected_hash


def mark_source_processed(source_id: str, content: str, state: Dict[str, Any]) -> None:
    """标记来源为已处理。"""
    state.setdefault("processed_sources", {})[source_id] = {
        "hash": source_hash(content),
        "processed_at": now_utc(),
    }


def find_job(state: Dict[str, Any], job_id: str) -> Optional[Dict[str, Any]]:
    """根据 job_id 查找任务。"""
    for job in state.get("jobs", []):
        if job.get("job_id") == job_id:
            return job
    return None


def find_jobs_by_stage(state: Dict[str, Any], stage: str) -> List[Dict[str, Any]]:
    """返回指定阶段的全部任务。"""
    return [j for j in state.get("jobs", []) if j.get("stage") == stage]


def find_jobs_by_step(state: Dict[str, Any], step: str) -> List[Dict[str, Any]]:
    """返回指定 step 的全部任务。"""
    return [j for j in state.get("jobs", []) if j.get("step") == step]


def update_job(
    state: Dict[str, Any],
    job_id: str,
    status: str,
    error: str = "",
    result: Optional[Dict[str, Any]] = None,
) -> bool:
    """更新任务状态。"""
    job = find_job(state, job_id)
    if not job:
        return False
    job["status"] = status
    if status == "running":
        job["started_at"] = now_utc()
    if status in ("done", "failed"):
        job["finished_at"] = now_utc()
    if error:
        job["last_error"] = error[:500]
    if status == "failed":
        job["attempts"] = job.get("attempts", 0) + 1
    if result is not None:
        job["result"] = result
    return True


def get_stage_status(state: Dict[str, Any], stage: str) -> str:
    """获取阶段整体状态。"""
    return state.get("stage_status", {}).get(stage, JOB_STATUS_PENDING)


def set_stage_status(state: Dict[str, Any], stage: str, status: str) -> None:
    """设置阶段整体状态。"""
    state.setdefault("stage_status", {})[stage] = status
