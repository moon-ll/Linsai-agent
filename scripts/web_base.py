#!/usr/bin/env python3
"""web_base.py — Web 服务器共享基础设施。

为 web_server.py 及各 web_routes_*.py 路由 Mixin 提供：
    - 全局并发状态（文件锁 / 知识库忙标志 / 后台任务表 / 日志器）
    - 工具函数（_get_file_lock / _try_acquire_kb_busy / _release_kb_busy /
      split_response_stream / _update_memory_async）
    - 常量（MIME_TYPES / _PROJECT_ROOT / _WEB_DIR / _SCRIPT_DIR）
    - BaseRequestHandler 基类：所有 HTTP handler 共用的 _send_json /
      _send_sse_header / _send_sse / _send_static / _read_json_body /
      log_message / do_OPTIONS 方法

设计要点：
    - 所有路由 Mixin 的 self 是最终 RequestHandler 实例，可直接调用本基类方法
    - _PROJECT_ROOT / _WEB_DIR 为模块级全局，web_server.py 的 --root 选项会
      直接覆写 web_base._PROJECT_ROOT / web_base._WEB_DIR，故各 Mixin 应通过
      web_base._PROJECT_ROOT 引用（不要 from ... import 快照）
    - 仅使用 Python 标准库

用法（由 web_server.py 聚合，不单独运行）：
    from web_base import BaseRequestHandler
"""

import json
import re
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# 路径与 sys.path
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
_WEB_DIR = _PROJECT_ROOT / "web"

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# 统一日志
try:
    from logger import get_logger, setup_logging
    setup_logging()
    _log = get_logger("web_server")
except Exception:
    _log = None

# 异步记忆更新需要 memory_manager
import memory_manager as mm


# ---------------------------------------------------------------------------
# 全局并发状态
# ---------------------------------------------------------------------------
# P1-9: 全局文件写入锁，防止并发 read-modify-write 竞争
_file_locks: Dict[str, threading.Lock] = {}
_file_locks_guard = threading.Lock()


def _get_file_lock(key: str) -> threading.Lock:
    """获取指定文件的写入锁（线程安全）。"""
    with _file_locks_guard:
        if key not in _file_locks:
            _file_locks[key] = threading.Lock()
        return _file_locks[key]


# P1-11: 同步/重建防重入标志
_kb_busy = False
_kb_busy_lock = threading.Lock()


def _try_acquire_kb_busy() -> bool:
    """尝试获取知识库忙标志，成功返回 True，已在忙返回 False。"""
    global _kb_busy
    with _kb_busy_lock:
        if _kb_busy:
            return False
        _kb_busy = True
        return True


def _release_kb_busy() -> None:
    """释放知识库忙标志。"""
    global _kb_busy
    with _kb_busy_lock:
        _kb_busy = False


# P1-12: 后台任务状态跟踪
_bg_tasks: Dict[str, dict] = {}
_bg_tasks_lock = threading.Lock()


# ---------------------------------------------------------------------------
# MIME 类型
# ---------------------------------------------------------------------------
MIME_TYPES: Dict[str, str] = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff2": "font/woff2",
}


# ---------------------------------------------------------------------------
# 流式切分
# ---------------------------------------------------------------------------
def split_response_stream(text: str) -> List[str]:
    """将 LLM 完整回复切分为流式块，按句子或代码块切分。"""
    if not text:
        return []

    chunks: List[str] = []
    # 先分离代码块
    parts = re.split(r"(```[\s\S]*?```)", text)

    for part in parts:
        if part.startswith("```"):
            chunks.append(part)
            continue

        # 按句子结束符切分，保留结束符
        sentences = re.split(r"([。！？…\.!\?]+)", part)
        current = ""
        for i in range(0, len(sentences), 2):
            current += sentences[i]
            if i + 1 < len(sentences):
                current += sentences[i + 1]
                if current.strip():
                    chunks.append(current)
                current = ""
        if current.strip():
            chunks.append(current)

    return [c for c in chunks if c.strip()]


def _update_memory_async(session_id: str) -> None:
    """异步更新用户画像和工作上下文。"""
    try:
        mm.update_user_profile(session_id)
        mm.update_working_context(session_id)
    except Exception as e:
        if _log:
            _log.debug("异步更新记忆失败: %s", e)


# ---------------------------------------------------------------------------
# 基类：HTTP handler 共用方法
# ---------------------------------------------------------------------------
class BaseRequestHandler:
    """所有路由 Mixin 与最终 RequestHandler 共用的 HTTP 工具方法基类。

    注意：本类不继承 BaseHTTPRequestHandler，由 web_server.py 的 RequestHandler
    在 MRO 末尾混入 BaseHTTPRequestHandler。本类仅提供方法，不提供 do_GET 等入口。
    self 在运行时是最终 RequestHandler 实例，可访问 send_response / wfile 等。
    """

    def log_message(self, fmt: str, *args: Any) -> None:
        """重写日志，显示时间但精简格式。"""
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def _send_json(self, data: Any, status: int = 200) -> None:
        """发送 JSON 响应。"""
        body = json.dumps(data, ensure_ascii=False, indent=None).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_sse_header(self) -> None:
        """发送 SSE 响应头。"""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _send_sse(self, data: Dict[str, Any]) -> None:
        """发送一条 SSE 事件。"""
        line = f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        self.wfile.write(line.encode("utf-8"))
        self.wfile.flush()

    def _send_static(self, rel_path: str) -> None:
        """发送静态文件。"""
        fpath = _WEB_DIR / rel_path.lstrip("/")
        if not fpath.exists() or not fpath.is_file():
            self._send_json({"error": "Not found"}, 404)
            return

        ext = fpath.suffix.lower()
        mime = MIME_TYPES.get(ext, "application/octet-stream")
        data = fpath.read_bytes()

        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> Dict[str, Any]:
        """读取请求体并解析为 JSON。"""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body)

    def do_OPTIONS(self) -> None:
        """处理 CORS 预检请求。"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
