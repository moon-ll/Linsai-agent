#!/usr/bin/env python3
"""Token 用量追踪器 — 记录和分析 LLM 调用消耗。

用途：
    记录每次对话的 prompt/completion token 用量，支持 API 精确统计和 CLI 估算。

用法示例：
    >>> from usage_tracker import record_usage, get_stats
    >>> record_usage("20260508-测试", "minimax", "你好", "你好！", {"prompt_tokens": 10, "completion_tokens": 5})
    >>> stats = get_stats("daily")

规范：
    - 仅使用 Python 3 标准库
    - JSON 文件 ensure_ascii=False, indent=2
    - 时间戳使用 UTC ISO 格式
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
USAGE_DIR = PROJECT_ROOT / "memory" / "usage"
USAGE_PATH = USAGE_DIR / "usage.json"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _this_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _ensure_dir() -> None:
    USAGE_DIR.mkdir(parents=True, exist_ok=True)


def _load_usage() -> Dict[str, Any]:
    _ensure_dir()
    if not USAGE_PATH.exists():
        return {"records": [], "total": {"prompt": 0, "completion": 0, "calls": 0}}
    try:
        with open(USAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"records": [], "total": {"prompt": 0, "completion": 0, "calls": 0}}


def _save_usage(data: Dict[str, Any]) -> None:
    _ensure_dir()
    with open(USAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _estimate_tokens(text: str) -> int:
    """估算文本的 token 数量。

    策略：
        - 中文：1 字 ≈ 1 token
        - 英文：1 词 ≈ 1.3 token
        - 简化估算：utf-8 字节数 // 3（经验值，覆盖中英文混合）
    """
    if not text:
        return 0
    return max(1, len(text.encode("utf-8")) // 3)


def record_usage(
    session_id: str,
    provider: str,
    prompt_text: str,
    response_text: str,
    usage_dict: Optional[Dict[str, int]] = None,
) -> None:
    """记录一次 LLM 调用的 token 用量。

    Args:
        session_id: 会话 ID
        provider: Provider 名称（minimax/kimi/claude）
        prompt_text: 发送给 LLM 的完整 prompt（含 system_prompt + messages）
        response_text: LLM 返回的文本
        usage_dict: API 返回的 usage 字段，如 {"prompt_tokens": 100, "completion_tokens": 50}
                   若为 None（CLI 调用），则使用字符估算
    """
    data = _load_usage()

    if usage_dict:
        prompt_tokens = usage_dict.get("prompt_tokens", 0)
        completion_tokens = usage_dict.get("completion_tokens", 0)
        is_estimated = False
    else:
        prompt_tokens = _estimate_tokens(prompt_text)
        completion_tokens = _estimate_tokens(response_text)
        is_estimated = True

    record = {
        "timestamp": _now_utc(),
        "date": _today(),
        "month": _this_month(),
        "session_id": session_id,
        "provider": provider,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "is_estimated": is_estimated,
    }

    data["records"].append(record)

    # 更新总计
    data["total"]["prompt"] += prompt_tokens
    data["total"]["completion"] += completion_tokens
    data["total"]["calls"] += 1

    _save_usage(data)


def get_stats(period: str = "daily") -> Dict[str, Any]:
    """获取用量统计。

    Args:
        period: daily / monthly / by_session / by_provider / total / recent

    Returns:
        对应维度的统计数据
    """
    data = _load_usage()
    records = data.get("records", [])

    if period == "total":
        return data.get("total", {"prompt": 0, "completion": 0, "calls": 0})

    if period == "daily":
        today = _today()
        result = {"prompt": 0, "completion": 0, "calls": 0, "date": today}
        for r in records:
            if r.get("date") == today:
                result["prompt"] += r["prompt_tokens"]
                result["completion"] += r["completion_tokens"]
                result["calls"] += 1
        return result

    if period == "monthly":
        month = _this_month()
        result = {"prompt": 0, "completion": 0, "calls": 0, "month": month}
        for r in records:
            if r.get("month") == month:
                result["prompt"] += r["prompt_tokens"]
                result["completion"] += r["completion_tokens"]
                result["calls"] += 1
        return result

    if period == "by_session":
        result: Dict[str, Any] = {}
        for r in records:
            sid = r["session_id"]
            if sid not in result:
                result[sid] = {"prompt": 0, "completion": 0, "calls": 0}
            result[sid]["prompt"] += r["prompt_tokens"]
            result[sid]["completion"] += r["completion_tokens"]
            result[sid]["calls"] += 1
        return result

    if period == "by_provider":
        result: Dict[str, Any] = {}
        for r in records:
            p = r["provider"]
            if p not in result:
                result[p] = {"prompt": 0, "completion": 0, "calls": 0}
            result[p]["prompt"] += r["prompt_tokens"]
            result[p]["completion"] += r["completion_tokens"]
            result[p]["calls"] += 1
        return result

    if period == "recent":
        # 最近 30 条记录
        return {"records": records[-30:]}

    return {}


def get_usage_summary() -> Dict[str, Any]:
    """返回用于 Web 界面展示的用量摘要。"""
    daily = get_stats("daily")
    total = get_stats("total")
    by_provider = get_stats("by_provider")
    return {
        "daily": daily,
        "total": total,
        "by_provider": by_provider,
    }


if __name__ == "__main__":
    # 自检
    print("◐ Token 用量追踪器自检")
    print(f"  _estimate_tokens('hello world') = {_estimate_tokens('hello world')}")
    print(f"  _estimate_tokens('你好世界') = {_estimate_tokens('你好世界')}")
    record_usage("test-session", "minimax", "测试 prompt", "测试回复", {"prompt_tokens": 10, "completion_tokens": 5})
    record_usage("test-session", "kimi", "测试 prompt2", "测试回复2", None)
    print(f"  日统计: {get_stats('daily')}")
    print(f"  Provider统计: {get_stats('by_provider')}")
    print("✓ 自检通过")
