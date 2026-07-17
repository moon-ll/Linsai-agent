#!/usr/bin/env python3
"""web_routes_projects.py — 项目/NSFC/论文池路由 Mixin。

提供 ProjectRoutesMixin，封装项目总控、NSFC 仪表盘、文献候选池、
意见/执行追踪等 HTTP 路由：
    - GET/POST  /api/projects                      项目概况
    - GET       /api/projects/list                 项目清单
    - GET       /api/projects/overview             项目总控总览
    - GET       /api/projects/opinions             意见列表
    - GET       /api/projects/dispatches           执行追踪列表
    - GET/POST  /api/projects/nsfc/*               NSFC 仪表盘/树/课题/资料/待决策/决策/章节/申请书
    - GET/POST  /api/projects/papers/*             候选/池/简报
    - POST      /api/projects/papers/feedback      文献反馈
    - POST      /api/projects/nsfc/pending/{pid}   待决策项操作
    - POST      /api/projects/nsfc/discuss-summary 讨论总结
    - POST      /api/projects/opinions             提交意见
    - PUT       /api/projects/opinions/{id}/resolve 标记意见已解决

同时包含跨进程派活函数 _write_dispatch_to_hermes_plans / _dispatch_hermes_async，
供 web_routes_tasks.py 的 _do_dispatch_hermes 调用。

路由表格式：(HTTP方法, re.compile(正则), handler名)
handler 签名：GET/DELETE → (self, parsed, body=None, **path_params)
             POST/PUT   → (self, parsed, body, **path_params)
仅使用 Python 标准库。
"""

import datetime
import json
import re
import threading
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs

import web_base
from web_base import _log, _get_file_lock

import project_reader as pr
import project_dispatch as pdh
import paper_pool as pp
import hermes_bridge as hb
import kb_importer as ki
import task_manager as tm
import common as _cms


# ---------------------------------------------------------------------------
# v3.1.0: 项目总控 — hermes 反馈落点（plans/ 目录契约）+ 异步派活 worker
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_PROJECT_ROUTES = [
    # --- GET ---
    ("GET", re.compile(r"^/api/projects$"), "_proj_overview"),
    ("GET", re.compile(r"^/api/projects/list$"), "_proj_list"),
    ("GET", re.compile(r"^/api/projects/overview$"), "_proj_overview_stats"),
    ("GET", re.compile(r"^/api/projects/opinions$"), "_proj_opinions"),
    ("GET", re.compile(r"^/api/projects/dispatches$"), "_proj_dispatches"),
    ("GET", re.compile(r"^/api/projects/nsfc/dashboard$"), "_proj_nsfc_dashboard"),
    ("GET", re.compile(r"^/api/projects/nsfc/tree$"), "_proj_nsfc_tree"),
    ("GET", re.compile(r"^/api/projects/nsfc/topics$"), "_proj_nsfc_topics"),
    ("GET", re.compile(r"^/api/projects/nsfc/references$"), "_proj_nsfc_references"),
    ("GET", re.compile(r"^/api/projects/nsfc/pending$"), "_proj_nsfc_pending"),
    ("GET", re.compile(r"^/api/projects/nsfc/decisions$"), "_proj_nsfc_decisions"),
    ("GET", re.compile(r"^/api/projects/nsfc/chapters$"), "_proj_nsfc_chapters"),
    ("GET", re.compile(r"^/api/projects/nsfc/proposal$"), "_proj_nsfc_proposal"),
    ("GET", re.compile(r"^/api/projects/papers/candidates$"), "_proj_papers_candidates"),
    ("GET", re.compile(r"^/api/projects/papers/pool$"), "_proj_papers_pool"),
    ("GET", re.compile(r"^/api/projects/papers/briefings$"), "_proj_papers_briefings"),
    # --- POST（GET 重复路由，do_POST 中也有同名端点） ---
    ("POST", re.compile(r"^/api/projects$"), "_proj_overview"),
    ("POST", re.compile(r"^/api/projects/nsfc/dashboard$"), "_proj_nsfc_dashboard"),
    ("POST", re.compile(r"^/api/projects/nsfc/tree$"), "_proj_nsfc_tree"),
    ("POST", re.compile(r"^/api/projects/nsfc/topics$"), "_proj_nsfc_topics"),
    ("POST", re.compile(r"^/api/projects/nsfc/references$"), "_proj_nsfc_references"),
    ("POST", re.compile(r"^/api/projects/nsfc/pending$"), "_proj_nsfc_pending"),
    ("POST", re.compile(r"^/api/projects/nsfc/decisions$"), "_proj_nsfc_decisions"),
    ("POST", re.compile(r"^/api/projects/nsfc/chapters$"), "_proj_nsfc_chapters"),
    ("POST", re.compile(r"^/api/projects/nsfc/proposal$"), "_proj_nsfc_proposal"),
    ("POST", re.compile(r"^/api/projects/papers/candidates$"), "_proj_papers_candidates"),
    ("POST", re.compile(r"^/api/projects/papers/pool$"), "_proj_papers_pool"),
    ("POST", re.compile(r"^/api/projects/papers/briefings$"), "_proj_papers_briefings"),
    # --- POST（独有） ---
    ("POST", re.compile(r"^/api/projects/papers/feedback$"), "_proj_papers_feedback"),
    ("POST", re.compile(r"^/api/projects/nsfc/pending/(?P<pid>.+)$"), "_proj_nsfc_pending_action"),
    ("POST", re.compile(r"^/api/projects/nsfc/discuss-summary$"), "_proj_nsfc_discuss_summary"),
    ("POST", re.compile(r"^/api/projects/opinions$"), "_proj_opinions_post"),
    # v4.1: 文献讨论归档
    ("POST", re.compile(r"^/api/paper-discussion/archive$"), "_paper_discussion_archive"),
    # v4.1: 轻量对话（讨论弹窗用）
    ("POST", re.compile(r"^/api/chat/simple$"), "_chat_simple"),
    # --- PUT ---
    ("PUT", re.compile(r"^/api/projects/opinions/(?P<op_id>[^/]+)/resolve$"), "_proj_opinion_resolve"),
]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class ProjectRoutesMixin:
    """项目/NSFC/论文池路由 Mixin。"""

    # --- GET（含 POST 重复） ---

    def _proj_overview(self, parsed, body=None):
        """项目概况（GET+POST 重复）"""
        self._send_json(pr.get_projects_overview())

    def _proj_list(self, parsed, body=None):
        """项目清单（供任务表单下拉框）"""
        self._send_json({"projects": pr.get_projects_list()})

    def _proj_overview_stats(self, parsed, body=None):
        """项目总控总览（聚合进度+任务+意见+执行）"""
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
            if _log:
                _log.debug("解析 NSFC 状态失败: %s", e)
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

    def _proj_opinions(self, parsed, body=None):
        """项目意见列表"""
        qs = parse_qs(parsed.query)
        self._send_json({"opinions": pdh.list_opinions(
            project=qs.get("project", [""])[0],
            status=qs.get("status", [""])[0],
        )})

    def _proj_dispatches(self, parsed, body=None):
        """执行追踪列表"""
        qs = parse_qs(parsed.query)
        self._send_json({"dispatches": pdh.list_dispatches(
            project=qs.get("project", [""])[0],
            status=qs.get("status", [""])[0],
            limit=int(qs.get("limit", ["50"])[0]),
        )})

    def _proj_nsfc_dashboard(self, parsed, body=None):
        """NSFC 仪表盘（GET+POST 重复）"""
        self._send_json(pr.parse_nsfc_state())

    def _proj_nsfc_tree(self, parsed, body=None):
        """NSFC 层次结构树（GET+POST 重复）"""
        self._send_json(pr.parse_nsfc_state_hierarchical())

    def _proj_nsfc_topics(self, parsed, body=None):
        """NSFC 课题产物卡片（GET+POST 重复）"""
        self._send_json({"topics": pr.get_nsfc_topics()})

    def _proj_nsfc_references(self, parsed, body=None):
        """NSFC 调研资料清单（GET+POST 重复）"""
        self._send_json(pr.get_nsfc_references())

    def _proj_nsfc_pending(self, parsed, body=None):
        """NSFC 待决策项（GET+POST 重复）"""
        self._send_json({"pending": pr.get_nsfc_pending()})

    def _proj_nsfc_decisions(self, parsed, body=None):
        """NSFC 决策时间轴（GET+POST 重复）"""
        limit = int(parse_qs(parsed.query).get("limit", ["10"])[0])
        self._send_json({"decisions": pr.get_decisions(limit=limit)})

    def _proj_nsfc_chapters(self, parsed, body=None):
        """NSFC 申请书章节列表（GET+POST 重复）"""
        self._send_json({"chapters": pr.get_proposal_chapters()})

    def _proj_nsfc_proposal(self, parsed, body=None):
        """NSFC 申请书章节内容（GET+POST 重复）"""
        topic = parse_qs(parsed.query).get("topic", [""])[0]
        self._send_json(pr.read_proposal_content(topic))

    def _proj_papers_candidates(self, parsed, body=None):
        """文献候选列表（GET+POST 重复）"""
        self._send_json(pr.get_candidates())

    def _proj_papers_pool(self, parsed, body=None):
        """候选池（三状态持久化）+ v4.2 统一状态合并"""
        status_filter = parse_qs(parsed.query).get("status", [""])[0]
        pool_data = pp.get_pool(status=status_filter)
        # v4.2: 合并 item-status.json 的统一状态（推送标记等）
        try:
            import state_sync as ss
            for paper in pool_data.get("papers", []):
                aid = paper.get("arxiv_id", "")
                info = ss.get_item_info(aid)
                if info:
                    paper["unified_status"] = info.get("status", "")
                    paper["pushed_to_feishu"] = info.get("status", "") == "pushed" or \
                        any(h.get("status") == "pushed" for h in info.get("history", []))
                    paper["updated_by"] = info.get("updated_by", "")
            pool_data["status_summary_unified"] = ss.get_status_summary()
        except Exception:
            pass
        self._send_json(pool_data)

    def _proj_papers_briefings(self, parsed, body=None):
        """文献简报列表（GET+POST 重复）"""
        self._send_json({"briefings": pr.get_briefings()})

    # --- POST（独有） ---

    def _proj_papers_feedback(self, parsed, body):
        """文献反馈（感兴趣/跳过/归档）→ 归档+深分析+hermes偏好"""
        arxiv_id = body.get("arxiv_id", "").strip()
        action = body.get("action", "").strip()  # interested/skip/archive/later/discuss_done
        if not arxiv_id or action not in ("interested", "skip", "archive", "later", "discuss_done"):
            self._send_json({"error": "需要 arxiv_id 和 action(interested/skip/archive/later/discuss_done)"}, 400)
            return

        # 记录反馈到本地（累积偏好）
        fb_path = web_base._PROJECT_ROOT / "memory" / "paper-feedback.json"
        with _get_file_lock("paper-feedback"):
            fb = []
            if fb_path.exists():
                try:
                    fb = json.loads(fb_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    fb = []  # 容错：文件损坏时返回默认值
            fb.append({"arxiv_id": arxiv_id, "action": action, "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
            _cms.save_json(fb_path, fb[-200:])

        result: Dict[str, Any] = {"action": action, "arxiv_id": arxiv_id}

        # 候选池状态联动（v2.9.3 重构：感兴趣≠归档）
        pool_status_map = {
            "interested": pp.STATUS_VIEWED,
            "later": pp.STATUS_VIEWED,
            "skip": pp.STATUS_VIEWED,
            "archive": pp.STATUS_ARCHIVED,
            "discuss_done": pp.STATUS_ARCHIVED,
        }
        pp.update_status(arxiv_id, pool_status_map.get(action, pp.STATUS_VIEWED))

        # v3.7: 反向同步状态到 hermes status.json（失败记入待同步队列，不阻塞用户操作）
        try:
            import briefing_sync as bsync
            sync_result = bsync.sync_to_hermes(arxiv_id, pool_status_map.get(action, pp.STATUS_VIEWED), action)
            result["hermes_synced"] = sync_result.get("success", False)
        except Exception as e:
            if _log:
                _log.warning("反向同步 hermes 失败: %s", e)
            result["hermes_synced"] = False

        if action == "interested":
            # 感兴趣：仅记录偏好，不归档（归档需充分讨论后）
            # 异步反馈 hermes 偏好
            try:
                title = body.get("title", arxiv_id)
                def _hermes_feedback():
                    try:
                        hb.oneshot(f"用户对 arXiv {arxiv_id}（{title}）标记为感兴趣，请更新研究偏好记忆。", timeout=120)
                    except Exception as e:
                        if _log:
                            _log.debug("hermes 偏好反馈失败: %s", e)
                threading.Thread(target=_hermes_feedback, daemon=True).start()
            except Exception as e:
                if _log:
                    _log.debug("启动 hermes 反馈线程失败: %s", e)
        elif action in ("archive", "discuss_done"):
            # 归档：深度阅读+讨论后的沉淀
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
                label = "不感兴趣（跳过）" if action == "skip" else "稍后讨论"
                def _hermes_pref():
                    try:
                        hb.oneshot(f"用户对 arXiv {arxiv_id} 标记为{label}，请更新偏好。", timeout=60)
                    except Exception as e:
                        if _log:
                            _log.debug("hermes 偏好反馈失败: %s", e)
                threading.Thread(target=_hermes_pref, daemon=True).start()
            except Exception as e:
                if _log:
                    _log.debug("启动 hermes 偏好线程失败: %s", e)

        self._send_json({"success": True, "result": result})

    def _proj_nsfc_pending_action(self, parsed, body, pid):
        """NSFC 待决策项操作（approve/reject/discuss）"""
        action = body.get("action", "").strip()  # approve/reject/discuss
        dec_path = web_base._PROJECT_ROOT / "memory" / "nsfc-decisions.json"
        with _get_file_lock("nsfc-decisions"):
            decs = {}
            if dec_path.exists():
                try:
                    decs = json.loads(dec_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    decs = {}

            if action == "discuss":
                # 标记讨论中，返回该课题的知识库上下文供注入
                decs[pid] = {"status": "discussing", "started_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
                _cms.save_json(dec_path, decs)
                title = body.get("title", "")
                topic = body.get("related_topic", "")
                # v4.2: 同步到项目 .copilot-sync.json
                try:
                    import state_sync as ss
                    nsfc_dir = str(pr.NSFC_DIR)
                    ss.register_project(nsfc_dir, "NSFC-强场超快")
                    ss.update_decision_status(nsfc_dir, pid, "discussing", decided_by="copilot", title=title)
                except Exception:
                    pass
                # 收集该课题的 references 上下文
                context_files = []
                refs = pr.get_nsfc_references()
                for r in refs.get("references", [])[:5]:
                    context_files.append(r.get("path", ""))
                self._send_json({"success": True, "status": "discussing", "title": title,
                                 "context_files": context_files, "topic": topic})
            elif action in ("approve", "reject"):
                decs[pid] = {"status": action, "decided_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "summary": body.get("summary", "")}
                _cms.save_json(dec_path, decs)
                # v4.2: 同步到项目 .copilot-sync.json
                try:
                    import state_sync as ss
                    nsfc_dir = str(pr.NSFC_DIR)
                    ss.register_project(nsfc_dir, "NSFC-强场超快")
                    ss.update_decision_status(nsfc_dir, pid, action, decided_by="copilot",
                                             title=body.get("title", ""))
                except Exception:
                    pass
                # 异步反馈 hermes
                title = body.get("title", "")
                try:
                    label = "通过" if action == "approve" else "否决"
                    def _fb():
                        try:
                            hb.oneshot(f"用户对待决策项「{title}」标记为{label}。请更新项目状态。", timeout=120)
                        except Exception as e:
                            if _log:
                                _log.debug("hermes 反馈失败: %s", e)
                    threading.Thread(target=_fb, daemon=True).start()
                except Exception as e:
                    if _log:
                        _log.debug("启动 hermes 反馈线程失败: %s", e)
                self._send_json({"success": True, "status": action})
            else:
                self._send_json({"error": "action 需为 approve/reject/discuss"}, 400)

    def _proj_nsfc_discuss_summary(self, parsed, body):
        """NSFC 讨论总结 → 写 discussions + 反馈 hermes"""
        pid = body.get("pending_id", "")
        title = body.get("title", "")
        summary = body.get("summary", "").strip()
        topic = body.get("topic", "")
        if not summary:
            self._send_json({"error": "缺少 summary"}, 400)
            return

        # 写回 discussions/{date}_decisions.md
        today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        disc_dir = pr.NSFC_DIR / "discussions"
        disc_file = disc_dir / f"{today}_decisions.md"
        disc_dir.mkdir(parents=True, exist_ok=True)
        entry = f"\n\n## 决策: {title} 🌐 林赛CoPilot讨论捕获\n\n"
        entry += f"**决策**: ✅ 已讨论（{topic}）\n\n"
        entry += f"**讨论总结**:\n\n{summary}\n\n"
        entry += f"**来源**: 林赛CoPilot Web 讨论({datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})\n"
        entry += f"**可推翻**: 用户可在后续讨论中调整\n\n---\n"
        mode = "a" if disc_file.exists() else "w"
        with open(disc_file, mode, encoding="utf-8") as f:
            f.write(entry)

        # 更新持久化状态
        dec_path = web_base._PROJECT_ROOT / "memory" / "nsfc-decisions.json"
        with _get_file_lock("nsfc-decisions"):
            decs = {}
            if dec_path.exists():
                try:
                    decs = json.loads(dec_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    decs = {}
            if pid:
                decs[pid] = {"status": "discussed", "decided_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "summary": summary[:200]}
                _cms.save_json(dec_path, decs)

        # 异步反馈 hermes
        try:
            def _fb2():
                try:
                    hb.oneshot(f"用户在林赛CoPilot讨论了「{title}」（课题{topic}），结论：{summary[:500]}。请据此更新 state.md 和后续 BRAIN 计划。", timeout=180)
                except Exception as e:
                    if _log:
                        _log.debug("hermes 反馈失败: %s", e)
            threading.Thread(target=_fb2, daemon=True).start()
        except Exception as e:
            if _log:
                _log.debug("启动 hermes 反馈线程失败: %s", e)

        self._send_json({"success": True, "written_to": str(disc_file.relative_to(pr.NSFC_DIR)), "pid": pid})

    def _proj_opinions_post(self, parsed, body):
        """提交项目意见"""
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
                if _log:
                    _log.debug("意见反馈 hermes 失败: %s", e)
        self._send_json({"success": True, "opinion": op})

    # --- PUT ---

    def _proj_opinion_resolve(self, parsed, body, op_id):
        """标记意见已解决"""
        resolved = pdh.resolve_opinion(op_id)
        if resolved:
            self._send_json({"success": True, "opinion": resolved})
        else:
            self._send_json({"error": "意见不存在"}, 404)

    # ===================================================================
    # v4.1: 文献讨论独立窗口支持
    # ===================================================================

    def _chat_simple(self, parsed, body):
        """轻量对话端点（文献讨论弹窗用，不走 session/工具链，直接 LLM）。"""
        import llm_router as lr
        sys_prompt = body.get("system_prompt", "你是林赛，强场超快光学独立PI。")
        messages = body.get("messages", [])
        if not messages:
            self._send_json({"error": "缺少 messages"}, 400)
            return
        try:
            router = lr.LLMRouter()
            resp, usage, provider = router.call_llm(sys_prompt, messages)
            self._send_json({"response": resp, "provider": provider, "usage": usage})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _paper_discussion_archive(self, parsed, body):
        """文献讨论归档：全文→整理→凝练→概念。

        mode:
          auto — 全自动四步
          step1_summarize — 只做整理（返回摘要供用户确认）
          step2_finalize — 用户确认后凝练+提取概念
        """
        import llm_router as lr
        from datetime import datetime, timezone
        import kb_importer as ki
        import knowledge_base as kb

        arxiv_id = body.get("arxiv_id", "")
        title = body.get("title", "")
        mode = body.get("mode", "auto")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        today = datetime.now().strftime("%Y%m%d")

        # 收集对话全文
        messages = body.get("messages", [])
        full_text = "\n\n".join([f"{'🧑用户' if m['role']=='user' else '🔬林赛'}: {m['content']}" for m in messages])

        if mode in ("auto", "step1_summarize"):
            # 第一步：AI 整理讨论为结构化摘要
            sys_prompt = (
                "你是林赛。请把以下关于论文的讨论整理为结构化摘要。\n"
                "输出格式（JSON）：\n"
                '{"summary": "3-5段讨论摘要（核心观点/分歧/结论）", '
                '"key_points": ["核心观点1", "核心观点2", ...], '
                '"concepts": ["应提取为知识库概念的关键术语1", ...], '
                '"open_questions": ["未解决的问题1", ...]}\n'
                "只输出JSON。"
            )
            user_msg = f"论文：{title} (arXiv:{arxiv_id})\n\n讨论全文：\n{full_text[:6000]}"
            try:
                router = lr.LLMRouter()
                resp, _, _ = router.call_llm(sys_prompt, [{"role": "user", "content": user_msg}])
                import json as _json
                resp_clean = resp.strip()
                if resp_clean.startswith("```"): resp_clean = resp_clean.split("\n", 1)[1]
                if resp_clean.endswith("```"): resp_clean = resp_clean.rsplit("```", 1)[0]
                parsed_result = _json.loads(resp_clean.strip())
            except _json.JSONDecodeError:
                parsed_result = {"summary": resp[:1000], "key_points": [], "concepts": [], "open_questions": []}
            except Exception as e:
                self._send_json({"error": f"AI整理失败: {e}"}, 500)
                return

            if mode == "step1_summarize":
                self._send_json({"success": True, "summary": parsed_result.get("summary", ""),
                                 "concepts_suggested": parsed_result.get("concepts", []),
                                 "key_points": parsed_result.get("key_points", [])})
                return

            # auto 模式继续往下
            summary = parsed_result.get("summary", "")
            concepts = parsed_result.get("concepts", [])

        elif mode == "step2_finalize":
            summary = body.get("summary", "")
            concepts = body.get("concepts_suggested", [])
        else:
            self._send_json({"error": "未知 mode"}, 400)
            return

        # 第二步：保存讨论全文 + 摘要到知识库
        disc_dir = web_base._PROJECT_ROOT / "knowledge" / "wiki" / "projects" / "deepxiv-论文库" / "讨论记录"
        disc_dir.mkdir(parents=True, exist_ok=True)
        disc_file = disc_dir / f"讨论-{today}-{arxiv_id}.md"

        content = f"""---
title: "讨论：{title[:40]}"
type: "papers"
arxiv_id: "{arxiv_id}"
created: "{now}"
updated: "{now}"
tags: ["讨论记录", "文献阅读"]
related: ["高次谐波产生"]
project: ["deepxiv-论文库"]
growth_stage: "mature"
confidence: 0.85
---

# 讨论：{title}

**arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})

## 讨论摘要

{summary}

## 核心观点

"""
        for kp in (parsed_result.get("key_points", []) if mode == "auto" else []):
            content += f"- {kp}\n"
        content += f"\n## 开放问题\n\n"
        for oq in (parsed_result.get("open_questions", []) if mode == "auto" else []):
            content += f"- {oq}\n"
        content += f"\n## 讨论全文\n\n{full_text[:8000]}\n"

        disc_file.write_text(content, encoding="utf-8")

        # 第三步：提取概念条目（生成 seedling 笔记）
        concepts_generated = 0
        for concept_name in concepts[:5]:
            concept_name = concept_name.strip()
            if not concept_name or len(concept_name) < 2:
                continue
            # 检查是否已存在
            existing = kb.list_wiki_pages("concepts")
            if any(p["title"] == concept_name for p in existing):
                continue  # 已有则跳过
            # 生成 seedling 概念笔记
            stub_content = f"""---
title: "{concept_name}"
type: "concepts"
created: "{now}"
updated: "{now}"
tags: ["自动提取", "文献讨论"]
related: ["{title[:20]}"]
project: ["deepxiv-论文库"]
source_arxiv: "{arxiv_id}"
growth_stage: "seedling"
confidence: 0.4
---

# {concept_name}

> 从讨论 arXiv:{arxiv_id} 中提取的种子概念，待补充。

## 来源

- 讨论：{title}
- arXiv: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})

## 林赛的理解

（待补充——请基于讨论内容完善此概念笔记）
"""
            try:
                kb.save_wiki_page(concept_name, "concepts", stub_content)
                concepts_generated += 1
            except Exception:
                pass

        self._send_json({"success": True, "file": str(disc_file.name),
                         "concepts_generated": concepts_generated,
                         "summary": summary[:200]})
