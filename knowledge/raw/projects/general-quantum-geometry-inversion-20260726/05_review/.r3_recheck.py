# R3 independent recheck (critic)
import re

paths = {'rationale':'rationale.md','content':'content.md','scheme':'scheme.md','refs':'references.md','full':'full_review.md'}
txt = {k: open(v, encoding='utf-8').read() for k,v in paths.items()}

tot = len(txt['rationale'])+len(txt['content'])+len(txt['scheme'])
print("chars:", {k:len(v) for k,v in txt.items()}, "| concat+4 =", tot+4, "(report says 51970)")
print("content CJK chars:", len(re.findall(r'[\u4e00-\u9fff]', txt['content'])))

c = txt['content']
body = re.sub(r'\$\$.*?\$\$', ' ', c, flags=re.S)
sents = re.split(r'[。！？；]', body)
long_s = [(s.strip()[:60], len(s.strip())) for s in sents if len(s.strip())>120]
print("\ncontent.md >120char sentences:", len(long_s))
for t,l in sorted(long_s, key=lambda x:-x[1])[:8]: print("  ", l, "|", t)

print("\nself-ref 本项目:", len(re.findall(r'本项目', c)), "| 本课题:", len(re.findall(r'本课题', c)))
print("'为..提供':", len(re.findall(r'为[^。]{0,24}提供', c)))
print("在此基础上:", c.count('在此基础上'), "| 此外:", c.count('此外'), "| 同时:", c.count('同时'), "| 因此:", c.count('因此'), "| 然而:", c.count('然而'), "| 基于此:", c.count('基于此'))
print("bold **..**:", len(re.findall(r'\*\*[^*]+\*\*', c)))

for w in ['首次','尚未见','填补','国际领先','国际首创','普适','决定性意义','新的高度']:
    hits = [(c[:m.start()].count('\n')+1, c[max(0,m.start()-25):m.start()+35].replace('\n',' ')) for m in re.finditer(w, c)]
    if hits: print("REDFLAG", w, hits[:4])

cits = sorted(set(int(x) for x in re.findall(r'\[(\d+)', c)))
print("\ncontent.md cites [N]:", cits)

for name in ['Queisser','Lange','NEwwave','NEWWAVE','Ikeda','Khurelbaatar','Rivera-Dean','Fazekos','Aversa','Sumaya','Loaiza','Wilkinson','Karniadakis','Raissi','Tyulnev','Rasputnyi','Ghalgaoui','Goswami','Sala','Yang']:
    where = [k for k,v in txt.items() if name in v]
    print(f"{name}: in {where}")
