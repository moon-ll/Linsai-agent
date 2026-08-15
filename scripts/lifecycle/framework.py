#!/usr/bin/env python3
"""生命周期 cron 框架安装与卸载。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import hermes_bridge as hb
from paths import PROJECT_ROOT

from .constants import (
    DEFAULT_ORCHESTRATE_SCHEDULE,
    DEFAULT_PROMPT_OPTIMIZE_SCHEDULE,
    DEFAULT_REPAIR_SCHEDULE,
    DEFAULT_RETROSPECTIVE_SCHEDULE,
    DEFAULT_KB_SYNC_SCHEDULE,
    KB_SYNC_CRON_NAME,
    DEFAULT_KB_DISTILL_SCHEDULE,
    KB_DISTILL_CRON_NAME,
    DEFAULT_WEEKEND_INPUT_SCHEDULE,
    DEFAULT_WEEKEND_OUTPUT_SCHEDULE,
    DEFAULT_WEEKEND_REFLECTION_SCHEDULE,
    DEFAULT_WORKER_INTERVAL,
    HERMES_PROFILE,
    JOB_STATUS_PENDING,
    WEEKEND_JOB_INPUT,
    WEEKEND_JOB_OUTPUT,
    WEEKEND_JOB_REFLECTION,
    WEEKEND_JOBS,
)
from weekend_pipeline.constants import (
    DEFAULT_WORKER_SCHEDULE as WEEKEND_DEFAULT_WORKER_SCHEDULE,
    WEEKEND_WORKER_CRON_NAME,
)
from .utils import _load_weekend_jobs, _save_weekend_jobs, _write_wrapper_script

try:
    from logger import get_logger
    _log = get_logger("lifecycle_cron")
except Exception:
    _log = None


def _cron_create_idempotent(
    script_name: str,
    name: str,
    schedule: str,
) -> Dict[str, Any]:
    """v6.8.53: 幂等创建框架 cron——同名且调度一致则跳过，不一致则删旧建新。

    背景：setup_cron_framework 每次调用都无条件 create，而 cleanup_cron_duplicates
    只处理"已存在多副本"（len>1 才删）。第二次 setup 时同名只剩 1 个，cleanup
    不删、create 再建 → 每执行一次 setup 副本数 +1（实测 2026-08-14 两次 setup
    产生 5 组重复，lc-kb-sync 双实例次日将并发执行两次 kb_auto_sync）。
    """
    for cron in hb.cron_list_profile(HERMES_PROFILE):
        if cron.get("name") == name:
            if cron.get("schedule") == schedule and cron.get("status") == "active":
                if _log:
                    _log.info(f"[cron 幂等] {name} 已存在且调度一致，跳过创建")
                return {"success": True, "skipped": True, "id": cron.get("id", "")}
            # 调度变化或已暂停 → 删旧建新
            if _log:
                _log.warning(
                    f"[cron 幂等] {name} 调度不一致或非 active，删除旧实例后重建"
                )
            hb.cron_delete(cron.get("id", ""), profile=HERMES_PROFILE)
            break
    return hb.cron_create_no_agent(
        script_name=script_name,
        name=name,
        schedule=schedule,
        workdir=str(PROJECT_ROOT),
        profile=HERMES_PROFILE,
    )


def cleanup_cron_duplicates(
    self,
    framework_names: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """v6.8.23: 清理 HERMES_PROFILE 下所有同名 cron 副本，每类仅保留最新 1 个。

    历史根因：setup_cron_framework 在每次升级/手动 setup 时未彻底清理
    历史累积的同名 cron，导致 jobs.json 中出现 5× 同名实例（lc-prompt-optimize
    / lc-repair / lc-daily-orchestrate / lc-retrospective），每天 14:00 cron 触发
    时被 hermes 同时调度 5 次，叠加 prompt_optimizer.cmd_auto 的"每分钟持续写入"
    行为，4h 内可生成 5000+ 条 prompt_tuning journal 条目（debug-journal.json
    从 46MB 涨至 49MB+）。

    触发场景（具体、可信）：
      1. 用户多次执行 `proposal_lifecycle.py --setup-cron-v2`，但 setup_cron_framework
         内联的清理逻辑只能覆盖"创建前存在的副本"，无法处理历史累积
      2. hermes scheduler 同时调度 5 个 lc-prompt-optimize，每天 14:00 触发 5 次
      3. 每次 cmd_auto 从 7 天窗口内 ~5000 条 prompt_tuning 日志采集，生成
         fingerprint 唯一的 suggestion，写入 critic/SOUL.md 并 append 新 journal
      4. 基数持续增长，磁盘 4h 窗口内 +3MB

    Args:
        framework_names: 需要去重的 cron 名称列表，默认覆盖 lc-* 框架 4 类 +
            lc-hourly-monitor + lc-kb-sync（v6.8.53 补入，否则监控端检测到
            kb-sync 重复后自动去重清不掉，异常每小时复现永不收敛）。

    Returns:
        删除记录列表，每项 {name, id, created_at}。
    """
    if framework_names is None:
        framework_names = [
            "lc-daily-orchestrate", "lc-repair",
            "lc-prompt-optimize", "lc-retrospective",
            "lc-hourly-monitor",
            KB_SYNC_CRON_NAME,
            KB_DISTILL_CRON_NAME,
        ]
    removed: List[Dict[str, str]] = []
    # 按 name 分组
    by_name: Dict[str, List[Dict]] = {}
    for cron in hb.cron_list_profile(HERMES_PROFILE):
        cname = cron.get("name", "")
        if cname in framework_names:
            by_name.setdefault(cname, []).append(cron)

    for cname, group in by_name.items():
        if len(group) <= 1:
            continue
        # 保留最新（created_at 最大），其余删除
        group_sorted = sorted(group, key=lambda c: c.get("created_at", ""))
        keeper = group_sorted[-1]
        for old in group_sorted[:-1]:
            cid = old.get("id", "")
            res = hb.cron_delete(cid, profile=HERMES_PROFILE)
            removed.append({
                "name": cname,
                "id": cid,
                "created_at": old.get("created_at", ""),
                "deleted": bool(res.get("success")),
            })
            if _log:
                _log.warning(
                    f"[cron 副本清理] 删除 {cname} id={cid} "
                    f"(created={old.get('created_at','')[:19]}); "
                    f"保留 id={keeper.get('id')}"
                )
    return removed


def setup_cron_framework(
    self,
    orchestrate_schedule: str = DEFAULT_ORCHESTRATE_SCHEDULE,
    worker_interval: str = DEFAULT_WORKER_INTERVAL,
    repair_schedule: str = DEFAULT_REPAIR_SCHEDULE,
    install_weekend: bool = True,
) -> Dict[str, Any]:
    """安装 v6.7.12 cron 框架：删除旧单一 cron，创建 orchestrate + repair + 全局微调度器 + weekend。

    worker_interval 参数保留以兼容 CLI，但实际 worker 已由全局微调度器替代，
    每 5 分钟从所有 optimizing proposal 中挑选一个最优先的 pending job 执行。

    v6.8.23: 在创建前调用 cleanup_cron_duplicates()，处理历史累积的
    同名 cron 副本（每类保留最新 1 个）。
    """
    self._write_generic_wrappers()

    # v6.8.23: 用统一去重函数替换 v6.7.12 内联清理逻辑，统一处理历史副本
    dedup_removed = self.cleanup_cron_duplicates()

    # 删除旧的大 cron（兼容 v6.7.4 及之前）—— 仍保留此分支处理中文名旧 cron
    old_names = ["每日提案系统编排", "每日编排"]
    removed = [r["name"] for r in dedup_removed]
    for cron in hb.cron_list_profile(HERMES_PROFILE):
        cname = cron.get("name", "")
        if cname in old_names:
            hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
            removed.append(cname)

    # orchestrate cron（v6.8.53: 幂等创建）
    orch = _cron_create_idempotent(
        script_name="lc_orchestrate.sh",
        name="lc-daily-orchestrate",
        schedule=orchestrate_schedule,
    )

    # repair cron（v6.8.53: 幂等创建）
    rep = _cron_create_idempotent(
        script_name="lc_repair.sh",
        name="lc-repair",
        schedule=repair_schedule,
    )

    # 全局微调度器 cron（每 5 分钟执行一个 job）
    micro = self.schedule_micro_scheduler()

    # 暂停旧的 per-proposal worker，避免并发
    pause_res = self.pause_old_worker_crons()

    # 立即执行一次 orchestrate，确保 checkpoint 就位
    orch_now = self.run_orchestrator()

    result = {
        "success": orch.get("success") and rep.get("success") and micro.get("success"),
        "removed_old": removed,
        "orchestrate": orch,
        "repair": rep,
        "micro_scheduler": micro,
        "paused_workers": pause_res.get("paused", []),
        "first_orchestrate": orch_now,
    }

    # 安装周末任务 cron
    if install_weekend:
        weekend = self.setup_weekend_crontab()
        result["weekend"] = weekend
        result["success"] = result["success"] and all(
            c.get("result", {}).get("success") for c in weekend.get("created", [])
        )

    # 安装 prompt 自动优化 cron（每天 14:00）—— 先清理同名旧实例
    # v6.8.23: 改用 cleanup_cron_duplicates 统一处理（保留最新 1 个）
    extra_cleanup = self.cleanup_cron_duplicates(framework_names=["lc-prompt-optimize"])
    for r in extra_cleanup:
        if r["name"] not in removed:
            removed.append(r["name"])
    prompt_opt = _cron_create_idempotent(
        script_name="lc_prompt_optimize.sh",
        name="lc-prompt-optimize",
        schedule=DEFAULT_PROMPT_OPTIMIZE_SCHEDULE,
    )
    result["prompt_optimize"] = prompt_opt
    result["success"] = result["success"] and prompt_opt.get("success")

    # 安装复盘 cron（每周一 15:00）—— 先清理同名旧实例
    # v6.8.23: 改用 cleanup_cron_duplicates 统一处理（保留最新 1 个）
    extra_cleanup = self.cleanup_cron_duplicates(framework_names=["lc-retrospective"])
    for r in extra_cleanup:
        if r["name"] not in removed:
            removed.append(r["name"])
    retro = _cron_create_idempotent(
        script_name="lc_retrospective.sh",
        name="lc-retrospective",
        schedule=DEFAULT_RETROSPECTIVE_SCHEDULE,
    )
    result["retrospective"] = retro
    result["success"] = result["success"] and retro.get("success")

    # 安装知识库每日同步 cron（v6.8.51）—— sync_all 含 hermes 会话/简报/PDF
    # 同步 + 索引重建 + 图谱重建。此前 kb_auto_sync 设计为 LaunchAgent 但从未安装，
    # 导致索引停在 08-08、growth-log 断流两个月。先清理同名旧实例。
    extra_cleanup = self.cleanup_cron_duplicates(framework_names=[KB_SYNC_CRON_NAME])
    for r in extra_cleanup:
        if r["name"] not in removed:
            removed.append(r["name"])
    kb_sync = _cron_create_idempotent(
        script_name="lc_kb_sync.sh",
        name=KB_SYNC_CRON_NAME,
        schedule=DEFAULT_KB_SYNC_SCHEDULE,
    )
    result["kb_sync"] = kb_sync
    result["success"] = result["success"] and kb_sync.get("success")

    # 安装知识库每日蒸馏 cron（v6.9.5）—— lc-kb-sync 之后 10 分钟，
    # 补上 raw→wiki 蒸馏的流水线生产者（此前接口存在但无人调用，
    # 351 项积压）。单篇失败不阻断批次（wrapper 已 exit 0）。
    extra_cleanup = self.cleanup_cron_duplicates(framework_names=[KB_DISTILL_CRON_NAME])
    for r in extra_cleanup:
        if r["name"] not in removed:
            removed.append(r["name"])
    kb_distill = _cron_create_idempotent(
        script_name="lc_kb_distill.sh",
        name=KB_DISTILL_CRON_NAME,
        schedule=DEFAULT_KB_DISTILL_SCHEDULE,
    )
    result["kb_distill"] = kb_distill
    result["success"] = result["success"] and kb_distill.get("success")

    return result

def setup_weekend_crontab(
    self,
    input_schedule: str = DEFAULT_WEEKEND_INPUT_SCHEDULE,
    output_schedule: str = DEFAULT_WEEKEND_OUTPUT_SCHEDULE,
    reflection_schedule: str = DEFAULT_WEEKEND_REFLECTION_SCHEDULE,
) -> Dict[str, Any]:
    """安装周末任务 cron：输入（周六早）/ 输出（周六午）/ 反思（周日早）。"""
    self._write_generic_wrappers()
    # 先清理已存在的 weekend cron，避免重复安装
    self.teardown_weekend_crontab()

    # 确保 weekend_jobs 状态文件存在
    weekend_jobs = _load_weekend_jobs()
    for job_key in WEEKEND_JOBS:
        weekend_jobs.setdefault("jobs", {}).setdefault(job_key, {
            "status": JOB_STATUS_PENDING,
            "last_run": "",
            "started_at": "",
            "finished_at": "",
            "last_error": "",
            "attempts": 0,
        })
    _save_weekend_jobs(weekend_jobs)

    created = []
    for job_key, schedule in [
        (WEEKEND_JOB_INPUT, input_schedule),
        (WEEKEND_JOB_OUTPUT, output_schedule),
        (WEEKEND_JOB_REFLECTION, reflection_schedule),
    ]:
        script_name = f"lc_{job_key}.sh"
        cron_name = f"lc-weekend-{job_key.replace('_', '-')}"
        res = hb.cron_create_no_agent(
            script_name=script_name,
            name=cron_name,
            schedule=schedule,
            workdir=str(PROJECT_ROOT),
            profile=HERMES_PROFILE,
        )
        created.append({"job": job_key, "cron": cron_name, "result": res})

    # 新增 weekend worker：每 20 分钟执行一个 pending job
    worker_res = hb.cron_create_no_agent(
        script_name="lc_weekend_worker.sh",
        name=WEEKEND_WORKER_CRON_NAME,
        schedule=WEEKEND_DEFAULT_WORKER_SCHEDULE,
        workdir=str(PROJECT_ROOT),
        profile=HERMES_PROFILE,
    )
    created.append({"job": "weekend_worker", "cron": WEEKEND_WORKER_CRON_NAME, "result": worker_res})

    return {"success": True, "created": created}

def teardown_weekend_crontab(self) -> Dict[str, Any]:
    """卸载所有 lc-weekend- 开头的 cron。"""
    removed = []
    for cron in self.list_lifecycle_crons():
        name = cron.get("name", "")
        if name.startswith("lc-weekend-"):
            res = hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
            if res.get("success"):
                removed.append(name)
    return {"success": True, "removed": removed}

def teardown_cron_framework(self) -> Dict[str, Any]:
    """卸载所有 lc- 开头的 lifecycle cron（含周末任务）。"""
    removed = []
    for cron in self.list_lifecycle_crons():
        res = hb.cron_delete(cron.get("id"), profile=HERMES_PROFILE)
        if res.get("success"):
            removed.append(cron.get("name"))
    return {"success": True, "removed": removed}