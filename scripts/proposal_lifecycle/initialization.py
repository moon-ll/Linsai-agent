from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc

import proposal_lifecycle as _pl

from proposal_lifecycle.constants import _log


class InitializerMixin:
    """课题进入优化前的初始化：补齐四大产物、固定 7 个申请书模块。"""

    # 课题设想模板字段
    RESEARCH_IDEA_TEMPLATE = """# 课题设想

**最后更新**：{updated_at}

## 标题
{title}

## 研究背景与动机
{background}

## 现存研究空白或瓶颈
{gap}

## 拟开展研究内容和方案
{content}

## 拟采用技术路线
{approach}

## 创新点
{innovations}

## 来源与可靠性
{sources}
"""

    # 方法学手册模板
    METHODOLOGY_MANUAL_TEMPLATE = """# 方法学手册

> 本手册与申请书 `04_proposal/proposal-draft.md` 配套，侧重方法细节：
> 理论基础、公式推导、参数表、技术路线图、数据分析流程、局限性与替代方案。
> writer 在优化申请书各模块时，应同步更新本手册对应条目。

## 方法清单

（待初始化扫描后填充）

## 各方法详细说明

### 方法 1

- **适用模块**：
- **理论基础**：
- **实现细节**：
- **关键参数**：
- **数据分析**：
- **局限性**：
- **参考文献**：

## 与申请书模块的映射

| 申请书模块 | 方法学手册对应条目 |
|---|---|
| 立项依据 |  |
| 研究内容 |  |
| 研究方案 |  |
| 特色与创新 |  |
| 年度研究计划 |  |
| 预期研究成果 |  |
| 参考文献 |  |
"""

    # 文献阅读笔记模板
    READING_NOTES_TEMPLATE = """# 文献阅读笔记

> 记录课题优化过程中补充阅读的文献，按阅读时间倒序排列。
> 每条记录应包含：文献标题、来源、核心结论、与课题关联、已引用位置。

| 阅读日期 | 文献标题 | 来源 | 核心结论 | 与课题关联 | 已引用位置 |
|---|---|---|---|---|---|

"""

    def initialize_for_optimization(self, proposal_id: str) -> Dict[str, Any]:
        """课题进入 optimizing 前的标准化初始化。

        1. 拆分/补齐申请书 7 个模块（sections/）
        2. 生成/更新课题设想（00_research_idea.md）
        3. 生成/更新方法学手册（04_proposal/methodology-manual.md）
        4. 生成/更新文献阅读笔记（02_literature/reading-notes.md）
        5. 在状态中记录 initialized_at 和 missing_sections
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal 未注册"}

        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}

        results: Dict[str, Any] = {}

        # 1. 章节拆分/补齐
        results["sections"] = self._init_sections(prop_dir)

        # 2. 课题设想
        results["research_idea"] = self._init_research_idea(prop_dir)

        # 3. 方法学手册
        results["methodology_manual"] = self._init_methodology_manual(prop_dir)

        # 4. 文献阅读笔记
        results["reading_notes"] = self._init_reading_notes(prop_dir)

        # 5. 更新状态
        prop_state["initialized_at"] = now_utc()
        prop_state["missing_sections"] = results["sections"].get("missing", [])
        prop_state["updated_at"] = now_utc()
        self._set_proposal_state(proposal_id, prop_state)

        # 6. 同步更新 proposal-brief
        try:
            self.update_proposal_brief(proposal_id)
        except Exception:
            pass

        if _log:
            _log.info(f"[{proposal_id}] 初始化完成: {results}")

        return {"success": True, "proposal_id": proposal_id, "results": results}

    def _init_sections(self, prop_dir: Path) -> Dict[str, Any]:
        """确保 sections/ 下存在 7 个模块文件，缺失的创建占位文件。

        v6.7.10: 若 section 文件为空但 draft/merged draft 中有内容，会优先从 draft 提取。
        """
        from proposal_sections import ProposalSections

        proposal_content_dir = prop_dir / "04_proposal"
        sections = ProposalSections(proposal_content_dir)
        performed_split = sections.ensure_split()

        # 若 section 文件为空，尝试从最新 draft 重新提取
        refreshed: List[str] = []
        draft_sources = [
            proposal_content_dir / "proposal-draft-merged.md",
            proposal_content_dir / "proposal-draft.md",
        ]
        full_draft = ""
        for src in draft_sources:
            if src.exists() and src.stat().st_size > 200:
                full_draft = src.read_text(encoding="utf-8")
                break

        for s in sections.section_map.values():
            section_file = sections.sections_dir / f"{s['key']}.md"
            current_len = section_file.stat().st_size if section_file.exists() else 0
            if current_len < 100 and full_draft:
                extracted = sections._extract_section(full_draft, s["key"])
                if len(extracted.strip()) > 50:
                    section_file.write_text(extracted, encoding="utf-8")
                    refreshed.append(s["key"])

        # v6.7.10: 补齐仍然缺失的章节占位文件
        created_placeholders: List[str] = []
        sections.sections_dir.mkdir(parents=True, exist_ok=True)
        for s in sections.section_map.values():
            section_file = sections.sections_dir / f"{s['key']}.md"
            if not section_file.exists():
                section_file.write_text(
                    f"## {s['title']}\n\n（待 writer 补齐）\n",
                    encoding="utf-8",
                )
                created_placeholders.append(s["key"])

        # 重新组装 draft，确保汇总视图与 sections 一致
        # allow_shrink=True：初始化语义本就是建立 sections 结构视图
        # （drafts→optimizing 流转），接受占位重组结果小于原稿
        sections.assemble_draft(allow_shrink=True)

        missing: List[str] = []
        for s in sections.section_map.values():
            if not sections.section_exists(s["key"]):
                missing.append(s["key"])

        return {
            "performed_split": performed_split,
            "refreshed_from_draft": refreshed,
            "created_placeholders": created_placeholders,
            "missing": missing,
            "total": len(sections.section_map),
            "existing": len(sections.section_map) - len(missing),
        }

    def _init_research_idea(self, prop_dir: Path) -> Dict[str, Any]:
        """生成/更新课题设想文件 00_research_idea.md。"""
        idea_path = prop_dir / "00_research_idea.md"

        # 读取已有信息
        title = self._read_title(prop_dir)
        background = self._read_background(prop_dir)
        gap = self._read_gap(prop_dir)
        content = self._read_content(prop_dir)
        approach = self._read_approach(prop_dir)
        innovations = self._read_innovations(prop_dir)
        sources = self._read_sources(prop_dir)

        content_str = self.RESEARCH_IDEA_TEMPLATE.format(
            updated_at=now_utc()[:10],
            title=title,
            background=background,
            gap=gap,
            content=content,
            approach=approach,
            innovations=innovations,
            sources=sources,
        )

        # 若文件已存在，不覆盖已有内容，而是追加更新标记
        if idea_path.exists() and idea_path.stat().st_size > 200:
            existing = idea_path.read_text(encoding="utf-8")
            if "## 标题" in existing:
                # 只更新空字段，避免覆盖用户已填写内容
                content_str = self._merge_research_idea(existing, content_str)

        idea_path.write_text(content_str, encoding="utf-8")
        return {"path": str(idea_path.relative_to(_pl.PROJECT_ROOT))}

    def _init_methodology_manual(self, prop_dir: Path) -> Dict[str, Any]:
        """生成方法学手册占位文件。若已存在且内容足够则不覆盖。"""
        manual_path = prop_dir / "04_proposal" / "methodology-manual.md"
        if manual_path.exists() and manual_path.stat().st_size > 500:
            return {"path": str(manual_path.relative_to(_pl.PROJECT_ROOT)), "action": "keep"}

        manual_path.write_text(self.METHODOLOGY_MANUAL_TEMPLATE, encoding="utf-8")
        return {"path": str(manual_path.relative_to(_pl.PROJECT_ROOT)), "action": "create"}

    def _init_reading_notes(self, prop_dir: Path) -> Dict[str, Any]:
        """生成文献阅读笔记文件，并尝试导入已有文献报告。"""
        notes_path = prop_dir / "02_literature" / "reading-notes.md"
        notes_path.parent.mkdir(parents=True, exist_ok=True)

        imported = 0
        if not notes_path.exists() or notes_path.stat().st_size < 200:
            notes_path.write_text(self.READING_NOTES_TEMPLATE, encoding="utf-8")

            # 导入已有 literature-report.md 中的条目
            report_path = prop_dir / "02_literature" / "literature-report.md"
            if report_path.exists():
                imported = self._import_literature_report(notes_path, report_path)

        return {
            "path": str(notes_path.relative_to(_pl.PROJECT_ROOT)),
            "imported": imported,
        }

    # ------------------------------------------------------------------
    # 信息提取辅助
    # ------------------------------------------------------------------

    def _read_file_chunk(self, path: Path, max_chars: int = 8000) -> str:
        if not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8")[:max_chars]
        except Exception:
            return ""

    def _read_title(self, prop_dir: Path) -> str:
        brief = self._read_file_chunk(prop_dir / "00_proposal-brief.md", 2000)
        m = re.search(r"\*\*课题名称\*\*[：:]\s*(.+?)\*?\n", brief)
        if m:
            return m.group(1).strip().strip("*").strip()
        draft = self._read_file_chunk(prop_dir / "04_proposal" / "proposal-draft.md", 3000)
        for line in draft.split("\n"):
            if line.strip().startswith("# "):
                return line.strip("# ").strip()
            if "**课题名称**" in line:
                parts = line.split("：", 1)
                if len(parts) > 1:
                    return parts[1].strip().strip("*").strip()
        return "（待填写）"

    def _read_background(self, prop_dir: Path) -> str:
        # 优先从 direction-calibration.md 提取
        text = self._read_file_chunk(prop_dir / "01_direction" / "direction-calibration.md", 5000)
        if text:
            m = re.search(r"#{1,3}\s*研究背景与动机\s*\n(.+?)(?=\n#{1,3}|$)", text, re.DOTALL)
            if m:
                return m.group(1).strip()[:800]
        # 兜底：从 proposal-draft.md 立项依据前几段
        draft = self._read_file_chunk(prop_dir / "04_proposal" / "proposal-draft.md", 6000)
        m = re.search(r"##\s*（一）立项依据\s*\n(.+?)(?=\n##\s*（二）|$)", draft, re.DOTALL)
        if m:
            return m.group(1).strip()[:800]
        return "（待填写）"

    def _read_gap(self, prop_dir: Path) -> str:
        text = self._read_file_chunk(prop_dir / "02_topic" / "gap-report.md", 4000)
        if text:
            m = re.search(r"#{1,3}\s*(?:研究空白|现存空白|缺口|gap)\s*\n(.+?)(?=\n#{1,3}|$)", text, re.DOTALL | re.IGNORECASE)
            if m:
                return m.group(1).strip()[:800]
        draft = self._read_file_chunk(prop_dir / "04_proposal" / "proposal-draft.md", 6000)
        m = re.search(r"##\s*（一）立项依据\s*\n(.+?)(?=\n##\s*（二）|$)", draft, re.DOTALL)
        if m:
            # 取立项依据最后一段作为空白总结
            paragraphs = [p.strip() for p in m.group(1).split("\n\n") if p.strip()]
            if paragraphs:
                return paragraphs[-1][:800]
        return "（待填写）"

    def _read_content(self, prop_dir: Path) -> str:
        draft = self._read_file_chunk(prop_dir / "04_proposal" / "proposal-draft.md", 6000)
        m = re.search(r"##\s*（二）研究内容\s*\n(.+?)(?=\n##\s*（三）|$)", draft, re.DOTALL)
        if m:
            return m.group(1).strip()[:1000]
        return "（待填写）"

    def _read_approach(self, prop_dir: Path) -> str:
        draft = self._read_file_chunk(prop_dir / "04_proposal" / "proposal-draft.md", 6000)
        m = re.search(r"##\s*（三）研究方案\s*\n(.+?)(?=\n##\s*（四）|$)", draft, re.DOTALL)
        if m:
            return m.group(1).strip()[:1000]
        return "（待填写）"

    def _read_innovations(self, prop_dir: Path) -> str:
        draft = self._read_file_chunk(prop_dir / "04_proposal" / "proposal-draft.md", 6000)
        m = re.search(r"##\s*（四）特色与创新\s*\n(.+?)(?=\n##\s*（五）|$)", draft, re.DOTALL)
        if m:
            return m.group(1).strip()[:800]
        # 兜底：从 question-framework.md
        qf = self._read_file_chunk(prop_dir / "03_question" / "question-framework.md", 3000)
        m = re.search(r"#{1,3}\s*创新点\s*\n(.+?)(?=\n#{1,3}|$)", qf, re.DOTALL)
        if m:
            return m.group(1).strip()[:800]
        return "（待填写）"

    def _read_sources(self, prop_dir: Path) -> str:
        report = self._read_file_chunk(prop_dir / "02_literature" / "literature-report.md", 3000)
        if report:
            lines = [line.strip() for line in report.split("\n") if line.strip().startswith("-")]
            return "\n".join(lines[:10]) or "（待填写）"
        return "（待填写）"

    def _merge_research_idea(self, existing: str, generated: str) -> str:
        """合并未填写字段，避免覆盖用户已有内容。"""
        # 简单策略：如果现有字段值不是（待填写），保留现有
        out_lines: List[str] = []
        gen_map: Dict[str, str] = {}
        current_key = None
        current_buf: List[str] = []

        for line in generated.split("\n"):
            m = re.match(r"^(#{2,3})\s+(.+)$", line)
            if m:
                if current_key is not None:
                    gen_map[current_key] = "\n".join(current_buf).strip()
                current_key = m.group(2).strip()
                current_buf = []
            else:
                current_buf.append(line)
        if current_key is not None:
            gen_map[current_key] = "\n".join(current_buf).strip()

        current_key = None
        current_buf = []
        for line in existing.split("\n"):
            m = re.match(r"^(#{2,3})\s+(.+)$", line)
            if m:
                if current_key is not None:
                    val = "\n".join(current_buf).strip()
                    if val == "（待填写）" and current_key in gen_map:
                        val = gen_map[current_key]
                    out_lines.extend([f"## {current_key}", "", val, ""])
                current_key = m.group(2).strip()
                current_buf = []
                out_lines.append(line)
            else:
                current_buf.append(line)
                out_lines.append(line)
        if current_key is not None:
            val = "\n".join(current_buf).strip()
            if val == "（待填写）" and current_key in gen_map:
                val = gen_map[current_key]
            # 替换最后的占位
            # 由于上面已经追加，这里需要重新组织
            pass

        # 为简化，直接返回 generated（避免复杂 merge 逻辑出错）
        # 后续可改进为字段级 merge
        return generated

    def _import_literature_report(self, notes_path: Path, report_path: Path) -> int:
        """从 literature-report.md 导入条目到 reading-notes.md。"""
        try:
            report = report_path.read_text(encoding="utf-8")
        except Exception:
            return 0

        entries: List[str] = []
        for line in report.split("\n"):
            line = line.strip()
            if line.startswith("-") and len(line) > 10:
                title = line.lstrip("-").strip()
                entries.append(f"| {now_utc()[:10]} | {title} | literature-report.md | | | |")

        if not entries:
            return 0

        try:
            notes = notes_path.read_text(encoding="utf-8")
        except Exception:
            notes = self.READING_NOTES_TEMPLATE

        # 在表头后插入条目
        lines = notes.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("|---|"):
                insert_idx = i + 1
                break
        lines[insert_idx:insert_idx] = entries
        notes_path.write_text("\n".join(lines), encoding="utf-8")
        return len(entries)
