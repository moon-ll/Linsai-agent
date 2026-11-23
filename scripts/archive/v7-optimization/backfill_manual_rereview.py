#!/usr/bin/env python3
"""手册复评回流：管线外 method_manual 评审产出 → 生命周期状态（v7.3.45）。

背景（G2-1 状态回流断点）：评审团/人工会话（如 v7.3.38-40 三册手册补评）
直接写 05_review/critic-round-{n}-method_manual.md，但生命周期状态
（score_history + section_passes["method_manual"]）只有管线 writer 步
（executor._run_manual_writer_step）会更新——会话产出停滞在文件层，
已达标课题（ssh-weyl/attosecond 数值门槛已全过）被 stale 手册门卡住，
无法在轮次完成时经 B 通道验收线晋级。

本脚本扫描 optimizing 课题的最新 method_manual 评审报告，按与 writer 步
**同一过线口径**回流状态：
  过线 = 报告分 ≥ min_overall_score（general 0.85 / key 0.90 / major 0.95）
         且无 critical/high 问题行 且 两维（严谨/就绪）≥0.70
         且就绪度 ≥ L3 且手册体积 ≥ MANUAL_MIN_BYTES。
幂等：报告轮次 ≤ score_history 已有 method_manual 最大轮次时跳过。
provenance：条目带 source="manual_rereview_backfill" + 报告相对路径，
与管线原生条目可区分，审计可溯源。

报告解析容错三种书写（G2-4 契约告警）：契约纯文本（`综合评分：0.89`）、
加粗行（`- 综合：**0.89**`）、表格行（`| 综合 | 0.89 |`）——非契约格式
解析成功时输出 ⚠ 提醒（评审产出方应对齐报告输出契约，否则管线原生
解析链 _read_critic_report 读不到分）。

用法：
    python3 scripts/backfill_manual_rereview.py --dry-run
    python3 scripts/backfill_manual_rereview.py --apply
    python3 scripts/backfill_manual_rereview.py --proposal general-ssh-weyl-20260920 --apply
    python3 scripts/backfill_manual_rereview.py --self-check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import file_lock, load_json, save_json  # noqa: E402
from lifecycle.constants import MANUAL_MIN_BYTES, MANUAL_READY_LEVEL  # noqa: E402

LIFECYCLE = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
STANDARDS = PROJECT_ROOT / "memory" / "nsfc-standards.json"
PROPOSAL_ROOT = PROJECT_ROOT / "research_proposals"

MANUAL_DIM_FLOOR = 0.70  # 与 executor._run_manual_writer_step 同口径
SOURCE_TAG = "manual_rereview_backfill"

# --sections 模式：章节终评报告 → 生命周期账本（不覆盖 last_score）
SOURCE_TAG_SECTIONS = "section_rereview_backfill"
SECTION_KEYS = ("rationale", "content", "scheme", "full_review", "references")
_SHA_PAT = re.compile(r"评审时\s*sha256[：:]\s*`([0-9a-fA-F]{64})`")
# 与 executor.expected_dim_keys 同口径的兜底（懒导入失败时用）
_SECTION_DIMS = {
    "rationale": ("innovation", "feasibility", "rigor", "expression"),
    "content": ("innovation", "feasibility", "rigor", "expression"),
    "scheme": ("innovation", "feasibility", "rigor", "expression"),
    "full_review": ("innovation", "feasibility", "rigor", "expression"),
    "references": ("rigor", "completeness"),
}

# 与 proposal_lifecycle.optimize._ISSUE_NOISE_PAT 同款噪声过滤
_ISSUE_NOISE_PAT = re.compile(
    r"^\s*(\||#|>|---|```)"
    r"|红线抑制校验|纪律：|强制.*区间|评分块|综合评分"
    r"|执行清单|对照.*通过|不通过.*\||锚点对比结论"
)


# ---------------------------------------------------------------------------
# 报告解析（容错多种书写）
# ---------------------------------------------------------------------------

def _strip_line(line: str) -> str:
    """去掉加粗标记，便于统一匹配。"""
    return line.replace("**", "")


_DIM_LABELS = (("严谨性", "rigor"), ("就绪度", "readiness"))


def _dim_segments(line: str) -> List[Tuple[str, str]]:
    """按维度标签切段（"手册就绪度"不算"就绪度"标签；段在"综合/手册就绪度"
    处截断，防止吞掉行内后续的综合分与锚定表述），段内取末值由调用方做。"""
    marks: List[Tuple[int, str, str]] = []
    for lab, key in _DIM_LABELS:
        for m in re.finditer(lab, line):
            if lab == "就绪度" and line.rfind("手册", 0, m.start()) == m.start() - 2:
                continue
            marks.append((m.start(), lab, key))
    marks.sort()
    out: List[Tuple[str, str]] = []
    for i, (pos, lab, key) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(line)
        body_start = pos + len(lab)
        cut = re.search(r"综合|手册就绪度", line[body_start:end])
        if cut:
            end = body_start + cut.start()
        out.append((key, line[pos:end]))
    return out


def parse_manual_report(text: str) -> Dict[str, Any]:
    """解析手册评审报告的评分块。

    解析规则（v7.3.45 实测校准）：
    - 跳过 blockquote 行（`>` 开头）——常是旧轮数值引用，非本评审结论；
    - 综合分：全篇**最后一条** `综合(评分)? + 数字` 行胜出（终评在文末），
      行内取最左匹配；
    - 维度分：按标签切段、段内取**最后一个** 0.x 数值（兼容"0.86→0.87"
      修订式与"（③0.90+⑤0.91+⑧0.91）/3 = 0.91"算式），全篇末次出现胜出；
    - 就绪度分级：优先"手册就绪度"行，兜底"就绪度等级/等级维持"行。

    Returns:
        {"score": float, "dims": {rigor, readiness}, "level": int,
         "contract_ok": bool, "warnings": [str]}
    """
    warnings: List[str] = []
    score = 0.0
    dims: Dict[str, float] = {}
    level = -1
    contract_score = contract_dims = contract_level = False
    level_fallback_hit = False

    for raw in text.splitlines():
        line = _strip_line(raw).strip()
        if not line or line.startswith(">"):
            continue
        # 就绪度分级：主（手册就绪度行）→ 兜底（等级/就绪度等级行）
        if "手册就绪度" in line:
            m = re.search(r"L\s*([0-4])", line)
            if m:
                level = int(m.group(1))
                level_fallback_hit = False
                contract_level = contract_level or bool(
                    re.search(r"手册就绪度[：:]\s*L", line))
        elif level_fallback_hit is False and re.search(
                r"(?:就绪度等级|等级维持|等级[：:]|判定[：:])", line):
            m = re.search(r"L\s*([0-4])", line)
            if m:
                level = int(m.group(1))
                level_fallback_hit = True
        # 综合分：最后一条匹配行胜出
        m = re.search(r"综合(?:评分)?[：:|\s]*\(?(0\.\d+)", line)
        if m:
            score = float(m.group(1))
            contract_score = contract_score or bool(
                re.search(r"综合评分[：:]", line))
        # 维度分：切段取末值，末次出现胜出
        for key, seg in _dim_segments(line):
            nums = re.findall(r"0\.\d+", seg)
            if nums:
                dims[key] = float(nums[-1])
                contract_dims = contract_dims or bool(
                    re.search(r"(严谨性|就绪度)[：:]", line))

    if score == 0.0:
        warnings.append("未解析到综合评分")
    if len(dims) < 2:
        warnings.append("维度分解析不全（需 rigor+readiness）")
    if level < 0:
        warnings.append("未解析到手册就绪度分级（L0-L4）")
    contract_ok = contract_score and contract_dims and contract_level
    if not contract_ok and score > 0:
        warnings.append(
            "评分块非契约纯文本格式（加粗/表格），管线原生解析链将读不到分——"
            "请评审产出方对齐报告输出契约"
        )
    return {"score": score, "dims": dims, "level": level,
            "contract_ok": contract_ok, "warnings": warnings}


def count_blocking_issues(text: str) -> int:
    """统计未闭环 critical/high 问题行（与 optimize._extract_issues 同口径）。"""
    out = 0
    seen = set()
    for raw in text.split("\n"):
        stripped = raw.strip()
        if len(stripped) < 20 or _ISSUE_NOISE_PAT.search(stripped):
            continue
        for sev in ("critical", "high"):
            if f"[{sev}]" in stripped or f"（{sev}）" in stripped:
                key = stripped[:80]
                if key not in seen:
                    seen.add(key)
                    out += 1
                break
    return out


# ---------------------------------------------------------------------------
# 过线判定与回填
# ---------------------------------------------------------------------------

def min_score_for(project_type: str) -> float:
    """按项目类型取达标线（与 optimize._get_quality_threshold 同口径）。"""
    standards = load_json(STANDARDS, default={}) or {}
    t = (standards.get("project_types") or {}).get(project_type) or {}
    qt = t.get("quality_threshold") or {}
    try:
        return float(qt.get("min_overall_score", 0.90))
    except (TypeError, ValueError):
        return 0.90


def judge_pass(parsed: Dict[str, Any], project_type: str,
               manual_bytes: int, blocking_issues: int) -> Tuple[bool, str]:
    """与 _run_manual_writer_step 同口径的过线判定。"""
    line = min_score_for(project_type)
    if parsed["score"] <= 0:
        return False, f"报告分不可解析（线 {line:.2f}）"
    if parsed["score"] < line:
        return False, f"报告分 {parsed['score']:.2f} < 达标线 {line:.2f}"
    if blocking_issues > 0:
        return False, f"存在 {blocking_issues} 条 critical/high 问题行"
    for k, v in parsed["dims"].items():
        if v < MANUAL_DIM_FLOOR:
            return False, f"维度 {k}={v:.2f} < 短板线 {MANUAL_DIM_FLOOR:.2f}"
    if len(parsed["dims"]) < 2:
        return False, "维度分不全（rigor+readiness）"
    if parsed["level"] < MANUAL_READY_LEVEL:
        return False, f"就绪度 L{parsed['level']} < L{MANUAL_READY_LEVEL}"
    if manual_bytes < MANUAL_MIN_BYTES:
        return False, f"手册体积 {manual_bytes}B < {MANUAL_MIN_BYTES}B"
    return True, f"过线（{parsed['score']:.2f} ≥ {line:.2f}，L{parsed['level']}）"


def latest_manual_report(pdir: Path) -> Optional[Tuple[int, Path]]:
    """最新一份 method_manual 评审报告（按文件修改时间——跨生命周期世代的
    轮号不可比：旧世代 r4 可能早于本轮重置后的 r1）。"""
    rev = pdir / "05_review"
    if not rev.exists():
        return None
    best: Optional[Tuple[int, Path]] = None
    best_mtime = -1.0
    for f in rev.glob("critic-round-*-method_manual.md"):
        m = re.fullmatch(r"critic-round-(\d+)-method_manual\.md", f.name)
        if not m or f.stat().st_size <= 100:
            continue
        mt = f.stat().st_mtime
        if mt > best_mtime:
            best_mtime = mt
            best = (int(m.group(1)), f)
    return best


def _sha256_of(path: Path) -> str:
    """流式计算文件 sha256（与报告头“评审时 sha256”同口径）。"""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_report_sha(text: str) -> str:
    """取报告头的评审时 sha256（缺失或格式不符返回空串）。"""
    m = _SHA_PAT.search(text)
    return m.group(1).lower() if m else ""


def latest_section_report(pdir: Path, section: str) -> Optional[Path]:
    """某章节最新一份终评报告（按修改时间；同世代 final/final2 取最新）。"""
    rev = pdir / "05_review"
    if not rev.exists():
        return None
    best: Optional[Path] = None
    best_mtime = -1.0
    for f in rev.glob(f"critic-*-{section}.md"):
        try:
            if f.stat().st_size <= 100:
                continue
            mt = f.stat().st_mtime
        except OSError:
            continue
        if mt > best_mtime:
            best_mtime = mt
            best = f
    return best


def _dims_partial(section: str, dims: Dict[str, float]) -> bool:
    """维度是否解析不全（优先复用 executor.judge_dims_partial）。"""
    try:
        # 懒导入：默认手册模式与 --self-check 不加载重量级执行器依赖
        from lifecycle.executor import judge_dims_partial
        partial, _present, _missing = judge_dims_partial(section, dims)
        return bool(partial)
    except Exception:  # pragma: no cover - 与 executor 口径的兜底
        expected = set(_SECTION_DIMS.get(section, ()))
        return bool(expected - set(dims or {}))


def _current_round(ps: Dict[str, Any]) -> int:
    """取当前轮次：显式 current_round → 管线 job 最大轮 → 历史最大轮。"""
    cr = ps.get("current_round")
    if isinstance(cr, int) and cr > 0:
        return cr
    rounds = [j.get("round") for j in (ps.get("pipeline_jobs") or [])
              if isinstance(j, dict) and isinstance(j.get("round"), int)]
    if rounds:
        return max(rounds)
    hist = [h.get("round") for h in (ps.get("score_history") or [])
            if isinstance(h, dict) and isinstance(h.get("round"), int)]
    return max(hist) if hist else 1


def backfill_sections(lifecycle: Dict[str, Any], apply: bool,
                      only_pid: Optional[str] = None) -> List[Dict[str, Any]]:
    """章节终评报告 → 账本：sha256 闸门校验后写 score_history 与
    section_scores_20261107；**不覆盖 last_score / section_passes**。"""
    from proposal_lifecycle import ProposalLifecycle

    lc = ProposalLifecycle()
    results: List[Dict[str, Any]] = []
    for pid, ps in (lifecycle.get("proposals") or {}).items():
        if not isinstance(ps, dict) or ps.get("status") != "optimizing":
            continue
        if only_pid and pid != only_pid:
            continue
        pdir = PROPOSAL_ROOT / "optimizing" / pid
        if not pdir.exists():
            continue

        history = ps.get("score_history") or []
        known = {h.get("report") for h in history
                 if isinstance(h, dict)
                 and h.get("source") == SOURCE_TAG_SECTIONS}
        rnd = _current_round(ps)
        line = min_score_for(ps.get("project_type", "general"))
        floor = getattr(lc, "DIMENSION_FLOOR", {}) or {}

        entries: List[Dict[str, Any]] = []
        sections: Dict[str, Any] = {}
        problems: List[str] = []
        skips: List[str] = []
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for sec in SECTION_KEYS:
            report = latest_section_report(pdir, sec)
            if report is None:
                problems.append(f"{sec}：无对应终评报告")
                continue
            rel = str(report.relative_to(PROPOSAL_ROOT))
            if rel in known:
                skips.append(f"{sec}：{report.name} 已入史，幂等跳过")
                continue
            try:
                text = report.read_text(encoding="utf-8", errors="ignore")
            except OSError as e:
                problems.append(f"{sec}：报告读取失败 {e}")
                continue

            body_path = pdir / "04_proposal" / "sections" / f"{sec}.md"
            if not body_path.exists():
                problems.append(f"{sec}：正文文件缺失 {body_path.name}")
                continue
            body_sha = _sha256_of(body_path)
            head_sha = parse_report_sha(text)
            if not head_sha:
                problems.append(f"{sec}：{report.name} 报告头无评审时 sha256")
                continue
            if head_sha != body_sha:
                problems.append(
                    f"{sec}：sha256 不一致（报告 {head_sha[:12]}… / "
                    f"正文 {body_sha[:12]}…）"
                )
                continue

            score = lc._extract_score({"output": text})
            dims = lc._extract_dimension_scores({"output": text})
            issues = lc._extract_issues({"output": text})
            blocking = count_blocking_issues(text)
            if score <= 0 or not dims:
                problems.append(
                    f"{sec}：分数/维度解析失败（score={score}, dims={dims}）"
                )
                continue
            partial = _dims_partial(sec, dims)
            weak = [k for k, f in floor.items() if k in dims and dims[k] < f]
            passed = (score >= line and not weak
                      and blocking == 0 and not partial)
            caliber = "references_2d" if sec == "references" else "section_4d"
            entry = {
                "round": rnd,
                "score": score,
                "score_raw": None if sec == "references" else score,
                "dim_scores": dims,
                "weakest_dim": min(dims, key=dims.get) if dims else None,
                "focus_section": sec,
                "section_passed": passed,
                "issues_count": len(issues),
                "high_issues": blocking,
                "caliber": caliber,
                "dims_partial": partial,
                "dims_present": not partial,
                "anchor_conclusion": "",
                "source": SOURCE_TAG_SECTIONS,
                "report": rel,
                "backfilled_at": stamp,
                "at": stamp,
            }
            entries.append(entry)
            sections[sec] = {
                "score": score,
                "dims": dims,
                "section_passed": passed,
                "weak_dims": weak,
                "blocking_issues": blocking,
                "caliber": caliber,
                "report": rel,
                "sha256": body_sha,
            }

        if problems:
            results.append({"pid": pid, "action": "abort",
                            "problems": problems, "skipped": skips})
            continue

        if not entries:
            results.append({"pid": pid, "action": "skip",
                            "detail": "全部章节已入史（幂等）"
                                      if skips else "无可用章节报告"})
            continue

        chapter_scores = [v["score"] for k, v in sections.items()
                          if k != "references"]
        aggregate = {
            "min": round(min(chapter_scores), 4) if chapter_scores else 0.0,
            "mean_section_4d": (round(sum(chapter_scores) / len(chapter_scores), 4)
                                if chapter_scores else 0.0),
            "critical": sum(1 for v in sections.values()
                            if v["blocking_issues"] > 0),
            "high": sum(1 for v in sections.values() if v["blocking_issues"] > 0),
        }
        block = {
            "review_date": "2026-11-07",
            "caliber": "章节 section_4d / 参考文献 references_2d",
            "sections": sections,
            "aggregate": aggregate,
            "gate_note": ("section_passes 布尔未改动，保留至 11-09 人工判门；"
                          "自动晋级仍被 monitor 0.81 < 0.85 阻断。"),
        }
        results.append({"pid": pid, "action": "backfill" if apply else "would",
                        "round": rnd, "sections": sections,
                        "aggregate": aggregate, "skipped": skips,
                        "entries": entries})
        if apply:
            prev = ps.get("last_score")
            history.extend(entries)
            ps["score_history"] = history
            ps["last_score_prev"] = prev
            ps["last_score_caliber"] = (
                f"{prev} 为轮次 {rnd} 单章节 writer 步写入的该章 critic 加权分"
                "（scripts/lifecycle/executor.py:1832），非五章聚合、"
                "不含 monitor 加权；与 section_scores_20261107 不可直接比较。"
            )
            ps["section_scores_20261107"] = block
            ps["updated_at"] = stamp
    return results


def backfill(lifecycle: Dict[str, Any], apply: bool,
             only_pid: Optional[str] = None) -> List[Dict[str, Any]]:
    """扫描并（apply=True 时）回填；返回逐课题结果供 dry-run 预览。"""
    results: List[Dict[str, Any]] = []
    for pid, ps in (lifecycle.get("proposals") or {}).items():
        if not isinstance(ps, dict) or ps.get("status") != "optimizing":
            continue
        if only_pid and pid != only_pid:
            continue
        pdir = PROPOSAL_ROOT / "optimizing" / pid
        if not pdir.exists():
            continue
        found = latest_manual_report(pdir)
        if not found:
            results.append({"pid": pid, "action": "skip",
                            "detail": "无 method_manual 评审报告"})
            continue
        rnd, report = found
        history = ps.get("score_history") or []
        known_rounds = [
            h.get("round") for h in history
            if isinstance(h, dict) and h.get("focus_section") == "method_manual"
        ]
        if known_rounds and rnd <= max(known_rounds):
            results.append({"pid": pid, "action": "skip",
                            "detail": f"r{rnd} 已入史（最大已录轮次 "
                                      f"{max(known_rounds)}），幂等跳过"})
            continue
        try:
            text = report.read_text(encoding="utf-8", errors="ignore")
        except OSError as e:
            results.append({"pid": pid, "action": "skip",
                            "detail": f"报告读取失败：{e}"})
            continue
        parsed = parse_manual_report(text)
        manual_path = pdir / "03_method" / "method-manual.md"
        manual_bytes = manual_path.stat().st_size if manual_path.exists() else 0
        blocking = count_blocking_issues(text)
        passed, reason = judge_pass(parsed, ps.get("project_type", "general"),
                                    manual_bytes, blocking)
        entry = {
            "round": rnd,
            "score": parsed["score"],
            "score_raw": None,
            "dim_scores": parsed["dims"],
            "weakest_dim": (min(parsed["dims"], key=parsed["dims"].get)
                            if parsed["dims"] else None),
            "focus_section": "method_manual",
            "section_passed": passed,
            "issues_count": blocking,
            "high_issues": blocking,
            "manual_readiness_level": parsed["level"],
            "manual_bytes": manual_bytes,
            "manual_actions_applied": 0,
            "caliber": "manual_2d",
            "dims_partial": len(parsed["dims"]) < 2,
            "dims_present": len(parsed["dims"]) == 2,
            "anchor_conclusion": "",  # 手册为操作文档，语体锚点不适用
            "source": SOURCE_TAG,
            "report": str(report.relative_to(PROPOSAL_ROOT)),
            "backfilled_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"),
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        results.append({"pid": pid, "action": "backfill" if apply else "would",
                        "round": rnd, "passed": passed, "reason": reason,
                        "score": parsed["score"], "level": parsed["level"],
                        "warnings": parsed["warnings"], "entry": entry})
        if apply:
            history.append(entry)
            ps["score_history"] = history
            sp = ps.get("section_passes") or {}
            sp["method_manual"] = passed
            ps["section_passes"] = sp
            ps["updated_at"] = entry["at"]
    return results


def _print_sections(results: List[Dict[str, Any]], applied: bool) -> int:
    """章节模式结果打印；返回码 0=无中止，1=有章节被中止。"""
    n_ok = n_skip = n_abort = 0
    for r in results:
        action = r.get("action")
        if action in ("backfill", "would"):
            n_ok += 1
            verb = "已回填" if action == "backfill" else "将回填"
            print(f"✓ {r['pid']}  r{r.get('round')}  五章终评 → {verb}")
            for sec, v in (r.get("sections") or {}).items():
                icon = "✓" if v.get("section_passed") else "⚠"
                print(f"  {icon} {sec:<12} score={v['score']:.2f} "
                      f"dims={v['dims']} sha={v['sha256'][:12]}…")
            agg = r.get("aggregate") or {}
            print(f"  聚合：min={agg.get('min')} "
                  f"mean_section_4d={agg.get('mean_section_4d')} "
                  f"critical={agg.get('critical')} high={agg.get('high')}")
            for s in r.get("skipped") or []:
                print(f"  ○ {s}")
        elif action == "abort":
            n_abort += 1
            print(f"✗ {r['pid']}  中止（不写盘）：")
            for p in r.get("problems") or []:
                print(f"  ✗ {p}")
        else:
            n_skip += 1
            print(f"○ {r['pid']}  跳过：{r.get('detail')}")
    mode = "已回填" if applied else "预演（--apply 生效）"
    print(f"—— {mode}：回填 {n_ok} / 跳过 {n_skip} / 中止 {n_abort}")
    return 0 if n_abort == 0 else 1


def _self_check() -> bool:
    ok = True
    # 1) 契约纯文本格式
    t1 = "## 评分\n严谨性：0.75\n就绪度：0.80\n综合评分：0.78\n手册就绪度：L2\n"
    p1 = parse_manual_report(t1)
    ok1 = (p1["score"] == 0.78 and p1["dims"] == {"rigor": 0.75,
           "readiness": 0.80} and p1["level"] == 2 and p1["contract_ok"])
    # 2) 加粗行格式（ssh-weyl 实测样式）
    t2 = ("- 严谨性：**0.88**（说明）\n- 就绪度：**0.91**（说明）\n"
          "- 综合：**0.89**（≥0.85 门槛）。\n- 手册就绪度：**L3**（未达 L4 因…）\n")
    p2 = parse_manual_report(t2)
    ok2 = (p2["score"] == 0.89 and p2["dims"] == {"rigor": 0.88,
           "readiness": 0.91} and p2["level"] == 3 and not p2["contract_ok"])
    # 3) 表格行格式（attosecond 实测样式）
    t3 = ("| 严谨性（rigor） | 0.90 | 说明 |\n| 就绪度（readiness） | 0.88 | 说明 |\n"
          "| 综合 | **0.89** | ≥0.85；无 critical / high 残留 |\n"
          "| 手册就绪度分级 | **L3** | 说明 |\n")
    p3 = parse_manual_report(t3)
    ok3 = (p3["score"] == 0.89 and p3["dims"] == {"rigor": 0.90,
           "readiness": 0.88} and p3["level"] == 3 and not p3["contract_ok"])
    # 4) blockquote 旧轮引用跳过 + 算式段取末值（order-param 实测样式）
    t4 = ("> 第 2 轮原报告只给综合分（严谨性 0.62 / 就绪度 0.66 / 综合 0.64）。\n"
          "**综合**：严谨性 =（③0.90 + ⑤0.91 + ⑧0.91）/3 = **0.91**；"
          "就绪度 = 八项均值 **0.91**；综合 **0.91**。\n"
          "严谨性：0.91\n就绪度：0.91\n综合评分：0.91\n手册就绪度：L4\n")
    p4 = parse_manual_report(t4)
    ok4 = (p4["score"] == 0.91 and p4["dims"] == {"rigor": 0.91,
           "readiness": 0.91} and p4["level"] == 4)
    # 5) 修订式 "0.86→0.87" 段内取末值 + "等级维持" 兜底（berry 实测样式）
    t5 = ("| 综合分 | **0.87**（严谨性 0.86 / 就绪度 0.88） |\n"
          "| 就绪度等级 | **L3（可开工）** |\n"
          "**复评结果**：严谨性 0.86→0.87、就绪度 0.88→0.89，**综合 0.88**。"
          "综合未达 L4 的 0.90+ 锚，等级维持 **L3**。critical 0 / high 0 不变。\n")
    p5 = parse_manual_report(t5)
    ok5 = (p5["score"] == 0.88 and p5["dims"] == {"rigor": 0.87,
           "readiness": 0.89} and p5["level"] == 3)
    # 6) 过线判定：general 0.85 过 / key 0.90 不过
    passed_g, _ = judge_pass(p2, "general", 58000, 0)
    passed_k, _ = judge_pass(p2, "key", 58000, 0)
    ok6 = passed_g and not passed_k
    # 7) 有 critical 问题行不过
    passed_i, _ = judge_pass(p2, "general", 58000, 2)
    ok7 = not passed_i
    # 8) 问题行计数：契约行收、表格行不收
    n1 = count_blocking_issues("- [critical]｜要素①｜§2｜缺口说明文字足够长认证有效行\n")
    n2 = count_blocking_issues("| [high] | 表格行不收 |\n短行\n")
    ok8 = n1 == 1 and n2 == 0
    # 9) 章节模式：sha 闸门 + 评分块解析（临时目录，零落盘）
    import tempfile
    ok9 = False
    with tempfile.TemporaryDirectory() as td:
        sp = Path(td) / "rationale.md"
        sp.write_text("# 正文\n", encoding="utf-8")
        sha = _sha256_of(sp)
        rep = (f"# 终评\n\n- 评审时 sha256：`{sha}`\n\n## 评分\n"
               "创新性：0.84\n可行性：0.85\n严谨性：0.90\n表达质量：0.79\n"
               "综合评分：0.85\n")
        ok9 = parse_report_sha(rep) == sha and parse_report_sha("无 sha 头") == ""
        try:
            from proposal_lifecycle import ProposalLifecycle
            lc = ProposalLifecycle()
            sc = lc._extract_score({"output": rep})
            dm = lc._extract_dimension_scores({"output": rep})
            ok9 = (ok9 and sc == 0.85 and len(dm) == 4
                   and dm.get("innovation") == 0.84
                   and dm.get("expression") == 0.79)
        except Exception:
            ok9 = False
    # 10) 维度完整性：references 需 rigor+completeness 两维
    ok10 = (_dims_partial("references",
                          {"rigor": 0.90, "completeness": 0.90}) is False
            and _dims_partial("references", {"rigor": 0.90}) is True)
    for i, o in enumerate((ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8, ok9, ok10), 1):
        print(f"{'✓' if o else '✗'} 自检 {i}")
        ok = ok and o
    return ok


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="手册复评回流生命周期状态")
    ap.add_argument("--dry-run", action="store_true", help="只预览，不落盘")
    ap.add_argument("--apply", action="store_true", help="备份后写盘")
    ap.add_argument("--proposal", default=None, help="只处理指定课题")
    ap.add_argument("--sections", action="store_true",
                    help="章节终评回流：5 章 sha256 校验，不覆盖 last_score")
    ap.add_argument("--self-check", action="store_true", help="运行内置自检")
    args = ap.parse_args(argv)
    if args.self_check:
        return 0 if _self_check() else 1
    if not (args.dry_run or args.apply):
        ap.print_help()
        return 2

    runner = backfill_sections if args.sections else backfill
    data = load_json(LIFECYCLE, default={"proposals": {}})
    if args.dry_run:
        results = runner(json.loads(json.dumps(data)), apply=False,
                         only_pid=args.proposal)
    else:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        suffix = "sections" if args.sections else "manual"
        backup = LIFECYCLE.with_name(f"_lifecycle.json.bak-{suffix}-{ts}")
        shutil.copy2(LIFECYCLE, backup)
        with file_lock("proposal-lifecycle"):
            results = runner(data, apply=True, only_pid=args.proposal)
            save_json(LIFECYCLE, data)
        print(f"✓ 备份：{backup.name}")

    if args.sections:
        return _print_sections(results, args.apply)

    n_back = n_skip = 0
    for r in results:
        if r["action"] in ("backfill", "would"):
            n_back += 1
            icon = "✓" if r.get("passed") else "⚠"
            print(f"{icon} {r['pid']}  r{r.get('round')} "
                  f"score={r.get('score'):.2f} L{r.get('level')} "
                  f"→ {'回填' if r['action'] == 'backfill' else '将回填'}"
                  f"（{r.get('reason')}）")
            for w in r.get("warnings") or []:
                print(f"  ⚠ {w}")
        else:
            n_skip += 1
            print(f"○ {r['pid']}  跳过：{r.get('detail')}")
    mode = "已回填" if args.apply else "预演（--apply 生效）"
    print(f"—— {mode}：回填 {n_back} / 跳过 {n_skip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
