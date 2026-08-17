from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import shutil

from common import now_utc

import proposal_lifecycle as _pl

from proposal_lifecycle.constants import (
    _log,
    LIFECYCLE_STAGES,
    PROJECT_TYPES,
    PROPOSALS_ROOT,
)


class TransitionsMixin:
    # ------------------------------------------------------------------
    # 状态流转
    # ------------------------------------------------------------------

    def transition(
        self,
        proposal_id: str,
        to_stage: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """流转 proposal 到指定阶段。

        Args:
            proposal_id: 课题 ID
            to_stage: 目标阶段（drafts/optimizing/pending_review/archived）
            reason: 流转原因

        Returns:
            {success, from_stage, to_stage, path}
        """
        if to_stage not in LIFECYCLE_STAGES:
            return {"success": False, "error": f"非法阶段: {to_stage}"}

        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": f"proposal 未注册: {proposal_id}"}

        from_stage = prop_state["status"]
        if from_stage == to_stage:
            return {"success": False, "error": f"已在 {to_stage} 阶段"}

        # 移动目录
        from_dir = self.root / from_stage / proposal_id
        to_dir = self.root / to_stage / proposal_id
        if not from_dir.exists():
            return {"success": False, "error": f"源目录不存在: {from_dir}"}

        to_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(from_dir), str(to_dir))

        # 更新状态
        prop_state["status"] = to_stage
        prop_state["updated_at"] = now_utc()
        prop_state["transition_history"].append({
            "from": from_stage, "to": to_stage, "at": now_utc(), "reason": reason
        })

        # 审核退回：pending_review → optimizing 时归零优化轮次
        if from_stage == "pending_review" and to_stage == "optimizing":
            prop_state["optimization_rounds"] = 0
            # v6.9.24: 归零轮次时同步归档清理旧轮次残留 job。
            # 此前仅归零计数器，退回前生命周期的 done/pending job 全部残留
            # pipeline_jobs：_compute_actual_round 按"整轮 done"向上扫描会
            # 消耗旧 done 轮次直接跳轮（实测 bsv 2026-08-15 退回后残留
            # r7 done×29 + r8 done×23/pending×2，新进度到 r6 完成后将被
            # 一次性推到 r8=DEFAULT_MAX_ROUNDS 提前触顶流转，损失 2 轮
            # 优化；r8-derived 残留还会在轮末空窗被误调度）。归档遵循
            # "产出即资产"原则，job 证据不丢弃。
            raw_jobs = prop_state.get("pipeline_jobs") or []
            old_jobs = [
                j for j in (raw_jobs.values() if isinstance(raw_jobs, dict) else raw_jobs)
                if isinstance(j, dict)
            ]
            if old_jobs:
                try:
                    from lifecycle.utils import append_archive_jobs
                    append_archive_jobs(proposal_id, old_jobs)
                except Exception as e:
                    if _log:
                        _log.warning(f"[{proposal_id}] 归档退回前旧 job 失败（继续清空）: {e}")
            prop_state["pipeline_jobs"] = []
            if _log:
                _log.info(
                    f"[{proposal_id}] 审核退回，归零 optimization_rounds，"
                    f"归档清理旧轮次 job {len(old_jobs)} 个"
                )

        self._set_proposal_state(proposal_id, prop_state)

        if _log:
            _log.info(f"流转 {proposal_id}: {from_stage} → {to_stage} ({reason})")

        # v6.7.10: 进入 optimizing 时自动执行初始化，确保四大产物和 7 个申请书模块就位
        init_result = None
        if to_stage == "optimizing":
            try:
                init_result = self.initialize_for_optimization(proposal_id)
                if _log and init_result.get("success"):
                    _log.info(f"[{proposal_id}] 进入 optimizing 后自动初始化完成")
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 进入 optimizing 后初始化失败: {e}")

        # 更新 proposal-brief（状态变更后）
        try:
            self.update_proposal_brief(proposal_id)
        except Exception:
            pass

        # v6.8.33: 状态流转事件钩子——按目标阶段同步/清理知识库镜像。
        # 归档→清理活跃镜像（已由 feedback_archive 写入 knowledge/raw）；
        # 其他流转（晋级 pending_review / 退回 optimizing）→ 刷新镜像保持一致。
        try:
            if to_stage == "archived":
                from proposal_kb_sync import cleanup_kb_mirror
                cleanup_kb_mirror(proposal_id)
            else:
                from lifecycle.micro_scheduler import _sync_proposal_to_kb
                _sync_proposal_to_kb(proposal_id)
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 流转({to_stage})KB 钩子失败: {e}")

        return {
            "success": True,
            "proposal_id": proposal_id,
            "from_stage": from_stage,
            "to_stage": to_stage,
            "path": str(to_dir.relative_to(_pl.PROJECT_ROOT)),
            "init_result": init_result,
        }

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    def list_by_status(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """按状态列出 proposal。"""
        state = self._load_state()
        proposals = []
        for pid, data in state["proposals"].items():
            if status and data.get("status") != status:
                continue
            proposals.append({
                "proposal_id": pid,
                "status": data.get("status"),
                "project_type": data.get("project_type", "general"),
                "optimization_rounds": data.get("optimization_rounds", 0),
                "last_score": data.get("last_score", 0.0),
                "updated_at": data.get("updated_at", ""),
            })
        return proposals

    def get_dashboard(self) -> Dict[str, Any]:
        """获取仪表盘数据。"""
        state = self._load_state()
        dashboard = {
            "total": len(state["proposals"]),
            "by_status": {},
            "by_type": {},
            "proposals": state["proposals"],
        }
        for stage in LIFECYCLE_STAGES:
            dashboard["by_status"][stage] = sum(
                1 for d in state["proposals"].values() if d.get("status") == stage
            )
        for ptype in PROJECT_TYPES:
            dashboard["by_type"][ptype] = sum(
                1 for d in state["proposals"].values() if d.get("project_type") == ptype
            )
        return dashboard
