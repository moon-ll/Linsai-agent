# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——B4 启动包集成（机械组装，零 LLM）。

深研三步产物 → topic-report.md 课题报告。组装是确定性的：按模板拼接
背景/问题/方案三节原文 + 参考文献节 + 关联课题节；超 G1 上限时保留各节
首部内容并附全文指针（不丢内容，报告是入口不是仓库）。

用法示例：
    python3 scripts/topic_pipeline.py --assemble general-mos2-hhg-20261116
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from . import state
from .card import append_card_event
from .constants import G1_REPORT_MAX_CHARS

_REPORT_TEMPLATE_HEAD = """# {title}

- 课题 ID: {topic_id}
- 状态: {stage}
- 来源: {source}
- 关联课题: {related}
- 本报告由工作台 B4 机械组装（各节全文见课题目录，此处为整合视图）

## 一、问题一句话陈述

{problem}

## 二、背景调研摘要

{background}

## 三、问题定位

{problem_sec}

## 四、方案分解

{scheme}

## 五、参考文献

{references}
"""


def _read_or(path: Path, fallback: str = "（产物缺失，待深研补齐）", limit: int = 2600) -> str:
    if not path.exists():
        return fallback
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return fallback
    if len(text) > limit:
        head = text[:limit]
        # 在最后一个段落边界截断，避免半句
        cut = head.rfind("\n\n")
        if cut > 400:
            head = head[:cut]
        return head + f"\n\n……（节选，全文见 `{path.name}`）"
    return text


def _bib_summary(tdir: Path) -> str:
    bib = tdir / "04_references" / "references.bib"
    if not bib.exists():
        return "（references.bib 缺失，待深研补齐——A4 硬门）"
    lines = [l for l in bib.read_text(encoding="utf-8").splitlines() if l.strip()]
    n_entries = sum(1 for l in lines if l.strip().startswith("@"))
    n_source = sum(1 for l in lines if l.strip().lower().startswith("source:"))
    return (
        f"共 {n_entries} 条 bib 条目，其中 {n_source} 条带 source 溯源行。"
        f"完整条目见 `04_references/references.bib`。\n"
    )


def _wikilink_count(text: str) -> int:
    return len(set(re.findall(r"\[\[([^\]]+)\]\]", text)))


def mount_methods_pack(topic_id: str) -> Dict[str, Any]:
    """B4：按课题关键词聚合 KB 方法页/方法主题/论文方法卡 → 03_scheme/kb-methods-pack.md。

    复用 kb_methods_pack 的匹配器（零 LLM，只读知识库）；A3 验收要求素材包已挂载。
    """
    tdir_path = state.topic_dir(topic_id)
    if tdir_path is None:
        return {"success": False, "error": f"课题不存在或目录缺失: {topic_id}"}
    tdir = Path(tdir_path)
    from .card import parse_card
    fields = parse_card(tdir / "topic-card.md")
    text_parts = [str(fields.get("title", "")), str(fields.get("problem", ""))]
    for rel in ("01_background/literature-map.md", "02_problem/problem.md"):
        p = tdir / rel
        if p.exists():
            try:
                text_parts.append(p.read_text(encoding="utf-8")[:3000])
            except Exception:
                pass
    text = "\n".join(text_parts)

    sections: list = [f"# 方法学素材包（{topic_id}）", "", f"> 由 B4 组装时按关键词聚合知识库（{state._now()}）", ""]
    matched = {"method_pages": 0, "method_topics": 0, "paper_cards": 0}
    try:
        import kb_methods_pack as kmp
        kws = kmp._keywords(text)
        for p in (kmp._match_method_pages(kws, top=8) or []):
            sections += [f"## 方法页：{p.get('title', '')}", f"- 来源：{p.get('path', '')}", ""]
            matched["method_pages"] += 1
        for t in (kmp._match_method_topics(kws, top=4) or []):
            sections += [f"## 方法专题：{t.get('title', '')}", f"- 来源：{t.get('path', '')}", ""]
            matched["method_topics"] += 1
        for c in (kmp._match_paper_cards(kws, top=6) or []):
            sections += [f"## 论文方法卡：{c.get('title', '')}", f"- 来源：{c.get('path', '')}", ""]
            matched["paper_cards"] += 1
    except Exception as e:  # noqa: BLE001
        sections += [f"（知识库匹配不可用：{e}）", ""]
    if not any(matched.values()):
        sections += ["（KB 暂无匹配方法页——B3 写作时按参数溯源纪律从检索池补充）", ""]
    out = tdir / "03_scheme" / "kb-methods-pack.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(sections), encoding="utf-8")
    return {"success": True, "pack": str(out), "matched": matched}


def assemble_report(topic_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """B4：把深研产物组装为课题报告（零 LLM）。"""
    tdir_path = state.topic_dir(topic_id)
    if tdir_path is None:
        return {"success": False, "error": f"课题不存在或目录缺失: {topic_id}"}
    tdir = Path(tdir_path)
    from .card import parse_card
    fields = parse_card(tdir / "topic-card.md")
    st_data = state.load_state()
    rec = state.get_topic(st_data, topic_id) or {}
    if not dry_run:
        mount_methods_pack(topic_id)

    related = rec.get("related") or fields.get("related") or []
    related_str = "、".join(related) if related else "（暂无，显式声明）"

    bg = _read_or(tdir / "01_background" / "literature-map.md")
    prob = _read_or(tdir / "02_problem" / "problem.md", limit=2600)
    scheme = _read_or(tdir / "03_scheme" / "scheme.md", limit=3600)

    report = _REPORT_TEMPLATE_HEAD.format(
        title=fields.get("title") or rec.get("title", topic_id),
        topic_id=topic_id,
        stage=rec.get("stage", ""),
        source=fields.get("source") or rec.get("source", ""),
        related=related_str,
        problem=fields.get("problem") or rec.get("problem", "（待注册补充）"),
        background=bg,
        problem_sec=prob,
        scheme=scheme,
        references=_bib_summary(tdir),
    )
    # G1 篇幅自适应：超限时按比例收缩三节再拼一次（确定性，保证 ≤ 上限）
    if len(report) > G1_REPORT_MAX_CHARS:
        budget = G1_REPORT_MAX_CHARS - (len(report) - len(bg) - len(prob) - len(scheme)) - 200
        budget = max(budget, 2400)
        bg = _read_or(tdir / "01_background" / "literature-map.md", limit=int(budget * 0.30) or 800)
        prob = _read_or(tdir / "02_problem" / "problem.md", limit=int(budget * 0.30) or 800)
        scheme = _read_or(tdir / "03_scheme" / "scheme.md", limit=int(budget * 0.40) or 1000)
        report = _REPORT_TEMPLATE_HEAD.format(
            title=fields.get("title") or rec.get("title", topic_id),
            topic_id=topic_id,
            stage=rec.get("stage", ""),
            source=fields.get("source") or rec.get("source", ""),
            related=related_str,
            problem=fields.get("problem") or rec.get("problem", "（待注册补充）"),
            background=bg,
            problem_sec=prob,
            scheme=scheme,
            references=_bib_summary(tdir),
        )
    body_chars = len(report)
    over_limit = body_chars > G1_REPORT_MAX_CHARS
    if dry_run:
        return {"success": True, "dry_run": True, "report_chars": body_chars, "over_limit": over_limit}
    (tdir / "topic-report.md").write_text(report, encoding="utf-8")
    append_card_event(
        tdir / "topic-card.md",
        f"{state._now()} B4 启动包集成完成（报告 {body_chars} 字符{'，超 G1 上限' if over_limit else ''}）",
    )
    return {
        "success": True,
        "topic_id": topic_id,
        "report": str(tdir / "topic-report.md"),
        "report_chars": body_chars,
        "over_limit": over_limit,
        "wikilinks": _wikilink_count(report),
    }
