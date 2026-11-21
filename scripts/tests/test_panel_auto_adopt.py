#!/usr/bin/env python3
"""v7.2.0 评审团自动晋级 + 7 天否决窗口测试。

覆盖：
1. check_auto_adopt_windows：窗口期满自动归档 / 窗口内跳过 / vetoed 跳过 /
   reject_lean 期满转人工 / 无窗口标记（常规晋级）不动
2. veto_auto_adopt：否决标记 + 通道守卫
3. _check_new_panel_requests：新请求 2h 内提醒 / 超时不提醒
4. run_panel 通过分支自动晋级语义（源码锚点 + 纯逻辑）

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_panel_auto_adopt.py
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class PanelAutoAdoptTests(TestSuite):
    def __init__(self):
        super().__init__("v7.2.0 评审团自动晋级 + 否决窗口测试")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        import importlib
        for m in ("panel_review", "paths"):
            sys.modules.pop(m, None)
        import paths  # noqa: F401
        import panel_review

        now = datetime.now(timezone.utc)

        # ============================================================
        # 1. check_auto_adopt_windows 决策逻辑（fake lifecycle）
        # ============================================================
        class _FakeLC:
            def __init__(self, proposals):
                self._store = dict(proposals)
                self.archived = []
            def list_by_status(self, status):
                return [
                    {"proposal_id": pid} for pid, p in self._store.items()
                    if p.get("status") == status
                ]
            def _get_proposal_state(self, pid):
                return self._store.get(pid)
            def _set_proposal_state(self, pid, st):
                self._store[pid] = st
            def archive_proposal(self, pid, comment, verdict):
                self.archived.append((pid, verdict))
                self._store[pid]["status"] = "archived"
                return {"success": True}

        def _mk(status="pending_review", started_days_ago=None, vetoed=False,
                score_history=None, issues=None):
            ps = {"status": status, "optimization_rounds": 3,
                  "last_score": 0.78, "score_history": score_history or [],
                  "open_critical_issues": issues or []}
            if started_days_ago is not None:
                ps["panel_auto_adopt_at"] = _iso(now - timedelta(days=started_days_ago))
                ps["panel_auto_adopt_window_days"] = 7
            if vetoed:
                ps["panel_adopt_vetoed"] = True
            return ps

        # 1a. 窗口期满（8 天前开启）+ 预审非 reject → 自动归档
        lc = _FakeLC({"p-expired": _mk(started_days_ago=8)})
        r = panel_review.check_auto_adopt_windows(lc)
        self.assert_true(r.get("success"), "扫描应成功")
        self.assert_eq(r.get("archived"), ["p-expired"], "期满课题应自动归档")
        self.assert_eq(lc.archived[0][1], "panel_auto_adopt", "归档 verdict 标记")

        # 1b. 窗口内（2 天前开启）→ 跳过
        lc2 = _FakeLC({"p-inwin": _mk(started_days_ago=2)})
        r2 = panel_review.check_auto_adopt_windows(lc2)
        self.assert_eq(r2.get("archived"), [], "窗口内不归档")
        self.assert_eq(r2.get("skipped")[0].get("reason"), "in_window", "跳过原因")
        self.assert_true(r2.get("skipped")[0].get("remaining_days", 0) > 4,
                         "剩余天数应约 5")

        # 1c. 已否决 → 跳过
        lc3 = _FakeLC({"p-veto": _mk(started_days_ago=9, vetoed=True)})
        r3 = panel_review.check_auto_adopt_windows(lc3)
        self.assert_eq(r3.get("archived"), [], "否决课题不归档")
        self.assert_eq(r3.get("skipped")[0].get("reason"), "vetoed", "跳过原因为 vetoed")

        # 1d. 无窗口标记（常规晋级通道）→ 不动
        lc4 = _FakeLC({"p-normal": _mk()})
        r4 = panel_review.check_auto_adopt_windows(lc4)
        self.assert_eq(r4.get("archived"), [], "常规晋级课题不自动归档")

        # 1e. 期满但存在未解决高危 → 转人工
        bad_issues = [{"severity": "high", "description": "判据矛盾",
                       "round_resolved": None, "stale": False}]
        lc5 = _FakeLC({"p-reject": _mk(started_days_ago=9, issues=bad_issues)})
        r5 = panel_review.check_auto_adopt_windows(lc5)
        self.assert_eq(r5.get("archived"), [], "存在高危课题期满不归档")
        self.assert_eq(r5.get("skipped")[0].get("reason"), "unresolved_critical_at_expiry",
                       "期满高危转人工")
        self.assert_true("panel_auto_adopt_at" not in lc5._store["p-reject"],
                         "窗口标记应撤销回人工通道")

        # 1e2. 空 score_history（人工退回重置过）但无高危 → 仍可归档
        # （compute_pre_review 的"模块数<=2"依赖 history 完整性，评审团
        # 通道守卫不应被 history 重置误挡）
        lc5b = _FakeLC({"p-nohist": _mk(started_days_ago=9, score_history=[])})
        r5b = panel_review.check_auto_adopt_windows(lc5b)
        self.assert_eq(r5b.get("archived"), ["p-nohist"],
                       "空 history 无高危课题应可归档")

        # 1f. 配置关闭 → 整体跳过
        orig_cfg = panel_review._panel_auto_adopt_config
        panel_review._panel_auto_adopt_config = lambda: {"enabled": False, "window_days": 7}
        try:
            lc6 = _FakeLC({"p-off": _mk(started_days_ago=9)})
            r6 = panel_review.check_auto_adopt_windows(lc6)
            self.assert_eq(r6.get("skipped"), "disabled", "配置关闭整体跳过")
        finally:
            panel_review._panel_auto_adopt_config = orig_cfg

        # ============================================================
        # 2. veto_auto_adopt 守卫（fake lc 复用 CronMixin 真实接口）
        # ============================================================
        from proposal_lifecycle.cron import CronMixin

        class _FakeLC2(CronMixin):
            _store = {}
            def _get_proposal_state(self, pid):
                return dict(self._store.get(pid) or {})
            def _set_proposal_state(self, pid, st):
                self._store[pid] = st

        flc = _FakeLC2()
        flc._store["p-v"] = {
            "status": "pending_review",
            "panel_auto_adopt_at": _iso(now - timedelta(days=1)),
        }
        import proposal_lifecycle as pl_mod
        _orig_cls = pl_mod.ProposalLifecycle
        pl_mod.ProposalLifecycle = lambda: flc
        try:
            rv = panel_review.veto_auto_adopt("p-v", reason="方案第 3 节不可操作")
        finally:
            pl_mod.ProposalLifecycle = _orig_cls
        self.assert_true(rv.get("success"), "窗口内否决应成功")
        self.assert_true(flc._store["p-v"].get("panel_adopt_vetoed"), "否决标志置位")

        # 通道守卫：非评审团通道（无窗口）不能否决
        flc._store["p-nochan"] = {"status": "pending_review"}
        pl_mod.ProposalLifecycle = lambda: flc
        try:
            rv2 = panel_review.veto_auto_adopt("p-nochan")
        finally:
            pl_mod.ProposalLifecycle = _orig_cls
        self.assert_true(not rv2.get("success"), "无窗口通道应拒绝否决")
        # 守卫：非 pending_review 状态
        flc._store["p-opt"] = {"status": "optimizing", "panel_auto_adopt_at": _iso(now)}
        pl_mod.ProposalLifecycle = lambda: flc
        try:
            rv3 = panel_review.veto_auto_adopt("p-opt")
        finally:
            pl_mod.ProposalLifecycle = _orig_cls
        self.assert_true(not rv3.get("success"), "optimizing 状态应拒绝否决")

        # ============================================================
        # 3. _check_new_panel_requests（fake ProposalLifecycle）
        # ============================================================
        sys.modules.pop("lifecycle_monitor", None)
        import lifecycle_monitor as lm
        import proposal_lifecycle as pl_mod

        class _FakePL:
            def __init__(self, store):
                self._store = store
            def list_by_status(self, status):
                return [{"proposal_id": pid} for pid, p in self._store.items()
                        if p.get("status") == status]
            def _get_proposal_state(self, pid):
                return self._store.get(pid)

        _store_fix = {
            "p-new": {  # 1h 前请求 → 提醒
                "status": "optimizing", "panel_review_requested": True,
                "panel_requested_at": _iso(now - timedelta(hours=1)),
                "panel_review_reason": "v7.1.8 r3 触发评审团",
                "optimization_rounds": 3, "last_score": 0.78,
            },
            "p-old": {  # 5h 前请求 → 不提醒（交给 72h escalate）
                "status": "optimizing", "panel_review_requested": True,
                "panel_requested_at": _iso(now - timedelta(hours=5)),
                "panel_review_reason": "x", "optimization_rounds": 6,
            },
            "p-none": {  # 无请求
                "status": "optimizing", "panel_review_requested": False,
            },
        }
        _orig_pl_cls = pl_mod.ProposalLifecycle
        pl_mod.ProposalLifecycle = lambda: _FakePL(_store_fix)
        try:
            alerts = lm._check_new_panel_requests()
            self.assert_eq(len(alerts), 1, "仅新请求产生告警")
            self.assert_eq(alerts[0]["type"], "panel_request_new", "告警类型")
            self.assert_eq(alerts[0]["proposal_id"], "p-new", "课题 ID")
            self.assert_true("r3" in alerts[0]["message"], "消息含轮次")
        finally:
            pl_mod.ProposalLifecycle = _orig_pl_cls

        # ============================================================
        # 4. 源码锚点：run_panel 通过分支 + 编排挂载 + monitor 可执行性
        # ============================================================
        src = (_SCRIPTS_DIR / "panel_review.py").read_text(encoding="utf-8")
        self.assert_true("panel_auto_adopt_at" in src, "run_panel 应写窗口起点")
        self.assert_true("check_auto_adopt_windows" in src, "窗口扫描函数存在")
        self.assert_true("veto_auto_adopt" in src, "否决接口存在")
        self.assert_true("--auto-adopt-scan" in src, "CLI 扫描入口存在")
        self.assert_true("--veto" in src, "CLI 否决入口存在")
        self.assert_true("skipped_unresolved_critical" in src, "晋级前高危守卫存在")

        orch = (_SCRIPTS_DIR / "lifecycle" / "orchestrator.py").read_text(encoding="utf-8")
        self.assert_true("check_auto_adopt_windows" in orch,
                         "每日编排应挂载窗口扫描")

        mon = (_SCRIPTS_DIR / "lifecycle_monitor.py").read_text(encoding="utf-8")
        self.assert_true("_check_new_panel_requests" in mon,
                         "monitor 应含新评审团请求检查")
        self.assert_true('"panel_request_new"' in mon, "告警类型锚点")

        msrc = (_SCRIPTS_DIR / "adversarial" / "monitor.py").read_text(encoding="utf-8")
        self.assert_true("executability_score" in msrc,
                         "monitor prompt 应含可执行性评估")
        ssrc = (_SCRIPTS_DIR / "adversarial" / "scoring.py").read_text(encoding="utf-8")
        self.assert_true("executability_score" in ssrc,
                         "monitor_history 应落库可执行性分")
        esrc = (_SCRIPTS_DIR / "lifecycle" / "executor.py").read_text(encoding="utf-8")
        self.assert_true("last_executability_score" in esrc,
                         "prop_state 顶层应有可执行性快照")


def main() -> None:
    suite = PanelAutoAdoptTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"\n{'✓' if len(suite.results) - ok == 0 else '✗'} {suite.name}: {ok}/{len(suite.results)} 通过")
    for r in suite.results:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
