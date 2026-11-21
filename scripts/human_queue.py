#!/usr/bin/env python3
"""待人工处理队列聚合器（v6.9.0 R6）。

把散落在各状态里"等人"的事项聚合成单一队列，每项附 AI 建议动作与
等待时长，超过 72h 标记催办（由 lifecycle_monitor 通知）：

  - pending_review 课题 → 建议动作取自验收决策包预审（v6.9.0 R1）
  - drafts 课题        → 建议动作取自立项决策包推荐（v6.9.0 R4）
  - 负反馈告警课题     → 仅在自动清除已用尽后进入队列（v6.9.0 R2 降噪）
  - 评审团请求（panel_request，v6.10.14）/ 策略（strategy，v6.9.58）
    / 簇裁决（cluster_stale，v6.10.7）
  - 输入端熔断（input_broken，v7.2.55——补齐 monitor 告警的队列来源）
  - 配额/重评门复核（quota_review，v7.3.28——持久源
    memory/config/quota-reviews.json，不随快照重写丢失）

用法：
    python3 scripts/human_queue.py            # 聚合并打印
    python3 scripts/human_queue.py --self-check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common import load_json, now_utc, save_json  # noqa: E402
from paths import MEMORY_DIR  # noqa: E402

try:
    from logger import get_logger
    _log = get_logger("human_queue")
except Exception:  # pragma: no cover
    _log = None

HUMAN_QUEUE_PATH = MEMORY_DIR / "human-queue.json"
"""队列快照（控制台 /api/console/human-queue 与 monitor 共用）。"""

WEEKEND_INPUT_DIR = MEMORY_DIR / "weekend-input"
"""输入端周末产物目录（input_broken 检测数据源，测试可注入覆盖）。"""

QUOTA_REVIEWS_PATH = MEMORY_DIR / "config" / "quota-reviews.json"
"""配额/重评门复核待办持久源（v7.3.28）。

与 human-queue.json 派生快照的本质区别：本文件是人工登记的**真相源**，
聚合器每次重写快照都从这里重新读取，因此条目不会因整文件覆盖而丢失。
结构：{"items": [{id, title, criteria, decided_basis, due_date, status, notes}]}。
status 取 pending / done / skipped，仅 pending 入队。"""

ESCALATE_AFTER_H = 72.0
"""催办阈值：等待超过 72 小时标记 escalate，由 monitor 飞书通知。"""

VERDICT_ACTIONS = {
    "approve_lean": "打开审核会话验收（预审建议通过，可一键采纳）",
    "attention": "打开审核会话验收（预审需人工裁量）",
    "reject_lean": "打开审核会话验收（预审建议退回）",
}


def _dt_from_iso(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def _hours_since(value: Any, now: datetime) -> Optional[float]:
    dt = _dt_from_iso(value)
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return round((now - dt).total_seconds() / 3600.0, 1)


def _pending_review_since(prop_state: Dict[str, Any]) -> Optional[str]:
    """从 transition_history 找最近一次进入 pending_review 的时间。"""
    for entry in reversed(prop_state.get("transition_history") or []):
        if isinstance(entry, dict) and entry.get("to") == "pending_review":
            return entry.get("at")
    return prop_state.get("updated_at")


def collect_human_queue(
    proposals: Optional[Dict[str, Dict[str, Any]]] = None,
    now: Optional[datetime] = None,
    escalate_after_h: float = ESCALATE_AFTER_H,
) -> Dict[str, Any]:
    """聚合待人工事项。proposals/now 可注入（测试零污染）。"""
    if proposals is None:
        proposals = (
            load_json(
                Path(__file__).resolve().parent.parent / "research_proposals" / "_lifecycle.json",
                default={"proposals": {}},
            ).get("proposals")
            or {}
        )
    if now is None:
        now = datetime.now(timezone.utc)

    items: List[Dict[str, Any]] = []

    for pid, ps in (proposals or {}).items():
        if not isinstance(ps, dict):
            continue
        status = ps.get("status")

        if status == "pending_review":
            waiting = _hours_since(_pending_review_since(ps), now)
            dossier = ps.get("review_dossier") or {}
            verdict = dossier.get("pre_review_verdict")
            action = VERDICT_ACTIONS.get(verdict, "打开审核会话验收")
            items.append(
                {
                    "type": "review",
                    "proposal_id": pid,
                    "title": ps.get("title", pid),
                    "waiting_hours": waiting,
                    "suggested_action": action,
                    "pre_review_verdict": verdict,
                    "can_adopt": bool(dossier.get("can_adopt")),
                    "last_score": ps.get("last_monitor_score"),
                }
            )

        elif status == "drafts":
            waiting = _hours_since(ps.get("created_at") or ps.get("updated_at"), now)
            idea = ps.get("idea_dossier") or {}
            rec = idea.get("recommendation")
            # v7.3.10: 用户已裁决 hold 的草案不再计入"待激活"催办链——
            # 保留队列可见性（记录裁决 + 重启条件），escalate 恒为 False。
            decision = ps.get("activation_decision") or {}
            if decision.get("decision") == "hold":
                items.append(
                    {
                        "type": "activate_hold",
                        "proposal_id": pid,
                        "title": ps.get("title", pid),
                        "waiting_hours": waiting,
                        "suggested_action": "保持搁置（已裁决 hold），满足重评门后再提交激活",
                        "recommendation": rec,
                        "decision": "hold",
                        "decision_reason": decision.get("reason", ""),
                        "reactivation_gate": decision.get("reactivation_gate") or {},
                        "hold": True,
                    }
                )
            else:
                action = (
                    f"激活进入优化（预审建议：{rec}）"
                    if rec
                    else "激活进入优化或保持搁置"
                )
                items.append(
                    {
                        "type": "activate",
                        "proposal_id": pid,
                        "title": ps.get("title", pid),
                        "waiting_hours": waiting,
                        "suggested_action": action,
                        "recommendation": rec,
                    }
                )

        elif status == "optimizing" and ps.get("scheduler_frozen") and "转人工" in str(ps.get("scheduler_frozen_reason") or ""):
            # v7.3.83: 平台 park 转人工——高位平台且手册门未过线自动冻结的
            # 课题（completion._park_if_gate_blocked 置位），等人裁决采纳/
            # 解冻。与 executor 写冲突冻结（reason 无"转人工"）区分，
            # 后者走链路自愈不进队列。
            frozen_reason = str(ps.get("scheduler_frozen_reason") or "")
            items.append(
                {
                    "type": "parked",
                    "proposal_id": pid,
                    "title": ps.get("title", pid),
                    "waiting_hours": _hours_since(ps.get("updated_at"), now),
                    "suggested_action": "打开审核会话采纳归档，或手册过线后解冻继续轮转",
                    "reason": frozen_reason[:120],
                    "last_score": ps.get("last_score", 0),
                }
            )

        elif status == "optimizing" and ps.get("panel_review_requested"):
            # v6.10.14 第六类：平台期课题转评审团——0.70-0.85 主平台带
            # 连续 4 轮无边际提升，自动循环止损暂停，等评审团深度修改
            # v6.10.15: waiting_hours（panel_requested_at 起算，旧数据
            # 回退 updated_at）→ 参与 72h escalate 催办链
            reason = ps.get("panel_review_reason", "主平台带")
            waiting = _hours_since(
                ps.get("panel_requested_at") or ps.get("updated_at"), now)
            items.append(
                {
                    "type": "panel_request",
                    "proposal_id": pid,
                    "title": ps.get("title", pid),
                    "waiting_hours": waiting,
                    "suggested_action": "运行评审团模式深度修改，完成后清除 panel_request 标志",
                    "reason": reason[:120],
                    "last_score": ps.get("last_score", 0),
                }
            )

        elif status == "optimizing" and ps.get("a_gate_panel_request"):
            # v7.3.42 用户裁决：A 通道析取提醒——任一模块 ≥0.85 且无
            # critical/high 时登记一条"建议专家评审"。不晋级、不拦路，
            # 与 panel_review_requested（平台期深度修改）语义区分。
            hint = ps.get("a_gate_panel_request") or {}
            try:
                _hit = float(hint.get("score") or 0.0)
            except (TypeError, ValueError):
                _hit = 0.0
            items.append(
                {
                    "type": "panel_request",
                    "source": "a_gate",
                    "proposal_id": pid,
                    "title": ps.get("title", pid),
                    "waiting_hours": _hours_since(
                        hint.get("created_at") or ps.get("updated_at"), now),
                    "suggested_action": (
                        f"建议专家评审：{hint.get('module', '?')} 判定分 "
                        f"{_hit:.2f}（≥0.85），评审报告 {hint.get('report_path', '?')}"
                    ),
                    "hit_module": hint.get("module"),
                    "hit_score": round(_hit, 3),
                    "report_path": hint.get("report_path"),
                }
            )

        elif status == "optimizing" and ps.get("negative_feedback_alert"):
            # R2 降噪：自动清除尚未用尽且冷却中的告警不进人工队列
            auto_used = int(ps.get("negative_feedback_auto_clear_count", 0)) >= 1
            if auto_used:
                waiting = _hours_since(ps.get("negative_feedback_at"), now)
                reasons = ps.get("negative_feedback_reasons") or []
                items.append(
                    {
                        "type": "negative_feedback",
                        "proposal_id": pid,
                        "title": ps.get("title", pid),
                        "waiting_hours": waiting,
                        "suggested_action": "人工清除负反馈告警（自动清除已用尽）",
                        "reasons": reasons[:3],
                    }
                )

        # v7.2.66 定案1 三检查点副驾制——大纲检查点（15 分钟级）：
        # 首轮优化完成后课题的方向/大纲交用户过目（Agent Laboratory 实证
        # 前端人工介入优于全自动 +0.58/10；本系统唯一非空转裁决=方向修正
        # berry 案例）。非阻塞：课题继续轮转，用户反馈经 06_feedback 回注；
        # outline_confirmed=True 后不再出现。
        #
        # v7.3.43（BUG-45）：本条**移出 elif 链**改为独立判定。
        # 原位置（elif status=="optimizing" and optimization_rounds>=1
        # and not outline_confirmed and not outline_checkpoint_sent）
        # 排在 panel_review_requested / a_gate_panel_request /
        # negative_feedback_alert 之前，且四个分支共用同一条 if/elif 链
        # → 同一课题只能命中一个分支。生产实测 14 课题中 7 个
        # optimization_rounds>=1，而 outline_checkpoint_sent 全库为
        # None（写入点 micro_scheduler.py:2012 只在「本轮核心已完成」
        # 短路路径触发，主 job 执行路径 micro_scheduler.py:2187-2191
        # 不写）→ outline_review 条件对所有已完成课题恒真 → 恒优先
        # 命中 → a_gate_panel_request（v7.3.42 新功能）与其余两类
        # optimizing 提醒**永久不可达**（实测：仅 a_gate 时出队条目是
        # outline_review 而非 panel_request）。
        if (status == "optimizing"
                and ps.get("optimization_rounds", 0) >= 1
                and not ps.get("outline_confirmed")
                and not ps.get("outline_checkpoint_sent")):
            items.append(
                {
                    "type": "outline_review",
                    "proposal_id": pid,
                    "title": ps.get("title", pid),
                    "waiting_hours": _hours_since(ps.get("updated_at"), now),
                    "suggested_action": "15 分钟过目大纲与关键判据（方向纠偏成本最低的时刻），可回复意见或确认",
                    "rounds": ps.get("optimization_rounds", 0),
                }
            )

    items.sort(key=lambda i: (i.get("waiting_hours") or -1), reverse=True)

    # v6.9.58 第四类：策略建议待人工确认——中高风险/非白名单键的
    # strategy_optimizer 建议此前只活在 dashboard JSON 里无人消费
    # （实测 3 周 0 采纳），接入队列获得控制台展示 + monitor 催办。
    items.extend(_pending_strategy_suggestions(now))

    # v6.10.7 第五类：高相关待积累簇超 4 周未满员——stale 清理保护后
    # 转人工裁决（补检索凑第 3 篇 / 关闭），避免窄方向积累被自动作废
    items.extend(_pending_cluster_reviews(now))

    # v7.2.55（健康检查改进项 p）第七类：输入端熔断——lifecycle_monitor
    # 的 input_pipeline_broken 告警只走飞书去重缓存，队列无此类型来源，
    # 连续 13 轮健康检查「建议写入队列」因无派生路径而永不落地。
    items.extend(_pending_input_broken(now))

    # v7.3.28 第八类：配额/重评门复核——持久源读取（非派生），聚合重写不丢
    items.extend(_pending_quota_reviews(now))

    # v7.2.55: escalate 统一在全部类型并入后计算（此前 strategy /
    # cluster_stale 项缺少 escalate 键，CLI 打印 KeyError、催办链漏判）
    for item in items:
        # v7.3.10: hold 裁决项不催办（用户裁决后不再提醒，直至重评门满足）
        if item.get("hold"):
            item["escalate"] = False
            continue
        item["escalate"] = (
            item.get("waiting_hours") is not None
            and item.get("waiting_hours") >= escalate_after_h
        )

    escalated = [i for i in items if i.get("escalate")]
    return {
        "generated_at": now_utc(),
        "items": items,
        "summary": {
            "total": len(items),
            "review": sum(1 for i in items if i["type"] == "review"),
            "activate": sum(1 for i in items if i["type"] == "activate"),
            "activate_hold": sum(1 for i in items if i["type"] == "activate_hold"),
            "negative_feedback": sum(
                1 for i in items if i["type"] == "negative_feedback"
            ),
            "strategy": sum(1 for i in items if i["type"] == "strategy"),
            "cluster_stale": sum(1 for i in items if i["type"] == "cluster_stale"),
            "panel_request": sum(1 for i in items if i["type"] == "panel_request"),
            "outline_review": sum(1 for i in items if i["type"] == "outline_review"),
            "input_broken": sum(1 for i in items if i["type"] == "input_broken"),
            "quota_review": sum(1 for i in items if i["type"] == "quota_review"),
            "escalated": len(escalated),
        },
    }


def _pending_input_broken(now: datetime) -> List[Dict[str, Any]]:
    """v7.2.55: 输入端熔断入队（与 lifecycle_monitor 同口径独立检测）。

    判据与 lifecycle_monitor._check_weekend_input 完全一致：最近 2 个
    weekend-input/ideas-*.json 产物文件的 actions 均为空。等待时长以
    较旧文件的文件名日期（ideas-YYYY-MM-DD）零点起算——恢复后最近一次
    周末产物非空即自动退出队列，不依赖告警缓存过期。
    """
    items: List[Dict[str, Any]] = []
    try:
        files = sorted(WEEKEND_INPUT_DIR.glob("ideas-*.json"))
        if len(files) < 2:
            return items
        recent = files[-2:]
        counts = []
        for f in recent:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                value = data.get("actions", data.get("ideas", []))
                counts.append(len(value) if isinstance(value, list) else 0)
            except Exception:
                counts.append(0)
        if not all(c == 0 for c in counts):
            return items
        waiting = _hours_since(_ideas_stem_to_iso(recent[0].stem), now)
        items.append({
            "type": "input_broken",
            "proposal_id": "global:input-pipeline",
            "title": "输入端熔断：连续周末零研究设想",
            "waiting_hours": waiting,
            "suggested_action": (
                "检查 summarize 新料过滤与 compose 路由链路，或人工补检索投放"
            ),
            "detail": f"{recent[0].stem} / {recent[-1].stem} 两次周末运行零设想",
        })
    except Exception as exc:  # noqa: BLE001 —— 队列聚合不因单源失败而断
        if _log:
            _log.warning("输入端熔断检测失败: %s", exc)
    return items


def _ideas_stem_to_iso(stem: str) -> Optional[str]:
    """ideas-YYYY-MM-DD → YYYY-MM-DDT00:00:00Z（等待时长起算锚点）。"""
    m = re.match(r"^ideas-(\d{4}-\d{2}-\d{2})$", stem)
    return f"{m.group(1)}T00:00:00Z" if m else None


def _pending_quota_reviews(now: datetime) -> List[Dict[str, Any]]:
    """v7.3.28: 配额/重评门复核事项入队（持久源 config/quota-reviews.json）。

    只处理 status == "pending" 的条目；done / skipped 视为已裁决，自动退出
    队列（无需人工改快照，改持久源即生效）。

    waiting_hours 语义（以到期日 due_date 为可行动起算点）：
      · 到期前恒为 0——未到点不计等待，按既有 escalate 口径不催办；
      · 到期后为「超期小时数」，≥ ESCALATE_AFTER_H（72h）才催办。
    另给 due_in_hours（正数=距到期还剩小时数，0=已到期）供展示。
    """
    items: List[Dict[str, Any]] = []
    try:
        data = load_json(QUOTA_REVIEWS_PATH, default={})
    except Exception as exc:  # noqa: BLE001 —— 队列聚合不因单源失败而断
        if _log:
            _log.warning("配额复核持久源读取失败: %s", exc)
        return items
    entries = data.get("items") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return items

    for e in entries:
        if not isinstance(e, dict) or e.get("status", "pending") != "pending":
            continue
        qid = str(e.get("id") or e.get("title") or "").strip()
        if not qid:
            continue
        due = e.get("due_date")
        overdue = _hours_since(due, now)
        waiting = 0.0 if overdue is None else max(0.0, overdue)
        items.append({
            "type": "quota_review",
            "proposal_id": f"global:quota_review:{qid}",
            "quota_review_id": qid,
            "title": e.get("title", qid),
            "criteria": e.get("criteria") or [],
            "decided_basis": e.get("decided_basis", ""),
            "due_date": due,
            "status": "pending",
            "waiting_hours": waiting,
            "overdue_hours": None if overdue is None else max(0.0, overdue),
            "due_in_hours": None if overdue is None else round(max(0.0, -overdue), 1),
            "suggested_action": "到期日逐条核对 criteria，满足才改配置值，否则维持现状",
            "notes": e.get("notes", ""),
        })
    return items



def _pending_cluster_reviews(now: datetime) -> List[Dict[str, Any]]:
    """v6.10.7: 聚合 stale 保护簇的人工裁决条目。

    数据源为 weekend-input/clusters.json 中 pending_human_review=True
    的 open 簇（由 close_stale_clusters 保护分支标记）。列表小（≤10 量级）
    且零 LLM，直接读文件不做缓存。人工处置路径：①按簇关键词定向补检索
    凑第 3 篇（簇 updated_at 刷新即自动退出保护）②确无价值则手工置
    closed。cluster_stale 等待时长以 stale_notified_at 起算。
    """
    try:
        registry = load_json(
            Path(__file__).resolve().parent.parent
            / "memory" / "weekend-input" / "clusters.json",
            default={},
        )
    except Exception:
        return []
    items: List[Dict[str, Any]] = []
    for c in registry.get("clusters", []) or []:
        if not isinstance(c, dict):
            continue
        if c.get("pending_human_review") and c.get("status") == "open":
            waiting = _hours_since(c.get("stale_notified_at"), now)
            members = len(c.get("member_source_ids", []) or [])
            cid = c.get("cluster_id", "")
            items.append({
                "type": "cluster_stale",
                # v6.10.10 修复：补 proposal_id 字段供消费者以 id 维度
                # 遍历 items 不抛 KeyError；与 review/activate/negative_feedback
                # 共享 proposal_id 语义槽位，cluster_id 保留供专门消费者区分
                "proposal_id": cid,
                "cluster_id": cid,
                "title": str(c.get("title", ""))[:60],
                "members": members,
                "waiting_hours": waiting,
                "suggested_action": "人工裁决：定向补检索凑第 3 篇或关闭该簇",
            })
    return items


_STRATEGY_CACHE = MEMORY_DIR / ".cache" / "human-queue-strategy-cache.json"
_STRATEGY_CACHE_TTL_S = 3600

_STRATEGY_DISPOSITIONS_PATH = MEMORY_DIR / "config" / "strategy-dispositions.json"
"""策略建议裁决账本（v7.2.43）。

背景：`run_human_queue()` 每次聚合重建 items 并整文件覆盖
memory/human-queue.json——人工/自动写在快照里的裁决字段
（status/resolution/resolved_at）在下一次聚合时丢失，critic_timeout/
writer_timeout 两条过期建议因此 3 次复活（10-19 auto_resolved → 10-19
复活 → 10-24 再复活）。账本以策略 key 为维度持久化裁决，聚合时跳过
已裁决项；**suggested 值与裁决时不同则重新入队**（防陈旧裁决永久压制
新建议）。
"""


def record_strategy_disposition(key: str, status: str, resolution: str = "",
                                suggested: Any = None) -> bool:
    """记录一条策略建议的裁决（供设置中心/控制台/守卫调用）。

    Args:
        key: 策略键（如 critic_timeout）
        status: 裁决状态（auto_resolved / applied / rejected）
        resolution: 裁决理由
        suggested: 裁决针对的建议值快照（值再变时条目重新入队）
    """
    from common import file_lock
    try:
        with file_lock("strategy-dispositions"):
            data = load_json(_STRATEGY_DISPOSITIONS_PATH, default={})
            if not isinstance(data, dict):
                data = {}
            data[key] = {
                "status": status,
                "resolution": resolution,
                "suggested": suggested,
                "at": now_utc(),
            }
            save_json(_STRATEGY_DISPOSITIONS_PATH, data)
        # 裁决变更后立即失效聚合缓存（1h TTL 内缓存会掩盖新裁决）
        try:
            if _STRATEGY_CACHE.exists():
                _STRATEGY_CACHE.unlink()
        except OSError:
            pass
        return True
    except Exception as exc:  # noqa: BLE001
        if _log:
            _log.warning(f"策略裁决账本写入失败: {exc}")
        return False


def _load_strategy_dispositions() -> Dict[str, Any]:
    data = load_json(_STRATEGY_DISPOSITIONS_PATH, default={})
    return data if isinstance(data, dict) else {}


def _pending_strategy_suggestions(now: datetime) -> List[Dict[str, Any]]:
    """聚合待人工确认的策略建议（1h 文件缓存，防 monitor/刷页重复计算）。"""
    cached = load_json(_STRATEGY_CACHE, {})
    ts = cached.get("at", "")
    if ts:
        try:
            age = (now - datetime.fromisoformat(ts.replace("Z", "+00:00"))).total_seconds()
            if age < _STRATEGY_CACHE_TTL_S:
                return cached.get("items", [])
        except ValueError:
            pass
    items: List[Dict[str, Any]] = []
    # v7.2.43：裁决账本——已裁决 key 且 suggested 值未变 → 跳过（防复活）
    dispositions = _load_strategy_dispositions()
    try:
        from strategy_optimizer import AUTO_APPLY_KEYS, suggest_strategies
        result = suggest_strategies()
        current = result.get("current") or {}
        for key, sug in (result.get("suggested") or {}).items():
            if key in AUTO_APPLY_KEYS or current.get(key) == sug:
                continue  # 白名单项由 auto_apply_low_risk 处理
            disp = dispositions.get(key)
            if isinstance(disp, dict) and disp.get("suggested") == sug:
                continue  # 已裁决且建议值未变——保持裁决，不再入队
            items.append({
                "type": "strategy",
                # v7.2.26 修复：补 proposal_id 字段供消费者以 id 维度
                # 遍历 items 不抛 KeyError；strategy 类全局共享，无具体课
                # 题归属，使用 agent_str "global:strategy" 标识。
                "proposal_id": f"global:strategy:{key}",
                "title": f"策略建议：{key}",
                "current": current.get(key),
                "suggested": sug,
                "risk": result.get("risk", "unknown"),
                "waiting_hours": None,
                "suggested_action": "在设置中心/控制台确认应用（低风险项已自动应用）",
            })
    except Exception as exc:  # noqa: BLE001 —— 队列聚合不因策略模块失败而断
        if _log:
            _log.warning("策略建议聚合失败: %s", exc)
    try:
        _STRATEGY_CACHE.parent.mkdir(parents=True, exist_ok=True)
        save_json(_STRATEGY_CACHE, {"at": now_utc(), "items": items})
    except OSError:
        pass
    return items


def run_human_queue(persist: bool = True) -> Dict[str, Any]:
    """聚合 + 持久化快照（monitor 与控制台共用）。"""
    result = collect_human_queue()
    # v7.2.55: 快照补 updated_at（健康检查曾以「无 updated_at」无法测量
    # 队列文件新鲜度；与 generated_at 同值，供消费方按统一键名读取）。
    result["updated_at"] = result.get("generated_at") or now_utc()
    if persist:
        try:
            HUMAN_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
            save_json(HUMAN_QUEUE_PATH, result)
        except Exception as exc:
            if _log:
                _log.warning(f"队列快照写入失败: {exc}")
    return result


def load_human_queue_snapshot() -> Dict[str, Any]:
    return load_json(HUMAN_QUEUE_PATH, default={"items": [], "summary": {}})


def _self_check() -> None:
    from datetime import timedelta

    now = datetime(2026, 8, 14, 12, 0, tzinfo=timezone.utc)
    proposals = {
        # 待审 3 天 + 决策包 approve_lean → 催办 + 可采纳
        "a-review": {
            "status": "pending_review",
            "title": "待审课题",
            "updated_at": "2026-08-11T10:00:00Z",
            "transition_history": [
                {"from": "optimizing", "to": "pending_review", "at": "2026-08-11T11:00:00Z"}
            ],
            "review_dossier": {
                "pre_review_verdict": "approve_lean",
                "can_adopt": True,
            },
            "last_monitor_score": 0.87,
        },
        # drafts 半天 → 不催办
        "b-draft": {
            "status": "drafts",
            "title": "新设想",
            "created_at": "2026-08-14T02:00:00Z",
            "idea_dossier": {"recommendation": "activate"},
        },
        # 负反馈冷却中（自动清除未用尽）→ 不进队列
        "c-neg-cooling": {
            "status": "optimizing",
            "negative_feedback_alert": True,
            "negative_feedback_at": "2026-08-13T00:00:00Z",
            "negative_feedback_auto_clear_count": 0,
        },
        # 负反馈自动清除已用尽 → 进队列
        "d-neg-exhausted": {
            "status": "optimizing",
            "negative_feedback_alert": True,
            "negative_feedback_at": "2026-08-12T00:00:00Z",
            "negative_feedback_auto_clear_count": 1,
            "negative_feedback_reasons": ["score 下降"],
            "title": "反复触发课题",
        },
        # optimizing 正常 → 不进队列
        "e-normal": {"status": "optimizing"},
    }

    result = collect_human_queue(proposals=proposals, now=now)
    ids = {i["proposal_id"] for i in result["items"]}
    # v6.10.10 修复：self_check 改为子集断言。_pending_cluster_reviews /
    # _pending_strategy_suggestions / _pending_feedback_review 会读
    # 生产文件，items 可能含外部累积条目；只要测试项必含即可
    assert {"a-review", "b-draft", "d-neg-exhausted"} <= ids, ids
    assert result["summary"]["escalated"] >= 1
    review = next(i for i in result["items"] if i["proposal_id"] == "a-review")
    assert review["escalate"] is True
    assert review["waiting_hours"] == 73.0
    assert review["can_adopt"] is True
    assert "一键采纳" in review["suggested_action"]
    draft = next(i for i in result["items"] if i["proposal_id"] == "b-draft")
    assert draft["escalate"] is False
    print("✓ human_queue 自检通过")


def main() -> None:
    parser = argparse.ArgumentParser(description="待人工处理队列")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return

    result = run_human_queue()
    s = result["summary"]
    print(
        f"待人工事项 {s['total']} 项：验收 {s['review']} / 激活 {s['activate']} / "
        f"负反馈 {s['negative_feedback']} / 配额复核 {s.get('quota_review', 0)}；"
        f"催办 {s['escalated']} 项"
    )
    for item in result["items"]:
        wait = item.get("waiting_hours")
        due_in = item.get("due_in_hours")
        if item["type"] == "quota_review" and due_in is not None and due_in > 0:
            wait_s = f"距到期 {due_in:.0f}h"
        else:
            wait_s = f"等待 {wait:.0f}h" if wait is not None else "等待 ?"
        flag = " ⚠ 催办" if item["escalate"] else ""
        print(f"  [{item['type']}] {item['title'][:30]} · {wait_s} · {item['suggested_action']}{flag}")


if __name__ == "__main__":
    main()
