#!/usr/bin/env python3
"""告警防线可触发性测试（v6.8.54）。

背景（2026-08-14 架构评审）："防线自己失效时无人报警"是系统性盲区——
输入端熔断曾静默失效 13 天。本套件验证每类告警在合成快照/数据下
**确实会触发**，防止"告警代码存在但永不执行"的回归。

覆盖：
  1. health_sensor KB 四类告警（索引停更/生长断流/蒸馏积压/图谱失连）
     ——v6.8.50 引入但正向触发从未被回归覆盖（此前仅 --self-check）。
  2. cron_manifest.validate_cron_topology 三类问题检出（缺失/重复/漂移）。
  3. 双上限终态自动解锁策略（should_auto_unlock 六种场景）。
  4. error_history 裁剪（trim_error_history）。

运行：python3 scripts/self_test.py --module（自动纳入）
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from test_runner import TestSuite


class KbAlertCircuitTests(TestSuite):
    """KB 四类告警在合成快照下必须触发。"""

    def __init__(self):
        super().__init__("KB 告警防线可触发性")

    def setup(self):
        pass

    def teardown(self):
        pass

    def _snap(self, **kb_overrides):
        kb = {
            # 字段名与 health_sensor._collect_kb_signals 输出契约一致
            # （预计算数值而非时间戳）
            "index_age_h": 1.0,
            "growth_stall_days": 0.2,
            "pending_distill": 100,
            "graph_connectivity": 0.60,
        }
        kb.update(kb_overrides)
        # health_sensor 快照结构：kb 位于 collect_health_snapshot 返回 dict 顶层
        return {"global": {"idle_done_jobs_2h": 0, "api_error_jobs_2h": 0,
                           "score_drops": 0, "monitored_proposals": 2},
                "kb": kb}

    def _types(self, **kb_overrides):
        from health_sensor import evaluate_risks
        return {r.get("type") for r in evaluate_risks(self._snap(**kb_overrides))}

    def run_tests(self):
        # ── 用例 1-4：四类 KB 告警正向触发 ──
        t = self._types(index_age_h=72.0)
        self.assert_in("kb_index_stale", t, "索引停更 72h 应触发（阈值 48h）")

        t = self._types(growth_stall_days=8.0)
        self.assert_in("kb_growth_stall", t, "生长断流 8 天应触发（阈值 7 天）")

        t = self._types(pending_distill=800)
        self.assert_in("kb_distill_backlog", t, "蒸馏积压 800 应触发")

        t = self._types(graph_connectivity=0.30)
        self.assert_in("kb_graph_disconnect", t, "连通性 0.30 应触发")

        # ── 用例 5：健康 KB 零告警（防误报回归基线） ──
        from health_sensor import evaluate_risks
        kb_alerts = [r for r in evaluate_risks(self._snap())
                     if str(r.get("type", "")).startswith("kb_")]
        self.assert_eq(len(kb_alerts), 0, "健康 KB 不应触发任何 kb_* 告警")


class CronTopologyTests(TestSuite):
    """validate_cron_topology 三类问题检出 + 清单完备性。"""

    def __init__(self):
        super().__init__("cron 拓扑对账")

    def setup(self):
        pass

    def teardown(self):
        pass

    def _ok_crons(self):
        from lifecycle.cron_manifest import CRON_MANIFEST
        base = [{"name": n, "schedule": (s.get("schedule") or "0 9 * * 1")}
                for n, s in CRON_MANIFEST.items()]
        base.append({"name": "lc-weekend-input", "schedule": "0 9 * * 6"})
        return base

    def run_tests(self):
        from lifecycle.cron_manifest import CRON_MANIFEST, validate_cron_topology

        # ── 用例 1：完全一致拓扑零问题 ──
        self.assert_eq(validate_cron_topology(self._ok_crons()), [],
                       "一致的拓扑不应产生问题")

        # ── 用例 2：缺失检出 ──
        crons = [c for c in self._ok_crons() if c["name"] != "lc-repair"]
        kinds = {i["kind"] for i in validate_cron_topology(crons)}
        self.assert_in("missing", kinds, "缺失应被检出")

        # ── 用例 3：重复检出 ──
        dup = self._ok_crons() + [{"name": "lc-kb-sync", "schedule": "x"}]
        kinds = {i["kind"] for i in validate_cron_topology(dup)}
        self.assert_in("duplicate", kinds, "重复应被检出")

        # ── 用例 4：调度漂移检出（v6.8.54 新增能力） ──
        drift = [dict(c) for c in self._ok_crons()]
        for c in drift:
            if c["name"] == "lc-daily-orchestrate":
                c["schedule"] = "0 3 * * 1"
        drifts = [i for i in validate_cron_topology(drift) if i["kind"] == "drift"]
        self.assert_eq(len(drifts) > 0, True, "调度漂移应被检出")

        # ── 用例 5：清单必须覆盖全部固定 cron（防新增遗漏） ──
        expected = {
            "lc-daily-orchestrate", "lc-repair",
            "lc-retrospective", "lc-kb-sync", "lc-hourly-monitor",
            "lc-micro-scheduler",
        }  # v6.9.68: lc-prompt-optimize 暂停移出清单（恢复时加回）
        missing = expected - set(CRON_MANIFEST)
        self.assert_eq(missing, set(), f"清单缺少固定 cron: {missing}")


class AutoUnlockPolicyTests(TestSuite):
    """双上限终态自动解锁策略（v6.8.54，替代人工解锁）。"""

    def __init__(self):
        super().__init__("双上限自动解锁策略")

    def setup(self):
        pass

    def teardown(self):
        pass

    def _terminal_job(self, hours_ago=25, **extra):
        fin = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        job = {"status": "failed", "attempts": 3, "repair_attempts": 3,
               "finished_at": fin}
        job.update(extra)
        return job

    def run_tests(self):
        from lifecycle.utils import should_auto_unlock
        now = datetime.now(timezone.utc)

        # ── 用例 1：双上限 + 冷却期满 → 解锁 ──
        self.assert_eq(should_auto_unlock(self._terminal_job(25), now), True,
                       "双上限且失败超 24h 应解锁")
        # ── 用例 2：冷却期内 → 不解锁（给根因修复留时间） ──
        self.assert_eq(should_auto_unlock(self._terminal_job(2), now), False,
                       "失败仅 2h 不应解锁")
        # ── 用例 3：终生一次上限 → 防无限重试循环 ──
        self.assert_eq(should_auto_unlock(self._terminal_job(25, auto_unlock_count=1), now),
                       False, "已自动解锁过一次不应再解锁")
        # ── 用例 4/5：repair 未达上限不解锁；attempts 不再作为门槛（v6.9.49） ──
        self.assert_eq(should_auto_unlock(self._terminal_job(25, repair_attempts=1), now),
                       False, "repair 未达上限不应解锁")
        # v6.9.49 死角修复：repair 重置(attempts=0, rep_att=3)后单次失败
        # → attempts=1/rep_att=3。原断言期望 False 会造成三路恢复皆死的
        # 永久死锁（08-24 order-param r7-references-critic 实证），现应解锁。
        self.assert_eq(should_auto_unlock(self._terminal_job(25, attempts=1), now),
                       True, "repair 已放弃(attempts<MAX)且失败超24h 应解锁（v6.9.49 死角）")
        # ── 用例 5b：死角态的冷却与终生一次约束同样生效 ──
        self.assert_eq(should_auto_unlock(self._terminal_job(2, attempts=1), now),
                       False, "死角态失败仅 2h 不应解锁")
        self.assert_eq(should_auto_unlock(
            self._terminal_job(25, attempts=1, auto_unlock_count=1), now),
            False, "死角态已解锁过一次不应再解锁")
        # ── 用例 6：非 failed 状态 ──
        self.assert_eq(should_auto_unlock(self._terminal_job(25, status="pending"), now),
                       False, "pending 状态不应解锁")
        # ── 用例 7：畸形输入安全 ──
        self.assert_eq(should_auto_unlock({}, now), False, "空 job 应安全返回 False")
        self.assert_eq(should_auto_unlock(
            {"status": "failed", "attempts": 3, "repair_attempts": 3,
             "finished_at": "not-a-date"}, now), False, "坏时间戳应安全返回 False")


class ErrorHistoryTrimTests(TestSuite):
    """error_history 裁剪（v6.8.54，控 _lifecycle.json 膨胀）。"""

    def __init__(self):
        super().__init__("error_history 裁剪")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from lifecycle.utils import ERROR_HISTORY_CAP, trim_error_history

        job = {"error_history": [{"i": i} for i in range(40)]}
        trim_error_history(job)
        self.assert_eq(len(job["error_history"]), ERROR_HISTORY_CAP,
                       "40 条应裁剪到上限")
        self.assert_eq(job["error_history"][0]["i"], 40 - ERROR_HISTORY_CAP,
                       "应保留最近 N 条")

        small = {"error_history": [{"i": 1}, {"i": 2}]}
        trim_error_history(small)
        self.assert_eq(len(small["error_history"]), 2, "低于上限不应裁剪")

        trim_error_history({})  # 不应抛异常
        trim_error_history({"error_history": None})  # 不应抛异常


if __name__ == "__main__":
    total_fail = 0
    for cls in (KbAlertCircuitTests, CronTopologyTests, AutoUnlockPolicyTests,
                ErrorHistoryTrimTests):
        suite = cls()
        suite.setup()
        suite.run_tests()
        suite.teardown()
        ok = sum(1 for r in suite.results if r.passed)
        total_fail += len(suite.results) - ok
        print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if total_fail else 0)
