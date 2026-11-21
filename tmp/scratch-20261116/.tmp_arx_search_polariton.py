# 临时脚本：arXiv API 检索 → JSON（用完即删）
# 主题：TMD 微腔激子极化激元 Rabi 分裂 / 退相时间 / SHG 超快光谱 / BIC 时频测量
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
    'all:"exciton-polariton" AND all:microcavity AND all:"Rabi splitting"',
    'all:polariton AND all:microcavity AND all:MoS2',
    'all:polariton AND all:microcavity AND all:"transition metal dichalcogenide"',
    'all:"second harmonic generation" AND all:MoS2 AND all:ultrafast',
    'all:"pump-probe" AND all:"second harmonic generation"',
    'all:"time-resolved" AND all:"second harmonic generation" AND all:monolayer',
    'all:"bound state in the continuum" AND all:"time-frequency"',
    'all:"coherence time" AND all:polariton AND all:microcavity',
    'all:"nonlinear spectroscopy" AND all:"transition metal dichalcogenide"',
    'all:"upper polariton" AND all:"lower polariton" AND all:splitting',
]

seen = {}
for q in queries:
    try:
        res = api(q)
        print("QUERY %-70s -> %d" % (q, len(res)), file=sys.stderr)
        for r in res:
            base = re.sub(r"v\d+$", "", r["arxiv_id"])
            if base not in seen:
                r["arxiv_id"] = base
                seen[base] = r
    except Exception as ex:
        print("ERR %s: %s" % (q, ex), file=sys.stderr)
    time.sleep(1)

with open(".tmp_arx_polariton.json", "w", encoding="utf-8") as f:
    json.dump(list(seen.values()), f, ensure_ascii=False, indent=1)
print("TOTAL %d" % len(seen), file=sys.stderr)
