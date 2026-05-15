#!/usr/bin/env python3
"""林赛知识库引擎 —— raw/wiki 分层 + 知识图谱 + 生长机制。

架构设计（借鉴 Karpathy 笔记系统）：
    knowledge/
    ├── raw/              # 用户提供的原始材料（只读，保留原貌）
    │   ├── papers/       # 论文 PDF/笔记
    │   ├── notes/        # 用户手写笔记
    │   └── webclips/     # 网页剪藏
    ├── wiki/             # LLM 智能管理的结构化知识（林赛的研究笔记）
    │   ├── concepts/     # 核心概念（如"固体高次谐波"、"阿秒脉冲"）
    │   ├── methods/      # 实验方法与技术
    │   ├── people/       # 重要学者与林赛的评价
    │   ├── papers/       # 论文精读笔记（林赛的批注）
    │   └── projects/     # 项目相关的知识聚合
    ├── index.json        # 统一倒排索引（raw + wiki）
    ├── graph.json        # 知识图谱（概念间链接关系）
    ├── growth-log.json   # 知识生长日志（记录何时/为何新增/更新）
    └── README.md         # 知识库使用指南

核心机制：
    1. raw → wiki 提炼：LLM 将原始材料提炼为林赛视角的结构化笔记
    2. 交互触发生长：对话中遇到新概念 → 自动生成 wiki stub → 后续交互中丰满
    3. 知识图谱：概念间的引用关系，用于上下文构建时拉取关联知识
    4. 生长日志：记录林赛的"学习轨迹"

用法示例：
    >>> from knowledge_base import ingest_raw, search, get_wiki_page
    >>> ingest_raw("knowledge/raw/papers/solid_hhg_review.md")
    >>> results = search("固体HHG相位匹配", top_k=3, source="wiki")
    >>> page = get_wiki_page("wiki/concepts/固体高次谐波产生.md")

规范：
    - 仅使用 Python 3 标准库
    - wiki 页面使用 YAML frontmatter + Markdown
    - 索引文件：knowledge/index.json
    - 支持增量索引
"""

import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ─────────────────────────────────────────────
# 路径与常量
# ─────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
RAW_DIR = KNOWLEDGE_DIR / "raw"
WIKI_DIR = KNOWLEDGE_DIR / "wiki"
INDEX_PATH = KNOWLEDGE_DIR / "index.json"
GRAPH_PATH = KNOWLEDGE_DIR / "graph.json"
GROWTH_LOG_PATH = KNOWLEDGE_DIR / "growth-log.json"
ALIASES_PATH = KNOWLEDGE_DIR / "aliases.json"

_SUPPORTED_EXTS = {".md", ".txt", ".rst"}
_WIKI_TYPES = {"concepts", "methods", "people", "papers", "projects"}

_STOPWORDS: Set[str] = {
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人",
    "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
    "你", "会", "着", "没有", "看", "好", "自己", "这", "那",
    "可以", "他", "她", "它", "们", "与", "及", "或", "但是", "因为",
    "所以", "如果", "则", "而", "于", "以", "为", "之", "其", "将",
    "被", "把", "让", "向", "从", "到", "对", "关于", "根据", "按照",
    "我们", "这个", "那个", "什么", "怎么", "如何", "为什么",
}


# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────

def _load_aliases() -> Dict[str, List[str]]:
    """加载别名映射。"""
    if not ALIASES_PATH.exists():
        return {}
    try:
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {k: v if isinstance(v, list) else [v] for k, v in data.items()}
    except Exception:
        return {}


def _expand_query_with_aliases(query: str) -> List[str]:
    """使用别名扩展查询词。"""
    aliases = _load_aliases()
    if not aliases:
        return [query]
    expanded = [query]
    lower_query = query.lower()
    for canonical, alts in aliases.items():
        matches = canonical.lower() in lower_query
        if not matches:
            for alt in alts:
                if alt.lower() in lower_query:
                    matches = True
                    break
        if matches:
            replaced = query
            for alt in alts:
                replaced = replaced.replace(alt, canonical)
            if replaced != query:
                expanded.append(replaced)
    return expanded


def _exact_concept_match(query: str) -> bool:
    """检查查询是否精确命中知识库中的概念标题。"""
    if not INDEX_PATH.exists():
        return False
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        docs = data.get("documents", {})
        query_lower = query.lower()
        for doc_info in docs.values():
            title = doc_info.get("title", "")
            if title and (title.lower() in query_lower or query_lower in title.lower()):
                return True
    except Exception:
        pass
    return False


def _has_tech_terms(query: str) -> bool:
    """检查查询是否包含科研/技术相关术语。"""
    return bool(re.search(
        r"(实验|方案|设计|参数|模型|理论|计算|测量|数据|结果|分析|"
        r"激光|脉冲|光谱|相位|振幅|偏振|晶体|样品|光路|"
        r"论文|文献|引用|作者|期刊|方程|公式|推导|"
        r"HHG|attosecond|nonlinear|dispersion|phase|amplitude)",
        query, re.IGNORECASE,
    ))


def should_search_knowledge(query: str, session_mode: str = "co-working") -> bool:
    """判断当前查询是否需要检索知识库。"""
    text = query.strip()
    if not text or len(text) < 10:
        return False
    # 简单闲聊过滤
    if re.match(r"^(你好|您好|嗨|哈喽|hello|hi|hey|在吗|谢谢|再见|拜拜)", text, re.I):
        return False
    # 1. 用户明确请求
    if re.search(r"(查(?:一)?下|搜索|知识库|我记得|之前说过|相关知识|参考资料|笔记里)", text):
        return True
    # 2. 精确概念匹配
    if _exact_concept_match(text):
        return True
    # 3. 工作模式 + 技术讨论
    if session_mode == "co-working" and len(text) > 50 and _has_tech_terms(text):
        return True
    # 4. 快速验证 + 技术术语
    if session_mode == "quick-check" and _has_tech_terms(text):
        return True
    # 5. 深度对话 + 引用过往
    if session_mode == "deep-talk" and len(text) > 30:
        if re.search(r"(之前|上次|以前|记得|说过|讨论过)", text):
            return True
    return False


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tokenize(text: str) -> List[str]:
    """分词：提取中文词组（2字以上）和英文单词、数字。"""
    tokens = []
    # 中文字符串（连续2字以上）
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}", text):
        word = m.group()
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
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    current_text = ""
    current_idx = 0

    for para in paragraphs:
        if len(current_text) + len(para) + 2 <= max_chars:
            current_text += para + "\n\n"
        else:
            if current_text:
                chunks.append({"id": f"chunk_{current_idx}", "text": current_text.strip()})
                current_idx += 1
            current_text = para + "\n\n"

    if current_text:
        chunks.append({"id": f"chunk_{current_idx}", "text": current_text.strip()})

    return chunks


def _safe_filename(name: str) -> str:
    """将概念名转换为安全的文件名（保留中文）。"""
    # 移除危险字符，但保留中文
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name).strip()
    return safe if safe else "untitled"


def _ensure_dirs() -> None:
    """确保知识库目录结构存在。"""
    for d in [RAW_DIR / "papers", RAW_DIR / "notes", RAW_DIR / "webclips"]:
        d.mkdir(parents=True, exist_ok=True)
    for t in _WIKI_TYPES:
        (WIKI_DIR / t).mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
# Frontmatter 解析与生成
# ─────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """解析 Markdown 文件的 YAML frontmatter。

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
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            # 简单类型推断
            if val.startswith("[") and val.endswith("]"):
                # 数组：["a", "b"] 或 [a, b]
                inner = val[1:-1]
                meta[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            elif val.lower() in ("true", "false"):
                meta[key] = val.lower() == "true"
            elif re.match(r"^\d+\.\d+$", val):
                meta[key] = float(val)
            elif re.match(r"^\d+$", val):
                meta[key] = int(val)
            else:
                meta[key] = val.strip('"').strip("'")
    return meta, body


def build_frontmatter(meta: Dict[str, Any]) -> str:
    """将字典转换为 YAML frontmatter 字符串（Obsidian 兼容格式）。"""
    lines = ["---"]
    for key, val in meta.items():
        if isinstance(val, list):
            if not val:
                lines.append(f'{key}: []')
            else:
                # YAML 标准数组格式，Obsidian 完全兼容
                items = ', '.join(f'"{v}"' for v in val)
                lines.append(f'{key}: [{items}]')
        elif isinstance(val, bool):
            lines.append(f'{key}: {"true" if val else "false"}')
        elif isinstance(val, (int, float)):
            lines.append(f'{key}: {val}')
        else:
            # 字符串值，简单转义双引号
            s = str(val).replace('"', '\\"')
            lines.append(f'{key}: "{s}"')
    lines.append("---")
    return "\n".join(lines)


_WIKILINK_RE = re.compile(r"(?<!\!)\[\[([^\]\|]+)(?:\|[^\]]*)?\]\]")
_WIKILINKS_SECTION_RE = re.compile(
    r"\n?<!-- linsai-wikilinks -->\n.*?<!-- /linsai-wikilinks -->\n?",
    re.DOTALL,
)


def _extract_wikilinks(text: str) -> List[str]:
    """从 Markdown 正文中提取所有 [[WikiLink]]（不含显示文本）。"""
    links = []
    for m in _WIKILINK_RE.finditer(text):
        link = m.group(1).strip()
        if link:
            links.append(link)
    return links


def _get_aliases_for_concept(title: str) -> List[str]:
    """从 aliases.json 中查找给定概念的所有别名。"""
    if not ALIASES_PATH.exists():
        return []
    try:
        with open(ALIASES_PATH, "r", encoding="utf-8") as f:
            aliases = json.load(f)
    except Exception:
        return []
    # aliases.json 格式: {标准词: [别名1, 别名2, ...]}
    # 反向查找：哪些标准词包含此 title 作为别名
    result: Set[str] = set()
    for canonical, alts in aliases.items():
        if canonical == title:
            result.update(alts)
            continue
        if title in alts:
            result.add(canonical)
            result.update(a for a in alts if a != title)
    return sorted(result)


def _inject_wikilinks(page_text: str) -> str:
    """同步 frontmatter 的 related 与正文 [[WikiLink]]，返回更新后的页面文本。

    策略：
    1. 从正文中提取所有已存在的 [[WikiLink]]
    2. 与 frontmatter['related'] 合并、去重
    3. 更新 frontmatter['related']
    4. 在正文末尾注入/更新 <!-- linsai-wikilinks --> 区域
    5. 把当前概念的别名写入 frontmatter['aliases']
    """
    fm, body = parse_frontmatter(page_text)
    if not fm:
        return page_text

    title = fm.get("title", "")

    # 提取正文中已有的 wikilinks（排除 wikilinks 区域本身的）
    # 先去掉旧的 wikilinks 区域
    clean_body = _WIKILINKS_SECTION_RE.sub("\n", body).strip()
    body_links = set(_extract_wikilinks(clean_body))

    # 合并 frontmatter related 和正文中的链接
    related = set(r for r in fm.get("related", []) if isinstance(r, str) and r)
    merged = sorted(related | body_links)
    fm["related"] = merged

    # 注入别名
    aliases = _get_aliases_for_concept(title)
    if aliases:
        fm["aliases"] = aliases

    # 构建 wikilinks 区域
    if merged:
        link_lines = "\n".join(f"- [[{name}]]" for name in merged)
        wikilinks_section = (
            f"\n\n<!-- linsai-wikilinks -->\n"
            f"## 关联概念\n\n"
            f"{link_lines}\n"
            f"<!-- /linsai-wikilinks -->"
        )
    else:
        wikilinks_section = (
            "\n\n<!-- linsai-wikilinks -->\n"
            "## 关联概念\n\n"
            "_暂无关联概念_\n"
            "<!-- /linsai-wikilinks -->"
        )

    new_body = clean_body.rstrip() + wikilinks_section
    new_fm = build_frontmatter(fm)
    return f"{new_fm}\n\n{new_body}\n"


def build_wiki_page(title: str, wiki_type: str, content: str,
                    meta: Optional[Dict[str, Any]] = None) -> str:
    """构建标准 wiki 页面文本（含 frontmatter + 林赛视角结构）。"""
    default_meta = {
        "title": title,
        "type": wiki_type,
        "created": _now_utc(),
        "updated": _now_utc(),
        "tags": [],
        "related": [],
        "source_raw": "",
        "growth_stage": "seedling",
        "confidence": 0.5,
    }
    if meta:
        default_meta.update(meta)
    fm = build_frontmatter(default_meta)
    return f"{fm}\n\n{content.strip()}"


# ─────────────────────────────────────────────
# Wiki 页面管理
# ─────────────────────────────────────────────

def get_wiki_page(rel_path: str) -> Optional[Dict[str, Any]]:
    """读取 wiki 页面，解析 frontmatter 和内容。

    Args:
        rel_path: 相对 knowledge/ 的路径，如 "wiki/concepts/固体高次谐波产生.md"

    Returns:
        {"frontmatter": dict, "body": str, "path": str} 或 None
    """
    path = KNOWLEDGE_DIR / rel_path
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        return {"frontmatter": fm, "body": body, "path": str(rel_path)}
    except Exception:
        return None


def list_wiki_pages(wiki_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """列出所有 wiki 页面（只返回 frontmatter，不加载全文）。"""
    pages = []
    dirs = [WIKI_DIR / wiki_type] if wiki_type else [WIKI_DIR / t for t in _WIKI_TYPES]
    for d in dirs:
        if not d.exists():
            continue
        for fpath in sorted(d.glob("*.md")):
            try:
                text = fpath.read_text(encoding="utf-8")
                fm, _ = parse_frontmatter(text)
                rel = str(fpath.relative_to(KNOWLEDGE_DIR))
                pages.append({
                    "path": rel,
                    "title": fm.get("title", fpath.stem),
                    "type": fm.get("type", wiki_type or "unknown"),
                    "growth_stage": fm.get("growth_stage", "unknown"),
                    "confidence": fm.get("confidence", 0.0),
                    "updated": fm.get("updated", ""),
                    "tags": fm.get("tags", []),
                })
            except Exception:
                continue
    return pages


def save_wiki_page(rel_path: str, content: str, meta: Optional[Dict[str, Any]] = None,
                   append: bool = False) -> str:
    """保存 wiki 页面。

    Args:
        rel_path: 相对 knowledge/ 的路径
        content: Markdown 内容
        meta: frontmatter 数据（如页面已存在则合并更新）
        append: 为 True 时在现有内容后追加

    Returns:
        保存的文件路径（相对 knowledge/）
    """
    _ensure_dirs()
    path = KNOWLEDGE_DIR / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)

    existing_fm: Dict[str, Any] = {}
    existing_body = ""
    if path.exists():
        text = path.read_text(encoding="utf-8")
        existing_fm, existing_body = parse_frontmatter(text)

    if meta:
        existing_fm.update(meta)
    existing_fm["updated"] = _now_utc()

    if append and existing_body:
        body = existing_body + "\n\n" + content.strip()
    else:
        body = content.strip()

    page_text = build_wiki_page(
        title=existing_fm.get("title", path.stem),
        wiki_type=existing_fm.get("type", "concepts"),
        content=body,
        meta=existing_fm,
    )
    path.write_text(page_text, encoding="utf-8")

    # 注入 Obsidian 双向链接并同步图谱
    final_text = _inject_wikilinks(path.read_text(encoding="utf-8"))
    path.write_text(final_text, encoding="utf-8")

    fm, _ = parse_frontmatter(final_text)
    title = fm.get("title", "")
    if title:
        wiki_type = fm.get("type", "concepts")
        growth_stage = fm.get("growth_stage", "growing")
        update_graph_node(title, wiki_type, str(rel_path), growth_stage)
        for related in fm.get("related", []):
            if related:
                add_graph_edge(title, related, "related")

    return str(rel_path)


def delete_wiki_page(rel_path: str) -> bool:
    """删除 wiki 页面，同时清理图谱中的关联。"""
    path = KNOWLEDGE_DIR / rel_path
    if not path.exists():
        return False
    try:
        path.unlink()
        # 清理图谱
        page = get_wiki_page(rel_path)
        title = page["frontmatter"].get("title", "") if page else ""
        if title:
            _remove_graph_node(title)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
# 知识图谱管理
# ─────────────────────────────────────────────

def _load_graph() -> Dict[str, Any]:
    """加载知识图谱。"""
    if not GRAPH_PATH.exists():
        return {"nodes": {}, "edges": []}
    try:
        with open(GRAPH_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 确保结构完整
        if "nodes" not in data or "edges" not in data:
            return {"nodes": {}, "edges": []}
        return data
    except Exception:
        return {"nodes": {}, "edges": []}


def _save_graph(graph: Dict[str, Any]) -> None:
    """保存知识图谱。"""
    with open(GRAPH_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)


def _remove_graph_node(title: str) -> None:
    """从图谱中移除节点及其关联边。"""
    graph = _load_graph()
    if title in graph["nodes"]:
        del graph["nodes"][title]
    graph["edges"] = [e for e in graph["edges"] if e.get("from") != title and e.get("to") != title]
    _save_graph(graph)


def update_graph_node(title: str, wiki_type: str, path: str,
                      growth_stage: str = "seedling") -> None:
    """更新或创建知识图谱节点。"""
    graph = _load_graph()
    graph["nodes"][title] = {
        "type": wiki_type,
        "path": path,
        "growth_stage": growth_stage,
    }
    _save_graph(graph)


def add_graph_edge(from_node: str, to_node: str, relation: str = "related") -> None:
    """添加知识图谱边（去重）。"""
    graph = _load_graph()
    exists = any(
        e.get("from") == from_node and e.get("to") == to_node and e.get("relation") == relation
        for e in graph["edges"]
    )
    if not exists:
        graph["edges"].append({"from": from_node, "to": to_node, "relation": relation})
        _save_graph(graph)


def get_related_concepts(title: str, depth: int = 1) -> List[Dict[str, Any]]:
    """通过知识图谱获取关联概念。

    Args:
        title: 中心概念名
        depth: 遍历深度（1=直接关联，2=间接关联）

    Returns:
        关联概念列表，每项含 title, relation, path, growth_stage
    """
    graph = _load_graph()
    if title not in graph["nodes"]:
        return []

    related = []
    visited = {title}
    queue = [(title, 0)]

    while queue:
        node, d = queue.pop(0)
        if d >= depth:
            continue
        for edge in graph["edges"]:
            if edge["from"] == node:
                neighbor = edge["to"]
            elif edge["to"] == node:
                neighbor = edge["from"]
            else:
                continue
            if neighbor in visited:
                continue
            visited.add(neighbor)
            node_info = graph["nodes"].get(neighbor, {})
            related.append({
                "title": neighbor,
                "relation": edge["relation"],
                "path": node_info.get("path", ""),
                "growth_stage": node_info.get("growth_stage", "unknown"),
                "distance": d + 1,
            })
            queue.append((neighbor, d + 1))

    return related


def get_graph_summary() -> Dict[str, Any]:
    """返回知识图谱概览。"""
    graph = _load_graph()
    stages = {}
    for n in graph["nodes"].values():
        s = n.get("growth_stage", "unknown")
        stages[s] = stages.get(s, 0) + 1
    return {
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "growth_stages": stages,
    }


# ─────────────────────────────────────────────
# 生长日志管理
# ─────────────────────────────────────────────

def _load_growth_log() -> List[Dict[str, Any]]:
    """加载生长日志。"""
    if not GROWTH_LOG_PATH.exists():
        return []
    try:
        with open(GROWTH_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_growth_log(log: List[Dict[str, Any]]) -> None:
    """保存生长日志。"""
    with open(GROWTH_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def log_growth(action: str, target: str, trigger: str, reason: str = "") -> None:
    """记录一次知识生长事件。

    Args:
        action: create | update | link | distill | ingest
        target: 目标文件路径（相对 knowledge/）
        trigger: raw_ingest | conversation | manual | auto
        reason: 人类可读的原因说明
    """
    log = _load_growth_log()
    log.append({
        "timestamp": _now_utc(),
        "action": action,
        "target": target,
        "trigger": trigger,
        "reason": reason,
    })
    _save_growth_log(log)


def get_growth_log(limit: int = 50, target: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取生长日志。

    Args:
        limit: 返回最近 N 条
        target: 只返回特定目标的日志
    """
    log = _load_growth_log()
    if target:
        log = [e for e in log if e.get("target") == target]
    return log[-limit:][::-1]


def get_growth_candidates() -> List[Dict[str, Any]]:
    """获取待生长的概念列表。

    返回 seedling 阶段的 wiki 页面，或知识图谱中缺少 wiki 的节点。
    """
    candidates = []
    for page in list_wiki_pages():
        if page.get("growth_stage") == "seedling":
            candidates.append({
                "title": page["title"],
                "path": page["path"],
                "type": page["type"],
                "reason": "处于 seedling 阶段，需要进一步丰满",
            })
    return candidates


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

    if auto_distill:
        wiki_path = distill_raw_to_wiki(rel_path)
        result["wiki_path"] = wiki_path
        result["message"] += f" | 已提炼为 wiki: {wiki_path}"

    return result


# ─────────────────────────────────────────────
# raw → wiki 提炼（需要 LLM 配合）
# ─────────────────────────────────────────────

def distill_raw_to_wiki(raw_rel_path: str,
                        target_wiki: Optional[str] = None) -> Optional[str]:
    """将 raw 文件提炼为林赛视角的 wiki 页面。

    注意：此函数生成提炼 prompt，实际 LLM 调用由 copilot_engine 完成。
    这里提供的是"提炼指令生成"和"结果保存"的封装。

    Args:
        raw_rel_path: raw 文件相对路径
        target_wiki: 指定输出 wiki 路径（可选）

    Returns:
        生成的 wiki 页面路径，或 None（如果失败）
    """
    raw_path = KNOWLEDGE_DIR / raw_rel_path
    if not raw_path.exists():
        return None

    try:
        raw_text = raw_path.read_text(encoding="utf-8")
    except Exception:
        return None

    # 推断 wiki 类型
    category = raw_path.parent.name
    wiki_type_map = {
        "papers": "papers",
        "notes": "concepts",
        "webclips": "concepts",
    }
    wiki_type = wiki_type_map.get(category, "concepts")

    # 生成建议的文件名
    title_guess = raw_path.stem
    safe_name = _safe_filename(title_guess)
    wiki_filename = f"{safe_name}.md"
    wiki_rel = f"wiki/{wiki_type}/{wiki_filename}"

    if target_wiki:
        wiki_rel = target_wiki

    # 生成提炼 prompt（供 LLM 使用）
    distill_prompt = _build_distill_prompt(raw_text, raw_path.name, wiki_type)

    # 注意：实际 LLM 调用不在此模块中进行
    # 调用方应使用此 prompt 调用 LLM，然后将结果传给 save_distilled_wiki()
    return wiki_rel, distill_prompt


def _build_distill_prompt(raw_text: str, raw_name: str, wiki_type: str) -> str:
    """构建 raw → wiki 的提炼 prompt。"""
    # 截断过长的 raw 文本
    truncated = raw_text[:8000] + ("\n\n... [内容截断，共 {} 字符]".format(len(raw_text)) if len(raw_text) > 8000 else "")

    type_instructions = {
        "concepts": "提炼为一个核心概念页面，包含：定义、物理直觉、数学表达、实验关联、林赛的个人理解。",
        "methods": "提炼为一个实验方法页面，包含：原理、步骤、注意事项、林赛的使用经验。",
        "people": "提炼为一个学者评价页面，包含：贡献概述、与林赛研究方向的关联、林赛的评价。",
        "papers": "提炼为一篇论文精读笔记，包含：核心发现、方法亮点、与林赛工作的关联、批判性思考。",
        "projects": "提炼为一个项目知识聚合页面，包含：目标、方法、进展、关键决策。",
    }

    return f"""请将以下原始材料提炼为林赛（强场超快光学 PI）的研究笔记。

原始材料来源: {raw_name}
笔记类型: {wiki_type}
要求: {type_instructions.get(wiki_type, type_instructions["concepts"])}

请使用以下格式输出（包含 YAML frontmatter）：

【输出格式要求】直接输出 markdown 原文，不要加代码块标记（如 ```markdown），不要添加任何解释性文字。输出必须从 ---（YAML frontmatter）开始。

---
title: "标题"
type: {wiki_type}
created: "{_now_utc()}"
updated: "{_now_utc()}"
tags: ["标签1", "标签2"]
related: ["相关概念1", "相关概念2"]
source_raw: "{raw_name}"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# 标题

## 林赛的理解
（用第一人称写，体现林赛作为强场超快光学 PI 的视角和经验）

## 核心要点

## 实验/研究关联

## 开放问题

## 来源
- 原始材料：{raw_name}
- 蒸馏时间：{_now_utc()}

原始材料内容如下：

{truncated}
"""


def save_distilled_wiki(wiki_rel_path: str, llm_output: str,
                        raw_rel_path: str = "") -> str:
    """保存 LLM 提炼后的 wiki 页面，并更新图谱和日志。

    Args:
        wiki_rel_path: wiki 页面相对路径
        llm_output: LLM 生成的完整 wiki 页面文本（含 frontmatter）
        raw_rel_path: 源 raw 文件路径（用于日志）

    Returns:
        保存的 wiki 路径
    """
    path = KNOWLEDGE_DIR / wiki_rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(llm_output, encoding="utf-8")

    # 注入 Obsidian 双向链接
    final_text = _inject_wikilinks(path.read_text(encoding="utf-8"))
    path.write_text(final_text, encoding="utf-8")

    # 解析 frontmatter 更新图谱
    fm, _ = parse_frontmatter(final_text)
    title = fm.get("title", path.stem)
    wiki_type = fm.get("type", "concepts")
    growth_stage = fm.get("growth_stage", "growing")

    update_graph_node(title, wiki_type, wiki_rel_path, growth_stage)

    # 添加关联边
    for related in fm.get("related", []):
        if related:
            add_graph_edge(title, related, "related")

    # 记录生长日志
    log_growth("distill", wiki_rel_path, "raw_ingest",
               f"从 {raw_rel_path or 'raw'} 提炼生成" if raw_rel_path else "从 raw 提炼生成")

    # 重建索引
    build_index()

    return wiki_rel_path


# ─────────────────────────────────────────────
# 交互触发生长
# ─────────────────────────────────────────────

def check_similar_concepts(concept_name: str, threshold: float = 0.9) -> List[Dict[str, Any]]:
    """检查知识库中是否存在与给定概念高度相似的条目。

    Returns:
        相似概念列表，每项含 title, doc, score, path
    """
    results = search(concept_name, top_k=5)
    similar = []
    for r in results:
        score = r.get("score", 0)
        if score >= threshold:
            similar.append({
                "title": r.get("title", ""),
                "doc": r.get("doc", ""),
                "score": score,
                "source": r.get("source", ""),
                "growth_stage": r.get("growth_stage", ""),
            })
    return similar


def create_wiki_stub(concept_name: str, context: str = "",
                     trigger: str = "conversation") -> str:
    """基于上下文创建 wiki stub（交互触发生长）。

    当对话中遇到知识库中不存在的新概念时，创建 stub，
    标记为 seedling 阶段，后续交互中逐步丰满。

    Args:
        concept_name: 概念名称
        context: 触发创建的上下文（对话片段）
        trigger: 触发来源

    Returns:
        创建的 wiki 路径
    """
    _ensure_dirs()
    safe_name = _safe_filename(concept_name)
    wiki_rel = f"wiki/concepts/{safe_name}.md"

    # 如果已存在，不重复创建
    if (KNOWLEDGE_DIR / wiki_rel).exists():
        return wiki_rel

    stub_content = f"""# {concept_name}

## 林赛的理解

（待补充——这个概念是在对话中首次遇到的，林赛正在学习中。）

## 核心要点

（待补充）

## 触发上下文

> {context[:500] if context else "暂无上下文"}

## 开放问题

- 这个概念与林赛现有的知识体系如何关联？
"""

    meta = {
        "title": concept_name,
        "type": "concepts",
        "tags": [],
        "related": [],
        "source_raw": "",
        "growth_stage": "seedling",
        "confidence": 0.3,
    }

    save_wiki_page(wiki_rel, stub_content, meta)
    update_graph_node(concept_name, "concepts", wiki_rel, "seedling")
    log_growth("create", wiki_rel, trigger,
               f"对话中遇到新概念 '{concept_name}'，创建 seedling stub")

    build_index()
    return wiki_rel


def grow_wiki_prompt(wiki_rel_path: str, new_context: str,
                     reason: str = "") -> Tuple[str, str]:
    """生成 wiki 丰满 prompt，供 LLM 使用。

    Returns:
        (wiki_path, prompt_text)
    """
    page = get_wiki_page(wiki_rel_path)
    if not page:
        return wiki_rel_path, ""

    fm = page["frontmatter"]
    body = page["body"]
    title = fm.get("title", wiki_rel_path)

    prompt = f"""请帮助林赛（强场超快光学 PI）丰满他的研究笔记。

现有笔记：《{title}》
当前生长阶段：{fm.get("growth_stage", "unknown")}
当前确信度：{fm.get("confidence", 0.5)}

现有内容：

---
{body[:4000]}
---

新上下文（来自与用户的对话）：
{new_context[:3000]}

{reason}

请基于新上下文，补充或修正现有笔记。要求：
1. 保持第一人称"林赛"的视角
2. 添加"林赛的理解"、"实验经验"或"批判性思考"部分
3. 更新 related 字段，添加关联概念
4. 如果内容足够充实，将 growth_stage 提升为 "growing" 或 "mature"
5. 适当提升 confidence

请输出完整的 wiki 页面（含 frontmatter），可以直接覆盖原有内容。
"""
    return wiki_rel_path, prompt


def apply_growth(wiki_rel_path: str, llm_output: str,
                 trigger: str = "conversation") -> str:
    """应用 LLM 生成的丰满内容，更新 wiki 页面。

    Args:
        wiki_rel_path: wiki 页面路径
        llm_output: LLM 生成的完整 wiki 页面
        trigger: 触发来源

    Returns:
        更新后的 wiki 路径
    """
    path = KNOWLEDGE_DIR / wiki_rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(llm_output, encoding="utf-8")

    # 注入 Obsidian 双向链接
    final_text = _inject_wikilinks(path.read_text(encoding="utf-8"))
    path.write_text(final_text, encoding="utf-8")

    fm, _ = parse_frontmatter(final_text)
    title = fm.get("title", path.stem)
    wiki_type = fm.get("type", "concepts")
    growth_stage = fm.get("growth_stage", "growing")

    update_graph_node(title, wiki_type, wiki_rel_path, growth_stage)

    for related in fm.get("related", []):
        if related:
            add_graph_edge(title, related, "related")

    log_growth("update", wiki_rel_path, trigger,
               f"基于对话上下文丰满 '{title}'，阶段更新为 {growth_stage}")

    build_index()
    return wiki_rel_path


# ─────────────────────────────────────────────
# 索引系统（增强版：同时索引 raw + wiki）
# ─────────────────────────────────────────────

def _compute_idf(doc_count: int, term_doc_freq: Dict[str, int]) -> Dict[str, float]:
    idf = {}
    for term, freq in term_doc_freq.items():
        idf[term] = math.log(doc_count / (freq + 1)) + 1
    return idf


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

        # 对于 wiki 页面，解析 frontmatter 获取额外元数据
        title = file_path.stem
        tags: List[str] = []
        growth_stage = ""
        if source == "wiki":
            try:
                fm, body = parse_frontmatter(text)
                title = fm.get("title", title)
                tags = fm.get("tags", [])
                growth_stage = fm.get("growth_stage", "")
                # 索引时包含 frontmatter 中的标签
                text = body + " " + " ".join(tags)
                if growth_stage:
                    text += " " + growth_stage
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

    return index_data


def search(query: str, top_k: int = 3, source: str = "all") -> List[Dict[str, Any]]:
    """根据查询检索相关知识段落（增强版）。

    Args:
        query: 用户输入的查询文本
        top_k: 返回最相关的 K 个段落
        source: "all" | "raw" | "wiki" — 只返回指定来源的结果

    Returns:
        段落列表，每项含 text, doc, score, source, title, growth_stage
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


def get_kb_health() -> Dict[str, Any]:
    """返回知识库健康度数据，供仪表盘使用。"""
    status = get_index_status()
    graph = get_graph_summary()
    candidates = get_growth_candidates()

    # 统计 capture 文件
    capture_dir = KNOWLEDGE_DIR / "captures"
    capture_count = len(list(capture_dir.glob("*.md"))) if capture_dir.exists() else 0

    # 统计本周新增（基于 growth-log）
    log = get_growth_log(limit=200)
    week_count = 0
    try:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        for entry in log:
            ts = entry.get("timestamp", "")
            if ts:
                try:
                    et = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if et >= week_ago:
                        week_count += 1
                except Exception:
                    pass
    except Exception:
        pass

    # 待蒸馏 raw：已索引但未关联 wiki 的 raw 文件
    raw_files = list_raw_files()
    wiki_from_raw = set()
    for page in list_wiki_pages():
        fm = get_wiki_page(page.get("path", ""))
        if fm:
            src = fm.get("frontmatter", {}).get("source_raw", "")
            if src:
                wiki_from_raw.add(src)
    pending_distill = len([f for f in raw_files if f["name"] not in wiki_from_raw])

    return {
        "indexed": status.get("indexed", False),
        "raw_count": status.get("raw_count", 0),
        "wiki_count": status.get("wiki_count", 0),
        "capture_count": capture_count,
        "chunks": status.get("chunks", 0),
        "growth_stages": graph.get("growth_stages", {}),
        "graph_nodes": graph.get("node_count", 0),
        "graph_edges": graph.get("edge_count", 0),
        "graph_orphans": _count_graph_orphans(),
        "week_new": week_count,
        "pending_distill": pending_distill,
        "growth_candidates": len(candidates),
        "built_at": status.get("built_at", ""),
    }


def _count_graph_orphans() -> int:
    """统计知识图谱中无对应 wiki 文件的孤儿节点。"""
    graph = _load_graph()
    orphans = 0
    for title, node in graph.get("nodes", {}).items():
        path = node.get("path", "")
        if path and not (KNOWLEDGE_DIR / path).exists():
            orphans += 1
    return orphans


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
    return {"success": True, "path": str(target.relative_to(KNOWLEDGE_DIR))}


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("◐ 林赛知识库引擎自检")
    _ensure_dirs()

    # 1. 检查目录结构
    print(f"  raw/ 目录: {'✓' if RAW_DIR.exists() else '✗'}")
    print(f"  wiki/ 目录: {'✓' if WIKI_DIR.exists() else '✗'}")

    # 2. 重建索引
    idx = build_index(force=True)
    docs = idx.get("documents", {})
    raw_count = sum(1 for d in docs.values() if d.get("source") == "raw")
    wiki_count = sum(1 for d in docs.values() if d.get("source") == "wiki")
    print(f"  索引文档: raw={raw_count}, wiki={wiki_count}")
    print(f"  索引词项: {len(idx['inverted'])}")
    print(f"  图谱节点: {idx.get('graph_summary', {}).get('node_count', 0)}")

    # 3. 搜索测试
    results = search("固体 HHG", top_k=3, source="all")
    print(f"  搜索 '固体 HHG': 命中 {len(results)} 条")
    for r in results:
        src_icon = "📚" if r["source"] == "raw" else "📝"
        print(f"    {src_icon} [{r['title']}] ({r['source']}) score={r['score']:.3f}")

    # 4. Wiki 管理测试
    test_wiki = "wiki/concepts/测试概念.md"
    save_wiki_page(test_wiki, "# 测试概念\n\n这是测试内容。", {
        "title": "测试概念",
        "type": "concepts",
        "tags": ["测试"],
        "related": ["固体HHG"],
        "growth_stage": "seedling",
    })
    page = get_wiki_page(test_wiki)
    print(f"  Wiki 创建: {'✓' if page else '✗'}")
    if page:
        print(f"    title={page['frontmatter'].get('title')}")
        print(f"    stage={page['frontmatter'].get('growth_stage')}")

    # 5. 图谱测试
    graph = get_graph_summary()
    print(f"  图谱: 节点={graph['node_count']} 边={graph['edge_count']}")

    # 6. 生长日志测试
    log = get_growth_log(limit=5)
    print(f"  生长日志: {len(log)} 条记录")

    # 清理测试数据
    delete_wiki_page(test_wiki)
    build_index(force=True)

    print("✓ 自检通过")
