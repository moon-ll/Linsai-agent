"""复刻 optimize.py _detect_ai_patterns 的程序化检测口径，用于 writer 修订自检。

用途：修改章节后重跑，确认表达质量天花板各分项的实际数值。
只读章节文件，不写入任何正文。
"""
import re
import sys

BASE = ("/Users/ll/Desktop/LinSai-CoPilot/research_proposals/optimizing/"
        "general-floquet-20261107/04_proposal/sections/")

FILES = ["rationale.md", "content.md", "scheme.md"]

AI_TERM_WHITELIST = [
    "关键科学问题", "关键难点", "系统误差", "系统偏差", "系统性",
    "有效性", "同时电离", "同时或近同时电离", "同时性",
]
REDUNDANT_WORDS = ["显著", "重要", "系统", "良好", "成熟", "完整", "关键",
                   "精准", "一系列", "有效", "高效"]
TRANSITIONS = ["在此基础上", "此外", "同时", "与此同时", "因此", "然而", "基于此"]
META_PATTERNS = [
    r"沿着.{0,10}这一主线", r"我们可以辨识", r"构成本项目的.{0,6}基线",
    r"一个根本性问题.{0,6}浮现", r"需要特别说明的是", r"需要澄清的是",
    r"需要指出的是", r"值得注意的是", r"这一判断构成", r"这一跃迁携带",
]
SELF_REF = [r"详\s*§\d", r"见\s*§\d", r"方法学手册\s*§\d",
            r"与\s*§\d\s*一致", r"详见\s*§\d", r"参见\s*§\d"]


def detect(files=None, verbose=False):
    files = files or FILES
    texts = []
    for key in files:
        txt = open(BASE + key).read()
        cut = txt.find("### 参考文献")
        if cut > 0:
            txt = txt[:cut]
        texts.append(txt)
    full_text = "\n\n".join(texts)
    total_chars = len(full_text)

    text_for_count = full_text
    for term in sorted(AI_TERM_WHITELIST, key=len, reverse=True):
        text_for_count = text_for_count.replace(term, "□" * len(term))

    sentences = re.split(r'[。！？\n]', full_text)

    ceiling = 1.0
    out = {}

    tc = sum(text_for_count.count(w) for w in TRANSITIONS)
    thr = max(8, int(total_chars / 1000 * 1.0))
    pen = max(0, (tc - thr) * 0.02)
    ceiling -= pen
    out["transition_words"] = (tc, thr, pen,
                               {w: text_for_count.count(w) for w in TRANSITIONS if text_for_count.count(w)})

    tpl = len(re.findall(r"为.{1,20}提供.{0,10}(基础|支撑|途径|条件|工具|指导)", full_text))
    pen = max(0, (tpl - 8) * 0.03)
    ceiling -= pen
    out["template_phrases"] = (tpl, 8, pen, {})

    subj = sum(1 for s in sentences if any(s.strip().startswith(x)
                for x in ["本项目拟", "本项目将", "本项目计划", "本项目旨在"]))
    pen = max(0, (subj - 5) * 0.02)
    ceiling -= pen
    out["template_subject"] = (subj, 5, pen, {})

    rc = sum(text_for_count.count(w) for w in REDUNDANT_WORDS)
    thr = max(12, int(total_chars / 1000 * 2.0))
    pen = max(0, (rc - thr) * 0.01)
    ceiling -= pen
    out["redundant_modifiers"] = (rc, thr, pen,
                                  {w: text_for_count.count(w) for w in REDUNDANT_WORDS if text_for_count.count(w)})

    severe = [s for s in sentences if len(s.strip()) > 120]
    free = 2 + int(total_chars / 1000 * 0.15)
    pen = max(0, (len(severe) - free) * 0.02)
    ceiling -= pen
    out["long_sentences"] = (len(severe), free, pen,
                             [s.strip()[:70] for s in severe])

    mc = sum(len(re.findall(p, full_text)) for p in META_PATTERNS)
    pen = max(0, (mc - 2) * 0.03)
    ceiling -= pen
    out["meta_discourse"] = (mc, 2, pen, {})

    bold = len(re.findall(r'\*\*[^*]+\*\*', full_text))
    per1k = bold / max(total_chars, 1) * 1000
    pen = min(0.15, int(max(0, per1k - 3)) * 0.03) if per1k > 3 else 0.0
    ceiling -= pen
    out["excessive_bold"] = (bold, 3, pen, {"per_1k": round(per1k, 2)})

    lb = len(re.findall(r'(?:^|\n)(?:\d+\.\s+.+(?:\n|$)){2,}', full_text))
    lb += len(re.findall(r'(?:^|\n)(?:[-*]\s+.+(?:\n|$)){2,}', full_text))
    pen = min(0.20, lb * 0.05)
    ceiling -= pen
    out["bullet_list"] = (lb, 0, pen, {})

    sr = sum(len(re.findall(p, full_text)) for p in SELF_REF)
    pen = 0.10 if sr > 15 else (0.05 if sr > 10 else 0.0)
    ceiling -= pen
    out["self_reference"] = (sr, 10, pen, {})

    raw = ceiling
    ceiling = max(ceiling, 0.5)
    print(f"全文字符数：{total_chars}")
    print(f"表达质量天花板：{ceiling:.2f}（raw={raw:.4f}）")
    for k, (c, thr, pen, extra) in out.items():
        flag = "⚠️" if pen > 0 else "✓"
        line = f"  {flag} {k}: count={c} threshold={thr} penalty={pen:.4f}"
        if extra and pen > 0:
            line += f" {extra}"
        print(line)
    if verbose:
        for s in out["long_sentences"][3]:
            print("   *", s)
    return ceiling


if __name__ == "__main__":
    args = sys.argv[1:]
    files = [a for a in args if a.endswith(".md")] or None
    detect(files, verbose=True)
