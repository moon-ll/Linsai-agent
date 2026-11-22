"""
schema.py — 论文标准结构定义
所有从 deepxiv 获取的论文均遵循此 Schema。
"""

PAPER_SCHEMA = {
    "arxiv_id": str,          # arXiv ID（如 "1012.3863"）
    "status": str,            # verified | failed | partial
    "fetched_via": "deepxiv",
    "fetched_at": str,        # ISO 时间戳
    # --- 基本信息 ---
    "title": str,
    "authors": list,          # ["Author 1", "Author 2", ...]
    "year": int,
    "journal": str,
    "doi": str,
    "arxiv_url": str,
    "pdf_url": str,
    "categories": list,       # ["physics.atom-ph", ...]
    "tags": list,             # 用户指定的领域标签
    # --- 内容 ---
    "abstract": str,          # 原文 abstract（--preview 获取）
    "key_scientific_questions": list,
    "core_findings": list,
    "methods": list,
    "summary_outlook": str,
    # --- 元数据 ---
    "citation_count": int,
    "tldr": str,
    "error_message": str,      # 失败时记录原因
}

FRONTMATTER_FIELDS = [
    "arxiv_id", "status", "fetched_via", "fetched_at",
    "title", "authors", "year", "journal", "doi",
    "arxiv_url", "pdf_url", "categories", "tags",
    "citation_count", "tldr",
]

CONTENT_SECTIONS = [
    "摘要（原文 Abstract）",
    "关键科学问题",
    "核心发现与创新点",
    "主要方法",
    "总结与展望",
]
