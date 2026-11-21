#!/usr/bin/env python3
"""
test_literature_no_dual_burn.py — literature_service 双烧降级直调删除回归（v7.3.86）

背景：hermes researcher 超时/失败后，旧方案B把同一份 ~29k 字符检索 prompt
全文经 llm_gateway 直调（落全局 minimax 链）——降级端无联网能力，只能凭
参数化知识硬答。11-16 账本实证两起双烧共 61.4k token、router 侧重发
32.4k 仅产出 171 字符，占当日 MiniMax 池可见消耗 38%。v7.3.86 删除两处
方案B：失败/超时直接返回空列表（_dispatch_researcher）或占位符
（_dispatch_deep_read），由上游按"无新论文/未执行"成功放行。

覆盖：
    1. hermes 失败 → _dispatch_researcher 返回 []，且 llm_complete 零调用
    2. hermes 失败 → _dispatch_deep_read 返回占位符，且 llm_complete 零调用
    3. hermes 成功路径不受影响（检索结果解析 / 深读原文返回）

注意：零真实子进程/网络调用（monkeypatch hermes_memory 与 llm_gateway）。
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


def _patch(targets):
    """批量替换模块属性，返回 (apply, restore)。targets: [(模块, 名, 假体)]"""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        saved = [(mod, name, getattr(mod, name, None)) for mod, name, _ in targets]
        for mod, name, fake in targets:
            setattr(mod, name, fake)
        try:
            yield
        finally:
            for mod, name, orig in saved:
                setattr(mod, name, orig)

    return _ctx()


class LiteratureNoDualBurnTests(TestSuite):
    def __init__(self):
        super().__init__("literature_service 双烧降级删除测试（v7.3.86）")

    def run_tests(self):
        import hermes_memory
        import llm_gateway
        from literature_service import LiteratureService

        svc = LiteratureService()
        calls = {"llm_complete": 0}

        def fake_llm_complete(*a, **kw):
            calls["llm_complete"] += 1
            return True, '[{"arxiv_id": "0000.0000"}]', None

        def fake_agent_fail(profile, prompt, timeout=300):
            return {"success": False, "output": "", "error": "hermes agent 超时（480s）"}

        # 1. _dispatch_researcher：hermes 失败 → 空列表，零直调
        with _patch([(hermes_memory, "_run_hermes_agent", fake_agent_fail),
                     (llm_gateway, "llm_complete", fake_llm_complete),
                     (llm_gateway, "is_llm_available", lambda: True)]):
            got = svc._dispatch_researcher("检索 prompt", source="pipeline")
        self.assert_true(
            got == [] and calls["llm_complete"] == 0,
            "hermes 失败后 _dispatch_researcher 返回空列表且零直调",
            f"got={got}, llm_complete 调用 {calls['llm_complete']} 次",
        )

        # 2. _dispatch_deep_read：hermes 失败 → 占位符，零直调
        calls["llm_complete"] = 0
        with _patch([(hermes_memory, "_run_hermes_agent", fake_agent_fail),
                     (llm_gateway, "llm_complete", fake_llm_complete),
                     (llm_gateway, "is_llm_available", lambda: True)]):
            got = svc._dispatch_deep_read("2501.12345")
        self.assert_true(
            "> 深度阅读未执行" in got and calls["llm_complete"] == 0,
            "hermes 失败后 _dispatch_deep_read 返回占位符且零直调",
            f"got={got!r}, llm_complete 调用 {calls['llm_complete']} 次",
        )

        # 3a. hermes 成功：检索结果可解析（正常路径不受影响）
        ok_output = "- 2403.15337 | 强场HHG探测量子材料 | 某某等 | 2024 | 0.9 | 摘要"
        fake_agent_ok = lambda profile, prompt, timeout=300: {
            "success": True, "output": ok_output, "error": ""}
        with _patch([(hermes_memory, "_run_hermes_agent", fake_agent_ok),
                     (llm_gateway, "llm_complete", fake_llm_complete),
                     (llm_gateway, "is_llm_available", lambda: True)]):
            got = svc._dispatch_researcher("检索 prompt", source="pipeline")
        self.assert_true(
            isinstance(got, list) and len(got) >= 1
            and got[0].get("arxiv_id") == "2403.15337",
            "hermes 成功路径检索结果解析不受影响",
            f"got={got}",
        )

        # 3b. hermes 成功：深读原文返回
        with _patch([(hermes_memory, "_run_hermes_agent", fake_agent_ok),
                     (llm_gateway, "llm_complete", fake_llm_complete),
                     (llm_gateway, "is_llm_available", lambda: True)]):
            got = svc._dispatch_deep_read("2501.12345")
        self.assert_true(
            got == ok_output,
            "hermes 成功路径深读原文返回不受影响",
            f"got={got!r}",
        )


if __name__ == "__main__":
    suite = LiteratureNoDualBurnTests()
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
