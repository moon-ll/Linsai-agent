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
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from common import now_utc, load_json, save_json  # noqa: E402

# lark-cli 路径（TRAE 插件安装位置）
LARK_CLI = str(Path.home() / ".trae-cn" / "plugins" / "trae-remote-official" / "lark" / "1.0.3" / "bin" / "lark-cli")

# 告警去重缓存
ALERT_CACHE_PATH = PROJECT_ROOT / "memory" / "monitor-alert-cache.json"

# 系统看板路径
KANBAN_PATH = PROJECT_ROOT / "memory" / "system-kanban.json"

# 告警去重窗口（秒）
ALERT_DEDUP_WINDOW = 4 * 3600  # 4 小时

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


def _mark_notified(alert_key: str, message: str) -> None:
    """记录告警已通知。"""
    cache = _load_alert_cache()
    cache.setdefault("alerts", {})[alert_key] = {
        "last_sent": now_utc(),
        "message": message[:200],
    }
    # 清理过期记录
    cutoff = datetime.now().timestamp() - ALERT_DEDUP_WINDOW
    for key in list(cache.get("alerts", {}).keys()):
        info = cache["alerts"][key]
        sent = info.get("last_sent", "")
        if sent:
            try:
                dt = datetime.fromisoformat(sent.replace("Z", "+00:00"))
                if dt.timestamp() < cutoff:
                    del cache["alerts"][key]
            except Exception:
                pass
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


def _check_proposals() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """检查所有 optimizing 课题状态。

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

    for p in proposals:
        pid = p["proposal_id"]
        rounds = p.get("optimization_rounds", 0)
        score = p.get("last_score", 0)
        jobs = ctrl._get_jobs(pid)

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
        try:
            kanban_data = load_json(KANBAN_PATH, default={})
            history = kanban_data.get("execution_history", [])
            # 只看最近 2 小时的记录
            from datetime import timezone
            now_dt = datetime.now(timezone.utc)
            recent = []
            for h in history:
                try:
                    h_dt = datetime.fromisoformat(h.get("at", "").replace("Z", "+00:00"))
                    if (now_dt - h_dt).total_seconds() < 7200 and not h.get("success", True):
                        recent.append(h)
                except Exception:
                    pass

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

        # v6.8.16 改进2: 停滞课题检测
        # v6.8.27 修复: 旧版要求 done==0 才触发，但大多数停滞课题已有部分 done job
        # 改为：只要 updated_at 超 48h 且当前还有 pending job（说明没跑完就卡了）
        STALL_THRESHOLD_HOURS = 48
        try:
            last_activity = p.get("updated_at", "")
            if last_activity:
                last_dt = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
                hours_since = (datetime.now(timezone.utc) - last_dt).total_seconds() // 3600
                pending_count = total - done
                if hours_since >= STALL_THRESHOLD_HOURS and pending_count > 0:
                    anomalies.append({
                        "type": "stalled",
                        "proposal_id": pid,
                        "hours": int(hours_since),
                        "done": done,
                        "total": total,
                        "pending": pending_count,
                        "message": (
                            f"课题 {pid[:40]} 停滞 {int(hours_since)}h，"
                            f"{done}/{total} job 完成，{pending_count} 个 pending 未执行。"
                            f"建议检查 cron 是否正常或手动触发微调度器。"
                        ),
                    })
        except Exception:
            pass

    # v6.8.27: 输入端熔断检测——从周末任务提升为每小时检查
    # 连续 2 周 weekend input 的 ideas_count=0 → input_pipeline_broken
    try:
        weekend_path = PROJECT_ROOT / "memory" / "weekend-jobs.json"
        if weekend_path.exists():
            import json
            weekend_data = json.loads(weekend_path.read_text(encoding="utf-8"))
            weekend_input = weekend_data.get("weekend_input", {})
            started_at = weekend_input.get("started_at", "")
            ideas_count = 0
            result = weekend_input.get("result", {})
            if isinstance(result, dict):
                ideas_count = result.get("ideas_count", 0)
            # 如果最近一次 weekend input 无新设想且距上次执行超过 7 天
            if started_at and ideas_count == 0:
                input_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                days_since = (datetime.now(timezone.utc) - input_dt).total_seconds() // 86400
                if days_since >= 7:
                    anomalies.append({
                        "type": "input_pipeline_broken",
                        "message": (
                            f"输入端连续 {int(days_since)} 天未产生新研究设想，"
                            f"上次 weekend input 于 {started_at}。"
                            f"建议检查 idea_generator prompt 或 hermes researcher profile 状态。"
                        ),
                    })
    except Exception:
        pass

    return stats, anomalies


# 必须存在的 cron 前缀列表
REQUIRED_CRON_PREFIXES = [
    "lc-daily-orchestrate",
    "lc-repair",
    "lc-micro-scheduler",
    "lc-hourly-monitor",
    "lc-prompt-optimize",
    "lc-retrospective",
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


def _check_cron_status() -> Optional[Dict[str, Any]]:
    """检查生命周期 cron 是否完整注册且正常执行。

    三层检测：
    1. 必需 cron 前缀是否全部存在
    2. 每个 cron 的 last_run_at 是否在合理时间范围内
    3. worker cron 数量是否与 optimizing 课题数匹配
    """
    try:
        import hermes_bridge as hb
        crons = hb.cron_list_profile("linsai")
        cron_names = [c.get("name", "") for c in crons]

        # 1. 检查必需前缀
        missing = []
        for prefix in REQUIRED_CRON_PREFIXES:
            if not any(name.startswith(prefix) for name in cron_names):
                missing.append(prefix)

        # 2. 检查 weekend cron
        has_weekend = any(name.startswith("lc-weekend-") for name in cron_names)
        if not has_weekend:
            missing.append("lc-weekend-*")

        if missing:
            return {
                "type": "cron_missing",
                "missing": missing,
                "message": f"生命周期 cron 缺失: {', '.join(missing)}",
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
            if last_run:
                try:
                    last_dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
                    elapsed = (now_dt - last_dt).total_seconds()
                    # v6.8.34 修复: 固定 2h 阈值对每日(24h)/每6h cron 恒误报，
                    # 改为按各 cron 自身调度间隔估算阈值（至少 2h）。
                    interval = _estimate_cron_interval(c.get("schedule", ""))
                    threshold = max(CRON_STALE_THRESHOLD, interval * 2)
                    if elapsed > threshold:
                        hours = int(elapsed // 3600)
                        stale_crons.append(f"{name} ({hours}h 未执行)")
                except Exception:
                    pass
            else:
                # 有注册但从未执行过
                # 排除刚创建的 cron（created_at 在 10 分钟内）
                created = c.get("created_at", "")
                if created:
                    try:
                        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        age = (now_dt - created_dt).total_seconds()
                        if age > 600:
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


def run_monitor(dry_run: bool = False) -> Dict[str, Any]:
    """执行一次监控周期。

    Args:
        dry_run: True 时只检查不发飞书通知

    Returns:
        {success, stats, anomalies, notified}
    """
    if _log:
        _log.info("=== 每小时监控启动 ===")

    # 1. 检查课题状态
    stats, anomalies = _check_proposals()

    # 2. 检查 cron 状态
    cron_issue = _check_cron_status()
    if cron_issue:
        anomalies.append(cron_issue)
        # cron 缺失时自动修复（不等待人工介入）
        if cron_issue.get("type") == "cron_missing" and not dry_run:
            repaired = _auto_repair_cron()
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

    # 5. 更新看板
    _update_kanban(stats, focus_info)

    # 6. 异常通知（去重）
    notified: List[str] = []
    if anomalies and not dry_run:
        # 汇总告警内容
        alert_lines: List[str] = []
        alert_keys: List[str] = []
        alert_messages: List[str] = []
        for a in anomalies:
            alert_key = f"{a.get('type')}:{a.get('proposal_id', '')}:{a.get('job_id', '')}"
            if _should_notify(alert_key):
                alert_lines.append(f"- {a['message']}")
                alert_keys.append(alert_key)
                alert_messages.append(a["message"])
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
            if _send_feishu(title, content):
                for key, msg in zip(alert_keys, alert_messages):
                    _mark_notified(key, msg)

    result = {
        "success": True,
        "timestamp": now_utc(),
        "stats": stats,
        "anomaly_count": len(anomalies),
        "notified_count": len(notified),
        "focus": focus_info,
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
