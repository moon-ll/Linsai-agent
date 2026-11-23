#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kb_fill_wiki_notes.py — 将 hermes 深度分析 JSON 转换为 wiki/papers/ 5 维度阅读笔记

用途：
    扫描 hermes 深度分析 JSON 目录与 LinSai-CoPilot 知识库 wiki/papers/ 目录，
    找出尚未生成 wiki 笔记的深度分析，并按照统一的 5 维度格式补齐笔记。

5 维度映射（从深度分析 JSON 字段提取）：
    - 研究问题（Research Question）   ← why_notable / why_notable_text
    - 研究背景（Background）          ← linsai_connection
    - 研究方法（Methods）             ← new_methods
    - 主要发现与核心结论（Main Results）← core_findings
    - 潜在研究方向（Future Directions）← what_next

用法示例：
    # 预览（不写入文件）
    python3 kb_fill_wiki_notes.py --dry-run

    # 实际写入
    python3 kb_fill_wiki_notes.py --apply

约束：
    - 仅使用 Python 标准库（json, pathlib, re, os, datetime, sys）
    - PROJECT_ROOT 硬编码为 /Users/ll/Desktop/LinSai-CoPilot
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ===========================================================================
# 路径常量
# ===========================================================================

PROJECT_ROOT = Path("/Users/ll/Desktop/LinSai-CoPilot")

# hermes 深度分析 JSON 目录
DEEP_ANALYSIS_DIR = Path.home() / "Desktop" / "hermes_workspace" / "knowledge_base" / "AI_wiki" / "briefings"

# wiki 笔记输出目录
WIKI_PAPERS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "papers"

# raw 论文目录（用于关联 source_raw）
RAW_PAPERS_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"

# 未涉及此维度的占位文本
PLACEHOLDER = "（深度分析中未涉及此维度）"


# ===========================================================================
# 辅助函数
# ===========================================================================

def now_iso() -> str:
    """返回当前 UTC ISO 时间戳。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_arxiv_id_from_json(filename: str) -> str:
    """从 deep_analysis_XXXX.XXXXX.json 提取 arxiv_id。"""
    m = re.match(r"deep_analysis_(.+)\.json$", filename)
    return m.group(1) if m else ""


def load_json(path: Path) -> dict:
    """安全加载 JSON 文件。"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_authors(raw) -> list:
    """
    将 authors 字段统一为列表。
    支持字符串（逗号分隔）和列表两种输入。
    """
    if isinstance(raw, list):
        return [a.strip() for a in raw if a and a.strip()]
    if isinstance(raw, str):
        # 按逗号或分号分割，去掉机构括号信息
        parts = re.split(r"[,;，；]", raw)
        return [p.strip() for p in parts if p and p.strip()]
    return []


def find_raw_file(arxiv_id: str) -> str:
    """
    在 raw/papers/ 中根据 arxiv_id 查找对应的 raw 文件名。
    raw 文件命名格式: {YEAR}-{ARXIV_ID}-{slug}.md
    返回相对路径（相对于 knowledge/），如 raw/papers/2025-2503.04335-xxx.md
    找不到则返回空字符串。
    """
    if not RAW_PAPERS_DIR.exists():
        return ""
    for f in RAW_PAPERS_DIR.iterdir():
        if not f.is_file() or not f.name.endswith(".md"):
            continue
        # 文件名中包含该 arxiv_id（注意避免子串误匹配，用边界检查）
        if f"-{arxiv_id}-" in f.name:
            return f"raw/papers/{f.name}"
    return ""


def format_list_field(items) -> str:
    """将列表字段格式化为 Markdown 无序列表。"""
    if isinstance(items, list):
        if not items:
            return PLACEHOLDER
        lines = []
        for item in items:
            text = item.strip() if isinstance(item, str) else str(item)
            if text:
                lines.append(f"- {text}")
        return "\n".join(lines) if lines else PLACEHOLDER
    if isinstance(items, str) and items.strip():
        return items.strip()
    return PLACEHOLDER


def format_text_field(text) -> str:
    """将文本字段格式化为段落。"""
    if isinstance(text, str) and text.strip():
        return text.strip()
    return PLACEHOLDER


def combine_text(*fields) -> str:
    """合并多个文本字段，跳过空值。"""
    parts = []
    for f in fields:
        if isinstance(f, str) and f.strip():
            parts.append(f.strip())
    return "\n\n".join(parts) if parts else PLACEHOLDER


# ===========================================================================
# 核心逻辑：从 JSON 生成笔记内容
# ===========================================================================

def build_note_content(data: dict, arxiv_id: str) -> str:
    """根据深度分析 JSON 构建 5 维度 wiki 笔记的完整 Markdown 内容。"""

    title = data.get("title", arxiv_id)
    authors = normalize_authors(data.get("authors"))
    direction = data.get("direction", "")
    timestamp = now_iso()

    # source_raw 关联
    source_raw = find_raw_file(arxiv_id)

    # 提取 5 个维度
    # 1. 研究问题 ← why_notable (+ why_notable_text)
    why_notable = data.get("why_notable", "")
    why_notable_text = data.get("why_notable_text", "")
    rq_content = combine_text(why_notable, why_notable_text)

    # 2. 研究背景 ← linsai_connection
    linsai_conn = data.get("linsai_connection", "")
    bg_content = format_text_field(linsai_conn)

    # 3. 研究方法 ← new_methods
    methods_content = format_list_field(data.get("new_methods"))

    # 4. 主要发现与核心结论 ← core_findings
    findings_content = format_list_field(data.get("core_findings"))

    # 5. 潜在研究方向 ← what_next
    future_content = format_list_field(data.get("what_next"))

    # 构建 frontmatter
    authors_yaml = json.dumps(authors, ensure_ascii=False) if authors else "[]"

    frontmatter = f"""---
title: "{title}"
type: "paper"
created: "{timestamp}"
updated: "{timestamp}"
tags: []
related: []
source_raw: "{source_raw}"
growth_stage: "growing"
confidence: 0.85
arxiv_id: "{arxiv_id}"
project: []
authors: {authors_yaml}
read_status: "deep_read"
used_by_proposals: []
direction: "{direction}"
note_format: "5-dimension"
note_source: "从 hermes 深度分析转换"
---"""

    # 构建正文
    body = f"""# {title}

**arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id}){f' | **方向**: {direction}' if direction else ''}

---

## 研究问题（Research Question）

{rq_content}

## 研究背景（Background）

{bg_content}

## 研究方法（Methods）

{methods_content}

## 主要发现与核心结论（Main Results）

{findings_content}

## 潜在研究方向（Future Directions）

{future_content}


<!-- linsai-wikilinks -->
## 关联概念

_暂无关联概念_
<!-- /linsai-wikilinks -->
"""

    return frontmatter + "\n\n" + body


# ===========================================================================
# 扫描与对比
# ===========================================================================

def scan_deep_analysis() -> dict:
    """
    扫描深度分析目录，返回 {arxiv_id: json_path} 字典。
    """
    result = {}
    if not DEEP_ANALYSIS_DIR.exists():
        print(f"✗ 深度分析目录不存在: {DEEP_ANALYSIS_DIR}")
        return result
    for f in sorted(DEEP_ANALYSIS_DIR.iterdir()):
        if f.is_file() and f.name.startswith("deep_analysis_") and f.name.endswith(".json"):
            aid = extract_arxiv_id_from_json(f.name)
            if aid:
                result[aid] = f
    return result


def scan_wiki_papers() -> set:
    """
    扫描 wiki/papers/ 目录，返回已有笔记的 arxiv_id 集合。
    笔记文件名格式: {arxiv_id}.md（顶层目录，排除 .backup/）
    """
    result = set()
    if not WIKI_PAPERS_DIR.exists():
        print(f"✗ wiki/papers 目录不存在: {WIKI_PAPERS_DIR}")
        return result
    for f in WIKI_PAPERS_DIR.iterdir():
        if f.is_file() and f.name.endswith(".md"):
            aid = f.stem  # 文件名去掉 .md
            result.add(aid)
    return result


def find_missing() -> list:
    """
    找出缺失的笔记，返回 [(arxiv_id, json_path), ...] 列表。
    """
    deep = scan_deep_analysis()
    existing = scan_wiki_papers()

    missing = []
    for aid, jpath in deep.items():
        if aid not in existing:
            missing.append((aid, jpath))

    # 按 arxiv_id 排序
    missing.sort(key=lambda x: x[0])
    return missing


# ===========================================================================
# 主流程
# ===========================================================================

def main():
    # 解析参数
    dry_run = "--dry-run" in sys.argv
    apply_mode = "--apply" in sys.argv

    if not dry_run and not apply_mode:
        print("用法: python3 kb_fill_wiki_notes.py --dry-run | --apply")
        print()
        print("  --dry-run   预览将要补齐的笔记（不写入文件）")
        print("  --apply     实际写入笔记文件")
        sys.exit(0)

    print("=" * 70)
    print("kb_fill_wiki_notes — wiki/papers 5 维度笔记补齐工具")
    print("=" * 70)
    print()

    # 扫描
    deep = scan_deep_analysis()
    existing = scan_wiki_papers()
    print(f"○ 深度分析 JSON 总数: {len(deep)}")
    print(f"○ 已有 wiki 笔记总数: {len(existing)}")
    print()

    missing = find_missing()
    print(f"⚠ 缺失笔记数: {len(missing)}")
    print()

    if not missing:
        print("✓ 所有深度分析 JSON 均已有对应 wiki 笔记，无需补齐。")
        return

    # 统计 source_raw 关联情况
    raw_linked = 0
    raw_missing = 0
    for aid, _ in missing:
        if find_raw_file(aid):
            raw_linked += 1
        else:
            raw_missing += 1

    mode_label = "预览（dry-run）" if dry_run else "写入（apply）"
    print(f"○ 运行模式: {mode_label}")
    print(f"○ source_raw 已关联: {raw_linked}，未找到 raw 文件: {raw_missing}")
    print()
    print("-" * 70)

    # 逐个处理
    success = 0
    failed = 0
    for aid, jpath in missing:
        try:
            data = load_json(jpath)
            content = build_note_content(data, aid)
            out_path = WIKI_PAPERS_DIR / f"{aid}.md"
            source_raw = find_raw_file(aid)

            # 输出状态
            raw_tag = "✓" if source_raw else "○"
            print(f"  {raw_tag} {aid}  {data.get('title', '?')[:60]}")

            if dry_run:
                # dry-run 模式：仅打印文件名和前几行
                print(f"      → 将写入: {out_path.name}")
                print(f"      → source_raw: {source_raw or '(未找到)'}")
                success += 1
            else:
                # apply 模式：实际写入
                WIKI_PAPERS_DIR.mkdir(parents=True, exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"      → 已写入: {out_path.name}")
                success += 1

        except Exception as e:
            print(f"  ✗ {aid}  处理失败: {e}")
            failed += 1

    print("-" * 70)
    print()
    print(f"{'✓' if failed == 0 else '⚠'} 完成：成功 {success}，失败 {failed}")
    if dry_run:
        print("  （dry-run 模式，未实际写入。使用 --apply 执行写入。）")
    else:
        print(f"  （已写入 {success} 篇笔记到 {WIKI_PAPERS_DIR}）")


if __name__ == "__main__":
    main()
