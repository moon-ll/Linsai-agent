#!/usr/bin/env python3
"""WeekendPipeline 主类。"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from datetime import datetime, timezone

from common import file_lock, now_utc, save_json
from paths import PROJECT_ROOT
from proposal_lifecycle import ProposalLifecycle

from .constants import (
    JOB_STATUS_DONE,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    PIPELINE_STATE_PATH,
    STAGE_INPUT,
    STAGE_OUTPUT,
    STAGE_REFLECTION,
    STAGES,
    STEP_ANALYZE,
    STEP_CLUSTER_ASSIGN,
    STEP_CLUSTER_DISTILL,
    STEP_COLLECT,
    STEP_COMPOSE,
    STEP_DEEP_READ,
    STEP_EXTRACT,
    STEP_HEALTH,
    STEP_KB_DEEP_HEALTH,
    STEP_KB_MERGE,
    STEP_RECOMMEND,
    STEP_REPORT,
    STEP_RETRIEVE,
    STEP_SELECT,
    STEP_SUMMARIZE,
    STEP_SYNC,
    STEP_TOPIC_MATCH,
    STEP_WEEKLY_REPORT,
)
from .executor import execute_job, pick_next_job, repair_stale_and_failed
from .jobs import stage_job_templates
from .state import (
    ensure_pipeline_state,
    find_job,
    find_jobs_by_stage,
    get_stage_status,
    load_pipeline_state,
    save_pipeline_state,
    set_stage_status,
    trim_processed_sources,
    update_job,
)

# job 执行器注册
from . import input_jobs, output_jobs, reflection_jobs

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


class WeekendPipeline:
    """周末任务流水线：将 input/output/reflection 拆分为小 checkpoint job。"""

    def __init__(self, state_path: Optional[Any] = None) -> None:
        self.state_path = state_path
        self.state = load_pipeline_state(state_path)
        self.handlers: Dict[tuple, Callable[[Dict[str, Any], Dict[str, Any], bool], Dict[str, Any]]] = {}
        self._register_handlers()

    def _save(self) -> None:
        save_pipeline_state(self.state, self.state_path)

    def _save_unlocked(self) -> None:
        """在已持有 weekend-pipeline 锁的上下文中使用，避免嵌套锁死锁。"""
        path = self.state_path or PIPELINE_STATE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        self.state["updated_at"] = now_utc()
        save_json(path, self.state)

    def _register_handlers(self) -> None:
        """注册 job 执行器（v6.9.7: key 统一为 (stage, step) 二元组）。

        旧版混用 job_id 与 step 两种 key，靠 execute_job 的回退逻辑
        兜底，存在同名 step 静默错绑风险（旧代码注释曾自认冲突）。
        二元组天然隔离三个阶段；同阶段同 step 需要多个 handler 时，
        必须拆分为不同 step 常量（reflection 阶段的 kb_deep_health
        与 kb_merge 即此例）。
        """
        self.handlers = {
            # input
            (STAGE_INPUT, STEP_COLLECT): input_jobs.run_input_collect,
            (STAGE_INPUT, STEP_SUMMARIZE): input_jobs.run_input_summarize,
            # v6.9.12: 知识簇链路取代 gap/select/retrieve/deep_read
            (STAGE_INPUT, STEP_CLUSTER_ASSIGN): input_jobs.run_input_cluster_assign,
            (STAGE_INPUT, STEP_CLUSTER_DISTILL): input_jobs.run_input_cluster_distill,
            (STAGE_INPUT, STEP_TOPIC_MATCH): input_jobs.run_input_topic_match,
            (STAGE_INPUT, STEP_COMPOSE): input_jobs.run_input_compose,
            # output：extract 一步两义（归档课题萃取 / 日常知识萃取），
            # 统一入口 run_output_extract 内部按 job_id 分派
            (STAGE_OUTPUT, STEP_SYNC): output_jobs.run_output_sync_proposals,
            (STAGE_OUTPUT, STEP_EXTRACT): output_jobs.run_output_extract,
            (STAGE_OUTPUT, STEP_HEALTH): output_jobs.run_output_kb_health,
            (STAGE_OUTPUT, STEP_WEEKLY_REPORT): output_jobs.run_output_generate_weekly_report,
            (STAGE_OUTPUT, STEP_COLLECT): output_jobs.run_output_collect_daily_sources,
            # reflection
            (STAGE_REFLECTION, STEP_HEALTH): reflection_jobs.run_reflection_health_check,
            (STAGE_REFLECTION, STEP_KB_DEEP_HEALTH): reflection_jobs.run_reflection_kb_deep_health,
            (STAGE_REFLECTION, STEP_KB_MERGE): reflection_jobs.run_reflection_kb_merge_duplicates,
            (STAGE_REFLECTION, STEP_COLLECT): reflection_jobs.run_reflection_collect_state,
            (STAGE_REFLECTION, STEP_ANALYZE): reflection_jobs.run_reflection_analyze_patterns,
            (STAGE_REFLECTION, STEP_REPORT): reflection_jobs.run_reflection_report,
            (STAGE_REFLECTION, STEP_RECOMMEND): reflection_jobs.run_reflection_recommend,
        }

    def _reset_stage_for_new_week(self, stage: str) -> int:
        """检查是否跨周，若是则重置该阶段所有 job 为 pending。

        当该阶段自身最近一次 job 完成距今超过 6 天时，视为新一周开始，
        将该阶段所有 job 重置为 pending，清除执行记录。

        v6.8.53: 跨周判定基准从全局 state.updated_at 改为"该阶段自身
        最近一次 job 完成时间"。旧实现读全局 updated_at——周六同一优先
        级下 output/reflection（或 weekend-worker 每 20 分钟）先跑会刷新
        它，导致 input 阶段的跨周重置永不触发：input job 自 08-01 全部
        done 后，08-08 weekend_input 变成 no-op 却标记成功，研究设想
        发现停摆两周无人察觉（运行时已证实）。

        Returns: 重置的 job 数量
        """
        stage_jobs = [j for j in self.state.get("jobs", []) if j.get("stage") == stage]
        if not stage_jobs:
            return 0
        finished_times = [
            j.get("finished_at", "") for j in stage_jobs
            if j.get("finished_at")
        ]
        if not finished_times:
            # 该阶段从未有 job 完成过：job 本就是 pending，无需重置
            return 0

        try:
            last_fin = max(finished_times)
            last_dt = datetime.fromisoformat(last_fin.replace("Z", "+00:00"))
            delta_days = (datetime.now(timezone.utc) - last_dt).days
            if delta_days < 6:
                return 0
        except Exception:
            return 0

        if _log:
            _log.info(
                f"[weekend-pipeline] 检测到跨周（上次更新距今 {delta_days} 天），"
                f"重置 {stage} 阶段 job"
            )

        reset_count = 0
        for job in self.state.get("jobs", []):
            if job.get("stage") == stage:
                job["status"] = JOB_STATUS_PENDING
                job["started_at"] = ""
                job["finished_at"] = ""
                job["last_error"] = ""
                job["attempts"] = 0
                if "result" in job:
                    del job["result"]
                reset_count += 1

        if reset_count > 0:
            # 注意：调用方 sync_stage_jobs 已持有 weekend-pipeline 锁，
            # 此处必须用 _save_unlocked（嵌套同名 flock 会自死锁）
            self._save_unlocked()

        return reset_count

    def _build_reverse_deps(self) -> Dict[str, List[str]]:
        """构建反向依赖图：job_id → 依赖它的下游 job_id 列表。"""
        reverse: Dict[str, List[str]] = {}
        for j in self.state.get("jobs", []):
            for dep in j.get("depends_on", []):
                reverse.setdefault(dep, []).append(j["job_id"])
        return reverse

    def _verify_artifacts(self, stage: str) -> int:
        """检查已完成 job 的声明产物是否存在，缺失则级联重置为 pending。

        v6.9.7: 从 output 阶段专用硬编码 map 通用化为读取 job 自身
        声明的 artifact 字段（见 jobs._base_job），三阶段统一生效。
        {date} 占位符以该 job 自身 finished_at 日期格式化——晚于执行
        日检查时不会因日期错位误判（旧实现取检查当日，晚一天跑 cron
        就会误重置）。无确定性产物的 job（如萃取写动态 wiki 页）不
        声明 artifact，自然跳过。

        Returns: 重置的 job 数量
        """
        to_reset: set = set()
        for job in self.state.get("jobs", []):
            if job.get("stage") != stage:
                continue
            if job.get("status") != JOB_STATUS_DONE:
                continue
            pattern = job.get("artifact", "")
            if not pattern:
                continue
            jid = job.get("job_id", "")
            date_str = (job.get("finished_at", "") or now_utc())[:10]
            try:
                artifact_path = PROJECT_ROOT / pattern.format(date=date_str)
            except (KeyError, IndexError, ValueError):
                continue
            if not artifact_path.exists():
                to_reset.add(jid)
                if _log:
                    _log.warning(
                        f"[weekend-pipeline] 产物缺失: {jid} "
                        f"({artifact_path.name})，重置为 pending"
                    )

        # 级联重置：下游依赖也需重置，避免用旧数据生成
        if to_reset:
            reverse = self._build_reverse_deps()
            cascade = list(to_reset)
            visited = set(to_reset)  # v6.9.7: 防同一下游被多条路径重复遍历
            while cascade:
                jid = cascade.pop(0)
                for downstream in reverse.get(jid, []):
                    if downstream in visited:
                        continue
                    downstream_job = find_job(self.state, downstream)
                    if downstream_job and downstream_job.get("status") == JOB_STATUS_DONE:
                        visited.add(downstream)
                        to_reset.add(downstream)
                        cascade.append(downstream)
                        if _log:
                            _log.info(
                                f"[weekend-pipeline] 级联重置: {downstream} (依赖 {jid})"
                            )

        # 执行重置
        reset_count = 0
        for jid in to_reset:
            job = find_job(self.state, jid)
            if not job:
                continue
            job["status"] = JOB_STATUS_PENDING
            job["started_at"] = ""
            job["finished_at"] = ""
            job["last_error"] = ""
            job["attempts"] = 0
            if "result" in job:
                del job["result"]
            reset_count += 1

        if reset_count > 0:
            # 同 _reset_stage_for_new_week：调用方持锁，禁嵌套锁
            self._save_unlocked()

        return reset_count

    def sync_stage_jobs(self, stage: str) -> Dict[str, Any]:
        """幂等地为指定阶段创建任务。

        自动检测跨周：若该阶段上次完成距今超过 6 天，
        先将该阶段所有 job 重置为 pending 再创建新任务。

        v6.9.7 三项增强：
        1. 字段级合并：模板新增的声明性字段（如 artifact）会补齐到
           已存在的 job 上，旧 state 无需迁移即可获得产物校验能力。
        2. 产物检测三阶段通用（声明式 artifact，见 _verify_artifacts）。
        3. processed_sources 滚动裁剪（保留 4 周，防止只增不减膨胀）。

        v6.9.13: 全程持 weekend-pipeline 锁 + 锁内重载状态。旧版只在
        落盘时经 save_pipeline_state 抢锁，但读状态用的是进程启动时的
        快照——与 20 分钟 worker 并发时会用 stale 快照覆盖 worker 刚
        写入的 job 终态（08-15 实测：sync 覆盖 summarize done → 整个
        job 重跑一遍 LLM）。子例程的保存改走 _save_unlocked（嵌套同名
        flock 会自死锁）。
        """
        if stage not in STAGES:
            raise ValueError(f"未知阶段: {stage}")

        with file_lock("weekend-pipeline"):
            self.state = load_pipeline_state(self.state_path)

            # 跨周检测：重置已完成 job，避免新一周无任务可执行
            self._reset_stage_for_new_week(stage)

            archived_ids: List[str] = []
            if stage == STAGE_OUTPUT:
                try:
                    archived_ids = [p["proposal_id"] for p in ProposalLifecycle().list_by_status("archived")]
                except Exception as e:
                    if _log:
                        _log.warning(f"获取 archived proposals 失败: {e}")

            templates = stage_job_templates(stage, archived_proposal_ids=archived_ids)
            added = []
            for t in templates:
                existing = find_job(self.state, t["job_id"])
                if existing is None:
                    self.state.setdefault("jobs", []).append(t)
                    added.append(t["job_id"])
                else:
                    # 字段级合并：补齐模板新增的声明性字段（artifact），
                    # 不覆盖任何运行时状态（status/attempts/finished_at 等）
                    for key in ("artifact",):
                        if t.get(key) and not existing.get(key):
                            existing[key] = t[key]
                    # v6.9.13: 依赖图随模板刷新。depends_on 是结构字段而非
                    # 运行时状态——v6.9.12 链路重构后旧 state 里 compose 仍
                    # 指向已废弃的 input_deep_read，而 dependencies_satisfied
                    # 要求依赖位于 done 集合，废弃 job 已被清理永远无法满足
                    # → compose 永久死锁、input 阶段永无终态（08-15 实测）。
                    if existing.get("depends_on") != t.get("depends_on"):
                        if _log:
                            _log.info(
                                f"[weekend-pipeline] 依赖刷新: {t['job_id']} "
                                f"{existing.get('depends_on')} -> {t.get('depends_on')}"
                            )
                        existing["depends_on"] = list(t.get("depends_on", []))

            # v6.9.12: 清理废弃 job 的 state 残留（模板已删除但 state 里
            # 还挂着的旧 job——不清理会永远 done/pending 挂在列表里，
            # 且旧 step 的 done 状态会污染阶段终态汇总）
            if stage == STAGE_INPUT:
                from .jobs import DEPRECATED_INPUT_JOBS
                before = len(self.state.get("jobs", []))
                self.state["jobs"] = [
                    j for j in self.state.get("jobs", [])
                    if not (j.get("stage") == STAGE_INPUT and j.get("job_id") in DEPRECATED_INPUT_JOBS)
                ]
                removed = before - len(self.state["jobs"])
                if removed and _log:
                    _log.info(f"input 阶段清理废弃 job {removed} 个（v6.9.12 知识簇链路取代）")

            # 产物检测：声明了 artifact 的 done job 若产物缺失则级联重置
            self._verify_artifacts(stage)

            # v6.9.7: processed_sources 滚动裁剪（与 error_history 策略对齐）
            trimmed = trim_processed_sources(self.state)

            set_stage_status(self.state, stage, JOB_STATUS_PENDING)
            self._save_unlocked()
            return {
                "success": True,
                "stage": stage,
                "added": len(added),
                "jobs": added,
                "trimmed_sources": trimmed,
            }

    def _finalize_stage_status(self, stage: str) -> None:
        """阶段终态汇总（run_stage/run_next 共用）。

        v6.9.10: run_next 逐 job 推进时同样需要汇总——旧版只有 run_stage
        做终态判定，worker cron 用 run_next 推完整阶段后 stage_status
        永远停在 pending（控制台显示阶段未完成，实际 job 已全 done）。
        """
        stage_jobs = find_jobs_by_stage(self.state, stage)
        if stage_jobs and all(j.get("status") == JOB_STATUS_DONE for j in stage_jobs):
            set_stage_status(self.state, stage, JOB_STATUS_DONE)
        elif any(j.get("status") == JOB_STATUS_FAILED for j in stage_jobs):
            set_stage_status(self.state, stage, JOB_STATUS_FAILED)
        else:
            set_stage_status(self.state, stage, JOB_STATUS_PENDING)

    def run_next(self, stage: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """执行下一个 pending 且依赖满足的任务。

        v6.9.7 两项加固：
        1. 非阻塞抢锁：锁被 run_stage 或其它 worker 持有时温和退出
           （skipped=lock_busy）。旧版阻塞等锁，run_stage 持锁可达
           数小时，worker cron 每 20 分钟 spawn 的进程全部堆积在
           flock 上；现在单 job 执行期间（分钟级）到达的 worker 才
           会等待，其余立即退出留给下一 tick。
        2. dry-run 零落盘：预览模式不持久化状态。旧版 dry-run 会把
           假 done 写入状态文件（output 曾因此需要 _verify_artifacts
           自愈，input/reflection 连自愈都没有），现在预览不留痕。

        v6.9.10: job 执行后补阶段终态汇总（见 _finalize_stage_status）。
        """
        try:
            with file_lock("weekend-pipeline", blocking=False):
                self.state = load_pipeline_state(self.state_path)
                job = pick_next_job(self.state, stage=stage)
                if not job:
                    return {"success": True, "message": "没有可执行任务", "executed": 0}

                result = execute_job(self.state, job, self.handlers, dry_run=dry_run)
                if not dry_run:
                    self._finalize_stage_status(job["stage"])
                    self._save_unlocked()
                return {
                    "success": result.get("success"),
                    "job_id": job["job_id"],
                    "result": result,
                    "executed": 1,
                }
        except TimeoutError:
            return {
                "success": True,
                "message": "锁忙（run_stage/其它 worker 持有中），本轮跳过",
                "executed": 0,
                "skipped": "lock_busy",
            }

    def run_stage(self, stage: str, dry_run: bool = False) -> Dict[str, Any]:
        """顺序执行阶段内所有 pending 任务。

        v6.9.7: 锁粒度从"整阶段一次持锁"细化为"每 job 一持一放"。
        旧版在 file_lock 内跑完整阶段，LLM 慢时段（单 job 6-10 分钟）
        持锁可达数小时，期间所有 worker 进程阻塞排队。细化后每两个
        job 之间释放锁，worker 可在间隙抢锁协作推进（pick_next_job
        在锁内 reload 状态，不会重复执行同一 job）。

        dry-run 同样零落盘（语义见 run_next）。
        """
        if stage not in STAGES:
            raise ValueError(f"未知阶段: {stage}")

        results: List[Dict[str, Any]] = []
        count = 0
        while True:
            with file_lock("weekend-pipeline"):
                # dry-run 零落盘：磁盘状态不会推进，若每轮 reload 将无限
                # 重复 pick 同一个 pending job。故 dry-run 仅首轮 reload，
                # 后续轮复用内存状态（前序 job 已在内存标 done）。
                # 非 dry-run 每轮 reload，保证与其它进程（worker）协作推进。
                if not dry_run or count == 0:
                    self.state = load_pipeline_state(self.state_path)
                job = pick_next_job(self.state, stage=stage)
                if not job:
                    break
                if count == 0 and not dry_run:
                    set_stage_status(self.state, stage, JOB_STATUS_RUNNING)
                    self._save_unlocked()
                result = execute_job(self.state, job, self.handlers, dry_run=dry_run)
                if not dry_run:
                    self._save_unlocked()
            results.append(result)
            count += 1
            if not result.get("success"):
                # 失败即停该阶段，等待 repair 重试（保持旧语义）
                break

        # 汇总阶段状态（终态判定）
        with file_lock("weekend-pipeline"):
            self.state = load_pipeline_state(self.state_path)
            self._finalize_stage_status(stage)
            if not dry_run:
                self._save_unlocked()

        return {
            "success": True,
            "stage": stage,
            "dry_run": dry_run,
            "executed": count,
            "results": results,
        }

    def list_jobs(self, stage: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出任务。"""
        jobs = self.state.get("jobs", [])
        if stage:
            jobs = [j for j in jobs if j.get("stage") == stage]
        return jobs

    def repair(self) -> Dict[str, Any]:
        """修复 stale/failed 任务。"""
        repaired = repair_stale_and_failed(self.state)
        self._save()
        return {"success": True, "repaired": repaired, "at": now_utc()}

    def ensure_all_stages(self) -> Dict[str, Any]:
        """确保三个阶段任务都存在。"""
        results = {}
        for s in STAGES:
            results[s] = self.sync_stage_jobs(s)
        return results


def get_pipeline(state_path: Optional[Any] = None) -> WeekendPipeline:
    return WeekendPipeline(state_path=state_path)
