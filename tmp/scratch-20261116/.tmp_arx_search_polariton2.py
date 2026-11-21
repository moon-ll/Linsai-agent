# 临时脚本：补充检索（用完即删）
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
    'all:"second harmonic generation" AND all:"transition metal dichalcogenide"',
    'all:"second harmonic generation" AND all:parity',
    'all:"second harmonic generation" AND all:"even layers"',
    'all:"bound states in the continuum" AND all:"time-frequency"',
    'all:"time-frequency resolved" AND all:"bound state"',
    'all:"Rabi splitting" AND all:monolayer AND all:microcavity',
    'all:polariton AND all:dephasing AND all:TMD',
    'all:"polariton" AND all:"MoS2" AND all:"coherence"',
    'all:"second harmonic generation" AND all:WS2 AND all:ultrafast',
    'all:"second harmonic generation" AND all:"3R-MoS2"',
    'all:"cavity" AND all:"exciton-polariton" AND all:"meV" AND all:"monolayer"',
    'all:"ultrafast" AND all:"second harmonic" AND all:"valley"',
]

prev = json.load(open(".tmp_arx_polariton.json"))
seen = {re.sub(r"v\d+$", "", r["arxiv_id"]): r for r in prev}
new = 0
for q in queries:
    try:
        res = api(q)
        print("QUERY %-70s -> %d" % (q, len(res)), file=sys.stderr)
        for r in res:
            base = re.sub(r"v\d+$", "", r["arxiv_id"])
            if base not in seen:
                r["arxiv_id"] = base
                seen[base] = r
                new += 1
    except Exception as ex:
        print("ERR %s: %s" % (q, ex), file=sys.stderr)
    time.sleep(1)

with open(".tmp_arx_polariton.json", "w", encoding="utf-8") as f:
    json.dump(list(seen.values()), f, ensure_ascii=False, indent=1)
print("TOTAL %d NEW %d" % (len(seen), new), file=sys.stderr)
