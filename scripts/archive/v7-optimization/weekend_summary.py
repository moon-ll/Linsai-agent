#!/usr/bin/env python3
"""weekend_summary.py — 周末收尾汇总（v6.9.99，T2 周末维护链）。

周日 22:00 cron（lc-weekend-summary）执行：零 LLM 汇总本周末全链路
产出，写 memory/weekend-summary-{date}.md，供人工一屏掌握周末成果。

数据源：
- memory/weekend-pipeline.json — 反思链 calibration job 结果（high 数、
  注入课题数；state 被跨周重置前的权威口径）
- memory/weekend-input/ — summaries-{date}-r{N}.json（消化轮次/篇数）、
  clusters-week-{date}.json（新成簇）、routes-{date}.json（路由动作分布）
- research_proposals/optimizing/*/06_feedback/calibration-{date}.md —
  机器可读摘要行（pipeline state 不可用时的回退源）
- knowledge/wiki/methods/ — mtime 落在周末窗口内（周六 00:00 本地起）
  的方法页数

用法示例：
    python3 scripts/weekend_summary.py              # 生成汇总
    python3 scripts/weekend_summary.py --dry-run    # 仅打印不落盘
    python3 scripts/weekend_summary.py --self-check # 自检（临时目录，零污染）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import load_json, now_utc  # noqa: E402

# calibration 报告尾部的机器可读摘要行（maintenance_jobs 写入）
_CALIB_MARKER_RE = re.compile(
    r"<!-- calibration: (\{.*?\}) -->"
)

WEEKEND_INPUT_DIRNAME = "memory/weekend-input"
METHODS_RELPATH = "knowledge/wiki/methods"


# ---------------------------------------------------------------------------
# 时间窗口
# ---------------------------------------------------------------------------

def weekend_dates(now: Optional[datetime] = None) -> List[str]:
    """返回本周末（周六/周日）的日期字符串列表（本地时间口径）。

    与 weekend_pipeline._reset_stage_for_new_week 的"最近过去的周六
    00:00 本地"锚点一致：周六/周日运行返回本周末两天；工作日运行
    返回刚过去的周末（供补跑场景）。now 可注入供回归测试固定时钟。
    """
    local = now.astimezone() if now is not None else datetime.now().astimezone()
    days_since_sat = (local.weekday() - 5) % 7
    sat = (local - timedelta(days=days_since_sat)).date()
    return [sat.isoformat(), (sat + timedelta(days=1)).isoformat()]


def _weekend_anchor(now: Optional[datetime] = None) -> datetime:
    """本周末起点（周六 00:00 本地时间），供 mtime 窗口判定。"""
    local = now.astimezone() if now is not None else datetime.now().astimezone()
    days_since_sat = (local.weekday() - 5) % 7
    sat = (local - timedelta(days=days_since_sat)).replace(
        hour=0, minute=0, second=0, microsecond=0)
    return sat


# ---------------------------------------------------------------------------
# 各维度采集（root 可注入，默认 PROJECT_ROOT）
# ---------------------------------------------------------------------------

def collect_digest_stats(root: Path, dates: List[str]) -> Dict[str, int]:
    """消化轮次/篇数：统计周末两日的 summaries-{date}-r{N}.json。

    轮次 = 轮次号文件个数（旧名 summaries-{date}.json 为首轮兼容快照，
    不重复计数）；篇数 = 各文件 summaries 数组长度之和。
    """
    input_dir = root / WEEKEND_INPUT_DIRNAME
    rounds = 0
    papers = 0
    for d in dates:
        if not input_dir.exists():
            break
        for f in sorted(input_dir.glob(f"summaries-{d}-r*.json")):
            m = re.search(r"-r(\d+)\.json$", f.name)
            if not m:
                continue
            rounds += 1
            data = load_json(f, default={})
            papers += len(data.get("summaries", []) or [])
    return {"rounds": rounds, "papers": papers}


def collect_cluster_stats(root: Path, dates: List[str]) -> Dict[str, int]:
    """簇统计：本周末新成簇数（clusters-week）与蒸馏簇数（distilled）。"""
    input_dir = root / WEEKEND_INPUT_DIRNAME
    new_clusters = 0
    distilled = 0
    for d in dates:
        cw = input_dir / f"clusters-week-{d}.json"
        if cw.exists():
            data = load_json(cw, default={})
            new_clusters += len(data.get("new_clusters", []) or [])
        dc = input_dir / f"distilled-clusters-{d}.json"
        if dc.exists():
            data = load_json(dc, default={})
            distilled += len(data.get("clusters", []) or [])
    return {"new_clusters": new_clusters, "distilled_clusters": distilled}


def collect_route_stats(root: Path, dates: List[str]) -> Dict[str, Any]:
    """新想法路由：routes-{date}.json 的动作分布（new/merge/expansion/defer）。"""
    input_dir = root / WEEKEND_INPUT_DIRNAME
    total = 0
    actions: Dict[str, int] = {}
    for d in dates:
        rp = input_dir / f"routes-{d}.json"
        if not rp.exists():
            continue
        data = load_json(rp, default={})
        for r in data.get("routes", []) or []:
            if not isinstance(r, dict):
                continue
            total += 1
            act = str(r.get("action", "?"))
            actions[act] = actions.get(act, 0) + 1
    return {"total": total, "actions": actions}


def collect_calibration_stats(root: Path, dates: List[str]) -> Dict[str, Any]:
    """校准 high 数：优先读 weekend-pipeline.json 的 job result。

    回退源：optimizing/*/06_feedback/calibration-{date}.md 尾部的
    机器可读摘要行（state 跨周重置后仍可追溯当日报告）。
    """
    result: Dict[str, Any] = {"high_total": 0, "injected_count": 0, "source": "none"}
    pipe = root / "memory" / "weekend-pipeline.json"
    if pipe.exists():
        data = load_json(pipe, default={})
        for j in data.get("jobs", []) or []:
            if j.get("job_id") == "reflection_proposal_calibration":
                jr = j.get("result") or {}
                if isinstance(jr, dict) and "high_total" in jr:
                    result["high_total"] = int(jr.get("high_total", 0) or 0)
                    result["injected_count"] = len(jr.get("injected", []) or [])
                    result["source"] = "pipeline-state"
                    return result

    # 回退：扫描当日校准报告的 marker 行
    scanned = 0
    for d in dates:
        for f in (root / "research_proposals" / "optimizing").glob(
                f"*/06_feedback/calibration-{d}.md"):
            try:
                text = f.read_text(encoding="utf-8")
            except Exception:
                continue
            m = _CALIB_MARKER_RE.search(text)
            if not m:
                continue
            try:
                payload = json.loads(m.group(1))
                result["high_total"] += int(payload.get("high", 0) or 0)
                scanned += 1
            except Exception:
                continue
    if scanned:
        result["source"] = "calibration-reports"
    return result


def collect_methods_changes(root: Path, now: Optional[datetime] = None) -> int:
    """方法页变动数：knowledge/wiki/methods/ 下 mtime 落在周末窗口内的文件数。"""
    methods_dir = root / METHODS_RELPATH
    if not methods_dir.is_dir():
        return 0
    anchor = _weekend_anchor(now)
    count = 0
    for f in methods_dir.glob("*.md"):
        try:
            if datetime.fromtimestamp(f.stat().st_mtime).astimezone() >= anchor:
                count += 1
        except Exception:
            continue
    return count


# ---------------------------------------------------------------------------
# 汇总生成
# ---------------------------------------------------------------------------

def generate_summary(
    root: Optional[Path] = None,
    now: Optional[datetime] = None,
    write: bool = True,
) -> Dict[str, Any]:
    """生成周末收尾汇总，返回 {"success", "path", "text", "stats"}。"""
    root = root or PROJECT_ROOT
    dates = weekend_dates(now)
    date_str = now.astimezone().date().isoformat() if now is not None \
        else datetime.now().astimezone().date().isoformat()

    digest = collect_digest_stats(root, dates)
    clusters = collect_cluster_stats(root, dates)
    routes = collect_route_stats(root, dates)
    calibration = collect_calibration_stats(root, dates)
    methods_changed = collect_methods_changes(root, now)

    if routes["actions"]:
        route_line = "- 路由合计：{t} 条（{a}）".format(
            t=routes["total"],
            a=", ".join(f"{k}={v}" for k, v in sorted(routes["actions"].items())),
        )
    else:
        route_line = f"- 路由合计：{routes['total']} 条（无动作分布）"

    lines = [
        f"# 周末收尾汇总 — {date_str}",
        "",
        f"> 生成时间：{now_utc()} | 窗口：{dates[0]} ~ {dates[1]}（本地）",
        "> 来源：weekend_summary.py（零 LLM，lc-weekend-summary 周日 22:00）",
        "",
        "## 输入端",
        "",
        f"- 消化轮次：{digest['rounds']} 轮 | 深读篇数：{digest['papers']} 篇",
        f"- 新成簇：{clusters['new_clusters']} 个 | 蒸馏簇：{clusters['distilled_clusters']} 个",
        route_line,
        "",
        "## 维护链（T2）",
        "",
        f"- 校准 high 问题：{calibration['high_total']} 个（口径：{calibration['source']}）",
        f"- 反馈注入课题：{calibration['injected_count']} 个",
        f"- 方法页变动：{methods_changed} 个（knowledge/wiki/methods/，周末窗口内 mtime）",
        "",
        "## 反思链产物索引",
        "",
    ]

    # 反思产物索引（存在才列，缺省不误导）
    rf = root / "memory" / "weekend-reflection"
    for name, label in [
        (f"proposal-calibration-{dates[-1]}.md", "课题校准汇总"),
        (f"link-deep-review-{dates[-1]}.md", "全链路深度复盘"),
        (f"kb-taxonomy-apply-{dates[-1]}.md", "分类体系执行"),
        ("weekend-reflection-%s.json" % dates[-1], "反思报告"),
    ]:
        lines.append(f"- {'✓' if (rf / name).exists() else '○'} {label}：{name}")

    lines.append("")
    text = "\n".join(lines)

    out_path = root / "memory" / f"weekend-summary-{date_str}.md"
    if write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")

    return {
        "success": True,
        "path": str(out_path),
        "text": text,
        "stats": {
            "dates": dates,
            "digest": digest,
            "clusters": clusters,
            "routes": routes,
            "calibration": calibration,
            "methods_changed": methods_changed,
        },
    }


# ---------------------------------------------------------------------------
# 自检（临时目录构造数据，零污染、零 LLM）
# ---------------------------------------------------------------------------


def _self_check() -> bool:
    import tempfile

    print("=" * 50)
    print("◐ weekend_summary 自检")
    print("=" * 50)
    ok = True

    # 1) 周末窗口：周日运行 → 本周末两天；周三运行 → 上周末两天
    sunday = datetime(2026, 9, 6, 22, 0, 0).astimezone()   # 2026-09-06 是周日
    got = weekend_dates(sunday)
    if got == ["2026-09-05", "2026-09-06"]:
        print(f"✓ 周末窗口（周日运行）：{got}")
    else:
        print(f"✗ 周末窗口（周日运行）异常：{got}"); ok = False
    wednesday = datetime(2026, 9, 9, 12, 0, 0).astimezone()
    got = weekend_dates(wednesday)
    if got == ["2026-09-05", "2026-09-06"]:
        print(f"✓ 周末窗口（工作日补跑回看上周末）：{got}")
    else:
        print(f"✗ 周末窗口（工作日）异常：{got}"); ok = False

    with tempfile.TemporaryDirectory(prefix="weekend_summary_check_") as td:
        root = Path(td)
        dates = ["2026-09-05", "2026-09-06"]

        # 2) 消化轮次/篇数（含旧名不重复计数）
        winput = root / WEEKEND_INPUT_DIRNAME
        winput.mkdir(parents=True)
        (winput / "summaries-2026-09-05-r1.json").write_text(
            json.dumps({"summaries": [{"a": 1}, {"a": 2}, {"a": 3}]}), encoding="utf-8")
        (winput / "summaries-2026-09-05.json").write_text(
            json.dumps({"summaries": [{"a": 1}, {"a": 2}, {"a": 3}]}), encoding="utf-8")
        (winput / "summaries-2026-09-06-r2.json").write_text(
            json.dumps({"summaries": [{"a": 1}]}), encoding="utf-8")
        digest = collect_digest_stats(root, dates)
        if digest == {"rounds": 2, "papers": 4}:
            print(f"✓ 消化统计（旧名快照不重复计）：{digest}")
        else:
            print(f"✗ 消化统计异常：{digest}"); ok = False

        # 3) 簇与路由
        (winput / "clusters-week-2026-09-05.json").write_text(
            json.dumps({"new_clusters": [{"x": 1}, {"x": 2}]}), encoding="utf-8")
        (winput / "distilled-clusters-2026-09-05.json").write_text(
            json.dumps({"clusters": [{"x": 1}]}), encoding="utf-8")
        (winput / "routes-2026-09-06.json").write_text(
            json.dumps({"routes": [
                {"action": "new"}, {"action": "merge"},
                {"action": "new"}, {"action": "defer"}]}), encoding="utf-8")
        cs = collect_cluster_stats(root, dates)
        rs = collect_route_stats(root, dates)
        if cs == {"new_clusters": 2, "distilled_clusters": 1}:
            print(f"✓ 簇统计：{cs}")
        else:
            print(f"✗ 簇统计异常：{cs}"); ok = False
        if rs == {"total": 4, "actions": {"new": 2, "merge": 1, "defer": 1}}:
            print(f"✓ 路由统计：{rs}")
        else:
            print(f"✗ 路由统计异常：{rs}"); ok = False

        # 4) 校准回退源（marker 解析）
        fb = root / "research_proposals" / "optimizing" / "p1" / "06_feedback"
        fb.mkdir(parents=True)
        (fb / "calibration-2026-09-06.md").write_text(
            "# x\n\n<!-- calibration: {\"proposal_id\": \"p1\", "
            "\"high\": 2, \"issues\": 5, \"date\": \"2026-09-06\"} -->\n",
            encoding="utf-8")
        cal = collect_calibration_stats(root, dates)
        if cal["high_total"] == 2 and cal["source"] == "calibration-reports":
            print(f"✓ 校准回退源解析：{cal}")
        else:
            print(f"✗ 校准回退源异常：{cal}"); ok = False

        # 5) 方法页窗口
        methods = root / METHODS_RELPATH
        methods.mkdir(parents=True)
        fresh = methods / "fresh.md"
        fresh.write_text("x", encoding="utf-8")
        old = methods / "old.md"
        old.write_text("x", encoding="utf-8")
        import os
        sat_anchor_ts = datetime(2026, 9, 5, 0, 0, 0).timestamp()
        os.utime(old, (sat_anchor_ts - 86400, sat_anchor_ts - 86400))
        got = collect_methods_changes(root, now=sunday)
        if got == 1:
            print(f"✓ 方法页窗口过滤：{got}")
        else:
            print(f"✗ 方法页窗口过滤异常：{got}"); ok = False

        # 6) 汇总生成（不落盘）+ 落盘
        res = generate_summary(root, now=sunday, write=False)
        if not (root / "memory" / "weekend-summary-2026-09-06.md").exists():
            print("✓ write=False 不落盘")
        else:
            print("✗ write=False 不应落盘"); ok = False
        if "消化轮次：2" in res["text"] and "high 问题：2" in res["text"]:
            print("✓ 汇总文本含关键指标")
        else:
            print("✗ 汇总文本缺关键指标"); ok = False
        res2 = generate_summary(root, now=sunday, write=True)
        if (root / "memory" / "weekend-summary-2026-09-06.md").exists():
            print("✓ write=True 落盘")
        else:
            print("✗ write=True 应落盘"); ok = False

    print("自检结果: %s" % ("通过" if ok else "失败"))
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description="周末收尾汇总（零 LLM）")
    ap.add_argument("--dry-run", action="store_true", help="仅打印汇总不写文件")
    ap.add_argument("--self-check", action="store_true", help="运行自检")
    args = ap.parse_args()

    if args.self_check:
        sys.exit(0 if _self_check() else 1)

    res = generate_summary(write=not args.dry_run)
    print(res["text"] if args.dry_run else "✓ 周末汇总已生成：%s" % res["path"])


if __name__ == "__main__":
    main()
