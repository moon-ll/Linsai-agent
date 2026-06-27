#!/usr/bin/env python3
"""kb_wiki.py — Wiki 页面管理。

负责 wiki 页面的构建、读取、列表、保存、删除，以及交互触发生长
（相似概念检查、stub 创建、丰满 prompt 生成、生长应用）。

依赖：kb_text（frontmatter/安全文件名）、kb_graph（图谱节点/边/双向链接注入）、
      kb_index（检索/索引重建）、paths（KNOWLEDGE_DIR/WIKI_DIR）、common（now_utc）。

门面 knowledge_base 在加载完成后会向本模块注入以下函数，以解决子模块→门面依赖：
    _ensure_dirs  — 目录初始化
    log_growth    — 生长日志记录
    _log          — 日志对象
在门面未注入前这些名字为 None 占位，函数体保持与原 knowledge_base.py 完全一致。

用法示例：
    >>> from kb_wiki import save_wiki_page, get_wiki_page
    >>> save_wiki_page("wiki/concepts/测试.md", "# 测试", {"title": "测试"})
    >>> page = get_wiki_page("wiki/concepts/测试.md")

规范：
    - 仅使用 Python 3 标准库
    - 不修改任何函数逻辑，自 knowledge_base.py 物理迁移而来
"""

from typing import Any, Dict, List, Optional, Tuple

from common import now_utc as _now_utc
from paths import KNOWLEDGE_DIR, WIKI_DIR
from kb_text import parse_frontmatter, build_frontmatter, _safe_filename
from kb_graph import (
    update_graph_node, add_graph_edge, _remove_graph_node, _inject_wikilinks,
)
from kb_index import search, build_index


# ─────────────────────────────────────────────
# 门面注入依赖（占位，由 knowledge_base 加载后覆盖）
# ─────────────────────────────────────────────

_ensure_dirs = None  # type: ignore
log_growth = None  # type: ignore
_log = None


# ─────────────────────────────────────────────
# 常量
# ─────────────────────────────────────────────

_WIKI_TYPES = {"concepts", "methods", "people", "papers", "projects"}


# ─────────────────────────────────────────────
# Wiki 页面管理
# ─────────────────────────────────────────────

def build_wiki_page(title: str, wiki_type: str, content: str,
                    meta: Optional[Dict[str, Any]] = None) -> str:
    """构建标准 wiki 页面文本（含 frontmatter + 林赛视角结构）。"""
    default_meta = {
        "title": title,
        "type": wiki_type,
        "created": _now_utc(),
        "updated": _now_utc(),
        "tags": [],
        "related": [],
        "source_raw": "",
        "growth_stage": "seedling",
        "confidence": 0.5,
    }
    if meta:
        default_meta.update(meta)
    fm = build_frontmatter(default_meta)
    return f"{fm}\n\n{content.strip()}"


def get_wiki_page(rel_path: str) -> Optional[Dict[str, Any]]:
    """读取 wiki 页面，解析 frontmatter 和内容。

    Args:
        rel_path: 相对 knowledge/ 的路径，如 "wiki/concepts/固体高次谐波产生.md"

    Returns:
        {"frontmatter": dict, "body": str, "path": str} 或 None
    """
    path = KNOWLEDGE_DIR / rel_path
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        return {"frontmatter": fm, "body": body, "path": str(rel_path)}
    except Exception:
        return None


def list_wiki_pages(wiki_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """列出所有 wiki 页面（只返回 frontmatter，不加载全文）。

    支持子目录（v2.7.0）：projects/ 等类型下可按项目再分子目录，
    用 rglob 递归扫描，使子库结构可见。
    """
    pages = []
    dirs = [WIKI_DIR / wiki_type] if wiki_type else [WIKI_DIR / t for t in _WIKI_TYPES]
    for d in dirs:
        if not d.exists():
            continue
        for fpath in sorted(d.rglob("*.md")):
            try:
                text = fpath.read_text(encoding="utf-8")
                fm, _ = parse_frontmatter(text)
                rel = str(fpath.relative_to(KNOWLEDGE_DIR))
                pages.append({
                    "path": rel,
                    "title": fm.get("title", fpath.stem),
                    "type": fm.get("type", wiki_type or "unknown"),
                    "growth_stage": fm.get("growth_stage", "unknown"),
                    "confidence": fm.get("confidence", 0.0),
                    "updated": fm.get("updated", ""),
                    "tags": fm.get("tags", []),
                    "project": fm.get("project", ""),
                })
            except Exception:
                continue
    return pages


def save_wiki_page(rel_path: str, content: str, meta: Optional[Dict[str, Any]] = None,
                   append: bool = False) -> str:
    """保存 wiki 页面。

    Args:
        rel_path: 相对 knowledge/ 的路径
        content: Markdown 内容
        meta: frontmatter 数据（如页面已存在则合并更新）
        append: 为 True 时在现有内容后追加

    Returns:
        保存的文件路径（相对 knowledge/）
    """
    _ensure_dirs()
    path = KNOWLEDGE_DIR / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)

    existing_fm: Dict[str, Any] = {}
    existing_body = ""
    if path.exists():
        text = path.read_text(encoding="utf-8")
        existing_fm, existing_body = parse_frontmatter(text)

    if meta:
        existing_fm.update(meta)
    existing_fm["updated"] = _now_utc()

    if append and existing_body:
        body = existing_body + "\n\n" + content.strip()
    else:
        body = content.strip()

    page_text = build_wiki_page(
        title=existing_fm.get("title", path.stem),
        wiki_type=existing_fm.get("type", "concepts"),
        content=body,
        meta=existing_fm,
    )
    path.write_text(page_text, encoding="utf-8")

    # 注入 Obsidian 双向链接并同步图谱
    final_text = _inject_wikilinks(path.read_text(encoding="utf-8"))
    path.write_text(final_text, encoding="utf-8")

    fm, _ = parse_frontmatter(final_text)
    title = fm.get("title", "")
    if title:
        wiki_type = fm.get("type", "concepts")
        growth_stage = fm.get("growth_stage", "growing")
        update_graph_node(title, wiki_type, str(rel_path), growth_stage)
        for related in fm.get("related", []):
            if related:
                add_graph_edge(title, related, "related")
        # 子库归属（v2.7.0）：frontmatter 含 project 时，自动连 项目→title 边
        projects = fm.get("project", [])
        if isinstance(projects, str):
            projects = [projects] if projects else []
        for proj in projects:
            if proj:
                # 确保项目节点存在（作为汇聚节点）
                update_graph_node(proj, "projects", f"wiki/projects/{proj}", "mature")
                add_graph_edge(title, proj, "belongs_to")

    return str(rel_path)


def delete_wiki_page(rel_path: str) -> bool:
    """删除 wiki 页面，同时清理图谱中的关联。"""
    path = KNOWLEDGE_DIR / rel_path
    if not path.exists():
        return False
    try:
        path.unlink()
        # 清理图谱
        page = get_wiki_page(rel_path)
        title = page["frontmatter"].get("title", "") if page else ""
        if title:
            _remove_graph_node(title)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
# 交互触发生长
# ─────────────────────────────────────────────

def check_similar_concepts(concept_name: str, threshold: float = 0.9) -> List[Dict[str, Any]]:
    """检查知识库中是否存在与给定概念高度相似的条目。

    Returns:
        相似概念列表，每项含 title, doc, score, path
    """
    results = search(concept_name, top_k=5)
    similar = []
    for r in results:
        score = r.get("score", 0)
        if score >= threshold:
            similar.append({
                "title": r.get("title", ""),
                "doc": r.get("doc", ""),
                "score": score,
                "source": r.get("source", ""),
                "growth_stage": r.get("growth_stage", ""),
            })
    return similar


def create_wiki_stub(concept_name: str, context: str = "",
                     trigger: str = "conversation") -> str:
    """基于上下文创建 wiki stub（交互触发生长）。

    当对话中遇到知识库中不存在的新概念时，创建 stub，
    标记为 seedling 阶段，后续交互中逐步丰满。

    Args:
        concept_name: 概念名称
        context: 触发创建的上下文（对话片段）
        trigger: 触发来源

    Returns:
        创建的 wiki 路径
    """
    _ensure_dirs()
    safe_name = _safe_filename(concept_name)
    wiki_rel = f"wiki/concepts/{safe_name}.md"

    # 如果已存在，不重复创建
    if (KNOWLEDGE_DIR / wiki_rel).exists():
        return wiki_rel

    stub_content = f"""# {concept_name}

## 林赛的理解

（待补充——这个概念是在对话中首次遇到的，林赛正在学习中。）

## 核心要点

（待补充）

## 触发上下文

> {context[:500] if context else "暂无上下文"}

## 开放问题

- 这个概念与林赛现有的知识体系如何关联？
"""

    meta = {
        "title": concept_name,
        "type": "concepts",
        "tags": [],
        "related": [],
        "source_raw": "",
        "growth_stage": "seedling",
        "confidence": 0.3,
    }

    save_wiki_page(wiki_rel, stub_content, meta)
    update_graph_node(concept_name, "concepts", wiki_rel, "seedling")
    log_growth("create", wiki_rel, trigger,
               f"对话中遇到新概念 '{concept_name}'，创建 seedling stub")

    build_index()
    if _log:
        _log.info(f"创建 wiki stub (seedling): {wiki_rel} ← 概念 '{concept_name}'")
    return wiki_rel


def grow_wiki_prompt(wiki_rel_path: str, new_context: str,
                     reason: str = "") -> Tuple[str, str]:
    """生成 wiki 丰满 prompt，供 LLM 使用。

    Returns:
        (wiki_path, prompt_text)
    """
    page = get_wiki_page(wiki_rel_path)
    if not page:
        return wiki_rel_path, ""

    fm = page["frontmatter"]
    body = page["body"]
    title = fm.get("title", wiki_rel_path)

    prompt = f"""请帮助林赛（强场超快光学 PI）丰满他的研究笔记。

现有笔记：《{title}》
当前生长阶段：{fm.get("growth_stage", "unknown")}
当前确信度：{fm.get("confidence", 0.5)}

现有内容：

---
{body[:4000]}
---

新上下文（来自与用户的对话）：
{new_context[:3000]}

{reason}

请基于新上下文，补充或修正现有笔记。要求：
1. 保持第一人称"林赛"的视角
2. 添加"林赛的理解"、"实验经验"或"批判性思考"部分
3. 更新 related 字段，添加关联概念
4. 如果内容足够充实，将 growth_stage 提升为 "growing" 或 "mature"
5. 适当提升 confidence

请输出完整的 wiki 页面（含 frontmatter），可以直接覆盖原有内容。
"""
    return wiki_rel_path, prompt


def apply_growth(wiki_rel_path: str, llm_output: str,
                 trigger: str = "conversation") -> str:
    """应用 LLM 生成的丰满内容，更新 wiki 页面。

    Args:
        wiki_rel_path: wiki 页面路径
        llm_output: LLM 生成的完整 wiki 页面
        trigger: 触发来源

    Returns:
        更新后的 wiki 路径
    """
    path = KNOWLEDGE_DIR / wiki_rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(llm_output, encoding="utf-8")

    # 注入 Obsidian 双向链接
    final_text = _inject_wikilinks(path.read_text(encoding="utf-8"))
    path.write_text(final_text, encoding="utf-8")

    fm, _ = parse_frontmatter(final_text)
    title = fm.get("title", path.stem)
    wiki_type = fm.get("type", "concepts")
    growth_stage = fm.get("growth_stage", "growing")

    update_graph_node(title, wiki_type, wiki_rel_path, growth_stage)

    for related in fm.get("related", []):
        if related:
            add_graph_edge(title, related, "related")

    log_growth("update", wiki_rel_path, trigger,
               f"基于对话上下文丰满 '{title}'，阶段更新为 {growth_stage}")

    build_index()
    return wiki_rel_path
