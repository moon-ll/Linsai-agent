#!/usr/bin/env python3
"""生命周期 cron 拓扑清单（v6.8.54）：声明式协调取代隐式时间错开。

背景（2026-08-14 架构评审结论）：16 个 cron 的时序协调此前完全靠
"时间错开 + 各自为政"，跨机制错误假设频发——cron setup 不幂等导致副本
翻倍（v6.8.53 修）、lc-kb-sync 双实例、monitor 只按前缀匹配无法发现
"调度表达式漂移"（同名 cron 存在但跑错了时间）。本模块把期望拓扑
声明为单一真相源：

  v8.0.0 注记（2026-11-16）：本清单为 v7 优化环 cron 拓扑，已随优化环停用退役；
  v8 实际调度清单见 topic_pipeline/cron.py 的 V8_CRON_JOBS 与
  workbench_monitor.V8_CRON_EXPECTED。不要用 --setup-cron-v2 重装本清单
  （会复活已停用的优化环 job）。

  - framework.py 安装时对照清单创建（幂等 helper 已在 v6.8.53 落地）；
  - lifecycle_monitor._check_cron_status 用 validate_cron_topology() 对账，
    检出缺失/重复/调度漂移三类问题并触发自动修复。

用法：
    from lifecycle.cron_manifest import CRON_MANIFEST, validate_cron_topology
    issues = validate_cron_topology(hermes_bridge.cron_list_profile("linsai"))

自检：
    python3 -m lifecycle.cron_manifest --self-check
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .constants import (
    DEFAULT_KB_DISTILL_SCHEDULE,
    DEFAULT_KB_SYNC_SCHEDULE,
    DEFAULT_ORCHESTRATE_SCHEDULE,
    DEFAULT_PANEL_REVIEW_SCHEDULE,
    DEFAULT_PROMPT_OPTIMIZE_SCHEDULE,
    DEFAULT_REPAIR_SCHEDULE,
    DEFAULT_WEEKEND_INPUT_SCHEDULE,
    DEFAULT_WEEKEND_SUMMARY_SCHEDULE,
    KB_DISTILL_CRON_NAME,
    KB_DISTILL_SUNDAY_CRON_NAME,
    KB_DISTILL_SUNDAY_SCHEDULE,
    KB_SYNC_CRON_NAME,
    MICRO_SCHEDULER_SCHEDULE,  # v7.2.1: 启用 lc-micro-scheduler 漂移检测
    PANEL_REVIEW_CRON_NAME,  # v7.2.57: 评审团宿主
    SIDE_WORKER_SCHEDULE,  # v7.3.55: 并行试点 side-worker
    WEEKEND_INPUT_ANCHOR_CRONS,
    WEEKEND_INPUT_CRON_NAME,
    WEEKEND_INPUT_NIGHT_CRONS,
    WEEKEND_SUMMARY_CRON_NAME,
)

# ── 拓扑清单 ─────────────────────────────────────────────────────────
# schedule=None 表示"仅校验存在性"（调度由安装方决定或按参数化生成），
# 其余条目校验调度表达式与清单一致（漂移即告警）。
# 对账范围说明（v6.10.43）：本清单只收录 lifecycle 域 cron。
# 以下不参与对账（非遗漏）：
#   - "林赛简报"5 条（检索入池/候选推送/健康检查/高分自动深读/每日汇总）
#     —— hermes 简报域，自有 schema 与落盘；
#   - lc-prompt-optimize —— 已暂停（见下方注释）；
#   - lc-weekend-worker —— worker 前缀动态生成，不参与数量对账。
CRON_MANIFEST: Dict[str, Dict[str, Any]] = {
    "lc-daily-orchestrate": {
        "schedule": DEFAULT_ORCHESTRATE_SCHEDULE,
        "category": "framework",
        "purpose": "每日编排：时段规划 + per-proposal worker 安装/卸载",
        "depends": ["lc-hourly-monitor"],
    },
    "lc-repair": {
        "schedule": DEFAULT_REPAIR_SCHEDULE,
        "category": "framework",
        "purpose": "每 6h 链路修复：stale 重置/失败重试/双上限自动解锁",
        "depends": [],
    },
    # lc-prompt-optimize 已于 v6.9.68 暂停并移出期望拓扑（否则 monitor
    # 每小时对账报 missing）。暂停原因与整改项：只增不减（41/41 append）、
    # 审计虚标 verified、writer SOUL 12.5KB 而分数净-27。
    #
    # v6.9.87 二次保险：原修复仅停留在清单层面，hermes cron 实际仍 enabled
    # 且 2026-09-02 06:00Z 触发 9 条 suggestions auto-applied 污染 SOUL.md。
    # 现已在 scripts/prompt_optimizer.py cmd_auto 入口加 PROMPT_OPTIMIZER_ENABLED
    # 守卫（默认 False = 暂停，env PROMPT_OPTIMIZER_ENABLED=1 显式启用），
    # cron 配置保持不变避免影响其它 gateway 行为。恢复方法：
    #   1) 一次性：export PROMPT_OPTIMIZER_ENABLED=1 后跑 auto
    #   2) 永久恢复：把本条目加回 CRON_MANIFEST 并设 PROMPT_OPTIMIZER_ENABLED 常量
    #     hermes --profile linsai cron create "0 14 * * *" --name lc-prompt-optimize \
    #       --script lc_prompt_optimize.sh --no-agent --deliver local \
    #       --workdir /Users/ll/Desktop/LinSai-CoPilot
    # （schedule 常量 DEFAULT_PROMPT_OPTIMIZE_SCHEDULE 保留）。
    # v6.9.99（T2）撤除 lc-retrospective（周一 15:00）——复盘主函数
    # retrospective.run_retrospective 由周日反思链内 reflection_link_deep_review
    # job 复用执行（报告落 memory/weekend-reflection/link-deep-review-{date}.md），
    # 周一独立 cron 不再需要。残留实例由 monitor 对账外的手工/安装清理移除。
    # v7.2.67 迁移：治理全部转 ZCode 定时任务（运转/治理分离，用户裁决
    # 10-31）——本 cron 已 pause，确定性四相由 ZCode 每日治理会话（16:40）
    # 驱动 self_optimizer.py --run 执行，智能实施由该会话完成。
    # v7.2.65: 自迭代每日窗口（用户裁决 10-31）——16:30 为全周唯一无固定
    # 任务碰撞槽位（工作日 13-18 设计空窗内、避开周六 14:00 weekend-output
    # 与 18:50 蒸馏）。编排：活指标摘要→基准门→提案 worklist→台账；
    # 零 LLM、零自动应用（变异须经基准门+试点+台账三闸，DGM 式准入）。
    "lc-self-optimize": {
        "schedule": "30 16 * * *",
        "category": "framework",
        "purpose": "每日 16:30 自迭代窗口：self_optimizer 四相（摘要/基准门/提案/台账）",
        "depends": [],
    },
    "lc-daily-backup": {
        "schedule": "0 13 * * *",
        "category": "framework",
        "purpose": "每日 13:00 用户数据备份（24h 幂等防重 + 轮转保留最近 7 份，v6.9.54；v6.9.62 由 03:17 移窗避开 worker 时段并发写、并补入 framework 安装闭环）",
        "depends": [],
    },
    KB_SYNC_CRON_NAME: {
        "schedule": DEFAULT_KB_SYNC_SCHEDULE,
        "category": "framework",
        "purpose": "每日 12:40 知识库治理：多端同步 + 索引/图谱重建 + 生长晋升",
        "depends": [],
    },
    KB_DISTILL_CRON_NAME: {
        "schedule": DEFAULT_KB_DISTILL_SCHEDULE,
        "category": "framework",
        "purpose": "每日 12:50 知识库蒸馏：raw→wiki 批量 5 篇（最旧优先）",
        "depends": [KB_SYNC_CRON_NAME],
    },
    # v6.9.99（T2）周日蒸馏小批：固定 --batch 8，独立于每日主档的
    # --auto 自适应档（主档按积压 5/10/20 篇升降档，本档恒定小批
    # 在周末窗口额外消化，不干扰主档口径）。
    # v6.9.72 加：18:50 第二档（--auto，与 12:50 主档 FIFO 取不重复）。
    # v6.10.x 曾撤出 manifest 导致对账盲区，v6.10.43 补录。
    "lc-kb-distill-pm": {
        "schedule": "50 18 * * *",
        "category": "framework",
        "purpose": "每日 18:50 知识库蒸馏第二档（--auto + kb_linker 补边）",
    },
    # v7.1.5: 凌晨 02:50 第三档（追赶档）——承接早高峰前的积压，消化昨
    # 日漏网与新进料；与 12:50/18:50/周日20:00 形成 4 时段蒸馏节奏。
    "lc-kb-distill-night": {
        # v7.2.66 治理减法第一档暂停（积压 0，12:50 主档足够消化日增；恢复：hermes cron resume
        "schedule": "50 2 * * *",
        "category": "framework",
        "purpose": "每日 02:50 知识库蒸馏第三档（--auto，凌晨追赶档）",
        "depends": [],
    },
    # v6.9.70 删除后于 09-02 被重建（sync_engine __main__ 已改为真 sync_all，
    # 不再是当年的 self_check 冒充），v6.10.43 补录消除对账盲区前科。
    "lc-daily-sync": {
        "schedule": "0 23 * * *",
        "category": "framework",
        "purpose": "每日 23:00 日终同步 hermes 产出→知识库（sync_all）",
        "depends": [],
    },
    KB_DISTILL_SUNDAY_CRON_NAME: {
        # v7.3.10 补注：与 lc-kb-distill-night 同批暂停（2026-10-30T23:57Z
        # 治理减法第一档，积压 0，12:50 主档足够消化日增；恢复：
        # hermes cron resume lc-kb-distill-sunday）
        "schedule": KB_DISTILL_SUNDAY_SCHEDULE,
        "category": "framework",
        "purpose": "周日 20:00 蒸馏小批：kb_distill --batch 8（周末额外消化）",
        "depends": [KB_DISTILL_CRON_NAME],
    },
    "lc-hourly-monitor": {
        "schedule": None,
        "category": "monitor",
        "purpose": "每小时健康检查：cron 对账/卡住课题/连续失败/告警去重通知",
        "depends": [],
    },
    "lc-micro-scheduler": {
        # v7.2.1: 登记实际 schedule 启用 validate_cron_topology 漂移检测
        # 历史 schedule=None 跳过漂移检测 → v7.1.7 节奏降频（5→15 分钟）
        # 部署未生效 4h 才被体检发现
        "schedule": MICRO_SCHEDULER_SCHEDULE,
        "category": "scheduler",
        "purpose": "微调度器：时段内派发 job、清理 stale、维护看板",
        "depends": ["lc-daily-orchestrate"],
    },
    # v7.3.55: 并行试点 side-worker（目标判据 G2-D 配套·用户裁决 2026-11-06）。
    # 与主 tick 错相 2 分钟（2-59/5），互补消费非聚焦课题 ready job，实现 2 并发；
    # 执行侧配置门控（memory/config/schedules/parallel-workers.json，默认禁用），
    # cron 常驻但空转秒退——配额紧张时置 enabled=false 即回退单并发，无需撤 cron。
    "lc-side-worker": {
        "schedule": SIDE_WORKER_SCHEDULE,
        "category": "scheduler",
        "purpose": "并行试点 side-worker：互补消费非聚焦课题 ready job（单 job/次，配置门控）",
        "depends": ["lc-daily-orchestrate"],
    },
    PANEL_REVIEW_CRON_NAME: {
        # v7.2.57: 评审团宿主——此前 panel/review 类 cron 为 0，
        # panel_review_requested 标志积压无人消费致主链轮转冻结
        # （P0-1 停摆 126h 的根因残余）。队列空时 --run-all 秒退。
        "schedule": DEFAULT_PANEL_REVIEW_SCHEDULE,
        "category": "framework",
        "purpose": "每日 10:00 评审团队列消费：三角色评审+writer 深度修改+critic 验收",
        "depends": ["lc-daily-orchestrate"],
    },
}

# v6.9.98 周末输入链多轮化（T1）：首轮 + 5 锚点轮 + 4 夜间轮全部登记，
# 参与缺失/重复/漂移三类对账（monitor 每小时核验）。全部触发同一入口
# lc_weekend_input.sh（weekend_orchestrator --input）；轮次接力由
# weekend worker（*/20，run_next 路径）按冷却期完成，锚点/夜间 cron
# 只是保底触发与夜间时段覆盖。安装由 framework.setup_weekend_crontab
# 统一重建（teardown 删除 lc-weekend- 前缀后重建全套）。
CRON_MANIFEST[WEEKEND_INPUT_CRON_NAME] = {
    "schedule": DEFAULT_WEEKEND_INPUT_SCHEDULE,
    "category": "weekend",
    "purpose": "周末输入链首轮（周六 09:30）：collect→deep_digest→cluster→distill→match→compose",
    "depends": [],
}
for _name, _sched in WEEKEND_INPUT_ANCHOR_CRONS:
    CRON_MANIFEST[_name] = {
        "schedule": _sched,
        "category": "weekend",
        "purpose": f"输入链锚点轮保底触发（{_sched}）：轮次接力由 weekend worker 完成",
        "depends": [WEEKEND_INPUT_CRON_NAME],
    }
for _name, _sched in WEEKEND_INPUT_NIGHT_CRONS:
    CRON_MANIFEST[_name] = {
        "schedule": _sched,
        "category": "weekend",
        "purpose": f"输入链夜间轮（{_sched}）：凌晨时段覆盖，同 --input 入口幂等触发",
        "depends": [WEEKEND_INPUT_CRON_NAME],
    }
del _name, _sched

# v6.9.99（T2）周末收尾汇总：周日 22:00，零 LLM 汇总本周末产出。
# 与 input/output/reflection/worker 同属 lc-weekend- 前缀组，安装由
# setup_weekend_crontab 统一重建（teardown 删前缀后重建全套）。
CRON_MANIFEST[WEEKEND_SUMMARY_CRON_NAME] = {
    "schedule": DEFAULT_WEEKEND_SUMMARY_SCHEDULE,
    "category": "weekend",
    "purpose": "周日 22:00 周末收尾汇总：消化轮次/簇/路由/校准 high/方法页变动",
    "depends": [],
}

# 周末任务组（三个子任务 + weekend worker，按前缀校验存在性）
WEEKEND_CRON_PREFIX = "lc-weekend-"

# worker 前缀：v6.7.5 的 per-proposal worker cron 已被微调度器集中派发
# 取代（v6.8+），现存实例仅作为遗留清理目标（orchestrator.run_repair
# 会删除不属 optimizing 的 lc-worker-*）。不参与拓扑对账，防止
# "worker 数 0 ≠ 课题数 N" 的永久性误报。
WORKER_CRON_PREFIX = "lc-worker-"


def validate_cron_topology(
    actual_crons: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    """对账实际 cron 与清单，返回问题列表（空列表 = 拓扑一致）。

    Args:
        actual_crons: hb.cron_list_profile() 的原始返回。

    Returns:
        [{"kind": "missing"|"duplicate"|"drift", "name": ..., "detail": ...}]
    """
    issues: List[Dict[str, str]] = []
    names = [c.get("name", "") for c in actual_crons]

    # 1. 缺失 + 重复 + 调度漂移（按清单逐条对账）
    for name, spec in CRON_MANIFEST.items():
        instances = [c for c in actual_crons if c.get("name", "") == name]
        if not instances:
            issues.append({"kind": "missing", "name": name,
                           "detail": f"{name} 不存在（{spec['purpose'][:20]}…）"})
            continue
        if len(instances) > 1:
            issues.append({"kind": "duplicate", "name": name,
                           "detail": f"{name} 存在 {len(instances)} 份副本"})
            continue
        expected = spec.get("schedule")
        actual_sched = instances[0].get("schedule", "")
        if expected and actual_sched != expected:
            issues.append({
                "kind": "drift", "name": name,
                "detail": f"{name} 调度漂移: 期望 {expected!r} 实际 {actual_sched!r}",
            })

    # 2. 周末任务组（存在性）
    if not any(n.startswith(WEEKEND_CRON_PREFIX) for n in names):
        issues.append({"kind": "missing", "name": f"{WEEKEND_CRON_PREFIX}*",
                       "detail": "周末任务 cron 组（input/output/reflection）全部缺失"})

    return issues


def _self_check() -> None:
    """自检：清单完整性 + validate 三类问题检出。"""
    print("=== cron_manifest 自检 ===")
    assert len(CRON_MANIFEST) >= 7, "清单至少覆盖 7 个固定 cron"
    for name, spec in CRON_MANIFEST.items():
        assert spec.get("category"), f"{name} 缺少 category"
        assert spec.get("purpose"), f"{name} 缺少 purpose"
    print(f"✓ 清单完整（{len(CRON_MANIFEST)} 固定 + 周末组 + worker 动态）")

    ok_crons = [{"name": n, "schedule": (s.get("schedule") or "0 9 * * 1")}
                for n, s in CRON_MANIFEST.items()]
    # v6.9.98: lc-weekend-input 已进清单（schedule 明确参与漂移对账），
    # 此处仅补一个清单外周末名验证前缀组存在性检查仍然生效
    ok_crons += [
        {"name": "lc-weekend-output", "schedule": "0 14 * * 6"},
        {"name": "lc-worker-p1", "schedule": "*/20 * * * *"},
    ]
    assert validate_cron_topology(ok_crons) == [], \
        "完全一致的拓扑不应产生问题（worker 为遗留清理目标不参与对账）"

    miss = [c for c in ok_crons if c["name"] != "lc-repair"]
    kinds = {i["kind"] for i in validate_cron_topology(miss)}
    assert "missing" in kinds, "缺失应被检出"

    dup = ok_crons + [{"name": "lc-repair", "schedule": "x"}]
    kinds = {i["kind"] for i in validate_cron_topology(dup)}
    assert "duplicate" in kinds, "重复应被检出"

    drift = [dict(c) for c in ok_crons]
    for c in drift:
        # v6.9.99: lc-retrospective 已撤出清单，漂移用例改用每日备份 cron
        if c["name"] == "lc-daily-backup":
            c["schedule"] = "17 3 * * *"
    kinds = {i["kind"] for i in validate_cron_topology(drift)}
    assert "drift" in kinds, "调度漂移应被检出"
    print("✓ validate_cron_topology：缺失/重复/漂移三类问题均可检出")


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        _self_check()
