#!/usr/bin/env python3
"""试点变体记分卡（v7.3.59，对标批次 B·SICA 变体谱系）。

背景（memory/goals/2026-11-07-benchmark-sota-analysis.md 批次 B）：
    自进化试点机制（self_optimizer adoption-ledger）此前只有状态机
    （pending→piloting→adopted/rolled_back），晋升决策无量化依据——
    一个试点"是否真的让链路变好"只能凭印象裁决。对标 SICA（评估→
    改自身→重评的变体谱系：每个变体带 base/variant 指标对与 parent
    谱系），本模块补记分卡层。

记分卡 schema（memory/self-optimize/pilot-scorecards.json）：
    {scorecard_id, parent, source, action, proposal_id, round_start,
     status: open|adopted|reverted|fizzle,
     base: {metrics:{k:v}, at},       # 试点开启时的活指标快照
     variant: {metrics:{k:v}, at},    # 裁决时的指标快照（close 时补）
     delta: {k: after-before},        # close 时计算
     decision: {outcome, reason, at},
     opened_at}

指标口径（确定性零 LLM，全部取自 retrospective._analyze_live_ledgers 7 天窗）：
    failure_rate        调用失败率（%）
    bug_velocity_per_day BUG 修复速率（/天）
    whack_rate_pct      打地鼠复发率（%）
    timeout_failures    超时类失败次数
    daily_rounds        日均评分轮次

方向语义（delta 解读由裁决者完成，本模块只报差值与符号）：
    failure_rate / bug_velocity_per_day / whack_rate_pct / timeout_failures
    越低越好；daily_rounds 越高越好（吞吐）。

谱系（SICA parent 链）：
    open_scorecard 未显式给 parent 时，自动取同 source 的最近一个 adopted
    记分卡为父——形成 "v1 adopted → v2 以 v1 为父 → …" 的演化链；
    reverted/fizzle 不进父链（失败变体不作为演化基线）。

接线：
    - self_optimizer.promote_pilot：晋升试点时自动开卡（base 快照），
      scorecard_id 回写 ledger 试点条目（fail-open）。
    - self_optimizer.phase_ledger：基准门转红自动回滚试点时同步关卡
      （outcome=reverted）。
    - ZCode 每日治理会话：裁决试点结局时调 close_scorecard。

用法：
    python3 scripts/pilot_scorecard.py --open <source> <action> <proposal_id> <round>
    python3 scripts/pilot_scorecard.py --close <scorecard_id> <adopted|reverted|fizzle> [--reason R]
    python3 scripts/pilot_scorecard.py --report
    python3 scripts/pilot_scorecard.py --self-check
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import file_lock, load_json, now_utc, save_json  # noqa: E402

SCORECARDS_PATH = PROJECT_ROOT / "memory" / "self-optimize" / "pilot-scorecards.json"
OUTCOMES = {"adopted", "reverted", "fizzle"}

# 活指标 → 记分卡标量键的防御性提取（缺项跳过，不虚构）
_METRIC_PATHS = {
    "failure_rate": ("call_health", "failure_rate"),
    "bug_velocity_per_day": ("bug_velocity", "bug_velocity_per_day"),
    "whack_rate_pct": ("whack_a_mole", "rate_pct"),
    "timeout_failures": ("call_health", "timeout_failures"),
    "daily_rounds": ("machine_hours", "daily_rounds"),
}


def _snapshot_metrics() -> Dict[str, Any]:
    """从活账本提取标量指标快照（fail-open：任何异常降级为空快照）。"""
    try:
        return _snapshot_metrics_inner()
    except Exception as exc:
        return {"metrics": {}, "at": now_utc(), "error": str(exc)[:120]}


def _snapshot_metrics_inner() -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    from retrospective import _analyze_live_ledgers
    live = (_analyze_live_ledgers(period_days=7) or {})
    for key, (sec, field) in _METRIC_PATHS.items():
        try:
            v = (live.get(sec) or {}).get(field)
            if isinstance(v, (int, float)):
                metrics[key] = v
        except Exception:
            continue
    return {"metrics": metrics, "at": now_utc()}


def _load() -> Dict[str, Any]:
    return load_json(SCORECARDS_PATH, default={"scorecards": []})


def _save(data: Dict[str, Any]) -> None:
    data["updated_at"] = now_utc()
    save_json(SCORECARDS_PATH, data)


def _default_parent(data: Dict[str, Any], source: str) -> Optional[str]:
    """同 source 最近一个 adopted 记分卡为默认父（失败变体不进父链）。"""
    best = None
    for sc in data.get("scorecards", []):
        if sc.get("source") == source and sc.get("status") == "adopted":
            if best is None or str(sc.get("opened_at", "")) > str(best.get("opened_at", "")):
                best = sc
    return best.get("scorecard_id") if best else None


def open_scorecard(source: str, action: str, proposal_id: str,
                   round_start: int, parent: Optional[str] = None,
                   ledger_ref: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """开卡：记录 base 指标快照 + 谱系。幂等防护：同 source+action 已有
    open 卡时拒绝重复开卡（一变异一卡）。"""
    with file_lock("pilot-scorecards"):
        data = _load()
        for sc in data.get("scorecards", []):
            if sc.get("status") == "open" and sc.get("source") == source \
                    and sc.get("action") == action:
                return {"success": False,
                        "error": f"同源试点已有 open 卡 {sc.get('scorecard_id')}（先裁决再开新卡）"}
        if parent is None:
            parent = _default_parent(data, source)
        try:
            base = _snapshot_metrics()
        except Exception as exc:  # 快照层故障降级为空快照（开卡不崩，fail-open）
            base = {"metrics": {}, "at": now_utc(), "error": str(exc)[:120]}
        sc = {
            "scorecard_id": f"ps-{now_utc()[:10].replace('-', '')}-{len(data.get('scorecards', [])) + 1:03d}",
            "parent": parent,
            "source": source, "action": action,
            "proposal_id": proposal_id, "round_start": round_start,
            "status": "open",
            "base": base,
            "variant": None,
            "delta": None,
            "decision": None,
            "ledger_ref": ledger_ref or {},
            "opened_at": now_utc(),
        }
        data.setdefault("scorecards", []).append(sc)
        _save(data)
        return {"success": True, "scorecard_id": sc["scorecard_id"],
                "parent": parent, "base_metrics": sc["base"].get("metrics", {})}


def close_scorecard(scorecard_id: str, outcome: str, reason: str = "") -> Dict[str, Any]:
    """关卡：variant 指标快照 + delta 计算 + 终态裁决。"""
    if outcome not in OUTCOMES:
        return {"success": False, "error": f"outcome 须为 {sorted(OUTCOMES)}"}
    with file_lock("pilot-scorecards"):
        data = _load()
        sc = next((s for s in data.get("scorecards", [])
                   if s.get("scorecard_id") == scorecard_id), None)
        if not sc:
            return {"success": False, "error": f"记分卡不存在: {scorecard_id}"}
        if sc.get("status") != "open":
            return {"success": False, "error": f"记分卡已终态 {sc.get('status')}，不可重复裁决"}
        try:
            variant = _snapshot_metrics()
        except Exception as exc:  # 快照层故障降级（关卡不崩，delta 置空）
            variant = {"metrics": {}, "at": now_utc(), "error": str(exc)[:120]}
        delta: Dict[str, Any] = {}
        base_m = (sc.get("base") or {}).get("metrics", {})
        for k, after in (variant.get("metrics") or {}).items():
            if k in base_m:
                try:
                    delta[k] = round(float(after) - float(base_m[k]), 4)
                except Exception:
                    continue
        sc["status"] = outcome
        sc["variant"] = variant
        sc["delta"] = delta
        sc["decision"] = {"outcome": outcome, "reason": reason, "at": now_utc()}
        _save(data)
        return {"success": True, "scorecard_id": scorecard_id,
                "outcome": outcome, "delta": delta,
                "base_metrics": base_m, "variant_metrics": variant.get("metrics", {})}


def scorecard_report() -> Dict[str, Any]:
    """谱系 + delta 汇总（ZCode 治理会话的晋升决策输入）。"""
    data = _load()
    scs = data.get("scorecards", [])
    chains: Dict[str, List[Dict[str, Any]]] = {}
    for sc in scs:
        root = sc.get("source", "?")
        chains.setdefault(root, []).append(sc)
    summary = []
    for sc in scs:
        d = sc.get("delta") or {}
        summary.append({
            "scorecard_id": sc.get("scorecard_id"),
            "parent": sc.get("parent"),
            "source": sc.get("source"), "action": sc.get("action"),
            "status": sc.get("status"),
            "delta": d,
            "verdict_hint": _verdict_hint(d),
        })
    return {"total": len(scs), "open": sum(1 for s in scs if s.get("status") == "open"),
            "chains": {k: len(v) for k, v in chains.items()},
            "scorecards": summary}


def _verdict_hint(delta: Dict[str, Any]) -> str:
    """方向感知的 delta 一句话解读（Lower-better / Higher-better）。"""
    lower_better = ("failure_rate", "bug_velocity_per_day", "whack_rate_pct",
                    "timeout_failures")
    good = bad = 0
    for k, v in delta.items():
        if not isinstance(v, (int, float)) or v == 0:
            continue
        if k in lower_better:
            good += v < 0
            bad += v > 0
        else:  # daily_rounds 越高越好
            good += v > 0
            bad += v < 0
    if good and not bad:
        return "指标向好（晋升正信号）"
    if bad and not good:
        return "指标恶化（回退信号）"
    if good and bad:
        return "信号混合（人工裁量）"
    return "无有效 delta"


def _self_check() -> bool:
    """自检：开卡/关卡/delta/谱系/幂等防护/非法 outcome。"""
    import tempfile
    global SCORECARDS_PATH
    ok = True
    with tempfile.TemporaryDirectory() as td:
        orig = SCORECARDS_PATH
        try:
            SCORECARDS_PATH = Path(td) / "pilot-scorecards.json"
            r1 = open_scorecard("call_health", "修复降级链", "prop-x", 3)
            ok &= r1["success"]
            print(("✓" if r1["success"] else "✗") + " 开卡 + base 快照")
            # 幂等防护：同源重复开卡拒绝
            r1b = open_scorecard("call_health", "修复降级链", "prop-x", 3)
            ok &= r1b["success"] is False
            print(("✓" if r1b["success"] is False else "✗") + " 同源重复开卡拒绝")
            r2 = close_scorecard(r1["scorecard_id"], "adopted", reason="指标向好")
            ok &= r2["success"]
            print(("✓" if r2["success"] else "✗") + " 关卡 adopted + delta")
            r2b = close_scorecard(r1["scorecard_id"], "reverted")
            ok &= r2b["success"] is False
            print(("✓" if r2b["success"] is False else "✗") + " 终态不可重复裁决")
            r3 = open_scorecard("call_health", "重试梯度二档", "prop-x", 4)
            ok &= r3["success"] and r3.get("parent") == r1["scorecard_id"]
            print(("✓" if r3["success"] and r3.get("parent") == r1["scorecard_id"] else "✗")
                  + " 谱系：新卡默认父 = 同源最近 adopted")
            r4 = close_scorecard(r3["scorecard_id"], "fizzle")
            r5 = open_scorecard("call_health", "第三档", "prop-x", 5)
            ok &= r5["success"] and r5.get("parent") == r1["scorecard_id"]
            print(("✓" if r5.get("parent") == r1["scorecard_id"] else "✗")
                  + " 失败变体（fizzle）不进父链")
            r6 = close_scorecard("ps-nonexist", "adopted")
            ok &= r6["success"] is False
            r7 = close_scorecard(r5["scorecard_id"], "bogus")
            ok &= r7["success"] is False
            print(("✓" if (r6["success"] is False and r7["success"] is False) else "✗")
                  + " 非法 id/outcome 拒绝")
            close_scorecard(r5["scorecard_id"], "adopted")
            rep = scorecard_report()
            ok &= rep["total"] == 3 and rep["open"] == 0
            print(("✓" if (rep["total"] == 3 and rep["open"] == 0) else "✗") + " 报告汇总")
        finally:
            SCORECARDS_PATH = orig
    print("✓ pilot_scorecard 自检通过" if ok else "✗ pilot_scorecard 自检失败")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="试点变体记分卡（SICA 变体谱系）")
    ap.add_argument("--open", nargs=4, metavar=("SOURCE", "ACTION", "PROPOSAL_ID", "ROUND"))
    ap.add_argument("--parent", help="显式指定父记分卡（默认自动取同源最近 adopted）")
    ap.add_argument("--close", nargs=2, metavar=("SCORECARD_ID", "OUTCOME"))
    ap.add_argument("--reason", default="", help="裁决理由")
    ap.add_argument("--report", action="store_true", help="谱系 + delta 汇总")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        return 0 if _self_check() else 1
    if args.open:
        r = open_scorecard(args.open[0], args.open[1], args.open[2], int(args.open[3]),
                           parent=args.parent)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r.get("success") else 1
    if args.close:
        r = close_scorecard(args.close[0], args.close[1], reason=args.reason)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r.get("success") else 1
    if args.report:
        print(json.dumps(scorecard_report(), ensure_ascii=False, indent=1))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
