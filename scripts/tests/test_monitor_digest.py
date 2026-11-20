#!/usr/bin/env python3
"""
test_monitor_digest.py — 健康检查"发现即消化"机制测试（v7.3.44）

覆盖：
    1. lifecycle.utils.digest_failed_job_action 纯决策函数：
       - retry 路径：repair_attempts < MAX 且失败过 2h 冷却 → "retry"
       - retry 冷却未满 → None（防 429 窗口烧重试预算）
       - retry 路径不与 auto_unlock 争用（repair_attempts 未达上限时）
       - auto_unlock 路径：双上限终态 + 24h 冷却满 → "auto_unlock"
       - auto_unlock 额度已用（auto_unlock_count>=1）→ None
       - 非 failed 状态 → None
    2. lifecycle_monitor._digest_failed_jobs 执行逻辑（fake ctrl，不落盘）：
       - retry 消化：字段重置与 run_repair 同构（attempts=0/repair_attempts+1）
       - auto_unlock 消化：auto_unlock_count 记账 + error_history 留痕
       - dry_run：只决策不写回（ctrl._save_jobs 不被调用、job 字段不变）
       - 落盘异常时 fail-open 返回空（下轮 lc-repair 兜底）

    2026-11-05 实证背景：ssh-weyl critic 双上限终态满足解锁条件后，
    因 lc-repair 12h 调度量化（上次扫描时差 50 分钟不够 24h 冷却），
    告警连刷 46 轮才解锁——本机制把处置时机从"下一轮 repair"提前到
    "满足条件即执行"。

注意：
    本测试不调用 hermes/LLM、不写真实数据目录，fake ctrl 只记录调用。
"""

import copy
import importlib
import sys
from datetime import datetime, timedelta, timezone

from test_runner import TestSuite

# v7.3.53（BUG-49）：固定时间锚点 + 相对时间戳。
#
# 根因：本文件原用绝对时间戳（如 finished_at="2026-11-05T04:50:31Z"）
# 配固定 now（2026-11-05T13:00:00Z）来断言「24h 冷却未满 → 无可消化动作」。
# 但 `_digest_failed_jobs` 内部硬取 `datetime.now(timezone.utc)`（真实墙钟），
# 判据的「相对墙钟」属性使该断言**随真实日期翻转**：2026-11-06T04:50:31Z
# 一过（当时 now=2026-11-06T08:0xZ），job 年龄从 8.16h 变为 27.4h 越过 24h
# 冷却线 → 消化动作从「无」变为「auto_unlock」→ 用例必失败。
# v84 轮（11-06 12h）实测 3657/3657 全绿，本轮（11-06 16h）实测
# 3654/3657 —— 同一份代码、同一份夹具，仅因日期推进 4 小时即翻红。
#
# 修复口径：① 时间戳改为相对锚点 `_NOW` 的偏移量（永不随墙钟漂移）；
# ② `_digest_failed_jobs` 调用显式传入 `now=_NOW`（v7.3.53 新增注入缝）。
# **判据、阈值、决策逻辑一字未动。**
_NOW = datetime(2026, 11, 5, 13, 0, 0, tzinfo=timezone.utc)


def _ago(hours: float) -> str:
    """相对锚点 _NOW 偏移若干小时的 ISO 时间戳。"""
    return (_NOW - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _job(**overrides):
    """构造标准 failed job 夹具（时间戳相对锚点，不随墙钟漂移）。"""
    base = {
        "job_id": "test-proposal-r1-scheme-critic",
        "status": "failed",
        "attempts": 3,
        "repair_attempts": 0,
        "started_at": _ago(32.5),
        "finished_at": _ago(32.0),
        "last_error": "超时(1200s)",
        "error_history": [],
    }
    base.update(overrides)
    return base


class _FakeCtrl:
    """记录 _save_jobs 调用的假 controller（可注入落盘异常）。"""

    def __init__(self, fail_save=False):
        self.saved = []          # [(pid, jobs)]
        self.fail_save = fail_save

    def _save_jobs(self, pid, jobs):
        if self.fail_save:
            raise RuntimeError("模拟落盘失败")
        self.saved.append((pid, copy.deepcopy(jobs)))


class MonitorDigestTests(TestSuite):
    def __init__(self):
        super().__init__("健康检查发现即消化机制测试")
        self.utils = None
        self.monitor = None

    def setup(self):
        for mod_name in list(sys.modules.keys()):
            if mod_name in ("lifecycle_monitor", "lifecycle.utils", "lifecycle"):
                del sys.modules[mod_name]
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
        self.utils = importlib.import_module("lifecycle.utils")
        self.monitor = importlib.import_module("lifecycle_monitor")

    def run_tests(self):
        now = _NOW

        # ================================================================
        # 一、digest_failed_job_action 纯决策函数
        # ================================================================
        self.assert_eq(
            self.utils.digest_failed_job_action(
                _job(repair_attempts=1, finished_at=_ago(8.5)), now),
            "retry",
            "retry：repair_attempts<MAX 且失败已过 2h 冷却",
        )
        self.assert_eq(
            self.utils.digest_failed_job_action(
                _job(repair_attempts=1, finished_at=_ago(0.5)), now),
            None,
            "retry 冷却未满（失败仅 0.5h）→ None",
        )
        self.assert_eq(
            self.utils.digest_failed_job_action(
                _job(repair_attempts=1, finished_at=""), now),
            "retry",
            "finished_at 缺失（异常态）→ 放行 retry 交执行方重置",
        )
        self.assert_eq(
            self.utils.digest_failed_job_action(
                _job(status="running"), now),
            None,
            "非 failed 状态 → None",
        )
        self.assert_eq(
            self.utils.digest_failed_job_action(
                _job(repair_attempts=3, finished_at=_ago(32)), now),
            "auto_unlock",
            "双上限终态 + 失败超 24h → auto_unlock",
        )
        self.assert_eq(
            self.utils.digest_failed_job_action(
                _job(repair_attempts=3, finished_at=_ago(8)), now),
            None,
            "双上限终态但 24h 冷却未满（失败 8h 前）→ None",
        )
        self.assert_eq(
            self.utils.digest_failed_job_action(
                _job(repair_attempts=3, auto_unlock_count=1,
                     finished_at=_ago(32)), now),
            None,
            "auto_unlock 额度已用（终生一次）→ None",
        )

        # ================================================================
        # 二、_digest_failed_jobs 执行逻辑（fake ctrl）
        # ================================================================
        # 2.1 retry 消化：字段重置与 run_repair 同构
        ctrl = _FakeCtrl()
        job = _job(repair_attempts=1, finished_at=_ago(8.5))
        result = self.monitor._digest_failed_jobs(
            "test-proposal", [job], ctrl, now=now)
        self.assert_eq(len(result), 1, "retry 消化返回 1 条记录")
        self.assert_eq(result[0]["action"], "retry", "动作名为 retry")
        self.assert_eq(job["status"], "pending", "job 状态重置为 pending")
        self.assert_eq(job["attempts"], 0, "attempts 清零")
        self.assert_eq(job["repair_attempts"], 2, "repair_attempts 1→2")
        self.assert_eq(job["last_error"], "", "last_error 清空")
        self.assert_eq(len(ctrl.saved), 1, "ctrl._save_jobs 落盘一次")
        self.assert_eq(ctrl.saved[0][0], "test-proposal", "落盘 pid 正确")

        # 2.2 auto_unlock 消化：记账 + error_history 留痕
        ctrl = _FakeCtrl()
        job = _job(repair_attempts=3, finished_at=_ago(32))
        result = self.monitor._digest_failed_jobs(
            "test-proposal", [job], ctrl, now=now)
        self.assert_eq(result[0]["action"], "auto_unlock", "动作名为 auto_unlock")
        self.assert_eq(job["status"], "pending", "解锁后状态 pending")
        self.assert_eq(job.get("auto_unlock_count"), 1, "auto_unlock_count 记账 1")
        self.assert_eq(job["repair_attempts"], 3, "解锁不动 repair_attempts")
        hist = job.get("error_history") or []
        self.assert_true(
            any("监控消化" in str(e.get("error", "")) for e in hist),
            "error_history 留痕含消化来源标记",
        )

        # 2.3 双上限 + 冷却未满：不消化、不落盘
        # v7.3.53（BUG-49）：此处即原「墙钟定时炸弹」现场——失败时间距 now
        # 仅 8h（未满 24h 冷却线），旧实现用真实墙钟判定 → 日期一过
        # 该断言必翻转失败。现显式传入 now=锚点，判据恒定。
        ctrl = _FakeCtrl()
        job = _job(repair_attempts=3, finished_at=_ago(8))
        result = self.monitor._digest_failed_jobs(
            "test-proposal", [job], ctrl, now=now)
        self.assert_eq(len(result), 0, "无可消化动作 → 空列表")
        self.assert_eq(job["status"], "failed", "job 状态不变")
        self.assert_eq(len(ctrl.saved), 0, "未触发落盘")

        # 2.4 dry_run：只决策不写回
        ctrl = _FakeCtrl()
        job = _job(repair_attempts=1, finished_at=_ago(8.5))
        result = self.monitor._digest_failed_jobs(
            "test-proposal", [job], ctrl, dry_run=True, now=now)
        self.assert_eq(len(result), 1, "dry_run 仍返回消化决策（可观测）")
        self.assert_eq(job["status"], "failed", "dry_run 不改内存 job 字段")
        self.assert_eq(len(ctrl.saved), 0, "dry_run 不落盘")

        # 2.5 落盘失败 fail-open：返回空，交下轮 lc-repair 兜底
        ctrl = _FakeCtrl(fail_save=True)
        job = _job(repair_attempts=1, finished_at=_ago(8.5))
        result = self.monitor._digest_failed_jobs(
            "test-proposal", [job], ctrl, now=now)
        self.assert_eq(len(result), 0, "落盘失败 → 返回空（不虚报已消化）")
        self.assert_eq(job["status"], "pending", "内存字段已重置（下轮幂等跳过）")

        # ================================================================
        # 三、决策与执行的边界一致性
        # ================================================================
        # retry 冷却阈值可调：cooldown=0 时刚失败也放行（等价 repair 语义）
        self.assert_eq(
            self.utils.digest_failed_job_action(
                _job(repair_attempts=0, finished_at=_ago(0.02)),
                now, retry_cooldown_h=0.0),
            "retry",
            "retry_cooldown_h=0 退化为 repair 原语义（无冷却）",
        )
        # MAX_JOB_ATTEMPTS 对齐（决策函数引用同一常量）
        self.assert_eq(self.utils.MAX_JOB_ATTEMPTS, 3, "MAX_JOB_ATTEMPTS=3 对齐")

        # ================================================================
        # 四、BUG-49 反向断言：注入缝是承重结构（防修复被旁路）
        # ================================================================
        # 若 `_digest_failed_jobs` 的 now 注入缝被移除（退化为真实墙钟），
        # 则 2.3 的固定 now 断言将不再生效 → 该用例必然随日期翻转。
        # 这里证明「同一 job 的判定是 now 的函数」——两个 now 均相对同一
        # 基准时钟构造，与墙钟无关，故本断言本身永不翻转：
        #   · now = base        → job 年龄 48h（越过 24h 冷却线）→ auto_unlock
        #   · now = base - 30h  → job 年龄 18h（未满 24h 冷却线）→ None
        base = datetime.now(timezone.utc)
        aged_job = _job(
            repair_attempts=3,
            finished_at=(base - timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.assert_eq(
            self.utils.digest_failed_job_action(aged_job, base),
            "auto_unlock",
            "now=base：job 失败 48h，越过 24h 冷却线 → auto_unlock",
        )
        self.assert_eq(
            self.utils.digest_failed_job_action(
                aged_job, base - timedelta(hours=30)),
            None,
            "now=base-30h：同一 job 失败仅 18h，未满冷却线 → None"
            "（证明判定随 now 变化，故必须固定 now 才能稳定断言）",
        )


if __name__ == "__main__":
    suite = MonitorDigestTests()
    suite.setup()
    suite.run_tests()
    s = suite.summary()
    print(f"\n{'✓' if s['failed'] == 0 else '✗'} {s['name']}: {s['passed']}/{s['total']} 通过")
    for r in s["results"]:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    sys.exit(0 if s["failed"] == 0 else 1)
