#!/usr/bin/env python3
"""共享容错 JSON 提取器（v7.3.57，目标判据 G2-C 后续批次·统一收敛）。

背景（memory/goals/2026-11-05-双目标判据.md G2-C 后续项 + 11-07 实测）：
    周末输入链 deep_digest 单批 8 篇败 2 篇（2026-11-07 00:26/00:29）——
    LLM 返回围栏 JSON，中文值内含未转义 ASCII 引号（"Expecting ',' delimiter"
    落在中文字符串中段）。此前各消费点各自实现围栏解析，健壮度不一：
    weekend input 有 brace 切片降级，idea_generator / knowledge_output ×2
    仅围栏正则（非贪婪 + 无修复通道）。本模块统一收敛四消费点为同一
    提取链，并补确定性修复通道。

提取链（逐级降级，全部确定性、零 LLM）：
    1. 预处理：剥 <think> 块、剥开头围栏（含无闭合截断形态）
    2. 围栏块正则提取
    3. 字符串态感知平衡扫描——取首个完整顶层 {…} / […]（兼容前后言/尾注，
       优于旧"首个 { 到最后一个 }"切片：尾注含 } 时旧切片必败）
    4. json.loads 直解
    5. 修复通道（仅在上一步失败后启用，保证内容零篡改的最好努力）：
       a. CJK 邻接内引号转义——值内裸 ASCII `"` 若后继非结构字符则视为
          字符串内部引号补 `\\` 转义（今晚实测失败类的确定性修复）
       b. 去尾逗号 `,` 后紧跟 `}` / `]`
    6. 全败 → (None, 原因描述)，由调用方自行记录原始响应

内容完整性纪律：修复只动 JSON 结构字符（引号转义/逗号删除），不改写
任何字符串内容字符；测试含内容完整性断言。

用法：
    from llm_json_lib import extract_json
    value, reason = extract_json(text)
    if value is None:
        log(f"解析失败: {reason}")  # 调用方自行落账原始响应片段
"""

from __future__ import annotations

import json
import re
from typing import Any, List, Optional, Tuple

# CJK 统一表意文字 + CJK 标点 + 全角形态（引号邻接判定的"内容字符"域）
_CJK_CHAR_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")
# 结构后继字符：合法闭引号之后只可能跟这些（或下一个 key 的开引号 / 结尾）
_STRUCT_AFTER = set(':,}]')
_THINK_RE = re.compile(r"<think>[\s\S]*?</think>", re.IGNORECASE)
_LEAD_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*\n?", re.IGNORECASE)
_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def _strip_think_and_fence(text: str) -> str:
    """剥 think 块与开头围栏（含 v6.10.9 的无闭合截断形态）。"""
    t = _THINK_RE.sub("", text or "")
    return _LEAD_FENCE_RE.sub("", t.strip())


def _balanced_scan(s: str) -> Optional[str]:
    """字符串态感知平衡扫描：返回首个完整顶层 {…} / […] 子串。

    与旧"首个 { 到最后一个 }"切片的差异：正文 JSON 后带含 } 的尾注时
    旧切片产生的子串 json.loads 必败，本扫描按栈深度精确闭合。
    截断（无闭合）时返回 None（修复通道无法补全缺失内容）。
    """
    start = -1
    open_char = ""
    depth = 0
    in_str = False
    esc = False
    for i, ch in enumerate(s):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"' and start >= 0:
            in_str = True
            continue
        if ch in "{[":
            if start < 0:
                start, open_char, depth = i, ch, 1
            else:
                if open_char == "{" and ch == "[" or open_char == "[" and ch == "{":
                    # 顶层类型不同的嵌套开口：按当前栈统一计数
                    pass
                depth += 1
        elif ch in "}]":
            if start < 0:
                continue
            depth -= 1
            if depth == 0:
                return s[start:i + 1]
    return None


def _escape_inner_cjk_quotes(s: str) -> str:
    """值内裸 ASCII 引号转义：闭引号判定 = 后继非空字符 ∈ {':', ',', '}', ']',
    '"'}（后者 = 紧跟下一 key/value 的开引号）或到尾；否则视为字符串内部
    引号补 `\\`。CJK 邻接仅作辅助判定信号（后继为 CJK 内容字符必为内引号），
    非 CJK 后继也按同一结构规则处理（"ATI" saddle 类内引号同样受益）。
    """
    chars = list(s)
    n = len(chars)
    out: List[str] = []
    i = 0
    in_str = False
    while i < n:
        ch = chars[i]
        if in_str and ch == "\\" and i + 1 < n:
            out.append(ch)
            out.append(chars[i + 1])
            i += 2
            continue
        if ch == '"':
            if not in_str:
                in_str = True
                out.append(ch)
                i += 1
                continue
            j = i + 1
            while j < n and chars[j] in " \t\r\n":
                j += 1
            nxt = chars[j] if j < n else ""
            if nxt == "" or nxt in _STRUCT_AFTER or nxt == '"':
                in_str = False
                out.append(ch)
            else:
                out.append("\\")
                out.append('"')
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _try_loads(s: str) -> Optional[Any]:
    """loads + 两级修复重试（尾逗号 → CJK 内引号）。全败返回 None。"""
    try:
        return json.loads(s)
    except Exception:
        pass
    # 修复 1：尾逗号
    try:
        return json.loads(_TRAILING_COMMA_RE.sub(r"\1", s))
    except Exception:
        pass
    # 修复 2：CJK 邻接内引号转义（今晚实测失败类），转义后再过一次尾逗号
    try:
        return json.loads(_TRAILING_COMMA_RE.sub(r"\1", _escape_inner_cjk_quotes(s)))
    except Exception:
        return None


def extract_json(text: str) -> Tuple[Optional[Any], str]:
    """从 LLM 响应文本提取 JSON 值。

    Returns:
        (value, "") 成功；(None, 原因) 全链失败——调用方负责落账原始响应。
    """
    if not text or not text.strip():
        return None, "空响应"
    stripped = _strip_think_and_fence(text)

    # 候选串：围栏块内容优先，其次剥围栏后全文
    candidates: List[str] = []
    m = _FENCE_RE.search(stripped)
    if m:
        candidates.append(m.group(1))
    candidates.append(stripped)

    for cand in candidates:
        v = _try_loads(cand)
        if v is not None:
            return v, ""
        # 平衡扫描子串（处理前言/尾注包裹），扫描后再走一遍修复链
        bal = _balanced_scan(cand)
        if bal and bal != cand:
            v = _try_loads(bal)
            if v is not None:
                return v, ""
    return None, "围栏/平衡扫描/修复链均未产出可解析 JSON"


def _self_check() -> bool:
    """自检：八类实测失败形态 + 内容完整性。"""
    ok = True

    def _eq(actual, expected, name):
        nonlocal ok
        good = actual == expected
        ok &= good
        print(("✓ " if good else "✗ ") + name)

    # 1. 常规围栏
    v, r = extract_json('```json\n{"a": 1}\n```')
    _eq((v, r), ({"a": 1}, ""), "常规围栏")
    # 2. 开头围栏无闭合（截断形态）
    v, r = extract_json('```json\n{"a": 1}')
    _eq(v, {"a": 1}, "开头围栏无闭合")
    # 3. 中文前言包裹（无围栏）
    v, r = extract_json('以下是分析结果：\n{"core": "测试", "n": 2}\n以上。')
    _eq(v, {"core": "测试", "n": 2}, "前言/尾注包裹")
    # 4. 今晚实测失败类：中文值内未转义引号
    raw = '```json\n{\n  "core": "该文提出"时空涡旋"方案，系统揭示耦合规律",\n  "n": 1\n}\n```'
    v, r = extract_json(raw)
    _eq(v, {"core": "该文提出\"时空涡旋\"方案，系统揭示耦合规律", "n": 1}, "CJK 内引号修复（今晚失败类）")
    # 5. 内容完整性：修复不改写字符串内容字符
    _eq((v or {}).get("core", ""), "该文提出\"时空涡旋\"方案，系统揭示耦合规律", "修复后内容逐字一致")
    # 6. 尾逗号
    v, r = extract_json('{"a": [1, 2, 3,]}')
    _eq(v, {"a": [1, 2, 3]}, "尾逗号")
    # 7. think 块包裹
    v, r = extract_json('<think>推理过程…</think>\n{"ok": true}')
    _eq(v, {"ok": True}, "think 块剥离")
    # 8. 顶层数组 + 前言
    v, r = extract_json('结果如下：\n[{"k": 1}, {"k": 2}]')
    _eq(v, [{"k": 1}, {"k": 2}], "顶层数组")
    # 9. 空响应
    v, r = extract_json("")
    _eq(v is None and r == "空响应", True, "空响应给因")
    # 10. 纯垃圾
    v, r = extract_json("这不是 JSON")
    _eq(v is None and len(r) > 0, True, "垃圾给因")
    # 11. 尾注含 } 的平衡扫描（旧切片必败形态）
    v, r = extract_json('{"a": {"b": 1}}\n注：以上 {} 为占位。')
    _eq(v, {"a": {"b": 1}}, "尾注含 } 平衡扫描")
    # 12. 截断（有 { 无闭合 }）——修复链无法补全，须给因不抛
    v, r = extract_json('```json\n{"core": "未闭合', safe=False) if False else extract_json('```json\n{"core": "未闭合')
    _eq(v is None and len(r) > 0, True, "截断给因不抛")
    print("✓ llm_json_lib 自检通过" if ok else "✗ llm_json_lib 自检失败")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if _self_check() else 1)
