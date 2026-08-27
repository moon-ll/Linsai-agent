#!/usr/bin/env python3
"""生命周期 cron 拓扑清单（v6.8.54）：声明式协调取代隐式时间错开。

背景（2026-08-14 架构评审结论）：16 个 cron 的时序协调此前完全靠
"时间错开 + 各自为政"，跨机制错误假设频发——cron setup 不幂等导致副本
翻倍（v6.8.53 修）、lc-kb-sync 双实例、monitor 只按前缀匹配无法发现
"调度表达式漂移"（同名 cron 存在但跑错了时间）。本模块把期望拓扑
声明为单一真相源：

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
    DEFAULT_PROMPT_OPTIMIZE_SCHEDULE,
    DEFAULT_REPAIR_SCHEDULE,
    DEFAULT_RETROSPECTIVE_SCHEDULE,
    KB_DISTILL_CRON_NAME,
    KB_SYNC_CRON_NAME,
)

# ── 拓扑清单 ─────────────────────────────────────────────────────────
# schedule=None 表示"仅校验存在性"（调度由安装方决定或按参数化生成），
# 其余条目校验调度表达式与清单一致（漂移即告警）。
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
    "lc-prompt-optimize": {
        "schedule": DEFAULT_PROMPT_OPTIMIZE_SCHEDULE,
        "category": "framework",
        "purpose": "每日 14:00 prompt 自动优化（备份原文件）",
        "depends": [],
    },
    "lc-retrospective": {
        "schedule": DEFAULT_RETROSPECTIVE_SCHEDULE,
        "category": "framework",
        "purpose": "每周一 15:00 链路复盘",
        "depends": [],
    },
    "lc-daily-backup": {
        "schedule": "0 13 * * *",
        "category": "framework",
        "purpose": "每日 13:00 用户数据备份（24h 幂等防重 + 轮转保留最近 7 份，v6.9.54；v6.9.62 由 03:17 移窗避开 worker 时段并发写、并补入 framework 安装闭环）",
        "depends": [],
    },
    "lc-daily-sync": {
        "schedule": "0 23 * * *",
        "category": "framework",
        "purpose": "每日 23:00 日终同步 hermes 产出→知识库（sync_all；与 12:40 kb-sync 各覆盖半天进料，v6.9.58 补录——此前游离在清单外是拓扑对账盲区；v6.9.62 补入安装闭环）",
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
    "lc-hourly-monitor": {
        "schedule": None,
        "category": "monitor",
        "purpose": "每小时健康检查：cron 对账/卡住课题/连续失败/告警去重通知",
        "depends": [],
    },
    "lc-micro-scheduler": {
        "schedule": None,
        "category": "scheduler",
        "purpose": "微调度器：时段内派发 job、清理 stale、维护看板",
        "depends": ["lc-daily-orchestrate"],
    },
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
    ok_crons += [
        {"name": "lc-weekend-input", "schedule": "0 9 * * 6"},
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
        if c["name"] == "lc-retrospective":
            c["schedule"] = "0 3 * * 1"
    kinds = {i["kind"] for i in validate_cron_topology(drift)}
    assert "drift" in kinds, "调度漂移应被检出"
    print("✓ validate_cron_topology：缺失/重复/漂移三类问题均可检出")


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        _self_check()
