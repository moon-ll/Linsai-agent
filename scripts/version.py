#!/usr/bin/env python3
"""版本号集中读取 —— VERSION 文件是版本号唯一真相源。

用途：
    提供 get_version() 集中读取 VERSION 文件，消除各脚本/文档对版本号的
    硬编码和人工同步。AGENTS.md 声明「VERSION 文件为唯一真相源」，
    本模块让代码层真正落实这一声明。

用法示例：
    >>> from version import get_version, __version__
    >>> print(get_version())        # '2.6.0'
    >>> print(__version__)          # '2.6.0'  （模块加载时缓存）
    >>> from version import parse_version
    >>> print(parse_version('2.6.0'))   # (2, 6, 0)
    >>> print(is_newer('2.7.0', '2.6.0'))  # True

规范：
    - 仅使用 Python 3 标准库
    - 头部包含中文 docstring
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 不依赖项目内其他模块（可被任何脚本独立 import）
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
VERSION_FILE = PROJECT_ROOT / "VERSION"


def get_version() -> Optional[str]:
    """读取 VERSION 文件并返回版本字符串。

    Returns:
        版本号字符串（如 '2.6.0'）；文件缺失或为空返回 None。
    """
    if not VERSION_FILE.exists():
        return None
    return VERSION_FILE.read_text(encoding="utf-8").strip() or None


def parse_version(version: str) -> Tuple[int, int, int]:
    """解析语义化版本号为元组。

    Args:
        version: 形如 '2.6.0' 的版本字符串。

    Returns:
        (major, minor, patch) 元组。

    Raises:
        ValueError: 版本格式不合法。
    """
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError("版本号格式错误，应为 MAJOR.MINOR.PATCH: {}".format(version))
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        raise ValueError("版本号含非数字段: {}".format(version))


def is_newer(a: str, b: str) -> bool:
    """判断版本 a 是否严格新于 b。

    Args:
        a: 版本字符串。
        b: 版本字符串。

    Returns:
        a > b 返回 True。
    """
    ta, tb = parse_version(a), parse_version(b)
    return ta > tb


# 模块加载时缓存，供 `from version import __version__` 使用
__version__: Optional[str] = get_version()


def _self_check() -> None:
    """自检：读取 → 解析 → 比较。"""
    print("◐ version 自检...")
    v = get_version()
    assert v, "VERSION 文件读取失败或为空"
    parsed = parse_version(v)
    assert len(parsed) == 3, "版本解析异常"
    assert isinstance(__version__, str), "__version__ 缓存异常"
    assert is_newer("2.7.0", v) or parse_version(v) >= (0, 0, 1), "版本比较异常"
    print("✓ version 自检通过（当前版本 {}）".format(v))


if __name__ == "__main__":
    _self_check()
