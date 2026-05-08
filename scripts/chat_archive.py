#!/usr/bin/env python3
"""聊天记录智能归档系统 — 关键词提炼 + 跨会话全文检索。

将聊天记录视为"外部存档"（类似微信历史记录），与林赛的"人脑记忆"分离。
- 完整保留所有 messages.json
- 为每个会话自动提炼核心关键词
- 支持跨会话全文搜索

用法:
    python3 scripts/chat_archive.py --keywords <session_id>   # 为指定会话生成关键词
    python3 scripts/chat_archive.py --search "相位匹配"         # 搜索历史记录
    python3 scripts/chat_archive.py --index                     # 重建全局索引
    python3 scripts/chat_archive.py --self-check                # 运行自检
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 路径与导入
_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import copilot_engine as ce


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
_SESSIONS_DIR = _PROJECT_ROOT / "sessions"
_KEYWORDS_FILE = "keywords.json"
_ARCHIVE_INDEX = _PROJECT_ROOT / "memory" / "chat-archive-index.json"

# 中文停用词（简单列表）
_STOP_WORDS = {
    "的", "了", "在", "是", "我", "你", "他", "她", "它", "我们", "你们",
    "他们", "这", "那", "有", "和", "与", "或", "但", "而", "因为", "所以",
    "如果", "就", "都", "要", "会", "能", "可以", "请", "把", "被", "让",
    "对", "给", "为", "从", "到", "上", "下", "中", "里", "个", "种",
    "想", "说", "做", "看", "用", "来", "去", "过", "也", "很", "非常",
    "可能", "大概", "应该", "一定", "不", "没", "无", "非", "没",
}

# 提取关键词时关注的高价值词性模式
_KEYWORD_PATTERNS = [
    r"[A-Z]{2,}",  # 英文缩写/术语
    r"[\u4e00-\u9fa5]{2,8}",  # 中文词组
]


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _load_messages(session_id: str) -> List[Dict[str, Any]]:
    """加载指定会话的完整消息列表。"""
    msg_path = _SESSIONS_DIR / session_id / "messages.json"
    if not msg_path.exists():
        return []
    try:
        with open(msg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else data.get("messages", [])
    except Exception:
        return []


def _load_session_state(session_id: str) -> Dict[str, Any]:
    """加载会话状态。"""
    state_path = _SESSIONS_DIR / session_id / "state.json"
    if not state_path.exists():
        return {}
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _extract_words(text: str) -> List[str]:
    """从文本中提取候选关键词。"""
    if not text:
        return []

    words = []
    # 英文术语（2-20字母）
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9\-]{1,19}", text):
        word = m.group().lower()
        if len(word) >= 2:
            words.append(word)

    # 中文词组（2-8字）
    for m in re.finditer(r"[\u4e00-\u9fa5]{2,8}", text):
        words.append(m.group())

    return words


def _filter_stop_words(words: List[str]) -> List[str]:
    """过滤停用词和过短词。"""
    filtered = []
    for w in words:
        if w in _STOP_WORDS:
            continue
        if len(w) < 2:
            continue
        if re.match(r"^\d+$", w):
            continue
        filtered.append(w)
    return filtered


def _count_freq(words: List[str]) -> Dict[str, int]:
    """统计词频。"""
    freq: Dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return freq


# ---------------------------------------------------------------------------
# 关键词提炼
# ---------------------------------------------------------------------------

def extract_keywords(session_id: str, force: bool = False) -> List[str]:
    """为指定会话提取核心关键词。

    策略:
        1. 先通过词频统计做候选（本地、零成本）
        2. 如果会话有消息，调用 LLM 做语义提炼（更精准）
        3. 合并去重，保存到 keywords.json

    Returns:
        关键词列表（按重要性排序）
    """
    kw_path = _SESSIONS_DIR / session_id / _KEYWORDS_FILE

    # 如果已存在且不强制重新生成，直接返回
    if not force and kw_path.exists():
        try:
            with open(kw_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("keywords", [])
        except Exception:
            pass

    messages = _load_messages(session_id)
    if not messages:
        return []

    # ---- 阶段 1：本地词频统计（零成本）----
    all_text = " ".join([m.get("content", "") for m in messages])
    words = _extract_words(all_text)
    words = _filter_stop_words(words)
    freq = _count_freq(words)

    # 取高频词作为候选
    candidates = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    local_keywords = [w for w, c in candidates[:20]]

    # ---- 阶段 2：LLM 语义提炼（更精准）----
    llm_keywords: List[str] = []
    try:
        # 构建精简摘要供 LLM 分析
        summary = "\n".join([
            f"{'用户' if m['role']=='user' else '林赛'}: {m['content'][:100]}"
            for m in messages[:10]
        ])

        prompt = (
            "你是信息整理助手。请从以下对话中提炼 5-10 个核心关键词，"
            "用于后续检索。要求:\n"
            "1. 关键词应涵盖讨论的主题、技术、方法、概念\n"
            "2. 优先选择专业术语和实体名词\n"
            "3. 中英文混合时保留英文缩写\n"
            "4. 只返回关键词列表，每行一个，不要解释\n\n"
            f"对话摘要:\n{summary}\n\n关键词:"
        )

        resp = ce.call_llm(
            "你是一个严谨的信息整理助手，只输出关键词列表。",
            [{"role": "user", "content": prompt}],
        )

        # 解析 LLM 返回的关键词
        for line in resp.strip().split("\n"):
            line = line.strip().lstrip("-•* ").rstrip(",.;:，。；：")
            if line and len(line) < 30:
                llm_keywords.append(line)
    except Exception:
        pass  # LLM 失败不影响本地关键词

    # ---- 阶段 3：合并去重 ----
    merged: List[str] = []
    seen = set()
    for w in llm_keywords + local_keywords:
        w = w.strip()
        if not w:
            continue
        # 子串去重：如果 "MATLAB" 已存在，不再加 "MATLAB编程"
        skip = False
        for existing in list(seen):
            if w in existing and len(w) < len(existing):
                skip = True
                break
            if existing in w and len(existing) < len(w):
                seen.discard(existing)
        if skip:
            continue
        if w not in seen:
            seen.add(w)
            merged.append(w)

    # 限制数量
    merged = merged[:15]

    # 保存
    state = _load_session_state(session_id)
    kw_data = {
        "session_id": session_id,
        "topic": state.get("topic", ""),
        "keywords": merged,
        "generated_at": state.get("last_active", ""),
        "message_count": len(messages),
    }
    try:
        with open(kw_path, "w", encoding="utf-8") as f:
            json.dump(kw_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return merged


def get_session_keywords(session_id: str) -> List[str]:
    """获取会话关键词（缓存优先）。"""
    kw_path = _SESSIONS_DIR / session_id / _KEYWORDS_FILE
    if kw_path.exists():
        try:
            with open(kw_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("keywords", [])
        except Exception:
            pass
    return extract_keywords(session_id)


# ---------------------------------------------------------------------------
# 跨会话搜索
# ---------------------------------------------------------------------------

def search_history(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """跨会话全文搜索历史消息。

    策略:
        1. 按空格切分查询词
        2. 遍历所有 sessions/ 下的 messages.json
        3. 匹配消息内容是否包含查询词
        4. 按匹配度排序（匹配词数多的优先）
    """
    if not query or not query.strip():
        return []

    query_terms = [t.strip().lower() for t in query.split() if len(t.strip()) >= 2]
    if not query_terms:
        return []

    results: List[Dict[str, Any]] = []

    for sess_dir in _SESSIONS_DIR.iterdir():
        if not sess_dir.is_dir() or sess_dir.name in ("archived", "agora_exports"):
            continue

        messages = _load_messages(sess_dir.name)
        state = _load_session_state(sess_dir.name)
        topic = state.get("topic", sess_dir.name)

        for msg in messages:
            content = msg.get("content", "")
            if not content:
                continue

            content_lower = content.lower()
            match_count = sum(1 for t in query_terms if t in content_lower)

            if match_count > 0:
                # 截取匹配上下文（前后50字）
                preview = content[:120] + "…" if len(content) > 120 else content
                results.append({
                    "session_id": sess_dir.name,
                    "topic": topic,
                    "msg_id": msg.get("msg_id", ""),
                    "role": msg.get("role", ""),
                    "content_preview": preview,
                    "full_content": content,
                    "timestamp": msg.get("timestamp", ""),
                    "match_score": match_count,
                })

    # 按匹配度排序，取前 N 条
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:limit]


# ---------------------------------------------------------------------------
# 全局索引
# ---------------------------------------------------------------------------

def build_archive_index() -> Dict[str, Any]:
    """重建聊天记录全局索引。

    索引结构:
    {
      "version": "1.0",
      "updated_at": "2026-05-08T12:00:00Z",
      "sessions": [
        {
          "session_id": "...",
          "topic": "...",
          "message_count": 12,
          "keywords": [...],
          "last_active": "..."
        }
      ],
      "total_messages": 156
    }
    """
    sessions = []
    total_messages = 0

    for sess_dir in sorted(_SESSIONS_DIR.iterdir()):
        if not sess_dir.is_dir() or sess_dir.name in ("archived", "agora_exports"):
            continue

        state = _load_session_state(sess_dir.name)
        messages = _load_messages(sess_dir.name)
        keywords = get_session_keywords(sess_dir.name)

        sessions.append({
            "session_id": sess_dir.name,
            "topic": state.get("topic", sess_dir.name),
            "mode": state.get("mode", "co-working"),
            "message_count": len(messages),
            "keywords": keywords,
            "last_active": state.get("last_active", ""),
        })
        total_messages += len(messages)

    index = {
        "version": "1.0",
        "updated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_sessions": len(sessions),
        "total_messages": total_messages,
        "sessions": sessions,
    }

    try:
        _ARCHIVE_INDEX.parent.mkdir(parents=True, exist_ok=True)
        with open(_ARCHIVE_INDEX, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"✗ 索引保存失败: {e}")

    return index


def get_archive_index() -> Dict[str, Any]:
    """读取全局索引（缓存优先）。"""
    if _ARCHIVE_INDEX.exists():
        try:
            with open(_ARCHIVE_INDEX, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return build_archive_index()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _self_check() -> bool:
    """运行模块级自检。"""
    ok = True

    # 1. 路径推导
    if _SESSIONS_DIR.name == "sessions":
        print("✓ SESSIONS_DIR 推导正确")
    else:
        print("✗ SESSIONS_DIR 推导异常")
        ok = False

    # 2. 分词
    words = _extract_words("固体HHG实验中使用了MATLAB和Python")
    if len(words) >= 4:
        print(f"✓ 分词提取: {len(words)} 个词")
    else:
        print(f"✗ 分词异常: {words}")
        ok = False

    # 3. 停用词过滤
    filtered = _filter_stop_words(["的", "了", "固体", "实验", "MATLAB"])
    if "的" not in filtered and "固体" in filtered:
        print("✓ 停用词过滤正确")
    else:
        print("✗ 停用词过滤异常")
        ok = False

    # 4. 搜索（空查询）
    if search_history("") == []:
        print("✓ 空查询处理正确")
    else:
        print("✗ 空查询异常")
        ok = False

    return ok


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="聊天记录智能归档系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/chat_archive.py --keywords 20260508-固体HHG   # 生成关键词
  python3 scripts/chat_archive.py --search "相位匹配"              # 搜索历史
  python3 scripts/chat_archive.py --index                           # 重建索引
  python3 scripts/chat_archive.py --self-check                      # 自检
        """,
    )
    parser.add_argument("--keywords", metavar="SID", help="为指定会话生成关键词")
    parser.add_argument("--search", metavar="QUERY", help="搜索历史记录")
    parser.add_argument("--index", action="store_true", help="重建全局索引")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args(argv)

    if args.self_check:
        print("=== 聊天记录归档系统自检 ===")
        ok = _self_check()
        print("-" * 30)
        print("✓ 全部通过" if ok else "✗ 存在失败项")
        return 0 if ok else 1

    if args.keywords:
        kws = extract_keywords(args.keywords, force=True)
        print(f"✓ 关键词已生成 ({len(kws)} 个):")
        for w in kws:
            print(f"  • {w}")
        return 0

    if args.search:
        results = search_history(args.search)
        print(f"✓ 找到 {len(results)} 条匹配:")
        for r in results:
            print(f"\n  [{r['session_id']}] {r['topic']}")
            print(f"  {r['role']}: {r['content_preview']}")
        return 0

    if args.index:
        idx = build_archive_index()
        print(f"✓ 索引已重建")
        print(f"  会话数: {idx['total_sessions']}")
        print(f"  消息数: {idx['total_messages']}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
