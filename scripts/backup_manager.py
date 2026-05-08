#!/usr/bin/env python3
"""备份管理器 — 保护用户数据不因代码更新而丢失。

用法:
    python3 scripts/backup_manager.py              # 创建备份
    python3 scripts/backup_manager.py --list       # 列出备份
    python3 scripts/backup_manager.py --restore PATH  # 恢复指定备份
    python3 scripts/backup_manager.py --auto       # 自动模式（24h内只备份一次）
    python3 scripts/backup_manager.py --cleanup    # 清理旧备份（保留最近10个）

备份内容:
    sessions/   对话记录与会话状态
    memory/     用户画像、工作上下文、记忆片段
    tasks/      任务数据
    references/ 文献索引与笔记

备份位置: backups/YYYY-MM-DDTHH-MM-SS.zip
"""

import argparse
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
_BACKUPS_DIR = _PROJECT_ROOT / "backups"

# 需要备份的用户数据目录（相对项目根目录）
_DATA_DIRS = ["sessions", "memory", "tasks", "references"]

# 自动备份间隔（小时）
_AUTO_BACKUP_INTERVAL_HOURS = 24

# 默认保留备份数量
_DEFAULT_KEEP_COUNT = 10

# 备份大小警告阈值（MB）
_SIZE_WARNING_MB = 100


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _format_size(size_bytes: int) -> str:
    """将字节数转为人类可读格式。"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _count_data_files() -> dict:
    """统计各数据目录下的文件数量与总大小。"""
    stats = {}
    for name in _DATA_DIRS:
        d = _PROJECT_ROOT / name
        if not d.exists():
            stats[name] = {"files": 0, "size": 0}
            continue
        files = list(d.rglob("*"))
        file_count = sum(1 for f in files if f.is_file())
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        stats[name] = {"files": file_count, "size": total_size}
    return stats


# ---------------------------------------------------------------------------
# 核心功能
# ---------------------------------------------------------------------------

def create_backup(label: str = "") -> Path:
    """创建备份，返回备份文件路径。

    Args:
        label: 可选标签，附加到文件名中便于识别。
    """
    _ensure_dir(_BACKUPS_DIR)
    timestamp = _now_str()
    label_part = f"-{label}" if label else ""
    backup_path = _BACKUPS_DIR / f"{timestamp}{label_part}.zip"

    stats_before = _count_data_files()
    total_files = sum(s["files"] for s in stats_before.values())

    if total_files == 0:
        print("⚠ 未检测到用户数据，跳过备份。")
        return backup_path

    print(f"◐ 正在备份 {total_files} 个文件 …")

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in _DATA_DIRS:
            src_dir = _PROJECT_ROOT / name
            if not src_dir.exists():
                continue
            for fpath in src_dir.rglob("*"):
                if fpath.is_file():
                    arcname = fpath.relative_to(_PROJECT_ROOT)
                    zf.write(fpath, arcname)

    size = backup_path.stat().st_size
    print(f"✓ 备份完成: {backup_path.relative_to(_PROJECT_ROOT)}")
    print(f"  大小: {_format_size(size)}")
    for name, s in stats_before.items():
        if s["files"] > 0:
            print(f"  {name}: {s['files']} 个文件, {_format_size(s['size'])}")

    if size > _SIZE_WARNING_MB * 1024 * 1024:
        print(f"⚠ 备份体积超过 {_SIZE_WARNING_MB}MB，"
              f"建议清理 references/papers/ 中的大文件。")

    # 记录自动备份时间戳
    _record_auto_backup_time()
    return backup_path


def _record_auto_backup_time() -> None:
    """记录最近一次自动备份的时间。"""
    meta_path = _BACKUPS_DIR / ".auto-backup-meta.json"
    data = {"last_auto_backup": datetime.now(timezone.utc).isoformat()}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_last_auto_backup_time() -> Optional[datetime]:
    """获取最近一次自动备份的时间。"""
    meta_path = _BACKUPS_DIR / ".auto-backup-meta.json"
    if not meta_path.exists():
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return datetime.fromisoformat(data["last_auto_backup"])
    except Exception:
        return None


def auto_backup(min_interval_hours: int = _AUTO_BACKUP_INTERVAL_HOURS) -> Optional[Path]:
    """自动备份：距上次备份超过指定小时数才执行。

    Returns:
        备份文件路径，或 None（跳过）。
    """
    last = _get_last_auto_backup_time()
    if last is not None:
        elapsed = (datetime.now(timezone.utc) - last).total_seconds() / 3600
        if elapsed < min_interval_hours:
            return None
    return create_backup(label="auto")


def list_backups() -> List[Path]:
    """列出所有备份，按时间排序（最新的在最后）。"""
    if not _BACKUPS_DIR.exists():
        print("○ 尚无备份目录。")
        return []

    backups = sorted(
        [p for p in _BACKUPS_DIR.iterdir() if p.suffix == ".zip"],
        key=lambda p: p.stat().st_mtime,
    )

    if not backups:
        print("○ 尚无备份。")
        return []

    print(f"{'序号':>4}  {'时间':<22}  {'大小':>10}  {'文件名'}")
    print("-" * 70)
    for i, bp in enumerate(backups, 1):
        size = _format_size(bp.stat().st_size)
        mtime = datetime.fromtimestamp(
            bp.stat().st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i:>4}  {mtime:<22}  {size:>10}  {bp.name}")
    print(f"\n总计 {len(backups)} 个备份，"
          f"占用 {_format_size(sum(b.stat().st_size for b in backups))}")
    return backups


def restore_backup(backup_path: Path) -> bool:
    """恢复备份。先创建当前状态的应急备份，再解压覆盖。

    Returns:
        是否成功。
    """
    if not backup_path.exists():
        print(f"✗ 备份文件不存在: {backup_path}")
        return False

    # 先创建应急备份
    print("◐ 创建应急备份（当前状态）…")
    emergency = create_backup(label="pre-restore")

    print(f"◐ 正在恢复: {backup_path.name} …")
    with zipfile.ZipFile(backup_path, "r") as zf:
        zf.extractall(_PROJECT_ROOT)

    print("✓ 恢复完成。")
    print(f"  应急备份: {emergency.name}")
    print("  如需回滚，运行:")
    print(f"    python3 scripts/backup_manager.py --restore {emergency}")
    return True


def cleanup_old_backups(keep: int = _DEFAULT_KEEP_COUNT) -> int:
    """清理旧备份，保留最近 N 个。返回删除数量。"""
    if not _BACKUPS_DIR.exists():
        return 0

    backups = sorted(
        [p for p in _BACKUPS_DIR.iterdir() if p.suffix == ".zip"],
        key=lambda p: p.stat().st_mtime,
    )

    if len(backups) <= keep:
        print(f"○ 备份数量 ({len(backups)}) 未超过保留上限 ({keep})，无需清理。")
        return 0

    to_remove = backups[:-keep]
    removed_size = 0
    for bp in to_remove:
        removed_size += bp.stat().st_size
        bp.unlink()

    print(f"✓ 已清理 {len(to_remove)} 个旧备份，"
          f"释放 {_format_size(removed_size)}。")
    print(f"  保留最近 {keep} 个备份。")
    return len(to_remove)


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> bool:
    """运行模块级自检。"""
    ok = True

    # 1. 路径常量正确推导
    if _PROJECT_ROOT.name != "LinSai-CoPilot":
        print("✗ PROJECT_ROOT 推导异常")
        ok = False
    else:
        print("✓ PROJECT_ROOT 推导正确")

    # 2. 备份目录可创建
    _ensure_dir(_BACKUPS_DIR)
    if _BACKUPS_DIR.exists():
        print("✓ 备份目录可创建")
    else:
        print("✗ 备份目录创建失败")
        ok = False

    # 3. 空数据时优雅处理
    stats = _count_data_files()
    total = sum(s["files"] for s in stats.values())
    print(f"✓ 数据文件统计: {total} 个文件")

    # 4. 备份/恢复/清理流程
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        # 模拟创建一些数据
        (tmp_root / "sessions" / "test").mkdir(parents=True)
        (tmp_root / "sessions" / "test" / "messages.json").write_text("[]")

        # 临时替换常量测试
        orig_backups_dir = globals()["_BACKUPS_DIR"]
        globals()["_BACKUPS_DIR"] = tmp_root / "backups"
        globals()["_PROJECT_ROOT"] = tmp_root

        bp = create_backup(label="test")
        if bp.exists():
            print("✓ 备份创建成功")
        else:
            print("✗ 备份创建失败")
            ok = False

        backups = list_backups()
        if len(backups) == 1:
            print("✓ 备份列表正确")
        else:
            print("✗ 备份列表异常")
            ok = False

        # 修改数据后恢复
        (tmp_root / "sessions" / "test" / "messages.json").write_text("[1]")
        if restore_backup(bp):
            content = (tmp_root / "sessions" / "test" / "messages.json").read_text()
            if content == "[]":
                print("✓ 恢复功能正确")
            else:
                print("✗ 恢复后数据不匹配")
                ok = False
        else:
            ok = False

        cleanup_old_backups(keep=5)
        if not (tmp_root / "backups" / bp.name).exists():
            print("✗ 清理误删了备份")
            ok = False
        else:
            print("✓ 清理保留策略正确")

        # 恢复常量
        globals()["_BACKUPS_DIR"] = orig_backups_dir
        globals()["_PROJECT_ROOT"] = _SCRIPT_DIR.parent.resolve()

    return ok


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="LinSai-CoPilot 备份管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/backup_manager.py              # 手动备份
  python3 scripts/backup_manager.py --auto       # 自动备份（24h间隔）
  python3 scripts/backup_manager.py --list       # 查看备份列表
  python3 scripts/backup_manager.py --restore backups/2026-05-08T10-00-00Z.zip
  python3 scripts/backup_manager.py --cleanup    # 清理旧备份
  python3 scripts/backup_manager.py --self-check # 运行自检
        """,
    )
    parser.add_argument("--list", action="store_true", help="列出所有备份")
    parser.add_argument("--restore", metavar="PATH", help="恢复指定备份")
    parser.add_argument("--auto", action="store_true", help="自动备份模式")
    parser.add_argument("--cleanup", action="store_true", help="清理旧备份")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)

    if args.self_check:
        print("=== 备份管理器自检 ===")
        ok = _self_check()
        print("-" * 30)
        print("✓ 全部通过" if ok else "✗ 存在失败项")
        return 0 if ok else 1

    if args.list:
        list_backups()
        return 0

    if args.restore:
        path = Path(args.restore)
        if not path.is_absolute():
            path = _PROJECT_ROOT / path
        restore_backup(path)
        return 0

    if args.cleanup:
        cleanup_old_backups()
        return 0

    if args.auto:
        result = auto_backup()
        if result is None:
            print("○ 距上次自动备份不足24小时，跳过。")
        return 0

    # 默认：手动创建备份
    create_backup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
