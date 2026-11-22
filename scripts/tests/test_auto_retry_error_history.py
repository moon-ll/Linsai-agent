#!/usr/bin/env python3
"""
test_auto_retry_error_history.py — _auto_retry_failed_jobs 错误历史保留回归测试

覆盖缺陷（v6.8.27）：
    _auto_retry_failed_jobs 在重置 failed→pending 时无条件设置
    job["last_error"] = ""，导致失败原因被立即擦除。
    实证场景：2026-08-12 14:35:29Z general-moire-strong-field-probe-20260726-r7-
    references-writer 因 900s 超时被 stale 检测标记为 failed，last_error 应为
    "运行超时/进程僵死"；同一次 micro_scheduler 调度中 _auto_retry_failed_jobs
    又把它改回 pending 并清空 last_error → 错误上下文彻底丢失。
    当 attempt 2/3 再次失败时，错误历史归零，无法区分"再次超时"与"另一种新错误"。

验证点：
    - 重试前 last_error 包含具体错误（如"运行超时/进程僵死"）
    - 重试后 last_error 仍保留（不丢失）
    - 错误被同时追加到 job.error_history 字段（保留最近 10 条）
    - 重试 attempts 增加、status 变回 pending

注意：
    本测试不调用 hermes/LLM；通过直接构造 jobs 列表调用 _auto_retry_failed_jobs
    （作为模块级函数，需传入 self 即 mock controller）验证行为。
"""

import sys
import json
import shutil
import importlib
from pathlib import Path
from unittest.mock import MagicMock

from test_runner import TestSuite, create_isolated_env, patch_module_root


class AutoRetryErrorHistoryTests(TestSuite):
    def __init__(self):
        super().__init__("_auto_retry_failed_jobs 错误历史保留测试")
        self.tmp_root = None
        self.ms = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / sub).mkdir(parents=True, exist_ok=True)
        for mod_name in list(sys.modules.keys()):
            if "micro_scheduler" in mod_name or mod_name in ["lifecycle", "paths", "common"]:
                del sys.modules[mod_name]
        self.ms = importlib.import_module("lifecycle.micro_scheduler")
        patch_module_root("lifecycle.micro_scheduler", self.tmp_root)
        import paths
        paths.PROJECT_ROOT = self.tmp_root

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_jobs_file(self, proposal_id, jobs):
        """写入 proposal 的 jobs.json。"""
        jobs_path = self.tmp_root / "research_proposals" / "optimizing" / proposal_id / "_jobs.json"
        jobs_path.parent.mkdir(parents=True, exist_ok=True)
        jobs_path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_jobs_file(self, proposal_id):
        jobs_path = self.tmp_root / "research_proposals" / "optimizing" / proposal_id / "_jobs.json"
        return json.loads(jobs_path.read_text(encoding="utf-8"))

    def run_tests(self):
        pid = "general-moire-strong-field-probe-20260726"

        # ================================================================
        # 测试 1：核心回归 — failed → pending 重试必须保留 last_error
        # 修复前：last_error 被无条件清空（""）
        # 修复后：last_error 保留，error_history 追加一条历史记录
        # ================================================================
        jobs = [
            {
                "job_id": f"{pid}-r7-references-writer",
                "proposal_id": pid,
                "step": "writer",
                "section_key": "references",
                "round": 7,
                "status": "failed",
                "depends_on": [f"{pid}-r7-references-critic"],
                "attempts": 1,
                "scheduled_at": "",
                "started_at": "2026-08-12T14:20:29Z",
                "finished_at": "2026-08-12T14:35:29Z",
                "last_error": "运行超时/进程僵死",
                "repair_attempts": 0,
            },
            {
                "job_id": f"{pid}-r7-monitor-monitor",
                "proposal_id": pid,
                "step": "monitor",
                "section_key": "monitor",
                "round": 7,
                "status": "pending",
                "depends_on": [f"{pid}-r7-references-writer"],
                "attempts": 0,
                "scheduled_at": "",
                "started_at": "",
                "finished_at": "",
                "last_error": "",
                "repair_attempts": 0,
            },
        ]
        self._make_jobs_file(pid, jobs)

        # 构造 mock controller：_save_jobs 实际写回文件
        ctrl = MagicMock()
        ctrl._get_jobs.side_effect = lambda p: self._read_jobs_file(p)
        ctrl._save_jobs.side_effect = lambda p, j: self._make_jobs_file(p, j)

        retry_count = self.ms._auto_retry_failed_jobs(ctrl, pid)
        self.assert_eq(
            retry_count, 1,
            "重试一个阻塞 pending 任务的 failed job",
            "应返回重试计数 1",
        )

        # 验证 last_error 保留
        after = self._read_jobs_file(pid)
        writer_job = next(j for j in after if j["job_id"] == f"{pid}-r7-references-writer")

        self.assert_eq(
            writer_job["status"], "pending",
            "failed job 重试后状态应为 pending",
            "状态机正确流转",
        )
        self.assert_eq(
            writer_job["attempts"], 2,
            "attempts 应从 1 递增到 2",
            "attempts 计数正确",
        )
        self.assert_eq(
            writer_job["repair_attempts"], 1,
            "repair_attempts 应从 0 递增到 1",
            "repair_attempts 计数正确",
        )
        self.assert_eq(
            writer_job["last_error"], "运行超时/进程僵死",
            "last_error 必须保留（修复前会被清空导致上下文丢失）",
            "v6.8.27: 重试时不擦除 last_error，保留错误上下文供后续诊断",
        )

        # 验证 error_history 字段被追加
        self.assert_true(
            isinstance(writer_job.get("error_history"), list) and len(writer_job["error_history"]) >= 1,
            "error_history 字段应追加一条历史",
            "v6.8.27: 重试时将 last_error 追加到 error_history",
        )
        if writer_job.get("error_history"):
            hist_entry = writer_job["error_history"][0]
            self.assert_eq(
                hist_entry.get("error"), "运行超时/进程僵死",
                "error_history[0].error 应为原 last_error",
                "历史条目的 error 字段正确",
            )
            self.assert_eq(
                hist_entry.get("attempts"), 1,
                "error_history[0].attempts 应为失败时的 attempts=1",
                "历史条目的 attempts 字段正确",
            )

        # ================================================================
        # 测试 2：连续失败 — error_history 累积多条
        # ================================================================
        jobs2 = [
            {
                "job_id": f"{pid}-r7-references-writer",
                "proposal_id": pid,
                "step": "writer",
                "section_key": "references",
                "round": 7,
                "status": "failed",
                "depends_on": [f"{pid}-r7-references-critic"],
                "attempts": 2,
                "last_error": "运行超时/进程僵死",
                "error_history": [
                    {"at": "2026-08-12T14:35:29Z", "error": "运行超时/进程僵死", "attempts": 1},
                ],
                "repair_attempts": 1,
            },
            {
                "job_id": f"{pid}-r7-monitor-monitor",
                "proposal_id": pid,
                "step": "monitor",
                "section_key": "monitor",
                "round": 7,
                "status": "pending",
                "depends_on": [f"{pid}-r7-references-writer"],
                "attempts": 0,
                "last_error": "",
            },
        ]
        self._make_jobs_file(pid, jobs2)

        retry_count2 = self.ms._auto_retry_failed_jobs(ctrl, pid)
        self.assert_eq(
            retry_count2, 1,
            "第二次重试应返回 1",
            "重试计数正确",
        )
        after2 = self._read_jobs_file(pid)
        writer2 = next(j for j in after2 if j["job_id"] == f"{pid}-r7-references-writer")

        self.assert_eq(
            writer2["last_error"], "运行超时/进程僵死",
            "第二次重试 last_error 仍保留",
            "v6.8.27: 即使已有 error_history，last_error 仍不丢失",
        )
        self.assert_true(
            len(writer2.get("error_history", [])) >= 2,
            "第二次重试后 error_history 应累积 2 条",
            f"v6.8.27: error_history 单调累积，实际 {len(writer2.get('error_history', []))} 条",
        )

        # ================================================================
        # 测试 3：超过 attempts 上限的不重试 — last_error 不变
        # ================================================================
        jobs3 = [
            {
                "job_id": f"{pid}-r7-references-writer",
                "proposal_id": pid,
                "step": "writer",
                "section_key": "references",
                "round": 7,
                "status": "failed",
                "depends_on": [f"{pid}-r7-references-critic"],
                "attempts": 3,  # 已达 MAX_JOB_ATTEMPTS
                "last_error": "运行超时/进程僵死",
                "error_history": [],
                "repair_attempts": 0,
            },
            {
                "job_id": f"{pid}-r7-monitor-monitor",
                "proposal_id": pid,
                "step": "monitor",
                "section_key": "monitor",
                "round": 7,
                "status": "pending",
                "depends_on": [f"{pid}-r7-references-writer"],
                "attempts": 0,
                "last_error": "",
            },
        ]
        self._make_jobs_file(pid, jobs3)

        retry_count3 = self.ms._auto_retry_failed_jobs(ctrl, pid)
        self.assert_eq(
            retry_count3, 0,
            "attempts 达上限时不重试",
            "attempts=3 >= MAX_JOB_ATTEMPTS=3，重试计数应为 0",
        )
        after3 = self._read_jobs_file(pid)
        writer3 = next(j for j in after3 if j["job_id"] == f"{pid}-r7-references-writer")
        self.assert_eq(
            writer3["status"], "failed",
            "超过 attempts 上限的 failed job 保持 failed 状态",
            "状态不被错误重试",
        )
        self.assert_eq(
            writer3["last_error"], "运行超时/进程僵死",
            "超过 attempts 上限的 job last_error 保持原样",
            "失败原因保留以供诊断",
        )

        # ================================================================
        # 测试 4：孤立 failed job（不阻塞任何 pending）不被重试
        # ================================================================
        jobs4 = [
            {
                "job_id": f"{pid}-r7-references-writer",
                "proposal_id": pid,
                "step": "writer",
                "section_key": "references",
                "round": 7,
                "status": "failed",
                "depends_on": [f"{pid}-r7-references-critic"],
                "attempts": 1,
                "last_error": "运行超时/进程僵死",
                "error_history": [],
                "repair_attempts": 0,
            },
            # 没有 pending job 引用该 failed job
        ]
        self._make_jobs_file(pid, jobs4)

        retry_count4 = self.ms._auto_retry_failed_jobs(ctrl, pid)
        self.assert_eq(
            retry_count4, 0,
            "孤立 failed job 不被重试",
            "无 pending 任务依赖，不重试以减少无意义执行",
        )
        after4 = self._read_jobs_file(pid)
        writer4 = next(j for j in after4 if j["job_id"] == f"{pid}-r7-references-writer")
        self.assert_eq(
            writer4["status"], "failed",
            "孤立 failed job 状态保持",
            "避免无差别重试",
        )
        self.assert_eq(
            writer4["last_error"], "运行超时/进程僵死",
            "孤立 failed job last_error 保持",
            "错误上下文不被改动",
        )


if __name__ == "__main__":
    suite = AutoRetryErrorHistoryTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    s = suite.summary()
    print(f"\n{'✓' if s['failed'] == 0 else '✗'} {s['name']}: {s['passed']}/{s['total']} 通过")
    for r in s["results"]:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if s["failed"] == 0 else 1)