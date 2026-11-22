#!/usr/bin/env python3
"""清理 hermes cron 框架中的同名重复副本。

用途：
    当 lc-daily-orchestrate / lc-repair / lc-hourly-monitor /
    lc-prompt-optimize / lc-retrospective 出现多个同名副本时，
    每类仅保留 created_at 最新的 1 个，删除其余。

    v6.8.30 修复 cron_list_profile 缺失 created_at 字段后，
    cleanup_cron_duplicates 已能正确排序，但因 sandbox 写权限限制，
    需在本机终端手动执行此脚本完成历史副本清理。

用法：
    python3 scripts/cleanup_cron_duplicates.py          # 执行清理
    python3 scripts/cleanup_cron_duplicates.py --dry-run # 预览
"""

import json
import os
import sys
from pathlib import Path

CRON_JOBS_PATH = Path.home() / ".hermes" / "profiles" / "linsai" / "cron" / "jobs.json"

FRAMEWORK_NAMES = [
    "lc-daily-orchestrate",
    "lc-repair",
    "lc-prompt-optimize",
    "lc-retrospective",
    "lc-hourly-monitor",
]


def main(dry_run: bool = False) -> int:
    if not CRON_JOBS_PATH.exists():
        print(f"✗ 文件不存在: {CRON_JOBS_PATH}")
        return 1

    with open(CRON_JOBS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    jobs = data.get("jobs", [])
    print(f"读取 {len(jobs)} 个 cron job")

    # 按 name 分组
    by_name: dict = {}
    other_jobs = []
    for j in jobs:
        name = j.get("name", "")
        if name in FRAMEWORK_NAMES:
            by_name.setdefault(name, []).append(j)
        else:
            other_jobs.append(j)

    # 每类保留 created_at 最大的
    kept = []
    to_remove = []
    for name, group in by_name.items():
        group_sorted = sorted(group, key=lambda c: c.get("created_at", ""))
        kept.append(group_sorted[-1])
        for old in group_sorted[:-1]:
            to_remove.append(old)
            print(
                f"  {'[dry-run] ' if dry_run else ''}删除 {name} "
                f"id={old.get('id')} created={old.get('created_at', '')[:19]}"
            )

    if not to_remove:
        print("✓ 无重复 cron 副本")
        return 0

    print(f"\n共 {len(to_remove)} 个重复副本待删除，保留 {len(kept) + len(other_jobs)} 个 cron")

    if dry_run:
        print("[dry-run] 未实际修改文件")
        return 0

    # 原子写入
    new_jobs = other_jobs + kept
    data["jobs"] = new_jobs
    tmp_path = str(CRON_JOBS_PATH) + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, str(CRON_JOBS_PATH))

    print(f"✓ 已删除 {len(to_remove)} 个重复副本，剩余 {len(new_jobs)} 个 cron")
    return 0


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    sys.exit(main(dry_run=dry))
