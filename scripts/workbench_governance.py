#!/usr/bin/env python3
"""工作台治理入口（v8.0.2，ZCode 每日治理会话的数据采集器）。

v7 的 self_optimizer.py 已随优化环归档（scripts/archive/v7-optimization/），
本脚本承接其职责并适配 v8 数据源——治理闭环格式不变（基准门→活指标→
worklist→台账→日报），数据域换为课题工作台：

  A 基准门：test_topic_pipeline + 版本单调守门 + workbench_monitor
  B 活指标：topics 分布/needs_human + step_usage 调用健康 + BUG 速率
  C worklist：memory/self-optimize/worklist.json（沿用，含 7 天关闭抑制）
  D 日报：memory/self-optimize/daily-<date>.md

用法：
    python3 scripts/workbench_governance.py --run
    python3 scripts/workbench_governance.py --self-check
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common import file_lock, load_json, now_utc, save_json  # noqa: E402
from paths import PROJECT_ROOT  # noqa: E402

REPORT_DIR = PROJECT_ROOT / "memory" / "self-optimize"
WORKLIST_PATH = REPORT_DIR / "worklist.json"
LEDGER_PATH = REPORT_DIR / "adoption-ledger.json"

BENCHMARK_CMDS: List[List[str]] = [
    [sys.executable, str(SCRIPTS_DIR / "tests" / "test_topic_pipeline.py")],
    [sys.executable, "-m", "unittest", "scripts.tests.test_version_monotonic"],
    [sys.executable, str(SCRIPTS_DIR / "workbench_monitor.py")],
]
# v8.0.3: monitor 的 exit 1=「有 issue」是其 cron 告警语义；治理门禁只认
# 系统级故障（[high]，如 cron 缺失/深研停滞/KB 断流），业务等人类
# （[medium] needs_human，v8 设计行为）不禁止治理实施、转日报待办。


def phase_benchmark() -> Dict[str, Any]:
    """A 基准门：三项全绿才允许任何治理性代码变更（DGM 式准入，v8 数据源）。"""
    results, gate = [], True
    for cmd in BENCHMARK_CMDS:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=600, cwd=str(PROJECT_ROOT))
            ok = proc.returncode == 0
        except Exception as exc:
            ok = False
            results.append({"cmd": cmd[-1], "ok": False, "error": str(exc)[:120]})
            gate = False
            continue
        if cmd[-1].endswith("workbench_monitor.py") and not ok:
            # v8.0.3 分级：仅 high 级 issue 才判红；medium 转告警
            out = proc.stdout + proc.stderr
            has_high = "[high]" in out
            ok = not has_high
            results.append({"cmd": cmd[-1], "ok": ok,
                            "notice": "" if has_high else "medium 级告警放行（见日报待人工）"})
        else:
            results.append({"cmd": cmd[-1], "ok": ok})
        gate = gate and ok
    return {"gate": gate, "suites": results}


def phase_metrics() -> Dict[str, Any]:
    """B 活指标（确定性零 LLM）：topics 进度 / 调用健康 / BUG 速率。"""
    out: Dict[str, Any] = {}

    # 1) topics 分布 + needs_human
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        from topic_pipeline import state as tstate
        data = tstate.load_state()
        stages: Dict[str, int] = {}
        for rec in data.get("topics", {}).values():
            stages[rec.get("stage", "?")] = stages.get(rec.get("stage", "?"), 0) + 1
        out["topics"] = {
            "stages": stages,
            "total": sum(stages.values()),
            "rejected": len(data.get("rejected", {})),
        }
    except Exception as exc:
        out["topics"] = {"error": str(exc)[:120]}

    # 2) 调用健康（当月 step_usage，最近 7 天窗口）
    try:
        month = now_utc()[:7]
        path = PROJECT_ROOT / "memory" / "usage" / f"step-usage-{month}.jsonl"
        import json as _json
        total = failed = 0
        top: Dict[str, int] = {}
        cutoff = (date.today() - timedelta(days=7)).isoformat()
        if path.exists():
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                try:
                    rec = _json.loads(line)
                except Exception:
                    continue
                if str(rec.get("ts", ""))[:10] < cutoff:
                    continue
                total += 1
                if not rec.get("success"):
                    failed += 1
                    key = f"{rec.get('kind','?')}:{rec.get('name','?')}｜{str(rec.get('error',''))[:36]}"
                    top[key] = top.get(key, 0) + 1
        out["call_health"] = {
            "total": total, "failed": failed,
            "failure_rate": round(failed / total * 100, 1) if total else 0.0,
            "top_failures": sorted(top.items(), key=lambda x: -x[1])[:3],
        }
    except Exception as exc:
        out["call_health"] = {"error": str(exc)[:120]}

    # 3) BUG 速率（近 7 天 CHANGELOG BUG-N 提及，按编号去重）
    try:
        text = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        sections = re.split(r"## (v[\d.]+) - (\d{4}-\d{2}-\d{2})", text)
        bugs: set = set()
        for i in range(1, len(sections), 3):
            d = sections[i + 1]
            if d >= cutoff:
                bugs |= set(re.findall(r"BUG-\d+", sections[i + 2]))
        out["bug_velocity"] = {"per_day": round(len(bugs) / 7, 2), "count": len(bugs)}
    except Exception as exc:
        out["bug_velocity"] = {"error": str(exc)[:120]}
    return out


def _worklist_items(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    def add(source: str, action: str, detail: str) -> None:
        items.append({"source": source, "action": action, "detail": detail,
                      "raised_at": now_utc(), "status": "pending"})

    call = metrics.get("call_health") or {}
    if call.get("failure_rate", 0) > 15:
        add("call_health", "排查调用失败链",
            f"失败率 {call['failure_rate']}% 超阈值 15%；TOP {call.get('top_failures')}")
    bug = metrics.get("bug_velocity") or {}
    if bug.get("per_day", 0) > 0.5:
        add("bug_velocity", "复杂度预算复核",
            f"BUG 速率 {bug['per_day']}/天 超阈值 0.5；近 7 天 {bug.get('count')} 个")
    return items


def phase_worklist(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """C 工单追加去重（签名）+ 7 天关闭抑制（沿用 v7.2.76 语义）。"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with file_lock("self-optimize-worklist"):
        data = load_json(WORKLIST_PATH, default={"items": []})
        existing = {f"{i.get('source')}|{i.get('action')}"
                    for i in data.get("items", []) if i.get("status") == "pending"}
        for i in data.get("items", []):
            if i.get("status") == "done" and i.get("closed_at"):
                m = re.match(r"(\d{4}-\d{2}-\d{2})", str(i["closed_at"]))
                if m:
                    try:
                        cd = date(*map(int, m.group(1).split("-")))
                        if date.today() - cd < timedelta(days=7):
                            existing.add(f"{i.get('source')}|{i.get('action')}")
                    except Exception:
                        pass
        added = 0
        for item in _worklist_items(metrics):
            sig = f"{item['source']}|{item['action']}"
            if sig not in existing:
                data["items"].append(item)
                existing.add(sig)
                added += 1
        data["updated_at"] = now_utc()
        save_json(WORKLIST_PATH, data)
    return {"added": added}


def phase_ledger(benchmark: Dict[str, Any]) -> Dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with file_lock("self-optimize-ledger"):
        ledger = load_json(LEDGER_PATH, default={"sessions": [], "pilots": []})
        ledger["sessions"].append({"at": now_utc(),
                                   "benchmark_gate": benchmark.get("gate")})
        ledger["sessions"] = ledger["sessions"][-90:]
        save_json(LEDGER_PATH, ledger)
    return {"recorded": True}


def run_daily() -> Dict[str, Any]:
    benchmark = phase_benchmark()
    metrics = phase_metrics()
    wl = (phase_worklist(metrics) if benchmark.get("gate")
          else {"added": 0, "skipped": "基准门红，本日不发提案"})
    phase_ledger(benchmark)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORT_DIR / f"daily-{now_utc()[:10]}.md"
    lines = [f"# 治理日报（v8 工作台）{now_utc()[:10]}", "",
             f"- 基准门：{'✓ 绿' if benchmark.get('gate') else '✗ 红（禁止变更实施）'}",
             f"- 工单新增：{wl.get('added', 0)} 条"]
    for key, val in metrics.items():
        lines.append(f"- {key}: {val}")
    report.write_text("\n".join(lines), encoding="utf-8")
    return {"benchmark": benchmark.get("gate"), "metrics": metrics,
            "worklist": wl, "report": str(report)}


def _self_check() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        global WORKLIST_PATH, LEDGER_PATH, REPORT_DIR
        old = (WORKLIST_PATH, LEDGER_PATH, REPORT_DIR)
        WORKLIST_PATH, LEDGER_PATH, REPORT_DIR = (Path(td) / "w.json",
                                                  Path(td) / "l.json", Path(td))
        metrics = {"call_health": {"failure_rate": 46.4, "top_failures": [["glm:429", 90]]},
                   "bug_velocity": {"per_day": 0.2}}
        w1 = phase_worklist(metrics)
        w2 = phase_worklist(metrics)
        assert w1["added"] == 1 and w2["added"] == 0, (w1, w2)
        # 7 天抑制：关闭后 7 天内同签名不重提
        with file_lock("self-optimize-worklist"):
            data = load_json(WORKLIST_PATH)
            data["items"][0]["status"] = "done"
            data["items"][0]["closed_at"] = now_utc()
            save_json(WORKLIST_PATH, data)
        assert phase_worklist(metrics)["added"] == 0
        phase_ledger({"gate": True})
        assert (Path(td) / "l.json").exists()
        WORKLIST_PATH, LEDGER_PATH, REPORT_DIR = old
    print("✓ workbench_governance 自检通过")


if __name__ == "__main__":
    import json
    if "--self-check" in sys.argv:
        _self_check()
    elif "--run" in sys.argv:
        print(json.dumps(run_daily(), ensure_ascii=False, indent=2, default=str))
    else:
        print(__doc__)
