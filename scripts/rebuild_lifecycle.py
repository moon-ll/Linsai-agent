#!/usr/bin/env python3
"""rebuild_lifecycle.py — 基于现有 critic 报告重建 _lifecycle.json（v6.7.1 修复工具）

用途:
    当 _lifecycle.json 中的 score_history / optimization_rounds 与实际 critic 报告
    不一致时，扫描 05_review/critic-round-*.md 重新计算并修复状态文件。

用法:
    python3 scripts/rebuild_lifecycle.py --dry-run   # 预览变更
    python3 scripts/rebuild_lifecycle.py             # 执行重建

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
from typing import Any, Dict, List, Optional

from common import now_utc, load_json, save_json, file_lock
from paths import PROJECT_ROOT

# 复用 proposal_lifecycle 的评分提取逻辑
sys.path.insert(0, str(Path(__file__).parent))
from proposal_lifecycle import ProposalLifecycle, PROPOSAL_SECTIONS

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


def rebuild_lifecycle(dry_run: bool = False) -> Dict[str, Any]:
    """扫描 critic 报告并重建 _lifecycle.json。"""
    if not LIFECYCLE_PATH.exists():
        return {"error": "_lifecycle.json 不存在"}

    lifecycle = load_json(LIFECYCLE_PATH, default={"proposals": {}})
    proposals = lifecycle.get("proposals", {})

    lc = ProposalLifecycle()
    changes: List[Dict[str, Any]] = []

    for pid, state in proposals.items():
        prop_dir = _find_proposal_dir(pid)
        if not prop_dir:
            continue

        review_dir = prop_dir / "05_review"
        critic_files = sorted(review_dir.glob("critic-round-*.md")) if review_dir.exists() else []

        old_rounds = state.get("optimization_rounds", 0)
        old_last_score = state.get("last_score", 0.0)

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
            min_score = threshold.get("min_overall_score", 0.8)
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

        state["optimization_rounds"] = new_rounds
        state["last_score"] = last_score
        state["last_dim_scores"] = last_dim_scores
        state["section_passes"] = section_passes
        state["score_history"] = new_score_history
        state["updated_at"] = now_utc()

    if dry_run:
        return {"dry_run": True, "changes": changes, "total_proposals": len(proposals)}

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
        "total_proposals": len(proposals),
        "backup_path": str(backup_path.relative_to(PROJECT_ROOT)),
    }


def _self_check() -> None:
    """自检：验证重建逻辑基本可用。"""
    print("=== rebuild_lifecycle._self_check ===")
    result = rebuild_lifecycle(dry_run=True)
    assert "changes" in result
    print(f"  扫描 {result['total_proposals']} 个 proposal")
    for c in result["changes"][:3]:
        print(f"  - {c['proposal_id']}: rounds {c['old_rounds']} → {c['new_rounds']}, "
              f"score {c['old_last_score']:.2f} → {c['new_last_score']:.2f}")
    print("=== 通过 ===")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        _self_check()
    else:
        dry = len(sys.argv) > 1 and sys.argv[1] == "--dry-run"
        result = rebuild_lifecycle(dry_run=dry)
        print(json.dumps(result, ensure_ascii=False, indent=2))
