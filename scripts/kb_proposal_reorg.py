#!/usr/bin/env python3
"""知识库提案整理脚本 —— 将最新申请书版本和优化报告纳入知识库统一管理。

依据最新架构设计（v6.8+），在 knowledge/wiki/projects/NSFC-强场超快/ 下维护：
  - versions/      ← 最新申请书快照（含 frontmatter + 链接到源文件）
  - reports/       ← 优化报告汇总（含各轮评审链接 + 评分变化表）

v6.8.5 改进：
  - 动态扫描 _lifecycle.json 获取所有 proposal（不再硬编码列表）
  - 动态查找 proposal 目录（覆盖 drafts/optimizing/pending_review/archived）
  - reports 页面加入评分变化表（从 optimization-report-round-N.md 提取）
  - reports 页面加入优化报告链接

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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NSFC_KB_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "projects" / "NSFC-强场超快"
PROPOSALS_ROOT = PROJECT_ROOT / "research_proposals"

# 新目录
VERSIONS_DIR = NSFC_KB_DIR / "versions"
REPORTS_DIR = NSFC_KB_DIR / "reports"

# 旧索引
PROPOSALS_INDEX = NSFC_KB_DIR / "proposals-index.md"
MOC_FILE = NSFC_KB_DIR / "MOC.md"

# 所有生命周期阶段（查找 proposal 目录时按此顺序搜索）
_LIFECYCLE_STAGES = ["drafts", "optimizing", "pending_review", "archived"]

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


def _extract_label(proposal_id: str, brief_text: str) -> str:
    """从 proposal-brief 中提取可读标签，回退到 ID。"""
    title = _extract_title(brief_text)
    if title:
        return title[:40]
    # 从 ID 推断
    parts = proposal_id.split("-")
    if len(parts) > 1:
        return parts[1] if not parts[0].startswith(("general", "key", "major")) else "-".join(parts[1:-1])
    return proposal_id


def _find_proposal_dir(proposal_id: str) -> Tuple[Optional[Path], str]:
    """动态查找 proposal 目录，返回 (path, stage)。"""
    for stage in _LIFECYCLE_STAGES:
        d = PROPOSALS_ROOT / stage / proposal_id
        if d.exists():
            return d, stage
    return None, ""


def _get_all_proposals() -> List[Tuple[str, str, Path]]:
    """从 _lifecycle.json 动态获取所有 proposal。

    Returns:
        [(proposal_id, stage, prop_dir), ...] 按状态优先级排序
    """
    lifecycle = load_json(PROPOSALS_ROOT / "_lifecycle.json") or {}
    proposals = lifecycle.get("proposals", {})
    result = []
    for pid in sorted(proposals.keys()):
        prop_dir, stage = _find_proposal_dir(pid)
        if prop_dir:
            result.append((pid, stage, prop_dir))
    return result


def _get_latest_round(prop_dir: Path) -> Tuple[int, str]:
    """获取提案最新轮次和 merged 文件路径。"""
    proposal_dir = prop_dir / "04_proposal"
    if not proposal_dir.exists():
        return 0, ""

    merged = proposal_dir / "proposal-draft-merged.md"
    if merged.exists():
        max_round = 0
        for f in proposal_dir.glob("proposal-draft-r*.md"):
            m = re.search(r"r(\d+)", f.name)
            if m:
                r = int(m.group(1))
                if r > max_round:
                    max_round = r
        return max_round, str(merged)

    return 0, ""


def _parse_optimization_report(report_path: Path) -> Optional[Dict[str, Any]]:
    """从 optimization-report-round-N.md 提取评分变化数据。

    Returns:
        {round, scores: {metric: {prev, curr, delta}}, total: {prev, curr, delta}}
    """
    text = read_file(report_path)
    if not text:
        return None

    result: Dict[str, Any] = {"round": 0, "scores": {}, "total": {}}

    # 提取轮次
    m = re.search(r"第\s*(\d+)\s*轮", text)
    if m:
        result["round"] = int(m.group(1))

    # 提取评分变化表
    # 格式: | innovation | 0.85 | 0.30 | -0.55 |
    # 总分行可能有 ** 加粗: | **总分** | **0.79** | **0.81** | **+0.02** |
    lines = text.split("\n")
    in_table = False
    for line in lines:
        if "| 指标 |" in line or "| metric |" in line:
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            # 去除 ** 加粗标记
            clean_line = line.replace("**", "")
            cells = [c.strip() for c in clean_line.split("|")]
            cells = [c for c in cells if c]  # 去除空字符串
            if len(cells) >= 4:
                metric = cells[0]
                try:
                    prev = float(cells[1])
                    curr = float(cells[2])
                    delta_str = cells[3].replace("+", "")
                    delta = float(delta_str)
                    if metric in ("总分", "total", "overall"):
                        result["total"] = {"prev": prev, "curr": curr, "delta": delta}
                    else:
                        result["scores"][metric] = {"prev": prev, "curr": curr, "delta": delta}
                except (ValueError, IndexError):
                    pass

    return result if result["scores"] or result["total"] else None


def _collect_score_history(prop_dir: Path) -> List[Dict[str, Any]]:
    """收集所有优化报告的评分历史。

    Returns:
        [{round, total_curr, total_prev, delta, ...}, ...] 按轮次排序
    """
    review_dir = prop_dir / "05_review"
    if not review_dir.exists():
        return []

    history = []
    for report_file in sorted(review_dir.glob("optimization-report-round-*.md")):
        data = _parse_optimization_report(report_file)
        if data:
            entry = {
                "round": data["round"],
                "total": data.get("total", {}),
                "scores": data.get("scores", {}),
                "file": report_file.name,
            }
            history.append(entry)

    history.sort(key=lambda x: x["round"])
    return history


def _status_cn(stage: str) -> str:
    return {
        "drafts": "初稿",
        "optimizing": "优化中",
        "pending_review": "待校验",
        "archived": "已归档",
    }.get(stage, stage)


def _format_delta(delta: float) -> str:
    """格式化分数变化，带正负号。"""
    if delta > 0:
        return f"+{delta:.2f}"
    return f"{delta:.2f}"


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
        all_proposals = _get_all_proposals()
        print(f"{'='*60}")
        print(f"知识库提案整理 {'（DRY RUN）' if self.dry_run else '（实际写入）'}")
        print(f"发现 {len(all_proposals)} 个已注册课题")
        print(f"{'='*60}\n")

        # 1. 创建目录
        self._ensure_dirs()

        # 2. 处理每个提案
        for pid, stage, prop_dir in all_proposals:
            self._process_proposal(pid, stage, prop_dir)

        # 3. 更新索引
        self._update_proposals_index(all_proposals)
        self._update_moc(all_proposals)

        # 4. 报告
        self._print_report()

    def _ensure_dirs(self) -> None:
        """确保新目录存在。"""
        if not self.dry_run:
            VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            (NSFC_KB_DIR / ".gitkeep").touch(exist_ok=True)
        print(f"  ✓ 目录已就绪: versions/ reports/")

    def _process_proposal(self, proposal_id: str, stage: str, prop_dir: Path) -> None:
        """处理单个提案。"""
        brief_text = read_file(prop_dir / "00_proposal-brief.md")
        label = _extract_label(proposal_id, brief_text)
        print(f"\n  [{label}] ({proposal_id}) [{_status_cn(stage)}]")

        latest_round, merged_path = _get_latest_round(prop_dir)

        # 创建版本页
        if merged_path:
            self._create_version_page(proposal_id, label, stage, prop_dir, merged_path, latest_round)

        # 创建报告页
        self._create_report_page(proposal_id, label, stage, prop_dir, latest_round)

    def _create_version_page(
        self,
        proposal_id: str,
        label: str,
        stage: str,
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
        lifecycle = load_json(PROPOSALS_ROOT / "_lifecycle.json") or {}
        prop_data = lifecycle.get("proposals", {}).get(proposal_id, {})
        last_score = prop_data.get("last_score", 0)

        # 标题
        title = _extract_title(merged_text) or label

        # 构建版本页
        rel_source = f"research_proposals/{stage}/{proposal_id}/04_proposal/proposal-draft-merged.md"

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
            "status": stage,
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
        lines.append(f"**状态**：{_status_cn(stage)}")
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
        lines.append(f"- 各章节文件：`research_proposals/{stage}/{proposal_id}/04_proposal/sections/`")
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
        stage: str,
        prop_dir: Path,
        latest_round: int,
    ) -> None:
        """创建优化报告汇总页（含评分变化表）。"""
        review_dir = prop_dir / "05_review"
        if not review_dir.exists():
            print(f"    ○ 无评审目录: 05_review/")
            return

        # 收集所有评审文件
        critic_rounds = sorted(review_dir.glob("critic-round-*.md"))
        meta_reviews = sorted(review_dir.glob("meta-review-*.md"))
        review_reports = sorted(review_dir.glob("review-report*.md"))
        opt_reports = sorted(review_dir.glob("optimization-report-round-*.md"))

        # 收集评分历史
        score_history = _collect_score_history(prop_dir)

        # 各轮 critic 信息
        round_info = []
        for f in critic_rounds:
            m = re.search(r"round-(\d+)", f.name)
            r = int(m.group(1)) if m else 0
            round_info.append((r, f.name))

        # 获取当前分数
        lifecycle = load_json(PROPOSALS_ROOT / "_lifecycle.json") or {}
        prop_data = lifecycle.get("proposals", {}).get(proposal_id, {})
        last_score = prop_data.get("last_score", 0)

        frontmatter = {
            "title": f"{label} — 优化报告",
            "type": "proposal_reports",
            "proposal_id": proposal_id,
            "latest_round": latest_round,
            "last_score": last_score,
            "critic_rounds": len(critic_rounds),
            "optimization_reports": len(opt_reports),
            "status": stage,
            "created": now_utc(),
            "updated": now_utc(),
            "project": ["NSFC-强场超快"],
            "growth_stage": "growing",
            "confidence": 1.0,
        }

        rel_review_dir = f"research_proposals/{stage}/{proposal_id}/05_review/"

        lines = [build_frontmatter(frontmatter), ""]
        lines.append(f"# {label} — 优化报告")
        lines.append("")
        lines.append(f"**课题 ID**：`{proposal_id}`")
        lines.append(f"**累计轮次**：{latest_round}")
        lines.append(f"**当前分数**：{last_score}")
        lines.append(f"**状态**：{_status_cn(stage)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 评分变化趋势
        if score_history:
            lines.append("## 评分变化趋势")
            lines.append("")
            lines.append("| 轮次 | 总分 | 变化 | innovation | feasibility | rigor | completeness |")
            lines.append("|------|------|------|------------|-------------|-------|-------------|")

            prev_total = None
            for entry in score_history:
                r = entry["round"]
                total = entry.get("total", {})
                curr_total = total.get("curr", 0)
                delta_str = _format_delta(total.get("delta", 0)) if total else "—"

                scores = entry.get("scores", {})
                innov = scores.get("innovation", {}).get("curr", "—")
                feas = scores.get("feasibility", {}).get("curr", "—")
                rigor = scores.get("rigor", {}).get("curr", "—")
                complet = scores.get("completeness", {}).get("curr", "—")

                def _fmt(v):
                    return f"{v:.2f}" if isinstance(v, float) else str(v)

                lines.append(
                    f"| 第 {r} 轮 | {_fmt(curr_total)} | {delta_str} | "
                    f"{_fmt(innov)} | {_fmt(feas)} | {_fmt(rigor)} | {_fmt(complet)} |"
                )
            lines.append("")

        # 优化报告链接
        if opt_reports:
            lines.append(f"## 优化报告（共 {len(opt_reports)} 份）")
            lines.append("")
            lines.append("| 轮次 | 报告 |")
            lines.append("|------|------|")
            for f in opt_reports:
                m = re.search(r"round-(\d+)", f.name)
                r = int(m.group(1)) if m else 0
                lines.append(f"| 第 {r} 轮 | [{f.name}]({rel_review_dir}{f.name}) |")
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
        if not critic_rounds and not meta_reviews and not review_reports and not opt_reports:
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
        self.stats["details"].append(
            f"  ✓ 报告页: reports/{proposal_id}.md ({len(round_info)}轮评审, {len(opt_reports)}份优化报告)"
        )

    def _update_proposals_index(self, all_proposals: List[Tuple[str, str, Path]]) -> None:
        """更新 proposals-index.md。"""
        lifecycle = load_json(PROPOSALS_ROOT / "_lifecycle.json") or {}
        proposals_data = lifecycle.get("proposals", {})

        fm = {
            "title": "NSFC 课题生命周期索引",
            "type": "index",
            "created": now_utc(),
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
        lines.append("| 课题 | 类型 | 状态 | 当前轮次 | 分数 | 最新版本 | 优化报告 |")
        lines.append("|------|------|------|---------|------|---------|---------|")

        for pid, stage, prop_dir in all_proposals:
            brief_text = read_file(prop_dir / "00_proposal-brief.md")
            label = _extract_label(pid, brief_text)
            prop_data = proposals_data.get(pid, {})
            project_type = "重点" if "key-" in pid else ("重大" if "major-" in pid else "面上")
            latest_round = prop_data.get("optimization_rounds", 0)
            last_score = prop_data.get("last_score", "—")

            version_link = f"[版本](versions/{pid}.md)"
            report_link = f"[报告](reports/{pid}.md)"

            lines.append(
                f"| {label} | {project_type} | {_status_cn(stage)} | 第{latest_round}轮 | "
                f"{last_score} | {version_link} | {report_link} |"
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
        lines.append("├── versions/           ← 最新申请书快照（由 kb_proposal_reorg.py 维护）")
        lines.append("├── reports/            ← 优化报告汇总 + 评分变化表（由 kb_proposal_reorg.py 维护）")
        lines.append("├── decisions/          ← 决策记录")
        lines.append("├── topics/             ← 课题方向笔记（T1-T5）")
        lines.append("└── .gitkeep")
        lines.append("```")
        lines.append("")
        lines.append("> 数据流：`research_proposals/`（源）→ `proposal_kb_sync.py` → `proposals/`")
        lines.append("> `research_proposals/`（源）→ `kb_proposal_reorg.py` → `versions/` + `reports/`")
        lines.append("")
        lines.append(f"> 由 `scripts/kb_proposal_reorg.py` 自动更新（{now_utc()[:10]}）。")

        content = "\n".join(lines)

        if not self.dry_run:
            PROPOSALS_INDEX.write_text(content, encoding="utf-8")

        self.stats["index_updated"] = True
        self.stats["details"].append(f"  ✓ 索引已更新: proposals-index.md")

    def _update_moc(self, all_proposals: List[Tuple[str, str, Path]]) -> None:
        """更新 MOC.md，加入课题链接。"""
        text = read_file(MOC_FILE)
        if not text:
            print(f"  ○ MOC.md 不存在，跳过")
            return

        fm, body = parse_frontmatter(text)
        fm["updated"] = now_utc()

        lifecycle = load_json(PROPOSALS_ROOT / "_lifecycle.json") or {}
        proposals_data = lifecycle.get("proposals", {})

        lines = [build_frontmatter(fm), ""]
        lines.append("# NSFC 强场超快课题知识地图")
        lines.append("")
        lines.append("> 本页是 NSFC 强场超快光学课题的知识入口，聚合课题相关概念、方法、人物和论文。")
        lines.append("")

        # 课题总览
        lines.append("## 申请书与优化报告")
        lines.append("")
        lines.append("| 课题 | 状态 | 轮次 | 分数 | 版本 | 报告 |")
        lines.append("|------|------|------|------|------|------|")

        for pid, stage, prop_dir in all_proposals:
            brief_text = read_file(prop_dir / "00_proposal-brief.md")
            label = _extract_label(pid, brief_text)
            prop_data = proposals_data.get(pid, {})
            latest_round = prop_data.get("optimization_rounds", 0)
            last_score = prop_data.get("last_score", "—")

            version_link = f"[版本](versions/{pid}.md)"
            report_link = f"[报告](reports/{pid}.md)"

            lines.append(
                f"| {label} | {_status_cn(stage)} | 第{latest_round}轮 | {last_score} | "
                f"{version_link} | {report_link} |"
            )

        lines.append("")

        # 保留原有 body 中非自动生成的部分
        # 提取 "## 课题相关概念" 及之后的内容
        preserved_sections = []
        capture = False
        for line in body.split("\n"):
            if "课题相关概念" in line or "相关方法" in line or "相关团队" in line or "课题论文" in line or "外部链接" in line:
                capture = True
            if capture:
                preserved_sections.append(line)

        if preserved_sections:
            lines.extend(preserved_sections)
        else:
            # 回退：保留所有原始内容
            lines.append(body)

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
        print(f"\n  ✓ 版本页创建: {s['versions_created']}")
        print(f"  ✓ 报告页创建: {s['reports_created']}")
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
