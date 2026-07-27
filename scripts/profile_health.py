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

    每条记录包含：{at, profile, action, success, duration_s, error}
    """
    log_file = LOGS_DIR / "linsai.log"
    if not log_file.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    records: List[Dict[str, Any]] = []

    # 匹配派活行：[INFO] [profile.linsai] 派活给 xxx profile
    # 匹配完成行：[INFO] xxx 优化完成 / [ERROR] xxx 失败
    dispatch_pattern = re.compile(
        r"\[(?P<at>[\d\-T:Z]+)\] \[(?P<level>\w+)\] \[(?P<mod>[\w\.]+)\] "
        r".*?(?P<profile>writer|critic|researcher|analyst|reviewer|linsai|pipeline-runner|writer) profile",
        re.IGNORECASE
    )
    # 简单成功率：从 ERROR 行反推
    error_pattern = re.compile(
        r"\[(?P<at>[\d\-T:Z]+)\] \[(?P<level>ERROR|WARNING)\] \[(?P<mod>[\w\.]+)\] (?P<msg>.*)"
    )

    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                # 仅处理最近 window_hours 内的日志
                m = dispatch_pattern.search(line)
                if m:
                    try:
                        at = datetime.fromisoformat(m.group("at").replace("Z", "+00:00"))
                    except Exception:
                        continue
                    if at < cutoff:
                        continue
                    records.append({
                        "at": at.isoformat(),
                        "profile": m.group("profile").lower(),
                        "level": m.group("level"),
                        "action": "dispatch",
                    })

                m2 = error_pattern.search(line)
                if m2:
                    try:
                        at = datetime.fromisoformat(m2.group("at").replace("Z", "+00:00"))
                    except Exception:
                        continue
                    if at < cutoff:
                        continue
                    # 找到对应 profile 记录（最近的 dispatch）
                    for r in reversed(records):
                        if r.get("profile") and not r.get("completed"):
                            r["success"] = m2.group("level") != "ERROR"
                            r["error"] = m2.group("msg")[:200] if not r["success"] else ""
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

    # 3. 从 _lifecycle 读取失败记录
    lifecycle_fails = _read_lifecycle_failures()

    # 4. 逐 profile 计算健康度
    profiles_out: Dict[str, Dict[str, Any]] = {}
    alerts: List[Dict[str, Any]] = []

    for name in TEAM_PROFILE_NAMES:
        cur = current_by_name.get(name, {})
        recs = by_profile.get(name, [])

        # 状态派生：基于 exists / gateway_running / heartbeat_alive
        if not cur or not cur.get("exists", True):
            status = "offline"
        elif cur.get("heartbeat_alive"):
            status = "working"
        elif cur.get("gateway_running"):
            status = "idle"
        else:
            status = "blocked"

        # 成功率
        if recs:
            completed = [r for r in recs if r.get("completed")]
            if completed:
                success_count = sum(1 for r in completed if r.get("success"))
                total = len(completed)
                success_rate = round(success_count / total, 3)
            else:
                success_rate = None
        else:
            success_rate = None

        # 平均耗时（仅完整记录的）
        durations = [r.get("duration_s", 0) for r in recs if r.get("duration_s")]
        avg_duration = round(sum(durations) / len(durations), 1) if durations else 0

        # 最近错误
        failed_recs = [r for r in recs if r.get("completed") and not r.get("success")]
        recent_error = failed_recs[-1]["error"] if failed_recs else ""

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
