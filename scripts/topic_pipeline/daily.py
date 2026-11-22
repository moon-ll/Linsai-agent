# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——每日深研调度（--daily，cron lc-topic-daily 入口）。

每个工作日对队首问题候选执行：深研（B1→B3）→ 组装（B4）→ 验收自检。
配额默认 1 课题/天，`memory/config/workbench.json` 可调：
    {"daily_quota": 1, "deep_research_enabled": true}

用法示例：
    python3 scripts/topic_pipeline.py --daily
    python3 scripts/topic_pipeline.py --daily --dry-run
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from common import load_json

from . import acceptance, assemble, deep_research, state
from .constants import DEFAULT_DAILY_QUOTA, PROJECT_ROOT

_CONFIG_PATH = PROJECT_ROOT / "memory" / "config" / "workbench.json"


def _config() -> Dict[str, Any]:
    return load_json(_CONFIG_PATH, default={}) or {}


def queue_head(limit: int) -> List[Dict[str, Any]]:
    """问题候选队列（questions 阶段，先到先研，needs_human 跳过）。"""
    data = state.load_state()
    out: List[Dict[str, Any]] = []
    # 1) questions 队列（先到先研）
    for tid in state.list_by_stage(data, "questions"):
        rec = state.get_topic(data, tid) or {}
        if rec.get("needs_human"):
            continue
        out.append({"topic_id": tid, "title": rec.get("title", ""), "created_at": rec.get("created_at", "")})
        if len(out) >= limit:
            return out
    # 2) kickoff 缺口续研（含 v7 迁移课题——check 记录的缺口由深研补齐流程消化）
    for tid in state.list_by_stage(data, "kickoff"):
        rec = state.get_topic(data, tid) or {}
        if rec.get("needs_human"):
            continue
        if not (rec.get("deep_dive_gaps") or rec.get("check_gaps") or []):
            continue
        out.append({"topic_id": tid, "title": rec.get("title", ""), "created_at": rec.get("created_at", "")})
        if len(out) >= limit:
            break
    return out


def run_daily(dry_run: bool = False, runner=None) -> Dict[str, Any]:
    """每日入口：取队首候选 → 深研 → 组装 → 自检。"""
    cfg = _config()
    if not cfg.get("deep_research_enabled", True):
        return {"success": True, "skipped": "deep_research_enabled=false（workbench.json）"}
    quota = int(cfg.get("daily_quota") or DEFAULT_DAILY_QUOTA)
    batch = queue_head(quota)
    if not batch:
        return {"success": True, "skipped": "问题队列为空（等待周末输入链发现）"}

    results: List[Dict[str, Any]] = []
    for item in batch:
        tid = item["topic_id"]
        dive = deep_research.deep_dive(tid, dry_run=dry_run, runner=runner)
        asm = assemble.assemble_report(tid, dry_run=dry_run)
        chk = acceptance.check_topic(tid, dry_run=dry_run) if not dive.get("gaps") else {"skipped": "深研有缺口"}
        results.append({"topic_id": tid, "title": item["title"],
                        "deep_dive": {k: v for k, v in dive.items() if k != "steps_run"},
                        "assemble": {k: v for k, v in asm.items() if k != "report"},
                        "check": {k: v for k, v in (chk or {}).items() if k != "verdict"} if isinstance(chk, dict) else chk})
    return {
        "success": True,
        "quota": quota,
        "processed": len(batch),
        "results": results,
        "summary": "；".join(
            f"{r['topic_id']}: {'✓ 全过' if (r.get('check') or {}).get('verdict', {}).get('passed') else '◐ 缺口 ' + ','.join((r.get('check') or {}).get('verdict', {}).get('gaps', []) or r.get('deep_dive', {}).get('gaps', []))}"
            for r in results),
    }
