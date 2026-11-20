#!/usr/bin/env python3
"""
test_exemplar_injection_log.py — 跨课题范例注入可观测性回归测试

验证 v6.9.3 修复（proposal_lifecycle.optimize._load_cross_proposal_exemplar）:

背景（2026-08-13 10h / 2026-08-15 08h 两轮体检）:
    范例注入逻辑经实时数据实证正确（低分课题产出范文块、≥0.75 跳过），
    但函数此前无任何日志输出，全量日志 0 条"参考范文"记录，无法区分
    "已注入"与"从未触发"，连续两轮被标记"潜在死代码风险"。
    修复后注入成功时输出一条 INFO 日志（含接收/捐赠课题与双方分数）。

验证点:
    - 低分课题（<0.75）注入成功 → _log.info 恰好 1 条，含接收课题、
      捐赠课题、章节、双方分数
    - 高分课题（≥0.75）跳过 → 无日志
    - 范文文件缺失（早退分支）→ 无日志
    - 注入块内容不回归：仍含【参考范文】头与来源课题（v6.8.24/25 修复）

用法:
    python3 scripts/self_test.py --module          # 全量回归（自动纳入）
    python3 scripts/tests/test_exemplar_injection_log.py   # 单文件直跑

注意：
    本测试不调用真实 hermes/LLM，不读写真实 _lifecycle.json（状态走桩）。
"""

from __future__ import annotations

import importlib
import shutil
import sys
import tempfile
from pathlib import Path

# 让 tests 目录与 scripts 目录均可作为导入入口
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from test_runner import TestSuite

DONOR = "donor-high-20260815"
RECEIVER_LOW = "receiver-low-20260815"
RECEIVER_HIGH = "receiver-high-20260815"


class _LogRecorder:
    """最小日志桩：仅捕获 info 级消息。"""

    def __init__(self):
        self.infos: list = []

    def info(self, msg):
        self.infos.append(msg)

    def warning(self, msg):  # pragma: no cover - 占位
        pass

    def error(self, msg):  # pragma: no cover - 占位
        pass


class _ShimLifecycle:
    """状态桩：替代 lifecycle manager 的两个状态读取方法。"""

    def __init__(self, proposals: dict):
        self._props = proposals

    def _get_proposal_state(self, pid: str) -> dict:
        return self._props.get(pid, {})

    def _load_state(self) -> dict:
        return {"proposals": self._props}


class ExemplarInjectionLogTests(TestSuite):
    """回归测试：v6.9.3 范例注入 INFO 日志留痕。"""

    def __init__(self):
        super().__init__("跨课题范例注入可观测性测试")
        self.tmp_root: Path = None
        self.opt_mod = None
        self.pl_constants = None
        self._orig_root = None
        self._orig_log = None

    # ---------- 环境 ----------
    def setup(self):
        self.tmp_root = Path(tempfile.mkdtemp(prefix="exemplar-log-test-"))

        # 捐赠课题的范文文件（optimizing/<donor>/04_proposal/sections/content.md）
        donor_dir = self.tmp_root / "optimizing" / DONOR / "04_proposal" / "sections"
        donor_dir.mkdir(parents=True, exist_ok=True)
        (donor_dir / "content.md").write_text(
            "# 研究内容（捐赠课题范文）\n\n" + "论证密度示范段落。\n" * 40,
            encoding="utf-8",
        )

        # 导入被测模块（constants.PROPOSALS_ROOT 在函数内局部 import，
        # 运行时读取模块属性，可直接打桩）
        self.pl_constants = importlib.import_module("proposal_lifecycle.constants")
        self.opt_mod = importlib.import_module("proposal_lifecycle.optimize")
        self._orig_root = self.pl_constants.PROPOSALS_ROOT
        self._orig_log = self.opt_mod._log
        self.pl_constants.PROPOSALS_ROOT = self.tmp_root

    def teardown(self):
        if self._orig_root is not None:
            self.pl_constants.PROPOSALS_ROOT = self._orig_root
        if self._orig_log is not None:
            self.opt_mod._log = self._orig_log
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    def _proposals(self, receiver_score: float) -> dict:
        return {
            DONOR: {
                "status": "optimizing",
                "last_score": 0.83,
                "score_history": [
                    {"score": 0.86},
                    {"score": 0.83},
                ],
            },
            RECEIVER_LOW if receiver_score < 0.75 else RECEIVER_HIGH: {
                "status": "optimizing",
                "last_score": receiver_score,
                "score_history": [{"score": receiver_score}],
            },
        }

    def _run(self, receiver_id: str, receiver_score: float, section: str = "content"):
        """注入函数 + 日志桩，返回 (block, recorder)。"""
        rec = _LogRecorder()
        self.opt_mod._log = rec
        shim = _ShimLifecycle(self._proposals(receiver_score))
        block = self.opt_mod._load_cross_proposal_exemplar(shim, receiver_id, section)
        return block, rec

    # ---------- 用例 ----------
    def run_tests(self):
        # 1) 低分接收者：注入成功且恰好 1 条 INFO
        block, rec = self._run(RECEIVER_LOW, 0.18)
        self.assert_true(bool(block), "低分课题产出范例块", "返回为空")
        self.assert_in("【参考范文（来自评分 0.86 的高质量课题", block,
                       "范例块应含 0.86 评分头")
        self.assert_in(DONOR, block, "范例块应含捐赠课题来源")
        self.assert_eq(len(rec.infos), 1, "注入成功恰好 1 条 INFO 日志")
        if rec.infos:
            msg = rec.infos[0]
            self.assert_in(RECEIVER_LOW, msg, "日志含接收课题")
            self.assert_in(DONOR, msg, "日志含捐赠课题")
            self.assert_in("content", msg, "日志含章节")
            self.assert_in("0.86", msg, "日志含范文峰值分")
            self.assert_in("0.18", msg, "日志含当前分")

        # 2) 高分接收者（≥0.75）：跳过且无日志
        block2, rec2 = self._run(RECEIVER_HIGH, 0.79)
        self.assert_eq(block2, "", "高分课题（0.79）跳过注入")
        self.assert_eq(len(rec2.infos), 0, "跳过注入不产生日志")

        # 3) 范文文件缺失（早退分支）：无日志
        missing_dir = self.tmp_root / "optimizing" / DONOR / "04_proposal" / "sections"
        (missing_dir / "rationale.md").unlink(missing_ok=True)
        # rationale.md 本就不存在 → 走 exists() 早退
        block3, rec3 = self._run(RECEIVER_LOW, 0.18, section="rationale")
        self.assert_eq(block3, "", "范文文件缺失时返回空")
        self.assert_eq(len(rec3.infos), 0, "早退分支不产生日志")


if __name__ == "__main__":
    suite = ExemplarInjectionLogTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    summary = suite.summary()
    print(f"{summary['name']}: {summary['passed']}/{summary['total']} 通过")
    for r in summary["results"]:
        mark = "✓" if r.passed else "✗"
        print(f"  {mark} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if summary["failed"] == 0 else 1)
