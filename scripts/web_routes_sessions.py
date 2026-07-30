#!/usr/bin/env python3
"""web_routes_sessions.py — 会话/消息路由 Mixin。

提供 SessionRoutesMixin，封装与会话管理、消息收发、历史搜索相关的全部 HTTP 路由：
    - GET  /api/sessions                      会话列表
    - GET  /api/sessions/{sid}/messages       会话历史消息
    - GET  /api/sessions/{sid}/keywords       会话关键词
    - GET  /api/history                       历史搜索
    - GET  /api/archive-index                 归档索引
    - POST /api/sessions                      创建会话
    - POST /api/sessions/{sid}/messages       发送消息（SSE 流式输出）
    - PUT  /api/sessions/{sid}/messages/{mid} 编辑消息
    - DELETE /api/sessions/{sid}/messages/{mid} 删除消息

路由表格式：(HTTP方法, re.compile(正则), handler名)
handler 签名：GET/DELETE → (self, parsed, **path_params)
             POST/PUT   → (self, parsed, body, **path_params)

self 是最终 RequestHandler 实例，可调用 _send_json / _send_sse 等基类方法。
仅使用 Python 标准库。
"""

import json
import queue
import re
import threading
import time
from typing import Any, Dict, Tuple
from urllib.parse import parse_qs

import web_base
from web_base import _log, _get_file_lock, split_response_stream, _update_memory_async

import session_manager as sm
import context_builder as cb
import copilot_engine as ce
import usage_tracker as ut
import chat_archive as ca
import backup_manager as bm  # _delete_message 删除前备份
import common as _cms  # P1-3: 原子化 JSON 写入


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_SESSION_ROUTES = [
    # GET
    ("GET", re.compile(r"^/api/sessions$"), "_sess_list"),
    ("GET", re.compile(r"^/api/sessions/(?P<sid>[^/]+)/messages$"), "_sess_messages"),
    ("GET", re.compile(r"^/api/sessions/(?P<sid>[^/]+)/keywords$"), "_sess_keywords"),
    ("GET", re.compile(r"^/api/history$"), "_sess_history"),
    ("GET", re.compile(r"^/api/archive-index$"), "_sess_archive_index"),
    # POST
    ("POST", re.compile(r"^/api/sessions$"), "_sess_create"),
    ("POST", re.compile(r"^/api/sessions/(?P<sid>[^/]+)/messages$"), "_sess_send_message"),
    # PUT
    ("PUT", re.compile(r"^/api/sessions/(?P<sid>[^/]+)/messages/(?P<msg_id>[^/]+)$"), "_sess_edit_message"),
    # DELETE
    ("DELETE", re.compile(r"^/api/sessions/(?P<sid>[^/]+)/messages/(?P<msg_id>[^/]+)$"), "_sess_delete_message"),
    ("DELETE", re.compile(r"^/api/sessions/(?P<sid>[^/]+)$"), "_sess_delete_session"),
]


# ---------------------------------------------------------------------------
# 模块级辅助函数（消息编辑/删除）
# ---------------------------------------------------------------------------
def _edit_message(session_id: str, msg_id: str, new_content: str) -> bool:
    """编辑指定消息。"""
    # P1-1: 路径遍历防护
    try:
        from web_base import _safe_join
        msg_path = _safe_join(web_base._PROJECT_ROOT / "sessions", session_id, "messages.json")
    except ValueError:
        return False
    if not msg_path.exists():
        return False
    lock = _get_file_lock(str(msg_path))  # P1-9: 文件锁
    try:
        with lock:
            with open(msg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            messages = data if isinstance(data, list) else data.get("messages", [])
            for msg in messages:
                if msg.get("msg_id") == msg_id:
                    msg["content"] = new_content
                    break
            else:
                return False
            _cms.save_json(msg_path,
                          data if isinstance(data, list) else {"messages": messages})
            return True
    except Exception:
        return False


def _delete_message(session_id: str, msg_id: str) -> bool:
    """删除指定消息（P0-9: 删除前自动备份）。"""
    # P1-1: 路径遍历防护
    try:
        from web_base import _safe_join
        msg_path = _safe_join(web_base._PROJECT_ROOT / "sessions", session_id, "messages.json")
    except ValueError:
        return False
    if not msg_path.exists():
        return False
    lock = _get_file_lock(str(msg_path))  # P1-9: 文件锁
    try:
        with lock:
            with open(msg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            messages = data if isinstance(data, list) else data.get("messages", [])
            original_len = len(messages)
            messages = [m for m in messages if m.get("msg_id") != msg_id]
            if len(messages) == original_len:
                return False
            # P0-9: 删除前备份
            try:
                bm.create_backup(targets=["sessions"], label="pre-delete-msg")
            except Exception as e:
                if _log:
                    _log.debug("删除前备份失败: %s", e)
            _cms.save_json(msg_path,
                          data if isinstance(data, list) else {"messages": messages})
            return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class SessionRoutesMixin:
    """会话/消息路由 Mixin。"""

    # --- GET ---

    def _sess_list(self, parsed):
        """会话列表"""
        sessions = sm.list_sessions()
        self._send_json([{
            "session_id": s["session_id"],
            "topic": s.get("topic", ""),
            "mode": s.get("mode", "co-working"),
            "message_count": s.get("message_count", 0),
            "last_active": s.get("last_active", ""),
        } for s in sessions])

    def _sess_messages(self, parsed, sid):
        """会话历史消息"""
        messages, state = sm.load_session(sid)
        # 兼容两种 messages.json 格式
        if isinstance(messages, dict):
            messages = messages.get("messages", [])
        self._send_json({
            "session_id": sid,
            "topic": state.get("topic", ""),
            "mode": state.get("mode", "co-working"),
            "project_id": state.get("project_id", ""),
            "messages": messages,
        })

    def _sess_keywords(self, parsed, sid):
        """会话关键词"""
        kws = ca.get_session_keywords(sid)
        self._send_json({"session_id": sid, "keywords": kws})

    def _sess_history(self, parsed):
        """历史搜索"""
        query = parse_qs(parsed.query).get("q", [""])[0]
        results = ca.search_history(query)
        self._send_json({"query": query, "results": results})

    def _sess_archive_index(self, parsed):
        """归档索引"""
        idx = ca.get_archive_index()
        self._send_json(idx)

    # --- POST ---

    def _sess_create(self, parsed, body):
        """创建会话"""
        topic = body.get("topic", "新会话")
        mode = body.get("mode", "co-working")
        sid, _ = sm.create_session(topic, mode)
        self._send_json({"session_id": sid, "topic": topic, "mode": mode})

    def _sess_send_message(self, parsed, body, sid):
        """发送消息（SSE 流式返回）"""
        user_input = body.get("content", "").strip()
        mode = body.get("mode", "co-working")

        if not user_input:
            self._send_json({"error": "内容不能为空"}, 400)
            return

        # 保存用户消息
        sm.append_message(sid, "user", user_input, mode)

        # 进入 SSE 流
        self._send_sse_header()

        q: "queue.Queue[Tuple[str, Any]]" = queue.Queue()

        def llm_worker() -> None:
            """在后台线程调用 LLM，支持工具调用。"""
            try:
                context = cb.build_context(sid, user_input, mode)
                system_prompt = context.get("system_prompt", "")
                messages = context.get("messages", [])

                # v3.4: 发送知识库命中元数据（供前端展示引用来源）
                kb_hits = context.get("kb_hits", [])
                if kb_hits:
                    q.put(("metadata", {"kb_hits": kb_hits}))

                # 调用 LLM（支持工具调用）
                response, usage, provider_name, tool_log = ce.call_llm_with_tools(system_prompt, messages)

                if not response or not response.strip():
                    q.put(("error", "LLM 返回为空"))
                    return

                # 如果有工具调用，先发送工具事件
                if tool_log:
                    q.put(("tools", tool_log))

                # 记录 token 用量
                try:
                    full_prompt = system_prompt + "\n".join(m.get("content", "") for m in messages)
                    ut.record_usage(sid, provider_name, full_prompt, response, usage)
                except Exception as e:
                    if _log:
                        _log.debug("记录 token 用量失败: %s", e)

                # 切分并流式输出
                chunks = split_response_stream(response)
                for chunk in chunks:
                    q.put(("token", chunk))
                    # 模拟打字延迟
                    delay = max(0.02, min(0.08, len(chunk) * 0.01))
                    time.sleep(delay)

                q.put(("done", response.strip()))
            except Exception as e:
                if _log:
                    _log.error(f"LLM 调用失败: {e}", exc_info=True)
                q.put(("error", str(e)))

        thread = threading.Thread(target=llm_worker)
        thread.start()

        full_response = ""
        while True:
            event_type, data = q.get()
            if event_type == "token":
                self._send_sse({"type": "token", "content": data})
                full_response += data
            elif event_type == "tools":
                self._send_sse({"type": "tools", "calls": data})
            elif event_type == "metadata":
                # v3.4: 知识库命中元数据
                self._send_sse({"type": "metadata", **data})
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

    # --- PUT ---

    def _sess_edit_message(self, parsed, body, sid, msg_id):
        """编辑消息"""
        new_content = body.get("content", "").strip()
        if not new_content:
            self._send_json({"error": "内容不能为空"}, 400)
            return
        ok = _edit_message(sid, msg_id, new_content)
        if ok:
            self._send_json({"success": True})
        else:
            self._send_json({"error": "消息未找到"}, 404)

    # --- DELETE ---

    def _sess_delete_message(self, parsed, sid, msg_id):
        """删除消息"""
        ok = _delete_message(sid, msg_id)
        if ok:
            self._send_json({"success": True})
        else:
            self._send_json({"error": "消息未找到"}, 404)

    def _sess_delete_session(self, parsed, sid):
        """删除会话（含备份）"""
        ok = sm.delete_session(sid)
        if ok:
            self._send_json({"success": True})
        else:
            self._send_json({"error": "会话未找到或删除失败"}, 404)
