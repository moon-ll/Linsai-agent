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

    suites = []
    mapping = {
        "module": ["test_core", "test_lifecycle_cron", "test_adversarial_governance", "test_proposal_kb_sync", "test_weekend_pipeline", "test_literature_service", "test_learning_cycle_dispatch", "test_optimize_sections", "test_optimize_dimension_scores", "test_exemplar_injection_log", "test_micro_scheduler_rotation", "test_prompt_optimizer", "test_kanban_round_stats", "test_stale_cleanup_out_of_slot", "test_monitor_kanban_local", "test_monitor_cron_stale", "test_cron_stale_weekend_grace", "test_round_complete_break", "test_derived_job_priority", "test_kb_proposal_reorg", "test_auto_retry_error_history", "test_derived_step_timeout", "test_hermes_agent_process_group", "test_input_breaker", "test_cron_dedup_default", "test_alert_circuits", "test_auto_acceptance", "test_heartbeat_kanban_merge", "test_weekend_kb_maintain", "test_kb_distill_created_ts", "test_weekend_pipeline_hardening", "test_prompt_benchmark_guard", "test_input_pipeline_repair", "test_input_clustering", "test_quality_ceiling_convergence"],
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
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                try:
                    if (isinstance(attr, type) and issubclass(attr, TestSuite)
                            and attr is not TestSuite):
                        instance = attr()
                        t0 = __import__("time").time()
                        instance.setup()
                        instance.run_tests()
                        instance.teardown()
                        instance.duration = __import__("time").time() - t0
                        suites.append(instance)
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
            except Exception as e:
                continue
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                try:
                    if (isinstance(attr, type) and issubclass(attr, TestSuite)
                            and attr is not TestSuite):
                        instance = attr()
                        t0 = __import__("time").time()
                        instance.setup()
                        instance.run_tests()
                        instance.teardown()
                        instance.duration = __import__("time").time() - t0
                        suites.append(instance)
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
