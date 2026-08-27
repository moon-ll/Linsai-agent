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
    """生成章节体量上下文文本（v6.9.55 起纯信息性——不作为门限）。

    字数是症状不是判据：本表只提供体量参考，供 writer/critic 定位
    "是否有冗余嫌疑"；真正的拦截与修复指令由质量检测器
    （detect_redundancy / detect_irrelevance）给出。
    """
    rep = budget_report(sections_dir)
    if not rep:
        return ""
    lines = ["【章节体量参考（程序统计，非门限——质量缺陷才是判据）】"]
    for sec, r in rep.items():
        mark = "参考上限之上" if r["status"] == "over" else ("偏短" if r["status"] == "under" else "常规区间")
        lines.append(
            f"- {SECTION_CN.get(sec, sec)}：{r['chars']} 字（参考 {r['min']}-{r['max']}）{mark}"
        )
    over = [s for s, r in rep.items() if r["status"] == "over"]
    if over:
        lines.append(
            "体量超出参考区间的章节应优先排查冗余（重复论证/复述其他章节）"
            "与无关内容——若两类缺陷零命中，属实质性长文，不因字数扣分。"
        )
    if focus_key and focus_key in rep:
        r = rep[focus_key]
        if r["status"] == "under":
            lines.append(
                f"聚焦章节偏短：{SECTION_CN.get(focus_key, focus_key)} 当前 {r['chars']} 字，"
                f"参考下限 {r['min']} 字，需补足论证而非注水。"
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
    # v6.9.59 修复：同日二次迁移改为追加（writer 污染反复复发时，首次
    # 记录不再被覆盖丢失——产出即资产）。
    if out.exists():
        with out.open("a", encoding="utf-8") as f:
            f.write(f"\n\n---\n\n<!-- 追加迁移：{_now_utc()} -->\n\n" + text)
    else:
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
    # v6.9.59 修复：同日二次剥离改为追加，不覆盖首次记录（同上）。
    payload = "\n\n---\n\n".join(moved)
    if out.exists():
        with out.open("a", encoding="utf-8") as f:
            f.write(f"\n\n---\n\n<!-- 追加剥离：{_now_utc()} -->\n\n" + payload)
    else:
        out.write_text(header + payload, encoding="utf-8")
    rp.write_text("\n\n".join(keep).rstrip() + "\n", encoding="utf-8")
    return str(out)


# ---------------------------------------------------------------------------
# ⑥ 写入门卫 + 质量门（v6.9.54 引入，v6.9.55 重构为质量核心）
#
# 设计理念（v6.9.55 校准）：字数是症状，冗余/无关是病因。
# 一个论证密集的 8500 字章节是优质品，一个充满重复论证的 5500 字章节
# 才是劣质品——字数门会误伤前者、放过后者。因此：
#   - guard_written_artifacts：writer 落盘后立即确定性修复结构污染
#     （references 工作日志 / full_review 核查记录），零存活；
#   - quality_gate：拦截的是"质量缺陷"本身——
#       ① 冗余：跨章节重复句（NSFC 评审红线"无跨章节内容重复"）、
#          章节内成片重复论证；
#       ② 无关：与课题核心术语脱钩的成片段落（跑题/复制污染）。
#     字数超限不独立拦截：无冗余命中的超限章节按"实质性长文"放行，
#     有冗余命中时字数并入放大理由。
# ---------------------------------------------------------------------------

# 预算门收敛速率（仅在有冗余命中时用于量化指令）
BUDGET_GATE_REDUCTION_RATIO = 0.10

# 冗余检测阈值
SENT_MIN_CHARS = 20          # 短于 20 字的句子不参与重复判定（易撞车）
CROSS_DUP_EXACT_LIMIT = 1    # 跨章节归一化完全相同句 ≥1 处即拦截
WITHIN_DUP_EXACT_LIMIT = 3   # 章节内完全相同句 ≥3 处才拦截（允许必要强调）
CROSS_DUP_SIM_LIMIT = 2      # 跨章节高相似句（containment>0.85）≥2 处拦截
PARA_MIN_CHARS = 150         # 无关检测只看 >150 字的实质段落
IRRELEVANT_RATIO_LIMIT = 0.25  # 疑似无关段落字数占比 >25% 且成片才拦截

# 英文停用词（核心术语提取时排除）
STOPWORDS_EN = {
    "the", "and", "for", "with", "from", "that", "this", "these", "those",
    "are", "was", "were", "has", "have", "had", "can", "will", "would",
    "using", "used", "use", "based", "which", "into", "such", "than",
    "then", "also", "between", "through", "under", "over", "above",
    "where", "when", "how", "why", "what", "not", "but", "all", "any",
    "one", "two", "three", "each", "other", "more", "most", "some",
    "our", "its", "their", "been", "being", "both", "via", "per",
    "within", "without", "toward", "towards", "among", "across",
}


def guard_written_artifacts(prop_dir: Path) -> Dict[str, Any]:
    """写入门卫：writer 落盘后立即执行确定性修复（幂等）。

    在 executor 判定 writer job 成功之前调用：
    1. references.md 出现工作日志段落 → 剥离迁 05_review/（条目无损）；
    2. full_review.md 出现核查记录/超骨架上限 → 迁 05_review/ 并重写骨架。

    污染从"跨轮存续、事后清理"变为"当轮清除、零存活"。

    Returns:
        {"repaired": [修复描述...], "errors": [异常描述...]}
    """
    result: Dict[str, Any] = {"repaired": [], "errors": []}
    try:
        r1 = migrate_full_review_record(prop_dir, dry_run=False)
        if r1:
            result["repaired"].append(f"full_review 骨架重写（记录迁 {Path(r1).name}）")
    except Exception as e:  # 守卫自身故障不阻塞 job（fail-open + 记录）
        result["errors"].append(f"full_review guard: {e}")
    try:
        r2 = strip_references_worklog(prop_dir, dry_run=False)
        if r2:
            result["repaired"].append(f"references 工作日志剥离（迁 {Path(r2).name}）")
    except Exception as e:
        result["errors"].append(f"references guard: {e}")
    return result


def section_char_count(sections_dir: Path, section_key: str) -> int:
    """读取章节当前中文字数；文件不存在返回 0。"""
    p = sections_dir / f"{section_key}.md"
    if not p.exists():
        return 0
    return _cn_chars(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 质量缺陷检测器（确定性，零 LLM）
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> List[str]:
    """按中英文句读切句，过滤短句。"""
    import re
    raw = re.split(r"[。；？！\n]", text)
    return [s.strip() for s in raw if len(s.strip()) >= SENT_MIN_CHARS]


def _normalize_sentence(s: str) -> str:
    """归一化：仅保留文字与数字（去标点/空白/格式），小写。"""
    import re
    return re.sub(r"[^\w\u4e00-\u9fff]+", "", s).lower()


def _token_set(norm: str) -> set:
    """归一化句的特征集：中文 2-gram + 英文词 + 数字串。"""
    import re
    feats = set()
    # 英文词与数字
    for w in re.findall(r"[a-z0-9]+", norm):
        feats.add(w)
    # 中文 2-gram
    cn = re.findall(r"[\u4e00-\u9fff]", norm)
    for i in range(len(cn) - 1):
        feats.add(cn[i] + cn[i + 1])
    return feats


def _containment(a: set, b: set) -> float:
    """集合包含度：交集 / 较小集合（子串包含场景比 Jaccard 更合适）。"""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def extract_core_terms(prop_dir: Path) -> set:
    """提取课题核心术语（相关性判定的锚）。

    来源优先级：00_research_idea.md → 00_proposal-brief.md → proposal_id 分词。
    英文术语直接成词；中文不做分词（零依赖），靠英文术语 + 符号锚定，
    误伤由"成片才拦截"的保守阈值兜底。
    """
    import re as _re
    terms = set()
    for part in prop_dir.name.split("-"):
        if len(part) >= 3 and not part.isdigit() and part not in ("general", "key", "major"):
            terms.add(part.lower())
    for fname in ("00_research_idea.md", "00_proposal-brief.md"):
        p = prop_dir / fname
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8")[:30000]
            except Exception:
                continue
            for w in _re.findall(r"[A-Za-z][A-Za-z-]{2,}", text):
                wl = w.lower().strip("-")
                if wl and wl not in STOPWORDS_EN and len(wl) >= 3:
                    terms.add(wl)
            break
    return terms


def detect_redundancy(sections_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """冗余检测：章节内重复 + 跨章节重复（NSFC 红线）。

    Returns:
        {"within": [{section, sentence, count}],
         "cross": [{sections, sentence, kind}]}  kind=exact|similar
    """
    sec_sents: Dict[str, List[str]] = {}
    for sec in ("rationale", "content", "scheme"):
        p = sections_dir / f"{sec}.md"
        if not p.exists():
            continue
        sec_sents[sec] = _split_sentences(p.read_text(encoding="utf-8"))

    # 章节内：归一化后完全相同句计数
    within: List[Dict[str, Any]] = []
    for sec, sents in sec_sents.items():
        seen: Dict[str, List[str]] = {}
        for s in sents:
            norm = _normalize_sentence(s)
            if len(norm) < SENT_MIN_CHARS:
                continue
            seen.setdefault(norm, []).append(s)
        for norm, occ in seen.items():
            if len(occ) >= 2:
                within.append({"section": sec, "sentence": occ[0][:80], "count": len(occ)})

    # 跨章节：精确匹配（dict）+ 高相似（同长度桶内 containment）
    cross: List[Dict[str, Any]] = []
    norm_map: Dict[str, List[str]] = {}
    for sec, sents in sec_sents.items():
        for s in sents:
            norm = _normalize_sentence(s)
            if len(norm) < SENT_MIN_CHARS:
                continue
            norm_map.setdefault(norm, []).append(sec)
    for norm, secs in norm_map.items():
        if len(set(secs)) >= 2:
            cross.append({
                "sections": sorted(set(secs)),
                "sentence": norm[:80],
                "kind": "exact",
            })

    # 高相似：按长度分桶控制复杂度
    by_len: Dict[int, List[Tuple[str, str]]] = {}
    for sec, sents in sec_sents.items():
        for s in sents:
            norm = _normalize_sentence(s)
            if len(norm) < SENT_MIN_CHARS:
                continue
            by_len.setdefault(len(norm) // 20, []).append((sec, norm))
    reported: set = set()
    for _, items in by_len.items():
        feats = [(sec, norm, _token_set(norm)) for sec, norm in items]
        for i in range(len(feats)):
            for j in range(i + 1, len(feats)):
                s1, n1, f1 = feats[i]
                s2, n2, f2 = feats[j]
                if s1 == s2:
                    continue  # 跨章节才算（章节内已有精确计数）
                if n1 == n2 or _containment(f1, f2) > 0.85:
                    key = (n1[:40], n2[:40])
                    if key in reported or key[::-1] in reported:
                        continue
                    reported.add(key)
                    cross.append({
                        "sections": sorted({s1, s2}),
                        "sentence": f"{n1[:40]} ≈ {n2[:40]}",
                        "kind": "similar",
                    })

    exact_n = sum(1 for c in cross if c["kind"] == "exact")
    sim_n = len(cross) - exact_n
    if exact_n > CROSS_DUP_EXACT_LIMIT * 3 or sim_n > CROSS_DUP_SIM_LIMIT * 5:
        cross = cross[:20]  # 输出防爆
    return {"within": within, "cross": cross}


def detect_irrelevance(sections_dir: Path, core_terms: set) -> List[Dict[str, Any]]:
    """无关内容检测：段落级核心术语命中（保守——成片才升级）。

    Returns:
        [{section, index, chars, preview}] 疑似无关段落列表。
    """
    paras: List[Dict[str, Any]] = []
    for sec in ("rationale", "content", "scheme"):
        p = sections_dir / f"{sec}.md"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        lowered = text.lower()
        offset = 0
        idx = 0
        for block in text.split("\n\n"):
            start = lowered.find(block.lower(), offset)
            if start >= 0:
                offset = start + len(block)
            stripped = block.strip()
            if len(stripped) < PARA_MIN_CHARS or stripped.startswith(("#", "|", ">")):
                continue
            blob = stripped.lower()
            hits = sum(1 for t in core_terms if t in blob)
            if hits == 0:
                paras.append({
                    "section": sec, "index": idx, "chars": len(stripped),
                    "preview": stripped[:60],
                })
            idx += 1
    return paras


def quality_gate(
    sections_dir: Path,
    section_key: str,
    before_chars: Optional[int],
    prop_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """质量门：以质量缺陷为唯一拦截判据（字数仅上下文/放大器）。

    程序化拦截（字面确凿，零误伤）：
    ① 跨章节归一化完全相同句 ≥1 处，或高相似句 ≥2 处（评审红线）；
    ② 章节内任一句重复 ≥3 次，或 ≥3 组句子各自重复（成片复制）。

    语义层线索（不拦截，交 LLM 裁决）：
    - 无关内容检测是启发式（中文密集段落与英文术语表天然低重叠，
      08-27 实测 40+ 段核心论证被误标），相关性判断属语义判断——
      疑似无关段落列表注入 critic/writer prompt，由 LLM 复核裁决。

    字数超限不独立拦截——无上述命中的超限章节按"实质性长文"放行。

    Args:
        before_chars: writer 写入前该章节中文字数（诊断上下文）。
        prop_dir: 课题目录（核心术语提取；None 则跳过无关检测）。
    """
    after = section_char_count(sections_dir, section_key)
    budget = SECTION_BUDGETS.get(section_key)
    over_budget = bool(budget and after > budget[1])

    # v6.9.59 修复：跨章节冗余产生于三个正文章节之间，也只有正文
    # writer（每轮聚焦一个章节、被授权修改该章节）才可能消除。
    # references/full_review 的 writer 被指令约束"只修改聚焦章节文件"，
    # 物理上无法修复正文冗余——对非正文章节套用全局 cross 判据会让
    # 这两类 job 永远 passed=False，晋级主路径（5 模块全通过）被系统
    # 性封死。v6.9.54 的"无预算章节恒通过"出口在 v6.9.55 重构时意外
    # 丢失，本修复恢复该语义：非正文章节零信息通过——其结构卫生由
    # 写入门卫（guard_written_artifacts）专职负责（工作日志剥离/
    # 骨架迁移），句子重复检测对文献条目列表天然失真。
    is_body_section = section_key in SECTION_BUDGETS

    redundancy = {"within": [], "cross": []}
    irrelevant: List[Dict[str, Any]] = []
    try:
        redundancy = detect_redundancy(sections_dir)
    except Exception:
        pass
    # 无关检测仅对正文章节适用：references 是文献条目列表、
    # full_review 是逻辑骨架，核心术语锚定对二者天然失真。
    if prop_dir is not None and is_body_section:
        try:
            # 无锚定则无法判定相关性——核心术语为空时跳过无关检测，
            # 避免空集导致"全部段落零命中"的误拦（fail-safe）。
            terms = extract_core_terms(prop_dir)
            irrelevant = detect_irrelevance(sections_dir, terms) if terms else []
        except Exception:
            irrelevant = []

    # 判定 ①：跨章节重复（仅正文章节作为拦截依据；检测结果仍随
    # result 携带，供 critic prompt 注入线索）
    if is_body_section:
        cross_exact = [c for c in redundancy["cross"] if c["kind"] == "exact"]
        cross_sim = [c for c in redundancy["cross"] if c["kind"] == "similar"]
    else:
        cross_exact, cross_sim = [], []
    # 判定 ②：章节内重复（聚焦章节自身的）——任一句重复 ≥3 次
    # 或 ≥3 组不同句子各自重复，均为成片复制信号
    within_sec = [w for w in redundancy["within"] if w["section"] == section_key]
    max_repeat = max((w["count"] for w in within_sec), default=0)
    # 无关段落：语义判断交 LLM，程序只收集线索（见 result["irrelevant"]）

    reasons: List[str] = []
    if len(cross_exact) >= CROSS_DUP_EXACT_LIMIT:
        sample = cross_exact[0]["sentence"][:50] if cross_exact else ""
        reasons.append(f"跨章节重复句 {len(cross_exact)} 处（如：{sample}）")
    if len(cross_sim) >= CROSS_DUP_SIM_LIMIT:
        reasons.append(f"跨章节高相似句 {len(cross_sim)} 处")
    if len(within_sec) >= WITHIN_DUP_EXACT_LIMIT or max_repeat >= WITHIN_DUP_EXACT_LIMIT:
        sample2 = within_sec[0]["sentence"][:50] if within_sec else ""
        reasons.append(
            f"章节内重复论证：{len(within_sec)} 组（最高单句重复 {max_repeat} 次，如：{sample2}）"
        )
    # 无关占比不进拦截（语义判断交 LLM）——仅在结果中携带供 prompt 注入

    if reasons:
        detail = "；".join(reasons)
        if over_budget:
            detail += f"。冗余/无关同时导致膨胀：{after} 字（参考体量 ≤{budget[1] if budget else '-'}）"
        return {
            "applies": True, "passed": False, "chars": after, "before": before_chars,
            "over_budget": over_budget,
            "reason": f"质量缺陷未修复：{detail}",
            "redundancy": redundancy, "irrelevant": irrelevant,
        }

    note = ""
    if over_budget:
        note = (
            f"实质性长文放行：{after} 字（参考体量 ≤{budget[1]}），"
            f"冗余/无关检测零命中——密度合格，字数不作为扣分项"
        )
    return {
        "applies": True, "passed": True, "chars": after, "before": before_chars,
        "over_budget": over_budget, "reason": note or "质量检测零命中",
        "redundancy": redundancy, "irrelevant": irrelevant,
    }


def quality_directives_text(prop_dir: Path, focus_key: Optional[str] = None) -> str:
    """writer/critic 质量指令：冗余给处置指令，无关给复核线索（LLM 裁决）。"""
    sections_dir = prop_dir / "04_proposal" / "sections"
    if not sections_dir.exists():
        return ""
    redundancy = {"within": [], "cross": []}
    irrelevant: List[Dict[str, Any]] = []
    try:
        redundancy = detect_redundancy(sections_dir)
        terms = extract_core_terms(prop_dir)
        if terms:
            irrelevant = detect_irrelevance(sections_dir, terms)
    except Exception:
        return ""
    lines: List[str] = []
    cross = redundancy["cross"][:6]
    within = redundancy["within"][:6]
    if cross:
        lines.append("【冗余修复指令（程序检测，逐条处置）】")
        lines.append("以下句子在多个章节重复出现（NSFC 评审红线'无跨章节内容重复'）：")
        for c in cross:
            lines.append(f"- [{'/'.join(c['sections'])}] {c['sentence']}")
        lines.append(
            "处置：保留最合适章节中的那一份，其余删除或改写为该章节独有的"
            "视角性引用（如方案引用立项依据结论时只写'如 §一所述'式指代，不复述论证）。"
        )
    if focus_key:
        w = [x for x in within if x["section"] == focus_key][:5]
        if w:
            lines.append(f"\n【聚焦章节内重复论证（{focus_key}）】")
            for x in w:
                lines.append(f"- 重复 {x['count']} 次：{x['sentence']}")
            lines.append("处置：合并为一次完整论证，其余删除。")
    if irrelevant:
        irr_focus = [p for p in irrelevant if not focus_key or p["section"] == focus_key][:8]
        if irr_focus:
            lines.append("\n【相关性复核线索（程序初筛，需你语义裁决）】")
            lines.append(
                "以下段落与课题核心术语零重叠。程序无法判断相关性（中文论证段"
                "天然低术语密度，存在误报），请逐一复核：确属与课题论证链无关的"
                "内容删除；属核心论证的保留（无需改动措辞）。"
            )
            for p in irr_focus:
                lines.append(f"- [{p['section']} 第{p['index'] + 1}段] {p['preview']}…")
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# ⑦ critic 报告 digest + 方法学手册单一真相源（v6.9.60 同构问题治理）
#
# 同构问题排查结论（08-27 全环节审计）：
#   A. 方法学手册双真相源——03_method/method-manual.md（update_method_manual
#      derived job 维护，实测 47KB）与 04_proposal/methodology-manual.md
#      （writer 维护，10KB）并存，读者（weekend/kb_sync vs writer prompt）
#      各指一处，互不同步。修复：单一真相源 = 03_method（读者多），
#      04_proposal 旧文件迁移存档 + 原位 stub 指针。
#   B. critic 报告无篇幅约束（实测 16-37KB）——writer 每轮必读全文，
#      是超时输入大头。修复：程序化 digest（提取问题结构）替代全文
#      注入，报告 ≤ 阈值时用原文。
# ---------------------------------------------------------------------------

# critic 报告超过此值时启用 digest（writer 输入瘦身）
CRITIC_REPORT_DIGEST_THRESHOLD = 25 * 1024
CRITIC_DIGEST_MAX_BYTES = 8 * 1024


def build_critic_digest(report_path: Path) -> Optional[Path]:
    """为大体量 critic 报告生成问题结构 digest（零 LLM）。

    提取规则：severity 标记行（critical/high/medium/low/严重/高/中/低）
    整行保留 + 各级标题保留 + 评分块保留；其余叙述段丢弃。产物写入
    同目录 .critic-digest-{原名}，供 writer 读取替代全文。

    Returns:
        digest 路径；报告未超阈值或解析失败返回 None（调用方用原文）。
    """
    try:
        raw = report_path.read_text(encoding="utf-8")
    except Exception:
        return None
    if len(raw.encode("utf-8")) <= CRITIC_REPORT_DIGEST_THRESHOLD:
        return None

    import re
    sev = re.compile(
        r"(critical|high|medium|low|严重|高优先|中优先|低优先|P0|P1)", re.I)
    score = re.compile(r"(综合评分|总评|评分[：:]|创新性[：:]|可行性[：:]|严谨性[：:]|完整性[：:]|表达[：:])")
    keep: List[str] = [
        f"<!-- v6.9.60 程序 digest：全文 {len(raw.encode('utf-8')) // 1024}KB 超阈值，"
        f"仅保留问题结构（severity 行/标题/评分）。完整报告：{report_path.name} -->"
    ]
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith(("#", "```", "【", "|")) or sev.search(s) or score.search(s):
            keep.append(line)
    digest = "\n".join(keep)
    # 超预算时按字节截断（中文 UTF-8 3 字节/字，字符截断会放大约 3 倍）
    raw_digest = digest.encode("utf-8")
    if len(raw_digest) > CRITIC_DIGEST_MAX_BYTES:
        cut = raw_digest[: CRITIC_DIGEST_MAX_BYTES].decode("utf-8", errors="ignore")
        digest = cut + "\n…（digest 截断，详见完整报告）"
    out = report_path.parent / f".critic-digest-{report_path.name}"
    try:
        out.write_text(digest, encoding="utf-8")
        return out
    except Exception:
        return None


def migrate_methodology_manual(prop_dir: Path, dry_run: bool = False) -> Optional[str]:
    """一次性迁移：04_proposal/methodology-manual.md 归档 + 原位 stub。

    双真相源分裂修复的存量动作：03_method/method-manual.md 为唯一真相源
    （update_method_manual derived job 维护，weekend/kb_sync 读取）；
    04_proposal 旧文件（writer 曾写）整体迁 05_review/ 存档，原位留
    指针 stub 防旧引用读空。

    Returns:
        迁移产物路径，未触发返回 None。
    """
    legacy = prop_dir / "04_proposal" / "methodology-manual.md"
    canonical = prop_dir / "03_method" / "method-manual.md"
    if not legacy.exists():
        return None
    text = legacy.read_text(encoding="utf-8")
    if text.strip().startswith("<!-- v6.9.60") and "03_method" in text[:200]:
        return None  # 已是 stub，幂等

    out = prop_dir / "05_review" / f"methodology-manual-legacy-{_date_tag()}.md"
    if dry_run:
        return f"(dry-run) {out.name} ← 04_proposal 旧手册归档 + stub 指针"

    review_dir = prop_dir / "05_review"
    review_dir.mkdir(parents=True, exist_ok=True)
    # 唯一真相源不存在时先从旧文件落位（防 stub 指针悬空）
    if not canonical.exists():
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_text(text, encoding="utf-8")
    out.write_text(
        f"<!-- v6.9.60 从 04_proposal/methodology-manual.md 迁出的旧手册 -->\n"
        f"<!-- 方法学手册唯一真相源：03_method/method-manual.md -->\n\n" + text,
        encoding="utf-8",
    )
    stub = (
        f"<!-- v6.9.60 方法学手册唯一真相源已迁至 03_method/method-manual.md -->\n"
        f"<!-- 本文件为兼容指针，请勿在此写入内容。 -->\n\n"
        f"# 方法学手册（已迁移）\n\n"
        f"本手册的唯一真相源：`03_method/method-manual.md`。\n"
        f"历史版本存档：`05_review/{out.name}`。\n"
    )
    legacy.write_text(stub, encoding="utf-8")
    return str(out)


# ---------------------------------------------------------------------------
# ⑤ 批量入口与 CLI
# ---------------------------------------------------------------------------

def apply_all(project_root: Path, dry_run: bool = False) -> Dict[str, list]:
    """对全部 optimizing 课题执行一次性清洗（含 v6.9.60 手册归档）。"""
    opt_dir = project_root / "research_proposals" / "optimizing"
    result = {"full_review": [], "references": [], "methodology": []}
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
        r3 = migrate_methodology_manual(prop_dir, dry_run=dry_run)
        if r3:
            result["methodology"].append({"proposal": prop_dir.name, "out": r3})
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
        # v6.9.59 修复：断言同步 v6.9.55 重构语义——预算报告为纯信息性
        # 体量参考（"削减目标"量化指令已由质量检测器接管），不再包含
        # "净删/削减至"字样。
        assert "章节体量参考" in txt and "参考上限之上" in txt, "体量参考应标注超限章节"
        assert "优先排查冗余" in txt, "超限提示应引导排查冗余（v6.9.55 语义）"

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
