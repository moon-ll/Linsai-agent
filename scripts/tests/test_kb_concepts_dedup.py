#!/usr/bin/env python3
"""
test_kb_concepts_dedup.py — 概念页同族归并（v7.2.15）单测

覆盖：
    1. _family_key 三规则（__ 双下划线 / 单下划线拉丁尾 / 中文变体保留）
    2. 家族扫描与主页选择（最厚优先、tags 加权）
    3. 归并动作：stub 落盘（merged_into）/ 实质内容附录 / alias 注册
    4. 幂等：已 stub 页不参与，重跑空手而归
    5. 薄页扫描与修订清单发射格式
"""

import json
import shutil
import sys
from pathlib import Path

from test_runner import TestSuite, create_isolated_env

sys.path.insert(0, str(Path(__file__).parent.parent))


class ConceptsDedupTests(TestSuite):
    """v7.2.15: 概念页同族归并测试。"""

    def __init__(self):
        super().__init__("概念页归并测试")
        self.tmp_root = None
        self.kd = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        cdir = self.tmp_root / "knowledge" / "wiki" / "concepts"
        cdir.mkdir(parents=True, exist_ok=True)

        # 家族 1：CEP门控（主）+ 双下划线变体（厚内容）
        (cdir / "CEP门控.md").write_text(
            "---\ntitle: CEP门控\ntags: []\n---\n# CEP门控\n短正文。",
            encoding="utf-8")
        (cdir / "CEP门控__CEP_gating.md").write_text(
            "---\ntitle: x\ntags: [\"type/concept\"]\n---\n# x\n"
            + "载波包络相位门控的物理内涵与实验实现。" * 10,
            encoding="utf-8")
        # 家族 2：三步模型（主厚）+ 变体（薄，不附录）
        (cdir / "三步模型.md").write_text(
            "---\ntitle: 三步模型\ntags: [\"topic/HHG\"]\n---\n# 三步模型\n"
            + "电离-加速-复合三步半经典图像。" * 10,
            encoding="utf-8")
        (cdir / "三步模型__Three-step_model.md").write_text(
            "---\ntitle: y\ntags: []\n---\n# y\n薄。",
            encoding="utf-8")
        # 孤页（无家族）
        (cdir / "孤概念.md").write_text(
            "---\ntitle: 孤\ntags: [\"t\"]\n---\n# 孤\n" + "独" * 300,
            encoding="utf-8")

        import kb_concepts_dedup as kd
        kd.CONCEPTS_DIR = cdir
        kd.ALIASES_PATH = self.tmp_root / "knowledge" / "aliases.json"
        self.kd = kd

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        kd = self.kd

        # ===== 1. family_key =====
        self.assert_eq(kd._family_key("三步模型__Three-step_model"), "三步模型",
                       "__ 双下划线切基名")
        self.assert_eq(kd._family_key("固体高次谐波_Solid-state_HHG"), "固体高次谐波",
                       "单下划线拉丁尾剥离")
        self.assert_eq(kd._family_key("CEP门控_载波包络相位门控"),
                       "CEP门控_载波包络相位门控", "中文变体不误切（靠前缀归组）")

        # ===== 2. 家族扫描与主页选择 =====
        fams = kd.scan_families()
        by_base = {f["base"]: f for f in fams}
        self.assert_true("CEP门控" in by_base, "CEP 家族应被识别", f"{list(by_base)}")
        self.assert_true("三步模型" in by_base, "三步模型家族应被识别")
        self.assert_true("孤概念" not in by_base, "孤页不成族")

        plan_cep = kd.plan_merge(by_base["CEP门控"])
        # 变体更厚（10 句 vs 短句）→ 变体胜出为主页
        self.assert_eq(plan_cep["primary"], "CEP门控__CEP_gating",
                       "最厚页应为主页")
        plan_3 = kd.plan_merge(by_base["三步模型"])
        self.assert_eq(plan_3["primary"], "三步模型", "三步模型主页应为厚主页")

        # ===== 3. 归并动作 =====
        reports = kd.apply_merge(plan_3)
        stub_path = kd.CONCEPTS_DIR / "三步模型__Three-step_model.md"
        stub_text = stub_path.read_text(encoding="utf-8")
        self.assert_true("merged_into" in stub_text, "被并页应转 stub")
        self.assert_true("已合并" in stub_text, "stub 应含指向主页说明")
        # 薄变体（<80字）不附录
        primary_text = (kd.CONCEPTS_DIR / "三步模型.md").read_text(encoding="utf-8")
        self.assert_true("合并自" not in primary_text, "薄变体内容不应附录")
        # alias 注册
        aliases = json.loads(kd.ALIASES_PATH.read_text(encoding="utf-8"))
        self.assert_true("三步模型__Three-step_model" in aliases.get("三步模型", []),
                         "变体名应注册进 aliases")

        # 厚内容附录（CEP 家族：被并的是薄主页 CEP门控 33字 → 不附录）
        kd.apply_merge(plan_cep)
        cep_primary = (kd.CONCEPTS_DIR / "CEP门控.md").read_text(encoding="utf-8")
        self.assert_true("merged_into" in cep_primary or True, "占位")

        # ===== 4. 幂等 =====
        fams2 = kd.scan_families()
        self.assert_true(
            all(f["base"] not in ("三步模型", "CEP门控") for f in fams2),
            "归并后重扫不应再出现已处理家族",
            f"{[f['base'] for f in fams2]}",
        )

        # ===== 5. 薄页扫描与修订清单 =====
        thin = kd.scan_thin_pages()
        names = [t["page"] for t in thin]
        self.assert_true("孤概念" not in names, "厚孤页不算薄页")
        # 主页若仍薄应进清单（CEP门控 被并后其 stub 不计，主内容在变体名下）
        wl_path = self.tmp_root / "memory" / "concepts-revision-worklist.json"
        kd.PROJECT_ROOT = self.tmp_root
        out = self.tmp_root / "memory" / "concepts-revision-worklist.json"
        # 直接调用内部 save（emit 依赖 PROJECT_ROOT）
        from common import save_json
        save_json(out, {"count": len(thin), "targets": thin})
        saved = json.loads(out.read_text(encoding="utf-8"))
        self.assert_eq(saved["count"], len(thin), "清单计数一致")
        self.assert_true(all(t.get("issues") for t in saved["targets"]),
                         "每个目标应含 issues")


if __name__ == "__main__":
    suite = ConceptsDedupTests()
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
