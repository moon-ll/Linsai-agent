#!/usr/bin/env python3
"""circuit_breaker.py — API 配额熔断器（v6.8.50 双平面架构·维持平面防御层）

背景：2026-08-14 MiniMax Token Plan 耗尽期间，微调度器持续派发 job、
hermes 持续 429 空转三小时（v6.8.48 已让这类 job 标记 success=False +
error=api_error:*）。本模块在此之上止血：连续 API 错误达到阈值后暂停派发，
冷却期后半开试探，成功才恢复——避免下一次配额耗尽再空烧数小时。

状态机（经典三态）：
    closed（正常派发）
      └─ 连续 API_FAILURE_THRESHOLD 个 api_error → open
    open（拒绝派发）
      └─ 冷却 OPEN_COOLDOWN_S 后 → probing（半开）
    probing（放行 1 个 job 试探）
      ├─ 成功 → closed（计数清零）
      └─ api_error → open（重新计时）

状态文件：memory/circuit-state.json（fcntl 锁保护，原子写入）

用法:
    python3 scripts/circuit_breaker.py --status     # 查看状态
    python3 scripts/circuit_breaker.py --self-check # 自检

    # 微调度器集成（lifecycle/micro_scheduler.py）：
    from circuit_breaker import allow_dispatch, record_job_result
    if not allow_dispatch():
        break  # 熔断中，本 cron 周期不派发
    result = self.execute_job(job)
    record_job_result(result.get("success", False), result.get("error", ""))
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from common import now_utc, load_json, save_json, file_lock
from paths import PROJECT_ROOT

MEMORY_DIR = PROJECT_ROOT / "memory"
STATE_PATH = MEMORY_DIR / "circuit-state.json"
LOCK_NAME = "circuit-breaker"

# ── 参数 ────────────────────────────────────────────────────────────────
API_FAILURE_THRESHOLD = 3       # 连续 api_error 达到此数 → 熔断
OPEN_COOLDOWN_S = 3600          # open → probing 冷却时间（1h）
HISTORY_LIMIT = 20              # 状态变迁历史保留条数


def _default_state() -> Dict[str, Any]:
    return {
        "state": "closed",
        "consecutive_api_errors": 0,
        "opened_at": "",
        "last_transition_at": now_utc(),
        "last_probe_result": "",
        "history": [],
    }


def _load() -> Dict[str, Any]:
    st = load_json(STATE_PATH, default=None)
    if not isinstance(st, dict) or not st.get("state"):
        return _default_state()
    return st


def _save(st: Dict[str, Any]) -> None:
    save_json(STATE_PATH, st)


def _append_history(st: Dict[str, Any], event: str, detail: str = "") -> None:
    st.setdefault("history", []).append({
        "at": now_utc(), "event": event, "detail": detail[:200],
    })
    st["history"] = st["history"][-HISTORY_LIMIT:]


def _age_seconds(opened_at: str) -> float:
    """open 状态已持续的秒数。"""
    if not opened_at:
        return 0.0
    try:
        t = datetime.fromisoformat(opened_at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - t).total_seconds()
    except Exception:
        return 0.0


def get_state() -> Dict[str, Any]:
    """读取当前熔断状态（只读）。"""
    return _load()


def allow_dispatch() -> bool:
    """调度前询问：当前是否允许派发 job。

    closed → True；open 且未过冷却 → False；
    open 且已过冷却 → 切换为 probing 并放行一次（True）；
    probing → False（一次试探只放行一个 job，防并发全部涌入）。
    """
    with file_lock(LOCK_NAME):
        st = _load()
        state = st.get("state", "closed")
        if state == "closed":
            return True
        if state == "open":
            if _age_seconds(st.get("opened_at", "")) >= OPEN_COOLDOWN_S:
                st["state"] = "probing"
                st["last_transition_at"] = now_utc()
                _append_history(st, "open->probing", "冷却结束，放行试探 job")
                _save(st)
                return True
            return False
        # probing：本试探 job 已放行，其余拒绝
        return False


def record_job_result(success: bool, error: str = "") -> Dict[str, Any]:
    """job 执行后回报结果，驱动状态机迁移。

    Args:
        success: job 是否成功
        error: 失败时的 error 字段（api_error:* 为 API 错误标记）

    Returns:
        迁移后的状态摘要（供调用方记日志）
    """
    is_api_error = str(error or "").startswith("api_error")
    with file_lock(LOCK_NAME):
        st = _load()
        state = st.get("state", "closed")

        if success:
            if state in ("probing", "open"):
                st["state"] = "closed"
                st["opened_at"] = ""
                st["last_probe_result"] = "ok"
                _append_history(st, f"{state}->closed", "试探成功，恢复派发")
            st["consecutive_api_errors"] = 0
        elif is_api_error:
            st["consecutive_api_errors"] = st.get("consecutive_api_errors", 0) + 1
            if state == "probing":
                st["state"] = "open"
                st["opened_at"] = now_utc()
                st["last_probe_result"] = "api_error"
                _append_history(st, "probing->open", f"试探失败({error[:80]})，重新熔断")
            elif state == "closed" and st["consecutive_api_errors"] >= API_FAILURE_THRESHOLD:
                st["state"] = "open"
                st["opened_at"] = now_utc()
                _append_history(st, "closed->open",
                                f"连续 {st['consecutive_api_errors']} 次 API 错误，暂停派发")
        else:
            # 非 API 类失败（如超时/解析错误）不触发熔断，交给既有重试机制
            pass

        _save(st)
        return {
            "state": st["state"],
            "consecutive_api_errors": st["consecutive_api_errors"],
        }


def force_reset() -> Dict[str, Any]:
    """手动复位为 closed（人工确认配额已恢复时使用）。"""
    with file_lock(LOCK_NAME):
        st = _load()
        st["state"] = "closed"
        st["consecutive_api_errors"] = 0
        st["opened_at"] = ""
        _append_history(st, "manual-reset", "人工复位")
        _save(st)
        return {"state": st["state"]}


def _self_check() -> None:
    """自检：状态机全路径（在临时状态文件上运行，不污染真实状态）。"""
    global STATE_PATH
    import tempfile
    from pathlib import Path
    print("=== circuit_breaker 自检 ===")
    real_path = STATE_PATH
    with tempfile.TemporaryDirectory() as td:
        STATE_PATH = Path(td) / "circuit-state.json"

        # 路径1：closed 正常派发
        assert allow_dispatch() is True, "closed 应允许派发"
        print("✓ closed 状态允许派发")

        # 路径2：连续 API 错误 → open
        for i in range(API_FAILURE_THRESHOLD):
            r = record_job_result(False, "api_error:HTTP 429")
        assert r["state"] == "open", f"连续 {API_FAILURE_THRESHOLD} 次应熔断: {r}"
        assert allow_dispatch() is False, "open 冷却期内应拒绝派发"
        print(f"✓ 连续 {API_FAILURE_THRESHOLD} 次 api_error → open，派发被拒")

        # 路径3：非 API 错误不计入熔断
        STATE_PATH = Path(td) / "s2.json"
        record_job_result(False, "timeout: 300s")
        r = record_job_result(False, "parse_error")
        assert r["consecutive_api_errors"] == 0, "非 API 错误不应计入"
        print("✓ 非 API 错误（超时/解析）不触发熔断")

        # 路径4：冷却后 half-open 试探 + 成功恢复
        STATE_PATH = Path(td) / "s3.json"
        for _ in range(API_FAILURE_THRESHOLD):
            record_job_result(False, "api_error:quota")
        st = _load()
        st["opened_at"] = (datetime.now(timezone.utc) - timedelta(seconds=OPEN_COOLDOWN_S + 60)).strftime("%Y-%m-%dT%H:%M:%SZ")
        _save(st)
        assert allow_dispatch() is True, "冷却期满应放行试探"
        assert allow_dispatch() is False, "probing 只放行一个"
        r = record_job_result(True)
        assert r["state"] == "closed", "试探成功应恢复 closed"
        print("✓ 冷却→probing→试探成功→closed 全链路")

        # 路径5：试探失败重新熔断
        STATE_PATH = Path(td) / "s4.json"
        for _ in range(API_FAILURE_THRESHOLD):
            record_job_result(False, "api_error:quota")
        st = _load()
        st["opened_at"] = (datetime.now(timezone.utc) - timedelta(seconds=OPEN_COOLDOWN_S + 60)).strftime("%Y-%m-%dT%H:%M:%SZ")
        _save(st)
        assert allow_dispatch() is True
        r = record_job_result(False, "api_error:still-quota")
        assert r["state"] == "open", "试探失败应回 open"
        print("✓ 试探失败→重新熔断")

    STATE_PATH = real_path
    print("✓ circuit_breaker: 自检全部通过（临时目录，零污染）")


def main() -> None:
    parser = argparse.ArgumentParser(description="API 配额熔断器")
    parser.add_argument("--status", action="store_true", help="查看当前状态")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    parser.add_argument("--reset", action="store_true", help="人工复位为 closed")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return
    if args.reset:
        print(json.dumps(force_reset(), ensure_ascii=False))
        return
    # 默认打印状态
    print(json.dumps(get_state(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
