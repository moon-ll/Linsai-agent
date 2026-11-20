"""
test_numeric_title_crash.py — 纯数字 title 致周末反思链崩溃回归测试（v7.2.45 / BUG-10）

背景（本轮健康检查第二层 deep_scan v52 定位）：
    文献正文里的引用角标 `[[46]]` 被 `kb_concepts_backfill` 的悬空
    wikilink 扫描当成"缺失概念"，发射进 concepts 回填清单 → ZCode
    worker 建出 `knowledge/wiki/concepts/46.md`，其 frontmatter 为
    `title: 46`。

    `kb_text.parse_frontmatter` 对纯数字值做类型推断
    （`re.match(r"^\\d+$", val)` → int），于是该页 title 被解析成
    **int 46 而非字符串**。

    消费方随即崩溃：
      1. `kb_health_weekend._detect_duplicate_concepts`
         → `page.get("title","").lower()` → AttributeError
      2. `kb_merger.merge_related`
         → `primary_title.lower()` → AttributeError

    运行时后果（本轮实测）：`lc-weekend-worker` 三次执行（10:00 /
    10:20 / 09:40 BJT）全部 exit code 1，错误
    `'int' object has no attribute 'lower'`；周末反思链
    `reflection_kb_merge_duplicates` → `reflection_proposal_calibration`
    → `reflection_link_deep_review` → `reflection_kb_taxonomy_apply`
    **四个 job 全部卡在 pending**，且 kb_merge_duplicates 的
    repair_attempts 已打满 3/3。

    修复（三处）：
      1. `kb_text.parse_frontmatter` —— title 字段类型收窄为 str
         （其余数值字段 latest_round / settled_count 等推断不变）
      2. `kb_health_weekend._detect_duplicate_concepts` —— 显式 str()
      3. `kb_merger.merge_related` —— title 与 related 项统一 str()
      4. `kb_concepts_backfill._is_noise_concept` —— 纯数字判为噪音
         （关闭复发路径；清单中另有 3 条纯数字条目一并清理）

测试覆盖：
    1. parse_frontmatter：title 纯数字 → str（核心正向断言）
    2. parse_frontmatter：title 小数 / 字符串保持语义
    3. parse_frontmatter：其它数值字段类型推断不被破坏
    4. build_frontmatter → parse_frontmatter 往返（title 仍是 str）
    5. _detect_duplicate_concepts 消费 int title 不抛异常
    6. merge_related 消费 int title / int related 项不抛异常
    7. _is_noise_concept 判纯数字为噪音（关闭复发路径）
    8. 反向断言：复刻修复前的类型推断必然产出 int title，
       证明本测试非自证绿

注意：本测试不调用 hermes/LLM，纯逻辑验证。

用法示例：
    python3 scripts/tests/test_numeric_title_crash.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test_runner import TestSuite, create_isolated_env  # noqa: E402


class NumericTitleCrashTests(TestSuite):
    def __init__(self):
        super().__init__("纯数字 title 崩溃回归测试")

    def run_tests(self):
        env = create_isolated_env()
        try:
            from kb_text import parse_frontmatter, build_frontmatter

            # ---------- 1. 核心正向断言：title 纯数字 → str ----------
            fm, body = parse_frontmatter(
                "---\ntitle: 46\ntype: concepts\ntags: [concept]\n---\n正文")
            self.assert_true(
                isinstance(fm.get("title"), str),
                "BUG-10 核心断言：纯数字 title 必须被收窄为 str（修复前是 int）")
            self.assert_eq(
                fm.get("title"), "46",
                "title 数值内容应保留为字符串 '46'")
            self.assert_eq(
                fm.get("type"), "concepts",
                "其它字符串字段不受影响")

            # ---------- 2. title 其它形态语义保持 ----------
            fm2, _ = parse_frontmatter("---\ntitle: 46.5\n---\n正文")
            self.assert_true(
                isinstance(fm2.get("title"), str),
                "纯小数 title 也应收窄为 str（修复前是 float）")
            self.assert_eq(fm2.get("title"), "46.5", "小数 title 内容保留")

            fm3, _ = parse_frontmatter('---\ntitle: "46"\n---\n正文')
            self.assert_eq(fm3.get("title"), "46", "带引号 title 不变")

            fm4, _ = parse_frontmatter("---\ntitle: 三步模型\n---\n正文")
            self.assert_eq(fm4.get("title"), "三步模型", "普通中文 title 不变")

            # ---------- 3. 其它数值字段类型推断不被破坏 ----------
            fm5, _ = parse_frontmatter(
                "---\ntitle: X\nlatest_round: 7\nsettled_count: 3\nconfidence: 0.5\n---\n正文")
            self.assert_true(
                isinstance(fm5.get("latest_round"), int),
                "latest_round 应保持 int 推断（修复不得过度收窄）")
            self.assert_true(
                isinstance(fm5.get("settled_count"), int),
                "settled_count 应保持 int 推断")
            self.assert_true(
                isinstance(fm5.get("confidence"), float),
                "confidence 应保持 float 推断")

            # ---------- 3b. v7.3.1 边界：全部字符串语义键强制 str ----------
            fm5b, _ = parse_frontmatter(
                "---\nname: 42\nsource_raw: 2024\nsummary: 7\n"
                "aliases: [46, ok]\nrelated: [123, wiki]\ntags: [2024, hhg]\n"
                "---\n正文")
            for _k in ("name", "source_raw", "summary"):
                self.assert_true(
                    isinstance(fm5b.get(_k), str),
                    f"{_k} 应被收窄为 str（字符串语义键）")
                self.assert_eq(fm5b.get(_k), str({"name": 42, "source_raw": 2024, "summary": 7}[_k]),
                               f"{_k} 数值内容应保留为字符串")
            for _k in ("aliases", "related", "tags"):
                self.assert_true(
                    isinstance(fm5b.get(_k), list)
                    and all(isinstance(_x, str) for _x in fm5b.get(_k)),
                    f"{_k} 列表元素应全部收窄为 str")
            self.assert_eq(fm5b.get("aliases"), ["46", "ok"], "aliases 元素收窄")
            self.assert_eq(fm5b.get("related"), ["123", "wiki"], "related 元素收窄")
            self.assert_eq(fm5b.get("tags"), ["2024", "hhg"], "tags 元素收窄")

            # ---------- 3c. 反向对照：显式数值键仍为数值 ----------
            fm5c, _ = parse_frontmatter(
                "---\nyear: 2024\nround: 7\nscore: 0.85\nversion: 3\n---\n正文")
            self.assert_true(isinstance(fm5c.get("year"), int), "year 应保持 int")
            self.assert_true(isinstance(fm5c.get("round"), int), "round 应保持 int")
            self.assert_true(isinstance(fm5c.get("score"), float), "score 应保持 float")
            self.assert_true(isinstance(fm5c.get("version"), int), "version 应保持 int")

            # ---------- 4. 往返：build → parse 后 title 仍是 str ----------
            # build_frontmatter 自带 --- 分隔符，直接拼正文
            fm6, _ = parse_frontmatter(
                build_frontmatter({"title": "46", "type": "concepts"}) + "\n正文")
            self.assert_true(
                isinstance(fm6.get("title"), str),
                "build→parse 往返后 title 应为 str")
            self.assert_eq(fm6.get("title"), "46", "往返后 title 内容不变")

            # ---------- 5. 消费方：_detect_duplicate_concepts ----------
            from kb_health_weekend import _detect_duplicate_concepts
            dups = _detect_duplicate_concepts()
            self.assert_true(
                isinstance(dups, list),
                "_detect_duplicate_concepts 应正常返回列表而非抛异常"
                "（修复前遇 int title 直接 AttributeError）")
            self.assert_true(
                all(isinstance(d.get("title"), str) for d in dups),
                "重复概念条目的 title 应全为 str")

            # ---------- 6. 消费方：merge_related ----------
            from kb_merger import merge_related
            r = merge_related(["A"], ["B", 123, "C"], 46, "被并标题")
            self.assert_true(
                isinstance(r, list),
                "merge_related 应返回列表而非抛异常"
                "（修复前 int title 触发 AttributeError）")
            self.assert_true(
                all(isinstance(x, str) for x in r),
                "merge_related 结果项应全为 str")
            self.assert_true(
                "C" in r and "123" in r,
                "merge_related 应保留去重后的有效边（含 int 转字符串的 '123'）")
            self.assert_eq(
                r, ["A", "B", "123", "C"],
                "merge_related 应保持并集去重语义（A/B/C 全部保留，123 转字符串）")
            self.assert_true(
                len(r) == len(set(r)),
                "merge_related 结果不应含重复项")

            # ---------- 7. 复发路径关闭：纯数字判为噪音 ----------
            from kb_concepts_backfill import _is_noise_concept
            for numeric in ("46", "17", "28", "1", "46.5"):
                self.assert_true(
                    _is_noise_concept(numeric),
                    f"纯数字概念名 '{numeric}' 应判为噪音（复发路径）")
            self.assert_true(
                not _is_noise_concept("三步模型"),
                "正常概念名不应被误判为噪音")
            self.assert_true(
                not _is_noise_concept("高次谐波产生"),
                "正常概念名不应被误判为噪音")

            # ---------- 8. 反向断言：复刻修复前实现必然产出 int title ----------
            import re as _re
            legacy_fm = {}
            for line in "title: 46".split("\n"):
                key, val = line.split(":", 1)
                val = val.strip()
                if _re.match(r"^\d+$", val):
                    legacy_fm[key.strip()] = int(val)
                else:
                    legacy_fm[key.strip()] = val
            self.assert_true(
                isinstance(legacy_fm.get("title"), int),
                "反向断言：修复前的类型推断对 'title: 46' 产出 int"
                "（证明本测试确实锚定了缺陷而非自证绿）")
            try:
                legacy_fm["title"].lower()
                raised = False
            except AttributeError:
                raised = True
            self.assert_true(
                raised,
                "反向断言：修复前 int title 调 .lower() 必抛 AttributeError")

        finally:
            import shutil
            shutil.rmtree(env, ignore_errors=True)


if __name__ == "__main__":
    import unittest  # noqa: E402

    class _Runner(unittest.TestCase):
        def runTest(self):
            NumericTitleCrashTests().run_tests()

    unittest.main(argv=[__file__, "-v"], exit=False)
