# -*- coding: utf-8 -*-
"""课题相似度（v8 A2 新颖性对照）——中文 2-gram + 词元 overlap 的确定性 Jaccard。

零 LLM：与周末输入链 topic_match 的预筛算法同族（2-gram + 关键词 overlap），
用于问题候选与既有课题的新颖性对照。阈值 0.50，≥ 阈值视为与既有课题重复。

用法示例：
    from topic_pipeline.similarity import jaccard_similarity
    score = jaccard_similarity("莫尔超晶格中的轨道磁性", ["moire 强场探测", "twist 角度依赖"])
"""
from __future__ import annotations

import re
from typing import Iterable, List, Set

# 拉丁词与 CJK 字符混排提取：拉丁按词、CJK 按字
_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9\-]*|[\u4e00-\u9fff]")


def _tokens(text: str) -> List[str]:
    return _TOKEN_RE.findall((text or "").lower())


def _bigrams(text: str) -> Set[str]:
    """中文 2-gram + 拉丁词集合（拉丁词本身即词元，不做词内 bigram）。"""
    grams: Set[str] = set()
    latin_words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{1,}", (text or "").lower())
    grams.update(w.lower() for w in latin_words)
    cjk_runs = re.findall(r"[\u4e00-\u9fff]{2,}", text or "")
    for run in cjk_runs:
        chars = list(run)
        for i in range(len(chars) - 1):
            grams.add(chars[i] + chars[i + 1])
    # 单字 CJK（被切散的情况）也计入，避免空集
    for tok in _tokens(text):
        if re.match(r"[\u4e00-\u9fff]", tok):
            grams.add(tok)
    return grams


def jaccard_similarity(text: str, others: Iterable[str]) -> float:
    """text 与一组既有文本的最大相似度（0-1）。

    Args:
        text: 候选问题文本（标题 + 一句话问题）
        others: 既有课题文本列表（标题/问题陈述）
    Returns:
        最大 Jaccard 相似度；others 为空返回 0.0
    """
    g1 = _bigrams(text)
    if not g1:
        return 0.0
    best = 0.0
    for other in others:
        g2 = _bigrams(other or "")
        if not g2:
            continue
        union = g1 | g2
        if not union:
            continue
        score = len(g1 & g2) / len(union)
        if score > best:
            best = score
    return round(best, 4)
