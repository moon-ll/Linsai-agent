#!/usr/bin/env python3
"""housekeeping.py — 数据域滚动治理守护（v6.10.42）。

背景（09-24 用户提出"持续膨胀文档需要分割+滚动释放"）：全库审计确认
已有机制覆盖 linsai.log（30 天轮转）、method-manual（v6.10.41 软上限）、
kanban execution_history（200 条）、error_history（10 条）、
processed_sources（28 天）——但五类文件持续膨胀无治理：

    1. memory/weekend-input/sources-*.json 周快照：每周 2-4.5MB，实测
       12+ 个累计约 30MB，无任何清理；
    2. ~/.hermes/profiles/*/memories/MEMORY.md：纯追加，researcher 已
       183KB/1183 条（其中 430+ 条是 job 完成日志噪音）；
    3. research_proposals/*/04_proposal/proposal-draft-rN.md 轮次备份：
       每轮 100KB+，r1-rN 无限累积（git 历史已有，可安全裁剪）；
    4. knowledge/*.bak* 手工备份（graph/categories）：累积无清理；
    5. reading-notes.md：writer 每轮追加，实测 27-51KB 持续增长。

治理原则（保守）：
    - 可再生数据（轮次备份/手工 bak）超限直接删除；
    - 资产类数据（周快照/记忆/笔记）只做"归档分割"——gzip 压缩或移入
      archive 文件，不删除内容；
    - 全程 dry-run 预览 + apply 落地双模式，输出中文统计。

用法：
    python3 scripts/housekeeping.py --dry-run    # 预览
    python3 scripts/housekeeping.py --apply      # 执行
    python3 scripts/housekeeping.py --status     # 各域体积概览
    python3 scripts/housekeeping.py --self-check

挂接：kb_auto_sync.run_sync() 尾部每日调用（12:40 cron lc-kb-sync）。
"""

from __future__ import annotations

import argparse
import gzip
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from common import now_utc  # noqa: E402
from paths import PROJECT_ROOT  # noqa: E402

try:
    from logger import get_logger
    _log = get_logger("housekeeping")
except Exception:
    _log = None

# ── 策略常量（集中声明，便于调参） ────────────────────────────────
WEEKEND_INPUT_DIR = PROJECT_ROOT / "memory" / "weekend-input"
PROPOSALS_ROOT = PROJECT_ROOT / "research_proposals"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
HERMES_PROFILES = Path.home() / ".hermes" / "profiles"

# 1. weekend-input 周快照：>8 周 gzip 压缩，>24 周删除压缩档
SNAPSHOT_RETAIN_DAYS = 56
SNAPSHOT_ARCHIVE_DAYS = 168
SNAPSHOT_PATTERNS = [
    "sources-*.json", "summaries-*.json", "distilled-clusters-*.json",
    "clusters-week-*.json", "ideas-*.json", "decisions-*.json",
    "directions-*.json", "deep-read-*.json", "briefings-*.json",
]
# 活文件（注册表/管线状态，永不触碰）
SNAPSHOT_EXACT_KEEP = {"clusters.json", "weekend-pipeline.json", "scope-terms.json"}

# 2. profile MEMORY.md：>120KB 或 >900 条时滚动；保留"尾部累计 ≥40KB
#    或 ≥200 条"（取先到者）——按字节切而非按条数切（v6.10.42 首版按
#    条数切实测 859→500 条仅 196KB→192KB，长条目全在保留区，无效）。
MEMORY_MAX_BYTES = 120_000
MEMORY_MAX_ENTRIES = 900
MEMORY_KEEP_BYTES = 40_000
MEMORY_MIN_KEEP_ENTRIES = 200
MEMORY_SEPARATOR = "\n§\n"

# 3. 课题 draft 轮次备份：保留最近 3 版
DRAFT_BACKUP_KEEP = 3

# 4. knowledge 手工 bak：同前缀保留最近 2 个
KNOWLEDGE_BAK_KEEP = 2

# 5. reading-notes：>60KB 分割，保留最近 40KB（条目边界）
READING_NOTES_MAX_BYTES = 60_000
READING_NOTES_KEEP_BYTES = 40_000


def _age_days(path: Path) -> float:
    """文件修改时间距今天数。"""
    return (datetime.now(timezone.utc) - datetime.fromtimestamp(
        path.stat().st_mtime, timezone.utc)).total_seconds() / 86400


def _fmt(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / 1024 / 1024:.1f}MB"
    return f"{size_bytes / 1024:.0f}KB"


# ── 1. weekend-input 周快照滚动 ─────────────────────────────────
def roll_weekend_snapshots(dry_run: bool = True) -> Dict[str, Any]:
    """周快照：超 8 周 gzip 压缩，压缩档超 24 周删除。

    v6.10.42 修复：首版用 glob(SNAPSHOT_PATTERNS) 扫描，但压缩档
    `sources-*.json.gz` 后缀不匹配 `sources-*.json`，导致压缩档永远
    无法进入超龄删除分支（测试实测捕获）。改为 iterdir + fnmatch：
    去掉 .gz 后缀再匹配模式，.json 与 .json.gz 统一治理。
    """
    import fnmatch
    stats = {"compressed": 0, "deleted": 0, "freed": 0, "skipped": 0}
    if not WEEKEND_INPUT_DIR.exists():
        return stats
    for path in sorted(WEEKEND_INPUT_DIR.iterdir()):
        if not path.is_file() or path.name in SNAPSHOT_EXACT_KEEP:
            continue
        name = path.name
        is_gz = name.endswith(".gz")
        base_name = name[:-3] if is_gz else name
        if not any(fnmatch.fnmatch(base_name, pat) for pat in SNAPSHOT_PATTERNS):
            continue
        age = _age_days(path)
        if is_gz:
            if age > SNAPSHOT_ARCHIVE_DAYS:
                if dry_run:
                    stats["deleted"] += 1
                    stats["freed"] += path.stat().st_size
                    continue
                try:
                    size = path.stat().st_size
                    path.unlink()
                    stats["deleted"] += 1
                    stats["freed"] += size
                except Exception as e:
                    if _log:
                        _log.warning(f"[housekeeping] 删除超龄压缩档失败 {name}: {e}")
                    stats["skipped"] += 1
            else:
                stats["skipped"] += 1
            continue
        # 原始 .json
        if age > SNAPSHOT_RETAIN_DAYS:
            gz_path = path.with_suffix(path.suffix + ".gz")
            if dry_run:
                stats["compressed"] += 1
                stats["freed"] += int(path.stat().st_size * 0.85)
                continue
            try:
                with open(path, "rb") as f_in, gzip.open(gz_path, "wb", compresslevel=6) as f_out:
                    shutil.copyfileobj(f_in, f_out)
                stats["compressed"] += 1
                stats["freed"] += int(path.stat().st_size * 0.85)
                path.unlink()
            except Exception as e:
                if _log:
                    _log.warning(f"[housekeeping] 压缩失败 {name}: {e}")
                stats["skipped"] += 1
        else:
            stats["skipped"] += 1
    return stats


# ── 2. hermes profile MEMORY.md 滚动 ────────────────────────────
def roll_profile_memory(dry_run: bool = True) -> Dict[str, Any]:
    """MEMORY.md 超限滚动：旧条目移入 MEMORY-archive-{date}.md（不删除）。

    保留策略：从最后一条向前累计字节，凑满 MEMORY_KEEP_BYTES（40KB）即
    停（至少 MEMORY_MIN_KEEP_ENTRIES 条）；此前所有条目归档。
    """
    stats = {"rolled": 0, "entries_archived": 0, "profiles": []}
    if not HERMES_PROFILES.exists():
        return stats
    for mem_path in HERMES_PROFILES.glob("*/memories/MEMORY.md"):
        try:
            text = mem_path.read_text(encoding="utf-8")
        except Exception:
            continue
        entries = [e.strip() for e in text.split(MEMORY_SEPARATOR) if e.strip()]
        size = mem_path.stat().st_size
        if size <= MEMORY_MAX_BYTES and len(entries) <= MEMORY_MAX_ENTRIES:
            continue
        # 从尾部累计保留字节
        keep_count = 0
        acc = 0
        for e in reversed(entries):
            acc += len(e.encode("utf-8"))
            keep_count += 1
            if acc >= MEMORY_KEEP_BYTES and keep_count >= MEMORY_MIN_KEEP_ENTRIES:
                break
            if keep_count >= len(entries):
                break
        if keep_count >= len(entries):
            continue  # 全部保留也凑不满 40KB（条数少体积大），不动
        archive_entries = entries[:-keep_count]
        keep_text = MEMORY_SEPARATOR.join(entries[-keep_count:]) + "\n§\n"
        archive_path = mem_path.parent / f"MEMORY-archive-{datetime.now(timezone.utc):%Y%m%d}.md"
        if dry_run:
            stats["rolled"] += 1
            stats["entries_archived"] += len(archive_entries)
            stats["profiles"].append(
                f"{mem_path.parent.parent.name}({len(entries)}→{keep_count}条,"
                f"{_fmt(size)}→{_fmt(len(keep_text.encode()))})")
            continue
        try:
            if archive_path.exists():
                old = archive_path.read_text(encoding="utf-8")
                archive_path.write_text(
                    old + MEMORY_SEPARATOR.join(archive_entries) + "\n§\n", encoding="utf-8")
            else:
                archive_path.write_text(
                    MEMORY_SEPARATOR.join(archive_entries) + "\n§\n", encoding="utf-8")
            mem_path.write_text(keep_text, encoding="utf-8")
            stats["rolled"] += 1
            stats["entries_archived"] += len(archive_entries)
            stats["profiles"].append(
                f"{mem_path.parent.parent.name}(归档{len(archive_entries)}条→{archive_path.name})")
        except Exception as e:
            if _log:
                _log.warning(f"[housekeeping] MEMORY 滚动失败 {mem_path}: {e}")
    return stats


# ── 3. 课题 draft 轮次备份裁剪 ──────────────────────────────────
def prune_draft_backups(dry_run: bool = True) -> Dict[str, Any]:
    """proposal-draft-rN.md 保留最近 3 版（git 历史兜底，可再生）。"""
    stats = {"deleted": 0, "freed": 0}
    if not PROPOSALS_ROOT.exists():
        return stats
    for draft_path in PROPOSALS_ROOT.glob("*/**/04_proposal/proposal-draft-r*.md"):
        m = re.match(r".*proposal-draft-r(\d+)\.md$", str(draft_path))
        if not m:
            continue
        rn = int(m.group(1))
        # 同目录最大轮次
        siblings = [int(x.group(1)) for x in (
            re.match(r".*proposal-draft-r(\d+)\.md$", str(p))
            for p in draft_path.parent.glob("proposal-draft-r*.md")) if x]
        if not siblings:
            continue
        if max(siblings) - rn < DRAFT_BACKUP_KEEP:
            continue  # 最近 3 版保留
        if dry_run:
            stats["deleted"] += 1
            stats["freed"] += draft_path.stat().st_size
            continue
        try:
            size = draft_path.stat().st_size
            draft_path.unlink()
            stats["deleted"] += 1
            stats["freed"] += size
        except Exception as e:
            if _log:
                _log.warning(f"[housekeeping] 删除轮次备份失败 {draft_path}: {e}")
    return stats


# ── 4. knowledge 手工 bak 清理 ───────────────────────────────────
def clean_knowledge_baks(dry_run: bool = True) -> Dict[str, Any]:
    """同名前缀 bak 保留最近 2 个。"""
    stats = {"deleted": 0, "freed": 0}
    if not KNOWLEDGE_DIR.exists():
        return stats
    from collections import defaultdict
    groups: Dict[str, List[Path]] = defaultdict(list)
    for p in KNOWLEDGE_DIR.iterdir():
        if not p.is_file():
            continue
        name = p.name
        # 归组：base + bak 标识（categories.json.bak.2026-09-13 / graph.json.bak-kbhealth-20260923）
        m = re.match(r"^(.*?)\.bak.*$", name)
        if m:
            groups[m.group(1)].append(p)
    for base, paths in groups.items():
        paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for p in paths[KNOWLEDGE_BAK_KEEP:]:
            if dry_run:
                stats["deleted"] += 1
                stats["freed"] += p.stat().st_size
                continue
            try:
                size = p.stat().st_size
                p.unlink()
                stats["deleted"] += 1
                stats["freed"] += size
            except Exception as e:
                if _log:
                    _log.warning(f"[housekeeping] 删除 bak 失败 {p}: {e}")
    return stats


# ── 5. reading-notes 分割 ───────────────────────────────────────
def split_reading_notes(dry_run: bool = True) -> Dict[str, Any]:
    """>60KB 的阅读笔记：旧段移入 reading-notes-archive-{date}.md。"""
    stats = {"split": 0, "archived_bytes": 0, "proposals": []}
    if not PROPOSALS_ROOT.exists():
        return stats
    for notes_path in PROPOSALS_ROOT.glob("*/**/02_literature/reading-notes.md"):
        try:
            text = notes_path.read_text(encoding="utf-8")
        except Exception:
            continue
        size = len(text.encode("utf-8"))
        if size <= READING_NOTES_MAX_BYTES:
            continue
        # 从保留边界之后的条目边界（## 开头行）切分
        cut_char = 0
        for i, line in enumerate(text.split("\n")):
            pass
        lines = text.split("\n")
        # 找到使保留部分 ≥ KEEP_BYTES 的最早 ## 边界
        acc = 0
        boundary_idx = len(lines)
        boundaries = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
        for bi in boundaries:
            prefix_len = len("\n".join(lines[:bi]).encode("utf-8"))
            if prefix_len >= size - READING_NOTES_KEEP_BYTES:
                boundary_idx = bi
                break
        if boundary_idx >= len(lines):
            continue  # 无合适边界（单条超长），跳过
        archive_text = "\n".join(lines[:boundary_idx])
        keep_text = "\n".join(lines[boundary_idx:])
        archive_path = notes_path.parent / f"reading-notes-archive-{datetime.now(timezone.utc):%Y%m%d}.md"
        if dry_run:
            stats["split"] += 1
            stats["archived_bytes"] += len(archive_text.encode("utf-8"))
            stats["proposals"].append(
                f"{notes_path.parent.parent.name}({_fmt(size)}→{_fmt(len(keep_text.encode()))})")
            continue
        try:
            if archive_path.exists():
                old = archive_path.read_text(encoding="utf-8")
                archive_path.write_text(archive_text + "\n\n---\n\n" + old, encoding="utf-8")
            else:
                archive_path.write_text(archive_text, encoding="utf-8")
            notes_path.write_text(keep_text, encoding="utf-8")
            stats["split"] += 1
            stats["archived_bytes"] += len(archive_text.encode("utf-8"))
            stats["proposals"].append(f"{notes_path.parent.parent.name}(旧段→{archive_path.name})")
        except Exception as e:
            if _log:
                _log.warning(f"[housekeeping] 笔记分割失败 {notes_path}: {e}")
    return stats


# ── 总入口 ──────────────────────────────────────────────────────
def run_all(dry_run: bool = True) -> Dict[str, Any]:
    report = {
        "mode": "dry_run" if dry_run else "apply",
        "weekend_snapshots": roll_weekend_snapshots(dry_run),
        "profile_memory": roll_profile_memory(dry_run),
        "draft_backups": prune_draft_backups(dry_run),
        "knowledge_baks": clean_knowledge_baks(dry_run),
        "reading_notes": split_reading_notes(dry_run),
    }
    return report


def show_status() -> None:
    print("=== 数据域体积概览 ===")
    for name, path in [
        ("logs/", PROJECT_ROOT / "logs"),
        ("memory/weekend-input/", WEEKEND_INPUT_DIR),
        ("research_proposals/", PROPOSALS_ROOT),
        ("knowledge/(*.bak)", KNOWLEDGE_DIR),
    ]:
        if not path.exists():
            print(f"  {name}: 不存在")
            continue
        if name.endswith("(*.bak)"):
            total = sum(p.stat().st_size for p in path.glob("*.bak*") if p.is_file())
            print(f"  {name}: {_fmt(total)}")
        else:
            total = sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
            print(f"  {name}: {_fmt(total)}")
    mem = HERMES_PROFILES / "researcher" / "memories" / "MEMORY.md"
    if mem.exists():
        text = mem.read_text(encoding="utf-8")
        print(f"  hermes researcher MEMORY.md: {_fmt(mem.stat().st_size)} / {len(text.split(MEMORY_SEPARATOR))} 条")


def _self_check() -> List[str]:
    """自检：策略常量合法 + 各治理函数在临时目录冒烟。"""
    errors: List[str] = []
    import tempfile
    globals_backup = {
        "WEEKEND_INPUT_DIR": WEEKEND_INPUT_DIR, "PROPOSALS_ROOT": PROPOSALS_ROOT,
        "KNOWLEDGE_DIR": KNOWLEDGE_DIR, "HERMES_PROFILES": HERMES_PROFILES,
    }
    try:
        with tempfile.TemporaryDirectory(prefix="hk_check_") as td:
            tmp = Path(td)
            # 快照滚动冒烟：造一个 60+ 天前的旧快照
            wi = tmp / "weekend-input"
            wi.mkdir()
            old = wi / "sources-2026-01-01.json"
            old.write_text("[]" * 1000, encoding="utf-8")
            import os
            old_time = datetime.now(timezone.utc).timestamp() - 60 * 86400
            os.utime(old, (old_time, old_time))
            globals()["WEEKEND_INPUT_DIR"] = wi
            st = roll_weekend_snapshots(dry_run=False)
            if st["compressed"] != 1 or not old.with_suffix(".json.gz").exists():
                errors.append(f"快照压缩冒烟失败: {st}")
            # draft 裁剪冒烟
            pr = tmp / "proposals"
            pd = pr / "optimizing" / "x" / "04_proposal"
            pd.mkdir(parents=True)
            for rn in (1, 2, 3, 4, 5, 6):
                (pd / f"proposal-draft-r{rn}.md").write_text("# r" * 500, encoding="utf-8")
            globals()["PROPOSALS_ROOT"] = pr
            st2 = prune_draft_backups(dry_run=False)
            if st2["deleted"] != 3:  # r1-r3 删，r4-r6 留
                errors.append(f"draft 裁剪冒烟失败: {st2}")
        if errors:
            return errors
        print("✓ 自检通过")
    except Exception as e:
        errors.append(f"自检异常: {e}")
    finally:
        for k, v in globals_backup.items():
            globals()[k] = v
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="数据域滚动治理守护")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="预览（默认）")
    mode.add_argument("--apply", action="store_true", help="执行")
    mode.add_argument("--status", action="store_true", help="体积概览")
    mode.add_argument("--self-check", action="store_true", help="自检")
    args = parser.parse_args()

    if args.self_check:
        errs = _self_check()
        for e in errs:
            print(f"✗ {e}")
        sys.exit(1 if errs else 0)
    if args.status:
        show_status()
        return

    dry = not args.apply
    print(f"=== 滚动治理（{'预览' if dry else '执行'}）===")
    report = run_all(dry_run=dry)
    ws = report["weekend_snapshots"]
    print(f"1. 周末快照: 压缩 {ws['compressed']} 个 / 删除超龄压缩档 {ws['deleted']} 个 / 释放约 {_fmt(ws['freed'])}")
    pm = report["profile_memory"]
    print(f"2. profile 记忆: 滚动 {pm['rolled']} 个 / 归档 {pm['entries_archived']} 条")
    for p in pm["profiles"]:
        print(f"   - {p}")
    db = report["draft_backups"]
    print(f"3. draft 轮次备份: 删除 {db['deleted']} 个 / 释放 {_fmt(db['freed'])}")
    kb = report["knowledge_baks"]
    print(f"4. knowledge bak: 删除 {kb['deleted']} 个 / 释放 {_fmt(kb['freed'])}")
    rn = report["reading_notes"]
    print(f"5. 阅读笔记: 分割 {rn['split']} 个 / 归档 {_fmt(rn['archived_bytes'])}")
    for p in rn["proposals"]:
        print(f"   - {p}")
    if dry:
        print("\n（预览模式，加 --apply 执行）")


if __name__ == "__main__":
    main()
