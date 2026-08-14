from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import os
import subprocess

from common import now_utc, load_json, hermes_subprocess_env

import proposal_lifecycle as _pl

from proposal_sections import ProposalSections, PROPOSAL_SECTIONS

from proposal_lifecycle.constants import (
    _log,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_SCORE_THRESHOLD,
)

# v6.8.6: 范本写作标杆已提炼嵌入 nsfc-standards.json 的
# reference_materials.style_benchmark 字段，agent 读 JSON 即可获取全部规则，
# 无需每次读原始范本文件（节省 ~29KB token/次）。


class OptimizeMixin:
    # ------------------------------------------------------------------
    # 对抗优化循环
    # ------------------------------------------------------------------

    def _get_quality_threshold(self, project_type: str) -> Dict[str, Any]:
        """从 nsfc-standards.json 读取项目类型的质量阈值。"""
        standards = load_json(self.standards_path, default={})
        types = standards.get("project_types", {})
        return types.get(project_type, {}).get("quality_threshold", {
            "min_overall_score": DEFAULT_SCORE_THRESHOLD,
            "max_high_issues": 0,
            "max_medium_issues": 3,
        })

    def optimize_cycle(
        self,
        proposal_id: str,
        max_rounds: int = DEFAULT_MAX_ROUNDS,
        critic_timeout: int = 600,
        writer_timeout: int = 900,
    ) -> Dict[str, Any]:
        """执行一轮 writer-critic 对抗优化循环。

        流程：critic 评审 → writer 根据评审意见优化 → 记录分数变化

        Args:
            proposal_id: 课题 ID
            max_rounds: 最大对抗轮数
            critic_timeout: critic profile 超时
            writer_timeout: writer profile 超时

        Returns:
            {round, score_before, score_after, issues_found, done, reason}
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal 未注册"}

        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}

        project_type = prop_state.get("project_type", "general")
        threshold = self._get_quality_threshold(project_type)
        current_round = prop_state.get("optimization_rounds", 0)

        if current_round >= max_rounds:
            return {"success": False, "error": f"已达最大轮数 {max_rounds}"}

        # P1-1: 确定本轮聚焦章节（轮转 + 每4轮整体审查）
        # v6.8.16 改进4: 维度轮换——连续 3 轮在同一维度原地踏步则跳过
        # v6.8.24 修复: 旧版窗口 [-6:] 在 5-section 轮转下同 section 最多出现 2 次，
        # 阈值 3 永远不可达。改为 [-12:]（覆盖 2+ 个完整轮转周期）。
        section_cycle = current_round % (len(PROPOSAL_SECTIONS) + 1)
        if section_cycle < len(PROPOSAL_SECTIONS):
            focus_section = PROPOSAL_SECTIONS[section_cycle]
            is_full_review = False
            # 检查该维度是否连续 3 轮无提升
            score_history = prop_state.get("score_history", [])
            if len(score_history) >= 6:
                same_section_rounds = [
                    h for h in score_history[-12:]
                    if h.get("focus_section") == focus_section.get("key")
                ]
                if len(same_section_rounds) >= 3:
                    deltas = [
                        same_section_rounds[i + 1]["score"] - same_section_rounds[i]["score"]
                        for i in range(len(same_section_rounds) - 1)
                    ]
                    if all(abs(d) < 0.01 for d in deltas[-3:]):
                        # 该维度原地踏步，强制切换到最弱维度
                        _dim_scores = score_history[-1].get("dim_scores", {})
                        _weakest = min(_dim_scores, key=_dim_scores.get) if _dim_scores else None
                        if _weakest and _weakest != focus_section.get("key"):
                            for _sec in PROPOSAL_SECTIONS:
                                if _sec.get("key") == _weakest:
                                    focus_section = _sec
                                    break
                            if _log:
                                _log.info(
                                    f"[{proposal_id}] 维度轮换: {section_cycle}→{focus_section['key']}"
                                    f"（连续3轮原地踏步，切换到最弱维度）"
                                )
        else:
            focus_section = None  # 第4轮做整体一致性审查
            is_full_review = True

        # 读取当前申请书
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        if not proposal_path.exists():
            return {"success": False, "error": "申请书不存在，请先执行管线生成初稿"}

        score_before = prop_state.get("last_score", 0.0)

        # v6.8.17: 加载历史人工审核反馈（反馈闭环——从对话中学习）
        # _run_critic 内部会各自加载 _load_human_feedback_block（v6.8.19 修复：
        # 避免跨方法 NameError），optimize_cycle 层不再重复加载

        # 1. critic 评审
        if _log:
            section_name = focus_section["cn"] if focus_section else "整体一致性"
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: critic 评审（聚焦：{section_name}）")
        # v6.8.7: 程序化 AI 写作模式检测——在 critic 之前运行，产出表达质量天花板
        sections_obj = ProposalSections(prop_dir / "04_proposal")
        sections_obj.ensure_split()
        # v6.8.38: 基于实际 sections 文件重算 missing_sections。该字段只在初始化时写入
        # (initialization.py)，之后 writer 补全模块也不刷新，会停留在旧值（如 moire 曾标
        # 缺 innovation/plan/outcome，但这些压根不在 5 标准模块内、且文件实际都在），导致
        # critic 被引导去"重点检查"已存在的模块。此处每轮按 section_exists(内容>50字)重算
        # 并回写 prop_state，让 critic 聚焦真正缺失/空置的模块。
        missing_sections = [s["key"] for s in PROPOSAL_SECTIONS
                            if not sections_obj.section_exists(s["key"])]
        if missing_sections != prop_state.get("missing_sections"):
            prop_state["missing_sections"] = missing_sections
            self._set_proposal_state(proposal_id, prop_state)
        ai_check = self._detect_ai_patterns(prop_dir, sections_obj)
        if _log:
            _log.info(f"[{proposal_id}] AI 检测: ceiling={ai_check['ceiling']:.2f}, "
                       f"issues={len(ai_check['top_issues'])}")

        critic_result = self._run_critic(
            proposal_id, prop_dir, project_type, current_round + 1, critic_timeout,
            focus_section=focus_section, is_full_review=is_full_review,  # P1-1
            missing_sections=missing_sections,
            ai_check_result=ai_check,  # v6.8.7: 传入程序化检测结果
        )
        if _log:
            elapsed = critic_result.get("elapsed_s", 0)
            _log.info(
                f"[{proposal_id}] 对抗轮 {current_round + 1}: critic 完成 "
                f"success={critic_result.get('success')} elapsed={elapsed}s"
            )

        # v6.7.4 修复：critic 失败/超时（如 elapsed=300s success=False）时不应计入一轮，
        # 否则 lifecycle 的 optimization_rounds 与实际 critic 报告文件脱节，导致一致性检查失败。
        if not critic_result.get("success"):
            err = critic_result.get("error", "unknown")
            if _log:
                _log.warning(
                    f"[{proposal_id}] 对抗轮 {current_round + 1}: critic 失败（{err[:80]}），"
                    f"不计入本轮，跳过 writer"
                )
            return {
                "success": False,
                "round": current_round + 1,
                "score_before": score_before,
                "score_after": score_before,
                "score_delta": 0.0,
                "error": err,
                "reason": "critic 失败，未修改状态",
            }

        # 预解析维度分数，供 writer 聚焦（P0-2）
        pre_dims = self._extract_dimension_scores(critic_result)
        pre_weakest = self._get_weakest_dimension(pre_dims)

        # P1-2: 文献定向补充（严谨性不足时触发 researcher 检索）
        lit_supplement = ""
        if pre_dims.get("rigor", 1.0) < 0.70 or self._has_lit_gap(critic_result):
            if _log:
                _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: researcher 定向检索文献缺口")
            lit_supplement = self._run_researcher_targeted(
                proposal_id, prop_dir, critic_result, focus_section,
                timeout=600,
            )

        # 2. writer 根据评审意见优化
        if _log:
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: writer 优化")
        writer_result = self._run_writer_optimize(
            proposal_id, prop_dir, project_type, critic_result, writer_timeout,
            weakest_dim=pre_weakest, dim_scores=pre_dims,  # P0-2
            focus_section=focus_section, is_full_review=is_full_review,  # P1-1
            lit_supplement=lit_supplement,  # P1-2
            missing_sections=missing_sections,
            ai_check_result=ai_check,  # v6.8.7: 传入程序化检测结果
        )
        if _log:
            elapsed = writer_result.get("elapsed_s", 0)
            _log.info(
                f"[{proposal_id}] 对抗轮 {current_round + 1}: writer 完成 "
                f"success={writer_result.get('success')} elapsed={elapsed}s"
            )

        # 3. 解析新分数（v6.6.3：优先从 critic 写入的 report_path 文件读取，
        #    hermes stdout 摘要通常只截取前几行，遗漏末尾的"## 评分"代码块）
        report_path = prop_dir / "05_review" / f"critic-round-{current_round + 1}.md"

        # v6.7.1: critic 通过 hermes agent loop 异步写盘，等待文件生成且稳定
        if not (report_path.exists() and report_path.stat().st_size > 100):
            waited = self._wait_for_critic_report(report_path, timeout=30)
            if waited and _log:
                _log.info(f"[{proposal_id}] critic 报告已生成: {report_path.name}")

        if report_path.exists() and report_path.stat().st_size > 100:
            try:
                file_content = report_path.read_text(encoding="utf-8")
                file_result = {"output": file_content}
                score_after = self._extract_score(file_result)
                dim_scores = self._extract_dimension_scores(file_result)  # P0-2
                issues = self._extract_issues(file_result)
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 读取 critic 报告失败: {e}，回退到 stdout")
                # 回退：使用 hermes stdout 摘要
                score_after = self._extract_score(critic_result)
                dim_scores = self._extract_dimension_scores(critic_result)
                issues = self._extract_issues(critic_result)
        else:
            # 文件未生成（critic 未写盘），用 stdout 摘要
            if _log:
                _log.warning(f"[{proposal_id}] critic 报告未生成，使用 stdout 摘要评分")
            score_after = self._extract_score(critic_result)
            dim_scores = self._extract_dimension_scores(critic_result)
            issues = self._extract_issues(critic_result)
        weakest_dim = self._get_weakest_dimension(dim_scores)

        # v6.8.7: 程序化天花板强制执行——表达质量得分不得超过 AI 检测产出的天花板
        if ai_check and "expression" in dim_scores:
            ceiling = ai_check.get("ceiling", 1.0)
            if dim_scores["expression"] > ceiling:
                if _log:
                    _log.warning(
                        f"[{proposal_id}] 表达质量 {dim_scores['expression']:.2f} > 天花板 {ceiling:.2f}，"
                        f"强制 cap 至 {ceiling:.2f}"
                    )
                dim_scores["expression"] = ceiling
                # 重新计算综合分
                score_after = self._recalculate_score(dim_scores, project_type)

        # v6.8.8: 综合分天花板——scoring_integrity_rules.rule_1
        # AI 检测天花板低时，综合分也必须受限，防止其他维度高分掩盖表达质量短板
        if ai_check:
            ai_ceiling = ai_check.get("ceiling", 1.0)
            overall_ceiling = 1.0
            if ai_ceiling < 0.7:
                overall_ceiling = 0.75
            elif ai_ceiling < 0.8:
                overall_ceiling = 0.80
            elif ai_ceiling < 0.9:
                overall_ceiling = 0.85
            if score_after > overall_ceiling:
                if _log:
                    _log.warning(
                        f"[{proposal_id}] 综合分 {score_after:.2f} > 综合天花板 {overall_ceiling:.2f}"
                        f"（AI天花板={ai_ceiling:.2f}），强制 cap"
                    )
                score_after = overall_ceiling

        # v6.8.8: references 评审专用计分——N/A 维度不纳入加权
        section_key_for_check = focus_section["key"] if focus_section else "full_review"
        if section_key_for_check == "references" and dim_scores:
            # references 评审：综合分 = (严谨性 + 完整性) / 2，忽略 N/A 维度
            ref_dims = {k: v for k, v in dim_scores.items() if k in ("rigor", "completeness") and v > 0}
            if ref_dims:
                score_after = sum(ref_dims.values()) / len(ref_dims)
                if _log:
                    _log.info(f"[{proposal_id}] references 评审专用计分: {score_after:.2f} (dims={ref_dims})")

        # v6.8.8: 评审报告完整性验证——anti_superficial_review.programmatic_validation
        report_invalid_reason = ""
        if report_path.exists() and report_path.stat().st_size > 100:
            try:
                report_content = report_path.read_text(encoding="utf-8")
                has_anchor = "锚点对比" in report_content or "范本对标" in report_content
                has_style = "写作风格" in report_content
                # references 评审不需要锚点对比和写作风格评估
                if section_key_for_check != "references":
                    if not has_anchor:
                        report_invalid_reason = "缺少'锚点对比'段落"
                    elif not has_style:
                        report_invalid_reason = "缺少'写作风格评估'段落"
                if report_invalid_reason and _log:
                    _log.warning(f"[{proposal_id}] 评审报告不完整: {report_invalid_reason}")
            except Exception:
                pass

        # P1-1: 确定本轮模块 key
        section_key = focus_section["key"] if focus_section else "full_review"

        # P1-3: 判断该模块是否"对抗胜利"（分数达标 + 各维度无短板）
        min_score = threshold.get("min_overall_score", DEFAULT_SCORE_THRESHOLD)
        weak_dims = [
            k for k, floor in self.DIMENSION_FLOOR.items()
            if k in dim_scores and dim_scores[k] < floor
        ]
        # v6.8.8: 评审报告不完整（缺锚点对比/写作风格评估）时强制不通过
        section_passed = (
            score_after >= min_score
            and len(weak_dims) == 0
            and not report_invalid_reason
        )

        # 4. 更新状态
        # v6.7.1：_set_proposal_state 内部已加 file_lock("proposal-lifecycle")，
        # 不再外层包 file_lock(f"proposal-{proposal_id}")，避免嵌套锁和潜在竞态
        prop_state = self._get_proposal_state(proposal_id)
        prop_state["optimization_rounds"] = current_round + 1
        # v6.8.21: 清理旧轮次 job
        from lifecycle.utils import archive_old_round_jobs
        archive_old_round_jobs(proposal_id, current_round + 1)
        prop_state["last_score"] = score_after
        prop_state["last_dim_scores"] = dim_scores  # P0-2: 记录维度分数
        # P1-3: 记录各模块对抗胜利状态
        section_passes = prop_state.get("section_passes", {})
        section_passes[section_key] = section_passed
        prop_state["section_passes"] = section_passes
        prop_state["score_history"].append({
            "round": current_round + 1,
            "score": score_after,
            "dim_scores": dim_scores,  # P0-2
            "weakest_dim": weakest_dim,  # P0-2
            "focus_section": section_key,  # P1-1
            "section_passed": section_passed,  # P1-3
            "issues_count": len(issues),
            "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
            "at": now_utc(),
        })
        prop_state["updated_at"] = now_utc()
        persisted = self._set_proposal_state(proposal_id, prop_state)
        if not persisted and _log:
            _log.error(f"[{proposal_id}] _lifecycle.json 状态更新失败")

        # 4.5 更新 proposal-brief（贯穿全生命周期的元信息）
        try:
            self.update_proposal_brief(proposal_id)
        except Exception:
            pass

        # v6.7.11: full_review 轮同步更新课题设想、方法学手册、文献阅读笔记
        if is_full_review and writer_result.get("success"):
            try:
                sync_result = self._sync_derivative_artifacts(proposal_id, prop_dir, timeout=300)
                if _log:
                    _log.info(
                        f"[{proposal_id}] 同步产物完成 success={sync_result.get('success')}"
                    )
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 同步产物失败: {e}")

        # v6.8.33: 轮次完成后立即同步知识库（事件驱动），覆盖 cron sweep/CLI 所有调用方
        try:
            from lifecycle.micro_scheduler import _sync_proposal_to_kb
            _sync_proposal_to_kb(proposal_id)
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 轮次完成 KB 同步失败: {e}")

        # 5. 判定是否达标
        done_result = self._check_done(proposal_id, threshold)

        return {
            "success": True,
            "round": current_round + 1,
            "score_before": score_before,
            "score_after": score_after,
            "score_delta": round(score_after - score_before, 4),
            "dim_scores": dim_scores,  # P0-2
            "weakest_dim": weakest_dim,  # P0-2
            "issues_found": len(issues),
            "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
            "done": done_result["done"],
            "reason": done_result["reason"],
            "threshold": threshold,
        }

    def _detect_ai_patterns(self, prop_dir: Path, sections: 'ProposalSections') -> Dict[str, Any]:
        """程序化检测申请书中的 AI 写作模式，产出表达质量天花板。

        这是评审跑偏的核心修复：不再让 LLM 凭感觉判断 AI 味，
        而是用代码客观计数，产出 expression_quality_ceiling，
        critic 的表达质量评分不得超过此天花板。

        Returns:
            {
                "ceiling": float,              # 表达质量天花板 (0.5-1.0)
                "total_chars": int,            # 全文字符数
                "details": {                   # 各检测项详情
                    "transition_words": {"count": N, "threshold": N, "penalty": float},
                    "template_phrases": {...},
                    "template_subject": {...},
                    "redundant_modifiers": {...},
                    "long_sentences": {...},
                    "meta_discourse": {...},
                    "excessive_bold": {...},
                    "bullet_list_substitution": {...},
                },
                "report_text": str,            # 供 critic/writer prompt 使用的文本报告
                "top_issues": List[str],       # 最严重的 AI 模式问题（供 writer 优先修复）
            }
        """
        import re

        # 读取所有正文章节内容
        body_keys = ["rationale", "content", "scheme"]
        texts = []
        for key in body_keys:
            try:
                txt = sections.read_section(key)
                if txt.strip():
                    texts.append(txt)
            except Exception:
                pass

        if not texts:
            return {"ceiling": 0.5, "total_chars": 0, "details": {}, "report_text": "（无法读取申请书内容）", "top_issues": []}

        full_text = "\n\n".join(texts)
        total_chars = len(full_text)
        if total_chars == 0:
            return {"ceiling": 0.5, "total_chars": 0, "details": {}, "report_text": "（申请书内容为空）", "top_issues": []}

        ceiling = 1.0
        details: Dict[str, Any] = {}
        top_issues: List[str] = []

        # 1. 死板关联词
        ai_transitions = ["在此基础上", "此外", "同时", "与此同时", "因此", "然而", "基于此"]
        transition_count = sum(full_text.count(w) for w in ai_transitions)
        transition_threshold = 8
        transition_penalty = max(0, (transition_count - transition_threshold) * 0.02)
        ceiling -= transition_penalty
        details["transition_words"] = {
            "count": transition_count, "threshold": transition_threshold,
            "penalty": round(transition_penalty, 4),
            "found": {w: full_text.count(w) for w in ai_transitions if full_text.count(w) > 0}
        }
        if transition_penalty > 0:
            top_issues.append(f"死板关联词超标：{transition_count}次（阈值{transition_threshold}），扣{transition_penalty:.2f}")

        # 2. 模板句式 "为...提供...基础/支撑/途径"
        template_patterns = [
            r"为.{1,20}提供.{0,10}(基础|支撑|途径|条件|工具|指导)",
        ]
        template_count = sum(len(re.findall(p, full_text)) for p in template_patterns)
        template_threshold = 8
        template_penalty = max(0, (template_count - template_threshold) * 0.03)
        ceiling -= template_penalty
        details["template_phrases"] = {
            "count": template_count, "threshold": template_threshold,
            "penalty": round(template_penalty, 4)
        }
        if template_penalty > 0:
            top_issues.append(f"模板句式'为...提供...'超标：{template_count}次（阈值{template_threshold}），扣{template_penalty:.2f}")

        # 3. 模板主语 "本项目拟/本项目将" 句首
        # 按句号分句，检查句首
        sentences = re.split(r'[。！？\n]', full_text)
        subject_patterns = ["本项目拟", "本项目将", "本项目计划", "本项目旨在"]
        subject_count = sum(1 for s in sentences if any(s.strip().startswith(p) for p in subject_patterns))
        subject_threshold = 5
        subject_penalty = max(0, (subject_count - subject_threshold) * 0.02)
        ceiling -= subject_penalty
        details["template_subject"] = {
            "count": subject_count, "threshold": subject_threshold,
            "penalty": round(subject_penalty, 4)
        }
        if subject_penalty > 0:
            top_issues.append(f"模板主语'本项目拟/将'句首超标：{subject_count}次（阈值{subject_threshold}），扣{subject_penalty:.2f}")

        # 4. 冗余修饰词
        redundant_words = ["显著", "重要", "系统", "良好", "成熟", "完整", "关键", "精准", "一系列", "有效", "高效"]
        redundant_count = sum(full_text.count(w) for w in redundant_words)
        redundant_threshold = 12
        redundant_penalty = max(0, (redundant_count - redundant_threshold) * 0.01)
        ceiling -= redundant_penalty
        details["redundant_modifiers"] = {
            "count": redundant_count, "threshold": redundant_threshold,
            "penalty": round(redundant_penalty, 4),
            "found": {w: full_text.count(w) for w in redundant_words if full_text.count(w) > 0}
        }
        if redundant_penalty > 0:
            top_issues.append(f"冗余修饰词超标：{redundant_count}次（阈值{redundant_threshold}），扣{redundant_penalty:.2f}")

        # 5. 超长句
        severe_count = sum(1 for s in sentences if len(s.strip()) > 120)
        long_penalty = severe_count * 0.02
        ceiling -= long_penalty
        details["long_sentences"] = {
            "severe_count": severe_count, "penalty": round(long_penalty, 4),
            "examples": [s.strip()[:80] + "..." for s in sentences if len(s.strip()) > 120][:3]
        }
        if long_penalty > 0:
            top_issues.append(f"超长句(>120字)：{severe_count}处，扣{long_penalty:.2f}")

        # 6. 元话语
        meta_patterns = [
            r"沿着.{0,10}这一主线", r"我们可以辨识", r"构成本项目的.{0,6}基线",
            r"一个根本性问题.{0,6}浮现", r"需要特别说明的是", r"需要澄清的是",
            r"需要指出的是", r"值得注意的是", r"这一判断构成", r"这一跃迁携带",
        ]
        meta_count = sum(len(re.findall(p, full_text)) for p in meta_patterns)
        meta_threshold = 2
        meta_penalty = max(0, (meta_count - meta_threshold) * 0.03)
        ceiling -= meta_penalty
        details["meta_discourse"] = {
            "count": meta_count, "threshold": meta_threshold,
            "penalty": round(meta_penalty, 4)
        }
        if meta_penalty > 0:
            top_issues.append(f"元话语超标：{meta_count}次（阈值{meta_threshold}），扣{meta_penalty:.2f}")

        # 7. 过度加粗
        bold_count = len(re.findall(r'\*\*[^*]+\*\*', full_text))
        bold_per_1k = bold_count / max(total_chars, 1) * 1000
        bold_threshold = 3  # per 1k chars
        bold_excess = max(0, bold_per_1k - bold_threshold)
        bold_penalty = 0.0
        if bold_excess > 0:
            bold_penalty = min(0.15, int(bold_excess) * 0.03)  # 最多扣0.15
        ceiling -= bold_penalty
        details["excessive_bold"] = {
            "count": bold_count, "per_1k_chars": round(bold_per_1k, 2),
            "threshold_per_1k": bold_threshold, "penalty": round(bold_penalty, 4)
        }
        if bold_penalty > 0:
            top_issues.append(f"加粗标记过多：{bold_count}处（{bold_per_1k:.1f}/千字，阈值{bold_threshold}/千字），扣{bold_penalty:.2f}")

        # 8. 编号列表替代论述
        # 检测连续的 "1. xxx\n2. xxx" 或 "- xxx\n- xxx" 模式
        list_blocks = len(re.findall(r'(?:^|\n)(?:\d+\.\s+.+(?:\n|$)){2,}', full_text))
        list_blocks += len(re.findall(r'(?:^|\n)(?:[-*]\s+.+(?:\n|$)){2,}', full_text))
        list_penalty = min(0.20, list_blocks * 0.05)
        ceiling -= list_penalty
        details["bullet_list_substitution"] = {
            "count": list_blocks, "penalty": round(list_penalty, 4)
        }
        if list_penalty > 0:
            top_issues.append(f"编号/bullet列表替代论述：{list_blocks}处，扣{list_penalty:.2f}")

        # 9. 自引用泛滥（v6.8.8: scoring_integrity_rules.rule_7）
        self_ref_patterns = [
            r"详\s*§\d", r"见\s*§\d", r"方法学手册\s*§\d",
            r"与\s*§\d\s*一致", r"详见\s*§\d", r"参见\s*§\d",
            r"详\s*§\d\.\d", r"见\s*§\d\.\d", r"方法学手册\s*§\d\.\d",
        ]
        self_ref_count = sum(len(re.findall(p, full_text)) for p in self_ref_patterns)
        self_ref_penalty = 0.0
        if self_ref_count > 15:
            self_ref_penalty = 0.10
        elif self_ref_count > 10:
            self_ref_penalty = 0.05
        ceiling -= self_ref_penalty
        details["self_reference"] = {
            "count": self_ref_count, "threshold_1": 10, "threshold_2": 15,
            "penalty": round(self_ref_penalty, 4)
        }
        if self_ref_penalty > 0:
            top_issues.append(f"自引用泛滥：{self_ref_count}次（阈值10/15），扣{self_ref_penalty:.2f}")

        # 天花板下限
        ceiling = max(ceiling, 0.5)

        # 构建报告文本
        report_lines = [
            f"【程序化 AI 写作模式检测报告】",
            f"全文字符数：{total_chars}",
            f"表达质量天花板：{ceiling:.2f}（critic 表达质量评分不得超过此值）",
            f"",
            f"各检测项详情：",
        ]
        for name, info in details.items():
            if info.get("penalty", 0) > 0:
                report_lines.append(f"  ⚠️ {name}: {info}")
            else:
                report_lines.append(f"  ✓ {name}: {info}")

        if top_issues:
            report_lines.append(f"")
            report_lines.append(f"最严重的 AI 模式问题（writer 必须优先修复）：")
            for issue in top_issues:
                report_lines.append(f"  - {issue}")

        report_text = "\n".join(report_lines)

        if _log:
            _log.info(f"AI pattern detection: ceiling={ceiling:.2f}, total_chars={total_chars}, "
                       f"issues={len(top_issues)}")

        return {
            "ceiling": round(ceiling, 4),
            "total_chars": total_chars,
            "details": details,
            "report_text": report_text,
            "top_issues": top_issues,
        }

    def _build_enforcement_checklist_text(
        self,
        standards_path: str,
        focus_section: Optional[Dict[str, str]],
        is_full_review: bool,
    ) -> str:
        """v6.8.8: 从 nsfc-standards.json 读取 enforcement_checklist 并格式化为 prompt 文本。

        这是评审跑偏的核心修复：不再依赖 LLM 读取 JSON 文件中的 review_checklist，
        而是由程序读取并直接嵌入 prompt，确保 LLM 能看到具体的检查条目。
        """
        try:
            standards = load_json(Path(standards_path), default={})
        except Exception:
            return ""

        section_standards = standards.get("section_standards", {})

        # 确定要读取的 section key
        if is_full_review:
            section_key = "full_review"
        elif focus_section:
            section_key = focus_section.get("key", "")
        else:
            section_key = ""

        if not section_key:
            return ""

        section_def = section_standards.get(section_key, {})
        ec = section_def.get("enforcement_checklist", {})
        items = ec.get("items", [])
        if not items:
            return ""

        # 格式化为 prompt 文本
        lines = [
            f"\n【执行清单（{section_def.get('cn', section_key)}——必须逐条检查，每条给出'通过/不通过'判断）】",
        ]
        for item in items:
            lines.append(f"  {item['id']}. {item['check']}")
            lines.append(f"     通过条件：{item['pass_if']}")
        lines.append("")
        lines.append("不通过条目数 > 3 时，该 section 得分不得高于 0.70。")
        lines.append("评审报告中必须包含'执行清单对照'段落，逐条报告通过/不通过状态。")
        lines.append("")

        # 添加锚点对比要求
        mc = section_def.get("mandatory_comparison", {})
        if mc:
            lines.append(f"【锚点对比（{section_def.get('cn', section_key)}——评审报告中必须包含，缺失则评审无效）】")
            lines.append(f"  格式：{mc.get('format', '引用申请书原文→引用锚点→指出差距→给出档位判定')}")
            for pair in mc.get("anchor_pairs", []):
                lines.append(f"  对比对：{pair}")
            lines.append(f"  {mc.get('blocking_rule', '缺失则评审无效')}")
            lines.append("")

        return "\n".join(lines)

    def _run_critic(
        self,
        proposal_id: str,
        prop_dir: Path,
        project_type: str,
        round_num: int,
        timeout: int,
        focus_section: Optional[Dict[str, str]] = None,
        is_full_review: bool = False,
        missing_sections: Optional[List[str]] = None,
        ai_check_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """派活给 critic profile 做对抗评审。

        P1-1: 支持章节级评审（focus_section）和整体审查（is_full_review）。
        v6.7.7: 默认按章节拆分文件读取，降低单次 LLM 负载、减少超时。
        v6.8.3-fix10: references 模块使用轻量化专用 prompt，不走重型评审流程。
        """
        sections = ProposalSections(prop_dir / "04_proposal")
        sections.ensure_split()  # 兼容旧格式：自动拆分
        standards_path = str(self.standards_path.relative_to(_pl.PROJECT_ROOT))
        report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # v6.7.7: 构建要读取的文件列表
        is_references = focus_section and focus_section.get("key") == "references"

        if is_references:
            # v6.8.3-fix10: references 模块轻量化 prompt
            # 参考文献检验不需要叙述式检查、创新性评分、7模块完整性检查
            # 聚焦：引文格式、编号一致性、引用相关性、缺失引用检测
            ref_file = prop_dir / "04_proposal" / "sections" / "references.md"
            # 同时读取正文，检查正文中的引用标记是否在参考文献列表中
            body_files = [
                str(prop_dir / "04_proposal" / "sections" / f"{s['key']}.md")
                for s in PROPOSAL_SECTIONS
                if s["key"] in ("rationale", "content", "scheme") and sections.section_exists(s["key"])
            ]
            read_instruction = (
                f"【参考文献文件】{ref_file}\n"
                f"【正文文件】\n" + "\n".join(f"- {p}" for p in body_files) +
                "\n\n请读取参考文献文件和正文文件，做参考文献检验。\n"
            )
            prompt = (
                f"请对以下 NSFC 申请书的参考文献做第 {round_num} 轮检验。\n\n"
                f"【项目类型】{project_type}\n\n"
                f"{read_instruction}\n"
                f"请执行以下检查（不需要检查写作风格、创新性或可行性）：\n"
                f"1. 引文格式：是否统一使用 [N] 编号，作者、年份、期刊、卷页是否完整\n"
                f"2. 编号一致性：正文中引用的 [N] 是否在参考文献列表中都能找到，反之亦然\n"
                f"3. 引用相关性：每条参考文献是否与申请书的科学问题相关，是否有无关引用\n"
                f"4. 缺失引用：正文中做出的重要论断是否缺少文献支撑\n"
                f"5. 引用数量：参考文献总数是否在 15-30 篇区间（NSFC 面上项目惯例）\n"
                f"6. 时效性：是否包含近 3 年的文献，是否有过于陈旧的引用\n\n"
                f"每个问题按严重程度分级（critical/high/medium/low），给出具体修改建议。\n\n"
                f"【评分（必填）】\n"
                f"只评两个维度（0-1），创新性和可行性标记为 N/A：\n"
                f"  - 严谨性（rigor）：引文格式、编号一致性、作者信息完整性\n"
                f"  - 完整性（completeness）：引用数量、时效性、缺失引用情况\n\n"
                f"在检验报告末尾，必须包含如下格式的评分块（供程序解析）：\n"
                f"```\n"
                f"## 评分\n"
                f"创新性：N/A\n"
                f"可行性：N/A\n"
                f"严谨性：0.75\n"
                f"完整性：0.90\n"
                f"综合评分：0.82\n"
                f"```\n"
                f"（注：创新性和可行性填 N/A，综合评分为严谨性和完整性的均值）\n"
                f"将检验报告写入：{report_path}\n"
            )
            # v6.8.37: references 检验超时从 300s 放宽到 600s。300s 对 references 丰富
            # 的课题偏紧（quantum-geometry 曾连续 3 次 300s 超时、重试耗尽卡住）；
            # 600s 与调用方 critic_timeout 默认值一致，仍短于主 critic 的 900s
            # （references 评审不评创新/可行性，较主 critic 轻）。
            return self._run_hermes("critic", prompt, min(timeout, 600))

        elif is_full_review:
            focus_text = (
                f"\n【本轮为整体一致性审查】\n"
                f"请检查三个章节之间的逻辑衔接、术语一致性、内容冗余/矛盾。\n"
                f"不需要逐段细审，聚焦整体连贯性。\n\n"
            )
            files_to_read = [
                str(prop_dir / "04_proposal" / "sections" / f"{s['key']}.md")
                for s in PROPOSAL_SECTIONS
                if sections.section_exists(s['key'])
            ]
            read_instruction = (
                "【申请书章节文件】\n" +
                "\n".join(f"- {p}" for p in files_to_read) +
                "\n\n请读取以上全部章节文件，做整体一致性审查。\n"
            )
        elif focus_section:
            focus_text = (
                f"\n【本轮聚焦章节】{focus_section['title']}（{focus_section['desc']}）\n"
                f"请重点深入评审该章节，其他章节只做简要一致性检查。\n"
                f"对该章节的评审应细致到段落级别。\n\n"
            )
            section_file = prop_dir / "04_proposal" / "sections" / f"{focus_section['key']}.md"
            files_to_read = [str(section_file)]
            read_instruction = (
                f"【申请书聚焦章节文件】{section_file}\n"
                f"请主要读取以上聚焦章节文件；如需检查跨章节一致性，可简要读取其他章节。\n\n"
            )
        else:
            focus_text = ""
            files_to_read = [str(prop_dir / "04_proposal" / "proposal-draft.md")]
            read_instruction = f"【申请书文件】{files_to_read[0]}\n"

        # v6.7.10: 模块完整性检查提示
        section_key_to_cn = {s["key"]: s["cn"] for s in PROPOSAL_SECTIONS}
        missing_cn = [section_key_to_cn.get(k, k) for k in (missing_sections or [])]
        completeness_hint = ""
        if missing_cn:
            completeness_hint = (
                f"\n【模块完整性警告】当前申请书缺失以下模块：{', '.join(missing_cn)}。\n"
                f"请在「严谨性」维度大幅扣分（缺 1 个模块不高于 0.5，缺 2 个及以上不高于 0.3），\n"
                f"并将每个缺失模块标记为 [critical] issue，要求 writer 必须补齐。\n"
            )

        # v6.8.6: 强化叙述式写作风格检查 + 去AI味检测 + 指标红线 + 内容边界
        narrative_rules = (
            "\n【写作风格红线（重点检查，对照范本 references/nsfc-templates/）】\n"
            "申请书必须是连贯的叙述/论述式研究故事，不是知识整理或文献罗列。\n"
            "评审时请以范本的语体风格和论证密度为标杆，重点检查并严惩以下问题：\n\n"
            "■ 叙述式违规：\n"
            "- 是否以科学问题为主线展开，而不是罗列文献、数据或概念\n"
            "- 是否存在 'A做了X，B做了Y，C做了Z' 式的文献堆砌\n"
            "- 是否存在大量条目式、bullet-list 式表达替代论证\n"
            "- 段落之间是否有过渡，是否形成逻辑递进\n"
            "- 研究内容是否围绕核心问题组织，而非平行堆砌\n"
            "- 研究方案是否说明'为什么选这个方法'，而非只罗列步骤\n"
            "- 立项依据是否采用五层递进结构（大背景→领域脉络→核心问题→国内现状→本项目定位）\n"
            "- 研究目标是否每条至少含1个可检验量化指标\n"
            "- 特色与创新是否遵循四步闭环（现有局限→方案→量化优势→定位收束）\n\n"
            "■ AI写作味（issue_type 使用 'anti_ai'）：\n"
            "- 死板关联词高频出现：在此基础上、此外、同时、与此同时、因此、然而、基于此\n"
            "- 模板句式：'为…提供…基础/支撑/途径' 超过15次 → [high] issue\n"
            "- 模板主语滥用：'本项目拟/本项目将' 作为句首滥用法\n"
            "- 冗余修饰堆砌：显著、重要、系统、良好、成熟、完整、关键、精准\n"
            "- 空洞概括句：'具有决定性意义''迈向新的高度'\n"
            "- 超长句：单句>80字应标记，>120字标记为 [high] issue\n\n"
            "■ 指标红线 P0（issue_type 使用 'red_line'，severity 标为 [critical]）：\n"
            "- 同一指标在不同章节数值或口径不一致\n"
            "- 同时宣称两个存在原理约束的量且违反物理约束\n"
            "- 理论框架未注明适用条件与失效边界\n"
            "- '首次''尚未见报道'等缺乏文献支撑\n"
            "- 指标无'方案→指标'的实现路径\n\n"
            "■ 内容越界（issue_type 使用 'boundary'）：\n"
            "- 研究方案中出现'为什么研究/为什么可行'口吻（应归研究内容或可行性）\n"
            "- 可行性分析复述研究方案技术细节（应聚焦'为什么能做成'）\n"
            "- 跨章节大量重复内容\n\n"
            "■ 锚点回归（强制要求）：\n"
            "- 评分时必须读取 general_principles.scoring_rubric，逐条对照档位描述打分\n"
            "- 评分时必须读取 reference_materials.benchmark_anchors，将申请书文字与范本锚点段落对比\n"
            "- 每条评审意见必须标注违反的 rubric 条款编号或标准条款名称\n"
            "- 若申请书存在 anti_ai_patterns 中列举的模式，表达质量直接扣至 0.6-0.7 区间\n"
            "- 若存在 indicator_red_lines 违规，严谨性直接扣至 0.6-0.7 区间\n"
            "- 不得凭感觉打分，必须给出档位依据\n\n"
            "凡是发现上述问题，必须标记 severity 和 issue_type，并给出具体改写建议。\n"
            "问题按 P1（必改）/P2（强烈建议）/P3（建议）分级。\n"
        )

        # v6.8.7: 程序化 AI 检测结果（强制锚点回归机制）
        ai_check_text = ""
        if ai_check_result:
            ai_check_text = (
                f"\n{ai_check_result['report_text']}\n\n"
                f"⚠️ 强制约束：你的表达质量评分不得超过天花板 {ai_check_result['ceiling']:.2f}。\n"
                f"若天花板 < 0.7，你必须在评审报告中明示'程序化检测发现AI写作模式，表达质量被强制限制'。\n"
                f"你必须将检测到的 AI 模式问题列入问题清单，标注 issue_type='anti_ai'，severity ≥ [high]。\n"
            )

        # v6.8.8: 嵌入 section enforcement_checklist 到 prompt（不再依赖 LLM 读取 JSON）
        enforcement_checklist_text = self._build_enforcement_checklist_text(
            standards_path, focus_section, is_full_review
        )

        prompt = (
            f"请对以下 NSFC 申请书做第 {round_num} 轮对抗评审。\n\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path}，重点关注：\n"
            f"  - section_standards（每个 section 的详细撰写要求和评审清单，必须逐条对照）\n"
            f"  - programmatic_checks（程序化检测规则和表达质量天花板）\n"
            f"  - overall_review_requirements（整体评审要求，含防跑偏规则）\n"
            f"  - project_types.{project_type} 的评审标准与权重\n"
            f"  - general_principles.writing_style_rules（叙述式写作规则）\n"
            f"  - general_principles.writing_style_rules.anti_ai_patterns（去AI味清单）\n"
            f"  - general_principles.indicator_red_lines（P0指标红线）\n"
            f"  - general_principles.scoring_rubric（评分档位标准，必须逐条对照打分）\n"
            f"  - reference_materials.style_benchmark（范本写作标杆摘要）\n"
            f"  - reference_materials.benchmark_anchors（范本锚点段落，评分时对比使用）\n\n"
            f"{read_instruction}"
            f"{focus_text}"
            f"{completeness_hint}"
            f"{ai_check_text}\n"
            f"{enforcement_checklist_text}\n"
            f"{narrative_rules}\n"
            f"请执行：\n"
            f"0. 模块完整性检查：确认申请书是否包含标准模块。\n"
            f"1. 读取指定的申请书文件和质量标准配置文件\n"
            f"2. 【强制】逐条对照上方'执行清单'中的每一条，对每条给出'通过/不通过'判断，不通过须引用具体段落\n"
            f"3. 【强制】将申请书文字与 benchmark_anchors 中的范本锚点段落做结构化对比（引用申请书原文→引用锚点→指出差距）\n"
            f"4. 【强制】引用程序化 AI 检测结果，将检测到的 AI 模式列入问题清单\n"
            f"5. 按项目类型标准做红队评审，尽可能找出问题\n"
            f"6. 重点检查写作风格：凡是发现知识整理/文献罗列/条目式堆砌/缺乏连贯叙事，标记为 [high] narrative issue\n"
            f"7. 每个问题给出具体、可执行的修改建议，并标注违反的 rubric 条款或标准条款\n"
            f"8. 按严重程度分级（critical/high/medium/low）\n\n"
            f"【评审报告必须包含以下段落（缺一不可，缺失则评审无效）】\n"
            f"- '执行清单对照'段落：逐条报告上方执行清单的通过/不通过状态\n"
            f"- '写作风格评估'段落：引用程序化检测结果，评估叙述式写作合规性\n"
            f"- '锚点对比'段落：引用申请书原文与 benchmark_anchors 对比，指出差距\n"
            f"- '锚点回归'说明：每条评审意见标注违反的 rubric 档位或标准条款名称\n\n"
            f"【多维度评分（必填，按 scoring_rubric 档位打分）】\n"
            f"请从以下 4 个维度分别评分（0-1），每个维度必须引用 scoring_rubric 中对应档位描述作为依据：\n"
            f"  - 创新性（innovation）：科学问题是否新颖、方法是否有突破\n"
            f"  - 可行性（feasibility）：技术路线能否落地、是否有支撑\n"
            f"  - 严谨性（rigor）：逻辑链条、文献支撑是否充分、指标口径是否一致、模块是否完整\n"
            f"  - 表达质量（expression）：是否连贯叙述式行文、是否消除AI味、是否对标范本水准\n"
            f"  ⚠️ 表达质量评分不得超过程序化天花板。若天花板 < 0.7，表达质量必须 ≤ 天花板。\n\n"
            f"在评审报告末尾，必须包含如下格式的评分块（供程序解析）：\n"
            f"```\n"
            f"## 评分\n"
            f"创新性：0.85\n"
            f"可行性：0.80\n"
            f"严谨性：0.75\n"
            f"表达质量：0.70\n"
            f"综合评分：0.78\n"
            f"```\n"
            f"将评审报告写入：{report_path}\n"
        )

        # v6.8.17: 注入历史人工审核反馈（反馈闭环）
        # v6.8.19 修复: 在 _run_critic 自己的作用域内加载，避免跨方法未定义 NameError
        _human_feedback_block = self._load_human_feedback_block(proposal_id)
        if _human_feedback_block:
            prompt += _human_feedback_block

        # v6.8.22: 注入历史遗留 P0 记忆（断裂点1）——critic 需核对这些历史问题是否仍存在
        _p0_memory = self._build_p0_memory_text(proposal_id, exclude_resolved=True)
        if _p0_memory:
            prompt += (
                _p0_memory
                + "请逐条核对这些历史遗留问题在当前申请书中是否仍存在：\n"
                + "  - 若仍存在，必须在问题清单中再次标记（severity 不变或更高），并引用具体段落\n"
                + "  - 若已解决，请明确说明'已解决'，避免误报\n"
                + "严禁因为历史问题曾出现就重复机械扣分，务必基于当前文本实际判断。\n"
            )

        # v6.8.18: 注入 agent 分数反馈——让 critic 看到自己的表现，才能调整
        _score_feedback = self._load_agent_score_feedback("critic")
        if _score_feedback:
            prompt += _score_feedback

        return self._run_hermes("critic", prompt, timeout)

    def _load_human_feedback_block(self, proposal_id: str) -> str:
        """v6.8.19: 加载历史人工审核反馈的 prompt 片段（仅当存在时返回非空字符串）。

        抽出该方法是因为原版在 optimize_cycle 局部变量中加载一次后，
        在 _run_critic 方法内被引用，导致跨方法作用域 NameError。
        通过 proposal_id 重新查询 prop_state，避免跨方法依赖。
        """
        prop_state = self._get_proposal_state(proposal_id) or {}
        try:
            from proposal_lifecycle.feedback_archive import load_review_feedback_for_optimization
            block = load_review_feedback_for_optimization(prop_state)
        except Exception:
            return ""
        return block or ""

    def _load_agent_score_feedback(self, role: str) -> str:
        """v6.8.18: 加载 agent 分数反馈——让 agent 看到自己的表现历史。

        只有当分数 <80（偏离初始 100 较远）或最近 3 轮有 reason 时才注入，
        避免无意义的冗余。

        v6.8.24: 修复 JSON 路径 bug——agent-scores.json 顶层直接是 role key，
        旧版读 scores["agents"][role] 永远返回空 dict，导致奖惩反馈完全失效。
        """
        try:
            import json
            from pathlib import Path
            scores_path = _pl.PROJECT_ROOT / "memory" / "agent-scores.json"
            if not scores_path.exists():
                return ""
            scores = json.loads(scores_path.read_text(encoding="utf-8"))
            # v6.8.24: 实际结构是 {role: {score, history, ...}}，不是 {agents: {role: ...}}
            agent = scores.get(role, {})
            score = agent.get("score", 100)
            initial = agent.get("initial_score", 100)
            history = agent.get("history", [])

            if score >= 80 and not history:
                return ""  # 分数健康，无需反馈

            lines = [
                f"\n\n【你的表现评价（累积分数 {score}/{initial}）】\n",
            ]

            # 最近 3 轮的反馈
            recent = history[-3:] if len(history) >= 3 else history
            if recent:
                lines.append("近期评价：\n")
                for h in recent:
                    delta = h.get("score", h.get("delta", 0))
                    reason = h.get("reason", "")
                    at = h.get("at", h.get("timestamp", ""))[:10]
                    if reason:
                        lines.append(f"- [{at}] 分数变化 {delta:+.1f}：{reason[:200]}\n")

            if score < 40:
                lines.append(
                    "\n⚠ 你的分数已严重偏低。请特别注意：\n"
                )
                if role == "critic":
                    lines.append(
                        "- 严格但准确：评分必须与申请书实际质量匹配，不要虚高也不要过度苛刻\n"
                        "- 每个问题都要有具体引用和可操作的改进建议\n"
                    )
                else:
                    lines.append(
                        "- 必须实质性回应当前 critic 的所有重要问题\n"
                        "- 避免表面修改（改了措辞但没改内容）\n"
                    )

            return "".join(lines) if len(lines) > 2 else ""
        except Exception:
            return ""

    # P1-2: 文献缺口检测和定向检索
    def _has_lit_gap(self, critic_result: Dict[str, Any]) -> bool:
        """检测 critic 是否指出了文献缺口。"""
        output = critic_result.get("output", "")
        gap_keywords = ["文献不足", "缺乏文献", "文献缺口", "缺少引用", "引用不足",
                        "支撑不足", "无文献", "需补充文献", "文献支撑", "缺乏近"]
        return any(kw in output for kw in gap_keywords)

    def _run_gap_identifier(
        self,
        proposal_id: str,
        prop_dir: Path,
        critic_result: Dict[str, Any],
        focus_section: Optional[Dict[str, str]],
        timeout: int = 120,
    ) -> Optional[Path]:
        """v6.7.7: 从 critic 报告中识别文献缺口，输出结构化 gap analysis。

        将 researcher 拆分为两步：
        1. gap_identifier（轻量，快速）：分析 critic 报告，提取需要补充文献的论点
        2. literature_searcher（重）：根据 gap analysis 执行定向检索

        Returns:
            gap analysis JSON 文件路径；失败返回 None
        """
        section_hint = f"聚焦章节：{focus_section['cn']}\n" if focus_section else ""
        critic_output = critic_result.get("output", "")[:3000]

        target_dir = prop_dir / "02_literature" / "gap-analysis"
        target_dir.mkdir(parents=True, exist_ok=True)
        import time as _t
        gap_path = target_dir / f"gap-analysis-r{int(_t.time())}.json"

        prompt = (
            f"请分析以下评审报告，识别需要补充文献支撑的具体缺口。\n\n"
            f"【课题】{proposal_id}\n"
            f"{section_hint}"
            f"【评审报告内容】\n{critic_output}\n\n"
            f"请执行：\n"
            f"1. 逐条阅读评审报告中指出的文献/引用/支撑不足问题\n"
            f"2. 对每个问题，明确：论点是什么、缺什么类型的文献、建议检索关键词\n"
            f"3. 忽略与文献无关的问题（如逻辑、格式等）\n"
            f"4. 输出严格的 JSON 文件到：{gap_path}\n"
            f"JSON 格式：\n"
            f"{{\n"
            f"  \"gaps\": [\n"
            f"    {{\n"
            f"      \"claim\": \"需要支撑的论点\",\n"
            f"      \"missing_evidence\": \"缺少什么证据/文献\",\n"
            f"      \"search_keywords\": [\"keyword1\", \"keyword2\"],\n"
            f"      \"priority\": \"high|medium|low\"\n"
            f"    }}\n"
            f"  ]\n"
            f"}}\n"
        )

        result = self._run_hermes("researcher", prompt, timeout)
        if result.get("success") and gap_path.exists():
            if _log:
                _log.info(f"[{proposal_id}] 文献缺口识别完成: {gap_path.name}")
            return gap_path
        else:
            if _log:
                _log.warning(f"[{proposal_id}] 文献缺口识别失败: {result.get('error', '')[:100]}")
            return None

    def _run_literature_searcher(
        self,
        proposal_id: str,
        prop_dir: Path,
        gap_path: Path,
        focus_section: Optional[Dict[str, str]],
        timeout: int = 300,
    ) -> Optional[Path]:
        """v6.7.11: 根据 gap analysis 执行定向文献检索（知识库优先 + 精确联网补充）。

        改造：通过 LiteratureService 统一检索/入库/状态查询。

        Args:
            gap_path: _run_gap_identifier 生成的 JSON 文件路径

        Returns:
            lit-gap markdown 文件路径；失败返回 None
        """
        section_hint = f"聚焦章节：{focus_section['cn']}\n" if focus_section else ""

        target_dir = prop_dir / "02_literature" / "targeted-research"
        target_dir.mkdir(parents=True, exist_ok=True)
        import time as _t
        result_path = target_dir / f"lit-gap-{int(_t.time())}.md"

        # 改造：使用 LiteratureService 替换原有逻辑
        import json
        from literature_service import LiteratureService
        svc = LiteratureService()

        # 解析 gap 关键词
        try:
            gap_data = json.loads(gap_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            gap_data = {"gaps": []}
        gaps = gap_data.get("gaps", [])
        all_keywords = []
        for g in gaps:
            all_keywords.extend(g.get("search_keywords", []))
        gap_keywords = list(dict.fromkeys(all_keywords))[:10]  # 去重，最多 10 个

        # 1. 通过 LiteratureService.get_context() 获取本地知识库预检索结果
        kb_context = svc.get_context(gap_keywords=gap_keywords, proposal_id=proposal_id)

        # 2. 通过 LiteratureService.search() 执行联网检索
        papers = svc.search(keywords=gap_keywords, source="pipeline", proposal_id=proposal_id)

        # v6.8.44: 多源学术检索补充——在 hermes 联网检索基础上，
        # 叠加 OpenAlex（期刊论文）+ arXiv 检索结果，弥补单一 hermes 途径盲区。
        # 任一来源失败（限流/超时）不影响已有结果。
        multi_source_papers = []
        try:
            import external_fetcher as ef
            # 将 gap 关键词组合为检索查询（取前 2 个关键词，避免超长查询触发 OpenAlex 限制）
            combined_query = " ".join(gap_keywords[:2]) if gap_keywords else "high harmonic generation"
            oa_papers = ef.search_academic(
                combined_query, max_results=5,
                sources=("arxiv", "openalex"),
            )
            # 去重：与已有 hermes 检索结果对比（按 arxiv_id / doi / title）
            existing_keys = set()
            for p in papers:
                aid = p.get("arxiv_id", "")
                if aid:
                    existing_keys.add(f"arxiv:{aid}")
            for p in oa_papers:
                aid = p.get("arxiv_id", "")
                doi = (p.get("doi") or "").replace("https://doi.org/", "")
                title_key = p.get("title", "").strip().lower()[:80]
                key = f"arxiv:{aid}" if aid else (f"doi:{doi}" if doi else f"title:{title_key}")
                if key not in existing_keys:
                    existing_keys.add(key)
                    multi_source_papers.append(p)
            if _log and multi_source_papers:
                _log.info(
                    f"[{proposal_id}] 多源检索补充 {len(multi_source_papers)} 篇"
                    f"（OpenAlex+arXiv，去重后）"
                )
        except Exception as e:
            if _log:
                _log.warning(f"[{proposal_id}] 多源学术检索失败（降级跳过）: {e}")

        # 3. 构建输出 markdown（保持与原来相同的文件路径和格式）
        lines = [
            f"# 定向文献检索报告\n",
            f"## 课题\n{proposal_id}\n",
        ]
        if section_hint:
            lines.append(f"## 聚焦章节\n{section_hint}\n")
        lines.append(f"## 检索关键词\n- {'、'.join(gap_keywords)}\n")
        lines.append(f"## 本地知识库预检索结果\n{kb_context}\n")
        lines.append(f"## 新增检索结果\n")
        for p in papers:
            arxiv_id = p.get("arxiv_id", "")
            title = p.get("title", "")
            authors = p.get("authors", "")
            year = p.get("year", "")
            score = p.get("score", 0.5)
            tldr = p.get("tldr", "")
            source_tag = "本地知识库" if not p.get("is_new", True) else "联网检索"
            lines.append(f"- {arxiv_id} | {title} | {authors} | {year} | {score} | {tldr} | 来源：{source_tag}")

        # v6.8.44: 多源学术检索结果（期刊论文 + 预印本）
        if multi_source_papers:
            lines.append(f"\n## 多源学术检索补充（OpenAlex + arXiv）\n")
            for p in multi_source_papers:
                aid = p.get("arxiv_id", "")
                doi = (p.get("doi") or "").replace("https://doi.org/", "")
                title = p.get("title", "")
                authors_list = p.get("authors", [])
                authors = ", ".join(authors_list[:3]) if isinstance(authors_list, list) else str(authors_list)
                year = p.get("year", "")
                venue = p.get("venue", "")
                cit = p.get("citation_count", 0)
                source_tag = p.get("source", "academic")
                # 期刊论文优先显示 DOI，预印本显示 arXiv ID
                ident = f"arXiv:{aid}" if aid else (f"DOI:{doi}" if doi else "无ID")
                abstract = (p.get("abstract") or "")[:150]
                lines.append(
                    f"- {ident} | {title} | {authors} | {year} | {venue} | "
                    f"引用:{cit} | 来源：{source_tag} | {abstract}"
                )

        result_path.write_text("\n".join(lines), encoding="utf-8")

        # v6.8.44: 多源检索有结果时也算成功（hermes 可能无结果但 OpenAlex 有期刊论文）
        total_papers = len(papers) + len(multi_source_papers)
        if total_papers:
            if _log:
                _log.info(
                    f"[{proposal_id}] 文献检索完成: {result_path.name} "
                    f"(hermes={len(papers)}, 多源={len(multi_source_papers)})"
                )
            return result_path
        else:
            if _log:
                _log.warning(f"[{proposal_id}] 文献检索未返回结果")
            return None

    def _build_kb_context_from_gap(
        self,
        gap_path: Path,
        proposal_id: Optional[str] = None,
        top_k_per_gap: int = 3,
        max_total: int = 15,
    ) -> str:
        """v6.7.11: 根据 gap analysis 预检索本地知识资产。

        改造：内部通过 LiteratureService.get_context() 实现，统一检索路径。

        Returns:
            结构化本地知识文本；失败返回提示语
        """
        try:
            import json
            gap_data = json.loads(gap_path.read_text(encoding="utf-8"))
            gaps = gap_data.get("gaps", [])
            if not gaps:
                return "（无预检索结果）"

            # 收集所有关键词
            all_keywords = []
            for g in gaps:
                all_keywords.extend(g.get("search_keywords", []))
            gap_keywords = list(dict.fromkeys(all_keywords))[:10]

            from literature_service import LiteratureService
            svc = LiteratureService()
            return svc.get_context(gap_keywords=gap_keywords, proposal_id=proposal_id)
        except Exception as e:
            if _log:
                _log.warning(f"知识库预检索失败: {e}")
            return "（知识库预检索失败，请联网检索补充）"

    def _run_researcher_targeted(
        self,
        proposal_id: str,
        prop_dir: Path,
        critic_result: Dict[str, Any],
        focus_section: Optional[Dict[str, str]],
        timeout: int = 300,
    ) -> str:
        """v6.7.7: researcher 入口——先识别缺口，再执行检索，保持单 job 节奏。

        内部拆分为 _run_gap_identifier + _run_literature_searcher，
        但对外仍是一个 job 调用，避免 worker cron 节奏变慢。
        """
        # 第一步：识别缺口（轻量，默认 300s）
        gap_path = self._run_gap_identifier(
            proposal_id, prop_dir, critic_result, focus_section, timeout=300
        )
        if not gap_path:
            return ""

        # 第二步：执行检索（重量，剩余超时）
        result_path = self._run_literature_searcher(
            proposal_id, prop_dir, gap_path, focus_section, timeout=max(timeout - 300, 180)
        )
        if result_path:
            # v6.7.10: 自动将检索结果导入文献阅读笔记
            try:
                from literature_notes import LiteratureNotes
                ln = LiteratureNotes(prop_dir)
                imported = ln.import_from_report(result_path)
                if _log and imported:
                    _log.info(f"[{proposal_id}] 已导入 {imported} 条文献阅读笔记")
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 导入文献阅读笔记失败: {e}")
            return f"\n【文献补充（researcher 定向检索）】\n请参考 {result_path} 中的新文献，在修订时引用。\n"
        return ""

    def _run_writer_optimize(
        self,
        proposal_id: str,
        prop_dir: Path,
        project_type: str,
        critic_result: Dict[str, Any],
        timeout: int,
        weakest_dim: str = "",
        dim_scores: Optional[Dict[str, float]] = None,
        focus_section: Optional[Dict[str, str]] = None,
        is_full_review: bool = False,
        lit_supplement: str = "",
        missing_sections: Optional[List[str]] = None,
        ai_check_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """派活给 writer profile 根据评审意见优化申请书。

        P0-2: 聚焦最弱维度，针对性改进。
        P1-1: 支持章节级修订（focus_section）。
        v6.7.7: 章节级修订只写入对应 section 文件，再自动组装 proposal-draft.md。
        """
        sections = ProposalSections(prop_dir / "04_proposal")
        sections.ensure_split()
        standards_path = str(self.standards_path.relative_to(_pl.PROJECT_ROOT))
        # 找最新的 critic 报告
        review_dir = prop_dir / "05_review"
        critic_reports = sorted(review_dir.glob("critic-round-*.md"), reverse=True)
        latest_critic = str(critic_reports[0]) if critic_reports else ""

        # P0-2: 构建维度聚焦提示
        dim_focus = ""
        if weakest_dim and dim_scores:
            dim_cn = {"innovation": "创新性", "feasibility": "可行性", "rigor": "严谨性", "expression": "表达质量", "completeness": "完整性"}
            weakest_cn = dim_cn.get(weakest_dim, weakest_dim)
            dim_scores_str = "、".join(f"{dim_cn.get(k,k)} {v:.2f}" for k, v in dim_scores.items())
            dim_focus = (
                f"\n【维度评分（本轮聚焦）】\n"
                f"各维度：{dim_scores_str}\n"
                f"⚠️ 最弱维度：{weakest_cn}（{dim_scores[weakest_dim]:.2f}）\n"
                f"请优先改进 {weakest_cn} 相关的问题，这是本轮的聚焦重点。\n"
            )

        # v6.7.7: 构建写入目标与读取文件列表
        section_files = [
            str(prop_dir / "04_proposal" / "sections" / f"{s['key']}.md")
            for s in PROPOSAL_SECTIONS
            if sections.section_exists(s['key'])
        ]

        # v6.7.10: 构建缺失模块提示
        section_key_to_cn = {s["key"]: s["cn"] for s in PROPOSAL_SECTIONS}
        missing_cn = [section_key_to_cn.get(k, k) for k in (missing_sections or [])]
        missing_hint = ""
        if missing_cn:
            missing_hint = (
                f"\n【缺失模块必须补齐】当前申请书还缺少以下模块：{', '.join(missing_cn)}。\n"
                f"若本轮聚焦章节在缺失列表中，请先生成完整内容；\n"
                f"若其他缺失模块已有相关素材（如研究方案中包含预期成果描述），请拆分并补充独立文件。\n"
            )

        # 四大产物路径
        research_idea_path = prop_dir / "00_research_idea.md"
        methodology_manual_path = prop_dir / "04_proposal" / "methodology-manual.md"
        reading_notes_path = prop_dir / "02_literature" / "reading-notes.md"

        if focus_section:
            target_section_file = prop_dir / "04_proposal" / "sections" / f"{focus_section['key']}.md"
            section_focus = (
                f"\n【本轮聚焦章节】{focus_section['title']}\n"
                f"请只修改该章节文件：{target_section_file}\n"
                f"不要修改其他章节文件。\n"
                f"修改完成后，将优化后的完整章节内容覆盖写入 {target_section_file}\n"
                f"系统会自动根据章节文件重新组装 proposal-draft.md。\n"
            )
            # v6.8.22: 断裂点4——存在未解决 P0 时放宽章节限制，允许跨章节修复
            try:
                unresolved_p0 = [
                    e for e in self._load_open_critical_issues(proposal_id)
                    if isinstance(e, dict) and e.get("round_resolved") is None and not e.get("stale")
                ]
                if unresolved_p0:
                    cross_sections = sorted({e.get("section", "?") for e in unresolved_p0})
                    section_focus += (
                        f"\n【例外：历史遗留 P0 跨章节修复】\n"
                        f"当前存在 {len(unresolved_p0)} 条未解决的 critical/high 问题，"
                        f"涉及章节：{', '.join(cross_sections)}。\n"
                        f"为消除这些 P0，你可以一并修改上述涉及章节文件（即使不在本轮聚焦章节内），"
                        f"但每次改动必须与聚焦章节问题直接相关，避免无关大改。\n"
                    )
            except Exception:
                pass
            primary_read = str(target_section_file)
        elif is_full_review:
            target_section_file = None
            section_focus = (
                f"\n【本轮为整体一致性修订】\n"
                f"请只做章节间的衔接、术语统一、冗余删减，不要大幅改动内容。\n"
                f"可修改任意章节文件（在 {prop_dir}/04_proposal/sections/ 下），\n"
                f"但请保持各章节文件独立，系统会自动组装 proposal-draft.md。\n"
            )
            primary_read = str(prop_dir / "04_proposal" / "proposal-draft.md")
        else:
            target_section_file = None
            section_focus = ""
            primary_read = str(prop_dir / "04_proposal" / "proposal-draft.md")

        # v6.8.6: 强化叙述式写作风格要求 + 去AI味 + 范本对标
        narrative_requirement = (
            "\n【写作风格要求（必须遵守，对照范本 references/nsfc-templates/）】\n"
            "申请书必须是连贯的叙述/论述式研究故事，不是知识整理或文献罗列。\n"
            "撰写/修改前请先阅读范本文件，以范本的语体风格和论证密度为标杆。\n\n"
            "■ 叙述式写作核心规则：\n"
            "- 以科学问题为主线，所有内容服务于论证'为什么要做、为什么是你做、怎么做'\n"
            "- 使用连贯段落和过渡句，段落之间形成逻辑递进\n"
            "- 每一处文献引用都应嵌入论证链条，禁止 'A做了X，B做了Y' 式简单罗列\n"
            "- 禁止使用大量条目式、bullet-list 式表达替代论述\n"
            "- 立项依据采用五层递进：大背景→领域发展脉络→核心问题与挑战→国内研究现状→本项目定位\n"
            "- 研究内容突出内在逻辑和递进关系；研究目标每条至少含1个可检验量化指标\n"
            "- 研究方案讲清楚'为什么选这个方法、如何解决关键科学问题'\n"
            "- 特色与创新每点遵循四步闭环：现有局限→本项目方案→量化优势→创新定位收束\n"
            "- 方法学手册才是细节（公式/参数表/步骤）的归属地，申请书重思路重论证\n\n"
            "■ 去AI味（评审减分项，必须清除）：\n"
            "- 死板关联词：在此基础上、此外、同时、与此同时、因此、然而、基于此 → 用内容驱动衔接替代\n"
            "- 模板句式：'为…提供…基础/支撑/途径' → 改为具体动词（保障、确立、对接、满足、形成）\n"
            "- 模板主语滥用：'本项目拟/本项目将' → 删除模板主语，直接以动词或内容词开头\n"
            "- 冗余修饰：显著、重要、系统、良好、成熟、完整、关键、精准 → 逐处删除或换具体表述\n"
            "- 超长句：单句>80字应拆分，>120字属严重超长句（重点段每段不超过3个超长句）\n"
            "- 空洞概括句：'具有决定性意义''迈向新的高度' → 删除\n\n"
            "■ 指标红线（P0，违反即致命）：\n"
            "- 同一指标在不同章节的数值与口径必须一致\n"
            "- '首次''尚未见报道'等须有文献支撑，未完成研究用'拟/有望首次'\n"
            "- 理论框架须注明适用条件与失效边界\n"
            "- 研究方案须写明'方案→指标'的实现路径\n\n"
            "如果评审报告已指出 narrative/anti-AI 问题，必须优先重写为连贯叙述。\n"
        )

        # v6.8.7: 程序化 AI 检测结果——writer 必须修复检测到的 AI 模式问题
        ai_check_text = ""
        if ai_check_result and ai_check_result.get("top_issues"):
            ai_check_text = (
                f"\n【程序化 AI 写作模式检测结果（必须修复）】\n"
                f"表达质量天花板：{ai_check_result['ceiling']:.2f}\n"
                f"当前天花板{'低于 0.7，属于严重 AI 味' if ai_check_result['ceiling'] < 0.7 else '在 0.7 以上，但仍有改进空间'}。\n"
                f"检测到的问题：\n"
            )
            for issue in ai_check_result["top_issues"]:
                ai_check_text += f"  - {issue}\n"
            ai_check_text += (
                f"\n你必须在本次修改中优先解决上述 AI 模式问题：\n"
                f"  - 死板关联词 → 用内容驱动衔接替代（进而、据此、理解…后、确立后）\n"
                f"  - 模板句式'为...提供...' → 改为具体动词（保障、确立、对接、满足、形成）\n"
                f"  - 模板主语'本项目拟/将' → 删除，直接以动词或内容词开头\n"
                f"  - 冗余修饰 → 逐处删除或换具体表述\n"
                f"  - 超长句 → 拆分为短句（<60字）\n"
                f"  - 元话语 → 删除，直接陈述科学事实\n"
                f"  - 过度加粗 → 删除加粗标记，范本中几乎不用\n"
                f"  - 编号列表 → 改为连贯叙述式段落\n"
                f"修改后，每个段落与 benchmark_anchors 中的范本锚点段落对比，确保语体和论证密度达标。\n"
            )

        prompt = (
            f"请根据对抗评审意见优化申请书。\n\n"
            f"【主读取文件】{primary_read}\n"
            f"【所有章节文件】\n" +
            "\n".join(f"- {p}" for p in section_files) + "\n\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path}，重点关注：\n"
            f"  - section_standards（每个 section 的详细撰写要求，必须逐条对标）\n"
            f"  - programmatic_checks（程序化检测规则，了解哪些模式会被扣分）\n"
            f"  - writing_style_rules + anti_ai_patterns（写作风格与去AI味）\n"
            f"  - indicator_red_lines（指标红线）\n"
            f"  - content_boundaries（内容边界）\n"
            f"  - general_principles.scoring_rubric（评分档位标准，写作时对标目标档位≥0.9）\n"
            f"  - reference_materials.style_benchmark（范本写作标杆摘要）\n"
            f"  - reference_materials.benchmark_anchors（范本锚点段落，写作时模仿其语体和论证密度）\n"
            f"【评审报告】{latest_critic}\n"
            f"{dim_focus}"
            f"{section_focus}"
            f"{missing_hint}"
            f"{lit_supplement}"
            f"{ai_check_text}\n"
            f"{narrative_requirement}\n"
            f"请执行：\n"
            f"1. 读取主读取文件（章节级修订只读聚焦章节，整体修订可读全部章节）\n"
            f"2. 读取评审报告中的所有问题\n"
            f"3. 逐条解决每个问题（按严重程度优先）\n"
            f"4. 重点改进最弱维度相关的问题\n"
            f"5. 如果评审报告存在 narrative/list-style 类问题，必须将对应段落重写为连贯叙述式论述\n"
            f"6. 只修改聚焦章节文件（或整体衔接涉及的章节文件），保持其他章节不变（增量优化）\n"
            f"7. 将优化后的内容覆盖写入对应章节 .md 文件（不是 proposal-draft.md）\n"
            f"8. 补齐缺失模块：若当前聚焦章节或 missing 列表中的模块为空，必须生成完整内容\n"
            f"9. 同步更新四大产物：\n"
            f"   a) 课题设想：{research_idea_path}\n"
            f"      若研究内容、技术路线、创新点有重大调整，同步更新课题设想对应部分。\n"
            f"   b) 方法学手册：{methodology_manual_path}\n"
            f"      申请书重思路，方法学手册重细节（公式推导/参数表/技术路线图/局限性）。\n"
            f"      只更新与聚焦章节对应的细节部分。\n"
            f"   c) 文献阅读笔记：{reading_notes_path}\n"
            f"      若本轮使用了新文献（尤其是 {lit_supplement[:80] if lit_supplement else '定向检索结果'}），\n"
            f"      请在笔记中追加一条记录：阅读日期、文献标题、来源、核心结论、与课题关联、已引用位置。\n"
        )

        # v6.8.17: cross-proposal 范例注入——从最高分课题提取范例段落
        # v6.8.19 修复: section_key 必须从 focus_section 派生（原版直接引用未定义变量，
        # 导致 writer 每次必抛 NameError，4h 内 5 个 writer job 全失败）
        if focus_section:
            section_key = focus_section.get("key", "")
        elif is_full_review:
            section_key = "full_review"
        else:
            section_key = ""
        _exemplar_block = _load_cross_proposal_exemplar(self, proposal_id, section_key)
        if _exemplar_block:
            prompt += _exemplar_block

        # v6.8.22: 注入未解决 P0 列表（断裂点2）——writer 必须优先消除历史遗留 P0
        _p0_memory = self._build_p0_memory_text(proposal_id, exclude_resolved=False)
        if _p0_memory:
            prompt += (
                _p0_memory
                + "请将上述状态为'待解决'的历史遗留 P0 问题列为最高优先级处理：\n"
                + "  - 逐条分析各问题在当前申请书中的体现，针对性修改对应章节\n"
                + "  - 修改后请明确说明每个待解决问题的处理结果（已消除 / 已缓解 / 无法处理及原因）\n"
                + "即使该问题归属章节不是本轮聚焦章节，只要严重影响质量，也应一并修复。\n"
                + "状态为'已解决'的问题请保持现状，不要为了改而改导致质量回退。\n"
            )

        # v6.8.18: 注入 agent 分数反馈
        _writer_score_feedback = self._load_agent_score_feedback("writer")
        if _writer_score_feedback:
            prompt += _writer_score_feedback

        # v6.8.27: Writer 侧注入人工审核反馈（之前只有 critic 侧注入）
        # 避免 writer 重复犯人工审核已指出的问题
        _writer_human_feedback = self._load_human_feedback_block(proposal_id)
        if _writer_human_feedback:
            prompt += "\n\n## 历史人工审核反馈\n\n以下为人工审核曾指出的问题，请在本次修改中避免重蹈覆辙：\n" + _writer_human_feedback

        result = self._run_hermes("writer", prompt, timeout)

        # v6.7.7: writer 返回后，自动从 sections/ 重新组装 proposal-draft.md
        if result.get("success"):
            try:
                sections.assemble_draft()
                if _log:
                    _log.info(f"[{proposal_id}] 已从 sections/ 重新组装 proposal-draft.md")
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 组装 proposal-draft.md 失败: {e}")

        return result

    def _sync_derivative_artifacts(
        self,
        proposal_id: str,
        prop_dir: Path,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """v6.7.11: 根据最新申请书同步更新课题设想、方法学手册、文献阅读笔记。

        只在 full_review 轮调用，避免每轮都增加 hermes 开销。
        """
        research_idea_path = prop_dir / "00_research_idea.md"
        methodology_manual_path = prop_dir / "04_proposal" / "methodology-manual.md"
        reading_notes_path = prop_dir / "02_literature" / "reading-notes.md"
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"

        # 确保目录存在
        reading_notes_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取现有内容长度，判断是否跳过
        ri_len = len(research_idea_path.read_text(encoding="utf-8").strip()) if research_idea_path.exists() else 0
        mm_len = len(methodology_manual_path.read_text(encoding="utf-8").strip()) if methodology_manual_path.exists() else 0
        rn_len = len(reading_notes_path.read_text(encoding="utf-8").strip()) if reading_notes_path.exists() else 0

        # 如果课题设想已经比较完整（>2000字符）且方法学手册也完整（>5000字符），则跳过
        if ri_len > 2000 and mm_len > 5000:
            return {"success": True, "skipped": True, "reason": "课题设想和方法学手册已较完整"}

        prompt = (
            f"请根据最新申请书，同步更新以下三个配套文件。\n\n"
            f"【申请书】{proposal_path}\n"
            f"【现有课题设想】{research_idea_path}（当前 {ri_len} 字符）\n"
            f"【现有方法学手册】{methodology_manual_path}（当前 {mm_len} 字符）\n"
            f"【现有文献阅读笔记】{reading_notes_path}（当前 {rn_len} 字符）\n\n"
            f"更新要求：\n"
            f"1. {research_idea_path}：课题设想。包含标题、研究背景与动机、现存研究空白/瓶颈、拟开展研究内容和方案、拟采用技术路线、创新点。基于申请书提炼，不添加申请书中未出现的内容。\n"
            f"   **重要约束（v6.8.27）**：本次更新仅限同步申请书已有内容，"
            f"不允许新增科学目标或改变研究方向。如需方向性调整，应在报告中标注"
            f"'需要退回研究设想评审'，由系统触发 idea_review。\n"
            f"2. {methodology_manual_path}：方法学手册。重方法细节（公式推导/参数表/技术路线图/局限性/误差分析）。若已较完整，只补充申请书新增或调整部分对应的方法细节。\n"
            f"3. {reading_notes_path}：文献阅读笔记。若申请书引用了新文献而笔记中未记录，请按时间倒序追加一条记录，包含：阅读日期、文献标题、来源、核心结论、与课题关联、已引用位置。\n\n"
            f"请直接覆盖写入对应文件，不需要在 stdout 中输出全文。"
        )

        result = self._run_hermes("writer", prompt, timeout)
        return result

    def _run_hermes(self, profile: str, prompt: str, timeout: int) -> Dict[str, Any]:
        """执行 hermes oneshot。

        v6.8.3-fix9: 使用 Popen + 进程组杀死替代 subprocess.run，
        确保 timeout 后 hermes CLI 及其子进程被彻底清理。
        subprocess.run(timeout=N) 在 macOS 上只 kill 直接子进程，
        如果 hermes CLI fork 了额外进程（如 gateway worker），
        这些进程会继续运行导致 CLI 端口/管道不释放，Python 侧永远收不到子进程退出信号。
        """
        env = hermes_subprocess_env()

        import time
        import signal
        cmd = ["hermes", "--profile", profile, "-z", prompt]
        t0 = time.time()
        proc = None
        try:
            # start_new_session=True 使子进程成为新进程组的 leader
            # timeout 后可以用 os.killpg 杀死整个进程组
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=env, cwd=str(_pl.PROJECT_ROOT),
                start_new_session=True,
            )
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                # 杀死整个进程组（hermes CLI + 所有子进程）
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                        proc.wait(timeout=3)
                except (ProcessLookupError, PermissionError):
                    pass
                elapsed = round(time.time() - t0, 2)
                return {"success": False, "output": "", "error": f"超时({timeout}s)", "elapsed_s": elapsed}

            elapsed = round(time.time() - t0, 2)
            if proc.returncode == 0:
                output = stdout.strip()
                if len(output) > 50000:
                    output = output[:50000] + f"\n... (截断，共{len(output)}字符)"
                return {"success": True, "output": output, "elapsed_s": elapsed}
            return {
                "success": False, "output": stdout[:2000],
                "error": stderr[:500], "elapsed_s": elapsed,
            }
        except Exception as e:
            # 兜底：确保进程被清理
            if proc and proc.poll() is None:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    pass
            return {"success": False, "output": "", "error": str(e), "elapsed_s": 0}

    def _wait_for_critic_report(
        self,
        report_path: Path,
        timeout: int = 30,
        stable_interval: float = 1.0,
    ) -> bool:
        """等待 critic 报告文件生成并稳定。

        hermes critic profile 通过 agent loop 异步写盘，Python 进程返回时
        文件可能尚未生成或仍在写入。轮询等待文件存在且大小稳定。

        Args:
            report_path: 期望的 critic 报告路径
            timeout: 最大等待秒数
            stable_interval: 连续两次大小不变的间隔秒数

        Returns:
            True 表示文件已生成且稳定；False 表示超时
        """
        import time
        deadline = time.time() + timeout
        last_size = -1
        stable_since = None

        while time.time() < deadline:
            if report_path.exists():
                try:
                    current_size = report_path.stat().st_size
                except Exception:
                    current_size = -1
                if current_size > 100 and current_size == last_size:
                    if stable_since is None:
                        stable_since = time.time()
                    elif time.time() - stable_since >= stable_interval:
                        return True
                else:
                    stable_since = None
                last_size = current_size
            time.sleep(0.5)

        return False

    def _extract_score(self, critic_result: Dict[str, Any]) -> float:
        """从 critic 输出中提取综合评分。"""
        output = critic_result.get("output", "")
        import re
        # 优先匹配 "综合评分：0.85" / "综合分 0.85"（v6.6.3：兼容 GLM-5.2 的简化输出）
        patterns = [
            r"综合评分[：:]\s*(0\.\d+)",
            r"综合分[：:]?\s*(0\.\d+)",
            r"overall[\s_]*score[：:\s]+(0\.\d+)",
            r"score[：:]\s*(0\.\d+)",
            r"评分[：:]\s*(0\.\d+)",
            r"(0\.\d+)\s*/\s*1(?:\.0+)?\b",  # 0.07 / 1 或 0.07 / 1.00
        ]
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return float(match.group(1))

        # 回退：如果有维度分数，取加权平均
        dims = self._extract_dimension_scores(critic_result)
        if dims:
            weights = {"innovation": 0.30, "feasibility": 0.25, "rigor": 0.25, "expression": 0.20}
            total = sum(dims.get(k, 0) * w for k, w in weights.items())
            return round(total, 4)
        return 0.0

    # 维度中英文映射
    _DIM_MAP = {
        "创新性": "innovation", "创新": "innovation", "innovation": "innovation",
        "可行性": "feasibility", "feasibility": "feasibility",
        "严谨性": "rigor", "rigor": "rigor",
        "表达质量": "expression", "expression": "expression", "表达": "expression",
        "完整性": "completeness", "completeness": "completeness",
    }
    # 各维度短板阈值（低于此值视为短板）
    # v6.8.3: 提升阈值，避免偏科通过（原 0.65/0.60 → 0.70/0.65）
    DIMENSION_FLOOR = {"innovation": 0.70, "feasibility": 0.70, "rigor": 0.70, "expression": 0.70, "completeness": 0.65}

    def _extract_dimension_scores(self, critic_result: Dict[str, Any]) -> Dict[str, float]:
        """从 critic 输出中提取 4 维度分数（P0-2）。

        兼容 v6.6.3 GLM-5.2 输出格式：
        - `| 创新性（innovation） | 0.05 |` （markdown 表格 + 括号别名）
        - `| 创新性（innovation） | 0.30 | 0.78 |` （markdown 表格含权重列，得分列在最后）
        - `创新性：0.85` / `创新性 0.85` / `创新性（innovation） 0.85`

        v6.8.9 修复：表格行若含权重列（如 `| 维度 | 权重 | 得分 |`），
        原实现的正则会误匹配到权重列（第一个数字）。现改为取表格行内
        最后一个数字作为得分列。

        Returns:
            {innovation, feasibility, rigor, completeness}
        """
        output = critic_result.get("output", "")
        import re
        dims: Dict[str, float] = {}
        # 收集所有"维度名+分数"对（去重，每个维度只取第一个匹配）
        for cn_name, en_key in self._DIM_MAP.items():
            if en_key in dims:
                continue
            score = None
            # 模式1：markdown 表格行。兼容 `| 维度 | 得分 |` 与 `| 维度 | 权重 | 得分 |`，
            # 分数总在行内最后一个数字列，故取该行最后一个 0.x 数字。
            table_m = re.search(
                rf"\|\s*{cn_name}[（(]?{en_key}[）)]?\s*\|[^|\n]*(\|[^|\n]*)*\|",
                output, re.IGNORECASE,
            )
            if table_m:
                # v6.8.9 修复：取表格行内"最后一个独立纯数字单元格"作为得分列。
                # 批评报告维度表格式为 `| 维度 | 权重 | 得分 | 档位 | 主要短板 |`，
                # 档位/主要短板评语中可能含数字（如 "U/W ~ 0.5"、"已扣 ceiling 0.05"、
                # "17.4%"），若直接取行内最后一个 0.x 会误读到评语中的数字。
                # 得分列总是独立成格的纯数字，故取最后一个匹配 `0.xx` 的单元格。
                cells = table_m.group(0).strip().split("|")
                pure_nums = [
                    float(c.strip()) for c in cells
                    if re.fullmatch(r"\s*0\.\d+\s*", c)
                ]
                if pure_nums:
                    score = pure_nums[-1]
            # 模式2：行内格式（表格未命中时兜底）
            if score is None:
                for pat in [
                    rf"{cn_name}[（(]{en_key}[）)]\s*[：:|]?\s*(0\.\d+)",   # 创新性（innovation） 0.05
                    rf"{cn_name}[：:]\s*(0\.\d+)",                            # 创新性：0.05
                    rf"{cn_name}\s+(0\.\d+)",                                 # 创新性 0.05
                ]:
                    m = re.search(pat, output, re.IGNORECASE)
                    if m:
                        score = float(m.group(1))
                        break
            if score is not None:
                dims[en_key] = score
        return dims

    def _get_weakest_dimension(self, dims: Dict[str, float]) -> str:
        """找出最弱的维度（P0-2，供 writer 聚焦改进）。"""
        if not dims:
            return ""
        return min(dims, key=dims.get)

    def _recalculate_score(self, dim_scores: Dict[str, float], project_type: str) -> float:
        """v6.8.7: 根据维度分数和项目类型权重重新计算综合分。"""
        standards = load_json(self.standards_path, default={})
        types = standards.get("project_types", {})
        weights_map = types.get(project_type, {}).get("evaluation_focus", {})
        # 映射中文权重名到英文 key
        weight_mapping = {
            "创新性权重": "innovation", "可行性权重": "feasibility",
            "严谨性权重": "rigor", "表达质量权重": "expression",
            "系统性权重": "systematic", "战略意义权重": "strategic",
            "完整性权重": "completeness",
        }
        if not weights_map:
            # 默认面上权重
            weights_map = {"创新性权重": 0.30, "可行性权重": 0.25, "严谨性权重": 0.25, "表达质量权重": 0.20}

        total_weight = 0.0
        weighted_sum = 0.0
        for cn_weight_key, en_dim_key in weight_mapping.items():
            w = weights_map.get(cn_weight_key, 0)
            if w > 0 and en_dim_key in dim_scores:
                weighted_sum += dim_scores[en_dim_key] * w
                total_weight += w

        if total_weight > 0:
            return round(weighted_sum / total_weight, 4)
        # 回退：简单平均
        return round(sum(dim_scores.values()) / max(len(dim_scores), 1), 4)

    def _extract_issues(self, critic_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从 critic 输出中提取问题列表（简化版，只提取严重程度）。"""
        output = critic_result.get("output", "")
        issues = []
        for line in output.split("\n"):
            for sev in ["critical", "high", "medium", "low"]:
                if f"[{sev}]" in line or f"（{sev}）" in line:
                    issues.append({"severity": sev, "line": line.strip()[:100]})
        return issues


# ---------------------------------------------------------------------------
# v6.8.22: P0 跨轮持久化（断裂点3、1、2、4 的数据基础）
# ---------------------------------------------------------------------------

    def _update_open_critical_issues(
        self,
        proposal_id: str,
        new_issues: List[Dict[str, Any]],
        current_round: int,
        focus_section_key: str,
    ) -> List[Dict[str, Any]]:
        """更新 proposal 的 open_critical_issues 列表（跨轮 P0 记忆）。

        逻辑：
        1. 仅吸纳 critical/high 级问题（P0/P1 级），medium/low 不入库。
        2. 去重：同 section + 同 severity + 描述相似度>0.8 视为同一问题，只更新最新轮次。
        3. 已存在但本轮 critic 报告中未再出现的问题 → 尝试标记为已解决（round_resolved）。
        4. 超过 MAX_P0_TRACK_ROUNDS 轮仍未被复现也未标记解决的问题 → 降级为 stale（保留记录）。
        5. 返回更新后的 open_critical_issues 列表。
        """
        MAX_P0_TRACK_ROUNDS = 10
        prop_state = self._get_proposal_state(proposal_id)
        if prop_state is None:
            return []
        open_list = prop_state.get("open_critical_issues", [])
        if not isinstance(open_list, list):
            open_list = []

        # 本轮 critic 报告的 section 归属
        section_key = focus_section_key or "full_review"

        # 1) 收集本轮出现的 critical/high 问题签名
        current_sigs = set()
        current_entries = []
        for issue in (new_issues or []):
            sev = issue.get("severity", "").lower()
            if sev not in ("critical", "high"):
                continue  # 只跟踪 P0/P1 级
            desc = (issue.get("line") or issue.get("description") or "").strip()
            if not desc:
                continue
            sim_key = self._issue_similarity_key(desc)
            sig = (section_key, sev, sim_key)
            current_sigs.add(sig)
            current_entries.append({
                "severity": sev,
                "section": section_key,
                "description": desc[:300],
                "first_seen_round": current_round,
                "last_seen_round": current_round,
                "round_resolved": None,
                "stale": False,
            })

        # 2) 合并：保留历史 + 更新 last_seen / 标记解决
        seen_this_round = set()
        merged = []
        for entry in open_list:
            if not isinstance(entry, dict):
                continue
            sig = (entry.get("section", ""), (entry.get("severity") or "").lower(), self._issue_similarity_key(entry.get("description", "")))
            if sig in current_sigs:
                # 本轮仍出现 → 更新 last_seen，清除 resolved（若曾被误标记）
                entry["last_seen_round"] = current_round
                entry["round_resolved"] = None
                entry["stale"] = False
                seen_this_round.add(sig)
            elif entry.get("round_resolved") is None and not entry.get("stale"):
                # 历史未解决问题，本轮未复现 → 视为已解决
                entry["round_resolved"] = current_round
            merged.append(entry)

        # 3) 加入本轮新出现、且历史不存在的问题
        for entry in current_entries:
            sig = (entry["section"], entry["severity"], self._issue_similarity_key(entry["description"]))
            if sig not in seen_this_round:
                merged.append(entry)
                seen_this_round.add(sig)

        # 4) 超长滞留未复现且已标记解决的，超过 MAX_P0_TRACK_ROUNDS 轮未复现 → stale 降级
        for entry in merged:
            if entry.get("stale"):
                continue
            resolved = entry.get("round_resolved")
            if resolved is not None and (current_round - resolved) > MAX_P0_TRACK_ROUNDS:
                entry["stale"] = True

        # 5) 列表上限保护（最近 40 条，按 last_seen_round 降序保留）
        merged.sort(key=lambda e: e.get("last_seen_round", 0), reverse=True)
        merged = merged[:40]

        prop_state["open_critical_issues"] = merged
        self._set_proposal_state(proposal_id, prop_state)
        return merged

    def _issue_similarity_key(self, description: str) -> str:
        """生成问题描述的可比对相似键：取前 30 个字符，去掉空白与标点，小写。

        用于跨轮去重——同一问题在不同轮次的措辞略有差异时仍能识别为同一问题。
        """
        import re
        if not description:
            return ""
        norm = re.sub(r"[\s，。；：、,.!?！？;:'\"“”‘’（）()\[\]【】\-—]", "", description.lower())
        return norm[:30]

    def _load_open_critical_issues(self, proposal_id: str) -> List[Dict[str, Any]]:
        """读取指定 proposal 的 open_critical_issues 列表（供 prompt 注入）。"""
        prop_state = self._get_proposal_state(proposal_id)
        if prop_state is None:
            return []
        open_list = prop_state.get("open_critical_issues", [])
        return [e for e in (open_list or []) if isinstance(e, dict)]

    def _build_p0_memory_text(self, proposal_id: str, exclude_resolved: bool = True) -> str:
        """构建注入 critic/writer prompt 的历史 P0 记忆文本。

        exclude_resolved=True（critic 用）：只列出仍未解决（round_resolved is None）的 P0。
        exclude_resolved=False（writer 用）：列出全部未解决 + 最近已解决的问题。
        """
        entries = self._load_open_critical_issues(proposal_id)
        if not entries:
            return ""

        unresolved = [e for e in entries if e.get("round_resolved") is None and not e.get("stale")]
        if exclude_resolved:
            target = unresolved
        else:
            # writer 需要看到未解决 + 最近 3 条已解决（防止反复横跳）
            resolved = sorted(
                [e for e in entries if e.get("round_resolved") is not None],
                key=lambda e: e.get("round_resolved", 0), reverse=True,
            )[:3]
            target = unresolved + resolved

        if not target:
            return ""

        sev_cn = {"critical": "严重(P0)", "high": "较高(P1)"}
        lines = []
        for e in target:
            sev = (e.get("severity") or "high").lower()
            if e.get("round_resolved") is None:
                status = f"待解决（首见于 R{e.get('first_seen_round')}）"
            else:
                status = f"已解决（R{e.get('round_resolved')} 起未复现）"
            lines.append(
                f"- [{sev_cn.get(sev, sev)}] 归属章节={e.get('section','?')} 状态={status} "
                f"问题：{e.get('description','')[:120]}"
            )
        block = "\n".join(lines)
        return (
            f"\n\n【历史遗留问题记忆（跨轮持久化，必须逐条核对）】\n"
            f"以下问题是此前多轮对抗评审中反复/遗留的 P0 级问题，请务必处理：\n"
            f"{block}\n"
        )


# ---------------------------------------------------------------------------
# v6.8.17: cross-proposal 范例注入
# ---------------------------------------------------------------------------

def _load_cross_proposal_exemplar(lifecycle_obj, current_proposal_id: str, section_key: str) -> str:
    """从最高分课题中提取范例段落，注入到低分课题的 writer prompt。

    v6.8.24 修复：旧版用 last_score + 阈值 0.80 → 所有课题从未达到 → 死代码。
    改为：用历史峰值分数（score_history 中的最大值），阈值降至 0.70，
    扫描 optimizing/ 和 pending_review/ 目录。

    v6.8.25 修复：旧版扫描各课题目录下的独立 _lifecycle.json，但实际所有状态
    存储在全局 research_proposals/_lifecycle.json 中，各课题目录无此文件 →
    函数永远跳过所有课题 → 完全失效。改为从全局状态文件读取。
    """
    try:
        from proposal_lifecycle.constants import PROPOSALS_ROOT

        # 找到当前课题的分数
        current_state = lifecycle_obj._get_proposal_state(current_proposal_id)
        current_score = current_state.get("last_score", 0.0) if current_state else 0.0
        if current_score >= 0.75:
            return ""  # 当前课题已足够好，不需要范例

        # v6.8.24: 从 score_history 取历史峰值，而非 last_score
        def _best_score_from_state(state: dict) -> float:
            """从 proposal state 中提取历史最高分。"""
            last = state.get("last_score", 0.0)
            history = state.get("score_history", [])
            if not history:
                return last
            peak = max((h.get("score", 0) for h in history if isinstance(h, dict)), default=0)
            return max(last, peak)

        # v6.8.25: 从全局 _lifecycle.json 读取所有课题状态，而非各课题目录下的独立文件
        global_state = lifecycle_obj._load_state()
        all_proposals = global_state.get("proposals", {})

        best_proposal = None
        best_score = 0.70  # v6.8.24: 门槛从 0.80 降至 0.70（实际可达到的水平）
        best_status = None
        for pid, pstate in all_proposals.items():
            if pid == current_proposal_id:
                continue
            # v6.8.25: 只从 optimizing 和 pending_review 状态的课题中选范例
            p_status = pstate.get("status", "")
            if p_status not in ("optimizing", "pending_review"):
                continue
            score = _best_score_from_state(pstate)
            if score > best_score:
                best_score = score
                best_proposal = pid
                best_status = p_status

        if not best_proposal or not best_status:
            return ""

        # 提取范例课题的对应章节
        section_file_map = {
            "rationale": "rationale.md",
            "content": "content.md",
            "scheme": "scheme.md",
        }
        section_file = section_file_map.get(section_key)
        if not section_file:
            return ""

        exemplar_path = PROPOSALS_ROOT / best_status / best_proposal / "04_proposal" / "sections" / section_file
        if not exemplar_path.exists():
            return ""

        text = exemplar_path.read_text(encoding="utf-8")
        # 取前 2000 字符作为范例（足够展示写作风格，不会太长）
        exemplar_text = text[:2000]

        return (
            f"\n\n【参考范文（来自评分 {best_score:.2f} 的高质量课题，仅供学习写作风格和论证密度）】\n"
            f"来源课题：{best_proposal}\n"
            f"章节：{section_file}\n"
            f"---\n{exemplar_text}\n---\n"
            f"请在本次修改中参考上述范文的论证密度、行文连贯性和具体性，"
            f"但不要照抄内容（研究领域不同）。\n"
        )
    except Exception:
        return ""
