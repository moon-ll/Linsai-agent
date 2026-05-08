#!/usr/bin/env python3
"""
task_manager.py — 任务 CRUD、状态流转与逾期检测

用法示例:
    from scripts.task_manager import create_task, list_tasks, transition_task

    task_id, path = create_task("设计固体HHG光路", category="research", priority="high")
    transition_task(task_id, "active")
    tasks = list_tasks(status="active", sort_by="priority")
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
TASKS_DIR = PROJECT_ROOT / "tasks"
MEMORY_DIR = PROJECT_ROOT / "memory"

STATUS_DIRS = {
    "backlog": TASKS_DIR / "backlog",
    "active": TASKS_DIR / "active",
    "completed": TASKS_DIR / "completed",
    "paused": TASKS_DIR / "backlog",
}

PRIORITY_ORDER = {"urgent": 0, "high": 1, "medium": 2, "low": 3}

CATEGORY_DEFAULTS = {
    "research": {"tags": ["研究"]},
    "writing": {"tags": ["写作"]},
    "experiment": {"tags": ["实验"]},
    "reminder": {"tags": ["提醒"], "priority": "low"},
    "general": {"tags": []},
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _find_task_file(task_id: str) -> Optional[Path]:
    for subdir in ("backlog", "active", "completed"):
        candidate = TASKS_DIR / subdir / f"{task_id}.json"
        if candidate.exists():
            return candidate
    return None


def _load_task_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _generate_task_id(title: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    prefix = title[:10].strip()
    return f"TASK-{ts}-{prefix}"


def _validate_priority(priority: str) -> str:
    allowed = {"low", "medium", "high", "urgent"}
    return priority if priority in allowed else "medium"


def _validate_category(category: str) -> str:
    allowed = {"general", "research", "writing", "experiment", "reminder"}
    return category if category in allowed else "general"


def _ensure_dirs() -> None:
    for d in STATUS_DIRS.values():
        d.mkdir(parents=True, exist_ok=True)


def create_task(
    title: str,
    category: str = "general",
    due_date: str = "",
    priority: str = "medium",
    description: str = "",
    related_session: str = "",
) -> Tuple[str, Path]:
    """创建新任务，返回 (task_id, task_file_path)。"""
    _ensure_dirs()
    category = _validate_category(category)
    defaults = CATEGORY_DEFAULTS.get(category, {})
    final_priority = defaults.get("priority", priority)
    final_priority = _validate_priority(final_priority)
    tags = defaults.get("tags", [])

    task_id = _generate_task_id(title)
    # 若 ID 已存在则加序号
    counter = 1
    base_id = task_id
    while _find_task_file(task_id):
        task_id = f"{base_id}-{counter}"
        counter += 1

    task = {
        "task_id": task_id,
        "title": title,
        "category": category,
        "status": "backlog",
        "priority": final_priority,
        "description": description,
        "due_date": due_date,
        "created_at": _now_utc(),
        "updated_at": _now_utc(),
        "completed_at": None,
        "related_session": related_session,
        "tags": list(tags),
    }

    path = STATUS_DIRS["backlog"] / f"{task_id}.json"
    _write_json(path, task)
    print(f"✓ 任务已创建: {task_id} → {path.name}")
    return task_id, path


def get_task(task_id: str) -> dict:
    """读取任务文件，返回任务字典。在所有 tasks 子目录中搜索。"""
    path = _find_task_file(task_id)
    if path is None:
        raise FileNotFoundError(f"✗ 未找到任务: {task_id}")
    return _load_task_file(path)


def update_task(task_id: str, **fields) -> dict:
    """更新任务字段，自动更新 updated_at。"""
    path = _find_task_file(task_id)
    if path is None:
        raise FileNotFoundError(f"✗ 未找到任务: {task_id}")

    task = _load_task_file(path)
    readonly = {"task_id", "created_at", "status"}
    for key, value in fields.items():
        if key in readonly:
            print(f"⚠ 字段 '{key}' 只读，已跳过")
            continue
        if key == "priority":
            value = _validate_priority(value)
        if key == "category":
            value = _validate_category(value)
        task[key] = value

    task["updated_at"] = _now_utc()
    _write_json(path, task)
    print(f"✓ 任务已更新: {task_id}")
    return task


def transition_task(task_id: str, new_status: str) -> bool:
    """状态流转：backlog → active → completed/paused。
    自动将任务文件移动到对应目录。
    """
    allowed = {"backlog", "active", "completed", "paused"}
    if new_status not in allowed:
        print(f"✗ 无效状态: {new_status}")
        return False

    path = _find_task_file(task_id)
    if path is None:
        print(f"✗ 未找到任务: {task_id}")
        return False

    task = _load_task_file(path)
    old_status = task.get("status", "backlog")

    # 简单状态机校验
    valid_transitions = {
        "backlog": {"active", "paused"},
        "active": {"completed", "paused", "backlog"},
        "paused": {"active", "backlog"},
        "completed": {"active", "backlog"},
    }
    if new_status not in valid_transitions.get(old_status, set()):
        print(f"⚠ 状态流转不允许: {old_status} → {new_status}")
        return False

    task["status"] = new_status
    task["updated_at"] = _now_utc()
    if new_status == "completed":
        task["completed_at"] = _now_utc()
    else:
        task["completed_at"] = None

    new_dir = STATUS_DIRS[new_status]
    new_dir.mkdir(parents=True, exist_ok=True)
    new_path = new_dir / f"{task_id}.json"

    _write_json(new_path, task)
    if path != new_path:
        path.unlink()

    print(f"✓ 状态流转: {task_id} {old_status} → {new_status}")
    _sync_to_working_context(task)
    return True


def list_tasks(status: str = "all", sort_by: str = "due_date") -> List[dict]:
    """列出任务。status: all/backlog/active/completed/paused。sort_by: due_date/priority/created_at。"""
    tasks = []
    for subdir in ("backlog", "active", "completed"):
        if status != "all" and status != subdir and not (status == "paused" and subdir == "backlog"):
            continue
        folder = TASKS_DIR / subdir
        if not folder.exists():
            continue
        for f in folder.glob("TASK-*.json"):
            try:
                task = _load_task_file(f)
            except (json.JSONDecodeError, KeyError):
                continue
            required = {"task_id", "title", "status", "priority", "created_at"}
            if not required.issubset(task.keys()):
                continue
            # paused 任务在 backlog 目录里，但状态为 paused
            if status == "paused" and task.get("status") != "paused":
                continue
            if status != "all" and status != "paused" and task.get("status") != status:
                continue
            tasks.append(task)

    def sort_key(t: dict):
        if sort_by == "priority":
            return PRIORITY_ORDER.get(t.get("priority", "medium"), 2)
        if sort_by == "due_date":
            dd = t.get("due_date", "")
            return dd if dd else "9999-12-31"
        if sort_by == "created_at":
            return t.get("created_at", "")
        return ""

    reverse = sort_by == "created_at"
    tasks.sort(key=sort_key, reverse=reverse)
    return tasks


def check_overdue_tasks() -> List[dict]:
    """检查逾期任务（due_date < 今天 且 status 不是 completed）。"""
    today = _today_date()
    overdue = []
    for task in list_tasks(status="all"):
        dd = task.get("due_date", "")
        st = task.get("status", "")
        if dd and dd < today and st != "completed":
            overdue.append(task)
    return overdue


def delete_task(task_id: str) -> bool:
    """删除任务文件，返回是否成功。"""
    path = _find_task_file(task_id)
    if path is None:
        print(f"✗ 未找到任务: {task_id}")
        return False
    path.unlink()
    print(f"✓ 任务已删除: {task_id}")
    return True


def _sync_to_working_context(task: dict):
    """将 active 任务的项目名加入 working-context.json 的 active_projects（如文件存在）。"""
    wc_path = MEMORY_DIR / "working-context.json"
    if not wc_path.exists():
        return
    try:
        data = json.loads(wc_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return

    active_projects = data.get("active_projects", [])
    # 去重更新：若任务为 active，加入；若已非 active 且其中存在同名项目，视情况保留
    if task.get("status") == "active" and task.get("title"):
        names = {p.get("name") for p in active_projects}
        if task["title"] not in names:
            active_projects.append({
                "name": task["title"],
                "status": "active",
                "milestones": [],
                "deadlines": [task["due_date"]] if task.get("due_date") else [],
            })
            data["active_projects"] = active_projects
            data["updated_at"] = _now_utc()
            _write_json(wc_path, data)
            print(f"◐ 已同步到工作上下文: {task['title']}")


def _cleanup_test_data(prefix: str = "TASK-") -> None:
    """清理所有以 prefix 开头的测试任务。"""
    for subdir in ("backlog", "active", "completed"):
        folder = TASKS_DIR / subdir
        if not folder.exists():
            continue
        for f in folder.glob(f"{prefix}*.json"):
            f.unlink()
            print(f"✓ 清理测试文件: {f.name}")


if __name__ == "__main__":
    print("=" * 40)
    print("task_manager.py 自检开始")
    print("=" * 40)

    # 1. 创建 4 个不同 category 的任务
    print("\n[1] 创建 4 个不同 category 的任务")
    t1, _ = create_task("设计固体HHG光路", category="research", priority="high", due_date="2026-05-20")
    t2, _ = create_task("撰写实验方案", category="writing", priority="medium", due_date="2026-05-18")
    t3, _ = create_task("搭建光路系统", category="experiment", priority="urgent", due_date="2026-05-10")
    t4, _ = create_task("提醒开组会", category="reminder", due_date="2026-05-15")

    # 2. 测试状态流转: backlog → active → completed
    print("\n[2] 测试状态流转: backlog → active → completed")
    transition_task(t1, "active")
    transition_task(t1, "completed")

    # 再激活一个任务到 active
    transition_task(t3, "active")

    # 3. 列出所有任务（按不同方式排序）
    print("\n[3] 列出所有任务（按不同方式排序）")
    print("--- 按 due_date ---")
    for t in list_tasks(sort_by="due_date"):
        print(f"  ○ {t['task_id']}: {t['title']} [{t['status']}] due={t.get('due_date','无')}")

    print("--- 按 priority ---")
    for t in list_tasks(sort_by="priority"):
        print(f"  ○ {t['task_id']}: {t['title']} [{t['status']}] priority={t['priority']}")

    print("--- 按 created_at ---")
    for t in list_tasks(sort_by="created_at"):
        print(f"  ○ {t['task_id']}: {t['title']} [{t['status']}] created={t['created_at']}")

    print("--- 仅 active ---")
    for t in list_tasks(status="active"):
        print(f"  ◐ {t['task_id']}: {t['title']} [{t['status']}]")

    # 4. 更新任务字段
    print("\n[4] 更新任务字段")
    updated = update_task(t2, description="补充泵浦-探测光路设计", priority="high")
    print(f"  更新后 description={updated['description']}, priority={updated['priority']}")

    # 尝试更新只读字段
    update_task(t2, title="新标题", created_at="不应该改")

    # 5. 测试逾期检测（创建 1 个昨天的逾期任务）
    print("\n[5] 测试逾期检测")
    yesterday = (datetime.now(timezone.utc).replace(day=datetime.now(timezone.utc).day - 1)
                 if datetime.now(timezone.utc).day > 1 else datetime.now(timezone.utc))
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    t_overdue, _ = create_task("逾期测试任务", category="general", due_date=yesterday_str)
    # 修正 due_date 为昨天（创建时自动生成的是今天，直接修改）
    update_task(t_overdue, due_date=yesterday_str)
    overdue = check_overdue_tasks()
    if any(t["task_id"] == t_overdue for t in overdue):
        print(f"✓ 正确检测到逾期任务: {t_overdue}")
    else:
        print(f"✗ 未检测到逾期任务: {t_overdue}")

    # 6. 删除测试任务
    print("\n[6] 删除测试任务")
    delete_task(t_overdue)

    # 7. 清理所有测试数据
    print("\n[7] 清理所有测试数据")
    _cleanup_test_data(prefix="TASK-20260508-")

    print("\n" + "=" * 40)
    print("task_manager.py 自检完成")
    print("=" * 40)
