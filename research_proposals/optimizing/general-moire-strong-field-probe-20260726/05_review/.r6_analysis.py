# -*- coding: utf-8 -*-
"""Round-6 content.md 红队评审辅助分析脚本"""
import re, os, json

BASE = "/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-moire-strong-field-probe-20260726"
SEC = os.path.join(BASE, "04_proposal/sections")
files = {n: open(os.path.join(SEC, n), encoding="utf-8").read() for n in
         ["rationale.md", "content.md", "scheme.md", "references.md", "full_review.md"]}

print("== 1. 字符数对账 ==")
tot = 0
for n, t in files.items():
    if n == "references.md":
        continue
    print(n, "chars=", len(t), "cjk=", len(re.findall(r'[\u4e00-\u9fff]', t)))
    if n != "full_review.md":
        tot += len(t)
print("三章节字符和(+2x2分隔):", tot + 4, " 检测报告值: 31428")

print("\n== 2. 检测报告3个超长句例句定位 ==")
probes = ["自 2018 年 Cao 等人", "围绕这一核心问题，选取 TMDC", "第一层挑战来自计算规模"]
for p in probes:
    hit = [n for n, t in files.items() if p in t]
    print(repr(p[:18]), "->", hit if hit else "NOT FOUND (疑似旧版文字)")

print("\n== 3. content.md 超长句独立复核（>120字，句号切分，排除标题/引用行）==")
ct = files["content.md"]
severe = []
for i, line in enumerate(ct.split("\n"), 1):
    if line.startswith("#") or line.startswith("[") or not line.strip():
        continue
    for s in re.split(r"[。]", line):
        s = s.strip()
        if len(s) > 120:
            severe.append((i, len(s), s[:60]))
print("content.md >120字句子数:", len(severe))
for i, L, h in severe:
    print(f"  L{i} len={L} {h}...")
mid = []
for i, line in enumerate(ct.split("\n"), 1):
    if line.startswith("#") or not line.strip():
        continue
    for s in re.split(r"[。]", line):
        s = s.strip()
        if 80 < len(s) <= 120:
            mid.append((i, len(s)))
print("80-120字句数:", len(mid), "分布行:", [m[0] for m in mid])

print("\n== 4. 词汇频次统计（content.md / 三章节合计） ==")
for w in ["闭环", "读出", "改写", "递进", "1:1", "可证伪", "降阶", "有效", "完整", "关键", "系统", "显著", "精准", "成熟", "良好", "本项目拟", "本项目将", "本项目"]:
    c3 = sum(files[n].count(w) for n in ["rationale.md", "content.md", "scheme.md"])
    print(f"{w}: content={ct.count(w)}  三章节={c3}")

print("\n== 5. 自引用统计 ==")
for n in ["rationale.md", "content.md", "scheme.md"]:
    refs = re.findall(r"§[一二三四五0-9.]+", files[n])
    print(n, "count=", len(refs), refs[:15])

print("\n== 6. 关键数值跨章节一致性 grep ==")
pats = ["±0.05", "±0.02", "±0.1", "0.1°", "15%", "12%", "18%", "30%", "6%", "5%", "8×10¹⁰", "1.6×10¹¹",
        "3×10¹¹", "10¹²", "20%", "0.2", "2.5", "3 μm", "CEP", "I_c", "Δ_CI", "平方正比", "唯一", "尚未见报道", "首次"]
for p in pats:
    for n in ["rationale.md", "content.md", "scheme.md"]:
        for i, line in enumerate(files[n].split("\n"), 1):
            if p in line:
                print(f"[{p}] {n}:L{i}: {line.strip()[:100]}")
    print("-")

print("\n== 7. scheme/rationale 标题结构 ==")
for n in ["rationale.md", "scheme.md"]:
    print(n, [l for l in files[n].split("\n") if l.startswith("#")])

print("\n== 8. references.md 中关键作者/文献匹配 ==")
for a in ["Nikola", "Tyulnev", "Molinero", "Mrudul", "Zhou", "Kozák", "Lian", "Xu", "Meng", "Bauer", "Hansen",
          "Ghimire", "Xiao", "Mak", "Cao", "Bistritzer", "Matter", "Floquet"]:
    for i, line in enumerate(files["references.md"].split("\n"), 1):
        if a in line:
            print(f"[{a}] L{i}: {line.strip()[:150]}")

print("\n== 9. content.md 中 [CITE:] 标签 ==")
for m in re.finditer(r"\[CITE:[^\]]+\]", ct):
    print(" ", m.group(0))
print("content.md 内联作者-年份（无CITE标签）计数:",
      len(re.findall(r"\d{4} 年在 \*", ct)) + len(re.findall(r"等 \d{4} 年", ct)))

print("\n== 10. 方法学手册存在性 ==")
for root, dirs, fs in os.walk(BASE):
    for f in fs:
        if "method" in f.lower() or "手册" in f:
            print(os.path.join(root, f))
