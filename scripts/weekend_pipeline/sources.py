#!/usr/bin/env python3
"""来源收集与去重。"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import file_sha256, load_json, now_utc, save_json
from paths import PROJECT_ROOT

from .constants import RELIABILITY_DERIVED, RELIABILITY_RELIABLE
from .state import is_source_processed, mark_source_processed

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


# ---------------------------------------------------------------------------
# v6.9.18 方向相关性过滤
# ---------------------------------------------------------------------------

SCOPE_TERMS_PATH = PROJECT_ROOT / "memory" / "weekend-input" / "scope-terms.json"

# 种子词表（NSFC-强场超快方向核心术语，中英双语）。首跑生成
# scope-terms.json 后以文件为准，用户可手工增删。
# 背景：08-16 实测无方向过滤，6G 漏波天线/CIGS 光伏/CVD 生长等跨领域
# 论文全部进入聚类池并成簇（"智能透射面无线能量传输"与"二维纳米带
# 晶体管"同簇）。research-profile.json 的 TF-IDF 关键词被运维词污染
# （"识库/开放问题/prompt"），不可用作方向词表。
SCOPE_SEED_TERMS = [
    # 中文核心术语
    "高次谐波", "强场", "超快", "阿秒", "非线性光学", "极紫外", "太赫兹",
    "二维材料", "拓扑", "能谷", "谷极化", "莫尔", "扭转", "压缩光", "量子光",
    "贝里相位", "缀饰", "电离", "隧穿", "相干", "飞秒", "皮秒", "瞬态",
    "光谱学", "电子动力学", "含时密度泛函", "反铁磁", "交变磁", "铁电",
    "激子", "自旋", "超冷", "量子几何", "手性", "层析",
    # 英文核心术语
    "hhg", "high harmonic", "strong field", "attosecond",
    "ultrafast", "femtosecond", "nonlinear optic", "xuv", "extreme ultraviolet",
    "terahertz", "thz", "2d material", "two-dimensional", "topological",
    "valley", "moire", "twisted bilayer", "squeezed light", "squeezed vacuum",
    "berry phase", "berry curvature", "floquet", "ionization", "tunneling",
    "quantum light", "tddft", "electron dynamics", "altermagnet", "wigner",
    # v6.9.18 回放补充（08-16 真实数据误杀修正）：
    "quantum geometry", "quantum geometric", "quantum spin hall", "spin hall",
    "single-cycle", "few-cycle", "carrier-envelope", "orbital angular momentum",
    "tomography", "fieldoscopy", "petahertz", "frequency comb", "spectral comb",
    "x-ray laser", "soft x-ray", "plasmon", "exciton", "magnon", "chirality",
    "spatially resolved", "time-resolved",
]

# 词表自动补充时排除的课题标题通用词
_SCOPE_STOPWORDS = {
    "general", "major", "key", "the", "and", "with", "for", "from", "using",
    "driven", "based", "probe", "readout", "optical", "inversion",
}

# v6.9.22: 核心范式词表——"强场超快光学"的两条研究范式标志词。
# 背景：08-16 注册的 berry-mnps3 课题跑偏（纯准静态凝聚态：第一性
# 原理 + 滑移工程器件化，无任何强场/超快维度），用户指示纠偏方向：
# 这一族课题要么通过强场实现操控，要么用 HHG/超快光谱实现超快测量。
# 旧方向关只查宽词表（"自旋/能谷/激子"单命中即过），材料/物态词
# 与范式词不分层，导致纯静态凝聚态簇可开新课题。修复：new 路由
# 门槛强制命中本表（merge/expansion 注入现有课题不受影响——材料
# 语境词仍由 SCOPE_SEED_TERMS 宽表覆盖采集与挂载场景）。
CORE_THEME_TERMS = [
    # —— 范式 A：强场操控（光场作为超快旋钮）——
    "强场", "超强激光", "强激光", "太赫兹", "thz", "terahertz",
    "floquet", "缀饰", "载波包络", "carrier-envelope", "电离", "ionization",
    "隧穿", "tunneling", "波形", "waveform", "petahertz",
    "single-cycle", "few-cycle", "sub-cycle", "亚周期",
    # —— 范式 B：HHG/超快光谱测量（谱学作为超快探针）——
    "高次谐波", "谐波产生", "hhg", "high harmonic", "harmonic generation",
    "超快", "ultrafast", "阿秒", "attosecond", "飞秒", "femtosecond",
    "皮秒", "picosecond", "瞬态", "transient", "泵浦", "pump-probe", "pump probe",
    "时间分辨", "time-resolved", "超快光谱", "瞬态吸收", "transient absorption",
    "瞬态反射", "fieldoscopy", "极紫外", "xuv", "extreme ultraviolet",
]


# v7.3.62：核心范式判定前的窄剥离——编辑注与准静态"瞬态"短语。
# 背景（2026-11-07 跨域过滤审计实测）：
#   ① 量化金融簇 M1/M5 的摘要末尾带编辑注"注意：本文为量化金融方向…
#      与强场超快光学无物理内容上的关联"/"（注：…与强场超快光学主题
#      无直接关联…）"，注记本身含"强场/超快/瞬态"，会把自己判成核心
#      范式成员（误命中）；
#   ② 半导体缺陷簇的 "Deep-Level Transient Spectroscopy"/"DLTS" 是
#      准静态电学瞬态，被 '瞬态/transient' 词条误命中。
# 剥离只认"注：/注意：/编辑注："前缀（括注或句首句），以及 DLTS 固定
# 短语；正文里的物理括注（如"带隙约 1.1 eV"）不在剥离范围内。
_EDITORIAL_NOTE_PAREN = re.compile(
    r"[（(]\s*(?:编辑)?注\s*[：:][^）)]*[）)]"
)
_EDITORIAL_NOTE_SENT = re.compile(
    r"(?:^|[。；\n])\s*(?:编辑注|注意|注)\s*[：:][^。\n]*。?"
)
_QUASI_STATIC_TRANSIENT = re.compile(
    r"deep[-\s]*level\s+transient\s+spectroscop(?:y|ies)|dlts|"
    r"深能级瞬态谱(?:学)?|深能级瞬态光谱",
    re.I,
)


def _strip_editorial_notes(text: str) -> str:
    """剥离编辑注与准静态瞬态短语（仅 core_theme_hit 判定前使用）。"""
    if not text:
        return text
    cleaned = _EDITORIAL_NOTE_PAREN.sub(" ", text)
    cleaned = _EDITORIAL_NOTE_SENT.sub("。", cleaned)
    cleaned = _QUASI_STATIC_TRANSIENT.sub(" ", cleaned)
    return cleaned


def core_theme_hit(text: str) -> Optional[str]:
    """检查文本是否命中核心范式词（强场操控或 HHG/超快光谱测量）。

    v6.9.22 新增：与 scope_hit（宽词表，采集过滤用）分层——本函数
    是 new 路由的硬门槛，仅命中材料/物态语境词（自旋/能谷/激子等）
    不算对齐核心主题。匹配归一化逻辑与 scope_hit 一致（连字符归一、
    左词界 + 后缀延展、中英子串）。

    v7.3.62：判定前剥离编辑注与 DLTS 类准静态"瞬态"短语，防注记
    自命中（详见 _strip_editorial_notes）。
    """
    return scope_hit(_strip_editorial_notes(text), CORE_THEME_TERMS)


def load_scope_terms(persist: bool = True) -> List[str]:
    """加载方向词表（文件优先；不存在则从种子词生成并落盘）。

    词表持久化在 memory/weekend-input/scope-terms.json，用户可手工编辑
    调整口径；文件存在即以文件为准（不再自动重建，防止覆盖人工调整）。
    persist=False 供 dry-run 使用：只生成不落盘（零落盘不变式）。

    v6.9.22: 移除"从活跃课题标题自动补词"——该机制是同义反复漂移
    引擎（课题标题词进词表 → 新簇命中这些词算方向相关 → 注册新课题
    → 新课题标题再扩词表），方向会越漂越宽且永不可逆（文件为准语义
    下污染词永久 baked in）。方向扩张只应通过人工编辑词表或升级
    SCOPE_SEED_TERMS 实现。
    """
    if SCOPE_TERMS_PATH.exists():
        data = load_json(SCOPE_TERMS_PATH, default={})
        terms = data.get("terms") or []
        if terms:
            return [str(t).lower() for t in terms]

    terms = [t.lower() for t in SCOPE_SEED_TERMS if t]

    if persist:
        SCOPE_TERMS_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_json(SCOPE_TERMS_PATH, {
            "terms": terms,
            "generated_at": now_utc(),
            "source": "seed",
            "note": "方向相关性过滤词表，可手工增删；文件存在即以此为准",
        })
    return terms


def scope_hit(text: str, terms: Optional[List[str]] = None) -> Optional[str]:
    """检查文本是否命中方向词表，返回命中词（未命中返回 None）。

    匹配口径（08-16 真实数据回放标定）：
    - 连字符归一：'high-harmonic' 与词表 'high harmonic' 等价（实测
      核心论文 'solid-state high-harmonic generation' 因连字符被误杀）；
    - 英文单词（无空格）：左词界 + 允许后缀延展——'altermagnet' 命中
      'altermagnetism'、'topological' 命中 'topologically'；
    - 英文短语（含空格）/中文：子串匹配。
    """
    if not text:
        return None
    terms = terms or load_scope_terms()
    lowered = re.sub(r"[-–—]", " ", text.lower())
    for term in terms:
        if not term:
            continue
        term_norm = re.sub(r"[-–—]", " ", term.lower()).strip()
        if not term_norm:
            continue
        if re.search(r"[a-z]", term_norm):
            if " " in term_norm:
                if term_norm in lowered:
                    return term
            elif re.search(rf"\b{re.escape(term_norm)}", lowered):
                return term
        elif term_norm in lowered:
            return term
    return None


# v6.9.18 运维简报识别：标题/正文命中且无论文条目的简报不是学术内容
_OPS_BRIEFING_MARKERS = (
    "空记录", "cron 自动运行", "个人知识库运维", "流水线运维", "文献追踪流水线运维",
)


def _is_ops_briefing(title: str, text: str) -> bool:
    """识别运维性简报（08-16 实测其聚成 8 成员簇污染输入链）。

    判据（满足其一）：① 正文过短（空简报）；② 标题命中运维标记；
    ③ 正文头部命中运维标记且全文无 arXiv 编号（正常学术简报列论文）。
    """
    if len(text or "") < 300:
        return True
    title = title or ""
    if any(m in title for m in _OPS_BRIEFING_MARKERS):
        return True
    if any(m in (text or "")[:600] for m in _OPS_BRIEFING_MARKERS):
        if "arxiv" not in (text or "").lower():
            return True
    return False


BRIEFING_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "reviews"
CAPTURES_DIR = PROJECT_ROOT / "knowledge" / "captures"
REFERENCES_NOTES_DIR = PROJECT_ROOT / "references" / "notes"
RAW_PAPERS_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"

# v6.8.13: Hermes workspace 文献来源路径
HERMES_WORKSPACE = Path.home() / "Desktop" / "hermes_workspace"
HERMES_BRIEFINGS_DIR = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings"
HERMES_BRIEFINGS_PAPERS_DIR = HERMES_BRIEFINGS_DIR / "papers"


def _read_text(path: Path, max_chars: int = 8000) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except Exception:
        return ""


def _file_mtime_iso(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    except Exception:
        return ""


# v6.9.12: 源质量分层（聚类提炼的质量来源设计）
SOURCE_TIER_PAPER = 1       # 学术一手文献（raw papers + hermes papers）
SOURCE_TIER_BRIEFING = 2    # 每日精选简报（二手但已筛选）
SOURCE_TIER_CAPTURE = 3     # 讨论捕获（背景上下文）
SOURCE_TIER_NOTE = 3        # 手工笔记（背景上下文）


def distilled_paper_ids() -> set:
    """已提炼论文 id 集合（wiki/papers 页的 arxiv_id / 文件 stem）。

    v6.9.12: 知识已蒸馏成 wiki 页的 raw 论文不再作为聚类源。
    判据：knowledge/wiki/papers/*.md frontmatter 的 arxiv_id 字段
    或页文件名 stem。实测 wiki 页 326 个（含 arxiv_id 直标）。
    """
    ids: set = set()
    wiki_papers_dir = PROJECT_ROOT / "knowledge" / "wiki" / "papers"
    if not wiki_papers_dir.exists():
        return ids
    for f in wiki_papers_dir.glob("*.md"):
        ids.add(f.stem)
        try:
            head = f.read_text(encoding="utf-8")[:800]
            for line in head.split("\n"):
                if line.startswith("arxiv_id:"):
                    val = line.split(":", 1)[1].strip().strip('"\'')
                    if val:
                        ids.add(val)
                    break
        except Exception:
            continue
    return ids


def _make_source_id(prefix: str, path: Path) -> str:
    return f"{prefix}:{path.relative_to(PROJECT_ROOT)}"


def _backlog_exempt(sid: str, text: str, state: Optional[Dict[str, Any]]) -> bool:
    """v6.9.11: 补课豁免——来源从未被处理过时豁免时间窗口/数量上限。

    背景：v6.7.7-v6.9.10 的"收集即标记"缺陷给大量文献打上虚假的
    已处理标记（实际从未摘要）。修复删除标记后，这些积压文献的
    文件 mtime 已老化，会被 7 天窗口/mtime 前 N 上限挡在收集之外，
    "恢复未处理"也轮不到消费。待处理语义应由标记决定而非文件
    新鲜度：未处理的全收（补课），已处理的按原窗口过滤。
    """
    if state is None:
        return False
    return not is_source_processed(sid, text, state)


def collect_briefings(
    days: int = 7,
    state: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """收集最近 N 天的文献简报。

    v6.8.13: 三路读取——CoPilot wiki/reviews + hermes_briefings + hermes papers。
    v6.9.11: 窗口外文件若从未处理过（无标记）则豁免窗口收进（补课），
    已处理过的旧文件仍跳过。
    """
    cutoff = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)
    sources = []
    seen_ids = set()

    def _in_window_or_backlog(f: Path, sid: str, text: str) -> bool:
        """窗口内直接放行；窗口外仅放行未处理过的（补课）。"""
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        except Exception:
            return True
        if mtime >= cutoff:
            return True
        return _backlog_exempt(sid, text, state)

    # 路径 A：CoPilot wiki/reviews（同步后的简报）
    for f in sorted(BRIEFING_DIR.glob("briefing-*.md"), reverse=True):
        text = _read_text(f, 6000)
        if not text:
            continue
        sid = _make_source_id("briefing", f)
        if not _in_window_or_backlog(f, sid, text):
            continue
        seen_ids.add(sid)
        sources.append({
            "source_id": sid,
            "type": "briefing",
            "path": str(f.relative_to(PROJECT_ROOT)),
            "text": text,
            "mtime": _file_mtime_iso(f),
            "reliability": RELIABILITY_RELIABLE,
        })

    # 路径 B：hermes workspace briefings/research_briefing_*.md（每日精选简报）
    if HERMES_BRIEFINGS_DIR.exists():
        for f in sorted(HERMES_BRIEFINGS_DIR.glob("research_briefing_*.md"), reverse=True):
            text = _read_text(f, 6000)
            if not text:
                continue
            sid = f"hermes_briefing:{f.name}"
            if sid in seen_ids:
                continue
            if not _in_window_or_backlog(f, sid, text):
                continue
            seen_ids.add(sid)
            sources.append({
                "source_id": sid,
                "type": "briefing",
                "path": str(f),
                "text": text,
                "mtime": _file_mtime_iso(f),
                "reliability": RELIABILITY_RELIABLE,
            })

    return sources


def collect_paper_pool(
    limit: int = 20,
    state: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """收集文献池中的新增论文。

    v6.8.13: 从 knowledge/raw/papers/ 的 frontmatter 读取（取代空的 paper-pool.json）。
    v6.8.14: 同时从 hermes workspace papers/ 读取补充。
    v6.9.11: mtime 前 N 上限仅约束已处理论文；未处理过的（无标记）
    全量收进（补课）——旧实现按 mtime 倒序截断，池中较旧的一半
    待处理论文永远排不进前 N，恢复未处理标记后也轮不到摘要。
    """
    sources = []
    seen_ids = set()
    admitted_processed = 0  # 已处理论文的收纳计数（受 limit 约束）

    def _admit(f: Path) -> bool:
        """v6.9.11: 未处理的全收（补课）；已处理的最多 limit 条。"""
        nonlocal admitted_processed
        arxiv_id = f.stem
        sid = f"paper:{arxiv_id}"
        text_probe = _read_text(f, 2000)
        if _backlog_exempt(sid, text_probe, state):
            return True
        if admitted_processed >= limit:
            return False
        admitted_processed += 1
        return True

    # 路径 A：CoPilot knowledge/raw/papers/*.md（YAML frontmatter）
    if RAW_PAPERS_DIR.exists():
        for f in sorted(RAW_PAPERS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
            if not _admit(f):
                continue
            try:
                text = _read_text(f, 1500)
                # 提取 frontmatter 中的标题和摘要
                title = ""
                abstract = ""
                if text.startswith("---"):
                    end = text.find("---", 3)
                    if end > 0:
                        fm = text[3:end].strip()
                        for line in fm.split("\n"):
                            if line.startswith("title:"):
                                title = line.split(":", 1)[1].strip().strip('"\'')
                            elif line.startswith("abstract:"):
                                abstract = line.split(":", 1)[1].strip().strip('"\'')

                arxiv_id = f.stem
                sid = f"paper:{arxiv_id}"
                seen_ids.add(sid)
                body_text = f"{title}\n\n{abstract}" if abstract else text
                sources.append({
                    "source_id": sid,
                    "type": "paper",
                    "path": str(f.relative_to(PROJECT_ROOT)),
                    "arxiv_id": arxiv_id,
                    "title": title or arxiv_id,
                    "abstract": abstract[:800],
                    "text": body_text[:2000],
                    "reliability": RELIABILITY_RELIABLE,
                })
            except Exception:
                continue

    # 路径 B：hermes workspace papers/*.md（补充来源）
    if HERMES_BRIEFINGS_PAPERS_DIR.exists():
        for f in sorted(HERMES_BRIEFINGS_PAPERS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
            if not _admit(f):
                continue
            arxiv_id = f.stem
            sid = f"paper:{arxiv_id}"
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            text = _read_text(f, 2000)
            if text and len(text) > 100:
                sources.append({
                    "source_id": sid,
                    "type": "paper",
                    "path": str(f),
                    "arxiv_id": arxiv_id,
                    "title": arxiv_id,
                    "abstract": text[:800],
                    "text": text[:2000],
                    "reliability": RELIABILITY_DERIVED,
                })

    return sources


def collect_captures(limit: int = 10) -> List[Dict[str, Any]]:
    """收集归档讨论。"""
    sources = []
    if not CAPTURES_DIR.exists():
        return sources
    for f in sorted(CAPTURES_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        text = _read_text(f, 3000)
        if text:
            sources.append({
                "source_id": _make_source_id("capture", f),
                "type": "capture",
                "path": str(f.relative_to(PROJECT_ROOT)),
                "text": text,
                "mtime": _file_mtime_iso(f),
                "reliability": RELIABILITY_RELIABLE,
            })
    return sources


def collect_reference_notes() -> List[Dict[str, Any]]:
    """收集用户参考笔记。"""
    sources = []
    if not REFERENCES_NOTES_DIR.exists():
        return sources
    for f in REFERENCES_NOTES_DIR.glob("*.md"):
        text = _read_text(f, 3000)
        if text:
            sources.append({
                "source_id": _make_source_id("reference", f),
                "type": "reference_note",
                "path": str(f.relative_to(PROJECT_ROOT)),
                "text": text,
                "mtime": _file_mtime_iso(f),
                "reliability": RELIABILITY_RELIABLE,
            })
    return sources


def collect_kb_concepts_and_methods(
    state: Optional[Dict[str, Any]] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """从 Knowledge Base 拉取现有 concepts/methods/papers。

    优先读取 reliable/derived 的 wiki 页面，避免重复处理已收录内容。
    """
    result: Dict[str, List[Dict[str, Any]]] = {
        "concepts": [],
        "methods": [],
        "papers": [],
    }
    try:
        import knowledge_base as kb
    except Exception:
        if _log:
            _log.warning("无法导入 knowledge_base，跳过 KB 来源收集")
        return result

    try:
        pages = kb.list_wiki_pages()
    except Exception as e:
        if _log:
            _log.warning(f"list_wiki_pages 失败: {e}")
        return result

    for page in pages:
        wiki_type = page.get("type", "")
        path = page.get("path", "")
        title = page.get("title", "")
        if wiki_type not in result:
            continue
        # 优先加载可靠/派生页面，unverified 跳过
        try:
            full = kb.get_wiki_page(path)
            fm = full.get("frontmatter", {}) if full else {}
            reliability = fm.get("source_reliability", RELIABILITY_DERIVED)
            if reliability == RELIABILITY_RELIABLE or reliability == RELIABILITY_DERIVED:
                body = (full.get("body", "") if full else "")[:1500]
                source = {
                    "source_id": f"kb:{wiki_type}:{path}",
                    "type": f"kb_{wiki_type}",
                    "path": path,
                    "title": title,
                    "text": body,
                    "reliability": reliability,
                }
                # 去重：若已处理过同样 hash 则跳过
                if state is None or not is_source_processed(source["source_id"], source["text"], state):
                    result[wiki_type].append(source)
        except Exception:
            continue

    return result


def collect_all_sources(
    state: Optional[Dict[str, Any]] = None,
    days: int = 7,
    paper_limit: int = 20,
    capture_limit: int = 10,
    persist_scope: bool = True,
) -> Dict[str, Any]:
    """统一收集所有来源并返回结构化结果。

    v6.9.10: papers/briefings/captures/reference_notes 不再在收集时预标记
    为已处理。旧版"收集即标记"使 summarize 的 new_paper_sources 过滤恒为
    空——输入端自 v6.7.7 上线起从未真正摘要过新料，ideas 连续全零。
    标记职责归还消费方（summarize 摘要成功后才 mark，见 input_jobs）。
    kb 类来源保留标记：gap_analysis 依赖 processed_sources 中的
    kb:concept 记录作为知识库概念输入，且 collect_kb_concepts_and_methods
    靠它去重跳过已收录页面。

    v6.9.12 源甄别（聚类提炼的质量来源）：
    1. 已提炼排除——knowledge/wiki/papers/ 中已有同 arxiv_id 提炼页的
       raw 论文不再作为聚类源（其知识已升华进 wiki，重复聚类纯冗余；
       wiki 页可带 used_by_proposals 直接关联课题）。排除在 collect
       层完成，不消耗 summarize 的 LLM 名额。
    2. 质量分层 tier——paper=1（学术一手）/ briefing=2（二手精选）/
       capture=3 / note=3（讨论与手工笔记）。tier ≤2 进聚类主源
       （new_paper_sources 口径不变），tier=3 仅作 gap 上下文。
    3. v6.9.18 方向/运维过滤——paper 与方向词表（scope-terms.json）
       零交集的跨领域论文跳过（08-16 实测 6G 天线/CIGS 光伏等成乱簇）；
       briefing 命中运维特征（空记录/cron 运维且无论文条目）跳过
       （08-16 实测运维简报聚成 8 成员簇）。
    """
    sources: Dict[str, Any] = {
        "briefings": collect_briefings(days=days, state=state),
        "papers": collect_paper_pool(limit=paper_limit, state=state),
        "captures": collect_captures(limit=capture_limit),
        "reference_notes": collect_reference_notes(),
        "kb": collect_kb_concepts_and_methods(state=state),
        "collected_at": now_utc(),
    }

    # v6.9.12: 已提炼排除 + tier 标注
    # v6.9.18: 方向过滤（paper）+ 运维简报过滤（briefing）——见函数
    # docstring 第 3 点
    distilled = distilled_paper_ids()
    scope_terms = load_scope_terms(persist=persist_scope)
    kept_papers = []
    excluded = 0
    out_of_scope = 0
    for s in sources.get("papers", []):
        if s.get("source_id", "").split(":")[-1] in distilled:
            excluded += 1
            continue
        probe = " ".join([s.get("title", ""), s.get("abstract", "") or s.get("text", "")])
        if scope_hit(probe, scope_terms) is None:
            out_of_scope += 1
            continue
        s["tier"] = SOURCE_TIER_PAPER
        kept_papers.append(s)
    sources["papers"] = kept_papers
    sources["distilled_excluded"] = excluded
    sources["out_of_scope"] = out_of_scope
    kept_briefings = []
    ops_skipped = 0
    for s in sources.get("briefings", []):
        if _is_ops_briefing(s.get("path", ""), s.get("text", "")):
            ops_skipped += 1
            continue
        s["tier"] = SOURCE_TIER_BRIEFING
        kept_briefings.append(s)
    sources["briefings"] = kept_briefings
    sources["ops_briefings_skipped"] = ops_skipped
    for s in sources.get("captures", []):
        s["tier"] = SOURCE_TIER_CAPTURE
    for s in sources.get("reference_notes", []):
        s["tier"] = SOURCE_TIER_NOTE

    if state is not None:
        for wiki_type, items in sources.get("kb", {}).items():
            for s in items:
                if not is_source_processed(s["source_id"], s["text"], state):
                    mark_source_processed(s["source_id"], s["text"], state)

    return sources


def new_paper_sources(sources: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从已收集来源中过滤出尚未处理的新论文/简报。"""
    new_sources = []
    for s in sources.get("papers", []) + sources.get("briefings", []):
        if not is_source_processed(s["source_id"], s["text"], state):
            new_sources.append(s)
    return new_sources


def search_kb_for_query(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """在 KB 中检索与查询相关的页面。"""
    try:
        import knowledge_base as kb
    except Exception:
        return []

    try:
        results = kb.search(query, top_k=top_k, source="wiki")
    except Exception:
        return []

    enriched = []
    for r in results:
        try:
            page = kb.get_wiki_page(r.get("path", ""))
            if page:
                enriched.append({
                    "path": r.get("path", ""),
                    "title": r.get("title", ""),
                    "score": r.get("score", 0.0),
                    "body": page.get("body", "")[:1500],
                })
            else:
                enriched.append(r)
        except Exception:
            enriched.append(r)
    return enriched


def list_kb_paper_pages() -> List[Dict[str, Any]]:
    """列出 KB 中已有的 paper 类型页面。"""
    try:
        import knowledge_base as kb
    except Exception:
        return []

    try:
        return kb.list_wiki_pages(wiki_type="paper")
    except Exception:
        return []
