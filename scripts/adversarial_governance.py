#!/usr/bin/env python3
"""对抗评审奖惩与监察机制（v6.7.6）。

为 writer-critic 对抗链路引入：
- agent（writer/critic）奖惩分数
- 全局监察员 monitor（独立评分 + meta-review）
- 上下文敏感的禁止清单
- 反串通（anti-collusion）机制
- 负反馈预警

本模块为向后兼容的薄封装，实际实现已迁移至 adversarial/ 子包。

用法：
    from adversarial_governance import AdversarialGovernance
    ag = AdversarialGovernance()
    monitor_result = ag.run_monitor_step(...)
    deltas = ag.apply_monitor_result(proposal_id, round_num, section_key,
                                     score_before, score_after, dim_scores,
                                     monitor_result, proposal_state)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from paths import PROJECT_ROOT

# 路径常量保留在本模块，使 test_runner.patch_module_root 等 monkey-patch 机制可生效。
AGENT_SCORES_PATH = PROJECT_ROOT / "memory" / "agent-scores.json"
STANDARDS_PATH = PROJECT_ROOT / "memory" / "nsfc-standards.json"

# 向后兼容：重新导出子包中的常量与工具函数。
from adversarial.constants import (  # noqa: E402
    CALIBRATION_BONUS,
    CALIBRATION_PENALTY_FACTOR,
    COLLUSION_PENALTY,
    CRITIC_HIGH_ISSUE_BONUS,
    CRITIC_PROGRESS_WEIGHT,
    CRITIC_REGRESSION_PENALTY,
    DEFAULT_INITIAL_SCORE,
    DEFAULT_SCORES,
    MONITOR_DELTA_CAP,
    MONITOR_TIMEOUT,
    PLACEHOLDER_PATTERNS,
    PROHIBITION_PENALTIES,
    ROLES,
    SCORE_MAX,
    SCORE_MIN,
    SEVERITY_MARKERS,
    TEMPLATE_PHRASES,
    WRITER_ISSUE_REDUCTION_WEIGHT,
    WRITER_PROGRESS_WEIGHT,
)
from adversarial.utils import (  # noqa: E402
    _clamp_score,
    _count_high_critical_issues,
    _dim_std,
    _extract_dim_scores,
    _extract_json_object,
    _extract_overall_score,
    _safe_float,
    _text_similarity,
)

try:
    from logger import get_logger
    _log = get_logger("adversarial_governance")
except Exception:
    _log = None


def __getattr__(name: str) -> Any:
    """惰性加载 AdversarialGovernance 类与自检函数，避免循环导入。"""
    if name == "AdversarialGovernance":
        from adversarial.governance import AdversarialGovernance as _AdversarialGovernance
        globals()[name] = _AdversarialGovernance
        return _AdversarialGovernance
    if name == "_self_check":
        from adversarial.governance import _self_check as _self_check_fn
        globals()[name] = _self_check_fn
        return _self_check_fn
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
