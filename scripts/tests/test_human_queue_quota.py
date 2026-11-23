#!/usr/bin/env python3
"""配额/重评门复核（quota_review）持久源回归（v7.3.28）。

覆盖四段：
    ① 写入持久源 → ② 聚合入队（总数/分类计数/字段透传）→
    ③ 再聚合幂等不丢（run_human_queue 整文件重写后条目仍在）→
    ④ 到期催办判定（到期前 0 等待不催办、到期后按超期小时数、≥72h 催办）。

零污染：临时目录 + 屏蔽 strategy / cluster_stale / input_broken 三个
外部派生源（它们会读生产文件），只测本类型逻辑。

用法：
    python3 scripts/self_test.py --module   # 自动发现
"""

import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).parent.parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from test_runner import TestSuite  # noqa: E402

import human_queue as HQ  # noqa: E402
from common import load_json, save_json  # noqa: E402

_DUE = "2026-11-09T00:00:00Z"


def _due_dt():
    return datetime(2026, 11, 9, 0, 0, tzinfo=timezone.utc)


def _entry(**kw):
    e = {
        "id": "quota_review_1109",
        "title": "11-09 配额复核：候选簇 ≥10 且方向过滤生效 → NEW_WEEKLY_QUOTA 2→3",
        "criteria": ["① 当周候选簇 ≥10", "② 方向过滤已上线并生效"],
        "decided_basis": "CHANGELOG v7.3.22 裁决 3",
        "due_date": _DUE,
        "status": "pending",
        "notes": "到期日复核，不以定时器自动改配置",
    }
    e.update(kw)
    return e


class HumanQueueQuotaTests(TestSuite):
    def __init__(self):
        super().__init__("配额复核持久源（v7.3.28）")

    def setup(self):
        self._tmp = tempfile.mkdtemp(prefix="hq_quota_")
        self._path = Path(self._tmp) / "quota-reviews.json"
        self._snap = Path(self._tmp) / "human-queue.json"
        self._orig_path = HQ.QUOTA_REVIEWS_PATH
        self._orig_snap = HQ.HUMAN_QUEUE_PATH
        HQ.QUOTA_REVIEWS_PATH = self._path
        HQ.HUMAN_QUEUE_PATH = self._snap
        self._patch = []
        for name in ("_pending_strategy_suggestions", "_pending_cluster_reviews",
                     "_pending_input_broken"):
            self._patch.append((name, getattr(HQ, name)))
            setattr(HQ, name, lambda now: [])

    def teardown(self):
        for name, fn in self._patch:
            setattr(HQ, name, fn)
        HQ.QUOTA_REVIEWS_PATH = self._orig_path
        HQ.HUMAN_QUEUE_PATH = self._orig_snap
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _write(self, entries):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        save_json(self._path, {"items": entries})

    def _quota_items(self, result):
        return [i for i in result["items"] if i["type"] == "quota_review"]

    def run_tests(self):
        # ── ① 写入持久源 ──────────────────────────────────────────
        self._write([_entry()])
        self.assert_true(self._path.exists(), "持久源文件应写入")
        data = load_json(self._path, default={})
        self.assert_eq(len(data.get("items") or []), 1, "写入 1 条 pending 事项")

        # ── ② 聚合入队（到期前） ──────────────────────────────────
        before = _due_dt().replace(day=6)  # 2026-11-06，距到期 72h
        result = HQ.collect_human_queue(proposals={}, now=before)
        qi = self._quota_items(result)
        self.assert_eq(len(qi), 1, "到期前条目应入队")
        item = qi[0]
        self.assert_eq(item["proposal_id"], "global:quota_review:quota_review_1109",
                       "proposal_id 前缀带类型，便于消费者区分")
        self.assert_eq(item["title"], _entry()["title"], "标题透传")
        self.assert_eq(len(item["criteria"]), 2, "判据列表透传")
        self.assert_true("v7.3.22" in item["decided_basis"], "决策依据透传")
        self.assert_eq(item["waiting_hours"], 0.0, "到期前等待恒为 0")
        self.assert_eq(item["escalate"], False, "到期前不催办")
        self.assert_true(item["due_in_hours"] > 0, "应给出距到期小时数")
        self.assert_eq(result["summary"]["quota_review"], 1, "分类计数 quota_review=1")
        self.assert_eq(result["summary"]["total"], 1, "total 计入该条")

        # ── ③ 再聚合幂等不丢（整文件重写后仍在） ──────────────────
        run1 = HQ.run_human_queue()
        run2 = HQ.run_human_queue()
        for idx, run in enumerate((run1, run2), start=1):
            self.assert_eq(run["summary"]["quota_review"], 1,
                           f"第 {idx} 次聚合 quota_review=1")
            self.assert_true(
                any(i["proposal_id"] == "global:quota_review:quota_review_1109"
                    for i in run["items"]),
                f"第 {idx} 次聚合条目仍在队列")
        snap = load_json(self._snap, default={})
        self.assert_true(
            any(i["proposal_id"] == "global:quota_review:quota_review_1109"
                for i in snap.get("items") or []),
            "快照重写后条目仍被重新载入（非幽灵）")
        self.assert_eq(run1["summary"]["total"], run2["summary"]["total"],
                       "两次聚合 total 一致")

        # ── ④ 到期催办判定 ────────────────────────────────────────
        at_due = HQ.collect_human_queue(proposals={}, now=_due_dt())
        self.assert_eq(self._quota_items(at_due)[0]["waiting_hours"], 0.0,
                       "到期当刻等待为 0")
        self.assert_eq(self._quota_items(at_due)[0]["escalate"], False,
                       "到期当刻尚不催办（沿用 72h 口径）")
        overdue30 = HQ.collect_human_queue(
            proposals={}, now=_due_dt().replace(day=10, hour=6))
        oi = self._quota_items(overdue30)[0]
        self.assert_eq(oi["waiting_hours"], 30.0, "超期 30h 计为等待 30h")
        self.assert_eq(oi["escalate"], False, "超期不足 72h 不催办")
        overdue100 = HQ.collect_human_queue(
            proposals={}, now=_due_dt().replace(day=13, hour=4))
        li = self._quota_items(overdue100)[0]
        self.assert_eq(li["waiting_hours"], 100.0, "超期 100h 计为等待 100h")
        self.assert_eq(li["escalate"], True, "超期 ≥72h 催办")
        self.assert_eq(li["due_in_hours"], 0.0, "已到期 due_in_hours 归 0")

        # ── ⑤ status=done 自动退出；无 due_date 不催办 ─────────────
        self._write([_entry(status="done")])
        self.assert_eq(len(self._quota_items(
            HQ.collect_human_queue(proposals={}, now=before))), 0,
            "status=done 不入队（改持久源即退队）")
        self._write([_entry(due_date=None)])
        nd = self._quota_items(HQ.collect_human_queue(proposals={}, now=before))[0]
        self.assert_eq(nd["waiting_hours"], 0.0, "无到期日时等待为 0")
        self.assert_eq(nd["escalate"], False, "无到期日不催办")
