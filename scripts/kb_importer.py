#!/usr/bin/env python3
"""产出导入转换器 —— 把 hermes 的文献产出导入林赛知识库。

用途：
    将 hermes 每日文献简报系统的产出（daily_candidates.json / deep_analysis_*.json）
    转换为林赛知识库的标准格式，沉淀到「文献简报」子库。

数据流：
    hermes 产出（~/Desktop/hermes_workspace/knowledge_base/AI_wiki/briefings/）
        ↓ 导入
    林赛知识库
        ├─ raw/papers/{year}-{arxiv_id}-{slug}.md  （候选论文）
        └─ wiki/projects/文献简报/{title}.md        （深度解析）

字段映射（已验证对齐）：
    hermes 字段        →  林赛字段
    arxiv_id           →  frontmatter.arxiv_id
    title/authors/date →  frontmatter.title/authors/year
    tldr/abstract      →  正文摘要
    why_notable        →  ## 研究问题（Research Question）
    linsai_connection  →  ## 研究背景（Background）
    new_methods        →  ## 研究方法（Methods）
    core_findings      →  ## 主要发现与核心结论（Main Results）
    what_next          →  ## 潜在研究方向（Future Directions）

用法示例：
    >>> from kb_importer import import_candidate, import_deep_analysis
    >>> import_candidate('2403.15337')        # 导入单篇候选
    >>> import_deep_analysis('2403.15337')     # 导入深度解析到子库 wiki
    >>> import_all_candidates()                # 批量导入当日全部候选

规范：
    - 仅使用 Python 3 标准库
    - 头部包含中文 docstring
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 输出使用中文，状态图标统一
    - 所有导入的文件带 project: ["文献简报"] frontmatter，纳入子库检索
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc as _now_utc

from paths import PROJECT_ROOT, KNOWLEDGE_DIR, PDF_DIR, RAW_DIR, WIKI_DIR
RAW_PAPERS_DIR = KNOWLEDGE_DIR / "raw" / "papers"
WIKI_PAPERS_DIR = WIKI_DIR / "papers"
WIKI_PROJECTS_DIR = KNOWLEDGE_DIR / "wiki" / "projects" / "deepxiv-论文库"
PROJECT_TAG = "deepxiv-论文库"  # 归档论文默认子库（原"文献简报"，v2.9.3 重命名避免与每日简报混淆）

# hermes 简报产出目录
HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
BRIEFINGS_DIR = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings"


def _slugify(text: str, max_len: int = 50) -> str:
    """将标题转为文件名安全的 slug。"""
    # 保留中英文字母数字，其余替换为连字符
    slug = re.sub(r"[^\w\u4e00-\u9fff\-]", "-", text.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug[:max_len]


def _extract_year(date_str: str) -> str:
    """从日期字符串提取年份（如 '2024-03' → '2024'）。"""
    m = re.match(r"(\d{4})", date_str or "")
    return m.group(1) if m else str(datetime.now().year)


def _load_candidates() -> Dict[str, Any]:
    """加载 daily_candidates.json。"""
    path = BRIEFINGS_DIR / "daily_candidates.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_deep_analysis(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """加载指定论文的深度解析。"""
    path = BRIEFINGS_DIR / f"deep_analysis_{arxiv_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _find_candidate(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """从 daily_candidates 中查找指定论文。"""
    data = _load_candidates()
    for p in data.get("papers", []):
        if p.get("arxiv_id") == arxiv_id:
            return p
    return None


def import_candidate(arxiv_id: str, project: str = "") -> Optional[str]:
    """导入单篇候选论文到 raw/papers/。

    Args:
        arxiv_id: arXiv 论文 ID（如 '2403.15337'）
        project: 归属项目标签（空则按 direction 自动推断）

    Returns:
        生成的文件相对路径；未找到候选返回 None。
    """
    candidate = _find_candidate(arxiv_id)
    if not candidate:
        print(f"○ 未找到候选论文: {arxiv_id}")
        return None

    # 子库自动分类（v2.9.0）：project 为空时按 direction 推断
    if not project:
        project = infer_project(candidate.get("direction", ""))

    # v6.8.51: 键存在但值为 null 时 .get(k, "") 仍返回 None（hermes 侧 JSON
    # 偶发 null 字段），None 混入 fm_lines 会让 join 中断整条同步链——统一收敛为空串
    def _nz(v: Any) -> str:
        return v if isinstance(v, str) else ""

    title = _nz(candidate.get("title")) or arxiv_id
    year = _extract_year(candidate.get("date", ""))
    authors = candidate.get("authors", "")
    if isinstance(authors, list):
        # 过滤 None 项（偶发 null 条目）
        authors = ", ".join(str(a) for a in authors if a)
    authors = _nz(authors)
    tldr = _nz(candidate.get("tldr"))
    abstract = _nz(candidate.get("abstract"))
    direction = _nz(candidate.get("direction"))
    score = candidate.get("score_deepxiv") or 0
    ai_reason = _nz(candidate.get("ai_reason"))
    # v6.9.73: agent 相关性第二道门字段（简报 cron Step 1.5 打分）
    score_agent = candidate.get("score_agent")
    agent_note = _nz(candidate.get("agent_note"))
    agent_rejected = bool(candidate.get("agent_rejected"))

    slug = _slugify(title)
    filename = f"{year}-{arxiv_id}-{slug}.md"
    out_path = RAW_PAPERS_DIR / filename

    # 检查是否已导入（避免重复）
    if out_path.exists():
        print(f"⚠ 已存在，跳过: {filename}")
        return str(out_path.relative_to(KNOWLEDGE_DIR))

    # has_pdf 检测：检查 PDF_DIR 中是否存在对应 PDF
    has_pdf = False
    pdf_candidates = [
        PDF_DIR / f"{arxiv_id}.pdf",
        PDF_DIR / f"{arxiv_id}.PDF",
        PDF_DIR / f"{arxiv_id}v1.pdf",
        PDF_DIR / f"{arxiv_id}v2.pdf",
    ]
    for pdf_path in pdf_candidates:
        if pdf_path.exists():
            has_pdf = True
            break

    # 生成 frontmatter + 正文（扩展字段 v6.7.10+）
    tags = [PROJECT_TAG]
    if direction:
        tags.append(direction)

    # 构建 status_history 列表（Python 对象，用于 json.dumps）
    status_history = [
        {
            "status": "unseen",
            "timestamp": _now_utc(),
            "source": "hermes-简报",
        },
    ]

    # 构建 frontmatter（手动拼接 YAML 避免 f-string 嵌套问题）
    abstract_short = (abstract[:200] if abstract else "").replace('"', '\\"')
    fm_lines = [
        "---",
        f'title: "{title}"',
        f'arxiv_id: "{arxiv_id}"',
        f'authors: "{authors}"',
        f'year: "{year}"',
        f"tags: {json.dumps(tags, ensure_ascii=False)}",
        f'project: ["{project}"]',
        f'direction: "{direction}"',
        f'source: "hermes-简报"',
        f'imported_at: "{_now_utc()}"',
        f"score_deepxiv: {score}",
        f"score_agent: {json.dumps(score_agent)}",
        f'agent_note: "{agent_note}"',
        f"agent_rejected: {json.dumps(agent_rejected)}",
        f'abstract: "{abstract_short}"',
        "status: \"unseen\"",
        "unified_status: \"pool\"",
        "read_status: \"unread\"",
        "used_by_proposals: []",
        f"has_pdf: {json.dumps(has_pdf)}",
        "discussed_in_briefing: false",
        f"status_history: {json.dumps(status_history, ensure_ascii=False)}",
        "---",
        "",
        f"# {title}",
        "",
        f"**arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})",
        f"**作者**: {authors}",
        f"**方向**: {direction}",
        f"**deepxiv 评分**: {score}",
        "",
        "## TL;DR",
        "",
        tldr,
        "",
        "## 摘要",
        "",
        abstract,
        "",
        "## AI 评价",
        "",
        ai_reason,
    ]
    content = "\n".join(fm_lines)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"✓ 候选论文已导入: {filename}")
    return str(out_path.relative_to(KNOWLEDGE_DIR))


def import_deep_analysis(arxiv_id: str, project: str = "") -> Optional[str]:
    """导入深度解析到 wiki/papers/{arxiv_id}.md 的 ## 深度解析 段落。

    将 hermes 的深度分析（why_notable / core_findings / linsai_connection）
    转换为林赛视角的结构化内容，追加到论文 wiki 页面。

    Args:
        arxiv_id: arXiv 论文 ID
        project: 归属项目标签（空则按 direction 推断）

    Returns:
        生成的 wiki 文件相对路径；无深度解析返回 None。
    """
    from kb_wiki import save_wiki_page, get_wiki_page, build_wiki_page

    analysis = _load_deep_analysis(arxiv_id)
    if not analysis:
        print(f"○ 无深度解析: {arxiv_id}")
        return None

    # 子库自动分类
    if not project:
        project = infer_project(analysis.get("direction", ""))

    title = analysis.get("title", arxiv_id)
    authors = analysis.get("authors", "")
    date = analysis.get("date", "")
    direction = analysis.get("direction", "")
    why_notable = analysis.get("why_notable", "")
    core_findings = analysis.get("core_findings", [])
    new_methods = analysis.get("new_methods", [])
    what_next = analysis.get("what_next", [])
    linsai_connection = analysis.get("linsai_connection", "")

    # 目标路径：wiki/papers/{arxiv_id}.md
    rel_path = f"wiki/papers/{arxiv_id}.md"
    wiki_path = WIKI_PAPERS_DIR / f"{arxiv_id}.md"

    # 渲染列表项（容错：None / 非 list / 空）
    def _list_items(items) -> str:
        if not items:
            return "（暂无）"
        if isinstance(items, str):
            return items
        if not isinstance(items, list):
            return str(items)
        return "\n".join(f"- {item}" for item in items)

    # 构建深度解析段落
    deep_analysis_section = f"""## 深度解析

### 研究问题（Research Question）

{why_notable}

### 研究背景（Background）

{linsai_connection}

### 研究方法（Methods）

{_list_items(new_methods)}

### 主要发现与核心结论（Main Results）

{_list_items(core_findings)}

### 潜在研究方向（Future Directions）

{_list_items(what_next)}

### 来源

- [arXiv {arxiv_id}](https://arxiv.org/abs/{arxiv_id})
- 导入自 hermes 深度分析（{_now_utc()}）
"""

    if wiki_path.exists():
        # 已存在：追加 ## 深度解析 段落
        existing = get_wiki_page(rel_path)
        if existing:
            existing_body = existing.get("body", "")
            # 检查是否已有深度解析，避免重复追加
            if "## 深度解析" not in existing_body:
                save_wiki_page(rel_path, deep_analysis_section, append=True)
                print(f"✓ 深度解析已追加: wiki/papers/{arxiv_id}.md")
            else:
                print(f"○ 深度解析已存在，跳过: wiki/papers/{arxiv_id}.md")
    else:
        # 不存在：创建新页面（含论文元数据 + 深度解析）
        tags = [PROJECT_TAG, "深度解析"]
        if direction:
            tags.append(direction)

        meta = {
            "title": title,
            "type": "papers",
            "arxiv_id": arxiv_id,
            "authors": authors,
            "date": date,
            "direction": direction,
            "tags": tags,
            "project": [project],
            "source": "hermes-深度解析",
            "imported_at": _now_utc(),
            "growth_stage": "growing",
            "confidence": 0.8,
            "related": [],
            "status": "unseen",
            "unified_status": "pool",
            "read_status": "unread",
            "used_by_proposals": [],
            "has_pdf": False,
            "discussed_in_briefing": False,
            "status_history": [],
        }
        body = f"""# {title}

**arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id}) | **方向**: {direction}

{deep_analysis_section}
"""
        save_wiki_page(rel_path, body, meta)
        print(f"✓ 深度解析已创建新页面: wiki/papers/{arxiv_id}.md")

    return str(rel_path)


def import_all_candidates(project: str = "", with_analysis: bool = False) -> List[str]:
    """批量导入当日全部候选论文。

    Args:
        project: 归属项目标签
        with_analysis: 是否同时导入已有深度解析（默认 False，仅导入候选元数据）

    Returns:
        成功导入的 arxiv_id 列表
    """
    data = _load_candidates()
    papers = data.get("papers", [])
    if not papers:
        print("○ 无候选论文可导入")
        return []

    imported = []
    print(f"◐ 批量导入 {len(papers)} 篇候选...")
    for p in papers:
        aid = p.get("arxiv_id", "")
        if not aid:
            continue
        result = import_candidate(aid, project)
        if result:
            imported.append(aid)
            if with_analysis:
                import_deep_analysis(aid, project)

    print(f"✓ 导入完成: {len(imported)}/{len(papers)} 篇")
    return imported


def import_deep_analysis_all() -> Dict[str, Any]:
    """v6.8.14 WP2: 批量转换 hermes deep_analysis JSON 为 wiki/papers 5 维度笔记。

    链 ③：hermes deep_analysis_*.json → knowledge/wiki/papers/{arxiv_id}.md

    仅处理有完整 5 维度字段的 JSON（why_notable / core_findings / new_methods /
    what_next / linsai_connection），低质量分析自动跳过。

    Returns:
        {"imported": int, "skipped": int, "errors": int}
    """
    if not BRIEFINGS_DIR.exists():
        return {"imported": 0, "skipped": 0, "errors": 0}

    # 确保 kb_wiki 门面依赖已初始化（_ensure_dirs 等由 knowledge_base 注入）
    try:
        import knowledge_base as _kb  # noqa: F401 — 触发 kb_wiki 依赖注入
    except Exception:
        # knowledge_base 不可用时，手动初始化 kb_wiki 依赖
        import kb_wiki
        if kb_wiki._ensure_dirs is None:
            def _fallback_ensure_dirs():
                for t in ["concepts", "methods", "people", "papers", "projects"]:
                    (kb_wiki.WIKI_DIR / t).mkdir(parents=True, exist_ok=True)
            kb_wiki._ensure_dirs = _fallback_ensure_dirs
        if kb_wiki.log_growth is None:
            kb_wiki.log_growth = lambda *a, **kw: None

    analysis_files = sorted(BRIEFINGS_DIR.glob("deep_analysis_*.json"))
    imported = 0
    skipped = 0
    errors = 0

    # 必需字段（5 维度）
    required_fields = ["why_notable", "core_findings", "new_methods", "what_next", "linsai_connection"]

    for f in analysis_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            errors += 1
            continue

        arxiv_id = data.get("arxiv_id", "")
        if not arxiv_id:
            # 从文件名提取
            arxiv_id = f.stem.replace("deep_analysis_", "")
            if not arxiv_id:
                skipped += 1
                continue

        # 质量门槛：至少 3 个维度有实质内容
        filled = sum(1 for field in required_fields if data.get(field))
        if filled < 3:
            skipped += 1
            continue

        # 幂等检查：已有深度解析则跳过
        wiki_path = WIKI_PAPERS_DIR / f"{arxiv_id}.md"
        if wiki_path.exists():
            try:
                existing = wiki_path.read_text(encoding="utf-8")
                if "## 深度解析" in existing:
                    skipped += 1
                    continue
            except Exception:
                pass

        # 调用单篇导入
        try:
            result = import_deep_analysis(arxiv_id)
            if result:
                imported += 1
            else:
                skipped += 1
        except Exception:
            errors += 1

    return {"imported": imported, "skipped": skipped, "errors": errors}


def import_session_discussion(session_path: Path, project: str = PROJECT_TAG,
                              qa_type: str = "paper-discussion",
                              related_papers: Optional[List[str]] = None,
                              related_proposals: Optional[List[str]] = None) -> Optional[str]:
    """导入 hermes 会话为林赛讨论记录（qa/ 层）。

    将 hermes 的单文件会话 JSON 提取为林赛格式的讨论 markdown，
    通过 save_qa_page() 沉淀到 qa/ 层。

    Args:
        session_path: hermes 会话文件路径
        project: 归属项目标签
        qa_type: 讨论类型（"paper-discussion" / "proposal-discussion" / "project-discussion"）
        related_papers: 关联论文 arxiv_id 列表
        related_proposals: 关联 proposal_id 列表

    Returns:
        生成的讨论记录路径；失败返回 None。
    """
    from kb_wiki import save_qa_page

    session_path = Path(session_path)
    if not session_path.exists():
        return None

    try:
        data = json.loads(session_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    messages = data.get("messages", [])
    platform = data.get("platform", "unknown")
    session_id = data.get("session_id", session_path.stem)
    model = data.get("model", "")

    if not messages:
        return None

    # 生成讨论正文
    date_str = datetime.now().strftime("%Y%m%d")
    slug = f"讨论-{date_str}-{session_id[:8]}"

    lines = [
        f"**会话 ID**: `{session_id}`  ",
        f"**平台**: {platform}  ",
        f"**模型**: {model}  ",
        f"**导入时间**: {_now_utc()}  ",
        f"**归属项目**: {project}",
        "",
        "---",
        "",
    ]
    for m in messages:
        role = m.get("role", "unknown")
        content = m.get("content", "")
        label = "用户" if role == "user" else "林赛"
        lines.append(f"### {label}")
        lines.append("")
        lines.append(content[:2000])  # 截断超长消息
        lines.append("")

    body = "\n".join(lines)

    # 通过 save_qa_page 写入
    title = f"讨论记录 {date_str} ({session_id[:8]})"
    try:
        rel_path = save_qa_page(
            slug=slug,
            title=title,
            qa_type=qa_type,
            body=body,
            related_papers=related_papers,
            related_proposals=related_proposals,
        )
        print(f"✓ 讨论记录已导入: {rel_path}")
        return rel_path
    except Exception as e:
        print(f"✗ 讨论记录导入失败: {e}")
        return None


# ============================================================
# 智能生长（v2.9.0：归档自动 + wiki 确认）
# ============================================================

# 子库分类规则：direction 关键词 → 子库名
_SUBPROJECT_RULES = [
    (["固体HHG", "固体", "solid", "凝聚态", "2D", "MoS", "h-BN", "拓扑", "拓扑绝缘", "topological",
      "谷电子", "铁电", "石墨烯", " Transition metal"], "NSFC-强场超快"),
    (["气体HHG", "气体", "原子", "分子"], "deepxiv-论文库"),
]


def infer_project(direction: str, default: str = PROJECT_TAG) -> str:
    """根据研究方向推断归属子库。

    Args:
        direction: 论文方向标签（如 "固体HHG"、"2D材料"）
        default: 无法匹配时的默认子库

    Returns:
        子库名（"NSFC-强场超快" 或 "文献简报"）
    """
    if not direction:
        return default
    d_lower = direction.lower()
    for keywords, project in _SUBPROJECT_RULES:
        for kw in keywords:
            if kw.lower() in d_lower:
                return project
    return default


def suggest_wiki_notes(arxiv_id: str) -> Dict[str, Any]:
    """从深分析推断 wiki 笔记建议（供用户确认后生成）。

    读取 deep_analysis 的 core_findings / new_methods / linsai_connection，
    提取关键词，匹配现有 concepts，返回结构化建议。

    Returns:
        {
          "arxiv_id": str, "title": str, "available": bool,
          "concepts": [{"name": str, "existing": bool, "reason": str}],  # 建议的 concept 笔记
          "methods": [{"name": str, "reason": str}],  # 建议的 method 笔记
          "relations": [{"from": str, "to": str, "reason": str}],  # 建议的图谱关联
          "project": str,  # 建议归属子库
        }
    """
    analysis = _load_deep_analysis(arxiv_id)
    if not analysis:
        return {"arxiv_id": arxiv_id, "available": False, "concepts": [], "methods": [], "relations": []}

    title = analysis.get("title", arxiv_id)
    direction = analysis.get("direction", "")
    project = infer_project(direction)

    # 收集现有 concepts（用于匹配）
    import sys
    if str(PROJECT_ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    try:
        from knowledge_base import list_wiki_pages
        existing_concepts = {p["title"]: p for p in list_wiki_pages("concepts")}
    except Exception:
        existing_concepts = {}

    # 从 core_findings 提取概念关键词
    concepts_suggested = []
    core_findings = analysis.get("core_findings") or []
    if isinstance(core_findings, str):
        core_findings = [core_findings]
    for finding in core_findings[:5]:
        if not isinstance(finding, str):
            continue
        # 简单关键词提取：找中文/英文术语（>3字符的名词短语）
        import re
        terms = re.findall(r"[\u4e00-\u9fff]{2,8}|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*|[A-Z]{2,}(?:-[A-Z]{2,})*", finding)
        for term in set(terms):
            if len(term) < 3 or term in ("The", "This", "These", "HHG", "We", "Our"):
                continue
            # 匹配现有 concept（模糊）
            matched = None
            for ec_title in existing_concepts:
                if term in ec_title or ec_title in term:
                    matched = ec_title
                    break
            concepts_suggested.append({
                "name": term,
                "existing": matched is not None,
                "existing_title": matched or "",
                "reason": f"出现在核心发现: {finding[:60]}",
            })

    # 去重（同名只留一个，优先 existing=True）
    seen = {}
    for c in concepts_suggested:
        key = c["name"]
        if key not in seen or c["existing"]:
            seen[key] = c
    concepts_suggested = list(seen.values())[:8]

    # 从 new_methods 提取方法建议
    methods_suggested = []
    new_methods = analysis.get("new_methods") or []
    if isinstance(new_methods, str):
        new_methods = [new_methods]
    for m in new_methods[:3]:
        if isinstance(m, str) and len(m) > 5:
            methods_suggested.append({"name": m[:40], "reason": "深分析标注的新方法"})

    # 关联建议：linsai_connection 提到的概念
    relations_suggested = []
    linsai_conn = analysis.get("linsai_connection") or ""
    if isinstance(linsai_conn, str):
        for ec_title in list(existing_concepts.keys())[:10]:
            if ec_title in linsai_conn:
                relations_suggested.append({
                    "from": title, "to": ec_title, "reason": "林赛视角中提及",
                })

    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "available": True,
        "concepts": concepts_suggested,
        "methods": methods_suggested,
        "relations": relations_suggested,
        "project": project,
    }


def grow_from_suggestion(arxiv_id: str, confirmed: Dict[str, Any]) -> Dict[str, Any]:
    """按用户确认的建议生成 wiki 笔记 + 连图谱。

    Args:
        arxiv_id: 论文 ID
        confirmed: {
          "concepts": [{"name": str, "generate": bool}],  # 用户确认要生成的 concept
          "relations": [{"from": str, "to": str, "confirm": bool}],  # 确认的关联
          "project": str,  # 归属子库
        }

    Returns:
        {success, generated_concepts: [...], generated_relations: [...]}
    """
    import sys
    if str(PROJECT_ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from knowledge_base import save_wiki_page, add_graph_edge

    project = confirmed.get("project", PROJECT_TAG)
    analysis = _load_deep_analysis(arxiv_id)
    if not analysis:
        return {"success": False, "error": "无深分析数据"}

    generated = []

    # 生成确认的 concept 笔记（种子级，标记 seedling 待用户补充）
    for c in confirmed.get("concepts", []):
        if not c.get("generate"):
            continue
        name = c.get("name", "").strip()
        if not name:
            continue
        wiki_type = c.get("type", "concepts")
        content = f"""---
title: "{name}"
type: "{wiki_type}"
created: "{_now_utc()}"
updated: "{_now_utc()}"
tags: ["{project}", "自动提取"]
related: []
aliases: []
project: ["{project}"]
source_arxiv: "{arxiv_id}"
growth_stage: "seedling"
confidence: 0.4
---

# {name}

## 来源

从 arXiv [{arxiv_id}](https://arxiv.org/abs/{arxiv_id}) 的深度分析自动提取。

> 这是一个种子笔记，请补充你的理解。

## 林赛的理解

（待补充）

## 核心要点

（待补充）

## 来源论文

- {analysis.get('title', arxiv_id)} ([arXiv {arxiv_id}](https://arxiv.org/abs/{arxiv_id}))
"""
        try:
            rel_path = save_wiki_page(name, wiki_type, content)
            generated.append({"type": wiki_type, "name": name, "path": rel_path})
        except Exception as e:
            generated.append({"type": wiki_type, "name": name, "error": str(e)})

    # 生成确认的关联边
    relations_made = []
    for r in confirmed.get("relations", []):
        if not r.get("confirm"):
            continue
        try:
            add_graph_edge(r["from"], r["to"], r.get("reason", "related"))
            relations_made.append({"from": r["from"], "to": r["to"]})
        except Exception:
            pass

    return {
        "success": True,
        "generated_concepts": [g for g in generated if g.get("type") == "concepts"],
        "generated_all": generated,
        "generated_relations": relations_made,
        "project": project,
    }


def _self_check() -> None:
    """自检：验证产出目录可读 + 字段映射。"""
    print("=" * 50)
    print("◐ kb_importer 自检")
    print("=" * 50)

    # 1. 检查 hermes 产出目录
    print("\n[1/3] 检查 hermes 产出目录...")
    if BRIEFINGS_DIR.exists():
        candidates = _load_candidates()
        n = len(candidates.get("papers", []))
        print(f"  ✓ daily_candidates.json 可读，{n} 篇候选")
        # 检查字段
        if n > 0:
            p = candidates["papers"][0]
            required = ["arxiv_id", "title", "authors", "tldr"]
            missing = [f for f in required if f not in p]
            assert not missing, f"候选字段缺失: {missing}"
            print(f"  ✓ 字段完整: {list(p.keys())}")
    else:
        print(f"  ○ hermes 产出目录不存在: {BRIEFINGS_DIR}")

    # 2. 检查深度解析
    print("\n[2/3] 检查深度解析...")
    analysis_files = list(BRIEFINGS_DIR.glob("deep_analysis_*.json")) if BRIEFINGS_DIR.exists() else []
    print(f"  ✓ 找到 {len(analysis_files)} 份深度解析")
    if analysis_files:
        aid = analysis_files[0].stem.replace("deep_analysis_", "")
        analysis = _load_deep_analysis(aid)
        if analysis:
            # 核心字段必填，其余容错（早期格式可能缺 core_findings 等）
            required = ["arxiv_id", "title"]
            missing = [f for f in required if f not in analysis]
            assert not missing, f"深度解析核心字段缺失: {missing}"
            print(f"  ✓ 字段可读（{len(analysis.keys())} 个）: {list(analysis.keys())[:6]}...")

    # 3. 测试 slugify
    print("\n[3/3] 测试工具函数...")
    assert _slugify("High Harmonic Generation by Bright Squeezed Vacuum") == "high-harmonic-generation-by-bright-squeezed-vacuum"
    assert _extract_year("2024-03") == "2024"
    assert _extract_year("") == str(datetime.now().year)
    print("  ✓ _slugify / _extract_year 正常")

    print("\n✓ kb_importer 自检通过")


if __name__ == "__main__":
    _self_check()
