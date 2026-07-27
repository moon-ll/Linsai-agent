#!/usr/bin/env python3
"""web_routes_system.py — 系统状态路由 Mixin。

提供 SystemRoutesMixin，封装版本/心跳/记忆/LLM状态/Provider/用量/工具/
同步/备份/后台任务等 HTTP 路由：
    - GET  /api/version                版本号
    - GET  /api/heartbeat              心跳 + 主动提醒
    - GET  /api/memory/status          记忆系统状态
    - GET  /api/memory/reflow          手动触发认知回流
    - GET  /api/llm-status             LLM 状态
    - GET  /api/providers              Provider 列表
    - GET  /api/providers/current      当前 Provider
    - GET  /api/usage                  Token 用量
    - GET  /api/usage/daily            日用量
    - GET  /api/tools                  可用工具列表
    - GET+POST /api/sync/status        同步状态
    - GET  /api/sync/auto-status       自动同步状态
    - GET  /api/backup/list            备份列表
    - GET  /api/task-status/{id}       后台任务状态
    - POST /api/llm-provider           切换 LLM Provider
    - POST /api/switch-provider        切换 LLM Provider（别名）
    - POST /api/sync/run               触发同步
    - POST /api/backup                 备份操作

路由表格式：(HTTP方法, re.compile(正则), handler名)
handler 签名：GET/DELETE → (self, parsed, body=None, **path_params)
             POST/PUT   → (self, parsed, body, **path_params)
仅使用 Python 标准库。
"""

import datetime
import json
import re
from pathlib import Path

import web_base
from web_base import (
    _log,
    _try_acquire_kb_busy,
    _release_kb_busy,
    _bg_tasks,
    _bg_tasks_lock,
)
from common import lazy_load

import proactive_engine as pe
import llm_router as lr
import usage_tracker as ut
import sync_engine as se
import backup_manager as bm


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_SYSTEM_ROUTES = [
    # --- GET ---
    ("GET", re.compile(r"^/api/version$"), "_sys_version"),
    ("GET", re.compile(r"^/api/dashboard$"), "_sys_dashboard"),
    ("GET", re.compile(r"^/api/health$"), "_sys_health"),
    ("GET", re.compile(r"^/api/heartbeat$"), "_sys_heartbeat"),
    ("GET", re.compile(r"^/api/memory/status$"), "_sys_memory_status"),
    ("GET", re.compile(r"^/api/memory/reflow$"), "_sys_memory_reflow"),
    ("GET", re.compile(r"^/api/llm-status$"), "_sys_llm_status"),
    ("GET", re.compile(r"^/api/providers$"), "_sys_providers"),
    ("GET", re.compile(r"^/api/providers/current$"), "_sys_providers_current"),
    ("GET", re.compile(r"^/api/usage$"), "_sys_usage"),
    ("GET", re.compile(r"^/api/usage/daily$"), "_sys_usage_daily"),
    ("GET", re.compile(r"^/api/tools$"), "_sys_tools"),
    ("GET", re.compile(r"^/api/sync/status$"), "_sys_sync_status"),
    ("GET", re.compile(r"^/api/sync/auto-status$"), "_sys_sync_auto_status"),
    ("GET", re.compile(r"^/api/backup/list$"), "_sys_backup_list"),
    ("GET", re.compile(r"^/api/task-status/(?P<task_id>.+)$"), "_sys_task_status"),
    # --- POST ---
    ("POST", re.compile(r"^/api/llm-provider$"), "_sys_llm_provider"),
    ("POST", re.compile(r"^/api/switch-provider$"), "_sys_llm_provider"),
    ("POST", re.compile(r"^/api/sync/status$"), "_sys_sync_status"),
    ("POST", re.compile(r"^/api/sync/run$"), "_sys_sync_run"),
    ("POST", re.compile(r"^/api/backup$"), "_sys_backup"),
    # --- 生命周期管理（v6.5.0）---
    ("GET", re.compile(r"^/api/lifecycle/dashboard$"), "_sys_lifecycle_dashboard"),
    ("GET", re.compile(r"^/api/lifecycle/list/(?P<status>.+)$"), "_sys_lifecycle_list"),
    ("POST", re.compile(r"^/api/lifecycle/register$"), "_sys_lifecycle_register"),
    ("POST", re.compile(r"^/api/lifecycle/(?P<proposal_id>[^/]+)/transition$"), "_sys_lifecycle_transition"),
    ("POST", re.compile(r"^/api/lifecycle/(?P<proposal_id>[^/]+)/optimize$"), "_sys_lifecycle_optimize"),
    ("POST", re.compile(r"^/api/lifecycle/(?P<proposal_id>[^/]+)/feedback$"), "_sys_lifecycle_feedback"),
    ("POST", re.compile(r"^/api/lifecycle/cron-sweep$"), "_sys_lifecycle_cron_sweep"),
]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class SystemRoutesMixin:
    """系统状态路由 Mixin。"""

    # --- GET ---

    def _sys_version(self, parsed, body=None):
        """版本号"""
        version = (web_base._PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self._send_json({"version": version, "name": "LinSai-CoPilot"})

    def _sys_dashboard(self, parsed, body=None):
        """v6.0 仪表盘聚合：今日文献/任务/决策/hermes状态，一次请求返回。"""
        result = {"papers": {}, "tasks": {}, "decisions": [], "hermes": {}}

        # 1. 文献候选统计（从 item-status.json）
        try:
            import state_sync as ss
            summary = ss.get_status_summary()
            result["papers"] = {
                "total": sum(summary.values()),
                "unseen": summary.get("unseen", 0) + summary.get("pushed", 0) + summary.get("candidate", 0) + summary.get("interested", 0),
                "pushed": summary.get("pushed", 0),
                "viewed": summary.get("viewed", 0),
                "archived": summary.get("archived", 0),
            }
            # 取前3篇 pushed/unseen 的论文
            items = ss.get_items_by_status()
            top = sorted([i for i in items if i.get("status") in ("pushed", "unseen", "candidate")],
                        key=lambda x: x.get("score", 0), reverse=True)[:3]
            result["papers"]["preview"] = [{"arxiv_id": p.get("arxiv_id", ""), "title": p.get("title", ""),
                                           "direction": p.get("direction", ""), "pushed": p.get("status") == "pushed"}
                                          for p in top]
        except Exception:
            result["papers"] = {"total": 0, "unseen": 0, "preview": []}

        # 2. 任务统计
        try:
            import task_manager as tm
            tasks = tm.list_tasks()
            active = [t for t in tasks if t.get("status") == "active"]
            backlog = [t for t in tasks if t.get("status") == "backlog"]
            result["tasks"] = {
                "total": len(tasks),
                "active": len(active),
                "backlog": len(backlog),
                "preview": [{"task_id": t.get("task_id", ""), "title": t.get("title", "")[:40],
                            "status": t.get("status", ""), "assignee": t.get("assignee", "")}
                           for t in (active + backlog)[:3]],
            }
        except Exception:
            result["tasks"] = {"total": 0, "active": 0, "preview": []}

        # 3. NSFC 待决策项
        try:
            import project_reader as pr
            pending = pr.get_nsfc_pending()
            result["decisions"] = [{"id": p["id"], "title": p["title"][:60], "topic": p.get("related_topic", "")}
                                  for p in pending[:3]]
            result["decisions_total"] = len(pending)
        except Exception:
            result["decisions"] = []

        # 4. hermes cron 状态
        try:
            import hermes_bridge as hb
            jobs = hb.cron_list()
            active_jobs = [j for j in jobs if j.get("status") == "active"]
            result["hermes"] = {
                "available": hb.check_hermes_available().get("hermes_cli", False),
                "cron_active": len(active_jobs),
                "cron_total": len(jobs),
                "jobs": [{"name": j["name"][:30], "schedule": j.get("schedule", ""),
                         "last_status": j.get("last_status", "")} for j in active_jobs[:3]],
            }
        except Exception:
            result["hermes"] = {"available": False, "cron_active": 0}

        self._send_json(result)

    def _sys_health(self, parsed, body=None):
        """系统健康检查：聚合版本、LLM、知识库、关键目录状态。"""
        import os
        from paths import KNOWLEDGE_DIR, MEMORY_DIR, SESSIONS_DIR, TASKS_DIR

        health = {
            "status": "ok",
            "version": "",
            "llm": {},
            "knowledge_base": {},
            "directories": {},
        }

        # 版本
        try:
            version_path = web_base._PROJECT_ROOT / "VERSION"
            health["version"] = version_path.read_text(encoding="utf-8").strip()
        except Exception:
            health["version"] = "unknown"

        # LLM 状态
        try:
            status = lr.get_status()
            health["llm"] = {
                "active_provider": status.get("active_provider", ""),
                "providers": [
                    {"name": p["name"], "available": p["available"]}
                    for p in status.get("providers", [])
                ],
            }
        except Exception as e:
            health["llm"] = {"error": str(e)}

        # 知识库统计
        try:
            import knowledge_base as kb
            summary = kb.get_kb_health()
            health["knowledge_base"] = {
                "total_docs": summary.get("raw_count", 0) + summary.get("wiki_count", 0),
                "wiki_count": summary.get("wiki_count", 0),
                "raw_count": summary.get("raw_count", 0),
                "graph_nodes": summary.get("graph_nodes", 0),
            }
        except Exception as e:
            health["knowledge_base"] = {"error": str(e)}

        # 关键目录可访问性
        for name, path in [
            ("knowledge", KNOWLEDGE_DIR),
            ("memory", MEMORY_DIR),
            ("sessions", SESSIONS_DIR),
            ("tasks", TASKS_DIR),
        ]:
            health["directories"][name] = {
                "exists": path.exists(),
                "writable": os.access(str(path), os.W_OK) if path.exists() else False,
            }

        # 总体状态：LLM 至少一个可用 + 知识库无错误 + 目录全部存在
        llm_ok = any(p.get("available") for p in health["llm"].get("providers", []))
        kb_ok = "error" not in health["knowledge_base"]
        dirs_ok = all(d["exists"] for d in health["directories"].values())
        health["status"] = "ok" if (llm_ok and kb_ok and dirs_ok) else "degraded"

        self._send_json(health)

    def _sys_heartbeat(self, parsed, body=None):
        """心跳 + 主动提醒"""
        try:
            reminders = pe.heartbeat()
            # v3.4: 生成主动消息文案，让前端可直接展示
            messages = []
            for sig in reminders[:3]:
                try:
                    msg = pe.generate_proactive_message(sig)
                    messages.append({"type": sig.get("type", ""), "severity": sig.get("severity", "low"), "message": msg})
                except Exception as e:
                    if _log:
                        _log.debug("生成主动消息失败: %s", e)
            self._send_json({"status": "ok", "reminders": reminders, "proactive_messages": messages})
        except Exception as e:
            self._send_json({"status": "ok", "reminders": [], "proactive_messages": [], "error": str(e)})

    def _sys_memory_status(self, parsed, body=None):
        """记忆系统状态"""
        try:
            from memory_reflow import get_memory_status
            status = get_memory_status()
            self._send_json(status)
        except Exception as e:
            self._send_json({"error": str(e)})

    def _sys_memory_reflow(self, parsed, body=None):
        """手动触发认知回流"""
        try:
            from memory_reflow import reflow_all
            result = reflow_all(max_count=20)
            self._send_json({"success": True, "result": result})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def _sys_llm_status(self, parsed, body=None):
        """LLM 状态"""
        try:
            self._send_json(lr.get_status())
        except Exception as e:
            self._send_json({"provider": "none", "model": "未配置", "error": str(e)})

    def _sys_providers(self, parsed, body=None):
        """Provider 列表"""
        status = lr.get_status()
        self._send_json({"providers": status.get("providers", [])})

    def _sys_providers_current(self, parsed, body=None):
        """当前 Provider"""
        status = lr.get_status()
        self._send_json({"current": status.get("force_provider") or "auto"})

    def _sys_usage(self, parsed, body=None):
        """Token 用量"""
        self._send_json(ut.get_usage_summary())

    def _sys_usage_daily(self, parsed, body=None):
        """日用量"""
        self._send_json(ut.get_stats("daily"))

    def _sys_tools(self, parsed, body=None):
        """可用工具列表"""
        te_mod = lazy_load("tool_engine")
        if te_mod:
            self._send_json({"tools": te_mod.list_tools()})
        else:
            self._send_json({"tools": []})

    def _sys_sync_status(self, parsed, body=None):
        """同步状态（GET+POST 重复）"""
        self._send_json(se.get_sync_status())

    def _sys_sync_auto_status(self, parsed, body=None):
        """自动同步状态（LaunchAgent + auto_sync_history）"""
        agent_path = Path.home() / "Library" / "LaunchAgents" / "com.linsai.kb-auto-sync.plist"
        sync_state_path = web_base._PROJECT_ROOT / "memory" / "sync-state.json"
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

    def _sys_backup_list(self, parsed, body=None):
        """备份列表"""
        try:
            backups = bm.list_backups()
            self._send_json({"backups": [
                {"name": b.name, "size_kb": round(b.stat().st_size / 1024, 1),
                 "modified": datetime.datetime.fromtimestamp(b.stat().st_mtime).isoformat()}
                for b in backups[:20]
            ]})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    # ------------------------------------------------------------------
    # 生命周期管理（v6.5.0）
    # ------------------------------------------------------------------

    def _sys_lifecycle_dashboard(self, parsed, body=None):
        """生命周期仪表盘"""
        try:
            from proposal_lifecycle import ProposalLifecycle
            lc = ProposalLifecycle()
            dashboard = lc.get_dashboard()
            self._send_json({"status": "ok", "data": dashboard})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _sys_lifecycle_list(self, parsed, body=None, **kwargs):
        """按状态列出 proposal"""
        status = parsed.group("status") if hasattr(parsed, "group") else None
        try:
            from proposal_lifecycle import ProposalLifecycle
            lc = ProposalLifecycle()
            proposals = lc.list_by_status(status)
            self._send_json({"status": "ok", "proposals": proposals})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _sys_lifecycle_register(self, parsed, body=None):
        """注册新 proposal

        body 必填：proposal_id
        body 可选：project_type（general/key/major）
        """
        if not body or "proposal_id" not in body:
            self._send_json({"error": "缺少 proposal_id"}, 400)
            return
        try:
            from proposal_lifecycle import ProposalLifecycle
            lc = ProposalLifecycle()
            result = lc.register(
                body["proposal_id"],
                project_type=body.get("project_type", "general"),
                source=body.get("source", "new"),
                source_detail=body.get("source_detail", ""),
            )
            self._send_json({"status": "ok", "data": result})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _sys_lifecycle_transition(self, parsed, body=None, **kwargs):
        """流转 proposal

        body 必填：to_stage
        body 可选：reason
        """
        proposal_id = parsed.group("proposal_id")
        if not body or "to_stage" not in body:
            self._send_json({"error": "缺少 to_stage"}, 400)
            return
        try:
            from proposal_lifecycle import ProposalLifecycle
            lc = ProposalLifecycle()
            result = lc.transition(proposal_id, body["to_stage"], body.get("reason", ""))
            self._send_json({"status": "ok", "data": result})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _sys_lifecycle_optimize(self, parsed, body=None, **kwargs):
        """执行一轮对抗优化（后台异步，因为 hermes oneshot 需要 30s-5min）"""
        proposal_id = parsed.group("proposal_id")
        import threading, uuid
        task_id = f"opt_{uuid.uuid4().hex[:8]}"
        with _bg_tasks_lock:
            _bg_tasks[task_id] = {"status": "running", "proposal_id": proposal_id, "started_at": _now_utc()}
        def _worker():
            try:
                from proposal_lifecycle import ProposalLifecycle
                lc = ProposalLifecycle()
                result = lc.optimize_cycle(proposal_id)
                with _bg_tasks_lock:
                    _bg_tasks[task_id] = {"status": "done", "result": result, "finished_at": _now_utc()}
            except Exception as e:
                with _bg_tasks_lock:
                    _bg_tasks[task_id] = {"status": "failed", "error": str(e), "finished_at": _now_utc()}
        threading.Thread(target=_worker, daemon=True).start()
        self._send_json({"status": "accepted", "task_id": task_id, "message": "优化已启动（后台执行，hermes oneshot 需要 1-5 分钟）"})

    def _sys_lifecycle_feedback(self, parsed, body=None, **kwargs):
        """提交人工反馈

        body 必填：feedback_text
        body 可选：verdict（默认 major_revision）
        """
        proposal_id = parsed.group("proposal_id")
        if not body or "feedback_text" not in body:
            self._send_json({"error": "缺少 feedback_text"}, 400)
            return
        try:
            from proposal_lifecycle import ProposalLifecycle
            lc = ProposalLifecycle()
            result = lc.submit_feedback(
                proposal_id, body["feedback_text"],
                verdict=body.get("verdict", "major_revision"),
            )
            self._send_json({"status": "ok", "data": result})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _sys_lifecycle_cron_sweep(self, parsed, body=None):
        """执行 cron 扫描（后台异步，因为多个课题的 hermes oneshot 需要很长时间）"""
        import threading, uuid
        task_id = f"sweep_{uuid.uuid4().hex[:8]}"
        with _bg_tasks_lock:
            _bg_tasks[task_id] = {"status": "running", "type": "cron_sweep", "started_at": _now_utc()}
        def _worker():
            try:
                from proposal_lifecycle import ProposalLifecycle
                lc = ProposalLifecycle()
                result = lc.run_cron_sweep()
                with _bg_tasks_lock:
                    _bg_tasks[task_id] = {"status": "done", "result": result, "finished_at": _now_utc()}
            except Exception as e:
                with _bg_tasks_lock:
                    _bg_tasks[task_id] = {"status": "failed", "error": str(e), "finished_at": _now_utc()}
        threading.Thread(target=_worker, daemon=True).start()
        self._send_json({"status": "accepted", "task_id": task_id, "message": "cron 扫描已启动（后台执行）"})

    def _sys_task_status(self, parsed, body=None, task_id=None):
        """后台任务状态"""
        with _bg_tasks_lock:
            task = _bg_tasks.get(task_id, {"status": "unknown"})
        self._send_json(task)

    # --- POST ---

    def _sys_llm_provider(self, parsed, body):
        """切换 LLM Provider"""
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

    def _sys_sync_run(self, parsed, body):
        """触发多端同步（防重入）"""
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

    def _sys_backup(self, parsed, body):
        """备份操作（list/create/restore）"""
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
