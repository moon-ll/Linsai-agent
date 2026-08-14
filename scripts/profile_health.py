#!/usr/bin/env python3
"""profile_health.py — 单 profile 健康度计算（v6.7 林赛总控能力·子模块）

计算每个 hermes profile 的实时健康度：
- 状态：idle / working / blocked / offline
- 最近 24h 成功率
- 平均耗时
- 最近错误
- 自动建议

数据源：
- hermes_bridge.list_team_profiles() — 状态
- logs/linsai.log — 历史派活记录
- proposal_lifecycle._lifecycle.json — cron 失败记录

用法:
    from profile_health import compute_profile_health
    result = compute_profile_health(window_hours=24)
    for profile, health in result['profiles'].items():
        print(profile, health['status'], health['success_rate_24h'])
"""

from __future__ import annotations

import json
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc, load_json, clean_subprocess_env
from paths import PROJECT_ROOT, LOGS_DIR
from hermes_bridge import list_team_profiles

# 团队 profile 列表
TEAM_PROFILE_NAMES = ["linsai", "pipeline-runner", "researcher", "analyst", "writer", "critic", "reviewer"]


def _parse_log_records(window_hours: int = 24) -> List[Dict[str, Any]]:
    """从 linsai.log 解析最近 N 小时的派活记录。

    匹配 proposal_lifecycle v6.7.1 日志格式：
    - [timestamp] [INFO] [linsai.proposal_lifecycle] [proposal_id] 对抗轮 N: critic 评审...
    - [timestamp] [INFO] [linsai.proposal_lifecycle] 对抗轮 N: critic 完成 success=X elapsed=Ns

    每条记录包含：{at, profile, action, success, duration_s, error}
    """
    log_file = LOGS_DIR / "linsai.log"
    if not log_file.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    records: List[Dict[str, Any]] = []

    # v6.7.12: 同时兼容 optimize.py 旧日志与 lifecycle/executor.py 新日志
    logger_part = r"\[linsai\.(?:proposal_lifecycle|lifecycle_cron)\]"

    # 启动行：提取 profile 和 proposal_id
    dispatch_pattern = re.compile(
        r"\[(?P<at>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})\] \[(?P<level>\w+)\] "
        + logger_part
        + r" \[(?P<proposal_id>[\w\-]+)\] "
        r"对抗轮\s+\d+:\s*(?P<profile>critic|writer|researcher) "
        r"(评审|优化|定向检索)",
        re.IGNORECASE,
    )
    # 完成行：提取 profile、success、elapsed
    complete_pattern = re.compile(
        r"\[(?P<at>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})\] \[(?P<level>\w+)\] "
        + logger_part
        + r" \[(?P<proposal_id>[\w\-]+)\] 对抗轮\s+\d+:\s*(?P<profile>critic|writer|researcher) 完成 "
        r"success=(?P<success>True|False) elapsed=(?P<elapsed>\d+(?:\.\d+)?)s",
        re.IGNORECASE,
    )
    # ERROR 行：匹配 proposal_lifecycle / lifecycle_cron 模块错误
    error_pattern = re.compile(
        r"\[(?P<at>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})\] \[(?P<level>ERROR)\] "
        + logger_part
        + r" (?P<msg>.*)"
    )

    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                m = dispatch_pattern.search(line)
                if m:
                    try:
                        at = datetime.fromisoformat(m.group("at").replace(" ", "T") + "+00:00")
                    except Exception:
                        continue
                    if at < cutoff:
                        continue
                    records.append({
                        "at": at.isoformat(),
                        "profile": m.group("profile").lower(),
                        "proposal_id": m.group("proposal_id"),
                        "action": "dispatch",
                    })
                    continue

                m2 = complete_pattern.search(line)
                if m2:
                    try:
                        at = datetime.fromisoformat(m2.group("at").replace(" ", "T") + "+00:00")
                    except Exception:
                        continue
                    if at < cutoff:
                        continue
                    profile = m2.group("profile").lower()
                    # 找到最近一条同 profile 且未完成的 dispatch
                    for r in reversed(records):
                        if r.get("profile") == profile and not r.get("completed"):
                            r["success"] = m2.group("success").lower() == "true"
                            r["duration_s"] = float(m2.group("elapsed"))
                            r["completed"] = True
                            break
                    continue

                m3 = error_pattern.search(line)
                if m3:
                    try:
                        at = datetime.fromisoformat(m3.group("at").replace(" ", "T") + "+00:00")
                    except Exception:
                        continue
                    if at < cutoff:
                        continue
                    # 找到最近一条未完成的 dispatch 标记为失败
                    for r in reversed(records):
                        if not r.get("completed"):
                            r["success"] = False
                            r["error"] = m3.group("msg")[:200]
                            r["completed"] = True
                            break
    except Exception:
        pass
    return records


def _read_lifecycle_failures() -> Dict[str, List[Dict[str, Any]]]:
    """读取 _lifecycle.json 中所有 proposal 的 cron_failures。"""
    lifecycle_file = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    if not lifecycle_file.exists():
        return {}
    try:
        data = load_json(lifecycle_file)
        out: Dict[str, List[Dict[str, Any]]] = {}
        for pid, s in data.get("proposals", {}).items():
            fails = s.get("cron_failures", [])
            if fails:
                out[pid] = fails
        return out
    except Exception:
        return {}


# v6.8.50: job step → profile 映射（pipeline_jobs 是比日志更可靠的一手数据源）
_STEP_PROFILE_MAP = {
    "critic": "critic",
    "writer": "writer",
    "monitor": "monitor",
    "lit_search": "researcher",
    "lit_read": "researcher",
    "lit_note": "researcher",
    "idea_review": "researcher",
    "idea_fix": "writer",
    "gap_analysis": "analyst",
    "reference_check": "reviewer",
    "full_review": "critic",
}


def _read_pipeline_job_records(window_hours: int) -> List[Dict[str, Any]]:
    """v6.8.50: 从 _lifecycle.json 的 pipeline_jobs 提取 profile 执行记录。

    背景：日志正则解析与当前日志格式脱节，导致 profile_health 长期
    dispatch_count=0 / success_rate=null（2026-08-14 实测 7 个 profile 全部
    空数据却报 working）。pipeline_jobs 中每个 job 都有 step/status/
    started_at/finished_at/last_error，是一手数据源，此处转为与日志解析
    相同的 record 格式供下游统一消费。
    """
    lifecycle_file = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
    if not lifecycle_file.exists():
        return []
    records: List[Dict[str, Any]] = []
    try:
        data = load_json(lifecycle_file, default={"proposals": {}})
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        for pid, s in (data.get("proposals") or {}).items():
            for j in s.get("pipeline_jobs") or []:
                step = str(j.get("step", "") or "")
                profile = _STEP_PROFILE_MAP.get(step)
                if not profile:
                    continue
                finished = j.get("finished_at", "")
                if not finished:
                    continue
                try:
                    ft = datetime.fromisoformat(str(finished).replace("Z", "+00:00"))
                except Exception:
                    continue
                if ft < cutoff:
                    continue
                duration_s = 0.0
                try:
                    st = datetime.fromisoformat(str(j.get("started_at", "")).replace("Z", "+00:00"))
                    duration_s = max(0.0, (ft - st).total_seconds())
                except Exception:
                    pass
                status = j.get("status", "")
                records.append({
                    "profile": profile,
                    "at": ft.isoformat(),
                    "proposal_id": pid,
                    "success": status == "done",
                    "completed": status in ("done", "failed"),
                    "duration_s": duration_s,
                    "error": str(j.get("last_error", "") or "")[:200],
                    "source": "pipeline_jobs",
                })
    except Exception:
        pass
    return records


def compute_profile_health(window_hours: int = 24) -> Dict[str, Any]:
    """计算所有 profile 的健康度。

    Args:
        window_hours: 时间窗（小时），默认 24

    Returns:
        {
          'profiles': { profile_name: {status, success_rate_24h, avg_duration_s, recent_error, suggestion} },
          'alerts': [ {level, type, profile, msg} ],
          'computed_at': ISO 字符串
        }
    """
    # 1. 从 hermes_bridge 获取当前状态
    current_profiles = list_team_profiles()
    current_by_name: Dict[str, Dict[str, Any]] = {}
    for p in current_profiles:
        # list_team_profiles 返回的格式：name/label/role/exists/gateway_running/cron_count/heartbeat_alive
        name = p.get("name") or ""
        if name:
            current_by_name[name] = p

    # 2. 从 log 解析历史派活记录
    log_records = _parse_log_records(window_hours)
    by_profile: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in log_records:
        by_profile[r["profile"]].append(r)

    # 2.5 v6.8.50: 合并 pipeline_jobs 一手数据（优先于日志解析——
    # 日志正则脱节曾导致 7 个 profile 全部空数据却报 working）
    pipeline_records = _read_pipeline_job_records(window_hours)
    for r in pipeline_records:
        by_profile[r["profile"]].append(r)

    # 3. 从 _lifecycle 读取失败记录
    lifecycle_fails = _read_lifecycle_failures()

    # 4. 逐 profile 计算健康度
    profiles_out: Dict[str, Dict[str, Any]] = {}
    alerts: List[Dict[str, Any]] = []

    for name in TEAM_PROFILE_NAMES:
        cur = current_by_name.get(name, {})
        recs = by_profile.get(name, [])

        # 先计算失败记录，供状态派生和建议使用
        completed_recs = [r for r in recs if r.get("completed")]
        failed_recs = [r for r in recs if r.get("completed") and not r.get("success")]
        recent_error = failed_recs[-1].get("error", "") if failed_recs else ""

        # 状态派生：基于 exists / heartbeat_alive / 实际失败证据
        # v6.7.10 修复：pipeline 使用 hermes --profile -z 一次性调用，不依赖常驻 gateway。
        # 因此 gateway_running 不再作为 blocked 依据；blocked 仅由最近失败记录触发。
        if not cur or not cur.get("exists", True):
            status = "offline"
        elif cur.get("heartbeat_alive"):
            status = "working"
        elif failed_recs:
            # v6.8.54: blocked 仅在最近连续 2 次失败时标记——单次瞬时失败
            # （如 28s api_error）此前会立刻显示 blocked，造成"看起来坏了
            # 其实没坏"的误报噪音（2026-08-14 体检：writer/critic 曾同时
            # 被误标，成功率仍 0.90）。单次失败归入 degraded（降级但存活）。
            tail = [bool(r.get("success")) for r in completed_recs[-2:]]
            if len(tail) == 2 and not any(tail):
                status = "blocked"
            else:
                status = "degraded"
        else:
            status = "idle"

        # 成功率
        if completed_recs:
            success_count = sum(1 for r in completed_recs if r.get("success"))
            total = len(completed_recs)
            success_rate = round(success_count / total, 3)
        else:
            success_rate = None

        # 平均耗时（仅完整记录的）
        durations = [r.get("duration_s", 0) for r in recs if r.get("duration_s")]
        avg_duration = round(sum(durations) / len(durations), 1) if durations else 0

        # 建议
        suggestion = ""
        if success_rate is not None and success_rate < 0.5:
            suggestion = "成功率 < 50%，建议检查 provider 配置或切换 fallback"
            alerts.append({
                "level": "warning",
                "type": "low_success_rate",
                "profile": name,
                "msg": f"{name} 成功率仅 {success_rate*100:.0f}%，建议排查",
            })
        elif status == "offline":
            suggestion = "Profile offline，hermes CLI 可能未注册该 profile"
            alerts.append({
                "level": "error",
                "type": "profile_offline",
                "profile": name,
                "msg": f"{name} 离线，请检查 ~/.hermes/profiles/{name}/config.yaml",
            })
        elif recent_error and "timeout" in recent_error.lower():
            suggestion = "最近一次失败是超时，可考虑增加 timeout"

        profiles_out[name] = {
            "status": status,
            "success_rate_24h": success_rate,
            "dispatch_count_24h": len(recs),
            "avg_duration_s": avg_duration,
            "recent_error": recent_error,
            "suggestion": suggestion,
        }

    return {
        "profiles": profiles_out,
        "alerts": alerts,
        "window_hours": window_hours,
        "computed_at": now_utc(),
    }


def _self_check() -> None:
    """自检：测试 compute_profile_health 的基本输出。"""
    print("=== profile_health._self_check ===")
    result = compute_profile_health(window_hours=24)
    assert "profiles" in result, "缺 profiles 字段"
    assert len(result["profiles"]) >= 5, f"应至少 5 个 profile，实际 {len(result['profiles'])}"
    for name, h in result["profiles"].items():
        assert "status" in h
        assert "success_rate_24h" in h
        print(f"  ✓ {name}: status={h['status']}, success_rate={h['success_rate_24h']}")
    print(f"  alerts: {len(result['alerts'])} 条")
    print("=== 通过 ===")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        _self_check()
    else:
        # 打印健康度
        result = compute_profile_health()
        print(json.dumps(result, ensure_ascii=False, indent=2))
