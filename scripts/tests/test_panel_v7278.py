#!/usr/bin/env python3
"""v7.2.78 评审团机制接入测试（钩子链 + 口径注入 + 锚集守卫）。

覆盖：
1. _count_long_sentences：超长句（>120 字）计数、正常文本零计数、
   缺失章节容错
2. _params_supplement_block：有口径表注入 canonical；有
   params-conflicts.json 时附待清项；无表 fail-open 返回空串
3. _anchor_gate：compare_proposal 返回 anchor_stronger → 挂起；
   返回 None（无锚集）→ 放行；异常 → 放行（fail-open）
4. run_panel 源码守卫：落盘钩子三环存在、verify 口径靶子条件注入、
   自动晋级走 _anchor_gate 分支

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_panel_v7278.py
"""

import importlib.util
import json
import sys
import tempfile
import types
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


class PanelV7278Tests(TestSuite):
    def __init__(self):
        super().__init__("v7.2.78 评审团机制接入测试")
        self.tmp_root = None

    def assert_true(self, condition, name, msg: str = "") -> bool:
        # 本套件调用习惯为 (名称, 条件)，翻转对齐基类签名
        if isinstance(condition, str):
            condition, name = name, condition
        return super().assert_true(bool(condition), str(name), msg)

    def setup(self):
        self.tmp_root = Path(tempfile.mkdtemp(prefix="panel-v7278-"))

    def teardown(self):
        pass

    def run_tests(self):
        if self.tmp_root is None:
            self.setup()
        self.test_long_sentences()
        self.test_params_block()
        self.test_anchor_gate()
        self.test_run_panel_wiring()

    # ─────────────────────────────────────────────
    # 1. _count_long_sentences
    # ─────────────────────────────────────────────
    def test_long_sentences(self):
        from panel_review import _count_long_sentences, LONG_SENTENCE_THRESHOLD

        prop_dir = self.tmp_root / "prop-a"
        sec = prop_dir / "04_proposal" / "sections"
        sec.mkdir(parents=True)
        long_sentence = "这" * (LONG_SENTENCE_THRESHOLD + 10) + "。"
        (sec / "rationale.md").write_text(
            f"这是正常短句。{long_sentence}", encoding="utf-8")
        (sec / "content.md").write_text("正常内容，没有超长句。", encoding="utf-8")
        self.assert_true(
            "超长句计数为 1（130 字句命中，短句不命中）",
            _count_long_sentences(prop_dir) == 1,
        )
        # scheme.md 缺失不报错
        empty_dir = self.tmp_root / "prop-b"
        (empty_dir / "04_proposal" / "sections").mkdir(parents=True)
        (empty_dir / "04_proposal" / "sections" / "content.md").write_text(
            "短句。", encoding="utf-8")
        self.assert_true(
            "缺失章节容错且正常文本零计数",
            _count_long_sentences(empty_dir) == 0,
        )
        # 空目录
        none_dir = self.tmp_root / "prop-c"
        none_dir.mkdir()
        self.assert_true("无 sections 目录返回 0", _count_long_sentences(none_dir) == 0)

    # ─────────────────────────────────────────────
    # 2. _params_supplement_block
    # ─────────────────────────────────────────────
    def test_params_block(self):
        from panel_review import _params_supplement_block

        # 无口径表 → 空串
        bare = self.tmp_root / "prop-bare"
        (bare / "04_proposal").mkdir(parents=True)
        self.assert_true("无口径表 fail-open 返回空串",
                         _params_supplement_block(bare) == "")

        # 有口径表 → 注入 canonical
        p1 = self.tmp_root / "prop-params"
        (p1 / "04_proposal").mkdir(parents=True)
        (p1 / "04_proposal" / "params.json").write_text(json.dumps({
            "entries": [{"key": "原子数", "canonical": "双层 12,400",
                         "stale_patterns": [r"11,?000"], "note": "口径"}],
        }, ensure_ascii=False), encoding="utf-8")
        blk = _params_supplement_block(p1)
        self.assert_true("口径块含 canonical 值", "12,400" in blk)
        self.assert_true("口径块含禁用模式", "11,?000" in blk)

        # + params-conflicts.json → 附待清项
        (p1 / "05_review").mkdir()
        (p1 / "05_review" / "params-conflicts.json").write_text(json.dumps({
            "active": True,
            "conflicts": [{"key": "原子数", "canonical": "双层 12,400",
                           "hits": [{"section": "scheme.md", "count": 2}]}],
        }, ensure_ascii=False), encoding="utf-8")
        blk2 = _params_supplement_block(p1)
        self.assert_true("待清项注入含残留位置", "scheme.md×2" in blk2)
        self.assert_true("待清项标注口径 key", "原子数" in blk2)

    # ─────────────────────────────────────────────
    # 3. _anchor_gate（mock anchor_corpus）
    # ─────────────────────────────────────────────
    def test_anchor_gate(self):
        from panel_review import _anchor_gate

        saved = {k: sys.modules.get(k) for k in ("anchor_corpus",)}

        def _install(compare_return):
            fake = types.ModuleType("anchor_corpus")

            def compare_proposal(pid, module="rationale"):
                return compare_return

            fake.compare_proposal = compare_proposal
            sys.modules["anchor_corpus"] = fake

        try:
            # 落败 → 挂起（返回原因）
            _install({"module": "rationale",
                      "final": {"verdict": "anchor_stronger",
                                "anchor": "/x/anchors/parsed/范本A.json",
                                "gap_points": ["操作性五问缺答", "指标口径模糊"]},
                      "per_anchor": []})
            held = _anchor_gate("pid-x")
            self.assert_true("anchor_stronger 触发挂起", "rationale 不及锚点" in held)
            self.assert_true("挂起原因含锚点名", "范本A" in held)

            # comparable → 放行
            _install({"module": "rationale",
                      "final": {"verdict": "comparable", "anchor": "/x/a.json",
                                "gap_points": []},
                      "per_anchor": []})
            self.assert_true("comparable 放行", _anchor_gate("pid-x") == "")

            # 无锚集（None）→ 放行
            _install(None)
            self.assert_true("无锚集 fail-open 放行", _anchor_gate("pid-x") == "")

            # 异常 → 放行
            def _boom(pid, module="rationale"):
                raise RuntimeError("boom")
            fake = types.ModuleType("anchor_corpus")
            fake.compare_proposal = _boom
            sys.modules["anchor_corpus"] = fake
            self.assert_true("锚集异常 fail-open 放行", _anchor_gate("pid-x") == "")
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v

    # ─────────────────────────────────────────────
    # 4. run_panel 源码守卫
    # ─────────────────────────────────────────────
    def test_run_panel_wiring(self):
        src = (_SCRIPTS_DIR / "panel_review.py").read_text(encoding="utf-8")
        self.assert_true("落盘钩子链注释存在（阶段 B+）", "阶段 B+" in src)
        self.assert_true("draft 同步守卫接入（ProposalSections.assemble_draft）",
                         "assemble_draft" in src)
        self.assert_true("口径落盘校验接入（run_check_and_persist）",
                         "run_check_and_persist" in src)
        self.assert_true("长句自检门接入（_count_long_sentences 调用）",
                         src.count("_count_long_sentences(") >= 2)
        self.assert_true("仅修句补丁红线（禁改技术内容）",
                         "禁止改动任何技术内容、数值、公式、引用编号" in src)
        self.assert_true("verify prompt 含口径靶子条件注入",
                         "口径落盘校验靶子" in src and "if params_conflict_n" in src)
        self.assert_true("自动晋级走 _anchor_gate 分支",
                         "_anchor_gate(proposal_id)" in src
                         and "held_anchor_stronger" in src)
        self.assert_true("锚集挂起写 06_panel 记录",
                         "panel-anchor-verdict.md" in src)
        self.assert_true("三角色 prompt 传口径块（params_supplement=）",
                         "params_supplement=params_supp" in src)
        # 真模块可导入（非 mock）
        spec = importlib.util.find_spec("anchor_corpus")
        self.assert_true("anchor_corpus 真模块存在", spec is not None)


if __name__ == "__main__":
    suite = PanelV7278Tests()
    suite.run_tests()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"\n{'✓' if suite.results and len(suite.results) - ok == 0 else '✗'} {suite.name}: {ok}/{len(suite.results)} 通过")
    for r in suite.results:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    raise SystemExit(1 if len(suite.results) - ok else 0)
