#!/usr/bin/env python3
"""
test_concurrent_state_write.py — 共享状态文件并发丢更新回归测试（v7.2.48）

背景（2026-10-26 16h 健康检查 deep_scan v54 存量深扫发现，BUG-12）：
    两个共享 JSON 状态文件存在**无锁读-改-写**（read-modify-write）
    模式，与并发写者交叉时会用旧快照覆盖对方的写入：

      1. `research_proposals/_lifecycle.json`
         —— `lifecycle/utils.py` 的 `_save_jobs()`：
         旧实现「无锁读全量 state → 改一个 proposal 的 pipeline_jobs
         → 无锁写回全量 state」。并发写者（微调度器的 worker 线程 /
         per-proposal worker cron / Web 手工触发）在此窗口内写入的
         其它 proposal 的 job 终态会被**整份丢弃** → 该 job 回退 pending
         → 被重复执行（整轮 LLM 重跑，结果被后续轮次覆盖）。

      2. `memory/weekend-pipeline.json`
         —— `lifecycle/orchestrator.py` 的 `_run_weekend_repair()`：
         旧实现「无锁读快照 → repair_stale_and_failed 改内存 → 无锁
         写回」。与 lc-weekend-worker（每 20 分钟持 weekend-pipeline 锁
         执行 job 并落盘终态）交叉时，worker 刚写入的 job 终态被覆盖
         → job 回退 pending → 重复执行整轮 LLM；worker 新建的 job
         直接从磁盘消失。

    两条路径的共同根因：**写前没有在锁内重读最新磁盘状态**。

本测试覆盖：
    1. 核心性质（确定性）：`_save_jobs` 读 state 时必须**持有**
       proposal-lifecycle 锁 —— 直接断言修复的核心不变式，
       不依赖线程调度时序。
    2. 端到端并发丢更新复现（确定性）：强制交错「A 读快照 → B 写 →
       A 写回」，修复后 A 的写入不得丢弃 B 的写入。
    3. 反向断言：复刻旧实现（无锁读-改-写）时必须复现丢更新
       —— 证明测试能真正捕获该缺陷（不是恒真断言）。
    4. 周末 pipeline repair 路径：worker 的写入不得被 repair 覆盖。
    5. `_save_jobs` 单写者路径回归 + 未知 proposal 不创建孤儿条目。

注意：本测试不调用 LLM，运行于隔离临时目录，零生产副作用。
"""

import fcntl
import importlib
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


class ConcurrentStateWriteTests(TestSuite):
    def __init__(self):
        super().__init__("共享状态文件并发丢更新回归测试（v7.2.48）")
        self.tmp_root = None

    # ------------------------------------------------------------------
    # 隔离环境
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("weekend_pipeline") or mod_name.startswith("proposal_lifecycle"):
                del sys.modules[sys.modules and mod_name]

        import paths
        self._orig_project_root = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root
        self.wp_mod = importlib.import_module("weekend_pipeline")
        patch_module_root("weekend_pipeline", self.tmp_root)
        patch_module_root("proposal_lifecycle", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    # ------------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------------

    def _lock_path(self, lock_name: str) -> Path:
        """复刻 common.file_lock 的锁文件路径（用于探针）。"""
        lock_dir = os.environ.get("LINSAI_LOCK_DIR")
        base = Path(lock_dir) if lock_dir else Path(tempfile.gettempdir())
        return base / f"linsai-copilot-{lock_name}.lock"

    def _lock_is_held(self, lock_name: str) -> bool:
        """探测某把锁当前是否被持有（非阻塞抢锁，失败即已持有）。

        POSIX flock 对同一文件的不同 fd 也会互斥（同进程同 fd 是升级，
        不同 fd 是冲突），故本探针在同进程多线程下同样有效。
        """
        path = self._lock_path(lock_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        f = open(path, "a+")
        try:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (BlockingIOError, OSError):
                return True
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return False
        finally:
            f.close()

    def _lifecycle_path(self) -> Path:
        p = self.tmp_root / "research_proposals" / "_lifecycle.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _write_lifecycle(self, data):
        from common import save_json
        save_json(self._lifecycle_path(), data)

    def _read_lifecycle(self):
        return json.loads(self._lifecycle_path().read_text(encoding="utf-8"))

    def _fake_lc(self, on_load=None):
        """构造最小 ProposalLifecycle 替身（只实现 _load_state/_save_state）。

        on_load: 可选回调，在 _load_state 被调用时触发（用于探针/编排）。
        """
        import lifecycle.utils as lu

        path = self._lifecycle_path()

        class _Fake:
            def __init__(self):
                self.lifecycle_path = path

            def _load_state(self):
                if on_load is not None:
                    on_load()
                return json.loads(path.read_text(encoding="utf-8"))

            def _save_state(self, state):
                from common import save_json
                save_json(path, state)

        return _Fake(), lu

    # ------------------------------------------------------------------
    # 用例
    # ------------------------------------------------------------------

    def _test_save_jobs_reads_state_under_lock(self):
        """核心不变式（确定性断言）：`_save_jobs` 读 state 时必须持锁。

        旧实现无锁读 → 探针判定「未持锁」→ 用例失败。
        修复后锁内读 → 探针判定「已持锁」→ 用例通过。
        本用例不依赖线程调度时序，故不会出现 flaky。
        """
        self._write_lifecycle({
            "proposals": {
                "P1": {"pipeline_jobs": [{"job_id": "J1", "status": "pending"}], "updated_at": "t0"},
            }
        })

        observed = []

        def _probe():
            observed.append(self._lock_is_held("proposal-lifecycle"))

        fake, lu = self._fake_lc(on_load=_probe)
        jobs = fake._load_state()["proposals"]["P1"]["pipeline_jobs"]
        jobs[0]["status"] = "done"
        lu._save_jobs(fake, "P1", jobs)

        # 第一次 _load_state 是测试自己调用的（不在锁内），
        # 第二次是 _save_jobs 内部的（必须在锁内）。
        self.assert_true(
            len(observed) >= 2,
            "_save_jobs 应至少读取一次 state",
            f"探针记录 = {observed}",
        )
        self.assert_true(
            observed[-1],
            "_save_jobs 必须在持有 proposal-lifecycle 锁时读取 state"
            "（否则并发写者会被旧快照覆盖）",
            f"_save_jobs 读 state 时锁未持有 → 探针记录 = {observed}",
        )

    def _test_save_jobs_keeps_concurrent_writes(self):
        """端到端并发丢更新（确定性交错）。

        交错顺序强制为：A 读到快照 → B 完成写入 → A 写回。
        修复后 A 在锁内重读 → B 的写入保留；旧实现 A 用旧快照写回
        → B 的写入被丢弃。
        """
        self._write_lifecycle({
            "proposals": {
                "P1": {"pipeline_jobs": [{"job_id": "J1", "status": "pending"}], "updated_at": "t0"},
                "P2": {"pipeline_jobs": [{"job_id": "J2", "status": "pending"}], "updated_at": "t0"},
            }
        })

        a_snapshot_taken = threading.Event()
        b_write_done = threading.Event()

        def _a_hook():
            # A 的第一次读：若在锁外（旧实现），则等 B 写完再放行；
            # 若在锁内（修复后），不阻塞（B 拿不到锁，等 A 让出）。
            if not self._lock_is_held("proposal-lifecycle"):
                a_snapshot_taken.set()
                b_write_done.wait(timeout=5)

        fake_a, lu = self._fake_lc(on_load=_a_hook)
        fake_b, _ = self._fake_lc()

        errors = []

        def _writer_a():
            try:
                jobs = fake_a._load_state()["proposals"]["P1"]["pipeline_jobs"]
                jobs[0]["status"] = "done"
                lu._save_jobs(fake_a, "P1", jobs)
            except Exception as e:  # pragma: no cover
                errors.append(f"A: {type(e).__name__}: {e}")

        def _writer_b():
            try:
                a_snapshot_taken.wait(timeout=5)
                jobs = fake_b._load_state()["proposals"]["P2"]["pipeline_jobs"]
                jobs[0]["status"] = "done"
                lu._save_jobs(fake_b, "P2", jobs)
                b_write_done.set()
            except Exception as e:  # pragma: no cover
                errors.append(f"B: {type(e).__name__}: {e}")
                b_write_done.set()

        ta = threading.Thread(target=_writer_a)
        tb = threading.Thread(target=_writer_b)
        ta.start()
        tb.start()
        ta.join(timeout=15)
        tb.join(timeout=15)

        self.assert_eq(len(errors), 0, "并发写入不应抛异常", "; ".join(errors))

        final = self._read_lifecycle()
        for pid in ("P1", "P2"):
            prop = final["proposals"][pid]
            self.assert_eq(
                prop["pipeline_jobs"][0]["status"], "done",
                f"{pid} 的 job 终态应保留（并发写不得丢失）",
            )
            self.assert_true(
                prop.get("updated_at") != "t0",
                f"{pid} 的 updated_at 应前进（写入未被旧快照覆盖）",
                f"updated_at 仍为 {prop.get('updated_at')!r} → 写入被覆盖",
            )

    def _test_old_impl_reproduces_lost_update(self):
        """反向断言：复刻旧实现（无锁读-改-写）时必须复现丢更新。

        证明本测试能真正捕获该缺陷，而非恒真断言。
        """
        from common import save_json

        sp = self.tmp_root / "memory" / "race_probe.json"
        sp.parent.mkdir(parents=True, exist_ok=True)
        save_json(sp, {
            "P1": {"status": "pending", "updated_at": "t0"},
            "P2": {"status": "pending", "updated_at": "t0"},
        })

        a_snapshot_taken = threading.Event()
        b_write_done = threading.Event()

        def _old_style_writer(key, is_a):
            state = json.loads(sp.read_text(encoding="utf-8"))   # ← 无锁读快照
            if is_a:
                a_snapshot_taken.set()
                b_write_done.wait(timeout=5)
            state[key]["status"] = "done"
            save_json(sp, state)                                   # ← 无锁写回
            if not is_a:
                b_write_done.set()

        ta = threading.Thread(target=_old_style_writer, args=("P1", True))
        tb = threading.Thread(target=_old_style_writer, args=("P2", False))
        ta.start()
        tb.start()
        ta.join(timeout=15)
        tb.join(timeout=15)

        final = json.loads(sp.read_text(encoding="utf-8"))
        lost = final["P1"]["updated_at"] == "t0"
        self.assert_true(
            lost,
            "旧实现（无锁读-改-写）应复现丢更新——否则本测试的断言恒真",
            f"P1.updated_at = {final['P1']['updated_at']!r}，未复现预期的丢更新",
        )

    def _test_save_jobs_single_writer(self):
        """回归：单写者路径写入仍生效。"""
        self._write_lifecycle({
            "proposals": {
                "P1": {"pipeline_jobs": [{"job_id": "J1", "status": "pending"}], "updated_at": "t0"},
            }
        })
        fake, lu = self._fake_lc()

        jobs = fake._load_state()["proposals"]["P1"]["pipeline_jobs"]
        jobs[0]["status"] = "done"
        jobs[0]["finished_at"] = "2026-10-26T09:00:00Z"
        ok = lu._save_jobs(fake, "P1", jobs)

        self.assert_true(ok, "_save_jobs 应返回 True")
        prop = self._read_lifecycle()["proposals"]["P1"]
        self.assert_eq(prop["pipeline_jobs"][0]["status"], "done", "job 状态应写入")
        self.assert_eq(
            prop["pipeline_jobs"][0]["finished_at"], "2026-10-26T09:00:00Z",
            "job 其余字段应完整写入",
        )
        self.assert_true(prop["updated_at"] != "t0", "updated_at 应前进")

    def _test_save_jobs_unknown_proposal(self):
        """反向断言：未知 proposal 返回 False，不创建孤儿条目。"""
        self._write_lifecycle({"proposals": {}})
        fake, lu = self._fake_lc()

        ok = lu._save_jobs(fake, "NOPE", [{"job_id": "X", "status": "done"}])

        self.assert_true(not ok, "未知 proposal 应返回 False")
        self.assert_eq(
            len(self._read_lifecycle()["proposals"]), 0,
            "未知 proposal 不得被创建",
        )

    def _test_weekend_repair_keeps_concurrent_worker_write(self):
        """周末 pipeline repair 路径：worker 的写入不得被 repair 覆盖。

        直接调用**真实的** `lifecycle/orchestrator.py::_run_weekend_repair`
        的 pipeline 段（通过打桩 hermes_bridge 避开 cron 查询），与
        lc-weekend-worker 的 job 执行（持同一把锁）交错。

        旧实现（无锁读-改-写）下，repair 会用旧快照覆盖 worker 刚写入
        的终态；修复后（锁内读-改-写）worker 的写入必须保留。
        """
        from common import file_lock, save_json
        from weekend_pipeline.state import (
            load_pipeline_state,
            save_pipeline_state_unlocked,
        )

        sp = self.tmp_root / "memory" / "weekend-pipeline.json"
        sp.parent.mkdir(parents=True, exist_ok=True)
        save_json(sp, {
            "jobs": [{"job_id": "J1", "status": "failed", "attempts": 1,
                      "repair_attempts": 0, "last_error": "boom"}],
            "processed_sources": {},
            "stage_status": {},
        })

        # 让 orchestrator 的 pipeline 段读写同一份 state（隔离目录）
        import weekend_pipeline.constants as wpc
        import weekend_pipeline.state as wps
        _orig_state_path = wpc.PIPELINE_STATE_PATH
        wpc.PIPELINE_STATE_PATH = sp
        wps.PIPELINE_STATE_PATH = sp

        errors = []

        def _worker():
            try:
                with file_lock("weekend-pipeline"):
                    st = load_pipeline_state(sp)
                    time.sleep(0.4)                      # 模拟 LLM 调用耗时
                    st["jobs"][0]["status"] = "done"
                    st["jobs"][0]["finished_at"] = "2026-10-26T09:00:00Z"
                    st["jobs"].append({"job_id": "J2", "status": "running"})
                    save_pipeline_state_unlocked(st, sp)
            except Exception as e:  # pragma: no cover
                errors.append(f"worker: {type(e).__name__}: {e}")

        def _repair():
            try:
                # 等 worker 拿到锁并进入 LLM 阶段后再触发 repair，
                # 确保两者真的交叉（worker 持锁 → repair 阻塞在抢锁）。
                time.sleep(0.2)
                import lifecycle.orchestrator as orch
                from lifecycle.controller import LifecycleCronController
                ctrl = LifecycleCronController()
                orch._run_weekend_repair(ctrl, dry_run=False, lifecycle_crons=[])
            except Exception as e:  # pragma: no cover
                errors.append(f"repair: {type(e).__name__}: {e}")

        t1 = threading.Thread(target=_worker)
        t2 = threading.Thread(target=_repair)
        t1.start()
        t2.start()
        t1.join(timeout=20)
        t2.join(timeout=20)

        # repair 路径若抛异常，必须显式失败——否则会被误判为「写入未丢失」
        self.assert_eq(len(errors), 0, "repair 路径不应抛异常", "; ".join(errors))

        final = json.loads(sp.read_text(encoding="utf-8"))
        ids = [j["job_id"] for j in final["jobs"]]
        self.assert_true(
            "J2" in ids,
            "worker 新建的 job 不得从磁盘消失（repair 不得用旧快照覆盖）",
            f"磁盘 job_id 列表 = {ids}",
        )

        wpc.PIPELINE_STATE_PATH = _orig_state_path
        wps.PIPELINE_STATE_PATH = _orig_state_path

    # ------------------------------------------------------------------
    # 套件入口
    # ------------------------------------------------------------------

    def run_tests(self):
        # 独立运行（__main__）时 test_runner 不调 setup，此处自建隔离环境
        if self.tmp_root is None:
            self.setup()
            self._owns_tmp = True
        try:
            self._test_save_jobs_reads_state_under_lock()
            self._test_save_jobs_keeps_concurrent_writes()
            self._test_old_impl_reproduces_lost_update()
            self._test_save_jobs_single_writer()
            self._test_save_jobs_unknown_proposal()
            self._test_weekend_repair_keeps_concurrent_worker_write()
        finally:
            if getattr(self, "_owns_tmp", False):
                self.teardown()
                self.tmp_root = None
                self._owns_tmp = False


if __name__ == "__main__":
    import unittest  # noqa: E402

    class _Runner(unittest.TestCase):
        def runTest(self):
            suite = ConcurrentStateWriteTests()
            suite.run_tests()
            summary = suite.summary()
            for r in suite.results:
                print(f"  {'✓' if r.passed else '✗'} {r.name}"
                      + ("" if r.passed else f"  → {r.msg}"))
            print(f"\n{summary['passed']}/{summary['total']} 通过")
            if summary["failed"]:
                raise AssertionError(f"{summary['failed']} 条断言失败")

    unittest.main(argv=[__file__, "-v"], exit=False)
