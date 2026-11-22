#!/usr/bin/env python3
"""
test_method_manual_module.py — 方法手册第六评审模块（v7.3.0）单测

背景（用户裁决 2026-11-02）：
    课题产出的目的是"提供可以开展的课题"——研究方法手册的详细程度与
    完整度决定课题能否正式开工。手册从轮末 derived 维护步升级为第六
    评审模块（method_manual），进入对抗评审 / section_passes / 晋级 /
    验收判据全链路。

验证点：
    1. 模块清单：REVIEW_SECTION_KEYS=6（含 method_manual），申请书正文
       PROPOSAL_SECTIONS 保持 5（手册不进 sections/ 文件机制）
    2. 建轮链：manual critic+writer 插在 references 后、monitor 前；
       monitor 依赖 manual writer；derived update_method_manual 撤除；
       手册过线后常规轮跳过（monitor 依赖重接 references writer）
    3. 评分口径：expected_dim_keys("method_manual")=（readiness, rigor）；
       _DIM_MAP 含"就绪度"
    4. completion：REQUIRED_SECTIONS=6；5/6 全胜不达标；escape 阀警告
       附"手册未达开工就绪"
    5. dossier 预审：monitor/exec 双门达标但手册未过线 → attention
       （不可 approve）；手册过线 → approve_lean；can_adopt 手册门
    6. 手册 writer 步：score_history 入史（caliber=manual_2d）+
       section_passes 门控（L2 不通过 / L3 无缺口通过）
    7. 手册产物检查 _manual_product_ok：含手册 job 的轮次须手册 ≥400B
"""

import json
import sys
import shutil
import importlib
from pathlib import Path
from types import SimpleNamespace

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from test_runner import TestSuite, create_isolated_env


def _make_job(pid, round_num, section_key, step, status="done", depends_on=None):
    return {
        "job_id": f"{pid}-r{round_num}-{section_key}-{step}",
        "proposal_id": pid,
        "step": step,
        "section_key": section_key,
        "round": round_num,
        "status": status,
        "depends_on": depends_on or [],
        "attempts": 0, "scheduled_at": "", "started_at": "", "finished_at": "",
        "last_error": "", "cron_job_id": "",
    }


class MethodManualModuleTests(TestSuite):
    """v7.3.0: 方法手册第六评审模块测试。"""

    def __init__(self):
        super().__init__("方法手册第六模块")
        self.tmp_root = None
        self.lc = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        pid = "general-manual-module-test-20261102"
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / pid
        (prop_dir / "04_proposal" / "sections").mkdir(parents=True, exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text(
            "# 申请书\n\n" + "研究方案内容。" * 200, encoding="utf-8")
        for sec in ["rationale.md", "content.md", "scheme.md",
                    "full_review.md", "references.md"]:
            (prop_dir / "04_proposal" / "sections" / sec).write_text(
                "# " + sec + "\n\n" + "x" * 100, encoding="utf-8")
        self.pid = pid
        self.prop_dir = prop_dir

        for mod_name in list(sys.modules.keys()):
            if mod_name in ["lifecycle", "lifecycle.controller", "lifecycle.executor",
                            "lifecycle.micro_scheduler", "paths", "common",
                            "proposal_lifecycle", "proposal_sections"]:
                del sys.modules[mod_name]
        self._saved_skill_loader = sys.modules.get("skill_loader")
        sys.modules["skill_loader"] = SimpleNamespace(inject_block=lambda *a, **k: "")

        controller = importlib.import_module("lifecycle.controller")
        import paths
        paths.PROJECT_ROOT = self.tmp_root
        self.lc = controller.LifecycleCronController()
        self.controller_mod = controller
        # 状态与阈值打桩（隔离真实 _lifecycle.json）
        self._state_store = {}
        self.lc._get_proposal_state = lambda pid: self._state_store.get(pid)
        self.lc._set_proposal_state = lambda pid, st: self._state_store.__setitem__(pid, st)
        self.lc._get_quality_threshold = lambda pt: {"min_overall_score": 0.85}
        self.lc._find_proposal_dir = (
            lambda p: self.prop_dir if p == self.pid else None
        )

    def teardown(self):
        if getattr(self, "_saved_skill_loader", None) is not None:
            sys.modules["skill_loader"] = self._saved_skill_loader
        else:
            sys.modules.pop("skill_loader", None)
        for _mod in ("lifecycle", "lifecycle.controller", "lifecycle.executor",
                     "lifecycle.micro_scheduler", "paths", "common",
                     "proposal_lifecycle", "proposal_sections"):
            sys.modules.pop(_mod, None)
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ===== 用例 =====

    def test_module_registry(self):
        """场景1: 评审模块 6 个，申请书正文模块保持 5 个。"""
        from proposal_sections import (
            PROPOSAL_SECTIONS, SECTION_KEYS, REVIEW_SECTION_KEYS, MANUAL_SECTION_KEY,
        )
        self.assert_eq(len(PROPOSAL_SECTIONS), 5, "申请书正文模块保持 5")
        self.assert_eq(len(SECTION_KEYS), 5, "SECTION_KEYS 保持 5")
        self.assert_eq(len(REVIEW_SECTION_KEYS), 6, "评审模块应为 6")
        self.assert_true(MANUAL_SECTION_KEY in REVIEW_SECTION_KEYS, "含 method_manual")
        self.assert_true(MANUAL_SECTION_KEY not in SECTION_KEYS, "手册不进正文清单")

    def test_build_round_jobs_manual_chain(self):
        """场景2: 手册链插入 references 后，monitor 依赖手册 writer。"""
        self._state_store[self.pid] = {"status": "optimizing", "section_passes": {}}
        jobs = self.lc._build_full_round_jobs(self.pid, 1)
        manual_jobs = [j for j in jobs if j.get("section_key") == "method_manual"]
        self.assert_eq(len(manual_jobs), 2, "手册链应为 critic+writer 2 job")
        self.assert_eq(manual_jobs[0]["step"], "critic", "手册 critic 在前")
        self.assert_eq(manual_jobs[1]["step"], "writer", "手册 writer 在后")
        # 依赖：manual critic ← references writer；manual writer ← manual critic
        ref_writer = next(
            j for j in jobs
            if j["section_key"] == "references" and j["step"] == "writer")
        self.assert_eq(
            manual_jobs[0]["depends_on"], [ref_writer["job_id"]],
            "手册 critic 依赖 references writer")
        self.assert_eq(
            manual_jobs[1]["depends_on"], [manual_jobs[0]["job_id"]],
            "手册 writer 依赖手册 critic")
        # monitor 依赖手册 writer；derived 撤除 update_method_manual
        monitor = next(j for j in jobs if j["section_key"] == "monitor")
        self.assert_eq(
            monitor["depends_on"], [manual_jobs[1]["job_id"]],
            "monitor 依赖手册 writer")
        self.assert_true(
            all(j["step"] != "update_method_manual" for j in jobs),
            "derived update_method_manual 应撤除")

    def test_build_round_jobs_skip_passed_manual(self):
        """场景2b: 手册过线后常规轮跳过，monitor 重接 references writer。"""
        self._state_store[self.pid] = {
            "status": "optimizing",
            "section_passes": {"method_manual": True},
        }
        jobs = self.lc._build_full_round_jobs(self.pid, 2)
        manual_jobs = [j for j in jobs if j.get("section_key") == "method_manual"]
        self.assert_eq(len(manual_jobs), 0, "过线手册常规轮应跳过")
        monitor = next(j for j in jobs if j["section_key"] == "monitor")
        ref_writer = next(
            j for j in jobs
            if j["section_key"] == "references" and j["step"] == "writer")
        self.assert_eq(
            monitor["depends_on"], [ref_writer["job_id"]],
            "跳过时 monitor 重接 references writer")
        # 强制复检轮（round % 3 == 0）全量重建
        jobs_r3 = self.lc._build_full_round_jobs(self.pid, 3)
        manual_r3 = [j for j in jobs_r3 if j.get("section_key") == "method_manual"]
        self.assert_eq(len(manual_r3), 2, "强制复检轮手册链应重建")

    def test_dim_caliber(self):
        """场景3: 手册 2 维口径（readiness/rigor）。"""
        from lifecycle.executor import (
            MANUAL_DIM_KEYS, expected_dim_keys, judge_dims_partial,
        )
        self.assert_eq(expected_dim_keys("method_manual"), ("readiness", "rigor"),
                       "手册期望维度集")
        partial, present, missing = judge_dims_partial(
            "method_manual", {"readiness": 0.9})
        self.assert_true(partial, "缺 rigor 应判残缺")
        self.assert_eq(missing, ["rigor"], "缺失维度为 rigor")
        partial2, _, _ = judge_dims_partial(
            "method_manual", {"readiness": 0.9, "rigor": 0.8})
        self.assert_true(not partial2, "两维齐备不残缺")
        _ = MANUAL_DIM_KEYS

    def test_completion_requires_manual(self):
        """场景4: REQUIRED_SECTIONS=6；5/6 全胜不达标；6/6 全胜只提醒不晋级。"""
        from proposal_sections import REVIEW_SECTION_KEYS
        comp = self.lc  # CompletionMixin 已组合进控制器
        self.assert_eq(len(comp.REQUIRED_SECTIONS), 6, "达标门应为 6 模块")
        self.assert_eq(comp.REQUIRED_SECTIONS, REVIEW_SECTION_KEYS, "与真相源一致")
        base = {
            "status": "optimizing",
            "score_history": [],
            "last_score": 0.9,
            "section_passes": {
                "rationale": True, "content": True, "scheme": True,
                "full_review": True, "references": True,
            },
            "optimization_rounds": 5,
            "monitor_history": [{"monitor_independent_score": 0.92}],
            "open_critical_issues": [],
        }
        self._state_store[self.pid] = base
        r = comp._check_done(self.pid, {"min_overall_score": 0.85})
        self.assert_true(not r["done"], "5/6 模块不应达标")
        self.assert_true("method_manual" in r.get("reason", ""),
                         "未达标原因应点名 method_manual")
        base["section_passes"]["method_manual"] = True
        self._state_store[self.pid] = base
        r2 = comp._check_done(self.pid, {"min_overall_score": 0.85})
        # v7.3.42 用户裁决：A 通道 6/6 全胜不再自动晋级，只写专家评审提醒
        self.assert_true(not r2["done"], "6/6 全胜在提醒模式下不应自动晋级")
        self.assert_eq(r2.get("promotion_kind"), None, "A 通道不再产出晋级标记")

    def test_escape_valve_manual_warning(self):
        """场景4b: 逃生阀晋级时手册未就绪 → 质量警告点名手册。"""
        # 分数缓慢爬升避免先触发"连续无提升"阀，让最大轮数阀生效
        self._state_store[self.pid] = {
            "status": "optimizing",
            "score_history": [
                {"round": i, "score": 0.80 + i * 0.005, "focus_section": "rationale"}
                for i in range(1, 8)
            ],
            "last_score": 0.8,
            "section_passes": {},
            "optimization_rounds": 8,
            "monitor_history": [],
            "open_critical_issues": [],
        }
        r = self.lc._check_done(self.pid, {"min_overall_score": 0.85})
        self.assert_true(r["done"], "达到最大轮数应触发逃生阀")
        self.assert_eq(r.get("promotion_kind"), "escape_max_rounds", "逃生阀晋级")
        self.assert_true(
            "方法手册未达开工就绪" in (r.get("quality_warning") or ""),
            "质量警告应点名手册未就绪")

    def test_dossier_manual_gate(self):
        """场景5: 手册未过线 → 预审至多 attention；过线 → approve_lean。"""
        from review_dossier import (
            VERDICT_APPROVE, VERDICT_ATTENTION, can_adopt_pre_review,
            compute_pre_review,
        )
        sections = ["rationale", "content", "scheme", "full_review",
                    "references", "method_manual"]
        base = {
            "score_history": [
                {"round": i + 1, "focus_section": s, "score": 0.88,
                 "section_passed": True}
                for i, s in enumerate(sections)
            ],
            "open_critical_issues": [],
            "last_monitor_score": 0.88,
            "monitor_history": [{
                "monitor_independent_score": 0.88, "high_issues_after": 0,
                "executability_score": 0.86, "round": 6,
            }],
            "optimization_rounds": 6,
        }
        # 手册未过线：把手册条目改为未通过（L2）
        not_ready = json.loads(json.dumps(base))
        not_ready["score_history"][-1] = {
            "round": 6, "focus_section": "method_manual", "score": 0.78,
            "section_passed": False, "manual_readiness_level": 2,
        }
        pre = compute_pre_review(not_ready)
        self.assert_eq(pre["verdict"], VERDICT_ATTENTION,
                       "手册未过线应封顶 attention")
        self.assert_true(
            any("手册" in r for r in pre["reasons"]), "reasons 应含手册原因")
        self.assert_true(not pre["metrics"]["manual_ready"], "manual_ready=False")
        self.assert_true(
            not can_adopt_pre_review({
                "pre_review_verdict": pre["verdict"], "monitor_score": 0.88,
                "executability_score": 0.86,
                "manual_ready": pre["metrics"]["manual_ready"],
            }), "手册门应禁用一键采纳")
        # 手册过线（L3）
        pre2 = compute_pre_review(base)
        self.assert_eq(pre2["verdict"], VERDICT_APPROVE, "手册过线可 approve_lean")
        self.assert_true(pre2["metrics"]["manual_ready"], "manual_ready=True")

    def _write_manual_report(self, round_num, score, level, gap_line=None):
        report = (
            f"# 手册就绪度评审 R{round_num}\n\n"
            "## 问题清单\n\n"
            + (gap_line + "\n" if gap_line else "")
            + "\n## 评分\n创新性：N/A\n可行性：N/A\n"
            f"严谨性：{score}\n就绪度：{score}\n综合评分：{score}\n"
            f"手册就绪度：L{level}\n"
        )
        path = self.prop_dir / "05_review" / f"critic-round-{round_num}-method_manual.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")

    def _patch_manual_hermes(self):
        plan = json.dumps({"actions": [
            {"action": "add", "section": "R1 计算协议", "detail": "补齐实施步骤",
             "source_hint": ""},
        ]}, ensure_ascii=False)
        calls = []

        def fake(profile, prompt, timeout=300):
            calls.append({"profile": profile, "prompt": prompt, "timeout": timeout})
            if "更新计划" in prompt:
                return {"success": True, "output": plan, "error": "", "elapsed_s": 10}
            # 阶段2：模拟手册被写大（超过占位体积）
            manual = self.prop_dir / "03_method" / "method-manual.md"
            manual.parent.mkdir(parents=True, exist_ok=True)
            manual.write_text("# 方法学手册\n\n" + "x" * 2000, encoding="utf-8")
            return {"success": True, "output": "已更新", "error": "", "elapsed_s": 30}

        self.lc._run_hermes = fake
        self.manual_calls = calls

    def test_manual_writer_step_scoring(self):
        """场景6: 手册 writer 步入史 + 门控（L2 不通过 / L3 通过）。"""
        manual = self.prop_dir / "03_method" / "method-manual.md"
        manual.parent.mkdir(parents=True, exist_ok=True)
        manual.write_text("# 方法学手册\n\n" + "x" * 1500, encoding="utf-8")
        self._state_store[self.pid] = {
            "status": "optimizing", "score_history": [], "section_passes": {},
        }

        # L2 + 分 0.78 → 不通过
        self._write_manual_report(1, 0.78, 2)
        self._patch_manual_hermes()
        r = self.lc._run_manual_writer_step(self.pid, {"round": 1})
        self.assert_true(r.get("success"), f"writer 步应成功: {r}")
        self.assert_true(not r.get("section_passed"), "L2+0.78 不应过线")
        st = self._state_store[self.pid]
        entry = st["score_history"][-1]
        self.assert_eq(entry["focus_section"], "method_manual", "入史 focus_section")
        self.assert_eq(entry["caliber"], "manual_2d", "入史口径标记")
        self.assert_eq(entry["manual_readiness_level"], 2, "就绪度入史")
        self.assert_true("method_manual" in st["section_passes"], "section_passes 记录")
        # 缺口驱动：报告含 high 缺口 → 计划 prompt 注入缺口块
        self._write_manual_report(
            2, 0.70, 1,
            gap_line="[high]｜要素④｜R1 计算协议｜缺实施步骤｜按方法页补齐协议细节")
        self._patch_manual_hermes()
        r2 = self.lc._run_manual_writer_step(self.pid, {"round": 2})
        self.assert_true(r2.get("success"), "缺口场景应成功")
        self.assert_true(
            "缺口驱动升级" in self.manual_calls[0]["prompt"],
            "critic 缺口应注入阶段1计划 prompt")

        # L3 + 分 0.88 无缺口 → 通过
        self._write_manual_report(3, 0.88, 3)
        self._patch_manual_hermes()
        r3 = self.lc._run_manual_writer_step(self.pid, {"round": 3})
        self.assert_true(r3.get("section_passed"), "L3+0.88 无缺口应过线")
        self.assert_eq(self._state_store[self.pid]["section_passes"]["method_manual"],
                       True, "过线写入 section_passes")

    def test_manual_product_ok(self):
        """场景7: 手册产物检查 helper。"""
        from lifecycle.micro_scheduler import _manual_product_ok
        prop_dir = self.prop_dir / "04_proposal"
        manual_jobs = [_make_job(self.pid, 1, "method_manual", "writer")]
        plain_jobs = [_make_job(self.pid, 1, "rationale", "writer")]
        # 清理前序用例可能残留的手册（用例顺序隔离）
        manual = self.prop_dir / "03_method" / "method-manual.md"
        if manual.exists():
            manual.unlink()
        # 无手册 job → 恒 True
        self.assert_true(_manual_product_ok(prop_dir, plain_jobs), "无手册 job 恒过")
        # 有手册 job 但手册缺失 → False
        self.assert_true(
            not _manual_product_ok(prop_dir, manual_jobs), "手册缺失应不过")
        # 手册超占位体积 → True
        manual.parent.mkdir(parents=True, exist_ok=True)
        manual.write_text("# 方法学手册\n\n" + "x" * 1000, encoding="utf-8")
        self.assert_true(_manual_product_ok(prop_dir, manual_jobs), "实质手册应过")

    def run_tests(self):
        self.test_module_registry()
        self.test_build_round_jobs_manual_chain()
        self.test_build_round_jobs_skip_passed_manual()
        self.test_dim_caliber()
        self.test_completion_requires_manual()
        self.test_escape_valve_manual_warning()
        self.test_dossier_manual_gate()
        self.test_manual_writer_step_scoring()
        self.test_manual_product_ok()


if __name__ == "__main__":
    suite = MethodManualModuleTests()
    try:
        suite.setup()
        suite.run_tests()
    finally:
        suite.teardown()
    total = len(suite.results)
    passed = sum(1 for r in suite.results if r.passed)
    failed = [r for r in suite.results if not r.passed]
    print(f"\n=== {suite.name} ===")
    print(f"通过 {passed}/{total}")
    for r in failed:
        print(f"  ✗ {r.name}: {r.msg}")
    sys.exit(1 if failed else 0)
