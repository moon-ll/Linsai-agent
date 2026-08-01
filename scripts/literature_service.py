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
from paths import PROJECT_ROOT, KNOWLEDGE_DIR, RAW_DIR, WIKI_DIR, QA_DIR

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

        if _log:
            _log.info(
                f"[LiteratureService] search source={source} depth={depth} "
                f"keywords={keywords} exclude={len(processed_ids | local_ids)} 篇"
            )

        # 3. 构建检索 prompt（注入 exclude_ids）
        exclude_prompt = ""
        if processed_ids or local_ids:
            all_exclude = processed_ids | local_ids
            exclude_prompt = (
                f"\n\n【请跳过以下已处理论文（共 {len(all_exclude)} 篇）】\n"
                + "\n".join(sorted(all_exclude))
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
            read_status = existing_note.get("read_status", "unread")
            if read_status == READ_STATUS_DEEP_READ:
                # 追加 proposal_id 到 used_by_proposals
                if proposal_id:
                    self._mark_used_by_proposal(arxiv_id, proposal_id)
                return {
                    "arxiv_id": arxiv_id,
                    "read_status": read_status,
                    "note_path": str(wiki_path),
                    "content": existing_note.get("content", ""),
                    "cached": True,
                }

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
        if not wiki_path.exists():
            if _log:
                _log.warning(f"[LiteratureService] 论文 wiki 页面不存在: {arxiv_id}")
            return False

        # 1. 读取现有 frontmatter
        existing = self.kw_get(f"wiki/papers/{arxiv_id}.md")
        if not existing:
            return False

        # 2. 更新 used_by_proposals
        meta = existing.get("meta", {})
        used_by = meta.get("used_by_proposals", [])
        if isinstance(used_by, str):
            used_by = [used_by]
        if proposal_id not in used_by:
            used_by.append(proposal_id)
        meta["used_by_proposals"] = used_by

        # 3. 更新 citations
        if citation_location:
            citations = meta.get("proposals_citations", {})
            if isinstance(citations, list):
                citations = {}
            prop_cites = citations.get(proposal_id, [])
            if citation_location not in prop_cites:
                prop_cites.append(citation_location)
            citations[proposal_id] = prop_cites
            meta["proposals_citations"] = citations

        # 4. 回写
        meta["updated"] = now_utc()
        content = existing.get("content", "")
        page = self.kw_build(
            title=meta.get("title", arxiv_id),
            wiki_type="papers",
            content=content,
            meta=meta,
        )
        self.kw_save(f"wiki/papers/{arxiv_id}.md", page)
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
        """扫描本地 raw/papers/ 目录，返回 {arxiv_id: info}。"""
        papers: Dict[str, Dict[str, Any]] = {}
        if not RAW_PAPERS_DIR.exists():
            return papers

        for f in RAW_PAPERS_DIR.glob("*.md"):
            try:
                from kb_text import parse_frontmatter
                text = f.read_text(encoding="utf-8")
                fm, _ = parse_frontmatter(text)
                arxiv_id = fm.get("arxiv_id", "") or self._extract_arxiv_from_filename(f.name)
                if arxiv_id:
                    papers[arxiv_id] = {
                        "title": fm.get("title", ""),
                        "has_pdf": fm.get("has_pdf", False),
                        "read_status": fm.get("read_status", "unread"),
                        "score": fm.get("score_deepxiv", fm.get("score", 0)),
                        "used_by_proposals": fm.get("used_by_proposals", []),
                    }
            except Exception:
                pass
        return papers

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
            f"4. 每篇论文的标题行必须以 '- ' 开头，格式为：\n"
            f"   '- arxiv_id | 标题 | 作者 | 年份 | score | TL;DR'\n"
            f"{exclude_prompt}"
        )
        return prompt

    def _dispatch_researcher(self, prompt: str, source: str) -> List[Dict[str, Any]]:
        """委托 hermes researcher 联网检索并解析返回结果。

        若 LLM 不可用，返回空列表。
        """
        try:
            from llm_gateway import llm_complete, is_llm_available
            if not is_llm_available():
                if _log:
                    _log.warning("[LiteratureService] LLM 不可用，跳过联网检索")
                return []
        except Exception:
            pass

        results: List[Dict[str, Any]] = []
        try:
            # 尝试通过 hermes_bridge 派活
            from hermes_bridge import dispatch_to_profile
            result = dispatch_to_profile("researcher", prompt, timeout=300)
            if result and result.get("success"):
                text = result.get("output", "")
                results = self._parse_researcher_output(text)
        except Exception:
            # 降级：直接通过 LLM 网关检索
            try:
                from llm_gateway import llm_complete
                resp = llm_complete("researcher", prompt, timeout=300)
                if resp:
                    results = self._parse_researcher_output(resp)
            except Exception:
                pass

        return results

    def _parse_researcher_output(self, text: str) -> List[Dict[str, Any]]:
        """解析 researcher 输出的论文列表。"""
        papers: List[Dict[str, Any]] = []
        for line in text.split("\n"):
            line = line.strip()
            if not line.startswith("- "):
                continue
            parts = line[2:].split("|")
            if len(parts) >= 2:
                arxiv_id = self._extract_arxiv_id({"title": parts[0].strip()})
                paper = {
                    "arxiv_id": arxiv_id or parts[0].strip(),
                    "title": parts[1].strip() if len(parts) > 1 else parts[0].strip(),
                    "authors": parts[2].strip() if len(parts) > 2 else "",
                    "year": parts[3].strip() if len(parts) > 3 else "",
                    "score": self._safe_float(parts[4].strip()) if len(parts) > 4 else 0.5,
                    "tldr": parts[5].strip() if len(parts) > 5 else "",
                    "is_new": False,
                    "has_local_pdf": False,
                    "read_status": "unread",
                }
                papers.append(paper)
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
    ) -> None:
        """将新论文入库 KB。"""
        for paper in papers:
            arxiv_id = self._extract_arxiv_id(paper)
            if not arxiv_id:
                continue
            try:
                import kb_importer as ki
                from kb_text import build_frontmatter

                # 构建 raw/papers/ 条目
                raw_dir = RAW_DIR / "papers"
                raw_dir.mkdir(parents=True, exist_ok=True)
                slug = f"{paper.get('year', '2024')}-{arxiv_id}-{self._safe_filename(paper.get('title', 'untitled'))}"
                raw_path = raw_dir / f"{slug}.md"
                if raw_path.exists():
                    continue

                fm = {
                    "title": paper.get("title", ""),
                    "arxiv_id": arxiv_id,
                    "authors": paper.get("authors", ""),
                    "year": paper.get("year", "2024"),
                    "tags": ["deepxiv-论文库"],
                    "project": ["NSFC-强场超快"],
                    "direction": paper.get("direction", ""),
                    "source": source,
                    "imported_at": now_utc(),
                    "score_deepxiv": paper.get("score", 0.5),
                    "status": "unseen",
                    "unified_status": "pool",
                    "read_status": "unread",
                    "used_by_proposals": [proposal_id] if proposal_id else [],
                    "has_pdf": False,
                    "abstract": "",
                    "status_history": [
                        {"status": "pool", "at": now_utc(), "by": "literature_service"}
                    ],
                }
                content = build_frontmatter(fm)
                content += f"\n\n# {paper.get('title', '')}\n\n{paper.get('tldr', '')}\n"
                raw_path.write_text(content, encoding="utf-8")

                if _log:
                    _log.info(f"[LiteratureService] 新论文入库: {arxiv_id} ({paper.get('title', '')[:50]})")
            except Exception as e:
                if _log:
                    _log.warning(f"[LiteratureService] 入库失败 {arxiv_id}: {e}")

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

    def _get_wiki_paper_note(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """获取 wiki/papers/ 页面。"""
        try:
            return self.kw_get(f"wiki/papers/{arxiv_id}.md")
        except Exception:
            return None

    def _save_wiki_paper_note(
        self,
        arxiv_id: str,
        content: str,
        proposal_id: Optional[str] = None,
    ) -> None:
        """保存阅读笔记到 wiki/papers/。"""
        try:
            # 检查是否已有页面
            existing = self._get_wiki_paper_note(arxiv_id)
            if existing:
                # 追加新的阅读笔记段落
                old_content = existing.get("content", "")
                meta = existing.get("meta", {})
                if proposal_id:
                    used_by = meta.get("used_by_proposals", [])
                    if isinstance(used_by, str):
                        used_by = [used_by]
                    if proposal_id not in used_by:
                        used_by.append(proposal_id)
                    meta["used_by_proposals"] = used_by
                meta["read_status"] = READ_STATUS_DEEP_READ
                meta["updated"] = now_utc()
                page = self.kw_build(
                    title=meta.get("title", arxiv_id),
                    wiki_type="papers",
                    content=old_content + f"\n\n## 阅读笔记\n\n### {proposal_id or 'general'}\n\n{content}",
                    meta=meta,
                )
            else:
                # 创建新页面
                meta = {
                    "title": f"Paper: {arxiv_id}",
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
                page = self.kw_build(
                    title=f"Paper: {arxiv_id}",
                    wiki_type="papers",
                    content=f"## 深度解析\n\n（来自简报深度分析）\n\n## 阅读笔记\n\n### {proposal_id or 'general'}\n\n{content}",
                    meta=meta,
                )
            self.kw_save(f"wiki/papers/{arxiv_id}.md", page)
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
            f"2. 输出格式：\n"
            f"   ## 核心结论\n"
            f"   ## 方法与创新\n"
            f"   ## 与课题关联\n"
            f"   ## 关键图表/数据\n"
            f"   ## 局限性\n"
        )
        try:
            from hermes_bridge import dispatch_to_profile
            result = dispatch_to_profile("researcher", prompt, timeout=300)
            if result and result.get("success"):
                return result.get("output", f"# Paper: {arxiv_id}\n\n> 阅读完成，但未返回内容\n")
        except Exception:
            try:
                resp = llm_complete("researcher", prompt, timeout=300)
                if resp:
                    return resp
            except Exception:
                pass

        return f"# Paper: {arxiv_id}\n\n> 深度阅读未执行\n"

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