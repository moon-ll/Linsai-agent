#!/usr/bin/env python3
"""clusters.py — 输入端知识簇注册表（v6.9.12）。

设计目标（对应用户四点需求中的"聚类 + 防冗余"）：
    1. 持久化簇注册表：聚类结果跨周存活，不再每周无状态重猜。
    2. 增量归簇：新摘要优先匹配已有 open 簇（"沿已有类融入"），
       匹配失败才挂 orphans（单篇不成簇，凑齐 ≥2 篇才开新簇）。
    3. 簇生命周期：open（积累中）→ linked（已路由到课题）→ closed
       （陈旧关闭）。linked/closed 簇不再吸收新成员，但保留在注册
       表中供查重（防止同样的主题未来重复开簇）。
    4. 全部归簇逻辑零 LLM（确定性关键词 Jaccard），LLM 只用于簇内
       提炼（cluster_distill job），成本可控、可回归测试。

用法：
    from weekend_pipeline.clusters import (
        load_clusters, assign_summaries, form_new_clusters,
    )
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


CLUSTERS_PATH = PROJECT_ROOT / "memory" / "weekend-input" / "clusters.json"

# 簇状态
CLUSTER_OPEN = "open"        # 积累中，可吸收新成员
CLUSTER_LINKED = "linked"    # 已路由到课题（merge/new/expansion 均算）
CLUSTER_CLOSED = "closed"    # 陈旧关闭（长期无新成员且未链接课题）

# 归簇参数（关键词 Jaccard 口径，实测物理领域摘要关键词重合度标定）
ASSIGN_SIM_THRESHOLD = 0.22       # 新摘要 vs 已有簇：超过即归入
FORM_CLUSTER_SIM_THRESHOLD = 0.30  # orphans 互相之间：超过可聚团
MIN_CLUSTER_MEMBERS = 2           # 成新簇最少成员数（单篇不成簇，防冗余）
ORPHAN_MAX_AGE_DAYS = 42          # orphan 超龄丢弃（一直凑不成簇的散料）
CLUSTER_STALE_WEEKS = 4           # open 簇 N 周无新成员且未链接 → closed


# ---------------------------------------------------------------------------
# 注册表 I/O
# ---------------------------------------------------------------------------


def load_clusters(path: Optional[Path] = None) -> Dict[str, Any]:
    """加载簇注册表（不存在返回空骨架）。"""
    path = path or CLUSTERS_PATH
    data = load_json(path, default={})
    if "clusters" not in data:
        data["clusters"] = []
    if "orphans" not in data:
        data["orphans"] = []
    return data


def save_clusters(data: Dict[str, Any], path: Optional[Path] = None) -> None:
    """原子保存簇注册表。"""
    path = path or CLUSTERS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now_utc()
    with file_lock("weekend-clusters"):
        save_json(path, data)


# ---------------------------------------------------------------------------
# 相似度（零 LLM，确定性）
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> set:
    """中英文混合分词（词集合）。"""
    if not text:
        return set()
    words = set(re.findall(r"[a-zA-Z]{3,}", text.lower()))
    words.update(re.findall(r"[\u4e00-\u9fff]{2,8}", text))
    return words


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def summary_similarity(item: Dict[str, Any], cluster: Dict[str, Any]) -> float:
    """摘要条目 vs 簇的相似度：关键词 0.7 + 标题 0.3。

    关键词权重高：LLM 摘要产出的 keywords 是主题的最强信号；
    标题 token 作补充（关键词漏提时兜底）。
    """
    kw_a = set(item.get("keywords", []) or [])
    kw_b = set(cluster.get("keywords", []) or [])
    ti_a = _tokenize(item.get("title", ""))
    ti_b = _tokenize(cluster.get("title", ""))
    return 0.7 * _jaccard(kw_a, kw_b) + 0.3 * _jaccard(ti_a, ti_b)


def item_similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """两条摘要之间的相似度（orphan 聚团用）。"""
    kw_a = set(a.get("keywords", []) or [])
    kw_b = set(b.get("keywords", []) or [])
    ti_a = _tokenize(a.get("title", ""))
    ti_b = _tokenize(b.get("title", ""))
    return 0.7 * _jaccard(kw_a, kw_b) + 0.3 * _jaccard(ti_a, ti_b)


# ---------------------------------------------------------------------------
# 增量归簇
# ---------------------------------------------------------------------------


def _new_cluster_id() -> str:
    """生成簇 id：cl_{日期}_{短随机}。"""
    import hashlib
    seed = f"{now_utc()}-{id(object())}"
    return f"cl_{now_utc()[:10].replace('-', '')}_{hashlib.sha256(seed.encode()).hexdigest()[:6]}"


def _merge_keywords(cluster: Dict[str, Any], item: Dict[str, Any], cap: int = 12) -> None:
    """簇关键词合并：保留高频/新词，上限 cap。"""
    existing = list(cluster.get("keywords", []) or [])
    for kw in item.get("keywords", []) or []:
        if kw and kw not in existing:
            existing.append(kw)
    cluster["keywords"] = existing[:cap]


def assign_summaries(
    summaries: List[Dict[str, Any]],
    registry: Dict[str, Any],
    threshold: float = ASSIGN_SIM_THRESHOLD,
) -> Dict[str, Any]:
    """把本周摘要增量归入已有 open 簇；未匹配的挂 orphans。

    防冗余核心：只与 open 簇匹配（linked/closed 簇已路由，重开无意义，
    但保留在注册表供 topic_match 查重）。单条摘要可归多个簇时选最高分。

    Returns:
        {"assigned": [{cluster_id, source_id, score}...],
         "orphaned": [source_id...]}
    """
    assigned: List[Dict[str, Any]] = []
    orphaned: List[str] = []
    open_clusters = [c for c in registry.get("clusters", []) if c.get("status") == CLUSTER_OPEN]

    for item in summaries:
        sid = item.get("source_id", "")
        if not sid:
            continue
        best_cluster, best_score = None, 0.0
        for c in open_clusters:
            score = summary_similarity(item, c)
            if score > best_score:
                best_score, best_cluster = score, c

        if best_cluster is not None and best_score >= threshold:
            # 沿已有类融入：追加成员、合并关键词、刷新时间戳
            members = best_cluster.setdefault("member_source_ids", [])
            if sid not in members:
                members.append(sid)
                best_cluster.setdefault("member_summaries", []).append({
                    "source_id": sid,
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "keywords": item.get("keywords", []) or [],
                })
                _merge_keywords(best_cluster, item)
                best_cluster["updated_at"] = now_utc()
            assigned.append({"cluster_id": best_cluster["cluster_id"], "source_id": sid, "score": round(best_score, 3)})
        else:
            # 挂 orphans 等凑簇（单篇不成簇）
            orphans = registry.setdefault("orphans", [])
            if not any(o.get("source_id") == sid for o in orphans):
                orphans.append({
                    "source_id": sid,
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "keywords": item.get("keywords", []) or [],
                    "first_seen": now_utc(),
                })
            orphaned.append(sid)

    return {"assigned": assigned, "orphaned": orphaned}


def form_new_clusters(
    registry: Dict[str, Any],
    threshold: float = FORM_CLUSTER_SIM_THRESHOLD,
    min_members: int = MIN_CLUSTER_MEMBERS,
) -> List[Dict[str, Any]]:
    """从 orphans 中聚团成新簇（贪心种子法）。

    规则：取首个 orphan 为种子，吸走所有与种子相似 ≥threshold 的
    orphan 成团；团规模 ≥min_members 才开新簇，其余留 orphans。
    新簇需与全部已有簇（含 linked/closed）查重——与已有簇过近的
    团不开新簇，成员退回 orphans（防止换皮重开）。
    """
    orphans: List[Dict[str, Any]] = registry.get("orphans", [])
    all_clusters = registry.get("clusters", [])
    formed: List[Dict[str, Any]] = []
    remaining = list(orphans)
    deferred: List[Dict[str, Any]] = []  # 已当过种子或查重退回的，本轮不再当种子

    while remaining:
        seed = remaining.pop(0)
        group = [seed]
        rest: List[Dict[str, Any]] = []
        for o in remaining:
            if item_similarity(seed, o) >= threshold:
                group.append(o)
            else:
                rest.append(o)
        remaining = rest  # 未被吸走的可继续当后续种子

        if len(group) < min_members:
            # 单篇不成簇：种子本轮已试过 → deferred；其余成员放回
            # remaining 等待与别的种子聚团（否则成员会静默丢失）
            deferred.append(seed)
            remaining.extend(group[1:])
            continue

        # 与全部已有簇查重（防换皮重开）
        candidate_title = seed.get("title", "")
        candidate_kw = set()
        for g in group:
            candidate_kw.update(g.get("keywords", []) or [])
        too_close = False
        for c in all_clusters + formed:
            kw_sim = _jaccard(candidate_kw, set(c.get("keywords", []) or []))
            ti_sim = _jaccard(_tokenize(candidate_title), _tokenize(c.get("title", "")))
            if 0.7 * kw_sim + 0.3 * ti_sim >= threshold:
                too_close = True
                break
        if too_close:
            # 团员全部退回 deferred（防止同轮反复聚同一个不合格团）
            deferred.extend(group)
            continue

        cluster = {
            "cluster_id": _new_cluster_id(),
            "title": candidate_title,
            "keywords": sorted(candidate_kw)[:12],
            "summary": "",  # 待 cluster_distill 提炼
            "member_source_ids": [g.get("source_id", "") for g in group],
            "member_summaries": [
                {
                    "source_id": g.get("source_id", ""),
                    "title": g.get("title", ""),
                    "summary": g.get("summary", ""),
                    "keywords": g.get("keywords", []) or [],
                }
                for g in group
            ],
            "status": CLUSTER_OPEN,
            "linked_proposal_id": None,
            "created_at": now_utc(),
            "updated_at": now_utc(),
        }
        all_clusters.append(cluster)
        formed.append(cluster)

    # orphans 收敛为：剩余可聚项 + 本轮已试过种子的散料
    registry["orphans"] = remaining + deferred
    return formed


# ---------------------------------------------------------------------------
# 生命周期维护
# ---------------------------------------------------------------------------


def prune_orphans(registry: Dict[str, Any], max_age_days: int = ORPHAN_MAX_AGE_DAYS) -> int:
    """丢弃超龄 orphan（一直凑不成簇的散料，避免无限堆积）。"""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    before = len(registry.get("orphans", []))
    registry["orphans"] = [
        o for o in registry.get("orphans", [])
        if o.get("first_seen", "") >= cutoff
    ]
    return before - len(registry["orphans"])


def close_stale_clusters(registry: Dict[str, Any], stale_weeks: int = CLUSTER_STALE_WEEKS) -> int:
    """open 簇 N 周无新成员且未链接课题 → closed（不再吸收，防僵尸簇）。"""
    cutoff = (datetime.now(timezone.utc) - timedelta(weeks=stale_weeks)).strftime("%Y-%m-%dT%H:%M:%SZ")
    closed = 0
    for c in registry.get("clusters", []):
        if c.get("status") == CLUSTER_OPEN and c.get("updated_at", "") < cutoff:
            c["status"] = CLUSTER_CLOSED
            closed += 1
    return closed


def mark_linked(registry: Dict[str, Any], cluster_id: str, proposal_id: str) -> bool:
    """簇路由到课题后标记 linked。"""
    for c in registry.get("clusters", []):
        if c.get("cluster_id") == cluster_id:
            c["status"] = CLUSTER_LINKED
            c["linked_proposal_id"] = proposal_id
            c["updated_at"] = now_utc()
            return True
    return False


def open_clusters_with_fresh_members(registry: Dict[str, Any], week_start_iso: str) -> List[Dict[str, Any]]:
    """列出本周有新成员的 open 簇（cluster_distill 的处理对象）。"""
    return [
        c for c in registry.get("clusters", [])
        if c.get("status") == CLUSTER_OPEN and c.get("updated_at", "") >= week_start_iso
    ]
