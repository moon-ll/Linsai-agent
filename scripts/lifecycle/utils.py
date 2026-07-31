#!/usr/bin/env python3
"""生命周期 cron 框架纯工具函数。"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT


from .constants import (
    HERMES_SCRIPTS_DIR,
    JOB_STATUS_RUNNING,
    MAX_JOB_ATTEMPTS,
    STALE_RUNNING_SECONDS,
    WEEKEND_JOBS_PATH,
)

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


# 工具函数
# ---------------------------------------------------------------------------


def _ensure_hermes_scripts_dir() -> Path:
    HERMES_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    return HERMES_SCRIPTS_DIR


def _write_wrapper_script(name: str, content: str) -> Path:
    """把包装脚本写入 ~/.hermes/profiles/linsai/scripts/，并返回路径。"""
    _ensure_hermes_scripts_dir()
    path = HERMES_SCRIPTS_DIR / name
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)
    return path


def _dt_from_iso(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        # 兼容末尾带 Z 的 ISO
        v = value.replace("Z", "+00:00")
        return datetime.fromisoformat(v)
    except Exception:
        return None


def _is_stale(job: Dict[str, Any], stale_seconds: int = STALE_RUNNING_SECONDS) -> bool:
    if job.get("status") != JOB_STATUS_RUNNING:
        return False
    started = _dt_from_iso(job.get("started_at", ""))
    if not started:
        return True
    return (datetime.now(timezone.utc) - started).total_seconds() > stale_seconds


def _make_job_id(proposal_id: str, round_num: int, section_key: str, step: str) -> str:
    return f"{proposal_id}-r{round_num}-{section_key}-{step}"


def _make_cron_name(job: Dict[str, Any]) -> str:
    """hermes cron 名称（短，便于 list 识别）。"""
    pid = job.get("proposal_id", "unknown")[:24]
    return f"lc-{pid}-r{job.get('round', 0)}-{job.get('section_key', 'x')}-{job.get('step', 'x')}"


def _short_uuid() -> str:
    return uuid.uuid4().hex[:8]


def _load_weekend_jobs() -> Dict[str, Any]:
    """加载周末任务状态。"""
    with file_lock("weekend-jobs"):
        if WEEKEND_JOBS_PATH.exists():
            try:
                return load_json(WEEKEND_JOBS_PATH, default={"jobs": {}})
            except Exception:
                pass
    return {"jobs": {}}


def _save_weekend_jobs(data: Dict[str, Any]) -> None:
    """保存周末任务状态。"""
    with file_lock("weekend-jobs"):
        WEEKEND_JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
        data["updated_at"] = now_utc()
        save_json(WEEKEND_JOBS_PATH, data)


def _is_weekend() -> bool:
    """判断当前是否为周末（周六或周日）。"""
    return datetime.now(timezone.utc).weekday() >= 5


def _get_jobs(self, proposal_id: str) -> List[Dict[str, Any]]:
    state = self._get_proposal_state(proposal_id)
    if not state:
        return []
    return state.get("pipeline_jobs", [])

def _save_jobs(self, proposal_id: str, jobs: List[Dict[str, Any]]) -> bool:
    state = self._load_state()
    if proposal_id not in state.get("proposals", {}):
        return False
    state["proposals"][proposal_id]["pipeline_jobs"] = jobs
    state["proposals"][proposal_id]["updated_at"] = now_utc()
    self._save_state(state)
    return True

def _job_by_id(self, jobs: List[Dict[str, Any]], job_id: str) -> Optional[Dict[str, Any]]:
    for j in jobs:
        if j.get("job_id") == job_id:
            return j
    return None
