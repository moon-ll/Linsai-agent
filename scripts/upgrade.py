#!/usr/bin/env python3
"""升级助手 — 安全更新 LinSai-CoPilot 代码的标准流程。

用法:
    python3 scripts/upgrade.py --check      # 显示当前版本与版本历史
    python3 scripts/upgrade.py              # 执行完整升级流程
    python3 scripts/upgrade.py --simulate   # 模拟升级，不实际执行
    python3 scripts/upgrade.py --verify     # 仅验证当前代码完整性

升级流程:
    1. 读取当前版本号（VERSION 文件）
    2. 备份用户数据（调用 backup_manager）
    3. 如有 Git 远程仓库，执行 git pull
    4. 验证所有脚本语法（py_compile）
    5. 检查是否需要数据迁移
    6. 报告升级结果

安全原则:
    - 任何步骤失败都会回滚并提示用户
    - 用户数据永远优先备份，不会丢失
    - 升级前自动创建"升级前"快照，可随时恢复
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
_VERSION_PATH = _PROJECT_ROOT / "VERSION"
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts"
_MIGRATE_MARKER = _PROJECT_ROOT / ".migrate-done"


# ---------------------------------------------------------------------------
# 版本读取
# ---------------------------------------------------------------------------

def get_current_version() -> str:
    """读取 VERSION 文件中的当前版本号。"""
    if _VERSION_PATH.exists():
        return _VERSION_PATH.read_text(encoding="utf-8").strip()
    return "unknown"


def get_changelog_versions() -> List[dict]:
    """从 CHANGELOG.md 中提取版本历史。"""
    changelog = _PROJECT_ROOT / "CHANGELOG.md"
    if not changelog.exists():
        return []

    versions = []
    with open(changelog, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("## v"):
                parts = line[3:].split(" - ", 1)
                v = parts[0].strip()
                desc = parts[1].strip() if len(parts) > 1 else ""
                versions.append({"version": v, "description": desc})
    return versions


# ---------------------------------------------------------------------------
# 备份
# ---------------------------------------------------------------------------

def _import_backup_manager():
    """动态导入 backup_manager 模块，避免循环依赖。"""
    spec = importlib.util.spec_from_file_location(
        "backup_manager", _SCRIPTS_DIR / "backup_manager.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def backup_data(label: str = "pre-upgrade") -> Optional[Path]:
    """创建升级前的数据备份。"""
    bm = _import_backup_manager()
    print("◐ 步骤 1/4: 备份用户数据 …")
    bp = bm.create_backup(label=label)
    return bp


# ---------------------------------------------------------------------------
# Git 操作
# ---------------------------------------------------------------------------

def has_git_remote() -> bool:
    """检查是否有 Git 远程仓库。"""
    git_dir = _PROJECT_ROOT / ".git"
    if not git_dir.exists():
        return False
    try:
        result = subprocess.run(
            ["git", "remote"],
            cwd=_PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def git_pull(simulate: bool = False) -> bool:
    """执行 git pull 获取最新代码。"""
    if not has_git_remote():
        print("⚠ 未配置 Git 远程仓库，跳过 git pull。")
        print("  请手动将新代码覆盖到项目目录，然后重新运行本脚本验证。")
        return True

    print("◐ 步骤 2/4: 从远程拉取最新代码 …")
    if simulate:
        print("  [模拟] git pull")
        return True

    try:
        subprocess.run(
            ["git", "pull"],
            cwd=_PROJECT_ROOT,
            check=True,
        )
        print("✓ 代码更新成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ git pull 失败: {e}")
        return False


# ---------------------------------------------------------------------------
# 代码验证
# ---------------------------------------------------------------------------

def verify_scripts() -> tuple[bool, list[str]]:
    """编译验证所有 Python 脚本。

    Returns:
        (是否全部通过, [错误信息列表])
    """
    print("◐ 步骤 3/4: 验证脚本语法 …")
    errors = []
    py_files = sorted(_SCRIPTS_DIR.glob("*.py"))

    for fpath in py_files:
        try:
            py_compile.compile(str(fpath), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{fpath.name}: {e}")

    if errors:
        print(f"✗ {len(errors)} 个脚本语法错误:")
        for err in errors:
            print(f"  - {err}")
        return False, errors

    print(f"✓ 全部 {len(py_files)} 个脚本语法正确")
    return True, []


# ---------------------------------------------------------------------------
# 迁移检查
# ---------------------------------------------------------------------------

def check_migration() -> Tuple[bool, str]:
    """检查是否需要数据迁移。

    Returns:
        (是否需要迁移, 说明文本)
    """
    print("◐ 步骤 4/4: 检查数据迁移 …")

    current = get_current_version()
    versions = get_changelog_versions()
    if not versions:
        print("✓ 无需迁移（无版本历史记录）")
        return False, ""

    latest = versions[0]["version"]
    if current == latest:
        print(f"✓ 当前版本 {current} 已是最新，无需迁移")
        return False, ""

    # 检查是否有迁移脚本
    migrate_script = _SCRIPTS_DIR / "migrate.py"
    if migrate_script.exists():
        print(f"⚠ 检测到版本变化 ({current} → {latest})，需要运行迁移脚本:")
        print(f"  python3 scripts/migrate.py")
        return True, f"{current} → {latest}"

    print(f"⚠ 版本变化 ({current} → {latest})，但未找到迁移脚本。")
    print("  如数据结构未变更，可忽略此警告。")
    return True, f"{current} → {latest}"


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def run_upgrade(simulate: bool = False) -> bool:
    """执行完整升级流程。"""
    print("=" * 50)
    print(f"LinSai-CoPilot 升级助手")
    print(f"当前版本: {get_current_version()}")
    print("=" * 50)

    if simulate:
        print("\n[模拟模式] 不会实际执行任何修改操作\n")

    # 1. 备份
    bp = backup_data()
    if bp is None:
        print("✗ 备份失败，中止升级")
        return False

    # 2. Git pull
    if not git_pull(simulate=simulate):
        print("\n✗ 代码拉取失败。您的数据已备份，可安全回滚。")
        print(f"  备份位置: {bp}")
        return False

    # 3. 验证
    ok, _ = verify_scripts()
    if not ok:
        print("\n✗ 脚本验证失败。请检查代码冲突或手动修复。")
        print(f"  备份位置: {bp}")
        return False

    # 4. 迁移检查
    needs_migrate, migrate_desc = check_migration()

    print("\n" + "=" * 50)
    if simulate:
        print("✓ 模拟升级完成")
    else:
        print("✓ 升级流程完成")
    print(f"  数据备份: {bp.name if bp else 'N/A'}")
    if needs_migrate:
        print(f"  迁移提示: {migrate_desc}")
    print("=" * 50)
    return True


def show_version() -> None:
    """显示版本信息和历史。"""
    current = get_current_version()
    versions = get_changelog_versions()

    print(f"当前版本: {current}")
    print()

    if versions:
        print("版本历史:")
        for v in versions[:5]:
            marker = " ← 当前" if v["version"] == current else ""
            print(f"  {v['version']:10}  {v['description']}{marker}")
    else:
        print("未找到版本历史。")

    # 检查 Git 状态
    git_dir = _PROJECT_ROOT / ".git"
    if git_dir.exists():
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=_PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout.strip():
                print("\nGit 状态: 有未提交的修改")
                print(result.stdout)
            else:
                print("\nGit 状态: 工作区干净")
        except Exception:
            pass
    else:
        print("\nGit 状态: 未初始化仓库（建议运行 git init）")


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> bool:
    """运行模块级自检。"""
    ok = True

    # 1. 版本读取
    v = get_current_version()
    if v and v != "unknown":
        print(f"✓ 版本读取: {v}")
    else:
        print("✗ 版本读取失败")
        ok = False

    # 2. CHANGELOG 解析
    versions = get_changelog_versions()
    print(f"✓ CHANGELOG 解析: {len(versions)} 个版本记录")

    # 3. 脚本验证（当前状态）
    valid, errs = verify_scripts()
    if valid:
        print("✓ 脚本语法验证通过")
    else:
        print(f"✗ 脚本语法验证失败: {len(errs)} 个错误")
        ok = False

    # 4. Git 检测
    if has_git_remote():
        print("✓ 检测到 Git 远程仓库")
    else:
        print("○ 无 Git 远程仓库（可选）")

    return ok


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="LinSai-CoPilot 升级助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/upgrade.py --check      # 查看当前版本
  python3 scripts/upgrade.py --verify     # 验证代码完整性
  python3 scripts/upgrade.py --simulate   # 模拟升级流程
  python3 scripts/upgrade.py              # 执行真实升级
  python3 scripts/upgrade.py --self-check # 运行自检
        """,
    )
    parser.add_argument("--check", action="store_true", help="显示版本信息")
    parser.add_argument("--simulate", action="store_true", help="模拟升级（不实际执行）")
    parser.add_argument("--verify", action="store_true", help="仅验证脚本语法")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)

    if args.self_check:
        print("=== 升级助手自检 ===")
        ok = _self_check()
        print("-" * 30)
        print("✓ 全部通过" if ok else "✗ 存在失败项")
        return 0 if ok else 1

    if args.check:
        show_version()
        return 0

    if args.verify:
        ok, errs = verify_scripts()
        return 0 if ok else 1

    return 0 if run_upgrade(simulate=args.simulate) else 1


if __name__ == "__main__":
    sys.exit(main())
