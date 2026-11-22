#!/usr/bin/env python3
"""
test_method_manual_two_phase.py — 手册更新两阶段生成（v7.2.11）单测

背景：
    旧实现单次 hermes 会话读全册（60-186KB）+ 压缩合并 + 写回，qgi r1 与
    attosecond r1 双双 600s 超时。v7.2.11 拆两阶段：
      阶段1（规划）：手册头部目录 + 体积统计 + 方案节选 → 更新计划 JSON
      阶段2（逐节执行）：每动作独立 hermes 会话（≤300s），只改一个小节

验证点：
    1. 两阶段调用序列（阶段1规划 prompt + 每动作一个执行 prompt）
    2. 超时从 600s 降为 240s（阶段1）/ 300s（阶段2）
    3. 计划解析：代码块包裹 / 裸 JSON / 尾逗号 / 杂文 / 非法输出 None
    4. 空计划（actions=[]）合法跳过 → success + skipped_reason
    5. 阶段1失败 → 整体失败（带"阶段1"标记）
    6. 阶段2部分失败 → 仍 success（applied 计数）
    7. 阶段2全部失败 → 失败（带"阶段2"标记）
    8. 手册超 60KB → 阶段1 prompt 含压缩任务要求
    9. 计划文件 manual-update-plan.md 落盘
"""

import json
import os
import sys
import shutil
import importlib
from pathlib import Path
from types import SimpleNamespace

from test_runner import TestSuite, create_isolated_env


_PLAN_OK = json.dumps({
    "actions": [
        {"action": "add", "section": "泵浦探测序列", "detail": "新增双光子吸收泵浦参数", "source_hint": "pump-probe"},
        {"action": "revise", "section": "数据采集", "detail": "补充采样率参数", "source_hint": ""},
        {"action": "compress", "section": "理论模型对比", "detail": "合并三段重复推导", "source_hint": ""},
        {"action": "merge", "section": "样品制备", "detail": "与制备流程合并", "source_hint": ""},
    ]
}, ensure_ascii=False)


class MethodManualTwoPhaseTests(TestSuite):
    """v7.2.11: update_method_manual 两阶段生成测试。"""

    def __init__(self):
        super().__init__("手册两阶段生成测试")
        self.tmp_root = None
        self.lc = None
        self.calls = []

    def setup(self):
        self.tmp_root = create_isolated_env()
        pid = "general-two-phase-test-20261002"
        prop_dir = self.tmp_root / "research_proposals" / "optimizing" / pid
        (prop_dir / "04_proposal").mkdir(parents=True, exist_ok=True)
        (prop_dir / "04_proposal" / "proposal-draft.md").write_text(
            "# 申请书\n\n" + "研究方案内容。" * 200, encoding="utf-8"
        )
        self.pid = pid
        self.prop_dir = prop_dir

        for mod_name in list(sys.modules.keys()):
            if mod_name in ["lifecycle", "lifecycle.controller", "lifecycle.executor",
                            "paths", "common", "proposal_lifecycle"]:
                del sys.modules[mod_name]

        # v7.2.26 修复：setup/teardown 配对保存并还原 sys.modules["skill_loader"]
        # 此前只有 setup 写入 SimpleNamespace，teardown 不还原——v7.2.25 self_test
        # glob 模式纳入本套件后 SimpleNamespace 占位会泄漏到 test_nsfc_writing_skill
        # 等下游套件，触发 24/31 失败的级联 false negative（健康检查 14 日 04h BJT 触发）。
        self._saved_skill_loader = sys.modules.get("skill_loader")

        # skill_loader 用空实现替换（隔离真实 skills 注入）
        sys.modules["skill_loader"] = SimpleNamespace(
            inject_block=lambda *a, **k: ""
        )

        controller = importlib.import_module("lifecycle.controller")
        import paths
        paths.PROJECT_ROOT = self.tmp_root
        self.lc = controller.LifecycleCronController()
        self.controller_mod = controller

        self.calls = []

    def teardown(self):
        # v7.2.26 修复：teardown 还原 sys.modules["skill_loader"] 与被清
        # 除的模块，否则污染后续套件——v7.2.25 self_test glob 模式纳入
        # 本套件后,SimpleNamespace 占位会泄漏到 test_nsfc_writing_skill
        # 等下游套件，触发 24/31 失败的级联 false negative（健康检查
        # 14 日 04h BJT 触发）。
        if getattr(self, "_saved_skill_loader", None) is not None:
            sys.modules["skill_loader"] = self._saved_skill_loader
        else:
            sys.modules.pop("skill_loader", None)
        # setup 阶段 del 掉的模块,让 Python 重新 import 时从 sys.path 重建
        for _mod in ("lifecycle", "lifecycle.controller", "lifecycle.executor",
                     "paths", "common", "proposal_lifecycle"):
            sys.modules.pop(_mod, None)
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ===== 工具 =====

    def _patch_hermes(self, plan_output=_PLAN_OK, exec_ok=True, exec_fail_sections=None):
        """Mock _run_hermes：第 1 次调用=阶段1 返回计划；后续=阶段2 逐动作。"""
        calls = self.calls
        calls.clear()  # 每次打桩清空调用记录（跨用例隔离）
        fail_sections = set(exec_fail_sections or [])
        state = {"n": 0}
        lc = self.lc
        prop_dir = self.prop_dir

        def fake_run_hermes(profile, prompt, timeout=300):
            state["n"] += 1
            calls.append({
                "profile": profile, "prompt": prompt,
                "timeout": timeout, "idx": state["n"],
            })
            if state["n"] == 1:
                return {"success": True, "output": plan_output, "error": "", "elapsed_s": 10}
            # 阶段2：按 prompt 中是否含失败小节名决定成败
            hit_fail = any(s in prompt for s in fail_sections)
            if exec_ok and not hit_fail:
                return {"success": True, "output": "已更新", "error": "", "elapsed_s": 30}
            return {"success": False, "output": "", "error": "超时(300s)", "elapsed_s": 300}

        lc._run_hermes = fake_run_hermes
        lc._find_proposal_dir = lambda pid: prop_dir if pid == self.pid else None

    def _make_manual(self, size=1000):
        manual = self.prop_dir / "03_method" / "method-manual.md"
        manual.parent.mkdir(parents=True, exist_ok=True)
        manual.write_text("# 方法学手册\n\n" + "x" * size, encoding="utf-8")
        return manual

    # ===== 用例 =====

    def test_two_phase_call_sequence(self):
        """场景1: 1 次规划 + 4 次逐节执行，profile 全为 writer。"""
        self._make_manual()
        self._patch_hermes()
        result = self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(result.get("success"), f"应成功: {result}")
        self.assert_eq(len(self.calls), 5, "调用数应为 1 规划 + 4 执行")
        first = self.calls[0]
        self.assert_true("更新计划" in first["prompt"], "第 1 次调用应是规划 prompt")
        for c in self.calls[1:]:
            self.assert_true(
                "小节级更新" in c["prompt"] or "手册路径" in c["prompt"],
                "后续调用应是逐节执行 prompt",
                f"prompt 缺执行标记: {c['prompt'][:60]}",
            )
        self.assert_eq(result.get("applied"), 4, "applied 应为 4")

    def test_timeouts_reduced(self):
        """场景2: 阶段1=240s；阶段2 按动作分级（v7.3.3）——compress/merge=480s
        （通读重写大段，bsv 66KB 全册压缩 300s 三连超时实录）、
        add/revise=300s；全程无 600s。"""
        self._make_manual()
        self._patch_hermes()
        self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_eq(self.calls[0]["timeout"], 240, "阶段1 timeout 应为 240s")
        # _PLAN_OK 动作序：add / revise / compress / merge
        expected = [300, 300, 480, 480]
        actual = [c["timeout"] for c in self.calls[1:]]
        self.assert_eq(actual, expected, "阶段2 按动作分级超时")
        for c in self.calls:
            self.assert_true(
                c["timeout"] != 600, "不应再出现 600s 单会话超时",
                f"timeout={c['timeout']}",
            )

    def test_plan_parse_variants(self):
        """场景3: 计划解析的四种输入形态。"""
        p = self.lc._parse_manual_plan
        # 裸 JSON
        r1 = p(_PLAN_OK)
        self.assert_eq(len(r1), 4, "裸 JSON 应解析 4 个动作")
        # markdown 代码块包裹
        r2 = p("说明如下：\n```json\n" + _PLAN_OK + "\n```\n以上。")
        self.assert_eq(len(r2), 4, "代码块包裹应解析 4 个动作")
        # 尾逗号
        r3 = p('{"actions": [{"action": "add", "section": "A", "detail": "d",},],}')
        self.assert_eq(len(r3), 1, "尾逗号应被修复并解析 1 个动作")
        # 非法输出 → None
        r4 = p("完全不是 JSON 的输出")
        self.assert_true(r4 is None, "非法输出应返回 None")
        # 合法空计划 → 空列表（与 None 区分）
        r5 = p('{"actions": []}')
        self.assert_eq(r5, [], "空 actions 应返回空列表而非 None")

    def test_empty_plan_legal_skip(self):
        """场景4: 空计划合法跳过 → success + skipped_reason。"""
        self._make_manual()
        self._patch_hermes(plan_output='{"actions": []}')
        result = self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(result.get("success"), f"空计划应成功: {result}")
        self.assert_eq(result.get("skipped_reason"), "empty_plan", "应标记 empty_plan")
        self.assert_eq(len(self.calls), 1, "空计划只应调用 1 次（阶段1）")

    def test_phase1_failure(self):
        """场景5: 阶段1失败 → 整体失败带'阶段1'标记。"""
        self._make_manual()
        self._patch_hermes(plan_output="")  # 规划输出空 → 解析 None
        # 改造：让阶段1调用直接失败
        lc = self.lc
        calls = self.calls

        def fake(profile, prompt, timeout=300):
            calls.append({"profile": profile, "prompt": prompt, "timeout": timeout})
            return {"success": False, "output": "", "error": "超时(240s)", "elapsed_s": 240}

        lc._run_hermes = fake
        lc._find_proposal_dir = lambda pid: self.prop_dir
        result = lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(not result.get("success"), "阶段1失败应整体失败")
        self.assert_true("阶段1" in str(result.get("error", "")), f"错误应带阶段1标记: {result}")

    def test_phase2_partial_failure(self):
        """场景6: 阶段2部分失败 → 仍 success，applied 计数正确。"""
        self._make_manual()
        self._patch_hermes(exec_fail_sections=["数据采集", "样品制备"])
        result = self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(result.get("success"), f"部分失败仍应 success: {result}")
        self.assert_eq(result.get("applied"), 2, "applied 应为 2（4 动作 2 失败）")

    def test_phase2_all_failure(self):
        """场景7: 阶段2全部失败 → 失败带'阶段2'标记。"""
        self._make_manual()
        self._patch_hermes(exec_ok=False)
        result = self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(not result.get("success"), "全部失败应返回失败")
        self.assert_true("阶段2" in str(result.get("error", "")), f"错误应带阶段2标记: {result}")

    def test_overcap_manual_requires_compress(self):
        """场景8: 手册超 60K 字符 → 阶段1 只提示按节瘦身，不再强制整册压缩。"""
        self._make_manual(size=70000)
        self._patch_hermes()
        self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        first_prompt = self.calls[0]["prompt"]
        self.assert_true(
            "体积提示" in first_prompt and "单节瘦身" in first_prompt,
            "超上限手册的阶段1 prompt 应含按节瘦身提示",
        )
        # v7.3.32: 整册压缩口径已移除——不得再要求"必须包含 compress"
        self.assert_true(
            "必须包含至少一个 action=compress" not in first_prompt
            and "整册重写" in first_prompt,
            "阶段1 不应强制整册压缩动作",
        )
        # 未超上限时不应含体积提示
        self.calls.clear()
        self._make_manual(size=1000)
        self._patch_hermes()
        self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(
            "体积提示" not in self.calls[0]["prompt"],
            "未超上限手册不应触发体积提示",
        )

    def test_plan_file_written(self):
        """场景9: 计划文件 manual-update-plan.md 落盘。"""
        self._make_manual()
        self._patch_hermes()
        result = self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        plan_path = Path(result.get("plan_path", ""))
        self.assert_true(plan_path.exists(), f"计划文件应落盘: {plan_path}")
        content = plan_path.read_text(encoding="utf-8")
        self.assert_true("[add] 泵浦探测序列" in content, "计划文件应含动作明细")

    def test_first_round_no_manual(self):
        """场景10: 手册不存在（首轮）→ 正常走两阶段，阶段1 提示首轮创建。"""
        manual = self.prop_dir / "03_method" / "method-manual.md"
        if manual.exists():
            manual.unlink()  # 清掉前序用例残留
        self._patch_hermes()
        result = self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(result.get("success"), f"首轮应成功: {result}")
        self.assert_true(
            "首轮创建" in self.calls[0]["prompt"],
            "手册不存在时阶段1应提示首轮创建",
        )

    def _seed_params(self):
        """v7.3.27: 播种口径表（4.19 eV 禁用旧值为例）。"""
        params = self.prop_dir / "04_proposal" / "params.json"
        params.write_text(json.dumps({
            "entries": [{
                "key": "MgO KP 模型带隙口径",
                "canonical": "KP 两带模型带隙位于布里渊区边缘约 13.6 eV，非 Γ 点",
                "stale_patterns": [r"4\.19 eV"],
                "note": "",
            }]
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_params_stale_hits_injected(self):
        """场景11（v7.3.27）: 手册写入侧接入口径表——计划与逐节执行 prompt
        都必须含 canonical 值与全册禁用旧值命中行号。"""
        manual = self.prop_dir / "03_method" / "method-manual.md"
        manual.parent.mkdir(parents=True, exist_ok=True)
        manual.write_text(
            "# 方法学手册\n\n| 0.8 | MgO 4.19 eV |\n" + "正文\n" * 200,
            encoding="utf-8",
        )
        self._seed_params()
        self._patch_hermes()
        self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(len(self.calls) >= 2, "应有规划 + 执行调用")
        plan_prompt = self.calls[0]["prompt"]
        self.assert_true(
            "手册口径旧值命中" in plan_prompt, "计划 prompt 应含零 LLM 命中块"
        )
        self.assert_true(
            "13.6 eV" in plan_prompt, "计划 prompt 应含 canonical 值"
        )
        self.assert_true(
            "- L3｜" in plan_prompt and "命中 `4.19 eV`" in plan_prompt,
            "命中块应给出命中行号（本例 L3）与命中原文",
        )
        for c in self.calls[1:]:
            self.assert_true(
                "手册口径旧值命中" in c["prompt"],
                "逐节执行 prompt 也应含命中块（避免只改点名行）",
            )

    def test_compress_cap_uses_chars(self):
        """场景12（v7.3.27）: 体积阈值按字符数而非 UTF-8 字节——3 万中文字
        （约 9 万字节）不应触发体积提示；7 万字符可以。"""
        manual = self.prop_dir / "03_method" / "method-manual.md"
        manual.parent.mkdir(parents=True, exist_ok=True)
        manual.write_text("# 方法学手册\n\n" + "研" * 30000, encoding="utf-8")
        self._patch_hermes()
        self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(
            "体积提示" not in self.calls[0]["prompt"],
            "3 万中文字（9 万字节）不应触发体积提示",
        )
        # 恢复 7 万字符场景
        self.calls.clear()
        manual.write_text("# 方法学手册\n\n" + "研" * 70000, encoding="utf-8")
        self._patch_hermes()
        self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(
            "体积提示" in self.calls[0]["prompt"],
            "7 万字符应触发体积提示",
        )

    def test_full_scheme_injected(self):
        """场景13（v7.3.27）: 方案输入不再截断 8000 字符——offset 9000 的
        判据标记必须出现在计划 prompt 中。"""
        sections = self.prop_dir / "04_proposal" / "sections"
        sections.mkdir(parents=True, exist_ok=True)
        marker = "▣末端判据标记▣"
        (sections / "scheme.md").write_text(
            "# 研究方案\n\n" + "甲" * 9000 + "\n" + marker, encoding="utf-8"
        )
        self._patch_hermes()
        self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        self.assert_true(
            marker in self.calls[0]["prompt"],
            "方案 8000 字符之后的判据应进入计划 prompt",
        )

    def test_toc_injected_in_plan_prompt(self):
        """场景14（v7.3.32）: 阶段1 注入全量目录（标题+行范围+字符数）。"""
        manual = self.prop_dir / "03_method" / "method-manual.md"
        manual.parent.mkdir(parents=True, exist_ok=True)
        manual.write_text(
            "# 方法学手册\n\n"
            "### 2.3 反常电流\n\n" + "甲" * 300 + "\n\n"
            "### 2.4 缺陷耦合\n\n" + "乙" * 300 + "\n\n"
            "### 4.1 平台基线\n\n" + "丙" * 1200 + "\n",
            encoding="utf-8",
        )
        self._patch_hermes()
        self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        prompt = self.calls[0]["prompt"]
        self.assert_true("目录（共 3 节" in prompt, "阶段1 应注入全量目录")
        self.assert_true("L" in prompt and "字符）" in prompt, "目录应含行范围与字符数")
        for h in ("### 2.3 反常电流", "### 2.4 缺陷耦合", "### 4.1 平台基线"):
            self.assert_true(h in prompt, f"目录应含小节标题 {h}")
        self.assert_true("头部节选" not in prompt, "不应再只喂头部节选")

    def test_section_range_injected_in_exec_prompt(self):
        """场景15（v7.3.32）: 阶段2 注入目标节行范围与原文，强制单节边界。"""
        manual = self.prop_dir / "03_method" / "method-manual.md"
        manual.parent.mkdir(parents=True, exist_ok=True)
        manual.write_text(
            "# 方法学手册\n\n"
            "### 泵浦探测序列\n\n" + "甲" * 200 + "\n\n"
            "### 数据采集\n\n" + "乙" * 200 + "\n\n"
            "### 理论模型对比\n\n" + "丙" * 200 + "\n\n"
            "### 样品制备\n\n" + "丁" * 200 + "\n",
            encoding="utf-8",
        )
        self._patch_hermes()
        self.lc._run_update_method_manual_step(self.pid, {"round": 1})
        prompts = [c["prompt"] for c in self.calls[1:]]
        self.assert_true(prompts, "应有阶段2执行调用")
        for p in prompts:
            self.assert_true("目标节行范围" in p, "执行 prompt 应含行范围")
            self.assert_true("写入边界（强制）" in p, "执行 prompt 应含写入边界")
            self.assert_true("禁止整册重写" in p, "执行 prompt 应禁止整册重写")

    def test_out_of_range_detected(self):
        """场景16（v7.3.32）: 行级 diff 能识别目标节之外的改动。"""
        executor_mod = importlib.import_module("lifecycle.executor")
        before = "l1\nl2\nl3\nl4\nl5\nl6"
        after_in = "l1\nl2\nX3\nl4\nl5\nl6"
        after_out = "Y1\nl2\nl3\nl4\nl5\nl6"
        self.assert_eq(
            executor_mod._manual_out_of_range(before, after_in, 3, 4), 0,
            "节内改动不应计为越界",
        )
        self.assert_true(
            executor_mod._manual_out_of_range(before, after_out, 3, 4) > 0,
            "节外改动应计为越界",
        )

    def test_section_brief_truncates(self):
        """场景17（v7.3.32）: 单节超 8000 字符时只给首尾各半并标注省略。"""
        executor_mod = importlib.import_module("lifecycle.executor")
        body = "头" * 5000 + "尾" * 5000
        brief = executor_mod._manual_section_brief(body, cap=8000)
        self.assert_true(len(brief) < len(body), "超限单节应被裁剪")
        self.assert_true("中段已省略" in brief, "裁剪结果应标注省略")
        self.assert_true(brief.startswith("头"), "应保留节首")
        self.assert_true(brief.endswith("尾"), "应保留节尾")
        short = executor_mod._manual_section_brief("短节", cap=8000)
        self.assert_eq(short, "短节", "未超限小节应原样返回")

    def test_subsection_belongs_to_parent_section(self):
        """场景18（v7.3.33 / BUG-42）: #### 子节归属父节，不得提前截断。

        生产实证（houston 手册）：`### 2.11 目标一判据协议` 下挂 4 个
        #### 子节（2.11.1~2.11.4，判据正文），v7.3.32 的实现把「下一个
        任意级标题」当节边界 → 父节只拿到 333 字符（标题+首段），
        真正要改的判据正文全在授权范围外。正确语义：节边界 = 下一个
        **同级或更高级**标题。
        """
        executor_mod = importlib.import_module("lifecycle.executor")
        text = (
            "# 方法学手册\n\n"
            "### 2.11 目标一判据协议\n\n"
            "父节导语。\n\n"
            "#### 2.11.1 谱形一致性判据\n\n"
            "子节正文甲。\n\n"
            "#### 2.11.2 通道份额判据\n\n"
            "子节正文乙。\n\n"
            "### 2.12 下一节\n\n"
            "下一节正文。\n"
        )
        sl = executor_mod._manual_section_slice(text, "### 2.11 目标一判据协议")
        self.assert_true(sl is not None, "应命中父节")
        self.assert_true("#### 2.11.1 谱形一致性判据" in sl["body"],
                        "父节切片应包含 #### 子节标题")
        self.assert_true("子节正文甲" in sl["body"],
                        "父节切片应包含子节正文")
        self.assert_true("子节正文乙" in sl["body"],
                        "父节切片应包含第二个子节正文")
        self.assert_true("下一节正文" not in sl["body"],
                        "父节切片不应越过下一个同级标题")
        # 范围核算：end 为「末行 1-based 序号」，下一个同级标题在 lines[end]
        lines = text.split("\n")
        next_heading = lines[sl["end"]]
        self.assert_true(next_heading.startswith("### 2.12"),
                        f"节边界应停在下一个同级标题前，实际为 {next_heading!r}")

    def test_toc_char_count_includes_subsections(self):
        """场景19（v7.3.33 / BUG-42）: 目录字符数含子节，planner 不被失真体量误导。"""
        executor_mod = importlib.import_module("lifecycle.executor")
        text = (
            "# 方法学手册\n\n"
            "## 2. 第二层\n\n"
            "### 2.11 目标一判据协议\n\n"
            "父节导语。\n\n"
            "#### 2.11.1 子判据\n\n"
            + "子节正文。" * 200 + "\n\n"
            "### 2.12 下一节\n\n"
            "下一节。\n"
        )
        toc = executor_mod._manual_toc(text)
        by_title = {t["title"]: t for t in toc}
        parent = by_title.get("### 2.11 目标一判据协议")
        self.assert_true(parent is not None, "目录应含父节")
        # 父节字符数必须覆盖子节正文（子节 800 字符 + 父节导语）
        self.assert_true(parent["chars"] > 700,
                        f"父节字符数应含子节正文，实际 {parent['chars']}")
        top = by_title.get("## 2. 第二层")
        self.assert_true(top is not None, "目录应含二级节")
        self.assert_true(top["chars"] > parent["chars"],
                        "二级节字符数应大于其子节（口径统一后的嵌套关系）")

    def run_tests(self):
        self.test_two_phase_call_sequence()
        self.test_timeouts_reduced()
        self.test_plan_parse_variants()
        self.test_empty_plan_legal_skip()
        self.test_phase1_failure()
        self.test_phase2_partial_failure()
        self.test_phase2_all_failure()
        self.test_overcap_manual_requires_compress()
        self.test_plan_file_written()
        self.test_first_round_no_manual()
        self.test_params_stale_hits_injected()
        self.test_compress_cap_uses_chars()
        self.test_full_scheme_injected()
        self.test_toc_injected_in_plan_prompt()
        self.test_section_range_injected_in_exec_prompt()
        self.test_out_of_range_detected()
        self.test_section_brief_truncates()
        self.test_subsection_belongs_to_parent_section()
        self.test_toc_char_count_includes_subsections()


if __name__ == "__main__":
    suite = MethodManualTwoPhaseTests()
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
