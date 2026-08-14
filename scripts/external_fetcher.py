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
import logging
import math
import os
import re
import shutil
import string
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import now_utc as _now_utc

_log = logging.getLogger(__name__)

from paths import PROJECT_ROOT, KNOWLEDGE_DIR, RAW_DIR
CACHE_DIR = KNOWLEDGE_DIR / ".cache"
CACHE_DIR_ARXIV = CACHE_DIR / "arxiv"
CACHE_DIR_WIKI = CACHE_DIR / "wikipedia"
CACHE_DIR_ACADEMIC = CACHE_DIR / "academic"
RAW_INDEX_PATH = CACHE_DIR / "raw-index.json"
RAW_QUEUE_PATH = CACHE_DIR / "raw-pending-queue.json"

# ---------------------------------------------------------------------------
# 多源学术检索配置（v6.8.42）
#   - OpenAlex  ：2026-02 起 usage-based，无 key 每天约 $0.10 demo 预算（约 100 次 search）
#                 免费 key（openalex.org/settings/api）每天 $1 免费额度（约 1000 次 search）
#   - Semantic Scholar：无 key 1 req/s（共享 IP 常 429），免费 key 大幅提升
#   - 优先从项目 .env 读取 OPENALEX_API_KEY / SEMANTIC_SCHOLAR_API_KEY，缺失则匿名降级
# ---------------------------------------------------------------------------
_ACADEMIC_MAILTO = "linsai-copilot@localhost"
_OPENALEX_API = "https://api.openalex.org/works"
_CROSSREF_API = "https://api.crossref.org/works"
_S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"
_PUBMED_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
_DEFAULT_HTTP_TIMEOUT = 15

# deepxiv CLI 路径（优先使用 venv 中的安装）
_DEEPXIV_PATH = shutil.which("deepxiv") or str(Path.home() / ".venv" / "bin" / "deepxiv")

# Wikipedia API
_WIKI_API_URL = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
_WIKI_TIMEOUT = 5
_WIKI_RETRIES = 1


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

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
    CACHE_DIR_ACADEMIC.mkdir(parents=True, exist_ok=True)  # v6.8.42: 多源学术检索缓存


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
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        pass  # 容错：缓存损坏时返回默认值
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
    except OSError:
        return ""  # 容错：文件不可读时返回空
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

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"⚠ deepxiv 返回非 JSON: {result.stdout[:100]}", file=sys.stderr)
            return []
        papers = data.get("result", [])
        if not papers:
            # 尝试 trending 作为 fallback
            return _fetch_arxiv_trending(max_results)

        normalized = []
        for p in papers:
            # v6.8.42 修复：deepxiv 返回 authors 元素类型不一致（dict/str 混排），
            # 原实现 a.get("name") 遇 str 直接异常 → 整个 arXiv 检索静默返回空
            authors = []
            for a in p.get("authors", []) or []:
                if isinstance(a, dict):
                    nm = a.get("name", "")
                elif isinstance(a, str):
                    nm = a.strip()
                else:
                    nm = str(a)
                if nm:
                    authors.append(nm)
            normalized.append({
                "source": "arxiv",
                "arxiv_id": p.get("arxiv_id", ""),
                "title": p.get("title", ""),
                "authors": authors,
                "abstract": p.get("abstract", ""),
                "tldr": p.get("tldr", ""),
                "url": p.get("url", ""),
                "date": p.get("date", ""),
                "citation_count": p.get("citation_count", 0),
                "score": p.get("score", 0.0),
                "venue": p.get("venue", ""),
                "year": 0,
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
    except Exception as e:
        _log.debug("arXiv 检索失败: %s", e)
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

    except Exception as e:
        _log.debug("arXiv 论文获取失败: %s", e)
        return None


# ---------------------------------------------------------------------------
# 多源学术检索（v6.8.42）— OpenAlex / Semantic Scholar / PubMed / Crossref
#   用于丰富论文来源：deepxiv 仅覆盖 arXiv 预印本，
#   OpenAlex（240M+ works，含期刊）与 Crossref（DOI 元数据）补充正式出版物。
# ---------------------------------------------------------------------------

def _load_academic_api_keys() -> Dict[str, str]:
    """从项目 .env 读取学术 API key（缺失返回空字符串，不影响降级运行）。

    支持的环境变量：
      OPENALEX_API_KEY           OpenAlex 免费 key（openalex.org/settings/api）
      SEMANTIC_SCHOLAR_API_KEY   Semantic Scholar 免费 key
    """
    keys: Dict[str, str] = {}
    env_map = {
        "OPENALEX_API_KEY": os.environ.get("OPENALEX_API_KEY", ""),
        "SEMANTIC_SCHOLAR_API_KEY": os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""),
    }
    # 兜底：从项目 .env 读取（复用 llm_router 的解析器，不引入第三方依赖）
    try:
        from llm_router import load_env_file
        env_data = load_env_file(PROJECT_ROOT / ".env") or {}
    except Exception:
        env_data = {}
    for var, val in env_map.items():
        if val:
            keys[var] = val.strip()
        elif env_data.get(var):
            keys[var] = str(env_data[var]).strip()
    return keys


_SSL_CONTEXT = None  # 模块级缓存，避免每次请求重建

def _make_ssl_context():
    """构建可用 SSL 上下文（沙箱 Python 默认 CA 路径常失效）。

    依次尝试：env SSL_CERT_FILE → /etc/ssl/cert.pem → homebrew openssl → 默认。
    全部失败时回退无验证（仅用于只读学术元数据抓取），并记录警告。
    """
    global _SSL_CONTEXT
    if _SSL_CONTEXT is not None:
        return _SSL_CONTEXT
    import ssl
    candidates = [
        os.environ.get("SSL_CERT_FILE", ""),
        "/etc/ssl/cert.pem",
        "/etc/ssl/certs/ca-certificates.crt",
        "/opt/homebrew/etc/openssl@3/cert.pem",
        "/usr/local/etc/openssl@3/cert.pem",
    ]
    for cafile in candidates:
        if cafile and os.path.exists(cafile):
            try:
                ctx = ssl.create_default_context(cafile=cafile)
                _SSL_CONTEXT = ctx
                return ctx
            except (ssl.SSLError, OSError):
                continue
    try:
        ctx = ssl.create_default_context()
        _SSL_CONTEXT = ctx
        return ctx
    except (ssl.SSLError, OSError):
        pass
    _log.warning("未找到可用 CA 证书，学术检索 HTTPS 降级为无验证模式（仅只读元数据抓取）")
    _SSL_CONTEXT = ssl._create_unverified_context()
    return _SSL_CONTEXT


def _http_get_json(url: str, timeout: int = _DEFAULT_HTTP_TIMEOUT,
                   retries: int = 2, sleep_base: float = 1.5) -> Optional[Any]:
    """通用 HTTP GET + JSON 解析，带轻量重试（429/5xx 退避）。"""
    headers = {
        "User-Agent": "LinSai-CoPilot/1.0 (academic search; mailto:%s)" % _ACADEMIC_MAILTO,
        "Accept": "application/json",
    }
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=_make_ssl_context()) as resp:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(sleep_base * (2 ** attempt))
                continue
            _log.debug("HTTP %s: %s", e.code, url[:120])
            return None
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
            if attempt < retries:
                time.sleep(sleep_base)
                continue
            _log.debug("请求失败: %s (%s)", url[:120], e)
            return None
    return None


def _openalex_reconstruct_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> str:
    """重建 OpenAlex 摘要（倒排索引 → 纯文本）。"""
    if not inverted_index:
        return ""
    try:
        positions: Dict[int, str] = {}
        for word, idxs in inverted_index.items():
            for i in idxs:
                positions[i] = word
        if not positions:
            return ""
        return " ".join(positions[i] for i in sorted(positions))
    except Exception:
        return ""


def _openalex_extract_arxiv_id(work: Dict[str, Any]) -> str:
    """从 OpenAlex work 的 locations 中提取 arXiv ID（若有）。"""
    for loc in work.get("locations") or []:
        url = loc.get("landing_page_url") or ""
        m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}|[a-z\-]+/\d{7})", url)
        if m:
            return m.group(1)
    return ""


def fetch_openalex(query: str, max_results: int = 5,
                   api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """OpenAlex 学术检索：240M+ works（期刊论文 + 预印本 + 会议）。

    无需 key 即可使用（demo 预算）；配置 OPENALEX_API_KEY 后额度提升 10 倍。
    结果含 DOI、作者、期刊、年份、引用数、摘要（倒排索引重建）。
    """
    cache_path = CACHE_DIR_ACADEMIC / f"openalex_{_cache_key(query)}_{max_results}.json"
    cached = _load_cache(cache_path, ttl_hours=24)
    if cached is not None:
        return cached

    if api_key is None:
        api_key = _load_academic_api_keys().get("OPENALEX_API_KEY", "")

    params = {
        "search": query,
        "per_page": str(max_results),
        "mailto": _ACADEMIC_MAILTO,
        "select": (
            "id,doi,title,display_name,publication_year,publication_date,"
            "cited_by_count,type,authorships,abstract_inverted_index,"
            "primary_location,locations,open_access"
        ),
    }
    if api_key:
        params["api_key"] = api_key
    url = _OPENALEX_API + "?" + urllib.parse.urlencode(params)

    data = _http_get_json(url)
    if not data or not isinstance(data, dict):
        print(f"⚠ OpenAlex 检索失败（可能无 key 或已达额度）: {query}", file=sys.stderr)
        return []

    normalized = []
    for w in data.get("results", [])[:max_results]:
        authors = []
        for a in w.get("authorships") or []:
            nm = (a.get("author") or {}).get("display_name", "")
            if nm:
                authors.append(nm)
        venue = ""
        pl = w.get("primary_location") or {}
        src = pl.get("source") or {}
        # 期刊名优先，preprint repository 标记为 arXiv
        venue = src.get("display_name", "") or ""
        arxiv_id = _openalex_extract_arxiv_id(w)
        date = w.get("publication_date") or ""
        if not date and w.get("publication_year"):
            date = f"{w['publication_year']}-01-01"
        # 统一主 URL：优先 arXiv / OA 链接，否则 OpenAlex 详情页
        url_main = f"https://openalex.org/{w.get('id','').rsplit('/',1)[-1]}" if w.get("id") else ""
        oa = w.get("open_access") or {}
        if arxiv_id:
            url_main = f"https://arxiv.org/abs/{arxiv_id}"
        elif oa.get("oa_url"):
            url_main = oa["oa_url"]
        normalized.append({
            "source": "openalex",
            "arxiv_id": arxiv_id,
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "title": w.get("display_name") or w.get("title") or "",
            "authors": authors,
            "abstract": _openalex_reconstruct_abstract(w.get("abstract_inverted_index")),
            "tldr": "",
            "url": url_main,
            "date": date,
            "citation_count": w.get("cited_by_count") or 0,
            "score": 0.0,
            "venue": venue,
            "year": w.get("publication_year") or 0,
        })

    _save_cache(cache_path, normalized)
    return normalized


def fetch_semantic_scholar(query: str, max_results: int = 5,
                           api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Semantic Scholar 学术检索（可选源）。

    无 key 时 1 req/s（共享 IP 易 429，会自动跳过）；配置 SEMANTIC_SCHOLAR_API_KEY
    后限流大幅提升。提供 TLDR（一句话摘要）与引用数。
    """
    cache_path = CACHE_DIR_ACADEMIC / f"s2_{_cache_key(query)}_{max_results}.json"
    cached = _load_cache(cache_path, ttl_hours=24)
    if cached is not None:
        return cached

    if api_key is None:
        api_key = _load_academic_api_keys().get("SEMANTIC_SCHOLAR_API_KEY", "")

    params = {
        "query": query,
        "limit": str(max_results),
        "fields": "title,year,authors,abstract,citationCount,externalIds,url,venue,publicationDate",
    }
    url = _S2_API + "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "LinSai-CoPilot/1.0"}
    if api_key:
        headers["x-api-key"] = api_key

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=_DEFAULT_HTTP_TIMEOUT, context=_make_ssl_context()) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"⚠ Semantic Scholar 限流（429），跳过该源: {query}", file=sys.stderr)
            return []
        _log.debug("S2 HTTP %s: %s", e.code, query)
        return []
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        _log.debug("S2 请求失败: %s", e)
        return []

    if not data:
        return []
    normalized = []
    for p in data.get("data") or []:
        ext = p.get("externalIds") or {}
        arxiv_id = ""
        aurl = ext.get("ArXiv", "")
        m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})", aurl)
        if m:
            arxiv_id = m.group(1)
        year = p.get("year") or 0
        if not year and p.get("publicationDate"):
            try:
                year = int(p["publicationDate"][:4])
            except (ValueError, TypeError):
                year = 0
        normalized.append({
            "source": "semantic_scholar",
            "arxiv_id": arxiv_id,
            "doi": (ext.get("DOI") or "").replace("https://doi.org/", ""),
            "title": p.get("title") or "",
            "authors": [a.get("name", "") for a in p.get("authors") or []],
            "abstract": p.get("abstract") or "",
            "tldr": "",  # S2 tldr 需要独立端点，略过
            "url": p.get("url") or "",
            "date": p.get("publicationDate") or "",
            "citation_count": p.get("citationCount") or 0,
            "score": 0.0,
            "venue": p.get("venue") or "",
            "year": year,
        })

    _save_cache(cache_path, normalized)
    return normalized


def fetch_pubmed(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """PubMed E-utilities 检索（可选通用兜底，生物医学文献）。

    物理领域覆盖有限，但可作为跨学科兜底。不需要 key，3 req/s 限制。
    """
    cache_path = CACHE_DIR_ACADEMIC / f"pubmed_{_cache_key(query)}_{max_results}.json"
    cached = _load_cache(cache_path, ttl_hours=24)
    if cached is not None:
        return cached

    esearch = (
        f"{_PUBMED_EUTILS}/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}"
        f"&retmode=json&retmax={max_results}&sort=relevance"
    )
    data = _http_get_json(esearch, retries=1)
    if not data:
        return []
    idlist = (data.get("esearchresult") or {}).get("idlist") or []
    if not idlist:
        return []

    # esummary 批量拉取元数据
    ids = ",".join(idlist)
    esummary = f"{_PUBMED_EUTILS}/esummary.fcgi?db=pubmed&id={ids}&retmode=json"
    sdata = _http_get_json(esummary, retries=1)
    if not sdata:
        return []

    result = sdata.get("result") or {}
    normalized = []
    for pmid in idlist:
        it = result.get(pmid)
        if not it:
            continue
        doi = ""
        eloc = it.get("elocationid") or ""
        for ident in it.get("articleids") or []:
            if ident.get("idtype") == "doi":
                doi = ident.get("value", "")
        pubdate = it.get("pubdate") or ""
        year = 0
        m = re.match(r"(\d{4})", pubdate or "")
        if m:
            year = int(m.group(1))
        authors = [a.get("name", "") for a in (it.get("authors") or [])][:20]
        normalized.append({
            "source": "pubmed",
            "arxiv_id": "",
            "doi": doi,
            "title": it.get("title") or "",
            "authors": authors,
            "abstract": "",
            "tldr": "",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "date": pubdate,
            "citation_count": 0,
            "score": 0.0,
            "venue": it.get("fulljournalname") or it.get("source") or "",
            "year": year,
        })

    _save_cache(cache_path, normalized)
    return normalized


def fetch_crossref_doi(doi: str) -> Optional[Dict[str, Any]]:
    """Crossref DOI → 权威元数据补全（期刊论文）。

    注意：Crossref 关键词搜索相关性差（常返回书章节/SI 附件），
    因此仅用作「已知 DOI 的元数据补全」，不作为发现源。
    """
    if not doi:
        return None
    clean = doi.strip().replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
    url = f"{_CROSSREF_API}/{urllib.parse.quote(clean, safe='')}"
    data = _http_get_json(url, retries=2)
    if not data or data.get("status") != "ok":
        return None
    msg = data.get("message") or {}
    title = (msg.get("title") or [""])[0]
    journal = (msg.get("container-title") or [""])[0]
    authors = []
    for a in msg.get("author") or []:
        name = " ".join([a.get("given", ""), a.get("family", "")]).strip()
        if name:
            authors.append(name)
    date_parts = (msg.get("published") or msg.get("issued") or {}).get("date-parts") or [[]]
    year = (date_parts[0] or [0])[0] or 0
    return {
        "source": "crossref",
        "arxiv_id": "",
        "doi": clean,
        "title": title,
        "authors": authors,
        "abstract": "",
        "tldr": "",
        "url": f"https://doi.org/{clean}",
        "date": "-".join(str(x) for x in (date_parts[0] or [])),
        "citation_count": msg.get("is-referenced-by-count") or 0,
        "score": 0.0,
        "venue": journal,
        "year": year,
    }


def search_academic(query: str, max_results: int = 5,
                    sources: Tuple[str, ...] = ("arxiv", "openalex")) -> List[Dict[str, Any]]:
    """多源学术论文检索聚合：顺序查询各源，按 DOI/arXiv ID 去重合并。

    用例：
      - 默认链：deepxiv(arXiv) + OpenAlex（期刊+预印本互补）
      - 扩展链：可加 semantic_scholar / pubmed
    任一来源失败（限流/超时/无结果）不影响其它来源。

    Returns:
        合并去重后的论文列表，按 citation_count 降序，每项带 source 标签。
    """
    results: Dict[str, Dict[str, Any]] = {}
    seen_keys: set = set()

    def _merge(items: List[Dict[str, Any]]) -> None:
        for p in items:
            key = ""
            if p.get("doi"):
                key = f"doi:{p['doi']}"
            elif p.get("arxiv_id"):
                key = f"arxiv:{p['arxiv_id']}"
            else:
                key = f"title:{_cache_key(p.get('title', ''))}"
            if key in seen_keys:
                # 已有来源保留，仅补充缺失的 DOI/abstract 等字段
                existing = results.get(key)
                if existing:
                    for f in ("doi", "abstract", "venue", "year"):
                        if not existing.get(f) and p.get(f):
                            existing[f] = p[f]
                continue
            seen_keys.add(key)
            results[key] = p

    if "arxiv" in sources:
        _merge(fetch_arxiv(query, max_results=max_results))

    if "openalex" in sources:
        _merge(fetch_openalex(query, max_results=max_results))

    if "semantic_scholar" in sources:
        _merge(fetch_semantic_scholar(query, max_results=max_results))

    if "pubmed" in sources:
        _merge(fetch_pubmed(query, max_results=max_results))

    merged = list(results.values())
    merged.sort(key=lambda x: (x.get("citation_count") or 0), reverse=True)
    return merged[:max_results * 2]


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
                except Exception as e:
                    _log.debug("deepxiv wsearch 单次失败: %s", e)
                    continue
        return []
    except Exception as e:
        _log.debug("deepxiv wsearch 失败: %s", e)
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
    except Exception as e:
        _log.debug("DuckDuckGo 检索失败: %s", e)
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
        except Exception as e:
            _log.debug("Wikipedia 获取失败: %s", e)
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


# 兼容接口：learning_engine.py 仍在调用，保留供 Wikipedia 词条蒸馏使用
def fetch_wikipedia(title: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """获取 Wikipedia 词条摘要（封装 _fetch_wikipedia_fallback，标记 source）。

    learning_engine.py 的概念蒸馏流程调用此接口获取百科释义。
    如需多源联网检索，请使用 fetch_web_search()。
    """
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
        except (json.JSONDecodeError, OSError):
            pass  # 容错：文件损坏时返回默认值

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
            except (OSError, AttributeError):
                continue  # 容错：文件不可访问时跳过

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
        except (json.JSONDecodeError, OSError):
            pass  # 容错：文件损坏时返回默认值
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
        import knowledge_base as kb
        if hasattr(kb, "search_light"):
            results = kb.search_light(title, top_k=1)
            results = results.get("results", []) if isinstance(results, dict) else results
            if results:
                max_sim = results[0].get("score", 0)
                novelty = max(0.0, 1.0 - max_sim)
    except Exception as e:
        _log.debug("知识库相似度检测失败: %s", e)

    # 3. 可靠性：来源权重
    reliability_map = {
        "arxiv": 0.9,
        "openalex": 0.85,       # v6.8.42: 开放学术目录（期刊+预印本）
        "crossref": 0.9,        # v6.8.42: DOI 注册机构，元数据权威
        "pubmed": 0.85,         # v6.8.42: NCBI 生物医学
        "semantic_scholar": 0.85,  # v6.8.42
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
        sources: 来源列表（None 表示全部）
                支持：arxiv / openalex / semantic_scholar / pubmed /
                      web / wikipedia / raw（v6.8.42 起新增 3 个学术源）

    Returns:
        排序后的候选列表
    """
    if sources is None:
        sources = ["arxiv", "openalex", "wikipedia", "raw"]

    # 获取研究方向关键词
    try:
        from research_profiler import get_research_keywords
        research_keywords = get_research_keywords(top_k=10)
    except Exception as e:
        _log.debug("研究方向关键词获取失败: %s", e)
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

    # v6.8.42: 补充学术来源（期刊论文 / 多学科覆盖）
    if "openalex" in sources:
        candidates.extend(fetch_openalex(query, max_results=max_results))

    if "semantic_scholar" in sources:
        candidates.extend(fetch_semantic_scholar(query, max_results=max_results))

    if "pubmed" in sources:
        candidates.extend(fetch_pubmed(query, max_results=max_results))

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

    print("\n[4/8] 测试 fetch_openalex（多源学术检索 v6.8.42）...")
    oa_papers = fetch_openalex("high harmonic generation solid", max_results=3)
    print(f"   返回论文数: {len(oa_papers)}")
    if oa_papers:
        p0 = oa_papers[0]
        print(f"   第一篇: {p0.get('title', 'N/A')[:50]}")
        print(f"   年份={p0.get('year')} 引文={p0.get('citation_count')} 期刊={p0.get('venue','')[:30]} DOI={p0.get('doi')}")
        assert p0.get("source") == "openalex"
        assert "authors" in p0
    else:
        print("   ⚠ OpenAlex 获取失败（可能网络或额度问题）")
    print("   ✓ OpenAlex 获取测试完成")

    print("\n[5/8] 测试 fetch_semantic_scholar...")
    s2_papers = fetch_semantic_scholar("high harmonic generation", max_results=2)
    print(f"   返回论文数: {len(s2_papers)}")
    if s2_papers:
        assert s2_papers[0].get("source") == "semantic_scholar"
    else:
        print("   ⚠ S2 无返回（无 key 时可能 429，属预期降级）")
    print("   ✓ S2 获取测试完成")

    print("\n[6/8] 测试 search_academic 聚合去重...")
    merged = search_academic("solid state high harmonic generation", max_results=3,
                             sources=("arxiv", "openalex"))
    print(f"   聚合论文数: {len(merged)}")
    for m in merged[:3]:
        print(f"   - [{m.get('source')}] {m.get('title','')[:45]} (DOI={m.get('doi')})")
    if merged:
        assert all(m.get("source") in ("arxiv", "openalex") for m in merged)
    print("   ✓ 聚合搜索通过")

    print("\n[7/8] 测试 scan_raw_changes...")
    changes = scan_raw_changes()
    print(f"   新增: {len(changes['added'])}, 修改: {len(changes['modified'])}, 删除: {len(changes['deleted'])}")
    assert "scanned_at" in changes
    print("   ✓ Raw 扫描通过")

    print("\n[8/8] 测试 score_opportunity...")
    from datetime import timedelta as _td
    time_30d = _td(days=10)
    sample = {
        "source": "arxiv",
        "title": "Attosecond spectroscopy of solid-state HHG",
        "abstract": "We investigate high harmonic generation in solids using attosecond pulses.",
        # 用相对日期避免断言漂移（v6.8.42）
        "date": (datetime.now(timezone.utc).replace(tzinfo=None) - time_30d).strftime("%Y-%m-%d"),
    }
    score = score_opportunity(sample, [("attosecond", 0.9), ("HHG", 0.8), ("solid-state", 0.7)])
    print(f"   评分: {score}")
    assert 0 <= score["overall"] <= 1
    assert score["reliability"] == 0.9  # arXiv
    assert score["timeliness"] == 1.0   # 近30天
    oa_score = score_opportunity({**sample, "source": "openalex"}, [("attosecond", 0.9)])
    assert oa_score["reliability"] == 0.85  # OpenAlex 权重
    print("   来源权重: openalex=0.85 已生效")
    print("   ✓ 评分通过")

    print("\n[9/9] 测试 discover_learning_opportunities（含新学术源）...")
    ops = discover_learning_opportunities(query="quantum", max_results=2, sources=["arxiv", "openalex"])
    print(f"   发现机会数: {len(ops)}")
    if ops:
        print(f"   最高分: {ops[0].get('_score', {}).get('overall', 0)}")
    print("   ✓ 统一发现接口通过")

    print("\n" + "=" * 50)
    print("✓ 所有自检项目通过")
    print("=" * 50)
