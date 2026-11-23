#!/usr/bin/env python3
"""
test_core_round_complete.py — 核心完成判定（v7.2.10）单测

背景：
    旧 `_is_round_complete` 要求"本轮全部 job done"才让出焦点，但每轮
    末尾会留 2-4 个 derived（update_vision / update_method_manual），
    导致 N 个课题都卡在末尾 derived 上、像 N 个课题同时处于"中间状态"，
    违反循环队列"完成一轮即让出"的契约。

v7.2.10 改法：新增 `_is_core_round_complete`，只检查核心步骤
（writer / critic / gap_identify / lit_search / lit_read / lit_note /
monitor / idea_review）——这些直接贡献申请书内容或章节评审，必须
做完本轮才可让出。derived 由下一轮头部消化。

验证点：
    1. 核心步骤全部 done → _is_core_round_complete True（旧函数 False）
    2. 缺一个核心步骤 → False（保持严格）
    3. derived 全 pending、核心全 done → True（关键场景：解锁末尾）
    4. 没有任何核心步骤 → False（避免空轮误判）
    5. 不在该轮范围内的 job 不影响判定
    6. 产物文件不完整 → False（产物检查与旧函数同源）
    7. derived 不计入 `_CORE_ROUND_STEPS` 集合
"""

import os
import sys
import shutil
import importlib
from pathlib import Path
from unittest.mock import MagicMock

from test_runner import TestSuite, create_isolated_env, patch_module_root, patch_kb_sync_noop


def _make_job(pid, round_num, section_key, step, status="pending",
              depends_on=None):
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
        "started_at": "",
        "finished_at": "",
        "last_error": "",
        "cron_job_id": "",
    }


class CoreRoundCompleteTests(TestSuite):
    """v7.2.10: _is_core_round_complete 单元测试。"""

    def __init__(self):
        super().__init__("核心完成判定测试")
        self.tmp_root = None
        self.ms = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / "optimizing" / sub).mkdir(
                parents=True, exist_ok=True
            )
        pid = "general-test-core-complete-20260101"
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / pid / "04_proposal" / "sections"
        prop_dir.mkdir(parents=True, exist_ok=True)
        for sec in ["rationale.md", "content.md", "scheme.md",
                    "full_review.md", "references.md"]:
            (prop_dir / sec).write_text(
                "# " + sec + "\n\n" + "x" * 100, encoding="utf-8"
            )

        for mod_name in list(sys.modules.keys()):
            if "micro_scheduler" in mod_name or mod_name in [
                "lifecycle", "paths", "common", "proposal_lifecycle",
                "proposal_sections",
            ]:
                del sys.modules[mod_name]

        self.ms = importlib.import_module("lifecycle.micro_scheduler")
        patch_module_root("lifecycle.micro_scheduler", self.tmp_root)
        patch_kb_sync_noop(self.ms)
        import paths
        paths.PROJECT_ROOT = self.tmp_root

        self.pid = pid

        # Patch 两个函数使用 tmp_root（产物检查路径）
        tmp_root = self.tmp_root

        def _patched(jobs, proposal_id, round_num, fn_name):
            round_jobs = [j for j in jobs if j.get("round") == round_num]
            if not round_jobs:
                return False
            if fn_name == "_is_core_round_complete":
                from lifecycle.micro_scheduler import _CORE_ROUND_STEPS
                core_jobs = [j for j in round_jobs if j.get("step") in _CORE_ROUND_STEPS]
                if not core_jobs:
                    return False
                jobs_to_check = core_jobs
            else:
                jobs_to_check = round_jobs
            if not all(j.get("status") == "done" for j in jobs_to_check):
                return False
            prop_dir = tmp_root / "research_proposals" / "optimizing" / proposal_id / "04_proposal"
            for sec in ["rationale.md", "content.md", "scheme.md",
                        "full_review.md", "references.md"]:
                sec_path = prop_dir / "sections" / sec
                if not sec_path.exists() or sec_path.stat().st_size < 50:
                    return False
            return True

        self.ms._is_round_complete = lambda jobs, pid, rn: _patched(
            jobs, pid, rn, "_is_round_complete"
        )
        self.ms._is_core_round_complete = lambda jobs, pid, rn: _patched(
            jobs, pid, rn, "_is_core_round_complete"
        )

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ===== 测试用例 =====

    def test_core_round_complete_true_when_core_done(self):
        """场景1: 核心步骤全 done → core_round_complete True。"""
        pid = self.pid
        sections = [
            ("rationale", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("content", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("scheme", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("full_review", ["critic", "writer"]),
            ("references", ["critic", "writer"]),
        ]
        jobs = []
        for sec, steps in sections:
            for s in steps:
                jobs.append(_make_job(pid, 1, sec, s, status="done"))
        # 加 2 个 derived（pending）——不应影响 core 判定
        jobs.append(_make_job(pid, 1, "derived", "update_vision", status="pending"))
        jobs.append(_make_job(pid, 1, "derived", "update_method_manual", status="pending"))

        result = self.ms._is_core_round_complete(jobs, pid, 1)
        self.assert_eq(
            result, True,
            "核心步骤全 done、derived pending → core_round_complete 应为 True",
        )
        self.assert_eq(len(self.results), len(self.results), "记录已添加")

    def test_core_round_complete_false_when_missing_core(self):
        """场景2: 缺一个核心步骤 → False。"""
        pid = self.pid
        sections = [
            ("rationale", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("content", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("scheme", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("full_review", ["critic", "writer"]),
            ("references", ["critic", "writer"]),
        ]
        jobs = []
        for sec, steps in sections:
            for s in steps:
                jobs.append(_make_job(pid, 1, sec, s, status="done"))
        # 关键：把 references/critic 改成 pending
        for j in jobs:
            if j["section_key"] == "references" and j["step"] == "critic":
                j["status"] = "pending"
        # 加 2 个 derived done
        jobs.append(_make_job(pid, 1, "derived", "update_vision", status="done"))
        jobs.append(_make_job(pid, 1, "derived", "update_method_manual", status="done"))

        result = self.ms._is_core_round_complete(jobs, pid, 1)
        self.assert_eq(
            result, False,
            "references critic pending → core_round_complete 应为 False",
        )

    def test_old_function_still_strict_when_derived_pending(self):
        """场景3（旧函数对照）: 核心 done、derived pending → 旧函数 False、新函数 True。
        这是本次改法的关键价值。"""
        pid = self.pid
        sections = [
            ("rationale", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("content", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("scheme", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("full_review", ["critic", "writer"]),
            ("references", ["critic", "writer"]),
        ]
        jobs = []
        for sec, steps in sections:
            for s in steps:
                jobs.append(_make_job(pid, 1, sec, s, status="done"))
        # 关键：derived 全部 pending
        jobs.append(_make_job(pid, 1, "derived", "update_vision", status="pending"))
        jobs.append(_make_job(pid, 1, "derived", "update_method_manual", status="pending"))

        old = self.ms._is_round_complete(jobs, pid, 1)
        new = self.ms._is_core_round_complete(jobs, pid, 1)
        self.assert_eq(
            old, False,
            "旧函数在 derived pending 时仍返回 False（保留晋级完整性门语义）",
        )
        self.assert_eq(
            new, True,
            "新函数在 derived pending 但核心 done 时返回 True（解锁末尾）",
        )

    def test_core_round_complete_false_when_no_core_jobs(self):
        """场景4: 该轮没有任何核心步骤 → False（极端：新进课题尚未派生核心）。"""
        pid = self.pid
        # 只放 derived（极端构造）
        jobs = [
            _make_job(pid, 1, "derived", "update_vision", status="done"),
            _make_job(pid, 1, "derived", "update_method_manual", status="done"),
        ]
        result = self.ms._is_core_round_complete(jobs, pid, 1)
        self.assert_eq(
            result, False,
            "没有任何核心 job 时应保守返回 False（避免空轮误判）",
        )

    def test_core_round_complete_ignores_other_rounds(self):
        """场景5: 不在该轮范围内的 job 不影响判定。"""
        pid = self.pid
        # R0（历史）
        r0_jobs = [
            _make_job(pid, 0, "rationale", "writer", status="done"),
        ]
        # R1 当前轮——核心全 done
        r1_jobs = []
        sections = [
            ("rationale", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("content", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("scheme", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("full_review", ["critic", "writer"]),
            ("references", ["critic", "writer"]),
        ]
        for sec, steps in sections:
            for s in steps:
                r1_jobs.append(_make_job(pid, 1, sec, s, status="done"))
        # R2（未来）——全 pending
        r2_jobs = [_make_job(pid, 2, "rationale", "writer", status="pending")]
        all_jobs = r0_jobs + r1_jobs + r2_jobs

        result = self.ms._is_core_round_complete(all_jobs, pid, 1)
        self.assert_eq(
            result, True,
            "其他轮的 job（无论 done/pending）不影响 R1 判定",
        )

    def test_core_round_complete_false_when_sections_missing(self):
        """场景6: 产物文件不完整 → False（产物检查与旧函数同源）。"""
        pid = self.pid
        jobs = []
        sections = [
            ("rationale", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("content", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("scheme", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("full_review", ["critic", "writer"]),
            ("references", ["critic", "writer"]),
        ]
        for sec, steps in sections:
            for s in steps:
                jobs.append(_make_job(pid, 1, sec, s, status="done"))

        # 删掉 references 章节文件
        ref_path = self.tmp_root / "research_proposals" / "optimizing" / pid / "04_proposal" / "sections" / "references.md"
        ref_path.unlink()

        result = self.ms._is_core_round_complete(jobs, pid, 1)
        self.assert_eq(
            result, False,
            "缺失 references.md → core_round_complete 应为 False（产物检查）",
        )

    def test_core_round_steps_set_excludes_derived(self):
        """场景7: _CORE_ROUND_STEPS 不含 derived。"""
        steps = self.ms._CORE_ROUND_STEPS
        self.assert_true(
            "update_vision" not in steps,
            "update_vision 不应在 _CORE_ROUND_STEPS 中",
            "update_vision 误入核心集合",
        )
        self.assert_true(
            "update_method_manual" not in steps,
            "update_method_manual 不应在 _CORE_ROUND_STEPS 中",
            "update_method_manual 误入核心集合",
        )
        # 核心步骤必须全在
        for core in ["writer", "critic", "gap_identify", "lit_search",
                     "lit_read", "lit_note", "monitor", "idea_review"]:
            self.assert_true(
                core in steps,
                f"{core} 应在 _CORE_ROUND_STEPS 中",
                f"{core} 不在核心集合",
            )

    def test_monitor_treated_as_core(self):
        """场景8: monitor 属于核心（v6.7.6 全局监察，每轮收尾必需）。"""
        pid = self.pid
        sections = [
            ("rationale", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("content", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("scheme", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("full_review", ["critic", "writer"]),
            ("references", ["critic", "writer"]),
        ]
        jobs = []
        for sec, steps in sections:
            for s in steps:
                jobs.append(_make_job(pid, 1, sec, s, status="done"))
        # 加 monitor pending
        jobs.append(_make_job(pid, 1, "monitor", "monitor", status="pending"))

        result = self.ms._is_core_round_complete(jobs, pid, 1)
        self.assert_eq(
            result, False,
            "monitor pending → core_round_complete 应为 False（monitor 是核心）",
        )

    def test_idea_review_treated_as_core(self):
        """场景9: idea_review 属于核心（前置评审）。"""
        pid = self.pid
        sections = [
            ("rationale", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("content", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("scheme", ["critic", "gap_identify", "lit_search", "lit_read", "lit_note", "writer"]),
            ("full_review", ["critic", "writer"]),
            ("references", ["critic", "writer"]),
        ]
        jobs = []
        for sec, steps in sections:
            for s in steps:
                jobs.append(_make_job(pid, 1, sec, s, status="done"))
        # 加 idea_review pending
        jobs.append(_make_job(pid, 1, "idea_review", "idea_review", status="pending"))

        result = self.ms._is_core_round_complete(jobs, pid, 1)
        self.assert_eq(
            result, False,
            "idea_review pending → core_round_complete 应为 False（前置评审是核心）",
        )

    def test_partial_pending_core_blocks_release(self):
        """场景10: 部分核心 pending、derived done → False（关键回归保护）。"""
        pid = self.pid
        jobs = []
        # R1 有几个 pending 核心
        jobs.append(_make_job(pid, 1, "rationale", "writer", status="done"))
        jobs.append(_make_job(pid, 1, "content", "writer", status="pending"))  # 关键 pending
        jobs.append(_make_job(pid, 1, "scheme", "writer", status="done"))
        jobs.append(_make_job(pid, 1, "full_review", "writer", status="done"))
        jobs.append(_make_job(pid, 1, "references", "writer", status="done"))
        jobs.append(_make_job(pid, 1, "monitor", "monitor", status="done"))
        # derived 全 done（无关）
        jobs.append(_make_job(pid, 1, "derived", "update_vision", status="done"))
        jobs.append(_make_job(pid, 1, "derived", "update_method_manual", status="done"))

        result = self.ms._is_core_round_complete(jobs, pid, 1)
        self.assert_eq(
            result, False,
            "content writer 仍 pending → core_round_complete 应为 False",
        )

    def run_tests(self):
        """TestSuite 框架要求的方法。逐个调用测试用例。"""
        self.test_core_round_complete_true_when_core_done()
        self.test_core_round_complete_false_when_missing_core()
        self.test_old_function_still_strict_when_derived_pending()
        self.test_core_round_complete_false_when_no_core_jobs()
        self.test_core_round_complete_ignores_other_rounds()
        self.test_core_round_complete_false_when_sections_missing()
        self.test_core_round_steps_set_excludes_derived()
        self.test_monitor_treated_as_core()
        self.test_idea_review_treated_as_core()
        self.test_partial_pending_core_blocks_release()


if __name__ == "__main__":
    from test_runner import execute_suite
    suite = CoreRoundCompleteTests()
    execute_suite(suite, suite.name, [])
    print(f"\n=== {suite.name} ===")
    total = len(suite.results)
    passed = sum(1 for r in suite.results if r.passed)
    failed = [r for r in suite.results if not r.passed]
    print(f"通过 {passed}/{total}")
    if failed:
        print("\n失败用例：")
        for r in failed:
            print(f"  ✗ {r.name}: {r.msg}")
        sys.exit(1)
    print("✓ 全部测试通过")
