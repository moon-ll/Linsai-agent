#!/usr/bin/env python3
"""
research_profiler.py — 研究方向感知器

用途：
    从用户画像、活跃任务、最近会话中动态提取研究方向关键词，
    为自主学习引擎提供"该学什么"的方向指引。

用法示例：
    >>> from research_profiler import build_research_profile, get_research_keywords
    >>> profile = build_research_profile()
    >>> print(profile["keywords"])
    [('阿秒科学', 0.85), ('固体高次谐波', 0.72), ...]
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
MEMORY_DIR = PROJECT_ROOT / "memory"
TASKS_DIR = PROJECT_ROOT / "tasks"
SESSIONS_DIR = PROJECT_ROOT / "sessions"
PROFILE_PATH = MEMORY_DIR / "research-profile.json"

# 中英文通用停用词
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "of", "to", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "just", "and",
    "but", "if", "or", "because", "until", "while", "about", "against",
    "this", "that", "these", "those", "i", "me", "my", "myself", "we",
    "our", "you", "your", "he", "him", "his", "she", "her", "it", "its",
    "they", "them", "their", "的", "了", "在", "是", "我", "有", "和",
    "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说",
    "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这",
    "那", "个", "为", "之", "与", "及", "等", "可", "能", "让", "给",
    "把", "被", "对", "将", "还", "可以", "我们", "你们", "他们",
    "什么", "怎么", "为什么", "如何", "还是", "或者", "以及", "但是",
}

# 技术术语模式
_TECH_PATTERNS = [
    # 英文：大写缩写（HHG, DFG, PRL）或 连字符复合词（solid-state）
    re.compile(r"\b[A-Z]{2,8}\b"),
    re.compile(r"\b[a-z]+(?:-[a-z]+)+\b"),
    # 数字+单位（如 800nm, 10fs, 1e15 W/cm²）
    re.compile(r"\b\d+\.?\d*\s*(?:nm|μm|mm|cm|m|fs|ps|ns|us|ms|s|eV|keV|MeV|GeV|Hz|kHz|MHz|GHz|THz|PHz|W|mW|kW|MW|GW|TW|PW|V|kV|MV|GV|J|mJ|μJ|nJ|K|°C|°F|bar|mbar|atm|Pa|kPa|MPa|GPa|a\.u\.|arb\.?\s*unit)\b", re.IGNORECASE),
    # 中文：2-8个连续汉字（可能是专业术语）
    re.compile(r"[\u4e00-\u9fff]{2,8}"),
]


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any = None) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default if default is not None else {}


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 关键词提取
# ---------------------------------------------------------------------------

def _extract_terms(text: str) -> List[str]:
    """从文本中提取候选技术术语。"""
    if not text:
        return []

    terms: List[str] = []
    for pat in _TECH_PATTERNS:
        for match in pat.finditer(text):
            term = match.group(0).strip()
            if len(term) >= 2 and term.lower() not in _STOPWORDS:
                terms.append(term)

    # 额外：提取英文名词短语（连续的小写字母序列，长度 4-20）
    for match in re.finditer(r"\b[a-z]{4,20}\b", text):
        word = match.group(0)
        if word not in _STOPWORDS:
            terms.append(word)

    return terms


def _tfidf_weights(term_counter: Counter, all_counters: List[Counter]) -> Dict[str, float]:
    """基于 TF-IDF 计算权重。"""
    total_docs = max(len(all_counters), 1)
    weights = {}

    for term, count in term_counter.items():
        tf = 1 + math.log(count) if count > 0 else 0
        doc_freq = sum(1 for c in all_counters if term in c)
        idf = math.log(total_docs / (doc_freq + 1)) + 1
        weights[term] = tf * idf

    return weights


# ---------------------------------------------------------------------------
# 数据源提取
# ---------------------------------------------------------------------------

def _from_user_profile() -> Tuple[Counter, float]:
    """从用户画像提取研究关键词。"""
    profile = _load_json(MEMORY_DIR / "user-profile.json", {})
    text_parts = []

    research_field = profile.get("research_field", "")
    if research_field:
        text_parts.append(research_field)

    interests = profile.get("interests", [])
    if isinstance(interests, list):
        text_parts.extend(interests)

    skills = profile.get("skills", [])
    if isinstance(skills, list):
        text_parts.extend(skills)

    text = " ".join(str(p) for p in text_parts)
    terms = _extract_terms(text)
    return Counter(terms), 1.0  # 用户画像权重最高


def _from_active_tasks() -> Tuple[Counter, float]:
    """从活跃任务提取关键词。"""
    active_dir = TASKS_DIR / "active"
    if not active_dir.exists():
        return Counter(), 0.8

    texts = []
    for fpath in sorted(active_dir.glob("*.json")):
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            title = data.get("title", "")
            description = data.get("description", "")
            tags = data.get("tags", [])
            parts = [title, description]
            if isinstance(tags, list):
                parts.extend(tags)
            texts.append(" ".join(str(p) for p in parts if p))
        except Exception:
            continue

    text = " ".join(texts)
    terms = _extract_terms(text)
    return Counter(terms), 0.8


def _from_recent_sessions(limit: int = 3, window_days: int = 30) -> Tuple[Counter, float]:
    """从最近活跃会话提取技术术语。"""
    if not SESSIONS_DIR.exists():
        return Counter(), 0.6

    cutoff = datetime.now(timezone.utc).timestamp() - window_days * 86400
    sessions = []

    for sess_dir in sorted(SESSIONS_DIR.iterdir()):
        if not sess_dir.is_dir():
            continue
        state_path = sess_dir / "state.json"
        if not state_path.exists():
            continue
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            last_active = state.get("last_active", "")
            if not last_active:
                continue
            la_ts = datetime.fromisoformat(last_active.replace("Z", "+00:00")).timestamp()
            if la_ts >= cutoff:
                sessions.append((la_ts, sess_dir))
        except Exception:
            continue

    # 按最近活跃排序，取 limit 个
    sessions.sort(reverse=True)
    sessions = sessions[:limit]

    texts = []
    for _, sess_dir in sessions:
        msg_path = sess_dir / "messages.json"
        if not msg_path.exists():
            continue
        try:
            msgs = json.loads(msg_path.read_text(encoding="utf-8"))
            for msg in msgs:
                content = msg.get("content", "")
                if isinstance(content, str) and len(content) > 10:
                    texts.append(content)
        except Exception:
            continue

    text = " ".join(texts)
    terms = _extract_terms(text)
    return Counter(terms), 0.6


# ---------------------------------------------------------------------------
# 主接口
# ---------------------------------------------------------------------------

def build_research_profile() -> Dict[str, Any]:
    """构建研究方向画像，保存到 memory/research-profile.json。

    Returns:
        {
            "keywords": [("阿秒科学", 0.85), ("HHG", 0.72), ...],
            "sources": {"profile": [...], "tasks": [...], "sessions": [...]},
            "built_at": "2026-05-12T10:00:00Z",
            "version": "1.0"
        }
    """
    profile_counter, profile_w = _from_user_profile()
    tasks_counter, tasks_w = _from_active_tasks()
    sessions_counter, sessions_w = _from_recent_sessions()

    all_counters = [profile_counter, tasks_counter, sessions_counter]

    # 加权合并
    merged = Counter()
    for term, count in profile_counter.items():
        merged[term] += count * profile_w
    for term, count in tasks_counter.items():
        merged[term] += count * tasks_w
    for term, count in sessions_counter.items():
        merged[term] += count * sessions_w

    # TF-IDF 权重
    weights = _tfidf_weights(merged, all_counters)

    # 排序，取 top 20
    sorted_keywords = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:20]

    # 归一化到 0-1
    if sorted_keywords:
        max_w = sorted_keywords[0][1]
        min_w = sorted_keywords[-1][1]
        rng = max_w - min_w if max_w > min_w else 1.0
        sorted_keywords = [(t, round((w - min_w) / rng, 3)) for t, w in sorted_keywords]

    result = {
        "keywords": sorted_keywords,
        "sources": {
            "profile": list(profile_counter.keys())[:10],
            "tasks": list(tasks_counter.keys())[:10],
            "sessions": list(sessions_counter.keys())[:10],
        },
        "built_at": _now_utc(),
        "version": "1.0",
    }

    _save_json(PROFILE_PATH, result)
    return result


def get_research_keywords(top_k: int = 10) -> List[Tuple[str, float]]:
    """读取研究方向关键词。若不存在则重新构建。"""
    profile = _load_json(PROFILE_PATH, {})
    if not profile:
        profile = build_research_profile()
    keywords = profile.get("keywords", [])
    return keywords[:top_k]


def get_research_profile_text() -> str:
    """返回研究方向文本，供 prompt 注入使用。"""
    keywords = get_research_keywords(top_k=10)
    if not keywords:
        return "研究方向未知"
    parts = [f"{term}（相关度 {weight:.0%}）" for term, weight in keywords]
    return "、".join(parts)


def update_if_stale(max_age_days: int = 7) -> Optional[Dict[str, Any]]:
    """如果画像过期，则重新构建并返回变化 diff。

    Returns:
        变化报告，或 None（如果未过期）
    """
    profile = _load_json(PROFILE_PATH, {})
    built_at = profile.get("built_at", "")
    if not built_at:
        return build_research_profile()

    try:
        built_dt = datetime.fromisoformat(built_at.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - built_dt).days
    except Exception:
        return build_research_profile()

    if age_days < max_age_days:
        return None

    old_keywords = {k: w for k, w in profile.get("keywords", [])}
    new_profile = build_research_profile()
    new_keywords = {k: w for k, w in new_profile.get("keywords", [])}

    # 计算变化
    old_set = set(old_keywords.keys())
    new_set = set(new_keywords.keys())
    added = new_set - old_set
    removed = old_set - new_set
    changed = {k for k in old_set & new_set if abs(old_keywords[k] - new_keywords[k]) > 0.1}

    drift = 0.0
    if old_set:
        common = old_set & new_set
        if common:
            drift = sum(abs(old_keywords[k] - new_keywords[k]) for k in common) / len(common)

    diff = {
        "updated": True,
        "old_age_days": age_days,
        "added_keywords": list(added)[:10],
        "removed_keywords": list(removed)[:10],
        "changed_keywords": list(changed)[:10],
        "direction_drift": round(drift, 3),
        "new_profile": new_profile,
    }

    # 如果方向漂移 > 20%，记录到生长日志
    if drift > 0.2:
        try:
            kb = _import_kb()
            kb.log_growth("profile_update", "research-profile", "auto",
                          f"研究方向漂移 {drift:.0%}，新增: {', '.join(list(added)[:3])}")
        except Exception:
            pass

    return diff


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("◐ 开始 research_profiler 自检")
    print("=" * 50)

    print("\n[1/4] 测试 _extract_terms...")
    sample = "我在研究固体高次谐波产生（solid-state HHG），使用 800nm 飞秒激光。"
    terms = _extract_terms(sample)
    print(f"   输入: {sample}")
    print(f"   提取: {terms}")
    assert any("HHG" in t for t in terms), "应提取 HHG"
    assert any("800nm" in t for t in terms), "应提取 800nm"
    assert any("固体" in t for t in terms), "应提取中文术语"
    print("   ✓ 术语提取通过")

    print("\n[2/4] 测试 build_research_profile...")
    profile = build_research_profile()
    assert "keywords" in profile
    assert "built_at" in profile
    assert "sources" in profile
    print(f"   关键词数量: {len(profile['keywords'])}")
    if profile["keywords"]:
        print(f"   前 3 个: {profile['keywords'][:3]}")
    print("   ✓ 画像构建通过")

    print("\n[3/4] 测试 get_research_keywords...")
    kw = get_research_keywords(top_k=5)
    assert isinstance(kw, list)
    print(f"   返回: {kw}")
    print("   ✓ 读取通过")

    print("\n[4/4] 测试 get_research_profile_text...")
    text = get_research_profile_text()
    print(f"   文本: {text[:100]}")
    print("   ✓ 文本生成通过")

    print("\n" + "=" * 50)
    print("✓ 所有自检项目通过")
    print("=" * 50)
