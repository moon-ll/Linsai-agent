#!/usr/bin/env python3
"""输入链轮次接力（v6.9.98）。

周末输入链自 v6.9.98 起多轮化：每轮 collect → deep_digest →
cluster_assign → cluster_distill → methods_settle（v6.10.0 T3 插入）
→ topic_match → compose 七步全部走完后，若仍有未消化源且冷却期满，
weekend worker（*/20 tick，run_next 路径）把 input 阶段整体重置为
pending 开新轮（round+1），直至源尽（剩余 0）或周日 23:59（北京
时间）窗口闭合。

设计要点：
    - 判定函数全部为纯函数（读 state dict，不碰文件系统），支持
      now 时钟注入（参考 lifecycle.utils._is_weekend 的注入式设计），
      回归测试可固定时间验证边界（冷却、周日窗口、工作日）。
    - 剩余源数量取自本轮 deep_digest job result 的 remaining_sources
      （同一次 collect 快照内的口径，避免接力判定再扫一遍来源目录）。
    - 跨周重置（pipeline._reset_stage_for_new_week）把 round 归 1，
      本模块不负责跨周判定。

用法：
    from weekend_pipeline.rounds import (
        should_open_next_round, reset_input_for_new_round,
    )
    ok, reason = should_open_next_round(state, now=fixed_dt)
    if ok:
        new_round = reset_input_for_new_round(state)  # 调用方需持 weekend-pipeline 锁

自检：
    python3 -m weekend_pipeline.rounds --self-check
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from .constants import (
    INPUT_DEEP_DIGEST_JOB_ID,
    INPUT_ROUND_COOLDOWN_SECONDS,
    JOB_STATUS_DONE,
    JOB_STATUS_PENDING,
    STAGE_INPUT,
)

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None

# 业务时区（北京时间，Asia/Shanghai）——周末窗口开合判定锚点，
# 与 lifecycle.utils._is_weekend 同口径，不随宿主机时区漂移
BUSINESS_TZ = timezone(timedelta(hours=8))


def _dt_from_iso(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def current_round(state: Dict[str, Any]) -> int:
    """当前输入链轮次（state.input_round.round，缺省 1）。"""
    ir = state.get("input_round") or {}
    try:
        return max(1, int(ir.get("round", 1)))
    except Exception:
        return 1


def _input_jobs(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [j for j in state.get("jobs", []) if j.get("stage") == STAGE_INPUT]


def input_round_finished_at(state: Dict[str, Any]) -> str:
    """本轮 input 阶段最后完成时间（job finished_at 最大值，ISO）。"""
    finished = [j.get("finished_at", "") for j in _input_jobs(state) if j.get("finished_at")]
    return max(finished) if finished else ""


def is_input_round_complete(state: Dict[str, Any]) -> bool:
    """本轮 input 阶段是否全部 step（v6.10.0 起七步）done。"""
    jobs = _input_jobs(state)
    return bool(jobs) and all(j.get("status") == JOB_STATUS_DONE for j in jobs)


def remaining_sources(state: Dict[str, Any]) -> Optional[int]:
    """本轮 deep_digest 后剩余未消化源数量（无记录返回 None，保守不开轮）。"""
    for j in _input_jobs(state):
        if j.get("job_id") == INPUT_DEEP_DIGEST_JOB_ID:
            result = j.get("result") or {}
            val = result.get("remaining_sources")
            if isinstance(val, int):
                return val
            return None
    return None


def input_window_closed(now: Optional[datetime] = None) -> bool:
    """周末输入窗口是否已闭合（不再开新轮）。

    口径（北京时间）：周六全天开；周日 23:59 前开、之后闭；工作日
    （周一至周五）恒闭——轮次接力是周末链路语义，工作日触发（如
    lc-repair 补跑后的 worker tick）不得开新轮。
    """
    if now is None:
        now = datetime.now(BUSINESS_TZ)
    else:
        now = now.astimezone(BUSINESS_TZ)
    weekday = now.weekday()
    if weekday == 5:  # 周六
        return False
    if weekday == 6:  # 周日：23:59 后闭合
        return now.hour > 23 or (now.hour == 23 and now.minute >= 59)
    return True


def should_open_next_round(
    state: Dict[str, Any],
    now: Optional[datetime] = None,
    cooldown_seconds: int = INPUT_ROUND_COOLDOWN_SECONDS,
) -> Tuple[bool, str]:
    """判定是否应把 input 阶段重置开新轮。

    条件（全部满足）：
      1. 本轮 input 阶段全部 job done（六步走完）；
      2. 本轮 deep_digest 记录 remaining_sources ≥ 1（仍有未消化源）；
      3. 距本轮 input 阶段最后完成时间已过冷却期（默认 90 分钟）；
      4. 周末窗口未闭合（北京时间，周日 23:59 后 / 工作日不开）。

    Returns:
        (是否开轮, 原因说明)。原因供日志与测试断言。
    """
    if not is_input_round_complete(state):
        return False, "本轮七步未全部完成"
    rem = remaining_sources(state)
    if rem is None:
        return False, "无 remaining_sources 记录（保守不开轮）"
    if rem < 1:
        return False, "未消化源已清零（源尽，stage 终态 done）"
    last_fin = input_round_finished_at(state)
    last_dt = _dt_from_iso(last_fin)
    if last_dt is None:
        return False, "本轮无完成时间戳（保守不开轮）"
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    elapsed = (now - last_dt).total_seconds()
    if elapsed < cooldown_seconds:
        return False, (
            f"冷却期未满（{int(elapsed // 60)} 分钟 < "
            f"{cooldown_seconds // 60} 分钟）"
        )
    if input_window_closed(now):
        return False, "周末输入窗口已闭合（周日 23:59 后或非周末）"
    return True, f"剩余 {rem} 源，冷却 {int(elapsed // 60)} 分钟已满"


def reset_input_for_new_round(state: Dict[str, Any]) -> int:
    """把 input 阶段整体重置为 pending 开新轮（调用方需持 weekend-pipeline 锁）。

    动作：
      - round+1，记录 prev_round_finished_at（本轮最后完成时间）；
      - input 阶段全部 job → pending，清 started_at/finished_at/
        last_error/result，attempts 保留（失败史不因开新轮抹除）；
      - 各 job 打 round 标（deep_digest 产物校验 {round} 的格式化来源）；
      - 清 last_summaries_path / last_routes_path（防下游误读上一轮产物，
        新轮由 deep_digest / topic_match 重新记录）；
      - stage_status.input → pending。

    Returns:
        新轮次号。
    """
    ir = state.setdefault("input_round", {})
    new_round = current_round(state) + 1
    ir["round"] = new_round
    ir["prev_round_finished_at"] = input_round_finished_at(state)
    ir["last_summaries_path"] = ""
    ir["last_routes_path"] = ""

    for job in _input_jobs(state):
        job["status"] = JOB_STATUS_PENDING
        job["started_at"] = ""
        job["finished_at"] = ""
        job["last_error"] = ""
        # attempts / repair_attempts 保留（v6.9.98 需求：开新轮不清失败史）
        if "result" in job:
            del job["result"]
        job["round"] = new_round

    state.setdefault("stage_status", {})[STAGE_INPUT] = JOB_STATUS_PENDING
    if _log:
        _log.info(
            f"[weekend-pipeline] 输入链轮次接力：开启第 {new_round} 轮"
            f"（上轮完成于 {ir['prev_round_finished_at'] or '未知'}）"
        )
    return new_round


def _self_check() -> None:
    """自检：接力判定边界 + 重置动作。"""
    print("=== weekend_pipeline.rounds 自检 ===")

    # 周六 12:00（北京时间）
    sat = datetime(2026, 9, 5, 4, 0, 0, tzinfo=timezone.utc)  # 北京时间 12:00
    assert input_window_closed(sat) is False, "周六窗口应开"
    # 周日 23:00（北京时间）
    sun_early = datetime(2026, 9, 6, 15, 0, 0, tzinfo=timezone.utc)  # 北京 23:00
    assert input_window_closed(sun_early) is False, "周日 23:00 窗口仍开"
    # 周日 23:59:30（北京时间）
    sun_late = datetime(2026, 9, 6, 15, 59, 30, tzinfo=timezone.utc)
    assert input_window_closed(sun_late) is True, "周日 23:59 后窗口闭合"
    # 周一
    mon = datetime(2026, 9, 7, 4, 0, 0, tzinfo=timezone.utc)
    assert input_window_closed(mon) is True, "工作日窗口恒闭"
    print("✓ 周末窗口开合边界（周六开/周日 23:59 闭/工作日闭）")

    def _job(jid: str, status: str = "done", finished: str = "2026-09-05T04:00:00Z") -> Dict[str, Any]:
        return {"job_id": jid, "stage": "input", "status": status, "finished_at": finished}

    done_state = {
        "jobs": [
            _job("input_collect_sources"),
            _job(INPUT_DEEP_DIGEST_JOB_ID),
            _job("input_cluster_assign"),
            _job("input_cluster_distill"),
            _job("input_methods_settle"),  # v6.10.0（T3）第七步
            _job("input_topic_match"),
            _job("input_compose_ideas", finished="2026-09-05T05:30:00Z"),
        ],
        "stage_status": {"input": "done"},
    }
    # deep_digest 的 result 注入 remaining_sources
    for j in done_state["jobs"]:
        if j["job_id"] == INPUT_DEEP_DIGEST_JOB_ID:
            j["result"] = {"remaining_sources": 7}

    ok, reason = should_open_next_round(done_state, now=datetime(2026, 9, 5, 7, 30, 0, tzinfo=timezone.utc))
    assert ok, f"冷却满 + 剩余 7 源 + 周六 → 应开轮（{reason}）"

    ok, _ = should_open_next_round(done_state, now=datetime(2026, 9, 5, 6, 0, 0, tzinfo=timezone.utc))
    assert not ok, "冷却 30 分钟未满 → 不开轮"

    empty_state = {"jobs": [dict(j, result={"remaining_sources": 0}) if j["job_id"] == INPUT_DEEP_DIGEST_JOB_ID else dict(j) for j in done_state["jobs"]]}
    ok, _ = should_open_next_round(empty_state, now=datetime(2026, 9, 5, 8, 0, 0, tzinfo=timezone.utc))
    assert not ok, "源尽（剩余 0）→ 不开轮"
    print("✓ 接力判定（冷却/源尽/剩余门槛）")

    new_round = reset_input_for_new_round(done_state)
    assert new_round == 2, "重置后轮次应为 2"
    assert all(j["status"] == "pending" for j in done_state["jobs"]), "job 应全部重置 pending"
    assert done_state["input_round"]["prev_round_finished_at"] == "2026-09-05T05:30:00Z", "应记录上轮完成时间"
    assert done_state["input_round"].get("last_routes_path", "") == "", "last_routes_path 应清空（防跨轮误读）"
    assert done_state["stage_status"]["input"] == "pending", "stage_status 应回 pending"
    print("✓ 重置动作（round+1 / job pending / prev_round_finished_at / last_routes_path 清空）")
    print("✓ rounds 自检通过")


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        _self_check()
