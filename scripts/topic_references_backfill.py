# -*- coding: utf-8 -*-
"""topic_references_backfill — v8 启动包 references.bib 批量生成（零 LLM）。

背景（worklist-and-prompt 任务 4，2026-11-18）：v7 迁移启动包的 04_references/
只有 bib-candidates-*.bib 与 references-source.md，没有 references.bib，A4 直接
判 0 条。本脚本按「合并 candidates → DOI/arXiv/归一化标题去重 → 补 source 溯源
行 → 生成规范 references.bib」流水线批量补齐。

红线（执行清单原话）：
    - 不得为凑条数编造条目。candidates 里缺 source 的标 needs_review 而不是
      补一个假的。
    - references-source.md 为编号权威（正文 [N] 引用该编号），生成条目与
      [N] 一一对应（键名内嵌编号 ref<N>）。

诚实性设计（针对 v7 遗留列表的格式异构——逗号题名/无 DOI: 前缀/markdown 斜体/
缺题名等）：
    - 标题只在可靠可得时写入 title 字段：① 引号内原文；② 候选条目按
      DOI/arXiv 匹配命中。其余**不写 title 字段**，完整编号行原文进 note
      （零信息损失、零编造）。
    - 身份字段（doi/eprint）以编号行原文为准；候选仅补 author/journal/year。
    - 无 DOI 且无 arXiv 的条目标 needs_review（不剔除、不编造）。
    - 无任何资料域（编号表空且无 candidates）→ 跳过并记 needs_review。

用法示例：
    python3 scripts/topic_references_backfill.py --plan            # 预览全部（不写盘）
    python3 scripts/topic_references_backfill.py --apply           # 生成（跳过已有 bib）
    python3 scripts/topic_references_backfill.py --topic <tid> --apply --force
    python3 scripts/topic_references_backfill.py --self-check      # 零依赖自检
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc, save_json  # noqa: E402

TOPICS_ROOT = PROJECT_ROOT / "research_topics"
AUDIT_PATH = PROJECT_ROOT / "research_topics" / "_audit" / "references-backfill.json"

_STAGES = ("questions", "kickoff", "ready")

_DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s;，；]+)")
_ARXIV_RE = re.compile(r"arXiv[:：]\s*([a-z\-]+/\d{7}|\d{4}\.\d{4,5})(v\d+)?", re.I)


# --------------------------------------------------------------- 基础解析
def _norm_title(s: str) -> str:
    """归一化标题：去重音/markdown 记号/下标差异，仅留字母数字。"""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[*_`]", "", s)
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _surname_of(seg: str) -> str:
    """第一作者姓氏：兼容「Surname L」（中文数字风格，姓在前）与
    「L. Surname」（西文风格，名在前）两种排版。"""
    first = re.split(r",|\band\b|；", seg or "", 1)[0].strip()
    first = re.sub(r"\b(et al\.?|等)\s*$", "", first).strip().rstrip(".")
    toks = first.replace("*", "").split()
    if not toks:
        return ""
    if len(toks) == 2 and len(toks[1]) <= 2 and toks[1].isalpha() and toks[1] == toks[1]:
        return toks[0]  # 「Šmejkal L」→ Šmejkal
    return toks[-1]  # 「D. J. Thouless」→ Thouless


def _ascii_fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^A-Za-z]", "", s)


def _title_from_body(body: str) -> str:
    """标题提取：① 引号内原文（可靠）；② 边界启发（作者块首边界 → 年份/期刊尾前
    末边界），产物须通过标题校验（长度/含空格/不含年份卷期/不含作者缩写模式），
    不可靠一律返回空串走 note 兜底（宁缺毋错，不编造）。"""
    q = re.search(r"[“\"']([^“”\"']{15,})[”\"']", body)
    if q:
        return q.group(1).strip().rstrip(",")
    t = re.split(r"DOI[:：]", body, 1, flags=re.I)[0]
    t = re.split(r"arXiv[:：]", t, 1, flags=re.I)[0]
    t = re.sub(r"\b10\.\d{4,9}/\S+$", "", t).strip().rstrip(". ")
    if not t:
        return ""
    all_cuts = [m.end() for m in re.finditer(r"(?<=\.)\s", t)]
    if not all_cuts:
        return ""
    year = _year_from_body(t)
    year_pos = t.rfind(year) if year else len(t)
    if year_pos <= 0:
        year_pos = len(t)
    before_year = [c for c in all_cuts if c < year_pos]
    if not before_year:
        return ""
    cand = t[all_cuts[0]:before_year[-1]].strip().rstrip(".")
    ok = (len(cand) >= 15 and " " in cand
          and not re.search(r"(?:19|20)\d{2}", cand)
          and not re.search(r"\d{1,3}\s*:\s*\d{1,4}", cand)
          and not re.search(r"(?:^|[\s,])[A-Z]\.(?:[\s,]|$)", cand))
    return cand if ok else ""


def _year_from_body(body: str) -> str:
    """年份：优先括号内 19/20 开头 4 位；否则取行内最后一个该形式年份。"""
    m = re.search(r"\((19|20)\d{2}\)", body)
    if m:
        return m.group(0)[1:-1]
    years = re.findall(r"(?:19|20)\d{2}", body)
    return years[-1] if years else ""


def _parse_source_list(text: str) -> List[Dict[str, Any]]:
    """解析 references-source.md 编号条目 [N] 正文。"""
    out: List[Dict[str, Any]] = []
    for m in re.finditer(r"^\[(\d{1,3})\]\s*(.+)$", text, re.M):
        n = int(m.group(1))
        body = m.group(2).strip()
        doi_m = _DOI_RE.search(body)
        doi = doi_m.group(1).rstrip(".,;）") if doi_m else ""
        arx_m = _ARXIV_RE.search(body)
        arxiv = (arx_m.group(1) + (arx_m.group(2) or "")) if arx_m else ""
        first_seg = re.split(r"[,，]", body, 1)[0]
        out.append({"n": n, "body": body, "doi": doi, "arxiv": arxiv,
                    "title": _title_from_body(body),
                    "surname": _surname_of(first_seg),
                    "year": _year_from_body(body)})
    return out


def _parse_candidates(path: Path) -> List[Dict[str, Any]]:
    """解析单个 bib-candidates 文件的 @ 条目。"""
    text = path.read_text(encoding="utf-8")
    out: List[Dict[str, Any]] = []
    for chunk in re.split(r"(?=^@\w+\{)", text, flags=re.M):
        chunk = chunk.strip()
        if not chunk.startswith("@"):
            continue
        key_m = re.match(r"@\w+\{([^,]+),", chunk)
        rec: Dict[str, Any] = {"key": key_m.group(1).strip() if key_m else "",
                               "file": path.name}
        f = lambda name: (re.search(rf"^\s*{name}\s*=\s*[{{\"']?(.+?)[}}\"']?,?\s*$",
                                    chunk, re.M | re.I) or [None, ""])[1].strip()
        rec["title"] = re.sub(r"[{}]", "", f("title"))
        rec["author"] = re.sub(r"[{}]", "", f("author"))
        rec["journal"] = re.sub(r"[{}]", "", f("journal"))
        rec["year"] = f("year")
        rec["doi"] = f("doi").rstrip(".,;") or (_DOI_RE.search(f("doi")) or [None, ""])[1]
        url = f("url")
        arx_m = re.search(r"arxiv\.org/(?:abs|pdf)/([a-z\-]+/\d{7}|\d{4}\.\d{4,5})", url, re.I)
        rec["arxiv"] = arx_m.group(1) if arx_m else ""
        out.append(rec)
    return out


def _match_candidate(entry: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """按 DOI → arXiv → 归一化标题 匹配候选条目（身份字段以编号行为准）。"""
    for key_field in ("doi", "arxiv"):
        v = (entry.get(key_field) or "").lower().rstrip(".")
        if v:
            for c in candidates:
                if (c.get(key_field) or "").lower().rstrip(".") == v:
                    return c
    t = _norm_title(entry.get("title") or "")
    if t and len(t) >= 20:
        for c in candidates:
            if _norm_title(c.get("title") or "") == t:
                return c
    return None


# --------------------------------------------------------------- 渲染
def _render_entry(key: str, fields: List[str], source_line: str,
                  notes: List[str]) -> str:
    """渲染单条 bib：字段逗号分隔；source 溯源行末置（A4 硬门格式）。"""
    if notes:
        fields.append("  note = {" + "; ".join(notes) + "}")
    body = "@article{" + key + ",\n" + ",\n".join(fields) + ",\n  source: " + source_line + "\n}\n"
    return body


def _bib_entry(entry: Dict[str, Any], cand: Optional[Dict[str, Any]]) -> str:
    """编号模式单条：title 可靠才写；候选补 author/journal；原文兜底进 note。"""
    surname = _ascii_fold(_surname_of((cand or {}).get("author", "")) if cand and cand.get("author")
                          else entry["surname"]) or "ref"
    year = (cand or {}).get("year") or entry["year"] or "n.d."
    key = f"{surname}{year}ref{entry['n']}"
    title = (cand or {}).get("title") or entry["title"]
    doi = entry["doi"] or (cand or {}).get("doi", "")
    arxiv = entry["arxiv"] or (cand or {}).get("arxiv", "")
    fields: List[str] = []
    if title:
        fields.append(f"  title = {{{title}}}")
    if cand and cand.get("author"):
        fields.append(f"  author = {{{cand['author']}}}")
    elif entry["surname"]:
        fields.append(f"  author = {{{entry['surname']} et al.}}")
    if cand and cand.get("journal"):
        fields.append(f"  journal = {{{cand['journal']}}}")
    fields.append(f"  year = {{{year}}}")
    if doi:
        fields.append(f"  doi = {{{doi}}}")
    if arxiv:
        fields.append(f"  eprint = {{{arxiv}}}")
    notes: List[str] = []
    if not doi and not arxiv:
        notes.append("needs_review: 无 DOI/arXiv 溯源字段，待核验（不编造）")
    if not title:
        notes.append("needs_review: 编号行无法可靠解析标题，完整原文如下（不编造）")
    # 编号行原文恒入 note：卷期页/期刊等未结构化信息零损失（诚实溯源）
    notes.append(f"编号行原文: {entry['body']}")
    src = f"references-source.md [{entry['n']}]"
    if cand:
        src += f"; {cand['file']}({cand['key']})"
    return _render_entry(key, fields, src, notes)


def _dedupe_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """候选自身去重（DOI/arXiv/归一化标题；无任何标识者不去重、逐条保留）。"""
    seen: set = set()
    out: List[Dict[str, Any]] = []
    for c in candidates:
        ident = (c.get("doi", "").lower().rstrip("."), c.get("arxiv", "").lower(),
                 _norm_title(c.get("title", "")))
        if ident == ("", "", ""):
            out.append(c)
            continue
        if ident in seen:
            continue
        seen.add(ident)
        out.append(c)
    return out


def build_candidates_bib(candidates: List[Dict[str, Any]], topic_id: str) -> Dict[str, Any]:
    """无编号基准（references-source.md 空但 candidates 存在）：以候选条目自建制。

    键沿用候选原键（溯源到文件）；身份字段全部来自候选记录，不编造。
    """
    parts = [
        f"% references.bib（v8 批量回填·candidates-only）——课题: {topic_id}",
        f"% 生成: {now_utc()} by scripts/topic_references_backfill.py（零 LLM 机械合并）",
        "% 说明: references-source.md 无编号条目，本文件由 bib-candidates 去重生成；",
        "% 每条末行 source 溯源到候选文件；needs_review = 溯源字段缺失待核验，未编造。",
        "",
    ]
    keys: List[str] = []
    for c in _dedupe_candidates(candidates):
        doi, arxiv = c.get("doi", ""), c.get("arxiv", "")
        fields = []
        if c.get("title"):
            fields.append(f"  title = {{{c['title']}}}")
        if c.get("author"):
            fields.append(f"  author = {{{c['author']}}}")
        if c.get("journal"):
            fields.append(f"  journal = {{{c['journal']}}}")
        if c.get("year"):
            fields.append(f"  year = {{{c['year']}}}")
        if doi:
            fields.append(f"  doi = {{{doi}}}")
        if arxiv:
            fields.append(f"  eprint = {{{arxiv}}}")
        notes = []
        if not doi and not arxiv:
            notes.append("needs_review: 无 DOI/arXiv 溯源字段，待核验（不编造）")
        key = c.get("key") or "refentry"
        keys.append(key)
        parts.append(_render_entry(key, fields, f"{c['file']}({key})", notes))
    text = "\n".join(parts)
    return {"text": text, "n_entries": len(keys),
            "n_matched": 0, "n_unmatched": 0,
            "n_review": len(re.findall(r"needs_review:", text)),
            "keys": sorted(set(keys))}


def build_bib_text(entries: List[Dict[str, Any]], candidates: List[Dict[str, Any]],
                   topic_id: str) -> Dict[str, Any]:
    """合并生成 references.bib 全文与审计统计（编号模式）。"""
    used_keys: set = set()
    parts = [
        f"% references.bib（v8 批量回填）——课题: {topic_id}",
        f"% 生成: {now_utc()} by scripts/topic_references_backfill.py（零 LLM 机械合并）",
        "% 条目集合 = references-source.md 编号条目（正文 [N] 引用基准），键名内嵌编号 ref<N>；",
        "% candidates 按 DOI/arXiv/归一化标题匹配补充元数据，身份字段以编号行为准；",
        "% note 保留编号行原文（格式异构年份卷期等零信息损失）；每条末行 source: 溯源（A4 硬门）。",
        "% needs_review = 溯源字段缺失待核验，未编造。",
        "",
    ]
    n_matched = n_unmatched = 0
    for e in entries:
        cand = _match_candidate(e, candidates)
        if cand:
            n_matched += 1
        else:
            n_unmatched += 1
        body = _bib_entry(e, cand)
        used_keys.add(re.match(r"@article\{([^,]+),", body).group(1))
        parts.append(body)
    text = "\n".join(parts)
    return {"text": text, "n_entries": len(entries),
            "n_matched": n_matched, "n_unmatched": n_unmatched,
            "n_review": len(re.findall(r"needs_review:", text)),
            "keys": sorted(used_keys)}


# --------------------------------------------------------------- 校验
def validate_topic(tdir: Path) -> Dict[str, Any]:
    """交叉校验：正文 [N] ↔ bib 键内嵌编号 双向对应（独立于生成逻辑）+ A4 口径。"""
    bib_path = tdir / "04_references" / "references.bib"
    if not bib_path.exists():
        return {"ok": False, "reason": "references.bib 不存在"}
    bib = bib_path.read_text(encoding="utf-8")
    keys = re.findall(r"@article\{([^,]+),", bib)
    nums = set()
    for k in keys:
        m = re.search(r"ref(\d+)$", k)
        if m:
            nums.add(int(m.group(1)))
    n_source = len(re.findall(r"^\s*source\s*:", bib, re.M))
    corpus = ""
    for p in tdir.rglob("*.md"):
        corpus += p.read_text(encoding="utf-8") + "\n"
    cited = set(int(n) for n in re.findall(r"\[(\d{1,3})\]", corpus))
    report = tdir / "topic-report.md"
    report_cited = set()
    if report.exists():
        report_cited = set(int(n) for n in
                           re.findall(r"\[(\d{1,3})\]", report.read_text(encoding="utf-8")))
    dangling = sorted(n for n in report_cited if n not in nums)
    dup = sorted({k for k in keys if keys.count(k) > 1})
    out: Dict[str, Any] = {"n_bib": len(keys), "n_report_cited": len(report_cited),
                           "dangling": dangling, "dup_keys": dup,
                           "source_lines_complete": n_source == len(keys)}
    if nums:
        out["uncited"] = sorted(n for n in nums if n not in cited)
        out["ok"] = (not dangling and not out["uncited"] and not dup
                     and out["source_lines_complete"])
    else:
        out["uncited"] = []
        out["ok"] = bool(keys) and not dangling and not dup and out["source_lines_complete"]
    return out


# --------------------------------------------------------------- 主流程
def _iter_topics() -> List[Path]:
    out: List[Path] = []
    for stage in _STAGES:
        d = TOPICS_ROOT / stage
        if d.exists():
            out += sorted(x for x in d.iterdir() if x.is_dir())
    return out


def process_topic(tdir: Path, apply: bool, force: bool = False) -> Dict[str, Any]:
    ref_dir = tdir / "04_references"
    topic_id = tdir.name
    res: Dict[str, Any] = {"topic_id": topic_id, "stage": tdir.parent.name}
    if (ref_dir / "references.bib").exists() and not force:
        res["skipped"] = "references.bib 已存在（幂等跳过；--force 重生成）"
        return res
    src_text = ""
    src_path = ref_dir / "references-source.md"
    if src_path.exists():
        src_text = src_path.read_text(encoding="utf-8")
    entries = _parse_source_list(src_text)
    candidates: List[Dict[str, Any]] = []
    for cpath in sorted(ref_dir.glob("bib-candidates-*.bib")):
        candidates += _parse_candidates(cpath)
    if not entries and not candidates:
        res["needs_review"] = "资料覆盖不足：references-source.md 无编号条目且无 bib-candidates——按红线不生成、不编造，待深研链 B1 补齐"
        return res
    if entries:
        gen = build_bib_text(entries, candidates, topic_id)
        res["mode"] = "numbered"
    else:
        gen = build_candidates_bib(candidates, topic_id)
        res["mode"] = "candidates-only"
    res.update({"n_entries": gen["n_entries"], "n_matched": gen["n_matched"],
                "n_candidates_raw": len(candidates), "n_review": gen["n_review"]})
    if apply:
        ref_dir.mkdir(parents=True, exist_ok=True)
        (ref_dir / "references.bib").write_text(gen["text"], encoding="utf-8")
        res["written"] = str(ref_dir / "references.bib")
        res["validate"] = validate_topic(tdir)
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="v8 启动包 references.bib 批量回填")
    ap.add_argument("--plan", action="store_true", help="预览全部（不写盘）")
    ap.add_argument("--apply", action="store_true", help="写盘生成")
    ap.add_argument("--topic", default="", help="仅处理指定课题")
    ap.add_argument("--force", action="store_true", help="已存在也重生成")
    ap.add_argument("--self-check", action="store_true", help="零依赖自检")
    args = ap.parse_args()
    if args.self_check:
        return _self_check()
    if not (args.plan or args.apply):
        ap.print_help()
        return 2
    results = []
    for tdir in _iter_topics():
        if args.topic and tdir.name != args.topic:
            continue
        results.append(process_topic(tdir, apply=args.apply, force=args.force))
    for r in results:
        if r.get("skipped"):
            print(f"  ○ {r['topic_id']}: {r['skipped']}")
        elif r.get("needs_review"):
            print(f"  ⚠ {r['topic_id']}: {r['needs_review']}")
        else:
            v = r.get("validate") or {}
            mark = "✓" if (not args.apply or v.get("ok")) else "✗"
            extra = "" if not args.apply else \
                (f" | 校验: bib{v.get('n_bib')} 悬空{len(v.get('dangling') or [])}"
                 f" 未引用{len(v.get('uncited') or [])} 重复键{len(v.get('dup_keys') or [])}"
                 f" source行{'全' if v.get('source_lines_complete') else '缺'}")
            print(f"  {mark} {r['topic_id']} [{r.get('mode','')}]: 条目 {r['n_entries']}"
                  f"（候选匹配 {r['n_matched']}，needs_review {r['n_review']}，原始候选 {r['n_candidates_raw']}）{extra}")
    if args.apply:
        save_json(AUDIT_PATH, {"at": now_utc(), "results": results})
        print(f"  ✓ 审计落盘: {AUDIT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


def _self_check() -> int:
    """自检：内嵌小样（解析/匹配/键名/溯源行/needs_review/中文数字姓氏）。"""
    src_text = (
        "[1] D. J. Thouless et al., “Quantized Hall conductance in a two-dimensional periodic potential,” "
        "Phys. Rev. Lett. 49, 405 (1982). DOI: 10.1103/PhysRevLett.49.405\n"
        "[2] Someone Else, “A paper without identifiers,” Some Journal (2019).\n"
        "[3] Šmejkal L, Sinova J, Jungwirth T. Emerging research landscape of altermagnetism. "
        "Phys Rev X, 2022, 12: 040501. DOI: 10.1103/PhysRevX.12.040501\n"
        "[4] N. Kumar, S. Najmaei, Q. Cui, et al., Phys. Rev. B 87, 161403(R) (2013).\n"
        "[5] Juraj Krempaský, Libor Šmejkal, et al. Altermagnetic lifting. Nature 626, 517-522 (2024). 10.1038/s41586-023-06907-7\n"
    )
    entries = _parse_source_list(src_text)
    assert len(entries) == 5, f"编号解析数量异常: {len(entries)}"
    assert entries[0]["doi"] == "10.1103/PhysRevLett.49.405", f"DOI 解析失败: {entries[0]['doi']}"
    assert entries[0]["title"].startswith("Quantized Hall"), "引号标题解析失败"
    assert entries[2]["surname"] == "Šmejkal", f"中文数字姓氏解析失败: {entries[2]['surname']}"
    assert entries[2]["year"] == "2022", f"年份解析失败: {entries[2]['year']}"
    assert entries[4]["doi"] == "10.1038/s41586-023-06907-7", f"裸 DOI 解析失败: {entries[4]['doi']}"
    assert not entries[3]["title"], "无题名条目不应编造标题"
    cand_text = ("@article{x1988,\n  title = {Quantized Hall Conductance in a Two-Dimensional Periodic Potential},\n"
                 "  author = {D. J. Thouless and Others},\n  journal = {Phys. Rev. Lett.},\n  year = {1982},\n"
                 "  doi = {10.1103/PhysRevLett.49.405},\n}\n")
    cpath = Path("/tmp/tref_selfcheck_candidates.bib")
    cpath.write_text(cand_text, encoding="utf-8")
    cands = _parse_candidates(cpath)
    assert len(cands) == 1 and cands[0]["doi"] == "10.1103/PhysRevLett.49.405", "候选解析失败"
    gen = build_bib_text(entries, cands, "general-selfcheck-20260101")
    assert gen["n_matched"] == 1, "DOI 匹配失败"
    assert "thouless1982ref1" in [k.lower() for k in gen["keys"]], f"键名异常: {gen['keys']}"
    assert any(k.lower().endswith(("ref2", "ref3", "ref4", "ref5")) for k in gen["keys"]), "编号键缺失"
    assert re.search(r"^\s*source\s*:", gen["text"], re.M), "source 溯源行缺失"
    assert "needs_review" in gen["text"], "无溯源字段条目未标注 needs_review"
    assert ",\n  year" in gen["text"] or gen["text"].count("},\n") >= 3, "字段逗号分隔异常"
    print("  ✓ topic_references_backfill 自检：解析/匹配/键名/溯源行/needs_review/双姓氏风格 全过")
    cpath.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
