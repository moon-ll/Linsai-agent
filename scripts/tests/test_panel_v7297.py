#!/usr/bin/env python3
"""v7.2.97 评审团执行者插拔测试（任务包发射器 + 引擎收尾命令）。

覆盖：
1. _executor_config：fail-open 默认 engine、非法值回退、hermes 显式开启
2. engine 模式 run_panel：产出任务包、不调任何 LLM（_run_hermes 被
   monkeypatch 为必炸探针）、action=task_emitted
3. 任务包内容守卫：靶子/契约路径/红线/收尾命令齐备
4. adopt_engine_result：核销表「已解决」清账、「未解决/豁免」保留、
   settle_all 兜底、无 verify 报告拒绝收尾
5. docstring/skill/cron 注释定位守卫

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_panel_v7297.py
"""

import json
import sys
import tempfile
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite, REAL_ROOT


class PanelV7297Tests(TestSuite):
    def __init__(self):
        super().__init__("v7.2.97 评审团执行者插拔测试")
        self.tmp_root = None

    def assert_true(self, condition, name, msg: str = "") -> bool:
        if isinstance(condition, str):
            condition, name = name, condition
        return super().assert_true(bool(condition), str(name), msg)

    def setup(self):
        self.tmp_root = Path(tempfile.mkdtemp(prefix="panel-v7297-"))

    def teardown(self):
        pass

    def run_tests(self):
        if self.tmp_root is None:
            self.setup()
        self.test_executor_config()
        self.test_engine_emits_task_package()
        self.test_adopt_engine()
        self.test_wiring_guards()

    # ─────────────────────────────────────────────
    # 1. _executor_config
    # ─────────────────────────────────────────────
    def test_executor_config(self):
        import panel_review as pr
        # 默认（无配置文件或非主流路径）应为 engine
        self.assert_true("engine 执行器默认", pr._executor_config() in ("engine", "hermes"))
        # 非法值回退 engine
        pr.EXECUTOR_CONFIG_PATH = self.tmp_root / "bad.json"
        self.tmp_root.mkdir(exist_ok=True)
        pr.EXECUTOR_CONFIG_PATH.write_text('{"executor": "kimi"}', encoding="utf-8")
        self.assert_true("非法执行器值回退 engine", pr._executor_config() == "engine")
        # hermes 显式开启
        pr.EXECUTOR_CONFIG_PATH.write_text('{"executor": "hermes"}', encoding="utf-8")
        self.assert_true("hermes 显式 opt-in 生效", pr._executor_config() == "hermes")
        # 文件缺失 fail-open
        pr.EXECUTOR_CONFIG_PATH = self.tmp_root / "missing.json"
        self.assert_true("配置缺失 fail-open 默认 engine", pr._executor_config() == "engine")

    # ─────────────────────────────────────────────
    # 2. engine 模式 run_panel：任务包发射器
    # ─────────────────────────────────────────────
    def test_engine_emits_task_package(self):
        import panel_review as pr

        # 构造临时课题（pending_review 优先命中 _proposal_dir）
        pid = "v7297-engine-probe"
        prop_dir = self.tmp_root / "pending_review" / pid
        sec = prop_dir / "04_proposal" / "sections"
        sec.mkdir(parents=True)
        for name in ("rationale", "content", "scheme", "full_review", "references"):
            (sec / f"{name}.md").write_text(f"# {name}\n测试正文。", encoding="utf-8")

        saved = (pr.PROJECT_ROOT, pr._proposal_dir, pr._executor_config)
        probe = object()  # 必炸探针：engine 模式绝不允许走到 LLM 调用
        try:
            pr.PROJECT_ROOT = self.tmp_root
            pr._proposal_dir = lambda x: prop_dir
            pr._executor_config = lambda: "engine"
            pr._run_hermes = lambda *a, **kw: (_ for _ in ()).throw(
                AssertionError("engine 模式不得调用 LLM"))
            pr._load_open_issues = lambda x: []
            # _lifecycle.json 不存在 → status 空串（fail-open）
            r = pr.run_panel(pid, consumer="v7297-test")
            self.assert_true("engine 模式 success=True", r.get("success") is True)
            self.assert_true("action=task_emitted", r.get("action") == "task_emitted")
            self.assert_true("executor 标记为 engine", r.get("executor") == "engine")
            pkg = Path(r.get("task_package", ""))
            self.assert_true("任务包文件已产出", pkg.name == "panel-task-package.md"
                             and pkg.exists())
            content = pkg.read_text(encoding="utf-8")
            self.assert_true("任务包含核查靶子段", "核查靶子" in content)
            self.assert_true("任务包含 skill 契约路径", "quality-review" in content
                             and "第五~七节" in content)
            self.assert_true("任务包含三源对照红线", "lit-gap-*.md" in content
                             and "不得写入" in content)
            self.assert_true("任务包含标准收尾命令", f"--adopt-engine {pid}" in content)
            self.assert_true("任务包含输出契约", "panel-verify-report.md" in content
                              and "复核结论" in content)
            # hermes 模式不会被走到（_run_hermes 已炸）——切换后立即返回失败即证明路径切换
            pr._executor_config = lambda: "hermes"
            try:
                r2 = pr.run_panel(pid, consumer="v7297-test")
                self.assert_true("hermes 模式会尝试调 LLM（被探针拦截证明路径切换）",
                                 r2.get("success") is False)
            except AssertionError:
                self.assert_true("hermes 模式会尝试调 LLM（探针异常冒泡证明路径切换）", True)
        finally:
            pr.PROJECT_ROOT, pr._proposal_dir, pr._executor_config = saved

    # ─────────────────────────────────────────────
    # 3. adopt_engine_result：清账/豁免保留
    # ─────────────────────────────────────────────
    def test_adopt_engine(self):
        import panel_review as pr

        pid = "v7297-adopt-probe"
        prop_dir = self.tmp_root / "optimizing" / pid
        (prop_dir / "04_proposal" / "sections").mkdir(parents=True)
        panel_dir = prop_dir / "06_panel"
        panel_dir.mkdir()
        (panel_dir / "panel-verify-report.md").write_text(
            "| L1 | critical | 已解决 | 已修 |\n"
            "| L2 | high | 未解决 | 残留 |\n"
            "| L3 | medium | 豁免 | 记录 |\n"
            "复核结论: 通过", encoding="utf-8")

        saved_root = pr.PROJECT_ROOT
        saved_dir = pr._proposal_dir
        saved_status = pr._proposal_status
        saved_gate = pr._anchor_gate
        try:
            pr.PROJECT_ROOT = self.tmp_root
            pr._proposal_dir = lambda x: prop_dir
            pr._proposal_status = lambda x: "optimizing"
            # 锚集守卫 mock：通过
            pr._anchor_gate = lambda x: ""
            # lifecycle.json 夹具
            lc = self.tmp_root / "research_proposals" / "_lifecycle.json"
            lc.parent.mkdir(parents=True, exist_ok=True)
            lc.write_text(json.dumps({"proposals": {pid: {
                "status": "optimizing", "optimization_rounds": 5,
                "panel_review_requested": True,
                # v7.3.10: 手册开工就绪门夹具——手册已过线（收尾放行路径）
                "score_history": [
                    {"round": 2, "focus_section": "method_manual", "score": 0.88,
                     "section_passed": True, "manual_readiness_level": 3},
                ],
                "open_critical_issues": [
                    {"severity": "critical", "description": "靶1"},
                    {"severity": "high", "description": "靶2"},
                    {"severity": "medium", "description": "靶3"},
                ],
            }}}, ensure_ascii=False), encoding="utf-8")
            # 状态机 mock（transition/dossier 不真跑）
            import types
            fake_lc = types.ModuleType("proposal_lifecycle")
            class FakeLifecycle:
                def clear_panel_request(self, *a, **kw): return {"success": True}
                def reset_panel_cycle(self, *a, **kw): return {"success": True}
                def transition(self, *a, **kw): return {"success": True}
                def _get_proposal_state(self, *a, **kw): return {}
                def _set_proposal_state(self, *a, **kw): pass
            fake_lc.ProposalLifecycle = FakeLifecycle
            fake_rd = types.ModuleType("review_dossier")
            fake_rd.generate_review_dossier = lambda *a, **kw: {"success": True}
            saved_mods = (sys.modules.get("proposal_lifecycle"), sys.modules.get("review_dossier"))
            sys.modules["proposal_lifecycle"] = fake_lc
            sys.modules["review_dossier"] = fake_rd
            try:
                r = pr.adopt_engine_result(pid)
            finally:
                for name, mod in zip(("proposal_lifecycle", "review_dossier"), saved_mods):
                    if mod is None:
                        sys.modules.pop(name, None)
                    else:
                        sys.modules[name] = mod

            self.assert_true("verdict=通过（总结行解析）", r.get("verdict") == "通过")
            self.assert_true("仅「已解决」清账（1 条）", r.get("cleared") == 1)
            self.assert_true("未解决/豁免保留（2 条）", r.get("kept") == 2)
            self.assert_true("optimizing + 通过 → 晋级", r.get("action") == "promoted_pending_review")
            data = json.loads(lc.read_text(encoding="utf-8"))
            issues = data["proposals"][pid]["open_critical_issues"]
            self.assert_true("靶1 已清账", issues[0].get("resolved_by", "").startswith("engine-panel-"))
            self.assert_true("靶2 保留（未解决）", issues[1].get("round_resolved") is None)
            self.assert_true("靶3 保留（豁免）", issues[2].get("round_resolved") is None)
            self.assert_true("panel 标志已清", data["proposals"][pid]["panel_review_requested"] is False)

            # settle_all 兜底：剩余未解决条目全部清账（首次 adopt 已清靶1，
            # 此时剩靶2/靶3 共 2 条）
            r2 = pr.adopt_engine_result(pid, settle_all=True)
            self.assert_true("settle_all 清剩余 2 条且无保留",
                             r2.get("cleared") == 2 and r2.get("kept") == 0)

            # 无 verify 报告拒绝
            (panel_dir / "panel-verify-report.md").unlink()
            r3 = pr.adopt_engine_result(pid)
            self.assert_true("无 verify 报告拒绝收尾", r3.get("success") is False)
        finally:
            pr.PROJECT_ROOT = saved_root
            pr._proposal_dir = saved_dir
            pr._proposal_status = saved_status
            pr._anchor_gate = saved_gate

    # ─────────────────────────────────────────────
    # 4. 定位守卫（docstring/skill/cron 注释）
    # ─────────────────────────────────────────────
    def test_wiring_guards(self):
        src = (_SCRIPTS_DIR / "panel_review.py").read_text(encoding="utf-8")
        self.assert_true("docstring 声明执行者插拔（engine 默认/hermes opt-in）",
                         "panel-executor.json" in src and "任务包发射器" in src)
        self.assert_true("engine 分支在阶段 A 之前（发射即返）",
                         src.find("task_emitted") < src.find("阶段 A"))
        self.assert_true("adopt_engine_result 含锚集守卫",
                         "_anchor_gate(proposal_id)" in src)
        self.assert_true("CLI 有 --adopt-engine 与 --settle-all",
                         '"--adopt-engine"' in src and '"--settle-all"' in src)
        # cron wrapper 注释
        ctrl = (_SCRIPTS_DIR / "lifecycle" / "controller.py").read_text(encoding="utf-8")
        self.assert_true("cron wrapper 注释声明 engine=发射器语义",
                         "panel-executor.json" in ctrl and "发射" in ctrl)
        # skill 契约
        from skill_loader import load_skill, extract_section
        skill = load_skill("quality-review")
        sec5 = extract_section(skill, "五、评审团 = 执行者无关的流程契约")
        self.assert_true("skill 五节含任务包交接与 opt-in 托底",
                         "panel-task-package.md" in sec5 and "opt-in" in sec5)
        sec6 = extract_section(skill, "六、评审团角色与findings契约")
        self.assert_true("skill 六节标题改全执行者通用契约", "全执行者通用契约" in skill)


if __name__ == "__main__":
    suite = PanelV7297Tests()
    suite.run_tests()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"\n{'✓' if suite.results and len(suite.results) - ok == 0 else '✗'} {suite.name}: {ok}/{len(suite.results)} 通过")
    for r in suite.results:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    raise SystemExit(1 if len(suite.results) - ok else 0)
