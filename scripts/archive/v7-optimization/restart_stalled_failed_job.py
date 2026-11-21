#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v7.2.5: restart_stalled_failed_job

聚焦工具：处理"attempts 用尽 + 看板 pending + controller 未触发"的卡死场景。

实战回归：2026-09-25 11:45 / 12:15 berry-mnps3-rashba r6-rationale-writer 两次
1500s 超时，attempts=3 用尽。但 controller 的自动重试/复活逻辑都把这种状态当
"修复系统已放弃"——结果：
  - 看板 next_job=writer/rationale（仍指向 r6-writer）
  - jobs=5/25, pending=20（含 r6-writer + 后续 20 个被阻塞的 pending）
  - 5 天未触发（2026-09-25 12:15 → 2026-09-29 22:30）
  - 监控只能告警，不能自愈

本工具提供手动 "force_restart"：
  1. 找出 attempts=3 + status=failed + finished_at 已超 24h 的 job
  2. attempts 重置 0、status→pending、repair_attempts 不动
  3. 写入修复标记（manual_force_restart_at + reason），便于审计

设计原则：
  - 只针对 attempts>=MAX 且 finished_at 已超 24h 的 job（避免反复触发）
  - 每个 job 至多 manual_force_restart 一次（防止坏输入导致无限重试）
  - 默认 dry-run，先列出待解锁 job，再 --apply 执行

用法：
  python3 scripts/restart_stalled_failed_job.py --dry-run
  python3 scripts/restart_stalled_failed_job.py --apply --proposal <id> --reason 'xxx'
  python3 scripts/restart_stalled_failed_job.py --apply-all
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# 确保能 import 项目内模块（脚本位于 scripts/ 下）
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import file_lock, now_utc, save_json  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LIFECYCLE_JSON = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"

MAX_JOB_ATTEMPTS = 3
MIN_FINISHED_AGE_HOURS = 24.0  # 距 finished_at 至少 24h 才允许（给根因留修复窗口）
OUTPUT_LOG = PROJECT_ROOT / "memory" / "stalled-job-restart.json"


def _dt(s: str) -> Optional[datetime]:
    if not s or not isinstance(s, str):
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def scan_stalled_failed_jobs(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """扫描所有卡死的 failed job（attempts 用尽 + 已 finished 超 24h）。

    返回按 proposal 分组的 list，每项含 proposal_id + job_id + 失败原因等元信息。
    """
    proposals = state.get("proposals", {})
    stalled = []
    now = datetime.now(timezone.utc)

    for pid, p_state in proposals.items():
        if p_state.get("status") != "optimizing":
            continue
        jobs = p_state.get("pipeline_jobs", []) or []
        for job in jobs:
            if job.get("status") != "failed":
                continue
            attempts = int(job.get("attempts", 0))
            if attempts < MAX_JOB_ATTEMPTS:
                continue
            finished = str(job.get("finished_at") or "")
            fin_dt = _dt(finished)
            if not fin_dt:
                continue
            age_h = (now - fin_dt).total_seconds() / 3600.0
            if age_h < MIN_FINISHED_AGE_HOURS:
                continue
            # 已 manual_force_restart 过的跳过
            if int(job.get("manual_force_restart_count", 0)) >= 1:
                continue

            stalled.append({
                "proposal_id": pid,
                "job_id": job.get("job_id"),
                "attempts": attempts,
                "repair_attempts": int(job.get("repair_attempts", 0)),
                "finished_at": finished,
                "finished_age_hours": round(age_h, 1),
                "last_error": (job.get("last_error") or "")[:200],
                "current_round": job.get("round"),
                "current_step": job.get("step"),
            })
    return stalled


def apply_restart(state: Dict[str, Any], target_pid: str, reason: str = "manual") -> Dict[str, Any]:
    """手动重置指定 proposal 的 stalled failed job。

    仅重置 attempts 已达 MAX + finished_at 超 24h + 未 manual_force_restart 过的 job。
    重置后 attempts=0, status=pending, error_history 保留（溯源）。
    """
    proposals = state.get("proposals", {})
    if target_pid not in proposals:
        return {"success": False, "error": f"proposal 未注册: {target_pid}"}

    p_state = proposals[target_pid]
    if p_state.get("status") != "optimizing":
        return {"success": False, "error": f"proposal 非 optimizing 状态: {p_state.get('status')}"}

    jobs = p_state.get("pipeline_jobs", []) or []
    now = datetime.now(timezone.utc)
    restarted: List[str] = []
    skipped: List[Dict[str, Any]] = []

    for job in jobs:
        if job.get("status") != "failed":
            continue
        attempts = int(job.get("attempts", 0))
        if attempts < MAX_JOB_ATTEMPTS:
            continue
        finished = str(job.get("finished_at") or "")
        fin_dt = _dt(finished)
        if not fin_dt:
            continue
        age_h = (now - fin_dt).total_seconds() / 3600.0
        if age_h < MIN_FINISHED_AGE_HOURS:
            skipped.append({
                "job_id": job.get("job_id"),
                "reason": f"finished 仅 {age_h:.1f}h，未到 {MIN_FINISHED_AGE_HOURS}h 门槛",
            })
            continue
        if int(job.get("manual_force_restart_count", 0)) >= 1:
            skipped.append({
                "job_id": job.get("job_id"),
                "reason": "已 manual_force_restart 过一次，本工具每 job 仅 1 次",
            })
            continue

        # 实际重置
        job["status"] = "pending"
        job["attempts"] = 0
        job["manual_force_restart_count"] = int(job.get("manual_force_restart_count", 0)) + 1
        job["manual_force_restart_at"] = now_utc()
        job["manual_force_restart_reason"] = reason[:200]
        # last_error 不清（保留溯源），started_at / finished_at 清空
        job["started_at"] = ""
        job["finished_at"] = ""
        restarted.append(job.get("job_id"))

    if not restarted:
        return {
            "success": True,
            "proposal_id": target_pid,
            "restarted": [],
            "skipped": skipped,
            "message": "无符合门槛的 stalled failed job",
        }

    p_state["pipeline_jobs"] = jobs
    p_state["updated_at"] = now_utc()
    proposals[target_pid] = p_state

    return {
        "success": True,
        "proposal_id": target_pid,
        "restarted": restarted,
        "skipped": skipped,
    }


def persist_state(
    state: Dict[str, Any],
    restarted_by_pid: Optional[Dict[str, List[str]]] = None,
) -> bool:
    """原子写入 _lifecycle.json（通过 common.save_json）。

    v7.2.50（BUG-17）：改为**锁内读-改-写**。
    旧实现「无锁读全量 state → 改一个 proposal 的 pipeline_jobs →
    无锁写回全量 state」，与并发写者（`_save_jobs` / `_set_proposal_state`）
    交叉时把对方的写入整份覆盖 → job 终态丢失（回退 pending → 被重复
    执行，整轮 LLM 重跑）。与 BUG-12/15/16 同根因，本工具是
    `_lifecycle.json` 上最后一条未纳入锁的写路径。

    v7.2.51（BUG-18）：锁内重读本身还不够 —— 旧版把**快照里的全部 job**
    合并回磁盘，等于用锁外旧快照覆盖并发写者刚写入的 job 终态
    （实测：worker 把 J2 跑成 done，本工具落盘后 J2 回退 pending）。
    现只把**本工具本次真正改动过的 job**（`restarted_by_pid` 记录的
    job_id）合并回去，其余 job 一律保持磁盘版。
    并追加终态守卫：磁盘上该 job 已不是 failed（worker 已接管/完成）
    时不再回写，避免把已完成 job 打回 pending 造成 LLM 重跑。
    """
    try:
        with file_lock("proposal-lifecycle"):
            # 锁内重读：基于最新磁盘状态重新施加本工具的改动，
            # 避免用调用方持有的旧快照覆盖并发写者。
            fresh = json.loads(LIFECYCLE_JSON.read_text(encoding="utf-8"))
            fresh_props = fresh.get("proposals", {})
            for pid, p_state in (state.get("proposals") or {}).items():
                if pid not in fresh_props:
                    continue
                # 只把本工具真正改动过的 job 合并回去，其余字段保持磁盘版
                jobs_new = p_state.get("pipeline_jobs")
                jobs_old = fresh_props[pid].get("pipeline_jobs")
                if jobs_new is None or jobs_old is None:
                    continue
                # v7.2.51：白名单 —— 本次真正改动过的 job_id
                allowed = set((restarted_by_pid or {}).get(pid) or [])
                old_by_id = {}
                if isinstance(jobs_old, dict):
                    old_by_id = dict(jobs_old)
                else:
                    old_by_id = {j.get("job_id"): j for j in jobs_old if isinstance(j, dict)}
                changed = []
                if isinstance(jobs_new, dict):
                    changed = list(jobs_new.values())
                else:
                    changed = [j for j in jobs_new if isinstance(j, dict)]
                for job in changed:
                    jid = job.get("job_id")
                    if not jid or jid not in old_by_id:
                        continue
                    # 未被本工具改动的 job → 保持磁盘版，不回写旧快照
                    if jid not in allowed:
                        continue
                    # 终态守卫：磁盘上该 job 已不是 failed，说明 worker
                    # 已接管或完成，不得再打回 pending（否则 LLM 重跑）
                    if old_by_id[jid].get("status") != "failed":
                        continue
                    old_by_id[jid] = job
                if isinstance(jobs_old, dict):
                    fresh_props[pid]["pipeline_jobs"] = old_by_id
                else:
                    order = [j.get("job_id") for j in jobs_old if isinstance(j, dict)]
                    fresh_props[pid]["pipeline_jobs"] = [
                        old_by_id.get(jid, {}) for jid in order
                    ]
            save_json(LIFECYCLE_JSON, fresh)
        return True
    except Exception as e:
        print(f"✗ 写入失败: {e}")
        return False


def log_action(records: List[Dict[str, Any]]) -> None:
    OUTPUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "log_version": 1,
        "updated_at": now_utc(),
        "records": records,
    }
    OUTPUT_LOG.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_dry_run() -> int:
    """扫描并打印所有 stalled failed job（不修改）。"""
    if not LIFECYCLE_JSON.exists():
        print(f"✗ _lifecycle.json 不存在: {LIFECYCLE_JSON}")
        return 1
    state = json.loads(LIFECYCLE_JSON.read_text(encoding="utf-8"))
    stalled = scan_stalled_failed_jobs(state)
    if not stalled:
        print("✓ 当前无 stalled failed job（attempts=3 + finished>24h）")
        return 0

    print(f"=== 检测到 {len(stalled)} 个 stalled failed job ===")
    print(f"{'课题':45s} {'job_id':55s} {'attempts':>8s} {'age_h':>5s}  失败原因")
    print("-" * 130)
    for s in stalled:
        short = s["proposal_id"].replace("general-", "").replace("-20260726", "").replace("-20260727", "").replace("-20260816", "").replace("-20260822", "").replace("-20260905", "").replace("-20260920", "")
        jid = (s["job_id"] or "(no job_id)")[-55:]
        err = s["last_error"][:60]
        print(f"{short:45s} {jid:55s} {s['attempts']:>8d} {s['finished_age_hours']:>5.1f}  {err}")

    print()
    print("建议：")
    print("  - 单个 proposal: --apply --proposal <id> --reason 'xxx'")
    print("  - 全部 eligible: --apply-all")
    return 0


def cmd_apply(proposal_id: str, reason: str) -> int:
    """处理指定 proposal 的 stalled failed job。"""
    if not LIFECYCLE_JSON.exists():
        print(f"✗ _lifecycle.json 不存在: {LIFECYCLE_JSON}")
        return 1
    state = json.loads(LIFECYCLE_JSON.read_text(encoding="utf-8"))
    result = apply_restart(state, proposal_id, reason=reason)
    if not result.get("success"):
        print(f"✗ {result.get('error')}")
        return 1
    restarted = result.get("restarted", [])
    if not restarted:
        print(f"○ {proposal_id}: {result.get('message')}")
        for sk in result.get("skipped", []):
            print(f"   跳过 {sk['job_id'][-50:]}: {sk['reason']}")
        return 0
    if not persist_state(state, {proposal_id: restarted}):
        return 1
    log_action([{
        "proposal_id": proposal_id,
        "restarted": restarted,
        "skipped": result.get("skipped", []),
        "reason": reason,
        "at": now_utc(),
    }])
    print(f"✓ {proposal_id}: 重启 {len(restarted)} 个 stalled job")
    for jid in restarted:
        print(f"  ✓ {jid}")
    for sk in result.get("skipped", []):
        print(f"  ○ 跳过 {sk['job_id']}: {sk['reason']}")
    return 0


def cmd_apply_all(reason: str) -> int:
    """处理所有 eligible 的 stalled failed job。"""
    if not LIFECYCLE_JSON.exists():
        print(f"✗ _lifecycle.json 不存在: {LIFECYCLE_JSON}")
        return 1
    state = json.loads(LIFECYCLE_JSON.read_text(encoding="utf-8"))
    stalled = scan_stalled_failed_jobs(state)
    if not stalled:
        print("✓ 无 stalled failed job")
        return 0

    # 按 proposal 分组
    by_pid: Dict[str, List[Dict[str, Any]]] = {}
    for s in stalled:
        by_pid.setdefault(s["proposal_id"], []).append(s)

    all_records = []
    restarted_by_pid: Dict[str, List[str]] = {}
    for pid in by_pid:
        result = apply_restart(state, pid, reason=reason)
        if not result.get("success"):
            print(f"✗ {pid}: {result.get('error')}")
            continue
        restarted = result.get("restarted", [])
        restarted_by_pid[pid] = restarted
        all_records.append({
            "proposal_id": pid,
            "restarted": restarted,
            "skipped": result.get("skipped", []),
            "reason": reason,
            "at": now_utc(),
        })
        if result.get("restarted"):
            print(f"✓ {pid}: 重启 {len(result['restarted'])} 个 stalled job")
        for sk in result.get("skipped", []):
            print(f"  ○ {pid} 跳过 {sk['job_id']}: {sk['reason']}")

    if not persist_state(state, restarted_by_pid):
        return 1
    log_action(all_records)
    return 0


def main():
    parser = argparse.ArgumentParser(description="v7.2.5: 重启 stalled failed job")
    sub = parser.add_subparsers(dest="cmd")

    p_dry = sub.add_parser("dry-run", help="只扫描，不修改")
    p_dry.set_defaults(func=lambda a: cmd_dry_run())

    p_apply = sub.add_parser("apply", help="重启指定 proposal 的 stalled failed job")
    p_apply.add_argument("--proposal", required=True, help="proposal_id")
    p_apply.add_argument("--reason", default="manual_force_restart", help="重启原因")
    p_apply.set_defaults(func=lambda a: cmd_apply(a.proposal, a.reason))

    p_all = sub.add_parser("apply-all", help="重启所有 eligible 的 stalled failed job")
    p_all.add_argument("--reason", default="manual_force_restart_batch", help="重启原因")
    p_all.set_defaults(func=lambda a: cmd_apply_all(a.reason))

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())