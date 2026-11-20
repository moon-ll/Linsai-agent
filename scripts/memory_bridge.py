#!/usr/bin/env python3
"""memory_bridge.py — hermes → CoPilot 记忆单向同步。

将 hermes linsai profile 的 MEMORY.md / USER.md 同步到 CoPilot，
使 CoPilot 的上下文构建能感知 hermes 端的最新记忆。

同步方向：hermes → CoPilot（单向，hermes 是权威源）
同步策略：
  1. 原文快照：hermes MEMORY.md + USER.md → memory/hermes-memory-snapshot.json
  2. 关键词提取：从 Markdown 中提取研究关键词 → 合并到 user-profile.json
  3. 增量跳过：文件 mtime 未变则跳过

hermes 记忆文件位置：
  ~/.hermes/profiles/linsai/memories/MEMORY.md  — 高频核心事实（§ 分隔）
  ~/.hermes/profiles/linsai/memories/USER.md    — 用户身份/偏好/科研特征

CoPilot 目标文件：
  memory/hermes-memory-snapshot.json  — 原文快照（供 context_builder 注入）
  memory/user-profile.json            — 研究关键词合并

用法示例：
    >>> from memory_bridge import sync_memory
    >>> result = sync_memory()
    >>> print(result)  # {"synced": True, "memory_md_size": 3064, ...}

规范：仅标准库，PROJECT_ROOT 推导，JSON ensure_ascii=False。
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from paths import MEMORY_DIR
from common import save_json, load_json

# ========== 路径配置 ==========
# hermes 实际安装在 ~/.hermes（非 paths.py 中的旧版 ~/.kimi）
_HERMES_HOME = Path.home() / ".hermes"
HERMES_LINSAI_MEMORIES = _HERMES_HOME / "profiles" / "linsai" / "memories"
HERMES_MEMORY_MD = HERMES_LINSAI_MEMORIES / "MEMORY.md"
HERMES_USER_MD = HERMES_LINSAI_MEMORIES / "USER.md"

# CoPilot 快照路径
SNAPSHOT_PATH = MEMORY_DIR / "hermes-memory-snapshot.json"
USER_PROFILE_PATH = MEMORY_DIR / "user-profile.json"

# ========== 研究关键词库（用于从 Markdown 中提取）==========
_RESEARCH_KEYWORDS = [
    "HHG", "高次谐波", "固体HHG", "阿秒", "attosecond",
    "强场", "超快", "谷电子学", "能谷电子学", "valleytronics",
    "拍赫兹", "TMD", "拓扑绝缘体", "相位匹配",
    "量子几何", "Berry curvature", "Floquet",
    "XUV", "非线性光学", "condensed matter",
    "deepxiv", "NSFC", "PRL",
]

# 用户偏好关键词
_PREFERENCE_KEYWORDS = [
    "回复简洁", "writing-plans", "简报",
    "系统性解决", "不为空洞鼓励",
    "先弄清原因", "先规划再行动",
]


# ========== 工具函数 ==========

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_hermes_file(path: Path) -> str:
    """安全读取 hermes 文件。"""
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _extract_keywords(text: str, keyword_list: List[str]) -> List[str]:
    """从文本中提取出现的关键词。"""
    found = []
    text_lower = text.lower()
    for kw in keyword_list:
        if kw.lower() in text_lower:
            if kw not in found:
                found.append(kw)
    return found


def _extract_sections(text: str) -> Dict[str, str]:
    """从 USER.md 提取标题章节（## 标题 → 内容）。"""
    sections = {}
    current_title = ""
    current_lines = []
    for line in text.split("\n"):
        if line.startswith("## "):
            if current_title:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_title:
        sections[current_title] = "\n".join(current_lines).strip()
    return sections


# ========== 核心同步接口 ==========

def sync_memory(force: bool = False) -> Dict[str, Any]:
    """将 hermes 记忆同步到 CoPilot（单向）。

    Args:
        force: 强制同步（忽略 mtime 检查）

    Returns:
        同步结果字典
    """
    result: Dict[str, Any] = {
        "synced": False,
        "memory_md_size": 0,
        "user_md_size": 0,
        "keywords_extracted": 0,
        "snapshot_updated": False,
        "profile_updated": False,
        "skipped": False,
        "error": "",
    }

    # 1. 读取 hermes 记忆文件
    memory_md = _read_hermes_file(HERMES_MEMORY_MD)
    user_md = _read_hermes_file(HERMES_USER_MD)

    if not memory_md and not user_md:
        result["error"] = "hermes 记忆文件不存在或为空"
        return result

    result["memory_md_size"] = len(memory_md)
    result["user_md_size"] = len(user_md)

    # 2. 增量检查：mtime 未变则跳过
    if not force and SNAPSHOT_PATH.exists():
        try:
            old_snapshot = load_json(SNAPSHOT_PATH)
            old_memory_mtime = old_snapshot.get("memory_md_mtime", 0)
            old_user_mtime = old_snapshot.get("user_md_mtime", 0)
            current_memory_mtime = HERMES_MEMORY_MD.stat().st_mtime if HERMES_MEMORY_MD.exists() else 0
            current_user_mtime = HERMES_USER_MD.stat().st_mtime if HERMES_USER_MD.exists() else 0
            if old_memory_mtime == current_memory_mtime and old_user_mtime == current_user_mtime:
                result["skipped"] = True
                result["synced"] = True
                return result
        except Exception:
            pass  # 快照损坏，继续同步

    # 3. 保存原文快照
    memory_md_mtime = HERMES_MEMORY_MD.stat().st_mtime if HERMES_MEMORY_MD.exists() else 0
    user_md_mtime = HERMES_USER_MD.stat().st_mtime if HERMES_USER_MD.exists() else 0

    snapshot = {
        "memory_md": memory_md,
        "user_md": user_md,
        "memory_md_mtime": memory_md_mtime,
        "user_md_mtime": user_md_mtime,
        "synced_at": _now(),
        "source": "hermes-profile-linsai",
    }
    try:
        save_json(SNAPSHOT_PATH, snapshot)
        result["snapshot_updated"] = True
    except Exception as e:
        result["error"] = f"快照保存失败: {e}"
        return result

    # 4. 提取研究关键词，合并到 user-profile.json
    combined_text = memory_md + "\n" + user_md
    research_keywords = _extract_keywords(combined_text, _RESEARCH_KEYWORDS)
    preference_keywords = _extract_keywords(combined_text, _PREFERENCE_KEYWORDS)
    result["keywords_extracted"] = len(research_keywords)

    try:
        profile = load_json(USER_PROFILE_PATH)
        if not isinstance(profile, dict):
            profile = {}

        # 合并研究关键词（不覆盖已有，只追加新词）
        existing_research = profile.get("research_field", [])
        if not isinstance(existing_research, list):
            existing_research = []
        for kw in research_keywords:
            if kw not in existing_research:
                existing_research.append(kw)
        profile["research_field"] = existing_research

        # 更新 hermes 偏好（单独字段，不覆盖 CoPilot 自有偏好）
        hermes_prefs = profile.get("hermes_preferences", {})
        hermes_prefs["keywords"] = preference_keywords
        hermes_prefs["last_synced"] = _now()
        profile["hermes_preferences"] = hermes_prefs

        # 记录同步时间
        profile["hermes_memory_synced_at"] = _now()

        save_json(USER_PROFILE_PATH, profile)
        result["profile_updated"] = True
    except Exception as e:
        result["error"] = f"user-profile 更新失败: {e}"
        # 快照已保存，不算完全失败

    result["synced"] = True
    return result


def get_hermes_memory_snapshot() -> Dict[str, Any]:
    """获取 hermes 记忆快照（供 context_builder 使用）。"""
    if not SNAPSHOT_PATH.exists():
        return {}
    try:
        return load_json(SNAPSHOT_PATH)
    except Exception:
        return {}


def get_hermes_memory_text(max_chars: int = 3000) -> str:
    """获取 hermes 记忆文本（截断版，供 prompt 注入）。

    Args:
        max_chars: 最大字符数

    Returns:
        合并的 MEMORY.md + USER.md 文本（截断）
    """
    snapshot = get_hermes_memory_snapshot()
    memory_md = snapshot.get("memory_md", "")
    user_md = snapshot.get("user_md", "")
    combined = f"=== hermes MEMORY.md ===\n{memory_md}\n\n=== hermes USER.md ===\n{user_md}"
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n...(截断)"
    return combined


# ========== 自检 ==========

def _self_check() -> int:
    """自检：验证 hermes 记忆文件读取 + 快照 + 关键词提取。"""
    print("=== memory_bridge 自检 ===")
    checks = 0
    fails = 0

    # 1. hermes 记忆文件存在
    if HERMES_MEMORY_MD.exists() or HERMES_USER_MD.exists():
        checks += 1
        mem_size = HERMES_MEMORY_MD.stat().st_size if HERMES_MEMORY_MD.exists() else 0
        usr_size = HERMES_USER_MD.stat().st_size if HERMES_USER_MD.exists() else 0
        print(f"  [1/5] hermes 记忆文件存在 ✓ (MEMORY: {mem_size}B, USER: {usr_size}B)")
    else:
        fails += 1
        print(f"  [1/5] hermes 记忆文件不存在 ✗")

    # 2. 同步执行
    try:
        result = sync_memory(force=True)
        assert result["synced"], f"同步失败: {result.get('error')}"
        checks += 1
        print(f"  [2/5] 同步执行 ✓ (memory: {result['memory_md_size']}B, user: {result['user_md_size']}B)")
    except Exception as e:
        fails += 1
        print(f"  [2/5] 同步执行 ✗: {e}")

    # 3. 快照文件生成
    try:
        snapshot = get_hermes_memory_snapshot()
        assert "memory_md" in snapshot, "快照缺少 memory_md"
        assert "user_md" in snapshot, "快照缺少 user_md"
        checks += 1
        print(f"  [3/5] 快照文件 ✓ (memory_md: {len(snapshot['memory_md'])} chars)")
    except Exception as e:
        fails += 1
        print(f"  [3/5] 快照文件 ✗: {e}")

    # 4. 关键词提取
    try:
        result = sync_memory(force=True)
        assert result["keywords_extracted"] > 0, "未提取到关键词"
        checks += 1
        print(f"  [4/5] 关键词提取 ✓ ({result['keywords_extracted']} 个)")
    except Exception as e:
        fails += 1
        print(f"  [4/5] 关键词提取 ✗: {e}")

    # 5. user-profile.json 更新
    try:
        profile = load_json(USER_PROFILE_PATH)
        assert "hermes_memory_synced_at" in profile, "user-profile 缺少 hermes_memory_synced_at"
        assert "hermes_preferences" in profile, "user-profile 缺少 hermes_preferences"
        checks += 1
        print(f"  [5/5] user-profile 更新 ✓ (research_field: {len(profile.get('research_field', []))} 个)")
    except Exception as e:
        fails += 1
        print(f"  [5/5] user-profile 更新 ✗: {e}")

    print(f"=== 结果: {checks}/{checks + fails} 通过 ===\n")
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        sys.exit(_self_check())
    print("memory_bridge — hermes → CoPilot 记忆单向同步")
    print(f"hermes MEMORY.md: {HERMES_MEMORY_MD}")
    print(f"hermes USER.md: {HERMES_USER_MD}")
    print(f"CoPilot 快照: {SNAPSHOT_PATH}")
    print("\n用法: from memory_bridge import sync_memory")
    print("自检: python3 memory_bridge.py --self-check")
