#!/usr/bin/env python3
"""
test_llm_router_429_no_retry.py — llm_router 429 限流不空转回归（v7.3.66）

背景：`_call_api` 把 urllib HTTPError 统一包成 RuntimeError，路由层的
`except HTTPError` 分支取不到 429，落入通用异常分支后对同 provider 重试。
11-07 18:51 日志实测同一调用连发两条 429（request_id 不同）后才降级 kimi，
失败账本与限流计数被无谓放大。

覆盖：
    1. 429 → provider.call 抛 RateLimitError（不再包成普通 RuntimeError）
    2. 降级链 retry=1：429 provider 只被调 1 次（不重试），成功切到下一 provider
    3. 非 429 错误（如 500）仍按原语义重试（不回归通用重试通道）

注意：零真实网络调用（urlopen 打桩）；计量账本 monkeypatch 在内存捕获。
"""

import io
import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


class _FakeResp:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _make_api_provider(name: str, base_url: str, priority: int = 1):
    from llm_router import LLMProvider
    return LLMProvider({
        "name": name,
        "type": "api",
        "priority": priority,
        "base_url": base_url,
        "api_key": "test-key",
        "model": "test-model",
    })


def _make_router(providers, retry: int = 0):
    from llm_router import LLMRouter
    r = LLMRouter.__new__(LLMRouter)
    r.config = {"providers": [], "strategy": "priority", "timeout": 10, "retry": retry}
    r.providers = list(providers)
    r._round_robin_idx = 0
    r.force_provider = None
    r._last_used = None
    return r


def _ok_body(text: str) -> bytes:
    return json.dumps({
        "choices": [{"message": {"content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20},
    }).encode("utf-8")


class LlmRouter429NoRetryTests(TestSuite):
    def __init__(self):
        super().__init__("llm_router 429 限流不重试回归测试（v7.3.66）")

    def run_tests(self):
        import llm_router

        # ── 1. 429 → 专用 RateLimitError ─────────────────────
        p = _make_api_provider("p-429", "http://127.0.0.1:9/v1-429")

        def _raise_429(req, timeout=None, context=None):
            raise llm_router.urllib.error.HTTPError(
                "http://127.0.0.1:9/v1-429", 429, "Too Many Requests", {},
                io.BytesIO(b'{"error":"rate_limit"}'))

        orig_urlopen = llm_router.urllib.request.urlopen
        llm_router.urllib.request.urlopen = _raise_429
        caught = None
        try:
            p.call("sys", [{"role": "user", "content": "u"}], timeout=5)
        except Exception as e:
            caught = e
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        self.assert_true(isinstance(caught, llm_router.RateLimitError),
                         "429 应抛专用 RateLimitError，实际 "
                         f"{type(caught).__name__}: {caught}")
        self.assert_eq(getattr(caught, "code", None), 429, "RateLimitError 应携带 429")

        # ── 2. 降级链 retry=1：429 provider 仅 1 次调用 ──────
        counts = {"bad": 0, "ok": 0}

        def _fake_urlopen(req, timeout=None, context=None):
            if "/v1-ok" in getattr(req, "full_url", ""):
                counts["ok"] += 1
                return _FakeResp(_ok_body("降级成功正文"))
            counts["bad"] += 1
            raise llm_router.urllib.error.HTTPError(
                getattr(req, "full_url", ""), 429, "Too Many Requests", {},
                io.BytesIO(b'{"error":"rate_limit"}'))

        bad = _make_api_provider("bad-429", "http://127.0.0.1:9/v1-bad", priority=1)
        ok = _make_api_provider("ok", "http://127.0.0.1:9/v1-ok", priority=2)
        router = _make_router([bad, ok], retry=1)
        records = []
        orig_record = llm_router._record_llm_call
        llm_router._record_llm_call = lambda name, **kw: records.append((name, kw))
        llm_router.urllib.request.urlopen = _fake_urlopen
        try:
            text, _usage, used = router.call_llm(
                "sys", [{"role": "user", "content": "u"}], timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen
            llm_router._record_llm_call = orig_record

        self.assert_eq(text, "降级成功正文", "429 后应降级成功")
        self.assert_eq(used, "ok", "实际使用的 provider 应为 ok")
        self.assert_eq(counts["bad"], 1,
                       f"retry=1 时 429 provider 应只调 1 次（不重试），实际 {counts['bad']} 次")
        self.assert_eq(counts["ok"], 1, f"成功 provider 应调 1 次，实际 {counts['ok']} 次")
        failed_rec = [r for r in records
                      if r[0] == "bad-429" and "429" in str(r[1].get("error", ""))]
        self.assert_eq(len(failed_rec), 1,
                       "429 失败应恰好记 1 条账本（不因重试重复记账）")

        # ── 3. 非 429 错误仍走重试（不回归） ─────────────────
        counts2 = {"bad": 0, "ok": 0}

        def _fake_urlopen_500(req, timeout=None, context=None):
            if "/v1-ok" in getattr(req, "full_url", ""):
                counts2["ok"] += 1
                return _FakeResp(_ok_body("500 后降级正文"))
            counts2["bad"] += 1
            raise llm_router.urllib.error.HTTPError(
                getattr(req, "full_url", ""), 500, "Server Error", {},
                io.BytesIO(b'{"error":"boom"}'))

        bad2 = _make_api_provider("bad-500", "http://127.0.0.1:9/v1-bad", priority=1)
        ok2 = _make_api_provider("ok", "http://127.0.0.1:9/v1-ok", priority=2)
        router2 = _make_router([bad2, ok2], retry=1)
        llm_router.urllib.request.urlopen = _fake_urlopen_500
        try:
            text2, _u2, used2 = router2.call_llm(
                "sys", [{"role": "user", "content": "u"}], timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        self.assert_eq(text2, "500 后降级正文", "500 后应降级成功")
        self.assert_eq(used2, "ok", "500 场景实际 provider 应为 ok")
        self.assert_eq(counts2["bad"], 2,
                       f"retry=1 时 500 provider 应调 2 次（保留原重试语义），"
                       f"实际 {counts2['bad']} 次")


if __name__ == "__main__":
    suite = LlmRouter429NoRetryTests()
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
