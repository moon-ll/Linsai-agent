#!/usr/bin/env python3
"""web_routes_hermes.py — Hermes 路由 Mixin。

提供 HermesRoutesMixin，封装 hermes cron 管理、手动派活等 HTTP 路由：
    - GET  /api/hermes/cron              cron job 列表
    - POST /api/hermes/cron              cron job 列表（GET 重复）
    - POST /api/hermes/cron/{id}/{action} cron 控制（pause/resume/run）
    - POST /api/hermes/run               手动派活（SSE 流式返回）

修复：原 web_server.py 中 _send_sse_raw 未定义的 bug，
     改为 self._send_sse({"type": "done"})。

路由表格式：(HTTP方法, re.compile(正则), handler名)
handler 签名：GET/DELETE → (self, parsed, body=None, **path_params)
             POST/PUT   → (self, parsed, body, **path_params)
仅使用 Python 标准库。
"""

import queue
import re
import threading
from typing import Any, Tuple

from web_base import _log, split_response_stream

import hermes_bridge as hb


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_HERMES_ROUTES = [
    # GET
    ("GET", re.compile(r"^/api/hermes/cron$"), "_her_cron_list"),
    # POST（GET 重复 + 独有）
    ("POST", re.compile(r"^/api/hermes/cron$"), "_her_cron_list"),
    ("POST", re.compile(r"^/api/hermes/cron/(?P<job_id>[^/]+)/(?P<action>pause|resume|run)$"), "_her_cron_control"),
    ("POST", re.compile(r"^/api/hermes/run$"), "_her_run"),
]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class HermesRoutesMixin:
    """Hermes 路由 Mixin。"""

    def _her_cron_list(self, parsed, body=None):
        """hermes cron job 列表（GET+POST 重复）"""
        self._send_json({"jobs": hb.cron_list(), "status": hb.check_hermes_available()})

    def _her_cron_control(self, parsed, body, job_id, action):
        """hermes cron 控制（暂停/恢复/触发）"""
        result = hb.cron_control(job_id, action)
        self._send_json(result)

    def _her_run(self, parsed, body):
        """hermes 手动派活（oneshot agent loop，SSE 流式返回）。

        P0-1 修复：原实现后台线程直接写 self.wfile，非线程安全。
        改为 queue.Queue 模式，主线程负责所有 wfile 写入。
        """
        prompt = body.get("prompt", "").strip()
        if not prompt:
            self._send_json({"error": "缺少 prompt"}, 400)
            return
        timeout = min(int(body.get("timeout", 300)), 600)  # P3: 服务端最大 600s 上限
        # 进入 SSE 流
        self._send_sse_header()

        q: "queue.Queue[Tuple[str, Any]]" = queue.Queue()

        def _hermes_worker() -> None:
            """后台线程：调用 hermes oneshot，结果通过 queue 传回主线程。"""
            try:
                result = hb.oneshot(prompt, timeout=timeout)
                output = result.get("output", "") or result.get("error", "")
                for chunk in split_response_stream(output):
                    q.put(("token", chunk))
                q.put(("done", result.get("success", True)))
            except Exception as e:
                if _log:
                    _log.error("Hermes oneshot 失败: %s", e, exc_info=True)
                q.put(("error", str(e)))

        thread = threading.Thread(target=_hermes_worker, daemon=True)
        thread.start()

        # 主线程负责所有 SSE 写入（线程安全）
        try:
            while True:
                event_type, data = q.get(timeout=timeout + 30)
                if event_type == "token":
                    self._send_sse({"type": "token", "content": data})
                elif event_type == "done":
                    self._send_sse({"type": "done", "success": data})
                    break
                elif event_type == "error":
                    self._send_sse({"type": "error", "message": data})
                    self._send_sse({"type": "done"})
                    break
        except queue.Empty:
            self._send_sse({"type": "error", "message": "Hermes 调用超时"})
            self._send_sse({"type": "done"})
        finally:
            thread.join(timeout=5)
