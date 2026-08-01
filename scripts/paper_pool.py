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

from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc, load_json, save_json

from paths import PROJECT_ROOT
POOL_PATH = PROJECT_ROOT / "memory" / "paper-pool.json"

# 三状态
STATUS_UNSEEN = "unseen"
STATUS_VIEWED = "viewed"
STATUS_ARCHIVED = "archived"
VALID_STATUSES = {STATUS_UNSEEN, STATUS_VIEWED, STATUS_ARCHIVED}


def _load() -> Dict[str, Any]:
    """加载候选池（{arxiv_id: {status, title, ...}}）。"""
    return load_json(POOL_PATH, {})


def _save(pool: Dict[str, Any]) -> None:
    """保存候选池（原子写入，避免半写损坏）。"""
    save_json(POOL_PATH, pool)


def add_candidates(candidates: Optional[List[Dict]] = None) -> int:
    """将候选论文同步入池（未在池中的以 unseen 入池，已存在的不动）。

    Args:
        candidates: 候选列表（None 则从 hermes daily_candidates.json 读取）

    Returns:
        新增入池的数量
    """
    if candidates is None:
        # 委托 LiteratureService 获取每日简报候选论文
        from literature_service import LiteratureService
        svc = LiteratureService()
        papers = svc.search(keywords=[""], source="briefing")
        candidates = papers

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
            "added_at": now_utc(),
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
    def _safe_score(v: Any) -> float:
        try:
            return float(v) if v is not None else 0.0
        except (ValueError, TypeError):
            return 0.0
    sorted_papers = sorted(papers.items(), key=lambda x: _safe_score(x[1].get("score", 0)), reverse=True)
    return {
        "total": len(pool),
        "by_status": by_status,
        "papers": [{"arxiv_id": k, **v} for k, v in sorted_papers],
    }


def get_paper_status(arxiv_id: str) -> Optional[str]:
    """查询单篇论文状态（不存在返回 None）。

    供 briefing_sync 正向同步使用：判断当前状态是否可升级。

    Args:
        arxiv_id: 论文 ID

    Returns:
        unseen/viewed/archived，或 None（不在池中）
    """
    pool = _load()
    if arxiv_id not in pool:
        return None
    return pool[arxiv_id].get("status", STATUS_UNSEEN)


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
    pool[arxiv_id]["updated_at"] = now_utc()
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


def has_local_pdf(arxiv_id: str) -> bool:
    """检查论文是否已有本地 PDF 原文。

    供前端展示"查看原文"按钮、learning_engine 决定是否需要下载使用。

    Args:
        arxiv_id: 论文 ID

    Returns:
        True 表示 PDF 已存储在本地
    """
    try:
        import sys
        if str(PROJECT_ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from pdf_manager import get_library
        return get_library().has_pdf(arxiv_id)
    except Exception:
        return False


def get_pool_with_pdf_status(status: str = "") -> Dict[str, Any]:
    """返回论文池数据，每篇附加 has_pdf 字段。

    Args:
        status: 按状态过滤（空字符串=全部）

    Returns:
        与 get_pool 相同结构，但每篇论文多一个 has_pdf 布尔字段
    """
    pool = _load()
    result = {}
    for aid, entry in pool.items():
        if status and entry.get("status") != status:
            continue
        entry = dict(entry)
        entry["has_pdf"] = has_local_pdf(aid)
        result[aid] = entry
    return result


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
    assert callable(get_paper_status)
    assert callable(has_local_pdf)
    assert callable(get_pool_with_pdf_status)
    # get_paper_status：不存在的 ID 返回 None
    _test_aid = "test_nonexist_0000"
    assert get_paper_status(_test_aid) is None, "不存在论文应返回 None"
    # has_local_pdf：不存在的 ID 返回 False
    assert has_local_pdf(_test_aid) is False, "不存在论文应返回 False"
    print("  ✓ get_pool / update_status / get_paper_status / has_local_pdf 就绪")
    print("\n✓ paper_pool 自检通过")


if __name__ == "__main__":
    _self_check()
