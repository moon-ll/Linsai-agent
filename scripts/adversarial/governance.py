#!/usr/bin/env python3
"""对抗评审奖惩与监察机制 — AdversarialGovernance 组合类。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import now_utc

from . import monitor, prohibitions, scoring, utils
from .constants import DEFAULT_INITIAL_SCORE, MONITOR_TIMEOUT, ROLES

try:
    from logger import get_logger
    _log = get_logger("adversarial_governance")
except Exception:
    _log = None


class AdversarialGovernance:
    """对抗评审奖惩与监察引擎。"""

    def __init__(self) -> None:
        import adversarial_governance

        self.scores_path = adversarial_governance.AGENT_SCORES_PATH
        self.standards_path = adversarial_governance.STANDARDS_PATH
        self._ensure_scores_file()

    # ------------------------------------------------------------------
    # agent 分数持久化
    # ------------------------------------------------------------------

    def _ensure_scores_file(self) -> None:
        if not self.scores_path.exists():
            default = {
                role: {
                    "score": DEFAULT_INITIAL_SCORE,
                    "initial_score": DEFAULT_INITIAL_SCORE,
                    "history": [],
                    "prohibition_violations": [],
                    "updated_at": now_utc(),
                }
                for role in ROLES
            }
            scoring.save_agent_scores(self.scores_path, default)

    def load_agent_scores(self) -> Dict[str, Any]:
        return scoring.load_agent_scores(self.scores_path)

    def save_agent_scores(self, scores: Dict[str, Any]) -> None:
        scoring.save_agent_scores(self.scores_path, scores)

    # ------------------------------------------------------------------
    # hermes reviewer 调用
    # ------------------------------------------------------------------

    def _call_reviewer(self, prompt: str, timeout: int = MONITOR_TIMEOUT) -> Dict[str, Any]:
        """调用 reviewer profile 执行 monitor 任务。"""
        return monitor._call_reviewer(prompt, timeout=timeout)

    # ------------------------------------------------------------------
    # 禁止清单（规则层）
    # ------------------------------------------------------------------

    def detect_writer_prohibitions(
        self,
        draft_text: str,
        prev_draft_text: str,
        critic_text: str,
        focus_section: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """检测 writer 违规信号（规则层）。"""
        return prohibitions.detect_writer_prohibitions(
            draft_text, prev_draft_text, critic_text, focus_section=focus_section
        )

    def detect_critic_prohibitions(
        self,
        critic_text: str,
        dim_scores: Dict[str, float],
        proposal_score: float,
    ) -> List[Dict[str, Any]]:
        """检测 critic 违规信号（规则层）。"""
        return prohibitions.detect_critic_prohibitions(critic_text, dim_scores, proposal_score)

    def _text_similarity(self, a: str, b: str) -> float:
        """简单字符级相似度（用于检测 surface change）。"""
        return utils._text_similarity(a, b)

    # ------------------------------------------------------------------
    # Monitor 步骤
    # ------------------------------------------------------------------

    def build_monitor_prompt(
        self,
        proposal_id: str,
        project_type: str,
        round_num: int,
        section_key: str,
        section_name: str,
        critic_report_path: Path,
        current_draft_path: Path,
        prev_draft_path: Optional[Path],
        score_before: float,
        score_after: float,
        dim_scores: Dict[str, float],
    ) -> str:
        """构造 monitor prompt。"""
        return monitor.build_monitor_prompt(
            proposal_id, project_type, round_num, section_key, section_name,
            critic_report_path, current_draft_path, prev_draft_path,
            score_before, score_after, dim_scores,
            standards_path=self.standards_path,
        )

    def run_monitor_step(
        self,
        proposal_id: str,
        prop_dir: Path,
        project_type: str,
        round_num: int,
        section_key: str,
        section_name: str,
        score_before: float,
        score_after: float,
        dim_scores: Dict[str, float],
        prev_draft_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """执行一轮 monitor，返回结构化结果。"""
        return monitor.run_monitor_step(
            proposal_id=proposal_id,
            prop_dir=prop_dir,
            project_type=project_type,
            round_num=round_num,
            section_key=section_key,
            section_name=section_name,
            score_before=score_before,
            score_after=score_after,
            dim_scores=dim_scores,
            prev_draft_path=prev_draft_path,
            standards_path=self.standards_path,
        )

    # ------------------------------------------------------------------
    # 分数计算
    # ------------------------------------------------------------------

    def compute_rule_deltas(
        self,
        monitor_score: float,
        prev_monitor_score: float,
        critic_score: float,
        writer_violations: List[str],
        critic_violations: List[str],
        high_issues_before: int,
        high_issues_after: int,
    ) -> Tuple[float, float]:
        """规则层计算 writer/critic 本轮 delta。"""
        return scoring.compute_rule_deltas(
            monitor_score, prev_monitor_score, critic_score,
            writer_violations, critic_violations,
            high_issues_before, high_issues_after,
        )

    def _penalty_for_violations(self, violations: List[str], role: str) -> float:
        """根据违规类型返回总扣分。"""
        return scoring._penalty_for_violations(violations, role)

    def apply_monitor_result(
        self,
        proposal_id: str,
        round_num: int,
        section_key: str,
        score_before: float,
        score_after: float,
        dim_scores: Dict[str, float],
        monitor_result: Dict[str, Any],
        proposal_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """根据 monitor 结果更新 agent 分数、monitor_history，返回 deltas。"""
        return scoring.apply_monitor_result(
            self.scores_path,
            proposal_id=proposal_id,
            round_num=round_num,
            section_key=section_key,
            score_before=score_before,
            score_after=score_after,
            dim_scores=dim_scores,
            monitor_result=monitor_result,
            proposal_state=proposal_state,
        )

    # ------------------------------------------------------------------
    # 负反馈检测
    # ------------------------------------------------------------------

    def check_negative_feedback(
        self,
        proposal_state: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """判断是否需要触发负反馈告警。"""
        return scoring.check_negative_feedback(proposal_state, agent_scores=self.load_agent_scores())

    def record_monitor_history(
        self,
        proposal_state: Dict[str, Any],
        round_num: int,
        section_key: str,
        score_before: float,
        score_after: float,
        monitor_result: Dict[str, Any],
        deltas: Dict[str, Any],
    ) -> Dict[str, Any]:
        """把 monitor 记录写入 proposal_state，返回更新后的 state。"""
        return scoring.record_monitor_history(
            proposal_state,
            round_num=round_num,
            section_key=section_key,
            score_before=score_before,
            score_after=score_after,
            monitor_result=monitor_result,
            deltas=deltas,
            agent_scores=self.load_agent_scores(),
        )


# ---------------------------------------------------------------------------
# 模块自检
# ---------------------------------------------------------------------------


def _self_check() -> Dict[str, Any]:
    """模块自检：验证规则层、分数计算、负反馈检测可正常运行。"""
    ag = AdversarialGovernance()
    scores = ag.load_agent_scores()
    checks = {
        "scores_initialized": scores.get("writer", {}).get("score") == 100,
        "placeholder_detected": bool(ag.detect_writer_prohibitions("[待填]", "", "")),
        "lazy_critic_detected": bool(ag.detect_critic_prohibitions("还可以", {}, 0.5)),
        "negative_feedback_detected": False,
    }

    prop_state = {"monitor_history": [
        {"monitor_independent_score": 0.70, "local_writer_score": 95, "local_critic_score": 95, "collusion_risk": "none"},
        {"monitor_independent_score": 0.65, "local_writer_score": 90, "local_critic_score": 90, "collusion_risk": "none"},
        {"monitor_independent_score": 0.60, "local_writer_score": 85, "local_critic_score": 85, "collusion_risk": "none"},
    ]}
    alert, _ = ag.check_negative_feedback(prop_state)
    checks["negative_feedback_detected"] = alert

    all_ok = all(checks.values())
    return {"success": all_ok, "checks": checks}
