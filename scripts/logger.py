#!/usr/bin/env python3
"""统一日志模块 —— 为 LinSai-CoPilot 各组件提供结构化日志记录。

用法:
    >>> from logger import get_logger
    >>> log = get_logger("web_server")
    >>> log.info("服务器启动于端口 8080")
    >>> log.warning("LLM 降级到 kimi CLI")
    >>> log.error("索引文件损坏", exc_info=True)

规范:
    - 仅使用 Python 标准库 logging
    - 日志文件按日期轮转：logs/linsai-YYYY-MM-DD.log
    - 同时输出到控制台（彩色）和文件
    - 避免在循环中高频调用 debug（性能敏感路径）
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"

# 颜色映射（控制台）
_COLORS = {
    "DEBUG": "\x1b[36m",    # 青色
    "INFO": "\x1b[32m",     # 绿色
    "WARNING": "\x1b[33m",  # 黄色
    "ERROR": "\x1b[31m",    # 红色
    "CRITICAL": "\x1b[35m", # 紫色
    "RESET": "\x1b[0m",
}


class _ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式。"""

    def format(self, record: logging.LogRecord) -> str:
        color = _COLORS.get(record.levelname, _COLORS["RESET"])
        reset = _COLORS["RESET"]
        # 简短时间: 14:30:00
        time_str = self.formatTime(record, "%H:%M:%S")
        return f"{color}[{time_str}] [{record.levelname}] [{record.name}] {record.getMessage()}{reset}"


class _PlainFormatter(logging.Formatter):
    """纯文本文件日志格式。"""

    def format(self, record: logging.LogRecord) -> str:
        time_str = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        msg = record.getMessage()
        if record.exc_info:
            msg += "\n" + self.formatException(record.exc_info)
        return f"[{time_str}] [{record.levelname}] [{record.name}] {msg}"


# 全局日志配置（延迟初始化）
_loggers: dict = {}
_root_configured: bool = False


def _ensure_logs_dir() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _get_log_file() -> Path:
    _ensure_logs_dir()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return LOGS_DIR / f"linsai-{today}.log"


def setup_logging(level: int = logging.INFO, file_level: int = logging.DEBUG) -> None:
    """初始化全局日志配置。

    Args:
        level: 控制台日志级别（默认 INFO）
        file_level: 文件日志级别（默认 DEBUG，记录更详细）
    """
    global _root_configured
    if _root_configured:
        return

    _ensure_logs_dir()

    # 根日志器
    root = logging.getLogger("linsai")
    root.setLevel(logging.DEBUG)
    root.handlers = []  # 清除已有 handler，避免重复

    # 控制台 handler（带颜色）
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(_ColoredFormatter())
    root.addHandler(console)

    # 文件 handler（纯文本，追加模式）
    log_file = _get_log_file()
    file_handler = logging.FileHandler(str(log_file), encoding="utf-8", mode="a")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(_PlainFormatter())
    root.addHandler(file_handler)

    _root_configured = True
    root.info(f"日志系统初始化完成 → {log_file}")


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """获取指定模块的日志器。

    Args:
        name: 模块名，如 "web_server", "copilot_engine"
        level: 可选的独立级别

    Returns:
        logging.Logger 实例
    """
    if not _root_configured:
        setup_logging()

    logger = logging.getLogger(f"linsai.{name}")
    if level is not None:
        logger.setLevel(level)
    return logger


if __name__ == "__main__":
    setup_logging()
    log = get_logger("logger_test")
    log.debug("这是一条 DEBUG 日志")
    log.info("这是一条 INFO 日志")
    log.warning("这是一条 WARNING 日志")
    try:
        1 / 0
    except Exception:
        log.error("这是一条带堆栈的 ERROR 日志", exc_info=True)
    print(f"\n日志文件: {_get_log_file()}")
