#!/usr/bin/env python3
"""待人工处理队列聚合器（v6.9.0 R6）。

把散落在各状态里"等人"的事项聚合成单一队列，每项附 AI 建议动作与
等待时长，超过 72h 标记催办（由 lifecycle_monitor 通知）：

  - pending_review 课题 → 建议动作取自验收决策包预审（v6.9.0 R1）
  - drafts 课题        → 建议动作取自立项决策包推荐（v6.9.0 R4）
  - 负反馈告警课题     → 仅在自动清除已用尽后进入队列（v6.9.0 R2 降噪）

用法：
    python3 scripts/human_queue.py            # 聚合并打印
    python3 scripts/human_queue.py --self-check
"""

from __future__ import annotations

import argparse
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

    items.sort(key=lambda i: (i.get("waiting_hours") or -1), reverse=True)
    for item in items:
        item["escalate"] = (
            item.get("waiting_hours") is not None
            and item.get("waiting_hours") >= escalate_after_h
        )

    # v6.9.58 第四类：策略建议待人工确认——中高风险/非白名单键的
    # strategy_optimizer 建议此前只活在 dashboard JSON 里无人消费
    # （实测 3 周 0 采纳），接入队列获得控制台展示 + monitor 催办。
    items.extend(_pending_strategy_suggestions(now))

    escalated = [i for i in items if i["escalate"]]
    return {
        "generated_at": now_utc(),
        "items": items,
        "summary": {
            "total": len(items),
            "review": sum(1 for i in items if i["type"] == "review"),
            "activate": sum(1 for i in items if i["type"] == "activate"),
            "negative_feedback": sum(
                1 for i in items if i["type"] == "negative_feedback"
            ),
            "strategy": sum(1 for i in items if i["type"] == "strategy"),
            "escalated": len(escalated),
        },
    }


_STRATEGY_CACHE = MEMORY_DIR / ".cache" / "human-queue-strategy-cache.json"
_STRATEGY_CACHE_TTL_S = 3600


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
    try:
        from strategy_optimizer import AUTO_APPLY_KEYS, suggest_strategies
        result = suggest_strategies()
        current = result.get("current") or {}
        for key, sug in (result.get("suggested") or {}).items():
            if key in AUTO_APPLY_KEYS or current.get(key) == sug:
                continue  # 白名单项由 auto_apply_low_risk 处理
            items.append({
                "type": "strategy",
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
    assert ids == {"a-review", "b-draft", "d-neg-exhausted"}, ids
    assert result["summary"]["total"] == 3
    assert result["summary"]["escalated"] == 1
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
        f"负反馈 {s['negative_feedback']}；催办 {s['escalated']} 项"
    )
    for item in result["items"]:
        wait = item.get("waiting_hours")
        wait_s = f"{wait:.0f}h" if wait is not None else "?"
        flag = " ⚠ 催办" if item["escalate"] else ""
        print(f"  [{item['type']}] {item['title'][:30]} · 等待 {wait_s} · {item['suggested_action']}{flag}")


if __name__ == "__main__":
    main()
