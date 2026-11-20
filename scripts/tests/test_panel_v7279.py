#!/usr/bin/env python3
"""v7.2.79 评审团结构化契约测试（findings 聚合去重 + verify 结构化判定）。

覆盖：
1. _parse_finding_rows：skill 六节表格行契约解析（大小写/无关行忽略）
2. _aggregate_table：跨角色去重（同位置+同题合并）、severity 置顶排序
3. _aggregate_findings：有结构化条目 → 聚合表+原文；无条目 → fail-open
   退回原文拼接
4. _parse_verify_verdict：核销表 critical/high 未解决 → 需返工；L 条目
   severity 反解；C 条目用表内级别；medium/low 不拦；无核销表 → 退回
   总结行字符串比对（v6 行为）
5. run_panel 源码接线守卫

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_panel_v7279.py
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


class PanelV7279Tests(TestSuite):
    def __init__(self):
        super().__init__("v7.2.79 评审团结构化契约测试")
        self.tmp_root = None

    def assert_true(self, condition, name, msg: str = "") -> bool:
        if isinstance(condition, str):
            condition, name = name, condition
        return super().assert_true(bool(condition), str(name), msg)

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_tests(self):
        from panel_review import (
            _parse_finding_rows, _aggregate_table, _aggregate_findings,
            _parse_verify_verdict,
        )

        findings = {
            "researcher": (
                "## 遗留问题核对\n| 1 | 仍存在 | L3 | 建议 |\n\n"
                "## 新发现问题\n"
                "| P1 | high | scheme§3.2 | 指标口径与口径表冲突 | 对齐 params.json |\n"
                "| P2 | low | rationale§2 | 表述冗余 | 精简 |\n"
            ),
            "critic": (
                "## 新发现问题\n"
                "| P1 | HIGH | scheme§3.2 | 指标口径与口径表冲突 | 改为 canonical |\n"
                "| P1 | critical | references§文献[5] | 引用凭记忆改写 | 三源对照誊写 |\n"
            ),
            "reviewer": "自由文本，无结构化条目\n## 新发现问题\n无\n",
        }

        # 1. 解析
        rows = _parse_finding_rows(findings)
        self.assert_true("解析出 4 条结构化条目（reviewer 无条目）", len(rows) == 4)
        self.assert_true("severity 大小写归一", all(r["severity"].islower() for r in rows))

        # 2. 聚合去重 + 排序
        table = _aggregate_table(findings)
        self.assert_true("聚合表存在", table.startswith("【聚合条目表"))
        # researcher P1 与 critic P1 同位置同题 → 合并为 1 条，共 3 条
        self.assert_true("同位置同题跨角色去重（4→3 条）",
                         table.count("| C") == 3)
        lines = [ln for ln in table.splitlines() if ln.startswith("| C")]
        first_cells = [c.strip() for c in lines[0].split("|")]
        self.assert_true("critical 置顶首位", first_cells[1] == "C1"
                         and first_cells[2] == "critical")
        self.assert_true("来源列保留首报角色", "researcher" in lines[1])

        # 3. writer 聚合输出 / fail-open
        agg = _aggregate_findings(findings)
        self.assert_true("聚合输出含表+原文", "聚合条目表" in agg and "核查发现（原文）" in agg)
        plain = _aggregate_findings({"a": "纯文本无条目"})
        self.assert_true("无条目 fail-open 退回原文拼接",
                         "聚合条目表" not in plain and "纯文本无条目" in plain)

        # 4. verify 判定
        issue_block = "1. [CRITICAL] 数值链断裂\n2. [HIGH] 超长句\n3. [MEDIUM] 措辞"
        # 全部解决 → 通过
        v_ok = ("| L1 | critical | 已解决 | 已修复 |\n"
                "| L2 | high | 已解决 | 已拆句 |\n"
                "| C1 | high | 已解决 | 已对齐 |\n"
                "复核结论: 通过")
        self.assert_true("核销表全解决 → 通过", _parse_verify_verdict(v_ok, issue_block) == "通过")
        # L1 (CRITICAL) 未解决 → 需返工（severity 从 issue_block 反解）
        v_bad = ("| L1 | critical | 未解决 | 仍残留 |\n"
                 "复核结论: 通过")  # 总结行与表格矛盾时以表格为准
        self.assert_true("critical 未解决 → 需返工（表格优先于总结行）",
                         _parse_verify_verdict(v_bad, issue_block) == "需返工")
        # C 条目用表内级别
        v_c = ("| C2 | critical | 未解决 | 引用仍凭记忆 |\n")
        self.assert_true("C 条目 critical 未解决 → 需返工",
                         _parse_verify_verdict(v_c, issue_block) == "需返工")
        # medium/low 未解决不拦
        v_mid = ("| L3 | medium | 未解决 | 措辞待改 |\n"
                 "| C1 | low | 未解决 | 冗余 |\n")
        self.assert_true("仅 medium/low 未解决 → 通过",
                         _parse_verify_verdict(v_mid, issue_block) == "通过")
        # 无核销表 → 退回总结行（v6 行为）
        self.assert_true("无核销表退回总结行判定（通过）",
                         _parse_verify_verdict("复核结论: 通过", issue_block) == "通过")
        self.assert_true("无核销表退回总结行判定（需返工为保守默认）",
                         _parse_verify_verdict("格式崩坏输出", issue_block) == "需返工")

        # 5. run_panel 源码接线
        src = (_SCRIPTS_DIR / "panel_review.py").read_text(encoding="utf-8")
        self.assert_true("阶段 B 接聚合（combined=_aggregate_findings）",
                         "combined = _aggregate_findings(findings)" in src)
        self.assert_true("阶段 C 接聚合表靶子（agg_table）",
                         "agg_table = _aggregate_table(findings)" in src
                         and "新发现聚合条目" in src)
        self.assert_true("verdict 走结构化解析（_parse_verify_verdict）",
                         "verdict = _parse_verify_verdict(verify_text, issue_block)" in src)
        # skill 七节核销表契约同步
        from skill_loader import load_skill, extract_section
        sec7 = extract_section(load_skill("quality-review"), "七、评审团修改与复核纪律")
        self.assert_true("skill 七节含核销表格式契约",
                         "核销表" in sec7 and "已解决/部分/未解决" in sec7)
        self.assert_true("skill 七节判定线升级为 critical/high",
                         "任一 critical/high 未解决" in sec7)


if __name__ == "__main__":
    suite = PanelV7279Tests()
    suite.run_tests()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"\n{'✓' if suite.results and len(suite.results) - ok == 0 else '✗'} {suite.name}: {ok}/{len(suite.results)} 通过")
    for r in suite.results:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    raise SystemExit(1 if len(suite.results) - ok else 0)
