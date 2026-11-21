#!/usr/bin/env python3
"""统一文献服务层 — 检索/阅读/入库/状态的唯一入口。

用途：
    作为文献检索、深度阅读、入库、状态查询的枢纽层。
    每日简报（linsai cron）和全链路（researcher）都通过此服务操作，
    确保去重逻辑统一、入库路径统一、状态追踪统一。

用法示例：
    >>> from literature_service import LiteratureService
    >>> svc = LiteratureService()
    >>> new_papers = svc.search(
    ...     keywords=["固体HHG", "Berry曲率"],
    ...     source="briefing",
    ...     depth="standard",
    ... )
    >>> ctx = svc.get_context(
    ...     gap_keywords=["量子几何"],
    ...     proposal_id="general-quantum-geometry-20260726",
    ... )
    >>> note = svc.read(
    ...     arxiv_id="2403.15337",
    ...     proposal_id="general-quantum-geometry-20260726",
    ... )

规范：仅标准库，PROJECT_ROOT 推导，JSON ensure_ascii=False。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from common import now_utc, load_json, save_json, file_lock
from paths import PROJECT_ROOT, KNOWLEDGE_DIR, RAW_DIR, WIKI_DIR, QA_DIR, HERMES_BRIEFING_PAPERS_DIR, HERMES_BRIEFINGS_DIR

try:
    from logger import get_logger
    _log = get_logger("literature_service")
except Exception:
    _log = None


# ─────────────────────────────────────────────
# 常量
# ─────────────────────────────────────────────

RAW_PAPERS_DIR = RAW_DIR / "papers"
WIKI_PAPERS_DIR = WIKI_DIR / "papers"
QA_PAPER_DIR = QA_DIR / "paper-discussions"

# 搜索深度对应的论文数量
DEPTH_LIMITS = {"quick": 3, "standard": 8, "deep": 15}

# read_status 值域
READ_STATUS_UNREAD = "unread"
READ_STATUS_SKIMMED = "skimmed"
READ_STATUS_DEEP_READ = "deep-read"
VALID_READ_STATUSES = {READ_STATUS_UNREAD, READ_STATUS_SKIMMED, READ_STATUS_DEEP_READ}

# 来源类型
SOURCE_BRIEFING = "briefing"
SOURCE_PIPELINE = "pipeline"


def _normalize_citations(raw: Any) -> Dict[str, Any]:
    """把 proposals_citations 归一为 dict。

    v7.3.6 修复：kb_text.build_frontmatter 对 dict 值走 else 分支做 str()
    序列化，proposals_citations 因此被写成 "{'pid': ['adversarial-review']}"
    字符串；parse_frontmatter 不反解 dict 字符串 → 取回仍是 str。消费方若直接
    .get() 会抛 AttributeError。此处做形态归一：

    - dict → 原样返回
    - str → ast.literal_eval 还原为 dict；解析失败返回空 dict
    - list / None / 其它 → 空 dict

    Args:
        raw: frontmatter 中 proposals_citations 的原始值
    Returns:
        规范化后的 dict
    """
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, str):
        try:
            import ast
            parsed = ast.literal_eval(raw)
        except Exception:
            return {}
        if isinstance(parsed, dict):
            return parsed
    return {}


def _wiki_paper_candidates(arxiv_id: str) -> List[Path]:
    """列出 wiki/papers/ 下同一篇论文的所有命名代候选路径。

    v7.3.12（BUG-38）修复：`wiki/papers/` 存在多代命名并存的历史事实——
      - 裸 id 代：  `2407.15253.md`
      - 下划线 slug 代：`2024-2407_15253-<slug>.md`（id 中的 `.` 被
        `safe_filename` 换成 `_`，是采集侧 `_safe_filename` 的产物）
      - 点号 slug 代：`2024-2407.15253-<slug>.md`（少数未替换变体）
      - 裸 id+slug 代：`2407.15253-<slug>.md`
    旧实现只认裸 id 代（`WIKI_PAPERS_DIR / f"{arxiv_id}.md"`），
    下划线 slug 代的论文一律判「页面不存在」→ link_to_proposal 静默
    返回 False，used_by_proposals / proposals_citations 永不落盘。

    实测生产证据：11-04 02:46 houston r2 lit_note 批量关联时，34 篇中
    5 篇（如 2503.02469 / 2402.15375 / 2411.06509 / 2503.14360 /
    1502.07183）在 KB 中确实存在（仅下划线 slug 代），却全部报
    「论文 wiki 页面不存在」。全库口径：wiki 下划线 slug 代 1805 篇，
    其中 989 篇无裸 id 对应页 → 全部不可达。

    顺序约定：裸 id 代优先（它是 link_to_proposal 的写回目标），
    其余按 slug 代补充；调用方须自行决定是否回退写入。

    v7.3.13（BUG-39）补第五代命名：**id 被完全去点**的 slug 代
    （`2024-240703189-<slug>.md`，即 `2407.03189` → `240703189`）。
    该形态由采集侧把 id 的 `.` 整体删除（而非替换为 `_`）产生，
    v7.3.12 的 4 个 pattern 全部匹配不到 → 这 59 篇论文对
    `literature_service` 依旧不可达。实测：59 篇中 25 篇无裸 id
    对应页（即无法靠"回退裸 id"救回），其中 14 篇是真实主内容页。

    v7.3.14（BUG-41）补第六代命名：**题名以 `[id] ` 开头**的 slug 代
    （`2609_38727__Metaphotonics_for_HHG.md`）。该形态由周末输出端
    萃取简报里的 `- [2609.38727] Metaphotonics for HHG` 条目产生——
    `common.safe_filename` 会把 `[]`、`.`、空格统一替成 `_`（并
    `strip` 掉首尾 `_`），于是 id 与题名之间留下 `__`。前 5 个 pattern
    全部匹配不到 → 这 12 篇论文对 `literature_service` 依旧不可达，
    关联关系永不落盘、read() 缓存判定读不到 read_status → 已深读
    误判未读、重复派发深度阅读。实测：12 篇全部带 `[NNNN.NNNNN]`
    题名前缀，且 12 篇在 KB 中均另有裸 id 代或 slug 代主页。

    顺序约定：裸 id 代优先（它是 link_to_proposal 的写回目标），
    其余按 slug 代补充；调用方须自行决定是否回退写入。

    Args:
        arxiv_id: 规范 arXiv id（如 "2407.15253"）
    Returns: 候选路径列表（存在的优先，裸 id 代排首位）
    """
    base = WIKI_PAPERS_DIR
    if not base.exists():
        return []
    ident = arxiv_id.replace(".", "_")
    ident_flat = arxiv_id.replace(".", "")
    patterns = [
        f"{arxiv_id}.md",          # 裸 id 代
        f"*-{ident}-*.md",         # 下划线 slug 代
        f"*-{arxiv_id}-*.md",      # 点号 slug 代 / 裸 id+slug 代
        f"{arxiv_id}-*.md",        # 裸 id 前缀 + slug（无年份段）
        f"*-{ident_flat}-*.md",    # 去点 slug 代（v7.3.13 / BUG-39）
        f"{ident}__*.md",          # 题名以 [id] 开头的 slug 代（v7.3.14 / BUG-41）
    ]
    found: List[Path] = []
    seen = set()
    for pat in patterns:
        for p in sorted(base.glob(pat)):
            if p in seen:
                continue
            seen.add(p)
            found.append(p)
    return found


class LiteratureService:
    """统一文献服务。所有检索/阅读/入库操作通过此类。"""

    def __init__(self) -> None:
        """初始化文献服务。"""
        # 延迟导入，避免循环依赖
        self._kb = None
        self._kb_wiki = None
        self._state_sync = None
        self._kb_importer = None

    # ─────────────────────────────────────────────
    # 内部依赖初始化
    # ─────────────────────────────────────────────

    def _ensure_imports(self) -> None:
        """延迟导入依赖模块。"""
        if self._kb is not None:
            return
        import sys
        if str(PROJECT_ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

        import knowledge_base as kb
        self._kb = kb

        from kb_wiki import save_wiki_page, get_wiki_page, build_wiki_page
        self._kw_save = save_wiki_page
        self._kw_get = get_wiki_page
        self._kw_build = build_wiki_page

        import state_sync as ss
        self._state_sync = ss

        import kb_importer as ki
        self._kb_importer = ki

    @property
    def kb(self):
        self._ensure_imports()
        return self._kb

    @property
    def state_sync(self):
        self._ensure_imports()
        return self._state_sync

    @property
    def kb_importer(self):
        self._ensure_imports()
        return self._kb_importer

    @property
    def kw_save(self):
        self._ensure_imports()
        return self._kw_save

    @property
    def kw_get(self):
        self._ensure_imports()
        return self._kw_get

    @property
    def kw_build(self):
        self._ensure_imports()
        return self._kw_build

    # ─────────────────────────────────────────────
    # 核心方法
    # ─────────────────────────────────────────────

    def search(
        self,
        keywords: List[str],
        source: str = SOURCE_BRIEFING,
        proposal_id: Optional[str] = None,
        depth: str = "standard",
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """统一检索入口。

        1. 调用 state_sync.get_processed_ids() 获取已处理论文 ID
        2. 调用 KB raw/papers 已有 arxiv_id 列表
        3. 合并去重，将 exclude_ids 注入 researcher prompt
        4. 委托 hermes researcher profile 联网检索（或委托简报 cron）
        5. 新论文通过 knowledge_base.ingest_raw() 入库
        6. 若 proposal_id 不为 None，标记 used_by_proposals
        7. 返回结构化论文列表

        Args:
            keywords: 检索关键词列表
            source: "briefing"（每日简报）或 "pipeline"（全链路）
            proposal_id: 关联课题 ID（source="pipeline" 时必填）
            depth: "quick"(3篇) / "standard"(8篇) / "deep"(15篇)
            max_results: 最大返回数
        Returns:
            论文列表，每条含 arxiv_id/title/authors/direction/score/
            tldr/is_new/has_local_pdf/read_status
        """
        # 1+2. 获取已处理论文 ID 和本地已有论文
        processed_ids = self._get_exclude_ids(proposal_id)
        local_papers = self._scan_local_raw_papers()
        local_ids = set(local_papers.keys())

        # v6.8.14 WP4: KB-first 本地预检索——先查知识库，命中 ≥60% 直接返回
        kb_results = self._search_kb_papers(keywords, max_results=max_results or DEPTH_LIMITS.get(depth, 8))
        kb_limit = (max_results or DEPTH_LIMITS.get(depth, 8))
        if len(kb_results) >= kb_limit * 0.6:
            if _log:
                _log.info(f"[LiteratureService] KB-first 命中 {len(kb_results)}/{kb_limit}，直接返回本地结果")
            # 标记 used_by_proposals
            if proposal_id:
                for paper in kb_results:
                    arxiv_id = paper.get("arxiv_id", "")
                    if arxiv_id:
                        self._mark_used_by_proposal(arxiv_id, proposal_id)
            return kb_results[:kb_limit]

        if _log:
            _log.info(
                f"[LiteratureService] search source={source} depth={depth} "
                f"keywords={keywords} exclude={len(processed_ids | local_ids)} 篇 "
                f"KB-only={len(kb_results)}（不足 {int(kb_limit * 0.6)}，fallback 在线检索）"
            )

        # 3. 构建检索 prompt（注入 exclude_ids）
        exclude_prompt = ""
        if processed_ids or local_ids:
            all_exclude = processed_ids | local_ids
            exclude_prompt = (
                f"\n\n【请跳过以下已处理论文（共 {len(all_exclude)} 篇）】\n"
                + "\n".join(sorted(str(x) for x in all_exclude))
            )

        # 4. 委托 hermes 联网检索
        limit = max_results or DEPTH_LIMITS.get(depth, 8)
        prompt = self._build_search_prompt(keywords, source, depth, limit, exclude_prompt)
        results = self._dispatch_researcher(prompt, source)

        # 5. 新论文入库
        new_papers = []
        existing_papers = []
        for paper in results:
            arxiv_id = self._extract_arxiv_id(paper)
            if arxiv_id in local_ids:
                paper["is_new"] = False
                paper["has_local_pdf"] = local_papers.get(arxiv_id, {}).get("has_pdf", False)
                paper["read_status"] = local_papers.get(arxiv_id, {}).get("read_status", "unread")
                existing_papers.append(paper)
            else:
                paper["is_new"] = True
                paper["read_status"] = "unread"
                new_papers.append(paper)

        # 5. 新论文入库 KB
        if new_papers and source == SOURCE_BRIEFING:
            # 简报模式：通过 kb_importer 入库
            self._ingest_new_papers(new_papers, source, proposal_id)
        elif new_papers and source == SOURCE_PIPELINE:
            # 全链路模式：通过 kb_importer.import_candidate() 入库
            self._ingest_new_papers(new_papers, source, proposal_id)

        # v6.8.51: 入库后即时重建索引，新论文立即可被检索
        # （此前索引仅靠手动/周维护重建，新文献存在最长数日检索盲区；
        #   v2 全量重建 1012 文档约 2s，挂在此处代价可接受）
        if new_papers:
            try:
                if self.kb and hasattr(self.kb, "build_index"):
                    self.kb.build_index()
            except Exception as e:
                if _log:
                    _log.warning(f"[LiteratureService] 入库后重建索引失败（不影响入库结果）: {e}")

        # 6. 若有关联课题，标记 used_by_proposals
        if proposal_id:
            for paper in existing_papers + new_papers:
                arxiv_id = self._extract_arxiv_id(paper)
                if arxiv_id:
                    self._mark_used_by_proposal(arxiv_id, proposal_id)

        # 7. 合并返回
        all_papers = new_papers + existing_papers
        return all_papers[:limit]

    def read(
        self,
        arxiv_id: str,
        proposal_id: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """统一深度阅读入口。

        1. 检查 knowledge/wiki/papers/{arxiv_id}.md 是否已有阅读笔记
        2. 已有且 read_status="deep-read" 且非 force → 直接返回
        3. 未有 → 调用 hermes researcher 深度阅读
        4. 通过 kb_wiki.save_wiki_page() 写入 wiki/papers/
        5. 更新 frontmatter: read_status, used_by_proposals
        6. 返回阅读笔记内容

        Args:
            arxiv_id: 论文 arXiv ID
            proposal_id: 关联课题 ID
            force: 强制重新阅读
        Returns:
            {"arxiv_id": ..., "read_status": ...,
             "note_path": ..., "content": ...}
        """
        if _log:
            _log.info(f"[LiteratureService] read arxiv_id={arxiv_id} proposal_id={proposal_id} force={force}")

        wiki_path = WIKI_PAPERS_DIR / f"{arxiv_id}.md"

        # 1. 检查是否已有阅读笔记
        existing_note = self._get_wiki_paper_note(arxiv_id)

        # 2. 缓存命中
        if existing_note and not force:
            # v7.3.6 修复：read_status / 正文位于 frontmatter / body 键内，
            # 原实现取顶层键恒为默认值 → 已深读论文被误判为未读并重复派发深度阅读。
            _note_fm = existing_note.get("frontmatter", {}) or {}
            read_status = _note_fm.get("read_status", "unread")
            if read_status == READ_STATUS_DEEP_READ:
                # 追加 proposal_id 到 used_by_proposals
                if proposal_id:
                    self._mark_used_by_proposal(arxiv_id, proposal_id)
                    # v7.3.12（BUG-38）：缓存命中页可能位于 slug 代命名下 →
                    # 关联信息须回写到该页，否则 used_by_proposals 永不落盘。
                    actual = WIKI_PAPERS_DIR / f"{arxiv_id}.md"
                    if not actual.exists():
                        candidates = _wiki_paper_candidates(arxiv_id)
                        if candidates:
                            self._link_to_existing_page(
                                candidates[0], arxiv_id, proposal_id
                            )
                return {
                    "arxiv_id": arxiv_id,
                    "read_status": read_status,
                    "note_path": str(wiki_path),
                    "content": existing_note.get("body", ""),
                    "cached": True,
                }

        # v6.8.1: 优先使用 hermes 深度分析 JSON（已有 5 维结构化数据）
        note_content = self._build_note_from_hermes_analysis(arxiv_id)
        if not note_content:
            # 3. 调用 hermes researcher 深度阅读
            note_content = self._dispatch_deep_read(arxiv_id)

        # 4. 通过 kb_wiki.save_wiki_page() 写入 wiki/papers/
        if note_content:
            self._save_wiki_paper_note(arxiv_id, note_content, proposal_id)

        # 5. 更新 raw/papers/ frontmatter 的 read_status
        self._update_read_status(arxiv_id, READ_STATUS_DEEP_READ, proposal_id)

        return {
            "arxiv_id": arxiv_id,
            "read_status": READ_STATUS_DEEP_READ,
            "note_path": str(wiki_path),
            "content": note_content,
            "cached": False,
        }

    def get_context(
        self,
        gap_keywords: List[str],
        proposal_id: Optional[str] = None,
    ) -> str:
        """构建文献上下文（替代 _build_kb_context_from_gap）。

        三层预检索（全部走 KB 门面）：
        1. knowledge/raw/papers/ — 关键词匹配 frontmatter
        2. knowledge/wiki/papers/ — 匹配阅读笔记内容
        3. knowledge_base.search() — wiki 概念/方法检索
        命中条目标注 has_pdf、read_status、used_by_proposals。

        Args:
            gap_keywords: 缺口分析产出的关键词
            proposal_id: 当前课题 ID
        Returns:
            结构化文本，注入 researcher prompt
        """
        if _log:
            _log.info(f"[LiteratureService] get_context keywords={gap_keywords} proposal_id={proposal_id}")

        # 1. raw/papers/ frontmatter 检索
        raw_hits = self._search_raw_papers(gap_keywords)

        # 2. wiki/papers/ 阅读笔记检索
        wiki_hits = self._search_wiki_papers(gap_keywords)

        # 3. KB 概念/方法检索
        kb_hits = self._search_kb(gap_keywords)

        # 合并去重
        all_hits: Dict[str, Dict[str, Any]] = {}
        for hit in raw_hits:
            aid = hit.get("arxiv_id", "")
            if aid:
                all_hits[aid] = hit
        for hit in wiki_hits:
            aid = hit.get("arxiv_id", "")
            if aid and aid not in all_hits:
                all_hits[aid] = hit
            elif aid:
                all_hits[aid].update(hit)

        # 构建结构化文本
        lines = ["【本地知识库预检索结果】\n"]
        if not all_hits and not kb_hits:
            lines.append("（无预检索结果）\n")
            return "\n".join(lines)

        # 论文命中
        if all_hits:
            lines.append(f"--- 论文命中（共 {len(all_hits)} 篇）---\n")
            for aid, hit in sorted(all_hits.items(), key=lambda x: -self._safe_float(x[1].get("score", 0))):
                title = hit.get("title", "未知")
                score = hit.get("score", 0)
                has_pdf = hit.get("has_pdf", False)
                read_status = hit.get("read_status", "unread")
                used_by = hit.get("used_by_proposals", [])
                lines.append(
                    f"- {title} (arXiv:{aid}) "
                    f"score={score} "
                    f"{'[有PDF]' if has_pdf else ''} "
                    f"[{read_status}] "
                    f"被{len(used_by)}个课题引用"
                )

        # KB 概念/方法命中
        if kb_hits:
            lines.append(f"\n--- KB 概念/方法命中（共 {len(kb_hits)} 条）---\n")
            for hit in kb_hits[:10]:
                lines.append(f"- {hit.get('title', '')} [{hit.get('type', '')}]")

        return "\n".join(lines)

    def link_to_proposal(
        self,
        arxiv_id: str,
        proposal_id: str,
        citation_location: str = "",
    ) -> bool:
        """将论文关联到课题（替代 lit_note 步骤的写入）。

        1. 读取 wiki/papers/{arxiv_id}.md frontmatter
        2. used_by_proposals 追加 proposal_id（去重）
        3. 若有 citation_location，追加到 proposals_citations 字段
        4. 通过 kb_wiki.save_wiki_page() 回写

        Returns: 是否成功更新
        """
        if _log:
            _log.info(f"[LiteratureService] link_to_proposal arxiv_id={arxiv_id} proposal_id={proposal_id}")

        wiki_path = WIKI_PAPERS_DIR / f"{arxiv_id}.md"
        # v7.3.12（BUG-38）：多命名代解析——裸 id 代不存在时回退到 slug 代
        # （下划线 / 点号 / 裸 id+slug），避免「论文确实在 KB 里却判不存在」。
        rel_path = f"wiki/papers/{arxiv_id}.md"
        if not wiki_path.exists():
            candidates = _wiki_paper_candidates(arxiv_id)
            if not candidates:
                if _log:
                    _log.warning(f"[LiteratureService] 论文 wiki 页面不存在: {arxiv_id}")
                return False
            actual = candidates[0]
            rel_path = f"wiki/papers/{actual.name}"
            wiki_path = actual
            if _log:
                _log.info(
                    f"[LiteratureService] 论文页走命名代回退: {arxiv_id} -> {actual.name}"
                )

        # 1. 读取现有 frontmatter
        existing = self.kw_get(rel_path)
        if not existing:
            return False

        # 2. 更新 used_by_proposals
        # v7.3.6 修复：get_wiki_page 返回键为 "frontmatter"/"body"（非 "meta"/"content"），
        # 原实现恒取空 dict → 回写时全部 frontmatter 丢失（created/source_raw/tags 等被重置为默认值），
        # 且正文被清空。与 _save_wiki_paper_note v6.8.51 同源缺陷，此处一并修正。
        meta = dict(existing.get("frontmatter", {}) or {})
        used_by = meta.get("used_by_proposals", [])
        if isinstance(used_by, str):
            used_by = [used_by]
        if proposal_id not in used_by:
            used_by.append(proposal_id)
        meta["used_by_proposals"] = used_by

        # 3. 更新 citations
        if citation_location:
            citations = meta.get("proposals_citations", {})
            # v7.3.6 修复：kb_text.build_frontmatter 对 dict 值一律
            # str() 序列化（dict 落到 else 分支），proposals_citations 被写成
            # 字符串 "{'pid': ['adversarial-review']}"；parse_frontmatter 不会
            # 反解该字符串 → 取回仍是 str。旧实现只判 list 不判 str →
            # citations.get(...) 抛 AttributeError: 'str' object has no
            # attribute 'get' → lit_note 步骤整体失败（实测 11-03 19:55
            # berry r2 content-lit_note attempts=3 终态失败）。
            # 此处把 str 形态归一为 dict（用 ast.literal_eval，失败则重建）。
            citations = _normalize_citations(citations)
            prop_cites = citations.get(proposal_id, [])
            if not isinstance(prop_cites, list):
                prop_cites = []
            if citation_location not in prop_cites:
                prop_cites.append(citation_location)
            citations[proposal_id] = prop_cites
            meta["proposals_citations"] = citations

        # 4. 回写
        meta["updated"] = now_utc()
        content = existing.get("body", "")
        page = self.kw_build(
            title=meta.get("title", arxiv_id),
            wiki_type="papers",
            content=content,
            meta=meta,
        )
        # v7.3.12（BUG-38）：回写到**实际存在的页**（可能是 slug 代），
        # 否则会在裸 id 名下新建一页 → 同一篇论文出现两个页面（真重复）。
        self.kw_save(rel_path, page)
        return True

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        """安全地将值转换为 float。"""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        try:
            v = str(value).strip()
            return float(v) if v else default
        except (ValueError, TypeError):
            return default

    def get_status(self, arxiv_id: str) -> Dict[str, Any]:
        """查询论文状态（统一状态查询入口）。

        从 KB raw/papers frontmatter 读取：
        status, unified_status, read_status,
        used_by_proposals, has_pdf, score
        """
        raw_path = self._find_raw_paper_path(arxiv_id)
        if not raw_path:
            return {"arxiv_id": arxiv_id, "status": "unknown", "read_status": "unread"}

        from kb_text import parse_frontmatter
        text = raw_path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        return {
            "arxiv_id": arxiv_id,
            "status": fm.get("status", "unseen"),
            "unified_status": fm.get("unified_status", "pool"),
            "read_status": fm.get("read_status", "unread"),
            "used_by_proposals": fm.get("used_by_proposals", []),
            "has_pdf": fm.get("has_pdf", False),
            "score": self._safe_float(fm.get("score_deepxiv", fm.get("score", 0))),
            "title": fm.get("title", ""),
            "source": fm.get("source", ""),
        }

    # ─────────────────────────────────────────────
    # 内部方法
    # ─────────────────────────────────────────────

    def _get_exclude_ids(self, proposal_id: Optional[str] = None) -> Set[str]:
        """获取需要排除的论文 ID 集合。

        合并 state_sync.get_processed_ids() 和 KB raw/papers 已有 ID。
        若指定 proposal_id，另排除已关联此 proposal 的论文。
        """
        exclude: Set[str] = set()

        # state_sync 已处理论文
        try:
            processed = self.state_sync.get_processed_ids()
            exclude.update(processed)
        except Exception:
            pass

        # KB raw/papers 已有论文
        if RAW_PAPERS_DIR.exists():
            for f in RAW_PAPERS_DIR.glob("*.md"):
                raw_id = self._extract_arxiv_from_filename(f.name)
                if raw_id:
                    exclude.add(raw_id)

        # 若指定 proposal_id，排除已关联此 proposal 的论文
        if proposal_id and WIKI_PAPERS_DIR.exists():
            for f in WIKI_PAPERS_DIR.glob("*.md"):
                try:
                    from kb_text import parse_frontmatter
                    text = f.read_text(encoding="utf-8")
                    fm, _ = parse_frontmatter(text)
                    used_by = fm.get("used_by_proposals", [])
                    if isinstance(used_by, str):
                        used_by = [used_by]
                    if proposal_id in used_by:
                        raw_id = fm.get("arxiv_id", "") or self._extract_arxiv_from_filename(f.name)
                        if raw_id:
                            exclude.add(raw_id)
                except Exception:
                    pass

        return exclude

    def _scan_local_raw_papers(self) -> Dict[str, Dict[str, Any]]:
        """扫描本地文献源，返回 {arxiv_id: info}。

        v6.8.1: 合并两个源 —
        1. knowledge/raw/papers/（CoPilot 原生）
        2. hermes briefings/papers/（hermes 简报产出，零拷贝读取）
        对于仅在 hermes 源中的论文，惰性物化到 raw/papers/。
        """
        papers: Dict[str, Dict[str, Any]] = {}

        def _coerce_arxiv_id(val: Any) -> str:
            """确保 arxiv_id 始终为字符串（YAML 无引号数字会被解析为 float）。"""
            if not val:
                return ""
            return str(val)

        # 源 1: CoPilot 原生 raw/papers/
        if RAW_PAPERS_DIR.exists():
            for f in RAW_PAPERS_DIR.glob("*.md"):
                try:
                    from kb_text import parse_frontmatter
                    text = f.read_text(encoding="utf-8")
                    fm, _ = parse_frontmatter(text)
                    arxiv_id = _coerce_arxiv_id(fm.get("arxiv_id", "")) or self._extract_arxiv_from_filename(f.name)
                    if arxiv_id:
                        papers[arxiv_id] = {
                            "title": fm.get("title", ""),
                            "has_pdf": fm.get("has_pdf", False),
                            "read_status": fm.get("read_status", "unread"),
                            "score": fm.get("score_deepxiv", fm.get("score", 0)),
                            "used_by_proposals": fm.get("used_by_proposals", []),
                            "source": "raw",
                        }
                except Exception:
                    pass

        # 源 2: hermes briefings/papers/（零拷贝读取 + 惰性物化）
        if HERMES_BRIEFING_PAPERS_DIR.exists():
            for f in HERMES_BRIEFING_PAPERS_DIR.glob("*.md"):
                try:
                    from kb_text import parse_frontmatter
                    text = f.read_text(encoding="utf-8")
                    fm, _ = parse_frontmatter(text)
                    arxiv_id = _coerce_arxiv_id(fm.get("arxiv_id", "")) or self._extract_arxiv_from_filename(f.name)
                    if arxiv_id and arxiv_id not in papers:
                        papers[arxiv_id] = {
                            "title": fm.get("title", ""),
                            "has_pdf": False,
                            "read_status": "unread",
                            "score": fm.get("score", 0),
                            "used_by_proposals": [],
                            "source": "hermes-briefing",
                        }
                        # 惰性物化：在 raw/papers/ 中创建对应 .md
                        self._materialize_from_briefing(arxiv_id, f, fm)
                except Exception:
                    pass

        return papers

    def _materialize_from_briefing(self, arxiv_id: str, briefing_path: Path, fm: Dict[str, Any]) -> None:
        """惰性物化：将 hermes 简报 .md 复制为 raw/papers/ 格式。

        幂等：目标文件已存在则跳过。
        """
        try:
            raw_dir = RAW_DIR / "papers"
            raw_dir.mkdir(parents=True, exist_ok=True)
            year = fm.get("year", "")
            title = fm.get("title", arxiv_id)
            slug = self._safe_filename(f"{year}-{arxiv_id}-{title}") if hasattr(self, '_safe_filename') else f"{year}-{arxiv_id}"
            raw_path = raw_dir / f"{slug}.md"
            if raw_path.exists():
                return
            # 构建 CoPilot 格式的 frontmatter
            from kb_text import build_frontmatter
            copilot_fm = {
                "title": fm.get("title", ""),
                "arxiv_id": arxiv_id,
                "authors": fm.get("authors", ""),
                "year": year,
                "tags": ["deepxiv-论文库"],
                "project": ["NSFC-强场超快"],
                "direction": fm.get("direction", ""),
                "source": "hermes-briefing",
                "imported_at": now_utc(),
                "score_deepxiv": fm.get("score", 0.5),
                "status": "unseen",
                "read_status": "unread",
                "has_pdf": False,
            }
            fm_str = build_frontmatter(copilot_fm)
            # 读取 briefing 正文（去掉原始 frontmatter）
            text = briefing_path.read_text(encoding="utf-8")
            body = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL).strip()
            raw_path.write_text(f"{fm_str}\n{body}", encoding="utf-8")
            if _log:
                _log.info(f"[LiteratureService] 惰性物化: {arxiv_id} → {raw_path.name}")
        except Exception as e:
            if _log:
                _log.warning(f"[LiteratureService] 物化 {arxiv_id} 失败: {e}")

    def _build_note_from_hermes_analysis(self, arxiv_id: str) -> Optional[str]:
        """v6.8.1 + v6.8.3: 从 hermes deep_analysis_{aid}.json 构建阅读笔记。

        hermes 的深度分析包含结构化数据（why_notable, core_findings,
        new_methods, what_next, linsai_connection），转换为统一的 5 维度
        学术阅读笔记格式（研究问题、研究背景、研究方法、主要发现、潜在方向）。

        Returns:
            阅读笔记 markdown 内容，或 None（JSON 不存在时）
        """
        analysis_path = HERMES_BRIEFINGS_DIR / f"deep_analysis_{arxiv_id}.json"
        if not analysis_path.exists():
            return None

        try:
            data = json.loads(analysis_path.read_text(encoding="utf-8"))
        except Exception:
            return None

        if not data or not data.get("arxiv_id"):
            return None

        title = data.get("title", arxiv_id)
        authors = data.get("authors", [])
        if isinstance(authors, list):
            authors_str = ", ".join(authors)
        else:
            authors_str = str(authors)

        def _list(items) -> str:
            if isinstance(items, list):
                return "\n".join(f"- {item}" for item in items)
            return str(items) if items else "（暂无）"

        lines = [
            f"# {title}",
            f"",
            f"**arXiv ID**: {arxiv_id}",
            f"**作者**: {authors_str}",
            f"**日期**: {data.get('date', '')}",
            f"**方向**: {data.get('direction', '')}",
            f"",
            f"## 研究问题（Research Question）",
            f"",
            data.get("why_notable", "（无数据）"),
            f"",
            f"## 研究背景（Background）",
            f"",
            data.get("linsai_connection", "（无数据）"),
            f"",
            f"## 研究方法（Methods）",
            f"",
        ]

        methods = data.get("new_methods", [])
        lines.append(_list(methods))

        lines.extend([
            f"",
            f"## 主要发现与核心结论（Main Results）",
            f"",
        ])

        findings = data.get("core_findings", [])
        lines.append(_list(findings))

        lines.extend([
            f"",
            f"## 潜在研究方向（Future Directions）",
            f"",
        ])

        what_next = data.get("what_next", [])
        lines.append(_list(what_next))

        if _log:
            _log.info(f"[LiteratureService] 从 hermes 深度分析构建笔记: {arxiv_id}")
        return "\n".join(lines)

    def _build_search_prompt(
        self,
        keywords: List[str],
        source: str,
        depth: str,
        limit: int,
        exclude_prompt: str,
    ) -> str:
        """构建用于 researcher 联网检索的 prompt。"""
        kw_str = "、".join(keywords)
        prompt = (
            f"请检索以下主题的最新论文（近 2 年）。\n\n"
            f"【检索关键词】{kw_str}\n"
            f"【来源】{source}\n"
            f"【检索深度】{depth}（最多 {limit} 篇）\n\n"
            f"要求：\n"
            f"1. 使用 web_search 和 DeepXiv 工具检索 arXiv 论文\n"
            f"2. 对每篇论文给出：arxiv_id、标题、作者、年份、评分(0-1)、TL;DR\n"
            f"3. 按评分从高到低排序\n"
            f"4. **必须**输出 JSON 数组格式（不要 markdown 代码块标记）：\n"
            f'   [{{"arxiv_id": "2403.15337", "title": "标题", "authors": "作者", "year": "2024", "score": 0.9, "tldr": "摘要"}}]\n'
            f"5. 如果检索不到论文，输出空数组 []\n"
            f"{exclude_prompt}"
        )
        return prompt

    def _dispatch_researcher(self, prompt: str, source: str) -> List[Dict[str, Any]]:
        """委托 hermes researcher 联网检索并解析返回结果。

        通过 hermes CLI oneshot 模式派发（与简报工作流一致）；失败/超时
        直接返回空列表——调用方 search() 空结果按"无新论文"成功放行
        （executor lit_search 仅异常才 success:False 触发重试），无重试风暴。

        v7.3.86: 删除旧方案B降级直调（hermes 失败后同 prompt 全文经
        llm_gateway 直调，落全局 minimax 链）——降级端无联网能力，检索
        prompt 只能凭参数化知识硬答：11-16 账本实证两起双烧共 61.4k
        token（hermes 480s 超时空烧 29.1k + router 全文重发 32.4k 仅
        产出 171 字符），占当日 MiniMax 池可见消耗 38%，近乎纯烧。
        """
        results: List[Dict[str, Any]] = []

        # hermes agent loop（多步 web_search）
        # v7.3.81: 超时 300→480——researcher 全库成功分布 p99=441s、
        # max=633s，300 只盖到 p90=232s（账本 74 次超时恰卡在 300s 档，
        # 属可自然完成的近失杀）；对齐 executor v7.3.45 梯度化思路按
        # p99 锚定，联网检索 agent loop（多步 web_search）需要余量。
        try:
            from hermes_memory import _run_hermes_agent
            agent_result = _run_hermes_agent("researcher", prompt, timeout=480)
            if agent_result.get("success"):
                text = agent_result.get("output", "")
                results = self._parse_researcher_output(text)
                if results:
                    return results
        except Exception as e:
            if _log:
                _log.warning(f"[LiteratureService] hermes agent 调用失败: {e}")

        if _log:
            _log.warning(
                "[LiteratureService] researcher 派发未成功（超时/失败），"
                "本轮返回空结果（v7.3.86 起不再降级直调）")
        return results

    def _parse_researcher_output(self, text: str) -> List[Dict[str, Any]]:
        """解析 researcher 输出的论文列表。

        多格式兼容（按优先级尝试）：
        1. JSON 数组格式: [{"arxiv_id": ..., "title": ...}, ...]
        2. 管道符格式: - arxiv_id | 标题 | 作者 | 年份 | 评分 | 摘要
        3. Markdown 表格格式: | 2403.15337 | 标题 | ... |
        4. 自然语言提取: arXiv:2403.15337 出现在文本任意位置
        """
        import re
        if not text or not text.strip():
            return []

        arxiv_pattern = re.compile(r"(\d{4}\.\d{4,5})")

        # ── 格式 1: JSON 数组 ──
        json_papers = self._try_parse_json(text, arxiv_pattern)
        if json_papers:
            return json_papers

        # ── 格式 2 + 3: 管道符 / Markdown 表格 / 编号列表 ──
        pipe_papers = self._try_parse_pipe_or_table(text, arxiv_pattern)
        if pipe_papers:
            return pipe_papers

        # ── 格式 4: 自然语言提取（兜底） ──
        nl_papers = self._try_parse_natural_language(text, arxiv_pattern)
        return nl_papers

    def _try_parse_json(self, text: str, arxiv_pattern) -> List[Dict[str, Any]]:
        """尝试从文本中提取 JSON 数组。"""
        import re
        cleaned = text.strip()
        # 去除 markdown 代码块标记
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        # 尝试找到 JSON 数组（支持嵌套在文本中的情况）
        for start in range(len(cleaned)):
            if cleaned[start] == '[':
                # 找到匹配的 ]
                depth = 0
                for end in range(start, len(cleaned)):
                    if cleaned[end] == '[':
                        depth += 1
                    elif cleaned[end] == ']':
                        depth -= 1
                        if depth == 0:
                            try:
                                data = json.loads(cleaned[start:end + 1])
                                if isinstance(data, list):
                                    papers = []
                                    for item in data:
                                        if not isinstance(item, dict):
                                            continue
                                        arxiv_id = str(item.get("arxiv_id", ""))
                                        m = arxiv_pattern.search(arxiv_id)
                                        if m:
                                            arxiv_id = m.group(1)
                                        papers.append({
                                            "arxiv_id": arxiv_id,
                                            "title": str(item.get("title", item.get("name", ""))),
                                            "authors": str(item.get("authors", "")),
                                            "year": str(item.get("year", "")),
                                            "score": self._safe_float(item.get("score", 0.5)),
                                            "tldr": str(item.get("tldr", item.get("summary", item.get("abstract", "")))),
                                            "is_new": False,
                                            "has_local_pdf": False,
                                            "read_status": "unread",
                                        })
                                    if papers:
                                        return papers
                            except (json.JSONDecodeError, KeyError, TypeError):
                                pass
        return []

    def _try_parse_pipe_or_table(self, text: str, arxiv_pattern) -> List[Dict[str, Any]]:
        """尝试管道符格式和 Markdown 表格格式。"""
        import re
        papers: List[Dict[str, Any]] = []
        in_table = False
        header_parsed = False

        for line in text.split("\n"):
            line = line.strip()
            if not line:
                # 表格结束
                if in_table:
                    in_table = False
                continue

            # 检测 Markdown 表格分隔行（|---|---|）
            if re.match(r"^\|[\s\-:|]+\|$", line):
                in_table = True
                header_parsed = True
                continue

            # 检测 Markdown 表格数据行（以 | 开头）
            if line.startswith("|") and "|" in line[1:]:
                if not header_parsed:
                    # 这是表头行，跳过
                    in_table = True
                    continue
                # 表格数据行：split by | but skip empty first field
                parts = [p.strip() for p in line.strip("|").split("|")]
                # 查找含 arxiv_id 的字段
                arxiv_id = ""
                title_idx = -1
                for idx, p in enumerate(parts):
                    m = arxiv_pattern.search(p)
                    if m and not arxiv_id:
                        arxiv_id = m.group(1)
                    if not p and idx > 0:
                        continue
                    if title_idx < 0 and p and not arxiv_pattern.match(p.strip()):
                        title_idx = idx
                if title_idx < 0:
                    title_idx = 1 if len(parts) > 1 else 0
                paper = {
                    "arxiv_id": arxiv_id,
                    "title": parts[title_idx] if title_idx < len(parts) else "",
                    "authors": parts[title_idx + 1] if title_idx + 1 < len(parts) else "",
                    "year": "",
                    "score": 0.5,
                    "tldr": parts[title_idx + 2] if title_idx + 2 < len(parts) else "",
                    "is_new": False,
                    "has_local_pdf": False,
                    "read_status": "unread",
                }
                if arxiv_id or paper["title"]:
                    papers.append(paper)
                continue

            # 非表格行，检查管道符格式（- arxiv_id | title | ...）
            in_table = False
            header_parsed = False
            # 去除常见前缀："- ", "1. ", "1) ", "* ", "• "
            stripped = re.sub(r"^(?:[-*•] |\d+[.)] )", "", line).strip()
            if not stripped:
                continue

            parts = stripped.split("|")
            if len(parts) >= 2:
                first_field = parts[0].strip()
                arxiv_match = arxiv_pattern.search(first_field)
                arxiv_id = arxiv_match.group(1) if arxiv_match else ""
                # 标题可能是第二个字段
                title = parts[1].strip() if len(parts) > 1 else first_field
                papers.append({
                    "arxiv_id": arxiv_id,
                    "title": title,
                    "authors": parts[2].strip() if len(parts) > 2 else "",
                    "year": parts[3].strip() if len(parts) > 3 else "",
                    "score": self._safe_float(parts[4].strip()) if len(parts) > 4 else 0.5,
                    "tldr": parts[5].strip() if len(parts) > 5 else "",
                    "is_new": False,
                    "has_local_pdf": False,
                    "read_status": "unread",
                })

        return papers

    def _try_parse_natural_language(self, text: str, arxiv_pattern) -> List[Dict[str, Any]]:
        """兜底：从自然语言中提取所有 arXiv ID。

        注意：自然语言提取只返回 arXiv ID，不编造标题/作者等字段。
        调用方应通过后端（如 DeepXiv API）补充完整元数据后再入库。
        标题标记为"(需补充元数据)"，避免低质量数据污染知识库。
        """
        import re
        papers: List[Dict[str, Any]] = []
        seen_ids: set = set()
        for m in arxiv_pattern.finditer(text):
            aid = m.group(1)
            if aid in seen_ids:
                continue
            seen_ids.add(aid)
            papers.append({
                "arxiv_id": aid,
                "title": "(需补充元数据)",
                "authors": "",
                "year": "",
                "score": 0.3,
                "tldr": "",
                "is_new": False,
                "has_local_pdf": False,
                "read_status": "unread",
                "_needs_metadata": True,  # 标记需要后续补充
            })
        return papers

    def _extract_arxiv_id(self, paper: Dict[str, Any]) -> str:
        """从论文信息中提取 arxiv_id。"""
        # 优先从显式字段取
        aid = paper.get("arxiv_id", "")
        if aid and re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", aid):
            return aid.split("v")[0]
        if aid and re.match(r"^\d{7,8}$", aid):
            return aid

        # 从标题中提取
        title = paper.get("title", "")
        m = re.search(r"(\d{4}\.\d{4,5}(v\d+)?)", title)
        if m:
            return m.group(1).split("v")[0]
        m = re.search(r"arXiv:(\d{4}\.\d{4,5})", title)
        if m:
            return m.group(1)

        return aid

    def _extract_arxiv_from_filename(self, filename: str) -> str:
        """从文件名中提取 arxiv_id。"""
        # 格式: YYYY-arxiv_id-slug.md
        m = re.match(r"\d{4}-(\d{4}\.\d{4,5}(v\d+)?)-", filename)
        if m:
            return m.group(1).split("v")[0]
        m = re.match(r"(\d{4}\.\d{4,5})", filename)
        if m:
            return m.group(1).split("v")[0]
        return ""

    def _ingest_new_papers(
        self,
        papers: List[Dict[str, Any]],
        source: str,
        proposal_id: Optional[str] = None,
    ) -> Dict[str, int]:
        """将新论文入库 KB。跳过需要补充元数据的条目。

        Returns:
            {"ingested": int, "failed": int, "skipped": int}
        """
        ingested = 0
        failed = 0
        skipped = 0
        for paper in papers:
            arxiv_id = self._extract_arxiv_id(paper)
            # v6.8.43: 支持无 arXiv ID 的期刊论文（OpenAlex/Crossref/PubMed 来源），以 DOI 作为标识
            doi = str(paper.get("doi", "") or "").strip()
            doi_clean = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi).strip()
            # v6.9.47: researcher agent 常把期刊 DOI 直接塞进 arxiv_id 字段
            # （中文期刊无 arXiv 预印本，08-24 attosecond r2 lit_search 10 篇
            # 全部此形态）。该形态绕过 arxiv 校验（_extract_arxiv_id 兜底
            # 原样返回）与 DOI 清洗，identifier 保留 "/" 使 raw/papers
            # write_text 抛 ENOENT——实测 10 篇丢 8 篇（failed=8）。
            # 归一化：非 arxiv 形态且匹配 DOI 模式 → 移入 doi_clean，
            # 走 doi-{slug} 清洗路径（点/斜杠转连字符）。
            if (
                arxiv_id
                and not re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", arxiv_id)
                and not re.match(r"^\d{7,8}$", arxiv_id)
                and re.match(r"^10\.\d{4,9}/\S+$", arxiv_id)
            ):
                if not doi_clean:
                    doi_clean = arxiv_id
                arxiv_id = ""
            if not arxiv_id and not doi_clean:
                continue
            # v6.8.44: DOI 标识符保留点/斜杠结构（转连字符），避免 _safe_filename 剥点后
            # 产生有损文件名（如 10.1038/x → 101038x），造成 DOI 可读性差与潜在碰撞
            doi_slug = self._safe_filename(doi_clean.replace("/", "-").replace(".", "-"))
            identifier = arxiv_id or f"doi-{doi_slug}"
            # v6.8.3: 跳过自然语言提取的缺元数据条目，不污染知识库
            if paper.get("_needs_metadata"):
                if _log:
                    _log.info(f"[LiteratureService] 跳过缺元数据论文: {identifier}，需通过 DeepXiv 补充")
                skipped += 1
                continue
            try:
                import kb_importer as ki
                from kb_text import build_frontmatter

                # 构建 raw/papers/ 条目
                raw_dir = RAW_DIR / "papers"
                raw_dir.mkdir(parents=True, exist_ok=True)
                title_safe = self._safe_filename(paper.get("title", "untitled"))
                slug = f"{paper.get('year', '2024')}-{identifier}-{title_safe}"
                raw_path = raw_dir / f"{slug}.md"
                if raw_path.exists():
                    skipped += 1
                    continue

                fm = {
                    "title": paper.get("title", ""),
                    "doi": doi_clean,  # v6.8.43: 期刊论文 DOI（可为空）
                    "authors": paper.get("authors", ""),
                    "year": paper.get("year", "2024"),
                    "tags": ["deepxiv-论文库"],
                    "project": ["NSFC-强场超快"],
                    "direction": paper.get("direction", ""),
                    "source": paper.get("source", source),
                    "imported_at": now_utc(),
                    "score_deepxiv": paper.get("score", 0.5),
                    "status": "unseen",
                    "unified_status": "pool",
                    "read_status": "unread",
                    "used_by_proposals": [proposal_id] if proposal_id else [],
                    "has_pdf": False,
                    "abstract": paper.get("abstract", "")[:200],
                    "status_history": [
                        {"status": "pool", "at": now_utc(), "by": "literature_service"}
                    ],
                }
                if arxiv_id:
                    fm["arxiv_id"] = arxiv_id
                content = build_frontmatter(fm)
                body = f"\n\n# {paper.get('title', '')}\n\n{paper.get('tldr', '')}\n"
                if doi_clean and not arxiv_id:
                    body += f"\n**DOI**: [https://doi.org/{doi_clean}](https://doi.org/{doi_clean})\n"
                content += body
                raw_path.write_text(content, encoding="utf-8")
                ingested += 1

                if _log:
                    _log.info(f"[LiteratureService] 新论文入库: {identifier} ({paper.get('title', '')[:50]})")
            except Exception as e:
                failed += 1
                if _log:
                    _log.warning(f"[LiteratureService] 入库失败 {identifier}: {e}")
        return {"ingested": ingested, "failed": failed, "skipped": skipped}

    def _mark_used_by_proposal(self, arxiv_id: str, proposal_id: str) -> None:
        """在 raw/papers/ frontmatter 中标记论文被课题引用。"""
        raw_path = self._find_raw_paper_path(arxiv_id)
        if not raw_path:
            return
        try:
            from kb_text import parse_frontmatter, build_frontmatter
            text = raw_path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            used_by = fm.get("used_by_proposals", [])
            if isinstance(used_by, str):
                used_by = [used_by]
            if proposal_id not in used_by:
                used_by.append(proposal_id)
                fm["used_by_proposals"] = used_by
                fm["updated"] = now_utc()
                new_fm = build_frontmatter(fm)
                raw_path.write_text(f"{new_fm}\n\n{body.strip()}", encoding="utf-8")
        except Exception:
            pass

    def _update_read_status(
        self,
        arxiv_id: str,
        read_status: str,
        proposal_id: Optional[str] = None,
    ) -> None:
        """更新 raw/papers/ frontmatter 的 read_status。"""
        raw_path = self._find_raw_paper_path(arxiv_id)
        if not raw_path:
            return
        try:
            from kb_text import parse_frontmatter, build_frontmatter
            text = raw_path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            fm["read_status"] = read_status
            fm["read_at"] = now_utc()
            if proposal_id:
                used_by = fm.get("used_by_proposals", [])
                if isinstance(used_by, str):
                    used_by = [used_by]
                if proposal_id not in used_by:
                    used_by.append(proposal_id)
                fm["used_by_proposals"] = used_by
            fm["updated"] = now_utc()
            new_fm = build_frontmatter(fm)
            raw_path.write_text(f"{new_fm}\n\n{body.strip()}", encoding="utf-8")
        except Exception:
            pass

    def _find_raw_paper_path(self, arxiv_id: str) -> Optional[Path]:
        """在 raw/papers/ 中查找对应 arxiv_id 的文件。"""
        if not RAW_PAPERS_DIR.exists():
            return None
        for f in RAW_PAPERS_DIR.glob(f"*-{arxiv_id}-*.md"):
            return f
        for f in RAW_PAPERS_DIR.glob(f"*-{arxiv_id}.md"):
            return f
        return None

    def _link_to_existing_page(
        self,
        page_path: Path,
        arxiv_id: str,
        proposal_id: str,
        citation_location: str = "",
    ) -> bool:
        """把课题关联信息回写到**已存在的**论文页（可能位于 slug 代命名下）。

        v7.3.12（BUG-38）：link_to_proposal 的裸 id 路径不可达时（页面以
        下划线 slug 代命名），关联信息无处落盘。本方法直接对既有页做
        used_by_proposals / proposals_citations 增量更新，不新建页面。

        Args:
            page_path: 已存在的论文页路径
            arxiv_id: 规范 arXiv id
            proposal_id: 课题 id
            citation_location: 引文位置标记（可空）
        Returns: 是否成功写回
        """
        try:
            rel_path = f"wiki/papers/{page_path.name}"
            existing = self.kw_get(rel_path)
            if not existing:
                return False
            meta = dict(existing.get("frontmatter", {}) or {})
            used_by = meta.get("used_by_proposals", [])
            if isinstance(used_by, str):
                used_by = [used_by]
            if proposal_id not in used_by:
                used_by.append(proposal_id)
            meta["used_by_proposals"] = used_by

            if citation_location:
                citations = _normalize_citations(meta.get("proposals_citations", {}))
                prop_cites = citations.get(proposal_id, [])
                if not isinstance(prop_cites, list):
                    prop_cites = []
                if citation_location not in prop_cites:
                    prop_cites.append(citation_location)
                citations[proposal_id] = prop_cites
                meta["proposals_citations"] = citations

            meta["updated"] = now_utc()
            page = self.kw_build(
                title=meta.get("title", arxiv_id),
                wiki_type="papers",
                content=existing.get("body", ""),
                meta=meta,
            )
            self.kw_save(rel_path, page)
            return True
        except Exception as e:
            if _log:
                _log.warning(
                    f"[LiteratureService] 关联回写失败 {page_path.name}: {e}"
                )
            return False

    def _get_wiki_paper_note(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """获取 wiki/papers/ 页面。

        v7.3.12（BUG-38）：多命名代解析——裸 id 代不存在时回退到 slug 代
        （下划线 / 点号 / 裸 id+slug），否则下划线 slug 代的已深读论文会被
        误判为「未读」并重复派发深度阅读（read() 缓存判定走本方法）。
        """
        try:
            page = self.kw_get(f"wiki/papers/{arxiv_id}.md")
            if page:
                return page
            candidates = _wiki_paper_candidates(arxiv_id)
            for p in candidates:
                got = self.kw_get(f"wiki/papers/{p.name}")
                if got:
                    return got
            return None
        except Exception:
            return None

    def _save_wiki_paper_note(
        self,
        arxiv_id: str,
        content: str,
        proposal_id: Optional[str] = None,
        title: Optional[str] = None,
    ) -> None:
        """保存阅读笔记到 wiki/papers/。

        v6.8.51 修复：
        - 旧实现 kw_build 构建整页后交给 kw_save 二次包裹 → 双 frontmatter 污染
          （实测 147 篇笔记中 95 篇叠加、99 篇 title 退化为裸 arXiv ID）。
          现改为直接传正文 + meta，由 kb_wiki 门面统一构建。
        - 旧实现 existing.get("content") 恒为空（get_wiki_page 返回键为 "body"），
          导致每次追加笔记都会覆盖掉历史笔记。现读取 "body"。
        """
        try:
            paper_rel = f"wiki/papers/{arxiv_id}.md"
            display_title = title or f"Paper: {arxiv_id}"
            existing = self._get_wiki_paper_note(arxiv_id)
            if existing:
                # v7.3.12（BUG-38）：既有页可能位于 slug 代命名下——回写到
                # 该页而非裸 id 名下，否则同一篇论文会多出一个重复页面
                # （生产实证：30 篇真重复页 title="Paper: <id>" 由此产生）。
                actual = WIKI_PAPERS_DIR / f"{arxiv_id}.md"
                if not actual.exists():
                    candidates = _wiki_paper_candidates(arxiv_id)
                    if candidates:
                        paper_rel = f"wiki/papers/{candidates[0].name}"
                # 追加新的阅读笔记段落
                old_content = existing.get("body", "")
                meta = dict(existing.get("frontmatter", {}))
                if proposal_id:
                    used_by = meta.get("used_by_proposals", [])
                    if isinstance(used_by, str):
                        used_by = [used_by]
                    if proposal_id not in used_by:
                        used_by.append(proposal_id)
                    meta["used_by_proposals"] = used_by
                meta["read_status"] = READ_STATUS_DEEP_READ
                meta["updated"] = now_utc()
                if title:
                    meta["title"] = title
                self.kw_save(
                    paper_rel,
                    old_content
                    + f"\n\n## 阅读笔记\n\n### {proposal_id or 'general'}\n\n{content}",
                    meta=meta,
                )
            else:
                # 创建新页面：title 优先用论文真实题名（v6.8.51，避免裸 ID）
                meta = {
                    "title": display_title,
                    "type": "papers",
                    "arxiv_id": arxiv_id,
                    "tags": ["literature", "deep-read"],
                    "project": ["NSFC-强场超快"],
                    "read_status": READ_STATUS_DEEP_READ,
                    "used_by_proposals": [proposal_id] if proposal_id else [],
                    "read_at": now_utc(),
                    "created": now_utc(),
                    "updated": now_utc(),
                    "growth_stage": "mature",
                    "confidence": 0.8,
                }
                self.kw_save(
                    paper_rel,
                    f"## 深度解析\n\n（来自简报深度分析）\n\n## 阅读笔记\n\n### {proposal_id or 'general'}\n\n{content}",
                    meta=meta,
                )
        except Exception as e:
            if _log:
                _log.warning(f"[LiteratureService] 保存阅读笔记失败 {arxiv_id}: {e}")

    def _dispatch_deep_read(self, arxiv_id: str) -> str:
        """调用 hermes researcher 深度阅读论文。"""
        try:
            from llm_gateway import llm_complete, is_llm_available
            if not is_llm_available():
                return f"# Paper: {arxiv_id}\n\n> 深度阅读未执行（LLM 不可用）\n"
        except Exception:
            pass

        prompt = (
            f"请深度阅读以下论文并整理为结构化笔记。\n\n"
            f"【arXiv ID】{arxiv_id}\n\n"
            f"要求：\n"
            f"1. 使用 web_search 获取论文信息\n"
            f"2. 输出必须包含以下五个维度，每个维度不少于 3 句实质内容：\n"
            f"   ## 研究问题（Research Question）\n"
            f"   论文的核心研究问题、目标或中心论点（the research question, aim, or central argument）。\n\n"
            f"   ## 研究背景（Background）\n"
            f"   该问题的学术背景、前人工作、领域现状及研究动机（the background of the question）。\n\n"
            f"   ## 研究方法（Methods）\n"
            f"   数据来源、实验方法、理论框架或技术路线（data and method）。\n\n"
            f"   ## 主要发现与核心结论（Main Results）\n"
            f"   关键结果、定量发现、核心结论与图表数据（main results and findings）。\n\n"
            f"   ## 潜在研究方向（Future Directions）\n"
            f"   研究局限性、注意事项及未解决的开放问题（limitations, caveats, and open questions）。\n"
        )
        try:
            from hermes_memory import _run_hermes_agent
            # v7.3.81: 超时 300→480（同 _dispatch_researcher：深读五维
            # 长结构化输出 + 联网检索，300s 档为近失杀，按成功 p99=441s
            # 锚定）。
            # v7.3.86: 删除降级 LLM 直调——无联网能力下近年小众 arXiv 论文
            # 只能凭参数化知识硬答，幻觉笔记会污染知识库（v7.3.85 刚清完
            # 噪音）；失败/超时统一走下方占位符，executor._fallback_read
            # 视其为有效 content，不触发重试风暴。
            agent_result = _run_hermes_agent("researcher", prompt, timeout=480)
            if agent_result.get("success"):
                return agent_result.get("output", f"# Paper: {arxiv_id}\n\n> 阅读完成，但未返回内容\n")
        except Exception as e:
            if _log:
                _log.warning(f"[LiteratureService] deep_read hermes 调用失败: {e}")

        return f"# Paper: {arxiv_id}\n\n> 深度阅读未执行\n"

    def _search_kb_papers(self, keywords: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
        """v6.8.14 WP4: KB-first 本地论文检索——合并 raw/papers + wiki/papers。

        链 ⑥：先查本地知识库，命中 ≥60% 直接返回，不足才 fallback 在线检索。
        """
        raw_hits = self._search_raw_papers(keywords)
        wiki_hits = self._search_wiki_papers(keywords)

        # 合并去重（按 arxiv_id）
        seen = set()
        merged = []
        for hit in raw_hits + wiki_hits:
            aid = hit.get("arxiv_id", "")
            if aid and aid not in seen:
                seen.add(aid)
                hit["is_new"] = False
                hit["has_local_pdf"] = hit.get("has_pdf", False)
                merged.append(hit)

        return sorted(merged, key=lambda x: -self._safe_float(x.get("score", 0)))[:max_results]

    def _search_raw_papers(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """在 raw/papers/ frontmatter 中检索关键词。"""
        hits: List[Dict[str, Any]] = []
        if not RAW_PAPERS_DIR.exists():
            return hits
        for f in RAW_PAPERS_DIR.glob("*.md"):
            try:
                from kb_text import parse_frontmatter
                text = f.read_text(encoding="utf-8")
                fm, _ = parse_frontmatter(text)
                title = fm.get("title", "")
                abstract = fm.get("abstract", "")
                full_text = f"{title} {abstract} {fm.get('tags', [])}"
                score = self._match_keywords(full_text, keywords)
                if score > 0:
                    hits.append({
                        "arxiv_id": fm.get("arxiv_id", ""),
                        "title": title,
                        "score": score,
                        "has_pdf": fm.get("has_pdf", False),
                        "read_status": fm.get("read_status", "unread"),
                        "used_by_proposals": fm.get("used_by_proposals", []),
                    })
            except Exception:
                pass
        return sorted(hits, key=lambda x: -float(x["score"]))[:10]

    def _search_wiki_papers(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """在 wiki/papers/ 阅读笔记中检索关键词。"""
        hits: List[Dict[str, Any]] = []
        if not WIKI_PAPERS_DIR.exists():
            return hits
        for f in WIKI_PAPERS_DIR.glob("*.md"):
            try:
                from kb_text import parse_frontmatter
                text = f.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(text)
                score = self._match_keywords(f"{fm.get('title', '')} {body[:500]}", keywords)
                if score > 0:
                    hits.append({
                        "arxiv_id": fm.get("arxiv_id", ""),
                        "title": fm.get("title", ""),
                        "score": score,
                        "read_status": fm.get("read_status", "unread"),
                        "used_by_proposals": fm.get("used_by_proposals", []),
                    })
            except Exception:
                pass
        return sorted(hits, key=lambda x: -self._safe_float(x["score"]))[:10]


    def _search_kb(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """通过 knowledge_base.search() 检索 wiki 概念/方法。"""
        try:
            results = self.kb.search(" ".join(keywords), top_k=5, source="wiki")
            return [
                {"title": r.get("title", ""), "type": r.get("type", "wiki"), "score": r.get("score", 0.5)}
                for r in results
            ]
        except Exception:
            return []

    def _match_keywords(self, text: str, keywords: List[str]) -> float:
        """简单关键词匹配评分。"""
        text_lower = text.lower()
        score = 0.0
        for kw in keywords:
            kw_lower = kw.lower().strip()
            if kw_lower in text_lower:
                score += 1.0
        return score / max(len(keywords), 1)

    def _safe_filename(self, name: str) -> str:
        """生成安全的文件名片段。"""
        import re
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[-\s]+', '-', name)
        return name[:60].strip('-').lower()


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> bool:
    """运行自检，验证 LiteratureService 基本功能。"""
    print("=== LiteratureService 自检 ===")
    svc = LiteratureService()

    # 1. 测试 extract_arxiv_id
    assert svc._extract_arxiv_id({"arxiv_id": "2403.15337"}) == "2403.15337"
    assert svc._extract_arxiv_id({"arxiv_id": "2403.15337v2"}) == "2403.15337"
    assert svc._extract_arxiv_id({"title": "arXiv:2403.15337 Test"}) == "2403.15337"
    print("✓ _extract_arxiv_id")

    # 2. 测试 extract_arxiv_from_filename
    assert svc._extract_arxiv_from_filename("2024-2403.15337-test.md") == "2403.15337"
    assert svc._extract_arxiv_from_filename("2403.15337.md") == "2403.15337"
    print("✓ _extract_arxiv_from_filename")

    # 3. 测试 match_keywords
    assert svc._match_keywords("HHG in solids", ["HHG"]) == 1.0
    assert svc._match_keywords("Quantum metric", ["HHG", "Berry"]) == 0.0
    print("✓ _match_keywords")

    # 4. 测试 get_status（论文不存在时返回 unknown）
    status = svc.get_status("9999.99999")
    assert status["status"] == "unknown"
    print("✓ get_status (unknown paper)")

    # 5. 测试 parse_researcher_output
    text = "- 2403.15337 | HHG Test | Author | 2024 | 0.9 | Great paper"
    papers = svc._parse_researcher_output(text)
    assert len(papers) == 1
    assert papers[0]["arxiv_id"] == "2403.15337"
    print("✓ _parse_researcher_output")

    # 6. 测试 safe_filename
    fn = svc._safe_filename("HHG in Solids: A Review")
    assert "hhg-in-solids" in fn
    print("✓ _safe_filename")

    print("\n✓ LiteratureService 自检全部通过")
    return True


if __name__ == "__main__":
    _self_check()