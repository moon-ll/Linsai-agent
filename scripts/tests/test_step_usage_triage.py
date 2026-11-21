"""test_step_usage_triage.py — 调用计量账本 + 链路单发化/分诊纯函数回归（v6.10.55）

覆盖：
1. step_usage：记录→月分片落盘→汇总聚合（真实/估算 token、失败行）
2. _extract_gaps_json：直连解析/围栏/嵌套提取/引号修复/垃圾输入
3. _parse_lit_report_papers + _rank_lit_read_ids：报告解析、关键词
   排序、cap 上限、0 命中原序、多源段隔离
4. _valid_brief_text：update_vision 直调产物结构校验
5. hermes_memory._profile_primary_model：config.yaml 主模型归因
6. llm_router 计量包装结构（wrapper + impl 共存）

零污染：临时目录，零 LLM 调用。
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test_runner import TestSuite


class StepUsageTriageTests(TestSuite):
    """计量账本与单发化/分诊纯函数回归。"""

    def __init__(self):
        super().__init__("step_usage_triage")

    def setup(self):
        self._tmp = tempfile.TemporaryDirectory()
        import step_usage
        self._su = step_usage
        self._orig_dir = step_usage.USAGE_DIR
        self._orig_guard = step_usage._in_test_context
        step_usage.USAGE_DIR = Path(self._tmp.name) / "usage"
        step_usage._in_test_context = lambda: False  # 绕过守卫测记录逻辑本身

    def teardown(self):
        self._su.USAGE_DIR = self._orig_dir
        self._su._in_test_context = self._orig_guard
        self._tmp.cleanup()

    def run_tests(self):
        su = self._su

        # ── 1. step_usage 记录与汇总 ──
        self.assert_true(su.record_call(
            "llm_router", "minimax", model="MiniMax-M3", prefer="",
            usage={"prompt_tokens": 100, "completion_tokens": 50},
            elapsed_s=1.5), "真实 usage 记录成功")
        self.assert_true(su.record_call(
            "hermes_agent", "writer", prompt_chars=4000,
            output_chars=2000, elapsed_s=120.0), "hermes 估算记录成功")
        self.assert_true(su.record_call(
            "llm_router", "minimax", success=False, error="429 限流",
            elapsed_s=0.3, prefer="panel"), "失败行记录成功")

        shards = list(su.USAGE_DIR.glob("step-usage-*.jsonl"))
        self.assert_eq(len(shards), 1, "月分片只落一个文件")
        lines = shards[0].read_text(encoding="utf-8").strip().splitlines()
        self.assert_eq(len(lines), 3, "三行 JSONL 流水")
        recs = [json.loads(x) for x in lines]
        self.assert_eq(recs[0]["prompt_tokens"], 100, "真实 prompt token 直取")
        self.assert_true(not recs[0]["tokens_estimated"], "有 usage 不标记估算")
        self.assert_eq(recs[1]["prompt_tokens"], 2000, "估算口径 chars/2")
        self.assert_true(recs[1]["tokens_estimated"], "无 usage 标记估算")
        self.assert_true(not recs[2]["success"], "失败行 success=false")

        s = su.summarize(days=1)
        self.assert_eq(s["total"]["calls"], 3, "汇总调用数")
        self.assert_eq(s["total"]["fails"], 1, "汇总失败数")
        writer_rows = [r for r in s["by_call"] if r["name"] == "writer"]
        self.assert_eq(len(writer_rows), 1, "writer 聚合行存在")
        self.assert_eq(writer_rows[0]["estimated_calls"], 1, "估算计数")
        self.assert_eq(writer_rows[0]["prompt_tokens"], 2000, "聚合 token")

        # ── 1b. 测试上下文守卫 ──
        self.assert_true(su._in_test_context() is False, "守卫默认放行（已 patch）")
        import step_usage as _su_mod
        self.assert_true(_su_mod._in_test_context.__code__ is not None,
                         "守卫函数可调用")
        # 模拟真实入口命中守卫：record_call 应拒绝写入
        _su_mod._in_test_context = lambda: True
        before = list(su.USAGE_DIR.glob("step-usage-*.jsonl"))
        self.assert_true(not su.record_call("llm_router", "minimax"),
                         "守卫生效时拒绝记账")
        self.assert_eq(list(su.USAGE_DIR.glob("step-usage-*.jsonl")), before,
                       "守卫生效时不产生新分片")
        _su_mod._in_test_context = lambda: False  # 恢复，供后续用例

        # ── 2. _extract_gaps_json ──
        from lifecycle.executor import _extract_gaps_json
        self.assert_eq(
            _extract_gaps_json('{"gaps": [{"claim": "x"}]}'),
            {"gaps": [{"claim": "x"}]}, "直连解析")
        self.assert_eq(
            _extract_gaps_json('```json\n{"gaps": []}\n```'),
            {"gaps": []}, "围栏剥离")
        self.assert_true(
            _extract_gaps_json('前缀说明 {"gaps": [{"claim": "论证"光源"五环"}]} 后缀')
            is not None, "前缀+引号修复+配平提取")
        self.assert_true(
            _extract_gaps_json('{"gaps": [{"claim": "论证"光源"五环"}]}')
            is not None, "无前缀引号修复")
        self.assert_eq(
            _extract_gaps_json('说明 {"gaps": [{"a": 1}]} {"noise": true}'),
            {"gaps": [{"a": 1}]}, "嵌套提取取首个含 gaps 对象")
        self.assert_eq(_extract_gaps_json("不是 JSON"), None, "垃圾输入")
        self.assert_eq(_extract_gaps_json(""), None, "空输入")
        self.assert_eq(_extract_gaps_json('{"no_gaps_key": 1}'), None, "缺 gaps 键")

        # ── 3. lit_read 分诊 ──
        from lifecycle.executor import _parse_lit_report_papers, _rank_lit_read_ids, _LIT_READ_CAP
        report = (
            "# 定向文献检索报告\n\n## 课题\np1\n\n## 章节\nrationale\n\n"
            "## 检索关键词\n- crystal orientation、Berry curvature\n\n"
            "## 检索结果\n"
            "- 2401.11111 | Berry curvature effects | A | 2024 | 0.9 | berry curvature response | 来源：联网检索\n"
            "- 2402.22222 | Random unrelated | B | 2024 | 0.8 | nothing here | 来源：联网检索\n"
            "- 2403.33333 | HHG crystal orientation | C | 2025 | 0.7 | crystal orientation study | 来源：联网检索\n"
            "- 2404.44444 | Another | D | 2024 | 0.6 | misc | 来源：联网检索\n"
            "\n## 多源学术检索补充（arxiv+openalex）\n"
            "- arXiv:2405.55555 | Multi | X | 2024 | venue | 引用:3 | 来源：arxiv | abstract\n"
        )
        ps = _parse_lit_report_papers(report)
        self.assert_eq(
            [p["arxiv_id"] for p in ps],
            ["2401.11111", "2402.22222", "2403.33333", "2404.44444"],
            "报告条目按序解析")
        self.assert_true(all("2405.55555" != p["arxiv_id"] for p in ps),
                         "多源补充段不参与分诊")
        self.assert_eq(_parse_lit_report_papers("格式漂移无段落"), [], "格式漂移返回空")

        ranked = _rank_lit_read_ids(ps, "crystal orientation", cap=3)
        self.assert_eq(ranked[0], "2403.33333", "关键词命中者排榜首")
        self.assert_eq(len(ranked), 3, "cap 上限生效")
        self.assert_true("2405.55555" not in ranked, "多源 id 不入深读清单")

        zero = _rank_lit_read_ids(ps, "zzz-no-hit", cap=3)
        self.assert_eq(zero, ["2401.11111", "2402.22222", "2403.33333"],
                       "0 命中保持报告原序（稳定排序）")
        self.assert_eq(_rank_lit_read_ids(ps, "", cap=2),
                       ["2401.11111", "2402.22222"], "空关键词原序+cap")
        self.assert_eq(_LIT_READ_CAP, 3, "深读上限常量为 3")

        # ── 4. _valid_brief_text ──
        from lifecycle.executor import _valid_brief_text
        self.assert_true(_valid_brief_text("# 标题\n" + "x" * 250), "markdown 标题+足量")
        self.assert_true(_valid_brief_text("---\ntitle: x\n---\n" + "y" * 250),
                         "frontmatter 形态")
        self.assert_true(not _valid_brief_text("太短"), "过短拒绝")
        self.assert_true(not _valid_brief_text("a" * 300), "无标题结构拒绝")
        self.assert_true(not _valid_brief_text(""), "空串拒绝")

        # ── 5. profile 主模型归因 ──
        from hermes_memory import _profile_primary_model, _PROFILE_MODEL_CACHE
        _PROFILE_MODEL_CACHE.clear()
        with tempfile.TemporaryDirectory() as td:
            import hermes_memory as hm
            orig = hm._PROFILES_DIR
            hm._PROFILES_DIR = Path(td)
            try:
                pdir = Path(td) / "writer"
                (pdir / "config.yaml").parent.mkdir(parents=True)
                (pdir / "config.yaml").write_text(
                    "model:\n  default: MiniMax-M3\n  provider: minimax-cn\n",
                    encoding="utf-8")
                self.assert_eq(_profile_primary_model("writer"), "MiniMax-M3",
                               "config.yaml 主模型解析")
                self.assert_eq(_profile_primary_model("missing"), "",
                               "缺失 profile 返回空串")
            finally:
                hm._PROFILES_DIR = orig
                _PROFILE_MODEL_CACHE.clear()

        # ── 6. llm_router 计量包装结构 ──
        import llm_router as lr
        self.assert_true(hasattr(lr.LLMRouter, "_call_llm_impl"),
                         "impl 方法存在")
        doc = (lr.LLMRouter.call_llm.__doc__ or "")
        self.assert_true("计量" in doc, "call_llm 为计量包装层")
        self.assert_true(callable(lr._record_llm_call), "记账辅助函数存在")


if __name__ == "__main__":
    suite = StepUsageTriageTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    total = len(suite.results)
    print(f"\n{'✓ 全部通过' if ok == total else '✗ 存在失败'}: {ok}/{total}")
    for r in suite.results:
        if not r.passed:
            print(f"  ✗ {r.name}: {r.msg}")
    sys.exit(0 if ok == total else 1)
