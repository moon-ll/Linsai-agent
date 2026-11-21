# -*- coding: utf-8 -*-
"""R2 rationale 聚焦评审的程序化分析脚本"""
import re, json
from pathlib import Path

BASE = Path('/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-quantum-geometry-inversion-20260726')
r = (BASE / '04_proposal/sections/rationale.md').read_text(encoding='utf-8')
content = (BASE / '04_proposal/sections/content.md').read_text(encoding='utf-8')
scheme = (BASE / '04_proposal/sections/scheme.md').read_text(encoding='utf-8')
refs = (BASE / '04_proposal/sections/references.md').read_text(encoding='utf-8')
lines = r.split('\n')

print('====== 1. rationale 基本统计 ======')
zh = len(re.findall(r'[\u4e00-\u9fff]', r))
print(f'总字符 {len(r)}, 中文字符 {zh}, 行数 {len(lines)}')

print('\n====== 2. 引用编号与引用定位矩阵比对 ======')
cits_per_line = {}
used = set()
for i, ln in enumerate(lines, 1):
    if ln.startswith('#'): continue
    found = []
    for m in re.finditer(r'\[(\d+)(?:[–-](\d+))?(?:,\s*(\d+))?\]', ln):
        a, b, c = m.group(1), m.group(2), m.group(3)
        nums = set()
        if b: nums.update(range(int(a), int(b)+1))
        else: nums.add(int(a))
        if c: nums.add(int(c))
        found.extend(sorted(nums)); used.update(nums)
    if found: cits_per_line[i] = found
print('rationale 实际引用编号:', sorted(used))
print('引用行映射:', json.dumps(cits_per_line, ensure_ascii=False))

# matrix claimed rationale rows
matrix_rows = re.findall(r'\| \[(\d+)\] ([^|]+)\| ([^|]*)\|', refs)
claimed_rationale = []
for num, name, ctx in matrix_rows:
    ctx = ctx.strip()
    if 'rationale' in ctx:
        claimed_rationale.append(int(num))
print('引用定位矩阵声称出现在 rationale 的编号:', sorted(claimed_rationale))
print('矩阵声称但 rationale 实际未引用:', sorted(set(claimed_rationale) - used))
print('rationale 实际引用但矩阵未标 rationale:', sorted(used - set(claimed_rationale)))

print('\n====== 3. 句长分析（折叠公式后）======')
long120, long80 = [], []
sent_total = 0
para_lens = []
for i, ln in enumerate(lines, 1):
    if ln.startswith('#') or not ln.strip(): continue
    text = re.sub(r'\$[^$]*\$', 'X', ln)
    text = re.sub(r'\$\$[^$]*\$\$', 'X', text)
    n_sent = 0
    for s in re.split(r'(?<=[。？！；])', text):
        s2 = s.strip()
        if len(s2) < 10: continue
        sent_total += 1; n_sent += 1
        if len(s2) > 120: long120.append((i, len(s2), s2[:60]))
        elif len(s2) > 80: long80.append((i, len(s2)))
    para_lens.append(n_sent)
print(f'总句数(≥10字): {sent_total}, >120字: {len(long120)}句 ({100*len(long120)/sent_total:.1f}%), 80-120字: {len(long80)}')
for i, l, ex in long120: print(f'  L{i} {l}字: {ex}...')

print('\n====== 4. AI 模式计数（rationale 单独）======')
print('本项目(次):', r.count('本项目'), '| 本申请:', r.count('本申请'), '| 本文:', r.count('本文'))
print('句首"本项目":', len(re.findall(r'[。；\n]本项目', r)))
for w in ['同时','因此','然而','基于此','此外','在此基础上','与此同时','进而','据此']:
    print(f'  关联词 {w}: {r.count(w)}')
mod_total = 0
for w in ['显著','重要','系统','成熟','完整','关键','有效','精准','良好','一系列']:
    n = r.count(w); mod_total += n
    print(f'  修饰词 {w}: {n}')
print('修饰词合计:', mod_total)
print('破折号——插入语:', r.count('——'))
print('括号密度: 全角( :', r.count('（'), ' 半角(:', r.count('('))
m_need = re.findall(r'为.{0,14}提供.{0,8}(?:基础|支撑|条件|途径|工具|指导|正当性|参照)', r)
print('为…提供…句式:', len(m_need), m_need[:6])
print('含"详见"的内部指针:', len(re.findall(r'详见', r)), re.findall(r'详见[^。；]{2,22}', r)[:12])

print('\n====== 5. 跨章节数字口径核查 ======')
def cnt(pat, txt): return len(re.findall(pat, txt))
checks = [
    ('Fisher比阈值 <1.2', r'[<＜]\s*1\.2'),
    ('Fisher比阈值 ≥2/≥ 2', r'(≥|\\geq\s*|＞)\s*2(?![0-9])'),
    ('后验方差收缩比≥2', r'收缩比'),
    ('条件数 cond<10', r'条件数|cond'),
    ('|ρ_Ωg|<0.3', r'rho|ρ'),
    ('TiSe₂各向异性≥2°', r'各向异性'),
    ('偏振旋转14.2°', r'14\.2'),
    ('7阶 9.5°', r'9\.5'),
    ('OPCPA 1.3–4.5μm', r'1\.3[–-]4\.5'),
    ('3.0μm 2×10^11', r'2\\times\s*10\^\{?11'),
    ('Ω误差<12%', r'12\\?%'),
    ('PINN n=200', r'n\s*=\s*200'),
    ('SNR>3', r'SNR'),
    ('正交残差<5%', r'正交残差'),
    ('U/W≲1.0', r'U/W'),
    ('r≤1.5 压缩参数', r'r\s*\\leq\s*1\.5|r ≤ 1\.5'),
    ('谐波阶次 n≤11', r'n \\leq 11|n ≤ 11'),
    ('5-15%红移', r'5[–-]15\\?%|5–15%'),
    ('~30%反演误差', r'30\\?%'),
    ('10⁻⁴ photons', r'10\^\{-?4\}|\$10\^'),
    ('BSV 10²–10³ 增强', r'10\^\{?2\}?[–-]10\^\{?3\}?|10\^2–10\^3|10²–10³'),
    ('2×10¹³ 光子', r'2\\times\s*10\^\{?13'),
    ('25 fs/9μJ', r'25\s*fs'),
    ('±1 V/Å', r'\\pm\s*1\s*V'),
    ('500 谱 过渡方案', r'500\s*(?:谱|条|个)'),
    ('Year2Q4启动2D SBE', r'Year 2 Q4'),
    ('Fisher信息比>2乘性', r'乘性'),
]
print(f"{'指标':<22} {'rat':>4} {'cont':>5} {'sch':>4}")
for name, pat in checks:
    print(f'{name:<22} {cnt(pat,r):>4} {cnt(pat,content):>5} {cnt(pat,scheme):>4}')

print('\n====== 6. 术语一致性 ======')
for t in ['BSV-SBE', 'SBE-Houston', 'tdDMFT', 'TDDFT', 'PINN', 'HMG-Schema', 'OPCPA', 'Fisher 信息', '后验方差', '可辨识性', '两堵墙', '光场统计墙', '电子结构墙', '乘性', '加性']:
    print(f'  {t}: rat={r.count(t)} cont={content.count(t)} sch={scheme.count(t)}')

print('\n====== 7. 方法学手册存在性 ======')
for pat in ['方法学手册', 'methodology']:
    hits = [str(p) for p in BASE.rglob('*') if p.is_file() and pat.lower() in p.name.lower() and '.git' not in str(p)]
    print(pat, '文件命中:', hits[:5])
mm = re.findall(r'方法学手册\s*(§[\dA-Z.]+)', r)
print('rationale 引用的方法学手册小节:', sorted(set(mm)))
# 手册在 repo 中的正文出现
for p in BASE.rglob('*.md'):
    if 'review' in str(p): continue
    try: t = p.read_text(encoding='utf-8')[:200]
    except Exception: continue
    if '方法学手册' in t and p.name not in ('rationale.md','content.md','scheme.md'):
        print('候选手册文件:', p)
        break

print('\n====== 8. 国内文献条目检查 ======')
print('references 含中文条目数:', len(re.findall(r'^\[\d+\].*[\u4e00-\u9fff]{4,}', refs, re.M)))
for name in ['孟胜', '兰鹏飞', '陶镇生', '王慧田', 'Gaarde', 'Madsen', 'ICFO']:
    print(f'  {name}: rat={r.count(name)} refs={refs.count(name)}')

print('\n====== 9. 合作方 affiliation ======')
m = re.search(r'ICFO[^。]{0,80}', r)
print('ICFO 上下文:', m.group(0) if m else 'N/A')
