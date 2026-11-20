# R3 round-3 cross-check part 4 (critic)
import re, json

base = '/Users/ll/Desktop/LinSai-CoPilot/'
c = open('content.md', encoding='utf-8').read()
r = open('references.md', encoding='utf-8').read()
s = open('scheme.md', encoding='utf-8').read()

# section_standards for 研究内容
d = json.load(open(base+'memory/nsfc-standards.json', encoding='utf-8'))
ss = d['general_principles']['section_standards']
print('section_standards keys:', list(ss.keys()))
print(json.dumps(ss.get('研究内容', {}), ensure_ascii=False, indent=1)[:2800])

# module presence
for w in ['研究目标', '关键科学问题', '拟解决的关键']:
    print(w, 'in content:', c.count(w), '| in scheme:', s.count(w))

# verbatim duplication content<->scheme: find longest common substrings
def norm(t):
    return re.sub(r'\s+', '', t)
cn, sn = norm(c), norm(s)
# candidate duplicated passages from content
probes = [
    'R2的统计基础说明',
    'R4的训练阶段（Year2Q3',
    '弱关联基准（ZnO/MgO',
    '低温HHG工程可行性要点',
    'BaF₂',
    'JanisST-100',
    'Lakeshore336',
    '±5μm',
    '150GPU',
    '三次样条插值',
    'MC Dropout，50次前向传播',
    '两阶段温度扫描',
    '全温基线80–300K',
    '阶段一（Year1Q3）的判定标准',
    '单次完整训练耗时',
]
for p in probes:
    pn = norm(p)
    print(f'DUP "{p[:22]}": content={pn in cn}, scheme={pn in sn}')

# scheme headings
print('\nscheme headings:')
for m in re.finditer(r'^#{1,3} .+$', s, flags=re.M):
    print('  ', m.group(0)[:70])

# exact overlap length of the R2 stats paragraph
m = re.search(r'R2 的统计基础说明：(.{0,400})', c, flags=re.S)
if m:
    frag = norm(m.group(0))[:180]
    print('\nR2 stats frag in scheme:', frag in sn)
m2 = re.search(r'R4 的训练阶段（Year 2 Q3–Year 3 Q3(.{0,300})', c, flags=re.S)
if m2:
    print('R4 training frag in scheme:', norm(m2.group(0))[:150] in sn)

# Ikeda 5-15% contexts
for m in re.finditer(r'5[–-]15\s*%', c + '||SCHEME||' + s):
    side = 'content' if m.start() < len(c) else 'scheme'
    t = c if side == 'content' else s
    off = m.start() if side == 'content' else m.start()-len(c)-9
    print(f'Ikeda 5-15% [{side}]:', t[max(0,off-90):off+60].replace('\n',' ')[:160])

# r>=15 / threshold claim
for m in re.finditer(r'r\s*\\gtrsim\s*15', c):
    print('r15 ctx:', c[max(0,m.start()-120):m.start()+60].replace('\n',' ')[:220])

# 谐波阶次范围 & SNR 10:1 in content
for m in re.finditer(r'10:1', c):
    print('SNR ctx:', c[max(0,m.start()-80):m.start()+40].replace('\n',' ')[:150])

# §2.1 quantified objectives?
print('\nGo/No-Go count in content:', len(re.findall(r'Go 判据|Go：|No-Go', c)))
# word count per section (2.1-2.5)
sec = re.split(r'^### ', c, flags=re.M)
for blk in sec[1:]:
    title = blk.split('\n')[0][:38]
    han = len(re.findall(r'[\u4e00-\u9fff]', blk))
    print(f'section {title}: hanzi={han}')
