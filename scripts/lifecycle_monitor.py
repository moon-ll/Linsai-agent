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
        # v6.9.31 修复: 停滞时钟改用「job 级最后活动」（任一 job 的
        # finished_at/started_at 最大值）——旧口径读 proposal 的 updated_at，
        # 会被 repair 重置 / cron 失败记录 / stale 清理等非执行写入刷新，
        # 掩盖真实停滞（08-21 bsv 实证：updated_at 距 26.1h、job 实际停滞
        # 87.7h，48h 告警永不触发）。无 job 时间戳时回退 updated_at。
        STALL_THRESHOLD_HOURS = 48
        try:
            job_activity = ""
            for j in jobs:
                t = j.get("finished_at") or j.get("started_at") or ""
                if t > job_activity:
                    job_activity = t
            last_activity = job_activity or p.get("updated_at", "")
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

    背景（v6.9.2）: lc-micro-scheduler 的 `*/5 * * * 1-5` 周末按设计暂停，
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
            # `*/5 * * * 1-5` 在周末）当天本就不该执行，跳过两项检测，
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
    """
    healed: List[Dict[str, Any]] = []
    try:
        from proposal_lifecycle import ProposalLifecycle
        from lifecycle.utils import should_auto_clear_negative_feedback

        lc = ProposalLifecycle()
        state = lc._load_state()
        dirty = False
        now = datetime.now(timezone.utc)
        for pid, ps in (state.get("proposals") or {}).items():
            if not isinstance(ps, dict) or ps.get("status") != "optimizing":
                continue
            if not ps.get("negative_feedback_alert"):
                continue
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

    # 1. 检查课题状态
    stats, anomalies = _check_proposals()

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
        type_names = {"review": "验收", "activate": "激活", "negative_feedback": "负反馈"}
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
