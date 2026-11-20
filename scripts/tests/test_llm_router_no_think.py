#!/usr/bin/env python3
"""
test_llm_router_no_think.py — llm_router 机械任务请求级关思考回归（v7.3.83）

背景：2026-11-15 token 治理裁决①——账本周回溯 think-only 57 次空烧 622k
tokens 零产出；kb_distill / weekend_input 为结构化抽取/格式化任务，GLM 系
(bigmodel) 支持请求级 thinking 参数，关思考后思考 token 直接不产生。

覆盖：
    1. 机械任务（kb_distill）对 glm 注入 thinking:disabled
    2. 判断类任务（panel/governance）不注入
    3. 非 GLM provider（minimax）不注入
    4. 端点 HTTP 400 拒绝参数时剥离重发一次（第二发成功）
    5. call() → _call_api 的 prefer 透传链路

注意：零真实网络调用（monkeypatch urlopen 捕获 payload）。
"""

import json
import sys
import urllib.error
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


def _make_provider(name="glm", model="glm-5.3"):
    from llm_router import LLMProvider
    return LLMProvider({
        "name": name,
        "type": "api",
        "priority": 3,
        "base_url": "https://fake.invalid/api",
        "api_key": "test-key",
        "model": model,
    })


class _FakeResp:
    """假 urlopen 返回：记录请求 payload，回 200 JSON。"""
    last_payload = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return json.dumps({
            "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        }).encode("utf-8")


class _Fake400Resp(_FakeResp):
    """第一发回 400，第二发放行（用类属性计数区分）。"""

    def read(self):
        _Fake400Resp.count += 1
        if _Fake400Resp.count == 1:
            raise urllib.error.HTTPError(
                "fake", 400, "thinking param not supported",
                {}, io.BytesIO(b'{"error":"bad request"}'))
        return super().read()


import io  # noqa: E402  (置于 _Fake400Resp 之后仅为可读性)


class LlmRouterNoThinkTests(TestSuite):
    def __init__(self):
        super().__init__("llm_router 机械任务关思考测试（v7.3.83）")

    def _capture(self, provider, prefer, resp_cls=_FakeResp):
        """monkeypatch urlopen，跑 _call_api，返回捕获的 payload 列表。"""
        import urllib.request
        payloads = []
        orig = urllib.request.urlopen

        def fake_urlopen(req, timeout=0, context=None):
            payloads.append(json.loads(req.data.decode("utf-8")))
            resp_cls.last_payload = payloads[-1]
            if isinstance(resp := resp_cls(), object) and resp_cls is _Fake400Resp:
                return resp
            return _FakeResp()

        urllib.request.urlopen = fake_urlopen
        try:
            provider._call_api("sys", [{"role": "user", "content": "hi"}],
                               timeout=3, prefer=prefer)
        finally:
            urllib.request.urlopen = orig
        return payloads

    def run_tests(self):
        import io as _io  # 确保 io 可用（_Fake400Resp 使用）

        # 1. 机械任务 kb_distill 对 glm 注入 thinking:disabled
        payloads = self._capture(_make_provider(), "kb_distill")
        self.assert_true(
            len(payloads) == 1 and payloads[0].get("thinking") == {"type": "disabled"},
            "kb_distill 对 glm 注入 thinking:disabled",
            f"payload={payloads}",
        )

        # 2. weekend_input 同样注入
        payloads = self._capture(_make_provider(), "weekend_input")
        self.assert_true(
            payloads[0].get("thinking") == {"type": "disabled"},
            "weekend_input 对 glm 注入 thinking:disabled",
            f"payload={payloads}",
        )

        # 3. 判断类任务不注入
        for pref in ("panel", "governance", None):
            payloads = self._capture(_make_provider(), pref)
            self.assert_true(
                "thinking" not in payloads[0],
                f"prefer={pref} 不注入 thinking",
                f"payload={payloads[0].get('thinking')}",
            )

        # 4. 非 GLM provider 不注入
        payloads = self._capture(_make_provider(name="minimax", model="MiniMax-M3"),
                                 "kb_distill")
        self.assert_true(
            "thinking" not in payloads[0],
            "minimax 不注入 thinking（仅 GLM 系支持该参数）",
            f"payload={payloads[0].get('thinking')}",
        )

        # 5. HTTP 400 → 剥离重发一次成功（第二发无 thinking 字段）
        _Fake400Resp.count = 0
        payloads = self._capture(_make_provider(), "kb_distill", _Fake400Resp)
        self.assert_true(
            len(payloads) == 2 and "thinking" not in payloads[1],
            "400 拒绝后剥离 thinking 重发一次",
            f"发数={len(payloads)} 第二发thinking={payloads[-1].get('thinking')}",
        )

        # 6. call() → _call_api prefer 透传链路
        import urllib.request
        payloads6 = []
        orig = urllib.request.urlopen

        def fake6(req, timeout=0, context=None):
            payloads6.append(json.loads(req.data.decode("utf-8")))
            return _FakeResp()

        urllib.request.urlopen = fake6
        try:
            _make_provider().call("sys", [{"role": "user", "content": "hi"}],
                                  timeout=3, prefer="kb_distill")
        finally:
            urllib.request.urlopen = orig
        self.assert_true(
            payloads6 and payloads6[0].get("thinking") == {"type": "disabled"},
            "call() 透传 prefer 至 _call_api",
            f"payload={payloads6}",
        )


if __name__ == "__main__":
    suite = LlmRouterNoThinkTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    failed = [r for r in suite.results if not r.passed]
    print(f"完成：通过 {len(suite.results) - len(failed)}，失败 {len(failed)}")
    for r in failed:
        print(f"  ✗ {r.name}: {r.msg}")
    sys.exit(1 if failed else 0)
