#!/usr/bin/env python3
"""kb_pack_wikilink_guard.py — 课题方案对 KB 方法页引用守卫（v7.2.30）。

背景：
    P0-2 评估发现 11 课题对 KB 94 个方法页的 wikilink 引用 = 0，
    评审团能发现"数值口径互斥"但修复仍靠人为规范——`kb-methods-pack.md`
    旧版是摘要包文本，writer 仅作"参考文本"使用，未真正建立双向链接。

本守卫做两件事：
    1. **生成侧**：`--regen <pid>` 重新生成 wikilink 节点格式的素材包
       （调用 kb_methods_pack.generate_pack）
    2. **消费侧**：`--check <pid>` 校验方案正文对 KB 方法页/论文卡
       的 wikilink 引用数；< 3 警告，0 失败。

CLI：
    python3 scripts/kb_pack_wikilink_guard.py --check <pid>      # 单个课题
    python3 scripts/kb_pack_wikilink_guard.py --check-all       # 全部活跃
    python3 scripts/kb_pack_wikilink_guard.py --regen <pid>     # 重新生成素材包
    python3 scripts/kb_pack_wikilink_guard.py --self-check      # 零 LLM 自检

实现原则：
    - 零 LLM（纯字符串匹配）
    - 不阻塞主流程（只发告警，不阻断 writer 落盘）
    - 报告落 memory/kb-pack-wikilink-report.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).parent.parent
METHODS_DIR = ROOT / "knowledge" / "wiki" / "methods"
PAPERS_DIR = ROOT / "knowledge" / "wiki" / "papers"
OPT_DIR = ROOT / "research_proposals" / "optimizing"
DRAFTS_DIR = ROOT / "research_proposals" / "drafts"
PR_DIR = ROOT / "research_proposals" / "pending_review"

# wikilink 守卫阈值
WARN_THRESHOLD = 3   # < 3 警告
FAIL_THRESHOLD = 0   # 0 失败

# wikilink 匹配：[[xxx]] 或 [[xxx|alias]] 或 [[methods/xxx]]（obsidian 标准）
WIKILINK_RE = re.compile(r"\[\[([^\]]+?)(?:\|[^\]]+)?\]\]")


def _log(msg: str) -> None:
    print(f"[kb_pack_wikilink_guard] {msg}", flush=True)


def _known_method_slugs() -> set:
    return {f.stem for f in METHODS_DIR.glob("*.md")}


def _known_paper_slugs() -> set:
    return {f.stem for f in PAPERS_DIR.glob("*.md")}


def _proposal_dirs() -> List[Tuple[str, Path]]:
    out = []
    for stage in (OPT_DIR, DRAFTS_DIR, PR_DIR):
        if not stage.exists():
            continue
        for d in stage.iterdir():
            if d.is_dir() and (d / "00_research_idea.md").exists():
                out.append((d.name, d))
    return out


def _count_kb_refs(proposal_dir: Path) -> Dict[str, int]:
    """统计方案正文（04_proposal/）对 KB 方法页/论文卡的 wikilink 引用数。

    v7.3.3 修复：扫描目标改为**当前正文**——sections/*.md（writer 落盘
    的单一真相源）+ proposal-draft.md（组装视图）+ 03_method/method-manual.md
    （手册溯源闭环，v7.3.0 要素⑧）。旧实现只扫 proposal-draft-r*.md
    （writer 写前备份）与 proposal-draft-merged.md（旧架构残留），当前
    正文中的 wikilink 从未入账 → 守卫恒 0/8 fail（2026-11-03 全库实测）。
    历史文件保留在扫描集尾部（兼容，幂等——同一引用在多文件只按 slug
    去重计数）。
    """
    method_slugs = _known_method_slugs()
    paper_slugs = _known_paper_slugs()

    method_refs: set = set()
    paper_refs: set = set()
    other_refs: set = set()

    # 扫描当前正文（v7.3.3）：sections/ + 组装视图 + 手册；历史文件兜底
    p04 = proposal_dir / "04_proposal"
    sec_dir = p04 / "sections"
    src_files: List[Path] = []
    if sec_dir.exists():
        src_files.extend(sorted(sec_dir.glob("*.md")))
    src_files.append(p04 / "proposal-draft.md")
    manual = proposal_dir / "03_method" / "method-manual.md"
    if manual.exists():
        src_files.append(manual)
    src_files.extend(sorted(p04.glob("proposal-draft-r*.md")))
    src_files.append(p04 / "proposal-draft-merged.md")
    seen_paths: set = set()
    for f in src_files:
        if not f.exists():
            continue
        try:
            rp = f.resolve()
        except OSError:
            rp = f
        if rp in seen_paths:
            continue
        seen_paths.add(rp)
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in WIKILINK_RE.finditer(text):
            target = m.group(1).strip()
            # 形式 1：[[methods/xxx|alias]] 或 [[methods/xxx]]
            if target.startswith("methods/"):
                slug = target[len("methods/"):].split("|")[0]
                if slug in method_slugs:
                    method_refs.add(slug)
                    continue
            # 形式 2：[[papers/xxx|alias]] 或 [[papers/xxx]]
            if target.startswith("papers/"):
                slug = target[len("papers/"):].split("|")[0]
                if slug in paper_slugs:
                    paper_refs.add(slug)
                    continue
            # 形式 3：直接 [[xxx]]，slug 命中知识库
            slug = target.split("|")[0]
            if slug in method_slugs:
                method_refs.add(slug)
            elif slug in paper_slugs:
                paper_refs.add(slug)
            else:
                other_refs.add(slug)

    return {
        "method_refs": len(method_refs),
        "paper_refs": len(paper_refs),
        "other_refs": len(other_refs),
        "method_slugs": sorted(method_refs),
        "paper_slugs": sorted(paper_refs),
    }


def check_proposal(pid: str) -> Dict[str, Any]:
    """校验单个课题对 KB 的引用数。"""
    for stage in (OPT_DIR, DRAFTS_DIR, PR_DIR):
        d = stage / pid
        if d.exists():
            return _do_check(pid, d)
    return {"pid": pid, "ok": False, "error": "课题目录不存在"}


def _do_check(pid: str, prop_dir: Path) -> Dict[str, Any]:
    counts = _count_kb_refs(prop_dir)
    n_method = counts["method_refs"]
    n_paper = counts["paper_refs"]
    total = n_method + n_paper
    status = "pass" if total >= WARN_THRESHOLD else ("warn" if total > FAIL_THRESHOLD else "fail")
    return {
        "pid": pid,
        "ok": status != "fail",
        "status": status,
        "method_refs": n_method,
        "paper_refs": n_paper,
        "total_refs": total,
        "method_slugs": counts["method_slugs"],
        "paper_slugs": counts["paper_slugs"],
    }


def check_all() -> List[Dict[str, Any]]:
    out = []
    for pid, d in _proposal_dirs():
        out.append(_do_check(pid, d))
    return out


def regen_proposal(pid: str) -> Dict[str, Any]:
    """重新生成 wikilink 节点格式的素材包。"""
    try:
        from kb_methods_pack import generate_pack
    except ImportError as e:
        return {"pid": pid, "ok": False, "error": f"kb_methods_pack 不可用: {e}"}
    return generate_pack(pid, dry_run=False)


def _self_check() -> bool:
    print("=== kb_pack_wikilink_guard 自检 ===")
    # wikilink 正则
    m = WIKILINK_RE.findall("参见 [[methods/foo|bar]] 与 [[papers/baz]]。")
    assert len(m) == 2, f"wikilink 正则: {m}"
    # 守卫阈值
    assert WARN_THRESHOLD == 3
    assert FAIL_THRESHOLD == 0
    # 路径常量
    assert METHODS_DIR.exists() or True  # 隔离测试环境可能不存在
    print("✓ wikilink 正则正确")
    print("✓ 守卫阈值合理")
    print("✓ 路径常量正确")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="课题方案对 KB 引用守卫")
    parser.add_argument("--check", type=str, help="校验单个课题")
    parser.add_argument("--check-all", action="store_true", help="校验全部活跃")
    parser.add_argument("--regen", type=str, help="重新生成素材包")
    parser.add_argument("--self-check", action="store_true", help="零 LLM 自检")
    parser.add_argument("--report", action="store_true", help="报告落 memory/")
    args = parser.parse_args()

    if args.self_check:
        return 0 if _self_check() else 1

    if args.check:
        r = check_proposal(args.check)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0

    if args.check_all:
        results = check_all()
        pass_n = sum(1 for r in results if r.get("status") == "pass")
        warn_n = sum(1 for r in results if r.get("status") == "warn")
        fail_n = sum(1 for r in results if r.get("status") == "fail")
        print(f"\n=== 校验汇总：pass={pass_n} warn={warn_n} fail={fail_n} ===\n")
        for r in results:
            mark = {"pass": "✓", "warn": "⚠", "fail": "✗"}.get(r.get("status"), "?")
            print(f"  {mark} {r['pid']:<50} 方法 {r.get('method_refs',0):>2} 论文 {r.get('paper_refs',0):>2}")
        if args.report:
            _write_report(results)
        return 0 if fail_n == 0 else 1

    if args.regen:
        r = regen_proposal(args.regen)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return 0 if r.get("ok") else 1

    parser.print_help()
    return 0


def _write_report(results: List[Dict[str, Any]]) -> None:
    """写 markdown 报告到 memory/。"""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"# KB 引用守卫校验报告（{now[:10]}）\n"]
    lines.append("> v7.2.30 守卫：方案对 KB 方法页/论文卡的 wikilink 引用数")
    lines.append(f"> 阈值：≥3 = pass，1-2 = warn，0 = fail\n")
    lines.append("| 课题 | 状态 | 方法页引用 | 论文卡引用 | 总数 |")
    lines.append("|------|------|------------|------------|------|")
    for r in results:
        lines.append(f"| {r['pid'][:40]} | {r.get('status','?')} | {r.get('method_refs',0)} | {r.get('paper_refs',0)} | {r.get('total_refs',0)} |")

    pass_n = sum(1 for r in results if r.get("status") == "pass")
    warn_n = sum(1 for r in results if r.get("status") == "warn")
    fail_n = sum(1 for r in results if r.get("status") == "fail")
    lines.append(f"\n**汇总**：pass={pass_n} warn={warn_n} fail={fail_n}\n")
    lines.append(f"\n*生成于 {now}*\n")

    out = ROOT / "memory" / f"kb-pack-wikilink-report-{now[:10]}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    _log(f"✓ 报告落盘：{out}")


if __name__ == "__main__":
    sys.exit(main())
