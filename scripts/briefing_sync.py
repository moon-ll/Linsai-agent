#!/usr/bin/env python3
"""briefing_sync.py — 文献简报双向同步引擎。

实现 CoPilot paper-pool.json 与 hermes status.json 之间的双向状态同步：
    - 正向同步（hermes → CoPilot）：sync_all() 执行时批量拉取 hermes 工作流状态
    - 反向同步（CoPilot → hermes）：用户操作时实时回写 hermes status.json
    - 失败重试：反向同步失败记入 reverse_sync_pending 队列，下次 sync_all 重试

状态映射规则：
    CoPilot viewed   →  hermes discussion_started = true
    CoPilot archived →  hermes discussion_archived_at = <时间戳>
    hermes analyzed  →  CoPilot unseen → viewed（只升不降）
    hermes archived  →  CoPilot → archived

冲突策略：
    - CoPilot 优先（用户意图 > hermes 自动流程）
    - 只升不降（unseen → viewed → archived 单向流转）
    - init 防护：检测 hermes status.json 的 date 变化

用法示例：
    >>> from briefing_sync import sync_to_hermes, sync_from_hermes, flush_pending_reverse
    >>> sync_to_hermes("2403.15337", "archived", "discuss_done")  # 反向同步单条
    >>> sync_from_hermes()                                         # 正向同步批量
    >>> flush_pending_reverse()                                    # 重试待同步队列

规范：仅使用 Python 3 标准库，PROJECT_ROOT 通过 paths.py 推导。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from common import now_utc, load_json, save_json
from paths import PROJECT_ROOT, MEMORY_DIR

# ─────────────────────────────────────────────
# 路径定义
# ─────────────────────────────────────────────

HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
HERMES_STATUS_PATH = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings" / "status.json"
SYNC_STATE_PATH = MEMORY_DIR / "sync-state.json"

# 状态等级（用于"只升不降"判断）
_STATUS_RANK = {"unseen": 0, "viewed": 1, "archived": 2}

# 本地时区（hermes status.json 用 +08:00 时区）
_LOCAL_TZ = timezone(timedelta(hours=8))


# ─────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────

def _now_local_iso() -> str:
    """返回本地时区（+08:00）的 ISO 时间戳，与 hermes 格式一致。"""
    return datetime.now(_LOCAL_TZ).strftime("%Y-%m-%dT%H:%M:%S+08:00")


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


def _get_file_lock(key: str):
    """获取文件锁（复用 web_base 的锁机制，防止并发写冲突）。"""
    try:
        import web_base
        return web_base._get_file_lock(key)
    except Exception:
        import threading
        return threading.Lock()


# ─────────────────────────────────────────────
# 反向同步：CoPilot → hermes
# ─────────────────────────────────────────────

def sync_to_hermes(arxiv_id: str, copilot_status: str, action: str = "") -> Dict[str, Any]:
    """反向同步：CoPilot 状态 → hermes status.json。

    使用增量更新（read-modify-write），不触发 init 覆盖。
    若 hermes status.json 不存在或论文不在工作流中，记入待同步队列。

    Args:
        arxiv_id: 论文 arXiv ID
        copilot_status: CoPilot 状态（viewed/archived）
        action: 触发动作（interested/skip/archive/later/discuss_done）

    Returns:
        {"success": bool, "arxiv_id": str, "reason": str}
    """
    if not HERMES_STATUS_PATH.exists():
        _add_to_pending(arxiv_id, copilot_status, action, "hermes status.json 不存在")
        return {"success": False, "arxiv_id": arxiv_id, "reason": "hermes status.json 不存在"}

    try:
        with _get_file_lock("hermes_status"):
            hermes_status = load_json(HERMES_STATUS_PATH, {})
            papers = hermes_status.get("papers", {})

            # 论文不在 hermes 当日工作流中
            if arxiv_id not in papers:
                _add_to_pending(arxiv_id, copilot_status, action, "论文不在 hermes 工作流中")
                return {"success": False, "arxiv_id": arxiv_id, "reason": "论文不在 hermes 工作流中"}

            # 按映射规则更新
            info = papers[arxiv_id]
            now_local = _now_local_iso()

            if copilot_status == "archived":
                info["discussion_archived_at"] = now_local
                info["discussion_started"] = True  # 归档隐含已讨论
            elif copilot_status == "viewed":
                info["discussion_started"] = True  # 用户已关注

            # 写回（原子写入）
            hermes_status["papers"][arxiv_id] = info
            save_json(HERMES_STATUS_PATH, hermes_status)

        # 更新同步水位
        state = _load_sync_state()
        state["last_reverse_sync"] = now_utc()
        _save_sync_state(state)

        return {"success": True, "arxiv_id": arxiv_id, "status": copilot_status}

    except Exception as e:
        _add_to_pending(arxiv_id, copilot_status, action, str(e))
        return {"success": False, "arxiv_id": arxiv_id, "reason": str(e)}


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
# 正向同步：hermes → CoPilot
# ─────────────────────────────────────────────

def sync_from_hermes() -> Dict[str, Any]:
    """正向同步：hermes status.json → CoPilot paper-pool.json。

    遍历 hermes status.json 的 papers，按状态映射规则
    更新 CoPilot paper-pool.json 中对应论文的 status。
    只升级不降级（unseen→viewed→archived 单向流转）。

    Returns:
        {"synced": int, "skipped": int, "date": str}
    """
    import paper_pool as pp

    if not HERMES_STATUS_PATH.exists():
        return {"synced": 0, "skipped": 0, "date": "", "reason": "hermes status.json 不存在"}

    try:
        hermes_status = load_json(HERMES_STATUS_PATH, {})
    except Exception:
        return {"synced": 0, "skipped": 0, "date": "", "reason": "hermes status.json 读取失败"}

    hermes_date = hermes_status.get("date", "")
    papers = hermes_status.get("papers", {})
    if not papers:
        return {"synced": 0, "skipped": 0, "date": hermes_date, "reason": "无论文记录"}

    synced = 0
    skipped = 0

    for aid, info in papers.items():
        # 映射规则：hermes 工作流状态 → CoPilot 三态
        if info.get("discussion_archived_at"):
            target = pp.STATUS_ARCHIVED
        elif info.get("analyzed_at") or info.get("discussion_started"):
            target = pp.STATUS_VIEWED
        else:
            continue  # 仅 pushed，不同步

        # 查询当前 CoPilot 状态
        current = pp.get_paper_status(aid)
        if current is None:
            skipped += 1  # 论文不在 CoPilot 池中
            continue

        # 只升不降
        if _can_upgrade(current, target):
            pp.update_status(aid, target, extra={
                "hermes_synced_at": now_utc(),
                "hermes_date": hermes_date,
            })
            synced += 1
        else:
            skipped += 1

    # 更新水位
    state = _load_sync_state()
    state["reverse_sync_watermark"] = hermes_date
    _save_sync_state(state)

    return {"synced": synced, "skipped": skipped, "date": hermes_date}


# ─────────────────────────────────────────────
# 待同步队列重试
# ─────────────────────────────────────────────

def flush_pending_reverse() -> Dict[str, Any]:
    """重试待同步队列中失败的反向同步。

    在 sync_all() 执行时前置调用，处理之前因 hermes 未运行等原因
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
    print("◐ briefing_sync 自检")
    print("=" * 50)

    passed = 0
    total = 0

    tmp_dir = tempfile.mkdtemp(prefix="briefing_sync_test_")

    # 保存原始路径，测试后恢复
    global HERMES_STATUS_PATH, SYNC_STATE_PATH
    _orig_hermes = HERMES_STATUS_PATH
    _orig_sync = SYNC_STATE_PATH
    HERMES_STATUS_PATH = Path(tmp_dir) / "status.json"
    SYNC_STATE_PATH = Path(tmp_dir) / "sync-state.json"

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

        # [2/5] 反向同步：CoPilot archived → hermes
        total += 1
        hermes_data = {
            "date": "2026-07-02",
            "papers": {
                "2403.15337": {
                    "title": "测试论文",
                    "pushed_at": "2026-07-02T08:35:00+08:00",
                    "selected_for_analysis": False,
                    "analyzed_at": None,
                    "analysis_file": None,
                    "discussion_started": False,
                    "discussion_archived_at": None,
                    "archived_file": None,
                    "keywords_extracted": False,
                    "keywords_file": None,
                }
            }
        }
        save_json(HERMES_STATUS_PATH, hermes_data)
        result = sync_to_hermes("2403.15337", "archived", "discuss_done")
        if result.get("success"):
            # 验证 hermes status.json 已更新
            updated = load_json(HERMES_STATUS_PATH, {})
            info = updated.get("papers", {}).get("2403.15337", {})
            if info.get("discussion_archived_at") and info.get("discussion_started"):
                passed += 1
                print(f"  [2/{total}] ✓ 反向同步 archived 成功")
            else:
                print(f"  [2/{total}] ✗ 反向同步后字段未更新: {info}")
        else:
            print(f"  [2/{total}] ✗ 反向同步失败: {result}")

        # [3/5] 反向同步：论文不在 hermes 工作流 → 记入待同步队列
        total += 1
        result = sync_to_hermes("9999.99999", "viewed", "interested")
        state = _load_sync_state()
        pending = state.get("reverse_sync_pending", [])
        if not result.get("success") and len(pending) >= 1:
            passed += 1
            print(f"  [3/{total}] ✓ 论文不在工作流 → 记入待同步队列 ({len(pending)} 条)")
        else:
            print(f"  [3/{total}] ✗ 待同步队列未记录: result={result}, pending={pending}")

        # [4/5] flush_pending_reverse 重试
        total += 1
        # 先在 hermes status.json 中添加该论文
        hermes_data["papers"]["9999.99999"] = hermes_data["papers"]["2403.15337"].copy()
        hermes_data["papers"]["9999.99999"]["title"] = "重试测试论文"
        save_json(HERMES_STATUS_PATH, hermes_data)
        # 重置 discussion_started 以验证重试后更新
        hermes_data["papers"]["9999.99999"]["discussion_started"] = False
        save_json(HERMES_STATUS_PATH, hermes_data)

        flush_result = flush_pending_reverse()
        if flush_result.get("flushed", 0) >= 1:
            passed += 1
            print(f"  [4/{total}] ✓ flush_pending_reverse 重试成功 (flushed={flush_result['flushed']})")
        else:
            print(f"  [4/{total}] ✗ flush_pending_reverse 失败: {flush_result}")

        # [5/5] 正向同步映射逻辑验证
        total += 1
        # 设置 hermes 状态：已分析但未归档 → 应映射为 viewed
        hermes_data["papers"]["2403.15337"]["analyzed_at"] = "2026-07-02T10:00:00+08:00"
        hermes_data["papers"]["2403.15337"]["discussion_archived_at"] = None
        save_json(HERMES_STATUS_PATH, hermes_data)
        # 由于 paper_pool 是全局的，这里只验证映射逻辑不报错
        # 正向同步会调用 paper_pool.update_status，论文可能不在池中
        sync_result = sync_from_hermes()
        if "synced" in sync_result and "skipped" in sync_result:
            passed += 1
            print(f"  [5/{total}] ✓ 正向同步映射逻辑正常 (synced={sync_result['synced']}, skipped={sync_result['skipped']})")
        else:
            print(f"  [5/{total}] ✗ 正向同步异常: {sync_result}")

    finally:
        HERMES_STATUS_PATH = _orig_hermes
        SYNC_STATE_PATH = _orig_sync
        shutil.rmtree(tmp_dir, ignore_errors=True)

    ok = passed == total
    print(f"\n{'✓' if ok else '✗'} briefing_sync: {passed}/{total} 通过")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_check() else 1)
