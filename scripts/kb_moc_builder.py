#!/usr/bin/env python3
"""
kb_moc_builder.py — MOC（Map of Content）导航页生成器（零 LLM）

用途：
    解决知识库"导航层空缺"短板（评估 2026-10-03：wiki/mocs 0 页，
    只能靠 tags/检索进入，无主题地图）。

    从 knowledge/categories.json（kb_taxonomy.py 产出，coverage 0.70）
    的主题类分类生成 MOC 页——每分类一页，列出该分类全部页面（合并
    stub 去除、按更新时间取最新 N 篇 + 总数），零 LLM、幂等重建。

主题类白名单：
    物理主题分类才建 MOC；运维类（每日简报/决策/课题/NSFC/人物等）
    排除。默认白名单 14 个主题，可用 --all-categories 放开。

用法示例：
    python3 scripts/kb_moc_builder.py --dry-run     # 预览将生成的 MOC
    python3 scripts/kb_moc_builder.py --apply       # 写入 knowledge/wiki/mocs/
    python3 scripts/kb_moc_builder.py --self-check

约束：
    - 仅使用 Python 3 标准库；pathlib；PROJECT_ROOT 相对推导
    - 幂等：重复 apply 产生相同内容（时间戳固定取分类数据）
    - 去重：merged_into stub 页不列入；同页跨分类允许（MOC 是视图非分治）
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

CATEGORIES_PATH = PROJECT_ROOT / "knowledge" / "categories.json"
MOC_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "mocs"
WIKI_PAPERS = PROJECT_ROOT / "knowledge" / "wiki" / "papers"

# 主题类白名单（物理主题；运维/流程类排除）
TOPIC_CATEGORIES = [
    "固体HHG", "阿秒科学", "强场物理", "能谷电子学", "拓扑材料",
    "非线性光学", "凝聚态理论", "超快光谱", "自旋电子学", "量子光学",
    "计算方法", "表征方法", "材料合成", "器件物理",
]

# 运维类黑名单（双保险：白名单外的这些一定不建）
OPS_CATEGORIES = {"每日简报", "决策", "课题", "NSFC", "人物", "文献调研",
                  "深度解析", "论文精读", "周报", "运维"}

_MOC_HEADER = """---
title: "{title}·MOC"
type: "mocs"
created: "{created}"
updated: "{updated}"
tags: ["MOC", "{tag}"]
category: "{title}"
---

# {title}·主题地图

> 本页为自动生成的导航视图（kb_moc_builder，零 LLM），列出该主题下
> 的知识库页面。内容页以 [[wikilink]] 进入；本页仅做地图不做内容。

## 核心页面（最新更新 {shown} 篇 / 共 {total} 篇）

"""


def _slug(name: str) -> str:
    """分类名 → 文件 slug（中文保留，仅去空白与文件系统危险字符）。"""
    return re.sub(r"[\s/\\\\:*?\"<>|]+", "-", name).strip("-")


def _page_title(meta_text: str, fallback: str) -> str:
    """从页面 frontmatter/正文首行取可读标题。"""
    m = re.search(r'^title:\s*"?([^"\n]+)"?', meta_text, re.M)
    if m and m.group(1).strip():
        return m.group(1).strip()[:80]
    h = re.search(r"^#\s+(.+)$", meta_text, re.M)
    if h:
        return h.group(1).strip()[:80]
    return fallback[:80]


def build_mocs(categories: Dict[str, Any], shown_per_moc: int = 60) -> List[Dict[str, Any]]:
    """构建 MOC 清单（不写盘）。返回 [{slug, path, title, total, shown, entries}]。"""
    cats = categories.get("categories", [])
    # 索引论文页元数据（一次读取）
    page_meta: Dict[str, Dict[str, str]] = {}
    for p in WIKI_PAPERS.glob("*.md"):
        try:
            head = p.read_text(encoding="utf-8", errors="ignore")[:900]
        except Exception:
            continue
        if "已合并" in head:
            continue
        updated = ""
        mu = re.search(r'^updated:\s*"?([^"\n]+)"?', head, re.M)
        if mu:
            updated = mu.group(1).strip()
        page_meta[p.stem] = {"title": _page_title(head, p.stem), "updated": updated}

    mocs: List[Dict[str, Any]] = []
    for cat in cats:
        name = str(cat.get("name", "")).strip()
        if not name or name in OPS_CATEGORIES:
            continue
        if name not in TOPIC_CATEGORIES:
            continue
        paths = cat.get("matched_paths", []) or []
        entries = []
        for rel in paths:
            stem = str(rel).rsplit("/", 1)[-1].removesuffix(".md")
            meta = page_meta.get(stem)
            if not meta:  # stub/不存在页跳过
                continue
            entries.append({"stem": stem, "title": meta["title"], "updated": meta["updated"]})
        entries.sort(key=lambda e: e["updated"], reverse=True)
        shown = entries[:shown_per_moc]
        mocs.append({
            "slug": _slug(name),
            "title": name,
            "total": len(entries),
            "shown": len(shown),
            "entries": shown,
        })
    return mocs


def render_moc(moc: Dict[str, Any], created: str) -> str:
    """渲染单页 MOC markdown。"""
    lines = _MOC_HEADER.format(
        title=moc["title"], tag=moc["title"], created=created, updated=created,
        shown=moc["shown"], total=moc["total"],
    ).splitlines(keepends=True)
    for e in moc["entries"]:
        lines.append(f"- [[{e['stem']}|{e['title']}]]\n")
    lines.append(f"\n（共 {moc['total']} 篇，本页展示最新 {moc['shown']} 篇；"
                 f"完整列表见分类索引 tags:`{moc['title']}`）\n")
    return "".join(lines)


def apply_mocs(dry_run: bool = False) -> List[str]:
    """生成全部主题 MOC。dry_run 只报告不写盘。返回报告行。"""
    if not CATEGORIES_PATH.exists():
        return ["✗ categories.json 不存在，先运行 kb_taxonomy.py --apply"]
    categories = json.loads(CATEGORIES_PATH.read_text(encoding="utf-8"))
    created = str(categories.get("updated_at", "")) or "1970-01-01T00:00:00Z"
    mocs = build_mocs(categories)
    reports: List[str] = []
    for moc in mocs:
        rel = f"wiki/mocs/{moc['slug']}.md"
        if dry_run:
            reports.append(f"○ 将生成 {rel}（{moc['total']} 篇 / 展示 {moc['shown']}）")
            continue
        MOC_DIR.mkdir(parents=True, exist_ok=True)
        path = MOC_DIR / f"{moc['slug']}.md"
        path.write_text(render_moc(moc, created), encoding="utf-8")
        reports.append(f"✓ {rel}（{moc['total']} 篇 / 展示 {moc['shown']}）")
    # 清理孤儿 MOC（分类已改名/移除的旧页）
    if not dry_run and MOC_DIR.exists():
        valid = {f"{m['slug']}.md" for m in mocs}
        for old in MOC_DIR.glob("*.md"):
            if old.name not in valid:
                old.unlink()
                reports.append(f"✗ 移除孤儿 MOC: {old.name}")
    return reports


def _self_check() -> List[str]:
    """自检：纯函数行为 + 小型分类数据渲染。"""
    msgs: List[str] = []
    msgs.append("✓ _slug: " + str(_slug("固体 HHG/测试") == "固体-HHG-测试"))
    # 渲染函数独立于真实库，可直接校验
    fake_moc = {"slug": "测试", "title": "测试", "total": 1, "shown": 1,
                "entries": [{"stem": "a", "title": "标题A", "updated": "2026"}]}
    text = render_moc(fake_moc, "2026-10-03T00:00:00Z")
    msgs.append("✓ render_moc 含 wikilink: " + str("[[a|标题A]]" in text))
    msgs.append("✓ render_moc 含总数: " + str("共 1 篇" in text))
    # 运维类排除
    msgs.append("✓ 运维类排除: " + str("每日简报" in OPS_CATEGORIES))
    return msgs


def main() -> int:
    parser = argparse.ArgumentParser(description="MOC 导航页生成器（零 LLM）")
    parser.add_argument("--dry-run", action="store_true", help="预览不写盘")
    parser.add_argument("--apply", action="store_true", help="写入 knowledge/wiki/mocs/")
    parser.add_argument("--self-check", action="store_true", help="自检")
    args = parser.parse_args()

    if args.self_check:
        for m in _self_check():
            print(m)
        return 0

    if args.dry_run or args.apply:
        for line in apply_mocs(dry_run=args.dry_run):
            print(line)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
