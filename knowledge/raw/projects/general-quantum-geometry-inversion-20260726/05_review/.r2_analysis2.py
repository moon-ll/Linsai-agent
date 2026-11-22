# -*- coding: utf-8 -*-
"""R2 补充核查：僵尸条目 / 跨章边界 / 重复度 / 手册指针"""
import re
from pathlib import Path
BASE = Path('/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-quantum-geometry-inversion-20260726')
r = (BASE/'04_proposal/sections/rationale.md').read_text(encoding='utf-8')
content = (BASE/'04_proposal/sections/content.md').read_text(encoding='utf-8')
scheme = (BASE/'04_proposal/sections/scheme.md').read_text(encoding='utf-8')

def used_nums(t):
    s = set()
    for m in re.finditer(r'\[(\d+)(?:[–-](\d+))?\]', t):
        a,b = m.group(1), m.group(2)
        if b: s.update(range(int(a),int(b)+1))
        else: s.add(int(a))
    return s

ur, uc, us = used_nums(r), used_nums(content), used_nums(scheme)
allu = ur|uc|us
print('== 僵尸条目判定（41 条中未被任何章节引用）==')
zombies = [n for n in range(1,42) if n not in allu]
print('僵尸条目:', zombies)
for n in sorted(zombies):
    m = re.search(rf'^\[{n}\] (.+)', (BASE/'04_proposal/sections/references.md').read_text(encoding='utf-8'), re.M)
    print(f'  [{n}]', (m.group(1)[:70] if m else '?'))
print('矩阵声称 rationale 但 rationale 未引:', sorted(set([9,10,22,39,40]) - ur, key=int), '| 其中 content/scheme 引用情况:', {n: (n in uc, n in us) for n in [9,10,22,39,40]})

print('\n== scheme/content 中的 BSV-SBE 适用边界声明 ==')
for name, t in [('content',content),('scheme',scheme)]:
    for kw in ['适用条件','失效边界','适用区间','适用范围']:
        for m in re.finditer(kw, t):
            ln = t[:m.start()].count('\n')+1
            ctx = t[max(0,m.start()-60):m.start()+120].replace('\n',' ')
            print(f'{name} L{ln} [{kw}]: ...{ctx[:150]}...')

print('\n== Fisher 比灰区（1.2 与 2 之间）是否处理 ==')
for name, t in [('rationale',r),('content',content),('scheme',scheme)]:
    for m in re.finditer(r'1\.2', t):
        ctx = t[max(0,m.start()-50):m.start()+80].replace('\n',' ')
        print(f'{name}: ...{ctx}...')

print('\n== scheme 年度计划与 rationale §1.4 重复度 ==')
for kw in ['BSV 源', 'Phase 1', 'Year 2 Q3', '主动收窄']:
    print(f'"{kw}": rat={r.count(kw)} cont={content.count(kw)} sch={scheme.count(kw)}')

print('\n== 方法学手册小节存在性 ==')
manual = None
for cand in [BASE/'03_method/method-manual.md', BASE/'04_proposal/methodology-manual.md']:
    if cand.exists(): manual = cand.read_text(encoding='utf-8'); print('手册文件:', cand, len(manual), 'chars')
if manual:
    for sec in ['§1D.3','§2D.4','§2.2','1D.3','2D.4']:
        print(f'  手册含 "{sec}":', sec in manual)
    # 灵敏度系数 0.5 在手册？
    print('  手册含 "灵敏度系数":', '灵敏度系数' in manual, '| 含 "S_\\\\Omega":', ('S_' in manual))
else:
    print('  未找到手册正文 → rationale 的 3 处手册指针全部悬空')

print('\n== 检测报告 self_reference 口径推断 ==')
selfref_pat = r'本项目|本申请|本文|本节|本章|本课题|本研究'
for name, t in [('rationale',r),('content',content),('scheme',scheme)]:
    n = len(re.findall(selfref_pat, t))
    print(f'{name}: {n} 次 (字符占比 {len(t)/61484*100:.0f}%)')

print('\n== 同一限定语重复（preprint 待核实）==')
for name, t in [('rationale',r),('content',content),('scheme',scheme)]:
    n = t.count('正式发表状态待核实') + t.count('正式发表状态待 2026')
    print(f'{name}: {n} 次')

print('\n== 破折号插入语统计 ==')
for name, t in [('rationale',r),('content',content),('scheme',scheme)]:
    print(f'{name}: {t.count("——")} 次')

print('\n== rationale 引用标记实例数（v6.9.9 校准 10-20 次基准）==')
for name, t in [('rationale',r),('content',content),('scheme',scheme)]:
    marks = re.findall(r'\[[0-9][0-9–,\s–-]*\]', t)
    print(f'{name}: {len(marks)} 个 [N] 标记实例')
