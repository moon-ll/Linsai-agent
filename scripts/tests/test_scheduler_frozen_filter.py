#!/usr/bin/env python3
"""BUG-46 回归测试：scheduler_frozen 冻结过滤死路径。

背景（2026-11-06 08h 健康检查发现，v7.3.50 修复）：

`micro_scheduler._sync_queue` 依据 `optimizing` 列表里的
`scheduler_frozen` 标志把冻结课题剔出轮转名单（v7.2.66 组合手术「定案 4」：
berry 置 scheduler_frozen + WIP 硬窗口）。但该标志的**唯一数据来源**
`proposal_lifecycle.transitions.list_by_status` 从未把该键放进返回字典
→ `p.get("scheduler_frozen")` 恒为 None → 冻结集合恒为空 → 过滤恒不命中
（结构性死路径）。

后果：
- 冻结课题仍会被追加进轮转窗口（`queue`），挤占 MAX_ROTATION_WIP=3 的名额；
- 「解冻只需清标志，下个 tick 自动召回」的 pull-based 语义失效——解冻后
  课题会**重复**被追加（已在 queue 里则不追加，但冻结期间它被永久排除在
  窗口外，队列位置丢失）；
- 生产实证：berry 的 scheduler_frozen=True（v7.2.66 置位、v7.3.46 再次置位）
  从未真正阻断其进入轮转名单。

本测试覆盖：
- list_by_status 必须返回 scheduler_frozen 键（布尔归一）
- 冻结课题被 _sync_queue 剔出轮转窗口
- 未冻结课题不受影响
- 冻结 + 解冻（清标志）后能被重新召回（pull-based 语义）
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lifecycle.micro_scheduler import _load_focus_state, _sync_queue


class _FakeLifecycle:
    """最小 ProposalLifecycle 替身：只提供 list_by_status 所需字段。"""

    def __init__(self, proposals):
        self._proposals = proposals

    def list_by_status(self, status=None):
        out = []
        for pid, data in self._proposals.items():
            if status and data.get("status") != status:
                continue
            out.append({
                "proposal_id": pid,
                "status": data.get("status"),
                "project_type": data.get("project_type", "general"),
                "optimization_rounds": data.get("optimization_rounds", 0),
                "last_score": data.get("last_score", 0.0),
                "updated_at": data.get("updated_at", ""),
                "panel_review_requested": data.get("panel_review_requested", False),
                "scheduler_frozen": bool(data.get("scheduler_frozen", False)),
            })
        return out


class TestSchedulerFrozenFilter(unittest.TestCase):
    """BUG-46 回归：冻结课题必须真正被剔出轮转窗口。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.frozen_pid = "prop-frozen-20261106"
        self.free_pid = "prop-free-20261106"

    def tearDown(self):
        self._td.cleanup()

    def _state(self):
        return {"queue": [], "queue_full": [], "queue_index": 0}

    def _opt(self, frozen=True):
        return _FakeLifecycle({
            self.frozen_pid: {"status": "optimizing", "scheduler_frozen": frozen},
            self.free_pid: {"status": "optimizing", "scheduler_frozen": False},
        }).list_by_status("optimizing")

    # ── 1) list_by_status 必须暴露 scheduler_frozen ─────────────────
    def test_list_by_status_exposes_scheduler_frozen(self):
        """list_by_status 返回项必须含 scheduler_frozen 键（BUG-46 根因点）。"""
        from proposal_lifecycle.transitions import TransitionsMixin
        import inspect
        src = inspect.getsource(TransitionsMixin.list_by_status)
        self.assertIn("scheduler_frozen", src,
                      "list_by_status 仍未返回 scheduler_frozen —— 冻结过滤仍是死路径")

    def test_list_by_status_returns_true_flag(self):
        """真实实现：冻结课题返回 scheduler_frozen=True。"""
        from proposal_lifecycle.state import StateMixin
        from proposal_lifecycle.transitions import TransitionsMixin
        from proposal_lifecycle import ProposalLifecycle
        import json
        import os

        tmp = Path(self._td.name) / "_lifecycle.json"
        tmp.write_text(json.dumps({
            "proposals": {
                "p-frozen": {"status": "optimizing", "scheduler_frozen": True},
                "p-free": {"status": "optimizing"},
            }
        }, ensure_ascii=False), encoding="utf-8")

        class _PL(ProposalLifecycle):
            def _load_state(self):
                return json.loads(tmp.read_text(encoding="utf-8"))

        pl = _PL()
        rows = {r["proposal_id"]: r for r in pl.list_by_status("optimizing")}
        self.assertTrue(rows["p-frozen"]["scheduler_frozen"])
        self.assertFalse(rows["p-free"]["scheduler_frozen"])

    # ── 2) 冻结课题被剔出轮转窗口 ───────────────────────────────────
    def test_frozen_proposal_excluded_from_queue(self):
        """冻结课题不得进入轮转窗口。"""
        state = self._state()
        q = _sync_queue(state, self._opt(frozen=True))
        self.assertNotIn(self.frozen_pid, q, "冻结课题仍在轮转窗口内")
        self.assertIn(self.free_pid, q, "未冻结课题被误排除")

    def test_frozen_proposal_removed_from_existing_queue(self):
        """已在窗口内的冻结课题应被主动剔除。"""
        state = self._state()
        state["queue"] = [self.frozen_pid, self.free_pid]
        q = _sync_queue(state, self._opt(frozen=True))
        self.assertNotIn(self.frozen_pid, q, "已有队列中的冻结课题未被剔除")

    def test_unfrozen_proposal_recalled(self):
        """解冻（清标志）后应被自动召回（pull-based 语义）。"""
        state = self._state()
        state["queue"] = [self.free_pid]
        q = _sync_queue(state, self._opt(frozen=False))
        self.assertIn(self.frozen_pid, q, "解冻后未被召回")

    def test_frozen_proposal_not_in_queue_full(self):
        """冻结课题不得被塞进候补单（queue_full）。"""
        state = self._state()
        _sync_queue(state, self._opt(frozen=True))
        self.assertNotIn(self.frozen_pid, state.get("queue_full", []))


if __name__ == "__main__":
    unittest.main()
