#!/usr/bin/env python3
"""
test_llm_router_think_only.py — llm_router「剥离 think 标签后为空」回归（v7.2.54）

背景：2026-10-28 12h 健康检查发现（BUG-21）——
`_call_api` 的空 content 判定（v6.10.9）发生在**剥离 think 标签之前**，
只覆盖「原始 content 为空」。推理型模型（MiniMax-M3 等）把 max_tokens
预算全部耗在 <think> 思考块、正文为空时，原始 content 非空 → 放行 →
`call()` 剥离后为空串 → provider 链视作成功、**不降级**，step_usage
账本记 success=True 而 output_chars=0。

运行时证据（step_usage 账本全库）：
  97 行 success=True 且 output_chars=0 且 prompt_chars>0，
  全部 provider=minimax、全部 completion_tokens=4096（= max_tokens 上限）；
  近 7 天 1060 条中占 72 条（6.8%），success_rate 虚高 6.70pp。
旁证（logs/linsai.log 10:04:06）：同秒出现
  「LLM 路由成功: provider=minimax (从 glm 降级/fallback)」与
  「LLM 返回空内容（provider=minimax）视为失败」
  → gateway 拦住了，但降级链未继续到 kimi/claude。

覆盖：
    1. API 路径 content 仅含 think 块 → provider.call() 抛 RuntimeError
    2. 模式 B 降级链：首个 provider think-only → 自动降级到下一个 provider
    3. 计量账本：失败 provider 记 success=False（不记成功）
    4. 正常内容（含 think 前缀 + 正文）→ 不回归，仍返回正文
    5. CLI 路径 think-only → 同样抛错（同样触发降级）

注意：零真实网络/子进程调用（urlopen 与 subprocess.run 均打桩）；
计量通过 monkeypatch `_record_llm_call` 在内存中捕获，不写盘
（step_usage.record_call 在测试上下文亦拒绝记账）。
"""

import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


THINK_ONLY = "<think>推理预算耗尽于此，正文为空</think>"
THINK_PLUS_BODY = "<think>先想一想</think>这是正文"


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
    """构造不含真实配置的 router 实例（绕过 __init__ 读取 .env/llm-config.json）。"""
    from llm_router import LLMRouter
    r = LLMRouter.__new__(LLMRouter)
    r.config = {"providers": [], "strategy": "priority", "timeout": 10, "retry": retry}
    r.providers = list(providers)
    r._round_robin_idx = 0
    r.force_provider = None
    r._last_used = None
    return r


class LlmRouterThinkOnlyTests(TestSuite):
    def __init__(self):
        super().__init__("llm_router think-only 空输出回归测试（v7.2.54）")

    def run_tests(self):
        import llm_router

        # ── 1. API 路径：think-only content → provider.call() 抛错 ──
        p = _make_api_provider("p-think", "http://127.0.0.1:9/v1-think")

        def _fake_urlopen(req, timeout=None, context=None):
            body = json.dumps({
                "choices": [{"message": {"content": THINK_ONLY},
                             "finish_reason": "length"}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 4096},
            }).encode("utf-8")
            return _FakeResp(body)

        orig_urlopen = llm_router.urllib.request.urlopen
        llm_router.urllib.request.urlopen = _fake_urlopen
        raised = False
        msg = ""
        try:
            p.call("sys", [{"role": "user", "content": "u"}], timeout=5)
        except RuntimeError as e:
            raised = True
            msg = str(e)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        self.assert_true(raised, "think-only 响应应抛 RuntimeError（触发 provider 降级）")
        self.assert_true("think" in msg, "错误信息应说明 think 标签剥离后为空",
                         f"msg={msg!r}")

        # ── 2. CLI 路径：think-only stdout → 同样抛错 ──────────
        cli_provider = llm_router.LLMProvider({
            "name": "kimi", "type": "cli", "priority": 1,
        })

        class _FakeCompleted:
            returncode = 0
            stdout = THINK_ONLY
            stderr = ""

        orig_run = llm_router.subprocess.run
        llm_router.subprocess.run = lambda *a, **k: _FakeCompleted()
        cli_raised = False
        try:
            cli_provider.call("sys", [{"role": "user", "content": "u"}], timeout=5)
        except RuntimeError:
            cli_raised = True
        finally:
            llm_router.subprocess.run = orig_run

        self.assert_true(cli_raised, "CLI 路径 think-only 响应同样应抛 RuntimeError")

        # ── 3. 降级链：首 provider think-only → 降级到下一个 ──
        p1 = _make_api_provider("p-think", "http://127.0.0.1:9/v1-think", priority=1)
        p2 = _make_api_provider("p-ok", "http://127.0.0.1:9/v1-ok", priority=2)

        def _fake_urlopen2(req, timeout=None, context=None):
            if "/v1-ok" in getattr(req, "full_url", ""):
                content = "降级后的正常正文"
            else:
                content = THINK_ONLY
            body = json.dumps({
                "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 32},
            }).encode("utf-8")
            return _FakeResp(body)

        router = _make_router([p1, p2])
        records = []
        orig_record = llm_router._record_llm_call
        llm_router._record_llm_call = lambda name, **kw: records.append((name, kw))
        llm_router.urllib.request.urlopen = _fake_urlopen2
        try:
            text, usage, provider_name = router.call_llm(
                "sys", [{"role": "user", "content": "u"}], timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen
            llm_router._record_llm_call = orig_record

        self.assert_eq(text, "降级后的正常正文", "think-only provider 应被跳过，返回下一个 provider 的正文")
        self.assert_eq(provider_name, "p-ok", "实际使用的 provider 应为 p-ok")
        # v7.3.81: 首次 think-only 就地升预算重试一次（打桩恒返 think-only，
        # 升预算后仍空）→ 切下一 provider；p1 共调 2 次、failure_count=2
        self.assert_eq(p1.failure_count, 2,
                       "think-only provider 应记 2 次失败（首次 + 升预算重试仍空）")

        # ── 4. 计量账本：失败 provider 记 success=False ───────
        failed_rec = [r for r in records
                      if r[0] == "p-think" and r[1].get("success") is False]
        self.assert_true(len(failed_rec) >= 1, "think-only provider 应在账本记 success=False")
        ok_rec = [r for r in records
                  if r[0] == "p-ok" and r[1].get("success") is True]
        self.assert_true(len(ok_rec) >= 1, "成功 provider 应在账本记 success=True")
        zero_out = [r for r in records
                    if r[1].get("success") is True and r[1].get("output_chars") == 0]
        self.assert_eq(len(zero_out), 0,
                       "不应再出现 success=True 且 output_chars=0 的记账")

        # ── 5. 正常内容（含 think 前缀）不回归 ────────────────
        p_ok = _make_api_provider("p-body", "http://127.0.0.1:9/v1-body")

        def _fake_urlopen3(req, timeout=None, context=None):
            body = json.dumps({
                "choices": [{"message": {"content": THINK_PLUS_BODY},
                             "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            }).encode("utf-8")
            return _FakeResp(body)

        llm_router.urllib.request.urlopen = _fake_urlopen3
        try:
            text2, _usage2 = p_ok.call("sys", [{"role": "user", "content": "u"}], timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        self.assert_eq(text2, "这是正文", "含 think 前缀的正常内容应剥离后返回正文")

        # ── 6. 全部 provider think-only → 整体失败 ───────────
        q1 = _make_api_provider("q-think", "http://127.0.0.1:9/v1-think", priority=1)
        router2 = _make_router([q1])
        all_raised = False
        llm_router.urllib.request.urlopen = _fake_urlopen
        try:
            router2.call_llm("sys", [{"role": "user", "content": "u"}], timeout=5)
        except RuntimeError:
            all_raised = True
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        self.assert_true(all_raised, "全部 provider think-only 时应整体失败而非返回空串")

        # ── 7.（v7.3.81 修订）think-only 首次就地升预算重试一次 ────
        # v7.2.55 语义（同预算直接 break）已被 v7.3.81 修订：账本全库
        # 214 次回溯证明 think-only 全部是预算型（completion_tokens 恰
        # 为 4096），首次失败就地升 max_tokens 重试一次（不消耗 retry
        # 额度）；打桩恒返 think-only 时升预算重试仍空 → break 切下一
        # provider。think provider 恰好 2 次调用（首次 + 升预算重试）。
        call_counts = {"think": 0, "ok": 0}

        def _fake_urlopen_count(req, timeout=None, context=None):
            if "/v1-ok" in getattr(req, "full_url", ""):
                call_counts["ok"] += 1
                content = "计数正常正文"
            else:
                call_counts["think"] += 1
                content = THINK_ONLY
            body = json.dumps({
                "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 32},
            }).encode("utf-8")
            return _FakeResp(body)

        c1 = _make_api_provider("c-think", "http://127.0.0.1:9/v1-think", priority=1)
        c2 = _make_api_provider("c-ok", "http://127.0.0.1:9/v1-ok", priority=2)
        router3 = _make_router([c1, c2], retry=1)
        llm_router.urllib.request.urlopen = _fake_urlopen_count
        try:
            text3, _, used3 = router3.call_llm(
                "sys", [{"role": "user", "content": "u"}], timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        self.assert_eq(text3, "计数正常正文", "v7.3.81 场景下降级应成功")
        self.assert_eq(call_counts["think"], 2,
                       "think-only provider 应恰被调 2 次（首次 + 升预算重试，"
                       "不消耗 retry 额度），"
                       f"实际 {call_counts['think']} 次")
        self.assert_eq(call_counts["ok"], 1,
                       f"成功 provider 应只被调 1 次，实际 {call_counts['ok']} 次")

        # ── 8.（v7.2.55）ThinkOnlyResponseError 携带 usage ──
        p_usage = _make_api_provider("u-think", "http://127.0.0.1:9/v1-think")
        llm_router.urllib.request.urlopen = _fake_urlopen
        carried = {}
        try:
            p_usage.call("sys", [{"role": "user", "content": "u"}], timeout=5)
        except llm_router.ThinkOnlyResponseError as e:
            carried = e.usage or {}
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        self.assert_eq(carried.get("completion_tokens"), 4096,
                       "专用异常应携带本次实际消耗的 usage（token 可见）")

        # ── 9.（v7.3.81）升预算救活：同 provider 返回正文，不降级 ──
        # 打桩按请求 payload 里的 max_tokens 区分行为：默认 4096 时返
        # think-only（模拟思考 token 打满预算），升到 16384 后返正常正文
        # （思考有了空间、正文放得下）。断言：c-think 自身救活成功，
        # 降级候选 c-ok 零调用；第二次请求的 max_tokens 确为 16384。
        rescue_counts = {"think": 0, "ok": 0}
        bumped_tokens_seen = []

        def _fake_urlopen_rescue(req, timeout=None, context=None):
            if "/v1-ok" in getattr(req, "full_url", ""):
                rescue_counts["ok"] += 1
                content = "不应走到降级"
            else:
                rescue_counts["think"] += 1
                payload = json.loads(req.data.decode("utf-8"))
                bumped_tokens_seen.append(payload.get("max_tokens"))
                if (payload.get("max_tokens") or 0) > 4096:
                    content = "升预算后的正常正文"
                else:
                    content = THINK_ONLY
            body = json.dumps({
                "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 32},
            }).encode("utf-8")
            return _FakeResp(body)

        r1 = _make_api_provider("c-think", "http://127.0.0.1:9/v1-think", priority=1)
        r2 = _make_api_provider("c-ok", "http://127.0.0.1:9/v1-ok", priority=2)
        router4 = _make_router([r1, r2], retry=1)
        llm_router.urllib.request.urlopen = _fake_urlopen_rescue
        try:
            text4, _u4, used4 = router4.call_llm(
                "sys", [{"role": "user", "content": "u"}], timeout=5)
        finally:
            llm_router.urllib.request.urlopen = orig_urlopen

        self.assert_eq(text4, "升预算后的正常正文",
                       "升预算重试应救活同 provider，返回其正文")
        self.assert_eq(used4, "c-think",
                       "救活后不应降级到下一 provider")
        self.assert_eq(rescue_counts["ok"], 0,
                       f"降级候选应零调用，实际 {rescue_counts['ok']} 次")
        self.assert_eq(rescue_counts["think"], 2,
                       "think provider 应恰被调 2 次（首次 4096 + 升预算重试），"
                       f"实际 {rescue_counts['think']} 次")
        self.assert_eq(bumped_tokens_seen[-1], 16384,
                       f"升预算重试的 max_tokens 应为 16384 起步，"
                       f"实际 {bumped_tokens_seen[-1]}")


if __name__ == "__main__":
    suite = LlmRouterThinkOnlyTests()
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
