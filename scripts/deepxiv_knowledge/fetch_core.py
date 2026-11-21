"""
fetch_core.py — deepxiv 论文获取核心逻辑
v5-final: --head (JSON) 为主，--preview 补充，LaTeX 清理正确
"""

import re, json, subprocess, time, sys
from pathlib import Path
from typing import Optional

DEEPXIV = str(Path.home() / ".venv" / "bin" / "deepxiv")

# Unicode superscript/subscript 表
SUPER_S = {"0":"⁰","1":"¹","2":"²","3":"³","4":"⁴","5":"⁵","6":"⁶","7":"⁷","8":"⁸","9":"⁹"}
SUPER_S_REPLACE = [(f"^{n}", SUPER_S[n]) for n in SUPER_S]


def _run(cmd: list, timeout: int = 60) -> tuple[str, str, int]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1


def fetch_head(arxiv_id: str, max_retries: int = 3) -> Optional[dict]:
    """获取论文结构化 JSON（--head），返回统一格式 dict。"""
    clean = arxiv_id.strip().replace("arXiv:", "").replace("arxiv:", "")
    for attempt in range(max_retries):
        out, err, code = _run([DEEPXIV, "paper", clean, "--head"], timeout=60)
        if code == 0 and out.strip().startswith("{"):
            try:
                data = json.loads(out)
                if data.get("arxiv_id"):
                    return _normalize_head(data)
            except json.JSONDecodeError:
                pass
        if "not found" in (out + err).lower():
            return None
        time.sleep((2 ** attempt) + 2)
    return None


def fetch_preview(arxiv_id: str, max_retries: int = 3) -> tuple[Optional[str], Optional[str]]:
    """获取扩展正文预览（~10KB，含 Abstract + 部分正文）。"""
    clean = arxiv_id.strip().replace("arXiv:", "").replace("arxiv:", "")
    for attempt in range(max_retries):
        out, err, code = _run([DEEPXIV, "paper", clean, "--preview"], timeout=120)
        if code == 0 and len(out) > 200:
            return out, None
        if "not found" in (out + err).lower():
            return None, "PAPER_NOT_FOUND"
        time.sleep((2 ** attempt) + 3)
    return None, f"FAILED after {max_retries} retries"


def fetch_json_search(query: str, limit: int = 10) -> Optional[list]:
    for attempt in range(3):
        out, err, code = _run(
            [DEEPXIV, "search", query, "--limit", str(limit), "--format", "json"], timeout=60
        )
        if code == 0:
            try:
                return json.loads(out).get("result", [])
            except json.JSONDecodeError:
                return None
        time.sleep(2 ** attempt)
    return None


# ============================================================
# 内部解析
# ============================================================

def _normalize_head(data: dict) -> dict:
    """将 --head JSON 映射为统一格式 dict。"""
    authors_raw = data.get("authors", [])
    if isinstance(authors_raw, list):
        authors = []
        for a in authors_raw:
            if isinstance(a, dict):
                name = a.get("name", "")
            elif isinstance(a, str):
                name = a
            else:
                name = str(a)
            if name:
                authors.append(name.strip())
    elif isinstance(authors_raw, str):
        authors = [a.strip() for a in authors_raw.split(",") if a.strip()]
    else:
        authors = []

    year = 0
    date_str = data.get("publish_at") or ""
    if date_str:
        try:
            year = int(date_str[:4])
        except ValueError:
            pass

    doi = data.get("doi") or ""
    if not doi:
        doi = (data.get("externalIds") or {}).get("DOI", "")

    abstract = _clean_latex(data.get("abstract", ""))
    tldr = _clean_latex(data.get("tldr", ""))
    cats = data.get("categories", [])
    if isinstance(cats, str):
        cats = [c.strip() for c in cats.split(",") if c.strip()]

    arxiv_id = data.get("arxiv_id", "")
    return {
        "arxiv_id": arxiv_id,
        "title": _clean_latex(data.get("title", "")),
        "authors": authors,
        "year": year,
        "journal": data.get("journal_name") or data.get("venue") or "",
        "doi": doi,
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}",
        "citation_count": data.get("citations") or 0,
        "tldr": tldr,
        "categories": cats,
        "abstract": abstract,
        # 保留原始 sections 供 _extract_sections_from_head 使用
        "sections": data.get("sections") or [],
        # content 字段由调用方填充（head section TLDR 或 preview 解析）
        "key_scientific_questions": [],
        "core_findings": [],
        "methods": [],
        "summary_outlook": tldr,
    }


def _extract_sections_from_head(head_data: dict) -> dict:
    """
    从 deepxiv --head JSON 的 sections 数组提取结构化内容。
    这是 deepxiv 官方解析的各节摘要，远比 preview 解析可靠。

    映射规则：
      Introduction / I.           → 关键科学问题
      Methods/Experimental/Setup  → 主要方法
      Results / Discussion         → 核心发现与创新点
      Conclusion / Outlook         → 总结与展望
    """
    sections = {
        "key_scientific_questions": [],
        "core_findings": [],
        "methods": [],
        "summary_outlook": "",
    }
    raw_sections = head_data.get("sections") or []
    if not raw_sections:
        return sections

    intro_parts, method_parts, finding_parts, conclusion_parts = [], [], [], []

    for sec in raw_sections:
        name = sec.get("name", "").strip().lower()
        tldr = sec.get("tldr", "").strip()
        # 去除 [research paper] 等前缀
        tldr = re.sub(r"^\[.*?\]\s*", "", tldr).strip()
        if not tldr:
            continue

        if any(k in name for k in ["introduction", "i.", " i "]):
            intro_parts.append(tldr)
        elif any(k in name for k in ["method", "methods", "methodology", "experimental",
                                      "setup", "experiment", " ii."]):
            if not any(n in name for n in ["results", "result#", " iii."]):
                method_parts.append(tldr)
        elif any(k in name for k in ["results", "discussion", "result#"]):
            finding_parts.append(tldr)
        elif any(k in name for k in ["conclusion", "outlook", "summary"]):
            conclusion_parts.append(tldr)
        elif any(k in name for k in [
            "acknowledgment", "reference", "supplementary", "appendix",
            "author", "affiliation", "footnote", "abstra"
        ]):
            # 非实质内容节 → 忽略
            pass
        else:
            finding_parts.append(tldr)

    sections["key_scientific_questions"] = intro_parts[:4]
    sections["methods"] = method_parts[:3]
    sections["core_findings"] = finding_parts[:6]
    sections["summary_outlook"] = " ".join(conclusion_parts[:2])
    return sections


def _extract_sections_from_preview(preview_text: str) -> dict:
    """从 preview 补充提取结构化 content（仅 abstract 之后的段落）。"""
    sections = {
        "key_scientific_questions": [],
        "core_findings": [],
        "methods": [],
        "summary_outlook": "",
    }
    if not preview_text or len(preview_text) < 200:
        return sections

    text = _clean(preview_text)

    # Introduction（关键科学问题）
    INTRO_PAT = re.compile(
        r"(?:I\.?\s*)?(?:INTRODUCTION)\s*\n*\s*(.{100,4000}?)"
        r"(?=\n\s*(?:II\.?|Methods|EXPERIMENTAL|Methodology|Results|III\.?))",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    m = INTRO_PAT.search(text)
    intro_text = m.group(1) if m else ""
    if intro_text:
        sections["key_scientific_questions"] = _bullets(intro_text)

    # Methods
    METHOD_PAT = re.compile(
        r"(?:Methods|Methodology|Experimental|Setup|Experiment|Apparatus)\s*\n*\s*(.{80,2000}?)"
        r"(?=\n\s*(?:Results|III\.?|Discussion|IV\.?|Conclusion))",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    m = METHOD_PAT.search(text)
    if m:
        sections["methods"] = _bullets(m.group(1))

    # 核心发现
    FIND_PAT = re.compile(
        r"[^.!?\n]{15,300}"
        r"(?:\d[\d.,]+\s*(?:times|percent|nm|eV|THz|Hz|mJ|GW|MHz|%|"
        r"as|fs|ns|keV|MeV|fold|faster|slower|bright|higher|lower|"
        r"increased|decreased|demonstrated|measured|observed|revealed|showed|demonstrates|achieves))"
        r"[^.!?\n]{0,150}",
        re.IGNORECASE
    )
    seen, cleaned = set(), []
    for f in FIND_PAT.findall(text):
        f = f.strip()
        if len(f) > 50 and f not in seen:
            seen.add(f)
            cleaned.append(f[:200])
    sections["core_findings"] = cleaned[:6]
    return sections


def _bullets(text: str) -> list:
    KW = [
        "we show", "we demonstrate", "we find", "we observe", "we measure",
        "we develop", "we introduce", "we propose", "we investigate",
        "we examine", "reveal", "demonstrate", "observe", "measure",
        "develop", "introduce", "discover", "study", "address",
        "challenge", "show that", "first", "new", "unique",
        "significant", "substantial", "demonstrates", "achieves",
    ]
    points, seen = [], set()
    for line in text.splitlines():
        s = line.strip()
        if len(s) < 40:
            continue
        lower = s.lower()
        if any(k in lower for k in KW):
            clean = re.sub(r"\s+", " ", s)[:200]
            if clean not in seen and len(clean) > 40:
                seen.add(clean)
                points.append(clean)
        if len(points) >= 6:
            break
    return points


def _clean_latex(text: str) -> str:
    """清理 LaTeX $math$ 标记，替换上标为 Unicode。"""
    if not text:
        return ""
    def _math(m):
        inner = m.group(1).strip()
        for old, new in SUPER_S_REPLACE:
            inner = inner.replace(old, new)
        return inner
    text = re.sub(r"\$([^$]+)\$", _math, text)
    text = re.sub(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{[^{}]*\})?", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clean(text: str) -> str:
    """轻量清理（移除 LaTeX 数学块，保留文字）。"""
    if not text:
        return ""
    text = re.sub(r"\\\[.*?\\\]", "", text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]+\$", "", text)
    text = re.sub(r"\\[^a-zA-Z\n]", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()
