#!/usr/bin/env python3
"""多端同步层 —— 把 hermes 各端（本地/飞书/Web）的产出汇聚到林赛知识库。

用途：
    定时扫描 hermes linsai profile 的新会话和文献产出，导入林赛知识库，
    使无论用户在哪个端（本地 hermes、飞书机器人、Web 界面）产生的讨论和文献，
    最终都能在林赛 CoPilot Web 端看到、检索到。

同步方向：
    hermes 产出 → 林赛知识库（单向导入，标记来源）
    - 文献产出（daily_candidates / deep_analysis）→ knowledge/raw + wiki/projects/文献简报
    - hermes 会话（sessions/）→ wiki/projects/文献简报/讨论记录（提取讨论内容）

去重机制：
    用 memory/sync-state.json 记录已同步的 session_id 和文献 arxiv_id，
    避免重复导入。

用法示例：
    >>> from sync_engine import sync_all, sync_hermes_sessions, sync_hermes_outputs
    >>> result = sync_all()                      # 全量同步
    >>> print(f"新增 {result['new_sessions']} 会话, {result['new_papers']} 文献")

程序化调用（可由 Web/API 或 cron 触发）：
    >>> from sync_engine import sync_all
    >>> sync_all()

规范：
    - 仅使用 Python 3 标准库
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - 同步是幂等的（重复运行不会重复导入）
    - 导入失败不阻塞（记录错误，继续处理其他）
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from common import now_utc as _now_utc

from paths import PROJECT_ROOT, MEMORY_DIR
SYNC_STATE_PATH = MEMORY_DIR / "sync-state.json"

# hermes linsai profile 路径
HERMES_HOME = Path.home() / ".hermes"
LINSAI_PROFILE = HERMES_HOME / "profiles" / "linsai"
LINSAI_SESSIONS = LINSAI_PROFILE / "sessions"

# hermes 文献产出
HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
BRIEFINGS_DIR = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings"


def _load_sync_state() -> Dict[str, Any]:
    """加载同步状态（记录已同步的 ID）。"""
    if not SYNC_STATE_PATH.exists():
        return {
            "synced_sessions": [],
            "synced_papers": [],
            "last_sync": "",
            "history": [],
        }
    try:
        return json.loads(SYNC_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"synced_sessions": [], "synced_papers": [], "last_sync": "", "history": []}


def _save_sync_state(state: Dict[str, Any]) -> None:
    """保存同步状态。"""
    state["last_sync"] = _now_utc()
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    SYNC_STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _import_kb_helper():
    """动态导入 knowledge_base 模块（供 sync_all 自动重建用）。"""
    import importlib.util
    kb_path = PROJECT_ROOT / "scripts" / "knowledge_base.py"
    spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
    kb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb)
    return kb


def sync_hermes_sessions(max_count: int = 50) -> Dict[str, Any]:
    """同步 hermes linsai 的新会话到林赛讨论记录。

    扫描 hermes sessions/ 目录，将未同步的会话导入为讨论记录。
    跳过无实质内容的会话（如纯工具调用、空会话）。

    Args:
        max_count: 单次最多同步的会话数（防止一次导入过多）

    Returns:
        {new_sessions, skipped, errors}
    """
    # 延迟导入（避免循环依赖）
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from kb_importer import import_session_discussion

    state = _load_sync_state()
    synced_ids = set(state.get("synced_sessions", []))

    if not LINSAI_SESSIONS.exists():
        return {"new_sessions": 0, "skipped": 0, "errors": 0, "reason": "sessions 目录不存在"}

    # 扫描会话文件（按修改时间倒序）
    session_files = sorted(
        LINSAI_SESSIONS.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    new_count = 0
    skipped = 0
    errors = 0

    for sf in session_files:
        if new_count >= max_count:
            break

        # 用文件名作为唯一标识（含时间戳，天然唯一）
        session_key = sf.stem
        if session_key in synced_ids:
            skipped += 1
            continue

        # 只同步有实质内容的会话（消息数 > 2，且含用户输入）
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
            messages = data.get("messages", [])
            has_user = any(m.get("role") == "user" for m in messages)
            if len(messages) < 3 or not has_user:
                skipped += 1
                synced_ids.add(session_key)  # 标记已处理，避免重复扫描
                continue

            # 检测平台来源
            platform = data.get("platform", "local")

            # 导入为讨论记录
            result = import_session_discussion(sf, project="文献简报")
            if result:
                new_count += 1
                synced_ids.add(session_key)
            else:
                errors += 1
                synced_ids.add(session_key)  # 失败也标记，避免反复尝试
        except Exception:
            errors += 1
            synced_ids.add(session_key)

    # 更新状态
    state["synced_sessions"] = list(synced_ids)[-500:]  # 保留最近 500 条记录
    _save_sync_state(state)

    return {"new_sessions": new_count, "skipped": skipped, "errors": errors}


def sync_hermes_outputs() -> Dict[str, Any]:
    """同步 hermes 文献产出到林赛知识库。

    扫描 daily_candidates.json，将未导入的候选论文导入 raw/papers/。
    注意：不自动导入深度解析（需用户在 Web 端勾选）。

    Returns:
        {new_papers, skipped, errors}
    """
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from kb_importer import _load_candidates, import_candidate

    state = _load_sync_state()
    synced_papers = set(state.get("synced_papers", []))

    candidates = _load_candidates()
    papers = candidates.get("papers", [])

    if not papers:
        return {"new_papers": 0, "skipped": 0, "errors": 0, "reason": "无候选论文"}

    new_count = 0
    skipped = 0
    errors = 0

    for p in papers:
        aid = p.get("arxiv_id", "")
        if not aid:
            continue
        if aid in synced_papers:
            skipped += 1
            continue

        result = import_candidate(aid)
        if result:
            new_count += 1
            synced_papers.add(aid)
        else:
            errors += 1
            synced_papers.add(aid)

    state["synced_papers"] = list(synced_papers)[-500:]
    _save_sync_state(state)

    return {"new_papers": new_count, "skipped": skipped, "errors": errors}


def sync_all() -> Dict[str, Any]:
    """全量同步：待同步重试 + 会话 + 文献产出 + 简报状态。

    Returns:
        {new_sessions, new_papers, skipped_sessions, skipped_papers, errors, timestamp}
    """
    print("◐ 开始多端同步...")

    # [0/5] 重试失败的反向同步（CoPilot→hermes）
    print("  [0/5] 重试待同步队列...")
    try:
        import briefing_sync as bsync
        flush_result = bsync.flush_pending_reverse()
        if flush_result.get("flushed", 0) > 0:
            print(f"    重试成功 {flush_result['flushed']} 条，剩余 {flush_result['remaining']} 条")
        elif flush_result.get("remaining", 0) > 0:
            print(f"    仍有 {flush_result['remaining']} 条待重试")
        else:
            print(f"    无待同步项")
    except Exception as e:
        print(f"  ⚠ 待同步重试失败: {e}")

    print("  [1/5] 同步 hermes 会话...")
    sess_result = sync_hermes_sessions()
    print(f"    新增 {sess_result['new_sessions']} 会话, 跳过 {sess_result['skipped']}")

    print("  [2/5] 同步文献产出...")
    paper_result = sync_hermes_outputs()
    print(f"    新增 {paper_result['new_papers']} 文献, 跳过 {paper_result['skipped']}")

    # [2.5/5] 正向同步简报状态（hermes→CoPilot）
    print("  [2.5/5] 同步简报状态（hermes→CoPilot）...")
    briefing_result = {"synced": 0, "skipped": 0}
    try:
        briefing_result = bsync.sync_from_hermes()
        if briefing_result.get("synced", 0) > 0:
            print(f"    状态升级 {briefing_result['synced']} 篇，跳过 {briefing_result['skipped']} 篇")
        else:
            print(f"    无状态需升级（跳过 {briefing_result.get('skipped', 0)} 篇）")
    except Exception as e:
        print(f"  ⚠ 简报状态同步失败: {e}")

    # 记录同步历史
    state = _load_sync_state()
    state["history"].append({
        "timestamp": _now_utc(),
        "new_sessions": sess_result["new_sessions"],
        "new_papers": paper_result["new_papers"],
        "briefing_synced": briefing_result.get("synced", 0),
    })
    state["history"] = state["history"][-20:]  # 保留最近 20 次记录
    _save_sync_state(state)

    total_new = sess_result["new_sessions"] + paper_result["new_papers"]

    # 同步后自动重建索引和图谱（v3.1 自维护闭环）
    if total_new > 0:
        print("  [3/5] 重建索引和图谱...")
        try:
            import sys
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
            from kb_maintenance import cmd_reindex, cmd_rebuild_graph
            kb = _import_kb_helper()
            cmd_reindex(kb)
            cmd_rebuild_graph(kb)
        except Exception as e:
            print(f"  ⚠ 自动重建失败: {e}")

        # v3.4: 认知回流 — 从新同步的 hermes 会话中提炼记忆
        print("  [4/5] 认知回流（记忆提炼）...")
        try:
            from memory_reflow import reflow_all
            reflow_result = reflow_all(max_count=20)
            if reflow_result.get("processed", 0) > 0:
                print(f"    提炼 {reflow_result['processed']} 个会话 → {reflow_result['stats']['snippets']} 条记忆片段")
            else:
                print(f"    无新会话需提炼")
        except Exception as e:
            print(f"  ⚠ 认知回流失败: {e}")

        print(f"✓ 同步完成：新增 {total_new} 项，索引/图谱/记忆已更新")
    else:
        print("✓ 同步完成：无新增（已是最新）")

    return {
        "new_sessions": sess_result["new_sessions"],
        "new_papers": paper_result["new_papers"],
        "briefing_synced": briefing_result.get("synced", 0),
        "skipped_sessions": sess_result["skipped"],
        "skipped_papers": paper_result["skipped"],
        "errors": sess_result["errors"] + paper_result["errors"],
        "timestamp": _now_utc(),
    }


def get_sync_status() -> Dict[str, Any]:
    """返回同步状态（供 Web 展示）。"""
    state = _load_sync_state()
    return {
        "last_sync": state.get("last_sync", ""),
        "synced_sessions_count": len(state.get("synced_sessions", [])),
        "synced_papers_count": len(state.get("synced_papers", [])),
        "history": state.get("history", [])[-5:],
    }


def _self_check() -> None:
    """自检：验证同步链路（不实际导入）。"""
    print("=" * 50)
    print("◐ sync_engine 自检")
    print("=" * 50)

    print("\n[1/5] 检查数据源...")
    print(f"  hermes sessions: {'✓' if LINSAI_SESSIONS.exists() else '✗'}")
    if LINSAI_SESSIONS.exists():
        count = len(list(LINSAI_SESSIONS.glob("*.json")))
        print(f"    {count} 个会话文件")
    print(f"  hermes 文献产出: {'✓' if BRIEFINGS_DIR.exists() else '✗'}")

    print("\n[2/5] 同步状态文件...")
    state = _load_sync_state()
    print(f"  已同步会话: {len(state.get('synced_sessions', []))}")
    print(f"  已同步文献: {len(state.get('synced_papers', []))}")
    print(f"  待同步队列: {len(state.get('reverse_sync_pending', []))} 条")
    print(f"  上次同步: {state.get('last_sync', '从未')}")

    print("\n[3/5] 验证去重机制...")
    # 模拟：连续调用 sync_all 应幂等（第二次无新增）
    # 不实际调用（会修改状态），只验证函数可用
    assert callable(sync_all), "sync_all 不可调用"
    assert callable(sync_hermes_sessions), "sync_hermes_sessions 不可调用"
    assert callable(sync_hermes_outputs), "sync_hermes_outputs 不可调用"
    print("  ✓ 同步函数就绪")

    print("\n[4/5] 双向同步模块...")
    try:
        import briefing_sync as bsync
        assert callable(bsync.sync_to_hermes), "sync_to_hermes 不可调用"
        assert callable(bsync.sync_from_hermes), "sync_from_hermes 不可调用"
        assert callable(bsync.flush_pending_reverse), "flush_pending_reverse 不可调用"
        print("  ✓ briefing_sync 就绪")
    except ImportError:
        print("  ⚠ briefing_sync 未安装")

    print("\n[5/5] 同步状态查询...")
    status = get_sync_status()
    print(f"  历史记录: {len(status['history'])} 条")

    print("\n✓ sync_engine 自检通过")


if __name__ == "__main__":
    _self_check()
