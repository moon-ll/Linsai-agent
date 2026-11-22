#!/usr/bin/env python3
"""
test_housekeeping.py — v6.10.42 数据域滚动治理回归测试

背景（09-24 用户提出"持续膨胀文档需分割+滚动释放"）：五类文件无治理
（weekend-input 周快照 32.7MB / hermes MEMORY.md 196KB / draft 轮次
备份无上限 / knowledge bak 累积 / reading-notes 持续追加）。
housekeeping.py 统一治理，本套件验证各治理函数行为（临时目录零污染）。

验证点：
    1. 周快照：>8 周 gzip / 压缩档 >24 周删除 / 新文件与活文件不动
    2. MEMORY.md：超限滚动（按字节尾部累计）+ 归档不丢内容 + 未超限不动
    3. draft 轮次备份：仅保留最近 3 版
    4. knowledge bak：同前缀保留最近 2 个
    5. reading-notes：>60KB 按 ## 边界分割，旧段入归档
"""

import sys
import os
import shutil
import importlib
from datetime import datetime, timezone
from pathlib import Path

from test_runner import TestSuite, create_isolated_env


class HousekeepingTests(TestSuite):
    def __init__(self):
        super().__init__("数据域滚动治理回归（v6.10.42）")
        self.tmp_root = None
        self.hk = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in list(sys.modules.keys()):
            if mod_name in ("housekeeping", "paths", "common"):
                del sys.modules[mod_name]
        self.hk = importlib.import_module("housekeeping")

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _patch_dirs(self):
        """把 housekeeping 的四个根目录指到隔离环境。"""
        self.hk.WEEKEND_INPUT_DIR = self.tmp_root / "weekend-input"
        self.hk.PROPOSALS_ROOT = self.tmp_root / "research_proposals"
        self.hk.KNOWLEDGE_DIR = self.tmp_root / "knowledge"
        self.hk.HERMES_PROFILES = self.tmp_root / "profiles"

    def _set_age(self, path: Path, days: float) -> None:
        t = datetime.now(timezone.utc).timestamp() - days * 86400
        os.utime(path, (t, t))

    def _test_weekend_snapshots(self):
        self._patch_dirs()
        wi = self.hk.WEEKEND_INPUT_DIR
        wi.mkdir(parents=True)
        fresh = wi / "sources-2026-09-20.json"
        fresh.write_text("[]" * 10, encoding="utf-8")
        old = wi / "sources-2026-07-01.json"
        old.write_text("x" * 2000, encoding="utf-8")
        self._set_age(old, 70)
        ancient_gz = wi / "sources-2026-03-01.json.gz"
        ancient_gz.write_bytes(b"fakegzip" * 100)
        self._set_age(ancient_gz, 200)
        live = wi / "clusters.json"  # 活注册表
        live.write_text("{}", encoding="utf-8")
        self._set_age(live, 200)

        st = self.hk.roll_weekend_snapshots(dry_run=False)

        self.assert_true(fresh.exists(), "8 周内快照不应被压缩")
        self.assert_true(old.with_suffix(".json.gz").exists(), "超 8 周快照应压缩为 .gz")
        self.assert_true(not old.exists(), "压缩后原文件应删除")
        self.assert_true(not ancient_gz.exists(), "超 24 周压缩档应删除")
        self.assert_true(live.exists(), "活注册表 clusters.json 永不触碰")
        self.assert_eq(st["compressed"], 1, "压缩计数")

    def _test_profile_memory_roll(self):
        self._patch_dirs()
        mem_dir = self.hk.HERMES_PROFILES / "researcher" / "memories"
        mem_dir.mkdir(parents=True)
        mem = mem_dir / "MEMORY.md"
        # 300 条 × 500B ≈ 150KB（超 120KB 上限），尾部最后几条长
        entries = [f"[条目{i}] " + "内" * 150 for i in range(300)]
        entries[-1] = "[最新条目] 最重要的记忆"
        mem.write_text("\n§\n".join(entries) + "\n§\n", encoding="utf-8")
        small = self.hk.HERMES_PROFILES / "critic" / "memories"
        small.mkdir(parents=True)
        small_mem = small / "MEMORY.md"
        small_mem.write_text("少量记忆\n§\n", encoding="utf-8")

        st = self.hk.roll_profile_memory(dry_run=False)

        self.assert_eq(st["rolled"], 1, "仅超限的 researcher 滚动")
        new_text = mem.read_text(encoding="utf-8")
        self.assert_in("[最新条目]", new_text, "最新条目必须保留")
        self.assert_true(
            mem.stat().st_size < self.hk.MEMORY_MAX_BYTES,
            f"滚动后应低于上限，实际 {mem.stat().st_size}")
        archive = mem_dir / f"MEMORY-archive-{datetime.now(timezone.utc):%Y%m%d}.md"
        self.assert_true(archive.exists(), "归档文件应落盘")
        if archive.exists():
            arch_text = archive.read_text(encoding="utf-8")
            self.assert_in("[条目0]", arch_text, "最老条目应进归档（内容不丢失）")
            self.assert_true("[条目0]" not in new_text, "已归档条目不应残留在主文件")
        self.assert_eq(
            small_mem.read_text(encoding="utf-8"), "少量记忆\n§\n",
            "未超限 profile 不动")

    def _test_draft_backup_prune(self):
        self._patch_dirs()
        pd = self.hk.PROPOSALS_ROOT / "optimizing" / "x" / "04_proposal"
        pd.mkdir(parents=True)
        for rn in (1, 2, 3, 4, 5):
            (pd / f"proposal-draft-r{rn}.md").write_text("# r" * 200, encoding="utf-8")
        (pd / "proposal-draft.md").write_text("# current", encoding="utf-8")

        st = self.hk.prune_draft_backups(dry_run=False)

        for rn in (3, 4, 5):
            self.assert_true(
                (pd / f"proposal-draft-r{rn}.md").exists(),
                f"最近 3 版内的 r{rn} 应保留")
        for rn in (1, 2):
            self.assert_true(
                not (pd / f"proposal-draft-r{rn}.md").exists(),
                f"超出 3 版的 r{rn} 应删除")
        self.assert_true((pd / "proposal-draft.md").exists(), "当前版永不删")
        self.assert_eq(st["deleted"], 2, "删除计数")

    def _test_knowledge_bak_clean(self):
        self._patch_dirs()
        kd = self.hk.KNOWLEDGE_DIR
        kd.mkdir(parents=True, exist_ok=True)
        for ts in ("2026-08-01", "2026-08-20", "2026-09-05", "2026-09-20"):
            p = kd / f"categories.json.bak.{ts}"
            p.write_text("{}", encoding="utf-8")
            self._set_age(p, 30)
        # 不同时间戳保证 mtime 排序稳定
        for i, ts in enumerate(("2026-08-01", "2026-08-20", "2026-09-05", "2026-09-20")):
            self._set_age(kd / f"categories.json.bak.{ts}", 40 - i)
        live = kd / "categories.json"
        live.write_text("{}", encoding="utf-8")

        st = self.hk.clean_knowledge_baks(dry_run=False)

        remaining = sorted(kd.glob("categories.json.bak.*"))
        self.assert_eq(len(remaining), 2, "同前缀保留最近 2 个")
        self.assert_true(live.exists(), "正本永不删")
        self.assert_eq(st["deleted"], 2, "删除计数")

    def _test_reading_notes_split(self):
        self._patch_dirs()
        nd = self.hk.PROPOSALS_ROOT / "optimizing" / "y" / "02_literature"
        nd.mkdir(parents=True)
        # 构造 >60KB：每条 ~1KB × 70 条
        lines = []
        for i in range(70):
            lines.append(f"## 论文{i}")
            lines.append("笔记内容" * 120)
            lines.append("")
        notes = nd / "reading-notes.md"
        notes.write_text("\n".join(lines), encoding="utf-8")
        self.assert_true(
            notes.stat().st_size > self.hk.READING_NOTES_MAX_BYTES,
            "前置：测试笔记应超上限")

        st = self.hk.split_reading_notes(dry_run=False)

        new_text = notes.read_text(encoding="utf-8")
        archive = nd / f"reading-notes-archive-{datetime.now(timezone.utc):%Y%m%d}.md"
        self.assert_true(archive.exists(), "归档应落盘")
        self.assert_true(
            notes.stat().st_size <= self.hk.READING_NOTES_MAX_BYTES + 2048,
            f"分割后应接近保留上限，实际 {notes.stat().st_size}")
        self.assert_in("## 论文69", new_text, "最新条目保留")
        self.assert_true("## 论文0" not in new_text, "最老条目应移入归档")
        if archive.exists():
            self.assert_in("## 论文0", archive.read_text(encoding="utf-8"), "旧条目入归档不丢失")
        self.assert_eq(st["split"], 1, "分割计数")

    def run_tests(self):
        self._test_weekend_snapshots()
        self._test_profile_memory_roll()
        self._test_draft_backup_prune()
        self._test_knowledge_bak_clean()
        self._test_reading_notes_split()
