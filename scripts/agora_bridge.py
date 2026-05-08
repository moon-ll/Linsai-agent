#!/usr/bin/env python3
"""
agora_bridge.py — Agora 群聊系统桥接模块

用途：
    将 LinSai-CoPilot 的当前研究上下文导出为 Agora（persona-discussion）
    兼容的会话格式，支持"召唤历史人物群聊"功能。

用法示例：
    >>> from agora_bridge import export_to_agora, import_from_agora
    >>> export_to_agora("20260508-固体HHG", ["费曼", "狄拉克"])
    >>> import_from_agora("agora_sessions/20260508-固体HHG-群聊.json")

注意：
    本模块为协议预留层。Agora 系统的具体消息格式需根据实际对接项目调整。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).parent.parent.resolve()
AGORA_DIR = PROJECT_ROOT / "sessions" / "agora_exports"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any = None) -> Any:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default if default is not None else {}


def export_to_agora(
    session_id: str,
    personas: list[str],
    topic: str = "",
    output_name: str = "",
) -> Path:
    """将当前会话上下文导出为 Agora 兼容格式。

    参数:
        session_id: 当前 CoPilot 会话 ID
        personas: 要召唤的历史人物列表，如 ["费曼", "狄拉克"]
        topic: 讨论主题（默认使用原会话主题）
        output_name: 输出文件名（默认自动生成）

    返回:
        导出的 JSON 文件路径
    """
    AGORA_DIR.mkdir(parents=True, exist_ok=True)

    # 读取原会话
    session_path = PROJECT_ROOT / "sessions" / session_id
    messages_path = session_path / "messages.json"
    state_path = session_path / "state.json"

    messages = _load_json(messages_path, default=[])
    state = _load_json(state_path, default={})

    if isinstance(messages, dict):
        messages = messages.get("messages", [])

    if not topic:
        topic = state.get("topic", "未命名讨论")

    # 构建 Agora 兼容格式
    export_data = {
        "export_version": "1.0",
        "source": "LinSai-CoPilot",
        "exported_at": _now_utc(),
        "original_session": session_id,
        "topic": topic,
        "mode": "agora",
        "invited_personas": personas,
        "context_summary": _build_context_summary(messages, state),
        "messages": [
            {
                "role": m.get("role", "user"),
                "content": m.get("content", ""),
                "timestamp": m.get("timestamp", ""),
                "sender": "林赛" if m.get("role") == "assistant" else "用户",
            }
            for m in messages[-10:]  # 导出最近10条作为上下文
            if m.get("content")
        ],
        "system_prompt_hint": (
            f"当前讨论主题：{topic}。"
            "用户正在与林赛（Lin Sai，强场超快光学PI）进行1对1协作，"
            f"现在邀请 {', '.join(personas)} 加入讨论。"
            "请基于各自的历史人物视角参与对话。"
        ),
    }

    if not output_name:
        safe_topic = "".join(c if c.isalnum() or c in "_-" else "_" for c in topic)[:30]
        output_name = f"agora_{session_id}_{safe_topic}.json"

    output_path = AGORA_DIR / output_name
    output_path.write_text(
        json.dumps(export_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"✓ Agora 导出完成: {output_path.name}")
    return output_path


def import_from_agora(agora_file: Path | str) -> dict:
    """从 Agora 导出文件读取讨论结果。

    返回包含 discussion_summary 和 key_insights 的字典，
    可用于回流到 LinSai-CoPilot 的记忆系统。
    """
    path = Path(agora_file)
    data = _load_json(path, default={})

    result = {
        "topic": data.get("topic", ""),
        "personas": data.get("invited_personas", []),
        "summary": data.get("discussion_summary", "未提供摘要"),
        "key_insights": data.get("key_insights", []),
        "imported_at": _now_utc(),
    }
    print(f"✓ Agora 导入完成: {path.name}")
    return result


def _build_context_summary(messages: list, state: dict) -> str:
    """从会话构建简短的上下文摘要。"""
    topic = state.get("topic", "未命名")
    msg_count = len(messages)
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    last_user = user_msgs[-1] if user_msgs else ""
    return (
        f"主题：{topic}，共 {msg_count} 条消息。"
        f"用户最新输入：{last_user[:100]}..."
    )


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("◐ Agora 桥接模块自检")
    print("=" * 50)

    # 1. 创建测试会话数据
    test_session_dir = PROJECT_ROOT / "sessions" / "20260508-Agora测试"
    test_session_dir.mkdir(parents=True, exist_ok=True)

    test_messages = [
        {"msg_id": "msg_001", "role": "user", "content": "我在研究固体HHG中的相位匹配问题", "timestamp": "2026-05-08T09:00:00Z", "mode": "co-working"},
        {"msg_id": "msg_002", "role": "assistant", "content": "相位匹配在固体HHG中确实是个关键问题。你考虑过多晶取向的影响吗？", "timestamp": "2026-05-08T09:01:00Z", "mode": "co-working"},
    ]
    (test_session_dir / "messages.json").write_text(
        json.dumps(test_messages, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (test_session_dir / "state.json").write_text(
        json.dumps({"topic": "固体HHG相位匹配", "mode": "co-working", "started_at": "2026-05-08T09:00:00Z"}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # 2. 导出到 Agora
    print("\n[1/3] 导出到 Agora...")
    export_path = export_to_agora(
        "20260508-Agora测试",
        personas=["费曼", "狄拉克"],
        topic="固体HHG中的相位匹配",
    )
    assert export_path.exists(), "导出文件应已创建"
    print(f"   导出路径: {export_path}")

    # 3. 验证导出格式
    print("\n[2/3] 验证导出格式...")
    exported = _load_json(export_path)
    assert exported["source"] == "LinSai-CoPilot"
    assert "费曼" in exported["invited_personas"]
    assert "狄拉克" in exported["invited_personas"]
    assert len(exported["messages"]) == 2
    print("   ✓ 格式正确")

    # 4. 导入（模拟）
    print("\n[3/3] 导入讨论结果...")
    result = import_from_agora(export_path)
    assert result["topic"] == "固体HHG中的相位匹配"
    assert result["personas"] == ["费曼", "狄拉克"]
    print("   ✓ 导入成功")

    # 5. 清理
    print("\n[清理] 删除测试数据...")
    import shutil
    if test_session_dir.exists():
        shutil.rmtree(test_session_dir)
    for f in AGORA_DIR.glob("agora_*.json"):
        f.unlink()
    print("   ✓ 测试数据已清理")

    print("\n" + "=" * 50)
    print("✓ Agora 桥接模块自检通过")
    print("=" * 50)
