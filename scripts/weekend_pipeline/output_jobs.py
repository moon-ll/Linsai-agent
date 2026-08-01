#!/usr/bin/env python3
"""输出阶段 job 执行器。"""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from common import load_json, now_utc, save_json, safe_filename
from llm_gateway import is_llm_available, llm_complete
from paths import PROJECT_ROOT
from proposal_lifecycle import ProposalLifecycle

from .constants import (
    RELIABILITY_DERIVED,
    RELIABILITY_RELIABLE,
    RELIABILITY_UNVERIFIED,
    WEEKEND_OUTPUT_DIR,
)
from .sources import collect_briefings, collect_captures, collect_reference_notes

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


KB_ROOT = PROJECT_ROOT / "knowledge" / "wiki"
KB_CONCEPTS_DIR = KB_ROOT / "concepts"
KB_METHODS_DIR = KB_ROOT / "methods"
KB_PEOPLE_DIR = KB_ROOT / "people"
KB_PAPERS_DIR = KB_ROOT / "papers"
KB_REVIEWS_DIR = KB_ROOT / "reviews"
UNVERIFIED_CLAIMS_PATH = PROJECT_ROOT / "knowledge" / ".cache" / "unverified-claims.json"
HEALTH_REPORT_PATH = PROJECT_ROOT / "knowledge" / ".cache" / "kb-health-weekly.json"


def _ensure_output_dirs() -> None:
    WEEKEND_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for d in [KB_CONCEPTS_DIR, KB_METHODS_DIR, KB_PEOPLE_DIR, KB_PAPERS_DIR, KB_REVIEWS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    UNVERIFIED_CLAIMS_PATH.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def _read_text(path: Path, max_chars: int = 8000) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except Exception:
        return ""


def _llm_json(system: str, user: str, timeout: int = 120) -> Any:
    if not is_llm_available():
        return None
    ok, text, meta = llm_complete(system, user, timeout=timeout)
    if not ok:
        return None
    try:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        json_str = m.group(1) if m else text
        return json.loads(json_str)
    except Exception:
        return None


def _extract_frontmatter(text: str) -> tuple:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, m.group(2)


def _write_wiki_page(kind: str, title: str, body: str, sources: List[Dict[str, Any]],
                     reliability: str = RELIABILITY_DERIVED) -> Dict[str, Any]:
    """写入 wiki 页面，已存在则追加。"""
    _ensure_output_dirs()
    if kind == "concept":
        path = KB_CONCEPTS_DIR / (safe_filename(title) + ".md")
    elif kind == "method":
        path = KB_METHODS_DIR / (safe_filename(title) + ".md")
    elif kind == "person":
        path = KB_PEOPLE_DIR / (safe_filename(title) + ".md")
    elif kind == "paper":
        path = KB_PAPERS_DIR / (safe_filename(title) + ".md")
    else:
        path = KB_ROOT / (safe_filename(title) + ".md")

    existing = _read_text(path)
    if existing:
        existing_fm, existing_body = _extract_frontmatter(existing)
        body = existing_body + "\n\n---\n\n" + body
        sources = existing_fm.get("sources", []) + sources

    frontmatter = {
        "title": title,
        "type": kind,
        "source_reliability": reliability,
        "sources": sources,
        "updated_at": now_utc(),
        "created_at": existing and _extract_frontmatter(existing)[0].get("created_at", now_utc()) or now_utc(),
    }

    fm_lines = ["---"]
    for k, v in frontmatter.items():
        if isinstance(v, list):
            fm_lines.append(f"{k}:")
            for item in v:
                if isinstance(item, dict):
                    fm_lines.append(f"  - title: \"{item.get('title', '')}\"")
                    fm_lines.append(f"    source_type: {item.get('source_type', '')}")
                else:
                    fm_lines.append(f"  - {item}")
        else:
            fm_lines.append(f'{k}: "{v}"')
    fm_lines.append("---")

    content = "\n".join(fm_lines) + "\n\n" + body
    path.write_text(content, encoding="utf-8")
    return {"success": True, "path": str(path.relative_to(PROJECT_ROOT)), "reliability": reliability}


# ---------------------------------------------------------------------------
# Job handlers
# ---------------------------------------------------------------------------


def run_output_sync_proposals(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """调用 proposal_kb_sync 把所有 proposal 同步到 KB。"""
    import proposal_kb_sync as pks
    sync = pks.ProposalKbSync()
    result = sync.sync_all(dry_run=dry_run)
    return {"success": True, **result}


def run_output_extract(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """根据 job_id 判断是 archived proposal 萃取还是 daily knowledge 萃取。"""
    job_id = job.get("job_id", "")
    if job_id.startswith("output_extract_archived_proposal_"):
        return _extract_archived_proposal(job_id[len("output_extract_archived_proposal_"):], dry_run=dry_run)
    if job_id == "output_extract_daily_knowledge":
        return _extract_daily_knowledge(dry_run=dry_run)
    return {"success": False, "error": f"未知 extract job: {job_id}"}


def _archive_proposal_files(proposal_id: str, prop_dir: Path) -> Dict[str, Any]:
    """将 proposal 核心产物复制到 knowledge/raw/projects/{proposal_id}/。"""
    archive_dir = PROJECT_ROOT / "knowledge" / "raw" / "projects" / proposal_id
    archive_dir.mkdir(parents=True, exist_ok=True)

    files_to_archive = [
        ("00_proposal-brief.md", "研究设想"),
        ("03_method/method-manual.md", "方法学手册"),
        ("02_literature/reading-notes.md", "文献阅读笔记"),
        ("04_proposal/proposal-draft.md", "申请书"),
    ]

    archived = []
    for rel_path, label in files_to_archive:
        src = prop_dir / rel_path
        if src.exists():
            dst = archive_dir / src.name
            shutil.copy2(src, dst)
            archived.append({"label": label, "path": str(dst.relative_to(PROJECT_ROOT))})

    return {"success": True, "archive_dir": str(archive_dir.relative_to(PROJECT_ROOT)), "archived": archived}


def _extract_archived_proposal(proposal_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """从已归档 proposal 萃取可靠知识，并归档核心产物。"""
    lc = ProposalLifecycle()
    prop_dir = lc._find_proposal_dir(proposal_id)
    if not prop_dir:
        return {"success": False, "error": "proposal 目录不存在"}

    proposal_text = _read_text(prop_dir / "04_proposal" / "proposal-draft.md", 8000)
    if not proposal_text:
        return {"success": False, "error": "申请书为空"}

    if dry_run:
        return {"success": True, "proposal_id": proposal_id, "dry_run": True, "message": "dry-run 跳过归档萃取"}

    # 1. 归档核心产物到 knowledge/raw/projects/
    archive_result = _archive_proposal_files(proposal_id, prop_dir)

    if not is_llm_available():
        return {"success": False, "error": "LLM 不可用", "archive_result": archive_result}

    # 2. 从申请书 + 方法学手册萃取可靠知识
    method_text = _read_text(prop_dir / "03_method" / "method-manual.md", 4000)
    combined_text = proposal_text[:4000]
    if method_text:
        combined_text += f"\n\n【方法学手册补充】\n{method_text[:2000]}"

    system = (
        "你是林赛，擅长从归档申请书中萃取可靠知识。只提取有明确依据的概念、方法、关键论文和创新点。"
        "输出合法 JSON。"
    )
    user = f"""请从以下已归档 NSFC 申请书（含方法学手册）中萃取知识：

```
{combined_text}
```

输出格式：
{{
  "concepts": [{{"title": "...", "summary": "...", "source_passage": "..."}}],
  "methods": [{{"title": "...", "summary": "...", "source_passage": "..."}}],
  "people": [{{"name": "...", "affiliation": "...", "source_passage": "..."}}],
  "papers": [{{"title": "...", "authors": "...", "source_passage": "..."}}]
}}
"""
    extracted = _llm_json(system, user, timeout=120) or {}

    results: Dict[str, List[Dict[str, Any]]] = {"concepts": [], "methods": [], "people": [], "papers": []}
    source_meta = {"title": proposal_id, "source_type": "archived_proposal"}
    for c in extracted.get("concepts", []):
        results["concepts"].append(_write_wiki_page("concept", c["title"], c.get("summary", ""), [source_meta], RELIABILITY_RELIABLE))
    for m in extracted.get("methods", []):
        results["methods"].append(_write_wiki_page("method", m["title"], m.get("summary", ""), [source_meta], RELIABILITY_RELIABLE))
    for p in extracted.get("people", []):
        results["people"].append(_write_wiki_page("person", p["name"], p.get("affiliation", ""), [source_meta], RELIABILITY_RELIABLE))
    for p in extracted.get("papers", []):
        results["papers"].append(_write_wiki_page("paper", p["title"], p.get("authors", ""), [source_meta], RELIABILITY_RELIABLE))

    return {"success": True, "proposal_id": proposal_id, "archive_result": archive_result, "results": results}


def run_output_collect_daily_sources(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """收集日常可靠来源。"""
    sources = []
    sources.extend(collect_briefings(days=7))

    # researcher targeted-research
    lc = ProposalLifecycle()
    for prop in lc.list_by_status("optimizing"):
        pid = prop["proposal_id"]
        prop_dir = lc._find_proposal_dir(pid)
        if not prop_dir:
            continue
        targeted_dir = prop_dir / "02_literature" / "targeted-research"
        if targeted_dir.exists():
            for f in sorted(targeted_dir.glob("lit-gap-*.md"), reverse=True)[:3]:
                sources.append({
                    "source_id": f"researcher:{pid}:{f.name}",
                    "type": "researcher_targeted",
                    "path": str(f.relative_to(PROJECT_ROOT)),
                    "text": _read_text(f, 4000),
                    "reliability": RELIABILITY_RELIABLE,
                })

    sources.extend(collect_reference_notes())
    sources.extend(collect_captures(limit=20))

    if not dry_run:
        save_json(WEEKEND_OUTPUT_DIR / f"daily-sources-{now_utc()[:10]}.json", {"sources": sources})

    return {"success": True, "source_count": len(sources)}


def _extract_daily_knowledge(dry_run: bool = False) -> Dict[str, Any]:
    """从日常来源萃取知识，写 wiki 前检查相似概念。"""
    sources_path = WEEKEND_OUTPUT_DIR / f"daily-sources-{now_utc()[:10]}.json"
    data = load_json(sources_path, default={})
    sources = data.get("sources", [])
    if not sources:
        return {"success": True, "message": "无日常来源"}

    if dry_run:
        return {"success": True, "dry_run": True, "message": "dry-run 跳过日常知识萃取"}

    if not is_llm_available():
        return {"success": False, "error": "LLM 不可用"}

    selected = sources[:6]
    combined = "\n\n---\n\n".join(
        f"【来源: {s['type']} | {s['path']}】\n{s['text'][:1200]}"
        for s in selected
    )

    system = (
        "你是林赛，擅长从文献和讨论中萃取可靠知识。只提取来源中明确提到的概念、方法、论文和学者。"
        "输出合法 JSON。"
    )
    user = f"""请从以下来源中提取可靠知识：

{combined[:5000]}

输出格式：
{{
  "concepts": [{{"title": "...", "summary": "...", "source_path": "..."}}],
  "methods": [{{"title": "...", "summary": "...", "source_path": "..."}}],
  "people": [{{"name": "...", "affiliation": "...", "source_path": "..."}}],
  "papers": [{{"title": "...", "authors": "...", "source_path": "..."}}],
  "unverified_claims": [{{"claim": "...", "reason": "来源未直接支撑"}}]
}}
"""
    extracted = _llm_json(system, user, timeout=150) or {}

    if dry_run:
        return {"success": True, "extracted": extracted, "dry_run": True}

    try:
        import knowledge_base as kb
    except Exception:
        kb = None

    def _source_meta_from_path(source_path: str) -> Dict[str, Any]:
        if "briefing" in source_path:
            return {"title": Path(source_path).name, "source_type": "briefing"}
        if "lit-gap" in source_path:
            return {"title": Path(source_path).name, "source_type": "researcher_targeted"}
        if "references/notes" in source_path:
            return {"title": Path(source_path).name, "source_type": "reference_note"}
        if "captures" in source_path:
            return {"title": Path(source_path).name, "source_type": "capture"}
        return {"title": Path(source_path).name, "source_type": "unknown"}

    results: Dict[str, List[Dict[str, Any]]] = {"concepts": [], "methods": [], "people": [], "papers": []}

    for c in extracted.get("concepts", []):
        title = c["title"]
        summary = c.get("summary", "")
        src = _source_meta_from_path(c.get("source_path", ""))
        # 检查相似概念
        if kb:
            try:
                similar = kb.check_similar_concepts(title, threshold=0.9)
                if similar:
                    similar_path = similar[0].get("path", "")
                    similar_page = kb.get_wiki_page(similar_path)
                    if similar_page:
                        existing_body = similar_page.get("body", "")
                        new_body = existing_body + "\n\n---\n\n" + summary
                        kb.save_wiki_page(similar_path, new_body, similar_page.get("frontmatter", {}))
                        results["concepts"].append({"success": True, "path": similar_path, "action": "append"})
                        continue
            except Exception:
                pass
        results["concepts"].append(_write_wiki_page("concept", title, summary, [src], RELIABILITY_RELIABLE))

    for m in extracted.get("methods", []):
        src = _source_meta_from_path(m.get("source_path", ""))
        results["methods"].append(_write_wiki_page("method", m["title"], m.get("summary", ""), [src], RELIABILITY_RELIABLE))
    for p in extracted.get("people", []):
        src = _source_meta_from_path(p.get("source_path", ""))
        results["people"].append(_write_wiki_page("person", p["name"], p.get("affiliation", ""), [src], RELIABILITY_RELIABLE))
    for p in extracted.get("papers", []):
        src = _source_meta_from_path(p.get("source_path", ""))
        results["papers"].append(_write_wiki_page("paper", p["title"], p.get("authors", ""), [src], RELIABILITY_RELIABLE))

    unverified = extracted.get("unverified_claims", [])
    if unverified:
        existing = load_json(UNVERIFIED_CLAIMS_PATH, default={"claims": []})
        for u in unverified:
            u["recorded_at"] = now_utc()
            existing["claims"].append(u)
        save_json(UNVERIFIED_CLAIMS_PATH, existing)

    return {"success": True, "results": results, "unverified_count": len(unverified)}


def run_output_kb_health(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """运行 KB 健康检查。"""
    _ensure_output_dirs()
    try:
        import knowledge_base as kb
    except Exception:
        return {"success": False, "error": "无法导入 knowledge_base"}

    try:
        health = kb.get_kb_health()
    except Exception as e:
        return {"success": False, "error": f"get_kb_health 失败: {e}"}

    derived_overdue = []
    for page in kb.list_wiki_pages():
        try:
            p = kb.get_wiki_page(page.get("path", ""))
            if not p:
                continue
            fm = p.get("frontmatter", {})
            if fm.get("source_reliability") == RELIABILITY_DERIVED:
                updated = fm.get("updated_at", "")
                if updated:
                    dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    days_old = (datetime.now(timezone.utc) - dt).days
                    if days_old > 30:
                        derived_overdue.append({
                            "title": fm.get("title", ""),
                            "path": page.get("path", ""),
                            "days_old": days_old,
                        })
        except Exception:
            pass

    report = {
        "checked_at": now_utc(),
        "health": health,
        "derived_overdue": derived_overdue,
        "derived_overdue_count": len(derived_overdue),
    }

    if not dry_run:
        save_json(HEALTH_REPORT_PATH, report)

    return {"success": True, "report": report, "dry_run": dry_run}


def run_output_generate_weekly_report(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """生成周末输出报告，汇总各 job 执行结果。"""
    from datetime import datetime as dt_module

    date_str = now_utc()[:10]
    report_path = WEEKEND_OUTPUT_DIR / f"weekend-output-report-{date_str}.md"

    jobs = state.get("jobs", [])

    # 统计各 job 状态
    output_jobs = [j for j in jobs if j.get("stage") == "output"]
    done = sum(1 for j in output_jobs if j.get("status") == "done")
    failed = sum(1 for j in output_jobs if j.get("status") == "failed")
    pending = sum(1 for j in output_jobs if j.get("status") == "pending")
    total = len(output_jobs)

    # 收集各 job 的结果摘要
    summaries = []
    for j in output_jobs:
        jid = j.get("job_id", "?")
        status = j.get("status", "?")
        result = j.get("result", {})
        step = j.get("step", "?")
        error = (j.get("last_error", "") or "")[:100]

        if status == "done":
            if step == "sync":
                synced = result.get("synced_count", 0)
                summaries.append(f"- **{jid}**: ✓ 同步 {synced} 个 proposal 到 KB")
            elif step == "extract":
                if "archived_proposal" in jid:
                    summaries.append(f"- **{jid}**: ✓ 已归档 proposal 萃取完成")
                elif "daily_knowledge" in jid:
                    extracted = result.get("results", {})
                    concepts = len(extracted.get("concepts", []))
                    methods = len(extracted.get("methods", []))
                    people = len(extracted.get("people", []))
                    papers = len(extracted.get("papers", []))
                    unverified = result.get("unverified_count", 0)
                    summaries.append(
                        f"- **{jid}**: ✓ 日常知识萃取 "
                        f"({concepts}概念, {methods}方法, {people}学者, {papers}论文, "
                        f"{unverified}未验证声明)"
                    )
                else:
                    summaries.append(f"- **{jid}**: ✓ 完成")
            elif step == "collect":
                count = result.get("source_count", 0)
                summaries.append(f"- **{jid}**: ✓ 收集 {count} 条来源")
            elif step == "health":
                report = result.get("report", {})
                overdue = report.get("derived_overdue_count", 0)
                health = report.get("health", {})
                total_pages = health.get("total_pages", 0) if isinstance(health, dict) else 0
                summaries.append(
                    f"- **{jid}**: ✓ KB 健康检查 "
                    f"(共 {total_pages} 页, {overdue} 页过期待更新)"
                )
            elif step == "weekly_report":
                summaries.append(f"- **{jid}**: ✓ 周报生成完成")
            else:
                summaries.append(f"- **{jid}**: ✓ 完成")
        elif status == "failed":
            summaries.append(f"- **{jid}**: ✗ 失败 - {error}")
        elif status == "pending":
            summaries.append(f"- **{jid}**: ○ 待执行")
        else:
            summaries.append(f"- **{jid}**: ◐ 进行中")

    # 健康报告摘要
    health_report = load_json(HEALTH_REPORT_PATH, default={})
    health_lines = []
    health = health_report.get("health", {})
    if isinstance(health, dict):
        total_pages = health.get("total_pages", 0)
        by_type = health.get("by_type", {})
        health_lines.append(f"- 知识库共 {total_pages} 页")
        for t, count in sorted(by_type.items()):
            health_lines.append(f"  - {t}: {count} 页")
    overdue = health_report.get("derived_overdue", [])
    if overdue:
        health_lines.append(f"- 超过 30 天未更新的派生知识: {len(overdue)} 条")
        for o in overdue[:5]:
            health_lines.append(f"  - {o.get('title', '?')} ({o.get('days_old', 0)} 天)")

    lines = [
        f"# 周末知识输出报告（{date_str}）",
        "",
        "本报告汇总周末 output 阶段执行结果。",
        "",
        "---",
        "",
        f"## 执行概况",
        f"",
        f"- 总 job: {total}",
        f"- 完成: {done}",
        f"- 失败: {failed}",
        f"- 待执行: {pending}",
        f"",
        "## 任务详情",
        "",
    ]
    lines.extend(summaries)

    lines.extend([
        "",
        "## 知识库健康",
        "",
    ])
    lines.extend(health_lines)

    lines.extend([
        "",
        "---",
        "",
        f"*报告生成时间: {now_utc()}*",
    ])

    if not dry_run:
        report_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "success": True,
        "report_path": str(report_path.relative_to(PROJECT_ROOT)),
        "dry_run": dry_run,
        "summary": {
            "total": total,
            "done": done,
            "failed": failed,
            "pending": pending,
        },
    }
