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

    def _set_proposal_state(self, proposal_id: str, data: Dict[str, Any]) -> bool:
        """持久化单个 proposal 状态，返回是否成功。

        v6.7.1 修复：
        - 写入后重新读取校验，避免并发覆盖导致的状态丢失
        - 校验失败时最多重试 2 次
        """
        for attempt in range(3):
            try:
                with file_lock("proposal-lifecycle"):
                    state = self._load_state()
                    state["proposals"][proposal_id] = data
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
