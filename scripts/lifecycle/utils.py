#!/usr/bin/env python3
"""生命周期 cron 框架纯工具函数。"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
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
    """判断修复系统已放弃的 failed job 是否应自动解锁重跑（v6.8.54，v6.9.49 放宽）。

    背景：attempts 与 repair_attempts 耗尽后 job 进入"需人工介入"
    终态，下游 pending 全部阻塞形成课题死锁——2026-08-14 两次人工解锁
    （key-transient r4-critic / moire r8-writer），根因均为已修复的超时
    分级问题。本策略把该终态交给 lc-repair 自动处置一次。

    v6.9.49 死角修复：原条件要求 attempts>=MAX 且 repair_attempts>=MAX
    双上限齐备，但存在系统性死角——repair 在 repair_attempts 2→3 时
    重置 attempts=0，此后 job 只需再失败一次（attempts=1, rep_att=3），
    三条恢复路径同时失效：repair 拒绝（rep_att 达上限）、依赖链重试被
    _is_proposal_stuck 的 rep_att>=MAX 判卡死跳过、auto_unlock 拒绝
    （attempts<MAX）。2026-08-24 21:55 order-param r7-references-critic
    实证死锁（94% 完成的课题被单 job 永久阻塞）。修复：解锁资格以
    repair_attempts>=MAX（修复系统已明确放弃）为准，不再要求 attempts
    同时达上限——run_repair 仅在 rep_att>=MAX 分支调用本函数，语义不变，
    仅消除死角。

    条件（全部满足才解锁）：
      1. failed 且 repair_attempts >= MAX_JOB_ATTEMPTS（修复系统已放弃；
         attempts 是否达上限不再作为门槛，v6.9.49）
      2. auto_unlock_count < 1（每个 job 终生至多自动解锁一次，
         防止坏输入导致无限重试循环）
      3. 最近一次失败距今超过 cooldown_hours（默认 24h，给根因修复
         留出落地时间，也避免短时间连环重置）
    """
    try:
        if job.get("status") != "failed":
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


NEG_FEEDBACK_CLEAR_COOLDOWN_H = 24.0
"""负反馈告警自动清除冷却时长（v6.9.0 R2）。

触发即人工清除此前是唯一恢复路径，负反馈课题会无限期停滞。现冷却期满
后由 lifecycle_monitor 自动清除一次并降级策略（退回研究设想评审），
再触发则不再自动清除（negative_feedback_auto_clear_count 上限 1）。"""

AUTO_ROLLBACK_MARGIN = 0.03
"""自动回退触发幅度（v6.9.0 R3）：当前分距历史最佳不足该幅度时不回退。"""


def should_auto_clear_negative_feedback(
    prop_state: Dict[str, Any],
    now: datetime,
    cooldown_hours: float = NEG_FEEDBACK_CLEAR_COOLDOWN_H,
) -> bool:
    """判断负反馈告警是否应自动清除（v6.9.0 R2）。

    条件（全部满足）：
      1. negative_feedback_alert 为 True
      2. negative_feedback_auto_clear_count < 1（每课题至多自动清除一次）
      3. negative_feedback_at 距今超过 cooldown_hours
    无时间戳（遗留数据）返回 False，由 monitor 首次发现时补戳。
    """
    try:
        if not prop_state.get("negative_feedback_alert"):
            return False
        if int(prop_state.get("negative_feedback_auto_clear_count", 0)) >= 1:
            return False
        alert_dt = _dt_from_iso(str(prop_state.get("negative_feedback_at") or ""))
        if alert_dt is None:
            return False
        age_h = (now - alert_dt).total_seconds() / 3600.0
        return age_h >= cooldown_hours
    except Exception:
        return False


def find_proposal_dir(proposal_id: str, root: Optional[Path] = None) -> Optional[Path]:
    """在四个阶段目录中定位课题目录（v6.9.0 R3）。"""
    base = root or (PROJECT_ROOT / "research_proposals")
    for stage in ("optimizing", "pending_review", "drafts", "archived"):
        d = base / stage / proposal_id
        if d.is_dir():
            return d
    return None


def should_auto_rollback(
    prop_state: Dict[str, Any],
    margin: float = AUTO_ROLLBACK_MARGIN,
) -> Optional[Dict[str, Any]]:
    """判断连续下降是否应自动回退最佳轮次草稿（v6.9.0 R3）。

    条件（全部满足才返回回退计划）：
      1. score_history >= 3 且最近两轮连续下降（s[-1] < s[-2] <= s[-3]）
      2. 当前分距历史最佳超过 margin（排除天花板附近正常波动）
      3. 最佳轮不是最新轮（最新就是最佳时无可回退）
      4. auto_rollback_count < 1（每课题至多自动回退一次）
    返回 {"best_round", "best_score", "current"} 或 None。
    """
    try:
        history = prop_state.get("score_history") or []
        if len(history) < 3:
            return None
        if int(prop_state.get("auto_rollback_count", 0)) >= 1:
            return None
        scores = [float(e.get("score") or 0.0) for e in history]
        if not (scores[-1] < scores[-2] <= scores[-3]):
            return None
        best_entry = max(history, key=lambda e: float(e.get("score") or 0.0))
        best_score = float(best_entry.get("score") or 0.0)
        if scores[-1] >= best_score - margin:
            return None
        best_round = int(best_entry.get("round") or 0)
        if best_round == int(history[-1].get("round") or 0):
            return None
        return {
            "best_round": best_round,
            "best_score": best_score,
            "current": scores[-1],
        }
    except Exception:
        return None


def perform_auto_rollback(
    proposal_id: str,
    prop_state: Dict[str, Any],
    plan: Dict[str, Any],
    root: Optional[Path] = None,
) -> Dict[str, Any]:
    """执行最佳轮次草稿回退（v6.9.0 R3）。

    - 恢复 04_proposal/proposal-draft-r{best_round}.md → proposal-draft.md
      （r{N} 备份即第 N 轮 writer 产出，rN+1 启动时保存）
    - 回退前把当前草稿另存 proposal-draft-pre-rollback.md（证据保全）
    - 记录 rollback_history 与 auto_rollback_count（上限 1 次）
    """
    prop_dir = find_proposal_dir(proposal_id, root)
    if prop_dir is None:
        return {"success": False, "error": "proposal_dir_not_found"}
    draft_dir = prop_dir / "04_proposal"
    src = draft_dir / f"proposal-draft-r{plan['best_round']}.md"
    if not src.exists():
        return {"success": False, "error": "best_round_backup_missing"}
    dst = draft_dir / "proposal-draft.md"
    try:
        if dst.exists():
            (draft_dir / "proposal-draft-pre-rollback.md").write_text(
                dst.read_text(encoding="utf-8"), encoding="utf-8"
            )
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    except Exception as exc:
        return {"success": False, "error": f"write_failed: {exc}"}
    prop_state["auto_rollback_count"] = int(prop_state.get("auto_rollback_count", 0)) + 1
    prop_state["rolled_back_to_round"] = plan["best_round"]
    prop_state.setdefault("rollback_history", []).append(
        {
            "at": now_utc(),
            "restored_round": plan["best_round"],
            "best_score": plan["best_score"],
            "from_score": plan["current"],
            "auto": True,
        }
    )
    return {
        "success": True,
        "restored_round": plan["best_round"],
        "path": str(dst),
    }


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


BUSINESS_TZ = timezone(timedelta(hours=8))
"""业务时区（北京时间，Asia/Shanghai）。

AGENTS.md 与全链路调度口径（工作日时段 00:30-03:30 等）均按北京时间
定义；周末/工作日判定必须锚定此时区，不随宿主机时区漂移。"""


def _is_weekend(now: Optional[datetime] = None) -> bool:
    """判断当前是否为周末（周六或周日，按业务时区北京时间）。

    v6.9.44: 改用北京时间 weekday。此前用 UTC weekday，与业务时区
    （UTC+8）偏差 8 小时：每周一 00:00-08:00 BJ（UTC 仍处周日）被
    误判为周末，lc-repair 走周末分支跳过 failed job 重试（08-24
    周一实测：00:00/06:03 两次修复扫描 weekend=True，前一晚 4 个
    attempts=3 failed job 零重试，最早拖到 12:00 repair 才自愈，
    每周一固定损失 6-12h）；反向 BJ 周六 00:00-08:00（UTC 周五）
    被误判为工作日，周末阶段补跑窗口错失。微调度器 cron
    （*/5 * * * 1-5）与 _weekend_stage_catchup 均按本地时间求值，
    本函数对齐同一口径；显式锚定 BUSINESS_TZ 而非机器本地时区，
    保证宿主机时区变化时业务语义不变。now 参数供回归测试注入固定
    带时区时钟（任意时区 aware 表达均先归一到北京时间再判定）。
    """
    if now is None:
        now = datetime.now(BUSINESS_TZ)
    else:
        now = now.astimezone(BUSINESS_TZ)
    return now.weekday() >= 5


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
