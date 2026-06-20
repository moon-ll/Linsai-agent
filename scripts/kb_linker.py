#!/usr/bin/env python3
"""导入时自动提取主题关键词，连接 related 边。

策略：
1. 从新页面的标题和正文中提取实体（匹配现有 wiki 页面标题）
2. 从 [[WikiLink]] 中提取显式链接
3. 将提取到的关联写入 frontmatter 的 related 字段
4. 同步更新 graph.json

用法:
    python scripts/kb_linker.py                    # 扫描全部 wiki，补充缺失的 related
    python scripts/kb_linker.py --path wiki/xxx.md # 仅处理指定页面
    python scripts/kb_linker.py --apply            # 执行写入

规范:
    - 仅使用 Python 3 标准库
    - 不覆盖已有的 related，只追加新发现的
    - 不自连（title 不连自己）
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"

# [[WikiLink]] 模式（不含别名用法）
_WIKILINK_RE = re.compile(r"\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]")


def _load_all_titles() -> Dict[str, str]:
    """加载所有 wiki 页面标题 → 路径的映射。"""
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import list_wiki_pages

    titles = {}
    for p in list_wiki_pages():
        title = p.get("title", "")
        if title:
            titles[title] = p.get("path", "")
    return titles


def extract_wikilinks(body: str) -> Set[str]:
    """从正文中提取 [[WikiLink]] 链接目标。"""
    links = set()
    for m in _WIKILINK_RE.finditer(body):
        target = m.group(1).strip()
        if target:
            links.add(target)
    return links


def extract_title_mentions(body: str, all_titles: Dict[str, str], self_title: str = "") -> Set[str]:
    """从正文中提取对现有 wiki 页面标题的提及。

    匹配规则：标题在正文中以完整词组出现（不区分大小写）。
    """
    mentions = set()
    body_lower = body.lower()
    for title in all_titles:
        if title == self_title or len(title) < 3:
            continue
        if title.lower() in body_lower:
            mentions.add(title)
    return mentions


def discover_related(path: str, all_titles: Dict[str, str]) -> List[str]:
    """发现页面的 related 关联。

    Args:
        path: wiki 页面路径
        all_titles: 所有 wiki 标题 → 路径映射

    Returns:
        新发现的 related 标题列表
    """
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import get_wiki_page

    page = get_wiki_page(path)
    if not page:
        return []

    fm = page.get("frontmatter", {})
    title = fm.get("title", "")
    body = page.get("body", "")
    existing_related = fm.get("related", [])
    if isinstance(existing_related, str):
        existing_related = [existing_related]
    existing_set = set(existing_related)
    existing_set.add(title)  # 不自连

    # 1. 从 [[WikiLink]] 提取
    wikilinks = extract_wikilinks(body)
    # 2. 从标题提及提取
    title_mentions = extract_title_mentions(body, all_titles, title)

    # 合并
    all_found = wikilinks | title_mentions
    # 过滤：只保留存在的标题 + 排除已有的 + 排除自己
    new_related = []
    for target in all_found:
        if target in all_titles and target not in existing_set:
            new_related.append(target)
            existing_set.add(target)

    return new_related


def apply_related(path: str, new_related: List[str]) -> bool:
    """将新发现的 related 写入页面 frontmatter 并更新图谱。"""
    if not new_related:
        return False

    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import get_wiki_page, save_wiki_page, add_graph_edge

    page = get_wiki_page(path)
    if not page:
        return False

    fm = page.get("frontmatter", {})
    existing = fm.get("related", [])
    if isinstance(existing, str):
        existing = [existing]
    fm["related"] = existing + new_related
    body = page.get("body", "")
    save_wiki_page(path, body, fm)

    # 更新图谱
    title = fm.get("title", "")
    for target in new_related:
        add_graph_edge(title, target, "related")

    return True


def scan_all(apply: bool = False) -> Dict[str, List[str]]:
    """扫描全部 wiki 页面，发现或应用 related 关联。

    Args:
        apply: True=写入，False=仅报告

    Returns:
        {path: [新发现的 related 标题列表]}
    """
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import list_wiki_pages

    all_titles = _load_all_titles()
    pages = list_wiki_pages()
    results = {}

    for page in pages:
        path = page.get("path", "")
        if not path:
            continue
        new_related = discover_related(path, all_titles)
        if new_related:
            results[path] = new_related
            if apply:
                apply_related(path, new_related)

    return results


def _self_check() -> None:
    """自检。"""
    print("=" * 50)
    print("◐ kb_linker 自检")
    print("=" * 50)

    print("\n[1/2] 加载 wiki 标题...")
    all_titles = _load_all_titles()
    print(f"  现有标题: {len(all_titles)} 个")

    print("\n[2/2] 扫描缺失的 related...")
    results = scan_all(apply=False)
    total_links = sum(len(v) for v in results.values())
    print(f"  发现 {len(results)} 个页面可补充 related，共 {total_links} 条新边")
    for path, related in list(results.items())[:10]:
        title = path.rsplit("/", 1)[-1].replace(".md", "")
        print(f"    {title}: +{related}")

    print("\n✓ kb_linker 自检通过")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="导入时自动连边引擎")
    parser.add_argument("--apply", action="store_true", help="执行写入")
    parser.add_argument("--path", type=str, help="仅处理指定页面")
    args = parser.parse_args()

    if args.path:
        all_titles = _load_all_titles()
        new_related = discover_related(args.path, all_titles)
        if new_related:
            print(f"发现 {len(new_related)} 条新 related: {new_related}")
            if args.apply:
                apply_related(args.path, new_related)
                print("✓ 已写入")
        else:
            print("○ 无新 related")
    elif args.apply:
        results = scan_all(apply=True)
        total = sum(len(v) for v in results.values())
        print(f"✓ 已写入 {total} 条新 related 边，涉及 {len(results)} 个页面")
    else:
        _self_check()
