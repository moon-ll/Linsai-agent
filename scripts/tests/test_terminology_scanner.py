#!/usr/bin/env python3
"""
test_terminology_scanner.py — 跨章记号/术语一致性扫描器回归测试（v7.3.58）

背景：chiral/phonon 专家交接单 20 条残留中 8 条属跨章记号/术语变体
（记号四形 I₀/(I_q⁰)/δI_q⁽⁰⁾、对映体互换/反转、相图/相位图、即时/瞬时），
多轮 critic 均未报——本扫描器为该失败类的零 LLM 自动发现层。

覆盖：
    1. CJK 变体对检出（4 类正例）+ 滑窗重叠假阳性过滤（反例）
    2. 共同词缀停用（X手性 系同族命名不报）
    3. 记号归一三形态同键（I₀/I_0；I_q⁽⁰⁾/I_q^(0)）+ δ 前缀分组
    4. 符号过滤（长英文散文词不进组）+ 子串支配坍缩
    5. 落盘与 strict 退出码

零 LLM、零落盘污染（临时目录隔离）。
"""

import sys
import importlib
import json
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT

sys.path.insert(0, str(REAL_ROOT / "scripts"))


class TerminologyScannerTests(TestSuite):
    def __init__(self):
        super().__init__("跨章记号/术语一致性扫描器回归测试")
        self.tmp_root = None
        self.ts = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in list(sys.modules.keys()):
            if "terminology_scanner" in mod_name or mod_name in ("paths", "common"):
                del sys.modules[mod_name]
        self.ts = importlib.import_module("terminology_scanner")
        patch_module_root("terminology_scanner", self.tmp_root)
        import paths
        paths.PROJECT_ROOT = self.tmp_root

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            import shutil
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _make_prop(self, rationale: str, content: str):
        prop = self.tmp_root / "research_proposals" / "optimizing" / "prop-test"
        sec = prop / "04_proposal" / "sections"
        sec.mkdir(parents=True, exist_ok=True)
        (sec / "rationale.md").write_text(rationale, encoding="utf-8")
        (sec / "content.md").write_text(content, encoding="utf-8")
        return prop

    # ---------- 用例 ----------

    def test_cjk_variant_pairs_detected(self):
        """4 类正例：长术语/短术语/同前缀/同后缀。"""
        prop = self._make_prop(
            "对映体互换判据成立。对映体互换给出符号行为。对映体互换为初判入口。"
            "相图给出边界，相图坐标为温度，相图第三处。"
            "即时响应与瞬时效应混用。即时读出为先。资料归档依材料清单，资料第三处，资料第四处。",
            "对映体反转判据独立执行，对映体反转优先，对映体反转第三处。"
            "相位图见方案，相位图横轴为波长，相位图纵轴为产额。"
            "即时读出与瞬时读出并存，瞬时读出为主。材料清单为准，材料第三处，材料第四处。")
        pairs = {(p["a"], p["b"]) for p in
                 self.ts.scan_proposal(prop).get("cjk_variant_pairs", [])}
        def has(a, b):
            return (a, b) in pairs or (b, a) in pairs
        self.assert_true(has("对映体互换", "对映体反转"), "长术语变体对检出")
        self.assert_true(has("相图", "相位图"), "相图/相位图检出")
        self.assert_true(has("即时", "瞬时"), "即时/瞬时检出")
        self.assert_true(has("资料", "材料"), "资料/材料检出")

    def test_overlapping_window_false_positive_filtered(self):
        """滑窗重叠假阳性（对映/映体 无公共前后缀）不报。"""
        prop = self._make_prop(
            "对映体互换判据成立。对映体互换给出符号行为。对映体互换为初判入口。",
            "对映体反转判据独立执行，对映体反转优先，对映体反转第三处。")
        pairs = {(p["a"], p["b"]) for p in
                 self.ts.scan_proposal(prop).get("cjk_variant_pairs", [])}
        self.assert_true(not has2(pairs, "对映", "映体"), "滑窗重叠 gram 不成对")
        self.assert_true(not has2(pairs, "互换", "反转") or has2(pairs, "对映体互换", "对映体反转"),
                         "子 gram 对被长形态支配坍缩")

    def test_shared_affix_family_filtered(self):
        """X手性 系同族命名（不同物理量共享词缀）不报。"""
        prop = self._make_prop(
            "自旋手性贡献显著。自旋手性读出稳定。自旋手性第三处出现。",
            "场手性响应不同。场手性另行标定。场手性第三处出现。")
        pairs = {(p["a"], p["b"]) for p in
                 self.ts.scan_proposal(prop).get("cjk_variant_pairs", [])}
        self.assert_true(not has2(pairs, "自旋手性", "场手性"), "共同词缀同族不报")

    def test_token_variant_groups(self):
        """记号三形态归一：I₀/I_0 同组；I_q⁽⁰⁾/I_q^(0) 同组；δ 前缀分组。"""
        prop = self._make_prop(
            "产额记作 I₀ 与 I_0 两种形态。I₀ 出现于份额表，I_0 见方案。"
            "零泵浦项记 I_q⁽⁰⁾，而 I_q^(0) 见于附录。I_q⁽⁰⁾ 再次出现。"
            "微扰量 δI_q⁽⁰⁾ 单独定义，δI_q^(0) 同义。",
            "I_0 归一后入表，I_0 定义如前。I_q⁽⁰⁾ 与正文呼应，I_q^(0) 第四处。"
            "δI_q⁽⁰⁾ 的传播见误差节，δI_q^(0) 同。")
        groups = {g["group_key"]: {v["form"] for v in g["variants"]}
                  for g in self.ts.scan_proposal(prop).get("token_variant_groups", [])}
        self.assert_true(has_group(groups, "I_0", {"I₀", "I_0"}), "I₀/I_0 同组")
        self.assert_true(has_group(groups, "I_q", {"I_q⁽⁰⁾", "I_q^(0)"}),
                         "I_q⁽⁰⁾/I_q^(0) 同组")
        self.assert_true(any(k.startswith("δ") for k in groups), "δ 前缀独立分组")

    def test_english_prose_words_filtered(self):
        """长英文散文词（Harmonic 类，无上下标）不进记号组。"""
        prop = self._make_prop(
            "The Harmonic spectrum and Floquet engineering are discussed. "
            "Harmonic yields scale with Floquet theory. Harmonic third.",
            "Harmonic order differs; Floquet states evolve. Floquet and Harmonic.")
        groups = self.ts.scan_proposal(prop).get("token_variant_groups", [])
        bad = [g for g in groups if "Harmonic" in g["group_key"] or "Floquet" in g["group_key"]]
        self.assert_true(not bad, "长散文词不进记号组")

    def test_persist_and_strict(self):
        """落盘 + strict 退出码（有候选对 → 1）。"""
        prop = self._make_prop(
            "即时响应与瞬时效应混用。即时读出为先，即时第三处。",
            "瞬时读出为主，瞬时第三处，瞬时另一处。")
        res = self.ts.run_and_persist(prop, strict=True)
        out = prop / "05_review" / "terminology-scan.json"
        self.assert_true(out.exists(), "报告落盘")
        self.assert_eq(res["exit"], 1, "strict 有候选 → exit 1")
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assert_true(data.get("checked") is True, "报告 checked=true")

    def run_tests(self):
        self.test_cjk_variant_pairs_detected()
        self.test_overlapping_window_false_positive_filtered()
        self.test_shared_affix_family_filtered()
        self.test_token_variant_groups()
        self.test_english_prose_words_filtered()
        self.test_persist_and_strict()


def has2(pairs, a, b):
    return (a, b) in pairs or (b, a) in pairs


def has_group(groups, key_prefix, expected_forms):
    for k, forms in groups.items():
        if k == key_prefix or k.startswith(key_prefix):
            if expected_forms <= forms:
                return True
    return False


if __name__ == "__main__":
    suite = TerminologyScannerTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    s = suite.summary()
    print(f"\n{'✓' if s['failed'] == 0 else '✗'} {s['name']}: {s['passed']}/{s['total']} 通过")
    for r in s["results"]:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if s["failed"] == 0 else 1)
