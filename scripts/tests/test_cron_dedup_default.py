#!/usr/bin/env python3
"""
test_cron_dedup_default.py — cleanup_cron_duplicates 默认清单覆盖测试（v6.8.53）

覆盖缺陷：
    monitor 检测端 REQUIRED_CRON_PREFIXES 含 lc-kb-sync（v6.8.51 起），
    但 cleanup_cron_duplicates 的默认 framework_names 清单只有 5 个旧名称。
    结果：2026-08-14 lc-kb-sync 双实例（两次 setup 各建一份），每小时
    monitor 检测到 cron_duplicate → 自动去重清不掉 → 异常每小时复现永不
    收敛，且次日 12:40 将并发执行两次 kb_auto_sync。

修复：
    默认清单补入 KB_SYNC_CRON_NAME；配合创建路径幂等
    （_cron_create_idempotent）双保险。

注意：
    本测试以 FakeHB 替换 hermes_bridge，不调用 hermes/LLM。
"""

import sys
import importlib

from test_runner import TestSuite


class CronDedupDefaultTests(TestSuite):
    def __init__(self):
        super().__init__("cron 去重默认清单测试")

    def setup(self):
        # 强制重新导入，避免缓存污染
        for mod_name in list(sys.modules.keys()):
            if mod_name == "lifecycle.framework":
                del sys.modules[mod_name]
        self.fw = importlib.import_module("lifecycle.framework")
        self._orig_hb = self.fw.hb

    def teardown(self):
        self.fw.hb = self._orig_hb

    def run_tests(self):
        deleted_ids = []

        class FakeHB:
            @staticmethod
            def cron_list_profile(profile):
                return [
                    {
                        "id": "old-kb",
                        "name": "lc-kb-sync",
                        "created_at": "2026-08-14T19:03:11+08:00",
                    },
                    {
                        "id": "new-kb",
                        "name": "lc-kb-sync",
                        "created_at": "2026-08-14T19:26:01+08:00",
                    },
                ]

            @staticmethod
            def cron_delete(cid, profile=None):
                deleted_ids.append(cid)
                return {"success": True}

        self.fw.hb = FakeHB()
        # cleanup_cron_duplicates 是 mixin 风格函数（self 未使用），传 None
        removed = self.fw.cleanup_cron_duplicates(None)

        self.assert_eq(len(removed), 1, "默认清单应覆盖 lc-kb-sync 并删除 1 个副本")
        self.assert_eq(
            removed[0].get("name") if removed else "",
            "lc-kb-sync",
            "被删除的应是 lc-kb-sync",
        )
        self.assert_eq(
            removed[0].get("id") if removed else "",
            "old-kb",
            "应保留最新、删除较旧副本",
        )
        self.assert_eq(deleted_ids, ["old-kb"], "删除调用应恰好命中较旧副本")
