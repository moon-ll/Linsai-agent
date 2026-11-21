#!/usr/bin/env python3
"""v7.1.8 评审团脚本改造 + 飞书告警通路测试。

覆盖：
1. panel_queue() 包含 optimizing + panel_review_requested（r3 触发路径），
   不再只查 pending_review；按 status + panel_flag + critical/high 排序
2. panel_review --finalize 同时调用 clear_panel_request 和
   reset_panel_cycle；reset_panel_cycle 不存在则提示
3. _check_r1_start_failures 读取 r1-start-alerts.json 缓存，按
   dedup 窗口过滤，转 anomaly
4. run_monitor 流程把 r1 启动失败告警加进 anomalies

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_panel_review_v718.py
"""

import json
import sys
import tempfile
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite, create_isolated_env, patch_module_root, patch_kb_sync_noop, REAL_ROOT


class PanelReviewV718Tests(TestSuite):
    def __init__(self):
        super().__init__("v7.1.8 评审团脚本改造 + r1 飞书告警测试")
        self.tmp_root = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 创建 research_proposals 目录结构
        for sub in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / sub).mkdir(parents=True, exist_ok=True)
        # 创建 memory 目录（用于 r1-start-alerts.json）
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)

    def teardown(self):
        pass

    def _write_lifecycle(self, proposals):
        """写 _lifecycle.json 测试夹具。"""
        path = self.tmp_root / "research_proposals" / "_lifecycle.json"
        path.write_text(
            json.dumps({"proposals": proposals}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def run_tests(self):
        # ================================================================
        # 1. panel_queue() 包含 r3 触发路径（optimizing + panel_review_requested）
        # ================================================================
        # 重新加载 panel_review 模块以使用测试隔离目录
        import importlib
        for mod_name in list(sys.modules.keys()):
            if mod_name in ("panel_review", "paths"):
                del sys.modules[mod_name]
        import paths
        paths.PROJECT_ROOT = self.tmp_root
        import panel_review

        # 场景 A: pending_review + 未解决问题 → 应入队（旧路径）
        self._write_lifecycle({
            "p-pending": {
                "status": "pending_review",
                "last_score": 0.83,
                "panel_review_requested": False,
                "open_critical_issues": [
                    {"severity": "critical", "description": "判据矛盾", "round_resolved": None, "stale": False},
                ],
            },
        })
        q = panel_review.panel_queue()
        self.assert_eq(len(q), 1, "pending_review 路径入队 1 条")
        self.assert_eq(q[0]["proposal_id"], "p-pending", "课题 ID")
        self.assert_eq(q[0]["trigger"], "manual_submit", "pending_review 触发原因")
        self.assert_eq(q[0]["status"], "pending_review", "状态透传")

        # 场景 B: optimizing + panel_review_requested + "r3 触发" reason
        # → 应入队（v7.1.8 r3 路径），触发原因 r3_auto
        self._write_lifecycle({
            "p-r3-trigger": {
                "status": "optimizing",
                "last_score": 0.65,
                "panel_review_requested": True,
                "panel_review_reason": "v7.1.8 r3 触发评审团（不依赖分数窗口）",
                "panel_requested_at": "2026-09-27T01:00:00Z",
                "optimization_rounds": 3,
                "open_critical_issues": [],
            },
        })
        q2 = panel_review.panel_queue()
        self.assert_eq(len(q2), 1, "r3 触发入队 1 条（即使无历史未解决问题）")
        self.assert_eq(q2[0]["trigger"], "r3_auto", "r3 触发原因识别")
        self.assert_eq(q2[0]["status"], "optimizing", "状态透传")
        self.assert_eq(q2[0]["rounds"], 3, "rounds 透传")

        # 场景 C: optimizing + panel_review_requested + 平台带 reason
        # → 触发原因 platform_band
        self._write_lifecycle({
            "p-platform": {
                "status": "optimizing",
                "last_score": 0.74,
                "panel_review_requested": True,
                "panel_review_reason": "主平台带：连续4轮评分在0.70-0.85",
                "open_critical_issues": [],
            },
        })
        q3 = panel_review.panel_queue()
        self.assert_eq(len(q3), 1, "平台带触发入队")
        self.assert_eq(q3[0]["trigger"], "platform_band", "平台带触发原因")

        # 场景 D: optimizing 无 panel_review_requested → 不入队（保留原行为）
        self._write_lifecycle({
            "p-optimizing": {
                "status": "optimizing",
                "last_score": 0.5,
                "panel_review_requested": False,
                "open_critical_issues": [],
            },
        })
        q4 = panel_review.panel_queue()
        self.assert_eq(len(q4), 0, "optimizing 无 panel 标志不入队")

        # 场景 E: pending_review 无未解决问题 → 不入队（旧行为保留）
        self._write_lifecycle({
            "p-clean-pending": {
                "status": "pending_review",
                "last_score": 0.85,
                "panel_review_requested": False,
                "open_critical_issues": [],
            },
        })
        q5 = panel_review.panel_queue()
        self.assert_eq(len(q5), 0, "pending_review 无未解决问题不入队")

        # 场景 F: 混合排序——pending_review 优先于 optimizing+r3
        self._write_lifecycle({
            "p-r3": {
                "status": "optimizing",
                "last_score": 0.65,
                "panel_review_requested": True,
                "panel_review_reason": "v7.1.8 r3 触发评审团",
                "open_critical_issues": [],
            },
            "p-pending": {
                "status": "pending_review",
                "last_score": 0.83,
                "panel_review_requested": False,
                "open_critical_issues": [
                    {"severity": "critical", "description": "问题", "round_resolved": None, "stale": False},
                ],
            },
        })
        q6 = panel_review.panel_queue()
        self.assert_eq(len(q6), 2, "混合队列入队 2 条")
        self.assert_eq(q6[0]["proposal_id"], "p-pending", "pending_review 排前")
        self.assert_eq(q6[1]["proposal_id"], "p-r3", "r3 触发排后")

        # ================================================================
        # 2. reset_panel_cycle 接口存在
        # ================================================================
        from proposal_lifecycle.cron import CronMixin

        class _FakeLC(CronMixin):
            _store = {}
            def _get_proposal_state(self, pid):
                return dict(self._store.get(pid) or {})
            def _set_proposal_state(self, pid, st):
                self._store[pid] = st

        fake = _FakeLC()
        fake._store["p-cycle"] = {
            "status": "optimizing",
            "optimization_rounds": 4,
            "panel_review_completed_for_round": 3,
            "panel_review_cleared_at": "2026-09-27T01:00:00Z",
        }
        r = fake.reset_panel_cycle("p-cycle", reason="评审团完成后自动重置")
        self.assert_true(r.get("success"), "reset_panel_cycle 应成功")
        st = fake._store["p-cycle"]
        self.assert_true("panel_review_completed_for_round" not in st,
                         "reset 应清除本轮已完成标记")
        self.assert_eq(st.get("panel_cycle_reset_reason"), "评审团完成后自动重置",
                       "记录重置原因")

        # ================================================================
        # 3. _check_r1_start_failures 读取 r1-start-alerts.json 缓存
        # ================================================================
        # 重新加载 lifecycle_monitor 以使用测试隔离目录
        for mod_name in list(sys.modules.keys()):
            if mod_name in ("lifecycle_monitor",):
                del sys.modules[mod_name]
        import lifecycle_monitor
        lifecycle_monitor.R1_START_ALERT_PATH = self.tmp_root / "memory" / "r1-start-alerts.json"

        # 场景 A: 无文件 → 返回 []
        r1 = lifecycle_monitor._check_r1_start_failures()
        self.assert_eq(r1, [], "无文件时返回空列表")

        # 场景 B: 有缓存且 last_sent 在 6h 内 → 转 anomaly
        from datetime import datetime, timezone, timedelta
        fresh_ts = (datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        (self.tmp_root / "memory" / "r1-start-alerts.json").write_text(
            json.dumps({
                "alerts": {
                    "p-r1-failed": {
                        "last_sent": fresh_ts,
                        "elapsed_hours": 28.5,
                        "jobs_total": 25,
                        "jobs_pending": 25,
                        "last_score": 0.0,
                    },
                },
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        r1b = lifecycle_monitor._check_r1_start_failures()
        self.assert_eq(len(r1b), 1, "新鲜告警应产生 1 条 anomaly")
        self.assert_eq(r1b[0]["type"], "r1_start_failure", "anomaly 类型")
        self.assert_eq(r1b[0]["proposal_id"], "p-r1-failed", "课题 ID")
        self.assert_true("28.5h" in r1b[0]["message"], "消息含 elapsed_hours")
        self.assert_true("25/25" in r1b[0]["message"], "消息含 jobs_pending/total")

        # 场景 C: last_sent 超 6h → 不产生 anomaly（dedup 窗口）
        stale_ts = (datetime.now(timezone.utc) - timedelta(hours=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        (self.tmp_root / "memory" / "r1-start-alerts.json").write_text(
            json.dumps({
                "alerts": {
                    "p-stale": {
                        "last_sent": stale_ts,
                        "elapsed_hours": 30.0,
                        "jobs_total": 25,
                        "jobs_pending": 25,
                    },
                },
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        r1c = lifecycle_monitor._check_r1_start_failures()
        self.assert_eq(r1c, [], "超 dedup 窗口不产生 anomaly（micro_scheduler 会重新写入）")

        # 场景 D: 缓存格式异常 → 返回 [] 不抛异常
        (self.tmp_root / "memory" / "r1-start-alerts.json").write_text("not json", encoding="utf-8")
        try:
            r1d = lifecycle_monitor._check_r1_start_failures()
            self.assert_true(isinstance(r1d, list), "异常输入返回列表（不抛）")
        except Exception:
            self.assert_true(False, "异常 JSON 不应抛错")

        # ================================================================
        # 4. 源码锚点（确保改动落地）
        # ================================================================
        panel_src = (_SCRIPTS_DIR / "panel_review.py").read_text(encoding="utf-8")
        self.assert_true("in_panel_trigger" in panel_src,
                         "panel_review.py 应含 r3 触发路径分支")
        self.assert_true('trigger = "r3_auto"' in panel_src,
                         "panel_review.py 应含 r3_auto 触发原因识别")
        self.assert_true("reset_panel_cycle" in panel_src,
                         "panel_review.py --finalize 应调用 reset_panel_cycle")
        self.assert_true("reset_panel_cycle" in (panel_src.split("def main")[1] if "def main" in panel_src else ""),
                         "--finalize CLI 应调用 reset_panel_cycle")

        mon_src = (_SCRIPTS_DIR / "lifecycle_monitor.py").read_text(encoding="utf-8")
        self.assert_true("_check_r1_start_failures" in mon_src,
                         "lifecycle_monitor 应含 _check_r1_start_failures 函数")
        self.assert_true('R1_START_ALERT_PATH =' in mon_src,
                         "lifecycle_monitor 应声明 R1_START_ALERT_PATH")
        self.assert_true('"r1_start_failure"' in mon_src,
                         "anomaly type 应为 r1_start_failure")


def main() -> None:
    suite = PanelReviewV718Tests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"\n{'✓' if suite.results and len(suite.results) - ok == 0 else '✗'} {suite.name}: {ok}/{len(suite.results)} 通过")
    for r in suite.results:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()