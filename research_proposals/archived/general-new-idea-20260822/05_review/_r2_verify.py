# R2 references verification: CrossRef DOI lookup + arXiv abs page check
import json, re, time, urllib.request, urllib.error, urllib.parse, sys

UA = {"User-Agent": "Mozilla/5.0 (ref-audit; mailto:critic@example.org)",
      "Accept": "application/json"}

# n: (doi_or_None, first_author_family, year, journal, volume, page/artnum, title_snippet)
REFS = {
1: ("10.1038/nphys1847", "Ghimire", 2011, "Nature Physics", "7", "138-141", "Observation of high-order harmonic generation in a bulk crystal"),
2: ("10.1126/science.aam8861", "Yoshikawa", 2017, "Science", "356", "736-738", "High-harmonic generation in graphene enhanced by elliptically polarized light excitation"),
3: ("10.1038/nphys3946", "Liu", 2017, "Nature Physics", "13", "262-265", "High-harmonic generation from an atomically thin semiconductor"),
4: ("10.1103/PhysRevLett.113.073901", "Vampa", 2014, "Physical Review Letters", "113", "073901", "Theoretical analysis of high-harmonic generation in solids"),
5: ("10.1103/PhysRevB.94.115164", "Luu", 2016, "Physical Review B", "94", "115164", "High-order harmonic generation in solids: A unifying approach"),
6: ("10.1103/PhysRevX.12.031042", "Šmejkal", 2022, "Physical Review X", "12", "031042", "Beyond conventional ferromagnetism and antiferromagnetism"),
7: ("10.1038/s41586-023-06907-7", "Krempaský", 2024, "Nature", "626", "517-522", "Altermagnetic lifting of Kramers spin degeneracy"),
8: ("10.1038/s41586-026-10902-z", "Long", 2026, "Nature", "656", "854-860", "3D bulk-resolved g-wave altermagnetic order parameter in CrSb"),
9: ("10.1103/PhysRevLett.133.206401", "Ding", 2024, "Physical Review Letters", "133", "206401", "Large band splitting in g-wave altermagnet CrSb"),
10: ("10.1038/s41467-024-46476-5", "Reimers", 2024, "Nature Communications", "15", "2116", "Direct observation of altermagnetic band splitting in CrSb thin films"),
11: ("10.1038/s41467-025-56647-7", "Yang", 2025, "Nature Communications", "16", "1442", "Three-dimensional mapping of the altermagnetic spin splitting in CrSb"),
12: (None, "Dal Din", 2025, "arXiv:2511.01690", "", "", "Unconventional relativistic spin polarization of electronic bands in an altermagnet"),
13: ("10.1103/PhysRevB.109.115102", "Osumi", 2024, "Physical Review B", "109", "115102", "Observation of a giant band splitting in altermagnetic MnTe"),
14: (None, "Usanov", 2026, "arXiv:2603.16635", "", "", "Discerning ground state and photoemission-induced spin textures in altermagnetic α-MnTe"),
15: (None, "Zeng", 2025, "arXiv:2511.02447", "", "", "Non-altermagnetic spin texture in MnTe"),
16: ("10.1103/PhysRevB.110.235101", "Werner", 2024, "Physical Review B", "110", "235101", "High harmonic generation in altermagnets"),
17: ("10.1103/ypfs-fy39", "Haag", 2026, "Physical Review Materials", "10", "074413", "Signatures of bulk g-wave altermagnetism in optically excited α-MnTe"),
18: (None, "Mizuno", 2026, "arXiv:2606.31573", "", "", "High-harmonic spin-current signatures of altermagnetic spin-group symmetry"),
19: ("10.1186/s40580-026-00536-2", "Liu", 2026, "Nano Convergence", "13", "6", "Symmetry-driven spin splitting in altermagnets: an angle-resolved photoemission spectroscopy perspective"),
20: ("10.1088/1361-648X/ae6385", "Ly", 2026, "J. Phys.: Condens. Matter", "38", "175803", "High-harmonic spin and charge pumping in altermagnets"),
21: ("10.1103/9gv7-vhxw", "Liu", 2025, "Physical Review Letters", "112", "L081105", "Anisotropic high harmonic generation as a gauge of altermagnetism in RuO2"),
22: ("10.1103/PhysRevLett.118.087403", "Tancogne-Dejean", 2017, "Physical Review Letters", "118", "087403", "Impact of the electronic band structure in high-harmonic generation spectra of solids"),
23: ("10.1038/nature14652", "Hohenleutner", 2015, "Nature", "523", "572-575", "Real-time observation of interfering crystal electrons in high-harmonic generation"),
24: ("10.1016/j.progsurf.2025.100795", "Suzuki", 2025, "Progress in Surface Science", "100", "100795", "Time-resolved photoemission spectroscopy of quantum materials using high harmonic generation"),
25: ("10.1038/s41586-024-08234-x", "Amin", 2024, "Nature", "636", "348-353", "Nanoscale imaging and control of altermagnetism in MnTe"),
26: ("10.1103/m8lc-f8gk", "Liu", 2026, "Physical Review Letters", "136", "236705", "Observation of switchable chiral magnons in an altermagnet"),
27: ("10.1038/s42005-025-02232-9", "Li", 2025, "Communications Physics", "8", "311", "Topological Weyl altermagnetism in CrSb"),
28: ("10.1103/PhysRevLett.132.036702", "Lee", 2024, "Physical Review Letters", "132", "036702", "Broken Kramers degeneracy in altermagnetic MnTe"),
29: (None, "Jaeschke-Ubiergo", 2025, "arXiv:2503.10797", "", "", "Atomic altermagnetism"),
30: ("10.7498/aps.66.134207", "Liu", 2017, "Acta Physica Sinica", "66", "134207", "High harmonic generation experiments based on solid-state supercontinuum"),
31: ("10.1038/s41566-018-0129-0", "Silva", 2018, "Nature Photonics", "12", "266-270", "High-harmonic spectroscopy of ultrafast many-body dynamics in strongly correlated systems"),
32: ("10.1038/nature14517", "Vampa", 2015, "Nature", "522", "462-464", "Linking high harmonics from gases and solids"),
}

ARXIV = {12: "2511.01690", 14: "2603.16635", 15: "2511.02447", 18: "2606.31573",
         19: "2602.13590", 20: "2602.09738", 26: "2605.14124", 27: "2405.14777",
         29: "2503.10797"}

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def crossref(doi):
    body = fetch("https://api.crossref.org/works/" + urllib.request.quote(doi))
    m = json.loads(body)["message"]
    title = m.get("title", [""])[0]
    ct = (m.get("container-title") or [""])[0]
    vol = m.get("volume", "")
    page = m.get("page") or m.get("article-number", "")
    issued = m.get("issued", {}).get("date-parts", [[None]])[0][0]
    fam = ""
    if m.get("author"):
        fam = m["author"][0].get("family", "") or m["author"][0].get("name", "")
    given = m["author"][0].get("given", "") if m.get("author") else ""
    return dict(title=title, journal=ct, vol=vol, page=str(page), year=issued, fam=fam, given=given)

out = []
for n in sorted(REFS):
    doi, fam, yr, jr, vol, pg, ti = REFS[n]
    if not doi:
        continue
    try:
        c = crossref(doi)
        flags = []
        if norm(fam.split()[-1]) not in norm(c["fam"]) and norm(c["fam"]) not in norm(fam):
            flags.append("AUTHOR")
        if c["year"] != yr:
            flags.append(f"YEAR({c['year']})")
        if norm(vol) != norm(c["vol"]):
            flags.append(f"VOL({c['vol']})")
        if norm(pg).replace(" ", "") != norm(c["page"]).replace(" ", ""):
            flags.append(f"PAGE({c['page']})")
        jok = norm(jr).split()[0] in norm(c["journal"]) or norm(c["journal"]).split()[0] in norm(jr)
        if not jok:
            flags.append(f"JOURNAL({c['journal']})")
        tok = norm(ti)[:25] in norm(c["title"]) or norm(c["title"])[:25] in norm(ti)
        if not tok:
            flags.append("TITLE")
        out.append((n, "OK " if not flags else " ".join(flags), c))
        print(f"[{n:2d}] {';'.join(flags) if flags else 'MATCH'} | {c['fam']} {c['year']} {c['journal']} v{c['vol']} p{c['page']} | {c['title'][:70]}")
    except urllib.error.HTTPError as e:
        print(f"[{n:2d}] HTTP_{e.code} {doi}")
        out.append((n, f"HTTP_{e.code}", doi))
    except Exception as e:
        print(f"[{n:2d}] ERR {type(e).__name__}: {e}")
        out.append((n, "ERR", str(e)[:80]))
    time.sleep(0.4)

print("\n===== arXiv abs checks =====")
for n, aid in sorted(ARXIV.items()):
    try:
        html = fetch(f"https://arxiv.org/abs/{aid}")
        t = re.search(r'<meta name="citation_title" content="([^"]+)"', html)
        a1 = re.findall(r'<meta name="citation_author" content="([^"]+)"', html)
        d = re.search(r'<meta name="citation_date" content="([^"]+)"', html)
        print(f"[{n:2d}] {aid} | {(a1[0] if a1 else '?')} | {d.group(1) if d else '?'} | {t.group(1)[:70] if t else '?'}")
    except Exception as e:
        print(f"[{n:2d}] {aid} ERR {type(e).__name__}: {str(e)[:60]}")
    time.sleep(0.5)
