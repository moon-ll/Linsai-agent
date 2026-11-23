#!/usr/bin/env python3
"""literature_screener — 文献质量筛选器（v6.10.52）。

目的：在 fulltext 升级前做零 LLM 成本的质量分档，把有限的蒸馏预算
花在高价值文献上。

评分维度（全部离线计算，零成本）：
    1. 相关性   — score_deepxiv（DeepXiv 检索相关度）+ score_agent（agent 主题打分/10）
    2. 重要性   — 引用数（citation_count，池 json 有）+ 是否被在研课题引用
    3. 可参考性 — 是否有全文（has_fulltext）、是否有 PDF、笔记字数
    4. 时效     — 年份（2024+ 加权）

分档：
    A（必升）— agent≥8 或课题已引用 + 相关度≥0.7
    B（应升）— 组合分达阈值
    C（观察）— 低分边缘
    D（候选清理）— 多维低分且零引用

用法：
    python3 scripts/literature_screener.py --scan        # 全库分档
    python3 scripts/literature_screener.py --scan --json # JSON 输出
    python3 scripts/literature_screener.py --cleanup-d   # 预览 D 档清理

规范：仅标准库；中文 docstring；零 LLM 调用。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from paths import KNOWLEDGE_DIR  # noqa: E402

RAW_PAPERS = KNOWLEDGE_DIR / "raw" / "papers"
HERMES_POOL = Path.home() / "Desktop" / "hermes_workspace" / "knowledge_base" / "AI_wiki" / "03-raw" / "papers"


def _fm(text: str, key: str) -> Any:
    """从 frontmatter 提取字段（容错）。"""
    m = re.search(rf'{key}:\s*"?([^\n"]+?)"?\s*(\n|$)', text)
    return m.group(1).strip() if m else None


def _citation_count(arxiv_id: str) -> int:
    """从 hermes 侧池 json 读引用数（无则 0）。"""
    if not arxiv_id:
        return 0
    f = HERMES_POOL / f"{arxiv_id}.json"
    if not f.exists():
        return 0
    try:
        return int(json.loads(f.read_text(encoding="utf-8")).get("citation_count", 0) or 0)
    except Exception:
        return 0


def scan_paper(wiki: Path, raw_by_aid: Dict[str, Path]) -> Dict[str, Any]:
    """对一篇 wiki 计算筛选分（零 LLM）。"""
    head = wiki.read_text(encoding="utf-8", errors="ignore")[:900]
    body_cn = len(re.findall(r"[一-鿿]", wiki.read_text(encoding="utf-8", errors="ignore")))

    # raw 关联（frontmatter 直连 → arxiv_id 反查）
    raw = None
    sr = _fm(head, "source_raw")
    if sr:
        cand = RAW_PAPERS / sr
        if cand.exists():
            raw = cand
    aid = (_fm(head, "arxiv_id") or "")
    if raw is None and aid:
        m = re.search(r"(\d{4}\.\d{4,5})", str(wiki.name))
        aid = m.group(1) if m else aid
        raw = raw_by_aid.get(aid)

    rh = raw.read_text(encoding="utf-8", errors="ignore")[:1200] if raw else ""
    _sd = _fm(rh, "score_deepxiv")
    try:
        score_deep = float(_sd) if _sd and _sd != "null" else 0.0
    except ValueError:
        score_deep = 0.0
    sa = _fm(rh, "score_agent")
    score_agent = float(sa) if sa and sa not in ("null", "None") else None
    rejected = bool(re.search(r"agent_rejected:\s*true", rh))
    has_fulltext = bool(re.search(r"has_fulltext:\s*true", rh))
    used_by = bool(re.search(r"used_by_proposals:\s*\[\"\w", rh))
    year = _fm(head, "year") or _fm(rh, "year") or ""
    try:
        year_i = int(str(year)[:4])
    except ValueError:
        year_i = 0
    cc = _citation_count(str(_fm(head, "arxiv_id") or aid))

    # ── 组合评分（0-100）──
    s = 0
    # 相关性（40 分）
    s += min(25, score_deep * 25)
    if score_agent is not None:
        s += (score_agent / 10) * 15
    else:
        s += min(15, score_deep * 15)  # 无 agent 分时用 deep 分补
    # 重要性（25 分）
    s += 10 if used_by else 0
    s += min(10, cc * 2)  # 引用数
    s += 5 if year_i >= 2025 else (3 if year_i >= 2024 else 0)
    # 可参考性（20 分）
    s += 12 if has_fulltext else 0
    s += min(8, body_cn // 300)
    # 摘要级已有笔记的保底（15 分）
    s += 15 if body_cn > 600 else (8 if body_cn > 300 else 0)

    # 分档
    if rejected and not used_by:
        tier = "D"
    elif score_agent is not None and score_agent >= 8:
        tier = "A" if s >= 60 else "B"
    elif used_by and score_deep >= 0.7:
        tier = "A"
    elif s >= 62:
        tier = "A"
    elif s >= 48:
        tier = "B"
    elif s >= 35:
        tier = "C"
    else:
        tier = "D"

    return {
        "wiki": str(wiki), "raw": str(raw) if raw else "",
        "arxiv_id": aid, "score_deep": round(score_deep, 2),
        "score_agent": score_agent, "used_by": used_by,
        "has_fulltext": has_fulltext, "year": year_i, "citations": cc,
        "body_cn": body_cn, "combo": round(s, 1), "tier": tier,
    }


def scan_all() -> List[Dict[str, Any]]:
    """全库扫描。"""
    raw_by_aid = {}
    for p in RAW_PAPERS.glob("*.md"):
        m = re.search(r"(\d{4}\.\d{4,5})", p.name)
        if m:
            raw_by_aid.setdefault(m.group(1), p)
    out = []
    for w in (KNOWLEDGE_DIR / "wiki" / "papers").glob("*.md"):
        out.append(scan_paper(w, raw_by_aid))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="文献质量筛选器（零 LLM）")
    ap.add_argument("--scan", action="store_true", help="全库分档")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--tier", metavar="A/B/C/D", help="只看某档")
    args = ap.parse_args()

    if args.scan:
        rows = scan_all()
        if args.tier:
            rows = [r for r in rows if r["tier"] == args.tier.upper()]
        if args.json:
            print(json.dumps(rows, ensure_ascii=False))
            return
        from collections import Counter
        dist = Counter(r["tier"] for r in rows)
        print(f"全库 {len(rows)} 篇分档: {dict(sorted(dist.items()))}")
        for tier in "ABCD":
            sub = [r for r in rows if r["tier"] == tier]
            if not sub:
                continue
            sub.sort(key=lambda r: -r["combo"])
            print(f"\n=== {tier} 档（{len(sub)} 篇）示例 ===")
            for r in sub[:5]:
                print(f"  combo={r['combo']} deep={r['score_deep']} agent={r['score_agent']} "
                      f"used={r['used_by']} ft={r['has_fulltext']} | {Path(r['wiki']).name[:40]}")
        return
    ap.print_help()


if __name__ == "__main__":
    main()
