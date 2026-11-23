# R3 final spot checks
import re

paths = {'rationale':'rationale.md','content':'content.md','scheme':'scheme.md','refs':'references.md'}
txt = {k: open(v, encoding='utf-8').read() for k,v in paths.items()}
c, s, r, refs = txt['content'], txt['scheme'], txt['rationale'], txt['refs']

# 1. [50] false positive?
print("[50] ctx:", [c[m.start()-30:m.start()+30] for m in re.finditer(r'\[50', c)])
print("[0-cite] ctx:", [c[m.start()-20:m.start()+15] for m in re.finditer(r'\[0[,.\]]', c)][:3])

# 2. Q1/Q2 and R1 task numbering in content
print("\nQ1/Q2 in content:", len(re.findall(r'Q[12]', c)), re.findall(r'.{18}Q[12].{18}', c)[:5])
print("R1 任务 mentions:", re.findall(r'R1 任务 \d', c))
print("R3 任务 mentions:", sorted(set(re.findall(r'R3 任务 \d', c))))

# 3. r>=15 text
m = re.search(r'.{60}gtrsim 15.{80}', c)
print("\nr~15:", m.group(0) if m else None)

# 4. scheme: intensity window & engineering overlap
print("\nscheme 0.1 window:", re.findall(r'0\.1[^。]{0,20}1\.0', s)[:4])
for key in ['Janis ST-100', 'Lakeshore 336', 'BaF₂', '±5 μm', 'z_R', '瑞利长度', 'PID 温控']:
    print(f"  '{key}' content={key in c} scheme={key in s}")

# 5. preprint share of content-cited refs
cited = set()
for m in re.finditer(r'\[(\d+(?:,\s*\d+)*(?:-\d+)?)\]', c):
    for part in m.group(1).split(','):
        part = part.strip()
        if '-' in part:
            a,b = part.split('-'); cited.update(range(int(a), int(b)+1))
        elif part.isdigit(): cited.add(int(part))
cited -= {0, 50}
preprints, journals = [], []
for n in sorted(cited):
    m = re.search(r'^\s*\['+str(n)+r'\](.+)$', refs, flags=re.M)
    e = m.group(1) if m else ''
    (preprints if 'arXiv' in e and '*' not in e.split('arXiv')[0][:80] else journals).append(n)
print("\ncontent-cited:", sorted(cited))
print("arXiv-only cites:", preprints, f"-> {len(preprints)}/{len(cited)} = {len(preprints)/len(cited):.0%}")

# 6. refs recency
years = re.findall(r'\((\d{4})\)', refs)
from collections import Counter
cnt = Counter(years)
recent = sum(v for k,v in cnt.items() if int(k) >= 2023)
total = sum(cnt.values())
print(f"\nrefs year coverage {total} entries w/ year; >=2023: {recent} ({recent/max(total,1):.0%})")

# 7. Queisser / Lange bare cites
print("\nQueisser in refs:", 'Queisser' in refs, "| Lange in refs:", 'Lange' in refs, "| Lange entry:", re.search(r'^\s*\[(\d+)\][^\n]*Lange', refs, flags=re.M).group(0)[:90] if re.search(r'Lange', refs) else None)
print("Queisser cites in content:", re.findall(r'.{15}Queisser.{25}', c))
print("Lange cites in content:", len(re.findall(r'Lange', c)))

# 8. bare author-year citations without [N] (names followed by 等(年份) but no bracket)
for pat in [r'[A-Z][a-z]+ 等[人]?\s*[（(]\d{4}[）)](?![^\[]{0,40}\[)']:
    print("bare author-year:", re.findall(pat, c))
