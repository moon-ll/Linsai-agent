"""A 通道收分口径（v7.3.41）

背景：
    section_4d 综合分在写入 score_history 前会依次经过表达质量天花板
    （expression_quality_ceiling）与综合天花板（overall_ceiling）两级 cap。
    后者按「表达质量（含无 AI 写作痕迹）」给总分封顶（<0.9 → ≤0.85），
    等于用文风一票否决科学质量：全库 409 份章节评审中 39.1% 被压到 ≤0.85，
    A 通道（5 模块各自 ≥0.90）因此在统计上不可达。

本模块把「验收判定分」与「总评展示分」拆成两个口径：
    - display（score）：保留 cap 后值，用于看板、报告、总评展示与其它环节；
    - gate（score_raw）：cap 前四维加权分（0.30/0.25/0.25/0.20），仅用于 A 通道判定。

开关：
    LINSAI_A_GATE_RAW_SCORE 默认 on（未设置/1/true/on 均视为开启）；
    置 0/false/off 回退旧口径（gate = display），可一键还原。

用法示例：
    >>> from proposal_lifecycle.a_gate import calibers, gate_score
    >>> calibers(0.85, 0.90)
    {'display': 0.85, 'gate': 0.90, 'caliber': 'raw'}
    >>> gate_score(0.85, 0.90)  # 开关关闭时返回 0.85
    0.90
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

A_GATE_RAW_ENV = "LINSAI_A_GATE_RAW_SCORE"
# v7.3.42: A 通道从"5 模块全过自动晋级"改为"任一模块达标 → 专家评审提醒"
PANEL_PROMPT_ENV = "LINSAI_A_GATE_PANEL_PROMPT"
PANEL_PROMPT_FLOOR = 0.85
_OFF_VALUES = ("0", "false", "off", "no")


def panel_prompt_enabled(env: Optional[Dict[str, str]] = None) -> bool:
    """A 通道是否启用"达标即提醒专家评审"（默认开）。"""
    environ = os.environ if env is None else env
    return str(environ.get(PANEL_PROMPT_ENV, "1")).strip().lower() not in _OFF_VALUES


def _unresolved_blocking(prop_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """未解决的 critical/high 问题（stale 与已闭环的排除）。"""
    out = []
    for e in prop_state.get("open_critical_issues") or []:
        if not isinstance(e, dict):
            continue
        if e.get("round_resolved") is not None or e.get("stale"):
            continue
        if (e.get("severity") or "").lower() in ("critical", "high"):
            out.append(e)
    return out


def _report_path(prop_state: Dict[str, Any], section: str, round_num: Any,
                 proposal_id: Optional[str] = None) -> str:
    """命中模块对应的评审报告路径（不存在时给目录级路径）。"""
    pid = proposal_id or prop_state.get("proposal_id") or ""
    status = prop_state.get("status") or "optimizing"
    root = Path(__file__).resolve().parents[2] / "research_proposals"
    pdir = root / status / pid
    if not pdir.exists():
        for sub in ("optimizing", "pending_review", "archived", "drafts"):
            if (root / sub / pid).exists():
                pdir = root / sub / pid
                break
    rev = pdir / "05_review"
    try:
        n = int(round_num)
    except (TypeError, ValueError):
        n = 0
    if n > 0:
        tagged = rev / f"critic-round-{n}-{section}.md"
        if tagged.exists():
            return str(tagged)
        bare = rev / f"critic-round-{n}.md"
        if bare.exists() and section == "full_review":
            return str(bare)
    return str(rev)


def evaluate_panel_prompt(prop_state: Dict[str, Any],
                          sections: Sequence[str],
                          floor: float = PANEL_PROMPT_FLOOR,
                          enabled: Optional[bool] = None,
                          proposal_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """任一模块判定分 ≥ floor 且无 critical/high → 返回提醒条目；否则 None。

    只做判定，不写状态——写入由调用方负责（便于开关关闭时零副作用）。
    """
    if enabled is None:
        enabled = panel_prompt_enabled()
    if not enabled:
        return None
    if _unresolved_blocking(prop_state):
        return None
    hist = prop_state.get("score_history") or []
    best = None
    for s in sections:
        mg = module_gate_score(hist, s)
        if not mg["found"] or mg["gate"] < floor:
            continue
        if best is None or mg["gate"] > best["score"]:
            best = {"module": s, "score": round(mg["gate"], 3),
                    "display": round(mg["display"], 3), "round": mg["round"]}
    if not best:
        return None
    best["report_path"] = _report_path(prop_state, best["module"], best["round"],
                                       proposal_id=proposal_id)
    best["floor"] = floor
    return best


def raw_gate_enabled(env: Optional[Dict[str, str]] = None) -> bool:
    """A 通道是否使用 cap 前原始分（默认开）。

    Args:
        env: 可注入的环境字典（测试用），缺省读 os.environ。
    """
    environ = os.environ if env is None else env
    return str(environ.get(A_GATE_RAW_ENV, "1")).strip().lower() not in _OFF_VALUES


def calibers(score_display: float, score_raw: Optional[float] = None,
             enabled: Optional[bool] = None) -> Dict[str, Any]:
    """拆分两个口径：display 永远保留 cap 后值，gate 按开关取原始分。

    Args:
        score_display: cap 后的综合分（score_after / score_history["score"]）。
        score_raw: cap 前的四维加权分（score_history["score_raw"]），缺失则回落 display。
        enabled: 覆盖开关（None 读环境变量）。

    Returns:
        {"display": float, "gate": float, "caliber": "raw"|"display"}
    """
    on = raw_gate_enabled() if enabled is None else bool(enabled)
    display = float(score_display or 0.0)
    if on and score_raw is not None:
        try:
            return {"display": display, "gate": float(score_raw), "caliber": "raw"}
        except (TypeError, ValueError):
            pass
    return {"display": display, "gate": display, "caliber": "display"}


def gate_score(score_display: float, score_raw: Optional[float] = None,
               enabled: Optional[bool] = None) -> float:
    """仅取验收判定分（便捷函数）。"""
    return calibers(score_display, score_raw, enabled)["gate"]


def section_gate_passed(score_display: float, score_raw: Optional[float],
                        min_score: float, weak_dims: Iterable[str] = (),
                        enabled: Optional[bool] = None) -> bool:
    """A 通道单模块判定：判定分 ≥ 门槛且无短板维度。"""
    return gate_score(score_display, score_raw, enabled) >= min_score and not list(weak_dims)


def module_gate_score(score_history: Sequence[Dict[str, Any]], section: str,
                      enabled: Optional[bool] = None) -> Dict[str, Any]:
    """从 score_history 取某模块最近一条非残缺记录，返回判定口径。

    Returns:
        {"found": bool, "gate": float, "display": float, "caliber": str,
         "round": int|None, "dim_scores": dict}
    """
    if enabled is None:
        enabled = raw_gate_enabled()
    for h in reversed(list(score_history or [])):
        if h.get("focus_section") != section or h.get("dims_partial"):
            continue
        try:
            display = float(h.get("score", 0.0))
        except (TypeError, ValueError):
            continue
        raw = h.get("score_raw")
        # references / method_manual 为 2 维专用口径，score_raw 是 2 维重算
        # 之前的四维占位值，不可用于该模块判定——回落 cap 后 display。
        if h.get("caliber") != "section_4d" or section == "method_manual":
            raw = None
        c = calibers(display, raw, enabled)
        return {
            "found": True,
            "gate": c["gate"],
            "display": c["display"],
            "caliber": c["caliber"],
            "round": h.get("round"),
            "dim_scores": h.get("dim_scores") or {},
        }
    return {"found": False, "gate": 0.0, "display": 0.0,
            "caliber": "display", "round": None, "dim_scores": {}}
