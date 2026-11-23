#!/usr/bin/env python3
"""
test_governance_routing.py — v7.3.86 token 治理路由回归

背景：v7.3.82（11-15）停用 kimi 后，无 prefer 标签的直调全部落全局
minimax 链（M3 链首）。v7.3.86 治理：① 补注册 weekend_output → glm-first
（TASK_MAX_TOKENS 早已有预算、偏好漏注册的纯遗漏）；② 机械/判断类无标签
直调补 prefer="governance"（glm-first）；③ step_usage/llm_router 增 note
观测字段（think_only_retry 取证，不改行为）。

覆盖：
    1. TASK_PROVIDER_PREFS 含 weekend_output 且链序 (glm, glm-fallback)
    2. weekend_output 不并入 TASKS_DISABLE_THINKING（长文生成不关思考）
    3. 六处机械/判断类调用点静态守卫（prefer="governance" 在位）
    4. note 观测字段链路（record_call/_record_llm_call 签名 + 重试记账点）

说明：第 3 项为源码静态断言（调用方模块 import 重、函数依赖会话/页面
状态，行为级 mock 成本高；标签属声明式配置，静态守卫即可防回归）。
"""

import inspect
import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite

_PROJECT_ROOT = _SCRIPTS_DIR.parent

# 六处补标签调用点：(文件, 在位锚文本)
_GOVERNANCE_SITES = [
    ("scripts/chat_archive.py", "只输出关键词列表"),
    ("scripts/kb_merger.py", "知识库蒸馏器"),
    ("scripts/web_routes_system.py", "整理审核意见"),
    ("scripts/web_routes_tasks.py", "router.call_llm(sys_prompt"),
    ("scripts/lifecycle/executor.py", "只输出合法 JSON"),
]


class GovernanceRoutingTests(TestSuite):
    def __init__(self):
        super().__init__("v7.3.86 token 治理路由测试")

    def run_tests(self):
        from llm_router import TASK_PROVIDER_PREFS, TASKS_DISABLE_THINKING

        # 1. weekend_output 注册与链序
        self.assert_true(
            TASK_PROVIDER_PREFS.get("weekend_output") == ("glm", "glm-fallback"),
            "weekend_output 注册 glm-first 且链序 (glm, glm-fallback)",
            f"实际: {TASK_PROVIDER_PREFS.get('weekend_output')}",
        )

        # 2. 不关思考（裁决②：长文生成类）
        self.assert_true(
            "weekend_output" not in TASKS_DISABLE_THINKING,
            "weekend_output 不并入 TASKS_DISABLE_THINKING",
            f"实际 TASKS_DISABLE_THINKING={TASKS_DISABLE_THINKING}",
        )

        # 3. 六处调用点 prefer="governance" 静态守卫
        for rel, anchor in _GOVERNANCE_SITES:
            text = (_PROJECT_ROOT / rel).read_text(encoding="utf-8")
            # 取锚点后 600 字符窗口，断言窗口内带 prefer="governance"
            idx = text.find(anchor)
            ok = idx >= 0 and 'prefer="governance"' in text[idx:idx + 600]
            self.assert_true(
                ok, f"{rel} 调用点 prefer=governance 在位",
                f"anchor={anchor!r}, 找到={idx >= 0}",
            )

        # 4. note 观测字段链路
        import step_usage
        import llm_router
        sig_su = inspect.signature(step_usage.record_call).parameters
        sig_lr = inspect.signature(llm_router._record_llm_call).parameters
        self.assert_true(
            "note" in sig_su and "note" in sig_lr,
            "record_call/_record_llm_call 均支持 note 参数",
            f"step_usage: {list(sig_su)}; llm_router: {list(sig_lr)}",
        )
        router_src = (_SCRIPTS_DIR / "llm_router.py").read_text(encoding="utf-8")
        self.assert_true(
            'note=f"think_only_retry:{effective_max_tokens}"' in router_src,
            "think-only 升预算重试记账带 note=think_only_retry:<预算>",
            "llm_router.py 未找到 note=f\"think_only_retry:...\" 记账点",
        )


if __name__ == "__main__":
    suite = GovernanceRoutingTests()
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
