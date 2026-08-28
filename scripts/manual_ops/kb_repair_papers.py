#!/usr/bin/env python3
"""kb_repair_papers.py — 一次性修复 wiki/papers 历史写入缺陷（v6.8.51）。

修复两类历史污染（根因已于 v6.8.51 在 kb_wiki.save_wiki_page 门面层堵死，
本脚本负责清理存量）：

1. 双 frontmatter：旧版 _save_wiki_paper_note 用 kw_build 构建整页后交给
   save_wiki_page 二次包裹，外层 frontmatter 是默认值（title=文件名、
   type=concepts），内层才是真实元数据 → 消费方（list_wiki_pages/graph/
   检索过滤）只读到外层错误元数据。实测 147 篇笔记中 95 篇受污染。

2. 裸 arXiv ID 标题：外层默认 title 退化为 "2511.13114" 这类裸 ID，
   人类在 Obsidian 中不可读。实测 99 篇。修复时从 raw/papers/ 同 ID
   条目的 frontmatter 回填真实题名。

用法:
    python3 scripts/kb_repair_papers.py --dry-run   # 预览（默认动作）
    python3 scripts/kb_repair_papers.py             # 执行修复
    python3 scripts/kb_repair_papers.py --self-check

规范:
    - 仅使用 Python 3 标准库
    - 幂等：重复运行对已修复文件无操作
    - 修复后经 kb_wiki.save_wiki_page 门面写回（自动注入双向链接/更新图谱）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from paths import KNOWLEDGE_DIR, WIKI_DIR, RAW_DIR  # noqa: E402
from kb_text import parse_frontmatter  # noqa: E402

# 裸 arXiv ID 标题模式（含 "Paper: 2511.13114" 变体）
_BARE_ID_TITLE = re.compile(r"^(?:Paper:\s*)?(\d{4}\.\d{4,5})$")
# DOI 标题模式（v6.8.43 期刊论文）
_BARE_DOI_TITLE = re.compile(r"^(?:Paper:\s*)?(doi-\S+)$")


def _load_raw_titles() -> Dict[str, str]:
    """从 raw/papers/ 建立 arxiv_id → 真实题名 映射。"""
    titles: Dict[str, str] = {}
    raw_papers = RAW_DIR / "papers"
    if not raw_papers.exists():
        return titles
    for f in sorted(raw_papers.glob("*.md")):
        try:
            fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        aid = str(fm.get("arxiv_id", "")).strip()
        title = str(fm.get("title", "")).strip()
        if aid and title and aid not in titles:
            titles[aid] = title
    return titles


def _split_double_frontmatter(text: str) -> Optional[Tuple[Dict[str, Any], str]]:
    """若文本存在双 frontmatter（外层+内层），返回合并后的 fm 与真实正文。

    合并规则：内层（真实写入方元数据）覆盖外层默认值；
    created 取两者中更早的（保留真实创建时间）。
    """
    if not text.lstrip().startswith("---"):
        return None
    outer_fm, rest = parse_frontmatter(text)
    if not rest.lstrip().startswith("---"):
        return None
    inner_fm, body = parse_frontmatter(rest)
    if not inner_fm:
        return None
    merged = dict(outer_fm)
    merged.update(inner_fm)
    c_out = str(outer_fm.get("created", ""))
    c_in = str(inner_fm.get("created", ""))
    if c_out and (not c_in or c_out < c_in):
        merged["created"] = c_out
    return merged, body.strip()


def _needs_title_backfill(fm: Dict[str, Any]) -> Optional[str]:
    """若 title 是裸 ID，返回待回填的 arxiv_id；否则返回 None。"""
    title = str(fm.get("title", "")).strip()
    m = _BARE_ID_TITLE.match(title)
    return m.group(1) if m else None


def repair(dry_run: bool = False) -> Dict[str, Any]:
    """执行修复。返回统计摘要。

    覆盖目录：wiki/papers（双 FM/裸标题/类型）+ concepts/methods/people/reviews
    （仅类型规范化，v6.8.51 推广：历史单数 type 分裂类型桶）。
    """
    # 先加载门面（knowledge_base 加载后向 kb_wiki 注入 _ensure_dirs/log_growth 等依赖）
    import knowledge_base  # noqa: F401
    from kb_wiki import save_wiki_page, get_wiki_page

    raw_titles = _load_raw_titles()
    stats = {
        "scanned": 0,
        "fixed_double_fm": 0,
        "fixed_title": 0,
        "fixed_type": 0,
        "title_backfilled": 0,
        "title_not_found": 0,
        "unchanged": 0,
        "errors": 0,
    }

    files: List[Path] = []
    for sub in ("papers", "concepts", "methods", "people", "reviews"):
        d = WIKI_DIR / sub
        if d.exists():
            files.extend(sorted(d.glob("*.md")))
    stats["scanned"] = len(files)

    for f in files:
        rel = f.relative_to(KNOWLEDGE_DIR)
        in_papers = f.parent.name == "papers"
        try:
            text = f.read_text(encoding="utf-8")

            # ① 双 frontmatter 修复（仅 papers 有此历史污染源）
            if in_papers:
                split = _split_double_frontmatter(text)
                if split:
                    merged_fm, body = split
                    # ② 顺带回填裸 ID 标题
                    aid = _needs_title_backfill(merged_fm)
                    if aid and aid in raw_titles:
                        merged_fm["title"] = raw_titles[aid]
                        stats["title_backfilled"] += 1
                    elif aid:
                        stats["title_not_found"] += 1
                    if merged_fm.get("type") != "papers":
                        merged_fm["type"] = "papers"
                        stats["fixed_type"] += 1
                    if not dry_run:
                        save_wiki_page(str(rel), body, meta=merged_fm)
                    stats["fixed_double_fm"] += 1
                    print(f"  ✓ [双FM] {rel.name}")
                    continue

            fm, body = parse_frontmatter(text)

            # ② 裸 ID 标题修复（仅 papers）
            if in_papers:
                aid = _needs_title_backfill(fm)
                if aid and aid in raw_titles:
                    fm["title"] = raw_titles[aid]
                    if fm.get("type") != "papers":
                        fm["type"] = "papers"
                    if not dry_run:
                        save_wiki_page(str(rel), body, meta=fm)
                    stats["fixed_title"] += 1
                    print(f"  ✓ [标题] {rel.name} → {raw_titles[aid][:40]}")
                    continue

            # ③ type 规范化（v6.8.51，推广到全部子目录）：
            #    wiki/<dir>/ 下的页面 type 统一为目录名。历史写入器产生过
            #    "paper"/"concept"/缺失 等脏值，导致按类型过滤/统计分裂。
            parent_name = f.parent.name
            if parent_name in ("papers", "concepts", "methods", "people", "reviews", "projects"):
                old_type = fm.get("type", "(缺失)")
                if old_type != parent_name:
                    fm["type"] = parent_name
                    if not dry_run:
                        save_wiki_page(str(rel), body, meta=fm)
                    stats["fixed_type"] += 1
                    print(f"  ✓ [类型] {rel}: {old_type} → {parent_name}")
                    continue

            stats["unchanged"] += 1
        except Exception as e:
            stats["errors"] += 1
            print(f"  ✗ [错误] {rel.name}: {e}")

    return stats


def _self_check() -> bool:
    """自检：构造双 FM 与裸标题夹具，验证拆分/回填逻辑。"""
    import tempfile

    ok = True

    # 用例 1：双 frontmatter 拆分
    dirty = (
        "---\n"
        'title: "2511.13114"\n'
        'type: "concepts"\n'
        'created: "2026-08-13T03:26:08Z"\n'
        "---\n"
        "---\n"
        'title: "2511.13114"\n'
        'type: "papers"\n'
        'created: "2026-08-14T00:40:31Z"\n'
        'used_by_proposals: ["p1"]\n'
        "---\n\n"
        "## 深度解析\n\n正文内容。\n"
    )
    split = _split_double_frontmatter(dirty)
    if not split:
        print("  ✗ 双 FM 拆分失败")
        ok = False
    else:
        fm, body = split
        if fm.get("type") != "papers" or fm.get("created") != "2026-08-13T03:26:08Z":
            print(f"  ✗ 双 FM 合并语义错误: type={fm.get('type')} created={fm.get('created')}")
            ok = False
        if "深度解析" not in body:
            print("  ✗ 双 FM 正文提取错误")
            ok = False

    # 用例 2：正常单 FM 不误伤
    clean = '---\ntitle: "正常标题"\ntype: "papers"\n---\n\n正文。\n'
    if _split_double_frontmatter(clean) is not None:
        print("  ✗ 单 FM 被误判为双 FM")
        ok = False

    # 用例 3：裸 ID 标题识别
    if _needs_title_backfill({"title": "2511.13114"}) != "2511.13114":
        print("  ✗ 裸 ID 标题未识别")
        ok = False
    if _needs_title_backfill({"title": "Paper: 2405.16125"}) != "2405.16125":
        print("  ✗ Paper: 前缀变体未识别")
        ok = False
    if _needs_title_backfill({"title": "Real Paper Title"}) is not None:
        print("  ✗ 正常标题被误判")
        ok = False

    # 用例 4：save_wiki_page 门面防御回归（临时目录隔离，同 kb_wiki._self_check 模式）
    with tempfile.TemporaryDirectory() as td:
        import kb_wiki
        import kb_graph as _kg
        tmp_root = Path(td) / "knowledge"
        (tmp_root / "wiki" / "papers").mkdir(parents=True)
        _orig = {
            "KNOWLEDGE_DIR": kb_wiki.KNOWLEDGE_DIR,
            "WIKI_DIR": kb_wiki.WIKI_DIR,
            "_ensure_dirs": kb_wiki._ensure_dirs,
            "GRAPH_PATH": _kg.GRAPH_PATH,
            "ALIASES_PATH": _kg.ALIASES_PATH,
        }
        kb_wiki.KNOWLEDGE_DIR = tmp_root
        kb_wiki.WIKI_DIR = tmp_root / "wiki"
        _kg.GRAPH_PATH = tmp_root / "graph.json"
        _kg.ALIASES_PATH = tmp_root / "aliases.json"
        kb_wiki._ensure_dirs = lambda: None
        try:
            # 4a：整页文本误传 → 不再双包裹
            full_page = '---\ntitle: "T1"\ntype: "papers"\n---\n\n正文A\n'
            kb_wiki.save_wiki_page("wiki/papers/x.md", full_page)
            saved = (tmp_root / "wiki" / "papers" / "x.md").read_text(encoding="utf-8")
            if saved.count("title:") != 1:
                print(f"  ✗ 门面防御①失效：title 出现 {saved.count('title:')} 次")
                ok = False
            if 'type: "papers"' not in saved:
                print("  ✗ 门面防御①失效：内层真实 type 未透传")
                ok = False
            # 4b：空 content 仅更新 meta → 正文保留
            kb_wiki.save_wiki_page("wiki/papers/x.md", "", meta={"read_status": "deep-read"})
            saved2 = (tmp_root / "wiki" / "papers" / "x.md").read_text(encoding="utf-8")
            if "正文A" not in saved2 or "deep-read" not in saved2:
                print("  ✗ 门面防御②失效：空 content 清空了正文")
                ok = False
        finally:
            kb_wiki.KNOWLEDGE_DIR = _orig["KNOWLEDGE_DIR"]
            kb_wiki.WIKI_DIR = _orig["WIKI_DIR"]
            kb_wiki._ensure_dirs = _orig["_ensure_dirs"]
            _kg.GRAPH_PATH = _orig["GRAPH_PATH"]
            _kg.ALIASES_PATH = _orig["ALIASES_PATH"]

    if ok:
        print("  ✓ 双FM拆分 / 单FM不误伤 / 裸ID识别 / 门面防御 全部通过")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="修复 wiki/papers 历史 双 frontmatter 与裸 ID 标题")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写文件")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    print("=" * 50)
    print("◐ kb_repair_papers" + ("（dry-run）" if args.dry_run else ""))
    print("=" * 50)

    if args.self_check:
        passed = _self_check()
        print(("✓" if passed else "✗") + " kb_repair_papers 自检" + ("" if passed else " 失败"))
        return 0 if passed else 1

    stats = repair(dry_run=args.dry_run)
    print("-" * 50)
    print(
        f"{'预览' if args.dry_run else '完成'}: 扫描 {stats['scanned']} | "
        f"双FM修复 {stats['fixed_double_fm']} | 标题修复 {stats['fixed_title']} "
        f"（回填 {stats['title_backfilled']} / 未找到 raw 题名 {stats['title_not_found']}） | "
        f"类型修复 {stats['fixed_type']} | 无需处理 {stats['unchanged']} | 错误 {stats['errors']}"
    )
    if args.dry_run:
        print("提示：去掉 --dry-run 执行实际修复")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
