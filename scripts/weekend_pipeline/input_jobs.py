#!/usr/bin/env python3
"""输入阶段 job 执行器。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import load_json, now_utc, save_json, safe_filename
from llm_gateway import is_llm_available, llm_complete
from paths import PROJECT_ROOT

from .constants import RELIABILITY_DERIVED, RELIABILITY_RELIABLE, WEEKEND_INPUT_DIR
from .sources import (
    collect_all_sources,
    list_kb_paper_pages,
    new_paper_sources,
    search_kb_for_query,
)
from .state import mark_source_processed

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


def _ensure_input_dir() -> None:
    WEEKEND_INPUT_DIR.mkdir(parents=True, exist_ok=True)


def _read_text(path: Path, max_chars: int = 8000) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except Exception:
        return ""


def _llm_json(system: str, user: str, timeout: int = 120, prefer: str = "weekend_input") -> Any:
    """调用 LLM 并解析 JSON。

    v6.9.14: 默认 prefer="weekend_input"——本模块三个 LLM 调用点
    （summarize 摘要 / cluster_distill 知识卡 / topic_match 仲裁）
    统一走 GLM 最新（glm-5.3）为主模型，失败回落全局链。调用方
    可显式传 prefer=None 恢复全局策略。
    """
    if not is_llm_available():
        return None
    ok, text, meta = llm_complete(system, user, timeout=timeout, prefer=prefer)
    if not ok:
        if _log:
            _log.warning(f"LLM 调用失败: {meta.get('error', 'unknown')}")
        return None
    try:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        json_str = m.group(1) if m else text
        return json.loads(json_str)
    except Exception as e:
        if _log:
            _log.warning(f"解析 LLM 输出失败: {e}")
        return None


def _tokenize(text: str) -> set:
    if not text:
        return set()
    words = set(re.findall(r"[a-zA-Z]{3,}", text.lower()))
    words.update(re.findall(r"[\u4e00-\u9fff]{2,8}", text))
    return words


def _jaccard_similarity(a: str, b: str) -> float:
    set_a = _tokenize(a)
    set_b = _tokenize(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


# ---------------------------------------------------------------------------
# Job handlers
# ---------------------------------------------------------------------------


def run_input_collect(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """收集来源并记录 processed_sources。

    v6.8.13: 前置调用 sync_engine.sync_hermes_outputs() 确保 hermes 产出已汇聚。
    """
    if not dry_run:
        try:
            import sync_engine
            sync_engine.sync_hermes_outputs()
            if _log:
                _log.info("输入端：hermes outputs 已同步")
        except Exception as e:
            if _log:
                _log.warning(f"输入端：sync_hermes_outputs 失败（继续）: {e}")

    sources = collect_all_sources(state=state, days=7, paper_limit=20, capture_limit=10,
                                  persist_scope=not dry_run)
    _ensure_input_dir()
    if not dry_run:
        save_json(WEEKEND_INPUT_DIR / f"sources-{now_utc()[:10]}.json", sources)
    # v6.9.12: distilled_excluded 是 int 计数，跳过 len()；kb 是 dict，
    # len 取子类型数
    source_counts = {
        k: (len(v) if isinstance(v, (list, dict)) else v)
        for k, v in sources.items()
        if k != "collected_at"
    }
    return {"success": True, "source_counts": source_counts}


def _coerce_summary_data(data: Any, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """v6.9.13: 把 LLM 摘要输出收敛为带溯源字段的 dict；无法收敛返回 None。

    08-15 实测：system prompt 要求"JSON 数组"而 user 模板要求对象，
    30/30 篇全部返回 [{"title","summary","keywords"}] 数组形状；旧代码
    只回填 dict 形状，数组条目直接落盘且无 source_id/path/tier，
    cluster_assign 取条目 .get() 时崩溃（'list' object has no
    attribute 'get'），且来源已 mark processed 失去重跑资格。
    """
    if isinstance(data, list):
        data = next((x for x in data if isinstance(x, dict)), None)
    if not isinstance(data, dict):
        return None
    data.setdefault("title", paper.get("title", ""))
    data["source_id"] = paper.get("source_id", "")
    data["path"] = paper.get("path", "")
    data["tier"] = paper.get("tier", 2)
    # v6.9.14: 关键词摄取归一化——去尾部括注（"高次谐波产生 (HHG)" →
    # "高次谐波产生"）、去空、去重、截断到 15。同义不同形会让聚类
    # 集合成员永不相等（08-15 实测 4 个/181 个关键词带括注后缀）。
    from .clusters import norm_keyword
    kws: list = []
    seen: set = set()
    for kw in (data.get("keywords") or [])[:20]:
        nk = norm_keyword(kw)
        if nk and nk not in seen:
            kws.append(nk)
            seen.add(nk)
        if len(kws) >= 15:
            break
    data["keywords"] = kws
    return data


def run_input_summarize(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """对新增论文/简报做轻量摘要（聚类主源：tier ≤2）。

    v6.9.7: 无新增论文时也写出空产物文件——job 模板已声明
    artifact=summaries-{date}.json，产物校验依赖"done 必有产物"
    不变式；此前无新增论文提前 return 不落文件，会导致下一轮
    sync 误判产物缺失而反复重置（空转循环）。
    v6.9.12: 摘要条目携带 source_id/path/tier，供下游增量归簇
    与信息源挂载回溯原始文献。
    """
    sources = collect_all_sources(state=state, days=7, paper_limit=20, capture_limit=10,
                                  persist_scope=not dry_run)
    papers = new_paper_sources(sources, state)
    if not papers:
        if not dry_run:
            _ensure_input_dir()
            save_json(WEEKEND_INPUT_DIR / f"summaries-{now_utc()[:10]}.json", {"summaries": []})
        return {"success": True, "summarized": 0, "message": "无新增论文/简报"}

    if dry_run:
        return {"success": True, "summarized": len(papers), "dry_run": True, "message": "dry-run 跳过 LLM 摘要"}

    if not is_llm_available():
        return {"success": False, "error": "LLM 不可用"}

    summaries = []
    system = "你是林赛，擅长对学术文献做一句话核心摘要。输出合法 JSON 对象。"
    # v6.9.14: 关键词要求 5 个 → 10-15 个且强制含 2-4 个领域级标签。
    # 08-15 实测：5 个论文特定关键词的集合太稀疏（30 篇中仅 2 对共享
    # ≥2 词，435 对最高 Jaccard 0.161），聚类的共享词表必须由领域级
    # 标签（如 固态高次谐波/强场物理/二维材料/阿秒动力学）提供。
    kw_spec = (
        "。其中 keywords 为 10-15 个关键词：2-4 个领域级标签"
        "（如：固态高次谐波、强场物理、非线性光学、二维材料、阿秒动力学、"
        "拓扑材料、量子光学 等，标注本文所属大方向），其余为本文具体贡献关键词"
    )
    # v6.9.11: 单次容量 10 → 30。每篇 LLM timeout 60s，最坏 30×60=1800s，
    # 在 weekend job stale 阈值（STALE_RUNNING_SECONDS=3600）内安全。
    # 旧值 10 配合每周一跑，消化能力 ~10 条/周 < 稳态新料增速，且补课
    # 积压（92 条）需 9 周才能清完。
    failed_llm = 0
    for p in papers[:30]:
        user = (
            f"请用 1-2 句话总结以下文献的核心贡献：\n\n"
            f"标题：{p.get('title', '')}\n内容：{p.get('text', '')[:1200]}\n\n"
            f"输出 JSON：{{\"title\": \"...\", \"summary\": \"...\", \"keywords\": [\"...\"]}}{kw_spec}。"
        )
        data = _llm_json(system, user, timeout=60)
        normalized = _coerce_summary_data(data, p) if data else None
        if normalized is not None:
            summaries.append(normalized)
            mark_source_processed(p["source_id"], p["text"], state)
        else:
            failed_llm += 1

    # v6.9.12 故障防线（对齐 v6.8.46 hermes 429 防线语义）：有新料但
    # 全部摘要失败（LLM 限额/故障）时返回 success=False 而非空转标
    # done——否则空 summaries 向下游传播，整链空跑，熔断只能事后报。
    # 未 mark 的来源保持"未处理"状态，repair 重试或下周自然续跑。
    if summaries or failed_llm == 0:
        _ensure_input_dir()
        if not dry_run:
            save_json(WEEKEND_INPUT_DIR / f"summaries-{now_utc()[:10]}.json", {"summaries": summaries})
        return {"success": True, "summarized": len(summaries)}
    return {
        "success": False,
        "error": f"LLM 故障：{failed_llm} 篇新料全部摘要失败（未标记已处理，等待重试）",
        "summarized": 0,
    }


# ---------------------------------------------------------------------------
# v6.9.12: 知识簇链路（cluster_assign → cluster_distill → topic_match）
# ---------------------------------------------------------------------------


def run_input_cluster_assign(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """增量归簇：本周摘要沿已有 open 簇融入，孤篇挂 orphans 等凑簇。

    取代旧 gap_analysis 的"每周无状态重猜 5 个方向"——簇注册表跨周
    持久化，新知识优先融入已有类（防冗余核心），单篇不成簇。
    全程零 LLM（关键词 Jaccard，确定性可回归）。
    """
    from .clusters import (
        assign_summaries,
        close_stale_clusters,
        form_new_clusters,
        load_clusters,
        prune_orphans,
        save_clusters,
    )

    summaries_path = WEEKEND_INPUT_DIR / f"summaries-{now_utc()[:10]}.json"
    summaries = load_json(summaries_path, default={}).get("summaries", [])

    if dry_run:
        return {
            "success": True,
            "assigned": 0,
            "new_clusters": 0,
            "dry_run": True,
            "message": f"dry-run 跳过归簇（{len(summaries)} 条待归）",
        }

    registry = load_clusters()
    result = assign_summaries(summaries, registry)
    formed = form_new_clusters(registry)
    pruned = prune_orphans(registry)
    closed = close_stale_clusters(registry)
    save_clusters(registry)

    _ensure_input_dir()
    save_json(WEEKEND_INPUT_DIR / f"clusters-week-{now_utc()[:10]}.json", {
        "assigned": result["assigned"],
        "orphaned": result["orphaned"],
        "new_clusters": [
            {"cluster_id": c["cluster_id"], "title": c["title"], "members": len(c["member_source_ids"])}
            for c in formed
        ],
    })

    return {
        "success": True,
        "assigned": len(result["assigned"]),
        "orphaned": len(result["orphaned"]),
        "new_clusters": len(formed),
        "orphan_pruned": pruned,
        "stale_closed": closed,
        "total_open_clusters": sum(
            1 for c in registry.get("clusters", []) if c.get("status") == "open"
        ),
    }


def run_input_cluster_distill(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """簇内提炼：对本周有新成员的 open 簇生成结构化知识卡（LLM）。

    知识卡 = 簇级摘要（150-300 字）+ 开放问题，是 topic_match 判断
    簇与课题关系的主要依据。LLM 不可用时簇沿用成员摘要拼接（降级
    不阻塞链路）。
    """
    from .clusters import load_clusters, open_clusters_with_fresh_members, save_clusters

    if dry_run:
        return {"success": True, "distilled": 0, "dry_run": True, "message": "dry-run 跳过簇提炼"}

    # 本周窗口：7 天前起有更新的簇
    from datetime import datetime, timedelta, timezone
    week_start = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    registry = load_clusters()
    targets = open_clusters_with_fresh_members(registry, week_start)
    if not targets:
        _ensure_input_dir()
        save_json(WEEKEND_INPUT_DIR / f"distilled-clusters-{now_utc()[:10]}.json", {"clusters": []})
        return {"success": True, "distilled": 0, "message": "本周无待提炼簇"}

    system = (
        "你是林赛，擅长综合多篇文献摘要提炼主题级知识卡。"
        "输出合法 JSON 对象：{\"title\": \"主题名\", \"summary\": \"150-300字综合摘要\", "
        "\"open_questions\": [\"开放问题...\"]}。"
    )
    distilled_out = []
    for c in targets[:8]:  # 周上限 8 簇（LLM 成本控制）
        members = c.get("member_summaries", [])[:12]
        user = (
            f"簇主题：{c.get('title', '')}\n"
            f"簇关键词：{', '.join(c.get('keywords', []))}\n\n"
            f"成员文献摘要：\n{json.dumps(members, ensure_ascii=False, indent=1)}\n\n"
            f"输出 JSON："
        )
        card = _llm_json(system, user, timeout=120)
        if isinstance(card, dict) and card.get("summary"):
            c["summary"] = card.get("summary", "")
            c["title"] = card.get("title", "") or c.get("title", "")
            c["open_questions"] = card.get("open_questions", []) or []
            # v6.9.18: 知识卡来源标记——topic_match 的 new 门槛仅认
            # LLM 提炼卡（降级拼接的弱卡不足以支撑开新课题）
            c["distilled_by"] = "llm"
        elif not c.get("summary"):
            # 降级：成员摘要拼接（无 LLM 时保持链路可继续）
            joined = "；".join(m.get("summary", "") for m in members[:6])
            c["summary"] = joined[:500]
            c.setdefault("distilled_by", "fallback")
        c["distilled_at"] = now_utc()
        distilled_out.append({
            "cluster_id": c["cluster_id"],
            "title": c["title"],
            "members": len(c.get("member_source_ids", [])),
            "distilled_by": c.get("distilled_by", ""),
        })

    save_clusters(registry)
    _ensure_input_dir()
    save_json(WEEKEND_INPUT_DIR / f"distilled-clusters-{now_utc()[:10]}.json", {"clusters": distilled_out})

    return {"success": True, "distilled": len(distilled_out)}


def _load_all_stage_proposals() -> List[Dict[str, Any]]:
    """读取全阶段课题清单（drafts/optimizing/pending_review/archived）。

    v6.9.12: 取代旧 direction_select 只读 KB 静态页（3000 字截断、
    status 靠中文行解析）的弱数据源。直接读 research_proposals/
    目录 + 各课题 00 号 brief，覆盖全部生命周期阶段且实时。
    """
    from proposal_lifecycle import ProposalLifecycle

    proposals: List[Dict[str, Any]] = []
    try:
        lc = ProposalLifecycle()
        for status in ("drafts", "optimizing", "pending_review", "archived"):
            for p in lc.list_by_status(status):
                prop_dir = lc._find_proposal_dir(p["proposal_id"])
                brief_text = ""
                if prop_dir:
                    for f in sorted(prop_dir.glob("00_*.md")):
                        brief_text = _read_text(f, 2000)
                        break
                proposals.append({
                    "proposal_id": p["proposal_id"],
                    "title": p.get("title", p["proposal_id"]),
                    "status": status,
                    "text": brief_text or p.get("title", ""),
                })
    except Exception as e:
        if _log:
            _log.warning(f"读取全阶段课题清单失败: {e}")
    return proposals


# v6.9.18: new 动作周配额——08-16 实测 141 簇无差别路由产出 72 new
# （54 个弱簇课题泛滥成灾，46 个 new-idea-NN 占位名）。宁缺毋滥。
NEW_WEEKLY_QUOTA = 2
# new 门槛成员数（与 clusters.MIN_CLUSTER_MEMBERS 对齐，弱簇只允许
# merge/expansion 信息注入，不满足则 defer 继续积累）
NEW_MIN_MEMBERS = 3

# v6.9.18 补：运维簇识别词（路由前置过滤）。08-16 复跑实测运维简报
# 簇（"每日简报/hermes-briefing"）知识卡含个别领域词可过方向关，
# LLM 仲裁无 reject 选项只能判 new——注册了运维课题。
_OPS_CLUSTER_MARKERS = (
    "每日简报", "hermes-briefing", "对话记忆", "知识管理", "运维",
    "自动化系统", "cron",
)


def _is_ops_cluster(cluster: Dict[str, Any]) -> bool:
    """识别运维内容簇：标题命中运维标记，或关键词命中 ≥2 个运维词。"""
    title = cluster.get("title", "") or ""
    if any(m in title for m in _OPS_CLUSTER_MARKERS[:6]):
        return True
    kws = [str(k).lower() for k in (cluster.get("keywords") or [])]
    hits = sum(1 for m in _OPS_CLUSTER_MARKERS if any(m in k for k in kws))
    return hits >= 2


def _new_gates(
    cluster: Dict[str, Any],
    proposals: List[Dict[str, Any]],
    scope_terms: List[str],
    quota_left: int,
) -> tuple:
    """new 动作四重门槛（v6.9.18）。

    Returns:
        (ok, reason)。ok=False 时簇路由为 defer（保持 open 继续积累）。
    """
    members = len(cluster.get("member_source_ids", []))
    if members < NEW_MIN_MEMBERS:
        return False, f"成员 {members} < {NEW_MIN_MEMBERS}，继续积累"
    if cluster.get("distilled_by") != "llm":
        return False, "知识卡非 LLM 提炼（缺失或降级拼接）"
    if quota_left <= 0:
        return False, f"本周 new 配额已用尽（上限 {NEW_WEEKLY_QUOTA}）"
    cluster_text = " ".join([
        cluster.get("title", ""), cluster.get("summary", ""),
        " ".join(cluster.get("keywords", [])),
    ])
    from .sources import scope_hit, core_theme_hit
    if scope_hit(cluster_text, scope_terms) is None:
        return False, "簇主题与方向词表无交集"
    # v6.9.22: 核心范式强制关——开新课题必须命中"强场操控"或
    # "HHG/超快光谱测量"范式词。仅命中材料/物态语境词（自旋/能谷/
    # 激子/交变磁等）的纯静态凝聚态簇不够格注册新课题，只能通过
    # merge/expansion 注入现有课题。08-16 实测：berry-mnps3 准静态
    # 滑移器件化课题即从此漏洞注册。
    if core_theme_hit(cluster_text) is None:
        return False, "仅语境词命中，未命中强场操控/超快测量核心范式"
    # 与现有课题的重叠检查（hold 线对齐 idea_generator 口径）
    try:
        from idea_generator import IDEA_HOLD_SIMILARITY
    except Exception:
        IDEA_HOLD_SIMILARITY = 0.50
    for p in proposals:
        if _jaccard_similarity(cluster_text, p["title"] + " " + p["text"]) >= IDEA_HOLD_SIMILARITY:
            return False, f"与现有课题 {p['proposal_id']} 高度重叠"
    return True, "成员/知识卡/方向/重叠/配额五关全过"


def run_input_topic_match(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """课题判断：open 簇 vs 全阶段课题，产出路由决策（merge/new/expansion/defer）。

    两级判断：Jaccard 预筛 top-3 候选 → LLM 仲裁（概念级重合判断，
    词袋测不出的同机制不同术语场景）。LLM 不可用时回退纯 Jaccard
    阈值（0.35，与旧口径一致）。
    v6.9.18: new 动作加四重门槛（成员数/LLM 知识卡/方向相关/不与
    现有课题重叠）+ 周配额；不达标的簇路由 defer（保持 open 继续
    积累，不丢失），取代旧版"低置信一律按新课题处理"的泛滥路径。
    """
    from .clusters import load_clusters
    from .sources import load_scope_terms

    if dry_run:
        return {"success": True, "routes": 0, "dry_run": True, "message": "dry-run 跳过课题匹配"}

    registry = load_clusters()
    open_c = [c for c in registry.get("clusters", []) if c.get("status") == "open"]
    if not open_c:
        _ensure_input_dir()
        save_json(WEEKEND_INPUT_DIR / f"routes-{now_utc()[:10]}.json", {"routes": []})
        return {"success": True, "routes": 0, "message": "无待路由簇"}

    proposals = _load_all_stage_proposals()
    scope_terms = load_scope_terms()
    quota_left = NEW_WEEKLY_QUOTA
    # 配额优先给成员最多的簇：先按成员数降序处理，先到先得
    open_c.sort(key=lambda c: len(c.get("member_source_ids", [])), reverse=True)

    routes = []
    for c in open_c:
        # v6.9.18 补：运维簇前置 defer（不进课题路由，保持 open 无害积累）
        if _is_ops_cluster(c):
            routes.append({
                "cluster_id": c["cluster_id"],
                "cluster_title": c.get("title", ""),
                "action": "defer",
                "target_id": None,
                "reason": "运维内容簇（简报/cron/系统元数据），不参与课题路由",
                "members": len(c.get("member_source_ids", [])),
                "candidates": [],
            })
            continue

        cluster_text = " ".join([c.get("title", ""), c.get("summary", ""), " ".join(c.get("keywords", []))])
        scored = sorted(
            (
                {"proposal": p, "score": _jaccard_similarity(cluster_text, p["title"] + " " + p["text"])}
                for p in proposals
            ),
            key=lambda x: x["score"],
            reverse=True,
        )[:8]  # v6.9.58: top-3→top-8——08-22 实测交变磁体簇的语义相关课题
        # （berry-mnps3，标题字面重叠低）被 top-3 截断排除在 LLM 仲裁视野外，
        # LLM 据"三个不相关课题"误判 new，与 idea_generator 路径重复立项
        # （general-new-idea-20260822 vs berry-mnps3 同方向）。仲裁候选多
        # 几行成本可忽略，截断漏检代价是整个重复课题。

        action, target_id, reason = None, None, ""
        best = scored[0] if scored else None
        if best and best["score"] >= 0.35:
            # 高置信重合：archived 课题 → expansion（文献挂载），
            # 活跃课题 → merge（信息注入）
            if best["proposal"]["status"] == "archived":
                action, target_id = "expansion", best["proposal"]["proposal_id"]
            else:
                action, target_id = "merge", best["proposal"]["proposal_id"]
            reason = f"Jaccard {best['score']:.2f}"
        else:
            # 中低置信：LLM 仲裁（top-3 候选一起判断，概念级重合）
            action, target_id, reason = _llm_arbitrate_cluster(c, scored)
            if action == "new":
                # LLM 判新也要过门槛（弱簇/离题/配额尽 → defer）
                ok, gate_reason = _new_gates(c, proposals, scope_terms, quota_left)
                if ok:
                    quota_left -= 1
                    reason = f"{reason}；{gate_reason}"
                else:
                    action, target_id = "defer", None
                    reason = f"new 门槛未过：{gate_reason}"

        routes.append({
            "cluster_id": c["cluster_id"],
            "cluster_title": c.get("title", ""),
            "action": action or "new",
            "target_id": target_id,
            "reason": reason,
            "members": len(c.get("member_source_ids", [])),
            "candidates": [
                {"proposal_id": s["proposal"]["proposal_id"], "score": round(s["score"], 3)}
                for s in scored
            ],
        })

    _ensure_input_dir()
    save_json(WEEKEND_INPUT_DIR / f"routes-{now_utc()[:10]}.json", {"routes": routes})
    from collections import Counter
    return {
        "success": True,
        "routes": len(routes),
        "actions": dict(Counter(r.get("action") for r in routes)),
    }


def _llm_arbitrate_cluster(
    cluster: Dict[str, Any],
    scored: List[Dict[str, Any]],
) -> tuple:
    """LLM 仲裁簇与课题的关系（Jaccard 中低置信时）。

    v6.9.18 补：仲裁选项加 defer（非研究内容/质量不足不路由），
    并向 LLM 说明 new 的实际后果（注册新研究课题进人工立项队列）
    ——08-16 复跑实测旧三选项下运维簇只能被塞给 new。

    Returns:
        (action, target_id, reason)。LLM 不可用/失败 → ("new", None, "无匹配")。
    """
    if not is_llm_available():
        return "new", None, "Jaccard 低置信且 LLM 不可用，按新课题处理"

    cands = "\n".join(
        f"- [{s['proposal']['status']}] {s['proposal']['proposal_id']}: "
        f"{s['proposal']['title']}（相似度 {s['score']:.2f}）摘要：{s['proposal']['text'][:300]}"
        for s in scored
    ) or "（无候选课题）"

    system = (
        "你是林赛，判断一个知识簇与候选课题的关系。merge=信息属于该课题应融合；"
        "expansion=主题相邻应把文献挂为补充信息源；new=值得开创新研究课题"
        "（将注册为新课题并进入人工立项队列，需具备明确科学问题）；"
        "defer=非研究内容（系统运维/流程记录）或科学含量不足，不应路由。"
        "【核心主题约束（v6.9.22）】课题组核心范式是强场超快光学："
        "要么通过强场/THz 光场实现物性操控（强场驱动、Floquet 工程），"
        "要么用高次谐波光谱/超快光谱实现超快测量（HHG 谱学、泵浦-探测）。"
        "若知识簇不含任何强场操控或超快测量维度（纯准静态凝聚态物性、"
        "器件工程、静态第一性原理计算），不得判 new——可判 defer（主题"
        "不对齐，继续积累等待范式嫁接）或 merge/expansion（注入现有课题）。"
        '输出 JSON：{"action": "merge|expansion|new|defer", '
        '"target_id": "课题id或null", "reason": "一句话"}。'
    )
    user = (
        f"知识簇：{cluster.get('title', '')}\n"
        f"簇摘要：{cluster.get('summary', '')[:600]}\n"
        f"关键词：{', '.join(cluster.get('keywords', []))}\n\n"
        f"候选课题：\n{cands}"
    )
    verdict = _llm_json(system, user, timeout=90)
    if isinstance(verdict, dict) and verdict.get("action") in ("merge", "expansion", "new", "defer"):
        action = verdict["action"]
        target = verdict.get("target_id")
        if action in ("merge", "expansion") and not target:
            # action 指向课题但未给 id：回退最高分候选
            if scored:
                target = scored[0]["proposal"]["proposal_id"]
            else:
                action = "new"
                target = None
        if action == "defer":
            target = None
        return action, target, verdict.get("reason", "LLM 仲裁")
    return "new", None, "LLM 仲裁失败，按新课题处理"


def _group_merge_routes(
    merge_routes: List[Dict[str, Any]],
    cluster_index: Dict[str, Dict[str, Any]],
    threshold: float = 0.30,
) -> Dict[str, str]:
    """同目标课题的 merge 簇连通分组（v6.9.18）。

    按目标课题分组后，组内只保留一个"主簇"（成员最多）走 enrich
    知识卡注入，其余簇只挂信息源——根治 08-16 实测 BSV 课题被 6
    个同主题变体簇重复注入（enrich 句级去重对同义不同措辞的知识
    卡无能为力）。

    Returns:
        {cluster_id: 同组主簇 id}——非主簇映射到主簇 id。
    """
    from .clusters import cluster_similarity

    leader: Dict[str, str] = {}
    groups_by_target: Dict[str, List[Dict[str, Any]]] = {}
    for r in merge_routes:
        c = cluster_index.get(r.get("cluster_id", ""))
        target = r.get("target_id", "")
        if not c or not target:
            continue
        groups = groups_by_target.setdefault(target, [])
        placed = False
        for g in groups:
            if cluster_similarity(c, g["leader"]) >= threshold:
                leader[c["cluster_id"]] = g["leader"]["cluster_id"]
                # 主簇取成员更多者（组内重组时更新 follower 映射）
                if len(c.get("member_source_ids", [])) > len(g["leader"].get("member_source_ids", [])):
                    leader[g["leader"]["cluster_id"]] = c["cluster_id"]
                    g["leader"] = c
                placed = True
                break
        if not placed:
            leader[c["cluster_id"]] = c["cluster_id"]
            groups.append({"leader": c})
    return leader


def run_input_compose(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """路由落地：簇融入课题/注册新课题/挂载补充信息源（进下周工作流）。

    v6.9.12 三条路由落地（取代旧 compose 依赖 decisions 且 expansion
    空转）：
    - new：register_from_idea 注册 drafts 新课题
    - merge：enrich_from_idea 注入活跃课题 + 文献挂载到 02_literature
    - expansion：文献挂载到课题 02_literature/supplementary-sources-{date}.json
      （references 校验步骤与下周 writer 可读）
    全部路由完成后簇标 linked，不再吸收新成员。
    v6.9.18:
    - defer 路由不落地（簇保持 open 继续积累，等待成员/知识卡成熟）；
    - 同目标课题的多个 merge 簇先连通分组，组内只有主簇注入知识卡，
      其余簇只挂信息源（防同主题变体簇重复注入）；
    - 信息源挂载改用簇内 member_summaries（跨周可用），修复旧实现
      依赖当天 summaries 文件导致跨周成员挂载必失败（08-16 实测
      expansion 成功率 12/58）。
    """
    from proposal_lifecycle import ProposalLifecycle
    from .clusters import load_clusters, mark_linked, save_clusters

    routes_path = WEEKEND_INPUT_DIR / f"routes-{now_utc()[:10]}.json"
    routes = load_json(routes_path, default={}).get("routes", [])

    # 摘要索引：source_id → 摘要条目（member_summaries 缺 path 的旧簇回退用）
    summaries_path = WEEKEND_INPUT_DIR / f"summaries-{now_utc()[:10]}.json"
    summaries = load_json(summaries_path, default={}).get("summaries", [])
    summary_index = {s.get("source_id", ""): s for s in summaries if isinstance(s, dict)}

    registry = load_clusters()
    cluster_index = {c.get("cluster_id"): c for c in registry.get("clusters", [])}

    # 同目标 merge 簇分组：非主簇只挂信息源不重复注入
    merge_routes = [r for r in routes if r.get("action") == "merge" and r.get("target_id")]
    leader_map = _group_merge_routes(merge_routes, cluster_index)

    lc = ProposalLifecycle()
    actions = []
    for r in routes:
        cid = r.get("cluster_id", "")
        cluster = cluster_index.get(cid)
        if not cluster:
            continue
        action = r.get("action", "new")
        target_id = r.get("target_id")

        if action == "defer":
            # v6.9.18: 暂缓路由——簇保持 open 继续积累，不落地不标 linked
            actions.append({
                "cluster_id": cid, "cluster_title": cluster.get("title", ""),
                "action": "defer", "result": {"success": True, "action": "defer",
                                              "message": r.get("reason", "门槛未过，继续积累")},
            })
            continue

        is_merge_follower = (
            action == "merge"
            and leader_map.get(cid, cid) != cid
        )
        if is_merge_follower:
            # 同组非主簇：只挂信息源，不重复注入知识卡
            if dry_run:
                result = {"action": "merge_follower", "target_id": target_id, "dry_run": True}
            else:
                written = _write_supplementary_sources(target_id, cluster, summary_index)
                result = {"success": written, "action": "merge_follower", "target_id": target_id,
                          "message": "同组非主簇：仅挂载信息源（知识卡由主簇注入）"}
                if written:
                    mark_linked(registry, cid, target_id or "")
            actions.append({
                "cluster_id": cid, "cluster_title": cluster.get("title", ""),
                "action": "merge_follower", "result": result,
            })
            continue

        idea = {
            "title": cluster.get("title", ""),
            "background": f"知识簇综合：{cluster.get('summary', '')}",
            "gap": "；".join(cluster.get("open_questions", []) or []) or cluster.get("summary", "")[:200],
            "content": cluster.get("member_source_ids", []),
            "approach": "待进一步细化",
            "innovations": cluster.get("open_questions", []) or [cluster.get("summary", "")[:120]],
            "sources": [
                {"title": m.get("title", sid), "source_type": "weekend_cluster"}
                for sid, m in ((ms.get("source_id", ""), ms) for ms in cluster.get("member_summaries", []))
            ],
            "keywords": cluster.get("keywords", []),
            "cluster_id": cid,  # v6.9.18: enrich 注入标题带簇 ID 防去重误删
            "generated_at": now_utc(),
            "reliability": RELIABILITY_DERIVED,
        }

        if dry_run:
            result = {"action": action, "target_id": target_id, "dry_run": True}
        elif action == "new":
            result = lc.register_from_idea(idea, project_type="general")
        elif action == "merge" and target_id:
            result = lc.enrich_from_idea(target_id, idea)
            result = dict(result) if isinstance(result, dict) else {"success": False}
            result["supplementary_written"] = _write_supplementary_sources(target_id, cluster, summary_index)
        elif action == "expansion" and target_id:
            written = _write_supplementary_sources(target_id, cluster, summary_index)
            result = {"success": written, "action": "expansion", "target_id": target_id,
                      "message": "补充信息源已挂载到课题文献目录"}
        else:
            result = {"action": action, "target_id": target_id, "message": "路由目标缺失，跳过"}

        if not dry_run and result.get("success") and action != "new":
            mark_linked(registry, cid, result.get("proposal_id") or target_id or "")
        elif not dry_run and action == "new" and result.get("success"):
            mark_linked(registry, cid, result.get("proposal_id", ""))

        actions.append({"cluster_id": cid, "cluster_title": cluster.get("title", ""), "action": action, "result": result})

    if not dry_run:
        save_clusters(registry)
        save_json(WEEKEND_INPUT_DIR / f"ideas-{now_utc()[:10]}.json", {"generated_at": now_utc(), "actions": actions})

    return {"success": True, "ideas_count": len(actions)}


def _write_supplementary_sources(
    proposal_id: str,
    cluster: Dict[str, Any],
    summary_index: Dict[str, Dict[str, Any]],
) -> bool:
    """把簇成员文献挂载为课题补充信息源（02_literature/ 下）。

    融入下周工作流的机制：references 校验步骤与 writer 以课题目录
    为输入域，补充清单落盘后即进入下一轮优化的可见范围。
    v6.9.18: 条目改从簇自身 member_summaries 构建（含跨周成员），
    当天 summaries 索引仅作旧簇（无 member_summaries）的回退——
    旧实现只用当天索引，跨周积累的簇成员全部查不到，08-16 实测
    expansion 挂载成功率 12/58。
    """
    from proposal_lifecycle import ProposalLifecycle

    try:
        lc = ProposalLifecycle()
        prop_dir = lc._find_proposal_dir(proposal_id)
        if not prop_dir:
            return False
        lit_dir = prop_dir / "02_literature"
        lit_dir.mkdir(parents=True, exist_ok=True)

        entries = []
        seen_sids = set()
        for ms in cluster.get("member_summaries", []):
            sid = ms.get("source_id", "")
            if not sid or sid in seen_sids:
                continue
            seen_sids.add(sid)
            entries.append({
                "source_id": sid,
                "title": ms.get("title", ""),
                "summary": ms.get("summary", ""),
                "path": ms.get("path", "") or summary_index.get(sid, {}).get("path", ""),
                "added_via": f"cluster:{cluster.get('cluster_id', '')}",
                "added_at": now_utc(),
            })
        # 旧簇回退：member_summaries 缺失时从当天摘要索引补
        if not entries:
            for sid in cluster.get("member_source_ids", []):
                s = summary_index.get(sid)
                if s:
                    entries.append({
                        "source_id": sid,
                        "title": s.get("title", ""),
                        "summary": s.get("summary", ""),
                        "path": s.get("path", ""),
                        "added_via": f"cluster:{cluster.get('cluster_id', '')}",
                        "added_at": now_utc(),
                    })
        if not entries:
            return False
        out = lit_dir / f"supplementary-sources-{now_utc()[:10]}.json"
        save_json(out, {"proposal_id": proposal_id, "cluster_id": cluster.get("cluster_id", ""),
                        "entries": entries})
        return True
    except Exception as e:
        if _log:
            _log.warning(f"补充信息源挂载失败（{proposal_id}）: {e}")
        return False
