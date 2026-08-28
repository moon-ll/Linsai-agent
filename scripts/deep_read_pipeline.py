#!/usr/bin/env python3
"""deep_read_pipeline — 深度阅读管线（v6.9.75 知识库质量线）。

职责：决定"哪些论文值得全文级处理"，并补齐 PDF 原文与全文文本。

双门入池（简报 cron 的 gate1/gate2）之后的第三层分流：
    - 用户指定清单（memory/deep-read-requests.json）→ 必读
    - agent 打分 score_agent ≥ 8 → 自动深度阅读
    - 其余 → 摘要级（留档，不消耗全文精读成本）

深度阅读 = ensure_pdf（arXiv PDF 落库 knowledge/raw/pdfs/）
         + get_or_extract_text（三级降级全文抽取 → _text_cache/）
         + raw frontmatter 标记 has_fulltext: true
之后 kb_distill 对 has_fulltext 论文走五要素深度蒸馏，
无全文论文走摘要级轻量笔记（digest_level: abstract）。

用法示例：
    python3 scripts/deep_read_pipeline.py --process          # 处理待深度阅读
    python3 scripts/deep_read_pipeline.py --request 2501.17380  # 用户指定
    python3 scripts/deep_read_pipeline.py --backfill         # 全库补 PDF
    python3 scripts/deep_read_pipeline.py --list             # 查看队列

规范：仅标准库；中文 docstring；路径经 paths 推导。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common import load_json, now_utc, save_json  # noqa: E402
from paths import KNOWLEDGE_DIR, MEMORY_DIR  # noqa: E402

try:
    from logger import get_logger
    _log = get_logger("deep_read_pipeline")
except Exception:  # pragma: no cover
    _log = None

REQUESTS_PATH = MEMORY_DIR / "deep-read-requests.json"
"""用户指定的深度阅读清单：{"requests": [{"arxiv_id": ..., "note": ..., "added_at": ...}]}"""

AUTO_SCORE_THRESHOLD = 8
"""agent 打分（score_agent, 1-10）达到该值的论文自动进入深度阅读。"""

RAW_PAPERS_DIR = KNOWLEDGE_DIR / "raw" / "papers"


# ─────────────────────────────────────────────
# 用户指定清单
# ─────────────────────────────────────────────

def add_request(arxiv_id: str, note: str = "") -> Dict[str, Any]:
    """把一篇论文加入用户指定深度阅读清单。"""
    data = load_json(REQUESTS_PATH, default={"requests": []})
    reqs = data.get("requests", [])
    if any(r.get("arxiv_id") == arxiv_id for r in reqs):
        return {"success": True, "message": f"{arxiv_id} 已在清单中", "added": False}
    reqs.append({"arxiv_id": arxiv_id, "note": note, "added_at": now_utc()})
    save_json(REQUESTS_PATH, {"requests": reqs})
    return {"success": True, "message": f"{arxiv_id} 已加入深度阅读清单", "added": True}


def load_requests() -> List[Dict[str, Any]]:
    """读取用户指定清单。"""
    return load_json(REQUESTS_PATH, default={"requests": []}).get("requests", [])


# ─────────────────────────────────────────────
# 候选选取
# ─────────────────────────────────────────────

def _raw_frontmatter(raw_path: Path) -> Dict[str, Any]:
    """粗提取 raw md frontmatter 的关键字段（不做完整 YAML 解析）。"""
    out: Dict[str, Any] = {}
    try:
        head = raw_path.open(encoding="utf-8", errors="ignore").read(1200)
    except OSError:
        return out
    m = re.search(r"arxiv_id:\s*\"?([^\n\"#]+?)\"?\s*\n", head)
    if m:
        out["arxiv_id"] = m.group(1).strip()
    m = re.search(r"score_agent:\s*(null|\d+(?:\.\d+)?)", head)
    if m and m.group(1) != "null":
        try:
            out["score_agent"] = float(m.group(1))
        except ValueError:
            pass
    m = re.search(r"agent_rejected:\s*(true|false)", head)
    if m:
        out["agent_rejected"] = m.group(1) == "true"
    m = re.search(r"has_fulltext:\s*(true|false)", head)
    if m:
        out["has_fulltext"] = m.group(1) == "true"
    return out


def select_candidates(raw_dir: Optional[Path] = None) -> Dict[str, List[Dict[str, Any]]]:
    """扫描 raw/papers，按深度阅读规则分流。

    Returns:
        {"deep": [...], "abstract_level": [...]}——deep 为待全文处理
        （用户指定 ∪ score_agent≥8，且尚无全文标记），abstract_level
        为其余（含 rejected）。
    """
    root = raw_dir or RAW_PAPERS_DIR
    requested = {r.get("arxiv_id", "").strip(): r for r in load_requests()}
    deep: List[Dict[str, Any]] = []
    abstract_level: List[Dict[str, Any]] = []
    if not root.exists():
        return {"deep": deep, "abstract_level": abstract_level}
    for p in sorted(root.glob("*.md")):
        fm = _raw_frontmatter(p)
        if fm.get("has_fulltext"):
            continue  # 已是全文级
        entry = {"path": p, "arxiv_id": fm.get("arxiv_id", ""),
                 "score_agent": fm.get("score_agent"), "reason": ""}
        aid = entry["arxiv_id"]
        if aid and aid in requested:
            entry["reason"] = "用户指定"
            deep.append(entry)
        elif fm.get("score_agent") is not None and fm["score_agent"] >= AUTO_SCORE_THRESHOLD:
            entry["reason"] = f"agent 打分 {fm['score_agent']} ≥ {AUTO_SCORE_THRESHOLD}"
            deep.append(entry)
        else:
            abstract_level.append(entry)
    return {"deep": deep, "abstract_level": abstract_level}


# ─────────────────────────────────────────────
# 深度阅读执行
# ─────────────────────────────────────────────

def process_one(raw_path: Path, arxiv_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """对单篇执行：抓 PDF → 抽全文 → 标记 has_fulltext。"""
    from pdf_manager import ensure_pdf_for_arxiv
    if dry_run:
        return {"success": True, "raw": raw_path.name, "dry_run": True}
    meta = ensure_pdf_for_arxiv(arxiv_id, title="")
    if not meta:
        return {"success": False, "raw": raw_path.name,
                "error": "PDF 获取失败（非 arXiv 或下载失败）"}
    from pdf_manager import PdfLibrary
    text = PdfLibrary().get_pdf_text(arxiv_id)
    if not text:
        return {"success": False, "raw": raw_path.name, "error": "全文抽取失败"}
    # frontmatter 标记
    t = raw_path.read_text(encoding="utf-8")
    if "has_fulltext:" in t:
        t = re.sub(r"has_fulltext:\s*\w+", "has_fulltext: true", t, count=1)
    else:
        t = t.replace("---\n", "---\nhas_fulltext: true\n", 1)
    raw_path.write_text(t, encoding="utf-8")
    return {"success": True, "raw": raw_path.name, "arxiv_id": arxiv_id,
            "text_chars": len(text), "pdf": meta.get("path", "")}


def process_deep_reads(dry_run: bool = False, limit: Optional[int] = None) -> Dict[str, Any]:
    """处理全部待深度阅读条目。"""
    sel = select_candidates()
    todo = sel["deep"][:limit] if limit else sel["deep"]
    results = []
    for entry in todo:
        if not entry["arxiv_id"]:
            results.append({"success": False, "raw": entry["path"].name,
                            "error": "raw 无 arxiv_id（DOI 型论文，暂不支持自动抓取）"})
            continue
        r = process_one(entry["path"], entry["arxiv_id"], dry_run=dry_run)
        r["reason"] = entry["reason"]
        results.append(r)
        if _log:
            _log.info("[deep-read] %s: %s", entry["path"].name[:40],
                      "OK" if r.get("success") else r.get("error", ""))
    return {
        "deep_total": len(sel["deep"]),
        "abstract_level": len(sel["abstract_level"]),
        "processed": len(results),
        "ok": sum(1 for r in results if r.get("success")),
        "results": results,
    }


# ─────────────────────────────────────────────
# 全库补 PDF（存量重构第一步）
# ─────────────────────────────────────────────

def backfill_pdfs(dry_run: bool = False, limit: Optional[int] = None) -> Dict[str, Any]:
    """为全库 raw/papers 中带 arxiv_id 且尚无 PDF 的论文批量抓取。"""
    from pdf_manager import ensure_pdf_for_arxiv
    results = {"ok": 0, "fail": 0, "skip": 0, "items": []}
    rows = []
    for p in sorted(RAW_PAPERS_DIR.glob("*.md")):
        fm = _raw_frontmatter(p)
        aid = fm.get("arxiv_id", "")
        if not aid or not re.match(r"^\d{4}\.\d{4,5}", aid):
            results["skip"] += 1
            continue  # DOI 型/无 ID：暂不支持
        try:
            head = p.open(encoding="utf-8", errors="ignore").read(1200)
        except OSError:
            continue
        if re.search(r"has_fulltext:\s*true", head):
            results["skip"] += 1
            continue
        rows.append((p, aid))
    if limit:
        rows = rows[:limit]
    for p, aid in rows:
        if dry_run:
            results["ok"] += 1
            continue
        meta = ensure_pdf_for_arxiv(aid, title="")
        if meta:
            t = p.read_text(encoding="utf-8")
            if "has_fulltext:" in t:
                t = re.sub(r"has_fulltext:\s*\w+", "has_fulltext: true", t, count=1)
            else:
                t = t.replace("---\n", "---\nhas_fulltext: true\n", 1)
            p.write_text(t, encoding="utf-8")
            results["ok"] += 1
            results["items"].append(aid)
        else:
            results["fail"] += 1
            if _log and results["fail"] <= 5:
                _log.warning("[backfill] %s 抓取失败", aid)
    return results


def _self_check() -> None:
    """自检：清单读写（临时注入）+ 分流逻辑。"""
    import tempfile
    from pathlib import Path as _P
    with tempfile.TemporaryDirectory() as td:
        raw_dir = _P(td)
        (raw_dir / "a.md").write_text(
            '---\narxiv_id: "2501.17380"\nscore_agent: 9\n---\n正文', encoding="utf-8")
        (raw_dir / "b.md").write_text(
            '---\narxiv_id: "2502.00001"\nscore_agent: 5\n---\n正文', encoding="utf-8")
        (raw_dir / "c.md").write_text(
            '---\narxiv_id: "2503.00002"\nhas_fulltext: true\n---\n正文', encoding="utf-8")
        sel = select_candidates(raw_dir)
        assert len(sel["deep"]) == 1 and sel["deep"][0]["path"].name == "a.md", sel
        assert len(sel["abstract_level"]) == 1, "c 已有全文应跳过"
    fm = _raw_frontmatter(RAW_PAPERS_DIR)
    assert isinstance(fm, dict)
    print("✓ deep_read_pipeline 自检通过")


def main() -> None:
    parser = argparse.ArgumentParser(description="深度阅读管线")
    parser.add_argument("--process", action="store_true", help="处理待深度阅读条目")
    parser.add_argument("--request", metavar="ARXIV_ID", help="用户指定深度阅读")
    parser.add_argument("--note", metavar="NOTE", default="", help="--request 附注")
    parser.add_argument("--backfill", action="store_true", help="全库补 PDF（存量重构）")
    parser.add_argument("--list", action="store_true", help="查看分流队列")
    parser.add_argument("--dry-run", action="store_true", help="预览不落盘")
    parser.add_argument("--limit", type=int, default=None, help="本次最多处理条数")
    parser.add_argument("--self-check", action="store_true", help="自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return
    if args.request:
        print(add_request(args.request, args.note)["message"])
        return
    if args.list:
        sel = select_candidates()
        print(f"待深度阅读 {len(sel['deep'])} 篇：")
        for e in sel["deep"][:20]:
            print(f"  {e['path'].name[:50]} [{e['reason']}]")
        print(f"摘要级 {len(sel['abstract_level'])} 篇")
        return
    if args.backfill:
        r = backfill_pdfs(dry_run=args.dry_run, limit=args.limit)
        print(f"补 PDF: 成功 {r['ok']} | 失败 {r['fail']} | 跳过 {r['skip']}")
        return
    if args.process:
        r = process_deep_reads(dry_run=args.dry_run, limit=args.limit)
        print(f"深度阅读: 待处理 {r['deep_total']} | 本次 {r['processed']} | "
              f"成功 {r['ok']} | 摘要级 {r['abstract_level']}")
        return
    parser.print_help()


if __name__ == "__main__":
    main()
