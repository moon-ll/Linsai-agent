# 临时脚本：arXiv API 检索 → JSON（用完即删）
import json, re, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "linsai-copilot-researcher/1.0 (literature search)"}

def api(query, max_results=60):
    url = ("https://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": str(max_results),
    }))
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        xml = r.read().decode("utf-8", "replace")
    entries = re.findall(r"<entry>(.*?)</entry>", xml, re.S)
    out = []
    for e in entries:
        def tag(t):
            m = re.search(r"<%s>(.*?)</%s>" % (t, t), e, re.S)
            return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
        aid = tag("id").split("/abs/")[-1]
        title = tag("title")
        summary = tag("summary")
        pub = tag("published")[:10]
        authors = re.findall(r"<name>(.*?)</name>", e)
        cats = re.findall(r'<category term="([^"]+)"', e)
        out.append({"arxiv_id": aid, "title": title, "authors": ", ".join(authors[:6]),
                    "published": pub, "abstract": summary, "categories": cats})
    return out

queries = [
    'cat:cond-mat.supr-con',
    'cat:cond-mat.str-el',
    'cat:cond-mat.mtrl-sci',
    'cat:physics.optics',
    'all:"high harmonic generation" AND all:symmetry',
    'all:"quantum oscillations" AND all:"spin splitting"',
    'all:"pairing symmetry" AND all:"order parameter"',
    'all:"ultrafast" AND all:"order parameter"',
    'all:"spin resonance" AND all:symmetry AND all:"order parameter"',
    'all:"differential" AND all:"reflectivity" AND all:"ultrafast"',
    'all:"order parameter" AND all:"classification" AND all:spectroscopy',
]

seen = {}
for q in queries:
    try:
        res = api(q)
        print("QUERY %-70s -> %d" % (q, len(res)), file=sys.stderr)
        for r in res:
            if r["arxiv_id"] not in seen:
                seen[r["arxiv_id"]] = r
    except Exception as ex:
        print("ERR %s: %s" % (q, ex), file=sys.stderr)
    time.sleep(1)

with open(".tmp_arx_results.json", "w", encoding="utf-8") as f:
    json.dump(list(seen.values()), f, ensure_ascii=False, indent=1)
print("TOTAL %d" % len(seen), file=sys.stderr)
