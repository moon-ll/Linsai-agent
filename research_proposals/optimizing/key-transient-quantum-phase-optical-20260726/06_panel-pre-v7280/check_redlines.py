#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""程序化检测：超长句/自引用/元话语/模板句式/方法学手册指针等红线项。可重复运行（改前基线/改后验收）。"""
import re, sys, json

BASE = "/Users/ll/Desktop/LinSai-CoPilot/research_proposals/pending_review/key-transient-quantum-phase-optical-20260726/04_proposal/sections/"
FILES = {"rat": "rationale.md", "con": "content.md", "sch": "scheme.md", "full": "full_review.md", "refs": "references.md"}

def load(tag):
    with open(BASE + FILES[tag], encoding="utf-8") as f:
        lines = f.read().split("\n")
    return lines

def strip_latex(s):
    return re.sub(r"\$[^$]*\$", "", s)

def sentences(text):
    # 按句号/问号/叹号切分
    parts = re.split(r"(?<=[。！？])", text)
    return [p for p in parts if p.strip()]

def count_chars(s):
    return len(re.sub(r"\s", "", s))

def long_sentences(lines, tag):
    """返回 (剥LaTeX口径, 原始口径) 超长句列表：>120 字"""
    out_net, out_raw = [], []
    for i, ln in enumerate(lines, 1):
        if ln.startswith("#") or ln.startswith("|") or ln.startswith(">"):
            continue
        for sent in sentences(ln):
            net = count_chars(strip_latex(sent))
            raw = count_chars(sent)
            if net > 120:
                out_net.append((i, net, sent.strip()[:60]))
            if raw > 120:
                out_raw.append((i, raw, sent.strip()[:60]))
    return out_net, out_raw

SELFREF = ["本项目", "本研究", "本课题", "本方案", "本文"]
META = ["需要特别说明的是", "值得一提的是", "需要说明的是", "不难看出", "值得注意的是"]
CONNECT = ["在此基础上", "与此同时", "基于此"]
DECOR = ["显著", "重要", "系统", "良好", "成熟", "完整", "关键", "精准", "一系列", "有效", "高效"]

def grep_count(lines, pat):
    n = 0
    for i, ln in enumerate(lines, 1):
        c = len(re.findall(pat, ln))
        if c:
            n += c
    return n

def grep_lines(lines, pat):
    return [(i, ln.strip()[:80]) for i, ln in enumerate(lines, 1) if re.search(pat, ln)]

report = {}
all_self = 0
for tag in ["rat", "con", "sch"]:
    lines = load(tag)
    net, raw = long_sentences(lines, tag)
    sf = {w: grep_count(lines, w) for w in SELFREF}
    sf_total = sum(sf.values())
    all_self += sf_total
    report[tag] = {
        "long_net": [(i, n) for i, n, _ in net],
        "long_net_detail": net,
        "long_raw_count": len(raw),
        "selfref": sf, "selfref_total": sf_total,
        "meta": {m: grep_count(lines, m) for m in META if grep_count(lines, m)},
        "connect": {c: grep_count(lines, c) for c in CONNECT if grep_count(lines, c)},
        "decor_total": grep_count(lines, "|".join(DECOR)),
        "template_wei": grep_count(lines, r"为.{1,18}提供.{0,6}(基础|支撑|途径|条件|工具|指导)"),
        "manual_ptr": grep_lines(lines, r"(详见|见)方法学手册"),
    }
report["三章自引用合计"] = all_self

# sch 专项
sch = load("sch")
report["sch专项"] = {
    "本项目行号": grep_lines(sch, "本项目"),
    "方法学手册全部行号": grep_lines(sch, "方法学手册"),
}

# 三现句检测
pat_cp = "圆偏振 HHG"  # 圆偏振HHG角色句
rat, con = load("rat"), load("con")
report["三现_圆偏振HHG时间分辨"] = {
    "rat": grep_lines(rat, r"圆偏振 HHG的时间分辨|圆偏振 HHG 的时间分辨"),
    "con": grep_lines(con, r"圆偏振 HHG 承担|时间分辨能力为光场周期"),
    "sch": grep_lines(sch, r"时间分辨能力为光场周期"),
}
report["三现_同一件事母题"] = {
    "full": grep_lines(load("full"), r"不可分割"),
    "con": grep_lines(con, r"不可分割"),
    "sch": grep_lines(sch, r"同一件事"),
}
report["三现_三家互补"] = {
    "rat_L65区": grep_lines(rat, r"MIT|MPQ|ELI-ALPS"),
    "sch": grep_lines(sch, r"MIT|MPQ|Zair"),
}
report["ATA推导"] = {
    "rat_206": grep_lines(rat, r"206"),
    "sch_94": grep_lines(sch, r"94"),
    "con_81": grep_lines(con, r"方和根"),
}
report["Mokhtari双现"] = {"rat": grep_lines(rat, r"15–30|15-30")}
report["Zair归属"] = {"sch": grep_lines(sch, r"Zair"), "rat": grep_lines(rat, r"Zhao 等\[15\]")}
report["答辩式元话语候选"] = {
    "sch": grep_lines(sch, r"真正理由|不是\"|回应了|并列|拼成"),
}
report["sch_L5目录句"] = {"sch": grep_lines(sch, r"§1 论证|§2 给出|§7 给出")}

print(json.dumps(report, ensure_ascii=False, indent=1))
