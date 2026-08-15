#!/usr/bin/env python3
"""周末任务流水线常量。"""

from __future__ import annotations

from pathlib import Path

from paths import PROJECT_ROOT

# 任务状态
JOB_STATUS_PENDING = "pending"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_DONE = "done"
JOB_STATUS_FAILED = "failed"

# 阶段
STAGE_INPUT = "input"
STAGE_OUTPUT = "output"
STAGE_REFLECTION = "reflection"
STAGES = [STAGE_INPUT, STAGE_OUTPUT, STAGE_REFLECTION]

# 步骤/任务类型（用于 job['step']）
STEP_COLLECT = "collect"
STEP_SUMMARIZE = "summarize"
STEP_ANALYZE = "analyze"
STEP_SELECT = "select"
STEP_RETRIEVE = "retrieve"
STEP_DEEP_READ = "deep_read"
STEP_COMPOSE = "compose"
STEP_SYNC = "sync"
STEP_EXTRACT = "extract"
STEP_HEALTH = "health"
STEP_REPORT = "report"
STEP_WEEKLY_REPORT = "weekly_report"
STEP_RECOMMEND = "recommend"
# v6.9.6 新增知识库深度维护；v6.9.7 拆分为两个独立 step：
# handler 注册统一 (stage, step) 二元组后，同阶段同 step 无法区分两个 job，
# 故 deep_health 与 merge 各占一个 step（旧 STEP_KB_MAINTAIN 单值已废弃）
STEP_KB_DEEP_HEALTH = "kb_deep_health"  # 深度健康检查（重复检测/孤儿清理/分类候选）
STEP_KB_MERGE = "kb_merge"              # 重复页合并执行器（周限 5 对）

# v6.9.7: processed_sources 滚动裁剪保留窗口（天），与 error_history 裁剪策略对齐
PROCESSED_SOURCES_MAX_AGE_DAYS = 28

# 周末任务状态文件
PIPELINE_STATE_PATH = PROJECT_ROOT / "memory" / "weekend-pipeline.json"

# 输入/输出/反思产物目录
WEEKEND_INPUT_DIR = PROJECT_ROOT / "memory" / "weekend-input"
WEEKEND_OUTPUT_DIR = PROJECT_ROOT / "memory" / "weekend-output"
WEEKEND_REFLECTION_DIR = PROJECT_ROOT / "memory" / "weekend-reflection"

# 来源可靠性标签
RELIABILITY_RELIABLE = "reliable"
RELIABILITY_DERIVED = "derived"
RELIABILITY_UNVERIFIED = "unverified"

# 默认最大重试次数
MAX_JOB_ATTEMPTS = 3

# stale 阈值：running 超过该秒数视为死锁
STALE_RUNNING_SECONDS = 3600

# 默认 cron 表达式
DEFAULT_WORKER_SCHEDULE = "*/20 * * * 6,0"
DEFAULT_WEEKEND_INPUT_SCHEDULE = "0 9 * * 6"
DEFAULT_WEEKEND_OUTPUT_SCHEDULE = "0 14 * * 6"
DEFAULT_WEEKEND_REFLECTION_SCHEDULE = "0 9 * * 0"

# Proposal KB 子目录
NSFC_PROPOSALS_KB_DIR = (
    PROJECT_ROOT / "knowledge" / "wiki" / "projects" / "NSFC-强场超快" / "proposals"
)

# cron 名称
WEEKEND_WORKER_CRON_NAME = "lc-weekend-worker"
