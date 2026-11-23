#!/usr/bin/env python3
"""LLM 解析失败三层修复测试（v6.10.9）。

覆盖周末输入端实测三类失败：
① 空 content（router._call_api 抛错 + gateway 兜底）
② 响应截断（TASK_MAX_TOKENS 放宽 weekend_input）
③ 开头围栏无闭合（_llm_json 剥离前置 ```json）

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_llm_parse_hardening.py
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


class LlmParseHardeningTests(TestSuite):
    def __init__(self):
        super().__init__("LLM 解析失败三层修复测试（v6.10.9）")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        # ── 1. TASK_MAX_TOKENS 放宽 weekend_input ──────────────
        from llm_router import TASK_MAX_TOKENS
        self.assert_eq(TASK_MAX_TOKENS.get("weekend_input"), 16384,
                       "weekend_input 应放宽到 16384")
        self.assert_eq(TASK_MAX_TOKENS.get("kb_distill_deep"), 16384,
                       "kb_distill_deep 原值保持")

        # ── 2. _llm_json：完整围栏（原行为不回归）──────────────
        from weekend_pipeline.input_jobs import _llm_json
        orig_complete = _llm_json.__globals__["llm_complete"]
        orig_avail = _llm_json.__globals__["is_llm_available"]
        try:
            _llm_json.__globals__["is_llm_available"] = lambda: True

            def _mock(text):
                def _f(system, user, timeout=120, prefer=None):
                    return True, text, {"provider": "mock"}
                return _f

            ok_case = '```json\n{"core": "测试", "n": 1}\n```'
            _llm_json.__globals__["llm_complete"] = _mock(ok_case)
            r = _llm_json("s", "u")
            self.assert_eq(r, {"core": "测试", "n": 1}, "完整围栏应正常解析")

            # ── 3. 开头围栏无闭合（v6.10.9 剥离）────────────────
            # 实测 06:24 形态：```json 开头 + 完整 JSON 但尾部 ``` 截断
            trunc_case = '```json\n{"core": "截断但括号完整", "n": 2}'
            _llm_json.__globals__["llm_complete"] = _mock(trunc_case)
            r = _llm_json("s", "u")
            self.assert_eq(r, {"core": "截断但括号完整", "n": 2},
                           "开头围栏无闭合应剥离后解析")

            # ── 4. 真截断（无闭合 }）→ None 不抛异常 ────────────
            dead_case = '{\n  "core": "很长正文被切断'
            _llm_json.__globals__["llm_complete"] = _mock(dead_case)
            r = _llm_json("s", "u")
            self.assert_eq(r, None, "无闭合括号的截断响应应安全返回 None")

            # ── 5. 空响应 → None 不抛异常 ───────────────────────
            _llm_json.__globals__["llm_complete"] = _mock("")
            r = _llm_json("s", "u")
            self.assert_eq(r, None, "空响应应返回 None")

            # ── 6. 前言+JSON 尾注（v6.10.1 降级保持）────────────
            noise_case = '以下是分析结果：\n{"core": "带前言"}\n希望有帮助'
            _llm_json.__globals__["llm_complete"] = _mock(noise_case)
            r = _llm_json("s", "u")
            self.assert_eq(r, {"core": "带前言"}, "前言尾注形态应走大括号降级")

        finally:
            _llm_json.__globals__["llm_complete"] = orig_complete
            _llm_json.__globals__["is_llm_available"] = orig_avail

        # ── 7. router._call_api 空 content 抛错 ─────────────────
        # 用 monkeypatch urlopen 返回空 content 的 200 响应
        from unittest import mock
        from llm_router import LLMProvider
        import json as _json

        class _FakeResp:
            def read(self):
                return _json.dumps({
                    "choices": [{"message": {"content": ""},
                                 "finish_reason": "stop"}],
                }).encode("utf-8")
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False

        p = LLMProvider({
            "name": "t", "type": "api",
            "base_url": "https://example.invalid/v1",
            "api_key": "k", "model": "m",
        })
        with mock.patch("urllib.request.urlopen", return_value=_FakeResp()):
            try:
                p._call_api("sys", [{"role": "user", "content": "u"}], 30)
                raised = False
            except RuntimeError as e:
                raised = True
                self.assert_true("空 content" in str(e), "错误信息应说明空 content")
        self.assert_true(raised, "空 content 应抛 RuntimeError（触发 provider 降级）")

        # ── 8. gateway 空 content 兜底 ─────────────────────────
        from llm_gateway import llm_complete as gw_complete
        import llm_gateway as gw
        orig_router = gw._get_router

        class _R:
            def call_llm(self, s, m, timeout=90, prefer=None):
                return ("", {}, "mock-empty")

        try:
            gw._get_router = lambda: _R()
            ok, text, meta = gw_complete("s", "u")
            self.assert_eq(ok, False, "空 content 应视为失败")
            self.assert_eq(text, "", "失败时文本为空")
            self.assert_eq(meta.get("error"), "empty content", "错误标记")
        finally:
            gw._get_router = orig_router


def main() -> None:
    suite = LlmParseHardeningTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
