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
    CRITIC_HIGH_ISSUE_BONUS,
    CRITIC_INFLATION_MONITOR_THRESHOLD,
    CRITIC_INFLATION_PENALTY,
    CRITIC_INFLATION_SCORE_THRESHOLD,
    CRITIC_OVERHARSH_MONITOR_THRESHOLD,
    CRITIC_OVERHARSH_PENALTY,
    CRITIC_OVERHARSH_SCORE_THRESHOLD,
    CRITIC_PROGRESS_WEIGHT,
    CRITIC_REGRESSION_PENALTY,
    LOW_SCORE_ALERT_THRESHOLD,
    MONITOR_DELTA_CAP,
    PROHIBITION_PENALTIES,
    RECOVERY_BONUS,
    RECOVERY_BONUS_MIN_SCORE,
    ROLES,
    WRITER_ISSUE_REDUCTION_WEIGHT,
    WRITER_PROGRESS_WEIGHT,
    WRITER_QUALITY_GATE_LOW,
    WRITER_QUALITY_GATE_LOW_PENALTY,
    WRITER_QUALITY_GATE_MID,
    WRITER_QUALITY_GATE_MID_PENALTY,
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
    critic_proposal_score: float,  # 批评家对申请书的评分（0-1），非 agent 分数（0-150）
    writer_violations: List[str],
    critic_violations: List[str],
    high_issues_before: int,
    high_issues_after: int,
) -> Tuple[float, float]:
    """规则层计算 writer/critic 本轮 delta。

    注意：critic_proposal_score 是批评家对申请书的评分（0-1 区间），
    不是批评家 agent 的全局分数（0-150 区间）。两者在 scoring 模块中并存。
    """
    monitor_delta = monitor_score - prev_monitor_score

    # Writer
    writer_delta = monitor_delta * WRITER_PROGRESS_WEIGHT
    writer_delta += max(0, high_issues_before - high_issues_after) * WRITER_ISSUE_REDUCTION_WEIGHT
    writer_delta += _penalty_for_violations(writer_violations, "writer")
    # v6.8.9 防摆烂：monitor 评分低时，writer 的"微调式改进"未实质推进质量，
    # 抑制正奖励甚至反向扣分，倒逼 writer 通过实质性提升申请书质量来得分。
    writer_delta += _writer_quality_gate(monitor_score)

    # Critic
    critic_delta = 0.0
    if monitor_delta > 0.05:
        critic_delta += monitor_delta * CRITIC_PROGRESS_WEIGHT
        critic_delta += min(high_issues_after, 5) * CRITIC_HIGH_ISSUE_BONUS
    elif monitor_delta < -0.05:
        critic_delta -= CRITIC_REGRESSION_PENALTY
    critic_delta += _penalty_for_violations(critic_violations, "critic")

    # Critic 校准奖励 / 惩罚
    calibration_error = abs(critic_proposal_score - monitor_score)
    if calibration_error < 0.10:
        critic_delta += CALIBRATION_BONUS
    elif calibration_error > 0.20:
        critic_delta -= min(8.0, (calibration_error - 0.20) * CALIBRATION_PENALTY_FACTOR)

    # v6.8.9 防摆烂：critic 评审质量门槛——评分虚高放水或过度苛刻都扣分，
    # 倒逼 critic 通过"严格而准确的评审"（评分贴合 monitor 独立判断）得分。
    critic_delta += _critic_quality_gate(monitor_score, critic_proposal_score)

    return writer_delta, critic_delta


def _writer_quality_gate(monitor_score: float) -> float:
    """v6.8.9 防摆烂：writer 质量门槛。

    monitor 独立评分代表第三方对申请书本身上限的判断。评分低说明申请书
    质量差，writer 只做微调并未实质推进质量，不应获得正奖励；评分过差时
    反向扣分，促使 writer 深入重写而非流于表面。
    """
    if monitor_score < WRITER_QUALITY_GATE_LOW:
        return WRITER_QUALITY_GATE_LOW_PENALTY
    if monitor_score < WRITER_QUALITY_GATE_MID:
        return WRITER_QUALITY_GATE_MID_PENALTY
    return 0.0


def _critic_quality_gate(monitor_score: float, critic_proposal_score: float) -> float:
    """v6.8.9 防摆烂：critic 评审质量门槛。

    - monitor 评分低（申请书质量差）但 critic 给高分 → 评分虚高/放水，重扣。
    - monitor 评分高（质量尚可）但 critic 给过低分 → 过度苛刻/不准确，扣分。
    二者都要求 critic 的评审严格且准确，与 monitor 独立判断贴合时才得高分。
    """
    penalty = 0.0
    if monitor_score < CRITIC_INFLATION_MONITOR_THRESHOLD and \
            critic_proposal_score >= CRITIC_INFLATION_SCORE_THRESHOLD:
        penalty += CRITIC_INFLATION_PENALTY
    elif monitor_score >= CRITIC_OVERHARSH_MONITOR_THRESHOLD and \
            critic_proposal_score < CRITIC_OVERHARSH_SCORE_THRESHOLD:
        penalty += CRITIC_OVERHARSH_PENALTY
    return penalty


def _penalty_for_violations(violations: List[str], role: str) -> float:
    """根据违规类型返回总扣分。

    先精确匹配 PROHIBITION_PENALTIES 中的预定义类型名；
    无匹配时，通过关键词兜底匹配 monitor 输出的自由文本违规描述。
    """
    _KEYWORD_PENALTIES = [
        # 严重等级关键词 → 默认扣分
        (("[severe]", "severe", "[critical]", "critical"), -10),
        (("[high]", " high"), -6),
        # 行为类型关键词
        (("禁止", "fabrication", "杜撰", "伪造"), -12),
        (("wrong_citation", "错误引用", "虚标", "虚假"), -8),
        (("placeholder", "占位符", "未清理", "待核验", "TODO"), -4),
        (("surface_change", "表面修改", "零改进", "未修改", "零响应"), -5),
        (("template_rigidity", "僵化模板", "模板", "套话"), -6),
        (("score_content_mismatch", "评分与内容矛盾", "高分"), -8),
        (("lazy_review", "消极评审", "过短"), -10),
        (("rigid_scoring", "僵化评分"), -8),
        (("unactionable", "不可操作建议"), -6),
        (("missed_major", "遗漏重大"), -10),
        (("未解决", "未修复", "未回应"), -6),
    ]

    total = 0.0
    for v in violations:
        vtype = v if isinstance(v, str) else v.get("type", "")
        penalty = PROHIBITION_PENALTIES.get(role, {}).get(vtype, 0)

        # 精确匹配失败 → 关键词兜底
        if penalty == 0 and vtype:
            v_lower = vtype.lower()
            for keywords, p in _KEYWORD_PENALTIES:
                if any(kw in v_lower for kw in keywords):
                    penalty = p
                    break

        total += penalty
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

    # 加载 agent 分数（用于后续恢复判断和更新）
    scores = load_agent_scores(scores_path)
    old_writer = scores["writer"]["score"]
    old_critic = scores["critic"]["score"]

    # 批评家恢复机制：分数过低时，如近期无严重违规，给予小幅恢复奖励
    if old_critic < RECOVERY_BONUS_MIN_SCORE and critic_delta <= 0:
        recent_violations = scores["critic"]["prohibition_violations"][-5:]
        has_severe_recent = any(
            v.get("type", "") and (
                "severe" in v.get("type", "").lower()
                or "critical" in v.get("type", "").lower()
                or v.get("penalty", 0) <= -8
            )
            for v in recent_violations
        )
        if not has_severe_recent:
            critic_delta += RECOVERY_BONUS
            if _log:
                _log.info(
                    f"批评家恢复: old={old_critic}, 近5轮无严重违规，"
                    f"奖励 {RECOVERY_BONUS} 分（delta={critic_delta:.1f}）"
                )

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


def check_low_score_alert(proposal_state: Dict[str, Any]) -> bool:
    """检查课题分数是否低于低分预警阈值，返回是否触发预警。

    在 proposal_state 中设置 low_score_alert 和 low_score_alert_reason 字段。
    低分预警条件：
    - 当前分数 < LOW_SCORE_ALERT_THRESHOLD（默认 0.65）
    - 同时有 monitor_history 且最近 3 轮分数呈下降趋势
    """
    last_score = proposal_state.get("last_score", 0.0)
    if last_score >= LOW_SCORE_ALERT_THRESHOLD:
        proposal_state["low_score_alert"] = False
        proposal_state.pop("low_score_alert_reason", None)
        return False

    # 分数低于阈值，检查趋势
    monitor_history = proposal_state.get("monitor_history", [])
    recent_scores = [
        entry.get("proposal_score_after", entry.get("monitor_independent_score", 0.0))
        for entry in monitor_history[-3:]
    ]

    if len(recent_scores) >= 3 and all(
        recent_scores[i] > recent_scores[i + 1] for i in range(len(recent_scores) - 1)
    ):
        # 连续 3 轮下降 + 低于阈值 → 高风险预警
        proposal_state["low_score_alert"] = True
        proposal_state["low_score_alert_reason"] = (
            f"分数{last_score:.2f}低于阈值{LOW_SCORE_ALERT_THRESHOLD:.2f}，"
            f"且最近3轮持续下降（{', '.join(f'{s:.2f}' for s in recent_scores)}）"
        )
        return True

    # 低于阈值但分数稳定 → 低风险预警
    rounds = proposal_state.get("optimization_rounds", 1)
    if rounds >= 3:
        proposal_state["low_score_alert"] = True
        proposal_state["low_score_alert_reason"] = (
            f"分数{last_score:.2f}低于阈值{LOW_SCORE_ALERT_THRESHOLD:.2f}，"
            f"已进行{rounds}轮优化，建议人工关注"
        )
        return True

    # 低于阈值但轮次尚浅 → 暂不预警
    proposal_state["low_score_alert"] = False
    return False


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

    # 低分预警：课题分数低于阈值时标记
    check_low_score_alert(proposal_state)

    return proposal_state
