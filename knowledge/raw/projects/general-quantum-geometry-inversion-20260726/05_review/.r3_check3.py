# R3 round-3 cross-check part 3 (critic)
import re
import json

base = '/Users/ll/Desktop/LinSai-CoPilot/'
c = open('content.md', encoding='utf-8').read()
r = open('references.md', encoding='utf-8').read()
s = open('scheme.md', encoding='utf-8').read()
ra = open('rationale.md', encoding='utf-8').read()

# remaining ref entries
for n in [1, 2, 4, 6, 9, 15, 17, 18, 19, 20, 30, 35, 40]:
    m = re.search(rf'^\[{n}\] (.+)$', r, flags=re.M)
    print(f"[{n}]", (m.group(1)[:100] if m else 'MISSING'))
m = re.search(r'^\[22\] (.+)$', r, flags=re.M)
print('[22] FULL:', m.group(1)[:180] if m else 'MISSING')

# rationale citation numbers
ranums = set()
for m in re.finditer(r'\[([\d,\s]+)\]', ra):
    if any(ch.isalpha() for ch in m.group(1)):
        continue
    for x in m.group(1).split(','):
        if x.strip().isdigit():
            ranums.add(int(x.strip()))
print('rationale cites:', sorted(ranums))
# where does rationale mention Lange
for m in re.finditer(r'Lange', ra):
    print('RA Lange ctx:', ra[max(0, m.start()-60):m.start()+90].replace('\n', ' ')[:170])

# scheme: statistical approach consistency
for w in ['Mann-Whitney', '功效', '条件数', 'SNR', 'z 检验', '样本量']:
    hits = [(s[:m.start()].count('\n')+1, s[max(0, m.start()-40):m.start()+60].replace('\n',' ')) for m in re.finditer(w, s)]
    print(f'SCHEME "{w}": {len(hits)}')
    for ln, ctx in hits[:3]:
        print('   L', ln, ctx[:130])

# scheme g2 threshold
for m in re.finditer(r'g\^\{\(2\)\}\(0\)[^。]{0,50}', s):
    print('SCHEME g2 tail:', m.group(0)[:90])
# 1e-6
print('content 10⁻⁶:', len(re.findall(r'10⁻⁶', c)), '| scheme:', len(re.findall(r'10⁻⁶', s)))
# 三指标 thresholds in scheme
for w in ['0\.3', 'cond', '条件数', 'rho', 'C_\{\\Omega g\}']:
    print(f'SCHEME {w}:', len(re.findall(w, s)))

# rationale §1.4 两阶段温扫
for m in re.finditer(r'§1\.4|180–220|两阶段', ra + c):
    src = 'RA' if m.start() < len(ra) else 'CT'
    txt = ra if src == 'RA' else c
    off = m.start() if src == 'RA' else m.start()-len(ra)-1
    print(src, m.group(0), ':', txt[max(0, off-60):off+90].replace('\n', ' ')[:160])

# content long sentences line numbers (recount, skip display math)
body = re.sub(r'\$\$.*?\$\$', ' ', c, flags=re.S)
body_ns = re.sub(r'\n+', '\n', body)
for i, line in enumerate(body_ns.split('\n'), 1):
    for sent in re.split(r'(?<=[。！？])', line):
        t = sent.strip()
        if len(t) > 120 and not t.startswith('['):
            print(f'LONG L{i} ({len(t)}):', t[:55])

# section_standards
d = json.load(open(base+'memory/nsfc-standards.json', encoding='utf-8'))
ss = d['general_principles']['section_standards']
print()
print('section_standards keys:', list(ss.keys()))
print(json.dumps(ss.get('研究内容', {}), ensure_ascii=False, indent=1)[:2600])
