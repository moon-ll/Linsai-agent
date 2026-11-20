#!/usr/bin/env python3
"""
test_stage_weekly_report.py — 阶段级 WoW 回归检测回归测试（v7.3.61 批次 D，目标 3）

覆盖：
    1. 双周窗口聚合（本周/上周分片、窗口边界、跨月文件）
    2. R1 失败率回归（≥+5pp 且样本 ≥5）触发与不触发
    3. R2 时延回归（p50 ≥+50% 且上周 p50 ≥60s）触发与不触发
    4. 低频阶段（窗口 <3 次）不参与比对；畸形行跳过
    5. run_and_persist 落盘 + run_retrospective 集成节（fail-open）

零 LLM；账本用合成 JSONL 注入临时目录，now 注入固定时钟（无墙钟炸弹）。
"""

import sys
import importlib
import json
import shutil
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT

sys.path.insert(0, str(REAL_ROOT / "scripts"))


class StageWeeklyReportTests(TestSuite):
    def __init__(self):
        super().__init__("阶段级 WoW 回归检测回归测试")
        self.tmp_root = None
        self.sw = None
        self._orig_patches = []

    def setup(self):
        self.tmp_root = create_isolated_env()
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith(("stage_weekly_report", "retrospective")) \
                    or mod_name in ("paths", "common"):
                del sys.modules[mod_name]
        self.sw = importlib.import_module("stage_weekly_report")
        patch_module_root("stage_weekly_report", self.tmp_root)
        import paths
        paths.PROJECT_ROOT = self.tmp_root
        self.sw.USAGE_DIR = self.tmp_root / "memory" / "usage"
        self.sw.OUT_DIR = self.tmp_root / "memory" / "self-optimize"

    def teardown(self):
        for obj, name, orig in self._orig_patches:
            setattr(obj, name, orig)
        self._orig_patches.clear()
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _write_ledger(self, lines_by_file):
        self.sw.USAGE_DIR.mkdir(parents=True, exist_ok=True)
        for fname, lines in lines_by_file.items():
            p = self.sw.USAGE_DIR / fname
            p.write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in lines) + "\n",
                         encoding="utf-8")

    @staticmethod
    def _entry(month, day, hour, kind, name, success, elapsed):
        return {"ts": f"2026-{month:02d}-{day:02d}T{hour:02d}:00:00Z", "kind": kind,
                "name": name, "success": success, "elapsed_s": elapsed, "error": ""}

    def _now(self):
        from datetime import datetime, timezone
        return datetime(2026, 11, 7, 12, 0, 0, tzinfo=timezone.utc)

    # ---------- 用例 ----------

    def test_regression_rules(self):
        """R1/R2 触发与不触发：researcher 恶化双触发；writer 平稳不触发。"""
        cur, prev = [], []
        # 本周 researcher（11 月）：40% 失败 vs 上周（10 月）10%；p50 340s vs 100s
        for i in range(10):
            cur.append(self._entry(11, 1 + i % 7, 8, "hermes_agent", "researcher",
                                   i % 5 >= 2, 300 + (i * 20) % 100))
            prev.append(self._entry(10, 24 + i % 7, 8, "hermes_agent", "researcher",
                                    i != 0, 100))
        # 两周平稳 writer：0 失败，p50 120s
        for i in range(10):
            cur.append(self._entry(11, 1 + i % 7, 9, "hermes_agent", "writer", True, 120))
            prev.append(self._entry(10, 24 + i % 7, 9, "hermes_agent", "writer", True, 120))
        self._write_ledger({"step-usage-2026-11.jsonl": cur,
                            "step-usage-2026-10.jsonl": prev})
        rep = self.sw.build_report(self.sw.USAGE_DIR, now=self._now())
        rows = {r["step"]: r for r in rep["stages"]}
        rr = rows.get("hermes_agent:researcher", {})
        wr = rows.get("hermes_agent:writer", {})
        self.assert_true(any("R1" in f for f in rr["regressions"]),
                         "R1 失败率回归触发")
        self.assert_true(any("R2" in f for f in rr["regressions"]),
                         "R2 时延回归触发")
        self.assert_eq(wr["regressions"], [], "平稳阶段无回归")
        self.assert_eq(wr["cur_failure_rate"], 0.0, "writer 失败率 0%")

    def test_low_frequency_and_malformed(self):
        """低频（<3 次）不比对；畸形行/空行跳过不抛。"""
        cur = [self._entry(11, 3, 8, "llm_router", "kimi", False, 5)]
        cur.append({"ts": "not-a-date", "kind": "x", "name": "y"})
        cur.append({"bad": 1})
        self._write_ledger({"step-usage-2026-11.jsonl": cur,
                            "step-usage-2026-10.jsonl": []})
        rep = self.sw.build_report(self.sw.USAGE_DIR, now=self._now())
        steps = [r["step"] for r in rep["stages"]]
        self.assert_true("llm_router:kimi" not in steps, "低频阶段不比对")
        self.assert_true(rep["regressions"] == [], "无假回归")

    def test_persist_and_retrospective_section(self):
        """run_and_persist 落盘 JSON；run_retrospective 报告含阶段级节。"""
        self._write_ledger({
            "step-usage-2026-11.jsonl": [self._entry(11, 3, 8, "hermes_agent", "critic", False, 90)
                                         for _ in range(6)],
            "step-usage-2026-10.jsonl": [self._entry(10, 26, 8, "hermes_agent", "critic", False, 90)
                                         for _ in range(6)],
        })
        rep, md = self.sw.run_and_persist(now=self._now())
        out = self.sw.OUT_DIR / "stage-weekly-2026-11-07.json"
        self.assert_true(out.exists(), "JSON 落盘")
        self.assert_true("阶段级 WoW 回归检测" in md, "markdown 节")
        # retrospective 集成节（真实生产函数，报告追加 fail-open）
        import retrospective
        out_md = retrospective.run_retrospective("7d")
        text = Path(out_md).read_text(encoding="utf-8")
        self.assert_true("阶段级 WoW 回归检测" in text, "复盘报告含阶段级节")

    def run_tests(self):
        self.test_regression_rules()
        self.test_low_frequency_and_malformed()
        self.test_persist_and_retrospective_section()


if __name__ == "__main__":
    suite = StageWeeklyReportTests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    s = suite.summary()
    print(f"\n{'✓' if s['failed'] == 0 else '✗'} {s['name']}: {s['passed']}/{s['total']} 通过")
    for r in s["results"]:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if s["failed"] == 0 else 1)
