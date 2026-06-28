#!/usr/bin/env python3
"""安全升级流程 —— 备份优先，可验证，可回滚。

用途：
    LinSai-CoPilot 的标准升级助手。执行流程：
    1. 检查当前版本（VERSION 文件）
    2. 备份当前用户数据（调用 backup_manager）
    3. 验证所有脚本语法（py_compile）
    4. 若 VERSION 发生变化且存在 scripts/migrate.py，执行迁移
    5. 运行自测（self_test）确认回归通过
    失败任意一步即中止并提示回滚。

设计原则（见 AGENTS.md「标准升级流程 SOP」）：
    - 备份优先：升级前必须先备份
    - 恢复可验证：备份包必须能完整恢复
    - 升级可回滚：失败时能一键回到之前状态

用法示例：
    >>> # 检查当前版本与升级前置条件
    >>> python3 scripts/upgrade.py --check
    >>> # 模拟升级（查看会做什么，不实际执行）
    >>> python3 scripts/upgrade.py --simulate
    >>> # 执行升级（备份 → 验证 → 迁移 → 自测）
    >>> python3 scripts/upgrade.py

规范：
    - 仅使用 Python 3 标准库
    - 头部包含中文 docstring
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 输出使用中文，状态图标统一：✓ 成功、✗ 失败、⚠ 警告、○ 待处理、◐ 进行中
"""

from __future__ import annotations

import argparse
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Optional

from paths import PROJECT_ROOT, SCRIPTS_DIR
VERSION_FILE = PROJECT_ROOT / "VERSION"
MIGRATE_SCRIPT = SCRIPTS_DIR / "migrate.py"
SELF_TEST_SCRIPT = SCRIPTS_DIR / "self_test.py"


def read_version() -> Optional[str]:
    """读取 VERSION 文件，返回版本字符串或 None。"""
    if not VERSION_FILE.exists():
        return None
    return VERSION_FILE.read_text(encoding="utf-8").strip() or None


def _collect_python_files() -> list:
    """收集 scripts/ 下所有 .py 文件（含子包）。"""
    return sorted(SCRIPTS_DIR.rglob("*.py"))


def verify_syntax() -> bool:
    """用 py_compile 验证所有脚本语法。

    Returns:
        全部通过返回 True。
    """
    files = _collect_python_files()
    if not files:
        print("⚠ 未发现任何 Python 脚本")
        return False

    print("◐ 验证 {} 个脚本语法...".format(len(files)))
    failed = []
    for f in files:
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as e:
            failed.append((f, str(e)))

    if failed:
        for f, err in failed:
            print("✗ 语法错误: {}".format(f.relative_to(PROJECT_ROOT)))
            print("  {}".format(err.splitlines()[0] if err else ""))
        print("✗ {} 个脚本语法验证失败".format(len(failed)))
        return False

    print("✓ 全部 {} 个脚本语法正确".format(len(files)))
    return True


def run_migration(current: str) -> bool:
    """若存在 migrate.py 且 VERSION 变化，执行迁移。

    Args:
        current: 当前版本号（升级前读取的）。

    Returns:
        迁移成功或无需迁移返回 True。
    """
    if not MIGRATE_SCRIPT.exists():
        print("○ 无迁移脚本（scripts/migrate.py），跳过迁移步骤")
        return True

    new_version = read_version()
    if new_version and new_version == current:
        print("○ 版本未变化（{}），跳过迁移".format(current))
        return True

    print("◐ 执行迁移脚本 {} → {}...".format(current, new_version or "?"))
    try:
        result = subprocess.run(
            [sys.executable, str(MIGRATE_SCRIPT)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            print("✓ 迁移成功")
            if result.stdout.strip():
                print(result.stdout.strip())
            return True
        print("✗ 迁移失败（退出码 {}）".format(result.returncode))
        if result.stderr.strip():
            print(result.stderr.strip())
        return False
    except subprocess.TimeoutExpired:
        print("✗ 迁移超时（>300s）")
        return False
    except Exception as e:
        print("✗ 迁移异常: {}".format(e))
        return False


def run_self_test() -> bool:
    """运行自测，确认回归通过。

    Returns:
        自测通过返回 True（self_test 非零退出视为失败，但不阻塞升级完成报告）。
    """
    if not SELF_TEST_SCRIPT.exists():
        print("○ 无自测脚本，跳过回归测试")
        return True

    print("◐ 运行自测回归...")
    try:
        result = subprocess.run(
            [sys.executable, str(SELF_TEST_SCRIPT)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print("✓ 自测通过")
            return True
        print("⚠ 自测有失败项（退出码 {}），请人工检查".format(result.returncode))
        if result.stdout.strip():
            # 只显示末尾摘要
            tail = "\n".join(result.stdout.strip().splitlines()[-15:])
            print(tail)
        return False
    except subprocess.TimeoutExpired:
        print("⚠ 自测超时（>120s），请人工运行 python3 scripts/self_test.py 确认")
        return False
    except Exception as e:
        print("⚠ 自测运行异常: {}".format(e))
        return False


def do_check() -> None:
    """检查当前版本与升级前置条件。"""
    print("=== 升级前置检查 ===\n")
    version = read_version()
    if version:
        print("✓ 当前版本: {}".format(version))
    else:
        print("✗ 未找到 VERSION 文件")
        sys.exit(1)

    # 语法预检
    ok = verify_syntax()

    # 备份模块可用性
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from backup_manager import list_backups  # noqa: E402

        backups = list_backups()
        if backups:
            print("✓ 最近备份: {}（共 {} 份）".format(backups[0].name, len(backups)))
        else:
            print("○ 暂无备份，升级前会自动创建")
    except Exception as e:
        print("⚠ 备份模块不可用: {}".format(e))

    # 迁移脚本
    if MIGRATE_SCRIPT.exists():
        print("✓ 存在迁移脚本: {}".format(MIGRATE_SCRIPT.name))
    else:
        print("○ 无迁移脚本")

    print("\n前置检查{}，可执行升级".format("通过" if ok else "未完全通过"))


def do_simulate() -> None:
    """模拟升级，展示将要执行的步骤（不实际执行）。"""
    version = read_version()
    print("=== 升级模拟（dry-run，不实际执行）===\n")
    print("当前版本: {}".format(version or "?"))
    print("\n将要执行的步骤：")
    print("  1. [备份] 调用 backup_manager.create_backup() 全量备份用户数据")
    print("     → sessions/ memory/ tasks/ knowledge/ references/")
    print("  2. [验证] py_compile 校验 scripts/ 下所有 .py 语法")
    print("  3. [迁移] 若 VERSION 变化且存在 scripts/migrate.py，执行迁移")
    print("  4. [自测] 运行 self_test.py 确认回归通过")
    print("\n失败处理：任一步骤失败即中止；已创建的备份可用于回滚：")
    print("  python3 scripts/backup_manager.py --restore <备份文件>")
    print("\n模拟完成。去掉 --simulate 执行真实升级。")


def do_upgrade() -> int:
    """执行完整升级流程。

    Returns:
        退出码：0 成功，非 0 失败。
    """
    version_before = read_version()
    print("=== 执行升级 ===\n")
    print("当前版本: {}\n".format(version_before or "?"))

    # 步骤 1：备份
    print("--- 步骤 1/4：备份数据 ---")
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from backup_manager import create_backup  # noqa: E402

        backup_path = create_backup(label="pre-upgrade")
        if not backup_path:
            print("✗ 备份失败，中止升级（数据安全优先）")
            return 1
        print("  回滚命令: python3 scripts/backup_manager.py --restore {}\n".format(backup_path.name))
    except Exception as e:
        print("✗ 备份模块异常: {}，中止升级".format(e))
        return 1

    # 步骤 2：验证语法
    print("--- 步骤 2/4：验证脚本语法 ---")
    if not verify_syntax():
        print("\n✗ 语法验证失败，升级中止。可用备份回滚：")
        print("  python3 scripts/backup_manager.py --restore {}".format(backup_path.name))
        return 2
    print()

    # 步骤 3：迁移
    print("--- 步骤 3/4：数据迁移 ---")
    if not run_migration(version_before):
        print("\n✗ 迁移失败，升级中止。可用备份回滚：")
        print("  python3 scripts/backup_manager.py --restore {}".format(backup_path.name))
        return 3
    print()

    # 步骤 4：自测
    print("--- 步骤 4/4：回归自测 ---")
    test_ok = run_self_test()
    print()

    version_after = read_version()
    print("=== 升级完成 ===")
    print("版本: {} → {}".format(version_before or "?", version_after or "?"))
    if not test_ok:
        print("⚠ 自测未全通过，请人工运行 python3 scripts/self_test.py 检查")
        print("  如需回滚: python3 scripts/backup_manager.py --restore {}".format(backup_path.name))
        return 4
    print("✓ 升级成功，所有检查通过")
    return 0


def _self_check() -> None:
    """自检：版本读取 + 语法验证。"""
    print("◐ upgrade 自检...")
    version = read_version()
    assert version, "VERSION 文件读取失败"
    assert verify_syntax(), "语法验证失败"
    print("✓ upgrade 自检通过（版本 {}）".format(version))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LinSai-CoPilot 安全升级助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="升级流程：备份 → 验证语法 → 迁移 → 自测。失败可回滚。",
    )
    parser.add_argument("--check", action="store_true", help="检查当前版本与前置条件")
    parser.add_argument("--simulate", action="store_true", help="模拟升级（不实际执行）")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return

    if args.check:
        do_check()
        return

    if args.simulate:
        do_simulate()
        return

    # 默认：执行升级
    sys.exit(do_upgrade())


if __name__ == "__main__":
    main()
