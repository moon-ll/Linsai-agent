#!/usr/bin/env python3
"""
test_monitor_reviewer_fallback.py — monitor reviewer 通道空输出兜底回归测试（v7.3.19）

背景：
    `_call_reviewer` 走 hermes reviewer profile（agent 模式，需工具读盘）。实测对
    长评审输入（monitor-view ~90KB）返回 **0 退出码 + 空 stdout**，下游
    `monitor_independent_score=0` 判定解析失败，monitor 结果不落盘，晋级门条件②
    （独立分一致）永远卡住。

修复：
    hermes 通道返回空输出或失败时，自动回退 `llm_gateway.llm_complete` 单轮直连，
    评审对象（正文视图 + critic 摘要）由 `_build_inline_context` 内联进 prompt，
    零工具依赖；结果带 `channel` 字段便于观测，且仍走原有 JSON 解析，不伪造分数。

覆盖：
    1. hermes 空输出 → gateway 兜底成功
    2. hermes 正常输出 → 不触发 gateway
    3. hermes 空输出且 gateway 失败 → 返回失败并带 gateway_error（不伪造）
    4. hermes 非 0 退出码 → 同样走 gateway 兜底
    5. `_build_inline_context` 只内联存在的 .md 文件

注意：本测试 mock subprocess 与 LLM，不发起真实调用。
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent))

from adversarial import monitor as mon  # noqa: E402


def _hermes_result(stdout: str, returncode: int = 0):
    return mock.Mock(returncode=returncode, stdout=stdout, stderr="")


class MonitorReviewerFallbackTests(unittest.TestCase):
    def test_empty_stdout_falls_back_to_gateway(self):
        with mock.patch.object(mon.subprocess, "run", return_value=_hermes_result("")), \
                mock.patch("llm_gateway.llm_complete",
                           return_value=(True, '{"monitor_independent_score": 0.84}', {"provider": "glm"})):
            result = mon._call_reviewer("评审指令", inline_text="正文内容")
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("channel"), "gateway")
        self.assertIn("0.84", result.get("output", ""))
        self.assertEqual(result.get("provider"), "glm")

    def test_hermes_output_skips_gateway(self):
        with mock.patch.object(mon.subprocess, "run", return_value=_hermes_result('{"ok":1}')), \
                mock.patch("llm_gateway.llm_complete") as gw:
            result = mon._call_reviewer("评审指令", inline_text="正文内容")
        gw.assert_not_called()
        self.assertEqual(result.get("channel"), "hermes")
        self.assertEqual(result.get("output"), '{"ok":1}')

    def test_both_channels_empty_returns_failure(self):
        with mock.patch.object(mon.subprocess, "run", return_value=_hermes_result("")), \
                mock.patch("llm_gateway.llm_complete",
                           return_value=(False, "", {"error": "429"})):
            result = mon._call_reviewer("评审指令", inline_text="正文内容")
        self.assertFalse(result.get("success"))
        self.assertEqual(result.get("output"), "")
        self.assertIn("429", result.get("gateway_error", ""))

    def test_nonzero_exit_falls_back_to_gateway(self):
        with mock.patch.object(mon.subprocess, "run",
                               return_value=_hermes_result("", returncode=1)), \
                mock.patch("llm_gateway.llm_complete",
                           return_value=(True, "审查结论", {"provider": "glm"})):
            result = mon._call_reviewer("评审指令", inline_text="正文内容")
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("channel"), "gateway")

    def test_inline_context_only_reads_existing_md(self, ):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.md"
            b = Path(tmp) / "b.md"
            a.write_text("A 正文", encoding="utf-8")
            missing = Path(tmp) / "missing.md"
            ctx = mon._build_inline_context(a, missing, None, b)
            self.assertIn("A 正文", ctx)
            self.assertEqual(ctx, "A 正文")

    def test_no_inline_text_no_gateway(self):
        with mock.patch.object(mon.subprocess, "run", return_value=_hermes_result("")), \
                mock.patch("llm_gateway.llm_complete") as gw:
            result = mon._call_reviewer("评审指令")
        gw.assert_not_called()
        self.assertFalse(result.get("success"))


if __name__ == "__main__":
    unittest.main(argv=[__file__, "-v"], exit=False)
