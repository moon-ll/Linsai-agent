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
MONITOR_TIMEOUT = 300

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
CRITIC_REGRESSION_PENALTY = 5

# 校准奖励 / 惩罚
CALIBRATION_BONUS = 3
CALIBRATION_PENALTY_FACTOR = 40  # 每 0.1 误差扣 4 分

# 串通惩罚
COLLUSION_PENALTY: Dict[str, int] = {"medium": -5, "high": -10}

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
