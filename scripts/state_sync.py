#!/usr/bin/env python3
"""统一状态同步层 —— Copilot 和 hermes 之间的状态总线。

用途：
    让 Copilot Web 和 hermes cron 共享同一个状态真相源。
    Copilot 操作（感兴趣/讨论/归档）→ 写回 hermes 的 item-status.json
    hermes 操作（推送/检索）→ 写回同一文件
    双方都能读到对方的最新状态。

核心文件：
    ~/Desktop/hermes_workspace/knowledge_base/AI_wiki/briefings/item-status.json
    （论文统一状态，Copilot 和 hermes 共用）

    各项目目录下 .copilot-sync.json
    （项目/任务/决策状态）

统一状态枚举（论文生命周期）：
    pool → candidate → pushed → viewed → interested → discussing → discussed → archived
                                                                ↗
                                                          skipped

用法示例：
    >>> from state_sync import update_item_status, get_item_status, get_processed_ids
    >>> update_item_status("2403.15337", "discussed", updated_by="copilot",
    ...                    discussion_path="knowledge/...")
    >>> status = get_item_status("2403.15337")  # → "discussed"
    >>> processed = get_processed_ids()  # → {"2403.15337", ...} (status>=viewed)

规范：仅标准库，PROJECT_ROOT 推导，JSON ensure_ascii=False。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

PROJECT_ROOT = Path(__file__).parent.parent
HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
BRIEFINGS_DIR = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings"
ITEM_STATUS_PATH = BRIEFINGS_DIR / "item-status.json"

# 统一状态枚举（按生命周期排序，序号越大越"不可逆"）
STATUS_ORDER = {
    "pool": 0,
    "candidate": 1,
    "pushed": 2,
    "viewed": 3,
    "interested": 4,
    "discussing": 5,
    "discussed": 6,
    "archived": 7,
    "skipped": 6,  # skipped 与 discussed 同级（都表示用户已处理）
}

# status >= viewed 表示用户已经处理过（hermes 不应重复推送）
PROCESSED_THRESHOLD = STATUS_ORDER["viewed"]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_item_status() -> Dict[str, Any]:
    """加载论文统一状态。"""
    if not ITEM_STATUS_PATH.exists():
        return {"version": "1.0", "updated_at": _now(), "items": {}}
    try:
        return json.loads(ITEM_STATUS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"version": "1.0", "updated_at": _now(), "items": {}}


def _save_item_status(data: Dict[str, Any]) -> None:
    """保存论文统一状态。"""
    ITEM_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = _now()
    ITEM_STATUS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def update_item_status(
    arxiv_id: str,
    new_status: str,
    updated_by: str = "copilot",
    title: str = "",
    direction: str = "",
    score: float = 0,
    **extra: Any,
) -> Dict[str, Any]:
    """更新论文统一状态，写入 hermes 的 item-status.json。

    Args:
        arxiv_id: arXiv 论文 ID
        new_status: 新状态（pool/candidate/pushed/viewed/interested/discussing/discussed/archived/skipped）
        updated_by: 操作来源（copilot/hermes-cron/feishu）
        title/direction/score: 论文元数据（首次注册时填）
        **extra: 额外字段（discussion_path/archived_to 等）

    Returns:
        更新后的 item dict
    """
    data = _load_item_status()
    items = data.setdefault("items", {})

    item = items.get(arxiv_id, {})
    # 首次注册时填充元数据
    if not item:
        item = {
            "arxiv_id": arxiv_id,
            "title": title,
            "direction": direction,
            "score": score,
            "first_seen": _now(),
            "history": [],
        }

    # 状态合并：如果新状态的"不可逆性"低于已有状态，保留已有（除非 updated_by 明确覆盖）
    old_status = item.get("status", "")
    old_order = STATUS_ORDER.get(old_status, -1)
    new_order = STATUS_ORDER.get(new_status, -1)
    if old_order > new_order and old_status not in ("", "pool", "candidate"):
        # 已有状态更"高级"，不降级（除非显式要求）
        pass
    else:
        item["status"] = new_status

    item["last_updated"] = _now()
    item["updated_by"] = updated_by
    item.update(extra)

    # 记录历史
    item.setdefault("history", []).append({
        "status": new_status, "by": updated_by, "at": _now(),
    })

    items[arxiv_id] = item
    _save_item_status(data)
    return item


def get_item_status(arxiv_id: str) -> str:
    """获取论文当前状态。"""
    data = _load_item_status()
    return data.get("items", {}).get(arxiv_id, {}).get("status", "")


def get_item_info(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """获取论文完整状态信息。"""
    data = _load_item_status()
    return data.get("items", {}).get(arxiv_id)


def get_processed_ids() -> Set[str]:
    """获取所有已处理论文的 arxiv_id（status >= viewed）。

    hermes cron 检索入池时应跳过这些论文。
    """
    data = _load_item_status()
    processed = set()
    for aid, item in data.get("items", {}).items():
        status = item.get("status", "")
        if STATUS_ORDER.get(status, -1) >= PROCESSED_THRESHOLD:
            processed.add(aid)
    return processed


def get_items_by_status(status: str = "") -> List[Dict[str, Any]]:
    """按状态获取论文列表（空=全部）。"""
    data = _load_item_status()
    items = list(data.get("items", {}).values())
    if status:
        items = [i for i in items if i.get("status") == status]
    return items


def get_status_summary() -> Dict[str, int]:
    """获取状态分布统计。"""
    data = _load_item_status()
    from collections import Counter
    c = Counter(i.get("status", "unknown") for i in data.get("items", {}).values())
    return dict(c)


# ============================================================
# 项目/任务/决策状态同步（.copilot-sync.json）
# ============================================================

def _get_project_sync_path(project_dir: str) -> Path:
    """获取项目的 .copilot-sync.json 路径。"""
    return Path(project_dir) / ".copilot-sync.json"


def load_project_sync(project_dir: str) -> Dict[str, Any]:
    """加载项目同步状态。"""
    path = _get_project_sync_path(project_dir)
    if not path.exists():
        return {"project": Path(project_dir).name, "decisions": {}, "tasks": {},
                "last_hermes_update": "", "last_copilot_view": ""}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"project": Path(project_dir).name, "decisions": {}, "tasks": {},
                "last_hermes_update": "", "last_copilot_view": ""}


def save_project_sync(project_dir: str, data: Dict[str, Any]) -> None:
    """保存项目同步状态。"""
    path = _get_project_sync_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def update_decision_status(
    project_dir: str,
    decision_id: str,
    status: str,
    decided_by: str = "copilot",
    title: str = "",
    **extra: Any,
) -> Dict[str, Any]:
    """更新决策状态，写入项目的 .copilot-sync.json。

    Args:
        project_dir: 项目目录路径
        decision_id: 决策 ID
        status: pending/approved/rejected/discussing/discussed
        decided_by: copilot/hermes/feishu
    """
    data = load_project_sync(project_dir)
    decision = data.setdefault("decisions", {}).setdefault(decision_id, {})
    if not decision:
        decision["title"] = title
        decision["created_at"] = _now()
    decision["status"] = status
    decision["decided_by"] = decided_by
    decision["decided_at"] = _now()
    decision.update(extra)
    data["decisions"][decision_id] = decision
    if decided_by == "copilot":
        data["last_copilot_view"] = _now()
    else:
        data["last_hermes_update"] = _now()
    save_project_sync(project_dir, data)
    return decision


def register_project(project_dir: str, project_name: str = "") -> None:
    """注册新项目（创建 .copilot-sync.json）。"""
    path = _get_project_sync_path(project_dir)
    if path.exists():
        return  # 已注册
    name = project_name or Path(project_dir).name
    save_project_sync(project_dir, {
        "project": name,
        "decisions": {},
        "tasks": {},
        "last_hermes_update": "",
        "last_copilot_view": "",
    })


def update_task_status(
    project_dir: str,
    task_id: str,
    status: str,
    title: str = "",
    assignee: str = "",
    **extra: Any,
) -> Dict[str, Any]:
    """更新任务状态。"""
    data = load_project_sync(project_dir)
    task = data.setdefault("tasks", {}).setdefault(task_id, {})
    if not task:
        task["title"] = title
        task["assignee"] = assignee
        task["created_at"] = _now()
    task["status"] = status
    task["updated_at"] = _now()
    task.update(extra)
    data["tasks"][task_id] = task
    save_project_sync(project_dir, data)
    return task


# ============================================================
# 初始化（从现有数据合并）
# ============================================================

def initialize_from_existing() -> int:
    """从现有 paper-pool + briefing_state 合并初始化 item-status.json。

    Returns:
        初始化的论文数量
    """
    data = _load_item_status()
    items = data.setdefault("items", {})

    # 1. 从 Copilot paper-pool.json 导入
    pool_path = PROJECT_ROOT / "memory" / "paper-pool.json"
    if pool_path.exists():
        try:
            pool = json.loads(pool_path.read_text(encoding="utf-8"))
            for aid, p in pool.items():
                if aid not in items:
                    items[aid] = {
                        "arxiv_id": aid,
                        "title": p.get("title", ""),
                        "direction": p.get("direction", ""),
                        "score": p.get("score", 0),
                        "status": p.get("status", "pool"),
                        "first_seen": p.get("added_at", _now()),
                        "last_updated": p.get("updated_at", _now()),
                        "updated_by": "copilot",
                        "history": [],
                    }
        except Exception:
            pass

    # 2. 从 hermes daily_candidates.json 导入（补充 pool/candidate 状态）
    candidates_path = BRIEFINGS_DIR / "daily_candidates.json"
    if candidates_path.exists():
        try:
            cands = json.loads(candidates_path.read_text(encoding="utf-8"))
            for p in cands.get("papers", []):
                aid = p.get("arxiv_id", "")
                if aid and aid not in items:
                    items[aid] = {
                        "arxiv_id": aid,
                        "title": p.get("title", ""),
                        "direction": p.get("direction", ""),
                        "score": p.get("score_deepxiv", 0),
                        "status": "candidate",
                        "first_seen": _now(),
                        "last_updated": _now(),
                        "updated_by": "hermes-cron",
                        "history": [],
                    }
        except Exception:
            pass

    # 3. 从 Copilot paper-feedback.json 补充 history
    fb_path = PROJECT_ROOT / "memory" / "paper-feedback.json"
    if fb_path.exists():
        try:
            feedbacks = json.loads(fb_path.read_text(encoding="utf-8"))
            for fb in feedbacks:
                aid = fb.get("arxiv_id", "")
                action = fb.get("action", "")
                if aid in items and action:
                    status_map = {
                        "interested": "interested", "skip": "skipped",
                        "later": "viewed", "archive": "archived",
                        "discuss_done": "archived",
                    }
                    s = status_map.get(action, "viewed")
                    items[aid].setdefault("history", []).append({
                        "status": s, "by": "copilot", "at": fb.get("timestamp", _now()),
                    })
        except Exception:
            pass

    _save_item_status(data)
    return len(items)


# ============================================================
# 自检
# ============================================================

def _self_check() -> None:
    print("=" * 50)
    print("◐ state_sync 自检")
    print("=" * 50)

    print("\n[1/4] item-status.json 路径...")
    print(f"  {ITEM_STATUS_PATH}")
    print(f"  存在: {ITEM_STATUS_PATH.exists()}")

    print("\n[2/4] 初始化（从现有数据合并）...")
    count = initialize_from_existing()
    print(f"  ✓ 初始化 {count} 篇论文")

    print("\n[3/4] 状态分布...")
    summary = get_status_summary()
    for s, n in sorted(summary.items(), key=lambda x: STATUS_ORDER.get(x[0], 99)):
        print(f"  {s}: {n}")

    print("\n[4/4] 功能验证...")
    # 测试更新
    test_aid = "TEST.00001"
    update_item_status(test_aid, "viewed", updated_by="self-check", title="测试论文")
    assert get_item_status(test_aid) == "viewed"
    processed = get_processed_ids()
    assert test_aid in processed
    print(f"  ✓ update/get_item_status 正常")
    print(f"  ✓ get_processed_ids: {len(processed)} 篇已处理")

    # 清理测试数据
    data = _load_item_status()
    data["items"].pop(test_aid, None)
    _save_item_status(data)

    print("\n✓ state_sync 自检通过")


if __name__ == "__main__":
    _self_check()
