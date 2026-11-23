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
    filter_section_caliber,
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


DIGEST_RETRY_COOLDOWN_H = 2.0
"""健康检查消化 retry 类 failed job 的冷却时长（v7.3.44）。

retry 消化与 lc-repair 的重置语义完全一致（attempts=0 / repair_attempts+1），
仅执行时机从 12h 调度量化提前到"满足条件即执行"。加冷却是因为 repair
原节奏隐含 ~12h 重试间隔，monitor 每小时消化若不加节制，429 限流窗口期
（实测 <2h）会把 3 次 repair_attempts 在数小时内烧完。2h 冷却让瞬时
API 故障窗口先过去再重派，最坏等待从 12h 收敛到 ~2h。"""


def digest_failed_job_action(
    job: Dict[str, Any],
    now: datetime,
    retry_cooldown_h: float = DIGEST_RETRY_COOLDOWN_H,
) -> Optional[str]:
    """判断一个 failed job 是否可被健康检查即时消化（v7.3.44），返回动作名。

    与 run_repair 的 step 3 决策同构（复用 should_auto_unlock，含其
    24h 冷却与每 job 终生一次约束），仅新增 retry 路径的冷却门槛：

    - "retry"      : failed 且 repair_attempts < MAX 且失败距今 ≥ retry_cooldown_h
    - "auto_unlock": 双上限终态且满足 should_auto_unlock（24h 冷却）
    - None         : 无自动消化路径（如 retry 冷却未满 / 解锁额度已用），
                     维持原语义——等 lc-repair 或人工介入

    纯决策函数不落盘；执行方负责写回（复用 controller._save_jobs 的
    proposal-lifecycle 锁）。
    """
    try:
        if job.get("status") != "failed":
            return None
        repair_attempts = int(job.get("repair_attempts", 0))
        if repair_attempts < MAX_JOB_ATTEMPTS:
            finished = str(job.get("finished_at") or "")
            if not finished:
                return "retry"
            fin_dt = datetime.fromisoformat(finished.replace("Z", "+00:00"))
            age_h = (now - fin_dt).total_seconds() / 3600.0
            return "retry" if age_h >= retry_cooldown_h else None
        if should_auto_unlock(job, now):
            return "auto_unlock"
        return None
    except Exception:
        return None


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


# v6.10.5: 全局类负反馈原因 → agent 映射。这些原因源于跨课题共享的
# 全局 agent 分数（memory/agent-scores.json 单一实体），任何一个课题的
# 惨烈对抗把全局分拖破 50 都会连锁触发其他课题的负反馈告警（实测
# 2026-09-09：qgi 对抗把 writer 全局分拖到 45.6，mos2/order-parameter/
# key-transient 等自身健康的课题被连坐挂警、冻结流转）。
# 阈值 50 与 adversarial/scoring.py check_negative_feedback 的全局分
# 线对齐（彼处为字面量）。
NEG_FEEDBACK_GLOBAL_REASONS: Dict[str, str] = {
    "writer 全局分数低于 50": "writer",
    "critic 全局分数低于 50": "critic",
}
NEG_FEEDBACK_GLOBAL_FLOOR = 50


def global_recovery_clear_plan(
    prop_state: Dict[str, Any],
    agent_scores: Dict[str, Any],
    floor: int = NEG_FEEDBACK_GLOBAL_FLOOR,
) -> Optional[Dict[str, Any]]:
    """v6.10.5: 全局条件回升感知——连坐告警的解除计划。

    场景：负反馈原因中含全局类条目（writer/critic 全局分 <50），而对应
    agent 的全局分现已回升至 floor 及以上。此时该原因已事实消失，应从
    告警中移除；若移除后无剩余原因（课题自身无问题），整条告警解除。

    与 24h 冷却自愈（should_auto_clear_negative_feedback）互不影响：
    本路径不占 negative_feedback_auto_clear_count 额度，也不降级
    idea_review_required——被连坐不是课题自身的错，不应触发惩罚性
    退回研究设想评审。

    Returns:
        None：无告警 / 无全局类原因 / 全局分未恢复（维持现状）
        {"action": "clear"}：全局原因全部恢复且无剩余原因 → 解除告警
        {"action": "trim", "remaining": [...]}：全局原因恢复但仍有
            课题自身原因 → 保留告警，仅更新 reasons
    """
    try:
        if not prop_state.get("negative_feedback_alert"):
            return None
        reasons = list(prop_state.get("negative_feedback_reasons") or [])
        if not reasons:
            return None
        global_hits = [r for r in reasons if r in NEG_FEEDBACK_GLOBAL_REASONS]
        if not global_hits:
            return None
        recovered = []
        for r in global_hits:
            role = NEG_FEEDBACK_GLOBAL_REASONS[r]
            try:
                current = float(
                    (agent_scores.get(role) or {}).get("score", -1.0)
                )
            except (TypeError, ValueError):
                # 读不到分数视为"未恢复"：维持告警现状，避免误解除。
                current = -1.0
            if current >= floor:
                recovered.append(r)
        if not recovered:
            return None
        remaining = [r for r in reasons if r not in recovered]
        if remaining:
            return {"action": "trim", "remaining": remaining}
        return {"action": "clear"}
    except Exception:
        return None


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
      0. 仅取章节口径条目（references / method_manual 为 2 维专用口径，
         不参与；v6.9.78 排除 references，v7.3.33 补 method_manual）
      1. score_history >= 3 且最近两轮连续下降（s[-1] < s[-2] <= s[-3]）
      2. 当前分距历史最佳超过 margin（排除天花板附近正常波动）
      3. 最佳条目不是最新条目（v6.9.78 起按条目位置判定而非 round 号——
         微调度器一轮内 5 个 section job 共用同一 round 号，按 round 号
         比较会使回退永不触发）
      4. auto_rollback_count < 1（每课题至多自动回退一次）
    返回 {"best_round", "best_score", "current"} 或 None。
    """
    try:
        history = prop_state.get("score_history") or []
        # v6.9.78: references 轮为 2 维专用口径（rigor/completeness 均值），
        # 与章节 4 维加权分不可比——混入会同时污染"连续下降"与"历史最佳"
        # 判定（口径切换本身即产生伪下降/伪峰值）。回退以章节口径为准。
        # v7.3.33（BUG-43）：补 method_manual（手册轮同为 2 维专用口径
        # readiness/rigor）。旧实现只排 references → 手册分被当章节分参与
        # 连续下降/历史最佳判定（实测 5 课题受影响，houston 3 条手册分
        # 0.66/0.75/0.82 全在视野内）。
        history = filter_section_caliber(history)
        if len(history) < 3:
            return None
        if int(prop_state.get("auto_rollback_count", 0)) >= 1:
            return None
        scores = [float(e.get("score") or 0.0) for e in history]
        if not (scores[-1] < scores[-2] <= scores[-3]):
            return None
        # v6.9.78: 原实现用 round 号判"最佳轮=最新轮"（best_round ==
        # history[-1].round 则不回退）——微调度器一轮内 5 个 section job
        # 共用同一 round 号，且审核退回后 pass 重置使全遍条目 round 恒为 1，
        # 该条件永远成立，回退在微调度器路径永不触发（bsv 实测连续 4 轮
        # 下滑至 0.5 无回退）。改为按条目位置判定：最佳条目即最新条目时
        # 才视为"无可回退"。
        best_idx = max(range(len(history)), key=lambda i: scores[i])
        best_score = scores[best_idx]
        if scores[-1] >= best_score - margin:
            return None
        if best_idx == len(history) - 1:
            return None
        best_round = int(history[best_idx].get("round") or 0)
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
    （*/15 * * * 1-5）与 _weekend_stage_catchup 均按本地时间求值，
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
    """保存指定 proposal 的 pipeline_jobs。

    v7.2.48：持 proposal-lifecycle 锁做「读-改-写」，修并发丢更新。
    旧实现无锁读全量 state → 改一个 proposal → 无锁写回全量 state，
    与并发写者交叉时后者会用自己的旧快照覆盖前者的写入。实测场景
    （10-26 16h 健康检查 BUG-12 复现）：微调度器线程读快照 S0 →
    另一线程写入 P2 的 job 终态 → 前者写回 S0 → **P2 的写入被完全
    丢弃**（job 终态回退 pending → 该 job 被重复执行，重跑整轮 LLM，
    结果被后续轮次覆盖）。锁内重读可保证写入基于最新磁盘状态。

    落盘走 _save_state（其内部不加锁，避免嵌套同名 flock 自死锁）。
    """
    for attempt in range(3):
        try:
            with file_lock("proposal-lifecycle"):
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

                # 写入后校验：并发写者可能在锁释放前抢先写入，导致本次
                # 写入被覆盖——重读确认自己的 updated_at 生效，否则重试。
                verify = self._load_state()
                persisted = (verify.get("proposals") or {}).get(proposal_id, {})
                if persisted.get("updated_at") == state["proposals"][proposal_id]["updated_at"]:
                    return True
                if _log:
                    _log.warning(
                        f"[_save_jobs] {proposal_id} 写入校验失败，"
                        f"第 {attempt + 1} 次重试"
                    )
        except Exception as e:
            if _log:
                _log.error(f"[_save_jobs] {proposal_id} 写入异常: {e}")
    return False

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

    v7.2.50（BUG-16）：改为**锁内读-改-写**。
    旧实现「无锁读全量 state → 裁剪 → 无锁写回全量 state」与并发写者
    （`_save_jobs` 写 job 终态 / `_set_proposal_state` 写状态字段）交叉时，
    本函数用旧快照把对方的写入整份覆盖 → 刚写入的 job 终态回退 pending
    → 被重复执行（整轮 LLM 重跑）。与 BUG-12 同根因，此前只修了
    `_save_jobs` 一侧，archive 侧遗漏。
    落盘走 save_json（原子写），锁内重读保证基于最新磁盘状态。
    """
    lifecycle_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    if not lifecycle_path.exists():
        return 0

    with file_lock("proposal-lifecycle"):
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

        # 归档必须在写回 state 之前完成（append_archive_jobs 用独立锁
        # lifecycle-archive，与 proposal-lifecycle 不冲突；写回 state 后
        # 归档若失败则 job 证据仍在磁盘 active 区，不会丢失）
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
