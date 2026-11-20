from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from common import now_utc, load_json, save_json, file_lock

import proposal_lifecycle as _pl

from proposal_lifecycle.constants import (
    _log,
    LIFECYCLE_STAGES,
)


class StateMixin:
    """提案生命周期管理器。"""

    def __init__(self) -> None:
        self.root = _pl.PROPOSALS_ROOT
        self.lifecycle_path = self.root / "_lifecycle.json"
        self.standards_path = _pl.PROJECT_ROOT / "memory" / "nsfc-standards.json"
        self.root.mkdir(parents=True, exist_ok=True)
        for stage in LIFECYCLE_STAGES:
            (self.root / stage).mkdir(parents=True, exist_ok=True)
        self._ensure_lifecycle_state()

    # ------------------------------------------------------------------
    # 状态管理
    # ------------------------------------------------------------------

    def _ensure_lifecycle_state(self) -> None:
        """确保全局生命周期状态文件存在。"""
        if not self.lifecycle_path.exists():
            default = {
                "proposals": {},  # {proposal_id: {status, project_type, ...}}
                "updated_at": now_utc(),
            }
            save_json(self.lifecycle_path, default)

    def _load_state(self) -> Dict[str, Any]:
        return load_json(self.lifecycle_path, default={"proposals": {}})

    def _save_state(self, state: Dict[str, Any]) -> None:
        state["updated_at"] = now_utc()
        save_json(self.lifecycle_path, state)

    def _get_proposal_state(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        state = self._load_state()
        return state["proposals"].get(proposal_id)

    def _set_proposal_state(
        self,
        proposal_id: str,
        data: Dict[str, Any],
        update_jobs: bool = False,
    ) -> bool:
        """持久化单个 proposal 状态，返回是否成功。

        v6.7.1 修复：
        - 写入后重新读取校验，避免并发覆盖导致的状态丢失
        - 校验失败时最多重试 2 次

        v7.2.50（BUG-15）：`pipeline_jobs` 默认不由本函数管辖。
        旧实现整份替换 proposal 条目 → 把调用方**锁外旧快照**里的
        pipeline_jobs 一并写回，与并发写者（`_save_jobs` / archive）交叉时
        对方的 job 终态被整份丢弃（job 回退 pending → 被重复执行，整轮
        LLM 重跑）。生产实测更严重的一环：monitor 步骤先
        `archive_old_round_jobs` 从磁盘删除旧轮次 job，随后本函数用旧
        快照把已归档的 job **复活**（实测 9 课题 251 条旧轮次 job 同时
        存在于活链与归档文件，双重计数）。

        现改为：锁内重读磁盘上的最新 pipeline_jobs 并保留（除非调用方
        显式声明 `update_jobs=True`——如「审核退回清空旧 job」这类
        确有改写意图的场景）。调用方传入的 `data` 通常来自
        `_get_proposal_state()`，天然带着读快照时的 pipeline_jobs，
        故不能用「key 是否存在」判断意图，必须用显式开关。
        """
        for attempt in range(3):
            try:
                with file_lock("proposal-lifecycle"):
                    state = self._load_state()
                    # v7.2.50：pipeline_jobs 由 _save_jobs 独占写入，本函数
                    # 默认不再回写调用方的旧快照，避免丢弃并发写者的终态。
                    disk_prop = (state.get("proposals") or {}).get(proposal_id) or {}
                    merged_prop = dict(data)
                    if not update_jobs:
                        disk_jobs = disk_prop.get("pipeline_jobs")
                        if disk_jobs is not None:
                            merged_prop["pipeline_jobs"] = disk_jobs
                    state["proposals"][proposal_id] = merged_prop
                    self._save_state(state)

                    # 写入后校验：重新读取确认 proposal 数据已持久化
                    verify = self._load_state()
                    persisted = verify["proposals"].get(proposal_id, {})
                    if persisted.get("updated_at") == data.get("updated_at"):
                        return True
                    # 校验失败：可能被其他进程覆盖，重试
                    if _log:
                        _log.warning(
                            f"[_set_proposal_state] {proposal_id} 写入校验失败，"
                            f"第 {attempt + 1} 次重试"
                        )
            except Exception as e:
                if _log:
                    _log.error(f"[_set_proposal_state] {proposal_id} 写入异常: {e}")
        return False

    def _find_proposal_dir(self, proposal_id: str) -> Optional[Path]:
        """在四个阶段目录中查找 proposal 目录。"""
        for stage in LIFECYCLE_STAGES:
            d = self.root / stage / proposal_id
            if d.exists():
                return d
        return None
