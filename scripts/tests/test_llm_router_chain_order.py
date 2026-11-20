#!/usr/bin/env python3
"""
test_llm_router_chain_order.py — llm_router 降级链治理回归（v7.3.80）

背景（近 7 天 step_usage 账本实证，2026-11-11 token 消耗分析）：
  - 总消耗 6.03M tokens/7 天，其中失败重试白烧 1.28M（21%）；
  - `_apply_task_preference` 首个偏好命中即 return，panel 声明
    ("kimi","claude","glm") 实际链序 kimi → minimax → minimax-fallback
    → claude，claude/glm 提升被吞；
  - kimi CLI 对 panel 尺寸 prompt（50k+ 字符）14/15 超时且成对出现
    （retry=1 重试重演），每轮白等 2×PANEL_TIMEOUT；
  - minimax（M3）panel 尺寸 think-only 12/12，成功调用 prompt 尺寸
    p99=27k 字符、≥40k 字符仅 7 次成功——大 prompt 全价烧完才降级。

覆盖：
    1. 多偏好全部提前（修复后语义）：声明顺序整体置顶，其余稳定
    2. panel 排除清单：kimi 被摘出候选链（零调用），claude 首选生效
    3. 大 prompt 守卫：≥40k 字符跳过 minimax 用下一家并记账；小 prompt
       不受影响；末位不跳（无候选时仍尝试）
    4. 超时不重试：CLI 超时（retry=1）同 provider 只调 1 次即降级

注意：零真实网络/子进程调用（urlopen / subprocess.run / shutil.which
均打桩）；计量通过 monkeypatch `_record_llm_call` 内存捕获，不写盘。
"""

import json
import subprocess
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


class _FakeResp:
    """模拟 urllib 响应对象（支持上下文管理器协议）。"""

    def __init__(self, payload: bytes):
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _api(name: str, priority: int):
    from llm_router import LLMProvider
    return LLMProvider({"name": name, "type": "api", "priority": priority,
                        "base_url": f"http://127.0.0.1:9/{name}",
                        "api_key": "test-key", "model": "test-model"})


def _cli(name: str, priority: int):
    from llm_router import LLMProvider
    return LLMProvider({"name": name, "type": "cli", "priority": priority})


def _make_router(providers, retry: int = 0):
    """构造不含真实配置的 router 实例（绕过 __init__ 读取 .env/llm-config.json）。"""
    from llm_router import LLMRouter
    r = LLMRouter.__new__(LLMRouter)
    r.config = {"providers": [], "strategy": "priority", "timeout": 10, "retry": retry}
    r.providers = list(providers)
    r._round_robin_idx = 0
    r.force_provider = None
    r._last_used = None
    return r


def _api_ok(payload_content: str):
    """构造恒定成功响应的 urlopen 打桩。"""
    def _fake(req, timeout=None, context=None):
        body = json.dumps({
            "choices": [{"message": {"content": payload_content},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }).encode("utf-8")
        return _FakeResp(body)
    return _fake


class LlmRouterChainOrderTests(TestSuite):
    def __init__(self):
        super().__init__("llm_router 降级链治理回归测试（v7.3.80）")

    def run_tests(self):
        import llm_router

        # ── 1. 多偏好全部提前（_apply_task_preference 修复）──────────
        chain = [_api("minimax", 1), _api("minimax-fallback", 2),
                 _api("glm", 3), _cli("kimi", 1), _cli("claude", 2)]
        ordered = llm_router._apply_task_preference(list(chain), "panel")
        self.assert_eq(
            [p.name for p in ordered],
            ["claude", "minimax-fallback", "glm", "minimax", "kimi"],
            "panel 偏好 (claude, minimax-fallback, glm) 应按声明顺序全部提前，"
            "其余保持全局相对顺序",
        )
        # 偏好全不在链中 → 原样返回
        self.assert_eq(
            [p.name for p in llm_router._apply_task_preference(list(chain), "governance-x")],
            [p.name for p in chain],
            "未注册标签不应改变顺序",
        )

        # ── 2. panel 排除清单：kimi 摘出，claude 首选命中 ────────────
        which_hits = []
        orig_which = llm_router.shutil.which
        llm_router.shutil.which = lambda name: which_hits.append(name) or name in ("kimi", "claude")

        subprocess_calls = []

        class _FakeCompleted:
            returncode = 0
            stdout = "panel 评审正文（claude CLI）"
            stderr = ""

        def _fake_run(*args, **kwargs):
            cmd = args[0] if args else kwargs.get("args", [])
            subprocess_calls.append(list(cmd))
            return _FakeCompleted()

        orig_run = llm_router.subprocess.run
        llm_router.subprocess.run = _fake_run

        records = []
        orig_record = llm_router._record_llm_call
        llm_router._record_llm_call = lambda name, **kw: records.append((name, kw))

        router = _make_router([_api("minimax", 1), _cli("kimi", 1),
                               _cli("claude", 2), _api("minimax-fallback", 2),
                               _api("glm", 3)])
        try:
            text, _u, used = router.call_llm(
                "sys", [{"role": "user", "content": "u"}],
                timeout=5, prefer="panel")
        finally:
            llm_router.subprocess.run = orig_run
            llm_router.shutil.which = orig_which
            llm_router._record_llm_call = orig_record

        self.assert_eq(used, "claude", "panel 首选应为 claude（排除 kimi 后偏好队首）")
        self.assert_true("claude" in " ".join(subprocess_calls[0]) if subprocess_calls else False,
                         "应调用 claude CLI")
        self.assert_true(
            all("kimi" not in cmd for cmd in subprocess_calls),
            f"kimi 应被排除清单摘出零调用，实际调用 {subprocess_calls}",
        )

        # ── 3a. 大 prompt 守卫：minimax 被跳过，glm 接管并记账 ───────
        big_user = "字" * 45000  # ≥ THINK_ONLY_PRONE_MIN_CHARS(40000)
        records2 = []
        llm_router._record_llm_call = lambda name, **kw: records2.append((name, kw))
        orig_urlopen = llm_router.urllib.request.urlopen
        llm_router.urllib.request.urlopen = _api_ok("大 prompt 由 glm 接管")
        router2 = _make_router([_api("minimax", 1), _api("glm", 2)])
        try:
            text2, _u2, used2 = router2.call_llm(
                "sys", [{"role": "user", "content": big_user}], timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen
            llm_router._record_llm_call = orig_record

        self.assert_eq(used2, "glm", "≥40k 字符 prompt 应跳过 minimax 用 glm")
        self.assert_eq(text2, "大 prompt 由 glm 接管", "守卫生效时应返回后续 provider 正文")
        skip_rec = [kw for n, kw in records2
                    if n == "minimax" and "skip" in (kw.get("error") or "")]
        self.assert_true(len(skip_rec) >= 1,
                         "被守卫跳过的 provider 应在账本记 skip 标记")

        # ── 3b. 小 prompt 不受守卫影响 ────────────────────────────────
        records3 = []
        llm_router._record_llm_call = lambda name, **kw: records3.append((name, kw))
        llm_router.urllib.request.urlopen = _api_ok("小 prompt minimax 正常")
        router3 = _make_router([_api("minimax", 1), _api("glm", 2)])
        try:
            _t3, _u3, used3 = router3.call_llm(
                "sys", [{"role": "user", "content": "u"}], timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen
            llm_router._record_llm_call = orig_record

        self.assert_eq(used3, "minimax", "小 prompt 应照常走 minimax 主模型")

        # ── 3c. 末位不跳：仅剩 minimax 可用时仍尝试 ──────────────────
        llm_router.urllib.request.urlopen = _api_ok("末位 minimax 兜底")
        router4 = _make_router([_api("minimax", 1)])
        try:
            _t4, _u4, used4 = router4.call_llm(
                "sys", [{"role": "user", "content": big_user}], timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        self.assert_eq(used4, "minimax",
                       "无后续候选时守卫不应跳过末位 provider（有尝试总比失败强）")

        # ── 4. 超时不重试：CLI 超时（retry=1）只调 1 次即降级 ─────────
        timeout_calls = []

        def _fake_run_timeout(*args, **kwargs):
            timeout_calls.append(1)
            raise subprocess.TimeoutExpired(cmd="kimi", timeout=5)

        llm_router.shutil.which = lambda name: name in ("kimi",)
        llm_router.subprocess.run = _fake_run_timeout
        records5 = []
        llm_router._record_llm_call = lambda name, **kw: records5.append((name, kw))
        llm_router.urllib.request.urlopen = _api_ok("超时后 glm 接管")
        router5 = _make_router([_cli("kimi", 1), _api("glm", 2)], retry=1)
        try:
            _t5, _u5, used5 = router5.call_llm(
                "sys", [{"role": "user", "content": "u"}], timeout=5)
        finally:
            llm_router.subprocess.run = orig_run
            llm_router.shutil.which = orig_which
            llm_router.urllib.request.urlopen = orig_urlopen
            llm_router._record_llm_call = orig_record

        self.assert_eq(used5, "glm", "CLI 超时后应降级到下一 provider")
        self.assert_eq(len(timeout_calls), 1,
                       f"超时 provider 不应重试（v7.3.80），实际调 {len(timeout_calls)} 次")


if __name__ == "__main__":
    suite = LlmRouterChainOrderTests()
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
