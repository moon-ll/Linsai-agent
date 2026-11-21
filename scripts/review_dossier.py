#!/usr/bin/env python3
"""验收决策包生成器（v6.9.0 R1）。

课题晋级 pending_review 时自动生成"验收决策包"（review-dossier.md），
把人工验收从"从头读完申请书"变成"核验一页摘要"：

  - 分数曲线 + 维度分 + 各模块通过状态
  - 未解决问题清单（按严重度）
  - 与上一轮的 diff 摘要（增删行数 + 变化量）
  - 参考文献校验结论（最近一轮 references 结果）
  - 规则预审结论：approve_lean / attention / reject_lean + 依据

预审为确定性规则（零成本、可测试、不依赖 LLM）。审核会话注入决策包
而非原文节选；approve_lean 且最新分 >= 0.85 时控制台提供"一键采纳预审"。

用法：
    python3 scripts/review_dossier.py --generate <proposal_id>
    python3 scripts/review_dossier.py --summary <proposal_id>
    python3 scripts/review_dossier.py --self-check
"""

from __future__ import annotations

import argparse
import difflib
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common import load_json, now_utc, save_json  # noqa: E402
from paths import PROJECT_ROOT  # noqa: E402

try:
    from logger import get_logger
    _log = get_logger("review_dossier")
except Exception:  # pragma: no cover
    _log = None

from proposal_lifecycle import ProposalLifecycle  # noqa: F401  保留给调用方复用
from proposal_lifecycle.constants import PROPOSALS_ROOT  # noqa: E402

from lifecycle.utils import find_proposal_dir  # noqa: E402

# 评审模块全集（v7.3.0 起为 6 模块：申请书正文 5 + 方法手册）
from proposal_sections import REVIEW_SECTION_KEYS  # noqa: E402

SECTION_ORDER: List[str] = list(REVIEW_SECTION_KEYS)
SECTION_NAMES: Dict[str, str] = {
    "rationale": "立项依据",
    "content": "研究内容",
    "scheme": "研究方案（含创新与成果）",
    "full_review": "整篇一致性",
    "references": "参考文献",
    "method_manual": "方法手册（开工就绪度）",
}

APPROVE_SCORE_GATE = 0.85
"""一键采纳预审的分数门槛：approve_lean 且最新分 >= 0.85 才允许。

注意：自动达标晋级门槛（DEFAULT_SCORE_THRESHOLD）为 0.90，达到即自动
晋级；0.85 是"人工可快速采纳"的宽松线，低于它的任何课题都值得细读。"""

# v7.2.61 判据换轨（瓶颈诊断 2026-10-30 定案 2 灰度）：绝对分数线从
# 一键采纳守卫退役，改为「问题活口径 + monitor 独立分 + 可执行性」双门。
# 依据：0.9 免检线 3 个月 0 触发（四层 cap 下数学不可达）、账本
# open_critical_issues 修复不销账（ssh-weyl monitor 0.91 被陈账判
# reject_lean）、monitor 与 critic 相关性 r≈0。
MONITOR_ADOPT_GATE = 0.80
"""一键采纳的 monitor 独立分门槛（活口径信号，不受程序 cap）。"""

EXECUTABILITY_ADOPT_GATE = 0.75
"""一键采纳的可执行性门槛（monitor v7.2.0 口径：≥0.75 表示可直接执行）。"""

REJECT_SCORE_GATE = 0.75
"""预审退回线：最新评分低于此值直接建议 reject_lean。"""

VERDICT_APPROVE = "approve_lean"
VERDICT_ATTENTION = "attention"
VERDICT_REJECT = "reject_lean"


# ---------------------------------------------------------------------------
# 纯函数：预审规则
# ---------------------------------------------------------------------------


def last_entry_per_section(score_history: List[Dict[str, Any]]) -> Dict[str, Dict]:
    """每个模块取最近一次轮次记录（focus_section 维度）。"""
    result: Dict[str, Dict] = {}
    for entry in score_history or []:
        section = entry.get("focus_section")
        if section in SECTION_ORDER:
            result[section] = entry
    return result


def _manual_not_ready_reason(manual_entry: Optional[Dict]) -> str:
    """v7.3.0: 手册未过线的可读原因（供预审 reasons 与人工队列展示）。"""
    if not manual_entry:
        return (
            "方法手册从未评审（无 method_manual 轮次记录），"
            "课题尚不可正式开工"
        )
    level = manual_entry.get("manual_readiness_level")
    level_txt = f"L{level}" if isinstance(level, (int, float)) else "未知级"
    return (
        f"方法手册未达开工就绪（{level_txt}，分 "
        f"{float(manual_entry.get('score', 0.0) or 0.0):.2f}），"
        f"课题尚不可正式开工"
    )


def compute_pre_review(
    prop_state: Dict[str, Any],
    reject_gate: float = REJECT_SCORE_GATE,
    approve_gate: float = APPROVE_SCORE_GATE,
) -> Dict[str, Any]:
    """规则预审：approve_lean / attention / reject_lean + 依据。

    v7.2.61 判据换轨（灰度第一批）：**monitor 活口径优先**。

    背景：账本 open_critical_issues 只在 critic 轮维护——评审团/manual
    修订/R9 处置等修复渠道绕过 critic 轮，修复不销账（实测 ssh-weyl
    monitor 活口径高危 2、账本挂 14+1 条全部陈账，预审被陈账误判
    reject_lean）。故当 monitor_history 存在时，以 monitor 末条
    high_issues_after 为活口径主锚，账本降级为参考明细（供人工核验）。

    判定顺序（monitor 活口径存在时）：
      1. 活口径高危 >= 3 → reject_lean
      2. 活口径高危 1-2 → attention（附账本差异说明）
      3. 存在近 2 轮内未销账 critical → attention（保守）
      4. monitor 独立分 >= 0.80 且可执行性 >= 0.75 且活口径高危 0
         → approve_lean
      5. 其余 → attention

    无 monitor 活口径时回退旧账本规则（先命中先返回）：
      1. 存在未解决高危问题 → reject_lean
      2. 通过模块数 <= 2 → reject_lean
      3. 无 monitor 评分 → attention
      4. 带质量警告晋级 → attention
      5. 最新评分 < reject_gate → reject_lean
      6. 5/5 模块通过 + 无未解决问题 + 分数 >= approve_gate → approve_lean
      7. 其余 → attention
    """
    history = prop_state.get("score_history") or []
    section_map = last_entry_per_section(history)
    passed = {k for k, e in section_map.items() if e.get("section_passed")}
    passed_count = len(passed)

    # v7.3.0: 方法手册开工就绪门——手册未过线（L<3 或 2 维分 <0.85 或有
    # critical/high 缺口）的课题不可"建议通过"，一键采纳同步禁用。
    # 用户裁决（2026-11-02）：手册的详细程度与完整度决定课题能否正式开工。
    _manual_entry = section_map.get("method_manual")
    manual_ready = bool(_manual_entry and _manual_entry.get("section_passed"))

    # 未解决问题（open_critical_issues 中未被标记 stale/已解决的）
    unresolved = [
        i
        for i in (prop_state.get("open_critical_issues") or [])
        if isinstance(i, dict) and not i.get("stale") and not i.get("round_resolved")
    ]
    high_issues = [i for i in unresolved if str(i.get("severity", "")) == "high"]
    critical_issues = [i for i in unresolved if str(i.get("severity", "")) == "critical"]
    last_score = prop_state.get("last_monitor_score")
    if last_score is None and history:
        # v6.10.27: 回退取最近一条章节 4 维口径分（排除 references 2 维
        # 收尾分），避免把引用审校分当整篇分做预审门槛（旧逻辑取
        # history[-1]，每轮 references 收尾时拿到 2 维分）。
        # v7.3.0: method_manual 同为 2 维异口径，一并排除。
        for h in reversed(history):
            if h.get("focus_section") not in ("references", "method_manual"):
                last_score = h.get("score")
                break

    # v7.2.61: monitor 活口径（末条 monitor_history）
    monitor_hist = prop_state.get("monitor_history") or []
    last_mon = (
        monitor_hist[-1]
        if monitor_hist and isinstance(monitor_hist[-1], dict)
        else {}
    )
    live_high = last_mon.get("high_issues_after")
    live_high = int(live_high) if isinstance(live_high, (int, float)) else None
    monitor_exec = last_mon.get("executability_score")
    monitor_exec = float(monitor_exec) if isinstance(monitor_exec, (int, float)) else None
    rounds = int(prop_state.get("optimization_rounds", 0) or 0)
    recent_critical = [
        i
        for i in critical_issues
        if (i.get("last_seen_round") or 0) >= rounds - 1
    ]

    # v7.2.103 数据陈旧度闸门：monitor 末条 `at` 早于课题最近状态变更
    # （updated_at——亲审收尾/评审团修复/adopt 等任何状态写均刷新它）时，
    # 活口径锚描述的是修复前的文本。当日实测（2026-11-01）：houston 的
    # reject_lean 基于 13 天前 monitor 数据、order-parameter 基于 26 天前，
    # 而亲审修复均在其后。规则：陈旧时活口径驱动的 reject_lean 降为
    # attention 并附数据代际说明（保守：永不因陈旧判定反向升级 verdict）。
    data_vintage = None
    mon_at = last_mon.get("at") if last_mon else None
    upd_at = prop_state.get("updated_at")
    if mon_at and upd_at:
        try:
            mon_dt = datetime.fromisoformat(str(mon_at).replace("Z", "+00:00"))
            upd_dt = datetime.fromisoformat(str(upd_at).replace("Z", "+00:00"))
            if upd_dt > mon_dt:
                data_vintage = {
                    "stale": True,
                    "monitor_at": str(mon_at),
                    "state_updated_at": str(upd_at),
                    "lag_hours": round((upd_dt - mon_dt).total_seconds() / 3600.0, 1),
                }
        except ValueError:
            pass

    metrics = {
        "passed_modules": passed_count,
        "total_modules": len(SECTION_ORDER),
        "unresolved_issues": len(unresolved),
        "high_issues": len(high_issues),
        "critical_issues": len(critical_issues),
        "last_score": last_score,
        "quality_warning": prop_state.get("quality_warning"),
        "rounds": rounds,
        # v6.10.3 F2: 晋级方式标注——escape_* 为逃生阀晋级（非真达标），
        # all_sections_passed 为全模块对抗胜利晋级。决策包据此提示人工。
        "promotion_kind": prop_state.get("promotion_kind", ""),
        # v7.2.61: 活口径信号（供前端/审计区分账本口径与 monitor 口径）
        "live_high": live_high,
        "live_high_round": last_mon.get("round"),
        # v7.2.103: 数据陈旧度信号（monitor 末条早于状态变更时标记）
        "data_vintage": data_vintage,
        "monitor_executability": monitor_exec,
        # v7.3.0: 手册就绪信号（未过线 → 课题不可开工，verdict 封顶 attention）
        "manual_ready": manual_ready,
        "manual_readiness_level": (
            _manual_entry.get("manual_readiness_level")
            if _manual_entry else None
        ),
    }

    _PROMOTION_KIND_CN = {
        "escape_max_rounds": "逃生阀：达到最大轮数",
        "escape_no_improvement": "逃生阀：连续无提升",
        "quality_declining": "质量下降暂停",
        "all_sections_passed": "全模块对抗胜利",
        # v7.2.24 通道 B：验收线晋级（连续 3 轮 ≥0.82 无下降 + monitor
        # ≥0.80）——主晋级通道，转人工验收；标注供人工识别口径来源
        "acceptance_line": "验收线：稳定平台 + monitor 背书",
    }
    reasons: List[str] = []
    _pk = prop_state.get("promotion_kind") or ""
    if _pk in _PROMOTION_KIND_CN:
        # 逃生阀晋级时把晋级方式写进 reasons 首位（不改 verdict 规则，
        # 仅为人工提供"这不是达标晋级"的显式信号）
        reasons.insert(0, f"晋级方式：{_PROMOTION_KIND_CN[_pk]}")

    if live_high is not None:
        # v7.2.61 主路径：monitor 活口径优先
        if data_vintage and data_vintage.get("stale") and live_high >= 1:
            # v7.2.103 数据陈旧：高危计数描述修复前文本，reject_lean 降为
            # attention（保守——陈旧永不反向升级 verdict）
            verdict = VERDICT_ATTENTION
            reasons.append(
                f"monitor 活口径高危 {live_high}（R{last_mon.get('round', '?')}），"
                f"但 monitor 末条（{str(mon_at)[:16]}）早于最近状态变更"
                f"（{str(upd_at)[:16]}，滞后 {data_vintage['lag_hours']}h）——"
                f"活口径锚陈旧，判定降级为人工裁量；建议 monitor 复测或对照"
                f"引擎预判做文本级核验"
            )
        elif live_high >= 3:
            verdict = VERDICT_REJECT
            reasons.append(
                f"monitor 活口径高危 {live_high}（R{last_mon.get('round', '?')}）"
            )
        elif live_high >= 1:
            verdict = VERDICT_ATTENTION
            reasons.append(
                f"monitor 活口径高危 {live_high}（R{last_mon.get('round', '?')}），需人工裁量"
            )
        elif recent_critical:
            verdict = VERDICT_ATTENTION
            reasons.append(
                f"活口径高危 0，但账本存在近 2 轮内 critical "
                f"{len(recent_critical)} 条未销账，保守转人工核验"
            )
        elif critical_issues:
            verdict = VERDICT_ATTENTION
            reasons.append(
                f"活口径高危 0，但账本存在陈年 critical {len(critical_issues)} 条，请人工核验明细"
            )
        else:
            _mon_ok = last_score is not None and float(last_score) >= MONITOR_ADOPT_GATE
            _exec_ok = monitor_exec is not None and monitor_exec >= EXECUTABILITY_ADOPT_GATE
            if _mon_ok and _exec_ok and manual_ready:
                verdict = VERDICT_APPROVE
                reasons.append(
                    f"活口径高危 0，monitor 独立分 {float(last_score):.2f} ≥ "
                    f"{MONITOR_ADOPT_GATE}，可执行性 {monitor_exec:.2f} ≥ "
                    f"{EXECUTABILITY_ADOPT_GATE}，方法手册已过开工就绪门"
                )
            else:
                verdict = VERDICT_ATTENTION
                _why = []
                if not _mon_ok:
                    _why.append(
                        f"monitor 独立分 {float(last_score):.2f} < {MONITOR_ADOPT_GATE}"
                        if last_score is not None
                        else "缺少 monitor 独立分"
                    )
                if not _exec_ok:
                    _why.append(
                        f"可执行性 {monitor_exec:.2f} < {EXECUTABILITY_ADOPT_GATE}"
                        if monitor_exec is not None
                        else "缺少可执行性评分"
                    )
                if not manual_ready:
                    _why.append(_manual_not_ready_reason(_manual_entry))
                reasons.append("活口径高危 0，但" + "、".join(_why))
        if len(unresolved) > (live_high or 0) + 2:
            reasons.append(
                f"账本未销账 {len(unresolved)} 条（high {len(high_issues)} + "
                f"critical {len(critical_issues)}）——多为评审团/人工修订等修复"
                "渠道绕过 critic 轮所致，明细见下表，请以 monitor 活口径为准复核"
            )
    else:
        # 回退路径：无 monitor 活口径（老课题/monitor 缺失）——沿用旧账本规则
        if high_issues:
            verdict = VERDICT_REJECT
            reasons.append(f"存在 {len(high_issues)} 个未解决高危问题")
        elif critical_issues:
            verdict = VERDICT_REJECT
            reasons.append(f"存在 {len(critical_issues)} 个未解决 critical 问题")
        elif passed_count <= 2:
            verdict = VERDICT_REJECT
            reasons.append(f"仅通过 {passed_count}/{len(SECTION_ORDER)} 模块")
        elif last_score is None:
            verdict = VERDICT_ATTENTION
            reasons.append("缺少 monitor 独立评分")
        elif prop_state.get("quality_warning"):
            verdict = VERDICT_ATTENTION
            reasons.append(f"带质量警告晋级：{prop_state['quality_warning'][:80]}")
        elif float(last_score) < reject_gate:
            verdict = VERDICT_REJECT
            reasons.append(f"最新评分 {float(last_score):.2f} 低于门槛 {reject_gate}")
        elif (
            passed_count == len(SECTION_ORDER)
            and not unresolved
            and float(last_score) >= approve_gate
        ):
            verdict = VERDICT_APPROVE
            reasons.append(
                f"5/5 模块通过，无未解决问题，评分 {float(last_score):.2f} >= {approve_gate}"
            )
        else:
            verdict = VERDICT_ATTENTION
            reasons.append(
                f"通过 {passed_count}/{len(SECTION_ORDER)} 模块，"
                f"评分 {float(last_score):.2f}，需人工裁量"
            )

    metrics["unresolved_detail"] = [
        {
            "severity": str(i.get("severity", "")),
            "section": str(i.get("section", "")),
            "last_seen_round": i.get("last_seen_round"),
            "description": (i.get("description") or "")[:120],
        }
        for i in unresolved[:8]
    ]
    return {"verdict": verdict, "reasons": reasons, "metrics": metrics}


def can_adopt_pre_review(dossier: Optional[Dict[str, Any]]) -> bool:
    """一键采纳守卫（v7.2.61 换轨）。

    旧门：approve_lean 且 last_score >= 0.85（分数制）——上线以来零触发
    （死代码），因 0.85+ 分被程序 cap 结构性锁死。
    新门：approve_lean 且 monitor 独立分 >= 0.80 且可执行性 >= 0.75
    （活口径双门，与 compute_pre_review 主路径一致）。
    v7.3.0: 加手册门——manual_ready 为 False（手册未过开工就绪线）时
    禁止一键采纳（与 compute_pre_review 主路径的手册封顶一致，防御纵深）。
    """
    if not dossier:
        return False
    if dossier.get("pre_review_verdict") != VERDICT_APPROVE:
        return False
    metrics = dossier.get("metrics") or {}
    if dossier.get("manual_ready", metrics.get("manual_ready")) is False:
        return False
    monitor_score = dossier.get("monitor_score", dossier.get("last_score"))
    try:
        monitor_score = float(monitor_score or 0.0)
    except (TypeError, ValueError):
        return False
    if monitor_score < MONITOR_ADOPT_GATE:
        return False
    exec_score = dossier.get("executability_score")
    if exec_score is None:
        return False
    try:
        exec_score = float(exec_score)
    except (TypeError, ValueError):
        return False
    return exec_score >= EXECUTABILITY_ADOPT_GATE


# ---------------------------------------------------------------------------
# v7.2.62 环④：判据自校准（事件驱动——用户裁决落地即记样本）
# ---------------------------------------------------------------------------

CALIBRATION_PATH = PROJECT_ROOT / "memory" / "criteria-calibration.json"
CALIBRATION_MIN_SAMPLES = 5
CALIBRATION_ALERT_RATE = 0.70


def record_criteria_calibration(
    proposal_id: str, dossier_verdict: str, user_decision: str
) -> None:
    """用户裁决落地时记录校准样本（机器预审 vs 真实决定）。

    自迭代的 ground truth 通道：预审判据（活口径双门）是否可信，唯一
    检验是它与用户真实决定的一致率。旧设计按月审计（人类节拍）；改为
    事件驱动——每次 review-verdict / review-adopt 落地即追加样本，
    攒满 CALIBRATION_MIN_SAMPLES 条即可出审计结论（大模型节拍）。
    fail-open：记录失败绝不阻断验收流程。
    """
    try:
        from common import file_lock

        with file_lock("criteria-calibration"):
            data = load_json(CALIBRATION_PATH, default={"samples": []})
            data.setdefault("samples", []).append({
                "at": now_utc(),
                "proposal_id": proposal_id,
                "dossier_verdict": dossier_verdict,
                # approve / reject / pause（与 review-verdict 语义对齐）
                "user_decision": user_decision,
            })
            data["updated_at"] = now_utc()
            save_json(CALIBRATION_PATH, data)
    except Exception as exc:  # pragma: no cover
        if _log:
            _log.warning(f"[{proposal_id}] 判据校准样本记录失败: {exc}")


def audit_criteria_calibration() -> Dict[str, Any]:
    """审计机器预审与用户裁决的一致率；不达线则给出重校建议。

    判定矩阵（attention=交人工裁量，用户任意决定均不算预审错）：
      - attention ↔ 任意           → 一致
      - approve_lean ↔ approve     → 一致
      - reject_lean ↔ reject       → 一致
      - approve_lean ↔ reject / reject_lean ↔ approve → 硬错
    """
    data = load_json(CALIBRATION_PATH, default={"samples": []})
    samples = data.get("samples") or []
    n = len(samples)
    result: Dict[str, Any] = {"n": n, "agreement_rate": None,
                              "status": "insufficient_samples",
                              "mismatches": [], "suggestion": ""}
    if n < CALIBRATION_MIN_SAMPLES:
        result["suggestion"] = f"样本不足（{n}/{CALIBRATION_MIN_SAMPLES}），继续积累"
        return result
    agree = 0
    for s in samples:
        dv = str(s.get("dossier_verdict", ""))
        ud = str(s.get("user_decision", ""))
        if dv == VERDICT_ATTENTION or (
            (dv == VERDICT_APPROVE and ud == "approve")
            or (dv == VERDICT_REJECT and ud == "reject")
            or (dv not in (VERDICT_APPROVE, VERDICT_REJECT) and ud == "pause")
        ):
            agree += 1
        else:
            result["mismatches"].append({
                "at": s.get("at"),
                "proposal_id": s.get("proposal_id"),
                "dossier_verdict": dv,
                "user_decision": ud,
            })
    rate = agree / n
    result["agreement_rate"] = round(rate, 3)
    if rate >= CALIBRATION_ALERT_RATE:
        result["status"] = "healthy"
    else:
        result["status"] = "recalibrate"
        result["suggestion"] = (
            f"一致率 {rate:.0%} < {CALIBRATION_ALERT_RATE:.0%}（n={n}）——判据已被"
            "博弈或漂移，建议重校 MONITOR_ADOPT_GATE / EXECUTABILITY_ADOPT_GATE"
            "或活口径高危阈值；硬错样本见 mismatches"
        )
    return result


# ---------------------------------------------------------------------------
# diff 摘要
# ---------------------------------------------------------------------------


def summarize_draft_diff(proposal_dir: Optional[Path]) -> Optional[Dict[str, Any]]:
    """对比当前草稿与上一轮备份，返回增删行数摘要。"""
    if proposal_dir is None:
        return None
    draft_dir = proposal_dir / "04_proposal"
    current = draft_dir / "proposal-draft.md"
    if not current.exists():
        return None
    backups = sorted(
        draft_dir.glob("proposal-draft-r*.md"),
        key=lambda p: int(p.stem.rsplit("r", 1)[-1]) if p.stem.rsplit("r", 1)[-1].isdigit() else 0,
    )
    if not backups:
        return None
    prev = backups[-1]
    try:
        old_lines = prev.read_text(encoding="utf-8").splitlines()
        new_lines = current.read_text(encoding="utf-8").splitlines()
        added = removed = 0
        for line in difflib.unified_diff(old_lines, new_lines, lineterm="", n=0):
            if line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1
        return {
            "prev_round": prev.stem.rsplit("r", 1)[-1],
            "added_lines": added,
            "removed_lines": removed,
            "old_words": len(" ".join(old_lines)),
            "new_words": len(" ".join(new_lines)),
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 决策包生成
# ---------------------------------------------------------------------------


def generate_review_dossier(
    proposal_id: str,
    proposals_root: Optional[Path] = None,
    update_state: bool = True,
) -> Dict[str, Any]:
    """生成 05_review/review-dossier.md 并把摘要写回 prop_state。

    失败不抛异常（best-effort）：晋级链路中的调用方不应因决策包失败而中断。
    """
    try:
        root = proposals_root or PROPOSALS_ROOT
        lc_data = load_json(root / "_lifecycle.json", default={"proposals": {}})
        prop_state = (lc_data.get("proposals") or {}).get(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal_not_found"}

        pre = compute_pre_review(prop_state)
        # v7.2.69: 锚集对比（真实中标本子 pairwise，治 Goodhart 的非漂移锚）——
        # 无锚集（references/anchors/ 未入库）时静默跳过，零成本
        try:
            from anchor_corpus import compare_proposal, load_anchors
            if load_anchors() and prop_state.get("status") == "pending_review":
                _cmp = {m: compare_proposal(proposal_id, m)
                        for m in ("rationale", "scheme")}
                _cmp = {k: v for k, v in _cmp.items() if v}
            else:
                _cmp = {}
        except Exception:
            _cmp = {}
        prop_dir = find_proposal_dir(proposal_id, root)
        diff = summarize_draft_diff(prop_dir)
        history = prop_state.get("score_history") or []

        # 参考文献最近一次结果
        refs = last_entry_per_section(history).get("references")
        refs_summary = None
        if refs:
            refs_summary = {
                "round": refs.get("round"),
                "score": refs.get("score"),
                "passed": refs.get("section_passed"),
            }

        dossier = {
            "proposal_id": proposal_id,
            "title": prop_state.get("title", ""),
            "project_type": prop_state.get("project_type", "general"),
            "generated_at": now_utc(),
            "pre_review_verdict": pre["verdict"],
            "pre_review_reasons": pre["reasons"],
            "last_score": pre["metrics"]["last_score"],
            # v7.2.61: 活口径双门字段（can_adopt_pre_review 消费）
            "monitor_score": pre["metrics"]["last_score"],
            "executability_score": pre["metrics"].get("monitor_executability"),
            "metrics": pre["metrics"],
            "diff": diff,
            "references": refs_summary,
            "anchor_comparison": _cmp or None,
            # v7.3.0: 手册就绪门字段（can_adopt_pre_review 消费）
            "manual_ready": pre["metrics"].get("manual_ready", False),
            "can_adopt": can_adopt_pre_review({
                "pre_review_verdict": pre["verdict"],
                "last_score": pre["metrics"]["last_score"],
                "monitor_score": pre["metrics"]["last_score"],
                "executability_score": pre["metrics"].get("monitor_executability"),
                "manual_ready": pre["metrics"].get("manual_ready", False),
            }),
        }

        md_path = _write_dossier_markdown(prop_dir, dossier, prop_state, history, refs_summary)
        dossier["path"] = str(md_path) if md_path else None

        if update_state and md_path:
            _record_dossier_in_state(proposal_id, dossier)
        return {"success": True, **dossier}
    except Exception as exc:
        if _log:
            _log.warning(f"[{proposal_id}] 决策包生成失败: {exc}")
        return {"success": False, "error": str(exc)}


def _write_dossier_markdown(
    prop_dir: Optional[Path],
    dossier: Dict[str, Any],
    prop_state: Dict[str, Any],
    history: List[Dict[str, Any]],
    refs_summary: Optional[Dict[str, Any]],
) -> Optional[Path]:
    if prop_dir is None:
        return None
    review_dir = prop_dir / "05_review"
    review_dir.mkdir(parents=True, exist_ok=True)
    path = review_dir / "review-dossier.md"

    m = dossier["metrics"]
    verdict_label = {
        VERDICT_APPROVE: "建议通过（approve_lean）",
        VERDICT_ATTENTION: "需人工裁量（attention）",
        VERDICT_REJECT: "建议退回（reject_lean）",
    }[dossier["pre_review_verdict"]]

    lines: List[str] = []
    lines.append(f"# 验收决策包 · {dossier['title'] or dossier['proposal_id']}")
    lines.append("")
    lines.append(f"- 生成时间：{dossier['generated_at']}")
    lines.append(f"- 课题类型：{dossier['project_type']}")
    lines.append(f"- 优化轮次：{m['rounds']}")
    lines.append("")
    lines.append("## 预审结论")
    lines.append("")
    lines.append(f"**{verdict_label}**")
    for r in dossier["pre_review_reasons"]:
        lines.append(f"- {r}")
    if dossier["can_adopt"]:
        lines.append("")
        lines.append(
            f"> monitor 独立分 {float(dossier['last_score']):.2f} ≥ {MONITOR_ADOPT_GATE}，"
            f"可执行性 ≥ {EXECUTABILITY_ADOPT_GATE}，活口径高危 0——"
            "支持控制台「一键采纳预审」。"
        )
    lines.append("")
    lines.append("## 模块通过状态")
    lines.append("")
    section_map = last_entry_per_section(history)
    lines.append("| 模块 | 最近轮次 | 分数 | 通过 |")
    lines.append("|---|---|---|---|")
    for key in SECTION_ORDER:
        e = section_map.get(key)
        if e:
            mark = "✓" if e.get("section_passed") else "✗"
            # v7.3.0: 手册行附就绪度分级（L0-L4）
            extra = ""
            if key == "method_manual":
                _lv = e.get("manual_readiness_level")
                extra = f"（L{_lv}）" if isinstance(_lv, (int, float)) else "（未分级）"
            lines.append(
                f"| {SECTION_NAMES[key]} | R{e.get('round', '?')} | "
                f"{float(e.get('score') or 0):.2f} | {mark}{extra} |"
            )
        else:
            lines.append(f"| {SECTION_NAMES[key]} | - | - | ○ 未执行 |")
    lines.append("")
    lines.append(
        f"通过 **{m['passed_modules']}/{m['total_modules']}** · 未解决问题 "
        f"**{m['unresolved_issues']}**（高危 {m['high_issues']}）"
        + (
            f" · monitor 活口径高危 **{m['live_high']}**（R{m.get('live_high_round', '?')}）"
            if m.get("live_high") is not None
            else ""
        )
    )
    # v7.3.0: 手册开工就绪门——未过线时显式提示（课题能否正式开始由手册决定）
    if not m.get("manual_ready"):
        lines.append("")
        lines.append(
            f"> ⚠ 方法手册未达开工就绪：{_manual_not_ready_reason(section_map.get('method_manual'))}"
            "。v7.3.0 起手册就绪度为验收硬门，未过线不可归档开工。"
        )
    # v7.2.61: 未解决问题明细（此前只有计数无明细——用户无从判断"高危"
    # 是学术错误还是风格债，30 分钟决策不可能完成）
    detail = m.get("unresolved_detail") or []
    if detail:
        lines.append("")
        lines.append("### 未解决问题明细（Top8，请逐条核验是否已被后续修复）")
        lines.append("")
        lines.append("| 级别 | 章节 | 最近轮 | 描述 |")
        lines.append("|---|---|---|---|")
        for it in detail:
            desc = str(it.get("description", "")).replace("|", "\\|")
            lines.append(
                f"| {it.get('severity', '?')} | {it.get('section', '?')} | "
                f"R{it.get('last_seen_round', '?')} | {desc} |"
            )
        if m.get("live_high") is not None and m.get("live_high") < m.get("high_issues", 0):
            lines.append("")
            lines.append(
                "> 注：monitor 活口径高危数低于账本计数——账本条目可能已被"
                "评审团/人工修订修复但未销账，请以正文实际情况为准。"
            )
    # v7.2.62: 申请人无关化设计声明（替代 v7.2.61 的「缺口提示」口径）
    # 用户设计决策（与 nsfc-standards.json scope_exclusion v6.9.64 一致）：
    # 课题库产出申请人无关的研究方案，研究基础/工作条件章按设计排除，
    # 不列为缺陷、不提示注入、不计入验收完整性判据。
    lines.append("")
    lines.append(
        "> ℹ 设计说明：研究基础/工作条件章按设计排除（申请人无关化，"
        "scope_exclusion v6.9.64）——非缺口，无需注入，验收不检查该章。"
    )
    _sb = m.get("sent_back_count", 0)
    _pa = m.get("promotion_attempts", 0)
    if _pa or _sb:
        lines.append("")
        lines.append(
            f"> 🔁 裁决史：曾晋级 {_pa} 次、被退回 {_sb} 次"
            + ("——多次退回后分数仍平台化时，请考虑结构性重写/合并/换题选项"
               if _sb >= 3 else "")
        )
    lines.append("")
    lines.append("## 分数曲线")
    lines.append("")
    if history:
        lines.append("```")
        for e in history[-10:]:
            score = e.get("score")
            score_s = f"{float(score):.2f}" if score is not None else "  -  "
            lines.append(f"R{e.get('round', '?')} {score_s}  {e.get('focus_section', '')}")
        lines.append("```")
    else:
        lines.append("（无评分历史）")
    lines.append("")
    lines.append("## 与上一轮差异")
    lines.append("")
    diff = dossier.get("diff")
    if diff:
        lines.append(
            f"- 相比 R{diff['prev_round']}：+{diff['added_lines']} 行 / "
            f"-{diff['removed_lines']} 行（篇幅 {diff['old_words']} → {diff['new_words']} 字符）"
        )
    else:
        lines.append("- 无上一轮备份可比")
    lines.append("")
    lines.append("## 参考文献校验")
    lines.append("")
    if refs_summary:
        mark = "✓ 通过" if refs_summary.get("passed") else "✗ 未通过"
        lines.append(
            f"- 最近校验：R{refs_summary.get('round')}，"
            f"分数 {float(refs_summary.get('score') or 0):.2f}，{mark}"
        )
    else:
        lines.append("- 无 references 校验记录")
    anchor = dossier.get("anchor_comparison") or {}
    if anchor:
        _V = {"ours_stronger": "我方更强", "comparable": "相当", "anchor_stronger": "锚点更强"}
        lines.append("")
        lines.append("## 锚集对比（vs 真实中标本子，交换顺序双跑）")
        for mod, r in anchor.items():
            f = r.get("final") or {}
            lines.append(
                f"- {SECTION_NAMES.get(mod, mod)} vs {f.get('anchor', '?')}："
                f"**{_V.get(f.get('verdict'), '？')}**")
            for g in (f.get("gap_points") or [])[:3]:
                lines.append(f"  - 差距点：{g}")
    warning = prop_state.get("quality_warning")
    if warning:
        # v7.2.61: 渲染前整行去重——旧版 executor 无限追加导致同两行守卫
        # 警告在决策包里重复 12 遍（ssh-weyl 实测）
        _seen_lines: set = set()
        _deduped: List[str] = []
        for ln in str(warning).splitlines():
            if ln.strip() and ln not in _seen_lines:
                _seen_lines.add(ln)
                _deduped.append(ln)
        lines.append("")
        lines.append("## 质量警告")
        lines.append("")
        for ln in _deduped:
            lines.append(f"> {ln}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _record_dossier_in_state(proposal_id: str, dossier: Dict[str, Any]) -> None:
    """把决策包摘要写回 _lifecycle.json（锁保护 + 重读合并防覆盖）。"""
    from common import file_lock

    with file_lock("proposal-lifecycle"):
        data = load_json(PROPOSALS_ROOT / "_lifecycle.json", default={"proposals": {}})
        prop = (data.get("proposals") or {}).get(proposal_id)
        if not prop:
            return
        prop["review_dossier"] = {
            "generated_at": dossier["generated_at"],
            "pre_review_verdict": dossier["pre_review_verdict"],
            "pre_review_reasons": dossier["pre_review_reasons"],
            "last_score": dossier["last_score"],
            # v7.2.61: 活口径双门字段——Web review-adopt 守卫
            # （can_adopt_pre_review）从 state 摘要读取，缺这两字段会
            # 恒 False（一键采纳永久死锁）。
            "monitor_score": dossier.get("monitor_score"),
            "executability_score": dossier.get("executability_score"),
            "can_adopt": dossier["can_adopt"],
            "path": dossier.get("path"),
        }
        data["updated_at"] = now_utc()
        save_json(PROPOSALS_ROOT / "_lifecycle.json", data)


def get_dossier_summary(proposal_id: str) -> Optional[Dict[str, Any]]:
    """读取 prop_state 中的决策包摘要（无则返回 None）。"""
    data = load_json(PROPOSALS_ROOT / "_lifecycle.json", default={"proposals": {}})
    prop = (data.get("proposals") or {}).get(proposal_id)
    if not prop:
        return None
    summary = prop.get("review_dossier")
    if summary and summary.get("path"):
        summary = dict(summary)
        md = Path(summary["path"])
        summary["content"] = md.read_text(encoding="utf-8") if md.exists() else None
    return summary


def dossier_context_for_session(proposal_id: str, max_chars: int = 2400) -> str:
    """审核会话注入用的决策包文本块。"""
    summary = get_dossier_summary(proposal_id)
    if not summary:
        return ""
    verdict_label = {
        VERDICT_APPROVE: "建议通过（approve_lean）",
        VERDICT_ATTENTION: "需人工裁量（attention）",
        VERDICT_REJECT: "建议退回（reject_lean）",
    }.get(summary.get("pre_review_verdict"), summary.get("pre_review_verdict", ""))
    parts = [
        "【验收决策包（系统预审）】",
        f"预审结论：{verdict_label}",
    ]
    for r in summary.get("pre_review_reasons", [])[:4]:
        parts.append(f"- {r}")
    if summary.get("last_score") is not None:
        parts.append(f"最新 monitor 评分：{float(summary['last_score']):.2f}")
    if summary.get("can_adopt"):
        parts.append(
            "该课题满足「一键采纳预审」条件（approve_lean 且 monitor 独立分 ≥ "
            f"{MONITOR_ADOPT_GATE} 且可执行性 ≥ {EXECUTABILITY_ADOPT_GATE}），"
            "可在全链路页一键通过，或在此讨论后给结论。"
        )
    text = "\n".join(parts)
    return text[:max_chars]


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------


def _self_check() -> None:
    import tempfile

    # 1. 预审规则（v7.2.61：monitor 活口径优先 + 无 monitor 回退旧账本规则）
    base_state = {
        "score_history": [
            {"round": 1, "focus_section": s, "score": 0.86, "section_passed": True}
            for s in SECTION_ORDER
        ],
        "open_critical_issues": [],
        "last_monitor_score": 0.88,
        "optimization_rounds": 5,
    }

    # 1a. monitor 活口径主路径：高危 0 + 分与可执行性达标 → approve
    live = dict(base_state)
    live["monitor_history"] = [
        {"round": 5, "high_issues_after": 0, "executability_score": 0.82}
    ]
    pre = compute_pre_review(live)
    assert pre["verdict"] == VERDICT_APPROVE, pre
    # v7.3.14: 断言随模块数自适应（v7.3.0 六模块后硬编码 5 过期，测试漂移）
    assert pre["metrics"]["passed_modules"] == len(SECTION_ORDER)
    assert pre["metrics"]["live_high"] == 0

    # 1b. 活口径高危 1-2 → attention（不再被陈账判 reject）
    live2 = dict(live)
    live2["monitor_history"] = [
        {"round": 8, "high_issues_after": 2, "executability_score": 0.88}
    ]
    live2["open_critical_issues"] = [{"severity": "high", "last_seen_round": 8}] * 14
    live2["optimization_rounds"] = 8
    pre2 = compute_pre_review(live2)
    assert pre2["verdict"] == VERDICT_ATTENTION, pre2
    assert any("账本未销账" in r for r in pre2["reasons"]), pre2
    assert len(pre2["metrics"]["unresolved_detail"]) == 8

    # 1c. 活口径高危 >= 3 → reject
    live3 = dict(live)
    live3["monitor_history"] = [{"round": 5, "high_issues_after": 4}]
    assert compute_pre_review(live3)["verdict"] == VERDICT_REJECT

    # 1d. 活口径 0 但近轮 critical 未销账 → attention（保守）
    live4 = dict(live)
    live4["open_critical_issues"] = [
        {"severity": "critical", "last_seen_round": 5}
    ]
    live4["optimization_rounds"] = 5
    assert compute_pre_review(live4)["verdict"] == VERDICT_ATTENTION

    # 1e. 活口径 0 但可执行性缺失 → attention
    live5 = dict(live)
    live5["monitor_history"] = [{"round": 5, "high_issues_after": 0}]
    assert compute_pre_review(live5)["verdict"] == VERDICT_ATTENTION

    # 1f. 无 monitor 活口径 → 回退旧账本规则
    fallback = dict(base_state)
    fallback["open_critical_issues"] = [{"severity": "high"}]
    assert compute_pre_review(fallback)["verdict"] == VERDICT_REJECT

    few = dict(base_state)
    few["score_history"] = base_state["score_history"][:2]
    assert compute_pre_review(few)["verdict"] == VERDICT_REJECT

    warn = dict(base_state)
    warn["quality_warning"] = "达到最大轮数8（已通过2/5模块）"
    assert compute_pre_review(warn)["verdict"] == VERDICT_ATTENTION

    # 2. 采纳守卫（v7.2.61 换轨：monitor 分 + 可执行性双门）
    assert can_adopt_pre_review(
        {
            "pre_review_verdict": VERDICT_APPROVE,
            "monitor_score": 0.86,
            "executability_score": 0.80,
        }
    )
    assert not can_adopt_pre_review(
        {
            "pre_review_verdict": VERDICT_APPROVE,
            "monitor_score": 0.86,
            "executability_score": 0.70,
        }
    )
    assert not can_adopt_pre_review(
        {
            "pre_review_verdict": VERDICT_APPROVE,
            "monitor_score": 0.78,
            "executability_score": 0.90,
        }
    )
    assert not can_adopt_pre_review(None)

    # 3. 端到端（临时目录）
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pid = "test-dossier-proposal"
        pdir = root / "optimizing" / pid / "04_proposal"
        pdir.mkdir(parents=True)
        (pdir / "proposal-draft-r1.md").write_text("第一轮内容\n" * 10, encoding="utf-8")
        (pdir / "proposal-draft.md").write_text(
            "第二轮内容\n" * 12, encoding="utf-8"
        )
        state = {
            "proposals": {
                pid: dict(
                    base_state,
                    title="测试课题",
                    monitor_history=[
                        {"round": 5, "high_issues_after": 0, "executability_score": 0.82}
                    ],
                )
            }
        }
        save_json(root / "_lifecycle.json", state)

        result = generate_review_dossier(pid, proposals_root=root, update_state=False)
        assert result["success"], result
        assert result["can_adopt"] is True
        assert result["diff"]["added_lines"] > 0
        md = (root / "optimizing" / pid / "05_review" / "review-dossier.md").read_text(
            encoding="utf-8"
        )
        assert "验收决策包" in md and "建议通过" in md

        # diff：无备份时返回 None 摘要但不失败
        (pdir / "proposal-draft-r1.md").unlink()
        diff = summarize_draft_diff(root / "optimizing" / pid)
        assert diff is None

    print("✓ review_dossier 自检通过")


def main() -> None:
    parser = argparse.ArgumentParser(description="验收决策包生成器")
    parser.add_argument("--generate", metavar="ID", help="为指定课题生成决策包")
    parser.add_argument("--summary", metavar="ID", help="读取决策包摘要")
    parser.add_argument(
        "--audit-calibration", action="store_true",
        help="v7.2.62 环④：审计机器预审与用户裁决一致率")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return
    if args.audit_calibration:
        import json as _json
        print(_json.dumps(audit_criteria_calibration(), ensure_ascii=False, indent=2))
        return
    if args.generate:
        result = generate_review_dossier(args.generate)
        if result.get("success"):
            print(
                f"✓ 决策包已生成：{result.get('path')}\n"
                f"  预审：{result['pre_review_verdict']}（{'；'.join(result['pre_review_reasons'])}）\n"
                f"  可一键采纳：{'是' if result['can_adopt'] else '否'}"
            )
        else:
            print(f"✗ 生成失败：{result.get('error')}")
        return
    if args.summary:
        import json

        summary = get_dossier_summary(args.summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2) if summary else "（无决策包）")
        return
    parser.print_help()


if __name__ == "__main__":
    main()
