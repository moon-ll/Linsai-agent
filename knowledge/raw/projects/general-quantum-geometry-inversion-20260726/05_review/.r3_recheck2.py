# R3 cross-check part 2
import re, json

paths = {'rationale':'rationale.md','content':'content.md','scheme':'scheme.md','refs':'references.md','full':'full_review.md'}
txt = {k: open(v, encoding='utf-8').read() for k,v in paths.items()}
refs = txt['refs']; c = txt['content']; s = txt['scheme']; r = txt['rationale']

# A. refs entries
entries = re.findall(r'^\s*\[(\d+)\]', refs, flags=re.M)
nums = sorted(set(int(x) for x in entries))
print("refs entries:", len(nums), "min:", nums[0], "max:", nums[-1], "continuous:", nums == list(range(nums[0], nums[-1]+1)))
missing = [n for n in range(1, nums[-1]+1) if n not in nums]
print("missing numbers:", missing)

# B. specific entries
for n in [13, 21, 22, 23, 24, 25, 26, 27, 28, 29, 41, 50, 7, 8]:
    m = re.search(r'^\s*\['+str(n)+r'\](.+)$', refs, flags=re.M)
    print(f"[{n}]:", (m.group(1).strip()[:150] if m else "NOT FOUND"))

# C. [50] [41] usage context in content
for n in [50, 41]:
    for m in re.finditer(r'\['+str(n)+r'\]', c):
        print(f"content [{n}] ctx:", c[max(0,m.start()-80):m.start()+20].replace('\n',' '))

# D. self-ref total across 3 sections
tot_self = sum(len(re.findall('本项目|本课题|本研究', v)) for k,v in [('r',r),('c',c),('s',s)])
print("\nself-ref across 3 sections:", tot_self, "(report: 83)")
print("本项目 in r/c/s:", r.count('本项目'), c.count('本项目'), s.count('本项目'))

# E. cross-section refs sanity
print("\n'§1.2' in rationale:", '§1.2' in r or '1.2' in r, "| Q1/Q2 in rationale:", len(re.findall(r'Q1|Q2', r)))
print("scheme headings:", re.findall(r'^#{2,3} .+$', s, flags=re.M)[:12])
print("'§3.5'/'3.5' in scheme:", '3.5' in s, "| '风险' in scheme:", s.count('风险'))
print("方法学手册 mentions in content:", c.count('方法学手册'))
import os
mm = [f for f in os.listdir('.') if 'manual' in f.lower() or '方法学' in f]
print("manual-like files in sections/:", mm)
parent = os.listdir('..')
print("04_proposal contents:", parent)

# F. key-number consistency between content and scheme
for tok in ['10⁻⁵','10^{-5}','1.5','π/6','\\pi/6','0.3, 0.7','0.1, 1.0','cond','条件数','< 10','60','0.05','15%','30%','48','GPU','±5','5 μm','Janis','Lakeshore','BaF₂','200 K','±0.1 K','128','256']:
    hc, hs = c.count(tok), s.count(tok)
    if hc or hs: print(f"tok {tok!r}: content={hc} scheme={hs}")

# G. U/W phrasing across files
for m in re.finditer(r'U/W[^。]{0,60}', c+s):
    pass
uw_c = re.findall(r'U/W\s*[\\lesssimgtrsim><~≈≤≥]{1,3}\s*[0-9.]+|[0-9.]+\s*[–-]\s*[0-9.]+', c)
print("\nU/W claims in content:", uw_c[:12])
EOF_MARKER = True
