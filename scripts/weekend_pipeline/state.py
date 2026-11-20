#!/usr/bin/env python3
"""周末任务流水线状态管理。"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
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


def save_pipeline_state_unlocked(data: Dict[str, Any], path: Optional[Path] = None) -> None:
    """在已持有 weekend-pipeline 锁的上下文中保存状态（v7.2.48）。

    供「锁内读-改-写」场景使用：调用方已持同名 flock，嵌套同名
    flock 会自死锁（POSIX flock 对同一 fd 重复加锁是升级而非阻塞，
    但本模块每次 file_lock 都新开 fd → 同一进程内二次 flock 会
    阻塞等待自己释放 → 死锁），故必须走本函数。

    落盘仍用 save_json（原子写：tempfile + fsync + os.replace）。
    """
    path = path or PIPELINE_STATE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now_utc()
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


def trim_processed_sources(state: Dict[str, Any], max_age_days: int = None) -> int:
    """滚动裁剪 processed_sources（v6.9.7 新增）。

    该字典历史上只增不减（实测已达 291 条），与 error_history 的裁剪
    策略对齐，仅保留最近 max_age_days 天的记录。旧格式（纯字符串
    hash，无时间戳）无法判定年龄，保留不动；再次处理同一来源时会
    自动升级为新格式（dict 带 processed_at）。

    Returns: 实际删除的记录数
    """
    from .constants import PROCESSED_SOURCES_MAX_AGE_DAYS
    if max_age_days is None:
        max_age_days = PROCESSED_SOURCES_MAX_AGE_DAYS

    processed = state.get("processed_sources", {})
    if not processed:
        return 0
    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    cutoff = cutoff_dt.isoformat(timespec="seconds").replace("+00:00", "Z")
    stale = [
        sid
        for sid, rec in processed.items()
        # 仅裁剪"明确可判定为过期"的记录：缺 processed_at 的（早期
        # 版本写入或异常数据）无法判定年龄，保留待其再次被处理时升级
        if isinstance(rec, dict) and rec.get("processed_at") and str(rec["processed_at"]) < cutoff
    ]
    for sid in stale:
        del processed[sid]
    return len(stale)


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
