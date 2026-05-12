#!/usr/bin/env python3
"""
external_fetcher.py — 外部信息获取与本地资源扫描

用途：
    封装 arXiv（deepxiv CLI）、Wikipedia API、本地 raw/ 扫描，
    为自主学习引擎提供统一的信息发现接口。

用法示例：
    >>> from external_fetcher import fetch_arxiv, fetch_wikipedia, scan_raw_changes
    >>> papers = fetch_arxiv("quantum optics", max_results=3)
    >>> wiki = fetch_wikipedia("Attosecond")
    >>> changes = scan_raw_changes()
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
RAW_DIR = KNOWLEDGE_DIR / "raw"
CACHE_DIR = KNOWLEDGE_DIR / ".cache"
CACHE_DIR_ARXIV = CACHE_DIR / "arxiv"
CACHE_DIR_WIKI = CACHE_DIR / "wikipedia"
RAW_INDEX_PATH = CACHE_DIR / "raw-index.json"
RAW_QUEUE_PATH = CACHE_DIR / "raw-pending-queue.json"

# deepxiv CLI 路径（优先使用 venv 中的安装）
_DEEPXIV_PATH = shutil.which("deepxiv") or str(Path.home() / ".venv" / "bin" / "deepxiv")

# Wikipedia API
_WIKI_API_URL = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
_WIKI_TIMEOUT = 5
_WIKI_RETRIES = 1


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_date(date_str: str) -> Optional[datetime]:
    """解析日期字符串。"""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(date_str[:len(fmt.replace("%", "00"))], fmt)
        except ValueError:
            continue
    return None


def _ensure_cache_dirs() -> None:
    CACHE_DIR_ARXIV.mkdir(parents=True, exist_ok=True)
    CACHE_DIR_WIKI.mkdir(parents=True, exist_ok=True)


def _cache_key(query: str) -> str:
    """生成缓存文件名。"""
    return hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]


def _load_cache(cache_path: Path, ttl_hours: int) -> Optional[Any]:
    """加载缓存，TTL 过期返回 None。"""
    if not cache_path.exists():
        return None
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        cached_at = data.get("_cached_at", "")
        if cached_at:
            cached_dt = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
            age_hours = (datetime.now(timezone.utc) - cached_dt).total_seconds() / 3600
            if age_hours <= ttl_hours:
                return data.get("result")
    except Exception:
        pass
    return None


def _save_cache(cache_path: Path, result: Any) -> None:
    """保存缓存。"""
    _ensure_cache_dirs()
    cache_path.write_text(
        json.dumps({"_cached_at": _now_utc(), "result": result}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _file_sha256(fpath: Path) -> str:
    """计算文件 sha256。"""
    h = hashlib.sha256()
    try:
        h.update(fpath.read_bytes())
    except Exception:
        return ""
    return h.hexdigest()


# ---------------------------------------------------------------------------
# arXiv 获取（deepxiv CLI）
# ---------------------------------------------------------------------------

def fetch_arxiv(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """通过 deepxiv CLI 搜索 arXiv 论文。

    Args:
        query: 搜索关键词
        max_results: 最大返回数

    Returns:
        论文列表，每项含 arxiv_id, title, authors, abstract, tldr, url, date, citation_count
    """
    cache_path = CACHE_DIR_ARXIV / f"{_cache_key(query)}_{max_results}.json"
    cached = _load_cache(cache_path, ttl_hours=24)
    if cached is not None:
        return cached

    # 检查 deepxiv 是否可用
    if not Path(_DEEPXIV_PATH).exists() and not shutil.which("deepxiv"):
        print(f"⚠ deepxiv CLI 未安装，跳过 arXiv 搜索: {query}", file=sys.stderr)
        return []

    cmd = [_DEEPXIV_PATH, "search", query, "--limit", str(max_results), "--format", "json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"⚠ deepxiv search 失败: {result.stderr[:200]}", file=sys.stderr)
            return []

        data = json.loads(result.stdout)
        papers = data.get("result", [])
        if not papers:
            # 尝试 trending 作为 fallback
            return _fetch_arxiv_trending(max_results)

        normalized = []
        for p in papers:
            normalized.append({
                "source": "arxiv",
                "arxiv_id": p.get("arxiv_id", ""),
                "title": p.get("title", ""),
                "authors": [a.get("name", "") for a in p.get("authors", [])],
                "abstract": p.get("abstract", ""),
                "tldr": p.get("tldr", ""),
                "url": p.get("url", ""),
                "date": p.get("date", ""),
                "citation_count": p.get("citation_count", 0),
                "score": p.get("score", 0.0),
            })

        _save_cache(cache_path, normalized)
        return normalized

    except subprocess.TimeoutExpired:
        print(f"⚠ deepxiv search 超时: {query}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"⚠ deepxiv JSON 解析失败: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"⚠ deepxiv search 异常: {e}", file=sys.stderr)
        return []


def _fetch_arxiv_trending(max_results: int = 5) -> List[Dict[str, Any]]:
    """获取 trending 论文作为 fallback。"""
    cache_path = CACHE_DIR_ARXIV / f"trending_{max_results}.json"
    cached = _load_cache(cache_path, ttl_hours=24)
    if cached is not None:
        return cached

    cmd = [_DEEPXIV_PATH, "trending", "--limit", str(max_results)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return []

        # 解析文本输出提取 arXiv ID
        ids = re.findall(r"arXiv:(\d+\.\d+)", result.stdout)
        papers = []
        for arxiv_id in ids[:max_results]:
            p = fetch_arxiv_paper(arxiv_id)
            if p:
                papers.append(p)

        _save_cache(cache_path, papers)
        return papers
    except Exception:
        return []


def fetch_arxiv_paper(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """获取单篇 arXiv 论文详情（deepxiv paper --brief）。"""
    cache_path = CACHE_DIR_ARXIV / f"paper_{arxiv_id}.json"
    cached = _load_cache(cache_path, ttl_hours=168)  # 7天缓存
    if cached is not None:
        return cached

    cmd = [_DEEPXIV_PATH, "paper", arxiv_id, "--brief"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return None

        text = result.stdout
        # 解析文本输出
        title_match = re.search(r"📄\s*(.+)", text)
        title = title_match.group(1).strip() if title_match else ""

        date_match = re.search(r"📅\s*Published:\s*(.+)", text)
        date = date_match.group(1).strip() if date_match else ""

        cite_match = re.search(r"📊\s*Citations:\s*(\d+)", text)
        citation_count = int(cite_match.group(1)) if cite_match else 0

        url_match = re.search(r"🔗\s*PDF:\s*(\S+)", text)
        url = url_match.group(1).strip() if url_match else f"https://arxiv.org/pdf/{arxiv_id}"

        tldr_match = re.search(r"💡\s*TLDR:\s*\[research paper\]\s*(.+)", text, re.DOTALL)
        tldr = tldr_match.group(1).strip() if tldr_match else ""

        paper = {
            "source": "arxiv",
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": [],
            "abstract": "",
            "tldr": tldr,
            "url": url,
            "date": date,
            "citation_count": citation_count,
            "score": 0.0,
        }

        _save_cache(cache_path, paper)
        return paper

    except Exception:
        return None


# ---------------------------------------------------------------------------
# 联网检索（Web Search）— 多源搜索
# ---------------------------------------------------------------------------

def _fetch_deepxiv_wsearch(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """通过 deepxiv wsearch 进行联网检索。"""
    if not Path(_DEEPXIV_PATH).exists() and not shutil.which("deepxiv"):
        return []

    cmd = [_DEEPXIV_PATH, "wsearch", query]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return []

        # 解析 JSON 输出（deepxiv wsearch 在 stdout 中返回 JSON）
        lines = result.stdout.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("{"):
                try:
                    data = json.loads(line)
                    if data.get("success") and data.get("results"):
                        items = []
                        for r in data["results"][:max_results]:
                            items.append({
                                "source": "web",
                                "title": r.get("title", ""),
                                "snippet": r.get("snippet", r.get("description", "")),
                                "url": r.get("url", ""),
                                "fetched_at": _now_utc(),
                            })
                        return items
                except Exception:
                    continue
        return []
    except Exception:
        return []


def _fetch_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """通过 DuckDuckGo HTML 进行联网检索。"""
    encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        items = []
        # 解析搜索结果
        for match in re.finditer(r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>', html):
            href, title = match.groups()
            items.append({
                "source": "web",
                "title": re.sub(r"<[^>]+>", "", title).strip(),
                "snippet": "",
                "url": href,
                "fetched_at": _now_utc(),
            })
            if len(items) >= max_results:
                break
        return items
    except Exception:
        return []


def _fetch_wikipedia_fallback(title: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """Wikipedia 作为联网检索的 fallback。"""
    cache_path = CACHE_DIR_WIKI / f"{_cache_key(f'{lang}:{title}')}.json"
    cached = _load_cache(cache_path, ttl_hours=168)
    if cached is not None:
        return cached

    encoded_title = urllib.parse.quote(title.replace(" ", "_"))
    url = _WIKI_API_URL.format(lang=lang, title=encoded_title)
    req = urllib.request.Request(url, headers={"User-Agent": "LinSai-CoPilot/1.0"})

    for attempt in range(_WIKI_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=_WIKI_TIMEOUT) as resp:
                data = json.loads(resp.read())
            result = {
                "source": "web",
                "title": data.get("title", title),
                "snippet": data.get("extract", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://{lang}.wikipedia.org/wiki/{encoded_title}"),
                "fetched_at": _now_utc(),
            }
            _save_cache(cache_path, result)
            return result
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except Exception:
            pass
    return None


def fetch_web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """通用联网检索接口：多源搜索，自动降级。

    搜索链：
      1. deepxiv wsearch
      2. DuckDuckGo HTML
      3. Wikipedia fallback（仅取 top-1 概念）

    Returns:
        搜索结果列表，每项含 source, title, snippet, url, fetched_at
    """
    cache_path = CACHE_DIR / ".cache" / "web" / f"{_cache_key(query)}_{max_results}.json"
    cached = _load_cache(cache_path, ttl_hours=24)
    if cached is not None:
        return cached

    results = []

    # 1. deepxiv wsearch
    results = _fetch_deepxiv_wsearch(query, max_results)
    if results:
        _save_cache(cache_path, results)
        return results

    # 2. DuckDuckGo HTML
    results = _fetch_duckduckgo(query, max_results)
    if results:
        _save_cache(cache_path, results)
        return results

    # 3. Wikipedia fallback（仅对单概念查询）
    if " " not in query.strip():
        wiki = _fetch_wikipedia_fallback(query, lang="en")
        if wiki:
            results = [wiki]
            _save_cache(cache_path, results)
            return results

    return []


# 保留旧接口以兼容
def fetch_wikipedia(title: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """【已弃用】请使用 fetch_web_search()。保留此接口以兼容现有代码。"""
    result = _fetch_wikipedia_fallback(title, lang)
    if result:
        result["source"] = "wikipedia"
    return result


# ---------------------------------------------------------------------------
# 本地 raw 扫描
# ---------------------------------------------------------------------------

def scan_raw_changes() -> Dict[str, Any]:
    """扫描 raw/ 目录，检测新增/修改/删除的文件。

    Returns:
        {
            "added": [{path, name, category, size, mtime, sha256}],
            "modified": [...],
            "deleted": [...],
            "unchanged": [...],
            "scanned_at": "2026-05-12T10:00:00Z"
        }
    """
    old_index: Dict[str, Dict[str, Any]] = {}
    if RAW_INDEX_PATH.exists():
        try:
            old_index = json.loads(RAW_INDEX_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    current: Dict[str, Dict[str, Any]] = {}
    if RAW_DIR.exists():
        for fpath in sorted(RAW_DIR.rglob("*")):
            if not fpath.is_file():
                continue
            # 排除隐藏文件
            if any(p.startswith(".") or p.startswith("__") for p in fpath.parts):
                continue
            rel = str(fpath.relative_to(KNOWLEDGE_DIR))
            try:
                stat = fpath.stat()
                current[rel] = {
                    "path": rel,
                    "name": fpath.name,
                    "category": fpath.parent.name,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "sha256": _file_sha256(fpath),
                }
            except Exception:
                continue

    added = []
    modified = []
    unchanged = []
    deleted = []

    for rel, info in current.items():
        if rel not in old_index:
            added.append(info)
        elif old_index[rel].get("sha256") != info["sha256"]:
            modified.append(info)
        else:
            unchanged.append(info)

    for rel, info in old_index.items():
        if rel not in current:
            deleted.append(info)

    # 保存新索引
    _ensure_cache_dirs()
    RAW_INDEX_PATH.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "added": added,
        "modified": modified,
        "deleted": deleted,
        "unchanged": unchanged,
        "scanned_at": _now_utc(),
    }


def get_raw_pending_queue() -> List[Dict[str, Any]]:
    """获取未处理 raw 文件队列。"""
    if RAW_QUEUE_PATH.exists():
        try:
            return json.loads(RAW_QUEUE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def update_raw_pending_queue(items: List[Dict[str, Any]]) -> None:
    """更新未处理队列。"""
    _ensure_cache_dirs()
    RAW_QUEUE_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 生长机会评估器
# ---------------------------------------------------------------------------

def _cosine_similarity(vec1: Counter, vec2: Counter) -> float:
    """计算两个 Counter 的余弦相似度。"""
    keys = set(vec1.keys()) | set(vec2.keys())
    dot = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in keys)
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def score_opportunity(item: Dict[str, Any],
                       research_keywords: List[Tuple[str, float]]) -> Dict[str, Any]:
    """评估一个学习机会的优先级。

    Args:
        item: 学习材料（arXiv 论文 / Wikipedia 词条 / raw 文件）
        research_keywords: 研究方向关键词列表 [(term, weight), ...]

    Returns:
        {
            "overall": 0.72,
            "relevance": 0.65,    # 与研究方向的相关性
            "novelty": 0.80,      # 与现有知识库的差异
            "reliability": 0.90,  # 来源可信度
            "timeliness": 0.50,   # 时效性
            "details": {...}
        }
    """
    source = item.get("source", "")

    # 1. 相关性：与研究方向关键词的余弦相似度
    item_text = " ".join([
        item.get("title", ""),
        item.get("abstract", ""),
        item.get("tldr", ""),
        item.get("extract", ""),
    ])
    item_terms = Counter(re.findall(r"[a-zA-Z]+|[\u4e00-\u9fff]{2,8}", item_text.lower()))
    research_terms = Counter({k.lower(): v for k, v in research_keywords})
    relevance = _cosine_similarity(item_terms, research_terms)

    # 2. 新颖性：与现有知识库的相似度（简化版：检查标题是否已存在）
    title = item.get("title", "")
    # 尝试导入 knowledge_base 的 search 函数
    novelty = 0.8  # 默认高新颖性
    try:
        import importlib.util
        kb_path = Path(__file__).parent / "knowledge_base.py"
        if kb_path.exists():
            spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
            kb = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(kb)
            if hasattr(kb, "search_light"):
                results = kb.search_light(title, top_k=1)
                if results:
                    max_sim = results[0].get("score", 0)
                    novelty = max(0.0, 1.0 - max_sim)
    except Exception:
        pass

    # 3. 可靠性：来源权重
    reliability_map = {
        "arxiv": 0.9,
        "wikipedia": 0.7,
        "raw": 0.8,
    }
    reliability = reliability_map.get(source, 0.5)

    # 4. 时效性
    timeliness = 0.5
    date_str = item.get("date", "")
    if date_str:
        dt = _parse_date(date_str)
        if dt:
            days_ago = (datetime.now(timezone.utc) - dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt).days
            if days_ago <= 30:
                timeliness = 1.0
            elif days_ago <= 90:
                timeliness = 0.7
            else:
                timeliness = 0.5

    # 综合评分（加权）— v1.8 阶段 4 调优权重
    overall = relevance * 0.35 + novelty * 0.25 + reliability * 0.2 + timeliness * 0.2

    return {
        "overall": round(min(overall, 1.0), 3),
        "relevance": round(min(relevance, 1.0), 3),
        "novelty": round(min(novelty, 1.0), 3),
        "reliability": round(reliability, 3),
        "timeliness": round(timeliness, 3),
        "source": source,
        "title": title,
    }


def rank_opportunities(items: List[Dict[str, Any]],
                        research_keywords: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
    """对候选学习机会排序。"""
    scored = []
    for item in items:
        score = score_opportunity(item, research_keywords)
        scored.append({**item, "_score": score})

    scored.sort(key=lambda x: x["_score"]["overall"], reverse=True)
    return scored


# ---------------------------------------------------------------------------
# 统一发现接口
# ---------------------------------------------------------------------------

def discover_learning_opportunities(query: Optional[str] = None,
                                     max_results: int = 5,
                                     sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """统一发现接口：搜索网络资源 + 扫描本地 raw，返回排序后的候选列表。

    Args:
        query: 搜索关键词（None 时使用研究方向关键词）
        max_results: 每种来源的最大返回数
        sources: 来源列表 ["arxiv", "wikipedia", "raw"]（None 表示全部）

    Returns:
        排序后的候选列表
    """
    if sources is None:
        sources = ["arxiv", "wikipedia", "raw"]

    # 获取研究方向关键词
    try:
        from research_profiler import get_research_keywords
        research_keywords = get_research_keywords(top_k=10)
    except Exception:
        research_keywords = []

    # 确定搜索词
    if not query and research_keywords:
        # 取前 3 个关键词组合
        top_terms = [k[0] for k in research_keywords[:3]]
        query = " ".join(top_terms)
    if not query:
        query = "physics optics"  # 默认 fallback

    candidates = []

    if "arxiv" in sources:
        papers = fetch_arxiv(query, max_results=max_results)
        candidates.extend(papers)

    if "web" in sources:
        # 对每个研究方向关键词进行联网检索
        for term, _ in research_keywords[:3]:
            web_results = fetch_web_search(term, max_results=max_results)
            candidates.extend(web_results)

    if "raw" in sources:
        changes = scan_raw_changes()
        for info in changes.get("added", []) + changes.get("modified", []):
            candidates.append({
                "source": "raw",
                **info,
                "title": info.get("name", ""),
            })

    # 排序
    ranked = rank_opportunities(candidates, research_keywords)
    return ranked


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("◐ 开始 external_fetcher 自检")
    print("=" * 50)

    print("\n[1/6] 测试 fetch_arxiv...")
    papers = fetch_arxiv("quantum", max_results=2)
    print(f"   返回论文数: {len(papers)}")
    if papers:
        print(f"   第一篇: {papers[0].get('title', 'N/A')[:50]}")
        assert "arxiv_id" in papers[0]
        assert "title" in papers[0]
    print("   ✓ arXiv 获取通过")

    print("\n[2/6] 测试 fetch_arxiv_paper...")
    paper = fetch_arxiv_paper("2501.12345")
    if paper:
        print(f"   标题: {paper.get('title', 'N/A')[:50]}")
        assert "arxiv_id" in paper
    else:
        print("   ⚠ 单篇获取失败（可能网络问题）")
    print("   ✓ 单篇获取测试完成")

    print("\n[3/6] 测试 fetch_wikipedia...")
    wiki = fetch_wikipedia("Attosecond", lang="en")
    if wiki:
        print(f"   标题: {wiki.get('title')}")
        print(f"   摘要: {wiki.get('extract', '')[:60]}...")
        assert "extract" in wiki
    else:
        print("   ⚠ Wikipedia 获取失败（可能网络超时）")
    print("   ✓ Wikipedia 获取测试完成")

    print("\n[4/6] 测试 scan_raw_changes...")
    changes = scan_raw_changes()
    print(f"   新增: {len(changes['added'])}, 修改: {len(changes['modified'])}, 删除: {len(changes['deleted'])}")
    assert "scanned_at" in changes
    print("   ✓ Raw 扫描通过")

    print("\n[5/6] 测试 score_opportunity...")
    sample = {
        "source": "arxiv",
        "title": "Attosecond spectroscopy of solid-state HHG",
        "abstract": "We investigate high harmonic generation in solids using attosecond pulses.",
        "date": "2026-04-15",
    }
    score = score_opportunity(sample, [("attosecond", 0.9), ("HHG", 0.8), ("solid-state", 0.7)])
    print(f"   评分: {score}")
    assert 0 <= score["overall"] <= 1
    assert score["reliability"] == 0.9  # arXiv
    assert score["timeliness"] == 1.0   # 近30天
    print("   ✓ 评分通过")

    print("\n[6/6] 测试 discover_learning_opportunities...")
    ops = discover_learning_opportunities(query="quantum", max_results=2, sources=["arxiv"])
    print(f"   发现机会数: {len(ops)}")
    if ops:
        print(f"   最高分: {ops[0].get('_score', {}).get('overall', 0)}")
    print("   ✓ 统一发现接口通过")

    print("\n" + "=" * 50)
    print("✓ 所有自检项目通过")
    print("=" * 50)
