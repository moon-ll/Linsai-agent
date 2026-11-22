#!/usr/bin/env python3
"""side-worker：并行试点第二 worker（v7.3.55，目标判据 G2-D 配套·用户裁决 2026-11-06）。

背景（memory/goals/2026-11-05-双目标判据.md §G2-D 与 11-06 02:00 巡检）：
    微调度器每 tick 至多 1 长步，全链 286 job ≈ 12-24h/扫。v7.2.50 已建
    per-proposal 锁支持跨课题并行；本模块补"第二 worker"——与主 tick
    互补消费**轮转名单上非聚焦课题**的 ready job，实现 2 并发试点。
    并发上限受配置门控（默认 disabled），配额是真实约束
    （11-01 minimax 故障日 101/105 失败）。

与主 tick 的关系（安全性设计）：
    - 完全解耦：不持有 lifecycle-micro-scheduler 全局锁，轮转/focus
      状态零写入（轮转语义归主 tick 独占）；只读 queue_full。
    - per-proposal 非阻塞 flock：主 tick 正在执行的课题直接跳过
      （不排队不堆积，下个 tick 再来）。
    - _list_ready_jobs_for_proposal 对存在 running job 的课题返回空，
      与非阻塞锁构成双保险。
    - execute_job 的状态写入全部走既有 file_lock + 原子写（BUG-12
      修复后跨进程安全）；看板不写（主 tick 下轮自然刷新）。
    - 熔断器 open 时拒派发（与主 tick 同口径）。
    - 仅工作时段内执行（复用 _current_focus_slot）。
    - 单次至多 1 个 job（试点保守口径）。

配置（memory/config/schedules/parallel-workers.json，缺失/损坏/false 一律跳过）：
    {"enabled": true, "max_jobs_per_run": 1}

用法：
    python3 scripts/proposal_lifecycle.py --side-worker
    （cron lc-side-worker：2-59/5 * * * 1-5，与主 tick 错相 2 分钟）
"""

from __future__ import annotations

from typing import Any, Dict, List

from common import file_lock, load_json
from paths import PROJECT_ROOT

# v7.2.71: 轮转双键跨模块单一真相源（与 micro_scheduler 同源）
from rotation_queue import get_rotation_queue

from .constants import JOB_STATUS_DONE, JOB_STATUS_PENDING

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None

# 配置文件路径（与 focus-slots.json 同目录，同一治理口径）
PARALLEL_CONFIG_PATH = PROJECT_ROOT / "memory" / "config" / "schedules" / "parallel-workers.json"

# 候选扫描上限：轮转名单很长时避免 side-worker tick 无谓扫描（试点口径）
_MAX_CANDIDATE_SCAN = 8


def _load_parallel_config() -> Dict[str, Any]:
    """读取并行试点配置；缺失/损坏/enabled 非 True 一律按禁用处理（fail-safe）。"""
    try:
        cfg = load_json(PARALLEL_CONFIG_PATH, default={})
    except Exception:
        return {"enabled": False}
    if not isinstance(cfg, dict) or cfg.get("enabled") is not True:
        return {"enabled": False}
    cfg.setdefault("max_jobs_per_run", 1)
    return cfg


def run_side_worker(self, max_jobs: int = 0) -> Dict[str, Any]:
    """side-worker 入口：互补消费非聚焦课题的 ready job（单 job/次）。

    Returns:
        与 run_micro_scheduler 同构的结果 dict：
        {success, executed_count, executed, skip_reason?, reason?}
    """
    # 0. 配置门控（默认禁用——试点必须显式开启）
    cfg = _load_parallel_config()
    if not cfg.get("enabled"):
        return {"success": True, "executed_count": 0, "executed": [],
                "skip_reason": "parallel_disabled",
                "reason": "parallel-workers.json 未启用并行试点"}

    # 1. 时段检查（与主 tick 同口径；非工作时段零动作）
    from .micro_scheduler import _current_focus_slot
    slot_info = _current_focus_slot()
    if slot_info is None:
        return {"success": True, "executed_count": 0, "executed": [],
                "skip_reason": "out_of_slot", "reason": "非工作时段"}

    # 2. 熔断器（与主 tick 同口径：open/probing 期间不派发）
    try:
        from circuit_breaker import allow_dispatch as cb_allow_dispatch
        if not cb_allow_dispatch():
            return {"success": True, "executed_count": 0, "executed": [],
                    "skip_reason": "circuit_open",
                    "reason": "API 熔断器 open/probing 中，side-worker 跳过派发"}
    except ImportError:
        pass
    except Exception as e:
        if _log:
            _log.warning(f"[side-worker] 熔断器状态读取异常，按正常派发: {e}")

    # 3. 自身互斥（非阻塞）+ 执行体：上一个 side-worker 尚未结束时温和退出
    try:
        with file_lock("lifecycle-side-worker", blocking=False):
            return _run_side_worker_locked(self, cfg, max_jobs)
    except TimeoutError:
        return {"success": True, "executed_count": 0, "executed": [],
                "skip_reason": "lock_busy", "reason": "上一个 side-worker 仍在执行"}


def _run_side_worker_locked(self, cfg: Dict[str, Any], max_jobs: int) -> Dict[str, Any]:
    """持锁执行体：候选选择 → 非阻塞抢 per-proposal 锁 → 执行 job。"""
    # 4. 候选名单：queue_full 全序（只读，不写轮转状态）
    focus_state = load_json(PROJECT_ROOT / "memory" / "lifecycle-focus.json", default={})
    order = get_rotation_queue(focus_state) if focus_state else []
    if not order:
        return {"success": True, "executed_count": 0, "executed": [],
                "skip_reason": "no_queue", "reason": "轮转名单为空"}

    target = max_jobs if isinstance(max_jobs, int) and max_jobs > 0 \
        else int(cfg.get("max_jobs_per_run") or 1)
    executed: List[Dict[str, Any]] = []
    scanned = 0

    for pid in order:
        if len(executed) >= target or scanned >= _MAX_CANDIDATE_SCAN:
            break
        scanned += 1

        # 5. 扫描 ready job（内部自带 running 课题短路 + 自动重试）
        try:
            ready = self._list_ready_jobs_for_proposal(pid)
        except Exception as e:
            if _log:
                _log.warning(f"[side-worker] 扫描 {pid} 失败: {e}")
            continue
        if not ready:
            continue

        item = ready[0]
        job = item["job"]

        # 6. per-proposal 非阻塞抢锁：主 tick（或其它 worker）正在该课题
        #    上执行时直接跳过——绝不排队堆积
        try:
            with file_lock(f"proposal-{pid}", blocking=False):
                _execute_side_job(self, pid, job, executed)
        except TimeoutError:
            continue
        except Exception as e:
            # 单候选故障不拖垮整个 side-worker tick（fail-soft，落账可见）
            if _log:
                _log.warning(f"[side-worker] 执行 {pid} 异常: {e}")
            executed.append({
                "proposal_id": pid,
                "job_id": job.get("job_id", ""),
                "step": job.get("step"),
                "success": False,
                "error": str(e)[:200],
                "worker": "side",
            })

    if not executed:
        return {"success": True, "executed_count": 0, "executed": [],
                "skip_reason": "no_ready_candidate",
                "reason": f"前 {scanned} 个候选均无 ready job 或锁忙"}
    return {"success": True, "executed_count": len(executed), "executed": executed,
            "worker": "side"}


def _execute_side_job(self, pid: str, job: Dict[str, Any],
                      executed: List[Dict[str, Any]]) -> None:
    """锁内执行单 job：重校验（镜像主 tick）→ execute_job → 落账。

    write_lock_held 跳过与硬故障经 SkipSideJob 异常上抛，由调用方区分处理。
    """
    jobs = self._get_jobs(pid)
    refreshed = next((j for j in jobs if j["job_id"] == job["job_id"]), None)
    if not refreshed or refreshed.get("status") != JOB_STATUS_PENDING:
        return
    done_ids = {j["job_id"] for j in jobs if j.get("status") == JOB_STATUS_DONE}
    if not all(d in done_ids for d in refreshed.get("depends_on", [])):
        return

    result = self.execute_job(refreshed)
    if result.get("skipped") == "write_lock_held":
        if _log:
            _log.warning(
                f"[side-worker] 跳过 {pid}/{refreshed.get('step')}: "
                f"{result.get('error', '')}"
            )
        return
    executed.append({
        "proposal_id": pid,
        "job_id": refreshed["job_id"],
        "step": refreshed.get("step"),
        "success": bool(result.get("success", False)),
        "error": (result.get("error") or "")[:200] or None,
        "worker": "side",
    })
    if _log:
        _log.info(
            f"[side-worker] 执行 {pid}/{refreshed.get('step')} "
            f"success={result.get('success')}"
        )
