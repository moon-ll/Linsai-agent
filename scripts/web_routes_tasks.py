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
# v5.2: kanban_reader 桥接 hermes kanban.db
import kanban_reader as kr
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
    ("POST", re.compile(r"^/api/tasks/ai-assist$"), "_task_ai_assist"),
    ("POST", re.compile(r"^/api/tasks/(?P<tid>[^/]+)$"), "_task_post_action"),  # 兜底：POST删除等
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
        """任务列表（v5.2: 合并 hermes kanban.db + 本地任务）"""
        # v5.2: 优先从 hermes kanban.db 读取
        tasks = []
        if kr.is_available():
            try:
                kanban_tasks = kr.list_tasks()
                tasks.extend(kanban_tasks)
            except Exception as e:
                if _log:
                    _log.warning("读取 kanban.db 失败，回退本地: %s", e)
        # 合并本地任务（兼容降级）
        try:
            local_tasks = tm.list_tasks()
            for t in local_tasks:
                t["source"] = "local"
            tasks.extend(local_tasks)
        except Exception:
            pass
        self._send_json(tasks)

    def _task_get(self, parsed, tid):
        """单个任务详情（v5.2: kanban 任务用 t_ 前缀识别）"""
        # v5.2: kanban 任务
        if tid.startswith("t_") and kr.is_available():
            task = kr.get_task(tid)
            if task:
                self._send_json(task)
                return
            self._send_json({"error": f"kanban 任务不存在: {tid}"}, 404)
            return
        # 本地任务
        try:
            task = tm.get_task(tid)
            self._send_json(task)
        except FileNotFoundError:
            self._send_json({"error": f"任务不存在: {tid}"}, 404)

    # --- POST ---

    def _task_ai_assist(self, parsed, body):
        """AI 辅助任务指派：根据用户输入的目标，生成完整的任务描述 + hermes 派活 prompt。

        用户只需提供 task_goal（任务目标）和 requirements（要求，可选），
        AI 会自动生成：
          - description: 结构化的任务描述（背景/目标/交付物/约束）
          - hermes_prompt: 可直接派给 hermes 的执行指令
          - suggested_project: 建议归属项目
          - suggested_priority: 建议优先级
        """
        goal = body.get("goal", "").strip()
        if not goal:
            self._send_json({"error": "请提供任务目标"}, 400)
            return
        requirements = body.get("requirements", "").strip()
        project = body.get("project", "")

        # 构建 AI 辅助 prompt
        sys_prompt = (
            "你是林赛，强场超快光学独立PI。用户想创建一个科研任务并可能派给 hermes agent 执行。"
            "请根据用户的任务目标，生成结构化的任务描述和 hermes 派活指令。\n\n"
            "输出格式（严格JSON）：\n"
            '{"description": "3-5句话的任务描述，包含背景和目标", '
            '"deliverables": "预期产出物（如报告/数据/文档）", '
            '"constraints": "约束条件（如时间/方法/格式）", '
            '"hermes_prompt": "可直接派给hermes的完整执行指令（包含目标/步骤/产出格式）", '
            '"suggested_priority": "high/medium/low"}\n'
            "只输出JSON，不要其他内容。"
        )
        user_msg = f"任务目标：{goal}"
        if requirements:
            user_msg += f"\n额外要求：{requirements}"
        if project:
            user_msg += f"\n归属项目：{project}"

        try:
            import llm_router as lr
            router = lr.LLMRouter()
            messages = [{"role": "user", "content": user_msg}]
            resp, usage, provider = router.call_llm(sys_prompt, messages)
            # 解析 JSON
            import json as _json
            # 清理可能的 markdown 代码块包裹
            resp_clean = resp.strip()
            if resp_clean.startswith("```"):
                resp_clean = resp_clean.split("\n", 1)[1] if "\n" in resp_clean else resp_clean[3:]
            if resp_clean.endswith("```"):
                resp_clean = resp_clean.rsplit("```", 1)[0]
            resp_clean = resp_clean.strip()
            result = _json.loads(resp_clean)
            result["goal"] = goal
            result["success"] = True
            self._send_json(result)
        except _json.JSONDecodeError:
            # LLM 返回的不是合法 JSON，返回原始文本
            self._send_json({"success": True, "description": resp[:500], "hermes_prompt": resp[:500],
                             "deliverables": "", "constraints": "", "suggested_priority": "medium",
                             "goal": goal, "raw": True})
        except Exception as e:
            self._send_json({"error": f"AI 辅助失败: {e}"}, 500)

    def _task_create(self, parsed, body):
        """创建任务（v5.2: 支持 kanban.db 创建，assignee=hermes 时写入 kanban）"""
        title = body.get("title", "").strip()
        if not title:
            self._send_json({"error": "缺少 title"}, 400)
            return
        project = body.get("project", "").strip()
        assignee = body.get("assignee", "myself")

        # v5.2: assignee=hermes 或 source=hermes 时写入 kanban.db
        if (assignee == "hermes" or body.get("source") == "hermes") and kr.is_available():
            kanban_id = kr.create_task(
                title=title,
                description=body.get("description", ""),
                assignee=body.get("kanban_assignee", "copilot"),
                priority=body.get("priority", "medium"),
                copilot_status="backlog",
                created_by="copilot",
            )
            if kanban_id:
                task_obj = kr.get_task(kanban_id) or {
                    "task_id": kanban_id, "title": title,
                    "status": "backlog", "source": "hermes",
                }
                # 派活给 hermes
                dispatch_id = ""
                if assignee == "hermes":
                    prompt = body.get("hermes_prompt", "").strip() or body.get("prompt", "").strip() or f"请执行项目任务：{title}。"
                    dispatch_id = self._do_dispatch_hermes(kanban_id, prompt, project, source="create")
                task_obj["dispatch_id"] = dispatch_id
                self._send_json(task_obj)
                return
            # kanban 创建失败，回退本地
            if _log:
                _log.warning("kanban.db 创建失败，回退本地任务")

        # 本地任务创建
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
            # 优先使用 AI 生成的 hermes_prompt，其次 body.prompt，最后从 title+description 构造
            prompt = body.get("hermes_prompt", "").strip() or body.get("prompt", "").strip() or f"请执行项目任务：{title}。" + (f"\n描述：{body.get('description','')}" if body.get("description") else "")
            dispatch_id = self._do_dispatch_hermes(tid, prompt, project, source="create")
        # P5-1: 返回完整任务对象，确保前端 createNewTask() 可直接 push 到 State.tasks
        try:
            task_obj = tm.get_task(tid)
            task_obj["source"] = "local"
            task_obj["dispatch_id"] = dispatch_id
            self._send_json(task_obj)
        except Exception:
            self._send_json({"success": True, "task_id": tid, "title": title, "status": "backlog", "source": "local", "dispatch_id": dispatch_id})

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
        """通用字段更新（含 status 拖拽）。

        v5.2: kanban 任务（t_ 前缀）更新状态到 kanban.db
        """
        # v5.2: kanban 任务状态更新
        if tid.startswith("t_") and kr.is_available():
            new_status = body.get("status", "")
            if new_status:
                ok = kr.update_task_status(tid, new_status)
                if ok:
                    task = kr.get_task(tid)
                    self._send_json({"success": True, "task": task})
                    return
                self._send_json({"error": "kanban 状态更新失败"}, 500)
                return
            # 非状态更新（如 title/description）暂不支持 kanban 任务
            self._send_json({"error": "kanban 任务仅支持状态更新"}, 400)
            return
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

    def _task_post_action(self, parsed, body, tid):
        """POST 兜底路由（action=delete 等）"""
        action = body.get("action", "")
        if action == "delete":
            ok = tm.delete_task(tid)
            if ok:
                self._send_json({"success": True})
            else:
                self._send_json({"error": "任务不存在"}, 404)
        else:
            self._send_json({"error": "未知 action"}, 400)

    def _task_delete(self, parsed, tid):
        """删除任务"""
        ok = tm.delete_task(tid)
        if ok:
            self._send_json({"success": True})
        else:
            self._send_json({"error": "任务不存在"}, 404)
