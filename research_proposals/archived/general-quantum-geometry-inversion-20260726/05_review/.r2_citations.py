# -*- coding: utf-8 -*-
"""R2 引用双向核查（修正正则）+ 批量 DOI/arXiv 反查"""
import re, json, subprocess
from pathlib import Path
BASE = Path('/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-quantum-geometry-inversion-20260726')
S = BASE / '04_proposal/sections'
r = (S/'rationale.md').read_text(encoding='utf-8')
content = (S/'content.md').read_text(encoding='utf-8')
scheme = (S/'scheme.md').read_text(encoding='utf-8')

PAT = re.compile(r'\[(\d+(?:\s*[–-]\s*\d+)?(?:\s*,\s*\d+(?:\s*[–-]\s*\d+)?)*)\]')
def used_nums(t):
    s = set()
    for m in PAT.finditer(t):
        for part in m.group(1).split(','):
            part = part.strip()
            rm = re.match(r'(\d+)\s*[–-]\s*(\d+)', part)
            if rm: s.update(range(int(rm.group(1)), int(rm.group(2))+1))
            else: s.add(int(part))
    return s

ur, uc, us = used_nums(r), used_nums(content), used_nums(scheme)
allu = ur | uc | us
print('== 双向引用核查（修正正则后）==')
print('rationale 引用:', sorted(ur))
print('content 引用:', sorted(uc))
print('scheme 引用:', sorted(us))
zombies = [n for n in range(1,42) if n not in allu]
print('僵尸条目（三章节均未引用）:', zombies)

refs = (S/'references.md').read_text(encoding='utf-8')
matrix_rows = re.findall(r'\| \[(\d+)\][^|]+\|([^|]*)\|', refs)
mism = []
for num, ctx in matrix_rows:
    n = int(num); ctx = ctx.strip()
    claimed = re.findall(r'rationale|content|scheme', ctx)
    actual = []
    if n in ur: actual.append('rationale')
    if n in uc: actual.append('content')
    if n in us: actual.append('scheme')
    claim_set = set(x for x in ['rationale','content','scheme'] if x in ctx)
    act_set = set(actual)
    if claim_set != act_set:
        mism.append((n, sorted(claim_set), sorted(act_set)))
print('\n矩阵声称 vs 实际引用错位（编号, 声称, 实际）:')
for n, c, a in sorted(mism):
    print(f'  [{n}] 声称{c} 实际{a}')
print(f'共 {len(mism)} 处错位')

print('\n== DOI 批量反查 ==')
dois = {
 '1': '10.1038/nature14512', '2': '10.1038/s41467-018-07373-0',
 '3': '10.1103/PhysRevResearch.4.013041', '4': '10.1038/s41566-018-0250-0',
 '5': '10.1038/s41567-023-02127-y', '6': '10.1038/s41586-023-06899-0',
 '7': '10.1038/s41567-024-02659-x', '10': '10.1038/s41586-024-07021-y',
 '26': '10.1103/PhysRevB.49.8869', '28': '10.1016/j.jcp.2018.10.045',
 '29': '10.1038/sdata.2016.18', '30': '10.1098/rspa.1984.0023',
 '31': '10.1103/RevModPhys.82.1959', '32': '10.1103/PhysRevLett.71.1994',
 '33': '10.1103/PhysRevA.49.2117', '34': '10.1038/nphys1847',
 '35': '10.1103/PhysRevLett.52.997', '37': '10.1103/RevModPhys.81.299',
 '38': '10.1038/387471a0', '41': '10.1038/s42254-021-00314-5',
}
for n, doi in dois.items():
    out = subprocess.run(['curl','-s','--max-time','15',f'https://api.crossref.org/works/{doi}'],
                         capture_output=True, text=True).stdout
    try:
        d = json.loads(out)['message']
        title = d['title'][0] if d.get('title') else '?'
        jr = (d.get('container-title') or ['?'])[0]
        yr = d.get('issued',{}).get('date-parts',[[None]])[0][0]
        print(f'[{n}] OK  "{title[:70]}" | {jr[:35]} v{d.get("volume")} p{d.get("page")} ({yr})')
    except Exception:
        print(f'[{n}] FAIL({doi}) — 解析失败/不存在')

print('\n== 标题检索定位正确 DOI ==')
searches = {
 'Liu-Fu-Kais': 'Quantum geometry high harmonic spectrum solids Berry curvature quantum metric',
 'Silva-Mott': 'High-harmonic generation Mott insulator Sr2CuO3',
 'Ghalgaoui-nonclassical': 'High-harmonic spectroscopy solids non-classical light',
 'Uzan-Berry': 'Berry phase high-harmonic generation solid',
 'Goswami-nonlinear-Hall': 'quantum metric nonlinear Hall antiferromagnet',
}
for k, q in searches.items():
    out = subprocess.run(['curl','-s','--max-time','20',
        f'https://api.crossref.org/works?query.bibliographic={q.replace(" ","+")}&rows=3&select=title,DOI,container-title,issued,volume,page'],
        capture_output=True, text=True).stdout
    try:
        items = json.loads(out)['message']['items']
        print(f'--- {k} ---')
        for it in items:
            t = (it.get('title') or ['?'])[0]
            jr = (it.get('container-title') or ['?'])[0]
            yr = it.get('issued',{}).get('date-parts',[[None]])[0][0]
            print(f'   {t[:72]} | {jr[:30]} ({yr}) | {it["DOI"]} v{it.get("volume")} p{it.get("page")}')
    except Exception as e:
        print(f'--- {k} FAIL {e}')

print('\n== arXiv 抽查（rationale 所引关键预印本）==')
ax = {'8':'2409.04216','9':'2406.17845','11':'2606.02238','12':'2604.13901','13':'2508.00296',
      '15':'2605.03794','17':'2605.28236','18':'2606.06999','19':'2510.15207','20':'2503.15932','23':'2512.24553'}
for n, aid in ax.items():
    out = subprocess.run(['curl','-s','--max-time','15',
        f'http://export.arxiv.org/api/query?id_list={aid}'],
        capture_output=True, text=True).stdout
    tm = re.findall(r'<title>(.*?)</title>', out, re.S)
    title = tm[1].strip().replace('\n',' ') if len(tm)>1 else 'NOT FOUND'
    am = re.findall(r'<name>(.*?)</name>', out)
    print(f'[{n}] arXiv:{aid} → "{title[:75]}" | 作者: {", ".join(am[:4])}')
