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
from typing import Any, Dict, List, Optional, Tuple

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import load_json, now_utc, save_json, safe_filename
from paths import PROJECT_ROOT
from knowledge_base import save_extracted_knowledge

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


def _item_title(item: Any, key: str = "title") -> str:
    """v6.9.79: LLM 萃取条目标识守卫（缺键/非 dict/空串返回空串，调用方跳过）。

    与 weekend_pipeline/output_jobs.py 同型修复：LLM 返回的条目缺
    title/name 键时裸取 item["title"] 抛 KeyError，本 CLI 路径
    （--daily / --archive）同样触发。守卫后跳过该条目并计数。
    """
    if not isinstance(item, dict):
        return ""
    return str(item.get(key) or "").strip()


# v7.3.85: 人名页噪音过滤（与 weekend_pipeline/output_jobs.py 同型）——
# 11-14/15 周末输出端产出 83 张人名页全部为噪音：裸姓氏（引文列表泵出）、
# 「Ghimire 等人」「Kivshar（研究组）」等组指代、affiliation 填「未在文中提及」
# 的空壳。只挡已观测垃圾形态（裸姓氏/组指代/占位正文），不设正文长度门槛
# （合法短单位如「清华大学」不误杀，v6.9.79 守卫测试夹具回归验证）。
_PERSON_NOISE_BODY_RE = re.compile(
    r"未在文中提及|未提及|未明确|无法确认|不确定|未知|无\s*$|没有\s*$|unknown|not\s*mentioned|^\s*n/?a\s*$",
    re.IGNORECASE,
)


def _is_noise_person(name: str, body: str) -> bool:
    """判定 LLM 萃取的 people 条目是否为噪音（裸姓氏/组指代/空壳）。"""
    n = (name or "").strip()
    if not n:
        return True
    # 1) 裸姓氏：纯拉丁单 token（无空格无分隔点）——引文列表泵出的姓氏，无法消歧
    if re.fullmatch(r"[A-Za-z][A-Za-z\-]*", n):
        return True
    # 2) 组指代/元噪音：X 等人 / X 等 / X 研究组 / X（来源仅以…出现）/ 含 (?)
    if re.search(r"等人|等\s*$|研究组|（[^）]*出现|\(\?\)", n):
        return True
    # 3) 空壳 body：空或「未在文中提及」类占位
    b = (body or "").strip()
    if not b or _PERSON_NOISE_BODY_RE.search(b):
        return True
    return False


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
    """写入 wiki 页面，带 frontmatter 标记来源与可靠性。

    委托给 knowledge_base.save_extracted_knowledge() 门面处理，
    自动构建 frontmatter、注入双向链接、更新图谱、记录生长日志。
    """
    _ensure_dirs()

    # 读取现有内容，追加而非覆盖
    path = _build_wiki_path(kind, title)
    existing = _read_text(path)
    if existing:
        existing_fm, existing_body = _extract_frontmatter(existing)
        body = existing_body + "\n\n---\n\n" + body
        # v6.9.79: sources 读侧归一（与 weekend_pipeline/output_jobs.py 同型）——
        # 朴素 frontmatter 行解析下 list 形态解析为空串，裸拼 str + list 抛 TypeError
        existing_sources = existing_fm.get("sources")
        if isinstance(existing_sources, list):
            pass
        elif isinstance(existing_sources, str) and existing_sources.strip():
            existing_sources = [existing_sources]
        else:
            existing_sources = []
        sources = existing_sources + list(sources)

    rel_path = save_extracted_knowledge(title, kind, body, sources, reliability)

    return {"success": True, "path": rel_path, "reliability": reliability}


# ---------------------------------------------------------------------------
# 1. 归档 proposal 知识萃取
# ---------------------------------------------------------------------------


def extract_from_archived_proposal(proposal_id: str, prop_dir: Path, dry_run: bool = False) -> Dict[str, Any]:
    """从已归档 proposal 中萃取可靠知识。"""
    proposal_text = _read_text(prop_dir / "04_proposal" / "proposal-draft.md", 8000)
    if not proposal_text:
        return {"success": False, "error": "申请书为空"}

    if dry_run:
        return {"success": True, "dry_run": True, "message": "dry-run 跳过归档知识萃取"}

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

    ok, text, meta = llm_complete(system_prompt, user_prompt, timeout=120, prefer="governance")
    if not ok:
        return {"success": False, "error": meta.get("error", "LLM 调用失败")}

    # v7.3.57: 共享容错提取器（llm_json_lib）统一收敛——围栏/平衡扫描/
    # CJK 内引号修复链，取代此前仅围栏正则无降级通道的实现
    from llm_json_lib import extract_json
    extracted, reason = extract_json(text)
    if extracted is None:
        return {"success": False, "error": f"解析失败: {reason}", "raw": text[:500]}

    results = {"concepts": [], "methods": [], "people": [], "papers": []}
    source_meta = {"title": proposal_id, "source_type": "archived_proposal"}
    skipped_invalid = 0

    for c in extracted.get("concepts", []):
        title = _item_title(c)
        if not title:
            skipped_invalid += 1
            continue
        r = _write_wiki_page("concept", title, c.get("summary", ""), [source_meta], RELIABILITY_RELIABLE)
        results["concepts"].append(r)
    for m in extracted.get("methods", []):
        title = _item_title(m)
        if not title:
            skipped_invalid += 1
            continue
        r = _write_wiki_page("method", title, m.get("summary", ""), [source_meta], RELIABILITY_RELIABLE)
        results["methods"].append(r)
    for p in extracted.get("people", []):
        name = _item_title(p, "name")
        if not name:
            skipped_invalid += 1
            continue
        # v7.3.85: 人名噪音过滤（裸姓氏/组指代/空壳不建页）
        affiliation = p.get("affiliation", "")
        if _is_noise_person(name, affiliation):
            skipped_invalid += 1
            continue
        r = _write_wiki_page("person", name, affiliation, [source_meta], RELIABILITY_RELIABLE)
        results["people"].append(r)
    for p in extracted.get("papers", []):
        title = _item_title(p)
        if not title:
            skipped_invalid += 1
            continue
        r = _write_wiki_page("paper", title, p.get("authors", ""), [source_meta], RELIABILITY_RELIABLE)
        results["papers"].append(r)

    _log_info(f"归档课题 {proposal_id} 萃取完成: concepts={len(results['concepts'])}, methods={len(results['methods'])}, skipped_invalid={skipped_invalid}")
    return {"success": True, "results": results, "skipped_invalid": skipped_invalid}


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

    if dry_run:
        return {"success": True, "dry_run": True, "message": "dry-run 跳过日常知识萃取"}

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

    ok, text, meta = llm_complete(system_prompt, user_prompt, timeout=150, prefer="governance")
    if not ok:
        return {"success": False, "error": meta.get("error", "LLM 调用失败")}

    # v7.3.57: 共享容错提取器（llm_json_lib）统一收敛——围栏/平衡扫描/
    # CJK 内引号修复链，取代此前仅围栏正则无降级通道的实现
    from llm_json_lib import extract_json
    extracted, reason = extract_json(text)
    if extracted is None:
        return {"success": False, "error": f"解析失败: {reason}", "raw": text[:500]}

    results = {"concepts": [], "methods": [], "people": [], "papers": []}
    skipped_invalid = 0

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
        title = _item_title(c)
        if not title:
            skipped_invalid += 1
            continue
        src = _source_meta_from_path(c.get("source_path", ""))
        r = _write_wiki_page("concept", title, c.get("summary", ""), [src], RELIABILITY_RELIABLE)
        results["concepts"].append(r)
    for m in extracted.get("methods", []):
        title = _item_title(m)
        if not title:
            skipped_invalid += 1
            continue
        src = _source_meta_from_path(m.get("source_path", ""))
        r = _write_wiki_page("method", title, m.get("summary", ""), [src], RELIABILITY_RELIABLE)
        results["methods"].append(r)
    for p in extracted.get("people", []):
        name = _item_title(p, "name")
        if not name:
            skipped_invalid += 1
            continue
        src = _source_meta_from_path(p.get("source_path", ""))
        # v7.3.85: 人名噪音过滤（裸姓氏/组指代/空壳不建页）
        affiliation = p.get("affiliation", "")
        if _is_noise_person(name, affiliation):
            skipped_invalid += 1
            continue
        r = _write_wiki_page("person", name, affiliation, [src], RELIABILITY_RELIABLE)
        results["people"].append(r)
    for p in extracted.get("papers", []):
        title = _item_title(p)
        if not title:
            skipped_invalid += 1
            continue
        src = _source_meta_from_path(p.get("source_path", ""))
        r = _write_wiki_page("paper", title, p.get("authors", ""), [src], RELIABILITY_RELIABLE)
        results["papers"].append(r)

    # 保存 unverified claims
    unverified = extracted.get("unverified_claims", [])
    if unverified:
        existing = load_json(UNVERIFIED_CLAIMS_PATH, default={"claims": []})
        for u in unverified:
            u["recorded_at"] = now_utc()
            existing["claims"].append(u)
        save_json(UNVERIFIED_CLAIMS_PATH, existing)

    _log_info(f"日常知识萃取完成: concepts={len(results['concepts'])}, methods={len(results['methods'])}, unverified={len(unverified)}, skipped_invalid={skipped_invalid}")
    return {"success": True, "results": results, "unverified_count": len(unverified), "skipped_invalid": skipped_invalid}


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
