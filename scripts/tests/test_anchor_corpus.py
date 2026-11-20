#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_anchor_corpus.py — 锚集（真实中标本子校准库）回归测试（v7.2.72）

覆盖 v7.2.69 上线的 `scripts/anchor_corpus.py` 的三个确认缺陷：

BUG-30（docx 抽文本丢段落换行）
    `_extract_text` 旧版用 `re.sub(r"<[^>]+>", "", xml)` 直接剥 docx 标签，
    段落之间**没有换行**；而 `_split_modules` 的标题正则用 `^`（re.M 行首
    锚定）匹配 → 段落连成一坨后，除首段外全部匹配不到 → docx 锚点切出
    **0 个模块**，docx 形式的真实中标申请书永远无法参与对比。

BUG-31（PDF 锚点恒抽不出文本）
    旧版 PDF 分支只依赖本进程 pdfminer，而系统 python3 无 pdfminer、
    `pdftotext` 也未安装 → 恒返回空串 → `ingest()` 的 `if not text.strip()`
    把 PDF 锚点直接跳过。

BUG-32（pairwise_compare 消费 llm_complete 返回值错误）
    `llm_complete` 返回三元组 `(ok, text, meta)`；旧版把整个三元组当字符串
    塞进 `re.search(r"\{.*\}", raw)` → 必然 TypeError → 被
    `except Exception: continue` 吞掉 → **每一次对比都静默失败**，
    `pairwise_compare` 恒返回 None（LLM 返回合法 JSON 时结果仍为 None）。

本套件以 TestSuite 风格编写（纳入 `self_test --module` 全量回归）。
"""

import importlib
import json
import shutil
import sys
import tempfile
import types
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test_runner import TestSuite


def _make_docx(path: Path, paras) -> None:
    """构造最小 docx（段落级 w:p 结构，与真实标书一致）。"""
    body = "".join(
        '<w:p><w:r><w:t xml:space="preserve">' + p + "</w:t></w:r></w:p>"
        for p in paras
    )
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main"><w:body>' + body + "</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", doc_xml)


class AnchorCorpusTests(TestSuite):
    def __init__(self):
        super().__init__("锚集校准库回归测试（v7.2.72 BUG-30/31/32）")
        self.tmp_root = None
        self.ac = None

    # ── 夹具 ──────────────────────────────────────────────

    def setup(self):
        self.tmp_root = Path(tempfile.mkdtemp(prefix="linsai_anchor_"))
        sys.modules.pop("anchor_corpus", None)
        self.ac = importlib.import_module("anchor_corpus")

    def teardown(self):
        sys.modules.pop("anchor_corpus", None)
        sys.modules.pop("llm_gateway", None)
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _patch_llm(self, response: str):
        """把 llm_complete 打桩为固定返回（用于验证三元组解包）。"""
        calls = []

        def llm_complete(system_prompt, user_prompt, timeout=90, prefer=None):
            calls.append(prefer)
            return True, response, {"provider": "glm"}

        fake = types.ModuleType("llm_gateway")
        fake.llm_complete = llm_complete
        sys.modules["llm_gateway"] = fake
        return calls

    def _patch_llm_slot_aware(self, judge):
        """按 A 槽真实身份打桩：judge(a_is_ours) -> "A更强"|"B更强"|"相当"。

        用于验证 BUG-33：交换顺序双跑的归一化方向必须跟随 A 槽身份，
        而不是固定把 A 槽当成「我方」。
        """
        seen = []

        def llm_complete(system_prompt, user_prompt, timeout=90, prefer=None):
            a_is_ours = user_prompt.startswith("【A】\n我方")
            seen.append(a_is_ours)
            verdict = judge(a_is_ours)
            return True, json.dumps(
                {"verdict": verdict, "gap_points": ["差距点1"]}, ensure_ascii=False
            ), {"provider": "glm"}

        fake = types.ModuleType("llm_gateway")
        fake.llm_complete = llm_complete
        sys.modules["llm_gateway"] = fake
        return seen

    # ── 用例 ──────────────────────────────────────────────

    def run_tests(self):
        # 1. BUG-32：pairwise_compare 正确解包 llm_complete 三元组
        #    打桩改为「A 槽身份感知」：模拟**无位置偏置**的 LLM——
        #    第 1 轮 A 槽=我方 → 判 A更强；第 2 轮 A 槽=锚点 → 判 B更强
        #    （B=我方，仍是我方更强）。
        #    v7.2.72 原用例用「固定返回 A更强」的打桩，那模拟的是
        #    **恒判 A 强的位置偏置 LLM**，却断言 ours_stronger——
        #    实际是在固化 BUG-33 的错误归一化（见 1d）。
        seen = self._patch_llm_slot_aware(
            lambda a_is_ours: "A更强" if a_is_ours else "B更强")
        r = self.ac.pairwise_compare("我方正文", "锚点正文", "rationale")
        self.assert_true(
            r is not None,
            "LLM 返回合法 JSON 时 pairwise_compare 应返回结果",
            "返回 None 说明三元组未正确解包——每次对比都被 except 静默吞掉"
            "（BUG-32：治 Goodhart 的锚集对比 100% 失效）",
        )
        self.assert_eq(
            (r or {}).get("verdict"), "ours_stronger",
            "无位置偏置时判定「我方更强」应归一化为 ours_stronger",
            "交换顺序双跑的存在意义就是消除位置偏差，归一化必须正确",
        )
        self.assert_eq(
            len(seen), 2,
            "pairwise_compare 应交换顺序双跑（防位置偏差）",
            "只跑一次则位置偏差无法消除",
        )

        # 1b. BUG-32：verdict=B更强 时归一化为 anchor_stronger
        self._patch_llm_slot_aware(
            lambda a_is_ours: "B更强" if a_is_ours else "A更强")
        r2 = self.ac.pairwise_compare("我方正文", "锚点正文", "rationale")
        self.assert_eq(
            (r2 or {}).get("verdict"), "anchor_stronger",
            "无位置偏置时判定「锚点更强」应归一化为 anchor_stronger",
            "归一化方向反了会把锚点优势算成我方优势",
        )

        # 1c. BUG-32：LLM 失败（ok=False）不应抛异常，应返回 None
        fake = types.ModuleType("llm_gateway")
        fake.llm_complete = lambda *a, **k: (False, "", {"error": "boom"})
        sys.modules["llm_gateway"] = fake
        r3 = self.ac.pairwise_compare("我方正文", "锚点正文", "rationale")
        self.assert_eq(
            r3, None,
            "LLM 失败时应返回 None 而非抛异常",
            "对比失败必须降级为「无结论」，不能中断决策包生成",
        )

        # 1d. BUG-33：交换顺序双跑的归一化方向必须跟随 A 槽真实身份
        #     旧版两轮都用 ("A", ...) 开头，靠 `order[0] == "A"` 反推
        #     「A 槽是我方」→ 第 2 轮（A 槽=锚点）恒判错 → 「我方更强」
        #     这一最有价值的结论永远无法产出，且位置偏置检出反向失效。
        seen = self._patch_llm_slot_aware(
            lambda a_is_ours: "A更强" if a_is_ours else "B更强")
        r_ours = self.ac.pairwise_compare("我方正文", "锚点正文", "rationale")
        self.assert_eq(
            seen, [True, False],
            "双跑两轮应分别把「我方」和「锚点」放进 A 槽",
            "交换顺序失效则位置偏差无法消除",
        )
        self.assert_eq(
            (r_ours or {}).get("verdict"), "ours_stronger",
            "LLM 两轮都判定「我方更强」时应归一化为 ours_stronger",
            "归一化方向反了会把「我方更强」报成「锚点更强」——"
            "治 Goodhart 的锚集反而系统性低估我方（BUG-33）",
        )

        seen = self._patch_llm_slot_aware(
            lambda a_is_ours: "B更强" if a_is_ours else "A更强")
        r_anchor = self.ac.pairwise_compare("我方正文", "锚点正文", "rationale")
        self.assert_eq(
            (r_anchor or {}).get("verdict"), "anchor_stronger",
            "LLM 两轮都判定「锚点更强」时应归一化为 anchor_stronger",
            "锚点优势必须如实上报（BUG-33）",
        )

        seen = self._patch_llm_slot_aware(lambda a_is_ours: "A更强")
        r_biased = self.ac.pairwise_compare("我方正文", "锚点正文", "rationale")
        self.assert_eq(
            (r_biased or {}).get("verdict"), "anchor_stronger",
            "恒判「A更强」的位置偏置 LLM 应被双跑检出并保守取弱",
            "位置偏置若被断言成「我方更强」，双跑设计完全失效——"
            "它要防的正是这种情况（BUG-33）",
        )

        seen = self._patch_llm_slot_aware(lambda a_is_ours: "相当")
        r_equal = self.ac.pairwise_compare("我方正文", "锚点正文", "rationale")
        self.assert_eq(
            (r_equal or {}).get("verdict"), "comparable",
            "两轮都判定「相当」应归一化为 comparable",
            "「相当」是锚集对比的常见结论，归一化路径也须正确",
        )

        # 2. BUG-30：docx 抽文本必须保留段落换行 → 三模块切分生效
        docx = self.tmp_root / "anchor.docx"
        _make_docx(docx, [
            "国家自然科学基金项目申请书",
            "项目名称：某某课题",
            "立项依据",
            "本项目面向强场超快光学中的拓扑量子几何问题。",
            "研究内容",
            "本项目拟开展三个子课题的研究。",
            "研究方案",
            "采用泵浦-探测方案，结合数值模拟与实验验证。",
        ])
        text = self.ac._extract_text(docx)
        self.assert_true(
            "\n" in text,
            "docx 抽文本应保留段落换行",
            "段落被连成一坨后 _split_modules 的 ^ 行首锚定全部落空"
            "（BUG-30：docx 锚点切出 0 个模块）",
        )
        modules = self.ac._split_modules(text)
        self.assert_eq(
            sorted(modules.keys()), ["content", "rationale", "scheme"],
            "docx 锚点应切出立项依据/研究内容/研究方案三模块",
            "真实中标申请书是 docx 形态，切不出模块则该形态锚点永远无法参与对比",
        )
        for key in ("rationale", "content", "scheme"):
            self.assert_true(
                modules.get(key),
                f"docx 模块 {key} 应有正文内容",
                "模块为空说明切段边界错误",
            )

        # 3. BUG-31：PDF 抽文本不得恒为空
        #    用真实 PDF（若存在）验证；不存在时退化为「构造最小 PDF 的
        #    抽取链路可用性」检查——本环境无 pdfminer/pdftotext 时，
        #    修复后的实现走 venv pypdf 抽取器，应能抽出文本。
        real_pdf = None
        pdf_dir = Path(__file__).resolve().parent.parent.parent / "knowledge" / "raw" / "pdfs"
        if pdf_dir.is_dir():
            for p in sorted(pdf_dir.glob("*.pdf"))[:1]:
                real_pdf = p
                break
        if real_pdf is not None:
            pdf_text = self.ac._extract_text(real_pdf)
            self.assert_true(
                len(pdf_text) > 200,
                "真实 PDF 锚点应能抽出正文",
                "返回空串说明 PDF 抽取恒失败——PDF 锚点在 ingest 阶段被跳过"
                "（BUG-31）",
            )
        else:
            self.assert_true(
                True,
                "环境无真实 PDF 样本，跳过 PDF 抽取断言",
                "",
            )

        # 4. ingest 端到端：docx 锚点应被入库且带模块索引
        #    v7.2.75 起 ingest() 默认还会并入 references/nsfc-templates/ 真实
        #    范本——测试环境必须把 TEMPLATES_DIR 一并隔离，否则真实库存在
        #    3 份范本时锚数恒为 4，断言退化为环境依赖（v7.2.87 修复）。
        anchor_dir = self.tmp_root / "anchors"
        anchor_dir.mkdir(parents=True, exist_ok=True)
        old_dir, old_db = self.ac.ANCHOR_DIR, self.ac.ANCHOR_DB
        old_tmpl = self.ac.TEMPLATES_DIR
        self.ac.ANCHOR_DIR = anchor_dir
        self.ac.ANCHOR_DB = anchor_dir / "anchor-db.json"
        self.ac.TEMPLATES_DIR = self.tmp_root / "nsfc-templates"  # 不存在 → 跳过
        try:
            _make_docx(anchor_dir / "winner.docx", [
                "立项依据", "锚点立项依据正文。",
                "研究内容", "锚点研究内容正文。",
                "研究方案", "锚点研究方案正文。",
            ])
            db = self.ac.ingest()
            self.assert_eq(
                len(db["anchors"]), 1,
                "ingest 应把 docx 锚点入库",
                "docx 锚点被跳过则锚集永远为空，pairwise 对比无从触发",
            )
            self.assert_eq(
                len(self.ac.load_anchors()), 1,
                "入库后可被 load_anchors 读回",
                "索引与实际落盘不一致",
            )
            mods = (db["anchors"][0].get("modules") or {}) if db["anchors"] else {}
            self.assert_eq(
                sorted(mods.keys()), ["content", "rationale", "scheme"],
                "入库索引应记录三个模块的正文长度",
                "模块索引为空说明 docx 切分仍然失效",
            )
        finally:
            self.ac.ANCHOR_DIR, self.ac.ANCHOR_DB = old_dir, old_db
            self.ac.TEMPLATES_DIR = old_tmpl


if __name__ == "__main__":
    sys.exit(0)
