#!/usr/bin/env python3
"""
test_gap_identify_write_memory_unbound.py — v7.2.2 UnboundLocalError 回归测试

背景：2026-09-27 20:00:22Z mos2 r1-rationale-gap_identify 抛
"UnboundLocalError: cannot access local variable '_write_memory' where it
is not associated with a value"。根因：executor.py 函数内 `from
hermes_memory import _write_memory` 让符号被标记为局部变量；当 raw_text
非空（直接调用成功）跳过导入分支后，except 块引用 `_write_memory` 即
触发 UnboundLocalError。

修复：v7.2.2 把 `from hermes_memory import _run_hermes_agent, _write_memory`
提升至模块级 try/except（与 llm_router / adversarial_governance 守卫风格
一致），并删除 4 处函数内 import。

验证矩阵（5 断言）：
    1. 模块级 `_write_memory` 与 hermes_memory._write_memory 同对象
    2. 模块级 `_run_hermes_agent` 与 hermes_memory._run_hermes_agent 同对象
    3. executor.py 内仅 1 处模块级 hermes_memory import
    4. _run_gap_identify_step / _run_lit_search_step / _run_lit_read_step /
       _run_lit_note_step 内无函数内 import
    5. fail-open 守卫：缺失模块导入回退为 None

用法示例：
    python3 scripts/tests/test_gap_identify_write_memory_unbound.py
"""

import re
import sys
from pathlib import Path

from test_runner import TestSuite, create_isolated_env


class GapIdentifyWriteMemoryUnboundTests(TestSuite):
    def __init__(self):
        super().__init__("v7.2.2 _write_memory UnboundLocalError 回归测试")

    def setup(self):
        create_isolated_env()

    def teardown(self):
        pass

    def run_tests(self):
        # ---------- 1. 模块级 _write_memory 与 hermes_memory._write_memory 同对象 ----------
        from lifecycle import executor as exec_mod
        from hermes_memory import _write_memory as ref_write_memory

        self.assert_true(
            exec_mod._write_memory is not None,
            "模块级 _write_memory 可用",
            "模块级 _write_memory 应当可用（导入守卫未生效）",
        )
        self.assert_true(
            exec_mod._write_memory is ref_write_memory,
            "模块级 _write_memory 与 hermes_memory._write_memory 同对象",
            "模块级 _write_memory 应与 hermes_memory._write_memory 同对象",
        )

        # ---------- 2. 模块级 _run_hermes_agent 与 hermes_memory._run_hermes_agent 同对象 ----------
        from hermes_memory import _run_hermes_agent as ref_run_agent
        self.assert_true(
            exec_mod._run_hermes_agent is ref_run_agent,
            "模块级 _run_hermes_agent 与 hermes_memory._run_hermes_agent 同对象",
            "模块级 _run_hermes_agent 应与 hermes_memory._run_hermes_agent 同对象",
        )

        # ---------- 3. executor.py 内仅 1 处模块级 hermes_memory import ----------
        executor_path = Path(exec_mod.__file__)
        source = executor_path.read_text(encoding="utf-8")
        pattern = re.compile(r"^\s*from hermes_memory import ", re.MULTILINE)
        matches = pattern.findall(source)
        self.assert_eq(
            len(matches), 1,
            "executor.py 内仅保留 1 处模块级 hermes_memory import",
            f"实际 {len(matches)} 处",
        )

        # ---------- 4. 各 step 函数内无函数内 import ----------
        all_clear = True
        details = []
        for fn_name in (
            "_run_gap_identify_step",
            "_run_lit_search_step",
            "_run_lit_read_step",
            "_run_lit_note_step",
        ):
            m = re.search(
                rf"def {fn_name}\(.*?(?=^def |\Z)",
                source,
                re.DOTALL | re.MULTILINE,
            )
            if not m:
                details.append(f"{fn_name}: 未找到函数体")
                all_clear = False
                continue
            if "from hermes_memory import" in m.group(0):
                details.append(f"{fn_name}: 仍含函数内 import")
                all_clear = False
        self.assert_true(
            all_clear,
            "step 函数体内无函数内 import",
            " | ".join(details),
        )

        # ---------- 5. fail-open 守卫：缺失模块导入回退为 None ----------
        try:
            from hermes_memory_does_not_exist import _write_memory as _bad
        except Exception:
            _bad = None  # type: ignore[misc,assignment]
        self.assert_true(
            _bad is None,
            "缺失模块导入回退为 None（fail-open 守卫生效）",
            "守卫未生效",
        )


def main() -> None:
    suite = GapIdentifyWriteMemoryUnboundTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()