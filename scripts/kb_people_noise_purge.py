#!/usr/bin/env python3
"""人名页噪音治理（v7.3.85）

2026-11-15 巡检发现的知识库质量事件治理：
  1. 11-14/15 周末输出端 knowledge_output / weekend_pipeline.output_jobs
     从归档课题/简报萃取 people 实体时无人名噪音过滤，产出 83 张人名页
     （裸姓氏「Ding/Han/Liu」、组指代「Ghimire 等人」、空壳「未在文中提及」），
     经查 83/83 全部为噪音。
  2. kb_linker 标题提及匹配把 people 页标题也当概念词表，且纯拉丁标题
     走大小写不敏感子串匹配（"Han" 命中 "Hamilton"），全库泵出约 2000 条
     假 related 边（Ding×705 / Liu×238 / Lee×110 / Yang×104）。
  3. 顺带归并 briefing stub 重复家族 固体HHG / 固体 HHG（标题含空格变体）。

治理步骤：
  1. 全 wiki 剥离指向 people 页的 related 条目与正文 [[人名]] 自由链接
     （防 _inject_wikilinks 把正文链接合并回 related 的回填通道）
  2. 隔离 knowledge/wiki/people → knowledge/trash/people-noise-<date>/
     （附 manifest.json；不直接删除，属用户资产可恢复）
  3. 固体 HHG → 固体HHG 归并：变体转 merged_into stub、related/正文链接
     改写规范名、aliases.json 注册变体
  4. 重建索引与图谱（cmd_reindex + cmd_rebuild_graph 两遍式端点校验，
     悬空边自动丢弃）

生产端止血（同版本已修复，本脚本不涉及）：
  - kb_linker._load_all_titles 排除 type=people
  - kb_linker.extract_title_mentions 纯拉丁标题词边界匹配
  - knowledge_output._is_noise_person / output_jobs._is_noise_person
    人名噪音过滤（裸姓氏/组指代/空壳不建页）

用法：
  python3 scripts/kb_people_noise_purge.py            # 预览（不落盘）
  python3 scripts/kb_people_noise_purge.py --apply    # 执行治理
  python3 scripts/kb_people_noise_purge.py --apply --skip-rebuild
                                                      # 执行但跳过索引/图谱重建
  python3 scripts/kb_people_noise_purge.py --self-check

规范：
  - 仅使用 Python 3 标准库
  - 原子写入走 kb_wiki.save_wiki_page（defer_graph/defer_growth_log 批量化）
  - 幂等：重复执行无副作用（二次运行剥离数为 0、隔离目录已存在则跳过）
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

KB_ROOT = PROJECT_ROOT / "knowledge"
WIKI_DIR = KB_ROOT / "wiki"
PEOPLE_DIR = WIKI_DIR / "people"
TRASH_DIR = KB_ROOT / "trash"
ALIASES_PATH = KB_ROOT / "aliases.json"

# briefing stub 重复家族：变体标题（含空格）→ 规范标题
_SOLID_HHG_VARIANT = "固体 HHG"
_SOLID_HHG_CANONICAL = "固体HHG"
_SOLID_HHG_VARIANT_FILE = WIKI_DIR / "concepts" / "固体_HHG.md"
_SOLID_HHG_CANONICAL_FILE = WIKI_DIR / "concepts" / "固体HHG.md"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _collect_people_targets() -> Set[str]:
    """收集 people 页的标题与文件 stem，构成待剥离目标集。"""
    targets: Set[str] = set()
    if not PEOPLE_DIR.exists():
        return targets
    for f in PEOPLE_DIR.glob("*.md"):
        targets.add(f.stem)
        m = re.search(r'^title: "(.*)"\s*$', f.read_text(encoding="utf-8")[:800], re.M)
        if m and m.group(1).strip():
            targets.add(m.group(1).strip())
    return targets


def _link_pattern(name: str) -> "re.Pattern[str]":
    """[[name]] / [[name|别名]] 链接模式（保留别名文本改写为裸名）。"""
    return re.compile(r"\[\[" + re.escape(name) + r"(?:\|([^\]]*))?\]\]")


def _strip_page(path: Path, targets: Set[str], rename_map: Dict[str, str]) -> Dict[str, int]:
    """单页剥离：frontmatter related 过滤 + 正文自由链接改写。

    Returns:
        {"related_removed": int, "related_renamed": int, "body_links": int}
    """
    from kb_wiki import parse_frontmatter

    # kb_wiki 是 sys.modules 单例，save_wiki_page 依赖 _ensure_dirs 注入
    # （见 kb_merger.py 同款注释）——必须先加载 knowledge_base 门面
    import knowledge_base  # noqa: F401

    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if not fm:
        return {"related_removed": 0, "related_renamed": 0, "body_links": 0}

    related = fm.get("related", [])
    if isinstance(related, str):
        related = [related]
    new_related: List[str] = []
    removed = renamed = 0
    for r in related:
        if not isinstance(r, str) or not r.strip():
            continue
        rs = r.strip()
        if rs in targets:
            removed += 1
            continue
        mapped = rename_map.get(rs)
        if mapped:
            renamed += 1
            new_related.append(mapped)
        else:
            new_related.append(rs)
    if not removed and not renamed:
        # frontmatter 无变化，但正文可能仍有自由链接
        pass

    body_links = 0
    new_body = body
    for name in targets:
        pat = _link_pattern(name)
        if pat.search(new_body):
            body_links += len(pat.findall(new_body))
            new_body = pat.sub(lambda m: m.group(1) or name, new_body)
    for variant, canonical in rename_map.items():
        pat = _link_pattern(variant)
        if pat.search(new_body):
            body_links += len(pat.findall(new_body))
            new_body = pat.sub(f"[[{canonical}]]", new_body)

    if removed or renamed:
        fm["related"] = new_related
    if not removed and not renamed and not body_links:
        return {"related_removed": 0, "related_renamed": 0, "body_links": 0}

    from kb_wiki import save_wiki_page

    rel = str(path.relative_to(KB_ROOT))
    save_wiki_page(rel, new_body, fm, defer_graph=True, defer_growth_log=True)
    return {"related_removed": removed, "related_renamed": renamed, "body_links": body_links}


def strip_people_links(targets: Set[str], dry_run: bool) -> Dict[str, Any]:
    """步骤 1：全 wiki 剥离人名链接与 固体 HHG 变体规范化。"""
    rename_map = {_SOLID_HHG_VARIANT: _SOLID_HHG_CANONICAL}
    changed = 0
    total_removed = total_renamed = total_body = 0
    pages: List[Path] = []
    for sub in sorted(WIKI_DIR.glob("*")):
        if not sub.is_dir() or sub.name == "people":
            continue
        pages.extend(sub.rglob("*.md"))

    preview_limit: List[str] = []
    for p in pages:
        if dry_run:
            # 预览只统计，不落盘
            text = p.read_text(encoding="utf-8")
            hit_related = 0
            m = re.search(r"^related: \[(.*)\]\s*$", text[:1200], re.M)
            if m:
                entries = re.findall(r'"([^"]+)"', m.group(1))
                hit_related = sum(1 for e in entries if e in targets)
            hit_body = sum(len(_link_pattern(t).findall(text)) for t in targets)
            hit_body += len(_link_pattern(_SOLID_HHG_VARIANT).findall(text))
            if hit_related or hit_body:
                changed += 1
                total_removed += hit_related
                total_body += hit_body
                if len(preview_limit) < 8:
                    preview_limit.append(f"{p.name} (related {hit_related} / 正文 {hit_body})")
            continue
        r = _strip_page(p, targets, rename_map)
        if r["related_removed"] or r["related_renamed"] or r["body_links"]:
            changed += 1
            total_removed += r["related_removed"]
            total_renamed += r["related_renamed"]
            total_body += r["body_links"]

    return {
        "pages_changed": changed,
        "related_removed": total_removed,
        "related_renamed": total_renamed,
        "body_links_rewritten": total_body,
        "preview": preview_limit,
    }


def quarantine_people(dry_run: bool) -> Dict[str, Any]:
    """步骤 2：隔离 people 目录到 trash（附 manifest，可恢复）。"""
    if not PEOPLE_DIR.exists():
        return {"skipped": "people 目录不存在（已隔离过）", "moved": 0}
    pages = sorted(PEOPLE_DIR.glob("*.md"))
    manifest = {
        "quarantined_at": _now_utc(),
        "reason": "v7.3.85 人名页噪音治理：83 张人名页 83/83 为噪音"
                  "（裸姓氏/组指代/空壳），且作为 kb_linker 词表泵出全库假边",
        "pages": [],
    }
    for f in pages:
        text = f.read_text(encoding="utf-8")
        m = re.search(r'^title: "(.*)"\s*$', text[:800], re.M)
        c = re.search(r"^created: \"(.*)\"\s*$", text[:800], re.M)
        manifest["pages"].append({
            "file": f.name,
            "title": m.group(1) if m else f.stem,
            "created": c.group(1) if c else "",
        })

    dest = TRASH_DIR / "people-noise-20261115"
    if dry_run:
        return {"would_move": len(pages), "dest": str(dest)}
    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.glob("*.md")):
        return {"skipped": f"隔离目录已存在且非空: {dest}", "moved": 0}
    (dest / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    moved = 0
    for f in pages:
        shutil.move(str(f), str(dest / f.name))
        moved += 1
    # 清理空目录
    try:
        PEOPLE_DIR.rmdir()
    except OSError:
        pass
    return {"moved": moved, "dest": str(dest)}


def merge_solid_hhg(dry_run: bool) -> Dict[str, Any]:
    """步骤 3：固体 HHG → 固体HHG 归并（变体转 stub + aliases 注册）。"""
    result: Dict[str, Any] = {}
    if not (_SOLID_HHG_VARIANT_FILE.exists() and _SOLID_HHG_CANONICAL_FILE.exists()):
        return {"skipped": "家族成员缺失或已归并", "files": [
            str(_SOLID_HHG_VARIANT_FILE), str(_SOLID_HHG_CANONICAL_FILE)]}

    from kb_wiki import parse_frontmatter

    # 同 _strip_page：先加载 knowledge_base 门面完成 _ensure_dirs 注入
    import knowledge_base  # noqa: F401

    var_fm, var_body = parse_frontmatter(_SOLID_HHG_VARIANT_FILE.read_text(encoding="utf-8"))
    keep_fm, keep_body = parse_frontmatter(_SOLID_HHG_CANONICAL_FILE.read_text(encoding="utf-8"))

    if var_fm.get("merged_into"):
        return {"skipped": "变体页已是 stub（幂等）"}

    # 变体的 related 并入主页（排除 people 噪音与自指）
    var_related = var_fm.get("related", [])
    if isinstance(var_related, str):
        var_related = [var_related]
    keep_related = keep_fm.get("related", [])
    if isinstance(keep_related, str):
        keep_related = [keep_related]
    merged_rel = list(keep_related)
    added_rel = []
    for r in var_related:
        if isinstance(r, str) and r.strip() and r != _SOLID_HHG_CANONICAL and r not in merged_rel:
            merged_rel.append(r.strip())
            added_rel.append(r.strip())
    keep_fm["related"] = merged_rel

    # aliases 注册变体
    keep_aliases = keep_fm.get("aliases", [])
    if isinstance(keep_aliases, str):
        keep_aliases = [keep_aliases]
    new_aliases = [a for a in (_SOLID_HHG_VARIANT, "固体_HHG") if a not in keep_aliases]
    keep_fm["aliases"] = keep_aliases + new_aliases

    # aliases.json 全库别名注册
    if not dry_run:
        aliases = {}
        if ALIASES_PATH.exists():
            try:
                aliases = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
            except Exception:
                aliases = {}
        entry = aliases.setdefault(_SOLID_HHG_CANONICAL, [])
        for a in new_aliases:
            if a not in entry:
                entry.append(a)
        ALIASES_PATH.write_text(
            json.dumps(aliases, ensure_ascii=False, indent=2), encoding="utf-8")

    if dry_run:
        return {"would_merge": True, "related_added": added_rel, "aliases_added": new_aliases}

    from kb_wiki import save_wiki_page

    save_wiki_page("wiki/concepts/固体HHG.md", keep_body, keep_fm,
                   defer_graph=True, defer_growth_log=True)

    # 变体页转重定向 stub（沿用 kb_merger 格式）
    ts = _now_utc()
    stub_fm = {
        "title": var_fm.get("title", _SOLID_HHG_VARIANT),
        "type": "concepts",
        "created": var_fm.get("created", ts),
        "updated": ts,
        "tags": [],
        "related": [_SOLID_HHG_CANONICAL],
        "source_raw": "",
        "growth_stage": "seedling",
        "confidence": 0.5,
        "merged_into": "wiki/concepts/固体HHG.md",
        "merged_at": ts,
    }
    stub_body = (
        f"# {_SOLID_HHG_VARIANT}（已合并）\n\n"
        f"本页已合并至 **{_SOLID_HHG_CANONICAL}**（`wiki/concepts/固体HHG.md`）。"
        f"标题空格变体归并（v7.3.85 人名页噪音治理顺带处理）。"
    )
    stub_fm["quality_gate_skip"] = True
    save_wiki_page("wiki/concepts/固体_HHG.md", stub_body, stub_fm,
                   defer_graph=True, defer_growth_log=True)
    return {"merged": True, "related_added": added_rel, "aliases_added": new_aliases}


def rebuild(dry_run: bool) -> Dict[str, Any]:
    """步骤 4：重建索引与图谱（两遍式端点校验清悬空边/人名节点）。"""
    if dry_run:
        return {"would_rebuild": True}
    from kb_maintenance import cmd_reindex, cmd_rebuild_graph

    import importlib.util

    kb_path = SCRIPTS_DIR / "knowledge_base.py"
    spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
    kb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb)
    cmd_reindex(kb)
    cmd_rebuild_graph(kb)
    return {"rebuilt": True}


def run(apply: bool, skip_rebuild: bool = False) -> Dict[str, Any]:
    dry_run = not apply
    mode = "dry-run 预览" if dry_run else "执行"
    print(f"○ 人名页噪音治理（{mode}）")

    targets = _collect_people_targets()
    print(f"  1. people 目标集: {len(targets)} 个标题/stem")
    r1 = strip_people_links(targets, dry_run)
    print(f"  2. 剥离链接: 页面 {r1['pages_changed']},"
          f" related 移除 {r1['related_removed']},"
          f" 规范化改名 {r1['related_renamed']},"
          f" 正文链接改写 {r1['body_links_rewritten']}")
    for line in r1.get("preview", []):
        print(f"     · {line}")
    r2 = quarantine_people(dry_run)
    print(f"  3. 隔离 people 目录: {json.dumps(r2, ensure_ascii=False, default=str)}")
    r3 = merge_solid_hhg(dry_run)
    print(f"  4. 固体HHG 家族归并: {json.dumps(r3, ensure_ascii=False, default=str)}")
    r4: Dict[str, Any] = {}
    if not skip_rebuild:
        r4 = rebuild(dry_run)
        print(f"  5. 索引/图谱重建: {json.dumps(r4, ensure_ascii=False, default=str)}")

    if dry_run:
        print("⚠ dry-run 未落盘。确认后执行：--apply")
    return {"strip": r1, "quarantine": r2, "merge": r3, "rebuild": r4}


def _self_check() -> bool:
    """自检：夹具验证剥离/改写/归并判定逻辑（零落盘）。"""
    ok = True

    # 链接模式：[[Ding]] / [[Ding|某人]] / [[固体 HHG]]
    p1 = _link_pattern("Ding")
    if not p1.search("- [[Ding]]"):
        print("✗ 自检失败: [[Ding]] 未命中")
        ok = False
    m = p1.search("[[Ding|丁某]]")
    if not m or m.group(1) != "丁某":
        print("✗ 自检失败: 别名链接解析异常")
        ok = False
    p2 = _link_pattern("固体 HHG")
    if not p2.search("- [[固体 HHG]]"):
        print("✗ 自检失败: 空格变体未命中")
        ok = False
    # 不误伤
    if p1.search("- [[Dingle温度]]"):
        print("✗ 自检失败: [[Dingle温度]] 被误伤")
        ok = False

    # 目标集收集（当前库应为 0 或已隔离态也能跑通）
    t = _collect_people_targets()
    print(f"✓ 目标集收集正常（当前 {len(t)} 项）")
    print("✓ kb_people_noise_purge 自检通过" if ok else "✗ 自检未通过")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="人名页噪音治理 v7.3.85")
    parser.add_argument("--apply", action="store_true", help="执行治理（默认 dry-run 预览）")
    parser.add_argument("--skip-rebuild", action="store_true", help="跳过索引/图谱重建")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        sys.exit(0 if _self_check() else 1)
    run(apply=args.apply, skip_rebuild=args.skip_rebuild)


if __name__ == "__main__":
    main()
