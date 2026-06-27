#!/usr/bin/env python3
"""kb_index.py — 知识库索引与检索。

负责统一倒排索引的构建（raw + wiki 增量）、TF-IDF 检索、轻量检索、
索引状态查询、增强上下文（图谱关联拉取）、raw 文件管理与纳入、动态文档添加。

依赖：kb_text（分词/分块/frontmatter/IDF）、kb_graph（图谱概览/关联概念）、
      paths（INDEX_PATH 等）、common（now_utc）。

门面 knowledge_base 在加载完成后会向本模块注入以下函数，以解决子模块→门面依赖：
    _ensure_dirs          — 目录初始化
    log_growth            — 生长日志记录
    distill_raw_to_wiki   — raw 蒸馏编排
    _load_aliases         — 别名加载
    get_wiki_page         — wiki 页面读取（用于增强上下文）
    _log                  — 日志对象
在门面未注入前这些名字为 None 占位，函数体保持与原 knowledge_base.py 完全一致。

用法示例：
    >>> from kb_index import build_index, search
    >>> idx = build_index(force=True)
    >>> results = search("固体HHG", top_k=3)

规范：
    - 仅使用 Python 3 标准库
    - 不修改任何函数逻辑，自 knowledge_base.py 物理迁移而来
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc as _now_utc
from paths import INDEX_PATH, KNOWLEDGE_DIR, RAW_DIR, WIKI_DIR
from kb_text import parse_frontmatter, _chunk_document, _tokenize, _compute_idf
from kb_graph import get_graph_summary, get_related_concepts


# ─────────────────────────────────────────────
# 门面注入依赖（占位，由 knowledge_base 加载后覆盖）
# ─────────────────────────────────────────────

_ensure_dirs = None  # type: ignore
log_growth = None  # type: ignore
distill_raw_to_wiki = None  # type: ignore
_load_aliases = None  # type: ignore
get_wiki_page = None  # type: ignore
_log = None


# ─────────────────────────────────────────────
# 常量
# ─────────────────────────────────────────────

_SUPPORTED_EXTS = {".md", ".txt", ".rst"}


# ─────────────────────────────────────────────
# raw 文件管理
# ─────────────────────────────────────────────

def _should_index(fpath: Path) -> bool:
    """判断文件是否应该被索引（排除 Obsidian 配置等隐藏目录）。"""
    if not fpath.is_file():
        return False
    if fpath.suffix.lower() not in _SUPPORTED_EXTS:
        return False
    # 排除 .obsidian/、.git/、__pycache__/ 等隐藏目录
    parts = fpath.parts
    for p in parts:
        if p.startswith(".") and p not in (".", ".."):
            return False
        if p.startswith("__"):
            return False
    return True


def list_raw_files() -> List[Dict[str, Any]]:
    """列出所有 raw 文件。"""
    files = []
    if not RAW_DIR.exists():
        return files
    for fpath in sorted(RAW_DIR.rglob("*")):
        if _should_index(fpath):
            rel = str(fpath.relative_to(KNOWLEDGE_DIR))
            files.append({
                "path": rel,
                "name": fpath.name,
                "category": fpath.parent.name,  # papers/notes/webclips
                "size": fpath.stat().st_size,
                "mtime": fpath.stat().st_mtime,
            })
    return files


def ingest_raw(rel_path: str, auto_distill: bool = False) -> Dict[str, Any]:
    """将 raw 文件纳入知识库系统。

    Args:
        rel_path: 相对 knowledge/ 的路径
        auto_distill: 是否自动触发 LLM 提炼生成 wiki

    Returns:
        {"success": bool, "path": str, "message": str, "wiki_path": str|null}
    """
    _ensure_dirs()
    raw_path = KNOWLEDGE_DIR / rel_path
    if not raw_path.exists():
        return {"success": False, "path": rel_path, "message": "文件不存在", "wiki_path": None}

    # 确保在 raw/ 目录内
    try:
        raw_path.relative_to(RAW_DIR)
    except ValueError:
        return {"success": False, "path": rel_path, "message": "文件必须在 knowledge/raw/ 目录内", "wiki_path": None}

    log_growth("ingest", rel_path, "manual", f"将 {raw_path.name} 纳入知识库")

    # 重建索引以纳入新 raw 文件
    build_index()

    result = {
        "success": True,
        "path": rel_path,
        "message": f"已纳入索引: {raw_path.name}",
        "wiki_path": None,
    }
    if _log:
        _log.info(f"raw 文件已纳入知识库: {rel_path}" + ("（含自动蒸馏）" if auto_distill else ""))

    if auto_distill:
        wiki_path = distill_raw_to_wiki(rel_path)
        result["wiki_path"] = wiki_path
        result["message"] += f" | 已提炼为 wiki: {wiki_path}"

    return result


# ─────────────────────────────────────────────
# 索引系统（增强版：同时索引 raw + wiki）
# ─────────────────────────────────────────────

def build_index(force: bool = False) -> Dict[str, Any]:
    """扫描 knowledge/raw/ 和 knowledge/wiki/ 目录，构建统一倒排索引。

    Args:
        force: 为 True 时强制全量重建

    Returns:
        索引数据字典
    """
    _ensure_dirs()

    # 加载旧索引
    old_index: Dict[str, Any] = {}
    if not force and INDEX_PATH.exists():
        try:
            with open(INDEX_PATH, "r", encoding="utf-8") as f:
                old_index = json.load(f)
        except Exception:
            old_index = {}

    old_docs = old_index.get("documents", {})

    # 收集所有待索引文件
    all_files: List[Path] = []
    for base_dir in [RAW_DIR, WIKI_DIR]:
        if base_dir.exists():
            for fpath in base_dir.rglob("*"):
                if _should_index(fpath):
                    all_files.append(fpath)

    docs: Dict[str, Dict[str, Any]] = {}
    all_chunks: List[Dict[str, Any]] = []
    term_doc_freq: Dict[str, int] = {}

    for file_path in sorted(all_files):
        rel_key = str(file_path.relative_to(KNOWLEDGE_DIR))
        mtime = file_path.stat().st_mtime
        old_doc = old_docs.get(rel_key)

        # 增量更新
        if not force and old_doc and old_doc.get("mtime") == mtime:
            docs[rel_key] = old_doc
            for chunk in old_doc.get("chunk_list", []):
                all_chunks.append({
                    "id": chunk["id"],
                    "doc": rel_key,
                    "text": chunk["text"],
                    "keywords": set(chunk.get("keywords", [])),
                    "source": old_doc.get("source", "raw"),
                })
            continue

        # 读取并索引
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            continue

        # 判断来源（raw 还是 wiki）
        source = "wiki" if "wiki/" in rel_key else "raw"

        # 解析 frontmatter 获取额外元数据（wiki 必解析；raw 也尝试解析 project/tags）
        title = file_path.stem
        tags: List[str] = []
        growth_stage = ""
        project: Any = ""
        if source == "wiki":
            try:
                fm, body = parse_frontmatter(text)
                title = fm.get("title", title)
                tags = fm.get("tags", [])
                growth_stage = fm.get("growth_stage", "")
                project = fm.get("project", "")
                # 索引时包含 frontmatter 中的标签
                text = body + " " + " ".join(tags)
                if growth_stage:
                    text += " " + growth_stage
            except Exception:
                pass

        # 推断 project（v2.7.0）：若 frontmatter 未声明，从路径 wiki/projects/<项目名>/ 推断
        if not project and source == "wiki":
            parts = Path(rel_key).parts
            if len(parts) >= 3 and parts[1] == "projects":
                project = parts[2]  # wiki/projects/<项目名>/...

        # raw 文件也尝试解析 project/tags frontmatter（导入的候选论文带 project 标签）
        if not project and source == "raw":
            try:
                fm_raw, _ = parse_frontmatter(text)
                project = fm_raw.get("project", "")
                if not tags:
                    tags = fm_raw.get("tags", [])
            except Exception:
                pass

        chunks = _chunk_document(text)
        doc_chunks = []
        for chunk in chunks:
            keywords = _tokenize(chunk["text"])
            chunk["keywords"] = keywords
            doc_chunks.append(chunk)
            all_chunks.append({
                "id": chunk["id"],
                "doc": rel_key,
                "text": chunk["text"],
                "keywords": set(keywords),
                "source": source,
            })

        docs[rel_key] = {
            "title": title,
            "path": rel_key,
            "source": source,
            "size": file_path.stat().st_size,
            "mtime": mtime,
            "chunks": len(doc_chunks),
            "chunk_list": doc_chunks,
            "project": project,
        }
        if tags:
            docs[rel_key]["tags"] = tags
        if growth_stage:
            docs[rel_key]["growth_stage"] = growth_stage

    # 计算 IDF
    for chunk in all_chunks:
        for term in chunk["keywords"]:
            term_doc_freq[term] = term_doc_freq.get(term, 0) + 1

    doc_count = len(all_chunks) if all_chunks else 1
    idf = _compute_idf(doc_count, term_doc_freq)

    # 构建倒排索引
    inverted: Dict[str, List[str]] = {}
    for chunk in all_chunks:
        for term in chunk["keywords"]:
            cid = f"{chunk['doc']}::{chunk['id']}"
            if term not in inverted:
                inverted[term] = []
            if cid not in inverted[term]:
                inverted[term].append(cid)

    # 图谱统计
    graph_summary = get_graph_summary()

    index_data = {
        "documents": docs,
        "inverted": inverted,
        "idf": idf,
        "doc_count": doc_count,
        "built_at": _now_utc(),
        "graph_summary": graph_summary,
    }

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    if _log:
        _log.info(f"索引构建完成: 文档={len(docs)}, 词项={len(inverted)}, 图谱节点={graph_summary.get('node_count', 0)}")
    return index_data


def search(query: str, top_k: int = 3, source: str = "all", project: str = "") -> List[Dict[str, Any]]:
    """根据查询检索相关知识段落（增强版）。

    Args:
        query: 用户输入的查询文本
        top_k: 返回最相关的 K 个段落
        source: "all" | "raw" | "wiki" — 只返回指定来源的结果
        project: 只返回属于指定项目子库的结果（v2.7.0，空字符串=不过滤）

    Returns:
        段落列表，每项含 text, doc, score, source, title, growth_stage, project
    """
    if not INDEX_PATH.exists():
        return []

    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            index_data = json.load(f)
    except Exception:
        return []

    query_terms = _tokenize(query)
    if not query_terms:
        return []

    # 别名扩展：将查询中的别名替换为 canonical 形式
    aliases = _load_aliases()
    expanded_terms = set(query_terms)
    for term in list(query_terms):
        for canonical, alts in aliases.items():
            if term.lower() == canonical.lower() or any(term.lower() == a.lower() for a in alts):
                expanded_terms.add(canonical.lower())
                for alt in alts:
                    expanded_terms.add(alt.lower())
    query_terms = list(expanded_terms)

    inverted = index_data.get("inverted", {})
    idf = index_data.get("idf", {})
    docs = index_data.get("documents", {})

    # 收集候选
    candidates: Dict[str, Dict[str, Any]] = {}
    for term in query_terms:
        for cid in inverted.get(term, []):
            if cid not in candidates:
                doc_name, chunk_id = cid.split("::", 1)
                candidates[cid] = {"doc": doc_name, "chunk_id": chunk_id, "terms": set()}
            candidates[cid]["terms"].add(term)

    # 计算 TF-IDF 得分
    scored = []
    for cid, info in candidates.items():
        doc_name = info["doc"]
        doc_info = docs.get(doc_name, {})

        # 来源过滤
        doc_source = doc_info.get("source", "raw")
        if source != "all" and doc_source != source:
            continue

        # 项目子库过滤（v2.7.0）
        doc_project = doc_info.get("project", "")
        if project:
            # project 可能是字符串或列表
            if isinstance(doc_project, list):
                if project not in doc_project:
                    continue
            elif doc_project != project:
                continue

        chunk_id = info["chunk_id"]
        chunk_text = ""
        chunk_keywords = []
        for c in doc_info.get("chunk_list", []):
            if c["id"] == chunk_id:
                chunk_text = c["text"]
                chunk_keywords = c.get("keywords", [])
                break

        if not chunk_text:
            continue

        term_freq = {}
        for kw in chunk_keywords:
            term_freq[kw] = term_freq.get(kw, 0) + 1

        score = 0
        total_terms = len(chunk_keywords) if chunk_keywords else 1
        for term in info["terms"]:
            tf = term_freq.get(term, 0) / total_terms
            idf_val = idf.get(term, 1)
            score += tf * idf_val

        # wiki 结果加权（结构化知识优先）
        if doc_source == "wiki":
            score *= 1.2
            # mature 阶段再加权
            if doc_info.get("growth_stage") == "mature":
                score *= 1.1

        scored.append({
            "text": chunk_text,
            "doc": doc_name,
            "score": score,
            "source": doc_source,
            "title": doc_info.get("title", doc_name),
            "growth_stage": doc_info.get("growth_stage", ""),
            "project": doc_info.get("project", ""),
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def search_light(query: str, top_k: int = 3, source: str = "all") -> List[Dict[str, Any]]:
    """轻量检索：只返回标题、摘要、路径和分数，不返回全文。

    用于快速判断是否需要注入上下文，节省内存和序列化开销。
    """
    results = search(query, top_k=top_k, source=source)
    light = []
    for r in results:
        text = r.get("text", "")
        # 生成一句话摘要（取第一句或前 80 字符）
        summary = text.split("。")[0] if "。" in text else text[:80]
        if len(summary) > 80:
            summary = summary[:77] + "..."
        light.append({
            "title": r.get("title", ""),
            "doc": r.get("doc", ""),
            "score": r.get("score", 0),
            "source": r.get("source", ""),
            "growth_stage": r.get("growth_stage", ""),
            "summary": summary,
        })
    return light


def get_index_status() -> Dict[str, Any]:
    """返回知识库状态（增强版）。"""
    if not INDEX_PATH.exists():
        return {
            "indexed": False,
            "raw_count": 0,
            "wiki_count": 0,
            "chunks": 0,
        }
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        docs = data.get("documents", {})
        raw_count = sum(1 for d in docs.values() if d.get("source") == "raw")
        wiki_count = sum(1 for d in docs.values() if d.get("source") == "wiki")
        total_chunks = sum(d.get("chunks", 0) for d in docs.values())
        graph = data.get("graph_summary", {})
        return {
            "indexed": True,
            "raw_count": raw_count,
            "wiki_count": wiki_count,
            "chunks": total_chunks,
            "built_at": data.get("built_at", ""),
            "graph": graph,
        }
    except Exception:
        return {"indexed": False, "raw_count": 0, "wiki_count": 0, "chunks": 0}


# ─────────────────────────────────────────────
# 上下文构建增强：关联知识拉取
# ─────────────────────────────────────────────

def get_enriched_context(query: str, top_k: int = 3) -> Dict[str, Any]:
    """获取增强的上下文：搜索结果 + 关联知识。

    Returns:
        {
            "results": [...],       # 直接搜索结果
            "related": [...],       # 通过图谱关联的知识
            "missing_concepts": [...],  # 查询中可能缺失的新概念
        }
    """
    results = search(query, top_k=top_k, source="all")

    # 通过图谱拉取关联知识
    related = []
    seen = {r["doc"] for r in results}
    for r in results:
        title = r.get("title", "")
        if title:
            for rel in get_related_concepts(title, depth=1):
                if rel["path"] not in seen:
                    seen.add(rel["path"])
                    page = get_wiki_page(rel["path"])
                    if page:
                        related.append({
                            "title": rel["title"],
                            "relation": rel["relation"],
                            "text": page["body"][:300],
                            "path": rel["path"],
                        })

    # 检测缺失概念（查询中的词未在知识库中命中）
    query_terms = _tokenize(query)
    indexed_terms = set()
    if INDEX_PATH.exists():
        try:
            with open(INDEX_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            indexed_terms = set(data.get("inverted", {}).keys())
        except Exception:
            pass

    missing = [t for t in query_terms if t not in indexed_terms and len(t) >= 3]

    return {
        "results": results,
        "related": related[:top_k],
        "missing_concepts": missing[:5],
    }


# ─────────────────────────────────────────────
# 向后兼容 API
# ─────────────────────────────────────────────

def add_document(path: str, content: str) -> Dict[str, Any]:
    """向后兼容：动态添加文档到知识库。

    新文档默认放入 knowledge/raw/notes/ 目录。
    """
    _ensure_dirs()
    target = KNOWLEDGE_DIR / "raw" / "notes" / Path(path).name
    target.write_text(content, encoding="utf-8")
    log_growth("ingest", str(target.relative_to(KNOWLEDGE_DIR)), "manual",
               f"通过 add_document 添加: {path}")
    build_index()
    if _log:
        _log.info(f"文档已添加到知识库: {path} → raw/notes/")
    return {"success": True, "path": str(target.relative_to(KNOWLEDGE_DIR))}
