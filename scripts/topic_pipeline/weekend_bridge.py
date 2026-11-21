# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——周末输入链桥接适配器。

把 weekend_pipeline.input_jobs 的课题注册/融入/挂载三个落点适配到
research_topics 新域；`memory/config/workbench.json` 的
`weekend_register: "topics"|"legacy_proposals"` 控制新旧路径（默认 topics，
legacy 仅供回滚）。

用法示例：
    from topic_pipeline.weekend_bridge import register_from_idea_v8
    res = register_from_idea_v8(idea_dict)
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import load_json, save_json

from . import registration, state
from .card import append_card_event, render_card
from . import constants as _C

def _config_path():
    """配置路径（动态取 constants.PROJECT_ROOT，测试 root patch 可隔离）。"""
    return _C.PROJECT_ROOT / "memory" / "config" / "workbench.json"


def _cfg() -> Dict[str, Any]:
    return load_json(_config_path(), default={}) or {}


def weekend_register_mode() -> str:
    """周末链注册模式：topics（v8 默认）/ legacy_proposals（回滚用）。"""
    return str(_cfg().get("weekend_register") or "topics")


def _slug_from_cluster(cluster: Dict[str, Any]) -> str:
    kws = cluster.get("keywords") or []
    for kw in kws:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9]*", str(kw))
        if words:
            slug = "-".join(w.lower() for w in words)[:40].strip("-")
            if slug:
                return slug
    return registration.make_slug(cluster.get("title", ""))


def register_from_idea_v8(idea: Dict[str, Any]) -> Dict[str, Any]:
    """周末链 new 路由 → research_topics/questions/（返回 proposal_id 键以兼容 mark_linked）。"""
    cluster = idea.get("cluster_id", "")
    knowledge_card = f"来源簇 {cluster}：{idea.get('background', '')}\n\n空白点：{idea.get('gap', '')}"
    res = registration.register_question(
        title=str(idea.get("title", "")).strip(),
        problem=str(idea.get("gap", "") or idea.get("background", ""))[:400],
        source=f"weekend_cluster:{cluster}" if cluster else "weekend_input",
        slug=_slug_from_cluster({
            "title": idea.get("title", ""),
            "keywords": idea.get("keywords", []),
        }),
        knowledge_card=knowledge_card,
        related=[],
        force=False,
    )
    if res.get("registered"):
        res["proposal_id"] = res["topic_id"]
    return res


def enrich_from_idea_v8(topic_id: str, idea: Dict[str, Any]) -> Dict[str, Any]:
    """周末链 merge 路由 → 知识卡写入既有课题 01_background/。"""
    tdir_path = state.topic_dir(topic_id)
    if tdir_path is None:
        return {"success": False, "message": f"课题目录不存在: {topic_id}"}
    tdir = Path(tdir_path)
    bg = tdir / "01_background"
    bg.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    target = bg / f"knowledge-card-{date}.md"
    body = (
        f"# 知识卡注入（{date}，来源簇 {idea.get('cluster_id', '')}）\n\n"
        f"{idea.get('background', '')}\n\n"
        f"空白点：{idea.get('gap', '')}\n\n"
        f"信息源：\n" + "\n".join(f"- {s.get('title', '')}" for s in (idea.get("sources") or [])[:20])
    )
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    target.write_text(existing + ("\n\n" if existing else "") + body, encoding="utf-8")
    append_card_event(tdir / "topic-card.md", f"{state._now()} merge 知识卡注入（簇 {idea.get('cluster_id', '')}）")
    return {"success": True, "message": "知识卡已注入 01_background/", "topic_id": topic_id,
            "proposal_id": topic_id}


def write_supplementary_sources_v8(topic_id: str, cluster: Dict[str, Any],
                                   summary_index: Dict[str, Dict[str, Any]]) -> bool:
    """周末链 merge_follower/expansion 路由 → 补充信息源挂载（01_background/）。"""
    tdir_path = state.topic_dir(topic_id)
    if tdir_path is None:
        return False
    bg = Path(tdir_path) / "01_background"
    bg.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    entries: List[Dict[str, Any]] = []
    for ms in cluster.get("member_summaries", []) or []:
        sid = ms.get("source_id", "")
        s = summary_index.get(sid) or ms
        entries.append({
            "source_id": sid,
            "title": s.get("title", sid),
            "summary": (s.get("summary", "") or "")[:800],
            "path": s.get("path", ""),
        })
    if not entries:
        return False
    out = bg / f"supplementary-sources-{date}.json"
    existing = load_json(out, default={"entries": []}) or {"entries": []}
    seen = {e.get("source_id") for e in existing.get("entries", [])}
    for e in entries:
        if e["source_id"] not in seen:
            existing.setdefault("entries", []).append(e)
    existing["updated_at"] = state._now()
    save_json(out, existing)
    return True


def all_topics_and_legacy() -> List[Dict[str, Any]]:
    """topic_match 数据源：v8 全阶段课题 + v7 遗留课题（迁移过渡期对照）。"""
    out: List[Dict[str, Any]] = []
    for t in state.all_topics_for_match():
        out.append({
            "proposal_id": t["id"],
            "title": t["title"],
            "status": t["stage"] or "unknown",
            "text": t["text"],
        })
    try:
        from proposal_lifecycle import ProposalLifecycle  # legacy 只读对照
        lc = ProposalLifecycle()
        for status in ("drafts", "optimizing", "pending_review", "archived"):
            for p in lc.list_by_status(status):
                if any(x["proposal_id"] == p["proposal_id"] for x in out):
                    continue
                # text 口径与 v7 _load_all_stage_proposals 一致：brief 全文（2000 字截断）
                # 只有标题会让 Jaccard 预筛相似度失真（merge/expansion 误判 defer）
                brief_text = ""
                prop_dir = lc._find_proposal_dir(p["proposal_id"])
                if prop_dir:
                    for f in sorted(Path(prop_dir).glob("00_*.md")):
                        try:
                            brief_text = f.read_text(encoding="utf-8")[:2000]
                        except Exception:
                            brief_text = ""
                        break
                out.append({
                    "proposal_id": p["proposal_id"],
                    "title": p.get("title", p["proposal_id"]),
                    "status": status,
                    "text": brief_text or p.get("title", ""),
                })
    except Exception:
        pass
    return out
