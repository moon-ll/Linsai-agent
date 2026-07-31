#!/usr/bin/env python3
"""生命周期 cron 框架安装与卸载。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import hermes_bridge as hb
from paths import PROJECT_ROOT

from .constants import (
    DEFAULT_ORCHESTRATE_SCHEDULE,
    DEFAULT_REPAIR_SCHEDULE,
    DEFAULT_WEEKEND_INPUT_SCHEDULE,
    DEFAULT_WEEKEND_OUTPUT_SCHEDULE,
    DEFAULT_WEEKEND_REFLECTION_SCHEDULE,
    DEFAULT_WORKER_INTERVAL,
    HERMES_PROFILE,
    JOB_STATUS_PENDING,
    WEEKEND_JOB_INPUT,
    WEEKEND_JOB_OUTPUT,
    WEEKEND_JOB_REFLECTION,
    WEEKEND_JOBS,
)
from weekend_pipeline.constants import (
    DEFAULT_WORKER_SCHEDULE as WEEKEND_DEFAULT_WORKER_SCHEDULE,
    WEEKEND_WORKER_CRON_NAME,
)
from .utils import _load_weekend_jobs, _save_weekend_jobs, _write_wrapper_script

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


def setup_cron_framework(
    self,
    orchestrate_schedule: str = DEFAULT_ORCHESTRATE_SCHEDULE,
    worker_interval: str = DEFAULT_WORKER_INTERVAL,
    repair_schedule: str = DEFAULT_REPAIR_SCHEDULE,
    install_weekend: bool = True,
) -> Dict[str, Any]:
    """安装 v6.7.12 cron 框架：删除旧单一 cron，创建 orchestrate + repair + 全局微调度器 + weekend。

    worker_interval 参数保留以兼容 CLI，但实际 worker 已由全局微调度器替代，
    每 5 分钟从所有 optimizing proposal 中挑选一个最优先的 pending job 执行。
    """
    self._write_generic_wrappers()

    # 删除旧的大 cron（兼容 v6.7.4 及之前）
    old_names = ["每日提案系统编排", "每日编排"]
    removed = []
    for cron in hb.cron_list_profile(HERMES_PROFILE):
        if cron.get("name") in old_names:
            hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
            removed.append(cron.get("name"))

    # orchestrate cron
    orch = hb.cron_create_no_agent(
        script_name="lc_orchestrate.sh",
        name="lc-daily-orchestrate",
        schedule=orchestrate_schedule,
        workdir=str(PROJECT_ROOT),
        profile=HERMES_PROFILE,
    )

    # repair cron
    rep = hb.cron_create_no_agent(
        script_name="lc_repair.sh",
        name="lc-repair",
        schedule=repair_schedule,
        workdir=str(PROJECT_ROOT),
        profile=HERMES_PROFILE,
    )

    # 全局微调度器 cron（每 5 分钟执行一个 job）
    micro = self.schedule_micro_scheduler()

    # 暂停旧的 per-proposal worker，避免并发
    pause_res = self.pause_old_worker_crons()

    # 立即执行一次 orchestrate，确保 checkpoint 就位
    orch_now = self.run_orchestrator()

    result = {
        "success": orch.get("success") and rep.get("success") and micro.get("success"),
        "removed_old": removed,
        "orchestrate": orch,
        "repair": rep,
        "micro_scheduler": micro,
        "paused_workers": pause_res.get("paused", []),
        "first_orchestrate": orch_now,
    }

    # 安装周末任务 cron
    if install_weekend:
        weekend = self.setup_weekend_crontab()
        result["weekend"] = weekend
        result["success"] = result["success"] and all(
            c.get("result", {}).get("success") for c in weekend.get("created", [])
        )

    return result

def setup_weekend_crontab(
    self,
    input_schedule: str = DEFAULT_WEEKEND_INPUT_SCHEDULE,
    output_schedule: str = DEFAULT_WEEKEND_OUTPUT_SCHEDULE,
    reflection_schedule: str = DEFAULT_WEEKEND_REFLECTION_SCHEDULE,
) -> Dict[str, Any]:
    """安装周末任务 cron：输入（周六早）/ 输出（周六午）/ 反思（周日早）。"""
    self._write_generic_wrappers()
    # 先清理已存在的 weekend cron，避免重复安装
    self.teardown_weekend_crontab()

    # 确保 weekend_jobs 状态文件存在
    weekend_jobs = _load_weekend_jobs()
    for job_key in WEEKEND_JOBS:
        weekend_jobs.setdefault("jobs", {}).setdefault(job_key, {
            "status": JOB_STATUS_PENDING,
            "last_run": "",
            "started_at": "",
            "finished_at": "",
            "last_error": "",
            "attempts": 0,
        })
    _save_weekend_jobs(weekend_jobs)

    created = []
    for job_key, schedule in [
        (WEEKEND_JOB_INPUT, input_schedule),
        (WEEKEND_JOB_OUTPUT, output_schedule),
        (WEEKEND_JOB_REFLECTION, reflection_schedule),
    ]:
        script_name = f"lc_{job_key}.sh"
        cron_name = f"lc-weekend-{job_key.replace('_', '-')}"
        res = hb.cron_create_no_agent(
            script_name=script_name,
            name=cron_name,
            schedule=schedule,
            workdir=str(PROJECT_ROOT),
            profile=HERMES_PROFILE,
        )
        created.append({"job": job_key, "cron": cron_name, "result": res})

    # 新增 weekend worker：每 20 分钟执行一个 pending job
    worker_res = hb.cron_create_no_agent(
        script_name="lc_weekend_worker.sh",
        name=WEEKEND_WORKER_CRON_NAME,
        schedule=WEEKEND_DEFAULT_WORKER_SCHEDULE,
        workdir=str(PROJECT_ROOT),
        profile=HERMES_PROFILE,
    )
    created.append({"job": "weekend_worker", "cron": WEEKEND_WORKER_CRON_NAME, "result": worker_res})

    return {"success": True, "created": created}

def teardown_weekend_crontab(self) -> Dict[str, Any]:
    """卸载所有 lc-weekend- 开头的 cron。"""
    removed = []
    for cron in self.list_lifecycle_crons():
        name = cron.get("name", "")
        if name.startswith("lc-weekend-"):
            res = hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
            if res.get("success"):
                removed.append(name)
    return {"success": True, "removed": removed}

def teardown_cron_framework(self) -> Dict[str, Any]:
    """卸载所有 lc- 开头的 lifecycle cron（含周末任务）。"""
    removed = []
    for cron in self.list_lifecycle_crons():
        res = hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
        if res.get("success"):
            removed.append(cron.get("name"))
    return {"success": True, "removed": removed}