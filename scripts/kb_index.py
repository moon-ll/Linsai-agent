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
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc as _now_utc
import common as _cms
from paths import INDEX_PATH, KNOWLEDGE_DIR, RAW_DIR, WIKI_DIR, QA_DIR, HERMES_WIKI_DIR, HERMES_BRIEFING_PAPERS_DIR
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

# v6.8.51: 索引格式版本。v2 = 扁平 chunk 数组 + 整型倒排 postings。
# 加载时 format 不匹配（旧版 v1 / 无标记）视为过期索引，检索走空结果，
# 由日频 lc-kb-sync 或下一次 build_index() 重建。
INDEX_FORMAT = 2

# 两段式检索第二阶段精确打分的候选上限（第一阶段 IDF 覆盖率预排序后取 top N）
_PHASE2_CANDIDATES = 60

# 进程内索引缓存：按 (路径, mtime_ns, size) 签名校验，文件未变不重复加载。
# Web 服务器长驻进程下避免每次检索 157MB（v2 后 ~10MB）级 JSON 全量重读。
_INDEX_CACHE: Dict[str, Any] = {"data": None, "sig": None}


def _invalidate_index_cache() -> None:
    """索引文件被重写后清空进程内缓存（build_index / add_document 后调用）。"""
    _INDEX_CACHE["data"] = None
    _INDEX_CACHE["sig"] = None


def _load_index_cached() -> Dict[str, Any]:
    """带签名校验的索引加载。返回 {} 表示索引缺失/损坏/格式过期。"""
    global INDEX_PATH
    if not INDEX_PATH.exists():
        return {}
    try:
        st = INDEX_PATH.stat()
        sig = (str(INDEX_PATH), st.st_mtime_ns, st.st_size)
        if _INDEX_CACHE["sig"] == sig and _INDEX_CACHE["data"] is not None:
            return _INDEX_CACHE["data"]
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    if data.get("format") != INDEX_FORMAT:
        # 旧格式（v1 无 format 字段）→ 视为缺失，等待重建
        return {}
    _INDEX_CACHE["data"] = data
    _INDEX_CACHE["sig"] = sig
    return data


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

def build_index(force: bool = False, extra_wiki_dirs: Optional[List[tuple]] = None) -> Dict[str, Any]:
    """扫描 knowledge/raw/ 和 knowledge/wiki/ 目录，构建统一倒排索引。

    v5.0: 支持索引外部 wiki 目录（如 hermes AI_wiki/02-wiki/），
          使 CoPilot 检索引擎能命中 hermes 侧的结构化知识。

    v6.8.51 索引格式 v2（瘦身，原 157MB → 目标 <15MB）：
      - documents 不再内嵌 chunk_list（原 chunk 正文+全量关键词占 24MB）
      - chunk 扁平化为全局数组 [{"d": 文档, "i": chunk_id, "t": 正文}]
      - 倒排 postings 由 "doc::chunk_id" 长字符串改为整型下标（约 10 倍压缩）
      - 仅出现一次的中文 2-gram 不入倒排（46% 词条为纯噪声；英文保留，支撑论文名精确检索）
      - 放弃 mtime 增量（原增量依赖存储全量关键词）：全量分词重建，
        580 文档 / 12.8K chunk 约 5-10s，日频 cron 完全可接受
      - 检索改为两段式：先 IDF 覆盖率预排序，再对 top 候选重分词做精确 TF-IDF

    Args:
        force: 兼容参数（v2 起构建始终全量，忽略该值）
        extra_wiki_dirs: 外部 wiki 目录列表，每项为 (Path, source_label) 元组。
            默认 None 时自动包含 hermes wiki（标签 "hermes-wiki"）。
            传空列表 [] 则不索引任何外部目录（用于测试隔离）。

    Returns:
        索引数据字典
    """
    _ensure_dirs()

    # v5.0: 默认包含 hermes wiki + v6.8.1: 包含 hermes 简报论文
    if extra_wiki_dirs is None:
        extra_wiki_dirs = []
        if HERMES_WIKI_DIR.exists():
            extra_wiki_dirs.append((HERMES_WIKI_DIR, "hermes-wiki"))
        if HERMES_BRIEFING_PAPERS_DIR.exists():
            extra_wiki_dirs.append((HERMES_BRIEFING_PAPERS_DIR, "hermes-briefings"))

    # 收集所有待索引文件（v6.7.11: 加入 qa 模块）
    all_files: List[Path] = []
    for base_dir in [RAW_DIR, WIKI_DIR, QA_DIR]:
        if base_dir.exists():
            for fpath in base_dir.rglob("*"):
                if _should_index(fpath):
                    all_files.append(fpath)

    # v5.0: 收集外部 wiki 文件
    external_map: Dict[Path, str] = {}  # fpath → source_label
    for wiki_dir, source_label in extra_wiki_dirs:
        if wiki_dir.exists():
            for fpath in wiki_dir.rglob("*"):
                if _should_index(fpath):
                    all_files.append(fpath)
                    external_map[fpath] = source_label

    docs: Dict[str, Dict[str, Any]] = {}
    chunks_v2: List[Dict[str, str]] = []          # {"d": rel_key, "i": chunk_id, "t": text}
    chunk_terms: List[set] = []                    # 与 chunks_v2 平行：每 chunk 的去重词条
    term_doc_freq: Dict[str, int] = {}

    for file_path in sorted(all_files):
        # v5.0: 计算 rel_key 和 source（支持外部 wiki）
        source_label = external_map.get(file_path, "")
        if source_label:
            # 外部 wiki 文件：用 source_label/ 作为前缀
            wiki_dir = None
            for wd, sl in extra_wiki_dirs:
                if sl == source_label:
                    wiki_dir = wd
                    break
            if wiki_dir:
                try:
                    rel = file_path.relative_to(wiki_dir)
                    rel_key = f"{source_label}/{rel}"
                    source = source_label
                except ValueError:
                    rel_key = str(file_path)
                    source = source_label
            else:
                rel_key = str(file_path)
                source = source_label
        else:
            # CoPilot 内部文件
            rel_key = str(file_path.relative_to(KNOWLEDGE_DIR))
            if "qa/" in rel_key:
                source = "qa"
            elif "wiki/" in rel_key:
                source = "wiki"
            else:
                source = "raw"

        mtime = file_path.stat().st_mtime

        # 读取并索引
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            continue

        # 解析 frontmatter 获取额外元数据（wiki 和 hermes-wiki 共用）
        title = file_path.stem
        tags: List[str] = []
        growth_stage = ""
        project: Any = ""
        if source in ("wiki", "hermes-wiki", "qa"):
            try:
                fm, body = parse_frontmatter(text)
                title = fm.get("title", title)
                tags = fm.get("tags", [])
                # hermes wiki 缺失 growth_stage，默认 "growing"（结构化但未完全整合）
                growth_stage = fm.get("growth_stage", "growing" if source == "hermes-wiki" else "")
                project = fm.get("project", "")
                # 将 summary/description 加入索引文本（hermes wiki 特有字段）
                summary = fm.get("summary", "")
                description = fm.get("description", "")
                text = body + " " + " ".join(tags) + " " + summary + " " + description
                if growth_stage:
                    text += " " + growth_stage
            except Exception:
                pass

        # 推断 project（v2.7.0）：若 frontmatter 未声明，从路径 wiki/projects/<项目名>/ 推断
        if not project and source in ("wiki", "hermes-wiki"):
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
        for chunk in chunks:
            chunk_idx = len(chunks_v2)
            chunks_v2.append({"d": rel_key, "i": chunk["id"], "t": chunk["text"]})
            terms = set(_tokenize(chunk["text"]))
            chunk_terms.append(terms)
            for term in terms:
                term_doc_freq[term] = term_doc_freq.get(term, 0) + 1

        docs[rel_key] = {
            "title": title,
            "path": rel_key,
            "source": source,
            "size": file_path.stat().st_size,
            "mtime": mtime,
            "chunks": len(chunks),
            "project": project,
        }
        if tags:
            docs[rel_key]["tags"] = tags
        if growth_stage:
            docs[rel_key]["growth_stage"] = growth_stage

    # 计算 IDF
    doc_count = len(chunks_v2) if chunks_v2 else 1
    idf = _compute_idf(doc_count, term_doc_freq)

    # 构建倒排索引（v2: 整型下标 postings；df==1 的中文 2-gram 剔除）
    inverted: Dict[str, List[int]] = {}
    _cjk_re = re.compile(r"[\u4e00-\u9fff]")
    for chunk_idx, terms in enumerate(chunk_terms):
        for term in terms:
            if term_doc_freq.get(term, 0) == 1 and _cjk_re.search(term):
                continue  # 仅出现一次的中文 2-gram：纯噪声，不入倒排
            inverted.setdefault(term, []).append(chunk_idx)

    # 图谱统计
    graph_summary = get_graph_summary()

    index_data = {
        "format": INDEX_FORMAT,
        "documents": docs,
        "chunks": chunks_v2,
        "inverted": inverted,
        "idf": idf,
        "doc_count": doc_count,
        "built_at": _now_utc(),
        "graph_summary": graph_summary,
    }

    # v6.8.51: 索引为机器数据，用紧凑序列化（无缩进）+ 原子写入。
    # indent=2 会给约 300 万条 postings 各加一行，体积膨胀 ~10MB。
    import os
    import tempfile as _tf
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = _tf.mkstemp(dir=str(INDEX_PATH.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, separators=(",", ":"))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(INDEX_PATH))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    _invalidate_index_cache()

    if _log:
        _log.info(f"索引构建完成(v{INDEX_FORMAT}): 文档={len(docs)}, chunk={len(chunks_v2)}, 词项={len(inverted)}, 图谱节点={graph_summary.get('node_count', 0)}")
    return index_data


def search(query: str, top_k: int = 3, source: str = "all", project: str = "",
           doc_type: str = "", tag: str = "", stage: str = "",
           offset: int = 0) -> Dict[str, Any]:
    """根据查询检索相关知识段落（增强版）。

    Args:
        query: 用户输入的查询文本
        top_k: 返回最相关的 K 个段落（每页数量）
        source: "all" | "raw" | "wiki" | "hermes-wiki" — 只返回指定来源的结果
        project: 只返回属于指定项目子库的结果（v2.7.0，空字符串=不过滤）
        doc_type: 按文档类型过滤（concepts/methods/people/papers/projects/entities/topics），空串=不过滤
        tag: 按 frontmatter tags 过滤，空串=不过滤
        stage: 按 growth_stage 过滤（seedling/growing/mature），空串=不过滤
        offset: 分页偏移量，默认0

    Returns:
        {"results": [...], "total": N, "offset": offset, "limit": top_k}
        results 每项含 text, doc, score, source, title, growth_stage, project
    """
    empty = {"results": [], "total": 0, "offset": offset, "limit": top_k}
    if not INDEX_PATH.exists():
        return empty

    # v2: 带签名缓存的加载（格式过期/损坏返回 {}）
    index_data = _load_index_cached()
    if not index_data:
        return empty

    query_terms = _tokenize(query)
    if not query_terms:
        return empty

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
    chunks_v2 = index_data.get("chunks", [])

    # 收集候选（v2: postings 为 chunk 全局整型下标）
    candidates: Dict[int, Dict[str, Any]] = {}
    for term in query_terms:
        for chunk_idx in inverted.get(term, []):
            if chunk_idx not in candidates:
                candidates[chunk_idx] = {"terms": set()}
            candidates[chunk_idx]["terms"].add(term)

    # ── 第一阶段（廉价）：IDF 覆盖率预排序 ──
    # v2 不再存储每 chunk 全量关键词，TF 精确计算推迟到第二阶段，
    # 仅对预排序 top _PHASE2_CANDIDATES 个候选重分词，保证检索延迟有界。
    pre: List[Any] = []  # (覆盖分, chunk_idx)
    for chunk_idx, info in candidates.items():
        chunk = chunks_v2[chunk_idx]
        doc_info = docs.get(chunk["d"], {})

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

        # 文档类型过滤（按 wiki 子目录推断：wiki/{doc_type}/... 或 hermes-wiki/{doc_type}/...）
        if doc_type:
            doc_path_parts = Path(doc_info.get("path", chunk["d"])).parts
            if len(doc_path_parts) >= 2 and doc_path_parts[0] in ("wiki", "hermes-wiki"):
                doc_t = doc_path_parts[1]
            else:
                doc_t = ""
            if doc_t != doc_type:
                continue

        # 标签过滤（按 frontmatter tags）
        if tag:
            doc_tags = doc_info.get("tags", [])
            if not isinstance(doc_tags, list):
                doc_tags = [doc_tags] if doc_tags else []
            if tag not in doc_tags:
                continue

        # 生长阶段过滤
        if stage:
            if doc_info.get("growth_stage", "") != stage:
                continue

        cover = sum(idf.get(t, 1) for t in info["terms"])
        pre.append((cover, chunk_idx))

    if not pre:
        return empty

    pre.sort(key=lambda x: -x[0])
    top_candidates = pre[:_PHASE2_CANDIDATES]

    # ── 第二阶段（精确）：对 top 候选重分词计算 TF-IDF ──
    scored = []
    for cover, chunk_idx in top_candidates:
        chunk = chunks_v2[chunk_idx]
        doc_name = chunk["d"]
        doc_info = docs.get(doc_name, {})
        doc_source = doc_info.get("source", "raw")

        kws = _tokenize(chunk["t"])
        total_terms = len(kws) if kws else 1
        term_freq: Dict[str, int] = {}
        for kw in kws:
            term_freq[kw] = term_freq.get(kw, 0) + 1

        score = 0
        for term in candidates[chunk_idx]["terms"]:
            tf = term_freq.get(term, 0) / total_terms
            idf_val = idf.get(term, 1)
            score += tf * idf_val

        # wiki 结果加权（结构化知识优先，含 hermes-wiki）
        if doc_source in ("wiki", "hermes-wiki"):
            score *= 1.2
            # mature 阶段再加权
            if doc_info.get("growth_stage") == "mature":
                score *= 1.1

        scored.append({
            "text": chunk["t"],
            "doc": doc_name,
            "score": score,
            "source": doc_source,
            "title": doc_info.get("title", doc_name),
            "growth_stage": doc_info.get("growth_stage", ""),
            "project": doc_info.get("project", ""),
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    total = len(scored)
    paged = scored[offset:offset + top_k]
    return {"results": paged, "total": total, "offset": offset, "limit": top_k}


def search_light(query: str, top_k: int = 3, source: str = "all",
                 project: str = "", doc_type: str = "", tag: str = "",
                 stage: str = "", offset: int = 0) -> Dict[str, Any]:
    """轻量检索：只返回标题、摘要、路径和分数，不返回全文。

    用于快速判断是否需要注入上下文，节省内存和序列化开销。

    Returns:
        {"results": [...], "total": N, "offset": offset, "limit": top_k}
    """
    result = search(query, top_k=top_k, source=source, project=project,
                    doc_type=doc_type, tag=tag, stage=stage, offset=offset)
    light = []
    for r in result.get("results", []):
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
    return {
        "results": light,
        "total": result.get("total", 0),
        "offset": result.get("offset", offset),
        "limit": result.get("limit", top_k),
    }


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
        hermes_wiki_count = sum(1 for d in docs.values() if d.get("source") == "hermes-wiki")
        total_chunks = sum(d.get("chunks", 0) for d in docs.values())
        graph = data.get("graph_summary", {})
        return {
            "indexed": True,
            "raw_count": raw_count,
            "wiki_count": wiki_count,
            "hermes_wiki_count": hermes_wiki_count,
            "chunks": total_chunks,
            "built_at": data.get("built_at", ""),
            "graph": graph,
        }
    except Exception:
        return {"indexed": False, "raw_count": 0, "wiki_count": 0, "chunks": 0}


# ─────────────────────────────────────────────
# 上下文构建增强：关联知识拉取
# ─────────────────────────────────────────────

def get_enriched_context(query: str, top_k: int = 3, project: str = "") -> Dict[str, Any]:
    """获取增强的上下文：搜索结果 + 关联知识。

    Args:
        query: 查询文本
        top_k: 直接搜索结果数
        project: 课题分区过滤（空串=全局检索）。非空时先按课题检索，
                 不足 top_k 则补充全局检索，保证不丢失全局知识。

    Returns:
        {
            "results": [...],       # 直接搜索结果
            "related": [...],       # 通过图谱关联的知识
            "missing_concepts": [...],  # 查询中可能缺失的新概念
        }
    """
    # 项目感知检索：先按课题分区检索，不足则补充全局检索
    if project:
        kb_result = search(query, top_k=top_k, project=project)
        results = kb_result.get("results", [])
        if len(results) < top_k:
            extra = search(query, top_k=top_k - len(results))
            results.extend(extra.get("results", []))
    else:
        kb_result = search(query, top_k=top_k, source="all")
        results = kb_result.get("results", [])

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
    indexed_terms = set(_load_index_cached().get("inverted", {}).keys())

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


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> bool:
    """自检：验证索引构建 / TF-IDF 搜索 / 索引状态 / raw 文件列表。

    使用临时目录隔离，patch 路径常量并注入门面依赖桩。
    """
    import tempfile
    import shutil

    print("=" * 50)
    print("◐ kb_index 自检")
    print("=" * 50)

    passed = 0
    total = 0
    tmp_dir = tempfile.mkdtemp(prefix="kb_index_test_")
    tmp_kb = Path(tmp_dir) / "knowledge"
    (tmp_kb / "raw" / "papers").mkdir(parents=True, exist_ok=True)
    (tmp_kb / "raw" / "notes").mkdir(parents=True, exist_ok=True)
    (tmp_kb / "wiki" / "concepts").mkdir(parents=True, exist_ok=True)

    # 保存原始路径常量，测试后恢复
    global INDEX_PATH, KNOWLEDGE_DIR, RAW_DIR, WIKI_DIR, HERMES_WIKI_DIR, HERMES_BRIEFING_PAPERS_DIR, _ensure_dirs, log_growth, _load_aliases, _log
    _orig = {
        "INDEX_PATH": INDEX_PATH, "KNOWLEDGE_DIR": KNOWLEDGE_DIR,
        "RAW_DIR": RAW_DIR, "WIKI_DIR": WIKI_DIR, "HERMES_WIKI_DIR": HERMES_WIKI_DIR,
        "HERMES_BRIEFING_PAPERS_DIR": HERMES_BRIEFING_PAPERS_DIR,
    }
    INDEX_PATH = tmp_kb / "index.json"
    KNOWLEDGE_DIR = tmp_kb
    RAW_DIR = tmp_kb / "raw"
    WIKI_DIR = tmp_kb / "wiki"
    HERMES_WIKI_DIR = tmp_kb / "nonexistent-hermes-wiki"  # v5.0: 隔离，不索引真实 hermes wiki
    HERMES_BRIEFING_PAPERS_DIR = tmp_kb / "nonexistent-hermes-briefings"  # v6.8.1: 隔离

    # patch kb_graph 路径（build_index 调用 get_graph_summary）
    import kb_graph as _kg
    _orig_kg_graph = _kg.GRAPH_PATH
    _kg.GRAPH_PATH = tmp_kb / "graph.json"

    # 保存原始注入依赖，测试后恢复
    _orig_deps = {
        "_ensure_dirs": _ensure_dirs, "log_growth": log_growth,
        "_load_aliases": _load_aliases, "_log": _log,
    }

    try:
        # 注入门面依赖桩
        def _stub_ensure_dirs():
            for d in [RAW_DIR / "papers", RAW_DIR / "notes", RAW_DIR / "webclips"]:
                d.mkdir(parents=True, exist_ok=True)
            for t in ["concepts", "methods", "people", "papers", "projects"]:
                (WIKI_DIR / t).mkdir(parents=True, exist_ok=True)

        _ensure_dirs = _stub_ensure_dirs
        log_growth = lambda *a, **kw: None
        _load_aliases = lambda: {}
        _log = None

        # 准备测试文件
        (RAW_DIR / "notes" / "test_note.md").write_text(
            "固体高次谐波产生 HHG 相位匹配条件研究笔记", encoding="utf-8")
        (WIKI_DIR / "concepts" / "固体高次谐波.md").write_text(
            '---\ntitle: "固体高次谐波"\ntype: "concepts"\ngrowth_stage: "mature"\ntags: ["HHG"]\n---\n'
            '固体高次谐波产生是强场超快光学的重要课题', encoding="utf-8")

        # [1/5] 索引构建
        total += 1
        idx = build_index(force=True, extra_wiki_dirs=[])  # v5.0: 隔离外部 wiki
        docs = idx.get("documents", {})
        if len(docs) >= 2 and "inverted" in idx:
            passed += 1
            print(f"  [1/{total}] ✓ 索引构建: {len(docs)} 文档, {len(idx['inverted'])} 词项")
        else:
            print(f"  [1/{total}] ✗ 索引构建: docs={len(docs)}")

        # [2/5] TF-IDF 搜索
        total += 1
        res = search("固体高次谐波", top_k=3)
        results = res.get("results", [])
        if isinstance(res, dict) and "total" in res and len(results) >= 1 and results[0]["score"] > 0:
            passed += 1
            print(f"  [2/{total}] ✓ 搜索: 命中 {len(results)} 条 total={res['total']} (top score={results[0]['score']:.2f})")
        else:
            print(f"  [2/{total}] ✗ 搜索: res={res}")

        # [3/5] 轻量搜索
        total += 1
        light_res = search_light("HHG", top_k=2)
        light = light_res.get("results", []) if isinstance(light_res, dict) else light_res
        if isinstance(light, list) and all("summary" in r for r in light):
            passed += 1
            print(f"  [3/{total}] ✓ 轻量搜索: {len(light)} 条 (含 summary)")
        else:
            print(f"  [3/{total}] ✗ 轻量搜索: light={light}")

        # [4/5] 索引状态
        total += 1
        status = get_index_status()
        if status.get("indexed") and status.get("raw_count", 0) >= 1:
            passed += 1
            print(f"  [4/{total}] ✓ 索引状态: raw={status['raw_count']}, wiki={status.get('wiki_count', 0)}")
        else:
            print(f"  [4/{total}] ✗ 索引状态: status={status}")

        # [5/5] raw 文件列表
        total += 1
        raw_files = list_raw_files()
        if len(raw_files) >= 1 and raw_files[0]["name"] == "test_note.md":
            passed += 1
            print(f"  [5/{total}] ✓ raw 列表: {len(raw_files)} 文件")
        else:
            print(f"  [5/{total}] ✗ raw 列表: {raw_files}")

        # [6/6] v5.0: 外部 wiki 目录索引
        total += 1
        ext_wiki = Path(tmp_dir) / "external-wiki"
        (ext_wiki / "concepts").mkdir(parents=True, exist_ok=True)
        (ext_wiki / "concepts" / "阿秒科学.md").write_text(
            '---\ntitle: "阿秒科学"\ntype: "concept"\ntags: ["attosecond"]\n'
            'summary: "阿秒科学是研究阿秒时间尺度电子动力学的学科"\n---\n'
            '阿秒科学研究阿秒（10^-18秒）时间尺度的电子动力学', encoding="utf-8")
        idx2 = build_index(force=True, extra_wiki_dirs=[(ext_wiki, "hermes-wiki")])
        docs2 = idx2.get("documents", {})
        ext_docs = {k: v for k, v in docs2.items() if v.get("source") == "hermes-wiki"}
        if len(ext_docs) >= 1:
            # 验证搜索能命中外部 wiki
            res2 = search("阿秒科学", top_k=3)
            hit_external = any(r.get("source") == "hermes-wiki" for r in res2.get("results", []))
            if hit_external:
                passed += 1
                print(f"  [6/{total}] ✓ 外部 wiki 索引: {len(ext_docs)} 文档, 搜索命中")
            else:
                print(f"  [6/{total}] ✗ 外部 wiki 索引成功但搜索未命中")
        else:
            print(f"  [6/{total}] ✗ 外部 wiki 未被索引: docs2 keys={list(docs2.keys())[:5]}")
    finally:
        # 恢复路径常量
        INDEX_PATH = _orig["INDEX_PATH"]
        KNOWLEDGE_DIR = _orig["KNOWLEDGE_DIR"]
        RAW_DIR = _orig["RAW_DIR"]
        WIKI_DIR = _orig["WIKI_DIR"]
        HERMES_WIKI_DIR = _orig["HERMES_WIKI_DIR"]
        HERMES_BRIEFING_PAPERS_DIR = _orig["HERMES_BRIEFING_PAPERS_DIR"]
        _kg.GRAPH_PATH = _orig_kg_graph
        # 恢复注入依赖
        _ensure_dirs = _orig_deps["_ensure_dirs"]
        log_growth = _orig_deps["log_growth"]
        _load_aliases = _orig_deps["_load_aliases"]
        _log = _orig_deps["_log"]
        shutil.rmtree(tmp_dir, ignore_errors=True)

    ok = passed == total
    print(f"\n{'✓' if ok else '✗'} kb_index: {passed}/{total} 通过")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_check() else 1)
