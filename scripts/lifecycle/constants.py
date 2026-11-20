#!/usr/bin/env python3
"""生命周期 cron 框架常量。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

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
# v6.9.98: 输入首轮 09:00→09:30（多轮化，见下方锚点/夜间轮注释）
DEFAULT_WEEKEND_INPUT_SCHEDULE = "30 9 * * 6"
DEFAULT_WEEKEND_OUTPUT_SCHEDULE = "0 14 * * 6"
DEFAULT_WEEKEND_REFLECTION_SCHEDULE = "0 9 * * 0"

# v6.9.99（T2）周末收尾汇总 cron：周日 22:00（反思链 + 蒸馏小批之后）。
# 名称以 lc-weekend- 开头——与 input/output/reflection/worker 同组，
# 由 setup_weekend_crontab 统一重建（teardown 删前缀后重建全套，
# 避免"teardown 后 summary 永久消失"的安装闭环缺口）。
WEEKEND_SUMMARY_CRON_NAME = "lc-weekend-summary"
DEFAULT_WEEKEND_SUMMARY_SCHEDULE = "0 22 * * 0"

# v6.9.99（T2）周日蒸馏小批：20:00 固定 --batch 8。
# 与每日 12:50 主档（lc-kb-distill，--auto 自适应档）互不干扰——
# 主档按积压量升/降档（5/10/20 篇），本档恒定小批在周末窗口额外消化，
# 不参与 pending_distill_list 的档位计算口径。
KB_DISTILL_SUNDAY_CRON_NAME = "lc-kb-distill-sunday"
KB_DISTILL_SUNDAY_SCHEDULE = "0 20 * * 0"

# v6.9.98 周末输入链多轮化（T1）：
# - 锚点轮（日间保底触发）：worker（*/20 tick，run_next 路径）按冷却期
#   90 分钟自动接力开新轮，锚点 cron 只是保底——worker 正常时多数锚点
#   触发为幂等 no-op（阶段已 done 或已在跑新轮）；
# - 夜间轮（凌晨消化）：覆盖 00:00-08:00 无锚点时段，把周末窗口从
#   "周六上午单轮 30 篇浅摘要"扩展为"整个周末多轮深读"；
# - 全部触发同一入口 lc_weekend_input.sh（weekend_orchestrator --input）；
# - 全部登记进 lifecycle.cron_manifest.CRON_MANIFEST（缺失/重复/漂移
#   每小时对账），安装由 framework.setup_weekend_crontab 统一重建。
WEEKEND_INPUT_CRON_NAME = "lc-weekend-input"
WEEKEND_INPUT_ANCHOR_CRONS: List[Tuple[str, str]] = [
    ("lc-weekend-input-r2", "30 15 * * 6"),  # 周六 15:30
    ("lc-weekend-input-r3", "30 19 * * 6"),  # 周六 19:30
    ("lc-weekend-input-r4", "30 11 * * 0"),  # 周日 11:30
    ("lc-weekend-input-r5", "30 15 * * 0"),  # 周日 15:30
    ("lc-weekend-input-r6", "30 19 * * 0"),  # 周日 19:30
]
WEEKEND_INPUT_NIGHT_CRONS: List[Tuple[str, str]] = [
    ("lc-weekend-input-n1", "30 0 * * 6"),   # 周六 00:30
    ("lc-weekend-input-n2", "30 5 * * 6"),   # 周六 05:30
    ("lc-weekend-input-n3", "30 0 * * 0"),   # 周日 00:30
    ("lc-weekend-input-n4", "30 5 * * 0"),   # 周日 05:30
]

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

# v7.3.0: 方法手册第六评审模块（method_manual）的门槛常量。
# 手册就绪度分级 L0-L4（见 .hermes/skills/method-manual/SKILL.md 四节）：
# L0 占位/缺失、L1 提纲、L2 参数可复算、L3 协议可执行、L4 失效模式+溯源闭环。
# MANUAL_READY_LEVEL=3：达到 L3（协议可执行）才算"可开工"，模块方可过线
# （同时要求 critic 2 维口径分 ≥ 模块达标线且无 critical/high 缺口）。
MANUAL_READY_LEVEL = 3
# 手册实质内容下限（字节）：注册占位手册约 270B，低于此值视为占位未开工
MANUAL_MIN_BYTES = 400

# v6.8.26: 研究设想质量门槛——进入 optimizing 前的前置审核步骤
STEP_IDEA_REVIEW = "idea_review"
IDEA_REVIEW_THRESHOLD = 0.70       # 研究设想评审达标分数线
MAX_IDEA_REVIEW_ATTEMPTS = 3       # 最多迭代修复次数

# 微调度器 cron 名称与默认调度（每 15 分钟）
MICRO_SCHEDULER_NAME = "lc-micro-scheduler"
MICRO_SCHEDULER_SCHEDULE = "*/5 * * * 1-5"  # v7.2.66: 15→5 分钟回频（短步分级后占空比回升，回补 v7.1.7 降频的吞吐损失）

# v7.3.55: 并行试点 side-worker cron（与主 tick 错相 2 分钟；执行侧另有配置门控）
SIDE_WORKER_SCHEDULE = "2-59/5 * * * 1-5"

# prompt 自动优化与复盘 cron 表达式
DEFAULT_PROMPT_OPTIMIZE_SCHEDULE = "0 14 * * *"  # 每天 14:00（工作日时段间隙）
# v6.9.99（T2）撤除 DEFAULT_RETROSPECTIVE_SCHEDULE 与 lc-retrospective
# cron（周一 15:00）——复盘主函数由周日反思链内 reflection_link_deep_review
# job 复用执行（见 weekend_pipeline/maintenance_jobs.py）。

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

# 评审团 cron 宿主（v7.2.57）：每天 10:00 跑 panel_review --run-all。
# 背景（P0-1 根因残余）：panel_review_requested 标志由 monitor 设置后，
# 此前无任何 cron 调度宿主消费——11/11 课题同时带标志时主链自动轮转
# 冻结 126h，只能靠人工 --run-all 或健康检查轮救火（10-29 终结的 P0-1
# 停摆即此形态）。队列空时 --run-all 秒退零成本；10:00 在 lc-daily-
# orchestrate（08:55）入队之后、lc-kb-sync（12:40）之前，最坏卡滞
# 从"无限期"收敛到 24h。
PANEL_REVIEW_CRON_NAME = "lc-panel-review"
DEFAULT_PANEL_REVIEW_SCHEDULE = "0 10 * * *"  # 每天 10:00

# stale 阈值：running 超过该秒数视为死锁
# v6.8.3-fix9: 从 3600s 降低到 1800s（30min）。
# critic/writer 的 timeout 见下方分级常量（900/1200s），正常执行最长 ~12min。
# 1800s 给 hermes 足够的退出缓冲，同时避免卡住整个时段。
STALE_RUNNING_SECONDS = 1800

# critic/writer 超时分级（v6.8.52；v6.9.82 上调 900/1200 → 1200/1500）
# v6.8.52 背景：key-transient r4-scheme-critic 三连超时(900s)烧光 attempts
# 导致课题死锁（stuck=true, next_job=null）。实测大模块输入上下文长
# （scheme 42KB、rationale 46KB、full_review 跨全文），MiniMax 高峰期
# 变慢时 900s 不够用；profile_health 对超时失败的建议本身就是
# "可考虑增加 timeout"。
# v6.9.82 实证：critic 成功案例实测 840s–1140s（08-31 18:49 成功案例
# 约 19 分钟），普通模块 900s 上限随机砍掉大量本可完成的 job（全天
# critic 成功率 24%，15 次失败全部触顶超时而非解析问题）；凌晨备用
# 模型上 critic 也 >900s（3 连败触发 escape->open 停摆 1h15m）。
# 挂起风险由模型逃生兜底（分桶 2 次超时即切备用），白烧成本受控；
# writer 平均 387s 不受影响，仅慢尾受益。
# 1500s 仍 < STALE_RUNNING_SECONDS(1800s)，stale 僵死判定窗口安全。
CRITIC_WRITER_TIMEOUT_DEFAULT_S = 1200
CRITIC_WRITER_TIMEOUT_LARGE_S = 1500
# v7.3.0: method_manual critic 输入含手册头部 + 方案节选 + 素材包索引，
# 按大模块档放宽（与 rationale/scheme/full_review 同档）
# v7.3.14（BUG-40）：references 补入大模块档。optimize.py 的 references
# 分支写的是「上限对齐 critic_writer_timeout_s 的 LARGE 档 1500s」
# （v6.9.82/83 实测：references critic 成功案例 840–1140s，900s 基准
# 随机砍掉本可完成的 job），但 references 从未进 LARGE_TIMEOUT_SECTIONS
# → timeout 实为 1200s，min(1200, 1500) = 1200，该分支的「对齐 1500s」
# 意图自 v6.9.83 起从未生效。生产实证：ssh-weyl / houston 的 r2
# references-critic 连续触顶 1200s（elapsed 1200.96 / 1201.02 / 1201.13 /
# 1201.15 / 1201.21 / 1201.30），attempts 烧尽后阻塞 references-writer
# → method_manual-critic → method_manual-writer → monitor → update_vision
# 整条 r2 链。references 输入（references.md 23KB + 预检表 842B）远小于
# full_review（跨三章 106KB，同为 1500s 档且能成功），档位归属与实测
# 输入体量不匹配是根因。
LARGE_TIMEOUT_SECTIONS = {"rationale", "scheme", "full_review", "method_manual", "references"}


def critic_writer_timeout_s(section_key: str) -> int:
    """按模块返回 critic/writer 的超时秒数（大模块放宽，其余保持默认）。"""
    return CRITIC_WRITER_TIMEOUT_LARGE_S if section_key in LARGE_TIMEOUT_SECTIONS \
        else CRITIC_WRITER_TIMEOUT_DEFAULT_S


# ── 评分口径（caliber）唯一真相源 ──────────────────────────────────────
# v7.3.33（BUG-43）：score_history 条目的 caliber 分三类——章节 4 维加权分
# 与两维专用口径不可比，跨口径相减/取极值会制造伪信号。
#   section_4d     —— rationale/content/scheme/full_review 的 4 维加权分
#   references_2d  —— 引用审校（rigor/completeness 均值）
#   manual_2d      —— 方法手册就绪度（readiness/rigor 均值）
# 历史上三处消费点各写一份过滤口径且都漏了 manual_2d（v7.3.0 引入手册轮时
# 未同步），导致：health_sensor 把 references_2d→manual_2d 的口径切换误报为
# 「伪分数污染」、Web API 把手册分当章节分展示、should_auto_rollback 把
# 手册分当章节分参与「连续下降/历史最佳」判定。现统一到本常量。
CALIBER_SECTION_4D = "section_4d"
CALIBER_REFERENCES_2D = "references_2d"
CALIBER_MANUAL_2D = "manual_2d"

# 两维专用口径集合——与章节 4 维口径不可比，不参与章节分连续性判定
TWO_DIM_CALIBERS = frozenset({CALIBER_REFERENCES_2D, CALIBER_MANUAL_2D})

# 章节口径标识（focus_section 侧）——与 caliber 同义的另一种表示
TWO_DIM_SECTIONS = ("references", "method_manual")


def is_two_dim_caliber(entry: Dict[str, Any]) -> bool:
    """判定 score_history 条目是否为两维专用口径（不可与章节 4 维比较）。

    优先读 caliber 字段；缺 caliber 的历史条目按 focus_section 兜底
    （与 micro_scheduler._section_mean_score 同口径）。
    """
    cal = entry.get("caliber")
    if cal:
        return cal in TWO_DIM_CALIBERS
    return entry.get("focus_section") in TWO_DIM_SECTIONS


def filter_section_caliber(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """滤出章节 4 维口径条目（排除 references / method_manual 两维口径）。"""
    return [e for e in (history or []) if not is_two_dim_caliber(e)]

# 最大自动重试次数
MAX_JOB_ATTEMPTS = 3

# 软卡死阈值：连续聚焦同一 proposal 超过该时段数且轮次无推进时强制让出
# v6.8.10: 原本微调度器只检查"硬卡死"（failed job 阻塞 pending），
# 但 failed job 若不阻塞下游（如独立 content 模块），proposal 既不完成
# 也不卡死，导致永久占用焦点。该阈值确保最多 N 个时段后强制让出。
MAX_SOFT_STUCK_SLOTS = 2  # v6.8.20: 3→2，一个课题最多连续聚焦两个时段
