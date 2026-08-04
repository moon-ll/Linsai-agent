#!/usr/bin/env python3
"""Proposal 知识库同步工具（v6.8.2）。

将 research_proposals/ 下各课题的核心信息同步到 NSFC-强场超快知识库，
实现生命周期数据与全链路知识库的聚合。
同步完成后自动调用 kb_proposal_reorg.py 更新 versions/ 和 reports/。

用法：
    python3 scripts/proposal_kb_sync.py --sync-all
    python3 scripts/proposal_kb_sync.py --sync <proposal_id>
    python3 scripts/proposal_kb_sync.py --dry-run
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import load_json, now_utc, save_json
from paths import PROJECT_ROOT
from knowledge_base import save_proposal_sync, _slugify
import kb_wiki

try:
    from logger import get_logger
    _log = get_logger("proposal_kb_sync")
except Exception:
    _log = None

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

NSFC_KB_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "projects" / "NSFC-强场超快"
PROPOSALS_ROOT = PROJECT_ROOT / "research_proposals"
PROPOSALS_KB_SUBDIR = "proposals"
INDEX_FILENAME = "proposals-index.md"


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _safe_read(path: Path, max_chars: int = 5000) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
        return text[:max_chars]
    except Exception:
        return ""


def _extract_section(text: str, heading: str) -> str:
    """从 markdown 文本中提取指定 ## 章节内容。"""
    lines = text.split("\n")
    in_section = False
    section_lines = []
    for line in lines:
        if line.strip().startswith("## "):
            if in_section:
                break
            if heading in line:
                in_section = True
                continue
        if in_section:
            section_lines.append(line)
    return "\n".join(section_lines).strip()


def _extract_title_from_brief(text: str) -> str:
    for line in text.split("\n"):
        if "课题名称" in line and "**" in line:
            parts = line.split("：", 1)
            if len(parts) > 1:
                return parts[1].strip().strip("*").strip()
    return ""


def _extract_core_questions(prop_dir: Path) -> str:
    q_path = prop_dir / "03_question" / "question-framework.md"
    text = _safe_read(q_path, 3000)
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if (stripped.startswith("Q") and (":" in stripped or "：" in stripped) and len(stripped) > 5):
            lines.append(stripped)
        elif "主问题" in stripped and ("**" in stripped or len(stripped) > 10):
            lines.append(stripped)
    return "\n".join(lines[:6])


def _extract_innovations(prop_dir: Path) -> str:
    p_path = prop_dir / "04_proposal" / "proposal-draft.md"
    text = _safe_read(p_path, 5000)
    lines = []
    in_innovation = False
    for line in text.split("\n"):
        if "特色" in line and "创新" in line and "##" in line:
            in_innovation = True
            continue
        if in_innovation:
            if line.strip().startswith("## ") and "创新" not in line and "特色" not in line:
                break
            stripped = line.strip()
            if stripped.startswith("###") or (len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in "."):
                lines.append(stripped.lstrip("#").strip())
    return "\n".join(lines[:6])


def _extract_key_files(prop_dir: Path) -> List[Dict[str, str]]:
    """提取关键产物文件相对路径。"""
    files = []
    key_paths = [
        ("proposal-brief", "00_proposal-brief.md"),
        ("question-framework", "03_question/question-framework.md"),
        ("method-manual", "03_method/method-manual.md"),
        ("reading-notes", "02_literature/reading-notes.md"),
        ("proposal-draft", "04_proposal/proposal-draft.md"),
    ]
    for label, rel_path in key_paths:
        p = prop_dir / rel_path
        if p.exists():
            files.append({"label": label, "path": str(p.relative_to(PROJECT_ROOT))})
    return files


def _run_reorg(dry_run: bool = False) -> None:
    """调用 kb_proposal_reorg.py 更新 versions/ 和 reports/。"""
    reorg_script = _SCRIPT_DIR / "kb_proposal_reorg.py"
    if not reorg_script.exists():
        if _log:
            _log.warning("kb_proposal_reorg.py 不存在，跳过 versions/reports 同步")
        return

    cmd = [sys.executable, str(reorg_script)]
    if not dry_run:
        cmd.append("--apply")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            if _log:
                _log.warning(f"kb_proposal_reorg 返回非零: {result.stderr[:200]}")
        elif _log:
            _log.info("kb_proposal_reorg 同步完成")
    except subprocess.TimeoutExpired:
        if _log:
            _log.warning("kb_proposal_reorg 超时")
    except Exception as e:
        if _log:
            _log.warning(f"kb_proposal_reorg 调用失败: {e}")


# ---------------------------------------------------------------------------
# 同步逻辑
# ---------------------------------------------------------------------------


class ProposalKbSync:
    def __init__(self) -> None:
        self.nsfc_dir = NSFC_KB_DIR
        self.proposals_dir = PROPOSALS_ROOT
        self.proposals_kb_dir = self.nsfc_dir / PROPOSALS_KB_SUBDIR
        self.proposals_kb_dir.mkdir(parents=True, exist_ok=True)
        self.nsfc_dir.mkdir(parents=True, exist_ok=True)

    def _find_proposal_dir(self, proposal_id: str) -> Optional[Path]:
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            d = self.proposals_dir / stage / proposal_id
            if d.exists():
                return d
        return None

    def _load_lifecycle(self) -> Dict[str, Any]:
        lifecycle_path = self.proposals_dir / "_lifecycle.json"
        return load_json(lifecycle_path, default={"proposals": {}})

    def _map_status_cn(self, status: str) -> str:
        return {
            "drafts": "初稿",
            "optimizing": "优化中",
            "pending_review": "待校验",
            "archived": "已归档",
        }.get(status, status)

    def sync_proposal(self, proposal_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """同步单个 proposal 到知识库。"""
        state = self._load_lifecycle()
        prop_state = state["proposals"].get(proposal_id, {})
        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}

        brief_text = _safe_read(prop_dir / "00_proposal-brief.md", 3000)
        title = _extract_title_from_brief(brief_text) or proposal_id
        core_questions = _extract_core_questions(prop_dir)
        innovations = _extract_innovations(prop_dir)
        key_files = _extract_key_files(prop_dir)

        status = prop_state.get("status", "unknown")
        project_type = prop_state.get("project_type", "general")
        rounds = prop_state.get("optimization_rounds", 0)
        last_score = prop_state.get("last_score", 0.0)

        # 构建 metadata 字典，由 knowledge_base.save_proposal_sync 门面统一处理
        metadata = {
            "title": title,
            "proposal_id": proposal_id,
            "status": status,
            "project_type": project_type,
            "optimization_rounds": rounds,
            "last_score": last_score,
            "core_questions": core_questions,
            "innovations": innovations,
            "key_files": key_files,
        }

        if not dry_run:
            kb_path = save_proposal_sync(proposal_id, metadata)
        else:
            slug = _slugify(proposal_id)
            kb_path = f"wiki/projects/NSFC-强场超快/proposals/{slug}.md"

        return {
            "success": True,
            "proposal_id": proposal_id,
            "kb_path": kb_path,
            "title": title,
            "status": status,
        }

    def sync_all(self, dry_run: bool = False) -> Dict[str, Any]:
        """同步所有已注册 proposal，完成后自动更新 versions/ 和 reports/。"""
        state = self._load_lifecycle()
        results = []
        for proposal_id in sorted(state["proposals"].keys()):
            result = self.sync_proposal(proposal_id, dry_run=dry_run)
            results.append(result)
            if _log and result.get("success"):
                _log.info(f"同步 proposal 到知识库: {proposal_id}")

        self._update_index(results, dry_run=dry_run)

        # 同步完成后自动更新 versions/ 和 reports/
        _run_reorg(dry_run=dry_run)

        return {
            "success": True,
            "synced_count": sum(1 for r in results if r.get("success")),
            "failed_count": sum(1 for r in results if not r.get("success")),
            "results": results,
            "dry_run": dry_run,
        }

    def _update_index(self, results: List[Dict[str, Any]], dry_run: bool = False) -> None:
        """更新 proposals-index.md 索引。"""
        rows = []
        for r in sorted(results, key=lambda x: x.get("proposal_id", "")):
            if not r.get("success"):
                continue
            pid = r["proposal_id"]
            title = r.get("title", pid)
            # 标题可能很长（brief 把说明也写进标题行），索引中截断显示
            display_title = title.strip("*# ")
            if len(display_title) > 60:
                display_title = display_title[:57] + "..."
            status = self._map_status_cn(r.get("status", ""))
            md_path = f"{PROPOSALS_KB_SUBDIR}/{pid}.md"
            rows.append(f"| [{display_title}]({md_path}) | `{pid}` | {status} |")

        body = f"""# NSFC 课题生命周期索引

本页自动聚合 `research_proposals/` 中各课题的状态与核心信息。

| 课题 | ID | 状态 |
|------|-----|------|
{chr(10).join(rows) if rows else '| （暂无） | - | - |'}

---

> 由 `scripts/proposal_kb_sync.py` 自动生成，请勿手动修改本表。
"""
        index_meta = {
            "title": "NSFC 课题生命周期索引",
            "type": "index",
            "project": ["NSFC-强场超快"],
            "created": now_utc(),
            "updated": now_utc(),
            "growth_stage": "growing",
            "confidence": 1.0,
        }

        if not dry_run:
            kb_wiki.save_wiki_page(
                f"wiki/projects/NSFC-强场超快/{INDEX_FILENAME}",
                body,
                index_meta,
            )


def _self_check() -> Dict[str, Any]:
    sync = ProposalKbSync()
    result = sync.sync_all(dry_run=True)
    return {"success": result["synced_count"] > 0, "synced_count": result["synced_count"]}


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Proposal 知识库同步")
    parser.add_argument("--sync-all", action="store_true", help="同步所有已注册 proposal")
    parser.add_argument("--sync", metavar="ID", help="同步指定 proposal")
    parser.add_argument("--dry-run", action="store_true", help="只预览不写入")
    parser.add_argument("--self-check", action="store_true", help="模块自检")
    args = parser.parse_args(argv)

    if args.self_check:
        import json
        print(json.dumps(_self_check(), ensure_ascii=False, indent=2))
        return 0

    sync = ProposalKbSync()
    if args.sync:
        result = sync.sync_proposal(args.sync, dry_run=args.dry_run)
        print(f"同步 {args.sync}: {'成功' if result['success'] else '失败'}")
        if result.get("error"):
            print(f"  错误: {result['error']}")
        else:
            print(f"  知识库路径: {result['kb_path']}")
        return 0 if result["success"] else 1

    if args.sync_all:
        result = sync.sync_all(dry_run=args.dry_run)
        mode = "(dry-run)" if args.dry_run else ""
        print(f"同步完成 {mode}: 成功 {result['synced_count']}, 失败 {result['failed_count']}")
        for r in result["results"]:
            status = "✓" if r["success"] else "✗"
            print(f"  {status} {r['proposal_id']}: {r.get('title', '')}")
        return 0 if result["failed_count"] == 0 else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
