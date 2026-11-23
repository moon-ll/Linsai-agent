#!/usr/bin/env python3
"""
test_nsfc_writing_skill.py — v7.0.0 nsfc-writing skill（skill 架构）回归测试

背景（用户裁决 2026-09-25，v7.0.0 大版本迭代）：项目从 prompt 驱动迁移为
skill 驱动。skill 真相源放 .hermes/skills/（hermes 项目本地 trusted 目录，
agent 会话自动发现），CoPilot 管线经 skill_loader 按节裁剪注入。本套件验证
nsfc-writing skill 的完整性与 optimize.py 的角色化注入。

  S1 SKILL.md 结构完整（十节齐备，禁用词映射表存在）
  S2 角色化裁剪（writer/critic/purity 三路注入内容正确）
  S3 skill_loader fail-open（skill 缺失返回空）
  S4 optimize.py 注入挂接（critic/writer/purity 三处调用，防误删）
  S5 token 预算（注入块 ≤5KB）

运行：python3 scripts/self_test.py --module（自动纳入）
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from test_runner import TestSuite

SKILL_PATH = _SCRIPTS.parent / ".hermes" / "skills" / "nsfc-writing" / "SKILL.md"
OPTIMIZE_SRC = (_SCRIPTS / "proposal_lifecycle" / "optimize.py").read_text(encoding="utf-8")


class NsfcWritingSkillTests(TestSuite):
    """nsfc-writing skill 完整性与注入挂接（v7.0.0 skill 架构）。"""

    def __init__(self):
        super().__init__("写作纪律skill")

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        # S1: SKILL.md 结构完整（v2 十节）
        self.assert_true(SKILL_PATH.exists(), ".hermes/skills/nsfc-writing/SKILL.md 必须存在")
        text = SKILL_PATH.read_text(encoding="utf-8")
        self.assert_true(text.startswith("---"), "hermes 原生格式需 YAML frontmatter")
        for section in ["一、读者视角总纲", "二、叙事主线纪律", "三、禁用词与替换映射",
                        "四、叙述式写作规范", "五、正反对照", "六、文件纯净性与内容边界",
                        "七、内容质量纪律", "八、AI 写作模式修复", "九、writer 自检清单",
                        "十、critic 检查项"]:
            self.assert_true(f"## {section}" in text, f"SKILL.md 缺节：{section}")
        for word in ["交付物", "硬门控", "口径", "R1/R2/R3"]:
            self.assert_true(word in text, f"禁用词映射表缺词条：{word}")
        self.assert_true("每千字不超过 1 处" in text, "交叉引用预算规则缺失")
        self.assert_true("最多 1 个条件分支句" in text, "条件分支密度规则缺失")
        # 收编验证：原 optimize.py 硬编码块的关键内容已进 skill
        # v7.0.4：断言措辞对齐 skill 实际文本（"特色创新四步"；旧断言
        # "四步闭环"在 v7.0.2 skill 修订后失配，实测 40/41）
        for kw in ["五层递进", "特色创新四步", "章节文件白名单", "孤儿章节守卫",
                   "白名单术语", "密度论"]:
            self.assert_true(kw in text, f"收编内容缺失：{kw}")

        # S2: 角色化裁剪（v7.0.0 三路）
        import proposal_lifecycle.optimize as opt
        w = opt._load_nsfc_writing_skill_text("writer")
        c = opt._load_nsfc_writing_skill_text("critic")
        pu = opt._load_nsfc_writing_skill_text("purity")
        self.assert_true(w and c and pu, "三路注入均应非空（skill 存在时）")
        self.assert_true("顺叙为主" in w and "禁用词与替换映射" in w and "AI 写作模式修复" in w,
                         "writer 版须含叙事纪律+禁用词映射+AI 修复")
        self.assert_true("叙述式写作规范" in c and "critic 检查项" in c,
                         "critic 版须含叙述规范+检查项")
        self.assert_true("科学正确性优先级高于风格检查" in c,
                         "critic 版须含优先级护栏")
        self.assert_true("文件纯净性与内容边界" in pu and "内容质量纪律" in pu,
                         "purity 版须含纯净性红线+质量纪律")
        self.assert_true(".hermes/skills/nsfc-writing" in w,
                         "注入须给 skill 路径供 agent 按需深读")

        # S3: skill_loader fail-open
        import skill_loader
        self.assert_true(skill_loader.load_skill("__not_exist__") == "",
                         "skill 缺失时 load_skill 应返回空串（fail-open）")
        self.assert_true(skill_loader.inject_block("__not_exist__", ["任意节"]) == "",
                         "skill 缺失时 inject_block 应返回空串")

        # S4: optimize.py 三路挂接（防后续重构误删）
        for role in ("critic", "writer", "purity"):
            self.assert_true(
                f"_load_nsfc_writing_skill_text('{role}')" in OPTIMIZE_SRC,
                f"optimize.py 必须挂接 {role} 路 skill 注入",
            )
        # 硬编码收敛验证：旧块的关键句已不在源码
        for legacy in ["写作风格红线（重点检查，对照范本", "叙述式写作核心规则",
                       "文件纯净性红线（v6.9.46"]:
            self.assert_true(legacy not in OPTIMIZE_SRC,
                             f"旧硬编码块应已收敛进 skill：{legacy}")

        # S5: token 预算
        self.assert_true(len(w) <= 5120, f"writer 注入超预算（{len(w)} 字符 >5KB）")
        self.assert_true(len(c) <= 5120, f"critic 注入超预算（{len(c)} 字符 >5KB）")
        self.assert_true(len(pu) <= 5120, f"purity 注入超预算（{len(pu)} 字符 >5KB）")
