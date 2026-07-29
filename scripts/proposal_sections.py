#!/usr/bin/env python3
"""proposal 章节拆分工具 —— v6.7.7

用途：
    将单个 proposal-draft.md 按 NSFC 标准章节拆分为独立文件，
    支持分章节 critic/writer，降低单次 LLM 负载、减少超时。

章节映射（与 proposal_lifecycle.PROPOSAL_SECTIONS 保持一致）：
    rationale  → （一）立项依据
    content    → （二）研究内容
    method     → （三）研究方案

设计原则：
    - 保持 proposal-draft.md 作为汇总视图（自动从 sections/ 组装）
    - 旧格式兼容：若 sections/ 目录不存在，从 proposal-draft.md 解析
    - 新格式优先：若 sections/ 存在，读取 sections/{key}.md

用法示例：
    >>> from proposal_sections import ProposalSections
    >>> ps = ProposalSections(Path("research_proposals/optimizing/xxx/04_proposal"))
    >>> ps.ensure_split()                              # 自动拆分旧 draft
    >>> rationale = ps.read_section("rationale")       # 读取单章节
    >>> ps.write_section("content", "...")             # 写入单章节
    >>> ps.assemble_draft()                            # 组装完整 draft
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

# NSFC 申请书标准章节定义（与 proposal_lifecycle 解耦，避免循环导入）
PROPOSAL_SECTIONS = [
    {"key": "rationale", "title": "（一）立项依据", "cn": "立项依据", "desc": "科学意义、前人研究局限性"},
    {"key": "content", "title": "（二）研究内容", "cn": "研究内容", "desc": "研究内容、特色与创新点"},
    {"key": "method", "title": "（三）研究方案", "cn": "研究方案", "desc": "技术路线、可行性"},
]


class ProposalSections:
    """管理 proposal 的章节拆分与组装。"""

    # 匹配中文章节标题：## （一）立项依据
    SECTION_HEADER_RE = re.compile(r"^##\s*（[一二三四五六七八九十]+）\s*(.+)$", re.MULTILINE)

    def __init__(self, proposal_dir: Path) -> None:
        """Args:
            proposal_dir: proposal 目录，通常是 {proposal_id}/04_proposal
        """
        self.proposal_dir = Path(proposal_dir)
        self.draft_path = self.proposal_dir / "proposal-draft.md"
        self.sections_dir = self.proposal_dir / "sections"

        # key -> {title, cn, desc}
        self.section_map: Dict[str, Dict[str, str]] = {
            s["key"]: s for s in PROPOSAL_SECTIONS
        }
        # 标题前缀 -> key，用于解析旧 draft
        self.title_to_key: Dict[str, str] = {}
        for s in PROPOSAL_SECTIONS:
            self.title_to_key[s["title"]] = s["key"]
            self.title_to_key[s["cn"]] = s["key"]

    def is_split(self) -> bool:
        """是否已拆分为 sections/ 目录。"""
        return self.sections_dir.exists() and any(
            (self.sections_dir / f"{key}.md").exists() for key in self.section_map
        )

    def read_section(self, key: str) -> str:
        """读取指定章节内容。优先读 sections/{key}.md，否则从 draft 解析。"""
        section_file = self.sections_dir / f"{key}.md"
        if section_file.exists():
            return section_file.read_text(encoding="utf-8")

        # 未拆分或章节文件缺失，从完整 draft 解析
        full_draft = self._read_draft()
        return self._extract_section(full_draft, key)

    def write_section(self, key: str, content: str) -> Path:
        """写入指定章节，并同步更新 proposal-draft.md 汇总视图。"""
        self.sections_dir.mkdir(parents=True, exist_ok=True)
        section_file = self.sections_dir / f"{key}.md"
        section_file.write_text(content, encoding="utf-8")
        self.assemble_draft()
        return section_file

    def ensure_split(self) -> bool:
        """如果尚未拆分，自动将 proposal-draft.md 拆分为 sections/。

        Returns:
            True 表示执行了拆分，False 表示已拆分或没有 draft 可拆
        """
        if self.is_split():
            return False
        if not self.draft_path.exists():
            return False

        full_draft = self.draft_path.read_text(encoding="utf-8")
        self.sections_dir.mkdir(parents=True, exist_ok=True)

        # 解析每个章节并写入
        for key in self.section_map:
            content = self._extract_section(full_draft, key)
            (self.sections_dir / f"{key}.md").write_text(content, encoding="utf-8")

        # 保留原 draft 作为旧备份，重新组装新 draft
        backup = self.proposal_dir / "proposal-draft-merged.md"
        if not backup.exists():
            backup.write_text(full_draft, encoding="utf-8")
        self.assemble_draft()
        return True

    def assemble_draft(self) -> Path:
        """从 sections/ 组装完整 proposal-draft.md。"""
        parts: List[str] = []

        # 1. 读取标题/元信息（从 rationale 文件顶部提取 # 标题和 > 元信息）
        header = self._read_header_from_rationale()
        if header:
            parts.append(header.rstrip())
            parts.append("")
            parts.append("---")
            parts.append("")

        # 2. 按顺序拼接各章节
        for s in PROPOSAL_SECTIONS:
            key = s["key"]
            section_file = self.sections_dir / f"{key}.md"
            if not section_file.exists():
                continue
            content = section_file.read_text(encoding="utf-8").rstrip()
            if content:
                parts.append(content)
                parts.append("")
                parts.append("---")
                parts.append("")

        # 3. 移除末尾多余分隔符
        while parts and parts[-1] in ("", "---"):
            parts.pop()

        draft = "\n".join(parts) + "\n"
        self.draft_path.write_text(draft, encoding="utf-8")
        return self.draft_path

    def section_exists(self, key: str) -> bool:
        """指定章节是否有内容。"""
        return len(self.read_section(key).strip()) > 50

    def list_sections(self) -> List[str]:
        """返回当前已拆分的章节 key 列表。"""
        if not self.is_split():
            return []
        return [
            key for key in self.section_map
            if (self.sections_dir / f"{key}.md").exists()
        ]

    def _read_draft(self) -> str:
        if self.draft_path.exists():
            return self.draft_path.read_text(encoding="utf-8")
        return ""

    def _extract_section(self, full_draft: str, key: str) -> str:
        """从完整 draft 中按中文章节标题提取单个章节。"""
        target = self.section_map.get(key)
        if not target:
            return ""

        title = target["title"]
        # 构造匹配模式：## （一）立项依据
        pattern = re.escape(title)
        match = re.search(rf"^##\s*{pattern}\s*$", full_draft, re.MULTILINE)
        if not match:
            return ""

        start = match.start()
        # 找下一个同格式章节标题
        next_match = None
        for m in self.SECTION_HEADER_RE.finditer(full_draft, match.end()):
            if m.start() > start:
                next_match = m
                break

        end = next_match.start() if next_match else len(full_draft)
        section = full_draft[start:end].strip()
        return section

    def _read_header_from_rationale(self) -> str:
        """从 rationale 章节顶部提取项目标题和元信息。"""
        rationale = self.read_section("rationale")
        if not rationale:
            return ""
        lines = rationale.splitlines()
        header_lines: List[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("# ") or stripped.startswith("> "):
                header_lines.append(line)
            elif stripped == "":
                if header_lines and header_lines[-1].strip() == "":
                    continue
                header_lines.append(line)
            else:
                break
        return "\n".join(header_lines).rstrip()


def _self_check() -> None:
    """简单自检：在临时目录测试拆分与组装。"""
    import tempfile
    import shutil

    tmp = Path(tempfile.mkdtemp(prefix="ps_test_"))
    try:
        draft = tmp / "proposal-draft.md"
        draft.write_text(
            "# 面上项目申请书\n\n"
            "> 项目类型：面上项目\n\n"
            "---\n\n"
            "## （一）立项依据\n\n立项依据内容。\n\n"
            "---\n\n"
            "## （二）研究内容\n\n研究内容。\n\n"
            "---\n\n"
            "## （三）研究方案\n\n研究方案。\n",
            encoding="utf-8",
        )

        ps = ProposalSections(tmp)
        assert not ps.is_split()
        assert ps.ensure_split() is True
        assert ps.is_split()

        rationale = ps.read_section("rationale")
        assert "立项依据" in rationale
        assert "研究内容" not in rationale

        content = ps.read_section("content")
        assert "研究内容" in content
        assert "研究方案" not in content

        # 修改 content 章节，检查 draft 组装
        ps.write_section("content", "## （二）研究内容\n\n更新后的研究内容。\n")
        assembled = ps.draft_path.read_text(encoding="utf-8")
        assert "更新后的研究内容" in assembled
        assert "立项依据内容" in assembled

        print("✓ proposal_sections 自检通过")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    _self_check()
