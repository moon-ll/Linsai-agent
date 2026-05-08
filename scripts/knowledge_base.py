#!/usr/bin/env python3
"""本地知识库 — 基于关键词倒排索引的文档检索系统。

用途：
    为林赛提供可靠的本地知识来源。用户将文档放入 knowledge/ 目录，
    系统自动建立倒排索引，对话时根据用户输入自动检索相关段落注入上下文。

用法示例：
    >>> from knowledge_base import build_index, search
    >>> build_index()
    >>> results = search("固体HHG相位匹配", top_k=3)
    >>> for r in results:
    ...     print(r["text"][:100])

规范：
    - 仅使用 Python 3 标准库
    - 索引文件：knowledge/index.json
    - 支持增量索引（只更新变更的文档）
"""

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

PROJECT_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
INDEX_PATH = KNOWLEDGE_DIR / "index.json"

# 简单中文停用词
_STOPWORDS: Set[str] = {
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人",
    "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
    "你", "会", "着", "没有", "看", "好", "自己", "这", "那",
    "可以", "他", "她", "它", "们", "与", "及", "或", "但是", "因为",
    "所以", "如果", "则", "而", "于", "以", "为", "之", "其", "将",
    "被", "把", "让", "向", "从", "到", "对", "关于", "根据", "按照",
}

# 支持的知识文件扩展名
_SUPPORTED_EXTS = {".md", ".txt", ".rst"}


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tokenize(text: str) -> List[str]:
    """分词：提取中文词组（2字以上）和英文单词。"""
    tokens = []
    # 中文字符串（连续2字以上）
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}", text):
        word = m.group()
        # 进一步切分：2字、3字、4字窗口
        for size in (2, 3, 4):
            for i in range(len(word) - size + 1):
                tokens.append(word[i : i + size])
    # 英文单词
    for m in re.finditer(r"[a-zA-Z_][a-zA-Z0-9_]{1,}", text):
        tokens.append(m.group().lower())
    # 数字
    for m in re.finditer(r"\d+\.?\d*", text):
        tokens.append(m.group())
    return [t for t in tokens if t not in _STOPWORDS and len(t) >= 2]


def _chunk_document(text: str, max_chars: int = 500) -> List[Dict[str, str]]:
    """将文档按段落分块，每块不超过 max_chars 字符。"""
    chunks = []
    # 按空行分段落
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    current_text = ""
    current_idx = 0

    for para in paragraphs:
        if len(current_text) + len(para) + 2 <= max_chars:
            current_text += para + "\n\n"
        else:
            if current_text:
                chunks.append({
                    "id": f"chunk_{current_idx}",
                    "text": current_text.strip(),
                })
                current_idx += 1
            current_text = para + "\n\n"

    if current_text:
        chunks.append({
            "id": f"chunk_{current_idx}",
            "text": current_text.strip(),
        })

    return chunks


def _compute_idf(doc_count: int, term_doc_freq: Dict[str, int]) -> Dict[str, float]:
    """计算 IDF 值。"""
    idf = {}
    for term, freq in term_doc_freq.items():
        idf[term] = math.log(doc_count / (freq + 1)) + 1
    return idf


def build_index(force: bool = False) -> Dict[str, Any]:
    """扫描 knowledge/ 目录，构建或更新倒排索引。

    Args:
        force: 为 True 时强制全量重建索引

    Returns:
        索引数据字典
    """
    if not KNOWLEDGE_DIR.exists():
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    # 加载旧索引（用于增量更新）
    old_index: Dict[str, Any] = {}
    if not force and INDEX_PATH.exists():
        try:
            with open(INDEX_PATH, "r", encoding="utf-8") as f:
                old_index = json.load(f)
        except Exception:
            old_index = {}

    old_docs = old_index.get("documents", {})

    # 扫描知识文件
    docs: Dict[str, Dict[str, Any]] = {}
    all_chunks: List[Dict[str, Any]] = []
    term_doc_freq: Dict[str, int] = {}

    for file_path in sorted(KNOWLEDGE_DIR.iterdir()):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in _SUPPORTED_EXTS:
            continue
        if file_path.name == "index.json":
            continue

        mtime = file_path.stat().st_mtime
        old_doc = old_docs.get(file_path.name)

        # 增量：文件未修改则复用旧数据
        if not force and old_doc and old_doc.get("mtime") == mtime:
            docs[file_path.name] = old_doc
            for chunk in old_doc.get("chunks", []):
                all_chunks.append({
                    "id": chunk["id"],
                    "doc": file_path.name,
                    "text": chunk["text"],
                    "keywords": set(chunk.get("keywords", [])),
                })
            continue

        # 读取并重新索引
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            continue

        chunks = _chunk_document(text)
        doc_chunks = []
        for chunk in chunks:
            keywords = _tokenize(chunk["text"])
            chunk["keywords"] = keywords
            doc_chunks.append(chunk)
            all_chunks.append({
                "id": chunk["id"],
                "doc": file_path.name,
                "text": chunk["text"],
                "keywords": set(keywords),
            })

        docs[file_path.name] = {
            "title": file_path.stem,
            "path": str(file_path.relative_to(PROJECT_ROOT)),
            "size": file_path.stat().st_size,
            "mtime": mtime,
            "chunks": len(doc_chunks),
            "chunk_list": doc_chunks,
        }

    # 计算 term_doc_freq
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

    index_data = {
        "documents": docs,
        "inverted": inverted,
        "idf": idf,
        "doc_count": doc_count,
        "built_at": _now_utc(),
    }

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    return index_data


def search(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """根据查询检索相关知识段落。

    Args:
        query: 用户输入的查询文本
        top_k: 返回最相关的 K 个段落

    Returns:
        段落列表，每项含 text, doc, score
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

    inverted = index_data.get("inverted", {})
    idf = index_data.get("idf", {})
    docs = index_data.get("documents", {})

    # 收集候选 chunk
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
        chunk_id = info["chunk_id"]
        doc_info = docs.get(doc_name, {})
        chunk_text = ""
        chunk_keywords = []
        for c in doc_info.get("chunk_list", []):
            if c["id"] == chunk_id:
                chunk_text = c["text"]
                chunk_keywords = c.get("keywords", [])
                break

        if not chunk_text:
            continue

        # 统计词频
        term_freq = {}
        for kw in chunk_keywords:
            term_freq[kw] = term_freq.get(kw, 0) + 1

        score = 0
        total_terms = len(chunk_keywords) if chunk_keywords else 1
        for term in info["terms"]:
            tf = term_freq.get(term, 0) / total_terms
            idf_val = idf.get(term, 1)
            score += tf * idf_val

        scored.append({
            "text": chunk_text,
            "doc": doc_name,
            "score": score,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def get_index_status() -> Dict[str, Any]:
    """返回知识库索引状态。"""
    if not INDEX_PATH.exists():
        return {"indexed": False, "documents": 0, "chunks": 0}
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        docs = data.get("documents", {})
        total_chunks = sum(d.get("chunks", 0) for d in docs.values())
        return {
            "indexed": True,
            "documents": len(docs),
            "chunks": total_chunks,
            "built_at": data.get("built_at", ""),
        }
    except Exception:
        return {"indexed": False, "documents": 0, "chunks": 0}


if __name__ == "__main__":
    print("◐ 知识库自检")
    idx = build_index(force=True)
    print(f"  索引文档数: {len(idx['documents'])}")
    print(f"  索引词项数: {len(idx['inverted'])}")
    print(f"  索引时间: {idx['built_at']}")

    # 搜索测试
    results = search("固体 HHG", top_k=3)
    print(f"  搜索 '固体 HHG' 结果数: {len(results)}")
    for r in results:
        print(f"    [{r['doc']}] score={r['score']:.3f}: {r['text'][:60]}...")

    print("✓ 自检通过")
