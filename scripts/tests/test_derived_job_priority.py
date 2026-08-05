#!/usr/bin/env python3
"""
test_derived_job_priority.py — Derived job 优先级回归测试

验证缺陷 fix13 (v6.8.3):
    _CHAIN_ORDER 字典缺少 STEP_UPDATE_VISION / STEP_UPDATE_METHOD_MANUAL，
    导致它们的优先级默认为 99（最低）。当本轮 derived job 仍 pending 时，
    如果 sync_checkpoint 已创建下一轮 job（因 optimization_rounds 被推进），
    下一轮的 critic（优先级 0）会抢占本轮 derived job 的执行时机，
    导致：
    1. 本轮永远不会被检测为完成（derived job 未执行）
    2. 优化报告不生成
    3. 实际执行顺序混乱：下一轮 critic → 本轮 derived → 检测完成 → 报告

验证点：
    1. _CHAIN_ORDER 包含 STEP_UPDATE_VISION 和 STEP_UPDATE_METHOD_MANUAL
    2. derived job 优先级 < 默认值 99
    3. derived job 优先级 > monitor（确保在 monitor 之后执行）
    4. 当 derived job 和下一轮 critic 同时 pending 时，derived job 优先被选中
    5. 完整场景：derived job 执行后轮次完成，报告正确生成
"""

import sys
import json
import shutil
import importlib
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from test_runner import TestSuite, create_isolated_env, patch_module_root


def _make_job(pid, round_num, section_key, step, status="pending",
              started_at="", depends_on=None):
    """构造单个 pipeline job 字典。"""
    return {
        "job_id": f"{pid}-r{round_num}-{section_key}-{step}",
        "proposal_id": pid,
        "step": step,
        "section_key": section_key,
        "round": round_num,
        "status": status,
        "depends_on": depends_on or [],
        "attempts": 0,
        "scheduled_at": "",
        "started_at": started_at,
        "finished_at": "",
        "last_error": "",
        "cron_job_id": "",
    }


class DerivedJobPriorityTests(TestSuite):
    def __init__(self):
        super().__init__("Derived job 优先级回归测试")
        self.tmp_root = None
        self.ms = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / "optimizing" / sub).mkdir(
                parents=True, exist_ok=True
            )
        # 创建 proposal 目录结构（_is_round_complete 的产物检查需要）
        pid = "general-test-alpha-20260101"
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / pid / "04_proposal" / "sections"
        prop_dir.mkdir(parents=True, exist_ok=True)
        for sec in ["rationale.md", "content.md", "scheme.md", "full_review.md", "references.md"]:
            (prop_dir / sec).write_text("# " + sec + "\n\n" + "x" * 100, encoding="utf-8")

        for mod_name in list(sys.modules.keys()):
            if "micro_scheduler" in mod_name or mod_name in [
                "lifecycle", "paths", "common", "proposal_lifecycle",
                "proposal_sections",
            ]:
                del sys.modules[mod_name]

        self.ms = importlib.import_module("lifecycle.micro_scheduler")
        patch_module_root("lifecycle.micro_scheduler", self.tmp_root)
        import paths
        paths.PROJECT_ROOT = self.tmp_root

        self.pid = pid

        # Patch _is_round_complete 使用 tmp_root 路径
        tmp_root = self.tmp_root

        def _patched_is_round_complete(jobs, proposal_id, round_num):
            """使用 tmp_root 的 _is_round_complete 包装。"""
            round_jobs = [j for j in jobs if j.get("round") == round_num]
            if not round_jobs:
                return False
            if not all(j.get("status") == "done" for j in round_jobs):
                return False
            prop_dir = tmp_root / "research_proposals" / "optimizing" / proposal_id / "04_proposal"
            for sec in ["rationale.md", "content.md", "scheme.md", "full_review.md", "references.md"]:
                sec_path = prop_dir / "sections" / sec
                if not sec_path.exists() or sec_path.stat().st_size < 50:
                    return False
            return True

        self.ms._is_round_complete = _patched_is_round_complete

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _build_complete_round_jobs(self, pid, round_num):
        """构建一轮完整的 25 个 job（全部 done 状态）。"""
        jobs = []
        prev_writer_id = ""

        sections = [
            ("rationale", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("content", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("scheme", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("full_review", ["critic", "writer"]),
            ("references", ["critic", "writer"]),
        ]

        for sec_key, steps in sections:
            for step in steps:
                job = _make_job(pid, round_num, sec_key, step, status="done")
                if step == "critic" and prev_writer_id:
                    job["depends_on"] = [prev_writer_id]
                jobs.append(job)
                if step == "writer":
                    prev_writer_id = job["job_id"]

        # monitor
        monitor_job = _make_job(pid, round_num, "monitor", "monitor", status="done")
        monitor_job["depends_on"] = [prev_writer_id]
        jobs.append(monitor_job)

        # derived
        vision_job = _make_job(pid, round_num, "derived", "update_vision", status="done")
        vision_job["depends_on"] = [monitor_job["job_id"]]
        jobs.append(vision_job)

        manual_job = _make_job(pid, round_num, "derived", "update_method_manual", status="done")
        manual_job["depends_on"] = [vision_job["job_id"]]
        jobs.append(manual_job)

        return jobs

    def _make_mock_controller(self, proposals_config):
        """创建模拟控制器。"""
        ctrl = MagicMock()

        def _get_jobs(pid):
            return proposals_config.get(pid, {}).get("jobs", [])

        def _save_jobs(pid, jobs):
            proposals_config[pid]["jobs"] = jobs
            return True

        def _get_proposal_state(pid):
            return proposals_config.get(pid, {}).get("state", {})

        def _set_proposal_state(pid, state):
            proposals_config[pid]["state"] = state
            return True

        ctrl._get_jobs.side_effect = _get_jobs
        ctrl._save_jobs.side_effect = _save_jobs
        ctrl._get_proposal_state.side_effect = _get_proposal_state
        ctrl._set_proposal_state.side_effect = _set_proposal_state
        ctrl._is_proposal_stuck.return_value = False
        ctrl.list_by_status.return_value = [
            {"proposal_id": pid} for pid in proposals_config
        ]

        # 模拟 execute_job：标记 job 为 done
        def _execute_job(job):
            job["status"] = "done"
            job["finished_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            return {"success": True, "job_id": job["job_id"]}

        ctrl.execute_job.side_effect = _execute_job
        return ctrl

    def _setup_focus_state(self, queue, last_slot_index=0, last_proposal_index=0):
        """写入 focus state 文件。"""
        state = {
            "last_slot_index": last_slot_index,
            "last_proposal_index": last_proposal_index,
            "last_proposal_id": queue[last_proposal_index] if queue else "",
            "queue": queue,
            "focus_history": [],
            "last_day_key": datetime.now().strftime("%Y-%m-%d"),
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        state_path = self.tmp_root / "memory" / "lifecycle-focus.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def run_tests(self):
        pid = self.pid
        slot_info = (3, ("18:30", "22:30"))

        # ================================================================
        # 测试 1: _CHAIN_ORDER 包含 derived 步骤
        # ================================================================
        from lifecycle.constants import STEP_UPDATE_VISION, STEP_UPDATE_METHOD_MANUAL, STEP_MONITOR

        self.assert_true(
            STEP_UPDATE_VISION in self.ms._CHAIN_ORDER,
            "_CHAIN_ORDER 必须包含 STEP_UPDATE_VISION",
            f"缺少 {STEP_UPDATE_VISION}，当前 _CHAIN_ORDER keys: {list(self.ms._CHAIN_ORDER.keys())}",
        )
        self.assert_true(
            STEP_UPDATE_METHOD_MANUAL in self.ms._CHAIN_ORDER,
            "_CHAIN_ORDER 必须包含 STEP_UPDATE_METHOD_MANUAL",
            f"缺少 {STEP_UPDATE_METHOD_MANUAL}，当前 _CHAIN_ORDER keys: {list(self.ms._CHAIN_ORDER.keys())}",
        )

        # ================================================================
        # 测试 2: derived job 优先级 < 默认值 99
        # ================================================================
        vision_priority = self.ms._CHAIN_ORDER.get(STEP_UPDATE_VISION, 99)
        manual_priority = self.ms._CHAIN_ORDER.get(STEP_UPDATE_METHOD_MANUAL, 99)

        self.assert_true(
            vision_priority < 99,
            "update_vision 优先级必须 < 99（默认最低值）",
            f"当前优先级: {vision_priority}",
        )
        self.assert_true(
            manual_priority < 99,
            "update_method_manual 优先级必须 < 99（默认最低值）",
            f"当前优先级: {manual_priority}",
        )

        # ================================================================
        # 测试 3: derived job 优先级 > monitor（确保在 monitor 之后执行）
        # ================================================================
        monitor_priority = self.ms._CHAIN_ORDER.get(STEP_MONITOR, 99)

        self.assert_true(
            vision_priority > monitor_priority,
            "update_vision 优先级应 > monitor（确保 monitor 先执行）",
            f"monitor={monitor_priority}, update_vision={vision_priority}",
        )
        self.assert_true(
            manual_priority > vision_priority,
            "update_method_manual 优先级应 > update_vision（确保 vision 先执行）",
            f"update_vision={vision_priority}, update_method_manual={manual_priority}",
        )

        # ================================================================
        # 测试 4（核心回归）: derived job 优先于下一轮 critic 被选中
        # bug 现场: R6 的 derived job pending，R7 的 critic 也 pending，
        #           critic 优先级 0 < derived 优先级 99，critic 被先执行
        # 修复: derived 优先级 7/8 < 99，但仍 > critic 的 0
        #       但 derived 属于当前轮次，应先完成当前轮次再开下一轮
        # ================================================================
        # 构建 R6 的 25 个 job，除 update_vision 外全部 done
        r6_jobs = self._build_complete_round_jobs(pid, 6)
        # update_vision 设为 pending
        vision_job_idx = next(i for i, j in enumerate(r6_jobs) if j["step"] == "update_vision")
        r6_jobs[vision_job_idx]["status"] = "pending"
        # update_method_manual 依赖 update_vision，也 pending
        manual_job_idx = next(i for i, j in enumerate(r6_jobs) if j["step"] == "update_method_manual")
        r6_jobs[manual_job_idx]["status"] = "pending"

        # 模拟 sync_checkpoint 已创建 R7 的 critic（optimization_rounds 被推进到 6）
        r7_critic = _make_job(pid, 7, "rationale", "critic", status="pending")
        r6_jobs.append(r7_critic)

        proposals_config = {
            pid: {
                "jobs": r6_jobs,
                "state": {
                    "status": "optimizing",
                    "optimization_rounds": 6,  # 已推进到 6，next_round=7
                    "last_score": 0.70,
                    "score_history": [],
                    "project_type": "general",
                },
            },
        }
        ctrl = self._make_mock_controller(proposals_config)

        # 模拟 _list_ready_jobs_for_proposal 使用真实的 _job_priority_key
        def _list_ready(pid):
            jobs = ctrl._get_jobs(pid)
            done_ids = {j["job_id"] for j in jobs if j.get("status") == "done"}
            ready = []
            for job in jobs:
                if job.get("status") != "pending":
                    continue
                deps = job.get("depends_on", [])
                if all(d in done_ids for d in deps):
                    priority = self.ms._job_priority_key(ctrl, pid, job)
                    ready.append({"proposal_id": pid, "job": job, "priority": priority})
            ready.sort(key=lambda x: x["priority"])
            return ready

        ctrl._list_ready_jobs_for_proposal.side_effect = _list_ready
        # sync_checkpoint 不做任何事（已手动创建 R7 critic）
        ctrl.sync_checkpoint.return_value = {"success": True, "added": 0}
        ctrl._build_full_round_jobs = lambda pid, rn: self._build_complete_round_jobs(pid, rn)

        executed_jobs = []

        def _execute_and_track(job):
            job["status"] = "done"
            job["finished_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            executed_jobs.append(job["job_id"])
            return {"success": True, "job_id": job["job_id"]}

        ctrl.execute_job.side_effect = _execute_and_track

        with patch.object(self.ms, "_current_focus_slot", return_value=slot_info), \
             patch.object(self.ms, "_check_and_transition", return_value=None), \
             patch.object(self.ms, "_generate_round_report", return_value=None), \
             patch.object(self.ms, "_update_kanban"):
            self._setup_focus_state([pid], last_slot_index=3, last_proposal_index=0)
            ctrl._focus_proposal_for_slot = lambda slot_idx, opt: self.ms._focus_proposal_for_slot(
                ctrl, slot_idx, opt
            )

            result = self.ms.run_micro_scheduler(ctrl, max_jobs=5)

        # 验证第一个执行的 job 是 update_vision（不是 R7 的 critic）
        self.assert_true(
            len(executed_jobs) > 0,
            "应至少执行一个 job",
            f"executed_jobs={executed_jobs}",
        )
        self.assert_true(
            "update_vision" in executed_jobs[0],
            f"第一个执行的应是 update_vision，实际: {executed_jobs[0]}",
            f"executed_jobs={executed_jobs}",
        )

        # ================================================================
        # 测试 5: 完整场景 — derived job 执行后轮次完成，报告正确生成
        # ================================================================
        r1_jobs = self._build_complete_round_jobs(pid, 1)
        # update_vision 设为 pending
        vision_idx = next(i for i, j in enumerate(r1_jobs) if j["step"] == "update_vision")
        r1_jobs[vision_idx]["status"] = "pending"
        # update_method_manual 也 pending（依赖 vision）
        manual_idx = next(i for i, j in enumerate(r1_jobs) if j["step"] == "update_method_manual")
        r1_jobs[manual_idx]["status"] = "pending"

        proposals_config_2 = {
            pid: {
                "jobs": r1_jobs,
                "state": {
                    "status": "optimizing",
                    "optimization_rounds": 0,
                    "last_score": 0.75,
                    "score_history": [{"round": 1, "score": 0.75, "dim_scores": {}}],
                    "project_type": "general",
                },
            },
        }
        ctrl2 = self._make_mock_controller(proposals_config_2)

        report_generated = [False]

        def _list_ready_2(pid_arg):
            jobs = ctrl2._get_jobs(pid_arg)
            done_ids = {j["job_id"] for j in jobs if j.get("status") == "done"}
            ready = []
            for job in jobs:
                if job.get("status") != "pending":
                    continue
                deps = job.get("depends_on", [])
                if all(d in done_ids for d in deps):
                    priority = self.ms._job_priority_key(ctrl2, pid_arg, job)
                    ready.append({"proposal_id": pid_arg, "job": job, "priority": priority})
            ready.sort(key=lambda x: x["priority"])
            return ready

        ctrl2._list_ready_jobs_for_proposal.side_effect = _list_ready_2
        ctrl2.sync_checkpoint.return_value = {"success": True, "added": 0}
        ctrl2._build_full_round_jobs = lambda pid_arg, rn: self._build_complete_round_jobs(pid_arg, rn)

        def _generate_report(self_arg, proposal_id, round_num):
            report_generated[0] = True
            return f"/tmp/report-r{round_num}.md"

        executed_jobs_2 = []

        def _execute_and_track_2(job):
            job["status"] = "done"
            job["finished_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            executed_jobs_2.append(job["step"])
            return {"success": True, "job_id": job["job_id"]}

        ctrl2.execute_job.side_effect = _execute_and_track_2

        with patch.object(self.ms, "_current_focus_slot", return_value=slot_info), \
             patch.object(self.ms, "_check_and_transition", return_value=None), \
             patch.object(self.ms, "_generate_round_report", side_effect=_generate_report), \
             patch.object(self.ms, "_update_kanban"):
            self._setup_focus_state([pid], last_slot_index=3, last_proposal_index=0)
            ctrl2._focus_proposal_for_slot = lambda slot_idx, opt: self.ms._focus_proposal_for_slot(
                ctrl2, slot_idx, opt
            )

            result2 = self.ms.run_micro_scheduler(ctrl2, max_jobs=5)

        # 验证两个 derived job 都被执行
        self.assert_true(
            "update_vision" in executed_jobs_2,
            "update_vision 应被执行",
            f"executed_jobs_2={executed_jobs_2}",
        )
        self.assert_true(
            "update_method_manual" in executed_jobs_2,
            "update_method_manual 应被执行",
            f"executed_jobs_2={executed_jobs_2}",
        )

        # 验证执行顺序：update_vision 在 update_method_manual 之前
        vision_pos = executed_jobs_2.index("update_vision")
        manual_pos = executed_jobs_2.index("update_method_manual")
        self.assert_true(
            vision_pos < manual_pos,
            "update_vision 应在 update_method_manual 之前执行",
            f"vision_pos={vision_pos}, manual_pos={manual_pos}",
        )

        # 验证报告被生成
        self.assert_true(
            report_generated[0],
            "轮次完成后应生成优化报告",
            "报告未生成",
        )

        # 验证 optimization_rounds 被递增
        final_state = proposals_config_2[pid]["state"]
        self.assert_eq(
            final_state.get("optimization_rounds"), 1,
            "轮次完成后 optimization_rounds 应递增到 1",
        )
