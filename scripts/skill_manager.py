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
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
SKILLS_STATE_PATH = PROJECT_ROOT / "memory" / "skills-state.json"

# 缓存
_skills_cache: Optional[Dict[str, Dict[str, str]]] = None


# ─────────────────────────────────────────────
# 技能配置管理
# ─────────────────────────────────────────────

def _load_skill_state() -> Dict[str, Any]:
    """加载技能配置状态（自动/手动模式、激活列表）。"""
    if not SKILLS_STATE_PATH.exists():
        return {"mode": "auto", "active_skills": []}
    try:
        with open(SKILLS_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"mode": "auto", "active_skills": []}


def _save_skill_state(state: Dict[str, Any]) -> None:
    """保存技能配置状态。"""
    SKILLS_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SKILLS_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_skill_config() -> Dict[str, Any]:
    """获取技能配置。"""
    state = _load_skill_state()
    # 如果 active_skills 为空，默认全部激活
    all_skills = list(_load_skills().keys())
    if not state.get("active_skills"):
        state["active_skills"] = all_skills
    return state


def set_skill_config(mode: str, active_skills: List[str]) -> Dict[str, Any]:
    """设置技能配置。"""
    all_skills = list(_load_skills().keys())
    # 过滤掉不存在的技能
    valid = [s for s in active_skills if s in all_skills]
    state = {"mode": mode, "active_skills": valid}
    _save_skill_state(state)
    return state


def search_skills(query: str) -> List[Dict[str, Any]]:
    """模糊搜索技能，返回名称、触发词、描述。"""
    skills = _load_skills()
    if not query:
        return _build_skill_list(skills)

    query_lower = query.lower()
    matched = {}
    for name, info in skills.items():
        score = 0
        # 名称匹配权重最高
        if query_lower in name.lower():
            score += 10
        # 触发词匹配
        triggers = info.get("triggers", "")
        if query_lower in triggers.lower():
            score += 5
        # 上下文内容匹配
        context = info.get("context", "")
        if query_lower in context.lower():
            score += 3
        # 工作流匹配
        workflow = info.get("workflow", "")
        if query_lower in workflow.lower():
            score += 2
        if score > 0:
            matched[name] = (score, info)

    # 按分数排序
    sorted_names = sorted(matched.keys(), key=lambda n: matched[n][0], reverse=True)
    return _build_skill_list({n: matched[n][1] for n in sorted_names})


def _build_skill_list(skills: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
    """构建技能列表，包含摘要信息。"""
    result = []
    for name, info in skills.items():
        triggers = info.get("triggers", "")
        context = info.get("context", "")
        # 提取简要说明：取上下文第一行或前 60 字符
        desc = context.split("\n")[0] if context else ""
        if len(desc) > 60:
            desc = desc[:57] + "..."
        # 提取触发词摘要
        trigger_summary = triggers
        if len(trigger_summary) > 80:
            trigger_summary = trigger_summary[:77] + "..."
        result.append({
            "name": name,
            "description": desc,
            "triggers": trigger_summary,
            "has_workflow": bool(info.get("workflow")),
        })
    return result


def get_active_skills_for_input(user_input: str) -> List[str]:
    """根据当前配置和输入，返回应激活的技能列表。"""
    state = get_skill_config()
    mode = state.get("mode", "auto")
    active_list = state.get("active_skills", [])

    matched = match_skills(user_input)

    if mode == "manual":
        # 手动模式：只返回同时在 active_list 中且被匹配的技能
        return [m for m in matched if m in active_list]
    else:
        # 自动模式：返回所有匹配的技能
        return matched


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


def list_skills() -> List[Dict[str, Any]]:
    """返回所有技能列表（含摘要信息）。"""
    return search_skills("")


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
    """一键匹配并返回所有命中技能的上下文文本（遵循配置模式）。"""
    matched = get_active_skills_for_input(user_input)
    if not matched:
        return ""
    contexts = [get_skill_context(name) for name in matched]
    return "\n\n".join(contexts)


def get_active_skill_names(user_input: str) -> List[str]:
    """返回当前输入激活的技能名称列表（遵循配置模式）。"""
    return get_active_skills_for_input(user_input)


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
