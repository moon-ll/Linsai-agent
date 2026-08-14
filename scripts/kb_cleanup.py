#!/usr/bin/env python3
"""知识库清理脚本 (v6.8.14 WP0)

执行 WP0 数据清理：
  0.1 删除 raw/papers 空壳（正文 <1500 字符 + 迁移占位/空摘要）
  0.2 修复 wiki/papers 双FM破损文件（从 deep_analysis JSON 重建，无源则删除）
  0.3 回填 wiki/papers 元数据（arxiv_id→title/链接/方向）
  0.4 统一 frontmatter（type 字段修正 + 重复 tag 清理）
  0.5 重建 index.json
  0.6 重建 graph.json
  0.7 归档 test 课题

用法：
  python3 scripts/kb_cleanup.py --dry-run    # 只出报告，不执行
  python3 scripts/kb_cleanup.py              # 执行清理
  python3 scripts/kb_cleanup.py --step 1     # 只执行某一步
"""

import argparse
import json
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KB_ROOT = PROJECT_ROOT / "knowledge"
RAW_PAPERS = KB_ROOT / "raw" / "papers"
WIKI_PAPERS = KB_ROOT / "wiki" / "papers"
HERMES_BRIEFINGS = Path.home() / "Desktop" / "hermes_workspace" / "knowledge_base" / "AI_wiki" / "briefings"
INDEX_PATH = KB_ROOT / "index.json"
GRAPH_PATH = KB_ROOT / "graph.json"


def _parse_frontmatter(text: str) -> tuple:
    """解析 frontmatter，返回 (fm_dict, body)。"""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm_raw = parts[1].strip()
    body = parts[2].lstrip("\n")
    fm = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key:
                fm[key] = val
    return fm, body


def _build_frontmatter(fm: dict, extra: dict = None) -> str:
    """构建 YAML frontmatter 字符串。"""
    merged = {**fm, **(extra or {})}
    # 确保 type 正确
    if "type" in merged:
        t = merged["type"]
        if t in ("concepts",):
            merged["type"] = "paper"
        elif t == "papers":
            merged["type"] = "paper"
    lines = ["---"]
    for k, v in merged.items():
        if isinstance(v, str):
            lines.append(f'{k}: "{v}"')
        elif isinstance(v, list):
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def step1_delete_raw_stubs(dry_run: bool) -> dict:
    """删除 raw/papers 空壳。"""
    deleted = []
    for f in sorted(RAW_PAPERS.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)
        body_stripped = body.strip()
        has_migrate = "迁移脚本" in text
        has_empty_abs = fm.get("abstract", "x") in ('', '""', "''")
        is_short = len(body_stripped) < 1500
        if is_short and (has_migrate or has_empty_abs):
            deleted.append(f.name)
            if not dry_run:
                f.unlink()
    return {"step": "1_delete_raw_stubs", "deleted": deleted, "count": len(deleted)}


def step2_fix_wiki_broken(dry_run: bool) -> dict:
    """修复 wiki/papers 双FM破损文件。"""
    fixed = []
    deleted = []
    deep_analysis_dir = HERMES_BRIEFINGS

    for f in sorted(WIKI_PAPERS.glob("*.md")):
        if f.name.startswith("."):
            continue
        text = f.read_text(encoding="utf-8")
        fm_count = text.count("\n---\n")
        is_broken = fm_count >= 3 or len(text) < 500
        if not is_broken:
            continue

        arxiv_id = f.stem
        json_path = deep_analysis_dir / f"deep_analysis_{arxiv_id}.json"

        if json_path.exists():
            # 从 deep_analysis JSON 重建
            try:
                da = json.loads(json_path.read_text(encoding="utf-8"))
                new_content = _build_note_from_analysis(arxiv_id, da)
                if not dry_run:
                    f.write_text(new_content, encoding="utf-8")
                fixed.append(arxiv_id)
            except Exception as e:
                deleted.append(f"{arxiv_id} (重建失败: {e})")
                if not dry_run:
                    f.unlink()
        else:
            # 没有 deep_analysis，尝试从 raw/papers 重建
            raw_match = list(RAW_PAPERS.glob(f"*-{arxiv_id}-*.md"))
            if raw_match:
                raw_text = raw_match[0].read_text(encoding="utf-8")
                raw_fm, raw_body = _parse_frontmatter(raw_text)
                if len(raw_body.strip()) > 500:
                    # raw 有实质内容，构建最小 wiki 笔记
                    new_content = _build_minimal_note(arxiv_id, raw_fm, raw_body)
                    if not dry_run:
                        f.write_text(new_content, encoding="utf-8")
                    fixed.append(f"{arxiv_id} (from raw)")
                else:
                    deleted.append(f"{arxiv_id} (raw 也无内容)")
                    if not dry_run:
                        f.unlink()
            else:
                deleted.append(f"{arxiv_id} (无源)")
                if not dry_run:
                    f.unlink()

    return {"step": "2_fix_wiki_broken", "fixed": fixed, "deleted": deleted,
            "fixed_count": len(fixed), "deleted_count": len(deleted)}


def _build_note_from_analysis(arxiv_id: str, da: dict) -> str:
    """从 deep_analysis JSON 构建 5 维笔记。"""
    title = da.get("title", arxiv_id)
    direction = da.get("direction", "")
    authors = da.get("authors", [])
    if isinstance(authors, list):
        authors_str = ", ".join(authors[:5])
    else:
        authors_str = str(authors)
    date = da.get("date", "")

    fm = {
        "title": title,
        "type": "paper",
        "arxiv_id": arxiv_id,
        "authors": authors_str,
        "year": date[:4] if date else "",
        "direction": direction,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tags": [],
        "related": [],
        "growth_stage": "growing",
        "confidence": 0.7,
        "note_format": "5-dimension",
        "note_source": "deep_analysis_json",
        "read_status": "deep-read",
    }

    why_notable = da.get("why_notable", "（无数据）")
    linsai_conn = da.get("linsai_connection", "（无数据）")
    new_methods = da.get("new_methods", [])
    core_findings = da.get("core_findings", [])
    what_next = da.get("what_next", [])

    def _fmt_list(items):
        if isinstance(items, list):
            return "\n".join(f"- {item}" for item in items)
        return str(items)

    body = f"""# {title}

**arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id}) | **方向**: {direction}

---

## 研究问题（Research Question）

{why_notable}

## 研究背景（Background）

{linsai_conn}

## 研究方法（Methods）

{_fmt_list(new_methods)}

## 主要发现与核心结论（Main Results）

{_fmt_list(core_findings)}

## 潜在研究方向（Future Directions）

{_fmt_list(what_next)}
"""

    return _build_frontmatter(fm) + "\n" + body


def _build_minimal_note(arxiv_id: str, raw_fm: dict, raw_body: str) -> str:
    """从 raw/papers 构建最小 wiki 笔记。"""
    title = raw_fm.get("title", arxiv_id)
    fm = {
        "title": title,
        "type": "paper",
        "arxiv_id": arxiv_id,
        "direction": raw_fm.get("direction", ""),
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tags": [],
        "related": [],
        "growth_stage": "seedling",
        "confidence": 0.5,
        "note_format": "5-dimension",
        "note_source": "raw_fallback",
        "read_status": "skimmed",
    }
    body = f"""# {title}

**arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id}) | **方向**: {raw_fm.get('direction', '未分类')}

---

{raw_body[:4000]}
"""
    return _build_frontmatter(fm) + "\n" + body


def step3_backfill_metadata(dry_run: bool) -> dict:
    """回填 wiki/papers 元数据。"""
    backfilled = []

    # 构建 raw/papers 的 arxiv_id → fm 映射
    raw_map = {}
    for f in RAW_PAPERS.glob("*.md"):
        text = f.read_text(encoding="utf-8")
        fm, _ = _parse_frontmatter(text)
        # 从文件名提取 arxiv_id
        parts = f.stem.split("-")
        for p in parts:
            if re.match(r"\d{4}\.\d{4,5}", p):
                raw_map[p] = fm
                break

    for f in sorted(WIKI_PAPERS.glob("*.md")):
        if f.name.startswith("."):
            continue
        arxiv_id = f.stem
        text = f.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)

        changed = False
        raw_fm = raw_map.get(arxiv_id, {})

        # 回填 title
        if (fm.get("title") in (arxiv_id, "", None)) and raw_fm.get("title"):
            fm["title"] = raw_fm["title"]
            # 同时更新正文标题
            body = re.sub(r"^# .+$", f"# {raw_fm['title']}", body, count=1, flags=re.MULTILINE)
            changed = True

        # 回填 direction
        if not fm.get("direction") and raw_fm.get("direction"):
            fm["direction"] = raw_fm["direction"]
            changed = True

        # 修正 arxiv 链接
        if f"[{arxiv_id}](https://arxiv.org/abs/{arxiv_id})" not in body:
            if "[](https://arxiv.org/abs/)" in body:
                body = body.replace(
                    "[](https://arxiv.org/abs/)",
                    f"[{arxiv_id}](https://arxiv.org/abs/{arxiv_id})"
                )
                changed = True

        if changed:
            backfilled.append(arxiv_id)
            if not dry_run:
                f.write_text(_build_frontmatter(fm) + "\n" + body, encoding="utf-8")

    return {"step": "3_backfill_metadata", "backfilled": backfilled, "count": len(backfilled)}


def step4_unify_frontmatter(dry_run: bool) -> dict:
    """统一 frontmatter（type 字段 + 重复 tag）。"""
    fixed_type = []
    fixed_tags = []

    for subdir in ["papers", "concepts", "methods", "people", "reviews"]:
        d = KB_ROOT / "wiki" / subdir
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name.startswith(".") or f.name.endswith(".bak"):
                continue
            text = f.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            parts = text.split("---", 2)
            if len(parts) < 3:
                continue
            fm_raw = parts[1]
            body = parts[2]

            changed = False
            # 修正 type
            if re.search(r'^type:\s*"?(concepts)"?', fm_raw, re.MULTILINE):
                fm_raw = re.sub(r'^type:\s*"?concepts"?', 'type: "paper"', fm_raw, count=1, flags=re.MULTILINE)
                changed = True
                fixed_type.append(f.name)
            elif re.search(r'^type:\s*"?(papers)"?', fm_raw, re.MULTILINE):
                fm_raw = re.sub(r'^type:\s*"?papers"?', 'type: "paper"', fm_raw, count=1, flags=re.MULTILINE)
                changed = True
                fixed_type.append(f.name)

            # 清理重复 status tag
            tags_section = re.findall(r'^tags:\s*\[([^\]]*)\]', fm_raw, re.MULTILINE)
            if tags_section:
                tags_raw = tags_section[0]
                tags = [t.strip().strip('"').strip("'") for t in tags_raw.split(",")]
                # 去重
                seen = set()
                deduped = []
                for t in tags:
                    tl = t.lower()
                    if tl not in seen:
                        seen.add(tl)
                        deduped.append(t)
                if len(deduped) != len(tags):
                    new_tags = ", ".join(f'"{t}"' for t in deduped)
                    fm_raw = re.sub(
                        r'^tags:\s*\[[^\]]*\]',
                        f'tags: [{new_tags}]',
                        fm_raw,
                        count=1,
                        flags=re.MULTILINE,
                    )
                    changed = True
                    fixed_tags.append(f.name)

            if changed:
                if not dry_run:
                    f.write_text("---" + fm_raw + "---" + body, encoding="utf-8")

    return {"step": "4_unify_frontmatter", "fixed_type": fixed_type, "fixed_tags": fixed_tags,
            "type_count": len(fixed_type), "tags_count": len(fixed_tags)}


def step5_rebuild_index(dry_run: bool) -> dict:
    """重建 index.json。

    v6.8.51 修复：旧实现用自造的简化格式（total_documents + path 列表）直接覆写
    knowledge/index.json，会摧毁 kb_index 的倒排索引（documents 结构完全不同，
    检索方按 chunk_list/df 布局读取全部失效）。现委托 kb_index.build_index()
    走统一格式 v2 构建器。
    """
    if dry_run:
        return {"step": "5_rebuild_index", "would_rebuild": True, "skipped": "dry-run"}

    import kb_index

    index = kb_index.build_index(force=True)

    return {"step": "5_rebuild_index", "rebuilt": True, "doc_count": len(index.get("documents", {}))}


def step6_rebuild_graph(dry_run: bool) -> dict:
    """重建 graph.json。"""
    nodes = {}
    edges = []

    # 收集所有 wiki 页面作为节点
    for subdir in ["concepts", "methods", "people", "papers", "reviews"]:
        d = KB_ROOT / "wiki" / subdir
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name.startswith(".") or f.suffix == ".bak":
                continue
            text = f.read_text(encoding="utf-8")
            fm, _ = _parse_frontmatter(text)
            title = fm.get("title", f.stem)
            node_type = fm.get("type", subdir.rstrip("s"))
            growth = fm.get("growth_stage", "seedling")
            rel = f"wiki/{subdir}/{f.name}"

            # 节点 key 用 arxiv_id（论文）或 title（其他）
            arxiv_id = fm.get("arxiv_id", "")
            node_key = arxiv_id if arxiv_id else title

            if node_key and node_key not in nodes:
                nodes[node_key] = {
                    "type": node_type,
                    "path": rel,
                    "growth_stage": growth,
                }

            # 从 related 字段建边
            related_raw = fm.get("related", "[]")
            if isinstance(related_raw, str):
                try:
                    related_list = json.loads(related_raw)
                except Exception:
                    related_list = []
            else:
                related_list = related_raw or []

            for target in related_list:
                if target and target != node_key:
                    edges.append({"source": node_key, "target": target})

    # 收集 projects 节点
    proj_dir = KB_ROOT / "wiki" / "projects"
    if proj_dir.exists():
        for f in proj_dir.rglob("*.md"):
            if f.name.startswith(".") or "/_archive/" in str(f):
                continue
            text = f.read_text(encoding="utf-8")
            fm, _ = _parse_frontmatter(text)
            title = fm.get("title", f.stem)
            rel = str(f.relative_to(KB_ROOT))
            if title and title not in nodes:
                nodes[title] = {
                    "type": fm.get("type", "project"),
                    "path": rel,
                    "growth_stage": fm.get("growth_stage", "growing"),
                }

    # 收集 MOC 节点
    for moc_path in ["wiki/concepts/MOC-HHG.md", "wiki/projects/NSFC-强场超快/MOC.md", "wiki/projects/deepxiv-论文库/MOC.md"]:
        f = KB_ROOT / moc_path
        if f.exists():
            text = f.read_text(encoding="utf-8")
            fm, _ = _parse_frontmatter(text)
            title = fm.get("title", f.stem)
            if title and title not in nodes:
                nodes[title] = {"type": "MOC", "path": moc_path, "growth_stage": "mature"}

    graph = {
        "rebuilt_at": datetime.now(timezone.utc).isoformat(),
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }

    if not dry_run:
        GRAPH_PATH.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"step": "6_rebuild_graph", "nodes": len(nodes), "edges": len(edges)}


def step7_archive_test(dry_run: bool) -> dict:
    """归档 test 课题。"""
    archived = []
    # 搜索所有包含 test 的 wiki/projects 文件
    for f in (KB_ROOT / "wiki" / "projects").rglob("*test*"):
        if f.exists():
            archived.append(str(f.relative_to(KB_ROOT)))
            if not dry_run:
                archive_dir = KB_ROOT / "wiki" / "projects" / "_archive"
                archive_dir.mkdir(exist_ok=True)
                shutil.move(str(f), str(archive_dir / f.name))
    return {"step": "7_archive_test", "archived": archived, "count": len(archived)}


def main():
    parser = argparse.ArgumentParser(description="知识库清理脚本 v6.8.14")
    parser.add_argument("--dry-run", action="store_true", help="只出报告，不执行")
    parser.add_argument("--step", type=int, help="只执行某一步 (1-7)")
    args = parser.parse_args()

    steps = {
        1: ("删除 raw/papers 空壳", step1_delete_raw_stubs),
        2: ("修复 wiki/papers 破损文件", step2_fix_wiki_broken),
        3: ("回填 wiki/papers 元数据", step3_backfill_metadata),
        4: ("统一 frontmatter", step4_unify_frontmatter),
        5: ("重建 index.json", step5_rebuild_index),
        6: ("重建 graph.json", step6_rebuild_graph),
        7: ("归档 test 课题", step7_archive_test),
    }

    to_run = [args.step] if args.step else list(steps.keys())

    print(f"{'[DRY-RUN] ' if args.dry_run else ''}知识库清理 v6.8.14")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for n in to_run:
        title, func = steps[n]
        print(f"\n--- Step {n}: {title} ---")
        result = func(args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("清理完成" if not args.dry_run else "DRY-RUN 完成（未执行任何修改）")


if __name__ == "__main__":
    main()
