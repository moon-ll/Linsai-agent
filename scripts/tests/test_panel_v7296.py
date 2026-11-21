#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_panel_v7296.py — 评审团并发防护测试（v7.2.96）。

背景（v7.2.82 暴露、挂账「待治理轮处理」）：lc-panel-review cron（10:00）
与长跑消费者（v7.2.80 runner / 引擎亲审会话）并发消费同一评审团队列——
run_panel 主流程无任何互斥，仅靠产物文件缓存兜底，双方同时跑同一课题，
产出互相覆盖/重复消耗 LLM，runner 产物被迫降级为预审档案。

v7.2.96 双层防护：
1. run_panel 互斥外壳：per-proposal 非阻塞 flock（panel-<pid>），锁忙
   返回 skipped=lock_busy（周末流水线 run_next 同惯用法）；
2. 06_panel/claim.json 在场声明：手工会话经 --claim/--release 声明，
   脚本消费者读到新鲜异主声明即跳过；TTL 防会话崩溃僵尸。

覆盖：
1. _read_fresh_claim：缺失/损坏/过期 → None；新鲜 → 返回声明
2. claim_panel：写入/续期/异主拒抢
3. release_panel_claim：释放/归属校验（拒删他人声明）/重复释放幂等
4. run_panel：异主在场声明 → skipped=lock_busy；同主声明 → 正常执行
   （dry_run 路径）；panel 锁被持有时非阻塞跳过；退出清理声明
5. 源码守卫：--run-all 逐课题容错保留（v7.2.57 语义不回退）、CLI 入口

用法：
    python3 scripts/self_test.py --module   # 自动发现
    python3 scripts/tests/test_panel_v7296.py
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite


class PanelV7296Tests(TestSuite):
    def __init__(self):
        super().__init__("v7.2.96 评审团并发防护测试")
        self.tmp_root = None
        self.pr = None
        self._old_lock_dir = None

    def assert_true(self, condition, name, msg: str = "") -> bool:
        if isinstance(condition, str):
            condition, name = name, condition
        return super().assert_true(bool(condition), str(name), msg)

    def setup(self):
        self.tmp_root = Path(tempfile.mkdtemp(prefix="linsai_panel_v7296_"))
        # 隔离锁目录：与真实 cron/worker 争用同一 /tmp 锁文件
        self._old_lock_dir = os.environ.get("LINSAI_LOCK_DIR")
        os.environ["LINSAI_LOCK_DIR"] = str(self.tmp_root / "locks")
        import importlib
        self.pr = __import__("panel_review", fromlist=["x"])
        importlib.reload(self.pr)

    def teardown(self):
        if self._old_lock_dir is not None:
            os.environ["LINSAI_LOCK_DIR"] = self._old_lock_dir
        else:
            os.environ.pop("LINSAI_LOCK_DIR", None)
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)

    # ── 夹具：tmp 根接管 PROJECT_ROOT，构造最小课题布局 ──

    def _make_proposal(self, pid: str) -> Path:
        """optimizing/<pid>/06_panel + 空 _lifecycle.json（零问题清单）。"""
        prop = self.tmp_root / "research_proposals" / "optimizing" / pid
        (prop / "06_panel").mkdir(parents=True, exist_ok=True)
        lc = self.tmp_root / "research_proposals" / "_lifecycle.json"
        if not lc.exists():
            lc.write_text(json.dumps({"proposals": {}}, ensure_ascii=False),
                          encoding="utf-8")
        return prop

    def run_tests(self):
        pr = self.pr
        old_root = pr.PROJECT_ROOT
        pr.PROJECT_ROOT = self.tmp_root
        try:
            self._run_claim_tests(pr)
            self._run_runpanel_tests(pr)
            self._run_source_guard(pr)
        finally:
            pr.PROJECT_ROOT = old_root

    # ── 1-3. 在场声明原语 ──

    def _run_claim_tests(self, pr):
        pid = "general-v7296-claim-20261101"
        prop = self._make_proposal(pid)

        # 1. 缺失 → None
        self.assert_true(pr._read_fresh_claim(pid) is None,
                         "无声明文件时 _read_fresh_claim 返回 None")

        # 损坏 JSON → None（fail-open 不阻塞队列）
        cp = prop / "06_panel" / "claim.json"
        cp.write_text("{oops", encoding="utf-8")
        self.assert_true(pr._read_fresh_claim(pid) is None,
                         "损坏声明视作无声明（fail-open）")

        # 过期声明 → None（TTL 防僵尸）
        cp.write_text(json.dumps({
            "consumer": "ghost-session",
            "started_at": "2020-01-01T00:00:00Z",
        }, ensure_ascii=False), encoding="utf-8")
        self.assert_true(pr._read_fresh_claim(pid) is None,
                         "超 TTL 声明视作无声明（防会话崩溃僵尸）")

        # 新鲜声明 → 返回
        cp.write_text(json.dumps({
            "consumer": "manual-a",
            "started_at": pr.now_utc(),
        }, ensure_ascii=False), encoding="utf-8")
        fresh = pr._read_fresh_claim(pid)
        self.assert_true(fresh is not None and fresh.get("consumer") == "manual-a",
                         "新鲜声明正常读回")

        # 2. claim_panel：异主拒抢 / 同主续期
        r = pr.claim_panel(pid, consumer="manual-b")
        self.assert_true(not r.get("success") and r.get("skipped") == "claim_busy",
                         "异主声明存在时 claim 拒抢（claim_busy）")
        self.assert_true(r.get("holder") == "manual-a",
                         "claim_busy 返回持有人（运维可见）")
        r2 = pr.claim_panel(pid, consumer="manual-a")
        self.assert_true(r2.get("success"), "同 consumer 重复 claim 视为续期")

        # 3. release_panel_claim：归属校验 / 释放 / 幂等
        r = pr.release_panel_claim(pid, consumer="manual-b")
        self.assert_true(not r.get("success") and "拒绝释放" in r.get("error", ""),
                         "异主 release 拒绝（防误删他人声明）")
        r = pr.release_panel_claim(pid, consumer="manual-a")
        self.assert_true(r.get("released"), "归属方 release 成功")
        r = pr.release_panel_claim(pid, consumer="manual-a")
        self.assert_true(r.get("success") and not r.get("released"),
                         "重复 release 幂等")

        # 未知课题 → 目录不存在错误
        r = pr.claim_panel("nonexistent-v7296", consumer="x")
        self.assert_true(not r.get("success") and "不存在" in r.get("error", ""),
                         "未知课题 claim 返回目录不存在")

    # ── 4. run_panel 互斥外壳 ──

    def _run_runpanel_tests(self, pr):
        pid = "general-v7296-run-20261101"
        self._make_proposal(pid)
        cp = self.tmp_root / "research_proposals" / "optimizing" / pid / "06_panel" / "claim.json"

        # 异主在场声明 → run_panel 温和跳过（不进入三角色流程）
        cp.write_text(json.dumps({
            "consumer": "engine-review-session",
            "started_at": pr.now_utc(),
        }, ensure_ascii=False), encoding="utf-8")
        r = pr.run_panel(pid, dry_run=True, consumer="panel-runner")
        self.assert_true(r.get("skipped") == "lock_busy" and not r.get("success"),
                         "异主在场声明时 run_panel 返回 lock_busy 跳过")
        self.assert_true("engine-review-session" in r.get("reason", ""),
                         "跳过原因含持有人（可观测）")
        self.assert_true(cp.exists(), "跳过路径不清理异主声明")

        # 同主声明 → 正常进入 dry_run 流程，退出后声明清理
        # v7.2.97 起 executor 默认 "engine"（任务包发射器，不产三角色阶段）——
        # 本用例验证的是互斥外壳与三角色流程的对接，钉 hermes 路径
        old_exec = pr._executor_config
        pr._executor_config = lambda: "hermes"
        try:
            r = pr.run_panel(pid, dry_run=True, consumer="engine-review-session")
        finally:
            pr._executor_config = old_exec
        self.assert_true(r.get("success") is not False,
                         "同主声明时 run_panel 正常执行 dry_run 流程")
        self.assert_true(any("review_" in k for k in (r.get("stages") or {})),
                         "dry_run 流程产出三角色阶段记录（hermes 执行器）")
        self.assert_true(not cp.exists(),
                         "run_panel 退出后自动清理本消费者声明")

        # flock 互斥：手工先抢 panel-<pid> 锁 → run_panel 非阻塞跳过
        import fcntl
        lock_path = self.tmp_root / "locks" / f"linsai-copilot-panel-{pid}.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with open(lock_path, "w") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (BlockingIOError, OSError):
                return  # 环境不支持 flock：跳过该用例（Windows 降级路径）
            r = pr.run_panel(pid, dry_run=True, consumer="panel-runner")
            self.assert_true(r.get("skipped") == "lock_busy",
                             "panel 锁被持有时 run_panel 非阻塞跳过（不挂起）")

    # ── 5. 源码守卫 ──

    def _run_source_guard(self, pr):
        src = (_SCRIPTS_DIR / "panel_review.py").read_text(encoding="utf-8")
        self.assert_true("--claim" in src and "--release" in src,
                         "手工会话声明 CLI 入口存在")
        self.assert_true("逐课题容错" in src,
                         "--run-all 逐课题容错语义保留（v7.2.57 不回退）")
        self.assert_true("PANEL_CLAIM_TTL_HOURS" in src,
                         "在场声明 TTL 常量在位（防僵尸声明）")
        self.assert_true("lock_busy" in src,
                         "lock_busy 温和退出语义在位（周末流水线同惯用法）")


if __name__ == "__main__":
    suite = PanelV7296Tests()
    suite.setup()
    try:
        suite.run_tests()
    finally:
        suite.teardown()
    ok = sum(1 for r in suite.results if r.passed)
    total = len(suite.results)
    print(f"\n{'✓' if ok == total else '✗'} {suite.name}: {ok}/{total} 通过")
    for r in suite.results:
        icon = "✓" if r.passed else "✗"
        print(f"  {icon} {r.name}" + (f" — {r.msg}" if r.msg else ""))
    raise SystemExit(1 if total - ok else 0)
