#!/usr/bin/env python3
"""生命周期 cron 框架常量。"""

from __future__ import annotations

from pathlib import Path

from paths import PROJECT_ROOT

# hermes CLI 在执行 --script 时会在 ~/.hermes/profiles/<profile>/scripts/ 下查找，
# 因此包装脚本必须写到对应 profile 目录，而不是全局 ~/.hermes/scripts/
HERMES_SCRIPTS_DIR = Path.home() / ".hermes" / "profiles" / "linsai" / "scripts"
HERMES_PROFILE = "linsai"  # cron 统一挂在 linsai profile，便于 hermes_bridge 读取

# worker / repair / orchestrate / weekend 的默认 cron 表达式
DEFAULT_ORCHESTRATE_SCHEDULE = "55 8 * * *"
DEFAULT_WORKER_INTERVAL = "47 * * * 1-5"  # v6.7.7: 周中运行，周末暂停
DEFAULT_REPAIR_SCHEDULE = "0 */6 * * *"

# 周末任务 cron 表达式（周六输入/输出，周日反思）
DEFAULT_WEEKEND_INPUT_SCHEDULE = "0 9 * * 6"
DEFAULT_WEEKEND_OUTPUT_SCHEDULE = "0 14 * * 6"
DEFAULT_WEEKEND_REFLECTION_SCHEDULE = "0 9 * * 0"

# 周末任务状态（与 pipeline_jobs 类似，用于 repair 扫描）
WEEKEND_JOB_INPUT = "weekend_input"
WEEKEND_JOB_OUTPUT = "weekend_output"
WEEKEND_JOB_REFLECTION = "weekend_reflection"
WEEKEND_JOBS = [WEEKEND_JOB_INPUT, WEEKEND_JOB_OUTPUT, WEEKEND_JOB_REFLECTION]

# weekend_jobs 状态文件路径
WEEKEND_JOBS_PATH = PROJECT_ROOT / "memory" / "weekend-jobs.json"

# checkpoint 状态
JOB_STATUS_PENDING = "pending"
JOB_STATUS_RUNNING = "running"
JOB_STATUS_DONE = "done"
JOB_STATUS_FAILED = "failed"

# 步骤类型
STEP_CRITIC = "critic"
STEP_RESEARCHER = "researcher"
STEP_WRITER = "writer"
STEP_MONITOR = "monitor"  # v6.7.6: 全局监察步骤

# stale 阈值：running 超过该秒数视为死锁
STALE_RUNNING_SECONDS = 3600

# 最大自动重试次数
MAX_JOB_ATTEMPTS = 3
