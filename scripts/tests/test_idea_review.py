#!/usr/bin/env python3
"""
test_idea_review.py — 研究设想质量门槛（idea_review）单元测试（v6.8.26）

覆盖：
    - round 1 前置 idea_review job 生成
    - round 2 不生成 idea_review（无结构性缺陷时）
    - idea_review 作为 critic 前置依赖
    - _parse_idea_review_score 评分解析
    - _detect_structural_defect 结构性缺陷检测
    - idea_review_required 标志触发退回
    - 阈值常量正确性

注意：
    本测试不调用 hermes/LLM，仅验证状态机和解析逻辑。
"""

import sys
import shutil
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT
import importlib


class IdeaReviewTests(TestSuite):
    def __init__(self):
        super().__init__("研究设想质量门槛测试")
        self.tmp_root = None
        self.pl = None
        self.ctrl = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "research_proposals").mkdir(parents=True, exist_ok=True)
        for subdir in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / subdir).mkdir(exist_ok=True)

        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")

        for mod_name in ["proposal_lifecycle", "lifecycle_cron_framework"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        self.pl = importlib.import_module("proposal_lifecycle")
        self.ctrl = importlib.import_module("lifecycle_cron_framework")

        patch_module_root("proposal_lifecycle", self.tmp_root)
        patch_module_root("lifecycle_cron_framework", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_controller(self):
        return self.ctrl.LifecycleCronController()

    def _register_proposal(self, controller, pid, status="optimizing"):
        controller.register(pid, project_type="general")
        if status != "drafts":
            controller.transition(pid, status)
        prop_dir = controller.root / status / pid
        prop_dir.mkdir(parents=True, exist_ok=True)
        (prop_dir / "00_proposal-brief.md").write_text(f"# {pid}\n\ntest", encoding="utf-8")
        (prop_dir / "04_proposal").mkdir(exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text("# draft\n", encoding="utf-8")

    # ── 测试用例 ──

    def _test_round1_has_idea_review(self):
        """round 1 的 job 链应包含 idea_review 作为第一个 job。"""
        c = self._make_controller()
        pid = "general-idea-r1-20260101"
        self._register_proposal(c, pid)
        c.sync_checkpoint(pid)

        jobs = c._get_jobs(pid)
        idea_jobs = [j for j in jobs if j["step"] == "idea_review"]
        self.assert_eq(len(idea_jobs), 1, "round 1 包含 1 个 idea_review job")
        self.assert_eq(idea_jobs[0]["section_key"], "idea_review", "idea_review section_key")
        self.assert_eq(len(idea_jobs[0]["depends_on"]), 0, "idea_review 无前置依赖")

        # idea_review 是第一个 job（在所有 critic 之前）
        self.assert_eq(jobs[0]["step"], "idea_review", "第一个 job 是 idea_review")

    def _test_round2_no_idea_review(self):
        """round 2 无结构性缺陷时不应生成 idea_review。"""
        c = self._make_controller()
        pid = "general-idea-r2-20260102"
        self._register_proposal(c, pid)

        # 模拟 round 1 已完成
        prop_state = c._get_proposal_state(pid)
        prop_state["optimization_rounds"] = 1
        c._set_proposal_state(pid, prop_state)

        c.sync_checkpoint(pid)
        jobs = c._get_jobs(pid)
        idea_jobs = [j for j in jobs if j["step"] == "idea_review"]
        self.assert_eq(len(idea_jobs), 0, "round 2 无结构性缺陷时不生成 idea_review")

    def _test_round2_with_defect_triggers_idea_review(self):
        """round 2 有结构性缺陷标志时应重新生成 idea_review。"""
        c = self._make_controller()
        pid = "general-idea-defect-20260103"
        self._register_proposal(c, pid)

        # 模拟 round 1 已完成 + 结构性缺陷标志
        prop_state = c._get_proposal_state(pid)
        prop_state["optimization_rounds"] = 1
        prop_state["idea_review_required"] = True
        c._set_proposal_state(pid, prop_state)

        c.sync_checkpoint(pid)
        jobs = c._get_jobs(pid)
        idea_jobs = [j for j in jobs if j["step"] == "idea_review"]
        self.assert_eq(len(idea_jobs), 1, "round 2 有缺陷标志时生成 idea_review")

        # 标志应被清除
        prop_state = c._get_proposal_state(pid)
        self.assert_eq(prop_state.get("idea_review_required"), False, "idea_review_required 标志被清除")

    def _test_critic_depends_on_idea_review(self):
        """round 1 的 rationale critic 应依赖 idea_review。"""
        c = self._make_controller()
        pid = "general-idea-dep-20260104"
        self._register_proposal(c, pid)
        c.sync_checkpoint(pid)

        jobs = c._get_jobs(pid)
        rationale_critic = next(
            j for j in jobs
            if j["section_key"] == "rationale" and j["step"] == "critic"
        )
        idea_review_id = f"{pid}-r1-idea_review-idea_review"
        self.assert_in(idea_review_id, rationale_critic["depends_on"],
                       "rationale critic 依赖 idea_review")

    def _test_parse_score(self):
        """_parse_idea_review_score 应正确解析评审报告中的分数。"""
        from lifecycle.executor import _parse_idea_review_score

        report = """
## 评审报告

科学问题清晰度：0.75
创新点可检验性：0.70
内容方案切分：0.65
方向一致性：0.80

## 评分
科学问题清晰度：0.75
创新点可检验性：0.70
内容方案切分：0.65
方向一致性：0.80
综合评分：0.73
"""
        score, issues = _parse_idea_review_score(report)
        self.assert_eq(score, 0.73, "综合评分解析为 0.73")

    def _test_parse_score_fallback(self):
        """无综合评分时应取维度分数均值。"""
        from lifecycle.executor import _parse_idea_review_score

        report = """
科学问题清晰度：0.80
创新点可检验性：0.60
内容方案切分：0.70
方向一致性：0.90
"""
        score, issues = _parse_idea_review_score(report)
        # 4 个维度均值：(0.80 + 0.60 + 0.70 + 0.90) / 4 = 0.75
        self.assert_eq(score, 0.75, "无综合评分时取维度均值 0.75")

    def _test_detect_defect_empty(self):
        """无缺陷时应返回空字符串。"""
        from lifecycle.executor import _detect_structural_defect

        tmp = Path(self.tmp_root / "test_defect_empty")
        sections = tmp / "04_proposal" / "sections"
        sections.mkdir(parents=True, exist_ok=True)
        (sections / "content.md").write_text("A" * 500, encoding="utf-8")
        (sections / "scheme.md").write_text("B" * 500, encoding="utf-8")

        result = _detect_structural_defect(tmp)
        self.assert_eq(result, "", "无缺陷返回空字符串")

    def _test_detect_defect_vacancy(self):
        """模块空置应被检测到。"""
        from lifecycle.executor import _detect_structural_defect

        tmp = Path(self.tmp_root / "test_defect_vacancy")
        sections = tmp / "04_proposal" / "sections"
        sections.mkdir(parents=True, exist_ok=True)
        (sections / "content.md").write_text("A" * 500, encoding="utf-8")
        (sections / "scheme.md").write_text("短", encoding="utf-8")  # 不足 50 字节

        result = _detect_structural_defect(tmp)
        self.assert_true("空置" in result, "检测到模块空置", result)

    def _test_detect_defect_overlap(self):
        """文件级重复应被检测到。"""
        from lifecycle.executor import _detect_structural_defect

        tmp = Path(self.tmp_root / "test_defect_overlap")
        sections = tmp / "04_proposal" / "sections"
        sections.mkdir(parents=True, exist_ok=True)
        overlap_text = "这是一段完全相同的内容，用于测试文件级重复检测功能。" * 10
        (sections / "content.md").write_text(overlap_text + "content unique", encoding="utf-8")
        (sections / "scheme.md").write_text(overlap_text + "scheme unique", encoding="utf-8")

        result = _detect_structural_defect(tmp)
        self.assert_true("重复" in result, "检测到文件级重复", result)

    def _test_constants(self):
        """常量值应正确。"""
        from lifecycle.constants import (
            STEP_IDEA_REVIEW,
            IDEA_REVIEW_THRESHOLD,
            MAX_IDEA_REVIEW_ATTEMPTS,
        )
        self.assert_eq(STEP_IDEA_REVIEW, "idea_review", "STEP_IDEA_REVIEW 常量")
        self.assert_eq(IDEA_REVIEW_THRESHOLD, 0.70, "IDEA_REVIEW_THRESHOLD 为 0.70")
        self.assert_eq(MAX_IDEA_REVIEW_ATTEMPTS, 3, "MAX_IDEA_REVIEW_ATTEMPTS 为 3")

    def _test_chain_order_priority(self):
        """idea_review 在 _CHAIN_ORDER 中优先级最高（-1）。"""
        from lifecycle.micro_scheduler import _CHAIN_ORDER
        from lifecycle.constants import STEP_IDEA_REVIEW

        self.assert_in(STEP_IDEA_REVIEW, _CHAIN_ORDER, "idea_review 在 _CHAIN_ORDER 中")
        self.assert_eq(_CHAIN_ORDER[STEP_IDEA_REVIEW], -1, "idea_review 优先级为 -1（最高）")
