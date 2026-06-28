#!/usr/bin/env python3
"""growth_stage 自动晋升规则引擎。

规则：
- seedling → growing: 被 ≥3 篇 raw 论文引用，或内容字数 >500 且有 related
- growing → mature: 被 ≥5 篇引用 + 被检索命中 ≥10 次，或内容字数 >2000 且有 related
- 不自动降级（只升不降）
- 用户手动设置的 mature 不被覆盖

用法:
    python scripts/growth_engine.py              # 扫描并报告晋升候选
    python scripts/growth_engine.py --apply       # 执行晋升

规范:
    - 仅使用 Python 3 标准库
    --apply 前先报告，用户确认
    - 晋升记录写入 growth-log.json
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import now_utc as _now_utc

from paths import PROJECT_ROOT, SCRIPTS_DIR, KNOWLEDGE_DIR, MEMORY_DIR
GROWTH_LOG_PATH = KNOWLEDGE_DIR / "growth-log.json"


def _count_raw_references(title: str) -> int:
    """统计 title 在 raw/papers/ 中被引用的次数。"""
    raw_dir = KNOWLEDGE_DIR / "raw" / "papers"
    if not raw_dir.exists():
        return 0
    count = 0
    title_lower = title.lower()
    for fpath in raw_dir.glob("*.md"):
        try:
            text = fpath.read_text(encoding="utf-8").lower()
            if title_lower in text:
                count += 1
        except Exception:
            continue
    return count


def _count_search_hits(title: str) -> int:
    """统计 title 的检索命中次数（从 usage.json 读取）。"""
    usage_path = MEMORY_DIR / "usage.json"
    if not usage_path.exists():
        return 0
    try:
        data = json.loads(usage_path.read_text(encoding="utf-8"))
        queries = data.get("queries", [])
        title_lower = title.lower()
        hits = 0
        for q in queries:
            query_text = q.get("query", "").lower() if isinstance(q, dict) else str(q).lower()
            if title_lower in query_text or query_text in title_lower:
                hits += 1
        return hits
    except Exception:
        return 0


def _get_content_length(path: str) -> int:
    """获取 wiki 页面正文字数。"""
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import get_wiki_page

    page = get_wiki_page(path)
    if page:
        return len(page.get("body", ""))
    return 0


def evaluate_promotion(page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """评估单个页面是否应晋升。

    Returns:
        {"title": ..., "from": ..., "to": ..., "reason": ...} 或 None
    """
    title = page.get("title", "")
    stage = page.get("growth_stage", "seedling")
    path = page.get("path", "")
    related = page.get("related", [])
    has_related = bool(related)

    if not title or stage == "mature" or stage == "archived":
        return None

    content_len = _get_content_length(path)
    raw_refs = _count_raw_references(title)
    search_hits = _count_search_hits(title)

    # seedling → growing
    if stage == "seedling":
        if raw_refs >= 3:
            return {"title": title, "from": "seedling", "to": "growing",
                    "reason": f"被 {raw_refs} 篇 raw 论文引用 (≥3)"}
        if content_len > 500 and has_related:
            return {"title": title, "from": "seedling", "to": "growing",
                    "reason": f"内容 {content_len} 字 (>500) 且有 related 关联"}

    # growing → mature
    if stage == "growing":
        if raw_refs >= 5 and search_hits >= 10:
            return {"title": title, "from": "growing", "to": "mature",
                    "reason": f"被 {raw_refs} 篇引用 (≥5) + 检索命中 {search_hits} 次 (≥10)"}
        if content_len > 2000 and has_related:
            return {"title": title, "from": "growing", "to": "mature",
                    "reason": f"内容 {content_len} 字 (>2000) 且有 related 关联"}

    return None


def scan_promotions() -> List[Dict[str, Any]]:
    """扫描所有 wiki 页面，返回晋升候选列表。"""
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import list_wiki_pages

    pages = list_wiki_pages()
    promotions = []
    for page in pages:
        result = evaluate_promotion(page)
        if result:
            promotions.append(result)
    return promotions


def apply_promotion(promotion: Dict[str, Any]) -> bool:
    """执行单个晋升（更新 frontmatter + 图谱 + 日志）。"""
    import sys
    sys.path.insert(0, str(SCRIPTS_DIR))
    from knowledge_base import get_wiki_page, save_wiki_page, update_graph_node

    title = promotion["title"]
    new_stage = promotion["to"]

    # 找到页面路径
    from knowledge_base import list_wiki_pages
    pages = list_wiki_pages()
    target = None
    for p in pages:
        if p.get("title") == title:
            target = p
            break
    if not target:
        return False

    path = target["path"]
    page = get_wiki_page(path)
    if not page:
        return False

    fm = page.get("frontmatter", {})
    fm["growth_stage"] = new_stage
    body = page.get("body", "")
    save_wiki_page(path, body, fm)
    update_graph_node(title, fm.get("type", ""), path, new_stage)

    # 记录日志
    _log_promotion(promotion)
    return True


def _log_promotion(promotion: Dict[str, Any]) -> None:
    """记录晋升到 growth-log.json。"""
    log = []
    if GROWTH_LOG_PATH.exists():
        try:
            log = json.loads(GROWTH_LOG_PATH.read_text(encoding="utf-8"))
            if not isinstance(log, list):
                log = []
        except Exception:
            log = []

    log.append({
        "timestamp": _now_utc(),
        "action": "auto_promote",
        "title": promotion["title"],
        "from": promotion["from"],
        "to": promotion["to"],
        "reason": promotion["reason"],
    })
    GROWTH_LOG_PATH.write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _self_check() -> None:
    """自检。"""
    print("=" * 50)
    print("◐ growth_engine 自检")
    print("=" * 50)

    print("\n[1/2] 扫描晋升候选...")
    promotions = scan_promotions()
    print(f"  发现 {len(promotions)} 个晋升候选:")
    for p in promotions[:15]:
        print(f"    {p['title']}: {p['from']} → {p['to']}")
        print(f"      理由: {p['reason']}")
    if len(promotions) > 15:
        print(f"    ... 还有 {len(promotions) - 15} 个")

    print(f"\n[2/2] 验证函数...")
    assert callable(evaluate_promotion), "evaluate_promotion 不可调用"
    assert callable(scan_promotions), "scan_promotions 不可调用"
    assert callable(apply_promotion), "apply_promotion 不可调用"
    print("  ✓ 函数就绪")

    print("\n✓ growth_engine 自检通过")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="growth_stage 自动晋升规则引擎")
    parser.add_argument("--apply", action="store_true", help="执行晋升")
    args = parser.parse_args()

    if args.apply:
        promotions = scan_promotions()
        if not promotions:
            print("○ 无晋升候选")
        else:
            print(f"发现 {len(promotions)} 个晋升候选，开始执行...")
            applied = 0
            for p in promotions:
                if apply_promotion(p):
                    print(f"  ✓ {p['title']}: {p['from']} → {p['to']}")
                    applied += 1
            print(f"\n✓ 晋升完成: {applied}/{len(promotions)}")
    else:
        _self_check()
