#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_params_ref_integrity — 口径表-引用完整性守卫（v7.2.103，E3）。

背景（2026-11-01 attosecond 实测）：引用裁并（49→40）后，params.json 的
口径条目键仍引用已被裁并的编号「Jarecki[42]」——键成为死锚，后续 critic/
monitor 读到会误以为 [42] 存在。本守卫扫描指定课题（或全部 pending_review
+ optimizing 课题）的 params.json，把键与 canonical 文本中的 `[N]` 编号
与该课题 `04_proposal/sections/references.md`（或 proposal-draft.md 回退）
的实际条目对照，报告悬空编号。

只读报告，不修改任何文件（修复由调用方按报告执行，如 v7.2.103 的
「Jarecki[42] → Jarecki 2024」改名）。

用法：
    python3 scripts/check_params_ref_integrity.py                     # 全部活跃课题
    python3 scripts/check_params_ref_integrity.py --proposal PID      # 单课题
    python3 scripts/check_params_ref_integrity.py --self-check        # 自检
"""
import argparse
import json
import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from paths import PROJECT_ROOT  # noqa: E402


def check_proposal(prop_dir: Path) -> dict:
    """对单个课题做口径-引用完整性检查，返回报告 dict。"""
    params_file = prop_dir / "04_proposal" / "params.json"
    if not params_file.exists():
        return {"proposal": prop_dir.name, "status": "skip_no_params"}
    try:
        params = json.loads(params_file.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"proposal": prop_dir.name, "status": "skip_bad_json", "error": str(exc)[:120]}
    entries = params.get("entries") or []
    if not entries:
        return {"proposal": prop_dir.name, "status": "skip_no_entries"}

    refs_file = prop_dir / "04_proposal" / "sections" / "references.md"
    if not refs_file.exists():
        refs_file = prop_dir / "04_proposal" / "proposal-draft.md"
    ref_nums: set = set()
    if refs_file.exists():
        ref_nums = {int(x) for x in re.findall(r"^\[(\d+)\]", refs_file.read_text(encoding="utf-8"), re.M)}

    dangling = []
    for e in entries:
        texts = [str(e.get("key", "")), str(e.get("canonical", ""))]
        seen_entry = False
        for t in texts:
            if seen_entry:
                break
            for m in re.finditer(r"\[(\d+)\]", t):
                n = int(m.group(1))
                if ref_nums and n not in ref_nums:
                    dangling.append({"key": e.get("key", "")[:60], "ref": n})
                    seen_entry = True
                    break
    return {"proposal": prop_dir.name, "status": "ok" if not dangling else "dangling",
            "dangling": dangling, "ref_count": len(ref_nums)}


def run_all() -> list:
    reports = []
    root = PROJECT_ROOT / "research_proposals"
    for stage in ("pending_review", "optimizing"):
        stage_dir = root / stage
        if not stage_dir.exists():
            continue
        for d in sorted(stage_dir.iterdir()):
            if d.is_dir():
                reports.append(check_proposal(d))
    return reports


def _self_check() -> int:
    """自检：构造最小夹具验证悬空编号能被捕获。"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "optimizing" / "t-check"
        (d / "04_proposal" / "sections").mkdir(parents=True)
        (d / "04_proposal" / "sections" / "references.md").write_text(
            "[1] Alpha. 2020.\n[2] Beta. 2021.\n", encoding="utf-8")
        (d / "04_proposal" / "params.json").write_text(json.dumps(
            {"entries": [{"key": "X[1] 口径", "canonical": "x[1]"},
                          {"key": "Y[9] 口径", "canonical": "y[9]"}]},
            ensure_ascii=False), encoding="utf-8")
        rep = check_proposal(d)
        assert rep["status"] == "dangling", rep
        assert [x["ref"] for x in rep["dangling"]] == [9], rep
        print("✓ check_params_ref_integrity 自检通过（悬空 [9] 捕获，[1] 放行）")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="口径表-引用完整性守卫")
    ap.add_argument("--proposal", metavar="PID", help="仅检查单个课题")
    ap.add_argument("--self-check", action="store_true", help="自检")
    args = ap.parse_args()
    if args.self_check:
        sys.exit(_self_check())
    reports = [check_proposal(PROJECT_ROOT / "research_proposals" / "pending_review" / args.proposal)] \
        if args.proposal else run_all()
    bad = [r for r in reports if r.get("status") == "dangling"]
    for r in reports:
        mark = {"ok": "✓", "dangling": "✗"}.get(r["status"], "○")
        print(f"{mark} {r['proposal'][:52]:54s} {r['status']}"
              + (f" 悬空:{[x['ref'] for x in r['dangling']]}" if r["status"] == "dangling" else ""))
    print(f"\n{len(reports)} 课题，悬空口径键 {len(bad)} 个"
          + ("（修复：键改名去编号或补引用条目，勿机械删条目）" if bad else ""))


if __name__ == "__main__":
    main()
