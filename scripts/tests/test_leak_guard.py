#!/usr/bin/env python3
"""
test_leak_guard.py — 测试基建防泄漏回归（v6.9.54）

背景：2026-08 排查发现 --web-ci 每次运行泄漏 1 个 web_server 子进程
（累计 57 个孤儿），根因链：
    /api/heartbeat 内含外网检索（50s+） → ApiClient socket.timeout
    → run_tests 中途抛异常 → self_test 复制调度逻辑 except:pass
    → teardown 被跳过 + 套件从报告蒸发（"全量通过"掩盖 44 个断言）。

本套件锁定三层修复的回归：
    1. test_runner.execute_suite：teardown 放 finally；崩溃套件计入
       报告并追加 1 条失败结果（不得静默蒸发）。
    2. test_web_api._match_orphan_server：孤儿进程识别不误伤正式实例。
    3. backup_manager.prune_backups：轮转保留语义（keep/非 zip/keep<=0）。

用法（自动纳入 self_test 全量回归，无需单独运行）：
    python3 scripts/self_test.py --module
"""

import sys
import tempfile
import time
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
_TESTS_DIR = Path(__file__).parent.resolve()
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from test_runner import TestSuite  # noqa: E402


def _make_crash_suite() -> "TestSuite":
    """构造 run_tests 中途抛异常的假套件（模拟 socket.timeout 炸穿）。

    注意：必须工厂函数局部构造——若在模块级定义 TestSuite 子类，
    会被 run_all 的自动发现当作独立套件执行（v6.9.54 实测踩坑）。
    """

    class _CrashSuite(TestSuite):
        def __init__(self):
            super().__init__("崩溃套件")
            self.torndown = False

        def setup(self):
            self.setup_done = True

        def run_tests(self):
            self.assert_true(True, "崩溃前断言")
            raise RuntimeError("模拟 socket.timeout 炸穿")

        def teardown(self):
            self.torndown = True

    return _CrashSuite()


def _make_ok_suite() -> "TestSuite":
    """构造正常假套件（同样必须工厂函数，避免被自动发现）。"""

    class _OkSuite(TestSuite):
        def __init__(self):
            super().__init__("正常套件")
            self.torndown = False

        def run_tests(self):
            self.assert_true(True, "正常断言")

        def teardown(self):
            self.torndown = True

    return _OkSuite()


class LeakGuardSuite(TestSuite):
    """测试基建防泄漏回归。"""

    def __init__(self):
        super().__init__("测试基建防泄漏回归")

    def run_tests(self):
        from test_runner import execute_suite
        from test_web_api import _match_orphan_server

        # ── 1. execute_suite：异常时 teardown 仍被调用（finally 保护） ──
        suites = []
        execute_suite(_make_crash_suite(), "崩溃套件", suites)
        crashed = suites[0]
        self.assert_true(crashed.torndown, "异常套件 teardown 仍被调用（finally）")
        self.assert_true(len(suites) == 1, "崩溃套件仍进入报告（不蒸发）")
        crash_results = [r for r in crashed.results if not r.passed]
        self.assert_true(
            any(r.name == "套件完整执行" for r in crash_results),
            "崩溃套件追加'套件完整执行'失败结果")
        self.assert_true(
            any(r.passed for r in crashed.results),
            "崩溃前的已通过断言保留在报告中")

        # ── 2. execute_suite：正常路径 teardown 也被调用 ──
        suites2 = []
        execute_suite(_make_ok_suite(), "正常套件", suites2)
        ok = suites2[0]
        self.assert_true(ok.torndown, "正常套件 teardown 被调用")
        self.assert_true(
            ok.summary()["failed"] == 0, "正常套件无失败结果")

        # ── 3. execute_suite：teardown 自身异常不吞掉测试结果 ──
        bad = _make_ok_suite()

        def _bad_teardown():
            raise RuntimeError("清理失败")

        bad.teardown = _bad_teardown
        suites3 = []
        execute_suite(bad, "坏清理套件", suites3)
        bad = suites3[0]
        self.assert_true(
            len(bad.results) == 1 and bad.results[0].passed,
            "teardown 异常不影响已记录的测试结果")

        # ── 4. 孤儿进程识别：不误伤正式实例 ──
        orphan_cmd = (
            "/usr/bin/python3 /Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py "
            "--port 49435 --root /var/folders/xx/T/linsai_test_927weqn2"
        )
        prod_cmds = [
            "/usr/bin/python3 scripts/web_server.py --port 8080",
            "/usr/bin/python3 scripts/web_server.py --port 8088",
        ]
        unrelated = "/usr/bin/python3 scripts/other_server.py --root /var/folders/xx/T/linsai_test_1"
        self.assert_true(_match_orphan_server(orphan_cmd), "识别带 linsai_test root 的测试 server")
        for cmd in prod_cmds:
            self.assert_true(
                not _match_orphan_server(cmd),
                f"正式实例（无 --root）不误伤: {cmd[-30:]}")
        self.assert_true(
            not _match_orphan_server(unrelated),
            "非 web_server.py 进程不匹配")

        # ── 5. ApiClient 网络容错：连接拒绝返回 (0, 错误信息) 而非抛异常 ──
        from test_web_api import ApiClient
        import socket as _socket
        with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            free_port = s.getsockname()[1]
        client = ApiClient(f"http://127.0.0.1:{free_port}", timeout=3)
        try:
            code, payload = client.get("/api/version")
            self.assert_true(
                code == 0 and isinstance(payload, str),
                "连接拒绝返回 code=0 字符串（不抛异常炸套件）")
        except Exception as e:
            self.assert_true(False, f"网络错误不应抛异常: {type(e).__name__}: {e}")

        # ── 6. backup_manager.prune_backups：轮转保留语义 ──
        from backup_manager import prune_backups
        with tempfile.TemporaryDirectory() as td:
            tdir = Path(td)
            for i in range(4):
                p = tdir / f"2026-08-2{i}T00-00-00Z.zip"
                p.write_bytes(b"fake")
                stamp = 1756000000 + i * 86400
                import os
                os.utime(p, (stamp, stamp))
            (tdir / "notes.txt").write_text("非 zip 不动")
            (tdir / "subdir").mkdir()

            pruned = prune_backups(keep=2, backups_dir=tdir)
            self.assert_true(len(pruned) == 2, "prune keep=2 清理最旧 2 份")
            remaining = list(tdir.glob("*.zip"))
            self.assert_true(len(remaining) == 2, "保留最近 2 份")
            self.assert_true(
                (tdir / "notes.txt").exists() and (tdir / "subdir").exists(),
                "非 zip 文件与子目录不受影响")
            self.assert_true(
                prune_backups(keep=0, backups_dir=tdir) == [],
                "keep<=0 防误配清空（不删除）")

        # ── 7. 学习机会缓存：TTL 判定逻辑 ──
        from datetime import datetime, timedelta, timezone
        from proactive_engine import (
            _LEARNING_OPPS_CACHE,
            _learning_opps_cache_valid,
        )
        from common import save_json
        import json as _json
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        fresh_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        deg_ts = (datetime.now(timezone.utc) - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        cache_backup = _LEARNING_OPPS_CACHE.read_text() if _LEARNING_OPPS_CACHE.exists() else None
        try:
            save_json(_LEARNING_OPPS_CACHE, {"checked_at": old_ts, "signals": [{"x": 1}]})
            valid, _ = _learning_opps_cache_valid()
            self.assert_true(not valid, "超过 6h 的缓存过期")

            save_json(_LEARNING_OPPS_CACHE, {"checked_at": fresh_ts, "signals": [{"x": 1}]})
            valid, sigs = _learning_opps_cache_valid()
            self.assert_true(valid and sigs == [{"x": 1}], "TTL 内缓存命中并返回 signals")

            save_json(_LEARNING_OPPS_CACHE, {"checked_at": deg_ts, "signals": [], "degraded": True})
            valid, _ = _learning_opps_cache_valid()
            self.assert_true(not valid, "降级条目超过 10 分钟即过期（快速重试）")
        finally:
            # 还原现场（测试前不存在则删除）
            if cache_backup is not None:
                _LEARNING_OPPS_CACHE.write_text(cache_backup)
            elif _LEARNING_OPPS_CACHE.exists():
                _LEARNING_OPPS_CACHE.unlink()


if __name__ == "__main__":
    suite = LeakGuardSuite()
    t0 = time.time()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    failed = [r for r in suite.results if not r.passed]
    for r in suite.results:
        print(("✓ " if r.passed else "✗ ") + r.name + (f"  {r.msg}" if r.msg else ""))
    print(f"\n通过 {len(suite.results) - len(failed)}/{len(suite.results)}")
    sys.exit(0 if not failed else 1)
