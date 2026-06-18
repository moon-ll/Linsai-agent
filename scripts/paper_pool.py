#!/usr/bin/env python3
"""文献候选池 —— 三状态持久化管理。

用途：
    管理每日文献候选的生命周期，支持累积、分状态查看、按需归档。
    解决"不一定每天都能及时看"的问题——未决定的候选永远留在池中。

三状态：
    unseen   — 未看（新增候选默认状态）
    viewed   — 已看过但未讨论/未决定（用户标记"稍后"）
    archived — 已讨论完成，已归档到知识库

数据流：
    hermes 每日产出 candidates → 全部以 unseen 入池
    用户操作：
      👍 感兴趣 → 深分析 + 沉淀 → archived
      📥 归档   → archived
      ⏰ 稍后   → viewed（留在池中待回来看）
      👎 跳过   → viewed（记录不感兴趣，但保留可追溯）

持久化：
    memory/paper-pool.json — {arxiv_id: {status, title, added_at, ...}}

用法示例：
    >>> from paper_pool import add_candidates, get_pool, update_status
    >>> add_candidates()                    # 同步今日候选到池中
    >>> pool = get_pool(status="unseen")    # 获取未看候选
    >>> update_status("2403.15337", "archived")  # 标记已归档

规范：仅标准库，PROJECT_ROOT 推导，JSON ensure_ascii=False。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
POOL_PATH = PROJECT_ROOT / "memory" / "paper-pool.json"

# 三状态
STATUS_UNSEEN = "unseen"
STATUS_VIEWED = "viewed"
STATUS_ARCHIVED = "archived"
VALID_STATUSES = {STATUS_UNSEEN, STATUS_VIEWED, STATUS_ARCHIVED}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> Dict[str, Any]:
    """加载候选池（{arxiv_id: {status, title, ...}}）。"""
    if not POOL_PATH.exists():
        return {}
    try:
        return json.loads(POOL_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(pool: Dict[str, Any]) -> None:
    POOL_PATH.parent.mkdir(parents=True, exist_ok=True)
    POOL_PATH.write_text(json.dumps(pool, ensure_ascii=False, indent=2), encoding="utf-8")


def add_candidates(candidates: Optional[List[Dict]] = None) -> int:
    """将候选论文同步入池（未在池中的以 unseen 入池，已存在的不动）。

    Args:
        candidates: 候选列表（None 则从 hermes daily_candidates.json 读取）

    Returns:
        新增入池的数量
    """
    if candidates is None:
        # 从 hermes 产出读取
        import sys
        if str(PROJECT_ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from kb_importer import _load_candidates
        data = _load_candidates()
        candidates = data.get("papers", [])

    pool = _load()
    added = 0
    for p in candidates:
        aid = p.get("arxiv_id", "")
        if not aid or aid in pool:
            continue
        pool[aid] = {
            "status": STATUS_UNSEEN,
            "title": p.get("title", ""),
            "authors": p.get("authors", "") if isinstance(p.get("authors"), str) else ", ".join(p.get("authors", [])),
            "direction": p.get("direction", ""),
            "score": p.get("score_deepxiv", 0),
            "tldr": (p.get("tldr") or "")[:150],
            "added_at": _now(),
        }
        added += 1

    if added:
        _save(pool)
    return added


def get_pool(status: str = "") -> Dict[str, Any]:
    """获取候选池（可按状态过滤）。

    Args:
        status: 过滤状态（空=全部）

    Returns:
        {count, by_status: {unseen: N, viewed: N, archived: N}, papers: [...]}
    """
    pool = _load()
    if status and status in VALID_STATUSES:
        papers = {k: v for k, v in pool.items() if v.get("status") == status}
    else:
        papers = pool

    by_status = {s: 0 for s in VALID_STATUSES}
    for v in pool.values():
        s = v.get("status", STATUS_UNSEEN)
        if s in by_status:
            by_status[s] += 1

    # 按分数排序
    sorted_papers = sorted(papers.items(), key=lambda x: x[1].get("score", 0), reverse=True)
    return {
        "total": len(pool),
        "by_status": by_status,
        "papers": [{"arxiv_id": k, **v} for k, v in sorted_papers],
    }


def update_status(arxiv_id: str, status: str, extra: Optional[Dict] = None) -> bool:
    """更新候选状态。

    Args:
        arxiv_id: 论文 ID
        status: unseen/viewed/archived
        extra: 额外字段（如 discussion_summary）

    Returns:
        成功返回 True
    """
    if status not in VALID_STATUSES:
        return False
    pool = _load()
    if arxiv_id not in pool:
        return False
    pool[arxiv_id]["status"] = status
    pool[arxiv_id]["updated_at"] = _now()
    if extra:
        pool[arxiv_id].update(extra)
    _save(pool)
    return True


def remove(arxiv_id: str) -> bool:
    """从池中移除（彻底删除记录）。"""
    pool = _load()
    if arxiv_id in pool:
        del pool[arxiv_id]
        _save(pool)
        return True
    return False


def _self_check() -> None:
    """自检。"""
    print("=" * 50)
    print("◐ paper_pool 自检")
    print("=" * 50)
    print(f"\n[1/3] 候选池文件: {POOL_PATH} ({'存在' if POOL_PATH.exists() else '不存在'})")
    pool = _load()
    print(f"  当前池中: {len(pool)} 篇")

    print("\n[2/3] 同步今日候选...")
    added = add_candidates()
    print(f"  新增 {added} 篇入池")
    pool = _load()
    by_status = {s: sum(1 for v in pool.values() if v.get("status") == s) for s in VALID_STATUSES}
    print(f"  状态分布: 未看 {by_status[STATUS_UNSEEN]} / 已看 {by_status[STATUS_VIEWED]} / 已归档 {by_status[STATUS_ARCHIVED]}")

    print("\n[3/3] API 函数验证...")
    assert callable(get_pool) and callable(update_status)
    print("  ✓ get_pool / update_status 就绪")
    print("\n✓ paper_pool 自检通过")


if __name__ == "__main__":
    _self_check()
