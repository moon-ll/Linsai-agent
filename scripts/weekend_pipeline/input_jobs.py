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
    """收集来源并记录 processed_sources。"""
    sources = collect_all_sources(state=state, days=7, paper_limit=20, capture_limit=10)
    _ensure_input_dir()
    if not dry_run:
        save_json(WEEKEND_INPUT_DIR / f"sources-{now_utc()[:10]}.json", sources)
    return {"success": True, "source_counts": {k: len(v) if isinstance(v, list) else len(v) for k, v in sources.items() if k != "collected_at"}}


def run_input_summarize(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """对新增论文/简报做轻量摘要。"""
    sources = collect_all_sources(state=state, days=7, paper_limit=20, capture_limit=10)
    papers = new_paper_sources(sources, state)
    if not papers:
        return {"success": True, "summarized": 0, "message": "无新增论文/简报"}

    if dry_run:
        return {"success": True, "summarized": len(papers), "dry_run": True, "message": "dry-run 跳过 LLM 摘要"}

    if not is_llm_available():
        return {"success": False, "error": "LLM 不可用"}

    summaries = []
    system = "你是林赛，擅长对学术文献做一句话核心摘要。输出合法 JSON 数组。"
    for p in papers[:10]:
        user = f"请用 1-2 句话总结以下文献的核心贡献：\n\n标题：{p.get('title', '')}\n内容：{p.get('text', '')[:1200]}\n\n输出 JSON：{{\"title\": \"...\", \"summary\": \"...\", \"keywords\": [\"...\"]}}"
        data = _llm_json(system, user, timeout=60)
        if data:
            summaries.append(data)
            mark_source_processed(p["source_id"], p["text"], state)

    _ensure_input_dir()
    if not dry_run:
        save_json(WEEKEND_INPUT_DIR / f"summaries-{now_utc()[:10]}.json", {"summaries": summaries})

    return {"success": True, "summarized": len(summaries)}


def run_input_gap_analysis(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """基于摘要与 KB 识别研究缺口。"""
    summaries_path = WEEKEND_INPUT_DIR / f"summaries-{now_utc()[:10]}.json"
    summaries = load_json(summaries_path, default={}).get("summaries", [])

    if dry_run:
        return {"success": True, "directions_count": 2, "dry_run": True, "message": "dry-run 跳过 LLM 缺口分析"}

    kb_concepts = []
    for item in state.get("processed_sources", {}).values():
        if isinstance(item, dict) and item.get("source_id", "").startswith("kb:concept"):
            kb_concepts.append(item)

    system = (
        "你是林赛，擅长识别研究缺口。基于提供的文献摘要和知识库概念，"
        "输出 1-5 条研究缺口，每条包含 title/gap/keywords/related_sources。输出合法 JSON。"
    )
    user = f"""文献摘要：
{json.dumps(summaries[:8], ensure_ascii=False, indent=2)}

知识库概念：
{json.dumps(kb_concepts[:5], ensure_ascii=False, indent=2)}

输出 JSON 数组：
[{{"title": "...", "gap": "...", "keywords": ["..."], "related_sources": ["..."]}}]
"""
    directions = _llm_json(system, user, timeout=120) or []

    _ensure_input_dir()
    if not dry_run:
        save_json(WEEKEND_INPUT_DIR / f"directions-{now_utc()[:10]}.json", {"directions": directions})

    return {"success": True, "directions_count": len(directions)}


def run_input_direction_select(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """对比现有 proposal，决策 new/merge/expansion。"""
    directions_path = WEEKEND_INPUT_DIR / f"directions-{now_utc()[:10]}.json"
    directions = load_json(directions_path, default={}).get("directions", [])

    if dry_run:
        return {"success": True, "decisions_count": 0, "dry_run": True, "message": "dry-run 跳过方向选择"}

    # 读取 KB 中的 proposal 页面
    proposals_kb_dir = PROJECT_ROOT / "knowledge" / "wiki" / "projects" / "NSFC-强场超快" / "proposals"
    existing = []
    if proposals_kb_dir.exists():
        for f in proposals_kb_dir.glob("*.md"):
            if f.name == "proposals-index.md":
                continue
            text = _read_text(f, 3000)
            title = ""
            status = ""
            for line in text.split("\n"):
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"')
                if "生命周期状态" in line:
                    status = line.split("：")[-1].strip()
            existing.append({
                "proposal_id": f.stem,
                "title": title,
                "status": status,
                "text": text[:1000],
            })

    decisions = []
    for d in directions:
        idea_text = " ".join([d.get("title", ""), d.get("gap", ""), " ".join(d.get("keywords", []))])
        best = None
        best_score = 0.0
        for p in existing:
            score = _jaccard_similarity(idea_text, p["title"] + " " + p["text"])
            if score > best_score:
                best_score = score
                best = p

        if best and best_score > 0.35:
            if best.get("status") in ("优化中", "待校验"):
                action = "merge"
            else:
                action = "expansion"
        else:
            action = "new"

        decisions.append({
            "direction": d,
            "action": action,
            "target_id": best["proposal_id"] if best and action != "new" else None,
            "similarity": best_score,
        })

    if not dry_run:
        save_json(WEEKEND_INPUT_DIR / f"decisions-{now_utc()[:10]}.json", {"decisions": decisions})

    return {"success": True, "decisions_count": len(decisions)}


def run_input_retrieve_supplementary(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """对 new 方向，先在 KB 中检索，再决定是否需要补充检索。"""
    decisions_path = WEEKEND_INPUT_DIR / f"decisions-{now_utc()[:10]}.json"
    decisions = load_json(decisions_path, default={}).get("decisions", [])

    if dry_run:
        return {"success": True, "new_directions": 0, "kb_hits": 0, "dry_run": True, "message": "dry-run 跳过补充检索"}

    new_directions = [d for d in decisions if d.get("action") == "new"]
    supplementary = []
    for d in new_directions:
        query = " ".join(d.get("direction", {}).get("keywords", []))
        kb_results = search_kb_for_query(query, top_k=3) if query else []
        kb_papers = list_kb_paper_pages()

        # 若 KB 已有 paper 页面覆盖，直接引用
        refs = [{"type": "kb", "path": r.get("path", "")} for r in kb_results]
        refs.extend([{"type": "kb_paper", "path": p.get("path", "")} for p in kb_papers[:3]])

        supplementary.append({
            "direction": d.get("direction", {}),
            "kb_hits": len(refs),
            "references": refs,
        })

    if not dry_run:
        save_json(WEEKEND_INPUT_DIR / f"supplementary-{now_utc()[:10]}.json", {"supplementary": supplementary})

    return {"success": True, "new_directions": len(new_directions), "kb_hits": sum(s["kb_hits"] for s in supplementary)}


def run_input_deep_read(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """对补充检索到的核心 paper 做深度阅读（优先复用本地 raw papers）。"""
    sup_path = WEEKEND_INPUT_DIR / f"supplementary-{now_utc()[:10]}.json"
    supplementary = load_json(sup_path, default={}).get("supplementary", [])

    if dry_run:
        return {"success": True, "deep_read_count": 0, "dry_run": True, "message": "dry-run 跳过深度阅读"}

    read_results = []
    raw_papers_dir = PROJECT_ROOT / "knowledge" / "raw" / "papers"
    for item in supplementary:
        # 本地 raw 目录查找候选 PDF/笔记
        candidates = []
        if raw_papers_dir.exists():
            for f in raw_papers_dir.iterdir():
                if f.is_file():
                    candidates.append(str(f.relative_to(PROJECT_ROOT)))

        read_results.append({
            "direction": item.get("direction", {}).get("title", ""),
            "local_candidates": candidates[:5],
            "status": "待深度阅读",
        })

    if not dry_run:
        save_json(WEEKEND_INPUT_DIR / f"deep-read-{now_utc()[:10]}.json", {"read_results": read_results})

    return {"success": True, "deep_read_count": len(read_results)}


def run_input_compose(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """综合生成结构化研究设想，并调用 proposal_lifecycle 注册/融合/扩展。"""
    from proposal_lifecycle import ProposalLifecycle

    decisions_path = WEEKEND_INPUT_DIR / f"decisions-{now_utc()[:10]}.json"
    decisions = load_json(decisions_path, default={}).get("decisions", [])

    lc = ProposalLifecycle()
    actions = []
    for d in decisions[:3]:
        direction = d.get("direction", {})
        idea = {
            "title": direction.get("title", ""),
            "background": f"基于近期文献与 KB 分析识别出的研究缺口：{direction.get('gap', '')}",
            "gap": direction.get("gap", ""),
            "content": direction.get("related_sources", []),
            "approach": "待进一步细化",
            "innovations": [direction.get("gap", "")],
            "sources": [{"title": direction.get("title", ""), "source_type": "weekend_pipeline"}],
            "keywords": direction.get("keywords", []),
            "generated_at": now_utc(),
            "reliability": RELIABILITY_DERIVED,
        }

        action = d.get("action")
        target_id = d.get("target_id")
        if dry_run:
            result = {"action": action, "target_id": target_id, "dry_run": True}
        elif action == "new":
            name = safe_filename(idea["title"])[:40].strip("-").lower() or "new-idea"
            pid = lc.generate_proposal_id(name=name, project_type="general")
            result = lc.register_from_idea(idea, project_type="general")
        elif action == "merge" and target_id:
            result = lc.enrich_from_idea(target_id, idea)
        else:
            result = {"action": "expansion", "target_id": target_id, "message": "已记录扩展建议"}

        actions.append({"idea_title": idea["title"], "action": action, "result": result})

    if not dry_run:
        save_json(WEEKEND_INPUT_DIR / f"ideas-{now_utc()[:10]}.json", {"generated_at": now_utc(), "actions": actions})

    return {"success": True, "ideas_count": len(actions)}
