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

from paths import PROJECT_ROOT, SCRIPTS_DIR, KNOWLEDGE_DIR

# [[WikiLink]] 模式（不含别名用法）
_WIKILINK_RE = re.compile(r"\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]")


def _load_all_titles() -> Dict[str, str]:
    """加载所有 wiki 页面标题 → 路径的映射。

    v7.3.85: people 页（人名）不入词表——姓氏标题在正文子串匹配下全库
    命中（"Han" 命中 "Hamilton"、"Ding" 命中任意引文），11-14/15 一轮
    产出约 2000 条假边（Ding×705 / Liu×238 / Lee×110 / Yang×104），
    本过滤为止血修复；人名归属类链接不应由标题提及匹配自动生成。
    merged_into 重定向 stub 同样不入词表（与图谱重建 v6.10.52「跳过
    stub」口径一致，避免向已合并页补边）。
    """
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import list_wiki_pages

    titles = {}
    for p in list_wiki_pages():
        if p.get("type") == "people" or p.get("merged_into"):
            continue
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


_ASCII_TITLE_RE = re.compile(r"^[A-Za-z0-9 .\-']+$")
_ascii_re_cache: Dict[str, "re.Pattern[str]"] = {}


def _ascii_boundary_re(title: str) -> "re.Pattern[str]":
    """纯拉丁标题的词边界正则（缓存），避免子串假阳性命中。"""
    pat = _ascii_re_cache.get(title)
    if pat is None:
        pat = re.compile(r"(?<![A-Za-z])" + re.escape(title) + r"(?![A-Za-z])", re.IGNORECASE)
        _ascii_re_cache[title] = pat
    return pat


def extract_title_mentions(body: str, all_titles: Dict[str, str], self_title: str = "") -> Set[str]:
    """从正文中提取对现有 wiki 页面标题的提及。

    匹配规则：标题在正文中以完整词组出现（不区分大小写）。
    v7.3.85: 纯拉丁标题改为「子串预筛 + 词边界正则确认」两段式，
    避免 "Han" 命中 "Hamilton"、"Liu" 命中引文内片段等假阳性。
    """
    mentions = set()
    body_lower = body.lower()
    for title in all_titles:
        if title == self_title or len(title) < 3:
            continue
        if title.lower() not in body_lower:
            continue
        if _ASCII_TITLE_RE.match(title):
            if _ascii_boundary_re(title).search(body):
                mentions.add(title)
        else:
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


def apply_related_batch(items: List[Tuple[str, List[str]]]) -> int:
    """批量写入 related（v7.2.75）。

    背景：`apply_related` 每页做三件重活——
      1. `save_wiki_page` → 内部逐条 `add_graph_edge`（每条都要读全量
         5.1MB graph.json 再原子写回，实测 0.085s/条）
      2. `save_wiki_page` → `log_growth` → growth-log 全量重写
         （10.1MB / 38168 条，实测 0.18s/页）
      3. `save_wiki_page` → `_inject_wikilinks` 重新解析 frontmatter
    实测 758 页 × 平均 2 条 related 的补边批次里，图谱写 + growth-log
    写合计 >250s，是 lc-kb-distill-pm 逼近 cron 3600s 硬超时的主要
    成本之一（实测 2026-10-31 18:50 档 last_status=error）。

    本接口把图谱写合并为 **1 次**（`add_graph_edges_batch`），
    growth-log 写合并为 **1 次**（批量追加）。

    Args:
        items: (页面相对路径, 新增 related 标题列表) 序列。

    Returns:
        实际写入的页面数。
    """
    if not items:
        return 0

    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import get_wiki_page, save_wiki_page
    from kb_graph import add_graph_edges_batch, update_graph_nodes_batch
    from kb_wiki import _now_utc
    import knowledge_base as _kb

    edge_pairs: List[Tuple[str, str, str]] = []
    node_pairs: List[Tuple[str, str, str, str]] = []
    written = 0
    for path, new_related in items:
        if not new_related:
            continue
        page = get_wiki_page(path)
        if not page:
            continue
        fm = page.get("frontmatter", {})
        existing = fm.get("related", [])
        if isinstance(existing, str):
            existing = [existing]
        fm["related"] = existing + new_related
        body = page.get("body", "")
        # defer_graph / defer_growth_log：图谱与生长日志统一在批末补写
        save_wiki_page(path, body, fm,
                       defer_graph=True, defer_growth_log=True)
        title = fm.get("title", "")
        wiki_type = fm.get("type", "concepts")
        growth_stage = fm.get("growth_stage", "growing")
        if title:
            node_pairs.append((title, wiki_type, str(path), growth_stage))
        for target in new_related:
            edge_pairs.append((title, target, "related"))
        written += 1

    # 图谱：节点与边各一次读-改-写（替代逐页逐条全量重写）
    if node_pairs:
        update_graph_nodes_batch(node_pairs)
    if edge_pairs:
        add_graph_edges_batch(edge_pairs)

    # growth-log：批量追加一次（替代每页一次全量重写）
    if written and _kb.log_growth:
        try:
            log = _kb._load_growth_log()
            ts = _now_utc()
            for path, _ in items:
                log.append({
                    "timestamp": ts,
                    "action": "link",
                    "target": path,
                    "trigger": "auto",
                    "reason": "kb_linker 批量补边",
                })
            _kb._save_growth_log(log)
        except Exception:
            pass  # 日志失败不阻塞补边

    return written


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
    pending_items: List[Tuple[str, List[str]]] = []

    for page in pages:
        path = page.get("path", "")
        if not path:
            continue
        new_related = discover_related(path, all_titles)
        if new_related:
            results[path] = new_related
            if apply:
                pending_items.append((path, new_related))

    # v7.2.75：apply 走批量路径——图谱写 + growth-log 写各合并为 1 次，
    # 避免逐页逐边重复全量重写 5.1MB graph.json / 10.1MB growth-log.json
    # （实测这是 lc-kb-distill-pm 逼近 cron 3600s 硬超时的主因）。
    if apply and pending_items:
        apply_related_batch(pending_items)

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
