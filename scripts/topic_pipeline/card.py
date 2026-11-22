# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——课题卡（topic-card.md）渲染与解析。

课题卡是每个课题的身份证：一句话问题 + 来源 + 状态 + 关联。头域用
`- 键: 值` 列表形式（与 v7 00_proposal-brief.md 的风格一致，可读可解析）。

用法示例：
    from topic_pipeline.card import render_card, parse_card
    md = render_card(title="...", topic_id="...", fields={...})
    info = parse_card(path)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

STAGE_LABELS = {
    "questions": "问题候选",
    "kickoff": "深研中",
    "ready": "启动包就绪（待人工启动）",
    "active": "正式研究中",
    "archive": "已归档",
}


def render_card(
    title: str,
    topic_id: str,
    stage: str,
    problem: str = "",
    source: str = "",
    related: Optional[list] = None,
    migrated_from: str = "",
    knowledge_card: str = "",
) -> str:
    """渲染课题卡 Markdown。"""
    rel = "、".join(related) if related else "（暂无，显式声明）"
    lines = [
        f"# 课题卡：{title}",
        "",
        f"- 课题 ID: {topic_id}",
        f"- 状态: {stage}（{STAGE_LABELS.get(stage, stage)}）",
        f"- 来源: {source or '人工注册'}",
        f"- 一句话问题: {problem}",
        f"- 关联课题: {rel}",
    ]
    if migrated_from:
        lines.append(f"- 迁移自: {migrated_from}")
    lines += ["", "## 知识卡摘要", ""]
    lines.append(knowledge_card.strip() or "（待周末输入链知识卡注入）")
    lines += ["", "## 状态流转", ""]
    return "\n".join(lines) + "\n"


def append_card_event(path: Path, event: str) -> None:
    """在课题卡「状态流转」节追加一行事件记录。"""
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    marker = "## 状态流转"
    stamp = event.strip()
    if marker in text:
        text = text.rstrip("\n") + f"\n- {stamp}\n"
    else:
        text = text.rstrip("\n") + f"\n\n{marker}\n\n- {stamp}\n"
    path.write_text(text, encoding="utf-8")


def parse_card(path: Path) -> Dict[str, Any]:
    """解析课题卡头域（`- 键: 值` 列表），返回字段字典。"""
    fields: Dict[str, Any] = {}
    if not path.exists():
        return fields
    keymap = {
        "课题 ID": "topic_id",
        "状态": "stage",
        "来源": "source",
        "一句话问题": "problem",
        "关联课题": "related_raw",
        "迁移自": "migrated_from",
    }
    for line in path.read_text(encoding="utf-8").splitlines():
        m = line.strip()
        if not m.startswith("- ") or ":" not in m and "：" not in m:
            continue
        body = m[2:]
        sep = ":" if ":" in body else "："
        k, _, v = body.partition(sep)
        k = k.strip()
        if k in keymap:
            fields[keymap[k]] = v.strip()
    if fields.get("related_raw"):
        rel = fields["related_raw"]
        fields["related"] = [] if "暂无" in rel else [x.strip() for x in rel.replace("、", ",").split(",") if x.strip()]
    return fields
