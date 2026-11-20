"""测试模式下 KB 同步零写入守卫测试（v7.3.70）。

背景：micro_scheduler._sync_proposal_to_kb 会以子进程调用
kb_proposal_reorg.py --apply，子进程不继承 patch_module_root 的隔离根，
导致全量回归把真实 knowledge/wiki/projects 的 versions/reports 全量重写
（实测 2026-11-08 30 个真实课题页 created/updated 被改成测试时刻）。
"""

import os
import subprocess

from test_runner import TestSuite


class KbSyncTestModeGuardTests(TestSuite):
    def __init__(self):
        super().__init__("测试模式 KB 同步零写入守卫")

    def run_tests(self):
        # 1) test_runner 导入即置位测试模式
        self.assert_eq(
            os.environ.get("LINSAI_TEST_MODE"), "1",
            "test_runner 导入后应设置 LINSAI_TEST_MODE=1",
        )

        import proposal_kb_sync
        from lifecycle import micro_scheduler as ms

        calls = []
        orig_cls = proposal_kb_sync.ProposalKbSync
        orig_run = subprocess.run

        class _StubSync:
            def __init__(self):
                calls.append("init")

            def sync_proposal(self, proposal_id):
                calls.append("sync")

        proposal_kb_sync.ProposalKbSync = _StubSync
        subprocess.run = lambda *a, **kw: calls.append("reorg")

        try:
            # 2) 测试模式下：完全跳过同步（不实例化、不起子进程）
            ms._sync_proposal_to_kb("general-guard-test-20260101")
            self.assert_eq(calls, [], "测试模式不得写知识库或起 reorg 子进程")

            # 3) 非测试模式：恢复正常同步链路
            os.environ.pop("LINSAI_TEST_MODE", None)
            ms._sync_proposal_to_kb("general-guard-test-20260101")
            self.assert_eq(
                calls, ["init", "sync", "reorg"],
                "非测试模式应恢复 sync_proposal 与 reorg 子进程调用",
            )
        finally:
            proposal_kb_sync.ProposalKbSync = orig_cls
            subprocess.run = orig_run
            os.environ["LINSAI_TEST_MODE"] = "1"
