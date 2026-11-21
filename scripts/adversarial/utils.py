#!/usr/bin/env python3
"""对抗评审奖惩与监察机制 — 纯工具函数（解析 / 指标）。"""

from __future__ import annotations

import json
import math
import re
import statistics
from typing import Any, Dict, List, Optional

from .constants import SCORE_MAX, SCORE_MIN

try:
    from logger import get_logger
    _log = get_logger("adversarial_governance")
except Exception:
    _log = None


def _safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数。"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp_score(score: float) -> float:
    """将分数限制在合法区间。"""
    return max(SCORE_MIN, min(SCORE_MAX, score))


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """从文本中提取第一个 JSON 对象。"""
    # 尝试 ```json ... ``` 代码块
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # 尝试裸 JSON 对象
    for match in re.finditer(r"\{.*\}", text, re.DOTALL):
        try:
            return json.loads(match.group(0))
        except Exception:
            continue
    return None


def _extract_overall_score(text: str) -> float:
    """从文本中提取综合评分。"""
    patterns = [
        r"综合评分[：:]\s*(0\.\d+)",
        r"overall[\s_]*score[：:\s]+(0\.\d+)",
        r"score[：:]\s*(0\.\d+)",
        r"monitor_independent_score[\"\":\s]+(0\.\d+)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return float(m.group(1))
    return 0.0


def _extract_dim_scores(text: str) -> Dict[str, float]:
    """从文本中提取 4 维度分数。"""
    dims: Dict[str, float] = {}
    patterns = [
        ("innovation", r"创新性[（(]innovation[)）]?\s*[:：]?\s*(0\.\d+)"),
        ("feasibility", r"可行性[（(]feasibility[)）]?\s*[:：]?\s*(0\.\d+)"),
        ("rigor", r"严谨性[（(]rigor[)）]?\s*[:：]?\s*(0\.\d+)"),
        ("completeness", r"完整性[（(]completeness[)）]?\s*[:：]?\s*(0\.\d+)"),
    ]
    for key, pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            dims[key] = float(m.group(1))
    return dims


def _count_high_critical_issues(text: str) -> int:
    """统计 critic 报告中 high/critical 问题数量。"""
    count = 0
    for marker in ["[critical]", "[high]", "critical", "high"]:
        count += len(re.findall(re.escape(marker), text, re.IGNORECASE))
    return count


def _dim_std(dim_scores: Dict[str, float]) -> float:
    """计算四维度分数的标准差。"""
    values = [
        v for k, v in dim_scores.items()
        if k in ("innovation", "feasibility", "rigor", "completeness")
    ]
    if len(values) < 2:
        return 0.0
    try:
        return statistics.stdev(values)
    except Exception:
        return 0.0


def _text_similarity(a: str, b: str) -> float:
    """简单字符级相似度（用于检测 surface change）。"""
    if not a or not b:
        return 0.0
    # 去空白后比较最长公共子串比例太复杂，用 token set 近似
    tokens_a = set(re.findall(r"\w+", a))
    tokens_b = set(re.findall(r"\w+", b))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return intersection / union if union else 0.0
