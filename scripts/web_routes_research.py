#!/usr/bin/env python3
"""web_routes_research.py — 课题指导模块路由 Mixin。

提供 ResearchRoutesMixin，整体迁移自 web_server.py 的课题路由系统（v3.5.0）。
封装课题/单元/知识库/记忆/工作流的全链路 HTTP 路由（37 条）。

路由表 _RESEARCH_ROUTES 使用字符串模式（非编译正则），handler 签名为
    GET/DELETE  → (self, path, parsed, match)
    POST/PUT    → (self, path, parsed, body, match)
其中 match 为 re.match 返回的 Match 对象，通过 match.group(N) 提取路径参数。

独立分派器 _dispatch_research_routes 在 do_GET/do_POST/do_PUT/do_DELETE 中
优先于统一路由表调用，避免与 _all_route_tables() 冲突。

仅使用 Python 标准库。
"""

import re
from urllib.parse import parse_qs

import project_manager as pjm
import unit_manager as um
import project_kb as pkb
import project_memory as pmm
import project_workflow as pwf
import project_context as pctx


# ---------------------------------------------------------------------------
# 路由表（P2: 预编译正则，与其他路由模块一致）
# ---------------------------------------------------------------------------
_RESEARCH_ROUTES_RAW = [
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
    # v5.4: 项目决策同步（.copilot-sync.json）
    ("GET", r"^/api/research/projects/([^/]+)/sync-decisions$", "_rg_get_sync_decisions"),
    ("POST", r"^/api/research/projects/([^/]+)/sync-decisions$", "_rg_post_sync_decision"),
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

# 预编译正则
_RESEARCH_ROUTES = [(m, re.compile(p), h) for m, p, h in _RESEARCH_ROUTES_RAW]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class ResearchRoutesMixin:
    """课题指导模块路由 Mixin（v3.5.0 整体迁移）。"""

    def _dispatch_research_routes(self, method, path, parsed, body=None):
        """课题指导模块路由表分发。返回 True 表示已处理。"""
        for m, compiled_re, handler_name in _RESEARCH_ROUTES:
            if m != method:
                continue
            match = compiled_re.match(path)
            if match:
                handler = getattr(self, handler_name, None)
                if handler:
                    try:
                        if body is not None:
                            handler(path, parsed, body, match)
                        else:
                            handler(path, parsed, match)
                    except ValueError as e:
                        # 路径遍历等安全校验失败
                        self._send_json({"error": str(e)}, 400)
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
        """知识库搜索（?q=&layer=&top_k=&offset=）"""
        pid = match.group(1)
        qs = parse_qs(parsed.query)
        q = qs.get("q", [""])[0]
        layer = qs.get("layer", ["all"])[0]
        top_k = int(qs.get("top_k", ["5"])[0])
        offset = int(qs.get("offset", ["0"])[0])
        if not q:
            self._send_json({"results": [], "total": 0, "offset": offset, "limit": top_k})
            return
        result = pkb.search(pid, q, layer=layer, top_k=top_k, offset=offset)
        self._send_json(result)

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

    # v5.4: 项目决策同步（.copilot-sync.json）
    def _rg_get_sync_decisions(self, path, parsed, match):
        """获取项目的同步决策列表（.copilot-sync.json）"""
        pid = match.group(1)
        try:
            project_dir = str(pjm._project_dir(pid))
            from state_sync import load_project_sync
            data = load_project_sync(project_dir)
            decisions = data.get("decisions", {})
            # 转为列表并按时间排序
            decision_list = []
            for did, d in decisions.items():
                d_copy = dict(d)
                d_copy["decision_id"] = did
                decision_list.append(d_copy)
            decision_list.sort(key=lambda x: x.get("decided_at", ""), reverse=True)
            self._send_json({
                "project": pid,
                "decisions": decision_list,
                "last_hermes_update": data.get("last_hermes_update", ""),
                "last_copilot_view": data.get("last_copilot_view", ""),
            })
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _rg_post_sync_decision(self, path, parsed, body, match):
        """创建项目同步决策（写入 .copilot-sync.json，供 hermes 消费）"""
        pid = match.group(1)
        title = body.get("title", "").strip()
        if not title:
            self._send_json({"error": "缺少 title"}, 400)
            return
        try:
            project_dir = str(pjm._project_dir(pid))
            from state_sync import update_decision_status
            import time as _time
            decision_id = f"dc_{int(_time.time())}_{pid[-4:]}"
            status = body.get("status", "pending")
            decision = update_decision_status(
                project_dir,
                decision_id,
                status=status,
                decided_by="copilot",
                title=title,
                rationale=body.get("rationale", ""),
                action=body.get("action", ""),
                target=body.get("target", ""),
            )
            self._send_json({"success": True, "decision_id": decision_id, "decision": decision})
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
