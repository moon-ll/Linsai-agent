#!/usr/bin/env python3
"""kb_distill — raw→wiki 批量蒸馏器（v6.9.5）。

背景（2026-08-15 排查结论）：
    health_sensor 持续告警"待蒸馏 raw 积压 508 项"（阈值 300）。
    根因不是任务失败，而是 `distill_raw_to_wiki()` / `save_distilled_wiki()`
    接口自 v3.x 就存在，但**没有任何流水线生产者调用它们**——周末输出端
    做的是归档课题萃取与每日知识萃取，均不覆盖 raw→wiki 蒸馏。接口在、
    编排无，导致 raw/papers 360 篇论文长期零消化。

本模块补上这一环：
    1. 计算 pending 清单（已索引 raw 中无 wiki source_raw 关联者）
    2. 按文件修改时间 FIFO 取最旧 N 篇（--batch，默认 5）
    3. 每篇：生成蒸馏 prompt → llm_gateway（执行类默认链，MiniMax 主，
       额度期自动降级）→ 后处理注入 source_raw frontmatter →
       save_distilled_wiki（门面写入，自动更新图谱/生长日志/索引）
    4. 单篇失败跳过不中断批次；批次结束输出汇总

关键约束：
    - 蒸馏产物必须带 `source_raw` frontmatter——这是 pending_distill
      的判定依据（kb_health.py），缺了它蒸馏了也不减计数。
    - 写入统一走 knowledge_base 门面（v6.8.51 防双 frontmatter 规范）。

用法示例：
    python3 scripts/kb_distill.py --dry-run        # 预览将蒸馏的清单
    python3 scripts/kb_distill.py --batch 5        # 蒸馏最旧 5 篇
    python3 scripts/kb_distill.py --self-check     # 模块自检（零 LLM 调用）

cron 接入（见 setup 提示）：
    每日 12:50（lc-kb-sync 之后）跑一批 5 篇，508 项约 100 天消化；
    蒸馏副产物（wikilinks 注入）同步改善图谱连通性 0.45→阈值上方。
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc  # noqa: E402
from knowledge_base import (  # noqa: E402
    KNOWLEDGE_DIR,
    distill_raw_to_wiki,
    save_distilled_wiki,
)

DEFAULT_BATCH = 5
MAX_OUTPUT_CHARS = 6000          # 防失控输出
SOURCE_RAW_KEY = "source_raw"    # pending_distill 判定字段
# 排除目录（相对 KNOWLEDGE_DIR 的 posix 前缀）：
#   raw/pdfs/_text_cache/ 是 PDF 抽取中间缓存（纯数字命名、无语义），
#   蒸馏它们只会产出无意义 wiki 页；kb_health 计数包含它们属上游口径
#   宽松，此处主动排除，避免污染知识库。
EXCLUDE_PREFIXES = ("raw/pdfs/_text_cache/",)


def _is_excluded(rel_path: str) -> bool:
    return any(rel_path.startswith(p) for p in EXCLUDE_PREFIXES)


# ─────────────────────────────────────────────
# 清单计算
# ─────────────────────────────────────────────

def _wiki_source_raws() -> set:
    """收集现有 wiki 已占用的 source_raw 集合（纯文件名口径）。"""
    from knowledge_base import list_wiki_pages, get_wiki_page
    used = set()
    for pg in list_wiki_pages():
        fm = get_wiki_page(pg.get("path", "")) or {}
        src = (fm.get("frontmatter") or {}).get(SOURCE_RAW_KEY, "")
        if src:
            # 兼容历史数据：source_raw 可能带 raw/papers/ 前缀，统一取纯文件名
            used.add(Path(src).name)
    return used


def pending_distill_list(limit: Optional[int] = None) -> List[Path]:
    """返回待蒸馏 raw 清单（按最旧优先）。

    口径与 kb_health.get_kb_health 的 pending_distill / health_sensor
    告警完全同源：kb_index.list_raw_files() 的 name（纯文件名）对
    wiki frontmatter 的 source_raw（纯文件名）。

    Args:
        limit: 最多返回条数；None 返回全量。

    Returns:
        raw 文件绝对路径列表。
    """
    from kb_index import list_raw_files
    used = _wiki_source_raws()
    files = [
        (f["mtime"], KNOWLEDGE_DIR / f["path"])
        for f in list_raw_files()
        if Path(f["name"]).name not in used and not _is_excluded(f["path"])
    ]
    files.sort(key=lambda t: t[0])  # 最旧优先
    out = [p for _, p in files]
    return out[:limit] if limit is not None else out


# ─────────────────────────────────────────────
# 蒸馏执行
# ─────────────────────────────────────────────

def _ensure_source_raw(llm_output: str, raw_rel: str, wiki_type: str,
                       wiki_name: str) -> str:
    """确保输出含 frontmatter 且带 source_raw（不减计数的关键）。

    - 无 frontmatter → 构造最小合规头（title/type/created/growth_stage）
    - 有 frontmatter → 仅在缺 source_raw 时补写，不覆盖已有字段
    """
    # v6.9.7: created 必须取真实当前时间——此前硬编码 "2026-08-15T00:00:00Z"，
    # 而蒸馏系统提示要求 LLM 只输出正文（构造头部是主路径），导致 lc-kb-distill
    # 每日新蒸馏页的 created 全部冻结在同一天，污染 KB 新鲜度指标与
    # growth_engine 晋升时序判断。
    now = now_utc()
    if llm_output.lstrip().startswith("---"):
        if re.search(rf"^{SOURCE_RAW_KEY}\s*:", llm_output, re.M):
            return llm_output
        # 在 frontmatter 结束线前插入
        return re.sub(r"\n---\n", f"\n{SOURCE_RAW_KEY}: \"{raw_rel}\"\n---\n",
                      llm_output, count=1)
    fm = (f"---\ntitle: \"{wiki_name}\"\ntype: {wiki_type}\n"
          f"created: {now}\ngrowth_stage: seedling\n"
          f"{SOURCE_RAW_KEY}: \"{raw_rel}\"\n---\n\n")
    return fm + llm_output


def distill_one(raw_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """蒸馏单篇 raw → wiki。

    Returns:
        {success, raw, wiki, skipped?, error?}
    """
    raw_rel = raw_path.relative_to(KNOWLEDGE_DIR).as_posix()
    prepped = distill_raw_to_wiki(raw_rel)
    if not prepped:
        return {"success": False, "raw": raw_rel, "error": "prompt 生成失败"}
    wiki_rel, prompt = prepped
    if dry_run:
        return {"success": True, "raw": raw_rel, "wiki": wiki_rel, "skipped": True}

    from llm_gateway import llm_complete
    # v6.9.15: prefer="kb_distill" → GLM 主模型直连（默认 MiniMax 主链
    # 429 限额期单篇重试+降级最长 369s，350 篇积压不可行）。
    ok, text, meta = llm_complete(
        "你是知识库蒸馏器。按用户指令把原始文献提炼为 wiki 页面，"
        "直接输出 Markdown 正文（frontmatter 由系统补写），不要输出解释。",
        prompt, timeout=150, prefer="kb_distill",
    )
    if not ok or not text or not text.strip():
        return {"success": False, "raw": raw_rel,
                "error": f"LLM 失败: {str(meta.get('error', ''))[:60]}"}
    if len(text) > MAX_OUTPUT_CHARS:
        text = text[:MAX_OUTPUT_CHARS] + "\n\n... [蒸馏输出超长截断]"

    wiki_type = wiki_rel.split("/")[1] if "/" in wiki_rel else "concepts"
    # source_raw 必须是纯文件名——kb_health 以 name 对 name 匹配判定
    # pending_distill，带 raw/ 前缀会导致蒸馏后计数不减。
    final = _ensure_source_raw(text, raw_path.name, wiki_type,
                               Path(wiki_rel).stem)
    save_distilled_wiki(wiki_rel, final, raw_rel)
    return {"success": True, "raw": raw_rel, "wiki": wiki_rel}


def run_batch(batch: int = DEFAULT_BATCH, dry_run: bool = False) -> Dict[str, Any]:
    """执行一批蒸馏。

    Args:
        batch: 本批篇数上限。
        dry_run: 仅预览不调用 LLM。

    Returns:
        {total_pending, attempted, ok, failed, results}
    """
    pending = pending_distill_list()
    todo = pending[:batch]
    results = []
    for f in todo:
        try:
            results.append(distill_one(f, dry_run=dry_run))
        except Exception as exc:  # 单篇失败不中断批次
            results.append({"success": False,
                            "raw": f.relative_to(KNOWLEDGE_DIR).as_posix(),
                            "error": f"{type(exc).__name__}: {str(exc)[:60]}"})
    ok = sum(1 for r in results if r.get("success"))
    return {"total_pending": len(pending), "attempted": len(results),
            "ok": ok, "failed": len(results) - ok, "results": results}


# ─────────────────────────────────────────────
# CLI / 自检
# ─────────────────────────────────────────────

def _self_check() -> bool:
    """模块自检：清单计算 + frontmatter 注入逻辑（零 LLM、零写入）。"""
    ok = True
    # 1) 清单类型与排序
    lst = pending_distill_list(limit=3)
    if not isinstance(lst, list):
        print("✗ pending_distill_list 返回类型错误")
        ok = False
    else:
        print(f"✓ pending 清单（抽样 {len(lst)} 条，类型正确）")

    # 2) frontmatter 注入：无头 → 构造
    no_fm = _ensure_source_raw("正文内容", "x.md", "papers", "x")
    if no_fm.startswith("---") and 'source_raw: "x.md"' in no_fm:
        print("✓ 无 frontmatter → 构造含 source_raw（纯文件名）")
    else:
        print("✗ 无 frontmatter 构造失败"); ok = False

    # 3) frontmatter 注入：有头缺字段 → 补写
    has_fm = "---\ntitle: y\ntype: papers\n---\n\n正文"
    fixed = _ensure_source_raw(has_fm, "y.md", "papers", "y")
    if 'source_raw: "y.md"' in fixed and fixed.count("---") == 2:
        print("✓ 有 frontmatter 缺字段 → 补写 source_raw（纯文件名）")
    else:
        print("✗ 补写失败"); ok = False

    # 4) 已有字段 → 不覆盖
    keep = "---\nsource_raw: \"z.md\"\ntype: papers\n---\n\n正文"
    kept = _ensure_source_raw(keep, "other.md", "papers", "z")
    if 'z.md' in kept and 'other.md' not in kept:
        print("✓ 已有 source_raw → 不覆盖")
    else:
        print("✗ 覆盖了已有字段"); ok = False

    # 5) created 时间戳非冻结（v6.9.7 回归：与当前时间差 < 24h）
    import re as _re
    from datetime import datetime, timezone, timedelta
    fresh = _ensure_source_raw("正文内容", "x.md", "papers", "x")
    m = _re.search(r'^created:\s*"?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"?', fresh, _re.M)
    if m:
        try:
            ts = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - ts
            if abs(age) < timedelta(hours=24):
                print("✓ 构造头 created 取真实当前时间（非冻结）")
            else:
                print(f"✗ created 冻结在 {m.group(1)}"); ok = False
        except ValueError:
            print(f"✗ created 格式不可解析: {m.group(1)}"); ok = False
    else:
        print("✗ 构造头缺失 created 字段"); ok = False

    print("自检结果:", "✓ 通过" if ok else "✗ 失败")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="raw→wiki 批量蒸馏器")
    ap.add_argument("--batch", type=int, default=DEFAULT_BATCH,
                    help=f"本批蒸馏篇数（默认 {DEFAULT_BATCH}）")
    ap.add_argument("--dry-run", action="store_true", help="仅预览不调用 LLM")
    ap.add_argument("--self-check", action="store_true", help="模块自检")
    args = ap.parse_args()

    if args.self_check:
        return 0 if _self_check() else 1

    r = run_batch(batch=args.batch, dry_run=args.dry_run)
    print(f"待蒸馏总量: {r['total_pending']}（阈值 300）")
    print(f"本批: {r['attempted']} 篇，✓ {r['ok']}，✗ {r['failed']}")
    for item in r["results"]:
        mark = "○ 预览" if item.get("skipped") else ("✓" if item["success"] else "✗")
        extra = f" → {item.get('wiki', '')}" if item.get("wiki") else \
                f" | {str(item.get('error', ''))[:70]}"
        print(f"  {mark} {item['raw']}{extra}")
    return 0 if (r["failed"] == 0 or args.dry_run) else 1


if __name__ == "__main__":
    sys.exit(main())
