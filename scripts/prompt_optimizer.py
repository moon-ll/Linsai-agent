#!/usr/bin/env python3
"""prompt_optimizer.py — Prompt 闭环优化器（v6.8 林赛协作引擎）

从 failure_analyzer 的建议、debug journal 的 prompt_tuning 条目、agent-scores 的奖惩记录
综合分析，生成针对 hermes prompt 模板的具体修改建议，并自动应用。

hermes prompt 模板位于 ~/.hermes/profiles/{profile}/ 目录，主要入口为 SOUL.md。
修改前自动备份到 memory/prompt-backups/。

数据源:
- memory/debug-journal.json — category=prompt_tuning 的条目
- memory/agent-scores.json — writer/critic 带 reason 的奖惩记录
- scripts/failure_analyzer.py — PATTERN_LIBRARY 中定义的模式和建议
- ~/.hermes/profiles/{profile}/SOUL.md — hermes prompt 模板

输出:
- memory/prompt-suggestions.json — 建议记录（含应用状态）
- memory/prompt-backups/ — 应用前的备份

用法:
    python3 scripts/prompt_optimizer.py analyze              # 分析并生成建议
    python3 scripts/prompt_optimizer.py auto                 # 自动模式：分析+应用（cron 调用）
    python3 scripts/prompt_optimizer.py list                 # 列出建议
    python3 scripts/prompt_optimizer.py apply --id <id>       # 手动应用单条建议
    python3 scripts/prompt_optimizer.py apply --all           # 手动应用全部
    python3 scripts/prompt_optimizer.py --self-check          # 自检
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ─────────────────────────────────────────────
# 路径与常量
# ─────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
MEMORY_DIR = PROJECT_ROOT / "memory"

DEBUG_JOURNAL_PATH = MEMORY_DIR / "debug-journal.json"
AGENT_SCORES_PATH = MEMORY_DIR / "agent-scores.json"
SUGGESTIONS_PATH = MEMORY_DIR / "prompt-suggestions.json"
BACKUPS_DIR = MEMORY_DIR / "prompt-backups"

HERMES_PROFILES_DIR = Path.home() / ".hermes" / "profiles"

# 需要分析的 profile 列表
TARGET_PROFILES = ["writer", "critic", "researcher", "analyst", "linsai"]

# profile 别名到 prompt 文件的映射
PROFILE_PROMPT_MAP = {
    "writer": ["SOUL.md"],
    "critic": ["SOUL.md"],
    "researcher": ["SOUL.md"],
    "analyst": ["SOUL.md"],
    "linsai": ["SOUL.md"],
}

# v6.8.22 修复：debug journal 采集时间窗口（天数）。
# 历史背景：_log_auto_applied 会把每条成功应用写入一条 prompt_tuning 日志，
# 下次 auto 运行时会重新读取全部 prompt_tuning 条目作为输入 → 指数级膨胀。
# 限制窗口后，旧条目不再被采集，避免循环放大。
DEBUG_JOURNAL_WINDOW_DAYS = 7

# v6.8.22 修复：单次 auto 运行中，同一目标文件最多备份次数。
# 历史背景：内容已存在时仍会先备份再 return True，每天数千次备份浪费磁盘。
MAX_BACKUPS_PER_FILE_PER_RUN = 1

# failure_analyzer 模式到目标 profile 的映射
PATTERN_TO_PROFILE = {
    "score-zero-streak": "critic",
    "empty-draft": "writer",
    "env-pollution": None,  # 已修复
    "profile-timeout": None,  # 配置层面
    "file-missing": None,  # 代码层面
    "code-bug": None,  # 代码层面
    "rate-limit": None,  # 外部依赖
    "low-content-after-rewrite": "writer",
}


# ─────────────────────────────────────────────
# 数据加载
# ─────────────────────────────────────────────

def _load_json(path: Path, default: Any = None) -> Any:
    """加载 JSON 文件，失败时返回 default。"""
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def _save_json(path: Path, data: Any) -> None:
    """保存 JSON 文件（原子写入）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(path))
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def _now_utc() -> str:
    """返回当前 UTC ISO 字符串。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────────────────────────────
# 数据采集
# ─────────────────────────────────────────────

def _collect_debug_journal_entries() -> List[Dict]:
    """从 debug-journal.json 读取 category=prompt_tuning 的条目。

    v6.8.22: 限制为最近 DEBUG_JOURNAL_WINDOW_DAYS 天窗口内的条目，
    避免历史累积导致指数级膨胀（每条 auto 应用都会写入新 prompt_tuning
    条目，下次 auto 又读取 → 循环放大）。
    """
    data = _load_json(DEBUG_JOURNAL_PATH)
    entries = data.get("entries", [])

    # 计算 cutoff 时间戳（debug journal 的 timestamp 是 UTC ISO 格式）
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=DEBUG_JOURNAL_WINDOW_DAYS)

    result = []
    for e in entries:
        if e.get("category") != "prompt_tuning":
            continue
        ts = e.get("timestamp") or e.get("created_at") or ""
        # 解析并比较时间戳；解析失败的条目跳过（避免污染采集）
        try:
            from datetime import datetime as _dt
            entry_dt = _dt.strptime(ts[:19] + "Z", "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if entry_dt < cutoff:
                continue
        except (ValueError, TypeError):
            continue
        result.append(e)
    return result


def _collect_agent_score_reasons() -> List[Dict]:
    """从 agent-scores.json 中提取带 reason 的奖惩记录。"""
    data = _load_json(AGENT_SCORES_PATH)
    result = []

    for agent_name in ["writer", "critic"]:
        agent_data = data.get(agent_name, {})
        # 从 history 中提取带 reason 的记录
        for h in agent_data.get("history", []):
            reason = h.get("reason", "")
            if reason and len(reason.strip()) > 50:  # 只取有实质内容的
                result.append({
                    "agent": agent_name,
                    "round_ref": h.get("round_ref", ""),
                    "delta": h.get("delta", 0),
                    "reason": reason[:500],  # 截断
                    "at": h.get("at", ""),
                    "type": "score_change",
                })

        # 从 prohibition_violations 中提取
        for v in agent_data.get("prohibition_violations", []):
            vtype = v.get("type", "")
            if vtype and len(vtype.strip()) > 20:
                result.append({
                    "agent": agent_name,
                    "round_ref": v.get("round_ref", ""),
                    "delta": v.get("penalty", 0),
                    "reason": vtype[:500],
                    "at": v.get("at", ""),
                    "type": "prohibition_violation",
                })

    # 按 delta 排序，最负面优先
    result.sort(key=lambda x: x.get("delta", 0))
    return result


def _collect_failure_patterns() -> List[Dict]:
    """从 failure_analyzer.py 的 PATTERN_LIBRARY 读取模式和建议。"""
    patterns = []

    # 直接从 failure_analyzer 模块导入
    try:
        # 将 scripts 目录加入 sys.path
        scripts_dir = str(PROJECT_ROOT / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from failure_analyzer import PATTERN_LIBRARY

        for pat in PATTERN_LIBRARY:
            target_profile = PATTERN_TO_PROFILE.get(pat["id"])
            if target_profile and pat.get("suggested_prompt_change"):
                patterns.append({
                    "pattern_id": pat["id"],
                    "label": pat["label"],
                    "category": pat.get("category", ""),
                    "target_profile": target_profile,
                    "suggested_change": pat["suggested_prompt_change"],
                    "expected_impact": pat.get("expected_impact", ""),
                })
    except ImportError:
        # 如果无法导入，使用内联的 PATTERN_LIBRARY 副本
        patterns = _inline_pattern_library()

    return patterns


def _inline_pattern_library() -> List[Dict]:
    """内联的 PATTERN_LIBRARY 副本（当无法导入 failure_analyzer 时使用）。"""
    return [
        {
            "pattern_id": "score-zero-streak",
            "label": "连续 0 分（申请书内容空）",
            "category": "评分异常",
            "target_profile": "critic",
            "suggested_change": (
                "在 critic prompt 中明确：当申请书内容为占位符时，给 0.10 而非 0.00，"
                "并加 '本轮因内容缺失无法准确评分，建议先补充实质内容'。"
            ),
            "expected_impact": "score_history 能区分'空草稿'vs'完全失败'，避免连续 0 分触发无提升退出",
        },
        {
            "pattern_id": "empty-draft",
            "label": "申请书草稿为空",
            "category": "数据缺失",
            "target_profile": "writer",
            "suggested_change": (
                "在 writer 派活前增加预检：若 proposal-draft.md < 500 字节，"
                "先调用 writer 写一版'骨架充实版'再进入对抗循环。"
            ),
            "expected_impact": "避免对空草稿做无意义的对抗评审",
        },
        {
            "pattern_id": "low-content-after-rewrite",
            "label": "writer 优化后内容未实质性增长",
            "category": "数据缺失",
            "target_profile": "writer",
            "suggested_change": (
                "在 writer prompt 中明确：'请基于 brief 实质扩写申请书，"
                "总字数 ≥ 4000 字，每章节 ≥ 1200 字'。"
            ),
            "expected_impact": "避免 writer 仅做表面修改",
        },
    ]


def _discover_prompt_files() -> Dict[str, List[Path]]:
    """探索 hermes profiles 目录，发现可修改的 prompt 文件。"""
    result: Dict[str, List[Path]] = {}

    for profile in TARGET_PROFILES:
        profile_dir = HERMES_PROFILES_DIR / profile
        if not profile_dir.exists():
            continue

        prompt_files = []
        # 主 prompt 文件：SOUL.md
        soul_path = profile_dir / "SOUL.md"
        if soul_path.exists():
            prompt_files.append(soul_path)

        # 探索其他可能的 prompt 文件（prompts/ 子目录）
        prompts_dir = profile_dir / "prompts"
        if prompts_dir.exists():
            for md_file in prompts_dir.glob("**/*.md"):
                prompt_files.append(md_file)

        # 探索 memories/ 目录中的 USER.md（可能包含行为指令）
        user_md = profile_dir / "memories" / "USER.md"
        if user_md.exists():
            prompt_files.append(user_md)

        if prompt_files:
            result[profile] = prompt_files

    return result


# ─────────────────────────────────────────────
# 建议生成
# ─────────────────────────────────────────────

def _generate_suggestion_id() -> str:
    """生成唯一建议 ID。"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    # 加上 4 位随机数
    import random
    rand_part = f"{random.randint(0, 9999):04d}"
    return f"ps-{ts}-{rand_part}"


def _analyze_reasons_for_prompt_hints(reasons: List[Dict]) -> List[Dict]:
    """从 agent 分数原因中提取 prompt 相关的改进建议。"""
    suggestions = []

    # 常见问题模式关键词
    writer_patterns = [
        (r"零修改|完全未执行|逐字节相同|MD5.*一致|无实质性", "writer", "high",
         "writer 提交与上一轮相同的文件，需在 prompt 中强化'必须基于 critic 建议做实质性修改'的指令"),
        (r"表面修改|仅删除|仅增加.*分隔线|未实质回应", "writer", "medium",
         "writer 仅做表面修改，需在 prompt 中要求逐条回应 critic 的每个问题"),
        (r"占位符|待.*核验|TBD", "writer", "high",
         "writer 输出中残留占位符/TBD，需在 prompt 中明确禁止提交含占位符的内容"),
        (r"AI生成痕迹|优化记录|元信息", "writer", "high",
         "writer 输出中残留 AI 工作流元信息，需在 prompt 中要求清理所有迭代痕迹"),
    ]

    critic_patterns = [
        (r"事实错误|事实核查.*失职|基于错误.*前提", "critic", "high",
         "critic 评审基于错误的事实前提，需在 prompt 中强化'先核实文件状态再下结论'"),
        (r"过时的文件|文件系统快照", "critic", "medium",
         "critic 使用过时的文件状态信息，需在 prompt 中要求重新读取最新文件"),
        (r"评分.*不一致|综合分.*自报.*不匹配", "critic", "medium",
         "critic 报告内评分不一致，需在 prompt 中明确评分公式的自洽性要求"),
    ]

    all_patterns = writer_patterns + critic_patterns
    matched_patterns: Dict[str, int] = Counter()

    for r in reasons[:50]:  # 只检查最近 50 条
        reason_text = r.get("reason", "")
        agent = r.get("agent", "")

        for pattern, target, priority, description in all_patterns:
            if re.search(pattern, reason_text, re.IGNORECASE):
                key = f"{target}:{description[:50]}"
                matched_patterns[key] += 1

                if matched_patterns[key] == 1:  # 每种模式只建议一次
                    suggestions.append({
                        "source": "agent_score_analysis",
                        "pattern_key": key,
                        "target_profile": target,
                        "priority": priority,
                        "description": description,
                        "evidence_count": matched_patterns[key],
                        "sample_round_ref": r.get("round_ref", ""),
                    })

    # 更新 evidence_count
    for s in suggestions:
        key = f"{s['target_profile']}:{s['description'][:50]}"
        s["evidence_count"] = matched_patterns.get(key, 1)

    return suggestions


def _generate_suggestions(
    debug_entries: List[Dict],
    score_reasons: List[Dict],
    failure_patterns: List[Dict],
    prompt_files: Dict[str, List[Path]],
) -> List[Dict]:
    """综合所有数据源生成 prompt 修改建议。"""
    suggestions = []
    existing_ids: set = set()

    # 加载已有建议（避免重复）
    existing = _load_suggestions()
    for s in existing:
        existing_ids.add(s.get("fingerprint", ""))

    # 1. 从 failure_analyzer 模式生成建议
    for pat in failure_patterns:
        profile = pat["target_profile"]
        files = prompt_files.get(profile, [])
        if not files:
            continue

        target_file = files[0]  # 默认修改第一个（通常是 SOUL.md）
        target_file_rel = f"~/.hermes/profiles/{profile}/{target_file.name}"

        fingerprint = hashlib.md5(
            f"failure_analyzer:{pat['pattern_id']}".encode()
        ).hexdigest()[:12]

        if fingerprint in existing_ids:
            continue

        suggestions.append({
            "id": _generate_suggestion_id(),
            "source": "failure_analyzer",
            "pattern_id": pat["pattern_id"],
            "pattern_label": pat["label"],
            "target_profile": profile,
            "target_file": str(target_file),
            "target_file_display": target_file_rel,
            "priority": "high",
            "action": "append",
            "content": (
                f"\n## 优化规则（自动添加 {datetime.now(timezone.utc).strftime('%Y-%m-%d')}）\n\n"
                f"{pat['suggested_change']}\n"
            ),
            "description": f"[{pat['category']}] {pat['label']}：{pat['suggested_change'][:100]}",
            "expected_impact": pat.get("expected_impact", ""),
            "fingerprint": fingerprint,
            "status": "pending",
            "created_at": _now_utc(),
        })

    # 2. 从 debug journal prompt_tuning 条目生成建议
    for entry in debug_entries:
        title = entry.get("title", "")
        solution = entry.get("solution", "")
        tags = entry.get("tags", [])
        entry_id = entry.get("id", "")

        # 确定目标 profile
        target_profile = None
        for tag in tags:
            if tag in ("writer", "critic", "researcher", "analyst"):
                target_profile = tag
                break

        if not target_profile:
            target_profile = "writer"  # 默认 writer

        files = prompt_files.get(target_profile, [])
        if not files:
            continue

        target_file = files[0]
        target_file_rel = f"~/.hermes/profiles/{target_profile}/{target_file.name}"

        fingerprint = hashlib.md5(
            f"debug_journal:{entry_id}".encode()
        ).hexdigest()[:12]

        if fingerprint in existing_ids:
            continue

        suggestions.append({
            "id": _generate_suggestion_id(),
            "source": "debug_journal",
            "entry_id": entry_id,
            "target_profile": target_profile,
            "target_file": str(target_file),
            "target_file_display": target_file_rel,
            "priority": "high" if entry.get("severity") == "critical" else "medium",
            "action": "append",
            "content": (
                f"\n## 优化规则（来自 debug {entry_id}）\n\n"
                f"{solution}\n"
            ),
            "description": f"[{entry.get('category', '')}] {title}",
            "expected_impact": entry.get("lessons", ""),
            "fingerprint": fingerprint,
            "status": "pending",
            "created_at": _now_utc(),
        })

    # 3. 从 agent 分数原因中分析 prompt 改进
    score_hints = _analyze_reasons_for_prompt_hints(score_reasons)
    for hint in score_hints:
        profile = hint["target_profile"]
        files = prompt_files.get(profile, [])
        if not files:
            continue

        target_file = files[0]
        target_file_rel = f"~/.hermes/profiles/{profile}/{target_file.name}"

        fingerprint = hashlib.md5(
            f"score_analysis:{hint['pattern_key']}".encode()
        ).hexdigest()[:12]

        if fingerprint in existing_ids:
            continue

        suggestions.append({
            "id": _generate_suggestion_id(),
            "source": "agent_score_analysis",
            "pattern_key": hint["pattern_key"],
            "target_profile": profile,
            "target_file": str(target_file),
            "target_file_display": target_file_rel,
            "priority": hint["priority"],
            "action": "append",
            "content": (
                f"\n## 行为约束（来自评分分析，{hint['evidence_count']} 次证据）\n\n"
                f"{hint['description']}\n"
            ),
            "description": f"[{profile}] {hint['description'][:100]}",
            "expected_impact": f"减少重复出现的 {profile} 问题模式",
            "fingerprint": fingerprint,
            "status": "pending",
            "created_at": _now_utc(),
        })

    return suggestions


# ─────────────────────────────────────────────
# 建议管理
# ─────────────────────────────────────────────

def _load_suggestions() -> List[Dict]:
    """加载已有建议列表。"""
    return _load_json(SUGGESTIONS_PATH, [])


def _save_suggestions(suggestions: List[Dict]) -> None:
    """保存建议列表。"""
    _save_json(SUGGESTIONS_PATH, suggestions)


def _apply_suggestion(
    suggestion: Dict,
    backup_count_tracker: Optional[Dict[str, int]] = None,
) -> bool:
    """应用单条建议到 hermes prompt 文件。

    v6.8.22: 新增 backup_count_tracker 参数。当同一目标文件已被本次 run
    备份过 MAX_BACKUPS_PER_FILE_PER_RUN 次时，跳过备份（仅 skip）。
    历史背景：内容已存在时旧版本也会先 backup 再 return True，导致每天
    数千次冗余备份（每个 ~4.6MB），占用磁盘；新版本先 read 检查内容，
    已存在则跳过 backup，直接返回 True。

    Args:
        suggestion: 单条建议 dict。
        backup_count_tracker: 可选 dict，key=target_file 路径，value=已备份次数。
            同一 run 内复用此 dict 可限制单文件备份次数。

    Returns:
        True 表示成功（含"内容已存在"的跳过），False 表示失败。
    """
    target_file = Path(suggestion["target_file"])

    if not target_file.exists():
        print(f"  ✗ 目标文件不存在：{target_file}")
        return False

    # 读取当前内容（先于备份，避免"内容已存在"场景下浪费磁盘）
    try:
        current_content = target_file.read_text(encoding="utf-8")
    except PermissionError:
        print(f"  ✗ 读取失败（权限不足）：{target_file}")
        suggestion["apply_error"] = "read_permission_denied"
        return False

    # 检查是否已经包含相同内容（避免重复添加）—— v6.8.22: 在备份前判定
    content_to_add = suggestion.get("content", "").strip()
    if content_to_add in current_content:
        print(f"  ○ 内容已存在，跳过（不备份、不写入）")
        return True

    # 仅当确实需要写入时才执行备份
    backup_dir = BACKUPS_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)

    profile = suggestion.get("target_profile", "unknown")
    filename = target_file.name
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = backup_dir / f"{profile}-{filename}-{ts}.bak"

    # v6.8.22: 单次 run 内对同一文件最多备份 MAX_BACKUPS_PER_FILE_PER_RUN 次
    if backup_count_tracker is not None:
        key = str(target_file)
        current_count = backup_count_tracker.get(key, 0)
        if current_count >= MAX_BACKUPS_PER_FILE_PER_RUN:
            print(f"  ○ 本 run 已备份 {key} 达到上限，跳过备份")
        else:
            try:
                shutil.copy2(str(target_file), str(backup_path))
                backup_count_tracker[key] = current_count + 1
                print(f"  ✓ 备份至：{backup_path}")
            except PermissionError:
                print(f"  ✗ 备份失败（权限不足）：{target_file}")
                suggestion["apply_error"] = "backup_permission_denied"
                return False
    else:
        try:
            shutil.copy2(str(target_file), str(backup_path))
            print(f"  ✓ 备份至：{backup_path}")
        except PermissionError:
            print(f"  ✗ 备份失败（权限不足）：{target_file}")
            suggestion["apply_error"] = "backup_permission_denied"
            return False

    # 添加到文件末尾
    new_content = current_content.rstrip() + "\n" + content_to_add + "\n"
    try:
        target_file.write_text(new_content, encoding="utf-8")
    except PermissionError:
        print(f"  ✗ 写入失败（权限不足）：{target_file}")
        suggestion["apply_error"] = "write_permission_denied"
        return False

    print(f"  ✓ 已修改：{target_file}")
    return True


# ─────────────────────────────────────────────
# CLI 命令
# ─────────────────────────────────────────────

def cmd_analyze() -> None:
    """分析并生成建议。"""
    print("=== Prompt 优化建议分析 ===")
    print()

    # 1. 采集数据
    debug_entries = _collect_debug_journal_entries()
    score_reasons = _collect_agent_score_reasons()
    failure_patterns = _collect_failure_patterns()
    prompt_files = _discover_prompt_files()

    print(f"  数据源采集完成：")
    print(f"    debug journal（prompt_tuning, 最近 {DEBUG_JOURNAL_WINDOW_DAYS}d 窗口）: {len(debug_entries)} 条")
    print(f"    agent score reasons: {len(score_reasons)} 条")
    print(f"    failure patterns: {len(failure_patterns)} 条")
    print(f"    prompt 文件: {sum(len(v) for v in prompt_files.values())} 个")
    print()

    # 发现的 prompt 文件
    print("  发现的 prompt 文件：")
    for profile, files in sorted(prompt_files.items()):
        for f in files:
            rel = f.relative_to(HERMES_PROFILES_DIR)
            print(f"    {profile}: {rel}")
    print()

    # 生成建议
    new_suggestions = _generate_suggestions(
        debug_entries, score_reasons, failure_patterns, prompt_files
    )

    # 合并到已有建议
    existing = _load_suggestions()
    all_suggestions = existing + new_suggestions
    _save_suggestions(all_suggestions)

    print(f"  ✓ 新生成建议：{len(new_suggestions)} 条")
    print(f"  ✓ 待确认总计：{len([s for s in all_suggestions if s['status'] == 'pending'])} 条")
    print()

    # 展示新建议
    if new_suggestions:
        print("  新建议详情：")
        for i, s in enumerate(new_suggestions, 1):
            print(f"    [{s['priority'].upper()}] {s['id']}")
            print(f"      目标：{s['target_profile']}/{Path(s['target_file']).name}")
            print(f"      来源：{s['source']}")
            print(f"      说明：{s['description'][:80]}")
            print()
    else:
        print("  ○ 无新建议（可能已有相同建议或数据无变化）")


def cmd_list() -> None:
    """列出待确认的建议。"""
    suggestions = _load_suggestions()
    pending = [s for s in suggestions if s.get("status") == "pending"]
    applied = [s for s in suggestions if s.get("status") == "applied"]

    print(f"=== Prompt 修改建议 ===")
    print(f"  待确认：{len(pending)} 条 | 已应用：{len(applied)} 条")
    print()

    if pending:
        for i, s in enumerate(pending, 1):
            print(f"  {i}. [{s['priority'].upper()}] {s['id']}")
            print(f"     目标：{s['target_profile']}/{Path(s['target_file']).name}")
            print(f"     来源：{s['source']}")
            print(f"     说明：{s['description'][:100]}")
            print(f"     操作：{s['action']} | 创建于：{s['created_at']}")
            print()
    else:
        print("  ○ 无待确认建议")


def cmd_apply(suggestion_id: Optional[str] = None, apply_all: bool = False) -> None:
    """手动应用建议。"""
    suggestions = _load_suggestions()
    pending = [s for s in suggestions if s.get("status") == "pending"]

    if not pending:
        print("○ 无待确认建议")
        return

    if apply_all:
        to_apply = pending
        print(f"=== 手动应用全部建议（{len(to_apply)} 条）===")
    elif suggestion_id:
        to_apply = [s for s in pending if s.get("id") == suggestion_id]
        if not to_apply:
            print(f"✗ 未找到待确认建议：{suggestion_id}")
            return
    else:
        print("✗ 请指定 --id <id> 或 --all")
        return

    _apply_suggestions(to_apply, suggestions)


def cmd_auto() -> None:
    """自动模式：分析 + 应用（cron 调用入口）。

    流程：
    1. 采集数据并生成新建议
    2. 过滤出安全等级的建议（排除 critical 级别的激进修改）
    3. 自动应用，记录日志
    4. 输出执行摘要
    """
    import subprocess

    print("=== Prompt 自动优化（auto 模式）===")
    print()

    # 1. 采集数据
    debug_entries = _collect_debug_journal_entries()
    score_reasons = _collect_agent_score_reasons()
    failure_patterns = _collect_failure_patterns()
    prompt_files = _discover_prompt_files()

    new_suggestions = _generate_suggestions(
        debug_entries, score_reasons, failure_patterns, prompt_files
    )

    all_suggestions = _load_suggestions()

    # 将新建议合并到 all_suggestions（确保应用后状态变更被保存）
    if new_suggestions:
        all_suggestions.extend(new_suggestions)
        _save_suggestions(all_suggestions)

    if not new_suggestions:
        # 没有新建议，检查是否有遗留的 pending 建议
        pending = [s for s in all_suggestions if s.get("status") == "pending"]
        if pending:
            safe_pending = [s for s in pending if s.get("priority") in ("high", "medium")]
            if safe_pending:
                print(f"○ 无新建议，但发现 {len(safe_pending)} 条遗留 pending 建议，自动应用")
                backup_tracker: Dict[str, int] = {}
                _apply_suggestions(
                    safe_pending, all_suggestions, auto_mode=True,
                    backup_count_tracker=backup_tracker,
                )
                _log_auto_applied(safe_pending)
                print("\n✓ 自动优化完成")
                return
        print("○ 无新建议，无需操作")
        return

    print(f"  新生成建议：{len(new_suggestions)} 条")

    # 2. 安全过滤：只自动应用 high/medium 级别，跳过 critical
    safe_suggestions = [s for s in new_suggestions if s.get("priority") in ("high", "medium")]
    skipped = [s for s in new_suggestions if s.get("priority") not in ("high", "medium")]

    if skipped:
        print(f"  跳过 {len(skipped)} 条（priority 不在 high/medium）")
        for s in skipped:
            print(f"    [{s['priority'].upper()}] {s['id']}: {s['description'][:60]}")

    # 同时收集遗留的 pending 建议
    existing_pending = [
        s for s in all_suggestions
        if s.get("status") == "pending" and s.get("priority") in ("high", "medium")
    ]
    if existing_pending:
        print(f"  另发现 {len(existing_pending)} 条遗留 pending 建议，一并处理")

    to_apply = safe_suggestions + existing_pending
    if not to_apply:
        print("○ 无安全等级建议可应用")
        return

    # 3. 应用
    print(f"\n  自动应用 {len(to_apply)} 条建议：")
    # v6.8.22: 同一 run 内对同一文件最多备份 MAX_BACKUPS_PER_FILE_PER_RUN 次
    backup_tracker: Dict[str, int] = {}
    _apply_suggestions(
        to_apply, all_suggestions, auto_mode=True,
        backup_count_tracker=backup_tracker,
    )

    # 只记录成功应用的
    applied_ok = [s for s in to_apply if s.get("status") == "applied"]
    if applied_ok:
        _log_auto_applied(applied_ok)

    print("\n✓ 自动优化完成")


def _log_auto_applied(suggestions: List[Dict]) -> None:
    """将自动应用的记录写入 debug journal。"""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import debug_journal
        for s in suggestions:
            debug_journal.add_entry({
                "category": "prompt_tuning",
                "severity": "minor",
                "title": f"Prompt 自动优化：{s['target_profile']}/{Path(s['target_file']).name}",
                "context": f"来源：{s['source']}",
                "root_cause": s.get("description", ""),
                "solution": f"自动修改 hermes prompt 文件，操作：{s.get('action', 'append')}",
                "files_changed": [s.get("target_file", "")],
                "testing": "已备份原文件，修改后 hermes 下次 agent loop 自动生效",
                "lessons": s.get("description", ""),
                "tags": ["prompt_optimization", "auto_applied", s.get("target_profile", "")],
                "status": "verified",
            })
    except Exception:
        pass


def _apply_suggestions(
    to_apply: List[Dict],
    all_suggestions: List[Dict],
    auto_mode: bool = False,
    backup_count_tracker: Optional[Dict[str, int]] = None,
) -> None:
    """应用建议列表（内部共享函数）。

    v6.8.22: 新增 backup_count_tracker 参数，限制单次 run 内同一文件的
    备份次数（防止指数级备份浪费磁盘）。
    """
    success_count = 0
    fail_count = 0

    for s in to_apply:
        label = "自动" if auto_mode else "手动"
        print(f"\n{label}应用 {s['id']}：{s['description'][:60]}")
        if _apply_suggestion(s, backup_count_tracker=backup_count_tracker):
            s["status"] = "applied"
            s["applied_at"] = _now_utc()
            s["applied_mode"] = "auto" if auto_mode else "manual"
            s.pop("apply_error", None)
            success_count += 1
        else:
            # 失败标记为 failed，下次 auto 不会再选
            s["status"] = "failed"
            s["failed_at"] = _now_utc()
            s["failed_mode"] = "auto" if auto_mode else "manual"
            fail_count += 1

    # 保存更新
    _save_suggestions(all_suggestions)

    print(f"\n✓ 完成：成功 {success_count}，失败 {fail_count}")


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> None:
    """自检：验证脚本基本功能正确。"""
    print("=== prompt_optimizer._self_check ===")

    # 1. 路径检查
    assert PROJECT_ROOT.exists(), f"PROJECT_ROOT 不存在：{PROJECT_ROOT}"
    assert MEMORY_DIR.exists(), f"MEMORY_DIR 不存在：{MEMORY_DIR}"
    print("  ✓ 路径常量正确")

    # 2. 数据文件检查
    for path, name in [
        (DEBUG_JOURNAL_PATH, "debug-journal.json"),
        (AGENT_SCORES_PATH, "agent-scores.json"),
    ]:
        if path.exists():
            data = _load_json(path)
            print(f"  ✓ {name} 加载成功")
        else:
            print(f"  ○ {name} 不存在")

    # 3. hermes profiles 目录检查
    if HERMES_PROFILES_DIR.exists():
        profiles = [d.name for d in HERMES_PROFILES_DIR.iterdir() if d.is_dir()]
        print(f"  ✓ hermes profiles 目录存在（{len(profiles)} 个 profile）")

        # 检查目标 profile
        found_profiles = []
        for p in TARGET_PROFILES:
            if (HERMES_PROFILES_DIR / p).exists():
                found_profiles.append(p)
        print(f"  ✓ 目标 profile 已找到：{found_profiles}")
    else:
        print(f"  ○ hermes profiles 目录不存在：{HERMES_PROFILES_DIR}")

    # 4. 数据采集测试
    debug_entries = _collect_debug_journal_entries()
    print(f"  ✓ debug journal 采集：{len(debug_entries)} 条 prompt_tuning（窗口 {DEBUG_JOURNAL_WINDOW_DAYS}d）")

    score_reasons = _collect_agent_score_reasons()
    print(f"  ✓ agent score reasons 采集：{len(score_reasons)} 条")

    failure_patterns = _collect_failure_patterns()
    print(f"  ✓ failure patterns 采集：{len(failure_patterns)} 条")

    # 5. prompt 文件发现测试
    prompt_files = _discover_prompt_files()
    total_files = sum(len(v) for v in prompt_files.values())
    print(f"  ✓ prompt 文件发现：{total_files} 个文件")
    for profile, files in sorted(prompt_files.items()):
        print(f"      {profile}: {len(files)} 个")

    # 6. 建议生成测试
    if prompt_files:
        suggestions = _generate_suggestions(
            debug_entries, score_reasons, failure_patterns, prompt_files
        )
        print(f"  ✓ 建议生成测试：{len(suggestions)} 条")

        # 验证建议结构
        for s in suggestions:
            assert "id" in s, "建议缺少 id"
            assert "target_profile" in s, "建议缺少 target_profile"
            assert "target_file" in s, "建议缺少 target_file"
            assert "content" in s, "建议缺少 content"
            assert "fingerprint" in s, "建议缺少 fingerprint"
            assert s["status"] == "pending"
        print(f"  ✓ 建议结构验证通过")
    else:
        print("  ○ 跳过建议生成测试（无 prompt 文件）")

    # 7. 原因分析测试
    if score_reasons:
        hints = _analyze_reasons_for_prompt_hints(score_reasons)
        print(f"  ✓ 原因分析测试：{len(hints)} 条 prompt 提示")
    else:
        print("  ○ 跳过原因分析测试（无 score reasons）")

    # 8. 建议文件 I/O 测试
    test_suggestions_path = MEMORY_DIR / "test-prompt-suggestions.json"
    test_data = [{"id": "test-001", "status": "pending"}]
    _save_json(test_suggestions_path, test_data)
    loaded = _load_json(test_suggestions_path)
    assert loaded == test_data, "建议文件 I/O 不一致"
    test_suggestions_path.unlink(missing_ok=True)
    print("  ✓ 建议文件 I/O 正常")

    print("=== 通过 ===")


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="LinSai-CoPilot Prompt 闭环优化器"
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="运行自检",
    )

    # 子命令风格（但用位置参数简化）
    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        help="子命令：analyze / list / apply",
    )
    parser.add_argument(
        "--id",
        type=str,
        default=None,
        help="建议 ID（用于 apply --id <id>）",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="应用全部建议（慎用）",
    )

    args = parser.parse_args()

    if args.self_check:
        _self_check()
    elif args.command == "analyze":
        cmd_analyze()
    elif args.command == "auto":
        cmd_auto()
    elif args.command == "list":
        cmd_list()
    elif args.command == "apply":
        cmd_apply(suggestion_id=args.id, apply_all=args.all)
    else:
        parser.print_help()
        print()
        print("示例：")
        print("  python3 scripts/prompt_optimizer.py analyze           # 分析并生成建议")
        print("  python3 scripts/prompt_optimizer.py auto              # 自动分析+应用（cron 入口）")
        print("  python3 scripts/prompt_optimizer.py list               # 列出建议")
        print("  python3 scripts/prompt_optimizer.py apply --id <id>    # 手动应用单条")
        print("  python3 scripts/prompt_optimizer.py apply --all        # 手动应用全部")


if __name__ == "__main__":
    main()
