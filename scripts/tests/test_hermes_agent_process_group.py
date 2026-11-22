#!/usr/bin/env python3
"""
test_hermes_agent_process_group.py — hermes agent 进程组清理验证测试

验证 v6.8.40 修复:
    _run_hermes_agent 使用 Popen + start_new_session=True + os.killpg
    替代 subprocess.run(timeout=N)，确保超时后 hermes CLI 及其派生的
    gateway 子进程被彻底清理（与 proposal_lifecycle/optimize.py
    v6.8.3-fix9 修复策略一致）。

背景:
    subprocess.run(timeout=N) 在 macOS 上只 kill 直接子进程，若 hermes CLI
    fork 了额外进程（如 gateway worker），这些进程会继续运行导致 CLI
    端口/管道不释放，孤儿进程累积消耗资源（2026-07-26 机器冻结事故同类
    风险）。该函数被 lit_read/lit_search/gap_identify 及 literature_service
    深度阅读路径使用。

验证点:
    1. Popen 调用带 start_new_session=True（新进程组 leader）
    2. 超时时 os.killpg 被调用（SIGTERM，必要时 SIGKILL）
    3. 超时返回契约 {success:False, error 含超时, elapsed_s}
    4. 成功路径返回契约 {success:True, output 透传}
    5. 非零退出码返回 {success:False, error 含 stderr}
    6. FileNotFoundError 返回"未找到 hermes 命令"
"""

import importlib
import subprocess
import sys
from unittest.mock import MagicMock, patch

from test_runner import TestSuite, create_isolated_env, isolate_logger


class HermesAgentProcessGroupTests(TestSuite):
    def __init__(self):
        super().__init__("hermes agent 进程组清理验证测试")
        self.tmp_root = None
        self.hm = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in list(sys.modules.keys()):
            if mod_name in ["hermes_memory", "paths", "common", "logger"]:
                del sys.modules[mod_name]
        self.hm = importlib.import_module("hermes_memory")
        # v7.3.67：上面的模块清理使 logger 以真实 LOGS_DIR 重新导入，抵消了
        # create_isolated_env 的日志隔离。本套件会走到超时分支并打 WARNING，
        # 于是生产 logs/linsai.log 留下 "agent loop 超时 timeout=30s" 假告警
        # （巡检误判为异常增多）。重新隔离一次。
        isolate_logger(self.tmp_root)

    def teardown(self):
        pass

    def run_tests(self):
        # ================================================================
        # 测试 1: Popen 使用 start_new_session=True（成功路径）
        # ================================================================
        fake_proc = MagicMock()
        fake_proc.communicate.return_value = ("输出内容", "")
        fake_proc.returncode = 0
        with patch("hermes_memory.subprocess.Popen", return_value=fake_proc) as mock_popen:
            result = self.hm._run_hermes_agent("researcher", "测试提示", timeout=30)
            self.assert_true(
                result.get("success"),
                "成功路径应返回 success=True",
                f"result={result}",
            )
            self.assert_eq(
                result.get("output"), "输出内容",
                "成功路径应透传 output",
                f"result={result}",
            )
            kwargs = mock_popen.call_args.kwargs
            self.assert_true(
                kwargs.get("start_new_session") is True,
                "Popen 应使用 start_new_session=True（新进程组 leader）",
                f"kwargs={kwargs}",
            )

        # ================================================================
        # 测试 2: 超时时调用 os.killpg 清理整个进程组
        # ================================================================
        fake_proc2 = MagicMock()
        fake_proc2.communicate.side_effect = subprocess.TimeoutExpired("hermes", 30)
        fake_proc2.pid = 12345
        with patch("hermes_memory.subprocess.Popen", return_value=fake_proc2), \
             patch("hermes_memory.os.getpgid", return_value=12345), \
             patch("hermes_memory.os.killpg") as mock_killpg:
            result2 = self.hm._run_hermes_agent("researcher", "测试提示", timeout=30)
            self.assert_true(
                not result2.get("success"),
                "超时路径应返回 success=False",
                f"result={result2}",
            )
            self.assert_true(
                "超时" in result2.get("error", ""),
                "超时 error 应包含超时信息",
                f"result={result2}",
            )
            self.assert_true(
                mock_killpg.called,
                "超时后应调用 os.killpg 清理进程组",
                f"killpg calls={mock_killpg.call_args_list}",
            )
            first_call = mock_killpg.call_args_list[0]
            self.assert_eq(
                first_call.args[0], 12345,
                "killpg 应针对子进程组 pid",
                f"call={first_call}",
            )

        # ================================================================
        # 测试 3: 非零退出码返回 error（透传 stderr）
        # ================================================================
        fake_proc3 = MagicMock()
        fake_proc3.communicate.return_value = ("", "错误信息XYZ")
        fake_proc3.returncode = 1
        with patch("hermes_memory.subprocess.Popen", return_value=fake_proc3):
            result3 = self.hm._run_hermes_agent("researcher", "测试提示", timeout=30)
            self.assert_true(
                not result3.get("success"),
                "非零退出码应返回 success=False",
                f"result={result3}",
            )
            self.assert_true(
                "错误信息XYZ" in result3.get("error", ""),
                "非零退出码应透传 stderr",
                f"result={result3}",
            )

        # ================================================================
        # 测试 4: FileNotFoundError 返回"未找到 hermes 命令"
        # ================================================================
        with patch("hermes_memory.subprocess.Popen", side_effect=FileNotFoundError):
            result4 = self.hm._run_hermes_agent("researcher", "测试提示", timeout=30)
            self.assert_true(
                "未找到 hermes" in result4.get("error", ""),
                "FileNotFoundError 应返回未找到 hermes 命令",
                f"result={result4}",
            )

        # ================================================================
        # 测试 5: 一般异常兜底清理进程组
        # ================================================================
        fake_proc5 = MagicMock()
        fake_proc5.poll.return_value = None  # 进程仍在运行
        fake_proc5.communicate.side_effect = RuntimeError("boom")
        with patch("hermes_memory.subprocess.Popen", return_value=fake_proc5), \
             patch("hermes_memory.os.getpgid", return_value=999), \
             patch("hermes_memory.os.killpg") as mock_killpg5:
            result5 = self.hm._run_hermes_agent("researcher", "测试提示", timeout=30)
            self.assert_true(
                not result5.get("success"),
                "异常路径应返回 success=False",
                f"result={result5}",
            )
            self.assert_true(
                mock_killpg5.called,
                "异常兜底应调用 os.killpg 清理进程组",
                f"killpg calls={mock_killpg5.call_args_list}",
            )
