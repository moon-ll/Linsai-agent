#!/usr/bin/env python3
"""R5 references verification: CrossRef + arXiv full sweep, cache reuse vs R4."""
import json, re, time, sys, urllib.request, urllib.parse, urllib.error, xml.etree.ElementTree as ET
from difflib import SequenceMatcher

BASE = "/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/general-attosecond-streaking-20260822"
REFS = BASE + "/04_proposal/sections/references.md"
CACHE_IN = BASE + "/05_review/_r4_verify_cache.json"
CACHE_OUT = BASE + "/05_review/_r5_verify_cache.json"
MAILTO = "critic-nsfc-audit@example.org"
UA = "Mozilla/5.0 (Macintosh) nsfc-critic-R5/1.0 (mailto:%s)" % MAILTO

def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())

def sim(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()

def parse_refs(path):
    txt = open(path, encoding="utf-8").read()
    entries = {}
    for m in re.finditer(r"^\[(\d+)\](†?)\s+(.+)$", txt, re.M):
        entries[int(m.group(1))] = {"dagger": m.group(2), "raw": m.group(3).strip()}
    return entries

def extract_fields(raw):
    d = {}
    m = re.search(r"DOI:\s*(\S+)", raw)
    if m:
        d["doi"] = m.group(1).rstrip(".;，。；").strip(); d["src"] = "doi"; d["id"] = d["doi"]
    else:
        m = re.search(r"arXiv:(\d{4}\.\d{4,5})", raw)
        if m: d["src"] = "arxiv"; d["id"] = m.group(1); d["doi"] = None
        else: d["src"] = "none"; d["id"] = None; d["doi"] = None
    ym = re.search(r",\s*((?:19|20)\d{2})[\.,]", raw + ",")
    d["listed_year"] = ym.group(1) if ym else None
    parts = raw.split(". ")
    d["first_author"] = parts[0].split(",")[0].strip()
    d["title_guess"] = parts[1] if len(parts) > 2 else None
    vm = re.search(r",\s*(?:19|20)\d{2},\s*(\d+)(?:\((\d+)\))?:\s*([0-9A-Za-z\u03b1-\u03ff-]+(?:-\d+)?)", raw)
    d["vol"] = vm.group(1) if vm else None
    d["page"] = vm.group(3) if vm else None
    return d

def crossref_doi(doi):
    try:
        m = json.loads(http_get("https://api.crossref.org/works/" + urllib.parse.quote(doi)))["message"]
        year = None; online = None
        for k in ("published-print", "published-online", "issued", "created"):
            if m.get(k) and m[k].get("date-parts"):
                dp = m[k]["date-parts"][0]; y = dp[0]
                if y and year is None: year = y
                if k == "published-online" and len(dp) >= 2: online = "%04d-%02d" % (dp[0], dp[1])
        return {"ok": True, "title": " ".join(m.get("title") or [""]),
                "authors": [a.get("family", "") + "|" + a.get("given", "") for a in (m.get("author") or [])],
                "journal": (m.get("container-title") or [""])[0],
                "vol": str(m.get("volume") or ""), "page": str(m.get("page") or m.get("article-number") or ""),
                "year": year, "online": online, "doi": m.get("DOI", "")}
    except urllib.error.HTTPError as e:
        return {"ok": False, "err": "HTTP %d" % e.code}
    except Exception as e:
        return {"ok": False, "err": str(e)[:80]}

def arxiv_meta(aid):
    try:
        root = ET.fromstring(http_get("http://export.arxiv.org/api/query?id_list=" + aid + "&max_results=1"))
        ns = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
        e = root.find("a:entry", ns)
        if e is None: return {"ok": False, "err": "no entry"}
        return {"ok": True, "title": re.sub(r"\s+", " ", e.findtext("a:title", "", ns)).strip(),
                "authors": [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)],
                "journal_ref": e.findtext("ar:journal_ref", None, ns), "doi": e.findtext("ar:doi", None, ns)}
    except Exception as e:
        return {"ok": False, "err": str(e)[:80]}

def main():
    refs = parse_refs(REFS)
    cache = {}
    try: cache = json.load(open(CACHE_IN))
    except Exception: pass
    results, problems = {}, []
    for n in sorted(refs):
        raw = refs[n]["raw"]; fld = extract_fields(raw)
        rec = {"raw": raw, "dagger": refs[n]["dagger"], **fld}
        c = cache.get(str(n), {})
        if c.get("raw") == raw and c.get("truth", {}).get("ok"):
            rec["truth"] = c["truth"]; rec["from_cache"] = True
        elif fld["src"] == "doi":
            rec["truth"] = crossref_doi(fld["doi"]); time.sleep(1.0)
        elif fld["src"] == "arxiv":
            t = arxiv_meta(fld["id"]); time.sleep(0.5)
            if t.get("ok") and t.get("doi"):
                t["cr"] = crossref_doi(t["doi"]); time.sleep(1.0)
            rec["truth"] = t
        else:
            rec["truth"] = {"ok": False, "err": "no id"}
        results[n] = rec
        t = rec["truth"]
        line = "[%d]%s %s" % (n, "†" if refs[n]["dagger"] else " ", rec["src"])
        if not t.get("ok"):
            print(line, "LOOKUP-FAIL:", t.get("err")); problems.append((n, "lookup-fail", t.get("err"))); continue
        if fld["src"] == "doi":
            s = sim(fld["title_guess"], t["title"])
            fam0 = (t["authors"][0].split("|")[0] if t["authors"] else "")
            fam_ok = norm(fam0) in norm(fld["first_author"]) or norm(fld["first_author"]) in norm(fam0)
            vol_ok = (not fld["vol"]) or (fld["vol"] == t["vol"])
            pg = fld["page"] or ""
            pg_ok = (not pg) or norm(pg) == norm(t["page"]) or norm(pg).rstrip("0123456789") == norm(t["page"]).rstrip("0123456789")
            yr = fld["listed_year"]; yr_ok = (not yr) or (int(yr) == t["year"])
            jour_ok = norm(t["journal"]) in norm(raw) if t["journal"] else True
            flags = []
            if s < 0.97: flags.append("TITLE-SIM=%.2f" % s)
            if not fam_ok: flags.append("AUTH1=%s-vs-%s" % (fld["first_author"], fam0))
            if not vol_ok: flags.append("VOL=%s-vs-%s" % (fld["vol"], t["vol"]))
            if not pg_ok: flags.append("PAGE=%s-vs-%s" % (pg, t["page"]))
            if not yr_ok: flags.append("YEAR=%s-vs-%s" % (yr, t["year"]))
            if not jour_ok: flags.append("JOURNAL=%s" % t["journal"][:30])
            if t.get("online") and t["online"] > "2026-09": flags.append("ONLINE=%s" % t["online"])
            print(line, "OK" if not flags else " | ".join(flags))
            for f in flags: problems.append((n, f.split("=")[0], f))
        else:
            s = sim(fld["title_guess"], t["title"])
            a0 = t["authors"][0] if t["authors"] else ""
            fam_ok = norm(fld["first_author"]) in norm(a0.replace(" ", ""))
            flags = []
            if s < 0.97: flags.append("TITLE-SIM=%.2f" % s)
            if not fam_ok: flags.append("AUTH1=%s-vs-%s" % (fld["first_author"], a0))
            if t.get("journal_ref") or t.get("doi"): flags.append("PUBLISHED?jref=%s,doi=%s" % (t.get("journal_ref"), t.get("doi")))
            print(line, "OK" if not flags else " | ".join(flags))
            for f in flags: problems.append((n, f.split("=")[0].split("?")[0], f))
    json.dump(results, open(CACHE_OUT, "w"), ensure_ascii=False, indent=1)
    print("\n--- summary ---")
    print("entries:", len(results))
    yrs = [int(r["listed_year"]) for r in results.values() if r["listed_year"]]
    print("2023+:", sum(1 for y in yrs if y >= 2023), "/", len(yrs),
          " 2024+:", sum(1 for y in yrs if y >= 2024), "/", len(yrs))
    print("dagger:", sum(1 for r in results.values() if r["dagger"]))
    print("problem flags:", len(problems))
    for p in problems: print("  ", p)

if __name__ == "__main__":
    main()
