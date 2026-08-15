#!/usr/bin/env python3
"""输入阶段 job 执行器。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

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


def _llm_json(system: str, user: str, timeout: int = 120) -> Any:
    """调用 LLM 并解析 JSON。"""
    if not is_llm_available():
        return None
    ok, text, meta = llm_complete(system, user, timeout=timeout)
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

    sources = collect_all_sources(state=state, days=7, paper_limit=20, capture_limit=10)
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


def run_input_summarize(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """对新增论文/简报做轻量摘要（聚类主源：tier ≤2）。

    v6.9.7: 无新增论文时也写出空产物文件——job 模板已声明
    artifact=summaries-{date}.json，产物校验依赖"done 必有产物"
    不变式；此前无新增论文提前 return 不落文件，会导致下一轮
    sync 误判产物缺失而反复重置（空转循环）。
    v6.9.12: 摘要条目携带 source_id/path/tier，供下游增量归簇
    与信息源挂载回溯原始文献。
    """
    sources = collect_all_sources(state=state, days=7, paper_limit=20, capture_limit=10)
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
    system = "你是林赛，擅长对学术文献做一句话核心摘要。输出合法 JSON 数组。"
    # v6.9.11: 单次容量 10 → 30。每篇 LLM timeout 60s，最坏 30×60=1800s，
    # 在 weekend job stale 阈值（STALE_RUNNING_SECONDS=3600）内安全。
    # 旧值 10 配合每周一跑，消化能力 ~10 条/周 < 稳态新料增速，且补课
    # 积压（92 条）需 9 周才能清完。
    failed_llm = 0
    for p in papers[:30]:
        user = f"请用 1-2 句话总结以下文献的核心贡献：\n\n标题：{p.get('title', '')}\n内容：{p.get('text', '')[:1200]}\n\n输出 JSON：{{\"title\": \"...\", \"summary\": \"...\", \"keywords\": [\"...\"]}}"
        data = _llm_json(system, user, timeout=60)
        if data:
            # v6.9.12: 回填溯源字段（归簇成员清单、信息源挂载依赖）
            if isinstance(data, dict):
                data["source_id"] = p.get("source_id", "")
                data["path"] = p.get("path", "")
                data["tier"] = p.get("tier", 2)
                if not data.get("keywords"):
                    data["keywords"] = []
            summaries.append(data)
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
        elif not c.get("summary"):
            # 降级：成员摘要拼接（无 LLM 时保持链路可继续）
            joined = "；".join(m.get("summary", "") for m in members[:6])
            c["summary"] = joined[:500]
        distilled_out.append({
            "cluster_id": c["cluster_id"],
            "title": c["title"],
            "members": len(c.get("member_source_ids", [])),
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


def run_input_topic_match(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """课题判断：open 簇 vs 全阶段课题，产出路由决策（merge/new/expansion）。

    两级判断：Jaccard 预筛 top-3 候选 → LLM 仲裁（概念级重合判断，
    词袋测不出的同机制不同术语场景）。LLM 不可用时回退纯 Jaccard
    阈值（0.35，与旧口径一致）。
    """
    from .clusters import load_clusters

    if dry_run:
        return {"success": True, "routes": 0, "dry_run": True, "message": "dry-run 跳过课题匹配"}

    registry = load_clusters()
    open_c = [c for c in registry.get("clusters", []) if c.get("status") == "open"]
    if not open_c:
        _ensure_input_dir()
        save_json(WEEKEND_INPUT_DIR / f"routes-{now_utc()[:10]}.json", {"routes": []})
        return {"success": True, "routes": 0, "message": "无待路由簇"}

    proposals = _load_all_stage_proposals()
    routes = []
    for c in open_c:
        cluster_text = " ".join([c.get("title", ""), c.get("summary", ""), " ".join(c.get("keywords", []))])
        scored = sorted(
            (
                {"proposal": p, "score": _jaccard_similarity(cluster_text, p["title"] + " " + p["text"])}
                for p in proposals
            ),
            key=lambda x: x["score"],
            reverse=True,
        )[:3]

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

        routes.append({
            "cluster_id": c["cluster_id"],
            "cluster_title": c.get("title", ""),
            "action": action or "new",
            "target_id": target_id,
            "reason": reason,
            "candidates": [
                {"proposal_id": s["proposal"]["proposal_id"], "score": round(s["score"], 3)}
                for s in scored
            ],
        })

    _ensure_input_dir()
    save_json(WEEKEND_INPUT_DIR / f"routes-{now_utc()[:10]}.json", {"routes": routes})
    return {"success": True, "routes": len(routes)}


def _llm_arbitrate_cluster(
    cluster: Dict[str, Any],
    scored: List[Dict[str, Any]],
) -> tuple:
    """LLM 仲裁簇与课题的关系（Jaccard 中低置信时）。

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
        "expansion=主题相邻应把文献挂为补充信息源；new=与现有课题无关。"
        '输出 JSON：{"action": "merge|expansion|new", "target_id": "课题id或null", "reason": "一句话"}。'
    )
    user = (
        f"知识簇：{cluster.get('title', '')}\n"
        f"簇摘要：{cluster.get('summary', '')[:600]}\n"
        f"关键词：{', '.join(cluster.get('keywords', []))}\n\n"
        f"候选课题：\n{cands}"
    )
    verdict = _llm_json(system, user, timeout=90)
    if isinstance(verdict, dict) and verdict.get("action") in ("merge", "expansion", "new"):
        action = verdict["action"]
        target = verdict.get("target_id")
        if action != "new" and not target:
            # action 指向课题但未给 id：回退最高分候选
            if scored:
                target = scored[0]["proposal"]["proposal_id"]
            else:
                action = "new"
                target = None
        return action, target, verdict.get("reason", "LLM 仲裁")
    return "new", None, "LLM 仲裁失败，按新课题处理"


def run_input_compose(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """路由落地：簇融入课题/注册新课题/挂载补充信息源（进下周工作流）。

    v6.9.12 三条路由全部落地（取代旧 compose 依赖 decisions 且
    expansion 空转）：
    - new：register_from_idea 注册 drafts 新课题
    - merge：enrich_from_idea 注入活跃课题 + 文献挂载到 02_literature
    - expansion：文献挂载到课题 02_literature/supplementary-sources-{date}.json
      （references 校验步骤与下周 writer 可读）
    全部路由完成后簇标 linked，不再吸收新成员。
    """
    from proposal_lifecycle import ProposalLifecycle
    from .clusters import load_clusters, mark_linked, save_clusters

    routes_path = WEEKEND_INPUT_DIR / f"routes-{now_utc()[:10]}.json"
    routes = load_json(routes_path, default={}).get("routes", [])

    # 摘要索引：source_id → 摘要条目（信息源挂载需要 title/summary/path）
    summaries_path = WEEKEND_INPUT_DIR / f"summaries-{now_utc()[:10]}.json"
    summaries = load_json(summaries_path, default={}).get("summaries", [])
    summary_index = {s.get("source_id", ""): s for s in summaries if isinstance(s, dict)}

    registry = load_clusters()
    cluster_index = {c.get("cluster_id"): c for c in registry.get("clusters", [])}

    lc = ProposalLifecycle()
    actions = []
    for r in routes:
        cid = r.get("cluster_id", "")
        cluster = cluster_index.get(cid)
        if not cluster:
            continue
        action = r.get("action", "new")
        target_id = r.get("target_id")

        idea = {
            "title": cluster.get("title", ""),
            "background": f"知识簇综合：{cluster.get('summary', '')}",
            "gap": "；".join(cluster.get("open_questions", []) or []) or cluster.get("summary", "")[:200],
            "content": cluster.get("member_source_ids", []),
            "approach": "待进一步细化",
            "innovations": cluster.get("open_questions", []) or [cluster.get("summary", "")[:120]],
            "sources": [
                {"title": summary_index.get(sid, {}).get("title", sid), "source_type": "weekend_cluster"}
                for sid in cluster.get("member_source_ids", [])
                if sid in summary_index
            ],
            "keywords": cluster.get("keywords", []),
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
            # v6.9.12 落地：旧版仅记录建议（空转）
            written = _write_supplementary_sources(target_id, cluster, summary_index)
            result = {"success": written, "action": "expansion", "target_id": target_id,
                      "message": "补充信息源已挂载到课题文献目录"}
        else:
            result = {"action": action, "target_id": target_id, "message": "路由目标缺失，跳过"}

        if not dry_run and result.get("success") and action != "new":
            # 新课题 register 后 proposal_id 在 result 里，同样标 linked
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
