"""
pdf_extractor.py — 从 arXiv PDF 提取全文结构化内容
依赖 PyPDF2（标准 macOS 可用）

策略：
  1. 从 arXiv 下载 PDF（urllib）
  2. PyPDF2 提取全文
  3. 正则匹配章节（I. INTRODUCTION / II. METHODS 等）
  4. 提取各节要点（基于关键词的句子选择）
"""

import re
import io
import urllib.request
import ssl
from pathlib import Path
from typing import Optional

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    try:
        # v6.9.75: pypdf 是 PyPDF2 的后继维护版（API 兼容），venv 中装有
        from pypdf import PdfReader
        HAS_PYPDF2 = True
    except ImportError:
        HAS_PYPDF2 = False


# ============================================================
# PDF 下载与文字提取
# ============================================================

def fetch_pdf_text(arxiv_id: str, timeout: int = 60) -> tuple[Optional[str], Optional[str]]:
    """
    下载 arXiv PDF 并提取全文文字。
    返回 (full_text, error_msg)。
    """
    if not HAS_PYPDF2:
        return None, "PyPDF2 not available"

    clean_id = arxiv_id.strip().replace("arXiv:", "").replace("arxiv:", "")
    url = f"https://arxiv.org/pdf/{clean_id}.pdf"
    ctx = ssl.create_default_context()

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible)"})
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            data = r.read()
    except Exception as e:
        return None, f"download_failed: {e}"

    try:
        reader = PdfReader(io.BytesIO(data))
        text_parts = []
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                text_parts.append(txt)
        full_text = "\n".join(text_parts)
        # 清理 PDF 提取噪声
        full_text = _clean_pdf_text(full_text)
        return full_text, None
    except Exception as e:
        return None, f"pdf_parse_failed: {e}"


def _clean_pdf_text(text: str) -> str:
    """
    清理 PDF 提取的常见噪声，并智能合并断行。
    """
    if not text:
        return text

    lines = text.splitlines()
    if not lines:
        return text

    # 逐行过滤
    skip = set()
    for i, line in enumerate(lines):
        s = line.strip()
        if len(s) < 3: skip.add(i); continue
        if re.match(r"^\d+\s*\d*$", s): skip.add(i); continue
        if re.search(r"(http|www|arxiv\.|doi\.)", s, re.I): skip.add(i); continue
        if re.match(r"^[\w.+-]+@[\w.-]+$", s): skip.add(i); continue
        if re.match(r"^\d[A-Za-z]?\s+[A-Z]", s): skip.add(i); continue
        if re.match(r"^[\d]+\s+[A-Z][a-z]+,\s+[A-Z]", s): skip.add(i); continue

    cleaned = [lines[i] for i in range(len(lines)) if i not in skip]
    if not cleaned:
        return text

    # 碎片化检测
    non_empty = [l for l in cleaned if l.strip()]
    avg = sum(len(l.strip()) for l in non_empty) / max(len(non_empty), 1)

    if avg < 30:
        merged = " ".join(c.strip() for c in cleaned if c.strip())
    else:
        parts = [cleaned[0].strip()] if cleaned else []
        for s in cleaned[1:]:
            s = s.strip()
            if not s: continue
            last = parts[-1][-30:] if len(parts[-1]) >= 30 else parts[-1]
            if re.search(r"[a-zA-Z\)][.!?]\s*$", last):
                parts.append(" " + s)
            else:
                parts[-1] += " " + s
        merged = " ".join(parts)

    # === 移除作者/机构块 ===
    # PRL/arXiv 格式：...(Dated: YYYY-MM-DD) Abstract starts here
    # 策略：直接取 (Dated:...) 之后的内容（去除作者/机构）
    dated_m = re.search(
        r"\(\s*Dated\s*:\s*[^)]+\)\s*",
        merged, re.IGNORECASE
    )
    if dated_m:
        # 直接取 dated 之后的内容
        merged = merged[dated_m.end():].strip()

    # 清理
    merged = re.sub(r"-\n([a-z])", r"\1", merged, flags=re.IGNORECASE)
    merged = re.sub(r"\xad", "", merged)
    merged = re.sub(r"\n+", " ", merged)
    merged = re.sub(r"[ \t]{2,}", " ", merged)

    return merged.strip()



def extract_sections(full_text: str) -> dict[str, str]:
    """
    从 PDF 全文中解析章节，返回 {section_name: content}。
    支持：
      - 罗马数字 + 标题：I. INTRODUCTION, II. METHODS
      - 阿拉伯数字：1. Introduction, 2. Methods
      - 全大写节名：INTRODUCTION, METHODS, RESULTS
      - 无编号节名：Methods and Experimental Details
    """
    if not full_text:
        return {}

    sections = {}
    headings = []

    # 模式1：罗马数字/阿拉伯数字 + 标题
    for pat in [
        re.compile(r"^\s*([IVX]+\.)\s+([A-Z][A-Z\s&\-/']+?(?:\s+[A-Z][A-Z\s&\-/']+?){0,3})\s*$", re.MULTILINE),
        re.compile(r"^\s*(\d+\.)\s+([A-Z][A-Z\s&\-/']+?(?:\s+[A-Z][A-Z\s&\-/']+?){0,3})\s*$", re.MULTILINE),
    ]:
        for m in pat.finditer(full_text):
            headings.append((m.start(), m.group(2).strip().lower(), m.group(0).strip()))

    # 模式2：全大写多词行（排除页眉/URL/数字行）
    for m in re.finditer(r"^([A-Z][A-Z\s]{2,}[A-Z])\s*$", full_text, re.MULTILINE):
        name = m.group(1).strip()
        skip = any(kw in name for kw in ["HTTP", "DOI", "ISSN", "FIG.", "REFERENCE"])
        if not skip and len(name) > 5:
            headings.append((m.start(), name.lower(), name))

    if not headings:
        return {}

    headings.sort(key=lambda x: x[0])

    # 匹配节名到目标类别
    for i, (pos, name_lower, raw_name) in enumerate(headings):
        matched_target = None
        for target, keywords in TARGET_SECTIONS.items():
            if any(kw in name_lower for kw in keywords):
                matched_target = target
                break
        if matched_target is None:
            # 第二轮：宽泛匹配理论方法节
            method_kw = ["theory", "model", "approach", "tdse", "bloch", "hamiltonian",
                        "calculation", "numerical", "scheme", "basis", "formalism",
                        "equation", "equation of"]
            if any(kw in name_lower for kw in method_kw):
                matched_target = "methods"
        if matched_target is None:
            continue

        next_pos = headings[i + 1][0] if i + 1 < len(headings) else len(full_text)
        content = full_text[pos:next_pos][len(raw_name):].strip()
        if matched_target in sections:
            sections[matched_target] += "\n" + content
        else:
            sections[matched_target] = content

    return sections


# ============================================================
# 内容精简：从节文本中提取关键句子
# ============================================================

FINDING_KW = [
    "we show", "we demonstrate", "we find", "we observe", "we measure",
    "we report", "we prove", "we introduce", "we propose", "reveal",
    "demonstrate", "observe", "measure", "discover", "show that",
    "achieve", "reach", "reach a", "obtain", "achieves", "achieving",
    "observe that", "observe a", "demonstrate that", "demonstrate a",
    "report a", "report the", "first", "new", "novel", "unique",
    "significant", "substantial", "record", "highest", "lowest",
]

QUESTION_KW = [
    "why", "how", "what", "whether", "challenge", "problem",
    "unresolved", "unknown", "fundamental", "key question",
    "remain", "mechanism", "understanding", "origin",
]


def extract_bullets(section_text: str, kw_list: list, max_items: int = 5) -> list[str]:
    """从文本中提取包含关键词的完整句子作为要点。"""
    if not section_text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", section_text)
    bullets = []
    seen = set()

    for sent in sentences:
        s = sent.strip()
        if len(s) < 40 or len(s) > 500:
            continue
        lower = s.lower()
        # 过滤引用行
        if re.match(r"^\s*\[\d+\]\s", s):
            continue
        # 过滤 URL
        if re.search(r"(http|www|arxiv\.|doi\.)", s):
            continue
        # 过滤 affiliation 行（多逗号城市格式）
        if s.count(",") >= 2 and re.search(r"[A-Z][a-z]+,\s*[A-Z][a-z]+", s) and len(s) < 100:
            continue
        # 过滤含 @ 的行
        if "@" in s:
            continue

        if any(kw in lower for kw in kw_list):
            clean = re.sub(r"\$[^$]{0,80}\$", "", s)
            clean = re.sub(r"\[a-zA-Z]+\{[^}]*}", "", clean)
            clean = re.sub(r"­", "", clean)
            clean = re.sub(r"[ 	]+", " ", clean).strip()
            if clean and len(clean) > 40 and clean not in seen:
                seen.add(clean)
                bullets.append(clean)
                if len(bullets) >= max_items:
                    break

    return bullets


def extract_from_pdf(arxiv_id: str) -> dict:
    """
    完整提取流程：下载 PDF → 解析章节 → 提取要点。
    无章节时用全文关键词提取；有章节时从所有节中提取 findings。
    """
    result = {
        "key_scientific_questions": [],
        "methods": [],
        "core_findings": [],
        "summary_outlook": "",
        "_pdf_chars": 0,
        "_pdf_pages": 0,
        "_error": None,
    }

    full_text, err = fetch_pdf_text(arxiv_id)
    if err:
        result["_error"] = err
        return result

    result["_pdf_chars"] = len(full_text)
    sections = extract_sections(full_text)

    if sections:
        # 有章节结构（arXiv 预印本格式）
        intro = sections.get("introduction", "")
        result["key_scientific_questions"] = extract_bullets(intro, QUESTION_KW, max_items=4)

        methods_text = sections.get("methods", "")
        method_items = _extract_method_items(methods_text)
        result["methods"] = method_items[:4]

        # 从所有节（除 introduction）提取发现
        all_section_text = "\n".join(c for n, c in sections.items() if n != "introduction")
        result["core_findings"] = extract_bullets(all_section_text, FINDING_KW, max_items=6)

        conclusion = sections.get("conclusion", "")
        if conclusion:
            sentences = re.split(r"(?<=[.!?])\s+", conclusion.strip())
            result["summary_outlook"] = " ".join(sentences[:3]).strip()[:500]
    else:
        # 无章节结构（PRL/Science 期刊格式）：
        # 从全文关键词提取，优先从 abstract 和开头部分
        result["_error"] = "no_sections_found"
        # 用 "we" 开头的句子作为发现（研究论文的特征句）
        result["core_findings"] = extract_bullets(full_text, FINDING_KW, max_items=6)
        # 用 why/how/what 句作为科学问题
        result["key_scientific_questions"] = extract_bullets(full_text, QUESTION_KW, max_items=3)
        # 总结用前几句
        sentences = re.split(r"(?<=[.!?])\s+", full_text.strip())
        summary = next((s.strip() for s in sentences if len(s.strip()) > 80 and "fig" not in s.lower()), "")
        result["summary_outlook"] = summary[:500] if summary else ""

    return result


def _extract_method_items(text: str) -> list[str]:
    """从方法文本中提取具体方法/技术描述。"""
    if not text:
        return []

    METHOD_PHRASES = [
        # 测量技术
        "high harmonic generation", "streaking", "RABBITT", "FROG",
        "COLTRIMS", "VMI", "transient absorption", "attosecond streaking",
        "angular streaking", "electron spectroscopy", "photoelectron",
        "frequency-resolved", "frequency comb", "interferometer",
        "pump-probe",
        # 理论/数值方法
        "TDSE", "density functional", "DFT", "quantum dynamics",
        "SFA", "strong-field approximation", "Lewenstein model",
        "Bloch oscillation", "time-dependent", "numerical simulation",
        "Monte Carlo", "finite-difference", "ab initio",
        # 激光/光学系统
        "mid-infrared", "Ti:sapphire", "femtosecond", "ultrafast laser",
        "harmonic emission", "phase matching",
        "ellipticity", "polarization", "wavelength scan",
        "intensity", "pulse duration", "laser pulse",
        # 实验系统
        "gas cell", "hollow waveguide", "waveguide", "argon-filled",
        "neon", "helium", "krypton", "xenon",
        "solid-state", "semiconductor", "crystal", "graphene",
    ]

    # 分句
    sentences = re.split(r"(?<=[.!?])\s+", text)
    items = []
    seen = set()

    for sent in sentences:
        s = sent.strip()
        if len(s) < 30 or len(s) > 500:
            continue
        s_lower = s.lower()
        for phrase in METHOD_PHRASES:
            if phrase.lower() in s_lower:
                # 清理
                clean = re.sub(r"\$[^$]{0,80}\$", "", s)
                clean = re.sub(r"\xad", "", clean)
                clean = re.sub(r"\s+", " ", clean).strip()
                if clean and clean not in seen and len(clean) > 30:
                    seen.add(clean)
                    items.append(clean)
                    break  # 每句只用一个方法
    return items


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python3 pdf_extractor.py <arxiv_id>")
        sys.exit(1)

    aid = sys.argv[1]
    print(f"提取 {aid} ...")
    r = extract_from_pdf(aid)
    print(f"PDF: {r['_pdf_chars']:,} chars, 页数: {r['_pdf_pages']}")
    if r["_error"]:
        print(f"错误: {r['_error']}")
    print(f"\n关键科学问题 ({len(r['key_scientific_questions'])} 条):")
    for q in r["key_scientific_questions"]:
        print(f"  • {q[:120]}")
    print(f"\n主要方法 ({len(r['methods'])} 条):")
    for m in r["methods"]:
        print(f"  • {m[:120]}")
    print(f"\n核心发现 ({len(r['core_findings'])} 条):")
    for f in r["core_findings"]:
        print(f"  • {f[:120]}")
    print(f"\n总结: {r['summary_outlook'][:120]}")
