#!/usr/bin/env python3
"""
pdf_enricher.py — 对重点论文进行 PDF 全文增强
从 arXiv 下载 PDF → PyPDF2 提取正文 → 章节解析 → 追加/替换结构化内容

用法：
    python3 pdf_enricher.py <arxiv_id>        # 单篇
    python3 pdf_enricher.py --all              # 所有 top papers
    python3 pdf_enricher.py --rebuild          # 重建所有
"""

import sys, json, time, re
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from .pdf_extractor import extract_from_pdf  # 包模式
    HAS_PDF = True
except Exception as e:
    try:
        from pdf_extractor import extract_from_pdf  # 脚本模式
        HAS_PDF = True
    except Exception as e2:
        print(f"⚠️  PDF 提取模块不可用: {e2}")
        HAS_PDF = False

PROJECT_ROOT = _SCRIPT_DIR.parent.parent
RAW_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"
CKPT_PATH = PROJECT_ROOT / "knowledge" / "raw" / "checkpoint.json"
OUT_WIKI = PROJECT_ROOT / "knowledge" / "wiki" / "papers"

# Top 20 重点文献（按引用数排序）
TOP_PAPERS = [
    "2403.19535",  # Science 2012 keV HHG, 1537次
    "1012.3863",   # RABBITT attosecond, 461次
    "2404.01325",  # Phase matching X-ray, 367次
    "1006.3942",   # Water window phase matching, 312次
    "1502.07183",  # Bloch electrons solids, 270次
    "1707.05445",  # Angular streaking tunnelling, 261次
    "1806.11232",  # Topological sub-cycle, 184次
    "1812.11447",  # SFA Symphony, 183次
    "1910.13791",  # Quantum optics HHG, 137次
    "1102.1461",   # Attosecond streaking TDSE, 136次
    "1010.4558",   # Transient absorption helium, 132次
    "1411.1964",   # Isolated attosecond spatio-temporal, 130次
    "1010.2800",   # Delay atomic photoionization, 126次
    "1302.4495",   # Wigner delay noble gas, 109次
    "2103.16228",  # Self-probing HHG spectroscopy, 107次
    "1609.09852",  # Multi-level solid HHG, 102次
    "2111.08669",  # Solids HHG tutorial, 98次
    "1805.10453",  # Polarization HHG spectroscopy, 85次
    "1207.4653",   # Carbon K-edge water window, 84次
    "1809.08109",  # Reciprocal space trajectory, 80次
]


def slug_from_title(title: str) -> str:
    import re as re2
    s = re2.sub(r"[^\w\s\-]", "", title.lower())
    s = re2.sub(r"[\s_]+", "-", s)[:60]
    return s


def update_paper_file(aid: str, pdf_content: dict):
    """用 PDF 内容增强 raw paper 文件中的 content sections。"""
    # 找到对应的 raw paper 文件（处理 physics/XXXXXX 格式）
    safe_aid = aid.replace("/", "-")
    matching = list(RAW_DIR.glob(f"????-{safe_aid}-*.md"))
    if not matching:
        print(f"  ⚠️  未找到 raw paper 文件: {aid}")
        return

    f = matching[0]
    text = f.read_text(encoding="utf-8")

    # 替换 content sections（用字符串操作，避免 re.sub 的转义问题）
    def replace_section(text, sec_title, content):
        if isinstance(content, list):
            bullet_lines = "".join(f"- {item}\n" for item in content)
            new_section = f"## {sec_title}\n\n{bullet_lines}"
        else:
            new_section = f"## {sec_title}\n\n{content}\n"

        # 查找并替换现有 section
        marker = f"## {sec_title}\n"
        old_start = text.find(marker)
        if old_start >= 0:
            rest = text[old_start + len(marker):]
            next_heading = rest.find("\n## ")
            if next_heading >= 0:
                text = text[:old_start] + new_section + rest[next_heading + 1:]
            else:
                text = text[:old_start] + new_section
        else:
            text = text.rstrip() + "\n" + new_section
        return text

    if pdf_content.get("key_scientific_questions"):
        text = replace_section(text, "关键科学问题", pdf_content["key_scientific_questions"])
    if pdf_content.get("methods"):
        text = replace_section(text, "主要方法", pdf_content["methods"])
    if pdf_content.get("core_findings"):
        text = replace_section(text, "核心发现与创新点", pdf_content["core_findings"])
    if pdf_content.get("summary_outlook"):
        text = replace_section(text, "总结与展望", pdf_content["summary_outlook"])


    # 添加来源标注
    marker = f"\n<!-- PDF增强于 {time.strftime('%Y-%m-%d')}，chars={pdf_content['_pdf_chars']:,} -->\n"
    text = re.sub(r"(\n<!-- PDF增强于 .+ -->)", "", text)  # 去重
    text += marker

    f.write_text(text, encoding="utf-8")
    print(f"  ✅ 更新: {f.name} (PDF {pdf_content['_pdf_chars']:,} chars)")


def enrich_one(aid: str) -> bool:
    """增强单篇论文。"""
    if not HAS_PDF:
        print(f"  ⚠️  PDF 模块不可用，跳过")
        return False

    print(f"  → PDF 提取 {aid} ...", end=" ", flush=True)
    try:
        pdf_content = extract_from_pdf(aid)
        if pdf_content.get("_error") == "no_sections_found" and pdf_content.get("_pdf_chars", 0) == 0:
            print(f"失败")
            return False

        err = pdf_content.get("_error", "")
        chars = pdf_content.get("_pdf_chars", 0)
        q = len(pdf_content.get("key_scientific_questions", []))
        m = len(pdf_content.get("methods", []))
        f = len(pdf_content.get("core_findings", []))
        print(f"✅ ({chars:,} chars | Q:{q} M:{m} F:{f})" +
              (f" ⚠️ {err}" if err else ""))

        update_paper_file(aid, pdf_content)
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False


def rebuild_all(aids: list[str]):
    """重建所有论文。"""
    print(f"\n{'='*60}")
    print(f"  PDF 增强流水线")
    print(f"  论文: {len(aids)} 篇")
    print(f"{'='*60}\n")

    success = 0
    for i, aid in enumerate(aids, 1):
        print(f"[{i}/{len(aids)}]", end=" ")
        if enrich_one(aid):
            success += 1
        time.sleep(2)  # 礼貌性限流

    print(f"\n{'='*60}")
    print(f"  完成！成功 {success}/{len(aids)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if not HAS_PDF:
        print("错误: PyPDF2 不可用")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        rebuild_all(TOP_PAPERS)
    elif len(sys.argv) > 1 and sys.argv[1] == "--rebuild":
        # 读取所有 raw papers
        all_aids = []
        for f in sorted(RAW_DIR.glob("*.md")):
            import re as re2
            m = re2.search(r"/(\d{4})-(.+?)-", str(f))
            if m:
                all_aids.append(m.group(2))
        rebuild_all(all_aids)
    elif len(sys.argv) > 1:
        aid = sys.argv[1]
        enrich_one(aid)
    else:
        print(__doc__)
