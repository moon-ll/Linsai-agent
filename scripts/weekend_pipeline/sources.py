#!/usr/bin/env python3
"""来源收集与去重。"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import file_sha256, load_json, now_utc
from paths import PROJECT_ROOT

from .constants import RELIABILITY_DERIVED, RELIABILITY_RELIABLE
from .state import is_source_processed, mark_source_processed

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


BRIEFING_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "reviews"
CAPTURES_DIR = PROJECT_ROOT / "knowledge" / "captures"
REFERENCES_NOTES_DIR = PROJECT_ROOT / "references" / "notes"
PAPER_POOL_PATH = PROJECT_ROOT / "memory" / "paper-pool.json"
RAW_PAPERS_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"


def _read_text(path: Path, max_chars: int = 8000) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except Exception:
        return ""


def _file_mtime_iso(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    except Exception:
        return ""


def _make_source_id(prefix: str, path: Path) -> str:
    return f"{prefix}:{path.relative_to(PROJECT_ROOT)}"


def collect_briefings(days: int = 7) -> List[Dict[str, Any]]:
    """收集最近 N 天的文献简报。"""
    cutoff = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)
    sources = []
    if not BRIEFING_DIR.exists():
        return sources
    for f in sorted(BRIEFING_DIR.glob("briefing-*.md"), reverse=True):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                continue
        except Exception:
            pass
        text = _read_text(f, 6000)
        if text:
            sources.append({
                "source_id": _make_source_id("briefing", f),
                "type": "briefing",
                "path": str(f.relative_to(PROJECT_ROOT)),
                "text": text,
                "mtime": _file_mtime_iso(f),
                "reliability": RELIABILITY_RELIABLE,
            })
    return sources


def collect_paper_pool(limit: int = 20) -> List[Dict[str, Any]]:
    """收集文献池中的新增论文。"""
    sources = []
    if not PAPER_POOL_PATH.exists():
        return sources
    pool = load_json(PAPER_POOL_PATH, default={})
    for arxiv_id, info in list(pool.get("papers", {}).items())[:limit]:
        text = f"{info.get('title', '')}\n\n{info.get('abstract', '')[:800]}"
        sources.append({
            "source_id": f"paper:{arxiv_id}",
            "type": "paper",
            "path": str(PAPER_POOL_PATH.relative_to(PROJECT_ROOT)),
            "arxiv_id": arxiv_id,
            "title": info.get("title", ""),
            "abstract": info.get("abstract", "")[:800],
            "tags": info.get("tags", []),
            "text": text,
            "reliability": RELIABILITY_RELIABLE,
        })
    return sources


def collect_captures(limit: int = 10) -> List[Dict[str, Any]]:
    """收集归档讨论。"""
    sources = []
    if not CAPTURES_DIR.exists():
        return sources
    for f in sorted(CAPTURES_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        text = _read_text(f, 3000)
        if text:
            sources.append({
                "source_id": _make_source_id("capture", f),
                "type": "capture",
                "path": str(f.relative_to(PROJECT_ROOT)),
                "text": text,
                "mtime": _file_mtime_iso(f),
                "reliability": RELIABILITY_RELIABLE,
            })
    return sources


def collect_reference_notes() -> List[Dict[str, Any]]:
    """收集用户参考笔记。"""
    sources = []
    if not REFERENCES_NOTES_DIR.exists():
        return sources
    for f in REFERENCES_NOTES_DIR.glob("*.md"):
        text = _read_text(f, 3000)
        if text:
            sources.append({
                "source_id": _make_source_id("reference", f),
                "type": "reference_note",
                "path": str(f.relative_to(PROJECT_ROOT)),
                "text": text,
                "mtime": _file_mtime_iso(f),
                "reliability": RELIABILITY_RELIABLE,
            })
    return sources


def collect_kb_concepts_and_methods(
    state: Optional[Dict[str, Any]] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """从 Knowledge Base 拉取现有 concepts/methods/papers。

    优先读取 reliable/derived 的 wiki 页面，避免重复处理已收录内容。
    """
    result: Dict[str, List[Dict[str, Any]]] = {
        "concepts": [],
        "methods": [],
        "papers": [],
    }
    try:
        import knowledge_base as kb
    except Exception:
        if _log:
            _log.warning("无法导入 knowledge_base，跳过 KB 来源收集")
        return result

    try:
        pages = kb.list_wiki_pages()
    except Exception as e:
        if _log:
            _log.warning(f"list_wiki_pages 失败: {e}")
        return result

    for page in pages:
        wiki_type = page.get("type", "")
        path = page.get("path", "")
        title = page.get("title", "")
        if wiki_type not in result:
            continue
        # 优先加载可靠/派生页面，unverified 跳过
        try:
            full = kb.get_wiki_page(path)
            fm = full.get("frontmatter", {}) if full else {}
            reliability = fm.get("source_reliability", RELIABILITY_DERIVED)
            if reliability == RELIABILITY_RELIABLE or reliability == RELIABILITY_DERIVED:
                body = (full.get("body", "") if full else "")[:1500]
                source = {
                    "source_id": f"kb:{wiki_type}:{path}",
                    "type": f"kb_{wiki_type}",
                    "path": path,
                    "title": title,
                    "text": body,
                    "reliability": reliability,
                }
                # 去重：若已处理过同样 hash 则跳过
                if state is None or not is_source_processed(source["source_id"], source["text"], state):
                    result[wiki_type].append(source)
        except Exception:
            continue

    return result


def collect_all_sources(
    state: Optional[Dict[str, Any]] = None,
    days: int = 7,
    paper_limit: int = 20,
    capture_limit: int = 10,
) -> Dict[str, Any]:
    """统一收集所有来源并返回结构化结果。"""
    sources: Dict[str, Any] = {
        "briefings": collect_briefings(days=days),
        "papers": collect_paper_pool(limit=paper_limit),
        "captures": collect_captures(limit=capture_limit),
        "reference_notes": collect_reference_notes(),
        "kb": collect_kb_concepts_and_methods(state=state),
        "collected_at": now_utc(),
    }

    # 标记新来源为已处理
    if state is not None:
        for key in ["briefings", "papers", "captures", "reference_notes"]:
            for s in sources.get(key, []):
                if not is_source_processed(s["source_id"], s["text"], state):
                    mark_source_processed(s["source_id"], s["text"], state)
        for wiki_type, items in sources.get("kb", {}).items():
            for s in items:
                if not is_source_processed(s["source_id"], s["text"], state):
                    mark_source_processed(s["source_id"], s["text"], state)

    return sources


def new_paper_sources(sources: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从已收集来源中过滤出尚未处理的新论文/简报。"""
    new_sources = []
    for s in sources.get("papers", []) + sources.get("briefings", []):
        if not is_source_processed(s["source_id"], s["text"], state):
            new_sources.append(s)
    return new_sources


def search_kb_for_query(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """在 KB 中检索与查询相关的页面。"""
    try:
        import knowledge_base as kb
    except Exception:
        return []

    try:
        results = kb.search(query, top_k=top_k, source="wiki")
    except Exception:
        return []

    enriched = []
    for r in results:
        try:
            page = kb.get_wiki_page(r.get("path", ""))
            if page:
                enriched.append({
                    "path": r.get("path", ""),
                    "title": r.get("title", ""),
                    "score": r.get("score", 0.0),
                    "body": page.get("body", "")[:1500],
                })
            else:
                enriched.append(r)
        except Exception:
            enriched.append(r)
    return enriched


def list_kb_paper_pages() -> List[Dict[str, Any]]:
    """列出 KB 中已有的 paper 类型页面。"""
    try:
        import knowledge_base as kb
    except Exception:
        return []

    try:
        return kb.list_wiki_pages(wiki_type="paper")
    except Exception:
        return []
