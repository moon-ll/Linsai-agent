#!/usr/bin/env python3
"""周末维护链 job 执行器（v6.9.99，T2）。

反思链尾三个新 job 的 handler：
- run_reflection_proposal_calibration：全部 optimizing 课题的零 LLM
  程序化校准（引用对账 + 范本指标），high 级问题写入
  06_feedback/feedback-{N+1}-raw.md 并递增 human_feedback_count，
  借 load_review_feedback_for_optimization 通道注入下轮
  critic/writer prompt（无 high 问题只落报告不动 count，防反馈通胀）。
- run_reflection_link_deep_review：复用 retrospective.run_retrospective
  生成结构化周报（含策略建议预生成），报告落周末反思目录
  link-deep-review-{date}.md（取代已撤除的周一 lc-retrospective cron）。
- run_reflection_kb_taxonomy_apply：kb_taxonomy 候选分类执行
  （apply 前备份 categories.json，apply 后 scan_all_categories 刷新
  matched_paths）；无候选时写空产物文件，保持"done 必有产物"不变式。

用法（由 weekend_pipeline.executor 按二元组调度，不直接 CLI 调用）：
    python3 scripts/weekend_orchestrator.py --reflection   # 周日反思链入口
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import file_lock, load_json, now_utc, save_json

from proposal_lifecycle.constants import PROPOSALS_ROOT

from .constants import WEEKEND_REFLECTION_DIR

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


def _ensure_reflection_dir() -> None:
    WEEKEND_REFLECTION_DIR.mkdir(parents=True, exist_ok=True)


def _date_str() -> str:
    return now_utc()[:10]


# ---------------------------------------------------------------------------
# ① proposal_calibration —— 引用对账 + 范本指标（零 LLM）
# ---------------------------------------------------------------------------

# 参与正文引用统计的模块（references.md 自身是列表，排除）
_BODY_MODULES = ["rationale.md", "content.md", "scheme.md", "full_review.md"]

# 范本目标区间（NSFC 范式）
_RATIONALE_CJK_TARGET = (5000, 8000)      # 立项依据中文字数
_CITATION_COUNT_TARGET = (10, 20)         # 正文编号引用总次数

# 占位符特征（high 级）：writer 未完成引用/内容的典型残留
_PLACEHOLDER_PATTERNS = [
    "[CITE:", "[cite:", "[Cite:",
    "[REF:", "[ref:",
    "[INSERT", "[insert",
    "[占位", "占位符",
    "[TODO", "[todo", "TODO:",
    "TBD", "待补充",
]

# 噪声剥离：代码围栏 / 数学块（$$…$$）/ 行内数学（$…$）。
# T1 评审教训：$T\in[50,300]$ 这类数学区间若不豁免会被当成引用 [50,300]。
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_MATH_BLOCK_RE = re.compile(r"\$\$.*?\$\$", re.DOTALL)
_MATH_INLINE_RE = re.compile(r"\$[^$\n]+\$")
# 引用括号组：内容仅为数字/逗号/空格/连字符（如 [18] [5,6,16] [3-5]）
_CITATION_RE = re.compile(r"\[([0-9][0-9,\s\-–—]*)\]")
# references.md 条目行：行首 [N]
_REF_ENTRY_RE = re.compile(r"^\s*\[(\d+)\]", re.MULTILINE)
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def strip_noise(text: str) -> str:
    """剥离 frontmatter / 代码围栏 / 数学区块，供引用扫描使用。

    数学区间豁免是硬约束（T1 评审教训：$T\\in[50,300]$ 被误判为引用
    编号 50/300 触发超界误报）；frontmatter 中的编号（元数据）同样
    不属于正文引用。
    """
    if text.startswith("---"):
        m = re.match(r"^---[ \t]*\n.*?\n---[ \t]*\n?", text, re.DOTALL)
        if m:
            text = text[m.end():]
    text = _CODE_FENCE_RE.sub(" ", text)
    text = _MATH_BLOCK_RE.sub(" ", text)
    text = _MATH_INLINE_RE.sub(" ", text)
    return text


def _expand_bracket_numbers(content: str) -> List[int]:
    """把括号组内容展开为编号列表：[5,6,16]→[5,6,16]，[3-5]→[3,4,5]。"""
    numbers: List[int] = []
    for part in re.split(r"[,，]", content):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(\d+)\s*[-–—]\s*(\d+)$", part)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            # 连字符区间：正常文献引用跨度不会超过 20，超出视为数值区间
            # （如温度/能量范围误入），保守跳过防误报
            if 0 < hi - lo <= 20:
                numbers.extend(range(lo, hi + 1))
            continue
        if part.isdigit():
            numbers.append(int(part))
    return numbers


def scan_citations(text: str) -> Dict[str, Any]:
    """扫描去噪文本中的编号引用，返回统计与编号集合。"""
    occurrences = 0
    numbers: List[int] = []
    for m in _CITATION_RE.finditer(text):
        expanded = _expand_bracket_numbers(m.group(1))
        if not expanded:
            continue
        occurrences += 1
        numbers.extend(expanded)
    return {
        "occurrences": occurrences,          # 括号组出现次数
        "total_numbers": len(numbers),       # 展开后编号总个数
        "unique": sorted(set(numbers)),
        "max": max(numbers) if numbers else 0,
    }


def parse_reference_entries(ref_text: str) -> List[int]:
    """解析 references.md 的条目编号（行首 [N]）。"""
    return [int(m.group(1)) for m in _REF_ENTRY_RE.finditer(ref_text)]


def calibrate_proposal(prop_dir: Path) -> Dict[str, Any]:
    """对单个课题目录执行程序化校准，返回问题清单与统计。

    问题分级（与注入门槛对齐）：
    - high：引用超界 / 占位符 / 死条目 > 3 —— 触发反馈注入；
    - medium：立项依据字数越界 / 死条目（≤3 条）；
    - low：编号缺口 / 引用次数越界 / 主语混用 —— 仅记录不注入。
    """
    sections_dir = prop_dir / "04_proposal" / "sections"
    issues: List[Dict[str, Any]] = []
    stats: Dict[str, Any] = {
        "sections_found": [],
        "ref_entries": 0,
        "citation_occurrences": 0,
        "citation_unique": 0,
        "citation_max": 0,
        "rationale_cjk": 0,
        "subject_benketi": 0,
        "subject_women": 0,
        "high": 0,
    }

    body_texts: Dict[str, str] = {}
    for name in _BODY_MODULES:
        p = sections_dir / name
        if p.exists():
            try:
                body_texts[name] = p.read_text(encoding="utf-8")
                stats["sections_found"].append(name)
            except Exception:
                continue

    ref_path = sections_dir / "references.md"
    ref_text = ref_path.read_text(encoding="utf-8") if ref_path.exists() else ""
    ref_nums = parse_reference_entries(ref_text)
    stats["ref_entries"] = len(ref_nums)
    ref_num_set = set(ref_nums)

    # --- 1) 引用对账 ---
    # frontmatter 剥离必须逐文件执行：合并后拼接的文本只有首个文件能
    # 命中 "^---" 锚点，后续文件的 frontmatter 编号会泄漏进引用统计
    clean_texts = {name: strip_noise(t) for name, t in body_texts.items()}
    combined_clean = "\n\n".join(clean_texts.values())
    cit = scan_citations(combined_clean)
    stats["citation_occurrences"] = cit["occurrences"]
    stats["citation_unique"] = len(cit["unique"])
    stats["citation_max"] = cit["max"]

    if ref_nums:
        out_of_range = [n for n in cit["unique"] if n not in ref_num_set]
        for n in out_of_range:
            issues.append({
                "level": "high",
                "type": "引用超界",
                "where": "04_proposal/sections/（正文各模块）",
                "detail": f"引用编号 [{n}] 在 references.md 中无对应条目（列表共 {len(ref_nums)} 条）",
                "fix": f"为 [{n}] 补充参考文献条目，或改引现有编号（1-{max(ref_nums)}）",
            })
        dead = sorted(ref_num_set - set(cit["unique"]))
        if len(dead) > 3:
            issues.append({
                "level": "high",
                "type": "死条目过多",
                "where": "04_proposal/sections/references.md",
                "detail": f"参考文献有 {len(dead)} 条从未被正文引用：{dead[:10]}{'…' if len(dead) > 10 else ''}",
                "fix": "在立项依据/研究内容中补引支撑论点的关键文献，或删除无关条目并重排编号",
            })
        elif dead:
            issues.append({
                "level": "medium",
                "type": "死条目",
                "where": "04_proposal/sections/references.md",
                "detail": f"{len(dead)} 条参考文献未被正文引用：{dead}",
                "fix": "确认是否遗漏引用；无关联条目建议移除",
            })
        gaps = sorted(set(range(1, max(ref_nums) + 1)) - ref_num_set)
        if gaps:
            issues.append({
                "level": "low",
                "type": "编号缺口",
                "where": "04_proposal/sections/references.md",
                "detail": f"编号 1-{max(ref_nums)} 中有缺口：{gaps[:10]}{'…' if len(gaps) > 10 else ''}",
                "fix": "重新排序参考文献编号，消除跳号",
            })
    elif cit["occurrences"] > 0:
        issues.append({
            "level": "high",
            "type": "引用无列表",
            "where": "04_proposal/sections/references.md",
            "detail": f"正文有 {cit['occurrences']} 处编号引用但 references.md 为空或无条目",
            "fix": "补齐参考文献列表（references 校验步骤应已生成）",
        })

    # --- 2) 范本指标 ---
    rationale_clean = clean_texts.get("rationale.md", "")
    cjk_count = len(_CJK_RE.findall(rationale_clean))
    stats["rationale_cjk"] = cjk_count
    lo, hi = _RATIONALE_CJK_TARGET
    if cjk_count and not (lo <= cjk_count <= hi):
        issues.append({
            "level": "medium",
            "type": "立项依据字数越界",
            "where": "04_proposal/sections/rationale.md",
            "detail": f"中文字数 {cjk_count}，目标区间 {lo}-{hi}",
            "fix": "低于下限时补充科学意义/国内外现状论证；高于上限时压缩冗余叙述",
        })

    lo_c, hi_c = _CITATION_COUNT_TARGET
    if not (lo_c <= cit["occurrences"] <= hi_c):
        issues.append({
            "level": "low",
            "type": "引用次数越界",
            "where": "04_proposal/sections/（正文合计）",
            "detail": f"编号引用共 {cit['occurrences']} 处，范本目标 {lo_c}-{hi_c} 处",
            "fix": "过少时在关键论点处补引；过多时合并同类引用（如 [5,6,16]）",
        })

    # 主语混用计数（正文去噪后，复用逐文件剥离结果）
    subject_text = combined_clean
    stats["subject_benketi"] = len(re.findall(r"本课题", subject_text))
    stats["subject_women"] = len(re.findall(r"我们", subject_text))
    if stats["subject_benketi"] > 0 and stats["subject_women"] > 0:
        issues.append({
            "level": "low",
            "type": "主语混用",
            "where": "04_proposal/sections/（正文各模块）",
            "detail": f"「本课题」×{stats['subject_benketi']} 与「我们」×{stats['subject_women']} 混用",
            "fix": "统一主语口径（NSFC 申请书惯例建议统一为「本项目/本课题」）",
        })

    # 占位符扫描（对噪声剥离前的原文扫描，避免误删标记）
    for name, text in body_texts.items():
        for pat in _PLACEHOLDER_PATTERNS:
            idx = text.find(pat)
            if idx >= 0:
                line_no = text.count("\n", 0, idx) + 1
                issues.append({
                    "level": "high",
                    "type": "占位符残留",
                    "where": f"04_proposal/sections/{name}（第 {line_no} 行）",
                    "detail": f"发现占位符标记「{pat}」",
                    "fix": f"补全该处内容或引用后删除占位符（{name}）",
                })

    stats["high"] = sum(1 for i in issues if i["level"] == "high")
    return {"issues": issues, "stats": stats}


def _render_calibration_report(pid: str, result: Dict[str, Any], date_str: str) -> str:
    """渲染单课题校准报告 markdown（含机器可读摘要行，供收尾汇总提取）。"""
    stats = result["stats"]
    issues = result["issues"]
    lo, hi = _RATIONALE_CJK_TARGET
    lo_c, hi_c = _CITATION_COUNT_TARGET
    lines = [
        f"# 课题校准报告 — {pid}",
        "",
        f"> 生成时间：{now_utc()}",
        "> 来源：reflection_proposal_calibration（零 LLM 程序化校准，v6.9.99 周末维护链）",
        "",
        "## 总览",
        "",
        "| 指标 | 数值 | 目标/说明 |",
        "|------|------|-----------|",
        f"| 参考文献条数 | {stats['ref_entries']} | 行首 [N] 条目 |",
        f"| 正文引用次数 | {stats['citation_occurrences']} | 目标 {lo_c}-{hi_c} 处 |",
        f"| 唯一引用编号 | {stats['citation_unique']} | 最大编号 {stats['citation_max']} |",
        f"| 立项依据中文字数 | {stats['rationale_cjk']} | 目标 {lo}-{hi} |",
        f"| 主语计数 | 本课题 ×{stats['subject_benketi']} / 我们 ×{stats['subject_women']} | 混用则提示 |",
        f"| 问题合计 | {len(issues)}（high {stats['high']}） | high 触发反馈注入 |",
        "",
    ]
    if issues:
        lines.append("## 问题清单")
        lines.append("")
        lines.append("| 级别 | 类型 | 位置 | 说明 | 修法建议 |")
        lines.append("|------|------|------|------|----------|")
        for i in issues:
            lines.append(
                f"| {i['level']} | {i['type']} | {i['where']} | {i['detail']} | {i['fix']} |"
            )
        lines.append("")
    else:
        lines.append("未发现问题。")
        lines.append("")
    marker = (
        '<!-- calibration: {{"proposal_id": "{pid}", "high": {high}, '
        '"issues": {issues}, "date": "{date}"}} -->'
    ).format(pid=pid, high=stats["high"], issues=len(issues), date=date_str)
    lines.append(marker)
    lines.append("")
    return "\n".join(lines)


def _render_feedback_text(pid: str, result: Dict[str, Any], date_str: str) -> str:
    """渲染注入 06_feedback 的反馈正文（前 1500 字符将被 prompt 注入）。"""
    high_issues = [i for i in result["issues"] if i["level"] == "high"]
    lines = [
        "【周末校准自动反馈（零 LLM 程序化校准）】",
        f"发现 {len(high_issues)} 个 high 级问题，下轮优化请优先处理：",
        "",
    ]
    for n, i in enumerate(high_issues[:6], 1):
        lines.append(f"{n}. [{i['level']}]（{i['where']}）{i['detail']} → {i['fix']}")
    if len(high_issues) > 6:
        lines.append(f"…另有 {len(high_issues) - 6} 个 high 问题，详见完整报告。")
    lines.append("")
    lines.append(f"（完整校准报告：06_feedback/calibration-{date_str}.md）")
    return "\n".join(lines)


def _bump_feedback_counts(injections: List[Tuple[str, int]]) -> bool:
    """递增课题 human_feedback_count（file_lock("lifecycle") 保护）。

    必须在 feedback-{N+1}-raw.md 全部落盘之后调用——注入通道
    load_review_feedback_for_optimization 按 count 定位 raw 文件，
    先加计数后写文件会出现"计数指向不存在文件"的空注入窗口。
    """
    lifecycle_path = PROPOSALS_ROOT / "_lifecycle.json"
    with file_lock("lifecycle"):
        data = load_json(lifecycle_path, default={"proposals": {}})
        changed = False
        for pid, _num in injections:
            prop = data.get("proposals", {}).get(pid)
            if prop is None:
                continue
            prop["human_feedback_count"] = int(prop.get("human_feedback_count", 0)) + 1
            prop["updated_at"] = now_utc()
            changed = True
        if changed:
            save_json(lifecycle_path, data)
    return changed


def run_reflection_proposal_calibration(
    state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False
) -> Dict[str, Any]:
    """反思链尾 job①：全部 optimizing 课题程序化校准 + high 反馈注入。"""
    _ensure_reflection_dir()
    date_str = _date_str()

    try:
        from proposal_lifecycle import ProposalLifecycle
        lc = ProposalLifecycle()
        optimizing = lc.list_by_status("optimizing")
    except Exception as e:
        return {"success": False, "error": f"读取生命周期状态失败: {e}"}

    per_proposal: List[Dict[str, Any]] = []
    injections: List[Tuple[str, int]] = []       # (pid, feedback_num)
    injection_files: List[Tuple[Path, str]] = []  # (path, text)

    for p in optimizing:
        pid = p.get("proposal_id", "")
        if not pid:
            continue
        prop_dir = PROPOSALS_ROOT / "optimizing" / pid
        if not prop_dir.is_dir():
            continue
        try:
            result = calibrate_proposal(prop_dir)
        except Exception as e:
            per_proposal.append({
                "proposal_id": pid, "high": 0, "issues": 0, "error": str(e),
            })
            continue

        entry = {
            "proposal_id": pid,
            "high": result["stats"]["high"],
            "issues": len(result["issues"]),
            "stats": {k: v for k, v in result["stats"].items() if k != "sections_found"},
        }
        per_proposal.append(entry)

        if dry_run or result["stats"]["high"] == 0:
            # 无 high 问题：只落校准报告，不动 human_feedback_count（防反馈通胀）
            if not dry_run:
                fb_dir = prop_dir / "06_feedback"
                fb_dir.mkdir(parents=True, exist_ok=True)
                (fb_dir / f"calibration-{date_str}.md").write_text(
                    _render_calibration_report(pid, result, date_str), encoding="utf-8"
                )
            else:
                entry["dry_run"] = True
            continue

        # high 问题 → 追加写 feedback-{N+1}-raw.md + 递增计数
        lifecycle_data = load_json(PROPOSALS_ROOT / "_lifecycle.json",
                                   default={"proposals": {}})
        feedback_num = int(
            lifecycle_data.get("proposals", {}).get(pid, {}).get("human_feedback_count", 0)
        ) + 1
        fb_dir = prop_dir / "06_feedback"
        raw_path = fb_dir / f"feedback-{feedback_num}-raw.md"
        text = (
            f"# 人工审核反馈（第{feedback_num}次）\n\n"
            f"**时间**: {now_utc()}\n**结论**: minor_revision\n\n---\n\n"
            + _render_feedback_text(pid, result, date_str)
        )
        injection_files.append((raw_path, text))
        injections.append((pid, feedback_num))
        entry["feedback_num"] = feedback_num
        if not dry_run:
            fb_dir.mkdir(parents=True, exist_ok=True)
            (fb_dir / f"calibration-{date_str}.md").write_text(
                _render_calibration_report(pid, result, date_str), encoding="utf-8"
            )

    # 先落反馈文件，再统一递增计数（见 _bump_feedback_counts 注释）
    if not dry_run:
        for raw_path, text in injection_files:
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_text(text, encoding="utf-8")
        if injections:
            _bump_feedback_counts(injections)

        # 聚合产物（job artifact，"done 必有产物"不变式）
        agg_lines = [
            f"# 周末课题校准汇总 — {date_str}",
            "",
            f"> 生成时间：{now_utc()} | 来源：reflection_proposal_calibration（零 LLM）",
            "",
            "| 课题 | 问题数 | high | 反馈注入 |",
            "|------|--------|------|----------|",
        ]
        for e in per_proposal:
            agg_lines.append(
                f"| {e['proposal_id']} | {e['issues']} | {e['high']} | "
                f"{'feedback-' + str(e['feedback_num']) if e.get('feedback_num') else '—'} |"
            )
        if not per_proposal:
            agg_lines.append("| （本周末无 optimizing 课题） | — | — | — |")
        agg_lines.append("")
        high_total = sum(e.get("high", 0) for e in per_proposal)
        injected_total = len(injections)
        agg_lines.append(f"**high 合计**：{high_total} | **注入课题数**：{injected_total}")
        agg_lines.append("")
        (WEEKEND_REFLECTION_DIR / f"proposal-calibration-{date_str}.md").write_text(
            "\n".join(agg_lines), encoding="utf-8"
        )

    high_total = sum(e.get("high", 0) for e in per_proposal)
    if _log:
        _log.info(
            f"[proposal-calibration] 课题={len(per_proposal)}, high 合计={high_total}, "
            f"注入={len(injections)}, dry_run={dry_run}"
        )
    return {
        "success": True,
        "dry_run": dry_run,
        "proposals": len(per_proposal),
        "high_total": high_total,
        "injected": [pid for pid, _ in injections],
        "per_proposal": per_proposal,
    }


# ---------------------------------------------------------------------------
# ② link_deep_review —— 复用 retrospective 生成结构化周报
# ---------------------------------------------------------------------------


def run_reflection_link_deep_review(
    state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False
) -> Dict[str, Any]:
    """反思链尾 job②：全链路深度复盘（五源分析 + 策略建议预生成）。

    import 复用 retrospective.run_retrospective（不复制逻辑）；输出路径
    通过 v6.9.99 新增的 output_path 参数落到周末反思目录
    link-deep-review-{date}.md。dry-run 零落盘（run_retrospective 恒写
    文件并可能触发低风险策略自动应用，预览模式直接跳过）。
    """
    _ensure_reflection_dir()
    date_str = _date_str()
    target = WEEKEND_REFLECTION_DIR / f"link-deep-review-{date_str}.md"

    if dry_run:
        return {"success": True, "dry_run": True, "target": str(target),
                "message": "dry-run 跳过复盘执行（run_retrospective 恒写盘）"}

    try:
        from retrospective import run_retrospective
    except Exception as e:
        return {"success": False, "error": f"无法导入 retrospective: {e}"}

    try:
        output_path = run_retrospective("7d", output_path=target)
    except Exception as e:
        return {"success": False, "error": f"run_retrospective 失败: {e}"}

    return {
        "success": True,
        "report": str(output_path),
        "period": "7d",
    }


# ---------------------------------------------------------------------------
# ③ kb_taxonomy_apply —— 候选分类执行（零 LLM）
# ---------------------------------------------------------------------------


def run_reflection_kb_taxonomy_apply(
    state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False
) -> Dict[str, Any]:
    """反思链尾 job③：执行 kb_taxonomy 候选分类写入。

    流程：propose_categories（预览）→ apply_categories（内部先备份
    categories.json 为 .json.bak.{date} 再原子写入，同名跳过幂等）→
    scan_all_categories 刷新 matched_paths（apply 内部已接线）→
    coverage_after 验证。无候选时写空产物文件（"done 必有产物"）。

    v6.9.6 的"周日只提示不写入"哲学在此被 T2 显式推翻：候选生成
    （tag 频率 ≥5、清洗、上限 12、同名跳过）已是纯规则筛选，执行
    前有备份、执行幂等，风险受控；每周反思报告仍可追溯。
    """
    _ensure_reflection_dir()
    date_str = _date_str()

    try:
        from kb_taxonomy import propose_categories, apply_categories
    except Exception as e:
        return {"success": False, "error": f"无法导入 kb_taxonomy: {e}"}

    try:
        cands = propose_categories()
    except Exception as e:
        return {"success": False, "error": f"propose_categories 失败: {e}"}

    report_lines = [
        f"# 知识库分类体系执行报告 — {date_str}",
        "",
        f"> 生成时间：{now_utc()} | 来源：reflection_kb_taxonomy_apply（零 LLM）",
        "",
        f"- 候选分类：{len(cands)} 个",
    ]

    if dry_run:
        report_lines.append("- dry-run：仅预览，未写入 categories.json")
        return {"success": True, "dry_run": True, "candidates": len(cands),
                "names": [c["name"] for c in cands[:12]]}

    if not cands:
        report_lines.append("- 无候选（tag 频率未达门槛或均与现有分类同名）：本轮不写入")
        report_lines.append("- 空产物说明：保持 \"done 必有产物\" 不变式，非执行失败")
    else:
        for c in cands:
            report_lines.append(f"  - {c['name']}（覆盖 {c['pages']} 页，{c['reason']}）")
        try:
            applied = apply_categories(cands)
        except Exception as e:
            return {"success": False, "error": f"apply_categories 失败: {e}"}
        report_lines.append(f"- 写入结果：新增 {applied.get('added', 0)} 个（总 {applied.get('total', '?')}），已自动备份原 categories.json")
        try:
            from kb_taxonomy import coverage_after
            report_lines.append(f"- 写入后分类覆盖率：{coverage_after():.2f}")
        except Exception:
            pass

    (WEEKEND_REFLECTION_DIR / f"kb-taxonomy-apply-{date_str}.md").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )

    if _log:
        _log.info(f"[kb-taxonomy-apply] 候选={len(cands)}, dry_run={dry_run}")
    return {
        "success": True,
        "candidates": len(cands),
        "applied": bool(cands),
    }
