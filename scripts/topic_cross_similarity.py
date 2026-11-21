#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨包相似度矩阵（v8 人工启动裁决辅助）——零 LLM 确定性 2-gram Jaccard。

动机：16 个启动包就绪待人工 activate/reject，裁决者需要"哪几个包其实是
同一个方向"的聚类视图。A2 新颖性硬门只在注册时对照"新候选 vs 存量"，
存量包之间的两两重叠从未被盘点过。

口径：与 A2 门同族算法（topic_pipeline.similarity，中文 2-gram + 拉丁词
Jaccard），文本 = 标题 + 一句话问题陈述（state.all_topics_for_match）。
分级：≥0.50 A2 硬门级（理论上不该出现在 ready）；0.30-0.50 高重叠；
<0.30 正常。产物：research_topics/_audit/cross-similarity-<日期>.json +
stdout 摘要（供会话/日报引用）。

用法示例：
    >>> python3 scripts/topic_cross_similarity.py                 # ready 全矩阵
    >>> python3 scripts/topic_cross_similarity.py --stage all     # 跨 stage 全量
    >>> python3 scripts/topic_cross_similarity.py --self-check
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).parent.parent
AUDIT_DIR = PROJECT_ROOT / "research_topics" / "_audit"

# 分级阈值（与 A2 硬门 0.50 对齐；0.30 为人工需留意的重叠下界）
LEVEL_HARD = 0.50
LEVEL_HIGH = 0.30


def build_matrix(items: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """纯函数：对 [{id, text}] 两两算 Jaccard，返回按分降序的 pair 列表。

    零 LLM；复用 A2 门同族的 jaccard_similarity（对称，单对手即对得分）。
    """
    from topic_pipeline import similarity

    pairs: List[Dict[str, Any]] = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            if not a.get("text", "").strip() or not b.get("text", "").strip():
                continue
            s = similarity.jaccard_similarity(a["text"], [b["text"]])
            level = ("hard" if s >= LEVEL_HARD
                     else "high" if s >= LEVEL_HIGH else "normal")
            pairs.append({"a": a["id"], "b": b["id"], "score": round(s, 4),
                          "level": level})
    pairs.sort(key=lambda p: -p["score"])
    return pairs


def run(stage: str = "ready", dry_run: bool = False) -> Dict[str, Any]:
    from topic_pipeline import state

    items = [t for t in state.all_topics_for_match()
             if stage == "all" or t.get("stage") == stage]
    pairs = build_matrix(items)
    hard = [p for p in pairs if p["level"] == "hard"]
    high = [p for p in pairs if p["level"] == "high"]
    report = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stage": stage,
        "n_topics": len(items),
        "n_pairs": len(pairs),
        "hard_count": len(hard),
        "high_count": len(high),
        "thresholds": {"hard": LEVEL_HARD, "high": LEVEL_HIGH},
        "pairs": pairs,
    }
    print(f"跨包相似度矩阵（stage={stage}，{len(items)} 包 / {len(pairs)} 对）")
    print(f"  ○ A2 硬门级(≥{LEVEL_HARD}): {len(hard)} 对 | 高重叠(≥{LEVEL_HIGH}): {len(high)} 对")
    if high or hard:
        print("  需留意的重叠对（top 10）:")
        for p in (hard + high)[:10]:
            print(f"    [{p['level']}] {p['score']:.3f}  {p['a']}  ↔  {p['b']}")
    else:
        print("  ✓ 无 ≥0.30 重叠对——16 包方向分散，裁决互不影响")
    if not dry_run:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        out = AUDIT_DIR / f"cross-similarity-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
        from common import save_json
        save_json(out, report)
        print(f"  ✓ 审计产物: {out.relative_to(PROJECT_ROOT)}")
    return report


def _self_check() -> None:
    assert LEVEL_HARD == 0.50 and LEVEL_HIGH == 0.30 and LEVEL_HARD > LEVEL_HIGH
    items = [
        {"id": "a", "text": "固体高次谐波产生与拓扑边界态探测"},
        {"id": "b", "text": "固体高次谐波产生与拓扑边界态探测"},
        {"id": "c", "text": "阿秒条纹技术量子相位测量"},
    ]
    pairs = build_matrix(items)
    assert pairs[0]["score"] == 1.0 and pairs[0]["level"] == "hard"
    assert all(p["level"] != "hard" for p in pairs[1:])
    print("✓ topic_cross_similarity 自检通过")


def main() -> int:
    ap = argparse.ArgumentParser(description="跨包相似度矩阵（人工裁决辅助）")
    ap.add_argument("--stage", default="ready", help="stage 过滤：ready|all 等")
    ap.add_argument("--dry-run", action="store_true", help="只打印不落盘")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        _self_check()
        return 0
    run(stage=args.stage, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
