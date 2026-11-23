#!/usr/bin/env python3
# monitor r3 独立核查：正文↔新文献表映射 + 长句 + 计数 + 残留
import re, unicodedata
from pathlib import Path

BASE = Path("/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-moire-strong-field-probe-20260726")
SEC = BASE / "04_proposal" / "sections"
files = {n: (SEC / f"{n}.md").read_text(encoding="utf-8") for n in ["rationale", "content", "scheme", "references", "full_review"]}
draft = (BASE / "04_proposal" / "proposal-draft.md").read_text(encoding="utf-8")

# ---------- 1. 解析参考文献表 ----------
ref_text = files["references"]
entries = {}
for m in re.finditer(r"^\[(\d+)\]\s+(.+)$", ref_text, re.M):
    n, line = int(m.group(1)), m.group(2)
    ym = re.findall(r"\((\d{4})\)", line)
    year = int(ym[-1]) if ym else None
    first_author = re.split(r",", line)[0].strip()
    entries[n] = (first_author, year, line[:90])
print(f"== 参考文献条目数: {len(entries)} (编号 {min(entries)}-{max(entries)})")
nums = sorted(entries)
gaps = [n for n in range(1, max(entries) + 1) if n not in entries]
print(f"   跳号: {gaps if gaps else '无'}")
recent = [n for n, (a, y, l) in entries.items() if y and 2024 <= y <= 2026]
old = [n for n, (a, y, l) in entries.items() if y and y < 2024]
noyear = [n for n, (a, y, l) in entries.items() if y is None]
print(f"   2024-2026: {len(recent)} 条 ({len(recent)/len(entries)*100:.1f}%) | 2011-2023: {len(old)} 条 | 无年份: {noyear}")
print(f"   头注声称: 29 条 72.5% / 11 条 -> 实测 {len(recent)}/{len(old)}")

# ---------- 2. 正文引用提取与映射 ----------
cite_re = re.compile(r"\[(\d{1,2}(?:\s*,\s*\d{1,2})*)\]")
def extract_cites(text):
    found = []
    for m in cite_re.finditer(text):
        for tok in m.group(1).split(","):
            found.append(int(tok.strip()))
    return found

all_cites = {}
per_file_counts = {}
for name in ["rationale", "content", "scheme"]:
    cs = extract_cites(files[name])
    all_cites[name] = cs
    per_file_counts[name] = len(cs)
union = sorted(set(c for cs in all_cites.values() for c in cs))
dangling = [c for c in union if c > 40 or c < 1]
orphans = [n for n in sorted(entries) if n not in union]
print(f"\n== 正文引用: rationale {per_file_counts['rationale']} 处 / content {per_file_counts['content']} 处 / scheme {per_file_counts['scheme']} 处")
print(f"   引用编号并集: {len(union)} 个 | 悬空(>40): {dangling if dangling else '无'} | 文献表孤儿(未被引): {orphans if orphans else '无'}")

# ---------- 3. 具名作者 ↔ 角标一致性 ----------
name_map = {
    "Heide 等 2024 年在 *Nat. Phys.*": 3, "Ghimire 等 2011 年": 4, "Ghimire 等 2010 年": 4,
    "Molinero 等 2024 年在 *Optica*": 6, "Molinero 等 [6]": 6,
    "Du 等 2024 年": 7, "Cao 等 2024 年": 8, "Uzner 与 Neufeld 2026": 9,
    "Ikeda 等 2025": 10, "Hu 等 2024 年在 *Phys. Rev. Lett.*": 11,
    "Luu 与 Wörner 2018": 12, "Shan 等 2021": 13, "Pan 与 Das Sarma 2021": 14,
    "Xiong 等 2023 年": 15, "Lian 等 2024 年": 16, "Xiong 等 2024 年": 17,
    "Wu 等 2025 年": 18, "Chang Lee 等 2024 年在 *Nat. Commun.*": 19,
    "Yao 等 2025 年": 20, "Bathen 等 2026": 21, "Sun 等 2025 年": 22,
    "Peterka 等 2023 年": 23, "Mrudul 2024 年": 24, "Mrudul 的椭偏理论 [24]": 24,
    "Zhou 等 2023 年": 25, "Zhang 与 Tyulnev 等 2025": 26,
    "Hejazi 等 2026 年": 27, "Seewald 等 2025": 28, "Klein 等 2026": 29,
    "Cavaletto 与 Madsen 2024": 30, "Zhao 等 2025 年": 32,
    "Sato 与 Ikeda 2025": 33, "Tyulnev 等 2024 年": 34,
    "Dong 与 Liu 2022": 35, "Jessen 等 2025": 36, "Duncan 等 2025": 37,
    "Zhang 等 2026 年": 38, "de Almeida 等 2026": 39, "van Essen 等 2026": 40,
}
print(f"\n== 具名句 ↔ 角标/条目 抽查:")
mismatch = 0
for name in ["rationale", "content", "scheme"]:
    text = files[name]
    for phrase, expect in name_map.items():
        for m in re.finditer(re.escape(phrase) + r"(.{0,120}?)\[(\d{1,2}(?:\s*,\s*\d{1,2})*)\]", text, re.S):
            got = [int(t) for t in m.group(2).split(",")]
            if expect not in got:
                print(f"   [MISMATCH] {name}: '{phrase[:22]}...' 期望{expect} 实得{got}")
                mismatch += 1
# 具名但整句无角标（裁撤后无源断言候选）
anon_candidates = ["人工堆叠 TMDC 晶体的 HHG 随层数相干叠加", "时间分辨光电子能谱已在扭转双层体系中", "RABBIT 旁带振荡相对远失谐参考点出现 π 相移", "把多日累计的亚光周期稳定性延伸到 ≤59 mrad", "二维材料强场综述从方法学角度论证", "CEP 稳定度现状落在约 380 mrad"]
print(f"\n== 裁撤候选无源断言核验（正文具名/具数值但零角标）:")
for name in ["rationale", "content", "scheme"]:
    text = files[name]
    for ph in anon_candidates:
        idx = text.find(ph)
        if idx >= 0:
            window = text[idx: idx + len(ph) + 150]
            has_n = bool(re.search(r"\[\d{1,2}", window))
            print(f"   {'OK(有角标)' if has_n else '!! 无角标'} | {name}: {ph[:30]}...")

# ---------- 4. 长句统计（>120 字） ----------
def cn_len(s):
    return len(re.sub(r"\s", "", s))
def count_long(text, thresh=120):
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    body = re.sub(r"^\|.*$", "", body, flags=re.M)  # 去表格行
    body = re.sub(r"^#+\s.*$", "", body, flags=re.M)
    sents = re.split(r"[。！？]", body)
    return [s for s in sents if cn_len(s) > thresh]
print(f"\n== >120 字超长句统计:")
tot = 0
for name in ["rationale", "content", "scheme"]:
    ls = count_long(files[name])
    tot += len(ls)
    longest = max((cn_len(s) for s in ls), default=0)
    print(f"   {name}: {len(ls)} 处 (最长 {longest} 字)")
print(f"   三章合计: {tot} 处")

# ---------- 5. 中文字符体量 ----------
def cn_count(text):
    return len(re.findall(r"[\u4e00-\u9fff]", text))
print(f"\n== 中文字符体量 (参考区间 立项5000-8000/内容4000-7000/方案6000-10000):")
for name in ["rationale", "content", "scheme"]:
    print(f"   {name}: {cn_count(files[name])} 字")

# ---------- 6. 残留与一致性 grep ----------
checks = ["强场改写", "Malla", "No-Go", "Wang、Yu 与 Ciappina", "Gatti", "Moustaj", "Park 与 Lee", "Tai 等", "Lu 等 2025", "Velsink", "王崇阳"]
print(f"\n== 残留 grep（三章+draft，期望全 0 除注明）:")
for kw in checks:
    hits = {name: files[name].count(kw) for name in ["rationale", "content", "scheme"] if kw in files[name]}
    dh = draft.count(kw)
    if hits or dh:
        print(f"   '{kw}': sections={hits} draft={dh}")
print("   （未列出=零命中）")
for kw in ["30–50", "约 30%"]:
    hits = sum(files[n].count(kw) for n in ["rationale", "content", "scheme"])
    print(f"   失败率口径 '{kw}': {hits} 处")
for kw in ["< 15%", "±0.02°"]:
    for n in ["rationale", "content", "scheme"]:
        c = files[n].count(kw)
        if c:
            print(f"   '{kw}' in {n}: {c} 处")

# ---------- 7. references-notes 留痕 ----------
notes = BASE / "05_review" / "references-notes.md"
if notes.exists():
    t = notes.read_text(encoding="utf-8")
    secs = re.findall(r"^#+\s*(十[一二三四五六七八九]?|[一二三四五六七八九十]+)、《?([^,\n]{0,30})", t, re.M)
    tail = t[-400:]
    print(f"\n== references-notes.md: {len(t)} chars; 末节标题: {secs[-3:] if secs else '无'}; 尾部片段: ...{tail[-160:]}")
else:
    print("\n== references-notes.md 不存在")

# ---------- 8. 视图与 draft 与 sections 一致性 ----------
print(f"\n== proposal-draft.md 新旧状态: 含[41]-[48]角标: {[k for k in range(41,49) if f'[{k}]' in draft] or '无'}; 含'van Essen': {'是' if 'van Essen' in draft else '否'}")
v = (BASE / "05_review" / ".monitor-view-r3.md").read_text(encoding="utf-8")
print(f"== 视图含'van Essen 等 2026 年的瞬态 HHG 评述 [40]': {'是' if 'van Essen 等 2026 年的瞬态 HHG 评述 [40]' in v else '否'}")
print(f"== 视图引用并集与 sections 并集一致性: rationale角标数视图 {len(extract_cites(v))} (信息参考)")
