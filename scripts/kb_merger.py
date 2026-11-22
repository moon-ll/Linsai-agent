#!/usr/bin/env python3
"""重复 wiki 页合并执行器（v6.9.6）。

背景
----
kb_health_weekend 自 v3.x 就能检测"同名/近义概念"（_detect_duplicate_concepts
按 title 分组输出重复组），但检测出重复对后没有合并动作——"检测有、执行缺"。
本脚本补上执行器：以重复组为输入，选主页面、LLM 辅助融合正文、迁移 related
边/tags，被并页降级为重定向 stub（保留检索可达性）。

设计约束
--------
1. LLM 是增强不是依赖：融合调用失败时降级为"边迁移 + 正文附录并置"，
   保证合并永远可完成，只是质量略低。
2. 周限量护栏：默认每周最多 5 对（MAX_PAIRS_PER_WEEK），由周日反思 job
   （reflection_kb_merge_duplicates）调用，控 LLM 成本。
3. 全部写入走 kb_wiki.save_wiki_page 门面（frontmatter 合一防污染，
   自动记 growth log）。
4. 重定向 stub 而非删除：图谱/检索仍能命中旧标题，正文指向主页面。

用法示例
--------
    python3 scripts/kb_merger.py --dry-run      # 预览将合并的对
    python3 scripts/kb_merger.py --max-pairs 5  # 执行合并（周限量）
    python3 scripts/kb_merger.py --self-check   # 模块自检（零 LLM 零写入）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc  # noqa: E402

MAX_PAIRS_PER_WEEK = 5          # 周限量护栏（LLM 成本控制）
LLM_TIMEOUT = 120               # 单对融合超时
MAX_MERGE_BODY_CHARS = 8000     # 送 LLM 的正文截断

# 周执行留痕（防同周重复计数；周日 job 每周重置文件名）
_MERGE_LOG_DIR = PROJECT_ROOT / "memory" / "weekend-reflection"


# ---------------------------------------------------------------------------
# 检测：复用 kb_health_weekend 的同名分组
# ---------------------------------------------------------------------------


def _entity_key(stem: str) -> str:
    """v6.10.14: 提取文件名的实体标识键，用于排除"同名不同实体"误判。

    真重复（同一 arXiv 论文双存）文件名共享 ID 首段：analyses/
    2407.19609-attosecond-… vs papers/2407.19609。模板标题组则是不同
    proposal_id/日期共享同名 title：reports/general-quantum-… vs
    reports/general-moire-…、讨论-20260619-… vs 讨论-20260702-…。
    规则：按 "-" 取首段；首段纯字母（无数字，如 general/讨论）时再拼
    第二段——arXiv ID 首段含数字天然满足，模板组靠第二段区分。

    v7.2.48：arXiv 论文页优先用 arxiv_id 作实体键（治 slug 代退化）。
    旧规则对 slug 代命名 `2024-2406_14320-many-body-…` 取首段得
    `2024`（纯年份），而蒸馏产出的 slug 代全部形如 `<年份>-<id>-<标题>`，
    于是**同一年的所有论文页共用一个实体键** → 实体一致性守卫对
    同年同名论文彻底失效 → kb_merge 把两篇不同论文并成一篇
    （10-26 12h 健康检查实测：2406.14320 被并入 2407.16350，
    两页原始笔记各自保留但语义已错位；全库另有 2 组同类潜伏）。
    修复：文件名能解析出 arxiv_id 时直接以该 id 为实体键
    （`extract_arxiv_id` 覆盖裸 id 代与 slug 代两种命名），
    无法解析时才回退旧启发式（模板标题组不受影响）。
    """
    aid = extract_arxiv_id(stem)
    if aid:
        return f"arxiv:{aid}"
    parts = stem.split("-")
    if len(parts) >= 2 and not any(c.isdigit() for c in parts[0]):
        return f"{parts[0]}-{parts[1]}"
    return parts[0]


def detect_merge_pairs() -> List[Dict[str, Any]]:
    """返回待合并组：[{title, paths}]（同名且同实体）。

    排除已是重定向 stub 的页面（frontmatter 含 merged_into）。
    v6.10.14: 实体一致性过滤——同名组内文件名实体键不一致即"模板标题
    下不同实体"（不同课题的 reports/versions 页、不同日期的讨论记录），
    一律排除。实测两轮事故：09-06 与 09-13 kb_merge 把 moire 课题报告
    并入 qgi、3+3 个不同日期讨论页并成 stub，纯 title 分组无法区分
    "同一篇论文存两处"与"不同实体共用模板标题"。
    """
    from kb_health_weekend import _detect_duplicate_concepts
    from kb_wiki import get_wiki_page

    groups = _detect_duplicate_concepts()
    out: List[Dict[str, Any]] = []
    for g in groups:
        live = [p for p in g["paths"] if not _is_stub(p, get_wiki_page)]
        if len(live) > 1:
            from pathlib import Path as _P
            keys = {_entity_key(_P(p).stem) for p in live}
            if len(keys) > 1:
                continue  # 同名不同实体（模板标题组），排除
            out.append({"title": g["title"], "paths": live})
    return out


def _is_stub(path: str, getter) -> bool:
    """判断页面是否已是合并重定向 stub。"""
    page = getter(path)
    if not page:
        return False
    return bool((page.get("frontmatter") or {}).get("merged_into"))


# ---------------------------------------------------------------------------
# 合并核心
# ---------------------------------------------------------------------------


def pick_primary(paths: List[str], getter) -> str:
    """选主页面：正文长者优先（信息量大），同长比 updated_at 新者。"""
    best, best_key = "", (-1, "")
    for p in paths:
        page = getter(p)
        if not page:
            continue
        body_len = len(page.get("body", ""))
        updated = (page.get("frontmatter") or {}).get("updated_at", "")
        if body_len > best_key[0] or (body_len == best_key[0] and updated > best_key[1]):
            best, best_key = p, (body_len, updated)
    return best or paths[0]


def merge_related(primary_related: List[str], other_related: List[str],
                  primary_title: str, other_title: str) -> List[str]:
    """合并 related 边：并集去重，剔除互指与自指，保持主页面顺序在前。"""
    # v7.2.45 防御：title / related 项可能来自非字符串 frontmatter 值
    # （纯数字 title 曾被类型推断成 int），统一转字符串避免 .lower() 抛
    # AttributeError 打断整条周末反思链。
    def _s(v: Any) -> str:
        return str(v) if v is not None else ""

    merged = [_s(r) for r in (primary_related or [])]
    titles = {_s(primary_title).lower(), _s(other_title).lower()}
    for r in other_related or []:
        rs = _s(r)
        if rs and rs not in merged and rs.lower() not in titles:
            merged.append(rs)
    return [r for r in merged if r and r.lower() not in titles]


def _build_merge_prompt(title: str, primary_body: str, other_body: str) -> str:
    return (
        "你是知识库编辑。以下是对同一概念「%s」的两个 wiki 页正文，"
        "请合并为一篇结构化 Markdown：保留双方全部关键信息（定义/机制/"
        "实验/公式/来源），重复段落只留更完整版本，按逻辑重组章节，"
        "不要添加原文没有的内容，不要输出 frontmatter。\n\n"
        "=== 页面 A（主，内容较全）===\n%s\n\n=== 页面 B（被并入）===\n%s\n\n"
        "直接输出合并后的正文 Markdown："
    ) % (title, primary_body[:MAX_MERGE_BODY_CHARS], other_body[:MAX_MERGE_BODY_CHARS])


def _fallback_body(primary_body: str, other_body: str, other_title: str) -> str:
    """LLM 失败时的保守合并：A 原文 + B 独有内容附录。"""
    appendix = "\n\n## 合并自「%s」\n\n%s\n" % (other_title, (other_body or "").strip())
    return (primary_body or "").rstrip() + appendix


def build_stub_body(other_title: str, primary_title: str, primary_path: str) -> str:
    """构造被并页的重定向 stub 正文。"""
    return (
        "# %s（已合并）\n\n本页已合并至 **%s**（`%s`）。\n\n"
        "请前往主页面查看完整内容。\n"
    ) % (other_title, primary_title, primary_path)


def _ensure_wired() -> None:
    """确保 kb_wiki 门面依赖已注入（v6.10.52）。

    kb_wiki 的 _ensure_dirs/log_growth 是占位 None，由 knowledge_base
    模块加载时注入（knowledge_base.py 模块级 _kb_wiki_mod._ensure_dirs=…
    ）。kb_merger 被独立运行（CLI / 反思 job 直接 import）时若无人先
    import knowledge_base，save_wiki_page 会在 _ensure_dirs() 处以
    'NoneType' object is not callable 崩溃——实测 503 对全数失败的
    根因。kb_wiki 是 sys.modules 单例，import knowledge_base 的注入
    副作用对已持有引用的调用方同样生效。
    """
    import kb_wiki
    if kb_wiki._ensure_dirs is None:
        import knowledge_base  # noqa: F401  # 加载即完成注入


def merge_pair(primary_path: str, other_path: str, dry_run: bool = False,
               use_llm: bool = True) -> Dict[str, Any]:
    """合并一对页面：other 并入 primary。

    Args:
        use_llm: False 时跳过 LLM 融合，直接确定性附录并置（论文双世代
                 去重等大批量场景用，零成本零幻觉）。

    Returns:
        {"success", "primary", "merged", "mode": "llm"|"fallback", "edges"}
    """
    from kb_wiki import get_wiki_page, save_wiki_page

    _ensure_wired()
    pri = get_wiki_page(primary_path)
    oth = get_wiki_page(other_path)
    if not pri or not oth:
        return {"success": False, "error": "页面读取失败"}

    pri_fm, oth_fm = pri.get("frontmatter", {}), oth.get("frontmatter", {})
    pri_title = pri_fm.get("title", Path(primary_path).stem)
    oth_title = oth_fm.get("title", Path(other_path).stem)

    # 1) 融合正文（LLM 增强，失败降级；dry-run 直接预览不花 LLM 成本）
    mode = "fallback"
    merged_body = _fallback_body(pri.get("body", ""), oth.get("body", ""), oth_title)
    ok, text, _meta = False, "", None
    if use_llm and not dry_run:
        try:
            from llm_gateway import llm_complete
            # v7.3.86: 双页融合为蒸馏/格式化任务，prefer=governance 走 glm-first
            ok, text, _meta = llm_complete(
                "你是知识库蒸馏器，只输出 Markdown 正文。",
                _build_merge_prompt(pri_title, pri.get("body", ""), oth.get("body", "")),
                timeout=LLM_TIMEOUT,
                prefer="governance",
            )
        except Exception:
            ok = False
        if ok and text and len(text.strip()) > 50:
            merged_body = text.strip()
            mode = "llm"
    elif dry_run:
        mode = "preview"

    # 2) 边与标签迁移
    new_related = merge_related(
        pri_fm.get("related", []), oth_fm.get("related", []), pri_title, oth_title
    )
    new_tags = list(pri_fm.get("tags", []))
    for t in oth_fm.get("tags", []):
        if t and t not in new_tags:
            new_tags.append(t)

    if dry_run:
        return {
            "success": True, "dry_run": True, "mode": mode,
            "primary": primary_path, "merged": other_path,
            "edges": len(new_related), "tags": len(new_tags),
        }

    # 3) 写主页面（正文 + 合并后的 frontmatter）
    pri_fm["related"] = new_related
    pri_fm["tags"] = new_tags
    pri_fm["updated_at"] = now_utc()
    pri_fm["merged_from"] = pri_fm.get("merged_from", []) + [other_path]
    save_wiki_page(primary_path, merged_body, pri_fm)

    # 4) 被并页 → 重定向 stub（保留 title/source_raw 供检索）
    oth_fm["merged_into"] = primary_path
    oth_fm["merged_at"] = now_utc()
    oth_fm["updated_at"] = now_utc()
    save_wiki_page(other_path, build_stub_body(oth_title, pri_title, primary_path), oth_fm)

    return {
        "success": True, "mode": mode,
        "primary": primary_path, "merged": other_path,
        "edges": len(new_related), "tags": len(new_tags),
    }


def run_merge(max_pairs: int = MAX_PAIRS_PER_WEEK, dry_run: bool = False) -> Dict[str, Any]:
    """批量执行：按组逐对合并，单对失败跳过不中断。"""
    from kb_wiki import get_wiki_page

    pairs = detect_merge_pairs()
    done, failed = [], []
    budget = max_pairs
    for g in pairs:
        if budget <= 0:
            break
        primary = pick_primary(g["paths"], get_wiki_page)
        for p in g["paths"]:
            if p == primary or budget <= 0:
                continue
            try:
                r = merge_pair(primary, p, dry_run=dry_run)
                if r.get("success"):
                    done.append({"primary": primary, "merged": p, "mode": r.get("mode")})
                    budget -= 1
                else:
                    failed.append({"pair": [primary, p], "error": r.get("error")})
            except Exception as e:
                failed.append({"pair": [primary, p], "error": str(e)})

    return {
        "groups_detected": len(pairs),
        "merged": len(done),
        "failed": len(failed),
        "detail": done,
        "errors": failed,
        "dry_run": dry_run,
    }


# ---------------------------------------------------------------------------
# v6.10.52 论文页双世代去重（确定性，零 LLM）
#
# 2026-09-25 体检实锤：wiki/papers 同一 arXiv 论文两套页面并存——
# 旧代 slug 命名 `2010-1006_1827-attosecond-….md`（2026-08，title 为论文
# 真名，质量高）与新代裸 id `1006.1827.md`（2026-09，title=arxiv_id，
# 30% 带空"深度解析"占位小节），561 组重复占 papers 目录 54%。既有
# detect_merge_pairs 按 title 分组对这类重复完全失明（两代 title 不同），
# 且 _entity_key 按文件名首段取键（裸 id 代取到 `1006.1827`、slug 代取到
# 年份 `2010`），同名也会被判"不同实体"排除。本模块按 arxiv_id 文件名
# 分组，slug 代为主页面（与 kb_distill 产出命名一致，是未来规范），
# 裸 id 代正文以附录并入后转 stub——确定性执行，不走 LLM。
# ---------------------------------------------------------------------------

_BARE_ID_PAT = re.compile(r"^(\d{4}\.\d{4,5})(?:v\d+)?$")
_SLUG_ID_PAT = re.compile(r"^\d{4}-(\d{4})[._](\d{4,5})(?:v\d+)?-")
# v7.2.48：采集侧自 2026 起产出 `<年份>-<4位字母数字>-<4位字母数字>-<slug>`
# 命名（deepxiv 论文库 id，如 `2026-9jcm-8gd8-rainbow-…`），与旧 slug 代
# 同样带年份前缀 → 实体键若取年份会同样退化。
_BARE_ALNUM_PAT = re.compile(r"^(\d{4}\.[a-z]{4}[a-z0-9]{4})(?:v\d+)?$")
_SLUG_ALNUM_PAT = re.compile(r"^\d{4}-([a-z0-9]{4}-[a-z0-9]{4})(?:v\d+)?-")
# v7.2.49：采集侧另有一代「紧凑序号」命名 `<年份>-<YYMM><NNNNN>-<slug>`
# （如 `2026-260723652-carrier-envelope-…`），id 段为 9 位 = YYMM + 5 位
# 序号，与 slug 代的 `<YYMM>_<NNNNN>` 落在同一 arxiv id 空间。
_SLUG_COMPACT_PAT = re.compile(r"^\d{4}-(\d{4})(\d{5})-.+$")
# v7.2.49：analyses/ 目录的 `<arxivid>-<slug>` 命名（裸 id 直接连 slug，
# 无年份前缀）——同一 arxiv id 的另一种写法，须与裸 id 代归一到同一键。
_BARE_SLUG_PAT = re.compile(r"^(\d{4}\.\d{4,5})-.+$")


def extract_arxiv_id(stem: str) -> str:
    """从 wiki/papers 文件名 stem 提取 arXiv id，非 arXiv 命名返回空串。

    兼容各代命名（均归一到 `YYMM.NNNNN` 规范 id 形式）：
    - 裸 id 代：`1006.1827`
    - slug 代：`2010-1006_1827-slug…`（id 中的 `.` 写作 `_`，
      也兼容少数未替换的 `.` 变体）
    - 紧凑序号代：`2026-260723652-slug…`（9 位 = YYMM + 5 位序号）
    - analyses 代：`1006.1827-slug…`（裸 id 直接连 slug）

    v7.2.48：新增 arXiv 新式字母数字 id（`9jcm-8gd8`，采集侧命名
    `<年份>-<id>-<slug>`）——这类 id 同样带年份前缀，若实体键取年份
    会与旧 slug 代一样退化，故一并解析。

    v7.2.49：补齐紧凑序号代与 analyses 代——两者此前解析失败回退到
    年份首段，导致同一篇论文的两种命名被判为不同实体。
    """
    m = _BARE_ID_PAT.match(stem)
    if m:
        return m.group(1)
    m = _SLUG_ID_PAT.match(stem)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    m = _BARE_ALNUM_PAT.match(stem)
    if m:
        return m.group(1)
    m = _SLUG_ALNUM_PAT.match(stem)
    if m:
        return m.group(1)
    m = _SLUG_COMPACT_PAT.match(stem)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    m = _BARE_SLUG_PAT.match(stem)
    if m:
        return m.group(1)
    return ""


def detect_paper_generation_groups(pages: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """按 arxiv_id 分组检测双世代重复论文页。

    Args:
        pages: 可注入的页面列表（每项 {"path", "merged_into"}），默认扫描
               wiki/papers/ 实际文件。注入模式供自检/测试零 IO 使用。

    Returns:
        [{"arxiv_id", "paths": [live 页 path…]}]，仅含 ≥2 个存活页的组。
    """
    if pages is None:
        from kb_wiki import list_wiki_pages
        pages = [
            {"path": p["path"], "merged_into": p.get("merged_into", "")}
            for p in list_wiki_pages("papers")
        ]
    groups: Dict[str, List[str]] = {}
    for page in pages:
        if page.get("merged_into"):
            continue  # 已是 stub
        path = page.get("path", "")
        stem = Path(path).stem
        arxiv_id = extract_arxiv_id(stem)
        if arxiv_id:
            groups.setdefault(arxiv_id, []).append(path)
    return [
        {"arxiv_id": k, "paths": v} for k, v in sorted(groups.items()) if len(v) > 1
    ]


def _pick_paper_primary(paths: List[str], getter) -> str:
    """论文组选主：slug 代（文件名含 `-`）优先，多个 slug 代比正文长度。"""
    slug_paths = [p for p in paths if "-" in Path(p).stem]
    candidates = slug_paths or list(paths)
    return pick_primary(candidates, getter)


def merge_paper_generations(
    dry_run: bool = False,
    max_groups: Optional[int] = None,
    use_llm: bool = False,
) -> Dict[str, Any]:
    """执行双世代论文页去重：slug 代吸收裸 id 代（默认确定性附录并置）。

    合并后收集 {旧 title: 新 title} 映射并调用 rewrite_references 全库
    改写 related/正文 wikilink，保证引用不断链。

    Returns:
        {"groups_detected", "merged", "failed", "refs_rewritten",
         "title_map", "detail", "errors", "dry_run"}
    """
    from kb_wiki import get_wiki_page

    groups = detect_paper_generation_groups()
    done, failed, title_map = [], [], {}
    budget = max_groups if max_groups is not None else len(groups)
    for g in groups:
        if budget <= 0:
            break
        primary = _pick_paper_primary(g["paths"], get_wiki_page)
        for p in g["paths"]:
            if p == primary or budget <= 0:
                continue
            try:
                r = merge_pair(primary, p, dry_run=dry_run, use_llm=use_llm)
                if r.get("success"):
                    done.append({"primary": primary, "merged": p, "mode": r.get("mode")})
                    budget -= 1
                    pri_page = get_wiki_page(primary)
                    oth_page = get_wiki_page(p)
                    if pri_page and oth_page:
                        pri_title = (pri_page.get("frontmatter") or {}).get(
                            "title", Path(primary).stem)
                        oth_title = (oth_page.get("frontmatter") or {}).get(
                            "title", Path(p).stem)
                        if oth_title != pri_title:
                            title_map[oth_title] = pri_title
                else:
                    failed.append({"pair": [primary, p], "error": r.get("error")})
            except Exception as e:
                failed.append({"pair": [primary, p], "error": str(e)})

    refs_result = {"pages_changed": 0}
    if title_map and not dry_run:
        refs_result = rewrite_references(title_map)

    return {
        "groups_detected": len(groups),
        "merged": len(done),
        "failed": len(failed),
        "refs_rewritten": refs_result.get("pages_changed", 0),
        "title_map": title_map,
        "detail": done,
        "errors": failed,
        "dry_run": dry_run,
    }


# ---------------------------------------------------------------------------
# v6.10.52 全库引用改写：{旧 title: 新 title} → related 字段 + 正文 wikilink
# ---------------------------------------------------------------------------

def rewrite_references(mapping: Dict[str, str], dry_run: bool = False) -> Dict[str, Any]:
    """按映射全库改写 wiki 页引用（frontmatter related + 正文 [[wikilink]]）。

    - related 数组项精确匹配旧 title 才替换（不做子串替换，防误伤）。
    - 正文仅替换 [[旧]] / [[旧|别名]] 形式的 wikilink。
    - 只回写有变化的页面，走 kb_wiki 门面 save_wiki_page 保持格式统一。
    """
    if not mapping:
        return {"pages_changed": 0, "hits": 0, "paths_changed": []}

    import re
    from kb_wiki import get_wiki_page, list_wiki_pages, save_wiki_page

    _ensure_wired()
    pages_changed, hits, paths_changed = 0, 0, []
    for page in list_wiki_pages():
        path = page.get("path", "")
        full = get_wiki_page(path)
        if not full:
            continue
        fm = full.get("frontmatter") or {}
        body = full.get("body", "")

        related = fm.get("related", [])
        new_related = []
        changed = False
        for r in related:
            if r in mapping and mapping[r] != r:
                new_related.append(mapping[r])
                changed = True
                hits += 1
            else:
                new_related.append(r)

        new_body = body
        for old, new in mapping.items():
            pat = re.compile(r"\[\[" + re.escape(old) + r"(\||\]\])")

            def _repl(m, _new=new):
                return "[[" + _new + m.group(1)

            new_body, n = pat.subn(_repl, new_body)
            if n:
                changed = True
                hits += n

        if not changed:
            continue
        if dry_run:
            pages_changed += 1
            paths_changed.append(path)
            continue
        fm["related"] = new_related
        save_wiki_page(path, new_body, fm)
        pages_changed += 1
        paths_changed.append(path)

    return {"pages_changed": pages_changed, "hits": hits,
            "paths_changed": paths_changed, "dry_run": dry_run}


# ---------------------------------------------------------------------------
# v7.3.77 methods 同命名空间确定性归并（零 LLM，--dedup-papers 的泛化）
#
# 2026-11-06 起巡检实证：wiki/methods 中「磁/自旋群对称性分析」家族沉淀了
# 十余个近同名变体页（磁点群_/磁点群/磁群_/磁性群_/自旋空间群_磁性群 等
# 组合命名，methods_settle 每轮按论文语境现起名）+ hash 命名散页
# （m81064a58 等），同一方法家族的知识被切碎。既有两条去重通道对此均
# 失明：detect_merge_pairs 要求 title 完全相等；论文双世代按 arxiv_id
# 分组（methods 页无 id）。本节补齐两条通道：
#   - detect_method_name_groups：按归一键自动聚组（强重复自动归并通道）
#   - merge_name_family：显式家族清单合并通道（人工/ZCode 逐页实读内容
#     后策展成员清单，机器零 LLM 执行：附录并置 + stub 重定向 +
#     related/tags 边迁移 + 全库引用改写 + aliases 注册；幂等可重放）
# ---------------------------------------------------------------------------

ALIASES_PATH = PROJECT_ROOT / "knowledge" / "aliases.json"

_PAREN_QUALIFIER_PAT = re.compile(r"（[^）]*）|\([^)]*\)")
_NAME_SEP_PAT = re.compile(r"[\s_/\-—·、，,]+")


def normalize_method_name(name: str) -> str:
    """近同名归一键：剥离括号限定词与分隔符，拉丁字符转小写。

    「磁点群/自旋群对称性分析」→「磁点群自旋群对称性分析」；
    「磁性空间群对称性分析（拓扑量子化学框架）」→「磁性空间群对称性分析」。
    语义近邻（磁群/磁性群/磁点群 等同义缩写）不在此归一——那类家族由
    人工实读内容后走 merge_name_family 显式清单，机器不做语义猜测。
    """
    s = _PAREN_QUALIFIER_PAT.sub("", str(name))
    s = _NAME_SEP_PAT.sub("", s)
    return s.lower()


def detect_method_name_groups(
    namespace: str = "methods",
    pages: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """按 title 归一键分组检测近同名重复页（仅存活性页面）。

    Args:
        pages: 可注入页面列表（{"path","title","merged_into"}），缺省扫描
               指定命名空间。注入模式供自检/测试零 IO 使用。
    Returns:
        [{"name_key", "paths": [≥2 个存活页]}]，按 name_key 排序。
    """
    if pages is None:
        from kb_wiki import list_wiki_pages
        pages = [
            {"path": p["path"],
             "title": p.get("title") or Path(p["path"]).stem,
             "merged_into": p.get("merged_into", "")}
            for p in list_wiki_pages(namespace)
        ]
    groups: Dict[str, List[str]] = {}
    for page in pages:
        if page.get("merged_into"):
            continue  # 已是 stub
        key = normalize_method_name(page.get("title") or Path(page["path"]).stem)
        if key:
            groups.setdefault(key, []).append(page["path"])
    return [
        {"name_key": k, "paths": v} for k, v in sorted(groups.items()) if len(v) > 1
    ]


def _register_name_aliases(canonical: str, aliases: List[str]) -> int:
    """aliases.json 注册（canonical title → [被并页 title…]），幂等。"""
    import json

    from common import save_json

    data = {}
    if ALIASES_PATH.exists():
        try:
            data = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    lst = data.get(canonical)
    if isinstance(lst, str):
        lst = [lst]
    lst = list(lst or [])
    added = 0
    for a in aliases:
        if a and a != canonical and a not in lst:
            lst.append(a)
            added += 1
    if added or canonical not in data:
        data[canonical] = lst
        save_json(ALIASES_PATH, data)
    return added


def merge_name_family(
    primary_path: str,
    member_paths: List[str],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """把显式家族成员并入主页面（确定性附录并置，零 LLM）。

    成员清单须由人工/ZCode 实读内容后策展（归一键无法可靠判定「磁群 vs
    磁点群 vs 磁空间群」这类语义近邻，机器不猜）。返回结构与
    merge_paper_generations 对齐，便于 CLI 摘要展示与留痕对账。
    """
    from kb_wiki import get_wiki_page

    _ensure_wired()
    done, failed, title_map = [], [], {}
    pri_page = get_wiki_page(primary_path)
    if not pri_page:
        return {"success": False, "error": "主页面读取失败: %s" % primary_path}
    pri_title = (pri_page.get("frontmatter") or {}).get("title") or Path(primary_path).stem

    for p in member_paths:
        if p == primary_path:
            continue
        try:
            page = get_wiki_page(p)
            if not page:
                failed.append({"pair": [primary_path, p], "error": "页面读取失败"})
                continue
            oth_fm = page.get("frontmatter") or {}
            if oth_fm.get("merged_into"):
                done.append({"primary": primary_path, "merged": p,
                             "mode": "skipped-stub"})  # 幂等：已并过跳过
                continue
            oth_title = oth_fm.get("title") or Path(p).stem
            r = merge_pair(primary_path, p, dry_run=dry_run, use_llm=False)
            if r.get("success"):
                done.append({"primary": primary_path, "merged": p,
                             "mode": r.get("mode")})
                if oth_title != pri_title:
                    title_map[oth_title] = pri_title
            else:
                failed.append({"pair": [primary_path, p], "error": r.get("error")})
        except Exception as e:
            failed.append({"pair": [primary_path, p], "error": str(e)})

    refs_result = {"pages_changed": 0}
    aliases_added = 0
    if title_map and not dry_run:
        refs_result = rewrite_references(title_map)
        aliases_added = _register_name_aliases(pri_title, list(title_map.keys()))

    return {
        "success": True,
        "primary": primary_path,
        "members": len([p for p in member_paths if p != primary_path]),
        "merged": len(done),
        "failed": len(failed),
        "refs_rewritten": refs_result.get("pages_changed", 0),
        "aliases_added": aliases_added,
        "title_map": title_map,
        "detail": done,
        "errors": failed,
        "dry_run": dry_run,
    }


# ---------------------------------------------------------------------------
# 自检（零 LLM、零写入）
# ---------------------------------------------------------------------------


def _self_check() -> bool:
    ok = True
    print("=" * 50)
    print("◐ kb_merger 自检")
    print("=" * 50)

    # 1) 边合并：并集去重 + 剔除互指
    r = merge_related(["A", "B"], ["B", "C", "主标题", "被并标题"], "主标题", "被并标题")
    if r == ["A", "B", "C"]:
        print("✓ related 合并：并集去重，互指/自指剔除")
    else:
        print("✗ related 合并结果异常: %s" % r); ok = False

    # 2) 选主：正文长者胜
    fake = {
        "a.md": {"frontmatter": {"title": "短", "updated_at": "2026-08-15T00:00:00Z"}, "body": "x" * 10},
        "b.md": {"frontmatter": {"title": "长", "updated_at": "2026-08-01T00:00:00Z"}, "body": "x" * 100},
    }
    if pick_primary(["a.md", "b.md"], lambda p: fake.get(p)) == "b.md":
        print("✓ 选主：正文长度优先")
    else:
        print("✗ 选主逻辑异常"); ok = False

    # 3) stub 正文生成
    s = build_stub_body("旧概念", "新概念", "wiki/concepts/x.md")
    if "已合并" in s and "wiki/concepts/x.md" in s:
        print("✓ 重定向 stub 生成")
    else:
        print("✗ stub 生成异常"); ok = False

    # 4) 降级合并正文
    fb = _fallback_body("主体", "补充内容", "被并页")
    if "主体" in fb and "合并自「被并页」" in fb and "补充内容" in fb:
        print("✓ LLM 失败降级路径：正文附录并置")
    else:
        print("✗ 降级正文异常"); ok = False

    # 5) v6.10.52：arxiv id 文件名解析（双世代识别核心）
    cases = [
        ("1006.1827", "1006.1827"),
        ("1006.1827v2", "1006.1827"),
        ("2010-1006_1827-attosecond-streaking-enables", "1006.1827"),
        ("2025-s41566-025-01700-6-attosecond-virtual", ""),  # doi 源无 arxiv id
        ("RABBITT", ""),
    ]
    for stem, want in cases:
        got = extract_arxiv_id(stem)
        if got != want:
            print("✗ arxiv id 解析异常: %s → %s（期望 %s）" % (stem, got, want)); ok = False
    if ok:
        print("✓ arxiv id 文件名解析：裸 id / slug 代 / doi 排除")

    # 6) v6.10.52：注入式分组检测（零 IO）
    fake_pages = [
        {"path": "wiki/papers/1006.1827.md", "merged_into": ""},
        {"path": "wiki/papers/2010-1006_1827-attosecond-x.md", "merged_into": ""},
        {"path": "wiki/papers/1905.10109.md", "merged_into": ""},
        {"path": "wiki/papers/2020-1905_10109-properties-of-bsv.md", "merged_into": ""},
        {"path": "wiki/papers/old.md", "merged_into": "wiki/papers/other.md"},  # stub 跳过
    ]
    groups = detect_paper_generation_groups(fake_pages)
    ids = sorted(g["arxiv_id"] for g in groups)
    if ids == ["1006.1827", "1905.10109"] and all(len(g["paths"]) == 2 for g in groups):
        print("✓ 双世代分组检测：按 id 聚组，stub 排除")
    else:
        print("✗ 双世代分组异常: %s" % ids); ok = False

    # 7) v7.3.77：近同名归一键（分隔符/括号限定词剥离，组合方法页不误并）
    if (normalize_method_name("磁点群/自旋群对称性分析")
            == normalize_method_name("磁点群自旋群对称性分析")
            and normalize_method_name("磁性空间群对称性分析（拓扑量子化学框架）")
            == normalize_method_name("磁性空间群对称性分析")
            and normalize_method_name("磁空间群对称性分析与线性自旋波建模")
            != normalize_method_name("磁空间群对称性分析")):
        print("✓ 近同名归一键：变体同键，MSG+LSWT 组合方法页不被误并")
    else:
        print("✗ 近同名归一键异常"); ok = False

    # 8) v7.3.77：归一键分组检测（stub 排除、单页不成组）
    fake_ns = [
        {"path": "wiki/methods/a.md", "title": "磁点群/自旋群对称性分析", "merged_into": ""},
        {"path": "wiki/methods/b.md", "title": "磁点群自旋群对称性分析", "merged_into": ""},
        {"path": "wiki/methods/c.md", "title": "自旋空间群对称性分析",
         "merged_into": "wiki/methods/b.md"},
        {"path": "wiki/methods/d.md", "title": "磁点群对称性选择定则分析", "merged_into": ""},
    ]
    gs = detect_method_name_groups(pages=fake_ns)
    if (len(gs) == 1
            and sorted(gs[0]["paths"]) == ["wiki/methods/a.md", "wiki/methods/b.md"]):
        print("✓ 归一键分组：变体聚组，stub 排除，单页不成组")
    else:
        print("✗ 归一键分组异常: %s" % gs); ok = False

    print("自检结果: %s" % ("通过" if ok else "失败"))
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description="重复 wiki 页合并执行器")
    ap.add_argument("--max-pairs", type=int, default=MAX_PAIRS_PER_WEEK, help="本次最多合并对数")
    ap.add_argument("--dry-run", action="store_true", help="预览不写入")
    ap.add_argument("--self-check", action="store_true", help="模块自检")
    ap.add_argument("--dedup-papers", action="store_true",
                    help="论文页双世代去重（确定性附录并置，零 LLM）")
    ap.add_argument("--dedup-methods", action="store_true",
                    help="按 title 归一键自动归并近同名页（零 LLM，强重复通道）")
    ap.add_argument("--namespace", default="methods",
                    help="归一键自动通道扫描的命名空间（默认 methods）")
    ap.add_argument("--families", metavar="JSON",
                    help='显式家族清单 {"primary": 路径, "members": [路径…]}，'
                         "策展成员零 LLM 归并（语义近邻通道）")
    ap.add_argument("--max-groups", type=int, default=None,
                    help="双世代去重本次最多处理组数")
    ap.add_argument("--rewrite-refs", metavar="MAPPING_JSON",
                    help="按 {旧title: 新title} JSON 文件全库改写引用")
    args = ap.parse_args()

    if args.self_check:
        sys.exit(0 if _self_check() else 1)
    if args.dedup_papers:
        result = merge_paper_generations(
            dry_run=args.dry_run, max_groups=args.max_groups)
        if not args.dry_run:
            # 审计留痕：完整明细落盘（CLI 摘要截断 20 对，修复对账以此为准）
            import json
            log_path = _MERGE_LOG_DIR / ("dedup-papers-%s.json" % now_utc()[:10])
            _MERGE_LOG_DIR.mkdir(parents=True, exist_ok=True)
            slim = dict(result)
            slim.pop("title_map", None)
            log_path.write_text(
                json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
            print("明细留痕: %s" % log_path)
        print("双世代重复组: %d" % result["groups_detected"])
        print("本次合并: %d 对，失败 %d 对，引用改写 %d 页%s"
              % (result["merged"], result["failed"], result["refs_rewritten"],
                 "（dry-run）" if args.dry_run else ""))
        for d in result["detail"][:20]:
            print("  ✓ %s ← %s [%s]" % (d["primary"], d["merged"], d["mode"]))
        if len(result["detail"]) > 20:
            print("  … 其余 %d 对省略" % (len(result["detail"]) - 20))
        for e in result["errors"][:10]:
            print("  ✗ %s | %s" % (e["pair"], e["error"]))
        return
    if args.dedup_methods or args.families:
        import json
        results = []
        if args.families:
            fam = json.loads(Path(args.families).read_text(encoding="utf-8"))
            results.append(merge_name_family(
                fam["primary"], fam["members"], dry_run=args.dry_run))
        else:
            from kb_wiki import get_wiki_page
            for g in detect_method_name_groups(args.namespace):
                primary = pick_primary(g["paths"], get_wiki_page)
                results.append(merge_name_family(
                    primary, [p for p in g["paths"] if p != primary],
                    dry_run=args.dry_run))
        if not args.dry_run and results:
            log_path = _MERGE_LOG_DIR / ("dedup-methods-%s.json" % now_utc()[:10])
            _MERGE_LOG_DIR.mkdir(parents=True, exist_ok=True)
            slim = [{k: v for k, v in r.items() if k != "title_map"} for r in results]
            log_path.write_text(
                json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
            print("明细留痕: %s" % log_path)
        for r in results:
            skipped = sum(1 for d in r.get("detail", []) if d.get("mode") == "skipped-stub")
            print("%s 主页 %s | 成员 %d | 本次处理 %d（其中 stub 跳过 %d）失败 %d | "
                  "引用改写 %d 页 | aliases +%d%s"
                  % ("◐" if r.get("dry_run") else "✓", r.get("primary"),
                     r.get("members", 0), r.get("merged", 0), skipped,
                     r.get("failed", 0), r.get("refs_rewritten", 0),
                     r.get("aliases_added", 0),
                     "（dry-run）" if r.get("dry_run") else ""))
            for d in r.get("detail", []):
                print("  · %s ← %s [%s]" % (d["primary"], d["merged"], d.get("mode")))
            for e in r.get("errors", []):
                print("  ✗ %s | %s" % (e["pair"], e["error"]))
        if not results:
            print("○ 归一键自动通道：无近同名重复组")
        return
    if args.rewrite_refs:
        import json
        mapping = json.loads(Path(args.rewrite_refs).read_text(encoding="utf-8"))
        result = rewrite_references(mapping, dry_run=args.dry_run)
        print("引用改写: %d 页，%d 处命中%s"
              % (result["pages_changed"], result["hits"],
                 "（dry-run）" if args.dry_run else ""))
        return
    result = run_merge(max_pairs=args.max_pairs, dry_run=args.dry_run)
    print("检出重复组: %d" % result["groups_detected"])
    print("本次合并: %d 对%s" % (result["merged"], "（dry-run）" if args.dry_run else ""))
    for d in result["detail"]:
        print("  ✓ %s ← %s [%s]" % (d["primary"], d["merged"], d["mode"]))
    for e in result["errors"]:
        print("  ✗ %s | %s" % (e["pair"], e["error"]))


if __name__ == "__main__":
    main()
