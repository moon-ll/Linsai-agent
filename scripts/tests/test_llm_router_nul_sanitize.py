#!/usr/bin/env python3
"""
test_llm_router_nul_sanitize.py — llm_router 输入 NUL 字节净化回归（v6.9.80）

背景：2026-08-29 知识库存量重构（/tmp/rebuild_kb.sh）运行期暴露——
raw 论文正文偶含 \x00（PDF 抽取残留，当日实测 6 篇，如
2021-2111.08669-high-harmonic-generation-in-solids 等）。持有旧版
llm_router 的进程 API 路径 NameError 全灭后，CLI 降级链全部抛
ValueError("embedded null byte")（subprocess 参数不允许 NUL），
7 provider 全灭、该篇蒸馏终态失败。

覆盖：
    1. CLI 路径（kimi）：含 \x00 的 prompt 经 call() 后 subprocess
       参数不再含 NUL，且不再抛 ValueError
    2. API 路径：JSON 载荷中 messages content 无 \x00（也无 \u0000 转义）
    3. 干净输入零改写：无 \x00 时 system_prompt/messages 原样传递（不重建）

注意：零真实子进程/网络调用（subprocess.run 与 urlopen 均打桩）。
"""

import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


class _FakeCompleted:
    def __init__(self, stdout: str = "mock-answer"):
        self.returncode = 0
        self.stdout = stdout
        self.stderr = ""


class _FakeResp:
    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class LlmRouterNulSanitizeTests(TestSuite):
    def __init__(self):
        super().__init__("llm_router 输入 NUL 字节净化测试（v6.9.80）")

    def run_tests(self):
        import llm_router

        # ------------------------------------------------------------------
        # 1. CLI 路径：kimi provider + 打桩 subprocess.run
        # ------------------------------------------------------------------
        provider = llm_router.LLMProvider({
            "name": "kimi",
            "type": "cli",
            "priority": 1,
        })
        captured = {}

        def _fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["kwargs"] = kwargs
            return _FakeCompleted()

        orig_run = llm_router.subprocess.run
        llm_router.subprocess.run = _fake_run
        try:
            dirty_msgs = [{"role": "user", "content": "论文正文\x00含 NUL\x00字节"}]
            text, usage = provider.call("系统提示\x00", dirty_msgs, timeout=5)
        finally:
            llm_router.subprocess.run = orig_run

        self.assert_true(
            text == "mock-answer",
            "CLI 路径净化后调用成功返回",
            f"text={text!r}",
        )
        self.assert_true(
            usage is None,
            "CLI 路径 usage 为 None",
            f"usage={usage!r}",
        )
        joined_args = " ".join(str(a) for a in captured.get("cmd", []))
        self.assert_true(
            "\x00" not in joined_args,
            "CLI subprocess 参数不含 NUL 字节",
            f"args 片段={joined_args[:80]!r}",
        )
        self.assert_true(
            "含 NUL" in joined_args,
            "净化仅移除 NUL，正文其余内容保留",
            f"args 片段={joined_args[:80]!r}",
        )

        # ------------------------------------------------------------------
        # 2. API 路径：打桩 urlopen，校验 JSON 载荷
        # ------------------------------------------------------------------
        api_provider = llm_router.LLMProvider({
            "name": "fake-api",
            "type": "api",
            "priority": 1,
            "base_url": "http://127.0.0.1:9",
            "api_key": "test-key",
            "model": "test-model",
        })
        api_payload = {}

        def _fake_urlopen(req, timeout=None, context=None):
            api_payload["data"] = req.data
            body = json.dumps({
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 1},
            }).encode("utf-8")
            return _FakeResp(body)

        orig_urlopen = llm_router.urllib.request.urlopen
        llm_router.urllib.request.urlopen = _fake_urlopen
        try:
            dirty_msgs = [{"role": "user", "content": "abstract\x00with nul"}]
            api_text, api_usage = api_provider.call("sys", dirty_msgs, timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        payload_str = api_payload.get("data", b"").decode("utf-8", errors="replace")
        self.assert_true(
            "\u0000" not in payload_str and "\x00" not in payload_str,
            "API JSON 载荷无 NUL（含 \\u0000 转义）",
            f"payload 片段={payload_str[:120]!r}",
        )
        self.assert_true(
            api_usage is not None,
            "API 路径 usage 正常返回",
            f"usage={api_usage!r}",
        )

        # ------------------------------------------------------------------
        # 3. 干净输入零改写：无 NUL 时 messages 对象身份不变（不重建列表）
        # ------------------------------------------------------------------
        clean_provider = llm_router.LLMProvider({
            "name": "kimi",
            "type": "cli",
            "priority": 1,
        })
        seen = {}

        def _fake_run_clean(cmd, **kwargs):
            seen["prompt"] = " ".join(str(a) for a in cmd)
            return _FakeCompleted()

        llm_router.subprocess.run = _fake_run_clean
        try:
            clean_msgs = [{"role": "user", "content": "clean text"}]
            clean_provider.call("clean sys", clean_msgs, timeout=5)
        finally:
            llm_router.subprocess.run = orig_run

        self.assert_true(
            "clean sys" in seen.get("prompt", "") and "clean text" in seen.get("prompt", ""),
            "干净输入原样传递（快速路径零改写）",
            f"prompt={seen.get('prompt', '')[:80]!r}",
        )


if __name__ == "__main__":
    suite = LlmRouterNulSanitizeTests()
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
