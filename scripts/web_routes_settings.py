#!/usr/bin/env python3
"""web_routes_settings.py — 设置中心路由 Mixin（v6.7.7）。

提供统一的前端配置读写 API，覆盖：
- 链路配置（pipeline）
- 内容/模板配置（templates）
- Agent / Profile 配置（agents）
- 任务配置（tasks）
- 学习配置（learning）
- 自主级别配置（autonomy）
- 知识库/输出配置（kb_output）

设计原则：
- 所有配置继续使用现有 JSON 文件，不引入数据库。
- 写操作前自动备份旧文件到 memory/.settings-backup/。
- 每个 category 支持 GET 读取、POST 保存、POST /preview 预览差异。
- 保存失败时不覆盖原文件。

路由：
    GET  /api/settings/categories
    GET  /api/settings/:category
    POST /api/settings/:category
    POST /api/settings/:category/preview
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import web_base
from web_base import _log
from common import load_json, now_utc, save_json
from paths import PROJECT_ROOT


# ---------------------------------------------------------------------------
# 配置分类映射
# ---------------------------------------------------------------------------

SETTINGS_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "pipeline": {
        "label": "链路配置",
        "description": "达标分数、最大轮数、维度短板阈值、错峰间隔等",
        "files": {
            "pipeline": PROJECT_ROOT / "memory" / "pipeline-settings.json",
        },
        "defaults": {
            "max_rounds": 10,
            "score_threshold": 0.80,
            "no_improvement_limit": 3,
            "stagger_seconds": 90,
            "dimension_floor": {
                "innovation": 0.65,
                "feasibility": 0.65,
                "rigor": 0.65,
                "completeness": 0.60,
            },
        },
    },
    "templates": {
        "label": "内容/模板配置",
        "description": "NSFC 三类项目质量标准、撰写模板、方法学手册要求",
        "files": {
            "nsfc_standards": PROJECT_ROOT / "memory" / "nsfc-standards.json",
        },
    },
    "agents": {
        "label": "Agent / Profile 配置",
        "description": "各 profile 默认 Provider、超时、模型，以及路由策略",
        "files": {
            "llm_config": PROJECT_ROOT / "memory" / "llm-config.json",
        },
        "defaults": {
            "strategy": "priority",
            "timeout": 60,
            "retry": 1,
            "providers": [],
        },
    },
    "tasks": {
        "label": "任务配置",
        "description": "默认任务参数、hermes 自动派活开关",
        "files": {
            "tasks": PROJECT_ROOT / "memory" / "task-settings.json",
        },
        "defaults": {
            "default_assignee": "",
            "default_priority": "medium",
            "auto_dispatch_hermes": False,
        },
    },
    "learning": {
        "label": "学习配置",
        "description": "自主学习引擎参数、来源、配额",
        "files": {
            "learning_config": PROJECT_ROOT / "memory" / "learning-config.json",
        },
    },
    "autonomy": {
        "label": "自主级别配置",
        "description": "CoPilot 自主决策级别与提醒频率",
        "files": {
            "autonomy": PROJECT_ROOT / "memory" / "autonomy-level.json",
        },
    },
    "kb_output": {
        "label": "知识库 / 输出配置",
        "description": "可靠来源规则、derived 内容过期时间、归档萃取字段",
        "files": {
            "kb_output": PROJECT_ROOT / "memory" / "kb-output-settings.json",
        },
        "defaults": {
            "reliable_source_types": ["briefing", "paper", "user_input", "capture", "reference_note", "archived_proposal"],
            "derived_ttl_days": 30,
            "archive_extract_fields": ["title", "core_problem", "innovations", "key_artifacts"],
        },
    },
}


BACKUP_DIR = PROJECT_ROOT / "memory" / ".settings-backup"


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _ensure_backup_dir() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def _backup_file(path: Path) -> None:
    """备份文件到 .settings-backup/，文件名带时间戳。"""
    if not path.exists():
        return
    _ensure_backup_dir()
    ts = now_utc().replace(":", "-").replace("T", "_").rstrip("Z")
    backup_name = f"{path.stem}.{ts}{path.suffix}"
    shutil.copy2(path, BACKUP_DIR / backup_name)


def _load_category(category: str) -> Dict[str, Any]:
    """加载某个分类下的所有配置文件，合并返回。"""
    meta = SETTINGS_CATEGORIES.get(category)
    if not meta:
        raise ValueError(f"未知配置分类: {category}")

    result: Dict[str, Any] = {}
    # 先写入默认值（如果有）
    if "defaults" in meta:
        result.update(meta["defaults"])

    # 再覆盖已存在的文件内容
    for key, path in meta["files"].items():
        data = load_json(path, default={})
        if isinstance(data, dict):
            result.update(data)
        else:
            result[key] = data
    return result


def _save_category(category: str, data: Dict[str, Any]) -> None:
    """保存某个分类的配置到对应文件。

    当前每个分类只对应一个主文件，直接整体写入。
    如果未来一个分类对应多个文件，可在此拆分字段。
    """
    meta = SETTINGS_CATEGORIES.get(category)
    if not meta:
        raise ValueError(f"未知配置分类: {category}")

    files = meta["files"]
    if len(files) != 1:
        raise ValueError(f"分类 {category} 当前只支持单文件映射")

    path = list(files.values())[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    _backup_file(path)
    save_json(path, data)


def _compute_diff(old: Dict[str, Any], new: Dict[str, Any]) -> List[Dict[str, Any]]:
    """计算两个字典的一级差异，用于 preview。"""
    diff = []
    all_keys = set(old.keys()) | set(new.keys())
    for key in sorted(all_keys):
        if key.startswith("_"):
            continue
        ov = old.get(key)
        nv = new.get(key)
        if json.dumps(ov, sort_keys=True, ensure_ascii=False) != json.dumps(nv, sort_keys=True, ensure_ascii=False):
            diff.append({"key": key, "old": ov, "new": nv})
    return diff


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------

_SETTINGS_ROUTES_RAW = [
    ("GET", r"^/api/settings/categories$", "_stg_categories"),
    ("GET", r"^/api/settings/(?P<category>[^/]+)$", "_stg_get"),
    ("POST", r"^/api/settings/(?P<category>[^/]+)$", "_stg_post"),
    ("POST", r"^/api/settings/(?P<category>[^/]+)/preview$", "_stg_preview"),
]

_SETTINGS_ROUTES = [
    (method, re.compile(pattern), handler)
    for method, pattern, handler in _SETTINGS_ROUTES_RAW
]


class SettingsRoutesMixin:
    """设置中心路由 Mixin。

    路由由 web_server.py 的统一分派器 _try_route() 直接处理；
    本 Mixin 只提供 handler 方法，不提供独立分派器。
    """

    def _stg_categories(self, parsed, body=None):
        """GET /api/settings/categories — 列出所有配置分类。"""
        categories = []
        for key, meta in SETTINGS_CATEGORIES.items():
            categories.append({
                "key": key,
                "label": meta["label"],
                "description": meta.get("description", ""),
            })
        self._send_json({"status": "ok", "categories": categories})

    def _stg_get(self, parsed, body=None, **kwargs):
        """GET /api/settings/:category — 读取配置。"""
        category = kwargs.get("category")
        if category not in SETTINGS_CATEGORIES:
            self._send_json({"error": f"未知配置分类: {category}"}, 404)
            return
        try:
            data = _load_category(category)
            self._send_json({"status": "ok", "category": category, "data": data})
        except Exception as e:
            if _log:
                _log.error(f"读取设置 {category} 失败: {e}")
            self._send_json({"error": str(e)}, 500)

    def _stg_post(self, parsed, body=None, **kwargs):
        """POST /api/settings/:category — 保存配置。"""
        category = kwargs.get("category")
        if category not in SETTINGS_CATEGORIES:
            self._send_json({"error": f"未知配置分类: {category}"}, 404)
            return
        if not body or not isinstance(body, dict):
            self._send_json({"error": "请求体必须是 JSON 对象"}, 400)
            return

        try:
            _save_category(category, body)
            self._send_json({
                "status": "ok",
                "category": category,
                "saved_at": now_utc(),
            })
        except Exception as e:
            if _log:
                _log.error(f"保存设置 {category} 失败: {e}")
            self._send_json({"error": str(e)}, 500)

    def _stg_preview(self, parsed, body=None, **kwargs):
        """POST /api/settings/:category/preview — 预览变更差异。"""
        category = kwargs.get("category")
        if category not in SETTINGS_CATEGORIES:
            self._send_json({"error": f"未知配置分类: {category}"}, 404)
            return
        if not body or not isinstance(body, dict):
            self._send_json({"error": "请求体必须是 JSON 对象"}, 400)
            return

        try:
            old = _load_category(category)
            diff = _compute_diff(old, body)
            self._send_json({
                "status": "ok",
                "category": category,
                "diff": diff,
                "will_change": len(diff) > 0,
            })
        except Exception as e:
            if _log:
                _log.error(f"预览设置 {category} 失败: {e}")
            self._send_json({"error": str(e)}, 500)
