# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——验收自检（A1-A4 + G1-G2，零 LLM）。

六项判据逐项取证（docs/WORKBENCH-ARCHITECTURE.md §4）：全过 → 自动晋级
ready；不过 → 缺口清单写回课题卡与状态，同缺口补 2 次仍不过 → needs_human
挂起等人裁决。

用法示例：
    python3 scripts/topic_pipeline.py --check general-mos2-hhg-20261116
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from . import state
from .card import append_card_event
from .constants import (
    A1_MIN_RECENT,
    A1_MIN_SOURCES,
    A1_RECENT_MONTHS,
    A2_NOVELTY_THRESHOLD,
    A3_MIN_STEPS,
    GAP_REPAIR_LIMIT,
    G1_REPORT_MAX_CHARS,
    G2_MIN_WIKILINKS,
    STAGES,
)

# 近 24 个月判定：文件名/锚点中的年份 >= 当前年 - 2
import datetime as _dt
_RECENT_YEAR = _dt.date.today().year - 2


def _year_of(name: str) -> int:
    m = re.search(r"(20\d{2})", name or "")
    return int(m.group(1)) if m else 0


def _iter_md(tdir: Path, rel: str) -> List[Path]:
    d = tdir / rel
    if not d.exists():
        return []
    return [p for p in sorted(d.rglob("*.md")) if p.stat().st_size >= 200 and p.name != "topic-card.md"]


def _kb_wikilinks(tdir: Path) -> List[str]:
    """收集课题目录下所有 [[wikilink]]（去重）。"""
    links: set = set()
    for p in tdir.rglob("*.md"):
        try:
            links.update(re.findall(r"\[\[([^\]]+)\]\]", p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return sorted(links)


def check_a1(tdir: Path) -> Dict[str, Any]:
    """A1 背景调研充分：笔记/知识卡 ≥8 篇（近 24 个月 ≥3）+ KB 页 wikilink ≥3。"""
    notes = _iter_md(tdir, "01_background")
    years = []
    for p in notes:
        y = _year_of(p.name)
        if not y:
            # 从笔记内容中的年份锚点兜底
            try:
                y = _year_of(p.read_text(encoding="utf-8")[:2000])
            except Exception:
                y = 0
        years.append(y)
    recent = sum(1 for y in years if y and y >= _RECENT_YEAR)
    kb_links = [l for l in _kb_wikilinks(tdir) if "wiki" in l or "/" not in l]
    passed = len(notes) >= A1_MIN_SOURCES and recent >= A1_MIN_RECENT and len(kb_links) >= 3
    return {
        "code": "A1", "name": "背景调研充分", "passed": passed,
        "evidence": {
            "note_files": len(notes), "recent_count": recent,
            "recent_year_floor": _RECENT_YEAR, "kb_wikilinks": len(kb_links),
        },
        "gaps": [g for g, bad in (
            (f"笔记/知识卡 {len(notes)} < {A1_MIN_SOURCES}", len(notes) < A1_MIN_SOURCES),
            (f"近 24 个月文献 {recent} < {A1_MIN_RECENT}", recent < A1_MIN_RECENT),
        ) if bad],
    }


def check_a2(tdir: Path, topic_id: str, rec: Dict[str, Any]) -> Dict[str, Any]:
    """A2 问题定位清晰：problem.md 存在 + 一句话陈述节 + 新颖性对照非空 + 相似度 <0.50。"""
    prob = tdir / "02_problem" / "problem.md"
    exists = prob.exists() and prob.stat().st_size >= 200
    has_statement = False
    has_novelty = False
    if exists:
        text = prob.read_text(encoding="utf-8")
        has_statement = bool(re.search(r"问题一句话陈述", text))
        has_novelty = bool(re.search(r"新颖性对照|差异点", text))
    nov_score = (rec.get("novelty") or {}).get("max_score", 0.0)
    passed = exists and has_statement and has_novelty and nov_score < A2_NOVELTY_THRESHOLD
    gaps = []
    if not exists:
        gaps.append("02_problem/problem.md 缺失")
    else:
        if not has_statement:
            gaps.append("problem.md 缺「问题一句话陈述」节")
        if not has_novelty:
            gaps.append("problem.md 缺新颖性对照")
    return {
        "code": "A2", "name": "问题定位清晰", "passed": passed,
        "evidence": {"problem_md": exists, "statement": has_statement,
                     "novelty_section": has_novelty, "novelty_score": nov_score},
        "gaps": gaps,
    }


def check_a3(tdir: Path) -> Dict[str, Any]:
    """A3 方案分解明确：scheme.md ≥3 步骤节 + 每步判据 + 首月路线 + 方法素材包。"""
    scheme = tdir / "03_scheme" / "scheme.md"
    exists = scheme.exists() and scheme.stat().st_size >= 200
    steps = 0
    all_have_criteria = False
    has_first_month = False
    if exists:
        text = scheme.read_text(encoding="utf-8")
        step_heads = re.findall(r"^#{1,3}\s*S\d+", text, re.M)
        steps = len(step_heads)
        has_first_month = bool(re.search(r"首月路线", text))
        blocks = re.split(r"^#{1,3}\s*S\d+.*$", text, flags=re.M)[1:]
        all_have_criteria = bool(blocks) and all("判据" in b for b in blocks)
    pack = (tdir / "03_scheme" / "kb-methods-pack.md").exists()
    passed = exists and steps >= A3_MIN_STEPS and all_have_criteria and has_first_month and pack
    gaps = []
    if not exists:
        gaps.append("03_scheme/scheme.md 缺失")
    else:
        if steps < A3_MIN_STEPS:
            gaps.append(f"步骤数 {steps} < {A3_MIN_STEPS}")
        if not all_have_criteria:
            gaps.append("存在缺「判据」的步骤")
        if not has_first_month:
            gaps.append("缺「首月路线」节")
        if not pack:
            gaps.append("03_scheme/kb-methods-pack.md 缺失（方法素材包未挂载）")
    return {
        "code": "A3", "name": "方案分解明确", "passed": passed,
        "evidence": {"scheme_md": exists, "steps": steps,
                     "all_steps_criteria": all_have_criteria,
                     "first_month": has_first_month, "methods_pack": pack},
        "gaps": gaps,
    }


def check_a4(tdir: Path, report_text: str) -> Dict[str, Any]:
    """A4 参考文献真实：bib 非空 + 每条带 source 溯源行 + 报告 [ref:N] 有对应键。"""
    bib = tdir / "04_references" / "references.bib"
    exists = bib.exists()
    n_entries = n_source = 0
    keys: List[str] = []
    if exists:
        text = bib.read_text(encoding="utf-8")
        entries = re.split(r"(?=^@\w+\{)", text, flags=re.M)
        entries = [e for e in entries if e.strip().startswith("@")]
        n_entries = len(entries)
        for e in entries:
            m = re.match(r"@\w+\{([^,]+),", e.strip())
            if m:
                keys.append(m.group(1).strip())
            if re.search(r"^\s*source\s*:", e, re.M):
                n_source += 1
    cited = set(re.findall(r"\[ref:(\w+)\]", report_text)) if report_text else set()
    # 报告引用键须在 bib 中（无引用则不卡）
    dangling = sorted(c for c in cited if c not in keys)
    passed = exists and n_entries > 0 and n_source == n_entries and not dangling
    gaps = []
    if not exists:
        gaps.append("04_references/references.bib 缺失")
    else:
        if n_entries == 0:
            gaps.append("bib 无条目")
        if n_source < n_entries:
            gaps.append(f"{n_entries - n_source} 条 bib 缺 source 溯源行")
        if dangling:
            gaps.append(f"报告引用了 bib 中不存在的键: {','.join(dangling[:5])}")
    return {
        "code": "A4", "name": "参考文献真实", "passed": passed,
        "evidence": {"bib": exists, "entries": n_entries, "with_source": n_source,
                     "cited": len(cited), "dangling": dangling[:5]},
        "gaps": gaps,
    }


def check_g1(report_chars: int) -> Dict[str, Any]:
    passed = report_chars <= G1_REPORT_MAX_CHARS
    return {
        "code": "G1", "name": "篇幅约束", "passed": passed,
        "evidence": {"report_chars": report_chars, "limit": G1_REPORT_MAX_CHARS},
        "gaps": [f"报告 {report_chars} 字符 > {G1_REPORT_MAX_CHARS} 上限"] if not passed else [],
    }


def check_g2(rec: Dict[str, Any], report_text: str) -> Dict[str, Any]:
    """G2 关联明确：related 字段存在（无关联须显式声明）+ 报告 wikilink ≥5。"""
    has_related_field = "related" in (rec or {})
    n_links = len(set(re.findall(r"\[\[([^\]]+)\]\]", report_text or "")))
    passed = has_related_field and n_links >= G2_MIN_WIKILINKS
    gaps = []
    if not has_related_field:
        gaps.append("课题状态缺 related 字段（空关联也须显式声明 []）")
    if n_links < G2_MIN_WIKILINKS:
        gaps.append(f"报告 wikilink {n_links} < {G2_MIN_WIKILINKS}")
    return {
        "code": "G2", "name": "关联明确", "passed": passed,
        "evidence": {"related_field": has_related_field, "wikilinks": n_links},
        "gaps": gaps,
    }


def check_topic(topic_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """对单个课题执行六项验收自检；全过自动晋级 ready。"""
    tdir_path = state.topic_dir(topic_id)
    if tdir_path is None:
        return {"success": False, "error": f"课题不存在或目录缺失: {topic_id}"}
    tdir = Path(tdir_path)
    data = state.load_state()
    rec = state.get_topic(data, topic_id) or {}

    report_path = tdir / "topic-report.md"
    report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    report_chars = len(re.sub(r"\s", "", report_text))

    results = [
        check_a1(tdir),
        check_a2(tdir, topic_id, rec),
        check_a3(tdir),
        check_a4(tdir, report_text),
        check_g1(report_chars),
        check_g2(rec, report_text),
    ]
    failed = [r for r in results if not r["passed"]]
    all_gaps = sorted({g for r in failed for g in r["gaps"]})
    verdict = {
        "topic_id": topic_id,
        "stage": rec.get("stage", ""),
        "passed": not failed,
        "results": results,
        "gaps": all_gaps,
    }

    if dry_run:
        return {"success": True, "dry_run": True, "verdict": verdict}

    # 自检结果落盘
    (tdir / "kickoff-check.json").write_text(
        json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if verdict["passed"]:
        # v8.0.15：过检清零缺口标记对任意阶段生效——ready/active 课题复检全过时
        # 同样清残留（bsv 实例：晋级前已 in ready，旧 check_gaps 长期残留与
        # kickoff-check.json passed=true 矛盾）；目录搬移仍仅 kickoff→ready。
        with state.state_lock():
            data = state.load_state()
            state.upsert_topic(data, topic_id,
                               {"deep_dive_gaps": [], "check_gaps": [], "needs_human": False})
            state.save_state(data)
    if verdict["passed"] and rec.get("stage") in ("kickoff",):
        # v8.0.1：transition 统一入口（状态 + 目录搬移一致；check 文件已落盘随目录走）
        moved = state.transition(topic_id, "ready", "验收自检全过，启动包就绪")
        new_tdir = Path(moved["dir"]) if moved.get("dir") else tdir
        append_card_event(new_tdir / "topic-card.md",
                          f"{state._now()} 验收自检全过 → ready（启动包就绪，待人工启动）")
    elif failed:
        counters = rec.get("gap_repair_counts", {}) or {}
        bumped = dict(counters)
        for g in all_gaps:
            bumped[g] = bumped.get(g, 0) + 1
        needs_human = any(c > GAP_REPAIR_LIMIT for c in bumped.values())
        with state.state_lock():
            data = state.load_state()
            state.upsert_topic(data, topic_id, {
                "gap_repair_counts": bumped,
                "needs_human": needs_human,
                "check_gaps": all_gaps,
            })
            state.save_state(data)
        append_card_event(tdir / "topic-card.md",
                          f"{state._now()} 验收自检 {len(failed)} 项不过"
                          + ("，多次补齐未果 → needs_human（等人裁决）" if needs_human else "（缺口清单已写回）"))
    return {"success": True, "topic_id": topic_id, "verdict": verdict}
