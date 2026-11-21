# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——v7 存量课题迁移（research_proposals → research_topics）。

迁移原则（用户裁决 2026-11-16「避免资源浪费」）：复制不删除。v7 全部材料
按映射复制入新域，旧目录原位保留（research_proposals/ 标注 legacy）；
迁移报告落 research_topics/_audit/v8-migration-report.json。

阶段映射：drafts→questions / optimizing→kickoff / pending_review→ready /
archived→archive。报告与各节文件机械拼装（零 LLM），自检缺口如实记录，
由深研补齐流程消化。

用法示例：
    python3 scripts/topic_pipeline.py --migrate-v7            # 执行
    python3 scripts/topic_pipeline.py --migrate-v7 --dry-run  # 预览
"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import load_json

from . import state
from .card import render_card
from . import constants as _C
from .constants import AUDIT_DIRNAME, STAGES

# v7 数据域（保留原位，只读；PROJECT_ROOT 三层上溯，勿少算）
LEGACY_ROOT = Path(__file__).parent.parent.parent / "research_proposals"
LEGACY_STAGES = ("drafts", "optimizing", "pending_review", "archived")
STAGE_MAP = {
    "drafts": "questions",
    "optimizing": "kickoff",
    "pending_review": "ready",
    "archived": "archive",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _legacy_state_titles() -> Dict[str, str]:
    data = load_json(LEGACY_ROOT / "_lifecycle.json", default={}) or {}
    out = {}
    for pid, rec in (data.get("proposals") or {}).items():
        if isinstance(rec, dict):
            out[pid] = rec.get("title", "")
    return out


def _read_or(path: Path, limit: int = 2400) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if len(text) <= limit:
        return text
    head = text[:limit]
    cut = head.rfind("\n\n")
    if cut > 300:
        head = head[:cut]
    return head + f"\n\n……（节选自 `{path.name}`，全文见课题目录）"


def _clean_md(text: str) -> str:
    """去掉 markdown 标记（标题井号/加粗/引用/行内码），供回退提取。"""
    return re.sub(r"[#*>`\[\]]", "", text or "").strip()


def _extract_problem(idea_text: str, brief_text: str) -> str:
    """从 00_research_idea.md 抽问题陈述。

    优先级：核心科学问题节 → brief 核心问题行 → 研究背景/动机节首个 ≥80 字
    段落 → 正文首个 ≥80 字段落。全失败给占位（待深研补齐）。
    """
    m = re.search(r"#{1,3}[^\n]*核心科学问题[^\n]*\n(.*?)(?=\n#{1,3}|\Z)", idea_text, re.S)
    if m and m.group(1).strip():
        return _clean_md(m.group(1))[:1200]
    m = re.search(r"核心问题[^\n]*[:：]\s*(.+)", brief_text)
    if m and m.group(1).strip():
        return m.group(1).strip()
    m = re.search(r"#{1,3}[^\n]*(?:研究背景|背景与动机|背景调研)[^\n]*\n(.*?)(?=\n#{1,3}|\Z)", idea_text, re.S)
    if m:
        for para in m.group(1).split("\n\n"):
            cleaned = _clean_md(para)
            if len(cleaned) >= 80:
                return cleaned[:800]
    for para in (idea_text or "").split("\n\n"):
        cleaned = _clean_md(para)
        if len(cleaned) >= 80:
            return cleaned[:600]
    return "（迁移占位：待深研补齐问题陈述）"


def _copy_tree_subset(src: Path, dst: Path, patterns: tuple = ("*.md", "*.json", "*.bib")) -> int:
    """复制 src 下匹配文件到 dst（平铺，保留文件名；返回复制数）。"""
    n = 0
    if not src.exists():
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    for pat in patterns:
        for p in src.glob(pat):
            if p.is_file():
                shutil.copy2(p, dst / p.name)
                n += 1
    return n


def migrate_one(pid: str, stage_v7: str, prop_dir: Path, titles: Dict[str, str], dry_run: bool) -> Dict[str, Any]:
    """迁移单个 v7 课题到新域。"""
    stage_v8 = STAGE_MAP[stage_v7]
    topic_id = pid
    tdir = _C.TOPICS_ROOT / stage_v8 / topic_id
    title = titles.get(pid) or pid
    idea_path = prop_dir / "00_research_idea.md"
    brief_path = prop_dir / "00_proposal-brief.md"
    idea_text = idea_path.read_text(encoding="utf-8") if idea_path.exists() else ""
    brief_text = brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""
    problem = _extract_problem(idea_text, brief_text)
    actions: List[str] = []

    if dry_run:
        return {"topic_id": topic_id, "stage": stage_v8, "dry_run": True}

    if tdir.exists():
        return {"topic_id": topic_id, "stage": stage_v8, "skipped": "目标目录已存在"}

    # 1) 背景域：02_literature + 02_topic + 01_direction
    n = 0
    for sub in ("02_literature", "02_topic", "01_direction"):
        n += _copy_tree_subset(prop_dir / sub, tdir / "01_background")
    actions.append(f"01_background ← {n} 个文件")

    # 2) 问题域：研究设想原件 + 生成的 problem.md
    (tdir / "02_problem").mkdir(parents=True, exist_ok=True)
    if idea_path.exists():
        shutil.copy2(idea_path, tdir / "02_problem" / "idea-source.md")
    (tdir / "02_problem" / "problem.md").write_text(
        "# 问题定位（v7 迁移稿）\n\n"
        f"> 迁移自 research_proposals/{stage_v7}/{pid}/00_research_idea.md；"
        "新颖性对照与判据三标记待深研补齐。\n\n"
        "## 问题一句话陈述\n\n"
        f"{problem}\n",
        encoding="utf-8",
    )
    actions.append("02_problem ← idea-source.md + problem.md")

    # 3) 方案域：scheme 章节 + 方法手册 + 素材包
    (tdir / "03_scheme").mkdir(parents=True, exist_ok=True)
    scheme_src = prop_dir / "04_proposal" / "sections" / "scheme.md"
    if scheme_src.exists():
        shutil.copy2(scheme_src, tdir / "03_scheme" / "scheme-source.md")
    manual_src = prop_dir / "03_method" / "method-manual.md"
    if manual_src.exists():
        shutil.copy2(manual_src, tdir / "03_scheme" / "method-manual-source.md")
    pack_src = prop_dir / "03_method" / "kb-methods-pack.md"
    if pack_src.exists():
        shutil.copy2(pack_src, tdir / "03_scheme" / "kb-methods-pack.md")
    scheme_text = _read_or(scheme_src) if scheme_src.exists() else ""
    (tdir / "03_scheme" / "scheme.md").write_text(
        "# 方案分解（v7 迁移稿）\n\n"
        f"> 迁移自 research_proposals/{stage_v7}/{pid}/04_proposal/sections/scheme.md；"
        "步骤编号/首月路线/判据格式待深研改写为 S1..Sn 口径。\n\n"
        + (scheme_text or "（v7 方案章节缺失，待深研补齐）") + "\n",
        encoding="utf-8",
    )
    actions.append("03_scheme ← scheme-source + manual + pack + scheme.md")

    # 4) 参考文献域
    (tdir / "04_references").mkdir(parents=True, exist_ok=True)
    refs_src = prop_dir / "04_proposal" / "sections" / "references.md"
    if refs_src.exists():
        shutil.copy2(refs_src, tdir / "04_references" / "references-source.md")
    for bib in sorted((prop_dir / "02_literature").rglob("*.bib"))[:3]:
        if bib.name == "candidates.bib":
            shutil.copy2(bib, tdir / "04_references" / "references.bib")
        else:
            shutil.copy2(bib, tdir / "04_references" / f"bib-{bib.name}")
    actions.append("04_references ← references + bib")

    # 5) 课题报告（机械整合，带出处；各节限幅控制 G1 篇幅）
    report = (
        f"# {title}\n\n"
        f"- 课题 ID: {topic_id}\n- 状态: {stage_v8}\n- 迁移自: research_proposals/{stage_v7}/{pid}\n"
        f"- 迁移时间: {_now()}\n"
        f"- 本报告为 v7 材料机械整合（零 LLM），缺口见 kickoff-check.json\n\n"
        f"## 一、问题一句话陈述\n\n{problem}\n\n"
        f"## 二、背景调研摘要（迁移自 rationale/文献链）\n\n"
        + (_read_or(prop_dir / "04_proposal" / "sections" / "rationale.md", limit=1600) or "（v7 立项依据缺失）")
        + "\n\n## 三、问题定位（迁移自研究设想）\n\n"
        + _read_or(idea_path, limit=1400)
        + "\n\n## 四、方案分解（迁移自方案章节）\n\n"
        + (_read_or(scheme_src, limit=1600) if scheme_src.exists() else "（v7 方案章节缺失）")
        + "\n\n## 五、参考文献\n\n"
        + (_read_or(refs_src, limit=1200) if refs_src.exists() else "（v7 参考文献章节缺失）")
        + "\n"
    )
    (tdir / "topic-report.md").write_text(report, encoding="utf-8")
    actions.append("topic-report.md ← 五节机械整合")

    # 6) 课题卡
    card = render_card(
        title=title, topic_id=topic_id, stage=stage_v8, problem=problem,
        source=f"v7-migration:{stage_v7}", related=[],
        migrated_from=f"research_proposals/{stage_v7}/{pid}",
        knowledge_card="（v7 材料迁移，知识卡摘要见报告/设想原件）",
    )
    (tdir / "topic-card.md").write_text(card, encoding="utf-8")

    return {"topic_id": topic_id, "stage_v7": stage_v7, "stage_v8": stage_v8,
            "title": title, "problem": problem, "actions": actions}


def migrate_v7(dry_run: bool = False, only: Optional[str] = None) -> Dict[str, Any]:
    """执行 v7 → v8 全量迁移，写迁移报告与状态。"""
    titles = _legacy_state_titles()
    results: List[Dict[str, Any]] = []
    for stage_v7 in LEGACY_STAGES:
        root = LEGACY_ROOT / stage_v7
        if not root.exists():
            continue
        for prop_dir in sorted(root.iterdir()):
            if not prop_dir.is_dir() or prop_dir.name.startswith("_"):
                continue
            if only and prop_dir.name != only:
                continue
            try:
                res = migrate_one(prop_dir.name, stage_v7, prop_dir, titles, dry_run)
                results.append(res)
            except Exception as e:  # noqa: BLE001
                results.append({"topic_id": prop_dir.name, "error": str(e)})

    # 否决台账迁移
    rejected_moved = 0
    if not dry_run:
        legacy_state = load_json(LEGACY_ROOT / "_lifecycle.json", default={}) or {}
        with state.state_lock():
            data = state.load_state()
            for pid, rec in (legacy_state.get("rejected_ideas") or {}).items():
                if pid in data.get("rejected", {}):
                    continue
                if isinstance(rec, dict):
                    data.setdefault("rejected", {})[pid] = {
                        "title": rec.get("title", pid),
                        "reason": str(rec.get("reason", ""))[:300],
                        "rejected_at": rec.get("rejected_at", ""),
                        "migrated_from": "research_proposals/_rejected-ideas",
                    }
                    rejected_moved += 1
            # 登记迁移后的课题
            for res in results:
                if res.get("dry_run") or res.get("error") or res.get("skipped"):
                    continue
                state.upsert_topic(data, res["topic_id"], {
                    "title": res.get("title", ""),
                    "stage": res["stage_v8"],
                    "source": f"v7-migration:{res.get('stage_v7', '')}",
                    "problem": res.get("problem", "") if isinstance(res.get("problem"), str) else "",
                    "related": [],
                    "migrated_from": f"research_proposals/{res.get('stage_v7', '')}/{res['topic_id']}",
                })
            # v8.0.1：A2 新颖性证据回填（迁移课题此前默认 0.0 绕过硬门证据；
            # 对其余课题 + 否决台账做确定性 2-gram Jaccard 对照，排除自身）
            from . import similarity as _sim
            for tid, rec in data.get("topics", {}).items():
                if not isinstance(rec, dict) or rec.get("novelty") or not rec.get("title"):
                    continue
                others = [f"{r.get('title', '')} {r.get('problem', '')}"
                          for t2, r in data.get("topics", {}).items()
                          if t2 != tid and isinstance(r, dict)]
                others += [r.get("title", "") for r in data.get("rejected", {}).values()]
                text = f"{rec.get('title', '')} {rec.get('problem', '')}"
                best, competitor = 0.0, ""
                for o in others:
                    if not o.strip():
                        continue
                    s = _sim.jaccard_similarity(text, [o])
                    if s > best:
                        best, competitor = s, o[:60]
                rec["novelty"] = {"max_score": best, "competitor": competitor,
                                  "backfilled": True}
            state.save_state(data)

    report = {
        "action": "v7_to_v8_migration",
        "executed_at": _now(),
        "dry_run": dry_run,
        "count": len(results),
        "rejected_migrated": rejected_moved,
        "results": results,
        "legacy_preserved": str(LEGACY_ROOT),
    }
    if not dry_run:
        audit_dir = _C.TOPICS_ROOT / AUDIT_DIRNAME
        audit_dir.mkdir(parents=True, exist_ok=True)
        (audit_dir / "v8-migration-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # 迁移域写 legacy 标注
        (LEGACY_ROOT / "README-v7-LEGACY.md").write_text(
            "# v7 遗留数据域（legacy）\n\n"
            "> v8.0.0（2026-11-16）起本目录为只读遗留域：全部课题已迁移至\n"
            "> `research_topics/`（迁移报告：research_topics/_audit/v8-migration-report.json）。\n"
            "> 原则：复制不删除——本目录保留全部原始材料作审计与回滚线索，不再读写。\n"
            "> 旧生命周期脚本（多轮优化环）已停用，cron 见 memory/v8-cron-teardown.json。\n",
            encoding="utf-8",
        )
    return report
