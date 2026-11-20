#!/usr/bin/env python3
"""
test_input_breaker.py — lifecycle_monitor 输入端熔断检测测试

历史：
    v6.8.27 引入检测；v6.8.27-v6.8.52 读 weekend-jobs.json 顶层
    weekend_input 键（结构嵌套错误 + 从不记录 ideas_count），检测从未
    可能触发；v6.8.53 数据源改读 weekend-pipeline.json 的 input job
    结果；v6.9.10 口径再修正——旧实现"最近一次 ideas=0 且距今 ≥7 天"
    会被每周空跑刷新 finished_at（days_since 永远到不了 7），防线
    形同虚设。现口径扫 weekend-input/ideas-*.json 产物文件族：最近
    2 个文件 ideas 均为空即告警，不受空跑刷新影响。

注意：
    本测试不调用 hermes/LLM，使用隔离临时目录。
"""

import sys
import json
import shutil
import importlib

from test_runner import TestSuite, create_isolated_env


class InputBreakerTests(TestSuite):
    def __init__(self):
        super().__init__("输入端熔断数据源测试")
        self.tmp_root = None
        self.monitor = None
        self._orig_root = None
        self._hq_orig_dir = None

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

        # v7.2.55：human_queue 侧 input_broken 检测共用本隔离目录
        import human_queue
        self._hq_orig_dir = human_queue.WEEKEND_INPUT_DIR
        human_queue.WEEKEND_INPUT_DIR = (
            self.tmp_root / "memory" / "weekend-input"
        )

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if self._orig_root is not None:
            self.monitor.PROJECT_ROOT = self._orig_root
        if self._hq_orig_dir is not None:
            import human_queue
            human_queue.WEEKEND_INPUT_DIR = self._hq_orig_dir

    def _write_ideas(self, date: str, ideas) -> None:
        path = self.tmp_root / "memory" / "weekend-input" / f"ideas-{date}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"ideas": ideas}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _write_compose_output(self, date: str, actions) -> None:
        """按 compose 实际产出 schema 写文件（v6.9.13 口径锁定）。

        新旧 compose 均写 {"generated_at", "actions":[...]}，从未写过
        "ideas" 键——旧口径只读 "ideas" 恒为 0，链路恢复后告警永不解除。
        """
        path = self.tmp_root / "memory" / "weekend-input" / f"ideas-{date}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"generated_at": f"{date}T12:00:00Z", "actions": actions}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _breaker_anomalies(self):
        _, anomalies = self.monitor._check_proposals()
        return [a for a in anomalies if a.get("type") == "input_pipeline_broken"]

    def run_tests(self):
        # ── 用例 1：最近 2 个产物文件均空 → 触发熔断告警 ──
        self._write_ideas("2026-08-14", [])
        self._write_ideas("2026-08-15", [])
        hits = self._breaker_anomalies()
        self.assert_eq(len(hits), 1, "连续 2 次周末零设想应触发 input_pipeline_broken")
        if hits:
            self.assert_in(
                "2026-08-14", hits[0].get("message", ""),
                "告警应指出来源产物文件日期",
            )

        # ── 用例 2：最近一次产出非零 → 不触发（正常产出） ──
        self._write_ideas("2026-08-15", [{"title": "t", "gap": "g"}])
        self.assert_eq(
            len(self._breaker_anomalies()), 0,
            "最近一次产出非零（ideas=1）不应触发",
        )

        # ── 用例 3：仅 1 个产物文件 → 不触发（第二周窗口未过） ──
        for f in (self.tmp_root / "memory" / "weekend-input").glob("ideas-*.json"):
            f.unlink()
        self._write_ideas("2026-08-15", [])
        self.assert_eq(
            len(self._breaker_anomalies()), 0,
            "单产物文件（周窗口未过）不应触发",
        )

        # ── 用例 4：旧数据形状不再参与判定（数据源唯一） ──
        # weekend-jobs.json 顶层键与 weekend-pipeline.json job result
        # 均非新口径数据源，存在也不产生重复/误报。
        for f in (self.tmp_root / "memory" / "weekend-input").glob("ideas-*.json"):
            f.unlink()
        legacy = {
            "weekend_input": {
                "status": "done",
                "result": {"ideas_count": 0},
            }
        }
        (self.tmp_root / "memory" / "weekend-jobs.json").write_text(
            json.dumps(legacy, ensure_ascii=False), encoding="utf-8"
        )
        jobs = [
            {
                "job_id": "input_compose_ideas",
                "stage": "input",
                "status": "done",
                "finished_at": "2026-08-15T11:00:58Z",
                "result": {"ideas_count": 0},
            }
        ]
        (self.tmp_root / "memory" / "weekend-pipeline.json").write_text(
            json.dumps({"jobs": jobs}, ensure_ascii=False),
            encoding="utf-8",
        )
        self.assert_eq(
            len(self._breaker_anomalies()), 0,
            "数据源唯一（ideas-*.json），旧形状不产生误报",
        )

        # ── 用例 5：compose 真实 schema（actions 非空）→ 不触发 ──
        # v6.9.13 回归：compose 写 {"generated_at","actions"}，无 "ideas"
        # 键。旧口径对该 schema 恒读 0，链路恢复后告警永不解除。
        for f in (self.tmp_root / "memory" / "weekend-input").glob("ideas-*.json"):
            f.unlink()
        self._write_compose_output("2026-08-14", [])
        self._write_compose_output(
            "2026-08-15",
            [{"cluster_id": "cl_1", "action": "new", "result": {"success": True}}],
        )
        self.assert_eq(
            len(self._breaker_anomalies()), 0,
            "真实 schema 最近一次 actions 非空不应触发（旧口径误报）",
        )

        # ── 用例 6：compose 真实 schema（actions 均空）→ 触发 ──
        self._write_compose_output("2026-08-15", [])
        self.assert_eq(
            len(self._breaker_anomalies()), 1,
            "真实 schema 连续 2 次 actions 为空应触发",
        )

        # ── 用例 7-9（v7.2.55 改进项 p）：human_queue 侧 input_broken 入队 ──
        import human_queue
        from datetime import datetime, timezone

        # 用例 7：同口径（最近 2 文件 actions 均空）→ 入队 + 等待时长按较旧文件日期
        items = human_queue._pending_input_broken(
            datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc))
        self.assert_eq(len(items), 1, "连续 2 次零设想应入队 input_broken")
        if items:
            self.assert_eq(items[0]["type"], "input_broken", "类型应为 input_broken")
            # 较旧文件 2026-08-14 00:00Z → 2026-08-20 12:00Z = 156h
            self.assert_eq(items[0]["waiting_hours"], 156.0, "等待时长应按较旧文件零点起算")
            self.assert_in("2026-08-14", items[0]["detail"], "detail 应含较旧文件日期")

        # 用例 8：最近一次 actions 非空 → 不入队（恢复即自动退出）
        self._write_compose_output(
            "2026-08-15",
            [{"cluster_id": "cl_1", "action": "new", "result": {"success": True}}],
        )
        items = human_queue._pending_input_broken(
            datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc))
        self.assert_eq(len(items), 0, "最近一次产出非零不应入队")

        # 用例 9：escalate 联动——等待 ≥72h 的 input_broken 在聚合结果中被催办
        self._write_compose_output("2026-08-15", [])
        result = human_queue.collect_human_queue(proposals={}, now=None)
        broken = [i for i in result["items"] if i.get("type") == "input_broken"]
        self.assert_eq(len(broken), 1, "聚合结果应含 input_broken 项")
        if broken:
            self.assert_true(broken[0]["escalate"], "等待超 72h 应标记 escalate")
            self.assert_eq(result["summary"]["input_broken"], 1, "summary 应统计 input_broken")
