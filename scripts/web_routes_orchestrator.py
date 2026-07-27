#!/usr/bin/env python3
"""web_routes_orchestrator.py — 林赛总控路由 Mixin（v6.7）

提供 OrchestratorRoutesMixin，封装 4 大总控能力的 HTTP 路由（6 条）：
- GET  /api/orchestrator/dashboard          总仪表盘（4 区合一）
- GET  /api/orchestrator/profiles/health    7 个 profile 详细健康度
- GET  /api/orchestrator/failures/patterns  失败模式聚类 + 修正建议
- GET  /api/orchestrator/strategies         调度策略建议
- POST /api/orchestrator/strategies/apply   应用新策略（人工确认）
- GET  /api/orchestrator/pipeline/quality   Pipeline 状态机质量监控
- GET  /api/orchestrator/tuning-log         调优历史

设计原则：与 web_routes_pipeline.py 保持一致——独立分派器，正则预编译，
handler 签名 (self, path, parsed, match) 或 (self, path, parsed, body, match)。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import web_base
from web_base import _log

__all__ = ["OrchestratorRoutesMixin"]


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_ORCH_ROUTES_RAW = [
    # ---- GET ----
    ("GET", r"^/api/orchestrator/dashboard$", "_orch_get_dashboard"),
    ("GET", r"^/api/orchestrator/profiles/health$", "_orch_get_profiles_health"),
    ("GET", r"^/api/orchestrator/failures/patterns$", "_orch_get_failure_patterns"),
    ("GET", r"^/api/orchestrator/strategies$", "_orch_get_strategies"),
    ("GET", r"^/api/orchestrator/pipeline/quality$", "_orch_get_pipeline_quality"),
    ("GET", r"^/api/orchestrator/pipeline/quality/([^/]+)$", "_orch_get_pipeline_quality_one"),
    ("GET", r"^/api/orchestrator/tuning-log$", "_orch_get_tuning_log"),

    # ---- POST ----
    ("POST", r"^/api/orchestrator/strategies/apply$", "_orch_post_strategies_apply"),
]

# 预编译正则
_ORCH_ROUTES = [
    (method, re.compile(pattern), handler)
    for method, pattern, handler in _ORCH_ROUTES_RAW
]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class OrchestratorRoutesMixin:
    """林赛总控路由 Mixin（v6.7）。"""

    def _dispatch_orchestrator_routes(self, method: str, path: str, parsed, body=None) -> bool:
        """分派 orchestrator 路由。返回 True 表示已处理。"""
        for m, regex, handler in _ORCH_ROUTES:
            if m != method:
                continue
            match = regex.match(path)
            if match:
                if method in ("GET", "DELETE"):
                    return getattr(self, handler)(path, parsed, match)
                else:
                    return getattr(self, handler)(path, parsed, body, match)
        return False

    # -----------------------------------------------------------------
    # GET handlers
    # -----------------------------------------------------------------
    def _orch_get_dashboard(self, path, parsed, match):
        """GET /api/orchestrator/dashboard — 总仪表盘。"""
        try:
            from orchestrator import compute_dashboard
            window = int(parsed.get("window_hours", ["24"])[0]) if parsed.get("window_hours") else 24
            data = compute_dashboard(window_hours=window)
            return self._json_response(200, data)
        except Exception as e:
            return self._json_response(500, {"error": str(e)})

    def _orch_get_profiles_health(self, path, parsed, match):
        """GET /api/orchestrator/profiles/health — 7 个 profile 健康度。"""
        try:
            from profile_health import compute_profile_health
            window = int(parsed.get("window_hours", ["24"])[0]) if parsed.get("window_hours") else 24
            data = compute_profile_health(window_hours=window)
            return self._json_response(200, data)
        except Exception as e:
            return self._json_response(500, {"error": str(e)})

    def _orch_get_failure_patterns(self, path, parsed, match):
        """GET /api/orchestrator/failures/patterns — 失败模式聚类。"""
        try:
            from failure_analyzer import analyze_failures
            window = int(parsed.get("window_hours", ["24"])[0]) if parsed.get("window_hours") else 24
            data = analyze_failures(window_hours=window)
            return self._json_response(200, data)
        except Exception as e:
            return self._json_response(500, {"error": str(e)})

    def _orch_get_strategies(self, path, parsed, match):
        """GET /api/orchestrator/strategies — 调度策略建议。"""
        try:
            from strategy_optimizer import suggest_strategies
            window = int(parsed.get("window_hours", ["168"])[0]) if parsed.get("window_hours") else 168
            data = suggest_strategies(window_hours=window)
            return self._json_response(200, data)
        except Exception as e:
            return self._json_response(500, {"error": str(e)})

    def _orch_get_pipeline_quality(self, path, parsed, match):
        """GET /api/orchestrator/pipeline/quality — 所有 proposal 链路质量。"""
        try:
            from orchestrator import monitor_pipeline
            data = monitor_pipeline()
            return self._json_response(200, data)
        except Exception as e:
            return self._json_response(500, {"error": str(e)})

    def _orch_get_pipeline_quality_one(self, path, parsed, match):
        """GET /api/orchestrator/pipeline/quality/{proposal_id} — 单个 proposal 链路质量。"""
        try:
            from orchestrator import monitor_pipeline
            proposal_id = match.group(1)
            data = monitor_pipeline(proposal_id=proposal_id)
            return self._json_response(200, data)
        except Exception as e:
            return self._json_response(500, {"error": str(e)})

    def _orch_get_tuning_log(self, path, parsed, match):
        """GET /api/orchestrator/tuning-log — 调优历史。"""
        try:
            from paths import MEMORY_DIR
            from common import load_json
            log_path = MEMORY_DIR / "tuning-log.json"
            if not log_path.exists():
                return self._json_response(200, {"history": [], "count": 0})
            history = load_json(log_path)
            if not isinstance(history, list):
                history = []
            return self._json_response(200, {"history": history, "count": len(history)})
        except Exception as e:
            return self._json_response(500, {"error": str(e)})

    # -----------------------------------------------------------------
    # POST handlers
    # -----------------------------------------------------------------
    def _orch_post_strategies_apply(self, path, parsed, body, match):
        """POST /api/orchestrator/strategies/apply — 应用新策略（人工确认后）。"""
        try:
            if not isinstance(body, dict):
                return self._json_response(400, {"error": "请求体必须是 JSON 对象"})
            new_strats = body.get("strategies", {})
            confirmed_by = body.get("confirmed_by", "human")
            if not new_strats:
                return self._json_response(400, {"error": "缺少 strategies 字段"})
            from orchestrator import apply_strategies
            result = apply_strategies(new_strats, confirmed_by=confirmed_by)
            return self._json_response(200, result)
        except Exception as e:
            return self._json_response(500, {"error": str(e)})
