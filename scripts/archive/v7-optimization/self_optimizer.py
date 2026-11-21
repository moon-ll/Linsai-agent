#!/usr/bin/env python3
"""自迭代每日编排器（v7.2.65，lc-self-optimize 16:30）。

架构依据（用户裁决 2026-10-31 + 外部对标 DGM/DSPy/Voyager）：主链只留
只读观测与 prompt 注入（复发升级/校准采样）；一切「变异」（prompt/skill/
调度/门槛）集中到本窗口，过三道闸：基准门 → 单课题试点 → 台账采纳/回滚。
本版实现 A/B/C/D 四相的确定性骨架，零 LLM、零自动应用。

四相：
  A 摘要：retrospective 活账本五指标 + 判据校准审计 + glm 空响应计数
  B 基准门：关键回归套件全绿才允许任何变异进入试点（DGM 式准入）
  C 提案：⚠ 指标 → memory/self-optimize/worklist.json（ZCode/人工消费，
    v7.0.7 先例：升级类任务由 ZCode 执行，不自动 apply）
  D 台账：adoption-ledger.json 试点/采纳/回滚状态机（本版建骨架）

用法：
    python3 scripts/self_optimizer.py --run          # 每日 16:30 cron 入口
    python3 scripts/self_optimizer.py --self-check
"""

from __future__ import annotations

import subprocess
import sys
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

# 基准门套件（全绿 = 变异准入前提；控制在 ~5 分钟内）
BENCHMARK_SUITES: List[List[str]] = [
    [sys.executable, str(SCRIPTS_DIR / "review_dossier.py"), "--self-check"],
    [sys.executable, str(SCRIPTS_DIR / "tests" / "test_params_registry.py")],
    [sys.executable, str(SCRIPTS_DIR / "tests" / "test_retrospective_live.py")],
    [sys.executable, str(SCRIPTS_DIR / "tests" / "test_auto_acceptance.py")],
]


def phase_digest() -> Dict[str, Any]:
    """A 相：汇集活账本指标 + 判据校准审计（只读）。"""
    out: Dict[str, Any] = {}
    try:
        from retrospective import _analyze_live_ledgers
        out["live"] = _analyze_live_ledgers(period_days=7)
    except Exception as exc:
        out["live"] = {"error": str(exc)}
    try:
        from review_dossier import audit_criteria_calibration
        out["calibration"] = audit_criteria_calibration()
    except Exception as exc:
        out["calibration"] = {"error": str(exc)}
    return out


def phase_benchmark() -> Dict[str, Any]:
    """B 相：基准门。任一套件失败 → gate=False（本日禁止一切变异试点）。"""
    results = []
    gate = True
    for cmd in BENCHMARK_SUITES:
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600, cwd=str(PROJECT_ROOT))
            ok = proc.returncode == 0
        except Exception as exc:
            ok, proc = False, None
            results.append({"cmd": cmd[-1], "ok": False, "error": str(exc)})
            gate = False
            continue
        results.append({"cmd": cmd[-1], "ok": ok})
        gate = gate and ok
    return {"gate": gate, "suites": results}


def _worklist_items(digest: Dict[str, Any]) -> List[Dict[str, Any]]:
    """C 相：由 ⚠ 指标确定性生成提案条目（不自动应用）。"""
    items: List[Dict[str, Any]] = []

    def add(source: str, action: str, detail: str) -> None:
        items.append({"source": source, "action": action, "detail": detail,
                      "raised_at": now_utc(), "status": "pending"})

    live = (digest.get("live") or {})
    call = live.get("call_health") or {}
    _fr = call.get("failure_rate")
    # v7.2.70: 失败率口径兼容——retrospective 存的是百分数（24.3），
    # 防御性归一：>1 视为已是百分数，否则视为分数×100。旧版对 24.3
    # 再做 .1% 换算 → 工单详情显示 "2430.0%"（显示 bug）。
    if _fr is not None:
        _pct = _fr if _fr > 1 else _fr * 100
        if _pct > 15:
            add("call_health", "排查 llm_router 降级链",
                f"失败率 {_pct:.1f}% 超阈值 15%；TOP 失败 {call.get('top_failures')}")
    bug = live.get("bug_velocity") or {}
    if bug.get("bug_velocity_per_day") is not None and bug["bug_velocity_per_day"] > 0.5:
        add("bug_velocity", "复杂度预算复核",
            f"BUG 速率 {bug['bug_velocity_per_day']:.2f}/天 超阈值 0.5；近 7 天 {bug.get('bugs_fixed_in_period')} 个")
    cal = digest.get("calibration") or {}
    if cal.get("status") == "recalibrate":
        add("criteria_calibration", "判据重校评估",
            cal.get("suggestion", ""))
    return items


def phase_worklist(digest: Dict[str, Any]) -> Dict[str, Any]:
    """C 相：worklist 追加去重（按 source+action 签名）。

    v7.2.76: 7 天关闭抑制——同一签名工单 7 天内已 done 的不再重提
    （实测：call_health 工单 10-31 关闭、11-01 因 7 天回溯窗含爆发期
    又重开——指标是滞后窗口，修复已生效也会再触发；由 closed_at 判定）。
    """
    import re as _re
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with file_lock("self-optimize-worklist"):
        data = load_json(WORKLIST_PATH, default={"items": []})
        existing = {
            f"{i.get('source')}|{i.get('action')}"
            for i in data.get("items", []) if i.get("status") == "pending"
        }
        # 7 天内关闭的同签名 → 抑制重提
        _now = now_utc()
        for i in data.get("items", []):
            if i.get("status") == "done" and i.get("closed_at"):
                m = _re.match(r"(\d{4}-\d{2}-\d{2})", str(i["closed_at"]))
                if m and (_now[:10] >= m.group(1)):
                    _closed_date = m.group(1)
                    try:
                        from datetime import date, timedelta
                        _cd = date(*map(int, _closed_date.split("-")))
                        if date(*map(int, _now[:10].split("-"))) - _cd < timedelta(days=7):
                            existing.add(f"{i.get('source')}|{i.get('action')}")
                    except Exception:
                        pass
        added = 0
        for item in _worklist_items(digest):
            sig = f"{item['source']}|{item['action']}"
            if sig not in existing:
                data["items"].append(item)
                existing.add(sig)
                added += 1
        data["updated_at"] = now_utc()
        save_json(WORKLIST_PATH, data)
    return {"added": added, "total_pending":
            len([i for i in load_json(WORKLIST_PATH, default={"items": []})["items"]
                 if i.get("status") == "pending"])}


def phase_ledger(benchmark: Dict[str, Any], worklist: Dict[str, Any]) -> Dict[str, Any]:
    """D 相：台账——记录会话结论 + 试点状态机（v7.2.66 扩展）。

    试点状态机（环② A/B 门，DGM 式准入）：
      pending → piloting（基准门绿 + 指定试点课题）→ adopted / rolled_back
      规则：① 基准门红时禁止进入 piloting；② 试点记录绑定 proposal 与
      起始轮，供后续按「同类问题消长」裁决；③ 全程零自动应用——
      prompt_optimizer 污染 SOUL（净 -27 分）的教训制度化。
    """
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with file_lock("self-optimize-ledger"):
        ledger = load_json(LEDGER_PATH, default={"sessions": [], "pilots": []})
        ledger["sessions"].append({
            "at": now_utc(),
            "benchmark_gate": benchmark.get("gate"),
            "worklist_added": worklist.get("added"),
        })
        ledger["sessions"] = ledger["sessions"][-90:]
        # 状态机迁移：pending 项在基准门绿时可被外部（ZCode/人工）标记
        # piloting——此处只做守卫校验，不做自动晋升。
        for pilot in ledger.get("pilots", []):
            if pilot.get("status") == "piloting" and not benchmark.get("gate"):
                pilot["status"] = "rolled_back"
                pilot["reason"] = "基准门转红，自动回滚试点"
                # v7.3.59（批次 B）：同步关变体记分卡（outcome=reverted，
                # variant 快照入卡）——基准门红的回滚也是一次带指标的
                # 变体评估，不丢证据。fail-open。
                _scid = pilot.get("scorecard_id")
                if _scid:
                    try:
                        from pilot_scorecard import close_scorecard
                        close_scorecard(_scid, "reverted",
                                        reason="基准门转红，自动回滚试点")
                    except Exception:
                        pass
        ledger["updated_at"] = now_utc()
        save_json(LEDGER_PATH, ledger)
    return {"recorded": True}


def promote_pilot(source: str, action: str, proposal_id: str, round_start: int) -> Dict[str, Any]:
    """CLI/外部入口：把 worklist 提案晋升为试点（基准门守卫内建）。

    v7.3.59（批次 B·SICA 变体谱系）：晋升时自动开变体记分卡——base 指标
    快照 + 谱系（默认父 = 同源最近 adopted），scorecard_id 回写 ledger 试点
    条目；裁决试点结局时用 scorecard.close 量化 base/variant 指标对。
    fail-open：记分卡故障不阻断试点晋升。
    """
    bench = phase_benchmark()
    if not bench.get("gate"):
        return {"success": False, "error": "基准门未过，禁止试点"}
    scorecard_id = None
    try:
        from pilot_scorecard import open_scorecard
        sc = open_scorecard(source, action, proposal_id, round_start)
        if sc.get("success"):
            scorecard_id = sc.get("scorecard_id")
    except Exception:
        pass  # fail-open：记分卡层故障不影响试点状态机
    with file_lock("self-optimize-ledger"):
        ledger = load_json(LEDGER_PATH, default={"sessions": [], "pilots": []})
        ledger.setdefault("pilots", []).append({
            "source": source, "action": action,
            "proposal_id": proposal_id, "round_start": round_start,
            "status": "piloting", "at": now_utc(),
            "scorecard_id": scorecard_id,
        })
        save_json(LEDGER_PATH, ledger)
    with file_lock("self-optimize-worklist"):
        wl = load_json(WORKLIST_PATH, default={"items": []})
        for it in wl["items"]:
            if it.get("source") == source and it.get("action") == action \
                    and it.get("status") == "pending":
                it["status"] = "piloting"
        save_json(WORKLIST_PATH, wl)
    return {"success": True, "scorecard_id": scorecard_id}


def run_daily() -> Dict[str, Any]:
    digest = phase_digest()
    benchmark = phase_benchmark()
    worklist = phase_worklist(digest) if benchmark.get("gate") else {"added": 0, "skipped": "基准门未过，本日不发提案"}
    phase_ledger(benchmark, worklist)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = REPORT_DIR / f"daily-{now_utc()[:10]}.md"
    lines = [f"# 自迭代日报 {now_utc()[:10]}", "",
             f"- 基准门：{'✓ 绿' if benchmark.get('gate') else '✗ 红（禁止变异试点）'}",
             f"- 提案新增：{worklist.get('added', 0)} 条（待消费 {worklist.get('total_pending', '?')}）",
             f"- 判据校准：{(digest.get('calibration') or {}).get('status', '?')}",
             "", "## 活指标速览", ""]
    for key, val in (digest.get("live") or {}).items():
        lines.append(f"- {key}: {val}")
    report.write_text("\n".join(lines), encoding="utf-8")
    return {"benchmark": benchmark.get("gate"), "report": str(report), "worklist": worklist}


def _self_check() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        global WORKLIST_PATH, LEDGER_PATH, REPORT_DIR
        old_w, old_l, old_r = WORKLIST_PATH, LEDGER_PATH, REPORT_DIR
        WORKLIST_PATH = Path(td) / "worklist.json"
        LEDGER_PATH = Path(td) / "ledger.json"
        REPORT_DIR = Path(td)
        digest = {"live": {"call_health": {"failure_rate": 0.243,
                                           "top_failures": [["glm:空响应", 218]]},
                           "bug_velocity": {"bug_velocity_per_day": 1.57, "bugs_fixed_in_period": 11}},
                  "calibration": {"status": "insufficient_samples"}}
        w1 = phase_worklist(digest)
        w2 = phase_worklist(digest)  # 幂等：同签名不重复入列
        assert w1["added"] == 2 and w2["added"] == 0, (w1, w2)
        phase_ledger({"gate": True}, w1)
        assert (Path(td) / "ledger.json").exists()
        WORKLIST_PATH, LEDGER_PATH, REPORT_DIR = old_w, old_l, old_r
    print("✓ self_optimizer 自检通过")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        _self_check()
    elif "--promote-pilot" in sys.argv:
        # v7.2.95: 补 promote_pilot CLI 入口（healthcheck v71 焦点⑧——函数标注
        # "CLI/外部入口" 却未暴露，试点晋升侧永远进不去）
        import json
        idx = sys.argv.index("--promote-pilot")
        vals = sys.argv[idx + 1: idx + 5]
        if len(vals) < 4:
            print(json.dumps({"error": "用法: --promote-pilot SOURCE ACTION PROPOSAL_ID ROUND_START"}, ensure_ascii=False))
        else:
            print(json.dumps(promote_pilot(vals[0], vals[1], vals[2], int(vals[3])), ensure_ascii=False, indent=2, default=str))
    elif "--run" in sys.argv:
        import json
        print(json.dumps(run_daily(), ensure_ascii=False, indent=2, default=str))
    else:
        print(__doc__)
