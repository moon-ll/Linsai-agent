#!/usr/bin/env python3
"""kanban_reader.py — hermes kanban.db SQLite 读写层。

让 CoPilot Web 界面能读取/创建/更新 hermes 的 kanban.db 任务，
实现三端统一架构的任务看板桥接。

hermes kanban.db 位置：~/.hermes/kanban.db（SQLite WAL 模式）
CoPilot 通过 sqlite3 标准库以只读模式（mode=ro）查询，写入时用 WAL 模式。

状态映射（hermes 9 态 → CoPilot 4 态）：
    triage/todo/scheduled/ready → backlog
    running/review              → active
    blocked                     → paused
    done/archived               → completed

用法示例：
    >>> from kanban_reader import list_tasks, get_task, create_task
    >>> tasks = list_tasks()  # 返回 CoPilot 格式的任务列表
    >>> task = get_task("t_c620be93")
    >>> tid = create_task("测试任务", assignee="copilot")

规范：仅标准库，PROJECT_ROOT 推导，JSON ensure_ascii=False。
"""

import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ========== 路径配置 ==========
KANBAN_DB_PATH = Path.home() / ".hermes" / "kanban.db"

# ========== 状态映射 ==========
# hermes 9 态 → CoPilot 4 态
_HERMES_TO_COPILOT = {
    "triage": "backlog",
    "todo": "backlog",
    "scheduled": "backlog",
    "ready": "backlog",
    "running": "active",
    "review": "active",
    "blocked": "paused",
    "done": "completed",
    "archived": "completed",
}

# CoPilot 4 态 → hermes（写入时用）
_COPILOT_TO_HERMES = {
    "backlog": "todo",
    "active": "running",
    "paused": "blocked",
    "completed": "done",
}

# 优先级映射：hermes INTEGER → CoPilot 字符串
_INT_TO_PRIORITY = {0: "medium", 1: "high", 2: "medium", 3: "low"}
_PRIORITY_TO_INT = {"urgent": -1, "high": 1, "medium": 0, "low": 3}

# hermes 有效状态集合
_HERMES_VALID_STATUSES = {
    "triage", "todo", "scheduled", "ready", "running",
    "blocked", "review", "done", "archived",
}


# ========== 连接管理 ==========

def _connect_readonly() -> sqlite3.Connection:
    """连接 kanban.db 读取（WAL 模式支持并发读，不干扰 hermes worker）。

    注意：WAL 数据库用 mode=ro 会失败（需要访问 -wal/-shm 文件），
    因此使用普通连接 + WAL，SQLite WAL 的 MVCC 保证读不阻塞写。
    """
    if not KANBAN_DB_PATH.exists():
        raise FileNotFoundError(f"kanban.db 不存在: {KANBAN_DB_PATH}")
    conn = sqlite3.connect(str(KANBAN_DB_PATH), timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")  # 连接级只读保护
    return conn


def _connect_writable() -> sqlite3.Connection:
    """以读写模式连接 kanban.db（WAL 模式，与 hermes worker 并发安全）。"""
    if not KANBAN_DB_PATH.exists():
        raise FileNotFoundError(f"kanban.db 不存在: {KANBAN_DB_PATH}")
    conn = sqlite3.connect(str(KANBAN_DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def _ts_to_iso(ts: Optional[int]) -> Optional[str]:
    """Unix 时间戳 → ISO 8601 UTC 字符串。"""
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, OSError):
        return None


def _row_to_copilot_task(row: sqlite3.Row) -> Dict[str, Any]:
    """将 kanban.db 的 task 行映射为 CoPilot 任务格式。"""
    hermes_status = row["status"] or "todo"
    copilot_status = _HERMES_TO_COPILOT.get(hermes_status, "backlog")
    priority_int = row["priority"] if "priority" in row.keys() else 0
    return {
        "task_id": row["id"],
        "title": row["title"] or "",
        "description": row["body"] or "",
        "status": copilot_status,
        "priority": _INT_TO_PRIORITY.get(priority_int, "medium"),
        "category": "general",
        "assignee": row["assignee"] or "none",
        "created_at": _ts_to_iso(row["created_at"]) or "",
        "updated_at": _ts_to_iso(row["started_at"] or row["created_at"]) or "",
        "completed_at": _ts_to_iso(row["completed_at"]),
        "project": "",
        "source": "hermes",
        "hermes_status": hermes_status,
        "hermes_assignee": row["assignee"] or "",
        "workspace_kind": row["workspace_kind"] if "workspace_kind" in row.keys() else "scratch",
    }


# ========== 查询接口 ==========

def is_available() -> bool:
    """kanban.db 是否可读。"""
    return KANBAN_DB_PATH.exists()


def list_tasks(status_filter: str = "", include_archived: bool = False) -> List[Dict[str, Any]]:
    """列出 hermes kanban 任务（映射为 CoPilot 格式）。

    Args:
        status_filter: CoPilot 状态过滤（backlog/active/completed/paused），空=全部
        include_archived: 是否包含已归档任务（hermes status=archived）

    Returns:
        CoPilot 格式任务列表
    """
    if not is_available():
        return []

    try:
        conn = _connect_readonly()
        # 构建查询
        sql = "SELECT * FROM tasks"
        conditions = []
        params = []
        if not include_archived:
            conditions.append("status != 'archived'")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY created_at DESC"

        rows = conn.execute(sql, params).fetchall()
        conn.close()

        tasks = [_row_to_copilot_task(row) for row in rows]
        # CoPilot 状态过滤
        if status_filter:
            tasks = [t for t in tasks if t["status"] == status_filter]
        return tasks
    except Exception:
        return []


def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """获取单个 hermes kanban 任务详情。"""
    if not is_available():
        return None
    try:
        conn = _connect_readonly()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return _row_to_copilot_task(row)
    except Exception:
        return None


def get_task_count() -> Dict[str, int]:
    """获取任务计数（按 hermes 状态分组）。"""
    if not is_available():
        return {}
    try:
        conn = _connect_readonly()
        rows = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status"
        ).fetchall()
        conn.close()
        return {row["status"]: row["cnt"] for row in rows}
    except Exception:
        return {}


# ========== 写入接口 ==========

def _generate_kanban_id() -> str:
    """生成 kanban 风格的任务 ID：t_ + 8位十六进制。"""
    import secrets
    return f"t_{secrets.token_hex(4)}"


def create_task(
    title: str,
    description: str = "",
    assignee: str = "copilot",
    priority: str = "medium",
    copilot_status: str = "backlog",
    created_by: str = "copilot",
) -> Optional[str]:
    """在 hermes kanban.db 中创建任务。

    Args:
        title: 任务标题
        description: 任务描述（写入 body 字段）
        assignee: 指派给谁（copilot/analyst/researcher/writer）
        priority: CoPilot 优先级（urgent/high/medium/low）
        copilot_status: CoPilot 状态（backlog/active/paused/completed）
        created_by: 创建者标识

    Returns:
        新建任务的 ID（t_xxxxxxxx），失败返回 None
    """
    if not is_available():
        return None

    hermes_status = _COPILOT_TO_HERMES.get(copilot_status, "todo")
    # hermes 只允许新建时进入 running 或 blocked
    if hermes_status not in ("todo", "running", "blocked"):
        hermes_status = "todo"

    task_id = _generate_kanban_id()
    now = int(time.time())
    priority_int = _PRIORITY_TO_INT.get(priority, 0)

    try:
        conn = _connect_writable()
        conn.execute(
            """INSERT INTO tasks (id, title, body, assignee, status, priority,
               created_by, created_at, workspace_kind)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'scratch')""",
            (task_id, title, description, assignee, hermes_status,
             priority_int, created_by, now),
        )
        # 记录事件
        conn.execute(
            """INSERT INTO task_events (task_id, kind, payload, created_at)
               VALUES (?, 'created', ?, ?)""",
            (task_id, json.dumps({"created_by": created_by, "title": title}), now),
        )
        conn.commit()
        conn.close()
        return task_id
    except Exception:
        return None


def delete_task(task_id: str) -> bool:
    """从 hermes kanban.db 删除任务（含关联的事件/评论/附件）。

    Args:
        task_id: hermes 任务 ID（t_xxxxxxxx）

    Returns:
        是否成功
    """
    if not KANBAN_DB_PATH.exists():
        return False
    try:
        conn = _connect_writable()
        # 检查任务是否存在
        row = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            conn.close()
            return False
        # 删除关联数据 + 任务本身
        conn.execute("DELETE FROM task_events WHERE task_id = ?", (task_id,))
        conn.execute("DELETE FROM task_comments WHERE task_id = ?", (task_id,))
        conn.execute("DELETE FROM task_runs WHERE task_id = ?", (task_id,))
        conn.execute("DELETE FROM task_attachments WHERE task_id = ?", (task_id,))
        conn.execute("DELETE FROM task_links WHERE parent_id = ? OR child_id = ?", (task_id, task_id))
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def update_task_status(task_id: str, copilot_status: str) -> bool:
    """更新 hermes kanban 任务状态。

    Args:
        task_id: hermes 任务 ID（t_xxxxxxxx）
        copilot_status: CoPilot 状态（backlog/active/paused/completed）

    Returns:
        是否成功
    """
    if not is_available():
        return False

    hermes_status = _COPILOT_TO_HERMES.get(copilot_status, "todo")
    if hermes_status not in _HERMES_VALID_STATUSES:
        return False

    now = int(time.time())
    try:
        conn = _connect_writable()
        # 获取当前状态
        row = conn.execute("SELECT status FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            conn.close()
            return False
        old_status = row["status"]

        # 更新状态
        completed_at = now if hermes_status == "done" else None
        if hermes_status == "done" and completed_at:
            conn.execute(
                "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
                (hermes_status, completed_at, task_id),
            )
        else:
            conn.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (hermes_status, task_id),
            )

        # 记录事件
        conn.execute(
            """INSERT INTO task_events (task_id, kind, payload, created_at)
               VALUES (?, 'completed' IF ? = 'done' ELSE 'promoted', ?, ?)""",
            (task_id, hermes_status,
             json.dumps({"old": old_status, "new": hermes_status, "by": "copilot"}), now),
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ========== 自检 ==========

def _self_check() -> int:
    """自检：验证 kanban.db 读取 + 状态映射 + ID 生成。"""
    print("=== kanban_reader 自检 ===")
    checks = 0
    fails = 0

    # 1. kanban.db 存在
    if is_available():
        checks += 1
        print(f"  [1/6] kanban.db 存在 ✓ ({KANBAN_DB_PATH})")
    else:
        fails += 1
        print(f"  [1/6] kanban.db 不存在 ✗ ({KANBAN_DB_PATH})")
        print(f"=== 结果: {checks}/{checks + fails} 通过 ===\n")
        return 1

    # 2. 读取任务列表
    try:
        tasks = list_tasks()
        assert len(tasks) > 0, "任务列表为空"
        checks += 1
        print(f"  [2/6] 读取任务列表 ✓ ({len(tasks)} 个任务)")
    except Exception as e:
        fails += 1
        print(f"  [2/6] 读取任务列表 ✗: {e}")

    # 3. 状态映射正确
    try:
        statuses = set(t["status"] for t in tasks)
        valid = statuses <= {"backlog", "active", "paused", "completed"}
        assert valid, f"无效状态: {statuses}"
        checks += 1
        print(f"  [3/6] 状态映射 ✓ (出现的状态: {statuses})")
    except Exception as e:
        fails += 1
        print(f"  [3/6] 状态映射 ✗: {e}")

    # 4. 单个任务详情
    try:
        if tasks:
            tid = tasks[0]["task_id"]
            task = get_task(tid)
            assert task is not None, f"获取任务失败: {tid}"
            assert task["task_id"] == tid
            assert task["source"] == "hermes"
            checks += 1
            print(f"  [4/6] 单个任务详情 ✓ ({tid})")
        else:
            checks += 1
            print(f"  [4/6] 单个任务详情 ✓ (跳过，无任务)")
    except Exception as e:
        fails += 1
        print(f"  [4/6] 单个任务详情 ✗: {e}")

    # 5. 任务计数
    try:
        counts = get_task_count()
        assert len(counts) > 0, "计数为空"
        total = sum(counts.values())
        checks += 1
        print(f"  [5/6] 任务计数 ✓ ({total} 总计: {counts})")
    except Exception as e:
        fails += 1
        print(f"  [5/6] 任务计数 ✗: {e}")

    # 6. ID 格式验证
    try:
        new_id = _generate_kanban_id()
        assert new_id.startswith("t_") and len(new_id) == 10, f"ID 格式错误: {new_id}"
        checks += 1
        print(f"  [6/6] ID 生成格式 ✓ ({new_id})")
    except Exception as e:
        fails += 1
        print(f"  [6/6] ID 生成格式 ✗: {e}")

    print(f"=== 结果: {checks}/{checks + fails} 通过 ===\n")
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        sys.exit(_self_check())
    print("kanban_reader — hermes kanban.db SQLite 读写层")
    print(f"数据库: {KANBAN_DB_PATH}")
    print(f"可用: {is_available()}")
    if is_available():
        counts = get_task_count()
        print(f"任务计数: {counts}")
    print("\n用法: from kanban_reader import list_tasks, get_task, create_task")
    print("自检: python3 kanban_reader.py --self-check")
