#!/usr/bin/env python3
"""
test_side_worker.py — 并行试点 side-worker 回归测试（v7.3.55）

覆盖：
    1. 配置门控：parallel-workers.json 缺失/enabled=false → 零执行跳过
    2. 正常路径：候选课题有 ready job → 抢 per-proposal 锁执行 1 个
    3. 锁忙路径：候选课题被占用（TimeoutError）→ 跳到下一候选
    4. 轮转名单为空 → no_queue 跳过
    5. execute_job 返回 write_lock_held → 跳过且不计入执行
    6. 单候选异常 → fail-soft 落账（success=False）不拖垮 tick

注意：不调用 hermes/LLM。execute_job/_list_ready_jobs_for_proposal/
_get_jobs 均用桩替换；file_lock 经模块级桩分流（仅 lock_busy_pids 抛
TimeoutError，其余走真实实现），锁文件落在 create_isolated_env 的
LINSAI_LOCK_DIR 隔离目录。
"""

import sys
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT

sys.path.insert(0, str(REAL_ROOT / "scripts"))


class SideWorkerTests(TestSuite):
    def __init__(self):
        super().__init__("并行试点 side-worker 回归测试")
        self.tmp_root = None
        self.sw = None
        self.ctrl = None
        self._orig_file_lock = None

    # ---------- 夹具 ----------

    def setup(self):
        self.tmp_root = create_isolated_env()
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / sub).mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "memory" / "config" / "schedules").mkdir(parents=True, exist_ok=True)

        for mod_name in list(sys.modules.keys()):
            if "side_worker" in mod_name or "micro_scheduler" in mod_name \
                    or mod_name in ("lifecycle", "lifecycle.controller"):
                del sys.modules[mod_name]

        self.sw = importlib.import_module("lifecycle.side_worker")
        patch_module_root("lifecycle.side_worker", self.tmp_root)
        import paths
        paths.PROJECT_ROOT = self.tmp_root
        # v7.3.58: 配置路径显式注入——PARALLEL_CONFIG_PATH 是导入期常量，全量
        # 套件中其它套件可能先缓存过本模块（paths.PROJECT_ROOT 当时为真实
        # 根），重导入后常量仍指向真实文件 → 门控测试读到生产配置。显式
        # 重写为隔离路径，杜绝跨套件模块卫生问题。
        self.sw.PARALLEL_CONFIG_PATH = \
            self.tmp_root / "memory" / "config" / "schedules" / "parallel-workers.json"

        # 巡检修复：固定工作时段桩。真实 focus-slots.json 在 13:00-18:00
        # 为用户下午高峰空窗（不轮转），此时 _current_focus_slot() 恒返 None，
        # side-worker 按设计走 out_of_slot 跳过，导致本套件在下午时段运行
        # 时被误判为回归（实测 2026-11-07 13:18 复现 3/5）。
        import lifecycle.micro_scheduler as _micro
        self._micro = _micro
        self._orig_focus_slot = _micro._current_focus_slot
        _micro._current_focus_slot = lambda: (0, ("00:00", "23:59"))

        # file_lock 桩：默认全部走真实实现；ctrl.lock_busy_pids 命中的
        # proposal 锁抛 TimeoutError（模拟主 tick 正在执行该课题）
        from common import file_lock as real_file_lock
        self._orig_file_lock = self.sw.file_lock
        self.ctrl = StubController()

        def staged_file_lock(name, blocking=True):
            if name.startswith("proposal-") and \
                    name[len("proposal-"):] in self.ctrl.lock_busy_pids:
                class _BusyCtx:
                    def __enter__(self):
                        raise TimeoutError("lock busy (stub)")

                    def __exit__(self, *a):
                        return False
                return _BusyCtx()
            return real_file_lock(name, blocking=blocking)

        self.sw.file_lock = staged_file_lock

    def teardown(self):
        if self._orig_file_lock is not None:
            self.sw.file_lock = self._orig_file_lock
        if getattr(self, "_orig_focus_slot", None) is not None:
            self._micro._current_focus_slot = self._orig_focus_slot
        self._orig_focus_slot = None
        self.ctrl = None
        if self.tmp_root and self.tmp_root.exists():
            import shutil
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_config(self, enabled: bool):
        import json
        cfg_path = self.tmp_root / "memory" / "config" / "schedules" / "parallel-workers.json"
        cfg_path.write_text(json.dumps({"enabled": enabled, "max_jobs_per_run": 1}),
                            encoding="utf-8")

    def _write_queue(self, pids):
        import json
        focus = self.tmp_root / "memory" / "lifecycle-focus.json"
        focus.parent.mkdir(parents=True, exist_ok=True)
        focus.write_text(json.dumps({"queue": pids[:3], "queue_full": list(pids)}),
                         encoding="utf-8")

    # ---------- 用例 ----------

    def test_config_disabled_skips(self):
        """配置缺失或 enabled=false 时零执行（fail-safe 默认关闭）。"""
        self._write_config(False)
        r = self.sw.run_side_worker(self.ctrl)
        self.assert_eq(r.get("skip_reason"), "parallel_disabled", "disabled 应跳过")
        self.assert_eq(r.get("executed_count"), 0, "零执行")

        (self.tmp_root / "memory" / "config" / "schedules" / "parallel-workers.json").unlink()
        r2 = self.sw.run_side_worker(self.ctrl)
        self.assert_eq(r2.get("skip_reason"), "parallel_disabled", "配置缺失同样跳过")

    def test_normal_path_executes_one(self):
        """候选课题有 ready job → 抢锁执行 1 个并落账。"""
        self._write_config(True)
        self._write_queue(["p-b", "p-a"])
        self.ctrl.ready_jobs["p-b"] = [
            {"proposal_id": "p-b", "job": {"job_id": "j1", "step": "writer", "depends_on": []}}
        ]
        self.ctrl.exec_results["j1"] = {"success": True}
        r = self.sw.run_side_worker(self.ctrl)
        self.assert_eq(r.get("executed_count"), 1, "执行 1 个")
        self.assert_true(r["executed"][0]["proposal_id"] == "p-b", "执行 p-b")
        self.assert_true(r["executed"][0]["success"] is True, "success 落账")

    def test_lock_busy_skips_to_next_candidate(self):
        """候选锁忙（TimeoutError）→ 跳过该候选继续下一个。"""
        self._write_config(True)
        self._write_queue(["p-busy", "p-free"])
        self.ctrl.ready_jobs["p-busy"] = [
            {"proposal_id": "p-busy", "job": {"job_id": "jb", "step": "critic", "depends_on": []}}
        ]
        self.ctrl.ready_jobs["p-free"] = [
            {"proposal_id": "p-free", "job": {"job_id": "jf", "step": "writer", "depends_on": []}}
        ]
        self.ctrl.exec_results["jf"] = {"success": True}
        self.ctrl.lock_busy_pids = {"p-busy"}
        r = self.sw.run_side_worker(self.ctrl)
        self.assert_eq(r.get("executed_count"), 1, "锁忙跳过后仍执行 1 个")
        self.assert_true(r["executed"][0]["proposal_id"] == "p-free", "执行的是 p-free")

    def test_empty_queue_skips(self):
        """轮转名单为空 → no_queue 跳过且不触碰状态。"""
        self._write_config(True)
        (self.tmp_root / "memory" / "lifecycle-focus.json").write_text("{}", encoding="utf-8")
        r = self.sw.run_side_worker(self.ctrl)
        self.assert_eq(r.get("skip_reason"), "no_queue", "空名单跳过")

    def test_write_lock_held_not_counted(self):
        """execute_job 返回 write_lock_held → 不计入执行名额。"""
        self._write_config(True)
        self._write_queue(["p-b"])
        self.ctrl.ready_jobs["p-b"] = [
            {"proposal_id": "p-b", "job": {"job_id": "j1", "step": "writer", "depends_on": []}}
        ]
        self.ctrl.exec_results["j1"] = {"skipped": "write_lock_held", "success": False,
                                        "error": "写作锁被人工会话持有"}
        r = self.sw.run_side_worker(self.ctrl)
        self.assert_eq(r.get("executed_count"), 0, "write_lock_held 不计入")

    def test_candidate_failure_fail_soft(self):
        """单候选执行异常 → fail-soft 落账 success=False，不拖垮 tick。"""
        self._write_config(True)
        self._write_queue(["p-bad"])
        self.ctrl.ready_jobs["p-bad"] = [
            {"proposal_id": "p-bad", "job": {"job_id": "jx", "step": "writer", "depends_on": []}}
        ]

        def _boom(job):
            raise RuntimeError("模拟执行故障")

        self.ctrl.exec_fn = _boom
        r = self.sw.run_side_worker(self.ctrl)
        self.assert_true(r.get("success") is True, "tick 不被单候选故障拖垮")
        self.assert_eq(r.get("executed_count"), 1, "异常落账为 1 条")
        self.assert_true(r["executed"][0]["success"] is False, "success=False 可见")

    # ---------- 入口 ----------

    def run_tests(self):
        self.test_config_disabled_skips()
        self.test_normal_path_executes_one()
        self.test_lock_busy_skips_to_next_candidate()
        self.test_empty_queue_skips()
        self.test_write_lock_held_not_counted()
        self.test_candidate_failure_fail_soft()


class StubController:
    """最小桩控制器：只实现 side-worker 依赖面。"""

    def __init__(self):
        self.ready_jobs = {}
        self.exec_results = {}
        self.lock_busy_pids = set()
        self.exec_fn = None

    def _list_ready_jobs_for_proposal(self, proposal_id):
        return list(self.ready_jobs.get(proposal_id, []))

    def _get_jobs(self, proposal_id):
        job = self.ready_jobs.get(proposal_id, [{}])[0].get("job", {})
        return [dict(job, status="pending")]

    def execute_job(self, job):
        if self.exec_fn is not None:
            return self.exec_fn(job)
        return self.exec_results.get(job.get("job_id"), {"success": False})


if __name__ == "__main__":
    suite = SideWorkerTests()
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
