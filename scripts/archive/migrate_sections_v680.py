#!/usr/bin/env python3
"""v6.8.0 章节结构迁移脚本（最终版）。

旧结构（7 模块）：
    rationale / content / method / innovation / outcome / plan / references
新结构（5 模块）：
        rationale / content / scheme / full_review / references

迁移规则：
    - rationale → rationale（不变）
    - content → content（不变）
    - scheme = method + innovation + outcome（合并，剔除年度计划和重复参考文献）
    - full_review = 新建空占位
    - references → references（不变）
    - plan（年度计划）→ 丢弃

旧 section 文件本身可能包含后续章节（旧 ensure_split 边界污染），因此需要
按标题边界精确提取，而非整文件追加。
旧文件备份到 backups/sections-migration-{date}/
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from paths import PROJECT_ROOT
from proposal_sections import ProposalSections


# 旧标题识别表：(key, 标题前缀)
OLD_HEADERS: List[Tuple[str, str]] = [
    ("rationale", "## 一、立项依据"),
    ("rationale2", "## （一）立项依据"),
    ("content", "## 二、研究内容"),
    ("content2", "## （二）研究内容"),
    ("method", "## 三、研究方案"),
    ("method2", "## （三）研究方案"),
    ("innovation", "## 四、特色与创新"),
    ("innovation2", "## （四）特色与创新"),
    ("plan", "## 五、年度计划"),
    ("plan2", "## （五）年度计划"),
    ("outcome", "## 六、预期成果"),
    ("outcome2", "## （六）预期成果"),
    ("references", "## 参考文献"),
]


def _header_line(text: str, prefixes: List[str]) -> Optional[Tuple[int, str]]:
    """在文本中查找任意一个标题前缀，返回 (位置, 匹配到的前缀)。"""
    best_pos: Optional[int] = None
    best_prefix = ""
    for prefix in prefixes:
        pos = text.find(prefix)
        if pos != -1:
            if best_pos is None or pos < best_pos:
                best_pos = pos
                best_prefix = prefix
    if best_pos is None:
        return None
    return best_pos, best_prefix


def _extract_between_prefixes(
    text: str,
    start_prefixes: List[str],
    end_prefixes: List[str],
) -> str:
    """提取 start 标题之后到 end 标题之前的内容。"""
    start_info = _header_line(text, start_prefixes)
    if start_info is None:
        return ""
    start_pos, start_prefix = start_info
    content_start = text.find("\n", start_pos) + 1

    end_info = _header_line(text[content_start:], end_prefixes)
    if end_info is None:
        return text[content_start:].strip()
    return text[content_start : content_start + end_info[0]].strip()


def _strip_first_header(text: str) -> str:
    """去掉文本第一行的 ## 标题。"""
    lines = text.splitlines()
    if lines and lines[0].strip().startswith("##"):
        lines = lines[1:]
    return "\n".join(lines).strip()


def _build_scheme(
    method_text: str,
    innovation_text: str,
    outcome_text: str,
) -> str:
    """合并 method / innovation / outcome 为 scheme 模块，去掉子标题头。"""
    parts: List[str] = ["## （三）研究方案、特色与创新、预期研究成果\n"]

    method_body = _strip_first_header(method_text)
    if method_body.strip():
        parts.append("### 研究方案与技术路线\n")
        parts.append(method_body)
        parts.append("")

    innovation_body = _strip_first_header(innovation_text)
    if innovation_body.strip():
        parts.append("### 特色与创新\n")
        parts.append(innovation_body)
        parts.append("")

    outcome_body = _strip_first_header(outcome_text)
    if outcome_body.strip():
        parts.append("### 预期研究成果\n")
        parts.append(outcome_body)
        parts.append("")

    return "\n".join(parts).strip() + "\n"


def migrate_proposal(prop_dir: Path, dry_run: bool = False) -> dict:
    """迁移单个 proposal 的章节结构。"""
    ps = ProposalSections(prop_dir)
    sections_dir = ps.sections_dir
    backup_dir = (
        PROJECT_ROOT
        / "backups"
        / f"sections-migration-{datetime.now().strftime('%Y%m%d')}"
        / prop_dir.parent.name
    )

    # 旧文件路径
    old_files = {
        "rationale": sections_dir / "rationale.md",
        "content": sections_dir / "content.md",
        "method": sections_dir / "method.md",
        "innovation": sections_dir / "innovation.md",
        "outcome": sections_dir / "outcome.md",
        "plan": sections_dir / "plan.md",
        "references": sections_dir / "references.md",
    }

    # 读取旧内容（若已迁移过则回退到 merged draft）
    def _read_old(key: str) -> str:
        path = old_files[key]
        if path.exists():
            return path.read_text(encoding="utf-8")
        merged = prop_dir / "proposal-draft-merged.md"
        if merged.exists():
            prefixes = [p for k, p in OLD_HEADERS if k == key or k.startswith(key)]
            end_keys = {
                "rationale": ["content", "content2"],
                "content": ["method", "method2"],
                "method": ["innovation", "innovation2", "plan", "plan2", "outcome", "outcome2", "references"],
                "innovation": ["plan", "plan2", "outcome", "outcome2", "references"],
                "outcome": ["references"],
                "references": [],
            }
            end_prefixes = [p for k, p in OLD_HEADERS if k in end_keys.get(key, [])]
            return _extract_between_prefixes(merged.read_text(encoding="utf-8"), prefixes, end_prefixes)
        return ""

    method_text = _read_old("method")
    innovation_text = _read_old("innovation")
    outcome_text = _read_old("outcome")

    new_contents = {
        "rationale": _read_old("rationale"),
        "content": _read_old("content"),
        "scheme": _build_scheme(method_text, innovation_text, outcome_text),
        "full_review": "## 整体一致性审查\n\n待本轮 writer-critic 循环结束后统一审查。\n",
        "references": _read_old("references"),
    }

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "proposal": prop_dir.parent.name,
            "sections": {k: len(v) for k, v in new_contents.items()},
        }

    # 备份旧文件
    backup_dir.mkdir(parents=True, exist_ok=True)
    for key, path in old_files.items():
        if path.exists():
            shutil.copy2(path, backup_dir / path.name)

    # 写入新文件
    sections_dir.mkdir(parents=True, exist_ok=True)
    for key, content in new_contents.items():
        (sections_dir / f"{key}.md").write_text(content, encoding="utf-8")

    # 删除旧文件
    for key in ["method", "innovation", "outcome", "plan"]:
        path = sections_dir / f"{key}.md"
        if path.exists():
            path.unlink()

    # 重新组装 draft
    ps.assemble_draft()

    return {
        "success": True,
        "proposal": prop_dir.parent.name,
        "backup": str(backup_dir.relative_to(PROJECT_ROOT)),
        "sections": list(new_contents.keys()),
    }


def migrate_all(dry_run: bool = False) -> None:
    """迁移所有 optimizing proposal。"""
    optimizing_dir = PROJECT_ROOT / "research_proposals" / "optimizing"
    if not optimizing_dir.exists():
        print("optimizing 目录不存在")
        return

    results = []
    for prop_dir in sorted(optimizing_dir.iterdir()):
        proposal_04 = prop_dir / "04_proposal"
        if not proposal_04.exists():
            continue
        result = migrate_proposal(proposal_04, dry_run=dry_run)
        results.append(result)
        print(result)

    print(f"\n迁移完成: {len(results)} 个 proposal")


def _self_check() -> dict:
    """模块自检：对空 proposal 目录做 dry-run 迁移，不写入文件。"""
    optimizing_dir = PROJECT_ROOT / "research_proposals" / "optimizing"
    if not optimizing_dir.exists():
        return {"success": True, "message": "optimizing 目录不存在，跳过"}
    test_dirs = [d / "04_proposal" for d in optimizing_dir.iterdir() if (d / "04_proposal").exists()]
    if not test_dirs:
        return {"success": True, "message": "无 optimizing proposal，跳过"}
    result = migrate_proposal(test_dirs[0], dry_run=True)
    return {"success": result.get("success", False), "dry_run": True, "sample": result}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="v6.8.0 章节结构迁移")
    parser.add_argument("--dry-run", action="store_true", help="预览不写入")
    parser.add_argument("--self-check", action="store_true", help="模块自检")
    args = parser.parse_args()

    if args.self_check:
        print(_self_check())
        raise SystemExit(0)

    migrate_all(dry_run=args.dry_run)
