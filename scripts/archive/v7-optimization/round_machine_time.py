#!/usr/bin/env python3
"""单轮优化机时基线测量（G2-D 目标判据配套，零 LLM 只读）。

用途：目标模式 G2-D 判据「单轮优化机时可测可降」的统一口径工具。
口径：
- 机时 = 日志中「对抗轮 N: <step> 完成 success=...」行的 elapsed 累加
  （writer/critic/lit_*/gap_identify 等主步骤，含失败轮；模型逃生直调
  llm_router 不在此口径——直调本身即降级路径）。
- 轮次完成 = 各课题 monitor_history 中 monitor 记录的时间戳按日计数。
- 输出 每日：机时（小时）/ 完成轮次 / 机时每轮。

用法示例：
    python3 scripts/round_machine_time.py            # 近 7 天基线
    python3 scripts/round_machine_time.py --days 14  # 更长窗口
    python3 scripts/round_machine_time.py --json     # 机器可读输出
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LIFECYCLE = PROJECT_ROOT / "research_proposals" / "_lifecycle.json"

_STEP_RE = re.compile(
    r"\[(\d{4}-\d{2}-\d{2}) [^\]]+\].*?对抗轮 \d+: (\w+) 完成 success=(True|False) elapsed=([\d.]+)s"
)


def _self_check() -> bool:
    """自检：正则可解析当前日志至少一条步骤完成行（或日志为空时豁免）。"""
    log = LOG_DIR / "linsai.log"
    if not log.exists():
        print("○ 主日志不存在（首次运行），跳过")
        return True
    hit = 0
    with log.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if _STEP_RE.search(line):
                hit += 1
                if hit >= 1:
                    break
    print(f"{'✓' if hit else '⚠'} 日志步骤完成行解析：{hit} 条（0 条时口径可能漂移，需人工核对）")
    return True


def collect(days: int):
    """返回 {日期: {'secs': float, 'steps': int, 'rounds': int}}。"""
    per_day: Dict = defaultdict(lambda: {"secs": 0.0, "steps": 0, "rounds": 0})
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    # 日志主档 + 轮换档（linsai.log.2026-11-04）
    logs = [LOG_DIR / "linsai.log"] + sorted(LOG_DIR.glob("linsai.log.2*"))
    for log in logs:
        if not log.exists():
            continue
        with log.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = _STEP_RE.search(line)
                if not m:
                    continue
                d = m.group(1)
                try:
                    dt = datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
                # 日志时间为本地时区打印，粗对齐即可（基线口径自身一致）
                if dt < cutoff - timedelta(days=1):
                    continue
                per_day[d]["secs"] += float(m.group(4))
                per_day[d]["steps"] += 1
    # 轮次完成数：monitor_history 时间戳（同样受 days 窗口约束）
    if LIFECYCLE.exists():
        st = json.loads(LIFECYCLE.read_text(encoding="utf-8"))
        for v in (st.get("proposals") or {}).values():
            for h in (v.get("monitor_history") or []):
                at = (h.get("at") or "")[:10] if isinstance(h, dict) else ""
                if not at:
                    continue
                try:
                    dt = datetime.strptime(at, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
                if dt < cutoff - timedelta(days=1):
                    continue
                per_day[at]["rounds"] += 1
    return {d: v for d, v in sorted(per_day.items()) if v["secs"] or v["rounds"]}


def main():
    ap = argparse.ArgumentParser(description="单轮优化机时基线测量")
    ap.add_argument("--days", type=int, default=7, help="回看天数（默认 7）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()
    data = collect(args.days)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    print(f"单轮机时基线（近 {args.days} 天，口径：对抗轮步骤 elapsed 累加 / monitor 完成数）")
    print(f"{'日期':<12} {'机时h':>7} {'步骤':>5} {'完成轮次':>8} {'h/轮':>7}")
    tot_s = tot_r = 0
    for d, v in data.items():
        r = v["rounds"]
        per = f"{v['secs'] / 3600 / r:.1f}" if r else "-"
        print(f"{d:<12} {v['secs'] / 3600:>7.1f} {v['steps']:>5} {r:>8} {per:>7}")
        tot_s += v["secs"]
        tot_r += r
    if tot_r:
        print(f"\n窗口合计：机时 {tot_s / 3600:.1f}h，完成 {tot_r} 轮，平均 {tot_s / 3600 / tot_r:.1f} h/轮")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        sys.exit(0 if _self_check() else 1)
    main()
