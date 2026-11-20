#!/usr/bin/env python3
"""briefing_sync.py — 文献简报双向同步引擎（v5.0 重构）。

v5.0 重大变更：
    - 修复 v4.1 的路径 bug（HERMES_STATUS_PATH 指向不存在的 status.json）
    - 直接委托 state_sync 读写共享的 item-status.json，不再维护独立路径
    - state_sync 内部使用 common.file_lock（fcntl.flock）跨进程锁保护
    - 状态映射基于 item-status.json 的 9 级状态枚举，而非旧版的时间戳字段推断

同步方向：
    - 反向同步（CoPilot → item-status.json）：用户操作时实时回写统一状态
      sync_to_hermes() 委托 state_sync.update_item_status()
    - 正向同步（item-status.json → CoPilot）：sync_all() 批量拉取统一状态
      sync_from_hermes() 读取 state_sync._load_item_status() 并更新 paper-pool
    - 失败重试：反向同步失败记入 reverse_sync_pending 队列，下次 sync_all 重试

状态映射规则（统一状态 → CoPilot 三态）：
    pool/candidate/pushed    →  跳过（未处理）
    viewed/interested/
    discussing/skipped       →  CoPilot viewed（已看，保留可追溯）
    discussed/archived       →  CoPilot archived（已归档）

冲突策略：
    - CoPilot 优先（用户意图 > hermes 自动流程）
    - 只升不降（unseen → viewed → archived 单向流转）

用法示例：
    >>> from briefing_sync import sync_to_hermes, sync_from_hermes, flush_pending_reverse
    >>> sync_to_hermes("2403.15337", "archived", "discuss_done")  # 反向同步单条
    >>> sync_from_hermes()                                         # 正向同步批量
    >>> flush_pending_reverse()                                    # 重试待同步队列

规范：仅使用 Python 3 标准库，PROJECT_ROOT 通过 paths.py 推导。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from common import now_utc, load_json, save_json
from paths import PROJECT_ROOT, MEMORY_DIR

# ─────────────────────────────────────────────
# 路径定义
# ─────────────────────────────────────────────

# v5.0: 不再维护 HERMES_STATUS_PATH（旧 status.json 从未存在）
# 统一状态文件由 state_sync.ITEM_STATUS_PATH 管理，briefing_sync 委托读写
SYNC_STATE_PATH = MEMORY_DIR / "sync-state.json"

# CoPilot 三状态等级（用于"只升不降"判断）
_STATUS_RANK = {"unseen": 0, "viewed": 1, "archived": 2}

# CoPilot 操作 → 统一状态映射（反向同步用）
_ACTION_TO_UNIFIED = {
    "interested": "interested",
    "skip": "skipped",
    "later": "viewed",
    "archive": "archived",
    "discuss_done": "archived",
}

# CoPilot 三状态 → 统一状态映射（action 为空时回退）
_COPILOT_TO_UNIFIED = {
    "viewed": "viewed",
    "archived": "archived",
}

# 统一状态 → CoPilot 三状态映射（正向同步用）
_UNIFIED_TO_COPILOT = {
    "viewed": "viewed",
    "interested": "viewed",
    "discussing": "viewed",
    "skipped": "viewed",       # skip 保留为 viewed，可追溯
    "discussed": "archived",   # 讨论完成 → 归档
    "archived": "archived",    # 已归档到知识库
}


# ─────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────

def _can_upgrade(current: str, target: str) -> bool:
    """判断状态是否可升级（只升不降）。"""
    return _STATUS_RANK.get(target, 0) > _STATUS_RANK.get(current, 0)


def _load_sync_state() -> Dict[str, Any]:
    """加载同步状态文件。"""
    state = load_json(SYNC_STATE_PATH, {})
    if "reverse_sync_pending" not in state:
        state["reverse_sync_pending"] = []
    if "reverse_sync_watermark" not in state:
        state["reverse_sync_watermark"] = ""
    return state


def _save_sync_state(state: Dict[str, Any]) -> None:
    """保存同步状态文件。"""
    save_json(SYNC_STATE_PATH, state)


# ─────────────────────────────────────────────
# 反向同步：CoPilot → item-status.json（委托 state_sync）
# ─────────────────────────────────────────────

def sync_to_hermes(arxiv_id: str, copilot_status: str, action: str = "") -> Dict[str, Any]:
    """反向同步：CoPilot 操作 → 统一状态 item-status.json。

    v5.0 重构：直接委托 state_sync.update_item_status 写入共享的 item-status.json。
    state_sync 内部使用 file_lock 跨进程锁保护 read-modify-write 临界区。
    写入失败（权限/磁盘）时记入待同步队列，不阻塞用户操作。

    Args:
        arxiv_id: 论文 arXiv ID
        copilot_status: CoPilot 状态（viewed/archived，action 为空时用于回退映射）
        action: 触发动作（interested/skip/archive/later/discuss_done）

    Returns:
        {"success": bool, "arxiv_id": str, "status": str, "reason": str}
    """
    # 确定统一状态：优先使用 action 映射，回退到 copilot_status
    unified_status = _ACTION_TO_UNIFIED.get(action, "")
    if not unified_status:
        unified_status = _COPILOT_TO_UNIFIED.get(copilot_status, "viewed")

    try:
        import state_sync as ss

        # 从 CoPilot paper-pool 获取论文元数据（首次注册时填入）
        title = ""
        direction = ""
        try:
            import paper_pool as pp
            pool = pp._load()
            if arxiv_id in pool:
                title = pool[arxiv_id].get("title", "")
                direction = pool[arxiv_id].get("direction", "")
        except Exception:
            pass

        ss.update_item_status(
            arxiv_id, unified_status,
            updated_by="copilot",
            title=title,
            direction=direction,
        )
    except Exception as e:
        _add_to_pending(arxiv_id, copilot_status, action, str(e))
        return {"success": False, "arxiv_id": arxiv_id, "reason": str(e)}

    # 更新同步水位
    state = _load_sync_state()
    state["last_reverse_sync"] = now_utc()
    _save_sync_state(state)

    return {"success": True, "arxiv_id": arxiv_id, "status": unified_status}


def _add_to_pending(arxiv_id: str, copilot_status: str, action: str, reason: str) -> None:
    """将失败的反向同步记入待同步队列。"""
    state = _load_sync_state()
    pending = state.get("reverse_sync_pending", [])

    # 去重：同一 arxiv_id 只保留最新一条
    pending = [p for p in pending if p.get("arxiv_id") != arxiv_id]
    pending.append({
        "arxiv_id": arxiv_id,
        "copilot_status": copilot_status,
        "action": action,
        "reason": reason,
        "attempted_at": now_utc(),
        "retry_count": 0,
    })

    state["reverse_sync_pending"] = pending[-100:]  # 保留最近 100 条
    _save_sync_state(state)


# ─────────────────────────────────────────────
# 正向同步：item-status.json 水位标记更新
# ─────────────────────────────────────────────

def sync_from_hermes() -> Dict[str, Any]:
    """正向同步：统一状态 item-status.json 状态确认。

    v6.8.14 重构：paper-pool.json 已废弃（papers 字段为空，数据已迁移到
    item-status.json + knowledge/raw/papers/ frontmatter）。
    此函数不再写 paper-pool.json，只更新同步水位标记。

    Returns:
        {"synced": int, "skipped": int, "date": str}
    """
    import state_sync as ss

    if not ss.ITEM_STATUS_PATH.exists():
        return {"synced": 0, "skipped": 0, "date": "", "reason": "item-status.json 不存在"}

    try:
        data = ss._load_item_status()
    except Exception:
        return {"synced": 0, "skipped": 0, "date": "", "reason": "item-status.json 读取失败"}

    items = data.get("items", {})
    updated_at = data.get("updated_at", "")
    if not items:
        return {"synced": 0, "skipped": 0, "date": updated_at, "reason": "无论文记录"}

    # v6.8.14: paper-pool.json 已废弃，不再写入
    # 只更新同步水位
    state = _load_sync_state()
    state["reverse_sync_watermark"] = updated_at
    _save_sync_state(state)

    return {"synced": len(items), "skipped": 0, "date": updated_at}


# ─────────────────────────────────────────────
# 待同步队列重试
# ─────────────────────────────────────────────

def flush_pending_reverse() -> Dict[str, Any]:
    """重试待同步队列中失败的反向同步。

    在 sync_all() 执行时前置调用，处理之前因 item-status.json 不可写等原因
    失败的反向同步请求。

    Returns:
        {"flushed": int, "remaining": int, "errors": int}
    """
    state = _load_sync_state()
    pending = state.get("reverse_sync_pending", [])

    if not pending:
        return {"flushed": 0, "remaining": 0, "errors": 0}

    flushed = 0
    errors = 0
    still_pending = []

    for item in pending:
        aid = item.get("arxiv_id", "")
        status = item.get("copilot_status", "")
        action = item.get("action", "")

        if not aid or not status:
            continue

        result = sync_to_hermes(aid, status, action)
        if result.get("success"):
            flushed += 1
        else:
            # 增加重试计数
            item["retry_count"] = item.get("retry_count", 0) + 1
            item["last_retry"] = now_utc()
            # 超过 5 次重试则放弃
            if item["retry_count"] >= 5:
                errors += 1
            else:
                still_pending.append(item)

    state["reverse_sync_pending"] = still_pending
    _save_sync_state(state)

    return {
        "flushed": flushed,
        "remaining": len(still_pending),
        "errors": errors,
    }


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> bool:
    """自检：验证双向同步逻辑（使用临时文件，不修改真实数据）。"""
    import tempfile
    import shutil

    print("=" * 50)
    print("◐ briefing_sync 自检（v5.0 item-status.json schema）")
    print("=" * 50)

    passed = 0
    total = 0

    tmp_dir = tempfile.mkdtemp(prefix="briefing_sync_test_")

    # 保存原始路径，测试后恢复
    global SYNC_STATE_PATH
    _orig_sync = SYNC_STATE_PATH
    SYNC_STATE_PATH = Path(tmp_dir) / "sync-state.json"

    # patch state_sync 路径到临时目录
    import state_sync as ss
    _orig_item_path = ss.ITEM_STATUS_PATH
    ss.ITEM_STATUS_PATH = Path(tmp_dir) / "item-status.json"

    # patch paper_pool 路径到临时目录
    import paper_pool as pp
    _orig_pool_path = pp.POOL_PATH
    pp.POOL_PATH = Path(tmp_dir) / "paper-pool.json"

    try:
        # [1/5] _can_upgrade 状态升级判断
        total += 1
        ok = (_can_upgrade("unseen", "viewed") and
              _can_upgrade("unseen", "archived") and
              _can_upgrade("viewed", "archived") and
              not _can_upgrade("archived", "viewed") and
              not _can_upgrade("viewed", "viewed"))
        if ok:
            passed += 1
            print(f"  [1/{total}] ✓ _can_upgrade 状态升级判断正确")
        else:
            print(f"  [1/{total}] ✗ _can_upgrade 判断错误")

        # [2/5] 反向同步：CoPilot archived → item-status.json
        total += 1
        # 先在 paper-pool 中添加论文（提供元数据）
        pp._save({"2403.15337": {
            "status": "viewed",
            "title": "测试论文",
            "direction": "固体HHG",
            "added_at": now_utc(),
        }})
        result = sync_to_hermes("2403.15337", "archived", "discuss_done")
        if result.get("success"):
            info = ss.get_item_info("2403.15337")
            if info and info.get("status") == "archived":
                passed += 1
                print(f"  [2/{total}] ✓ 反向同步 archived 成功（item-status.json status=archived）")
            else:
                print(f"  [2/{total}] ✗ 反向同步后状态错误: {info}")
        else:
            print(f"  [2/{total}] ✗ 反向同步失败: {result}")

        # [3/5] 反向同步：新论文（不在 item-status 中）→ 自动注册
        total += 1
        result = sync_to_hermes("9999.88888", "viewed", "interested")
        if result.get("success"):
            info = ss.get_item_info("9999.88888")
            if info and info.get("status") == "interested":
                passed += 1
                print(f"  [3/{total}] ✓ 新论文自动注册（status=interested）")
            else:
                print(f"  [3/{total}] ✗ 新论文注册状态错误: {info}")
        else:
            print(f"  [3/{total}] ✗ 新论文同步失败: {result}")

        # [4/5] flush_pending_reverse 重试
        total += 1
        # 直接添加一条 pending 记录（模拟之前写失败的场景）
        _add_to_pending("7777.77777", "viewed", "later", "模拟写失败")
        flush_result = flush_pending_reverse()
        if flush_result.get("flushed", 0) >= 1:
            # 验证 item-status.json 已更新
            info = ss.get_item_info("7777.77777")
            if info and info.get("status") == "viewed":
                passed += 1
                print(f"  [4/{total}] ✓ flush_pending_reverse 重试成功 (flushed={flush_result['flushed']})")
            else:
                print(f"  [4/{total}] ✗ flush 后状态错误: {info}")
        else:
            print(f"  [4/{total}] ✗ flush_pending_reverse 失败: {flush_result}")

        # [5/5] 正向同步映射逻辑验证
        total += 1
        # 设置 item-status.json：一篇 viewed、一篇 archived
        ss.update_item_status("2403.15337", "viewed", updated_by="hermes-cron")
        ss.update_item_status("1111.22222", "archived", updated_by="hermes-cron",
                              title="归档测试", direction="测试")
        # 确保 CoPilot pool 中有这些论文（1111.22222 设为 unseen 以验证升级）
        pool = pp._load()
        pool["1111.22222"] = {"status": "unseen", "title": "归档测试", "added_at": now_utc()}
        pp._save(pool)

        sync_result = sync_from_hermes()
        if "synced" in sync_result and "skipped" in sync_result:
            # 验证 1111.22222 从 unseen 升级为 archived
            final_status = pp.get_paper_status("1111.22222")
            if final_status == "archived":
                passed += 1
                print(f"  [5/{total}] ✓ 正向同步映射正常 (synced={sync_result['synced']}, skipped={sync_result['skipped']})")
            else:
                print(f"  [5/{total}] ✗ 正向同步后状态错误: {final_status}")
        else:
            print(f"  [5/{total}] ✗ 正向同步异常: {sync_result}")

    finally:
        # 恢复路径
        SYNC_STATE_PATH = _orig_sync
        ss.ITEM_STATUS_PATH = _orig_item_path
        pp.POOL_PATH = _orig_pool_path
        # 清理临时目录
        shutil.rmtree(tmp_dir, ignore_errors=True)

    all_ok = passed == total
    print(f"\n{'✓' if all_ok else '✗'} briefing_sync: {passed}/{total} 通过")
    return all_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_check() else 1)
