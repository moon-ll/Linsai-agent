#!/usr/bin/env python3
"""health_sensor.py — 统一健康感知层（v6.8.50 双平面架构·证据层核心）

为维持平面（lifecycle_monitor / run_repair）与优化平面（prompt_optimizer /
retrospective）提供同一份健康信号快照，消除"监控建立在 success 标记可信"
假设上的盲区。

采集信号（全部只读，零侵入）：
1. 空转检测    —— 近 2h 内 done 但耗时 <30s 的 job（正常 LLM job 需数分钟；
                 2026-08-14 实例：429 空转期 critic 13s"成功"返回错误文本）
2. API 错误    —— 近 2h 内 last_error 以 api_error: 开头的 failed job
                 （v6.8.48 起 _run_hermes 对配额耗尽/限流打此标记）
3. 分数骤降    —— score_history 末两条分差 ≥0.30（伪分数污染的典型特征：
                 0.81→0.18）
4. 监控心跳    —— system-kanban.json hourly_monitor.timestamp 的时滞
5. 熔断状态    —— memory/circuit-state.json（circuit_breaker 维护）

用法:
    python3 scripts/health_sensor.py                # 打印当前快照
    python3 scripts/health_sensor.py --self-check   # 自检
    from health_sensor import collect_snapshot
        snap = collect_snapshot()
        if snap["global"]["api_error_jobs_2h"] >= 3: ...
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc, load_json
from paths import PROJECT_ROOT

MEMORY_DIR = PROJECT_ROOT / "memory"
LIFECYCLE_PATH = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
KANBAN_PATH = MEMORY_DIR / "system-kanban.json"
CIRCUIT_PATH = MEMORY_DIR / "circuit-state.json"

# ── 阈值（供 monitor/调度侧消费，sensor 本身只采集不判断） ──────────────
IDLE_JOB_SECONDS = 30          # done 但耗时低于此值视为疑似空转
RECENT_WINDOW_HOURS = 2        # 统计窗口
SCORE_DROP_THRESHOLD = 0.30    # score_history 末两条分差告警线
MONITOR_STALE_HOURS = 2.0      # 监控心跳时滞告警线（由 repair 侧消费）


def _parse_ts(ts: str) -> Optional[datetime]:
    """解析 UTC ISO 时间戳（兼容 Z 后缀与空值）。"""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except Exception:
        return None


def _scan_proposal_jobs(jobs: List[Dict[str, Any]], now: datetime) -> Dict[str, Any]:
    """扫描单个课题的 pipeline_jobs，统计窗口内空转与 API 错误。"""
    idle_jobs: List[str] = []
    api_error_jobs: List[str] = []
    for j in jobs:
        finished = _parse_ts(j.get("finished_at", ""))
        if not finished or (now - finished).total_seconds() > RECENT_WINDOW_HOURS * 3600:
            continue
        status = j.get("status", "")
        if status == "done":
            started = _parse_ts(j.get("started_at", ""))
            if started and 0 <= (finished - started).total_seconds() < IDLE_JOB_SECONDS:
                idle_jobs.append(j.get("job_id", "?"))
        elif status == "failed" and str(j.get("last_error", "")).startswith("api_error"):
            api_error_jobs.append(j.get("job_id", "?"))
    return {"idle_jobs": idle_jobs, "api_error_jobs": api_error_jobs}


def _detect_score_drop(history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """检测 score_history 末两条的骤降（伪分数污染特征）。"""
    if len(history) < 2:
        return None
    prev, last = history[-2], history[-1]
    try:
        delta = float(prev.get("score", 1.0)) - float(last.get("score", 0.0))
    except (TypeError, ValueError):
        return None
    if delta >= SCORE_DROP_THRESHOLD:
        return {
            "round": last.get("round"),
            "focus_section": last.get("focus_section", ""),
            "prev_score": float(prev.get("score", 0.0)),
            "last_score": float(last.get("score", 0.0)),
            "delta": round(delta, 2),
            "at": last.get("at", ""),
        }
    return None


def collect_snapshot() -> Dict[str, Any]:
    """采集一次全局健康快照（只读，可随时安全调用）。

    Returns:
        {
          "generated_at": ...,
          "global": {"idle_done_jobs_2h", "api_error_jobs_2h", "score_drops", ...},
          "proposals": {pid: {"idle_jobs": [...], "api_error_jobs": [...], "score_drop": {...}}},
          "monitor_heartbeat_age_h": float | None,
          "circuit": {"state", "consecutive_api_errors", "opened_at"} | None,
        }
    """
    now = datetime.now(timezone.utc)
    lc = load_json(LIFECYCLE_PATH, default={"proposals": {}})

    proposals_out: Dict[str, Any] = {}
    total_idle = 0
    total_api_err = 0
    score_drops: List[Dict[str, Any]] = []

    for pid, p in (lc.get("proposals") or {}).items():
        if p.get("status") not in ("optimizing", "pending_review"):
            continue
        jobs = p.get("pipeline_jobs") or []
        scan = _scan_proposal_jobs(jobs, now)
        drop = _detect_score_drop(p.get("score_history") or [])
        if scan["idle_jobs"] or scan["api_error_jobs"] or drop:
            proposals_out[pid] = {**scan, "score_drop": drop}
            if drop:
                drop["proposal_id"] = pid
                score_drops.append(drop)
        total_idle += len(scan["idle_jobs"])
        total_api_err += len(scan["api_error_jobs"])

    # 监控心跳时滞
    heartbeat_age_h: Optional[float] = None
    kanban = load_json(KANBAN_PATH, default={})
    hm_ts = _parse_ts((kanban.get("hourly_monitor") or {}).get("timestamp", ""))
    if hm_ts:
        heartbeat_age_h = round((now - hm_ts).total_seconds() / 3600, 2)

    # 熔断状态
    circuit = load_json(CIRCUIT_PATH, default=None)
    circuit_summary = None
    if isinstance(circuit, dict) and circuit.get("state"):
        circuit_summary = {
            "state": circuit.get("state"),
            "consecutive_api_errors": circuit.get("consecutive_api_errors", 0),
            "opened_at": circuit.get("opened_at", ""),
        }

    return {
        "generated_at": now_utc(),
        "global": {
            "idle_done_jobs_2h": total_idle,
            "api_error_jobs_2h": total_api_err,
            "score_drops": score_drops,
            "monitored_proposals": len(proposals_out),
        },
        "proposals": proposals_out,
        "monitor_heartbeat_age_h": heartbeat_age_h,
        "circuit": circuit_summary,
    }


def evaluate_risks(snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    """把快照翻译为告警条目（维持平面消费；阈值在此集中管理）。

    Returns:
        [{"type": "api_idle_spin" | "api_error_burst" | "score_drop" | "circuit_open",
          "level": "high"|"medium", "message": str, ...}]
    """
    risks: List[Dict[str, Any]] = []
    g = snapshot.get("global", {})

    # 1. 空转检测：窗口内 ≥3 个短时长 done job 视为系统性空转
    idle_n = g.get("idle_done_jobs_2h", 0)
    if idle_n >= 3:
        risks.append({
            "type": "api_idle_spin",
            "level": "high",
            "message": f"近 {RECENT_WINDOW_HOURS}h 内 {idle_n} 个 job 疑似 API 空转"
                       f"（done 但耗时 <{IDLE_JOB_SECONDS}s），检查配额/网关",
        })

    # 2. API 错误爆发
    err_n = g.get("api_error_jobs_2h", 0)
    if err_n >= 2:
        risks.append({
            "type": "api_error_burst",
            "level": "high",
            "message": f"近 {RECENT_WINDOW_HOURS}h 内 {err_n} 个 job 因 API 错误失败"
                       f"（429/配额耗尽），熔断器应已介入",
        })

    # 3. 分数骤降（伪分数污染特征）
    for d in g.get("score_drops", []) or []:
        risks.append({
            "type": "score_drop",
            "level": "high",
            "proposal_id": d.get("proposal_id", ""),
            "message": f"课题 {d.get('proposal_id', '')[:30]} 分数骤降 "
                       f"{d.get('prev_score')}→{d.get('last_score')}"
                       f"（r{d.get('round')} {d.get('focus_section', '')}），疑似伪分数污染",
        })

    # 4. 熔断器开启（信息级，说明防御在工作）
    circuit = snapshot.get("circuit")
    if circuit and circuit.get("state") in ("open", "probing"):
        risks.append({
            "type": "circuit_open",
            "level": "medium",
            "message": f"API 熔断器处于 {circuit.get('state')} 状态"
                       f"（连续 API 错误 {circuit.get('consecutive_api_errors')} 次，"
                       f"开启于 {circuit.get('opened_at', '?')[:19]}），调度暂停中",
        })

    return risks


def _self_check() -> None:
    """自检：快照结构 + 风险评估函数行为。"""
    print("=== health_sensor 自检 ===")
    snap = collect_snapshot()
    assert "generated_at" in snap, "快照缺少 generated_at"
    for key in ("idle_done_jobs_2h", "api_error_jobs_2h", "score_drops"):
        assert key in snap["global"], f"global 缺少 {key}"
    assert isinstance(snap["proposals"], dict), "proposals 应为 dict"
    assert snap["monitor_heartbeat_age_h"] is None or snap["monitor_heartbeat_age_h"] >= 0, \
        "心跳时滞应为非负数或 None"
    print(f"✓ 快照结构完整（监控课题 {snap['global']['monitored_proposals']} 个）")

    # 单元级：分数骤降检测
    assert _detect_score_drop([
        {"score": 0.81, "round": 3}, {"score": 0.18, "round": 4}
    ]) is not None, "0.81→0.18 应检出骤降"
    assert _detect_score_drop([
        {"score": 0.76, "round": 1}, {"score": 0.86, "round": 2}
    ]) is None, "上升不应检出"
    assert _detect_score_drop([{"score": 0.8}]) is None, "单条历史不应检出"
    print("✓ 分数骤降检测 3 用例通过")

    # 单元级：风险评估
    fake = {"global": {"idle_done_jobs_2h": 4, "api_error_jobs_2h": 0, "score_drops": []},
            "circuit": {"state": "open", "consecutive_api_errors": 3, "opened_at": "now"}}
    risks = evaluate_risks(fake)
    types = {r["type"] for r in risks}
    assert "api_idle_spin" in types and "circuit_open" in types, f"应检出空转与熔断: {types}"
    print("✓ 风险评估 2 用例通过")
    print("✓ health_sensor: 自检全部通过")


def main() -> None:
    parser = argparse.ArgumentParser(description="统一健康感知层")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    parser.add_argument("--risks", action="store_true", help="同时输出风险评估")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return

    snap = collect_snapshot()
    if args.risks:
        snap["risks"] = evaluate_risks(snap)
    print(json.dumps(snap, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
