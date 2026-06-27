#!/usr/bin/env python3
"""web_routes_kb.py — 知识库路由 Mixin。

提供 KbRoutesMixin，封装知识库搜索/索引/CRUD/分类/维护/生长等 HTTP 路由：
    - GET    /api/knowledge                    索引状态
    - GET    /api/knowledge/search             搜索
    - GET    /api/knowledge/raw                原始文件列表
    - GET    /api/knowledge/wiki               wiki 页列表
    - POST   /api/knowledge/wiki               保存 wiki 页
    - GET    /api/knowledge/wiki/{path}        读取 wiki 页
    - DELETE /api/knowledge/wiki/{path}        软删除 wiki 页
    - GET    /api/knowledge/graph              知识图谱
    - GET    /api/knowledge/related            关联概念
    - GET    /api/knowledge/growth-log         生长日志
    - GET    /api/knowledge/growth-candidates  生长候选
    - GET    /api/knowledge/enriched           增强上下文
    - GET    /api/knowledge/aliases            别名映射
    - POST   /api/knowledge/aliases            更新别名
    - GET    /api/knowledge/captures           对话捕获
    - GET    /api/knowledge/health             健康度
    - GET    /api/knowledge/categories         分类列表
    - GET    /api/knowledge/filters            过滤器
    - GET+POST /api/knowledge/files            文件树
    - GET+POST /api/knowledge/file-content     文件内容
    - POST   /api/knowledge/reindex            重建索引（后台）
    - POST   /api/knowledge/ingest             导入原始文件
    - POST   /api/knowledge/stub               创建 wiki 桩
    - POST   /api/knowledge/maintenance        批处理维护
    - POST   /api/knowledge/categories/*       分类 CRUD
    - POST   /api/knowledge/filter             过滤页面
    - POST   /api/knowledge/grow               智能生长
    - POST   /api/knowledge/suggest            wiki 建议

路由表格式：(HTTP方法, re.compile(正则), handler名)
handler 签名：GET/DELETE → (self, parsed, body=None, **path_params)
             POST/PUT   → (self, parsed, body, **path_params)
仅使用 Python 标准库。
"""

import datetime
import json
import re
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs

import web_base
from web_base import (
    _log,
    _get_file_lock,
    _try_acquire_kb_busy,
    _release_kb_busy,
    _bg_tasks,
    _bg_tasks_lock,
)
from common import lazy_load

import knowledge_base as kb
import kb_importer as ki
import kb_categories as kbc


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_KB_ROUTES = [
    # --- GET ---
    ("GET", re.compile(r"^/api/knowledge$"), "_kb_index_status"),
    ("GET", re.compile(r"^/api/knowledge/search$"), "_kb_search"),
    ("GET", re.compile(r"^/api/knowledge/raw$"), "_kb_raw_files"),
    ("GET", re.compile(r"^/api/knowledge/wiki$"), "_kb_wiki_list"),
    ("GET", re.compile(r"^/api/knowledge/wiki/(?P<wiki_rel>.+)$"), "_kb_wiki_get"),
    ("GET", re.compile(r"^/api/knowledge/graph$"), "_kb_graph"),
    ("GET", re.compile(r"^/api/knowledge/related$"), "_kb_related"),
    ("GET", re.compile(r"^/api/knowledge/growth-log$"), "_kb_growth_log"),
    ("GET", re.compile(r"^/api/knowledge/growth-candidates$"), "_kb_growth_candidates"),
    ("GET", re.compile(r"^/api/knowledge/enriched$"), "_kb_enriched"),
    ("GET", re.compile(r"^/api/knowledge/aliases$"), "_kb_aliases_get"),
    ("GET", re.compile(r"^/api/knowledge/captures$"), "_kb_captures"),
    ("GET", re.compile(r"^/api/knowledge/health$"), "_kb_health"),
    ("GET", re.compile(r"^/api/knowledge/categories$"), "_kb_categories"),
    ("GET", re.compile(r"^/api/knowledge/filters$"), "_kb_filters"),
    ("GET", re.compile(r"^/api/knowledge/files$"), "_kb_files"),
    ("GET", re.compile(r"^/api/knowledge/file-content$"), "_kb_file_content"),
    # --- POST ---
    ("POST", re.compile(r"^/api/knowledge/reindex$"), "_kb_reindex"),
    ("POST", re.compile(r"^/api/knowledge/ingest$"), "_kb_ingest"),
    ("POST", re.compile(r"^/api/knowledge/wiki$"), "_kb_wiki_save"),
    ("POST", re.compile(r"^/api/knowledge/stub$"), "_kb_stub"),
    ("POST", re.compile(r"^/api/knowledge/aliases$"), "_kb_aliases_set"),
    ("POST", re.compile(r"^/api/knowledge/maintenance$"), "_kb_maintenance"),
    ("POST", re.compile(r"^/api/knowledge/categories/create$"), "_kb_cat_create"),
    ("POST", re.compile(r"^/api/knowledge/categories/update$"), "_kb_cat_update"),
    ("POST", re.compile(r"^/api/knowledge/categories/delete$"), "_kb_cat_delete"),
    ("POST", re.compile(r"^/api/knowledge/categories/scan$"), "_kb_cat_scan"),
    ("POST", re.compile(r"^/api/knowledge/filter$"), "_kb_filter"),
    ("POST", re.compile(r"^/api/knowledge/files$"), "_kb_files"),
    ("POST", re.compile(r"^/api/knowledge/file-content$"), "_kb_file_content"),
    ("POST", re.compile(r"^/api/knowledge/grow$"), "_kb_grow"),
    ("POST", re.compile(r"^/api/knowledge/suggest$"), "_kb_suggest"),
    # --- DELETE ---
    ("DELETE", re.compile(r"^/api/knowledge/wiki/(?P<wiki_rel>.+)$"), "_kb_wiki_delete"),
]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class KbRoutesMixin:
    """知识库路由 Mixin。"""

    # --- GET ---

    def _kb_index_status(self, parsed, body=None):
        """索引状态"""
        self._send_json(kb.get_index_status())

    def _kb_search(self, parsed, body=None):
        """搜索"""
        query = parse_qs(parsed.query).get("q", [""])[0]
        source = parse_qs(parsed.query).get("source", ["all"])[0]
        top_k = int(parse_qs(parsed.query).get("top_k", ["3"])[0])
        results = kb.search(query, top_k=top_k, source=source)
        self._send_json({"query": query, "results": results})

    def _kb_raw_files(self, parsed, body=None):
        """原始文件列表"""
        self._send_json({"files": kb.list_raw_files()})

    def _kb_wiki_list(self, parsed, body=None):
        """wiki 页列表"""
        wiki_type = parse_qs(parsed.query).get("type", [None])[0]
        self._send_json({"pages": kb.list_wiki_pages(wiki_type)})

    def _kb_wiki_get(self, parsed, body=None, wiki_rel=None):
        """读取 wiki 页"""
        page = kb.get_wiki_page(f"wiki/{wiki_rel}")
        if page:
            self._send_json(page)
        else:
            self._send_json({"error": "Wiki 页面不存在"}, 404)

    def _kb_graph(self, parsed, body=None):
        """知识图谱"""
        self._send_json(kb.get_graph_summary())

    def _kb_related(self, parsed, body=None):
        """关联概念"""
        query = parse_qs(parsed.query).get("q", [""])[0]
        related = kb.get_related_concepts(query, depth=1)
        self._send_json({"concept": query, "related": related})

    def _kb_growth_log(self, parsed, body=None):
        """生长日志"""
        limit = int(parse_qs(parsed.query).get("limit", ["50"])[0])
        self._send_json({"log": kb.get_growth_log(limit=limit)})

    def _kb_growth_candidates(self, parsed, body=None):
        """生长候选"""
        self._send_json({"candidates": kb.get_growth_candidates()})

    def _kb_enriched(self, parsed, body=None):
        """增强上下文"""
        query = parse_qs(parsed.query).get("q", [""])[0]
        self._send_json(kb.get_enriched_context(query, top_k=3))

    def _kb_aliases_get(self, parsed, body=None):
        """别名映射"""
        aliases_path = web_base._PROJECT_ROOT / "knowledge" / "aliases.json"
        if aliases_path.exists():
            try:
                with open(aliases_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json({"aliases": data})
            except Exception as e:
                self._send_json({"aliases": {}, "error": str(e)})
        else:
            self._send_json({"aliases": {}})

    def _kb_captures(self, parsed, body=None):
        """对话捕获"""
        try:
            kc = lazy_load("kb_capture")
            if kc:
                self._send_json({"captures": kc.list_captures()})
            else:
                self._send_json({"captures": []})
        except Exception as e:
            self._send_json({"captures": [], "error": str(e)})

    def _kb_health(self, parsed, body=None):
        """健康度"""
        try:
            self._send_json(kb.get_kb_health())
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _kb_categories(self, parsed, body=None):
        """分类列表"""
        self._send_json({"categories": kbc.list_categories()})

    def _kb_filters(self, parsed, body=None):
        """过滤器"""
        self._send_json(kbc.get_all_filters())

    def _kb_files(self, parsed, body=None):
        """知识库文件树（GET+POST 重复）"""
        self._send_json(kb.list_wiki_pages())

    def _kb_file_content(self, parsed, body=None):
        """读取知识库文件内容（GET+POST 重复）"""
        fpath = parse_qs(parsed.query).get("path", [""])[0]
        if not fpath:
            self._send_json({"error": "缺少 path"}, 400)
            return
        full = web_base._PROJECT_ROOT / "knowledge" / fpath
        # 安全检查：防路径穿越
        try:
            full.resolve().relative_to((web_base._PROJECT_ROOT / "knowledge").resolve())
        except ValueError:
            self._send_json({"error": "路径越界"}, 403)
            return
        if not full.exists():
            self._send_json({"error": "文件不存在"}, 404)
            return
        content = full.read_text(encoding="utf-8")[:8000]  # 截断
        self._send_json({"path": fpath, "content": content, "size": len(content)})

    # --- POST ---

    def _kb_reindex(self, parsed, body):
        """重建知识库索引（防重入 + 后台线程）"""
        if not _try_acquire_kb_busy():
            self._send_json({"error": "知识库正在执行其他操作，请稍后再试"}, 409)
            return
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

    def _kb_ingest(self, parsed, body):
        """导入原始文件"""
        raw_path = body.get("path", "")
        auto_distill = body.get("auto_distill", False)
        if not raw_path:
            self._send_json({"error": "缺少 path 参数"}, 400)
            return
        result = kb.ingest_raw(raw_path, auto_distill=auto_distill)
        self._send_json(result, 200 if result.get("success") else 400)

    def _kb_wiki_save(self, parsed, body):
        """保存 wiki 页"""
        wiki_rel = body.get("path", "")
        content = body.get("content", "")
        meta = body.get("meta", {})
        if not wiki_rel:
            self._send_json({"error": "缺少 path 参数"}, 400)
            return
        try:
            # 支持仅更新 meta（标签编辑场景）
            if not content and meta:
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

    def _kb_stub(self, parsed, body):
        """创建 wiki 桩"""
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

    def _kb_aliases_set(self, parsed, body):
        """更新别名"""
        aliases = body.get("aliases", {})
        aliases_path = web_base._PROJECT_ROOT / "knowledge" / "aliases.json"
        try:
            with open(aliases_path, "w", encoding="utf-8") as f:
                json.dump(aliases, f, ensure_ascii=False, indent=2)
            self._send_json({"success": True, "aliases": aliases})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _kb_maintenance(self, parsed, body):
        """批处理维护"""
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
                km.cmd_weekly(kb_mod)
                health = kb_mod.get_kb_health()
                self._send_json({"success": True, "task": task, "health": health})
            else:
                self._send_json({"error": f"未知任务: {task}"}, 400)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _kb_cat_create(self, parsed, body):
        """创建分类"""
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

    def _kb_cat_update(self, parsed, body):
        """更新分类"""
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

    def _kb_cat_delete(self, parsed, body):
        """删除分类"""
        name = body.get("name", "").strip()
        if not name:
            self._send_json({"error": "缺少分类名称"}, 400)
            return
        deleted = kbc.delete_category(name)
        self._send_json({"success": deleted})

    def _kb_cat_scan(self, parsed, body):
        """扫描所有分类"""
        results = kbc.scan_all_categories()
        self._send_json({"success": True, "results": results})

    def _kb_filter(self, parsed, body):
        """过滤页面"""
        filters = body.get("filters", {})
        pages = kbc.filter_wiki_pages(filters)
        self._send_json({"pages": pages})

    def _kb_grow(self, parsed, body):
        """知识库智能生长"""
        arxiv_id = body.get("arxiv_id", "").strip()
        confirmed = body.get("confirmed", {})
        if not arxiv_id:
            self._send_json({"error": "缺少 arxiv_id"}, 400)
            return
        result = ki.grow_from_suggestion(arxiv_id, confirmed)
        self._send_json(result)

    def _kb_suggest(self, parsed, body):
        """查询 wiki 建议"""
        arxiv_id = body.get("arxiv_id", "").strip()
        if not arxiv_id:
            self._send_json({"error": "缺少 arxiv_id"}, 400)
            return
        self._send_json(ki.suggest_wiki_notes(arxiv_id))

    # --- DELETE ---

    def _kb_wiki_delete(self, parsed, body=None, wiki_rel=None):
        """软删除 wiki 页（移到 .trash/）"""
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
