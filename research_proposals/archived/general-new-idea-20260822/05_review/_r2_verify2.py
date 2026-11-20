# Pass 2: (a) et-al entries first-6 author check vs CrossRef; (b) pure-arXiv journal_ref check
import json, re, time, urllib.request, urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (ref-audit; mailto:critic@example.org)"}

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

# entries using "et al." — verify the named authors are the true first authors (count varies)
ETAL = {
7:  ("10.1038/s41586-023-06907-7", ["Krempaský","Šmejkal","D'Souza","Hajlaoui","Springholz"]),
8:  ("10.1038/s41586-026-10902-z", ["Long","Weinberger","Wu","Hansen","Tao","Shrestha"]),
9:  ("10.1103/PhysRevLett.133.206401", ["Ding","Jiang","Chen","Tao","Liu"]),
10: ("10.1038/s41467-024-46476-5", ["Reimers","Odenbreit","Šmejkal","Strocov","Constantinou"]),
11: ("10.1038/s41467-025-56647-7", ["Yang","Li","Yang","Li","Zheng"]),
25: ("10.1038/s41586-024-08234-x", ["Amin","Dal Din","Golias","Niu","Zakharov"]),
28: ("10.1103/PhysRevLett.132.036702", ["Lee","Lee","Jung","Jung","Kim"]),
}

def skel(s):
    return re.sub(r"[^a-z]", "", s.lower())

for n, (doi, named) in sorted(ETAL.items()):
    m = json.loads(fetch("https://api.crossref.org/works/" + urllib.parse.quote(doi)))["message"]
    fams = [a.get("family", "") for a in (m.get("author") or [])]
    ok = len(fams) >= len(named) + 1 and all(skel(named[i]) == skel(fams[i]) for i in range(len(named)))
    print(f"[{n:2d}] total_au={len(fams)} named_ok={ok} first6={fams[:6]}")

print("\n===== pure-arXiv journal_ref / DOI fields =====")
for n, aid in [(12, "2511.01690"), (14, "2603.16635"), (15, "2511.02447"), (18, "2606.31573"), (29, "2503.10797")]:
    html = fetch(f"https://arxiv.org/abs/{aid}")
    jr = re.search(r'jref[^<]*<[^>]*>([^<]+)<', html) or re.search(r'journal_ref[^>]*>([^<]+)<', html)
    doi = re.search(r'doi\.org/([^\s"<]+)|doi\.org%20?([^<\s"]+)', html)
    # arXiv abs pages list "Journal ref" in table rows
    m2 = re.search(r'Journal\s*ref\.?.{0,200}?</td>\s*<td[^>]*>(.*?)</td>', html, re.S)
    m3 = re.search(r'Journal\s*ref\.?.{0,200}?<td[^>]*>(.*?)</td>', html, re.S)
    row = (m2 or m3)
    txt = re.sub(r'<[^>]+>', ' ', row.group(1)).strip() if row else ""
    # also DOI row
    drow = re.search(r'(?:doi|DOI).{0,200}?</td>\s*<td[^>]*>(.*?)</td>', html, re.S)
    dtxt = re.sub(r'<[^>]+>', ' ', drow.group(1)).strip() if drow else ""
    print(f"[{n:2d}] {aid} | jref_row='{txt[:90]}' | doi_row='{dtxt[:60]}'")
    time.sleep(0.4)

print("\n===== [19] arXiv 2602.13590 full author list (journal-vs-arXiv identity) =====")
html = fetch("https://arxiv.org/abs/2602.13590")
aus = re.findall(r'<meta name="citation_author" content="([^"]+)"', html)
print("arXiv authors:", aus[:8], f"... total {len(aus)}")
