#!/usr/bin/env python3
"""
test_input_breaker.py — lifecycle_monitor 输入端熔断数据源修复测试（v6.8.53）

覆盖缺陷：
    lifecycle_monitor._check_proposals 的输入端熔断检测读
    weekend-jobs.json 顶层 weekend_input 键——实际结构嵌套在 jobs 下
    （weekend_data["jobs"]["weekend_input"]），且该文件从不记录
    result.ideas_count。双错叠加导致该检测自 v6.8.27 起从未可能触发：
    输入端自 08-01 起停摆 13 天（ideas=0 且未再执行）无人告警。

修复：
    数据源改读 weekend-pipeline.json 的 input job 结果
    （result.ideas_count + finished_at）。

注意：
    本测试不调用 hermes/LLM，使用隔离临时目录。
"""

import sys
import json
import shutil
import importlib
from datetime import datetime, timezone, timedelta

from test_runner import TestSuite, create_isolated_env


class InputBreakerTests(TestSuite):
    def __init__(self):
        super().__init__("输入端熔断数据源测试")
        self.tmp_root = None
        self.monitor = None
        self._orig_root = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)

        # 强制重新导入 lifecycle_monitor，避免缓存污染
        for mod_name in list(sys.modules.keys()):
            if mod_name == "lifecycle_monitor":
                del sys.modules[mod_name]

        self.monitor = importlib.import_module("lifecycle_monitor")
        self._orig_root = self.monitor.PROJECT_ROOT
        self.monitor.PROJECT_ROOT = self.tmp_root
        self.monitor.KANBAN_PATH = self.tmp_root / "memory" / "system-kanban.json"
        self.monitor.ALERT_CACHE_PATH = (
            self.tmp_root / "memory" / "monitor-alert-cache.json"
        )

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if self._orig_root is not None:
            self.monitor.PROJECT_ROOT = self._orig_root

    def _write_pipeline(self, ideas_count: int, finished_days_ago: float) -> None:
        fin = (
            datetime.now(timezone.utc) - timedelta(days=finished_days_ago)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        jobs = [
            {
                "job_id": "input_compose_ideas",
                "stage": "input",
                "status": "done",
                "finished_at": fin,
                "result": {"ideas_count": ideas_count},
            },
            {
                # 无 ideas_count 的 input job 应被过滤
                "job_id": "input_collect_sources",
                "stage": "input",
                "status": "done",
                "finished_at": fin,
                "result": {"sources": 5},
            },
        ]
        path = self.tmp_root / "memory" / "weekend-pipeline.json"
        path.write_text(
            json.dumps({"jobs": jobs, "updated_at": fin}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _breaker_anomalies(self):
        _, anomalies = self.monitor._check_proposals()
        return [a for a in anomalies if a.get("type") == "input_pipeline_broken"]

    def run_tests(self):
        # ── 用例 1：ideas=0 且 ≥7 天无新产出 → 触发熔断告警 ──
        self._write_pipeline(ideas_count=0, finished_days_ago=13)
        hits = self._breaker_anomalies()
        self.assert_eq(len(hits), 1, "停摆 13 天且 ideas=0 应触发 input_pipeline_broken")
        if hits:
            self.assert_in(
                "input_compose_ideas", hits[0].get("message", ""),
                "告警应指出来源 job",
            )

        # ── 用例 2：ideas>0 → 不触发（正常产出） ──
        self._write_pipeline(ideas_count=3, finished_days_ago=13)
        self.assert_eq(
            len(self._breaker_anomalies()), 0,
            "上周有产出（ideas=3）不应触发",
        )

        # ── 用例 3：ideas=0 但仅 2 天 → 不触发（第二周窗口未过） ──
        self._write_pipeline(ideas_count=0, finished_days_ago=2)
        self.assert_eq(
            len(self._breaker_anomalies()), 0,
            "仅 2 天未产出（周窗口未过）不应触发",
        )

        # ── 用例 4：旧错误数据形状（weekend-jobs.json 顶层键）不再影响 ──
        legacy = {
            "weekend_input": {
                "status": "done",
                "started_at": (
                    datetime.now(timezone.utc) - timedelta(days=30)
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "result": {"ideas_count": 0},
            }
        }
        (self.tmp_root / "memory" / "weekend-jobs.json").write_text(
            json.dumps(legacy, ensure_ascii=False), encoding="utf-8"
        )
        self._write_pipeline(ideas_count=0, finished_days_ago=13)
        hits = self._breaker_anomalies()
        self.assert_eq(
            len(hits), 1,
            "数据源唯一（weekend-pipeline.json），旧形状不产生重复/误报",
        )
