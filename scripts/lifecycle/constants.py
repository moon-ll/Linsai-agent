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
DEFAULT_REPAIR_SCHEDULE = "0 */12 * * *"  # v6.9.68: 6h→12h 降频（28 次扫描/7d 中有效动作近零）

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

# v6.7.12: researcher 拆分为 4 个连贯子步骤
STEP_GAP_IDENTIFY = "gap_identify"
STEP_LIT_SEARCH = "lit_search"
STEP_LIT_READ = "lit_read"
STEP_LIT_NOTE = "lit_note"

# v6.8.0: 一轮结束后的衍生更新步骤
STEP_UPDATE_VISION = "update_vision"
STEP_UPDATE_METHOD_MANUAL = "update_method_manual"

# v6.8.26: 研究设想质量门槛——进入 optimizing 前的前置审核步骤
STEP_IDEA_REVIEW = "idea_review"
IDEA_REVIEW_THRESHOLD = 0.70       # 研究设想评审达标分数线
MAX_IDEA_REVIEW_ATTEMPTS = 3       # 最多迭代修复次数

# 微调度器 cron 名称与默认调度（每 5 分钟）
MICRO_SCHEDULER_NAME = "lc-micro-scheduler"
MICRO_SCHEDULER_SCHEDULE = "*/5 * * * 1-5"  # 工作日每 5 分钟一次

# prompt 自动优化与复盘 cron 表达式
DEFAULT_PROMPT_OPTIMIZE_SCHEDULE = "0 14 * * *"  # 每天 14:00（工作日时段间隙）
DEFAULT_RETROSPECTIVE_SCHEDULE = "0 15 * * 1"  # 每周一 15:00（周末反思产出后）

# 知识库每日同步 cron（v6.8.51）：sync_all（hermes 会话/简报/PDF 同步 + 重建索引 + 图谱）
# 12:40 = 上午时段（08:30-12:30）结束后、下午空档，避开 worker 竞争 I/O
DEFAULT_KB_SYNC_SCHEDULE = "40 12 * * *"  # 每天 12:40
KB_SYNC_CRON_NAME = "lc-kb-sync"

# 知识库每日蒸馏 cron（v6.9.5）：kb_distill 批量 raw→wiki 蒸馏（最旧 5 篇/天）
# 12:50 = lc-kb-sync 之后 10 分钟，确保先完成多端同步与索引重建再取清单，
# 避免蒸馏到刚同步一半的 raw。351 项积压按此速率约 70 天消化。
DEFAULT_KB_DISTILL_SCHEDULE = "50 12 * * *"  # 每天 12:50
KB_DISTILL_CRON_NAME = "lc-kb-distill"

# 每日用户数据备份 cron（v6.9.54 引入，v6.9.62 补入安装闭环 + 移窗）
# 13:00（v6.9.62，原 03:17）——避开 00:30-03:30 worker 时段（zip 打包
# 860MB 期间并发写可使 zf.write 抛 FileNotFoundError 致当日备份静默跳过）
# 与 12:40/12:50 知识库任务链；午后无 worker 时段。
DAILY_BACKUP_SCHEDULE = "0 13 * * *"  # 每天 13:00
DAILY_BACKUP_CRON_NAME = "lc-daily-backup"

# 每日日终同步 cron（v6.9.58 补录 manifest，v6.9.62 补入安装闭环）
DAILY_SYNC_SCHEDULE = "0 23 * * *"  # 每天 23:00
DAILY_SYNC_CRON_NAME = "lc-daily-sync"

# stale 阈值：running 超过该秒数视为死锁
# v6.8.3-fix9: 从 3600s 降低到 1800s（30min）。
# critic/writer 的 timeout 见下方分级常量（900/1200s），正常执行最长 ~12min。
# 1800s 给 hermes 足够的退出缓冲，同时避免卡住整个时段。
STALE_RUNNING_SECONDS = 1800

# critic/writer 超时分级（v6.8.52）
# 背景：key-transient r4-scheme-critic 三连超时(900s)烧光 attempts 导致课题死锁
# （stuck=true, next_job=null）。实测大模块输入上下文长（scheme 42KB、
# rationale 46KB、full_review 跨全文），MiniMax 高峰期变慢时 900s 不够用；
# 而 profile_health 对超时失败的建议本身就是"可考虑增加 timeout"。
# 1200s 仍 < STALE_RUNNING_SECONDS(1800s)，stale 僵死判定窗口安全。
CRITIC_WRITER_TIMEOUT_DEFAULT_S = 900
CRITIC_WRITER_TIMEOUT_LARGE_S = 1200
LARGE_TIMEOUT_SECTIONS = {"rationale", "scheme", "full_review"}


def critic_writer_timeout_s(section_key: str) -> int:
    """按模块返回 critic/writer 的超时秒数（大模块放宽，其余保持默认）。"""
    return CRITIC_WRITER_TIMEOUT_LARGE_S if section_key in LARGE_TIMEOUT_SECTIONS \
        else CRITIC_WRITER_TIMEOUT_DEFAULT_S

# 最大自动重试次数
MAX_JOB_ATTEMPTS = 3

# 软卡死阈值：连续聚焦同一 proposal 超过该时段数且轮次无推进时强制让出
# v6.8.10: 原本微调度器只检查"硬卡死"（failed job 阻塞 pending），
# 但 failed job 若不阻塞下游（如独立 content 模块），proposal 既不完成
# 也不卡死，导致永久占用焦点。该阈值确保最多 N 个时段后强制让出。
MAX_SOFT_STUCK_SLOTS = 2  # v6.8.20: 3→2，一个课题最多连续聚焦两个时段
