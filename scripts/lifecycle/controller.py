#!/usr/bin/env python3
"""生命周期 cron 控制器：组合各子模块能力。"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保 scripts/ 在路径中（controller 位于 scripts/lifecycle/ 下）
_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT
from proposal_lifecycle import (
    ProposalLifecycle,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_NO_IMPROVEMENT_LIMIT,
)
from proposal_sections import PROPOSAL_SECTIONS

from .constants import (
    HERMES_SCRIPTS_DIR,
    HERMES_PROFILE,
    JOB_STATUS_PENDING,
    STEP_CRITIC,
    STEP_MONITOR,
    STEP_WRITER,
)
from .executor import (
    pick_next_job,
    _update_job,
    _read_critic_report,
    _run_critic_step,
    _insert_researcher_pipeline,
    _run_gap_identify_step,
    _run_lit_search_step,
    _run_lit_read_step,
    _run_lit_note_step,
    _run_researcher_step,
    _run_writer_step,
    _run_monitor_step,
    execute_job,
    execute_next_job,
)
from .framework import (
    setup_cron_framework,
    setup_weekend_crontab,
    teardown_weekend_crontab,
    teardown_cron_framework,
)
from .micro_scheduler import (
    _job_priority_key,
    _list_ready_jobs,
    _refresh_stale_jobs,
    pause_old_worker_crons,
    remove_micro_scheduler,
    run_micro_scheduler,
    schedule_micro_scheduler,
)
from .orchestrator import (
    _compute_actual_round,
    sync_checkpoint,
    run_orchestrator,
    run_repair,
    _run_weekend_repair,
    run_health_check,
)
from .scheduler import (
    _lifecycle_cron_prefix,
    list_lifecycle_crons,
    _compute_worker_minute,
    schedule_worker,
    remove_worker,
)
from .utils import (
    _ensure_hermes_scripts_dir,
    _write_wrapper_script,
    _get_jobs,
    _save_jobs,
    _job_by_id,
    _make_job_id,
    _section_for_round,
)

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


class LifecycleCronController(ProposalLifecycle):
    """在 ProposalLifecycle 之上增加 checkpoint + cron 小型化调度能力。"""

    def _write_generic_wrappers(self) -> Dict[str, Path]:
        """生成 orchestrate / repair / worker / weekend 通用包装脚本。"""
        project = str(PROJECT_ROOT)
        orchestrate = """#!/bin/bash
set -e
cd {project}
python3 scripts/proposal_lifecycle.py --orchestrate
""".format(project=project)

        repair = """#!/bin/bash
set -e
cd {project}
python3 scripts/proposal_lifecycle.py --repair
""".format(project=project)

        worker = """#!/bin/bash
set -e
cd {project}
SCRIPT_NAME=$(basename "$0")
PID="${{SCRIPT_NAME#lc_worker_}}"
PID="${{PID%.sh}}"
python3 scripts/proposal_lifecycle.py --worker-step "$PID"
""".format(project=project)

        weekend_input = """#!/bin/bash
set -e
cd {project}
python3 scripts/weekend_orchestrator.py --input
""".format(project=project)

        weekend_output = """#!/bin/bash
set -e
cd {project}
python3 scripts/weekend_orchestrator.py --output
""".format(project=project)

        weekend_reflection = """#!/bin/bash
set -e
cd {project}
python3 scripts/weekend_orchestrator.py --reflection
""".format(project=project)

        weekend_worker = """#!/bin/bash
set -e
cd {project}
python3 scripts/weekend_pipeline.py --run-next
""".format(project=project)

        return {
            "orchestrate": _write_wrapper_script("lc_orchestrate.sh", orchestrate),
            "repair": _write_wrapper_script("lc_repair.sh", repair),
            "worker": _write_wrapper_script("lc_worker.sh", worker),
            "weekend_input": _write_wrapper_script("lc_weekend_input.sh", weekend_input),
            "weekend_output": _write_wrapper_script("lc_weekend_output.sh", weekend_output),
            "weekend_reflection": _write_wrapper_script("lc_weekend_reflection.sh", weekend_reflection),
            "weekend_worker": _write_wrapper_script("lc_weekend_worker.sh", weekend_worker),
        }

    def _worker_script_for_proposal(self, proposal_id: str) -> Path:
        """为具体 proposal 复制 worker 包装脚本（脚本名携带 proposal_id）。"""
        self._write_generic_wrappers()
        script_name = f"lc_worker_{proposal_id}.sh"
        target = HERMES_SCRIPTS_DIR / script_name
        source = HERMES_SCRIPTS_DIR / "lc_worker.sh"
        if not source.exists():
            self._write_generic_wrappers()
        shutil.copy2(source, target)
        target.chmod(0o755)
        return target

    def _build_next_round_jobs(
        self,
        proposal_id: str,
        round_num: int,
        section: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """为下一轮生成 critic + writer + monitor 三个基础 job。"""
        section_key = section["key"]
        critic_id = _make_job_id(proposal_id, round_num, section_key, STEP_CRITIC)
        writer_id = _make_job_id(proposal_id, round_num, section_key, STEP_WRITER)
        monitor_id = _make_job_id(proposal_id, round_num, section_key, STEP_MONITOR)
        return [
            {
                "job_id": critic_id,
                "proposal_id": proposal_id,
                "step": STEP_CRITIC,
                "section_key": section_key,
                "round": round_num,
                "status": JOB_STATUS_PENDING,
                "depends_on": [],
                "attempts": 0,
                "scheduled_at": "",
                "started_at": "",
                "finished_at": "",
                "last_error": "",
                "cron_job_id": "",
            },
            {
                "job_id": writer_id,
                "proposal_id": proposal_id,
                "step": STEP_WRITER,
                "section_key": section_key,
                "round": round_num,
                "status": JOB_STATUS_PENDING,
                "depends_on": [critic_id],
                "attempts": 0,
                "scheduled_at": "",
                "started_at": "",
                "finished_at": "",
                "last_error": "",
                "cron_job_id": "",
            },
            {
                "job_id": monitor_id,
                "proposal_id": proposal_id,
                "step": STEP_MONITOR,
                "section_key": section_key,
                "round": round_num,
                "status": JOB_STATUS_PENDING,
                "depends_on": [writer_id],
                "attempts": 0,
                "scheduled_at": "",
                "started_at": "",
                "finished_at": "",
                "last_error": "",
                "cron_job_id": "",
            },
        ]

    # ------------------------------------------------------------------
    # checkpoint 工具函数（从 utils 模块绑定为方法）
    # ------------------------------------------------------------------
    _get_jobs = _get_jobs
    _save_jobs = _save_jobs
    _job_by_id = _job_by_id

    # ------------------------------------------------------------------
    # 单步执行（从 executor 模块绑定为方法）
    # ------------------------------------------------------------------
    pick_next_job = pick_next_job
    _update_job = _update_job
    _read_critic_report = _read_critic_report
    _run_critic_step = _run_critic_step
    _insert_researcher_pipeline = _insert_researcher_pipeline
    _run_gap_identify_step = _run_gap_identify_step
    _run_lit_search_step = _run_lit_search_step
    _run_lit_read_step = _run_lit_read_step
    _run_lit_note_step = _run_lit_note_step
    _run_researcher_step = _run_researcher_step
    _run_writer_step = _run_writer_step
    _run_monitor_step = _run_monitor_step
    execute_job = execute_job
    execute_next_job = execute_next_job

    # ------------------------------------------------------------------
    # 调度层（从 scheduler 模块绑定为方法）
    # ------------------------------------------------------------------
    _lifecycle_cron_prefix = _lifecycle_cron_prefix
    list_lifecycle_crons = list_lifecycle_crons
    _compute_worker_minute = _compute_worker_minute
    schedule_worker = schedule_worker
    remove_worker = remove_worker

    # ------------------------------------------------------------------
    # 编排与修复（从 orchestrator 模块绑定为方法）
    # ------------------------------------------------------------------
    _compute_actual_round = _compute_actual_round
    sync_checkpoint = sync_checkpoint
    run_orchestrator = run_orchestrator
    run_repair = run_repair
    _run_weekend_repair = _run_weekend_repair
    run_health_check = run_health_check

    # ------------------------------------------------------------------
    # 微调度器（从 micro_scheduler 模块绑定为方法）
    # ------------------------------------------------------------------
    _refresh_stale_jobs = _refresh_stale_jobs
    _job_priority_key = _job_priority_key
    _list_ready_jobs = _list_ready_jobs
    run_micro_scheduler = run_micro_scheduler
    schedule_micro_scheduler = schedule_micro_scheduler
    remove_micro_scheduler = remove_micro_scheduler
    pause_old_worker_crons = pause_old_worker_crons

    # ------------------------------------------------------------------
    # 安装 / 卸载（从 framework 模块绑定为方法）
    # ------------------------------------------------------------------
    setup_cron_framework = setup_cron_framework
    setup_weekend_crontab = setup_weekend_crontab
    teardown_weekend_crontab = teardown_weekend_crontab
    teardown_cron_framework = teardown_cron_framework



def get_controller() -> LifecycleCronController:
    return LifecycleCronController()
