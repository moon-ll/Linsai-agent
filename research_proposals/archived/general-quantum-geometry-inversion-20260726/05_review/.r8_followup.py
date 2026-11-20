#!/usr/bin/env python3
# R8 follow-up: pinpoint checks for [9][12][13][26][27] + Sodemann + new-entry diff vs R6 audit
import json, re, time, urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET

BASE = "/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-quantum-geometry-inversion-20260726"
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

def cr_doi(doi):
    body, st = fetch("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
    if st != 200:
        return {"status": st}
    j = json.loads(body)["message"]
    au = [(a.get("family", "") + ", " + a.get("given", "")) for a in (j.get("author") or [])]
    yr = None
    for k in ("published-print", "published-online", "issued", "created"):
        d = j.get(k, {}).get("date-parts", [[None]])
        if d and d[0] and d[0][0]:
            yr = d[0][0]; break
    return {"status": 200, "title": " ".join(j.get("title") or []), "authors": au,
            "journal": (j.get("container-title") or [""])[0], "vol": j.get("volume", ""),
            "pages": j.get("page", ""), "year": yr}

def cr_title(q, rows=3):
    url = ("https://api.crossref.org/works?query.bibliographic=" + urllib.parse.quote(q) +
           f"&rows={rows}&select=title,author,container-title,volume,page,issued,DOI")
    body, st = fetch(url)
    if st != 200:
        return {"status": st, "items": []}
    j = json.loads(body)["message"]
    out = []
    for it in j.get("items", []):
        au = [(a.get("family", "")) for a in (it.get("author") or [])]
        d = it.get("issued", {}).get("date-parts", [[None]])
        out.append({"title": " ".join(it.get("title") or []), "first": au[0] if au else "",
                    "jr": (it.get("container-title") or [""])[0], "vol": it.get("volume", ""),
                    "pg": it.get("page", ""), "yr": d[0][0] if d and d[0] else None,
                    "doi": it.get("DOI", "")})
    return {"status": 200, "items": out}

def arxiv_abs(iid):
    body, st = fetch("http://export.arxiv.org/api/query?id_list=" + iid)
    if st != 200:
        return {"status": st}
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(body)
    e = root.find("a:entry", ns)
    if e is None:
        return {"status": -2}
    aus = [(a.find("a:name", ns).text or "") for a in e.findall("a:author", ns)]
    return {"status": 200,
            "title": re.sub(r"\s+", " ", e.find("a:title", ns).text or "").strip(),
            "authors": aus,
            "abstract": re.sub(r"\s+", " ", (e.find("a:summary", ns).text or "")).strip()[:900],
            "published": (e.find("a:published", ns).text or "")[:10],
            "updated": (e.find("a:updated", ns).text or "")[:10]}

print("== [26] candidates ==")
print("R7-rec  PRB 52,14636 DOI:", json.dumps(cr_doi("10.1103/PhysRevB.52.14636"), ensure_ascii=False))
print("title-q 'Model of high-order harmonic generation in semiconductors':")
for it in cr_title("Model of high-order harmonic generation in semiconductors Aversa Sipe")["items"]:
    print("   ", json.dumps(it, ensure_ascii=False))

print("\n== [27] Fazekas-Tosatti DOI candidates ==")
print("10.1080/13642817908245359 ->", json.dumps(cr_doi("10.1080/13642817908245359"), ensure_ascii=False)[:400])

print("\n== Sodemann & Fu ==")
for it in cr_title("Sodemann Fu nonlinear Hall effect Berry curvature dipole")["items"][:2]:
    print("   ", json.dumps(it, ensure_ascii=False))

for tag, iid in [("[9]", "2406.17845"), ("[12]", "2604.13901"), ("[13]", "2508.00296")]:
    r = arxiv_abs(iid)
    print(f"\n== {tag} arXiv:{iid} ==")
    print(json.dumps(r, ensure_ascii=False, indent=1)[:1600])

print("\n== R6-audit vs R8 list diff ==")
try:
    r6 = json.load(open(BASE + "/02_literature/audit-r6-references.json"))
    olds = set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("arxiv", "arxiv_id", "id") and isinstance(v, str) and re.match(r"^\d{4}\.\d{4,5}", v):
                    olds.add(v.split("v")[0])
                walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(r6)
    new = {"2406.17845": 9, "2604.13901": 12, "2508.00296": 13, "2605.03794": 15, "2602.16454": 16,
           "2605.28236": 17, "2606.06999": 18, "2510.15207": 19, "2503.15932": 20, "2605.21925": 21,
           "2606.22714": 22, "2512.24553": 23, "2512.23538": 24, "2405.13885": 25, "2412.13329": 44,
           "2406.02257": 45, "2506.03251": 46, "2602.04370": 47}
    known = set(new)
    print("R6 audit arXiv ids found:", len(olds))
    print("current-list arXiv ids NOT in R6 audit pool:", sorted(known - olds))
except FileNotFoundError as e:
    print("R6 audit file missing:", e)
