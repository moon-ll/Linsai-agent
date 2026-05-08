#!/usr/bin/env python3
"""Web 服务器 — 为 LinSai-CoPilot 提供浏览器交互界面。

用法:
    python3 scripts/web_server.py           # 启动服务器，默认端口 8080
    python3 scripts/web_server.py --port 9000  # 指定端口
    python3 scripts/web_server.py --self-check # 运行自检

技术:
    - Python 3 标准库 http.server + threading
    - REST API + SSE (Server-Sent Events) 流式输出
    - 静态文件服务（web/ 目录）
    - 零第三方依赖
"""

import argparse
import json
import queue
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, unquote, urlparse


# ---------------------------------------------------------------------------
# 路径与导入
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
_WEB_DIR = _PROJECT_ROOT / "web"

# 确保项目脚本可被导入
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import context_builder as cb
import copilot_engine as ce
import document_handler as dh
import memory_manager as mm
import proactive_engine as pe
import session_manager as sm
import task_manager as tm


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


# ---------------------------------------------------------------------------
# 请求处理器
# ---------------------------------------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器：静态文件 + REST API + SSE。"""

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

    def do_GET(self) -> None:
        """处理 GET 请求。"""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        # 静态文件
        if path == "/":
            self._send_static("index.html")
            return
        if path.startswith("/web/"):
            self._send_static(path[5:])
            return

        # API 路由
        if path == "/api/version":
            version = (_PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()
            self._send_json({"version": version, "name": "LinSai-CoPilot"})
            return

        if path == "/api/sessions":
            sessions = sm.list_sessions()
            self._send_json([{
                "session_id": s["session_id"],
                "topic": s.get("topic", ""),
                "mode": s.get("mode", "co-working"),
                "message_count": s.get("message_count", 0),
                "last_active": s.get("last_active", ""),
            } for s in sessions])
            return

        if path.startswith("/api/sessions/") and path.endswith("/messages"):
            sid = path[len("/api/sessions/") : -len("/messages")]
            messages, state = sm.load_session(sid)
            # 兼容两种 messages.json 格式
            if isinstance(messages, dict):
                messages = messages.get("messages", [])
            self._send_json({
                "session_id": sid,
                "topic": state.get("topic", ""),
                "mode": state.get("mode", "co-working"),
                "messages": messages,
            })
            return

        if path == "/api/tasks":
            tasks = tm.list_tasks()
            self._send_json(tasks)
            return

        if path == "/api/heartbeat":
            reminders = pe.heartbeat()
            self._send_json({"reminders": reminders})
            return

        self._send_json({"error": f"Not found: {path}"}, 404)

    def do_POST(self) -> None:
        """处理 POST 请求。"""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        body = self._read_json_body()

        # 创建会话
        if path == "/api/sessions":
            topic = body.get("topic", "新会话")
            mode = body.get("mode", "co-working")
            sid, _ = sm.create_session(topic, mode)
            self._send_json({"session_id": sid, "topic": topic, "mode": mode})
            return

        # 发送消息（SSE 流式返回）
        if path.startswith("/api/sessions/") and path.endswith("/messages"):
            sid = path[len("/api/sessions/") : -len("/messages")]
            user_input = body.get("content", "").strip()
            mode = body.get("mode", "co-working")

            if not user_input:
                self._send_json({"error": "内容不能为空"}, 400)
                return

            # 保存用户消息
            sm.append_message(sid, "user", user_input, mode)

            # 进入 SSE 流
            self._send_sse_header()

            q: queue.Queue[Tuple[str, Any]] = queue.Queue()

            def llm_worker() -> None:
                """在后台线程调用 LLM。"""
                try:
                    context = cb.build_context(sid, user_input, mode)
                    system_prompt = context.get("system_prompt", "")
                    messages = context.get("messages", [])

                    # 调用 LLM 获取完整回复
                    response = ce.call_llm(system_prompt, messages)

                    if not response or not response.strip():
                        q.put(("error", "LLM 返回为空"))
                        return

                    # 切分并流式输出
                    chunks = split_response_stream(response)
                    for chunk in chunks:
                        q.put(("token", chunk))
                        # 模拟打字延迟
                        delay = max(0.02, min(0.08, len(chunk) * 0.01))
                        time.sleep(delay)

                    q.put(("done", response.strip()))
                except Exception as e:
                    q.put(("error", str(e)))

            thread = threading.Thread(target=llm_worker)
            thread.start()

            full_response = ""
            while True:
                event_type, data = q.get()
                if event_type == "token":
                    self._send_sse({"type": "token", "content": data})
                    full_response += data
                elif event_type == "done":
                    self._send_sse({"type": "done"})
                    full_response = data  # 使用完整原始文本
                    break
                elif event_type == "error":
                    self._send_sse({"type": "error", "message": str(data)})
                    break

            thread.join()

            # 保存林赛回复（如果成功）
            if full_response:
                sm.append_message(sid, "assistant", full_response, mode)
                # 异步更新记忆（不阻塞响应）
                threading.Thread(
                    target=_update_memory_async, args=(sid,), daemon=True
                ).start()
            return

        self._send_json({"error": f"Not found: {path}"}, 404)


def _update_memory_async(session_id: str) -> None:
    """异步更新用户画像和工作上下文。"""
    try:
        mm.update_user_profile(session_id)
        mm.update_working_context(session_id)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 服务器启动
# ---------------------------------------------------------------------------

def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    """启动 Web 服务器。"""
    server = ThreadingHTTPServer((host, port), RequestHandler)
    print(f"✓ 林赛 Web 界面已启动")
    print(f"  地址: http://{host}:{port}")
    print(f"  按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n○ 服务器已停止")
        server.shutdown()


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> bool:
    """运行模块级自检。"""
    ok = True

    # 1. 路径推导
    if _WEB_DIR.name == "web":
        print("✓ WEB_DIR 推导正确")
    else:
        print("✗ WEB_DIR 推导异常")
        ok = False

    # 2. 流式切分
    text = "你好。这是第一句！这是第二句？代码：`print(1)`。结束。"
    chunks = split_response_stream(text)
    if len(chunks) >= 4:
        print(f"✓ 流式切分: {len(chunks)} 个块")
    else:
        print(f"✗ 流式切分异常: {chunks}")
        ok = False

    # 3. 代码块不切分
    code = "```python\nprint(1)\nprint(2)\n```"
    chunks = split_response_stream(code)
    if len(chunks) == 1 and chunks[0] == code:
        print("✓ 代码块整体保留")
    else:
        print("✗ 代码块被错误切分")
        ok = False

    # 4. 空文本处理
    if split_response_stream("") == []:
        print("✓ 空文本处理正确")
    else:
        print("✗ 空文本处理异常")
        ok = False

    return ok


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="LinSai-CoPilot Web 服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/web_server.py              # 默认端口 8080
  python3 scripts/web_server.py --port 9000  # 指定端口
  python3 scripts/web_server.py --self-check # 运行自检
        """,
    )
    parser.add_argument("--port", type=int, default=8080, help="监听端口 (默认: 8080)")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址 (默认: 127.0.0.1)")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)

    if args.self_check:
        print("=== Web 服务器自检 ===")
        ok = _self_check()
        print("-" * 30)
        print("✓ 全部通过" if ok else "✗ 存在失败项")
        return 0 if ok else 1

    run_server(args.host, args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
