#!/usr/bin/env python3
"""
test_writer_recovery_bonus.py — writer 恢复加成回归测试（v6.10.6）

背景：惩罚为固定值（质量门 -2/-5、违规 -5/-8）而奖励按比例（20×monitor
增量、3×问题修复），writer 全局分随机游走天然负漂移（实测 100→42.9，近
10 轮累计 -32.8）。critic 自 v6.8.18 有 RECOVERY_BONUS 对冲，writer 无
对称机制。本测试守护新增的挣得式恢复：低位（<50）+ 正 delta + 近 5 轮
无严重违规 → +5 加成。

规则层参考（构造用例时据此计算预期值）：
    writer_rule_delta = monitor_delta×20 + max(0, 高优问题减少数)×3
                        + 违规罚分 + 质量门（monitor<0.70 再 -2，<0.50 再 -5）

注意：
    本测试不调用 hermes/LLM，仅验证奖惩数据逻辑。

用法示例：
    python3 scripts/tests/test_writer_recovery_bonus.py
"""

import copy
import json
import sys
import tempfile
from pathlib import Path

from test_runner import TestSuite, create_isolated_env


def _make_scores(writer_score: float, critic_score: float = 120.0) -> dict:
    from adversarial.constants import DEFAULT_INITIAL_SCORE

    tpl = {
        "score": DEFAULT_INITIAL_SCORE,
        "initial_score": DEFAULT_INITIAL_SCORE,
        "history": [],
        "prohibition_violations": [],
        "updated_at": "",
    }
    w = copy.deepcopy(tpl)
    w["score"] = writer_score
    c = copy.deepcopy(tpl)
    c["score"] = critic_score
    return {"writer": w, "critic": c, "updated_at": ""}


def _monitor_result(score: float) -> dict:
    return {
        "monitor_independent_score": score,
        "monitor_score_valid": True,
        "writer_prohibitions": [],
        "critic_prohibitions": [],
        "collusion_risk": "none",
        "raw_output": "",
        "writer_suggested_delta": 0.0,
        "critic_suggested_delta": 0.0,
    }


class WriterRecoveryBonusTests(TestSuite):
    def __init__(self):
        super().__init__("writer 恢复加成测试")
        self._tmp = None

    def setup(self):
        create_isolated_env()
        self._tmp = tempfile.mkdtemp(prefix="writer_recovery_")
        self._n = 0

    def teardown(self):
        pass

    def _apply(self, writer_score, prev_score, cur_score,
               issues_before=0, issues_after=0, writer_violations=None):
        """跑一轮 apply_monitor_result，返回结果与落盘分数。

        issues_after>0 时通过 raw_output 注入等量 critical 关键词，
        与生产路径（_count_high_critical_issues 扫描原文）一致。
        """
        from adversarial.scoring import apply_monitor_result

        self._n += 1
        scores = _make_scores(writer_score)
        if writer_violations:
            scores["writer"]["prohibition_violations"] = writer_violations
        scores_path = Path(self._tmp) / f"s{self._n}.json"
        scores_path.write_text(
            json.dumps(scores, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        raw = "critical issue\n" * issues_after
        mr = _monitor_result(cur_score)
        mr["raw_output"] = raw
        proposal_state = {
            "monitor_history": [
                {"monitor_independent_score": prev_score,
                 "high_issues_after": issues_before}
            ],
            "last_score": prev_score,
        }
        res = apply_monitor_result(
            scores_path=scores_path,
            proposal_id="test-proposal",
            round_num=1,
            section_key="rationale",
            score_before=prev_score,
            score_after=cur_score,
            dim_scores={},
            monitor_result=mr,
            proposal_state=proposal_state,
        )
        saved = json.loads(scores_path.read_text(encoding="utf-8"))
        return res, saved

    def run_tests(self):
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        fresh = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        stale = (now - timedelta(hours=72)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # ---------- 1. 低位 + 正轮 + 问题修复 → 加成 ----------
        # 规则层：monitor +0.10×20=2 + 问题修复 2×3=6 = 8；加成 +5 → 13
        res, saved = self._apply(42.9, 0.60, 0.70, issues_before=2, issues_after=0)
        self.assert_eq(res["writer_delta"], 13.0, "低位正轮 → 规则 8 + 加成 5")
        self.assert_eq(saved["writer"]["score"], 55.9, "落盘分数 42.9+13=55.9")

        # ---------- 2. 低位 + 负轮 → 不加成 ----------
        # 规则层：monitor -0.10×20=-2 + 质量门(0.60<0.70) -2 = -4
        res2, _ = self._apply(42.9, 0.70, 0.60)
        self.assert_eq(res2["writer_delta"], -4.0, "负轮不加成（恢复必须挣得）")

        # ---------- 3. 低位 + 零 delta 轮 → 不加成 ----------
        # 规则层：monitor 0 + 质量门 0（0.75≥0.70）= 0
        res3, _ = self._apply(42.9, 0.75, 0.75)
        self.assert_eq(res3["writer_delta"], 0.0, "零 delta 轮不加成")

        # ---------- 4. 已过阈值（≥50）→ 不加成 ----------
        # 规则层：monitor +0.10×20=2（无问题修复）
        res4, _ = self._apply(50.0, 0.60, 0.70)
        self.assert_eq(res4["writer_delta"], 2.0, "分数 50.0 不再触发（<50 边界）")
        res4b, _ = self._apply(55.0, 0.60, 0.70)
        self.assert_eq(res4b["writer_delta"], 2.0, "分数 55 不触发")

        # ---------- 5. 低位正轮但 48h 内有严重违规 → 不加成 ----------
        severe_fresh = [{"type": "severe fabrication", "penalty": -8.0, "at": fresh}]
        res5, _ = self._apply(42.9, 0.60, 0.70, writer_violations=severe_fresh)
        self.assert_eq(res5["writer_delta"], 2.0, "48h 内严重违规 → 不加成")

        # ---------- 6. 严重违规超窗（72h 前）→ 不阻断加成 ----------
        # 时间窗语义：干净轮次不新增违规条目，索引窗口会让一次严重违规
        # 无限期滞留（激励倒挂）；48h 后行为由后续轮次重新证明。
        severe_stale = [{"type": "severe fabrication", "penalty": -8.0, "at": stale}]
        res6a, _ = self._apply(42.9, 0.60, 0.70, writer_violations=severe_stale)
        self.assert_eq(res6a["writer_delta"], 7.0, "超窗严重违规不阻断恢复加成")

        # ---------- 7. 轻微违规（surface_change -5）不阻断加成 ----------
        minor = [{"type": "surface_change", "penalty": -5.0, "at": fresh}]
        res7, _ = self._apply(42.9, 0.60, 0.70, writer_violations=minor)
        self.assert_eq(
            res7["writer_delta"], 7.0, "轻微违规（>-8 非严重）不阻断恢复加成"
        )

        # ---------- 8. 违规时间戳损坏（None/垃圾值）不误伤 ----------
        broken_ts = [{"type": "severe fabrication", "penalty": -8.0, "at": "garbage"}]
        res8, _ = self._apply(42.9, 0.60, 0.70, writer_violations=broken_ts)
        self.assert_eq(
            res8["writer_delta"], 7.0,
            "时间戳解析失败的违规不阻断（读不到按未恢复处理会误伤反向）",
        )

        # ---------- 9. 返回结构完整性（critic 路径不受影响） ----------
        self.assert_true("critic_delta" in res7, "返回结构含 critic_delta")
        self.assert_true(
            isinstance(res7.get("new_writer_score"), (int, float)),
            "返回结构含 new_writer_score",
        )

        # ---------- 10. 大额正轮后 clamp 到合法区间 ----------
        res10, _ = self._apply(148.0, 0.60, 0.90, issues_before=3, issues_after=0)
        # 分数 148 ≥50 不触发加成；新分数 clamp ≤150
        self.assert_true(res10["new_writer_score"] <= 150, "新分数不超过 SCORE_MAX")


def main() -> None:
    suite = WriterRecoveryBonusTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    print(f"✓ {suite.name}: {ok}/{len(suite.results)} 通过")
    raise SystemExit(1 if len(suite.results) - ok else 0)


if __name__ == "__main__":
    main()
