#!/usr/bin/env python3
"""对抗评审奖惩与监察机制 — Monitor 步骤（prompt / reviewer 调用 / 结果解析）。"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

from common import hermes_subprocess_env

from .constants import MONITOR_TIMEOUT
from .prohibitions import detect_critic_prohibitions, detect_writer_prohibitions
from .utils import (
    _extract_dim_scores,
    _extract_json_object,
    _extract_overall_score,
    _safe_float,
)

try:
    from logger import get_logger
    _log = get_logger("adversarial_governance")
except Exception:
    _log = None


def _call_reviewer(prompt: str, timeout: int = MONITOR_TIMEOUT) -> Dict[str, Any]:
    """调用 reviewer profile 执行 monitor 任务。"""
    import adversarial_governance

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
            cwd=str(adversarial_governance.PROJECT_ROOT),
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


def build_monitor_prompt(
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
    standards_path: Optional[Path] = None,
) -> str:
    """构造 monitor prompt。"""
    import adversarial_governance

    prev_hint = f"\n【writer 修改前申请书】{prev_draft_path}" if prev_draft_path else ""
    dim_str = "、".join(f"{k}={v:.2f}" for k, v in dim_scores.items())
    if standards_path is None:
        standards_path = adversarial_governance.STANDARDS_PATH
    standards_rel = str(standards_path.relative_to(adversarial_governance.PROJECT_ROOT))
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
    standards_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """执行一轮 monitor，返回结构化结果。"""
    critic_report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
    current_draft_path = prop_dir / "04_proposal" / "proposal-draft.md"

    prompt = build_monitor_prompt(
        proposal_id, project_type, round_num, section_key, section_name,
        critic_report_path, current_draft_path, prev_draft_path,
        score_before, score_after, dim_scores,
        standards_path=standards_path,
    )

    result = _call_reviewer(prompt)
    output = result.get("output", "")

    parsed = _extract_json_object(output) or {}

    # 独立评分：优先取 JSON，否则从文本解析
    monitor_score = _safe_float(parsed.get("monitor_independent_score"), 0.0)
    if monitor_score == 0.0:
        monitor_score = _extract_overall_score(output)
    # v6.8.10: 当 monitor_score 仍为 0 时，记录 reviewer 原始输出用于调试
    monitor_score_valid = monitor_score > 0.0
    if not monitor_score_valid:
        if _log:
            _log.warning(
                f"[monitor] {proposal_id} r{round_num} {section_key} "
                f"monitor_independent_score=0，解析失败。"
                f" reviewer 输出前 500 字符: {output[:500]}"
            )
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
        writer_prohibitions = [v["type"] for v in detect_writer_prohibitions(
            current_draft_text, prev_draft_text, critic_text
        )]
    if not critic_prohibitions:
        critic_prohibitions = [v["type"] for v in detect_critic_prohibitions(
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
