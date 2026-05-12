#!/usr/bin/env python3
"""
learning_engine.py — 自主学习核心编排器

用途：
    将外部信息（arXiv 论文、Wikipedia 词条、本地 raw 文件）蒸馏为林赛视角的 wiki 知识，
    自动提取概念、更新知识图谱，实现知识库的自我生长。

用法示例：
    >>> from learning_engine import run_learning_cycle
    >>> result = run_learning_cycle(query="attosecond", sources=["arxiv"])
    >>> print(result["created"], result["updated"], result["concepts"])
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
WIKI_PAPERS_DIR = KNOWLEDGE_DIR / "wiki" / "papers"
MEMORY_DIR = PROJECT_ROOT / "memory"
COST_PATH = MEMORY_DIR / "learning-cost.json"

# 动态导入 knowledge_base
_kb = None

def _import_kb():
    global _kb
    if _kb is not None:
        return _kb
    try:
        import importlib.util
        kb_path = Path(__file__).parent / "knowledge_base.py"
        spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
        _kb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_kb)
        return _kb
    except Exception as e:
        print(f"✗ 无法导入 knowledge_base: {e}")
        raise


# 动态导入 llm_router
_router = None

def _import_router():
    global _router
    if _router is not None:
        return _router
    try:
        import importlib.util
        lr_path = Path(__file__).parent / "llm_router.py"
        spec = importlib.util.spec_from_file_location("llm_router", lr_path)
        lr_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lr_mod)
        _router = lr_mod.router
        return _router
    except Exception as e:
        print(f"✗ 无法导入 llm_router: {e}")
        raise


# 动态导入 external_fetcher
_ef = None

def _import_ef():
    global _ef
    if _ef is not None:
        return _ef
    try:
        import importlib.util
        ef_path = Path(__file__).parent / "external_fetcher.py"
        spec = importlib.util.spec_from_file_location("external_fetcher", ef_path)
        _ef = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_ef)
        return _ef
    except Exception as e:
        print(f"✗ 无法导入 external_fetcher: {e}")
        raise


# 动态导入 research_profiler
_rp = None

def _import_rp():
    global _rp
    if _rp is not None:
        return _rp
    try:
        import importlib.util
        rp_path = Path(__file__).parent / "research_profiler.py"
        spec = importlib.util.spec_from_file_location("research_profiler", rp_path)
        _rp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_rp)
        return _rp
    except Exception as e:
        print(f"✗ 无法导入 research_profiler: {e}")
        raise


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any = None) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default if default is not None else {}


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _safe_filename(name: str) -> str:
    """生成安全的文件名。"""
    safe = re.sub(r"[^\w\u4e00-\u9fff\-]", "_", name)
    safe = safe.strip("_")
    return safe if safe else "untitled"


# ---------------------------------------------------------------------------
# LLM 调用封装（成本追踪）
# ---------------------------------------------------------------------------

def _call_llm_for_learning(system_prompt: str, messages: list,
                            cost_tracker: Optional[Dict[str, Any]] = None) -> str:
    """学习专用 LLM 调用，自动降级 + 成本追踪。

    Args:
        system_prompt: 系统提示词
        messages: 消息列表
        cost_tracker: 成本追踪字典（可选，会被修改）

    Returns:
        LLM 生成的文本

    Raises:
        RuntimeError: 所有 Provider 均失败
    """
    router = _import_router()
    result, usage, provider = router.call_llm(system_prompt, messages)

    if cost_tracker is not None:
        cost_tracker["calls"] = cost_tracker.get("calls", 0) + 1
        cost_tracker["providers_used"] = cost_tracker.get("providers_used", []) + [provider]
        # token 估算：API 返回 usage，CLI 用字符数估算
        tokens = 0
        if isinstance(usage, dict):
            tokens = usage.get("total_tokens", usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0))
        if tokens == 0:
            # CLI 估算：输入 + 输出字符数 / 4
            text_len = len(system_prompt) + sum(len(m.get("content", "")) for m in messages) + len(result)
            tokens = text_len // 4
        cost_tracker["tokens"] = cost_tracker.get("tokens", 0) + tokens

    return result


def _record_cost(cost_tracker: Dict[str, Any], source_type: str) -> None:
    """记录学习成本到 learning-cost.json。"""
    if not cost_tracker:
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    month = today[:7]

    cost_data = _load_json(COST_PATH, {"daily": {}, "monthly": {}, "by_provider": {}, "by_source": {}, "total_calls": 0, "total_tokens": 0})

    # 估算成本（USD）—— 简化：MiniMax ~ $0.0015/1K tokens，kimi CLI ~ $0.001/1K，claude ~ $0.003/1K
    tokens = cost_tracker.get("tokens", 0)
    avg_rate = 0.002  # $/1K tokens 平均
    estimated_cost = tokens * avg_rate / 1000

    cost_data["daily"][today] = cost_data["daily"].get(today, 0) + estimated_cost
    cost_data["monthly"][month] = cost_data["monthly"].get(month, 0) + estimated_cost
    cost_data["total_calls"] = cost_data.get("total_calls", 0) + cost_tracker.get("calls", 0)
    cost_data["total_tokens"] = cost_data.get("total_tokens", 0) + tokens

    for provider in cost_tracker.get("providers_used", []):
        cost_data["by_provider"][provider] = cost_data["by_provider"].get(provider, 0) + estimated_cost
    cost_data["by_source"][source_type] = cost_data["by_source"].get(source_type, 0) + estimated_cost

    _save_json(COST_PATH, cost_data)


# ---------------------------------------------------------------------------
# Prompt 构建
# ---------------------------------------------------------------------------

def _build_arxiv_distill_prompt(paper_data: Dict[str, Any]) -> str:
    """构建 arXiv 论文精读 prompt。"""
    title = paper_data.get("title", "")
    abstract = paper_data.get("abstract", "")
    tldr = paper_data.get("tldr", "")
    authors = ", ".join(paper_data.get("authors", [])[:5])
    date = paper_data.get("date", "")
    arxiv_id = paper_data.get("arxiv_id", "")
    pdf_url = paper_data.get("url", f"https://arxiv.org/pdf/{arxiv_id}")

    return f"""你是一位强场超快光学独立 PI（林赛），正在阅读一篇最新的 arXiv 论文。

请基于以下论文信息，撰写一篇林赛视角的精读笔记。

【输出格式要求】直接输出 markdown 原文，不要加代码块标记（如 ```markdown），不要添加任何解释性文字。输出必须从 ---（YAML frontmatter）开始，到 ## 来源 章节结束。

论文信息：
- 标题：{title}
- 作者：{authors}
- arXiv ID：{arxiv_id}
- 发表日期：{date}
- 摘要：{abstract[:2000]}
- TLDR：{tldr[:1000]}
- PDF 链接：{pdf_url}

请输出完整的 wiki 页面，包含 YAML frontmatter 和以下章节。

重要：必须在正文末尾添加「## 来源」章节，包含原始论文的 arXiv 链接，方便人工校验。

---
title: "{title}"
type: papers
created: "{_now_utc()}"
updated: "{_now_utc()}"
tags: ["文献", "auto-grown"]
related: []
source_arxiv: "{arxiv_id}"
authors: "{authors}"
published: "{date}"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
review_status: "pending"
---

# {title}

## 林赛的理解
（用第一人称，体现你作为强场超快光学 PI 的视角。这篇论文和你的研究有什么关联？）

## 核心发现
（论文最重要的 2-3 个发现）

## 方法亮点
（实验或理论方法上的创新点）

## 与林赛工作的关联
（这篇论文如何启发或补充你的研究？）

## 批判性思考
（论文的局限性、你怀疑的地方、想进一步验证的问题）

## 实验参数备忘
（如果有具体参数，记录下来）

## 开放问题
（这篇论文引出的你感兴趣的问题）

## 来源
- arXiv 原文：[{arxiv_id}]({pdf_url})
- 检索时间：{_now_utc()}
"""


def _build_web_search_distill_prompt(web_data: Dict[str, Any]) -> str:
    """构建联网检索结果蒸馏 prompt。"""
    title = web_data.get("title", "")
    snippet = web_data.get("snippet", "")
    url = web_data.get("url", "")

    return f"""你是一位强场超快光学独立 PI（林赛），正在通过联网检索学习一个新的概念/信息。

【输出格式要求】直接输出 markdown 原文，不要加代码块标记（如 ```markdown），不要添加任何解释性文字。输出必须从 ---（YAML frontmatter）开始，到 ## 来源 章节结束。

检索结果：
- 标题：{title}
- 摘要/片段：{snippet[:2000]}
- 来源 URL：{url}

请输出完整的 wiki 页面，包含 YAML frontmatter 和以下章节。

重要：必须在正文末尾添加「## 来源」章节，包含原始来源的 Markdown 链接，方便人工校验。

---
title: "{title}"
type: concepts
created: "{_now_utc()}"
updated: "{_now_utc()}"
tags: ["网络检索", "auto-grown"]
related: []
source_url: "{url}"
growth_stage: "growing"
confidence: 0.6
auto_grown: true
review_status: "pending"
---

# {title}

## 林赛的理解
（用第一人称，从强场超快光学 PI 的角度理解这个信息。它是什么？为什么重要？）

## 核心要点
（提炼检索结果中的关键信息）

## 物理直觉
（用直觉性的语言解释，避免纯公式堆砌）

## 与林赛研究的关联
（这个信息如何与你的研究方向——阿秒科学、固体高次谐波、拍赫兹电子学——产生联系？）

## 开放问题
（你还想深入了解什么？）

## 来源
- 原始检索结果：[{title}]({url})
- 检索时间：{_now_utc()}
"""


# ---------------------------------------------------------------------------
# 统一蒸馏接口
# ---------------------------------------------------------------------------

def distill_content(source_type: str, source_data: Dict[str, Any],
                    cost_tracker: Optional[Dict[str, Any]] = None) -> Tuple[str, List[str], Dict[str, Any]]:
    """统一蒸馏接口：将任何来源的内容蒸馏为 wiki markdown。

    Args:
        source_type: "arxiv_paper" / "wikipedia" / "raw_note" / "raw_webclip"
        source_data: 原始数据字典
        cost_tracker: 成本追踪字典

    Returns:
        (wiki_markdown, extracted_concepts, quality_hints)
    """
    system_prompt = (
        "你是一位强场超快光学独立 PI（林赛），擅长将外部信息转化为你自己的研究笔记。"
        "严格按照用户提供的模板格式输出。只输出纯 markdown 文本，"
        "不要加代码块包裹（如 ```markdown），不要加任何解释性文字。"
    )
    messages = [{"role": "user", "content": ""}]

    if source_type == "arxiv_paper":
        messages[0]["content"] = _build_arxiv_distill_prompt(source_data)
    elif source_type == "web_search":
        messages[0]["content"] = _build_web_search_distill_prompt(source_data)
    elif source_type in ("raw_note", "raw_webclip"):
        # 复用 knowledge_base 的 distill prompt
        kb = _import_kb()
        raw_text = source_data.get("content", "")
        raw_name = source_data.get("name", "raw")
        wiki_type = "concepts" if source_type == "raw_webclip" else "concepts"
        messages[0]["content"] = kb._build_distill_prompt(raw_text, raw_name, wiki_type)
    else:
        raise ValueError(f"不支持的 source_type: {source_type}")

    wiki_text = _call_llm_for_learning(system_prompt, messages, cost_tracker)
    wiki_text = _extract_wiki_content(wiki_text)
    concepts = _extract_concepts_from_wiki(wiki_text)
    hints = {"source_type": source_type, "source_title": source_data.get("title", "")}

    return wiki_text, concepts, hints


# ---------------------------------------------------------------------------
# 论文精读引擎
# ---------------------------------------------------------------------------

def distill_arxiv_paper(paper_data: Dict[str, Any],
                        cost_tracker: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """将 arXiv 论文蒸馏为 wiki/papers/ 页面。

    Returns:
        生成的 wiki 页面路径，或 None（如果失败）
    """
    arxiv_id = paper_data.get("arxiv_id", "")
    if not arxiv_id:
        return None

    # 检查是否已存在
    kb = _import_kb()
    safe_id = _safe_filename(arxiv_id)
    wiki_rel = f"wiki/papers/{safe_id}.md"
    if (KNOWLEDGE_DIR / wiki_rel).exists():
        print(f"⚠ wiki/papers/{safe_id}.md 已存在，跳过")
        return wiki_rel

    wiki_text, concepts, hints = distill_content("arxiv_paper", paper_data, cost_tracker)

    # 保存 wiki
    kb.save_distilled_wiki(wiki_rel, wiki_text, raw_rel_path=f"arxiv:{arxiv_id}")

    # 提取概念并整合
    for concept in concepts:
        _integrate_concept(concept, wiki_text, source="arxiv_paper")

    print(f"✓ 论文精读已保存: {wiki_rel}")
    return wiki_rel


# ---------------------------------------------------------------------------
# Wikipedia 词条蒸馏
# ---------------------------------------------------------------------------

def distill_web_search(web_data: Dict[str, Any],
                        cost_tracker: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """将联网检索结果蒸馏为 wiki/concepts/ 页面。

    Returns:
        生成的 wiki 页面路径，或 None（如果失败）
    """
    title = web_data.get("title", "")
    if not title:
        return None

    kb = _import_kb()
    safe_name = _safe_filename(title)
    wiki_rel = f"wiki/concepts/{safe_name}.md"
    if (KNOWLEDGE_DIR / wiki_rel).exists():
        print(f"⚠ wiki/concepts/{safe_name}.md 已存在，跳过")
        return wiki_rel

    wiki_text, concepts, hints = distill_content("web_search", web_data, cost_tracker)

    source_url = web_data.get("url", "")
    kb.save_distilled_wiki(wiki_rel, wiki_text, raw_rel_path=f"web:{source_url}")

    for concept in concepts:
        _integrate_concept(concept, wiki_text, source="web_search")

    print(f"✓ 网络检索蒸馏已保存: {wiki_rel}")
    return wiki_rel


# ---------------------------------------------------------------------------
# raw 自动蒸馏管道
# ---------------------------------------------------------------------------

def auto_distill_raw(raw_rel_path: str,
                     cost_tracker: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """自动蒸馏 raw 文件为 wiki 页面。

    Returns:
        生成的 wiki 页面路径，或 None（如果失败）
    """
    kb = _import_kb()
    raw_path = KNOWLEDGE_DIR / raw_rel_path
    if not raw_path.exists():
        return None

    try:
        raw_text = raw_path.read_text(encoding="utf-8")
    except Exception:
        return None

    # 推断类型
    category = raw_path.parent.name
    wiki_type_map = {"papers": "papers", "notes": "concepts", "webclips": "concepts"}
    wiki_type = wiki_type_map.get(category, "concepts")

    source_data = {
        "content": raw_text,
        "name": raw_path.name,
        "type": wiki_type,
    }

    safe_name = _safe_filename(raw_path.stem)
    wiki_rel = f"wiki/{wiki_type}/{safe_name}.md"

    if (KNOWLEDGE_DIR / wiki_rel).exists():
        print(f"⚠ {wiki_rel} 已存在，跳过")
        return wiki_rel

    wiki_text, concepts, hints = distill_content("raw_note" if category == "notes" else "raw_webclip", source_data, cost_tracker)

    kb.save_distilled_wiki(wiki_rel, wiki_text, raw_rel_path=raw_rel_path)

    for concept in concepts:
        _integrate_concept(concept, wiki_text, source="raw")

    print(f"✓ raw 蒸馏已保存: {wiki_rel}")
    return wiki_rel


# ---------------------------------------------------------------------------
# Wiki 内容提取（处理 LLM 代码块包裹）
# ---------------------------------------------------------------------------

def _extract_wiki_content(raw_text: str) -> str:
    """从 LLM 输出中提取 wiki markdown 内容（处理代码块包裹）。"""
    raw_text = raw_text.strip()

    # 尝试提取 ```markdown ... ``` 代码块
    md_block = re.search(r'```markdown\s*\n(.*?)\n```', raw_text, re.DOTALL)
    if md_block:
        return md_block.group(1).strip()

    # 尝试提取 ``` ... ``` 代码块（无 markdown 标记）
    code_block = re.search(r'```\s*\n(.*?)\n```', raw_text, re.DOTALL)
    if code_block:
        content = code_block.group(1).strip()
        if content.startswith("---"):
            return content

    # 如果全文以 --- 开头，直接返回
    if raw_text.startswith("---"):
        return raw_text

    # 否则尝试找到第一个 --- 的位置
    first_fm = raw_text.find("---")
    if first_fm >= 0:
        return raw_text[first_fm:]

    return raw_text


# ---------------------------------------------------------------------------
# 概念提取
# ---------------------------------------------------------------------------

def _extract_concepts_from_wiki(wiki_text: str) -> List[str]:
    """从 wiki 内容中提取新概念名。

    策略：
    1. 提取 frontmatter 中的 related 字段
    2. 从 `## 核心发现` / `## 核心定义` / `## 核心要点` 下提取名词短语
    3. 提取 LLM 在 `related:` 中列出的概念
    """
    concepts = set()

    # 从 frontmatter 提取 related
    kb = _import_kb()
    try:
        fm, body = kb.parse_frontmatter(wiki_text)
        for r in fm.get("related", []):
            if r:
                concepts.add(r.strip())
    except Exception:
        pass

    # 从正文提取：标题下的列表项、加粗文字
    for match in re.finditer(r"\*\*(.+?)\*\*", wiki_text):
        term = match.group(1).strip()
        if 2 <= len(term) <= 30 and not term.startswith("http"):
            concepts.add(term)

    # 提取 `## 相关概念` 或类似章节下的内容
    for section in ["核心发现", "核心定义", "核心要点", "方法亮点", "实验参数备忘"]:
        pattern = rf"##\s*{section}\s*\n(.*?)(?=\n## |\Z)"
        m = re.search(pattern, wiki_text, re.DOTALL)
        if m:
            section_text = m.group(1)
            # 提取列表项和加粗项
            for line in section_text.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*"):
                    item = line.lstrip("-* ").strip()
                    if item:
                        # 取前半句作为概念名
                        concept = item.split(":")[0].split("——")[0].strip()
                        if 2 <= len(concept) <= 30:
                            concepts.add(concept)

    # 过滤：排除太短的、纯数字的、常见停用词
    filtered = []
    for c in concepts:
        if len(c) < 2 or c.isdigit():
            continue
        if c.lower() in {"the", "a", "an", "is", "are", "of", "in", "for", "on", "with", "to", "and", "or", "but"}:
            continue
        filtered.append(c)

    return filtered[:10]


# ---------------------------------------------------------------------------
# 知识整合器
# ---------------------------------------------------------------------------

def _integrate_concept(concept_name: str, new_content: str,
                       source: str = "auto") -> Optional[str]:
    """将新概念整合进知识库。

    如果概念已存在，追加新信息；如果不存在，创建 stub。

    Returns:
        wiki 页面路径
    """
    kb = _import_kb()
    safe_name = _safe_filename(concept_name)
    wiki_rel = f"wiki/concepts/{safe_name}.md"

    if (KNOWLEDGE_DIR / wiki_rel).exists():
        # 已有概念：尝试追加（简化版：记录到生长日志，不自动重写）
        kb.log_growth("concept_enrich", wiki_rel, source,
                      f"从 {source} 发现关联概念 '{concept_name}'，待进一步丰满")
        return wiki_rel
    else:
        # 检查相似概念，避免重复
        similar = kb.check_similar_concepts(concept_name, threshold=0.9)
        if similar:
            print(f"⚠ 概念 '{concept_name}' 与现有概念相似，跳过: {similar[0]['title']}")
            return None

        # 创建 stub
        stub_path = kb.create_wiki_stub(concept_name, context=new_content[:500], trigger=source)
        print(f"✓ 新概念 stub 已创建: {stub_path}")
        return stub_path


# ---------------------------------------------------------------------------
# 知识图谱自动扩展
# ---------------------------------------------------------------------------

def _auto_discover_edges(wiki_text: str, title: str) -> None:
    """从 wiki 内容中自动发现图谱关联。

    基于：
    1. frontmatter 中的 related 字段（已有）
    2. 正文中提到的其他 wiki 概念（通过搜索匹配）
    """
    kb = _import_kb()

    # 1. related 字段已在 save_distilled_wiki 中处理
    # 2. 从正文提取隐式关联
    try:
        fm, body = kb.parse_frontmatter(wiki_text)
        # 搜索正文中提到的其他概念
        all_wiki = kb.list_wiki_pages()
        for page in all_wiki:
            pt = page.get("title", "")
            if not pt or pt == title:
                continue
            # 简单匹配：概念名在正文中出现
            pattern = rf"\b{re.escape(pt)}\b"
            if re.search(pattern, body):
                kb.add_graph_edge(title, pt, "related")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 完整学习周期
# ---------------------------------------------------------------------------

def check_cost_limit() -> Tuple[bool, str]:
    """检查是否超过成本阈值。

    Returns:
        (是否允许继续, 原因)
    """
    cost_data = _load_json(COST_PATH, {})
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    month = today[:7]

    config = _load_json(MEMORY_DIR / "learning-config.json", {})
    daily_limit = config.get("cost_limit_daily", 0.5)
    monthly_limit = config.get("cost_limit_monthly", 10.0)

    daily_cost = cost_data.get("daily", {}).get(today, 0)
    monthly_cost = cost_data.get("monthly", {}).get(month, 0)

    if daily_cost >= daily_limit:
        return False, f"单日成本 ${daily_cost:.3f} 已超过阈值 ${daily_limit}"
    if monthly_cost >= monthly_limit:
        return False, f"单月成本 ${monthly_cost:.3f} 已超过阈值 ${monthly_limit}"

    return True, ""


def re_search_concepts(max_results: int = 3,
                       cost_tracker: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """对已有概念（mature/growing 阶段）重新搜索 arXiv 和 Wikipedia，查找近 30 天新内容。

    Returns:
        新发现的候选列表
    """
    kb = _import_kb()
    ef = _import_ef()

    # 获取 mature/growing 概念
    concepts = []
    for page in kb.list_wiki_pages():
        if page.get("growth_stage") in ("mature", "growing"):
            concepts.append(page.get("title", ""))

    if not concepts:
        return []

    # 取前 5 个概念进行 re-search
    candidates = []
    for concept in concepts[:5]:
        # arXiv
        papers = ef.fetch_arxiv(concept, max_results=max_results)
        for p in papers:
            date_str = p.get("date", "")
            if date_str:
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                days_ago = (datetime.now(timezone.utc) - dt.replace(tzinfo=timezone.utc)).days
                if days_ago <= 30:
                    candidates.append(p)

        # Wikipedia（通常没有"近30天"概念，跳过时效性过滤）
        wiki = ef.fetch_wikipedia(concept, lang="en")
        if wiki:
            candidates.append(wiki)

    # 去重（按标题）
    seen = set()
    unique = []
    for c in candidates:
        title = c.get("title", "")
        if title and title not in seen:
            seen.add(title)
            unique.append(c)

    return unique[:max_results * 3]


def run_learning_cycle(query: Optional[str] = None,
                       sources: Optional[List[str]] = None,
                       max_items: int = 3) -> Dict[str, Any]:
    """运行一次完整的自主学习周期。

    Args:
        query: 搜索关键词（None 时使用研究方向关键词）
        sources: 来源列表 ["arxiv", "wikipedia", "raw"]
        max_items: 最大处理数

    Returns:
        {
            "created": ["wiki/papers/xxx.md", ...],
            "updated": ["wiki/concepts/xxx.md", ...],
            "concepts": ["概念1", ...],
            "failed": [],
            "cost": {"calls": 3, "tokens": 1500},
            "duration_sec": 12.5
        }
    """
    import time
    start = time.time()

    # 成本阈值检查
    allowed, reason = check_cost_limit()
    if not allowed:
        print(f"⚠ 学习周期被暂停: {reason}")
        return {
            "created": [], "updated": [], "concepts": [], "failed": [reason],
            "cost": {"calls": 0, "tokens": 0}, "duration_sec": 0.0,
        }

    ef = _import_ef()
    cost_tracker: Dict[str, Any] = {"calls": 0, "tokens": 0, "providers_used": []}

    result = {
        "created": [],
        "updated": [],
        "concepts": [],
        "failed": [],
        "cost": cost_tracker,
        "duration_sec": 0.0,
    }

    print(f"◐ 启动学习周期: query={query}, sources={sources}")

    # 发现机会
    try:
        opportunities = ef.discover_learning_opportunities(
            query=query, max_results=max_items, sources=sources
        )
    except Exception as e:
        print(f"✗ 发现机会失败: {e}")
        result["failed"].append(f"discover: {e}")
        return result

    if not opportunities:
        print("○ 未发现学习机会")
        return result

    print(f"  发现 {len(opportunities)} 个机会，开始蒸馏...")

    for op in opportunities[:max_items]:
        source = op.get("source", "")
        score = op.get("_score", {}).get("overall", 0)
        title = op.get("title", "")

        print(f"  ◐ 处理: [{source}] {title[:40]}... (评分 {score})")

        try:
            if source == "arxiv":
                path = distill_arxiv_paper(op, cost_tracker)
                if path:
                    result["created"].append(path)
            elif source == "web":
                path = distill_web_search(op, cost_tracker)
                if path:
                    result["created"].append(path)
            elif source == "raw":
                raw_path = op.get("path", "")
                if raw_path:
                    path = auto_distill_raw(raw_path, cost_tracker)
                    if path:
                        result["created"].append(path)
            else:
                result["failed"].append(f"unknown source: {source}")
        except Exception as e:
            print(f"  ✗ 蒸馏失败: {e}")
            result["failed"].append(f"{source}:{title}: {e}")

    # 记录成本
    _record_cost(cost_tracker, "mixed")

    result["duration_sec"] = round(time.time() - start, 2)
    print(f"✓ 学习周期完成: 创建 {len(result['created'])} 个, 失败 {len(result['failed'])} 个, 耗时 {result['duration_sec']}s")
    return result


# ---------------------------------------------------------------------------
# 一键回滚
# ---------------------------------------------------------------------------

def rollback_growth(log_entry_id: Optional[str] = None,
                    wiki_path: Optional[str] = None) -> Dict[str, Any]:
    """回滚一次自主学习生长。

    Args:
        log_entry_id: growth-log.json 中的条目 ID（可选）
        wiki_path: 直接指定 wiki 路径回滚（可选）

    Returns:
        {"success": bool, "restored": ["path", ...], "deleted": ["path", ...]}
    """
    kb = _import_kb()
    result = {"success": False, "restored": [], "deleted": [], "errors": []}

    # 确定要回滚的 wiki 路径
    target_path = wiki_path
    if log_entry_id and not target_path:
        log = kb.get_growth_log(limit=100)
        for entry in log:
            if entry.get("id") == log_entry_id or entry.get("target") == log_entry_id:
                target_path = entry.get("target", "")
                break

    if not target_path:
        result["errors"].append("未找到可回滚的目标")
        return result

    full_path = KNOWLEDGE_DIR / target_path
    if not full_path.exists():
        result["errors"].append(f"文件不存在: {target_path}")
        return result

    # 创建备份目录
    backup_dir = KNOWLEDGE_DIR / ".backup" / "auto-grown" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 备份当前文件（即使是要删除的，也先备份）
        backup_path = backup_dir / Path(target_path).name
        backup_path.write_text(full_path.read_text(encoding="utf-8"), encoding="utf-8")

        # 删除文件
        full_path.unlink()
        result["deleted"].append(target_path)

        # 从图谱移除节点
        try:
            text = backup_path.read_text(encoding="utf-8")
            fm, _ = kb.parse_frontmatter(text)
            title = fm.get("title", "")
            if title:
                kb._remove_graph_node(title)
        except Exception as e:
            result["errors"].append(f"图谱清理失败: {e}")

        # 记录回滚日志
        kb.log_growth("rollback", target_path, "user", f"用户回滚生长，备份于 {backup_dir}")

        result["success"] = True
        print(f"✓ 回滚完成: {target_path}，备份于 {backup_dir}")

    except Exception as e:
        result["errors"].append(str(e))
        print(f"✗ 回滚失败: {e}")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="林赛自主学习引擎")
    parser.add_argument("--run", action="store_true", help="运行一次学习周期")
    parser.add_argument("--query", type=str, default=None, help="搜索关键词")
    parser.add_argument("--sources", type=str, default="arxiv,wikipedia,raw", help="来源列表，逗号分隔")
    parser.add_argument("--max", type=int, default=3, dest="max_items", help="最大处理数")
    args = parser.parse_args()

    if args.run:
        sources = [s.strip() for s in args.sources.split(",") if s.strip()]
        result = run_learning_cycle(query=args.query, sources=sources, max_items=args.max_items)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def _self_check() -> None:
    print("=" * 50)
    print("◐ 开始 learning_engine 自检")
    print("=" * 50)

    print("\n[1/5] 测试 _extract_concepts_from_wiki...")
    sample_wiki = """---
title: "固体高次谐波产生"
related: ["阿秒科学", "强场物理"]
---

## 核心发现
- **体光伏效应**是固体 HHG 的核心机制
- **带间跃迁**在强场下贡献显著
- 与**气体高次谐波**有本质区别

## 林赛的理解
我认为固体 HHG 的优势在于高密度靶材...
"""
    concepts = _extract_concepts_from_wiki(sample_wiki)
    print(f"   提取概念: {concepts}")
    assert "阿秒科学" in concepts, "应提取 frontmatter related"
    assert "体光伏效应" in concepts, "应提取加粗文字"
    print("   ✓ 概念提取通过")

    print("\n[2/5] 测试 _safe_filename...")
    assert _safe_filename("固体 HHG") == "固体_HHG"
    assert _safe_filename("test/file") == "test_file"
    print("   ✓ 文件名安全化通过")

    print("\n[3/5] 测试 _load_json / _save_json...")
    test_path = MEMORY_DIR / "test-learning.json"
    _save_json(test_path, {"key": "value"})
    data = _load_json(test_path)
    assert data.get("key") == "value"
    test_path.unlink()
    print("   ✓ JSON 读写通过")

    print("\n[4/5] 测试 prompt 构建...")
    arxiv_prompt = _build_arxiv_distill_prompt({
        "title": "Test Paper",
        "abstract": "This is a test abstract.",
        "tldr": "A test TLDR.",
        "authors": ["A", "B"],
        "date": "2026-01-01",
        "arxiv_id": "1234.56789"
    })
    assert "Test Paper" in arxiv_prompt
    assert "1234.56789" in arxiv_prompt
    assert "auto_grown: true" in arxiv_prompt

    wiki_prompt = _build_wikipedia_distill_prompt({
        "title": "Attosecond",
        "extract": "An attosecond is a very short time.",
        "description": "Unit of time",
        "url": "https://en.wikipedia.org/wiki/Attosecond"
    })
    assert "Attosecond" in wiki_prompt
    assert "auto_grown: true" in wiki_prompt
    print("   ✓ Prompt 构建通过")

    print("\n[5/5] 测试成本记录...")
    ct = {"calls": 2, "tokens": 1000, "providers_used": ["minimax"]}
    _record_cost(ct, "arxiv")
    cost_data = _load_json(COST_PATH, {})
    assert "daily" in cost_data
    assert "total_calls" in cost_data
    print(f"   成本数据: {json.dumps(cost_data, ensure_ascii=False)[:100]}...")
    print("   ✓ 成本记录通过")

    print("\n" + "=" * 50)
    print("✓ 所有自检项目通过")
    print("=" * 50)


if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1:
        main()
    else:
        _self_check()
