#!/usr/bin/env python3
"""对抗评审奖惩与监察机制 — 常量定义。"""

from __future__ import annotations

from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# 分数相关常量
# ---------------------------------------------------------------------------

DEFAULT_INITIAL_SCORE = 100
SCORE_MIN = 0
SCORE_MAX = 150
MONITOR_DELTA_CAP = 15
# v6.9.62: 600→900。600s 在 MiniMax 慢速期连续触顶（08-27 new-idea monitor
# 四连空输出超时）；v6.9.61 已把 monitor 输入从 120KB+（双份组装全文）压到
# 评审视图+程序 diff+digest，900s 余量充足。
MONITOR_TIMEOUT = 900

ROLES = ["writer", "critic"]

# 默认 agent 分数结构（模板，使用时需深拷贝并填充 updated_at）
DEFAULT_SCORES: Dict[str, Any] = {
    role: {
        "score": DEFAULT_INITIAL_SCORE,
        "initial_score": DEFAULT_INITIAL_SCORE,
        "history": [],
        "prohibition_violations": [],
        "updated_at": "",
    }
    for role in ROLES
}

# ---------------------------------------------------------------------------
# 规则层系数
# ---------------------------------------------------------------------------

WRITER_PROGRESS_WEIGHT = 20
WRITER_ISSUE_REDUCTION_WEIGHT = 3
CRITIC_PROGRESS_WEIGHT = 15
CRITIC_HIGH_ISSUE_BONUS = 2
CRITIC_REGRESSION_PENALTY = 3   # v6.8.18: 5→3

# 校准奖励 / 惩罚（v6.8.18: 降低惩罚幅度）
CALIBRATION_BONUS = 4           # v6.8.18: 3→4
CALIBRATION_PENALTY_FACTOR = 20  # v6.8.18: 40→20（每 0.1 误差扣 2 分）
CALIBRATION_PENALTY_MAX = 4.0    # v6.8.18: 新增上限

# 串通惩罚（v6.8.18: 降低）
COLLUSION_PENALTY: Dict[str, int] = {"medium": -3, "high": -6}  # v6.8.18: -5/-10 → -3/-6

# 批评家恢复机制（v6.8.18: 提高恢复力度）
RECOVERY_BONUS_MIN_SCORE = 40     # v6.8.18: 20→40
RECOVERY_BONUS = 5.0              # v6.8.18: 3→5

# ---------------------------------------------------------------------------
# v6.8.9 质量门槛（防摆烂）
# ---------------------------------------------------------------------------
# writer 质量门槛：monitor 独立评分低于中线下限时，writer 的"微调式改进"
# 未实质推进质量，不应获得正奖励，甚至反向抑制。
WRITER_QUALITY_GATE_LOW = 0.50            # 质量过差阈值（<此值反向抑制）
WRITER_QUALITY_GATE_LOW_PENALTY = -5.0    # 质量过差时的额外扣分
WRITER_QUALITY_GATE_MID = 0.70            # 质量欠佳阈值（<此值抑制正奖励）
WRITER_QUALITY_GATE_MID_PENALTY = -2.0    # 质量欠佳时的额外扣分

# critic 评审质量门槛：monitor 评分低但 critic 给申请书打高分 → 评分虚高/放水；
# monitor 评分高但 critic 打低分 → 过度苛刻/不准确。两者都扣分，倒逼 critic
# 通过"严格而准确的评审"（发现真问题、评分贴合 monitor）来获得分数。
CRITIC_INFLATION_MONITOR_THRESHOLD = 0.60  # monitor 评分低于此值视为"质量差"
CRITIC_INFLATION_SCORE_THRESHOLD = 0.75    # critic 给分≥此值视为"虚高"
CRITIC_INFLATION_PENALTY = -8.0            # 虚高放水扣分
CRITIC_OVERHARSH_MONITOR_THRESHOLD = 0.75  # monitor 评分≥此值视为"质量尚可"
CRITIC_OVERHARSH_SCORE_THRESHOLD = 0.55    # critic 给分<此值视为"过度苛刻"
CRITIC_OVERHARSH_PENALTY = -4.0            # 过度苛刻扣分

# 低分预警阈值
LOW_SCORE_ALERT_THRESHOLD = 0.65  # 课题分数低于此值触发低分预警

# 占位符信号（writer）
PLACEHOLDER_PATTERNS: List[str] = [
    r"待补充",
    r"TODO",
    r"\[引用\]",
    r"\[待填\]",
    r"\(待\)",
    r"请补充",
    r"此处补充",
    r"详见后文",
]

# 僵化模板信号（writer）—— 仅作为可疑信号，不直接扣分
TEMPLATE_PHRASES: List[str] = [
    "具有重要的科学意义",
    "具有重要的理论意义",
    "具有重要的应用价值",
    "本项目拟开展",
    "本项目拟研究",
    "旨在解决",
    "综上所述",
]

# 问题严重级别标识（critic 报告）
SEVERITY_MARKERS: List[str] = ["[critical]", "[high]", "[medium]", "[low]", "critical", "high"]

# ---------------------------------------------------------------------------
# 禁止清单 → 扣分映射
# ---------------------------------------------------------------------------

PROHIBITION_PENALTIES: Dict[str, Dict[str, int]] = {
    "writer": {
        "fabrication": -12,
        "wrong_citation": -8,
        "template_rigidity": -6,
        "unaddressed_issues": -8,
        "off_section_changes": -5,
        "placeholder": -4,
        "surface_change": -5,
    },
    "critic": {
        "lazy_review": -10,
        "rigid_scoring": -8,
        "missed_major_issues": -10,
        "unactionable_suggestions": -6,
        "score_content_mismatch": -8,
    },
}
