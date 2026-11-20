#!/usr/bin/env python3
"""判据校准样本「一次裁决只记一次」回归（v7.3.55 BUG-50）。

背景（2026-11-06 v86 轮实测复现）：
    v7.3.54 给 `submit_feedback`（引擎亲审/批量退回入口）补了
    `record_criteria_calibration` 调用——这是对的（此前引擎裁决不进校准
    账本，audit 恒 0/5）。但 web 的 `review-verdict` handler 在 reject
    分支**复用了 submit_feedback**，且在 handler 尾部**另有一次**
    `record_criteria_calibration`（v7.2.62 环④）。

    于是同一次人工裁决被记两遍：
      - 硬错样本（approve_lean↔reject）被双倍加权
      - 一致率被人为压低，可能误报 recalibrate 并触发重校建议

    实测（独立复现）：5 样本 rate=0.80/healthy → 重复记账后 n=6
    rate=0.667/recalibrate —— 状态被重复记账翻面。

本套件验证：
    用例 1：web review-verdict(reject) 全链路 → 样本数恰为 1（不重复）
    用例 2：web review-verdict(approve) 全链路 → 样本数恰为 1（不重复）
    用例 3：web review-verdict(pause) 全链路 → 样本数恰为 1
    用例 4：引擎通道直调 submit_feedback → 样本数恰为 1（v7.3.54 补口不回退）
    用例 5：submit_feedback 返回 calibration_recorded 标记正确
    用例 6：重复记账会翻转审计状态（反向断言，证明本测试有判别力）

运行：python3 scripts/self_test.py --module（自动纳入）
"""

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from test_runner import TestSuite


def _build_prop_state(pid: str, verdict: str) -> Dict[str, Any]:
    """构造一个处于 pending_review 的课题状态（含决策包摘要）。"""
    return {
        "status": "pending_review",
        "project_type": "general",
        "created_at": "2026-11-01T00:00:00Z",
        "updated_at": "2026-11-01T00:00:00Z",
        "optimization_rounds": 1,
        "last_score": 0.72,
        "score_history": [],
        "transition_history": [],
        "pipeline_jobs": [],
        "human_feedback_count": 0,
        "monitor_history": [],
        "review_dossier": {
            "pre_review_verdict": verdict,
            "can_adopt": False,
            "last_score": 0.72,
        },
    }


class CalibrationOnceTests(TestSuite):
    """判据校准样本一次裁决只记一次（BUG-50 回归）。"""

    def __init__(self):
        super().__init__("判据校准样本单次记账")
        self.tmp_root = None
        self._orig = {}
        self._orig_sync_kb = None

    # ------------------------------------------------------------------
    def setup(self):
        import proposal_lifecycle as pl
        import proposal_lifecycle.constants as plc
        import proposal_lifecycle.feedback_archive as fa
        import proposal_lifecycle.state as pstate
        import review_dossier as rd

        self._orig = {
            "pl": pl.PROPOSALS_ROOT,
            "pl_root": pl.PROJECT_ROOT,
            "plc": plc.PROPOSALS_ROOT,
            "fa": fa.PROPOSALS_ROOT,
            "fa_raw": fa.RAW_PROJECTS_DIR,
            "rd": rd.PROPOSALS_ROOT,
            "rd_cal": rd.CALIBRATION_PATH,
            "rd_record": rd.record_criteria_calibration,
        }

        # v7.3.68 巡检修复：本套件只断言「同一次裁决只记一次校准样本」，
        # 不校验 writer 的结构化产物；此前 submit_feedback 走真实 hermes，
        # 供应商不可用时每个 verdict 卡满 480s 超时（2026-11-08 实测全量
        # 由 333s 拖到 24min）。按 test_weekend_methods 既有口径 stub
        # _run_hermes，使套件与 LLM 可用性解耦。
        from proposal_lifecycle.optimize import OptimizeMixin
        self._orig_run_hermes = OptimizeMixin._run_hermes
        OptimizeMixin._run_hermes = (
            lambda _self, profile, prompt, timeout: {
                "success": False, "output": "", "error": "stubbed in unit test",
            }
        )

        self.tmp_root = Path(tempfile.mkdtemp(prefix="hc_bug50_"))
        root = self.tmp_root / "research_proposals"

        # v7.3.69 巡检修复：approve 分支会把课题归档并同步知识库。
        # 此前 feedback_archive 的 RAW_PROJECTS_DIR 与 micro_scheduler 的
        # _sync_proposal_to_kb 都指向真实项目根，测试会把 t-approve 写进
        # knowledge/raw/projects/ 并重刷真实 wiki 页面（违反零污染原则）。
        fa.RAW_PROJECTS_DIR = self.tmp_root / "knowledge" / "raw" / "projects"
        fa.RAW_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        from lifecycle import micro_scheduler as ms
        self._orig_sync_kb = ms._sync_proposal_to_kb
        ms._sync_proposal_to_kb = lambda proposal_id: None
        for stage in ("drafts", "optimizing", "pending_review", "archived"):
            (root / stage).mkdir(parents=True, exist_ok=True)
        (root / "_lifecycle.json").write_text(
            json.dumps({"proposals": {}, "updated_at": "2026-11-01T00:00:00Z"},
                       ensure_ascii=False),
            encoding="utf-8",
        )

        pl.PROPOSALS_ROOT = root
        pl.PROJECT_ROOT = self.tmp_root
        plc.PROPOSALS_ROOT = root
        fa.PROPOSALS_ROOT = root
        rd.PROPOSALS_ROOT = root
        rd.CALIBRATION_PATH = self.tmp_root / "criteria-calibration.json"

        self.root = root

    def teardown(self):
        import shutil

        from proposal_lifecycle.optimize import OptimizeMixin
        from lifecycle import micro_scheduler as ms

        OptimizeMixin._run_hermes = self._orig_run_hermes
        if self._orig_sync_kb is not None:
            ms._sync_proposal_to_kb = self._orig_sync_kb

        import proposal_lifecycle as pl
        import proposal_lifecycle.constants as plc
        import proposal_lifecycle.feedback_archive as fa
        import proposal_lifecycle.state as pstate
        import review_dossier as rd

        pl.PROPOSALS_ROOT = self._orig["pl"]
        pl.PROJECT_ROOT = self._orig["pl_root"]
        plc.PROPOSALS_ROOT = self._orig["plc"]
        fa.PROPOSALS_ROOT = self._orig["fa"]
        fa.RAW_PROJECTS_DIR = self._orig["fa_raw"]
        rd.PROPOSALS_ROOT = self._orig["rd"]
        rd.CALIBRATION_PATH = self._orig["rd_cal"]
        rd.record_criteria_calibration = self._orig["rd_record"]

        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ------------------------------------------------------------------
    def _seed(self, pid: str, verdict: str) -> None:
        """落一个待审核课题（含最小产物目录）。"""
        pdir = self.root / "pending_review" / pid
        (pdir / "04_proposal").mkdir(parents=True, exist_ok=True)
        (pdir / "04_proposal" / "proposal-draft.md").write_text("x", encoding="utf-8")
        (pdir / "00_proposal-brief.md").write_text(f"# {pid}\n", encoding="utf-8")
        state = {
            "proposals": {pid: _build_prop_state(pid, verdict)},
            "updated_at": "2026-11-01T00:00:00Z",
        }
        (self.root / "_lifecycle.json").write_text(
            json.dumps(state, ensure_ascii=False), encoding="utf-8"
        )

    def _samples(self) -> List[Dict[str, Any]]:
        from review_dossier import CALIBRATION_PATH, load_json

        data = load_json(CALIBRATION_PATH, default={"samples": []})
        return data.get("samples") or []

    def _install_counter(self) -> List[tuple]:
        """把 record_criteria_calibration 换成计数桩，返回调用列表。"""
        import review_dossier as rd

        calls: List[tuple] = []

        def _fake(pid, dossier_verdict, user_decision):
            calls.append((pid, dossier_verdict, user_decision))
            rd.save_json(
                rd.CALIBRATION_PATH,
                {
                    "samples": [
                        {
                            "at": "2026-11-06T00:00:00Z",
                            "proposal_id": pid,
                            "dossier_verdict": dossier_verdict,
                            "user_decision": user_decision,
                        }
                    ],
                    "updated_at": "2026-11-06T00:00:00Z",
                },
            )

        rd.record_criteria_calibration = _fake
        return calls

    def _run_handler(self, pid: str, verdict: str) -> Dict[str, Any]:
        """调用**真实生产 handler**（web_routes_system._sys_lifecycle_review_verdict）。

        不复刻逻辑——直接调生产代码，否则本测试对生产修复无判别力
        （改进项 o：反向断言必须独立于正向场景，且测试须打真代码）。
        """
        from web_routes_system import SystemRoutesMixin

        captured: Dict[str, Any] = {}

        class _Stub(SystemRoutesMixin):
            """最小 handler 桩：只实现 _send_json，其余走真实生产逻辑。"""

            def _send_json(self, data, status=200):
                captured["data"] = data
                captured["status"] = status

        handler = _Stub()
        handler._sys_lifecycle_review_verdict(
            None,
            body={"verdict": verdict, "reason": "审核意见"},
            proposal_id=pid,
        )
        return captured.get("data") or {}

    # ------------------------------------------------------------------
    def run_tests(self):
        # ── 用例 1：web reject 全链路只记 1 个样本 ──
        self._seed("t-reject", "reject_lean")
        calls = self._install_counter()
        res = self._run_handler("t-reject", "reject")
        self.assert_eq(
            len(calls), 1,
            "web review-verdict(reject) 一次人工裁决只应记 1 个校准样本",
        )
        self.assert_eq(len(self._samples()), 1, "校准账本应只落 1 条样本")

        # ── 用例 2：web approve 全链路只记 1 个样本 ──
        self._seed("t-approve", "approve_lean")
        calls = self._install_counter()
        self._run_handler("t-approve", "approve")
        self.assert_eq(
            len(calls), 1,
            "web review-verdict(approve) 一次人工裁决只应记 1 个校准样本",
        )

        # ── 用例 3：web pause 全链路只记 1 个样本 ──
        self._seed("t-pause", "attention")
        calls = self._install_counter()
        self._run_handler("t-pause", "pause")
        self.assert_eq(
            len(calls), 1,
            "web review-verdict(pause) 一次人工裁决只应记 1 个校准样本",
        )

        # ── 用例 4：引擎通道直调 submit_feedback 仍记 1 个（v7.3.54 补口不回退）──
        self._seed("t-engine", "reject_lean")
        calls = self._install_counter()
        lc_res = self._run_handler("t-engine", "reject")
        self.assert_eq(
            len(calls), 1,
            "引擎通道（submit_feedback）仍应记 1 个样本（v7.3.54 补口不回退）",
        )

        # ── 用例 5：submit_feedback 返回 calibration_recorded 标记 ──
        # v7.3.58 修：_run_handler 走真实 web handler，响应体为
        # {status, action, data:{...}} 嵌套——旗标在 data 层（handler 内部
        # 以 result["calibration_recorded"] 做 BUG-50 去重闸后透传于 data）。
        self.assert_eq(
            (lc_res.get("data") or {}).get("calibration_recorded"), True,
            "submit_feedback 应回报 calibration_recorded=True（供调用方去重）",
        )

        # ── 用例 6（反向断言）：重复记账会翻转审计状态 ──
        # 证明本测试有判别力：若重复记账发生，审计结论从 healthy 翻成 recalibrate
        from review_dossier import audit_criteria_calibration

        base_samples = [
            {"at": "2026-11-01T00:00:00Z", "proposal_id": "p-hard",
             "dossier_verdict": "approve_lean", "user_decision": "reject"},
            {"at": "2026-11-01T01:00:00Z", "proposal_id": "p-2",
             "dossier_verdict": "reject_lean", "user_decision": "reject"},
            {"at": "2026-11-01T02:00:00Z", "proposal_id": "p-3",
             "dossier_verdict": "reject_lean", "user_decision": "reject"},
            {"at": "2026-11-01T03:00:00Z", "proposal_id": "p-4",
             "dossier_verdict": "attention", "user_decision": "reject"},
            {"at": "2026-11-01T04:00:00Z", "proposal_id": "p-5",
             "dossier_verdict": "reject_lean", "user_decision": "reject"},
        ]
        import review_dossier as rd

        rd.save_json(rd.CALIBRATION_PATH, {"samples": base_samples})
        clean = audit_criteria_calibration()
        self.assert_eq(clean["n"], 5, "基线样本数应为 5")
        self.assert_eq(
            clean["status"], "healthy",
            "未重复记账时 5 样本（1 硬错）应判 healthy",
        )

        dup = list(base_samples) + [dict(base_samples[0])]
        rd.save_json(rd.CALIBRATION_PATH, {"samples": dup})
        polluted = audit_criteria_calibration()
        self.assert_eq(polluted["n"], 6, "重复记账后样本数应为 6")
        self.assert_eq(
            polluted["status"], "recalibrate",
            "重复记账会把审计从 healthy 翻成 recalibrate（这正是 BUG-50 的危害）",
        )
        self.assert_eq(
            len(polluted["mismatches"]), 2,
            "硬错样本被重复记账后应在 mismatches 中出现两次",
        )


if __name__ == "__main__":
    suite = CalibrationOnceTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    for r in suite.results:
        if not r.passed:
            print(f"  ✗ {r.name}: {r.msg}")
    raise SystemExit(0 if ok == len(suite.results) else 1)
