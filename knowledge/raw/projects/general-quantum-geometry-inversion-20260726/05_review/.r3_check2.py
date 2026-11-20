# R3 round-3 cross-check (critic)
import re

c = open('content.md', encoding='utf-8').read()
r = open('references.md', encoding='utf-8').read()
s = open('scheme.md', encoding='utf-8').read()
ra = open('rationale.md', encoding='utf-8').read()

# 1. full citation numbers incl comma lists
nums = set()
for m in re.finditer(r'\[([\d,\s]+)\]', c):
    for x in m.group(1).split(','):
        if x.strip().isdigit():
            nums.add(int(x.strip()))
print("content all [N]:", sorted(nums))
refs_have = set(int(m.group(1)) for m in re.finditer(r'^\[(\d+)\]', r, flags=re.M))
print("cited but NOT in refs:", sorted(nums - refs_have), "| in refs never cited by content:", sorted(refs_have - nums))
for m in re.finditer(r'\[50\]', c):
    ln = c[:m.start()].count('\n') + 1
    print(f"[50] at line {ln}:", c[max(0, m.start()-100):m.start()+30].replace('\n', ' '))
for m in re.finditer(r'\[16\]', c):
    ln = c[:m.start()].count('\n') + 1
    print(f"[16] at line {ln}:", c[max(0, m.start()-80):m.start()+15].replace('\n', ' '))

# 2. refs entries snapshot
for n in [3, 5, 7, 8, 10, 11, 12, 13, 14, 16, 21, 22, 23, 24, 25, 26, 27, 28, 29, 41]:
    m = re.search(rf'^\[{n}\] (.+)$', r, flags=re.M)
    print(f"[{n}]", (m.group(1)[:95] if m else 'MISSING'))

# 3. Queisser/Lange/Fazekas in refs?
for w in ['Queisser', 'Lange', 'Fazekas', 'Tosatti']:
    print(w, 'in refs:', w in r, '| in rationale:', w in ra, '| in scheme:', w in s, '| in content:', w in c)
    if w in ra:
        for m in list(re.finditer(w, ra))[:3]:
            print('   RA ctx:', ra[max(0, m.start()-50):m.start()+60].replace('\n', ' '))

# 4. methodology-manual refs and line-number refs
print()
print('manual refs in content:', len(re.findall(r'方法学手册', c)), '| in scheme:', len(re.findall(r'方法学手册', s)))
print('line-number refs:', re.findall(r'§\d\.\d 第 \d+ 行', c))
print('internal § refs in content:', re.findall(r'§\d\.\d', c)[:20])

# 5. cross-section numeric consistency
checks = [
    (r'10⁻⁵', 'coupling 1e-5'),
    (r'g\^\{\(2\)\}\(0\)\s*>\s*1\.5', 'g2>1.5'),
    (r'e\^\{-2r\}', 'khurel e^-2r'),
    (r'2°', 'pol 2deg'),
    (r'n\s*\\geq\s*60', 'n>=60'),
    (r'48\s*GPU', '48 gpu'),
    (r'±0\.1\s*K', 'pid 0.1K'),
    (r'15%', '15pct'),
    (r'3\.17', '3.17'),
]
for pat, lab in checks:
    print(lab, '| content:', len(re.findall(pat, c)), '| scheme:', len(re.findall(pat, s)), '| rationale:', len(re.findall(pat, ra)))

for m in list(re.finditer(r'Rivera-Dean', s))[:2]:
    print('SCHEME rivera ctx:', s[max(0, m.start()-150):m.start()+280].replace('\n', ' ')[:400])
for m in list(re.finditer(r'g\^\{\(2\)\}\(0\)', s))[:5]:
    print('SCHEME g2 ctx:', s[max(0, m.start()-100):m.start()+100].replace('\n', ' '))

# 6. Q1/Q2 in rationale
print()
print('Q1/Q2 in rationale:')
for m in list(re.finditer(r'Q[12]', ra))[:8]:
    print('  ', ra[max(0, m.start()-80):m.start()+130].replace('\n', ' ')[:200])

# 7. paragraph stats
paras = [p for p in c.split('\n\n') if p.strip()]
print()
print('paras:', len(paras))
