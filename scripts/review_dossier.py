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

# 五模块（与生命周期执行器一致）
SECTION_ORDER: List[str] = [
    "rationale",
    "content",
    "scheme",
    "full_review",
    "references",
]
SECTION_NAMES: Dict[str, str] = {
    "rationale": "立项依据",
    "content": "研究内容",
    "scheme": "研究方案（含创新与成果）",
    "full_review": "整篇一致性",
    "references": "参考文献",
}

APPROVE_SCORE_GATE = 0.85
"""一键采纳预审的分数门槛：approve_lean 且最新分 >= 0.85 才允许。

注意：自动达标晋级门槛（DEFAULT_SCORE_THRESHOLD）为 0.90，达到即自动
晋级；0.85 是"人工可快速采纳"的宽松线，低于它的任何课题都值得细读。"""

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


def compute_pre_review(
    prop_state: Dict[str, Any],
    reject_gate: float = REJECT_SCORE_GATE,
    approve_gate: float = APPROVE_SCORE_GATE,
) -> Dict[str, Any]:
    """规则预审：approve_lean / attention / reject_lean + 依据。

    判定顺序（先命中先返回）：
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

    # 未解决问题（open_critical_issues 中未被标记 stale/已解决的）
    unresolved = [
        i
        for i in (prop_state.get("open_critical_issues") or [])
        if isinstance(i, dict) and not i.get("stale") and not i.get("round_resolved")
    ]
    high_issues = [i for i in unresolved if str(i.get("severity", "")) == "high"]
    last_score = prop_state.get("last_monitor_score")
    if last_score is None and history:
        last_score = history[-1].get("score")

    metrics = {
        "passed_modules": passed_count,
        "total_modules": len(SECTION_ORDER),
        "unresolved_issues": len(unresolved),
        "high_issues": len(high_issues),
        "last_score": last_score,
        "quality_warning": prop_state.get("quality_warning"),
        "rounds": prop_state.get("optimization_rounds", 0),
    }

    reasons: List[str] = []
    if high_issues:
        verdict = VERDICT_REJECT
        reasons.append(f"存在 {len(high_issues)} 个未解决高危问题")
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

    return {"verdict": verdict, "reasons": reasons, "metrics": metrics}


def can_adopt_pre_review(dossier: Optional[Dict[str, Any]]) -> bool:
    """一键采纳守卫：决策包存在、预审 approve_lean、分数达标。"""
    if not dossier:
        return False
    if dossier.get("pre_review_verdict") != VERDICT_APPROVE:
        return False
    try:
        return float(dossier.get("last_score") or 0.0) >= APPROVE_SCORE_GATE
    except (TypeError, ValueError):
        return False


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
            "metrics": pre["metrics"],
            "diff": diff,
            "references": refs_summary,
            "can_adopt": (
                pre["verdict"] == VERDICT_APPROVE
                and pre["metrics"]["last_score"] is not None
                and float(pre["metrics"]["last_score"]) >= APPROVE_SCORE_GATE
            ),
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
            f"> 分数 {float(dossier['last_score']):.2f} ≥ {APPROVE_SCORE_GATE}，"
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
            lines.append(
                f"| {SECTION_NAMES[key]} | R{e.get('round', '?')} | "
                f"{float(e.get('score') or 0):.2f} | {mark} |"
            )
        else:
            lines.append(f"| {SECTION_NAMES[key]} | - | - | ○ 未执行 |")
    lines.append("")
    lines.append(
        f"通过 **{m['passed_modules']}/{m['total_modules']}** · 未解决问题 "
        f"**{m['unresolved_issues']}**（高危 {m['high_issues']}）"
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
    warning = prop_state.get("quality_warning")
    if warning:
        lines.append("")
        lines.append("## 质量警告")
        lines.append("")
        lines.append(f"> {warning}")
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
            "该课题满足「一键采纳预审」条件（approve_lean 且分数 ≥ "
            f"{APPROVE_SCORE_GATE}），可在全链路页一键通过，或在此讨论后给结论。"
        )
    text = "\n".join(parts)
    return text[:max_chars]


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------


def _self_check() -> None:
    import tempfile

    # 1. 预审规则
    base_state = {
        "score_history": [
            {"round": 1, "focus_section": s, "score": 0.86, "section_passed": True}
            for s in SECTION_ORDER
        ],
        "open_critical_issues": [],
        "last_monitor_score": 0.88,
        "optimization_rounds": 5,
    }
    pre = compute_pre_review(base_state)
    assert pre["verdict"] == VERDICT_APPROVE, pre
    assert pre["metrics"]["passed_modules"] == 5

    # 高危问题 → reject
    bad = dict(base_state)
    bad["open_critical_issues"] = [{"severity": "high"}]
    assert compute_pre_review(bad)["verdict"] == VERDICT_REJECT

    # 仅 2 模块通过 → reject
    few = dict(base_state)
    few["score_history"] = base_state["score_history"][:2]
    assert compute_pre_review(few)["verdict"] == VERDICT_REJECT

    # 质量警告 → attention
    warn = dict(base_state)
    warn["quality_warning"] = "达到最大轮数8（已通过2/5模块）"
    assert compute_pre_review(warn)["verdict"] == VERDICT_ATTENTION

    # 2. 采纳守卫
    assert can_adopt_pre_review(
        {"pre_review_verdict": VERDICT_APPROVE, "last_score": 0.86}
    )
    assert not can_adopt_pre_review(
        {"pre_review_verdict": VERDICT_APPROVE, "last_score": 0.80}
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
        state = {"proposals": {pid: dict(base_state, title="测试课题")}}
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
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
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
