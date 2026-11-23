# 临时脚本：过滤 + 预打分（用完即删）
import json, os, re

cands = json.load(open(".tmp_arx_polariton.json"))
raw_names = " ".join(os.listdir("knowledge/raw/papers"))

CUTOFF = "2024-11-13"

# 关键词组：与 10 组检索词对齐（小写匹配）
GROUPS = {
    "polariton_rabi": ["exciton-polariton", "rabi splitting", "rabisplitting"],
    "mos2_cavity": ["mos2", "molybdenum disulfide", "molybdenum disulphide"],
    "lp_up": ["lower polariton", "upper polariton", "lp-up", "up-lip"],
    "coherence": ["coherence time", "dephasing time", "coherence", "dephasing"],
    "tr_shg": ["time-resolved", "time resolved"],
    "transient_nl": ["transient", "nonlinear spectroscopy"],
    "pump_probe_shg": ["pump-probe", "pump probe"],
    "bic_tf": ["bound state in the continuum", "bic"],
    "shg_layers": ["second harmonic generation", "shg"],
    "parity": ["parity", "even layer", "odd layer", "layer-dependent", "2h-mos2", "2h mos2"],
    "tmd": ["tmd", "transition metal dichalcogenide", "monolayer", "monolayers", "moSe2", "wse2", "ws2"],
    "microcavity": ["microcavity", "cavity", "photonic"],
}

def hits(text, kws):
    t = text.lower()
    return sum(1 for k in kws if k in t)

kept, skipped_processed, skipped_old = [], 0, 0
for c in cands:
    if c["published"] < CUTOFF:
        skipped_old += 1
        continue
    if c["arxiv_id"] in raw_names:
        skipped_processed += 1
        continue
    title, abs_ = c["title"], c["abstract"]
    gscore = {}
    for g, kws in GROUPS.items():
        h = 2 * hits(title, kws) + hits(abs_, kws)
        if h:
            gscore[g] = h
    # 综合分：命中组数 + 加权总分，归一化到 0-1
    total = sum(gscore.values())
    ngroups = len(gscore)
    score = min(1.0, 0.35 * ngroups / 6 + 0.65 * min(total, 12) / 12)
    #  Polariton+SHG 主线加成
    if "polariton" in (title + abs_).lower() and ("microcavity" in (title + abs_).lower()):
        score = min(1.0, score + 0.1)
    if "second harmonic" in (title + abs_).lower() and ("pump" in (title + abs_).lower() or "ultrafast" in (title + abs_).lower() or "time-resolved" in (title + abs_).lower()):
        score = min(1.0, score + 0.1)
    c["score"] = round(score, 3)
    c["groups"] = sorted(gscore, key=gscore.get, reverse=True)[:4]
    kept.append(c)

kept.sort(key=lambda x: (-x["score"], x["published"]))
print("total=%d old=%d processed=%d kept=%d" % (len(cands), skipped_old, skipped_processed, len(kept)))
for c in kept[:40]:
    print("%.3f %-10s %s | %s | %s" % (c["score"], c["arxiv_id"], c["published"], c["title"][:95], ",".join(c["groups"])))

json.dump(kept, open(".tmp_arx_polariton_filtered.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
