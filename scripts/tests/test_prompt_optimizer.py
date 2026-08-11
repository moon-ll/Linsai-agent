#!/usr/bin/env python3
"""
test_prompt_optimizer.py — Prompt 优化器单元测试

覆盖：
    - _apply_suggestion 备份权限错误处理
    - _apply_suggestion 读取权限错误处理
    - _apply_suggestion 写入权限错误处理
    - apply_error 字段正确标记
    - _apply_suggestions 失败建议状态变更为 failed
    - _log_auto_applied 正确调用 debug_journal
    - 正常应用建议流程（无权限错误时的基线）

注意：
    本测试不修改真实 hermes profiles 文件，通过 monkey-patch
    shutil.copy2 / Path.read_text / Path.write_text 模拟权限错误。
"""

import sys
import shutil
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT
import importlib


class PromptOptimizerTests(TestSuite):
    def __init__(self):
        super().__init__("Prompt 优化器权限错误处理测试")
        self.tmp_root = None
        self.po_mod = None
        self.dj_mod = None

    def setup(self):
        self.tmp_root = create_isolated_env()

        # 创建 memory 目录（create_isolated_env 已创建，但确保子目录存在）
        (self.tmp_root / "memory" / "prompt-backups").mkdir(parents=True, exist_ok=True)

        # 创建模拟的 hermes profiles 目录
        hermes_dir = self.tmp_root / ".hermes" / "profiles"
        for profile in ["writer", "critic", "researcher", "analyst", "linsai"]:
            pdir = hermes_dir / profile
            pdir.mkdir(parents=True, exist_ok=True)
            (pdir / "SOUL.md").write_text(
                f"# {profile} SOUL\n\n这是测试用 prompt 文件。\n",
                encoding="utf-8",
            )

        # 强制重新导入模块
        for mod_name in ["prompt_optimizer", "debug_journal"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        self.po_mod = importlib.import_module("prompt_optimizer")
        self.dj_mod = importlib.import_module("debug_journal")

        patch_module_root("prompt_optimizer", self.tmp_root)
        patch_module_root("debug_journal", self.tmp_root)

        # 覆盖 HERMES_PROFILES_DIR 指向隔离环境
        self.po_mod.HERMES_PROFILES_DIR = hermes_dir

        # 覆盖 BACKUPS_DIR 指向隔离环境
        self.po_mod.BACKUPS_DIR = self.tmp_root / "memory" / "prompt-backups"

        # 覆盖 SUGGESTIONS_PATH 指向隔离环境
        self.po_mod.SUGGESTIONS_PATH = self.tmp_root / "memory" / "prompt-suggestions.json"

        # 覆盖 DEBUG_JOURNAL_PATH 指向隔离环境
        self.po_mod.DEBUG_JOURNAL_PATH = self.tmp_root / "memory" / "debug-journal.json"
        self.dj_mod._JOURNAL_PATH_OVERRIDE = self.tmp_root / "memory" / "debug-journal.json"

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_suggestion(self, profile="writer", content="## 测试优化规则\n\n测试内容\n"):
        """构造一条测试用建议。"""
        target_file = self.po_mod.HERMES_PROFILES_DIR / profile / "SOUL.md"
        return {
            "id": "test-ps-001",
            "source": "test",
            "target_profile": profile,
            "target_file": str(target_file),
            "target_file_display": f"~/.hermes/profiles/{profile}/SOUL.md",
            "priority": "high",
            "action": "append",
            "content": content,
            "description": "测试建议",
            "expected_impact": "验证权限错误处理",
            "fingerprint": "testfp001",
            "status": "pending",
            "created_at": "2026-08-05T00:00:00Z",
        }

    # ── 测试用例 ──

    def _test_backup_permission_error(self):
        """备份时遇到 PermissionError，应返回 False 并标记 apply_error。"""
        suggestion = self._make_suggestion()
        original_copy2 = shutil.copy2

        def mock_copy2(src, dst):
            raise PermissionError(13, "Permission denied", str(dst))

        with patch("shutil.copy2", mock_copy2):
            result = self.po_mod._apply_suggestion(suggestion)

        self.assert_eq(result, False, "备份权限错误时返回 False")
        self.assert_eq(
            suggestion.get("apply_error"), "backup_permission_denied",
            "apply_error 标记为 backup_permission_denied",
        )

    def _test_read_permission_error(self):
        """读取时遇到 PermissionError，应返回 False 并标记 apply_error。"""
        suggestion = self._make_suggestion()
        original_read_text = Path.read_text

        original_copy2 = shutil.copy2

        def mock_copy2_normal(src, dst):
            # 备份成功
            import os
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, "rb") as f_src, open(dst, "wb") as f_dst:
                f_dst.write(f_src.read())

        def mock_read_text(self, *args, **kwargs):
            raise PermissionError(13, "Permission denied", str(self))

        with patch("shutil.copy2", mock_copy2_normal), \
             patch.object(Path, "read_text", mock_read_text):
            result = self.po_mod._apply_suggestion(suggestion)

        self.assert_eq(result, False, "读取权限错误时返回 False")
        self.assert_eq(
            suggestion.get("apply_error"), "read_permission_denied",
            "apply_error 标记为 read_permission_denied",
        )

    def _test_write_permission_error(self):
        """写入时遇到 PermissionError，应返回 False 并标记 apply_error。"""
        suggestion = self._make_suggestion()
        original_copy2 = shutil.copy2

        def mock_copy2_normal(src, dst):
            import os
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, "rb") as f_src, open(dst, "wb") as f_dst:
                f_dst.write(f_src.read())

        def mock_write_text(self, *args, **kwargs):
            raise PermissionError(13, "Permission denied", str(self))

        with patch("shutil.copy2", mock_copy2_normal), \
             patch.object(Path, "write_text", mock_write_text):
            result = self.po_mod._apply_suggestion(suggestion)

        self.assert_eq(result, False, "写入权限错误时返回 False")
        self.assert_eq(
            suggestion.get("apply_error"), "write_permission_denied",
            "apply_error 标记为 write_permission_denied",
        )

    def _test_apply_suggestions_marks_failed(self):
        """_apply_suggestions 在建议失败时标记 status=failed。"""
        suggestion = self._make_suggestion()
        all_suggestions = [suggestion]

        def mock_copy2(src, dst):
            raise PermissionError(13, "Permission denied", str(dst))

        with patch("shutil.copy2", mock_copy2):
            self.po_mod._apply_suggestions(
                [suggestion], all_suggestions, auto_mode=True
            )

        self.assert_eq(
            suggestion["status"], "failed",
            "失败建议标记为 failed",
        )
        self.assert_in(
            "failed_at", suggestion,
            "失败建议包含 failed_at 时间戳",
        )
        self.assert_eq(
            suggestion.get("failed_mode"), "auto",
            "failed_mode 标记为 auto",
        )

    def _test_apply_suggestions_success_marks_applied(self):
        """正常应用时标记 status=applied。"""
        suggestion = self._make_suggestion(content="## 正常测试规则\n\n这是正常内容\n")
        all_suggestions = [suggestion]

        self.po_mod._apply_suggestions(
            [suggestion], all_suggestions, auto_mode=False
        )

        self.assert_eq(
            suggestion["status"], "applied",
            "成功建议标记为 applied",
        )
        self.assert_in(
            "applied_at", suggestion,
            "成功建议包含 applied_at 时间戳",
        )
        self.assert_eq(
            suggestion.get("applied_mode"), "manual",
            "applied_mode 标记为 manual",
        )
        # apply_error 应不存在
        self.assert_true(
            "apply_error" not in suggestion,
            "成功建议不应有 apply_error 字段",
        )

    def _test_apply_suggestion_content_already_exists(self):
        """内容已存在时跳过，返回 True。"""
        profile = "critic"
        existing_content = "## 已有规则\n\n已有内容\n"
        target_file = self.po_mod.HERMES_PROFILES_DIR / profile / "SOUL.md"
        target_file.write_text(f"# SOUL\n\n{existing_content}\n", encoding="utf-8")

        suggestion = self._make_suggestion(profile=profile, content=existing_content)
        result = self.po_mod._apply_suggestion(suggestion)

        self.assert_eq(result, True, "内容已存在时返回 True（跳过）")

    def _test_apply_suggestion_file_not_found(self):
        """目标文件不存在时返回 False。"""
        suggestion = self._make_suggestion()
        suggestion["target_file"] = "/nonexistent/path/SOUL.md"
        result = self.po_mod._apply_suggestion(suggestion)
        self.assert_eq(result, False, "目标文件不存在时返回 False")

    def _test_log_auto_applied_calls_debug_journal(self):
        """_log_auto_applied 正确调用 debug_journal.add_entry。"""
        suggestion = self._make_suggestion()
        suggestion["status"] = "applied"
        suggestion["applied_at"] = "2026-08-05T00:00:00Z"

        # 确保 debug_journal 模块路径正确
        sys.path.insert(0, str(self.tmp_root / "scripts"))

        self.po_mod._log_auto_applied([suggestion])

        # 验证 debug journal 中有记录
        journal_path = self.tmp_root / "memory" / "debug-journal.json"
        self.assert_true(journal_path.exists(), "debug journal 文件已创建")

        data = json.loads(journal_path.read_text(encoding="utf-8"))
        entries = data.get("entries", [])
        self.assert_true(len(entries) > 0, "debug journal 有条目")

        # 验证条目内容
        entry = entries[-1]
        self.assert_eq(entry["category"], "prompt_tuning", "条目 category 为 prompt_tuning")
        self.assert_eq(entry["severity"], "minor", "条目 severity 为 minor")
        self.assert_eq(entry["status"], "verified", "条目 status 为 verified")
        self.assert_in("prompt_optimization", entry["tags"], "标签包含 prompt_optimization")
        self.assert_in("auto_applied", entry["tags"], "标签包含 auto_applied")

    def _test_log_auto_applied_silent_failure(self):
        """_log_auto_applied 在 debug_journal 不可用时静默失败（不抛异常）。"""
        suggestion = self._make_suggestion()

        # 临时破坏 debug_journal 模块
        original_dj = sys.modules.get("debug_journal")
        sys.modules["debug_journal"] = None

        try:
            # 不应抛出异常
            self.assert_no_exception(
                self.po_mod._log_auto_applied,
                "debug_journal 不可用时不抛异常",
                [suggestion],
            )
        finally:
            # 恢复
            if original_dj is not None:
                sys.modules["debug_journal"] = original_dj
            else:
                sys.modules.pop("debug_journal", None)

    def _test_auto_mode_handles_failed_suggestions(self):
        """auto 模式下失败建议不会被记录到 debug_journal。"""
        suggestion = self._make_suggestion()
        all_suggestions = [suggestion]

        # 清空 debug journal（前面测试可能已写入记录）
        journal_path = self.tmp_root / "memory" / "debug-journal.json"
        if journal_path.exists():
            journal_path.unlink()

        def mock_copy2(src, dst):
            raise PermissionError(13, "Permission denied", str(dst))

        with patch("shutil.copy2", mock_copy2):
            # 模拟 cmd_auto 中的关键流程
            self.po_mod._apply_suggestions(
                [suggestion], all_suggestions, auto_mode=True
            )

        # 失败的建议不应被记录
        applied_ok = [s for s in [suggestion] if s.get("status") == "applied"]
        self.assert_eq(len(applied_ok), 0, "失败建议不计入 applied_ok")

        # debug journal 中不应有自动应用记录
        if journal_path.exists():
            data = json.loads(journal_path.read_text(encoding="utf-8"))
            auto_entries = [
                e for e in data.get("entries", [])
                if "auto_applied" in e.get("tags", [])
            ]
            self.assert_eq(len(auto_entries), 0, "失败建议不写入 debug journal")

    def _test_backup_file_created_on_success(self):
        """成功应用时备份文件被创建。"""
        suggestion = self._make_suggestion(content="## 备份测试规则\n\n测试备份\n")
        result = self.po_mod._apply_suggestion(suggestion)

        self.assert_eq(result, True, "建议成功应用")

        backup_files = list(self.po_mod.BACKUPS_DIR.glob("*.bak"))
        self.assert_true(len(backup_files) > 0, "备份文件已创建")

    def _test_file_content_modified_on_success(self):
        """成功应用后目标文件内容被修改。"""
        profile = "researcher"
        new_content = "## 新增优化规则（测试内容修改）\n\n这是测试添加的内容\n"
        suggestion = self._make_suggestion(profile=profile, content=new_content)

        target_file = self.po_mod.HERMES_PROFILES_DIR / profile / "SOUL.md"
        original = target_file.read_text(encoding="utf-8")

        result = self.po_mod._apply_suggestion(suggestion)
        self.assert_eq(result, True, "建议成功应用")

        modified = target_file.read_text(encoding="utf-8")
        self.assert_true(new_content.strip() in modified, "新内容已写入文件")
        self.assert_true(
            original.rstrip() in modified,
            "原始内容保留",
        )

    # ── v6.8.22 守护测试 ──

    def _test_collect_debug_journal_filters_by_window(self):
        """v6.8.22: _collect_debug_journal_entries 应只采集窗口内条目。

        历史 bug：auto 应用写入的 prompt_tuning 条目会被下次 auto 当作输入，
        形成指数级膨胀。修复：限制为最近 DEBUG_JOURNAL_WINDOW_DAYS 天。
        """
        from datetime import datetime, timezone, timedelta
        journal_path = self.tmp_root / "memory" / "debug-journal.json"

        now = datetime.now(timezone.utc)
        recent_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        old_ts = (now - timedelta(days=self.po_mod.DEBUG_JOURNAL_WINDOW_DAYS + 5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        borderline_ts = (now - timedelta(days=self.po_mod.DEBUG_JOURNAL_WINDOW_DAYS + 1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        journal = {
            "entries": [
                {"id": "dj-20260810-001", "category": "prompt_tuning", "timestamp": recent_ts, "title": "近期条目"},
                {"id": "dj-20260801-001", "category": "prompt_tuning", "timestamp": old_ts, "title": "过期条目"},
                {"id": "dj-20260801-002", "category": "prompt_tuning", "timestamp": borderline_ts, "title": "边界过期"},
                {"id": "dj-20260810-002", "category": "bug_fix", "timestamp": recent_ts, "title": "非 prompt_tuning"},
            ],
            "stats": {},
        }
        journal_path.write_text(json.dumps(journal, ensure_ascii=False), encoding="utf-8")
        self.dj_mod._JOURNAL_PATH_OVERRIDE = journal_path

        result = self.po_mod._collect_debug_journal_entries()

        # 只应返回 1 条（窗口内的近期 prompt_tuning）
        self.assert_eq(len(result), 1, "窗口外条目被过滤")
        self.assert_eq(result[0]["title"], "近期条目", "保留窗口内条目")

    def _test_apply_suggestion_no_backup_when_content_exists(self):
        """v6.8.22: 内容已存在时不应创建备份。

        历史 bug：旧实现先 backup 再判断 content_to_add 是否已存在，导致
        每天数千次冗余备份（每个 ~4.6MB）。新实现先 read 检查。
        """
        profile = "analyst"
        existing_content = "## 已存在规则 v6822\n\n这是已存在的内容\n"
        target_file = self.po_mod.HERMES_PROFILES_DIR / profile / "SOUL.md"
        target_file.write_text(f"# SOUL\n\n{existing_content}\n", encoding="utf-8")

        # 清空已有备份
        for f in self.po_mod.BACKUPS_DIR.glob("*.bak"):
            f.unlink()

        suggestion = self._make_suggestion(profile=profile, content=existing_content)
        result = self.po_mod._apply_suggestion(suggestion)

        self.assert_eq(result, True, "内容已存在时返回 True")
        backup_files = list(self.po_mod.BACKUPS_DIR.glob("*.bak"))
        self.assert_eq(len(backup_files), 0, "内容已存在时不创建备份")

    def _test_apply_suggestion_backup_count_tracker(self):
        """v6.8.22: backup_count_tracker 限制单 run 内同文件备份次数。

        多次真正写入时，超过 MAX_BACKUPS_PER_FILE_PER_RUN 次后跳过备份。
        """
        profile = "linsai"
        target_file = self.po_mod.HERMES_PROFILES_DIR / profile / "SOUL.md"
        target_file.write_text("# SOUL\n\n原始内容\n", encoding="utf-8")

        # 清空该 profile 的所有已有备份（避免被前面测试污染）
        for f in list(self.po_mod.BACKUPS_DIR.glob(f"{profile}-*.bak")):
            f.unlink()

        # 用 3 条不同的内容，模拟 3 次成功写入
        suggestions = []
        for i in range(3):
            content = f"## 测试规则 {i}\n\n内容 {i}\n"
            suggestions.append(self._make_suggestion(profile=profile, content=content))

        backup_tracker = {}
        for s in suggestions:
            self.po_mod._apply_suggestion(s, backup_count_tracker=backup_tracker)

        # 备份次数应 == MAX_BACKUPS_PER_FILE_PER_RUN（默认 1）
        backup_files = list(self.po_mod.BACKUPS_DIR.glob(f"{profile}-*.bak"))
        self.assert_eq(
            len(backup_files),
            self.po_mod.MAX_BACKUPS_PER_FILE_PER_RUN,
            f"备份数受 MAX_BACKUPS_PER_FILE_PER_RUN={self.po_mod.MAX_BACKUPS_PER_FILE_PER_RUN} 限制",
        )
        # tracker 也应记录
        self.assert_eq(
            backup_tracker.get(str(target_file), 0),
            self.po_mod.MAX_BACKUPS_PER_FILE_PER_RUN,
            "tracker 正确记录已备份次数",
        )

    def run_tests(self):
        """执行所有测试用例。"""
        self._test_backup_permission_error()
        self._test_read_permission_error()
        self._test_write_permission_error()
        self._test_apply_suggestions_marks_failed()
        self._test_apply_suggestions_success_marks_applied()
        self._test_apply_suggestion_content_already_exists()
        self._test_apply_suggestion_file_not_found()
        self._test_log_auto_applied_calls_debug_journal()
        self._test_log_auto_applied_silent_failure()
        self._test_auto_mode_handles_failed_suggestions()
        self._test_backup_file_created_on_success()
        self._test_file_content_modified_on_success()
        # v6.8.22 守护测试
        self._test_collect_debug_journal_filters_by_window()
        self._test_apply_suggestion_no_backup_when_content_exists()
        self._test_apply_suggestion_backup_count_tracker()


if __name__ == "__main__":
    from test_runner import print_report

    suite = PromptOptimizerTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    print_report([suite])
