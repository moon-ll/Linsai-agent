#!/usr/bin/env python3
"""
test_feedback_injection.py — 审核反馈注入闭环回归测试（v6.9.26）

覆盖两个历史缺陷（反馈闭环自 v6.8.17 引入起从未生效）：
    1. 门闩错误：load_review_feedback_for_optimization 以 review_history
       为门闩，但该字段仅在带 session_id 的 Web 审核提交时写入——CLI/
       脚本提交（无 session）不写，反馈永远不注入 critic/writer prompt。
    2. 长度判断永假：旧判断 len(lines) > 2 恒为 False（lines 最多含
       header + 1 个反馈共 2 个元素），函数恒返回空串。

修复：门闩改为 human_feedback_count；长度判断改为 len(lines) > 1。

注意：
    本测试不调用 hermes/LLM，仅验证注入函数的纯逻辑。
"""

import sys
import shutil
import json
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root
import importlib


class FeedbackInjectionTests(TestSuite):
    def __init__(self):
        super().__init__("审核反馈注入闭环测试（v6.9.26）")
        self.tmp_root = None
        self.fa_mod = None

    def setup(self):
        self.tmp_root = create_isolated_env()

        for mod_name in ["proposal_lifecycle.feedback_archive", "proposal_lifecycle"]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        self.fa_mod = importlib.import_module("proposal_lifecycle.feedback_archive")
        patch_module_root("proposal_lifecycle.feedback_archive", self.tmp_root)

        # 函数体内部 `from proposal_lifecycle.constants import PROPOSALS_ROOT`
        # 在调用时取模块属性，需同步 patch constants 模块
        from proposal_lifecycle import constants as plc
        plc.PROPOSALS_ROOT = self.tmp_root / "research_proposals"
        self.constants_mod = plc

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_feedback(self, proposal_id: str, num: int, text: str):
        fb_dir = self.tmp_root / "research_proposals" / "optimizing" / proposal_id / "06_feedback"
        fb_dir.mkdir(parents=True, exist_ok=True)
        (fb_dir / f"feedback-{num}-raw.md").write_text(text, encoding="utf-8")

    def _write_structured(self, proposal_id: str, num: int, data):
        fb_dir = self.tmp_root / "research_proposals" / "optimizing" / proposal_id / "06_feedback"
        fb_dir.mkdir(parents=True, exist_ok=True)
        (fb_dir / f"feedback-{num}-structured.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def run_tests(self):
        load = self.fa_mod.load_review_feedback_for_optimization
        pid = "test-proposal-001"

        # 1. 门闩修复：无 review_history 但 feedback_count>0 + raw 文件 → 注入
        self._write_feedback(pid, 1, "## 审核退回意见\n\n参考文献必须修复至 0.80 以上。")
        state = {"proposal_id": pid, "human_feedback_count": 1, "review_history": []}
        block = load(state)
        self.assert_true(len(block) > 50, "CLI 提交（无 review_history）也能注入反馈")
        self.assert_true("参考文献必须修复" in block, "注入块包含反馈正文")

        # 2. 长度判断修复：单条反馈（lines=2）非空返回
        self.assert_true("历史人工审核反馈" in block, "注入块含标题头")

        # 3. feedback_count=0 → 空串
        self.assert_eq(load({"proposal_id": pid, "human_feedback_count": 0}), "",
                       "无反馈记录返回空串")

        # 4. 反馈文件缺失 → 空串（目录在但文件不在）
        block4 = load({"proposal_id": pid, "human_feedback_count": 5,
                       "review_history": [{"session_id": "s"}]})
        self.assert_eq(block4, "", "反馈文件缺失时返回空串不崩溃")

        # 5. 审核对话摘要提取路径：含 '## 审核对话摘要' 时只注入摘要段
        pid2 = "test-proposal-002"
        self._write_feedback(
            pid2, 2,
            "# 人工审核反馈\n前置内容不应注入\n\n## 审核对话摘要\n摘要正文：句长超标是主要扣分项。\n",
        )
        block5 = load({"proposal_id": pid2, "human_feedback_count": 2})
        self.assert_true("句长超标" in block5, "摘要路径注入摘要正文")
        self.assert_true("前置内容不应注入" not in block5, "摘要路径排除摘要前内容")

        # 6. 结构化派活超时参数：writer 平均 350s+，120s 必超时
        src = Path(self.fa_mod.__file__).read_text(encoding="utf-8")
        self.assert_true(
            'timeout=480' in src and 'timeout=120' not in src.split("_structure_feedback")[1][:3000],
            "_structure_feedback 派 writer 超时 ≥480s（旧 120s 必超时）",
        )

        # 7. v6.9.42 兜底回退：raw 为无信息通用话术 + structured 存在
        #    → 注入结构化意见渲染（bsv 2026-08-23 实证：raw 155B 兜底、
        #    structured 8.6KB 实质意见，旧逻辑注入零信息）
        pid3 = "test-proposal-003"
        self._write_feedback(
            pid3, 3,
            "# 人工审核反馈（第3次）\n\n**时间**: x\n**结论**: major_revision\n\n---\n\n"
            "用户审核不通过，请根据审核意见修改。",
        )
        self._write_structured(pid3, 3, {
            "verdict": "major_revision",
            "overall_comment": "物理基线叙事不足",
            "issues": [
                {"section": "立项依据", "severity": "high",
                 "description": "1.2.2 节是数据堆砌缺叙事",
                 "instruction": "每个数据点嵌入一句话并点出对 Q1 的意义"},
                {"section": "研究方案", "severity": "critical",
                 "description": "技术路线与科学问题脱节",
                 "instruction": "补 Q1-Q4 映射表"},
            ],
        })
        block7 = load({"proposal_id": pid3, "human_feedback_count": 3})
        self.assert_true("结构化审核意见" in block7, "兜底 raw 时注入结构化渲染块")
        self.assert_true("数据堆砌缺叙事" in block7, "结构化渲染含 issue 描述")
        self.assert_true("补 Q1-Q4 映射表" in block7, "结构化渲染含 issue 指令")
        self.assert_true("[critical]（研究方案）" in block7, "渲染保留严重度与章节")
        self.assert_true("用户审核不通过，请根据审核意见修改" not in block7,
                         "通用兜底话术不再进入注入块")

        # 8. raw 有实质内容时优先 raw（structured 存在也不抢位）
        pid4 = "test-proposal-004"
        self._write_feedback(pid4, 1, "## 审核退回意见\n\n参考文献排序必须按出现顺序修复。")
        self._write_structured(pid4, 1, {
            "verdict": "major_revision",
            "overall_comment": "结构化兜底不应出现",
            "issues": [{"severity": "low", "description": "不应注入此条"}],
        })
        block8 = load({"proposal_id": pid4, "human_feedback_count": 1})
        self.assert_true("参考文献排序" in block8 and "不应注入此条" not in block8,
                         "实质 raw 优先，结构化仅作兜底")

        # 9. 兜底 raw + 无 structured → 保持旧行为（注入 raw 不崩溃）
        pid5 = "test-proposal-005"
        self._write_feedback(
            pid5, 2,
            "# 人工审核反馈（第2次）\n\n**结论**: major_revision\n\n---\n\n"
            "用户审核不通过，请根据审核意见修改。",
        )
        block9 = load({"proposal_id": pid5, "human_feedback_count": 2})
        self.assert_true(block9 != "" and "历史人工审核反馈" in block9,
                         "无 structured 兜底时维持旧行为非空返回")


if __name__ == "__main__":
    suite = FeedbackInjectionTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    s = suite.summary()
    for r in s["results"]:
        if not r.passed:
            print(f"  ✗ {r.name}: {r.msg}")
    print(f"通过 {s['passed']} / 失败 {s['failed']}")
    sys.exit(1 if s["failed"] else 0)
