#!/usr/bin/env python3
"""
proactive_engine.py — 主动感知引擎

用途：
    检测用户状态信号（任务逾期、会话休眠、压力关键词），
    生成交互建议，管理自主级别与交互模式识别。

用法示例：
    >>> from scripts.proactive_engine import heartbeat, classify_mode
    >>> signals = heartbeat()
    >>> mode = classify_mode("帮我看看这个光路设计")
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from session_manager import list_sessions, load_session
    from task_manager import list_tasks, create_task, transition_task, delete_task
    from memory_manager import get_relevant_memories
except ImportError as _import_err:
    print(f"✗ 无法导入依赖模块: {_import_err}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
STRESS_KEYWORDS: dict[str, list[str]] = {
    "high": ["失眠", "崩溃", "绝望", "想放弃", "活不下去"],
    "medium": ["疲惫", "累", "麻木", "焦虑", "压力大", "失眠", "拒稿", "被拒", "失败"],
    "low": ["延期", "拖延", "来不及", "担心", "紧张"],
}

MODE_PATTERNS: dict[str, list[str]] = {
    "co-working": ["帮我", "看看", "设计", "方案", "实验", "计算", "推导", "怎么", "如何", "对吗", "对不对"],
    "deep-talk": ["困惑", "迷茫", "焦虑", "担心", "害怕", "怀疑", "意义", "方向", "选择", "怎么办", "觉得"],
    "quick-check": ["量纲", "对吗", "正确吗", "验证", "检查一下", "快速", "确认"],
}


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)


def _autonomy_path() -> Path:
    d = _PROJECT_ROOT / "memory"
    d.mkdir(parents=True, exist_ok=True)
    return d / "autonomy-level.json"


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path, default: Any = None) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default if default is not None else {}


# ---------------------------------------------------------------------------
# 自主级别
# ---------------------------------------------------------------------------
def get_autonomy_level() -> str:
    """读取当前自主级别，默认 suggest。"""
    data = _read_json(_autonomy_path(), {})
    level = data.get("level", "suggest")
    if level not in ("observe", "suggest", "act"):
        level = "suggest"
    return level


def set_autonomy_level(level: str) -> str:
    """设置自主级别：observe / suggest / act。保存到 memory/autonomy-level.json。"""
    if level not in ("observe", "suggest", "act"):
        print(f"⚠ 无效级别 '{level}'，保持当前值")
        return get_autonomy_level()
    data = _read_json(_autonomy_path(), {})
    data["level"] = level
    data["updated_at"] = _now_utc()
    _write_json(_autonomy_path(), data)
    print(f"✓ 自主级别已设置为: {level}")
    return level


# ---------------------------------------------------------------------------
# 截止日期提醒
# ---------------------------------------------------------------------------
def check_due_reminders(days_ahead: int = 2) -> list[dict]:
    """检查即将到期的任务。返回任务列表（含task_id, title, due_date, days_remaining）。"""
    today = datetime.now(timezone.utc).date()
    deadline = today + timedelta(days=days_ahead)
    reminders: list[dict] = []
    for task in list_tasks(status="active"):
        dd = task.get("due_date", "").strip()
        if not dd:
            continue
        try:
            due = datetime.strptime(dd, "%Y-%m-%d").date()
        except ValueError:
            continue
        if today <= due <= deadline:
            reminders.append({"task_id": task["task_id"], "title": task["title"], "due_date": dd, "days_remaining": (due - today).days})
    return reminders


# ---------------------------------------------------------------------------
# 压力信号检测
# ---------------------------------------------------------------------------
def detect_stress_signals(session_id: str, window_days: int = 7) -> dict:
    """检测指定会话中的压力信号。"""
    try:
        messages, _state = load_session(session_id)
    except Exception as exc:
        print(f"✗ 加载会话失败: {exc}")
        return {
            "has_stress": False,
            "signals": [],
            "overall_risk": "none",
            "recommendation": "无法加载会话",
        }

    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    signals: list[dict] = []
    for msg in messages:
        if msg.get("role") != "user":
            continue
        ts = msg.get("timestamp", "")
        if ts:
            try:
                msg_dt = _parse_utc(ts)
                if msg_dt < cutoff:
                    continue
            except Exception:
                pass
        content = msg.get("content", "")
        for severity, keywords in STRESS_KEYWORDS.items():
            for kw in keywords:
                if kw in content:
                    # 提取上下文（关键词前后各15字）
                    idx = content.find(kw)
                    start = max(0, idx - 15)
                    end = min(len(content), idx + len(kw) + 15)
                    context = content[start:end]
                    # 避免同一关键词同一消息重复
                    if not any(s["keyword"] == kw and s.get("_msg_idx") == messages.index(msg) for s in signals):
                        signals.append({
                            "keyword": kw,
                            "severity": severity,
                            "count": 1,
                            "context": context,
                            "_msg_idx": messages.index(msg),
                        })

    # 去重合并同一关键词
    merged: dict[str, dict] = {}
    for s in signals:
        kw = s["keyword"]
        if kw in merged:
            merged[kw]["count"] += 1
        else:
            merged[kw] = {"keyword": kw, "severity": s["severity"], "count": s["count"], "context": s["context"]}
    signals = list(merged.values())

    # 评估整体风险
    severities = [s["severity"] for s in signals]
    if "high" in severities:
        overall_risk = "high"
        recommendation = "建议温和关切，询问是否需要帮助，避免强迫。"
    elif "medium" in severities:
        overall_risk = "medium"
        recommendation = "保持关注，在适当时机提供支持。"
    elif "low" in severities:
        overall_risk = "low"
        recommendation = "轻微压力信号，可自然提及。"
    else:
        overall_risk = "none"
        recommendation = "无显著压力信号。"

    return {
        "has_stress": bool(signals),
        "signals": signals,
        "overall_risk": overall_risk,
        "recommendation": recommendation,
    }


# ---------------------------------------------------------------------------
# 交互模式识别
# ---------------------------------------------------------------------------
def classify_mode(user_input: str) -> str:
    """基于用户输入判断交互模式。

    返回: "co-working" | "deep-talk" | "quick-check" | "unknown"
    """
    text = user_input.strip()
    if not text:
        return "unknown"

    # quick-check 更严格：短输入 + 特定关键词
    qc_matches = sum(1 for kw in MODE_PATTERNS["quick-check"] if kw in text)
    if qc_matches > 0 and len(text) <= 20:
        return "quick-check"

    scores: dict[str, int] = {}
    for mode, keywords in MODE_PATTERNS.items():
        scores[mode] = sum(1 for kw in keywords if kw in text)

    max_score = max(scores.values())
    if max_score == 0:
        return "unknown"

    # 若 quick-check 得分最高但输入不短，则降级为 co-working（如存在）
    best_mode = max(scores, key=scores.get)  # type: ignore[arg-type]
    if best_mode == "quick-check" and len(text) > 40:
        scores["quick-check"] = 0
        max_score = max(scores.values())
        if max_score == 0:
            return "unknown"
        best_mode = max(scores, key=scores.get)  # type: ignore[arg-type]

    return best_mode


# ---------------------------------------------------------------------------
# 主动消息生成
# ---------------------------------------------------------------------------
def generate_proactive_message(signal: dict) -> str:
    """基于信号生成主动消息文案。"""
    sig_type = signal.get("type", "")
    if sig_type == "due_reminder":
        return f"你之前提到 '{signal.get('task_title', '某项任务')}' 的截止日期是 {signal.get('due_date', '近期')}，需要我帮忙推进吗？"
    if sig_type == "stalled_task":
        return f"'{signal.get('task_title', '某项任务')}' 已经 {signal.get('days', '好几')} 天没有更新了，需要一起看看吗？"
    if sig_type == "stress_signal":
        return f"我注意到你最近提到了 '{signal.get('keyword', '一些压力')}’。不在疲惫时做重大决定——需要我帮你梳理一下吗？"
    if sig_type == "dormant_session":
        return f"我们关于 '{signal.get('topic', '之前的讨论')}' 的对话已经停了 {signal.get('days', '几')} 天，有什么新进展吗？"
    if sig_type == "learning_opportunity":
        top_score = signal.get("top_score", 0)
        candidates = signal.get("candidates", [])
        topics = "、".join(c["title"][:20] for c in candidates[:2])
        return f"我在浏览最新文献时发现了几个可能相关的方向：{topics}（相关度 {top_score:.0%}）。要启动自主学习吗？"
    return "有件事想提醒你，有空的时候看看？"


# ---------------------------------------------------------------------------
# 用户反馈处理
# ---------------------------------------------------------------------------
def handle_user_feedback(feedback: str) -> str:
    """处理用户对主动提醒的反馈。"""
    text = feedback.strip().lower()
    data = _read_json(_autonomy_path(), {})

    negative = ["现在不想聊", "稍后", "不用了", "别烦我", "不需要", "闭嘴"]
    positive = ["好的", "帮我", "看看", "可以", "说吧", "嗯"]
    frequency_complaint = ["太频繁了", "太多", "太吵", "安静点"]

    if any(k in text for k in negative):
        data["level"] = "observe"
        data["snooze_until"] = (datetime.now(timezone.utc) + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        data["last_feedback"] = text
        _write_json(_autonomy_path(), data)
        print("✓ 已退回被动模式（observe），24小时内不再主动提醒")
        return "observe"

    if any(k in text for k in frequency_complaint):
        data["frequency"] = "low"
        data["last_feedback"] = text
        _write_json(_autonomy_path(), data)
        print("✓ 已降低提醒频率")
        return "low_frequency"

    if any(k in text for k in positive):
        data["last_feedback"] = text
        _write_json(_autonomy_path(), data)
        print("✓ 保持当前级别")
        return data.get("level", "suggest")

    # 默认保持当前
    data["last_feedback"] = text
    _write_json(_autonomy_path(), data)
    print("⚠ 未识别反馈意图，保持当前级别")
    return data.get("level", "suggest")


# ---------------------------------------------------------------------------
# 自主学习机会检测
# ---------------------------------------------------------------------------

def _check_learning_opportunities() -> list[dict]:
    """检测自主学习机会，返回信号列表。"""
    signals = []

    # 读取配置
    config_path = _PROJECT_ROOT / "memory" / "learning-config.json"
    config = _read_json(config_path, {})
    if not config.get("auto_enabled", False):
        return signals

    # 检查自主级别
    if get_autonomy_level() not in ("suggest", "act"):
        return signals

    # 检查配额
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    last_run = config.get("last_auto_run", "")
    today_count = config.get("today_count", 0)
    week_count = config.get("week_count", 0)

    # 跨天重置
    if last_run != today:
        today_count = 0
        config["today_count"] = 0
        config["last_auto_run"] = today
        _write_json(config_path, config)

    if today_count >= config.get("daily_quota", 1):
        return signals
    if week_count >= config.get("weekly_quota", 5):
        return signals

    # 获取策略阈值
    strategy = config.get("strategy", "balanced")
    thresholds = config.get("thresholds", {"conservative": 0.8, "balanced": 0.5, "aggressive": 0.3})
    threshold = thresholds.get(strategy, 0.5)

    # 动态导入 external_fetcher
    try:
        import importlib.util
        ef_path = Path(__file__).parent / "external_fetcher.py"
        if not ef_path.exists():
            return signals
        spec = importlib.util.spec_from_file_location("external_fetcher", ef_path)
        ef = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ef)
    except Exception as e:
        print(f"⚠ 无法导入 external_fetcher: {e}")
        return signals

    # 发现学习机会
    try:
        opportunities = ef.discover_learning_opportunities(
            max_results=3,
            sources=config.get("sources", ["arxiv", "wikipedia", "raw"])
        )
    except Exception as e:
        print(f"⚠ 学习机会发现失败: {e}")
        return signals

    if not opportunities:
        return signals

    # 取最高分
    top = opportunities[0]
    score = top.get("_score", {})
    overall = score.get("overall", 0)

    if overall < threshold:
        return signals

    # 生成信号
    candidates = [{
        "title": op.get("title", "未知"),
        "source": op.get("source", "unknown"),
        "score": op.get("_score", {}).get("overall", 0),
    } for op in opportunities[:3]]

    signals.append({
        "type": "learning_opportunity",
        "severity": "low",
        "source": "auto_scan",
        "description": f"发现 {len(opportunities)} 个学习机会（最高相关度 {overall:.0%}）",
        "suggested_action": "启动自主学习",
        "candidates": candidates,
        "top_score": overall,
    })

    return signals


# ---------------------------------------------------------------------------
# 心跳扫描
# ---------------------------------------------------------------------------
def heartbeat() -> list[dict]:
    """执行一次完整的心跳扫描，返回检测到的信号列表。"""
    signals: list[dict] = []
    now = datetime.now(timezone.utc)

    # 1. 任务截止日期（未来2天内）
    for task in check_due_reminders(days_ahead=2):
        signals.append({"type": "due_reminder", "severity": "medium" if task["days_remaining"] <= 1 else "low", "source": task["task_id"], "description": f"任务 '{task['title']}' 将在 {task['days_remaining']} 天后到期", "suggested_action": "提醒用户推进任务", "task_title": task["title"], "due_date": task["due_date"]})

    # 2. 任务无进展（updated_at > 7天）
    stall_cutoff = now - timedelta(days=7)
    for task in list_tasks(status="active"):
        updated = task.get("updated_at", "")
        if not updated:
            continue
        try:
            updated_dt = _parse_utc(updated)
        except Exception:
            continue
        if updated_dt < stall_cutoff:
            days_stalled = (now - updated_dt).days
            signals.append({"type": "stalled_task", "severity": "medium" if days_stalled > 14 else "low", "source": task["task_id"], "description": f"任务 '{task['title']}' 已 {days_stalled} 天未更新", "suggested_action": "询问是否需要协助", "task_title": task["title"], "days": days_stalled})

    # 3. 会话休眠（last_active > 3天）
    dormant_cutoff = now - timedelta(days=3)
    for sess in list_sessions(status="active"):
        last_active = sess.get("last_active", "")
        if not last_active:
            continue
        try:
            la_dt = _parse_utc(last_active)
        except Exception:
            continue
        if la_dt < dormant_cutoff:
            days_dormant = (now - la_dt).days
            signals.append({"type": "dormant_session", "severity": "low", "source": sess["session_id"], "description": f"会话 '{sess.get('topic', sess['session_id'])}' 已休眠 {days_dormant} 天", "suggested_action": "温和询问是否有新进展", "topic": sess.get("topic", sess["session_id"]), "days": days_dormant})

    # 4. 压力信号（最近活跃会话）
    for sess in list_sessions(status="active")[:3]:
        sid = sess["session_id"]
        result = detect_stress_signals(sid, window_days=7)
        if result["has_stress"]:
            top_signal = result["signals"][0]
            signals.append({"type": "stress_signal", "severity": result["overall_risk"], "source": sid, "description": f"会话 '{sess.get('topic', sid)}' 检测到压力关键词 '{top_signal['keyword']}'", "suggested_action": result["recommendation"], "keyword": top_signal["keyword"]})

    # 5. 自主学习机会（learning opportunity）
    signals.extend(_check_learning_opportunities())

    print(f"✓ 心跳扫描完成，检测到 {len(signals)} 个信号")
    return signals


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("◐ 开始 proactive_engine 自检")
    print("=" * 50)

    print("\n[1/8] 设置自主级别为 suggest...")
    set_autonomy_level("suggest")
    assert get_autonomy_level() == "suggest"

    print("\n[2/8] 创建测试任务...")
    today = datetime.now(timezone.utc)
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    in3days = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    eight_days_ago = (today - timedelta(days=8)).strftime("%Y-%m-%dT%H:%M:%SZ")
    tid_due, _ = create_task("即将到期测试任务", category="research", due_date=tomorrow)
    transition_task(tid_due, "active")
    tid_far, _ = create_task("三天后任务", category="writing", due_date=in3days)
    transition_task(tid_far, "active")
    tid_stall, _ = create_task("停滞任务", category="experiment")
    transition_task(tid_stall, "active")
    tid_overdue, _ = create_task("逾期测试任务", category="general", due_date=yesterday)
    transition_task(tid_overdue, "active")
    active_stall_path = _PROJECT_ROOT / "tasks" / "active" / f"{tid_stall}.json"
    if active_stall_path.exists():
        task_data = _read_json(active_stall_path, {})
        task_data["updated_at"] = eight_days_ago
        _write_json(active_stall_path, task_data)

    print("\n[3/8] 创建测试会话...")
    from session_manager import create_session, append_message
    sid_stress, _ = create_session("压力检测测试", mode="deep-talk")
    append_message(sid_stress, "user", "最近实验一直失败，感觉很焦虑，压力大到失眠")
    append_message(sid_stress, "assistant", "理解你的感受。具体是哪一步出了问题？")
    append_message(sid_stress, "user", "我已经疲惫到麻木了，有点想放弃")
    sid_dormant, _ = create_session("休眠会话测试", mode="co-working")
    append_message(sid_dormant, "user", "帮我设计一个固体HHG光路")
    state_path = _PROJECT_ROOT / "sessions" / sid_dormant / "state.json"
    if state_path.exists():
        state_data = _read_json(state_path, {})
        state_data["last_active"] = (today - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        _write_json(state_path, state_data)

    print("\n[4/8] 运行 heartbeat...")
    signals = heartbeat()
    types_found = {s["type"] for s in signals}
    assert "due_reminder" in types_found and "stalled_task" in types_found and "dormant_session" in types_found and "stress_signal" in types_found, f"实际: {types_found}"
    print(f"   检测到信号类型: {types_found}")

    print("\n[5/8] 测试 classify_mode...")
    assert classify_mode("帮我看看这个光路设计") == "co-working"
    assert classify_mode("我很困惑，这个方向是不是错了") == "deep-talk"
    assert classify_mode("量纲对吗") == "quick-check"
    assert classify_mode("") == "unknown"
    assert classify_mode("好的") == "unknown"
    assert classify_mode("帮我推导一下这个公式的量纲，看看对不对，这是整个方案的第一步") == "co-working"
    print("   模式识别测试通过")

    print("\n[6/8] 测试 generate_proactive_message...")
    msg_due = generate_proactive_message({"type": "due_reminder", "task_title": "DFG申请", "due_date": "2026-05-10"})
    assert "DFG申请" in msg_due and "截止日期" in msg_due
    msg_stall = generate_proactive_message({"type": "stalled_task", "task_title": "光路搭建", "days": 10})
    assert "光路搭建" in msg_stall and "10" in msg_stall
    msg_stress = generate_proactive_message({"type": "stress_signal", "keyword": "焦虑"})
    assert "焦虑" in msg_stress and "不在疲惫时做重大决定" in msg_stress
    msg_dormant = generate_proactive_message({"type": "dormant_session", "topic": "固体HHG", "days": 5})
    assert "固体HHG" in msg_dormant and "5" in msg_dormant
    print("   消息生成测试通过")

    print("\n[7/8] 测试 handle_user_feedback...")
    set_autonomy_level("suggest")
    result = handle_user_feedback("现在不想聊")
    assert get_autonomy_level() == "observe" and result == "observe"
    set_autonomy_level("suggest")
    result = handle_user_feedback("太频繁了")
    assert _read_json(_autonomy_path(), {}).get("frequency") == "low" and result == "low_frequency"
    set_autonomy_level("suggest")
    result = handle_user_feedback("帮我看看")
    assert get_autonomy_level() == "suggest" and result == "suggest"
    print("   反馈处理测试通过")

    print("\n[8/8] 测试 detect_stress_signals...")
    stress_result = detect_stress_signals(sid_stress, window_days=7)
    assert stress_result["has_stress"] is True and stress_result["overall_risk"] == "high"
    keywords = [s["keyword"] for s in stress_result["signals"]]
    assert any(k in keywords for k in ["焦虑", "压力大", "失眠", "疲惫", "想放弃"])
    print(f"   检测到压力关键词: {keywords}")

    print("\n[清理] 删除测试数据...")
    for tid in (tid_due, tid_far, tid_stall, tid_overdue):
        delete_task(tid)
    for sid in (sid_stress, sid_dormant):
        sess_dir = _PROJECT_ROOT / "sessions" / sid
        if sess_dir.exists():
            shutil.rmtree(sess_dir)
            print(f"   已删除测试会话: {sid}")
    auth_path = _autonomy_path()
    if auth_path.exists():
        auth_path.unlink()
        print(f"   已删除 {auth_path.name}")

    print("\n" + "=" * 50)
    print("✓ 所有自检项目通过")
    print("=" * 50)
