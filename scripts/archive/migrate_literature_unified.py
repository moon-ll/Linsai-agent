#!/usr/bin/env python3
"""文献统一架构数据迁移脚本。

用途：
    将现有数据迁移到统一架构，支持 --dry-run 预览模式和 --backup 自动备份。

迁移步骤：
    1. 备份现有数据
    2. 合并 paper-pool 状态到 KB frontmatter
    3. 合并 item-status 历史到 KB frontmatter
    4. 迁移深度解析到 wiki/papers/
    5. 迁移 per-proposal 阅读笔记到 wiki/papers/
    6. 迁移讨论记录到 qa/ 层
    7. 重建索引和图谱
    8. 重建缓存视图

用法：
    python3 scripts/migrate_literature_unified.py --dry-run     # 预览模式
    python3 scripts/migrate_literature_unified.py --backup      # 自动备份
    python3 scripts/migrate_literature_unified.py               # 执行迁移

规范：仅标准库，PROJECT_ROOT 推导，JSON ensure_ascii=False。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# 确保可从 scripts/ 目录直接导入
_SCRIPT_DIR = Path(__file__).parent.resolve()
import sys
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock
from paths import PROJECT_ROOT, KNOWLEDGE_DIR, RAW_DIR, WIKI_DIR, QA_DIR, MEMORY_DIR


# ─────────────────────────────────────────────
# 常量
# ─────────────────────────────────────────────

RAW_PAPERS_DIR = RAW_DIR / "papers"
WIKI_PAPERS_DIR = WIKI_DIR / "papers"
WIKI_PROJECTS_DIR = WIKI_DIR / "projects"
HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
HERMES_STATUS_PATH = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings" / "item-status.json"
PROPOSALS_ROOT = PROJECT_ROOT / "research_proposals"

BACKUP_DIR = PROJECT_ROOT / "backups"

# 图标
ICON_OK = "✓"
ICON_WARN = "⚠"
ICON_SKIP = "○"
ICON_FAIL = "✗"


# ─────────────────────────────────────────────
# 日志
# ─────────────────────────────────────────────

try:
    from logger import get_logger
    _log = get_logger("migrate_literature")
except Exception:
    _log = None


def _log_info(msg: str) -> None:
    if _log:
        _log.info(msg)
    print(f"  {msg}")


def _log_warn(msg: str) -> None:
    if _log:
        _log.warning(msg)
    print(f"  {ICON_WARN} {msg}")


def _log_ok(msg: str) -> None:
    print(f"  {ICON_OK} {msg}")


def _log_fail(msg: str) -> None:
    print(f"  {ICON_FAIL} {msg}")


# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_arxiv_from_filename(filename: str) -> str:
    """从文件名中提取 arxiv_id。"""
    m = re.match(r"\d{4}-(\d{4}\.\d{4,5}(v\d+)?)-", filename)
    if m:
        return m.group(1).split("v")[0]
    m = re.match(r"(\d{4}\.\d{4,5})", filename)
    if m:
        return m.group(1).split("v")[0]
    # 旧格式：arxiv_id.md
    m = re.match(r"(\d{7,8})", filename)
    if m:
        return m.group(1)
    return ""


def _parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """解析 YAML frontmatter。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    content = m.group(2)
    fm: Dict[str, Any] = {}

    for line in m.group(1).split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()

        # 处理 JSON 列表值（如 [item1, item2] 或 [{"status": "pool"}])
        if v.startswith("["):
            try:
                v = json.loads(v)
            except Exception:
                v = [x.strip().strip('"').strip("'") for x in v.strip("[]").split(",") if x.strip()]
        elif v == "true":
            v = True
        elif v == "false":
            v = False
        elif v == "null":
            v = None
        else:
            v = v.strip('"').strip("'")
        fm[k] = v

    # 处理多行列表（以 - 开头的行）
    _extract_list_fields(text, fm)
    return fm, content


def _extract_list_fields(text: str, fm: Dict[str, Any]) -> None:
    """从 frontmatter 中提取列表字段。"""
    # used_by_proposals 等列表字段
    in_list = False
    list_key = ""
    list_values: List[str] = []
    for line in text.split("\n"):
        if line.startswith("---"):
            if in_list:
                break
            continue
        if line.startswith("  - "):
            if in_list:
                list_values.append(line.strip("- ").strip().strip('"').strip("'"))
            continue
        if ":" in line and not line.startswith(" "):
            if in_list and list_key:
                fm[list_key] = list_values
                list_values = []
                in_list = False
            k = line.split(":")[0].strip()
            if k in ("used_by_proposals", "status_history", "tags", "project", "proposals_citations"):
                in_list = True
                list_key = k
                continue
        if in_list:
            in_list = False
            if list_key:
                fm[list_key] = list_values
                list_values = []
    if in_list and list_key:
        fm[list_key] = list_values


def _build_frontmatter(fm: Dict[str, Any]) -> str:
    """构建 YAML frontmatter 文本。

    列表格式规范：
    - 字符串列表用 [...] 单行（如 `tags: [tag1, tag2]`）
    - 字典列表用 JSON 字符串（如 `status_history: [{"status": "pool"}]`），
      确保与 _parse_frontmatter 的解析逻辑兼容。
    """
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            if all(isinstance(item, str) for item in v):
                # 字符串列表 → [...] 单行
                items_str = ", ".join(f'"{item}"' if " " in item or ":" in item else item for item in v)
                lines.append(f"{k}: [{items_str}]")
            elif all(isinstance(item, dict) for item in v):
                # 字典列表 → JSON 字符串（确保可解析回列表）
                json_str = json.dumps(v, ensure_ascii=False)
                lines.append(f"{k}: {json_str}")
            else:
                # 混合类型，兜底
                lines.append(f"{k}:")
                for item in v:
                    lines.append(f"  - {item}")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            lines.append(f'{k}: "{v}"')
    lines.append("---")
    return "\n".join(lines)


def _safe_filename(name: str) -> str:
    """生成安全的文件名片段。"""
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return name[:60].strip('-').lower()


# ─────────────────────────────────────────────
# 迁移步骤
# ─────────────────────────────────────────────


class Migrator:
    """文献统一架构数据迁移器。"""

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.stats: Dict[str, Any] = {
            "paper_pool_merged": 0,
            "item_status_merged": 0,
            "deep_analyses_migrated": 0,
            "reading_notes_migrated": 0,
            "reading_note_entries": 0,
            "discussions_migrated": 0,
            "papers_imported": 0,
            "errors": [],
        }
        # 延迟导入
        self._kb = None
        self._kb_wiki = None

    def _ensure_kb(self) -> None:
        if self._kb is not None:
            return
        import knowledge_base as kb
        self._kb = kb
        from kb_wiki import save_wiki_page, get_wiki_page, build_wiki_page
        self._kw_save = save_wiki_page
        self._kw_get = get_wiki_page
        self._kw_build = build_wiki_page

    # ────────── 步骤 1: 备份 ──────────

    def backup(self) -> Path:
        """创建迁移备份包。"""
        backup_date = _now()[:10]
        # 使用时间戳避免冲突
        timestamp = _now().replace(":", "-").replace("T", "-")
        target_dir = BACKUP_DIR / f"literature-migration-{backup_date}-{timestamp}"
        if self.dry_run:
            _log_info(f"[dry-run] 将创建备份到: {target_dir}")
            return target_dir

        target_dir.mkdir(parents=True, exist_ok=True)
        _log_info(f"创建备份到: {target_dir}")

        # 备份 paper-pool.json
        pool_path = MEMORY_DIR / "paper-pool.json"
        if pool_path.exists():
            shutil.copy2(pool_path, target_dir / "paper-pool.json")
            _log_ok(f"paper-pool.json ({pool_path.stat().st_size} bytes)")

        # 备份 sync-state.json
        sync_path = MEMORY_DIR / "sync-state.json"
        if sync_path.exists():
            shutil.copy2(sync_path, target_dir / "sync-state.json")
            _log_ok(f"sync-state.json")

        # 备份 hermes item-status.json
        if HERMES_STATUS_PATH.exists():
            shutil.copy2(HERMES_STATUS_PATH, target_dir / "item-status.json")
            _log_ok(f"item-status.json")

        # 备份 raw/papers/
        if RAW_PAPERS_DIR.exists():
            raw_backup = target_dir / "raw-papers"
            if raw_backup.exists():
                shutil.rmtree(raw_backup)
            shutil.copytree(RAW_PAPERS_DIR, raw_backup)
            _log_ok(f"raw/papers/ ({len(list(RAW_PAPERS_DIR.glob('*.md')))} 个文件)")

        # 备份 wiki/papers/
        if WIKI_PAPERS_DIR.exists():
            wiki_backup = target_dir / "wiki-papers"
            if wiki_backup.exists():
                shutil.rmtree(wiki_backup)
            shutil.copytree(WIKI_PAPERS_DIR, wiki_backup)
            _log_ok(f"wiki/papers/ ({len(list(WIKI_PAPERS_DIR.glob('*.md')))} 个文件)")

        return target_dir

    # ────────── 步骤 2: 合并 paper-pool 状态到 KB frontmatter ──────────

    def merge_paper_pool_to_kb(self) -> None:
        """合并 paper-pool.json 状态到 KB raw/papers/ frontmatter。"""
        pool_path = MEMORY_DIR / "paper-pool.json"
        if not pool_path.exists():
            _log_info("paper-pool.json 不存在，跳过")
            return

        pool = load_json(pool_path, {})
        if not pool:
            _log_info("paper-pool.json 为空，跳过")
            return

        _log_info(f"合并 paper-pool 状态（共 {len(pool)} 条）...")

        for arxiv_id, entry in pool.items():
            raw_path = self._find_raw_paper(arxiv_id)
            if not raw_path:
                # 论文已入池但未导入 KB，补充导入
                if not self.dry_run:
                    self._import_paper_to_kb(arxiv_id, entry)
                self.stats["papers_imported"] += 1
                continue

            if self.dry_run:
                self.stats["paper_pool_merged"] += 1
                continue

            try:
                text = raw_path.read_text(encoding="utf-8")
                fm, body = _parse_frontmatter(text)

                # 合并状态字段
                pool_status = entry.get("status", "unseen")
                unified_status = entry.get("unified_status", "pool")
                hermes_synced = entry.get("hermes_synced_at", "")

                if "status" not in fm or fm["status"] == "unseen":
                    fm["status"] = pool_status
                if "unified_status" not in fm:
                    fm["unified_status"] = unified_status
                if hermes_synced and "hermes_synced_at" not in fm:
                    fm["hermes_synced_at"] = hermes_synced

                # 确保必填字段存在
                fm.setdefault("read_status", "unread")
                fm.setdefault("used_by_proposals", [])
                fm.setdefault("has_pdf", False)
                fm.setdefault("status_history", [
                    {"status": unified_status, "at": hermes_synced or _now(), "by": "hermes"}
                ])

                new_fm = _build_frontmatter(fm)
                raw_path.write_text(f"{new_fm}\n\n{body.strip()}", encoding="utf-8")
                self.stats["paper_pool_merged"] += 1
            except Exception as e:
                self.stats["errors"].append(f"合并 paper-pool {arxiv_id}: {e}")
                _log_warn(f"合并失败 {arxiv_id}: {e}")

        _log_ok(f"合并 {self.stats['paper_pool_merged']} 条，补充导入 {self.stats['papers_imported']} 篇")

    # ────────── 步骤 3: 合并 item-status 历史到 KB frontmatter ──────────

    def merge_item_status_to_kb(self) -> None:
        """合并 item-status.json 历史到 KB raw/papers/ frontmatter。"""
        if not HERMES_STATUS_PATH.exists():
            _log_info("item-status.json 不存在，跳过")
            return

        try:
            status_data = json.loads(HERMES_STATUS_PATH.read_text(encoding="utf-8"))
        except Exception:
            _log_warn("item-status.json 解析失败，跳过")
            return

        items = status_data.get("items", {})
        if not items:
            _log_info("item-status.json 为空，跳过")
            return

        _log_info(f"合并 item-status 历史（共 {len(items)} 条）...")

        for arxiv_id, item in items.items():
            raw_path = self._find_raw_paper(arxiv_id)
            if not raw_path:
                continue

            if self.dry_run:
                self.stats["item_status_merged"] += 1
                continue

            try:
                text = raw_path.read_text(encoding="utf-8")
                fm, body = _parse_frontmatter(text)

                # 合并 unified_status（以 item-status 为准）
                hermes_status = item.get("status", "")
                if hermes_status:
                    fm["unified_status"] = hermes_status

                # 合并 status_history
                history = item.get("history", [])
                existing_history = fm.get("status_history", [])
                # 兼容旧格式：可能是字符串列表（如 ["{status: pool, by: migration}"])
                if isinstance(existing_history, str):
                    existing_history = []
                elif isinstance(existing_history, list):
                    parsed: List[Dict[str, str]] = []
                    for h in existing_history:
                        if isinstance(h, dict):
                            parsed.append(h)
                        elif isinstance(h, str):
                            # 尝试解析旧格式 {status: pool, at: ..., by: migration}
                            m = re.findall(r'(\w+):\s*([^,}]+)', h)
                            if m:
                                parsed.append({k: v.strip() for k, v in m})
                    existing_history = parsed
                else:
                    existing_history = []
                existing_statuses = {(h.get("status", ""), h.get("by", "")) for h in existing_history}
                for h in history:
                    key = (h.get("status", ""), h.get("by", ""))
                    if key not in existing_statuses:
                        existing_history.append(h)
                        existing_statuses.add(key)
                fm["status_history"] = existing_history

                new_fm = _build_frontmatter(fm)
                raw_path.write_text(f"{new_fm}\n\n{body.strip()}", encoding="utf-8")
                self.stats["item_status_merged"] += 1
            except Exception as e:
                self.stats["errors"].append(f"合并 item-status {arxiv_id}: {e}")
                _log_warn(f"合并失败 {arxiv_id}: {e}")

        _log_ok(f"合并 {self.stats['item_status_merged']} 条")

    # ────────── 步骤 4: 迁移深度解析到 wiki/papers/ ──────────

    def migrate_deep_analysis(self) -> None:
        """迁移深度解析到 wiki/papers/。"""
        analyses_dir = WIKI_PROJECTS_DIR / "deepxiv-论文库" / "analyses"
        if not analyses_dir.exists():
            _log_info("深度解析目录不存在，跳过")
            return

        analysis_files = sorted(analyses_dir.glob("*.md"))
        if not analysis_files:
            _log_info("无深度解析文件，跳过")
            return

        _log_info(f"迁移深度解析（共 {len(analysis_files)} 个文件）...")

        for f in analysis_files:
            arxiv_id = self._extract_arxiv_from_content(f)
            if not arxiv_id:
                _log_warn(f"无法提取 arxiv_id: {f.name}")
                continue

            if self.dry_run:
                self.stats["deep_analyses_migrated"] += 1
                continue

            try:
                self._ensure_kb()
                content = f.read_text(encoding="utf-8")
                wiki_path = WIKI_PAPERS_DIR / f"{arxiv_id}.md"

                if wiki_path.exists():
                    # 追加到现有页面
                    existing = self._kw_get(f"wiki/papers/{arxiv_id}.md")
                    if existing:
                        old_content = existing.get("content", "")
                        new_content = old_content + f"\n\n## 深度解析\n\n{content.strip()}"
                        meta = existing.get("meta", {})
                        meta["updated"] = _now()
                        page = self._kw_build(
                            title=meta.get("title", arxiv_id),
                            wiki_type="papers",
                            content=new_content,
                            meta=meta,
                        )
                        self._kw_save(f"wiki/papers/{arxiv_id}.md", page)
                else:
                    # 创建新页面
                    meta = {
                        "title": f"Paper: {arxiv_id}",
                        "type": "papers",
                        "arxiv_id": arxiv_id,
                        "tags": ["deepxiv-论文库", "deep-analysis"],
                        "project": ["NSFC-强场超快", "deepxiv-论文库"],
                        "read_status": "unread",
                        "used_by_proposals": [],
                        "created": _now(),
                        "updated": _now(),
                        "growth_stage": "seedling",
                        "confidence": 0.5,
                    }
                    page = self._kw_build(
                        title=f"Paper: {arxiv_id}",
                        wiki_type="papers",
                        content=f"## 深度解析\n\n{content.strip()}",
                        meta=meta,
                    )
                    self._kw_save(f"wiki/papers/{arxiv_id}.md", page)

                self.stats["deep_analyses_migrated"] += 1
            except Exception as e:
                self.stats["errors"].append(f"迁移深度解析 {f.name}: {e}")
                _log_warn(f"迁移失败 {f.name}: {e}")

        _log_ok(f"迁移 {self.stats['deep_analyses_migrated']} 篇深度解析")

    # ────────── 步骤 5: 迁移 per-proposal 阅读笔记到 wiki/papers/ ──────────

    def migrate_reading_notes(self) -> None:
        """迁移 per-proposal 阅读笔记到 wiki/papers/。"""
        # 遍历所有 proposal 目录下的 reading-notes.md
        reading_notes_paths = []
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            stage_dir = PROPOSALS_ROOT / stage
            if stage_dir.exists():
                for d in stage_dir.iterdir():
                    if d.is_dir():
                        rn_path = d / "02_literature" / "reading-notes.md"
                        if rn_path.exists():
                            reading_notes_paths.append((d.name, rn_path))

        if not reading_notes_paths:
            _log_info("无 reading-notes 文件，跳过")
            return

        _log_info(f"迁移阅读笔记（共 {len(reading_notes_paths)} 个 proposal）...")

        for proposal_id, rn_path in reading_notes_paths:
            if self.dry_run:
                self.stats["reading_notes_migrated"] += 1
                continue

            try:
                self._ensure_kb()
                text = rn_path.read_text(encoding="utf-8")
                entries = self._parse_reading_notes_table(text)

                for entry in entries:
                    arxiv_id = entry.get("arxiv_id", "")
                    if not arxiv_id:
                        # 尝试从标题或来源提取
                        title = entry.get("title", "")
                        source = entry.get("source", "")
                        m = re.search(r"(\d{4}\.\d{4,5})", f"{title} {source}")
                        if m:
                            arxiv_id = m.group(1)
                    if not arxiv_id:
                        continue

                    wiki_path = WIKI_PAPERS_DIR / f"{arxiv_id}.md"
                    note_content = (
                        f"### {proposal_id}\n"
                        f"- 核心结论：{entry.get('conclusion', '')}\n"
                        f"- 与课题关联：{entry.get('relevance', '')}\n"
                        f"- 已引用位置：{entry.get('citation_location', '')}\n"
                        f"- 阅读日期：{entry.get('date', '')}\n"
                    )

                    if wiki_path.exists():
                        existing = self._kw_get(f"wiki/papers/{arxiv_id}.md")
                        if existing:
                            old_content = existing.get("content", "")
                            if f"### {proposal_id}" not in old_content:
                                new_content = old_content + f"\n\n## 阅读笔记\n\n{note_content}"
                                meta = existing.get("meta", {})
                                used_by = meta.get("used_by_proposals", [])
                                if isinstance(used_by, str):
                                    used_by = [used_by]
                                if proposal_id not in used_by:
                                    used_by.append(proposal_id)
                                meta["used_by_proposals"] = used_by
                                meta["read_status"] = "skimmed"
                                meta["updated"] = _now()
                                page = self._kw_build(
                                    title=meta.get("title", arxiv_id),
                                    wiki_type="papers",
                                    content=new_content,
                                    meta=meta,
                                )
                                self._kw_save(f"wiki/papers/{arxiv_id}.md", page)
                    else:
                        meta = {
                            "title": f"Paper: {arxiv_id}",
                            "type": "papers",
                            "arxiv_id": arxiv_id,
                            "tags": ["literature"],
                            "project": ["NSFC-强场超快"],
                            "read_status": "skimmed",
                            "used_by_proposals": [proposal_id],
                            "created": _now(),
                            "updated": _now(),
                            "growth_stage": "seedling",
                            "confidence": 0.5,
                        }
                        page = self._kw_build(
                            title=f"Paper: {arxiv_id}",
                            wiki_type="papers",
                            content=f"## 阅读笔记\n\n{note_content}",
                            meta=meta,
                        )
                        self._kw_save(f"wiki/papers/{arxiv_id}.md", page)

                    self.stats["reading_note_entries"] += 1

                # 标记原文件已迁移
                migrated_marker = "\n---\n> migrated: true\n"
                if migrated_marker not in text:
                    rn_path.write_text(text + migrated_marker, encoding="utf-8")

                self.stats["reading_notes_migrated"] += 1
            except Exception as e:
                self.stats["errors"].append(f"迁移阅读笔记 {proposal_id}: {e}")
                _log_warn(f"迁移失败 {proposal_id}: {e}")

        _log_ok(f"迁移 {self.stats['reading_notes_migrated']} 个 proposal，{self.stats['reading_note_entries']} 条笔记")

    # ────────── 步骤 6: 迁移讨论记录到 qa/ 层 ──────────

    def migrate_discussions(self) -> None:
        """迁移讨论记录到 qa/ 层。"""
        discussions_dir = WIKI_PROJECTS_DIR / "deepxiv-论文库" / "discussions"
        if not discussions_dir.exists():
            _log_info("讨论记录目录不存在，跳过")
            return

        discussion_files = sorted(discussions_dir.glob("*.md"))
        if not discussion_files:
            _log_info("无讨论记录文件，跳过")
            return

        _log_info(f"迁移讨论记录（共 {len(discussion_files)} 个文件）...")

        qa_paper_dir = QA_DIR / "paper-discussions"
        qa_proposal_dir = QA_DIR / "proposal-discussions"

        for f in discussion_files:
            if self.dry_run:
                self.stats["discussions_migrated"] += 1
                continue

            try:
                content = f.read_text(encoding="utf-8")
                # 检测是论文讨论还是 proposal 讨论
                is_paper_discussion = bool(re.search(r"\d{4}\.\d{4,5}", content))

                if is_paper_discussion:
                    target = qa_paper_dir / f.name
                    qa_type = "paper-discussion"
                else:
                    target = qa_proposal_dir / f.name
                    qa_type = "proposal-discussion"

                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                self.stats["discussions_migrated"] += 1

                # 更新 graph.json
                try:
                    self._ensure_kb()
                    from kb_graph import update_graph_node
                    update_graph_node(str(target), {"type": qa_type, "title": f.name.replace(".md", "")})
                except Exception:
                    pass
            except Exception as e:
                self.stats["errors"].append(f"迁移讨论 {f.name}: {e}")
                _log_warn(f"迁移失败 {f.name}: {e}")

        _log_ok(f"迁移 {self.stats['discussions_migrated']} 个讨论记录")

    # ────────── 步骤 7: 重建索引和图谱 ──────────

    def rebuild_index_and_graph(self) -> None:
        """重建索引和图谱。"""
        if self.dry_run:
            _log_info("[dry-run] 将重建 index.json 和 graph.json")
            return

        _log_info("重建索引和图谱...")
        try:
            from kb_index import build_index
            build_index()
            _log_ok("index.json 重建完成")
        except Exception as e:
            self.stats["errors"].append(f"重建索引: {e}")
            _log_warn(f"重建索引失败: {e}")

        # 重建 graph.json
        try:
            from kb_graph import _load_graph, _save_graph
            graph = _load_graph()
            _save_graph(graph)
            _log_ok("graph.json 重建完成")
        except Exception as e:
            self.stats["errors"].append(f"重建图谱: {e}")
            _log_warn(f"重建图谱失败: {e}")

    # ────────── 步骤 8: 重建缓存视图 ──────────

    def rebuild_caches(self) -> None:
        """重建 paper-pool.json 和 item-status.json 缓存视图。"""
        if self.dry_run:
            _log_info("[dry-run] 将重建 paper-pool.json 和 item-status.json 缓存")
            return

        _log_info("重建缓存视图...")

        # 从 KB frontmatter 重建 paper-pool.json
        new_pool: Dict[str, Any] = {}
        if RAW_PAPERS_DIR.exists():
            for f in RAW_PAPERS_DIR.glob("*.md"):
                try:
                    text = f.read_text(encoding="utf-8")
                    fm, _ = _parse_frontmatter(text)
                    arxiv_id = fm.get("arxiv_id", "") or _extract_arxiv_from_filename(f.name)
                    if arxiv_id:
                        new_pool[arxiv_id] = {
                            "status": fm.get("status", "unseen"),
                            "unified_status": fm.get("unified_status", "pool"),
                            "title": fm.get("title", ""),
                            "score_deepxiv": fm.get("score_deepxiv", 0),
                            "has_pdf": fm.get("has_pdf", False),
                            "read_status": fm.get("read_status", "unread"),
                            "used_by_proposals": fm.get("used_by_proposals", []),
                            "source": fm.get("source", ""),
                            "imported_at": fm.get("imported_at", _now()),
                            "hermes_synced_at": fm.get("hermes_synced_at", ""),
                        }
                except Exception:
                    pass

        save_json(MEMORY_DIR / "paper-pool.json", new_pool)
        _log_ok(f"paper-pool.json 重建完成（{len(new_pool)} 篇论文）")

        # 重建 item-status.json（hermes 端兼容，仅尝试写入本域）
        try:
            status_data = {"version": "1.0", "updated_at": _now(), "items": {}}
            for arxiv_id, entry in new_pool.items():
                status_data["items"][arxiv_id] = {
                    "arxiv_id": arxiv_id,
                    "title": entry.get("title", ""),
                    "status": entry.get("unified_status", "pool"),
                    "direction": "",
                    "score": entry.get("score_deepxiv", 0),
                    "first_seen": entry.get("imported_at", _now()),
                    "last_updated": _now(),
                    "updated_by": "copilot",
                    "history": [
                        {"status": entry.get("unified_status", "pool"), "by": "copilot", "at": _now()}
                    ],
                }

            # 优先写入本域（MEMORY_DIR），可被 hermes 同步读取
            local_status_path = MEMORY_DIR / "item-status.json"
            local_status_path.parent.mkdir(parents=True, exist_ok=True)
            local_status_path.write_text(
                json.dumps(status_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            _log_ok(f"item-status.json 重建完成（本地: {len(status_data['items'])} 篇论文）")

            # 尝试写入 hermes 工作区（可能权限不足，非致命）
            try:
                HERMES_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
                HERMES_STATUS_PATH.write_text(
                    json.dumps(status_data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                _log_ok(f"item-status.json 同步到 hermes 工作区")
            except (PermissionError, OSError):
                _log_info("hermes 工作区不可写，跳过 hermes 端同步")
        except Exception as e:
            self.stats["errors"].append(f"重建 item-status.json: {e}")
            _log_warn(f"重建 item-status.json 失败: {e}")

    # ────────── 辅助方法 ──────────

    def _find_raw_paper(self, arxiv_id: str) -> Optional[Path]:
        """在 raw/papers/ 中查找对应 arxiv_id 的文件。"""
        if not RAW_PAPERS_DIR.exists():
            return None
        # arxiv_id 可能包含 /（如 physics/9906053），替换为 - 以匹配文件名
        safe_id = arxiv_id.replace("/", "-")
        # 格式: YYYY-arxiv_id-slug.md
        for f in RAW_PAPERS_DIR.glob(f"*-{safe_id}-*.md"):
            return f
        for f in RAW_PAPERS_DIR.glob(f"*-{safe_id}.md"):
            return f
        for f in RAW_PAPERS_DIR.glob(f"{safe_id}.md"):
            return f
        return None

    def _import_paper_to_kb(self, arxiv_id: str, entry: Dict[str, Any]) -> None:
        """补充导入已入池但未入库的论文到 KB。"""
        try:
            RAW_PAPERS_DIR.mkdir(parents=True, exist_ok=True)
            title = entry.get("title", f"Paper {arxiv_id}")
            # arxiv_id 可能包含 /（如 physics/9906053），替换为 -
            safe_id = arxiv_id.replace("/", "-")
            slug = f"2024-{safe_id}-{_safe_filename(title)}"
            raw_path = RAW_PAPERS_DIR / f"{slug}.md"

            fm = {
                "title": title,
                "arxiv_id": arxiv_id,
                "authors": entry.get("authors", ""),
                "year": entry.get("year", "2024"),
                "tags": ["deepxiv-论文库"],
                "project": ["NSFC-强场超快"],
                "direction": entry.get("direction", ""),
                "source": "hermes-简报",
                "imported_at": _now(),
                "score_deepxiv": entry.get("score_deepxiv", 0),
                "status": entry.get("status", "unseen"),
                "unified_status": entry.get("unified_status", "pool"),
                "read_status": "unread",
                "used_by_proposals": [],
                "has_pdf": False,
                "abstract": "",
                "status_history": [
                    {"status": "pool", "at": _now(), "by": "migration"}
                ],
            }
            content = _build_frontmatter(fm)
            content += f"\n\n# {title}\n\n（通过迁移脚本补充导入）\n"
            raw_path.write_text(content, encoding="utf-8")
            _log_ok(f"补充导入: {arxiv_id}")
        except Exception as e:
            self.stats["errors"].append(f"补充导入 {arxiv_id}: {e}")

    def _extract_arxiv_from_content(self, f: Path) -> str:
        """从 frontmatter 或内容中提取 arxiv_id。"""
        try:
            text = f.read_text(encoding="utf-8")
            fm, _ = _parse_frontmatter(text)
            aid = fm.get("arxiv_id", "")
            if aid:
                return aid.split("v")[0]
            # 从文件名提取
            aid = _extract_arxiv_from_filename(f.name)
            if aid:
                return aid
            # 从内容中提取
            m = re.search(r"(\d{4}\.\d{4,5})", text)
            if m:
                return m.group(1)
        except Exception:
            pass
        return ""

    def _parse_reading_notes_table(self, text: str) -> List[Dict[str, str]]:
        """解析 reading-notes.md 的 Markdown 表格。"""
        entries: List[Dict[str, str]] = []
        in_table = False
        headers: List[str] = []

        for line in text.split("\n"):
            line = line.strip()
            if not line.startswith("|"):
                in_table = False
                continue
            # 跳过分隔行（如 |---|---|---|）
            if re.match(r"^\|[\s\-:]+\|", line):
                in_table = True
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not in_table:
                # 表头
                headers = cells
                in_table = True
            else:
                # 数据行
                entry: Dict[str, str] = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        key_map = {
                            "阅读日期": "date",
                            "文献标题": "title",
                            "来源": "source",
                            "核心结论": "conclusion",
                            "与课题关联": "relevance",
                            "已引用位置": "citation_location",
                        }
                        entry[key_map.get(headers[i], headers[i])] = cell
                if entry:
                    entries.append(entry)

        return entries

    # ────────── 验证 ──────────

    def verify(self) -> bool:
        """验证迁移结果。"""
        _log_info("\n验证迁移结果...")
        all_ok = True

        # 1. 检查 raw/papers/ 文件数
        if RAW_PAPERS_DIR.exists():
            count = len(list(RAW_PAPERS_DIR.glob("*.md")))
            _log_ok(f"raw/papers/: {count} 个文件")
        else:
            _log_warn("raw/papers/ 目录不存在")

        # 2. 检查 wiki/papers/ 文件数
        if WIKI_PAPERS_DIR.exists():
            count = len(list(WIKI_PAPERS_DIR.glob("*.md")))
            _log_ok(f"wiki/papers/: {count} 个文件")
        else:
            _log_warn("wiki/papers/ 目录不存在")

        # 3. 检查 qa/paper-discussions/ 文件数
        qa_paper_dir = QA_DIR / "paper-discussions"
        if qa_paper_dir.exists():
            count = len(list(qa_paper_dir.glob("*.md")))
            _log_ok(f"qa/paper-discussions/: {count} 个文件")
        else:
            _log_warn("qa/paper-discussions/ 目录不存在")

        # 4. 检查 paper-pool 缓存
        pool_path = MEMORY_DIR / "paper-pool.json"
        if pool_path.exists():
            pool = load_json(pool_path, {})
            _log_ok(f"paper-pool.json: {len(pool)} 篇论文")
        else:
            _log_warn("paper-pool.json 不存在")

        # 5. 检查 item-status 缓存
        if HERMES_STATUS_PATH.exists():
            try:
                status_data = json.loads(HERMES_STATUS_PATH.read_text(encoding="utf-8"))
                _log_ok(f"item-status.json: {len(status_data.get('items', {}))} 篇论文")
            except Exception:
                _log_warn("item-status.json 解析失败")

        # 6. 检查 graph.json
        graph_path = KNOWLEDGE_DIR / "graph.json"
        if graph_path.exists():
            _log_ok("graph.json 存在")
        else:
            _log_warn("graph.json 不存在")

        # 7. 检查 index.json
        index_path = KNOWLEDGE_DIR / "index.json"
        if index_path.exists():
            _log_ok("index.json 存在")
        else:
            _log_warn("index.json 不存在")

        # 8. 检查前端字段完整性
        if RAW_PAPERS_DIR.exists():
            missing_fields = 0
            for f in list(RAW_PAPERS_DIR.glob("*.md"))[:20]:  # 抽样检查
                try:
                    text = f.read_text(encoding="utf-8")
                    fm, _ = _parse_frontmatter(text)
                    for field in ["status", "unified_status", "read_status", "used_by_proposals"]:
                        if field not in fm:
                            missing_fields += 1
                            break
                except Exception:
                    pass
            if missing_fields:
                _log_warn(f"{missing_fields} 个文件缺少必要状态字段")
                all_ok = False
            else:
                _log_ok("raw/papers/ frontmatter 字段完整性检查通过")

        if self.stats["errors"]:
            _log_warn(f"迁移过程中有 {len(self.stats['errors'])} 个错误")
            for err in self.stats["errors"][:5]:
                _log_warn(f"  - {err}")
            all_ok = False

        return all_ok


# ─────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="文献统一架构数据迁移脚本")
    parser.add_argument("--dry-run", action="store_true", help="预览迁移，不实际修改文件")
    parser.add_argument("--backup", action="store_true", help="迁移前自动备份")
    args = parser.parse_args()

    m = Migrator(dry_run=args.dry_run)

    print(f"\n{'='*60}")
    print(f"文献统一架构数据迁移")
    print(f"模式: {'预览 (dry-run)' if args.dry_run else '执行'}")
    print(f"{'='*60}\n")

    # 步骤 1: 备份
    print("步骤 1/8: 备份")
    if args.backup and not args.dry_run:
        m.backup()
    else:
        print("  (跳过，使用 --backup 启用)")
    print()

    # 步骤 2: 合并 paper-pool
    print("步骤 2/8: 合并 paper-pool 状态到 KB frontmatter")
    m.merge_paper_pool_to_kb()
    print()

    # 步骤 3: 合并 item-status
    print("步骤 3/8: 合并 item-status 历史到 KB frontmatter")
    m.merge_item_status_to_kb()
    print()

    # 步骤 4: 迁移深度解析
    print("步骤 4/8: 迁移深度解析到 wiki/papers/")
    m.migrate_deep_analysis()
    print()

    # 步骤 5: 迁移阅读笔记
    print("步骤 5/8: 迁移 per-proposal 阅读笔记到 wiki/papers/")
    m.migrate_reading_notes()
    print()

    # 步骤 6: 迁移讨论记录
    print("步骤 6/8: 迁移讨论记录到 qa/ 层")
    m.migrate_discussions()
    print()

    if not args.dry_run:
        # 步骤 7: 重建索引和图谱
        print("步骤 7/8: 重建索引和图谱")
        m.rebuild_index_and_graph()
        print()

        # 步骤 8: 重建缓存视图
        print("步骤 8/8: 重建缓存视图")
        m.rebuild_caches()
        print()

    # 验证
    print("验证迁移结果...")
    ok = m.verify()
    print()

    print(f"{'='*60}")
    if ok:
        print("迁移验证通过")
    else:
        print("迁移验证有警告")
    print(f"统计: paper-pool合并={m.stats['paper_pool_merged']}, "
          f"item-status合并={m.stats['item_status_merged']}, "
          f"深度解析={m.stats['deep_analyses_migrated']}, "
          f"阅读笔记={m.stats['reading_notes_migrated']}({m.stats['reading_note_entries']}条), "
          f"讨论={m.stats['discussions_migrated']}, "
          f"补充导入={m.stats['papers_imported']}")
    if m.stats['errors']:
        print(f"错误数: {len(m.stats['errors'])}")
    print(f"{'='*60}\n")


def _self_check() -> bool:
    """运行自检。"""
    print("=== migrate_literature_unified 自检 ===")

    m = Migrator(dry_run=True)

    # 1. 测试 _extract_arxiv_from_filename
    assert _extract_arxiv_from_filename("2024-2403.15337-test.md") == "2403.15337"
    assert _extract_arxiv_from_filename("2403.15337.md") == "2403.15337"
    assert _extract_arxiv_from_filename("2301.12345.md") == "2301.12345"
    print("✓ _extract_arxiv_from_filename")

    # 2. 测试 _parse_frontmatter
    text = "---\ntitle: Test\narxiv_id: 2403.15337\nstatus: unseen\n---\n\nBody"
    fm, body = _parse_frontmatter(text)
    assert fm.get("title") == "Test"
    assert fm.get("arxiv_id") == "2403.15337"
    assert fm.get("status") == "unseen"
    assert body.strip() == "Body"
    print("✓ _parse_frontmatter")

    # 3. 测试 _build_frontmatter
    fm2 = {"title": "Test", "arxiv_id": "2403.15337", "status": "unseen", "used_by_proposals": ["p1", "p2"]}
    result = _build_frontmatter(fm2)
    assert "title:" in result
    assert "arxiv_id:" in result
    assert "used_by_proposals:" in result
    print("✓ _build_frontmatter")

    # 4. 测试 _parse_reading_notes_table
    table = """| 阅读日期 | 文献标题 | 来源 | 核心结论 | 与课题关联 | 已引用位置 |
|---|---|---|---|---|---|---|
| 2024-01-01 | Test Paper | arXiv | Good | High | Section 3 |"""
    entries = m._parse_reading_notes_table(table)
    assert len(entries) == 1
    assert entries[0]["title"] == "Test Paper"
    assert entries[0]["date"] == "2024-01-01"
    print("✓ _parse_reading_notes_table")

    # 5. 测试 _safe_filename
    fn = _safe_filename("HHG in Solids: A Review")
    assert "hhg-in-solids" in fn
    print("✓ _safe_filename")

    print("\n✓ migrate_literature_unified 自检全部通过")
    return True


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        _self_check()
    else:
        main()