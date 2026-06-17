"""
paper_reader.py — 读取所有 raw papers，构建知识库索引
"""

import json, re
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"


def parse_frontmatter(text: str) -> Dict:
    """从 Markdown 中解析 YAML frontmatter。"""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    fm_text = text[4:end]
    result = {}
    for line in fm_text.splitlines():
        if ": " in line:
            key, val = line.split(": ", 1)
            val = val.strip().strip('"').strip("'")
            # 处理 YAML 列表格式: [a, b, c] 或逗号分隔字符串: a, b, c
            stripped = val.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                result[key] = [v.strip() for v in stripped.strip("[]").split(",")]
            elif ", " in stripped or "," in stripped:
                # 逗号分隔字符串 → 拆分为列表
                result[key] = [v.strip() for v in stripped.replace(", ", ",").split(",") if v.strip()]
            else:
                result[key] = val
    return result


def load_all_papers() -> List[Dict]:
    """加载所有 raw papers，返回结构化列表。"""
    papers = []
    for fp in sorted(RAW_DIR.glob("*.md")):
        try:
            text = fp.read_text(encoding="utf-8")
            meta = parse_frontmatter(text)
            body = text[text.find("\n---\n", 4) + 5:]
            sections = {}
            parts = re.split(r"\n## ", body)
            for part in parts[1:]:
                lines = part.split("\n", 1)
                sec_name = lines[0].strip()
                sec_content = lines[1].strip() if len(lines) > 1 else ""
                sections[sec_name] = sec_content
            papers.append({
                "arxiv_id": meta.get("arxiv_id", fp.stem),
                "year": int(meta.get("year", 0) or 0),
                "title": meta.get("title", ""),
                "authors": meta.get("authors", ""),
                "journal": meta.get("journal", ""),
                "doi": meta.get("doi", ""),
                "tags": meta.get("tags", []),
                "citation_count": int(meta.get("citation_count", 0) or 0),
                "status": meta.get("status", "unknown"),
                "abstract": sections.get("摘要（原文 Abstract）", ""),
                "key_questions": sections.get("关键科学问题", ""),
                "core_findings": sections.get("核心发现与创新点", ""),
                "methods": sections.get("主要方法", ""),
                "summary": sections.get("总结与展望", ""),
            })
        except Exception as e:
            print(f"  解析失败 {fp.name}: {e}")
    return sorted(papers, key=lambda p: (p.get("year", 0), -p.get("citation_count", 0)), reverse=True)


def build_by_tag(papers: List[Dict]) -> Dict[str, List[Dict]]:
    """按 tag 分组的论文索引。"""
    tag_map = {}
    for p in papers:
        for tag in p.get("tags", []):
            tag_map.setdefault(tag, []).append(p)
    return tag_map


def build_by_year(papers: List[Dict]) -> Dict[int, List[Dict]]:
    """按年份分组的论文索引。"""
    year_map = {}
    for p in papers:
        yr = p.get("year", 0)
        if yr:
            year_map.setdefault(yr, []).append(p)
    return year_map
