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
RAW_PAPERS_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"

# v6.8.13: Hermes workspace 文献来源路径
HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
HERMES_BRIEFINGS_DIR = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings"
HERMES_BRIEFINGS_PAPERS_DIR = HERMES_BRIEFINGS_DIR / "papers"


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


# v6.9.12: 源质量分层（聚类提炼的质量来源设计）
SOURCE_TIER_PAPER = 1       # 学术一手文献（raw papers + hermes papers）
SOURCE_TIER_BRIEFING = 2    # 每日精选简报（二手但已筛选）
SOURCE_TIER_CAPTURE = 3     # 讨论捕获（背景上下文）
SOURCE_TIER_NOTE = 3        # 手工笔记（背景上下文）


def distilled_paper_ids() -> set:
    """已提炼论文 id 集合（wiki/papers 页的 arxiv_id / 文件 stem）。

    v6.9.12: 知识已蒸馏成 wiki 页的 raw 论文不再作为聚类源。
    判据：knowledge/wiki/papers/*.md frontmatter 的 arxiv_id 字段
    或页文件名 stem。实测 wiki 页 326 个（含 arxiv_id 直标）。
    """
    ids: set = set()
    wiki_papers_dir = PROJECT_ROOT / "knowledge" / "wiki" / "papers"
    if not wiki_papers_dir.exists():
        return ids
    for f in wiki_papers_dir.glob("*.md"):
        ids.add(f.stem)
        try:
            head = f.read_text(encoding="utf-8")[:800]
            for line in head.split("\n"):
                if line.startswith("arxiv_id:"):
                    val = line.split(":", 1)[1].strip().strip('"\'')
                    if val:
                        ids.add(val)
                    break
        except Exception:
            continue
    return ids


def _make_source_id(prefix: str, path: Path) -> str:
    return f"{prefix}:{path.relative_to(PROJECT_ROOT)}"


def _backlog_exempt(sid: str, text: str, state: Optional[Dict[str, Any]]) -> bool:
    """v6.9.11: 补课豁免——来源从未被处理过时豁免时间窗口/数量上限。

    背景：v6.7.7-v6.9.10 的"收集即标记"缺陷给大量文献打上虚假的
    已处理标记（实际从未摘要）。修复删除标记后，这些积压文献的
    文件 mtime 已老化，会被 7 天窗口/mtime 前 N 上限挡在收集之外，
    "恢复未处理"也轮不到消费。待处理语义应由标记决定而非文件
    新鲜度：未处理的全收（补课），已处理的按原窗口过滤。
    """
    if state is None:
        return False
    return not is_source_processed(sid, text, state)


def collect_briefings(
    days: int = 7,
    state: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """收集最近 N 天的文献简报。

    v6.8.13: 三路读取——CoPilot wiki/reviews + hermes_briefings + hermes papers。
    v6.9.11: 窗口外文件若从未处理过（无标记）则豁免窗口收进（补课），
    已处理过的旧文件仍跳过。
    """
    cutoff = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)
    sources = []
    seen_ids = set()

    def _in_window_or_backlog(f: Path, sid: str, text: str) -> bool:
        """窗口内直接放行；窗口外仅放行未处理过的（补课）。"""
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        except Exception:
            return True
        if mtime >= cutoff:
            return True
        return _backlog_exempt(sid, text, state)

    # 路径 A：CoPilot wiki/reviews（同步后的简报）
    for f in sorted(BRIEFING_DIR.glob("briefing-*.md"), reverse=True):
        text = _read_text(f, 6000)
        if not text:
            continue
        sid = _make_source_id("briefing", f)
        if not _in_window_or_backlog(f, sid, text):
            continue
        seen_ids.add(sid)
        sources.append({
            "source_id": sid,
            "type": "briefing",
            "path": str(f.relative_to(PROJECT_ROOT)),
            "text": text,
            "mtime": _file_mtime_iso(f),
            "reliability": RELIABILITY_RELIABLE,
        })

    # 路径 B：hermes workspace briefings/research_briefing_*.md（每日精选简报）
    if HERMES_BRIEFINGS_DIR.exists():
        for f in sorted(HERMES_BRIEFINGS_DIR.glob("research_briefing_*.md"), reverse=True):
            text = _read_text(f, 6000)
            if not text:
                continue
            sid = f"hermes_briefing:{f.name}"
            if sid in seen_ids:
                continue
            if not _in_window_or_backlog(f, sid, text):
                continue
            seen_ids.add(sid)
            sources.append({
                "source_id": sid,
                "type": "briefing",
                "path": str(f),
                "text": text,
                "mtime": _file_mtime_iso(f),
                "reliability": RELIABILITY_RELIABLE,
            })

    return sources


def collect_paper_pool(
    limit: int = 20,
    state: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """收集文献池中的新增论文。

    v6.8.13: 从 knowledge/raw/papers/ 的 frontmatter 读取（取代空的 paper-pool.json）。
    v6.8.14: 同时从 hermes workspace papers/ 读取补充。
    v6.9.11: mtime 前 N 上限仅约束已处理论文；未处理过的（无标记）
    全量收进（补课）——旧实现按 mtime 倒序截断，池中较旧的一半
    待处理论文永远排不进前 N，恢复未处理标记后也轮不到摘要。
    """
    sources = []
    seen_ids = set()
    admitted_processed = 0  # 已处理论文的收纳计数（受 limit 约束）

    def _admit(f: Path) -> bool:
        """v6.9.11: 未处理的全收（补课）；已处理的最多 limit 条。"""
        nonlocal admitted_processed
        arxiv_id = f.stem
        sid = f"paper:{arxiv_id}"
        text_probe = _read_text(f, 2000)
        if _backlog_exempt(sid, text_probe, state):
            return True
        if admitted_processed >= limit:
            return False
        admitted_processed += 1
        return True

    # 路径 A：CoPilot knowledge/raw/papers/*.md（YAML frontmatter）
    if RAW_PAPERS_DIR.exists():
        for f in sorted(RAW_PAPERS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
            if not _admit(f):
                continue
            try:
                text = _read_text(f, 1500)
                # 提取 frontmatter 中的标题和摘要
                title = ""
                abstract = ""
                if text.startswith("---"):
                    end = text.find("---", 3)
                    if end > 0:
                        fm = text[3:end].strip()
                        for line in fm.split("\n"):
                            if line.startswith("title:"):
                                title = line.split(":", 1)[1].strip().strip('"\'')
                            elif line.startswith("abstract:"):
                                abstract = line.split(":", 1)[1].strip().strip('"\'')

                arxiv_id = f.stem
                sid = f"paper:{arxiv_id}"
                seen_ids.add(sid)
                body_text = f"{title}\n\n{abstract}" if abstract else text
                sources.append({
                    "source_id": sid,
                    "type": "paper",
                    "path": str(f.relative_to(PROJECT_ROOT)),
                    "arxiv_id": arxiv_id,
                    "title": title or arxiv_id,
                    "abstract": abstract[:800],
                    "text": body_text[:2000],
                    "reliability": RELIABILITY_RELIABLE,
                })
            except Exception:
                continue

    # 路径 B：hermes workspace papers/*.md（补充来源）
    if HERMES_BRIEFINGS_PAPERS_DIR.exists():
        for f in sorted(HERMES_BRIEFINGS_PAPERS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
            if not _admit(f):
                continue
            arxiv_id = f.stem
            sid = f"paper:{arxiv_id}"
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            text = _read_text(f, 2000)
            if text and len(text) > 100:
                sources.append({
                    "source_id": sid,
                    "type": "paper",
                    "path": str(f),
                    "arxiv_id": arxiv_id,
                    "title": arxiv_id,
                    "abstract": text[:800],
                    "text": text[:2000],
                    "reliability": RELIABILITY_DERIVED,
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
    """统一收集所有来源并返回结构化结果。

    v6.9.10: papers/briefings/captures/reference_notes 不再在收集时预标记
    为已处理。旧版"收集即标记"使 summarize 的 new_paper_sources 过滤恒为
    空——输入端自 v6.7.7 上线起从未真正摘要过新料，ideas 连续全零。
    标记职责归还消费方（summarize 摘要成功后才 mark，见 input_jobs）。
    kb 类来源保留标记：gap_analysis 依赖 processed_sources 中的
    kb:concept 记录作为知识库概念输入，且 collect_kb_concepts_and_methods
    靠它去重跳过已收录页面。

    v6.9.12 源甄别（聚类提炼的质量来源）：
    1. 已提炼排除——knowledge/wiki/papers/ 中已有同 arxiv_id 提炼页的
       raw 论文不再作为聚类源（其知识已升华进 wiki，重复聚类纯冗余；
       wiki 页可带 used_by_proposals 直接关联课题）。排除在 collect
       层完成，不消耗 summarize 的 LLM 名额。
    2. 质量分层 tier——paper=1（学术一手）/ briefing=2（二手精选）/
       capture=3 / note=3（讨论与手工笔记）。tier ≤2 进聚类主源
       （new_paper_sources 口径不变），tier=3 仅作 gap 上下文。
    """
    sources: Dict[str, Any] = {
        "briefings": collect_briefings(days=days, state=state),
        "papers": collect_paper_pool(limit=paper_limit, state=state),
        "captures": collect_captures(limit=capture_limit),
        "reference_notes": collect_reference_notes(),
        "kb": collect_kb_concepts_and_methods(state=state),
        "collected_at": now_utc(),
    }

    # v6.9.12: 已提炼排除 + tier 标注
    distilled = distilled_paper_ids()
    kept_papers = []
    excluded = 0
    for s in sources.get("papers", []):
        if s.get("source_id", "").split(":")[-1] in distilled:
            excluded += 1
            continue
        s["tier"] = SOURCE_TIER_PAPER
        kept_papers.append(s)
    sources["papers"] = kept_papers
    sources["distilled_excluded"] = excluded
    for s in sources.get("briefings", []):
        s["tier"] = SOURCE_TIER_BRIEFING
    for s in sources.get("captures", []):
        s["tier"] = SOURCE_TIER_CAPTURE
    for s in sources.get("reference_notes", []):
        s["tier"] = SOURCE_TIER_NOTE

    if state is not None:
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
