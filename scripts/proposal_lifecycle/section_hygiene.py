#!/usr/bin/env python3
"""
section_hygiene.py — 章节卫生：字数预算预检 + full_review 骨架化 + references 工作日志清洗

v6.9.53 背景：分章节评审只限制了"单次评审读哪些章节"，没有限制章节本身的
体量。三类膨胀导致大输入 × API 慢速 = 超时（08-27 实证超时率 44%）：

    1. full_review.md 定位错位——writer 把"一致性核查记录"（round-N 修复
       确认表、逐项核查对照）当正文写进章节文件（qg 33KB / moire 25KB /
       order-param 23KB）。真实 NSFC 申请书没有"整体一致性审查"章节。
    2. references.md 存量污染回归——moire/order-param 各 28KB，内含
       [CITE:xxx] 映射表与核实声明（v6.9.46 红线之前的存量，无人清理）。
    3. 正文章节无长度预算——writer 逐条响应 critic 问题只追加不删减，
       kt-rationale 11364 字 / qg-scheme 10900 字 / qg-content 10412 字，
       远超 NSFC 各章节正常体量。

本模块提供：
    - SECTION_BUDGETS：各章节中文字数预算（与 nsfc-standards 对齐）
    - budget_report_text()：字数预算预检文本（附入 critic/writer prompt）
    - full_review_purity_text()：full_review.md 纯净性预检文本
    - migrate_full_review_record()：一次性清洗——核查记录迁 05_review/，
      full_review.md 重生成为"全文逻辑骨架"（≤3KB）
    - strip_references_worklog()：一次性清洗——剥离 references.md 中的
      工作日志段落（映射表/核实声明/闭环证据），迁 05_review/

用法示例：
    python3 scripts/proposal_lifecycle/section_hygiene.py --dry-run  # 全部课题预览
    python3 scripts/proposal_lifecycle/section_hygiene.py --apply    # 执行清洗
    python3 scripts/proposal_lifecycle/section_hygiene.py --self-check
"""

from __future__ import annotations

import re
import sys
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# 支持包内导入与独立 CLI 双模式
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# 预算与阈值
# ---------------------------------------------------------------------------

# 各章节中文字数预算（min, max）。依据 NSFC 面上/青年正文 30 页三段式改革
# 与范本体量校准：rationale 既有标准 5000-8000；content/scheme 为新增预算
# （08-27 实测膨胀样本 kt-rationale 11364 / qg-scheme 10900 / qg-content 10412）。
SECTION_BUDGETS: Dict[str, Tuple[int, int]] = {
    "rationale": (5000, 8000),
    "content": (4000, 7000),
    "scheme": (6000, 10000),
}

# full_review.md 是"全文逻辑骨架"，不是核查记录，上限 3000 字
FULL_REVIEW_MAX_CHARS = 3000
# references.md 纯文献列表正常体量（35 条约 8-12KB），超此值视为污染
REFERENCES_BLOAT_BYTES = 25 * 1024

SECTION_CN = {
    "rationale": "立项依据",
    "content": "研究内容",
    "scheme": "研究方案",
    "full_review": "全文逻辑骨架",
    "references": "参考文献",
}

# full_review.md 中的工作记录特征（round 引用 / 修复确认 / 逐项核查）
WORKLOG_PATTERNS = [
    r"round[-\s]?\d",
    r"第\s*\d+\s*轮",
    r"已修复确认",
    r"修复确认",
    r"本轮评审",
    r"writer.{0,6}critic",
    r"评审报告\s*§",
    r"闭环证据",
    r"核校日志",
    r"核实声明",
    r"§D",
    r"§E",
    r"§F",
]

# references.md 中应剥离的段落标题特征
REF_WORKLOG_HEADERS = [
    "映射表",
    "核实声明",
    "闭环",
    "核校",
    "工作日志",
    "证据索引",
    "修复声明",
    "引用挂钩总表",
    "引用映射",
    "§D",
    "§E",
    "§F",
]


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _date_tag() -> str:
    return datetime.now().strftime("%Y%m%d")


def _cn_chars(text: str) -> int:
    """统计中文字符数（章节体量的主口径）。"""
    return len(re.findall(r"[\u4e00-\u9fff]", text))


# ---------------------------------------------------------------------------
# ① 字数预算预检（零 LLM，附入 prompt）
# ---------------------------------------------------------------------------

def budget_report(sections_dir: Path) -> Dict[str, Dict[str, int]]:
    """统计各正文章节中文字数并比对预算。

    Returns:
        {section: {"chars": N, "min": M, "max": K, "status": ok|over|under}}
    """
    report: Dict[str, Dict[str, int]] = {}
    for sec, (lo, hi) in SECTION_BUDGETS.items():
        p = sections_dir / f"{sec}.md"
        if not p.exists():
            continue
        n = _cn_chars(p.read_text(encoding="utf-8"))
        status = "ok" if lo <= n <= hi else ("over" if n > hi else "under")
        report[sec] = {"chars": n, "min": lo, "max": hi, "status": status}
    return report


def budget_report_text(sections_dir: Path, focus_key: Optional[str] = None) -> str:
    """生成字数预算预检文本（critic 直接采信 / writer 量化指令）。"""
    rep = budget_report(sections_dir)
    if not rep:
        return ""
    lines = ["【章节字数预算预检（程序完成，请直接采信）】"]
    for sec, r in rep.items():
        mark = "✓" if r["status"] == "ok" else ("⚠超限" if r["status"] == "over" else "○偏短")
        lines.append(
            f"- {SECTION_CN.get(sec, sec)}：{r['chars']} 字（预算 {r['min']}-{r['max']}）{mark}"
        )
    over = [s for s, r in rep.items() if r["status"] == "over"]
    if over:
        lines.append(
            "超限章节必须压缩重写（critical）：删并重复论证、去冗余修饰、"
            "细节下沉方法学手册，把逐条响应式追加改为改写。禁止再追加新内容。"
        )
    if focus_key and focus_key in rep:
        r = rep[focus_key]
        if r["status"] == "over":
            lines.append(
                f"聚焦章节量化指令：{SECTION_CN.get(focus_key, focus_key)} 当前 {r['chars']} 字，"
                f"本轮必须削减至 ≤{r['max']} 字（净删 ≥{r['chars'] - r['max']} 字）。"
            )
        elif r["status"] == "under":
            lines.append(
                f"聚焦章节偏短：{SECTION_CN.get(focus_key, focus_key)} 当前 {r['chars']} 字，"
                f"预算下限 {r['min']} 字，需补足论证而非注水。"
            )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# ② full_review.md 纯净性预检
# ---------------------------------------------------------------------------

def full_review_purity_text(prop_dir: Path) -> str:
    """检查 full_review.md 是否被核查记录污染（零 LLM）。"""
    p = prop_dir / "04_proposal" / "sections" / "full_review.md"
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8")
    size = len(text.encode("utf-8"))
    cn = _cn_chars(text)
    hits: List[str] = []
    for pat in WORKLOG_PATTERNS:
        found = re.findall(pat, text, re.I)
        if found:
            hits.append(f"{pat}×{len(found)}")
    lines = []
    if size > FULL_REVIEW_MAX_CHARS * 3 // 2 or cn > FULL_REVIEW_MAX_CHARS or hits:
        lines.append("【full_review.md 纯净性告警（程序检测，按 critical 处置）】")
        lines.append(f"- 体量：{size // 1024}KB / {cn} 字（骨架上限 {FULL_REVIEW_MAX_CHARS} 字）")
        if hits:
            lines.append(f"- 工作记录特征命中：{'; '.join(hits[:8])}")
        lines.append(
            "- full_review.md 只保留'全文逻辑骨架'（主线论证链 + 章节衔接点 + 统一口径表），"
            "核查过程记录属 05_review/ 域。本轮必须将其迁移出去并重写为骨架。"
        )
    return ("\n".join(lines) + "\n") if lines else ""


# ---------------------------------------------------------------------------
# ③ full_review 骨架生成与一次性迁移
# ---------------------------------------------------------------------------

def generate_skeleton(sections_dir: Path) -> str:
    """从三个正文章节提取标题层级，生成全文逻辑骨架。"""
    lines = [
        "# 全文逻辑骨架",
        "",
        "> 本文件是申请书的论证骨架索引（程序维护）。过程性材料",
        "> （对照表、处置记录、轮次说明）一律写入 05_review/，不进入本文件。",
        "",
    ]
    for sec in ("rationale", "content", "scheme"):
        p = sections_dir / f"{sec}.md"
        if not p.exists():
            continue
        lines.append(f"## {SECTION_CN[sec]}（{sec}.md）")
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if re.match(r"^#{2,4}\s+\S", s) and not s.startswith("# "):
                # 压缩为一级列表项，保持骨架紧凑
                title = re.sub(r"^#+\s*", "", s)
                indent = {"##": "- ", "###": "  - ", "####": "    - "}.get(s.split()[0], "- ")
                lines.append(f"{indent}{title[:60]}")
        lines.append("")
    skeleton = "\n".join(lines)
    # 超预算时截断到标题层级的前半（骨架只降不升）
    return skeleton[: FULL_REVIEW_MAX_CHARS * 2]


def migrate_full_review_record(prop_dir: Path, dry_run: bool = False) -> Optional[str]:
    """一次性清洗：full_review.md 核查记录迁 05_review/，原位重生骨架。

    Returns:
        迁移产物路径（dry_run 时为预览标记），未触发返回 None。
    """
    sec_dir = prop_dir / "04_proposal" / "sections"
    fr = sec_dir / "full_review.md"
    if not fr.exists():
        return None
    text = fr.read_text(encoding="utf-8")
    cn = _cn_chars(text)
    hit = any(re.findall(pat, text, re.I) for pat in WORKLOG_PATTERNS)
    if cn <= FULL_REVIEW_MAX_CHARS and not hit:
        return None  # 已是干净骨架，无需处理

    review_dir = prop_dir / "05_review"
    out = review_dir / f"full-review-record-{_date_tag()}.md"
    if dry_run:
        return f"(dry-run) {out.name} ← full_review.md {cn}字记录迁移 + 骨架重写"

    review_dir.mkdir(parents=True, exist_ok=True)
    header = (
        f"<!-- v6.9.53 从 04_proposal/sections/full_review.md 迁出的核查记录 -->\n"
        f"<!-- 迁移时间：{_now_utc()}。full_review.md 已重写为全文逻辑骨架。 -->\n\n"
    )
    out.write_text(header + text, encoding="utf-8")
    fr.write_text(generate_skeleton(sec_dir), encoding="utf-8")
    return str(out)


# ---------------------------------------------------------------------------
# ④ references.md 工作日志剥离（一次性）
# ---------------------------------------------------------------------------

def _split_by_headers(text: str) -> List[Tuple[str, str]]:
    """按 markdown 二三级标题切段，返回 [(header, body), ...]。

    首段（首个标题之前的内容）header 为空串。
    """
    parts: List[Tuple[str, str]] = []
    cur_header, cur_lines = "", []
    for line in text.splitlines():
        if re.match(r"^#{1,3}\s+\S", line.strip()):
            if cur_lines or cur_header:
                parts.append((cur_header, "\n".join(cur_lines)))
            cur_header, cur_lines = line, []
        else:
            cur_lines.append(line)
    if cur_lines or cur_header:
        parts.append((cur_header, "\n".join(cur_lines)))
    return parts


def strip_references_worklog(prop_dir: Path, dry_run: bool = False) -> Optional[str]:
    """一次性清洗：剥离 references.md 中的工作日志段落，迁 05_review/。

    只剥离"标题命中工作日志特征"的段落与 CITE 映射表行；文献条目、
    条目内挂钩注释、正文说明全部保留。

    Returns:
        迁移产物路径，未触发返回 None。
    """
    sec_dir = prop_dir / "04_proposal" / "sections"
    rp = sec_dir / "references.md"
    if not rp.exists():
        return None
    text = rp.read_text(encoding="utf-8")

    keep: List[str] = []
    moved: List[str] = []
    for header, body in _split_by_headers(text):
        is_worklog = any(k in header for k in REF_WORKLOG_HEADERS) if header.strip() else False
        # 无标题区域内成片的 CITE 映射表行也视为工作日志
        cite_rows = [l for l in body.splitlines() if re.match(r"^\s*\|\s*\[CITE:", l)]
        if is_worklog or (len(cite_rows) >= 3 and not re.search(r"^\[\d+\]", body, re.M)):
            moved.append((header + "\n" + body).strip())
        else:
            keep.append((header + "\n" + body).rstrip())

    if not moved:
        return None
    review_dir = prop_dir / "05_review"
    out = review_dir / f"references-worklog-{_date_tag()}.md"
    if dry_run:
        return f"(dry-run) {out.name} ← 剥离 {len(moved)} 段工作日志（保留文献条目）"

    review_dir.mkdir(parents=True, exist_ok=True)
    header = (
        f"<!-- v6.9.53 从 04_proposal/sections/references.md 剥离的工作日志 -->\n"
        f"<!-- 剥离时间：{_now_utc()}。references.md 仅保留文献条目与条目内注释。 -->\n\n"
    )
    out.write_text(header + "\n\n---\n\n".join(moved), encoding="utf-8")
    rp.write_text("\n\n".join(keep).rstrip() + "\n", encoding="utf-8")
    return str(out)


# ---------------------------------------------------------------------------
# ⑤ 批量入口与 CLI
# ---------------------------------------------------------------------------

def apply_all(project_root: Path, dry_run: bool = False) -> Dict[str, list]:
    """对全部 optimizing 课题执行两类一次性清洗。"""
    opt_dir = project_root / "research_proposals" / "optimizing"
    result = {"full_review": [], "references": []}
    if not opt_dir.exists():
        return result
    for prop_dir in sorted(opt_dir.iterdir()):
        if not (prop_dir / "04_proposal").exists():
            continue
        r1 = migrate_full_review_record(prop_dir, dry_run=dry_run)
        if r1:
            result["full_review"].append({"proposal": prop_dir.name, "out": r1})
        r2 = strip_references_worklog(prop_dir, dry_run=dry_run)
        if r2:
            result["references"].append({"proposal": prop_dir.name, "out": r2})
    return result


def _self_check() -> bool:
    """模块自检：隔离临时目录验证骨架生成 / 迁移 / 剥离 / 预算报告。"""
    tmp = Path(tempfile.mkdtemp())
    try:
        sec = tmp / "04_proposal" / "sections"
        sec.mkdir(parents=True)
        review = tmp / "05_review"

        # 1. 预算报告
        (sec / "rationale.md").write_text("正" * 9000, encoding="utf-8")
        (sec / "content.md").write_text("正" * 5000, encoding="utf-8")
        rep = budget_report(sec)
        assert rep["rationale"]["status"] == "over", "超限章节应标 over"
        assert rep["content"]["status"] == "ok", "预算内章节应标 ok"
        txt = budget_report_text(sec, focus_key="rationale")
        assert "净删" in txt and "削减至" in txt, "量化指令应包含削减目标"

        # 2. full_review 迁移 + 骨架
        (sec / "scheme.md").write_text(
            "# 研究方案\n\n## 总体方案\n正文。\n\n## 技术路线\n正文。\n", encoding="utf-8"
        )
        (sec / "full_review.md").write_text(
            "# 整体一致性核查\n\n## 已修复确认\n经前 5 轮评审修复确认，"
            "本轮 round-6 重新核查未见复发。\n\n| A | B |\n|---|---|\n| 1 | 2 |\n" * 30,
            encoding="utf-8",
        )
        out = migrate_full_review_record(tmp, dry_run=False)
        assert out and Path(out).exists(), "核查记录应迁出"
        fr = (sec / "full_review.md").read_text(encoding="utf-8")
        assert "round-6" not in fr, "骨架不应含工作记录"
        assert "技术路线" in fr, "骨架应含章节标题"
        assert _cn_chars(fr) <= FULL_REVIEW_MAX_CHARS, "骨架应守住字数上限"
        # 干净骨架不再触发迁移
        assert migrate_full_review_record(tmp) is None, "干净骨架应幂等跳过"

        # 3. references 剥离
        entries = "\n".join(
            f"[{i}] Zhang Y., et al. *Some physics paper {i}*. **Nature {i}, 100 (2020).**"
            for i in range(1, 36)
        )
        (sec / "references.md").write_text(
            "# 参考文献\n\n" + entries + "\n\n## §D 引用挂钩映射表\n\n"
            "| [CITE:zhou_2023] | 3 | 8 | 黑磷 Floquet 能带工程 |\n"
            "| [CITE:xu_2023] | 4 | 9 | Floquet 反常霍尔 |\n"
            "| [CITE:cav_2024] | 5 | 10 | 阿秒瞬态吸收 |\n\n"
            "## §E 核实声明\n\n以上条目已逐条核实。\n",
            encoding="utf-8",
        )
        out2 = strip_references_worklog(tmp, dry_run=False)
        assert out2 and Path(out2).exists(), "工作日志应剥离迁出"
        ref = (sec / "references.md").read_text(encoding="utf-8")
        assert "[CITE:" not in ref and "核实声明" not in ref, "文献文件应无工作日志"
        assert "[35]" in ref and "[1]" in ref, "文献条目必须保留"

        # 4. 纯净性预检
        (sec / "full_review.md").write_text("骨架被污染 round-9 修复确认表" * 20, encoding="utf-8")
        purity = full_review_purity_text(tmp)
        assert "critical" in purity and "骨架" in purity, "污染应触发告警"

        print("✓ section_hygiene 自检通过")
        return True
    except AssertionError as e:
        print(f"✗ section_hygiene 自检失败: {e}")
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: List[str]) -> int:
    if "--self-check" in argv:
        return 0 if _self_check() else 1
    project_root = Path(__file__).parent.parent.parent
    dry = "--dry-run" in argv or "--apply" not in argv
    mode = "预览（dry-run）" if dry else "执行（apply）"
    print(f"=== 章节卫生清洗 · {mode} ===")
    result = apply_all(project_root, dry_run=dry)
    for kind, items in result.items():
        print(f"\n[{kind}] 触发 {len(items)} 个课题")
        for it in items:
            print(f"  - {it['proposal']}: {it['out']}")
    if dry and (result["full_review"] or result["references"]):
        print("\n预览无误后执行: python3 scripts/proposal_lifecycle/section_hygiene.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
