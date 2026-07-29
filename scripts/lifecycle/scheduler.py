#!/usr/bin/env python3
"""生命周期 cron 框架调度层。"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

import hermes_bridge as hb
from common import now_utc
from paths import PROJECT_ROOT

from .constants import HERMES_PROFILE

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


def _lifecycle_cron_prefix(self) -> str:
    return "lc-"

def list_lifecycle_crons(self) -> List[Dict[str, Any]]:
    """列出当前 hermes 中所有 lc- 开头的 cron job。"""
    jobs = hb.cron_list_profile(HERMES_PROFILE)
    return [j for j in jobs if j.get("name", "").startswith(self._lifecycle_cron_prefix())]

def _compute_worker_minute(self, proposal_id: str) -> int:
    """为 proposal 计算 worker cron 触发分钟，多个 worker 之间错开 6 分钟。

    优先读取 proposal state 中已持久化的 worker_minute，保证删除重建后不变。
    首次创建时基于 proposal_id hash 分配固定偏移（0-9），再映射到 47, 53, 59, 05, ...，
    使多个 worker 自然错开，且不依赖外部 hermes cron 列表。
    """
    prop_state = self._get_proposal_state(proposal_id)
    if prop_state and prop_state.get("worker_minute") is not None:
        return int(prop_state["worker_minute"])

    # 使用稳定哈希让分布均匀且跨运行一致，避免连续相似 ID 落在同一 bucket
    import hashlib
    h = int(hashlib.md5(proposal_id.encode("utf-8")).hexdigest(), 16)
    offset = h % 10
    minute = (47 + offset * 6) % 60

    # 持久化到 proposal state
    if prop_state:
        prop_state["worker_minute"] = minute
        prop_state["updated_at"] = now_utc()
        self._set_proposal_state(proposal_id, prop_state)

    return minute

def schedule_worker(self, proposal_id: str, interval: Optional[str] = None) -> Dict[str, Any]:
    """为 proposal 创建/更新 worker cron。幂等（按名称去重）。

    默认自动错开且仅在周中运行：多个 worker 之间间隔 6 分钟，schedule 为
    `{minute} * * * 1-5`。可通过 interval 参数强制指定。
    """
    script_path = self._worker_script_for_proposal(proposal_id)
    name = f"lc-worker-{proposal_id}"
    # 先检查是否已存在 active
    existing = self.list_lifecycle_crons()
    for job in existing:
        if job.get("name") == name and job.get("status") == "active":
            return {"success": True, "message": "worker 已存在", "cron_job_id": job.get("id")}

    if interval:
        schedule = interval
    else:
        minute = self._compute_worker_minute(proposal_id)
        schedule = f"{minute} * * * 1-5"

    result = hb.cron_create_no_agent(
        script_name=script_path.name,
        name=name,
        schedule=schedule,
        workdir=str(PROJECT_ROOT),
        profile=HERMES_PROFILE,
    )
    return result

def remove_worker(self, proposal_id: str) -> Dict[str, Any]:
    name = f"lc-worker-{proposal_id}"
    existing = self.list_lifecycle_crons()
    for job in existing:
        if job.get("name") == name:
            return hb.cron_delete(job.get("id"), profile=HERMES_PROFILE)
    return {"success": True, "message": "worker 不存在"}