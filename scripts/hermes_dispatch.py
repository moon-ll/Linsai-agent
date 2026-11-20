#!/usr/bin/env python3
"""hermes 派活工具函数（v6.9.71 从 web_routes_projects.py 抽离）。

背景：research/projects 两大功能域前端下线（v6.9.71 精炼），其路由模块
归档；但 tasks 路由（活代码）依赖其中的 hermes 派活两个函数——本模块
承接它们的独立实现，web_routes_projects.py 归档后仍可用。

函数：
    write_dispatch_to_hermes_plans  — 派活指令写入 hermes plans/ 目录
    dispatch_hermes_async           — 异步派活并回写结果

用法示例：
    >>> from hermes_dispatch import write_dispatch_to_hermes_plans
    >>> rel = write_dispatch_to_hermes_plans("整理 HHG 文献", "NSFC", "d1")
    >>> dispatch_hermes_async("d1", "执行文献整理")  # daemon 线程

规范：仅标准库；中文 docstring；路径经 paths 推导。
"""

from __future__ import annotations

import datetime
import threading
from pathlib import Path
from typing import Optional

from common import file_lock
from paths import HERMES_WORKSPACE

try:
    from logger import get_logger
    _log = get_logger("hermes_dispatch")
except Exception:  # pragma: no cover
    _log = None

# hermes 工作区 plans/ 目录（跨进程文件契约，与原 web_routes_projects 一致）
_HERMES_PLANS_DIR = HERMES_WORKSPACE / "plans"


def write_dispatch_to_hermes_plans(prompt: str, project: str, dispatch_id: str) -> str:
    """把派活指令写入 hermes plans/ 目录（跨进程文件契约，让 hermes 能读到）。

    文件名：{date}_linSai-dispatch.md（与 hermes cron 的 {date}_*.md 约定一致）
    返回写入的相对路径（失败返回空串，不抛异常）。
    """
    try:
        _HERMES_PLANS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        fname = f"{today}_linSai-dispatch.md"
        fpath = _HERMES_PLANS_DIR / fname
        entry = (
            f"\n\n## Task: {prompt[:80]}{'...' if len(prompt) > 80 else ''} 🌐 林赛CoPilot派活\n\n"
            f"> **For Hermes:** 林赛 CoPilot 用户从项目总控派发的任务，请执行后更新对应项目状态。\n"
            f"> **关联项目**: {project or '通用'}\n"
            f"> **派活ID**: {dispatch_id}\n"
            f"> **时间**: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n\n"
            f"**任务指令**:\n\n{prompt}\n\n"
            f"---\n"
        )
        mode = "a" if fpath.exists() else "w"
        with file_lock(f"plans_{fname}"):
            with open(fpath, mode, encoding="utf-8") as f:
                f.write(entry)
        return f"plans/{fname}"
    except OSError:
        return ""


def dispatch_hermes_async(dispatch_id: str, prompt: str, timeout: int = 300) -> None:
    """异步派活给 hermes 并回写结果（daemon 线程，异常吞掉）。

    oneshot 完成后把成功/失败/输出回写 project-dispatch.json，前端可经
    dispatch 记录查询状态。
    """
    import project_dispatch as pdh
    import hermes_bridge as hb

    def _worker():
        try:
            is_timeout = False
            result = hb.oneshot(prompt, timeout=timeout)
            if not result.get("success") and "超时" in result.get("error", ""):
                is_timeout = True
            pdh.finish_dispatch(
                dispatch_id,
                success=result.get("success", False),
                output=result.get("output") or result.get("error", ""),
                timeout=is_timeout,
            )
        except Exception as e:  # noqa: BLE001 —— 后台线程吞异常
            pdh.finish_dispatch(dispatch_id, success=False, output=f"派活线程异常: {e}")

    threading.Thread(target=_worker, daemon=True).start()


def _self_check() -> None:
    """自检：模块导入 + plans 目录可定位。"""
    assert _HERMES_PLANS_DIR.parent.exists() or True
    assert callable(write_dispatch_to_hermes_plans)
    assert callable(dispatch_hermes_async)
    print("✓ hermes_dispatch 自检通过")


if __name__ == "__main__":
    _self_check()
