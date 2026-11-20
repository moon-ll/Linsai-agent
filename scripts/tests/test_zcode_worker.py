#!/usr/bin/env python3
"""test_zcode_worker.py — ZCode worker 单元测试（v7.2.30）。

零 LLM：所有 LLM 调用用 stub，验证 worklist 加载、幂等性、prompt 构造、计数。
"""
import json
import sys
from pathlib import Path
from test_runner import TestSuite, create_isolated_env

REAL_ROOT = Path(__file__).parent.parent.parent


def _stub_llm_factory(responses: dict):
    """构造一个可按 prompt 关键词返回不同 body 的 stub LLM。"""
    class _StubLLM:
        def __init__(self, *a, **kw):
            self.calls = 0

        def __call__(self, prompt, **kw):
            self.calls += 1
            if "五要素" in prompt or "kb_distill" in prompt:
                return responses.get("distill", _default_body("distill"))
            if "概念页" in prompt or "林赛理解" in prompt:
                return responses.get("concepts", _default_body("concepts"))
            if "方法卡" in prompt or "参数表" in prompt:
                return responses.get("methods", _default_body("methods"))
            return _default_body("default")

    return _StubLLM


def _default_body(kind: str) -> str:
    if kind == "distill":
        return f"""# 测试蒸馏笔记

## 研究问题
测试研究问题描述，{{"五要素结构完整"}}
长度补充确保 ≥ 200 字。{('x' * 200)}

## 背景
测试背景。

## 方法
测试方法。

## 发现
测试发现。

## 开放方向
测试开放方向。
"""
    if kind == "concepts":
        return f"""# 测试概念

## 定义定位
测试定义。{('y' * 200)}

## 物理内涵
测试物理内涵。{('y' * 200)}

## 关联
测试关联 [[物理信息神经网络]]。

## 林赛理解
测试林赛理解。{('y' * 200)}
"""
    if kind == "methods":
        # v7.2.43：methods 输出为 JSON card（追加回论文页，非新建方法页）
        return ('```json\n'
                '{"method_name": "TDDFT", "principle": "测试原理：' + 'z' * 180 + '", '
                '"understanding": "测试林赛理解：' + 'z' * 100 + '", '
                '"params": [{"item": "截断能", "value": "100 Ry", "source": "本文"}, '
                '{"item": "时间步长", "value": "0.02 a.u.", "source": "本文"}], '
                '"boundary": "测试边界。", "representative": "Sato et al. npj Comput Mater 2025"}\n'
                '```')
    return f"# default body {'x' * 250}"


class ZCodeWorkerTests(TestSuite):
    def __init__(self):
        super().__init__("ZCode worker 单元测试（v7.2.30）")
        self.tmp_root = None
        self._saved_modules = {}

    # ------------------------------------------------------------------
    # 隔离环境 + 模块 stub
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 在隔离目录建 worklist
        (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "knowledge" / "wiki" / "papers").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "knowledge" / "wiki" / "concepts").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "knowledge" / "wiki" / "methods").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "knowledge" / "raw" / "papers").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / ".hermes" / "skills" / "literature-reading").mkdir(parents=True, exist_ok=True)
        # 创建空的 SKILL.md
        (self.tmp_root / ".hermes" / "skills" / "literature-reading" / "SKILL.md").write_text(
            "# literature-reading\n## 五要素\n测试 skill 内容\n", encoding="utf-8"
        )

        # worklist 内容
        (self.tmp_root / "memory" / "distill-worklist.json").write_text(
            json.dumps({
                "emitted_at": "2026-10-16T15:36:10Z",
                "count": 3,
                "task_note": "test distill",
                "targets": [
                    {"raw_name": "2024-test-001.md", "raw_rel": "raw/papers/2024-test-001.md",
                     "digest_hint": "abstract", "arxiv_id": "2401.00001", "mtime": "2026-10-12T00:16:39Z"},
                    {"raw_name": "2024-test-002.md", "raw_rel": "raw/papers/2024-test-002.md",
                     "digest_hint": "fulltext", "arxiv_id": "2401.00002", "mtime": "2026-10-12T00:16:39Z"},
                    {"raw_name": "2024-test-003.md", "raw_rel": "raw/papers/2024-test-003.md",
                     "digest_hint": "abstract", "arxiv_id": "2401.00003", "mtime": "2026-10-12T00:16:39Z"},
                ],
            }, ensure_ascii=False), encoding="utf-8"
        )
        (self.tmp_root / "memory" / "concepts-backfill-worklist.json").write_text(
            json.dumps({
                "emitted_at": "2026-10-06T15:53:55Z",
                "count": 2,
                "task_note": "test concepts",
                "targets": [
                    {"name": "PINN", "freq": 16, "priority_hint": "mid",
                     "sample_sources": ["2511.12512"]},
                    {"name": "贝里联络", "freq": 32, "priority_hint": "high",
                     "sample_sources": ["2401.00005"]},
                ],
            }, ensure_ascii=False), encoding="utf-8"
        )
        # v7.2.43：预建 methods 消费涉及的论文页
        # 2024-test-200.md：无方法卡（待补）；2024-test-done.md：已含 marker（幂等）
        papers_dir = self.tmp_root / "knowledge" / "wiki" / "papers"
        (papers_dir / "2024-test-200.md").write_text(
            "# 测试论文页\n\n## 研究问题\n测试正文。\n", encoding="utf-8")
        (papers_dir / "2024-test-done.md").write_text(
            "# 已补方法卡的论文\n\n<!-- methods-backfill:v1 -->\n**方法**：TDDFT\n",
            encoding="utf-8")
        # worklist 第三条：已消费（幂等用例）
        (self.tmp_root / "memory" / "methods-backfill-worklist.json").write_text(
            json.dumps({
                "emitted_at": "2026-10-18T14:10:44Z",
                "count": 3,
                "task_note": "test methods",
                "targets": [
                    {"method_name": "TDDFT", "page": "2024-test-100", "grade": "A",
                     "fulltext": False, "fulltext_path": "", "has_method_section": True,
                     "raw_stem": "2024-100", "priority_hint": "inline", "source": "all",
                     "prior_status": "no_method"},
                    # 生产端真实形态（v7.2.43 语义对齐后为常规条目）：论文页词干
                    {"page": "2024-test-200", "grade": "A",
                     "fulltext": False, "fulltext_path": "", "has_method_section": True,
                     "raw_stem": "2024-200", "priority_hint": "inline", "source": "all",
                     "prior_status": "no_method"},
                    {"page": "2024-test-done", "grade": "B",
                     "fulltext": False, "fulltext_path": "", "has_method_section": False,
                     "raw_stem": "2024-done", "priority_hint": "inline", "source": "all",
                     "prior_status": "no_method"},
                ],
            }, ensure_ascii=False), encoding="utf-8"
        )

        # 保存并 patch 模块路径
        self._saved_modules = {k: v for k, v in sys.modules.items()
                               if k in ("zcode_worker", "kb_wiki", "kb_distill", "llm_gateway", "scripts", "scripts.llm_gateway")}
        for k in self._saved_modules:
            del sys.modules[k]

        # 替换 ROOT 路径：zcode_worker.py 用 ROOT = __file__.parent.parent
        # 不能直接 patch——改用 monkey-patch zcode_worker.ROOT + zcode_worker.WORKLIST_DIR
        sys.path.insert(0, str(REAL_ROOT / "scripts"))
        import zcode_worker
        self._zcode_worker = zcode_worker
        self._zcode_worker.ROOT = self.tmp_root
        self._zcode_worker.WORKLIST_DIR = self.tmp_root / "memory"
        self._zcode_worker.KNOWLEDGE_DIR = self.tmp_root / "knowledge"
        self._zcode_worker.SKILL_DIR = self.tmp_root / ".hermes" / "skills"

    def teardown(self):
        # 还原模块
        for k in ("zcode_worker", "kb_wiki", "kb_distill", "llm_gateway", "scripts", "scripts.llm_gateway"):
            sys.modules.pop(k, None)
        for k, v in self._saved_modules.items():
            sys.modules[k] = v
        import shutil
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ------------------------------------------------------------------
    # 用例
    # ------------------------------------------------------------------

    def run_tests(self):
        self._test_status_loads_all_three_worklists()
        self._test_prompt_for_distill_contains_five_elements()
        self._test_prompt_for_concepts_contains_linsi_section()
        self._test_prompt_for_methods_contains_param_table()
        self._test_idempotent_already_done_targets()
        self._test_distill_idempotent_matches_write_path()
        self._test_consume_distill_dry_stub()
        self._test_consume_concepts_creates_wiki_file()
        self._test_consume_methods_creates_wiki_file()
        self._test_methods_page_only_target_consumes()
        self._test_methods_bad_json_fails_cleanly()
        self._test_failed_target_kept_in_worklist()
        self._test_consume_all_invokes_each_type()
        self._test_facade_injection_independent_of_distill()

    def _test_status_loads_all_three_worklists(self):
        """status 命令应能加载 3 个 worklist 并打印。"""
        zw = self._zcode_worker
        result = zw.show_status()
        self.assert_eq(len(result), 3, "3 个 worklist 都被加载")
        self.assert_eq(result["distill"]["count"], 3, "distill 3 条")
        self.assert_eq(result["concepts"]["count"], 2, "concepts 2 条")
        self.assert_eq(result["methods"]["count"], 3, "methods 3 条（含幂等用例条目）")

    def _test_prompt_for_distill_contains_five_elements(self):
        """distill prompt 必须含五要素关键词。"""
        zw = self._zcode_worker
        target = {"raw_name": "test.md", "raw_rel": "raw/papers/test.md",
                  "digest_hint": "abstract", "arxiv_id": "2401.00001"}
        p = zw._build_prompt(target, "distill")
        self.assert_true("五要素" in p, "distill prompt 含五要素")
        self.assert_true("研究问题" in p, "distill prompt 含研究问题")
        self.assert_true("2401.00001" in p, "distill prompt 含 arxiv_id")

    def _test_prompt_for_concepts_contains_linsi_section(self):
        """concepts prompt 必须含林赛理解节。"""
        zw = self._zcode_worker
        target = {"name": "PINN", "freq": 16, "priority_hint": "mid", "sample_sources": ["2511.12512"]}
        p = zw._build_prompt(target, "concepts")
        self.assert_true("林赛理解" in p, "concepts prompt 含林赛理解")
        self.assert_true("PINN" in p, "concepts prompt 含概念名")

    def _test_prompt_for_methods_contains_param_table(self):
        """methods prompt 必须含参数表要求。"""
        zw = self._zcode_worker
        target = {"page": "2024-test-200", "raw_stem": "2024-200", "grade": "A"}
        p = zw._build_prompt(target, "methods")
        self.assert_true("JSON" in p and "method_name" in p, "methods prompt 要求 JSON card")
        self.assert_true("2024-test-200" in p, "methods prompt 指向论文页")
        self.assert_true("测试论文页" in p, "methods prompt 嵌入论文页正文")
        self.assert_true("林赛理解" in p, "methods prompt 含 v7.1.3 林赛理解要求")

    def _test_idempotent_already_done_targets(self):
        """已落盘的 target 应被识别（避免重复消费）。"""
        zw = self._zcode_worker
        # 手工创建一个"已落盘"的 distill 产物
        wiki_dir = self.tmp_root / "knowledge" / "wiki" / "papers"
        (wiki_dir / "2024-test-001.md").write_text("# already done\n", encoding="utf-8")
        target = {"raw_name": "2024-test-001.md", "raw_rel": "raw/papers/2024-test-001.md"}
        self.assert_true(zw._check_already_done(target, "distill"), "已落盘视为完成")
        # concepts
        cdir = self.tmp_root / "knowledge" / "wiki" / "concepts"
        (cdir / "PINN.md").write_text("# PINN\n", encoding="utf-8")
        self.assert_true(zw._check_already_done({"name": "PINN"}, "concepts"), "已落盘 PINN 概念页")
        # v7.2.43：methods 已消费 = 论文页含 BACKFILL_MARKER（与 kb_methods_backfill._has_method_card 同口径）
        self.assert_true(
            zw._check_already_done({"page": "2024-test-done"}, "methods"),
            "论文页含 marker 判已消费")
        self.assert_true(
            not zw._check_already_done({"page": "2024-test-200"}, "methods"),
            "论文页无 marker 判未消费（防过度拦截）")

    def _test_distill_idempotent_matches_write_path(self):
        """v7.2.37 BUG-4：distill 幂等判定路径必须与 kb_distill 落盘路径一致。

        落盘走 kb_distill._deep_wiki_rel → _safe_filename(raw.stem)，会把 '.'
        换成 '_'（1911.12092 → 1911_12092）。此前幂等判定直接用 raw 词干拼路径，
        含 '.' 的 raw_name 永远判不出已落盘 → 陈旧条目被反复重蒸馏。
        """
        zw = self._zcode_worker
        raw_name = "2019-1911.12092-cooper-minimum-test.md"
        # 按真实落盘规则（点号换下划线）创建产物
        wiki_dir = self.tmp_root / "knowledge" / "wiki" / "papers"
        (wiki_dir / "2019-1911_12092-cooper-minimum-test.md").write_text(
            "# done\n", encoding="utf-8")
        # 若幂等判定用 raw 词干，这里会去找 2019-1911.12092-...md（不存在）
        self.assert_true(
            zw._check_already_done({"raw_name": raw_name}, "distill"),
            "含点号 raw_name 的已落盘产物应被识别（与 _deep_wiki_rel 同规则）")
        # 反向：未落盘必须仍判 False（防过度拦截）
        self.assert_true(
            not zw._check_already_done(
                {"raw_name": "2099-9999.99999-never-distilled.md"}, "distill"),
            "未落盘仍应判 False")

    def _test_consume_distill_dry_stub(self):
        """消费 distill 1 条（stub LLM + stub 落盘），验证 worklist 减 1。"""
        zw = self._zcode_worker
        # 注入 stub：scripts.llm_gateway.llm_complete + kb_distill.write_distilled_page
        # v7.2.35 修复：原 `from llm_gateway import call_llm` 错误 → 改 `scripts.llm_gateway.llm_complete`
        sys.modules["scripts"] = type(sys)("scripts")
        sys.modules["scripts.llm_gateway"] = type(sys)("scripts.llm_gateway")
        sys.modules["scripts.llm_gateway"].llm_complete = lambda *a, **kw: (True, _default_body("distill"), {})
        # kb_distill 必须真实存在（import from），这里 stub 一个简化版
        sys.modules["kb_distill"] = type(sys)("kb_distill")
        sys.modules["kb_distill"].write_distilled_page = lambda raw, body, level: {
            "raw_name": raw, "body_len": len(body), "digest_level": level
        }
        # 让 write_distilled_page 落盘一个空文件模拟
        import os
        original_stub = sys.modules["kb_distill"].write_distilled_page
        def stub_write(raw, body, level):
            wiki_p = self.tmp_root / "knowledge" / "wiki" / "papers" / raw
            wiki_p.parent.mkdir(parents=True, exist_ok=True)
            wiki_p.write_text(body, encoding="utf-8")
            return {"raw_name": raw, "body_len": len(body), "digest_level": level}
        sys.modules["kb_distill"].write_distilled_page = stub_write

        summary = zw.consume_worklist("distill", batch=1)
        self.assert_eq(summary["consumed"], 1, "consume 1 成功")
        self.assert_eq(summary["remaining"], 2, "剩余 2 条")
        # worklist 文件实际变更
        wl = json.loads((self.tmp_root / "memory" / "distill-worklist.json").read_text())
        self.assert_eq(len(wl["targets"]), 2, "worklist 写回 2 条")
        # 已落盘文件存在
        self.assert_true((self.tmp_root / "knowledge" / "wiki" / "papers" / "2024-test-001.md").exists(),
                         "落盘文件存在")

    def _test_facade_injection_independent_of_distill(self):
        """v7.2.38 BUG-5：concepts 落盘不得依赖 distill 分支的导入副作用。

        kb_wiki._ensure_dirs 是 knowledge_base 门面回填的（kb_wiki 模块顶层
        为 None 占位）。v7.2.37 BUG-4 修复后 distill 全部命中幂等快路径成为常态，
        kb_distill 从不被导入 → 门面永不注入 → save_wiki_page 首行抛
        TypeError: 'NoneType' object is not callable。此用例在纯净模块状态下
        直接验证 concepts 分支能自行完成注入并落盘。
        """
        zw = self._zcode_worker
        # 复现生产纯净态：清掉知识库门面相关模块（含 distill 间接导入的）
        for m in ("knowledge_base", "kb_wiki", "kb_graph", "kb_index",
                  "kb_text", "kb_distill", "kb_health"):
            sys.modules.pop(m, None)

        sys.modules["scripts"] = type(sys)("scripts")
        sys.modules["scripts.llm_gateway"] = type(sys)("scripts.llm_gateway")
        sys.modules["scripts.llm_gateway"].llm_complete = (
            lambda *a, **kw: (True, _default_body("concepts"), {}))

        # 用**真实** kb_wiki 模块：其 _ensure_dirs 顶层为 None 占位，
        # 未被 knowledge_base 门面注入时 save_wiki_page 首行必然 TypeError。
        # （早先用 FakeWiki stub 自带可用的 _ensure_dirs，无法复现故障，
        #  负向验证时用例仍绿 —— 已改为真实模块以保证回归有效性。）
        import importlib
        real_kb_wiki = importlib.import_module("kb_wiki")
        self.assert_true(real_kb_wiki._ensure_dirs is None,
                         "BUG-5 前置：kb_wiki._ensure_dirs 应处于未注入的 None 态")

        captured = {}
        orig_save = real_kb_wiki.save_wiki_page

        def _spy(rel, content, meta=None, append=False):
            captured["rel"] = rel
            captured["meta"] = meta
            return rel

        real_kb_wiki.save_wiki_page = _spy
        try:
            ok = zw._consume_one({"name": "门面注入验证", "freq": 1,
                                  "priority_hint": "mid",
                                  "sample_sources": ["2511.12512"]}, "concepts")
        finally:
            real_kb_wiki.save_wiki_page = orig_save

        self.assert_true(real_kb_wiki._ensure_dirs is not None,
                         "BUG-5：_consume_one 应已触发 knowledge_base 门面注入")
        self.assert_true(ok, "BUG-5：distill 未导入时 concepts 仍应落盘成功")
        self.assert_true(captured.get("rel"), "BUG-5：save_wiki_page 应被调用")
        self.assert_true((captured.get("meta") or {}).get("tags"),
                         "BUG-5：meta.tags 非空（v7.1.3 质量门控必需）")

    def _test_consume_concepts_creates_wiki_file(self):
        """消费 concepts 1 条，验证 wiki/concepts/<slug>.md 创建。"""
        zw = self._zcode_worker
        sys.modules["scripts"] = type(sys)("scripts")
        sys.modules["scripts.llm_gateway"] = type(sys)("scripts.llm_gateway")
        sys.modules["scripts.llm_gateway"].llm_complete = lambda *a, **kw: (True, _default_body("concepts"), {})
        sys.modules["kb_wiki"] = type(sys)("kb_wiki")
        # v7.2.36 BUG-2：worker 现以 meta 形参传 tags/type（v7.1.3 质量门控读它）
        self._meta_capture = []
        def _save(rel, content, meta=None, append=False):
            self._meta_capture.append((rel, meta))
            return rel
        sys.modules["kb_wiki"].save_wiki_page = _save

        # batch=2：第 1 条 贝里联络 未落盘 → 走真实消费；PINN 已由幂等用例预建
        summary = zw.consume_worklist("concepts", batch=2)
        self.assert_eq(summary["consumed"], 2, "concepts consume 2 成功（1 新建 + 1 幂等）")
        self.assert_eq(len(self._meta_capture), 1, "save_wiki_page 仅对新建条目调用 1 次")
        rel, meta = self._meta_capture[0]
        self.assert_true("贝里联络" in rel, f"落盘 slug 为未落盘条目: {rel}")
        self.assert_true((meta or {}).get("tags"), "meta.tags 非空（v7.1.3 质量门控必需）")
        self.assert_eq((meta or {}).get("type"), "concepts", "meta.type=concepts")

    def _test_consume_methods_creates_wiki_file(self):
        """v7.2.43：消费 methods 条目 → 论文页追加方法卡（_append_method_card）+ 台账标 ok。"""
        zw = self._zcode_worker
        sys.modules["scripts"] = type(sys)("scripts")
        sys.modules["scripts.llm_gateway"] = type(sys)("scripts.llm_gateway")
        sys.modules["scripts.llm_gateway"].llm_complete = lambda *a, **kw: (True, _default_body("methods"), {})
        # stub kb_methods_backfill（记录 _append_method_card 调用 + 内存台账）
        appended = []
        ledger = {"pages": {}}
        mod = type(sys)("kb_methods_backfill")
        def _append(page_path, card):
            appended.append((str(page_path), card))
            page_path.write_text(page_path.read_text(encoding="utf-8") + "\n<!-- methods-backfill:v1 -->\n", encoding="utf-8")
        mod._append_method_card = _append
        mod._load_state = lambda: ledger
        mod._save_state = lambda st: ledger.update(st)
        sys.modules["kb_methods_backfill"] = mod

        # batch=3：done 条目幂等跳过，test-100 无论文页（失败），test-200 正常消费
        summary = zw.consume_worklist("methods", batch=3)
        self.assert_eq(summary["consumed"], 2, "methods 消费 2（1 幂等 + 1 新建卡）")
        self.assert_eq(summary["failed"], 1, "论文页不存在的条目记失败")
        self.assert_eq(len(appended), 1, "_append_method_card 恰好调用 1 次")
        page_path, card = appended[0]
        self.assert_true("2024-test-200.md" in page_path, f"追加目标是论文页: {page_path}")
        self.assert_eq(card.get("method_name"), "TDDFT", "card.method_name 解析正确")
        self.assert_true(card.get("params"), "card.params 解析正确")
        self.assert_eq(ledger["pages"].get("2024-test-200", {}).get("status"), "ok", "台账标 ok")
        self.assert_eq(summary["remaining"], 1, "失败条目（论文页缺失）保留在 worklist")

    def _test_methods_page_only_target_consumes(self):
        """v7.2.43 语义对齐：只有 page/raw_stem 的条目（生产端真实形态）正常消费。"""
        zw = self._zcode_worker
        # 重置论文页（前序用例的 _append stub 已写入 marker，避免命中幂等）
        (self.tmp_root / "knowledge" / "wiki" / "papers" / "2024-test-200.md").write_text(
            "# 测试论文页\n\n## 研究问题\n测试正文。\n", encoding="utf-8")
        sys.modules["scripts"] = type(sys)("scripts")
        sys.modules["scripts.llm_gateway"] = type(sys)("scripts.llm_gateway")
        called = []
        sys.modules["scripts.llm_gateway"].llm_complete = lambda *a, **kw: called.append(1) or (True, _default_body("methods"), {})
        appended = []
        mod = type(sys)("kb_methods_backfill")
        mod._append_method_card = lambda p, c: appended.append((str(p), c))
        ledger = {"pages": {}}
        mod._load_state = lambda: ledger
        mod._save_state = lambda st: ledger.update(st)
        sys.modules["kb_methods_backfill"] = mod
        ok = zw._consume_one({"page": "2024-test-200", "grade": "A"}, "methods")
        self.assert_true(ok, "page-only methods 条目消费成功（v7.2.43 新语义）")
        self.assert_eq(len(called), 1, "page-only 条目触发 LLM 调用")
        self.assert_eq(len(appended), 1, "方法卡追加到论文页")

    def _test_methods_bad_json_fails_cleanly(self):
        """v7.2.43：LLM 输出非 JSON（或缺必备字段）→ 判失败保留重试。"""
        zw = self._zcode_worker
        # 重置论文页（避免前序用例的 marker 触发幂等直接返回 True）
        (self.tmp_root / "knowledge" / "wiki" / "papers" / "2024-test-200.md").write_text(
            "# 测试论文页\n\n## 研究问题\n测试正文。\n", encoding="utf-8")
        sys.modules["scripts"] = type(sys)("scripts")
        sys.modules["scripts.llm_gateway"] = type(sys)("scripts.llm_gateway")
        sys.modules["scripts.llm_gateway"].llm_complete = lambda *a, **kw: (True, "# 不是 JSON\n" + "x" * 250, {})
        appended = []
        mod = type(sys)("kb_methods_backfill")
        mod._append_method_card = lambda p, c: appended.append(1)
        mod._load_state = lambda: {"pages": {}}
        mod._save_state = lambda st: None
        sys.modules["kb_methods_backfill"] = mod
        ok = zw._consume_one({"page": "2024-test-200", "grade": "A"}, "methods")
        self.assert_true(not ok, "非 JSON 输出判失败")
        self.assert_eq(len(appended), 0, "无落盘")

    def _test_failed_target_kept_in_worklist(self):
        """失败的 target 保留在 worklist（重试可能成功）。"""
        zw = self._zcode_worker
        # LLM 返回过短
        sys.modules["scripts"] = type(sys)("scripts")
        sys.modules["scripts.llm_gateway"] = type(sys)("scripts.llm_gateway")
        sys.modules["scripts.llm_gateway"].llm_complete = lambda *a, **kw: (True, "x" * 100, {})
        sys.modules["kb_distill"] = type(sys)("kb_distill")
        sys.modules["kb_distill"].write_distilled_page = lambda *a, **kw: None

        summary = zw.consume_worklist("distill", batch=1)
        self.assert_eq(summary["consumed"], 0, "失败时不计数")
        self.assert_eq(summary["failed"], 1, "失败数=1")
        wl = json.loads((self.tmp_root / "memory" / "distill-worklist.json").read_text())
        # distill 之前可能已消费 1 条，剩余 2 条
        # 这条不成功的话，所有 2 条都还在
        self.assert_true(len(wl["targets"]) >= 2, "失败 target 保留")

    def _test_consume_all_invokes_each_type(self):
        """consume all 应分别跑 3 种类型。"""
        zw = self._zcode_worker
        sys.modules["scripts"] = type(sys)("scripts")
        sys.modules["scripts.llm_gateway"] = type(sys)("scripts.llm_gateway")
        sys.modules["scripts.llm_gateway"].llm_complete = lambda *a, **kw: (True, _default_body("default"), {})
        sys.modules["kb_wiki"] = type(sys)("kb_wiki")
        sys.modules["kb_wiki"].save_wiki_page = lambda rel, content: rel
        sys.modules["kb_distill"] = type(sys)("kb_distill")
        sys.modules["kb_distill"].write_distilled_page = lambda *a, **kw: {"x": 1}

        result = zw.consume_worklist("all", batch=1)
        self.assert_eq(result["success"], True, "consume all 返回 success")
        self.assert_eq(len(result["per_type"]), 3, "3 种类型都被处理")


if __name__ == "__main__":
    suite = ZCodeWorkerTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    import test_runner
    test_runner.print_report([suite])
    sys.exit(0 if suite.summary()["failed"] == 0 else 1)
