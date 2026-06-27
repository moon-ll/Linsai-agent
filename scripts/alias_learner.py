#!/usr/bin/env python3
"""别名自动发现引擎 —— 从知识库使用中学习别名候选。

三个发现来源：
1. [[WikiLink|显示名]] 的别名用法（如 [[三步模型|半经典模型]]）
2. frontmatter 的 aliases 字段（已声明但未录入 aliases.json）
3. 图谱 same_as 边（已声明的同义关系）

生成的候选需用户在别名 tab 确认后才生效。

用法:
    python scripts/alias_learner.py              # 发现别名候选
    python scripts/alias_learner.py --apply       # 将候选写入 aliases.json（需先确认）

规范:
    - 仅使用 Python 3 标准库
    - 不自动修改 aliases.json，只生成候选列表
    - 候选存储在 memory/alias-candidates.json
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from common import now_utc as _now_utc

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
MEMORY_DIR = PROJECT_ROOT / "memory"
ALIASES_PATH = KNOWLEDGE_DIR / "aliases.json"
CANDIDATES_PATH = MEMORY_DIR / "alias-candidates.json"

# [[WikiLink|别名]] 模式
_WIKILINK_ALIAS_RE = re.compile(r"\[\[([^\]\|]+)\|([^\]]+)\]\]")


def _load_aliases() -> Dict[str, List[str]]:
    """加载现有别名表。"""
    if not ALIASES_PATH.exists():
        return {}
    try:
        return json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_wiki_pages() -> List[Tuple[str, str, Dict[str, Any]]]:
    """加载所有 wiki 页面，返回 (path, text, frontmatter) 列表。"""
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import list_wiki_pages, get_wiki_page, parse_frontmatter

    pages = []
    for p in list_wiki_pages():
        path = p.get("path", "")
        full = get_wiki_page(path)
        if full:
            pages.append((path, full.get("body", ""), full.get("frontmatter", {})))
        else:
            # 直接读文件
            fpath = KNOWLEDGE_DIR / path
            if fpath.exists():
                text = fpath.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(text)
                pages.append((path, body, fm))
    return pages


def discover_from_wikilinks() -> List[Dict[str, str]]:
    """从 [[WikiLink|别名]] 用法中发现别名候选。

    Returns:
        [{"canonical": "三步模型", "alias": "半经典模型", "source": "wikilink", "path": "..."}]
    """
    candidates = []
    pages = _load_wiki_pages()

    for path, body, fm in pages:
        for m in _WIKILINK_ALIAS_RE.finditer(body):
            canonical = m.group(1).strip()
            alias = m.group(2).strip()
            if canonical and alias and canonical != alias:
                candidates.append({
                    "canonical": canonical,
                    "alias": alias,
                    "source": "wikilink",
                    "path": path,
                })
    return candidates


def discover_from_frontmatter() -> List[Dict[str, str]]:
    """从 frontmatter 的 aliases 字段发现别名候选。

    Returns:
        [{"canonical": "三步模型", "alias": "半经典模型", "source": "frontmatter", "path": "..."}]
    """
    candidates = []
    pages = _load_wiki_pages()

    for path, body, fm in pages:
        title = fm.get("title", "")
        aliases = fm.get("aliases", [])
        if not title or not aliases:
            continue
        if isinstance(aliases, str):
            aliases = [aliases]
        for alias in aliases:
            if alias and alias != title:
                candidates.append({
                    "canonical": title,
                    "alias": str(alias).strip(),
                    "source": "frontmatter",
                    "path": path,
                })
    return candidates


def discover_from_graph() -> List[Dict[str, str]]:
    """从图谱 same_as 边发现别名候选。

    Returns:
        [{"canonical": "三步模型", "alias": "半经典模型", "source": "graph"}]
    """
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import _load_graph

    graph = _load_graph()
    candidates = []
    for edge in graph.get("edges", []):
        if edge.get("relation") == "same_as":
            candidates.append({
                "canonical": edge.get("from", ""),
                "alias": edge.get("to", ""),
                "source": "graph",
            })
    return candidates


def filter_new_candidates(candidates: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """过滤掉已在 aliases.json 中的候选。"""
    aliases = _load_aliases()
    existing: Set[Tuple[str, str]] = set()
    for canonical, alts in aliases.items():
        for alt in alts:
            existing.add((canonical.lower(), alt.lower()))
            # 反向也标记
            existing.add((alt.lower(), canonical.lower()))

    new = []
    seen: Set[Tuple[str, str]] = set()
    for c in candidates:
        key = (c["canonical"].lower(), c["alias"].lower())
        if key in existing or key in seen:
            continue
        seen.add(key)
        new.append(c)
    return new


def discover_all() -> List[Dict[str, str]]:
    """运行所有发现器，返回去重后的新候选列表。"""
    all_candidates = []
    all_candidates.extend(discover_from_wikilinks())
    all_candidates.extend(discover_from_frontmatter())
    all_candidates.extend(discover_from_graph())
    return filter_new_candidates(all_candidates)


def save_candidates(candidates: List[Dict[str, str]]) -> None:
    """保存候选到 memory/alias-candidates.json。"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "candidates": candidates,
        "discovered_at": _now_utc(),
        "count": len(candidates),
    }
    CANDIDATES_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_candidates() -> List[Dict[str, str]]:
    """加载已保存的候选。"""
    if not CANDIDATES_PATH.exists():
        return []
    try:
        data = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
        return data.get("candidates", [])
    except Exception:
        return []


def apply_candidates(indices: List[int]) -> Dict[str, Any]:
    """将指定候选写入 aliases.json。

    Args:
        indices: 要应用的候选索引列表

    Returns:
        {"applied": N, "skipped": M}
    """
    candidates = load_candidates()
    aliases = _load_aliases()

    applied = 0
    skipped = 0
    for idx in indices:
        if idx < 0 or idx >= len(candidates):
            skipped += 1
            continue
        c = candidates[idx]
        canonical = c["canonical"]
        alias = c["alias"]
        if canonical not in aliases:
            aliases[canonical] = []
        if alias not in aliases[canonical]:
            aliases[canonical].append(alias)
            applied += 1
        else:
            skipped += 1

    ALIASES_PATH.write_text(
        json.dumps(aliases, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"applied": applied, "skipped": skipped}


def _self_check() -> None:
    """自检。"""
    print("=" * 50)
    print("◐ alias_learner 自检")
    print("=" * 50)

    print("\n[1/3] 加载现有别名...")
    aliases = _load_aliases()
    print(f"  现有别名: {len(aliases)} 组")

    print("\n[2/3] 发现别名候选...")
    candidates = discover_all()
    print(f"  发现新候选: {len(candidates)} 个")
    for c in candidates[:10]:
        print(f"    [{c['source']}] {c['canonical']} ← {c['alias']}")
    if len(candidates) > 10:
        print(f"    ... 还有 {len(candidates) - 10} 个")

    print("\n[3/3] 保存候选...")
    save_candidates(candidates)
    print(f"  ✓ 已保存到 {CANDIDATES_PATH}")

    print("\n✓ alias_learner 自检通过")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="别名自动发现引擎")
    parser.add_argument("--apply", action="store_true", help="将所有候选写入 aliases.json")
    args = parser.parse_args()

    if args.apply:
        candidates = load_candidates()
        if not candidates:
            print("○ 无候选可应用，先运行发现")
        else:
            result = apply_candidates(list(range(len(candidates))))
            print(f"✓ 应用 {result['applied']} 个别名，跳过 {result['skipped']} 个")
    else:
        _self_check()
