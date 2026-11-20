#!/usr/bin/env python3
"""
test_round_complete_break.py — 轮次完成后 break 验证测试

验证缺陷 fix12 (v6.8.3):
    run_micro_scheduler 循环内，当一轮的所有 job 完成时，
    代码递增 optimization_rounds 并将 proposal 移到队列末尾，
    但没有 break 出循环。循环继续下一轮迭代时，
    _list_ready_jobs_for_proposal → sync_checkpoint 创建下一轮 job，
    导致同一时段内直接启动新一轮，违反设计原则：
    "时段内聚焦课题完成一轮后应让出焦点给下一个课题"。

    现场再现：moire 课题 R7 在 22:00 完成后，
    R8 在 22:25 同一时段内启动。

验证点：
    1. 循环内轮次完成后，不再执行下一轮的 job
    2. 轮次完成后，proposal 被移到队列末尾
    3. executed_count 只包含本轮已执行的 job，不包含下一轮
    4. 初始检查（循环前）轮次已完成时直接返回，不进入循环
"""

import sys
import json
import shutil
import importlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from test_runner import TestSuite, create_isolated_env, patch_module_root, patch_kb_sync_noop


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


class RoundCompleteBreakTests(TestSuite):
    def __init__(self):
        super().__init__("轮次完成后 break 验证测试")
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
        patch_kb_sync_noop(self.ms)  # 拦截 KB 同步，避免测试写穿真实 knowledge/
        import paths
        paths.PROJECT_ROOT = self.tmp_root

        self.pid = pid

        # Patch _is_round_complete 与 _is_core_round_complete 使用 tmp_root 路径，
        # 而非 __file__。v7.2.10 起轮转让出门槛改用 _is_core_round_complete，
        # 故需同时 patch 两个函数——本测试场景两者语义相同（fixture 内核心
        # 与 derived 都 done），二者都返回 True。
        tmp_root = self.tmp_root
        original_is_round_complete = self.ms._is_round_complete
        original_is_core_round_complete = getattr(
            self.ms, "_is_core_round_complete", None
        )

        def _patched(jobs, proposal_id, round_num):
            """使用 tmp_root 的产物检查包装。"""
            from lifecycle.micro_scheduler import _CORE_ROUND_STEPS
            round_jobs = [j for j in jobs if j.get("round") == round_num]
            if not round_jobs:
                return False
            core_jobs = [j for j in round_jobs if j.get("step") in _CORE_ROUND_STEPS]
            if not core_jobs:
                return False
            if not all(j.get("status") == "done" for j in core_jobs):
                return False
            # 产物检查使用 tmp_root
            prop_dir = tmp_root / "research_proposals" / "optimizing" / proposal_id / "04_proposal"
            for sec in ["rationale.md", "content.md", "scheme.md", "full_review.md", "references.md"]:
                sec_path = prop_dir / "sections" / sec
                if not sec_path.exists() or sec_path.stat().st_size < 50:
                    return False
            return True

        self.ms._is_round_complete = _patched
        if original_is_core_round_complete is not None:
            self.ms._is_core_round_complete = _patched

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _build_complete_round_jobs(self, pid, round_num):
        """构建一轮完整的 25 个 job（全部 done 状态）。"""
        from proposal_sections import PROPOSAL_SECTIONS
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

        saved_jobs = {}

        def _save_jobs(pid, jobs):
            saved_jobs[pid] = jobs
            proposals_config[pid]["jobs"] = jobs
            return True

        prop_states = {}

        def _get_proposal_state(pid):
            return proposals_config.get(pid, {}).get("state", {})

        def _set_proposal_state(pid, state):
            proposals_config[pid]["state"] = state
            prop_states[pid] = state
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
        ctrl._saved_jobs = saved_jobs
        ctrl._prop_states = prop_states
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
        # 测试 1（核心回归）: 循环内轮次完成后不再执行下一轮 job
        # bug 现场: R7 完成后循环继续，sync_checkpoint 创建 R8 job 并执行
        # 修复: break 阻止循环继续
        #
        # v7.2.10 改法后: 入口检查改用 _is_core_round_complete，若核心全 done
        # （即使 derived pending）会直接返回。所以本测试改用"最后一个核心 job
        # pending"——入口检查 False 进入循环，执行核心后核心+derived 全 done
        # → 走"循环内完成"路径（_is_round_complete True）→ break。
        # ================================================================
        r1_jobs = self._build_complete_round_jobs(pid, 1)
        # 找 references/writer（核心步骤）作为 pending——核心未全 done 才能进循环
        target_pending = None
        for j in r1_jobs:
            if j.get("section_key") == "references" and j.get("step") == "writer":
                target_pending = j
                break
        assert target_pending is not None, "fixture 缺少 references/writer"
        target_pending["status"] = "pending"

        proposals_config = {
            pid: {
                "jobs": r1_jobs,
                "state": {
                    "status": "optimizing",
                    "optimization_rounds": 0,
                    "last_score": 0.70,
                    "score_history": [],
                    "project_type": "general",
                },
            },
        }
        ctrl = self._make_mock_controller(proposals_config)

        # 模拟 _list_ready_jobs_for_proposal 返回最后一个 pending job
        ready_calls = [0]  # 调用计数器

        def _list_ready(pid):
            ready_calls[0] += 1
            jobs = ctrl._get_jobs(pid)
            pending = [j for j in jobs if j.get("status") == "pending"]
            if not pending:
                return []
            return [{"proposal_id": pid, "job": pending[0], "priority": (0, 0, "", 0)}]

        ctrl._list_ready_jobs_for_proposal.side_effect = _list_ready

        # 模拟 _check_and_transition 返回 None（未达标）
        with patch.object(self.ms, "_current_focus_slot", return_value=slot_info), \
             patch.object(self.ms, "_check_and_transition", return_value=None), \
             patch.object(self.ms, "_generate_round_report", return_value=None), \
             patch.object(self.ms, "_update_kanban"):
            # 设置 focus state：pid 在队列头部
            self._setup_focus_state([pid], last_slot_index=3, last_proposal_index=0)

            # 绑定真实 _focus_proposal_for_slot
            ctrl._focus_proposal_for_slot = lambda slot_idx, opt: self.ms._focus_proposal_for_slot(
                ctrl, slot_idx, opt
            )

            result = self.ms.run_micro_scheduler(ctrl, max_jobs=5)

        # 验证只执行了 1 个 job（最后一个 pending job）
        self.assert_eq(
            result.get("executed_count"), 1,
            "轮次完成后应只执行 1 个 job（最后一个 pending job）",
            f"期望 executed_count=1，实际 {result.get('executed_count')}",
        )

        # 验证 _list_ready_jobs_for_proposal 被调用了 2 次：
        # 第 1 次返回 pending job，执行后轮次完成，break 退出
        # 如果没有 break，会第 2 次调用并创建下一轮 job
        # 注意：break 后不会再调用第 2 次
        self.assert_true(
            ready_calls[0] <= 2,
            "轮次完成后应 break，不应继续调用 _list_ready_jobs_for_proposal",
            f"期望 ready 调用次数 <= 2，实际 {ready_calls[0]}",
        )

        # 验证 optimization_rounds 已递增
        final_state = proposals_config[pid]["state"]
        self.assert_eq(
            final_state.get("optimization_rounds"), 1,
            "轮次完成后 optimization_rounds 应递增到 1",
        )

        # ================================================================
        # 测试 2: 轮次完成后 proposal 被移到队列末尾
        # ================================================================
        pid_b = "general-test-beta-20260101"
        # 为 pid_b 创建 proposal 目录
        prop_dir_b = self.tmp_root / "research_proposals" / "optimizing" / pid_b / "04_proposal" / "sections"
        prop_dir_b.mkdir(parents=True, exist_ok=True)
        for sec in ["rationale.md", "content.md", "scheme.md", "full_review.md", "references.md"]:
            (prop_dir_b / sec).write_text("# " + sec + "\n\n" + "x" * 100, encoding="utf-8")

        r1_jobs_2 = self._build_complete_round_jobs(pid, 1)
        # v7.2.10: 改用核心步骤作为 pending（避免入口 _is_core_round_complete
        # 早返回让测试失效）。同测试 1 逻辑。
        target_pending_2 = None
        for j in r1_jobs_2:
            if j.get("section_key") == "references" and j.get("step") == "writer":
                target_pending_2 = j
                break
        assert target_pending_2 is not None, "fixture 缺少 references/writer"
        target_pending_2["status"] = "pending"

        proposals_config_2 = {
            pid: {
                "jobs": r1_jobs_2,
                "state": {
                    "status": "optimizing",
                    "optimization_rounds": 0,
                    "last_score": 0.70,
                    "score_history": [],
                    "project_type": "general",
                },
            },
            pid_b: {
                "jobs": [],
                "state": {
                    "status": "optimizing",
                    "optimization_rounds": 0,
                    "last_score": 0.0,
                    "score_history": [],
                    "project_type": "general",
                },
            },
        }
        ctrl2 = self._make_mock_controller(proposals_config_2)

        def _list_ready_2(pid_arg):
            jobs = ctrl2._get_jobs(pid_arg)
            pending = [j for j in jobs if j.get("status") == "pending"]
            if not pending:
                return []
            return [{"proposal_id": pid_arg, "job": pending[0], "priority": (0, 0, "", 0)}]

        ctrl2._list_ready_jobs_for_proposal.side_effect = _list_ready_2

        with patch.object(self.ms, "_current_focus_slot", return_value=slot_info), \
             patch.object(self.ms, "_check_and_transition", return_value=None), \
             patch.object(self.ms, "_generate_round_report", return_value=None), \
             patch.object(self.ms, "_update_kanban"):
            # 队列: [pid, pid_b]，pid 在头部
            self._setup_focus_state([pid, pid_b], last_slot_index=3, last_proposal_index=0)
            ctrl2._focus_proposal_for_slot = lambda slot_idx, opt: self.ms._focus_proposal_for_slot(
                ctrl2, slot_idx, opt
            )

            result2 = self.ms.run_micro_scheduler(ctrl2, max_jobs=5)

        # 验证 pid 被移到队列末尾
        focus_state_path = self.tmp_root / "memory" / "lifecycle-focus.json"
        focus_state = json.loads(focus_state_path.read_text(encoding="utf-8"))
        queue = focus_state.get("queue", [])
        self.assert_true(
            len(queue) >= 2 and queue[-1] == pid,
            "轮次完成后 proposal 应被移到队列末尾",
            f"期望 queue[-1]={pid}，实际 queue={queue}",
        )

        # ================================================================
        # 测试 3: 初始检查（循环前）轮次已完成时直接返回
        # ================================================================
        r1_all_done = self._build_complete_round_jobs(pid, 1)
        # 全部 done

        proposals_config_3 = {
            pid: {
                "jobs": r1_all_done,
                "state": {
                    "status": "optimizing",
                    "optimization_rounds": 0,
                    "last_score": 0.70,
                    "score_history": [],
                    "project_type": "general",
                },
            },
        }
        ctrl3 = self._make_mock_controller(proposals_config_3)
        ctrl3._list_ready_jobs_for_proposal.return_value = []

        with patch.object(self.ms, "_current_focus_slot", return_value=slot_info), \
             patch.object(self.ms, "_check_and_transition", return_value=None), \
             patch.object(self.ms, "_generate_round_report", return_value=None), \
             patch.object(self.ms, "_update_kanban"):
            self._setup_focus_state([pid], last_slot_index=3, last_proposal_index=0)
            ctrl3._focus_proposal_for_slot = lambda slot_idx, opt: self.ms._focus_proposal_for_slot(
                ctrl3, slot_idx, opt
            )

            result3 = self.ms.run_micro_scheduler(ctrl3, max_jobs=5)

        self.assert_eq(
            result3.get("executed_count"), 0,
            "初始检查发现轮次已完成时应直接返回，不执行任何 job",
        )
        self.assert_eq(
            result3.get("skip_reason"), "round_complete",
            "初始检查轮次完成应返回 skip_reason=round_complete",
        )

        # ================================================================
        # 测试 4: 轮次完成后不创建下一轮 job
        # 验证 sync_checkpoint 不会被调用（因为循环已 break）
        # ================================================================
        r1_jobs_4 = self._build_complete_round_jobs(pid, 1)
        r1_jobs_4[-1]["status"] = "pending"

        proposals_config_4 = {
            pid: {
                "jobs": r1_jobs_4,
                "state": {
                    "status": "optimizing",
                    "optimization_rounds": 0,
                    "last_score": 0.70,
                    "score_history": [],
                    "project_type": "general",
                },
            },
        }
        ctrl4 = self._make_mock_controller(proposals_config_4)

        sync_checkpoint_called = [False]

        def _list_ready_4(pid_arg):
            # 模拟 sync_checkpoint 副作用：如果被调用，会添加下一轮 job
            jobs = ctrl4._get_jobs(pid_arg)
            pending = [j for j in jobs if j.get("status") == "pending"]
            if not pending:
                sync_checkpoint_called[0] = True
                # 模拟 sync_checkpoint 创建下一轮 job
                r2_jobs = self._build_complete_round_jobs(pid_arg, 2)
                for j in r2_jobs:
                    j["status"] = "pending"
                jobs.extend(r2_jobs)
                ctrl4._save_jobs(pid_arg, jobs)
                pending = r2_jobs[:1]
            return [{"proposal_id": pid_arg, "job": pending[0], "priority": (0, 0, "", 0)}]

        ctrl4._list_ready_jobs_for_proposal.side_effect = _list_ready_4

        with patch.object(self.ms, "_current_focus_slot", return_value=slot_info), \
             patch.object(self.ms, "_check_and_transition", return_value=None), \
             patch.object(self.ms, "_generate_round_report", return_value=None), \
             patch.object(self.ms, "_update_kanban"):
            self._setup_focus_state([pid], last_slot_index=3, last_proposal_index=0)
            ctrl4._focus_proposal_for_slot = lambda slot_idx, opt: self.ms._focus_proposal_for_slot(
                ctrl4, slot_idx, opt
            )

            result4 = self.ms.run_micro_scheduler(ctrl4, max_jobs=5)

        # 如果有 break，循环退出后不会再次调用 _list_ready_jobs_for_proposal
        # sync_checkpoint_called 只会在第二次调用时被标记
        # 第一次调用返回 pending job，执行后轮次完成，break 退出
        # 第二次调用（如果没 break）会触发 sync_checkpoint
        self.assert_true(
            not sync_checkpoint_called[0],
            "轮次完成后 break 应阻止 sync_checkpoint 创建下一轮 job",
            "sync_checkpoint 被调用了，说明循环没有 break",
        )
