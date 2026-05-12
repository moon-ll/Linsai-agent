#!/usr/bin/env python3
"""
session_manager.py — 会话管理器

用途：
    创建、加载、追加消息、列出、归档 LinSai-CoPilot 的会话。

用法示例：
    >>> from scripts.session_manager import create_session, append_message, list_sessions
    >>> sid, sdir = create_session("测试会话", "co-working")
    >>> msg = append_message(sid, "user", "你好，林赛")
    >>> for info in list_sessions():
    ...     print(info["session_id"], info["message_count"])

规范：
    - 仅使用 Python 3 标准库
    - 所有数据存放于 sessions/ 目录下
    - JSON 输出使用 ensure_ascii=False, indent=2
    - 时间戳统一 UTC ISO 格式
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def _get_project_root() -> Path:
    """返回项目根目录。"""
    return Path(__file__).parent.parent.resolve()


def _get_sessions_dir() -> Path:
    """返回 sessions 目录路径，若不存在则自动创建。"""
    d = _get_project_root() / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _get_archived_dir() -> Path:
    """返回归档目录路径，若不存在则自动创建。"""
    d = _get_sessions_dir() / "archived"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _now_utc() -> str:
    """返回当前 UTC ISO 时间字符串。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clean_topic(topic: str) -> str:
    """将主题中的非法字符替换为短横线。"""
    # 保留中文、英文、数字，其余替换为 -
    cleaned = re.sub(r"[^\w\u4e00-\u9fff]+", "-", topic.strip())
    # 去除首尾短横线，避免连续短横线
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned or "untitled"


def _write_json(path: Path, data: Any) -> None:
    """安全写入 JSON 文件。"""
    try:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"✗ 写入文件失败: {path} — {exc}")
        raise


def _read_json(path: Path) -> Any:
    """安全读取 JSON 文件。"""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"✗ 读取文件失败: {path} — {exc}")
        raise


def create_session(topic: str, mode: str = "co-working") -> tuple[str, Path]:
    """创建新会话，返回 (session_id, session_dir)。

    session_id 格式: YYYYMMDD-主题（主题中的非法字符替换为-）
    目录: sessions/YYYYMMDD-主题/
    初始化 messages.json（空列表）和 state.json。

    若会话目录已存在，则直接返回已有 session_id，不重复创建。
    """
    date_prefix = datetime.now(timezone.utc).strftime("%Y%m%d")
    cleaned = _clean_topic(topic)
    session_id = f"{date_prefix}-{cleaned}"
    session_dir = _get_sessions_dir() / session_id

    if session_dir.exists():
        print(f"⚠ 会话已存在，返回已有会话: {session_id}")
        return session_id, session_dir

    try:
        session_dir.mkdir(parents=True, exist_ok=True)

        # messages.json — 空消息列表
        messages_path = session_dir / "messages.json"
        _write_json(messages_path, [])

        # state.json — 会话元信息
        state = {
            "topic": topic,
            "mode": mode,
            "started_at": _now_utc(),
            "last_active": _now_utc(),
            "status": "active",
        }
        state_path = session_dir / "state.json"
        _write_json(state_path, state)

        # summary.md — 预留文件
        summary_path = session_dir / "summary.md"
        summary_path.write_text(f"# {topic}\n\n> 会话摘要预留位置\n", encoding="utf-8")

        print(f"✓ 会话创建成功: {session_id}")
        return session_id, session_dir
    except Exception as exc:  # noqa: BLE001
        print(f"✗ 创建会话失败: {exc}")
        raise


def load_session(session_id: str) -> tuple[list, dict]:
    """加载指定会话，返回 (messages列表, state字典)。

    messages.json 格式:
        [{"msg_id": "msg_001", "role": "user", ...}, ...]
    state.json 格式:
        {"topic": "...", "mode": "co-working", "started_at": "...",
         "last_active": "...", "status": "active"}

    若会话不存在，抛出 FileNotFoundError 并附带中文错误信息。
    """
    session_dir = _get_sessions_dir() / session_id

    if not session_dir.exists():
        err_msg = f"会话不存在: {session_id}"
        print(f"✗ {err_msg}")
        raise FileNotFoundError(err_msg)

    messages_path = session_dir / "messages.json"
    state_path = session_dir / "state.json"

    if not messages_path.exists() or not state_path.exists():
        err_msg = f"会话文件不完整: {session_id}"
        print(f"✗ {err_msg}")
        raise FileNotFoundError(err_msg)

    messages = _read_json(messages_path)
    state = _read_json(state_path)
    print(f"✓ 会话加载成功: {session_id}（共 {len(messages)} 条消息）")
    return messages, state


def append_message(
    session_id: str, role: str, content: str, mode: str = "co-working"
) -> dict:
    """向会话追加一条消息，自动写入 messages.json，更新 state.json 的 last_active。

    msg_id 自动生成（msg_001, msg_002... 基于当前消息数 + 1）
    返回追加的消息字典。
    """
    session_dir = _get_sessions_dir() / session_id

    if not session_dir.exists():
        err_msg = f"会话不存在，无法追加消息: {session_id}"
        print(f"✗ {err_msg}")
        raise FileNotFoundError(err_msg)

    messages_path = session_dir / "messages.json"
    state_path = session_dir / "state.json"

    try:
        messages: list = _read_json(messages_path)
        state: dict = _read_json(state_path)

        msg_id = f"msg_{len(messages) + 1:03d}"
        message = {
            "msg_id": msg_id,
            "role": role,
            "content": content,
            "timestamp": _now_utc(),
            "mode": mode,
        }
        messages.append(message)
        _write_json(messages_path, messages)

        state["last_active"] = _now_utc()
        _write_json(state_path, state)

        print(f"✓ 消息追加成功: {msg_id}")
        return message
    except Exception as exc:  # noqa: BLE001
        print(f"✗ 追加消息失败: {exc}")
        raise


def list_sessions(status: str = "all") -> list[dict]:
    """列出所有会话，返回会话元信息列表。

    status: "all" | "active" | "archived"
    每个元素:
        {"session_id": "...", "topic": "...", "mode": "...",
         "started_at": "...", "last_active": "...", "message_count": N}
    按 last_active 倒序排列。
    """
    sessions_dir = _get_sessions_dir()
    archived_dir = _get_archived_dir()
    result: list[dict] = []

    def _scan_dir(scan_dir: Path, is_archived: bool) -> None:
        if not scan_dir.exists():
            return
        for entry in scan_dir.iterdir():
            if not entry.is_dir():
                continue
            state_path = entry / "state.json"
            messages_path = entry / "messages.json"
            if not state_path.exists():
                continue
            try:
                state: dict = _read_json(state_path)
                msg_count = 0
                if messages_path.exists():
                    try:
                        msgs = _read_json(messages_path)
                        msg_count = len(msgs)
                    except Exception:  # noqa: S110
                        pass
                info = {
                    "session_id": entry.name,
                    "topic": state.get("topic", ""),
                    "mode": state.get("mode", ""),
                    "started_at": state.get("started_at", ""),
                    "last_active": state.get("last_active", ""),
                    "message_count": msg_count,
                    "status": "archived" if is_archived else state.get("status", "active"),
                }
                result.append(info)
            except Exception:  # noqa: S110
                continue

    if status in ("all", "active"):
        _scan_dir(sessions_dir, is_archived=False)
    if status in ("all", "archived"):
        _scan_dir(archived_dir, is_archived=True)

    result.sort(key=lambda x: x["last_active"], reverse=True)
    print(f"✓ 共检索到 {len(result)} 个会话（status={status}）")
    return result


def get_latest_session_id() -> Optional[str]:
    """返回最近活跃的会话 ID，无会话返回 None。"""
    sessions = list_sessions(status="active")
    if not sessions:
        print("○ 当前无活跃会话")
        return None
    latest = sessions[0]["session_id"]
    print(f"✓ 最近活跃会话: {latest}")
    return latest


def archive_session(session_id: str) -> bool:
    """将会话移动到 sessions/archived/ 目录，返回是否成功。"""
    sessions_dir = _get_sessions_dir()
    archived_dir = _get_archived_dir()
    src = sessions_dir / session_id

    if not src.exists():
        # 可能已经在 archived 里
        archived_src = archived_dir / session_id
        if archived_src.exists():
            print(f"⚠ 会话已处于归档状态: {session_id}")
            return True
        print(f"✗ 会话不存在，无法归档: {session_id}")
        return False

    dst = archived_dir / session_id
    if dst.exists():
        print(f"✗ 归档目标已存在，跳过: {session_id}")
        return False

    try:
        src.rename(dst)
        # 更新 state.json 中的 status
        state_path = dst / "state.json"
        if state_path.exists():
            state = _read_json(state_path)
            state["status"] = "archived"
            _write_json(state_path, state)
        print(f"✓ 会话归档成功: {session_id}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"✗ 归档会话失败: {exc}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("◐ 开始 session_manager 自检")
    print("=" * 50)

    # 1. 创建测试会话
    print("\n[1/6] 创建测试会话...")
    test_topic = "自检测试会话"
    sid, sdir = create_session(test_topic, mode="quick-check")
    assert sdir.exists(), "会话目录应已创建"
    assert (sdir / "messages.json").exists(), "messages.json 应已创建"
    assert (sdir / "state.json").exists(), "state.json 应已创建"
    print(f"   session_id = {sid}")

    # 重复创建应返回已有会话
    sid2, sdir2 = create_session(test_topic)
    assert sid2 == sid, "重复创建应返回已有 session_id"

    # 2. 追加消息
    print("\n[2/6] 追加消息...")
    msg1 = append_message(sid, "user", "你好，林赛", mode="quick-check")
    assert msg1["msg_id"] == "msg_001"
    assert msg1["role"] == "user"
    msg2 = append_message(sid, "assistant", "你好！有什么我可以帮你的？")
    assert msg2["msg_id"] == "msg_002"
    assert msg2["role"] == "assistant"
    msg3 = append_message(sid, "user", "帮我检查一下这个量纲对不对")
    assert msg3["msg_id"] == "msg_003"

    # 3. 列出会话
    print("\n[3/6] 列出会话...")
    all_sessions = list_sessions("all")
    active_sessions = list_sessions("active")
    assert any(s["session_id"] == sid for s in all_sessions), "all 应包含测试会话"
    assert any(s["session_id"] == sid for s in active_sessions), "active 应包含测试会话"
    assert all_sessions[0]["last_active"] >= all_sessions[-1]["last_active"], "应按 last_active 倒序"
    test_info = next(s for s in all_sessions if s["session_id"] == sid)
    assert test_info["message_count"] == 3, "消息数应为 3"

    # 4. 加载会话验证数据
    print("\n[4/6] 加载会话验证数据...")
    messages, state = load_session(sid)
    assert len(messages) == 3, "应加载 3 条消息"
    assert state["topic"] == test_topic, "主题应匹配"
    assert state["mode"] == "quick-check", "模式应匹配"
    assert messages[0]["content"] == "你好，林赛"
    assert messages[1]["content"] == "你好！有什么我可以帮你的？"

    # 5. 归档会话
    print("\n[5/6] 归档会话...")
    ok = archive_session(sid)
    assert ok, "归档应成功"
    assert not (_get_sessions_dir() / sid).exists(), "原目录应已移除"
    assert (_get_archived_dir() / sid).exists(), "归档目录应已存在"
    archived_sessions = list_sessions("archived")
    assert any(s["session_id"] == sid for s in archived_sessions), "archived 应包含测试会话"

    # 再次归档应返回 True（幂等）
    ok2 = archive_session(sid)
    assert ok2, "对已归档会话再次归档应返回 True"

    # 6. 清理测试数据
    print("\n[6/6] 清理测试数据...")
    archived_path = _get_archived_dir() / sid
    if archived_path.exists():
        import shutil
        shutil.rmtree(archived_path)
        print(f"   已删除归档目录: {archived_path.name}")

    # 验证清理
    assert not archived_path.exists(), "测试数据应已清理"

    print("\n" + "=" * 50)
    print("✓ 所有自检项目通过")
    print("=" * 50)
