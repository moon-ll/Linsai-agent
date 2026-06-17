#!/usr/bin/env python3
"""产出导入转换器 —— 把 hermes 的文献产出导入林赛知识库。

用途：
    将 hermes 每日文献简报系统的产出（daily_candidates.json / deep_analysis_*.json）
    转换为林赛知识库的标准格式，沉淀到「文献简报」子库。

数据流：
    hermes 产出（~/Desktop/hermes_workspace/knowledge_base/AI_wiki/briefings/）
        ↓ 导入
    林赛知识库
        ├─ raw/papers/{year}-{arxiv_id}-{slug}.md  （候选论文）
        └─ wiki/projects/文献简报/{title}.md        （深度解析）

字段映射（已验证对齐）：
    hermes 字段        →  林赛字段
    arxiv_id           →  frontmatter.arxiv_id
    title/authors/date →  frontmatter.title/authors/year
    tldr/abstract      →  正文摘要
    why_notable        →  ## 为什么值得关注
    core_findings      →  ## 核心发现
    linsai_connection  →  ## 林赛的理解
    what_next          →  ## 开放问题

用法示例：
    >>> from kb_importer import import_candidate, import_deep_analysis
    >>> import_candidate('2403.15337')        # 导入单篇候选
    >>> import_deep_analysis('2403.15337')     # 导入深度解析到子库 wiki
    >>> import_all_candidates()                # 批量导入当日全部候选

规范：
    - 仅使用 Python 3 标准库
    - 头部包含中文 docstring
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 输出使用中文，状态图标统一
    - 所有导入的文件带 project: ["文献简报"] frontmatter，纳入子库检索
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
RAW_PAPERS_DIR = KNOWLEDGE_DIR / "raw" / "papers"
WIKI_PROJECTS_DIR = KNOWLEDGE_DIR / "wiki" / "projects" / "文献简报"
PROJECT_TAG = "文献简报"

# hermes 简报产出目录
HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
BRIEFINGS_DIR = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings"


def _now_utc() -> str:
    """返回 UTC ISO 时间戳。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugify(text: str, max_len: int = 50) -> str:
    """将标题转为文件名安全的 slug。"""
    # 保留中英文字母数字，其余替换为连字符
    slug = re.sub(r"[^\w\u4e00-\u9fff\-]", "-", text.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug[:max_len]


def _extract_year(date_str: str) -> str:
    """从日期字符串提取年份（如 '2024-03' → '2024'）。"""
    m = re.match(r"(\d{4})", date_str or "")
    return m.group(1) if m else str(datetime.now().year)


def _load_candidates() -> Dict[str, Any]:
    """加载 daily_candidates.json。"""
    path = BRIEFINGS_DIR / "daily_candidates.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_deep_analysis(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """加载指定论文的深度解析。"""
    path = BRIEFINGS_DIR / f"deep_analysis_{arxiv_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _find_candidate(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """从 daily_candidates 中查找指定论文。"""
    data = _load_candidates()
    for p in data.get("papers", []):
        if p.get("arxiv_id") == arxiv_id:
            return p
    return None


def import_candidate(arxiv_id: str, project: str = PROJECT_TAG) -> Optional[str]:
    """导入单篇候选论文到 raw/papers/。

    Args:
        arxiv_id: arXiv 论文 ID（如 '2403.15337'）
        project: 归属项目标签（默认「文献简报」）

    Returns:
        生成的文件相对路径；未找到候选返回 None。
    """
    candidate = _find_candidate(arxiv_id)
    if not candidate:
        print(f"○ 未找到候选论文: {arxiv_id}")
        return None

    title = candidate.get("title", arxiv_id)
    year = _extract_year(candidate.get("date", ""))
    authors = candidate.get("authors", "")
    if isinstance(authors, list):
        authors = ", ".join(authors)
    tldr = candidate.get("tldr", "")
    abstract = candidate.get("abstract", "")
    direction = candidate.get("direction", "")
    score = candidate.get("score_deepxiv", 0)
    ai_reason = candidate.get("ai_reason", "")

    slug = _slugify(title)
    filename = f"{year}-{arxiv_id}-{slug}.md"
    out_path = RAW_PAPERS_DIR / filename

    # 检查是否已导入（避免重复）
    if out_path.exists():
        print(f"⚠ 已存在，跳过: {filename}")
        return str(out_path.relative_to(KNOWLEDGE_DIR))

    # 生成 frontmatter + 正文
    tags = [PROJECT_TAG]
    if direction:
        tags.append(direction)

    content = f"""---
title: "{title}"
arxiv_id: "{arxiv_id}"
authors: "{authors}"
year: "{year}"
tags: {json.dumps(tags, ensure_ascii=False)}
project: ["{project}"]
direction: "{direction}"
source: "hermes-简报"
imported_at: "{_now_utc()}"
score_deepxiv: {score}
---

# {title}

**arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})
**作者**: {authors}
**方向**: {direction}
**deepxiv 评分**: {score}

## TL;DR

{tldr}

## 摘要

{abstract}

## AI 评价

{ai_reason}
"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"✓ 候选论文已导入: {filename}")
    return str(out_path.relative_to(KNOWLEDGE_DIR))


def import_deep_analysis(arxiv_id: str, project: str = PROJECT_TAG) -> Optional[str]:
    """导入深度解析到 wiki/projects/文献简报/ 子库。

    将 hermes 的深度分析（why_notable / core_findings / linsai_connection）
    转换为林赛视角的结构化 wiki 页面。

    Args:
        arxiv_id: arXiv 论文 ID
        project: 归属项目标签

    Returns:
        生成的 wiki 文件相对路径；无深度解析返回 None。
    """
    analysis = _load_deep_analysis(arxiv_id)
    if not analysis:
        print(f"○ 无深度解析: {arxiv_id}")
        return None

    title = analysis.get("title", arxiv_id)
    authors = analysis.get("authors", "")
    date = analysis.get("date", "")
    direction = analysis.get("direction", "")
    why_notable = analysis.get("why_notable", "")
    core_findings = analysis.get("core_findings", [])
    new_methods = analysis.get("new_methods", [])
    what_next = analysis.get("what_next", [])
    linsai_connection = analysis.get("linsai_connection", "")

    slug = _slugify(title)
    filename = f"{slug}.md"
    out_path = WIKI_PROJECTS_DIR / filename

    tags = [PROJECT_TAG, "深度解析"]
    if direction:
        tags.append(direction)

    # 渲染列表项（容错：None / 非 list / 空）
    def _list_items(items) -> str:
        if not items:
            return "（暂无）"
        if isinstance(items, str):
            return items
        if not isinstance(items, list):
            return str(items)
        return "\n".join(f"- {item}" for item in items)

    content = f"""---
title: "{title}"
type: "papers"
arxiv_id: "{arxiv_id}"
authors: "{authors}"
date: "{date}"
direction: "{direction}"
tags: {json.dumps(tags, ensure_ascii=False)}
project: ["{project}"]
source: "hermes-深度解析"
imported_at: "{_now_utc()}"
growth_stage: "growing"
confidence: 0.8
related: []
---

# {title}

**arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id}) | **方向**: {direction}

## 为什么值得关注

{why_notable}

## 核心发现

{_list_items(core_findings)}

## 新方法

{_list_items(new_methods)}

## 林赛的理解

{linsai_connection}

## 开放问题

{_list_items(what_next)}

## 来源

- [arXiv {arxiv_id}](https://arxiv.org/abs/{arxiv_id})
- 导入自 hermes 深度分析（{_now_utc()}）
"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"✓ 深度解析已导入子库: wiki/projects/{project}/{filename}")
    return str(out_path.relative_to(KNOWLEDGE_DIR))


def import_all_candidates(project: str = PROJECT_TAG, with_analysis: bool = False) -> List[str]:
    """批量导入当日全部候选论文。

    Args:
        project: 归属项目标签
        with_analysis: 是否同时导入已有深度解析（默认 False，仅导入候选元数据）

    Returns:
        成功导入的 arxiv_id 列表
    """
    data = _load_candidates()
    papers = data.get("papers", [])
    if not papers:
        print("○ 无候选论文可导入")
        return []

    imported = []
    print(f"◐ 批量导入 {len(papers)} 篇候选...")
    for p in papers:
        aid = p.get("arxiv_id", "")
        if not aid:
            continue
        result = import_candidate(aid, project)
        if result:
            imported.append(aid)
            if with_analysis:
                import_deep_analysis(aid, project)

    print(f"✓ 导入完成: {len(imported)}/{len(papers)} 篇")
    return imported


def import_session_discussion(session_path: Path, project: str = PROJECT_TAG) -> Optional[str]:
    """导入 hermes 会话为林赛讨论记录。

    将 hermes 的单文件会话 JSON 提取为林赛格式的讨论 markdown，
    沉淀到对应项目的子库，标记来源平台。

    Args:
        session_path: hermes 会话文件路径
        project: 归属项目标签

    Returns:
        生成的讨论记录路径；失败返回 None。
    """
    session_path = Path(session_path)
    if not session_path.exists():
        return None

    try:
        data = json.loads(session_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    messages = data.get("messages", [])
    platform = data.get("platform", "unknown")
    session_id = data.get("session_id", session_path.stem)
    model = data.get("model", "")

    if not messages:
        return None

    # 生成讨论记录
    out_dir = WIKI_PROJECTS_DIR / "讨论记录"
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"讨论-{date_str}-{session_id[:8]}.md"
    out_path = out_dir / filename

    lines = [
        f"# 讨论记录（来源：{platform}）",
        "",
        f"**会话 ID**: `{session_id}`  ",
        f"**平台**: {platform}  ",
        f"**模型**: {model}  ",
        f"**导入时间**: {_now_utc()}  ",
        f"**归属项目**: {project}",
        "",
        "---",
        "",
    ]
    for m in messages:
        role = m.get("role", "unknown")
        content = m.get("content", "")
        label = "🧑 用户" if role == "user" else "🔬 林赛"
        lines.append(f"### {label}")
        lines.append("")
        lines.append(content[:2000])  # 截断超长消息
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ 讨论记录已导入: {filename}")
    return str(out_path.relative_to(KNOWLEDGE_DIR))


def _self_check() -> None:
    """自检：验证产出目录可读 + 字段映射。"""
    print("=" * 50)
    print("◐ kb_importer 自检")
    print("=" * 50)

    # 1. 检查 hermes 产出目录
    print("\n[1/3] 检查 hermes 产出目录...")
    if BRIEFINGS_DIR.exists():
        candidates = _load_candidates()
        n = len(candidates.get("papers", []))
        print(f"  ✓ daily_candidates.json 可读，{n} 篇候选")
        # 检查字段
        if n > 0:
            p = candidates["papers"][0]
            required = ["arxiv_id", "title", "authors", "tldr"]
            missing = [f for f in required if f not in p]
            assert not missing, f"候选字段缺失: {missing}"
            print(f"  ✓ 字段完整: {list(p.keys())}")
    else:
        print(f"  ○ hermes 产出目录不存在: {BRIEFINGS_DIR}")

    # 2. 检查深度解析
    print("\n[2/3] 检查深度解析...")
    analysis_files = list(BRIEFINGS_DIR.glob("deep_analysis_*.json")) if BRIEFINGS_DIR.exists() else []
    print(f"  ✓ 找到 {len(analysis_files)} 份深度解析")
    if analysis_files:
        aid = analysis_files[0].stem.replace("deep_analysis_", "")
        analysis = _load_deep_analysis(aid)
        if analysis:
            # 核心字段必填，其余容错（早期格式可能缺 core_findings 等）
            required = ["arxiv_id", "title"]
            missing = [f for f in required if f not in analysis]
            assert not missing, f"深度解析核心字段缺失: {missing}"
            print(f"  ✓ 字段可读（{len(analysis.keys())} 个）: {list(analysis.keys())[:6]}...")

    # 3. 测试 slugify
    print("\n[3/3] 测试工具函数...")
    assert _slugify("High Harmonic Generation by Bright Squeezed Vacuum") == "high-harmonic-generation-by-bright-squeezed-vacuum"
    assert _extract_year("2024-03") == "2024"
    assert _extract_year("") == str(datetime.now().year)
    print("  ✓ _slugify / _extract_year 正常")

    print("\n✓ kb_importer 自检通过")


if __name__ == "__main__":
    _self_check()
