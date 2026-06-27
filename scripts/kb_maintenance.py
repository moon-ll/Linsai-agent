#!/usr/bin/env python3
"""知识库维护脚本 —— 集中处理所有 LLM 密集型操作。

用法:
    python scripts/kb_maintenance.py --weekly      # 一键周维护
    python scripts/kb_maintenance.py --reindex     # 仅重建索引
    python scripts/kb_maintenance.py --candidates  # 查看生长/蒸馏候选
    python scripts/kb_maintenance.py --orphans     # 清理孤儿节点
    python scripts/kb_maintenance.py --health      # 输出健康度报告
    python scripts/kb_maintenance.py --captures    # 列出所有 capture

规范:
    - 仅使用 Python 3 标准库
    - 不自动调用 LLM，只生成候选报告供用户决策
    - 输出使用中文，状态图标统一
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc as _now_utc

PROJECT_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


def _import_kb():
    """动态导入 knowledge_base 模块。"""
    import importlib.util
    kb_path = Path(__file__).parent / "knowledge_base.py"
    spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
    kb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb)
    return kb


def cmd_reindex(kb) -> None:
    """重建索引。"""
    print("◐ 重建索引...")
    idx = kb.build_index(force=True)
    docs = idx.get("documents", {})
    raw_count = sum(1 for d in docs.values() if d.get("source") == "raw")
    wiki_count = sum(1 for d in docs.values() if d.get("source") == "wiki")
    capture_count = len(list((KNOWLEDGE_DIR / "captures").glob("*.md"))) if (KNOWLEDGE_DIR / "captures").exists() else 0
    print(f"  ✓ 索引完成: raw={raw_count}, wiki={wiki_count}, captures={capture_count}, chunks={idx.get('doc_count', 0)}")


def cmd_candidates(kb) -> None:
    """列出生长和蒸馏候选。"""
    print("\n◐ 生长候选（seedling 阶段 wiki）")
    candidates = kb.get_growth_candidates()
    if not candidates:
        print("  ○ 无生长候选")
    else:
        for c in candidates[:10]:
            print(f"  ○ {c['title']} [{c['type']}] — {c['reason']}")
        if len(candidates) > 10:
            print(f"  ... 还有 {len(candidates) - 10} 个")

    print("\n◐ 蒸馏候选（未关联 wiki 的 raw 文件）")
    raw_files = kb.list_raw_files()
    wiki_pages = kb.list_wiki_pages()
    wiki_sources = set()
    for page in wiki_pages:
        p = kb.get_wiki_page(page.get("path", ""))
        if p:
            src = p.get("frontmatter", {}).get("source_raw", "")
            if src:
                wiki_sources.add(src)

    pending = [f for f in raw_files if f["name"] not in wiki_sources]
    if not pending:
        print("  ○ 无蒸馏候选")
    else:
        for f in pending[:10]:
            print(f"  ○ {f['path']} ({f['size']} bytes)")
        if len(pending) > 10:
            print(f"  ... 还有 {len(pending) - 10} 个")


def cmd_orphans(kb) -> None:
    """清理知识图谱中的孤儿节点。"""
    print("◐ 扫描孤儿节点...")
    graph = kb._load_graph()
    orphans = []
    for title, node in list(graph.get("nodes", {}).items()):
        path = node.get("path", "")
        if path and not (KNOWLEDGE_DIR / path).exists():
            orphans.append(title)

    if not orphans:
        print("  ✓ 无孤儿节点")
        return

    print(f"  ⚠ 发现 {len(orphans)} 个孤儿节点")
    for title in orphans:
        del graph["nodes"][title]
        graph["edges"] = [e for e in graph["edges"] if e.get("from") != title and e.get("to") != title]
        print(f"    ✓ 已清理: {title}")

    kb._save_graph(graph)
    print(f"  ✓ 图谱已更新")


def cmd_captures(kb) -> None:
    """列出 capture 文件。"""
    capture_dir = KNOWLEDGE_DIR / "captures"
    if not capture_dir.exists():
        print("○ 无 capture 文件")
        return

    files = sorted(capture_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    print(f"◐ 共 {len(files)} 个 capture 文件")
    for f in files[:20]:
        text = f.read_text(encoding="utf-8")
        m = __import__("re").match(r"^---\s*\n(.*?)\n---\s*\n", text, __import__("re").DOTALL)
        topics = []
        session = ""
        if m:
            for line in m.group(1).strip().split("\n"):
                if line.startswith("topics:"):
                    inner = line[len("topics:"):].strip().strip("[]")
                    topics = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
                elif line.startswith("session:"):
                    session = line[len("session:"):].strip().strip('"').strip("'")
        topics_str = ", ".join(topics[:3]) if topics else "未分类"
        print(f"  ○ {f.name} | 会话: {session} | 话题: {topics_str}")


def cmd_health(kb) -> None:
    """输出健康度报告。"""
    health = kb.get_kb_health()
    print("\n┌─────────────────────────────────────────────┐")
    print("│           知识库健康度报告                   │")
    print("├─────────────────────────────────────────────┤")
    print(f"│  索引状态    {'✓ 已索引' if health['indexed'] else '✗ 未索引'}")
    print(f"│  总条目      raw: {health['raw_count']:<3}  wiki: {health['wiki_count']:<3}  capture: {health['capture_count']}")
    stages = health.get("growth_stages", {})
    seedling = stages.get("seedling", 0)
    growing = stages.get("growing", 0)
    mature = stages.get("mature", 0)
    print(f"│  生长分布    🌱{seedling:<3} 🌿{growing:<3} 🌳{mature}")
    print(f"│  图谱        节点: {health['graph_nodes']:<3} 边: {health['graph_edges']:<3} 孤儿: {health['graph_orphans']}")
    print(f"│  本周新增    {health['week_new']} 条")
    print(f"│  待蒸馏      {health['pending_distill']} 个 raw 文件")
    print(f"│  生长候选    {health['growth_candidates']} 个")
    print(f"│  索引时间    {health['built_at'][:19] if health['built_at'] else '未知'}")
    print("└─────────────────────────────────────────────┘")


def cmd_rebuild_graph(kb) -> None:
    """从所有 wiki 页面的 frontmatter 反向重建知识图谱。

    扫描 wiki/ 下全部 Markdown，提取 frontmatter 中的 title / type /
    growth_stage / related / project 字段，重建 graph.json 的节点与边。
    解决 import_candidate / import_deep_analysis 直接 write_text 绕过
    save_wiki_page 导致的图谱断层问题。
    """
    print("⏳ 重建知识图谱…")

    pages = kb.list_wiki_pages()
    if not pages:
        print("⚠ 没有 wiki 页面，跳过")
        return

    nodes: dict = {}
    edges: list = []
    edge_set: set = set()  # (from, to, relation) 去重

    for page in pages:
        fm = page.get("frontmatter", {})
        title = fm.get("title", "")
        if not title:
            # 从文件名推导标题
            title = page.get("path", "").rsplit("/", 1)[-1].replace(".md", "")

        wiki_type = fm.get("type", "")
        growth_stage = fm.get("growth_stage", "seedling")
        path = page.get("path", "")

        # 创建节点
        nodes[title] = {
            "type": wiki_type,
            "path": path,
            "growth_stage": growth_stage,
        }

        # 从 related 字段创建边
        related = fm.get("related", [])
        if isinstance(related, str):
            related = [related]
        if isinstance(related, list):
            for target in related:
                if target and target != title:
                    key = (title, target, "related")
                    if key not in edge_set:
                        edge_set.add(key)
                        edges.append({"from": title, "to": target, "relation": "related"})

        # 从 project 字段创建边
        project = fm.get("project", "")
        if isinstance(project, str) and project:
            project = [project]
        if isinstance(project, list):
            for proj in project:
                if proj and proj != title:
                    key = (title, proj, "project")
                    if key not in edge_set:
                        edge_set.add(key)
                        edges.append({"from": title, "to": proj, "relation": "project"})

    # 一次性保存
    graph = {"nodes": nodes, "edges": edges}
    kb._save_graph(graph)

    print(f"✓ 知识图谱重建完成: {len(nodes)} 节点, {len(edges)} 边")


def cmd_weekly(kb) -> None:
    """一键周维护。"""
    print(f"\n{'='*50}")
    print(f"  知识库周维护 —— {_now_utc()[:10]}")
    print(f"{'='*50}\n")

    # 1. 重建索引
    cmd_reindex(kb)

    # 2. 重建知识图谱
    print()
    cmd_rebuild_graph(kb)

    # 3. 清理孤儿
    print()
    cmd_orphans(kb)

    # 4. 候选报告
    print()
    cmd_candidates(kb)

    # 5. 健康度
    print()
    cmd_health(kb)

    print(f"\n{'='*50}")
    print("  周维护完成。请查看上述报告，决定是否手动执行蒸馏/生长。")
    print(f"{'='*50}")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="林赛知识库维护脚本")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--weekly", action="store_true", help="一键周维护")
    group.add_argument("--reindex", action="store_true", help="重建索引")
    group.add_argument("--candidates", action="store_true", help="查看生长/蒸馏候选")
    group.add_argument("--orphans", action="store_true", help="清理孤儿节点")
    group.add_argument("--captures", action="store_true", help="列出 capture 文件")
    group.add_argument("--health", action="store_true", help="输出健康度报告")
    group.add_argument("--rebuild-graph", action="store_true", help="从 frontmatter 反向重建知识图谱")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    kb = _import_kb()

    if args.weekly:
        cmd_weekly(kb)
    elif args.reindex:
        cmd_reindex(kb)
    elif args.candidates:
        cmd_candidates(kb)
    elif args.orphans:
        cmd_orphans(kb)
    elif args.captures:
        cmd_captures(kb)
    elif args.health:
        cmd_health(kb)
    elif args.rebuild_graph:
        cmd_rebuild_graph(kb)


if __name__ == "__main__":
    main()
