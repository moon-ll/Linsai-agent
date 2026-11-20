"""
paper_writer.py — 论文写入模块
将结构化数据写入 knowledge/raw/papers/<year>-<arxiv_id>-<title-slug>.md
"""

import re
from pathlib import Path
from datetime import datetime, timezone

try:
    from .schema import FRONTMATTER_FIELDS, CONTENT_SECTIONS  # 包模式
except ImportError:
    from schema import FRONTMATTER_FIELDS, CONTENT_SECTIONS    # 脚本模式

def slug_from_title(title: str) -> str:
    """将标题转换为 URL-safe slug。"""
    s = re.sub(r"[^\w\s\-]", "", title.lower())
    s = re.sub(r"[\s_]+", "-", s)[:60]
    return s

def write_paper(data: dict, out_dir: Path) -> Path:
    """
    将论文数据写入 Markdown 文件。
    文件名格式: <year>-<arxiv_id>-<slug>.md
    """
    arxiv_id = data.get("arxiv_id", "unknown")
    year = data.get("year", "0000")
    title = data.get("title", "Untitled")

    slug = slug_from_title(title)
    # arxiv ID 中 "/" → "-"（处理 physics/9906053 等旧格式）
    safe_id = arxiv_id.replace("/", "-")
    filename = f"{year}-{safe_id}-{slug}.md"
    filepath = out_dir / filename

    lines = []
    # --- frontmatter ---
    lines.append("---")
    for field in FRONTMATTER_FIELDS:
        val = data.get(field, "")
        if isinstance(val, list):
            val = ", ".join(str(v) for v in val)
        lines.append(f"{field}: {val}")
    lines.append("---")
    lines.append("")
    # --- 标题 ---
    lines.append(f"# {title}")
    lines.append("")
    # --- 内容 sections ---
    sections = [
        ("摘要（原文 Abstract）", data.get("abstract", "")),
        ("关键科学问题", data.get("key_scientific_questions", [])),
        ("核心发现与创新点", data.get("core_findings", [])),
        ("主要方法", data.get("methods", [])),
        ("总结与展望", data.get("summary_outlook", "")),
    ]
    for sec_title, sec_content in sections:
        lines.append(f"## {sec_title}")
        lines.append("")
        if isinstance(sec_content, str) and sec_content:
            lines.append(sec_content)
        elif isinstance(sec_content, list) and sec_content:
            for item in sec_content:
                lines.append(f"- {item}")
        else:
            lines.append("*（未提取到内容）*")
        lines.append("")

    # --- 页脚 ---
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines.append(f"---\n*本文件由 LinSai-CoPilot deepxiv 知识库流水线生成于 {now}*\n*来源：deepxiv CLI（arXiv API）*")

    out_dir.mkdir(parents=True, exist_ok=True)
    filepath.write_text("\n".join(lines), encoding="utf-8")
    return filepath
