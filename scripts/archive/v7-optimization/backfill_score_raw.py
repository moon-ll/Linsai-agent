#!/usr/bin/env python3
"""回填 score_history 的 score_raw（v7.3.42）。

背景：v7.3.41 把 A 通道判定改为 cap 前原始分（score_raw），但在册 107 条
历史记录该字段全为空，判定一律回落 cap 后 display，A 判定空转。

本脚本按每条记录的 (round, focus_section) 定位对应 critic 报告，从报告中
取原始维度分重算 score_raw：
  - 四维章节（rationale/content/scheme/full_review）：0.30 创新 + 0.25 可行
    + 0.25 严谨 + 0.20 表达；
  - references（references_2d）：严谨/完整均值；
  - method_manual（manual_2d）：严谨/就绪度均值；
  - 找不到可用来源 → score_raw=None + caliber="unknown"，不估算。

写入字段：score_raw、score_raw_caliber（four_dim/two_dim/unknown）。
写入前自动备份 _lifecycle.json，全程 file_lock + 原子写。

用法：
    python3 scripts/backfill_score_raw.py --dry-run
    python3 scripts/backfill_score_raw.py --apply
    python3 scripts/backfill_score_raw.py --self-check
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import file_lock, load_json, save_json  # noqa: E402

LIFECYCLE = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
PROPOSAL_ROOT = PROJECT_ROOT / "research_proposals"

W4 = {"创新性": 0.30, "可行性": 0.25, "严谨性": 0.25, "表达质量": 0.20}
W2_REF = ("严谨性", "完整性")
W2_MANUAL = ("严谨性", "就绪度")


def parse_dims(text: str) -> Dict[str, float]:
    """从 critic 报告文本提取维度分（行式优先，表格兜底）。"""
    dims: Dict[str, float] = {}
    line_pat = re.compile(
        r"^(创新性|可行性|严谨性|表达质量|完整性|就绪度)[（(]?[a-z_]*[）)]?[：:|\s]+"
        r"(?:0\.\d+|\*\*0\.\d+\*\*)",
        re.MULTILINE,
    )
    for m in line_pat.finditer(text):
        name = m.group(1)
        if name in dims:
            continue
        nums = re.findall(r"0\.\d+", m.group(0))
        if nums:
            dims[name] = float(nums[-1].strip("*"))
    if len(dims) >= 2:
        return dims
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().replace("**", "") for c in line.strip().split("|")[1:-1]]
        if not cells:
            continue
        head = cells[0]
        for name in ("创新性", "可行性", "严谨性", "表达质量", "完整性", "就绪度"):
            if name not in head:
                continue
            pure = [float(c) for c in cells if re.fullmatch(r"0\.\d+", c)]
            if pure:
                dims.setdefault(name, pure[-1])
    return dims


def compute_raw(section: str, dims: Dict[str, float]) -> Tuple[Optional[float], str]:
    """按口径重算 score_raw；缺维返回 (None, "unknown")。"""
    if section == "references":
        if all(k in dims for k in W2_REF):
            return round(sum(dims[k] for k in W2_REF) / 2, 4), "two_dim"
        return None, "unknown"
    if section == "method_manual":
        if all(k in dims for k in W2_MANUAL):
            return round(sum(dims[k] for k in W2_MANUAL) / 2, 4), "two_dim"
        return None, "unknown"
    if all(k in dims for k in W4):
        return round(sum(W4[k] * dims[k] for k in W4), 4), "four_dim"
    return None, "unknown"


def _proposal_dir(pid: str, status: str) -> Optional[Path]:
    direct = PROPOSAL_ROOT / status / pid
    if direct.exists():
        return direct
    for sub in ("optimizing", "pending_review", "archived", "drafts"):
        p = PROPOSAL_ROOT / sub / pid
        if p.exists():
            return p
    return None


def find_report(pdir: Optional[Path], rnd: Any, section: str) -> Optional[Path]:
    """按 (round, section) 定位报告：优先带 section 后缀，其次裸文件。"""
    if not pdir:
        return None
    try:
        n = int(rnd)
    except (TypeError, ValueError):
        return None
    rev = pdir / "05_review"
    if not rev.exists():
        return None
    tagged = rev / f"critic-round-{n}-{section}.md"
    if tagged.exists() and tagged.stat().st_size > 100:
        return tagged
    bare = rev / f"critic-round-{n}.md"
    if bare.exists() and bare.stat().st_size > 100:
        return bare
    return None


def backfill(lifecycle: Dict[str, Any]) -> Dict[str, Any]:
    """对 lifecycle 结构就地回填，返回统计。dry-run 传副本。"""
    stats = {"total": 0, "four_dim": 0, "two_dim": 0, "unknown": 0, "changed": 0}
    for pid, ps in (lifecycle.get("proposals") or {}).items():
        if not isinstance(ps, dict):
            continue
        pdir = _proposal_dir(pid, ps.get("status") or "optimizing")
        for key in ("score_history", "score_history_archive"):
            for h in ps.get(key) or []:
                stats["total"] += 1
                section = h.get("focus_section") or "full_review"
                report = find_report(pdir, h.get("round"), section)
                dims = {}
                if report:
                    try:
                        dims = parse_dims(report.read_text("utf-8", errors="ignore"))
                    except OSError:
                        dims = {}
                raw, caliber = compute_raw(section, dims)
                old = h.get("score_raw")
                h["score_raw"] = raw
                h["score_raw_caliber"] = caliber
                stats[caliber] += 1
                if old != raw:
                    stats["changed"] += 1
    return stats


def _self_check() -> bool:
    text = "创新性：0.84\n可行性：0.79\n严谨性：0.70\n表达质量：0.78\n综合评分：0.78\n"
    dims = parse_dims(text)
    raw, cal = compute_raw("rationale", dims)
    ok1 = raw == round(0.30 * 0.84 + 0.25 * 0.79 + 0.25 * 0.70 + 0.20 * 0.78, 4) and cal == "four_dim"
    dims2 = {"严谨性": 0.84, "完整性": 0.88}
    raw2, cal2 = compute_raw("references", dims2)
    ok2 = raw2 == 0.86 and cal2 == "two_dim"
    raw3, cal3 = compute_raw("rationale", {"创新性": 0.80})
    ok3 = raw3 is None and cal3 == "unknown"
    ok = ok1 and ok2 and ok3
    print(f"✓ parse_dims={dims}" if ok else f"✗ self-check 失败 {dims}")
    return ok


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="回填 score_history.score_raw")
    ap.add_argument("--dry-run", action="store_true", help="只统计，不落盘")
    ap.add_argument("--apply", action="store_true", help="备份后写盘")
    ap.add_argument("--self-check", action="store_true", help="运行内置自检")
    args = ap.parse_args(argv)
    if args.self_check:
        return 0 if _self_check() else 1
    if not (args.dry_run or args.apply):
        ap.print_help()
        return 2

    data = load_json(LIFECYCLE, default={"proposals": {}})
    if args.dry_run:
        stats = backfill(json.loads(json.dumps(data)))
    else:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        backup = LIFECYCLE.with_name(f"_lifecycle.json.bak-score-raw-{ts}")
        shutil.copy2(LIFECYCLE, backup)
        with file_lock("proposal-lifecycle"):
            stats = backfill(data)
            save_json(LIFECYCLE, data)
        print(f"备份：{backup.name}")

    print(f"记录 {stats['total']} 条：four_dim {stats['four_dim']} / "
          f"two_dim {stats['two_dim']} / unknown {stats['unknown']}；变更 {stats['changed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
