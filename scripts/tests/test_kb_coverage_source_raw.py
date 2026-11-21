#!/usr/bin/env python3
"""知识库覆盖率 source_raw 口径测试（v6.10.8）。

验证 sync_engine.compute_kb_coverage 用蒸馏页 frontmatter 的
source_raw（纯文件名）精确对账，修复 stem 匹配因命名差异
（点→下划线）导致的系统性低估（4.9% vs 真实 80.7%）。

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_kb_coverage_source_raw.py
"""

import sys
import tempfile
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


class KbCoverageSourceRawTests(TestSuite):
    def __init__(self):
        super().__init__("覆盖率 source_raw 口径测试（v6.10.8）")

    def setup(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="kb-cov-")
        self.root = Path(self.tmp.name)
        self.raw_dir = self.root / "raw"
        self.wiki_dir = self.root / "wiki"
        self.raw_dir.mkdir(parents=True)
        self.wiki_dir.mkdir(parents=True)

    def teardown(self):
        self.tmp.cleanup()

    def _mk_raw(self, name: str):
        (self.raw_dir / name).write_text("---\ntitle: x\n---\nbody", encoding="utf-8")

    def _mk_wiki(self, name: str, source_raw: str):
        (self.wiki_dir / name).write_text(
            f"---\nsource_raw: {source_raw}\n---\nbody", encoding="utf-8")

    def run_tests(self):
        from sync_engine import compute_kb_coverage

        # ── 1. 命名差异下 source_raw 口径正确计数 ─────────────
        self._mk_raw("2026-2604.03983-circular-dichroism.md")
        self._mk_raw("2026-2605.27252-real-time-tddft.md")
        self._mk_raw("2026-2607.00898-unread-paper.md")
        # wiki 蒸馏页：点号→下划线（历史命名规则），source_raw 指回原文件
        self._mk_wiki(
            "2026-2604_03983-circular-dichroism.md",
            "2026-2604.03983-circular-dichroism.md")
        self._mk_wiki(
            "2026-2605_27252-real-time-tddft.md",
            "2026-2605.27252-real-time-tddft.md")
        used = {
            "2026-2604.03983-circular-dichroism.md",
            "2026-2605.27252-real-time-tddft.md",
        }
        cov = compute_kb_coverage(self.raw_dir, self.wiki_dir, used_sources=used)
        self.assert_eq(cov["total"], 3, "分母应为 raw 全量")
        self.assert_eq(cov["covered"], 2, "两篇已蒸馏应计数（不受命名差异影响）")
        self.assert_eq(cov["coverage_pct"], 66.7, "覆盖率 2/3")
        self.assert_eq(len(cov["missing"]), 1, "缺 1 篇")
        self.assert_true(
            "2026-2607.00898-unread-paper.md" in cov["missing"], "缺失应为未蒸馏篇")

        # ── 2. 旧口径（stem 匹配）在同数据下会误报 ────────────
        old_raw = {f.stem for f in self.raw_dir.glob("*.md")}
        old_wiki = {f.stem for f in self.wiki_dir.glob("*.md")}
        old_cov = len(old_raw & old_wiki) / len(old_raw) * 100
        self.assert_eq(old_cov, 0.0, "旧口径在命名差异下计数为 0（回归锚点）")

        # ── 3. 空目录不崩溃 ───────────────────────────────────
        empty_raw = self.root / "empty-raw"
        empty_wiki = self.root / "empty-wiki"
        empty_raw.mkdir()
        cov = compute_kb_coverage(empty_raw, empty_wiki, used_sources=set())
        self.assert_eq(cov["total"], 0, "空目录分母 0")
        self.assert_eq(cov["coverage_pct"], 0.0, "空目录覆盖率 0 不除零")

        # ── 4. 回退分支：used_sources 为空时退 stem 匹配 ──────
        fb_root = Path(tempfile.mkdtemp(prefix="kb-fb-"))
        try:
            fb_raw, fb_wiki = fb_root / "r", fb_root / "w"
            fb_raw.mkdir(); fb_wiki.mkdir()
            same = "2020-2010.00001-same-name.md"
            (fb_raw / same).write_text("x", encoding="utf-8")
            (fb_wiki / same).write_text("y", encoding="utf-8")
            (fb_raw / "2020-2010.00002-other.md").write_text("x", encoding="utf-8")
            cov = compute_kb_coverage(fb_raw, fb_wiki, used_sources=set())
            self.assert_eq(cov["covered"], 1, "回退口径应命中同名文件")
            self.assert_eq(len(cov["missing"]), 1, "回退口径缺 1")
        finally:
            import shutil
            shutil.rmtree(fb_root, ignore_errors=True)

        # ── 5. source_raw 带路径前缀的历史兼容（_wiki_source_raws 已剥离）──
        # 注入侧模拟 kb_distill 的纯文件名归一（带 raw/papers/ 前缀的值不出现）
        cov = compute_kb_coverage(
            self.raw_dir, self.wiki_dir,
            used_sources={"raw/papers/2026-2604.03983-circular-dichroism.md"})
        self.assert_eq(
            cov["covered"], 0,
            "注入集合应由调用方保证纯文件名（前缀值不匹配属预期，防止静默虚高）")


def main() -> None:
    suite = KbCoverageSourceRawTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
