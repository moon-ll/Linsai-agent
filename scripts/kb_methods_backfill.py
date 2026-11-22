#!/usr/bin/env python3
"""存量论文页方法卡回补（v7.0.6 批次一·方法学升级主体）。

背景：v7.0.5 起新蒸馏带方法卡（literature-reading 五节），但 ~2100 篇
存量 papers 页是旧格式——方案写作缺可实施细节的根因。

**零 LLM 设计（v7.0.7 用户裁决）**：方法卡提取由 ZCode 自动化任务
执行（ZCode 会话即模型，直接读页面写方法卡），本脚本不调用项目的
llm_gateway/hermes LLM 链。职责分工：
    - 本脚本（零 LLM）：扫描分级 / 工作清单发射 / 方法卡落盘工具 /
      台账断点管理；
    - ZCode 自动化任务（闲时/定时）：消费 --worklist 清单，逐页提取
      方法卡，经 _append_method_card 写入并更新台账（库调用，零 LLM）。

扫描分级（零 LLM）：
    A 级：页内已有方法内容（装置/参数/序列等特征命中）→ 页内重排；
    B 级：页薄但来源 raw 有 has_fulltext 全文 → 回原文提取；
    C 级：无全文且页薄 → 跳过（留待未来深读）。
优先集：活跃课题 00 号设想的方法关键词命中的 KB 检索 top-N 页。

用法：
    python3 scripts/kb_methods_backfill.py --scan            # 分级扫描
    python3 scripts/kb_methods_backfill.py --worklist 60     # 发射待处理清单
    python3 scripts/kb_methods_backfill.py --status          # 台账进度
    python3 scripts/kb_methods_backfill.py --self-check

ZCode 任务消费方式（库调用，不经过 LLM 网关）：
    from kb_methods_backfill import _append_method_card, _load_state, _save_state, PAPERS_DIR
    card = {"method_name": ..., "principle": ..., "params": [...],
            "boundary": ..., "representative": ...}   # ZCode 读页后自行撰写
    _append_method_card(PAPERS_DIR / f"{page}.md", card)
    st = _load_state(); st["pages"][page] = {"status": "ok", "grade": "A", "at": ...}; _save_state(st)

规范：仅标准库；JSON ensure_ascii=False, indent=2。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import file_lock, load_json, now_utc, save_json
from paths import PROJECT_ROOT

try:
    from logger import get_logger
    _log = get_logger("kb_methods_backfill")
except Exception:
    _log = None

PAPERS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "papers"
RAW_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"
CACHE_DIR = PROJECT_ROOT / "knowledge" / "raw" / "pdfs" / "_text_cache"
STATE_PATH = PROJECT_ROOT / "memory" / "methods-backfill-state.json"
WORKLIST_PATH = PROJECT_ROOT / "memory" / "methods-backfill-worklist.json"
LIFECYCLE_PATH = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"

METHOD_CARD_HEADING = "## 研究方法（方法卡）"
BACKFILL_MARKER = "<!-- methods-backfill:v1 -->"

# 台账终态（不再进入工作清单）
_TERMINAL = ("ok", "no_method", "failed_final")


def _skip_by_ledger(rec: dict, has_method_section: bool = False) -> bool:
    """台账终态跳过判定（v7.2.16 状态漂移修复）。

    no_method 语义是"ZCode 判定该页无方法素材"——但页面内容会随蒸馏/
    深读更新增长：若现在页内已出现方法节（has_method_section=True），
    素材已到位，no_method 属状态漂移，应重新入选（v7.0.7 tagged 卡死
    缺陷的 no_method 变体）。
    """
    status = rec.get("status")
    if status in ("ok", "failed_final"):
        return True
    if status == "no_method":
        return not has_method_section
    return False

# 页内方法内容特征（A 级判定；命中 ≥2 视为有方法内容）
_METHOD_FEATURES = (
    "参数表", "装置", "测量序列", "光路", "脉冲", "积分时间", "扫描",
    "分辨率", "波段", "中心波长", "重复频率", "脉宽", "温控", "真空",
    "计算设置", "k 网格", "泛函", "网格", "截断能", "赝势", "超胞",
    "样品制备", "解理", "生长", "掺杂浓度", "实验步骤", "采集",
)


# ---------------------------------------------------------------------------
# 课题关键词 → 优先集
# ---------------------------------------------------------------------------

def _proposal_method_keywords() -> List[str]:
    """从活跃课题 00 号设想提取方法关键词（启发式，零 LLM）。"""
    kws = set()
    try:
        lc = load_json(LIFECYCLE_PATH, default={})
        for pid, st in (lc.get("proposals") or {}).items():
            if st.get("status") not in ("optimizing", "pending_review", "drafts"):
                continue
            prop_dir = PROJECT_ROOT / "research_proposals" / st.get("status", "optimizing") / pid
            for f in sorted(prop_dir.glob("00_*.md")):
                text = f.read_text(encoding="utf-8")[:3000]
                kws.update(re.findall(r"\b(?:HHG|TDDFT|SBE|TDSE|FROG|RABBITT|VMI|COLTRIMS|MOCVD|CVD|MBE|DFT|THz|XUV|OAM|SHG)\b", text))
                for w in re.findall(r"[一-龥]{2,6}(?:光谱|谱学|测量|探测|计算|模拟|沉积|外延|解理|泵浦|探测|调控)", text):
                    kws.add(w)
                break
    except Exception as e:
        if _log:
            _log.warning(f"课题关键词提取失败: {e}")
    return sorted(kws)


def _priority_pages(top_n: int = 120) -> set:
    """课题相关优先集：KB 检索命中课题关键词的 papers 页。"""
    prio: set = set()
    try:
        import knowledge_base as kb
    except Exception:
        return prio
    for kw in _proposal_method_keywords():
        try:
            rs = kb.search(kw, top_k=8, source="wiki")["results"]
            for r in rs:
                doc = r.get("doc", "")
                if doc.startswith("wiki/papers/"):
                    prio.add(doc[len("wiki/papers/"):-3] if doc.endswith(".md") else doc)
        except Exception:
            continue
    return prio


# ---------------------------------------------------------------------------
# 扫描分级
# ---------------------------------------------------------------------------

def _page_has_methods(text: str) -> bool:
    hits = sum(1 for f in _METHOD_FEATURES if f in text)
    return hits >= 2


def _has_method_card(text: str) -> bool:
    """已回补判定：方法卡小节与标记**同时**存在（v7.0.7 修正——旧口径
    只查标记，早期"溢出打标"的 66 页有标记无卡片，被误判 done 卡死）。"""
    return METHOD_CARD_HEADING in text and BACKFILL_MARKER in text


def _raw_stem_for(page_stem: str) -> Optional[Path]:
    """页 stem → raw 源文件。"""
    candidates = []
    m = re.match(r"^(\d{4})-(\d{4})_(\d{4,5})-(.*)", page_stem)
    if m:
        y, p1, p2, rest = m.groups()
        candidates.append(RAW_DIR / f"{y}-{p1}.{p2}-{rest}.md")
    if not candidates:
        candidates.append(RAW_DIR / f"{page_stem}.md")
    for c in candidates:
        if c.exists():
            return c
    return None


def _fulltext_for(raw_path: Optional[Path]) -> Optional[Path]:
    """raw md 的 has_fulltext 标记 → _text_cache 全文路径。"""
    if raw_path is None:
        return None
    try:
        head = raw_path.read_text(encoding="utf-8")[:1200]
        if not re.search(r"has_fulltext:\s*true", head):
            return None
        arxiv_like = re.search(r"(\d{4}\.\d{4,5})", raw_path.name)
        if arxiv_like:
            aid = arxiv_like.group(1)
            for cand in CACHE_DIR.glob(f"*{aid}*"):
                if cand.is_file():
                    return cand
    except Exception:
        pass
    return None


def scan_pages(limit: int = 0, only_priority: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    """全量扫描分级：{grade: [{page, reason, bytes, has_fulltext, has_method_section, raw_stem}]}。

    v7.1.0 扩展（用户裁决 2026-09-27）：每条目标加 has_method_section /
    has_fulltext_path / raw_stem 三字段，供 ZCode 任务分派策略（页内重排
    vs 全文重读）；has_method_section=True 用页内素材，False 需拉全文。
    """
    prio = _priority_pages() if only_priority else set()
    grades: Dict[str, List[Dict[str, Any]]] = {"A": [], "B": [], "C": [], "done": []}
    pages = sorted(PAPERS_DIR.glob("*.md"))
    if prio:
        pages.sort(key=lambda p: (0 if p.stem in prio else 1, p.stem))
    for f in pages:
        if limit and sum(len(v) for v in grades.values()) >= limit:
            break
        if only_priority and prio and f.stem not in prio:
            break  # 优先集已排序耗尽
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if _has_method_card(text):
            grades["done"].append({"page": f.stem})
            continue
        size = len(text)
        has_methods = _page_has_methods(text)
        raw = _raw_stem_for(f.stem)
        fulltext = _fulltext_for(raw)
        raw_stem = raw.stem if raw else ""
        if has_methods:
            grades["A"].append({
                "page": f.stem, "bytes": size,
                "fulltext": bool(fulltext),
                "fulltext_path": str(fulltext.relative_to(PROJECT_ROOT)) if fulltext else "",
                "has_method_section": True,
                "raw_stem": raw_stem,
            })
        elif fulltext is not None:
            grades["B"].append({
                "page": f.stem, "bytes": size,
                "fulltext": str(fulltext.relative_to(PROJECT_ROOT)),
                "has_method_section": False,
                "raw_stem": raw_stem,
            })
        else:
            grades["C"].append({
                "page": f.stem, "bytes": size,
                "has_method_section": False,
                "raw_stem": raw_stem,
            })
    return grades


# ---------------------------------------------------------------------------
# 方法卡落盘工具（ZCode 任务库调用）
# ---------------------------------------------------------------------------

def _format_method_card(card: Dict[str, Any]) -> str:
    """格式化方法卡（v7.0.5 四要素 + v7.1.3 林赛理解节）。

    要素：
    - 方法名 / 原理 / 参数表 / 适用边界 / 代表作（v7.0.5 五要素素材链）
    - 林赛理解（v7.1.3 用户裁决 2026-09-27 增）—— 与 concept 页的"林赛理解"对齐，
      让方法页不只罗列参数，也承载方法学认知（如"我最早把X当Y理解，但
      A 论文纠正了 Z 假设"）。理解节是"经过验证的知识积累"的核心区分点。
    """
    params = card.get("params") or []
    lines = [
        "",
        METHOD_CARD_HEADING,
        BACKFILL_MARKER,
        f"**方法**：{card.get('method_name', '')}",
        "",
        f"**原理**：{card.get('principle', '')}",
        "",
    ]
    # v7.1.3：林赛理解节（方法学素材链的"经过验证"层）
    understanding = card.get("understanding", "")
    if understanding:
        lines.append("**林赛理解**：")
        lines.append("")
        lines.append(understanding)
        lines.append("")
    if params:
        lines.append("**参数表**：")
        lines.append("")
        lines.append("| 参数 | 数值 | 出处 |")
        lines.append("| --- | --- | --- |")
        for p in params[:20]:
            lines.append(f"| {p.get('item', '')} | {p.get('value', '')} | {p.get('source', '')} |")
        lines.append("")
    if card.get("boundary"):
        lines.append(f"**适用边界**：{card['boundary']}")
    if card.get("representative"):
        lines.append(f"**代表作**：{card['representative']}")
    lines.append(f"*方法卡回补 {now_utc()[:10]}*")
    return "\n".join(lines) + "\n"


def _append_method_card(page_path: Path, card: Dict[str, Any]) -> None:
    """蒸馏页追加方法卡小节（不动既有正文；重跑先移除旧卡保持幂等）。

    v7.1.2 防御（用户裁决 2026-09-27）：旧版仅按 METHOD_CARD_HEADING + BACKFILL_MARKER
    完整对匹配移除，导致仅有 marker（无标题）的空壳卡残留污染论文页——v7.0.6
    上线期间 8 张 28B 空壳即此原因（v7.1.1 已批量清理）。v7.1.2 进一步把正则
    放宽到"前面任意 ## 标题前"，覆盖 marker 前是 "## 来源"/"## 关联概念"
    等其他二级标题的情形。
    """
    text = page_path.read_text(encoding="utf-8")
    if BACKFILL_MARKER in text:
        # 模式 1：完整卡节（METHOD_CARD_HEADING + BACKFILL_MARKER）
        text = re.sub(
            rf"\n?{re.escape(METHOD_CARD_HEADING)}\n{re.escape(BACKFILL_MARKER)}.*?(?=\n## |\Z)",
            "", text, flags=re.S)
        # 模式 2：孤 marker（无标题行，marker 前是任意二级标题）—v7.0.6/v7.0.7 残留
        text = re.sub(
            rf"\n{re.escape(BACKFILL_MARKER)}\s*(?=\n<|\n## |\Z)",
            "", text, flags=re.S)
    text = text.rstrip("\n") + "\n" + _format_method_card(card)
    page_path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# 台账 + 工作清单
# ---------------------------------------------------------------------------

def _load_state() -> Dict[str, Any]:
    st = load_json(STATE_PATH, default={"pages": {}, "updated_at": ""})
    st.setdefault("pages", {})
    return st


def _save_state(st: Dict[str, Any]) -> None:
    st["updated_at"] = now_utc()
    with file_lock("kb-methods-backfill"):
        save_json(STATE_PATH, st)


def emit_worklist(batch: int, only_priority: bool = True,
                  extra_pages: Optional[List[str]] = None) -> Dict[str, Any]:
    """发射待处理工作清单（零 LLM，供 ZCode 自动化任务消费）。

    目标 = 台账非终态页 ∪ 扫描新发现页（含历史"溢出打标"卡死页——
    v7.0.7 修正后标记页无卡片会重新入选）。

    v7.1.0 扩展（用户裁决 2026-09-27）：
        - 接受 extra_pages（每日深读 / kb_distill 蒸馏出口追加的 paper stem
          列表），按"高优先 B 级（fulltext 可用）"前置到清单头部，确保新蒸馏
          论文立即被 ZCode 写方法卡
        - 每条目标加 priority_hint 字段：'inline' = 页内重排（has_method_section
          已存在）/ 'fulltext' = 需读全文 / 'inline-and-merge' = 已有方法节 +
          有全文，两者交叉验证
        - 加 source 字段：'priority' / 'daily' / 'distill' / 'state-pending'，
          供 ZCode 任务按来源区分优先级
    """
    st = _load_state()
    grades = scan_pages(only_priority=only_priority)
    targets: List[Dict[str, Any]] = []
    seen = set()

    # 1) 每日/蒸馏追加：先于扫描目标，强制进入清单（即使已 done 也再触发一次）
    extra_set = set(extra_pages or [])
    for page in extra_set:
        # 查找 page 的 grade 元数据
        meta = None
        for g in grades.values():
            for item in g:
                if item["page"] == page:
                    meta = item
                    break
            if meta:
                break
        if not meta:
            # 该页不在扫描结果里（已 done 或未匹配），仍追加占位
            meta = {"page": page, "grade": "B", "fulltext": False,
                    "fulltext_path": "", "has_method_section": False, "raw_stem": ""}
        seen.add(page)
        targets.append({
            "page": page,
            "grade": meta["grade"],
            "fulltext": meta.get("fulltext", False),
            "fulltext_path": meta.get("fulltext_path", ""),
            "has_method_section": meta.get("has_method_section", False),
            "raw_stem": meta.get("raw_stem", ""),
            "priority_hint": "inline-and-merge" if (meta.get("has_method_section") and meta.get("fulltext")) else (
                "fulltext" if meta.get("fulltext") else "inline"
            ),
            "source": "daily" if extra_pages else "distill",
            "prior_status": st["pages"].get(page, {}).get("status", "new"),
        })

    # 2) 扫描 A/B 级
    for grade in ("A", "B"):
        for item in grades[grade]:
            page = item["page"]
            if page in seen:
                continue
            seen.add(page)
            if _skip_by_ledger(st["pages"].get(page, {}),
                                item.get("has_method_section", False)):
                continue
            targets.append({
                "page": page,
                "grade": grade,
                "fulltext": item.get("fulltext", False),
                "fulltext_path": item.get("fulltext_path", ""),
                "has_method_section": item.get("has_method_section", False),
                "raw_stem": item.get("raw_stem", ""),
                "priority_hint": "inline-and-merge" if (item.get("has_method_section") and item.get("fulltext")) else (
                    "fulltext" if item.get("fulltext") else "inline"
                ),
                "source": "priority" if only_priority else "all",
                "prior_status": st["pages"].get(page, {}).get("status", "new"),
            })
            if len(targets) >= batch:
                break
        if len(targets) >= batch:
            break

    # 3) 台账里挂着的 pending/failed（不在本次扫描目标里的）也带上
    for page, rec in st["pages"].items():
        if len(targets) >= batch:
            break
        if page in seen or rec.get("status") in _TERMINAL:
            continue
        targets.append({"page": page, "grade": rec.get("grade", "A"),
                        "fulltext": False, "fulltext_path": "",
                        "has_method_section": False, "raw_stem": "",
                        "priority_hint": "inline", "source": "state-pending",
                        "prior_status": rec.get("status")})

    save_json(WORKLIST_PATH, {"emitted_at": now_utc(), "count": len(targets),
                              "targets": targets})
    print(f"  ✓ 工作清单: {len(targets)} 页 → {WORKLIST_PATH.relative_to(PROJECT_ROOT)}")
    for t in targets[:6]:
        print(f"    [{t['grade']}|{t.get('priority_hint','?')}|{t.get('source','?')}] {t['page'][:55]}")
    if len(targets) > 6:
        print(f"    …共 {len(targets)} 页")
    return {"count": len(targets), "extra_added": len(extra_set)}


def append_to_worklist(extra_pages: List[str], source: str = "daily") -> Dict[str, Any]:
    """追加页面到现有 worklist（不覆盖、不重排）。

    入口：
        - 每日深读钩子（briefing cron 完成深读后调用）
        - kb_distill 蒸馏完成钩子（蒸馏落盘后调用）

    语义：保留已有 targets，按 source 打标追加到末尾（去重），下批 ZCode
    任务继续按出现顺序消费。追加不刷新 emitted_at（保留上次全量发射时间戳
    供下游区分）。
    """
    if not extra_pages:
        return {"count": 0, "appended": 0}
    existing = load_json(WORKLIST_PATH, default={
        "emitted_at": "", "count": 0, "targets": []})
    seen = {t["page"] for t in existing.get("targets", [])}
    # 查每页 grade 元数据
    grades = scan_pages(only_priority=False)
    flat = {item["page"]: {"grade": g, **item}
            for g, items in grades.items() for item in items}
    appended = 0
    for page in extra_pages:
        if page in seen:
            continue
        meta = flat.get(page, {})
        existing.setdefault("targets", []).append({
            "page": page,
            "grade": meta.get("grade", "B"),
            "fulltext": meta.get("fulltext", False),
            "fulltext_path": meta.get("fulltext_path", ""),
            "has_method_section": meta.get("has_method_section", False),
            "raw_stem": meta.get("raw_stem", ""),
            "priority_hint": "inline-and-merge" if (meta.get("has_method_section") and meta.get("fulltext")) else (
                "fulltext" if meta.get("fulltext") else "inline"
            ),
            "source": source,
            "prior_status": "appended",
        })
        appended += 1
        seen.add(page)
    existing["count"] = len(existing.get("targets", []))
    save_json(WORKLIST_PATH, existing)
    print(f"  ✓ 追加 {appended} 页（source={source}）→ 总计 {existing['count']} 页")
    return {"count": existing["count"], "appended": appended}


def show_status() -> None:
    st = _load_state()
    from collections import Counter
    c = Counter(v.get("status") for v in st["pages"].values())
    total_pages = len(list(PAPERS_DIR.glob("*.md")))
    print(f"台账页面: {len(st['pages'])} / papers 总量 {total_pages}")
    print(f"状态分布: {dict(c)}")
    print(f"更新时间: {st.get('updated_at', '')}")


def _self_check() -> int:
    failures = []
    # 1) 方法卡格式往返
    card = {"method_name": "自旋分辨HHG", "principle": "测椭圆率。",
            "params": [{"item": "脉宽", "value": "30 fs", "source": "原文"}],
            "boundary": "需偏振分析器消光比>1e4", "representative": "某等 2024"}
    block = _format_method_card(card)
    if METHOD_CARD_HEADING not in block or "| 脉宽 | 30 fs |" not in block:
        failures.append("方法卡格式化异常")
    # 2) A 级判定口径
    if _page_has_methods("没有任何方法相关内容的短文本"):
        failures.append("A 级误判：无方法内容命中")
    if not _page_has_methods("样品制备采用机械解理，测量序列覆盖 40 个温度点，脉宽 30 fs"):
        failures.append("A 级漏判：特征命中不足")
    # 3) 已回补判定必须同时含小节与标记（防溢出打标卡死复发）
    if _has_method_card(f"正文\n{BACKFILL_MARKER}\n"):
        failures.append("done 误判：仅有标记无方法卡小节")
    if not _has_method_card(f"正文\n{METHOD_CARD_HEADING}\n{BACKFILL_MARKER}\n内容"):
        failures.append("done 漏判：完整方法卡未识别")
    # v7.1.2 防御：孤 marker 重写应能清掉
    # 构造一个含孤 marker（前后是 ## 来源 / <!-- linsai-wikilinks -->）的页面，
    # 调 _append_method_card 验证旧 marker 被清
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        from pathlib import Path as _P
        test_path = _P(td) / "test.md"
        test_path.write_text(
            "正文\n\n## 来源\n\n<!-- methods-backfill:v1 -->\n\n<!-- linsai-wikilinks -->\n## 关联概念\n\n- [[X]]\n",
            encoding="utf-8")
        _append_method_card(test_path, {
            "method_name": "test", "principle": "p",
            "params": [{"item": "k", "value": "v", "source": "s"}],
            "boundary": "b", "representative": "r"})
        new_text = test_path.read_text(encoding="utf-8")
        # 旧 marker 应被清（至少 marker 出现次数从 1 降到 1 = 新 marker）
        if new_text.count(BACKFILL_MARKER) > 1:
            failures.append("孤 marker 清理失败：v7.1.2 防御正则需放宽")
        # 新卡应包含方法名
        if "test" not in new_text:
            failures.append("新方法卡未写入")
    # 4) raw stem 映射
    sample = sorted(PAPERS_DIR.glob("2026-*.md"))
    if sample:
        raw = _raw_stem_for(sample[0].stem)
        if raw is not None and not raw.exists():
            failures.append(f"raw 映射指向不存在文件: {raw.name}")
    if failures:
        for x in failures:
            print(f"✗ {x}")
        return 1
    print("✓ kb_methods_backfill 自检通过（零 LLM）")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="存量论文页方法卡回补（零 LLM 编排层）")
    parser.add_argument("--scan", action="store_true", help="分级扫描")
    parser.add_argument("--worklist", type=int, default=0, metavar="N",
                        help="发射 N 页待处理工作清单（ZCode 任务消费）")
    parser.add_argument("--all", action="store_true", help="不限优先集（全库）")
    parser.add_argument("--all-pages", action="store_true",
                        help="【别名】同 --all（v7.1.0 显式命名）")
    parser.add_argument("--append", type=str, default="",
                        help="追加 paper stem 列表（逗号分隔）到现有 worklist，"
                             "配合 --source 标识来源（daily/distill）")
    parser.add_argument("--source", type=str, default="daily",
                        choices=["daily", "distill", "manual"],
                        help="追加入口的来源标识（v7.1.0）")
    parser.add_argument("--status", action="store_true", help="台账进度")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)
    if args.self_check:
        return _self_check()
    if args.status:
        show_status()
        return 0
    if args.scan:
        grades = scan_pages(only_priority=not (args.all or args.all_pages))
        for g in ("done", "A", "B", "C"):
            print(f"{g}: {len(grades[g])}")
        return 0
    if args.append:
        pages = [p.strip() for p in args.append.split(",") if p.strip()]
        return append_to_worklist(pages, source=args.source).get("appended", 0)
    if args.worklist:
        emit_worklist(args.worklist, only_priority=not (args.all or args.all_pages))
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
