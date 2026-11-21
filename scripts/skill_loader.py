#!/usr/bin/env python3
"""skill_loader — 管线侧统一 skill 加载器（v7.0.0 skill 架构核心组件）。

用途：
    项目从"prompt 驱动"迁移为"skill 驱动"（用户裁决 2026-09-25）。skill 的
    单一真相源放 .hermes/skills/<name>/SKILL.md（hermes 项目本地 trusted
    目录，agent 会话自动进 skills index）；本加载器供 CoPilot 管线代码
    （optimize/executor/hermes_pipeline 等）按节裁剪注入 prompt——核心
    红线强制生效，完整 skill 给路径由 agent 按需深读，控制 token 预算。

用法示例：
    >>> from skill_loader import skill_sections, inject_block
    >>> secs = skill_sections("nsfc-writing", ["二、叙事主线纪律", "三、禁用词"])
    >>> block = inject_block("nsfc-writing", secs, note="写作时强制执行")
    >>> len(block) > 0
    True

设计：
    - fail-open：skill 文件缺失/节缺失返回空，不阻塞管线
    - 进程内缓存（skill 文件运行期不变更）
    - 节提取按 "## 前缀" 匹配（标题余文不敏感），跨 skill 统一
    - 注入块带预算上限（默认 4KB），超限截断并提示读全文

规范：
    - 仅使用 Python 3 标准库
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from paths import PROJECT_ROOT

SKILLS_ROOT = PROJECT_ROOT / ".hermes" / "skills"
MAX_BLOCK_CHARS = 4096

_cache: Dict[str, str] = {}

# v7.0.4: 管线六阶段 → skill 静态绑定表（单一真相源归位于本加载器）。
# 此前表定义散在 hermes_pipeline.STAGE_SKILLS，与 AGENTS/ARCHITECTURE
# "skill_loader.py 静态绑定表（管线步骤→skill）"的架构声明不符（审计
# 2026-09-26 发现）。hermes_pipeline 经 get_stage_skills() 消费。
# 说明：这是"阶段→skill"的粗粒度绑定（hermes 派活 prompt 只附 skill
# 路径引用）；optimize/executor/idea_generator 等按步骤/角色的细粒度
# 按节注入绑定在各消费点内联（见 SKILL-ARCHITECTURE §四.2）。
PIPELINE_STAGE_SKILLS: Dict[int, List[str]] = {
    0: ["research-proposal"],           # 方向校准（pipeline-runner）
    1: ["literature-reading"],          # 文献调研（researcher）
    2: ["research-proposal"],           # 缺口分析（analyst）
    3: ["research-proposal"],           # 科学问题（analyst）
    4: ["nsfc-writing", "research-proposal"],  # 申请书撰写（writer）
    5: ["nsfc-writing", "quality-review"],     # 质量自检（reviewer）
}


def get_stage_skills(stage_id: int) -> List[str]:
    """返回管线某阶段绑定的 skill 名列表（缺失返回空，fail-open）。"""
    return list(PIPELINE_STAGE_SKILLS.get(stage_id, []))


def skill_path(name: str) -> Path:
    """返回 skill 文件路径。"""
    return SKILLS_ROOT / name / "SKILL.md"


def load_skill(name: str) -> str:
    """读取 skill 全文（缓存，fail-open 返回空串）。"""
    if name not in _cache:
        try:
            _cache[name] = skill_path(name).read_text(encoding="utf-8")
        except Exception:
            _cache[name] = ""
    return _cache[name]


def extract_section(text: str, prefix: str) -> str:
    """按节标题前缀提取一节正文（到下一个 ## 或文末）。

    前缀匹配标题行 "## <prefix>..."，标题余文（编号后的说明文字）不敏感。
    """
    m = re.search(rf"## {re.escape(prefix)}[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
    return (m.group(1).strip() if m else "")


def skill_sections(name: str, prefixes: List[str]) -> Dict[str, str]:
    """批量提取 skill 的多个节，返回 {前缀: 正文}（缺失节不出现在结果中）。"""
    text = load_skill(name)
    if not text:
        return {}
    out: Dict[str, str] = {}
    for p in prefixes:
        sec = extract_section(text, p)
        if sec:
            out[p] = sec
    return out


def inject_block(
    name: str,
    prefixes: List[str],
    note: str = "强制执行",
    max_chars: int = MAX_BLOCK_CHARS,
    extra: str = "",
) -> str:
    """构造 prompt 注入块：核心节内容 + 完整 skill 路径 + 提示。

    Args:
        name: skill 名（.hermes/skills/ 下目录名）
        prefixes: 注入的节标题前缀列表（按序）
        note: 块头提示（如 "写作时强制执行" / "评审扣分依据"）
        max_chars: 注入块预算上限
        extra: 追加在节内容后的额外指令（如运行时裁剪说明）
    """
    secs = skill_sections(name, prefixes)
    if not secs:
        return ""
    parts = [f"\n【{name} skill（{note}）】\n"]
    for p in prefixes:
        if p in secs:
            parts.append(f"◆ {p}\n{secs[p]}\n\n")
    if extra:
        parts.append(f"{extra}\n")
    parts.append(
        f"完整 skill（含对照样例/自检清单，按需深读）：{skill_path(name)}\n"
    )
    block = "".join(parts)
    if len(block) > max_chars:
        block = block[:max_chars] + f"\n…（截断，读全文：{skill_path(name)}）\n"
    return block


def has_skill(name: str) -> bool:
    """skill 是否存在且非空。"""
    return bool(load_skill(name))


def _self_check() -> bool:
    """自检：加载/节提取/注入块/fail-open。"""
    ok = True
    # 5 个管线 skill 齐备
    for name in ["nsfc-writing", "research-proposal", "literature-reading",
                 "method-manual", "quality-review"]:
        if not has_skill(name):
            print(f"✗ 缺 skill：{name}")
            ok = False
    # 节提取
    w = skill_sections("nsfc-writing", ["二、叙事主线纪律", "十、critic 检查项"])
    if "顺叙为主" not in w.get("二、叙事主线纪律", ""):
        print("✗ nsfc-writing 二节提取失败")
        ok = False
    if "主线清晰度" not in w.get("十、critic 检查项", ""):
        print("✗ nsfc-writing 十节提取失败")
        ok = False
    # 可操作性五问（research-proposal 核心）
    rp = extract_section(load_skill("research-proposal"), "一、操作性五问")
    if "时间预算" not in rp or "拿什么做" not in rp:
        print("✗ research-proposal 操作性五问不完整")
        ok = False
    # 注入块
    blk = inject_block("literature-reading", ["一、五维笔记"], note="深读标准")
    if "研究问题" not in blk or "SKILL.md" not in blk:
        print("✗ 注入块构造异常")
        ok = False
    # fail-open
    if load_skill("__not_exist__") != "":
        print("✗ fail-open 失效")
        ok = False
    if ok:
        print("✓ skill_loader 自检通过")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if _self_check() else 1)
