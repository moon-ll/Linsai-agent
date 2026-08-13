#!/usr/bin/env python3
"""
test_derived_step_timeout.py — 衍生步骤超时值验证测试

验证 v6.8.39 修复:
    _run_update_vision_step / _run_update_method_manual_step 的 writer 调用
    超时由 300s 放宽到 600s，与 v6.8.37 references/critic 修复策略一致。

背景:
    key-transient r1 update_method_manual 实测超时(300s)（2026-08-13T19:05-19:10Z）。
    该步骤是轮次链末端，300s 超时若持续触发，repair 重试 3 次耗尽后
    轮次无法完成、课题卡死（与 v6.8.37 quantum-geometry 卡死同源）。

验证点:
    1. update_vision 调用 _run_hermes 时 timeout=600
    2. update_method_manual 调用 _run_hermes 时 timeout=600
"""

import sys
import importlib
from pathlib import Path
from unittest.mock import MagicMock

from test_runner import TestSuite, create_isolated_env


class DerivedStepTimeoutTests(TestSuite):
    def __init__(self):
        super().__init__("衍生步骤超时值验证测试")
        self.tmp_root = None
        self.executor = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in list(sys.modules.keys()):
            if mod_name in [
                "lifecycle", "lifecycle.executor", "paths", "common",
                "proposal_lifecycle", "proposal_sections",
            ]:
                del sys.modules[mod_name]
        self.executor = importlib.import_module("lifecycle.executor")

    def teardown(self):
        pass

    def _make_mock_self(self, prop_dir: Path) -> MagicMock:
        """构造 mock self：_find_proposal_dir 返回临时目录，_run_hermes 记录调用。"""
        mock_self = MagicMock()
        mock_self._find_proposal_dir.return_value = prop_dir
        mock_self._run_hermes.return_value = {"success": True, "output": "ok"}
        return mock_self

    def _make_prop_dir(self) -> Path:
        """构造带 proposal-draft.md 与 sections/scheme.md 的临时课题目录。"""
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / "test-proposal-20260101"
        sections = prop_dir / "04_proposal" / "sections"
        sections.mkdir(parents=True, exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text(
            "# 申请书\n\n" + "x" * 200, encoding="utf-8"
        )
        (sections / "scheme.md").write_text(
            "# 研究方案\n\n" + "y" * 200, encoding="utf-8"
        )
        return prop_dir

    def run_tests(self):
        prop_dir = self._make_prop_dir()

        # ================================================================
        # 测试 1: update_vision 使用 timeout=600
        # ================================================================
        mock_self = self._make_mock_self(prop_dir)
        result = self.executor._run_update_vision_step(mock_self, "test-proposal-20260101", {})
        self.assert_true(
            result.get("success"),
            "update_vision 应执行成功",
            f"result={result}",
        )
        call_args = mock_self._run_hermes.call_args
        timeout = call_args.kwargs.get("timeout") if call_args and call_args.kwargs else None
        self.assert_eq(
            timeout, 600,
            "update_vision 超时应为 600s（v6.8.39 修复）",
            f"实际 timeout={timeout}，call_args={call_args}",
        )

        # ================================================================
        # 测试 2: update_method_manual 使用 timeout=600
        # ================================================================
        mock_self2 = self._make_mock_self(prop_dir)
        result2 = self.executor._run_update_method_manual_step(
            mock_self2, "test-proposal-20260101", {}
        )
        self.assert_true(
            result2.get("success"),
            "update_method_manual 应执行成功",
            f"result={result2}",
        )
        call_args2 = mock_self2._run_hermes.call_args
        timeout2 = call_args2.kwargs.get("timeout") if call_args2 and call_args2.kwargs else None
        self.assert_eq(
            timeout2, 600,
            "update_method_manual 超时应为 600s（v6.8.39 修复）",
            f"实际 timeout={timeout2}，call_args={call_args2}",
        )

        # ================================================================
        # 测试 3: 超时失败时正确返回 error（回归保护）
        # ================================================================
        mock_self3 = self._make_mock_self(prop_dir)
        mock_self3._run_hermes.return_value = {
            "success": False, "error": "超时(600s)", "elapsed_s": 600.0,
        }
        result3 = self.executor._run_update_method_manual_step(
            mock_self3, "test-proposal-20260101", {}
        )
        self.assert_true(
            not result3.get("success") and "超时" in result3.get("error", ""),
            "超时失败应透传 error",
            f"result={result3}",
        )
