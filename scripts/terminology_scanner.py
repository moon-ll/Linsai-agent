#!/usr/bin/env python3
"""跨章记号/术语一致性扫描器（v7.3.58，目标：撰写质量与风格稳定性）。

对标背景（2026-11-07 同类项目对标调研，见 memory/goals/2026-11-07-benchmark-*.md）：
    科学写作术语一致性工具（Trinka 类）与长文一致性基准（ConStory-Bench 类）
    是同类系统的标准能力；本项目评审-修改多轮链路长期漏检**跨章记号/术语
    变体**——实证：chiral/phonon 专家交接单 20 条残留中 8 条属此类
    （"零泵浦产额记号四形 I₀/(I_q⁰)/δI_q⁽⁰⁾"、"对映体互换/反转"、
    "相图/相位图"、"即时/瞬时 1:26"、"判词零命中"），多轮 critic 均未报。
    根因：params_registry 口径表只覆盖人工播种的数值/表述，无**自动发现**
    通道。本扫描器补零 LLM 确定性发现层，产出候选报告（不改文——处置
    归 writer/critic 契约）。

扫描维度（全部确定性，报告不改文）：
    1. CJK 术语变体候选对——高频 n-gram（每处 ≥3 次）中字符 LCS 比 ≥0.5
       且互不为子串的配对（"相图/相位图"、"对映体互换/反转"、"即时/瞬时"
       形态），学术高频词停用表过滤误报。
    2. 拉丁/希腊记号变体组——记号 token 统一化（unicode 上下标→ASCII、
       去花括号、去 δ/Δ 前缀与 prime 旗标入键），同组出现 ≥2 个不同表面
       形态且非单次噪声即报（"I₀ vs I_0" 类记号四形发现通道）。
    3. 数值口径不在本扫描器范围（params_registry 口径表 + scan_text_conflicts
       已覆盖，避免双报）。

用法：
    python3 scripts/terminology_scanner.py --proposal <proposal_id>   # 扫描并落盘报告
    python3 scripts/terminology_scanner.py --proposal <id> --strict   # 有候选对则 exit 1
    python3 scripts/terminology_scanner.py --self-check

产出：
    05_review/terminology-scan.json + stdout 摘要；panel 任务包发射时内联
    引用（panel_review._emit_task_package 接线，作评审团核查靶子的补充层）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import load_json, now_utc, save_json  # noqa: E402

SECTIONS = ["rationale", "content", "scheme", "full_review"]
MANUAL_PATH = "03_method/method-manual.md"

# 学术高频停用 n-gram（LCS 配对误报过滤——这些词的变体对是正常语言现象）
_CJK_STOP = {
    "研究", "方法", "实验", "分析", "结果", "系统", "模型", "理论", "数据",
    "进行", "通过", "基于", "使用", "采用", "给出", "对应", "计算", "验证",
    "方案", "项目", "本文", "本章", "本节", "其中", "因此", "同时", "以及",
    "给出", "所述", "该文", "本项目", "本方案", "研究内容", "研究方案",
    "立项依据", "预期成果", "考核指标", "技术路线", "关键科学", "科学问题",
}

# 共同词缀停用：变体对共享此前缀/后缀时为同族命名（X手性 系=不同物理量），
# 非术语漂移，跳过
_CJK_AFFIX_STOP = {"手性", "效应", "判据", "阈值", "谐波", "条件", "分量",
                   "结构", "路径", "信号", "强度", "方向", "极化", "过程"}

# 记号 token：希腊/拉丁字母开头 + 可选上下标（三种形态：_x / ^x / 直接附着 unicode 上下标）
_SUBSUP_CLUSTER = r"A-Za-z0-9⁺⁻ⁿ⁰¹²³⁴⁵⁶⁷⁸⁹⁽⁾ᵢⱼ\^()"
_TOKEN_RE = re.compile(
    r"([Α-Ωα-ωA-Za-z][Α-Ωα-ωA-Za-z0-9]{0,7})"
    r"(?:[_\^]\{?([" + _SUBSUP_CLUSTER + r"]+)\}?"
    r"|([" + r"₀₁₂₃₄₅₆₇₈₉ᵢⱼ⁰¹²³⁴⁵⁶⁷⁸⁹⁽⁾⁺⁻ⁿ" + r"]+))?"
)
# unicode 上下标 → ASCII 转写（分组用，只求确定性不求排版保真）
_SUBSUP_MAP = {
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5",
    "₆": "6", "₇": "7", "₈": "8", "₉": "9", "ᵢ": "i", "ⱼ": "j",
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
    "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "ⁿ": "n", "⁺": "+",
    "⁻": "-", "⁽": "(", "⁾": ")", "^": "",
}


def _norm_token(full: str, sub: str) -> Tuple[str, str]:
    """记号归一：上下标转 ASCII 后统一为 full_sub 形态；返回 (group_key, surface)。

    三形态同键：I₀ / I_0 → I_0（键 i_0）；I_q⁽⁰⁾ / I_q^(0) → I_q(0)；
    δ 前缀入键分组呈现（δI 与 I 同族但分开报告，避免误合并不同物理量）。
    """
    translit = "".join(_SUBSUP_MAP.get(c, c) for c in (sub or ""))
    surface = f"{full}_{translit}" if translit else full
    surface = surface.replace("{", "").replace("}", "")
    # δ/Δ 微扰前缀入键旗标（δI_q 与 I_q 分组）
    key_core = surface
    prefix = ""
    if key_core[:1] in "δΔ":
        prefix, key_core = key_core[:1], key_core[1:]
    key = prefix + re.sub(r"[ \t]", "", key_core)
    return key, surface


def _lcs_ratio(a: str, b: str) -> float:
    """最长公共子序列长度 / 较短串长度。"""
    if not a or not b:
        return 0.0
    m, n = len(a), len(b)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            cur[j] = prev[j - 1] + 1 if a[i - 1] == b[j - 1] else max(prev[j], cur[j - 1])
        prev = cur
    return prev[n] / min(m, n)


def _load_texts(prop_dir: Path) -> Dict[str, str]:
    texts: Dict[str, str] = {}
    for name in SECTIONS:
        p = prop_dir / "04_proposal" / "sections" / f"{name}.md"
        if p.exists():
            texts[name] = p.read_text(encoding="utf-8", errors="replace")
    manual = prop_dir / MANUAL_PATH
    if manual.exists():
        texts["method_manual"] = manual.read_text(encoding="utf-8", errors="replace")
    return texts


def _variant_pair_ok(a: str, b: str) -> bool:
    """变体对形态规则：同前缀或同后缀 ≥1 字，且差异余部双方非空。

    正例：对映体互换/反转（同前缀"对映体"）、相图/相位图（同前缀"相"）、
    即时/瞬时（同后缀"时"）、资料/材料（同后缀"料"）。
    反例（滑窗重叠假阳性）：对映/映体（无公共前后缀——同词相邻窗）；
    同族命名（X手性 系，共享词缀在停用表）——不同物理量非术语漂移。
    """
    if a == b or a in b or b in a:
        return False
    # 公共前缀
    p = 0
    while p < min(len(a), len(b)) and a[p] == b[p]:
        p += 1
    if p >= 1 and a[p:] and b[p:]:
        shared = a[:p] if p <= len(a) else a
        if shared not in _CJK_AFFIX_STOP:
            return True
    # 公共后缀
    s = 0
    while s < min(len(a), len(b)) and a[-1 - s] == b[-1 - s]:
        s += 1
    if s >= 1 and a[:-s] and b[:-s]:
        shared = a[-s:] if s <= len(a) else a
        if shared not in _CJK_AFFIX_STOP:
            return True
    return False


def _scan_cjk_variant_pairs(texts: Dict[str, str],
                            min_freq: int = 3,
                            min_pairs: int = 0) -> List[Dict[str, Any]]:
    """高频 CJK n-gram 的变体候选对（报告不改文）。"""
    counts: Counter = Counter()
    where: Dict[str, set] = {}
    for name, text in texts.items():
        # 只取 CJK 连续段（长度 2-8），滑窗 2/3/4/5 gram（5 覆盖"对映体互换"类长术语）
        for seg in re.findall(r"[\u4e00-\u9fff]{2,8}", text):
            for size in (2, 3, 4, 5):
                for i in range(len(seg) - size + 1):
                    g = seg[i:i + size]
                    if g in _CJK_STOP:
                        continue
                    counts[g] += 1
                    where.setdefault(g, set()).add(name)
    freq = [g for g, c in counts.items() if c >= min_freq]
    freq.sort(key=lambda g: -counts[g])
    pairs: List[Dict[str, Any]] = []
    seen = set()
    for a, b in combinations(freq[:400], 2):
        if abs(len(a) - len(b)) > 1:
            continue
        if _lcs_ratio(a, b) < 0.5:
            continue
        if not _variant_pair_ok(a, b):
            continue
        key = tuple(sorted((a, b)))
        if key in seen:
            continue
        seen.add(key)
        pairs.append({
            "a": a, "b": b,
            "freq_a": counts[a], "freq_b": counts[b],
            "sections_a": sorted(where[a]), "sections_b": sorted(where[b]),
        })
        if 0 < min_pairs <= len(pairs):
            break
    return pairs


def _scan_token_variants(texts: Dict[str, str],
                         min_freq: int = 2) -> List[Dict[str, Any]]:
    """记号 token 变体组：按归一键分组，组内追踪**原始表面形态**（raw）。

    设计要点：I₀ 与 I_0 归一后同为 I_0（键 i_0）——变体恰恰体现在原始
    写法差异上，故组内计数按 raw 文本计，≥2 种 raw 形态且有复现即报。
    """
    raw_counts: Dict[str, Counter] = {}
    where: Dict[str, set] = {}
    for name, text in texts.items():
        body = re.sub(r"```[\s\S]*?```", "", text)  # 代码块不算正文记号
        for m in _TOKEN_RE.finditer(body):
            full, sub = m.group(1), (m.group(2) if m.group(2) is not None else (m.group(3) or ""))
            # 记号过滤：短 token（≤3 字符，数学符号典型形态）或带显式上下标；
            # 长英文散文词（Harmonic/Floquet 类）不进组
            if len(full) > 3 and not sub:
                continue
            key, _ = _norm_token(full, sub)
            if len(key.lstrip("δΔ")) < 1:
                continue
            raw = m.group(0).rstrip("{}")
            raw_counts.setdefault(key, Counter())[raw] += 1
            where.setdefault(key, set()).add(name)
    groups: List[Dict[str, Any]] = []
    for key, counter in raw_counts.items():
        distinct = {s for s, c in counter.items() if c >= min_freq}
        if len(distinct) >= 2:
            groups.append({
                "group_key": key,
                "variants": [{"form": s, "count": counter[s]} for s in sorted(distinct)],
                "sections": sorted(where[key]),
            })
    groups.sort(key=lambda g: -sum(v["count"] for v in g["variants"]))
    return groups


def scan_proposal(prop_dir: Path) -> Dict[str, Any]:
    """扫描一个课题，返回报告 dict（不落盘）。"""
    texts = _load_texts(prop_dir)
    if not texts:
        return {"checked": False, "reason": "无章节文件", "at": now_utc()}
    cjk_pairs = _scan_cjk_variant_pairs(texts)
    # 截断前两步整理：① 按词长降序优先（保留最长形态对）→ ② 子串支配坍缩
    # （同词滑窗子 gram 对如 体互/体反 ⊂ 对映体互换/对映体反转 只留最长）
    cjk_pairs.sort(key=lambda p: (-max(len(p["a"]), len(p["b"])),
                                  -min(p["freq_a"], p["freq_b"])))
    kept: List[Dict[str, Any]] = []
    for p in cjk_pairs:
        dominated = any(
            (p["a"] in q["a"] and p["b"] in q["b"])
            or (p["a"] in q["b"] and p["b"] in q["a"])
            for q in kept
        )
        if not dominated:
            kept.append(p)
    cjk_pairs = kept
    token_groups = _scan_token_variants(texts)
    return {
        "checked": True,
        "at": now_utc(),
        "proposal": prop_dir.name,
        "sections_scanned": sorted(texts.keys()),
        "cjk_variant_pairs": cjk_pairs[:12],
        "token_variant_groups": token_groups[:12],
        "summary": {
            "cjk_pair_candidates": len(cjk_pairs),
            "token_variant_groups": len(token_groups),
            "note": "候选报告不改文：处置归 writer/critic 契约；数值口径归 params_registry",
        },
    }


def run_and_persist(prop_dir: Path, strict: bool = False) -> Dict[str, Any]:
    """扫描 + 落盘 05_review/terminology-scan.json。strict 时有候选则 exit 1。"""
    report = scan_proposal(prop_dir)
    out = prop_dir / "05_review" / "terminology-scan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    save_json(out, report)
    s = report.get("summary", {})
    n_pair, n_tok = s.get("cjk_pair_candidates", 0), s.get("token_variant_groups", 0)
    print(f"✓ 术语扫描落盘: {out}")
    print(f"  CJK 变体候选对: {n_pair} | 记号变体组: {n_tok}")
    for p in report.get("cjk_variant_pairs", [])[:6]:
        print(f"  ~ {p['a']}({p['freq_a']}) ↔ {p['b']}({p['freq_b']}) @ {','.join(p['sections_a'][:2])}")
    for g in report.get("token_variant_groups", [])[:6]:
        forms = " / ".join(v["form"] for v in g["variants"])
        print(f"  ~ [{g['group_key']}] {forms}")
    if strict and (n_pair or n_tok):
        return {"report": report, "exit": 1}
    return {"report": report, "exit": 0}


def _self_check() -> bool:
    """自检：合成课题（已知变体）检出 + 停用词过滤 + 归一正确性。"""
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as td:
        prop = Path(td) / "prop-test"
        sec = prop / "04_proposal" / "sections"
        sec.mkdir(parents=True)
        # 各变体 ≥3 次（min_freq=3 生产口径）
        (sec / "rationale.md").write_text(
            "对映体互换判据成立。对映体互换给出符号行为。对映体互换为初判入口。"
            "相图给出边界，相图坐标为温度，相图第三处出现于此。"
            "即时响应与瞬时效应混用。即时读出为先。泵浦产额记作 I₀ 与 I_0 两种形态混用。"
            "I₀ 出现于份额表。\n", encoding="utf-8")
        (sec / "content.md").write_text(
            "对映体反转判据独立执行，对映体反转优先于互换判据，此为对映体反转的第三次出现。"
            "相位图见方案，相位图横轴为波长，相位图纵轴为产额。"
            "即时读出与瞬时读出并存，瞬时读出为正文主用形态。"
            "I_0 归一化后进入份额表，I_0 的定义见方案。\n", encoding="utf-8")
        rep = scan_proposal(prop)
        cjk = {(p["a"], p["b"]) for p in rep.get("cjk_variant_pairs", [])}
        got1 = ("对映体互换", "对映体反转") in cjk or ("对映体反转", "对映体互换") in cjk
        got2 = ("相图", "相位图") in cjk or ("相位图", "相图") in cjk
        got3 = ("即时", "瞬时") in cjk or ("瞬时", "即时") in cjk
        ok &= got1 and got2 and got3
        print(("✓" if got1 else "✗") + " 对映体互换/反转 检出")
        print(("✓" if got2 else "✗") + " 相图/相位图 检出")
        print(("✓" if got3 else "✗") + " 即时/瞬时 检出")
        # 停用词不得出现
        stops = [p for pair in cjk for p in pair if p in _CJK_STOP]
        ok &= not stops
        print(("✓" if not stops else "✗") + " 停用词过滤")
        # 记号归一：I₀ 与 I_0 同键（键区分大小写，数学符号大小写敏感）
        tok = {g["group_key"]: g["variants"] for g in rep.get("token_variant_groups", [])}
        merged = any(len(v) >= 2 for k, v in tok.items() if k.startswith("I_0") or k == "I_0")
        ok &= merged
        print(("✓" if merged else "✗") + " I₀/I_0 记号归一同组")
    print("✓ terminology_scanner 自检通过" if ok else "✗ terminology_scanner 自检失败")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="跨章记号/术语一致性扫描器（零 LLM，报告不改文）")
    ap.add_argument("--proposal", help="proposal_id（research_proposals/optimizing/ 下）")
    ap.add_argument("--strict", action="store_true", help="有候选变体则 exit 1")
    ap.add_argument("--self-check", action="store_true", help="内置自检")
    args = ap.parse_args()
    if args.self_check:
        return 0 if _self_check() else 1
    if not args.proposal:
        ap.print_help()
        return 2
    prop_dir = PROJECT_ROOT / "research_proposals" / "optimizing" / args.proposal
    if not prop_dir.exists():
        prop_dir = PROJECT_ROOT / "research_proposals" / "pending_review" / args.proposal
    if not prop_dir.exists():
        print(f"✗ 课题目录不存在: {args.proposal}")
        return 2
    return run_and_persist(prop_dir, strict=args.strict)["exit"]


if __name__ == "__main__":
    raise SystemExit(main())
