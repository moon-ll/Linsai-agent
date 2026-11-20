#!/usr/bin/env python3
"""lifecycle_monitor.py — 每小时全链路监控与异常告警（v6.8.2）。

功能：
    1. 检查所有 optimizing 课题的 job 执行状态（done/failed/pending/running）
    2. 更新系统看板（memory/system-kanban.json）
    3. 检测异常：卡住课题、连续失败、零进展、profile blocked
    4. 异常时通过 lark-cli 发送飞书通知

设计原则：
    - 纯标准库，零第三方依赖
    - lark-cli 不可用时优雅降级（只写看板+日志，不发通知）
    - 每小时运行一次，覆盖所有时段（含非工作时段）
    - 异常去重：同一异常 4 小时内不重复通知

用法：
    python3 scripts/lifecycle_monitor.py              # 执行一次监控
    python3 scripts/lifecycle_monitor.py --self-check  # 自检
    python3 scripts/lifecycle_monitor.py --dry-run     # 不发飞书通知

cron 注册（通过 hermes）：
    # wrapper 脚本由 lifecycle/controller.py 自动生成
    python3 scripts/proposal_lifecycle.py --setup-monitor
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc, load_json, save_json  # noqa: E402

# lark-cli 路径（TRAE 插件安装位置）。插件升级会变更版本目录（历史 1.0.3→1.0.4），
# 硬编码固定版本会使插件升级后飞书告警通道静默失效，故动态取插件目录最高版本，PATH 兜底。
_LARK_PLUGIN_DIR = Path.home() / ".trae-cn" / "plugins" / "trae-remote-official" / "lark"


def _resolve_lark_cli() -> str:
    """解析到已安装的 lark-cli：取插件目录中最高版本，其次 PATH 兜底。"""
    candidates: List[Tuple[int, int, int, Path]] = []
    if _LARK_PLUGIN_DIR.is_dir():
        for ver_dir in _LARK_PLUGIN_DIR.iterdir():
            if not ver_dir.is_dir():
                continue
            m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", ver_dir.name)
            if not m:
                continue
            cli = ver_dir / "bin" / "lark-cli"
            if cli.exists():
                candidates.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), cli))
    if candidates:
        candidates.sort(key=lambda c: c[:3], reverse=True)
        return str(candidates[0][3])
    on_path = shutil.which("lark-cli")
    return str(on_path) if on_path else ""


LARK_CLI = _resolve_lark_cli()

# 告警去重缓存
ALERT_CACHE_PATH = PROJECT_ROOT / "memory" / "monitor-alert-cache.json"

# 系统看板路径
KANBAN_PATH = PROJECT_ROOT / "memory" / "system-kanban.json"

# v7.1.8: r1 启动失败告警缓存路径——micro_scheduler 每个 tick 写入，
# lifecycle_monitor 每小时读取并经飞书链路发送。
R1_START_ALERT_PATH = PROJECT_ROOT / "memory" / "r1-start-alerts.json"

# 告警去重窗口（秒）。v6.9.68: 4h→24h——实测同批卡死 job 每 4h 复读一次，
# 7 天 90 条通知 90% 是重复（真实需人工的仅 2 类）；24h 冷却 + 夜间静默
# 把通知压缩为"每日至多一轮、只在工作时段"
ALERT_DEDUP_WINDOW = 24 * 3600  # 24 小时
# 夜间静默窗口（本地小时，不含边界）：22:00-08:00 只入缓存不发送
QUIET_HOURS = (22, 8)


def _in_quiet_hours() -> bool:
    """当前是否处于夜间静默窗口（22:00-08:00）。"""
    h = datetime.now().hour
    lo, hi = QUIET_HOURS
    return h >= lo or h < hi

try:
    from logger import get_logger
    _log = get_logger("lifecycle_monitor")
except Exception:
    _log = None


def _load_alert_cache() -> Dict[str, Any]:
    """加载告警去重缓存。"""
    return load_json(ALERT_CACHE_PATH, default={"alerts": {}})


def _save_alert_cache(cache: Dict[str, Any]) -> None:
    """保存告警去重缓存。"""
    ALERT_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_json(ALERT_CACHE_PATH, cache)


def _should_notify(alert_key: str) -> bool:
    """检查某告警是否应该通知（去重逻辑）。"""
    cache = _load_alert_cache()
    alerts = cache.get("alerts", {})
    last_sent = alerts.get(alert_key, {}).get("last_sent", "")
    if last_sent:
        try:
            last_dt = datetime.fromisoformat(last_sent.replace("Z", "+00:00"))
            elapsed = (datetime.now(last_dt.tzinfo) - last_dt).total_seconds()
            if elapsed < ALERT_DEDUP_WINDOW:
                return False
        except Exception:
            pass
    return True


def _prune_alert_cache(cache: Dict[str, Any]) -> int:
    """清理告警缓存中已过期的条目，返回清理数（v6.8.54）。

    此前仅在 _mark_notified 写入时顺带清理——若无新告警产生，过期条目
    会无限滞留在缓存文件里（实测 08-08 的 stalled 条目滞留 6 天），
    对任何读该文件的人构成"看起来有未处理告警"的噪音。
    """
    cutoff = datetime.now().timestamp() - ALERT_DEDUP_WINDOW
    removed = 0
    for key in list(cache.get("alerts", {}).keys()):
        info = cache["alerts"].get(key, {})
        sent = info.get("last_sent", "")
        if sent:
            try:
                dt = datetime.fromisoformat(sent.replace("Z", "+00:00"))
                if dt.timestamp() < cutoff:
                    del cache["alerts"][key]
                    removed += 1
            except Exception:
                pass
    return removed


def _mark_notified(alert_key: str, message: str) -> None:
    """记录告警已通知。"""
    cache = _load_alert_cache()
    cache.setdefault("alerts", {})[alert_key] = {
        "last_sent": now_utc(),
        "message": message[:200],
    }
    # 清理过期记录
    _prune_alert_cache(cache)
    _save_alert_cache(cache)


def _send_feishu(title: str, content: str) -> bool:
    """通过 lark-cli 发送飞书消息通知。

    优先尝试 lark-cli im +messages-send --user-id。
    不可用时返回 False，调用方应优雅降级。
    """
    if not os.path.isfile(LARK_CLI):
        if _log:
            _log.warning(f"lark-cli 不存在: {LARK_CLI}，跳过飞书通知")
        return False

    # 构建消息内容
    full_msg = f"{title}\n\n{content}"

    # 读取通知目标（open_id），优先从配置文件读取
    notify_config_path = PROJECT_ROOT / "memory" / "monitor-config.json"
    notify_config = load_json(notify_config_path, default={})
    user_id = notify_config.get("feishu_user_open_id", "")
    if not user_id:
        if _log:
            _log.warning("未配置 feishu_user_open_id（memory/monitor-config.json），跳过飞书通知")
        return False

    try:
        result = subprocess.run(
            [LARK_CLI, "im", "+messages-send", "--user-id", user_id, "--text", full_msg],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            if _log:
                _log.info(f"飞书通知发送成功: {title}")
            return True
        stderr = result.stderr.strip()
        if _log:
            _log.warning(f"lark-cli 发送失败 (exit={result.returncode}): {stderr[:200]}")
        return False
    except subprocess.TimeoutExpired:
        if _log:
            _log.warning("lark-cli 发送超时")
        return False
    except Exception as e:
        if _log:
            _log.warning(f"lark-cli 异常: {e}")
        return False


def _digest_failed_jobs(
    pid: str,
    jobs: List[Dict[str, Any]],
    ctrl: Any,
    dry_run: bool = False,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """v7.3.44: 发现即消化——满足自动修复条件的 failed job 立即重置。

    背景（11-05 实证）：ssh-weyl critic 双上限终态已满足 24h 解锁冷却，
    但 lc-repair 每 12h 才扫描一次且上次扫描时 job 年龄 23.2h（差 50
    分钟），告警连刷 46 轮才等来解锁窗口。监控此前对 cron 异常已有内联
    自愈（_auto_repair_cron），对 job 级 failed 却只报告不处置——本函数
    补齐后者：决策复用 lifecycle.utils.digest_failed_job_action（与
    run_repair step 3 同构，retry 加 2h 冷却防 429 窗口烧重试预算），
    写回复用 ctrl._save_jobs（proposal-lifecycle 锁，v7.2.48 防丢更新）。

    v7.3.53（BUG-49）：新增 `now` 注入缝——原实现内部硬取
    `datetime.now(timezone.utc)`，使「24h 冷却未满」这类**相对墙钟**
    判据无法被测试固定，导致 test_monitor_digest 的用例随真实日期翻转
    （2026-11-06T04:50:31Z 越过 24h 线后，断言「无可消化动作」必失败）。
    注入缝让调用方（测试）传入固定 now；不传时保持原行为（真实墙钟），
    **判据、阈值、决策逻辑一字未动**。

    Returns:
        消化记录列表 [{"job_id", "action", "action_desc"}]，dry_run 只
        返回决策不落盘。
    """
    from lifecycle.utils import digest_failed_job_action

    digested: List[Dict[str, Any]] = []
    dirty = False
    now = now or datetime.now(timezone.utc)
    for job in jobs:
        if not isinstance(job, dict) or job.get("status") != "failed":
            continue
        action = digest_failed_job_action(job, now)
        if not action:
            continue
        if action == "retry":
            repair_attempts = int(job.get("repair_attempts", 0))
            if not dry_run:
                job.update({
                    "status": "pending",
                    "started_at": "",
                    "finished_at": "",
                    "last_error": "",
                    "attempts": 0,
                    "repair_attempts": repair_attempts + 1,
                })
                dirty = True
            desc = f"失败已过冷却，retry 重置（repair_attempt {repair_attempts + 1}/{3}）"
        else:  # auto_unlock
            if not dry_run:
                job["auto_unlock_count"] = int(job.get("auto_unlock_count", 0)) + 1
                hist = job.get("error_history") or []
                hist.append({
                    "at": now_utc(),
                    "error": "自动解锁(监控消化 v7.3.44): 双上限终态且失败超24h，"
                             f"重置重跑（第{job['auto_unlock_count']}次/上限1）",
                    "attempts": job.get("attempts", 0),
                })
                job.update({
                    "status": "pending",
                    "attempts": 0,
                    "started_at": "",
                    "finished_at": "",
                    "last_error": "",
                    "error_history": hist,
                })
                dirty = True
            desc = "双上限终态自动解锁重跑"
        digested.append({
            "job_id": job.get("job_id", ""),
            "action": action,
            "action_desc": desc,
        })
    if dirty:
        try:
            ctrl._save_jobs(pid, jobs)
        except Exception as e:
            if _log:
                _log.warning(f"[digest] {pid} job 重置落盘失败（下轮 lc-repair 兜底）: {e}")
            return []
    return digested


def _check_proposals(dry_run: bool = False) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """检查所有 optimizing 课题状态。

    v7.3.44: failed job 发现即消化（_digest_failed_jobs）+ kanban 执行
    历史循环外单次读取并按 proposal_id 归因（原先每课题重复读同一文件，
    且全局错误被按课题重复放大报告）。

    Returns:
        (proposal_stats, anomalies)
    """
    from proposal_lifecycle import ProposalLifecycle
    from lifecycle.controller import get_controller

    pl = ProposalLifecycle()
    ctrl = get_controller()
    proposals = pl.list_by_status("optimizing")

    stats: List[Dict[str, Any]] = []
    anomalies: List[Dict[str, Any]] = []

    # v7.3.44 轻量化：执行历史循环外读一次，预解析最近 2h 失败记录按 pid 分桶
    recent_by_pid: Dict[str, List[Dict[str, Any]]] = {}
    try:
        kanban_data = load_json(KANBAN_PATH, default={})
        history = kanban_data.get("execution_history", [])
        from datetime import timezone as _tz
        now_dt = datetime.now(_tz.utc)
        for h in history:
            try:
                h_dt = datetime.fromisoformat(h.get("at", "").replace("Z", "+00:00"))
                if (now_dt - h_dt).total_seconds() < 7200 and not h.get("success", True):
                    recent_by_pid.setdefault(h.get("proposal_id", ""), []).append(h)
            except Exception:
                pass
    except Exception:
        pass

    for p in proposals:
        pid = p["proposal_id"]
        rounds = p.get("optimization_rounds", 0)
        score = p.get("last_score", 0)
        jobs = ctrl._get_jobs(pid)

        # v7.3.44: 先消化满足自动修复条件的 failed job（重置后不再计入
        # failed 统计与 stuck 告警，消化动作以 [已消化] 信息级异常留痕）
        for d in _digest_failed_jobs(pid, jobs, ctrl, dry_run=dry_run):
            anomalies.append({
                "type": "digested_job",
                "proposal_id": pid,
                "job_id": d["job_id"],
                "message": (
                    f"[已消化] 课题 {pid[:30]} 的 {str(d['job_id']).split('-')[-1]} "
                    f"{d['action_desc']}，已重置 pending 待微调度器重派"
                ),
            })

        done = sum(1 for j in jobs if j["status"] == "done")
        failed = sum(1 for j in jobs if j["status"] == "failed")
        pending = sum(1 for j in jobs if j["status"] == "pending")
        running = sum(1 for j in jobs if j["status"] == "running")
        total = len(jobs)

        stat = {
            "proposal_id": pid,
            "rounds": rounds,
            "score": score,
            "done": done,
            "failed": failed,
            "pending": pending,
            "running": running,
            "total": total,
            "progress_pct": round(done / total * 100, 1) if total else 0,
        }
        stats.append(stat)

        # 异常检测
        from lifecycle.constants import MAX_JOB_ATTEMPTS
        # 1. 有 failed job（不论 attempts 数，任何 failed 都应关注）
        failed_jobs = [j for j in jobs if j["status"] == "failed"]
        if failed_jobs:
            for sj in failed_jobs:
                err = sj.get("last_error", "")[:120]
                attempts = sj.get("attempts", 0)
                severity = "stuck" if attempts >= MAX_JOB_ATTEMPTS else "failed"
                anomalies.append({
                    "type": severity,
                    "proposal_id": pid,
                    "job_id": sj["job_id"],
                    "attempts": attempts,
                    "error": err,
                    "message": f"课题 {pid[:30]} 的 {sj['job_id'].split('-')[-1]} {severity}（attempts={attempts}）: {err}",
                })

        # 2. 连续同类 step 失败（不限 lit_search，扩展到所有 step）
        from collections import Counter
        failed_steps = [j.get("step", "") for j in jobs if j["status"] == "failed"]
        step_counts = Counter(failed_steps)
        for step_name, count in step_counts.items():
            if count >= 2:
                anomalies.append({
                    "type": "repeated_step_failure",
                    "proposal_id": pid,
                    "step": step_name,
                    "count": count,
                    "message": f"课题 {pid[:30]} 有 {count} 个 {step_name} 失败",
                })

        # 3. 检测执行历史中的系统性错误（429 限流、权限错误等）
        # v7.3.44: 改用循环外预解析的按 pid 分桶结果（原先每课题重复读
        # 整个 kanban 文件且把全局错误按课题重复放大报告）
        try:
            recent = recent_by_pid.get(pid, [])

            if recent:
                # 检查是否有 429/限流/权限错误模式
                rate_limit_errors = [h for h in recent if "429" in h.get("error", "") or "Token Plan" in h.get("error", "") or "用量上限" in h.get("error", "")]
                if len(rate_limit_errors) >= 2:
                    anomalies.append({
                        "type": "api_rate_limit",
                        "proposal_id": pid,
                        "count": len(rate_limit_errors),
                        "message": f"课题 {pid[:30]} 近 2h 内 {len(rate_limit_errors)} 次 API 限流（429/Token Plan 上限）",
                    })

                # 检查是否有权限/操作不允许错误
                perm_errors = [h for h in recent if "Operation not permitted" in h.get("error", "") or "Permission" in h.get("error", "")]
                if perm_errors:
                    anomalies.append({
                        "type": "permission_error",
                        "proposal_id": pid,
                        "count": len(perm_errors),
                        "message": f"课题 {pid[:30]} 近 2h 内 {len(perm_errors)} 次权限错误",
                    })
        except Exception:
            pass

        # v6.10.13: 停滞检测抽为 _check_proposal_stall（周末宽限版）
        _check_proposal_stall(pid, p, jobs, total, done, anomalies)
    # v6.8.27: 输入端熔断检测——从周末任务提升为每小时检查
    # 连续 2 周 weekend input 的 ideas_count=0 → input_pipeline_broken
    # v6.8.53: 数据源改读 weekend-pipeline.json 的 input job 结果。
    # v6.9.10: 口径再修正——旧实现"最近一次 ideas=0 且距今 ≥7 天"会被
    # 每周空跑刷新 finished_at（days_since 永远到不了 7），防线形同虚设
    # （08-01 起连续全零从未告警）。改为扫 weekend-input/ideas-*.json
    # 产物文件族：最近 2 个文件（跨 2 周）ideas 均为空即告警，不受
    # 空跑刷新影响。
    try:
        ideas_dir = PROJECT_ROOT / "memory" / "weekend-input"
        if ideas_dir.exists():
            import json
            idea_files = sorted(ideas_dir.glob("ideas-*.json"))
            if len(idea_files) >= 2:
                recent = idea_files[-2:]
                counts = []
                for f in recent:
                    try:
                        data = json.loads(f.read_text(encoding="utf-8"))
                        # v6.9.13: compose 实际产出 schema 为 {"generated_at",
                        # "actions":[...]}（新旧版本均如此，从未写过 "ideas"
                        # 键）。旧口径只读 "ideas" 恒为 0——链路恢复后告警
                        # 也永不解除。改以 actions 为主口径，ideas 键仅作
                        # 历史夹具兼容。
                        value = data.get("actions", data.get("ideas", []))
                        counts.append(len(value) if isinstance(value, list) else 0)
                    except Exception:
                        counts.append(0)
                if all(c == 0 for c in counts):
                    anomalies.append({
                        "type": "input_pipeline_broken",
                        "message": (
                            f"输入端连续 {len(recent)} 次周末运行零研究设想"
                            f"（{recent[0].stem} / {recent[-1].stem}），"
                            f"建议检查 summarize 新料过滤与 compose 路由链路。"
                        ),
                    })
    except Exception:
        pass

    return stats, anomalies


def _weekend_hours_between(last_dt, now) -> float:
    """v6.10.13: 计算窗口内落在周末（周六/周日，本地时区）的小时数。

    周末 worker 设计性暂停（v6.7.7+），课题 job 停在原地属预期——
    停滞检测应扣除周末时段再比对阈值，否则每个周末都批量误报
    （实测 09-13：8 条未解决告警中 5 条为周末设计性"停滞"）。
    """
    from datetime import timedelta
    total = 0.0
    cur = last_dt
    guard = 0
    while cur < now and guard < 400:
        day_start = cur.replace(hour=0, minute=0, second=0, microsecond=0)
        seg_end = min(day_start + timedelta(days=1), now)
        try:
            if cur.astimezone().weekday() >= 5:  # 周六=5 周日=6
                total += (seg_end - cur).total_seconds() / 3600
        except Exception:
            break
        cur = seg_end
        guard += 1
    return total


def _check_proposal_stall(pid, p, jobs, total, done, anomalies):
    """v6.8.16 改进2: 停滞课题检测。

    v6.8.27 修复: 旧版要求 done==0 才触发，但大多数停滞课题已有部分 done job
    改为：只要 updated_at 超 48h 且当前还有 pending job（说明没跑完就卡了）
    v6.9.31 修复: 停滞时钟改用「job 级最后活动」（任一 job 的
    finished_at/started_at 最大值）——旧口径读 proposal 的 updated_at，
    会被 repair 重置 / cron 失败记录 / stale 清理等非执行写入刷新，
    掩盖真实停滞（08-21 bsv 实证：updated_at 距 26.1h、job 实际停滞
    87.7h，48h 告警永不触发）。无 job 时间戳时回退 updated_at。
    v6.10.13: 周末宽限——停滞时钟扣除窗口内的周末小时（本地时区
    周六/周日），周一恢复后真实停滞仍会触发（净工时口径）。
    v7.2.6 改进: 区分「真停滞」与「队列末端排队」——
    旧逻辑把「48h+ 无新 job + 有 pending」一律告警，导致排在 queue 末端
    的 proposal 被误判（2026-09-29 berry-mnps3-rashba 实证：queue[9] 排
    队 4+ 天，pending=20 但实属正常轮转）。新增 `_classify_stall_kind`：
      - queue_tail  : 课题在 queue 后 1/3 且无 failed job → 排队中，非真停滞
      - job_stuck   : 有 failed 且 attempts>=MAX 但 finished<24h → 真卡死
      - blocked     : 有 pending 但上游 failed 未解锁 → 真卡死
      - idle        : 无 failed 无 pending 但 48h 无新 job → 真空转
    只对真停滞（job_stuck / blocked / idle）发出 stalled 告警；
    queue_tail 改发 queue_tail_warn（低优先级，提示但不阻塞决策）。
    """
    STALL_THRESHOLD_HOURS = 48
    try:
        job_activity = ""
        for j in jobs:
            t = j.get("finished_at") or j.get("started_at") or ""
            if t > job_activity:
                job_activity = t
        last_activity = job_activity or p.get("updated_at", "")
        if not last_activity:
            return
        last_dt = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        hours_since = (now - last_dt).total_seconds() // 3600
        weekend_h = _weekend_hours_between(last_dt, now)
        effective_h = max(0.0, hours_since - weekend_h)
        pending_count = total - done
        if not effective_h >= STALL_THRESHOLD_HOURS:
            return

        # v7.2.6: 区分真停滞 vs 队列末端排队
        stall_kind, extra = _classify_stall_kind(pid, jobs, pending_count)
        if stall_kind == "queue_tail":
            # 低优先级提示，不发 stalled 告警
            anomalies.append({
                "type": "queue_tail_warn",
                "proposal_id": pid,
                "queue_index": extra.get("queue_index", -1),
                "queue_total": extra.get("queue_total", 0),
                "hours": int(hours_since),
                "effective_hours": int(effective_h),
                "done": done,
                "total": total,
                "pending": pending_count,
                "message": (
                    f"课题 {pid[:40]} 排队中（queue[{extra.get('queue_index', '-')}]/"
                    f"{extra.get('queue_total', '-')}），"
                    f"{done}/{total} job 完成，{int(effective_h)}h 净工时未执行。"
                    f"非真停滞：若需优先处理可使用 scripts/promote_proposal_to_focus.py "
                    f"apply --proposal {pid}。"
                ),
            })
            return

        # 真停滞：job_stuck / blocked / idle。
        # v7.2.7 修复：idle + skip_alert（proposal 不在 focus queue + 无 pending，
        # 轮次已收尾）→ 不告警（test_stalled_clock 用例 4 实证）。
        if stall_kind == "idle" and extra.get("skip_alert"):
            return
        anomalies.append({
            "type": "stalled",
            "subtype": stall_kind,
            "proposal_id": pid,
            "hours": int(hours_since),
            "effective_hours": int(effective_h),
            "weekend_exempt_hours": int(weekend_h),
            "done": done,
            "total": total,
            "pending": pending_count,
            "stall_detail": extra,
            "message": (
                f"课题 {pid[:40]} 真停滞 {int(effective_h)}h（{stall_kind}，"
                f"周末豁免 {int(weekend_h)}h，净工时口径），"
                f"{done}/{total} job 完成，{pending_count} 个 pending 未执行。"
                f"建议："
                f"{_stall_remediation(stall_kind, extra)}"
            ),
        })
    except Exception:
        pass


def _classify_stall_kind(pid, jobs, pending_count):
    """v7.2.6: 把停滞归类为「queue_tail / job_stuck / blocked / idle / rotation_stall」。

    返回 (kind, detail_dict)。kind ∈ {"queue_tail", "job_stuck", "blocked",
    "idle", "rotation_stall"}。

    判断逻辑（优先级从强到弱）：
      1. 有 failed 且 attempts>=MAX 且 finished>=24h → job_stuck（已用尽的死 job）
      2. 有 failed 但 attempts<MAX 或 finished<24h → blocked（上游失败阻塞）
      3. 无 failed 但 pending>0 且上游 done 链路有中断 → blocked（依赖解锁缺失）
      4. 无 failed 无 pending 但无新 job → idle（真空转，可能需 inspect）
      5. 在 queue 队尾（后 1/3）→ queue_tail（排队中，非真停滞）
         非队尾 + 全链 ≥24h 无 job 执行 → rotation_stall（v7.2.55 调度级停滞）
         非队尾 + 链上仍有活动 → queue_tail（轮转推进中的正常等待）
         不在 queue 中 → blocked（上游调度未接管，v7.2.7）
    """
    failed_jobs = [j for j in jobs if j.get("status") == "failed"]
    pending_jobs = [j for j in jobs if j.get("status") == "pending"]
    done_jobs = [j for j in jobs if j.get("status") == "done"]
    from lifecycle.constants import MAX_JOB_ATTEMPTS
    from datetime import timezone as _tz

    # 1. 真卡死的 failed job（attempts 用尽 + 已 finished 超 24h）
    for j in failed_jobs:
        attempts = int(j.get("attempts", 0))
        finished = str(j.get("finished_at") or "")
        if attempts >= MAX_JOB_ATTEMPTS and finished:
            try:
                fin_dt = datetime.fromisoformat(finished.replace("Z", "+00:00"))
                age_h = (datetime.now(_tz.utc) - fin_dt).total_seconds() / 3600
                if age_h >= 24:
                    return "job_stuck", {
                        "stuck_job_id": j.get("job_id"),
                        "attempts": attempts,
                        "last_error": (j.get("last_error") or "")[:200],
                    }
            except Exception:
                pass

    # 2. 上游 failed 阻塞 pending（attempts 未用尽或未到 24h）
    if failed_jobs:
        return "blocked", {
            "blocking_jobs": [j.get("job_id") for j in failed_jobs[:3]],
            "blocking_attempts": [int(j.get("attempts", 0)) for j in failed_jobs[:3]],
        }

    # 3. pending 但依赖的 job 根本不存在（罕见：被清理/错位）
    # v7.2.9 修复：旧判定「dep not in done_ids」把正常串行链误判为
    # missing_deps——上游 job 尚在 pending/running 中排队是轮转的常态
    # （2026-09-30 order-parameter 实证：0 failed、r7-full_review-lit_note
    # 依赖的 lit_read 本身 pending，被误标 blocked，实际是等 queue 聚焦）。
    # 修正口径：dep 不在全部已知 job 集合（done ∪ pending ∪ running ∪
    # failed）中才算真缺失；failed 依赖由分支 2 提前拦截，此处不会命中。
    if pending_jobs:
        all_ids = {j.get("job_id") for j in jobs}
        broken_deps = []
        for j in pending_jobs[:5]:
            for dep in j.get("depends_on", []):
                if dep not in all_ids:
                    broken_deps.append(dep)
                    break
        if broken_deps:
            return "blocked", {"missing_deps": broken_deps[:5]}

    # 4. 无 failed 无 pending 但无新 job → idle
    # v7.2.7 修复：当 proposal 不在 focus queue 时，无 pending = 轮次已收尾，
    # 不应触发 idle stalled 告警（test_stalled_clock 用例 4 实证）。仅当在
    # focus queue 且无 pending 时才是「真空转」异常。
    if not failed_jobs and pending_count == 0:
        q_idx, q_tot = _get_proposal_queue_position(pid)
        if q_idx < 0 or q_tot <= 0:
            return "idle", {"note": "无 pending 无 failed 且不在 focus queue（轮次已收尾，无需告警）", "skip_alert": True}
        return "idle", {"note": "无 pending 无 failed，但停滞时钟触发（罕见）"}

    # 5. 默认：排队中（无任何失败 + 有 pending = 正常轮转末端）。
    # v7.2.7 修复：proposal 不在 queue 中（queue_index=-1 或 queue_total=0），
    # 不可降级为 queue_tail——这是真停滞信号（focus 调度未接管该 proposal），
    # 应保留 stalled 告警而非降级为 queue_tail_warn 掩盖。test_stalled_clock
    # 实证：fake queue（隔离测试环境）下默认归类 queue_tail 会让本应触发
    # stalled 的真停滞被静默。
    queue_index, queue_total = _get_proposal_queue_position(pid)
    if queue_index < 0 or queue_total <= 0:
        # proposal 不在 focus queue——是上游调度问题，归为 blocked 而非 queue_tail
        return "blocked", {
            "note": "proposal 不在 focus queue 中，上游调度未接管",
            "queue_index": queue_index,
            "queue_total": queue_total,
        }
    is_tail = queue_index >= max(0, queue_total - max(2, queue_total // 3))
    # v7.2.55（#8 判据虚设修复）：is_queue_tail 此前只写进 detail 无人消费，
    # 分支对 queue 头部课题也一律降级 queue_tail_warn（实测 11/11 全降级，
    # 其中 8/11 is_queue_tail=False——queue[0] 的 houston 158h 净工时停滞
    # 被低优先级 warn 掩盖）。修正：仅队尾课题维持 queue_tail（正常排队）；
    # 非队尾课题停滞时钟已触发时看全链推进——链上近 24h（周末豁免口径）
    # 仍有 job 执行说明轮转在推进，非队尾等待属正常；链整体冻结则是调度
    # 级停滞（rotation_stall），发真 stalled 告警。
    if is_tail:
        return ("queue_tail", {
            "queue_index": queue_index,
            "queue_total": queue_total,
            "is_queue_tail": True,
        })
    chain_age = _chain_last_activity_age_h()
    if chain_age is not None and chain_age >= CHAIN_PROGRESS_WINDOW_H:
        return ("rotation_stall", {
            "queue_index": queue_index,
            "queue_total": queue_total,
            "is_queue_tail": False,
            "chain_frozen_hours": round(chain_age, 1),
        })
    return ("queue_tail", {
        "queue_index": queue_index,
        "queue_total": queue_total,
        "is_queue_tail": False,
        "chain_active_hours": (
            round(chain_age, 1) if chain_age is not None else None
        ),
    })


def _known_proposal_ids():
    """读真实课题 id 集合（轮转名单白名单），读不到返回 None。

    v7.2.105（BUG-34）：轮转名单成员必然来自 `_lifecycle.json` 的
    proposals 集合，以其为权威白名单可精确剔除测试夹具占位 id，
    同时保证真实课题永不误杀。读不到时返回 None → 下游退化为形态判定
    （fail-open）。
    """
    try:
        from common import load_json
        path = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
        data = load_json(path, default={})
        props = data.get("proposals") or {}
        if not props:
            return None
        return set(props.keys())
    except Exception:
        return None


def _get_proposal_queue_position(pid):
    """v7.2.6: 读 memory/lifecycle-focus.json，返回 (queue_index, queue_total)。

    queue_index=-1 表示 proposal 不在 queue 中（不在 optimizing 或刚退出）。

    v7.2.70 修复：轮转队列改读 `queue_full`（完整候补名单）而非 `queue`。
    v7.2.66 引入 WIP 硬窗口后，`queue` 只保留前 MAX_ROTATION_WIP=3 个课题，
    其余候选课题被放进 `queue_full` 候补（pull-based 语义：成员晋级/归档/
    冻结后窗口自动下移）。旧实现只读 `queue` → 窗口外课题一律返回
    queue_index=-1 → `_classify_stall_kind` 分支 5 判为「不在 focus queue
    中，上游调度未接管」= blocked（真停滞）→ 正常候补课题被误发 stalled
    告警。实测（10-31 04h）：7 个 optimizing 课题中 4 个候补课题被判
    blocked；houston 的 stalled 告警即由此误判产生（实际只是 WIP 窗口外
    候补，其 r3-references-writer 依赖已满足可立即执行）。
    改读 `queue_full` 后，队尾判定（后 1/3）基于完整名单，恢复「候补 =
    排队中（非真停滞）」的原设计语义。
    """
    try:
        from common import load_json
        from rotation_queue import get_rotation_queue, sanitize_rotation_queue
        focus = load_json(PROJECT_ROOT / "memory" / "lifecycle-focus.json", default={})
        # v7.2.71: 经共享 helper 取完整候补名单（无 queue_full 键时回退旧 queue 键）
        queue = get_rotation_queue(focus)
        # v7.2.105（BUG-34）：剔除名单中的非法成员（测试夹具占位 id 等）。
        # 污染期间真实课题的 queue_index 恒为 -1 → _classify_stall_kind
        # 判 blocked（真停滞）→ 误发 stalled 告警。此处按与写入方
        # （micro_scheduler._sync_queue）相同的口径过滤，读写两侧一致。
        # 白名单取真实课题 id 集合；读不到时 sanitize 退化为形态判定
        # （fail-open，不误杀真实课题）。
        known = _known_proposal_ids()
        queue, _dropped = sanitize_rotation_queue(queue, known)
        if pid in queue:
            return queue.index(pid), len(queue)
        return -1, len(queue)
    except Exception:
        return -1, 0


# v7.2.55（#8 判据虚设修复）：全链推进窗口——链上最近一次 job 执行距今
# 超过该值即视为「轮转冻结」，非队尾课题的停滞不再降级为 queue_tail_warn。
CHAIN_PROGRESS_WINDOW_H = 24.0

_chain_activity_cache: Dict[str, Any] = {}
"""全链活动缓存（mtime 键控，测试可注入 {'age': float} 覆盖）。"""


def _chain_last_activity_age_h() -> Optional[float]:
    """v7.2.55: 全链（所有课题）最近一次 job 执行距今小时数（周末豁免口径）。

    数据源为 system-kanban.json 的 execution_history（微调度器主写，
    与健康检查「主链停摆」同口径），取末条 at。无记录/解析失败返回
    None（调用方按「无法判定」处理，不触发 rotation_stall）。
    mtime 键控缓存避免 monitor 单轮 11 课题重复读文件；测试可直接
    注入 _chain_activity_cache = {'age': x} 绕过读盘。
    """
    if "age" in _chain_activity_cache:
        return _chain_activity_cache["age"]
    try:
        mtime = KANBAN_PATH.stat().st_mtime
        cached = _chain_activity_cache.get("mtime")
        if cached == mtime and "age_value" in _chain_activity_cache:
            return _chain_activity_cache["age_value"]
        history = load_json(KANBAN_PATH, default={}).get("execution_history", [])
        last_at = history[-1].get("at", "") if history else ""
        if not last_at:
            _chain_activity_cache["mtime"] = mtime
            _chain_activity_cache["age_value"] = None
            return None
        last_dt = datetime.fromisoformat(str(last_at).replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        raw_h = (now - last_dt).total_seconds() / 3600.0
        age = max(0.0, raw_h - _weekend_hours_between(last_dt, now))
        _chain_activity_cache["mtime"] = mtime
        _chain_activity_cache["age_value"] = round(age, 1)
        return age
    except Exception:
        return None


def _stall_remediation(kind, detail):
    """v7.2.6: 真停滞的具体处置建议。"""
    if kind == "job_stuck":
        jid = (detail.get("stuck_job_id") or "unknown")[-50:]
        return (
            f"运行 scripts/restart_stalled_failed_job.py --proposal <id> 重启死 job，"
            f"或手动 promote 强制聚焦。stuck job: {jid}"
        )
    if kind == "blocked":
        blk = detail.get("blocking_jobs", [])
        return (
            f"上游 failed job 阻塞：{blk[:2]}；"
            f"可手动 promote 或修复上游失败（attempts 未用尽时等自动重试）"
        )
    if kind == "idle":
        return (
            "无 pending 无 failed 但停滞时钟触发——检查 proposal lifecycle "
            "完整性，必要时运行 scripts/rebuild_lifecycle.py --dry-run"
        )
    if kind == "rotation_stall":
        frozen = detail.get("chain_frozen_hours", "?")
        return (
            f"全链约 {frozen}h（周末豁免口径）无 job 执行——先查评审团队列"
            f"是否阻塞（panel_review --status），再查微调度器 cron 是否在跑"
        )
    return "运行 scripts/promote_proposal_to_focus.py apply --proposal <id> 或人工 inspect。"



# 必须存在的 cron 前缀列表
# v6.8.54: 拓扑校验已升级为 lifecycle.cron_manifest 清单对账
# （缺失/重复/调度漂移三类检测）。保留本常量供历史引用与外部脚本兼容，
# 新代码请使用 cron_manifest.CRON_MANIFEST / validate_cron_topology()。
REQUIRED_CRON_PREFIXES = [
    "lc-daily-orchestrate",
    "lc-repair",
    "lc-micro-scheduler",
    "lc-hourly-monitor",
    "lc-prompt-optimize",
    "lc-retrospective",
    "lc-kb-sync",
]

# cron 未执行告警阈值（秒）— 超过此时间未运行则告警
CRON_STALE_THRESHOLD = 2 * 3600  # 2 小时


def _estimate_cron_interval(schedule: str) -> int:
    """从 cron 表达式估算期望执行间隔（秒），用于调度感知的陈旧判定。

    仅覆盖本项目关键 cron 的常见形态：
      - `*/N * * * *` / `*/N * * * 1-5` → N 分钟
      - `0 */N * * *` → N 小时
      - 固定分钟+小时（如 `55 8 * * *`）→ 每日 24h
    无法解析时回退到 CRON_STALE_THRESHOLD（保守）。
    """
    try:
        fields = schedule.split()
        if len(fields) < 5:
            return CRON_STALE_THRESHOLD
        minute, hour = fields[0], fields[1]
        if minute.startswith("*/"):
            return max(60, int(minute[2:]) * 60)
        if hour.startswith("*/"):
            return max(3600, int(hour[2:]) * 3600)
        # 固定分钟+小时 → 每日一次
        return 24 * 3600
    except Exception:
        return CRON_STALE_THRESHOLD


def _cron_runs_today(schedule: str, today=None) -> bool:
    """判断 cron 表达式星期域是否覆盖今天（工作日-only cron 周末免检）。

    背景（v6.9.2）: lc-micro-scheduler 的 `*/15 * * * 1-5` 周末按设计暂停，
    但 _check_cron_status 的陈旧检测此前不感知星期域，从周六起持续误报
    "N小时 未执行"直至周一。本函数解析第 5 域（星期），当天不该执行时
    返回 False，供调用方跳过陈旧/从未执行两项检测。

    Args:
        schedule: cron 表达式（5 域，display 与 expr 形式一致）
        today: 可选日期（date），默认今天；注入用于测试

    Returns:
        今天是否可能执行该 cron；解析失败保守返回 True（照常检测）。
    """
    try:
        fields = schedule.split()
        if len(fields) < 5:
            return True
        dow = fields[4]
        if dow in ("*", "?"):
            return True
        allowed = set()
        for part in dow.split(","):
            part = part.strip()
            if not part or part.startswith(("*", "?")):
                # */N 或通配语义保守视为覆盖
                return True
            if "-" in part:
                lo, hi = part.split("-", 1)
                allowed.update(range(int(lo), int(hi) + 1))
            else:
                allowed.add(int(part))
        if today is None:
            today = datetime.now().date()
        py_wd = today.weekday()                    # Mon=0 .. Sun=6
        cron_wd = 0 if py_wd == 6 else py_wd + 1   # cron: 0/7=周日
        return cron_wd in allowed or (cron_wd == 0 and 7 in allowed)
    except Exception:
        return True


def _check_cron_status() -> Optional[Dict[str, Any]]:
    """检查生命周期 cron 是否完整注册且正常执行。

    三层检测：
    1. 拓扑对账（v6.8.54 升级）：cron_manifest 清单校验缺失/重复/调度漂移
    2. 关键 cron 的 last_run 是否在合理时间范围内
    3. （遗留）worker cron 由 run_repair 清理，不做数量对账
    """
    try:
        import hermes_bridge as hb
        crons = hb.cron_list_profile("linsai")
        cron_names = [c.get("name", "") for c in crons]

        # 1. 拓扑对账（v6.8.54：从 REQUIRED_CRON_PREFIXES 前缀匹配升级为
        # 清单对账，新增调度漂移检测——同名 cron 存在但跑错时间此前不可见）
        from lifecycle.cron_manifest import validate_cron_topology
        missing = []
        duplicated = []
        drifted = []
        for issue in validate_cron_topology(crons):
            if issue["kind"] == "missing":
                missing.append(issue["name"])
            elif issue["kind"] == "duplicate":
                duplicated.append(f"{issue['name']}(×2)")
            elif issue["kind"] == "drift":
                drifted.append(issue["detail"])
        if missing:
            return {
                "type": "cron_missing",
                "missing": missing,
                "message": f"生命周期 cron 缺失: {', '.join(missing)}",
            }
        if duplicated:
            return {
                "type": "cron_duplicate",
                "duplicated": duplicated,
                "message": f"生命周期 cron 重复: {', '.join(duplicated)}",
            }
        if drifted:
            return {
                "type": "cron_drift",
                "drifted": drifted,
                "message": f"cron 调度漂移: {'; '.join(drifted[:3])}",
            }

        # 3. 检查关键 cron 是否长时间未执行
        now_dt = datetime.now(timezone.utc)
        stale_crons = []
        for c in crons:
            name = c.get("name", "")
            # v6.8.34 修复: cron_list_profile 返回键为 last_run（非 last_run_at），
            # 旧代码读 last_run_at 恒为空 → 所有 cron 被误报"从未执行"。
            last_run = c.get("last_run") or c.get("last_run_at", "")
            # 只检查关键调度 cron
            if not any(name.startswith(p) for p in ["lc-micro-scheduler", "lc-daily-orchestrate", "lc-repair"]):
                continue
            schedule = c.get("schedule", "")
            # v6.9.2 修复: 星期域不含今天的 cron（如工作日-only 的
            # `*/15 * * * 1-5` 在周末）当天本就不该执行，跳过两项检测，
            # 避免从周六起持续误报 "N小时 未执行" 直至周一。
            if not _cron_runs_today(schedule):
                continue
            interval = _estimate_cron_interval(schedule)
            if last_run:
                try:
                    last_dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
                    elapsed = (now_dt - last_dt).total_seconds()
                    # v6.8.34 修复: 固定 2h 阈值对每日(24h)/每6h cron 恒误报，
                    # 改为按各 cron 自身调度间隔估算阈值（至少 2h）。
                    threshold = max(CRON_STALE_THRESHOLD, interval * 2)
                    if elapsed > threshold:
                        hours = int(elapsed // 3600)
                        stale_crons.append(f"{name} ({hours}h 未执行)")
                except Exception:
                    pass
            else:
                # 有注册但从未执行过
                # v6.9.2 修复: 固定 10 分钟宽限期对"创建晚于当日调度点"的
                # 每日 cron（昨晚创建、次日首跑）在首跑前持续误报"从未执行"。
                # 实测: lc-daily-orchestrate 08-14 20:13 创建、08-15 08:55 首跑，
                # 23:00 起连续 10 次被误报。改为与陈旧阈值一致的调度感知宽限
                # （interval*2，至少 2h），首跑未到达不再告警；超期未跑仍检出。
                created = c.get("created_at", "")
                if created:
                    try:
                        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        age = (now_dt - created_dt).total_seconds()
                        if age > max(CRON_STALE_THRESHOLD, interval * 2):
                            stale_crons.append(f"{name} (从未执行)")
                    except Exception:
                        pass

        if stale_crons:
            return {
                "type": "cron_stale",
                "stale": stale_crons,
                "message": f"cron 长时间未执行: {'; '.join(stale_crons[:3])}",
            }

    except Exception as e:
        return {
            "type": "cron_check_error",
            "message": f"cron 检查异常: {e}",
        }
    return None


def _check_zero_progress(stats: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """检测全链路零进展：所有课题的 pending > 0 但 done 在近期无变化。

    通过对比看板历史记录判断进展是否停滞。
    """
    try:
        existing = load_json(KANBAN_PATH, default={})
        hourly = existing.get("hourly_monitor", {})
        prev_done = hourly.get("total_done", -1)
        prev_ts = hourly.get("timestamp", "")

        curr_done = sum(s["done"] for s in stats)
        curr_pending = sum(s["pending"] for s in stats)

        # 如果上次看板有记录，且 pending > 0，但 done 完全没变
        if prev_done >= 0 and curr_pending > 0 and curr_done == prev_done:
            # 计算停滞时长
            stale_hours = 0
            if prev_ts:
                try:
                    prev_dt = datetime.fromisoformat(prev_ts.replace("Z", "+00:00"))
                    stale_hours = int((datetime.now(timezone.utc) - prev_dt).total_seconds() // 3600)
                except Exception:
                    pass

            # 停滞超过 3 小时才告警（给正常执行间隔留余量）
            if stale_hours >= 3:
                return {
                    "type": "zero_progress",
                    "prev_done": prev_done,
                    "curr_done": curr_done,
                    "curr_pending": curr_pending,
                    "stale_hours": stale_hours,
                    "message": f"全链路进展停滞 {stale_hours}h: done={curr_done} (无变化), pending={curr_pending}",
                }
    except Exception:
        pass
    return None


def _auto_repair_cron() -> bool:
    """自动修复缺失的 cron 框架。

    调用 --setup-cron-v2 重新安装完整框架。
    返回 True 表示修复成功。
    """
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "proposal_lifecycle.py"), "--setup-cron-v2"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            if _log:
                _log.info("cron 框架自动修复成功")
            return True
        else:
            if _log:
                _log.warning(f"cron 框架自动修复失败: {result.stderr[:200]}")
    except Exception as e:
        if _log:
            _log.warning(f"cron 框架自动修复异常: {e}")
    return False


def _auto_dedup_cron() -> bool:
    """自动清理重复 cron（保留每个框架名最新一份）。

    v6.8.33：检测到 cron_duplicate 告警时调用。注意不能用 _auto_repair_cron
    （它跑 --setup-cron-v2，会在去重后再创建一份，无法收敛到 1）。直接调用
    controller.cleanup_cron_duplicates（按 created_at 保留最新）。
    """
    try:
        from lifecycle.controller import get_controller
        ctrl = get_controller()
        result = ctrl.cleanup_cron_duplicates()
        if _log:
            _log.info(f"cron 自动去重完成: {result}")
        return bool(result)
    except Exception as e:
        if _log:
            _log.warning(f"cron 自动去重异常: {e}")
    return False


def _update_kanban(stats: List[Dict[str, Any]], focus: Optional[Dict[str, Any]]) -> None:
    """更新系统看板 — 合并到 scheduler 的看板格式，不覆盖已有字段。"""
    total_done = sum(s["done"] for s in stats)
    total_failed = sum(s["failed"] for s in stats)
    total_pending = sum(s["pending"] for s in stats)
    total_running = sum(s["running"] for s in stats)

    # 读取现有看板（scheduler 写入的详细格式），保留其结构
    existing = load_json(KANBAN_PATH, default={})

    # 只更新 hourly_monitor 和 updated_at 字段，不破坏 scheduler 的格式。
    # 必须同步刷新 updated_at_local，否则 micro_scheduler 不在工作时隙时该字段
    # 会停滞在上次执行时间（如 12:30:57），令 --kanban CLI / 监控 UI 误判为链路静默。
    now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing["updated_at"] = now_utc()
    existing["updated_at_local"] = now_local
    existing["hourly_monitor"] = {
        "timestamp": now_utc(),
        "total_proposals": len(stats),
        "total_done": total_done,
        "total_failed": total_failed,
        "total_pending": total_pending,
        "total_running": total_running,
    }

    if focus:
        existing["monitor_focus"] = focus

    KANBAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_json(KANBAN_PATH, existing)
    if _log:
        _log.info(f"看板已更新: done={total_done} failed={total_failed} pending={total_pending} running={total_running}")


def _persist_alerts(anomalies: List[Dict[str, Any]]) -> None:
    """v6.8.50: 告警落盘——飞书只是推送渠道，不是存储。

    背景：2026-08-14 04:00 lark-cli exit=3 发送失败，当次告警彻底丢失。
    现在：无论通知成败，告警一律持久化到看板 alerts 区（Web 控制台可见），
    条件消失时标记 resolved_at，保留最近 100 条供溯源。
    """
    try:
        existing = load_json(KANBAN_PATH, default={})
        alerts = existing.get("alerts") or []
        open_by_key = {a["key"]: a for a in alerts if a.get("key") and not a.get("resolved_at")}
        now = now_utc()
        seen_keys = set()
        for a in anomalies:
            key = f"{a.get('type')}:{a.get('proposal_id', '')}:{a.get('job_id', '')}"
            seen_keys.add(key)
            if key in open_by_key:
                open_by_key[key]["last_seen"] = now
                open_by_key[key]["count"] = int(open_by_key[key].get("count", 1)) + 1
                # v7.2.87 修复（healthcheck 焦点②）：存量告警 message 同步刷新，
                # 否则文案永久停留在首次出现时（旧处置建议误导操作）
                new_msg = a.get("message", "")
                if new_msg and new_msg != open_by_key[key].get("message"):
                    open_by_key[key]["message"] = new_msg
            else:
                alerts.append({
                    "key": key,
                    "level": a.get("level", "medium"),
                    "message": a.get("message", ""),
                    "first_seen": now,
                    "last_seen": now,
                    "count": 1,
                    "resolved_at": None,
                })
        # 恢复检测：本轮检查未再出现的未决告警 → 标记恢复时间
        for a in alerts:
            if a.get("key") and not a.get("resolved_at") and a["key"] not in seen_keys:
                a["resolved_at"] = now
        # 只保留最近 100 条（含已恢复），防止无限膨胀
        existing["alerts"] = alerts[-100:]
        save_json(KANBAN_PATH, existing)
    except Exception as e:
        if _log:
            _log.warning(f"告警落盘失败（不影响主流程）: {e}")


def _check_health_signals() -> Optional[Dict[str, Any]]:
    """v6.8.50: 感知层信号检查——捕获"看起来成功的失败"。

    2026-08-14 实例：MiniMax 配额耗尽期间 hermes job 13s"成功"返回 429 文本，
    三小时零告警（success 标记可信假设失效）。本检查经 health_sensor 统一采集：
    空转检测 / API 错误爆发 / 分数骤降 / 熔断状态。
    """
    try:
        from health_sensor import collect_snapshot, evaluate_risks
    except ImportError:
        return None
    try:
        risks = evaluate_risks(collect_snapshot())
    except Exception as e:
        if _log:
            _log.warning(f"健康感知层采集异常（跳过）: {e}")
        return None
    if not risks:
        return None
    # 聚合为单条告警（monitor 的通知链按条目处理）
    if len(risks) == 1:
        return risks[0]
    return {
        "type": "health_signals",
        "level": "high" if any(r.get("level") == "high" for r in risks) else "medium",
        "message": "；".join(r["message"] for r in risks[:4]),
        "_detail": risks,
    }


def _auto_heal_negative_feedback() -> List[Dict[str, Any]]:
    """v6.9.0 R2: 负反馈告警冷却自愈。

    24h 冷却期满自动清除一次（每课题上限 1 次），并做策略降级：
    设置 idea_review_required 退回研究设想评审（重想方向而非原地继续）。
    再触发则不再自动清除，进入人工队列（human_queue 只收自动清除用尽的）。

    v6.10.5: 全局回升解除（先于 24h 冷却判定）——负反馈原因中含
    "writer/critic 全局分数低于 50"（跨课题共享的全局分连坐类）且对应
    agent 全局分已回升至 50 及以上时：原因已事实消失，自动移除；
    若无剩余原因则整条告警解除。不占 auto_clear_count 额度、不降级
    idea_review_required（被连坐非课题自身问题，不应惩罚性退回设想评审）。
    """
    healed: List[Dict[str, Any]] = []
    try:
        from proposal_lifecycle import ProposalLifecycle
        from lifecycle.utils import (
            global_recovery_clear_plan,
            should_auto_clear_negative_feedback,
        )

        lc = ProposalLifecycle()
        state = lc._load_state()
        dirty = False
        now = datetime.now(timezone.utc)

        # v6.10.5: 全局 agent 分数快照（回升判定的数据源）
        agent_scores: Dict[str, Any] = {}
        try:
            agent_scores = load_json(
                PROJECT_ROOT / "memory" / "agent-scores.json", default={}
            ) or {}
        except Exception:
            agent_scores = {}

        for pid, ps in (state.get("proposals") or {}).items():
            if not isinstance(ps, dict) or ps.get("status") != "optimizing":
                continue
            if not ps.get("negative_feedback_alert"):
                continue
            # --- v6.10.5: 全局回升解除（连坐告警专用路径） ---
            plan = global_recovery_clear_plan(ps, agent_scores)
            if plan is not None:
                if plan.get("action") == "clear":
                    lc.clear_negative_feedback(
                        pid,
                        reason="auto-heal：全局 agent 分数回升，连坐告警解除",
                    )
                    healed.append({
                        "proposal_id": pid,
                        "kind": "global_recovery_clear",
                        "reasons": (ps.get("negative_feedback_reasons") or [])[:3],
                    })
                    if _log:
                        _log.info(
                            f"[{pid}] 负反馈告警解除（全局 agent 分回升，"
                            f"连坐原因消失；不占自愈额度）"
                        )
                    continue
                if plan.get("action") == "trim":
                    fresh = lc._get_proposal_state(pid) or ps
                    fresh["negative_feedback_reasons"] = plan.get("remaining") or []
                    lc._set_proposal_state(pid, fresh)
                    healed.append({
                        "proposal_id": pid,
                        "kind": "global_recovery_trim",
                        "reasons": plan.get("remaining", [])[:3],
                    })
                    if _log:
                        _log.info(
                            f"[{pid}] 负反馈告警裁剪（全局原因恢复，"
                            f"保留课题自身原因：{plan.get('remaining')}）"
                        )
                    # 告警继续挂（仍有自身原因），走下方补戳/冷却逻辑
            # --- 原有 24h 冷却路径 ---
            # 遗留数据无时间戳：补戳后从现在起算冷却
            if not ps.get("negative_feedback_at"):
                ps["negative_feedback_at"] = now_utc()
                dirty = True
                continue
            if not should_auto_clear_negative_feedback(ps, now):
                continue
            reasons = ps.get("negative_feedback_reasons") or []
            clear_res = lc.clear_negative_feedback(
                pid, reason="auto-heal：24h 冷却期满自动清除"
            )
            fresh = lc._get_proposal_state(pid) or ps
            fresh["negative_feedback_auto_clear_count"] = int(
                fresh.get("negative_feedback_auto_clear_count", 0)
            ) + 1
            fresh["idea_review_required"] = True
            fresh["idea_review_required_reason"] = (
                "负反馈自动清除降级：退回研究设想评审；" + "；".join(reasons)[:120]
            )
            lc._set_proposal_state(pid, fresh)
            healed.append({"proposal_id": pid, "reasons": reasons[:3]})
            if _log:
                _log.info(
                    f"[{pid}] 负反馈告警自动清除（24h 冷却期满），"
                    f"策略降级为研究设想评审；clear={clear_res.get('success', True)}"
                )
        if dirty:
            lc._save_state(state)
    except Exception as exc:
        if _log:
            _log.warning(f"负反馈自愈失败: {exc}")
    return healed


def _run_human_queue_step() -> Optional[Dict[str, Any]]:
    """v6.9.0 R6: 聚合待人工队列快照（>72h 催办由调用方生成告警）。"""
    try:
        from human_queue import run_human_queue

        return run_human_queue(persist=True)
    except Exception as exc:
        if _log:
            _log.warning(f"待人工队列聚合失败: {exc}")
        return None


def _check_r1_start_failures() -> List[Dict[str, Any]]:
    """v7.1.8: 读取 micro_scheduler 写入的 r1-start-alerts 缓存并转换为
    monitor 异常条目。micro_scheduler 每 tick 已做去重（6h dedup），
    monitor 端走标准的 24h dedup + 夜间静默 + 飞书链路。

    返回 anomaly 列表（每个待发送告警一条），告警内容包含课题 ID、
    elapsed_hours、jobs_pending，便于人工判断启动失败根因。
    """
    anomalies: List[Dict[str, Any]] = []
    if not R1_START_ALERT_PATH.exists():
        return anomalies
    try:
        cache = load_json(R1_START_ALERT_PATH, default={"alerts": {}})
    except Exception as e:
        if _log:
            _log.debug(f"[r1-start] 读告警缓存失败: {e}")
        return anomalies

    alerts = cache.get("alerts", {})
    if not alerts:
        return anomalies

    # 只把"最新发送时间 ≤ dedup 窗口"的告警再推一次（让 lifecycle_monitor
    # 的 _should_notify 控制节奏）。micro_scheduler 6h dedup + monitor 24h
    # dedup 双重去重，正常情况同课题每天最多 1 次告警。
    from datetime import timezone
    now_dt = datetime.now(timezone.utc)
    DEDUP_HOURS = 6  # 与 micro_scheduler R1_START_ALERT_DEDUP_HOURS 对齐
    for pid, info in alerts.items():
        last_sent = info.get("last_sent", "")
        if last_sent:
            try:
                last_dt = datetime.fromisoformat(last_sent.replace("Z", "+00:00"))
                if (now_dt - last_dt).total_seconds() > DEDUP_HOURS * 3600:
                    # 超过 dedup 窗口的不再推送（micro_scheduler 会在下次
                    # tick 重新写入 fresh last_sent）
                    continue
            except Exception:
                pass

        elapsed = info.get("elapsed_hours", 0)
        jobs_pending = info.get("jobs_pending", 0)
        jobs_total = info.get("jobs_total", 0)
        last_score = info.get("last_score", 0.0)
        anomalies.append({
            "type": "r1_start_failure",
            "proposal_id": pid,
            "job_id": "r1_startup",
            "message": (
                f"r1 启动失败：{pid[:40]} 进入 optimizing 已 {elapsed:.1f}h，"
                f"jobs {jobs_pending}/{jobs_total} 全部 pending，"
                f"0 推进（last_score={last_score:.2f}）"
            ),
        })

    return anomalies


def _check_new_panel_requests() -> List[Dict[str, Any]]:
    """v7.2.0: 新评审团请求即时通知——r3/平台带触发 panel_review_requested 后
    立即提醒（不等 72h escalate 催办），避免课题静默挂队 3 天无人知晓。

    触发条件：optimizing + panel_review_requested + panel_requested_at
    距今 <= 2h。monitor 24h dedup 保证同一课题只提醒一次。
    """
    anomalies: List[Dict[str, Any]] = []
    try:
        from proposal_lifecycle import ProposalLifecycle
        pl = ProposalLifecycle()
        from datetime import timezone
        now_dt = datetime.now(timezone.utc)
        for p in pl.list_by_status("optimizing"):
            pid = p["proposal_id"]
            ps = pl._get_proposal_state(pid) or {}
            if not ps.get("panel_review_requested"):
                continue
            requested_at = ps.get("panel_requested_at", "")
            if not requested_at:
                continue
            try:
                req_dt = datetime.fromisoformat(requested_at.replace("Z", "+00:00"))
            except Exception:
                continue
            elapsed_h = (now_dt - req_dt).total_seconds() / 3600.0
            if elapsed_h > 2.0:
                continue  # 非新请求，交给 72h escalate 链路
            reason = (ps.get("panel_review_reason") or "")[:80]
            rounds = ps.get("optimization_rounds", 0)
            score = ps.get("last_score", 0.0)
            anomalies.append({
                "type": "panel_request_new",
                "proposal_id": pid,
                "job_id": f"r{rounds}",
                "message": (
                    f"评审团请求：{pid[:40]} r{rounds}（{score:.2f}）"
                    f"已转评审团队列——{reason}。请在 CoPilot 会话发起亲审"
                    f"（panel_review --status 查看）"
                ),
            })
    except Exception as e:
        if _log:
            _log.debug(f"[panel-request] 扫描异常: {e}")
    return anomalies


def run_monitor(dry_run: bool = False) -> Dict[str, Any]:
    """执行一次监控周期。

    Args:
        dry_run: True 时只检查不发飞书通知

    Returns:
        {success, stats, anomalies, notified}
    """
    if _log:
        _log.info("=== 每小时监控启动 ===")

    # v6.8.54: 启动即清理过期告警缓存条目（此前仅在有新告警写入时顺带
    # 清理，无新告警时过期条目无限滞留，构成展示噪音）
    try:
        _cache = _load_alert_cache()
        _removed = _prune_alert_cache(_cache)
        if _removed > 0:
            _save_alert_cache(_cache)
            if _log:
                _log.info(f"清理过期告警缓存 {_removed} 条")
    except Exception:
        pass

    # 1. 检查课题状态（v7.3.44: dry_run 下消化只决策不落盘）
    stats, anomalies = _check_proposals(dry_run=dry_run)

    # 2. 检查 cron 状态
    cron_issue = _check_cron_status()
    if cron_issue:
        anomalies.append(cron_issue)
        # cron 缺失/重复/调度漂移时自动修复（不等待人工介入）
        # v6.8.54: 漂移加入自愈清单——setup 的幂等 helper 会删除
        # 调度不一致的旧实例后重建，漂移可被 setup 修复
        _ctype = cron_issue.get("type")
        if _ctype in ("cron_missing", "cron_duplicate", "cron_drift") and not dry_run:
            # 重复 → 直接去重（setup 会再创建，不能用 _auto_repair_cron）
            repaired = _auto_dedup_cron() if _ctype == "cron_duplicate" else _auto_repair_cron()
            if repaired:
                # 修复后重新检查
                recheck = _check_cron_status()
                if not recheck:
                    if _log:
                        _log.info("cron 框架自动修复成功，告警降级为信息")
                    cron_issue["auto_repaired"] = True
                    cron_issue["message"] = f"[已自愈] {cron_issue['message']}"
                else:
                    if _log:
                        _log.warning(f"cron 框架自动修复后仍有问题: {recheck}")

    # 3. 检查全链路零进展（cron 存在但 job 不推进）
    progress_issue = _check_zero_progress(stats)
    if progress_issue:
        anomalies.append(progress_issue)

    # 3.5 v6.8.50: 感知层信号检查（空转/API 错误爆发/分数骤降/熔断状态）
    health_issue = _check_health_signals()
    if health_issue:
        anomalies.append(health_issue)

    # 3.6 v6.9.0 R2: 负反馈告警冷却自愈（自愈信息以告警形式留痕）
    healed_items = _auto_heal_negative_feedback()

    # v7.1.8: r1 启动失败告警——读取 micro_scheduler 写入的 r1-start-alerts
    # 缓存（6h dedup），转 anomaly 走标准飞书链路
    r1_anomalies = _check_r1_start_failures()
    anomalies.extend(r1_anomalies)

    # v7.2.0: 新评审团请求即时通知（r3/平台带触发后 2h 内提醒一次，
    # 不等 72h escalate）
    panel_new = _check_new_panel_requests()
    anomalies.extend(panel_new)
    for h in healed_items:
        anomalies.append(
            {
                "type": "auto_healed_negative_feedback",
                "proposal_id": h["proposal_id"],
                "message": f"[已自愈] {h['proposal_id']} 负反馈告警 24h 冷却期满自动清除，策略降级为研究设想评审",
            }
        )

    # 3.7 v6.9.0 R6: 待人工队列聚合 + 超 72h 催办
    human_queue_summary: Optional[Dict[str, Any]] = None
    queue_result = _run_human_queue_step()
    if queue_result:
        human_queue_summary = queue_result.get("summary")
        type_names = {
            "review": "验收",
            "activate": "激活",
            "negative_feedback": "负反馈",
            # v6.10.15: 补齐新队列类型的催办标签（原 fallback 显英文 type）
            "cluster_stale": "簇裁决",
            "panel_request": "评审团",
            "strategy": "策略",
            # v7.2.55: 输入端熔断入队（改进项 p）后的催办标签
            "input_broken": "输入端熔断",
        }
        for item in queue_result.get("items", []):
            if not item.get("escalate"):
                continue
            label = type_names.get(item["type"], item["type"])
            anomalies.append(
                {
                    "type": "human_queue_escalation",
                    "proposal_id": item["proposal_id"],
                    # 去重键含天数桶：同一事项每天最多催办一次
                    "job_id": str(int((item.get("waiting_hours") or 0) // 24)),
                    "message": (
                        f"⏰ 待人工处理超 72h：{label}「{item['title'][:28]}」"
                        f"已等待 {(item.get('waiting_hours') or 0):.0f}h · "
                        f"建议：{item['suggested_action'][:50]}"
                    ),
                }
            )

    # 4. 获取当前聚焦
    focus_info: Optional[Dict[str, Any]] = None
    try:
        from lifecycle.controller import get_controller
        ctrl = get_controller()
        focus = ctrl.get_current_focus()
        if focus:
            focus_info = {
                "proposal_id": focus.get("focus_proposal"),
                "slot": focus.get("slot"),
                "next_job": focus.get("next_job", {}).get("job_id"),
            }
    except Exception:
        pass

    # 5. 更新看板 + 告警落盘（先落盘再通知，通知失败不丢告警）
    _update_kanban(stats, focus_info)
    _persist_alerts(anomalies)

    # 6. 异常通知（去重）
    notified: List[str] = []
    if anomalies and not dry_run:
        # 汇总告警内容
        alert_lines: List[str] = []
        alert_keys: List[str] = []
        alert_messages: List[str] = []
        # v6.9.68 夜间静默：异常照常入缓存与看板，但不发送飞书——
        # 次日首个工作时段的检测自然发出（_should_notify 24h 冷却未耗尽
        # 则由当日首次非静默运行补发同批异常）
        quiet = _in_quiet_hours()
        if quiet and _log:
            _log.info("夜间静默窗口（22:00-08:00），本次异常只入缓存不发送通知")
        for a in anomalies:
            alert_key = f"{a.get('type')}:{a.get('proposal_id', '')}:{a.get('job_id', '')}"
            if _should_notify(alert_key):
                alert_lines.append(f"- {a['message']}")
                alert_keys.append(alert_key)
                alert_messages.append(a["message"])
                if not quiet:
                    notified.append(alert_key)

        if alert_lines:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            title = f"⚠️ 林赛全链路异常告警 ({now_str})"
            content = "\n".join(alert_lines[:10])
            if len(alert_lines) > 10:
                content += f"\n... 还有 {len(alert_lines) - 10} 条"

            # v6.8.17 修复：只有飞书通知真正送达时才标记告警为已通知，
            # 否则 lark-cli 不可用时同一异常会在 4h 去重窗口内被"自我吞掉"，
            # 用户永远收不到真实告警。
            # v6.9.82 修复：夜间静默须同时拦截发送与标记——原实现只拦
            # notified 计数，_send_feishu 照发（08-30/31 夜间 22/23/00/03/07
            # 共 5 次实证），且发送成功后 _mark_notified 消耗 24h 冷却，
            # 次日工作时段也不会补发，与 v6.9.68"只入缓存不发送"设计相悖。
            # 不标记则次日首个非静默运行经 _should_notify 自然补发同批异常。
            if not quiet and _send_feishu(title, content):
                for key, msg in zip(alert_keys, alert_messages):
                    _mark_notified(key, msg)

    result = {
        "success": True,
        "timestamp": now_utc(),
        "stats": stats,
        "anomaly_count": len(anomalies),
        "notified_count": len(notified),
        "focus": focus_info,
        "human_queue": human_queue_summary,
        "auto_healed_negative_feedback": len(healed_items),
    }

    if _log:
        _log.info(
            f"监控完成: {len(stats)} 个课题, {len(anomalies)} 个异常, "
            f"通知 {len(notified)} 条"
        )

    return result


def _self_check() -> None:
    """自检。"""
    print("=== lifecycle_monitor 自检 ===")
    result = run_monitor(dry_run=True)
    assert result["success"], "监控执行失败"
    print(f"✓ 监控执行成功")
    print(f"  课题数: {len(result['stats'])}")
    print(f"  异常数: {result['anomaly_count']}")
    for s in result["stats"]:
        print(f"  {s['proposal_id'][:40]}: done={s['done']} failed={s['failed']} pending={s['pending']} ({s['progress_pct']}%)")
    print(f"✓ lifecycle_monitor 自检通过")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="每小时全链路监控与异常告警")
    parser.add_argument("--dry-run", action="store_true", help="不发飞书通知")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return 0

    result = run_monitor(dry_run=args.dry_run)
    # 打印摘要到 stdout（cron 日志可见）
    print(f"[lifecycle-monitor] {result['timestamp']}")
    print(f"  课题: {len(result['stats'])}, 异常: {result['anomaly_count']}, 通知: {result['notified_count']}")
    for s in result["stats"]:
        print(f"  {s['proposal_id'][:40]}: done={s['done']} failed={s['failed']} pending={s['pending']} ({s['progress_pct']}%)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
