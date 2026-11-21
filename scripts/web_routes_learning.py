#!/usr/bin/env python3
"""web_routes_learning.py — 自主学习路由 Mixin。

提供 LearningRoutesMixin，封装学习引擎配置/状态/触发/审批 HTTP 路由：
    - GET  /api/learning/config   学习配置读取
    - GET  /api/learning/status   学习状态（成本/配额/策略）
    - GET  /api/learning/queue    待审队列
    - GET  /api/learning/log      学习质量日志
    - POST /api/learning/config   学习配置更新
    - POST /api/learning/trigger  手动触发学习周期
    - POST /api/learning/review   待审项审批（approve/reject）

路由表格式：(HTTP方法, re.compile(正则), handler名)
handler 签名：GET/DELETE → (self, parsed, body=None, **path_params)
             POST/PUT   → (self, parsed, body, **path_params)
仅使用 Python 标准库。
"""

import datetime
import json
import re

import web_base
from web_base import _log
from common import lazy_load
import common as _cms


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_LEARNING_ROUTES = [
    # GET
    ("GET", re.compile(r"^/api/learning/config$"), "_learn_config_get"),
    ("GET", re.compile(r"^/api/learning/status$"), "_learn_status"),
    ("GET", re.compile(r"^/api/learning/queue$"), "_learn_queue"),
    ("GET", re.compile(r"^/api/learning/log$"), "_learn_log"),
    # POST
    ("POST", re.compile(r"^/api/learning/config$"), "_learn_config_set"),
    ("POST", re.compile(r"^/api/learning/trigger$"), "_learn_trigger"),
    ("POST", re.compile(r"^/api/learning/review$"), "_learn_review"),
]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class LearningRoutesMixin:
    """自主学习路由 Mixin。"""

    def _learn_config_get(self, parsed, body=None):
        """学习配置读取"""
        config_path = web_base._PROJECT_ROOT / "memory" / "learning-config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json(data)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
        else:
            self._send_json({"enabled": True, "auto_review": True, "review_interval": 7})

    def _learn_status(self, parsed, body=None):
        """学习状态（成本/配额/策略）"""
        try:
            cost_data = {}
            cost_path = web_base._PROJECT_ROOT / "memory" / "learning-cost.json"
            if cost_path.exists():
                with open(cost_path, "r", encoding="utf-8") as f:
                    cost_data = json.load(f)
            config_path = web_base._PROJECT_ROOT / "memory" / "learning-config.json"
            config = {}
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            self._send_json({
                "enabled": config.get("auto_enabled", False),
                "strategy": config.get("strategy", "balanced"),
                "today_cost": cost_data.get("daily", {}).get(datetime.datetime.now().strftime("%Y-%m-%d"), 0),
                "month_cost": cost_data.get("monthly", {}).get(datetime.datetime.now().strftime("%Y-%m"), 0),
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

    def _learn_queue(self, parsed, body=None):
        """待审队列"""
        try:
            qe = lazy_load("quality_evaluator")
            if qe:
                queue = qe.get_pending_queue()
                self._send_json({"queue": queue})
            else:
                self._send_json({"queue": []})
        except Exception as e:
            self._send_json({"queue": [], "error": str(e)})

    def _learn_log(self, parsed, body=None):
        """学习质量日志"""
        try:
            log_path = web_base._PROJECT_ROOT / "memory" / "learning-quality-log.json"
            if log_path.exists():
                with open(log_path, "r", encoding="utf-8") as f:
                    log = json.load(f)
                self._send_json({"log": log})
            else:
                self._send_json({"log": []})
        except Exception as e:
            self._send_json({"log": [], "error": str(e)})

    def _learn_config_set(self, parsed, body):
        """学习配置更新"""
        config_path = web_base._PROJECT_ROOT / "memory" / "learning-config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            # 只允许更新白名单字段
            allowed_fields = ["auto_enabled", "daily_quota", "weekly_quota", "strategy",
                              "cost_limit_daily", "cost_limit_monthly", "sources", "adversarial_mode", "notify_web"]
            for field in allowed_fields:
                if field in body:
                    config[field] = body[field]
            _cms.save_json(config_path, config)
            self._send_json({"success": True, "config": config})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _learn_trigger(self, parsed, body):
        """手动触发学习周期"""
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

    def _learn_review(self, parsed, body):
        """待审项审批（approve/reject）"""
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
