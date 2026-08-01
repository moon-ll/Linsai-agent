#!/usr/bin/env python3
"""文献阅读笔记管理工具 —— v6.7.10 (KB wiki/papers 后端)

用途：
    在研究课题优化过程中持续记录补充阅读的文献。
    存储后端改为 KB wiki/papers/ 页面，按 proposal_id 分段写入。

存储约定：
    knowledge/wiki/papers/{arxiv_id}.md → ## 阅读笔记 下的 ### {proposal_id}

兼容视图：
    {proposal_dir}/02_literature/reading-notes.md（由 list_notes() 动态生成，只读）
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc
from paths import KNOWLEDGE_DIR, WIKI_DIR


class LiteratureNotes:
    """管理单课题的文献阅读笔记（后端：KB wiki/papers/）。"""

    def __init__(self, proposal_dir: Path | str) -> None:
        """Args:
            proposal_dir: 课题根目录（如 research_proposals/optimizing/xxx）
        """
        self.proposal_dir = Path(proposal_dir)
        self.proposal_id = self.proposal_dir.name  # 从目录名推导 proposal_id
        self.notes_path = self.proposal_dir / "02_literature" / "reading-notes.md"
        # 新后端：wiki/papers/ 目录
        self.wiki_papers_dir = WIKI_DIR / "papers"

    # ─────────────────────────────────────────────
    # 内部工具方法
    # ─────────────────────────────────────────────

    def _find_paper_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """在 wiki/papers/ 中按标题模糊匹配查找论文。

        Returns:
            {arxiv_id, path, title} 或 None
        """
        if not self.wiki_papers_dir.exists():
            return None
        from kb_text import parse_frontmatter

        for fpath in self.wiki_papers_dir.glob("*.md"):
            try:
                text = fpath.read_text(encoding="utf-8")
                fm, _ = parse_frontmatter(text)
                fm_title = fm.get("title", "")
                if title and (title.lower() in fm_title.lower()
                              or fm_title.lower() in title.lower()):
                    return {
                        "arxiv_id": fm.get("arxiv_id", fpath.stem),
                        "path": str(fpath.relative_to(KNOWLEDGE_DIR)),
                        "title": fm_title,
                    }
            except Exception:
                continue
        return None

    def _generate_compat_reading_notes(self, notes: List[Dict[str, Any]]) -> None:
        """动态生成旧的 per-proposal reading-notes.md 作为只读兼容视图。"""
        lines = [
            "# 文献阅读笔记",
            "",
            "> 记录课题优化过程中补充阅读的文献（由 wiki/papers/ 动态生成）。",
            "> 此文件为只读兼容视图，编辑请直接修改 wiki/papers/ 下对应页面。",
            "",
            "| 阅读日期 | 文献标题 | 来源 | 核心结论 | 与课题关联 | 已引用位置 |",
            "|---|---|---|---|---|---|",
        ]
        for n in notes:
            date = n.get("date", "")
            title = n.get("title", "").replace("|", "/")
            source = n.get("source", "").replace("|", "/")
            conclusion = n.get("conclusion", "").replace("|", "/")
            relevance = n.get("relevance", "").replace("|", "/")
            citation = n.get("citation_location", "").replace("|", "/")
            lines.append(
                f"| {date} | {title} | {source} | {conclusion} | {relevance} | {citation} |"
            )

        self.notes_path.parent.mkdir(parents=True, exist_ok=True)
        self.notes_path.write_text("\n".join(lines), encoding="utf-8")

    # ─────────────────────────────────────────────
    # 公共接口
    # ─────────────────────────────────────────────

    def ensure_exists(self) -> None:
        """确保 wiki/papers/ 目录存在（新后端结构）。"""
        self.wiki_papers_dir.mkdir(parents=True, exist_ok=True)
        # 兼容旧版：也保留旧的 per-proposal reading-notes.md 目录
        self.notes_path.parent.mkdir(parents=True, exist_ok=True)

    def append_note(
        self,
        title: str,
        source: str = "",
        conclusion: str = "",
        relevance: str = "",
        citation_location: str = "",
        date: Optional[str] = None,
        arxiv_id: Optional[str] = None,
    ) -> None:
        """追加一条阅读笔记到对应论文的 wiki/papers/ 页面。

        笔记内容写入对应论文 wiki 页面的 ## 阅读笔记 > ### {proposal_id} 下。
        若未指定 arxiv_id，则按 title 模糊匹配已有论文页面。
        """
        from kb_wiki import save_wiki_page

        self.ensure_exists()
        date = date or now_utc()[:10]

        # 查找论文页面
        paper_path = None
        paper_arxiv_id = arxiv_id
        if arxiv_id:
            # 直接按 arxiv_id 定位
            rel = f"wiki/papers/{arxiv_id}.md"
            if (self.wiki_papers_dir / f"{arxiv_id}.md").exists():
                paper_path = rel
        else:
            # 按标题模糊查找
            paper_info = self._find_paper_by_title(title)
            if paper_info:
                paper_path = paper_info["path"]
                paper_arxiv_id = paper_info["arxiv_id"]

        if not paper_path:
            # 未找到对应论文，使用 safe_filename 创建新页面
            from common import safe_filename as _safe_filename
            safe_name = _safe_filename(title)
            paper_arxiv_id = paper_arxiv_id or safe_name
            paper_path = f"wiki/papers/{paper_arxiv_id}.md"
            meta = {
                "title": title,
                "arxiv_id": paper_arxiv_id,
                "type": "papers",
                "used_by_proposals": [],
                "read_status": "unread",
                "status": "unseen",
                "unified_status": "pool",
            }
            save_wiki_page(paper_path, f"# {title}\n\n## 阅读笔记\n", meta)

        # 构建笔记内容（按 proposal_id 分段）
        note_entry = f"""### {self.proposal_id}

| 阅读日期 | 核心结论 | 与课题关联 | 已引用位置 |
|---|---|---|---|
| {date} | {conclusion.replace('|', '/').replace(chr(10), ' ')} | {relevance.replace('|', '/').replace(chr(10), ' ')} | {citation_location.replace('|', '/')} |

**来源**: {source}
"""

        # 追加到现有页面（save_wiki_page 的 append=True 会在正文末尾追加）
        save_wiki_page(paper_path, note_entry, append=True)

        # 更新 frontmatter 中的 used_by_proposals
        from kb_wiki import get_wiki_page, build_wiki_page
        existing = get_wiki_page(paper_path)
        if existing:
            fm = existing.get("frontmatter", {})
            used_by = fm.get("used_by_proposals", [])
            if isinstance(used_by, str):
                used_by = [used_by]
            if self.proposal_id not in used_by:
                used_by.append(self.proposal_id)
                # 仅更新 meta，不覆盖正文
                save_wiki_page(paper_path, "", meta={"used_by_proposals": used_by})

    def import_from_report(self, report_path: Path | str) -> int:
        """从 literature-report.md 或 lit-gap-*.md 中导入论文关联。

        v6.7.10: 改为遍历报告中的论文，对每篇调用
        LiteratureService.link_to_proposal() 关联到课题。
        同时保留 append_note() 写入文本记录。

        Args:
            report_path: 报告文件路径

        Returns:
            成功处理的论文数目
        """
        report_path = Path(report_path)
        if not report_path.exists():
            return 0

        try:
            text = report_path.read_text(encoding="utf-8")
        except Exception:
            return 0

        # 从报告中提取论文条目
        entries = []
        for line in text.split("\n"):
            line = line.strip()
            if not line or len(line) <= 10:
                continue

            title = ""
            # 格式 1：'- Author (Year). Title...'
            if line.startswith("-"):
                title = line.lstrip("-").strip()
            # 格式 2：'**N. Author (Year). Title...**'
            elif re.match(r"^\*\*\d+\.\s+", line):
                title = re.sub(r"^\*\*\d+\.\s+", "", line).rstrip("*").strip()
            else:
                continue

            if not title:
                continue

            # 过滤掉非标题行
            if title.startswith(("核心结论", "支撑作用", "来源", "作者隶属")):
                continue

            # 提取 arxiv_id（如果有）
            aid = None
            m = re.search(r"(\d{4}\.\d{4,5})", title)
            if m:
                aid = m.group(1)
                title = title.replace(m.group(0), "").strip()

            # 提取来源标记
            source = ""
            m = re.search(r"\[(.+?)\]", title)
            if m:
                source = m.group(1)
                title = re.sub(r"\[.+?\]", "", title).strip()

            entries.append({
                "title": title,
                "arxiv_id": aid,
                "source": source or str(report_path.name),
            })

        # 对每篇论文调用 link_to_proposal
        from literature_service import LiteratureService
        svc = LiteratureService()
        count = 0
        for entry in entries:
            aid = entry["arxiv_id"]
            if not aid:
                # 尝试按标题匹配已有论文
                paper = self._find_paper_by_title(entry["title"])
                if paper:
                    aid = paper["arxiv_id"]
            if aid:
                try:
                    svc.link_to_proposal(aid, self.proposal_id)
                    count += 1
                except Exception:
                    pass
            # 同时保留 append_note 写入（作为文本记录）
            self.append_note(
                title=entry["title"],
                source=entry["source"],
                arxiv_id=aid,
            )

        return count

    def list_notes(self) -> List[Dict[str, Any]]:
        """返回已记录的笔记条目列表。

        从 KB wiki/papers/ 读取 frontmatter，筛选 used_by_proposals 含
        此 proposal_id 的页面。同时动态生成旧的 per-proposal reading-notes.md
        作为只读兼容视图。
        """
        if not self.wiki_papers_dir.exists():
            return []

        notes = []
        # 遍历所有 wiki/papers/ 页面
        for fpath in sorted(self.wiki_papers_dir.glob("*.md")):
            try:
                from kb_text import parse_frontmatter
                text = fpath.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(text)
                used_by = fm.get("used_by_proposals", [])
                if isinstance(used_by, str):
                    used_by = [used_by]
                if self.proposal_id not in used_by:
                    continue
                notes.append({
                    "date": (fm.get("imported_at", "")[:10]
                             if fm.get("imported_at") else ""),
                    "title": fm.get("title", fpath.stem),
                    "source": fm.get("source", ""),
                    "conclusion": "",
                    "relevance": "",
                    "citation_location": "",
                    "arxiv_id": fm.get("arxiv_id", fpath.stem),
                    "read_status": fm.get("read_status", "unread"),
                })
            except Exception:
                continue

        # 动态生成旧的 per-proposal reading-notes.md 作为只读兼容视图
        self._generate_compat_reading_notes(notes)

        return notes