# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——问题候选注册（questions/ 入口）。

注册三件事：ID 命名（沿用 v6.5.4 约定）、A2 新颖性硬门（零 LLM 2-gram
Jaccard，与全阶段既有课题 + 否决台账对照）、课题卡落盘 + 状态登记。

用法示例：
    python3 scripts/topic_pipeline.py --register \\
        --title "莫尔超晶格中的轨道磁性探测" \\
        --problem "转角双层 MoS2 的平带载流子能否产生可测的轨道磁矩响应" \\
        --source "manual" --slug "moire-orbital-magnetism"
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import similarity, state
from .card import append_card_event, render_card
from . import constants as _C
from .constants import A2_NOVELTY_THRESHOLD, SCOPE_SHORT, STAGES

_ID_PATTERN = re.compile(r"^(general|key|major)-([a-z][a-z0-9-]{1,40})-(\d{4})(\d{2})(\d{2})(?:-(\d{2}))?$")


def make_slug(text: str, max_len: int = 40) -> str:
    """从标题提取 latin slug（小写字母开头，连字符连接）。

    中文标题无 latin 词时回退 "topic"——调用方（周末链/LLM）可显式传 slug。
    """
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9]*", text or "")
    slug = "-".join(w.lower() for w in words)[:max_len].strip("-")
    return slug or "topic"


def _validate_id(topic_id: str) -> Optional[str]:
    m = _ID_PATTERN.match(topic_id or "")
    if not m:
        return f"课题 ID 不符合命名规则 {{general|key|major}}-{{slug}}-{{YYYYMMDD}}: {topic_id}"
    if len(m.group(2)) < 2:
        return "课题名称部分过短（≥2 字符）"
    return ""


def novelty_report(problem_text: str, extra_texts: Optional[List[str]] = None) -> Dict[str, Any]:
    """与全阶段既有课题 + 否决台账做相似度对照。

    Returns:
        {max_score, threshold, competitor, competitors(前3), passed}
    """
    texts: List[str] = [t.get("text", "") for t in state.all_topics_for_match()]
    st = state.load_state()
    texts += [r.get("title", "") for r in st.get("rejected", {}).values()]
    if extra_texts:
        texts += list(extra_texts)
    best = 0.0
    competitor = ""
    scores: List[Dict[str, Any]] = []
    for other in texts:
        if not other.strip():
            continue
        s = similarity.jaccard_similarity(problem_text, [other])
        scores.append({"text": other[:60], "score": s})
        if s > best:
            best, competitor = s, other[:60]
    scores.sort(key=lambda x: -x["score"])
    return {
        "max_score": best,
        "threshold": A2_NOVELTY_THRESHOLD,
        "competitor": competitor,
        "competitors": scores[:3],
        "passed": best < A2_NOVELTY_THRESHOLD,
    }


def register_question(
    title: str,
    problem: str = "",
    source: str = "manual",
    slug: str = "",
    knowledge_card: str = "",
    related: Optional[List[str]] = None,
    force: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """注册问题候选到 questions/（A2 新颖性硬门）。

    Returns:
        {registered, topic_id, dir, novelty, reason}
    """
    title = (title or "").strip()
    if not title:
        return {"registered": False, "reason": "标题为空"}
    problem_text = f"{title} {problem or ''}".strip()
    nov = novelty_report(problem_text)
    if not nov["passed"] and not force:
        return {
            "registered": False,
            "reason": f"新颖性不过：与既有课题相似度 {nov['max_score']} ≥ {A2_NOVELTY_THRESHOLD}（competitor: {nov['competitor']}）",
            "novelty": nov,
        }

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    base_slug = make_slug(slug or title)
    base_id = f"general-{base_slug}-{today}"
    topic_id = base_id
    seq = 2
    with state.state_lock():
        data = state.load_state()
        while topic_id in data.get("topics", {}) or topic_id in data.get("rejected", {}):
            topic_id = f"{base_id}-{seq:02d}"
            seq += 1
        if dry_run:
            return {"registered": False, "dry_run": True, "topic_id": topic_id,
                    "reason": "dry-run 预览，未落盘", "novelty": nov}
        tdir = _C.TOPICS_ROOT / "questions" / topic_id
        tdir.mkdir(parents=True, exist_ok=True)
        card = render_card(
            title=title, topic_id=topic_id, stage="questions",
            problem=problem, source=source, related=related,
            knowledge_card=knowledge_card,
        )
        (tdir / "topic-card.md").write_text(card, encoding="utf-8")
        append_card_event(tdir / "topic-card.md",
                          f"{state._now()} 注册（questions，来源 {source}，新颖性 {nov['max_score']}）")
        rec = state.upsert_topic(data, topic_id, {
            "title": title, "stage": "questions", "source": source,
            "problem": problem, "related": related or [],
        })
        rec["stage_history"] = [{"stage": "questions", "at": state._now(), "note": f"注册（{source}）"}]
        rec["novelty"] = {k: nov[k] for k in ("max_score", "competitor")}
        state.save_state(data)
    return {"registered": True, "topic_id": topic_id, "dir": str(tdir), "novelty": nov}
