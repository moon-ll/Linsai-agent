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
# v6.8.0: 申请书模块重划
# - 合并研究方案/特色与创新/预期研究成果为 scheme 模块
# - 去掉年度研究计划
# - references 作为一致性审查后的独立检验模块
PROPOSAL_SECTIONS = [
    {"key": "rationale", "title": "（一）立项依据", "cn": "立项依据", "desc": "科学意义、前人研究局限性"},
    {"key": "content", "title": "（二）研究内容", "cn": "研究内容", "desc": "研究内容、科学目标、关键问题"},
    {"key": "scheme", "title": "（三）研究方案、特色与创新、预期研究成果", "cn": "研究方案", "desc": "技术路线、可行性、创新点、预期成果"},
    {"key": "full_review", "title": "整体一致性审查", "cn": "整体一致性", "desc": "跨模块衔接与连贯性"},
    {"key": "references", "title": "参考文献检验", "cn": "参考文献", "desc": "引文准确性、相关性与格式"},
]

# 章节 key 列表（常用遍历）
SECTION_KEYS = [s["key"] for s in PROPOSAL_SECTIONS]
SECTION_TITLES = [s["title"] for s in PROPOSAL_SECTIONS]

# ---------------------------------------------------------------------------
# v7.3.0: 方法手册（method_manual）——第六个**评审**模块。
#
# 用户裁决（2026-11-02）：课题产出的目的是"提供可以开展的课题"，研究方法
# 手册的详细程度与完整度决定课题能否正式开工。故手册从轮末 derived 维护步
# 升级为正式评审模块，进入对抗评审 / section_passes / 晋级 / 验收判据。
#
# 边界：手册**不是申请书正文**——产物在 03_method/method-manual.md（唯一
# 真相源，update_method_manual 体系维护），不进 04_proposal/sections/，
# 也不参与 proposal-draft 组装与 ProposalSections 文件机制。因此
# PROPOSAL_SECTIONS（申请书正文 5 模块）保持不变，评审侧用 REVIEW_SECTION_KEYS。
MANUAL_SECTION_KEY = "method_manual"
MANUAL_SECTION_META = {
    "key": MANUAL_SECTION_KEY,
    "title": "研究方法手册（开工就绪度）",
    "cn": "方法手册",
    "desc": "八要素方法单元、参数可复算、协议可执行、溯源闭环（L0-L4 就绪度）",
}

# 评审模块全集 = 申请书正文 5 模块 + 方法手册（completion 达标门 / dossier 判据口径）
REVIEW_SECTION_KEYS = SECTION_KEYS + [MANUAL_SECTION_KEY]

# 幽灵写入防护阈值（v6.9.54）：拼接结果低于此字节数且将覆盖显著更大的
# 已有草稿时拒绝写入（正常五模块占位重组约 450B，不受影响）
MIN_ASSEMBLED_DRAFT_BYTES = 500


class ProposalSections:
    """管理 proposal 的章节拆分与组装。"""

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
        # v6.7.10: 同时兼容 （一）/一、/节 1： 等常见编号前缀
        self.title_to_key: Dict[str, str] = {}
        cn_nums = ["一", "二", "三", "四", "五", "六", "七"]
        for idx, s in enumerate(PROPOSAL_SECTIONS):
            self.title_to_key[s["title"]] = s["key"]
            self.title_to_key[s["cn"]] = s["key"]
            # 添加别名：一、立项依据 / 节 1：立项依据 / 1. 立项依据
            self.title_to_key[f"{cn_nums[idx]}、{s['cn']}"] = s["key"]
            self.title_to_key[f"节 {idx + 1}：{s['cn']}"] = s["key"]
            self.title_to_key[f"节 {idx+1}：{s['cn']}"] = s["key"]
            self.title_to_key[f"{idx + 1}. {s['cn']}"] = s["key"]
            self.title_to_key[f"{idx + 1}、{s['cn']}"] = s["key"]

        # v6.7.10: 添加 writer agent 常用的非标准标题别名（用于解析旧 draft）
        extra_aliases: Dict[str, List[str]] = {
            "rationale": [
                "科学意义与研究价值", "国内外研究现状及发展动态分析",
                "国内外研究现状", "研究背景与科学意义", "研究背景与意义",
                "项目背景", "立项依据与研究意义",
            ],
            "content": [
                "关键科学问题凝练", "研究内容与研究目标",
                "拟解决的关键科学问题", "研究目标与内容", "关键科学问题",
            ],
            "scheme": [
                "技术路线", "研究思路", "实施方案", "总体技术路线",
                "研究方法与技术路线",
                "发展新方法的重要性和必要性", "创新点", "方法学创新",
                "研究特色与创新点", "特色创新", "创新性",
                "预期成果", "预期研究目标", "研究成果", "预期研究产出",
            ],
            "references": [
                "参考文献", "引文列表", "文献目录", "参考文献目录",
            ],
        }
        for key, aliases in extra_aliases.items():
            for alias in aliases:
                self.title_to_key[alias] = key
                # v6.7.10: 为每个别名添加所有可能编号前缀（1-7），
                # 因为 writer 可能用节 3 表示研究内容、节 4 表示创新等
                for n in range(1, 8):
                    self.title_to_key[f"{cn_nums[n-1]}、{alias}"] = key
                    self.title_to_key[f"节 {n}：{alias}"] = key
                    self.title_to_key[f"{n}. {alias}"] = key
                    self.title_to_key[f"{n}、{alias}"] = key

        # 构建章节标题边界正则：匹配 ## 后接任意已知标题（长标题优先，避免子串误匹配）
        # 允许标题后带括号说明，如 "节 3：关键科学问题凝练（申请书级深度）"
        sorted_titles = sorted(self.title_to_key.keys(), key=len, reverse=True)
        titles_pattern = "|".join(re.escape(t) for t in sorted_titles)
        self.section_header_re = re.compile(
            rf"^##\s*(?:{titles_pattern})(?:\s*[（(][^）)]*[）)])?\s*$", re.MULTILINE
        )

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

        v6.7.10: 兼容旧 3 章格式；对新增 4 个模块（特色与创新/年度计划/预期成果/参考文献）
        若 draft 中不存在，则创建占位文件，便于后续 writer 补齐。

        Returns:
            True 表示执行了拆分，False 表示已拆分或没有 draft 可拆
        """
        if self.is_split():
            return False
        if not self.draft_path.exists():
            return False

        full_draft = self.draft_path.read_text(encoding="utf-8")
        self.sections_dir.mkdir(parents=True, exist_ok=True)

        # 解析每个章节并写入；旧 draft 中不存在的章节创建空占位文件
        for key in self.section_map:
            content = self._extract_section(full_draft, key)
            (self.sections_dir / f"{key}.md").write_text(content, encoding="utf-8")

        # 保留原 draft 作为旧备份，重新组装新 draft
        backup = self.proposal_dir / "proposal-draft-merged.md"
        if not backup.exists():
            backup.write_text(full_draft, encoding="utf-8")
        self.assemble_draft()
        return True

    def assemble_draft(self, allow_shrink: bool = False) -> Path:
        """从 sections/ 组装完整 proposal-draft.md。

        v6.9.54 幽灵写入防护：拼接结果过小且将覆盖显著更大的已有草稿时
        抛 ValueError（此前该防护从未落地——守护测试 test_ghost_write_guard
        因 import 错误自写下第一天起就被静默吞掉，从未运行过）。初始化
        等明确接受重置语义的调用方传 allow_shrink=True 豁免。

        Args:
            allow_shrink: True 时允许小结果覆盖已有草稿（初始化语义）。
        """
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

        # 4. 幽灵写入防护（v6.9.54）：空/残缺 sections 拼出的小结果
        #    不得覆盖已有的大草稿（v6.8.10 时代实测：1 字节文件覆盖 73KB 申请书）
        draft_bytes = len(draft.encode("utf-8"))
        if (not allow_shrink and draft_bytes < MIN_ASSEMBLED_DRAFT_BYTES
                and self.draft_path.exists()):
            existing = self.draft_path.stat().st_size
            if existing > max(MIN_ASSEMBLED_DRAFT_BYTES, draft_bytes * 2):
                raise ValueError(
                    f"拼接结果过小（{draft_bytes} 字节）将覆盖 {existing} 字节的现有草稿，"
                    "疑似幽灵写入（sections 空/残缺），已拒绝写入"
                )

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
        """从完整 draft 中按中文章节标题提取单个章节。

        v6.7.10: 兼容标准标题（一）立项依据 和别名（一、立项依据 / 节 1：立项依据 等）。
        """
        target = self.section_map.get(key)
        if not target:
            return ""

        # 收集该章节所有可能标题（标准 + 别名），按长度降序避免子串误匹配
        titles = [t for t, k in self.title_to_key.items() if k == key]
        titles.sort(key=len, reverse=True)

        match = None
        for title in titles:
            pattern = re.escape(title)
            # 允许标题后带括号说明
            m = re.search(
                rf"^##\s*{pattern}(?:\s*[（(][^）)]*[）)])?\s*$",
                full_draft, re.MULTILINE
            )
            if m:
                match = m
                break
        if not match:
            return ""

        start = match.start()
        # 找下一个已知章节标题作为边界
        next_match = None
        for m in self.section_header_re.finditer(full_draft, match.end()):
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
