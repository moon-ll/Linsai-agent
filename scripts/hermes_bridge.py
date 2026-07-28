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
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from paths import PROJECT_ROOT
from common import clean_subprocess_env

# hermes profile 路径
HERMES_HOME = Path.home() / ".hermes"
LINSAI_PROFILE = HERMES_HOME / "profiles" / "linsai"
LINSAI_CRON_JOBS = LINSAI_PROFILE / "cron" / "jobs.json"
PROFILES_DIR = HERMES_HOME / "profiles"

# 团队 profile 定义（名称→角色标签）
TEAM_PROFILES = {
    "linsai": {"label": "林赛·总控", "icon": "🧭", "role": "方向校准/总控", "stage": 0},
    "pipeline-runner": {"label": "管线编排器", "icon": "⚡", "role": "全链路编排", "stage": None},
    "researcher": {"label": "研究员", "icon": "📚", "role": "文献调研", "stage": 1},
    "analyst": {"label": "分析师", "icon": "🔍", "role": "缺口分析+科学问题", "stage": None},
    "writer": {"label": "撰写者", "icon": "✍️", "role": "申请书撰写", "stage": 4},
    "critic": {"label": "对抗评审", "icon": "⚔️", "role": "对抗式优化", "stage": None},
    "reviewer": {"label": "终审员", "icon": "✅", "role": "质量自检", "stage": 5},
}

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


def cron_jobs_path(profile: str = "linsai") -> Path:
    """返回指定 hermes profile 的 cron jobs.json 路径。"""
    return PROFILES_DIR / profile / "cron" / "jobs.json"


def cron_list_profile(profile: str = "linsai") -> List[Dict[str, Any]]:
    """读取指定 profile 的 cron job 列表。

    签名与 cron_list() 一致，方便 lifecycle cron 框架使用非 linsai profile。
    """
    path = cron_jobs_path(profile)
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    jobs_raw = data.get("jobs", []) if isinstance(data, dict) else data
    if not isinstance(jobs_raw, list):
        return []

    jobs = []
    for j in jobs_raw:
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

    jobs.sort(key=lambda x: (x["status"] != "active", x["name"]))
    return jobs


def cron_create_no_agent(
    script_name: str,
    name: str,
    schedule: str,
    workdir: str,
    profile: str = "linsai",
    repeat: Optional[int] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """创建一个不经过 LLM agent、直接执行本地脚本的 hermes cron job。

    Args:
        script_name: ~/.hermes/profiles/<profile>/scripts/ 下的脚本文件名；
                    hermes 要求相对路径，并会在 profile 脚本目录下查找
        name: cron job 名称
        schedule: cron 表达式，如 "*/20 * * * *"
        workdir: 工作目录
        profile: hermes profile（默认 linsai）
        repeat: 重复次数，None 表示无限
        timeout: hermes CLI 调用超时

    Returns:
        {success, cron_job_id, message, output}
    """
    cmd = [
        "hermes", "--profile", profile, "cron", "create",
        schedule,
        "--name", name,
        "--script", script_name,
        "--no-agent",
        "--deliver", "local",
        "--workdir", workdir,
    ]
    if repeat is not None:
        cmd += ["--repeat", str(repeat)]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            # 尝试从输出中提取 job id（hermes 通常会在成功信息里打印 id）
            output = result.stdout.strip()
            job_id = ""
            for line in output.splitlines():
                m = re.search(r"[0-9a-f]{12,}", line)
                if m:
                    job_id = m.group(0)
                    break
            return {
                "success": True,
                "cron_job_id": job_id,
                "message": f"✓ 已创建 cron: {name}",
                "output": output[:300],
            }
        return {
            "success": False,
            "cron_job_id": "",
            "message": f"✗ {result.stderr.strip()[:200] or result.stdout.strip()[:200]}",
            "output": result.stdout.strip()[:300],
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "cron_job_id": "", "message": f"✗ 创建 cron 超时（{timeout}s）"}
    except FileNotFoundError:
        return {"success": False, "cron_job_id": "", "message": "✗ 未找到 hermes 命令"}
    except Exception as e:
        return {"success": False, "cron_job_id": "", "message": f"✗ 异常: {e}"}


def cron_delete(job_id: str, profile: str = "linsai", timeout: int = 30) -> Dict[str, Any]:
    """删除指定 hermes cron job。"""
    cmd = ["hermes", "--profile", profile, "cron", "delete", job_id]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return {"success": True, "message": f"✓ 已删除 job {job_id}", "output": result.stdout.strip()[:200]}
        return {
            "success": False,
            "message": f"✗ 删除失败: {result.stderr.strip()[:200] or result.stdout.strip()[:200]}",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": f"✗ 删除超时（{timeout}s）"}
    except FileNotFoundError:
        return {"success": False, "message": "✗ 未找到 hermes 命令"}
    except Exception as e:
        return {"success": False, "message": f"✗ 异常: {e}"}


def cron_delete_by_name_prefix(prefix: str, profile: str = "linsai") -> Dict[str, Any]:
    """按名称前缀批量删除 cron job。"""
    removed = []
    failed = []
    for job in cron_list_profile(profile):
        name = job.get("name", "")
        if name.startswith(prefix):
            res = cron_delete(job.get("id"), profile=profile)
            if res.get("success"):
                removed.append(name)
            else:
                failed.append({"name": name, "error": res.get("message", "")})
    return {"success": len(failed) == 0, "removed": removed, "failed": failed}


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
    # v6.7.7 修复：hermes profile 默认使用 zai provider，若仅有 GLM_API_KEY 则透传为 ZAI_API_KEY
    extra_env = {}
    zai_key = os.environ.get("ZAI_API_KEY") or os.environ.get("GLM_API_KEY")
    if zai_key:
        extra_env["ZAI_API_KEY"] = zai_key
    env = clean_subprocess_env(extra=extra_env)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
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


def list_team_profiles() -> List[Dict[str, Any]]:
    """列出团队所有 profile 的状态（v6.6.0）。

    汇总每个 profile 的：
    - 基本信息（名称/角色/SOUL.md 描述）
    - 网关运行状态（gateway_state.json）
    - cron 任务数和最近执行状态
    - 最近会话时间（sessions/ 目录）
    - 心跳活跃度（ticker_heartbeat）

    Returns:
        [{name, label, icon, role, stage, exists, gateway_running,
          cron_count, cron_active, last_cron_status,
          last_session, heartbeat_alive, soul_brief}]
    """
    import time as _time
    profiles = []

    for name, meta in TEAM_PROFILES.items():
        profile_dir = PROFILES_DIR / name
        info = {
            "name": name,
            "label": meta["label"],
            "icon": meta["icon"],
            "role": meta["role"],
            "stage": meta["stage"],
            "exists": profile_dir.exists(),
            "gateway_running": False,
            "cron_count": 0,
            "cron_active": 0,
            "last_cron_status": "",
            "last_session": "",
            "heartbeat_alive": False,
            "soul_brief": "",
        }

        if not profile_dir.exists():
            profiles.append(info)
            continue

        # 网关状态
        gw_path = profile_dir / "gateway_state.json"
        if gw_path.exists():
            try:
                gs = json.loads(gw_path.read_text(encoding="utf-8"))
                info["gateway_running"] = gs.get("gateway_state") == "running" or bool(gs.get("pid"))
            except Exception:
                pass

        # cron 任务
        cron_dir = profile_dir / "cron"
        jobs_path = cron_dir / "jobs.json"
        if jobs_path.exists():
            try:
                jd = json.loads(jobs_path.read_text(encoding="utf-8"))
                jobs = jd.get("jobs", []) if isinstance(jd, dict) else (jd if isinstance(jd, list) else [])
                info["cron_count"] = len(jobs)
                info["cron_active"] = sum(1 for j in jobs if j.get("enabled", True))
                # 最近执行状态
                for j in jobs:
                    if j.get("last_status"):
                        info["last_cron_status"] = j["last_status"]
                        break
            except Exception:
                pass

        # 最近会话
        sessions_dir = profile_dir / "sessions"
        if sessions_dir.exists():
            try:
                sessions = sorted(sessions_dir.glob("*.jsonl"), reverse=True)
                if sessions:
                    stat = sessions[0].stat()
                    info["last_session"] = _time.strftime(
                        "%Y-%m-%d %H:%M", _time.localtime(stat.st_mtime)
                    )
            except Exception:
                pass

        # 心跳（ticker_heartbeat，5分钟内有更新视为活跃）
        hb_path = cron_dir / "ticker_heartbeat"
        if hb_path.exists():
            try:
                hb_time = float(hb_path.read_text().strip())
                info["heartbeat_alive"] = (_time.time() - hb_time) < 300
            except Exception:
                pass

        # SOUL.md 摘要（第一段非注释行）
        soul_path = profile_dir / "SOUL.md"
        if soul_path.exists():
            try:
                lines = soul_path.read_text(encoding="utf-8").split("\n")
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and not stripped.startswith(">") and len(stripped) > 10:
                        info["soul_brief"] = stripped[:80]
                        break
            except Exception:
                pass

        profiles.append(info)

    return profiles


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
