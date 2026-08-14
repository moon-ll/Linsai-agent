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

        # ── 用例 2：连续 api_error 达阈值 → open 拒绝派发 ──
        for _ in range(cb.API_FAILURE_THRESHOLD):
            r = cb.record_job_result(False, "api_error:HTTP 429")
        self.assert_eq(r["state"], "open", f"连续 {cb.API_FAILURE_THRESHOLD} 次 api_error 熔断")
        self.assert_true(not cb.allow_dispatch(), "open 冷却期内拒绝派发")

        # ── 用例 3：非 API 错误不触发熔断 ──
        cb.force_reset()  # 清除用例 2 残留的 open 状态
        r = cb.record_job_result(False, "timeout after 300s")
        self.assert_eq(r["state"], "closed", "超时类失败不熔断")
        self.assert_eq(r["consecutive_api_errors"], 0, "非 API 错误不累计计数")

        # ── 用例 4：冷却期满 → probing 放行一次 ──
        for _ in range(cb.API_FAILURE_THRESHOLD):
            cb.record_job_result(False, "api_error:quota")
        self._force_cooldown_expired()
        self.assert_true(cb.allow_dispatch(), "冷却期满放行试探 job")
        self.assert_true(not cb.allow_dispatch(), "probing 第二次请求被拒（单试探）")

        # ── 用例 5：试探成功 → closed 恢复 ──
        r = cb.record_job_result(True)
        self.assert_eq(r["state"], "closed", "试探成功恢复 closed")
        self.assert_eq(r["consecutive_api_errors"], 0, "恢复后计数清零")

        # ── 用例 6：试探失败 → 重新 open ──
        for _ in range(cb.API_FAILURE_THRESHOLD):
            cb.record_job_result(False, "api_error:quota")
        self._force_cooldown_expired()
        self.assert_true(cb.allow_dispatch(), "再次进入 probing")
        r = cb.record_job_result(False, "api_error:still-quota")
        self.assert_eq(r["state"], "open", "试探失败重新熔断")

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
