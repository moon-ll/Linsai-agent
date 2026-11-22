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

        语义约定（v6.10.50，用户裁决）：archived 是**人工审查通过的荣誉
        状态**——只收验收通过的课题；立项阶段被否的设想走 rejected_ideas
        台账（_lifecycle.json）+ _rejected-ideas/ 目录，不得进 archived。

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
            # v6.9.41: score_history 按遍次归档（P0）+ 退回对比报告（P1）。
            # 此前退回只清 rounds/job 不清 score_history，第二遍的 r1-r3 与
            # 第一遍的 r1-r8 混叠在同一数组（08-23 实测多课题两遍叠加），
            # 轨迹分析/毕业报告全建立在污染数据上。归档后生成"本遍 vs
            # 上遍"对比报告，回答"反馈注入为什么没打破天花板"。
            try:
                from proposal_lifecycle.pass_history import (
                    archive_pass_history,
                    generate_return_comparison,
                )
                archived = archive_pass_history(prop_state, reason=reason)
                if _log:
                    _log.info(
                        f"[{proposal_id}] 第 {prop_state.get('pass_number', 1) - 1} 遍 "
                        f"score_history 已归档（{archived} 条），开启第 "
                        f"{prop_state.get('pass_number', 1)} 遍"
                    )
                # 对比报告：有上一遍数据才生成。本分支在目录移动之后执行，
                # to_dir 即课题新位置，报告落盘其 05_review/ 子目录。
                report = generate_return_comparison(
                    proposal_id, prop_state, to_dir)
                if report and _log:
                    _log.info(f"[{proposal_id}] 退回对比报告: {report}")
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 遍次归档/对比报告失败（不阻断退回）: {e}")

            # v7.3.3: 退回时清理跨遍残留状态（实测 2026-11-03 三类污染）：
            # ① quality_warning 残留上一遍逃生阀文案（"达到最大轮数8…已通过
            #    0/5模块"）——决策包/看板展示误导人工裁量；只保留守卫类
            #    当前行（writer 每轮刷新的 KB引用/6章节缺）。
            # ② negative_feedback_alert 带着旧遍原因进入新遍（moire/bsv：
            #    at 早于退回数天）——退回本身即人工干预，负反馈目的已达成。
            # ③ monitor_history 跨遍连续性污染（attosecond/ssh-weyl：退回后
            #    首个 monitor 步把旧遍尾部 2 条与新遍 1 条拼成"连续 3 轮
            #    下降"）——记录本遍起始索引，连续性判定（check_negative_
            #    feedback 等）只看本遍条目；历史保留供 dossier 活口径。
            _GUARD_PREFIXES = ("KB引用", "6章节缺")
            _old_qw = prop_state.get("quality_warning") or ""
            _kept_qw = [
                ln for ln in _old_qw.splitlines()
                if ln.strip() and ln.strip().startswith(_GUARD_PREFIXES)
            ]
            if _kept_qw != [ln for ln in _old_qw.splitlines() if ln.strip()]:
                prop_state["quality_warning"] = "\n".join(_kept_qw)
            if prop_state.get("negative_feedback_alert"):
                prop_state["negative_feedback_alert"] = False
                # v7.3.78: negative_feedback_cleared 规范类型为 list
                # （registration.py 注册口径）；v7.3.3 旧实现写 bool True，
                # 与 cron.clear_negative_feedback 的 history.append 冲突
                # （实测 2026-11-11 attosecond 人工清除 AttributeError）。
                # 遗留 bool 视为无历史条目，归一为 list 后按条目追加。
                _cleared_history = prop_state.get("negative_feedback_cleared")
                if not isinstance(_cleared_history, list):
                    _cleared_history = []
                _cleared_history.append({
                    "cleared_at": now_utc(),
                    "previous_reasons": prop_state.get("negative_feedback_reasons", []),
                    "reason": "v7.3.3 退回自动清除（跨遍状态清理）",
                })
                prop_state["negative_feedback_cleared"] = _cleared_history[-10:]
                prop_state["negative_feedback_cleared_reason"] = (
                    f"v7.3.3 退回自动清除（旧遍原因: "
                    f"{';'.join(prop_state.get('negative_feedback_reasons') or [])[:120]}）"
                )
                prop_state["negative_feedback_reasons"] = []
                prop_state["negative_feedback_at"] = None
            prop_state["monitor_history_pass_start"] = len(
                prop_state.get("monitor_history") or [])
            if _log:
                _log.info(
                    f"[{proposal_id}] v7.3.3 退回清理: 旧遍警告已滤除，"
                    f"负反馈已清，monitor 本遍起点 "
                    f"{prop_state['monitor_history_pass_start']}"
                )

        # v7.2.50（BUG-15）：退回路径显式改写 pipeline_jobs（上方已归档并
        # 清空旧轮次 job），必须声明 update_jobs=True 才会真正落盘；
        # 否则会被默认的「保留磁盘最新 pipeline_jobs」合并逻辑覆盖。
        self._set_proposal_state(proposal_id, prop_state, update_jobs=True)

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
                # v6.10.14: 平台期评审团标志——调度层据此跳过自动轮转
                "panel_review_requested": data.get("panel_review_requested", False),
                # v7.3.52（BUG-46）：冻结标志——调度层据此把课题剔出轮转窗口。
                # 缺此键则 micro_scheduler._sync_queue 的
                # `p.get("scheduler_frozen")` 恒为 None → 冻结集合恒空 →
                # 过滤恒不命中（结构性死路径）。生产实证：berry 的
                # scheduler_frozen=True 从未真正阻断其进入轮转名单。
                "scheduler_frozen": bool(data.get("scheduler_frozen", False)),
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
