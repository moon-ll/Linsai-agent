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

    # v6.7.10: 7 个申请书模块 + 整体审查全部通过才算达标
    REQUIRED_SECTIONS = SECTION_KEYS + ["full_review"]

    def _check_done(self, proposal_id: str, threshold: Dict[str, Any]) -> Dict[str, Any]:
        """判定 proposal 是否达到输出标准（P1-3: 所有模块对抗胜利才算达标）。

        达标条件：7 个章节（立项依据/研究内容/研究方案/特色与创新/年度研究计划/预期研究成果/参考文献）
        + 整体审查，共 8 个模块全部通过。每个模块"通过"= 分数达标 + 各维度无短板。
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"done": False, "reason": "状态不存在"}

        last_score = prop_state.get("last_score", 0.0)
        score_history = prop_state.get("score_history", [])
        section_passes = prop_state.get("section_passes", {})  # P1-3
        min_score = threshold.get("min_overall_score", DEFAULT_SCORE_THRESHOLD)
        rounds = prop_state.get("optimization_rounds", 0)

        # 条件1（P1-3）：所有模块对抗胜利
        passed_sections = [s for s in self.REQUIRED_SECTIONS if section_passes.get(s)]
        all_passed = len(passed_sections) == len(self.REQUIRED_SECTIONS)
        if all_passed:
            return {"done": True, "reason": f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利（{','.join(passed_sections)}）"}

        # 条件2：连续N轮无提升（逃生阀）
        no_improve_limit = DEFAULT_NO_IMPROVEMENT_LIMIT
        if len(score_history) >= no_improve_limit + 1:
            recent_scores = [h["score"] for h in score_history[-(no_improve_limit + 1):]]
            deltas = [recent_scores[i + 1] - recent_scores[i] for i in range(len(recent_scores) - 1)]
            if all(d < 0.02 for d in deltas):
                passed_str = f"（已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块）"
                return {"done": True, "reason": f"连续{no_improve_limit}轮无显著提升{passed_str}"}

        # 条件3：达到最大轮数（逃生阀）
        if rounds >= DEFAULT_MAX_ROUNDS:
            passed_str = f"（已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块）"
            return {"done": True, "reason": f"达到最大轮数{DEFAULT_MAX_ROUNDS}{passed_str}"}

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
