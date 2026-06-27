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

import re
import threading

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
        """hermes 手动派活（oneshot agent loop，SSE 流式返回）"""
        prompt = body.get("prompt", "").strip()
        if not prompt:
            self._send_json({"error": "缺少 prompt"}, 400)
            return
        timeout = int(body.get("timeout", 300))
        # 在后台线程执行（agent loop 较慢），通过 SSE 返回
        self._send_sse_header()

        def _hermes_worker():
            try:
                result = hb.oneshot(prompt, timeout=timeout)
                for chunk in split_response_stream(result.get("output", "") or result.get("error", "")):
                    self._send_sse({"type": "token", "content": chunk})
                self._send_sse({"type": "done", "success": result["success"]})
            except Exception as e:
                self._send_sse({"type": "error", "message": str(e)})
            finally:
                # 修复：原 _send_sse_raw 不存在，改为 _send_sse
                self._send_sse({"type": "done"})
                self.wfile.flush()

        threading.Thread(target=_hermes_worker, daemon=True).start()
