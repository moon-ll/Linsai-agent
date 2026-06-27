#!/usr/bin/env python3
"""课题上下文注入引擎 — @课题知识库语法解析 + 课题上下文构建。

本模块负责两件事：
1. 解析用户输入中的 @课题知识库 语法，从指定课题的知识库检索信息
2. 为当前课题的对话构建课题上下文（长期记忆 + 当前单元 + 知识库摘要）

@ 语法设计：
    @PRJ-20260627-固体HHG 相位匹配条件   # 在指定课题知识库中搜索"相位匹配条件"
    @课题知识库 Lewenstein模型            # 在当前课题知识库中搜索（简写）
    @课题成果 Unit1报告                   # 搜索指定课题的 summary 层（单元报告）

用法:
    >>> from project_context import parse_at_references, build_project_context
    >>> refs = parse_at_references("@PRJ-固体HHG 相位匹配条件")
    >>> ctx = build_project_context("PRJ-20260627-固体HHG")

规范:
    - 仅使用 Python 3 标准库
    - 路径使用 pathlib.Path，PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - JSON 输出 ensure_ascii=False, indent=2
    - 时间戳使用 UTC ISO 格式
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from project_manager import get_project, list_projects
from project_memory import get_project_context as _get_memory_context
from project_kb import search as _kb_search, get_kb_stats


# @ 语法正则
# @PRJ-xxx query 或 @课题知识库 query 或 @课题成果 query
_AT_PATTERN = re.compile(
    r"@(?:"
    r"(?P<project_id>PRJ-[^\s]+)\s+(?P<query1>[^\n@]+)"
    r"|课题知识库\s+(?P<query2>[^\n@]+)"
    r"|课题成果\s+(?P<query3>[^\n@]+)"
    r")"
)


def parse_at_references(text: str) -> List[dict]:
    """解析用户输入中的 @课题知识库 引用。

    支持三种形式：
        @PRJ-xxx query           → 在指定课题知识库搜索
        @课题知识库 query          → 在当前课题知识库搜索（简写）
        @课题成果 query            → 搜索指定课题的 summary 层（单元报告）

    Returns:
        [{type, project_id, query, raw}]
        type:
          - "project_kb": @PRJ-xxx query 或 @课题知识库 query
          - "project_results": @课题成果 query（搜索 summary 层）
        project_id 为空字符串表示当前课题（需调用方用 current_project_id 填充）。
    """
    results: List[dict] = []
    for m in _AT_PATTERN.finditer(text):
        if m.group("project_id"):
            results.append({
                "type": "project_kb",
                "project_id": m.group("project_id"),
                "query": m.group("query1").strip(),
                "raw": m.group(0),
            })
        elif m.group("query2"):
            results.append({
                "type": "project_kb",
                "project_id": "",  # 当前课题
                "query": m.group("query2").strip(),
                "raw": m.group(0),
            })
        elif m.group("query3"):
            results.append({
                "type": "project_results",
                "project_id": "",  # 当前课题
                "query": m.group("query3").strip(),
                "raw": m.group(0),
            })
    return results


def resolve_at_references(text: str, current_project_id: str = "") -> Tuple[str, List[dict]]:
    """解析 @ 引用并检索知识库，返回 (enriched_text, references)。

    Args:
        text: 用户原始输入文本
        current_project_id: 当前课题 ID（用于填充 @课题知识库 / @课题成果 的简写形式）

    Returns:
        enriched_text: 原始文本（@ 引用保留原样，检索结果通过 references 单独返回）
        references: [{project_id, query, type, results: [{title, path, layer, score, snippet}]}]
    """
    refs = parse_at_references(text)
    if not refs:
        return text, []

    references: List[dict] = []
    for ref in refs:
        pid = ref["project_id"] or current_project_id
        if not pid:
            continue

        # 验证课题存在
        try:
            get_project(pid)
        except Exception:
            continue

        query = ref["query"]
        layer = "summary" if ref["type"] == "project_results" else "all"

        try:
            results = _kb_search(pid, query, layer=layer, top_k=3)
        except Exception:
            results = []

        references.append({
            "project_id": pid,
            "query": query,
            "type": ref["type"],
            "results": results,
        })

    return text, references


def build_project_context(project_id: str, include_kb: bool = True) -> str:
    """构建课题上下文（用于注入到 system_prompt）。

    包含：
        1. 课题基本信息（名称、目标、阶段）
        2. 课题长期记忆（PROJECT-MEMORY.md + 近期记忆片段 + 当前单元，由 get_project_context 提供）
        3. 知识库统计摘要（如果 include_kb=True）
        4. 当前单元信息（由 get_project_context 提供）

    Args:
        project_id: 课题 ID
        include_kb: 是否包含知识库统计摘要

    Returns:
        格式化文本，不超过 3000 字符。课题不存在时返回空字符串。
    """
    parts: List[str] = []

    # 1. 课题基本信息
    try:
        project = get_project(project_id)
        parts.append("[课题上下文]")
        parts.append(f"课题: {project.get('name', '')}")
        parts.append(f"目标: {project.get('goal', '')}")
        parts.append(f"阶段: {project.get('phase', 'init')}")
    except Exception:
        return ""

    # 2. 课题长期记忆（含近期记忆片段 + 当前单元，由 get_project_context 封装）
    try:
        mem_ctx = _get_memory_context(project_id)
        if mem_ctx:
            parts.append(f"\n{mem_ctx}")
    except Exception:
        pass

    # 3. 知识库统计
    if include_kb:
        try:
            stats = get_kb_stats(project_id)
            parts.append("\n[知识库概览]")
            parts.append(f"总文档: {stats.get('total', 0)}")
            by_layer = stats.get("by_layer", {})
            for layer in ("raw", "parsed", "summary"):
                count = by_layer.get(layer, 0)
                if count > 0:
                    parts.append(f"  {layer}: {count} 篇")
            by_tag = stats.get("by_tag", {})
            # by_tag 的值是文档计数（int），按计数倒序取前 5
            top_tags = sorted(by_tag.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_tags:
                tags_str = ", ".join(f"{tag}({count})" for tag, count in top_tags)
                parts.append(f"  热门标签: {tags_str}")
        except Exception:
            pass

    result = "\n".join(parts)
    # 截断到 3000 字符
    if len(result) > 3000:
        result = result[:2997] + "..."
    return result


def search_across_projects(query: str, top_k: int = 5) -> List[dict]:
    """跨所有课题的知识库搜索（用于全局检索）。

    遍历所有课题，在每个课题知识库中检索，合并结果按分数排序。

    Args:
        query: 查询文本
        top_k: 返回最相关的 K 条

    Returns:
        [{project_id, project_name, title, path, layer, score, snippet}]
    """
    results: List[dict] = []
    for proj in list_projects():
        pid = proj.get("project_id", "")
        if not pid:
            continue
        try:
            hits = _kb_search(pid, query, layer="all", top_k=2)
            for hit in hits:
                results.append({
                    "project_id": pid,
                    "project_name": proj.get("name", ""),
                    "title": hit.get("title", ""),
                    "path": hit.get("path", ""),
                    "layer": hit.get("layer", ""),
                    "score": hit.get("score", 0),
                    "snippet": hit.get("snippet", ""),
                })
        except Exception:
            continue

    # 按分数排序，取 top_k
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:top_k]


def _self_check() -> None:
    """自检。"""
    print("=" * 50)
    print("◐ project_context 自检")
    print("=" * 50)

    # 1. @ 语法解析
    print("\n[1/4] @ 语法解析...")
    tests = [
        ("@PRJ-20260627-测试 查相位匹配", "project_kb", "PRJ-20260627-测试", "查相位匹配"),
        ("@课题知识库 Lewenstein模型", "project_kb", "", "Lewenstein模型"),
        ("@课题成果 Unit1报告", "project_results", "", "Unit1报告"),
        ("普通消息没有@引用", None, None, None),
    ]
    all_ok = True
    for text, exp_type, exp_pid, exp_query in tests:
        refs = parse_at_references(text)
        if exp_type is None:
            ok = len(refs) == 0
        else:
            ok = (
                len(refs) == 1
                and refs[0]["type"] == exp_type
                and refs[0]["query"] == exp_query
            )
        print(f"  {'✓' if ok else '✗'} \"{text[:30]}\"")
        if not ok:
            all_ok = False

    # 2. 上下文构建（需要课题存在）
    print("\n[2/4] 上下文构建（无课题时）...")
    ctx = build_project_context("PRJ-NONEXISTENT")
    ok = ctx == ""
    print(f"  {'✓' if ok else '✗'} 空上下文: {ctx!r}" if not ok else f"  ✓ 空上下文")
    if not ok:
        all_ok = False

    # 3. 创建测试课题并构建上下文
    print("\n[3/4] 上下文构建（有课题时）...")
    from project_manager import create_project, delete_project
    from project_kb import add_document
    from project_memory import create_snippet, add_decision

    pid, _ = create_project("自检测试课题", goal="验证上下文注入")
    add_document(
        pid, "raw", "references", "测试文献",
        "这是关于相位匹配的文献内容", tags=["HHG", "相位匹配"],
    )
    add_document(
        pid, "parsed", "concepts", "相位匹配概念",
        "相位匹配是HHG的关键问题", tags=["相位匹配"],
    )
    create_snippet(pid, "相位敏感性", "HHG对驱动相位高度敏感", source="测试")
    add_decision(pid, "选择Lewenstein模型", "因更直观且适用于气体", "半导体布洛赫方程")

    ctx = build_project_context(pid)
    print(f"  上下文长度: {len(ctx)} 字符")
    ok_name = "自检测试课题" in ctx
    ok_kb = "知识库" in ctx
    print(f"  {'✓' if ok_name else '✗'} 含课题名")
    print(f"  {'✓' if ok_kb else '✗'} 含知识库")
    if not (ok_name and ok_kb):
        all_ok = False

    # 4. @ 引用检索
    print("\n[4/4] @ 引用检索...")
    text = f"@{pid} 相位匹配"
    enriched, refs = resolve_at_references(text, pid)
    ok_refs = len(refs) == 1
    print(f"  {'✓' if ok_refs else '✗'} 检索结果数: {len(refs)}")
    if refs:
        hit_count = len(refs[0].get("results", []))
        ok_hits = hit_count > 0
        print(f"  {'✓' if ok_hits else '✗'} 命中数: {hit_count}")
        if not ok_hits:
            all_ok = False
    else:
        all_ok = False

    # 清理
    delete_project(pid, confirm=True)

    print()
    if all_ok:
        print("✓ project_context 自检完成（全部通过）")
    else:
        print("⚠ project_context 自检完成（存在失败项）")


if __name__ == "__main__":
    _self_check()
