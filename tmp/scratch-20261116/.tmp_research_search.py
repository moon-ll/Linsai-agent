#!/usr/bin/env python3
"""临时检索脚本：researcher profile 关键词检索（deepxiv arXiv + OpenAlex + Semantic Scholar）"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))
import external_fetcher as ef

QUERIES = [
    "tellurium high harmonic generation nonlinear response",
    "tellurium nonlinear refractive index strong field",
    "first-principles analytical model high harmonic generation comparison",
    "strong field calculation uncertainty cross-validation high harmonic generation",
    "high harmonic generation field strength prediction benchmark accuracy",
    "unified theory high harmonic generation mechanisms interference",
    "geometric Berry mechanism photocurrent coupling high harmonic generation",
    "Floquet-Bloch nonlinear mechanisms coexistence high harmonic",
]


def run_query(q):
    try:
        res = ef.search_academic(q, max_results=8,
                                 sources=("arxiv", "openalex", "semantic_scholar"),
                                 year_from=2024)
        return q, res
    except Exception as e:
        return q, [{"error": str(e)}]


def main():
    out = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for q, res in pool.map(run_query, QUERIES):
            out[q] = res
            print(f"[done] {q}: {len(res)} 条", file=sys.stderr)

    # 特殊任务：arXiv 2610.14367 的期刊发表版本
    try:
        paper = ef.fetch_arxiv_paper("2610.14367")
        out["_special_2610.14367"] = paper
    except Exception as e:
        out["_special_2610.14367"] = {"error": str(e)}

    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
