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


def _build_monitor_review_view(prop_dir: Path, round_num: int) -> Optional[Path]:
    """生成 monitor 评审视图：正文章节拼接（排除 references/骨架）。

    v6.9.61：monitor 此前读组装全文 proposal-draft.md（实测 40-140KB，
    含 references 列表与 full_review 骨架——与 meta-review 无关的输入），
    是 new-idea monitor 4 连空输出超时（600s 触顶）的直接输入侧根因。
    critic 侧同类问题已于 v6.9.46/53 排除，monitor 是最后一个未瘦身的
    读取方。视图写 05_review/.monitor-view-rN.md 供 prompt 引用。
    """
    try:
        sec_dir = prop_dir / "04_proposal" / "sections"
        if not sec_dir.exists():
            return None
        parts = []
        for key, cn in (("rationale", "立项依据"), ("content", "研究内容"),
                        ("scheme", "研究方案")):
            p = sec_dir / f"{key}.md"
            if p.exists():
                parts.append(p.read_text(encoding="utf-8").strip())
        if not parts:
            return None
        out = prop_dir / "05_review" / f".monitor-view-r{round_num}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            "<!-- v6.9.61 monitor 评审视图：正文三章节（references/骨架已排除） -->\n\n"
            + "\n\n---\n\n".join(parts),
            encoding="utf-8",
        )
        return out
    except Exception:
        return None


def _build_monitor_diff_summary(
    current: str, prev: str, prop_dir: Path, round_num: int,
) -> Optional[Path]:
    """生成 writer 修改前后 diff 摘要（零 LLM，替代让 LLM 读第二份全文）。

    v6.9.61：旧 prompt 同时给 current/prev 两份组装全文（合计 80-280KB）
    供 LLM 对比。difflib 程序化生成统一 diff，限头部 ±400 行，写
    05_review/.monitor-diff-rN.md。
    """
    try:
        import difflib
        diff = list(difflib.unified_diff(
            prev.splitlines(keepends=True),
            current.splitlines(keepends=True),
            fromfile=f"prev-r{round_num - 1}", tofile=f"current-r{round_num}",
            n=1,
        ))
        if not diff:
            return None
        body = "".join(diff[:400])
        if len(diff) > 400:
            body += f"…（共 {len(diff)} 行 diff，已截断至前 400 行）\n"
        out = prop_dir / "05_review" / f".monitor-diff-r{round_num}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            f"<!-- v6.9.61 程序 diff：writer 本轮修改（+新增/-删除） -->\n\n```diff\n{body}```\n",
            encoding="utf-8",
        )
        return out
    except Exception:
        return None


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
    diff_summary_path: Optional[Path] = None,
) -> str:
    """构造 monitor prompt。

    v6.9.61 输入瘦身：
    - current_draft_path 由调用方传入"评审视图"（正文三章节，排除
      references/骨架），不再是组装全文；
    - prev_draft_path 由 diff_summary_path（程序化 diff 摘要）替代——
      monitor 只需知道"改了什么"，不需要再读一份全文；
    - critic 报告超阈值时由调用方换 digest 路径。
    """
    import adversarial_governance

    if diff_summary_path is not None:
        prev_hint = (
            f"\n【writer 本轮修改 diff（程序生成，+新增/-删除）】{diff_summary_path}"
        )
    elif prev_draft_path:
        prev_hint = f"\n【writer 修改前申请书】{prev_draft_path}"
    else:
        prev_hint = ""
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

    # v6.9.61 输入瘦身（LLM prompt 侧）：
    # ① 评审视图替代组装全文（排除 references/骨架，40-140KB→正文三章节）；
    # ② 程序 diff 摘要替代 prev 全文（monitor 只需"改了什么"）；
    # ③ critic 报告超阈值换 digest。
    # 规则检测（detect_*_prohibitions）仍读全文——本地零成本，不受影响。
    view_path = _build_monitor_review_view(prop_dir, round_num)
    prompt_current = view_path if view_path else current_draft_path
    diff_path = None
    if prev_draft_path and prev_draft_path.exists():
        try:
            diff_path = _build_monitor_diff_summary(
                current_draft_path.read_text(encoding="utf-8"),
                prev_draft_path.read_text(encoding="utf-8"),
                prop_dir, round_num,
            )
        except Exception:
            diff_path = None
    prompt_critic = critic_report_path
    try:
        from proposal_lifecycle.section_hygiene import build_critic_digest
        _dg = build_critic_digest(critic_report_path)
        if _dg:
            prompt_critic = _dg
    except Exception:
        pass

    prompt = build_monitor_prompt(
        proposal_id, project_type, round_num, section_key, section_name,
        prompt_critic, prompt_current, prev_draft_path,
        score_before, score_after, dim_scores,
        standards_path=standards_path,
        diff_summary_path=diff_path,
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
        # v6.8.47: 暴露分数有效性标志。0.0 意味着 JSON+文本双解析失败，
        # 下游奖惩（apply_monitor_result）据此跳过扣分，防止解析失败被当作真实 0 分顶格误扣
        "monitor_score_valid": monitor_score_valid,
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
