# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——cron 安装（hermes gateway no-agent 脚本 job）。

v8 深研链两个定时任务（docs/WORKBENCH-ARCHITECTURE.md §6.3）：
    lc-topic-daily        30 9 * * 1-5   每日深研 worker
    lc-workbench-monitor  0 */6 * * *    工作台轻量健康检查

幂等：同名 job 先删后建（与 lifecycle/framework 的 _cron_create_idempotent 语义一致）。

用法示例：
    python3 scripts/topic_pipeline.py --setup-cron
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .constants import PROJECT_ROOT

HERMES_PROFILE_SCRIPTS = Path.home() / ".hermes" / "profiles" / "linsai" / "scripts"

# (job 名, cron 表达式, wrapper 文件名, 说明)
V8_CRON_JOBS = [
    ("lc-topic-daily", "30 9 * * 1-5", "lc_topic_daily.sh",
     "每日深研 worker：取队首问题候选 → 单遍深研 → 组装 → 验收自检"),
    ("lc-workbench-monitor", "0 */6 * * *", "lc_workbench_monitor.sh",
     "工作台轻量健康检查：cron 对账 + topics 健康 + KB 告警"),
]

_WRAPPER_TEMPLATE = """#!/bin/bash
# {comment}
cd {project_root} || exit 1
{command} >> logs/{logfile} 2>&1
"""


def _write_wrapper(filename: str, command: str, comment: str) -> Path:
    HERMES_PROFILE_SCRIPTS.mkdir(parents=True, exist_ok=True)
    path = HERMES_PROFILE_SCRIPTS / filename
    path.write_text(_WRAPPER_TEMPLATE.format(
        comment=comment, project_root=PROJECT_ROOT,
        command=command, logfile=filename.replace(".sh", ".log")), encoding="utf-8")
    path.chmod(0o755)
    return path


def setup_cron() -> Dict[str, Any]:
    """安装 v8 深研链 cron（幂等，同名先删后建）。"""
    try:
        import hermes_bridge as hb
    except Exception as e:  # noqa: BLE001
        return {"success": False, "error": f"hermes_bridge 不可用: {e}"}

    jobs: List[Dict[str, Any]] = []
    for name, schedule, wrapper, comment in V8_CRON_JOBS:
        command = ("python3 scripts/topic_pipeline.py --daily"
                   if name == "lc-topic-daily"
                   else "python3 scripts/workbench_monitor.py")
        _write_wrapper(wrapper, command, comment)
        existing = {j.get("name"): j.get("id") for j in hb.cron_list_profile("linsai")}
        if existing.get(name):
            hb.cron_delete(existing[name])
        res = hb.cron_create_no_agent(
            script_name=wrapper, name=name, schedule=schedule,
            workdir=str(PROJECT_ROOT),
        )
        jobs.append({"name": name, "schedule": schedule, "wrapper": wrapper,
                     "success": res.get("success", False), "message": res.get("message", "")})
    return {"success": all(j["success"] for j in jobs), "jobs": jobs}


def teardown_cron() -> Dict[str, Any]:
    """移除 v8 深研链 cron（回滚用）。"""
    try:
        import hermes_bridge as hb
    except Exception as e:  # noqa: BLE001
        return {"success": False, "error": str(e)}
    removed: List[str] = []
    for name, _, _, _ in V8_CRON_JOBS:
        for j in hb.cron_list_profile("linsai"):
            if j.get("name") == name:
                res = hb.cron_delete(j.get("id"))
                if res.get("success"):
                    removed.append(name)
    return {"success": True, "removed": removed}
