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
from pathlib import Path
from typing import Any, Tuple

from web_base import _log, split_response_stream

import hermes_bridge as hb


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_HERMES_ROUTES = [
    # GET
    ("GET", re.compile(r"^/api/hermes/cron$"), "_her_cron_list"),
    ("GET", re.compile(r"^/api/hermes/profiles$"), "_her_profiles"),
    ("GET", re.compile(r"^/api/hermes/profiles/(?P<profile>[^/]+)/model$"), "_her_profile_model_get"),
    # POST（GET 重复 + 独有）
    ("POST", re.compile(r"^/api/hermes/cron$"), "_her_cron_list"),
    ("POST", re.compile(r"^/api/hermes/cron/(?P<job_id>[^/]+)/(?P<action>pause|resume|run)$"), "_her_cron_control"),
    ("POST", re.compile(r"^/api/hermes/run$"), "_her_run"),
    ("POST", re.compile(r"^/api/hermes/profiles/(?P<profile>[^/]+)/model$"), "_her_profile_model_set"),
]

# 允许前端切换的模型选项
_HERMES_MODEL_OPTIONS = [
    {"provider": "minimax-cn", "model": "MiniMax-M3", "label": "MiniMax-M3"},
    {"provider": "minimax-cn", "model": "MiniMax-M2.7", "label": "MiniMax-M2.7"},
    {"provider": "zai", "model": "glm-5.2", "label": "GLM-5.2"},
    {"provider": "zai", "model": "glm-5.1", "label": "GLM-5.1"},
    {"provider": "kimi-for-coding", "model": "k2.7 code", "label": "Kimi k2.7 code"},
]


def _profile_config_path(profile: str) -> Path:
    return Path.home() / ".hermes" / "profiles" / profile / "config.yaml"


def _read_profile_model(profile: str) -> dict:
    cfg = _profile_config_path(profile)
    if not cfg.exists():
        return {"error": "profile 不存在"}
    text = cfg.read_text(encoding="utf-8")
    default = re.search(r"^  default: (.*)$", text, re.MULTILINE)
    provider = re.search(r"^  provider: (.*)$", text, re.MULTILINE)
    return {
        "provider": provider.group(1).strip() if provider else "",
        "model": default.group(1).strip() if default else "",
        "options": _HERMES_MODEL_OPTIONS,
    }


def _write_profile_model(profile: str, provider: str, model: str) -> dict:
    cfg = _profile_config_path(profile)
    if not cfg.exists():
        return {"success": False, "error": "profile 不存在"}
    text = cfg.read_text(encoding="utf-8")

    # 更新 model 主模型
    text = re.sub(
        r"^model:\n  default: .*\n  provider: .*\n",
        f"model:\n  default: {model}\n  provider: {provider}\n",
        text,
        flags=re.MULTILINE,
    )

    # 更新 fallback_providers：当前选择以外的所有选项作为 fallback
    others = [opt for opt in _HERMES_MODEL_OPTIONS
              if not (opt["provider"] == provider and opt["model"] == model)]
    fb_lines = ["fallback_providers:"]
    for opt in others:
        fb_lines.append(f"- provider: {opt['provider']}")
        fb_lines.append(f"  model: {opt['model']}")
    fb_block = "\n".join(fb_lines) + "\n"

    text = re.sub(
        r"^fallback_providers:\n(?:- provider: .*\n  model: .*\n)*",
        fb_block,
        text,
        flags=re.MULTILINE,
    )

    cfg.write_text(text, encoding="utf-8")
    return {"success": True, "profile": profile, "provider": provider, "model": model}


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class HermesRoutesMixin:
    """Hermes 路由 Mixin。"""

    def _her_cron_list(self, parsed, body=None):
        """hermes cron job 列表（GET+POST 重复）"""
        self._send_json({"jobs": hb.cron_list(), "status": hb.check_hermes_available()})

    def _her_profiles(self, parsed, body=None, **kwargs):
        """团队 profile 状态面板（v6.6.0）"""
        try:
            profiles = hb.list_team_profiles()
            self._send_json({"status": "ok", "profiles": profiles})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _her_profile_model_get(self, parsed, body=None, profile=None, **kwargs):
        """GET /api/hermes/profiles/{profile}/model — 读取主模型配置。"""
        try:
            result = _read_profile_model(profile)
            if "error" in result:
                self._send_json(result, 404)
            else:
                self._send_json({"status": "ok", **result})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _her_profile_model_set(self, parsed, body, profile=None, **kwargs):
        """POST /api/hermes/profiles/{profile}/model — 切换主模型与 fallback。"""
        try:
            provider = body.get("provider", "").strip()
            model = body.get("model", "").strip()
            if not provider or not model:
                self._send_json({"error": "缺少 provider 或 model"}, 400)
                return
            valid = any(opt["provider"] == provider and opt["model"] == model
                        for opt in _HERMES_MODEL_OPTIONS)
            if not valid:
                self._send_json({"error": "不支持的模型组合"}, 400)
                return
            result = _write_profile_model(profile, provider, model)
            if result.get("success"):
                self._send_json({"status": "ok", **result})
            else:
                self._send_json(result, 400)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

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
