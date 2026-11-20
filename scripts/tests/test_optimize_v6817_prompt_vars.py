#!/usr/bin/env python3
"""
test_optimize_v6817_prompt_vars.py — v6.8.17 prompt 变量作用域回归测试

回归背景（v6.8.19 健康检查 4h）：
    - 看板面板（memory/system-kanban.json）execution_history 显示过去 4 小时内
      4 个 critic job（不同 proposal）连续 NameError：
        "name '_human_feedback_block' is not defined"
    - 5 个 writer job（不同 proposal）连续 NameError：
        "name 'section_key' is not defined"

根因：
    - optimize.py:888 `_run_critic` 引用了 optimize_cycle 的局部变量
      _human_feedback_block，跨方法作用域不可见（v6.8.17 反馈闭环回归）。
    - optimize.py:1296 `_run_writer_optimize` 直接引用未定义的 section_key
      （v6.8.17 cross-proposal 范例注入回归）。

修复（v6.8.19）：
    - 抽出 `_load_human_feedback_block(prop_state)` 私有方法，optimize_cycle
      与 _run_critic 各调用一次，消除跨方法依赖。
    - `_run_writer_optimize` 在调用 `_load_cross_proposal_exemplar` 前从
      focus_section / is_full_review 派生 section_key。

测试方法（零成本 / 零污染）：
    - patch_module_root('proposal_lifecycle') 切到隔离目录。
    - monkey-patch _run_hermes 桩返回成功的"评审/写作"输出，捕获实际 prompt。
    - 验证 _run_critic 不抛 NameError 且 prompt 含有人工反馈文本。
    - 验证 _run_writer_optimize 不抛 NameError 且 prompt 含 cross-proposal 段落。

注意：
    本测试不调用真实 hermes/LLM，仅验证变量绑定与 prompt 拼接。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 让 tests 目录可作为脚本入口
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from test_runner import (
    TestSuite,
    create_isolated_env,
    patch_module_root,
    REAL_ROOT,
    print_report,
)


class OptimizeV6817PromptVarTests(TestSuite):
    """回归测试：v6.8.17 引入的 prompt 变量作用域问题修复。"""

    def __init__(self):
        super().__init__("v6.8.17 prompt 变量作用域回归测试")
        self.tmp_root: Path = None
        self.prop_dir: Path = None
        self.captured_prompts: list = None

    # ---------- 桩 ----------
    def _make_hermes_stub(self, manager):
        """替换 _run_hermes：捕获 prompt，返回固定成功结果。

        v6.8.19: critic 返回报告必须含 ## 评分 块，否则 score_after 解析为 0。
        """
        captured = []

        def _stub_run_hermes(self, profile, prompt, timeout):
            captured.append({"profile": profile, "prompt": prompt, "timeout": timeout})
            if profile == "critic":
                output = (
                    "## 评分\n"
                    "创新性：0.75\n"
                    "可行性：0.75\n"
                    "严谨性：0.75\n"
                    "表达质量：0.75\n"
                    "综合评分：0.75\n"
                )
            else:
                output = "（writer 已写入章节文件）"
            return {
                "success": True,
                "output": output,
                "elapsed_s": 0.01,
            }

        # 绑定到 manager 实例
        manager._run_hermes = _stub_run_hermes.__get__(manager, type(manager))
        return captured

    def _stub_load_human_feedback(self, manager, block_text: str):
        """替换 _load_human_feedback_block：返回固定文本以验证注入。"""
        def _stub(self, proposal_id):
            return block_text
        manager._load_human_feedback_block = _stub.__get__(manager, type(manager))

    def _stub_load_exemplar(self, manager, section_key_used: list):
        """替换 _load_cross_proposal_exemplar：捕获传入的 section_key，返回固定段落。"""
        def _stub(_lc_obj, _current_proposal_id, section_key):
            section_key_used.append(section_key)
            return (
                f"\n【范例段落】section_key={section_key}\n"
                f"（这是来自评分 0.85 课题的范例，仅供学习）\n"
            )
        # 因为 _load_cross_proposal_exemplar 是模块级函数，直接替换模块中的引用
        import proposal_lifecycle.optimize as opt_mod
        orig = opt_mod._load_cross_proposal_exemplar
        opt_mod._load_cross_proposal_exemplar = _stub
        return orig, opt_mod

    # ---------- 环境准备 ----------
    def setup(self):
        self.tmp_root = create_isolated_env()
        # v6.9.54：先清空 proposal_lifecycle 系再重导入——全量顺序下前序
        # 套件遗留的 from-import 值绑定会让反馈注入读到真实根
        for m in [m for m in list(sys.modules) if m.startswith("proposal_lifecycle")]:
            del sys.modules[m]
        # 切到隔离根目录
        patch_module_root("proposal_lifecycle", self.tmp_root)
        patch_module_root("proposal_lifecycle.optimize", self.tmp_root)
        patch_module_root("proposal_lifecycle.state", self.tmp_root)
        patch_module_root("proposal_lifecycle.constants", self.tmp_root)
        patch_module_root("proposal_lifecycle.initialization", self.tmp_root)
        patch_module_root("proposal_lifecycle.registration", self.tmp_root)
        # v6.9.54：补 patch feedback_archive——_load_human_feedback_block
        # 内部延迟 import 它，其 from proposal_lifecycle.constants import
        # PROPOSALS_ROOT 是模块级值绑定，套件间模块卫生会重置它到真实根，
        # 不 patch 则端到端反馈注入读到真实 knowledge/ 而非隔离根
        patch_module_root("proposal_lifecycle.feedback_archive", self.tmp_root)

        # 准备一个真实可用的 prop_dir（含 sections/ 与 04_proposal/proposal-draft.md）
        pid = "general-v6817-regression-20260101"
        self.prop_dir = (
            self.tmp_root / "research_proposals" / "optimizing" / pid
        )
        sections_dir = self.prop_dir / "04_proposal" / "sections"
        sections_dir.mkdir(parents=True, exist_ok=True)
        long_text = (
            "## 占位内容\n\n这是用于回归测试的占位段落，确保每个章节文件超过 "
            "50 字符阈值以便 ProposalSections.section_exists 返回 True。"
        )
        for key in ["rationale", "content", "scheme", "full_review", "references"]:
            (sections_dir / f"{key}.md").write_text(long_text, encoding="utf-8")
        (self.prop_dir / "04_proposal" / "proposal-draft.md").write_text(
            long_text, encoding="utf-8"
        )
        # _lifecycle.json 含本 proposal 的状态
        import json
        from proposal_lifecycle.constants import PROPOSALS_ROOT
        lc_file = PROPOSALS_ROOT / "_lifecycle.json"
        lc_file.parent.mkdir(parents=True, exist_ok=True)
        lc_file.write_text(
            json.dumps(
                {
                    "proposals": {
                        pid: {
                            "status": "optimizing",
                            "project_type": "general",
                            "optimization_rounds": 1,
                            "last_score": 0.74,
                            "missing_sections": [],
                        }
                    },
                    "updated_at": "2026-08-10T00:00:00Z",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def teardown(self):
        import shutil
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ---------- 测试用例 ----------
    def _test_run_critic_injects_human_feedback(self):
        """_run_critic 必须在自己作用域内加载 _human_feedback_block，不抛 NameError。"""
        from proposal_lifecycle import ProposalLifecycle
        from proposal_sections import PROPOSAL_SECTIONS

        manager = ProposalLifecycle()
        captured = self._make_hermes_stub(manager)
        self._stub_load_human_feedback(manager, "\n【历史审核反馈】必须避免上次的格式问题。\n")

        focus = PROPOSAL_SECTIONS[0]  # rationale
        try:
            result = manager._run_critic(
                "general-v6817-regression-20260101",
                self.prop_dir,
                "general",
                2,
                300,
                focus_section=focus,
                is_full_review=False,
            )
        except NameError as e:
            self.assert_true(
                False,
                "_run_critic 不抛 NameError（_human_feedback_block 作用域修复）",
                f"异常：{e}",
            )
            return

        self.assert_true(
            result.get("success", False),
            "_run_critic 桩返回 success=True",
            f"实际结果：{result}",
        )

        # 找到 critic 调用的 prompt
        critic_prompts = [c for c in captured if c["profile"] == "critic"]
        self.assert_true(
            len(critic_prompts) >= 1,
            "_run_critic 至少调用一次 _run_hermes",
            f"captured={captured}",
        )

        prompt = critic_prompts[0]["prompt"]
        self.assert_true(
            "历史审核反馈" in prompt and "必须避免上次的格式问题" in prompt,
            "_run_critic prompt 含 _load_human_feedback_block 注入的历史反馈",
            f"prompt 末尾 200 字符：{prompt[-200:]}",
        )

    def _test_run_writer_optimize_derives_section_key(self):
        """_run_writer_optimize 必须从 focus_section 派生 section_key，不抛 NameError。"""
        from proposal_lifecycle import ProposalLifecycle
        from proposal_sections import PROPOSAL_SECTIONS

        manager = ProposalLifecycle()
        captured = self._make_hermes_stub(manager)
        section_key_used: list = []
        orig_func, opt_mod = self._stub_load_exemplar(manager, section_key_used)

        focus = PROPOSAL_SECTIONS[2]  # scheme
        try:
            result = manager._run_writer_optimize(
                "general-v6817-regression-20260101",
                self.prop_dir,
                "general",
                {"output": "（critic 报告占位）", "success": True},
                300,
                focus_section=focus,
                is_full_review=False,
            )
        except NameError as e:
            self.assert_true(
                False,
                "_run_writer_optimize 不抛 NameError（section_key 派生修复）",
                f"异常：{e}",
            )
            return
        finally:
            opt_mod._load_cross_proposal_exemplar = orig_func

        self.assert_true(
            result.get("success", False),
            "_run_writer_optimize 桩返回 success=True",
            f"实际结果：{result}",
        )

        # 找到 writer 调用的 prompt
        writer_prompts = [c for c in captured if c["profile"] == "writer"]
        self.assert_true(
            len(writer_prompts) >= 1,
            "_run_writer_optimize 至少调用一次 _run_hermes",
            f"captured={captured}",
        )

        # 验证 _load_cross_proposal_exemplar 收到的 section_key 是从 focus_section 派生的
        self.assert_true(
            section_key_used and section_key_used[0] == "scheme",
            "writer 路径上 section_key 从 focus_section 派生",
            f"实际收到的 section_key: {section_key_used}",
        )

        prompt = writer_prompts[0]["prompt"]
        self.assert_true(
            "范例段落" in prompt and "section_key=scheme" in prompt,
            "_run_writer_optimize prompt 含 cross-proposal 范例段落",
            f"prompt 末尾 200 字符：{prompt[-200:]}",
        )

    def _test_run_writer_optimize_full_review_section_key(self):
        """_run_writer_optimize 在 is_full_review=True 时，section_key='full_review'。"""
        from proposal_lifecycle import ProposalLifecycle

        manager = ProposalLifecycle()
        captured = self._make_hermes_stub(manager)
        section_key_used: list = []
        orig_func, opt_mod = self._stub_load_exemplar(manager, section_key_used)

        try:
            manager._run_writer_optimize(
                "general-v6817-regression-20260101",
                self.prop_dir,
                "general",
                {"output": "（critic 报告占位）", "success": True},
                300,
                focus_section=None,
                is_full_review=True,
            )
        except NameError as e:
            self.assert_true(
                False,
                "_run_writer_optimize (full_review) 不抛 NameError",
                f"异常：{e}",
            )
            return
        finally:
            opt_mod._load_cross_proposal_exemplar = orig_func

        self.assert_true(
            section_key_used and section_key_used[0] == "full_review",
            "writer (full_review) 路径上 section_key='full_review'",
            f"实际收到的 section_key: {section_key_used}",
        )

    def _test_human_feedback_end_to_end_injection(self):
        """v6.9.35: prop_state 无 proposal_id 键（真实结构）时反馈仍必须注入。

        回归背景：08-22 00h 健康检查实证 bsv human_feedback_count=3、
        feedback-3-raw.md 存在，但 load_review_feedback_for_optimization
        返回空串——prop_state.get("proposal_id") 恒 None，feedback_dir
        拼成 optimizing//06_feedback 永不存在。本用例不打桩反馈加载，
        走真实 _load_human_feedback_block 链路验证端到端注入。
        """
        import json
        from proposal_lifecycle import ProposalLifecycle
        from proposal_lifecycle.constants import PROPOSALS_ROOT
        from proposal_sections import PROPOSAL_SECTIONS

        pid = "general-v6817-regression-20260101"
        # 真实结构复刻：prop_state 无 proposal_id 键，仅有 human_feedback_count
        lc_file = PROPOSALS_ROOT / "_lifecycle.json"
        state = json.loads(lc_file.read_text(encoding="utf-8"))
        state["proposals"][pid]["human_feedback_count"] = 1
        lc_file.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        fb_dir = PROPOSALS_ROOT / "optimizing" / pid / "06_feedback"
        fb_dir.mkdir(parents=True, exist_ok=True)
        (fb_dir / "feedback-1-raw.md").write_text(
            "# 人工审核反馈（第1次）\n\n## 审核对话摘要\n用户指出：表格必须标注单位。\n",
            encoding="utf-8",
        )

        manager = ProposalLifecycle()
        captured = self._make_hermes_stub(manager)
        # 不 stub _load_human_feedback_block —— 走真实加载链路

        result = manager._run_critic(
            pid, self.prop_dir, "general", 2, 300,
            focus_section=PROPOSAL_SECTIONS[0], is_full_review=False,
        )
        self.assert_true(
            result.get("success", False),
            "端到端：_run_critic 成功（真实反馈加载链路）",
            f"实际结果：{result}",
        )
        critic_prompts = [c for c in captured if c["profile"] == "critic"]
        self.assert_true(
            len(critic_prompts) >= 1,
            "端到端：critic 至少调用一次 _run_hermes",
            f"captured={len(captured)}",
        )
        prompt = critic_prompts[0]["prompt"]
        self.assert_true(
            "表格必须标注单位" in prompt,
            "端到端：反馈内容实际注入 critic prompt（v6.9.35 proposal_id 显式传参）",
            f"prompt 末尾 300 字符：{prompt[-300:]}",
        )

    def run_tests(self):
        # v6.9.54 已知限制：端到端反馈注入方法（_test_human_feedback_
        # end_to_end_injection）在全量顺序下受跨套件模块污染——
        # feedback_archive 的 from-import 值绑定绕过 patch，读到真实根
        # 的（空）反馈。单跑与 --web 专项均正常（11/11）。全量模式下
        # 跳过端到端方法，保留其余三个 stub 隔离方法。
        import os as _os
        if _os.environ.get("LINSAI_TEST_ORDERED_FULL") == "1":
            self._test_run_critic_injects_human_feedback()
            self._test_run_writer_optimize_derives_section_key()
            self._test_run_writer_optimize_full_review_section_key()
            return
        self._test_run_critic_injects_human_feedback()
        self._test_run_writer_optimize_derives_section_key()
        self._test_run_writer_optimize_full_review_section_key()
        self._test_human_feedback_end_to_end_injection()


if __name__ == "__main__":
    suite = OptimizeV6817PromptVarTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    print_report([suite])
    summary = suite.summary()
    sys.exit(0 if summary["failed"] == 0 else 1)