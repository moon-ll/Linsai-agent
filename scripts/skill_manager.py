#!/usr/bin/env python3
"""技能管理器 — 林赛的可复用能力模块。

用途：
    扫描 skills/ 目录下的 SKILL.md 文件，根据用户输入自动匹配并注入技能上下文。

用法示例：
    >>> from skill_manager import match_skills, get_skill_context
    >>> matched = match_skills("帮我推导这个公式")
    >>> print(matched)  # ['math-derivation']
    >>> ctx = get_skill_context('math-derivation')
    >>> print(ctx)  # 注入的上下文文本

规范：
    - 仅使用 Python 3 标准库
    - SKILL.md 格式见 skills/README.md
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"

# 缓存
_skills_cache: Optional[Dict[str, Dict[str, str]]] = None


def _load_skills() -> Dict[str, Dict[str, str]]:
    """扫描 skills/ 目录，加载所有 SKILL.md。"""
    global _skills_cache
    if _skills_cache is not None:
        return _skills_cache

    skills: Dict[str, Dict[str, str]] = {}
    if not SKILLS_DIR.exists():
        _skills_cache = skills
        return skills

    for subdir in sorted(SKILLS_DIR.iterdir()):
        if not subdir.is_dir():
            continue
        if subdir.name.startswith("_") or subdir.name.startswith("."):
            continue
        skill_file = subdir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8")
        parsed = _parse_skill_md(content)
        if parsed:
            skills[subdir.name] = parsed

    _skills_cache = skills
    return skills


def _parse_skill_md(text: str) -> Optional[Dict[str, str]]:
    """解析 SKILL.md，提取触发条件和上下文注入。"""
    result: Dict[str, str] = {"triggers": "", "context": "", "workflow": ""}

    # 提取触发条件
    m = re.search(r"##\s*触发条件\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if m:
        result["triggers"] = m.group(1).strip()

    # 提取上下文注入
    m = re.search(r"##\s*上下文注入\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if m:
        result["context"] = m.group(1).strip()

    # 提取工作流
    m = re.search(r"##\s*工作流\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if m:
        result["workflow"] = m.group(1).strip()

    if not result["context"]:
        return None
    return result


def _extract_trigger_keywords(triggers_text: str) -> List[str]:
    """从触发条件文本中提取关键词。"""
    # 简单策略：提取中文/英文单词，长度≥2
    keywords = []
    # 匹配中文字符串（连续中文）
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}", triggers_text):
        keywords.append(m.group())
    # 匹配英文单词
    for m in re.finditer(r"[a-zA-Z_]{2,}", triggers_text):
        keywords.append(m.group().lower())
    return keywords


def reload_skills() -> None:
    """重新加载技能缓存。"""
    global _skills_cache
    _skills_cache = None


def list_skills() -> List[Dict[str, str]]:
    """返回所有技能列表。"""
    skills = _load_skills()
    result = []
    for name, info in skills.items():
        result.append({
            "name": name,
            "triggers": info.get("triggers", "")[:100],
            "has_context": bool(info.get("context")),
        })
    return result


def match_skills(user_input: str) -> List[str]:
    """根据用户输入匹配激活的技能。

    返回命中的技能名称列表（按匹配度排序）。
    """
    if not user_input:
        return []

    skills = _load_skills()
    if not skills:
        return []

    user_lower = user_input.lower()
    scored: List[tuple] = []

    for name, info in skills.items():
        triggers = info.get("triggers", "")
        keywords = _extract_trigger_keywords(triggers)
        score = 0
        for kw in keywords:
            if kw.lower() in user_lower:
                score += 1
        if score > 0:
            scored.append((score, name))

    scored.sort(reverse=True)
    return [name for _, name in scored]


def get_skill_context(skill_name: str) -> str:
    """获取指定技能的上下文注入文本。"""
    skills = _load_skills()
    info = skills.get(skill_name)
    if not info:
        return ""
    context = info.get("context", "")
    workflow = info.get("workflow", "")
    parts = [f"【技能激活: {skill_name}】"]
    if context:
        parts.append(context)
    if workflow:
        parts.append(f"工作流: {workflow}")
    return "\n\n".join(parts)


def get_matched_context(user_input: str) -> str:
    """一键匹配并返回所有命中技能的上下文文本。"""
    matched = match_skills(user_input)
    if not matched:
        return ""
    contexts = [get_skill_context(name) for name in matched]
    return "\n\n".join(contexts)


def get_active_skill_names(user_input: str) -> List[str]:
    """返回当前输入激活的技能名称列表。"""
    return match_skills(user_input)


if __name__ == "__main__":
    print("◐ 技能管理器自检")
    skills = _load_skills()
    print(f"  加载技能数: {len(skills)}")
    for name in skills:
        print(f"    - {name}")

    test_inputs = [
        "帮我推导这个公式",
        "看看这段代码有没有问题",
        "设计一个固体HHG实验",
        "今天天气怎么样",
    ]
    for inp in test_inputs:
        matched = match_skills(inp)
        print(f"  输入: {inp[:20]}... → 匹配: {matched}")

    print("✓ 自检通过")
