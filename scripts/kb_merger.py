#!/usr/bin/env python3
"""重复 wiki 页合并执行器（v6.9.6）。

背景
----
kb_health_weekend 自 v3.x 就能检测"同名/近义概念"（_detect_duplicate_concepts
按 title 分组输出重复组），但检测出重复对后没有合并动作——"检测有、执行缺"。
本脚本补上执行器：以重复组为输入，选主页面、LLM 辅助融合正文、迁移 related
边/tags，被并页降级为重定向 stub（保留检索可达性）。

设计约束
--------
1. LLM 是增强不是依赖：融合调用失败时降级为"边迁移 + 正文附录并置"，
   保证合并永远可完成，只是质量略低。
2. 周限量护栏：默认每周最多 5 对（MAX_PAIRS_PER_WEEK），由周日反思 job
   （reflection_kb_merge_duplicates）调用，控 LLM 成本。
3. 全部写入走 kb_wiki.save_wiki_page 门面（frontmatter 合一防污染，
   自动记 growth log）。
4. 重定向 stub 而非删除：图谱/检索仍能命中旧标题，正文指向主页面。

用法示例
--------
    python3 scripts/kb_merger.py --dry-run      # 预览将合并的对
    python3 scripts/kb_merger.py --max-pairs 5  # 执行合并（周限量）
    python3 scripts/kb_merger.py --self-check   # 模块自检（零 LLM 零写入）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc  # noqa: E402

MAX_PAIRS_PER_WEEK = 5          # 周限量护栏（LLM 成本控制）
LLM_TIMEOUT = 120               # 单对融合超时
MAX_MERGE_BODY_CHARS = 8000     # 送 LLM 的正文截断

# 周执行留痕（防同周重复计数；周日 job 每周重置文件名）
_MERGE_LOG_DIR = PROJECT_ROOT / "memory" / "weekend-reflection"


# ---------------------------------------------------------------------------
# 检测：复用 kb_health_weekend 的同名分组
# ---------------------------------------------------------------------------


def detect_merge_pairs() -> List[Dict[str, Any]]:
    """返回待合并组：[{title, paths}]（同名不同文件）。

    排除已是重定向 stub 的页面（frontmatter 含 merged_into）。
    """
    from kb_health_weekend import _detect_duplicate_concepts
    from kb_wiki import get_wiki_page

    groups = _detect_duplicate_concepts()
    out: List[Dict[str, Any]] = []
    for g in groups:
        live = [p for p in g["paths"] if not _is_stub(p, get_wiki_page)]
        if len(live) > 1:
            out.append({"title": g["title"], "paths": live})
    return out


def _is_stub(path: str, getter) -> bool:
    """判断页面是否已是合并重定向 stub。"""
    page = getter(path)
    if not page:
        return False
    return bool((page.get("frontmatter") or {}).get("merged_into"))


# ---------------------------------------------------------------------------
# 合并核心
# ---------------------------------------------------------------------------


def pick_primary(paths: List[str], getter) -> str:
    """选主页面：正文长者优先（信息量大），同长比 updated_at 新者。"""
    best, best_key = "", (-1, "")
    for p in paths:
        page = getter(p)
        if not page:
            continue
        body_len = len(page.get("body", ""))
        updated = (page.get("frontmatter") or {}).get("updated_at", "")
        if body_len > best_key[0] or (body_len == best_key[0] and updated > best_key[1]):
            best, best_key = p, (body_len, updated)
    return best or paths[0]


def merge_related(primary_related: List[str], other_related: List[str],
                  primary_title: str, other_title: str) -> List[str]:
    """合并 related 边：并集去重，剔除互指与自指，保持主页面顺序在前。"""
    merged = list(primary_related or [])
    titles = {primary_title.lower(), other_title.lower()}
    for r in other_related or []:
        if r and r not in merged and r.lower() not in titles:
            merged.append(r)
    return [r for r in merged if r and r.lower() not in titles]


def _build_merge_prompt(title: str, primary_body: str, other_body: str) -> str:
    return (
        "你是知识库编辑。以下是对同一概念「%s」的两个 wiki 页正文，"
        "请合并为一篇结构化 Markdown：保留双方全部关键信息（定义/机制/"
        "实验/公式/来源），重复段落只留更完整版本，按逻辑重组章节，"
        "不要添加原文没有的内容，不要输出 frontmatter。\n\n"
        "=== 页面 A（主，内容较全）===\n%s\n\n=== 页面 B（被并入）===\n%s\n\n"
        "直接输出合并后的正文 Markdown："
    ) % (title, primary_body[:MAX_MERGE_BODY_CHARS], other_body[:MAX_MERGE_BODY_CHARS])


def _fallback_body(primary_body: str, other_body: str, other_title: str) -> str:
    """LLM 失败时的保守合并：A 原文 + B 独有内容附录。"""
    appendix = "\n\n## 合并自「%s」\n\n%s\n" % (other_title, (other_body or "").strip())
    return (primary_body or "").rstrip() + appendix


def build_stub_body(other_title: str, primary_title: str, primary_path: str) -> str:
    """构造被并页的重定向 stub 正文。"""
    return (
        "# %s（已合并）\n\n本页已合并至 **%s**（`%s`）。\n\n"
        "请前往主页面查看完整内容。\n"
    ) % (other_title, primary_title, primary_path)


def merge_pair(primary_path: str, other_path: str, dry_run: bool = False) -> Dict[str, Any]:
    """合并一对页面：other 并入 primary。

    Returns:
        {"success", "primary", "merged", "mode": "llm"|"fallback", "edges"}
    """
    from kb_wiki import get_wiki_page, save_wiki_page

    pri = get_wiki_page(primary_path)
    oth = get_wiki_page(other_path)
    if not pri or not oth:
        return {"success": False, "error": "页面读取失败"}

    pri_fm, oth_fm = pri.get("frontmatter", {}), oth.get("frontmatter", {})
    pri_title = pri_fm.get("title", Path(primary_path).stem)
    oth_title = oth_fm.get("title", Path(other_path).stem)

    # 1) 融合正文（LLM 增强，失败降级；dry-run 直接预览不花 LLM 成本）
    mode = "fallback"
    merged_body = _fallback_body(pri.get("body", ""), oth.get("body", ""), oth_title)
    ok, text, _meta = False, "", None
    if not dry_run:
        try:
            from llm_gateway import llm_complete
            ok, text, _meta = llm_complete(
                "你是知识库蒸馏器，只输出 Markdown 正文。",
                _build_merge_prompt(pri_title, pri.get("body", ""), oth.get("body", "")),
                timeout=LLM_TIMEOUT,
            )
        except Exception:
            ok = False
        if ok and text and len(text.strip()) > 50:
            merged_body = text.strip()
            mode = "llm"
    else:
        mode = "preview"

    # 2) 边与标签迁移
    new_related = merge_related(
        pri_fm.get("related", []), oth_fm.get("related", []), pri_title, oth_title
    )
    new_tags = list(pri_fm.get("tags", []))
    for t in oth_fm.get("tags", []):
        if t and t not in new_tags:
            new_tags.append(t)

    if dry_run:
        return {
            "success": True, "dry_run": True, "mode": mode,
            "primary": primary_path, "merged": other_path,
            "edges": len(new_related), "tags": len(new_tags),
        }

    # 3) 写主页面（正文 + 合并后的 frontmatter）
    pri_fm["related"] = new_related
    pri_fm["tags"] = new_tags
    pri_fm["updated_at"] = now_utc()
    pri_fm["merged_from"] = pri_fm.get("merged_from", []) + [other_path]
    save_wiki_page(primary_path, merged_body, pri_fm)

    # 4) 被并页 → 重定向 stub（保留 title/source_raw 供检索）
    oth_fm["merged_into"] = primary_path
    oth_fm["merged_at"] = now_utc()
    oth_fm["updated_at"] = now_utc()
    save_wiki_page(other_path, build_stub_body(oth_title, pri_title, primary_path), oth_fm)

    return {
        "success": True, "mode": mode,
        "primary": primary_path, "merged": other_path,
        "edges": len(new_related), "tags": len(new_tags),
    }


def run_merge(max_pairs: int = MAX_PAIRS_PER_WEEK, dry_run: bool = False) -> Dict[str, Any]:
    """批量执行：按组逐对合并，单对失败跳过不中断。"""
    from kb_wiki import get_wiki_page

    pairs = detect_merge_pairs()
    done, failed = [], []
    budget = max_pairs
    for g in pairs:
        if budget <= 0:
            break
        primary = pick_primary(g["paths"], get_wiki_page)
        for p in g["paths"]:
            if p == primary or budget <= 0:
                continue
            try:
                r = merge_pair(primary, p, dry_run=dry_run)
                if r.get("success"):
                    done.append({"primary": primary, "merged": p, "mode": r.get("mode")})
                    budget -= 1
                else:
                    failed.append({"pair": [primary, p], "error": r.get("error")})
            except Exception as e:
                failed.append({"pair": [primary, p], "error": str(e)})

    return {
        "groups_detected": len(pairs),
        "merged": len(done),
        "failed": len(failed),
        "detail": done,
        "errors": failed,
        "dry_run": dry_run,
    }


# ---------------------------------------------------------------------------
# 自检（零 LLM、零写入）
# ---------------------------------------------------------------------------


def _self_check() -> bool:
    ok = True
    print("=" * 50)
    print("◐ kb_merger 自检")
    print("=" * 50)

    # 1) 边合并：并集去重 + 剔除互指
    r = merge_related(["A", "B"], ["B", "C", "主标题", "被并标题"], "主标题", "被并标题")
    if r == ["A", "B", "C"]:
        print("✓ related 合并：并集去重，互指/自指剔除")
    else:
        print("✗ related 合并结果异常: %s" % r); ok = False

    # 2) 选主：正文长者胜
    fake = {
        "a.md": {"frontmatter": {"title": "短", "updated_at": "2026-08-15T00:00:00Z"}, "body": "x" * 10},
        "b.md": {"frontmatter": {"title": "长", "updated_at": "2026-08-01T00:00:00Z"}, "body": "x" * 100},
    }
    if pick_primary(["a.md", "b.md"], lambda p: fake.get(p)) == "b.md":
        print("✓ 选主：正文长度优先")
    else:
        print("✗ 选主逻辑异常"); ok = False

    # 3) stub 正文生成
    s = build_stub_body("旧概念", "新概念", "wiki/concepts/x.md")
    if "已合并" in s and "wiki/concepts/x.md" in s:
        print("✓ 重定向 stub 生成")
    else:
        print("✗ stub 生成异常"); ok = False

    # 4) 降级合并正文
    fb = _fallback_body("主体", "补充内容", "被并页")
    if "主体" in fb and "合并自「被并页」" in fb and "补充内容" in fb:
        print("✓ LLM 失败降级路径：正文附录并置")
    else:
        print("✗ 降级正文异常"); ok = False

    print("自检结果: %s" % ("通过" if ok else "失败"))
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description="重复 wiki 页合并执行器")
    ap.add_argument("--max-pairs", type=int, default=MAX_PAIRS_PER_WEEK, help="本次最多合并对数")
    ap.add_argument("--dry-run", action="store_true", help="预览不写入")
    ap.add_argument("--self-check", action="store_true", help="模块自检")
    args = ap.parse_args()

    if args.self_check:
        sys.exit(0 if _self_check() else 1)
    result = run_merge(max_pairs=args.max_pairs, dry_run=args.dry_run)
    print("检出重复组: %d" % result["groups_detected"])
    print("本次合并: %d 对%s" % (result["merged"], "（dry-run）" if args.dry_run else ""))
    for d in result["detail"]:
        print("  ✓ %s ← %s [%s]" % (d["primary"], d["merged"], d["mode"]))
    for e in result["errors"]:
        print("  ✗ %s | %s" % (e["pair"], e["error"]))


if __name__ == "__main__":
    main()
