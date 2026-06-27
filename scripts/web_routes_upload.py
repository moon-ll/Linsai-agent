#!/usr/bin/env python3
"""web_routes_upload.py — 上传/文件路由 Mixin。

提供 UploadRoutesMixin，封装文件上传、本地文件打开、文献导入、Agora 导出等 HTTP 路由：
    - GET  /api/references     参考文献列表
    - POST /api/upload         文件上传
    - POST /api/open-local     打开本地文件/文件夹
    - POST /api/import/paper   导入文献到子库
    - POST /api/agora          Agora 导出

同时包含模块级函数 _handle_upload / _list_references。

路由表格式：(HTTP方法, re.compile(正则), handler名)
handler 签名：GET/DELETE → (self, parsed, body=None, **path_params)
             POST/PUT   → (self, parsed, body, **path_params)
仅使用 Python 标准库。
"""

import base64
import json
import os
import platform
import re
import subprocess
from typing import Any, Dict, List

import web_base
from web_base import _log

import document_handler as dh
import agora_bridge as ab
import kb_importer as ki


# ---------------------------------------------------------------------------
# 模块级函数
# ---------------------------------------------------------------------------
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

    dest_dir = web_base._PROJECT_ROOT / "references" / category
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
            if _log:
                _log.debug("更新引用索引失败: %s", e)

        return {
            "success": True,
            "path": str(dest_path.relative_to(web_base._PROJECT_ROOT)),
            "filename": dest_path.name,
            "category": category,
            "preview": text_preview,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _list_references() -> List[Dict[str, Any]]:
    """列出已上传的参考文献。"""
    refs: List[Dict[str, Any]] = []
    index_path = web_base._PROJECT_ROOT / "references" / "index.json"
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            refs = data if isinstance(data, list) else data.get("entries", [])
        except (json.JSONDecodeError, OSError):
            pass  # 容错：文件损坏时返回默认值
    return refs


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_UPLOAD_ROUTES = [
    # GET
    ("GET", re.compile(r"^/api/references$"), "_up_references"),
    # POST
    ("POST", re.compile(r"^/api/upload$"), "_up_upload"),
    ("POST", re.compile(r"^/api/open-local$"), "_up_open_local"),
    ("POST", re.compile(r"^/api/import/paper$"), "_up_import_paper"),
    ("POST", re.compile(r"^/api/agora$"), "_up_agora"),
]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class UploadRoutesMixin:
    """上传/文件路由 Mixin。"""

    def _up_references(self, parsed, body=None):
        """参考文献列表"""
        refs = _list_references()
        self._send_json(refs)

    def _up_upload(self, parsed, body):
        """文件上传"""
        result = _handle_upload(body)
        if result.get("success"):
            self._send_json(result)
        else:
            self._send_json(result, 400)

    def _up_open_local(self, parsed, body):
        """打开本地文件/文件夹（系统文件管理器）"""
        target = body.get("path", "")
        if not target:
            self._send_json({"error": "缺少 path 参数"}, 400)
            return
        # 安全校验：resolve 后必须在项目根目录内
        try:
            full = (web_base._PROJECT_ROOT / target).resolve()
            root_resolved = web_base._PROJECT_ROOT.resolve()
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

    def _up_import_paper(self, parsed, body):
        """导入文献到子库"""
        arxiv_id = body.get("arxiv_id", "").strip()
        with_analysis = body.get("with_analysis", False)
        if not arxiv_id:
            self._send_json({"error": "缺少 arxiv_id"}, 400)
            return
        results = {"candidate": ki.import_candidate(arxiv_id)}
        if with_analysis:
            results["analysis"] = ki.import_deep_analysis(arxiv_id)
        self._send_json({"success": True, "results": results})

    def _up_agora(self, parsed, body):
        """Agora 导出"""
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
