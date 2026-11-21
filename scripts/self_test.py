#!/usr/bin/env python3
"""
self_test.py — LinSai-CoPilot 内测统一入口

用途：
    作为"影子用户"自动化内测系统，替代真实用户完成项目上线前的
    全量回归测试。覆盖模块功能、场景剧本、人格一致性三大维度。

用法（命令行）：
    $ python3 scripts/self_test.py              # 运行全量测试（不含 Web API）
    $ python3 scripts/self_test.py --module     # 仅运行核心模块测试
    $ python3 scripts/self_test.py --scenario   # 仅运行场景剧本
    $ python3 scripts/self_test.py --persona    # 仅运行人格抽检
    $ python3 scripts/self_test.py --web        # 仅运行 Web API 测试
    $ python3 scripts/self_test.py --web-ci     # 全量回归 + Web API（CI 环境）
    $ python3 scripts/self_test.py --verbose    # 显示详细通过信息

用法（程序化）：
    >>> from self_test import run_tests
    >>> result = run_tests()              # 全量（不含 Web API）
    >>> result = run_tests(["module"])    # 仅核心模块
    >>> result = run_tests(web_ci=True)   # 全量 + Web API（CI 模式）
    >>> print(result["summary"])          # 结构化结果

规范：
    - 仅使用 Python 3 标准库
    - 测试隔离：所有写入操作在临时目录进行，不污染真实数据
    - 退出码：0 = 全量通过，1 = 存在失败
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# 确保 scripts/ 在路径中
_SCRIPTS_DIR = Path(__file__).parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# 确保 tests/ 子包可导入
_TESTS_DIR = _SCRIPTS_DIR / "tests"
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

import test_runner
from test_runner import TestSuite


def _run_selected(filters: List[str]) -> List[TestSuite]:
    """根据过滤器运行指定测试套件，返回套件列表。"""
    import importlib
    import os as _os
    # v6.9.57：module/scenario 等多套件有序运行同样存在跨套件模块污染
    # （实测 --module 顺序下 kb_sync 写穿真实 knowledge/），与 --web-ci
    # 一致标记 ORDERED_FULL——顺序敏感套件仅单跑（干净环境）完整执行
    if len(filters) > 1 or filters != ["web"]:
        _os.environ["LINSAI_TEST_ORDERED_FULL"] = "1"

    suites = []
    # v7.2.25 修：旧版维护一份手工"module"白名单 80+ 个测试模块名，新
    # 增的 test_acceptance_line_promotion 等 14 个测试从未被纳入，导致
    # "self_test --module" 长期漏跑（实测 --module 104 suite vs 全量
    # 118 suite，缺 14 个 + 247 个测试断言）。改为 glob 自动发现并按
    # 排除清单剔除 scenario/persona/web 三类专属套件，避免白名单漂移。
    # 排除清单仅限 scenario/persona/web（这些有独立 --scenario/--persona/
    # --web 入口），其他全部默认纳入"module"维度；test_web_api 因需启动
    # 子进程+端口，默认从 module 排除（与 --web_ci 分支一致）。
    from pathlib import Path as _P
    _module_excludes = {"test_runner", "test_web_api", "test_scenarios", "test_persona"}
    _module_mods = sorted([
        p.stem for p in _P(_TESTS_DIR).glob("test_*.py")
        if p.stem not in _module_excludes
    ])
    mapping = {
        "module": _module_mods,
        "scenario": "test_scenarios",
        "persona": "test_persona",
        "web": "test_web_api",
    }

    for key, mod_names in mapping.items():
        if key not in filters:
            continue
        if isinstance(mod_names, str):
            mod_names = [mod_names]
        for mod_name in mod_names:
            try:
                mod = importlib.import_module(mod_name)
            except Exception as e:
                print(f"⚠ 无法加载 {mod_name}: {e}")
                continue
            # v7.3.52（BUG-48）：iter_suite_factories 同时产出 TestSuite
            # 子类与 unittest.TestCase 子类——后者此前永不被收集，断言数
            # 恒 0 而报告显示全绿（生产实证：BUG-46/47 回归测试写成
            # unittest.TestCase，--module 报 3620/3620 全绿但单跑 5 失败
            # + 2 错误）。
            from test_runner import execute_suite, iter_suite_factories, UnittestSuiteAdapter
            for attr_name, attr in iter_suite_factories(mod, mod_name):
                try:
                    if issubclass(attr, TestSuite):
                        # v6.9.65（R3）：迁移到 execute_suite 调度——旧裸调
                        # （setup/run/teardown 无保护）在套件中途崩溃时
                        # teardown 被跳过 + 失败不计数，"--module 全绿"存在
                        # 假阳性面（12h 健康检查 R3；v6.9.56 的同类修复只
                        # 覆盖了全量路径）。execute_suite 统一提供 teardown
                        # finally 保护与失败计数。
                        execute_suite(attr(), attr_name, suites)
                    else:
                        execute_suite(UnittestSuiteAdapter(attr), attr_name, suites)
                except Exception as e:
                    print(f"⚠ 运行 {attr_name} 失败: {e}")

    return suites


def run_tests(filters: Optional[List[str]] = None, web_ci: bool = False) -> Dict[str, Any]:
    """程序化接口：运行内测并返回结构化结果。

    参数:
        filters: None 表示全量，或 ["module", "scenario", "persona"] 的子集
        web_ci:  CI 模式标志。为 True 时，全量回归纳入 test_web_api
                 （需启动子进程+端口）。默认 False 时全量跳过 test_web_api，
                 由 --web 显式专项运行。

    返回:
        {
            "passed": bool,
            "total": int,
            "passed_count": int,
            "failed_count": int,
            "duration": float,
            "suites": [
                {
                    "name": str,
                    "passed": int,
                    "failed": int,
                    "total": int,
                    "duration": float,
                    "failures": [{"name": str, "msg": str}, ...]
                },
                ...
            ],
            "summary": str,  # 人类可读摘要
        }
    """
    if filters:
        suites = _run_selected(filters)
    else:
        # 全量：通过 test_runner.run_all 的等价逻辑，但收集结果
        # v6.9.54：--web-ci 全量顺序下标记环境变量——test_proposal_kb_sync
        # 等套件存在跨套件模块污染（from-import 值绑定绕过 patch，历史上
        # 曾把测试课题写穿真实 knowledge/），全量模式跳过、单跑/专项验证
        if web_ci:
            os.environ["LINSAI_TEST_ORDERED_FULL"] = "1"
        suites = []
        import importlib
        test_dir = _TESTS_DIR
        for fpath in sorted(test_dir.glob("test_*.py")):
            mod_name = fpath.stem
            if mod_name == "test_runner":
                continue
            # test_web_api 需启动子进程+端口：默认全量跳过，
            # --web-ci（web_ci=True）时纳入全量回归，--web 时由 _run_selected 专项运行
            if mod_name == "test_web_api" and not web_ci:
                print("○ 跳过 test_web_api（需启动子进程；使用 --web-ci 在全量中纳入）")
                continue
            try:
                mod = importlib.import_module(mod_name)
            except Exception as e:  # noqa: BLE001 —— 隐式吞掉会让 14+ 套件永远不跑（v7.2.25）
                print(f"⚠ 加载测试模块 {mod_name} 失败: {type(e).__name__}: {str(e)[:200]}")
                continue
            # v7.3.52（BUG-48）：iter_suite_factories 同时产出 TestSuite
            # 子类与 unittest.TestCase 子类（后者此前永不被收集）。
            from test_runner import execute_suite, iter_suite_factories, UnittestSuiteAdapter
            for attr_name, attr in iter_suite_factories(mod, mod_name):
                try:
                    if issubclass(attr, TestSuite):
                        # v6.9.54：复用 execute_suite（teardown finally 保护 +
                        # 崩溃套件计入失败 + 套件间模块卫生；__module__ 过滤
                        # 防止 from-import 的套件类被重复执行）。此前这里是一
                        # 份复制调度且 except Exception: pass——WebApiSuite 因
                        # /api/heartbeat 超时崩溃后被静默吞掉：子进程泄漏 +
                        # 断言从未计数。
                        execute_suite(attr(), attr_name, suites)
                    else:
                        execute_suite(UnittestSuiteAdapter(attr), attr_name, suites)
                except Exception as e:
                    print(f"⚠ 实例化 {attr_name} 失败: {e}")

    # v7.2.49：集中回收本轮创建的隔离环境目录。
    # 缺陷：15 个套件用 create_isolated_env() 建隔离根但未在 teardown 清理，
    # 每次全量回归泄漏数十 MB～GB 到 /var/folders/…/T/，累积后写满磁盘
    # （2026-10-26 20h 实测：238GB / 磁盘 100% / 剩 117Mi，Shell 工具
    # 全线崩溃、健康检查无法执行）。此处按 finally 语义回收，atexit 兜底。
    try:
        from test_runner import cleanup_isolated_envs
        _reclaimed = cleanup_isolated_envs()
        if _reclaimed:
            print(f"✓ 回收隔离环境目录 {_reclaimed} 个")
    except Exception:
        pass

    # 汇总
    total_passed = 0
    total_failed = 0
    total_duration = 0.0
    suite_results = []

    for suite in suites:
        s = suite.summary()
        total_passed += s["passed"]
        total_failed += s["failed"]
        total_duration += suite.duration

        failures = [
            {"name": r.name, "msg": r.msg}
            for r in s["results"] if not r.passed
        ]
        suite_results.append({
            "name": s["name"],
            "passed": s["passed"],
            "failed": s["failed"],
            "total": s["total"],
            "duration": s["duration"],
            "failures": failures,
        })

    grand_total = total_passed + total_failed
    all_passed = total_failed == 0

    # 生成人类可读摘要
    lines = ["=" * 50, "  LinSai-CoPilot 内测报告", "=" * 50]
    for sr in suite_results:
        icon = "✓" if sr["failed"] == 0 else "✗"
        lines.append(f"\n{icon} {sr['name']}")
        lines.append(f"   通过 {sr['passed']}/{sr['total']}  |  耗时 {sr['duration']:.3f}s")
        for f in sr["failures"]:
            lines.append(f"   ✗ {f['name']}")
            if f["msg"]:
                lines.append(f"      → {f['msg']}")
    lines.append("\n" + "-" * 50)
    if all_passed:
        lines.append(f"🟢 全量通过  {total_passed}/{grand_total}  总耗时 {total_duration:.3f}s")
    else:
        lines.append(f"🔴 存在失败  {total_passed}/{grand_total}  总耗时 {total_duration:.3f}s")
    lines.append("=" * 50)
    summary = "\n".join(lines)

    return {
        "passed": all_passed,
        "total": grand_total,
        "passed_count": total_passed,
        "failed_count": total_failed,
        "duration": round(total_duration, 3),
        "suites": suite_results,
        "summary": summary,
    }


def main():
    parser = argparse.ArgumentParser(description="LinSai-CoPilot 内测系统")
    parser.add_argument("--module", action="store_true", help="仅运行核心模块测试")
    parser.add_argument("--scenario", action="store_true", help="仅运行场景剧本")
    parser.add_argument("--persona", action="store_true", help="仅运行人格抽检")
    parser.add_argument("--web", action="store_true", help="仅运行 Web API 虚拟用户测试")
    parser.add_argument("--web-ci", action="store_true",
                        help="CI 模式：全量回归 + Web API 测试（启动子进程）")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式结果")
    args = parser.parse_args()

    filters = []
    if args.module:
        filters.append("module")
    if args.scenario:
        filters.append("scenario")
    if args.persona:
        filters.append("persona")
    if args.web:
        filters.append("web")

    if args.web_ci:
        # CI 模式：确保 Web API 测试纳入
        if "web" not in filters:
            filters.append("web")
        # --web-ci 单独使用 → 全量回归 + Web API（走全量分支，web_ci=True）
        if len(filters) == 1:
            result = run_tests(None, web_ci=True)
        else:
            # 与其他 filter 组合 → 仅运行指定维度（含 web）
            result = run_tests(filters)
    else:
        result = run_tests(filters if filters else None)

    if args.json:
        import json
        # 移除不可序列化的 failures 细节，保留 summary
        output = {
            "passed": result["passed"],
            "total": result["total"],
            "passed_count": result["passed_count"],
            "failed_count": result["failed_count"],
            "duration": result["duration"],
            "suites": [
                {"name": s["name"], "passed": s["passed"], "failed": s["failed"],
                 "total": s["total"], "duration": s["duration"]}
                for s in result["suites"]
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(result["summary"])

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
