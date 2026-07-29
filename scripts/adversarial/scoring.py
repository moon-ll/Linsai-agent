#!/usr/bin/env python3
"""对抗评审奖惩与监察机制 — 分数更新 / 惩罚 / 负反馈逻辑。"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, List, Tuple

from common import load_json, now_utc, save_json

from .constants import (
    CALIBRATION_BONUS,
    CALIBRATION_PENALTY_FACTOR,
    COLLUSION_PENALTY,
    CRITIC_HIGH_ISSUE_BONUS,
    CRITIC_PROGRESS_WEIGHT,
    CRITIC_REGRESSION_PENALTY,
    DEFAULT_INITIAL_SCORE,
    DEFAULT_SCORES,
    MONITOR_DELTA_CAP,
    PROHIBITION_PENALTIES,
    ROLES,
    WRITER_ISSUE_REDUCTION_WEIGHT,
    WRITER_PROGRESS_WEIGHT,
)
from .utils import _clamp_score, _count_high_critical_issues, _safe_float

try:
    from logger import get_logger
    _log = get_logger("adversarial_governance")
except Exception:
    _log = None


def load_agent_scores(scores_path: Path) -> Dict[str, Any]:
    """加载 agent 分数，文件不存在时返回默认结构。"""
    default = copy.deepcopy(DEFAULT_SCORES)
    for role in ROLES:
        default[role]["updated_at"] = now_utc()
    return load_json(scores_path, default=default)


def save_agent_scores(scores_path: Path, scores: Dict[str, Any]) -> None:
    """持久化 agent 分数。"""
    scores["updated_at"] = now_utc()
    save_json(scores_path, scores)


def update_writer_score(old_score: float, delta: float) -> float:
    """更新 writer 分数并限制在合法区间。"""
    return _clamp_score(old_score + delta)


def update_critic_score(old_score: float, delta: float) -> float:
    """更新 critic 分数并限制在合法区间。"""
    return _clamp_score(old_score + delta)


def compute_rule_deltas(
    monitor_score: float,
    prev_monitor_score: float,
    critic_score: float,
    writer_violations: List[str],
    critic_violations: List[str],
    high_issues_before: int,
    high_issues_after: int,
) -> Tuple[float, float]:
    """规则层计算 writer/critic 本轮 delta。"""
    monitor_delta = monitor_score - prev_monitor_score

    # Writer
    writer_delta = monitor_delta * WRITER_PROGRESS_WEIGHT
    writer_delta += max(0, high_issues_before - high_issues_after) * WRITER_ISSUE_REDUCTION_WEIGHT
    writer_delta += _penalty_for_violations(writer_violations, "writer")

    # Critic
    critic_delta = 0.0
    if monitor_delta > 0.05:
        critic_delta += monitor_delta * CRITIC_PROGRESS_WEIGHT
        critic_delta += min(high_issues_after, 5) * CRITIC_HIGH_ISSUE_BONUS
    elif monitor_delta < -0.05:
        critic_delta -= CRITIC_REGRESSION_PENALTY
    critic_delta += _penalty_for_violations(critic_violations, "critic")

    # Critic 校准奖励 / 惩罚
    calibration_error = abs(critic_score - monitor_score)
    if calibration_error < 0.10:
        critic_delta += CALIBRATION_BONUS
    elif calibration_error > 0.20:
        critic_delta -= min(8.0, (calibration_error - 0.20) * CALIBRATION_PENALTY_FACTOR)

    return writer_delta, critic_delta


def _penalty_for_violations(violations: List[str], role: str) -> float:
    """根据违规类型返回总扣分。"""
    total = 0.0
    for v in violations:
        key = v if isinstance(v, str) else v.get("type", "")
        total += PROHIBITION_PENALTIES.get(role, {}).get(key, 0)
    return total


def apply_collusion_penalty(
    writer_delta: float,
    critic_delta: float,
    collusion_risk: str,
) -> Tuple[float, float]:
    """根据串通风险追加惩罚。"""
    penalty = COLLUSION_PENALTY.get(collusion_risk, 0)
    if collusion_risk in ("medium", "high"):
        # 若当前奖励为正，先清零再额外扣分
        writer_delta = min(writer_delta, 0) + penalty
        critic_delta = min(critic_delta, 0) + penalty
    return writer_delta, critic_delta


def _record_violations(
    scores: Dict[str, Any],
    role: str,
    violations: List[str],
    proposal_id: str,
    round_num: int,
    section_key: str,
) -> None:
    """将违规记录追加到对应 role 的分数结构中。"""
    for v in violations:
        vtype = v if isinstance(v, str) else v.get("type", "")
        penalty = _penalty_for_violations([vtype], role)
        scores[role]["prohibition_violations"].append({
            "type": vtype,
            "round_ref": f"{proposal_id}-r{round_num}-{section_key}",
            "penalty": penalty,
            "at": now_utc(),
        })
    scores[role]["prohibition_violations"] = scores[role]["prohibition_violations"][-20:]


def apply_monitor_result(
    scores_path: Path,
    proposal_id: str,
    round_num: int,
    section_key: str,
    score_before: float,
    score_after: float,
    dim_scores: Dict[str, float],
    monitor_result: Dict[str, Any],
    proposal_state: Dict[str, Any],
) -> Dict[str, Any]:
    """根据 monitor 结果更新 agent 分数，返回 deltas。"""
    monitor_score = monitor_result.get("monitor_independent_score", score_after)

    # 上一轮的 monitor 分数作为 baseline
    prev_monitor_score = score_before
    monitor_history = proposal_state.get("monitor_history", [])
    for entry in reversed(monitor_history):
        if entry.get("monitor_independent_score") is not None:
            prev_monitor_score = entry["monitor_independent_score"]
            break

    # high issues 数量
    high_issues_before = 0
    if monitor_history:
        high_issues_before = monitor_history[-1].get("high_issues_after", 0)
    high_issues_after = _count_high_critical_issues(
        monitor_result.get("raw_output", "")
    )

    writer_violations = monitor_result.get("writer_prohibitions", [])
    critic_violations = monitor_result.get("critic_prohibitions", [])

    writer_rule_delta, critic_rule_delta = compute_rule_deltas(
        monitor_score, prev_monitor_score, score_after,
        writer_violations, critic_violations,
        high_issues_before, high_issues_after,
    )

    # 与 monitor 建议混合（±15 限制）
    writer_suggested = float(monitor_result.get("writer_suggested_delta", 0.0))
    critic_suggested = float(monitor_result.get("critic_suggested_delta", 0.0))
    writer_monitor_delta = max(-MONITOR_DELTA_CAP, min(MONITOR_DELTA_CAP, writer_suggested))
    critic_monitor_delta = max(-MONITOR_DELTA_CAP, min(MONITOR_DELTA_CAP, critic_suggested))

    # 若 monitor 提供了非零建议，与规则层取平均；否则纯规则层
    if abs(writer_monitor_delta) > 0.001:
        writer_delta = (writer_rule_delta + writer_monitor_delta) / 2.0
    else:
        writer_delta = writer_rule_delta

    if abs(critic_monitor_delta) > 0.001:
        critic_delta = (critic_rule_delta + critic_monitor_delta) / 2.0
    else:
        critic_delta = critic_rule_delta

    # 串通惩罚
    collusion_risk = monitor_result.get("collusion_risk", "none")
    writer_delta, critic_delta = apply_collusion_penalty(
        writer_delta, critic_delta, collusion_risk
    )

    # 加载并更新 agent 分数
    scores = load_agent_scores(scores_path)
    old_writer = scores["writer"]["score"]
    old_critic = scores["critic"]["score"]
    new_writer = update_writer_score(old_writer, writer_delta)
    new_critic = update_critic_score(old_critic, critic_delta)

    scores["writer"]["score"] = new_writer
    scores["writer"]["history"].append({
        "round_ref": f"{proposal_id}-r{round_num}-{section_key}",
        "delta": round(writer_delta, 2),
        "reason": monitor_result.get("writer_assessment", "")[:100],
        "at": now_utc(),
    })
    scores["writer"]["history"] = scores["writer"]["history"][-50:]

    scores["critic"]["score"] = new_critic
    scores["critic"]["history"].append({
        "round_ref": f"{proposal_id}-r{round_num}-{section_key}",
        "delta": round(critic_delta, 2),
        "reason": monitor_result.get("critic_assessment", "")[:100],
        "at": now_utc(),
    })
    scores["critic"]["history"] = scores["critic"]["history"][-50:]

    # 记录违规
    _record_violations(scores, "writer", writer_violations, proposal_id, round_num, section_key)
    _record_violations(scores, "critic", critic_violations, proposal_id, round_num, section_key)

    save_agent_scores(scores_path, scores)

    return {
        "writer_delta": round(writer_delta, 2),
        "critic_delta": round(critic_delta, 2),
        "old_writer_score": round(old_writer, 2),
        "old_critic_score": round(old_critic, 2),
        "new_writer_score": round(new_writer, 2),
        "new_critic_score": round(new_critic, 2),
        "monitor_independent_score": monitor_score,
        "prev_monitor_score": prev_monitor_score,
        "collusion_risk": collusion_risk,
        "negative_feedback": monitor_result.get("negative_feedback", False),
        "high_issues_after": high_issues_after,
    }


def check_negative_feedback(
    proposal_state: Dict[str, Any],
    agent_scores: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """判断是否需要触发负反馈告警。"""
    reasons: List[str] = []
    monitor_history = proposal_state.get("monitor_history", [])
    if not monitor_history:
        return False, reasons

    # 1. monitor 独立分数连续 3 轮下降
    recent_scores = [entry.get("monitor_independent_score", 0.0) for entry in monitor_history[-3:]]
    if len(recent_scores) >= 3 and all(
        recent_scores[i] > recent_scores[i + 1] for i in range(len(recent_scores) - 1)
    ):
        reasons.append(f"monitor 独立分数连续 {len(recent_scores)} 轮下降")

    # 2. 本地 writer/critic 分数连续 3 轮双降
    recent_local_writer = [entry.get("local_writer_score", 100.0) for entry in monitor_history[-3:]]
    recent_local_critic = [entry.get("local_critic_score", 100.0) for entry in monitor_history[-3:]]
    if (len(recent_local_writer) >= 3 and
        all(recent_local_writer[i] > recent_local_writer[i + 1] for i in range(2)) and
        all(recent_local_critic[i] > recent_local_critic[i + 1] for i in range(2))):
        reasons.append("writer/critic 本地分数连续 3 轮双降")

    # 3. 串通风险连续 2 轮 >= medium
    recent_collusion = [entry.get("collusion_risk", "none") for entry in monitor_history[-2:]]
    if len(recent_collusion) >= 2 and all(r in ("medium", "high") for r in recent_collusion):
        reasons.append("串通风险连续 2 轮达到 medium/high")

    # 4. 全局 agent 分数 < 50
    if agent_scores.get("writer", {}).get("score", 100) < 50:
        reasons.append("writer 全局分数低于 50")
    if agent_scores.get("critic", {}).get("score", 100) < 50:
        reasons.append("critic 全局分数低于 50")

    return bool(reasons), reasons


def record_monitor_history(
    proposal_state: Dict[str, Any],
    round_num: int,
    section_key: str,
    score_before: float,
    score_after: float,
    monitor_result: Dict[str, Any],
    deltas: Dict[str, Any],
    agent_scores: Dict[str, Any],
) -> Dict[str, Any]:
    """把 monitor 记录写入 proposal_state，返回更新后的 state。"""
    monitor_history = proposal_state.setdefault("monitor_history", [])

    # 计算本地 agent 累计分数
    local_writer_score = DEFAULT_INITIAL_SCORE
    local_critic_score = DEFAULT_INITIAL_SCORE
    if monitor_history:
        local_writer_score = monitor_history[-1].get("local_writer_score", DEFAULT_INITIAL_SCORE)
        local_critic_score = monitor_history[-1].get("local_critic_score", DEFAULT_INITIAL_SCORE)

    local_writer_score = _clamp_score(local_writer_score + deltas["writer_delta"])
    local_critic_score = _clamp_score(local_critic_score + deltas["critic_delta"])

    entry = {
        "round": round_num,
        "section_key": section_key,
        "proposal_score_before": score_before,
        "proposal_score_after": score_after,
        "monitor_independent_score": deltas.get("monitor_independent_score", monitor_result.get("monitor_independent_score", score_after)),
        "writer_delta": deltas["writer_delta"],
        "critic_delta": deltas["critic_delta"],
        "local_writer_score": local_writer_score,
        "local_critic_score": local_critic_score,
        "writer_prohibitions": monitor_result.get("writer_prohibitions", []),
        "critic_prohibitions": monitor_result.get("critic_prohibitions", []),
        "collusion_risk": monitor_result.get("collusion_risk", "none"),
        "negative_feedback": monitor_result.get("negative_feedback", False),
        "overall_assessment": monitor_result.get("overall_assessment", "")[:500],
        "high_issues_after": deltas.get("high_issues_after", 0),
        "at": now_utc(),
    }
    monitor_history.append(entry)
    proposal_state["monitor_history"] = monitor_history[-50:]

    # 负反馈综合判定
    alert, reasons = check_negative_feedback(proposal_state, agent_scores=agent_scores)
    proposal_state["negative_feedback_alert"] = alert
    if alert:
        proposal_state["negative_feedback_reasons"] = reasons

    return proposal_state
