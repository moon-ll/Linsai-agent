#!/usr/bin/env python3
"""对抗评审奖惩与监察机制 — 规则层禁止清单检测。"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .constants import (
    PLACEHOLDER_PATTERNS,
    TEMPLATE_PHRASES,
)
from .utils import (
    _count_high_critical_issues,
    _dim_std,
    _text_similarity,
)

try:
    from logger import get_logger
    _log = get_logger("adversarial_governance")
except Exception:
    _log = None


def detect_writer_prohibitions(
    draft_text: str,
    prev_draft_text: str,
    critic_text: str,
    focus_section: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """检测 writer 违规信号（规则层）。"""
    violations: List[Dict[str, Any]] = []

    # 占位符
    placeholder_hits = []
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, draft_text, re.IGNORECASE):
            placeholder_hits.append(pat)
    if placeholder_hits:
        violations.append({
            "type": "placeholder",
            "label": "使用占位符/未完成段落",
            "penalty": -4,
            "signals": placeholder_hits[:3],
        })

    # 僵化模板：大量堆砌通用套话（简单启发式）
    template_count = sum(1 for phrase in TEMPLATE_PHRASES if phrase in draft_text)
    if template_count >= 5:
        violations.append({
            "type": "template_rigidity",
            "label": "疑似僵化模板/套话堆砌",
            "penalty": -6,
            "signals": [f"命中 {template_count} 个模板短语"],
        })

    # 未大幅改动：与上一版相似度过高（仅当有上一版时）
    if prev_draft_text and len(prev_draft_text) > 100:
        similarity = _text_similarity(prev_draft_text, draft_text)
        if similarity > 0.92:
            violations.append({
                "type": "surface_change",
                "label": "修改过于表面，与上一版相似度过高",
                "penalty": -5,
                "signals": [f"相似度 {similarity:.0%}"],
            })

    return violations


def detect_critic_prohibitions(
    critic_text: str,
    dim_scores: Dict[str, float],
    proposal_score: float,
) -> List[Dict[str, Any]]:
    """检测 critic 违规信号（规则层）。"""
    violations: List[Dict[str, Any]] = []

    # 报告过短 / 无实质问题
    if len(critic_text) < 600 and proposal_score < 0.70:
        violations.append({
            "type": "lazy_review",
            "label": "评审报告过短，疑似消极评审",
            "penalty": -10,
            "signals": [f"报告长度 {len(critic_text)}"],
        })

    # 四维度分数雷同
    std = _dim_std(dim_scores)
    if std < 0.03 and dim_scores:
        violations.append({
            "type": "rigid_scoring",
            "label": "四维度分数过于雷同，疑似僵化评分",
            "penalty": -8,
            "signals": [f"标准差 {std:.3f}"],
        })

    # 评分与内容矛盾：整体评分高但 high 问题很多
    high_count = _count_high_critical_issues(critic_text)
    if proposal_score > 0.75 and high_count >= 3:
        violations.append({
            "type": "score_content_mismatch",
            "label": "评分偏高但报告中有较多 high 问题，疑似评分与内容矛盾",
            "penalty": -8,
            "signals": [f"score={proposal_score:.2f}, high={high_count}"],
        })

    return violations
