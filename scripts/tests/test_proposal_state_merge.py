#!/usr/bin/env python3
"""
test_proposal_state_merge.py — proposal 状态写入的字段级合并回归（v7.2.50）

背景（2026-10-27 00h 健康检查 deep_scan v56 存量深扫发现，BUG-15/16/17）：
    BUG-12（v7.2.48）修了 `_save_jobs` 的无锁读-改-写，但同一条
    `_lifecycle.json` 共享状态文件上还有三条**同根因但未被覆盖**的路径：

      1. BUG-15 `_set_proposal_state` 整份替换 proposal 条目
         —— 它把调用方**锁外旧快照**里的 pipeline_jobs 一并写回，与
         `_save_jobs` 交叉时对方的 job 终态被丢弃（job 回退 pending
         → 被重复执行，整轮 LLM 重跑）。
         生产实测更严重的一环：monitor 步骤先 `archive_old_round_jobs`
         从磁盘删除旧轮次 job，随后 `_set_proposal_state` 用旧快照把
         已归档的 job **复活**（实测 9 课题 251 条旧轮次 job 同时存在
         于活链与归档文件，双重计数）。

      2. BUG-16 `archive_old_round_jobs` 无锁读-改-写
         —— 用旧快照把并发写者刚写入的 job 终态整份覆盖。

      3. BUG-17 `restart_stalled_failed_job` 直接改写 pipeline_jobs
         —— 与 _save_jobs 竞争的第三条写路径。

    本测试覆盖：
      1. `_set_proposal_state` 默认不覆盖磁盘上的 pipeline_jobs（BUG-15）；
      2. `update_jobs=True` 显式意图路径仍能改写 pipeline_jobs（退回清空）；
      3. 归档后 `_set_proposal_state` 不得复活已归档 job（生产实证路径）；
      4. `archive_old_round_jobs` 锁内读-改-写，不覆盖并发写者（BUG-16）；
      5. 反向断言：复刻旧实现时必须复现丢更新（证明测试非恒真）。

注意：本测试不调用 LLM，运行于隔离临时目录，零生产副作用。
"""

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


class ProposalStateMergeTests(TestSuite):
    def __init__(self):
        super().__init__("proposal 状态字段级合并回归测试（v7.2.50）")
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
        patch_module_root("lifecycle", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    # ------------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------------

    def _lifecycle_path(self) -> Path:
        p = self.tmp_root / "research_proposals" / "_lifecycle.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _write_lifecycle(self, data):
        from common import save_json
        save_json(self._lifecycle_path(), data)

    def _read_lifecycle(self):
        return json.loads(self._lifecycle_path().read_text(encoding="utf-8"))

    def _lc(self):
        """构造走真实 StateMixin._set_proposal_state 的最小实例。"""
        from proposal_lifecycle.state import StateMixin

        path = self._lifecycle_path()

        class _Real(StateMixin):
            def __init__(self):
                self.lifecycle_path = path
                self.root = path.parent

            def _ensure_lifecycle_state(self):
                pass

        return _Real()

    # ------------------------------------------------------------------
    # 用例
    # ------------------------------------------------------------------

    def _test_set_proposal_state_keeps_disk_pipeline_jobs(self):
        """BUG-15：`_set_proposal_state` 不得用旧快照覆盖磁盘上的 pipeline_jobs。

        真实触发场景（executor._run_writer_step / _run_monitor_step）：
        读 prop_state 快照 → LLM 调用（数分钟）→ 并发写者写入 job 终态
        → `_set_proposal_state` 写回快照 → 并发写者的终态被丢弃。
        """
        self._write_lifecycle({
            "proposals": {
                "P1": {
                    "pipeline_jobs": [{"job_id": "J1", "status": "running"}],
                    "updated_at": "t0",
                    "last_score": 0.5,
                },
            }
        })
        lc = self._lc()

        # writer 侧：读快照（锁外）
        snapshot = lc._get_proposal_state("P1")
        self.assert_true(
            snapshot is not None and "pipeline_jobs" in snapshot,
            "快照应含 pipeline_jobs（模拟调用方传入的整份 state）",
        )

        # 并发写者：把 J1 标记 done（走 _save_jobs 的写路径语义）
        from common import file_lock
        with file_lock("proposal-lifecycle"):
            state = lc._load_state()
            state["proposals"]["P1"]["pipeline_jobs"][0]["status"] = "done"
            state["proposals"]["P1"]["updated_at"] = "t1_concurrent"
            lc._save_state(state)

        # writer 收尾：基于旧快照写回分数
        snapshot["last_score"] = 0.88
        snapshot["score_history"] = [{"round": 3, "score": 0.88}]
        lc._set_proposal_state("P1", snapshot)

        prop = self._read_lifecycle()["proposals"]["P1"]
        self.assert_eq(
            prop["pipeline_jobs"][0]["status"], "done",
            "并发写者写入的 job 终态不得被 _set_proposal_state 的旧快照覆盖"
            "（否则 job 回退 pending → 整轮 LLM 重跑）",
        )
        self.assert_eq(
            prop.get("last_score"), 0.88,
            "调用方快照里的非 job 字段仍须正常落盘",
        )

    def _test_set_proposal_state_update_jobs_flag(self):
        """`update_jobs=True` 显式意图路径仍能改写 pipeline_jobs。

        对应「审核退回清空旧轮次 job」场景（transitions.py）：
        归档旧 job 后把 pipeline_jobs 置空，必须真正落盘。
        """
        self._write_lifecycle({
            "proposals": {
                "P1": {
                    "pipeline_jobs": [{"job_id": "J1", "status": "done"}],
                    "updated_at": "t0",
                },
            }
        })
        lc = self._lc()

        prop_state = lc._get_proposal_state("P1")
        prop_state["pipeline_jobs"] = []
        prop_state["optimization_rounds"] = 0
        lc._set_proposal_state("P1", prop_state, update_jobs=True)

        prop = self._read_lifecycle()["proposals"]["P1"]
        self.assert_eq(
            len(prop.get("pipeline_jobs") or []), 0,
            "update_jobs=True 时 pipeline_jobs 清空必须生效（退回归档场景）",
        )
        self.assert_eq(
            prop.get("optimization_rounds"), 0,
            "退回时 optimization_rounds 归零须落盘",
        )

    def _test_archived_jobs_not_resurrected(self):
        """BUG-15 生产实证：归档后的旧轮次 job 不得被 _set_proposal_state 复活。

        真实时序（executor._run_monitor_step）：
          L2318  prop_state = _get_proposal_state()   ← 快照含旧轮次 job
          L2420  archive_old_round_jobs(...)          ← 从磁盘删除旧轮次 job
          L2428  _set_proposal_state(prop_state)      ← 旧快照把 job 写回 → 复活
        """
        jobs = (
            [{"job_id": f"r1-j{i}", "round": 1, "status": "done"} for i in range(3)]
            + [{"job_id": f"r2-j{i}", "round": 2, "status": "done"} for i in range(3)]
            + [{"job_id": f"r3-j{i}", "round": 3, "status": "pending"} for i in range(3)]
        )
        self._write_lifecycle({
            "proposals": {
                "P1": {"pipeline_jobs": jobs, "optimization_rounds": 2, "updated_at": "t0"},
            }
        })

        import lifecycle.utils as lu
        lu.PROJECT_ROOT = self.tmp_root
        lu.LIFECYCLE_ARCHIVE_PATH = self.tmp_root / "research_proposals" / "_lifecycle_archive.json"

        lc = self._lc()
        prop_state = lc._get_proposal_state("P1")     # 快照（含 r1/r2/r3）
        prop_state["optimization_rounds"] = 3

        cleaned = lu.archive_old_round_jobs("P1", 3)
        self.assert_eq(cleaned, 6, "archive 应归档 6 条旧轮次 job")

        after_archive = self._read_lifecycle()["proposals"]["P1"]["pipeline_jobs"]
        self.assert_eq(
            sorted({j["round"] for j in after_archive}), [3],
            "归档后磁盘上只应保留当前轮次 job",
        )

        # monitor 收尾：用旧快照写回
        prop_state["last_monitor_score"] = 0.85
        lc._set_proposal_state("P1", prop_state)

        after_write = self._read_lifecycle()["proposals"]["P1"]["pipeline_jobs"]
        resurrected = [j for j in after_write if j.get("round", 0) < 3]
        self.assert_eq(
            len(resurrected), 0,
            "已归档的旧轮次 job 不得被 _set_proposal_state 的旧快照复活"
            "（生产实测 251 条双重计数）",
            f"复活了 {len(resurrected)} 条：{[j.get('job_id') for j in resurrected][:5]}",
        )

    def _test_archive_keeps_concurrent_write(self):
        """BUG-16：`archive_old_round_jobs` 不得覆盖并发写者的写入。

        旧实现为无锁读-改-写，与 `_save_jobs` 交叉时用旧快照覆盖
        对方刚写入的 job 终态。

        交错用**锁探针**强制（确定性，不依赖线程调度运气）：
        archive 读 state 时若**未持锁**（旧实现），就等 worker 写完再
        继续 → 必然用旧快照覆盖；修复后 archive 持锁读，worker 拿不到
        锁只能等 → archive 基于最新磁盘状态裁剪，worker 写入随后生效。
        """
        jobs = (
            [{"job_id": f"r{i}-j0", "round": i, "status": "done"} for i in (1, 2, 3)]
            + [{"job_id": "r4-j0", "round": 4, "status": "pending"}]
        )
        self._write_lifecycle({
            "proposals": {"P1": {"pipeline_jobs": jobs, "optimization_rounds": 3}}
        })

        import lifecycle.utils as lu
        lu.PROJECT_ROOT = self.tmp_root
        lu.LIFECYCLE_ARCHIVE_PATH = self.tmp_root / "research_proposals" / "_lifecycle_archive.json"

        errors = []
        a_snapshot_taken = threading.Event()
        b_write_done = threading.Event()

        def _lock_is_held(lock_name: str) -> bool:
            """探针：某把锁当前是否被持有。"""
            import fcntl
            lock_dir = os.environ.get("LINSAI_LOCK_DIR")
            base = Path(lock_dir) if lock_dir else Path(tempfile.gettempdir())
            base.mkdir(parents=True, exist_ok=True)
            f = open(base / f"linsai-copilot-{lock_name}.lock", "a+")
            try:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except (BlockingIOError, OSError):
                    return True
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return False
            finally:
                f.close()

        def _archive():
            try:
                orig_load = lu.load_json
                probed = {"done": False}

                def _probe_load(path, *a, **k):
                    r = orig_load(path, *a, **k)
                    if not probed["done"]:
                        probed["done"] = True
                        if not _lock_is_held("proposal-lifecycle"):
                            # 旧实现：无锁读快照 → 等 worker 写完 → 必然覆盖
                            a_snapshot_taken.set()
                            b_write_done.wait(timeout=5)
                    return r

                lu.load_json = _probe_load
                try:
                    lu.archive_old_round_jobs("P1", 4)
                finally:
                    lu.load_json = orig_load
            except Exception as e:  # pragma: no cover
                errors.append(f"archive: {type(e).__name__}: {e}")

        def _worker():
            try:
                from common import file_lock, save_json
                a_snapshot_taken.wait(timeout=5)
                with file_lock("proposal-lifecycle"):
                    d = json.loads(self._lifecycle_path().read_text(encoding="utf-8"))
                    d["proposals"]["P1"]["pipeline_jobs"][0]["status"] = "done-v2"
                    save_json(self._lifecycle_path(), d)
                b_write_done.set()
            except Exception as e:  # pragma: no cover
                errors.append(f"worker: {type(e).__name__}: {e}")
                b_write_done.set()

        ta = threading.Thread(target=_archive)
        tb = threading.Thread(target=_worker)
        ta.start()
        tb.start()
        ta.join(timeout=20)
        tb.join(timeout=20)

        self.assert_eq(len(errors), 0, "并发写入不应抛异常", "; ".join(errors))

        final = self._read_lifecycle()["proposals"]["P1"]
        self.assert_eq(
            final["pipeline_jobs"][0]["status"], "done-v2",
            "archive_old_round_jobs 不得用旧快照覆盖并发写者的 job 终态",
        )

    def _test_old_impl_reproduces_lost_update(self):
        """反向断言：复刻旧实现（无锁读-改-写）时必须复现丢更新。

        证明本测试能真正捕获该缺陷，而非恒真断言。

        交错：A 读快照 → B 写 P2=done → A 用旧快照写回 → **P2 的写入
        被丢弃**（P2 回到 pending）。
        """
        sp = self.tmp_root / "memory" / "race_probe_merge.json"
        sp.parent.mkdir(parents=True, exist_ok=True)
        from common import save_json
        save_json(sp, {"P1": {"status": "pending"}, "P2": {"status": "pending"}})

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
        self.assert_true(
            final["P2"]["status"] == "pending",
            "旧实现（无锁读-改-写）应复现丢更新——否则本测试断言恒真",
            f"P2.status = {final['P2']['status']!r}，未复现预期的丢更新",
        )

    def run_tests(self):
        if self.tmp_root is None:
            self.setup()
            self._owns_tmp = True
        try:
            self._test_set_proposal_state_keeps_disk_pipeline_jobs()
            self._test_set_proposal_state_update_jobs_flag()
            self._test_archived_jobs_not_resurrected()
            self._test_archive_keeps_concurrent_write()
            self._test_old_impl_reproduces_lost_update()
        finally:
            if getattr(self, "_owns_tmp", False):
                self.teardown()
                self.tmp_root = None
                self._owns_tmp = False


if __name__ == "__main__":
    import unittest  # noqa: E402

    class _Runner(unittest.TestCase):
        def runTest(self):
            suite = ProposalStateMergeTests()
            suite.run_tests()
            summary = suite.summary()
            for r in suite.results:
                print(f"  {'✓' if r.passed else '✗'} {r.name}"
                      + ("" if r.passed else f"  → {r.msg}"))
            print(f"\n{summary['passed']}/{summary['total']} 通过")
            if summary["failed"]:
                raise AssertionError(f"{summary['failed']} 条断言失败")

    unittest.main(argv=[__file__, "-v"], exit=False)
