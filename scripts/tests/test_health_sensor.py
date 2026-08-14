"""test_health_sensor.py — 统一健康感知层回归测试（v6.8.50）

验证 health_sensor 对"看起来成功的失败"的四类信号采集与风险评估，
重点回归 2026-08-14 真实故障模式（429 空转 / 伪分数骤降）。
零污染：临时目录 + 隔离数据文件。
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test_runner import TestSuite


def _fmt_ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class HealthSensorTests(TestSuite):
    """health_sensor 信号采集与风险评估回归。"""

    def __init__(self):
        super().__init__("health_sensor")

    def setup(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._tmpdir = Path(self._tmp.name)
        self._old_cwd = os.getcwd()
        # 备份真实路径并指向隔离目录
        import health_sensor as hs
        self._hs = hs
        self._orig = {
            "LIFECYCLE_PATH": hs.LIFECYCLE_PATH,
            "KANBAN_PATH": hs.KANBAN_PATH,
            "CIRCUIT_PATH": hs.CIRCUIT_PATH,
        }
        hs.LIFECYCLE_PATH = self._tmpdir / "_lifecycle.json"
        hs.KANBAN_PATH = self._tmpdir / "system-kanban.json"
        hs.CIRCUIT_PATH = self._tmpdir / "circuit-state.json"
        # v6.8.53: 隔离 KB 信号——_collect_kb_signals 经 facade 读真实知识库，
        # 真实 graph_connectivity(0.45)<0.50 会触发 kb_graph_disconnect 告警，
        # 污染"正常状态零告警"用例，且结果随全局 knowledge_base 模块的
        # patch 状态漂移（flake）。KB 告警逻辑由 health_sensor --self-check 覆盖。
        self._orig_kb = hs._collect_kb_signals
        hs._collect_kb_signals = lambda now: {}

    def teardown(self):
        for k, v in self._orig.items():
            setattr(self._hs, k, v)
        self._hs._collect_kb_signals = self._orig_kb
        self._tmp.cleanup()

    def _write_proposal(self, jobs=None, history=None, status="optimizing"):
        now = datetime.now(timezone.utc)
        lc = {"proposals": {"test-p1": {
            "status": status,
            "pipeline_jobs": jobs or [],
            "score_history": history or [],
        }}}
        self._hs.LIFECYCLE_PATH.write_text(
            json.dumps(lc, ensure_ascii=False, indent=2), encoding="utf-8")
        return now

    def _mk_job(self, now, *, status="done", dur_s=600, api_error=False, age_min=10):
        started = now - timedelta(minutes=age_min, seconds=dur_s)
        finished = now - timedelta(minutes=age_min)
        j = {
            "job_id": f"job-{age_min}-{status}",
            "status": status,
            "started_at": _fmt_ts(started),
            "finished_at": _fmt_ts(finished),
        }
        if status == "failed":
            j["last_error"] = "api_error:HTTP 429 已达到 Token Plan 用量上限" if api_error else "timeout"
        return j

    def run_tests(self):
        hs = self._hs
        now = datetime.now(timezone.utc)

        # ── 用例 1：空转检测（429 空转真实故障模式） ──
        self._write_proposal(jobs=[
            self._mk_job(now, status="done", dur_s=13),   # 13s done = 空转
            self._mk_job(now, status="done", dur_s=13, age_min=30),
            self._mk_job(now, status="done", dur_s=13, age_min=50),
            self._mk_job(now, status="done", dur_s=300, age_min=70),  # 正常 job
        ])
        snap = hs.collect_snapshot()
        self.assert_eq(snap["global"]["idle_done_jobs_2h"], 3,
                       "空转检测: 3 个 <30s done job 被识别")
        risks = hs.evaluate_risks(snap)
        self.assert_true(any(r["type"] == "api_idle_spin" for r in risks),
                         "风险评估: 空转 ≥3 触发 api_idle_spin 告警")

        # ── 用例 2：API 错误爆发 ──
        self._write_proposal(jobs=[
            self._mk_job(now, status="failed", api_error=True, age_min=5),
            self._mk_job(now, status="failed", api_error=True, age_min=25),
        ])
        snap = hs.collect_snapshot()
        self.assert_eq(snap["global"]["api_error_jobs_2h"], 2,
                       "API 错误: 2 个 api_error failed job 被统计")
        self.assert_true(any(r["type"] == "api_error_burst" for r in hs.evaluate_risks(snap)),
                         "风险评估: api_error ≥2 触发爆发告警")

        # ── 用例 3：分数骤降（0.81→0.18 真实案例） ──
        self._write_proposal(history=[
            {"round": 3, "score": 0.81, "at": _fmt_ts(now - timedelta(hours=3))},
            {"round": 4, "score": 0.18, "at": _fmt_ts(now - timedelta(hours=1))},
        ])
        snap = hs.collect_snapshot()
        drops = snap["global"]["score_drops"]
        self.assert_eq(len(drops), 1, "分数骤降: 0.81→0.18 被检出")
        self.assert_eq(drops[0]["delta"], 0.63, "分数骤降: 分差 0.63")
        self.assert_true(any(r["type"] == "score_drop" for r in hs.evaluate_risks(snap)),
                         "风险评估: 骤降触发 score_drop 告警")

        # ── 用例 4：正常状态零告警 ──
        self._write_proposal(jobs=[
            self._mk_job(now, status="done", dur_s=400),
        ], history=[
            {"round": 1, "score": 0.76, "at": _fmt_ts(now - timedelta(hours=5))},
            {"round": 2, "score": 0.82, "at": _fmt_ts(now - timedelta(hours=1))},
        ])
        snap = hs.collect_snapshot()
        self.assert_eq(len(hs.evaluate_risks(snap)), 0,
                       "正常状态: 空转 0 / API 错误 0 / 分数上升 → 零告警")

        # ── 用例 5：窗口外旧 job 不计入 ──
        self._write_proposal(jobs=[
            self._mk_job(now, status="done", dur_s=10, age_min=150),  # 2.5h 前
        ])
        snap = hs.collect_snapshot()
        self.assert_eq(snap["global"]["idle_done_jobs_2h"], 0,
                       "时间窗口: 2h 外的空转 job 不计入")

        # ── 用例 6：熔断状态透传 ──
        self._hs.CIRCUIT_PATH.write_text(json.dumps({
            "state": "open", "consecutive_api_errors": 3, "opened_at": _fmt_ts(now),
        }), encoding="utf-8")
        snap = hs.collect_snapshot()
        self.assert_true(snap["circuit"] and snap["circuit"]["state"] == "open",
                         "熔断状态: open 状态透传到快照")
        self.assert_true(any(r["type"] == "circuit_open" for r in hs.evaluate_risks(snap)),
                         "风险评估: 熔断 open 产生 medium 告警")


if __name__ == "__main__":
    suite = HealthSensorTests()
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
