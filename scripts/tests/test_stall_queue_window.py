#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_stall_queue_window.py — 停滞检测的轮转队列键一致性回归（v7.2.70）

覆盖缺陷 BUG-27：v7.2.66 引入轮转 WIP 硬窗口
（`micro_scheduler.MAX_ROTATION_WIP = 3`）后，`_sync_queue` 双键维护
轮转名单：

    queue_full = 完整候补名单（全部 optimizing 课题）
    queue      = 前 MAX_ROTATION_WIP 个（WIP 硬窗口）

而 `lifecycle_monitor._get_proposal_queue_position()` 仍只读 `queue`
→ WIP 窗口外的候补课题返回 queue_index=-1
→ 命中 `_classify_stall_kind` 分支 5「不在 focus queue 中，上游调度
未接管」= **blocked**（真停滞）
→ 正常候补课题被误发 `stalled` 真停滞告警。

实测（2026-10-31 04h）：7 个 optimizing 课题中 4 个候补被判 blocked。

本套件以 TestSuite 风格编写（纳入 `self_test --module` 全量回归），
覆盖：
    1. 队列位置解析以 `queue_full` 为准（WIP 窗口外仍能定位）
    2. WIP 窗口外候补课题分类为 queue_tail（非真停滞）
    3. 完整链路：`_check_proposal_stall` 不发 stalled 告警
    4. 真停滞场景不受影响（真 failed 阻塞仍判 blocked）
    5. 兼容回退：无 `queue_full` 键时回退旧 `queue` 键
"""

import sys
import importlib
import json
import shutil
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test_runner import TestSuite

# 固定时间锚：10 天前（done job）——跨多个周末，净工时必然 ≥ 48h 阈值
_NOW = datetime.now(timezone.utc)
_T_10D_AGO = _NOW - timedelta(days=10)


def _iso_z(dt):
    return dt.isoformat().replace("+00:00", "Z")


class StallQueueWindowTests(TestSuite):
    def __init__(self):
        super().__init__("停滞检测的轮转队列键一致性测试（v7.2.70 BUG-27）")
        self.tmp_root = None
        self.lm = None
        self._focus_path = None
        self._backup = None

    # ── 夹具 ──────────────────────────────────────────────

    # v7.2.105（BUG-34）：monitor 读轮转名单时按「真实课题白名单」过滤
    # 非法成员（测试夹具占位 id 等），白名单来源是 `_lifecycle.json` 的
    # proposals 集合。本套件的夹具 id（filler-N / test-*-only）不是真实
    # 课题 → 必须登记进隔离环境的 `_lifecycle.json`，否则 monitor 会把
    # 它们全部剔除 → queue_total 归零 → 队列位置解析断言全部失真。
    # 登记后过滤对本套件是恒等变换，断言意图（queue_full 为准 / 窗口外
    # 候补定位 / 旧键回退）完整保留。
    FIXTURE_IDS = (
        [f"filler-{i}" for i in range(6)]
        + ["test-wip-window-candidate"]
        + [f"legacy-{i}" for i in range(5)]
        + ["test-legacy-only"]
    )

    def setup(self):
        self.tmp_root = Path(tempfile.mkdtemp(prefix="linsai_stall_window_"))
        for mod_name in list(sys.modules.keys()):
            if mod_name in ("lifecycle_monitor", "paths", "common"):
                del sys.modules[mod_name]
        self.lm = importlib.import_module("lifecycle_monitor")
        import paths
        paths.PROJECT_ROOT = self.tmp_root
        self.lm.PROJECT_ROOT = self.tmp_root

        mem = self.tmp_root / "memory"
        mem.mkdir(parents=True, exist_ok=True)
        self._focus_path = mem / "lifecycle-focus.json"
        self._backup = None

        # 登记夹具 id 为「已知课题」（隔离环境，真实数据零接触）
        lc_dir = self.tmp_root / "research_proposals"
        lc_dir.mkdir(parents=True, exist_ok=True)
        (lc_dir / "_lifecycle.json").write_text(
            json.dumps({
                "proposals": {pid: {"status": "optimizing"} for pid in self.FIXTURE_IDS},
                "updated_at": "2026-11-02T00:00:00Z",
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def teardown(self):
        # v8.0.2：恢复被 _pin_chain_age 替换的模块级缓存，防跨套件污染
        if self.lm is not None and hasattr(self.lm, "_chain_activity_cache"):
            self.lm._chain_activity_cache = {}
        if self._focus_path and self._backup is not None:
            try:
                self._focus_path.write_text(self._backup, encoding="utf-8")
            except Exception:
                pass
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_focus(self, payload: dict):
        self._focus_path.write_text(
            __import__("json").dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8")

    def _make_jobs(self, n_done=10, n_pending=20):
        jobs = []
        for i in range(n_done):
            jobs.append({
                "job_id": f"job-done-{i}",
                "status": "done",
                "finished_at": _iso_z(_T_10D_AGO),
                "started_at": _iso_z(_T_10D_AGO),
                "depends_on": [],
            })
        for i in range(n_pending):
            jobs.append({
                "job_id": f"job-pending-{i}",
                "status": "pending",
                "finished_at": "",
                "started_at": "",
                "depends_on": [],
            })
        return jobs

    def _make_proposal(self, pid, jobs):
        return {"proposal_id": pid, "updated_at": _iso_z(_T_10D_AGO),
                "pipeline_jobs": jobs}

    def _pin_chain_age(self, hours):
        """固定全链活动龄（避免受真实看板影响）。"""
        self.lm._chain_activity_cache = {"age": hours}

    # ── 用例 ──────────────────────────────────────────────

    def run_tests(self):
        # 1. 队列位置解析以 queue_full 为准
        # 名单 6 项，WIP 窗口 = 前 3 项（queue[:3]），本课题置于 queue_full[3]
        # —— 窗口外但**非队尾**（队尾 = 后 1/3 = 索引 ≥ 6-max(2, 6//3)=4）。
        pid = "test-wip-window-candidate"
        full = [f"filler-{i}" for i in range(6)]
        full[3] = pid
        self._write_focus({
            "queue": full[:3],
            "queue_full": full,
        })
        idx, total = self.lm._get_proposal_queue_position(pid)
        self.assert_eq(idx, 3, "WIP 窗口外课题应读到 queue_full 位置 3")
        self.assert_eq(total, 6, "queue_total 应以 queue_full 完整名单为准")

        # 2. 分类为 queue_tail（非真停滞）
        # v8.0.2：固定全链活动龄——此用例此前隐式依赖真实看板的新鲜度，
        # v7 优化环停用后看板活动龄 >24h 阈值，分类翻转为 rotation_stall
        # （2026-11-17 实证）。分类逻辑测试不应受环境状态影响。
        self._pin_chain_age(1.0)
        jobs = self._make_jobs()
        kind, detail = self.lm._classify_stall_kind(pid, jobs, pending_count=20)
        self.assert_eq(kind, "queue_tail",
                       "WIP 窗口外候补应判 queue_tail 而非 blocked")
        self.assert_true(detail.get("is_queue_tail") is False,
                         "非队尾标记应显式为 False",
                         f"detail={detail}")

        # 3. 完整链路不发 stalled 告警
        p = self._make_proposal(pid, jobs)
        anomalies = []
        self._pin_chain_age(1.0)
        self.lm._check_proposal_stall(pid, p, jobs, len(jobs), 20, anomalies)
        kinds = [a.get("type") for a in anomalies]
        self.assert_true("stalled" not in kinds,
                         "WIP 窗口外候补不应发 stalled 真停滞告警",
                         f"kinds={kinds}")
        self.assert_in("queue_tail_warn", kinds,
                       "应发 queue_tail_warn 低优先级提示")

        # 4. 真停滞场景不受影响：failed 且 attempts 用尽 → job_stuck
        jobs2 = self._make_jobs(n_done=10, n_pending=5)
        jobs2.append({
            "job_id": "job-failed-stuck",
            "status": "failed",
            "attempts": 3,
            "finished_at": _iso_z(_T_10D_AGO),
            "started_at": _iso_z(_T_10D_AGO),
            "depends_on": [],
        })
        # 让 pending job 依赖该 failed job
        jobs2[-2]["depends_on"] = ["job-failed-stuck"]
        p2 = self._make_proposal("test-real-stuck", jobs2)
        anomalies2 = []
        self.lm._check_proposal_stall("test-real-stuck", p2, jobs2,
                                      len(jobs2), 10, anomalies2)
        kinds2 = [a.get("type") for a in anomalies2]
        self.assert_in("stalled", kinds2, "真 failed 阻塞仍应发 stalled 告警")

        # 5. 兼容回退：无 queue_full 键时回退旧 queue 键
        legacy = [f"legacy-{i}" for i in range(5)]
        legacy[2] = "test-legacy-only"
        self._write_focus({"queue": legacy})
        idx3, total3 = self.lm._get_proposal_queue_position("test-legacy-only")
        self.assert_eq(idx3, 2, "无 queue_full 键时应回退读 queue 键")
        self.assert_eq(total3, 5, "回退路径的 queue_total 应等于 queue 长度")


if __name__ == "__main__":
    suite = StallQueueWindowTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    passed = sum(1 for r in suite.results if r.passed)
    for r in suite.results:
        print(f"  {'✓' if r.passed else '✗'} {r.name}" +
              ("" if r.passed else f" — {r.msg}"))
    print(f"\n{passed}/{len(suite.results)} 通过")
    raise SystemExit(0 if passed == len(suite.results) else 1)
