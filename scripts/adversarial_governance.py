#!/usr/bin/env python3
"""对抗评审奖惩与监察机制（v6.7.6）。

为 writer-critic 对抗链路引入：
- agent（writer/critic）奖惩分数
- 全局监察员 monitor（独立评分 + meta-review）
- 上下文敏感的禁止清单
- 反串通（anti-collusion）机制
- 负反馈预警

用法：
    from adversarial_governance import AdversarialGovernance
    ag = AdversarialGovernance()
    monitor_result = ag.run_monitor_step(...)
    deltas = ag.apply_monitor_result(proposal_id, round_num, section_key,
                                     score_before, score_after, dim_scores,
                                     monitor_result, proposal_state)
"""

from __future__ import annotations

import json
import math
import re
import statistics
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import load_json, now_utc, save_json
from paths import PROJECT_ROOT

try:
    from logger import get_logger
    _log = get_logger("adversarial_governance")
except Exception:
    _log = None

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

AGENT_SCORES_PATH = PROJECT_ROOT / "memory" / "agent-scores.json"
STANDARDS_PATH = PROJECT_ROOT / "memory" / "nsfc-standards.json"

DEFAULT_INITIAL_SCORE = 100
SCORE_MIN = 0
SCORE_MAX = 150
MONITOR_DELTA_CAP = 15
MONITOR_TIMEOUT = 300

ROLES = ["writer", "critic"]

# 规则层系数
WRITER_PROGRESS_WEIGHT = 20
WRITER_ISSUE_REDUCTION_WEIGHT = 3
CRITIC_PROGRESS_WEIGHT = 15
CRITIC_HIGH_ISSUE_BONUS = 2
CRITIC_REGRESSION_PENALTY = 5

# 校准奖励/惩罚
CALIBRATION_BONUS = 3
CALIBRATION_PENALTY_FACTOR = 40  # 每 0.1 误差扣 4 分

# 串通惩罚
COLLUSION_PENALTY = {"medium": -5, "high": -10}

# 占位符信号（writer）
PLACEHOLDER_PATTERNS = [
    r"待补充",
    r"TODO",
    r"\[引用\]",
    r"\[待填\]",
    r"\(待\)",
    r"请补充",
    r"此处补充",
    r"详见后文",
]

# 僵化模板信号（writer）——仅作为可疑信号，不直接扣分
TEMPLATE_PHRASES = [
    "具有重要的科学意义",
    "具有重要的理论意义",
    "具有重要的应用价值",
    "本项目拟开展",
    "本项目拟研究",
    "旨在解决",
    "综上所述",
]

# 问题严重级别标识（critic 报告）
SEVERITY_MARKERS = ["[critical]", "[high]", "[medium]", "[low]", "critical", "high"]


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp_score(score: float) -> float:
    return max(SCORE_MIN, min(SCORE_MAX, score))


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """从文本中提取第一个 JSON 对象。"""
    # 尝试 ```json ... ``` 代码块
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # 尝试裸 JSON 对象
    for match in re.finditer(r"\{.*\}", text, re.DOTALL):
        try:
            return json.loads(match.group(0))
        except Exception:
            continue
    return None


def _extract_overall_score(text: str) -> float:
    """从文本中提取综合评分。"""
    patterns = [
        r"综合评分[：:]\s*(0\.\d+)",
        r"overall[\s_]*score[：:\s]+(0\.\d+)",
        r"score[：:]\s*(0\.\d+)",
        r"monitor_independent_score[\":\s]+(0\.\d+)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return float(m.group(1))
    return 0.0


def _extract_dim_scores(text: str) -> Dict[str, float]:
    """从文本中提取 4 维度分数。"""
    dims = {}
    patterns = [
        ("innovation", r"创新性[（(]innovation[)）]?\s*[:：]?\s*(0\.\d+)"),
        ("feasibility", r"可行性[（(]feasibility[)）]?\s*[:：]?\s*(0\.\d+)"),
        ("rigor", r"严谨性[（(]rigor[)）]?\s*[:：]?\s*(0\.\d+)"),
        ("completeness", r"完整性[（(]completeness[)）]?\s*[:：]?\s*(0\.\d+)"),
    ]
    for key, pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            dims[key] = float(m.group(1))
    return dims


def _count_high_critical_issues(text: str) -> int:
    """统计 critic 报告中 high/critical 问题数量。"""
    count = 0
    for marker in ["[critical]", "[high]", "critical", "high"]:
        count += len(re.findall(re.escape(marker), text, re.IGNORECASE))
    return count


def _dim_std(dim_scores: Dict[str, float]) -> float:
    values = [v for k, v in dim_scores.items() if k in ("innovation", "feasibility", "rigor", "completeness")]
    if len(values) < 2:
        return 0.0
    try:
        return statistics.stdev(values)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# AdversarialGovernance
# ---------------------------------------------------------------------------


class AdversarialGovernance:
    """对抗评审奖惩与监察引擎。"""

    def __init__(self) -> None:
        self.scores_path = AGENT_SCORES_PATH
        self.standards_path = STANDARDS_PATH
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
            save_json(self.scores_path, default)

    def load_agent_scores(self) -> Dict[str, Any]:
        return load_json(self.scores_path, default={
            role: {
                "score": DEFAULT_INITIAL_SCORE,
                "initial_score": DEFAULT_INITIAL_SCORE,
                "history": [],
                "prohibition_violations": [],
                "updated_at": now_utc(),
            }
            for role in ROLES
        })

    def save_agent_scores(self, scores: Dict[str, Any]) -> None:
        scores["updated_at"] = now_utc()
        save_json(self.scores_path, scores)

    # ------------------------------------------------------------------
    # hermes reviewer 调用
    # ------------------------------------------------------------------

    def _call_reviewer(self, prompt: str, timeout: int = MONITOR_TIMEOUT) -> Dict[str, Any]:
        """调用 reviewer profile 执行 monitor 任务。"""
        from common import hermes_subprocess_env
        import time

        # v6.7.7 修复：cron/无 shell 环境时自动读取 .env 并透传 ZAI_API_KEY
        env = hermes_subprocess_env()
        cmd = ["hermes", "--profile", "reviewer", "-z", prompt]
        t0 = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(PROJECT_ROOT),
                env=env,
            )
            elapsed = round(time.time() - t0, 2)
            if result.returncode == 0:
                output = result.stdout.strip()
                if len(output) > 50000:
                    output = output[:50000] + f"\n... (截断，共{len(output)}字符)"
                return {"success": True, "output": output, "elapsed_s": elapsed}
            return {
                "success": False,
                "output": result.stdout[:2000],
                "error": result.stderr[:500],
                "elapsed_s": elapsed,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": f"超时({timeout}s)", "elapsed_s": timeout}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e), "elapsed_s": round(time.time() - t0, 2)}

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
        violations = []
        lower = draft_text.lower()

        # 占位符
        placeholder_hits = []
        for pat in PLACEHOLDER_PATTERNS:
            if re.search(pat, draft_text, re.IGNORECASE):
                placeholder_hits.append(pat)
        if placeholder_hits:
            violations.append({
                "type": "placeholder",
                "label": "使用占位符/未完成段落",
                "penalty": -4,
                "signals": placeholder_hits[:3],
            })

        # 僵化模板：大量堆砌通用套话（简单启发式）
        template_count = sum(1 for phrase in TEMPLATE_PHRASES if phrase in draft_text)
        if template_count >= 5:
            violations.append({
                "type": "template_rigidity",
                "label": "疑似僵化模板/套话堆砌",
                "penalty": -6,
                "signals": [f"命中 {template_count} 个模板短语"],
            })

        # 未大幅改动：与上一版相似度过高（仅当有上一版时）
        if prev_draft_text and len(prev_draft_text) > 100:
            similarity = self._text_similarity(prev_draft_text, draft_text)
            if similarity > 0.92:
                violations.append({
                    "type": "surface_change",
                    "label": "修改过于表面，与上一版相似度过高",
                    "penalty": -5,
                    "signals": [f"相似度 {similarity:.0%}"],
                })

        return violations

    def detect_critic_prohibitions(
        self,
        critic_text: str,
        dim_scores: Dict[str, float],
        proposal_score: float,
    ) -> List[Dict[str, Any]]:
        """检测 critic 违规信号（规则层）。"""
        violations = []

        # 报告过短 / 无实质问题
        if len(critic_text) < 600 and proposal_score < 0.70:
            violations.append({
                "type": "lazy_review",
                "label": "评审报告过短，疑似消极评审",
                "penalty": -10,
                "signals": [f"报告长度 {len(critic_text)}"],
            })

        # 四维度分数雷同
        std = _dim_std(dim_scores)
        if std < 0.03 and dim_scores:
            violations.append({
                "type": "rigid_scoring",
                "label": "四维度分数过于雷同，疑似僵化评分",
                "penalty": -8,
                "signals": [f"标准差 {std:.3f}"],
            })

        # 评分与内容矛盾：整体评分高但 high 问题很多
        high_count = _count_high_critical_issues(critic_text)
        if proposal_score > 0.75 and high_count >= 3:
            violations.append({
                "type": "score_content_mismatch",
                "label": "评分偏高但报告中有较多 high 问题，疑似评分与内容矛盾",
                "penalty": -8,
                "signals": [f"score={proposal_score:.2f}, high={high_count}"],
            })

        return violations

    def _text_similarity(self, a: str, b: str) -> float:
        """简单字符级相似度（用于检测 surface change）。"""
        if not a or not b:
            return 0.0
        # 去空白后比较最长公共子串比例太复杂，用 token set 近似
        tokens_a = set(re.findall(r"\w+", a))
        tokens_b = set(re.findall(r"\w+", b))
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return intersection / union if union else 0.0

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
        prev_hint = f"\n【writer 修改前申请书】{prev_draft_path}" if prev_draft_path else ""
        dim_str = "、".join(f"{k}={v:.2f}" for k, v in dim_scores.items())
        standards_rel = str(self.standards_path.relative_to(PROJECT_ROOT))
        return (
            f"你是全局监察员（monitor），请对本轮 writer-critic 对抗进行独立、公正的 meta-review。\n\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_rel} 中 project_types.{project_type}\n"
            f"【本轮聚焦章节】{section_name}（{section_key}）\n"
            f"【critic 评审报告】{critic_report_path}\n"
            f"【writer 修改后申请书】{current_draft_path}"
            f"{prev_hint}\n\n"
            f"已知 critic 给出的本轮评分：综合 {score_after:.2f}，维度：{dim_str}\n"
            f"writer 修改前综合评分：{score_before:.2f}\n\n"
            f"请执行：\n"
            f"1. 独立阅读当前申请书，按 NSFC 标准给出本轮聚焦章节的综合评分（0-1）和 4 维度分数。\n"
            f"2. 判断 writer 修改是否实质性回应了 critic 的问题，是否存在表面修改、杜撰、错误引用、僵化模板、占位符等。\n"
            f"3. 判断 critic 评审是否准确、是否有遗漏重大问题、评分是否与报告内容一致。\n"
            f"4. 评估是否存在 writer-critic 串通（双方放水、分数虚高但质量未提升）。\n\n"
            f"输出必须是 JSON：\n"
            f"{{\n"
            f'  "monitor_independent_score": 0.72,\n'
            f'  "monitor_dim_scores": {{"innovation":0.8,"feasibility":0.7,"rigor":0.7,"completeness":0.7}},\n'
            f'  "writer_assessment": "...",\n'
            f'  "critic_assessment": "...",\n'
            f'  "writer_prohibitions": [],\n'
            f'  "critic_prohibitions": [],\n'
            f'  "writer_suggested_delta": 5,\n'
            f'  "critic_suggested_delta": 3,\n'
            f'  "collusion_risk": "none",\n'
            f'  "negative_feedback": false,\n'
            f'  "overall_assessment": "..."\n'
            f"}}\n\n"
            f"注意：\n"
            f"- 禁止清单的判定要结合当前申请书质量上下文，接近达标时无 severe 问题是合理的。\n"
            f"- 若申请书质量确实已高，writer 只做必要微调也是合理的，不要判为表面修改。\n"
            f"- 评分必须真实反映申请书质量，不要刻意迎合 critic 或 writer。\n"
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
        critic_report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
        current_draft_path = prop_dir / "04_proposal" / "proposal-draft.md"

        prompt = self.build_monitor_prompt(
            proposal_id, project_type, round_num, section_key, section_name,
            critic_report_path, current_draft_path, prev_draft_path,
            score_before, score_after, dim_scores,
        )

        result = self._call_reviewer(prompt)
        output = result.get("output", "")

        parsed = _extract_json_object(output) or {}

        # 独立评分：优先取 JSON，否则从文本解析
        monitor_score = _safe_float(parsed.get("monitor_independent_score"), 0.0)
        if monitor_score == 0.0:
            monitor_score = _extract_overall_score(output)
        monitor_dim_scores = parsed.get("monitor_dim_scores") or _extract_dim_scores(output)
        if not monitor_dim_scores:
            monitor_dim_scores = dim_scores

        # 禁止清单：优先取 monitor 输出，否则规则兜底
        writer_prohibitions = parsed.get("writer_prohibitions") or []
        critic_prohibitions = parsed.get("critic_prohibitions") or []

        current_draft_text = ""
        prev_draft_text = ""
        critic_text = ""
        try:
            if current_draft_path.exists():
                current_draft_text = current_draft_path.read_text(encoding="utf-8")
            if prev_draft_path and prev_draft_path.exists():
                prev_draft_text = prev_draft_path.read_text(encoding="utf-8")
            if critic_report_path.exists():
                critic_text = critic_report_path.read_text(encoding="utf-8")
        except Exception:
            pass

        if not writer_prohibitions:
            writer_prohibitions = [v["type"] for v in self.detect_writer_prohibitions(
                current_draft_text, prev_draft_text, critic_text
            )]
        if not critic_prohibitions:
            critic_prohibitions = [v["type"] for v in self.detect_critic_prohibitions(
                critic_text, dim_scores, score_after
            )]

        # 串通风险
        collusion_risk = parsed.get("collusion_risk", "none")
        if collusion_risk not in ("none", "low", "medium", "high"):
            collusion_risk = "none"

        # 负反馈（仅 monitor 建议，最终由 check_negative_feedback 综合判定）
        negative_feedback = bool(parsed.get("negative_feedback", False))

        return {
            "success": result.get("success", False),
            "error": result.get("error", ""),
            "monitor_independent_score": monitor_score,
            "monitor_dim_scores": monitor_dim_scores,
            "writer_assessment": parsed.get("writer_assessment", ""),
            "critic_assessment": parsed.get("critic_assessment", ""),
            "writer_prohibitions": writer_prohibitions,
            "critic_prohibitions": critic_prohibitions,
            "writer_suggested_delta": _safe_float(parsed.get("writer_suggested_delta"), 0.0),
            "critic_suggested_delta": _safe_float(parsed.get("critic_suggested_delta"), 0.0),
            "collusion_risk": collusion_risk,
            "negative_feedback": negative_feedback,
            "overall_assessment": parsed.get("overall_assessment", ""),
            "raw_output": output[:2000],
        }

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
        monitor_delta = monitor_score - prev_monitor_score

        # Writer
        writer_delta = monitor_delta * WRITER_PROGRESS_WEIGHT
        writer_delta += max(0, high_issues_before - high_issues_after) * WRITER_ISSUE_REDUCTION_WEIGHT
        writer_delta += self._penalty_for_violations(writer_violations, "writer")

        # Critic
        critic_delta = 0.0
        if monitor_delta > 0.05:
            critic_delta += monitor_delta * CRITIC_PROGRESS_WEIGHT
            critic_delta += min(high_issues_after, 5) * CRITIC_HIGH_ISSUE_BONUS
        elif monitor_delta < -0.05:
            critic_delta -= CRITIC_REGRESSION_PENALTY
        critic_delta += self._penalty_for_violations(critic_violations, "critic")

        # Critic 校准奖励/惩罚
        calibration_error = abs(critic_score - monitor_score)
        if calibration_error < 0.10:
            critic_delta += CALIBRATION_BONUS
        elif calibration_error > 0.20:
            critic_delta -= min(8.0, (calibration_error - 0.20) * CALIBRATION_PENALTY_FACTOR)

        return writer_delta, critic_delta

    def _penalty_for_violations(self, violations: List[str], role: str) -> float:
        """根据违规类型返回总扣分。"""
        # 与禁止清单表对应
        penalty_map = {
            "writer": {
                "fabrication": -12,
                "wrong_citation": -8,
                "template_rigidity": -6,
                "unaddressed_issues": -8,
                "off_section_changes": -5,
                "placeholder": -4,
                "surface_change": -5,
            },
            "critic": {
                "lazy_review": -10,
                "rigid_scoring": -8,
                "missed_major_issues": -10,
                "unactionable_suggestions": -6,
                "score_content_mismatch": -8,
            },
        }
        total = 0.0
        for v in violations:
            key = v if isinstance(v, str) else v.get("type", "")
            total += penalty_map.get(role, {}).get(key, 0)
        return total

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
        monitor_score = monitor_result.get("monitor_independent_score", score_after)

        # 上一轮的 monitor 分数作为 baseline
        prev_monitor_score = score_before
        monitor_history = proposal_state.get("monitor_history", [])
        for entry in reversed(monitor_history):
            if entry.get("monitor_independent_score") is not None:
                prev_monitor_score = entry["monitor_independent_score"]
                break

        # high issues 数量
        high_issues_before = 0
        if monitor_history:
            high_issues_before = monitor_history[-1].get("high_issues_after", 0)
        high_issues_after = _count_high_critical_issues(
            monitor_result.get("raw_output", "")
        )

        writer_violations = monitor_result.get("writer_prohibitions", [])
        critic_violations = monitor_result.get("critic_prohibitions", [])

        writer_rule_delta, critic_rule_delta = self.compute_rule_deltas(
            monitor_score, prev_monitor_score, score_after,
            writer_violations, critic_violations,
            high_issues_before, high_issues_after,
        )

        # 与 monitor 建议混合（±15 限制）
        writer_suggested = float(monitor_result.get("writer_suggested_delta", 0.0))
        critic_suggested = float(monitor_result.get("critic_suggested_delta", 0.0))
        writer_monitor_delta = max(-MONITOR_DELTA_CAP, min(MONITOR_DELTA_CAP, writer_suggested))
        critic_monitor_delta = max(-MONITOR_DELTA_CAP, min(MONITOR_DELTA_CAP, critic_suggested))

        # 若 monitor 提供了非零建议，与规则层取平均；否则纯规则层
        if abs(writer_monitor_delta) > 0.001:
            writer_delta = (writer_rule_delta + writer_monitor_delta) / 2.0
        else:
            writer_delta = writer_rule_delta

        if abs(critic_monitor_delta) > 0.001:
            critic_delta = (critic_rule_delta + critic_monitor_delta) / 2.0
        else:
            critic_delta = critic_rule_delta

        # 串通惩罚
        collusion_risk = monitor_result.get("collusion_risk", "none")
        collusion_penalty = COLLUSION_PENALTY.get(collusion_risk, 0)
        if collusion_risk in ("medium", "high"):
            # 若当前奖励为正，先清零再额外扣分
            writer_delta = min(writer_delta, 0) + collusion_penalty
            critic_delta = min(critic_delta, 0) + collusion_penalty

        # 加载并更新 agent 分数
        scores = self.load_agent_scores()
        old_writer = scores["writer"]["score"]
        old_critic = scores["critic"]["score"]
        new_writer = _clamp_score(old_writer + writer_delta)
        new_critic = _clamp_score(old_critic + critic_delta)

        scores["writer"]["score"] = new_writer
        scores["writer"]["history"].append({
            "round_ref": f"{proposal_id}-r{round_num}-{section_key}",
            "delta": round(writer_delta, 2),
            "reason": monitor_result.get("writer_assessment", "")[:100],
            "at": now_utc(),
        })
        scores["writer"]["history"] = scores["writer"]["history"][-50:]

        scores["critic"]["score"] = new_critic
        scores["critic"]["history"].append({
            "round_ref": f"{proposal_id}-r{round_num}-{section_key}",
            "delta": round(critic_delta, 2),
            "reason": monitor_result.get("critic_assessment", "")[:100],
            "at": now_utc(),
        })
        scores["critic"]["history"] = scores["critic"]["history"][-50:]

        # 记录违规
        for v in writer_violations:
            vtype = v if isinstance(v, str) else v.get("type", "")
            penalty = self._penalty_for_violations([vtype], "writer")
            scores["writer"]["prohibition_violations"].append({
                "type": vtype,
                "round_ref": f"{proposal_id}-r{round_num}-{section_key}",
                "penalty": penalty,
                "at": now_utc(),
            })
        scores["writer"]["prohibition_violations"] = scores["writer"]["prohibition_violations"][-20:]

        for v in critic_violations:
            vtype = v if isinstance(v, str) else v.get("type", "")
            penalty = self._penalty_for_violations([vtype], "critic")
            scores["critic"]["prohibition_violations"].append({
                "type": vtype,
                "round_ref": f"{proposal_id}-r{round_num}-{section_key}",
                "penalty": penalty,
                "at": now_utc(),
            })
        scores["critic"]["prohibition_violations"] = scores["critic"]["prohibition_violations"][-20:]

        self.save_agent_scores(scores)

        return {
            "writer_delta": round(writer_delta, 2),
            "critic_delta": round(critic_delta, 2),
            "old_writer_score": round(old_writer, 2),
            "old_critic_score": round(old_critic, 2),
            "new_writer_score": round(new_writer, 2),
            "new_critic_score": round(new_critic, 2),
            "monitor_independent_score": monitor_score,
            "prev_monitor_score": prev_monitor_score,
            "collusion_risk": collusion_risk,
            "negative_feedback": monitor_result.get("negative_feedback", False),
            "high_issues_after": high_issues_after,
        }

    # ------------------------------------------------------------------
    # 负反馈检测
    # ------------------------------------------------------------------

    def check_negative_feedback(
        self,
        proposal_state: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """判断是否需要触发负反馈告警。"""
        reasons: List[str] = []
        monitor_history = proposal_state.get("monitor_history", [])
        if not monitor_history:
            return False, reasons

        # 1. monitor 独立分数连续 3 轮下降
        recent_scores = [entry.get("monitor_independent_score", 0.0) for entry in monitor_history[-3:]]
        if len(recent_scores) >= 3 and all(
            recent_scores[i] > recent_scores[i + 1] for i in range(len(recent_scores) - 1)
        ):
            reasons.append(f"monitor 独立分数连续 {len(recent_scores)} 轮下降")

        # 2. 本地 writer/critic 分数连续 3 轮双降
        recent_local_writer = [entry.get("local_writer_score", 100.0) for entry in monitor_history[-3:]]
        recent_local_critic = [entry.get("local_critic_score", 100.0) for entry in monitor_history[-3:]]
        if (len(recent_local_writer) >= 3 and
            all(recent_local_writer[i] > recent_local_writer[i + 1] for i in range(2)) and
            all(recent_local_critic[i] > recent_local_critic[i + 1] for i in range(2))):
            reasons.append("writer/critic 本地分数连续 3 轮双降")

        # 3. 串通风险连续 2 轮 >= medium
        recent_collusion = [entry.get("collusion_risk", "none") for entry in monitor_history[-2:]]
        if len(recent_collusion) >= 2 and all(r in ("medium", "high") for r in recent_collusion):
            reasons.append("串通风险连续 2 轮达到 medium/high")

        # 4. 全局 agent 分数 < 50
        scores = self.load_agent_scores()
        if scores.get("writer", {}).get("score", 100) < 50:
            reasons.append("writer 全局分数低于 50")
        if scores.get("critic", {}).get("score", 100) < 50:
            reasons.append("critic 全局分数低于 50")

        return bool(reasons), reasons

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
        monitor_history = proposal_state.setdefault("monitor_history", [])

        # 计算本地 agent 累计分数
        local_writer_score = DEFAULT_INITIAL_SCORE
        local_critic_score = DEFAULT_INITIAL_SCORE
        if monitor_history:
            local_writer_score = monitor_history[-1].get("local_writer_score", DEFAULT_INITIAL_SCORE)
            local_critic_score = monitor_history[-1].get("local_critic_score", DEFAULT_INITIAL_SCORE)

        local_writer_score = _clamp_score(local_writer_score + deltas["writer_delta"])
        local_critic_score = _clamp_score(local_critic_score + deltas["critic_delta"])

        entry = {
            "round": round_num,
            "section_key": section_key,
            "proposal_score_before": score_before,
            "proposal_score_after": score_after,
            "monitor_independent_score": deltas.get("monitor_independent_score", monitor_result.get("monitor_independent_score", score_after)),
            "writer_delta": deltas["writer_delta"],
            "critic_delta": deltas["critic_delta"],
            "local_writer_score": local_writer_score,
            "local_critic_score": local_critic_score,
            "writer_prohibitions": monitor_result.get("writer_prohibitions", []),
            "critic_prohibitions": monitor_result.get("critic_prohibitions", []),
            "collusion_risk": monitor_result.get("collusion_risk", "none"),
            "negative_feedback": monitor_result.get("negative_feedback", False),
            "overall_assessment": monitor_result.get("overall_assessment", "")[:500],
            "high_issues_after": deltas.get("high_issues_after", 0),
            "at": now_utc(),
        }
        monitor_history.append(entry)
        proposal_state["monitor_history"] = monitor_history[-50:]

        # 负反馈综合判定
        alert, reasons = self.check_negative_feedback(proposal_state)
        proposal_state["negative_feedback_alert"] = alert
        if alert:
            proposal_state["negative_feedback_reasons"] = reasons

        return proposal_state


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
