#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harness 运转指标采集（v8.0.41）——48h 主动推进期半点轮的数据入口。

动机（2026-11-20 用户指令）：主动推进的同时高效收集实际运转数据，
以高效高质量产出课题为目标，针对性优化项目框架与工作 harness。
本脚本做零 LLM、只读的六路采集，输出一个 JSON 快照 + 中文摘要，
供半点优化轮与治理会话消费；每路 fail-open，坏源不影响其他路。

采集六路：
① 课题漏斗：文件系统域计数（真相源）+ _topics.json stage 分布 +
   状态漂移对账（索引 stage 与目录位置不符即报）；
② cron 健康：hermes_bridge cron_list_profile（paused 计数）+ incidents（CLI，fail-open）；
③ step_usage 24h：调用数/成功率/token/耗时/kind 分布（月分片 JSONL，跨月窗口）；
④ 备份：最新 *-auto.zip 年龄与体积；
⑤ KB 积压：蒸馏 remaining + 方法卡回补遗留（收官后应为 0）；
⑥ git 同步：ahead/behind（远程恢复点时效）。

用法示例：
    python3 scripts/harness_metrics.py                  # 采集+落盘+摘要
    python3 scripts/harness_metrics.py --quiet          # 只落盘不打印明细
    python3 scripts/harness_metrics.py --self-check     # 自检（真实源只读）
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from common import load_json, save_json  # noqa: E402

PROJECT_ROOT = Path(__file__).parent.parent
SNAPSHOT_PATH = PROJECT_ROOT / "memory" / ".cache" / "harness-metrics-snapshot.json"
HISTORY_PATH = PROJECT_ROOT / "memory" / ".cache" / "harness-metrics-history.jsonl"
# 趋势历史行数上限（超过则滚动保留后半，防无界增长）
HISTORY_MAX_LINES = 2000

# 备份新鲜度阈值与 workbench_monitor 对齐（>30h medium，>54h high）
BACKUP_WARN_HOURS = 30.0
BACKUP_CRITICAL_HOURS = 54.0
# 蒸馏积压上限（与 AGENTS「待蒸馏 140<300（cron 管）」口径一致）
DISTILL_BACKLOG_LIMIT = 300
# step_usage 成功率告警下限（24h 内调用数 >= 5 才参与判定）
SUCCESS_RATE_FLOOR = 0.9
TOPIC_DOMAINS = ("questions", "kickoff", "ready", "active", "archive")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(ts: str) -> datetime | None:
    """解析 UTC ISO 时间戳（%Y-%m-%dT%H:%M:%SZ），失败返回 None。"""
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def collect_topics(root: Path) -> Dict[str, Any]:
    """课题漏斗：文件系统域计数（真相源）+ 索引 stage 漂移对账。"""
    rt = root / "research_topics"
    fs_counts: Dict[str, int] = {}
    for dom in TOPIC_DOMAINS:
        fs_counts[dom] = len([p for p in (rt / dom).glob("*") if p.is_dir()]) if (rt / dom).is_dir() else 0
    rejected_dir = rt / "_rejected-questions"
    fs_counts["rejected-questions"] = (
        len([p for p in rejected_dir.glob("*") if p.is_dir()]) if rejected_dir.is_dir() else 0
    )
    idx = load_json(rt / "_topics.json", default={}) or {}
    topics = idx.get("topics", {}) if isinstance(idx, dict) else {}
    stage_counts = Counter()
    needs_human: List[str] = []
    drift: List[str] = []
    ready_ages_days: List[float] = []
    now = _now_utc()
    for tid, meta in topics.items():
        if not isinstance(meta, dict):
            continue
        stage = str(meta.get("stage", "?"))
        stage_counts[stage] += 1
        if meta.get("needs_human"):
            needs_human.append(tid)
        # 状态漂移：索引 stage 应与目录位置一致（目录位置才是真相源）
        if stage in TOPIC_DOMAINS and not (rt / stage / tid).is_dir():
            drift.append(f"{tid}: 索引={stage} 目录缺失")
        if stage == "ready":
            ts = _parse_ts(str(meta.get("updated_at", "")))
            if ts:
                ready_ages_days.append((now - ts).total_seconds() / 86400.0)
    return {
        "fs_counts": fs_counts,
        "index_stage_counts": dict(stage_counts),
        "needs_human": needs_human,
        "stage_drift": drift,
        "ready_oldest_days": round(max(ready_ages_days), 2) if ready_ages_days else None,
        "ready_count": len(ready_ages_days),
    }


def collect_step_usage(usage_dir: Path, hours: float = 24.0, now: datetime | None = None) -> Dict[str, Any]:
    """step_usage 近 N 小时聚合（月分片 JSONL，跨月窗口自动兼容）。"""
    now = now or _now_utc()
    start = now - timedelta(hours=hours)
    months = sorted({start.strftime("%Y-%m"), now.strftime("%Y-%m")})
    calls = 0
    ok = 0
    failed = 0
    tokens = 0
    tokens_estimated = 0
    elapsed_s = 0.0
    by_kind: Counter = Counter()
    by_name: Counter = Counter()
    skipped = 0
    for m in months:
        shard = usage_dir / f"step-usage-{m}.jsonl"
        if not shard.is_file():
            continue
        for line in shard.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:  # noqa: BLE001
                skipped += 1
                continue
            ts = _parse_ts(str(rec.get("ts", "")))
            if ts is None or not (start <= ts <= now):
                continue
            calls += 1
            if rec.get("success"):
                ok += 1
            else:
                failed += 1
            tokens += int(rec.get("prompt_tokens") or 0) + int(rec.get("completion_tokens") or 0)
            if rec.get("tokens_estimated"):
                tokens_estimated += 1
            try:
                elapsed_s += float(rec.get("elapsed_s") or 0.0)
            except (TypeError, ValueError):
                pass
            by_kind[str(rec.get("kind", "?"))] += 1
            by_name[str(rec.get("name", "?"))] += 1
    rate = round(ok / calls, 4) if calls else None
    return {
        "window_hours": hours,
        "calls": calls,
        "success": ok,
        "failed": failed,
        "success_rate": rate,
        "tokens_total": tokens,
        "tokens_estimated_lines": tokens_estimated,
        "elapsed_s_sum": round(elapsed_s, 1),
        "by_kind": dict(by_kind.most_common()),
        "top_names": dict(by_name.most_common(5)),
        "malformed_lines_skipped": skipped,
    }


def collect_cron() -> Dict[str, Any]:
    """hermes cron 健康桥接（fail-open）。

    口径说明：bridge/CLI 列表默认隐藏 paused job，paused 精确计数读
    profile 存储（~/.hermes/profiles/linsai/cron/jobs.json，只读）；
    incidents 取 CLI 的总数与 48h 内新增（ Last seen 判定）——
    历史旧账（如 2026-09 限额 429）不算新告警。
    """
    out: Dict[str, Any] = {
        "total": None, "paused": [],
        "incidents_total": None, "incidents_recent_48h": 0, "incidents_last_seen": None,
    }
    try:
        import hermes_bridge as hb

        jobs = hb.cron_list_profile("linsai")
        out["total"] = len(jobs)
    except Exception as e:  # noqa: BLE001
        out["error"] = f"hermes_bridge 不可用: {e}"
    try:
        store = json.loads(
            (Path.home() / ".hermes" / "profiles" / "linsai" / "cron" / "jobs.json").read_text(encoding="utf-8")
        )
        items = store.get("jobs", []) if isinstance(store, dict) else []
        out["paused"] = [j.get("name") for j in items if j.get("state") == "paused"]
        if out["total"] is None:
            out["total"] = len(items)
    except Exception:  # noqa: BLE001
        pass  # 存储不可读时 paused 维持空（bridge 口径）
    try:
        r = subprocess.run(
            ["hermes", "--profile", "linsai", "cron", "incidents"],
            capture_output=True, text=True, timeout=15,
        )
        text = r.stdout or ""
        m = re.search(r"(\d+)\s+incident", text)
        if m:
            out["incidents_total"] = int(m.group(1))
        cutoff = _now_utc() - timedelta(hours=48)
        latest: datetime | None = None
        for lm in re.finditer(r"Last seen:\s*(\S+)", text):
            try:
                dt = datetime.fromisoformat(lm.group(1))
            except ValueError:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if latest is None or dt > latest:
                latest = dt
            if dt >= cutoff:
                out["incidents_recent_48h"] += 1
        if latest:
            out["incidents_last_seen"] = latest.strftime("%Y-%m-%dT%H:%M:%S%z")
    except Exception as e:  # noqa: BLE001
        out["incidents_error"] = str(e)
    return out


def collect_backup(backup_dir: Path, now: datetime | None = None) -> Dict[str, Any]:
    """最新 auto 备份包年龄与体积。"""
    now = now or _now_utc()
    if not backup_dir.is_dir():
        return {"latest": None, "issue": "backups 目录缺失"}
    zips = sorted(backup_dir.glob("*-auto.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        return {"latest": None, "issue": "无 *-auto.zip 备份包"}
    latest = zips[-1]
    age_h = (now.timestamp() - latest.stat().st_mtime) / 3600.0
    return {
        "latest": latest.name,
        "age_hours": round(age_h, 1),
        "size_mb": round(latest.stat().st_size / (1024 * 1024), 1),
        "count": len(zips),
    }


def collect_kb(root: Path) -> Dict[str, Any]:
    """KB 积压：蒸馏 remaining + 方法卡回补遗留（收官后应为 0）。"""
    out: Dict[str, Any] = {}
    dw = load_json(root / "memory" / "distill-worklist.json", default={}) or {}
    rem = dw.get("remaining") if isinstance(dw, dict) else None
    if isinstance(rem, dict):
        rem = rem.get("count", rem.get("total"))
    out["distill_remaining"] = rem if isinstance(rem, int) else None
    mw = load_json(root / "memory" / "methods-backfill-worklist.json", default={}) or {}
    pending = 0
    if isinstance(mw, dict):
        pages = mw.get("pages")
        if isinstance(pages, dict):
            pending = sum(1 for v in pages.values() if isinstance(v, dict) and v.get("status") == "pending")
        elif isinstance(mw.get("items"), list):
            pending = sum(1 for v in mw["items"] if isinstance(v, dict) and v.get("status") == "pending")
    out["methods_backfill_pending"] = pending
    return out


def collect_worklist(root: Path) -> Dict[str, Any]:
    """治理工单状态分布。"""
    wl = load_json(root / "memory" / "self-optimize" / "worklist.json", default={}) or {}
    items = wl.get("items", []) if isinstance(wl, dict) else []
    c = Counter(str(i.get("status", "?")) for i in items if isinstance(i, dict))
    return {"total": len(items), "by_status": dict(c)}


def collect_monitor_state(root: Path) -> Dict[str, Any]:
    """workbench-monitor 状态文件（monitor 告警可见性入口，v8.0.46 语义）。

    monitor 告警不再产生 hermes incident（退出码恒 0），本采集保证告警
    仍进入 metrics 快照告警推导，可见性不降级。
    """
    st = load_json(root / "memory" / "workbench-monitor.json", default={}) or {}
    if not isinstance(st, dict) or "ok" not in st:
        return {"ok": None, "issues_count": None, "high_count": 0, "checked_at": None}
    issues = [i for i in st.get("issues", []) if isinstance(i, dict)]
    high = sum(1 for i in issues if i.get("severity") == "high")
    return {
        "ok": st.get("ok"),
        "issues_count": len(issues),
        "high_count": high,
        "checked_at": st.get("checked_at"),
    }


def collect_disk(root: Path) -> Dict[str, Any]:
    """磁盘余量（GB）——2026-11-22 失控 ugrep 234GB 写爆临时区的盲区补丁。"""
    import shutil as _shutil
    try:
        usage = _shutil.disk_usage(str(root))
        return {"free_gb": round(usage.free / (1024**3), 1), "total_gb": round(usage.total / (1024**3), 1)}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def collect_git(root: Path) -> Dict[str, Any]:
    """git 远程同步状态（ahead/behind），fail-open。"""
    out: Dict[str, Any] = {}
    for key, rev in (("ahead", "origin/main..main"), ("behind", "main..origin/main")):
        try:
            r = subprocess.run(
                ["git", "rev-list", "--count", rev],
                capture_output=True, text=True, timeout=10, cwd=str(root),
            )
            out[key] = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else None
        except Exception:  # noqa: BLE001
            out[key] = None
    return out


def derive_alerts(snap: Dict[str, Any]) -> List[str]:
    """从快照推导告警（只报告，不处置）。"""
    alerts: List[str] = []
    g = snap.get("git", {})
    if isinstance(g.get("ahead"), int) and g["ahead"] > 0:
        alerts.append(f"⚠ 远程滞后 {g['ahead']} commits，建议 git push origin main")
    t = snap.get("topics", {})
    if t.get("needs_human"):
        alerts.append(f"⚠ needs_human 挂起 {len(t['needs_human'])} 项: {', '.join(t['needs_human'][:5])}")
    if t.get("stage_drift"):
        alerts.append(f"⚠ 课题状态漂移 {len(t['stage_drift'])} 项（索引 stage 与目录位置不符）")
    b = snap.get("backup", {})
    age = b.get("age_hours")
    if isinstance(age, (int, float)):
        if age > BACKUP_CRITICAL_HOURS:
            alerts.append(f"✗ 备份包已 {age}h 未更新（>{BACKUP_CRITICAL_HOURS:.0f}h，备份链疑似断裂）")
        elif age > BACKUP_WARN_HOURS:
            alerts.append(f"⚠ 备份包已 {age}h 未更新（>{BACKUP_WARN_HOURS:.0f}h，medium）")
    kb = snap.get("kb", {})
    dr = kb.get("distill_remaining")
    if isinstance(dr, int) and dr > DISTILL_BACKLOG_LIMIT:
        alerts.append(f"⚠ 蒸馏积压 {dr} > {DISTILL_BACKLOG_LIMIT}")
    mb = kb.get("methods_backfill_pending")
    if isinstance(mb, int) and mb > 0:
        alerts.append(f"⚠ 方法卡回补遗留 {mb} 页（收官口径应为 0）")
    cr = snap.get("cron", {})
    inc = cr.get("incidents_recent_48h")
    if isinstance(inc, int) and inc > 0:
        alerts.append(f"⚠ hermes cron 48h 内新 incidents {inc} 条（历史总数 {cr.get('incidents_total')}）")
    if cr.get("paused"):
        alerts.append(f"○ cron 暂停中: {', '.join(str(p) for p in cr['paused'])}")
    su = snap.get("step_usage_24h", {})
    rate = su.get("success_rate")
    if isinstance(rate, float) and su.get("calls", 0) >= 5 and rate < SUCCESS_RATE_FLOOR:
        alerts.append(f"⚠ step_usage 24h 成功率 {rate:.0%} < {SUCCESS_RATE_FLOOR:.0%}")
    dk = snap.get("disk", {})
    free = dk.get("free_gb")
    if isinstance(free, (int, float)) and free < 10:
        alerts.append(f"✗ 磁盘余量 {free}GB < 10GB（备份/抓取面临 ENOSPC，需清理）")
    elif isinstance(free, (int, float)) and free < 20:
        alerts.append(f"⚠ 磁盘余量 {free}GB < 20GB（关注）")
    ms = snap.get("monitor_state", {})
    if ms.get("ok") is False:
        hi = ms.get("high_count") or 0
        prefix = "✗" if hi else "⚠"
        alerts.append(
            f"{prefix} workbench-monitor 报告异常（issues {ms.get('issues_count')}，high {hi}，"
            f"checked {ms.get('checked_at')}）"
        )
    return alerts


def append_history(snap: Dict[str, Any], path: Path = HISTORY_PATH) -> Dict[str, Any]:
    """快照关键指标压缩为一行 JSONL 追加（有界滚动），供轮间趋势对比。

    与全量快照的关系：快照供当轮细读，历史供跨轮漂移检测
    （如 ready 最老天数持续增长 → 裁决紧迫度提示）。
    """
    t = snap.get("topics", {})
    cr = snap.get("cron", {})
    su = snap.get("step_usage_24h", {})
    b = snap.get("backup", {})
    dk = snap.get("disk", {})
    free = dk.get("free_gb")
    if isinstance(free, (int, float)) and free < 10:
        alerts.append(f"✗ 磁盘余量 {free}GB < 10GB（备份/抓取面临 ENOSPC，需清理）")
    elif isinstance(free, (int, float)) and free < 20:
        alerts.append(f"⚠ 磁盘余量 {free}GB < 20GB（关注）")
    ms = snap.get("monitor_state", {})
    row = {
        "ts": snap.get("generated_at"),
        "ready": t.get("fs_counts", {}).get("ready"),
        "ready_oldest_days": t.get("ready_oldest_days"),
        "needs_human": len(t.get("needs_human", [])),
        "incidents_48h": cr.get("incidents_recent_48h"),
        "calls_24h": su.get("calls"),
        "success_rate": su.get("success_rate"),
        "distill": snap.get("kb", {}).get("distill_remaining"),
        "backup_age_h": b.get("age_hours"),
        "monitor_ok": ms.get("ok"),
        "ahead": snap.get("git", {}).get("ahead"),
        "disk_free_gb": snap.get("disk", {}).get("free_gb"),
        "alerts_n": len(snap.get("alerts", [])),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
    lines.append(json.dumps(row, ensure_ascii=False))
    if len(lines) > HISTORY_MAX_LINES:
        lines = lines[-HISTORY_MAX_LINES // 2:]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return row


def build_snapshot(root: Path = PROJECT_ROOT) -> Dict[str, Any]:
    """六路采集合并为一份快照（每路独立 fail-open）。"""
    snap: Dict[str, Any] = {"generated_at": _now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")}
    steps = (
        ("topics", lambda: collect_topics(root)),
        ("cron", collect_cron),
        ("step_usage_24h", lambda: collect_step_usage(root / "memory" / "usage")),
        ("backup", lambda: collect_backup(root / "backups")),
        ("kb", lambda: collect_kb(root)),
        ("worklist", lambda: collect_worklist(root)),
        ("monitor_state", lambda: collect_monitor_state(root)),
        ("disk", lambda: collect_disk(root)),
        ("git", lambda: collect_git(root)),
    )
    for name, fn in steps:
        try:
            snap[name] = fn()
        except Exception as e:  # noqa: BLE001
            snap[name] = {"error": f"采集失败: {e}"}
    snap["alerts"] = derive_alerts(snap)
    return snap


def _summary(snap: Dict[str, Any]) -> str:
    """中文摘要（供半点轮直接阅读）。"""
    lines = [f"harness 运转快照 @ {snap.get('generated_at')}"]
    t = snap.get("topics", {})
    fs = t.get("fs_counts", {})
    if fs:
        lines.append(
            "① 课题漏斗(fs): " + " ".join(f"{k}={v}" for k, v in fs.items())
            + f" · ready 最老 {t.get('ready_oldest_days')}d"
        )
    cr = snap.get("cron", {})
    if cr.get("total") is not None:
        lines.append(
            f"② cron: total={cr['total']} paused={cr.get('paused') or 0}"
            + f" incidents总={cr.get('incidents_total')} 48h新增={cr.get('incidents_recent_48h')}"
        )
    su = snap.get("step_usage_24h", {})
    if su.get("calls") is not None:
        rate = su.get("success_rate")
        lines.append(
            f"③ step_usage 24h: calls={su.get('calls')} 成功率={rate if rate is None else f'{rate:.0%}'}"
            + f" tokens={su.get('tokens_total')} elapsed={su.get('elapsed_s_sum')}s"
        )
    b = snap.get("backup", {})
    if b.get("latest"):
        lines.append(f"④ 备份: {b['latest']}（{b.get('age_hours')}h 前，{b.get('size_mb')}MB）")
    kb = snap.get("kb", {})
    lines.append(f"⑤ KB: 蒸馏积压={kb.get('distill_remaining')} 方法卡遗留={kb.get('methods_backfill_pending')}")
    g = snap.get("git", {})
    dk = snap.get("disk", {})
    lines.append(f"⑥ git: ahead={g.get('ahead')} behind={g.get('behind')} · 磁盘余量 {dk.get('free_gb')}GB")
    dk = snap.get("disk", {})
    free = dk.get("free_gb")
    if isinstance(free, (int, float)) and free < 10:
        alerts.append(f"✗ 磁盘余量 {free}GB < 10GB（备份/抓取面临 ENOSPC，需清理）")
    elif isinstance(free, (int, float)) and free < 20:
        alerts.append(f"⚠ 磁盘余量 {free}GB < 20GB（关注）")
    ms = snap.get("monitor_state", {})
    if ms.get("ok") is not None:
        lines.append(f"⑦ monitor: ok={ms.get('ok')} issues={ms.get('issues_count')} high={ms.get('high_count')}")
    for a in snap.get("alerts", []):
        lines.append(a)
    if not snap.get("alerts"):
        lines.append("✓ 无告警")
    return "\n".join(lines)


def _self_check() -> int:
    """自检：真实源只读采集 + 合成快照告警推导。"""
    ok = True
    snap = build_snapshot(PROJECT_ROOT)
    for key in ("generated_at", "topics", "cron", "step_usage_24h", "backup", "kb", "worklist", "monitor_state", "disk", "git", "alerts"):
        if key not in snap:
            print(f"✗ 快照缺字段 {key}")
            ok = False
    synthetic = {"git": {"ahead": 5, "behind": 0}, "topics": {}, "backup": {}, "kb": {}, "cron": {}, "step_usage_24h": {}}
    alerts = derive_alerts(synthetic)
    if not any("push" in a for a in alerts):
        print("✗ 合成快照未推导出 push 告警")
        ok = False
    print("✓ 六路快照字段齐全" if ok else "✗ 自检未通过")
    print(_summary(snap))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="harness 运转指标采集（只读，零 LLM）")
    ap.add_argument("--quiet", action="store_true", help="只落盘不打印摘要")
    ap.add_argument("--self-check", action="store_true", help="自检模式")
    args = ap.parse_args()
    if args.self_check:
        return _self_check()
    snap = build_snapshot(PROJECT_ROOT)
    save_json(SNAPSHOT_PATH, snap)
    row = append_history(snap)
    if not args.quiet:
        print(_summary(snap))
        print(f"快照: {SNAPSHOT_PATH}")
        print(f"历史: {HISTORY_PATH}（+1 行）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
