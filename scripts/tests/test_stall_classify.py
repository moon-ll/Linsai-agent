#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v7.2.6 test_stall_classify

测试 lifecycle_monitor._classify_stall_kind 与 _check_proposal_stall 在
新分类逻辑（queue_tail / job_stuck / blocked / idle）下的行为。

覆盖场景：
  1. queue_tail：proposal 在 queue 后 1/3、无 failed → 命中 queue_tail_warn
  2. job_stuck：有 failed attempts>=MAX + finished>=24h → 命中 stalled (job_stuck)
  3. blocked：有 failed 但 attempts<MAX → 命中 stalled (blocked)
  4. idle：无 failed 无 pending 但 48h 无新 job → stalled (idle)
  5. 短时间 stalled：hours_since < 48h → 不触发任何告警
  6. queue 位置解析：queue_index / queue_total 正确性
  7. berry-mnps3-rashba 真实回归：原 queue[9] 不再误判 stalled

时间策略：
  使用明确的、远过去的 finished_at（10 天前/5 天前），跨多个周末确保
 净工时 ≥ 48h 阈值。当前是周二，5 天前是周四，跨 1 个完整周末（48h）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

import importlib.util
spec = importlib.util.spec_from_file_location(
    "lifecycle_monitor_test",
    Path(__file__).resolve().parent.parent / "lifecycle_monitor.py",
)
lm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lm)


# 固定时间锚（10 天前、5 天前），跨多周末确保 effective>=48h
_NOW = datetime.now(timezone.utc)
_T_10D_AGO = _NOW - timedelta(days=10)   # done job
_T_5D_AGO = _NOW - timedelta(days=5)    # failed job
_T_2H_AGO = _NOW - timedelta(hours=2)   # 短窗口测试


def _iso_z(dt):
    return dt.isoformat().replace("+00:00", "Z")


def make_jobs(*, n_done=10, n_pending=5, n_failed=0, failed_attempts_max=False,
              failed_finished_at=None, last_done_at=None):
    """构造一组 pipeline_jobs 样本。

    默认：done 10 天前 / failed 5 天前 / pending 无时间戳。
    """
    jobs: List[Dict[str, Any]] = []
    for i in range(n_done):
        jobs.append({
            "job_id": f"job-done-{i}",
            "status": "done",
            "finished_at": _iso_z(last_done_at or _T_10D_AGO),
        })
    for i in range(n_pending):
        jobs.append({
            "job_id": f"job-pending-{i}",
            "status": "pending",
        })
    for i in range(n_failed):
        attempts = 3 if failed_attempts_max else 1
        fin = failed_finished_at if failed_finished_at is not None else _T_5D_AGO
        jobs.append({
            "job_id": f"job-failed-{i}",
            "status": "failed",
            "attempts": attempts,
            "finished_at": _iso_z(fin),
            "last_error": "超时(1500s)" if failed_attempts_max else "API 失败",
        })
    return jobs


def make_proposal(pid, jobs, updated_at=None):
    return {
        "proposal_id": pid,
        "status": "optimizing",
        "updated_at": _iso_z(updated_at or _T_10D_AGO),
        "pipeline_jobs": jobs,
    }


def _run_check(pid, p, jobs, anomalies):
    total = len(jobs)
    done = sum(1 for j in jobs if j.get("status") == "done")
    lm._check_proposal_stall(pid, p, jobs, total, done, anomalies)


def test_queue_tail_low_priority():
    """queue_tail：proposal 在 queue 后 1/3、无 failed → 命中 queue_tail_warn，不发 stalled。"""
    pid = "test-queue-tail-low"
    jobs = make_jobs(n_done=10, n_pending=20, n_failed=0)
    p = make_proposal(pid, jobs)
    anomalies: List[Dict[str, Any]] = []

    _inject_queue_with_n_items(13, pid, pos=11)
    try:
        _run_check(pid, p, jobs, anomalies)
        kinds = [a.get("type") for a in anomalies]
        assert "stalled" not in kinds, f"queue_tail 不应触发 stalled: {kinds}"
        assert "queue_tail_warn" in kinds, f"应触发 queue_tail_warn: {kinds}"
        a = next(a for a in anomalies if a.get("type") == "queue_tail_warn")
        assert a["queue_index"] == 11, f"queue_index 应=11: {a}"
        assert a["queue_total"] == 13, f"queue_total 应=13: {a}"
        print(f"  ✓ queue_tail 触发 queue_tail_warn（queue[11/13]）")
    finally:
        _restore_queue()


def test_job_stuck_subtype():
    """job_stuck：有 failed attempts>=MAX + finished>=24h → stalled (job_stuck)。

    注意：failed_finished_at 设 5 天前确保净工时够大；同时 _classify_stall_kind
    自身的 finished>=24h 判定（job_stuck 标准）也满足。
    """
    pid = "test-job-stuck-subtype"
    jobs = make_jobs(n_done=10, n_pending=5, n_failed=1,
                      failed_attempts_max=True,
                      failed_finished_at=_T_5D_AGO)
    p = make_proposal(pid, jobs)
    anomalies: List[Dict[str, Any]] = []

    _inject_queue_with_n_items(10, pid, pos=0)
    try:
        _run_check(pid, p, jobs, anomalies)
        kinds = [a.get("type") for a in anomalies]
        assert "stalled" in kinds, f"job_stuck 应触发 stalled: {kinds}"
        a = next(a for a in anomalies if a.get("type") == "stalled")
        assert a.get("subtype") == "job_stuck", f"subtype 应=job_stuck: {a}"
        assert a["stall_detail"].get("stuck_job_id") == "job-failed-0", \
            f"stuck_job_id 应=job-failed-0: {a}"
        assert a["stall_detail"]["attempts"] == 3, f"attempts 应=3: {a}"
        print(f"  ✓ job_stuck 触发 stalled subtype=job_stuck")
    finally:
        _restore_queue()


def test_blocked_subtype():
    """blocked：有 failed 但 attempts<MAX → stalled (blocked)。

    注：blocked 判定只看是否有 failed job（不论 attempts 与 finished）。
    """
    pid = "test-blocked-subtype"
    jobs = make_jobs(n_done=10, n_pending=5, n_failed=1,
                      failed_attempts_max=False,
                      failed_finished_at=_T_5D_AGO)
    p = make_proposal(pid, jobs)
    anomalies: List[Dict[str, Any]] = []

    _inject_queue_with_n_items(10, pid, pos=0)
    try:
        _run_check(pid, p, jobs, anomalies)
        kinds = [a.get("type") for a in anomalies]
        assert "stalled" in kinds, f"blocked 应触发 stalled: {kinds}"
        a = next(a for a in anomalies if a.get("type") == "stalled")
        assert a.get("subtype") == "blocked", f"subtype 应=blocked: {a}"
        assert "blocking_jobs" in a["stall_detail"], f"应含 blocking_jobs: {a}"
        print(f"  ✓ blocked 触发 stalled subtype=blocked")
    finally:
        _restore_queue()


def test_idle_subtype():
    """idle：无 failed 无 pending 但 48h 无新 job → stalled (idle)。"""
    pid = "test-idle-subtype"
    jobs = make_jobs(n_done=20, n_pending=0, n_failed=0)
    p = make_proposal(pid, jobs)
    anomalies: List[Dict[str, Any]] = []

    _inject_queue_with_n_items(10, pid, pos=0)
    try:
        _run_check(pid, p, jobs, anomalies)
        kinds = [a.get("type") for a in anomalies]
        assert "stalled" in kinds, f"idle 应触发 stalled: {kinds}"
        a = next(a for a in anomalies if a.get("type") == "stalled")
        assert a.get("subtype") == "idle", f"subtype 应=idle: {a}"
        print(f"  ✓ idle 触发 stalled subtype=idle")
    finally:
        _restore_queue()


def test_short_window_no_alert():
    """短时间窗口（< 48h）不应触发任何告警。"""
    pid = "test-short-window"
    jobs = make_jobs(n_done=10, n_pending=5, n_failed=0, last_done_at=_T_2H_AGO)
    p = make_proposal(pid, jobs, updated_at=_T_2H_AGO)
    anomalies: List[Dict[str, Any]] = []

    _inject_queue_with_n_items(10, pid, pos=0)
    try:
        _run_check(pid, p, jobs, anomalies)
        assert len(anomalies) == 0, f"短窗口不应告警: {anomalies}"
        print(f"  ✓ 短窗口（2h）无告警")
    finally:
        _restore_queue()


def test_queue_position_parser():
    """_get_proposal_queue_position 正确返回 (index, total)。"""
    _inject_queue_with_n_items(8, "test-queue-parser", pos=3)
    try:
        idx, total = lm._get_proposal_queue_position("test-queue-parser")
        assert idx == 3, f"应=3: {idx}"
        assert total == 8, f"应=8: {total}"

        idx, total = lm._get_proposal_queue_position("not-in-queue")
        assert idx == -1, f"不在 queue 应=-1: {idx}"
        assert total in (8, 0), f"queue_total 文件模式应=8、stub 模式应=0: {total}"
        print(f"  ✓ _get_proposal_queue_position 解析正确")
    finally:
        _restore_queue()


def test_berry_mnps3_real_case():
    """真实回归：berry-mnps3-rashba 状态应归类到 queue_tail 或 blocked。"""
    from pathlib import Path as P
    import json

    pid = "general-berry-mnps3-rashba-20260816"
    lc = json.loads((P(__file__).resolve().parent.parent.parent /
                     "research_proposals" / "_lifecycle.json").read_text())
    p_real = lc["proposals"][pid]
    jobs = p_real["pipeline_jobs"]

    _pin_chain_age(1.0)
    try:
        kind, detail = lm._classify_stall_kind(pid, jobs, pending_count=20)
        print(f"  ✓ berry-mnps3-rashba 真实分类: kind={kind}, detail={detail}")
        # r6-writer 是 pending（lc-repair 清了 attempts），所以要么 queue_tail，要么 blocked
        assert kind in ("queue_tail", "blocked"), f"应=queue_tail 或 blocked: {kind}"
    finally:
        _unpin_chain()


def test_serial_chain_not_blocked():
    """v7.2.9 修复回归：正常串行链不得误判 blocked。

    场景（2026-09-30 order-parameter 实证）：0 failed job，pending 链头
    依赖已满足，后续 pending job 的依赖是前序 pending job（排队串行）。
    旧逻辑「dep not in done_ids」把它标为 blocked+missing_deps；
    修正后应为 queue_tail（等 queue 聚焦的正常轮转）。
    """
    pid = "test-serial-chain"
    now = datetime.now(timezone.utc)
    t_done = _iso_z(now - timedelta(days=10))
    jobs = [
        # 链头：依赖全部 done，可直接执行（只等聚焦）
        {"job_id": "j-head", "status": "pending",
         "depends_on": ["j-a", "j-b"]},
        # 后续：依赖链头（pending）——正常串行
        {"job_id": "j-next", "status": "pending",
         "depends_on": ["j-head"]},
        {"job_id": "j-tail", "status": "pending",
         "depends_on": ["j-next"]},
        {"job_id": "j-a", "status": "done", "finished_at": t_done},
        {"job_id": "j-b", "status": "done", "finished_at": t_done},
    ]

    _inject_queue_with_n_items(10, pid, pos=5)
    _pin_chain_age(1.0)
    try:
        kind, detail = lm._classify_stall_kind(pid, jobs, pending_count=3)
        assert kind == "queue_tail", f"串行链应=queue_tail 实得 {kind}: {detail}"
        print(f"  ✓ 串行链（0 failed + pending 依赖链）→ queue_tail（不误判 blocked）")
    finally:
        _unpin_chain()
        _restore_queue()


def test_truly_missing_dep_blocked():
    """v7.2.9 修复回归：依赖的 job 确实不存在时仍报 blocked。

    pending job 的 depends_on 指向不在 job 集合中的 ID（被清理/错位），
    该链永远无法解锁——真阻塞，应保留 blocked + missing_deps。
    """
    pid = "test-missing-dep"
    now = datetime.now(timezone.utc)
    t_done = _iso_z(now - timedelta(days=10))
    jobs = [
        {"job_id": "j-orphan", "status": "pending",
         "depends_on": ["j-vanished"]},  # 该 job 不存在于集合
        {"job_id": "j-a", "status": "done", "finished_at": t_done},
    ]

    _inject_queue_with_n_items(10, pid, pos=0)
    try:
        kind, detail = lm._classify_stall_kind(pid, jobs, pending_count=1)
        assert kind == "blocked", f"真缺失依赖应=blocked 实得 {kind}: {detail}"
        assert detail.get("missing_deps") == ["j-vanished"], f"detail 异常: {detail}"
        print(f"  ✓ 真缺失依赖（j-vanished 不存在）→ blocked + missing_deps")
    finally:
        _restore_queue()


def test_order_parameter_real_case():
    """v7.2.9 真实回归：order-parameter（0 failed + 串行 pending 链）应为 queue_tail。

    修复前实测被误标 blocked（missing_deps 含 r7-full_review-lit_read 等
    本身 pending 的正常上游）；修复后应归 queue_tail。

    v7.3.46: 活数据前提守卫——本用例前提是「0 failed 纯串行链」；管线
    自然运转会产生 failed job（2026-11-06 实测 full_review writer 3×1500s
    耗尽 → blocked，断言误报）。前提不成立时跳过（纯 fixture 场景由
    test_serial_chain_not_blocked 覆盖），保留前提成立时的活数据冒烟价值。
    """
    from pathlib import Path as P
    import json

    pid = "general-order-parameter-ultrafast-readout-20260727"
    lc = json.loads((P(__file__).resolve().parent.parent.parent /
                     "research_proposals" / "_lifecycle.json").read_text())
    p_real = lc["proposals"].get(pid)
    if not p_real:
        print(f"  ○ 跳过：{pid} 不在 lifecycle（可能已流转/归档）")
        return
    jobs = p_real.get("pipeline_jobs", [])
    n_failed = sum(1 for j in jobs if j.get("status") == "failed")
    if n_failed:
        print(f"  ○ 跳过：活数据含 {n_failed} 个 failed job（0 failed 前提不成立，"
              f"blocked 分支属预期；串行链场景由 test_serial_chain_not_blocked 覆盖）")
        return
    pending_n = sum(1 for j in jobs if j.get("status") == "pending")
    _pin_chain_age(1.0)
    try:
        kind, detail = lm._classify_stall_kind(pid, jobs, pending_count=pending_n)
        print(f"  ✓ order-parameter 真实分类: kind={kind}, detail={detail}")
        # 0 failed + 依赖均存在于 job 集合 → queue_tail（等聚焦）
        assert kind == "queue_tail", f"应=queue_tail 实得 {kind}: {detail}"
    finally:
        _unpin_chain()


_QUEUE_BACKUP = None
_FOCUS_TMPDIR = None


def _pin_chain_age(hours):
    """v7.2.55: 注入全链活动缓存（hours=年龄小时数），绕过读盘。"""
    lm._chain_activity_cache = {"age": hours}


def _unpin_chain():
    lm._chain_activity_cache = {}


def test_rotation_stall_frozen_chain():
    """v7.2.55（#8 判据虚设修复）：非队尾 + 全链冻结 ≥24h → rotation_stall 真告警。

    修复前：is_queue_tail 只写不读，queue[0] 也一律降级 queue_tail_warn
    （实测 houston 158h 净工时停滞被掩盖）。
    """
    pid = "test-rotation-stall"
    jobs = make_jobs(n_done=10, n_pending=20, n_failed=0)
    p = make_proposal(pid, jobs)
    anomalies: List[Dict[str, Any]] = []

    _inject_queue_with_n_items(10, pid, pos=0)
    _pin_chain_age(100.0)
    try:
        kind, detail = lm._classify_stall_kind(pid, jobs, pending_count=20)
        assert kind == "rotation_stall", f"queue[0]+链冻结应=rotation_stall: {kind}"
        assert detail["chain_frozen_hours"] == 100.0, f"detail 异常: {detail}"

        _run_check(pid, p, jobs, anomalies)
        kinds = [a.get("type") for a in anomalies]
        assert "stalled" in kinds, f"rotation_stall 应触发 stalled: {kinds}"
        a = next(a for a in anomalies if a.get("type") == "stalled")
        assert a.get("subtype") == "rotation_stall", f"subtype 异常: {a}"
        assert "queue_tail_warn" not in kinds, f"不应再降级 warn: {kinds}"
        print("  ✓ queue[0] + 全链冻结 100h → stalled (rotation_stall)")
    finally:
        _unpin_chain()
        _restore_queue()


def test_nontail_active_chain_queue_tail():
    """v7.2.55：非队尾 + 链上仍有活动（轮转推进中）→ queue_tail 正常等待。"""
    pid = "test-nontail-active"
    jobs = make_jobs(n_done=10, n_pending=20, n_failed=0)
    p = make_proposal(pid, jobs)
    anomalies: List[Dict[str, Any]] = []

    _inject_queue_with_n_items(10, pid, pos=5)
    _pin_chain_age(1.0)
    try:
        kind, detail = lm._classify_stall_kind(pid, jobs, pending_count=20)
        assert kind == "queue_tail", f"链活跃应=queue_tail: {kind}"
        assert detail.get("is_queue_tail") is False, f"非队尾标记: {detail}"

        _run_check(pid, p, jobs, anomalies)
        kinds = [a.get("type") for a in anomalies]
        assert "stalled" not in kinds, f"链活跃不应 stalled: {kinds}"
        assert "queue_tail_warn" in kinds, f"应 queue_tail_warn: {kinds}"
        print("  ✓ queue[5] + 链 1h 前有活动 → queue_tail_warn（正常等待）")
    finally:
        _unpin_chain()
        _restore_queue()


def test_tail_frozen_still_warn():
    """v7.2.55：队尾课题即使全链冻结也维持 queue_tail（排队优先级本就最低）。"""
    pid = "test-tail-frozen"
    jobs = make_jobs(n_done=10, n_pending=20, n_failed=0)
    p = make_proposal(pid, jobs)
    anomalies: List[Dict[str, Any]] = []

    _inject_queue_with_n_items(13, pid, pos=11)
    _pin_chain_age(100.0)
    try:
        kind, detail = lm._classify_stall_kind(pid, jobs, pending_count=20)
        assert kind == "queue_tail", f"队尾应=queue_tail: {kind}"
        assert detail.get("is_queue_tail") is True, f"队尾标记: {detail}"

        _run_check(pid, p, jobs, anomalies)
        kinds = [a.get("type") for a in anomalies]
        assert "stalled" not in kinds and "queue_tail_warn" in kinds, kinds
        print("  ✓ queue[11/13] + 链冻结 → queue_tail_warn（队尾不升级）")
    finally:
        _unpin_chain()
        _restore_queue()


def _write_fixture_whitelist(root, ids):
    """把夹具 id 登记为「已知课题」（v7.2.105 BUG-34 白名单口径）。

    monitor 读轮转名单时按 `_lifecycle.json` 的 proposals 集合过滤非法
    成员（测试夹具占位 id 等）。本套件的夹具 id（filler-N / test-xxx）
    不是真实课题 → 会被整体剔除 → queue_total 归零 → 队列位置解析
    断言失真（"应=3: -1"）。登记后过滤对本套件是恒等变换，断言意图
    （queue_full 为准 / 窗口外候补定位）完整保留。
    """
    import json as _json
    lc_dir = Path(root) / "research_proposals"
    lc_dir.mkdir(parents=True, exist_ok=True)
    (lc_dir / "_lifecycle.json").write_text(
        _json.dumps({
            "proposals": {pid: {"status": "optimizing"} for pid in ids},
            "updated_at": "2026-11-02T00:00:00Z",
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _inject_wip_window(n_window: int, n_full: int, pid, full_pos: int):
    """临时把 lifecycle-focus.json 改成 v7.2.66 的 WIP 硬窗口形态。

    v7.2.66 起 `_sync_queue` 双键维护：`queue_full` = 完整候补名单，
    `queue` = 前 MAX_ROTATION_WIP 个（WIP 硬窗口）。monitor 的队列位置
    解析必须以 `queue_full` 为准，否则窗口外候补课题会被判 blocked
    （真停滞）——见 v7.2.70 修复。
    """
    global _QUEUE_BACKUP, _FOCUS_TMPDIR
    import tempfile
    from common import save_json

    # v7.2.104 隔离化：此前直接写真实 memory/lifecycle-focus.json（写-读窗口
    # 与并行写入者竞态，全量回归偶发"应读到 queue_full 中的位置 4: -1"）。
    # 改为临时目录注入 + patch lm.PROJECT_ROOT——真实文件零接触。
    _FOCUS_TMPDIR = tempfile.mkdtemp(prefix="linsai_stall_focus_")
    focus_dir = Path(_FOCUS_TMPDIR) / "memory"
    focus_dir.mkdir(parents=True, exist_ok=True)
    focus_path = focus_dir / "lifecycle-focus.json"
    _QUEUE_BACKUP = lm.PROJECT_ROOT
    full = [f"filler-full-{i}" for i in range(n_full)]
    if 0 <= full_pos < n_full:
        full[full_pos] = pid
    focus = {"queue_full": full, "queue": full[:n_window]}
    save_json(focus_path, focus)
    # v7.2.105：夹具 id 登记为已知课题，避免被白名单过滤整体剔除
    _write_fixture_whitelist(_FOCUS_TMPDIR, set(full))
    lm.PROJECT_ROOT = Path(_FOCUS_TMPDIR)


def test_wip_window_candidate_not_blocked():
    """v7.2.70 回归：WIP 窗口外的候补课题不得被判 blocked（真停滞）。

    场景（2026-10-31 04h 实测）：v7.2.66 组合手术引入 WIP 硬窗口
    （MAX_ROTATION_WIP=3）后，monitor 的 `_get_proposal_queue_position`
    仍只读 `queue` → 7 个 optimizing 课题中 4 个候补（queue_full 内
    但超出 WIP 窗口）返回 queue_index=-1 → `_classify_stall_kind`
    分支 5 判为「不在 focus queue 中，上游调度未接管」= blocked →
    误发 stalled 真停滞告警（houston 即因此被判 120h 真停滞，
    而其 r3-references-writer 依赖已满足可立即执行）。

    断言：改读 queue_full 后，窗口外候补课题应判 queue_tail
    （排队中，非真停滞），不产生 stalled 告警。
    """
    pid = "test-wip-candidate"
    jobs = make_jobs(n_done=10, n_pending=20, n_failed=0)
    p = make_proposal(pid, jobs)
    anomalies: List[Dict[str, Any]] = []

    # WIP 窗口 = 3，完整候补名单 = 7，本课题在候补名单第 4 位（窗口外）
    _inject_wip_window(n_window=3, n_full=7, pid=pid, full_pos=4)
    _pin_chain_age(1.0)
    try:
        idx, total = lm._get_proposal_queue_position(pid)
        assert idx == 4, f"应读到 queue_full 中的位置 4: {idx}"
        assert total == 7, f"queue_total 应以 queue_full 为准 = 7: {total}"

        kind, detail = lm._classify_stall_kind(pid, jobs, pending_count=20)
        assert kind == "queue_tail", f"WIP 窗口外候补应=queue_tail: {kind}"
        assert detail.get("is_queue_tail") is False, f"非队尾标记: {detail}"

        _run_check(pid, p, jobs, anomalies)
        kinds = [a.get("type") for a in anomalies]
        assert "stalled" not in kinds, f"WIP 窗口外候补不应发 stalled: {kinds}"
        assert "queue_tail_warn" in kinds, f"应 queue_tail_warn: {kinds}"
        print("  ✓ WIP 窗口外候补（queue_full[4]/7）→ queue_tail_warn（非真停滞）")
    finally:
        _unpin_chain()
        _restore_queue()


def _inject_queue_with_n_items(n, pid, pos):
    """临时把 lifecycle-focus.json 的 queue 改成 n 个 proposal，pid 在 pos。

    v7.2.70：生产形态自 v7.2.66 起双键维护（`queue_full` = 完整候补名单，
    `queue` = 前 MAX_ROTATION_WIP 个）。monitor 的队列位置解析以
    `queue_full` 为准，故夹具必须同时写两个键，否则残留的生产
    `queue_full` 会让注入的 pid 查不到位置 → 误判 blocked。
    （与 v68 BUG-25 同族的「夹具未跟随生产形态漂移」。）
    """
    global _QUEUE_BACKUP, _FOCUS_TMPDIR
    import tempfile
    from common import save_json

    # v7.2.104 隔离化（与 _inject_wip_window 同改）：临时目录 + patch lm.PROJECT_ROOT
    _FOCUS_TMPDIR = tempfile.mkdtemp(prefix="linsai_stall_focus_")
    focus_dir = Path(_FOCUS_TMPDIR) / "memory"
    focus_dir.mkdir(parents=True, exist_ok=True)
    focus_path = focus_dir / "lifecycle-focus.json"
    _QUEUE_BACKUP = lm.PROJECT_ROOT
    new_queue = [f"filler-{i}" for i in range(n)]
    if 0 <= pos < n:
        new_queue[pos] = pid
    focus = {"queue": new_queue, "queue_full": list(new_queue)}
    save_json(focus_path, focus)
    # v7.2.105：夹具 id 登记为已知课题，避免被白名单过滤整体剔除
    _write_fixture_whitelist(_FOCUS_TMPDIR, set(new_queue))
    lm.PROJECT_ROOT = Path(_FOCUS_TMPDIR)


def _restore_queue():
    global _QUEUE_BACKUP, _FOCUS_TMPDIR
    # v7.2.104 隔离化：还原 lm.PROJECT_ROOT 并清理临时目录（真实文件零接触）
    if _QUEUE_BACKUP is not None:
        lm.PROJECT_ROOT = _QUEUE_BACKUP
        _QUEUE_BACKUP = None
    if _FOCUS_TMPDIR:
        import shutil
        shutil.rmtree(_FOCUS_TMPDIR, ignore_errors=True)
        _FOCUS_TMPDIR = None


def main():
    print("=== v7.2.6/v7.2.9/v7.2.55: 停滞分类测试 ===\n")
    test_queue_tail_low_priority()
    test_job_stuck_subtype()
    test_blocked_subtype()
    test_idle_subtype()
    test_short_window_no_alert()
    test_queue_position_parser()
    test_berry_mnps3_real_case()
    test_serial_chain_not_blocked()
    test_truly_missing_dep_blocked()
    test_order_parameter_real_case()
    test_rotation_stall_frozen_chain()
    test_nontail_active_chain_queue_tail()
    test_tail_frozen_still_warn()
    test_wip_window_candidate_not_blocked()
    print("\n✓ 全部测试通过")


if __name__ == "__main__":
    main()

# ─────────────────────────────────────────────
# v7.2.95: 纳入 self_test 主回归（healthcheck v71 焦点⑥——原为裸函数零覆盖，
# unittest 0-test 假绿）。TestSuite 风格：裸 assert 的 AssertionError 由
# execute_suite 统一捕获计数。
# ─────────────────────────────────────────────
from test_runner import TestSuite  # noqa: E402


class StallClassifyTests(TestSuite):
    """v7.2.95 纳入主回归；v7.2.96 消除文件竞态。

    隔离策略：patch `lm._get_proposal_queue_position`（读 stub，零文件竞态）+
    `_inject_queue_with_n_items` 双模式（登记给 stub 读 + 真写文件供
    test_queue_position_parser 的解析测试）。chain age 已有内存注入
    （_pin_chain_age）无需处理。teardown 全量恢复。
    """

    def __init__(self):
        super().__init__("stall 分类逻辑测试（v7.2.6 场景 1-14，三板块现代化）")
        self._qspec = {}
        self._orig_qpos = None
        self._orig_inject = None

    def setup(self):
        global _inject_queue_with_n_items
        self._qspec = {}
        self._orig_qpos = lm._get_proposal_queue_position
        self._orig_inject = _inject_queue_with_n_items
        # 读 stub：qspec 优先，未知 pid 返回 (-1, 0)
        lm._get_proposal_queue_position = (
            lambda pid, _q=self._qspec: _q.get(pid, (-1, 0)))
        # 写 stub：登记 qspec（保留文件写供 parser 场景）
        _inject_queue_with_n_items_orig = _inject_queue_with_n_items

        def _dual_inject(n, pid, pos, _orig=_inject_queue_with_n_items_orig):
            self._qspec[pid] = (pos, n)
            _orig(n, pid, pos)

        _inject_queue_with_n_items = _dual_inject  # 重绑模块全局：场景函数调用走 stub

    def teardown(self):
        global _inject_queue_with_n_items
        lm._get_proposal_queue_position = self._orig_qpos
        _inject_queue_with_n_items = self._orig_inject  # 恢复模块全局
        _restore_queue()  # 恢复 focus 文件（场景函数 finally 之外的兜底）

    def run_tests(self):
        test_queue_tail_low_priority()
        test_job_stuck_subtype()
        test_blocked_subtype()
        test_idle_subtype()
        test_short_window_no_alert()
        # parser 场景测的是 _get_proposal_queue_position 的文件读取本身——
        # 临时恢复原函数（场景自含注入/恢复），场景后重建 stub
        lm._get_proposal_queue_position = self._orig_qpos
        test_queue_position_parser()
        lm._get_proposal_queue_position = (
            lambda pid, _q=self._qspec: _q.get(pid, (-1, 0)))
        test_berry_mnps3_real_case()
        test_serial_chain_not_blocked()
        test_truly_missing_dep_blocked()
        # order-parameter 场景：原回归意图=串行 pending 链不误判 blocked；
        # 课题现已不在 focus queue（前提变化），fixture 注入非队尾位置
        self._qspec["general-order-parameter-ultrafast-readout-20260727"] = (0, 13)
        test_order_parameter_real_case()
        test_rotation_stall_frozen_chain()
        test_nontail_active_chain_queue_tail()
        test_tail_frozen_still_warn()
        # wip_window 场景同为文件读取型——同款恢复/重 patch
        lm._get_proposal_queue_position = self._orig_qpos
        test_wip_window_candidate_not_blocked()
        lm._get_proposal_queue_position = (
            lambda pid, _q=self._qspec: _q.get(pid, (-1, 0)))

