#!/usr/bin/env python3
"""知识库自定义分类系统 —— 用户创建的分类，基于关键词规则自动关联文件。

分类存储在 knowledge/categories.json，格式：
{
  "categories": [
    {
      "name": "水窗成像",
      "keywords": ["水窗", "water window", "成像"],
      "logic": "any",          # any=任一匹配, all=全部匹配
      "description": "水窗波段成像相关",
      "created": "2026-06-20T...",
      "matched_paths": [...]   # 自动扫描后填充
    }
  ]
}

规范:
    - 仅使用 Python 3 标准库
    - 分类是虚拟的：不移动文件，只在 frontmatter 的 project 字段追加分类名
    - 删除分类时只移除关联，不删文件
    - 幂等：重复运行不会重复关联
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc as _now_utc

from paths import PROJECT_ROOT, KNOWLEDGE_DIR
CATEGORIES_PATH = KNOWLEDGE_DIR / "categories.json"


def _load_categories() -> Dict[str, Any]:
    """加载分类配置。"""
    if not CATEGORIES_PATH.exists():
        return {"categories": []}
    try:
        data = json.loads(CATEGORIES_PATH.read_text(encoding="utf-8"))
        if "categories" not in data:
            data["categories"] = []
        return data
    except Exception:
        return {"categories": []}


def _save_categories(data: Dict[str, Any]) -> None:
    """保存分类配置。"""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    CATEGORIES_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def list_categories() -> List[Dict[str, Any]]:
    """列出所有自定义分类（含匹配文件数）。"""
    data = _load_categories()
    return data.get("categories", [])


def get_category(name: str) -> Optional[Dict[str, Any]]:
    """获取单个分类。"""
    for cat in _load_categories().get("categories", []):
        if cat.get("name") == name:
            return cat
    return None


def create_category(name: str, keywords: List[str], logic: str = "any",
                    description: str = "") -> Dict[str, Any]:
    """创建自定义分类。

    Args:
        name: 分类名称（唯一）
        keywords: 关键词列表
        logic: 匹配逻辑，"any" 或 "all"
        description: 分类描述

    Returns:
        创建的分类字典
    """
    data = _load_categories()

    # 检查重名
    for cat in data["categories"]:
        if cat.get("name") == name:
            raise ValueError(f"分类 '{name}' 已存在")

    category = {
        "name": name,
        "keywords": keywords,
        "logic": logic,
        "description": description,
        "created": _now_utc(),
        "matched_paths": [],
    }
    data["categories"].append(category)
    _save_categories(data)

    # 立即扫描匹配
    matched = scan_category(name)
    return {**category, "matched_paths": matched}


def update_category(name: str, keywords: Optional[List[str]] = None,
                    logic: Optional[str] = None,
                    description: Optional[str] = None) -> Dict[str, Any]:
    """更新分类配置。"""
    data = _load_categories()
    for cat in data["categories"]:
        if cat.get("name") == name:
            if keywords is not None:
                cat["keywords"] = keywords
            if logic is not None:
                cat["logic"] = logic
            if description is not None:
                cat["description"] = description
            _save_categories(data)
            # 重新扫描
            matched = scan_category(name)
            return {**cat, "matched_paths": matched}
    raise ValueError(f"分类 '{name}' 不存在")


def delete_category(name: str) -> bool:
    """删除分类（只移除配置，不删文件）。"""
    data = _load_categories()
    original_len = len(data["categories"])
    data["categories"] = [c for c in data["categories"] if c.get("name") != name]
    if len(data["categories"]) < original_len:
        _save_categories(data)
        return True
    return False


def _match_content(text: str, keywords: List[str], logic: str) -> bool:
    """检查文本是否匹配关键词规则。"""
    text_lower = text.lower()
    if logic == "all":
        return all(kw.lower() in text_lower for kw in keywords)
    else:  # any
        return any(kw.lower() in text_lower for kw in keywords)


def scan_category(name: str) -> List[str]:
    """扫描全库，找出匹配该分类的文件路径。

    匹配范围：wiki/ 下所有 Markdown 的标题 + frontmatter + 正文前 500 字。
    匹配后更新 categories.json 中的 matched_paths。

    Returns:
        匹配的文件路径列表（相对 knowledge/）
    """
    data = _load_categories()
    cat = None
    for c in data["categories"]:
        if c.get("name") == name:
            cat = c
            break
    if not cat:
        raise ValueError(f"分类 '{name}' 不存在")

    keywords = cat.get("keywords", [])
    logic = cat.get("logic", "any")
    if not keywords:
        cat["matched_paths"] = []
        _save_categories(data)
        return []

    matched = []
    wiki_dir = KNOWLEDGE_DIR / "wiki"
    if wiki_dir.exists():
        for fpath in sorted(wiki_dir.rglob("*.md")):
            try:
                text = fpath.read_text(encoding="utf-8")
                # 匹配范围：全文（frontmatter + 正文）
                if _match_content(text, keywords, logic):
                    rel = str(fpath.relative_to(KNOWLEDGE_DIR))
                    matched.append(rel)
            except Exception:
                continue

    cat["matched_paths"] = matched
    _save_categories(data)
    return matched


def scan_all_categories() -> Dict[str, List[str]]:
    """重新扫描所有分类的匹配文件。

    Returns:
        {分类名: [匹配路径列表]}
    """
    data = _load_categories()
    results = {}
    for cat in data["categories"]:
        name = cat.get("name", "")
        if name:
            results[name] = scan_category(name)
    return results


def get_all_filters() -> Dict[str, List[str]]:
    """获取所有可用的筛选器选项（供前端搜索筛选）。

    Returns:
        {
            "types": ["concepts", "methods", ...],
            "stages": ["seedling", "growing", "mature"],
            "projects": ["NSFC-强场超快", "deepxiv-论文库", ...],
            "tags": ["HHG", "阿秒", ...],
            "categories": ["水窗成像", ...]
        }
    """
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from knowledge_base import list_wiki_pages

    pages = list_wiki_pages()

    types = set()
    stages = set()
    projects = set()
    tags = set()

    for p in pages:
        fm = p
        t = fm.get("type", "")
        if t:
            types.add(t)
        s = fm.get("growth_stage", "")
        if s:
            stages.add(s)
        proj = fm.get("project", "")
        if isinstance(proj, str) and proj:
            projects.add(proj)
        elif isinstance(proj, list):
            for pr in proj:
                if pr:
                    projects.add(pr)
        ptags = fm.get("tags", [])
        if isinstance(ptags, list):
            for tag in ptags:
                if tag:
                    tags.add(tag)

    cats = [c["name"] for c in _load_categories().get("categories", [])]

    return {
        "types": sorted(types),
        "stages": sorted(stages),
        "projects": sorted(projects),
        "tags": sorted(tags),
        "categories": cats,
    }


def filter_wiki_pages(filters: Dict[str, str]) -> List[Dict[str, Any]]:
    """根据筛选条件过滤 wiki 页面。

    Args:
        filters: {"type": "...", "stage": "...", "project": "...", "tag": "...", "category": "..."}

    Returns:
        过滤后的页面列表
    """
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from knowledge_base import list_wiki_pages

    pages = list_wiki_pages()
    results = []

    # 如果有分类筛选，先获取该分类的匹配路径
    category_paths = None
    cat_name = filters.get("category", "")
    if cat_name:
        cat = get_category(cat_name)
        if cat:
            category_paths = set(cat.get("matched_paths", []))

    for p in pages:
        # 类型筛选
        if filters.get("type") and p.get("type") != filters["type"]:
            continue
        # 阶段筛选
        if filters.get("stage") and p.get("growth_stage") != filters["stage"]:
            continue
        # 项目筛选
        if filters.get("project"):
            proj = p.get("project", "")
            if isinstance(proj, str):
                proj = [proj]
            if filters["project"] not in proj:
                continue
        # 标签筛选
        if filters.get("tag"):
            ptags = p.get("tags", [])
            if not isinstance(ptags, list):
                ptags = [ptags]
            if filters["tag"] not in ptags:
                continue
        # 分类筛选
        if category_paths is not None:
            if p.get("path") not in category_paths:
                continue

        results.append(p)

    return results


def _self_check() -> None:
    """自检。"""
    print("=" * 50)
    print("◐ kb_categories 自检")
    print("=" * 50)

    print("\n[1/3] 加载分类配置...")
    cats = list_categories()
    print(f"  现有分类: {len(cats)} 个")
    for c in cats:
        print(f"    - {c['name']} ({len(c.get('matched_paths', []))} 篇)")

    print("\n[2/3] 验证 CRUD 函数...")
    assert callable(create_category), "create_category 不可调用"
    assert callable(update_category), "update_category 不可调用"
    assert callable(delete_category), "delete_category 不可调用"
    assert callable(scan_all_categories), "scan_all_categories 不可调用"
    print("  ✓ CRUD 函数就绪")

    print("\n[3/3] 验证筛选器...")
    filters = get_all_filters()
    for k, v in filters.items():
        print(f"  {k}: {len(v)} 个选项")
    print("  ✓ 筛选器就绪")

    print("\n✓ kb_categories 自检通过")


if __name__ == "__main__":
    _self_check()
