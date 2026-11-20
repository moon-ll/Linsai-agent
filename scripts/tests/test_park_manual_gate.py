#!/usr/bin/env python3
"""
test_park_manual_gate.py — 平台课题 park 机制回归（v7.3.83）

背景：用户裁决 2026-11-15 token 治理④——平台/收敛此前只挂 quality_warning
而轮转照跑，bsv 实证 15 轮 0.80 原地（高轮次零收益空转）。高位平台且方法
手册门未过线（晋级无路）时自动冻结轮转（scheduler_frozen）+ 进等人队列
转人工；手册已过线不冻（正常晋级路径仍通）。

覆盖：
    1. 次优平台（0.80-0.85 平台）+ 手册门未过线 → 冻结 + reason 含"转人工"
    2. 次优平台 + 手册已过线 → 不冻结（正常晋级路径仍通）
    3. 质量收敛（≥0.85 平台）+ 手册门未过线 → 冻结
    4. 等人队列：parked 课题产出 type=parked 队列项
    5. 等人队列：executor 写冲突冻结（reason 无"转人工"）不进队列

注意：零 LLM、零网络、状态 mock 隔离（沿用 test_quality_ceiling_convergence
的磁盘新读语义 mock）。
"""

import copy
import sys
import importlib
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite, create_isolated_env


class ParkManualGateTests(TestSuite):
    def __init__(self):
        super().__init__("平台课题 park 机制测试（v7.3.83）")
        self.tmp_root = None
        self._comp = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in [
            "proposal_lifecycle.completion",
            "proposal_lifecycle",
            "proposal_sections",
        ]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.completion")
        from proposal_lifecycle.completion import CompletionMixin

        class _StateHolder:
            def __init__(self):
                self._disk = {}
                self.set_calls = []

            def _get_proposal_state(self, proposal_id):
                return copy.deepcopy(self._disk.get(proposal_id))

            def _set_proposal_state(self, proposal_id, state):
                self._disk[proposal_id] = copy.deepcopy(state)
                self.set_calls.append(proposal_id)
                return True

        class _FakeComp(CompletionMixin, _StateHolder):
            def __init__(self):
                _StateHolder.__init__(self)

        self._comp = _FakeComp()

    def teardown(self):
        pass

    def run_tests(self):
        comp = self._comp
        threshold = {"min_overall_score": 0.85}
        sections = ["rationale", "content", "scheme", "full_review", "references"]

        def _state(scores, manual_passed=False):
            # method_manual 是第六评审模块（v7.3.0），不在 5 章节清单里；
            # 键缺失与 False 同义（未过线）——与 completion 门检查语义一致。
            sp = {k: False for k in sections}
            sp["method_manual"] = manual_passed
            comp._set_proposal_state("p1", {
                "status": "optimizing",
                "score_history": [{"score": s} for s in scores],
                "last_score": scores[-1],
                "section_passes": sp,
                "optimization_rounds": len(scores),
                "monitor_history": [],
                "open_critical_issues": [],
            })

        # ---------- 1. 次优平台 + 手册门未过线 → 冻结转人工 ----------
        _state([0.79, 0.81, 0.82, 0.82, 0.82], manual_passed=False)
        res = comp._check_done("p1", threshold)
        self.assert_eq(res["done"], False, "次优平台不自动晋级（原有语义不变）")
        st = comp._get_proposal_state("p1")
        self.assert_eq(st.get("scheduler_frozen"), True,
                       "手册门未过线的次优平台应冻结轮转")
        self.assert_in("转人工", st.get("scheduler_frozen_reason") or "",
                       "冻结原因应标注转人工")

        # ---------- 2. 次优平台 + 手册已过线 → 不冻结 ----------
        _state([0.79, 0.81, 0.82, 0.82, 0.82], manual_passed=True)
        comp._check_done("p1", threshold)
        st2 = comp._get_proposal_state("p1")
        self.assert_true(not st2.get("scheduler_frozen"),
                         "手册已过线的平台课题不冻结（晋级路径仍通）")

        # ---------- 3. 质量收敛（≥0.85 平台）+ 手册门未过线 → 冻结 ----------
        _state([0.83, 0.86, 0.86, 0.86, 0.86], manual_passed=False)
        comp._check_done("p1", threshold)
        st3 = comp._get_proposal_state("p1")
        self.assert_eq(st3.get("scheduler_frozen"), True,
                       "收敛平台 + 手册门未过线同样冻结")
        self.assert_in("转人工", st3.get("scheduler_frozen_reason") or "",
                       "收敛冻结原因应标注转人工")

        # ---------- 4/5. 等人队列：parked 项产出与写冲突冻结隔离 ----------
        from human_queue import collect_human_queue
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        proposals = {
            "p-parked": {
                "status": "optimizing",
                "title": "平台课题",
                "scheduler_frozen": True,
                "scheduler_frozen_reason": "平台转人工：高位平台且方法手册门未过线，轮转暂停",
                "last_score": 0.82,
                "updated_at": (now - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            "p-conflict": {
                # executor 写冲突冻结（reason 无"转人工"）→ 不进队列
                "status": "optimizing",
                "title": "写冲突冻结课题",
                "scheduler_frozen": True,
                "scheduler_frozen_reason": "写冲突自动冻结：state 竞争",
                "last_score": 0.80,
                "updated_at": (now - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }
        q = collect_human_queue(proposals=proposals, now=now)
        all_items = q.get("items") or []
        parked = [i for i in all_items
                  if i.get("type") == "parked" and i.get("proposal_id") == "p-parked"]
        conflict = [i for i in all_items
                    if i.get("type") == "parked" and i.get("proposal_id") == "p-conflict"]
        self.assert_eq(len(parked), 1, "parked 课题进等人队列（type=parked）")
        self.assert_eq(len(conflict), 0, "写冲突冻结不进 parked 队列（走链路自愈）")
        if parked:
            self.assert_in("采纳", parked[0].get("suggested_action") or "",
                           "parked 建议动作含采纳/解冻")


if __name__ == "__main__":
    suite = ParkManualGateTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    failed = [r for r in suite.results if not r.passed]
    print(f"完成：通过 {len(suite.results) - len(failed)}，失败 {len(failed)}")
    for r in failed:
        print(f"  ✗ {r.name}: {r.msg}")
    sys.exit(1 if failed else 0)
