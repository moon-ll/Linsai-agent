#!/usr/bin/env python3
"""遍次（pass）历史隔离与退回对比报告（v6.9.41）。

背景：审核退回（pending_review → optimizing）时 optimization_rounds 与
pipeline_jobs 被清零重跑，但 score_history 从不清理——第二遍的 r1-r3
条目与第一遍的 r1-r8 混在同一个数组里（08-23 实测 quantum-geometry
两遍数据叠加，"27 天都在第一轮"实为第二遍重跑）。任何跨遍路径分析、
毕业报告、退回复盘都建立在被污染的数据上。

修复分两层：
1. 遍次隔离（P0）：退回时把 score_history 按"遍"归档到
   score_history_archive（[{pass, returned_at, reason, entries}]），
   当前 score_history 清空；prop_state 新增 pass_number 计数。
2. 退回对比报告（P1）：退回时若存在上一遍数据，生成本遍 vs 上遍
   对比（分数轨迹 / 模块通过 / 弱维度卡点 / 天花板是否移动），回答
   "反馈注入为什么没打破天花板"这一核心问题。

用法：
    from proposal_lifecycle.pass_history import archive_pass_history
    archive_pass_history(prop_state, reason)          # 退回时调用
    generate_return_comparison(proposal_id, prop_dir) # 退回时调用（有上遍才生成）

自检：
    python3 -m proposal_lifecycle.pass_history --self-check
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc

try:
    from logger import get_logger
    _log = get_logger("pass_history")
except Exception:
    _log = None

# 对比报告输出目录（相对课题目录）
REVIEW_SUBDIR = "05_review"


def archive_pass_history(
    prop_state: Dict[str, Any],
    reason: str = "",
    max_passes: int = 10,
) -> int:
    """退回时归档当前遍的 score_history（P0 核心操作）。

    Args:
        prop_state: proposal 状态 dict（原地修改）。
        reason: 退回原因（存入归档条目）。
        max_passes: 归档保留的最大遍数（FIFO 裁剪，默认 10）。

    Returns:
        归档的条目数（当前 score_history 长度）。
    """
    current = [h for h in (prop_state.get("score_history") or []) if isinstance(h, dict)]
    if not current:
        # 空历史（从未跑过 monitor）也推进 pass_number，保持计数一致
        prop_state["pass_number"] = int(prop_state.get("pass_number", 1)) + 1
        return 0

    archive = prop_state.setdefault("score_history_archive", [])
    if not isinstance(archive, list):
        archive = []
    archive.append({
        "pass": int(prop_state.get("pass_number", 1)),
        "returned_at": now_utc(),
        "reason": reason[:200],
        "entries": current,
    })
    # FIFO 裁剪：只保留最近 max_passes 遍（每遍约 8 轮 × 5 章节条目，10 遍足够）
    if len(archive) > max_passes:
        archive = archive[-max_passes:]
    prop_state["score_history_archive"] = archive
    prop_state["score_history"] = []
    prop_state["pass_number"] = archive[-1]["pass"] + 1
    return len(current)


def _round_trajectory(entries: List[Dict[str, Any]]) -> Dict[int, float]:
    """从遍内 score_history 提取轮 → 该轮最高分映射（非 dict 条目安全跳过）。"""
    traj: Dict[int, float] = {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        r = e.get("round")
        s = e.get("score")
        if isinstance(r, int) and isinstance(s, (int, float)):
            traj[r] = max(traj.get(r, 0.0), float(s))
    return traj


def _weakest_dim_counts(entries: List[Dict[str, Any]]) -> Dict[str, int]:
    """统计遍内各维度被判"最弱"的次数（卡点分析，非 dict 安全跳过）。"""
    counts: Dict[str, int] = {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        d = e.get("weakest_dim")
        if d:
            counts[d] = counts.get(d, 0) + 1
    return counts


def _section_pass_counts(entries: List[Dict[str, Any]]) -> Dict[str, int]:
    """统计各章节对抗通过次数（非 dict 安全跳过）。"""
    counts: Dict[str, int] = {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        sec = e.get("focus_section")
        if sec and e.get("section_passed"):
            counts[sec] = counts.get(sec, 0) + 1
    return counts


def _fmt_traj(traj: Dict[int, float]) -> str:
    if not traj:
        return "（无 monitor 记录）"
    return " → ".join(f"r{r}:{traj[r]:.2f}" for r in sorted(traj))


def generate_return_comparison(
    proposal_id: str,
    prop_state: Dict[str, Any],
    prop_dir: Path,
) -> Optional[str]:
    """退回时生成本遍 vs 上遍对比报告（P1）。

    仅当存在归档遍次时生成；报告落盘到课题目录
    05_review/return-comparison-pass{N}.md。

    Returns:
        报告路径（str）或 None（无上遍数据 / 写入失败）。
    """
    archive = prop_state.get("score_history_archive") or []
    current = [h for h in (prop_state.get("score_history") or []) if isinstance(h, dict)]
    # 调用时序：archive_pass_history 先行（current 已清空、刚结束的遍在
    # archive 末尾）→ "本遍" = archive[-1]，"上遍" = archive[-2]。
    if len(archive) < 2:
        return None

    this_pass = archive[-1]
    prev_pass = archive[-2]
    this_traj = _round_trajectory(this_pass.get("entries", []))
    prev_traj = _round_trajectory(prev_pass.get("entries", []))

    this_max = max(this_traj.values()) if this_traj else 0.0
    prev_max = max(prev_traj.values()) if prev_traj else 0.0
    this_weak = _weakest_dim_counts(this_pass.get("entries", []))
    prev_weak = _weakest_dim_counts(prev_pass.get("entries", []))
    this_passes = _section_pass_counts(this_pass.get("entries", []))
    prev_passes = _section_pass_counts(prev_pass.get("entries", []))

    lines: List[str] = []
    lines.append(f"# 退回对比报告 · 第 {this_pass.get('pass', '?')} 遍 vs 第 {prev_pass.get('pass', '?')} 遍")
    lines.append("")
    lines.append(f"- 生成时间：{now_utc()}")
    lines.append(f"- 本遍退回原因：{this_pass.get('reason', '') or '（未记录）'}")
    lines.append(f"- 上遍退回原因：{prev_pass.get('reason', '') or '（未记录）'}")
    lines.append("")

    # ① 分数轨迹对比
    lines.append("## 分数轨迹对比")
    lines.append("")
    lines.append(f"- 第 {prev_pass.get('pass', '?')} 遍：{_fmt_traj(prev_traj)}")
    lines.append(f"- 第 {this_pass.get('pass', '?')} 遍：{_fmt_traj(this_traj)}")
    lines.append(f"- 天花板：{prev_max:.2f} → {this_max:.2f}"
                 f"（{'上升' if this_max > prev_max + 0.01 else '下降' if this_max < prev_max - 0.01 else '未移动'}）")
    lines.append("")

    # ② 模块对抗通过对比
    lines.append("## 模块对抗通过对比")
    lines.append("")
    all_secs = sorted(set(this_passes) | set(prev_passes))
    if all_secs:
        lines.append("| 章节 | 上遍通过 | 本遍通过 |")
        lines.append("|------|---------|---------|")
        for sec in all_secs:
            lines.append(f"| {sec} | {prev_passes.get(sec, 0)} | {this_passes.get(sec, 0)} |")
    else:
        lines.append("（两遍均无任何章节通过对抗门）")
    total_prev = sum(prev_passes.values())
    total_this = sum(this_passes.values())
    verdict_pass = (
        "对抗通过数增加——反馈注入有效果，但未达晋级线"
        if total_this > total_prev
        else "对抗通过数无增长——注入的审核意见未转化为通过能力"
    )
    lines.append("")
    lines.append(f"**判定**：{verdict_pass}")
    lines.append("")

    # ③ 弱维度卡点
    lines.append("## 弱维度卡点（weakest_dim 出现次数）")
    lines.append("")
    all_dims = sorted(set(this_weak) | set(prev_weak), key=lambda d: -(this_weak.get(d, 0) + prev_weak.get(d, 0)))
    if all_dims:
        lines.append("| 维度 | 上遍 | 本遍 | 是否仍是卡点 |")
        lines.append("|------|------|------|------------|")
        for d in all_dims:
            p, t = prev_weak.get(d, 0), this_weak.get(d, 0)
            still = "是（未响应）" if p > 0 and t > 0 else "否（已缓解）" if p > 0 and t == 0 else "新出现" if t > 0 else ""
            lines.append(f"| {d} | {p} | {t} | {still} |")
    else:
        lines.append("（无 weakest_dim 记录）")
    lines.append("")

    # ④ 综合诊断
    stuck_same = [d for d in all_dims if prev_weak.get(d, 0) > 0 and this_weak.get(d, 0) > 0]
    lines.append("## 综合诊断")
    lines.append("")
    if this_max <= prev_max + 0.01 and total_this <= total_prev and stuck_same:
        lines.append(
            f"**天花板未移动 + 对抗通过无增长 + 卡点未变（{', '.join(stuck_same[:3])}）**：\n"
            "反馈注入未产生边际效果。建议人工抽查该维度的 critic 报告与 writer 响应，\n"
            "确认是 writer 未执行意见，还是执行了但被门槛拦截（AI 表达天花板 / 维度口径错位）。"
        )
    elif this_max > prev_max + 0.01:
        lines.append("天花板有上升，反馈通道部分有效——继续当前策略，关注对抗门通过数。")
    elif total_this > total_prev:
        lines.append("对抗通过数增加，但总分天花板未动——模块质量提升未传导到 monitor 总分口径。")
    else:
        lines.append("各指标持平，路径重演上一遍。")
    lines.append("")

    # ⑤ 本遍遗留（若 current 非空，说明归档前已有新遍条目混入——防御性记录）
    if current:
        lines.append(f"> ⚠ 生成时当前 score_history 非空（{len(current)} 条），可能存在调用时序异常。")
        lines.append("")

    try:
        out_dir = prop_dir / REVIEW_SUBDIR
        out_dir.mkdir(parents=True, exist_ok=True)
        pass_no = this_pass.get("pass", 0)
        out_path = out_dir / f"return-comparison-pass{pass_no}.md"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        if _log:
            _log.info(f"[{proposal_id}] 退回对比报告已生成: {out_path.name}")
        return str(out_path)
    except Exception as e:
        if _log:
            _log.warning(f"[{proposal_id}] 退回对比报告写入失败: {e}")
        return None


# ─────────────────────────────────────────────
# 存量数据迁移：按退回时间切分混叠的 score_history
# ─────────────────────────────────────────────

def migrate_overlaid_history(prop_state: Dict[str, Any]) -> int:
    """把历史混叠的 score_history 按 transition_history 的退回时间切成遍次。

    存量数据修复（一次性）：旧版退回不清理 score_history，多遍条目按
    时间顺序混在同一数组。本函数用 transition_history 中 pending_review
    → optimizing 的退回时间戳作为切分点，把条目按 at 时间分桶回填
    score_history_archive，并推导 pass_number。

    Args:
        prop_state: proposal 状态 dict（原地修改）。

    Returns:
        切分出的历史遍数（0 = 无需迁移 / 已有归档跳过）。
    """
    if prop_state.get("score_history_archive"):
        return 0  # 已迁移过
    current = [h for h in (prop_state.get("score_history") or []) if isinstance(h, dict)]
    if not current:
        prop_state.setdefault("pass_number", 1)
        return 0

    # 收集退回时间戳（pending_review → optimizing）
    returns = []
    for t in prop_state.get("transition_history", []):
        if isinstance(t, dict) and t.get("from") == "pending_review" and t.get("to") == "optimizing":
            at = t.get("at", "")
            if at:
                returns.append((at, t.get("reason", "")))
    if not returns:
        prop_state.setdefault("pass_number", 1)
        return 0

    returns.sort(key=lambda x: x[0])
    # 条目按 at 分桶：第 i 个退回点之前的条目属于第 i 遍
    buckets: List[Dict[str, Any]] = []
    remaining = list(current)
    pass_no = 1
    for cut_at, cut_reason in returns:
        before, rest = [], []
        for e in remaining:
            (before if (e.get("at", "") or "") < cut_at else rest).append(e)
        if before:
            buckets.append({
                "pass": pass_no,
                "returned_at": cut_at,
                "reason": (cut_reason or "")[:200],
                "entries": before,
            })
            pass_no += 1
        remaining = rest
    # 剩余条目 = 当前遍
    prop_state["score_history"] = remaining
    prop_state["score_history_archive"] = buckets
    prop_state["pass_number"] = pass_no
    return len(buckets)


def _self_check() -> bool:
    """模块自检：归档/轨迹提取/迁移切分（零 LLM、零外部文件）。"""
    ok = True

    # 1) archive_pass_history：归档 + 遍次推进 + 清空
    st = {"score_history": [{"round": 1, "score": 0.8, "at": "2026-08-01T00:00:00Z"}],
          "pass_number": 1}
    n = archive_pass_history(st, reason="人工审核退回(major_revision)")
    if n == 1 and st["score_history"] == [] and st["pass_number"] == 2 \
            and len(st["score_history_archive"]) == 1 \
            and st["score_history_archive"][0]["pass"] == 1:
        print("✓ 归档：条目移入 archive、pass_number 推进、当前清空")
    else:
        print("✗ 归档逻辑错误"); ok = False

    # 2) 空历史也推进计数
    st2 = {"score_history": [], "pass_number": 1}
    archive_pass_history(st2)
    if st2["pass_number"] == 2 and not st2.get("score_history_archive"):
        print("✓ 空历史：仅推进 pass_number 不建归档")
    else:
        print("✗ 空历史处理错误"); ok = False

    # 3) FIFO 裁剪
    st3 = {"score_history": [{"round": 1, "score": 0.5, "at": "t"}], "pass_number": 12}
    st3["score_history_archive"] = [
        {"pass": i, "returned_at": f"2026-08-{i:02d}", "reason": "", "entries": []}
        for i in range(1, 11)
    ]
    archive_pass_history(st3, max_passes=10)
    if len(st3["score_history_archive"]) == 10 and st3["score_history_archive"][-1]["pass"] == 12:
        print("✓ FIFO 裁剪：超过上限丢弃最旧遍")
    else:
        print("✗ 裁剪逻辑错误"); ok = False

    # 4) 轨迹提取（轮最高分）
    traj = _round_trajectory([
        {"round": 1, "score": 0.7}, {"round": 1, "score": 0.8},
        {"round": 2, "score": 0.75}, "bad",
    ])
    if traj == {1: 0.8, 2: 0.75}:
        print("✓ 轨迹提取：轮最高分、非 dict 安全跳过")
    else:
        print("✗ 轨迹提取错误"); ok = False

    # 5) 迁移切分：两个退回点切三遍
    st5 = {
        "transition_history": [
            {"from": "drafts", "to": "optimizing", "at": "2026-07-26T00:00:00Z", "reason": ""},
            {"from": "optimizing", "to": "pending_review", "at": "2026-08-01T00:00:00Z", "reason": "满8轮"},
            {"from": "pending_review", "to": "optimizing", "at": "2026-08-02T00:00:00Z", "reason": "退回1"},
            {"from": "optimizing", "to": "pending_review", "at": "2026-08-10T00:00:00Z", "reason": "满8轮"},
            {"from": "pending_review", "to": "optimizing", "at": "2026-08-11T00:00:00Z", "reason": "退回2"},
        ],
        "score_history": [
            {"round": 1, "score": 0.7, "at": "2026-07-28T00:00:00Z"},
            {"round": 2, "score": 0.8, "at": "2026-07-30T00:00:00Z"},
            {"round": 1, "score": 0.72, "at": "2026-08-03T00:00:00Z"},
            {"round": 2, "score": 0.86, "at": "2026-08-08T00:00:00Z"},
            {"round": 1, "score": 0.73, "at": "2026-08-20T00:00:00Z"},
        ],
    }
    n5 = migrate_overlaid_history(st5)
    if n5 == 2 and len(st5["score_history"]) == 1 \
            and st5["score_history"][0]["score"] == 0.73 \
            and st5["pass_number"] == 3:
        print("✓ 迁移切分：两退回点切三遍，当前遍只剩本遍条目")
    else:
        print(f"✗ 迁移切分错误（n={n5}, pass={st5.get('pass_number')}, "
              f"当前 {len(st5.get('score_history', []))} 条）"); ok = False

    # 6) 已迁移跳过（幂等）
    n6 = migrate_overlaid_history(st5)
    if n6 == 0:
        print("✓ 幂等：已有 archive 再次迁移跳过")
    else:
        print("✗ 幂等性错误"); ok = False

    print("自检结果:", "✓ 通过" if ok else "✗ 失败")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_check() else 1)
