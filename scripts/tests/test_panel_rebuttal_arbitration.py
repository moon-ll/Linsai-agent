#!/usr/bin/env python3
"""
test_panel_rebuttal_arbitration.py — 辩驳-仲裁子流程回归测试（v7.3.60 批次 C）

覆盖：
    1. rebuttal_scaffold：脚手架行与台账枚举同序/预填条目号/空 findings 提示
    2. 裁决表解析：三种裁决 + **加粗条目号**形态 + 畸形行跳过 + 未知 id 报告
    3. 台账应用：uphold_rebuttal 清账（resolved_by/tag/note）；
       uphold_finding / partial 保持 open 附仲裁注
    4. fail-open：无裁决文件 / 无可解析行 不动台账
    5. _open_findings_enumerated 与 adopt_engine 枚举同序性（stale/resolved 跳过）

零 LLM；_lifecycle.json 用临时课题注入（file_lock 同真实路径，测试内自清理）。
"""

import sys
import importlib
import json
import shutil
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT

sys.path.insert(0, str(REAL_ROOT / "scripts"))


def _mk_prop(tmp_root: Path, pid: str, criticals: list) -> None:
    """在隔离环境注册课题 + 注入 open_critical_issues。"""
    lc = tmp_root / "research_proposals" / "_lifecycle.json"
    lc.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(lc.read_text(encoding="utf-8")) if lc.exists() else {"proposals": {}}
    data["proposals"][pid] = {
        "status": "optimizing",
        "optimization_rounds": 2,
        "open_critical_issues": criticals,
    }
    lc.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    prop_dir = tmp_root / "research_proposals" / "optimizing" / pid
    (prop_dir / "06_panel").mkdir(parents=True, exist_ok=True)


class RebuttalArbitrationTests(TestSuite):
    def __init__(self):
        super().__init__("辩驳-仲裁子流程回归测试")
        self.tmp_root = None
        self.pr = None
        self._orig_lc = None

    def setup(self):
        self.tmp_root = create_isolated_env()
        (self.tmp_root / "research_proposals").mkdir(parents=True, exist_ok=True)
        (self.tmp_root / "research_proposals" / "_lifecycle.json").write_text(
            json.dumps({"proposals": {}}), encoding="utf-8")
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("panel_review") or mod_name in ("paths", "common"):
                del sys.modules[mod_name]
        self.pr = importlib.import_module("panel_review")
        patch_module_root("panel_review", self.tmp_root)
        import paths
        # 打桩 PROJECT_ROOT 指向隔离环境（_lifecycle.json / proposal 目录都在隔离侧）
        self._orig_lc = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root
        self.pr.PROJECT_ROOT = self.tmp_root

    def teardown(self):
        import paths
        paths.PROJECT_ROOT = self._orig_lc
        self.pr.PROJECT_ROOT = self._orig_lc
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _criticals(self):
        return [
            {"severity": "critical", "section": "rationale", "round_resolved": None,
             "stale": False,
             "description": "1. [critical] self_conflict｜L111｜互斥｜改分档"},
            {"severity": "high", "section": "scheme", "round_resolved": None,
             "stale": False,
             "description": "2. [high] notation｜L59｜记号四形｜统一"},
            {"severity": "critical", "section": "content", "round_resolved": 1,
             "stale": False,
             "description": "3. 已解决条目（不应出现在枚举中）"},
            {"severity": "low", "section": "content", "round_resolved": None,
             "stale": True,
             "description": "4. stale 条目（不应出现在枚举中）"},
        ]

    # ---------- 用例 ----------

    def test_scaffold_alignment(self):
        pid = "p-sca"
        _mk_prop(self.tmp_root, pid, self._criticals())
        r = self.pr.rebuttal_scaffold(pid)
        self.assert_true(r["success"], "脚手架生成成功")
        self.assert_eq(r["open_findings"], 2, "仅枚举未解决未 stale 条目")
        text = Path(r["path"]).read_text(encoding="utf-8")
        self.assert_true("| L1 |" in text and "self_conflict" in text, "L1 预填")
        self.assert_true("| L2 |" in text, "L2 预填")
        self.assert_true("| L3 |" not in text and "| L4 |" not in text,
                         "已解决/stale 条目不进脚手架")

    def test_scaffold_empty_findings(self):
        pid = "p-empty"
        _mk_prop(self.tmp_root, pid, [])
        r = self.pr.rebuttal_scaffold(pid)
        self.assert_true(r["success"] and r["open_findings"] == 0, "空 findings 成功")
        text = Path(r["path"]).read_text(encoding="utf-8")
        self.assert_true("无需辩驳" in text, "空表提示")

    def test_arbitration_apply(self):
        pid = "p-arb"
        _mk_prop(self.tmp_root, pid, self._criticals())
        arb = self.tmp_root / "research_proposals" / "optimizing" / pid / "06_panel" / "panel-arbitration.md"
        arb.write_text(
            "# 仲裁裁决表\n\n"
            "| 条目号 | 裁决 | 理由 |\n|---|---|---|\n"
            "| L1 | uphold_rebuttal | 判据为区间分段表述，互斥不成立（口径表 §1.5 同文） |\n"
            "| **L2** | uphold_finding | 记号四形实测存在，反驳依据不足 |\n"
            "| 条目五 | partial | 无 L/C 条目号的行应跳过 |\n"
            "| L99 | uphold_rebuttal | 越界条目号应报 unknown |\n",
            encoding="utf-8")
        r = self.pr.apply_arbitration(pid)
        self.assert_true(r["success"], "仲裁落账成功")
        self.assert_eq(r["rulings"], 3, "解析 3 条合法裁决行（L99 亦解析、应用时报越界）")
        self.assert_eq(r["withdrawn"], 1, "撤销 1 条")
        self.assert_eq(r["held"], 1, "维持 1 条")
        self.assert_true("L99" in (r.get("unknown_ids") or []), "越界 id 报 unknown")
        lc = json.loads((self.tmp_root / "research_proposals" / "_lifecycle.json")
                        .read_text(encoding="utf-8"))
        entries = lc["proposals"][pid]["open_critical_issues"]
        e1 = next(e for e in entries if "self_conflict" in str(e.get("description")))
        e2 = next(e for e in entries if "notation" in str(e.get("description")))
        self.assert_eq(e1.get("round_resolved"), 2, "uphold_rebuttal 清账")
        self.assert_true(str(e1.get("resolved_by", "")).startswith("panel-arbitration-"),
                         "resolved_by 仲裁标记")
        self.assert_true("维持反驳" in str(e1.get("resolved_note", "")), "清账注记")
        self.assert_eq(e2.get("round_resolved"), None, "uphold_finding 保持 open")
        self.assert_true("uphold_finding" in str(e2.get("arbitration_note", "")),
                         "维持注记")

    def test_arbitration_failopen(self):
        pid = "p-fo"
        _mk_prop(self.tmp_root, pid, self._criticals())
        r1 = self.pr.apply_arbitration(pid)
        self.assert_true(r1["success"] is False, "无裁决文件 fail-open")
        # 无可解析行
        arb = self.tmp_root / "research_proposals" / "optimizing" / pid / "06_panel" / "panel-arbitration.md"
        arb.write_text("本页无裁决。\n", encoding="utf-8")
        r2 = self.pr.apply_arbitration(pid)
        self.assert_true(r2["success"] is False, "无可解析行 fail-open")
        lc = json.loads((self.tmp_root / "research_proposals" / "_lifecycle.json")
                        .read_text(encoding="utf-8"))
        entries = lc["proposals"][pid]["open_critical_issues"]
        open_n = sum(1 for e in entries if e.get("round_resolved") is None and not e.get("stale"))
        self.assert_eq(open_n, 2, "fail-open 不动台账")

    def test_enumeration_order_matches_ledger(self):
        """_open_findings_enumerated 与 adopt_engine 清账同序（1-based 连续）。"""
        pid = "p-ord"
        _mk_prop(self.tmp_root, pid, self._criticals())
        lc = json.loads((self.tmp_root / "research_proposals" / "_lifecycle.json")
                        .read_text(encoding="utf-8"))
        pairs = self.pr._open_findings_enumerated(lc["proposals"][pid])
        self.assert_eq([i for i, _ in pairs], [1, 2], "连续 1-based 枚举")
        self.assert_true("self_conflict" in str(pairs[0][1].get("description")),
                         "L1=首条未解决项（与 adopt_engine/任务包同序）")

    def run_tests(self):
        self.test_scaffold_alignment()
        self.test_scaffold_empty_findings()
        self.test_arbitration_apply()
        self.test_arbitration_failopen()
        self.test_enumeration_order_matches_ledger()


if __name__ == "__main__":
    suite = RebuttalArbitrationTests()
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
