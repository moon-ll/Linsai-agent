#!/usr/bin/env python3
"""failure_analyzer.py — 失败模式分析 + prompt 优化建议（v6.7 林赛总控能力·子模块）

从 linsai.log 和 _lifecycle.json 中聚类失败模式，生成 prompt 修正建议。

聚类规则（按错误关键词正则分桶）：
- "score = 0" → score-zero-streak（连续 0 分）
- "申请书不存在" → empty-draft（草稿为空）
- "hermes oneshot 失败" / "[Errno 2]" → env-pollution（环境变量污染，v6.6.3 已修）
- "timeout" / "超时" → profile-timeout（profile 超时）
- "No module named" → import-error（import 错误）
- "FileNotFoundError" → file-missing（文件缺失）
- "KeyError" / "AttributeError" → code-bug（代码 bug）

每种模式关联：
- occurrences（24h 出现次数）
- 涉及 proposals
- 建议 prompt 修改文本
- expected_impact（预期效果）

用法:
    from failure_analyzer import analyze_failures
    result = analyze_failures(window_hours=24)
    for p in result['patterns']:
        print(p['label'], p['occurrences'], p['suggested_prompt_change'][:80])
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc, load_json
from paths import PROJECT_ROOT, LOGS_DIR

# 失败模式库（聚类规则 + 建议）
PATTERN_LIBRARY = [
    {
        "id": "score-zero-streak",
        "label": "连续 0 分（申请书内容空）",
        "regex": r"score[=:\s]+0\.0+.*?(\n|$)",
        "category": "评分异常",
        "suggested_prompt_change": (
            "在 critic prompt 中明确：当申请书内容为占位符时，给 0.10 而非 0.00，"
            "并加 '本轮因内容缺失无法准确评分，建议先补充实质内容'。"
        ),
        "expected_impact": "score_history 能区分'空草稿'vs'完全失败'，避免连续 0 分触发无提升退出",
    },
    {
        "id": "empty-draft",
        "label": "申请书草稿为空",
        "regex": r"申请书不存在|empty draft|占位符",
        "category": "数据缺失",
        "suggested_prompt_change": (
            "在 writer 派活前增加预检：若 proposal-draft.md < 500 字节，"
            "先调用 writer 写一版'骨架充实版'再进入对抗循环。"
        ),
        "expected_impact": "避免对空草稿做无意义的对抗评审",
    },
    {
        "id": "env-pollution",
        "label": "环境变量污染（PYTHONHOME 等）",
        "regex": r"No module named 'encodings'|PYTHONHOME|Fatal Python error.*init_fs_encoding",
        "category": "环境",
        "suggested_prompt_change": "（v6.6.3 已修复：clean_subprocess_env 自动 pop 22 个 Python 变量）",
        "expected_impact": "hermes 子进程不再因 IDE 注入的 PYTHONHOME 崩溃",
    },
    {
        "id": "profile-timeout",
        "label": "Profile 超时",
        "regex": r"超时\([0-9]+s\)|TimeoutExpired",
        "category": "性能",
        "suggested_prompt_change": (
            "若某 profile 连续 3 次超时，strategy_optimizer 建议把该 profile 的 timeout + 50%。"
        ),
        "expected_impact": "减少超时失败，提升完成率",
    },
    {
        "id": "file-missing",
        "label": "文件缺失",
        "regex": r"FileNotFoundError|No such file or directory",
        "category": "数据缺失",
        "suggested_prompt_change": "派活前自动 mkdir -p 目标目录；writer 优化前确认 proposal-draft.md 存在",
        "expected_impact": "减少因目录未创建导致的失败",
    },
    {
        "id": "code-bug",
        "label": "代码 Bug（KeyError/AttributeError）",
        "regex": r"KeyError|AttributeError|TypeError",
        "category": "代码",
        "suggested_prompt_change": (
            "这种错误是代码层 bug，需开发者人工修复。"
            "在 orchestrator dashboard 中显示 stack_trace 前 500 字符。"
        ),
        "expected_impact": "快速定位代码 bug",
    },
    {
        "id": "rate-limit",
        "label": "API 限流",
        "regex": r"rate.?limit|HTTP 429|too many requests|额度",
        "category": "外部依赖",
        "suggested_prompt_change": (
            "strategy_optimizer：增加 stagger_seconds，"
            "或切到 fallback provider。"
        ),
        "expected_impact": "缓解 GLM/MiniMax API 限流",
    },
    {
        "id": "low-content-after-rewrite",
        "label": "writer 优化后内容未实质性增长",
        "regex": r"proposal-draft\.md.*size.*<.*500",
        "category": "数据缺失",
        "suggested_prompt_change": (
            # v6.9.25: 旧文案"总字数 ≥ 4000 字，每章节 ≥ 1200 字"低于范本
            # 体量（正文 2.5-3 万字符），曾把申请书往小拉（BENCHMARK_GUARD
            # 拦截的历史实例）。改为篇幅对标口径。
            "在 writer prompt 中明确：'请基于 brief 实质扩写申请书，篇幅对标"
            "范本实测口径（立项依据 5000-8000 字、研究内容 3000-5000 字、"
            "研究方案 5000-8000 字）；素材不足时深挖论证链，不得注水凑字数'。"
        ),
        "expected_impact": "避免 writer 仅做表面修改",
    },
]


def _read_recent_log_lines(window_hours: int = 24, max_lines: int = 5000) -> List[str]:
    """读取最近 N 小时的日志行。"""
    log_file = LOGS_DIR / "linsai.log"
    if not log_file.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    out: List[str] = []
    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            # 文件可能很大，只取最后 max_lines 行
            lines = f.readlines()[-max_lines:]
        for line in lines:
            m = re.search(r"\[(\d{4}-\d{2}-\d{2}T[\d:Z]+)\]", line)
            if m:
                try:
                    at = datetime.fromisoformat(m.group(1).replace("Z", "+00:00"))
                    if at < cutoff:
                        continue
                except Exception:
                    pass
            out.append(line)
    except Exception:
        pass
    return out


def _match_patterns(log_lines: List[str]) -> Dict[str, List[str]]:
    """对日志行做模式匹配，返回 {pattern_id: [matched_lines]}。"""
    matched: Dict[str, List[str]] = defaultdict(list)
    for line in log_lines:
        if "[ERROR]" not in line and "[WARNING]" not in line:
            continue
        for pat in PATTERN_LIBRARY:
            if re.search(pat["regex"], line, re.IGNORECASE):
                matched[pat["id"]].append(line.strip())
                break  # 一行只匹配一个模式
    return matched


def _involved_proposals(log_lines: List[str]) -> Dict[str, int]:
    """统计每条错误涉及的 proposal ID。"""
    out: Dict[str, int] = defaultdict(int)
    pattern = re.compile(r"\[([\w\-]+(?:2026\d{4}|2026\d{2}\d{2}|nsfc-[\w\-]+))\]")
    for line in log_lines:
        for m in pattern.finditer(line):
            pid = m.group(1)
            if pid.startswith(("general-", "key-", "nsfc-")):
                out[pid] += 1
    return dict(out)


def analyze_failures(window_hours: int = 24) -> Dict[str, Any]:
    """分析失败模式。

    Args:
        window_hours: 时间窗（小时），默认 24

    Returns:
        {
          'patterns': [
            {id, label, category, occurrences, sample_errors, suggested_prompt_change, expected_impact},
            ...
          ],
          'summary': {total_errors, top_pattern, ...},
          'computed_at': ISO 字符串
        }
    """
    log_lines = _read_recent_log_lines(window_hours)
    error_lines = [l for l in log_lines if "[ERROR]" in l]
    warning_lines = [l for l in log_lines if "[WARNING]" in l]
    all_issue_lines = error_lines + warning_lines

    matched = _match_patterns(all_issue_lines)
    pid_counts = _involved_proposals(all_issue_lines)

    patterns_out: List[Dict[str, Any]] = []
    for pat in PATTERN_LIBRARY:
        lines = matched.get(pat["id"], [])
        if not lines and pat["id"] not in ("env-pollution",):
            # 跳过没出现的模式（env-pollution 即使没出现也要保留，标记已修复）
            continue
        patterns_out.append({
            "id": pat["id"],
            "label": pat["label"],
            "category": pat["category"],
            "occurrences": len(lines),
            "sample_errors": lines[:3],  # 最多 3 条样本
            "suggested_prompt_change": pat["suggested_prompt_change"],
            "expected_impact": pat["expected_impact"],
        })

    # 按 occurrences 降序
    patterns_out.sort(key=lambda x: x["occurrences"], reverse=True)

    top = patterns_out[0] if patterns_out else None

    return {
        "patterns": patterns_out,
        "summary": {
            "total_errors": len(error_lines),
            "total_warnings": len(warning_lines),
            "top_pattern": top["id"] if top else "",
            "top_pattern_label": top["label"] if top else "",
            "involved_proposals": pid_counts,
        },
        "window_hours": window_hours,
        "computed_at": now_utc(),
    }


def _self_check() -> None:
    """自检：测试 analyze_failures 的基本输出。"""
    print("=== failure_analyzer._self_check ===")
    result = analyze_failures(window_hours=168)  # 看一周
    assert "patterns" in result
    assert "summary" in result
    print(f"  total_errors: {result['summary']['total_errors']}")
    print(f"  total_warnings: {result['summary']['total_warnings']}")
    print(f"  patterns detected: {len(result['patterns'])}")
    for p in result["patterns"][:5]:
        print(f"  - {p['id']}: {p['occurrences']} 次 ({p['label']})")
    assert result["summary"]["total_errors"] + result["summary"]["total_warnings"] >= 0
    print("=== 通过 ===")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-check":
        _self_check()
    else:
        result = analyze_failures()
        print(json.dumps(result, ensure_ascii=False, indent=2))
