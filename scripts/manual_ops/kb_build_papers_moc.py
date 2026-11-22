#!/usr/bin/env python3
"""论文库 MOC 生成器（v6.10.52，2026-09-25 知识库体检产物）。

背景
----
wiki/papers 1500+ 存活页此前零索引（体检：浏览动线缺口，"能搜到、
逛不到"）。本脚本生成轻量地图页 wiki/papers/MOC.md：按年份聚合计数
+ 最近入库 + 入口链接（简报索引/HHG 地图/PDF 库）。幂等可重跑，
蒸馏批次后可再执行刷新。

用法
----
    python3 scripts/manual_ops/kb_build_papers_moc.py [--dry-run]
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

MOC_PATH = "wiki/papers/MOC.md"


def _year_of(stem: str) -> str:
    m = re.match(r"^(\d{4})-", stem)
    if m and 1990 <= int(m.group(1)) <= 2030:
        return m.group(1)
    m = re.match(r"^(\d{2})\d{2}\.", stem)  # 裸 id：YYxx.yyyyy（取出版世纪未知，归"未分年"）
    return m.group(1) + "xx" if m else "未分年"


def main(dry_run: bool = False) -> int:
    from kb_merger import _ensure_wired

    _ensure_wired()
    from kb_wiki import get_wiki_page, list_wiki_pages, save_wiki_page
    from common import now_utc

    papers = [p for p in list_wiki_pages("papers")
              if not p.get("merged_into") and p.get("path") != "wiki/papers/MOC.md"]
    years = Counter(_year_of(Path(p["path"]).stem) for p in papers)
    by_mtime = sorted(
        papers,
        key=lambda p: (PROJECT_ROOT / "knowledge" / p["path"]).stat().st_mtime,
        reverse=True,
    )[:20]

    year_lines = "\n".join(
        "- **%s 年**：%d 篇" % (y, c) for y, c in sorted(years.items(), reverse=True)
    )
    recent_lines = "\n".join(
        "- [[%s]]" % p.get("title") for p in by_mtime
    )
    body = (
        "# 🗺️ 论文库地图\n\n"
        "> wiki/papers 的浏览入口。存活论文页 %d 篇（另有合并重定向 stub 不计）。\n\n"
        "## 入口\n"
        "- [[MOC-HHG|🗺️ HHG 知识地图]] — 概念与方法体系\n"
        "- [[briefing-index|📰 简报索引]] — 文献精选汇总\n"
        "- [[_pdf-library|📚 PDF 全文库]] — 深度阅读层\n\n"
        "## 按年份分布\n%s\n\n"
        "## 最近入库（前 20）\n%s\n\n"
        "---\n*由 kb_build_papers_moc.py 生成 · %s*\n"
        % (len(papers), year_lines, recent_lines, now_utc()[:10])
    )

    if dry_run:
        print("dry-run：将生成 %s（%d 篇存活论文）" % (MOC_PATH, len(papers)))
        return 0
    meta = {
        "title": "🗺️ 论文库地图",
        "type": "papers",
        "created": now_utc(),
        "updated": now_utc(),
        "tags": ["MOC", "论文库"],
        "related": ["高次谐波产生"],
        "source_raw": "",
        "growth_stage": "growing",
        "confidence": 0.9,
    }
    existing = get_wiki_page(MOC_PATH)
    if existing:
        meta["created"] = (existing.get("frontmatter") or {}).get("created", now_utc())
    save_wiki_page(MOC_PATH, body, meta)
    print("✓ %s 生成（%d 篇存活论文, %d 个年份桶）"
          % (MOC_PATH, len(papers), len(years)))
    return 0


if __name__ == "__main__":
    sys.exit(main(dry_run="--dry-run" in sys.argv))
