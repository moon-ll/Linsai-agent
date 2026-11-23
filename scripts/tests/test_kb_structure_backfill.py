#!/usr/bin/env python3
"""
test_kb_structure_backfill.py — 知识库结构补足（v7.2.12）单测

覆盖：
    1. kb_concepts_backfill：悬空扫描排除规则（课题 ID/噪声/已存在页/
       alias 归一化/合并 stub）、优先级分档、worklist 发射格式、
       方法卡毕业扫描（≥3 次阈值 + 已有独立页跳过）
    2. kb_moc_builder：主题白名单过滤、运维类排除、stub 去除、
       更新时间排序与截断、渲染格式、孤儿 MOC 清理

全部零 LLM、临时隔离目录运行。
"""

import json
import shutil
import sys
from pathlib import Path

from test_runner import TestSuite, create_isolated_env


class KBStructureBackfillTests(TestSuite):
    """v7.2.12: 概念层扩容 + MOC 导航生成器测试。"""

    def __init__(self):
        super().__init__("知识库结构补足测试")
        self.tmp_root = None
        self.kb = None
        self.moc = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 构造隔离 wiki 结构
        wiki = self.tmp_root / "knowledge" / "wiki"
        (wiki / "papers").mkdir(parents=True, exist_ok=True)
        (wiki / "concepts").mkdir(parents=True, exist_ok=True)
        (wiki / "methods").mkdir(parents=True, exist_ok=True)
        (wiki / "mocs").mkdir(parents=True, exist_ok=True)

        # 已存在页
        (wiki / "concepts" / "贝里相位.md").write_text(
            "# 贝里相位\n内容", encoding="utf-8")
        (wiki / "methods" / "pump-probe.md").write_text(
            "# 泵浦探测\n内容", encoding="utf-8")

        # 论文页 1：含悬空 + 已存在 + 课题 ID + 噪声链接
        (wiki / "papers" / "p1.md").write_text(
            "# 论文一\n"
            "[[高次谐波产生（HHG）]] 与 [[BP-alias]] 相关。\n"
            "[[general-mos2-20260905]] 是课题。\n"
            "[[2020]] 是噪声。\n"
            "## 研究方法（方法卡）\n"
            "### TDSE求解器（方法卡）\n参数 a=1\n",
            encoding="utf-8")
        # 论文页 2-3：引用同一悬空概念（凑频次）
        for i in (2, 3):
            (wiki / "papers" / f"p{i}.md").write_text(
                f"# 论文{i}\n[[高次谐波产生（HHG）]]。\n"
                "### TDSE求解器（方法卡）\n参数 b=2\n",
                encoding="utf-8")
        # 合并 stub（不参与统计）
        (wiki / "papers" / "stub.md").write_text(
            "---\nmerged_into: x\n---\n# stub（已合并）\n[[高次谐波产生（HHG）]]",
            encoding="utf-8")
        # v7.2.16 净化 fixture：噪音 wikilink + 同义项（每类 1 次，均应被滤）
        (wiki / "papers" / "p6.md").write_text(
            "# 论文6\n"
            "[[Corkum]] 与 [[Krausz]] 是人名。\n"
            "[[论文精读：某深读笔记标题]]\n"
            "[[2607.19937]]\n"
            "[[NSFC-强场超快]]\n"
            "[[Edge states and quantum optical high harmonic generation]]\n"
            "[[对称性选择的非相对论自旋劈裂：反铁磁体中相干声子驱动]]\n"
            "[[谷电子学]] 与 [[能谷电子学]]\n",
            encoding="utf-8")
        # alias 映射：真实格式 key=规范名 value=[别名...]（knowledge/aliases.json）
        (self.tmp_root / "knowledge" / "aliases.json").write_text(
            json.dumps({"贝里相位": ["BP-alias", "berry-curvature"]},
                       ensure_ascii=False), encoding="utf-8")

        # 分类数据（MOC 源）
        cats = self.tmp_root / "knowledge" / "categories.json"
        cats.write_text(json.dumps({
            "updated_at": "2026-10-03T00:00:00Z",
            "categories": [
                {"name": "固体HHG", "matched_paths": [
                    "wiki/papers/p1.md", "wiki/papers/p2.md",
                    "wiki/papers/stub.md", "wiki/papers/nonexist.md"]},
                {"name": "每日简报", "matched_paths": ["wiki/papers/p1.md"]},
                {"name": "未知主题", "matched_paths": ["wiki/papers/p1.md"]},
            ]}, ensure_ascii=False), encoding="utf-8")

        # 加载两个模块并把路径指到隔离目录
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import kb_concepts_backfill as kb
        import kb_moc_builder as moc
        kb.WIKI_PAPERS = wiki / "papers"
        kb.WIKI_CONCEPTS = wiki / "concepts"
        kb.WIKI_METHODS = wiki / "methods"
        kb.ALIASES_PATH = self.tmp_root / "knowledge" / "aliases.json"
        kb.CONCEPTS_WORKLIST = self.tmp_root / "memory" / "concepts-wl.json"
        kb.GRADUATE_WORKLIST = self.tmp_root / "memory" / "graduate-wl.json"
        moc.CATEGORIES_PATH = cats
        moc.MOC_DIR = wiki / "mocs"
        moc.WIKI_PAPERS = wiki / "papers"
        self.kb = kb
        self.moc = moc

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def run_tests(self):
        kb, moc = self.kb, self.moc

        # ===== 概念悬空扫描 =====
        items = kb.scan_dangling_concepts(min_freq=1)
        names = {i["name"] for i in items}
        self.assert_true(
            "高次谐波产生（HHG）" in names,
            "高频悬空概念应被捕获",
            f"names={names}",
        )
        self.assert_true(
            "贝里相位" not in names and "BP-alias" not in names,
            "已存在页（含 alias 归一化到规范名）不算悬空",
            f"names={names}",
        )
        self.assert_true(
            not any(n.startswith("general-") for n in names),
            "课题 ID 不算概念缺口",
        )
        self.assert_true(
            "2020" not in names, "年份噪声应被排除",
        )
        # ===== v7.2.16 悬空清单净化 =====
        for noise in ("Corkum", "Krausz", "2607.19937", "NSFC-强场超快",
                      "Edge states and quantum optical high harmonic generation",
                      "对称性选择的非相对论自旋劈裂：反铁磁体中相干声子驱动"):
            self.assert_true(noise not in names, f"噪音应被剔除: {noise[:30]}")
        self.assert_true(
            not any("论文精读" in n for n in names), "深读笔记标题变体应被剔除",
        )
        self.assert_true(
            "谷电子学" not in names and "能谷电子学" in names,
            "同义项应归一到规范名（能谷电子学）",
            f"names={names}",
        )
        vv = next(i for i in items if i["name"] == "能谷电子学")
        self.assert_eq(vv["freq"], 2, "同义项频次累计（谷电子学+能谷电子学 各 1 次）")

        hhg = next(i for i in items if "HHG" in i["name"])
        self.assert_eq(hhg["freq"], 3, "stub 不计数，3 篇论文引用=频次 3")
        self.assert_eq(hhg["priority_hint"], "low", "频次 3 → low（阈值 20/5）")

        # ===== 概念 worklist 发射 =====
        n = kb.emit_concepts_worklist(batch=50)
        self.assert_eq(n, 2, "v7.2.16 后有效悬空概念 2 个（HHG + 能谷电子学）")
        wl = json.loads(kb.CONCEPTS_WORKLIST.read_text(encoding="utf-8"))
        self.assert_eq(wl["count"], 2, "worklist count 字段")
        self.assert_eq(wl["consumed_by"], "ZCode", "consumed_by=ZCode")
        self.assert_true("emitted_at" in wl, "worklist 应含 emitted_at")
        self.assert_true(
            wl["targets"][0]["sample_sources"], "targets 应含 sample_sources",
        )

        # ===== 方法卡毕业扫描（v7.2.12 口径：通用方法词提及频次） =====
        # fixture：p1-p3 含 TDSE 方法卡（3 次提及），pump-probe 已有独立页
        grads = kb.scan_method_graduation(min_shared=3)
        gnames = {g["method"] for g in grads}
        self.assert_true(
            "TDSE" in gnames,
            "TDSE 方法卡提及 3 次应进毕业清单",
            f"grads={gnames}",
        )
        # pump-probe 已有独立方法页 → 即使 3 次提及也不毕业
        (kb.WIKI_PAPERS / "p4.md").write_text(
            "# 论文4\n（方法卡）泵浦探测 pump-probe 使用\n", encoding="utf-8")
        (kb.WIKI_PAPERS / "p5.md").write_text(
            "# 论文5\n（方法卡）泵浦探测 pump-probe 记录\n", encoding="utf-8")
        grads2 = kb.scan_method_graduation(min_shared=3)
        self.assert_true(
            "泵浦探测" not in {g["method"] for g in grads2},
            "已有独立方法页的方法词不毕业",
        )
        gn = kb.emit_graduate_worklist()
        self.assert_true(gn >= 1, "毕业清单发射应至少 1 项")

        # ===== v7.2.16 方法卡台账漂移修复（_skip_by_ledger） =====
        import kb_methods_backfill as kmb
        self.assert_true(kmb._skip_by_ledger({"status": "ok"}), "ok 终态跳过")
        self.assert_true(kmb._skip_by_ledger({"status": "failed_final"}), "failed_final 跳过")
        self.assert_true(
            kmb._skip_by_ledger({"status": "no_method"}, False),
            "no_method 且无方法节 → 仍跳过（无素材）",
        )
        self.assert_true(
            not kmb._skip_by_ledger({"status": "no_method"}, True),
            "v7.2.16: no_method 但方法节已到位 → 重开（状态漂移）",
        )
        self.assert_true(
            not kmb._skip_by_ledger({}, True), "新页（无台账）不跳过",
        )

        # ===== MOC 构建 =====
        cats = json.loads(moc.CATEGORIES_PATH.read_text(encoding="utf-8"))
        mocs = moc.build_mocs(cats)
        self.assert_eq(len(mocs), 1, "仅固体HHG 进白名单（每日简报/未知主题排除）")
        m0 = mocs[0]
        self.assert_eq(m0["slug"], "固体HHG", "slug 保留中文名")
        self.assert_eq(m0["total"], 2, "stub 与不存在页不计")
        titles = [e["stem"] for e in m0["entries"]]
        self.assert_true("p1" in titles and "p2" in titles and "stub" not in titles,
                         "MOC 条目应含实体页不含 stub")

        # ===== MOC 渲染与写盘 =====
        reports = moc.apply_mocs(dry_run=True)
        self.assert_true(
            any("将生成" in r for r in reports), "dry-run 应报告将生成",
        )
        self.assert_true(
            not (moc.MOC_DIR / "固体HHG.md").exists(), "dry-run 不写盘",
        )
        reports = moc.apply_mocs(dry_run=False)
        moc_file = moc.MOC_DIR / "固体HHG.md"
        self.assert_true(moc_file.exists(), "apply 应写盘")
        text = moc_file.read_text(encoding="utf-8")
        self.assert_true("[[p1|" in text, "MOC 应含 wikilink 条目")
        self.assert_true("共 2 篇" in text, "MOC 应含总数说明")
        # 幂等：重复 apply 内容一致
        moc.apply_mocs(dry_run=False)
        self.assert_eq(
            moc_file.read_text(encoding="utf-8"), text, "重复 apply 幂等",
        )
        # 孤儿清理：伪造旧 MOC 后重建应删除
        (moc.MOC_DIR / "旧主题.md").write_text("x", encoding="utf-8")
        moc.apply_mocs(dry_run=False)
        self.assert_true(
            not (moc.MOC_DIR / "旧主题.md").exists(),
            "白名单外的孤儿 MOC 应被清理",
        )


if __name__ == "__main__":
    suite = KBStructureBackfillTests()
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
