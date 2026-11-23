#!/usr/bin/env python3
"""v7.2.77 评审团 skill 化对齐测试（双通道收敛 + 编排契约沉淀）。

覆盖：
1. quality-review SKILL.md 第五节收敛为「评审团双通道」（脚本编排=
   无人值守正轨，v7.2.77 用户裁决），六节（角色/findings 契约）与
   七节（修改/复核纪律）存在且关键内容齐备
2. panel_review._role_skill_block 注入矩阵：researcher/critic/reviewer
   按角色注四节/六节/一之二/nsfc-writing 十节，块非空
3. 旧硬编码 role_brief 已从脚本删除（skill 是单一真相源）
4. writer/verify 阶段 prompt 走 skill 注入（源码含 inject_block 调用）

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_panel_v7276.py
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite, REAL_ROOT


class PanelV7276Tests(TestSuite):
    def __init__(self):
        super().__init__("v7.2.77 评审团 skill 化对齐测试")
        self.tmp_root = None

    def assert_true(self, condition, name, msg: str = "") -> bool:
        # 本套件调用习惯为 (名称, 条件)，此处翻转对齐基类签名
        # （调用形如 assert_true("描述", <bool 表达式>)，字符串名不可靠
        # 作条件，凡 str 一律视为名称、真实条件取第二位）。
        if isinstance(condition, str):
            condition, name = name, condition
        return super().assert_true(bool(condition), str(name), msg)

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from skill_loader import load_skill, extract_section, inject_block
        skill_text = load_skill("quality-review")

        # ================================================================
        # 1. 第五节为执行者无关流程契约（v7.2.81 修正 v7.2.77 双通道表述）
        # ================================================================
        sec5 = extract_section(skill_text, "五、评审团 = 执行者无关的流程契约")
        self.assert_true(
            "第五节声明评审团为执行者无关流程契约（不绑定模型）",
            bool(sec5) and "不绑定任何模型" in sec5,
        )
        self.assert_true(
            "第五节声明引擎亲审为正轨",
            "引擎亲审（正轨" in sec5,
        )
        self.assert_true(
            "第五节将脚本 hermes 编排降为托底执行器（预审性质）",
            "无人值守托底执行器" in sec5 and "自动化预审" in sec5,
        )
        self.assert_true(
            "旧「直接亲审模式」单轨标题已移除",
            "五、评审团直接亲审模式" not in skill_text,
        )

        # ================================================================
        # 2. 六节：角色职责 + findings 输出契约
        # ================================================================
        sec6 = extract_section(skill_text, "六、评审团角色与findings契约")
        self.assert_true(
            "六节存在",
            bool(sec6),
        )
        for kw in ["researcher（科学内容审稿人）", "critic（表达红线审稿人）",
                   "reviewer（评审标准审稿人）", "findings 输出契约"]:
            self.assert_true(
                f"六节含关键内容: {kw}",
                kw in sec6,
            )

        # ================================================================
        # 3. 七节：writer 修改纪律（引用红线/口径表/异源）+ verify 判定
        # ================================================================
        sec7 = extract_section(skill_text, "七、评审团修改与复核纪律")
        self.assert_true(
            "七节存在",
            bool(sec7),
        )
        self.assert_true(
            "七节含引用三源对照零容忍红线（对齐 optimize.py v7.2.19）",
            "零容忍红线" in sec7 and "lit-gap-*.md" in sec7
            and "宁可少一条，不可编一条" in sec7,
        )
        self.assert_true(
            "七节含口径表一致性纪律",
            "params.json" in sec7,
        )
        self.assert_true(
            "七节含评委与 writer 异源纪律（PoLL 自偏好启示）",
            "异源" in sec7 and "自偏好" in sec7,
        )
        self.assert_true(
            "七节含 verify 判定格式（复核结论: 通过/需返工）",
            "复核结论: 通过" in sec7 and "复核结论: 需返工" in sec7,
        )

        # ================================================================
        # 4. 一之二节存在（v7.2.17 校准纪律，注入 reviewer/verify）
        # ================================================================
        sec12 = extract_section(skill_text, "一之二、分数锚点校准纪律")
        self.assert_true(
            "一之二节存在且含意见映射纪律",
            "先数档再打分" in sec12 and "已修复项不得重复扣分" in sec12,
        )

        # ================================================================
        # 5. _role_skill_block 注入矩阵
        # ================================================================
        from panel_review import _role_skill_block, _role_review_prompt

        blk_researcher = _role_skill_block("researcher")
        self.assert_true(
            "researcher 注入非空且含四节纪律+六节职责",
            "评审纪律" in blk_researcher and "科学内容审稿人" in blk_researcher,
        )
        blk_critic = _role_skill_block("critic")
        self.assert_true(
            "critic 注入含六节职责 + nsfc-writing 十节",
            "表达红线审稿人" in blk_critic and "主线清晰度" in blk_critic,
        )
        blk_reviewer = _role_skill_block("reviewer")
        self.assert_true(
            "reviewer 注入含四维锚点 + 一之二校准纪律 + 六节职责",
            "四维锚点评审法" in blk_reviewer
            and "先数档再打分" in blk_reviewer
            and "评审标准审稿人" in blk_reviewer,
        )
        self.assert_true(
            "注入块预算合规（单块 ≤ 2×MAX_BLOCK_CHARS）",
            all(len(b) <= 2 * 4096 for b in
                (blk_researcher, blk_critic, blk_reviewer)),
        )

        # ================================================================
        # 6. 旧硬编码已删除（skill 是单一真相源）
        # ================================================================
        panel_src = (_SCRIPTS_DIR / "panel_review.py").read_text(encoding="utf-8")
        self.assert_true(
            "旧 role_brief 三句话硬编码已从脚本删除",
            "科学内容审稿人：核查科学论证的准确性" not in panel_src
            and "表达红线审稿人：核查超长句" not in panel_src,
        )
        self.assert_true(
            "旧 writer 修改要求硬编码已删除（改走七节注入）",
            "【修改要求】" not in panel_src,
        )
        self.assert_true(
            "docstring 声明执行者无关契约与托底定位（v7.2.81）",
            "v7.2.81" in panel_src and "托底执行器" in panel_src,
        )
        self.assert_true(
            "writer/verify 阶段 prompt 走 skill 注入（inject_block 调用存在）",
            panel_src.count("inject_block") >= 3,
        )

        # ================================================================
        # 7. _role_review_prompt 引用 skill 定位语
        # ================================================================
        prompt = _role_review_prompt(
            "reviewer", "test-pid", REAL_ROOT / "research_proposals" / "optimizing" / "x",
            "1. [CRITICAL] 测试问题")
        self.assert_true(
            "角色 prompt 含 skill 定位语与 findings 契约引用",
            "三角色定点" in prompt and "findings 输出契约" in prompt,
        )


if __name__ == "__main__":
    suite = PanelV7276Tests()
    suite.run_tests()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"\n{'✓' if suite.results and len(suite.results) - ok == 0 else '✗'} {suite.name}: {ok}/{len(suite.results)} 通过")
    for r in suite.results:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    raise SystemExit(1 if len(suite.results) - ok else 0)
