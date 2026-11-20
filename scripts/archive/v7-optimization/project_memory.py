#!/usr/bin/env python3
"""课题记忆系统 — 对话存档、记忆片段、决策日志、风险登记。

为每个课题维护三层记忆结构：
1. 对话全文存档（conversations/）：会话结束时自动保存完整对话
2. 记忆片段（snippets/）：课题级的关键决策/用户偏好/重要发现
3. 长期记忆文件（PROJECT-MEMORY.md，≤100行核心记忆）：由 project_manager
   生成骨架，本模块负责动态维护（决策追加、进展更新、知识库要点替换）

存储结构:
    projects/{project_id}/memory/
    ├── conversations/          # 对话全文存档
    │   └── 2026-06-27-unit2-planning.json
    ├── decisions.md            # 决策日志（结构化 Markdown）
    ├── risks.md                # 风险登记簿
    └── snippets/               # 课题级记忆片段
        └── *.md

用法示例:
    >>> from project_memory import save_conversation, create_snippet, add_decision
    >>> from project_manager import create_project
    >>> pid, _ = create_project("固体HHG相位匹配研究", goal="建立理论模型")
    >>> save_conversation(pid, "session_001", messages, topic="unit1-planning")
    >>> create_snippet(pid, "驱动参数", "800nm/30fs钛宝石激光", importance=4)
    >>> add_decision(pid, "驱动激光选型", rationale="选用800nm/30fs")
    >>> ctx = get_project_context(pid)  # 注入到 system_prompt
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc as _now_utc, load_json as _read_json, save_json as _write_json, safe_filename

_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from project_manager import (
    _project_dir,
    get_project,
    append_to_project_memory,
    get_project_memory,
    update_project_memory,
)

# 懒加载 unit_manager（避免循环导入）
from common import lazy_load as _lazy_load
_try_unit_manager = _lazy_load("unit_manager")


# ---------------------------------------------------------------------------
# 目录辅助
# ---------------------------------------------------------------------------

def get_memory_dir(project_id: str) -> Path:
    """返回课题记忆库根目录。

    自动创建 conversations/ 和 snippets/ 子目录。
    """
    mdir = _project_dir(project_id) / "memory"
    (mdir / "conversations").mkdir(parents=True, exist_ok=True)
    (mdir / "snippets").mkdir(parents=True, exist_ok=True)
    return mdir


# ---------------------------------------------------------------------------
# 对话全文存档
# ---------------------------------------------------------------------------

def save_conversation(project_id: str, session_id: str, messages: list,
                      topic: str = "", mode: str = "co-working") -> str:
    """保存对话全文到课题记忆库。

    1. 生成文件名: {日期}-{主题}.json
    2. 内容: {session_id, topic, mode, saved_at, message_count, messages: [...]}
    3. 存储到 conversations/ 目录

    返回文件路径（字符串）。
    """
    conv_dir = get_memory_dir(project_id) / "conversations"
    conv_dir.mkdir(parents=True, exist_ok=True)

    date_str = _now_utc()[:10]  # YYYY-MM-DD
    safe_topic = safe_filename(topic) if topic else "conversation"
    filename = f"{date_str}-{safe_topic}.json"

    # 同日同主题去重：追加序号
    path = conv_dir / filename
    counter = 2
    while path.exists():
        filename = f"{date_str}-{safe_topic}-{counter}.json"
        path = conv_dir / filename
        counter += 1

    data = {
        "session_id": session_id,
        "topic": topic,
        "mode": mode,
        "saved_at": _now_utc(),
        "message_count": len(messages),
        "messages": messages,
    }
    _write_json(path, data)
    print(f"✓ 对话已存档: {filename}（{len(messages)} 条消息）")
    return str(path)


def list_conversations(project_id: str, limit: int = 20) -> List[dict]:
    """列出课题的对话存档，按时间倒序。"""
    conv_dir = get_memory_dir(project_id) / "conversations"
    if not conv_dir.exists():
        return []

    results: List[dict] = []
    for path in sorted(conv_dir.glob("*.json"), reverse=True):
        data = _read_json(path, {})
        if not data:
            continue
        results.append({
            "filename": path.name,
            "session_id": data.get("session_id", ""),
            "topic": data.get("topic", ""),
            "mode": data.get("mode", ""),
            "saved_at": data.get("saved_at", ""),
            "message_count": data.get("message_count", 0),
            "path": str(path),
        })
        if len(results) >= limit:
            break
    return results


def search_conversations(project_id: str, query: str, limit: int = 5) -> List[dict]:
    """在对话存档中搜索（关键词匹配）。

    搜索范围：topic + 每条消息的 content。
    返回结果按匹配次数倒序。
    """
    conv_dir = get_memory_dir(project_id) / "conversations"
    if not conv_dir.exists():
        return []

    q = query.lower()
    results: List[dict] = []

    for path in sorted(conv_dir.glob("*.json"), reverse=True):
        data = _read_json(path, {})
        if not data:
            continue

        # 构建可搜索文本
        searchable_parts: List[str] = [data.get("topic", "").lower()]
        messages = data.get("messages", [])
        for msg in messages:
            if isinstance(msg, dict):
                searchable_parts.append(str(msg.get("content", "")).lower())
            elif isinstance(msg, str):
                searchable_parts.append(msg.lower())
        searchable = " ".join(searchable_parts)

        if q not in searchable:
            continue

        match_count = searchable.count(q)

        # 提取匹配上下文片段
        snippet = ""
        for msg in messages:
            content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
            low = content.lower()
            if q in low:
                idx = low.find(q)
                start = max(0, idx - 30)
                end = min(len(content), idx + len(query) + 30)
                snippet = ("..." if start > 0 else "") + content[start:end] + ("..." if end < len(content) else "")
                break

        results.append({
            "filename": path.name,
            "topic": data.get("topic", ""),
            "saved_at": data.get("saved_at", ""),
            "message_count": data.get("message_count", 0),
            "match_count": match_count,
            "snippet": snippet,
            "path": str(path),
        })

    results.sort(key=lambda x: -x["match_count"])
    return results[:limit]


# ---------------------------------------------------------------------------
# 课题级记忆片段
# ---------------------------------------------------------------------------

def _parse_snippet(text: str) -> dict:
    """解析记忆片段文件的 frontmatter 和正文。"""
    result = {
        "id": "",
        "trigger": "",
        "source": "",
        "importance": 3,
        "project_id": "",
        "created_at": "",
        "summary": "",
    }
    if not text.startswith("---"):
        # 无 frontmatter，全部作为摘要
        result["summary"] = text.strip()
        return result

    parts = text.split("---", 2)
    if len(parts) < 3:
        result["summary"] = text.strip()
        return result

    fm_text = parts[1]
    result["summary"] = parts[2].strip()

    for line in fm_text.strip().split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if k == "importance":
            try:
                result["importance"] = int(v)
            except ValueError:
                pass
        elif k in result:
            result[k] = v

    return result


def create_snippet(project_id: str, trigger: str, summary: str,
                   source: str = "", importance: int = 3) -> str:
    """创建课题级记忆片段。

    1. 生成文件: snippets/{时间戳}-{trigger安全名}.md
    2. 内容: frontmatter (id, trigger, source, importance, project_id, created_at) + 正文
    3. 返回 snippet_id
    """
    if not 1 <= importance <= 5:
        raise ValueError("importance 必须在 1-5 之间")

    snip_dir = get_memory_dir(project_id) / "snippets"
    snip_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    safe_trigger = safe_filename(trigger)[:20] or "snippet"
    filename = f"{ts}-{safe_trigger}.md"
    sid = f"prj_snippet_{ts}"
    path = snip_dir / filename

    frontmatter = {
        "id": sid,
        "trigger": trigger,
        "source": source,
        "importance": importance,
        "project_id": project_id,
        "created_at": _now_utc(),
    }
    yaml_lines = ["---"] + [f"{k}: {v}" for k, v in frontmatter.items()] + ["---"]
    content = "\n".join(yaml_lines) + f"\n\n{summary}\n"
    path.write_text(content, encoding="utf-8")
    print(f"✓ 课题记忆片段已创建: {filename}")
    return sid


def search_snippets(project_id: str, query: str, limit: int = 5) -> List[dict]:
    """搜索课题记忆片段（关键词匹配）。

    匹配 frontmatter 中的关键词权重更高。按 importance 倒序排列。
    """
    snip_dir = get_memory_dir(project_id) / "snippets"
    if not snip_dir.exists():
        return []

    q = query.lower()
    results: List[dict] = []

    for path in sorted(snip_dir.glob("*.md"), reverse=True):
        text = path.read_text(encoding="utf-8")
        low = text.lower()
        if q not in low:
            continue

        # frontmatter 匹配加权
        weight = 1
        if "---" in low:
            fm_parts = low.split("---", 2)
            if len(fm_parts) >= 2 and q in fm_parts[1]:
                weight = 3

        snippet = _parse_snippet(text)
        snippet["weight"] = weight
        snippet["path"] = str(path)
        results.append(snippet)

    results.sort(key=lambda x: (-x.get("importance", 3), -x.get("weight", 1)))
    return results[:limit]


def list_snippets(project_id: str, limit: int = 20) -> List[dict]:
    """列出课题记忆片段，按创建时间倒序。"""
    snip_dir = get_memory_dir(project_id) / "snippets"
    if not snip_dir.exists():
        return []

    results: List[dict] = []
    for path in sorted(snip_dir.glob("*.md"), reverse=True):
        text = path.read_text(encoding="utf-8")
        snippet = _parse_snippet(text)
        snippet["path"] = str(path)
        results.append(snippet)
        if len(results) >= limit:
            break
    return results


# ---------------------------------------------------------------------------
# 决策日志
# ---------------------------------------------------------------------------

def add_decision(project_id: str, title: str, rationale: str = "",
                 alternatives: str = "", unit_id: str = "") -> str:
    """添加决策日志条目。

    写入 decisions.md，格式：
        ## {title}
        - 时间: {timestamp}
        - 单元: {unit_id}
        - 决策: {rationale}
        - 备选方案: {alternatives}

    同时追加到 PROJECT-MEMORY.md 的"关键决策"区域。

    返回 decision_id。
    """
    decisions_path = get_memory_dir(project_id) / "decisions.md"

    # 初始化文件头
    if not decisions_path.exists():
        decisions_path.write_text("# 决策日志\n\n", encoding="utf-8")

    timestamp = _now_utc()
    decision_id = f"decision_{timestamp.replace('-', '').replace(':', '').replace('T', '').replace('Z', '')}"

    entry = (
        f"## {title}\n"
        f"- 时间: {timestamp}\n"
        f"- 单元: {unit_id or '未指定'}\n"
        f"- 决策: {rationale or '（未记录）'}\n"
        f"- 备选方案: {alternatives or '（无）'}\n"
    )

    # 追加到 decisions.md
    content = decisions_path.read_text(encoding="utf-8")
    content += entry + "\n"
    decisions_path.write_text(content, encoding="utf-8")

    # 追加到 PROJECT-MEMORY.md 的"关键决策"区域
    mem_line = f"- {title}"
    if rationale:
        mem_line += f": {rationale[:60]}"
    append_to_project_memory(project_id, "关键决策", mem_line)

    print(f"✓ 决策已记录: {title}")
    return decision_id


def get_decisions(project_id: str) -> str:
    """读取决策日志全文。"""
    decisions_path = get_memory_dir(project_id) / "decisions.md"
    if not decisions_path.exists():
        return ""
    return decisions_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 风险登记簿
# ---------------------------------------------------------------------------

def add_risk_record(project_id: str, description: str, severity: str = "medium",
                    mitigation: str = "", unit_id: str = "") -> str:
    """添加风险记录到 risks.md。

    格式：
        ## {description}
        - 时间: {timestamp}
        - 严重程度: {severity_label} ({severity})
        - 单元: {unit_id}
        - 缓解措施: {mitigation}

    返回 risk_id。
    """
    risks_path = get_memory_dir(project_id) / "risks.md"

    # 初始化文件头
    if not risks_path.exists():
        risks_path.write_text("# 风险登记簿\n\n", encoding="utf-8")

    timestamp = _now_utc()
    risk_id = f"risk_{timestamp.replace('-', '').replace(':', '').replace('T', '').replace('Z', '')}"

    severity_labels = {"low": "低", "medium": "中", "high": "高", "critical": "严重"}
    severity_label = severity_labels.get(severity, severity)

    entry = (
        f"## {description}\n"
        f"- 时间: {timestamp}\n"
        f"- 严重程度: {severity_label} ({severity})\n"
        f"- 单元: {unit_id or '未指定'}\n"
        f"- 缓解措施: {mitigation or '（待制定）'}\n"
    )

    # 追加到 risks.md
    content = risks_path.read_text(encoding="utf-8")
    content += entry + "\n"
    risks_path.write_text(content, encoding="utf-8")

    print(f"✓ 风险已记录: {description[:40]}")
    return risk_id


def get_risks(project_id: str) -> str:
    """读取风险登记簿全文。"""
    risks_path = get_memory_dir(project_id) / "risks.md"
    if not risks_path.exists():
        return ""
    return risks_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# PROJECT-MEMORY.md 动态维护
# ---------------------------------------------------------------------------

def update_progress_in_memory(project_id: str, unit_id: str, unit_title: str,
                              status: str, summary: str = "") -> None:
    """更新 PROJECT-MEMORY.md 的课题进展区域。

    - status="completed": 追加 [✓] 行
    - status="active":    追加 [►] 行
    - status="planning":  追加 [○] 行
    """
    status_markers = {
        "completed": "[✓]",
        "active": "[►]",
        "planning": "[○]",
    }
    marker = status_markers.get(status, "[○]")

    line = f"- {marker} {unit_title}"
    if unit_id:
        line += f" ({unit_id})"
    if summary:
        line += f": {summary}"

    append_to_project_memory(project_id, "课题进展", line)
    print(f"✓ 课题进展已更新: {marker} {unit_title}")


def update_kb_summary_in_memory(project_id: str, kb_summary: str) -> None:
    """更新 PROJECT-MEMORY.md 的"知识库要点"区域。

    替换该区域的全部内容为 kb_summary（非追加）。
    """
    content = get_project_memory(project_id)
    if not content:
        # PROJECT-MEMORY.md 不存在，尝试初始化
        from project_manager import _init_project_memory
        try:
            proj = get_project(project_id)
            _init_project_memory(project_id, proj.get("name", "未命名课题"), proj.get("goal", ""))
            content = get_project_memory(project_id)
        except FileNotFoundError:
            print(f"✗ 课题不存在: {project_id}")
            return

    lines = content.split("\n")
    new_lines: List[str] = []
    in_kb_section = False
    kb_replaced = False

    for line in lines:
        if line.strip() == "## 知识库要点":
            in_kb_section = True
            new_lines.append(line)
            new_lines.append(kb_summary)
            kb_replaced = True
            continue
        if in_kb_section:
            if line.startswith("## "):
                # 进入下一个区域，停止替换
                in_kb_section = False
                new_lines.append(line)
            else:
                # 跳过旧内容
                continue
        else:
            new_lines.append(line)

    if not kb_replaced:
        new_lines.append("")
        new_lines.append("## 知识库要点")
        new_lines.append(kb_summary)

    new_content = "\n".join(new_lines)
    update_project_memory(project_id, new_content)
    print("✓ 知识库要点已更新")


# ---------------------------------------------------------------------------
# 上下文注入
# ---------------------------------------------------------------------------

def get_project_context(project_id: str) -> str:
    """获取课题上下文摘要（用于注入到对话 system_prompt）。

    包含：
    - PROJECT-MEMORY.md 全文（≤100行核心记忆）
    - 最近 3 条记忆片段
    - 当前单元信息（如果有）

    返回文本不超过 2000 字符。
    """
    parts: List[str] = []

    # 1. PROJECT-MEMORY.md 全文
    mem_content = get_project_memory(project_id)
    if mem_content:
        parts.append("[课题核心记忆]")
        parts.append(mem_content.rstrip())

    # 2. 最近 3 条记忆片段
    snippets = list_snippets(project_id, limit=3)
    if snippets:
        parts.append("")
        parts.append("[近期记忆片段]")
        for i, s in enumerate(snippets, 1):
            trigger = s.get("trigger", "")
            summary_text = s.get("summary", "")[:80]
            importance = s.get("importance", 3)
            parts.append(f"{i}. [{importance}★] {trigger}: {summary_text}")

    # 3. 当前单元信息
    try:
        project = get_project(project_id)
        current_unit_id = project.get("current_unit")
        if current_unit_id and _try_unit_manager is not None:
            unit = _try_unit_manager.get_unit(current_unit_id)
            if unit:
                parts.append("")
                parts.append("[当前单元]")
                parts.append(f"- 单元: {unit.get('title', current_unit_id)} ({current_unit_id})")
                parts.append(f"- 状态: {unit.get('status', 'unknown')}")
                if unit.get("description"):
                    parts.append(f"- 描述: {unit['description'][:80]}")
    except FileNotFoundError:
        pass

    context = "\n".join(parts)

    # 截断到 2000 字符
    if len(context) > 2000:
        context = context[:1997] + "..."

    return context


# ---------------------------------------------------------------------------
# 统计
# ---------------------------------------------------------------------------

def get_memory_stats(project_id: str) -> dict:
    """获取记忆库统计：对话数/片段数/决策数/风险数/记忆文件行数。"""
    mdir = get_memory_dir(project_id)

    # 对话数
    conv_dir = mdir / "conversations"
    conv_count = len(list(conv_dir.glob("*.json"))) if conv_dir.exists() else 0

    # 片段数
    snip_dir = mdir / "snippets"
    snip_count = len(list(snip_dir.glob("*.md"))) if snip_dir.exists() else 0

    # 决策数（统计 decisions.md 中 "## " 开头的行，排除文件头 "# "）
    decisions_path = mdir / "decisions.md"
    decision_count = 0
    if decisions_path.exists():
        decision_text = decisions_path.read_text(encoding="utf-8")
        decision_count = len(re.findall(r"^## ", decision_text, re.MULTILINE))

    # 风险数
    risks_path = mdir / "risks.md"
    risk_count = 0
    if risks_path.exists():
        risk_text = risks_path.read_text(encoding="utf-8")
        risk_count = len(re.findall(r"^## ", risk_text, re.MULTILINE))

    # 记忆文件行数
    mem_path = _project_dir(project_id) / "PROJECT-MEMORY.md"
    mem_lines = 0
    if mem_path.exists():
        mem_lines = len(mem_path.read_text(encoding="utf-8").split("\n"))

    return {
        "project_id": project_id,
        "conversation_count": conv_count,
        "snippet_count": snip_count,
        "decision_count": decision_count,
        "risk_count": risk_count,
        "memory_file_lines": mem_lines,
    }


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """自检：创建课题→保存对话→创建片段→添加决策→更新进展→获取上下文→清理。"""
    print("=" * 50)
    print("◐ project_memory 自检")
    print("=" * 50)

    from project_manager import create_project, delete_project

    print("\n[1/9] 创建测试课题...")
    pid, _ = create_project("记忆系统自检课题", goal="验证课题记忆系统完整链路")
    print(f"  课题ID: {pid}")

    print("\n[2/9] 保存测试对话 + 列出 + 搜索...")
    messages = [
        {"role": "user", "content": "林赛，帮我设计固体HHG实验方案"},
        {"role": "assistant", "content": "好的，我们先明确驱动激光参数。你的样品是什么？"},
        {"role": "user", "content": "驱动波长800nm，脉宽30fs，样品是MgO晶体"},
        {"role": "assistant", "content": "800nm/30fs是经典配置，MgO的带隙约7.8eV，适合HHG研究。"},
    ]
    conv_path = save_conversation(pid, "test_session_001", messages,
                                  topic="unit1-planning", mode="co-working")
    print(f"  存档文件: {Path(conv_path).name}")

    convs = list_conversations(pid)
    print(f"  对话存档数: {len(convs)}")
    assert len(convs) == 1, f"期望 1 条对话，实际 {len(convs)}"

    search_results = search_conversations(pid, "800nm")
    print(f"  搜索 '800nm' 返回: {len(search_results)} 条")
    assert len(search_results) >= 1, "搜索应至少返回 1 条结果"
    print(f"  匹配片段: {search_results[0]['snippet'][:50]}...")

    print("\n[3/9] 创建 2 个记忆片段 + 列出 + 搜索...")
    sid1 = create_snippet(pid, "驱动参数", "800nm/30fs钛宝石激光系统，经典HHG驱动配置",
                          source="test_session_001", importance=4)
    sid2 = create_snippet(pid, "样品选型", "MgO晶体，带隙约7.8eV，适合固体HHG研究",
                          source="test_session_001", importance=3)
    print(f"  片段ID: {sid1}, {sid2}")

    all_snippets = list_snippets(pid)
    print(f"  片段总数: {len(all_snippets)}")
    assert len(all_snippets) == 2, f"期望 2 个片段，实际 {len(all_snippets)}"

    snip_results = search_snippets(pid, "驱动")
    print(f"  搜索 '驱动' 返回: {len(snip_results)} 条")
    assert len(snip_results) >= 1, "片段搜索应至少返回 1 条结果"
    print(f"  最高权重片段: {snip_results[0]['trigger']} (importance={snip_results[0]['importance']})")

    print("\n[4/9] 添加 2 个决策...")
    did1 = add_decision(pid, "驱动激光选型",
                        rationale="选用800nm/30fs钛宝石激光系统",
                        alternatives="考虑过400nm/10fs但平均功率不足",
                        unit_id="unit-1")
    did2 = add_decision(pid, "样品温度方案",
                        rationale="室温开始测量，后续降温至77K对比",
                        unit_id="unit-1")
    print(f"  决策ID: {did1}, {did2}")

    decisions_text = get_decisions(pid)
    print(f"  决策日志行数: {len(decisions_text.splitlines())}")
    assert "驱动激光选型" in decisions_text, "决策日志应包含 '驱动激光选型'"
    assert "样品温度方案" in decisions_text, "决策日志应包含 '样品温度方案'"
    print(f"  决策日志内容预览:\n{decisions_text[:200]}...")

    print("\n[5/9] 添加 1 个风险...")
    rid1 = add_risk_record(pid, "MgO样品损伤阈值未知",
                           severity="high",
                           mitigation="先进行低功率预实验，逐步增加强度",
                           unit_id="unit-1")
    print(f"  风险ID: {rid1}")

    risks_text = get_risks(pid)
    print(f"  风险登记簿行数: {len(risks_text.splitlines())}")
    assert "MgO样品损伤阈值" in risks_text, "风险登记簿应包含 'MgO样品损伤阈值'"
    assert "高" in risks_text, "风险登记簿应包含严重程度 '高'"
    print(f"  风险登记簿内容预览:\n{risks_text[:200]}...")

    print("\n[6/9] 更新进展 + 更新知识库要点...")
    update_progress_in_memory(pid, "unit-1", "单元1：实验系统搭建",
                              status="completed", summary="光路搭建完成，驱动参数已确定")
    update_progress_in_memory(pid, "unit-2", "单元2：参数优化与数据采集",
                              status="active", summary="正在调试相位匹配条件")
    update_kb_summary_in_memory(pid, "已收录3篇固体HHG论文，1个MgO材料数据条目")

    mem_content = get_project_memory(pid)
    assert "[✓]" in mem_content, "记忆文件应包含已完成标记 [✓]"
    assert "[►]" in mem_content, "记忆文件应包含进行中标记 [►]"
    assert "已收录3篇固体HHG论文" in mem_content, "记忆文件应包含知识库要点更新"
    print(f"  PROJECT-MEMORY.md 行数: {len(mem_content.splitlines())}")
    print(f"  内容预览:\n{mem_content[:300]}...")

    print("\n[7/9] 获取上下文摘要...")
    context = get_project_context(pid)
    print(f"  上下文长度: {len(context)} 字符")
    assert len(context) <= 2000, f"上下文应 ≤2000 字符，实际 {len(context)}"
    assert "[课题核心记忆]" in context, "上下文应包含 [课题核心记忆]"
    assert "[近期记忆片段]" in context, "上下文应包含 [近期记忆片段]"
    print("-" * 40)
    print(context)
    print("-" * 40)

    print("\n[8/9] 获取统计信息...")
    stats = get_memory_stats(pid)
    print(f"  对话数:   {stats['conversation_count']}")
    print(f"  片段数:   {stats['snippet_count']}")
    print(f"  决策数:   {stats['decision_count']}")
    print(f"  风险数:   {stats['risk_count']}")
    print(f"  记忆行数: {stats['memory_file_lines']}")
    assert stats["conversation_count"] == 1, f"期望 1 条对话，实际 {stats['conversation_count']}"
    assert stats["snippet_count"] == 2, f"期望 2 个片段，实际 {stats['snippet_count']}"
    assert stats["decision_count"] == 2, f"期望 2 条决策，实际 {stats['decision_count']}"
    assert stats["risk_count"] == 1, f"期望 1 条风险，实际 {stats['risk_count']}"
    assert stats["memory_file_lines"] > 0, "记忆文件行数应 > 0"

    print("\n[9/9] 删除测试课题...")
    delete_project(pid, confirm=True)

    print("\n" + "=" * 50)
    print("✓ project_memory 自检全部通过")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="课题记忆系统")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
