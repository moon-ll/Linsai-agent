# -*- coding: utf-8 -*-
"""provenance_audit 回归测试（v8.0.99）。

覆盖动机：NSDR 包抽检发现"摘要级 raw 溯源被标全文核实"的溯源级别错位，
本工具将其模式化。用临时目录合成包验证：bib 解析、级别判定、
级别错位发现、悬空键发现、干净包零发现。

零 LLM / 零真实数据触碰。
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from provenance_audit import _bib_entries, _source_level, audit_topic  # noqa: E402

BIB_INFLATED = """% 注释
@article{RawClaim2026ref1,
  title = {Something},
  note = {数值出处 [ref:12] 全文核实},
  source: knowledge/raw/papers/2026-2606.02238-x.md
}

@article{WikiClaim2026ref2,
  title = {Other},
  note = {全文核实},
  source : knowledge/wiki/papers/2024-2405_12603-y.md
}
"""

REPORT = """正文引用 [ref:RawClaim2026ref1] 与 [ref:WikiClaim2026ref2]。
另有悬空 [ref:Ghost2026refX]。
"""


def _make_topic(root: Path, tid: str, bib: str, report: str) -> Path:
    d = root / "ready" / tid
    (d / "04_references").mkdir(parents=True)
    (d / "04_references" / "references.bib").write_text(bib, encoding="utf-8")
    (d / "topic-report.md").write_text(report, encoding="utf-8")
    return d


class TestProvenanceAudit(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_bib_parse_and_levels(self):
        es = _bib_entries(BIB_INFLATED)
        self.assertEqual(len(es), 2)
        self.assertEqual(_source_level(es[0]["source"]), "raw")
        self.assertEqual(_source_level(es[1]["source"]), "wiki")
        self.assertEqual(_source_level(""), "missing")

    def test_inflated_and_dangling_detected(self):
        d = _make_topic(self.root, "t1", BIB_INFLATED, REPORT)
        r = audit_topic(d)
        joined = "; ".join(r["issues"])
        self.assertIn("溯源级别错位", joined)
        self.assertIn("RawClaim2026ref1", joined)
        self.assertIn("Ghost2026refX", joined)

    def test_clean_topic_no_findings(self):
        clean_bib = BIB_INFLATED.replace("knowledge/raw/papers/2026-2606.02238-x.md",
                                         "knowledge/wiki/papers/2024-2402_04610-z.md")
        d = _make_topic(self.root, "t2", clean_bib,
                        "引用 [ref:WikiClaim2026ref2]。")
        r = audit_topic(d)
        self.assertEqual(r["issues"], [])


if __name__ == "__main__":
    unittest.main()
