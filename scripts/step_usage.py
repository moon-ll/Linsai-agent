#!/usr/bin/env python3
"""step_usage — 管线 LLM 调用计量账本（v6.10.52）。

背景：usage_tracker 只覆盖聊天会话（唯一生产者 web_routes_sessions），
管线侧（生命周期轮转 / 评审团 / 蒸馏 / 周末链路 / hermes agent loop）的
LLM 调用全程零记录——"今天谁在烧 token"只能靠日志考古。本模块给两类
调用通道补上统一账本：

    1. llm_router.call_llm   → CoPilot 侧全部直调（含 llm_gateway 包装）
    2. hermes_memory._run_hermes_agent → 全部 hermes agent loop 会话

设计：
    - JSONL 月分片（memory/usage/step-usage-YYYY-MM.jsonl），追加即写，
      避免大 JSON 的读改写竞态；file_lock 保护多进程（cron worker）并发。
    - token 优先取 API 返回的 usage；无 usage（CLI 型 provider / hermes）
      按 chars/2 粗估并标记 tokens_estimated=true。
    - provider 级失败（429/超时）同样入账（success=false），供后续做
      配额熔断与成本归因。

用法示例：
    python3 scripts/step_usage.py --summary            # 近 7 天汇总
    python3 scripts/step_usage.py --summary --days 30  # 近 30 天
    python3 scripts/step_usage.py --tail 20            # 最近 20 条流水
    python3 scripts/step_usage.py --self-check         # 自检

规范：仅标准库；中文 docstring；路径经 paths 推导。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common import file_lock, now_utc  # noqa: E402
from paths import MEMORY_DIR  # noqa: E402

try:
    from logger import get_logger
    _log = get_logger("step_usage")
except Exception:  # pragma: no cover
    _log = None

USAGE_DIR = MEMORY_DIR / "usage"
"""账本目录（与聊天侧 usage.json 同目录，文件名区分）。"""

SHARD_PREFIX = "step-usage-"
"""月分片文件名前缀：step-usage-YYYY-MM.jsonl。"""

RETENTION_DAYS = 180
"""分片保留天数（超出自动清理，仅清理本模块命名模式的文件）。"""

# 混合中英文本的粗估换算：约 2 字符 ≈ 1 token（保守偏低估，标记 estimated）
_CHARS_PER_TOKEN = 2


def estimate_tokens(chars: int) -> int:
    """按字符数粗估 token 数（无 usage 返回时的兜底口径）。"""
    if chars <= 0:
        return 0
    return max(1, chars // _CHARS_PER_TOKEN)


def _shard_path(ts: str) -> Path:
    """按 UTC 时间戳返回对应月分片路径。"""
    month = (ts or now_utc())[:7]
    return USAGE_DIR / f"{SHARD_PREFIX}{month}.jsonl"


def _in_test_context() -> bool:
    """v6.10.55: 测试上下文守卫——账本只记录真实管线/会话调用。

    判据：入口脚本名为 test_*/self_test（self_test --module 与
    python3 scripts/tests/test_x.py 两种入口覆盖）。历史测试套件
    （hermes 进程组/机制加固等）会走到被挂接的 _run_hermes_agent 与
    llm_router，不设守卫会把 "boom" 之类测试产物写进真实分片。

    v7.3.45 补口：`python3 -m unittest ...` 入口 argv[0] 是 unittest 的
    __main__.py，旧判据漏防——2026-11-01 实测 test_hermes_agent_process_group
    经此入口写入 28 条 '错误信息XYZ' 假数据。补进程内信号：unittest /
    pytest 已加载即视为测试上下文（生产脚本零依赖不导入二者）。
    """
    try:
        argv0 = Path(sys.argv[0] if sys.argv else "").name
        if argv0.startswith(("test_", "self_test")):
            return True
        if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
            return True
        # -m unittest / unittest.main() 进程内必加载 unittest 模块
        if "unittest" in sys.modules:
            return True
        return False
    except Exception:
        return False


def record_call(
    kind: str,
    name: str,
    *,
    provider: str = "",
    model: str = "",
    prefer: str = "",
    elapsed_s: float = 0.0,
    success: bool = True,
    prompt_chars: int = 0,
    output_chars: int = 0,
    usage: Optional[Dict[str, Any]] = None,
    error: str = "",
    note: str = "",
) -> bool:
    """追加一条调用记录。

    Args:
        kind: 通道类型（llm_router / hermes_agent）
        name: 调用对象（provider 名 或 hermes profile 名）
        usage: API 返回的 {prompt_tokens, completion_tokens}（可缺失）
        error: 失败原因摘要（success=false 时）
        note: v7.3.86 观测标注（如 think_only_retry:16384）——加性字段，
            聚合按固定键遍历不受影响，供预算调优回溯取证
    """
    if _in_test_context():
        return False
    rec: Dict[str, Any] = {
        "ts": now_utc(),
        "kind": kind,
        "name": name or "(unknown)",
        "provider": provider,
        "model": model,
        "prefer": prefer,
        "success": bool(success),
        "elapsed_s": round(float(elapsed_s or 0.0), 2),
        "prompt_chars": int(prompt_chars or 0),
        "output_chars": int(output_chars or 0),
        "error": (error or "")[:200],
        "note": (note or "")[:120],
    }
    pt = ct = None
    if isinstance(usage, dict):
        try:
            pt = int(usage.get("prompt_tokens") or 0) or None
            ct = int(usage.get("completion_tokens") or 0) or None
        except (TypeError, ValueError):
            pt = ct = None
    rec["prompt_tokens"] = pt if pt is not None else estimate_tokens(prompt_chars)
    rec["completion_tokens"] = ct if ct is not None else estimate_tokens(output_chars)
    rec["tokens_estimated"] = pt is None and ct is None

    line = json.dumps(rec, ensure_ascii=False)
    try:
        USAGE_DIR.mkdir(parents=True, exist_ok=True)
        path = _shard_path(rec["ts"])
        with file_lock("step_usage"):
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        _cleanup_old_shards()
        return True
    except OSError as e:
        if _log:
            _log.warning("[step_usage] 记录写入失败: %s", e)
        return False


def _cleanup_old_shards() -> None:
    """清理超过保留期的月分片（仅 step-usage-*.jsonl 命名）。"""
    import datetime as _dt
    cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=RETENTION_DAYS)
    try:
        for p in USAGE_DIR.glob(f"{SHARD_PREFIX}*.jsonl"):
            m = re.match(rf"{SHARD_PREFIX}(\d{{4}}-\d{{2}})\.jsonl", p.name)
            if not m:
                continue
            shard_dt = _dt.datetime.strptime(m.group(1), "%Y-%m").replace(
                tzinfo=_dt.timezone.utc)
            if shard_dt < cutoff:
                p.unlink(missing_ok=True)
    except OSError:
        pass


def _read_records(days: int) -> List[Dict[str, Any]]:
    """读取近 N 天（按日粒度过滤）的全部记录。"""
    import datetime as _dt
    cutoff_day = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days)).strftime("%Y-%m-%d")
    out: List[Dict[str, Any]] = []
    if not USAGE_DIR.exists():
        return out
    for p in sorted(USAGE_DIR.glob(f"{SHARD_PREFIX}*.jsonl")):
        try:
            with p.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if str(rec.get("ts", ""))[:10] >= cutoff_day:
                        out.append(rec)
        except OSError:
            continue
    return out


def summarize(days: int = 7) -> Dict[str, Any]:
    """按 天 × (kind, name) 聚合：调用数、失败数、时长、token（真实/估算分列）。"""
    recs = _read_records(days)
    buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "calls": 0, "fails": 0, "elapsed_s": 0.0,
        "prompt_tokens": 0, "completion_tokens": 0, "estimated_calls": 0,
    })
    for r in recs:
        key = f"{str(r.get('ts', ''))[:10]}|{r.get('kind', '?')}|{r.get('name', '?')}"
        b = buckets[key]
        b["calls"] += 1
        if not r.get("success"):
            b["fails"] += 1
        b["elapsed_s"] += float(r.get("elapsed_s") or 0.0)
        b["prompt_tokens"] += int(r.get("prompt_tokens") or 0)
        b["completion_tokens"] += int(r.get("completion_tokens") or 0)
        if r.get("tokens_estimated"):
            b["estimated_calls"] += 1

    by_day: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "calls": 0, "fails": 0, "elapsed_s": 0.0,
        "prompt_tokens": 0, "completion_tokens": 0})
    for key, b in buckets.items():
        day = key.split("|", 1)[0]
        d = by_day[day]
        for f in ("calls", "fails", "elapsed_s", "prompt_tokens", "completion_tokens"):
            d[f] += b[f]

    total = {
        "calls": sum(d["calls"] for d in by_day.values()),
        "fails": sum(d["fails"] for d in by_day.values()),
        "elapsed_s": round(sum(d["elapsed_s"] for d in by_day.values()), 1),
        "prompt_tokens": sum(d["prompt_tokens"] for d in by_day.values()),
        "completion_tokens": sum(d["completion_tokens"] for d in by_day.values()),
    }
    return {
        "days": days,
        "total": total,
        "by_day": {k: dict(v) for k, v in sorted(by_day.items(), reverse=True)},
        "by_call": [
            {"day": k.split("|", 1)[0], "kind": k.split("|")[1],
             "name": k.split("|", 2)[2] if k.count("|") >= 2 else "",
             **{f: (round(v[f], 1) if f == "elapsed_s" else v[f]) for f in
                ("calls", "fails", "elapsed_s", "prompt_tokens", "completion_tokens", "estimated_calls")}}
            for k, v in sorted(buckets.items(), key=lambda kv: (
                kv[0].split("|", 1)[0], -kv[1]["elapsed_s"]))
        ],
    }


def _self_check() -> None:
    """自检：临时目录内完整走一遍 记录→汇总→清理 输入输出契约。"""
    global USAGE_DIR
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        old_dir = USAGE_DIR
        USAGE_DIR = Path(td)
        try:
            assert record_call("llm_router", "minimax", usage={
                "prompt_tokens": 100, "completion_tokens": 50}, elapsed_s=1.5)
            assert record_call("hermes_agent", "writer", prompt_chars=4000,
                               output_chars=2000, elapsed_s=120.0)
            assert record_call("llm_router", "minimax", success=False,
                               error="429", elapsed_s=0.3, prefer="panel")
            s = summarize(days=1)
            assert s["total"]["calls"] == 3, s
            assert s["total"]["fails"] == 1
            # 真实 usage 不估算、hermes 估算
            est_rows = [r for r in s["by_call"] if r["name"] == "writer"]
            assert est_rows and est_rows[0]["estimated_calls"] == 1
            assert est_rows[0]["prompt_tokens"] == 2000
            shards = list(Path(td).glob(f"{SHARD_PREFIX}*.jsonl"))
            assert len(shards) == 1
        finally:
            USAGE_DIR = old_dir
    print("✓ step_usage 自检通过")


def main() -> int:
    parser = argparse.ArgumentParser(description="管线 LLM 调用计量账本")
    parser.add_argument("--summary", action="store_true", help="近 N 天汇总")
    parser.add_argument("--days", type=int, default=7, help="汇总时间窗（默认 7 天）")
    parser.add_argument("--tail", type=int, default=0, help="显示最近 N 条流水")
    parser.add_argument("--self-check", action="store_true", help="自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        return 0

    if args.tail:
        recs = _read_records(days=RETENTION_DAYS)
        for r in recs[-args.tail:]:
            flag = "✓" if r.get("success") else "✗"
            est = "~" if r.get("tokens_estimated") else " "
            print(f"{flag}{est} {str(r.get('ts',''))[:19]} {r.get('kind'):13} "
                  f"{r.get('name','')[:20]:20} in={r.get('prompt_tokens')} "
                  f"out={r.get('completion_tokens')} {r.get('elapsed_s')}s "
                  f"{r.get('error','')[:40]}")
        return 0

    if args.summary:
        s = summarize(days=args.days)
        t = s["total"]
        print(f"近 {args.days} 天：调用 {t['calls']} 次（失败 {t['fails']}），"
              f"总时长 {t['elapsed_s']}s，token in={t['prompt_tokens']} "
              f"out={t['completion_tokens']}")
        print(f"{'日期':<12}{'通道':<14}{'对象':<22}{'次数':>4}{'失败':>4}"
              f"{'时长s':>9}{'in_tok':>9}{'out_tok':>9}{'估算':>4}")
        for r in s["by_call"]:
            print(f"{r['day']:<12}{r['kind']:<14}{r['name'][:20]:<22}"
                  f"{r['calls']:>4}{r['fails']:>4}{r['elapsed_s']:>9}"
                  f"{r['prompt_tokens']:>9}{r['completion_tokens']:>9}"
                  f"{r['estimated_calls']:>4}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
