#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""工作台轻量健康检查（v8）——替代 v7 lifecycle_monitor 的精简版。

检查四件事（v8 不再有优化环，监控面大幅收窄）：
① cron 对账：v8 保留清单（文献/KB/备份/深研）逐个存在性校验；
② topics 健康：kickoff 停滞（>3 天无更新）、needs_human 待办计数；
③ 备份新鲜度：每日 auto 备份包产物级校验（cron 对账只看 job 存在性，
   11-14/11-16 两天缺包未被发现的盲区由此补上）；
④ KB 告警：复用 health_sensor 的知识库告警（fail-open）。
结果写 memory/workbench-monitor.json，异常打印 ⚠。

用法示例：
    python3 scripts/workbench_monitor.py [--dry-run]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from common import load_json, save_json  # noqa: E402

PROJECT_ROOT = Path(__file__).parent.parent
MONITOR_STATE = PROJECT_ROOT / "memory" / "workbench-monitor.json"

# v8 cron 对账基准（与 topic_pipeline/cron.py、设计文档 §6 一致）
V8_CRON_EXPECTED = [
    "lc-topic-daily",
    "lc-workbench-monitor",
    "lc-kb-sync", "lc-kb-distill", "lc-kb-distill-pm",
    "lc-weekend-input",
    "lc-daily-backup", "lc-zcode-worker",
]
KICKOFF_STALL_DAYS = 3
# 备份新鲜度分级：>30h=缺 1 个日备份周期（medium，转日报）；
# >54h=连续缺 2 个周期（high，备份链疑似断裂，入治理门）。
# 容忍备份本身耗时（约 20 分钟）与调度抖动，故 Warn 取 24h+6h。
BACKUP_WARN_HOURS = 30.0
BACKUP_CRITICAL_HOURS = 54.0


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_crons() -> List[Dict[str, Any]]:
    """hermes cron 对账（missing 报告，drift/重复不再属于 v8 风险面）。"""
    try:
        import hermes_bridge as hb
        jobs = {j.get("name"): j for j in hb.cron_list_profile("linsai")}
    except Exception as e:  # noqa: BLE001
        return [{"issue": f"hermes_bridge 不可用: {e}"}]
    issues: List[Dict[str, Any]] = []
    for name in V8_CRON_EXPECTED:
        if name not in jobs:
            issues.append({"issue": f"cron 缺失: {name}", "severity": "high"})
    return issues


def check_topics() -> List[Dict[str, Any]]:
    """topics 健康：kickoff 停滞 + needs_human 待办。"""
    from topic_pipeline import state as tstate
    data = tstate.load_state()
    issues: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    for tid, rec in (data.get("topics") or {}).items():
        if not isinstance(rec, dict):
            continue
        if rec.get("stage") == "kickoff":
            updated = rec.get("updated_at") or rec.get("created_at") or ""
            try:
                dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                if (now - dt).days >= KICKOFF_STALL_DAYS:
                    issues.append({"issue": f"kickoff 停滞 ≥{KICKOFF_STALL_DAYS} 天: {tid}",
                                   "severity": "medium"})
            except ValueError:
                pass
    needs = [tid for tid, rec in (data.get("topics") or {}).items()
             if isinstance(rec, dict) and rec.get("needs_human")]
    if needs:
        issues.append({"issue": f"needs_human 待人裁决 {len(needs)} 个: {','.join(needs[:5])}",
                       "severity": "medium"})
    return issues


def check_kb() -> List[Dict[str, Any]]:
    """KB 告警复用（fail-open：health_sensor 不可用只警告不阻塞）。"""
    try:
        import health_sensor
        alerts = health_sensor.collect_alerts() if hasattr(health_sensor, "collect_alerts") else []
        kb_alerts = [a for a in alerts if isinstance(a, dict)
                     and str(a.get("category", "")).startswith("kb")]
        return [{"issue": a.get("message", str(a))[:200], "severity": "medium"} for a in kb_alerts[:5]]
    except Exception:
        return []


def check_backups(backups_dir: Path | None = None) -> List[Dict[str, Any]]:
    """备份产物新鲜度（v8.0.28 新增，产物级校验）。

    动机：cron 对账只校验 lc-daily-backup job 存在性；2026-11 保留窗内
    11-14/11-16 两天实际缺 auto 包而监控全绿——job 在 ≠ 产物在。
    只认 *-auto.zip（每日自动全量），专项/partial 包不参与新鲜度。
    """
    root = backups_dir if backups_dir is not None else PROJECT_ROOT / "backups"
    if not root.exists():
        return [{"issue": "备份目录缺失: backups/", "severity": "high"}]
    auto = [p for p in root.glob("*-auto.zip") if p.is_file()]
    if not auto:
        return [{"issue": "无每日自动备份包（*-auto.zip）", "severity": "high"}]
    latest = max(auto, key=lambda p: p.stat().st_mtime)
    age_h = (datetime.now(timezone.utc).timestamp() - latest.stat().st_mtime) / 3600.0
    if age_h > BACKUP_CRITICAL_HOURS:
        sev = "high"
    elif age_h > BACKUP_WARN_HOURS:
        sev = "medium"
    else:
        return []
    return [{"issue": f"备份过期: 最新 auto 包 {latest.name} 已 {age_h:.0f} 小时未更新"
                      f"（warn {BACKUP_WARN_HOURS:.0f}h / critical {BACKUP_CRITICAL_HOURS:.0f}h）",
             "severity": sev}]


def run_monitor(dry_run: bool = False) -> Dict[str, Any]:
    issues = check_crons() + check_topics() + check_backups() + check_kb()
    report = {
        "checked_at": _now(),
        "ok": not issues,
        "issues": issues,
        "summary": "✓ 全部正常" if not issues else "；".join(i["issue"] for i in issues[:8]),
    }
    if not dry_run:
        save_json(MONITOR_STATE, report)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="工作台轻量健康检查")
    ap.add_argument("--dry-run", action="store_true", help="只检查不落盘")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        assert V8_CRON_EXPECTED and KICKOFF_STALL_DAYS > 0
        assert 0 < BACKUP_WARN_HOURS < BACKUP_CRITICAL_HOURS
        print("✓ workbench_monitor 自检通过")
        return 0
    report = run_monitor(dry_run=args.dry_run)
    print(("✓ " if report["ok"] else "⚠ ") + report["summary"])
    for i in report["issues"]:
        print(f"  [{i.get('severity', 'medium')}] {i['issue']}")
    # 退出语义（v8.0.46）：告警 ≠ 失败，恒 0——避免 hermes cron 把设计内告警
    # 记为 incident（11-18/11-19 实证 1 条污染）。告警可见性由 stdout 日志 +
    # memory/workbench-monitor.json 状态文件承担（harness_metrics 已接）；
    # incident 流只留真实崩溃（异常退出仍为非 0）。
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
