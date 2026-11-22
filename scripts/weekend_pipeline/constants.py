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
# v6.9.98: STEP_SUMMARIZE 已废弃——deep_digest（结构化深读）取代浅摘要，
# 常量保留仅供历史 state 解读参考，新链路使用 STEP_DEEP_DIGEST
STEP_SUMMARIZE = "summarize"
STEP_DEEP_DIGEST = "deep_digest"  # v6.9.98: 结构化深读（单轮 10 篇，全文输入）
STEP_ANALYZE = "analyze"
STEP_SELECT = "select"
STEP_RETRIEVE = "retrieve"
STEP_DEEP_READ = "deep_read"
STEP_COMPOSE = "compose"
# v6.9.12: 知识簇链路（取代 input 阶段的 analyze/select 旧用途）
STEP_CLUSTER_ASSIGN = "cluster_assign"    # 增量归簇（零 LLM）
STEP_CLUSTER_DISTILL = "cluster_distill"  # 簇内提炼（LLM 知识卡）
STEP_METHODS_SETTLE = "methods_settle"    # v6.10.0（T3）：方法学专题沉淀
STEP_TOPIC_MATCH = "topic_match"          # 簇 vs 全阶段课题路由判断
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
# v6.9.99 周末维护链（T2）：反思链尾三个新 step（handler 见 maintenance_jobs.py）
STEP_PROPOSAL_CALIBRATION = "proposal_calibration"  # 优化中课题零 LLM 程序化校准
STEP_LINK_DEEP_REVIEW = "link_deep_review"          # 全链路深度复盘（复用 retrospective）
STEP_KB_TAXONOMY_APPLY = "kb_taxonomy_apply"        # 分类体系候选执行（含空候选产物）
STEP_PANEL_PLAN = "panel_plan"                      # v6.10.15: 评审团执行计划（panel_request 队列盘点）

# v6.9.7: processed_sources 滚动裁剪保留窗口（天），与 error_history 裁剪策略对齐
PROCESSED_SOURCES_MAX_AGE_DAYS = 28

# ── v6.9.98: 输入链多轮化（deep_digest + 轮次接力） ──────────────────────
# deep_digest job id（jobs 模板与 rounds 接力判定的共同引用）
INPUT_DEEP_DIGEST_JOB_ID = "input_deep_digest_papers"
# 单轮深读批量上限（篇）：全文输入 + 结构化 JSON 输出，成本高于旧浅摘要
# （30 篇 × 60s），故 30→10；吞吐由多轮接力补回（每轮冷却 90 分钟）
DIGEST_BATCH_LIMIT = 10
# 轮次接力冷却期（秒）：整轮六步走完后距 input 阶段最后完成时间的最小间隔
INPUT_ROUND_COOLDOWN_SECONDS = 90 * 60
# cluster_distill 每轮簇上限（v6.9.98 语义变更：原"周限 8 簇"改为"每轮 ≤3 簇"，
# 多轮化下一个周末约 7 轮 × 3 = 21 簇，总吞吐提升且单轮 LLM 成本受控）
CLUSTER_DISTILL_ROUND_CAP = 3

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

# v7.2.46：failed job 达修复上限后的自动解锁冷却时长（小时）。
# 根因修复后需给足落地时间，避免短时间连环重置；与
# lifecycle.utils.should_auto_unlock 的 cooldown_hours=24.0 同口径。
AUTO_UNLOCK_COOLDOWN_HOURS = 24.0

# stale 阈值：running 超过该秒数视为死锁
STALE_RUNNING_SECONDS = 3600

# 默认 cron 表达式
DEFAULT_WORKER_SCHEDULE = "*/20 * * * 6,0"
# v6.9.98: 输入首轮 09:00→09:30——周六凌晨夜间轮（00:30/05:30）先消化积压，
# 09:30 首轮锚点与周六 output（14:00）之间留出轮次接力冷却空间
DEFAULT_WEEKEND_INPUT_SCHEDULE = "30 9 * * 6"
DEFAULT_WEEKEND_OUTPUT_SCHEDULE = "0 14 * * 6"
DEFAULT_WEEKEND_REFLECTION_SCHEDULE = "0 9 * * 0"

# Proposal KB 子目录
NSFC_PROPOSALS_KB_DIR = (
    PROJECT_ROOT / "knowledge" / "wiki" / "projects" / "NSFC-强场超快" / "proposals"
)

# cron 名称
WEEKEND_WORKER_CRON_NAME = "lc-weekend-worker"
