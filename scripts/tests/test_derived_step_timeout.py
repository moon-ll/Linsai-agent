#!/usr/bin/env python3
"""
test_derived_step_timeout.py — 衍生步骤超时值验证测试

验证:
    v6.8.39: _run_update_vision_step 超时 300s→600s（保持）。
    v7.2.11: _run_update_method_manual_step 拆两阶段——阶段1（规划）
    timeout=240s、阶段2（逐节执行）每动作 timeout=300s，不再有 600s
    单会话（qgi r1 / attosecond r1 双超时实证全册读写负载超限）。

背景:
    key-transient r1 update_method_manual 实测超时(300s)→v6.8.39 放宽
    600s 仍超时（qgi/attosecond）→v7.2.11 拆阶段从根源降低单会话负载。

验证点:
    1. update_vision 调用 _run_hermes 时 timeout=600
    2. update_method_manual 阶段1 timeout=240、阶段2 timeout=300
    3. 阶段1超时失败透传 error 且带"阶段1"标记
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
        # v7.2.16: 屏蔽直调快路径——llm_router 真实可达时（如 minimax 无限额）
        # update_vision 直调成功会绕过 _run_hermes，mock 落空致 flaky
        # （实测：直调成功时 call_args=None，timeout 断言必挂）。
        # 本套件焦点是 hermes 路径的 timeout 值，直调路径由生产验证覆盖。
        self._orig_router = getattr(self.executor, "llm_router", None)
        self.executor.llm_router = None

    def teardown(self):
        if getattr(self, "executor", None) is not None:
            self.executor.llm_router = getattr(self, "_orig_router", None)

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
        # 测试 2: update_method_manual 两阶段（v7.2.11）
        #   阶段1（规划）timeout=240，阶段2（逐节执行）timeout=300
        # ================================================================
        import json as _json
        mock_self2 = self._make_mock_self(prop_dir)
        _plan = _json.dumps({"actions": [
            {"action": "add", "section": "新方法小节", "detail": "补充参数", "source_hint": ""},
        ]}, ensure_ascii=False)
        mock_self2._run_hermes.side_effect = [
            {"success": True, "output": _plan, "error": "", "elapsed_s": 20},
            {"success": True, "output": "已更新", "error": "", "elapsed_s": 40},
        ]
        # MagicMock 的 _parse_manual_plan 会返回 MagicMock（不可迭代为空），
        # 显式返回真实动作列表
        mock_self2._parse_manual_plan.return_value = [
            {"action": "add", "section": "新方法小节", "detail": "补充参数", "source_hint": ""},
        ]
        result2 = self.executor._run_update_method_manual_step(
            mock_self2, "test-proposal-20260101", {}
        )
        self.assert_true(
            result2.get("success"),
            "update_method_manual 应执行成功（两阶段）",
            f"result={result2}",
        )
        all_calls = mock_self2._run_hermes.call_args_list
        self.assert_eq(
            len(all_calls), 2,
            "两阶段应恰好 2 次调用（1 规划 + 1 执行）",
        )
        t_plan = all_calls[0].kwargs.get("timeout")
        t_exec = all_calls[1].kwargs.get("timeout")
        self.assert_eq(
            t_plan, 240,
            "阶段1（规划）超时应为 240s（v7.2.11）",
            f"实际 timeout={t_plan}",
        )
        self.assert_eq(
            t_exec, 300,
            "阶段2（逐节执行）超时应为 300s（v7.2.11）",
            f"实际 timeout={t_exec}",
        )
        self.assert_true(
            t_plan != 600 and t_exec != 600,
            "不应再有 600s 单会话超时（v7.2.11 拆阶段后单会话负载更小）",
        )

        # ================================================================
        # 测试 3: 阶段1超时失败时正确返回 error（回归保护）
        # ================================================================
        mock_self3 = self._make_mock_self(prop_dir)
        mock_self3._run_hermes.return_value = {
            "success": False, "error": "超时(240s)", "elapsed_s": 240.0,
        }
        result3 = self.executor._run_update_method_manual_step(
            mock_self3, "test-proposal-20260101", {}
        )
        self.assert_true(
            not result3.get("success") and "超时" in result3.get("error", "")
            and "阶段1" in result3.get("error", ""),
            "阶段1超时失败应透传 error 并带阶段标记",
            f"result={result3}",
        )
