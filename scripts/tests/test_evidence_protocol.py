#!/usr/bin/env python3
"""
test_evidence_protocol.py — v7.2.67 PaperQA2 式证据协议块回归测试

覆盖 _build_evidence_protocol_block（scripts/proposal_lifecycle/optimize.py）：
    1. scheme 轮：证据池清单列出全部存在文件（相对路径）+ 四条核心纪律关键词
       + 方法参数溯源附加要求
    2. rationale / content 轮：返回空串（避免 prompt 膨胀）
    3. 无证据文件：返回精简协议不崩（禁新增无出处论断）
    4. references 轮：含「逐字段」对照三池誊写附加要求
    5. full_review 轮：精简版只给前两条纪律（③杜撰/④canonical 不出现）
    6. lit-gap 多份时按 mtime 取最新 1 份；candidates.bib 精确名优先、
       targeted-research/candidates-*.bib 布局回退可探测
    7. 部分证据文件缺失时只列存在的（不列缺席者）
    8. prop_dir=None 时 fail-open 不抛异常

注意：
    本测试不调用 hermes/LLM，仅验证纯文件系统探测 + 文本拼装逻辑。
"""

import os
import sys
import time
import importlib
from pathlib import Path

from test_runner import TestSuite, create_isolated_env


class EvidenceProtocolTests(TestSuite):
    def __init__(self):
        super().__init__("证据协议块注入测试")
        self.tmp_root = None
        self._opt = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        # 重新导入模块，避免复用其他测试的全局状态
        for mod_name in [
            "proposal_lifecycle.optimize",
            "proposal_lifecycle",
            "proposal_sections",
        ]:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
        importlib.import_module("proposal_lifecycle.optimize")
        from proposal_lifecycle.optimize import OptimizeMixin

        # 最小实例：不触发 LLM / 日志
        class _Fake(OptimizeMixin):
            def __init__(self):
                pass

        self._opt = _Fake()

    def teardown(self):
        # create_isolated_env 创建的临时目录由框架回收
        pass

    @staticmethod
    def _make_prop(root: Path, name: str = "test-evidence") -> Path:
        """构造一个含全部证据文件的课题目录（tempfile 布局）。"""
        prop = root / "research_proposals" / "optimizing" / name
        (prop / "02_literature" / "targeted-research").mkdir(parents=True)
        (prop / "03_method").mkdir(parents=True)
        (prop / "04_proposal").mkdir(parents=True)
        (prop / "02_literature" / "targeted-research" / "lit-gap-100.md").write_text(
            "# 定向文献检索报告\n", encoding="utf-8")
        (prop / "02_literature" / "reading-notes.md").write_text(
            "# 文献阅读笔记\n", encoding="utf-8")
        (prop / "02_literature" / "candidates.bib").write_text(
            "@article{demo2026}\n", encoding="utf-8")
        (prop / "03_method" / "kb-methods-pack.md").write_text(
            "# KB 方法素材包\n", encoding="utf-8")
        (prop / "03_method" / "method-manual.md").write_text(
            "# 方法学手册\n", encoding="utf-8")
        (prop / "04_proposal" / "params.json").write_text(
            '{"entries": {}}', encoding="utf-8")
        return prop

    def run_tests(self):
        opt = self._opt
        build = opt._build_evidence_protocol_block

        # ---------- 1. scheme 轮：全量证据池 + 四条纪律 ----------
        prop = self._make_prop(self.tmp_root, "full-pool")
        block = build("full-pool", prop, "scheme")
        for rel in (
            "02_literature/targeted-research/lit-gap-100.md",
            "02_literature/reading-notes.md",
            "02_literature/candidates.bib",
            "03_method/kb-methods-pack.md",
            "03_method/method-manual.md",
            "04_proposal/params.json",
        ):
            self.assert_in(
                rel, block,
                f"scheme 轮证据池清单应包含存在文件：{rel}",
            )
        # 四条核心纪律关键词：①逐一读取 ②[N] 引用与「方案设定值（待标定）」
        # ③杜撰红线 ④canonical 口径
        for kw in ("逐一读取", "[N]", "方案设定值（待标定）", "杜撰", "canonical"):
            self.assert_in(kw, block, f"scheme 轮协议块应含纪律关键词：{kw}")
        self.assert_in("方法参数溯源", block, "scheme 轮应含方法参数溯源附加要求")
        self.assert_true(block.startswith("\n\n【证据池协议"), "协议块以空行+标题起始")

        # ---------- 2. rationale / content 轮：返回空串 ----------
        self.assert_eq(
            build("full-pool", prop, "rationale"), "",
            "rationale 轮返回空串（避免 prompt 膨胀）",
        )
        self.assert_eq(
            build("full-pool", prop, "content"), "",
            "content 轮返回空串（避免 prompt 膨胀）",
        )

        # ---------- 3. 无证据文件：精简协议不崩 ----------
        empty_prop = self.tmp_root / "research_proposals" / "optimizing" / "no-evidence"
        empty_prop.mkdir(parents=True)
        block3 = build("no-evidence", empty_prop, "scheme")
        self.assert_true(
            isinstance(block3, str) and len(block3) > 0,
            "证据池全空时返回非空精简协议（不崩）",
        )
        self.assert_in("证据池为空", block3, "精简协议声明证据池为空")
        self.assert_in(
            "方案设定值（待标定）", block3,
            "精简协议仍要求无出处论断标注「方案设定值（待标定）」",
        )
        self.assert_in("杜撰", block3, "精简协议保留杜撰红线")

        # ---------- 4. references 轮：逐字段对照三池誊写 ----------
        block4 = build("full-pool", prop, "references")
        self.assert_in("逐字段", block4, "references 轮附加要求含「逐字段」")
        self.assert_in("candidates", block4, "references 轮三池含 candidates BibTeX")
        for kw in ("逐一读取", "[N]", "杜撰", "canonical"):
            self.assert_in(kw, block4, f"references 轮仍含完整四条纪律：{kw}")

        # ---------- 5. full_review 轮：精简版只给前两条 ----------
        block5 = build("full-pool", prop, "full_review")
        self.assert_in("逐一读取", block5, "full_review 精简版保留纪律①")
        self.assert_in("[N]", block5, "full_review 精简版保留纪律②")
        self.assert_true(
            "杜撰" not in block5 and "记忆转录" not in block5,
            "full_review 精简版不含纪律③（杜撰红线）",
        )
        self.assert_true(
            "以 canonical 条目为准" not in block5,
            "full_review 精简版不含纪律④（canonical 口径）",
        )
        self.assert_in(
            "03_method/kb-methods-pack.md", block5,
            "full_review 精简版仍列证据池清单",
        )

        # ---------- 6. lit-gap 取 mtime 最新 1 份 / candidates 布局回退 ----------
        prop6 = self._make_prop(self.tmp_root, "mtime-pick")
        old_gap = prop6 / "02_literature" / "targeted-research" / "lit-gap-200.md"
        old_gap.write_text("# 旧报告\n", encoding="utf-8")
        # 把 lit-gap-200.md 的 mtime 压到过去 → lit-gap-100.md 仍是最新
        os.utime(old_gap, (time.time() - 86400, time.time() - 86400))
        block6 = build("mtime-pick", prop6, "scheme")
        self.assert_in("lit-gap-100.md", block6, "lit-gap 取 mtime 最新一份（100）")
        self.assert_true(
            "lit-gap-200.md" not in block6, "旧 lit-gap 不入清单",
        )
        # candidates.bib 精确名优先于 candidates-*.bib
        (prop6 / "02_literature" / "targeted-research" / "candidates-300.bib").write_text(
            "@article{multi}\n", encoding="utf-8")
        block6b = build("mtime-pick", prop6, "scheme")
        self.assert_in(
            "02_literature/candidates.bib", block6b,
            "candidates.bib 精确名优先于 candidates-*.bib",
        )
        self.assert_true(
            "candidates-300.bib" not in block6b,
            "存在精确名 candidates.bib 时不列 candidates-*.bib",
        )
        # 无精确名时回退 targeted-research/candidates-*.bib（真实布局）
        prop6c = self._make_prop(self.tmp_root, "bib-fallback")
        (prop6c / "02_literature" / "candidates.bib").unlink()
        (prop6c / "02_literature" / "targeted-research" / "candidates-400.bib").write_text(
            "@article{fallback}\n", encoding="utf-8")
        block6c = build("bib-fallback", prop6c, "scheme")
        self.assert_in(
            "02_literature/targeted-research/candidates-400.bib", block6c,
            "无精确名时回退探测 targeted-research/candidates-*.bib",
        )

        # ---------- 7. 部分证据文件缺失：只列存在的 ----------
        prop7 = self._make_prop(self.tmp_root, "partial-pool")
        (prop7 / "03_method" / "kb-methods-pack.md").unlink()
        (prop7 / "04_proposal" / "params.json").unlink()
        block7 = build("partial-pool", prop7, "scheme")
        self.assert_in("02_literature/reading-notes.md", block7, "存在文件照常列入")
        self.assert_true(
            "kb-methods-pack.md" not in block7, "缺失的方法卡素材包不入清单",
        )
        self.assert_true(
            "04_proposal/params.json" not in block7,
            "缺失的口径表不入清单（纪律④措辞中的 params.json 属恒定文本，不算列入清单）",
        )

        # ---------- 8. prop_dir=None：fail-open 不抛异常 ----------
        self.assert_no_exception(
            build, "prop_dir=None 时 fail-open 不抛异常",
            "ghost-proposal", None, "scheme",
        )


if __name__ == "__main__":
    import time as _t
    suite = EvidenceProtocolTests()
    suite.setup()
    t0 = _t.time()
    suite.run_tests()
    suite.teardown()
    suite.duration = _t.time() - t0
    from test_runner import print_report
    print_report([suite])
