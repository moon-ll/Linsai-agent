#!/usr/bin/env python3
"""kb_health.py — 知识库健康度与维护。

计算知识库健康度指标：图谱连通性、分类覆盖率、别名命中率、孤儿节点数，
并汇总为仪表盘可用的健康度报告。

依赖：kb_graph（图谱加载/概览）、kb_index（索引状态/raw 列表）、
      kb_wiki（wiki 列表/读取）、paths（KNOWLEDGE_DIR）。

门面 knowledge_base 在加载完成后会向本模块注入以下函数，以解决子模块→门面依赖：
    get_growth_candidates — 待生长概念列表
    get_growth_log        — 生长日志查询
在门面未注入前这些名字为 None 占位，函数体保持与原 knowledge_base.py 完全一致。

用法示例：
    >>> from kb_health import get_kb_health
    >>> health = get_kb_health()
    >>> print(health["graph_connectivity"])

规范：
    - 仅使用 Python 3 标准库
    - 不修改任何函数逻辑，自 knowledge_base.py 物理迁移而来
"""

import json
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict

from paths import KNOWLEDGE_DIR
from kb_graph import _load_graph, get_graph_summary
from kb_index import get_index_status, list_raw_files
from kb_wiki import list_wiki_pages, get_wiki_page


# ─────────────────────────────────────────────
# 门面注入依赖（占位，由 knowledge_base 加载后覆盖）
# ─────────────────────────────────────────────

get_growth_candidates = None  # type: ignore
get_growth_log = None  # type: ignore


# ─────────────────────────────────────────────
# 健康度指标
# ─────────────────────────────────────────────

def get_kb_health() -> Dict[str, Any]:
    """返回知识库健康度数据，供仪表盘使用。"""
    status = get_index_status()
    graph = get_graph_summary()
    candidates = get_growth_candidates()

    # 统计 capture 文件
    capture_dir = KNOWLEDGE_DIR / "captures"
    capture_count = len(list(capture_dir.glob("*.md"))) if capture_dir.exists() else 0

    # 统计本周新增（基于 growth-log）
    log = get_growth_log(limit=200)
    week_count = 0
    try:
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        for entry in log:
            ts = entry.get("timestamp", "")
            if ts:
                try:
                    et = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if et >= week_ago:
                        week_count += 1
                except Exception:
                    pass
    except Exception:
        pass

    # 待蒸馏 raw：已索引但未关联 wiki 的 raw 文件
    raw_files = list_raw_files()
    wiki_from_raw = set()
    for page in list_wiki_pages():
        fm = get_wiki_page(page.get("path", ""))
        if fm:
            src = fm.get("frontmatter", {}).get("source_raw", "")
            if src:
                wiki_from_raw.add(src)
    pending_distill = len([f for f in raw_files if f["name"] not in wiki_from_raw])

    # v3.1.2: 图谱连通性（最大连通分量占比）
    graph_conn = _compute_graph_connectivity()

    # v3.1.2: 分类覆盖率
    category_coverage = _compute_category_coverage()

    # v3.1.2: 别名命中率
    alias_hit_rate = _compute_alias_hit_rate()

    return {
        "indexed": status.get("indexed", False),
        "raw_count": status.get("raw_count", 0),
        "wiki_count": status.get("wiki_count", 0),
        "capture_count": capture_count,
        "chunks": status.get("chunks", 0),
        "growth_stages": graph.get("growth_stages", {}),
        "graph_nodes": graph.get("node_count", 0),
        "graph_edges": graph.get("edge_count", 0),
        "graph_orphans": _count_graph_orphans(),
        "graph_connectivity": graph_conn,
        "category_coverage": category_coverage,
        "alias_hit_rate": alias_hit_rate,
        "week_new": week_count,
        "pending_distill": pending_distill,
        "growth_candidates": len(candidates),
        "built_at": status.get("built_at", ""),
    }


def _compute_graph_connectivity() -> float:
    """计算图谱连通性：最大连通分量节点数 / 总节点数。"""
    graph = _load_graph()
    nodes = graph.get("nodes", {})
    edges = graph.get("edges", [])
    if not nodes:
        return 0.0

    # 构建邻接表
    adj: Dict[str, set] = defaultdict(set)
    for edge in edges:
        f = edge.get("from", "")
        t = edge.get("to", "")
        if f and t:
            adj[f].add(t)
            adj[t].add(f)

    # BFS 找最大连通分量
    visited: set = set()
    max_component = 0
    for node in nodes:
        if node in visited:
            continue
        queue = deque([node])
        component_size = 0
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            component_size += 1
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        max_component = max(max_component, component_size)

    return round(max_component / len(nodes), 2) if nodes else 0.0


def _compute_category_coverage() -> Dict[str, Any]:
    """计算分类覆盖率：被自定义分类覆盖的 wiki 页面比例。"""
    cat_path = KNOWLEDGE_DIR / "categories.json"
    if not cat_path.exists():
        return {"total_categories": 0, "covered_pages": 0, "coverage_rate": 0.0}
    try:
        data = json.loads(cat_path.read_text(encoding="utf-8"))
        cats = data.get("categories", [])
        covered = set()
        for cat in cats:
            for p in cat.get("matched_paths", []):
                covered.add(p)
        wiki_count = len(list_wiki_pages())
        return {
            "total_categories": len(cats),
            "covered_pages": len(covered),
            "coverage_rate": round(len(covered) / wiki_count, 2) if wiki_count else 0.0,
        }
    except Exception:
        return {"total_categories": 0, "covered_pages": 0, "coverage_rate": 0.0}


def _compute_alias_hit_rate() -> Dict[str, Any]:
    """计算别名命中率：aliases.json 中的别名在 wiki 中被使用的比例。"""
    aliases_path = KNOWLEDGE_DIR / "aliases.json"
    if not aliases_path.exists():
        return {"total_aliases": 0, "used_aliases": 0, "hit_rate": 0.0}
    try:
        aliases = json.loads(aliases_path.read_text(encoding="utf-8"))
        total = 0
        used = 0
        # 收集所有 wiki 文本
        wiki_texts = []
        for page in list_wiki_pages():
            full = get_wiki_page(page.get("path", ""))
            if full:
                wiki_texts.append(full.get("body", "").lower())

        for canonical, alts in aliases.items():
            for alt in alts:
                total += 1
                alt_lower = alt.lower()
                if any(alt_lower in wt for wt in wiki_texts):
                    used += 1

        return {
            "total_aliases": total,
            "used_aliases": used,
            "hit_rate": round(used / total, 2) if total else 0.0,
        }
    except Exception:
        return {"total_aliases": 0, "used_aliases": 0, "hit_rate": 0.0}


def _count_graph_orphans() -> int:
    """统计知识图谱中无对应 wiki 文件的孤儿节点。"""
    graph = _load_graph()
    orphans = 0
    for title, node in graph.get("nodes", {}).items():
        path = node.get("path", "")
        if path and not (KNOWLEDGE_DIR / path).exists():
            orphans += 1
    return orphans


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> bool:
    """自检：验证健康度计算 / 图谱连通性 / 孤儿节点 / 别名命中率。

    使用临时目录隔离，patch 多模块路径常量并注入门面依赖桩。
    """
    import tempfile
    import shutil

    print("=" * 50)
    print("◐ kb_health 自检")
    print("=" * 50)

    passed = 0
    total = 0
    tmp_dir = tempfile.mkdtemp(prefix="kb_health_test_")
    tmp_kb = Path(tmp_dir) / "knowledge"
    (tmp_kb / "wiki" / "concepts").mkdir(parents=True, exist_ok=True)
    (tmp_kb / "raw" / "notes").mkdir(parents=True, exist_ok=True)
    (tmp_kb / "captures").mkdir(parents=True, exist_ok=True)

    # 保存原始路径常量
    global KNOWLEDGE_DIR, get_growth_candidates, get_growth_log
    _orig_kbh = {"KNOWLEDGE_DIR": KNOWLEDGE_DIR}
    KNOWLEDGE_DIR = tmp_kb

    # patch kb_index 路径
    import kb_index as _ki
    _orig_ki = {
        "INDEX_PATH": _ki.INDEX_PATH, "KNOWLEDGE_DIR": _ki.KNOWLEDGE_DIR,
        "RAW_DIR": _ki.RAW_DIR, "WIKI_DIR": _ki.WIKI_DIR,
    }
    _ki.INDEX_PATH = tmp_kb / "index.json"
    _ki.KNOWLEDGE_DIR = tmp_kb
    _ki.RAW_DIR = tmp_kb / "raw"
    _ki.WIKI_DIR = tmp_kb / "wiki"

    # patch kb_graph 路径
    import kb_graph as _kg
    _orig_kg = {"GRAPH_PATH": _kg.GRAPH_PATH, "ALIASES_PATH": _kg.ALIASES_PATH}
    _kg.GRAPH_PATH = tmp_kb / "graph.json"
    _kg.ALIASES_PATH = tmp_kb / "aliases.json"

    # patch kb_wiki 路径
    import kb_wiki as _kw
    _orig_kw = {"KNOWLEDGE_DIR": _kw.KNOWLEDGE_DIR, "WIKI_DIR": _kw.WIKI_DIR}
    _kw.KNOWLEDGE_DIR = tmp_kb
    _kw.WIKI_DIR = tmp_kb / "wiki"

    # 保存原始注入依赖
    _orig_deps = {"get_growth_candidates": get_growth_candidates, "get_growth_log": get_growth_log}

    try:
        # 注入门面依赖桩
        get_growth_candidates = lambda: []
        get_growth_log = lambda limit=50, target=None: []

        # 准备测试数据：图谱（2 节点 + 1 边，全连通）
        import json
        graph_data = {
            "nodes": {
                "概念A": {"type": "concepts", "path": "wiki/concepts/概念A.md", "growth_stage": "mature"},
                "概念B": {"type": "concepts", "path": "wiki/concepts/概念B.md", "growth_stage": "growing"},
                "孤儿概念": {"type": "concepts", "path": "wiki/concepts/不存在.md", "growth_stage": "seedling"},
            },
            "edges": [
                {"from": "概念A", "to": "概念B", "relation": "related"},
            ],
        }
        _kg._save_graph(graph_data)

        # 创建对应的 wiki 文件（概念A、概念B 存在，孤儿概念不存在）
        for name in ["概念A", "概念B"]:
            (tmp_kb / "wiki" / "concepts" / f"{name}.md").write_text(
                f'---\ntitle: "{name}"\ntype: "concepts"\ngrowth_stage: "mature"\n---\n内容', encoding="utf-8")

        # 准备索引数据
        index_data = {
            "documents": {
                "wiki/concepts/概念A.md": {"source": "wiki", "chunks": 1},
                "raw/notes/test.md": {"source": "raw", "chunks": 1},
            },
            "inverted": {}, "idf": {}, "doc_count": 2,
            "built_at": "2026-06-28T00:00:00Z",
            "graph_summary": {"node_count": 3, "edge_count": 1, "growth_stages": {"mature": 2}},
        }
        _ki._cms.save_json(tmp_kb / "index.json", index_data)

        # 准备别名
        (tmp_kb / "aliases.json").write_text(
            json.dumps({"概念A": ["CA", "A概念"]}, ensure_ascii=False), encoding="utf-8")

        # [1/5] 图谱连通性
        total += 1
        conn = _compute_graph_connectivity()
        # 概念A-B 连通（2节点），孤儿概念独立（1节点），最大分量=2，总=3，连通性=0.67
        if isinstance(conn, float) and 0.6 <= conn <= 0.7:
            passed += 1
            print(f"  [1/{total}] ✓ 连通性: {conn} (最大分量 2/3)")
        else:
            print(f"  [1/{total}] ✗ 连通性: conn={conn}")

        # [2/5] 孤儿节点计数
        total += 1
        orphans = _count_graph_orphans()
        if orphans == 1:
            passed += 1
            print(f"  [2/{total}] ✓ 孤儿节点: {orphans} 个")
        else:
            print(f"  [2/{total}] ✗ 孤儿节点: orphans={orphans}")

        # [3/5] 别名命中率
        total += 1
        alias_rate = _compute_alias_hit_rate()
        # 别名 "CA" 和 "A概念" 在 wiki 正文（"内容"）中未出现 → hit_rate=0.0
        if alias_rate["total_aliases"] == 2 and alias_rate["hit_rate"] == 0.0:
            passed += 1
            print(f"  [3/{total}] ✓ 别名命中率: {alias_rate['hit_rate']} (总 {alias_rate['total_aliases']})")
        else:
            print(f"  [3/{total}] ✗ 别名命中率: {alias_rate}")

        # [4/5] 分类覆盖率（无 categories.json → 空结果）
        total += 1
        cat_cov = _compute_category_coverage()
        if cat_cov["total_categories"] == 0 and cat_cov["coverage_rate"] == 0.0:
            passed += 1
            print(f"  [4/{total}] ✓ 分类覆盖率: 空配置返回 0.0")
        else:
            print(f"  [4/{total}] ✗ 分类覆盖率: {cat_cov}")

        # [5/5] 综合健康度
        total += 1
        health = get_kb_health()
        if (health.get("graph_nodes") == 3 and health.get("graph_orphans") == 1
                and health.get("indexed") is True):
            passed += 1
            print(f"  [5/{total}] ✓ 综合健康度: nodes={health['graph_nodes']}, orphans={health['graph_orphans']}")
        else:
            print(f"  [5/{total}] ✗ 综合健康度: {health}")
    finally:
        # 恢复所有路径常量
        KNOWLEDGE_DIR = _orig_kbh["KNOWLEDGE_DIR"]
        _ki.INDEX_PATH = _orig_ki["INDEX_PATH"]
        _ki.KNOWLEDGE_DIR = _orig_ki["KNOWLEDGE_DIR"]
        _ki.RAW_DIR = _orig_ki["RAW_DIR"]
        _ki.WIKI_DIR = _orig_ki["WIKI_DIR"]
        _kg.GRAPH_PATH = _orig_kg["GRAPH_PATH"]
        _kg.ALIASES_PATH = _orig_kg["ALIASES_PATH"]
        _kw.KNOWLEDGE_DIR = _orig_kw["KNOWLEDGE_DIR"]
        _kw.WIKI_DIR = _orig_kw["WIKI_DIR"]
        # 恢复注入依赖
        get_growth_candidates = _orig_deps["get_growth_candidates"]
        get_growth_log = _orig_deps["get_growth_log"]
        shutil.rmtree(tmp_dir, ignore_errors=True)

    ok = passed == total
    print(f"\n{'✓' if ok else '✗'} kb_health: {passed}/{total} 通过")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_check() else 1)
