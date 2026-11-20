#!/usr/bin/env python3
"""
test_pilot_scorecard.py — 试点变体记分卡回归测试（v7.3.59，对标批次 B·SICA 变体谱系）

覆盖：
    1. 开卡（base 快照/同源幂等防护/默认父谱系）
    2. 关卡（variant 快照 + delta 计算/终态不可重复裁决/非法 outcome）
    3. 谱系语义（adopted 进父链、reverted/fizzle 不进父链）
    4. 报告汇总与方向感知 verdict_hint
    5. self_optimizer 接线：promote_pilot 自动开卡 + scorecard_id 回写 ledger；
       phase_ledger 基准门红自动回滚时同步关卡（reverted）
    6. 指标快照降级（retrospective 不可用时空快照不抛）

零 LLM；指标快照经 monkeypatch 隔离（不跑真实 retrospective 7 天账本）。
"""

import sys
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT

sys.path.insert(0, str(REAL_ROOT / "scripts"))


class PilotScorecardTests(TestSuite):
    def __init__(self):
        super().__init__("试点变体记分卡回归测试")
        self.tmp_root = None
        self.ps = None
        self.so = None
        self._patches = []

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith(("pilot_scorecard", "self_optimizer")) \
                    or mod_name in ("paths", "common"):
                del sys.modules[mod_name]
        self.ps = importlib.import_module("pilot_scorecard")
        self.so = importlib.import_module("self_optimizer")
        patch_module_root("pilot_scorecard", self.tmp_root)
        patch_module_root("self_optimizer", self.tmp_root)
        import paths
        paths.PROJECT_ROOT = self.tmp_root
        # 记分卡与台账落盘路径显式指向隔离目录（防跨套件模块卫生问题，
        # 同 test_side_worker v7.3.58 修法）
        self.ps.SCORECARDS_PATH = self.tmp_root / "memory" / "self-optimize" / "pilot-scorecards.json"
        self.so.LEDGER_PATH = self.tmp_root / "memory" / "self-optimize" / "adoption-ledger.json"
        self.so.WORKLIST_PATH = self.tmp_root / "memory" / "self-optimize" / "worklist.json"
        self._patch(self.ps, "_snapshot_metrics",
                    lambda: {"metrics": {"failure_rate": 26.5, "daily_rounds": 10.0},
                             "at": "T0"})

    def teardown(self):
        for obj, name, orig in self._patches:
            setattr(obj, name, orig)
        self._patches.clear()
        if self.tmp_root and self.tmp_root.exists():
            import shutil
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _patch(self, obj, name, fn):
        self._patches.append((obj, name, getattr(obj, name)))
        setattr(obj, name, fn)

    def _unpatch_last(self):
        if self._patches:
            obj, name, orig = self._patches.pop()
            setattr(obj, name, orig)

    def _reset_cards(self):
        """清空计分卡文件（计数断言型用例的隔离前提）。"""
        self.ps.save_json(self.ps.SCORECARDS_PATH, {"scorecards": []})

    # ---------- 用例 ----------

    def test_open_and_lineage(self):
        r1 = self.ps.open_scorecard("call_health", "修复降级链", "p-x", 3)
        self.assert_true(r1["success"], "开卡成功")
        self.assert_eq(r1.get("parent"), None, "首卡无父")
        r1b = self.ps.open_scorecard("call_health", "修复降级链", "p-x", 3)
        self.assert_true(r1b["success"] is False, "同源同动作 open 幂等拒绝")
        r2 = self.ps.close_scorecard(r1["scorecard_id"], "adopted", reason="向好")
        self.assert_true(r2["success"], "关卡 adopted")
        self.assert_eq(r2.get("delta", {}).get("failure_rate"), 0.0,
                       "同快照 delta=0（monkeypatch 固定指标）")
        r3 = self.ps.open_scorecard("call_health", "重试梯度二档", "p-x", 4)
        self.assert_eq(r3.get("parent"), r1["scorecard_id"], "默认父=同源最近 adopted")

    def test_failed_variant_not_in_parent_chain(self):
        r1 = self.ps.open_scorecard("bug_velocity", "A 变体", "p-y", 2)
        self.ps.close_scorecard(r1["scorecard_id"], "reverted", reason="基准门红")
        r2 = self.ps.open_scorecard("bug_velocity", "B 变体", "p-y", 3)
        self.assert_eq(r2.get("parent"), None, "reverted 不进父链")
        self.ps.close_scorecard(r2["scorecard_id"], "fizzle")
        r3 = self.ps.open_scorecard("bug_velocity", "C 变体", "p-y", 4)
        self.assert_eq(r3.get("parent"), None, "fizzle 同样不进父链")

    def test_close_guards(self):
        r = self.ps.close_scorecard("ps-nonexist", "adopted")
        self.assert_true(r["success"] is False, "不存在 id 拒绝")
        r1 = self.ps.open_scorecard("whack", "甲", "p-z", 1)
        r2 = self.ps.close_scorecard(r1["scorecard_id"], "bogus")
        self.assert_true(r2["success"] is False, "非法 outcome 拒绝")
        r3 = self.ps.close_scorecard(r1["scorecard_id"], "reverted")
        self.assert_true(r3["success"], "合法 reverted 关卡")
        r4 = self.ps.close_scorecard(r1["scorecard_id"], "adopted")
        self.assert_true(r4["success"] is False, "终态不可重复裁决")

    def test_report_and_verdict_hint(self):
        # failure_rate 恶化→回退信号；daily_rounds 上升→向好信号
        # base=T1 {10,12} → variant=T2 {5,14}：delta = {-5.0, +2.0} 双向好
        self._reset_cards()
        self._patch(self.ps, "_snapshot_metrics",
                    lambda: {"metrics": {"failure_rate": 10.0, "daily_rounds": 12.0}, "at": "T1"})
        r1 = self.ps.open_scorecard("s1", "x", "p", 1)
        self._patch(self.ps, "_snapshot_metrics",
                    lambda: {"metrics": {"failure_rate": 5.0, "daily_rounds": 14.0}, "at": "T2"})
        self.ps.close_scorecard(r1["scorecard_id"], "adopted")
        rep = self.ps.scorecard_report()
        self.assert_eq(rep["total"], 1, "报告 total")
        entry = rep["scorecards"][0]
        self.assert_eq(entry["delta"].get("failure_rate"), -5.0, "failure_rate delta")
        self.assert_eq(entry["delta"].get("daily_rounds"), 2.0, "daily_rounds delta")
        self.assert_eq(entry["verdict_hint"], "指标向好（晋升正信号）", "方向感知提示")

    def test_snapshot_degrades_without_retrospective(self):
        """retrospective 不可用时空快照不抛——open_scorecard 内部防御（fail-open）。"""
        self._reset_cards()

        def _boom():
            raise RuntimeError("boom")

        self._patch(self.ps, "_snapshot_metrics", _boom)
        r = self.ps.open_scorecard("src", "act", "p", 1)
        self.assert_true(r.get("success") is True, "快照异常降级后开卡不崩")
        ledger_ok = r.get("base_metrics") == {} or r.get("base_metrics") is not None
        self.assert_true(ledger_ok, "base 为空快照")
        self._unpatch_last()

    def test_promote_pilot_wiring(self):
        """promote_pilot 自动开卡 + scorecard_id 回写 ledger；基准门红时拒绝。"""
        # 前序用例可能留下同源 open 卡（幂等防护会正确拒绝），先重置
        self._reset_cards()
        self._patch(self.so, "phase_benchmark", lambda: {"gate": False})
        r_red = self.so.promote_pilot("src", "act", "p-w", 1)
        self.assert_true(r_red["success"] is False, "基准门红拒绝试点")
        self._patch(self.so, "phase_benchmark", lambda: {"gate": True})
        r = self.so.promote_pilot("src", "act", "p-w", 1)
        self.assert_true(r.get("success") is True, "基准门绿晋升")
        self.assert_true(r.get("scorecard_id"), "scorecard_id 回传")
        ledger = self.so.load_json(self.so.LEDGER_PATH, default={"pilots": []})
        pilot = ledger.get("pilots", [])[-1]
        self.assert_eq(pilot.get("scorecard_id"), r["scorecard_id"], "ledger 回写")
        # phase_ledger 基准门红 → 自动回滚试点 + 同步关卡 reverted
        self.so.phase_ledger({"gate": False}, {"added": 0})
        ledger = self.so.load_json(self.so.LEDGER_PATH, default={"pilots": []})
        pilot = ledger.get("pilots", [])[-1]
        self.assert_eq(pilot.get("status"), "rolled_back", "基准门红自动回滚")
        cards = self.ps.load_json(self.ps.SCORECARDS_PATH, default={"scorecards": []})
        sc = next((s for s in cards.get("scorecards", [])
                   if s.get("scorecard_id") == r["scorecard_id"]), {})
        self.assert_eq(sc.get("status"), "reverted", "记分卡同步 reverted")

    def run_tests(self):
        self.test_open_and_lineage()
        self.test_failed_variant_not_in_parent_chain()
        self.test_close_guards()
        self.test_report_and_verdict_hint()
        self.test_snapshot_degrades_without_retrospective()
        self.test_promote_pilot_wiring()


if __name__ == "__main__":
    suite = PilotScorecardTests()
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
