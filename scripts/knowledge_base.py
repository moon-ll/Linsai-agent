#!/usr/bin/env python3
"""林赛知识库引擎 —— raw/wiki 分层 + 知识图谱 + 生长机制（门面模式）。

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

自 v3.5.5 起，本文件按职责拆分为 5 个子模块（物理迁移，函数逻辑不变）：
    - kb_text.py   文本处理基础工具（分词/分块/IDF/frontmatter/安全文件名）
    - kb_graph.py  知识图谱管理（节点/边/关联概念/WikiLink 注入）
    - kb_wiki.py   Wiki 页面管理（构建/读取/保存/删除/交互生长）
    - kb_index.py  索引与检索（倒排索引/TF-IDF 检索/raw 管理/增强上下文）
    - kb_health.py 健康度与维护（连通性/覆盖率/命中率/孤儿节点）

本文件保留为门面（Facade），职责：
    1. re-export 所有子模块的公开与私有函数（含 _load_graph / _save_graph /
       _inject_wikilinks / _build_distill_prompt / _expand_query_with_aliases 等），
       确保 `import knowledge_base as kb` 的外部模块无需任何改动。
    2. 保留别名管理、raw 蒸馏编排、生长日志、目录初始化等跨职责函数。
    3. 在加载完成后向子模块注入门面侧函数（_ensure_dirs / log_growth /
       _load_aliases / distill_raw_to_wiki / get_wiki_page / get_growth_candidates /
       get_growth_log / _log），解决子模块→门面依赖（子模块不反向 import 门面，
       兼容 spec_from_file_location 动态加载场景）。

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
import re
import sys as _sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# 确保子模块可被导入（兼容 spec_from_file_location 动态加载场景）
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in _sys.path:
    _sys.path.insert(0, str(_SCRIPTS_DIR))

from common import now_utc as _now_utc
import common as _cms

# 日志接入（可选，logger 模块不存在时降级为静默）
try:
    from logger import get_logger
    _log = get_logger("knowledge_base")
except Exception:
    _log = None

from paths import (
    PROJECT_ROOT, KNOWLEDGE_DIR, RAW_DIR, WIKI_DIR,
    INDEX_PATH, GRAPH_PATH, GROWTH_LOG_PATH, ALIASES_PATH,
)

# ─────────────────────────────────────────────
# 子模块 re-export（公开 + 私有函数 + 常量）
# ─────────────────────────────────────────────

from kb_text import (
    parse_frontmatter, build_frontmatter,
    _tokenize, _chunk_document, _compute_idf, _safe_filename,
    _STOPWORDS, _FRONTMATTER_RE,
)
from kb_graph import (
    _load_graph, _save_graph, _remove_graph_node,
    update_graph_node, add_graph_edge,
    get_related_concepts, get_graph_summary,
    _extract_wikilinks, _get_aliases_for_concept, _inject_wikilinks,
    _WIKILINK_RE, _WIKILINKS_SECTION_RE,
)
from kb_wiki import (
    build_wiki_page, get_wiki_page, list_wiki_pages,
    save_wiki_page, delete_wiki_page,
    check_similar_concepts, create_wiki_stub,
    grow_wiki_prompt, apply_growth,
    _WIKI_TYPES,
)
from kb_index import (
    build_index, search, search_light,
    get_index_status, get_enriched_context, add_document,
    _should_index, list_raw_files, ingest_raw,
    _SUPPORTED_EXTS,
)
from kb_health import (
    get_kb_health,
    _compute_graph_connectivity, _compute_category_coverage,
    _compute_alias_hit_rate, _count_graph_orphans,
)

# 引入子模块对象，用于注入门面侧函数
import kb_wiki as _kb_wiki_mod
import kb_index as _kb_index_mod
import kb_health as _kb_health_mod


# ─────────────────────────────────────────────
# 目录初始化（门面保留）
# ─────────────────────────────────────────────

def _ensure_dirs() -> None:
    """确保知识库目录结构存在。"""
    for d in [RAW_DIR / "papers", RAW_DIR / "notes", RAW_DIR / "webclips"]:
        d.mkdir(parents=True, exist_ok=True)
    for t in _WIKI_TYPES:
        (WIKI_DIR / t).mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
# 别名管理（门面保留：被 context_builder 直接调用）
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


# ─────────────────────────────────────────────
# 生长日志管理（门面保留）
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
    _cms.save_json(GROWTH_LOG_PATH, log)


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
# raw → wiki 提炼（门面保留：LLM prompt 编排，跨职责）
# ─────────────────────────────────────────────

def distill_raw_to_wiki(raw_rel_path: str,
                        target_wiki: Optional[str] = None) -> Optional[Tuple[str, str]]:
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
    if _log:
        _log.info(f"raw → wiki 蒸馏指令已生成: {raw_rel_path} → {wiki_rel}")
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
# 向子模块注入门面侧函数（解决子模块→门面依赖）
# ─────────────────────────────────────────────
# 子模块不反向 import 门面（兼容 spec_from_file_location 动态加载场景），
# 改由门面在加载完成后注入以下函数到子模块全局命名空间。
# 函数体保持与原 knowledge_base.py 完全一致（通过模块全局名查找注入对象）。

_kb_wiki_mod._ensure_dirs = _ensure_dirs
_kb_wiki_mod.log_growth = log_growth
_kb_wiki_mod._log = _log

_kb_index_mod._ensure_dirs = _ensure_dirs
_kb_index_mod.log_growth = log_growth
_kb_index_mod.distill_raw_to_wiki = distill_raw_to_wiki
_kb_index_mod._load_aliases = _load_aliases
_kb_index_mod.get_wiki_page = get_wiki_page
_kb_index_mod._log = _log

_kb_health_mod.get_growth_candidates = get_growth_candidates
_kb_health_mod.get_growth_log = get_growth_log


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
