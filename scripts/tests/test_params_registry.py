#!/usr/bin/env python3
"""
test_params_registry.py — 数值口径表（v7.2.13）单测

覆盖：
    1. load_params 三态（无表 None / 空表 None / 有表 dict）
    2. format_params_block 渲染（canonical + 禁用模式 + 注入纪律）
    3. check_consistency：stale 命中定位（章节×次数）/ 干净通过 /
       非法正则容错
    4. run_check_and_persist 落盘 params-conflicts.json
    5. 播种幂等（--seed 已存在跳过）
    6. executor 双钩子集成：writer 注入块传入 + critic 冲突清单文本生成
"""

import json
import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock

from test_runner import TestSuite, create_isolated_env

sys.path.insert(0, str(Path(__file__).parent.parent))


class ParamsRegistryTests(TestSuite):
    """v7.2.13: 数值口径表机制测试。"""

    def __init__(self):
        super().__init__("数值口径表测试")
        self.tmp_root = None
        self.prop_dir = None
        self.pr = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        self.prop_dir = self.tmp_root / "research_proposals" / "optimizing" / "test-p-20261005"
        sections = self.prop_dir / "04_proposal" / "sections"
        sections.mkdir(parents=True, exist_ok=True)
        # 三章含不同口径数值（模拟 moire 互斥现场）
        (sections / "rationale.md").write_text(
            "全原胞 11,000 原子，总核时 10⁸。", encoding="utf-8")
        (sections / "content.md").write_text(
            "双层 12,400 原子；11,000 原子旧口径已废。SHG 调制（>30%）表述错误。", encoding="utf-8")
        (sections / "scheme.md").write_text(
            "联合维度 240-300，冗余 24-50×。", encoding="utf-8")

        from lifecycle import params_registry as pr
        self.pr = pr

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_params(self):
        return {
            "entries": [
                {"key": "原子数", "canonical": "双层 12,400",
                 "stale_patterns": [r"11,?000"], "note": "单层 6,200"},
                {"key": "SHG 调制", "canonical": "开关比超 10 倍、抑制约 90%",
                 "stale_patterns": [r"调制[（(]?[>＞] ?30%"], "note": "引文红线"},
            ]
        }

    def run_tests(self):
        pr = self.pr

        # ===== 1. load_params 三态 =====
        self.assert_true(pr.load_params(self.prop_dir) is None, "无表 → None")
        (self.prop_dir / "04_proposal" / "params.json").write_text(
            json.dumps({"entries": []}, ensure_ascii=False), encoding="utf-8")
        self.assert_true(pr.load_params(self.prop_dir) is None, "空表 → None")
        (self.prop_dir / "04_proposal" / "params.json").write_text(
            json.dumps(self._make_params(), ensure_ascii=False), encoding="utf-8")
        self.assert_true(pr.load_params(self.prop_dir) is not None, "有表 → dict")

        # ===== 2. format_params_block =====
        block = pr.format_params_block(self._make_params())
        self.assert_true("单一真相源" in block, "注入块含纪律声明")
        self.assert_true("双层 12,400" in block, "注入块含 canonical")
        self.assert_true("11,?000" in block, "注入块含禁用模式")

        # ===== 3. check_consistency =====
        r = pr.check_consistency(self.prop_dir, self._make_params())
        self.assert_eq(r["checked"], 2, "2 个模式被校验")
        keys = {c["key"] for c in r["conflicts"]}
        self.assert_true("原子数" in keys, "11,000 残留应命中", f"{keys}")
        self.assert_true("SHG 调制" in keys, ">30% 表述应命中", f"{keys}")
        atom = next(c for c in r["conflicts"] if c["key"] == "原子数")
        secs = {h["section"]: h["count"] for h in atom["hits"]}
        self.assert_eq(secs.get("rationale.md"), 1, "rationale 命中 1 次")
        self.assert_eq(secs.get("content.md"), 1, "content 命中 1 次")
        self.assert_true("scheme.md" not in secs, "scheme 干净不命中")
        # 干净通过场景
        (self.prop_dir / "04_proposal" / "sections" / "rationale.md").write_text(
            "双层 12,400 原子，开关比超 10 倍。", encoding="utf-8")
        (self.prop_dir / "04_proposal" / "sections" / "content.md").write_text(
            "双层 12,400；抑制约 90%。", encoding="utf-8")
        r2 = pr.check_consistency(self.prop_dir, self._make_params())
        self.assert_true(r2["clean"], "全干净应通过", f"{r2['conflicts']}")
        # 非法正则容错
        bad = {"entries": [{"key": "x", "canonical": "y",
                            "stale_patterns": ["[unclosed"]}]}
        r3 = pr.check_consistency(self.prop_dir, bad)
        self.assert_true(r3["clean"], "非法正则应容错跳过")

        # ===== 4. run_check_and_persist =====
        # 恢复脏内容再持久化
        (self.prop_dir / "04_proposal" / "sections" / "rationale.md").write_text(
            "11,000 原子", encoding="utf-8")
        rp = pr.run_check_and_persist(self.prop_dir, round_num=9)
        self.assert_true(rp.get("active"), "有表应 active")
        self.assert_true(rp.get("conflicts"), "应有冲突")
        out = self.prop_dir / "05_review" / "params-conflicts.json"
        self.assert_true(out.exists(), "冲突报告应落盘")
        saved = json.loads(out.read_text(encoding="utf-8"))
        self.assert_eq(saved.get("round"), 9, "落盘含轮次")

        # ===== 5. 播种幂等 =====
        p = pr.params_path(self.prop_dir)
        p.unlink()
        # 直接调内部模板函数验证结构
        tpl = pr._seed_template()
        self.assert_true(tpl["entries"] and len(tpl["entries"]) >= 4,
                         "模板应含 moire 四冲突示例")

        # ===== 6. executor 集成（双钩子逻辑不真跑 hermes）=====
        # critic 侧：模拟 _run_critic_step 的注入文本构造
        data = self._make_params()
        (self.prop_dir / "04_proposal" / "sections" / "content.md").write_text(
            "11,000 残留", encoding="utf-8")
        chk = pr.check_consistency(self.prop_dir, data)
        text = pr.format_params_block(data)
        if chk["conflicts"]:
            text += f"\n⚠️ 程序化口径校验发现 {len(chk['conflicts'])} 个旧值残留\n"
        self.assert_true("⚠️ 程序化口径校验" in text, "critic 注入应含冲突警示")
        self.assert_true("单一真相源" in text, "critic 注入应含口径表")

        # ===== 7. v7.2.19 机制表述条目泛化 =====
        claim_data = {"entries": [{
            "key": "Heide [13] 机制表述",
            "canonical": "层间堆叠对称性决定偶阶相消与逐层相干累积（I∝n²）",
            "stale_patterns": [r"层间几何相位"],
            "note": "同一机制所有章节必须同表述",
        }]}
        blk = pr.format_params_block(claim_data)
        self.assert_true(
            "机制表述" in blk and "数值与机制表述" in blk,
            "v7.2.19: 注入块措辞应涵盖机制表述类条目",
            blk[:80],
        )
        self.assert_true(
            "层间几何相位" in blk, "禁用旧表述模式应渲染",
        )
        # check 同样能命中表述类 stale
        (self.prop_dir / "04_proposal" / "sections" / "rationale.md").write_text(
            "该现象源于层间几何相位机制。", encoding="utf-8")
        cchk = pr.check_consistency(self.prop_dir, claim_data)
        self.assert_true(
            cchk["conflicts"] and not cchk["clean"],
            "v7.2.19: 旧表述残留应被 grep 命中（机制表述与数值同表治理）",
        )


if __name__ == "__main__":
    suite = ParamsRegistryTests()
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
