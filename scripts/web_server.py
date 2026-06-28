#!/usr/bin/env python3
"""web_server.py — LinSai-CoPilot Web 服务器（聚合器）。

v3.5.6: 拆分为 Mixin 架构。本文件仅负责：
1. 导入所有路由 Mixin 并组装 RequestHandler
2. 统一路由分派（_dispatch_all / _all_route_tables / _try_route）
3. 服务器启动与 CLI 入口（run_server / main / _self_check）

业务逻辑分布在各 web_routes_*.py 子模块中：
    - web_base.py                    共享基础设施（全局状态/工具函数/BaseRequestHandler）
    - web_routes_sessions.py         会话/消息路由
    - web_routes_tasks.py            任务路由
    - web_routes_kb.py               知识库路由
    - web_routes_system.py           系统状态路由
    - web_routes_skills.py           技能路由
    - web_routes_learning.py         学习路由
    - web_routes_projects.py         项目/NSFC/论文池路由
    - web_routes_hermes.py           Hermes 路由
    - web_routes_upload.py           上传/文件路由
    - web_routes_research.py         课题指导模块路由（独立分派器）

用法：
    python3 scripts/web_server.py              # 默认端口 8080
    python3 scripts/web_server.py --port 9000  # 指定端口
    python3 scripts/web_server.py --self-check # 运行自检

仅使用 Python 标准库。
"""

import argparse
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, unquote

# 共享基础设施
import web_base
from web_base import _log, split_response_stream, BaseRequestHandler

# 各域路由 Mixin
from web_routes_sessions import SessionRoutesMixin, _SESSION_ROUTES
from web_routes_tasks import TaskRoutesMixin, _TASK_ROUTES
from web_routes_kb import KbRoutesMixin, _KB_ROUTES
from web_routes_system import SystemRoutesMixin, _SYSTEM_ROUTES
from web_routes_skills import SkillRoutesMixin, _SKILL_ROUTES
from web_routes_learning import LearningRoutesMixin, _LEARNING_ROUTES
from web_routes_projects import ProjectRoutesMixin, _PROJECT_ROUTES
from web_routes_hermes import HermesRoutesMixin, _HERMES_ROUTES
from web_routes_upload import UploadRoutesMixin, _UPLOAD_ROUTES
from web_routes_research import ResearchRoutesMixin


# ---------------------------------------------------------------------------
# 统一路由表（不含 research，research 有独立分派器）
# ---------------------------------------------------------------------------
_ALL_ROUTE_TABLES = [
    _SESSION_ROUTES,
    _TASK_ROUTES,
    _KB_ROUTES,
    _SYSTEM_ROUTES,
    _SKILL_ROUTES,
    _LEARNING_ROUTES,
    _PROJECT_ROUTES,
    _HERMES_ROUTES,
    _UPLOAD_ROUTES,
]


# ---------------------------------------------------------------------------
# 请求处理器
# ---------------------------------------------------------------------------
class RequestHandler(
    SessionRoutesMixin,
    TaskRoutesMixin,
    KbRoutesMixin,
    SystemRoutesMixin,
    SkillRoutesMixin,
    LearningRoutesMixin,
    ProjectRoutesMixin,
    HermesRoutesMixin,
    UploadRoutesMixin,
    ResearchRoutesMixin,
    BaseRequestHandler,
    BaseHTTPRequestHandler,
):
    """HTTP 请求处理器：静态文件 + REST API + SSE。

    继承所有域路由 Mixin，通过统一分派器 _dispatch_all 路由请求。
    课题模块（research）使用独立分派器 _dispatch_research_routes 优先处理。
    """

    def _dispatch_all(self, method: str, path: str, parsed, body=None) -> bool:
        """依次尝试所有域路由表，返回 True 表示已处理。"""
        for routes in _ALL_ROUTE_TABLES:
            if self._try_route(routes, method, path, parsed, body):
                return True
        return False

    def _try_route(self, routes, method: str, path: str, parsed, body=None) -> bool:
        """尝试单个路由表。匹配则调用 handler 并返回 True。"""
        for entry in routes:
            m, pattern, handler_name = entry
            if m != method:
                continue
            match = pattern.match(path)
            if match:
                handler = getattr(self, handler_name, None)
                if handler is None:
                    continue
                kwargs = match.groupdict()
                if body is not None:
                    handler(parsed, body, **kwargs)
                else:
                    handler(parsed, **kwargs)
                return True
        return False

    # --- HTTP 方法 ---

    def do_GET(self) -> None:
        """处理 GET 请求。"""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if _log:
            _log.info(f"GET {path}")

        # 静态文件
        if path == "/":
            self._send_static("index.html")
            return
        if path.startswith("/web/"):
            self._send_static(path[5:])
            return

        # 课题模块路由（独立分派器，字符串模式）
        if self._dispatch_research_routes("GET", path, parsed):
            return

        # 其他域路由表（编译正则模式）
        if self._dispatch_all("GET", path, parsed):
            return

        self._send_json({"error": f"Not found: {path}"}, 404)

    def do_POST(self) -> None:
        """处理 POST 请求。"""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if _log:
            _log.info(f"POST {path}")
        body = self._read_json_body()

        # 课题模块路由（独立分派器，字符串模式）
        if self._dispatch_research_routes("POST", path, parsed, body):
            return

        # 其他域路由表（编译正则模式）
        if self._dispatch_all("POST", path, parsed, body):
            return

        self._send_json({"error": f"Not found: {path}"}, 404)

    def do_PUT(self) -> None:
        """处理 PUT 请求。"""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if _log:
            _log.info(f"PUT {path}")
        body = self._read_json_body()

        # 课题模块路由（独立分派器，字符串模式）
        if self._dispatch_research_routes("PUT", path, parsed, body):
            return

        # 其他域路由表（编译正则模式）
        if self._dispatch_all("PUT", path, parsed, body):
            return

        self._send_json({"error": f"Not found: {path}"}, 404)

    def do_DELETE(self) -> None:
        """处理 DELETE 请求。"""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if _log:
            _log.info(f"DELETE {path}")

        # 课题模块路由（独立分派器，字符串模式）
        if self._dispatch_research_routes("DELETE", path, parsed):
            return

        # 其他域路由表（编译正则模式）
        if self._dispatch_all("DELETE", path, parsed):
            return

        self._send_json({"error": f"Not found: {path}"}, 404)


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
    if web_base._WEB_DIR.name == "web":
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

    # 5. 路由表完整性
    total_routes = sum(len(t) for t in _ALL_ROUTE_TABLES)
    if total_routes >= 120:
        print(f"✓ 路由表完整: {total_routes} 条")
    else:
        print(f"✗ 路由表不完整: 仅 {total_routes} 条")
        ok = False

    # 6. RequestHandler 可导入且继承正确
    try:
        assert hasattr(RequestHandler, "_dispatch_all"), "缺少 _dispatch_all"
        assert hasattr(RequestHandler, "_dispatch_research_routes"), "缺少 _dispatch_research_routes"
        assert hasattr(RequestHandler, "_send_json"), "缺少 _send_json"
        assert hasattr(RequestHandler, "_send_sse"), "缺少 _send_sse"
        assert hasattr(RequestHandler, "do_GET"), "缺少 do_GET"
        assert hasattr(RequestHandler, "do_POST"), "缺少 do_POST"
        assert hasattr(RequestHandler, "do_PUT"), "缺少 do_PUT"
        assert hasattr(RequestHandler, "do_DELETE"), "缺少 do_DELETE"
        print("✓ RequestHandler 继承完整")
    except AssertionError as e:
        print(f"✗ RequestHandler 继承异常: {e}")
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
    parser.add_argument("--root", default="", help="项目根目录覆盖（隔离测试用，默认: 脚本上级）")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)

    # --root 覆盖项目根目录（用于隔离测试环境）
    # 必须修改 web_base 的全局变量，因为所有 Mixin 通过 web_base._PROJECT_ROOT 引用
    if args.root:
        web_base._PROJECT_ROOT = Path(args.root).resolve()
        web_base._WEB_DIR = web_base._PROJECT_ROOT / "web"

    if args.self_check:
        print("=== Web 服务器自检 ===")
        ok = _self_check()
        print("-" * 30)
        print("✓ 全部通过" if ok else "✗ 存在失败项")
        return 0 if ok else 1

    if _log:
        _log.info(f"Web 服务器启动: http://{args.host}:{args.port}")
    run_server(args.host, args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
