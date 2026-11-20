# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——单遍深度研究（B1 背景调研 → B2 问题定位 → B3 方案分解）。

替代 v7 多轮优化环：每个课题一次单遍深研，不做多轮迭代优化。三步分别派给
researcher / analyst / writer profile，skill 纪律经 skill_loader 注入
（research-proposal / literature-reading / method-manual），产物落课题目录；
每步完成后做产物存在性校验，缺失即停（缺口留待下一次深研补齐）。

用法示例：
    python3 scripts/topic_pipeline.py --deep-dive general-mos2-hhg-20261116 --steps background,problem,scheme
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from . import state
from .card import append_card_event
from .constants import (
    PROJECT_ROOT,
    STEP_ARTIFACTS,
    STEP_PROFILE_MAP,
    STEP_TIMEOUTS,
)
from .hermes_runner import run_hermes

# skill 注入节前缀（fail-open：skill 缺失时注入块为空，prompt 仍完整可用）
# v8.0.1 校正：前缀须含 SKILL.md 节标题的中文序号（extract_section 匹配 "## <prefix>"）。
# 2026-11-17 全量验证发现旧前缀全部未命中（fail-open 掩盖，注入块静默为空）。
_SKILL_INJECTIONS = {
    "background": [
        ("literature-reading", ["一、五维笔记", "四、通用纪律"]),
    ],
    "problem": [
        ("research-proposal", ["〇、产出定位", "一、操作性五问"]),
    ],
    "scheme": [
        ("research-proposal", ["二、方案六要素模板", "五、质量递进链"]),
        ("method-manual", ["二、判据口径表", "三、参数溯源"]),
    ],
}


def _skill_block(step: str) -> str:
    try:
        import skill_loader
        parts = []
        for name, prefixes in _SKILL_INJECTIONS.get(step, []):
            parts.append(skill_loader.inject_block(name, prefixes))
        return "\n".join(p for p in parts if p)
    except Exception:
        return ""


def _load_card_fields(tdir: Path) -> Dict[str, Any]:
    from .card import parse_card
    return parse_card(tdir / "topic-card.md")


def _prompt(step: str, tdir: Path, fields: Dict[str, Any]) -> str:
    """构造深研派活 prompt（中文自然语言，产物契约明确）。"""
    problem = fields.get("problem", "")
    title = fields.get("title", "")
    common_head = (
        f"你是林赛研究工作台的深度研究执行者。课题目录：{tdir}\n"
        f"课题：{title}\n一句话问题：{problem}\n\n"
        f"【v8 纪律】这是单遍深度研究（课题启动包生产），不是项目书撰写："
        f"聚焦一个具体问题，交付可直接推进研究的方法和路线；不做多轮展开，"
        f"不写申请书式篇幅；引用必须真实可溯源（检索池/知识库页），"
        f"池中无记录不得写入，禁止凭记忆杜撰文献与数值。\n"
        f"课题卡：{tdir / 'topic-card.md'}（先读）\n"
    )
    if step == "background":
        return common_head + (
            "任务（B1 背景调研）：产出 01_background/literature-map.md——\n"
            "① 领域地图：该问题所在方向的现状脉络（≥4 段，每段带文献锚点 [ref:N]）；\n"
            "② 核心文献组：≥8 篇关键文献（含 ≥3 篇近 24 个月），每篇给出：出处、"
            "与本问题的关系一句话、关键数值/结论（原样保留并注明出处）；\n"
            "③ 知识库关联：列出可关联的 [[知识库页]]（检索 knowledge/wiki/）；\n"
            "④ 检索到的文献条目同步写入 04_references/references.bib，"
            "每条末行注明 `source: <KB页名|raw/papers路径|检索池>`（A4 溯源要求）。\n"
            "可用工具：多源学术检索与本地知识库检索。完成后写文件，不重复粘贴全文。\n"
            "【时间预算】本步限时 30 分钟：先完成检索骨架并尽早把 literature-map.md 与 references.bib "
            "落盘（先写后补），避免超时零产物。\n"
            + _skill_block("background")
        )
    if step == "problem":
        return common_head + (
            "任务（B2 问题定位）：先读 01_background/literature-map.md（如存在），"
            "产出 02_problem/problem.md——\n"
            "① 问题一句话陈述（单一、具体、可检验，禁止罗列多个问题）；\n"
            "② 为什么是这个问题（现状与空白，≤5 段，带文献锚点）；\n"
            "③ 新颖性对照：与既有工作/既有课题报告的差异点（≥3 条）；\n"
            "④ 可检验判据：给出 3-5 条判据，每条标注 [V]（已核实外部文献）/ "
            "[P]（自设阈值，说明理由）/ [D]（需预研标定）。\n"
            + _skill_block("problem")
        )
    if step == "scheme":
        return common_head + (
            "任务（B3 方案分解）：先读 02_problem/problem.md，产出 03_scheme/scheme.md——\n"
            "① 步骤分解 S1..Sn（n≥3）：每步含 方法 / 输入 / 输出 / 判据 / 预计工作量；\n"
            "② 里程碑 M1..Mk 与首月路线（先做什么、需要什么准备）；\n"
            "③ 风险与备选路线：每个关键步骤一条 fallback；\n"
            "④ 方法学素材：检索 knowledge/wiki/methods/ 与论文方法卡，"
            "把可用方法的参数（含单位与出处）写进对应步骤（参数溯源纪律）。\n"
            "同步更新 04_references/references.bib（新增引用补 source 溯源行）。\n"
            + _skill_block("scheme")
        )
    raise ValueError(f"未知深研步骤: {step}")


def _append_run_log(tdir: Path, entry: Dict[str, Any]) -> None:
    """深研运行历史落盘（保留最近 10 次），供诊断与 token 复盘。"""
    import json as _json
    path = tdir / "deep-dive-runs.json"
    try:
        history = _json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    except Exception:
        history = []
    if not isinstance(history, list):
        history = []
    history.append(entry)
    path.write_text(_json.dumps(history[-10:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _verify_artifacts(tdir: Path, step: str) -> Dict[str, Any]:
    """产物存在性校验：done 必有产物（缺失即该步未完成）。"""
    detail = []
    ok_all = True
    for rel in STEP_ARTIFACTS.get(step, []):
        p = tdir / rel
        ok = p.exists() and p.stat().st_size >= 50
        ok_all = ok_all and ok
        detail.append({"path": rel, "exists": p.exists(), "size": p.stat().st_size if p.exists() else 0, "ok": ok})
    return {"step": step, "ok": ok_all, "artifacts": detail}


def _scheme_is_migration_draft(tdir: Path) -> bool:
    """v8.0.6 B3 迁移稿识别：迁移稿不视为「已完成」，强制 B3 重写。

    特征（任一命中即判迁移稿，与 migration.py 产物特征一致）：
    ① 03_scheme/scheme-source.md 存在；② 文件头含迁移声明
    （「迁移稿」/「待深研改写」）；③ 按 A3 口径（acceptance.check_a3 同一
    正则）步骤数为 0。不改 A3 判据标准，只改「什么算完成」的识别。
    """
    scheme = tdir / "03_scheme" / "scheme.md"
    if not scheme.exists():
        return False
    if (tdir / "03_scheme" / "scheme-source.md").exists():
        return True
    try:
        text = scheme.read_text(encoding="utf-8")
    except Exception:
        return True
    head = text[:600]
    if "迁移稿" in head or "待深研改写" in head:
        return True
    import re as _re
    return not _re.findall(r"^#{1,3}\s*S\d+", text, _re.M)


def _read_state_rec(topic_id: str) -> Dict[str, Any]:
    data = state.load_state()
    return data, (state.get_topic(data, topic_id) or {})


def deep_dive(
    topic_id: str,
    steps: Optional[List[str]] = None,
    dry_run: bool = False,
    runner=None,
) -> Dict[str, Any]:
    """对指定课题执行单遍深研（默认 B1→B2→B3 顺序，跳过已完成步骤）。

    Args:
        runner: 可注入的 hermes 执行函数（测试用 mock）；默认 run_hermes
    Returns:
        {topic_id, steps_run, steps_ok, verify, gaps, next}
    """
    runner = runner or run_hermes
    steps = steps or list(STEP_PROFILE_MAP.keys())
    rec_dir = state.topic_dir(topic_id)
    if rec_dir is None:
        return {"success": False, "error": f"课题不存在或目录缺失: {topic_id}"}
    tdir = Path(rec_dir)
    fields = _load_card_fields(tdir)

    # questions → kickoff 晋级（首次深研时；阶段即目录，transition 统一入口）
    data, rec = _read_state_rec(topic_id)
    if rec.get("stage") == "questions" and not dry_run:
        moved = state.transition(topic_id, "kickoff", "进入深研")
        tdir = Path(moved["dir"]) if moved.get("dir") else tdir
        append_card_event(tdir / "topic-card.md", f"{state._now()} questions → kickoff（进入单遍深研）")

    run_log: List[Dict[str, Any]] = []
    gaps: List[str] = []
    for step in steps:
        if step not in STEP_PROFILE_MAP:
            return {"success": False, "error": f"未知步骤: {step}"}
        # 已有产物且 ≥50 字节的步骤跳过（补齐模式只做缺的）；
        # v8.0.6：scheme 步的迁移稿不视为已完成（steps=0 会让 A3 永挂，强制重写）
        verify0 = _verify_artifacts(tdir, step)
        if verify0["ok"] and not (step == "scheme" and _scheme_is_migration_draft(tdir)):
            run_log.append({"step": step, "skipped": "产物已存在"})
            continue
        if step == "scheme" and verify0["ok"]:
            run_log.append({"step": step, "note": "迁移稿判为缺口，强制 B3 重写"})
        if dry_run:
            run_log.append({"step": step, "dry_run": True})
            continue
        profile = STEP_PROFILE_MAP[step]
        prompt = _prompt(step, tdir, fields)
        res = runner(profile, prompt, timeout=STEP_TIMEOUTS.get(step, 900))
        verify = _verify_artifacts(tdir, step)
        run_log.append({
            "step": step, "profile": profile, "success": res.get("success"),
            "elapsed_s": res.get("elapsed_s"), "error": res.get("error", ""),
            "verify": verify,
        })
        # v8.0.6：缺口只看产物验收。runner 失败（如超时）但产物已落盘且过验
        # （attosecond 11-18 实例：1800s 超时却产出 49,917 字节 literature-map）
        # → 不计缺口、不 break，继续下一步；产物缺失才停（单遍纪律保留）。
        if not verify["ok"]:
            gaps.append(step)
            break  # 单遍纪律：产物缺失即停，缺口留待下次补齐
        if not res.get("success"):
            run_log[-1]["note"] = "runner 失败但产物已过验，按产物续跑"

    # v8.0.2：运行结果落盘（每步 success/elapsed/error 可追溯，此前仅内存+汇总行）
    if not dry_run and run_log:
        _append_run_log(tdir, {"at": state._now(), "topic_id": topic_id, "steps": run_log, "gaps": gaps})

    # 记录缺口与修复计数
    if not dry_run:
        with state.state_lock():
            data = state.load_state()
            rec = state.get_topic(data, topic_id) or {}
            prev = rec.get("deep_dive_gaps", [])
            counters = rec.get("gap_repair_counts", {}) or {}
            for g in gaps:
                counters[g] = counters.get(g, 0) + 1
            state.upsert_topic(data, topic_id, {
                "deep_dive_gaps": gaps,
                "gap_repair_counts": counters,
                "needs_human": any(c > 2 for c in counters.values()),
            })
            state.save_state(data)
        if gaps:
            append_card_event(tdir / "topic-card.md",
                              f"{state._now()} 深研缺口: {','.join(gaps)}（待下次补齐）")

    return {
        "success": not gaps,
        "topic_id": topic_id,
        "dir": str(tdir),
        "steps_run": run_log,
        "gaps": gaps,
    }
