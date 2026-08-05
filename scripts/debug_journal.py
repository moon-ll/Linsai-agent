#!/usr/bin/env python3
"""debug_journal.py — CoPilot 自身 debug 经验记录系统。

记录每次 debug 的发现过程、根因分析、解决方案、验证方法和经验教训，
支持按分类/严重程度/标签过滤、统计概览、高频模式检测和 Markdown 报告导出。

数据文件：memory/debug-journal.json

用法:
    python3 scripts/debug_journal.py add                      # 交互式添加
    python3 scripts/debug_journal.py list                      # 列出所有条目（最近优先）
    python3 scripts/debug_journal.py list --category bug_fix --severity critical
    python3 scripts/debug_journal.py show <id>                 # 显示详情
    python3 scripts/debug_journal.py stats                     # 统计概览
    python3 scripts/debug_journal.py patterns                  # 分析高频模式
    python3 scripts/debug_journal.py export                    # 导出 Markdown 报告
    python3 scripts/debug_journal.py --self-check              # 自检
    python3 scripts/debug_journal.py add --json <json_str>     # 非交互式添加（JSON 字符串）

无第三方依赖。仅标准库。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ─────────────────────────────────────────────
# 路径与常量
# ─────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
MEMORY_DIR = PROJECT_ROOT / "memory"
JOURNAL_PATH = MEMORY_DIR / "debug-journal.json"
REPORT_PATH = MEMORY_DIR / "debug-journal-report.md"

# 合法分类与严重程度
CATEGORIES = [
    "bug_fix", "config_change", "performance",
    "design_correction", "prompt_tuning", "infrastructure",
]
SEVERITIES = ["critical", "major", "minor"]

# 状态图标（与 AGENTS.md 规范一致）
OK = "✓"
WARN = "⚠"
FAIL = "✗"
PEND = "○"


# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────

def now_utc() -> str:
    """返回当前 UTC 时间的 ISO 8601 字符串。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _journal_path() -> Path:
    """返回当前使用的 journal 文件路径（支持自检时临时替换）。"""
    return _JOURNAL_PATH_OVERRIDE if _JOURNAL_PATH_OVERRIDE else JOURNAL_PATH


# 模块级变量，自检时临时替换
_JOURNAL_PATH_OVERRIDE: Optional[Path] = None


def _load_journal() -> Dict:
    """加载 debug journal 数据文件，不存在则返回空结构。"""
    path = _journal_path()
    if not path.exists():
        return {"entries": [], "stats": _empty_stats()}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "entries" not in data:
            data["entries"] = []
        if "stats" not in data:
            data["stats"] = _empty_stats()
        return data
    except Exception:
        return {"entries": [], "stats": _empty_stats()}


def _save_journal(data: Dict) -> None:
    """原子写入 debug journal 数据文件。"""
    path = _journal_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    import tempfile
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _empty_stats() -> Dict:
    """返回空的统计结构。"""
    return {
        "total_entries": 0,
        "by_category": {},
        "by_severity": {},
        "by_tag": {},
        "recent_pattern": "",
    }


def _generate_id() -> str:
    """生成唯一条目 ID：dj-YYYYMMDD-NNN。"""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    data = _load_journal()
    same_day = sum(
        1 for e in data["entries"]
        if e.get("id", "").startswith(f"dj-{date_str}-")
    )
    return f"dj-{date_str}-{same_day + 1:03d}"


# ─────────────────────────────────────────────
# 核心函数
# ─────────────────────────────────────────────

def add_entry(fields: Dict) -> Dict:
    """添加一条 debug 经验记录。

    自动生成 id 和 timestamp；若 fields 中已提供则保留原值。
    fields 中可包含以下键：
        category, severity, title, context, root_cause, solution,
        files_changed, testing, lessons, tags, related_entries,
        status, commit

    Args:
        fields: 包含条目字段的可选字典。

    Returns:
        新创建的条目字典。
    """
    entry = {
        "id": fields.get("id") or _generate_id(),
        "timestamp": fields.get("timestamp") or now_utc(),
        "category": fields.get("category", "bug_fix"),
        "severity": fields.get("severity", "major"),
        "title": fields.get("title", ""),
        "context": fields.get("context", ""),
        "root_cause": fields.get("root_cause", ""),
        "solution": fields.get("solution", ""),
        "files_changed": fields.get("files_changed", []),
        "testing": fields.get("testing", ""),
        "lessons": fields.get("lessons", ""),
        "tags": fields.get("tags", []),
        "related_entries": fields.get("related_entries", []),
        "status": fields.get("status", "pending_verification"),
        "commit": fields.get("commit", ""),
    }

    data = _load_journal()
    data["entries"].append(entry)
    data["stats"] = _update_stats(data["entries"])
    _save_journal(data)

    return entry


def list_entries(filters: Optional[Dict] = None) -> List[Dict]:
    """列出条目，支持按 category/severity/tag/status 过滤，按时间倒序。

    Args:
        filters: 过滤条件字典，可包含 category, severity, tag, status。

    Returns:
        匹配的条目列表（时间倒序）。
    """
    data = _load_journal()
    entries = data.get("entries", [])

    if filters is None:
        filters = {}

    result = entries
    if "category" in filters:
        cat = filters["category"]
        result = [e for e in result if e.get("category") == cat]
    if "severity" in filters:
        sev = filters["severity"]
        result = [e for e in result if e.get("severity") == sev]
    if "tag" in filters:
        tag = filters["tag"]
        result = [e for e in result if tag in e.get("tags", [])]
    if "status" in filters:
        st = filters["status"]
        result = [e for e in result if e.get("status") == st]

    # 按时间倒序
    result.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return result


def compute_stats() -> Dict:
    """计算统计概览。

    Returns:
        包含 total_entries, by_category, by_severity, by_tag 的统计字典。
    """
    data = _load_journal()
    entries = data.get("entries", [])
    return _update_stats(entries)


def detect_patterns() -> List[Dict]:
    """检测高频模式（同类问题出现 >= 2 次）。

    按 tag 聚类和 root_cause 关键词聚类两种维度检测，
    返回所有满足阈值的模式列表。

    Returns:
        模式列表，每个模式包含 type, key, count, entry_ids。
    """
    data = _load_journal()
    entries = data.get("entries", [])
    patterns: List[Dict] = []

    # 维度 1：按 tag 聚类
    tag_counter: Dict[str, List[str]] = {}
    for entry in entries:
        for tag in entry.get("tags", []):
            tag_counter.setdefault(tag, []).append(entry["id"])

    for tag, ids in sorted(tag_counter.items(), key=lambda x: -len(x[1])):
        if len(ids) >= 2:
            patterns.append({
                "type": "tag",
                "key": tag,
                "count": len(ids),
                "entry_ids": ids,
            })

    # 维度 2：按 root_cause 关键词聚类
    cause_keywords: Dict[str, List[str]] = {}
    for entry in entries:
        cause = entry.get("root_cause", "")
        words = _extract_keywords(cause)
        for word in words:
            if len(word) >= 2:
                cause_keywords.setdefault(word, []).append(entry["id"])

    for word, ids in sorted(cause_keywords.items(), key=lambda x: -len(x[1])):
        if len(ids) >= 2:
            patterns.append({
                "type": "root_cause_keyword",
                "key": word,
                "count": len(ids),
                "entry_ids": ids,
            })

    # 更新 stats 中的 recent_pattern
    data["stats"]["recent_pattern"] = (
        f"{len(patterns)} 个高频模式（{sum(p['count'] for p in patterns)} 条关联记录）"
        if patterns
        else "暂无高频模式"
    )
    _save_journal(data)

    return patterns


def export_report(output_path: Optional[Path] = None) -> None:
    """导出 Markdown 报告。

    Args:
        output_path: 输出路径，默认 memory/debug-journal-report.md。
    """
    path = output_path or REPORT_PATH
    data = _load_journal()
    entries = data.get("entries", [])
    stats = data.get("stats", _empty_stats())
    patterns = detect_patterns()

    lines: List[str] = []
    lines.append("# CoPilot Debug 经验报告")
    lines.append("")
    lines.append(f"> 生成时间：{now_utc()}")
    lines.append(f"> 总条目数：{stats.get('total_entries', 0)}")
    lines.append("")

    # ── 统计概览 ──
    lines.append("## 统计概览")
    lines.append("")
    lines.append("### 按分类")
    lines.append("")
    by_cat = stats.get("by_category", {})
    has_data = False
    for cat in CATEGORIES:
        count = by_cat.get(cat, 0)
        if count > 0:
            lines.append(f"- **{cat}**: {count}")
            has_data = True
    if not has_data:
        lines.append("- （暂无数据）")
    lines.append("")

    lines.append("### 按严重程度")
    lines.append("")
    by_sev = stats.get("by_severity", {})
    has_data = False
    for sev in SEVERITIES:
        count = by_sev.get(sev, 0)
        if count > 0:
            lines.append(f"- **{sev}**: {count}")
            has_data = True
    if not has_data:
        lines.append("- （暂无数据）")
    lines.append("")

    # ── 高频模式 ──
    lines.append("## 高频模式")
    lines.append("")
    if patterns:
        for p in patterns:
            marker = "[tag]" if p["type"] == "tag" else "[cause]"
            lines.append(
                f"- {marker} **{p['key']}** — 出现 {p['count']} 次 "
                f"(关联: {', '.join(p['entry_ids'])})"
            )
    else:
        lines.append("- 暂无高频模式")
    lines.append("")

    # ── 条目详情 ──
    lines.append("## 条目详情")
    lines.append("")
    if not entries:
        lines.append("（暂无条目）")
    else:
        sorted_entries = sorted(entries, key=lambda e: e.get("timestamp", ""), reverse=True)
        for entry in sorted_entries:
            eid = entry.get("id", "unknown")
            lines.append(f"### {eid}: {entry.get('title', '(无标题)')}")
            lines.append("")
            lines.append(f"- **时间**: {entry.get('timestamp', '')}")
            lines.append(f"- **分类**: {entry.get('category', '')}")
            lines.append(f"- **严重程度**: {entry.get('severity', '')}")
            lines.append(f"- **状态**: {entry.get('status', '')}")
            if entry.get("commit"):
                lines.append(f"- **关联提交**: {entry['commit']}")
            lines.append("")

            if entry.get("context"):
                lines.append(f"**发现过程**：{entry['context']}")
                lines.append("")
            if entry.get("root_cause"):
                lines.append(f"**根因分析**：{entry['root_cause']}")
                lines.append("")
            if entry.get("solution"):
                lines.append(f"**解决方案**：{entry['solution']}")
                lines.append("")
            if entry.get("files_changed"):
                lines.append(f"**变更文件**：{', '.join(entry['files_changed'])}")
                lines.append("")
            if entry.get("testing"):
                lines.append(f"**验证方法**：{entry['testing']}")
                lines.append("")
            if entry.get("lessons"):
                lines.append(f"**经验教训**：{entry['lessons']}")
                lines.append("")
            if entry.get("tags"):
                lines.append(f"**标签**：{', '.join(entry['tags'])}")
                lines.append("")
            if entry.get("related_entries"):
                lines.append(f"**关联条目**：{', '.join(entry['related_entries'])}")
                lines.append("")

    # 写入
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"{OK} 报告已导出: {path}")


def _update_stats(entries: List[Dict]) -> Dict:
    """根据条目列表更新统计信息。

    Args:
        entries: 所有条目列表。

    Returns:
        更新后的统计字典。
    """
    by_category: Counter = Counter()
    by_severity: Counter = Counter()
    by_tag: Counter = Counter()

    for entry in entries:
        cat = entry.get("category", "unknown")
        sev = entry.get("severity", "unknown")
        by_category[cat] += 1
        by_severity[sev] += 1
        for tag in entry.get("tags", []):
            by_tag[tag] += 1

    return {
        "total_entries": len(entries),
        "by_category": dict(by_category.most_common()),
        "by_severity": dict(by_severity.most_common()),
        "by_tag": dict(by_tag.most_common()),
        "recent_pattern": "",
    }


def _extract_keywords(text: str) -> List[str]:
    """从中文/英文混合文本中提取关键词。

    简单实现：按标点分割 + 过滤停用词 + 去重。

    Args:
        text: 输入文本。

    Returns:
        关键词列表。
    """
    stop_words = {
        "的", "了", "在", "是", "和", "与", "或", "不", "有", "被",
        "将", "到", "从", "对", "为", "以", "及", "等", "也", "但",
        "而", "又", "于", "中", "上", "下", "时", "会", "能", "可以",
        "导致", "影响", "因为", "所以", "问题", "修复", "方法",
        "the", "a", "an", "is", "are", "was", "were", "be", "to",
        "of", "in", "for", "and", "or", "not", "with", "by",
        "from", "at", "on", "that", "this", "it",
    }

    tokens = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z_][a-zA-Z0-9_]*', text)
    keywords: List[str] = []
    seen: set = set()

    for token in tokens:
        if re.match(r'^[a-zA-Z]', token):
            word = token.lower()
        else:
            word = token

        if word not in stop_words and word not in seen:
            keywords.append(word)
            seen.add(word)
            # 中文长词再拆 2-gram
            if re.match(r'^[\u4e00-\u9fff]+$', token) and len(token) >= 4:
                for i in range(len(token) - 1):
                    bigram = token[i:i + 2]
                    if bigram not in stop_words and bigram not in seen:
                        keywords.append(bigram)
                        seen.add(bigram)

    return keywords


# ─────────────────────────────────────────────
# 交互式输入
# ─────────────────────────────────────────────

def _prompt_field(prompt_text: str, default: str = "") -> str:
    """从 stdin 读取一个字段值。"""
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"  {prompt_text}{suffix}: ").strip()
    except EOFError:
        print()
        return default
    return value if value else default


def _prompt_list_field(prompt_text: str, default: list = None) -> list:
    """从 stdin 读取逗号分隔的列表字段。"""
    if default is None:
        default = []
    default_str = ", ".join(default) if default else ""
    suffix = f" [{default_str}]" if default_str else ""
    try:
        value = input(f"  {prompt_text}（逗号分隔）{suffix}: ").strip()
    except EOFError:
        print()
        return default
    if not value:
        return default
    return [v.strip() for v in value.split(",") if v.strip()]


def _interactive_add() -> Dict:
    """交互式引导用户填写 debug 条目字段。"""
    print("=== 添加 Debug 经验记录 ===")
    print()

    print(f"  分类 ({'/'.join(CATEGORIES)}):")
    category = _prompt_field("  选择分类", "bug_fix")
    while category not in CATEGORIES:
        print(f"  {WARN} 无效分类，可选: {', '.join(CATEGORIES)}")
        category = _prompt_field("  选择分类", "bug_fix")

    print(f"  严重程度 ({'/'.join(SEVERITIES)}):")
    severity = _prompt_field("  选择严重程度", "major")
    while severity not in SEVERITIES:
        print(f"  {WARN} 无效严重程度，可选: {', '.join(SEVERITIES)}")
        severity = _prompt_field("  选择严重程度", "major")

    title = _prompt_field("  标题（简短描述）")
    context = _prompt_field("  发现过程（怎么发现的问题）")
    root_cause = _prompt_field("  根本原因分析")
    solution = _prompt_field("  解决方案（具体到代码/配置变更）")
    files_changed = _prompt_list_field("  变更文件路径")
    testing = _prompt_field("  验证方法（命令+结果）")
    lessons = _prompt_field("  经验教训")
    tags = _prompt_list_field("  标签")
    status = _prompt_field("  状态 (verified/pending_verification)", "pending_verification")
    while status not in ("verified", "pending_verification"):
        print(f"  {WARN} 无效状态，可选: verified, pending_verification")
        status = _prompt_field("  状态", "pending_verification")
    commit = _prompt_field("  关联提交（可选）")

    fields = {
        "category": category,
        "severity": severity,
        "title": title,
        "context": context,
        "root_cause": root_cause,
        "solution": solution,
        "files_changed": files_changed,
        "testing": testing,
        "lessons": lessons,
        "tags": tags,
        "status": status,
        "commit": commit,
    }
    return add_entry(fields)


# ─────────────────────────────────────────────
# 显示函数
# ─────────────────────────────────────────────

def _show_entry(entry: Dict) -> None:
    """格式化输出单个条目详情。"""
    print(f"{'=' * 60}")
    print(f"  ID:     {entry.get('id', 'unknown')}")
    print(f"  标题:   {entry.get('title', '(无标题)')}")
    print(f"  时间:   {entry.get('timestamp', '')}")
    print(f"  分类:   {entry.get('category', '')}")
    print(f"  严重度: {entry.get('severity', '')}")
    print(f"  状态:   {entry.get('status', '')}")
    if entry.get("commit"):
        print(f"  提交:   {entry['commit']}")
    print(f"{'-' * 60}")
    if entry.get("context"):
        print(f"  发现过程: {entry['context']}")
    if entry.get("root_cause"):
        print(f"  根因分析: {entry['root_cause']}")
    if entry.get("solution"):
        print(f"  解决方案: {entry['solution']}")
    if entry.get("files_changed"):
        print(f"  变更文件: {', '.join(entry['files_changed'])}")
    if entry.get("testing"):
        print(f"  验证方法: {entry['testing']}")
    if entry.get("lessons"):
        print(f"  经验教训: {entry['lessons']}")
    if entry.get("tags"):
        print(f"  标签:     {', '.join(entry['tags'])}")
    if entry.get("related_entries"):
        print(f"  关联条目: {', '.join(entry['related_entries'])}")
    print(f"{'=' * 60}")
    print()


def _show_list(entries: List[Dict]) -> None:
    """格式化输出条目列表。"""
    if not entries:
        print("（暂无条目）")
        return

    for entry in entries:
        sev_icon = {"critical": FAIL, "major": WARN, "minor": OK}.get(
            entry.get("severity", ""), PEND
        )
        status_icon = {"verified": OK, "pending_verification": PEND}.get(
            entry.get("status", ""), PEND
        )
        print(
            f"  {sev_icon} {entry.get('id', 'unknown'):20s} "
            f"[{entry.get('category', '')}] "
            f"[{entry.get('severity', '')}] "
            f"{status_icon} {entry.get('title', '(无标题)')}"
        )
    print(f"\n  共 {len(entries)} 条")


def _show_stats(stats: Dict) -> None:
    """格式化输出统计概览。"""
    print(f"  总条目数: {stats.get('total_entries', 0)}")
    print()

    by_cat = stats.get("by_category", {})
    if by_cat:
        print("  按分类:")
        for cat, count in by_cat.items():
            print(f"    {cat:25s} {count}")
    print()

    by_sev = stats.get("by_severity", {})
    if by_sev:
        print("  按严重程度:")
        for sev, count in by_sev.items():
            icon = {"critical": FAIL, "major": WARN, "minor": OK}.get(sev, PEND)
            print(f"    {icon} {sev:15s} {count}")
    print()

    by_tag = stats.get("by_tag", {})
    if by_tag:
        print("  按标签 (Top 15):")
        for i, (tag, count) in enumerate(by_tag.items()):
            if i >= 15:
                print(f"    ... 共 {len(by_tag)} 个标签")
                break
            print(f"    #{tag}: {count}")


def _show_patterns(patterns: List[Dict]) -> None:
    """格式化输出高频模式。"""
    if not patterns:
        print("  （暂无高频模式，需要 >= 2 条同类记录才能检测到）")
        return

    print(f"  检测到 {len(patterns)} 个高频模式:\n")
    for p in patterns:
        marker = "[tag]" if p["type"] == "tag" else "[cause]"
        print(
            f"  {marker} {p['key']:30s} — 出现 {p['count']} 次 "
            f"(关联: {', '.join(p['entry_ids'])})"
        )


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> bool:
    """自检函数：验证数据文件读写、字段验证、统计计算、模式检测、报告导出。

    Returns:
        全部通过返回 True，否则 False。
    """
    print("=== debug_journal.py 自检 ===\n")

    global _JOURNAL_PATH_OVERRIDE
    all_passed = True
    test_dir = MEMORY_DIR / "_debug_journal_test"

    try:
        # ── 1. 数据文件读写 ──
        print("[1/6] 数据文件读写...")
        test_dir.mkdir(parents=True, exist_ok=True)
        _JOURNAL_PATH_OVERRIDE = test_dir / "test-journal.json"

        test_entry = add_entry({
            "category": "bug_fix",
            "severity": "critical",
            "title": "自检测试条目",
            "context": "单元测试自动生成",
            "root_cause": "测试用例",
            "solution": "自动验证",
            "files_changed": ["test.py"],
            "testing": "self-check",
            "lessons": "自动验证",
            "tags": ["self_check", "test"],
            "status": "verified",
            "commit": "test-001",
        })

        assert test_entry["id"].startswith("dj-"), f"ID 格式错误: {test_entry['id']}"
        assert test_entry["timestamp"].endswith("Z"), f"时间戳格式错误: {test_entry['timestamp']}"
        assert test_entry["category"] == "bug_fix"
        assert test_entry["severity"] == "critical"
        print(f"      {OK} 写入条目 {test_entry['id']}")

        data = _load_journal()
        assert len(data["entries"]) == 1, f"条目数错误: {len(data['entries'])}"
        print(f"      {OK} 读取验证通过")

        # ── 2. 字段验证 ──
        print("[2/6] 字段验证...")
        required_keys = [
            "id", "timestamp", "category", "severity", "title",
            "context", "root_cause", "solution", "files_changed",
            "testing", "lessons", "tags", "related_entries",
            "status", "commit",
        ]
        for key in required_keys:
            assert key in test_entry, f"缺少字段: {key}"
        print(f"      {OK} 15 个字段完整")

        # ── 3. 过滤与列表 ──
        print("[3/6] 过滤与列表...")
        all_entries = list_entries()
        assert len(all_entries) == 1

        filtered = list_entries({"category": "bug_fix"})
        assert len(filtered) == 1, f"category 过滤错误: {len(filtered)}"

        filtered = list_entries({"severity": "minor"})
        assert len(filtered) == 0, "severity 过滤错误"

        filtered = list_entries({"tag": "self_check"})
        assert len(filtered) == 1, "tag 过滤错误"

        filtered = list_entries({"status": "verified"})
        assert len(filtered) == 1, "status 过滤错误"

        print(f"      {OK} 过滤逻辑正确")

        add_entry({
            "category": "bug_fix",
            "severity": "major",
            "title": "自检测试条目2",
            "tags": ["self_check", "test"],
        })

        all_entries = list_entries()
        assert len(all_entries) == 2, f"条目总数错误: {len(all_entries)}"
        assert all_entries[0]["timestamp"] >= all_entries[1]["timestamp"], "排序错误"
        print(f"      {OK} 列表排序正确")

        # ── 4. 统计计算 ──
        print("[4/6] 统计计算...")
        stats = compute_stats()
        assert stats["total_entries"] == 2, f"总数错误: {stats['total_entries']}"
        assert stats["by_category"].get("bug_fix") == 2, "分类统计错误"
        assert stats["by_severity"].get("critical") == 1, "严重度统计错误"
        assert stats["by_severity"].get("major") == 1, "严重度统计错误"
        assert stats["by_tag"].get("self_check") == 2, "标签统计错误"
        print(f"      {OK} 统计数据正确")

        # ── 5. 模式检测 ──
        print("[5/6] 模式检测...")
        patterns = detect_patterns()
        tag_patterns = [p for p in patterns if p["type"] == "tag"]
        assert len(tag_patterns) >= 2, f"应检测到 >= 2 个标签模式，实际: {len(tag_patterns)}"
        pattern_keys = {p["key"] for p in tag_patterns}
        assert "self_check" in pattern_keys, "缺少 self_check 模式"
        assert "test" in pattern_keys, "缺少 test 模式"
        print(f"      {OK} 检测到 {len(patterns)} 个模式")

        # ── 6. 报告导出 ──
        print("[6/6] 报告导出...")
        test_report = test_dir / "test-report.md"
        export_report(test_report)
        assert test_report.exists(), "报告文件未生成"
        content = test_report.read_text(encoding="utf-8")
        assert "Debug 经验报告" in content, "报告标题缺失"
        assert "bug_fix" in content, "报告分类内容缺失"
        assert test_entry["id"] in content, "报告条目 ID 缺失"
        print(f"      {OK} 报告导出正确")

        print()
        print(f"{OK} 全部 6/6 项自检通过")

    except AssertionError as e:
        print(f"      {FAIL} 断言失败: {e}")
        all_passed = False
    except Exception as e:
        print(f"      {FAIL} 错误: {e}")
        all_passed = False
    finally:
        _JOURNAL_PATH_OVERRIDE = None
        import shutil
        try:
            if test_dir.exists():
                shutil.rmtree(str(test_dir))
        except OSError:
            pass

    return all_passed


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main() -> None:
    """CLI 入口函数。"""
    parser = argparse.ArgumentParser(
        description="CoPilot Debug 经验记录系统",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # add
    add_p = subparsers.add_parser("add", help="添加 debug 经验记录")
    add_p.add_argument(
        "--json", dest="json_str",
        help="非交互式添加，传入 JSON 字符串",
    )

    # list
    list_p = subparsers.add_parser("list", help="列出条目")
    list_p.add_argument("--category", help="按分类过滤")
    list_p.add_argument("--severity", help="按严重程度过滤")
    list_p.add_argument("--tag", help="按标签过滤")
    list_p.add_argument("--status", help="按状态过滤")

    # show
    show_p = subparsers.add_parser("show", help="显示条目详情")
    show_p.add_argument("entry_id", help="条目 ID")

    # stats
    subparsers.add_parser("stats", help="统计概览")

    # patterns
    subparsers.add_parser("patterns", help="检测高频模式")

    # export
    export_p = subparsers.add_parser("export", help="导出 Markdown 报告")
    export_p.add_argument("--output", dest="output_path", help="自定义输出路径")

    # self-check
    parser.add_argument("--self-check", action="store_true", help="运行自检")

    args = parser.parse_args()

    # ── 自检模式 ──
    if args.self_check:
        passed = _self_check()
        sys.exit(0 if passed else 1)
        return

    # ── 子命令分发 ──
    if args.command == "add":
        if args.json_str:
            try:
                fields = json.loads(args.json_str)
            except json.JSONDecodeError as e:
                print(f"{FAIL} JSON 解析失败: {e}")
                sys.exit(1)
            entry = add_entry(fields)
            print(f"{OK} 已添加: {entry['id']} — {entry.get('title', '')}")
        else:
            entry = _interactive_add()
            print(f"\n{OK} 已添加: {entry['id']} — {entry.get('title', '')}")

    elif args.command == "list":
        filters = {}
        if args.category:
            filters["category"] = args.category
        if args.severity:
            filters["severity"] = args.severity
        if args.tag:
            filters["tag"] = args.tag
        if args.status:
            filters["status"] = args.status
        entries = list_entries(filters)
        _show_list(entries)

    elif args.command == "show":
        data = _load_journal()
        target = None
        for e in data["entries"]:
            if e["id"] == args.entry_id:
                target = e
                break
        if target:
            _show_entry(target)
        else:
            print(f"{FAIL} 未找到条目: {args.entry_id}")
            sys.exit(1)

    elif args.command == "stats":
        stats = compute_stats()
        _show_stats(stats)

    elif args.command == "patterns":
        patterns = detect_patterns()
        _show_patterns(patterns)

    elif args.command == "export":
        out = Path(args.output_path) if args.output_path else None
        export_report(out)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
