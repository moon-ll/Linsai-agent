#!/usr/bin/env python3
"""
test_mechanism_hardening.py — v6.9.28 对抗/自优化机制加固回归测试

覆盖三个修复点：
    1. 锚点绑定顺序修复（references 轮跳过 + 绑定移至专用计分之后）
       - references 评审不受锚点结论 cap（口径为 rigor/completeness）
       - 源码级顺序守卫：references 专用计分代码段必须先于锚点绑定段
    2. writer 顽固升级（连续两轮负分 + 表面修改评价 → 强制逐条响应块）
       - 触发：最近 2 条 history 均负 delta 且 reason 命中表面修改关键词
       - 不触发：单轮负分 / 无关键词 / history 不足 2 条
       - 触发后：枚举 critic 报告 critical/high 问题行；报告缺失时输出兜底要求
    3. prompt_optimizer 语义去重（v6.9.25 合并历史规则后防重复追加）
       - 改写措辞的同义建议（占位符规则 vs SOUL 运行纪律正文）→ 命中率 ≥0.6
       - 全新内容 → 命中率 <0.6，正常追加
       - _apply_suggestion 对同义建议跳过写入（文件不变、不备份）

背景：08-20 机制体检发现——moire R2/R3 writer 连续表面修改仅罚不改（修复率
1/7）；锚点绑定在 references 专用计分之前执行被覆盖；v6.9.25 手工合并
auto-opt 规则后 fingerprint 7 天窗口过期会重复追加同义规则。

注意：不调用 LLM，运行于隔离临时目录。

用法示例：
    python3 scripts/tests/test_mechanism_hardening.py
"""

import sys
import json
import shutil
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root


def _load_optimize_module(tmp_root: Path):
    """在隔离目录下加载 proposal_lifecycle.optimize 并返回 OptimizeMixin。"""
    for mod_name in ["proposal_lifecycle.optimize", "proposal_lifecycle"]:
        if mod_name in sys.modules:
            del sys.modules[mod_name]
    importlib.import_module("proposal_lifecycle.optimize")
    import proposal_lifecycle as _pl
    _pl.PROJECT_ROOT = tmp_root
    from proposal_lifecycle.optimize import OptimizeMixin

    class _Fake(OptimizeMixin):
        def __init__(self):
            pass

    return _Fake()


class AnchorOrderTests(TestSuite):
    """1：锚点绑定顺序修复。"""

    def __init__(self):
        super().__init__("锚点绑定顺序修复测试（v6.9.28-1）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        self._opt = _load_optimize_module(self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        opt = self._opt

        # 1.1 references 口径不受锚点结论影响——专用计分独立于绑定函数。
        #     模拟 references 轮的实际数值流：rigor/completeness 平均。
        ref_dims = {"rigor": 0.58, "completeness": 0.66}
        ref_score = sum(ref_dims.values()) / len(ref_dims)
        self.assert_eq(round(ref_score, 2), 0.62, "references 专用计分 = (rigor+completeness)/2")

        # 1.2 差距明显结论若错误绑定 references 分（0.62 < 0.84）虽无实害，
        #     但口径错误；验证绑定函数对纯 references 维度无 expression 可 cap
        dims = {"rigor": 0.58, "completeness": 0.66}
        out = opt._apply_anchor_conclusion_binding(
            "p1", "锚点对比结论：差距明显", dims, ref_score, "general")
        self.assert_eq(dims["rigor"], 0.58, "绑定不应修改 rigor")
        self.assert_eq(out, ref_score, "无 expression 维度时绑定不应改综合分")

        # 1.3 源码级顺序守卫：references 专用计分段必须先于锚点绑定段出现
        #     （v6.9.28 前绑定在前者的赋值下被覆盖，references 轮形同虚设）
        src = Path(opt.__module__.replace(".", "/") + ".py")
        if not src.exists():
            src = Path(__file__).parent.parent / "proposal_lifecycle" / "optimize.py"
        text = src.read_text(encoding="utf-8")
        pos_ref = text.find("references 评审专用计分")
        pos_bind = text.find("锚点对比结论与评分档位强制绑定——范本锚点成为分数锚")
        self.assert_true(pos_ref > 0, "应存在 references 专用计分段")
        self.assert_true(pos_bind > 0, "应存在锚点绑定段")
        self.assert_true(
            pos_ref < pos_bind,
            "references 专用计分必须先于锚点绑定（防覆盖回归）",
        )
        # 1.4 references 轮跳过绑定的守卫注释存在（防误删）
        self.assert_true(
            "references 评审跳过绑定" in text,
            "references 轮跳过绑定的注释守卫应存在",
        )


class WriterEscalationTests(TestSuite):
    """2：writer 顽固升级机制。"""

    def __init__(self):
        super().__init__("writer 顽固升级测试（v6.9.28-2）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "05_review").mkdir(parents=True, exist_ok=True)
        self._opt = _load_optimize_module(self.tmp_root)
        self._report = self.tmp_root / "05_review" / "critic-round-3.md"
        self._report.write_text(
            "# 对抗评审报告（第3轮）\n"
            "### [critical] C1 — 编号 [12] 重复\n- 位置：references.md\n"
            "### [critical] C3 — [22] 作者署名错位\n- 位置：references.md\n"
            "### [high] H1 — [9] 标题拼写错误\n- 位置：references.md\n"
            "### [medium] M1 — 格式建议\n",
            encoding="utf-8")

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_scores(self, history):
        (self.tmp_root / "memory" / "agent-scores.json").write_text(
            json.dumps({"writer": {"score": 57.3, "history": history},
                        "critic": {"score": 97.0, "history": []}},
                       ensure_ascii=False),
            encoding="utf-8")

    def run_tests(self):
        opt = self._opt

        # 2.1 触发：连续两轮负分 + 表面修改评价 → 升级块含问题清单
        self._write_scores([
            {"delta": -16.9, "reason": "writer-r22 diff 仅 5 行，正文零改动", "at": "2026-08-20T04:19:52Z"},
            {"delta": -8.5, "reason": "writer 未修复 C3 critical 等问题", "at": "2026-08-20T14:21:54Z"},
        ])
        block = opt._build_writer_escalation_block(str(self._report))
        self.assert_true("顽固升级" in block, "触发时应输出顽固升级警告")
        self.assert_true("C1" in block and "C3" in block, "应枚举 critical 问题行")
        self.assert_true("H1" in block, "应枚举 high 问题行")
        self.assert_true("M1" not in block, "medium 问题不应枚举（聚焦 critical/high）")
        self.assert_true("问题→处理结果" in block, "应强制要求输出对照表")

        # 2.2 不触发：最近一轮 delta 为正
        self._write_scores([
            {"delta": -8.5, "reason": "未修复问题", "at": "2026-08-20T04:00:00Z"},
            {"delta": 4.4, "reason": "实质性参考文献工作", "at": "2026-08-20T14:00:00Z"},
        ])
        self.assert_eq(opt._build_writer_escalation_block(str(self._report)), "",
                       "最近一轮正分不应触发")

        # 2.3 不触发：负分但 reason 无表面修改关键词
        self._write_scores([
            {"delta": -3.0, "reason": "评分口径偏差", "at": "2026-08-20T04:00:00Z"},
            {"delta": -2.0, "reason": "格式问题", "at": "2026-08-20T14:00:00Z"},
        ])
        self.assert_eq(opt._build_writer_escalation_block(str(self._report)), "",
                       "无表面修改关键词不应触发")

        # 2.4 不触发：history 不足 2 条
        self._write_scores([{"delta": -10.0, "reason": "未修复 critical", "at": "2026-08-20T04:00:00Z"}])
        self.assert_eq(opt._build_writer_escalation_block(str(self._report)), "",
                       "history 不足 2 条不应触发")

        # 2.5 触发但报告缺失 → 兜底要求（无问题行但有对照表要求）
        self._write_scores([
            {"delta": -16.9, "reason": "零改动", "at": "2026-08-20T04:00:00Z"},
            {"delta": -8.5, "reason": "未处理 critic 问题", "at": "2026-08-20T14:00:00Z"},
        ])
        block2 = opt._build_writer_escalation_block(str(self.tmp_root / "nonexistent.md"))
        self.assert_true("顽固升级" in block2, "报告缺失也应触发升级警告")
        self.assert_true("问题→处理结果" in block2, "报告缺失也应要求对照表")
        self.assert_true("C1" not in block2, "报告缺失时不应有具体问题行")

        # 2.6 agent-scores.json 缺失 → 静默返回空
        (self.tmp_root / "memory" / "agent-scores.json").unlink()
        self.assert_eq(opt._build_writer_escalation_block(str(self._report)), "",
                       "agent-scores 缺失应返回空串")


class SemanticDedupTests(TestSuite):
    """3：prompt_optimizer 语义去重。"""

    SOUL_BODY = (
        "# Writer Profile\n\n## 运行纪律\n\n"
        "3. **禁止占位符**：不得提交\"待补充/TBD/待核验/XXX\"等占位内容；"
        "信息不足处改写为不依赖该信息的表述，或明确标注\"需要 researcher 补充文献\""
        "并给出替代论证。\n"
    )
    PARAPHRASED_RULE = (
        "\n<!--auto-opt:start:ps-x:2026-08-20T00:00:00Z:占位符|待.*核验|TBD-->\n"
        "## 自动优化规则（评分分析 2 次证据）\n\n"
        "提交前全文检索'待补充/TBD/待核验/XXX'，命中处一律改写为不依赖该信息的"
        "完整表述，或标注'需要 researcher 补充'并给出替代论证。\n"
        "<!--auto-opt:end:ps-x-->\n"
    )
    NEW_RULE = (
        "\n## 自动优化规则\n\n"
        "每张表格必须有表题，表题编号与正文引用一致，禁止无题表格。\n"
    )

    def __init__(self):
        super().__init__("语义去重测试（v6.9.28-3）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / ".hermes" / "profiles" / "writer").mkdir(parents=True, exist_ok=True)
        self._soul = self.tmp_root / ".hermes" / "profiles" / "writer" / "SOUL.md"
        self._soul.write_text(self.SOUL_BODY, encoding="utf-8")

        for mod_name in ["prompt_optimizer"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        self.po = importlib.import_module("prompt_optimizer")
        patch_module_root("prompt_optimizer", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        po = self.po

        # 3.1 同义改写 → 命中率 ≥0.6
        ratio = po._semantic_overlap_ratio(self.PARAPHRASED_RULE.strip(), self.SOUL_BODY)
        self.assert_true(ratio >= 0.6,
                         f"同义规则命中率应 ≥0.6，实际 {ratio:.0%}")

        # 3.2 全新内容 → 命中率 <0.6
        ratio2 = po._semantic_overlap_ratio(self.NEW_RULE.strip(), self.SOUL_BODY)
        self.assert_true(ratio2 < 0.6,
                         f"全新规则命中率应 <0.6，实际 {ratio2:.0%}")

        # 3.3 完全相同 → 1.0（精确匹配路径之上仍兼容）
        ratio3 = po._semantic_overlap_ratio(self.SOUL_BODY, self.SOUL_BODY)
        self.assert_eq(ratio3, 1.0, "完全相同内容命中率为 1.0")

        # 3.4 _apply_suggestion：同义建议跳过写入（文件不变）
        suggestion = {
            "target_file": str(self._soul),
            "target_profile": "writer",
            "content": self.PARAPHRASED_RULE,
        }
        before = self._soul.read_text(encoding="utf-8")
        ok = po._apply_suggestion(suggestion)
        after = self._soul.read_text(encoding="utf-8")
        self.assert_true(ok, "同义建议应返回 True（视为已应用）")
        self.assert_eq(after, before, "同义建议不应写入文件")
        self.assert_true(
            "semantically_present" in str(suggestion.get("apply_note", "")),
            "应记录 semantically_present 注记",
        )

        # 3.5 _apply_suggestion：全新内容正常追加
        suggestion2 = {
            "target_file": str(self._soul),
            "target_profile": "writer",
            "content": self.NEW_RULE,
        }
        ok2 = po._apply_suggestion(suggestion2)
        after2 = self._soul.read_text(encoding="utf-8")
        self.assert_true(ok2, "全新建议应成功应用")
        self.assert_true("表题编号与正文引用一致" in after2, "全新建议应写入文件")


class ExecutorPathTests(TestSuite):
    """4：executor.py 线上路径机制守护（v6.9.30）。

    背景：v6.9.28 的锚点绑定/AI 检测修复只落在 optimize.py（微调度器
    未调用的死代码），线上实际执行路径 executor.py 缺失，导致
    'template=score anchor' 机制整体失效。本套件做源码级守卫，
    防止移植逻辑再次只修死代码。
    """

    def __init__(self):
        super().__init__("executor 线上路径机制守护测试（v6.9.30-4）")

    def setup(self):
        self.tmp_root = create_isolated_env()
        self._exec = Path(__file__).parent.parent / "lifecycle" / "executor.py"
        self._text = self._exec.read_text(encoding="utf-8")
        self._opt_src = Path(__file__).parent.parent / "proposal_lifecycle" / "optimize.py"
        self._opt_text = self._opt_src.read_text(encoding="utf-8")

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        text = self._text

        # 4.1 critic 步骤必须先运行程序化 AI 检测（产出表达天花板）
        pos_critic_ai = text.find("def _run_critic_step")
        pos_ai_detect = text.find("ai_check = self._detect_ai_patterns")
        self.assert_true(pos_critic_ai > 0, "应存在 _run_critic_step")
        self.assert_true(pos_ai_detect > 0, "应存在 AI 检测调用")
        self.assert_true(
            pos_critic_ai < pos_ai_detect,
            "AI 检测应位于 _run_critic_step 内（critic 之前）",
        )

        # 4.2 AI 检测结果必须传入 critic（ai_check_result 参数）
        self.assert_true(
            "ai_check_result=ai_check" in text,
            "critic 调用应传入 ai_check_result",
        )

        # 4.3 writer 步骤必须应用锚点绑定（references 轮跳过）
        self.assert_true(
            "self._apply_anchor_conclusion_binding" in text,
            "writer 步骤应调用锚点绑定",
        )
        pos_ref_score = text.find("references 评审专用计分")
        pos_bind = text.find("锚点对比结论与评分档位强制绑定")
        self.assert_true(pos_ref_score > 0, "executor 应存在 references 专用计分段")
        self.assert_true(pos_bind > 0, "executor 应存在锚点绑定段")
        self.assert_true(
            pos_ref_score < pos_bind,
            "executor 中 references 专用计分必须先于锚点绑定（防覆盖回归）",
        )
        self.assert_true(
            'if section_key != "references":' in text,
            "executor 应存在 references 轮跳过绑定的守卫",
        )

        # 4.4 score_history 必须记录 ai_ceiling / ai_top_issues / anchor_conclusion
        self.assert_true('"ai_ceiling"' in text, "score_history 应含 ai_ceiling")
        self.assert_true('"ai_top_issues"' in text, "score_history 应含 ai_top_issues")
        self.assert_true('"anchor_conclusion"' in text, "score_history 应含 anchor_conclusion")

        # 4.5 程序化天花板强制执行（表达分 + 综合分 cap）
        self.assert_true(
            "dim_scores[\"expression\"] = ceiling" in text,
            "executor 应强制表达分 cap 至 AI 天花板",
        )
        self.assert_true(
            "overall_ceiling" in text,
            "executor 应存在综合分天花板",
        )

        # 4.6 references 评审超时 cap 必须 ≥1200s（v6.9.31）
        #     背景：references 输入含 references.md + 三个正文章节（约 106KB），
        #     MiniMax 慢 API 下主 critic 单章都要 1155s——600s cap 导致
        #     order-parameter r7 references-critic 连续 3 次超时卡死。
        opt_text = self._opt_text
        self.assert_true(
            "min(timeout, 1200)" in opt_text,
            "references 评审超时 cap 应为 1200s（v6.9.31 修复）",
        )
        self.assert_true(
            "min(timeout, 600)" not in opt_text,
            "references 评审不应再被 600s cap 限制",
        )


def main():
    from test_runner import print_report

    suites = []
    for cls in (AnchorOrderTests, WriterEscalationTests, SemanticDedupTests, ExecutorPathTests):
        s = cls()
        s.setup()
        s.run_tests()
        s.teardown()
        suites.append(s)
    print_report(suites)


if __name__ == "__main__":
    main()
