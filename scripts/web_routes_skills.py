#!/usr/bin/env python3
"""web_routes_skills.py — 技能路由 Mixin。

提供 SkillRoutesMixin，封装技能系统查询与配置 HTTP 路由：
    - GET  /api/skills          技能列表
    - GET  /api/skills/active   活跃技能（含模糊查询 ?q=）
    - GET  /api/skills/config   技能配置
    - GET  /api/skills/search   技能搜索 ?q=
    - POST /api/skills/config   更新技能配置

路由表格式：(HTTP方法, re.compile(正则), handler名)
handler 签名：GET/DELETE → (self, parsed, body=None, **path_params)
             POST/PUT   → (self, parsed, body, **path_params)
仅使用 Python 标准库。
"""

import re
from urllib.parse import parse_qs

from web_base import _log  # noqa: F401  (保持与其它路由模块导入风格一致)

import skill_manager as skm


# ---------------------------------------------------------------------------
# 路由表
# ---------------------------------------------------------------------------
_SKILL_ROUTES = [
    # GET
    ("GET", re.compile(r"^/api/skills$"), "_skill_list"),
    ("GET", re.compile(r"^/api/skills/active$"), "_skill_active"),
    ("GET", re.compile(r"^/api/skills/config$"), "_skill_config_get"),
    ("GET", re.compile(r"^/api/skills/search$"), "_skill_search"),
    # POST
    ("POST", re.compile(r"^/api/skills/config$"), "_skill_config_set"),
]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
def _pipeline_skills() -> list:
    """v7.0.4: 管线技能（.hermes/skills/）只读展示条目。

    管线 skill 是 CoPilot/hermes 管线的方法学真相源（skill_loader 消费），
    不参与会话技能的激活/匹配，故只在列表观测层透出，配置操作仍限
    会话技能。fail-open：目录缺失返回空。
    """
    try:
        from skill_loader import SKILLS_ROOT, load_skill
        out = []
        for d in sorted(SKILLS_ROOT.iterdir()) if SKILLS_ROOT.exists() else []:
            if not d.is_dir():
                continue
            text = load_skill(d.name)
            # frontmatter 的 description 行作为摘要
            desc = ""
            for line in text.split("\n")[:20]:
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip().strip('"\'')
                    break
            out.append({
                "name": d.name,
                "type": "pipeline",
                "source": "hermes_trusted",
                "path": str(d / "SKILL.md"),
                "triggers": "",
                "summary": desc[:120],
            })
        return out
    except Exception:
        return []


class SkillRoutesMixin:
    """技能路由 Mixin。"""

    def _skill_list(self, parsed, body=None):
        """技能列表（会话技能 + 管线技能观测条目）"""
        self._send_json({"skills": skm.list_skills() + _pipeline_skills()})

    def _skill_active(self, parsed, body=None):
        """活跃技能（含模糊查询；all 含管线技能观测条目）"""
        query = parse_qs(parsed.query).get("q", [""])[0]
        self._send_json({
            "active": skm.get_active_skill_names(query),
            "all": skm.list_skills() + _pipeline_skills(),
        })

    def _skill_config_get(self, parsed, body=None):
        """技能配置"""
        self._send_json(skm.get_skill_config())

    def _skill_search(self, parsed, body=None):
        """技能搜索"""
        query = parse_qs(parsed.query).get("q", [""])[0]
        self._send_json({"query": query, "results": skm.search_skills(query)})

    def _skill_config_set(self, parsed, body):
        """更新技能配置"""
        mode = body.get("mode", "auto")
        active = body.get("active_skills", [])
        try:
            result = skm.set_skill_config(mode, active)
            self._send_json({"success": True, "config": result})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)
