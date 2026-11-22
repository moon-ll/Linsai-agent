# -*- coding: utf-8 -*-
"""R2 scheme 评审辅助计数：scheme 本地 AI 模式计数 + 历史遗留问题 grep 核验"""
import re, statistics

BASE = '/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-berry-mnps3-rashba-20260816/04_proposal/sections/'
scheme = open(BASE + 'scheme.md', encoding='utf-8').read()
content = open(BASE + 'content.md', encoding='utf-8').read()
rationale = open(BASE + 'rationale.md', encoding='utf-8').read()

print('=== scheme.md 本地计数 ===')
print('chars =', len(scheme))

print('\n-- 关联词 --')
for w in ['在此基础上', '此外', '与此同时', '因此', '然而', '基于此', '同时', '进而', '据此']:
    n = scheme.count(w)
    if n:
        print(f'  [{w}] x{n}')

tpl = re.findall(r'为[^。，；]{0,28}提供', scheme)
print('\n-- 为...提供 类句式:', len(tpl), tpl)

print('\n-- 冗余修饰 --')
for w in ['显著', '重要', '系统', '良好', '成熟', '完整', '关键', '精准', '有效', '一系列']:
    n = scheme.count(w)
    if n:
        print(f'  [{w}] x{n}')

def sentences(text):
    out = []
    for i, ln in enumerate(text.split('\n'), 1):
        for s in re.split(r'[。？！；]', ln):
            s = s.strip()
            if len(re.sub(r'\s', '', s)) > 10:
                out.append((i, len(re.sub(r'\s', '', s)), s))
    return out

ss = sentences(scheme)
lens = [l for _, l, _ in ss]
print(f'\n-- 句统计: 句数={len(ss)} 中位={statistics.median(lens)}')
n80 = sum(1 for l in lens if l > 80)
n120 = sum(1 for l in lens if l > 120)
print(f'  >80字: {n80} ({n80/len(lens)*100:.1f}%)  >120字: {n120} ({n120/len(lens)*100:.1f}%)')
print('  >120字清单:')
for i, l, s in ss:
    if l > 120:
        print(f'    L{i} ({l}字): {s[:52]}...')

print('\n-- 引用体例 --')
print('  [N] 角标:', re.findall(r'\[\d+\]', scheme))
print('  文献N 散文:', re.findall(r'文献\s*\d+', scheme))
print('  裸arXiv:', re.findall(r'\d{4}\.\d{4,5}', scheme))

print('\n-- 声明性用词 --')
for w in ['首次', '从未', '尚未', '唯一', '国际领先', '填补空白', '证明']:
    n = scheme.count(w)
    if n:
        print(f'  [{w}] x{n}')

print('\n=== content.md 历史问题核验 ===')
css = sentences(content)
c120 = [(i, l) for i, l, _ in css if l > 120]
print('content >120字句数:', len(c120), '位置:', c120)
print('content 裸arXiv:', re.findall(r'\d{4}\.\d{4,5}', content))
for pat in ['三个特征', '两个特征', '[18]', '[22]', '[21]', '[17]', '针对瓶颈', '0.3 MV/cm', '90%', '70%']:
    print(f'  content 含[{pat}]:', pat in content or bool(re.search(re.escape(pat).replace(r'\[', '\\['), content)))
for m in re.finditer(r'.{18}\[1[78]\].{18}|.{18}\[2[12]\].{18}', content):
    print('   ctx:', m.group(0).replace('\n', ' '))

print('\n=== rationale.md 核验 ===')
print('rationale [首次] x', rationale.count('首次'), '; [11] x', len(re.findall(r'\[11\]', rationale)))
print('rationale 裸arXiv:', re.findall(r'\d{4}\.\d{4,5}', rationale))

print('\n=== 跨章关键数值对齐 ===')
pairs = [('D_sep', '重叠积分', scheme, content), ('信噪比之比', '', content, scheme)]
print('scheme 含"信噪比之比":', '信噪比之比' in scheme, '; content 含"信噪比之比":', '信噪比之比' in content)
print('scheme 含"重叠积分":', '重叠积分' in scheme, '; content 含"重叠积分":', '重叠积分' in content)
print('content S_ell 定义(谐波椭圆度对驱动椭圆度):', '谐波椭圆度对驱动椭圆度的导数' in content)
print('scheme S_ell 定义(∂I_n/∂ε):', '∂I_n/∂ε' in scheme)
print('scheme "0.4 V/Å":', scheme.count('0.4 V/Å'), '; content "0.4 V/Å":', content.count('0.4 V/Å'))
print('scheme "0.5–3.0 THz" x', scheme.count('0.5–3.0 THz'), '; "16–40 meV" x', scheme.count('16–40 meV'))
print('scheme R2 时序(Y1Q3):', 'Year 1 Q3' in scheme, '; R3 时序(Y1Q4):', 'Year 1 Q4' in scheme)
print('scheme 表格 R2 首现行含 "Year 2 Q3":', 'Year 2 Q3' in scheme, '; "R3 启动":', 'R3 启动' in scheme)
print('scheme 含 "content.md §2.3":', 'content.md §2.3' in scheme, '; "content 2.4":', 'content 2.4' in scheme)
print('content 时域层次句在 §2.4 (L35):', '真正可时域分离的只有' in content)
