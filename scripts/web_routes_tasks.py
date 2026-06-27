#!/usr/bin/env python3
"""web_routes_tasks.py — 任务路由 Mixin。

提供 TaskRoutesMixin，封装任务 CRUD、派活、子任务、进度更新等 HTTP 路由：
    - GET    /api/tasks                  任务列表
    - GET    /api/tasks/{tid}            单个任务详情
    - POST   /api/tasks                  创建任务（assignee=hermes 时自动派活）
    - POST   /api/tasks/{tid}/dispatch   派活给 hermes
    - PUT    /api/tasks/{tid}            通用字段更新（含 status 拖拽）
    - PUT    /api/tasks/{tid}/subtasks   切换子任务完成状态
    - PUT    /api/tasks/{tid}/progress   更新进度
    - DELETE /api/tasks/{tid}            删除任务

_do_dispatch_hermes 方法也位于本 Mixin（任务创建/派活共用），它调用
web_routes_projects 中的 _write_dispatch_to_hermes_plans / _dispatch_hermes_async。

路由表格式：(HTTP方法, re.compile(正则), handler名)
handler 签名：GET/DELETE → (self, parsed, **path_params)
             POST/PUT   → (self, parsed, body, **path_params)
仅使用 Python 标准库。
"""

import re
import threading
from urllib.parse import parse_qs  # noqa: F401  (保持与其它路由模块导入风格一致)

from web_base import _log

import task_manager as tm
import project_dispatch as pdh
import hermes_bridge as hb  # noqa: F401  (派活链路依赖，保持显式导入)
# _do_dispatch_hermes 依赖 projects 模块中的跨进程派活函数
from web_routes_projects import _write_dispatch_to_hermes_plans, _dispatch_hermes_async


# ---------------------------------------------------------------------------
# 路由表（更具体的路由放在前面）
# ---------------------------------------------------------------------------
_TASK_ROUTES = [
    # GET
    ("GET", re.compile(r"^/api/tasks$"), "_task_list"),
    ("GET", re.compile(r"^/api/tasks/(?P<tid>[^/]+)$"), "_task_get"),
    # POST
    ("POST", re.compile(r"^/api/tasks$"), "_task_create"),
    ("POST", re.compile(r"^/api/tasks/(?P<tid>[^/]+)/dispatch$"), "_task_dispatch"),
    # PUT（更具体的路由放在前面）
    ("PUT", re.compile(r"^/api/tasks/(?P<tid>[^/]+)/subtasks$"), "_task_subtasks"),
    ("PUT", re.compile(r"^/api/tasks/(?P<tid>[^/]+)/progress$"), "_task_progress"),
    ("PUT", re.compile(r"^/api/tasks/(?P<tid>[^/]+)$"), "_task_update"),
    # DELETE
    ("DELETE", re.compile(r"^/api/tasks/(?P<tid>.+)$"), "_task_delete"),
]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class TaskRoutesMixin:
    """任务路由 Mixin。"""

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
            if _log:
                _log.debug("写入 hermes plans 失败: %s", e)
        # 2. 起异步线程执行 oneshot 并回写结果（补齐 fire-and-forget 缺口）
        threading.Thread(
            target=_dispatch_hermes_async,
            args=(dispatch_id, prompt, 300),
            daemon=True,
        ).start()
        return dispatch_id

    # --- GET ---

    def _task_list(self, parsed):
        """任务列表"""
        tasks = tm.list_tasks()
        self._send_json(tasks)

    def _task_get(self, parsed, tid):
        """单个任务详情"""
        try:
            task = tm.get_task(tid)
            self._send_json(task)
        except FileNotFoundError:
            self._send_json({"error": f"任务不存在: {tid}"}, 404)

    # --- POST ---

    def _task_create(self, parsed, body):
        """创建任务（assignee=hermes 时自动派活）"""
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

    def _task_dispatch(self, parsed, body, tid):
        """派活给 hermes（任务卡片⚡按钮）"""
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

    # --- PUT ---

    def _task_update(self, parsed, body, tid):
        """通用字段更新（含 status 拖拽，修复 task.js:84 的 404 bug）"""
        try:
            updated = tm.update_task_fields(tid, **body)
            self._send_json({"success": True, "task": updated})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _task_subtasks(self, parsed, body, tid):
        """切换子任务完成状态"""
        subtask_id = body.get("subtask_id", "")
        try:
            tm.toggle_subtask(tid, subtask_id)
            self._send_json({"success": True})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _task_progress(self, parsed, body, tid):
        """更新进度"""
        progress = body.get("progress", 0)
        try:
            tm.update_progress(tid, int(progress))
            self._send_json({"success": True})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    # --- DELETE ---

    def _task_delete(self, parsed, tid):
        """删除任务"""
        ok = tm.delete_task(tid)
        if ok:
            self._send_json({"success": True})
        else:
            self._send_json({"error": "任务不存在"}, 404)
