#!/usr/bin/env python3
# R5 references full verification: CrossRef DOI lookup + arXiv API batch + title search for published versions
import json, re, time, difflib, urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
from collections import Counter

BASE = "/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-quantum-geometry-inversion-20260726"
text = open(f"{BASE}/04_proposal/sections/references.md").read()

entries = {}
for m in re.finditer(r'^\[(\d+)\]\s+(.+)$', text, re.M):
    entries[int(m.group(1))] = m.group(2).strip()

def parse(e):
    d = {}
    tm = re.search(r'"(.+?)"\s*\.?\s*$', e) or re.search(r'"(.+?)"', e)
    d['title'] = tm.group(1).rstrip('.') if tm else ''
    ym = re.search(r'\((\d{4})', e)
    d['year'] = ym.group(1) if ym else ''
    dm = re.search(r'DOI:\s*(10\.[^\s]+)', e)
    d['doi'] = dm.group(1).rstrip('.') if dm else ''
    am = re.search(r'arXiv:(\d{4}\.\d{4,5})', e)
    d['arxiv'] = am.group(1) if am else ''
    d['family'] = e.split(',')[0].strip()
    jm = re.search(r'\*([^*]+)\*', e)
    d['journal'] = jm.group(1) if jm else ''
    vm = re.search(r'\*\*\s*(\d+)\s*\*\*,?\s*([\w\u2013\-]*)', e)
    d['vol'] = vm.group(1) if vm else ''
    d['page'] = vm.group(2) if vm else ''
    return d

UA = {'User-Agent': 'nsfc-critic-refaudit/5.0 (mailto:critic@example.org)'}

def get_json(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as h:
            if h.code == 404:
                return {'__status__': 404}
            time.sleep(2 * (i + 1))
        except Exception:
            time.sleep(2 * (i + 1))
    return {'__status__': 'fail'}

def norm(s):
    return re.sub(r'[^a-z0-9 ]', '', (s or '').lower()).strip()

def ratio(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()

parsed = {n: parse(e) for n, e in entries.items()}

# 1) arXiv batch query
ids = [d['arxiv'] for d in parsed.values() if d['arxiv']]
arx = {}
try:
    url = f"http://export.arxiv.org/api/query?id_list={','.join(ids)}&max_results=100"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        root = ET.fromstring(r.read())
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    for en in root.findall('a:entry', ns):
        aid = en.find('a:id', ns).text.split('/abs/')[-1]
        aid_base = re.sub(r'v\d+$', '', aid)
        t = en.find('a:title', ns)
        aus = en.findall('a:author/a:name', ns)
        pub = en.find('a:published', ns)
        arx[aid_base] = {'title': ' '.join(t.text.split()) if t is not None else '',
                         'first_author': aus[0].text if aus else '',
                         'published': pub.text[:10] if pub is not None else '',
                         'n_auth': len(aus), 'id': aid}
except Exception as ex:
    print('ARXIV BATCH FAIL', ex)

# 2) CrossRef per-DOI
cr = {}
for n, d in sorted(parsed.items()):
    if not d['doi']:
        continue
    m = get_json(f"https://api.crossref.org/works/{urllib.parse.quote(d['doi'])}")
    if m.get('__status__'):
        cr[n] = m
    else:
        msg = m.get('message', {})
        cr[n] = {'title': (msg.get('title') or [''])[0],
                 'first': (msg.get('author') or [{}])[0].get('family', ''),
                 'container': (msg.get('container-title') or [''])[0],
                 'vol': msg.get('volume', ''), 'page': msg.get('page', ''),
                 'year': (msg.get('issued', {}).get('date-parts') or [['']])[0][0],
                 'type': msg.get('type', '')}
    time.sleep(0.35)

# 3) title search for arXiv-only entries (find published versions)
ts = {}
for n, d in sorted(parsed.items()):
    if d['doi'] or not d['title']:
        continue
    q = urllib.parse.quote(d['title'])
    m = get_json(f"https://api.crossref.org/works?query.bibliographic={q}&rows=2&select=title,author,container-title,volume,page,issued,DOI")
    if not m.get('__status__'):
        items = m.get('message', {}).get('items', [])
        ts[n] = [{'title': (it.get('title') or [''])[0],
                  'first': (it.get('author') or [{}])[0].get('family', ''),
                  'container': (it.get('container-title') or [''])[0],
                  'vol': it.get('volume', ''), 'page': it.get('page', ''),
                  'year': (it.get('issued', {}).get('date-parts') or [['']])[0][0],
                  'doi': it.get('DOI', ''),
                  'sim': round(ratio(d['title'], (it.get('title') or [''])[0]), 2)} for it in items]
    time.sleep(0.35)

out = {'entries': parsed, 'arxiv': arx, 'crossref': cr, 'title_search': ts}
json.dump(out, open(f"{BASE}/05_review/.r5_refs_verify.json", 'w'), ensure_ascii=False, indent=1)

print(f"total={len(parsed)} arxiv_ids={len(ids)} dois={sum(1 for d in parsed.values() if d['doi'])} arxok={len(arx)}")
print('--- ARXIV CHECK (only problems) ---')
for n, d in sorted(parsed.items()):
    if not d['arxiv']:
        continue
    a = arx.get(d['arxiv'])
    if not a:
        print(f"[{n}] arXiv:{d['arxiv']} NOT FOUND IN API")
        continue
    tr = ratio(d['title'], a['title'])
    fam_ok = norm(d['family']) in norm(a['first_author']) or norm(a['first_author'].split()[-1] if a['first_author'] else '') == norm(d['family'])
    flags = []
    if tr < 0.72:
        flags.append(f"title_sim={tr:.2f} entry='{d['title'][:70]}' api='{a['title'][:70]}'")
    if not fam_ok:
        flags.append(f"1st_author entry={d['family']} api={a['first_author']}")
    if a['published'][:4] != d['year']:
        flags.append(f"year entry={d['year']} v1pub={a['published'][:4]}")
    if flags:
        print(f"[{n}] arXiv:{d['arxiv']} " + '; '.join(flags))
print('--- CROSSREF CHECK (only problems) ---')
for n, d in sorted(parsed.items()):
    if not d['doi']:
        continue
    c = cr.get(n)
    if not c or c.get('__status__'):
        print(f"[{n}] DOI {d['doi']} -> {c}")
        continue
    tr = ratio(d['title'], c['title'])
    flags = []
    if tr < 0.72:
        flags.append(f"title_sim={tr:.2f} api='{c['title'][:70]}'")
    if norm(c.get('first', '')) != norm(d['family']):
        flags.append(f"1st entry={d['family']} api={c.get('first')}")
    if str(c.get('year', '')) != d['year']:
        flags.append(f"year entry={d['year']} api={c.get('year')}")
    if c.get('vol') and d['vol'] and str(c['vol']) != d['vol']:
        flags.append(f"vol entry={d['vol']} api={c['vol']}")
    pg = c.get('page', '')
    if pg and d['page'] and not d['page'].startswith(pg.split('-')[0]):
        flags.append(f"page entry={d['page']} api={pg}")
    if flags:
        print(f"[{n}] DOI:{d['doi']} " + '; '.join(flags))
print('--- TITLE SEARCH: arXiv-only entries possibly published (sim>=0.85) ---')
found_any = False
for n, hits in sorted(ts.items()):
    for h in hits:
        if h['sim'] >= 0.85 and h.get('doi'):
            found_any = True
            print(f"[{n}] PUBLISHED?: {h['container']} {h['vol']},{h['page']} ({h['year']}) DOI:{h['doi']} sim={h['sim']} first={h['first']}")
if not found_any:
    print('(none)')
print('--- year distribution ---')
yc = Counter(d['year'] for d in parsed.values())
print(dict(sorted(yc.items())))
recent = sum(v for k, v in yc.items() if k >= '2024')
print(f"2024-2026: {recent}/{len(parsed)} = {recent/len(parsed)*100:.1f}%")
arxonly = [n for n, d in sorted(parsed.items()) if not d['doi']]
print(f"arXiv-only ({len(arxonly)}): {arxonly}")
