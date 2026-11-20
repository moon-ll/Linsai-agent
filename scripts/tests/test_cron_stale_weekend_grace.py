#!/usr/bin/env python3
"""
test_cron_stale_weekend_grace.py — cron 陈旧检测的星期域感知与首跑宽限回归测试

验证 v6.9.2 两处修复（lifecycle_monitor._check_cron_status）:

1. 星期域不感知误报：lc-micro-scheduler 的 `*/15 * * * 1-5` 周末按设计暂停，
   旧逻辑从周六起持续报 "N小时 未执行" 直至周一（实测 2026-08-15 周六
   04:02 起 "lc-micro-scheduler (4h 未执行)"）。修复后当天不该执行的
   cron 跳过陈旧与从未执行两项检测。

2. 首跑前"从未执行"误报：lc-daily-orchestrate 08-14 20:13 创建、
   08-15 08:55 首跑，旧逻辑（created_at > 600s 即告警）从 23:00 起连续
   10 次误报 "从未执行"。修复后宽限期与陈旧阈值一致（interval*2），
   每日 cron 首跑前 48h 内不告警；超期未跑仍需检出（防真死 cron）。

验证点:
    - _cron_runs_today 星期域解析（*/1-5/列表/0与7周日/垃圾输入保守真）
    - 周末暂停 cron 当天不产生 cron_stale 告警
    - 运行日 cron 陈旧仍正常检出（防过度抑制）
    - 新建每日 cron 首跑前不告警；超宽限期未跑仍告警
"""

import sys
import shutil
import importlib
from datetime import datetime, timezone, timedelta, date

from test_runner import TestSuite, create_isolated_env, patch_module_root


def _iso(dt: datetime) -> str:
    """带时区 ISO 格式，与 hermes jobs.json 的 created_at/last_run_at 一致。"""
    return dt.astimezone(timezone.utc).isoformat()


class CronStaleWeekendGraceTests(TestSuite):
    def __init__(self):
        super().__init__("cron 陈旧检测星期域感知与首跑宽限测试")
        self.tmp_root = None
        self.lm = None
        self.hb = None
        self._orig_list = None

    def setup(self):
        self.tmp_root = create_isolated_env()

        # 强制重新导入，避免模块级常量/日志指向真实工作区
        for mod_name in list(sys.modules.keys()):
            if mod_name == "lifecycle" or mod_name.startswith("lifecycle.") \
                    or mod_name in ["paths", "common", "hermes_bridge",
                                    "lifecycle_monitor"]:
                del sys.modules[mod_name]

        self.hb = importlib.import_module("hermes_bridge")
        self.lm = importlib.import_module("lifecycle_monitor")

        for mod in ("hermes_bridge", "lifecycle_monitor", "paths", "common"):
            patch_module_root(mod, self.tmp_root)
        import paths
        paths.PROJECT_ROOT = self.tmp_root

        self._orig_list = self.hb.cron_list_profile

    def teardown(self):
        if self.hb is not None and self._orig_list is not None:
            self.hb.cron_list_profile = self._orig_list
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ── 工具 ──

    def _base_crons(self) -> list:
        """构造与 cron_manifest 拓扑一致的完整 cron 列表（不触发缺失/重复/漂移）。

        v6.9.98: lc-weekend-input 及锚点/夜间轮已登记进 CRON_MANIFEST
        （schedule 明确参与漂移对账），从清单生成即覆盖；此处不再手动
        重复添加（会造成 duplicate 误报）。
        """
        from lifecycle.cron_manifest import CRON_MANIFEST
        return [
            {"name": n, "schedule": (spec.get("schedule") or "0 9 * * 1")}
            for n, spec in CRON_MANIFEST.items()
        ]

    def _with_patch(self, crons: list):
        """替换 cron_list_profile 返回构造数据并执行 _check_cron_status。"""
        self.hb.cron_list_profile = lambda profile: crons
        return self.lm._check_cron_status()

    def _find(self, crons: list, name: str) -> dict:
        return next(c for c in crons if c["name"] == name)

    # ── 修复 1：_cron_runs_today 星期域解析 ──

    def _test_runs_today_weekday_only(self):
        """`1-5` 周一至周五覆盖、周六日不覆盖。"""
        # 2026-08-15 为周六、2026-08-17 为周一
        self.assert_eq(self.lm._cron_runs_today("*/15 * * * 1-5", date(2026, 8, 17)),
                       True, "周一被 1-5 覆盖")
        self.assert_eq(self.lm._cron_runs_today("*/15 * * * 1-5", date(2026, 8, 15)),
                       False, "周六不被 1-5 覆盖")
        self.assert_eq(self.lm._cron_runs_today("*/15 * * * 1-5", date(2026, 8, 16)),
                       False, "周日不被 1-5 覆盖")

    def _test_runs_today_sunday_zero_and_seven(self):
        """0 与 7 均表示周日。"""
        self.assert_eq(self.lm._cron_runs_today("0 9 * * 0", date(2026, 8, 16)),
                       True, "cron 0 = 周日")
        self.assert_eq(self.lm._cron_runs_today("0 9 * * 7", date(2026, 8, 16)),
                       True, "cron 7 = 周日")
        self.assert_eq(self.lm._cron_runs_today("0 9 * * 0", date(2026, 8, 15)),
                       False, "周六不被 0 覆盖")

    def _test_runs_today_wildcard_and_garbage(self):
        """`*` 恒真；列表/垃圾输入保守返回 True。"""
        self.assert_eq(self.lm._cron_runs_today("55 8 * * *", date(2026, 8, 15)),
                       True, "* 每天覆盖")
        self.assert_eq(self.lm._cron_runs_today("0 9 * * 6,0", date(2026, 8, 15)),
                       True, "列表含周六")
        self.assert_eq(self.lm._cron_runs_today("not-a-cron"), True, "垃圾输入保守真")
        self.assert_eq(self.lm._cron_runs_today(""), True, "空表达式保守真")

    # ── 修复 1：周末暂停 cron 免误报 ──

    def _test_weekend_paused_cron_not_flagged(self):
        """工作日-only cron 在不该运行的当天，即使 last_run 已 4h 也不告警。

        回归点：2026-08-15 周六 04:02 实测 "lc-micro-scheduler (4h 未执行)"。
        星期域按当天动态构造，保证任意日期运行本测试均验证"非运行日"分支。

        v7.2.1: lc-micro-scheduler 在 cron_manifest 中登记实际 schedule 启用
        漂移检测——本测试通过 _patch_drift_skip 临时禁用 validate_cron_topology
        的 drift 校验，专注验证 _cron_runs_today 免检逻辑。
        """
        crons = self._base_crons()
        today = datetime.now().date()
        # 构造一个"今天不运行"的调度：工作日跑 or 周末跑，取反
        sched = "*/15 * * * 1-5" if today.weekday() >= 5 else "*/15 * * * 6,0"
        micro = self._find(crons, "lc-micro-scheduler")
        micro["schedule"] = sched
        micro["last_run"] = _iso(datetime.now(timezone.utc) - timedelta(hours=4))

        # 临时禁用 cron 漂移校验以隔离星期域检测逻辑
        from lifecycle import cron_manifest as cm_mod
        orig_spec = cm_mod.CRON_MANIFEST.get("lc-micro-scheduler", {}).copy()
        orig_schedule = orig_spec.get("schedule")
        if orig_schedule is not None:
            cm_mod.CRON_MANIFEST["lc-micro-scheduler"]["schedule"] = sched
        try:
            result = self._with_patch(crons)
        finally:
            if orig_schedule is not None:
                cm_mod.CRON_MANIFEST["lc-micro-scheduler"]["schedule"] = orig_schedule

        self.assert_eq(result, None, "非运行日不产生 cron_stale",
                       "星期域不含今天时不应告警（v6.9.2 修复项）")

    def _test_running_day_stale_still_flagged(self):
        """运行日 last_run 超阈值仍须检出（防止修复过度抑制真异常）。

        v7.2.1: lc-micro-scheduler 在 cron_manifest 中登记实际 schedule 启用
        漂移检测——本测试同步 schedule 与清单，专注验证陈旧检测逻辑。
        """
        crons = self._base_crons()
        today = datetime.now().date()
        sched = "*/15 * * * 1-5" if today.weekday() < 5 else "*/15 * * * 6,0"
        micro = self._find(crons, "lc-micro-scheduler")
        micro["schedule"] = sched
        micro["last_run"] = _iso(datetime.now(timezone.utc) - timedelta(hours=4))
        # interval=15min → threshold=max(2h,30min)=2h，4h 前最后运行应告警

        # 同步 schedule 到清单避免 drift 误报
        from lifecycle import cron_manifest as cm_mod
        orig_schedule = cm_mod.CRON_MANIFEST.get("lc-micro-scheduler", {}).get("schedule")
        if orig_schedule is not None:
            cm_mod.CRON_MANIFEST["lc-micro-scheduler"]["schedule"] = sched
        try:
            result = self._with_patch(crons)
        finally:
            if orig_schedule is not None:
                cm_mod.CRON_MANIFEST["lc-micro-scheduler"]["schedule"] = orig_schedule

        self.assert_eq(result is not None and result.get("type"), "cron_stale",
                       "运行日陈旧仍检出")
        self.assert_in("lc-micro-scheduler",
                       [s.split(" ")[0] for s in result.get("stale", [])],
                       "告警含 micro-scheduler")

    # ── 修复 2b：周末 repair 的 input cron 名映射 ──

    def _test_weekend_repair_input_cron_name(self):
        """weekend_input 应按 lc-weekend-input 对账，不得误报 double-weekend 名。"""
        import lifecycle.orchestrator as orch
        crons = [
            {"name": "lc-weekend-input", "schedule": "30 9 * * 6", "status": "active"},
            {"name": "lc-weekend-weekend-output", "schedule": "0 14 * * 6", "status": "active"},
            {"name": "lc-weekend-weekend-reflection", "schedule": "30 9 * * 0", "status": "active"},
        ]
        res = orch._run_weekend_repair(None, dry_run=True, lifecycle_crons=crons)
        actions = [a.strip() for item in res["repaired"] for a in item.get("actions", [])]
        self.assert_eq([a for a in actions if a.startswith("missing cron")], [],
                       "cron 齐全时不应有任何 missing cron")

        res2 = orch._run_weekend_repair(None, dry_run=True, lifecycle_crons=[])
        acts2 = [a.strip() for item in res2["repaired"] if item.get("job") == "weekend_input"
                 for a in item.get("actions", [])]
        self.assert_eq("missing cron lc-weekend-input" in acts2, True,
                       "缺失时报 lc-weekend-input")
        self.assert_eq(any("lc-weekend-weekend-input" in a for a in acts2), False,
                       "不得再报 double-weekend 名")

    # ── 修复 2：首跑前"从未执行"宽限 ──

    def _test_fresh_daily_cron_before_first_run_not_flagged(self):
        """昨晚创建的每日 cron（首跑在今天稍晚）不应被报"从未执行"。

        回归点：lc-daily-orchestrate 08-14 20:13 创建、08-15 08:55 首跑，
        旧逻辑（age>600s 即告警）连续误报 10 次。每日 interval=24h → 宽限 48h。
        """
        crons = self._base_crons()
        orch = self._find(crons, "lc-daily-orchestrate")
        orch["created_at"] = _iso(datetime.now(timezone.utc) - timedelta(hours=13))

        result = self._with_patch(crons)
        self.assert_eq(result, None, "新建每日 cron 首跑前不告警",
                       "13h < 48h 宽限，不应报从未执行（v6.9.2 修复项）")

    def _test_dead_cron_never_ran_still_flagged(self):
        """创建超 3 天从未运行 → 仍须检出（真死 cron 不被宽限掩盖）。"""
        crons = self._base_crons()
        orch = self._find(crons, "lc-daily-orchestrate")
        orch["created_at"] = _iso(datetime.now(timezone.utc) - timedelta(days=3))

        result = self._with_patch(crons)
        self.assert_eq(result is not None and result.get("type"), "cron_stale",
                       "超宽限未跑仍检出")
        self.assert_in("lc-daily-orchestrate (从未执行)",
                       result.get("stale", []), "从未执行告警保留")

    def _test_repair_cron_grace_boundary(self):
        """6h 间隔 cron 宽限 12h：创建 8h 未跑不告警，13h 未跑告警。"""
        crons8 = self._base_crons()
        self._find(crons8, "lc-repair")["created_at"] = \
            _iso(datetime.now(timezone.utc) - timedelta(hours=8))
        self.assert_eq(self._with_patch(crons8), None, "repair 8h 未跑不告警")

        # v6.9.68: repair 降频 6h→12h，stale 阈值随之 2×12h=24h——
        # 13h 未跑属正常间隔内；26h 未跑才超宽限
        crons13 = self._base_crons()
        self._find(crons13, "lc-repair")["created_at"] = \
            _iso(datetime.now(timezone.utc) - timedelta(hours=13))
        result = self._with_patch(crons13)
        self.assert_eq(result is None, True,
                       "repair 13h 未跑属 12h 调度正常间隔")

        crons26 = self._base_crons()
        self._find(crons26, "lc-repair")["created_at"] = \
            _iso(datetime.now(timezone.utc) - timedelta(hours=26))
        result = self._with_patch(crons26)
        self.assert_eq(result is not None and result.get("type"), "cron_stale",
                       "repair 26h 未跑超宽限检出")

    def run_tests(self):
        self._test_runs_today_weekday_only()
        self._test_runs_today_sunday_zero_and_seven()
        self._test_runs_today_wildcard_and_garbage()
        self._test_weekend_paused_cron_not_flagged()
        self._test_running_day_stale_still_flagged()
        self._test_weekend_repair_input_cron_name()
        self._test_fresh_daily_cron_before_first_run_not_flagged()
        self._test_dead_cron_never_ran_still_flagged()
        self._test_repair_cron_grace_boundary()


if __name__ == "__main__":
    suite = CronStaleWeekendGraceTests()
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
