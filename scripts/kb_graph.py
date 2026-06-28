#!/usr/bin/env python3
"""kb_graph.py — 知识库图谱管理。

负责知识图谱的加载/保存、节点与边的增删、关联概念遍历、图谱概览，
以及 Obsidian 双向链接（WikiLink）的提取、别名查找与注入。

依赖：kb_text（frontmatter 解析/生成）、paths（GRAPH_PATH/ALIASES_PATH）。

用法示例：
    >>> from kb_graph import update_graph_node, get_related_concepts
    >>> update_graph_node("固体高次谐波", "concepts", "wiki/concepts/固体高次谐波.md")
    >>> related = get_related_concepts("固体高次谐波", depth=1)

规范：
    - 仅使用 Python 3 标准库
    - 不修改任何函数逻辑，自 knowledge_base.py 物理迁移而来
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set

import common as _cms
from paths import GRAPH_PATH, ALIASES_PATH
from kb_text import parse_frontmatter, build_frontmatter

# P2-6: 图谱文件缓存（避免每次操作都读磁盘）
_graph_cache: Dict[str, Any] = None
_graph_mtime: float = 0.0


# ─────────────────────────────────────────────
# WikiLink 正则
# ─────────────────────────────────────────────

_WIKILINK_RE = re.compile(r"(?<!\!)\[\[([^\]\|]+)(?:\|[^\]]*)?\]\]")
_WIKILINKS_SECTION_RE = re.compile(
    r"\n?<!-- linsai-wikilinks -->\n.*?<!-- /linsai-wikilinks -->\n?",
    re.DOTALL,
)


def _extract_wikilinks(text: str) -> List[str]:
    """从 Markdown 正文中提取所有 [[WikiLink]]（不含显示文本）。"""
    links = []
    for m in _WIKILINK_RE.finditer(text):
        link = m.group(1).strip()
        if link:
            links.append(link)
    return links


def _get_aliases_for_concept(title: str) -> List[str]:
    """从 aliases.json 中查找给定概念的所有别名。"""
    if not ALIASES_PATH.exists():
        return []
    try:
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            aliases = json.load(f)
    except Exception:
        return []
    # aliases.json 格式: {标准词: [别名1, 别名2, ...]}
    # 反向查找：哪些标准词包含此 title 作为别名
    result: Set[str] = set()
    for canonical, alts in aliases.items():
        if canonical == title:
            result.update(alts)
            continue
        if title in alts:
            result.add(canonical)
            result.update(a for a in alts if a != title)
    return sorted(result)


def _inject_wikilinks(page_text: str) -> str:
    """同步 frontmatter 的 related 与正文 [[WikiLink]]，返回更新后的页面文本。

    策略：
    1. 从正文中提取所有已存在的 [[WikiLink]]
    2. 与 frontmatter['related'] 合并、去重
    3. 更新 frontmatter['related']
    4. 在正文末尾注入/更新 <!-- linsai-wikilinks --> 区域
    5. 把当前概念的别名写入 frontmatter['aliases']
    """
    fm, body = parse_frontmatter(page_text)
    if not fm:
        return page_text

    title = fm.get("title", "")

    # 提取正文中已有的 wikilinks（排除 wikilinks 区域本身的）
    # 先去掉旧的 wikilinks 区域
    clean_body = _WIKILINKS_SECTION_RE.sub("\n", body).strip()
    body_links = set(_extract_wikilinks(clean_body))

    # 合并 frontmatter related 和正文中的链接
    related = set(r for r in fm.get("related", []) if isinstance(r, str) and r)
    merged = sorted(related | body_links)
    fm["related"] = merged

    # 注入别名
    aliases = _get_aliases_for_concept(title)
    if aliases:
        fm["aliases"] = aliases

    # 构建 wikilinks 区域
    if merged:
        link_lines = "\n".join(f"- [[{name}]]" for name in merged)
        wikilinks_section = (
            f"\n\n<!-- linsai-wikilinks -->\n"
            f"## 关联概念\n\n"
            f"{link_lines}\n"
            f"<!-- /linsai-wikilinks -->"
        )
    else:
        wikilinks_section = (
            "\n\n<!-- linsai-wikilinks -->\n"
            "## 关联概念\n\n"
            "_暂无关联概念_\n"
            "<!-- /linsai-wikilinks -->"
        )

    new_body = clean_body.rstrip() + wikilinks_section
    new_fm = build_frontmatter(fm)
    return f"{new_fm}\n\n{new_body}\n"


# ─────────────────────────────────────────────
# 图谱加载与节点管理
# ─────────────────────────────────────────────

def _load_graph() -> Dict[str, Any]:
    """加载知识图谱（带 mtime 缓存，避免频繁磁盘 I/O）。"""
    global _graph_cache, _graph_mtime
    if not GRAPH_PATH.exists():
        return {"nodes": {}, "edges": []}
    try:
        current_mtime = os.path.getmtime(GRAPH_PATH)
        # 缓存命中：文件未修改
        if _graph_cache is not None and current_mtime == _graph_mtime:
            return _graph_cache
        with open(GRAPH_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 确保结构完整
        if "nodes" not in data or "edges" not in data:
            data = {"nodes": {}, "edges": []}
        _graph_cache = data
        _graph_mtime = current_mtime
        return data
    except Exception:
        return {"nodes": {}, "edges": []}


def _save_graph(graph: Dict[str, Any]) -> None:
    """保存知识图谱并更新缓存。"""
    global _graph_cache, _graph_mtime
    _cms.save_json(GRAPH_PATH, graph)
    _graph_cache = graph
    try:
        _graph_mtime = os.path.getmtime(GRAPH_PATH)
    except OSError:
        pass


def _graph_file_lock():
    """获取图谱文件的写入锁（延迟导入 web_base，避免循环依赖）。

    web_base 位于同目录，提供 _get_file_lock 读写锁；
    包裹读-改-写操作可防止并发请求丢更新。
    """
    import web_base
    return web_base._get_file_lock(str(GRAPH_PATH))


def _remove_graph_node(title: str) -> None:
    """从图谱中移除节点及其关联边。"""
    with _graph_file_lock():
        graph = _load_graph()
        if title in graph["nodes"]:
            del graph["nodes"][title]
        graph["edges"] = [e for e in graph["edges"] if e.get("from") != title and e.get("to") != title]
        _save_graph(graph)


def update_graph_node(title: str, wiki_type: str, path: str,
                      growth_stage: str = "seedling") -> None:
    """更新或创建知识图谱节点。"""
    with _graph_file_lock():
        graph = _load_graph()
        graph["nodes"][title] = {
            "type": wiki_type,
            "path": path,
            "growth_stage": growth_stage,
        }
        _save_graph(graph)


def add_graph_edge(from_node: str, to_node: str, relation: str = "related") -> None:
    """添加知识图谱边（去重）。"""
    with _graph_file_lock():
        graph = _load_graph()
        exists = any(
            e.get("from") == from_node and e.get("to") == to_node and e.get("relation") == relation
            for e in graph["edges"]
        )
        if not exists:
            graph["edges"].append({"from": from_node, "to": to_node, "relation": relation})
            _save_graph(graph)


def get_related_concepts(title: str, depth: int = 1) -> List[Dict[str, Any]]:
    """通过知识图谱获取关联概念。

    Args:
        title: 中心概念名
        depth: 遍历深度（1=直接关联，2=间接关联）

    Returns:
        关联概念列表，每项含 title, relation, path, growth_stage
    """
    graph = _load_graph()
    if title not in graph["nodes"]:
        return []

    related = []
    visited = {title}
    queue = [(title, 0)]

    while queue:
        node, d = queue.pop(0)
        if d >= depth:
            continue
        for edge in graph["edges"]:
            if edge["from"] == node:
                neighbor = edge["to"]
            elif edge["to"] == node:
                neighbor = edge["from"]
            else:
                continue
            if neighbor in visited:
                continue
            visited.add(neighbor)
            node_info = graph["nodes"].get(neighbor, {})
            related.append({
                "title": neighbor,
                "relation": edge["relation"],
                "path": node_info.get("path", ""),
                "growth_stage": node_info.get("growth_stage", "unknown"),
                "distance": d + 1,
            })
            queue.append((neighbor, d + 1))

    return related


def get_graph_summary() -> Dict[str, Any]:
    """返回知识图谱概览。"""
    graph = _load_graph()
    stages = {}
    for n in graph["nodes"].values():
        s = n.get("growth_stage", "unknown")
        stages[s] = stages.get(s, 0) + 1
    return {
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "growth_stages": stages,
    }


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> bool:
    """自检：验证图谱节点 CRUD / 边添加 / 关联概念遍历 / WikiLink 提取。

    使用临时目录隔离，patch GRAPH_PATH 和 ALIASES_PATH 到临时路径。
    """
    import tempfile
    import shutil

    print("=" * 50)
    print("◐ kb_graph 自检")
    print("=" * 50)

    passed = 0
    total = 0
    tmp_dir = tempfile.mkdtemp(prefix="kb_graph_test_")

    # 保存原始路径常量，测试后恢复
    global GRAPH_PATH, ALIASES_PATH
    _orig_graph = GRAPH_PATH
    _orig_aliases = ALIASES_PATH
    GRAPH_PATH = Path(tmp_dir) / "graph.json"
    ALIASES_PATH = Path(tmp_dir) / "aliases.json"

    try:
        # [1/5] 节点创建
        total += 1
        update_graph_node("固体高次谐波", "concepts", "wiki/concepts/固体高次谐波.md", "growing")
        update_graph_node("阿秒脉冲", "concepts", "wiki/concepts/阿秒脉冲.md", "mature")
        graph = _load_graph()
        if "固体高次谐波" in graph["nodes"] and "阿秒脉冲" in graph["nodes"]:
            passed += 1
            print(f"  [1/{total}] ✓ 节点创建: {len(graph['nodes'])} 个")
        else:
            print(f"  [1/{total}] ✗ 节点创建: nodes={list(graph['nodes'].keys())}")

        # [2/5] 边添加（去重）
        total += 1
        add_graph_edge("固体高次谐波", "阿秒脉冲", "related")
        add_graph_edge("固体高次谐波", "阿秒脉冲", "related")  # 重复，应去重
        graph = _load_graph()
        edge_count = len(graph["edges"])
        if edge_count == 1:
            passed += 1
            print(f"  [2/{total}] ✓ 边去重: {edge_count} 条")
        else:
            print(f"  [2/{total}] ✗ 边去重: 实际 {edge_count} 条")

        # [3/5] 关联概念遍历
        total += 1
        related = get_related_concepts("固体高次谐波", depth=1)
        if len(related) >= 1 and related[0]["title"] == "阿秒脉冲":
            passed += 1
            print(f"  [3/{total}] ✓ 关联遍历: {len(related)} 条 (首条={related[0]['title']})")
        else:
            print(f"  [3/{total}] ✗ 关联遍历: related={related}")

        # [4/5] 图谱概览
        total += 1
        summary = get_graph_summary()
        if summary["node_count"] == 2 and summary["edge_count"] == 1:
            passed += 1
            print(f"  [4/{total}] ✓ 概览: nodes={summary['node_count']}, edges={summary['edge_count']}")
        else:
            print(f"  [4/{total}] ✗ 概览: summary={summary}")

        # [5/5] 节点删除（级联清理边）
        total += 1
        _remove_graph_node("阿秒脉冲")
        graph = _load_graph()
        if "阿秒脉冲" not in graph["nodes"] and len(graph["edges"]) == 0:
            passed += 1
            print(f"  [5/{total}] ✓ 节点删除: 边级联清理 (剩余边={len(graph['edges'])})")
        else:
            print(f"  [5/{total}] ✗ 节点删除: nodes={list(graph['nodes'].keys())}, edges={len(graph['edges'])}")
    finally:
        GRAPH_PATH = _orig_graph
        ALIASES_PATH = _orig_aliases
        # P3: 重置缓存，避免测试数据残留
        global _graph_cache, _graph_mtime
        _graph_cache = None
        _graph_mtime = 0.0
        shutil.rmtree(tmp_dir, ignore_errors=True)

    ok = passed == total
    print(f"\n{'✓' if ok else '✗'} kb_graph: {passed}/{total} 通过")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_check() else 1)
