#!/usr/bin/env python3
"""
test_kb_distill_frontmatter.py — 蒸馏产物元数据与队列口径回归测试（v7.2.75）

覆盖四个在本轮 healthcheck（2026-10-31 20h）中确认并修复的缺陷：

    BUG-34  蒸馏输出被 bullet 包裹 → 落盘成双块 frontmatter，真实元数据被埋
    BUG-35  raw/projects/ 课题产物混入文献蒸馏队列（队列毒化 + 知识污染）
    BUG-36  蒸馏无墙钟预算 + 补边逐条全量重写 → cron 3600s 硬超时
    BUG-37  frontmatter 行内数组按逗号切分 → 引号内逗号被误切，标签永久
            割裂，且 kb_linker 补边永不收敛

验证点全部为纯逻辑 / 纯函数断言：零 LLM、零生产写入。
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from test_runner import TestSuite


class KbDistillFrontmatterTests(TestSuite):
    """蒸馏元数据 / 队列口径 / 预算 / frontmatter 解析回归（零 LLM）。"""

    def __init__(self):
        super().__init__("kb_distill 元数据与队列口径回归测试（v7.2.75）")

    def run_tests(self):
        import kb_distill
        from kb_text import build_frontmatter, parse_frontmatter

        self.run_bug34_tests(kb_distill)
        self.run_bug35_tests(kb_distill)
        self.run_bug36_tests(kb_distill)
        self.run_bug37_tests(build_frontmatter, parse_frontmatter)

    # ── BUG-34 ────────────────────────────────────────────────
    def run_bug34_tests(self, kb_distill):
        """LLM 把整页包进 bullet → 必须还原为单块 frontmatter 且保留真元数据。"""
        from kb_text import parse_frontmatter
        bulleted = (
            "• ---\n"
            '  title: "课题质量验收"\n'
            "  type: concepts\n"
            '  created: "2026-10-31T04:54:22Z"\n'
            '  tags: ["质量验收", "课题生命周期"]\n'
            '  related: ["课题生命周期", "评审团评审"]\n'
            '  source_raw: "验收报告.md"\n'
            '  growth_stage: "growing"\n'
            "  ---\n"
            "\n"
            "  # 课题质量验收\n"
            "\n"
            "  ## 林赛的理解\n"
            "  正文开始。\n"
        )
        fixed = kb_distill._ensure_source_raw(
            bulleted, "验收报告.md", "concepts", "验收报告")

        # 关键：只允许一块 frontmatter（两个定界符）
        self.assert_eq(fixed.count("---"), 2,
                       "bullet 包裹形态还原后只有一块 frontmatter")
        self.assert_true("• ---" not in fixed,
                         "正文不再残留 bullet 包裹标记")

        fm, body = parse_frontmatter(fixed)
        self.assert_eq(fm.get("title"), "课题质量验收",
                       "真实 title 从内层 frontmatter 恢复（不被文件名覆盖）")
        self.assert_eq(fm.get("tags"), ["质量验收", "课题生命周期"],
                       "真实 tags 保留")
        self.assert_eq(fm.get("related"), ["课题生命周期", "评审团评审"],
                       "真实 related 保留")
        self.assert_eq(fm.get("source_raw"), "验收报告.md",
                       "source_raw 正确")
        self.assert_true(body.lstrip().startswith("# 课题质量验收"),
                         "正文首行为标题（无 bullet 噪声）")

        # 幂等：已还原形态再走一次不应变化
        again = kb_distill._ensure_source_raw(
            fixed, "验收报告.md", "concepts", "验收报告")
        self.assert_eq(again.count("---"), 2, "二次处理不产生第三块 frontmatter")

        # fail-open：非 bullet 形态的裸 frontmatter 不被改写
        plain = "---\ntitle: y\ntype: papers\n---\n\n正文"
        out = kb_distill._ensure_source_raw(plain, "y.md", "papers", "y")
        self.assert_eq(out.count("---"), 2, "裸 frontmatter 不受影响")
        self.assert_in('source_raw: "y.md"', out, "裸 frontmatter 仍补 source_raw")

        # 非 bullet 的正文不应被误伤
        body_only = "# 标题\n\n正文"
        out2 = kb_distill._ensure_source_raw(body_only, "z.md", "papers", "z")
        self.assert_true(out2.lstrip().startswith("---"),
                         "纯正文仍走构造头路径")
        self.assert_in("# 标题", out2, "纯正文内容保留")

    # ── BUG-35 ────────────────────────────────────────────────
    def run_bug35_tests(self, kb_distill):
        """raw/projects/ 课题产物不得进入文献蒸馏队列。"""
        self.assert_true(
            kb_distill._is_excluded("raw/projects/general-qgi-20260726/05_review/review-report.md"),
            "raw/projects 课题产物被排除出蒸馏队列")
        self.assert_true(
            kb_distill._is_excluded("raw/projects/x/00_imported/topics/_index.md"),
            "raw/projects 深层路径同样被排除")
        self.assert_true(
            not kb_distill._is_excluded("raw/papers/2507.09234-xxx.md"),
            "raw/papers 正常文献不被排除")
        self.assert_true(
            not kb_distill._is_excluded("raw/notes/solid-HHG-theory.md"),
            "raw/notes 不被误排除")
        self.assert_true(
            kb_distill._is_excluded("raw/pdfs/_text_cache/1234.txt.md"),
            "既有 _text_cache 排除规则保持")

    # ── BUG-36 ────────────────────────────────────────────────
    def run_bug36_tests(self, kb_distill):
        """蒸馏必须有墙钟预算；预算耗尽须优雅停批而非硬失败。"""
        self.assert_true(kb_distill.DEFAULT_TIME_BUDGET_S > 0,
                         "默认墙钟预算为正")
        self.assert_true(kb_distill.DEFAULT_TIME_BUDGET_S < 3600,
                         "默认预算小于 hermes cron 硬超时 3600s")

        # 预算耗尽 → 提前 break，剩余留待下一档
        calls = []

        def fake_distill(path, dry_run=False):
            calls.append(path)
            return {"success": True, "raw": path.name, "wiki": "w.md"}

        orig_distill = kb_distill.distill_one
        orig_pending = kb_distill.pending_distill_list
        try:
            from pathlib import Path as _P
            kb_distill.distill_one = fake_distill
            kb_distill.pending_distill_list = lambda: [
                _P("/tmp/fake/raw/x%d.md" % i) for i in range(10)
            ]
            # 预算耗尽 → 立即停批（不做任何一篇）
            # 用极小正预算触发（time_budget_s=0 语义是「不限」，见 CLI 帮助）
            r = kb_distill.run_batch(batch=10, time_budget_s=1e-9)
            self.assert_true("skipped" not in r,
                             "未被锁占用（lock_busy 不应出现）")
            self.assert_true("stopped_reason" in r,
                             "预算耗尽时返回 stopped_reason")
            self.assert_true("time_budget_exhausted" in r.get("stopped_reason", ""),
                             "stopped_reason 标明预算耗尽")
            self.assert_eq(len(calls), 0, "预算耗尽时一篇都不做")
            self.assert_eq(r["attempted"], 0, "attempted 反映实际执行数")
        finally:
            kb_distill.distill_one = orig_distill
            kb_distill.pending_distill_list = orig_pending

        # 预算 0 = 不限（CLI 契约），必须全部执行
        calls0 = []

        def fake_distill0(path, dry_run=False):
            calls0.append(path)
            return {"success": True, "raw": path.name, "wiki": "w.md"}

        from pathlib import Path as _P
        orig_distill = kb_distill.distill_one
        orig_pending = kb_distill.pending_distill_list
        try:
            kb_distill.distill_one = fake_distill0
            kb_distill.pending_distill_list = lambda: [
                _P("/tmp/fake/raw/w%d.md" % i) for i in range(3)
            ]
            r0 = kb_distill.run_batch(batch=3, time_budget_s=0)
            self.assert_eq(len(calls0), 3, "预算 0 = 不限，全部执行")
            self.assert_true("stopped_reason" not in r0,
                             "预算不限时无 stopped_reason")
        finally:
            kb_distill.distill_one = orig_distill
            kb_distill.pending_distill_list = orig_pending

        # 默认路径：预算充足 → 全部执行
        calls2 = []

        def fake_distill2(path, dry_run=False):
            calls2.append(path)
            return {"success": True, "raw": path.name, "wiki": "w.md"}

        from pathlib import Path as _P
        orig_distill = kb_distill.distill_one
        orig_pending = kb_distill.pending_distill_list
        try:
            kb_distill.distill_one = fake_distill2
            kb_distill.pending_distill_list = lambda: [
                _P("/tmp/fake/raw/y%d.md" % i) for i in range(3)
            ]
            r2 = kb_distill.run_batch(batch=3)
            self.assert_eq(len(calls2), 3, "预算充足时全部执行")
            self.assert_true("stopped_reason" not in r2,
                             "预算充足时无 stopped_reason")
        finally:
            kb_distill.distill_one = orig_distill
            kb_distill.pending_distill_list = orig_pending

        # CLI 参数已接线
        src = (PROJECT_ROOT / "scripts" / "kb_distill.py").read_text(
            encoding="utf-8")
        self.assert_true("--time-budget" in src, "CLI --time-budget 已接线")
        self.assert_true("time_budget_s=args.time_budget" in src,
                         "CLI 预算参数传入 run_batch")

        # 批量图谱写接口存在（补边写放大修复）
        from kb_graph import add_graph_edges_batch, update_graph_nodes_batch
        self.assert_true(callable(add_graph_edges_batch),
                         "add_graph_edges_batch 批量边写接口存在")
        self.assert_true(callable(update_graph_nodes_batch),
                         "update_graph_nodes_batch 批量节点写接口存在")

    # ── BUG-37 ────────────────────────────────────────────────
    def run_bug37_tests(self, build_frontmatter, parse_frontmatter):
        """frontmatter 行内数组：引号内逗号不得被当分隔符。"""
        tricky = "固体高次谐波辐射的理论分析 (Vampa et al., PRL 2014)"
        fm = {"title": "X",
              "related": [tricky, "13,24,25,28,29", "普通"]}
        built = build_frontmatter(fm)
        back, body = parse_frontmatter(built + "\n\n正文\n")
        self.assert_eq(back.get("related"), fm["related"],
                       "含逗号的列表项往返一致（不被切割）")
        self.assert_eq(body, "正文", "正文不受影响")

        # 二次往返仍一致（幂等）
        built2 = build_frontmatter(back)
        back2, _ = parse_frontmatter(built2 + "\n\n正文\n")
        self.assert_eq(back2.get("related"), fm["related"],
                       "二次往返仍一致（幂等）")

        # 单引号形式
        sq = parse_frontmatter(
            "---\nrelated: ['a, b', 'c']\n---\n\n正文\n")
        self.assert_eq(sq[0].get("related"), ["a, b", "c"],
                       "单引号内的逗号同样不被切割")

        # 无引号形式仍按逗号切分（保持旧行为）
        plain = parse_frontmatter("---\nrelated: [a, b]\n---\n\n正文\n")
        self.assert_eq(plain[0].get("related"), ["a", "b"],
                       "无引号列表仍按逗号切分（旧行为不变）")

        # 空列表
        empty = parse_frontmatter("---\nrelated: []\n---\n\n正文\n")
        self.assert_eq(empty[0].get("related"), [], "空列表解析为空")

        # 标量不受影响
        sc = parse_frontmatter("---\ntitle: 46\ncount: 7\nflag: true\n---\n\n正文\n")
        self.assert_eq(sc[0].get("title"), "46", "纯数字 title 仍为字符串（v7.2.45）")
        self.assert_eq(sc[0].get("count"), 7, "整数推断不变")
        self.assert_eq(sc[0].get("flag"), True, "布尔推断不变")


if __name__ == "__main__":
    import time
    suite = KbDistillFrontmatterTests()
    suite.setup()
    t0 = time.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = time.time() - t0
    from test_runner import print_report
    print_report([suite])
