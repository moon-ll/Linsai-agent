# R3 crossref verification for key cited entries
import json, urllib.request, re

def crossref_doi(doi):
    try:
        req = urllib.request.Request(f"https://api.crossref.org/works/{doi}",
                                     headers={"User-Agent": "nsfc-critic-audit/1.0 (mailto:critic@local)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            m = json.loads(r.read())["message"]
        title = m.get("title", [""])[0][:110]
        auth = ", ".join(a.get("family", "?") for a in m.get("author", [])[:4])
        year = (m.get("issued", {}).get("date-parts", [[None]])[0][0])
        cont = m.get("container-title", [""])[0][:50]
        vol, page = m.get("volume"), m.get("page")
        return f"OK | {auth} | {year} | {cont} | v{vol} p{page} | {title}"
    except Exception as e:
        return f"FAIL {type(e).__name__}: {str(e)[:80]}"

checks = {
    "[26] Aversa-Sipe PRB 49,8869": "10.1103/PhysRevB.49.8869",
    "[7] Rasputnyi Nat.Phys 2024":  "10.1038/s41567-024-02659-x",
    "[28] Raissi JCP 2019":         "10.1016/j.jcp.2018.10.045",
    "[41] Karniadakis NRP 2021":    "10.1038/s42254-021-00314-5",
    "[29] Wilkinson Sci Data 2016": "10.1038/sdata.2016.18",
}
for k, v in checks.items():
    print(k, "->", crossref_doi(v))

# Fazekas-Tosatti 1979: title search
import urllib.parse

def crossref_query(q):
    try:
        url = "https://api.crossref.org/works?query.bibliographic=" + urllib.parse.quote(q) + "&rows=3"
        req = urllib.request.Request(url, headers={"User-Agent": "nsfc-critic-audit/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            items = json.loads(r.read())["message"]["items"]
        out = []
        for m in items:
            out.append(f"{m.get('DOI','?')} | {(m.get('issued',{}).get('date-parts',[[None]])[0][0])} | {(m.get('title',[''])[0])[:80]}")
        return out
    except Exception as e:
        return [f"FAIL {e}"]

print("\nFazekas Tosatti query:")
for line in crossref_query("Fazekas Tosatti Electrical structural magnetic 1T-TaS2 Philosophical Magazine B 1979"):
    print("  ", line)

print("\nAversa Sipe nonlinear optical susceptibilities semiconductors query:")
for line in crossref_query("Aversa Sipe Nonlinear optical susceptibilities of semiconductors tight-binding 1994"):
    print("  ", line)
