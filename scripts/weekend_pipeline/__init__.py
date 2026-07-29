#!/usr/bin/env python3
"""周末任务流水线包。

将周末 input/output/reflection 任务拆分为可独立执行、可失败重试的小 checkpoint job，
并与 Knowledge Base 联动。
"""

from __future__ import annotations

from .constants import (
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    STAGE_INPUT,
    STAGE_OUTPUT,
    STAGE_REFLECTION,
    STAGES,
)
from .pipeline import WeekendPipeline, get_pipeline

__all__ = [
    "WeekendPipeline",
    "get_pipeline",
    "JOB_STATUS_PENDING",
    "JOB_STATUS_RUNNING",
    "JOB_STATUS_DONE",
    "JOB_STATUS_FAILED",
    "STAGE_INPUT",
    "STAGE_OUTPUT",
    "STAGE_REFLECTION",
    "STAGES",
]
