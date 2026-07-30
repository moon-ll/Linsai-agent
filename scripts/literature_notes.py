#!/usr/bin/env python3
"""文献阅读笔记管理工具 —— v6.7.10

用途：
    在研究课题优化过程中持续记录补充阅读的文献。
    每条记录包含：阅读日期、文献标题、来源、核心结论、与课题关联、已引用位置。

存储约定：
    {proposal_dir}/02_literature/reading-notes.md
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc


class LiteratureNotes:
    """管理单课题的文献阅读笔记。"""

    def __init__(self, proposal_dir: Path | str) -> None:
        """Args:
            proposal_dir: 课题根目录（如 research_proposals/optimizing/xxx）
        """
        self.proposal_dir = Path(proposal_dir)
        self.notes_path = self.proposal_dir / "02_literature" / "reading-notes.md"
        self.notes_path.parent.mkdir(parents=True, exist_ok=True)

    def ensure_exists(self) -> None:
        """确保笔记文件存在（不存在则创建模板）。"""
        if self.notes_path.exists() and self.notes_path.stat().st_size > 100:
            return
        template = """# 文献阅读笔记

> 记录课题优化过程中补充阅读的文献，按阅读时间倒序排列。
> 每条记录应包含：文献标题、来源、核心结论、与课题关联、已引用位置。

| 阅读日期 | 文献标题 | 来源 | 核心结论 | 与课题关联 | 已引用位置 |
|---|---|---|---|---|---|

"""
        self.notes_path.write_text(template, encoding="utf-8")

    def append_note(
        self,
        title: str,
        source: str = "",
        conclusion: str = "",
        relevance: str = "",
        citation_location: str = "",
        date: Optional[str] = None,
    ) -> None:
        """追加一条阅读笔记。"""
        self.ensure_exists()
        date = date or now_utc()[:10]
        # 清理表格分隔符
        title = title.replace("|", "/")
        source = source.replace("|", "/")
        conclusion = conclusion.replace("|", "/").replace("\n", " ")
        relevance = relevance.replace("|", "/").replace("\n", " ")
        citation_location = citation_location.replace("|", "/")
        row = f"| {date} | {title} | {source} | {conclusion} | {relevance} | {citation_location} |\n"

        text = self.notes_path.read_text(encoding="utf-8")
        lines = text.split("\n")
        insert_idx = len(lines)
        for i, line in enumerate(lines):
            if line.startswith("|---|"):
                insert_idx = i + 1
                break
        lines.insert(insert_idx, row)
        self.notes_path.write_text("\n".join(lines), encoding="utf-8")

    def import_from_report(self, report_path: Path | str) -> int:
        """从 literature-report.md 或 lit-gap-*.md 中导入条目。

        v6.7.11: 兼容 researcher 输出的两种格式
          - 以 '- ' 开头的简洁标题行
          - 以 '**N. ' 开头的详细文献条目（如 '**1. Author (Year). Title...'）
        返回导入条数。
        """
        report_path = Path(report_path)
        if not report_path.exists():
            return 0

        try:
            text = report_path.read_text(encoding="utf-8")
        except Exception:
            return 0

        count = 0
        for line in text.split("\n"):
            line = line.strip()
            if not line or len(line) <= 10:
                continue

            title = ""
            source = ""

            # 格式 1：'- Author (Year). Title...'
            if line.startswith("-"):
                title = line.lstrip("-").strip()
            # 格式 2：'**N. Author (Year). Title...**'（researcher 定向检索报告常用）
            elif re.match(r"^\*\*\d+\.\s+", line):
                # 去掉首尾 ** 和编号
                title = re.sub(r"^\*\*\d+\.\s+", "", line).rstrip("*").strip()
            else:
                continue

            if not title:
                continue

            # 过滤掉非标题行（核心结论/支撑作用/来源等以 '- ' 开头的说明）
            if title.startswith(("核心结论", "支撑作用", "来源", "作者隶属")):
                continue

            # 简单提取来源标记（如果有 [source] 标记）
            m = re.search(r"\[(.+?)\]", title)
            if m:
                source = m.group(1)
                title = re.sub(r"\[.+?\]", "", title).strip()

            self.append_note(title=title, source=source or str(report_path.name))
            count += 1
        return count

    def list_notes(self) -> List[Dict[str, Any]]:
        """返回已记录的笔记条目列表。"""
        if not self.notes_path.exists():
            return []
        notes: List[Dict[str, Any]] = []
        text = self.notes_path.read_text(encoding="utf-8")
        for line in text.split("\n"):
            if not line.startswith("|") or line.startswith("|---|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            # 去掉首尾的空白单元格
            parts = [p for p in parts if p or p == ""]
            if len(parts) >= 6:
                notes.append({
                    "date": parts[0],
                    "title": parts[1],
                    "source": parts[2],
                    "conclusion": parts[3],
                    "relevance": parts[4],
                    "citation_location": parts[5],
                })
        return notes
