#!/usr/bin/env python3
"""WeekendPipeline 主类。"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from datetime import datetime, timedelta, timezone

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
    STEP_DEEP_DIGEST,
    STEP_EXTRACT,
    STEP_HEALTH,
    STEP_KB_DEEP_HEALTH,
    STEP_KB_MERGE,
    STEP_KB_TAXONOMY_APPLY,
    STEP_LINK_DEEP_REVIEW,
    STEP_METHODS_SETTLE,
    STEP_PANEL_PLAN,
    STEP_PROPOSAL_CALIBRATION,
    STEP_RECOMMEND,
    STEP_REPORT,
    STEP_RETRIEVE,
    STEP_SELECT,
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
from . import maintenance_jobs  # v6.9.99（T2）：反思链尾维护链三连
from . import methods_jobs  # v6.10.0（T3）：方法学专题沉淀

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
            # v6.9.98: deep_digest 结构化深读取代 summarize 浅摘要
            #（多轮化：每轮 10 篇，轮次接力见 rounds.py）
            (STAGE_INPUT, STEP_DEEP_DIGEST): input_jobs.run_input_deep_digest,
            # v6.9.12: 知识簇链路取代 gap/select/retrieve/deep_read
            (STAGE_INPUT, STEP_CLUSTER_ASSIGN): input_jobs.run_input_cluster_assign,
            (STAGE_INPUT, STEP_CLUSTER_DISTILL): input_jobs.run_input_cluster_distill,
            # v6.10.0（T3）：方法线索沉淀进方法页（词表归组 + 按需回原文）
            (STAGE_INPUT, STEP_METHODS_SETTLE): methods_jobs.run_input_methods_settle,
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
            # v6.9.99（T2）周末维护链：calibration → deep_review → taxonomy_apply
            (STAGE_REFLECTION, STEP_PROPOSAL_CALIBRATION): maintenance_jobs.run_reflection_proposal_calibration,
            (STAGE_REFLECTION, STEP_LINK_DEEP_REVIEW): maintenance_jobs.run_reflection_link_deep_review,
            (STAGE_REFLECTION, STEP_KB_TAXONOMY_APPLY): maintenance_jobs.run_reflection_kb_taxonomy_apply,
            # v6.10.15: 评审团执行计划（panel_request 队列盘点，零 LLM）
            (STAGE_REFLECTION, STEP_PANEL_PLAN): reflection_jobs.run_reflection_panel_plan,
        }

    def _reset_stage_for_new_week(self, stage: str) -> int:
        """检查是否跨周，若是则重置该阶段跨周的 job 为 pending。

        跨周锚点：最近过去的周六 00:00（本地时间）。**逐 job 判定**——
        仅当某个 job 自身 finished_at 早于锚点（或从未完成）才重置它；
        本周末内完成过的 job 保持原状。

        v6.8.53: 跨周判定基准从全局 state.updated_at 改为"该阶段自身
        最近一次 job 完成时间"。旧实现读全局 updated_at——周六同一优先
        级下 output/reflection（或 weekend-worker 每 20 分钟）先跑会刷新
        它，导致 input 阶段的跨周重置永不触发：input job 自 08-01 全部
        done 后，08-08 weekend_input 变成 no-op 却标记成功，研究设想
        发现停摆两周无人察觉（运行时已证实）。

        v6.9.38: 滚动 144h 时差改为自然周锚点。旧实现
        delta_days = (now - last_fin).days < 6——上周完成时刻晚于本周
        入口 cron 时刻时（如 08-16 11:51 完成 vs 08-22 09:00 入口，
        时差 5 天 21 小时），入口 cron 必然差不满 6 天而 no-op 且标记
        成功，只能等 6h repair 的超期补跑兜底（08-22 实测空转 3 小时）。
        新口径与 lifecycle.orchestrator._weekend_catchup_decisions 的
        锚点一致：last_fin 早于本周六 00:00 即跨周，入口 cron 即时生效。

        v7.2.107（BUG-36）: 阶段级 max(finished_at) 口径改为 per-job 口径。
        旧实现只要阶段内**任意一个** job 在本周末内完成过就判「未跨周」，
        阶段内其余 job 全部保持 done → 阶段静默 no-op。生产实测
        reflection 阶段 11 个 job 分两批（5 个主链停在 10-25，6 个维护链
        10-30 手工重跑），max 值越过锚点 → 11-01 反思入口 cron 触发却
        主链从未重跑 → KB 健康评分永久停在 2026-10-25T01:00:25Z。
        per-job 口径下「部分重跑」不再遮蔽其余 job 的跨周重置。

        Returns: 重置的 job 数量
        """
        stage_jobs = [j for j in self.state.get("jobs", []) if j.get("stage") == stage]
        if not stage_jobs:
            return 0

        try:
            # 本周末锚点：最近过去的周六 00:00（本地时间）。
            local_now = datetime.now().astimezone()
            days_since_sat = (local_now.weekday() - 5) % 7
            anchor = (local_now - timedelta(days=days_since_sat)).replace(
                hour=0, minute=0, second=0, microsecond=0)
        except Exception:
            return 0

        # v7.2.107（BUG-36）跨周判定改为 **per-job 口径**。
        #
        # 旧实现取阶段内全部 job 的 max(finished_at) 作为唯一锚点比较：
        # 只要有**任意一个** job 在本周末内完成过，整个阶段就判为
        # 「未跨周」→ 所有 job 保持 done → 阶段静默 no-op。
        #
        # 生产实测（2026-11-02 16h 健康检查 v75 轮）：
        #   reflection 阶段 11 个 job 的 finished_at 分两批——
        #     · 5 个主链 job（health_check / collect_state / analyze_patterns
        #       / generate_report / recommend_actions）停留在 10-25 01:00Z
        #     · 6 个维护链 job（kb_deep_health / kb_merge_duplicates /
        #       proposal_calibration / link_deep_review / kb_taxonomy_apply
        #       / panel_plan）在 10-30 16:21~18:00 被手工重跑
        #   max(finished_at) = 2026-10-30T18:00:14Z → 本地 10-31 02:00:14
        #   → ≥ 锚点 2026-10-31 00:00（+08:00）→ 判定「未跨周」
        #   → 11-01 09:00 的 reflection 入口 cron（lc-weekend-weekend-reflection）
        #     触发 ok 但主链 5 个 job 从未重跑
        #   → 唯一写 health_updated_at 的 job（reflection_recommend_actions）
        #     再未执行 → KB 健康评分永久停在 2026-10-25T01:00:25Z
        #   → 阶段级「部分重跑」污染了整阶段的跨周判定，属数据流转异常。
        #
        # 修复分两层（v7.2.107，2026-11-02 20h 健康检查 v75 轮补正）：
        #
        #   ① **阶段级真跨周判定（前置闸门）**：必须存在**可解析**且早于
        #      锚点的 finished_at，才认定「该阶段确实跨周了」。无此证据
        #      → 一律 return 0，不做任何重置。这一层保住 v6.9.38 已提交
        #      契约（test_mechanism_hardening「时间戳异常应安全返回 0」：
        #      脏时间戳 / 全阶段无完成记录 → 安全 no-op），同时避免
        #      「某 job 恰好无 finished_at」被误当成跨周。
        #
        #   ② **per-job 口径重置**：真跨周时，逐 job 判定——早于锚点的
        #      job 与无可解析完成时间的 job 一并重置；本周末内完成过
        #      的 job 保持原状。这样「部分 job 被手工重跑」不再遮蔽
        #      其余 job 的跨周重置（BUG-36 主场景）。
        #
        # ⚠ v7.2.107 首版（未提交）把「无 finished_at」直接当作跨周证据，
        #   引入两个回归，本轮已修：
        #   R1 脏时间戳 → 被保守重置 → 违反 v6.9.38 已提交契约
        #      （test_mechanism_hardening 1 条失败）；
        #   R2 repair 重试后的 pending job（finished_at 被清空）→ 被当作
        #      跨周重置 → repair_attempts 被清零 → 「修复上限」守卫失效
        #      → job 无限重试；且 input 阶段误触发 input_round 归 1
        #      （实测 round 113 → 1，last_summaries_path 被清）→ 本轮
        #      产物指针丢失、轮次计数错乱。①② 两层闸门同时堵死 R1/R2。
        to_reset_ids = set()
        stale_dates = []
        has_cross_week = False
        for job in stage_jobs:
            fin = job.get("finished_at") or ""
            if not fin:
                # 无完成记录 → 无跨周证据（repair 重试后的 pending job
                # 属此类，绝不能被当作跨周重置，否则清零 repair_attempts）
                continue
            try:
                fin_dt = datetime.fromisoformat(fin.replace("Z", "+00:00")).astimezone()
            except Exception:
                # 时间戳不可解析 → 无法判定跨周，跳过（v6.9.38 契约：
                # 脏数据不得让整阶段跨周判定失效，也不得触发重置）
                if _log:
                    _log.warning(
                        f"[weekend-pipeline] {stage} 阶段 job "
                        f"{job.get('job_id')} finished_at 不可解析（{fin!r}），"
                        f"跳过跨周判定"
                    )
                continue
            if fin_dt < anchor:
                has_cross_week = True
                to_reset_ids.add(job.get("job_id"))
                stale_dates.append(fin_dt.date())

        if not has_cross_week:
            # 阶段级闸门：无可解析的跨周证据 → 未跨周 → 不重置任何 job，
            # 也不动 input_round（修复 R2 的关键：input_round 归 1 必须
            # 以「真跨周」为前提，而非「本次重置数 > 0」）
            return 0

        # 真跨周：把「无可解析完成时间」的 job 一并纳入重置
        # （从未完成的 job 在新一周需要重跑；v7.2.46 语义：跨周重置
        #  必须一并清 repair_attempts，否则失败打满的 job 再次永久卡死）
        for job in stage_jobs:
            fin = job.get("finished_at") or ""
            if not fin:
                to_reset_ids.add(job.get("job_id"))
                continue
            try:
                datetime.fromisoformat(fin.replace("Z", "+00:00")).astimezone()
            except Exception:
                to_reset_ids.add(job.get("job_id"))

        delta_days = (
            (local_now.date() - min(stale_dates)).days if stale_dates else 0
        )

        if _log:
            _log.info(
                f"[weekend-pipeline] 检测到跨周（最早待重置 job 距今 {delta_days} 天），"
                f"重置 {stage} 阶段 {len(to_reset_ids)} 个 job"
            )

        reset_count = 0
        for job in self.state.get("jobs", []):
            if job.get("stage") == stage and job.get("job_id") in to_reset_ids:
                job["status"] = JOB_STATUS_PENDING
                job["started_at"] = ""
                job["finished_at"] = ""
                job["last_error"] = ""
                job["attempts"] = 0
                # v7.2.46：跨周重置必须一并清 repair_attempts——它原本是
                # 只增不减的单向计数器，上周失败打满 3/3 的 job 即使跨周
                # 重置为 pending，重跑失败后 repair_attempts 仍是 3 →
                # executor 的 `repair_attempts < MAX_JOB_ATTEMPTS` 守卫
                # 立即为假 → 再次永久卡死（10-26 04h 健康检查 P0-2
                # 实测：reflection_kb_merge_duplicates 10-25 失败打满
                # 3/3，跨周重置后仍带 3，周末反思链四 job 永久 pending）。
                job["repair_attempts"] = 0
                if "result" in job:
                    del job["result"]
                reset_count += 1

        if reset_count > 0 and stage == STAGE_INPUT:
            # v6.9.98: 跨周重置后输入链轮次归 1（新一周从首轮重新计数），
            # 清除上周末的轮次产物指针（last_summaries_path 指向上周文件）
            ir = self.state.setdefault("input_round", {})
            ir["round"] = 1
            ir["prev_round_finished_at"] = ""
            ir["last_summaries_path"] = ""

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
                # v6.9.98: 支持 {round} 占位符（deep_digest 产物带轮次号），
                # 按 job 自身 round 字段格式化；不含 {round} 的模板多传
                # kwarg 无害。round 缺省 1（旧 state / 首轮 job 无该字段）
                artifact_path = PROJECT_ROOT / pattern.format(
                    date=date_str, round=job.get("round", 1))
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
                    # 字段级合并：声明性字段（artifact）随模板刷新；不覆盖任何
                    # 运行时状态（status/attempts/finished_at 等）。v7.3.73:
                    # 仅"为空才补"会让模板路径修正永远进不了旧 state——错误
                    # artifact 持续存在，_verify_artifacts 每轮误判产物缺失
                    # 并级联重置 sync/extract。artifact 无运行时语义，可安全刷新。
                    for key in ("artifact",):
                        if t.get(key) and existing.get(key) != t[key]:
                            if existing.get(key) and _log:
                                _log.info(
                                    f"[weekend-pipeline] 产物声明刷新: {t['job_id']} "
                                    f"{existing.get(key)} -> {t[key]}"
                                )
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

    def _maybe_advance_input_round(self, now: Optional[Any] = None) -> Optional[int]:
        """v6.9.98 输入链轮次接力：整轮完成后按需重置开新轮。

        判定委托 rounds.should_open_next_round（纯函数，now 可注入供
        回归测试固定时钟）；通过则 rounds.reset_input_for_new_round 把
        input 阶段整体重置为 pending（round+1、attempts 保留、记录
        prev_round_finished_at）。源尽 / 冷却未满 / 周日 23:59 后 /
        非周末均不开轮（stage 保持终态 done）。

        调用方（run_next）需已持有 weekend-pipeline 锁；本方法内部用
        _save_unlocked 落盘（嵌套同名 flock 会自死锁）。

        Returns:
            新轮次号（未开轮返回 None）。
        """
        from .rounds import reset_input_for_new_round, should_open_next_round
        ok, reason = should_open_next_round(self.state, now=now)
        if not ok:
            return None
        new_round = reset_input_for_new_round(self.state)
        if _log:
            _log.info(f"[weekend-pipeline] 输入链轮次接力：开启第 {new_round} 轮（{reason}）")
        self._save_unlocked()
        return new_round

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

    def _stage_heal_fingerprint(
        self, state: Dict[str, Any], stage: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """取 job 的自愈敏感字段快照（v7.2.52 / BUG-19，v7.2.53 扩到全库）。

        `_resolve_blocking_deps` 在自愈时改写 job 的 status / attempts /
        repair_attempts / auto_unlock_count / last_error / started_at /
        finished_at，但**不返回**自愈动作。调用方（run_stage）据此判断
        「本轮是否发生了自愈」，从而决定要不要落盘。

        只取自愈相关字段（不做全量序列化）——processed_sources 等大
        字段每轮都变，会让指纹失去意义。

        v7.2.53 修正（BUG-20）：指纹范围**不能**按 stage 收窄。
        `pick_next_job(state, stage)` 的自愈动作有两条路径会改写
        **stage 之外**的 job：
          ① stale running 扫描**不看 stage**（executor.py:206-213）——
             任意阶段的僵死 job 都会被标记 failed；
          ② `_resolve_blocking_deps` 的 `stage` 过滤只作用于
             **pending 的宿主 job**，但它修复的是该宿主的
             `depends_on` 依赖——依赖可以属于别的阶段。
        v7.2.52 用「阶段内指纹」比对，跨阶段自愈被完全漏检 →
        自愈结果不落盘 → 每 tick 重复做同样的自愈 → 跨阶段僵死
        job 永久卡在 running（磁盘上 attempts 永不增长）→
        **周末管线永久死锁**（实测见 test_weekend_pipeline_deadlock
        的 _test_run_stage_persists_cross_stage_heal）。
        """
        return {
            j.get("job_id", ""): {
                "status": j.get("status"),
                "attempts": j.get("attempts"),
                "repair_attempts": j.get("repair_attempts"),
                "auto_unlock_count": j.get("auto_unlock_count"),
            }
            for j in state.get("jobs", [])
        }

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
        v6.9.98: 持锁后先做输入链轮次接力判定（weekend worker */20 tick
        的主路径）——本轮七步（v6.10.0 起含 methods_settle）全 done 且
        剩余源 ≥1 且冷却期满且周末窗口未闭合时，重置 input 阶段开新轮
        （round+1）；dry-run 零落盘语义保持，不执行接力。
        """
        try:
            with file_lock("weekend-pipeline", blocking=False):
                self.state = load_pipeline_state(self.state_path)
                opened_round = None
                repaired = None
                if not dry_run:
                    # v7.2.46（P0-3 收窄版）：worker 路径补齐**失败 job 重试**
                    # 自愈——原先只有 lc-repair（周末模式）与入口 cron 触发
                    # repair_stale_and_failed，20 分钟 worker 只挑 job 不重试，
                    # failed 的叶子 job（无下游 pending 依赖）永远不被重试。
                    # 此处只做「失败 job 重试 + 自动解锁」，**不含**
                    # _verify_artifacts / 跨周重置 / 模板同步——那三项会
                    # 在 worker 高频路径上重置 done job（实测导致
                    # test_weekend_input_rounds 回归：artifact 缺失检查把
                    # 本轮 done job 重置为 pending，开轮链路断裂）。
                    # 自愈在锁内执行，落盘走 _save_unlocked（禁嵌套 flock）。
                    repaired = repair_stale_and_failed(self.state)
                    opened_round = self._maybe_advance_input_round()
                job = pick_next_job(self.state, stage=stage)
                if not job:
                    # v7.2.47：本轮自愈（repair_stale_and_failed）可能已把
                    # failed job 重置为 pending / 自动解锁，但若解锁后的 job
                    # 依赖仍不满足（如上游同样 failed 且未解锁），pick_next_job
                    # 返回 None → 此处提前 return **不落盘** → 自愈结果全部
                    # 丢失。后果（10-26 08h 健康检查 BUG-11 实测）：每个 tick
                    # 重复做同样的解锁动作，auto_unlock_count 永远回到 None，
                    # 「终生至多解锁一次」的守卫失效，repair_attempts 也永不
                    # 落盘 → 计数恒不增长 → auto-unlock 逃生阀永不触发 →
                    # 死锁修复形同虚设。必须在提前 return 前落盘自愈结果。
                    if repaired:
                        self._save_unlocked()
                    result = {"success": True, "message": "没有可执行任务", "executed": 0}
                    if opened_round is not None:
                        result["opened_input_round"] = opened_round
                    if repaired:
                        result["repaired"] = repaired
                    return result

                result = execute_job(self.state, job, self.handlers, dry_run=dry_run)
                if not dry_run:
                    self._finalize_stage_status(job["stage"])
                    self._save_unlocked()
                return {
                    "success": result.get("success"),
                    "job_id": job["job_id"],
                    "result": result,
                    "executed": 1,
                    **({"opened_input_round": opened_round} if opened_round is not None else {}),
                    **({"repaired": repaired} if repaired else {}),
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
                # v7.2.52（BUG-19）：pick_next_job 内部会通过
                # _resolve_blocking_deps 执行自愈（失败 job 重试 /
                # auto_unlock 逃生阀），且**不返回**自愈动作。本轮若无可
                # 执行 job 就直接 break，旧版**不落盘** → 自愈结果全部丢失：
                # auto_unlock_count 恒为 None（「终生至多解锁一次」守卫失效，
                # 每 tick 重复解锁）、repair_attempts 恒不增长 →
                # auto-unlock 逃生阀永不触发 → 周末反思链永久死锁。
                #
                # 该缺陷与 v7.2.47（BUG-11）同源，但修复只覆盖了 run_next
                # 路径；run_stage（周末入口 cron / run-all 主路径）未修。
                # 10-27 12h 健康检查 BUG-19 实测：同一份 state，run_next
                # 落盘成功（auto_unlock_count=1 / repair_attempts=0），
                # run_stage 落盘为空（failed/3/None）——两条路径两种结果。
                #
                # 修复：进 pick_next_job 前取自愈指纹，退出时比对，
                # 有变化即落盘（落盘走 _save_unlocked，禁嵌套同名 flock
                # 自死锁）。注意：函数末尾的「汇总阶段状态」块会
                # **重新 load 磁盘状态**，故必须在此处（reload 之前）落盘，
                # 否则自愈结果仍会被 reload 丢弃。
                #
                # v7.2.53（BUG-20）：指纹取**全库**而非本阶段——
                # pick_next_job 的 stale running 扫描不看 stage，
                # _resolve_blocking_deps 修复的是别阶段的依赖，
                # 两者都会改写 stage 之外的 job（详见
                # _stage_heal_fingerprint docstring）。
                heal_fp_before = self._stage_heal_fingerprint(self.state)
                job = pick_next_job(self.state, stage=stage)
                if not job:
                    # v7.2.52（BUG-19）：本轮无可执行 job，但 pick_next_job
                    # 内部的 _resolve_blocking_deps 可能已执行自愈（失败 job
                    # 重试 / auto_unlock 逃生阀）。旧版在此直接 break 且
                    # **不落盘** → 自愈结果全部丢失：auto_unlock_count 恒为
                    # None（「终生至多解锁一次」守卫失效，每 tick 重复解锁）、
                    # repair_attempts 恒不增长 → auto-unlock 逃生阀永不触发
                    # → 周末反思链永久死锁。
                    #
                    # 修复：比对自己愈敏感字段指纹，有变化即落盘。
                    # 落盘走 _save_unlocked（禁嵌套同名 flock 自死锁）。
                    # 注意：函数末尾的「汇总阶段状态」块会重新 load 磁盘状态，
                    # 故必须在此处（reload 之前）落盘，否则自愈结果仍被丢弃。
                    if not dry_run:
                        heal_fp_after = self._stage_heal_fingerprint(self.state)
                        if heal_fp_after != heal_fp_before:
                            self._save_unlocked()
                            if _log:
                                changed = [
                                    jid for jid, fp in heal_fp_after.items()
                                    if heal_fp_before.get(jid) != fp
                                ]
                                _log.info(
                                    f"[weekend_pipeline] 自愈结果落盘: "
                                    f"{len(changed)} 个 job（{', '.join(changed[:3])}"
                                    f"{' 等' if len(changed) > 3 else ''}）"
                                )
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
