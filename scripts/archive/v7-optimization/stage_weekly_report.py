#!/usr/bin/env python3
"""阶段级周报：per-step 失败率/时延 WoW 回归检测（v7.3.61，对标批次 D·目标 3）。

背景（memory/goals/2026-11-07-benchmark-sota-analysis.md 批次 D）：
    监管可观测性对标 Langfuse/LangSmith 类平台的 stage 聚合与 SLO 回归
    告警。本项目 step_usage 账本已有总量口径（retrospective 调用健康），
    但无 **per-step 阶段维度** 与 **周环比（WoW）回归检测**——失败率恶化
    （如 11-02 周 minimax 429 期 23.3%）只在总量层可见，定位不到具体
    阶段；阶段时延回归（researcher 超时梯度化 v7.3.45 这类改动的影响）
    也无系统比对。本模块补齐：双周窗口逐 step 聚合 → WoW delta → 确定
    性回归规则告警。

口径（确定性零 LLM，step_usage JSONL 月分片流式）：
    step 标签 = kind:name（与 retrospective 调用健康同口径，账本无独立
    step 字段）。窗口：本周 = [now-7d, now)，上周 = [now-14d, now-7d)。

回归规则（噪声地板防误报）：
    R1 失败率：fr_delta ≥ +5pp 且 本周该 step 总调用 ≥ 5
    R2 时延：p50 延时比 ≥ +50% 且 上周 p50 ≥ 60s
    两规则可叠加；step 总调用 < 3 的低频阶段不参与比对（样本不足）。

产出：
    memory/self-optimize/stage-weekly-<date>.json + stdout 摘要；
    retrospective.run_retrospective 尾部接入（fail-open，报告追加
    「阶段级 WoW 回归检测」节）。

用法：
    python3 scripts/stage_weekly_report.py --report      # 生成并落盘
    python3 scripts/stage_weekly_report.py --self-check
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc, save_json  # noqa: E402

USAGE_DIR = PROJECT_ROOT / "memory" / "usage"
OUT_DIR = PROJECT_ROOT / "memory" / "self-optimize"

# 回归规则阈值
FR_DELTA_PP = 5.0        # 失败率恶化（百分点）
FR_MIN_CALLS = 5         # 失败率比对的样本地板
P50_DELTA_PCT = 50.0     # p50 延时增幅（%）
P50_MIN_BASE_S = 60.0    # p50 比对的绝对地板（秒）
MIN_WINDOW_CALLS = 3     # 参与比对的最低窗口样本

_SUBSUP_MONTH_FMT = "%Y-%m"


def _month_files(usage_dir: Path, now: datetime) -> List[Path]:
    """当月 + 上月分片（与 retrospective 同口径）。"""
    files = []
    for offset in (0, 1):
        m = (now.replace(day=1) - timedelta(days=30 * offset))
        files.append(usage_dir / f"step-usage-{m.strftime(_SUBSUP_MONTH_FMT)}.jsonl")
    return files


def _collect_window(usage_dir: Path, start: datetime, end: datetime,
                    now: datetime) -> Dict[str, Dict[str, Any]]:
    """流式聚合一个窗口的 per-step 指标。"""
    stats: Dict[str, Dict[str, Any]] = {}
    for path in _month_files(usage_dir, now):
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e = json.loads(line)
                    except Exception:
                        continue
                    if not isinstance(e, dict):
                        continue
                    ts = _parse_ts(str(e.get("ts", "")))
                    if ts is None or not (start <= ts < end):
                        continue
                    label = f"{e.get('kind', 'unknown')}:{e.get('name', 'unknown')}"
                    st = stats.setdefault(label, {"total": 0, "failed": 0,
                                                  "elapsed": []})
                    st["total"] += 1
                    if not e.get("success", True):
                        st["failed"] += 1
                    el = e.get("elapsed_s")
                    if isinstance(el, (int, float)) and el >= 0:
                        st["elapsed"].append(float(el))
        except Exception:
            continue
    return stats


def _parse_ts(s: str) -> Optional[datetime]:
    try:
        return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _p50(values: List[float]) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    return round(s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2, 1)


def _stage_row(label: str, cur: Dict[str, Any], prev: Dict[str, Any]) -> Dict[str, Any]:
    cur_total = cur.get("total", 0)
    prev_total = prev.get("total", 0)
    cur_fr = round(cur.get("failed", 0) / cur_total * 100, 1) if cur_total else None
    prev_fr = round(prev.get("failed", 0) / prev_total * 100, 1) if prev_total else None
    cur_p50 = _p50(cur.get("elapsed", []))
    prev_p50 = _p50(prev.get("elapsed", []))
    row: Dict[str, Any] = {
        "step": label,
        "cur_total": cur_total, "prev_total": prev_total,
        "cur_failure_rate": cur_fr, "prev_failure_rate": prev_fr,
        "cur_p50_s": cur_p50, "prev_p50_s": prev_p50,
        "regressions": [],
    }
    # R1 失败率回归
    if cur_fr is not None and prev_fr is not None \
            and cur_total >= FR_MIN_CALLS and (cur_fr - prev_fr) >= FR_DELTA_PP:
        row["regressions"].append(
            f"R1 失败率 {prev_fr}%→{cur_fr}%（+{round(cur_fr - prev_fr, 1)}pp）")
    # R2 时延回归
    if cur_p50 is not None and prev_p50 is not None and prev_p50 >= P50_MIN_BASE_S:
        pct = round((cur_p50 - prev_p50) / prev_p50 * 100, 1)
        if pct >= P50_DELTA_PCT:
            row["regressions"].append(
                f"R2 p50 {prev_p50}s→{cur_p50}s（+{pct}%）")
    return row


def build_report(usage_dir: Path = USAGE_DIR, now: Optional[datetime] = None) -> Dict[str, Any]:
    """双周窗口聚合 + WoW 回归检测（确定性，零 LLM）。"""
    now = now or datetime.now(timezone.utc)
    week = timedelta(days=7)
    cur = _collect_window(usage_dir, now - week, now, now)
    prev = _collect_window(usage_dir, now - 2 * week, now - week, now)
    labels = sorted(set(cur) | set(prev))
    rows = []
    for label in labels:
        if cur.get(label, {}).get("total", 0) + prev.get(label, {}).get("total", 0) < MIN_WINDOW_CALLS:
            continue  # 低频阶段样本不足不比对
        rows.append(_stage_row(label, cur.get(label, {}), prev.get(label, {})))
    rows.sort(key=lambda r: -r["cur_total"])
    regressions = [{"step": r["step"], "flags": r["regressions"]}
                   for r in rows if r["regressions"]]
    return {
        "generated_at": now_utc(),
        "window": {"cur_start": (now - week).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "prev_start": (now - 2 * week).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "stages": rows,
        "regressions": regressions,
        "summary": {
            "stages_compared": len(rows),
            "regression_count": len(regressions),
            "note": "规则：R1 失败率 ≥+5pp（样本≥5）；R2 p50 ≥+50%（上周 p50≥60s）；"
                    "窗口样本 <3 的低频阶段不比对",
        },
    }


def _markdown(report: Dict[str, Any]) -> str:
    lines = ["## 阶段级 WoW 回归检测（批次 D，目标 3）", ""]
    s = report.get("summary", {})
    lines.append(f"- 比对阶段数：{s.get('stages_compared')} | 回归数：{s.get('regression_count')}")
    if report.get("regressions"):
        for r in report["regressions"]:
            lines.append(f"- ⚠ {r['step']}：{'；'.join(r['flags'])}")
    else:
        lines.append("- ✓ 无阶段级回归（阈值内）")
    lines.append("")
    lines.append("| step | 本周调数 | 失败率 | 上周失败率 | p50 | 上周 p50 |")
    lines.append("|---|---|---|---|---|---|")
    for r in report.get("stages", [])[:15]:
        lines.append(
            f"| {r['step']} | {r['cur_total']} | {r['cur_failure_rate']}% | "
            f"{r['prev_failure_rate']}% | {r['cur_p50_s']}s | {r['prev_p50_s']}s |")
    return "\n".join(lines)


def run_and_persist(now: Optional[datetime] = None) -> Tuple[Dict[str, Any], str]:
    """生成 + 落盘 JSON，返回 (报告, markdown 节文本)。"""
    report = build_report(USAGE_DIR, now)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    date = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    out = OUT_DIR / f"stage-weekly-{date}.json"
    save_json(out, report)
    return report, _markdown(report)


def _self_check() -> bool:
    """自检：合成账本 → 回归规则触发/不触发/低频不比对/畸形行跳过。"""
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as td:
        usage = Path(td) / "usage"
        usage.mkdir(parents=True)
        now = datetime(2026, 11, 7, 12, 0, 0, tzinfo=timezone.utc)
        m_cur = usage / "step-usage-2026-11.jsonl"
        m_prev = usage / "step-usage-2026-10.jsonl"
        # 本周（11-01..11-07）researcher 失败率 60%（回归应触发）
        cur_lines = []
        for i in range(10):
            cur_lines.append(json.dumps({
                "ts": f"2026-11-0{1 + i % 7}T08:00:00Z", "kind": "hermes_agent",
                "name": "researcher", "success": i % 5 >= 2,  # 6 失败
                "elapsed_s": 300 + (i * 20) % 100, "error": "" if i % 5 < 2 else "超时"}))
        # 本周 critic 健康（0 失败，不触发）
        for i in range(10):
            cur_lines.append(json.dumps({
                "ts": f"2026-11-0{1 + i % 7}T09:00:00Z", "kind": "hermes_agent",
                "name": "critic", "success": True, "elapsed_s": 120}))
        m_cur.write_text("\n".join(cur_lines) + "\n", encoding="utf-8")
        # 上周 researcher 失败率 10%、p50 100s；critic p50 100s
        prev_lines = []
        for i in range(10):
            prev_lines.append(json.dumps({
                "ts": f"2026-10-{25 + i % 7:02d}T08:00:00Z", "kind": "hermes_agent",
                "name": "researcher", "success": i != 0, "elapsed_s": 100}))
            prev_lines.append(json.dumps({
                "ts": f"2026-10-{25 + i % 7:02d}T09:00:00Z", "kind": "hermes_agent",
                "name": "critic", "success": True, "elapsed_s": 100}))
        m_prev.write_text("\n".join(prev_lines) + "\n", encoding="utf-8")
        rep = build_report(usage, now=now)
        rows = {r["step"]: r for r in rep["stages"]}
        r1 = rows.get("hermes_agent:researcher", {})
        r2 = rows.get("hermes_agent:critic", {})
        t1 = any("R1 失败率" in f for f in r1.get("regressions", []))
        t2 = any("R2 p50" in f for f in r1.get("regressions", []))
        ok &= t1 and t2
        print(("✓" if t1 and t2 else "✗") + " researcher R1+R2 回归触发")
        ok &= not r2.get("regressions")
        print(("✓" if not r2.get("regressions") else "✗") + " critic 无回归")
        # 低频阶段不比对
        low = usage / "step-usage-2026-11.jsonl"
        with low.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": "2026-11-03T08:00:00Z", "kind": "llm_router",
                                "name": "kimi", "success": False, "elapsed_s": 5}) + "\n")
        rep2 = build_report(usage, now=now)
        ok &= all("llm_router:kimi" != r["step"] for r in rep2["stages"])
        print(("✓" if all("llm_router:kimi" != r["step"] for r in rep2["stages"]) else "✗")
              + " 低频阶段（<3 次）不比对")
    print("✓ stage_weekly_report 自检通过" if ok else "✗ stage_weekly_report 自检失败")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="阶段级 WoW 回归检测（批次 D）")
    ap.add_argument("--report", action="store_true", help="生成并落盘阶段级周报")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        return 0 if _self_check() else 1
    if args.report:
        rep, md = run_and_persist()
        print(md)
        date = rep["generated_at"][:10]
        print(f"\n✓ JSON 落盘: memory/self-optimize/stage-weekly-{date}.json")
        return 1 if rep.get("regressions") else 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
