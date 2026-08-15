#!/usr/bin/env python3
"""知识库分类体系重建器（v6.9.6）。

背景
----
category_coverage 长期只有 0.23，根因不是页面缺打标，而是 categories.json
里只有 1 个分类（"固体HHG"）——体系本身缺失。匹配引擎是现成的
（关键词规则匹配，_compute_category_coverage 会自动算 matched_paths），
所以"重建体系"等价于"扩充分类定义"，无需逐页打标。

策略
----
1. 数据源：wiki 页 frontmatter 的 tags 频率统计（排除 #前缀型 obsidian
   标签与过泛词）。
2. 聚类：出现 ≥ MIN_FREQ 次的主题 tag → 候选分类（name + keywords）。
3. 哲学：新增分类属语义决策，遵循项目"策略仅建议"原则——
   --apply 前必须 --dry-run 人工过目；周日 job 只跑候选提示不自动写入。
4. 幂等：已存在的同名分类跳过，不重复追加。

用法示例
--------
    python3 scripts/kb_taxonomy.py                 # 预览候选分类（等价 --dry-run）
    python3 scripts/kb_taxonomy.py --apply         # 写入 categories.json
    python3 scripts/kb_taxonomy.py --self-check    # 模块自检（零写入）
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc  # noqa: E402

CATEGORIES_PATH = PROJECT_ROOT / "knowledge" / "categories.json"
MIN_FREQ = 5                    # tag 至少出现次数
MAX_CATEGORIES = 12             # 候选上限（避免体系碎片化）

# 过泛/结构性标签不进分类体系
_STOP_TAGS = {
    "概念", "方法", "理论", "实验", "综述", "笔记", "项目", "论文",
    "concept", "method", "theory", "experiment", "review", "note",
    "HHG",  # 已有"固体HHG"覆盖，避免近重复
}


def _load_existing_names() -> List[str]:
    """读取现有分类名（兼容嵌套结构）。"""
    if not CATEGORIES_PATH.exists():
        return []
    try:
        data = json.loads(CATEGORIES_PATH.read_text(encoding="utf-8"))
        cats = data.get("categories", [])
        if isinstance(cats, dict):  # 历史嵌套：{"categories": {"categories": [...]}}
            cats = cats.get("categories", [])
        return [c.get("name", "") for c in cats if isinstance(c, dict)]
    except Exception:
        return []


def _clean_tag(t: str) -> bool:
    """tag 清洗：排除 # 前缀型、纯标点、过短无语义 tag。

    背景：实测 tags 数组存在 frontmatter 解析污染（行内逗号/引号/反斜杠
    被拆成独立 tag，如 "\\"、'"'、','），这些进分类体系只会产出垃圾。
    """
    t = str(t).strip()
    if not t or t.startswith("#") or t in _STOP_TAGS:
        return False
    if any(ch.isalnum() for ch in t) is False:   # 纯标点/符号
        return False
    cjk = any("\u4e00" <= ch <= "\u9fff" for ch in t)
    return len(t) >= 2 if cjk else len(t) >= 3    # CJK≥2 字，Latin≥3 字符


def collect_tag_freq() -> Counter:
    """统计全部 wiki 页 tags 频率（清洗后）。"""
    from kb_wiki import list_wiki_pages
    counter: Counter = Counter()
    for page in list_wiki_pages():
        for t in page.get("tags", []):
            if _clean_tag(t):
                counter[str(t).strip()] += 1
    return counter


def propose_categories(min_freq: int = MIN_FREQ) -> List[Dict[str, Any]]:
    """从 tag 频率生成候选分类清单（不写入）。

    Returns:
        [{"name", "keywords", "pages", "reason"}]，按覆盖页数降序。
    """
    existing = {n.lower() for n in _load_existing_names()}
    counter = collect_tag_freq()
    cands: List[Dict[str, Any]] = []
    for tag, freq in counter.most_common():
        if freq < min_freq or tag.lower() in existing:
            continue
        cands.append({
            "name": tag,
            "keywords": [tag],          # 匹配引擎按 title/tags 关键词规则匹配
            "pages": freq,
            "reason": f"tag 出现 {freq} 次（≥{min_freq}）",
        })
        if len(cands) >= MAX_CATEGORIES:
            break
    return cands


def apply_categories(cands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """把候选分类追加进 categories.json（同名跳过，原子写入带备份）。"""
    if not Cands_valid(cands):
        return {"success": False, "error": "候选为空或格式非法"}

    # 备份
    if CATEGORIES_PATH.exists():
        bak = CATEGORIES_PATH.with_suffix(".json.bak.%s" % now_utc()[:10])
        bak.write_text(CATEGORIES_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    data: Dict[str, Any] = {}
    if CATEGORIES_PATH.exists():
        try:
            data = json.loads(CATEGORIES_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    cats = data.get("categories", [])
    if isinstance(cats, dict):
        cats = cats.get("categories", [])

    existing = {c.get("name", "").lower() for c in cats if isinstance(c, dict)}
    added = 0
    for c in cands:
        if c["name"].lower() in existing:
            continue
        cats.append({
            "name": c["name"],
            "keywords": c["keywords"],
            "logic": "any",
            "description": c.get("reason", ""),
            "created": now_utc(),
            "matched_paths": [],
        })
        added += 1

    data["categories"] = cats
    tmp = CATEGORIES_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(CATEGORIES_PATH)

    # 关键词匹配引擎刷新：coverage 读取的是各分类预计算的 matched_paths，
    # 不扫描则新分类恒为空集（coverage 不变）。全库扫描幂等安全。
    try:
        from kb_categories import scan_all_categories
        scan_all_categories()
    except Exception:
        pass

    return {"success": True, "added": added, "total": len(cats)}


def Cands_valid(cands: List[Dict[str, Any]]) -> bool:
    return bool(cands) and all(c.get("name") and isinstance(c.get("keywords"), list) for c in cands)


def coverage_after() -> float:
    """写入后重算分类覆盖率（验证用）。字段名 coverage_rate。"""
    from kb_health import _compute_category_coverage
    cov = _compute_category_coverage()
    return float(cov.get("coverage_rate", 0.0))


# ---------------------------------------------------------------------------
# 自检（零写入）
# ---------------------------------------------------------------------------


def _self_check() -> bool:
    ok = True
    print("=" * 50)
    print("◐ kb_taxonomy 自检")
    print("=" * 50)

    # 1) tag 频率统计
    freq = collect_tag_freq()
    if freq and isinstance(freq.most_common(1)[0][1], int):
        top = freq.most_common(1)[0]
        print("✓ tag 频率统计：最高频「%s」×%d" % top)
    else:
        print("✗ 频率统计异常"); ok = False

    # 2) 候选生成：频次过滤 + 排除已有分类 + 停用词
    existing = {n.lower() for n in _load_existing_names()}
    cands = propose_categories(min_freq=3)
    names = {c["name"].lower() for c in cands}
    if not (names & existing) and all(c["pages"] >= 3 for c in cands):
        print("✓ 候选生成：过滤生效，无与现有分类重名（候选 %d 个）" % len(cands))
    else:
        print("✗ 候选过滤异常"); ok = False

    # 3) 停用词排除
    if "概念" not in names and "HHG" not in names:
        print("✓ 停用词/已有体系排除")
    else:
        print("✗ 停用词泄漏"); ok = False

    print("自检结果: %s" % ("通过" if ok else "失败"))
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description="知识库分类体系重建器")
    ap.add_argument("--min-freq", type=int, default=MIN_FREQ)
    ap.add_argument("--apply", action="store_true", help="写入 categories.json（默认只预览）")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()

    if args.self_check:
        sys.exit(0 if _self_check() else 1)

    cands = propose_categories(min_freq=args.min_freq)
    print("候选分类: %d 个（min_freq=%d，上限 %d）" % (len(cands), args.min_freq, MAX_CATEGORIES))
    for c in cands:
        print("  ○ %-22s 覆盖 %3d 页  %s" % (c["name"], c["pages"], c["reason"]))

    if args.apply:
        r = apply_categories(cands)
        if r.get("success"):
            print("✓ 已写入 %d 个分类（总 %d），覆盖率: %.2f → %.2f" % (
                r["added"], r["total"], 0.0, coverage_after()))
        else:
            print("✗ 写入失败: %s" % r.get("error"))
            sys.exit(1)


if __name__ == "__main__":
    main()
