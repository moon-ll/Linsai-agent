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
            return {"done": True, "reason": f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利（{','.join(passed_sections)}）"}

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
