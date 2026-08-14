#!/usr/bin/env python3
"""生命周期 cron 框架纯工具函数。"""

from __future__ import annotations

import os
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


ERROR_HISTORY_CAP = 10
"""单个 job 的 error_history 保留上限（v6.8.54）。

背景：error_history 无上限增长曾把 _lifecycle.json 推向膨胀（重试风暴
场景单 job 可积累数十条），且每条含完整错误文本。保留最近 10 条足够
溯源，历史证据由归档文件兜底。"""

LIFECYCLE_ARCHIVE_PATH = PROJECT_ROOT / "research_proposals" / "_lifecycle_archive.json"
"""旧轮次 job 归档文件（v6.8.54）。

archive_old_round_jobs 此前直接丢弃旧轮次 job（error_history 证据丢失，
违背"产出即资产"）。现改为先归档再删除，全局上限 5000 条滚动裁剪。"""

ARCHIVE_JOB_CAP = 5000


def trim_error_history(job: Dict[str, Any], cap: int = ERROR_HISTORY_CAP) -> Dict[str, Any]:
    """裁剪 job 的 error_history 至最近 cap 条（原地修改并返回 job）。"""
    hist = job.get("error_history")
    if isinstance(hist, list) and len(hist) > cap:
        job["error_history"] = hist[-cap:]
    return job


def append_archive_jobs(proposal_id: str, jobs: List[Dict[str, Any]]) -> int:
    """把被裁剪的 job 追加进归档文件，返回实际归档数（文件锁保护）。"""
    if not jobs:
        return 0
    with file_lock("lifecycle-archive"):
        archive = load_json(LIFECYCLE_ARCHIVE_PATH, default={"jobs": []})
        ts = now_utc()
        for j in jobs:
            entry = dict(j)
            entry["_archived_from"] = proposal_id
            entry["_archived_at"] = ts
            archive.setdefault("jobs", []).append(entry)
        # 滚动裁剪：只保留最近 ARCHIVE_JOB_CAP 条
        if len(archive["jobs"]) > ARCHIVE_JOB_CAP:
            archive["jobs"] = archive["jobs"][-ARCHIVE_JOB_CAP:]
        save_json(LIFECYCLE_ARCHIVE_PATH, archive)
    return len(jobs)


def should_auto_unlock(job: Dict[str, Any], now: datetime, cooldown_hours: float = 24.0) -> bool:
    """判断双上限耗尽的 failed job 是否应自动解锁重跑（v6.8.54）。

    背景：attempts 与 repair_attempts 双双耗尽后 job 进入"需人工介入"
    终态，下游 pending 全部阻塞形成课题死锁——2026-08-14 两次人工解锁
    （key-transient r4-critic / moire r8-writer），根因均为已修复的超时
    分级问题。本策略把该终态交给 lc-repair 自动处置一次：

    条件（全部满足才解锁）：
      1. failed 且 attempts >= MAX_JOB_ATTEMPTS 且 repair_attempts >= MAX
      2. auto_unlock_count < 1（每个 job 终生至多自动解锁一次，
         防止坏输入导致无限重试循环）
      3. 最近一次失败距今超过 cooldown_hours（默认 24h，给根因修复
         留出落地时间，也避免短时间连环重置）
    """
    try:
        if job.get("status") != "failed":
            return False
        if int(job.get("attempts", 0)) < MAX_JOB_ATTEMPTS:
            return False
        if int(job.get("repair_attempts", 0)) < MAX_JOB_ATTEMPTS:
            return False
        if int(job.get("auto_unlock_count", 0)) >= 1:
            return False
        finished = str(job.get("finished_at") or "")
        if not finished:
            return False
        fin_dt = datetime.fromisoformat(finished.replace("Z", "+00:00"))
        age_h = (now - fin_dt).total_seconds() / 3600.0
        if age_h < cooldown_hours:
            return False
        return True
    except Exception:
        return False


def _ensure_hermes_scripts_dir() -> Path:
    HERMES_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    return HERMES_SCRIPTS_DIR


def _write_wrapper_script(name: str, content: str) -> Path:
    """把包装脚本写入 ~/.hermes/profiles/linsai/scripts/，并返回路径。

    如果文件已存在且可执行，跳过写入（避免沙盒权限问题）。
    """
    _ensure_hermes_scripts_dir()
    path = HERMES_SCRIPTS_DIR / name
    if path.exists() and os.access(path, os.X_OK):
        return path
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
    # v6.8.54: 保存前裁剪每个 job 的 error_history 至最近 10 条，
    # 防止重试风暴把 _lifecycle.json 推向膨胀
    for j in jobs:
        if isinstance(j, dict):
            trim_error_history(j)
    state["proposals"][proposal_id]["pipeline_jobs"] = jobs
    state["proposals"][proposal_id]["updated_at"] = now_utc()
    self._save_state(state)
    return True

def _job_by_id(self, jobs: List[Dict[str, Any]], job_id: str) -> Optional[Dict[str, Any]]:
    for j in jobs:
        if j.get("job_id") == job_id:
            return j
    return None


def archive_old_round_jobs(proposal_id: str, new_round: int) -> int:
    """v6.8.21b: 轮次推进后清理旧 job，只保留当前轮。

    保留 new_round（刚完成/进行中），更早轮次的 job 全部移除。
    pipeline_jobs 可能是 dict 或 list 格式。
    返回清理的 job 数量。
    """
    lifecycle_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    if not lifecycle_path.exists():
        return 0

    data = load_json(lifecycle_path)
    proposals = data.get("proposals", {})
    if proposal_id not in proposals:
        return 0

    prop = proposals[proposal_id]
    jobs_raw = prop.get("pipeline_jobs", {})

    # v6.8.54: 被清理的旧轮次 job 先归档再丢弃（此前直接删除，
    # error_history 证据丢失，违背"产出即资产"）
    to_archive: List[Dict[str, Any]] = []

    if isinstance(jobs_raw, dict):
        active = {}
        cleaned = 0
        for job_id, job in jobs_raw.items():
            if isinstance(job, dict):
                r = job.get("round", 0)
                if r < new_round:
                    cleaned += 1
                    to_archive.append(job)
                else:
                    active[job_id] = job
        if cleaned > 0:
            prop["pipeline_jobs"] = active
    elif isinstance(jobs_raw, list):
        active = []
        cleaned = 0
        for job in jobs_raw:
            if isinstance(job, dict):
                r = job.get("round", 0)
                if r < new_round:
                    cleaned += 1
                    to_archive.append(job)
                else:
                    active.append(job)
        if cleaned > 0:
            prop["pipeline_jobs"] = active
    else:
        return 0

    if cleaned == 0:
        return 0
    try:
        append_archive_jobs(proposal_id, to_archive)
    except Exception as e:
        if _log:
            _log.warning(f"归档旧轮次 job 失败（继续清理）: {e}")

    save_json(lifecycle_path, data)

    if _log:
        _log.info(
            f"[{proposal_id}] 清理了 {cleaned} 个旧轮次 job "
            f"(保留 R{new_round}+)"
        )
    return cleaned
