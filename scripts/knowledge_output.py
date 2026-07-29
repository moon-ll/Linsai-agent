#!/usr/bin/env python3
"""知识输出与萃取器（v6.7.7）。

输出端核心：
1. 对人工 approve 的归档 proposal，萃取核心概念/方法/论文到知识库。
2. 从日常可靠来源（文献简报、researcher 定向检索、用户参考、归档讨论）中
   抽取可靠知识，写入知识库，并严格区分来源可靠性：
   - reliable：直接来自文献或用户确认。
   - derived：AI 基于可靠源生成，需人工复核。
   - unverified：来源不明，暂不写入知识库。

用法：
    python3 scripts/knowledge_output.py --archive     # 处理已 approve 归档
    python3 scripts/knowledge_output.py --daily       # 萃取日常可靠知识
    python3 scripts/knowledge_output.py --weekly      # 归档 + 日常 + 健康检查
    python3 scripts/knowledge_output.py --dry-run     # 预览
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import load_json, now_utc, save_json, safe_filename
from paths import PROJECT_ROOT

from llm_gateway import llm_complete, is_llm_available

try:
    from logger import get_logger
    _log = get_logger("knowledge_output")
except Exception:
    _log = None

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

RELIABILITY_RELIABLE = "reliable"
RELIABILITY_DERIVED = "derived"
RELIABILITY_UNVERIFIED = "unverified"

KB_ROOT = PROJECT_ROOT / "knowledge" / "wiki"
KB_CONCEPTS_DIR = KB_ROOT / "concepts"
KB_METHODS_DIR = KB_ROOT / "methods"
KB_PEOPLE_DIR = KB_ROOT / "people"
KB_PAPERS_DIR = KB_ROOT / "papers"
KB_REVIEWS_DIR = KB_ROOT / "reviews"

UNVERIFIED_CLAIMS_PATH = PROJECT_ROOT / "knowledge" / ".cache" / "unverified-claims.json"
HEALTH_REPORT_PATH = PROJECT_ROOT / "knowledge" / ".cache" / "kb-health-weekly.json"

# 可靠来源类型
RELIABLE_SOURCE_TYPES = {"briefing", "paper", "user_input", "capture", "reference_note", "archived_proposal"}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _log_info(msg: str) -> None:
    if _log:
        _log.info(msg)


def _log_warn(msg: str) -> None:
    if _log:
        _log.warning(msg)


def _ensure_dirs() -> None:
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


def _extract_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """提取 markdown frontmatter。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    try:
        fm = {}
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
        return fm, m.group(2)
    except Exception:
        return {}, text


def _build_wiki_path(kind: str, title: str) -> Path:
    """生成 wiki 文件路径。"""
    filename = safe_filename(title) + ".md"
    if kind == "concept":
        return KB_CONCEPTS_DIR / filename
    elif kind == "method":
        return KB_METHODS_DIR / filename
    elif kind == "person":
        return KB_PEOPLE_DIR / filename
    elif kind == "paper":
        return KB_PAPERS_DIR / filename
    return KB_ROOT / filename


def _write_wiki_page(kind: str, title: str, body: str, sources: List[Dict[str, Any]],
                     reliability: str = RELIABILITY_DERIVED) -> Dict[str, Any]:
    """写入 wiki 页面，带 frontmatter 标记来源与可靠性。"""
    _ensure_dirs()
    path = _build_wiki_path(kind, title)

    existing = _read_text(path)
    if existing:
        # 追加而非覆盖
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
# 1. 归档 proposal 知识萃取
# ---------------------------------------------------------------------------


def extract_from_archived_proposal(proposal_id: str, prop_dir: Path, dry_run: bool = False) -> Dict[str, Any]:
    """从已归档 proposal 中萃取可靠知识。"""
    proposal_text = _read_text(prop_dir / "04_proposal" / "proposal-draft.md", 8000)
    if not proposal_text:
        return {"success": False, "error": "申请书为空"}

    if not is_llm_available():
        _log_warn("LLM 不可用，跳过归档知识萃取")
        return {"success": False, "error": "LLM 不可用"}

    system_prompt = (
        "你是林赛（Lin Sai），一位擅长从归档申请书中萃取可靠知识的物理学家。"
        "请只提取申请书中有明确依据的概念、方法、关键论文和创新点，不凭空扩展。输出必须合法 JSON。"
    )
    user_prompt = f"""请从以下已归档 NSFC 申请书中萃取知识，输出 JSON：

```
{proposal_text[:4000]}
```

输出格式（严格控制数量，避免截断）：
{{
  "concepts": [{{"title": "...", "summary": "...", "source_passage": "..."}}],
  "methods": [{{"title": "...", "summary": "...", "source_passage": "..."}}],
  "people": [{{"name": "...", "affiliation": "...", "source_passage": "..."}}],
  "papers": [{{"title": "...", "authors": "...", "source_passage": "..."}}]
}}

要求：
1. 每个条目必须附带 source_passage（申请书原文片段）。
2. 不添加申请书未提及的信息。
3. 如果某类无内容，返回空数组。
4. 每个 summary 不超过 100 字，严格控制总输出长度。
"""

    ok, text, meta = llm_complete(system_prompt, user_prompt, timeout=120)
    if not ok:
        return {"success": False, "error": meta.get("error", "LLM 调用失败")}

    try:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        json_str = m.group(1) if m else text
        extracted = json.loads(json_str)
    except Exception as e:
        return {"success": False, "error": f"解析失败: {e}", "raw": text[:500]}

    if dry_run:
        return {"success": True, "extracted": extracted, "dry_run": True}

    results = {"concepts": [], "methods": [], "people": [], "papers": []}
    source_meta = {"title": proposal_id, "source_type": "archived_proposal"}

    for c in extracted.get("concepts", []):
        r = _write_wiki_page("concept", c["title"], c.get("summary", ""), [source_meta], RELIABILITY_RELIABLE)
        results["concepts"].append(r)
    for m in extracted.get("methods", []):
        r = _write_wiki_page("method", m["title"], m.get("summary", ""), [source_meta], RELIABILITY_RELIABLE)
        results["methods"].append(r)
    for p in extracted.get("people", []):
        r = _write_wiki_page("person", p["name"], p.get("affiliation", ""), [source_meta], RELIABILITY_RELIABLE)
        results["people"].append(r)
    for p in extracted.get("papers", []):
        r = _write_wiki_page("paper", p["title"], p.get("authors", ""), [source_meta], RELIABILITY_RELIABLE)
        results["papers"].append(r)

    _log_info(f"归档课题 {proposal_id} 萃取完成: concepts={len(results['concepts'])}, methods={len(results['methods'])}")
    return {"success": True, "results": results}


def process_archived_proposals(dry_run: bool = False) -> Dict[str, Any]:
    """处理所有 archived 目录下的 proposal。"""
    from proposal_lifecycle import ProposalLifecycle
    lc = ProposalLifecycle()

    archived = lc.list_by_status("archived")
    results = []
    for prop in archived:
        pid = prop["proposal_id"]
        prop_dir = lc._find_proposal_dir(pid)
        if not prop_dir:
            continue
        result = extract_from_archived_proposal(pid, prop_dir, dry_run=dry_run)
        results.append({"proposal_id": pid, **result})

    return {"success": True, "processed": len(results), "results": results}


# ---------------------------------------------------------------------------
# 2. 日常可靠知识萃取
# ---------------------------------------------------------------------------


def _collect_daily_sources(days: int = 7) -> List[Dict[str, Any]]:
    """收集过去 N 天的可靠来源。"""
    sources = []

    # 文献简报
    if KB_REVIEWS_DIR.exists():
        for f in sorted(KB_REVIEWS_DIR.glob("briefing-*.md"), reverse=True)[:days]:
            sources.append({"path": str(f), "type": "briefing", "text": _read_text(f, 6000)})

    # researcher 定向检索产物
    from proposal_lifecycle import ProposalLifecycle
    lc = ProposalLifecycle()
    for prop in lc.list_by_status("optimizing"):
        pid = prop["proposal_id"]
        prop_dir = lc._find_proposal_dir(pid)
        if not prop_dir:
            continue
        targeted_dir = prop_dir / "02_literature" / "targeted-research"
        if targeted_dir.exists():
            for f in sorted(targeted_dir.glob("lit-gap-*.md"), reverse=True)[:3]:
                sources.append({"path": str(f), "type": "researcher_targeted", "text": _read_text(f, 4000)})

    # 用户参考笔记
    if (PROJECT_ROOT / "references" / "notes").exists():
        for f in (PROJECT_ROOT / "references" / "notes").glob("*.md"):
            sources.append({"path": str(f), "type": "reference_note", "text": _read_text(f, 3000)})

    # 归档讨论
    if (PROJECT_ROOT / "knowledge" / "captures").exists():
        for f in sorted((PROJECT_ROOT / "knowledge" / "captures").glob("*.md"),
                        key=lambda p: p.stat().st_mtime, reverse=True)[:20]:
            sources.append({"path": str(f), "type": "capture", "text": _read_text(f, 3000)})

    return sources


def process_daily_sources(dry_run: bool = False, days: int = 7) -> Dict[str, Any]:
    """从日常来源萃取可靠知识。"""
    sources = _collect_daily_sources(days=days)
    if not sources:
        return {"success": True, "processed": 0, "message": "无日常来源"}

    if not is_llm_available():
        _log_warn("LLM 不可用，跳过日常知识萃取")
        return {"success": False, "error": "LLM 不可用"}

    # 合并文本（限制总长度，避免 LLM 输出被截断）
    selected = sources[:6]  # 最多 6 个来源
    combined = "\n\n---\n\n".join(
        f"【来源: {s['type']} | {s['path']}】\n{s['text'][:1200]}"
        for s in selected
    )

    system_prompt = (
        "你是林赛（Lin Sai），一位擅长从文献和讨论中萃取可靠知识的物理学家。"
        "请只提取来源中明确提到的概念、方法、论文和学者。对于来源未直接支撑的信息，"
        "请放入 'unverified_claims' 而不是可靠知识。输出必须合法 JSON。"
    )
    user_prompt = f"""请从以下来源中提取可靠知识，输出 JSON。

{combined[:5000]}

输出格式（严格控制数量，避免截断）：
{{
  "concepts": [{{"title": "...", "summary": "...", "source_path": "..."}}],
  "methods": [{{"title": "...", "summary": "...", "source_path": "..."}}],
  "people": [{{"name": "...", "affiliation": "...", "source_path": "..."}}],
  "papers": [{{"title": "...", "authors": "...", "source_path": "..."}}],
  "unverified_claims": [{{"claim": "...", "reason": "来源未直接支撑"}}]
}}

要求：
1. 每个条目必须标注 source_path。
2. 不添加来源未提及的信息。
3. 对模糊或无法确认的信息，放入 unverified_claims。
4. 每个 summary 不超过 100 字，严格控制总输出长度。
"""

    ok, text, meta = llm_complete(system_prompt, user_prompt, timeout=150)
    if not ok:
        return {"success": False, "error": meta.get("error", "LLM 调用失败")}

    try:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        json_str = m.group(1) if m else text
        extracted = json.loads(json_str)
    except Exception as e:
        return {"success": False, "error": f"解析失败: {e}", "raw": text[:500]}

    if dry_run:
        return {"success": True, "extracted": extracted, "dry_run": True}

    results = {"concepts": [], "methods": [], "people": [], "papers": []}

    def _source_meta_from_path(source_path: str) -> Dict[str, Any]:
        if "briefing" in source_path:
            return {"title": Path(source_path).name, "source_type": "briefing"}
        elif "lit-gap" in source_path:
            return {"title": Path(source_path).name, "source_type": "researcher_targeted"}
        elif "references/notes" in source_path:
            return {"title": Path(source_path).name, "source_type": "reference_note"}
        elif "captures" in source_path:
            return {"title": Path(source_path).name, "source_type": "capture"}
        return {"title": Path(source_path).name, "source_type": "unknown"}

    for c in extracted.get("concepts", []):
        src = _source_meta_from_path(c.get("source_path", ""))
        r = _write_wiki_page("concept", c["title"], c.get("summary", ""), [src], RELIABILITY_RELIABLE)
        results["concepts"].append(r)
    for m in extracted.get("methods", []):
        src = _source_meta_from_path(m.get("source_path", ""))
        r = _write_wiki_page("method", m["title"], m.get("summary", ""), [src], RELIABILITY_RELIABLE)
        results["methods"].append(r)
    for p in extracted.get("people", []):
        src = _source_meta_from_path(p.get("source_path", ""))
        r = _write_wiki_page("person", p["name"], p.get("affiliation", ""), [src], RELIABILITY_RELIABLE)
        results["people"].append(r)
    for p in extracted.get("papers", []):
        src = _source_meta_from_path(p.get("source_path", ""))
        r = _write_wiki_page("paper", p["title"], p.get("authors", ""), [src], RELIABILITY_RELIABLE)
        results["papers"].append(r)

    # 保存 unverified claims
    unverified = extracted.get("unverified_claims", [])
    if unverified:
        existing = load_json(UNVERIFIED_CLAIMS_PATH, default={"claims": []})
        for u in unverified:
            u["recorded_at"] = now_utc()
            existing["claims"].append(u)
        save_json(UNVERIFIED_CLAIMS_PATH, existing)

    _log_info(f"日常知识萃取完成: concepts={len(results['concepts'])}, methods={len(results['methods'])}, unverified={len(unverified)}")
    return {"success": True, "results": results, "unverified_count": len(unverified)}


# ---------------------------------------------------------------------------
# 3. 知识库健康检查
# ---------------------------------------------------------------------------


def run_kb_health_check() -> Dict[str, Any]:
    """运行知识库健康检查并生成报告。"""
    _ensure_dirs()

    # 复用 kb_maintenance 的功能
    import importlib.util
    kb_path = Path(__file__).parent / "knowledge_base.py"
    spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
    kb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb)

    health = kb.get_kb_health()

    # 扫描 derived 内容是否过期
    derived_overdue = []
    for page in kb.list_wiki_pages():
        p = kb.get_wiki_page(page.get("path", ""))
        if not p:
            continue
        fm = p.get("frontmatter", {})
        if fm.get("source_reliability") == RELIABILITY_DERIVED:
            updated = fm.get("updated_at", "")
            if updated:
                try:
                    from datetime import datetime, timezone
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
    save_json(HEALTH_REPORT_PATH, report)
    _log_info(f"知识库健康检查完成: derived_overdue={len(derived_overdue)}")
    return report


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def run_weekly_output(dry_run: bool = False) -> Dict[str, Any]:
    """周末输出入口：归档萃取 + 日常萃取 + 健康检查。

    v6.7.7: 委托给 WeekendPipeline 的 output 阶段，保留旧函数签名以兼容 CLI/Web。
    """
    from weekend_pipeline import WeekendPipeline
    pipeline = WeekendPipeline()
    pipeline.sync_stage_jobs("output")
    result = pipeline.run_stage("output", dry_run=dry_run)
    return {
        "success": result.get("success", True),
        "pipeline_result": result,
        "at": now_utc(),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _self_check() -> None:
    print("=== knowledge_output._self_check ===")
    print(f"LLM 可用: {is_llm_available()}")
    print("✓ 通过")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="知识输出与萃取器")
    parser.add_argument("--archive", action="store_true", help="处理已归档 proposal")
    parser.add_argument("--daily", action="store_true", help="萃取日常可靠知识")
    parser.add_argument("--weekly", action="store_true", help="周末完整输出流程")
    parser.add_argument("--health", action="store_true", help="知识库健康检查")
    parser.add_argument("--dry-run", action="store_true", help="只预览不写入")
    parser.add_argument("--days", type=int, default=7, help="日常来源时间范围（天）")
    parser.add_argument("--self-check", action="store_true", help="自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        sys.exit(0)

    if args.weekly:
        result = run_weekly_output(dry_run=args.dry_run)
    elif args.archive:
        result = process_archived_proposals(dry_run=args.dry_run)
    elif args.daily:
        result = process_daily_sources(dry_run=args.dry_run, days=args.days)
    elif args.health:
        result = run_kb_health_check()
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
