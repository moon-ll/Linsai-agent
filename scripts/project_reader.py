#!/usr/bin/env python3
"""项目数据读取器 —— 解析 hermes NSFC 项目状态，供 Web 面板展示。

用途：
    读取 ~/Desktop/hermes_workspace/research_proposals/ 下的 NSFC 项目文件，
    解析 state.md（进度/待决策/路线图）、discussions（决策卡）、topics（申请书章节），
    以及文献简报系统的候选/简报列表，返回结构化数据供 Web 前端渲染。

解析对象：
    - state.md：按 ## 区块切分，提取「当前 Phase」「关键风险」「路线图」「6 问追踪」
    - discussions/*_decisions.md：提取决策卡（标题/结论/依据/用户原话/可推翻窗口）
    - topics/T{N}_*/notes/：申请书章节文档列表 + 元信息
    - knowledge_base/AI_wiki/briefings/daily_candidates.json：文献候选表格
    - knowledge_base/AI_wiki/briefings/research_briefing_*.md：简报列表

用法示例：
    >>> from project_reader import get_nsfc_dashboard, get_candidates, get_decisions
    >>> dashboard = get_nsfc_dashboard()      # NSFC 仪表盘数据
    >>> candidates = get_candidates()          # 今日文献候选
    >>> decisions = get_decisions(limit=5)     # 最近 5 条决策

规范：
    - 仅使用 Python 3 标准库
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 解析失败时优雅降级（返回空结构，不抛异常）
    - 所有路径用 pathlib.Path，不硬编码绝对路径
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent

# hermes 工作区
HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
NSFC_DIR = HERMES_WORKSPACE / "research_proposals" / "2026_NSFG_strongfield_ultrafast"
BRIEFINGS_DIR = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings"

# emoji 状态符号映射（state.md 用的状态体系）
STATUS_MAP = {
    "✅": "done",
    "⏳": "in_progress",
    "⚠️": "risk",
    "⚠": "risk",
    "📌": "pending_decision",
    "❌": "blocked",
}


def _read_text(path: Path) -> str:
    """安全读取文件文本。"""
    try:
        return path.read_text(encoding="utf-8") if path.exists() else ""
    except Exception:
        return ""


def _detect_status(text: str) -> str:
    """从一行文本检测状态（基于 emoji 符号）。"""
    for emoji, status in STATUS_MAP.items():
        if emoji in text:
            return status
    return "unknown"


# ============================================================
# NSFC 项目仪表盘
# ============================================================

def parse_nsfc_state() -> Dict[str, Any]:
    """解析 NSFC 项目的 state.md，返回仪表盘数据。

    Returns:
        {
            "available": bool,           # 项目是否存在
            "phase": str,                # 当前阶段
            "key_decisions": [str],      # 最近关键决策（摘要）
            "pending_decisions": [str],  # 待决策项（⚠️/📌 行）
            "risks": [str],              # 风险项
            "roadmap": [{task, status}], # 路线图
            "six_questions": {str: str}, # 6 问连续性追踪
            "brain_count": int,          # BRAIN 决策区块数
            "last_updated": str,         # 文件修改时间
        }
    """
    state_path = NSFC_DIR / "state.md"
    if not state_path.exists():
        return {"available": False, "reason": "NSFC 项目目录不存在"}

    text = _read_text(state_path)
    result: Dict[str, Any] = {
        "available": True,
        "phase": "",
        "key_decisions": [],
        "pending_decisions": [],
        "risks": [],
        "roadmap": [],
        "six_questions": {},
        "brain_count": 0,
        "last_updated": datetime.fromtimestamp(state_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
    }

    # 切分区块
    sections = re.split(r"^## ", text, flags=re.MULTILINE)

    for section in sections:
        lines = section.strip().split("\n")
        header = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:])

        # 当前 Phase
        if header.startswith("🎯"):
            result["phase"] = _extract_phase(body)

        # BRAIN 决策区块
        elif header.startswith("🧠"):
            result["brain_count"] += 1
            # 提取关键决策摘要（首段非空文本）
            for line in lines[1:6]:
                line = line.strip()
                if line and not line.startswith("|") and not line.startswith("-"):
                    result["key_decisions"].append(line[:100])
                    break

        # 关键状态 & 风险
        elif header.startswith("⚠️") or header.startswith("⚠"):
            for line in lines[1:]:
                line = line.strip()
                if not line or line.startswith("##"):
                    continue
                status = _detect_status(line)
                # 清理 emoji 和 markdown 符号
                clean = re.sub(r"^[✅⏳⚠️📌❌\-*\s]+", "", line).strip()
                if clean:
                    if status == "pending_decision":
                        result["pending_decisions"].append(clean)
                    elif status == "risk":
                        result["risks"].append(clean)
                    elif status in ("done", "in_progress"):
                        result["pending_decisions"].append(clean)  # 待办也收录

        # 路线图
        elif header.startswith("📅"):
            result["roadmap"] = _parse_table_rows(body)

        # 6 问连续性追踪
        elif header.startswith("🔁"):
            result["six_questions"] = _parse_six_questions(body)

    return result


def _extract_phase(body: str) -> str:
    """从「当前 Phase」区块提取阶段描述。"""
    # 匹配 "Phase: X" 或 "当前阶段 = X" 等
    m = re.search(r"(?:Phase|阶段)[：:]\s*(.+?)(?:\n|$)", body)
    if m:
        return m.group(1).strip()[:80]
    # fallback：取第一行非空
    for line in body.strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("|"):
            return line[:80]
    return "未知"


def _parse_table_rows(body: str) -> List[Dict[str, str]]:
    """解析 markdown 表格行，提取任务名和状态。"""
    rows = []
    for line in body.split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if not cells:
            continue
        # 第一列通常是任务名，最后一列通常是状态
        task = cells[0] if cells else ""
        status_cell = cells[-1] if len(cells) > 1 else task
        status = _detect_status(status_cell)
        if task and status != "unknown":
            rows.append({
                "task": re.sub(r"[✅⏳⚠️📌❌]", "", task).strip()[:60],
                "status": status,
            })
    return rows[:20]  # 限制条数


def _parse_six_questions(body: str) -> Dict[str, str]:
    """解析「6 问连续性追踪」的问答。"""
    questions = {}
    current_q = ""
    for line in body.split("\n"):
        line = line.strip()
        # 匹配 "1. 当前 phase" 或 "- 当前 phase" 形式
        m = re.match(r"^(?:\d+[\.\)、]|[-*])\s*(.{2,30}？|.{2,30}:)", line)
        if m:
            current_q = re.sub(r"[：:?？]$", "", m.group(1)).strip()
            rest = line[m.end():].strip()
            if rest:
                questions[current_q] = rest[:120]
        elif current_q and line:
            # 续行
            if current_q not in questions:
                questions[current_q] = line[:120]
    return questions


# ============================================================
# 决策时间轴
# ============================================================

def get_decisions(limit: int = 10) -> List[Dict[str, Any]]:
    """解析 discussions 目录下的决策记录，返回决策时间轴。

    Args:
        limit: 最多返回多少条决策

    Returns:
        [{date, title, decision, rationale, user_quote, output_files, overridable_window}]
    """
    discussions_dir = NSFC_DIR / "discussions"
    if not discussions_dir.exists():
        return []

    decisions = []
    # 按日期倒序扫描
    files = sorted(discussions_dir.glob("*_decisions.md"), reverse=True)
    for fpath in files:
        text = _read_text(fpath)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", fpath.name)
        date = date_match.group(1) if date_match else fpath.stem

        # 提取决策卡（## N. 决策 N: 标题）
        cards = re.split(r"^## \d+\.\s*决策\s*\d*[：:]", text, flags=re.MULTILINE)
        for card in cards[1:]:  # 跳过第一段（非决策内容）
            lines = card.strip().split("\n")
            title = lines[0].strip().rstrip("⭐").strip() if lines else ""
            if not title:
                continue

            card_text = "\n".join(lines[1:])
            decisions.append({
                "date": date,
                "title": title[:80],
                "decision": _extract_field(card_text, "决策"),
                "rationale": _extract_field(card_text, "依据"),
                "user_quote": _extract_field(card_text, "用户原话"),
                "output_files": _extract_field(card_text, "触发产出"),
                "overridable_window": _extract_field(card_text, "可推翻"),
                "file": str(fpath.name),
            })
            if len(decisions) >= limit:
                return decisions

    return decisions


def _extract_field(text: str, field_name: str) -> str:
    """从决策卡文本提取指定字段（如「依据」「用户原话」）的值。"""
    # 匹配 "**依据**: xxx" 或 "依据：xxx"
    pattern = rf"\**{re.escape(field_name)}\**[：:]\s*(.+?)(?:\n\*\*|\n##|\Z)"
    m = re.search(pattern, text, re.DOTALL)
    if m:
        val = m.group(1).strip()
        # 清理多余 markdown
        val = re.sub(r"\n+", " ", val)[:200]
        return val
    return ""


# ============================================================
# 申请书章节
# ============================================================

def get_proposal_chapters() -> List[Dict[str, Any]]:
    """列出 NSFC 申请书的各章节文档（topics/T1-T5）。

    Returns:
        [{topic, title, path, version, size_kb, modified}]
    """
    topics_dir = NSFC_DIR / "topics"
    if not topics_dir.exists():
        return []

    chapters = []
    # 扫描 T1-T5 目录
    for tdir in sorted(topics_dir.glob("T*")):
        if not tdir.is_dir():
            continue
        topic = tdir.name

        # 读 README 获取标题
        readme = _read_text(tdir / "README.md")
        title = ""
        for line in readme.split("\n"):
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break

        # 找 notes/ 下的立项依据文档
        notes_dir = tdir / "notes"
        doc_path = None
        if notes_dir.exists():
            docs = sorted(notes_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            if docs:
                doc_path = docs[0]

        version = ""
        size_kb = 0
        modified = ""
        if doc_path:
            # 从文件名提取版本
            vm = re.search(r"v(\d+\.\d+)", doc_path.name)
            version = vm.group(1) if vm else "?"
            size_kb = round(doc_path.stat().st_size / 1024, 1)
            modified = datetime.fromtimestamp(doc_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")

        chapters.append({
            "topic": topic,
            "title": title or topic,
            "path": str(doc_path.relative_to(NSFC_DIR)) if doc_path else "",
            "version": version,
            "size_kb": size_kb,
            "modified": modified,
        })

    # 加上共性顶层
    overall = topics_dir / "00_overall"
    if overall.exists():
        docs = sorted(overall.glob("*.md"), reverse=True)
        if docs:
            d = docs[0]
            chapters.insert(0, {
                "topic": "00",
                "title": "共性顶层（研究方向）",
                "path": str(d.relative_to(NSFC_DIR)),
                "version": "?",
                "size_kb": round(d.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(d.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            })

    return chapters


def read_proposal_content(topic: str) -> Dict[str, Any]:
    """读取指定章节的申请书内容。

    Args:
        topic: 章节标识（如 'T3' 或 '00'）

    Returns:
        {content, path, available}
    """
    topics_dir = NSFC_DIR / "topics"
    search_dirs = []
    if topic == "00":
        search_dirs.append(topics_dir / "00_overall")
    else:
        search_dirs.append(topics_dir / topic)
        search_dirs.append(topics_dir / f"{topic}_*")  # 通配

    for pattern in search_dirs:
        for tdir in topics_dir.glob(pattern.name if "*" in pattern.name else ""):
            if not tdir.is_dir():
                continue
            notes = tdir / "notes"
            check_dir = notes if notes.exists() else tdir
            docs = sorted(check_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            if docs:
                return {
                    "available": True,
                    "content": _read_text(docs[0]),
                    "path": str(docs[0].relative_to(NSFC_DIR)),
                    "size_kb": round(docs[0].stat().st_size / 1024, 1),
                }

    return {"available": False, "content": "", "path": ""}


# ============================================================
# 文献简报数据
# ============================================================

def get_candidates() -> Dict[str, Any]:
    """读取今日文献候选列表。

    Returns:
        {date, total, papers: [{arxiv_id, title, authors, score, direction, tldr, has_analysis}]}
    """
    path = BRIEFINGS_DIR / "daily_candidates.json"
    if not path.exists():
        return {"available": False, "date": "", "total": 0, "papers": []}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"available": False, "date": "", "total": 0, "papers": []}

    papers = []
    for p in data.get("papers", []):
        aid = p.get("arxiv_id", "")
        papers.append({
            "arxiv_id": aid,
            "title": p.get("title", ""),
            "authors": p.get("authors", "") if isinstance(p.get("authors"), str) else ", ".join(p.get("authors", [])),
            "score": p.get("score_deepxiv", 0),
            "direction": p.get("direction", ""),
            "tldr": p.get("tldr", "")[:150],
            "has_analysis": (BRIEFINGS_DIR / f"deep_analysis_{aid}.json").exists(),
        })

    # 按分数降序
    papers.sort(key=lambda x: x["score"], reverse=True)

    return {
        "available": True,
        "date": data.get("date", ""),
        "total": data.get("total_candidates", len(papers)),
        "papers": papers,
    }


def get_briefings() -> List[Dict[str, Any]]:
    """列出已有的研究简报文件。

    Returns:
        [{date, title, path, size_kb}]
    """
    if not BRIEFINGS_DIR.exists():
        return []

    briefings = []
    for fpath in sorted(BRIEFINGS_DIR.glob("research_briefing_*.md"), reverse=True):
        # 从文件名提取日期
        dm = re.search(r"(\d{8})", fpath.name)
        date = dm.group(1) if dm else fpath.stem
        date_fmt = f"{date[:4]}-{date[4:6]}-{date[6:8]}" if len(date) == 8 else date

        # 读首行标题
        first_line = ""
        try:
            first_line = fpath.read_text(encoding="utf-8").split("\n", 1)[0].lstrip("#").strip()
        except Exception:
            pass

        briefings.append({
            "date": date_fmt,
            "title": first_line or fpath.stem,
            "path": str(fpath.relative_to(HERMES_WORKSPACE)),
            "size_kb": round(fpath.stat().st_size / 1024, 1),
        })

    return briefings[:20]


# ============================================================
# 项目概况
# ============================================================

def get_projects_overview() -> Dict[str, Any]:
    """返回两个项目的概况（供 Web 首页展示）。"""
    nsfc_state = NSFC_DIR / "state.md"
    candidates = get_candidates()

    return {
        "nsfc": {
            "available": nsfc_state.exists(),
            "path": str(NSFC_DIR.relative_to(HERMES_WORKSPACE)) if NSFC_DIR.exists() else "",
            "phase": _extract_phase(_read_text(nsfc_state).split("## 🎯")[1].split("##")[0]) if nsfc_state.exists() else "",
        },
        "papers": {
            "available": candidates["available"],
            "date": candidates["date"],
            "total": candidates["total"],
        },
        "briefings_count": len(get_briefings()),
        "decisions_count": len(get_decisions(limit=100)),
    }


def get_projects_list() -> List[Dict[str, Any]]:
    """返回项目清单（供任务表单项目下拉框 + 总览页使用）。

    聚合三个来源，去重：
    1. NSFC hermes 项目（若存在）
    2. 知识库 wiki/projects/ 下的子库目录
    3. memory/working-context.json 的 active_projects

    Returns:
        [{name, source, status}]，name 唯一，按 source 优先级排序
    """
    seen = set()
    projects = []

    def _add(name: str, source: str, status: str = ""):
        name = (name or "").strip()
        if not name or name in seen:
            return
        seen.add(name)
        projects.append({"name": name, "source": source, "status": status})

    # 1. NSFC hermes 项目
    if NSFC_DIR.exists():
        _add("NSFC-强场超快", "hermes", "active")

    # 2. 知识库 wiki/projects/ 子库
    try:
        wiki_projects = PROJECT_ROOT / "knowledge" / "wiki" / "projects"
        if wiki_projects.exists():
            for d in wiki_projects.iterdir():
                if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("_"):
                    _add(d.name, "knowledge")
    except OSError:
        pass

    # 3. working-context.json 的 active_projects
    try:
        wc_path = PROJECT_ROOT / "memory" / "working-context.json"
        if wc_path.exists():
            wc = json.loads(wc_path.read_text(encoding="utf-8"))
            for p in wc.get("active_projects", []):
                _add(p.get("name", ""), "working-context", p.get("status", ""))
    except (json.JSONDecodeError, OSError):
        pass

    return projects


# ============================================================
# NSFC state.md 层次结构解析（v2.9.0 三层展开）
# ============================================================

# 文件路径正则：反引号路径 `xxx/yyy.md` 和 markdown 链接 [text](path)
_RE_TICK_PATH = re.compile(r"`([a-zA-Z0-9_/\-\.]+\.md)`")
_RE_MD_LINK = re.compile(r"\[([^\]]*?)\]\(([a-zA-Z0-9_/\-\.]+\.md)\)")
# 默认展开的关键区块（按 emoji 匹配）
_DEFAULT_OPEN_ICONS = {"🎯", "⚠️", "⚠", "📅"}


def parse_nsfc_state_hierarchical() -> Dict[str, Any]:
    """解析 NSFC state.md 为三层结构（供前端折叠树渲染）。

    层次：
      第1层：## 区块（标题 + emoji）
      第2层：区块内的 ### 子标题 / 表格行 / 列表项
      第3层：行内提取的文件路径（可点击读内容）

    Returns:
        {
          "available": bool,
          "sections": [
            {
              "title": "🧠 BRAIN 决策 (...)",
              "icon": "🧠",
              "summary": "首段非空摘要",
              "default_open": bool,  # 是否默认展开
              "rows": [  # 第2层
                {
                  "type": "table"|"list"|"text",
                  "cells": ["...", ...]  # table 行的单元格 / list 的文本
                  "file_paths": ["topics/...md", ...]  # 第3层
                  "status": "done"|"in_progress"|"risk"|"pending_decision"|""
                }
              ]
            }
          ],
          "last_updated": str,
        }
    """
    state_path = NSFC_DIR / "state.md"
    if not state_path.exists():
        return {"available": False, "sections": [], "reason": "state.md 不存在"}

    text = _read_text(state_path)
    result: Dict[str, Any] = {
        "available": True,
        "sections": [],
        "last_updated": datetime.fromtimestamp(state_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
    }

    # 第1层：按 ## 切区块
    raw_sections = re.split(r"^## ", text, flags=re.MULTILINE)
    for raw_sec in raw_sections[1:]:  # 跳过第一段（文件头）
        lines = raw_sec.strip().split("\n")
        if not lines:
            continue
        header = lines[0].strip()

        # 提取 emoji icon
        icon = ""
        for ch in header:
            if ord(ch) > 0x1F000:  # emoji 范围
                icon += ch

        # 摘要：首个非空非标题非表格行
        summary = ""
        for line in lines[1:5]:
            line = line.strip()
            if line and not line.startswith("|") and not line.startswith("#") and not line.startswith("---"):
                summary = line[:100]
                break

        # 第2层：解析区块内的行
        rows = []
        in_table = False
        for line in lines[1:]:
            line_stripped = line.strip()
            if not line_stripped:
                in_table = False
                continue

            # 表格行
            if line_stripped.startswith("|"):
                if "---" in line_stripped:
                    continue  # 表头分隔线
                cells = [c.strip() for c in line_stripped.split("|")[1:-1]]
                if cells and any(c for c in cells):
                    # 提取第3层文件路径
                    file_paths = set()
                    for cell in cells:
                        for m in _RE_TICK_PATH.finditer(cell):
                            file_paths.add(m.group(1))
                        for m in _RE_MD_LINK.finditer(cell):
                            file_paths.add(m.group(2))
                    # 检测状态
                    status = _detect_status(line_stripped)
                    rows.append({
                        "type": "table",
                        "cells": cells,
                        "file_paths": sorted(file_paths),
                        "status": status,
                    })
                in_table = True
                continue

            # 列表项（- 或 数字.）
            list_match = re.match(r"^(?:[-*]|\d+\.)\s+(.+)", line_stripped)
            if list_match:
                content = list_match.group(1)
                file_paths = set()
                for m in _RE_TICK_PATH.finditer(content):
                    file_paths.add(m.group(1))
                for m in _RE_MD_LINK.finditer(content):
                    file_paths.add(m.group(2))
                status = _detect_status(content)
                rows.append({
                    "type": "list",
                    "cells": [content],
                    "file_paths": sorted(file_paths),
                    "status": status,
                })
                continue

            # ### 子标题作为分隔标记（也作为 text 行）
            if line_stripped.startswith("###"):
                rows.append({
                    "type": "text",
                    "cells": [line_stripped.lstrip("#").strip()],
                    "file_paths": [],
                    "status": "",
                })
                continue

        result["sections"].append({
            "title": header[:80],
            "icon": icon or "📄",
            "summary": summary,
            "default_open": any(ic in header for ic in _DEFAULT_OPEN_ICONS) or len(rows) <= 3,
            "rows": rows,
        })

    return result


# ============================================================
# NSFC 结构化数据（v2.9.2：课题产物 + 调研资料 + 待决策项）
# ============================================================

# 中文课题名映射
_TOPIC_NAMES = {
    "T1": "量子几何", "T2": "谷电子学", "T3": "带动力学",
    "T4": "序参量", "T5": "反演方法学", "00": "共性顶层",
}


def get_nsfc_topics() -> List[Dict[str, Any]]:
    """扫描 topics/ 返回课题产物卡片列表。

    Returns:
        [{topic, name, direction, notes:[{name,size_kb,modified,version}],
          references_count, decisions_count, progress, total_kb}]
    """
    topics_dir = NSFC_DIR / "topics"
    if not topics_dir.exists():
        return []

    topics = []
    for tdir in sorted(topics_dir.iterdir()):
        if not tdir.is_dir() or not tdir.name.startswith(("T", "0")):
            continue

        topic_id = tdir.name.split("_")[0]
        name = _TOPIC_NAMES.get(topic_id, tdir.name)
        direction = tdir.name.split("_", 1)[1].replace("_", " ") if "_" in tdir.name else ""

        # notes/ 文档
        notes = []
        notes_dir = tdir / "notes"
        if notes_dir.exists():
            for f in sorted(notes_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
                vm = re.search(r"v(\d+\.\d+)", f.name)
                notes.append({
                    "name": f.name,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%m-%d"),
                    "version": vm.group(1) if vm else "?",
                })

        # references/ 和 decisions/ 计数
        refs_count = len(list((tdir / "references").glob("*.md"))) if (tdir / "references").exists() else 0
        decs_count = len(list((tdir / "decisions").glob("*.md"))) if (tdir / "decisions").exists() else 0

        # 进度推断（notes 总大小）
        total_kb = sum(n["size_kb"] for n in notes)
        if total_kb > 80:
            progress = "mature"
        elif total_kb > 30:
            progress = "growing"
        elif total_kb > 0:
            progress = "seedling"
        else:
            progress = "empty"

        topics.append({
            "topic": topic_id,
            "name": name,
            "direction": direction,
            "dir_name": tdir.name,
            "notes": notes,
            "references_count": refs_count,
            "decisions_count": decs_count,
            "progress": progress,
            "total_kb": total_kb,
        })

    return topics


def get_nsfc_references() -> Dict[str, Any]:
    """聚合 NSFC 项目的调研资料清单（按来源分类）。

    Returns:
        {references:[...], knowledge_base:{concepts:[],methods:[]}, briefs:[]}
    """
    result = {"references": [], "knowledge_base": {}, "briefs": []}

    # references/ 文献笔记
    refs_dir = NSFC_DIR / "references"
    if refs_dir.exists():
        for sub in refs_dir.iterdir():
            if sub.is_dir():
                for f in sub.glob("*.md"):
                    result["references"].append({
                        "name": f.name, "category": sub.name,
                        "size_kb": round(f.stat().st_size / 1024, 1),
                        "path": str(f.relative_to(NSFC_DIR)),
                    })
            elif sub.suffix == ".md":
                result["references"].append({
                    "name": sub.name, "category": "root",
                    "size_kb": round(sub.stat().st_size / 1024, 1),
                    "path": str(sub.relative_to(NSFC_DIR)),
                })

    # knowledge_base/ 概念/方法
    kb_dir = NSFC_DIR / "knowledge_base"
    if kb_dir.exists():
        for sub in ("concepts", "methods", "literature"):
            sub_dir = kb_dir / sub
            if sub_dir.exists():
                items = []
                for f in sub_dir.glob("*.md"):
                    items.append({"name": f.stem, "path": str(f.relative_to(NSFC_DIR)),
                                  "size_kb": round(f.stat().st_size / 1024, 1)})
                result["knowledge_base"][sub] = items

    # deliverables/daily_brief 简报
    brief_dir = NSFC_DIR / "deliverables" / "daily_brief"
    if brief_dir.exists():
        for f in sorted(brief_dir.glob("*.md"), reverse=True):
            dm = re.search(r"(\d{4}-\d{2}-\d{2})", f.name)
            result["briefs"].append({
                "date": dm.group(1) if dm else f.stem,
                "name": f.name, "path": str(f.relative_to(NSFC_DIR)),
                "size_kb": round(f.stat().st_size / 1024, 1),
            })

    return result


def get_nsfc_pending() -> List[Dict[str, Any]]:
    """从 state.md 提取待决策项（结构化）。

    合并持久化决策状态（memory/nsfc-decisions.json），
    approved/rejected 的不再返回。

    Returns:
        [{id, title, context, related_topic, status, source}]
    """
    import json as _json
    state_path = NSFC_DIR / "state.md"
    text = _read_text(state_path)

    # 加载持久化决策状态
    decisions_path = PROJECT_ROOT / "memory" / "nsfc-decisions.json"
    decided = {}
    if decisions_path.exists():
        try:
            decided = _json.loads(decisions_path.read_text(encoding="utf-8"))
        except Exception:
            decided = {}

    # 从 state.md 提取待决策行（⚠️/📌/待拍板/待讨论）
    pending = []
    pid_counter = 0
    for i, line in enumerate(text.split("\n"), 1):
        line_stripped = line.strip()
        if not any(mark in line_stripped for mark in ("⚠️", "⚠", "📌", "待.*拍板", "待.*讨论", "可推翻")):
            continue
        # 清理 markdown 符号
        clean = re.sub(r"^[✅⏳⚠️📌❌\-*\s]+", "", line_stripped).strip()
        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", clean)  # 去粗体
        if len(clean) < 5:
            continue

        pid_counter += 1
        pid = f"pd_{pid_counter:03d}"

        # 检测关联课题
        related_topic = ""
        for tid in _TOPIC_NAMES:
            if tid in clean or tid in line_stripped:
                related_topic = tid
                break

        # 持久化状态
        status = decided.get(pid, {}).get("status", "pending")
        if status in ("approved", "rejected"):
            continue  # 已决策的不显示

        pending.append({
            "id": pid,
            "title": clean[:80],
            "context": clean[:200],
            "related_topic": related_topic,
            "status": status,
            "source": f"state.md L{i}",
        })

    return pending


# ============================================================
# 自检
# ============================================================

def _self_check() -> None:
    """自检：验证各数据源可读。"""
    print("=" * 50)
    print("◐ project_reader 自检")
    print("=" * 50)

    print("\n[1/5] NSFC 项目目录...")
    if NSFC_DIR.exists():
        state = NSFC_DIR / "state.md"
        print(f"  ✓ 存在, state.md {'可读' if state.exists() else '缺失'}")
    else:
        print(f"  ○ 不存在: {NSFC_DIR}")

    print("\n[2/5] 解析 state.md...")
    dashboard = parse_nsfc_state()
    if dashboard["available"]:
        print(f"  ✓ Phase: {dashboard['phase'][:40]}")
        print(f"  ✓ BRAIN 区块: {dashboard['brain_count']}")
        print(f"  ✓ 待决策: {len(dashboard['pending_decisions'])} 项")
        print(f"  ✓ 风险: {len(dashboard['risks'])} 项")
        print(f"  ✓ 路线图: {len(dashboard['roadmap'])} 行")
    else:
        print(f"  ○ {dashboard.get('reason', '不可用')}")

    print("\n[3/5] 决策时间轴...")
    decisions = get_decisions(limit=5)
    print(f"  ✓ 提取 {len(decisions)} 条决策")
    if decisions:
        print(f"  示例: [{decisions[0]['date']}] {decisions[0]['title'][:40]}")

    print("\n[4/5] 申请书章节...")
    chapters = get_proposal_chapters()
    print(f"  ✓ {len(chapters)} 个章节")
    for c in chapters[:3]:
        print(f"    {c['topic']}: {c['title'][:30]} (v{c['version']}, {c['size_kb']}KB)")

    print("\n[5/5] 文献候选...")
    candidates = get_candidates()
    if candidates["available"]:
        print(f"  ✓ {candidates['total']} 篇候选, 日期 {candidates['date']}")
        if candidates["papers"]:
            top = candidates["papers"][0]
            print(f"  TOP1: {top['title'][:40]} (score={top['score']})")
    else:
        print("  ○ 无候选数据")

    print("\n✓ project_reader 自检通过")


if __name__ == "__main__":
    _self_check()
