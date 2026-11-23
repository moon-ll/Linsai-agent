#!/usr/bin/env python3
"""将 hermes workspace 中 2026_NSFG_strongfield_ultrafast 的课题雏形导入全自动链路并激活。

用途:
    hermes workspace 里已有 T1-T4 四个课题方向（量子几何、能谷/莫尔、能带动力学、序参量读出）
    以及候选方向中的 BSV 驱动 HHG。本脚本把这些已有内容映射到 LinSai-CoPilot
    research_proposals/ 的标准六阶段结构中，并迁移到 optimizing 区启动 writer-critic
    对抗优化。

用法:
    python3 scripts/import_hermes_topics.py --dry-run     # 预览变更
    python3 scripts/import_hermes_topics.py --import      # 只导入/充实内容
    python3 scripts/import_hermes_topics.py --activate    # 导入 + 迁移到 optimizing + 启动 cron sweep

注意:
    - 不删除现有 critic 报告或已有 pipeline 产物，只做增量补充
    - 导入前自动备份 research_proposals/_lifecycle.json
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json
from paths import PROJECT_ROOT
from proposal_lifecycle import ProposalLifecycle

# Hermes workspace 源目录
HERMES_PROP_DIR = Path.home() / "Desktop" / "hermes_workspace" / "research_proposals" / "2026_NSFG_strongfield_ultrafast"

# 课题映射：hermes topic -> LinSai proposal_id
# T2 能谷/自旋动力学内容充实到现有的 "莫尔超晶格" proposal（两者高度重叠）
TOPIC_MAPPING: List[Dict[str, Any]] = [
    {
        "topic": "T1_quantum_geometry",
        "proposal_id": "general-quantum-geometry-inversion-20260726",
        "project_type": "general",
        "stage": "pending_review",
        "name": "量子几何反演",
    },
    {
        "topic": "T2_valleytronics",
        "proposal_id": "general-moire-strong-field-probe-20260726",
        "project_type": "general",
        "stage": "optimizing",
        "name": "莫尔强场探针",
    },
    {
        "topic": "T3_band_dynamics",
        "proposal_id": "key-transient-quantum-phase-optical-20260726",
        "project_type": "key",
        "stage": "optimizing",
        "name": "瞬态量子相全光读写",
    },
    {
        "topic": "T4_order_parameters",
        "proposal_id": "general-order-parameter-ultrafast-readout-20260727",
        "project_type": "general",
        "stage": None,  # 新 proposal，需要注册
        "name": "序参量超快读出",
    },
]

# BSV 没有独立 topic 目录，内容来自 candidate_directions.md
BSV_PROPOSAL_ID = "general-bsv-driven-hhg-quantum-20260726"


def _topic_file(topic: str, rel_path: str) -> Optional[Path]:
    """获取 hermes topic 下的文件路径。"""
    f = HERMES_PROP_DIR / "topics" / topic / rel_path
    return f if f.exists() else None


def _candidate_directions_path() -> Path:
    return HERMES_PROP_DIR / "deliverables" / "candidate_directions.md"


def _read_text(f: Optional[Path]) -> str:
    if not f or not f.exists():
        return ""
    try:
        return f.read_text(encoding="utf-8")
    except Exception:
        return ""


def _ensure_standard_dirs(prop_dir: Path) -> None:
    """确保标准六阶段目录存在。"""
    for d in [
        "01_direction",
        "02_literature/targeted-research",
        "02_topic",
        "03_question",
        "04_proposal",
        "05_review",
    ]:
        (prop_dir / d).mkdir(parents=True, exist_ok=True)


def _write_if_missing(path: Path, content: str) -> bool:
    """文件不存在或内容为空时才写入，避免覆盖已有产物。"""
    if path.exists() and path.stat().st_size > 100:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _build_direction_text(topic: str, topic_name: str) -> str:
    """构建 01_direction/direction-calibration.md。"""
    readme = _read_text(_topic_file(topic, "README.md"))
    if not readme:
        return f"# 方向校准\n\n课题：{topic_name}\n\n（待补充方向校准内容）\n"
    # 在 README 前加方向校准标题
    return f"# 方向校准：{topic_name}\n\n> 来源：hermes workspace `{topic}` README.md\n\n{readme}\n"


def _build_literature_text(topic: str) -> str:
    """构建 02_literature/literature-report.md。"""
    refs = _read_text(_topic_file(topic, "references/关键论文列表.md"))
    if not refs:
        return "# 文献调研报告\n\n（待补充关键论文列表）\n"
    return f"# 文献调研报告\n\n> 来源：hermes workspace `{topic}/references/关键论文列表.md`\n\n{refs}\n"


def _build_gap_text(topic: str, topic_name: str) -> str:
    """构建 02_topic/gap-report.md。"""
    parts = [
        f"# 缺口分析报告：{topic_name}",
        f"> 来源：hermes workspace `{topic}` Q3/Q4/Q6 分析笔记\n",
    ]
    for rel in ["notes/Q3_method_landscape.md", "notes/Q4_h_blue_ocean.md", "notes/Q6_3d_gap_analysis.md"]:
        text = _read_text(_topic_file(topic, rel))
        if text:
            parts.append(text)
            parts.append("\n---\n")
    if len(parts) == 2:
        parts.append("（待补充缺口分析内容）\n")
    return "\n".join(parts)


def _build_question_text(topic: str, topic_name: str) -> str:
    """构建 03_question/question-framework.md。"""
    rationale = _read_text(_topic_file(topic, "notes/立项依据_v0.2.md"))
    if not rationale:
        return f"# 科学问题框架：{topic_name}\n\n（待补充科学问题）\n"
    # 简单提取核心问题部分作为问题框架
    framework = (
        f"# 科学问题框架：{topic_name}\n\n"
        f"> 来源：hermes workspace `{topic}/notes/立项依据_v0.2.md` 核心问题提炼\n\n"
        f"## 主科学问题\n\n"
        f"从 `{topic}` 立项依据中提炼的核心科学问题，详见 `04_proposal/proposal-draft.md`。\n\n"
        f"## 关键子问题\n\n"
        f"- 子问题 1：待 writer-critic 循环细化\n"
        f"- 子问题 2：待 writer-critic 循环细化\n"
        f"- 子问题 3：待 writer-critic 循环细化\n\n"
        f"## 与 T5 反演方法学接口\n\n"
        f"本课题的反演路径需与 `T5_inversion_methodology` 协同，详见方法学手册。\n"
    )
    return framework


def _build_proposal_text(topic: str, topic_name: str) -> str:
    """构建/补充 04_proposal/proposal-draft.md。"""
    rationale = _read_text(_topic_file(topic, "notes/立项依据_v0.2.md"))
    if not rationale:
        return f"# {topic_name} 申请书\n\n（待补充申请书正文）\n"
    # 在立项依据前加申请书标题
    return f"# {topic_name} 申请书\n\n> 来源：hermes workspace `{topic}/notes/立项依据_v0.2.md`\n\n{rationale}\n"


def _build_methodology_text(topic: str) -> str:
    """构建 04_proposal/methodology-manual.md。"""
    t5_rationale = _read_text(_topic_file("T5_inversion_methodology", "notes/立项依据_v0.1.md"))
    topic_q3 = _read_text(_topic_file(topic, "notes/Q3_method_landscape.md"))
    parts = ["# 方法学手册\n"]
    if t5_rationale:
        parts.append("> 来源：hermes workspace `T5_inversion_methodology/notes/立项依据_v0.1.md`\n")
        parts.append(t5_rationale)
    if topic_q3:
        parts.append("\n---\n")
        parts.append("> 来源：hermes workspace `{topic}/notes/Q3_method_landscape.md`\n")
        parts.append(topic_q3)
    if len(parts) == 1:
        parts.append("（待补充方法学细节：公式推导/参数表/技术路线图）\n")
    return "\n".join(parts)


def _build_bsv_proposal_text() -> str:
    """为 BSV 驱动 HHG 构建申请书草稿。"""
    candidates = _read_text(_candidate_directions_path())
    # 提取候选 4 部分
    bsv_section = ""
    if "### 候选 4" in candidates:
        start = candidates.find("### 候选 4")
        end = candidates.find("## 五个候选横向比较", start)
        if end == -1:
            end = len(candidates)
        bsv_section = candidates[start:end]
    if not bsv_section:
        bsv_section = "（候选 4：量子光场驱动的 HHG 内容待补充）\n"
    return f"# 量子光场驱动的 HHG 申请书\n\n> 来源：hermes workspace `deliverables/candidate_directions.md` 候选 4\n\n{bsv_section}\n"


def _build_bsv_direction_text() -> str:
    return "# 方向校准：量子光场驱动的 HHG\n\n> 来源：hermes workspace `deliverables/candidate_directions.md` 候选 4\n\n" \
           "用量子光场（明亮压缩真空 BSV、纠缠光子对）驱动固体/2D 材料的 HHG，" \
           "揭示经典光场无法触及的物理，建立固体多体态的非经典探针。\n"


def _build_bsv_literature_text() -> str:
    return "# 文献调研报告：量子光场驱动的 HHG\n\n" \
           "> 待 researcher profile 针对 Gorlach et al. 2024、BSV HHG 最新进展做定向检索。\n"


def _build_bsv_gap_text() -> str:
    return "# 缺口分析报告：量子光场驱动的 HHG\n\n" \
           "- 国际：2024 Nature Physics 已演示 BSV 驱动 HHG，但物理机制未完全理解\n" \
           "- 国内：几乎空白\n" \
           "- 关键缺口：BSV HHG 与经典光 HHG 的干涉指纹、量子光场作为多体态探针的理论框架\n"


def _build_bsv_question_text() -> str:
    return "# 科学问题框架：量子光场驱动的 HHG\n\n" \
           "1. BSV 驱动 HHG 的谱与经典光驱动有何本质差异？\n" \
           "2. BSV HHG 能否作为强关联体系的量子探针？\n" \
           "3. 量子光 HHG 与经典光 HHG 的干涉（量子指纹）如何提取？\n"


def import_topic_content(lc: ProposalLifecycle, mapping: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """导入单个 topic 内容到对应 proposal。"""
    topic = mapping["topic"]
    pid = mapping["proposal_id"]
    topic_name = mapping["name"]
    prop_dir = lc._find_proposal_dir(pid) or (lc.root / "drafts" / pid)

    result = {
        "proposal_id": pid,
        "topic": topic,
        "created_dirs": [],
        "written_files": [],
        "skipped_files": [],
    }

    if dry_run:
        return {**result, "dry_run": True, "would_write": [
            "01_direction/direction-calibration.md",
            "02_literature/literature-report.md",
            "02_topic/gap-report.md",
            "03_question/question-framework.md",
            "04_proposal/proposal-draft.md",
            "04_proposal/methodology-manual.md",
        ]}

    _ensure_standard_dirs(prop_dir)

    files_to_write = [
        (prop_dir / "01_direction" / "direction-calibration.md", _build_direction_text(topic, topic_name)),
        (prop_dir / "02_literature" / "literature-report.md", _build_literature_text(topic)),
        (prop_dir / "02_topic" / "gap-report.md", _build_gap_text(topic, topic_name)),
        (prop_dir / "03_question" / "question-framework.md", _build_question_text(topic, topic_name)),
        (prop_dir / "04_proposal" / "proposal-draft.md", _build_proposal_text(topic, topic_name)),
        (prop_dir / "04_proposal" / "methodology-manual.md", _build_methodology_text(topic)),
    ]

    for path, content in files_to_write:
        if _write_if_missing(path, content):
            result["written_files"].append(str(path.relative_to(lc.root)))
        else:
            result["skipped_files"].append(str(path.relative_to(lc.root)))

    return result


def import_bsv_content(lc: ProposalLifecycle, dry_run: bool = False) -> Dict[str, Any]:
    """导入 BSV 候选方向内容。"""
    pid = BSV_PROPOSAL_ID
    prop_dir = lc._find_proposal_dir(pid) or (lc.root / "drafts" / pid)
    result = {"proposal_id": pid, "topic": "BSV", "written_files": [], "skipped_files": []}

    if dry_run:
        return {**result, "dry_run": True}

    _ensure_standard_dirs(prop_dir)

    files_to_write = [
        (prop_dir / "01_direction" / "direction-calibration.md", _build_bsv_direction_text()),
        (prop_dir / "02_literature" / "literature-report.md", _build_bsv_literature_text()),
        (prop_dir / "02_topic" / "gap-report.md", _build_bsv_gap_text()),
        (prop_dir / "03_question" / "question-framework.md", _build_bsv_question_text()),
        (prop_dir / "04_proposal" / "proposal-draft.md", _build_bsv_proposal_text()),
        (prop_dir / "04_proposal" / "methodology-manual.md", _build_methodology_text("T4_order_parameters")),
    ]

    for path, content in files_to_write:
        if _write_if_missing(path, content):
            result["written_files"].append(str(path.relative_to(lc.root)))
        else:
            result["skipped_files"].append(str(path.relative_to(lc.root)))

    return result


def run_import(dry_run: bool = False) -> Dict[str, Any]:
    """执行导入。"""
    lc = ProposalLifecycle()

    # 备份 lifecycle
    backup_path = None
    if not dry_run:
        backup_dir = PROJECT_ROOT / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"_lifecycle.json.before-import.{now_utc().replace(':', '-')}"
        shutil.copy2(lc.lifecycle_path, backup_path)

    results: List[Dict[str, Any]] = []

    for mapping in TOPIC_MAPPING:
        # 新 proposal 需要先注册
        if mapping["stage"] is None:
            if not dry_run:
                reg = lc.register(
                    proposal_id=mapping["proposal_id"],
                    project_type=mapping["project_type"],
                    source="expansion",
                    source_detail=f"来自 hermes workspace 课题雏形 {mapping['topic']}",
                )
                if not reg.get("success") and "已存在" not in reg.get("error", ""):
                    results.append({
                        "proposal_id": mapping["proposal_id"],
                        "error": reg.get("error"),
                    })
                    continue

        result = import_topic_content(lc, mapping, dry_run=dry_run)
        results.append(result)

    # BSV
    results.append(import_bsv_content(lc, dry_run=dry_run))

    return {
        "dry_run": dry_run,
        "results": results,
        "backup_path": str(backup_path.relative_to(PROJECT_ROOT)) if backup_path else None,
    }


def run_activate(dry_run: bool = False) -> Dict[str, Any]:
    """导入 + 迁移到 optimizing + 启动 cron sweep。"""
    import_result = run_import(dry_run=dry_run)

    if dry_run:
        return {**import_result, "activation": "dry_run"}

    lc = ProposalLifecycle()
    transitions: List[Dict[str, Any]] = []

    # 将所有相关 proposal 迁移到 optimizing
    target_pids = [m["proposal_id"] for m in TOPIC_MAPPING] + [BSV_PROPOSAL_ID]
    for pid in target_pids:
        state = lc._get_proposal_state(pid)
        if not state:
            transitions.append({"proposal_id": pid, "error": "未注册"})
            continue
        current = state.get("status")
        if current == "optimizing":
            transitions.append({"proposal_id": pid, "status": "already_optimizing"})
            continue
        if current in ["drafts", "pending_review"]:
            res = lc.transition(pid, "optimizing", reason="从 hermes workspace 导入内容后激活全自动优化")
            transitions.append({"proposal_id": pid, "result": res})
        else:
            transitions.append({"proposal_id": pid, "status": current, "skipped": True})

    # 启动 cron sweep
    sweep_result = lc.run_cron_sweep()

    return {
        "import": import_result,
        "transitions": transitions,
        "sweep": sweep_result,
    }


def _self_check() -> None:
    """自检：验证源目录存在、映射正确。"""
    print("=== import_hermes_topics._self_check ===")
    assert HERMES_PROP_DIR.exists(), f"hermes workspace 不存在: {HERMES_PROP_DIR}"
    for mapping in TOPIC_MAPPING:
        topic_dir = HERMES_PROP_DIR / "topics" / mapping["topic"]
        assert topic_dir.exists(), f"topic 目录不存在: {topic_dir}"
    assert _candidate_directions_path().exists(), "candidate_directions.md 不存在"
    print(f"✓ hermes workspace: {HERMES_PROP_DIR}")
    print(f"✓ 课题映射: {len(TOPIC_MAPPING)} 个 topic + BSV")
    print("=== 通过 ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="导入 hermes workspace 课题雏形并激活全自动链路")
    parser.add_argument("--dry-run", action="store_true", help="预览变更，不写入")
    parser.add_argument("--import", action="store_true", dest="import_only", help="只导入内容，不激活")
    parser.add_argument("--activate", action="store_true", help="导入 + 迁移到 optimizing + 启动 cron sweep")
    parser.add_argument("--self-check", action="store_true", help="自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        sys.exit(0)

    if args.activate:
        result = run_activate(dry_run=args.dry_run)
    else:
        result = run_import(dry_run=args.dry_run)

    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
