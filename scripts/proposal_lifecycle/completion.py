from __future__ import annotations

from typing import Any, Dict

from proposal_lifecycle.constants import (
    _log,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_NO_IMPROVEMENT_LIMIT,
    DEFAULT_SCORE_THRESHOLD,
)

from proposal_sections import SECTION_KEYS


class CompletionMixin:
    # ------------------------------------------------------------------
    # 达标判定
    # ------------------------------------------------------------------

    # v6.8.0: 5 个申请书模块（含整体审查）全部通过才算达标
    REQUIRED_SECTIONS = SECTION_KEYS

    def _check_done(self, proposal_id: str, threshold: Dict[str, Any]) -> Dict[str, Any]:
        """判定 proposal 是否达到输出标准（P1-3: 所有模块对抗胜利才算达标）。

        达标条件：
        1. 条件1（达标）：5 个章节全部通过（分数达标 + 各维度无短板）
        2. 条件2（逃生阀）：连续N轮无显著提升
        3. 条件3（逃生阀）：达到最大轮数

        逃生阀触发时，如果分数低于达标线，附加 quality_warning 标记。
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"done": False, "reason": "状态不存在"}

        last_score = prop_state.get("last_score", 0.0)
        score_history = prop_state.get("score_history", [])
        section_passes = prop_state.get("section_passes", {})  # P1-3
        min_score = threshold.get("min_overall_score", DEFAULT_SCORE_THRESHOLD)
        rounds = prop_state.get("optimization_rounds", 0)

        # v6.8.3: 获取 monitor 独立评分作为校准参考
        monitor_history = prop_state.get("monitor_history", [])
        monitor_score = 0.0
        if monitor_history:
            last_monitor = monitor_history[-1]
            monitor_score = last_monitor.get("monitor_independent_score", 0.0)

        # 条件1（P1-3）：所有模块对抗胜利 + monitor 复核通过
        passed_sections = [s for s in self.REQUIRED_SECTIONS if section_passes.get(s)]
        all_passed = len(passed_sections) == len(self.REQUIRED_SECTIONS)
        if all_passed:
            # v6.8.9: monitor 作为第三方监管者把关——即使 writer-critic 对抗全部胜利，
            # 若 monitor 独立评分低于达标线，视为未达标，继续优化。
            # 防止 writer+critic 串通虚高通过（"摆烂"），监管者真正起到把关作用。
            if monitor_history and monitor_score > 0 and monitor_score < min_score:
                return {
                    "done": False,
                    "reason": (
                        f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利，"
                        f"但 monitor 独立评分{monitor_score:.2f}低于达标线{min_score:.2f}，"
                        f"不予流转，继续优化。"
                    ),
                }
            # v6.8.22: 断裂点5——P0 清零检查。即使 5 模块全胜，若存在未解决 critical P0，
            # 不予标达标流转，防止"带着致命问题出厂"。
            try:
                open_critical = prop_state.get("open_critical_issues", [])
                unresolved_criticals = [
                    e for e in (open_critical or [])
                    if isinstance(e, dict)
                    and e.get("round_resolved") is None
                    and not e.get("stale")
                    and (e.get("severity") or "").lower() == "critical"
                ]
                if unresolved_criticals:
                    sampled = ", ".join(
                        f"{e.get('section','?')}" for e in unresolved_criticals[:5]
                    )
                    return {
                        "done": False,
                        "reason": (
                            f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利，"
                            f"但仍有{len(unresolved_criticals)}条未解决 critical P0 "
                            f"（涉及：{sampled}{'...' if len(unresolved_criticals) > 5 else ''}），"
                            f"不予流转，继续优化。"
                        ),
                    }
            except Exception:
                pass  # 非关键路径，读取失败不阻断原有达标逻辑
            return {"done": True, "reason": f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利（{','.join(passed_sections)}）"}

        # v6.8.16 改进1: 质量天花板检测（收敛检测）
        # 连续 3 轮分数 ≥0.85 且每轮提升 <2% → 自动晋级到 pending_review
        # v6.9.27: 收敛线随达标线整体上调（面上 0.85），防止低分课题绕过新标准
        # v6.9.57 结构性注记：本收敛线与程序化天花板体系冲突——AI 写作检测
        #   ceiling<0.9 档把综合分 cap 在 0.85，锚点"差距明显"档 cap 在 0.84，
        #   导致锚点达标前综合分无法连续 4 轮 ≥0.85（全量 32 轮实测 max 0.81，
        #   本分支零触发，健康检查多轮定性为死代码）。在锚点对比"达标"成为
        #   常态前，晋级的实际主路径是全模块对抗胜利 + 人工验收（dossier）。
        #   配套的次优平台检测见下方 SUBOPTIMAL_FLOOR。
        CONVERGENCE_SCORE = 0.85
        CONVERGENCE_ROUNDS = 3
        CONVERGENCE_DELTA = 0.02
        if len(score_history) >= CONVERGENCE_ROUNDS + 1:
            recent = score_history[-(CONVERGENCE_ROUNDS + 1):]
            recent_scores = [h["score"] for h in recent]
            # v6.9.16 修复：窗口内全部轮次（含当前轮）都须 ≥0.80。
            # 原实现只约束前 3 轮（recent_scores[:-1]），"3 轮高位平台后
            # 当前轮骤降"（含伪分数污染，如实测 0.85→0.18）会被误判为
            # 质量收敛而自动晋级 pending_review，掩盖质量回退。
            if all(s >= CONVERGENCE_SCORE for s in recent_scores):
                # 且每轮提升 <2%
                deltas = [recent_scores[i + 1] - recent_scores[i] for i in range(len(recent_scores) - 1)]
                if all(d < CONVERGENCE_DELTA for d in deltas):
                    return {
                        "done": True,
                        "reason": (
                            f"质量收敛：连续{CONVERGENCE_ROUNDS}轮分数≥{CONVERGENCE_SCORE:.2f}"
                            f"且每轮提升<{CONVERGENCE_DELTA:.0%}，"
                            f"当前{last_score:.2f}，建议人工审核确认"
                        ),
                        "quality_warning": None,
                    }

        # v6.9.57: 次优平台检测——收敛线 0.85 在锚点达标前结构性不可达
        # （见上方注记），本检测把"贴近天花板的平台化"转为有效人工信号：
        # 0.80-0.85 区间连续平台 → 不自动晋级，仅置 quality_warning，
        # 由人工评估是否提前晋级验收（人工验收为主定位）。
        SUBOPTIMAL_FLOOR = 0.80
        if len(score_history) >= CONVERGENCE_ROUNDS + 1:
            _recent = [h["score"] for h in score_history[-(CONVERGENCE_ROUNDS + 1):]]
            if all(SUBOPTIMAL_FLOOR <= s < CONVERGENCE_SCORE for s in _recent):
                _deltas = [_recent[i + 1] - _recent[i] for i in range(len(_recent) - 1)]
                if all(abs(d) < CONVERGENCE_DELTA for d in _deltas):
                    try:
                        prop_state["quality_warning"] = (
                            f"○ 次优平台：连续{CONVERGENCE_ROUNDS}轮分数在"
                            f"{SUBOPTIMAL_FLOOR:.2f}-{CONVERGENCE_SCORE:.2f} 平台"
                            f"（当前{last_score:.2f}），贴近程序化天花板（AI检测/锚点绑定），"
                            f"自动提升空间有限，建议人工评估是否晋级验收"
                        )
                        # v6.9.59 修复：_get_proposal_state 每次从磁盘新读
                        # （无缓存），not-done 返回路径若不显式落盘，警告只
                        # 改了内存副本即丢失——单测 mock 返回同一 dict 引用
                        # 曾掩盖此问题，生产端 review_dossier 永远读不到信号。
                        self._set_proposal_state(proposal_id, prop_state)
                    except Exception:
                        pass  # 状态写入失败不阻断达标判定

        # v6.8.16 改进1: 质量下降检测
        # 连续 3 轮分数下降 → 标记 quality_declining，附加质量警告
        DECLINE_ROUNDS = 3
        if len(score_history) >= DECLINE_ROUNDS + 1:
            recent_scores = [h["score"] for h in score_history[-(DECLINE_ROUNDS + 1):]]
            deltas = [recent_scores[i + 1] - recent_scores[i] for i in range(len(recent_scores) - 1)]
            if all(d < 0 for d in deltas[-DECLINE_ROUNDS:]):
                quality_warning = (
                    f"⚠ 质量下降: 连续{DECLINE_ROUNDS}轮分数下降"
                    f"（{recent_scores[-DECLINE_ROUNDS-1]:.2f}→{recent_scores[-1]:.2f}）。"
                    f"建议人工干预检查优化方向。"
                )
                return {
                    "done": True,
                    "reason": f"连续{DECLINE_ROUNDS}轮质量下降，暂停自动优化",
                    "quality_warning": quality_warning,
                }

        # 条件2：连续N轮无提升（逃生阀）
        no_improve_limit = DEFAULT_NO_IMPROVEMENT_LIMIT
        if len(score_history) >= no_improve_limit + 1:
            recent_scores = [h["score"] for h in score_history[-(no_improve_limit + 1):]]
            deltas = [recent_scores[i + 1] - recent_scores[i] for i in range(len(recent_scores) - 1)]
            if all(d <= 0 for d in deltas):
                passed_str = f"（已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块）"
                # v6.8.3: 逃生阀触发时附加质量警告
                quality_warning = ""
                if last_score < min_score:
                    quality_warning = (
                        f"⚠ 质量警告: 分数{last_score:.2f}低于达标线{min_score:.2f}。"
                        f"已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块。"
                        f"monitor评分{monitor_score:.2f}。建议人工审核。"
                    )
                return {
                    "done": True,
                    "reason": f"连续{no_improve_limit}轮无显著提升{passed_str}",
                    "quality_warning": quality_warning if quality_warning else None,
                }

        # 条件3：达到最大轮数（逃生阀）
        if rounds >= DEFAULT_MAX_ROUNDS:
            passed_str = f"（已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块）"
            quality_warning = ""
            if last_score < min_score:
                quality_warning = (
                    f"⚠ 质量警告: 达到最大轮数{DEFAULT_MAX_ROUNDS}，分数{last_score:.2f}低于达标线{min_score:.2f}。"
                    f"已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块。"
                    f"monitor评分{monitor_score:.2f}。建议人工审核。"
                )
            return {
                "done": True,
                "reason": f"达到最大轮数{DEFAULT_MAX_ROUNDS}{passed_str}",
                "quality_warning": quality_warning if quality_warning else None,
            }

        # 未达标：报告进度
        missing = [s for s in self.REQUIRED_SECTIONS if not section_passes.get(s)]
        return {
            "done": False,
            "reason": f"已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块，待通过: {','.join(missing)}",
        }

    def auto_optimize_and_advance(self, proposal_id: str) -> Dict[str, Any]:
        """自动优化循环：反复执行对抗直到达标或无法提升，然后移入待校验。

        适用于 cron 自动驱动。
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal 未注册"}

        if prop_state["status"] != "optimizing":
            return {"success": False, "error": f"proposal 不在优化中（当前: {prop_state['status']}）"}

        threshold = self._get_quality_threshold(prop_state.get("project_type", "general"))
        rounds_done = 0
        last_result = {}

        while rounds_done < DEFAULT_MAX_ROUNDS:
            result = self.optimize_cycle(proposal_id)
            if not result.get("success"):
                break
            rounds_done += 1
            last_result = result

            if result.get("done"):
                # 达标或无法提升，移入待校验
                transition_result = self.transition(
                    proposal_id, "pending_review", reason=result["reason"]
                )
                return {
                    "success": True,
                    "advanced": True,
                    "rounds": rounds_done,
                    "final_score": result.get("score_after", 0),
                    "reason": result["reason"],
                    "transition": transition_result,
                }

        # 达到最大轮数
        transition_result = self.transition(
            proposal_id, "pending_review",
            reason=f"达到最大轮数{DEFAULT_MAX_ROUNDS}，当前分数{last_result.get('score_after', 0):.2f}"
        )
        return {
            "success": True,
            "advanced": True,
            "rounds": rounds_done,
            "final_score": last_result.get("score_after", 0),
            "reason": "达到最大轮数",
            "transition": transition_result,
        }
