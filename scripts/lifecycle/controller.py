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
    STEP_GAP_IDENTIFY,
    STEP_IDEA_REVIEW,
    STEP_LIT_NOTE,
    STEP_LIT_READ,
    STEP_LIT_SEARCH,
    STEP_MONITOR,
    STEP_UPDATE_METHOD_MANUAL,
    STEP_UPDATE_VISION,
    STEP_WRITER,
)
from .executor import (
    pick_next_job,
    _update_job,
    _read_critic_report,
    _salvage_critic_report,
    _run_critic_step,
    _insert_researcher_pipeline,
    _run_gap_identify_step,
    _run_lit_search_step,
    _run_lit_read_step,
    _run_lit_note_step,
    _run_researcher_step,
    _run_writer_step,
    _run_monitor_step,
    _run_update_vision_step,
    _run_update_method_manual_step,
    _manual_two_phase_update,
    _run_manual_critic_step,
    _run_manual_writer_step,
    _parse_manual_plan,
    _run_idea_review_step,
    execute_job,
    execute_next_job,
    _mark_degradation,
)
from .framework import (
    cleanup_cron_duplicates,
    setup_cron_framework,
    setup_weekend_crontab,
    teardown_weekend_crontab,
    teardown_cron_framework,
)
from .micro_scheduler import (
    _auto_retry_failed_jobs,
    _check_r1_start_failures,
    _current_focus_slot,
    _focus_proposal_for_slot,
    _generate_round_report,
    _get_current_day_key,
    _has_any_ready_or_failed_job,
    _is_proposal_stuck,
    _is_round_complete,
    _job_priority_key,
    _list_ready_jobs_for_proposal,
    _load_focus_slots,
    _load_focus_state,
    _refresh_stale_jobs,
    _save_focus_state,
    _sync_lifecycle_to_task_manager,
    _sync_previous_rounds_to_task_manager,
    _update_kanban,
    get_current_focus,
    pause_old_worker_crons,
    remove_micro_scheduler,
    run_micro_scheduler,
    schedule_micro_scheduler,
)

# v7.3.55: 并行试点 side-worker（独立模块，与 micro_scheduler 解耦）
from .side_worker import run_side_worker
from .orchestrator import (
    _cleanup_old_round_jobs,
    _check_monitor_heartbeat,
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

        prompt_optimize = """#!/bin/bash
set -e
cd {project}
python3 scripts/prompt_optimizer.py auto
""".format(project=project)

        # v6.9.99（T2）撤除 lc_retrospective.sh wrapper——复盘由周日反思链内
        # reflection_link_deep_review job 复用 retrospective.run_retrospective 执行。

        weekend_summary = """#!/bin/bash
set -e
cd {project}
# v6.9.99（T2）周末收尾汇总（周日 22:00）：零 LLM 汇总本周末全链路产出
# （消化轮次/篇数、簇数、路由分布、校准 high 数、方法页变动），
# 写 memory/weekend-summary-{{date}}.md。
python3 scripts/weekend_summary.py
""".format(project=project)

        kb_distill_sunday = """#!/bin/bash
cd {project}
# v6.9.99（T2）周日蒸馏小批（20:00）：固定 --batch 8，与每日 12:50 主档
# （lc-kb-distill --auto 自适应档）互不干扰——主档按积压 5/10/20 篇升降档，
# 本档恒定小批在周末窗口额外消化。不用 set -e：单篇失败不阻断
# （kb_distill 内部保证单篇失败跳过不中断）。
python3 scripts/kb_distill.py --batch 8
# 小批蒸馏后补边（与每日主档链一致，幂等零 LLM），防新页成图谱孤岛
python3 scripts/kb_linker.py --apply
exit 0
""".format(project=project)

        kb_sync = """#!/bin/bash
set -e
cd {project}
# v6.8.51 每日知识库治理（12:40，上午时段结束后）：
# 1) sync_all：hermes 会话/简报/PDF 同步 + 索引重建(v2) + 图谱重建
# 2) growth_engine --apply：growth_stage 自动晋升（seedling→growing→mature）
#    （此前无任何调用方，127/233 节点卡 seedling；纯规则无 LLM 成本）
python3 scripts/kb_auto_sync.py
python3 scripts/growth_engine.py --apply
""".format(project=project)

        kb_distill = """#!/bin/bash
cd {project}
# v6.9.5 每日 raw→wiki 蒸馏（12:50，lc-kb-sync 之后）：
# distill_raw_to_wiki/save_distilled_wiki 接口自 v3.x 存在但无流水线
# 生产者，351 项 raw 积压零消化。本任务按最旧优先蒸馏。
# v6.9.38: 固定 --batch 5 改 --auto——积压 >300 时 5 篇/天追不上日增
# 40+ 的进料速度（08-22 实测 347 项连续 46 次告警不收敛），自适应升档
# 20 篇/天追赶，积压回落 <150 后自动降回 5 篇。
# 注意：不用 set -e——单篇失败（批次退出码非零）不应阻断 growth 晋升
# 等后续逻辑，kb_distill 内部已保证单篇失败跳过不中断。
python3 scripts/kb_distill.py --auto
# v6.9.6 蒸馏后立即补边（kb_linker 关键词匹配，零 LLM 成本）：
# 新蒸馏页若无 related 边会成为图谱孤岛（连通度 0.45 已低于告警线
# 0.50）。实测一次可补 84 页/185 边。幂等：补过即不再缺。
python3 scripts/kb_linker.py --apply
exit 0
""".format(project=project)

        # v6.9.62: 备份与日终同步 wrapper——此前仅在 manifest 登记、由手工
        # 实例存在（teardown+setup 后永久消失，R2 安装闭环缺口），补齐生成。
        daily_backup = """#!/bin/bash
cd {project}
# v6.9.54 每日用户数据备份（24h 幂等防重 + 轮转保留最近 7 份）。
# v6.9.62: 03:17→13:00（R4）——避开 00:30-03:30 worker 时段（zip 打包
# 860MB 期间并发写可使 zf.write 抛 FileNotFoundError 致当日备份静默跳过）
# 与 12:40/12:50 知识库任务链。
python3 scripts/backup_manager.py --daily
exit 0
""".format(project=project)

        daily_sync = """#!/bin/bash
cd {project}
# v6.9.58 每日 23:00 日终同步 hermes 产出→知识库（与 12:40 kb-sync
# 各覆盖半天进料）。
python3 scripts/sync_engine.py
exit 0
""".format(project=project)

        # v7.2.57 评审团宿主：消费 panel_review_requested 队列（P0-1 停摆
        # 根因残余——此前无 cron 宿主，标志积压时主链自动轮转冻结）。
        # v7.2.97 起行为随执行器配置走（memory/config/panel-executor.json，
        # 默认 engine）：engine = 任务包发射器（不调 LLM、不改文件、幂等，
        # 任何 agent 入口按包 + skill 契约亲审，完成后 --adopt-engine 收尾）；
        # hermes（显式 opt-in）= 无人值守托底执行器。
        # 不用 set -e：panel_review --run-all 逐课题容错（v7.2.57），
        # python 退出码不阻断收尾。
        panel_review = """#!/bin/bash
cd {project}
# 每天 10:00 评审团队列消费（队列空时零成本退出；engine 模式=发射任务包）
python3 scripts/panel_review.py --run-all
exit 0
""".format(project=project)

        return {
            "orchestrate": _write_wrapper_script("lc_orchestrate.sh", orchestrate),
            "repair": _write_wrapper_script("lc_repair.sh", repair),
            "worker": _write_wrapper_script("lc_worker.sh", worker),
            "weekend_input": _write_wrapper_script("lc_weekend_input.sh", weekend_input),
            "weekend_output": _write_wrapper_script("lc_weekend_output.sh", weekend_output),
            "weekend_reflection": _write_wrapper_script("lc_weekend_reflection.sh", weekend_reflection),
            "weekend_worker": _write_wrapper_script("lc_weekend_worker.sh", weekend_worker),
            "prompt_optimize": _write_wrapper_script("lc_prompt_optimize.sh", prompt_optimize),
            # v6.9.99（T2）：weekend_summary（setup_weekend_crontab 的
            # cron_specs 按 lc_{job_key}.sh 约定引用）+ 周日蒸馏小批；
            # retrospective wrapper 已随 lc-retrospective cron 撤除。
            "weekend_summary": _write_wrapper_script("lc_weekend_summary.sh", weekend_summary),
            "kb_distill_sunday": _write_wrapper_script("lc_kb_distill_sunday.sh", kb_distill_sunday),
            "kb_sync": _write_wrapper_script("lc_kb_sync.sh", kb_sync),
            "kb_distill": _write_wrapper_script("lc_kb_distill.sh", kb_distill),
            "daily_backup": _write_wrapper_script("lc_daily_backup.sh", daily_backup),
            "daily_sync": _write_wrapper_script("lc_daily_sync.sh", daily_sync),
            # v7.2.57: 评审团宿主 wrapper（setup_cron_framework 消费）
            "panel_review": _write_wrapper_script("lc_panel_review.sh", panel_review),
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

    def _build_full_round_jobs(
        self,
        proposal_id: str,
        round_num: int,
    ) -> List[Dict[str, Any]]:
        """v6.8.0: 为下一轮生成完整申请书优化链（v7.3.0 起 26 个常规 job）。

        模块顺序：rationale → content → scheme → full_review → references
                  → method_manual → monitor → derived(update_vision)
        其中 rationale/content/scheme 各包含 critic + 4 个 researcher 子任务 + writer。

        v7.3.0: 方法手册（method_manual）从轮末 derived 维护步升级为第六评审
        模块——references 之后插入 manual critic → manual writer（两阶段升级）
        对抗链，monitor 依赖 manual writer。手册未过线（section_passes 为
        False 或无记录）时每轮必跑；过线后与正文章节同规则跳过、强制复检轮
        （round_num % 3 == 0）全量重建。旧 derived update_method_manual job
        撤除（其两阶段机制由 manual writer 步继承）。

        v6.10.41: 已通过章节跳过——section_passes 为 True 的正文章节不再
        无条件重跑完整对抗链（旧实现每轮固定 25 job / ~34 个 LLM 会话，
        后期轮次多数章节早已达标，纯重复消耗）。规则：
        - 常规轮：跳过已通过章节，依赖链自动重接（后续章节 critic 依赖
          最近一个未跳过章节的 writer；全跳过时回落 idea_review/无依赖）；
        - 强制复检轮（round_num % 3 == 0）：全量构建——防止 full_review/
          references 修订造成的跨章影响长期不被复检，也周期性校准分数；
        - 跳过的章节 section_passes 保持 True 不动，完成判定（completion）
          语义不变。
        """
        from proposal_sections import PROPOSAL_SECTIONS, MANUAL_SECTION_KEY

        def _job(section_key: str, step: str, depends_on: List[str]) -> Dict[str, Any]:
            return {
                "job_id": _make_job_id(proposal_id, round_num, section_key, step),
                "proposal_id": proposal_id,
                "step": step,
                "section_key": section_key,
                "round": round_num,
                "status": JOB_STATUS_PENDING,
                "depends_on": depends_on,
                "attempts": 0,
                "scheduled_at": "",
                "started_at": "",
                "finished_at": "",
                "last_error": "",
                "cron_job_id": "",
            }

        jobs: List[Dict[str, Any]] = []
        prev_writer_id = ""

        # v6.8.26: 第 1 轮或 monitor 检测到结构性缺陷时前置研究设想评审
        # v6.8.27 修复: 如果 idea_review 已通过（idea_review_passed=True），
        # 退回后不重跑——只在结构性缺陷标志触发时才重新评审
        idea_review_id = ""
        prop_state = self._get_proposal_state(proposal_id)
        need_idea_review = (
            (round_num <= 1 and not (prop_state and prop_state.get("idea_review_passed")))
            or (prop_state and prop_state.get("idea_review_required"))
        )
        if need_idea_review:
            idea_review_id = _make_job_id(proposal_id, round_num, "idea_review", STEP_IDEA_REVIEW)
            jobs.append(_job("idea_review", STEP_IDEA_REVIEW, []))
            # 后续第一个 critic 将依赖此 job
            # 清除标志位（本轮 idea_review 会重新评估）
            if prop_state and prop_state.get("idea_review_required"):
                prop_state["idea_review_required"] = False
                self._set_proposal_state(proposal_id, prop_state)

        # 3 个主模块：每个 critic + 4 researcher + writer
        # v6.10.41: 已通过章节跳过（详见 docstring）——常规轮跳过
        # section_passes=True 的章节，强制复检轮（round_num % 3 == 0）
        # 全量构建。prev_writer_id 不更新即完成依赖重接。
        _section_passes = (prop_state or {}).get("section_passes", {}) or {}
        _force_recheck = (round_num % 3 == 0)
        _skipped_sections: List[str] = []
        for section in PROPOSAL_SECTIONS[:3]:
            section_key = section["key"]
            if not _force_recheck and _section_passes.get(section_key):
                _skipped_sections.append(section_key)
                if _log:
                    _next_recheck = (round_num // 3 + 1) * 3
                    _log.info(
                        f"[{proposal_id}] r{round_num} 跳过已通过章节 {section_key}"
                        f"（下次强制复检轮 r{_next_recheck}）"
                    )
                continue
            critic_id = _make_job_id(proposal_id, round_num, section_key, STEP_CRITIC)
            gap_id = _make_job_id(proposal_id, round_num, section_key, STEP_GAP_IDENTIFY)
            search_id = _make_job_id(proposal_id, round_num, section_key, STEP_LIT_SEARCH)
            read_id = _make_job_id(proposal_id, round_num, section_key, STEP_LIT_READ)
            note_id = _make_job_id(proposal_id, round_num, section_key, STEP_LIT_NOTE)
            writer_id = _make_job_id(proposal_id, round_num, section_key, STEP_WRITER)

            # critic 依赖上一模块的 writer（第 1 轮还依赖 idea_review）
            critic_deps = []
            if prev_writer_id:
                critic_deps.append(prev_writer_id)
            if idea_review_id:
                critic_deps.append(idea_review_id)
            jobs.append(_job(section_key, STEP_CRITIC, critic_deps))
            jobs.append(_job(section_key, STEP_GAP_IDENTIFY, [critic_id]))
            jobs.append(_job(section_key, STEP_LIT_SEARCH, [gap_id]))
            jobs.append(_job(section_key, STEP_LIT_READ, [search_id]))
            jobs.append(_job(section_key, STEP_LIT_NOTE, [read_id]))
            jobs.append(_job(section_key, STEP_WRITER, [critic_id, note_id]))

            prev_writer_id = writer_id

        if _skipped_sections and _log:
            _log.info(
                f"[{proposal_id}] r{round_num} 跳过已通过章节: "
                f"{','.join(_skipped_sections)}（节省 {6 * len(_skipped_sections)} job）"
            )

        # full_review: critic → writer
        # v6.10.41: 全部正文章节被跳过时，full_review critic 依赖回落到
        # idea_review（若有）或无依赖（round 1 无 idea_review 的边角场景）。
        full_key = "full_review"
        full_critic_id = _make_job_id(proposal_id, round_num, full_key, STEP_CRITIC)
        full_writer_id = _make_job_id(proposal_id, round_num, full_key, STEP_WRITER)
        _full_critic_deps = [prev_writer_id] if prev_writer_id else (
            [idea_review_id] if idea_review_id else []
        )
        jobs.append(_job(full_key, STEP_CRITIC, _full_critic_deps))
        jobs.append(_job(full_key, STEP_WRITER, [full_critic_id]))

        # references: critic → writer
        ref_key = "references"
        ref_critic_id = _make_job_id(proposal_id, round_num, ref_key, STEP_CRITIC)
        ref_writer_id = _make_job_id(proposal_id, round_num, ref_key, STEP_WRITER)
        jobs.append(_job(ref_key, STEP_CRITIC, [full_writer_id]))
        jobs.append(_job(ref_key, STEP_WRITER, [ref_critic_id]))

        # v7.3.0: method_manual（方法手册第六评审模块）: critic → 两阶段升级 writer。
        # 跳过规则与正文章节一致（过线后常规轮跳过，强制复检轮全量）；
        # 跳过时依赖重接——monitor 依赖 references writer。
        _manual_passed = bool(_section_passes.get(MANUAL_SECTION_KEY))
        if _force_recheck or not _manual_passed:
            manual_critic_id = _make_job_id(proposal_id, round_num, MANUAL_SECTION_KEY, STEP_CRITIC)
            manual_writer_id = _make_job_id(proposal_id, round_num, MANUAL_SECTION_KEY, STEP_WRITER)
            jobs.append(_job(MANUAL_SECTION_KEY, STEP_CRITIC, [ref_writer_id]))
            jobs.append(_job(MANUAL_SECTION_KEY, STEP_WRITER, [manual_critic_id]))
            monitor_dep_id = manual_writer_id
        else:
            if _log:
                _next_recheck = (round_num // 3 + 1) * 3
                _log.info(
                    f"[{proposal_id}] r{round_num} 跳过已通过模块 {MANUAL_SECTION_KEY}"
                    f"（下次强制复检轮 r{_next_recheck}）"
                )
            monitor_dep_id = ref_writer_id

        # monitor（全局监察，独立 section_key；v7.3.0 起依赖手册 writer）
        monitor_id = _make_job_id(proposal_id, round_num, "monitor", STEP_MONITOR)
        jobs.append(_job("monitor", STEP_MONITOR, [monitor_dep_id]))

        # 衍生更新（v7.3.0: update_method_manual 已升级为正式模块 writer 步，
        # derived 链只剩 update_vision）
        vision_id = _make_job_id(proposal_id, round_num, "derived", STEP_UPDATE_VISION)
        jobs.append(_job("derived", STEP_UPDATE_VISION, [monitor_id]))

        return jobs

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
    _salvage_critic_report = _salvage_critic_report
    _run_critic_step = _run_critic_step
    _insert_researcher_pipeline = _insert_researcher_pipeline
    _run_gap_identify_step = _run_gap_identify_step
    _run_lit_search_step = _run_lit_search_step
    _run_lit_read_step = _run_lit_read_step
    _run_lit_note_step = _run_lit_note_step
    _run_researcher_step = _run_researcher_step
    _run_writer_step = _run_writer_step
    _run_monitor_step = _run_monitor_step
    _run_update_vision_step = _run_update_vision_step
    _run_update_method_manual_step = _run_update_method_manual_step
    _manual_two_phase_update = _manual_two_phase_update
    _run_manual_critic_step = _run_manual_critic_step
    _run_manual_writer_step = _run_manual_writer_step
    _parse_manual_plan = _parse_manual_plan
    _run_idea_review_step = _run_idea_review_step
    _mark_degradation = _mark_degradation
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
    # v6.9.1: 补绑 monitor 心跳互查——run_repair 调用 self._check_monitor_heartbeat，
    # 但该函数自 v6.8.50 起未绑定到本类，repair 每 6h 触发 AttributeError，
    # 心跳互查机制上线以来从未生效（日志实证 2026-08-15T00:00:52Z）。
    _check_monitor_heartbeat = _check_monitor_heartbeat
    sync_checkpoint = sync_checkpoint
    run_orchestrator = run_orchestrator
    run_repair = run_repair
    _run_weekend_repair = _run_weekend_repair
    run_health_check = run_health_check

    # ------------------------------------------------------------------
    # 微调度器（从 micro_scheduler 模块绑定为方法）
    # ------------------------------------------------------------------
    _auto_retry_failed_jobs = _auto_retry_failed_jobs
    _current_focus_slot = _current_focus_slot
    # v7.2.1 修复：v7.1.8 漏绑定为方法——run_micro_scheduler 内
    # self._check_r1_start_failures() 每次抛 AttributeError 被 except
    # 静默吞掉（仅 DEBUG 日志），r1 启动失败检测自上线起从未生效
    _check_r1_start_failures = _check_r1_start_failures
    _focus_proposal_for_slot = _focus_proposal_for_slot
    _generate_round_report = _generate_round_report
    _get_current_day_key = _get_current_day_key
    _has_any_ready_or_failed_job = _has_any_ready_or_failed_job
    _is_proposal_stuck = _is_proposal_stuck
    _is_round_complete = _is_round_complete
    _job_priority_key = _job_priority_key
    _list_ready_jobs_for_proposal = _list_ready_jobs_for_proposal
    _load_focus_slots = _load_focus_slots
    _load_focus_state = _load_focus_state
    _refresh_stale_jobs = _refresh_stale_jobs
    _save_focus_state = _save_focus_state
    _update_kanban = _update_kanban
    run_micro_scheduler = run_micro_scheduler
    run_side_worker = run_side_worker
    schedule_micro_scheduler = schedule_micro_scheduler
    remove_micro_scheduler = remove_micro_scheduler
    pause_old_worker_crons = pause_old_worker_crons
    get_current_focus = get_current_focus
    sync_lifecycle_to_task_manager = _sync_lifecycle_to_task_manager
    sync_lifecycle_history_tasks = _sync_previous_rounds_to_task_manager

    # ------------------------------------------------------------------
    # 安装 / 卸载（从 framework 模块绑定为方法）
    # ------------------------------------------------------------------
    cleanup_cron_duplicates = cleanup_cron_duplicates
    setup_cron_framework = setup_cron_framework
    setup_weekend_crontab = setup_weekend_crontab
    teardown_weekend_crontab = teardown_weekend_crontab
    teardown_cron_framework = teardown_cron_framework



def get_controller() -> LifecycleCronController:
    return LifecycleCronController()
