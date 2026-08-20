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

# v6.8.23 修复：单次 auto 运行中，最多应用 / 写入 journal 的 suggestion 数。
# 历史背景：debug-journal.json 在 7 天窗口内可达 ~5000 条 prompt_tuning 条目，
# 配合 cron 副本（5×）触发 cmd_auto 时，单次运行可能产生 15806+ 条 suggestion，
# 全部 append 到 critic/SOUL.md 并写入 5000+ 条新 journal 条目。即使进程最终退出，
# 单次 run 的磁盘放大已发生。设置上限后即使重复触发，journal 增长也被限制在
# MAX_AUTO_APPLY_PER_RUN × cron 副本数 / 天的可控范围内。
MAX_AUTO_APPLY_PER_RUN = 200

# v6.8.23 修复：cmd_auto 互斥锁文件路径。
# 历史背景：jobs.json 中存在 5 份同名 cron，hermes scheduler 同时触发时
# 多个 python3 scripts/prompt_optimizer.py auto 并发跑，叠加写 journal 导致
# debug-journal.json 持续膨胀。fcntl.flock 提供跨进程互斥。
CMD_AUTO_LOCK_PATH = MEMORY_DIR / ".prompt-optimizer-auto.lock"

# v6.8.24: applied/failed 建议保留天数。超过此天数的非 pending 建议将被清理。
SUGGESTION_RETENTION_DAYS = 7

# ─────────────────────────────────────────────
# v6.9.9: 范本守门 + 自动段回收
# ─────────────────────────────────────────────

# 自动追加段在 SOUL.md 中的标记格式（回收机制的定位锚点）。
# pattern_re 直接嵌入标记（回源自包含，不依赖 suggestions.json——
# 后者只保留 7 天，而回收窗口 14 天）
AUTO_TAG_START = "<!--auto-opt:start:{sid}:{ts}:{pat}-->"
AUTO_TAG_END = "<!--auto-opt:end:{sid}-->"
AUTO_TAG_RE = re.compile(
    r"\n?<!--auto-opt:start:([^:]+):([0-9TZ:.-]+):([^>]*)-->\n(.*?)\n?<!--auto-opt:end:\1-->\n?",
    re.S,
)

# 自动段回收保留期（天）：超期且对应问题未再出现的段落将被删除
AUTO_SECTION_RETENTION_DAYS = 14

# 范本守门规则：拦截与范本实测口径冲突的量化指令。
# 依据 references/nsfc-templates/ 实测（2026-08-15 校准）：
# - 范本总正文约 2.5-3 万字符，立项依据 5000-8000 字 → 总字数下限指令 < 10000 字
#   会把申请书往小拉（历史实例：prompt_optimizer 曾追加"总字数≥4000字"）
# - 参考文献范本实测 30-40 篇 → 篇数区间上限 < 25 或下限 < 15 与范本冲突
#   （历史实例：critic 运行时曾要求"15-30 篇"）
# - 评分体系由运行时 prompt（四维 + 天花板）统一约束，SOUL 层引入绝对分值
#   会造成双口径（历史实例："占位符给 0.10"）
BENCHMARK_GUARD_RULES = [
    (
        re.compile(r"(?:总字数|全文|正文总)[^\n]{0,12}(?:≥|>=|至少|不少于|不低于)?\s*(?<!\d)(\d{3,6})\s*字"),
        lambda m: int(m.group(1)) < 10000,
        "总字数下限低于 10000 字，与范本体量（2.5-3 万字符）冲突，会把申请书往小拉",
    ),
    (
        re.compile(r"每(?:个)?章节[^\n]{0,10}(?:≥|>=|至少|不少于|不低于)?\s*(?<!\d)(\d{3,6})\s*字"),
        lambda m: int(m.group(1)) < 3000,
        "章节字数下限低于 3000 字，低于范本最短章节体量（研究内容 3000-5000 字）",
    ),
    (
        re.compile(r"(?<!\d)(\d{1,3})\s*[-–~到至]\s*(\d{1,3})\s*篇"),
        lambda m: int(m.group(1)) < 30 and int(m.group(2)) <= 30,
        "参考文献篇数区间整体低于范本实测（30-40 篇），会把文献支撑往低压",
    ),
    (
        re.compile(r"(?:给|评|打)\s*0\.\d{1,2}\s*(?:分|而非)"),
        lambda m: True,
        "SOUL 层引入绝对评分魔法数，与运行时四维评分+天花板机制形成双口径",
    ),
]


def _benchmark_conflict_guard(suggestion: Dict) -> Optional[str]:
    """v6.9.9: 范本守门——拦截与范本实测口径冲突的建议内容。

    Returns:
        None 表示通过；str 为拒绝原因（写入 suggestion["guard_reason"]，
        status 置为 rejected_guard，不会追加到 SOUL.md）。
    """
    content = suggestion.get("content", "")
    for pattern, conflict_if, reason in BENCHMARK_GUARD_RULES:
        m = pattern.search(content)
        if m and conflict_if(m):
            return reason
    return None


def _wrap_auto_section(text: str, sid: str, pat: str = "-") -> str:
    """v6.9.9: 给自动追加段包裹定位标记注释（回收机制的锚点）。

    标记格式: <!--auto-opt:start:{sid}:{ts}:{pat}--> ... <!--auto-opt:end:{sid}-->
    pat 为问题模式的正则（agent_score_analysis 来源），回收时用于判断问题
    是否复现；其他来源填 "-"（永不自动回收，人工审阅）。
    老版本（v6.9.9 前）追加的段落无标记，不在回收范围内（由人工清理）。
    """
    ts = _now_utc()
    return f"\n{AUTO_TAG_START.format(sid=sid, ts=ts, pat=pat)}\n{text.rstrip()}\n{AUTO_TAG_END.format(sid=sid)}\n"


def _reap_stale_auto_sections(score_reasons: List[Dict]) -> int:
    """v6.9.9: 回收过期的自动追加段——让 SOUL.md "有增有减"。

    回收条件（同时满足）：
    1. 段龄超过 AUTO_SECTION_RETENTION_DAYS（14 天）
    2. 标记内嵌的 pattern_re 非 "-"（agent_score_analysis 来源），且对应
       问题模式在近期 score_reasons 中零命中（问题已消失，约束不再必要）

    其他来源（failure_analyzer / debug_journal）的段不自动回收——无法可靠
    判断问题是否复现，保留待人工审阅。回收前自动备份到
    prompt-backups/reap-{profile}-{file}-{ts}.bak。

    Returns: 回收的段数。
    """
    reaped = 0
    try:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=AUTO_SECTION_RETENTION_DAYS)
        cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return 0

    recent_reasons = [
        r.get("reason", "") for r in (score_reasons or [])[:100]
    ]
    # v6.9.25: 程序化 AI 检测的 top_issues 也作为"问题复现"信号——
    # ai_pattern_analysis 段的 pattern_re（如"超长句"）命中即保留
    recent_reasons.extend(_load_recent_ai_issues())

    prompt_files = _discover_prompt_files()
    backup_tracker: Dict[str, int] = {}

    for profile, files in prompt_files.items():
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue

            changed = False
            matches = list(AUTO_TAG_RE.finditer(content))
            for m in matches:
                sid, ts, pat_re = m.group(1), m.group(2), m.group(3)
                if ts >= cutoff_str:
                    continue  # 未过保留期
                if not pat_re or pat_re == "-":
                    continue  # 非 score_analysis 来源，不自动回收
                try:
                    if any(re.search(pat_re, r, re.IGNORECASE) for r in recent_reasons):
                        continue  # 问题仍在复现，约束保留
                except re.error:
                    continue
                content = content.replace(m.group(0), "\n")
                changed = True
                reaped += 1

            if changed:
                key = str(f)
                if backup_tracker.get(key, 0) < 1:
                    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy2(key, str(BACKUPS_DIR / f"reap-{f.parent.name}-{f.name}-{_now_ts_safe()}.bak"))
                        backup_tracker[key] = 1
                    except Exception:
                        pass
                try:
                    f.write_text(content.rstrip() + "\n", encoding="utf-8")
                except Exception as e:
                    print(f"  ⚠ 回收写入失败 {f}: {e}")
                    reaped -= 1
    return reaped


def _now_ts_safe() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _cleanup_old_suggestions() -> int:
    """v6.8.24: 清理超过保留期的 applied/failed 建议，防止 prompt-suggestions.json 无限膨胀。

    Returns: 清理的条目数。
    """
    suggestions = _load_suggestions()
    if not suggestions:
        return 0

    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=SUGGESTION_RETENTION_DAYS)

    kept = []
    cleaned = 0
    for s in suggestions:
        status = s.get("status", "")
        if status == "pending":
            kept.append(s)
            continue
        # applied/failed 超过保留期则删除
        ts = s.get("applied_at") or s.get("created_at") or ""
        try:
            entry_dt = datetime.strptime(ts[:19] + "Z", "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if entry_dt < cutoff:
                cleaned += 1
                continue
        except (ValueError, TypeError):
            # 时间戳解析失败的安全策略：保留
            pass
        kept.append(s)

    if cleaned > 0:
        _save_suggestions(kept)
    return cleaned


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
        # v6.8.24: 排除 auto_applied 标记的条目，断裂正反馈循环
        tags = e.get("tags", [])
        if "auto_applied" in tags:
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
    """从 agent-scores.json 中提取带 reason 的奖惩记录。

    v6.8.24: 遍历全部 7 个 profile（旧版硬编码只有 writer/critic）。
    """
    data = _load_json(AGENT_SCORES_PATH)
    result = []

    # v6.8.24: 覆盖全部 hermes profile
    all_profiles = ["writer", "critic", "researcher", "analyst", "reviewer", "linsai", "pipeline-runner"]
    for agent_name in all_profiles:
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


# ─────────────────────────────────────────────
# v6.9.25: 程序化 AI 检测数据源
# ─────────────────────────────────────────────

# 采集窗口（天）：与回收保留期对齐
AI_PATTERN_WINDOW_DAYS = 14

# 单次运行最多生成的 AI 检测建议数（防洪水）
MAX_AI_PATTERN_SUGGESTIONS = 6

# 问题类别 → 修复指令映射。
# 背景：_detect_ai_patterns 的扣分项此前只注入当轮 writer/critic prompt，
# 不进任何优化器数据源——优化器对真实失分点全盲（08-18 实测三课题
# ceiling 触底 0.5，9 条已应用建议无一指向超长句/冗余词/自引用）。
# 指令口径与 optimize.py 检测阈值严格一致（写明检测阈值本身，writer
# 按此自检即可通过程序化检测）。
AI_PATTERN_RULES = [
    {
        "key": "long_sentences",
        "label": "超长句",
        "match": re.compile(r"超长句"),
        "target": "writer",
        "priority": "high",
        "instruction": (
            "【必须】提交前逐句自检：任何单句超过 120 字必须拆分（80-120 字的"
            "技术性长句可保留，每段不超过 2 句）；拆分后多数句子以动词或实义"
            "成分开头。该项程序化检测每处扣 0.02，超长句堆积会把表达质量"
            "天花板压到 0.5。"
        ),
    },
    {
        "key": "self_reference",
        "label": "自引用泛滥",
        "match": re.compile(r"自引用泛滥"),
        "target": "writer",
        "priority": "high",
        "instruction": (
            "【禁止】申请书正文（立项依据/研究内容/研究方案）不得用"
            "'详§X / 见§X / 参见§X / 方法学手册§X'式自引用替代论证——检测阈值"
            "为全文 10 处（超 15 处固定扣 0.10）。细节论证直接写入正文；"
            "方法学细节归 04_proposal/methodology-manual.md，每节自引用不超过 5 处。"
        ),
    },
    {
        "key": "bullet_list_substitution",
        "label": "列表替代论述",
        "match": re.compile(r"列表替代论述"),
        "target": "writer",
        "priority": "high",
        "instruction": (
            "【禁止】用编号/项目符号列表替代段落论述（程序化检测每处扣 0.05，"
            "上限 0.20）。论述性内容一律写成完整段落；列表仅允许用于参数表、"
            "指标清单等确实需要逐项罗列的制表内容。"
        ),
    },
    {
        "key": "redundant_modifiers",
        "label": "冗余修饰词",
        "match": re.compile(r"冗余修饰词"),
        "target": "writer",
        "priority": "medium",
        "instruction": (
            "【必须】提交前全局检索计数修饰词（显著/重要/系统/良好/成熟/完整/"
            "关键/精准/一系列/有效/高效），合计超过 12 次必须压缩到 12 次以内"
            "（每超 1 次扣 0.01）——用具体数据、方法名、量化结论替代空泛修饰。"
        ),
    },
    {
        "key": "transition_words",
        "label": "死板关联词",
        "match": re.compile(r"死板关联词"),
        "target": "writer",
        "priority": "medium",
        "instruction": (
            "【必须】关联词（在此基础上/此外/同时/与此同时/因此/然而/基于此）"
            "全文合计不超过 8 次（每超 1 次扣 0.02）；段间衔接改用内容驱动"
            "（如'上述数值结果表明…'）。"
        ),
    },
    {
        "key": "template_phrases",
        "label": "模板句式",
        "match": re.compile(r"模板句式"),
        "target": "writer",
        "priority": "medium",
        "instruction": (
            "【必须】'为…提供…基础/支撑/途径/条件/工具/指导'句式全文不超过 8 次"
            "（每超 1 次扣 0.03）；改写为具体动作与对象（'该光谱可直接分辨"
            "两种谷极化通道的衰减时标'）。"
        ),
    },
    {
        "key": "template_subject",
        "label": "模板主语",
        "match": re.compile(r"模板主语"),
        "target": "writer",
        "priority": "medium",
        "instruction": (
            "【必须】'本项目拟/将/计划/旨在'句首全文不超过 5 次（每超 1 次扣 0.02）；"
            "直接以研究动作或对象开头（'我们拟'或以物理对象作主语）。"
        ),
    },
    {
        "key": "meta_discourse",
        "label": "元话语",
        "match": re.compile(r"元话语"),
        "target": "writer",
        "priority": "medium",
        "instruction": (
            "【禁止】元话语（'需要特别说明的是/值得指出的是/沿着…这一主线/"
            "一个根本性问题浮现'等）全文不超过 2 次（每超 1 次扣 0.03）；"
            "论述直接陈述事实与推理，不做自我解说。"
        ),
    },
    {
        "key": "excessive_bold",
        "label": "过度加粗",
        "match": re.compile(r"加粗标记过多"),
        "target": "writer",
        "priority": "low",
        "instruction": (
            "【必须】加粗密度不超过 3 处/千字；只加粗章节内核心结论句，"
            "不得整句/整段加粗。"
        ),
    },
]


def _load_recent_ai_issues(window_days: int = AI_PATTERN_WINDOW_DAYS) -> List[str]:
    """读取窗口期内全课题的 ai_top_issues 字符串（供采集与回收复用）。"""
    try:
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=window_days)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    except Exception:
        return []

    lc = _load_json(PROJECT_ROOT / "research_proposals" / "_lifecycle.json", {})
    issues: List[str] = []
    for prop in (lc.get("proposals") or {}).values():
        for h in prop.get("score_history") or []:
            if h.get("at", "") < cutoff:
                continue
            for line in h.get("ai_top_issues") or []:
                if isinstance(line, str) and line.strip():
                    issues.append(line.strip())
    return issues


def _collect_ai_pattern_hints(
    min_evidence: int = 2,
) -> List[Dict]:
    """v6.9.25: 从 lifecycle score_history 的 ai_top_issues 聚合问题类别。

    每个类别输出一条带 pattern_re 的 hint（进 _generate_suggestions 源 4），
    pattern_re 用于自动段回收——程序化检测仍在复现时约束保留。
    """
    from collections import defaultdict

    recent = _load_recent_ai_issues()
    if not recent:
        return []

    evidence: Dict[str, Dict] = defaultdict(lambda: {"count": 0, "sample": ""})
    for line in recent:
        for rule in AI_PATTERN_RULES:
            if rule["match"].search(line):
                ev = evidence[rule["key"]]
                ev["count"] += 1
                if not ev["sample"]:
                    ev["sample"] = line
                break  # 一行只归入最匹配的一个类别

    hints = []
    for rule in AI_PATTERN_RULES:
        ev = evidence.get(rule["key"])
        if not ev or ev["count"] < min_evidence:
            continue
        hints.append({
            "source": "ai_pattern_analysis",
            "pattern_key": f"{rule['target']}:ai:{rule['key']}",
            "pattern_re": rule["match"].pattern,
            "target_profile": rule["target"],
            "priority": rule["priority"],
            "instruction": rule["instruction"],
            "evidence_count": ev["count"],
            "sample_issue": ev["sample"][:120],
            "label": rule["label"],
        })

    hints.sort(key=lambda h: h["evidence_count"], reverse=True)
    return hints[:MAX_AI_PATTERN_SUGGESTIONS]


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
                # v6.9.25: 与 failure_analyzer 同步修正（旧文案"总字数≥4000字"
                # 与范本实测冲突，是 08-13 污染段的源头）
                "在 writer prompt 中明确：'请基于 brief 实质扩写申请书，篇幅对标"
                "范本实测口径（立项依据 5000-8000 字、研究内容 3000-5000 字、"
                "研究方案 5000-8000 字）；素材不足时深挖论证链，不得注水凑字数'。"
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
    """从 agent 分数原因中提取 prompt 相关的改进建议。

    v6.9.9: 每条模式新增 instruction 字段——追加到 SOUL.md 的文字必须是
    可执行指令（agent 读到即知道怎么做），而非"需在 prompt 中要求…"式
    元描述（那是写给系统管理员看的，agent 无法执行）。
    """
    suggestions = []

    # 常见问题模式关键词: (正则, 目标profile, 优先级, 诊断描述, 指令式文案)
    writer_patterns = [
        (r"零修改|完全未执行|逐字节相同|MD5.*一致|无实质性", "writer", "high",
         "writer 提交与上一轮相同的文件，需强化'必须基于 critic 建议做实质性修改'的指令",
         "逐条核对评审报告的每个问题并逐一修改，在输出末尾给出'问题→修改对照'清单；"
         "未修改的问题必须说明原因。禁止原样提交上一轮文件或仅做表面增删。"),
        (r"表面修改|仅删除|仅增加.*分隔线|未实质回应", "writer", "medium",
         "writer 仅做表面修改，需在 prompt 中要求逐条回应 critic 的每个问题",
         "对评审报告的每条问题给出明确的处理结论（已修改/未修改及原因），"
         "修改处须引用修改后的原句，让修改可被核对。"),
        (r"占位符|待.*核验|TBD", "writer", "high",
         "writer 输出中残留占位符/TBD，需在 prompt 中明确禁止提交含占位符的内容",
         "提交前全文检索'待补充/TBD/待核验/XXX'，命中处一律改写为不依赖该信息的"
         "完整表述，或标注'需要 researcher 补充'并给出替代论证。"),
        (r"AI生成痕迹|优化记录|元信息", "writer", "high",
         "writer 输出中残留 AI 工作流元信息，需在 prompt 中要求清理所有迭代痕迹",
         "提交的 .md 文件只包含申请书内容本身；删除迭代记录、优化说明、审稿对话、"
         "元信息等一切工作流痕迹后再写盘。"),
    ]

    critic_patterns = [
        (r"事实错误|事实核查.*失职|基于错误.*前提", "critic", "high",
         "critic 评审基于错误的事实前提，需在 prompt 中强化'先核实文件状态再下结论'",
         "评审前必须实际读取申请书当前文件内容，禁止基于记忆或上一轮印象下结论；"
         "每条问题给出章节与段落定位。"),
        (r"过时的文件|文件系统快照", "critic", "medium",
         "critic 使用过时的文件状态信息，需在 prompt 中要求重新读取最新文件",
         "开始评审前重新读取全部待审文件，确保引用的原文与当前文件一致。"),
        (r"评分.*不一致|综合分.*自报.*不匹配", "critic", "medium",
         "critic 报告内评分不一致，需在 prompt 中明确评分公式的自洽性要求",
         "综合评分必须等于各维度分按项目类型权重的加权平均，误差不超过 0.02；"
         "提交报告前复核维度分、问题数、综合分三者自洽。"),
    ]

    # v6.8.24: 新增 researcher/analyst/reviewer 的模式
    researcher_patterns = [
        (r"超时|timeout|agent loop.*超时", "researcher", "medium",
         "researcher agent loop 频繁超时，需在 prompt 中精简检索策略或限制搜索深度",
         "单次检索控制在 3 轮以内，优先使用聚合检索（search_academic），"
         "避免逐库遍历导致超时。"),
        (r"文献.*缺失|检索.*失败|无结果", "researcher", "medium",
         "researcher 文献检索结果不足，需在 prompt 中强化关键词组合策略和数据库覆盖",
         "检索时组合使用领域术语与具体材料/方法名（如'高次谐波+掺杂半导体'），"
         "单一关键词无结果时换同义术语重试一次。"),
    ]

    analyst_patterns = [
        (r"分析.*空|gap.*识别.*失败|缺口.*未发现", "analyst", "medium",
         "analyst 文献缺口识别能力不足，需在 prompt 中强化对比分析框架",
         "缺口分析按'已知→未知→本课题切入'三段展开，每个缺口须引用具体文献"
         "支撑'已知'部分。"),
    ]

    reviewer_patterns = [
        (r"串通|collusion|虚高|过度宽松", "reviewer", "high",
         "reviewer monitor 检测到 writer-critic 串通风险，需强化独立判断指令",
         "独立形成判断后再看 critic 报告；评分依据必须引用申请书原文与评分档位，"
         "不得复述 critic 的结论。"),
    ]

    all_patterns = writer_patterns + critic_patterns + researcher_patterns + analyst_patterns + reviewer_patterns
    matched_patterns: Dict[str, int] = Counter()

    for r in reasons[:50]:  # 只检查最近 50 条
        reason_text = r.get("reason", "")
        agent = r.get("agent", "")

        for pattern, target, priority, description, instruction in all_patterns:
            if re.search(pattern, reason_text, re.IGNORECASE):
                key = f"{target}:{description[:50]}"
                matched_patterns[key] += 1

                if matched_patterns[key] == 1:  # 每种模式只建议一次
                    suggestions.append({
                        "source": "agent_score_analysis",
                        "pattern_key": key,
                        "pattern_re": pattern,
                        "instruction": instruction,
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

        _sid = _generate_suggestion_id()
        suggestions.append({
            "id": _sid,
            "source": "failure_analyzer",
            "pattern_id": pat["pattern_id"],
            "pattern_label": pat["label"],
            "target_profile": profile,
            "target_file": str(target_file),
            "target_file_display": target_file_rel,
            "priority": "high",
            "action": "append",
            "content": _wrap_auto_section(
                f"## 自动优化规则（{datetime.now(timezone.utc).strftime('%Y-%m-%d')}，来自失败模式 {pat['pattern_id']}）\n\n"
                f"{pat['suggested_change']}\n",
                sid=_sid, pat="-",
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

        _sid = _generate_suggestion_id()
        suggestions.append({
            "id": _sid,
            "source": "debug_journal",
            "entry_id": entry_id,
            "target_profile": target_profile,
            "target_file": str(target_file),
            "target_file_display": target_file_rel,
            "priority": "high" if entry.get("severity") == "critical" else "medium",
            "action": "append",
            "content": _wrap_auto_section(
                f"## 自动优化规则（来自 debug {entry_id}）\n\n"
                f"{solution}\n",
                sid=_sid, pat="-",
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

        _sid = _generate_suggestion_id()
        suggestions.append({
            "id": _sid,
            "source": "agent_score_analysis",
            "pattern_key": hint["pattern_key"],
            "pattern_re": hint.get("pattern_re", ""),
            "target_profile": profile,
            "target_file": str(target_file),
            "target_file_display": target_file_rel,
            "priority": hint["priority"],
            "action": "append",
            "content": _wrap_auto_section(
                f"## 自动优化规则（评分分析 {hint['evidence_count']} 次证据）\n\n"
                f"{hint.get('instruction') or hint['description']}\n",
                sid=_sid, pat=hint.get("pattern_re", "-"),
            ),
            "description": f"[{profile}] {hint['description'][:100]}",
            "expected_impact": f"减少重复出现的 {profile} 问题模式",
            "fingerprint": fingerprint,
            "status": "pending",
            "created_at": _now_utc(),
        })

    # 4. 程序化 AI 检测聚合（v6.9.25）
    # 与源 1-3 的区别：数据不是 LLM 自评，而是 optimize.py 的确定性代码检测
    # （超长句/自引用/列表替代论述等 9 类），直接对应表达质量天花板扣分。
    for hint in _collect_ai_pattern_hints():
        profile = hint["target_profile"]
        files = prompt_files.get(profile, [])
        if not files:
            continue

        target_file = files[0]
        target_file_rel = f"~/.hermes/profiles/{profile}/{target_file.name}"

        fingerprint = hashlib.md5(
            f"ai_pattern_analysis:{hint['pattern_key']}".encode()
        ).hexdigest()[:12]

        if fingerprint in existing_ids:
            continue

        _sid = _generate_suggestion_id()
        suggestions.append({
            "id": _sid,
            "source": "ai_pattern_analysis",
            "pattern_key": hint["pattern_key"],
            "pattern_re": hint.get("pattern_re", ""),
            "target_profile": profile,
            "target_file": str(target_file),
            "target_file_display": target_file_rel,
            "priority": hint["priority"],
            "action": "append",
            "content": _wrap_auto_section(
                f"## 自动优化规则（程序化 AI 检测 {hint['evidence_count']} 轮复现："
                f"{hint['label']}）\n\n{hint['instruction']}\n",
                sid=_sid, pat=hint.get("pattern_re", "-"),
            ),
            "description": (
                f"[{profile}] 程序化检测 {hint['label']} 近期 {hint['evidence_count']} 轮复现"
                f"（样例：{hint['sample_issue'][:60]}）"
            ),
            "expected_impact": (
                "降低表达质量天花板扣分，解除综合分 0.75 硬上限"
            ),
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


def _semantic_overlap_ratio(new_content: str, existing: str) -> float:
    """v6.9.28: 计算建议内容与现有正文的语义重叠度（双口径取 max）。

    背景：v6.9.25 将历史 auto-opt 规则手工合并进 SOUL 正文（运行纪律/
    评分纪律段），原定位标记被去除。fingerprint 去重窗口仅 7 天，过期后
    同一问题模式的建议会以不同措辞再生成，精确子串匹配不再命中 →
    与正文重复的规则被再次追加。

    口径：
        1. 特征词覆盖率——去注释/标题后提取词元（CJK ≥3 字、ASCII ≥2 字，
           排除"内容/需要"等 2 字泛用词的虚假证据），统计在 existing 中的
           命中比例；≥6 字长词整词未命中时按内部 3-gram ≥40% 判部分命中
           （捕捉"整句重组但主干措辞复用"）。术语（TBD/待核验/researcher）
           是规则身份的主干，同义改写仍会复用。
        2. 字符 4-gram 包含度——两侧去空白后取新内容 4-gram 在 existing
           中的包含比例。捕捉局部措辞大量复用的场景。
        词级口径的盲区是"长句被完全重组"，n-gram 口径的盲区是短小新规则
        偶撞公共短语，取 max 互补。两口径均无信号（正文过短/纯标题）时
        返回 0——无法判定语义时不拦截，宁可多写不可误删。
    """
    import re as _re
    text = _re.sub(r"<!--.*?-->", "", new_content, flags=_re.S)
    text = _re.sub(r"^#+\s*.*$", "", text, flags=_re.M)

    # 口径 1：特征词覆盖率
    tokens = list(dict.fromkeys(
        t for t in _re.findall(r"[\w]+", text)
        if len(t) >= (3 if _re.match(r"[\u4e00-\u9fff]", t) else 2)
    ))
    token_ratio = 0.0
    if tokens:
        hits = 0
        for t in tokens:
            if t in existing:
                hits += 1
            elif len(t) >= 6:
                windows = [t[i:i + 3] for i in range(len(t) - 2)]
                window_hits = sum(1 for w in windows if w in existing)
                if windows and window_hits / len(windows) >= 0.4:
                    hits += 1
        token_ratio = hits / len(tokens)

    # 口径 2：字符 4-gram 包含度（两侧去空白，中英混排统一比较）
    new_cmp = _re.sub(r"\s+", "", text)
    existing_cmp = _re.sub(r"\s+", "", existing)
    ngram_ratio = 0.0
    if len(new_cmp) >= 4:
        grams = list(dict.fromkeys(new_cmp[i:i + 4] for i in range(len(new_cmp) - 3)))
        gram_hits = sum(1 for g in grams if g in existing_cmp)
        ngram_ratio = gram_hits / len(grams)

    return max(token_ratio, ngram_ratio)


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

    # v6.9.28: 语义级去重——v6.9.25 手工合并历史规则进 SOUL 正文后，
    # 同义建议会以不同措辞再生成，精确匹配失效；特征短语命中率 ≥60%
    # 判定为"正文已覆盖"，跳过追加（不备份、不写入）
    if content_to_add:
        _ratio = _semantic_overlap_ratio(content_to_add, current_content)
        if _ratio >= 0.6:
            print(f"  ○ 语义重复（特征短语命中 {_ratio:.0%}），跳过（不备份、不写入）")
            suggestion["apply_note"] = f"semantically_present:{_ratio:.0%}"
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
    print(f"    ai pattern hints（程序化检测，最近 {AI_PATTERN_WINDOW_DAYS}d）: {len(_collect_ai_pattern_hints())} 条")
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

    v6.8.23:
    - 加 fcntl.flock 互斥锁，防止 cron 副本并发触发时多个进程同时跑
    - 应用数量受 MAX_AUTO_APPLY_PER_RUN 限制，防止单次 run 写入过多
      journal 条目（即使 cron 副本被清理前仍可能重复触发）
    """
    import subprocess
    import fcntl

    print("=== Prompt 自动优化（auto 模式）===")
    print()

    # v6.8.24: 清理旧建议，防止文件无限膨胀
    cleaned = _cleanup_old_suggestions()
    if cleaned > 0:
        print(f"  ✓ 清理 {cleaned} 条过期 applied/failed 建议")

    # v6.9.9: 回收过期的自动追加段（问题已消失且段龄超 14 天的约束）
    try:
        _early_reasons = _collect_agent_score_reasons()
        reaped = _reap_stale_auto_sections(_early_reasons)
        if reaped > 0:
            print(f"  ✓ 回收 {reaped} 条过期自动优化段（问题未复现）")
    except Exception as reap_e:
        print(f"  ⚠ 自动段回收异常（忽略，继续主流程）：{reap_e}")

    # v6.8.23: 进程互斥锁（flock）。若已有进程持有锁（如上一个 cron 触发的实例
    # 仍在跑 / hang），当前进程直接退出，避免多个 cmd_auto 并发叠加写 journal。
    try:
        CMD_AUTO_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        lock_fd = open(CMD_AUTO_LOCK_PATH, "w")
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"○ cmd_auto 互斥：另一个实例正在运行（lock={CMD_AUTO_LOCK_PATH}），跳过本次执行")
            lock_fd.close()
            return
    except Exception as lock_e:
        print(f"⚠ cmd_auto 锁获取失败（继续执行）：{lock_e}")
        lock_fd = None

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
                # v6.8.23: 同样受 MAX_AUTO_APPLY_PER_RUN 截断
                if len(safe_pending) > MAX_AUTO_APPLY_PER_RUN:
                    print(f"○ 无新建议，但发现 {len(safe_pending)} 条遗留 pending；截断到 {MAX_AUTO_APPLY_PER_RUN}")
                    safe_pending = safe_pending[:MAX_AUTO_APPLY_PER_RUN]
                else:
                    print(f"○ 无新建议，但发现 {len(safe_pending)} 条遗留 pending 建议，自动应用")
                backup_tracker: Dict[str, int] = {}
                _apply_suggestions(
                    safe_pending, all_suggestions, auto_mode=True,
                    backup_count_tracker=backup_tracker,
                )
                _log_auto_applied(safe_pending)
                _record_intervention_baseline(safe_pending)  # v6.8.50 效果基线
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

    # v6.8.23: 应用数量上限。即使 5 份 cron 副本未清理，单次 run 也最多处理
    # MAX_AUTO_APPLY_PER_RUN 条，避免单 run 把 debug-journal 撑大数百条。
    # 历史触发场景：未清理 5 份 cron + cmd_auto 死循环 → 4h 窗口 +5102 条
    if len(to_apply) > MAX_AUTO_APPLY_PER_RUN:
        print(f"\n  ⚠ 待应用 {len(to_apply)} 条，超过 MAX_AUTO_APPLY_PER_RUN={MAX_AUTO_APPLY_PER_RUN}，截断")
        to_apply = to_apply[:MAX_AUTO_APPLY_PER_RUN]

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
        _record_intervention_baseline(applied_ok)  # v6.8.50 效果基线

    print("\n✓ 自动优化完成")


def _log_auto_applied(suggestions: List[Dict]) -> None:
    """将自动应用的记录写入 debug journal。

    v6.8.24: category 从 prompt_tuning 改为 prompt_applied_audit，
    断裂正反馈循环（旧版写入 prompt_tuning → 下次 _collect_debug_journal_entries
    又读回来 → 生成新 suggestion → 再次写入 → 指数膨胀）。
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import debug_journal
        for s in suggestions:
            debug_journal.add_entry({
                "category": "prompt_applied_audit",
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


def _record_intervention_baseline(suggestions: List[Dict]) -> None:
    """v6.8.50: 干预效果基线记录——优化平面闭环的证据锚点。

    每次成功应用 prompt 干预后，把当时的 agent-scores 快照记为基线。
    后续（retrospective / 人工）对比"基线 → 当前"即可量化干预是否有效，
    无效干预可回滚（备份在 memory/prompt-backups/）。

    闭环链：干预(apply) → 基线锚点(本函数) → 运行 N 轮 → 对比 agent-scores
    → 有效则沉淀/无效则回滚 → 周复盘归档。
    """
    try:
        from common import load_json, save_json
        scores_path = PROJECT_ROOT / "memory" / "agent-scores.json"
        scores = load_json(scores_path, default={})
        baseline_path = PROJECT_ROOT / "memory" / "prompt-interventions.json"
        interventions = load_json(baseline_path, default=[])
        if not isinstance(interventions, list):
            interventions = []
        from common import now_utc
        for s in suggestions:
            interventions.append({
                "at": now_utc(),
                "profile": s.get("target_profile", ""),
                "file": Path(s.get("target_file", "")).name,
                "description": str(s.get("description", ""))[:150],
                "baseline": {
                    "writer": (scores.get("writer") or {}).get("score"),
                    "critic": (scores.get("critic") or {}).get("score"),
                },
                "status": "active",  # active → validated / rolled_back
            })
        # 只保留最近 50 条
        interventions = interventions[-50:]
        save_json(baseline_path, interventions)
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
    guard_count = 0

    for s in to_apply:
        label = "自动" if auto_mode else "手动"
        print(f"\n{label}应用 {s['id']}：{s['description'][:60]}")

        # v6.9.9: 范本守门——与范本实测口径冲突的建议直接拒绝，不入 SOUL.md
        guard_reason = _benchmark_conflict_guard(s)
        if guard_reason:
            s["status"] = "rejected_guard"
            s["rejected_at"] = _now_utc()
            s["guard_reason"] = guard_reason
            guard_count += 1
            print(f"  ✗ 范本守门拦截：{guard_reason}")
            continue

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

    tail = f"，守门拦截 {guard_count}" if guard_count else ""
    print(f"\n✓ 完成：成功 {success_count}，失败 {fail_count}{tail}")


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
