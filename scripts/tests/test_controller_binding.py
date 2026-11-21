#!/usr/bin/env python3
"""controller 方法绑定完整性守卫（v7.2.1）。

背景：v7.1.8 在 micro_scheduler.py 新增模块级函数 `_check_r1_start_failures`
并在 run_micro_scheduler 内以 `self._check_r1_start_failures()` 调用，但漏在
controller.py 导入并绑定为类属性——每次 tick 抛 AttributeError 被 except
静默吞掉（仅 DEBUG 日志），r1 启动失败检测自上线起从未生效（09-28 检查
周末产出时发现，logs 实证 08:30-09:30 每 15 分钟一条）。

本测试静态扫描 run_micro_scheduler / _focus_proposal_for_slot 等 micro_scheduler
入口函数体里的 `self._xxx(` 调用，逐一断言 LifecycleCronController 类上存在
同名属性，防再犯。

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_controller_binding.py
"""

import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


class ControllerBindingTests(TestSuite):
    def __init__(self):
        super().__init__("controller 方法绑定完整性守卫（v7.2.1）")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        import inspect
        from lifecycle import micro_scheduler as ms
        from lifecycle.controller import LifecycleCronController

        # 入口函数：cron 直接或间接调度的调度层函数
        entry_funcs = [
            "run_micro_scheduler",
            "_focus_proposal_for_slot",
            "_update_kanban",
            "_list_ready_jobs_for_proposal",
            "_refresh_stale_jobs",
        ]
        self_call_re = re.compile(r"self\.([A-Za-z_][A-Za-z0-9_]*)\s*\(")

        missing = []
        checked_calls = 0
        for fname in entry_funcs:
            fn = getattr(ms, fname, None)
            if fn is None:
                self.assert_true(False, f"micro_scheduler 应含入口 {fname}")
                continue
            src = inspect.getsource(fn)
            for m in self_call_re.finditer(src):
                attr = m.group(1)
                checked_calls += 1
                if not hasattr(LifecycleCronController, attr):
                    missing.append(f"{fname} → self.{attr}")

        self.assert_true(
            not missing,
            f"存在未绑定方法（controller.py 缺类属性）: {missing[:5]}；"
            f"已检查 {checked_calls} 处 self 调用",
        )

        # 回归锚点：v7.2.1 修复的具体绑定
        self.assert_true(
            hasattr(LifecycleCronController, "_check_r1_start_failures"),
            "v7.2.1: _check_r1_start_failures 必须绑定为 controller 方法",
        )


def main() -> None:
    suite = ControllerBindingTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"\n{'✓' if len(suite.results) - ok == 0 else '✗'} {suite.name}: {ok}/{len(suite.results)} 通过")
    for r in suite.results:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
