#!/usr/bin/env python3
# R7(new cycle) references full-table reverse verification: Crossref + arXiv API
import re, time, json, unicodedata, urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

BASE = "/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-quantum-geometry-inversion-20260726"
REF = BASE + "/04_proposal/sections/references.md"
UA = {"User-Agent": "nsfc-critic-audit/1.0 (mailto: critic-audit@example.org)"}

def fetch(url, timeout=25, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace"), r.status
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, 404
            time.sleep(1.5 * (i + 1))
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None, -1

def norm(s):
    if not s: return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

def sim(a, b):
    return round(SequenceMatcher(None, norm(a), norm(b)).ratio(), 2)

text = open(REF).read()
entries = {}
for m in re.finditer(r"^\[(\d+)\]\s+(.+)$", text, re.M):
    entries[int(m.group(1))] = m.group(2).strip()

claims = {}
for n, line in sorted(entries.items()):
    t = re.search(r'"([^"]+)"', line)
    title = t.group(1).rstrip(".") if t else None
    fa = re.match(r"([A-Za-zÀ-ž''\- ]+?),", line)
    first_author = fa.group(1).strip() if fa else None
    ym = re.findall(r"\((\d{4})", line)
    year = int(ym[0]) if ym else None
    jm = re.search(r"\*([A-Za-z .&]+)\*", line)
    journal = jm.group(1).strip() if jm else None
    vm = re.search(r"\*\*(\d+)\*\*", line)
    vol = vm.group(1) if vm else None
    pm = re.search(r"\*\*\d+\*\*\s*,?\s*([\d]+[–—\-][\d]+|[\w.]+)", line)
    pages = pm.group(1) if pm else None
    stripped = line.replace("https://doi.org/", "")
    dois = [d.rstrip(".,") for d in re.findall(r"10\.\d{4,9}/[^\s,;)\"]+", stripped)]
    doi = next((d for d in dois if not d.startswith("10.48550/")), None)
    ax = re.search(r"arXiv[:\s](\d{4}\.\d{4,5})", line)
    claims[n] = dict(first_author=first_author, year=year, journal=journal, vol=vol,
                     pages=pages, title=title, doi=doi,
                     arxiv=ax.group(1) if ax else None, line=line)

print(f"total entries: {len(entries)}")

# ---------- Crossref ----------
cr = {}
for n, c in claims.items():
    if not c["doi"]:
        continue
    body, st = fetch("https://api.crossref.org/works/" + urllib.parse.quote(c["doi"], safe="/"))
    if st != 200 or not body:
        cr[n] = {"status": st}
        print(f"[{n}] CROSSREF status={st} doi={c['doi']}")
    else:
        j = json.loads(body)["message"]
        au = (j.get("author") or [{}])[0]
        fam = au.get("family") or au.get("name") or ""
        year = None
        for k in ("published-print", "published-online", "issued", "created"):
            d = j.get(k, {}).get("date-parts", [[None]])
            if d and d[0] and d[0][0]:
                year = d[0][0]
                break
        cr[n] = {"status": 200, "title": " ".join(j.get("title") or []),
                 "family": fam, "journal": (j.get("container-title") or [""])[0],
                 "vol": j.get("volume", ""), "pages": j.get("page", ""), "year": year,
                 "nau": len(j.get("author") or [])}
    time.sleep(0.7)

# ---------- arXiv (batched) ----------
arxiv_ids = {n: c["arxiv"] for n, c in claims.items() if c["arxiv"]}
ax = {}
ids = sorted(set(arxiv_ids.values()))
for i in range(0, len(ids), 20):
    chunk = ids[i:i + 20]
    url = "http://export.arxiv.org/api/query?id_list=" + ",".join(chunk) + "&max_results=" + str(len(chunk))
    body, st = fetch(url, timeout=40)
    if not body:
        print(f"ARXIV BATCH FAIL {st}: {chunk}")
        continue
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(body)
    for e in root.findall("a:entry", ns):
        eid = e.find("a:id", ns).text or ""
        m2 = re.search(r"abs/(\d{4}\.\d{4,5})", eid)
        if not m2:
            continue
        t = re.sub(r"\s+", " ", (e.find("a:title", ns).text or "")).strip()
        aus = [(a.find("a:name", ns).text or "") for a in e.findall("a:author", ns)]
        ax[m2.group(1)] = {"title": t, "authors": aus, "first": aus[0] if aus else "",
                           "published": (e.find("a:published", ns).text or "")[:4],
                           "updated": (e.find("a:updated", ns).text or "")[:4],
                           "nau": len(aus)}
    time.sleep(3)

print("\n===== CROSSREF COMPARISON =====")
for n, c in claims.items():
    if n not in cr:
        continue
    r = cr[n]
    if r.get("status") != 200:
        print(f"[{n}] DOI_UNRESOLVED ({r.get('status')}) {c['doi']}")
        continue
    ts = sim(c["title"], r["title"])
    fa_ok = norm(c["first_author"]) and norm(c["first_author"]) in norm(r["family"])
    yr = r["year"]
    flags = []
    if ts < 0.75: flags.append(f"TITLE sim={ts} claimed='{c['title'][:60]}' real='{r['title'][:60]}'")
    if not fa_ok: flags.append(f"AUTHOR claimed='{c['first_author']}' real1st='{r['family']}'")
    if c["year"] and yr and abs(int(c["year"]) - int(yr)) > 1: flags.append(f"YEAR {c['year']} vs {yr}")
    if c["journal"] and norm(c["journal"]) not in norm(r["journal"]) and norm(r["journal"]) not in norm(c["journal"]):
        flags.append(f"JOURNAL '{c['journal']}' vs '{r['journal']}'")
    if c["vol"] and r["vol"] and c["vol"] != str(r["vol"]): flags.append(f"VOL {c['vol']} vs {r['vol']}")
    if c["pages"] and r["pages"] and norm(c["pages"]) != norm(str(r["pages"])):
        flags.append(f"PAGES {c['pages']} vs {r['pages']}")
    print(f"[{n}] {'OK' if not flags else 'MISMATCH'}" + ("" if not flags else " :: " + " | ".join(flags)))

print("\n===== ARXIV COMPARISON =====")
for n, c in claims.items():
    if not c["arxiv"]:
        continue
    r = ax.get(c["arxiv"])
    if not r:
        print(f"[{n}] ARXIV_NOT_FOUND id={c['arxiv']}")
        continue
    ts = sim(c["title"], r["title"])
    allau = norm(" ".join(r["authors"]))
    fa_ok = norm(c["first_author"]) and norm(c["first_author"]) in allau
    first1 = r["first"].split()[-1] if r["first"] else ""
    flags = []
    if ts < 0.75: flags.append(f"TITLE sim={ts} claimed='{c['title'][:60]}' real='{r['title'][:60]}'")
    if not fa_ok: flags.append(f"AUTHOR claimed='{c['first_author']}' real1st='{first1}' ({r['nau']}au)")
    if c["year"] and abs(int(c["year"]) - int(r["published"])) > 0 and abs(int(c["year"]) - int(r["updated"])) > 0:
        flags.append(f"YEAR {c['year']} vs pub{r['published']}/upd{r['updated']}")
    print(f"[{n}] {'OK' if not flags else 'MISMATCH'}" + ("" if not flags else " :: " + " | ".join(flags)))

# ---------- extras ----------
print("\n===== EXTRAS =====")
dup = {}
for n, c in claims.items():
    key = c["doi"] or c["arxiv"]
    dup.setdefault(key, []).append(n)
for k, v in dup.items():
    if k and len(v) > 1:
        print(f"DUPLICATE {k}: {v}")

recent = sum(1 for c in claims.values() if c["year"] and c["year"] >= 2023)
print(f"recency: {recent}/{len(entries)} entries 2023+")

no_id = [n for n, c in claims.items() if not c["doi"] and not c["arxiv"]]
print(f"no identifier: {no_id}")
url_style = [n for n, c in claims.items() if "https://doi.org/" in c["line"]]
print(f"url-style DOI: {len(url_style)} entries {url_style[:30]}")
dual_id = [n for n, c in claims.items() if c["doi"] and c["arxiv"]]
print(f"dual identifier (doi+arxiv): {dual_id}")
etal = [n for n, c in claims.items() if re.search(r",\s*et al", c["line"])]
fullau = [n for n, c in claims.items() if c["line"].count(",") >= 5 and "et al" not in c["line"]]
print(f"'et al.' entries: {etal}")
print(f"full-author-list entries (>5 commas, no et al): {fullau}")
notes = [n for n, c in claims.items() if re.search(r"[\u4e00-\u9fff]", c["line"])]
print(f"entries with Chinese work-notes: {len(notes)} -> {notes}")
preprint_note = [n for n, c in claims.items() if "(preprint)" in c["line"] or "advance online" in c["line"]]
print(f"status annotations: {preprint_note}")

json.dump({"claims": {str(k): v for k, v in claims.items()}, "crossref": {str(k): v for k, v in cr.items()},
           "arxiv": ax}, open(BASE + "/05_review/.r7c_refs_verify.json", "w"), ensure_ascii=False, indent=1)
print("\nsaved .r7c_refs_verify.json")
