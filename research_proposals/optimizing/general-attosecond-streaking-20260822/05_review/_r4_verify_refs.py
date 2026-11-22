#!/usr/bin/env python3
"""R4 references verification: CrossRef + arXiv full sweep with cache reuse."""
import json, re, time, sys, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET

BASE = "/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-attosecond-streaking-20260822"
REFS = BASE + "/04_proposal/sections/references.md"
CACHE_IN = BASE + "/05_review/_r1_verify_cache_v2.json"
CACHE_OUT = BASE + "/05_review/_r4_verify_cache.json"

MAILTO = "critic-nsfc-audit@example.org"
UA = "Mozilla/5.0 (Macintosh) nsfc-critic-R4/1.0 (mailto:%s)" % MAILTO

def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.getallcontent() if hasattr(r, "getallcontent") else r.read()

def norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s

def parse_refs(path):
    txt = open(path, encoding="utf-8").read()
    entries = {}
    for m in re.finditer(r"^\[(\d+)\](†?)\s+(.+)$", txt, re.M):
        n = int(m.group(1)); entries[n] = {"dagger": m.group(2), "raw": m.group(3).strip()}
    return entries

def extract_fields(raw):
    d = {}
    d["doi"] = (re.search(r"DOI:\s*(\S+)", raw) or [None, None])[1]
    if d["doi"]:
        d["doi"] = d["doi"].rstrip(".;，。；").strip()
        d["src"] = "doi"
        d["id"] = d["doi"]
    else:
        m = re.search(r"arXiv:(\d{4}\.\d{4,5})", raw)
        if m:
            d["src"] = "arxiv"; d["id"] = m.group(1)
        else:
            d["src"] = "none"; d["id"] = None
    ym = re.search(r",\s*((?:19|20)\d{2})[\.,]", raw + ",")
    d["listed_year"] = ym.group(1) if ym else None
    # first author family name = text before first comma of the author block (before title period)
    head = raw.split(". ")[0]
    d["first_author"] = head.split(",")[0].strip()
    # title heuristic: first sentence ending ". " after author block
    parts = raw.split(". ")
    d["title_guess"] = parts[1] if len(parts) > 2 else None
    return d

def crossref_doi(doi):
    try:
        j = json.loads(http_get("https://api.crossref.org/works/" + urllib.parse.quote(doi)))
        m = j["message"]
        title = " ".join(m.get("title") or [""])
        auths = [a.get("family", "") for a in (m.get("author") or [])]
        year = None
        for k in ("published-print", "published-online", "issued", "created"):
            if m.get(k) and m[k].get("date-parts"):
                y = m[k]["date-parts"][0][0]
                if y: year = y; break
        return {"ok": True, "title": title, "authors": auths,
                "journal": (m.get("container-title") or [""])[0],
                "vol": str(m.get("volume") or ""), "page": str(m.get("page") or m.get("article-number") or ""),
                "year": year, "doi": m.get("DOI", "")}
    except urllib.error.HTTPError as e:
        return {"ok": False, "err": "HTTP %d" % e.code}
    except Exception as e:
        return {"ok": False, "err": str(e)[:80]}

def arxiv_meta(aid):
    try:
        xmlb = http_get("http://export.arxiv.org/api/query?id_list=" + aid + "&max_results=1")
        root = ET.fromstring(xmlb)
        ns = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
        e = root.find("a:entry", ns)
        if e is None: return {"ok": False, "err": "no entry"}
        title = re.sub(r"\s+", " ", (e.findtext("a:title", "", ns) or "")).strip()
        auths = [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)]
        jref = e.findtext("ar:journal_ref", None, ns)
        doi = e.findtext("ar:doi", None, ns)
        return {"ok": True, "title": title, "authors": auths, "journal_ref": jref, "doi": doi}
    except Exception as e:
        return {"ok": False, "err": str(e)[:80]}

def crossref_title_search(title, year=None):
    q = urllib.parse.quote("bibliographic:" + title)
    url = ("https://api.crossref.org/works?query.bibliographic=%s&rows=3&mailto=%s"
           % (urllib.parse.quote(title), MAILTO))
    try:
        j = json.loads(http_get(url))
        out = []
        for m in j["message"]["items"]:
            t = " ".join(m.get("title") or [""])
            out.append({"title": t, "doi": m.get("DOI", ""),
                        "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                        "journal": (m.get("container-title") or [""])[0]})
        return out
    except Exception as e:
        return [{"err": str(e)[:80]}]

def main():
    refs = parse_refs(REFS)
    cache = json.load(open(CACHE_IN)) if len(sys.argv) > 1 and sys.argv[1] == "cached" else {}
    results = {}
    only = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] else None
    for n in sorted(refs):
        if only and n not in only: continue
        raw = refs[n]["raw"]
        fld = extract_fields(raw)
        key = raw
        hit = cache.get(str(n), {}).get("raw") == raw and cache.get(str(n), {}).get("truth", {}).get("ok")
        rec = {"raw": raw, "dagger": refs[n]["dagger"], **fld}
        if hit:
            rec["truth"] = cache[str(n)]["truth"]
            rec["from_cache"] = True
        elif fld["src"] == "doi":
            rec["truth"] = crossref_doi(fld["id"]); time.sleep(1.0)
        elif fld["src"] == "arxiv":
            t = arxiv_meta(fld["id"]); time.sleep(0.5)
            if t.get("ok") and t.get("doi"):
                t["cr"] = crossref_doi(t["doi"]); time.sleep(1.0)
            elif t.get("ok"):
                t["cr_hits"] = crossref_title_search(t["title"]); time.sleep(1.0)
            rec["truth"] = t
        else:
            rec["truth"] = {"ok": False, "err": "no id"}
        results[n] = rec
        status = "OK" if rec["truth"].get("ok") else "FAIL:" + str(rec["truth"].get("err"))
        print("[%d] %s %s" % (n, rec["src"], status), flush=True)
    json.dump(results, open(CACHE_OUT, "w"), ensure_ascii=False, indent=1)
    print("saved ->", CACHE_OUT)

if __name__ == "__main__":
    main()
