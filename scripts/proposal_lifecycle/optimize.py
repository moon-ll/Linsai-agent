from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import subprocess

from common import now_utc, load_json, hermes_subprocess_env

import proposal_lifecycle as _pl

from proposal_sections import ProposalSections, PROPOSAL_SECTIONS

from proposal_lifecycle.constants import (
    _log,
    DEFAULT_MAX_ROUNDS,
    DEFAULT_SCORE_THRESHOLD,
)


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
        section_cycle = current_round % (len(PROPOSAL_SECTIONS) + 1)
        if section_cycle < len(PROPOSAL_SECTIONS):
            focus_section = PROPOSAL_SECTIONS[section_cycle]
            is_full_review = False
        else:
            focus_section = None  # 第4轮做整体一致性审查
            is_full_review = True

        # 读取当前申请书
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        if not proposal_path.exists():
            return {"success": False, "error": "申请书不存在，请先执行管线生成初稿"}

        score_before = prop_state.get("last_score", 0.0)

        # 1. critic 评审
        if _log:
            section_name = focus_section["cn"] if focus_section else "整体一致性"
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: critic 评审（聚焦：{section_name}）")
        critic_result = self._run_critic(
            proposal_id, prop_dir, project_type, current_round + 1, critic_timeout,
            focus_section=focus_section, is_full_review=is_full_review,  # P1-1
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
                timeout=300,
            )

        # 2. writer 根据评审意见优化
        if _log:
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: writer 优化")
        writer_result = self._run_writer_optimize(
            proposal_id, prop_dir, project_type, critic_result, writer_timeout,
            weakest_dim=pre_weakest, dim_scores=pre_dims,  # P0-2
            focus_section=focus_section, is_full_review=is_full_review,  # P1-1
            lit_supplement=lit_supplement,  # P1-2
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

        # P1-1: 确定本轮模块 key
        section_key = focus_section["key"] if focus_section else "full_review"

        # P1-3: 判断该模块是否"对抗胜利"（分数达标 + 各维度无短板）
        min_score = threshold.get("min_overall_score", DEFAULT_SCORE_THRESHOLD)
        weak_dims = [
            k for k, floor in self.DIMENSION_FLOOR.items()
            if k in dim_scores and dim_scores[k] < floor
        ]
        section_passed = score_after >= min_score and len(weak_dims) == 0

        # 4. 更新状态
        # v6.7.1：_set_proposal_state 内部已加 file_lock("proposal-lifecycle")，
        # 不再外层包 file_lock(f"proposal-{proposal_id}")，避免嵌套锁和潜在竞态
        prop_state = self._get_proposal_state(proposal_id)
        prop_state["optimization_rounds"] = current_round + 1
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

    def _run_critic(
        self,
        proposal_id: str,
        prop_dir: Path,
        project_type: str,
        round_num: int,
        timeout: int,
        focus_section: Optional[Dict[str, str]] = None,
        is_full_review: bool = False,
    ) -> Dict[str, Any]:
        """派活给 critic profile 做对抗评审。

        P1-1: 支持章节级评审（focus_section）和整体审查（is_full_review）。
        v6.7.7: 默认按章节拆分文件读取，降低单次 LLM 负载、减少超时。
        """
        sections = ProposalSections(prop_dir)
        sections.ensure_split()  # 兼容旧格式：自动拆分
        standards_path = str(self.standards_path.relative_to(_pl.PROJECT_ROOT))
        report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # v6.7.7: 构建要读取的文件列表
        if is_full_review:
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

        prompt = (
            f"请对以下 NSFC 申请书做第 {round_num} 轮对抗评审。\n\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path} 中 project_types.{project_type} 的标准\n\n"
            f"{read_instruction}"
            f"{focus_text}"
            f"请执行：\n"
            f"1. 读取指定的申请书文件（章节级评审只读聚焦章节，整体审查读全部章节）\n"
            f"2. 读取质量标准配置文件\n"
            f"3. 按项目类型标准做红队评审，尽可能找出问题\n"
            f"4. 每个问题给出具体、可执行的修改建议\n"
            f"5. 按严重程度分级（critical/high/medium/low）\n\n"
            f"【多维度评分（必填）】\n"
            f"请从以下 4 个维度分别评分（0-1），并指出每个维度的主要短板：\n"
            f"  - 创新性（innovation）：科学问题是否新颖、方法是否有突破\n"
            f"  - 可行性（feasibility）：技术路线能否落地、是否有支撑\n"
            f"  - 严谨性（rigor）：逻辑链条、文献支撑是否充分\n"
            f"  - 完整性（completeness）：章节是否齐全、格式是否规范\n\n"
            f"在评审报告末尾，必须包含如下格式的评分块（供程序解析）：\n"
            f"```\n"
            f"## 评分\n"
            f"创新性：0.85\n"
            f"可行性：0.80\n"
            f"严谨性：0.75\n"
            f"完整性：0.90\n"
            f"综合评分：0.82\n"
            f"```\n"
            f"将评审报告写入：{report_path}\n"
        )

        return self._run_hermes("critic", prompt, timeout)

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
        """v6.7.7: 根据 gap analysis 执行定向文献检索。

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

        prompt = (
            f"请根据文献缺口分析，执行定向文献检索。\n\n"
            f"【课题】{proposal_id}\n"
            f"{section_hint}"
            f"【文献缺口分析文件】{gap_path}\n"
            f"【输出文件】{result_path}\n\n"
            f"请执行：\n"
            f"1. 读取 {gap_path} 中的 JSON 缺口列表\n"
            f"2. 针对每个 high/medium 优先级缺口，检索 2-3 篇最相关的近2年论文\n"
            f"3. 每篇论文给出：标题、作者、年份、期刊/arXiv、核心结论、如何支撑该论点\n"
            f"4. 将检索结果写入 {result_path}，格式：每个缺口一段，列出推荐引用论文\n"
        )

        result = self._run_hermes("researcher", prompt, timeout)
        if result.get("success") and result_path.exists():
            if _log:
                _log.info(f"[{proposal_id}] 文献检索完成: {result_path.name}")
            return result_path
        else:
            if _log:
                _log.warning(f"[{proposal_id}] 文献检索失败: {result.get('error', '')[:100]}")
            return None

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
        # 第一步：识别缺口（轻量，默认 120s）
        gap_path = self._run_gap_identifier(
            proposal_id, prop_dir, critic_result, focus_section, timeout=120
        )
        if not gap_path:
            return ""

        # 第二步：执行检索（重量，剩余超时）
        result_path = self._run_literature_searcher(
            proposal_id, prop_dir, gap_path, focus_section, timeout=max(timeout - 120, 180)
        )
        if result_path:
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
    ) -> Dict[str, Any]:
        """派活给 writer profile 根据评审意见优化申请书。

        P0-2: 聚焦最弱维度，针对性改进。
        P1-1: 支持章节级修订（focus_section）。
        v6.7.7: 章节级修订只写入对应 section 文件，再自动组装 proposal-draft.md。
        """
        sections = ProposalSections(prop_dir)
        sections.ensure_split()
        standards_path = str(self.standards_path.relative_to(_pl.PROJECT_ROOT))
        # 找最新的 critic 报告
        review_dir = prop_dir / "05_review"
        critic_reports = sorted(review_dir.glob("critic-round-*.md"), reverse=True)
        latest_critic = str(critic_reports[0]) if critic_reports else ""

        # P0-2: 构建维度聚焦提示
        dim_focus = ""
        if weakest_dim and dim_scores:
            dim_cn = {"innovation": "创新性", "feasibility": "可行性", "rigor": "严谨性", "completeness": "完整性"}
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

        if focus_section:
            target_section_file = prop_dir / "04_proposal" / "sections" / f"{focus_section['key']}.md"
            section_focus = (
                f"\n【本轮聚焦章节】{focus_section['title']}\n"
                f"请只修改该章节文件：{target_section_file}\n"
                f"不要修改其他章节文件。\n"
                f"修改完成后，将优化后的完整章节内容覆盖写入 {target_section_file}\n"
                f"系统会自动根据章节文件重新组装 proposal-draft.md。\n"
            )
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

        prompt = (
            f"请根据对抗评审意见优化申请书。\n\n"
            f"【主读取文件】{primary_read}\n"
            f"【所有章节文件】\n" +
            "\n".join(f"- {p}" for p in section_files) + "\n\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path}\n"
            f"【评审报告】{latest_critic}\n"
            f"{dim_focus}"
            f"{section_focus}"
            f"{lit_supplement}\n"
            f"请执行：\n"
            f"1. 读取主读取文件（章节级修订只读聚焦章节，整体修订可读全部章节）\n"
            f"2. 读取评审报告中的所有问题\n"
            f"3. 逐条解决每个问题（按严重程度优先）\n"
            f"4. 重点改进最弱维度相关的问题\n"
            f"5. 只修改聚焦章节文件（或整体衔接涉及的章节文件），保持其他章节不变（增量优化）\n"
            f"6. 将优化后的内容覆盖写入对应章节 .md 文件（不是 proposal-draft.md）\n"
            f"7. 同步更新方法学手册：{prop_dir}/04_proposal/methodology-manual.md\n"
            f"   （申请书重思路，方法学手册重细节：公式推导/参数表/技术路线图）\n"
            f"   ⚠️ 方法学手册也按章节组织，只更新与聚焦章节对应的细节部分。\n"
        )

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

    def _run_hermes(self, profile: str, prompt: str, timeout: int) -> Dict[str, Any]:
        """执行 hermes oneshot。"""
        # v6.6.3 + v6.7.7 修复：清理 Python 变量 + 自动读取 .env + 透传 ZAI_API_KEY，
        # 避免 cron 等无 shell 环境因缺少 API Key 而失败
        env = hermes_subprocess_env()

        import time
        cmd = ["hermes", "--profile", profile, "-z", prompt]
        t0 = time.time()
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                env=env, cwd=str(_pl.PROJECT_ROOT),
            )
            elapsed = round(time.time() - t0, 2)
            if result.returncode == 0:
                output = result.stdout.strip()
                # v6.7.1: 提高截断阈值，避免 critic 评分代码块被截断
                # critic 报告通常 10-25KB，50KB 可保留完整评分
                if len(output) > 50000:
                    output = output[:50000] + f"\n... (截断，共{len(output)}字符)"
                return {"success": True, "output": output, "elapsed_s": elapsed}
            return {
                "success": False, "output": result.stdout[:2000],
                "error": result.stderr[:500], "elapsed_s": elapsed,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": f"超时({timeout}s)", "elapsed_s": timeout}
        except Exception as e:
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
            weights = {"innovation": 0.30, "feasibility": 0.25, "rigor": 0.25, "completeness": 0.20}
            total = sum(dims.get(k, 0) * w for k, w in weights.items())
            return round(total, 4)
        return 0.0

    # 维度中英文映射
    _DIM_MAP = {
        "创新性": "innovation", "创新": "innovation", "innovation": "innovation",
        "可行性": "feasibility", "feasibility": "feasibility",
        "严谨性": "rigor", "rigor": "rigor",
        "完整性": "completeness", "completeness": "completeness",
    }
    # 各维度短板阈值（低于此值视为短板）
    DIMENSION_FLOOR = {"innovation": 0.65, "feasibility": 0.65, "rigor": 0.65, "completeness": 0.60}

    def _extract_dimension_scores(self, critic_result: Dict[str, Any]) -> Dict[str, float]:
        """从 critic 输出中提取 4 维度分数（P0-2）。

        兼容 v6.6.3 GLM-5.2 输出格式：
        - `| 创新性（innovation） | 0.05 |` （markdown 表格 + 括号别名）
        - `创新性：0.85` / `创新性 0.85` / `创新性（innovation） 0.85`
        - 表格对齐：`| 创新性（innovation） | 0.05 | 主要短板 |`

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
            # 多种格式：行内/表格都支持
            patterns = [
                rf"\|\s*{cn_name}[（(]?{en_key}[）)]?\s*\|\s*(0\.\d+)",  # | 创新性（innovation） | 0.05 |
                rf"{cn_name}[（(]{en_key}[）)]\s*[：:|]?\s*(0\.\d+)",   # 创新性（innovation） 0.05
                rf"{cn_name}[：:]\s*(0\.\d+)",                            # 创新性：0.05
                rf"{cn_name}\s+(0\.\d+)",                                 # 创新性 0.05
            ]
            for pat in patterns:
                m = re.search(pat, output, re.IGNORECASE)
                if m:
                    dims[en_key] = float(m.group(1))
                    break
        return dims

    def _get_weakest_dimension(self, dims: Dict[str, float]) -> str:
        """找出最弱的维度（P0-2，供 writer 聚焦改进）。"""
        if not dims:
            return ""
        return min(dims, key=dims.get)

    def _extract_issues(self, critic_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从 critic 输出中提取问题列表（简化版，只提取严重程度）。"""
        output = critic_result.get("output", "")
        issues = []
        for line in output.split("\n"):
            for sev in ["critical", "high", "medium", "low"]:
                if f"[{sev}]" in line or f"（{sev}）" in line:
                    issues.append({"severity": sev, "line": line.strip()[:100]})
        return issues
