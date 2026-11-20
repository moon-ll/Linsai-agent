#!/usr/bin/env python3
"""regenerate_optimization_reports.py — 重生成历史优化报告（用当前 _generate_round_report 逻辑）。

用途：
    当 micro_scheduler._generate_round_report 的评分计算逻辑修复后（如 v6.8.33 的
    「总分与四维同源」修复），历史已生成的 optimization-report-round-*.md 仍是旧逻辑产物，
    其评分变化表的总分行与四维行数据源不一致。本脚本删除旧报告并重新生成，使历史报告
    与新逻辑一致（总分与四维取自同一条 score_history 记录）。

    重生成只改 05_review/optimization-report-round-*.md（自动生成的产物），不碰人工产出；
    评分数据来自 _lifecycle.json 的 score_history，保持只读。

用法：
    python3 scripts/regenerate_optimization_reports.py --dry-run    # 预览（含 score_history 覆盖检查）
    python3 scripts/regenerate_optimization_reports.py              # 执行（删旧+重生成，失败自动恢复）
    python3 scripts/regenerate_optimization_reports.py --self-check

安全：
    执行时先把旧报告 rename 到 .bak，重生成成功后删 .bak；失败则恢复 .bak，零数据丢失。
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

RESEARCH_ROOT = _SCRIPT_DIR.parent / "research_proposals"
STAGES = ["optimizing", "pending_review", "drafts", "archived"]


def _find_reports() -> List[Tuple[str, int, Path]]:
    """扫描所有 optimization-report-round-*.md。

    Returns:
        [(proposal_id, round_num, path), ...]
    """
    results: List[Tuple[str, int, Path]] = []
    for stage in STAGES:
        stage_dir = RESEARCH_ROOT / stage
        if not stage_dir.exists():
            continue
        for prop_dir in sorted(stage_dir.iterdir()):
            if not prop_dir.is_dir():
                continue
            review_dir = prop_dir / "05_review"
            if not review_dir.exists():
                continue
            for f in sorted(review_dir.glob("optimization-report-round-*.md")):
                m = re.search(r"round-(\d+)", f.name)
                if m:
                    results.append((prop_dir.name, int(m.group(1)), f))
    return results


def _check_coverage(ctrl, proposal_id: str, rnd: int) -> Tuple[bool, int]:
    """检查该 round 在 score_history 是否有记录（决定重生成是否会有四维行）。"""
    state = ctrl._get_proposal_state(proposal_id) or {}
    sh = state.get("score_history", [])
    rounds = [h for h in sh if h.get("round") == rnd]
    return (len(rounds) > 0, len(rounds))


def regenerate(dry_run: bool = False) -> dict:
    """重生成所有历史优化报告。

    Returns:
        {"regenerated", "degraded", "failed", "dry_run"}
    """
    from lifecycle.controller import get_controller
    from lifecycle.micro_scheduler import _generate_round_report

    ctrl = get_controller()
    reports = _find_reports()
    print(f"发现 {len(reports)} 份历史优化报告\n")

    regenerated, degraded, failed = [], [], []
    for pid, rnd, path in reports:
        has, n = _check_coverage(ctrl, pid, rnd)
        flag = "" if has else "  ⚠ score_history 无该轮记录（重生成将仅含总分行，无四维）"

        if dry_run:
            mark = "✓" if has else "◐"
            print(f"  [{mark}] {pid} round {rnd}  ← {path.name}{flag}")
            (regenerated if has else degraded).append((pid, rnd))
            continue

        # 执行：rename 备份 → 重生成 → 成功删备份 / 失败恢复
        bak = path.with_suffix(".md.bak")
        try:
            path.rename(bak)
            new_path = _generate_round_report(ctrl, pid, rnd)
            if new_path and Path(new_path).exists():
                bak.unlink(missing_ok=True)
                regenerated.append((pid, rnd))
                print(f"  ✓ {pid} round {rnd} 已重生成{flag}")
            else:
                bak.rename(path)
                failed.append((pid, rnd, "未生成"))
                print(f"  ✗ {pid} round {rnd} 未生成，已恢复原文件")
        except Exception as e:
            if bak.exists() and not path.exists():
                bak.rename(path)
            failed.append((pid, rnd, str(e)))
            print(f"  ✗ {pid} round {rnd} 异常: {e}（已恢复）")

    print(
        f"\n汇总: 重生成 {len(regenerated)}，"
        f"{'降级 ' + str(len(degraded)) + '，' if dry_run else ''}"
        f"失败 {len(failed)}"
    )
    return {
        "regenerated": len(regenerated),
        "degraded": len(degraded),
        "failed": len(failed),
        "dry_run": dry_run,
    }


def _self_check() -> bool:
    """自检：扫描器能工作 + controller 可创建 + 一份真实报告能被解析出 round。"""
    reports = _find_reports()
    if not reports:
        print("  ✗ 未扫描到任何 optimization-report（环境异常）")
        return False
    print(f"  ✓ 扫描到 {len(reports)} 份报告")
    try:
        from lifecycle.controller import get_controller
        ctrl = get_controller()
        print("  ✓ controller 可创建")
    except Exception as e:
        print(f"  ✗ controller 创建失败: {e}")
        return False
    # 验证 round 解析
    pid, rnd, _ = reports[0]
    if not isinstance(rnd, int) or rnd < 1:
        print(f"  ✗ round 解析异常: {rnd}")
        return False
    print(f"  ✓ round 解析正常（样本: {pid} round {rnd}）")
    print("  ✓ self-check 通过（未修改任何文件）")
    return True


def main():
    args = sys.argv[1:]
    if "--self-check" in args:
        ok = _self_check()
        sys.exit(0 if ok else 1)
    dry_run = "--dry-run" in args
    result = regenerate(dry_run=dry_run)
    if result["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
