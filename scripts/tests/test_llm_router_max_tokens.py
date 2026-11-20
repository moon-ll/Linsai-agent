#!/usr/bin/env python3
"""
test_llm_router_max_tokens.py — llm_router API 路径 max_tokens 传递回归（v6.9.79）

背景：2026-08-29 16:35 BJ output_extract_daily_knowledge 补跑时暴露——
LLMProvider.call() 收下 max_tokens 参数却不传给 _call_api，而 _call_api
内部 payload 构造引用 `max_tokens or 4096`（未定义名），API 类型
provider（minimax 等）每次调用必抛 NameError("name 'max_tokens' is
not defined")，主链只能靠 CLI 降级兜底（CLI 不可用时整链失败）。

覆盖：
    1. _call_api 不再抛 NameError（连接类异常为合法失败形态）
    2. _call_api 显式 max_tokens 路径
    3. call() → _call_api 传递路径（默认 None）

注意：零真实网络调用（base_url 指向不可达回环端口，预期 URLError）。
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


def _make_api_provider():
    from llm_router import LLMProvider
    return LLMProvider({
        "name": "fake-api",
        "type": "api",
        "priority": 1,
        "base_url": "http://127.0.0.1:9",  # discard 端口，连接必失败
        "api_key": "test-key",
        "model": "test-model",
    })


class LlmRouterMaxTokensTests(TestSuite):
    def __init__(self):
        super().__init__("llm_router API 路径 max_tokens 传递测试（v6.9.79）")

    def run_tests(self):
        messages = [{"role": "user", "content": "hello"}]

        # 1. 默认路径：不再 NameError，失败形态应为连接类异常
        p = _make_api_provider()
        err = ""
        try:
            p._call_api("sys", messages, timeout=3)
        except NameError as e:
            err = f"NameError: {e}"
        except Exception as e:
            err = f"{type(e).__name__}"
        self.assert_true(
            "NameError" not in err,
            "_call_api 默认路径不再抛 NameError",
            f"err={err}",
        )

        # 2. 显式 max_tokens 路径
        p2 = _make_api_provider()
        err2 = ""
        try:
            p2._call_api("sys", messages, timeout=3, max_tokens=128)
        except NameError as e:
            err2 = f"NameError: {e}"
        except Exception as e:
            err2 = f"{type(e).__name__}"
        self.assert_true(
            "NameError" not in err2,
            "_call_api 显式 max_tokens 不抛 NameError",
            f"err={err2}",
        )

        # 3. call() 传递路径（type=api → _call_api）
        p3 = _make_api_provider()
        err3 = ""
        try:
            p3.call("sys", messages, timeout=3)
        except NameError as e:
            err3 = f"NameError: {e}"
        except Exception as e:
            err3 = f"{type(e).__name__}"
        self.assert_true(
            "NameError" not in err3,
            "call() 经 _call_api 路径不抛 NameError",
            f"err={err3}",
        )

        # 4. call() 显式 max_tokens（模式 A 强制路径同型）
        p4 = _make_api_provider()
        err4 = ""
        try:
            p4.call("sys", messages, timeout=3, max_tokens=256)
        except NameError as e:
            err4 = f"NameError: {e}"
        except Exception as e:
            err4 = f"{type(e).__name__}"
        self.assert_true(
            "NameError" not in err4,
            "call() 显式 max_tokens 不抛 NameError",
            f"err={err4}",
        )


if __name__ == "__main__":
    suite = LlmRouterMaxTokensTests()
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
