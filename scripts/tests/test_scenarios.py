#!/usr/bin/env python3
"""
test_scenarios.py — 场景剧本测试（影子用户）

模拟 5 类典型用户与系统交互，验证端到端行为：
    1. 并肩工作：讨论固体 HHG 实验设计
    2. 深度对话：PRL 被拒后的情绪支持
    3. 快速验证：量纲检查
    4. 任务驱动：创建 DFG 申请提醒
    5. 主动感知：截止日期临近检测
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT, TestResult
import importlib


class ScenarioTests(TestSuite):
    def __init__(self):
        super().__init__("场景剧本测试（影子用户）")
        self.tmp_root = None
        self.sm = None
        self.skm = None
        self.tm = None
        self.pe = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in ["session_manager", "skill_manager", "task_manager", "proactive_engine"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        self.sm = importlib.import_module("session_manager")
        self.skm = importlib.import_module("skill_manager")
        self.tm = importlib.import_module("task_manager")
        self.pe = importlib.import_module("proactive_engine")

        for mod in [self.sm, self.skm, self.tm, self.pe]:
            patch_module_root(mod.__name__, self.tmp_root)
        # task_manager 额外缓存变量
        self.tm.TASKS_DIR = self.tmp_root / "tasks"
        self.tm.STATUS_DIRS = {
            "backlog": self.tm.TASKS_DIR / "backlog",
            "active": self.tm.TASKS_DIR / "active",
            "completed": self.tm.TASKS_DIR / "completed",
            "paused": self.tm.TASKS_DIR / "backlog",
        }

        # 技能用真实数据（只读）
        patch_module_root("skill_manager", REAL_ROOT)
        self.skm.reload_skills()

    def teardown(self):
        import shutil
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ------------------------------------------------------------------
    # 场景1：并肩工作 — 固体 HHG 实验设计
    # ------------------------------------------------------------------
    def _scenario_co_working(self):
        sid, _ = self.sm.create_session("固体HHG光路设计", "co-working")
        self.sm.append_message(sid, "user", "我在设计固体HHG实验，激光波长800nm，强度1e14 W/cm²，晶体厚度500μm")
        self.sm.append_message(sid, "assistant", "你用的是 BBO 还是 ZnO？相位匹配条件考虑过吗？")
        self.sm.append_message(sid, "user", "还没确定，BBO的d33更高但ZnO的损伤阈值更好")

        # 检查：技能触发
        matched = self.skm.match_skills("固体HHG实验设计")
        self.assert_in("experiment-design", matched, "场景1-触发 experiment-design")

        # 检查：会话消息数
        msgs, state = self.sm.load_session(sid)
        self.assert_eq(len(msgs), 3, "场景1-消息数=3")
        self.assert_eq(state["mode"], "co-working", "场景1-模式正确")

    # ------------------------------------------------------------------
    # 场景2：深度对话 — PRL 被拒
    # ------------------------------------------------------------------
    def _scenario_deep_talk(self):
        sid, _ = self.sm.create_session("PRL拒稿后", "deep-talk")
        self.sm.append_message(sid, "user", "PRL又被拒了，我开始怀疑这个方向是不是错了")
        self.sm.append_message(sid, "assistant", "我懂你。我第一篇PRL也转了PRA。关键不是期刊，是审稿人的核心质疑是什么。")

        msgs, state = self.sm.load_session(sid)
        self.assert_eq(state["mode"], "deep-talk", "场景2-模式为 deep-talk")
        self.assert_true(any("PRL" in m.get("content", "") for m in msgs), "场景2-内容含PRL")

    # ------------------------------------------------------------------
    # 场景3：快速验证 — 量纲检查
    # ------------------------------------------------------------------
    def _scenario_quick_check(self):
        sid, _ = self.sm.create_session("量纲检查", "quick-check")
        self.sm.append_message(sid, "user", "E = ħω 的量纲对吗？")

        msgs, _ = self.sm.load_session(sid)
        self.assert_eq(len(msgs), 1, "场景3-单条消息")

        # 技能触发：math-derivation 或 code-review 可能匹配
        matched = self.skm.match_skills("量纲检查 ħω")
        # 不强制断言具体技能，只断言不崩溃
        self.assert_true(isinstance(matched, list), "场景3-技能匹配不崩溃")

    # ------------------------------------------------------------------
    # 场景4：任务驱动 — DFG 申请截止提醒
    # ------------------------------------------------------------------
    def _scenario_task_driven(self):
        # 创建带截止日期的任务
        due = "2026-05-20T23:59:00Z"
        task_id, task_path = self.tm.create_task("DFG申请提交", priority="high", category="admin", due_date=due)
        tid = task_id

        # 检查任务存在
        fetched = self.tm.get_task(tid)
        self.assert_eq(fetched["title"], "DFG申请提交", "场景4-任务标题")
        self.assert_eq(fetched["status"], "backlog", "场景4-初始状态")

        # 检查逾期检测（由于日期在未来，不应逾期）
        overdue = self.tm.check_overdue_tasks()
        self.assert_true(not any(t["task_id"] == tid for t in overdue), "场景4-未逾期")

        # 模拟任务完成
        self.tm.transition_task(tid, "active")
        self.tm.transition_task(tid, "completed")
        completed = self.tm.list_tasks("completed")
        self.assert_true(any(t["task_id"] == tid for t in completed), "场景4-完成流转")

        # 子任务
        self.tm.add_subtask(tid, "准备预算表")
        updated = self.tm.get_task(tid)
        self.assert_true(len(updated.get("subtasks", [])) >= 1, "场景4-子任务添加")

    # ------------------------------------------------------------------
    # 场景5：主动感知 — 压力信号检测
    # ------------------------------------------------------------------
    def _scenario_proactive(self):
        sid, _ = self.sm.create_session("压力大", "co-working")
        self.sm.append_message(sid, "user", "连续三天失眠，对数据完全麻木了")

        # 检查 proactive_engine 的压力信号检测（使用真实模块，但隔离文件操作）
        patch_module_root("proactive_engine", self.tmp_root)
        pe = importlib.import_module("proactive_engine")

        result = pe.detect_stress_signals(sid)
        self.assert_true(isinstance(result, dict), "场景5-压力信号返回字典")
        signals = result.get("signals", [])
        self.assert_true(isinstance(signals, list), "场景5-信号列表")
        # 如果检测到压力词，应该有信号
        if signals:
            self.assert_in("keyword", signals[0], "场景5-信号有keyword字段")
            self.assert_in("severity", signals[0], "场景5-信号有severity字段")

    # ------------------------------------------------------------------
    def run_tests(self):
        print(f"\n▶ {self.name}")
        tests = [
            self._scenario_co_working,
            self._scenario_deep_talk,
            self._scenario_quick_check,
            self._scenario_task_driven,
            self._scenario_proactive,
        ]
        for t in tests:
            try:
                t()
            except Exception as e:
                import traceback
                self.results.append(
                    TestResult(t.__name__, False, 0.0, f"{type(e).__name__}: {e}")
                )
