#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""溯源审计（v8.0.99）——ready 包"全文核实"声明与溯源页级别的机械对账。

动机（2026-11-22 机动轮内容 QA）：NSDR 包抽检发现 B3 writer 会把摘要级 raw 页
来源标为"[V] 全文核实"（ref12 MgO 7.8 eV 实为摘要级溯源）。本工具把该抽检
模式化，对全部 ready 包机械扫描两类失真：
① 溯源页级别错位——bib 条目 source 指向 raw/papers（摘要级导入）而正文
   声称"全文核实"；
② 引用键悬空——正文 [ref:键] 在 bib 中不存在（A4 兜底复核）。
零 LLM；只读；输出中文审计报告；不修改任何包内容（修正由人/轮次执行）。

用法示例：
    python3 scripts/provenance_audit.py                # 全量扫描
    python3 scripts/provenance_audit.py --topic <id>   # 单包扫描
    python3 scripts/provenance_audit.py --self-check
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from common import save_json  # noqa: E402

PROJECT_ROOT = Path(__file__).parent.parent
READY_DIR = PROJECT_ROOT / "research_topics" / "ready"
AUDIT_PATH = PROJECT_ROOT / "research_topics" / "_audit" / "provenance-audit.json"


def _bib_entries(bib_text: str) -> List[Dict[str, str]]:
    """解析 bib：键 + source 行指向的页路径。"""
    out: List[Dict[str, str]] = []
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", bib_text, re.S):
        key = m.group(2).strip()
        body = m.group(3)
        sm = re.search(r"source\s*:?\s*(.+)", body)
        src = sm.group(1).strip() if sm else ""
        out.append({"key": key, "source": src})
    return out


def _source_level(src: str) -> str:
    """溯源页级别：wiki/papers=蒸馏级；raw/papers=摘要级；其它=外部/未知。"""
    has_wiki = "wiki/papers" in src or "wiki\\papers" in src
    has_raw = "raw/papers" in src or "raw\\papers" in src
    if has_wiki:
        return "wiki"  # 双路径（raw+wiki）以蒸馏页为准
    if has_raw:
        return "raw"
    if "wiki/papers" in src or "wiki\\papers" in src:
        return "wiki"
    if src:
        return "other"
    return "missing"


def audit_topic(tdir: Path) -> Dict[str, Any]:
    """单包审计：①全文核实×raw 级 ②悬空引用键。"""
    tid = tdir.name
    bib_path = tdir / "04_references" / "references.bib"
    report = tdir / "topic-report.md"
    res: Dict[str, Any] = {"topic": tid, "issues": [], "entries": 0}
    if not bib_path.is_file() or not report.is_file():
        res["issues"].append("缺 bib 或报告")
        return res
    bib_text = bib_path.read_text(encoding="utf-8")
    entries = _bib_entries(bib_text)
    res["entries"] = len(entries)
    key2level = {e["key"]: _source_level(e["source"]) for e in entries}
    raw_keys = [k for k, lv in key2level.items() if lv == "raw"]
    res["raw_level_keys"] = raw_keys
    text = report.read_text(encoding="utf-8")
    # ①"全文核实"声明 与 raw 级键同现的条目（启发式：bib 注释块里的"全文核实"）：
    # bib 的 note 字段若含"全文核实"且该键溯源为 raw → 级别错位
    inflated = []
    for e in entries:
        m = re.search(r"@(\w+)\{" + re.escape(e["key"]) + r",(.*?)\n\}", bib_text, re.S)
        body2 = m.group(2) if m else ""
        # 仅匹配肯定式"全文核实"，排除"待/需/尚未全文核实"
        affirmed = re.search(r"(?<![待需尚未])全文核实", body2) and not re.search(r"[待需尚未]\\s*全文核实", body2)
        if m and affirmed and key2level.get(e["key"]) == "raw":
            inflated.append(e["key"])
    if inflated:
        res["issues"].append(f"溯源级别错位（raw 级却标全文核实）: {', '.join(inflated)}")
    # ②悬空引用键
    cited = set(re.findall(r"\[ref:([^\]]+)\]", text))
    dangling = sorted(c for c in cited if c not in key2level)
    if dangling:
        res["issues"].append(f"悬空引用键: {', '.join(dangling)}")
    return res


def audit_all(stage_dir: Path = READY_DIR) -> Dict[str, Any]:
    """全量扫描 ready 包。"""
    out: Dict[str, Any] = {"scanned": 0, "clean": 0, "findings": []}
    for tdir in sorted(p for p in stage_dir.iterdir() if p.is_dir()):
        r = audit_topic(tdir)
        out["scanned"] += 1
        if r["issues"]:
            out["findings"].append(r)
        else:
            out["clean"] += 1
    return out


def _self_check() -> int:
    ok = True
    # 合成 bib 级别判定
    self_assert = [
        (_source_level("knowledge/raw/papers/x.md"), "raw"),
        (_source_level("knowledge/wiki/papers/x.md"), "wiki"),
        (_source_level(""), "missing"),
    ]
    for got, want in self_assert:
        if got != want:
            print(f"✗ 级别判定 {got} != {want}")
            ok = False
    print("✓ provenance_audit 自检通过" if ok else "✗ 自检未通过")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="ready 包溯源审计（零 LLM 只读）")
    ap.add_argument("--topic", help="单包扫描")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        return _self_check()
    if args.topic:
        tdir = READY_DIR / args.topic
        if not tdir.is_dir():
            print(f"✗ 包不存在: {args.topic}")
            return 1
        r = audit_topic(tdir)
        print(r["topic"], "→", "✓ 无问题" if not r["issues"] else "; ".join(r["issues"]))
        return 0
    out = audit_all()
    print(f"扫描 {out['scanned']} 包：✓ {out['clean']} 无问题，{len(out['findings'])} 包有发现")
    for f in out["findings"]:
        print(f"  ⚠ {f['topic']}: {'; '.join(f['issues'])}")
    save_json(AUDIT_PATH, out)
    print(f"审计产物: {AUDIT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
