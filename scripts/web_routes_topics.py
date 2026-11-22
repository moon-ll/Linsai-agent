# -*- coding: utf-8 -*-
"""课题工作台路由 Mixin（v8.0.0）——/api/topics/*。

v8 工作台的 Web 入口：课题看板、启动包详情、三个法定节点（启动/否决/归档）、
验收自检、每日深研触发（后台线程，deep-dive 经 hermes 耗时数分钟）。

注册：web_server.py 聚合 _TOPICS_ROUTES + TopicsRoutesMixin。

端点：
    GET  /api/topics                     看板（五阶段列表 + 统计）
    GET  /api/topics/{id}                详情（课题卡 + 报告 + 自检结果）
    POST /api/topics/{id}/activate       人工启动（ready/kickoff/questions → active）
    POST /api/topics/{id}/reject         否决（body: {reason}）
    POST /api/topics/{id}/archive        收尾归档
    POST /api/topics/{id}/check          运行验收自检
    POST /api/topics/daily               触发每日深研 worker（后台线程）
    GET  /api/topics/daily/status        深研 worker 执行状态
"""
from __future__ import annotations

import re

import web_base

# 后台深研 worker 状态（进程内，单实例足够）
_daily_status = {"running": False, "started_at": "", "result": None, "error": ""}


def _topic_id_from_path(parsed) -> str:
    path = getattr(parsed, "path", "") or ""
    m = re.match(r"^/api/topics/([^/]+)", path)
    return m.group(1) if m else ""


_TOPICS_ROUTES = [
    # --- GET ---
    ("GET", re.compile(r"^/api/topics/daily/status$"), "_topics_daily_status"),
    ("GET", re.compile(r"^/api/topics$"), "_topics_board"),
    ("GET", re.compile(r"^/api/topics/[^/]+$"), "_topics_detail"),
    # --- POST ---
    ("POST", re.compile(r"^/api/topics/daily$"), "_topics_daily_run"),
    ("POST", re.compile(r"^/api/topics/[^/]+/activate$"), "_topics_activate"),
    ("POST", re.compile(r"^/api/topics/[^/]+/reject$"), "_topics_reject"),
    ("POST", re.compile(r"^/api/topics/[^/]+/archive$"), "_topics_archive"),
    ("POST", re.compile(r"^/api/topics/[^/]+/check$"), "_topics_check"),
]


class TopicsRoutesMixin:
    """课题工作台路由 Mixin（v8.0.0）。"""

    # --- GET ---

    def _topics_board(self, parsed, body=None):
        """课题看板：五阶段列表 + 统计 + needs_human 待办。"""
        try:
            from topic_pipeline import state as tstate
            from topic_pipeline.card import STAGE_LABELS
            data = tstate.load_state()
            stages = {}
            for stage in ("questions", "kickoff", "ready", "active", "archive"):
                items = []
                for tid in tstate.list_by_stage(data, stage):
                    rec = data["topics"].get(tid) or {}
                    items.append({
                        "id": tid,
                        "title": rec.get("title", ""),
                        "problem": (rec.get("problem") or "")[:120],
                        "needs_human": bool(rec.get("needs_human")),
                        "gaps": rec.get("deep_dive_gaps") or rec.get("check_gaps") or [],
                        "updated_at": rec.get("updated_at", ""),
                    })
                stages[stage] = {"label": STAGE_LABELS.get(stage, stage), "count": len(items), "items": items}
            self._send_json({
                "success": True,
                "stages": stages,
                "rejected_count": len(data.get("rejected", {})),
                "needs_human": [tid for tid, rec in data.get("topics", {}).items()
                                if isinstance(rec, dict) and rec.get("needs_human")],
            })
        except Exception as e:  # noqa: BLE001
            self._send_json({"success": False, "error": str(e)}, status=500)

    def _topics_detail(self, parsed, body=None):
        """启动包详情：课题卡 + 报告正文 + 自检结果 + 状态。"""
        tid = _topic_id_from_path(parsed)
        try:
            from topic_pipeline import state as tstate
            from topic_pipeline.card import parse_card
            tdir = tstate.topic_dir(tid)
            if not tdir:
                self._send_json({"success": False, "error": f"课题不存在: {tid}"}, status=404)
                return
            from pathlib import Path
            tdir = Path(tdir)
            data = tstate.load_state()
            rec = data.get("topics", {}).get(tid) or {}
            card = parse_card(tdir / "topic-card.md")
            report_path = tdir / "topic-report.md"
            report = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
            check = {}
            check_path = tdir / "kickoff-check.json"
            if check_path.exists():
                import json as _json
                try:
                    check = _json.loads(check_path.read_text(encoding="utf-8"))
                except Exception:
                    check = {}
            self._send_json({
                "success": True,
                "id": tid,
                "stage": rec.get("stage", ""),
                "card": card,
                "record": {k: rec.get(k) for k in
                           ("title", "problem", "source", "related", "migrated_from",
                            "needs_human", "deep_dive_gaps", "gap_repair_counts", "stage_history")},
                "report": report,
                "report_chars": len(report),
                "check": check,
                "dir": str(tdir),
            })
        except Exception as e:  # noqa: BLE001
            self._send_json({"success": False, "error": str(e)}, status=500)

    def _topics_daily_status(self, parsed, body=None):
        result = dict(_daily_status)
        # v8.0.3 兜底：cron worker 在独立进程运行，本进程内存态为空时
        # 扫描课题 deep-dive-runs.json 取最近一次深研结果（跨进程可见）
        if not result.get("running") and not result.get("result"):
            import json as _json
            from pathlib import Path as _P
            latest = None
            root = _P(web_base._PROJECT_ROOT) / "research_topics"
            for p in root.glob("*/deep-dive-runs.json"):
                try:
                    runs = _json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    continue
                for r in runs if isinstance(runs, list) else []:
                    at = str(r.get("at", ""))
                    if latest is None or at > str(latest.get("at", "")):
                        latest = r
            if latest:
                gaps = latest.get("gaps") or []
                steps = latest.get("steps") or []
                ok_steps = sum(1 for s in steps if s.get("success") or s.get("skipped"))
                result["last_run_at"] = latest.get("at", "")
                result["last_topic"] = latest.get("topic_id", "")
                result["summary"] = (
                    f"{latest.get('topic_id', '')} 完成 {ok_steps}/{len(steps)} 步"
                    + (f"，缺口: {','.join(gaps)}（下次补齐）" if gaps else "，无缺口"))
        self._send_json({"success": True, **result})

    # --- POST ---

    def _topics_activate(self, parsed, body=None):
        """法定节点①：人工启动 ready（或人工裁量 questions/kickoff）→ active。"""
        tid = _topic_id_from_path(parsed)
        try:
            from topic_pipeline import state as tstate
            from topic_pipeline.card import append_card_event
            from pathlib import Path
            data = tstate.load_state()
            rec = data.get("topics", {}).get(tid)
            if not rec:
                self._send_json({"success": False, "error": f"课题不存在: {tid}"}, status=404)
                return
            if rec.get("stage") not in ("ready", "questions", "kickoff"):
                self._send_json({"success": False,
                                 "error": f"当前阶段 {rec.get('stage')} 不可启动（仅 ready 或人工裁量）"},
                                status=400)
                return
            # v8.0.1：transition 统一入口（状态 + 目录搬移一致）
            moved = tstate.transition(tid, "active", "人工立项启动（工作台）")
            tdir = moved.get("dir") or tstate.topic_dir(tid)
            if tdir:
                append_card_event(Path(tdir) / "topic-card.md", f"→ active（人工立项启动，工作台）")
            self._send_json({"success": True, "id": tid, "stage": "active"})
        except Exception as e:  # noqa: BLE001
            self._send_json({"success": False, "error": str(e)}, status=500)

    def _topics_reject(self, parsed, body=None):
        """法定节点②：否决问题候选（进台账防重复立项）。"""
        tid = _topic_id_from_path(parsed)
        reason = (body or {}).get("reason", "")
        if not reason:
            self._send_json({"success": False, "error": "否决须填写 reason"}, status=400)
            return
        try:
            from topic_pipeline import state as tstate
            from pathlib import Path
            with tstate.state_lock():
                d = tstate.load_state()
                if not d.get("topics", {}).get(tid):
                    self._send_json({"success": False, "error": f"课题不存在: {tid}"}, status=404)
                    return
                tstate.reject_topic(d, tid, str(reason)[:300])
                tstate.save_state(d)
            # v8.0.1：任意阶段目录 → _rejected-questions/（不再假设 questions）
            tstate.move_to_rejected(tid)
            self._send_json({"success": True, "id": tid, "rejected": True})
        except Exception as e:  # noqa: BLE001
            self._send_json({"success": False, "error": str(e)}, status=500)

    def _topics_archive(self, parsed, body=None):
        """法定节点③：收尾归档（active → archive）。"""
        tid = _topic_id_from_path(parsed)
        try:
            from topic_pipeline import state as tstate
            from topic_pipeline.card import append_card_event
            from pathlib import Path
            data = tstate.load_state()
            rec = data.get("topics", {}).get(tid)
            if not rec:
                self._send_json({"success": False, "error": f"课题不存在: {tid}"}, status=404)
                return
            # v8.0.1：transition 统一入口（状态 + 目录搬移一致）
            moved = tstate.transition(tid, "archive", "收尾归档（人工，工作台）")
            if moved.get("dir"):
                append_card_event(Path(moved["dir"]) / "topic-card.md",
                                  f"{moved.get('from', '')} → archive（收尾归档，工作台）")
            self._send_json({"success": True, "id": tid, "stage": "archive"})
        except Exception as e:  # noqa: BLE001
            self._send_json({"success": False, "error": str(e)}, status=500)

    def _topics_check(self, parsed, body=None):
        """运行验收自检（全过自动晋级 ready）。"""
        tid = _topic_id_from_path(parsed)
        try:
            from topic_pipeline import acceptance
            res = acceptance.check_topic(tid)
            if not res.get("success"):
                self._send_json(res, status=404)
                return
            self._send_json(res)
        except Exception as e:  # noqa: BLE001
            self._send_json({"success": False, "error": str(e)}, status=500)

    def _topics_daily_run(self, parsed, body=None):
        """触发每日深研 worker（后台线程——hermes 深研耗时数分钟）。"""
        import threading
        from datetime import datetime, timezone

        if _daily_status.get("running"):
            self._send_json({"success": False, "error": "深研 worker 已在运行", "status": _daily_status},
                            status=409)
            return

        def _worker():
            try:
                from topic_pipeline.daily import run_daily
                _daily_status.update({
                    "running": True,
                    "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "result": None, "error": "",
                })
                res = run_daily()
                _daily_status["result"] = res
                _daily_status["running"] = False
            except Exception as e:  # noqa: BLE001
                _daily_status["running"] = False
                _daily_status["error"] = str(e)

        threading.Thread(target=_worker, daemon=True).start()
        self._send_json({"success": True, "message": "深研 worker 已后台启动（GET /api/topics/daily/status 查询）"})
