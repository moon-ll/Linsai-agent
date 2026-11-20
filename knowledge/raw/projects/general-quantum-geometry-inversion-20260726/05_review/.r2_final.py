# -*- coding: utf-8 -*-
"""R2 最终核查：DOI 重试 / arXiv https 重试 / 精确标题检索 / 长句归属 / 术语"""
import re, json, subprocess
from pathlib import Path
BASE = Path('/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-quantum-geometry-inversion-20260726')
S = BASE / '04_proposal/sections'
r = (S/'rationale.md').read_text(encoding='utf-8')
content = (S/'content.md').read_text(encoding='utf-8')
scheme = (S/'scheme.md').read_text(encoding='utf-8')

def cr(doi):
    out = subprocess.run(['curl','-s','--max-time','20',f'https://api.crossref.org/works/{doi}'],capture_output=True,text=True).stdout
    try:
        d = json.loads(out)['message']
        t = d['title'][0] if d.get('title') else '?'
        jr = (d.get('container-title') or ['?'])[0]
        yr = d.get('issued',{}).get('date-parts',[[None]])[0][0]
        return f'"{t[:75]}" | {jr[:32]} v{d.get("volume")} p{d.get("page")} ({yr})'
    except Exception:
        return f'RETRY-FAIL ({len(out)} bytes)'

print('== 失败 DOI 重试 ==')
for n, doi in [('2','10.1038/s41467-018-07373-0'),('6','10.1038/s41586-023-06899-0'),('26','10.1103/PhysRevB.49.8869')]:
    print(f'[{n}] {doi} →', cr(doi))

print('\n== 精确标题检索（定位正确 DOI）==')
for k, q in [
 ('Vampa2015','Linking high harmonics from gases and solids'),
 ('Luu2018','Measurement of the Berry curvature of solid through high-harmonic spectroscopy'),
 ('LiuFuKais','Berry curvature quantum metric tensor high harmonic spectrum solids'),
 ('Silva2018','High-harmonic spectroscopy of ultrafast many-body dynamics strongly correlated'),
 ('Uzan2024','Direct observation Berry phase solid-state high-harmonic generation'),
 ('Goswami2024','quantum metric nonlinear Hall non-collinear antiferromagnet'),
]:
    out = subprocess.run(['curl','-s','--max-time','20',
      'https://api.crossref.org/works?query.bibliographic='+q.replace(' ','+')+'&rows=2&select=title,DOI,container-title,issued,volume,page'],
      capture_output=True,text=True).stdout
    try:
        items = json.loads(out)['message']['items']
        print(f'--- {k} ---')
        for it in items:
            t=(it.get('title') or ['?'])[0]; jr=(it.get('container-title') or ['?'])[0]
            yr=it.get('issued',{}).get('date-parts',[[None]])[0][0]
            print(f'   {t[:78]} | {jr[:28]} ({yr}) | {it["DOI"]}')
    except Exception as e:
        print(f'--- {k} FAIL {e}')

print('\n== arXiv https 重试 ==')
for n, aid in [('8','2409.04216'),('13','2508.00296'),('20','2503.15932'),('23','2512.24553'),('19','2510.15207'),('17','2605.28236'),('11','2606.02238')]:
    out = subprocess.run(['curl','-s','--max-time','20',f'https://export.arxiv.org/api/query?id_list={aid}'],capture_output=True,text=True).stdout
    tm = re.findall(r'<title>(.*?)</title>', out, re.S)
    tot = re.findall(r'totalResults[^>]*>(\d+)', out)
    title = tm[1].strip().replace('\n',' ')[:80] if len(tm)>1 else 'NOT FOUND'
    print(f'[{n}] {aid} total={tot[0] if tot else "?"} → {title}')

print('\n== 长句归属（>120 字，公式折叠，同算法）==')
for name, t in [('rationale',r),('content',content),('scheme',scheme)]:
    c = 0
    for ln in t.split('\n'):
        if ln.startswith('#') or not ln.strip(): continue
        text = re.sub(r'\$[^$]*\$','X',ln)
        for s2 in re.split(r'(?<=[。？！；])', text):
            s2 = s2.strip()
            if len(s2) >= 10:
                if len(s2) > 120: c += 1
    print(f'{name}: >120字句 {c}')

print('\n== rationale 内 适用/失效 关键词定位 ==')
for kw in ['适用','失效','边界条件']:
    for m in re.finditer(kw, r):
        ln = r[:m.start()].count('\n')+1
        print(f'  L{ln} [{kw}]:', r[max(0,m.start()-25):m.start()+45].replace('\n',' '))

print('\n== 布洛赫方程命名 ==')
for name, t in [('rat',r),('cont',content),('sch',scheme)]:
    for pat in ['半导体布洛赫方程','固体布洛赫方程','布洛赫方程']:
        n = t.count(pat)
        if n: print(f'  {name} "{pat}": {n}')

print('\n== rationale 加粗标记数 ==')
print('  ** 对数:', len(re.findall(r'\*\*[^*]+\*\*', r)))
print('  段落均长:', round(len(r)/ max(1,sum(1 for l in r.split(chr(10)) if l.strip() and not l.startswith('#')))))

print('\n== scheme 1T-TaS₂ U/W 上下文（报告引用用）==')
for m in re.finditer(r'1T-TaS₂[^。]{0,60}', scheme):
    print('  ', m.group(0)[:80])
print('\n== scheme 相图区间原句 ==')
for m in re.finditer(r'相图覆盖[^。]{0,90}', scheme):
    print('  ', m.group(0)[:120])

print('\n== [2] 在 rationale 的引用行确认 ==')
for i, ln in enumerate(r.split('\n'),1):
    if re.search(r'\[1[–-]3', ln) or '[2]' in ln:
        print(f'  L{i}:', ln[:100])
