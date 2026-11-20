#!/usr/bin/env python3
"""课题知识库引擎 —— 三层分层（raw/parsed/summary）+ 课题级倒排索引 + 标签索引。

复用 knowledge_base.py 的子库思想（按 project 隔离），但采用课题专属的三层
分层结构，每个课题的知识库独立存放在 projects/{project_id}/kb/ 下：

    projects/{project_id}/kb/
    ├── raw/                    # 原始信息层
    │   ├── proposals/          # 研究设想
    │   ├── references/         # 参考文献PDF/笔记
    │   └── data/               # 实验数据/计算结果
    ├── parsed/                 # 解析信息层（林赛结构化笔记）
    │   ├── concepts/
    │   ├── methods/
    │   └── literature/
    ├── summary/                # 概要信息层
    │   ├── unit-reports/       # 单元进展报告
    │   ├── milestone-reviews/  # 里程碑回顾
    │   └── project-summary.md  # 课题总结
    ├── index.json              # 课题级倒排索引
    ├── tags.json               # 课题级标签索引
    └── graph.json              # 课题级知识图谱

文档统一采用 YAML frontmatter + Markdown 格式，frontmatter 字段：
    title / layer / type / tags / unit / source_raw / created / updated

用法示例:
    >>> from project_kb import add_document, search, get_kb_stats
    >>> from project_manager import create_project
    >>> pid, _ = create_project("固体HHG相位匹配研究", goal="建立理论模型")
    >>> rel = add_document(pid, "parsed", "concepts", "相位匹配",
    ...                    "相位匹配是HHG效率的关键...", tags=["HHG"], unit="UNIT-001")
    >>> hits = search(pid, "相位匹配 HHG", top_k=3)
    >>> stats = get_kb_stats(pid)

规范:
    - 仅使用 Python 3 标准库
    - 路径使用 pathlib.Path，PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - JSON 输出 ensure_ascii=False, indent=2
    - 时间戳使用 UTC ISO 格式
"""

import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import (
    now_utc as _now_utc,
    load_json as _read_json,
    save_json as _write_json,
    safe_filename as _safe_fname,
)
from kb_text import _STOPWORDS
from project_manager import (
    _project_dir,
    get_project,
    create_project,
    delete_project,
)

# ─────────────────────────────────────────────
# 常量
# ─────────────────────────────────────────────

# 三层常量
LAYERS = ("raw", "parsed", "summary")

# type → layer 映射
TYPE_LAYER_MAP: Dict[str, str] = {
    "proposals": "raw",
    "references": "raw",
    "data": "raw",
    "concepts": "parsed",
    "methods": "parsed",
    "literature": "parsed",
    "unit-reports": "summary",
    "milestone-reviews": "summary",
    "project-summary": "summary",
}

# 各层包含的子类型（project-summary 为单文件，不单独建子目录）
_LAYER_TYPES: Dict[str, Tuple[str, ...]] = {
    "raw": ("proposals", "references", "data"),
    "parsed": ("concepts", "methods", "literature"),
    "summary": ("unit-reports", "milestone-reviews"),
}

# 文本文件后缀（导入时尝试读取内容生成 .md）
_TEXT_EXTS = {
    ".md", ".txt", ".rst", ".json", ".csv", ".py", ".js", ".ts",
    ".sh", ".yaml", ".yml", ".tex", ".bib", ".log", ".ini", ".toml",
}

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


# ─────────────────────────────────────────────
# 路径与目录
# ─────────────────────────────────────────────

def get_kb_dir(project_id: str) -> Path:
    """返回课题知识库根目录。"""
    return _project_dir(project_id) / "kb"


def get_layer_dir(project_id: str, layer: str) -> Path:
    """返回指定层级的目录。"""
    if layer not in LAYERS:
        raise ValueError(f"✗ 无效层级: {layer}，有效值: {LAYERS}")
    return get_kb_dir(project_id) / layer


def _ensure_kb_dirs(project_id: str) -> Path:
    """确保课题知识库目录结构存在，返回 kb 根目录。"""
    kb_dir = get_kb_dir(project_id)
    for layer, types in _LAYER_TYPES.items():
        for t in types:
            (kb_dir / layer / t).mkdir(parents=True, exist_ok=True)
    # summary 根目录（存放 project-summary.md）
    (kb_dir / "summary").mkdir(parents=True, exist_ok=True)
    return kb_dir


def _rel_path_str(fpath: Path, base: Path) -> str:
    """返回相对路径字符串（统一用正斜杠，跨平台一致）。"""
    return str(fpath.relative_to(base)).replace("\\", "/")


# ─────────────────────────────────────────────
# Frontmatter 解析与构建（简化版，独立实现）
# ─────────────────────────────────────────────

def _parse_frontmatter(text: str) -> Tuple[dict, str]:
    """解析 Markdown frontmatter（简化版 YAML）。

    Returns:
        (frontmatter_dict, body_markdown)
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    yaml_text = m.group(1).strip()
    body = m.group(2).strip()
    meta: Dict[str, Any] = {}
    for line in yaml_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        # 数组：["a", "b"] 或 [a, b] 或 []
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if not inner:
                meta[key] = []
            else:
                meta[key] = [
                    x.strip().strip('"').strip("'")
                    for x in inner.split(",")
                    if x.strip()
                ]
        elif val.lower() in ("true", "false"):
            meta[key] = val.lower() == "true"
        elif re.match(r"^-?\d+\.\d+$", val):
            meta[key] = float(val)
        elif re.match(r"^-?\d+$", val):
            meta[key] = int(val)
        else:
            meta[key] = val.strip('"').strip("'")
    return meta, body


def _build_frontmatter(meta: dict) -> str:
    """构建 Markdown frontmatter（简化版 YAML，Obsidian 兼容）。"""
    lines = ["---"]
    for key, val in meta.items():
        if isinstance(val, list):
            if not val:
                lines.append(f"{key}: []")
            else:
                # 去重保持顺序
                seen = set()
                deduped = []
                for v in val:
                    if v not in seen:
                        seen.add(v)
                        deduped.append(v)
                items = ", ".join(f'"{v}"' for v in deduped)
                lines.append(f"{key}: [{items}]")
        elif isinstance(val, bool):
            lines.append(f'{key}: {"true" if val else "false"}')
        elif isinstance(val, (int, float)):
            lines.append(f"{key}: {val}")
        else:
            s = str(val).replace('"', '\\"')
            lines.append(f'{key}: "{s}"')
    lines.append("---")
    return "\n".join(lines)


def _safe_filename(name: str) -> str:
    """生成安全文件名（保留中文/字母/数字/连字符，限长 80 字符）。"""
    safe = _safe_fname(name)
    if len(safe) > 80:
        safe = safe[:80]
    return safe if safe else "untitled"


# ─────────────────────────────────────────────
# 分词（简化版倒排索引用）
# ─────────────────────────────────────────────

def _tokenize(text: str) -> List[str]:
    """分词：中文 2-3 字 gram + 英文单词 + 数字。

    保留独立版本而非直接复用 kb_text._tokenize：
    kb_text 使用 2,3,4 字 gram（含 4-gram），而课题知识库索引用 2,3 字 gram。
    gram 大小直接影响 TF-IDF 倒排索引的粒度与搜索评分，替换为 4-gram 版本
    会改变既有课题索引的 token 分布与排序结果，故保持独立。
    _STOPWORDS 已统一从 kb_text 导入（合并版）。
    """
    tokens: List[str] = []
    # 中文字符串：提取 2 字和 3 字 gram
    for m in re.finditer(r"[\u4e00-\u9fff]+", text):
        word = m.group()
        for size in (2, 3):
            for i in range(len(word) - size + 1):
                tokens.append(word[i : i + size])
    # 英文单词（≥2 字符）
    for m in re.finditer(r"[a-zA-Z_][a-zA-Z0-9_]{1,}", text):
        tokens.append(m.group().lower())
    # 数字
    for m in re.finditer(r"\d+\.?\d*", text):
        tokens.append(m.group())
    return [t for t in tokens if t not in _STOPWORDS]


def _make_snippet(content: str, query_terms: List[str], max_len: int = 120) -> str:
    """从文档内容中截取包含首个命中词的片段。"""
    text = re.sub(r"\s+", " ", content.strip())
    pos = -1
    for term in query_terms:
        idx = text.find(term)
        if idx >= 0 and (pos < 0 or idx < pos):
            pos = idx
    if pos < 0:
        pos = 0
    start = max(0, pos - 30)
    end = min(len(text), start + max_len)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


# ─────────────────────────────────────────────
# 文档增删读
# ─────────────────────────────────────────────

def add_document(
    project_id: str,
    layer: str,
    doc_type: str,
    title: str,
    content: str,
    tags: Optional[List[str]] = None,
    unit: str = "",
    source_raw: str = "",
) -> str:
    """向课题知识库添加文档。

    1. 根据 doc_type 确定 layer（传入的 layer 可覆盖）
    2. 生成文件路径: kb/{layer}/{doc_type}/{safe_filename(title)}.md
    3. 写入 frontmatter + content
    4. 更新课题级 index.json 和 tags.json
    返回文件相对路径（相对 kb 根目录）
    """
    _ensure_kb_dirs(project_id)
    kb_dir = get_kb_dir(project_id)

    # 确定有效层级：显式传入合法 layer 时覆盖，否则按 doc_type 推断
    if layer in LAYERS:
        effective_layer = layer
    else:
        effective_layer = TYPE_LAYER_MAP.get(doc_type, "raw")

    # 生成文件路径（project-summary 为 summary 根目录下的单文件）
    if doc_type == "project-summary":
        file_path = kb_dir / "summary" / "project-summary.md"
    else:
        file_path = kb_dir / effective_layer / doc_type / f"{_safe_filename(title)}.md"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # 若文件已存在，保留原 created 时间
    created = _now_utc()
    if file_path.exists():
        try:
            old_fm, _ = _parse_frontmatter(file_path.read_text(encoding="utf-8"))
            if old_fm.get("created"):
                created = old_fm["created"]
        except Exception:
            pass

    tags = tags if tags else []
    now = _now_utc()
    meta = {
        "title": title,
        "layer": effective_layer,
        "type": doc_type,
        "tags": tags,
        "unit": unit,
        "source_raw": source_raw,
        "created": created,
        "updated": now,
    }
    page_text = _build_frontmatter(meta) + "\n\n" + content.strip()
    file_path.write_text(page_text, encoding="utf-8")

    rel_path = _rel_path_str(file_path, kb_dir)

    # 更新 tags.json
    _update_tags_index(project_id, rel_path, tags)

    # 重建倒排索引
    build_index(project_id)

    return rel_path


def get_document(project_id: str, rel_path: str) -> Optional[dict]:
    """读取文档，返回 {frontmatter, content, path}。"""
    kb_dir = get_kb_dir(project_id)
    fpath = kb_dir / rel_path
    if not fpath.exists():
        return None
    try:
        text = fpath.read_text(encoding="utf-8")
    except Exception:
        return None
    fm, body = _parse_frontmatter(text)
    return {
        "frontmatter": fm,
        "content": body,
        "path": rel_path,
    }


def list_documents(
    project_id: str,
    layer: str = "all",
    doc_type: str = "",
    tag: str = "",
    unit: str = "",
) -> List[dict]:
    """列出文档，支持多维度过滤。

    Args:
        layer: "all" | "raw" | "parsed" | "summary"
        doc_type: 按类型过滤（如 "concepts"）
        tag: 按标签过滤
        unit: 按所属单元过滤
    """
    kb_dir = get_kb_dir(project_id)
    if not kb_dir.exists():
        return []

    layers_to_scan = [layer] if layer in LAYERS else list(LAYERS)
    results: List[dict] = []

    for lay in layers_to_scan:
        layer_dir = kb_dir / lay
        if not layer_dir.exists():
            continue
        for fpath in sorted(layer_dir.rglob("*.md")):
            try:
                text = fpath.read_text(encoding="utf-8")
            except Exception:
                continue
            fm, _ = _parse_frontmatter(text)
            rel = _rel_path_str(fpath, kb_dir)
            doc_type_val = fm.get("type", fpath.parent.name)

            if doc_type and doc_type != doc_type_val:
                continue

            doc_tags = fm.get("tags", [])
            if not isinstance(doc_tags, list):
                doc_tags = [doc_tags] if doc_tags else []
            if tag and tag not in doc_tags:
                continue

            doc_unit = fm.get("unit", "")
            if unit and doc_unit != unit:
                continue

            try:
                size = fpath.stat().st_size
            except Exception:
                size = 0

            results.append({
                "path": rel,
                "title": fm.get("title", fpath.stem),
                "layer": fm.get("layer", lay),
                "type": doc_type_val,
                "tags": doc_tags,
                "unit": doc_unit,
                "source_raw": fm.get("source_raw", ""),
                "created": fm.get("created", ""),
                "updated": fm.get("updated", ""),
                "size": size,
            })
    return results


# ─────────────────────────────────────────────
# 倒排索引
# ─────────────────────────────────────────────

def build_index(project_id: str) -> dict:
    """构建课题级倒排索引。

    扫描 kb/{raw,parsed,summary} 下所有 .md 文件，分词后计算 TF-IDF，
    生成 index.json：{"word": [{"path": "...", "score": 1.0}, ...]}。
    """
    kb_dir = _ensure_kb_dirs(project_id)

    # 收集所有文档的词频信息
    docs: Dict[str, Dict[str, Any]] = {}  # rel_path -> {tf, token_count, title}
    for layer in LAYERS:
        layer_dir = kb_dir / layer
        if not layer_dir.exists():
            continue
        for fpath in sorted(layer_dir.rglob("*.md")):
            try:
                text = fpath.read_text(encoding="utf-8")
            except Exception:
                continue
            fm, body = _parse_frontmatter(text)
            # 索引 frontmatter 值 + 正文（使标签/标题/单元可被检索）
            index_text = body
            for v in fm.values():
                if isinstance(v, list):
                    index_text += " " + " ".join(str(x) for x in v)
                elif v:
                    index_text += " " + str(v)
            tokens = _tokenize(index_text)
            rel = _rel_path_str(fpath, kb_dir)
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            docs[rel] = {
                "tf": tf,
                "token_count": len(tokens),
                "title": fm.get("title", fpath.stem),
            }

    # 计算 IDF
    N = len(docs) if docs else 1
    df: Dict[str, int] = {}
    for info in docs.values():
        for term in info["tf"].keys():
            df[term] = df.get(term, 0) + 1
    idf = {term: math.log(N / (freq + 1)) + 1 for term, freq in df.items()}

    # 构建倒排索引
    inverted: Dict[str, List[dict]] = {}
    for rel, info in docs.items():
        total = info["token_count"] if info["token_count"] else 1
        for term, count in info["tf"].items():
            tf_val = count / total
            score = tf_val * idf.get(term, 1.0)
            inverted.setdefault(term, []).append({
                "path": rel,
                "score": round(score, 6),
            })

    # 每个 posting list 按分数降序
    for term in inverted:
        inverted[term].sort(key=lambda x: x["score"], reverse=True)

    # 写入 index.json（$meta 存放元信息，$ 不会出现在分词结果中）
    index_data = dict(inverted)
    index_data["$meta"] = {
        "doc_count": len(docs),
        "built_at": _now_utc(),
    }
    _write_json(kb_dir / "index.json", index_data)

    # 初始化 graph.json（若不存在）
    graph_path = kb_dir / "graph.json"
    if not graph_path.exists():
        _write_json(graph_path, {"nodes": {}, "edges": []})

    return index_data


def search(
    project_id: str,
    query: str,
    layer: str = "all",
    top_k: int = 5,
    offset: int = 0,
) -> Dict[str, Any]:
    """在课题知识库中搜索。

    复用 knowledge_base 的搜索逻辑，但限定在课题目录内。
    通过构建课题级 index.json 实现倒排索引。

    Args:
        query: 查询文本
        layer: "all" | "raw" | "parsed" | "summary"
        top_k: 返回最相关的 K 条（每页数量）
        offset: 分页偏移量，默认0

    Returns:
        {"results": [...], "total": N, "offset": offset, "limit": top_k}
        results 每项含 title, path, layer, score, snippet
    """
    empty = {"results": [], "total": 0, "offset": offset, "limit": top_k}
    kb_dir = get_kb_dir(project_id)
    index_path = kb_dir / "index.json"
    if not index_path.exists():
        build_index(project_id)

    index = _read_json(index_path, default={})
    if not index:
        return empty

    query_terms = _tokenize(query)
    if not query_terms:
        return empty

    # 聚合每个文档的得分
    scores: Dict[str, float] = {}
    for term in query_terms:
        for entry in index.get(term, []):
            p = entry.get("path", "")
            if not p:
                continue
            # 层级过滤
            if layer in LAYERS:
                doc_layer = p.split("/")[0] if "/" in p else ""
                if doc_layer != layer:
                    continue
            scores[p] = scores.get(p, 0.0) + entry.get("score", 0.0)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    total = len(ranked)
    paged = ranked[offset:offset + top_k]

    results: List[dict] = []
    for path, score in paged:
        doc_layer = path.split("/")[0] if "/" in path else ""
        title = Path(path).stem
        snippet = ""
        doc = get_document(project_id, path)
        if doc:
            fm = doc.get("frontmatter", {})
            title = fm.get("title", title)
            snippet = _make_snippet(doc.get("content", ""), query_terms)
        results.append({
            "title": title,
            "path": path,
            "layer": doc_layer,
            "score": round(score, 4),
            "snippet": snippet,
        })
    return {"results": results, "total": total, "offset": offset, "limit": top_k}


# ─────────────────────────────────────────────
# 标签索引
# ─────────────────────────────────────────────

def _update_tags_index(project_id: str, rel_path: str, tags: List[str]) -> None:
    """更新 tags.json（追加路径到对应标签列表）。"""
    if not tags:
        return
    kb_dir = get_kb_dir(project_id)
    tags_path = kb_dir / "tags.json"
    tags_data = _read_json(tags_path, default={})
    for t in tags:
        paths = tags_data.setdefault(t, [])
        if rel_path not in paths:
            paths.append(rel_path)
    _write_json(tags_path, tags_data)


def get_tags(project_id: str) -> dict:
    """获取课题级标签索引 {tag: [file_paths]}。"""
    kb_dir = get_kb_dir(project_id)
    return _read_json(kb_dir / "tags.json", default={})


def add_tag(project_id: str, rel_path: str, tag: str) -> None:
    """为文档添加标签（同步更新 tags.json 与 frontmatter）。"""
    kb_dir = get_kb_dir(project_id)
    tags_path = kb_dir / "tags.json"
    tags_data = _read_json(tags_path, default={})
    paths = tags_data.setdefault(tag, [])
    if rel_path not in paths:
        paths.append(rel_path)
    _write_json(tags_path, tags_data)

    # 同步 frontmatter
    fpath = kb_dir / rel_path
    if fpath.exists():
        try:
            text = fpath.read_text(encoding="utf-8")
            fm, body = _parse_frontmatter(text)
            existing = fm.get("tags", [])
            if not isinstance(existing, list):
                existing = [existing] if existing else []
            if tag not in existing:
                existing.append(tag)
            fm["tags"] = existing
            fm["updated"] = _now_utc()
            new_text = _build_frontmatter(fm) + "\n\n" + body
            fpath.write_text(new_text, encoding="utf-8")
        except Exception:
            pass

    # 重建索引以反映新标签
    build_index(project_id)


# ─────────────────────────────────────────────
# 统计
# ─────────────────────────────────────────────

def get_kb_stats(project_id: str) -> dict:
    """获取知识库统计信息。

    Returns:
        {total, by_layer, by_type, by_tag}
    """
    docs = list_documents(project_id)
    by_layer: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    by_tag: Dict[str, int] = {}
    for d in docs:
        lay = d.get("layer", "unknown")
        by_layer[lay] = by_layer.get(lay, 0) + 1
        t = d.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        for tg in d.get("tags", []):
            by_tag[tg] = by_tag.get(tg, 0) + 1
    return {
        "total": len(docs),
        "by_layer": by_layer,
        "by_type": by_type,
        "by_tag": by_tag,
    }


# ─────────────────────────────────────────────
# 外部文件导入
# ─────────────────────────────────────────────

def import_raw_file(
    project_id: str,
    source_path: str,
    doc_type: str = "references",
    title: str = "",
    tags: Optional[List[str]] = None,
) -> str:
    """将外部文件导入课题知识库 raw 层。

    1. 复制文件到 kb/raw/{doc_type}/（或对应层级）
    2. 如果是文本文件，提取内容生成 .md 文件（带 frontmatter）
    3. 如果是 PDF/二进制，只复制原文件，记录元信息（生成 sidecar .md）

    返回导入后的相对路径（.md 文件）
    """
    _ensure_kb_dirs(project_id)
    kb_dir = get_kb_dir(project_id)
    src = Path(source_path)
    if not src.exists():
        raise FileNotFoundError(f"✗ 源文件不存在: {source_path}")

    title = title or src.stem
    safe_title = _safe_filename(title)
    ext = src.suffix.lower()
    effective_layer = TYPE_LAYER_MAP.get(doc_type, "raw")

    # 目标目录
    if doc_type == "project-summary":
        target_dir = kb_dir / "summary"
    else:
        target_dir = kb_dir / effective_layer / doc_type
    target_dir.mkdir(parents=True, exist_ok=True)

    tags = tags if tags else []
    now = _now_utc()

    if ext in _TEXT_EXTS:
        # 文本文件：读取内容生成 .md
        try:
            content = src.read_text(encoding="utf-8")
        except Exception:
            content = src.read_bytes().decode("utf-8", errors="ignore")

        # 若本身是 .md，尝试剥离已有 frontmatter，仅保留正文
        if ext == ".md":
            _, body = _parse_frontmatter(content)
            if body:
                content = body

        md_path = target_dir / f"{safe_title}.md"
        meta = {
            "title": title,
            "layer": effective_layer,
            "type": doc_type,
            "tags": tags,
            "unit": "",
            "source_raw": src.name,
            "created": now,
            "updated": now,
        }
        page_text = _build_frontmatter(meta) + "\n\n" + content.strip()
        md_path.write_text(page_text, encoding="utf-8")
        rel_path = _rel_path_str(md_path, kb_dir)
    else:
        # 二进制文件：复制原文件 + 生成 sidecar 元信息 .md
        dest = target_dir / src.name
        counter = 1
        while dest.exists():
            dest = target_dir / f"{src.stem}_{counter}{src.suffix}"
            counter += 1
        dest.write_bytes(src.read_bytes())

        md_path = target_dir / f"{dest.stem}.md"
        meta = {
            "title": title,
            "layer": effective_layer,
            "type": doc_type,
            "tags": tags,
            "unit": "",
            "source_raw": dest.name,
            "created": now,
            "updated": now,
        }
        body = (
            f"# {title}\n\n"
            f"> 二进制文件元信息记录。原始文件: `{dest.name}`\n\n"
            f"- 大小: {dest.stat().st_size} 字节\n"
            f"- 格式: {src.suffix}\n"
            f"- 导入时间: {now}\n"
        )
        page_text = _build_frontmatter(meta) + "\n\n" + body
        md_path.write_text(page_text, encoding="utf-8")
        rel_path = _rel_path_str(md_path, kb_dir)

    # 更新标签索引与倒排索引
    _update_tags_index(project_id, rel_path, tags)
    build_index(project_id)

    return rel_path


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> None:
    """自检：创建测试课题 → 添加文档 → 搜索 → 标签 → 统计 → 清理。"""
    print("=" * 50)
    print("◐ project_kb 自检")
    print("=" * 50)

    print("\n[1/8] 创建测试课题...")
    pid, _ = create_project("KB自检测试课题", goal="验证课题知识库引擎")
    print(f"  课题ID: {pid}")
    print(f"  知识库目录: {get_kb_dir(pid)}")

    try:
        print("\n[2/8] 添加 raw 层文档(references)...")
        rel1 = add_document(
            pid, "raw", "references", "测试参考文献",
            "这是一篇关于固体高次谐波产生(HHG)的参考文献笔记，"
            "讨论了相位匹配条件与色散补偿。",
            tags=["HHG", "固体"],
        )
        print(f"  路径: {rel1}")

        print("\n[3/8] 添加 parsed 层文档(concepts)...")
        rel2 = add_document(
            pid, "parsed", "concepts", "测试概念",
            "测试概念是高次谐波产生的核心物理机制，"
            "涉及非线性极化与相位匹配。",
            tags=["概念", "HHG"], unit="UNIT-001",
        )
        print(f"  路径: {rel2}")

        print("\n[4/8] 添加 summary 层文档(unit-reports)...")
        rel3 = add_document(
            pid, "summary", "unit-reports", "UNIT-001进展报告",
            "本单元完成了测试概念的验证，确认了相位匹配条件的可行性。",
            tags=["进展"], unit="UNIT-001",
        )
        print(f"  路径: {rel3}")

        print("\n[5/8] 搜索 '测试概念'...")
        res = search(pid, "测试概念", top_k=5)
        results = res.get("results", []) if isinstance(res, dict) else res
        print(f"  命中: {len(results)} 条")
        for r in results:
            print(f"    [{r['layer']}] {r['title']} score={r['score']} "
                  f"snippet={r['snippet'][:40]}")

        print("\n[6/8] 列出文档(按层/按标签过滤)...")
        all_docs = list_documents(pid)
        print(f"  全部文档: {len(all_docs)}")
        parsed_docs = list_documents(pid, layer="parsed")
        print(f"  parsed 层: {len(parsed_docs)}")
        tag_docs = list_documents(pid, tag="HHG")
        print(f"  标签 HHG: {len(tag_docs)}")
        unit_docs = list_documents(pid, unit="UNIT-001")
        print(f"  单元 UNIT-001: {len(unit_docs)}")

        print("\n[7/8] 获取统计信息...")
        stats = get_kb_stats(pid)
        print(f"  总数: {stats['total']}")
        print(f"  按层: {stats['by_layer']}")
        print(f"  按类型: {stats['by_type']}")
        print(f"  按标签: {stats['by_tag']}")

        print("\n[8/8] 验证 get_document/add_tag/get_tags/import_raw_file...")
        doc = get_document(pid, rel2)
        print(f"  get_document: {'✓' if doc else '✗'} "
              f"(title={doc['frontmatter'].get('title') if doc else 'N/A'})")
        add_tag(pid, rel1, "新增标签")
        tags = get_tags(pid)
        print(f"  get_tags 标签数: {len(tags)}")
        print(f"  新增标签命中: {'✓' if '新增标签' in tags else '✗'}")

        # import_raw_file 测试（临时文本文件）
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8")
        tmp.write("导入测试内容：讨论阿秒脉冲的产生机制。")
        tmp.close()
        try:
            rel_imp = import_raw_file(
                pid, tmp.name, doc_type="references",
                title="导入测试文档", tags=["导入"])
            print(f"  import_raw_file: ✓ 路径={rel_imp}")
        finally:
            os.unlink(tmp.name)

        print("\n✓ project_kb 自检完成")
    finally:
        print("\n[清理] 删除测试课题...")
        delete_project(pid, confirm=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="课题知识库引擎")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    parser.add_argument("--stats", metavar="PROJECT_ID", help="查看课题知识库统计")
    parser.add_argument(
        "--search", nargs=2, metavar=("PROJECT_ID", "QUERY"),
        help="在课题知识库中搜索",
    )
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    elif args.stats:
        print(json.dumps(get_kb_stats(args.stats), ensure_ascii=False, indent=2))
    elif args.search:
        pid, query = args.search
        res = search(pid, query)
        for r in res.get("results", []) if isinstance(res, dict) else res:
            print(f"  [{r['layer']}] {r['title']} (score={r['score']})")
            print(f"    {r['snippet']}")
