"""提案生命周期管理 — 四阶段流转 + 对抗优化循环（v6.5.0）

用法示例：
    >>> from proposal_lifecycle import ProposalLifecycle
    >>> lc = ProposalLifecycle()
    >>> lc.list_by_status("optimizing")
    >>> lc.transition("nsfc-2026-hhg", "drafts", "optimizing")
    >>> lc.optimize_cycle("nsfc-2026-hhg")
    >>> lc.submit_feedback("nsfc-2026-hhg", "意见文本")

命令行：
    python3 scripts/proposal_lifecycle.py --dashboard
    python3 scripts/proposal_lifecycle.py --transition nsfc-2026-hhg drafts optimizing
    python3 scripts/proposal_lifecycle.py --optimize nsfc-2026-hhg
"""

from proposal_lifecycle.constants import (
    DEFAULT_MAX_ROUNDS,
    DEFAULT_NO_IMPROVEMENT_LIMIT,
    DEFAULT_SCORE_THRESHOLD,
    DEFAULT_STAGGER_SECONDS,
    LIFECYCLE_STAGES,
    PROJECT_TYPES,
    PROPOSALS_ROOT,
    PROJECT_ROOT,
)
from proposal_lifecycle.state import StateMixin
from proposal_lifecycle.naming import NamingMixin
from proposal_lifecycle.registration import RegistrationMixin
from proposal_lifecycle.metadata import MetadataMixin
from proposal_lifecycle.transitions import TransitionsMixin
from proposal_lifecycle.optimize import OptimizeMixin
from proposal_lifecycle.completion import CompletionMixin
from proposal_lifecycle.feedback_archive import FeedbackArchiveMixin
from proposal_lifecycle.cron import CronMixin


class ProposalLifecycle(
    StateMixin,
    NamingMixin,
    RegistrationMixin,
    MetadataMixin,
    TransitionsMixin,
    OptimizeMixin,
    CompletionMixin,
    FeedbackArchiveMixin,
    CronMixin,
):
    """提案生命周期管理器。"""
    pass


# Import CLI after class definition to avoid circular imports.
from proposal_lifecycle.cli import main

__all__ = [
    "ProposalLifecycle",
    "LIFECYCLE_STAGES",
    "PROJECT_TYPES",
    "DEFAULT_MAX_ROUNDS",
    "DEFAULT_NO_IMPROVEMENT_LIMIT",
    "DEFAULT_SCORE_THRESHOLD",
    "DEFAULT_STAGGER_SECONDS",
    "PROPOSALS_ROOT",
    "PROJECT_ROOT",
    "main",
]
