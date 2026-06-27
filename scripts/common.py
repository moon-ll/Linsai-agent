#!/usr/bin/env python3
"""LinSai-CoPilot 公共工具函数。

集中定义各脚本中重复的工具函数，消除 22+ 处 _now_utc、10+ 处 _load_json/_save_json 重复。

用法:
    from common import now_utc, load_json, save_json, safe_filename, lazy_load
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def now_utc() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path | str, default: Any = None) -> Any:
    """加载 JSON 文件，失败时返回 default。"""
    p = Path(path)
    if not p.exists():
        return default if default is not None else {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def save_json(path: Path | str, data: Any) -> None:
    """保存 JSON 文件（ensure_ascii=False, indent=2）。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_filename(name: str, separator: str = "_") -> str:
    """将任意字符串转为安全的文件名片段。

    保留中文、字母、数字、连字符，其余替换为 separator。
    """
    return re.sub(r"[^\w\u4e00-\u9fff\-]", separator, name).strip(separator)


def lazy_load(module_name: str):
    """懒加载同目录模块，容忍缺失或导入失败。

    用于消除 context_builder、web_server 等文件中重复的 importlib 样板。
    返回模块对象或 None。
    """
    try:
        import importlib.util
        _path = Path(__file__).parent / f"{module_name}.py"
        if not _path.exists():
            return None
        _spec = importlib.util.spec_from_file_location(module_name, _path)
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        return _mod
    except Exception:
        return None
