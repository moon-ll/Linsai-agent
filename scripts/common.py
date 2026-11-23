#!/usr/bin/env python3
"""LinSai-CoPilot 公共工具函数。

集中定义各脚本中重复的工具函数，消除 22+ 处 _now_utc、10+ 处 _load_json/_save_json 重复。

用法:
    from common import now_utc, load_json, save_json, safe_filename, lazy_load
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

# fcntl 为 POSIX 标准库（macOS/Linux 可用，Windows 无）
try:
    import fcntl as _fcntl
    _HAS_FCNTL = True
except ImportError:
    _fcntl = None
    _HAS_FCNTL = False


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
    """保存 JSON 文件（ensure_ascii=False, indent=2）。

    采用原子写入：先写入同目录临时文件并 fsync，再 os.replace() 到目标路径。
    os.replace() 在 POSIX 上是原子操作，保证文件要么完整更新要么保持不变，
    避免写入中途崩溃导致数据损坏。
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    # 原子写入：先写临时文件再 rename，保证目标文件不会出现半写状态
    fd, tmp_path = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(p))
    except Exception:
        # 写入失败时清理临时文件，避免残留
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


# 原子写入别名，供语义化调用
atomic_save_json = save_json


@contextmanager
def file_lock(lock_name: str = "global", blocking: bool = True) -> Iterator[None]:
    """跨进程文件锁（fcntl.flock，独占）。

    用于 CoPilot web_server 与 hermes cron 等独立进程之间的互斥。
    进程内并发由 threading.Lock 处理；跨进程并发由 fcntl.flock 处理。
    非 POSIX 环境（无 fcntl）降级为无锁，仅依赖原子写入防损坏。

    Args:
        lock_name: 锁名称，不同名称对应不同锁文件，互不阻塞。
            常用值："item-status"、"paper-pool"、"sync-state"。
        blocking: True（默认）阻塞等锁，行为与旧版一致；False 非阻塞
            抢锁，锁被占用时抛出 TimeoutError（v6.9.7 新增）。适用于
            cron worker 等"拿不到就退出、下个 tick 再来"的调用方，
            避免进程在 flock 上无限堆积。

    用法:
        >>> with file_lock("item-status"):
        ...     data = load_json(path)
        ...     data["key"] = "value"
        ...     save_json(path, data)

        >>> try:
        ...     with file_lock("weekend-pipeline", blocking=False):
        ...         ...  # 拿到锁
        ... except TimeoutError:
        ...     ...  # 锁忙，温和退出
    """
    # v6.8.36: 支持锁目录隔离（环境变量 LINSAI_LOCK_DIR）。测试经 create_isolated_env
    # 设置该变量指向隔离目录，避免与真实 cron/web 进程争用 /tmp 下的同一锁文件
    # （此前工作时段 file_lock("proposal-lifecycle") 与 lc-micro-scheduler 竞争，
    # 导致 test_round_complete_break 等测试挂起）。生产进程不设此变量，行为不变。
    _lock_dir = os.environ.get("LINSAI_LOCK_DIR")
    lock_dir = Path(_lock_dir) if _lock_dir else Path(tempfile.gettempdir())
    lock_path = lock_dir / f"linsai-copilot-{lock_name}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(lock_path, "w")
    acquired = False
    try:
        if _HAS_FCNTL:
            flags = _fcntl.LOCK_EX if blocking else (_fcntl.LOCK_EX | _fcntl.LOCK_NB)
            try:
                _fcntl.flock(f.fileno(), flags)
            except (BlockingIOError, OSError) as e:
                if not blocking:
                    # 非阻塞抢锁失败：统一抛 TimeoutError，调用方按"锁忙"处理
                    raise TimeoutError(f"锁 {lock_name} 被其它进程持有") from e
                # 阻塞模式：异常原样上抛（理论上仅信号中断等罕见场景）
                raise
            acquired = True
        yield
    finally:
        if _HAS_FCNTL and acquired:
            _fcntl.flock(f.fileno(), _fcntl.LOCK_UN)
        f.close()


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


def file_sha256(path: Path | str) -> str:
    """计算文件的 SHA-256 哈希值（分块读取，支持大文件）。

    用于 PDF 原文去重和完整性校验。

    Args:
        path: 文件路径

    Returns:
        十六进制哈希字符串（64 字符）

    用法:
        >>> h = file_sha256("/path/to/paper.pdf")
        >>> "a1b2c3..."
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)  # 64KB 分块
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def clean_subprocess_env(extra: Optional[dict] = None) -> dict:
    """构造一个干净的子进程环境，避免宿主 Python/TRAE 环境变量污染 hermes 等工具。

    关键场景：TRAE 等 IDE 在 shell 里设置了 PYTHONHOME/PYTHONPATH 指向 IDE 自己的 Python
    （如 3.13），但 hermes 等工具自带 venv（如 3.11）。当宿主 Python 变量被子进程继承时，
    子进程会按宿主 Python 版本去查找 stdlib（如 lib/python3.11），而 hermes venv 里只有
    自己的版本，找不到 encodings 等核心模块 → 子进程启动崩溃。

    解法：pop 全部 Python 相关变量，让 hermes 完全用自己 venv 里的解释器和 stdlib。
    同时保留 HOME/PATH/LANG 等必要变量，确保可执行文件能找到。

    Args:
        extra: 额外覆盖/补充的环境变量（如 {"PATH": "/custom/bin"}）

    Returns:
        可直接传给 subprocess.run(env=...) 的字典
    """
    env = dict(os.environ)
    # 清理全部 Python 变量（这些会让子进程用错误的 Python 版本启动）
    _PYTHON_VARS = (
        "PYTHONHOME", "PYTHONPATH", "PYTHONIOENCODING", "PYTHONUTF8",
        "PYTHONSTARTUP", "PYTHONBREAKPOINT", "PYTHONCASEOK", "PYTHONINSPECT",
        "PYTHONDEBUG", "PYTHONOPTIMIZE", "PYTHONDONTWRITEBYTECODE", "PYTHONUNBUFFERED",
        "PYTHONHASHSEED", "PYTHONTRACEMALLOC", "PYTHONMALLOCSTATS",
        "PYTHONNOUSERSITE", "PYTHONUSERBASE", "PYTHONWARNINGS",
        "__PYVENV_LAUNCHER__", "_PYTHON_PROJECT_BASE", "_PYTHON_LAUNCHER_ENV",
    )
    for k in _PYTHON_VARS:
        env.pop(k, None)
    if extra:
        env.update(extra)
    return env


def load_env_file(path: Path) -> Dict[str, str]:
    """简单解析 .env 文件（不需要 python-dotenv）。"""
    result: Dict[str, str] = {}
    if not path.exists():
        return result
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    result[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return result


def hermes_subprocess_env(extra: Optional[dict] = None, env_path: Optional[Path] = None) -> dict:
    """构造供 hermes CLI 使用的子进程环境。

    - 清理 Python 相关变量（避免 venv 冲突）
    - 自动读取项目根目录 .env，解决 cron 等无 shell 环境时读不到 API Key 的问题
    - 若配置了 GLM_API_KEY 但未配置 ZAI_API_KEY，自动透传，使 hermes 的 zai provider 可用

    Args:
        extra: 额外覆盖/补充的环境变量
        env_path: 指定 .env 文件路径，默认使用 PROJECT_ROOT/.env

    Returns:
        可直接传给 subprocess.run(env=...) 的字典
    """
    from paths import PROJECT_ROOT

    if env_path is None:
        env_path = PROJECT_ROOT / ".env"

    # 合并 .env 变量与显式 extra，确保 cron 等无 shell 环境也能读到 API Key
    merged_extra: Dict[str, str] = {}
    merged_extra.update(load_env_file(env_path))
    if extra:
        merged_extra.update(extra)

    zai_key = merged_extra.get("ZAI_API_KEY") or merged_extra.get("GLM_API_KEY") or merged_extra.get("Z_AI_API_KEY")
    if zai_key:
        merged_extra["ZAI_API_KEY"] = zai_key

    return clean_subprocess_env(extra=merged_extra)


def copy_file(src: Path | str, dst: Path | str, overwrite: bool = False) -> bool:
    """安全复制文件（支持二进制文件如 PDF）。

    Args:
        src: 源文件路径
        dst: 目标文件路径
        overwrite: 是否覆盖已存在文件（默认 False，不覆盖返回 False）

    Returns:
        True 表示复制成功，False 表示目标已存在且 overwrite=False

    用法:
        >>> copy_file("/tmp/upload.pdf", PDF_DIR / "2403.15337.pdf")
    """
    src_p, dst_p = Path(src), Path(dst)
    if not src_p.exists():
        raise FileNotFoundError(f"源文件不存在: {src_p}")
    if dst_p.exists() and not overwrite:
        return False
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_p, dst_p)
    return True
