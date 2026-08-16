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
CLUSTER_DEFERRED = "deferred"  # v6.9.18：路由暂缓（不满足 new 门槛，继续积累）

# 归簇参数（实测标定，见 _kw_similarity 注释）
ASSIGN_SIM_THRESHOLD = 0.22       # 新摘要 vs 已有簇：超过即归入
FORM_CLUSTER_SIM_THRESHOLD = 0.30  # orphans 互相之间：超过可聚团
MIN_CLUSTER_MEMBERS = 3           # 成新簇最少成员数（v6.9.18: 2→3，两篇
                                  # 凑数簇占 08-16 实测 143 簇的绝大多数）
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
    """中英文混合分词：中文 2-gram 滑窗 + 英文单词（v6.9.18）。

    旧实现中文按 {2,8} 贪婪连续切分——中文无空格，整句被切成超长
    token，两个不同句子的 token 集几乎恒不相交，标题相似度对中文
    恒近 0（08-16 实测乱聚与好聚的标题分量无区分度）。2-gram 与
    kb_text 索引同口径（内联实现，避免跨包导入私有函数），长短语
    匹配由相邻 2-gram 组合覆盖。
    """
    if not text:
        return set()
    tokens = set()
    for m in re.finditer(r"[a-zA-Z]{3,}", text.lower()):
        tokens.add(m.group())
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}", text):
        w = m.group()
        for i in range(len(w) - 1):
            tokens.add(w[i : i + 2])
    return tokens


def norm_keyword(kw: str) -> str:
    """关键词归一化（v6.9.14）。

    08-15 实测：GLM 摘要关键词存在同义不同形——"高次谐波产生" vs
    "高次谐波产生 (HHG)"，作为集合成员永不相等。统一去尾部括注、
    去首尾空白、转小写。
    """
    if not kw:
        return ""
    kw = re.sub(r"\s*[（(][^（）()]*[)）]\s*$", "", str(kw)).strip().lower()
    return kw


def kw_set(keywords) -> set:
    """关键词列表 → 归一化集合。"""
    return {norm_keyword(k) for k in (keywords or []) if norm_keyword(k)}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _overlap(a: set, b: set) -> float:
    """overlap 系数：|A∩B| / min(|A|,|B|)。

    08-15 实测标定：摘要关键词仅 5-15 个，同子领域两篇论文通常共享
    2-4 个核心词。Jaccard 分母是并集（2 共享/9 并集 ≈ 0.22），对短
    集合系统性偏低——435 对真实摘要最高仅 0.161，阈值 0.22/0.30
    永远达不到，簇零形成、输入链空转。overlap 以较小集合为分母
    （2/5 = 0.40），语义是"这篇的核心词是否落在簇的核心词内"，与
    归簇意图一致。标题 token 分量保持 Jaccard（token 集较长，无此问题）。
    """
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def summary_similarity(item: Dict[str, Any], cluster: Dict[str, Any]) -> float:
    """摘要条目 vs 簇的相似度：关键词 overlap 0.7 + 标题 Jaccard 0.3。

    关键词权重高：LLM 摘要产出的 keywords 是主题的最强信号；
    标题 token 作补充（关键词漏提时兜底）。
    """
    kw_a = kw_set(item.get("keywords"))
    kw_b = kw_set(cluster.get("keywords"))
    ti_a = _tokenize(item.get("title", ""))
    ti_b = _tokenize(cluster.get("title", ""))
    return 0.7 * _overlap(kw_a, kw_b) + 0.3 * _jaccard(ti_a, ti_b)


def item_similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """两条摘要之间的相似度（orphan 聚团用）。"""
    kw_a = kw_set(a.get("keywords"))
    kw_b = kw_set(b.get("keywords"))
    ti_a = _tokenize(a.get("title", ""))
    ti_b = _tokenize(b.get("title", ""))
    return 0.7 * _overlap(kw_a, kw_b) + 0.3 * _jaccard(ti_a, ti_b)


def cluster_similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """两簇之间的相似度（v6.9.18 compose 同课题归并注入用）。

    口径与归簇一致：关键词 overlap 0.7 + 标题 Jaccard 0.3。同目标
    课题的多个簇若彼此相似，只注入成员最多簇的知识卡，其余只挂
    信息源——根治 08-16 实测 BSV 课题被 6 个变体簇重复注入。
    """
    return item_similarity(a, b)


# ---------------------------------------------------------------------------
# 增量归簇
# ---------------------------------------------------------------------------


def _new_cluster_id(existing_ids: Optional[set] = None) -> str:
    """生成簇 id：cl_{日期}_{uuid6}，注册表内查重（v6.9.18）。

    旧实现用 id(object()) 做 hash seed——CPython 中临时对象立即回收，
    id 高频复用，同批创建大量碰撞（08-16 实测 143 簇中同一 ID 最多
    重复 10 次，mark_linked/cluster_index 按 ID 索引全部错绑）。
    """
    import uuid
    existing = existing_ids or set()
    while True:
        cid = f"cl_{now_utc()[:10].replace('-', '')}_{uuid.uuid4().hex[:6]}"
        if cid not in existing:
            return cid


def _top_group_keywords(group: List[Dict[str, Any]], top: int = 3) -> List[str]:
    """团内高频关键词（v6.9.18 簇标题来源）。

    按关键词在团内出现的成员数排序（被 ≥2 个成员共享的词更能代表
    共同主题），同频按首次出现顺序。取代旧实现直接拿种子论文标题
    当簇标题（单篇标题不是主题名）。
    """
    counts: Dict[str, int] = {}
    order: Dict[str, int] = {}
    for idx, g in enumerate(group):
        for kw in (g.get("keywords") or []):
            nk = norm_keyword(kw)
            if not nk:
                continue
            counts[nk] = counts.get(nk, 0) + 1
            order.setdefault(nk, idx)
    ranked = sorted(counts, key=lambda k: (-counts[k], order[k]))
    shared = [k for k in ranked if counts[k] >= 2]
    picked = (shared or ranked)[:top]
    return picked


def _merge_keywords(cluster: Dict[str, Any], item: Dict[str, Any], cap: int = 12) -> None:
    """簇关键词合并：归一化去重，保留新词，上限 cap。"""
    existing: list = []
    seen = set()
    for kw in list(cluster.get("keywords", []) or []):
        nk = norm_keyword(kw)
        if nk and nk not in seen:
            existing.append(nk)
            seen.add(nk)
    for kw in item.get("keywords", []) or []:
        nk = norm_keyword(kw)
        if nk and nk not in seen:
            existing.append(nk)
            seen.add(nk)
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
            # v6.9.18: member_summaries 补存 path——compose 的信息源
            # 挂载以簇内成员自述为准（跨周可用），不再依赖当天 summaries
            members = best_cluster.setdefault("member_source_ids", [])
            if sid not in members:
                members.append(sid)
                best_cluster.setdefault("member_summaries", []).append({
                    "source_id": sid,
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "keywords": item.get("keywords", []) or [],
                    "path": item.get("path", ""),
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
                    "path": item.get("path", ""),
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
    v6.9.18: 簇标题用团内高频关键词拼接（旧实现拿种子论文标题当
    主题名，既不是主题也无法跨语言）；簇 ID uuid 防碰撞。
    """
    orphans: List[Dict[str, Any]] = registry.get("orphans", [])
    all_clusters = registry.get("clusters", [])
    formed: List[Dict[str, Any]] = []
    remaining = list(orphans)
    deferred: List[Dict[str, Any]] = []  # 已当过种子或查重退回的，本轮不再当种子
    existing_ids = {c.get("cluster_id") for c in all_clusters}

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

        # 与全部已有簇查重（防换皮重开；关键词 overlap 口径与归簇一致）
        candidate_title = "、".join(_top_group_keywords(group))
        candidate_kw = kw_set([k for g in group for k in (g.get("keywords") or [])])
        too_close = False
        for c in all_clusters + formed:
            kw_sim = _overlap(candidate_kw, kw_set(c.get("keywords")))
            ti_sim = _jaccard(_tokenize(candidate_title), _tokenize(c.get("title", "")))
            if 0.7 * kw_sim + 0.3 * ti_sim >= threshold:
                too_close = True
                break
        if too_close:
            # 团员全部退回 deferred（防止同轮反复聚同一个不合格团）
            deferred.extend(group)
            continue

        cluster = {
            "cluster_id": _new_cluster_id(existing_ids),
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
                    "path": g.get("path", ""),
                }
                for g in group
            ],
            "status": CLUSTER_OPEN,
            "linked_proposal_id": None,
            "created_at": now_utc(),
            "updated_at": now_utc(),
        }
        existing_ids.add(cluster["cluster_id"])
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
