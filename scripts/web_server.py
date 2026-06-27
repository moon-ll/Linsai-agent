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
import base64
import datetime
import json
import os
import platform
import queue
import re
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, unquote, urlparse

# 统一日志
try:
    from logger import get_logger, setup_logging
    setup_logging()
    _log = get_logger("web_server")
except Exception:
    _log = None


# ---------------------------------------------------------------------------
# 路径与导入
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
_WEB_DIR = _PROJECT_ROOT / "web"

# 确保项目脚本可被导入
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import agora_bridge as ab
import chat_archive as ca
import context_builder as cb
import copilot_engine as ce
import document_handler as dh
import knowledge_base as kb
import llm_router as lr
import memory_manager as mm
import proactive_engine as pe
import session_manager as sm
import skill_manager as skm
import task_manager as tm
# v2.7.0: hermes 协作中枢模块
import project_reader as pr
import kb_importer as ki
import hermes_bridge as hb
import sync_engine as se
import paper_pool as pp  # v2.9.1: 候选池
import kb_categories as kbc  # v3.1: 自定义分类
import project_dispatch as pdh  # v3.1.0: 项目意见 + 执行追踪
import usage_tracker as ut
import backup_manager as bm  # v3.4.1: 提升为顶层导入，消除 3 处局部重复
from common import lazy_load  # v3.4.1: 统一懒加载，消除 6 处 importlib 样板
import common as _cms  # v3.5.2: 原子写入 + 并发锁
# v3.5: 课题指导模块
import project_manager as pjm
import unit_manager as um
import project_kb as pkb
import project_memory as pmm
import project_workflow as pwf
import project_context as pctx

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


# ---------------------------------------------------------------------------
# v3.1.0: 项目总控 — hermes 反馈落点（plans/ 目录契约）+ 异步派活 worker
# ---------------------------------------------------------------------------
# hermes 工作区 plans/ 目录是 hermes 已声明的"按 task 顺序执行"契约入口
# （见 ~/Desktop/hermes_workspace/plans/ 文件头声明 "For Hermes: 按 task 顺序执行"）
_HERMES_PLANS_DIR = pr.HERMES_WORKSPACE / "plans"


def _write_dispatch_to_hermes_plans(prompt: str, project: str, dispatch_id: str) -> str:
    """把派活指令写入 hermes plans/ 目录（跨进程文件契约，让 hermes 能读到）。

    文件名：{date}_linSai-dispatch.md（与 hermes cron 的 {date}_*.md 约定一致）
    返回写入的相对路径（失败返回空串，不抛异常）。
    """
    try:
        _HERMES_PLANS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        fname = f"{today}_linSai-dispatch.md"
        fpath = _HERMES_PLANS_DIR / fname
        # 文件头契约：For Hermes 声明 + Task 结构
        entry = (
            f"\n\n## Task: {prompt[:80]}{'...' if len(prompt) > 80 else ''} 🌐 林赛CoPilot派活\n\n"
            f"> **For Hermes:** 林赛 CoPilot 用户从项目总控派发的任务，请执行后更新对应项目状态。\n"
            f"> **关联项目**: {project or '通用'}\n"
            f"> **派活ID**: {dispatch_id}\n"
            f"> **时间**: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n\n"
            f"**任务指令**:\n\n{prompt}\n\n"
            f"---\n"
        )
        # 追加（同一天可能多个派活）
        mode = "a" if fpath.exists() else "w"
        with _get_file_lock(f"plans_{fname}"):
            with open(fpath, mode, encoding="utf-8") as f:
                f.write(entry)
        return f"plans/{fname}"
    except OSError:
        return ""


def _dispatch_hermes_async(dispatch_id: str, prompt: str, timeout: int = 300) -> None:
    """异步派活给 hermes 并回写结果（daemon 线程，异常吞掉，结果写 project-dispatch.json）。

    这是补齐 oneshot fire-and-forget 缺口的关键：oneshot 完成后把成功/失败/输出回写到
    dispatch 记录，前端可通过 GET /api/projects/dispatches 查询状态。
    """
    try:
        is_timeout = False
        result = hb.oneshot(prompt, timeout=timeout)
        if not result.get("success") and "超时" in result.get("error", ""):
            is_timeout = True
        pdh.finish_dispatch(
            dispatch_id,
            success=result.get("success", False),
            output=result.get("output") or result.get("error", ""),
            timeout=is_timeout,
        )
    except Exception as e:
        pdh.finish_dispatch(dispatch_id, success=False, output=f"派活线程异常: {e}")

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


# ---------------------------------------------------------------------------
# v3.5.1: 课题指导模块路由表（路由表模式验证）
# 后续迭代逐步将其他路由迁移到此模式
# 每条规则: (HTTP方法, URL正则模式, handler函数名)
# handler 签名: GET/DELETE → (self, path, parsed, match)
#               POST/PUT   → (self, path, parsed, body, match)
# 返回 True 表示已处理（由 _dispatch_research_routes 调用）
# ---------------------------------------------------------------------------

_RESEARCH_ROUTES = [
    # GET
    ("GET", r"^/api/research/projects$", "_rg_get_projects"),
    ("GET", r"^/api/research/projects/([^/]+)$", "_rg_get_project"),
    ("GET", r"^/api/research/projects/([^/]+)/status$", "_rg_get_project_status"),
    ("GET", r"^/api/research/projects/([^/]+)/units$", "_rg_get_units"),
    ("GET", r"^/api/research/projects/([^/]+)/units/([^/]+)$", "_rg_get_unit"),
    ("GET", r"^/api/research/projects/([^/]+)/kb/documents$", "_rg_get_kb_documents"),
    ("GET", r"^/api/research/projects/([^/]+)/kb/search$", "_rg_get_kb_search"),
    ("GET", r"^/api/research/projects/([^/]+)/kb/stats$", "_rg_get_kb_stats"),
    ("GET", r"^/api/research/projects/([^/]+)/kb/tags$", "_rg_get_kb_tags"),
    ("GET", r"^/api/research/projects/([^/]+)/kb/doc/(.+)$", "_rg_get_kb_doc"),
    ("GET", r"^/api/research/projects/([^/]+)/memory$", "_rg_get_memory"),
    ("GET", r"^/api/research/projects/([^/]+)/memory/stats$", "_rg_get_memory_stats"),
    ("GET", r"^/api/research/projects/([^/]+)/memory/snippets$", "_rg_get_memory_snippets"),
    ("GET", r"^/api/research/projects/([^/]+)/memory/conversations$", "_rg_get_memory_conversations"),
    ("GET", r"^/api/research/projects/([^/]+)/memory/file$", "_rg_get_memory_file"),
    ("GET", r"^/api/research/search$", "_rg_get_cross_search"),
    # POST
    ("POST", r"^/api/research/projects$", "_rg_post_project"),
    ("POST", r"^/api/research/projects/([^/]+)/units$", "_rg_post_unit"),
    ("POST", r"^/api/research/projects/([^/]+)/kb/documents$", "_rg_post_kb_document"),
    ("POST", r"^/api/research/projects/([^/]+)/kb/import$", "_rg_post_kb_import"),
    ("POST", r"^/api/research/projects/([^/]+)/memory/snippets$", "_rg_post_memory_snippet"),
    ("POST", r"^/api/research/projects/([^/]+)/memory/conversations$", "_rg_post_memory_conversation"),
    ("POST", r"^/api/research/projects/([^/]+)/memory/decisions$", "_rg_post_memory_decision"),
    ("POST", r"^/api/research/projects/([^/]+)/workflow/plan$", "_rg_post_workflow_plan"),
    ("POST", r"^/api/research/projects/([^/]+)/workflow/ai-plan$", "_rg_post_workflow_ai_plan"),
    ("POST", r"^/api/research/projects/([^/]+)/workflow/execute$", "_rg_post_workflow_execute"),
    ("POST", r"^/api/research/projects/([^/]+)/workflow/review$", "_rg_post_workflow_review"),
    ("POST", r"^/api/research/projects/([^/]+)/workflow/complete$", "_rg_post_workflow_complete"),
    ("POST", r"^/api/research/projects/([^/]+)/workflow/summary$", "_rg_post_workflow_summary"),
    # PUT（更具体的路由放在前面，通用路由放后面）
    ("PUT", r"^/api/research/projects/([^/]+)/transition$", "_rg_put_project_transition"),
    ("PUT", r"^/api/research/projects/([^/]+)/units/([^/]+)/transition$", "_rg_put_unit_transition"),
    ("PUT", r"^/api/research/projects/([^/]+)/units/([^/]+)/acceptance/([^/]+)$", "_rg_put_acceptance"),
    ("PUT", r"^/api/research/projects/([^/]+)/memory/file$", "_rg_put_memory_file"),
    ("PUT", r"^/api/research/projects/([^/]+)/units/([^/]+)$", "_rg_put_unit"),
    ("PUT", r"^/api/research/projects/([^/]+)$", "_rg_put_project"),
    # DELETE（更具体的路由放在前面）
    ("DELETE", r"^/api/research/projects/([^/]+)/units/([^/]+)$", "_rg_delete_unit"),
    ("DELETE", r"^/api/research/projects/([^/]+)$", "_rg_delete_project"),
]


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

    # ============================================================
    # v3.5.1: 课题指导模块路由表分发 + handler（_rg_* 系列）
    # ============================================================

    def _dispatch_research_routes(self, method, path, parsed, body=None):
        """v3.5.1: 课题指导模块路由表分发。返回 True 表示已处理。"""
        for m, pattern, handler_name in _RESEARCH_ROUTES:
            if m != method:
                continue
            match = re.match(pattern, path)
            if match:
                handler = getattr(self, handler_name, None)
                if handler:
                    if body is not None:
                        handler(path, parsed, body, match)
                    else:
                        handler(path, parsed, match)
                    return True
        return False

    # --- GET handlers ---

    def _rg_get_projects(self, path, parsed, match):
        """课题列表"""
        self._send_json({"projects": pjm.list_projects()})

    def _rg_get_project(self, path, parsed, match):
        """课题详情"""
        pid = match.group(1)
        try:
            self._send_json(pjm.get_project(pid))
        except FileNotFoundError:
            self._send_json({"error": f"课题不存在: {pid}"}, 404)

    def _rg_get_project_status(self, path, parsed, match):
        """课题状态概览"""
        pid = match.group(1)
        try:
            self._send_json(pwf.get_project_status(pid))
        except FileNotFoundError:
            self._send_json({"error": f"课题不存在: {pid}"}, 404)

    def _rg_get_units(self, path, parsed, match):
        """单元列表"""
        pid = match.group(1)
        self._send_json({"units": um.list_units(pid)})

    def _rg_get_unit(self, path, parsed, match):
        """单元详情"""
        pid, uid = match.group(1), match.group(2)
        try:
            self._send_json(um.get_unit(uid))
        except FileNotFoundError:
            self._send_json({"error": f"单元不存在: {uid}"}, 404)

    def _rg_get_kb_documents(self, path, parsed, match):
        """知识库文档列表（支持 ?layer=&type=&tag=&unit= 过滤）"""
        pid = match.group(1)
        qs = parse_qs(parsed.query)
        docs = pkb.list_documents(
            pid,
            layer=qs.get("layer", ["all"])[0],
            doc_type=qs.get("type", [""])[0],
            tag=qs.get("tag", [""])[0],
            unit=qs.get("unit", [""])[0],
        )
        self._send_json({"documents": docs})

    def _rg_get_kb_search(self, path, parsed, match):
        """知识库搜索（?q=&layer=）"""
        pid = match.group(1)
        qs = parse_qs(parsed.query)
        q = qs.get("q", [""])[0]
        layer = qs.get("layer", ["all"])[0]
        results = pkb.search(pid, q, layer=layer) if q else []
        self._send_json({"results": results})

    def _rg_get_kb_stats(self, path, parsed, match):
        """知识库统计"""
        pid = match.group(1)
        self._send_json(pkb.get_kb_stats(pid))

    def _rg_get_kb_tags(self, path, parsed, match):
        """知识库标签列表"""
        pid = match.group(1)
        self._send_json({"tags": pkb.get_tags(pid)})

    def _rg_get_kb_doc(self, path, parsed, match):
        """知识库文档详情（path 参数是文档相对路径，URL 编码）"""
        pid, doc_path = match.group(1), match.group(2)
        doc = pkb.get_document(pid, doc_path)
        if doc:
            self._send_json(doc)
        else:
            self._send_json({"error": "文档不存在"}, 404)

    def _rg_get_memory(self, path, parsed, match):
        """课题记忆上下文"""
        pid = match.group(1)
        self._send_json({"context": pmm.get_project_context(pid)})

    def _rg_get_memory_stats(self, path, parsed, match):
        """课题记忆统计"""
        pid = match.group(1)
        self._send_json(pmm.get_memory_stats(pid))

    def _rg_get_memory_snippets(self, path, parsed, match):
        """课题记忆片段列表"""
        pid = match.group(1)
        self._send_json({"snippets": pmm.list_snippets(pid)})

    def _rg_get_memory_conversations(self, path, parsed, match):
        """课题对话记录列表"""
        pid = match.group(1)
        self._send_json({"conversations": pmm.list_conversations(pid)})

    def _rg_get_memory_file(self, path, parsed, match):
        """课题长期记忆文件全文"""
        pid = match.group(1)
        self._send_json({"content": pjm.get_project_memory(pid)})

    def _rg_get_cross_search(self, path, parsed, match):
        """跨课题搜索"""
        qs = parse_qs(parsed.query)
        q = qs.get("q", [""])[0]
        results = pctx.search_across_projects(q) if q else []
        self._send_json({"results": results})

    # --- POST handlers ---

    def _rg_post_project(self, path, parsed, body, match):
        """创建课题"""
        try:
            pid, _ = pjm.create_project(
                body.get("name", "新课题"),
                goal=body.get("goal", ""),
                description=body.get("description", ""),
            )
            self._send_json({"project_id": pid})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_unit(self, path, parsed, body, match):
        """创建单元"""
        pid = match.group(1)
        try:
            uid, _ = um.create_unit(
                pid,
                body.get("title", "新单元"),
                acceptance_criteria=body.get("acceptance_criteria", []),
                description=body.get("description", ""),
            )
            self._send_json({"unit_id": uid})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_kb_document(self, path, parsed, body, match):
        """知识库添加文档"""
        pid = match.group(1)
        try:
            rel_path = pkb.add_document(
                pid,
                layer=body.get("layer", ""),
                doc_type=body.get("doc_type", "references"),
                title=body.get("title", "未命名文档"),
                content=body.get("content", ""),
                tags=body.get("tags", []),
                unit=body.get("unit", ""),
                source_raw=body.get("source_raw", ""),
            )
            self._send_json({"path": rel_path})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_kb_import(self, path, parsed, body, match):
        """知识库导入外部文件"""
        pid = match.group(1)
        try:
            rel_path = pkb.import_raw_file(
                pid,
                body.get("source_path", ""),
                doc_type=body.get("doc_type", "references"),
                title=body.get("title", ""),
                tags=body.get("tags", []),
            )
            self._send_json({"path": rel_path})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_memory_snippet(self, path, parsed, body, match):
        """添加记忆片段"""
        pid = match.group(1)
        try:
            pmm.create_snippet(
                pid,
                trigger=body.get("trigger", ""),
                summary=body.get("summary", ""),
                source=body.get("source", ""),
                importance=body.get("importance", 3),
            )
            self._send_json({"success": True})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_memory_conversation(self, path, parsed, body, match):
        """保存对话记录"""
        pid = match.group(1)
        try:
            pmm.save_conversation(
                pid,
                body.get("session_id", ""),
                body.get("messages", []),
                summary=body.get("summary", ""),
            )
            self._send_json({"success": True})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_memory_decision(self, path, parsed, body, match):
        """添加决策记录"""
        pid = match.group(1)
        try:
            pmm.add_decision(
                pid,
                title=body.get("title", ""),
                rationale=body.get("rationale", ""),
                unit_id=body.get("unit_id", ""),
            )
            self._send_json({"success": True})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_workflow_plan(self, path, parsed, body, match):
        """工作流：规划单元（批量）"""
        pid = match.group(1)
        try:
            unit_ids = pwf.plan_units(pid, body.get("unit_specs", []))
            self._send_json({"unit_ids": unit_ids})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_workflow_ai_plan(self, path, parsed, body, match):
        """工作流：AI 主动规划单元（返回建议，不直接创建）"""
        pid = match.group(1)
        try:
            result = pwf.ai_plan_units(pid, max_units=body.get("max_units", 5))
            self._send_json(result)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_workflow_execute(self, path, parsed, body, match):
        """工作流：开始单元执行（创建任务）"""
        pid = match.group(1)
        try:
            task_ids = pwf.start_unit_execution(
                pid,
                body.get("unit_id", ""),
                body.get("task_specs", []),
            )
            self._send_json({"task_ids": task_ids})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_workflow_review(self, path, parsed, body, match):
        """工作流：单元验收"""
        pid = match.group(1)
        try:
            result = pwf.review_unit(pid, body.get("unit_id", ""))
            self._send_json(result)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_workflow_complete(self, path, parsed, body, match):
        """工作流：完成单元"""
        pid = match.group(1)
        try:
            result = pwf.complete_unit(
                pid,
                body.get("unit_id", ""),
                review_notes=body.get("review_notes", ""),
                report_content=body.get("report_content", ""),
            )
            self._send_json(result)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_workflow_summary(self, path, parsed, body, match):
        """工作流：生成课题总结"""
        pid = match.group(1)
        try:
            report_path = pwf.generate_project_summary(pid)
            self._send_json({"path": report_path})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    # --- PUT handlers ---

    def _rg_put_project(self, path, parsed, body, match):
        """更新课题"""
        pid = match.group(1)
        try:
            updated = pjm.update_project(pid, **body)
            self._send_json({"success": True, "project": updated})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_put_project_transition(self, path, parsed, body, match):
        """课题状态流转"""
        pid = match.group(1)
        try:
            updated = pjm.transition_project(pid, body.get("status", ""))
            self._send_json({"success": True, "project": updated})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_put_unit(self, path, parsed, body, match):
        """更新单元"""
        pid, uid = match.group(1), match.group(2)
        try:
            updated = um.update_unit(uid, **body)
            self._send_json({"success": True, "unit": updated})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_put_unit_transition(self, path, parsed, body, match):
        """单元状态流转"""
        pid, uid = match.group(1), match.group(2)
        try:
            updated = um.transition_unit(uid, body.get("status", ""))
            self._send_json({"success": True, "unit": updated})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_put_acceptance(self, path, parsed, body, match):
        """验收标准勾选"""
        pid, uid, ac_id = match.group(1), match.group(2), match.group(3)
        try:
            updated = um.check_acceptance_criterion(
                uid, ac_id,
                met=body.get("met", True),
                notes=body.get("notes", ""),
            )
            self._send_json({"success": True, "unit": updated})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_put_memory_file(self, path, parsed, body, match):
        """更新课题长期记忆文件"""
        pid = match.group(1)
        try:
            pjm.update_project_memory(pid, body.get("content", ""))
            self._send_json({"success": True})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    # --- DELETE handlers ---

    def _rg_delete_project(self, path, parsed, match):
        """删除课题"""
        pid = match.group(1)
        try:
            ok = pjm.delete_project(pid, confirm=True)
            if ok:
                self._send_json({"success": True})
            else:
                self._send_json({"error": "删除失败"}, 500)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_delete_unit(self, path, parsed, match):
        """删除单元"""
        pid, uid = match.group(1), match.group(2)
        try:
            ok = um.delete_unit(uid, confirm=True)
            if ok:
                self._send_json({"success": True})
            else:
                self._send_json({"error": "删除失败"}, 500)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

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

        # v3.5.1: 课题模块路由表分发
        if self._dispatch_research_routes("GET", path, parsed):
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

        # 单个任务详情
        if path.startswith("/api/tasks/") and len(path.split("/")) == 4:
            tid = path[len("/api/tasks/"):]
            try:
                task = tm.get_task(tid)
                self._send_json(task)
            except FileNotFoundError:
                self._send_json({"error": f"任务不存在: {tid}"}, 404)
            return

        if path == "/api/heartbeat":
            try:
                reminders = pe.heartbeat()
                # v3.4: 生成主动消息文案，让前端可直接展示
                messages = []
                for sig in reminders[:3]:
                    try:
                        msg = pe.generate_proactive_message(sig)
                        messages.append({"type": sig.get("type",""), "severity": sig.get("severity","low"), "message": msg})
                    except Exception as e:
                        if _log: _log.debug("生成主动消息失败: %s", e)
                self._send_json({"status": "ok", "reminders": reminders, "proactive_messages": messages})
            except Exception as e:
                self._send_json({"status": "ok", "reminders": [], "proactive_messages": [], "error": str(e)})
            return

        # v3.4: 记忆系统状态 API
        if path == "/api/memory/status":
            try:
                from memory_reflow import get_memory_status
                status = get_memory_status()
                self._send_json(status)
            except Exception as e:
                self._send_json({"error": str(e)})
            return

        # v3.4: 手动触发认知回流
        if path == "/api/memory/reflow":
            try:
                from memory_reflow import reflow_all
                result = reflow_all(max_count=20)
                self._send_json({"success": True, "result": result})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)})
            return

        if path == "/api/references":
            refs = _list_references()
            self._send_json(refs)
            return

        # 会话关键词
        if path.startswith("/api/sessions/") and path.endswith("/keywords"):
            sid = path[len("/api/sessions/") : -len("/keywords")]
            kws = ca.get_session_keywords(sid)
            self._send_json({"session_id": sid, "keywords": kws})
            return

        # 历史搜索
        if path == "/api/history":
            query = parse_qs(parsed.query).get("q", [""])[0]
            results = ca.search_history(query)
            self._send_json({"query": query, "results": results})
            return

        # 归档索引
        if path == "/api/archive-index":
            idx = ca.get_archive_index()
            self._send_json(idx)
            return

        if path == "/api/llm-status":
            try:
                self._send_json(lr.get_status())
            except Exception as e:
                self._send_json({"provider": "none", "model": "未配置", "error": str(e)})
            return

        # Provider 列表
        if path == "/api/providers":
            status = lr.get_status()
            self._send_json({
                "providers": status.get("providers", [])
            })
            return

        # 当前 Provider
        if path == "/api/providers/current":
            status = lr.get_status()
            self._send_json({
                "current": status.get("force_provider") or "auto"
            })
            return

        # Token 用量统计
        if path == "/api/usage":
            self._send_json(ut.get_usage_summary())
            return

        if path == "/api/usage/daily":
            self._send_json(ut.get_stats("daily"))
            return

        # 技能系统
        if path == "/api/skills":
            self._send_json({"skills": skm.list_skills()})
            return

        if path == "/api/skills/active":
            query = parse_qs(parsed.query).get("q", [""])[0]
            self._send_json({
                "active": skm.get_active_skill_names(query),
                "all": skm.list_skills(),
            })
            return

        if path == "/api/skills/config":
            self._send_json(skm.get_skill_config())
            return

        if path == "/api/skills/search":
            query = parse_qs(parsed.query).get("q", [""])[0]
            self._send_json({"query": query, "results": skm.search_skills(query)})
            return

        # 知识库
        if path == "/api/knowledge":
            self._send_json(kb.get_index_status())
            return

        # 可用工具列表
        if path == "/api/tools":
            te_mod = lazy_load("tool_engine")
            if te_mod:
                self._send_json({"tools": te_mod.list_tools()})
            else:
                self._send_json({"tools": []})
            return

        if path == "/api/knowledge/search":
            query = parse_qs(parsed.query).get("q", [""])[0]
            source = parse_qs(parsed.query).get("source", ["all"])[0]
            top_k = int(parse_qs(parsed.query).get("top_k", ["3"])[0])
            results = kb.search(query, top_k=top_k, source=source)
            self._send_json({"query": query, "results": results})
            return

        # 知识库增强 API
        if path == "/api/knowledge/raw":
            self._send_json({"files": kb.list_raw_files()})
            return

        if path == "/api/knowledge/wiki":
            wiki_type = parse_qs(parsed.query).get("type", [None])[0]
            self._send_json({"pages": kb.list_wiki_pages(wiki_type)})
            return

        if path.startswith("/api/knowledge/wiki/"):
            wiki_rel = path[len("/api/knowledge/wiki/"):]
            page = kb.get_wiki_page(f"wiki/{wiki_rel}")
            if page:
                self._send_json(page)
            else:
                self._send_json({"error": "Wiki 页面不存在"}, 404)
            return

        if path == "/api/knowledge/graph":
            self._send_json(kb.get_graph_summary())
            return

        if path == "/api/knowledge/related":
            query = parse_qs(parsed.query).get("q", [""])[0]
            related = kb.get_related_concepts(query, depth=1)
            self._send_json({"concept": query, "related": related})
            return

        if path == "/api/knowledge/growth-log":
            limit = int(parse_qs(parsed.query).get("limit", ["50"])[0])
            self._send_json({"log": kb.get_growth_log(limit=limit)})
            return

        if path == "/api/knowledge/growth-candidates":
            self._send_json({"candidates": kb.get_growth_candidates()})
            return

        if path == "/api/knowledge/enriched":
            query = parse_qs(parsed.query).get("q", [""])[0]
            self._send_json(kb.get_enriched_context(query, top_k=3))
            return

        if path == "/api/knowledge/aliases":
            aliases_path = _PROJECT_ROOT / "knowledge" / "aliases.json"
            if aliases_path.exists():
                try:
                    with open(aliases_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._send_json({"aliases": data})
                except Exception as e:
                    self._send_json({"aliases": {}, "error": str(e)})
            else:
                self._send_json({"aliases": {}})
            return

        if path == "/api/knowledge/captures":
            try:
                kc = lazy_load("kb_capture")
                if kc:
                    self._send_json({"captures": kc.list_captures()})
                else:
                    self._send_json({"captures": []})
            except Exception as e:
                self._send_json({"captures": [], "error": str(e)})
            return

        if path == "/api/knowledge/health":
            try:
                self._send_json(kb.get_kb_health())
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # v3.1: 自定义分类 API
        if path == "/api/knowledge/categories":
            self._send_json({"categories": kbc.list_categories()})
            return

        if path == "/api/knowledge/filters":
            self._send_json(kbc.get_all_filters())
            return

        # --- 学习配置 API ---
        if path == "/api/learning/config":
            config_path = _PROJECT_ROOT / "memory" / "learning-config.json"
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._send_json(data)
                except Exception as e:
                    self._send_json({"error": str(e)}, 500)
            else:
                self._send_json({"enabled": True, "auto_review": True, "review_interval": 7})
            return

        if path == "/api/learning/status":
            try:
                cost_data = {}
                cost_path = _PROJECT_ROOT / "memory" / "learning-cost.json"
                if cost_path.exists():
                    with open(cost_path, "r", encoding="utf-8") as f:
                        cost_data = json.load(f)
                config_path = _PROJECT_ROOT / "memory" / "learning-config.json"
                config = {}
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                self._send_json({
                    "enabled": config.get("auto_enabled", False),
                    "strategy": config.get("strategy", "balanced"),
                    "today_cost": cost_data.get("daily", {}).get(datetime.now().strftime("%Y-%m-%d"), 0),
                    "month_cost": cost_data.get("monthly", {}).get(datetime.now().strftime("%Y-%m"), 0),
                    "total_calls": cost_data.get("total_calls", 0),
                    "total_tokens": cost_data.get("total_tokens", 0),
                    "today_quota_used": config.get("today_count", 0),
                    "today_quota_total": config.get("daily_quota", 1),
                    "cost_daily": cost_data.get("daily", {}),
                    "cost_monthly": cost_data.get("monthly", {}),
                    "daily_budget": config.get("cost_limit_daily", 0),
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/learning/queue":
            try:
                qe = lazy_load("quality_evaluator")
                if qe:
                    queue = qe.get_pending_queue()
                    self._send_json({"queue": queue})
                else:
                    self._send_json({"queue": []})
            except Exception as e:
                self._send_json({"queue": [], "error": str(e)})
            return

        if path == "/api/learning/log":
            try:
                log_path = _PROJECT_ROOT / "memory" / "learning-quality-log.json"
                if log_path.exists():
                    with open(log_path, "r", encoding="utf-8") as f:
                        log = json.load(f)
                    self._send_json({"log": log})
                else:
                    self._send_json({"log": []})
            except Exception as e:
                self._send_json({"log": [], "error": str(e)})
            return

        # ============================================================
        # v2.7.0: 项目面板 + hermes 协作中枢 API（GET）
        # ============================================================

        # 项目概况
        if path == "/api/projects":
            self._send_json(pr.get_projects_overview())
            return

        # v3.1.0: 项目清单（供任务表单下拉框）
        if path == "/api/projects/list":
            self._send_json({"projects": pr.get_projects_list()})
            return

        # v3.1.0: 项目总控总览（聚合进度+任务+意见+执行）
        if path == "/api/projects/overview":
            all_tasks = tm.list_tasks()
            task_by_status = {"backlog": 0, "active": 0, "completed": 0, "paused": 0}
            task_by_project: Dict[str, int] = {}
            for t in all_tasks:
                st = t.get("status", "backlog")
                task_by_status[st] = task_by_status.get(st, 0) + 1
                proj = t.get("project", "") or "通用"
                task_by_project[proj] = task_by_project.get(proj, 0) + 1
            try:
                nsfc = pr.parse_nsfc_state()
            except Exception as e:
                if _log: _log.debug("解析 NSFC 状态失败: %s", e)
                nsfc = {}
            self._send_json({
                "nsfc_phase": nsfc.get("phase", ""),
                "nsfc_available": nsfc.get("available", False),
                "task_stats": task_by_status,
                "task_by_project": task_by_project,
                "total_tasks": len(all_tasks),
                "projects": pr.get_projects_list(),
                "dispatch_stats": pdh.get_project_overview_stats(),
            })
            return

        # v3.1.0: 项目意见列表
        if path == "/api/projects/opinions":
            qs = parse_qs(parsed.query)
            self._send_json({"opinions": pdh.list_opinions(
                project=qs.get("project", [""])[0],
                status=qs.get("status", [""])[0],
            )})
            return

        # v3.1.0: 执行追踪列表
        if path == "/api/projects/dispatches":
            qs = parse_qs(parsed.query)
            self._send_json({"dispatches": pdh.list_dispatches(
                project=qs.get("project", [""])[0],
                status=qs.get("status", [""])[0],
                limit=int(qs.get("limit", ["50"])[0]),
            )})
            return

        # NSFC 仪表盘
        if path == "/api/projects/nsfc/dashboard":
            self._send_json(pr.parse_nsfc_state())
            return

        # NSFC 层次结构树（v2.9.0 三层展开）
        if path == "/api/projects/nsfc/tree":
            self._send_json(pr.parse_nsfc_state_hierarchical())
            return

        # v2.9.2: NSFC 课题产物卡片
        if path == "/api/projects/nsfc/topics":
            self._send_json({"topics": pr.get_nsfc_topics()})
            return

        # v2.9.2: NSFC 调研资料清单
        if path == "/api/projects/nsfc/references":
            self._send_json(pr.get_nsfc_references())
            return

        # v2.9.2: NSFC 待决策项
        if path == "/api/projects/nsfc/pending":
            self._send_json({"pending": pr.get_nsfc_pending()})
            return

        # NSFC 决策时间轴
        if path == "/api/projects/nsfc/decisions":
            limit = int(parse_qs(parsed.query).get("limit", ["10"])[0])
            self._send_json({"decisions": pr.get_decisions(limit=limit)})
            return

        # NSFC 申请书章节列表
        if path == "/api/projects/nsfc/chapters":
            self._send_json({"chapters": pr.get_proposal_chapters()})
            return

        # NSFC 申请书章节内容
        if path == "/api/projects/nsfc/proposal":
            topic = parse_qs(parsed.query).get("topic", [""])[0]
            self._send_json(pr.read_proposal_content(topic))
            return

        # 文献候选列表
        if path == "/api/projects/papers/candidates":
            self._send_json(pr.get_candidates())
            return

        # v2.9.1: 候选池（三状态持久化）
        if path == "/api/projects/papers/pool":
            status_filter = parse_qs(parsed.query).get("status", [""])[0]
            self._send_json(pp.get_pool(status=status_filter))
            return

        # v2.9.1: 知识库文件树（供 @文件讨论选择）
        if path == "/api/knowledge/files":
            self._send_json(kb.list_wiki_pages())
            return

        # v2.9.1: 读取知识库文件内容（供上下文注入）
        if path == "/api/knowledge/file-content":
            fpath = parse_qs(parsed.query).get("path", [""])[0]
            if not fpath:
                self._send_json({"error": "缺少 path"}, 400)
                return
            full = _PROJECT_ROOT / "knowledge" / fpath
            # 安全检查：防路径穿越
            try:
                full.resolve().relative_to((_PROJECT_ROOT / "knowledge").resolve())
            except ValueError:
                self._send_json({"error": "路径越界"}, 403)
                return
            if not full.exists():
                self._send_json({"error": "文件不存在"}, 404)
                return
            content = full.read_text(encoding="utf-8")[:8000]  # 截断
            self._send_json({"path": fpath, "content": content, "size": len(content)})
            return

        # 文献简报列表
        if path == "/api/projects/papers/briefings":
            self._send_json({"briefings": pr.get_briefings()})
            return

        # hermes cron job 列表
        if path == "/api/hermes/cron":
            self._send_json({"jobs": hb.cron_list(), "status": hb.check_hermes_available()})
            return

        # 同步状态
        if path == "/api/sync/status":
            self._send_json(se.get_sync_status())
            return

        # P0-10: 备份列表 GET
        if path == "/api/backup/list":
            try:
                backups = bm.list_backups()
                self._send_json({"backups": [
                    {"name": b.name, "size_kb": round(b.stat().st_size / 1024, 1),
                     "modified": datetime.datetime.fromtimestamp(b.stat().st_mtime).isoformat()}
                    for b in backups[:20]
                ]})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 自动同步状态（LaunchAgent + auto_sync_history）
        if path == "/api/sync/auto-status":
            agent_path = Path.home() / "Library" / "LaunchAgents" / "com.linsai.kb-auto-sync.plist"
            sync_state_path = Path(__file__).parent.parent / "memory" / "sync-state.json"
            auto_history = []
            if sync_state_path.exists():
                try:
                    state = json.loads(sync_state_path.read_text(encoding="utf-8"))
                    auto_history = state.get("auto_sync_history", [])[-5:]
                except (json.JSONDecodeError, OSError):
                    pass  # 容错：文件损坏时返回默认值
            self._send_json({
                "launchagent_installed": agent_path.exists(),
                "auto_sync_history": auto_history,
            })
            return

        # P1-12: 查询后台任务状态 (GET)
        if path.startswith("/api/task-status/"):
            task_id = path[len("/api/task-status/"):]
            with _bg_tasks_lock:
                task = _bg_tasks.get(task_id, {"status": "unknown"})
            self._send_json(task)
            return
        self._send_json({"error": f"Not found: {path}"}, 404)

    def _do_dispatch_hermes(self, task_id: str, prompt: str, project: str, source: str = "manual") -> str:
        """派活给 hermes 的统一入口：记录 dispatch → 写 plans/ → 起异步线程执行 → 回写结果。

        返回 dispatch_id（供前端跳执行追踪页查询状态）。
        """
        dispatch = pdh.record_dispatch(task_id, prompt, project, source=source)
        dispatch_id = dispatch["id"]
        # 1. 写 hermes plans/ 目录（跨进程契约，让 hermes cron/agent 能读到）
        try:
            _write_dispatch_to_hermes_plans(prompt, project, dispatch_id)
        except Exception as e:
            if _log: _log.debug("写入 hermes plans 失败: %s", e)
        # 2. 起异步线程执行 oneshot 并回写结果（补齐 fire-and-forget 缺口）
        threading.Thread(
            target=_dispatch_hermes_async,
            args=(dispatch_id, prompt, 300),
            daemon=True,
        ).start()
        return dispatch_id

    def do_POST(self) -> None:
        """处理 POST 请求。"""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        body = self._read_json_body()
        if _log:
            _log.info(f"POST {path}")

        # v3.5.1: 课题模块路由表分发
        if self._dispatch_research_routes("POST", path, parsed, body):
            return

        # 创建会话
        if path == "/api/sessions":
            topic = body.get("topic", "新会话")
            mode = body.get("mode", "co-working")
            sid, _ = sm.create_session(topic, mode)
            self._send_json({"session_id": sid, "topic": topic, "mode": mode})
            return

        # 学习配置更新
        if path == "/api/learning/config":
            config_path = _PROJECT_ROOT / "memory" / "learning-config.json"
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                # 只允许更新白名单字段
                allowed_fields = ["auto_enabled", "daily_quota", "weekly_quota", "strategy",
                                  "cost_limit_daily", "cost_limit_monthly", "sources", "adversarial_mode", "notify_web"]
                for field in allowed_fields:
                    if field in body:
                        config[field] = body[field]
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                self._send_json({"success": True, "config": config})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 学习触发
        if path == "/api/learning/trigger":
            try:
                le = lazy_load("learning_engine")
                if le:
                    query = body.get("query")
                    sources = body.get("sources", ["arxiv", "wikipedia", "raw"])
                    max_items = body.get("max_items", 2)
                    result = le.run_learning_cycle(query=query, sources=sources, max_items=max_items)
                    self._send_json(result)
                else:
                    self._send_json({"error": "学习引擎未安装"}, 500)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 学习审批
        if path == "/api/learning/review":
            try:
                qe = lazy_load("quality_evaluator")
                if qe:
                    action = body.get("action", "")
                    wiki_path = body.get("wiki_path", "")
                    if action == "approve":
                        success = qe.approve_pending(wiki_path)
                        self._send_json({"success": success, "action": "approve"})
                    elif action == "reject":
                        success = qe.reject_pending(wiki_path)
                        self._send_json({"success": success, "action": "reject"})
                    else:
                        self._send_json({"error": "无效操作"}, 400)
                else:
                    self._send_json({"error": "评估引擎未安装"}, 500)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 技能配置更新
        if path == "/api/skills/config":
            mode = body.get("mode", "auto")
            active = body.get("active_skills", [])
            try:
                result = skm.set_skill_config(mode, active)
                self._send_json({"success": True, "config": result})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
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
                        if _log: _log.debug("记录 token 用量失败: %s", e)

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
            return

        # 文件上传
        if path == "/api/upload":
            result = _handle_upload(body)
            if result.get("success"):
                self._send_json(result)
            else:
                self._send_json(result, 400)
            return

        # Agora 导出
        if path == "/api/agora":
            sid = body.get("session_id", "")
            topic = body.get("topic", "")
            personas = body.get("personas", [])
            if not sid or not personas:
                self._send_json({"error": "缺少 session_id 或 personas"}, 400)
                return
            try:
                export_path = ab.export_to_agora(sid, topic, personas)
                self._send_json({"success": True, "path": str(export_path)})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # 切换 LLM Provider
        if path == "/api/llm-provider" or path == "/api/switch-provider":
            name = body.get("provider", "").strip()
            if name == "auto" or name == "":
                lr.router.set_auto()
                self._send_json({"success": True, "mode": "auto", "active": lr.router.get_status()["active_provider"]})
            elif name == "cli_auto":
                if lr.router.set_provider("cli_auto"):
                    status = lr.router.get_status()
                    self._send_json({"success": True, "mode": "manual", "provider": "cli_auto", "active": status.get("active_provider", "")})
                else:
                    self._send_json({"error": "没有可用的 CLI Provider"}, 400)
            elif lr.router.set_provider(name):
                self._send_json({"success": True, "mode": "manual", "provider": name})
            else:
                self._send_json({"error": f"Provider {name} 不可用"}, 400)
            return

        # 重建知识库索引 (P1-11/P1-12: 防重入 + 后台线程)
        if path == "/api/knowledge/reindex":
            if not _try_acquire_kb_busy():
                self._send_json({"error": "知识库正在执行其他操作，请稍后再试"}, 409)
                return
            # P1-12: 后台线程执行，避免长时间阻塞
            task_id = f"reindex_{int(time.time())}"
            def _reindex_worker():
                try:
                    idx = kb.build_index(force=True)
                    with _bg_tasks_lock:
                        _bg_tasks[task_id] = {
                            "status": "done",
                            "documents": len(idx.get("documents", {})),
                            "terms": len(idx.get("inverted", {})),
                            "finished_at": datetime.datetime.now().isoformat(),
                        }
                except Exception as e:
                    with _bg_tasks_lock:
                        _bg_tasks[task_id] = {"status": "error", "error": str(e)}
                finally:
                    _release_kb_busy()
            threading.Thread(target=_reindex_worker, daemon=True).start()
            self._send_json({"success": True, "message": "索引重建已在后台启动", "task_id": task_id})
            return

        # 知识库增强 POST API
        if path == "/api/knowledge/ingest":
            raw_path = body.get("path", "")
            auto_distill = body.get("auto_distill", False)
            if not raw_path:
                self._send_json({"error": "缺少 path 参数"}, 400)
                return
            result = kb.ingest_raw(raw_path, auto_distill=auto_distill)
            self._send_json(result, 200 if result.get("success") else 400)
            return

        if path == "/api/knowledge/wiki":
            wiki_rel = body.get("path", "")
            content = body.get("content", "")
            meta = body.get("meta", {})
            if not wiki_rel:
                self._send_json({"error": "缺少 path 参数"}, 400)
                return
            try:
                # v3.1: 支持仅更新 meta（标签编辑场景）
                if not content and meta:
                    # 读取现有内容，仅更新 frontmatter
                    existing = kb.get_wiki_page(wiki_rel)
                    if existing:
                        content = existing.get("body", "")
                    else:
                        self._send_json({"error": "页面不存在"}, 404)
                        return
                saved = kb.save_wiki_page(wiki_rel, content, meta)
                self._send_json({"success": True, "path": saved})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/knowledge/stub":
            concept = body.get("concept", "")
            context = body.get("context", "")
            if not concept:
                self._send_json({"error": "缺少 concept 参数"}, 400)
                return
            # 相似概念检测
            similar = []
            if hasattr(kb, "check_similar_concepts"):
                similar = kb.check_similar_concepts(concept, threshold=0.9)
            if similar and not body.get("force", False):
                self._send_json({
                    "success": False,
                    "action": "suggest_merge",
                    "similar": similar,
                    "message": f"检测到 {len(similar)} 个相似概念，是否仍然创建？"
                }, 409)
                return
            wiki_path = kb.create_wiki_stub(concept, context, trigger="manual")
            self._send_json({"success": True, "path": wiki_path})
            return

        if path == "/api/knowledge/aliases":
            aliases = body.get("aliases", {})
            aliases_path = _PROJECT_ROOT / "knowledge" / "aliases.json"
            try:
                with open(aliases_path, "w", encoding="utf-8") as f:
                    json.dump(aliases, f, ensure_ascii=False, indent=2)
                self._send_json({"success": True, "aliases": aliases})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if path == "/api/knowledge/maintenance":
            task = body.get("task", "health")
            try:
                km = lazy_load("kb_maintenance")
                if not km:
                    self._send_json({"error": "维护模块未找到"}, 500)
                    return
                kb_mod = km._import_kb()

                if task == "reindex":
                    km.cmd_reindex(kb_mod)
                    self._send_json({"success": True, "task": task})
                elif task == "orphans":
                    km.cmd_orphans(kb_mod)
                    self._send_json({"success": True, "task": task})
                elif task == "candidates":
                    km.cmd_candidates(kb_mod)
                    self._send_json({"success": True, "task": task})
                elif task == "health":
                    health = kb_mod.get_kb_health()
                    self._send_json({"success": True, "task": task, "health": health})
                elif task == "weekly":
                    # weekly 输出到控制台，返回 health 数据
                    km.cmd_weekly(kb_mod)
                    health = kb_mod.get_kb_health()
                    self._send_json({"success": True, "task": task, "health": health})
                else:
                    self._send_json({"error": f"未知任务: {task}"}, 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # v3.1: 自定义分类 CRUD
        if path == "/api/knowledge/categories/create":
            name = body.get("name", "").strip()
            keywords = body.get("keywords", [])
            logic = body.get("logic", "any")
            description = body.get("description", "")
            if not name:
                self._send_json({"error": "缺少分类名称"}, 400)
                return
            try:
                cat = kbc.create_category(name, keywords, logic, description)
                self._send_json({"success": True, "category": cat})
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
            return

        if path == "/api/knowledge/categories/update":
            name = body.get("name", "").strip()
            if not name:
                self._send_json({"error": "缺少分类名称"}, 400)
                return
            try:
                cat = kbc.update_category(
                    name,
                    keywords=body.get("keywords"),
                    logic=body.get("logic"),
                    description=body.get("description"),
                )
                self._send_json({"success": True, "category": cat})
            except ValueError as e:
                self._send_json({"error": str(e)}, 400)
            return

        if path == "/api/knowledge/categories/delete":
            name = body.get("name", "").strip()
            if not name:
                self._send_json({"error": "缺少分类名称"}, 400)
                return
            deleted = kbc.delete_category(name)
            self._send_json({"success": deleted})
            return

        if path == "/api/knowledge/categories/scan":
            results = kbc.scan_all_categories()
            self._send_json({"success": True, "results": results})
            return

        if path == "/api/knowledge/filter":
            filters = body.get("filters", {})
            pages = kbc.filter_wiki_pages(filters)
            self._send_json({"pages": pages})
            return

        # 打开本地文件/文件夹（系统文件管理器）
        if path == "/api/open-local":
            target = body.get("path", "")
            if not target:
                self._send_json({"error": "缺少 path 参数"}, 400)
                return
            # 安全校验：resolve 后必须在项目根目录内
            try:
                full = (_PROJECT_ROOT / target).resolve()
                root_resolved = _PROJECT_ROOT.resolve()
                full.relative_to(root_resolved)
            except (ValueError, RuntimeError):
                self._send_json({"error": "路径超出项目范围"}, 403)
                return
            if not full.exists():
                self._send_json({"error": "路径不存在"}, 404)
                return
            sys_name = platform.system()
            try:
                if sys_name == "Darwin":
                    subprocess.run(["open", str(full)], check=False)
                elif sys_name == "Windows":
                    os.startfile(str(full))
                else:
                    subprocess.run(["xdg-open", str(full)], check=False)
                self._send_json({"success": True, "path": target, "system": sys_name})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # ============================================================
        # v2.7.0: 项目面板 + hermes 协作中枢 API
        # ============================================================

        # 项目概况
        if path == "/api/projects":
            self._send_json(pr.get_projects_overview())
            return

        # NSFC 仪表盘
        if path == "/api/projects/nsfc/dashboard":
            self._send_json(pr.parse_nsfc_state())
            return

        # NSFC 层次结构树（v2.9.0 三层展开）
        if path == "/api/projects/nsfc/tree":
            self._send_json(pr.parse_nsfc_state_hierarchical())
            return

        # v2.9.2: NSFC 课题产物卡片
        if path == "/api/projects/nsfc/topics":
            self._send_json({"topics": pr.get_nsfc_topics()})
            return

        # v2.9.2: NSFC 调研资料清单
        if path == "/api/projects/nsfc/references":
            self._send_json(pr.get_nsfc_references())
            return

        # v2.9.2: NSFC 待决策项
        if path == "/api/projects/nsfc/pending":
            self._send_json({"pending": pr.get_nsfc_pending()})
            return

        # NSFC 决策时间轴
        if path == "/api/projects/nsfc/decisions":
            limit = int(parse_qs(parsed.query).get("limit", ["10"])[0])
            self._send_json({"decisions": pr.get_decisions(limit=limit)})
            return

        # NSFC 申请书章节列表
        if path == "/api/projects/nsfc/chapters":
            self._send_json({"chapters": pr.get_proposal_chapters()})
            return

        # NSFC 申请书章节内容
        if path == "/api/projects/nsfc/proposal":
            topic = parse_qs(parsed.query).get("topic", [""])[0]
            self._send_json(pr.read_proposal_content(topic))
            return

        # 文献候选列表
        if path == "/api/projects/papers/candidates":
            self._send_json(pr.get_candidates())
            return

        # v2.9.1: 候选池（三状态持久化）
        if path == "/api/projects/papers/pool":
            status_filter = parse_qs(parsed.query).get("status", [""])[0]
            self._send_json(pp.get_pool(status=status_filter))
            return

        # v2.9.1: 知识库文件树（供 @文件讨论选择）
        if path == "/api/knowledge/files":
            self._send_json(kb.list_wiki_pages())
            return

        # v2.9.1: 读取知识库文件内容（供上下文注入）
        if path == "/api/knowledge/file-content":
            fpath = parse_qs(parsed.query).get("path", [""])[0]
            if not fpath:
                self._send_json({"error": "缺少 path"}, 400)
                return
            full = _PROJECT_ROOT / "knowledge" / fpath
            # 安全检查：防路径穿越
            try:
                full.resolve().relative_to((_PROJECT_ROOT / "knowledge").resolve())
            except ValueError:
                self._send_json({"error": "路径越界"}, 403)
                return
            if not full.exists():
                self._send_json({"error": "文件不存在"}, 404)
                return
            content = full.read_text(encoding="utf-8")[:8000]  # 截断
            self._send_json({"path": fpath, "content": content, "size": len(content)})
            return

        # 文献简报列表
        if path == "/api/projects/papers/briefings":
            self._send_json({"briefings": pr.get_briefings()})
            return

        # hermes cron job 列表
        if path == "/api/hermes/cron":
            self._send_json({"jobs": hb.cron_list(), "status": hb.check_hermes_available()})
            return

        # 同步状态
        if path == "/api/sync/status":
            self._send_json(se.get_sync_status())
            return

        # ============================================================
        # v2.7.0: hermes 控制 + 导入 + 同步（POST）
        # ============================================================

        # hermes cron 控制（暂停/恢复/触发）
        if path.startswith("/api/hermes/cron/") and path.endswith(("/pause", "/resume", "/run")):
            parts = path.split("/")
            if len(parts) >= 6:
                job_id = parts[4]
                action = parts[5]
                result = hb.cron_control(job_id, action)
                self._send_json(result)
            else:
                self._send_json({"error": "格式: /api/hermes/cron/<id>/<action>"}, 400)
            return

        # hermes 手动派活（oneshot agent loop）
        if path == "/api/hermes/run":
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
                    self._send_sse_raw("data: [DONE]\n\n")
                    self.wfile.flush()
            threading.Thread(target=_hermes_worker, daemon=True).start()
            return

        # 导入文献到子库
        if path == "/api/import/paper":
            arxiv_id = body.get("arxiv_id", "").strip()
            with_analysis = body.get("with_analysis", False)
            if not arxiv_id:
                self._send_json({"error": "缺少 arxiv_id"}, 400)
                return
            results = {"candidate": ki.import_candidate(arxiv_id)}
            if with_analysis:
                results["analysis"] = ki.import_deep_analysis(arxiv_id)
            self._send_json({"success": True, "results": results})
            return

        # 触发多端同步 (P1-11: 防重入)
        if path == "/api/sync/run":
            if not _try_acquire_kb_busy():
                self._send_json({"error": "知识库正在执行其他操作，请稍后再试"}, 409)
                return
            try:
                result = se.sync_all()
                self._send_json({"success": True, "result": result})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            finally:
                _release_kb_busy()
            return

        # P0-10: 备份 API
        if path == "/api/backup":
            action = body.get("action", "create")
            try:
                if action == "list":
                    backups = bm.list_backups()
                    self._send_json({"success": True, "backups": [
                        {"name": b.name, "size_kb": round(b.stat().st_size / 1024, 1),
                         "modified": datetime.datetime.fromtimestamp(b.stat().st_mtime).isoformat()}
                        for b in backups[:20]
                    ]})
                elif action == "create":
                    zip_path = bm.create_backup(label="web-manual")
                    if zip_path:
                        self._send_json({"success": True, "path": zip_path.name,
                                         "size_kb": round(zip_path.stat().st_size / 1024, 1)})
                    else:
                        self._send_json({"error": "备份失败"}, 500)
                elif action == "restore":
                    name = body.get("name", "")
                    if not name:
                        self._send_json({"error": "缺少备份名称"}, 400)
                        return
                    backup_path = bm.BACKUPS_DIR / name
                    if not backup_path.exists():
                        self._send_json({"error": "备份不存在"}, 404)
                        return
                    ok = bm.restore_backup(backup_path)
                    self._send_json({"success": ok})
                else:
                    self._send_json({"error": "未知操作"}, 400)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # v2.9.0: 文献反馈（👍感兴趣/👎跳过/📥归档）→ 归档+深分析+hermes偏好
        if path == "/api/projects/papers/feedback":
            arxiv_id = body.get("arxiv_id", "").strip()
            action = body.get("action", "").strip()  # interested/skip/archive/later/discuss_done
            if not arxiv_id or action not in ("interested", "skip", "archive", "later", "discuss_done"):
                self._send_json({"error": "需要 arxiv_id 和 action(interested/skip/archive/later/discuss_done)"}, 400)
                return

            # 记录反馈到本地（累积偏好）
            from datetime import datetime as _dt, timezone as _tz
            fb_path = _PROJECT_ROOT / "memory" / "paper-feedback.json"
            with _get_file_lock("paper-feedback"):
                fb = []
                if fb_path.exists():
                    try:
                        fb = json.loads(fb_path.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError):
                        fb = []  # 容错：文件损坏时返回默认值
                fb.append({"arxiv_id": arxiv_id, "action": action, "timestamp": _dt.now(_tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
                _cms.save_json(fb_path, fb[-200:])

            result = {"action": action, "arxiv_id": arxiv_id}

            # 候选池状态联动（v2.9.3 重构：感兴趣≠归档）
            # 正确流程：未看 → [感兴趣] → 已看未讨论 → [讨论完成] → 归档（深度沉淀）
            pool_status_map = {
                "interested": pp.STATUS_VIEWED,   # 感兴趣 → 已看未讨论（待深度阅读/讨论）
                "later": pp.STATUS_VIEWED,        # 稍后 → 已看未讨论
                "skip": pp.STATUS_VIEWED,         # 跳过 → 已看未讨论（保留可追溯）
                "archive": pp.STATUS_ARCHIVED,    # 归档 → 深度阅读+讨论后的最终沉淀
                "discuss_done": pp.STATUS_ARCHIVED,  # 讨论完成 → 归档
            }
            pp.update_status(arxiv_id, pool_status_map.get(action, pp.STATUS_VIEWED))

            if action == "interested":
                # 感兴趣：仅记录偏好，不归档（归档需充分讨论后）
                # 异步反馈 hermes 偏好
                try:
                    import threading as _th
                    title = body.get("title", arxiv_id)
                    def _hermes_feedback():
                        try:
                            hb.oneshot(f"用户对 arXiv {arxiv_id}（{title}）标记为感兴趣，请更新研究偏好记忆。", timeout=120)
                        except Exception as e:
                            if _log: _log.debug("hermes 偏好反馈失败: %s", e)
                    _th.Thread(target=_hermes_feedback, daemon=True).start()
                except Exception as e:
                    if _log: _log.debug("启动 hermes 反馈线程失败: %s", e)
            elif action in ("archive", "discuss_done"):
                # 归档：深度阅读+讨论后的沉淀
                # 归档候选到 raw
                result["archived"] = ki.import_candidate(arxiv_id)
                if action == "discuss_done":
                    # 讨论完成：归档 + 深分析 + wiki建议
                    analysis = ki.import_deep_analysis(arxiv_id)
                    result["has_analysis"] = analysis is not None
                    result["wiki_suggestion"] = ki.suggest_wiki_notes(arxiv_id)
                    result["discussion_summary"] = body.get("discussion_summary", "")
            elif action in ("skip", "later"):
                # 异步反馈偏好
                try:
                    import threading as _th
                    label = "不感兴趣（跳过）" if action == "skip" else "稍后讨论"
                    def _hermes_pref():
                        try:
                            hb.oneshot(f"用户对 arXiv {arxiv_id} 标记为{label}，请更新偏好。", timeout=60)
                        except Exception as e:
                            if _log: _log.debug("hermes 偏好反馈失败: %s", e)
                    _th.Thread(target=_hermes_pref, daemon=True).start()
                except Exception as e:
                    if _log: _log.debug("启动 hermes 偏好线程失败: %s", e)

            self._send_json({"success": True, "result": result})
            return

        # v2.9.0: 知识库智能生长（按用户确认生成 wiki 笔记）
        if path == "/api/knowledge/grow":
            arxiv_id = body.get("arxiv_id", "").strip()
            confirmed = body.get("confirmed", {})
            if not arxiv_id:
                self._send_json({"error": "缺少 arxiv_id"}, 400)
                return
            result = ki.grow_from_suggestion(arxiv_id, confirmed)
            self._send_json(result)
            return

        # v2.9.0: 查询 wiki 建议（不触发反馈，仅看建议）
        if path == "/api/knowledge/suggest":
            arxiv_id = body.get("arxiv_id", "").strip()
            if not arxiv_id:
                self._send_json({"error": "缺少 arxiv_id"}, 400)
                return
            self._send_json(ki.suggest_wiki_notes(arxiv_id))
            return

        # v2.9.2: NSFC 待决策项操作（approve/reject/discuss）
        m = re.match(r"^/api/projects/nsfc/pending/(.+)$", path)
        if m:
            from datetime import datetime as _dt, timezone as _tz
            pid = m.group(1)
            action = body.get("action", "").strip()  # approve/reject/discuss
            dec_path = _PROJECT_ROOT / "memory" / "nsfc-decisions.json"
            with _get_file_lock("nsfc-decisions"):
                decs = {}
                if dec_path.exists():
                    try: decs = json.loads(dec_path.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError): decs = {}  # 容错：文件损坏时返回默认值

                if action == "discuss":
                    # 标记讨论中，返回该课题的知识库上下文供注入
                    decs[pid] = {"status": "discussing", "started_at": _dt.now(_tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
                    _cms.save_json(dec_path, decs)
                    title = body.get("title", "")
                    topic = body.get("related_topic", "")
                    # 收集该课题的 references 上下文
                    context_files = []
                    refs = pr.get_nsfc_references()
                    for r in refs.get("references", [])[:5]:
                        context_files.append(r.get("path", ""))
                    self._send_json({"success": True, "status": "discussing", "title": title,
                                     "context_files": context_files, "topic": topic})
                elif action in ("approve", "reject"):
                    decs[pid] = {"status": action, "decided_at": _dt.now(_tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "summary": body.get("summary", "")}
                    _cms.save_json(dec_path, decs)
                    # 异步反馈 hermes
                    title = body.get("title", "")
                    try:
                        import threading as _th
                        label = "通过" if action == "approve" else "否决"
                        def _fb():
                            try: hb.oneshot(f"用户对待决策项「{title}」标记为{label}。请更新项目状态。", timeout=120)
                            except Exception as e:
                                if _log: _log.debug("hermes 反馈失败: %s", e)
                        _th.Thread(target=_fb, daemon=True).start()
                    except Exception as e:
                        if _log: _log.debug("启动 hermes 反馈线程失败: %s", e)
                    self._send_json({"success": True, "status": action})
                else:
                    self._send_json({"error": "action 需为 approve/reject/discuss"}, 400)
            return

        # v2.9.2: NSFC 讨论总结 → 写 discussions + 反馈 hermes
        if path == "/api/projects/nsfc/discuss-summary":
            from datetime import datetime as _dt, timezone as _tz
            pid = body.get("pending_id", "")
            title = body.get("title", "")
            summary = body.get("summary", "").strip()
            topic = body.get("topic", "")
            if not summary:
                self._send_json({"error": "缺少 summary"}, 400)
                return

            # 写回 discussions/{date}_decisions.md
            today = _dt.now(_tz.utc).strftime("%Y-%m-%d")
            disc_dir = pr.NSFC_DIR / "discussions"
            disc_file = disc_dir / f"{today}_decisions.md"
            disc_dir.mkdir(parents=True, exist_ok=True)
            entry = f"\n\n## 决策: {title} 🌐 林赛CoPilot讨论捕获\n\n"
            entry += f"**决策**: ✅ 已讨论（{topic}）\n\n"
            entry += f"**讨论总结**:\n\n{summary}\n\n"
            entry += f"**来源**: 林赛CoPilot Web 讨论({_dt.now(_tz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})\n"
            entry += f"**可推翻**: 用户可在后续讨论中调整\n\n---\n"
            mode = "a" if disc_file.exists() else "w"
            with open(disc_file, mode, encoding="utf-8") as f:
                f.write(entry)

            # 更新持久化状态
            dec_path = _PROJECT_ROOT / "memory" / "nsfc-decisions.json"
            with _get_file_lock("nsfc-decisions"):
                decs = {}
                if dec_path.exists():
                    try: decs = json.loads(dec_path.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError): decs = {}  # 容错：文件损坏时返回默认值
                if pid:
                    decs[pid] = {"status": "discussed", "decided_at": _dt.now(_tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "summary": summary[:200]}
                    _cms.save_json(dec_path, decs)

            # 异步反馈 hermes
            try:
                import threading as _th
                def _fb2():
                    try: hb.oneshot(f"用户在林赛CoPilot讨论了「{title}」（课题{topic}），结论：{summary[:500]}。请据此更新 state.md 和后续 BRAIN 计划。", timeout=180)
                    except Exception as e:
                        if _log: _log.debug("hermes 反馈失败: %s", e)
                _th.Thread(target=_fb2, daemon=True).start()
            except Exception as e:
                if _log: _log.debug("启动 hermes 反馈线程失败: %s", e)

            self._send_json({"success": True, "written_to": str(disc_file.relative_to(pr.NSFC_DIR)), "pid": pid})
            return

        # v2.8.0: 创建任务
        if path == "/api/tasks":
            title = body.get("title", "").strip()
            if not title:
                self._send_json({"error": "缺少 title"}, 400)
                return
            project = body.get("project", "").strip()
            assignee = body.get("assignee", "myself")
            tid, _ = tm.create_task(
                title=title,
                priority=body.get("priority", "medium"),
                category=body.get("category", "general"),
                due_date=body.get("due_date", ""),
                description=body.get("description", ""),
                project=project,
                assignee=assignee,
            )
            # 创建即派发：assignee=hermes 时自动派给 hermes 执行
            dispatch_id = ""
            if assignee == "hermes":
                prompt = body.get("prompt", "").strip() or f"请执行项目任务：{title}。" + (f"\n描述：{body.get('description','')}" if body.get("description") else "")
                dispatch_id = self._do_dispatch_hermes(tid, prompt, project, source="create")
            # P5-1: 返回完整任务对象，确保前端 createNewTask() 可直接 push 到 State.tasks
            try:
                task_obj = tm.get_task(tid)
                task_obj["dispatch_id"] = dispatch_id
                self._send_json(task_obj)
            except Exception:
                self._send_json({"success": True, "task_id": tid, "title": title, "status": "backlog", "dispatch_id": dispatch_id})
            return

        # v3.1.0: 派活给 hermes（任务卡片⚡按钮）
        m = re.match(r"^/api/tasks/([^/]+)/dispatch$", path)
        if m:
            tid = m.group(1)
            prompt = body.get("prompt", "").strip()
            project = body.get("project", "")
            if not prompt:
                # 未给 prompt 时，从任务自动构造
                try:
                    task = tm.get_task(tid)
                    prompt = f"请执行项目任务：{task.get('title','')}。" + (f"\n描述：{task.get('description','')}" if task.get("description") else "")
                    project = project or task.get("project", "")
                except Exception:
                    self._send_json({"error": "任务不存在，且未提供 prompt"}, 400)
                    return
            dispatch_id = self._do_dispatch_hermes(tid, prompt, project, source="manual")
            self._send_json({"success": True, "dispatch_id": dispatch_id})
            return

        # v3.1.0: 提交项目意见
        if path == "/api/projects/opinions":
            content = body.get("content", "").strip()
            if not content:
                self._send_json({"error": "缺少 content"}, 400)
                return
            project = body.get("project", "").strip()
            feed_hermes = bool(body.get("feed_hermes", False))
            op = pdh.add_opinion(project, content)
            # 可选：反馈给 hermes（fire-and-forget）
            if feed_hermes:
                try:
                    prompt = f"用户对项目「{project or '通用'}」提出意见：{content}。请知悉并考虑纳入后续工作。"
                    hb.oneshot  # 仅校验可调用，真正执行在 daemon 线程
                    threading.Thread(
                        target=lambda: hb.oneshot(prompt, timeout=120),
                        daemon=True,
                    ).start()
                    pdh.mark_opinion_fed(op["id"])
                    op["fed_to_hermes"] = True
                except Exception as e:
                    if _log: _log.debug("意见反馈 hermes 失败: %s", e)
            self._send_json({"success": True, "opinion": op})
            return
        self._send_json({"error": f"Not found: {path}"}, 404)

    def do_PUT(self) -> None:
        """处理 PUT 请求（消息编辑、任务子任务、任务进度）。"""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        body = self._read_json_body()

        # v3.5.1: 课题模块路由表分发
        if self._dispatch_research_routes("PUT", path, parsed, body):
            return

        # PUT /api/sessions/<id>/messages/<msg_id>
        m = re.match(r"^/api/sessions/([^/]+)/messages/([^/]+)$", path)
        if m:
            sid, msg_id = m.group(1), m.group(2)
            new_content = body.get("content", "").strip()
            if not new_content:
                self._send_json({"error": "内容不能为空"}, 400)
                return
            ok = _edit_message(sid, msg_id, new_content)
            if ok:
                self._send_json({"success": True})
            else:
                self._send_json({"error": "消息未找到"}, 404)
            return

        # v3.1.0: PUT /api/tasks/<id> 通用字段更新（含 status 拖拽，修复 task.js:84 的 404 bug）
        # 注意：严格匹配，排除 /subtasks /progress /dispatch 子路由
        m = re.match(r"^/api/tasks/([^/]+)$", path)
        if m and "/subtasks" not in path and "/progress" not in path and "/dispatch" not in path:
            tid = m.group(1)
            try:
                updated = tm.update_task_fields(tid, **body)
                self._send_json({"success": True, "task": updated})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # PUT /api/tasks/<id>/subtasks
        m = re.match(r"^/api/tasks/([^/]+)/subtasks$", path)
        if m:
            tid = m.group(1)
            subtask_id = body.get("subtask_id", "")
            try:
                tm.toggle_subtask(tid, subtask_id)
                self._send_json({"success": True})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # PUT /api/tasks/<id>/progress
        m = re.match(r"^/api/tasks/([^/]+)/progress$", path)
        if m:
            tid = m.group(1)
            progress = body.get("progress", 0)
            try:
                tm.update_progress(tid, int(progress))
                self._send_json({"success": True})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # v3.1.0: PUT /api/projects/opinions/<id>/resolve 标记意见已解决
        m = re.match(r"^/api/projects/opinions/([^/]+)/resolve$", path)
        if m:
            op_id = m.group(1)
            resolved = pdh.resolve_opinion(op_id)
            if resolved:
                self._send_json({"success": True, "opinion": resolved})
            else:
                self._send_json({"error": "意见不存在"}, 404)
            return
        self._send_json({"error": f"Not found: {path}"}, 404)

    def do_DELETE(self) -> None:
        """处理 DELETE 请求（消息删除）。"""
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        # v3.5.1: 课题模块路由表分发
        if self._dispatch_research_routes("DELETE", path, parsed):
            return

        # DELETE /api/sessions/<id>/messages/<msg_id>
        m = re.match(r"^/api/sessions/([^/]+)/messages/([^/]+)$", path)
        if m:
            sid, msg_id = m.group(1), m.group(2)
            ok = _delete_message(sid, msg_id)
            if ok:
                self._send_json({"success": True})
            else:
                self._send_json({"error": "消息未找到"}, 404)
            return

        # DELETE /api/knowledge/wiki/{path}  (P0-9: 软删除到 .trash/)
        if path.startswith("/api/knowledge/wiki/"):
            wiki_rel = path[len("/api/knowledge/wiki/"):]
            # P0-9: 软删除 — 移到 .trash/ 而非直接 unlink
            wiki_full = kb.KNOWLEDGE_DIR / f"wiki/{wiki_rel}"
            if not wiki_full.exists():
                self._send_json({"error": "Wiki 页面不存在"}, 404)
                return
            trash_dir = kb.KNOWLEDGE_DIR / ".trash"
            trash_dir.mkdir(exist_ok=True)
            trash_path = trash_dir / Path(wiki_rel).name
            # 避免覆盖
            if trash_path.exists():
                trash_path = trash_dir / f"{Path(wiki_rel).stem}_{int(time.time())}.md"
            try:
                wiki_full.rename(trash_path)
                # 清理图谱
                page = kb.get_wiki_page(f"wiki/{wiki_rel}")
                title = page["frontmatter"].get("title", "") if page else ""
                if title:
                    kb._remove_graph_node(title)
                self._send_json({"success": True, "message": f"已移至回收站: {trash_path.name}"})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # v2.8.0: DELETE /api/tasks/<id>
        m = re.match(r"^/api/tasks/(.+)$", path)
        if m:
            tid = m.group(1)
            ok = tm.delete_task(tid)
            if ok:
                self._send_json({"success": True})
            else:
                self._send_json({"error": "任务不存在"}, 404)
            return
        self._send_json({"error": f"Not found: {path}"}, 404)


def _update_memory_async(session_id: str) -> None:
    """异步更新用户画像和工作上下文。"""
    try:
        mm.update_user_profile(session_id)
        mm.update_working_context(session_id)
    except Exception as e:
        if _log: _log.debug("异步更新记忆失败: %s", e)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _edit_message(session_id: str, msg_id: str, new_content: str) -> bool:
    """编辑指定消息。"""
    msg_path = _PROJECT_ROOT / "sessions" / session_id / "messages.json"
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
            with open(msg_path, "w", encoding="utf-8") as f:
                json.dump(data if isinstance(data, list) else {"messages": messages},
                          f, ensure_ascii=False, indent=2)
            return True
    except Exception:
        return False


def _delete_message(session_id: str, msg_id: str) -> bool:
    """删除指定消息（P0-9: 删除前自动备份）。"""
    msg_path = _PROJECT_ROOT / "sessions" / session_id / "messages.json"
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
                if _log: _log.debug("删除前备份失败: %s", e)
            with open(msg_path, "w", encoding="utf-8") as f:
                json.dump(data if isinstance(data, list) else {"messages": messages},
                          f, ensure_ascii=False, indent=2)
            return True
    except Exception:
        return False


def _handle_upload(body: Dict[str, Any]) -> Dict[str, Any]:
    """处理文件上传，保存到 references/ 目录。"""
    filename = body.get("filename", "")
    content = body.get("content", "")
    category = body.get("category", "notes")
    is_base64 = body.get("is_base64", False)

    if not filename:
        return {"success": False, "error": "缺少文件名"}

    # 清理文件名
    safe_name = re.sub(r"[^\w\-.\s]", "_", filename).strip()
    if not safe_name:
        safe_name = "uploaded_file"

    dest_dir = _PROJECT_ROOT / "references" / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / safe_name

    # 避免覆盖：追加序号
    counter = 1
    stem = dest_path.stem
    suffix = dest_path.suffix
    while dest_path.exists():
        dest_path = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    try:
        if is_base64:
            raw = base64.b64decode(content)
            with open(dest_path, "wb") as f:
                f.write(raw)
            # 尝试提取文本摘要
            try:
                text_preview = dh.read_document(str(dest_path))
                if text_preview:
                    text_preview = text_preview[:200] + "…" if len(text_preview) > 200 else text_preview
            except Exception:
                text_preview = None
        else:
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)
            text_preview = content[:200] + "…" if len(content) > 200 else content

        # 更新索引
        try:
            dh.index_references()
        except Exception as e:
            if _log: _log.debug("更新引用索引失败: %s", e)

        return {
            "success": True,
            "path": str(dest_path.relative_to(_PROJECT_ROOT)),
            "filename": dest_path.name,
            "category": category,
            "preview": text_preview,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _list_references() -> List[Dict[str, Any]]:
    """列出已上传的参考文献。"""
    refs: List[Dict[str, Any]] = []
    index_path = _PROJECT_ROOT / "references" / "index.json"
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            refs = data if isinstance(data, list) else data.get("entries", [])
        except (json.JSONDecodeError, OSError):
            pass  # 容错：文件损坏时返回默认值
    return refs


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
    parser.add_argument("--root", default="", help="项目根目录覆盖（隔离测试用，默认: 脚本上级）")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)

    # --root 覆盖项目根目录（用于隔离测试环境）
    if args.root:
        global _PROJECT_ROOT, _WEB_DIR
        _PROJECT_ROOT = Path(args.root).resolve()
        _WEB_DIR = _PROJECT_ROOT / "web"

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
