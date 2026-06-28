#!/usr/bin/env python3
"""kb_text.py — 知识库文本处理基础工具。

提供分词、文档分块、IDF 计算、frontmatter 解析/生成、安全文件名等底层工具，
被 kb_graph / kb_wiki / kb_index / kb_health 子模块共享依赖。

用法示例：
    >>> from kb_text import _tokenize, parse_frontmatter, build_frontmatter
    >>> tokens = _tokenize("固体高次谐波产生")
    >>> fm, body = parse_frontmatter("---\\ntitle: 测试\\n---\\n正文")

规范：
    - 仅使用 Python 3 标准库
    - 不修改任何函数逻辑，自 knowledge_base.py 物理迁移而来
"""

import math
import re
from typing import Any, Dict, List, Set, Tuple


# ─────────────────────────────────────────────
# 常量
# ─────────────────────────────────────────────

_STOPWORDS: Set[str] = {
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人",
    "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
    "你", "会", "着", "没有", "看", "好", "自己", "这", "那",
    "可以", "他", "她", "它", "们", "与", "及", "或", "但是", "因为",
    "所以", "如果", "则", "而", "于", "以", "为", "之", "其", "将",
    "被", "把", "让", "向", "从", "到", "对", "关于", "根据", "按照",
    "我们", "这个", "那个", "什么", "怎么", "如何", "为什么",
}


# ─────────────────────────────────────────────
# Frontmatter 解析与生成
# ─────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """解析 Markdown 文件的 YAML frontmatter。

    Returns:
        (frontmatter_dict, body_markdown)
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    yaml_text = m.group(1).strip()
    body = m.group(2).strip()
    meta: Dict[str, Any] = {}
    for line in yaml_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            # 简单类型推断
            if val.startswith("[") and val.endswith("]"):
                # 数组：["a", "b"] 或 [a, b]
                inner = val[1:-1]
                meta[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            elif val.lower() in ("true", "false"):
                meta[key] = val.lower() == "true"
            elif re.match(r"^\d+\.\d+$", val):
                meta[key] = float(val)
            elif re.match(r"^\d+$", val):
                meta[key] = int(val)
            else:
                meta[key] = val.strip('"').strip("'")
    return meta, body


def build_frontmatter(meta: Dict[str, Any]) -> str:
    """将字典转换为 YAML frontmatter 字符串（Obsidian 兼容格式）。"""
    lines = ["---"]
    for key, val in meta.items():
        if isinstance(val, list):
            if not val:
                lines.append(f'{key}: []')
            else:
                # P1-16: 去重保持顺序，防止标签重复累积
                seen = set()
                deduped = []
                for v in val:
                    if v not in seen:
                        seen.add(v)
                        deduped.append(v)
                items = ', '.join(f'"{v}"' for v in deduped)
                lines.append(f'{key}: [{items}]')
        elif isinstance(val, bool):
            lines.append(f'{key}: {"true" if val else "false"}')
        elif isinstance(val, (int, float)):
            lines.append(f'{key}: {val}')
        else:
            # 字符串值，简单转义双引号
            s = str(val).replace('"', '\\"')
            lines.append(f'{key}: "{s}"')
    lines.append("---")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# 文本处理工具
# ─────────────────────────────────────────────

def _tokenize(text: str) -> List[str]:
    """分词：提取中文词组（2字以上）和英文单词、数字。"""
    tokens = []
    # 中文字符串（连续2字以上）
    for m in re.finditer(r"[\u4e00-\u9fff]{2,}", text):
        word = m.group()
        for size in (2, 3, 4):
            for i in range(len(word) - size + 1):
                tokens.append(word[i : i + size])
    # 英文单词
    for m in re.finditer(r"[a-zA-Z_][a-zA-Z0-9_]{1,}", text):
        tokens.append(m.group().lower())
    # 数字
    for m in re.finditer(r"\d+\.?\d*", text):
        tokens.append(m.group())
    return [t for t in tokens if t not in _STOPWORDS and len(t) >= 2]


def _chunk_document(text: str, max_chars: int = 500) -> List[Dict[str, str]]:
    """将文档按段落分块，每块不超过 max_chars 字符。"""
    chunks = []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    current_text = ""
    current_idx = 0

    for para in paragraphs:
        if len(current_text) + len(para) + 2 <= max_chars:
            current_text += para + "\n\n"
        else:
            if current_text:
                chunks.append({"id": f"chunk_{current_idx}", "text": current_text.strip()})
                current_idx += 1
            current_text = para + "\n\n"

    if current_text:
        chunks.append({"id": f"chunk_{current_idx}", "text": current_text.strip()})

    return chunks


def _compute_idf(doc_count: int, term_doc_freq: Dict[str, int]) -> Dict[str, float]:
    idf = {}
    for term, freq in term_doc_freq.items():
        idf[term] = math.log(doc_count / (freq + 1)) + 1
    return idf


def _safe_filename(name: str) -> str:
    """将概念名转换为安全的文件名（保留中文）。"""
    # 移除危险字符，但保留中文
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name).strip()
    return safe if safe else "untitled"


# ─────────────────────────────────────────────
# 自检
# ─────────────────────────────────────────────

def _self_check() -> bool:
    """自检：验证 tokenize/chunk/IDF/frontmatter 解析等文本工具。

    使用临时目录隔离，测试核心功能的正确性。
    """
    import tempfile

    print("=" * 50)
    print("◐ kb_text 自检")
    print("=" * 50)

    passed = 0
    total = 0
    tmp_dir = tempfile.mkdtemp(prefix="kb_text_test_")

    try:
        # [1/5] 分词：中文词组 + 英文单词
        total += 1
        tokens = _tokenize("固体高次谐波产生 HHG")
        has_cjk = any("高次" in t or "固体" in t for t in tokens)
        has_en = "hhg" in tokens
        if has_cjk and has_en:
            passed += 1
            print(f"  [1/{total}] ✓ 分词: 中文+英文 (tokens={len(tokens)})")
        else:
            print(f"  [1/{total}] ✗ 分词: has_cjk={has_cjk}, has_en={has_en}")

        # [2/5] 文档分块
        total += 1
        long_text = "段落一内容。\n\n段落二内容。\n\n段落三内容。"
        chunks = _chunk_document(long_text, max_chars=20)
        if len(chunks) >= 2 and all("text" in c and "id" in c for c in chunks):
            passed += 1
            print(f"  [2/{total}] ✓ 分块: {len(chunks)} 块")
        else:
            print(f"  [2/{total}] ✗ 分块: chunks={len(chunks)}")

        # [3/5] IDF 计算
        total += 1
        idf = _compute_idf(10, {"激光": 2, "相位": 5})
        if isinstance(idf, dict) and "激光" in idf and idf["激光"] > idf["相位"]:
            passed += 1
            print(f"  [3/{total}] ✓ IDF: 低频词权重更高 (激光={idf['激光']:.2f}, 相位={idf['相位']:.2f})")
        else:
            print(f"  [3/{total}] ✗ IDF: idf={idf}")

        # [4/5] frontmatter 解析
        total += 1
        fm_text = '---\ntitle: "测试"\ntags: ["HHG", "固体"]\nconfidence: 0.8\ngrowth_stage: "mature"\n---\n正文内容'
        fm, body = parse_frontmatter(fm_text)
        if (fm.get("title") == "测试" and fm.get("confidence") == 0.8
                and fm.get("growth_stage") == "mature" and "正文" in body):
            passed += 1
            print(f"  [4/{total}] ✓ frontmatter 解析: title={fm['title']}, tags={fm.get('tags')}")
        else:
            print(f"  [4/{total}] ✗ frontmatter 解析: fm={fm}")

        # [5/5] frontmatter 生成（往返一致性）
        total += 1
        meta = {"title": "往返测试", "tags": ["a", "b"], "confidence": True}
        built = build_frontmatter(meta)
        fm2, _ = parse_frontmatter(built + "\n正文")
        if fm2.get("title") == "往返测试" and fm2.get("tags") == ["a", "b"] and fm2.get("confidence") is True:
            passed += 1
            print(f"  [5/{total}] ✓ frontmatter 往返: 标签去重+类型保持")
        else:
            print(f"  [5/{total}] ✗ frontmatter 往返: fm2={fm2}")
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    ok = passed == total
    print(f"\n{'✓' if ok else '✗'} kb_text: {passed}/{total} 通过")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_check() else 1)
