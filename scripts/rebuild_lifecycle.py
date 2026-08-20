#!/usr/bin/env python3
"""rebuild_lifecycle.py — 基于现有 critic 报告重建 _lifecycle.json（v6.7.2 修复工具）

用途:
    当 _lifecycle.json 中的 score_history / optimization_rounds 与实际 critic 报告
    不一致时，扫描 05_review/critic-round-*.md 重新计算并修复状态文件。

    v6.7.2 新增：检测并修复 critic 报告轮次编号异常（如 [1,3] 缺 2、round-99 等）。

用法:
    python3 scripts/rebuild_lifecycle.py --dry-run              # 预览 lifecycle 重建
    python3 scripts/rebuild_lifecycle.py                        # 执行 lifecycle 重建
    python3 scripts/rebuild_lifecycle.py --normalize-rounds     # 重命名 critic 文件为连续编号
    python3 scripts/rebuild_lifecycle.py --normalize-rounds --dry-run  # 预览重命名

设计原则:
    - 只修改 score_history / last_score / last_dim_scores / section_passes /
      optimization_rounds / updated_at
    - 不修改 status / transition_history / project_type / source 等人工/流程状态
    - 重建前自动备份原 _lifecycle.json 到 backups/
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import now_utc, load_json, save_json, file_lock
from paths import PROJECT_ROOT

# 复用 proposal_lifecycle 的评分提取逻辑
sys.path.insert(0, str(Path(__file__).parent))
from proposal_lifecycle import ProposalLifecycle
from proposal_sections import PROPOSAL_SECTIONS

RESEARCH_PROPOSALS_DIR = PROJECT_ROOT / "research_proposals"
LIFECYCLE_PATH = RESEARCH_PROPOSALS_DIR / "_lifecycle.json"
BACKUP_DIR = PROJECT_ROOT / "backups"


def _parse_focus_section_from_report(text: str) -> Optional[str]:
    """从 critic 报告头部解析聚焦章节。"""
    # 匹配：> 本轮聚焦：（一）立项依据... 或 聚焦章节：立项依据
    patterns = [
        r"本轮聚焦[：:]\s*（[一二三四五]）?\s*([^\n]+)",
        r"聚焦章节[：:]\s*（[一二三四五]）?\s*([^\n]+)",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            label = m.group(1).strip()
            # 映射到 section key
            if "立项" in label or "依据" in label:
                return "rationale"
            if "内容" in label:
                return "content"
            if "方案" in label or "方法" in label:
                return "method"
            if "整体" in label or "一致性" in label or "审查" in label:
                return "full_review"
    return None


def _section_key_for_round(round_num: int) -> str:
    """根据 round 数推断 focus_section（与 optimize_cycle 一致）。"""
    section_cycle = (round_num - 1) % (len(PROPOSAL_SECTIONS) + 1)
    if section_cycle < len(PROPOSAL_SECTIONS):
        return PROPOSAL_SECTIONS[section_cycle]["key"]
    return "full_review"


def _find_proposal_dir(proposal_id: str) -> Optional[Path]:
    """在四阶段目录中查找 proposal 目录。"""
    for stage in ["optimizing", "pending_review", "drafts", "archived"]:
        d = RESEARCH_PROPOSALS_DIR / stage / proposal_id
        if d.exists():
            return d
    return None


def _cycle_start_ts(state: Dict[str, Any]) -> float:
    """v6.8.50: 计算当前周期起点（epoch 秒）。

    取 score_history 中"轮次回退点"（如 r8→r1，表示周期重启）之后最早
    条目的 at；无回退则退回全 history 最早条目。早于该时间点的 critic
    文件属于旧周期，重算时应排除——否则会把旧周期 round-8 的分数覆盖
    当前周期的 last_score（实测案例：瞬态课题 0.81 被误算成 0.48）。
    """
    hist = state.get("score_history") or []

    def _ts(v: Any) -> float:
        try:
            return datetime.fromisoformat(str(v).replace("Z", "+00:00")).timestamp()
        except Exception:
            return 0.0

    # 找最后一次轮次回退点（当前周期的起点；history 可能含多段旧周期）
    restart_idx = -1
    for i in range(1, len(hist)):
        try:
            if int(hist[i].get("round", 0)) < int(hist[i - 1].get("round", 0)):
                restart_idx = i
        except (TypeError, ValueError):
            continue
    if restart_idx > 0:
        ats = [_ts(h.get("at")) for h in hist[restart_idx:]]
        ats = [t for t in ats if t > 0]
        if ats:
            return min(ats)
    # 无回退：全 history 最早
    ats = [_ts(h.get("at")) for h in hist]
    ats = [t for t in ats if t > 0]
    return min(ats) if ats else 0.0


def rebuild_lifecycle(dry_run: bool = False, proposal_id: Optional[str] = None,
                      force: bool = False) -> Dict[str, Any]:
    """扫描 critic 报告并重建 _lifecycle.json。

    v6.8.50 安全护栏：
    - proposal_id: 只处理指定课题（定向校准）
    - 周期过滤: 只统计 mtime ≥ 当前周期起点的 critic 文件（防旧周期污染）
    - 漂移护栏: 重算 last_score 与现值分差 >0.30 且未 --force 时，
      保留现有 score 字段只告警（伪分数/旧文件混入双保险）
    """
    if not LIFECYCLE_PATH.exists():
        return {"error": "_lifecycle.json 不存在"}

    lifecycle = load_json(LIFECYCLE_PATH, default={"proposals": {}})
    proposals = lifecycle.get("proposals", {})

    lc = ProposalLifecycle()
    changes: List[Dict[str, Any]] = []
    skipped_by_guard: List[Dict[str, Any]] = []

    for pid, state in proposals.items():
        if proposal_id and pid != proposal_id:
            continue
        # v6.8.50: 已晋级/归档课题的轮次是历史事实，不参与重算
        # （bsv 晋级 pending_review 后若重算会被覆盖成错误轮次）
        if state.get("status") not in ("optimizing",):
            continue
        prop_dir = _find_proposal_dir(pid)
        if not prop_dir:
            continue

        review_dir = prop_dir / "05_review"
        critic_files = sorted(review_dir.glob("critic-round-*.md")) if review_dir.exists() else []

        old_rounds = state.get("optimization_rounds", 0)
        old_last_score = state.get("last_score", 0.0)

        # v6.8.50: 周期过滤——排除旧周期的 critic 文件
        cycle_start = _cycle_start_ts(state)
        if cycle_start > 0:
            critic_files = [f for f in critic_files if f.stat().st_mtime >= cycle_start - 60]
        # 过滤后无文件：当前周期无可解析报告（新格式带章节后缀或尚未生成），
        # 保留现状跳过，避免 rounds/score 被错误重置
        if not critic_files:
            continue

        new_score_history: List[Dict[str, Any]] = []
        section_passes: Dict[str, bool] = {}
        last_score = 0.0
        last_dim_scores: Dict[str, float] = {}

        for f in critic_files:
            m = re.search(r"critic-round-(\d+)\.md$", f.name)
            if not m:
                continue
            round_num = int(m.group(1))
            try:
                text = f.read_text(encoding="utf-8")
            except Exception:
                continue

            result = {"output": text}
            score = lc._extract_score(result)
            dim_scores = lc._extract_dimension_scores(result)
            issues = lc._extract_issues(result)

            # 推断聚焦章节
            focus_from_report = _parse_focus_section_from_report(text)
            section_key = focus_from_report or _section_key_for_round(round_num)

            # 判断该模块是否对抗胜利
            project_type = state.get("project_type", "general")
            threshold = lc._get_quality_threshold(project_type)
            min_score = threshold.get("min_overall_score", 0.85)
            dimension_floor = getattr(lc, "DIMENSION_FLOOR", {
                "innovation": 0.65, "feasibility": 0.65, "rigor": 0.65, "completeness": 0.60
            })
            weak_dims = [k for k, floor in dimension_floor.items() if k in dim_scores and dim_scores[k] < floor]
            section_passed = score >= min_score and len(weak_dims) == 0

            section_passes[section_key] = section_passed
            last_score = score
            last_dim_scores = dim_scores

            new_score_history.append({
                "round": round_num,
                "score": score,
                "dim_scores": dim_scores,
                "weakest_dim": min(dim_scores, key=dim_scores.get) if dim_scores else "",
                "focus_section": section_key,
                "section_passed": section_passed,
                "issues_count": len(issues),
                "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
                "at": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            })

        new_rounds = len(new_score_history)

        # 只有在有变化时才更新
        if (
            new_rounds != old_rounds
            or abs(last_score - old_last_score) > 0.001
            or not state.get("score_history")
        ):
            changes.append({
                "proposal_id": pid,
                "old_rounds": old_rounds,
                "new_rounds": new_rounds,
                "old_last_score": old_last_score,
                "new_last_score": last_score,
            })

        # v6.8.50 漂移护栏：重算分数与现值分差过大时，该课题完全保留现状。
        # 双保险场景：a) 旧周期文件混入（周期过滤失效时）b) 伪分数污染期
        # （0.81→0.18 案例：现值是清洗后的真实分，重算反而从污染文件捞回伪分）
        score_drift = abs(last_score - old_last_score)
        guard_triggered = (score_drift > 0.30) and (not force) and old_last_score > 0
        if guard_triggered:
            skipped_by_guard.append({
                "proposal_id": pid,
                "reason": f"score_drift {old_last_score:.2f}→{last_score:.2f} 超过 0.30，"
                          f"保留现状（--force 可强制覆盖）",
            })
            continue  # rounds/score/history 全部不动

        state["optimization_rounds"] = new_rounds
        state["last_score"] = last_score
        state["last_dim_scores"] = last_dim_scores
        state["section_passes"] = section_passes
        state["score_history"] = new_score_history
        state["updated_at"] = now_utc()

    if dry_run:
        return {"dry_run": True, "changes": changes, "skipped_by_guard": skipped_by_guard,
                "total_proposals": len(proposals)}

    # 备份原文件
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"_lifecycle.json.{now_utc().replace(':', '-')}"
    shutil.copy2(LIFECYCLE_PATH, backup_path)

    # 更新顶层时间戳
    lifecycle["updated_at"] = now_utc()

    # 写入新状态
    with file_lock("proposal-lifecycle"):
        save_json(LIFECYCLE_PATH, lifecycle)

    return {
        "success": True,
        "changes": changes,
        "skipped_by_guard": skipped_by_guard,
        "total_proposals": len(proposals),
        "backup_path": str(backup_path.relative_to(PROJECT_ROOT)),
    }


def _extract_rounds_from_files(critic_files: List[Path]) -> List[Tuple[int, Path]]:
    """提取 (round_num, path) 列表并按原编号排序。"""
    rounds: List[Tuple[int, Path]] = []
    for f in critic_files:
        m = re.search(r"critic-round-(\d+)\.md$", f.name)
        if m:
            rounds.append((int(m.group(1)), f))
    return sorted(rounds, key=lambda x: x[0])


def detect_round_anomalies(proposals: Dict[str, Any]) -> List[Dict[str, Any]]:
    """扫描所有 proposal 的 critic 报告，返回轮次异常信息。

    异常类型：
    - round_gap: 编号不连续（如 1,3 缺 2）
    - round_outlier: 异常大编号（>50 或 >实际数量+5）
    """
    anomalies: List[Dict[str, Any]] = []
    for pid, state in proposals.items():
        prop_dir = _find_proposal_dir(pid)
        if not prop_dir:
            continue
        review_dir = prop_dir / "05_review"
        critic_files = sorted(review_dir.glob("critic-round-*.md")) if review_dir.exists() else []
        rounds = _extract_rounds_from_files(critic_files)
        if not rounds:
            continue
        nums = [r[0] for r in rounds]
        expected = list(range(min(nums), max(nums) + 1))
        missing = [r for r in expected if r not in nums]
        if missing:
            anomalies.append({
                "proposal_id": pid,
                "type": "round_gap",
                "detail": f"critic 报告轮次不连续，缺失 {missing}",
                "round_nums": nums,
                "missing": missing,
            })
        if max(nums) > 50 or max(nums) > len(rounds) + 5:
            anomalies.append({
                "proposal_id": pid,
                "type": "round_outlier",
                "detail": f"存在异常轮次编号 {max(nums)}（实际仅 {len(rounds)} 份报告）",
                "round_nums": nums,
            })
    return anomalies


def normalize_critic_rounds(dry_run: bool = False) -> Dict[str, Any]:
    """将 critic 报告文件按时间顺序重命名为 sequential 编号，并重建 lifecycle。

    规则：
    - 按文件 mtime 排序（最早的为 round 1）
    - 仅当编号不连续或存在异常时才重命名
    - 重命名后调用 rebuild_lifecycle() 重建状态
    """
    if not LIFECYCLE_PATH.exists():
        return {"error": "_lifecycle.json 不存在"}

    lifecycle = load_json(LIFECYCLE_PATH, default={"proposals": {}})
    proposals = lifecycle.get("proposals", {})

    renames: List[Dict[str, Any]] = []
    for pid, state in proposals.items():
        prop_dir = _find_proposal_dir(pid)
        if not prop_dir:
            continue
        review_dir = prop_dir / "05_review"
        if not review_dir.exists():
            continue
        critic_files = sorted(review_dir.glob("critic-round-*.md"))
        rounds = _extract_rounds_from_files(critic_files)
        if not rounds:
            continue

        nums = [r[0] for r in rounds]
        expected = list(range(1, len(rounds) + 1))
        if nums == expected:
            continue  # 已连续，无需处理

        # 按 mtime 排序后重新编号
        rounds_by_time = sorted(rounds, key=lambda x: x[1].stat().st_mtime)
        for new_idx, (_, old_path) in enumerate(rounds_by_time, start=1):
            new_path = review_dir / f"critic-round-{new_idx}.md"
            if old_path == new_path:
                continue
            renames.append({
                "proposal_id": pid,
                "old": str(old_path.relative_to(PROJECT_ROOT)),
                "new": str(new_path.relative_to(PROJECT_ROOT)),
            })
            if not dry_run:
                # 若目标已存在（理论上不会，因为已连续编号不会冲突），先临时移动
                if new_path.exists():
                    temp_path = review_dir / f"critic-round-{new_idx}-tmp.md"
                    new_path.rename(temp_path)
                    new_path = review_dir / f"critic-round-{new_idx}.md"
                old_path.rename(new_path)

    rebuild_result: Dict[str, Any] = {"changes": []}
    if not dry_run and renames:
        rebuild_result = rebuild_lifecycle(dry_run=False)

    return {
        "dry_run": dry_run,
        "renames": renames,
        "rebuild": rebuild_result,
    }


def _self_check() -> None:
    """自检：验证重建逻辑与异常检测基本可用。"""
    print("=== rebuild_lifecycle._self_check ===")
    result = rebuild_lifecycle(dry_run=True)
    assert "changes" in result
    print(f"  扫描 {result['total_proposals']} 个 proposal")
    for c in result["changes"][:3]:
        print(f"  - {c['proposal_id']}: rounds {c['old_rounds']} → {c['new_rounds']}, "
              f"score {c['old_last_score']:.2f} → {c['new_last_score']:.2f}")

    anomalies = detect_round_anomalies(load_json(LIFECYCLE_PATH, default={"proposals": {}}).get("proposals", {}))
    print(f"  轮次异常: {len(anomalies)} 条")
    for a in anomalies[:3]:
        print(f"  - {a['proposal_id']}: {a['type']} -> {a['detail']}")
    print("=== 通过 ===")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        _self_check()
    elif len(sys.argv) > 1 and sys.argv[1] == "--normalize-rounds":
        dry = len(sys.argv) > 2 and sys.argv[2] == "--dry-run"
        result = normalize_critic_rounds(dry_run=dry)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        dry = "--dry-run" in sys.argv
        force = "--force" in sys.argv
        pid_arg: Optional[str] = None
        if "--proposal" in sys.argv:
            i = sys.argv.index("--proposal")
            if i + 1 < len(sys.argv):
                pid_arg = sys.argv[i + 1]
        result = rebuild_lifecycle(dry_run=dry, proposal_id=pid_arg, force=force)
        print(json.dumps(result, ensure_ascii=False, indent=2))
