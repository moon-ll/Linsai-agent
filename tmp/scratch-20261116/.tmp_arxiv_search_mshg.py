# -*- coding: utf-8 -*-
"""临时检索驱动：arXiv API + external_fetcher.search_academic 多源检索。
用法: python3 .tmp_arxiv_search_mshg.py
输出: .tmp_arxiv_results_mshg.json
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "scripts"))

SKIP = set()
for line in (ROOT / ".tmp_skip_ids_20261113.txt").read_text().splitlines():
    line = line.strip()
    if line:
        SKIP.add(line.lower())

DATE_RANGE = "submittedDate:[202411010000 TO 202611140000]"
ARXIV_QUERIES = [
    'abs:"magnetic second harmonic generation"',
    'abs:"second harmonic generation" AND abs:antiferromagnet',
    'abs:MSHG',
    'abs:"nonlinear optical" AND (abs:"Neel vector" OR abs:"Néel vector")',
    'abs:NiO AND abs:"second harmonic"',
    'abs:"optical detection" AND abs:"antiferromagnetic order"',
    'abs:"antiferromagnetic domain" AND abs:"second harmonic"',
    'abs:CrSb AND abs:"spin splitting"',
    'abs:"altermagnet" AND abs:"nonlinear optical"',
    'abs:"nonreciprocal" AND abs:"second harmonic" AND abs:antiferromagnet',
    'abs:"magnetization-induced second harmonic"',
    'abs:"spin splitting" AND abs:"first-principles" AND abs:"antiferromagnet"',
    'abs:"antiferromagnetic" AND abs:"second-harmonic generation"',
    'abs:"optical readout" AND abs:antiferromagnet',
]

NS = {"a": "http://www.w3.org/2005/Atom"}


def norm_arxiv(raw: str) -> str:
    raw = (raw or "").strip()
    m = re.search(r"(\d{4}\.\d{4,5})(v\d+)?", raw)
    return m.group(1) if m else ""


def arxiv_api_search(query: str, max_results: int = 40):
    q = f"({query}) AND {DATE_RANGE}"
    params = urllib.parse.urlencode({
        "search_query": q,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    url = "http://export.arxiv.org/api/query?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "linsai-researcher/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = resp.read()
    except Exception as e:
        print(f"  ✗ arXiv API 查询失败 [{query[:50]}]: {e}", file=sys.stderr)
        return []
    root = ET.fromstring(data)
    out = []
    for entry in root.findall("a:entry", NS):
        aid = norm_arxiv(entry.findtext("a:id", "", NS))
        title = re.sub(r"\s+", " ", entry.findtext("a:title", "", NS)).strip()
        authors = [a.findtext("a:name", "", NS) for a in entry.findall("a:author", NS)]
        published = entry.findtext("a:published", "", NS)
        summary = re.sub(r"\s+", " ", entry.findtext("a:summary", "", NS)).strip()
        year = published[:4] if published else ""
        out.append({
            "arxiv_id": aid,
            "title": title,
            "authors": ", ".join(authors[:8]) + (" et al." if len(authors) > 8 else ""),
            "year": year,
            "abstract": summary,
            "source": "arxiv_api",
        })
    return out


def main():
    candidates = {}

    # 1) arXiv API 直接检索
    for q in ARXIV_QUERIES:
        print(f"◐ arXiv API: {q}", file=sys.stderr)
        for p in arxiv_api_search(q):
            if not p["arxiv_id"]:
                continue
            if p["arxiv_id"].lower() in SKIP:
                continue
            candidates.setdefault(p["arxiv_id"], p)
        time.sleep(1)  # arXiv API 礼仪：间隔 1s

    # 2) external_fetcher.search_academic 多源
    try:
        from external_fetcher import search_academic
        kw_queries = [
            "magnetic second harmonic generation antiferromagnet",
            "MSHG antiferromagnetic domain imaging",
            "nonlinear optical readout antiferromagnetic order",
            "NiO magnetic second harmonic generation",
            "antiferromagnetic order parameter optical detection",
            "CrSb first-principles spin splitting",
            "nonreciprocal second harmonic generation antiferromagnet",
            "nonlinear optical probing antiferromagnetic altermagnet",
        ]
        for q in kw_queries:
            print(f"◐ search_academic: {q}", file=sys.stderr)
            try:
                papers = search_academic(q, max_results=8,
                                         sources=("arxiv", "openalex", "semantic_scholar"),
                                         year_from=2024)
            except Exception as e:
                print(f"  ✗ search_academic 失败: {e}", file=sys.stderr)
                continue
            for p in papers:
                aid = norm_arxiv(str(p.get("arxiv_id") or ""))
                if aid:
                    if aid.lower() in SKIP:
                        continue
                    if aid not in candidates:
                        candidates[aid] = {
                            "arxiv_id": aid,
                            "title": p.get("title", ""),
                            "authors": p.get("authors", "") or p.get("author", "") or "",
                            "year": str(p.get("year") or ""),
                            "abstract": p.get("abstract", "") or "",
                            "source": "search_academic",
                        }
                else:
                    # 无 arXiv ID 的期刊论文：以 DOI 为 key
                    doi = (p.get("doi") or "").strip()
                    if doi and doi.lower() not in SKIP:
                        key = "doi:" + doi
                        if key not in candidates:
                            candidates[key] = {
                                "arxiv_id": doi,
                                "title": p.get("title", ""),
                                "authors": p.get("authors", "") or "",
                                "year": str(p.get("year") or ""),
                                "abstract": p.get("abstract", "") or "",
                                "source": "search_academic",
                            }
    except Exception as e:
        print(f"✗ external_fetcher 导入失败: {e}", file=sys.stderr)

    results = sorted(candidates.values(), key=lambda x: x.get("year", ""), reverse=True)
    out = ROOT / ".tmp_arxiv_results_mshg.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"✓ 候选 {len(results)} 篇 → {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
