#!/usr/bin/env python3
"""数据备份与恢复 —— 用户数据无价，备份优先。

用途：
    将会话、记忆、任务、知识库等用户数据打包为 zip 备份；支持查看备份列表、
    恢复指定备份（恢复前自动创建一份"恢复前"应急备份，防止误覆盖）。

设计原则（见 AGENTS.md「数据安全原则」）：
    - 用户数据无价：sessions / memory / tasks / knowledge 一旦丢失不可重建
    - 备份优先：任何更新操作前必须先备份
    - 恢复可验证：备份包必须能完整恢复
    - 升级可回滚：升级失败时能一键回到之前状态

用法示例：
    >>> # 全量备份（默认）
    >>> python3 scripts/backup_manager.py
    >>> # 查看备份列表
    >>> python3 scripts/backup_manager.py --list
    >>> # 恢复指定备份（会自动创建当前状态的应急备份）
    >>> python3 scripts/backup_manager.py --restore backups/2026-05-08T10-00-00Z.zip
    >>> # 仅备份知识库
    >>> python3 scripts/backup_manager.py --only knowledge

程序化调用（copilot_engine 启动时自动备份）：
    >>> from backup_manager import auto_backup
    >>> path = auto_backup()        # 24h 内已备份则跳过，返回 Path 或 None
    >>> if path: print(path.name)

规范：
    - 仅使用 Python 3 标准库（zipfile / shutil / pathlib）
    - 头部包含中文 docstring
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 输出使用中文，状态图标统一：✓ 成功、✗ 失败、⚠ 警告、○ 待处理、◐ 进行中
    - 时间戳使用 UTC ISO 格式：文件名用 %Y-%m-%dT%H-%M-%SZ（冒号替换为连字符）
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
BACKUPS_DIR = PROJECT_ROOT / "backups"
# 备份范围：用户数据目录（与 .gitignore 排除范围一致 —— 用户数据不进 git，进备份）
BACKUP_TARGETS = ["sessions", "memory", "tasks", "knowledge", "references"]
# 24 小时内已有备份则 auto_backup 跳过（避免每次启动都打包）
AUTO_BACKUP_INTERVAL_HOURS = 24


def _utc_stamp() -> str:
    """返回 UTC ISO 时间戳（文件名安全格式，冒号替换为连字符）。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _ensure_backups_dir() -> Path:
    """确保备份目录存在。"""
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    return BACKUPS_DIR


def _collect_files(targets: list) -> list:
    """收集待备份文件（排除 .DS_Store、__pycache__、.cache 等噪声）。"""
    exclude_names = {".DS_Store", "Thumbs.db", "__pycache__", ".cache"}
    files = []
    for name in targets:
        root = PROJECT_ROOT / name
        if not root.exists():
            continue
        if root.is_file():
            if root.name not in exclude_names:
                files.append(root)
            continue
        for p in root.rglob("*"):
            if any(part in exclude_names for part in p.parts):
                continue
            if p.is_file():
                files.append(p)
    return files


def create_backup(targets: Optional[list] = None, label: str = "") -> Optional[Path]:
    """创建 zip 备份包。

    Args:
        targets: 备份目标子目录名列表；None 表示全量（BACKUP_TARGETS）。
        label: 备份标签，附加到文件名（如 "pre-restore"、"manual"）。

    Returns:
        备份文件 Path；失败返回 None。
    """
    targets = targets or BACKUP_TARGETS
    _ensure_backups_dir()
    stamp = _utc_stamp()
    suffix = "-{}".format(label) if label else ""
    zip_path = BACKUPS_DIR / "{}{}.zip".format(stamp, suffix)

    files = _collect_files(targets)
    if not files:
        print("⚠ 未发现任何待备份数据（项目可能尚未使用）")
        return None

    print("◐ 备份 {} 个文件 → {}".format(len(files), zip_path.name))
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                arcname = f.relative_to(PROJECT_ROOT)
                zf.write(f, arcname)
        size_kb = zip_path.stat().st_size / 1024
        print("✓ 备份完成: {} ({:.1f} KB)".format(zip_path.name, size_kb))
        return zip_path
    except Exception as e:
        print("✗ 备份失败: {}".format(e))
        if zip_path.exists():
            zip_path.unlink()
        return None


def list_backups() -> list:
    """列出所有备份文件（按时间倒序）。"""
    if not BACKUPS_DIR.exists():
        return []
    return sorted(BACKUPS_DIR.glob("*.zip"), reverse=True)


def restore_backup(zip_path) -> bool:
    """从备份恢复数据。

    恢复前自动创建一份当前状态的应急备份，防止误覆盖丢失数据。

    Args:
        zip_path: 备份 zip 文件的路径。

    Returns:
        成功返回 True。
    """
    zip_path = Path(zip_path)
    if not zip_path.exists():
        print("✗ 备份文件不存在: {}".format(zip_path))
        return False

    # 1. 恢复前先备份当前状态（防止恢复错版本）
    print("◐ 恢复前自动创建应急备份...")
    pre_backup = create_backup(label="pre-restore")
    if pre_backup:
        print("  应急备份: {}".format(pre_backup.name))

    # 2. 解压恢复
    print("◐ 从 {} 恢复...".format(zip_path.name))
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(PROJECT_ROOT)
        print("✓ 恢复完成（来自 {}）".format(zip_path.name))
        if pre_backup:
            print("  若需撤销，可用应急备份: {}".format(pre_backup.name))
        return True
    except Exception as e:
        print("✗ 恢复失败: {}".format(e))
        return False


def auto_backup() -> Optional[Path]:
    """自动备份（供 copilot_engine 启动调用）。

    24 小时内已有备份则跳过，避免每次启动都打包。
    失败静默返回 None（不阻塞主流程）。

    Returns:
        新建备份的 Path；跳过或失败返回 None。
    """
    try:
        backups = list_backups()
        if backups:
            newest = backups[0]
            mtime = datetime.fromtimestamp(newest.stat().st_mtime, tz=timezone.utc)
            age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
            if age_hours < AUTO_BACKUP_INTERVAL_HOURS:
                return None  # 近期已备份，跳过
        return create_backup(label="auto")
    except Exception:
        return None


def _self_check() -> None:
    """自检：创建→列表→完整性校验→清理临时备份。"""
    print("◐ backup_manager 自检...")
    before = len(list_backups())
    tmp = create_backup(label="selfcheck")
    assert tmp is not None and tmp.exists(), "备份创建失败"
    backups = list_backups()
    assert len(backups) == before + 1, "备份未出现在列表中"
    # 验证 zip 可读
    with zipfile.ZipFile(tmp, "r") as zf:
        assert zf.testzip() is None, "zip 完整性校验失败"
    # 清理临时备份
    tmp.unlink()
    assert len(list_backups()) == before, "清理后备份数量异常"
    print("✓ backup_manager 自检通过")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LinSai-CoPilot 数据备份/恢复",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="用户数据无价，备份优先。",
    )
    parser.add_argument("--list", action="store_true", help="列出所有备份")
    parser.add_argument("--restore", metavar="FILE", help="从指定 zip 恢复（会先创建应急备份）")
    parser.add_argument(
        "--only",
        metavar="DIR",
        help="仅备份指定目录（可选: {}）".format(", ".join(BACKUP_TARGETS)),
    )
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return

    if args.list:
        backups = list_backups()
        if not backups:
            print("○ 暂无备份")
            return
        print("\n{:<42} {:<12} {}".format("备份文件", "大小", "时间"))
        print("-" * 75)
        for b in backups:
            size = "{:.1f} KB".format(b.stat().st_size / 1024)
            mtime = datetime.fromtimestamp(b.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            print("{:<42} {:<12} {}".format(b.name, size, mtime))
        print()
        return

    if args.restore:
        restore_backup(Path(args.restore))
        return

    if args.only:
        if args.only not in BACKUP_TARGETS:
            print("✗ 未知目录: {}（可选: {}）".format(args.only, ", ".join(BACKUP_TARGETS)))
            sys.exit(1)
        create_backup(targets=[args.only])
        return

    # 默认：全量备份
    create_backup()


if __name__ == "__main__":
    main()
