from __future__ import annotations

from pathlib import Path

from paths import PROJECT_ROOT

try:
    from logger import get_logger
    _log = get_logger("proposal_lifecycle")
except Exception:
    _log = None


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

PROPOSALS_ROOT = PROJECT_ROOT / "research_proposals"

# 四阶段目录名
LIFECYCLE_STAGES = ["drafts", "optimizing", "pending_review", "archived"]

# 项目类型
PROJECT_TYPES = ["general", "key", "major"]

# 优化循环默认参数
DEFAULT_MAX_ROUNDS = 5
DEFAULT_SCORE_THRESHOLD = 0.80  # 默认达标分数（会被项目类型标准覆盖）
DEFAULT_NO_IMPROVEMENT_LIMIT = 3  # 连续3轮无提升则判定无法提升
DEFAULT_STAGGER_SECONDS = 90  # 错峰间隔（秒），课题间留间隔避免扎堆（P0-1）

