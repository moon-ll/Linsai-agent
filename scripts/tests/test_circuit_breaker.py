"""test_circuit_breaker.py — API 配额熔断器回归测试（v6.8.50）

验证三态状态机全路径：closed → open（连续 api_error）→ probing（冷却期满）
→ closed（试探成功）/ open（试探失败）。零污染：临时状态文件。
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test_runner import TestSuite


class CircuitBreakerTests(TestSuite):
    """circuit_breaker 状态机回归。"""

    def __init__(self):
        super().__init__("circuit_breaker")

    def setup(self):
        self._tmp = tempfile.TemporaryDirectory()
        import circuit_breaker as cb
        self._cb = cb
        self._orig_state_path = cb.STATE_PATH
        cb.STATE_PATH = Path(self._tmp.name) / "circuit-state.json"

    def teardown(self):
        self._cb.STATE_PATH = self._orig_state_path
        self._tmp.cleanup()

    def _force_cooldown_expired(self):
        """把 open 状态的 opened_at 改到冷却期之前。"""
        st = self._cb._load()
        st["opened_at"] = (datetime.now(timezone.utc) - timedelta(
            seconds=self._cb.OPEN_COOLDOWN_S + 60)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._cb._save(st)

    def run_tests(self):
        cb = self._cb

        # ── 用例 1：closed 正常派发，成功不改变状态 ──
        self.assert_true(cb.allow_dispatch(), "closed 状态允许派发")
        r = cb.record_job_result(True)
        self.assert_eq(r["state"], "closed", "成功 job 保持 closed")

        # ── 用例 2（v6.9.91）：连续 api_error → 激活逃生，双挂才 open ──
        for _ in range(cb.API_FAILURE_THRESHOLD):
            r = cb.record_job_result(False, "api_error:HTTP 429")
        self.assert_eq(r["state"], "closed", f"连续 {cb.API_FAILURE_THRESHOLD} 次 api_error 应逃生而非停摆")
        self.assert_true(r.get("escape_active"), "api_error 达阈值应激活模型逃生")
        self.assert_true(cb.allow_dispatch(), "逃生期间调度照常（有一模型可跑）")
        # 逃生中备用（minimax）也连续失败 → 主备双挂 → open 真停摆
        for _ in range(cb.ESCAPE_FAILURE_LIMIT):
            r = cb.record_job_result(False, "api_error:Token Plan")
        self.assert_eq(r["state"], "open", "逃生中备用也失败（双挂）才 open")
        self.assert_true(not cb.allow_dispatch(), "主备双挂 open 拒绝派发")

        # ── 用例 3：非 API 错误不触发熔断 ──
        cb.force_reset()
        r = cb.record_job_result(False, "timeout after 300s")
        self.assert_eq(r["state"], "closed", "超时类失败不熔断")
        self.assert_eq(r["consecutive_api_errors"], 0, "非 API 错误不累计计数")

        # ── 用例 4：冷却期满 → probing 放行一次 ──
        cb.force_open("测试-手动熔断")
        self._force_cooldown_expired()
        self.assert_true(cb.allow_dispatch(), "冷却期满放行试探 job")
        self.assert_true(not cb.allow_dispatch(), "probing 第二次请求被拒（单试探）")

        # ── 用例 5：试探成功 → closed 恢复 ──
        r = cb.record_job_result(True)
        self.assert_eq(r["state"], "closed", "试探成功恢复 closed")
        self.assert_eq(r["consecutive_api_errors"], 0, "恢复后计数清零")

        # ── 用例 6（v6.9.91）：试探遇 api_error → 激活逃生（非重新 open） ──
        cb.force_open("测试-手动熔断")
        self._force_cooldown_expired()
        self.assert_true(cb.allow_dispatch(), "再次进入 probing")
        r = cb.record_job_result(False, "api_error:still-quota")
        self.assert_eq(r["state"], "closed", "试探遇 api_error 应逃生而非重新 open")
        self.assert_true(r.get("escape_active"), "试探失败激活逃生")
        self.assert_true(cb.allow_dispatch(), "逃生后调度照常")

        # ── 用例 7：状态文件持久化与历史记录 ──
        st = cb.get_state()
        self.assert_true("history" in st and len(st["history"]) > 0,
                         "状态变迁历史被记录")
        self.assert_true(len(st["history"]) <= cb.HISTORY_LIMIT,
                         "历史条数受上限约束")

        # ── 用例 8：人工复位 ──
        for _ in range(cb.API_FAILURE_THRESHOLD):
            cb.record_job_result(False, "api_error:quota")
        r = cb.force_reset()
        self.assert_eq(r["state"], "closed", "人工复位为 closed")
        self.assert_true(cb.allow_dispatch(), "复位后允许派发")

        # ── 用例 9（v7.3.46）：按调用方主模型供应商分流逃生目标 ──
        # zai 系主模型（critic）→ minimax-cn（v6.9.68 原语义）
        t = cb._escape_target_for("critic")
        self.assert_eq(t["provider"], "minimax-cn", "critic（zai 主模型）→ minimax-cn")
        # minimax 系主模型（writer）→ zai glm-5.2（同源盲区修复）
        t = cb._escape_target_for("writer")
        self.assert_eq(t["provider"], "zai", "writer（minimax 主模型）→ zai")
        self.assert_eq(t["model"], "glm-5.2", "writer 逃生目标模型 glm-5.2")
        t = cb._escape_target_for("researcher")
        self.assert_eq(t["provider"], "zai", "researcher 同 writer 分流")
        # 未知 profile 回落默认目标（兼容）
        t = cb._escape_target_for("")
        self.assert_eq(t["provider"], "minimax-cn", "未知 profile 回落默认目标")
        t = cb._escape_target_for("linsai")
        self.assert_eq(t["provider"], "minimax-cn", "非管线 profile 回落默认目标")

        # 激活逃生后 override 按 profile 返回对应目标
        for _ in range(cb.API_FAILURE_THRESHOLD):
            cb.record_job_result(False, "api_error:HTTP 429")
        self.assert_true(cb._load()["escape"]["active"], "逃生已激活")
        t = cb.escape_override_target(profile="writer")
        self.assert_eq(t["provider"], "zai", "激活态 override：writer → zai 目标")
        t = cb.escape_override_target(profile="critic")
        self.assert_eq(t["provider"], "minimax-cn", "激活态 override：critic → minimax-cn 目标")
        cb.force_reset()


if __name__ == "__main__":
    suite = CircuitBreakerTests()
    suite.setup()
    suite.run_tests()
    suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    total = len(suite.results)
    print(f"\n{'✓ 全部通过' if ok == total else '✗ 存在失败'}: {ok}/{total}")
    for r in suite.results:
        if not r.passed:
            print(f"  ✗ {r.name}: {r.msg}")
    sys.exit(0 if ok == total else 1)
