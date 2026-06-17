#!/usr/bin/env python3
"""hermes 桥接核心 —— 从林赛 CoPilot 控制本地 hermes agent。

用途：
    林赛 CoPilot Web 通过本模块控制 hermes（+ profile linsai）的 cron 定时任务，
    并可手动派活（oneshot agent loop）。hermes 是真正的自主执行引擎，
    本模块是林赛对它的控制接口。

能力：
    - cron_list()：读取 linsai profile 的 cron job 列表（直接读 jobs.json，比解析 CLI 稳）
    - cron_control()：暂停/恢复/立即触发指定 job（subprocess 调 hermes cron 子命令）
    - oneshot()：手动派一个任务给 hermes agent（hermes -z，agent loop 自主执行）

架构关系：
    hermes（大脑和手脚）← 本模块（控制接口）← 林赛 Web（指挥台）
    hermes 的产出沉淀到 ~/Desktop/hermes_workspace/
    林赛通过 project_reader.py 读取这些产出做可视化

用法示例：
    >>> from hermes_bridge import cron_list, cron_control, oneshot
    >>> jobs = cron_list()                       # 列出所有 cron job
    >>> cron_control('dd309a92', 'pause')         # 暂停某 job
    >>> output = oneshot('深分析 arXiv 2403.15337')  # 手动派活（agent loop）

规范：
    - 仅使用 Python 3 标准库（subprocess 调 hermes CLI）
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 输出使用中文，状态图标统一
    - oneshot 默认超时 300s（agent loop 较慢），可配置
    - 失败优雅降级（返回错误信息，不抛异常）
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent

# hermes profile 路径
HERMES_HOME = Path.home() / ".hermes"
LINSAI_PROFILE = HERMES_HOME / "profiles" / "linsai"
LINSAI_CRON_JOBS = LINSAI_PROFILE / "cron" / "jobs.json"

# hermes CLI 命令前缀（linsai profile）
HERMES_CMD = ["hermes", "--profile", "linsai"]

# oneshot 默认超时（agent loop 慢）
ONESHOT_TIMEOUT = 300


def cron_list() -> List[Dict[str, Any]]:
    """读取 linsai profile 的 cron job 列表。

    直接读 jobs.json（比解析 `hermes cron list` 的人类可读输出更稳）。

    Returns:
        [{id, name, schedule_display, status, next_run, last_run, last_status, deliver}]
        失败返回空列表。
    """
    if not LINSAI_CRON_JOBS.exists():
        return []

    try:
        data = json.loads(LINSAI_CRON_JOBS.read_text(encoding="utf-8"))
    except Exception:
        return []

    jobs_raw = data.get("jobs", []) if isinstance(data, dict) else data
    if not isinstance(jobs_raw, list):
        return []

    jobs = []
    for j in jobs_raw:
        # 状态判定：enabled=False 或有 paused_at → paused；否则 active
        enabled = j.get("enabled", True)
        paused_at = j.get("paused_at")
        if not enabled or paused_at:
            status = "paused"
        else:
            status = "active"

        schedule = j.get("schedule", {})
        schedule_display = ""
        if isinstance(schedule, dict):
            schedule_display = schedule.get("display", schedule.get("expr", ""))
        elif isinstance(schedule, str):
            schedule_display = schedule

        jobs.append({
            "id": j.get("id", ""),
            "name": j.get("name", ""),
            "schedule": schedule_display,
            "status": status,
            "next_run": j.get("next_run_at", ""),
            "last_run": j.get("last_run_at", ""),
            "last_status": j.get("last_status", ""),
            "deliver": j.get("deliver", ""),
            "paused_at": paused_at or "",
        })

    # active 优先，再按名称排序
    jobs.sort(key=lambda x: (x["status"] != "active", x["name"]))
    return jobs


def cron_control(job_id: str, action: str, timeout: int = 30) -> Dict[str, Any]:
    """控制 cron job（暂停/恢复/立即触发）。

    Args:
        job_id: cron job 的 ID
        action: "pause" | "resume" | "run"
        timeout: 命令超时秒数

    Returns:
        {success, message}
    """
    if action not in ("pause", "resume", "run"):
        return {"success": False, "message": f"未知操作: {action}"}

    cmd = HERMES_CMD + ["cron", action, job_id]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            action_label = {"pause": "暂停", "resume": "恢复", "run": "触发"}[action]
            return {
                "success": True,
                "message": f"✓ 已{action_label} job {job_id}",
                "output": result.stdout.strip()[:200],
            }
        return {
            "success": False,
            "message": f"✗ hermes 返回错误: {result.stderr.strip()[:200] or result.stdout.strip()[:200]}",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": f"✗ 操作超时（{timeout}s）"}
    except FileNotFoundError:
        return {"success": False, "message": "✗ 未找到 hermes 命令，请确认已安装"}
    except Exception as e:
        return {"success": False, "message": f"✗ 执行异常: {e}"}


def oneshot(prompt: str, timeout: int = ONESHOT_TIMEOUT) -> Dict[str, Any]:
    """手动派活给 hermes agent（oneshot 模式，agent loop 自主执行）。

    用 `hermes --profile linsai -z <prompt>` 触发一次完整的 agent loop。
    hermes 会自主规划→调用工具→执行→返回最终结果。

    Args:
        prompt: 任务描述（中文自然语言）
        timeout: 超时秒数（agent loop 较慢，默认 300s）

    Returns:
        {success, output, error}
    """
    cmd = HERMES_CMD + ["-z", prompt]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            # 截断超长输出
            if len(output) > 16000:
                output = output[:16000] + f"\n\n... (已截断，共 {len(output)} 字符)"
            return {"success": True, "output": output, "error": ""}
        return {
            "success": False,
            "output": result.stdout.strip()[:2000],
            "error": result.stderr.strip()[:500] or f"退出码 {result.returncode}",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": f"agent 超时（{timeout}s）——任务可能仍在后台执行"}
    except FileNotFoundError:
        return {"success": False, "output": "", "error": "未找到 hermes 命令"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}


def check_hermes_available() -> Dict[str, Any]:
    """检查 hermes 是否可用（CLI + linsai profile + 网关状态）。"""
    import shutil

    available = shutil.which("hermes") is not None
    profile_exists = LINSAI_PROFILE.exists()

    # 检查网关状态（读 gateway_state.json）
    gateway_status = "unknown"
    gateway_path = LINSAI_PROFILE / "gateway_state.json"
    if gateway_path.exists():
        try:
            gs = json.loads(gateway_path.read_text(encoding="utf-8"))
            # 检查是否有活跃的网关进程标记
            gateway_status = "running" if gs.get("pid") else "unknown"
        except Exception:
            pass

    return {
        "hermes_cli": available,
        "linsai_profile": profile_exists,
        "gateway_status": gateway_status,
        "cron_jobs_count": len(cron_list()),
    }


def _self_check() -> None:
    """自检：验证 hermes 可用性 + cron 读取。"""
    print("=" * 50)
    print("◐ hermes_bridge 自检")
    print("=" * 50)

    print("\n[1/3] 检查 hermes 可用性...")
    status = check_hermes_available()
    print(f"  hermes CLI: {'✓' if status['hermes_cli'] else '✗'}")
    print(f"  linsai profile: {'✓' if status['linsai_profile'] else '✗'}")
    print(f"  网关状态: {status['gateway_status']}")

    print("\n[2/3] 读取 cron job 列表...")
    jobs = cron_list()
    print(f"  ✓ 读取 {len(jobs)} 个 job")
    for j in jobs[:3]:
        print(f"    [{j['status']}] {j['name'][:25]} | {j['schedule']} | last: {j['last_status']}")

    print("\n[3/3] oneshot 能力（不实际调用，验证命令构造）...")
    # 不实际调用 oneshot（会触发完整 agent loop，耗时），只验证函数可调用
    assert callable(oneshot), "oneshot 不可调用"
    print("  ✓ oneshot 函数就绪（实际调用需通过 Web/API 触发）")

    print("\n✓ hermes_bridge 自检通过")


if __name__ == "__main__":
    _self_check()
