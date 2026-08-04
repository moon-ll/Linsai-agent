#!/usr/bin/env python3
"""知识库提案整理脚本 —— 将最新申请书版本和优化报告纳入知识库统一管理。

依据最新架构设计（v6.8+），在 knowledge/wiki/projects/NSFC-强场超快/ 下新增：
  - versions/      ← 最新申请书快照（含 frontmatter + 链接到源文件）
  - reports/       ← 优化报告汇总（含各轮评审链接）

同时更新：
  - proposals-index.md  ← 修复链接，加入版本/报告入口
  - MOC.md              ← 加入新 sections 链接

用法：
    python3 scripts/kb_proposal_reorg.py              # 执行整理（dry-run 模式）
    python3 scripts/kb_proposal_reorg.py --apply      # 实际写入
    python3 scripts/kb_proposal_reorg.py --report     # 仅生成报告

规范：
    - 仅使用 Python 3 标准库
    - 不修改 research_proposals/ 下的任何文件
    - 不破坏 knowledge/ 现有数据结构和流动路径
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────
# 路径
# ─────────────────────────────────────────────

PROJECT_ROOT = Path("/Users/ll/Desktop/LinSai-CoPilot")
NSFC_KB_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "projects" / "NSFC-强场超快"
PROPOSALS_ROOT = PROJECT_ROOT / "research_proposals" / "optimizing"

# 新目录
VERSIONS_DIR = NSFC_KB_DIR / "versions"
REPORTS_DIR = NSFC_KB_DIR / "reports"

# 旧索引
PROPOSALS_INDEX = NSFC_KB_DIR / "proposals-index.md"
MOC_FILE = NSFC_KB_DIR / "MOC.md"

# 5 个优化中课题
OPTIMIZING_PROPOSALS = [
    "general-bsv-driven-hhg-quantum-20260726",
    "general-moire-strong-field-probe-20260726",
    "general-order-parameter-ultrafast-readout-20260727",
    "general-quantum-geometry-inversion-20260726",
    "key-transient-quantum-phase-optical-20260726",
]

PROPOSAL_LABELS = {
    "general-bsv-driven-hhg-quantum-20260726": "BSV-HHG 量子光场驱动",
    "general-moire-strong-field-probe-20260726": "莫尔超晶格强场探针",
    "general-order-parameter-ultrafast-readout-20260727": "序参量超快读出",
    "general-quantum-geometry-inversion-20260726": "量子几何反演",
    "key-transient-quantum-phase-optical-20260726": "瞬态量子相全光读写",
}

# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_file(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def build_frontmatter(fm: Dict[str, Any]) -> str:
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, str):
            lines.append(f'{k}: "{v}"')
        elif isinstance(v, bool):
            lines.append(f"{k}: {json.dumps(v)}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif isinstance(v, list):
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
        else:
            lines.append(f'{k}: "{v}"')
    lines.append("---")
    return "\n".join(lines)


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    fm: Dict[str, Any] = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            for line in fm_text.split("\n"):
                line = line.strip()
                if ":" in line:
                    key, _, val = line.partition(":")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    fm[key] = val
    return fm, body


def _extract_title(text: str) -> str:
    """从 proposal markdown 中提取标题。"""
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip()
    return ""


def _get_latest_round(prop_dir: Path) -> Tuple[int, str]:
    """获取提案最新轮次和 merged 文件路径。"""
    proposal_dir = prop_dir / "04_proposal"
    if not proposal_dir.exists():
        return 0, ""

    merged = proposal_dir / "proposal-draft-merged.md"
    if merged.exists():
        # 从文件名推断最高轮次
        max_round = 0
        for f in proposal_dir.glob("proposal-draft-r*.md"):
            m = re.search(r"r(\d+)", f.name)
            if m:
                r = int(m.group(1))
                if r > max_round:
                    max_round = r
        return max_round, str(merged)

    return 0, ""


# ─────────────────────────────────────────────
# 核心整理逻辑
# ─────────────────────────────────────────────

class KBProposalReorg:
    """知识库提案整理器。"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.stats: Dict[str, Any] = {
            "versions_created": 0,
            "reports_created": 0,
            "index_updated": False,
            "moc_updated": False,
            "errors": [],
            "details": [],
        }

    def run(self) -> None:
        """执行整理。"""
        print(f"{'='*60}")
        print(f"知识库提案整理 {'（DRY RUN）' if self.dry_run else '（实际写入）'}")
        print(f"{'='*60}\n")

        # 1. 创建目录
        self._ensure_dirs()

        # 2. 处理每个提案
        for pid in OPTIMIZING_PROPOSALS:
            prop_dir = PROPOSALS_ROOT / pid
            if not prop_dir.exists():
                print(f"  ○ 跳过（目录不存在）: {pid}")
                continue
            self._process_proposal(pid, prop_dir)

        # 3. 更新索引
        self._update_proposals_index()
        self._update_moc()

        # 4. 报告
        self._print_report()

    def _ensure_dirs(self) -> None:
        """确保新目录存在。"""
        if not self.dry_run:
            VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            (NSFC_KB_DIR / ".gitkeep").touch(exist_ok=True)
        print(f"  ✓ 目录已就绪: versions/ reports/")

    def _process_proposal(self, proposal_id: str, prop_dir: Path) -> None:
        """处理单个提案。"""
        label = PROPOSAL_LABELS.get(proposal_id, proposal_id)
        print(f"\n  [{label}] ({proposal_id})")

        latest_round, merged_path = _get_latest_round(prop_dir)

        # 创建版本页
        if merged_path:
            self._create_version_page(proposal_id, label, prop_dir, merged_path, latest_round)

        # 创建报告页
        self._create_report_page(proposal_id, label, prop_dir, latest_round)

    def _create_version_page(
        self,
        proposal_id: str,
        label: str,
        prop_dir: Path,
        merged_path: str,
        latest_round: int,
    ) -> None:
        """创建最新版本快照页。"""
        merged_file = Path(merged_path)
        merged_text = read_file(merged_file)
        merged_lines = merged_text.count("\n") + 1 if merged_text else 0

        # 获取提案类型
        project_type = "general"
        if "key-" in proposal_id:
            project_type = "key"
        elif "major-" in proposal_id:
            project_type = "major"

        # 获取当前分数
        lifecycle_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
        lifecycle = load_json(lifecycle_path) or {}
        proposals_data = lifecycle.get("proposals", {})
        prop_data = proposals_data.get(proposal_id, {})
        last_score = prop_data.get("last_score", 0)

        # 标题
        title = _extract_title(merged_text) or label

        # 构建版本页
        rel_source = f"research_proposals/optimizing/{proposal_id}/04_proposal/proposal-draft-merged.md"

        # 获取各章节摘要
        sections_dir = prop_dir / "04_proposal" / "sections"
        section_summaries = []
        if sections_dir.exists():
            for sec_file in sorted(sections_dir.glob("*.md")):
                sec_text = read_file(sec_file)
                sec_title = _extract_title(sec_text) or sec_file.stem
                sec_lines = sec_text.count("\n") + 1 if sec_text else 0
                section_summaries.append((sec_file.stem, sec_title, sec_lines))

        # 获取 proposal brief
        brief_text = read_file(prop_dir / "00_proposal-brief.md")

        frontmatter = {
            "title": f"{label} — 最新版本",
            "type": "proposal_version",
            "proposal_id": proposal_id,
            "project_type": project_type,
            "latest_round": latest_round,
            "last_score": last_score,
            "status": "optimizing",
            "created": now_utc(),
            "updated": now_utc(),
            "project": ["NSFC-强场超快"],
            "growth_stage": "growing",
            "confidence": 1.0,
        }

        lines = [build_frontmatter(frontmatter), ""]
        lines.append(f"# {label} — 最新版本")
        lines.append("")
        lines.append(f"**课题 ID**：`{proposal_id}`")
        lines.append(f"**类型**：{project_type}")
        lines.append(f"**最新轮次**：第 {latest_round} 轮")
        lines.append(f"**当前分数**：{last_score}")
        lines.append(f"**状态**：优化中")
        lines.append(f"**同步时间**：{now_utc()}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 章节概览
        if section_summaries:
            lines.append("## 章节概览")
            lines.append("")
            lines.append("| 章节 | 标题 | 行数 |")
            lines.append("|------|------|------|")
            for stem, sec_title, sec_lines in section_summaries:
                lines.append(f"| {stem} | {sec_title} | {sec_lines} |")
            lines.append("")

        # 提案摘要
        if brief_text:
            brief_body = brief_text
            # 跳过 frontmatter
            if brief_text.startswith("---"):
                _, brief_body = parse_frontmatter(brief_text)
            lines.append("## 课题简介")
            lines.append("")
            lines.append(brief_body[:800])
            if len(brief_body) > 800:
                lines.append("")
                lines.append(f"（完整简介见 [源文件]({rel_source})）")
            lines.append("")

        # 来源链接
        lines.append("## 来源")
        lines.append("")
        lines.append(f"- 最新申请书：[{rel_source}]({rel_source})")
        lines.append(f"- 各章节文件：`research_proposals/optimizing/{proposal_id}/04_proposal/sections/`")
        lines.append(f"- 优化报告：[reports/{proposal_id}.md](reports/{proposal_id}.md)")
        lines.append("")
        lines.append(f"> 本页由 `scripts/kb_proposal_reorg.py` 自动生成。")

        content = "\n".join(lines)

        if not self.dry_run:
            out_path = VERSIONS_DIR / f"{proposal_id}.md"
            out_path.write_text(content, encoding="utf-8")

        self.stats["versions_created"] += 1
        self.stats["details"].append(f"  ✓ 版本页: versions/{proposal_id}.md (r{latest_round}, {merged_lines}行)")

    def _create_report_page(
        self,
        proposal_id: str,
        label: str,
        prop_dir: Path,
        latest_round: int,
    ) -> None:
        """创建优化报告汇总页。"""
        review_dir = prop_dir / "05_review"
        if not review_dir.exists():
            print(f"    ○ 无评审目录: 05_review/")
            return

        # 收集所有评审文件
        critic_rounds = sorted(review_dir.glob("critic-round-*.md"))
        meta_reviews = sorted(review_dir.glob("meta-review-*.md"))
        review_reports = sorted(review_dir.glob("review-report*.md"))

        # 获取各轮分数（从 round 文件名推断）
        round_info = []
        for f in critic_rounds:
            m = re.search(r"round-(\d+)", f.name)
            r = int(m.group(1)) if m else 0
            round_info.append((r, f.name))

        # 获取当前分数
        lifecycle_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
        lifecycle = load_json(lifecycle_path) or {}
        proposals_data = lifecycle.get("proposals", {})
        prop_data = proposals_data.get(proposal_id, {})
        last_score = prop_data.get("last_score", 0)

        frontmatter = {
            "title": f"{label} — 优化报告",
            "type": "proposal_reports",
            "proposal_id": proposal_id,
            "latest_round": latest_round,
            "last_score": last_score,
            "critic_rounds": len(critic_rounds),
            "created": now_utc(),
            "updated": now_utc(),
            "project": ["NSFC-强场超快"],
            "growth_stage": "growing",
            "confidence": 1.0,
        }

        rel_review_dir = f"research_proposals/optimizing/{proposal_id}/05_review/"

        lines = [build_frontmatter(frontmatter), ""]
        lines.append(f"# {label} — 优化报告")
        lines.append("")
        lines.append(f"**课题 ID**：`{proposal_id}`")
        lines.append(f"**累计轮次**：{latest_round}")
        lines.append(f"**当前分数**：{last_score}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 对抗评审轮次
        if round_info:
            lines.append(f"## 对抗评审（共 {len(round_info)} 轮）")
            lines.append("")
            lines.append("| 轮次 | 文件 |")
            lines.append("|------|------|")
            for r, fname in sorted(round_info, key=lambda x: x[0]):
                lines.append(f"| 第 {r} 轮 | [{fname}]({rel_review_dir}{fname}) |")
            lines.append("")

        # Meta-review
        if meta_reviews:
            lines.append("## 独立评审")
            lines.append("")
            for f in meta_reviews:
                lines.append(f"- [{f.name}]({rel_review_dir}{f.name})")
            lines.append("")

        # Review report
        if review_reports:
            lines.append("## 综合评审报告")
            lines.append("")
            for f in review_reports:
                lines.append(f"- [{f.name}]({rel_review_dir}{f.name})")
            lines.append("")

        # 如果没有评审文件
        if not critic_rounds and not meta_reviews and not review_reports:
            lines.append("（暂无评审记录）")
            lines.append("")

        # 来源
        lines.append("## 来源")
        lines.append("")
        lines.append(f"- 评审目录：`{rel_review_dir}`")
        lines.append(f"- 最新版本：[versions/{proposal_id}.md](versions/{proposal_id}.md)")
        lines.append("")
        lines.append(f"> 本页由 `scripts/kb_proposal_reorg.py` 自动生成。")

        content = "\n".join(lines)

        if not self.dry_run:
            out_path = REPORTS_DIR / f"{proposal_id}.md"
            out_path.write_text(content, encoding="utf-8")

        self.stats["reports_created"] += 1
        self.stats["details"].append(f"  ✓ 报告页: reports/{proposal_id}.md ({len(round_info)}轮评审)")

    def _update_proposals_index(self) -> None:
        """更新 proposals-index.md。"""
        fm = {
            "title": "NSFC 课题生命周期索引",
            "type": "index",
            "created": "2026-08-02T06:02:42Z",
            "updated": now_utc(),
            "tags": [],
            "related": [],
            "source_raw": "",
            "growth_stage": "growing",
            "confidence": 1.0,
            "project": ["NSFC-强场超快"],
        }

        lines = [build_frontmatter(fm), ""]
        lines.append("# NSFC 课题生命周期索引")
        lines.append("")
        lines.append("本页聚合 `research_proposals/` 中各课题的最新状态、版本和优化报告。")
        lines.append("")

        # 生命周期状态图
        lines.append("## 课题总览")
        lines.append("")
        lines.append("| 课题 | 类型 | 当前轮次 | 分数 | 最新版本 | 优化报告 |")
        lines.append("|------|------|---------|------|---------|---------|")

        lifecycle_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
        lifecycle = load_json(lifecycle_path) or {}
        proposals_data = lifecycle.get("proposals", {})

        for pid in OPTIMIZING_PROPOSALS:
            label = PROPOSAL_LABELS.get(pid, pid)
            prop_data = proposals_data.get(pid, {})
            project_type = "重点" if "key-" in pid else "面上"
            latest_round = prop_data.get("optimization_rounds", 0)
            last_score = prop_data.get("last_score", "—")

            version_link = f"[📄](versions/{pid}.md)"
            report_link = f"[📊](reports/{pid}.md)"

            lines.append(
                f"| {label} | {project_type} | 第{latest_round}轮 | {last_score} | {version_link} | {report_link} |"
            )

        lines.append("")
        lines.append("---")
        lines.append("")

        # 知识库结构说明
        lines.append("## 知识库结构")
        lines.append("")
        lines.append("```")
        lines.append("knowledge/wiki/projects/NSFC-强场超快/")
        lines.append("├── MOC.md              ← 知识地图（入口）")
        lines.append("├── proposals-index.md  ← 本页（生命周期索引）")
        lines.append("├── proposals/          ← 元数据同步（由 proposal_kb_sync.py 维护）")
        lines.append("├── versions/           ← 最新申请书快照（本结构新增）")
        lines.append("├── reports/            ← 优化报告汇总（本结构新增）")
        lines.append("├── decisions/          ← 决策记录")
        lines.append("├── topics/             ← 课题方向笔记（T1-T5）")
        lines.append("└── .gitkeep")
        lines.append("```")
        lines.append("")
        lines.append("> 数据流：`research_proposals/`（源）→ `proposal_kb_sync.py` → `proposals/`")
        lines.append("> `research_proposals/`（源）→ `kb_proposal_reorg.py` → `versions/` + `reports/`")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 各课题详细
        lines.append("## 课题详情")
        lines.append("")

        for pid in OPTIMIZING_PROPOSALS:
            label = PROPOSAL_LABELS.get(pid, pid)
            lines.append(f"### {label}")
            lines.append("")
            lines.append(f"- **ID**：`{pid}`")
            lines.append(f"- **类型**：{'重点项目' if 'key-' in pid else '面上项目'}")
            lines.append(f"- **最新版本**：[versions/{pid}.md](versions/{pid}.md)")
            lines.append(f"- **优化报告**：[reports/{pid}.md](reports/{pid}.md)")
            lines.append(f"- **源文件**：`research_proposals/optimizing/{pid}/`")
            lines.append("")

        lines.append("")
        lines.append("> 由 `scripts/kb_proposal_reorg.py` 自动更新。")

        content = "\n".join(lines)

        if not self.dry_run:
            PROPOSALS_INDEX.write_text(content, encoding="utf-8")
            # 同时也保留原索引文件名用于兼容
            # （proposals-index.md 已存在，直接覆盖）

        self.stats["index_updated"] = True
        self.stats["details"].append(f"  ✓ 索引已更新: proposals-index.md")

    def _update_moc(self) -> None:
        """更新 MOC.md，加入新 sections 链接。"""
        text = read_file(MOC_FILE)
        if not text:
            print(f"  ○ MOC.md 不存在，跳过")
            return

        fm, body = parse_frontmatter(text)

        # 更新 frontmatter
        fm["updated"] = now_utc()

        # 构建新正文
        lines = [build_frontmatter(fm), ""]
        lines.append("# 🗺️ NSFC 强场超快课题知识地图")
        lines.append("")
        lines.append("> 本页是 NSFC 强场超快光学课题的知识入口，聚合课题相关概念、方法、人物和论文。")
        lines.append("")
        lines.append("## 📋 课题方向（T1-T5）")
        lines.append("")
        lines.append("| 课题 | 方向 | 进度 |")
        lines.append("|------|------|------|")
        lines.append("| T1 | 量子几何 | 🌳 成熟 |")
        lines.append("| T2 | 谷电子学 | 🌳 成熟 |")
        lines.append("| T3 | 带动力学 | 🌳 成熟 |")
        lines.append("| T4 | 序参量 | 🌳 成熟 |")
        lines.append("| T5 | 反演方法学 | 🌱 起步 |")
        lines.append("")

        # 新增：申请书版本和报告入口
        lines.append("## 📄 申请书与优化报告")
        lines.append("")
        lines.append("| 课题 | 最新版本 | 优化报告 | 状态 |")
        lines.append("|------|---------|---------|------|")

        lifecycle_path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
        lifecycle = load_json(lifecycle_path) or {}
        proposals_data = lifecycle.get("proposals", {})

        for pid in OPTIMIZING_PROPOSALS:
            label = PROPOSAL_LABELS.get(pid, pid)
            prop_data = proposals_data.get(pid, {})
            score = prop_data.get("last_score", "—")
            status = "🔄 优化中"

            version_link = f"[📄](versions/{pid}.md)"
            report_link = f"[📊](reports/{pid}.md)"

            lines.append(f"| {label} | {version_link} | {report_link} | {status} |")

        lines.append("")

        # 保留原有内容
        lines.append("## 🔬 课题相关概念")
        lines.append("")
        lines.append("- [[固体高次谐波]] — 课题核心研究对象")
        lines.append("- [[德鲁德模型]] — 带内电流描述")
        lines.append("- [[拓扑绝缘体]] — 拓扑材料 HHG")
        lines.append("- [[带间跃迁]] / [[带内电流]] — 固体 HHG 双机制")
        lines.append("")
        lines.append("## 🛠️ 相关方法")
        lines.append("")
        lines.append("- [[TDSE求解器]] — 理论计算核心")
        lines.append("- [[RABBITT]] / [[瞬态吸收光谱]] — 实验表征")
        lines.append("")
        lines.append("## 👤 相关团队")
        lines.append("")
        lines.append("- [[Ghimire-Reis]] — 固体 HHG 开创")
        lines.append("- [[北大HHG团队]] — 国内合作")
        lines.append("")
        lines.append("## 📄 课题论文（NSFC-强场超快子库）")
        lines.append("")
        lines.append("raw/papers/ 中标记 project=['NSFC-强场超快'] 的论文：")
        lines.append("- arXiv:1502.07183（拓扑 HHG）")
        lines.append("- arXiv:1806.11232")
        lines.append("- arXiv:2003.10430")
        lines.append("- arXiv:2304.12547")
        lines.append("- arXiv:2503.08052（滑移铁电 HHG）")
        lines.append("")
        lines.append("## 🔗 外部链接")
        lines.append("")
        lines.append("- hermes 课题目录：`~/Desktop/hermes_workspace/research_proposals/2026_NSFG_strongfield_ultrafast/`")
        lines.append("- 林赛课题目录：`research_proposals/optimizing/`")
        lines.append("")

        content = "\n".join(lines)

        if not self.dry_run:
            MOC_FILE.write_text(content, encoding="utf-8")

        self.stats["moc_updated"] = True
        self.stats["details"].append(f"  ✓ MOC 已更新: MOC.md")

    def _print_report(self) -> None:
        """打印整理报告。"""
        print(f"\n{'='*60}")
        print(f"整理报告 {'（DRY RUN — 未实际写入）' if self.dry_run else '（已写入）'}")
        print(f"{'='*60}")

        s = self.stats
        print(f"\n  ✓ 版本页创建: {s['versions_created']}/5")
        print(f"  ✓ 报告页创建: {s['reports_created']}/5")
        print(f"  ✓ 索引更新: {s['index_updated']}")
        print(f"  ✓ MOC 更新: {s['moc_updated']}")
        print(f"  ✗ 错误: {len(s['errors'])}")

        if s["details"]:
            print(f"\n变更详情:")
            for d in s["details"]:
                print(f"  {d}")

        if s["errors"]:
            print(f"\n错误详情:")
            for e in s["errors"]:
                print(f"  ✗ {e}")

        print(f"\n{'='*60}")
        print(f"知识库新增结构：")
        print(f"  {NSFC_KB_DIR}/")
        print(f"  ├── versions/       ← 5 篇最新申请书快照")
        print(f"  ├── reports/        ← 5 篇优化报告汇总")
        print(f"  ├── proposals/      ← 保留（元数据同步）")
        print(f"  ├── proposals-index.md（已更新）")
        print(f"  └── MOC.md          （已更新）")
        print(f"{'='*60}")
        print(f"数据流：")
        print(f"  research_proposals/（源）→ kb_proposal_reorg.py → versions/ + reports/")
        print(f"  research_proposals/（源）→ proposal_kb_sync.py → proposals/（不变）")
        print(f"  └── 不修改源文件，不影响现有数据流动")
        print(f"{'='*60}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="知识库提案整理脚本")
    parser.add_argument("--apply", action="store_true", help="实际写入（默认 dry-run）")
    parser.add_argument("--report", action="store_true", help="仅生成报告")
    args = parser.parse_args()

    if args.report:
        reorg = KBProposalReorg(dry_run=True)
        reorg.run()
        return

    reorg = KBProposalReorg(dry_run=not args.apply)
    reorg.run()


if __name__ == "__main__":
    main()