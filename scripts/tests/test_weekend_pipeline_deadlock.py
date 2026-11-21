#!/usr/bin/env python3
"""
test_weekend_pipeline_deadlock.py — 周末流水线「修复上限后永久死锁」回归测试（v7.2.46）

背景（2026-10-26 04h 健康检查 P0-2 实测）：
    `repair_attempts` 是**单向计数器**——`reset_failed_job` 只做 `+= 1`，
    全库无任何路径能把它归零。于是当 job 的失败根因是代码缺陷
    （而非瞬时超时）且该缺陷已被修复后，job 仍永久卡在 failed：

      1. `repair_stale_and_failed` 条件 `repair_attempts < MAX_JOB_ATTEMPTS`
         在 repair_attempts=3 时为假 → 不重试
      2. `_resolve_blocking_deps` 同一条件 → 下游 pending 全部阻塞
      3. `_reset_stage_for_new_week` 跨周重置只清 status/attempts，
         **不清 repair_attempts** → 跨周重跑仍带 3 → 再次失败

    生产后果：周末反思链 `reflection_kb_merge_duplicates`（BUG-10
    `int` title 崩溃，代码已于 v7.2.45 修复）在 10-25 02:20 失败后
    repair_attempts 打满 3/3，下游四个 job
    （proposal_calibration → link_deep_review → kb_taxonomy_apply →
    panel_plan）永久 pending → **整个周末反思链死锁**。

本测试覆盖：
    1. should_auto_unlock_failed 六种场景（与 proposal 级
       lifecycle.utils.should_auto_unlock 同构口径）
    2. repair_stale_and_failed 的自动解锁分支（含 repair_attempts 归零）
    3. _resolve_blocking_deps 的自动解锁分支（解锁下游阻塞）
    4. 跨周重置必须清 repair_attempts（v7.2.46 新增）
    5. 反向断言：未达上限 / 未过冷却期 / 已解锁过 → 不得解锁

注意：本测试不调用 LLM，运行于隔离临时目录，零生产副作用。
"""

import sys
import shutil
import importlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from test_runner import TestSuite, create_isolated_env, patch_module_root, REAL_ROOT


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class WeekendPipelineDeadlockTests(TestSuite):
    def __init__(self):
        super().__init__("周末流水线死锁逃生阀测试（v7.2.46）")
        self.tmp_root = None

    # ------------------------------------------------------------------
    # 隔离环境
    # ------------------------------------------------------------------

    def setup(self):
        self.tmp_root = create_isolated_env()
        for stage in ["drafts", "optimizing", "pending_review", "archived"]:
            (self.tmp_root / "research_proposals" / stage).mkdir(parents=True, exist_ok=True)

        standards_src = REAL_ROOT / "memory" / "nsfc-standards.json"
        if standards_src.exists():
            (self.tmp_root / "memory").mkdir(parents=True, exist_ok=True)
            shutil.copy(standards_src, self.tmp_root / "memory" / "nsfc-standards.json")

        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("weekend_pipeline") or mod_name.startswith("proposal_lifecycle"):
                del sys.modules[mod_name]

        import paths
        self._orig_project_root = paths.PROJECT_ROOT
        paths.PROJECT_ROOT = self.tmp_root
        self.wp_mod = importlib.import_module("weekend_pipeline")
        patch_module_root("weekend_pipeline", self.tmp_root)
        patch_module_root("proposal_lifecycle", self.tmp_root)

    def teardown(self):
        if self.tmp_root and self.tmp_root.exists():
            shutil.rmtree(self.tmp_root, ignore_errors=True)
        if hasattr(self, "_orig_project_root"):
            import paths
            paths.PROJECT_ROOT = self._orig_project_root

    # ------------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------------

    def _failed_job(self, **overrides):
        """构造一个「已达修复上限」的 failed job（默认失败于 30h 前）。"""
        now = datetime.now(timezone.utc)
        job = {
            "job_id": "reflection_kb_merge_duplicates",
            "stage": "reflection",
            "step": "kb_merge_duplicates",
            "status": "failed",
            "attempts": 1,
            "repair_attempts": 3,
            "started_at": _iso(now - timedelta(hours=30)),
            "finished_at": _iso(now - timedelta(hours=30)),
            "last_error": "'int' object has no attribute 'lower'",
            "depends_on": [],
        }
        job.update(overrides)
        return job

    def _state_with(self, jobs):
        return {"jobs": jobs, "stage_status": {}, "updated_at": _iso(datetime.now(timezone.utc))}

    # ------------------------------------------------------------------
    # 用例
    # ------------------------------------------------------------------

    def _test_should_auto_unlock_scenarios(self):
        """should_auto_unlock_failed 六种场景（与 proposal 级同构口径）。"""
        from weekend_pipeline.executor import should_auto_unlock_failed
        from weekend_pipeline.constants import MAX_JOB_ATTEMPTS

        now = datetime.now(timezone.utc)
        old = _iso(now - timedelta(hours=30))

        # 1. 达上限 + 超冷却期 → 可解锁
        self.assert_true(
            should_auto_unlock_failed(self._failed_job(finished_at=old), now),
            "达上限且失败超 24h → 应可解锁",
        )
        # 2. 未达上限 → 不可解锁
        self.assert_true(
            not should_auto_unlock_failed(
                self._failed_job(repair_attempts=MAX_JOB_ATTEMPTS - 1, finished_at=old), now
            ),
            "未达修复上限 → 不可解锁",
        )
        # 3. 冷却期内 → 不可解锁
        self.assert_true(
            not should_auto_unlock_failed(
                self._failed_job(finished_at=_iso(now - timedelta(hours=2))), now
            ),
            "冷却期 24h 内 → 不可解锁",
        )
        # 4. 已解锁过（auto_unlock_count>=1）→ 不可再解锁
        self.assert_true(
            not should_auto_unlock_failed(
                self._failed_job(finished_at=old, auto_unlock_count=1), now
            ),
            "已自动解锁过 → 不可再解锁（防无限重试）",
        )
        # 5. 非 failed → 不可解锁
        self.assert_true(
            not should_auto_unlock_failed(
                self._failed_job(finished_at=old, status="pending"), now
            ),
            "非 failed 状态 → 不可解锁",
        )
        # 6. 缺 finished_at → 不可解锁（无法判断冷却期）
        self.assert_true(
            not should_auto_unlock_failed(
                self._failed_job(finished_at=""), now
            ),
            "缺 finished_at → 不可解锁",
        )

    def _test_auto_unlock_resets_repair_attempts(self):
        """解锁时必须归零 repair_attempts——单向计数器缺陷的正解。"""
        from weekend_pipeline.executor import auto_unlock_failed_job

        job = self._failed_job()
        auto_unlock_failed_job(job)

        self.assert_eq(job["status"], "pending", "解锁后 status=pending")
        self.assert_eq(job["attempts"], 0, "解锁后 attempts=0")
        self.assert_eq(job["repair_attempts"], 0, "解锁后 repair_attempts 归零（关键）")
        self.assert_eq(job["auto_unlock_count"], 1, "auto_unlock_count=1")
        self.assert_eq(job["last_error"], "", "解锁后清空 last_error")
        self.assert_eq(job["finished_at"], "", "解锁后清空 finished_at")
        self.assert_true(bool(job.get("error_history")), "error_history 应记录解锁事件")

    def _test_repair_auto_unlocks_exhausted_job(self):
        """repair_stale_and_failed 的自动解锁分支。"""
        from weekend_pipeline.executor import repair_stale_and_failed

        job = self._failed_job()
        state = self._state_with([job])
        repaired = repair_stale_and_failed(state)

        self.assert_eq(len(repaired), 1, "应产生 1 条修复记录")
        self.assert_in("auto_unlock", repaired[0]["action"], "动作为 auto_unlock")
        self.assert_eq(job["status"], "pending", "job 应变 pending")
        self.assert_eq(job["repair_attempts"], 0, "repair_attempts 应归零")

    def _test_repair_does_not_unlock_within_cooldown(self):
        """冷却期内不得解锁（反向断言）。"""
        from weekend_pipeline.executor import repair_stale_and_failed

        now = datetime.now(timezone.utc)
        job = self._failed_job(finished_at=_iso(now - timedelta(hours=1)))
        state = self._state_with([job])
        repaired = repair_stale_and_failed(state)

        self.assert_eq(len(repaired), 0, "冷却期内不应有修复动作")
        self.assert_eq(job["status"], "failed", "job 保持 failed")
        self.assert_eq(job["repair_attempts"], 3, "repair_attempts 保持 3")

    def _test_resolve_blocking_deps_auto_unlocks(self):
        """_resolve_blocking_deps 自动解锁失败依赖，下游得以解锁。"""
        from weekend_pipeline.executor import _resolve_blocking_deps

        dep = self._failed_job()
        downstream = {
            "job_id": "reflection_proposal_calibration",
            "stage": "reflection",
            "step": "proposal_calibration",
            "status": "pending",
            "attempts": 0,
            "repair_attempts": None,
            "depends_on": ["reflection_kb_merge_duplicates"],
        }
        state = self._state_with([dep, downstream])

        resolved = _resolve_blocking_deps(state, "reflection")
        self.assert_eq(resolved, 1, "应解锁 1 个失败依赖")
        self.assert_eq(dep["status"], "pending", "失败依赖应变 pending")
        self.assert_eq(dep["repair_attempts"], 0, "失败依赖 repair_attempts 应归零")

        # 解锁后依赖变 pending（尚未 done），下游依赖此时仍**不**满足——
        # dependencies_satisfied 要求依赖在 done 集合，这是严格顺序语义
        # （失败不跳过，必须先重试成功）。下游会在被解锁的 job 跑完
        # 变 done 后才被挑出。
        from weekend_pipeline.executor import dependencies_satisfied
        self.assert_true(
            not dependencies_satisfied(downstream, state),
            "解锁后依赖仍非 done → 下游依赖暂不满足（严格顺序语义）",
        )

    def _test_pick_next_job_unblocks_after_auto_unlock(self):
        """端到端：pick_next_job 应在自动解锁后返回可执行 job。"""
        from weekend_pipeline.executor import pick_next_job

        dep = self._failed_job()
        downstream = {
            "job_id": "reflection_proposal_calibration",
            "stage": "reflection",
            "step": "proposal_calibration",
            "status": "pending",
            "attempts": 0,
            "repair_attempts": None,
            "depends_on": ["reflection_kb_merge_duplicates"],
        }
        state = self._state_with([dep, downstream])

        job = pick_next_job(state, stage="reflection")
        self.assert_true(job is not None, "自动解锁后应能挑出 job（此前恒为 None）")
        self.assert_eq(
            job["job_id"], "reflection_kb_merge_duplicates",
            "应先挑出被自动解锁的失败依赖",
        )

    def _test_cross_week_reset_clears_repair_attempts(self):
        """v7.2.46：跨周重置必须清 repair_attempts。"""
        from weekend_pipeline.pipeline import WeekendPipeline

        p = WeekendPipeline(state_path=self.tmp_root / "memory" / "weekend-pipeline.json")
        p.sync_stage_jobs("reflection")
        jobs = p.list_jobs(stage="reflection")
        target = jobs[0]
        target["status"] = "failed"
        target["repair_attempts"] = 3
        target["attempts"] = 1
        p._save()

        # 构造跨周：把该阶段所有 job 的 finished_at 推到上周（跨周锚点之前）
        for j in p.state["jobs"]:
            if j.get("stage") == "reflection":
                j["finished_at"] = "2020-01-01T00:00:00Z"
        p._save()

        reset_count = p._reset_stage_for_new_week("reflection")
        self.assert_true(reset_count > 0, "跨周重置应触发", f"reset_count={reset_count}")

        after = next(j for j in p.state["jobs"] if j["job_id"] == target["job_id"])
        self.assert_eq(after["status"], "pending", "跨周后 status=pending")
        self.assert_eq(after["attempts"], 0, "跨周后 attempts=0")
        self.assert_eq(
            after["repair_attempts"], 0,
            "跨周后 repair_attempts 必须归零（v7.2.46 关键修复点）",
        )

    def _test_run_next_persists_repair_when_no_job_runnable(self):
        """v7.2.47：run_next 在「无可执行 job」时必须落盘自愈结果。

        10-26 08h 健康检查 BUG-11 实测缺陷：v7.2.46 在 run_next 中新增
        的 repair_stale_and_failed 自愈，若解锁后的 job 依赖仍不满足
        （上游同样 failed 且未解锁），pick_next_job 返回 None → run_next
        提前 return 且**不落盘** → 自愈结果全部丢失。后果：
          - auto_unlock_count 恒为 None → 「终生至多解锁一次」守卫失效，
            每个 tick 重复解锁
          - repair_attempts 恒不增长 → auto-unlock 逃生阀永不触发
            → v7.2.46 的死锁修复形同虚设
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        # A：已达上限 + 超冷却期 → 本轮会被自动解锁；但依赖 B
        # B：同样 failed 但冷却期未到 → 本轮不解锁 → A 仍不可执行
        job_a = self._failed_job(
            job_id="reflection_proposal_calibration",
            step="proposal_calibration",
            depends_on=["reflection_kb_merge_duplicates"],
            finished_at=_iso(now - timedelta(hours=30)),
        )
        job_b = self._failed_job(
            job_id="reflection_kb_merge_duplicates",
            step="kb_merge_duplicates",
            depends_on=[],
            finished_at=_iso(now - timedelta(hours=1)),
        )
        state_path.write_text(
            json.dumps(
                {
                    "jobs": [job_a, job_b],
                    "stage_status": {"reflection": "failed"},
                    "processed_sources": {},
                    "input_round": {},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        pipe = WeekendPipeline(state_path=state_path)
        res = pipe.run_next(stage="reflection")
        self.assert_true(
            bool(res.get("repaired")),
            "本轮应产生自愈动作（auto_unlock）",
        )

        disk = json.loads(state_path.read_text(encoding="utf-8"))
        disk_a = next(j for j in disk["jobs"] if j["job_id"] == "reflection_proposal_calibration")
        self.assert_eq(
            disk_a.get("auto_unlock_count"), 1,
            "自愈结果必须落盘（auto_unlock_count=1）——否则每 tick 重复解锁，"
            "「终生至多一次」守卫失效",
        )
        self.assert_eq(
            disk_a.get("repair_attempts"), 0,
            "解锁后 repair_attempts 必须归零并落盘",
        )

        # 第二次 tick：磁盘已记录 auto_unlock_count=1 → 不应再解锁
        pipe2 = WeekendPipeline(state_path=state_path)
        res2 = pipe2.run_next(stage="reflection")
        disk2 = json.loads(state_path.read_text(encoding="utf-8"))
        disk_a2 = next(j for j in disk2["jobs"] if j["job_id"] == "reflection_proposal_calibration")
        self.assert_eq(
            disk_a2.get("auto_unlock_count"), 1,
            "已解锁过的 job 不得被重复解锁（守卫须真正生效）",
        )
        self.assert_true(
            not any(r.get("action", "").startswith("auto_unlock")
                    for r in (res2.get("repaired") or [])),
            "第二 tick 不应再次执行 auto_unlock",
        )

    def _test_run_stage_persists_heal_when_no_job_runnable(self):
        """v7.2.52（BUG-19）：run_stage 在「无可执行 job」时必须落盘自愈结果。

        10-27 16h 健康检查实测缺陷：v7.2.47 只修了 run_next 路径，
        run_stage（周末入口 cron / run-all 主路径）未修——自愈发生
        （_resolve_blocking_deps 解锁 failed 依赖）后 pick_next_job
        返回 None，旧版直接 break 且**不落盘**，函数末尾「汇总阶段
        状态」块又重新 load 磁盘状态 → 自愈结果被丢弃。后果与 BUG-11
        同构：
          - auto_unlock_count 恒为 None → 「终生至多解锁一次」守卫失效
          - repair_attempts 恒不增长 → auto-unlock 逃生阀永不触发
            → 周末反思链永久死锁

        触发形状（三节点，均为 reflection 阶段）：
          G（failed, auto_unlock_count=1 终生不可解锁）
            └─ F（failed, repair_attempts=3 且失败超 24h → 本轮被解锁）
                 └─ P（pending，依赖 F）
        _resolve_blocking_deps 解锁 F（status→pending / repair_attempts→0
        / auto_unlock_count→1），但 F 仍依赖未完成的 G → F 不可执行；
        P 依赖未完成的 F → 不可执行 → pick_next_job 返回 None。

        10-27 16h 隔离目录确定性复现：同一份 state，run_next 落盘成功
        （auto_unlock_count=1 / repair_attempts=0），run_stage 落盘为空
        （failed/3/None）——两条路径两种结果。
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_bug19_state(state_path)

        pipe = WeekendPipeline(state_path=state_path)
        pipe.run_stage("reflection")

        disk = json.loads(state_path.read_text(encoding="utf-8"))
        disk_f = next(j for j in disk["jobs"] if j["job_id"] == "reflection_kb_merge_duplicates")
        self.assert_eq(
            disk_f.get("auto_unlock_count"), 1,
            "run_stage 自愈结果必须落盘（auto_unlock_count=1）——否则每 tick "
            "重复解锁，「终生至多一次」守卫失效（BUG-19 核心断言）",
        )
        self.assert_eq(
            disk_f.get("repair_attempts"), 0,
            "解锁后 repair_attempts 必须归零并落盘",
        )
        self.assert_eq(
            disk_f.get("status"), "pending",
            "解锁后 status 应为 pending 并落盘",
        )

        # 第二次 tick：磁盘已记录 auto_unlock_count=1 → 不应再解锁
        pipe2 = WeekendPipeline(state_path=state_path)
        pipe2.run_stage("reflection")
        disk2 = json.loads(state_path.read_text(encoding="utf-8"))
        disk_f2 = next(j for j in disk2["jobs"] if j["job_id"] == "reflection_kb_merge_duplicates")
        self.assert_eq(
            disk_f2.get("auto_unlock_count"), 1,
            "已解锁过的 job 不得被重复解锁（守卫须真正生效）",
        )

    def _test_run_stage_and_run_next_heal_consistent(self):
        """v7.2.52（BUG-19）：run_stage 与 run_next 的自愈落盘结果必须一致。

        10-27 16h 健康检查实测：同一份 state，run_next 落盘成功
        （auto_unlock_count=1），run_stage 落盘为空（auto_unlock_count=None）
        ——两条路径两种结果。本用例锁定该一致性。
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        def _unlock_and_status():
            disk = json.loads(state_path.read_text(encoding="utf-8"))
            j = next(x for x in disk["jobs"] if x["job_id"] == "reflection_kb_merge_duplicates")
            return j.get("auto_unlock_count"), j.get("status")

        self._write_bug19_state(state_path)
        WeekendPipeline(state_path=state_path).run_stage("reflection")
        stage_count, stage_status = _unlock_and_status()

        self._write_bug19_state(state_path)
        WeekendPipeline(state_path=state_path).run_next(stage="reflection")
        next_count, next_status = _unlock_and_status()

        self.assert_eq(
            stage_count, next_count,
            f"run_stage 与 run_next 的自愈落盘结果必须一致"
            f"（run_stage={stage_count} / run_next={next_count}）",
        )
        self.assert_eq(
            stage_status, next_status,
            f"两条路径的自愈后 status 必须一致"
            f"（run_stage={stage_status} / run_next={next_status}）",
        )

    def _write_bug19_state(self, state_path):
        """写入 BUG-19 触发形状的 state（三节点链，见用例 docstring）。"""
        now = datetime.now(timezone.utc)
        # G：failed + auto_unlock_count=1 → 终生不可解锁（依赖链上游永久卡死）
        job_g = self._failed_job(
            job_id="reflection_kb_deep_health",
            step="kb_deep_health",
            depends_on=[],
            auto_unlock_count=1,
            finished_at=_iso(now - timedelta(hours=30)),
        )
        # F：failed + repair_attempts=3 + 失败超 24h → 本轮被自动解锁
        job_f = self._failed_job(
            job_id="reflection_kb_merge_duplicates",
            step="kb_merge_duplicates",
            depends_on=["reflection_kb_deep_health"],
            auto_unlock_count=0,
            finished_at=_iso(now - timedelta(hours=30)),
        )
        # P：pending，依赖 F → F 未 done 前不可执行
        job_p = {
            "job_id": "reflection_proposal_calibration",
            "stage": "reflection",
            "step": "proposal_calibration",
            "status": "pending",
            "attempts": 0,
            "repair_attempts": 0,
            "auto_unlock_count": 0,
            "started_at": "",
            "finished_at": "",
            "last_error": "",
            "depends_on": ["reflection_kb_merge_duplicates"],
        }
        state_path.write_text(
            json.dumps(
                {
                    "jobs": [job_g, job_f, job_p],
                    "stage_status": {"reflection": "failed"},
                    "processed_sources": {},
                    "input_round": {},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def _test_production_deadlock_shape_unblocked(self):
        """生产实测形状复现：BUG-10 失败态（repair_attempts=3/3）应被解锁。

        生产 state：reflection_kb_merge_duplicates 在 10-25 02:20 失败，
        repair_attempts 已打满 3/3，下游四 job 全 pending。
        """
        from weekend_pipeline.executor import repair_stale_and_failed, pick_next_job

        now = datetime.now(timezone.utc)
        dep = self._failed_job(finished_at=_iso(now - timedelta(hours=26)))
        chain = []
        prev = "reflection_kb_merge_duplicates"
        for jid, step in [
            ("reflection_proposal_calibration", "proposal_calibration"),
            ("reflection_link_deep_review", "link_deep_review"),
            ("reflection_kb_taxonomy_apply", "kb_taxonomy_apply"),
            ("reflection_panel_plan", "panel_plan"),
        ]:
            chain.append({
                "job_id": jid, "stage": "reflection", "step": step,
                "status": "pending", "attempts": 0, "repair_attempts": None,
                "depends_on": [prev],
            })
            prev = jid
        state = self._state_with([dep] + chain)

        repaired = repair_stale_and_failed(state)
        self.assert_eq(len(repaired), 1, "生产形状下应解锁 1 个 job")
        self.assert_eq(dep["status"], "pending", "失败 job 应被解锁")

        job = pick_next_job(state, stage="reflection")
        self.assert_true(job is not None, "解锁后应能挑出 job")
        self.assert_eq(job["job_id"], "reflection_kb_merge_duplicates", "先挑被解锁的 job")

    # ------------------------------------------------------------------

    def _test_run_stage_persists_cross_stage_heal(self):
        """v7.2.53（BUG-20）：run_stage 必须落盘**跨阶段**的自愈结果。

        10-27 20h 健康检查实测：v7.2.52 的指纹按 stage 收窄，但
        `pick_next_job(state, stage)` 的两条自愈路径都会改写 stage
        之外的 job：
          ① stale running 扫描**不看 stage**（executor.py:206-213）
          ② `_resolve_blocking_deps` 的 stage 过滤只作用于 pending 的
             **宿主 job**，它修复的是该宿主的 depends_on 依赖——
             依赖可以属于别的阶段

        v7.2.52 指纹漏检跨阶段自愈 → 结果不落盘 → 每 tick 重复自愈
        → 僵死 job 磁盘上 attempts 永不增长 → 永久死锁。

        触发形状：input 阶段一个 2h 未结束的 running job（僵死），
        run_stage 跑的是 reflection 阶段。
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        def _write():
            now = datetime.now(timezone.utc)
            stale = {
                "job_id": "input_cluster_distill", "stage": "input",
                "step": "cluster_distill", "status": "running",
                "attempts": 1, "repair_attempts": 0, "auto_unlock_count": 0,
                "started_at": _iso(now - timedelta(hours=2)),
                "finished_at": "", "last_error": "", "depends_on": [],
            }
            state_path.write_text(
                json.dumps(
                    {
                        "jobs": [stale],
                        "stage_status": {"input": "running", "reflection": "pending"},
                        "processed_sources": {},
                        "input_round": {},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

        _write()
        WeekendPipeline(state_path=state_path).run_stage("reflection")

        disk = json.loads(state_path.read_text(encoding="utf-8"))
        stale_disk = next(j for j in disk["jobs"] if j["job_id"] == "input_cluster_distill")
        self.assert_eq(
            stale_disk.get("status"), "failed",
            "跨阶段僵死 job 的 stale→failed 转换必须落盘——否则磁盘上 "
            "attempts 永不增长，pick_next_job 每 tick 看到它仍是 running → "
            "整条链永久阻塞（BUG-20 核心断言）",
        )
        self.assert_eq(
            stale_disk.get("attempts"), 2,
            "跨阶段僵死 job 的 attempts 必须在磁盘上增长（1→2）",
        )

    def _test_run_stage_cross_stage_heal_not_repeated(self):
        """v7.2.53（BUG-20）：跨阶段自愈落盘后不得被重复执行。

        修复前：自愈结果不落盘 → 每 tick 重复解锁同一 job →
        「终生至多解锁一次」守卫（auto_unlock_count）形同虚设。
        """
        from weekend_pipeline.pipeline import WeekendPipeline

        state_path = self.tmp_root / "memory" / "weekend-pipeline.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)

        # 跨阶段依赖：reflection 的 pending job 依赖 input 阶段的 failed job
        failed_dep = self._failed_job(
            job_id="input_cluster_distill",
            stage="input",
            step="cluster_distill",
            repair_attempts=3,
            auto_unlock_count=0,
            finished_at=_iso(now - timedelta(hours=30)),
        )
        pending_host = {
            "job_id": "reflection_kb_deep_health", "stage": "reflection",
            "step": "kb_deep_health", "status": "pending", "attempts": 0,
            "repair_attempts": 0, "auto_unlock_count": 0,
            "started_at": "", "finished_at": "", "last_error": "",
            "depends_on": ["input_cluster_distill"],
        }
        state_path.write_text(
            json.dumps(
                {
                    "jobs": [failed_dep, pending_host],
                    "stage_status": {"input": "failed", "reflection": "pending"},
                    "processed_sources": {},
                    "input_round": {},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        pipe = WeekendPipeline(state_path=state_path)
        pipe.run_stage("reflection")
        disk = json.loads(state_path.read_text(encoding="utf-8"))
        dep_disk = next(j for j in disk["jobs"] if j["job_id"] == "input_cluster_distill")
        self.assert_eq(
            dep_disk.get("auto_unlock_count"), 1,
            "跨阶段依赖的自动解锁必须落盘（auto_unlock_count=1）",
        )
        self.assert_eq(
            dep_disk.get("repair_attempts"), 0,
            "跨阶段依赖解锁后 repair_attempts 必须归零并落盘",
        )

        # 第二次 tick：磁盘已记录 auto_unlock_count=1 → 不得再解锁
        WeekendPipeline(state_path=state_path).run_stage("reflection")
        disk2 = json.loads(state_path.read_text(encoding="utf-8"))
        dep_disk2 = next(j for j in disk2["jobs"] if j["job_id"] == "input_cluster_distill")
        self.assert_eq(
            dep_disk2.get("auto_unlock_count"), 1,
            "已解锁过的 job 不得被重复解锁（跨阶段路径同样须守卫生效）",
        )

    def run_tests(self):
        # 独立运行（__main__）时 test_runner 不调 setup，此处自建隔离环境
        if self.tmp_root is None:
            self.setup()
            self._owns_tmp = True
        try:
            self._test_should_auto_unlock_scenarios()
            self._test_auto_unlock_resets_repair_attempts()
            self._test_repair_auto_unlocks_exhausted_job()
            self._test_repair_does_not_unlock_within_cooldown()
            self._test_resolve_blocking_deps_auto_unlocks()
            self._test_pick_next_job_unblocks_after_auto_unlock()
            self._test_cross_week_reset_clears_repair_attempts()
            self._test_run_next_persists_repair_when_no_job_runnable()
            self._test_run_stage_persists_heal_when_no_job_runnable()
            self._test_run_stage_and_run_next_heal_consistent()
            self._test_run_stage_persists_cross_stage_heal()
            self._test_run_stage_cross_stage_heal_not_repeated()
            self._test_production_deadlock_shape_unblocked()
        finally:
            if getattr(self, "_owns_tmp", False):
                self.teardown()
                self.tmp_root = None
                self._owns_tmp = False


if __name__ == "__main__":
    import unittest  # noqa: E402

    class _Runner(unittest.TestCase):
        def runTest(self):
            WeekendPipelineDeadlockTests().run_tests()

    unittest.main(argv=[__file__, "-v"], exit=False)
