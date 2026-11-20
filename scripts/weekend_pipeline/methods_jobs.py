#!/usr/bin/env python3
"""方法学专题沉淀 job（v6.10.0 T3）。

链路位置：input 阶段 cluster_distill 之后、topic_match 之前（step=
methods_settle，job_id=input_methods_settle）。消费 deep_digest 每轮
产物 summaries-{date}-r{N}.json 中的 method_leads（方法名 + 一句话
新信息），按需回原文定位方法段落，融合进 knowledge/wiki/methods/
方法页——文献内容消化以简报为主源，方法学整合是消化的附加产品。

架构要点（用户裁定）：
    - 仅当简报出现方法线索时才整合；按需回原文 = 定位而非全文
      （方法名/别名/参数符号/Methods|方法|实验装置 章节标题启发式，
      取命中行前后共 2-3KB 窗口）；
    - 方法页结构化专区由程序维护（<!-- methods-settle:v1 --> 标记
      包裹），LLM 输出结构化 JSON（principle/params/boundary/works）
      由程序格式化进专区；专区外的既有正文原样保留（不删不改）；
    - LLM 不可用或失败时降级为"附录式追加"（证据日志标 fallback）；
    - 方法页同时反哺 optimizing 课题（消费端见
      proposal_lifecycle/optimize.py 的 _load_methods_reference_block）。

用法：
    # 由 weekend_pipeline.pipeline 按 (STAGE_INPUT, STEP_METHODS_SETTLE)
    # 二元组自动调度，无需手工调用；排查时可：
    python3 -m weekend_pipeline.methods_jobs --self-check

自检：
    python3 -m weekend_pipeline.methods_jobs --self-check

规范：
    - 仅使用 Python 3 标准库；JSON 输出 ensure_ascii=False, indent=2
    - dry-run 零落盘；页面写入优先走 kb_wiki 统一门面（防双
      frontmatter），门面异常时降级为 tempfile+os.replace 原子写
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import load_json, now_utc, save_json
from paths import PROJECT_ROOT

from .constants import WEEKEND_INPUT_DIR

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None


# ---------------------------------------------------------------------------
# 路径与常量
# ---------------------------------------------------------------------------

# 方法页目录（相对 knowledge/）
METHODS_WIKI_REL_DIR = "wiki/methods"

# 方法词表（可手工编辑；结构 {slug, page, aliases:[], zh:[]}）
METHODS_LEXICON_PATH = PROJECT_ROOT / "memory" / "config" / "methods-lexicon.json"

# 反哺注入开关配置（研究管线消费端 optimize.py 同源读取）
METHODS_INJECT_PATH = PROJECT_ROOT / "memory" / "config" / "methods-inject.json"

# PDF 提取文本缓存（文件名风格 0707_4192.txt，即 arxiv 点号换下划线）
TEXT_CACHE_DIR = PROJECT_ROOT / "knowledge" / "raw" / "pdfs" / "_text_cache"

# 结构化专区标记（程序维护边界，LLM 不可见不负责）
SETTLE_BLOCK_BEGIN = "<!-- methods-settle:v1 -->"
SETTLE_BLOCK_END = "<!-- /methods-settle:v1 -->"

# growth_stage 晋升门槛（按 settled 次数；需求原文的 sprout 对齐
# growth_engine 现有体系 seedling/growing/mature，避免引入第四阶段值
# 分裂 growth_engine.evaluate_promotion 的晋升链）
SETTLE_TO_GROWING = 2     # seedling → growing：settled ≥ 2 次
SETTLE_TO_MATURE = 4      # growing → mature：settled ≥ 4 次
SETTLE_MATURE_BODY_CHARS = 1500  # 或正文 >1500 字直接 mature

# confidence：一手原文证据（有 txt 窗口）时 +0.1，上限 0.9
CONFIDENCE_STEP = 0.1
CONFIDENCE_CAP = 0.9

# 每轮方法页融合上限（控 LLM 成本；同 CLUSTER_DISTILL_ROUND_CAP 风格）
METHODS_SETTLE_ROUND_CAP = 8

# 回原文定位窗口（字符，约 3KB：命中行前 1KB + 后 2KB）
TXT_WINDOW_CHARS = 3072

# 段落定位启发式：章节标题词（Methods|方法|实验装置 等）
_SECTION_HEADER_RE = re.compile(
    r"(methods?|experimental setup|experiment|numerical implementation|"
    r"计算方法|实验方法|实验装置|方法与|理论方法|数值方法)",
    re.IGNORECASE,
)

# arxiv id 模式（0707.4192 / 2506.22860）
_ARXIV_ID_RE = re.compile(r"\b(\d{4}\.\d{4,5})\b")


# ---------------------------------------------------------------------------
# 初始词表（18 个现有方法页映射 + 常见强场超快方法词新页候选）
# ---------------------------------------------------------------------------

METHOD_SEED_LEXICON: List[Dict[str, Any]] = [
    # —— 理论方法（现有页）——
    {"slug": "tdse-solver", "page": "TDSE求解器.md",
     "aliases": ["TDSE", "time-dependent Schrodinger equation", "time-dependent-schrodinger",
                 "split-operator", "Crank-Nicolson", "SAE"],
     "zh": ["含时薛定谔", "分裂算符", "单活性电子"]},
    {"slug": "unified-hamiltonian-rt-tddft", "page": "统一Hamiltonian框架的rt-TDDFT.md",
     "aliases": ["rt-TDDFT", "real-time TDDFT", "TDDFT",
                 "time-dependent density functional theory"],
     "zh": ["含时密度泛函", "实时含时密度泛函"]},
    {"slug": "salmon-williams-lax", "page": "SALMON_rt-TDDFT___Williams-Lax.md",
     "aliases": ["SALMON", "Williams-Lax", "Williams-Lax method"],
     "zh": []},
    # —— 测量技术（现有页）——
    {"slug": "rabbitt", "page": "RABBITT.md",
     "aliases": ["RABBITT", "reconstruction of attosecond beating",
                 "attosecond beating by interference"],
     "zh": ["重建阿秒拍频干涉", "阿秒拍频"]},
    {"slug": "frog-crab", "page": "FROG.md",
     "aliases": ["FROG", "FROG-CRAB", "CRAB", "frequency-resolved optical gating"],
     "zh": ["频率分辨光学门", "阿秒脉冲重建"]},
    {"slug": "vmi", "page": "VMI.md",
     "aliases": ["VMI", "velocity map imaging", "velocity-map imaging"],
     "zh": ["速度映射成像", "速度影像"]},
    {"slug": "coltrims", "page": "COLTRIMS.md",
     "aliases": ["COLTRIMS", "cold target recoil ion momentum spectroscopy",
                 "reaction microscope"],
     "zh": ["冷靶反冲离子动量谱", "反应显微境", "反应显微镜"]},
    {"slug": "transient-absorption", "page": "瞬态吸收光谱.md",
     "aliases": ["transient absorption", "transient absorption spectroscopy",
                 "ATT", "absorption transient"],
     "zh": ["瞬态吸收", "瞬态吸收谱"]},
    {"slug": "attosecond-streaking", "page": "阿秒条纹相机.md",
     "aliases": ["attosecond streaking", "streak camera", "streaking trace",
                 "attosecond streak"],
     "zh": ["阿秒条纹", "条纹相机"]},
    {"slug": "covariance-mapping", "page": "协方差映射.md",
     "aliases": ["covariance mapping", "covariance map"],
     "zh": ["协方差映射", "协方差成像"]},
    {"slug": "waveform-control", "page": "波形控制.md",
     "aliases": ["waveform control", "carrier-envelope phase", "CEP",
                 "CEP stabilization"],
     "zh": ["波形控制", "载波包络相位"]},
    {"slug": "few-cycle-cep-gating", "page": "少周期脉冲CEP门控实验.md",
     "aliases": ["few-cycle CEP gating", "CEP gating", "few-cycle pulse"],
     "zh": ["少周期", "CEP 门控"]},
    {"slug": "sub15-cycle-cep", "page": "CEP门控sub-1_5-cycle激光脉冲技术.md",
     "aliases": ["sub-1.5-cycle", "sub-1.5 cycle", "sub-cycle pulse"],
     "zh": ["亚 1.5 周期", "亚周期脉冲"]},
    {"slug": "plasma-mirror", "page": "等离子体镜面实验方案.md",
     "aliases": ["plasma mirror", "plasma mirrors", "PM gating"],
     "zh": ["等离子体镜"]},
    {"slug": "sxfel-self-seeding", "page": "SXFEL自同步技术.md",
     "aliases": ["SXFEL", "self-seeding", "soft x-ray FEL"],
     "zh": ["软 X 射线自由电子激光", "自种子"]},
    {"slug": "si3n4-compression", "page": "双20_nm_Si-nitride膜压缩电子脉冲.md",
     "aliases": ["Si-nitride", "Si3N4 membrane", "membrane compression"],
     "zh": ["氮化硅膜", "膜压缩"]},
    {"slug": "attosecond-electron-train", "page": "高电流阿秒电子脉冲列整形.md",
     "aliases": ["attosecond electron pulse train", "electron pulse shaping"],
     "zh": ["阿秒电子脉冲列", "电子脉冲整形"]},
    # —— 常见强场超快方法词（无现有页，leads ≥2 条同类时新建页）——
    {"slug": "sbe-bloch-equations", "page": "sbe-bloch-equations.md",
     "aliases": ["SBE", "semiconductor Bloch equations", "Bloch equation",
                 "optical Bloch"],
     "zh": ["布洛赫方程", "半导体布洛赫"]},
    {"slug": "tight-binding-model", "page": "tight-binding-model.md",
     "aliases": ["tight-binding", "tight binding", "TB model", "TBM"],
     "zh": ["紧束缚"]},
    {"slug": "floquet-engineering", "page": "floquet-engineering.md",
     "aliases": ["Floquet", "Floquet engineering", "Floquet theorem",
                 "Floquet state", "Floquet band"],
     "zh": ["弗洛凯", "Floquet 工程", "周期驱动调控"]},
    {"slug": "dmft", "page": "dmft.md",
     "aliases": ["DMFT", "dynamical mean-field theory",
                 "dynamical mean field theory"],
     "zh": ["动力学平均场"]},
    {"slug": "rabi-oscillation", "page": "rabi-oscillation.md",
     "aliases": ["Rabi oscillation", "Rabi frequency", "Rabi"],
     "zh": ["拉比振荡", "喇比振荡", "拉比频率"]},
    {"slug": "thz-spectroscopy", "page": "thz-spectroscopy.md",
     "aliases": ["THz spectroscopy", "terahertz spectroscopy", "THz probe",
                 "THz detection", "THz field"],
     "zh": ["太赫兹谱", "太赫兹光谱", "太赫兹探测"]},
    {"slug": "pump-probe", "page": "pump-probe.md",
     "aliases": ["pump-probe", "pump probe", "pumped-probe",
                 "transient reflectivity", "time-resolved reflectivity"],
     "zh": ["泵浦探测", "抽运探测", "泵浦-探测"]},
    {"slug": "circular-dichroism", "page": "circular-dichroism.md",
     "aliases": ["circular dichroism", "CD spectroscopy"],
     "zh": ["圆二色", "圆二色谱", "圆偏振二色"]},
    {"slug": "arpes", "page": "arpes.md",
     "aliases": ["ARPES", "angle-resolved photoemission spectroscopy"],
     "zh": ["角分辨光电子能谱"]},
    {"slug": "squid-magnetometry", "page": "squid-magnetometry.md",
     "aliases": ["SQUID", "superconducting quantum interference device",
                 "SQUID magnetometry"],
     "zh": ["超导量子干涉"]},
    {"slug": "bayesian-inference", "page": "bayesian-inference.md",
     "aliases": ["Bayesian inference", "Bayesian", "MCMC"],
     "zh": ["贝叶斯推断", "贝叶斯"]},
]


# ---------------------------------------------------------------------------
# 词表与配置加载
# ---------------------------------------------------------------------------


def load_methods_lexicon(persist: bool = True) -> List[Dict[str, Any]]:
    """加载方法词表（文件优先；不存在则从种子生成并落盘）。

    与 sources.load_scope_terms 同语义：文件存在即以文件为准（用户可
    手工增删词条，不被种子覆盖）；persist=False 供 dry-run 使用
    （零落盘不变式）。
    """
    if METHODS_LEXICON_PATH.exists():
        data = load_json(METHODS_LEXICON_PATH, default={})
        entries = data.get("entries") or []
        if entries:
            return [e for e in entries if isinstance(e, dict) and e.get("slug")]
    entries = [dict(e) for e in METHOD_SEED_LEXICON]
    if persist:
        METHODS_LEXICON_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_json(METHODS_LEXICON_PATH, {
            "entries": entries,
            "generated_at": now_utc(),
            "source": "seed",
            "note": "方法学词表：method_leads 归组到方法页的映射，可手工增删；"
                    "page 为方法页文件名（不存在且同类 leads≥2 时按该名新建页）",
        })
    return entries


def load_inject_config() -> Dict[str, Any]:
    """加载反哺注入配置（enabled/max_pages/max_chars；缺省默认开）。"""
    if METHODS_INJECT_PATH.exists():
        data = load_json(METHODS_INJECT_PATH, default={})
        return {
            "enabled": bool(data.get("enabled", True)),
            "max_pages": int(data.get("max_pages", 3) or 3),
            "max_chars": int(data.get("max_chars", 400) or 400),
        }
    return {"enabled": True, "max_pages": 3, "max_chars": 400}


# ---------------------------------------------------------------------------
# 归组（纯函数）
# ---------------------------------------------------------------------------


def _norm_term(text: str) -> str:
    """匹配归一：小写 + 连字符/破折号归一为空格。"""
    return re.sub(r"[-–—]", " ", (text or "").lower()).strip()


def _term_in_name(term: str, name: str) -> bool:
    """词条词是否命中 lead 方法名（英文左词界 + 后缀延展；中文子串）。

    与 sources.scope_hit 的单词条匹配口径一致（'altermagnet' 命中
    'altermagnetism'），但不依赖词表文件——本函数只做单词条判断。
    """
    if not term or not name:
        return False
    term_n = _norm_term(term)
    name_n = _norm_term(name)
    if not term_n or not name_n:
        return False
    if re.search(r"[a-z]", term_n):
        if " " in term_n:
            return term_n in name_n
        return re.search(rf"\b{re.escape(term_n)}", name_n) is not None
    return term_n in name_n


def match_entry(name: str, entries: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """把一条方法线索名匹配到词表词条（无匹配返回 None）。

    匹配顺序：slug 精确 → 英文别名（词界）→ 中文名（子串）。
    首个命中即返回（词条顺序即优先级，手工编辑词表可控制）。
    """
    if not name:
        return None
    name_n = _norm_term(name)
    for entry in entries:
        if _norm_term(entry.get("slug", "")) == name_n:
            return entry
    for entry in entries:
        for alias in entry.get("aliases", []) or []:
            if _term_in_name(alias, name):
                return entry
    for entry in entries:
        for zh in entry.get("zh", []) or []:
            if _term_in_name(zh, name):
                return entry
    return None


def _fallback_slug(name: str) -> str:
    """从方法线索名生成英文 slug。

    优先提取名中最长英文段（如"半经典动力学方程（Berry曲率反常速度）"
    → berry）；无英文段（纯中文名）退化为连字符压缩 + hash 短码保
    唯一（页面 title 用中文 display 名，可读性由 title 承担）。
    """
    s = re.sub(r"[^0-9A-Za-z]+", "-", name.strip().lower()).strip("-")
    # 取最长的纯字母段（≥4 字符），跳过纯数字段
    segments = [seg for seg in s.split("-") if len(seg) >= 4 and seg.isalpha()]
    if segments:
        s = max(segments, key=len)
    elif not s:
        import hashlib
        s = "m" + hashlib.md5(name.encode("utf-8")).hexdigest()[:8]
    return s[:48]


def group_leads(
    summaries: List[Dict[str, Any]],
    lexicon: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """把本轮全部 method_leads 归组到方法页。

    Returns:
        (groups, unmatched)。group 结构：
        {"page": 文件名, "slug": 词条 slug 或派生 slug, "entry": 词条或 None,
         "create": 是否需新建页, "leads": [{name, note, source_id, title, tier}]}
        unmatched 为词表与同类聚合都不达标的散条（仅计数上报，不建页）。
    """
    by_page: Dict[str, Dict[str, Any]] = {}
    pending_named: Dict[str, List[Dict[str, Any]]] = {}

    for s in summaries:
        sid = s.get("source_id", "")
        title = s.get("title", "")
        tier = s.get("tier", 2)
        for lead in s.get("method_leads", []) or []:
            if not isinstance(lead, dict):
                continue
            name = str(lead.get("name", "") or "").strip()
            if not name:
                continue
            item = {
                "name": name,
                "note": str(lead.get("note", "") or "").strip(),
                "source_id": sid,
                "title": title,
                "tier": tier,
            }
            entry = match_entry(name, lexicon)
            if entry:
                page = entry.get("page", "") or f"{entry.get('slug')}.md"
                g = by_page.setdefault(page, {
                    "page": page, "slug": entry.get("slug", ""),
                    "entry": entry, "create": False, "leads": [],
                })
                g["leads"].append(item)
            else:
                pending_named.setdefault(_norm_term(name), []).append(item)

    # 词表无匹配：先按归一化名聚桶，再做同类宽松合并（同义不同形，
    # 如"海森堡不确定"与"海森堡不确定原理"——精确 key 会让同类散条
    # 永不相聚），合并后同类 ≥2 条且跨 ≥2 个不同来源 → 新建页
    buckets = _merge_similar_buckets(pending_named)

    unmatched: List[Dict[str, Any]] = []
    for key, items in buckets.items():
        distinct_sources = {i.get("source_id") for i in items}
        if len(items) >= 2 and len(distinct_sources) >= 2:
            name = items[0]["name"]
            slug = _fallback_slug(name)
            page = f"{slug}.md"
            g = by_page.setdefault(page, {
                "page": page, "slug": slug, "entry": None, "create": True,
                "leads": [],
            })
            g["leads"].extend(items)
            g.setdefault("display", name)
        else:
            # 散条：不达建页门槛，仅计数上报（宁缺毋滥，同 new 路由门槛哲学）
            unmatched.extend(items)

    groups = sorted(
        by_page.values(),
        key=lambda g: len(g["leads"]),
        reverse=True,
    )
    return groups, unmatched


def _merge_similar_buckets(
    pending_named: Dict[str, List[Dict[str, Any]]],
    similarity: float = 0.6,
) -> Dict[str, List[Dict[str, Any]]]:
    """同类宽松合并：桶 key 相似度 ≥ 阈值（SequenceMatcher）时并桶。

    归一化名精确聚桶对"同义不同形"的方法名（带/不带"原理""方法"
    等后缀）不敏感，同类线索会散落各桶永远不达建页门槛。并桶用
    最长 key 作代表（更完整的名称生成更好的 slug）。
    """
    from difflib import SequenceMatcher

    merged: Dict[str, List[Dict[str, Any]]] = {}
    for key in sorted(pending_named, key=len, reverse=True):
        items = pending_named[key]
        target = None
        for existing in merged:
            if key == existing:
                target = existing
                break
            ratio = SequenceMatcher(None, key, existing).ratio()
            if ratio >= similarity or key in existing or existing in key:
                target = existing
                break
        if target is None:
            merged[key] = list(items)
        else:
            merged[target].extend(items)
    return merged


# ---------------------------------------------------------------------------
# 按需回原文（定位而非全文）
# ---------------------------------------------------------------------------


def arxiv_id_from_source(source_id: str) -> str:
    """从 source_id 提取 arxiv id（如 0707.4192；无则空串）。

    source_id 形如 paper:2007-0707.4192-slug 或 paper:0707.4192
    （hermes papers 路径 stem 直接是 arxiv id）。
    """
    m = _ARXIV_ID_RE.search(source_id or "")
    return m.group(1) if m else ""


def txt_cache_path(source_id: str) -> Optional[Path]:
    """源对应的 PDF 提取 txt 路径（点号换下划线；无对应返回 None）。"""
    arxiv_id = arxiv_id_from_source(source_id)
    if not arxiv_id:
        return None
    p = TEXT_CACHE_DIR / f"{arxiv_id.replace('.', '_')}.txt"
    return p if p.exists() else None


def locate_txt_window(
    text: str,
    terms: List[str],
    window_chars: int = TXT_WINDOW_CHARS,
) -> str:
    """在原文 txt 中定位方法段落窗口（命中行前后共 2-3KB）。

    启发式（正则找命中行）：
      1) 方法名/别名命中行；
      2) 章节标题词（Methods|方法|实验装置 等）行；
      3) 参数符号（如 λ=800nm、intensity 10^14）行作为加权信号
         （仅在已有 1/2 命中时延伸窗口，不独立触发）。
    取首个命中行前后窗口（前 1/3 后 2/3），窗口边界按行对齐；第二处
    命中（与首窗不重叠）追加，最多两窗，总长受 window_chars×2 封顶。
    无命中返回空串。
    """
    if not text:
        return ""
    lines = text.split("\n")
    term_res = [re.compile(re.escape(t), re.IGNORECASE)
                for t in terms if t and len(t) >= 2]
    hits: List[int] = []
    for idx, line in enumerate(lines):
        if any(r.search(line) for r in term_res):
            hits.append(idx)
            continue
        if _SECTION_HEADER_RE.search(line) and idx < len(lines) - 1:
            # 章节标题行本身要像标题（短行或 Markdown 标题）
            if line.strip().startswith("#") or len(line.strip()) <= 80:
                hits.append(idx)

    if not hits:
        return ""

    _ALIGN_LIMIT = 200  # 行对齐回溯/前进上限（PDF 提取 txt 常见无换行巨行）

    def _window_at(idx: int) -> Tuple[int, int]:
        """命中行的字符窗口（行对齐：前 1/3 + 后 2/3）。

        行对齐限制回溯/前进 ≤200 字符：PDF 提取的 txt 可能整段无
        换行（万字符巨行），无上限对齐会让窗口边界一路退到巨行
        行首，命中内容被挤到窗口外。
        """
        start = sum(len(l) + 1 for l in lines[:idx])
        before = window_chars // 3
        after = window_chars - before
        s = max(0, start - before)
        e = min(len(text), start + after)
        # 行边界对齐（限制回溯量，超长行接受硬截半行）
        nl = text.rfind("\n", max(0, s - _ALIGN_LIMIT), s)
        if nl >= 0:
            s = nl + 1
        elif s > _ALIGN_LIMIT:
            s = s - _ALIGN_LIMIT
        nl2 = text.find("\n", e, e + _ALIGN_LIMIT)
        if nl2 >= 0:
            e = nl2 + 1
        return s, e

    spans: List[Tuple[int, int]] = []
    for idx in hits:
        s, e = _window_at(idx)
        # 与已有窗重叠则并窗
        merged = False
        for i, (ps, pe) in enumerate(spans):
            if s <= pe and e >= ps:
                spans[i] = (min(ps, s), max(pe, e))
                merged = True
                break
        if not merged:
            spans.append((s, e))
        if len(spans) >= 2:
            break  # 最多两窗（控注入体量）

    total_cap = window_chars * 2
    out_parts: List[str] = []
    used = 0
    for s, e in sorted(spans):
        seg = text[s:e]
        if used + len(seg) > total_cap:
            seg = seg[: total_cap - used]
        if seg.strip():
            out_parts.append(seg.strip())
            used += len(seg)
        if used >= total_cap:
            break
    return "\n……\n".join(out_parts)


def _evidence_for_group(group: Dict[str, Any]) -> Tuple[str, int]:
    """为组内 leads 逐条回原文，拼装证据文本。

    Returns:
        (evidence_text, txt_hit_count)。evidence 含每条 lead 的
        简报线索 + 原文窗口（如有）。
    """
    entry = group.get("entry") or {}
    terms = list(entry.get("aliases", []) or []) + list(entry.get("zh", []) or [])
    terms.append(group.get("display", "") or "")
    parts: List[str] = []
    txt_hits = 0
    for lead in group["leads"]:
        seg = f"[{lead.get('source_id', '')}] {lead.get('name', '')}: {lead.get('note', '')}"
        txt_path = txt_cache_path(lead.get("source_id", ""))
        if txt_path is not None:
            try:
                raw = txt_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                raw = ""
            window = locate_txt_window(raw, terms) if raw else ""
            if window:
                seg += f"\n原文定位（{txt_path.name}）：\n{window}"
                txt_hits += 1
        parts.append(seg)
    return "\n\n".join(parts), txt_hits


# ---------------------------------------------------------------------------
# growth_stage 晋升（纯函数）
# ---------------------------------------------------------------------------


def promote_growth_stage(current: str, settled_count: int, body_len: int) -> str:
    """按 settled 次数晋升 growth_stage（单调不降级）。

    seedling → growing（settled ≥2）→ mature（settled ≥4 或正文 >1500 字）。
    mature/未知值不降级不覆盖（growth_engine 同哲学：用户手设 mature
    不被覆盖）。需求原文的 sprout 对齐现有 growing 阶段名。
    """
    current = (current or "seedling").strip().strip('"\'') or "seedling"
    if current not in ("seedling", "growing"):
        return current  # mature/archived/用户自定义值不动
    if current == "seedling":
        if settled_count >= SETTLE_TO_MATURE or body_len > SETTLE_MATURE_BODY_CHARS:
            return "mature"
        if settled_count >= SETTLE_TO_GROWING:
            return "growing"
        return "seedling"
    # growing → mature
    if settled_count >= SETTLE_TO_MATURE or body_len > SETTLE_MATURE_BODY_CHARS:
        return "mature"
    return "growing"


# ---------------------------------------------------------------------------
# 方法页读写（统一门面 + 原子降级）
# ---------------------------------------------------------------------------


def _methods_page_abs(page_file: str) -> Path:
    """方法页绝对路径。

    用模块级 PROJECT_ROOT 构造（而非 paths.KNOWLEDGE_DIR 运行时绑定）：
    本模块的读路径与 kb 门面写路径在生产环境同源（paths 亦由
    PROJECT_ROOT 派生），测试隔离目录（重导入后 PROJECT_ROOT 指向
    tmp）下读写两侧一致——paths.KNOWLEDGE_DIR 是导入期绑定常量，
    patch paths.PROJECT_ROOT 不影响它，读侧用它会造成读写目录分裂。
    """
    return PROJECT_ROOT / "knowledge" / METHODS_WIKI_REL_DIR / page_file


def read_method_page(page_file: str) -> Dict[str, Any]:
    """读取方法页 {"frontmatter": dict, "body": str}；不存在返回空结构。"""
    path = _methods_page_abs(page_file)
    if not path.exists():
        return {"frontmatter": {}, "body": ""}
    try:
        from kb_text import parse_frontmatter
        fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        return {"frontmatter": fm, "body": body}
    except Exception as e:
        if _log:
            _log.warning(f"读取方法页失败（{page_file}）: {e}")
        return {"frontmatter": {}, "body": ""}


def save_method_page(page_file: str, body: str, meta: Dict[str, Any]) -> bool:
    """写入方法页：优先 kb_wiki 统一门面（防双 frontmatter + 图谱同步），
    门面异常时降级 kb_text frontmatter + tempfile+os.replace 原子写。
    """
    try:
        import knowledge_base as kb
        kb.save_wiki_page(f"{METHODS_WIKI_REL_DIR}/{page_file}", body, meta)
        return True
    except Exception as e:
        if _log:
            _log.warning(f"kb 门面写入失败（{page_file}），降级原子写: {e}")
    try:
        from kb_text import build_frontmatter
        path = _methods_page_abs(page_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        page_text = f"{build_frontmatter(meta)}\n\n{body.strip()}\n"
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(page_text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        return True
    except Exception as e:
        if _log:
            _log.warning(f"方法页原子写入失败（{page_file}）: {e}")
        return False


def _split_settle_block(body: str) -> Tuple[str, str]:
    """把正文拆为 (专区内容, 专区外正文)；无专区时专区为空。"""
    if SETTLE_BLOCK_BEGIN not in body or SETTLE_BLOCK_END not in body:
        return "", body.strip()
    begin = body.index(SETTLE_BLOCK_BEGIN) + len(SETTLE_BLOCK_BEGIN)
    end = body.index(SETTLE_BLOCK_END)
    block = body[begin:end].strip()
    rest = (body[: body.index(SETTLE_BLOCK_BEGIN)] +
            body[end + len(SETTLE_BLOCK_END):]).strip()
    return block, rest


def _render_settle_block(digest: Dict[str, Any], log_lines: List[str]) -> str:
    """把结构化摘要渲染为专区 Markdown。"""
    lines: List[str] = []
    principle = str(digest.get("principle", "") or "").strip()
    if principle:
        lines.append("## 原理")
        lines.append("")
        lines.append(principle)
        lines.append("")
    params = [p for p in (digest.get("params") or []) if isinstance(p, dict)]
    if params:
        lines.append("## 参数表")
        lines.append("")
        lines.append("| 参数 | 数值 | 出处 |")
        lines.append("| --- | --- | --- |")
        for p in params[:12]:
            lines.append(
                f"| {str(p.get('name', '')).strip() or '—'} "
                f"| {str(p.get('value', '')).strip() or '—'} "
                f"| {str(p.get('source', '')).strip() or '—'} |")
        lines.append("")
    boundary = str(digest.get("boundary", "") or "").strip()
    if boundary:
        lines.append("## 适用边界")
        lines.append("")
        lines.append(boundary)
        lines.append("")
    works = [str(w) for w in (digest.get("works") or []) if str(w).strip()]
    if works:
        lines.append("## 代表作")
        lines.append("")
        for w in works[:8]:
            lines.append(f"- {w.strip()}")
        lines.append("")
    if log_lines:
        lines.append("## 证据日志")
        lines.append("")
        lines.extend(log_lines)
        lines.append("")
    return "\n".join(lines).strip()


def _parse_settle_log(block: str) -> List[str]:
    """从专区正文提取既有证据日志行（保留追加语义）。"""
    lines: List[str] = []
    in_log = False
    for line in block.split("\n"):
        if line.strip() == "## 证据日志":
            in_log = True
            continue
        if in_log:
            if line.startswith("## "):
                break
            if line.strip().startswith("- "):
                lines.append(line.rstrip())
    return lines


def _build_page_body(digest: Dict[str, Any], log_lines: List[str], old_body: str) -> str:
    """组装完整正文：结构化专区（置顶）+ 既有专区外正文（原样保留）。"""
    _, rest = _split_settle_block(old_body)
    block = _render_settle_block(digest, log_lines)
    parts = [f"{SETTLE_BLOCK_BEGIN}\n\n{block}\n\n{SETTLE_BLOCK_END}"]
    if rest:
        parts.append(rest)
    return "\n\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# LLM 融合 / fallback
# ---------------------------------------------------------------------------


def _llm_merge_digest(
    page_title: str,
    old_block: str,
    evidence: str,
) -> Optional[Dict[str, Any]]:
    """LLM 融合：现有专区 + 新证据 → 结构化摘要 JSON（失败返回 None）。

    走项目现有 _llm_json 通道（weekend_input 优先 GLM，失败回落全局链）。
    """
    from .input_jobs import _llm_json

    system = (
        "你是林赛（强场超快光学方向研究者），维护团队的方法学知识页。"
        "输入为一个方法的当前知识摘要与新证据（文献简报线索 + 可选的"
        "原文定位片段），请把新信息融合进现有知识，输出合法 JSON 对象：\n"
        '  "principle": 原理一句话（吸收新证据后更新，保留仍然成立的旧要点）；\n'
        '  "params": 可核参数数组，每项 {"name": 参数名, "value": 数值+单位, '
        '"source": 出处（source_id 或文献标识）}，无则 []；\n'
        '  "boundary": 适用边界一句话（近似条件/失效边界/成本局限）；\n'
        '  "works": 代表作数组（引用 wiki/papers 卡名或 arXiv id，不生造），'
        "无则 []。\n"
        "要求：数值必须来自证据文本（不得推算编造）；与现有摘要矛盾的"
        "新证据以新为准并体现在 principle/boundary。"
    )
    user = (
        f"方法页：{page_title}\n\n"
        f"【当前知识摘要】\n{old_block or '（新建页：暂无摘要）'}\n\n"
        f"【本轮新证据】\n{evidence}\n\n"
        f"输出 JSON："
    )
    data = _llm_json(system, user, timeout=120)
    if not isinstance(data, dict):
        return None
    # 最小有效性：四个字段至少一个非空
    if not any(str(data.get(k) or "").strip() for k in ("principle", "boundary")) \
            and not (data.get("params") or data.get("works")):
        return None
    return data


# ---------------------------------------------------------------------------
# 主 handler
# ---------------------------------------------------------------------------


def run_input_methods_settle(
    state: Dict[str, Any],
    job: Dict[str, Any],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """方法学专题沉淀：本轮 method_leads → 归组 → 按需回原文 → 融合进方法页。

    产物 methods-settle-{date}-r{round}.json（"done 必有产物"不变式：
    空 leads 也写空产物文件）。dry-run 零落盘（词表生成同样不落盘）。
    """
    from .input_jobs import _load_round_summaries
    from .rounds import current_round

    lexicon = load_methods_lexicon(persist=not dry_run)
    summaries = _load_round_summaries(state)
    round_num = current_round(state)

    all_leads = sum(len(s.get("method_leads") or []) for s in summaries)
    date_str = now_utc()[:10]
    out_path = WEEKEND_INPUT_DIR / f"methods-settle-{date_str}-r{round_num}.json"

    if all_leads == 0:
        if not dry_run:
            WEEKEND_INPUT_DIR.mkdir(parents=True, exist_ok=True)
            save_json(out_path, {"round": round_num, "generated_at": now_utc(),
                                 "pages": [], "leads": 0,
                                 "message": "本轮无方法线索"})
        return {"success": True, "pages": 0, "leads": 0, "round": round_num,
                "message": "本轮 summaries 无 method_leads，写空产物"}

    groups, unmatched = group_leads(summaries, lexicon)

    if dry_run:
        return {
            "success": True, "dry_run": True, "round": round_num,
            "leads": all_leads, "pages": min(len(groups), METHODS_SETTLE_ROUND_CAP),
            "unmatched": len(unmatched),
            "message": f"dry-run 跳过方法页融合（{len(groups)} 组待融合）",
        }

    page_reports: List[Dict[str, Any]] = []
    total_txt = 0
    fallback_pages = 0
    for group in groups[:METHODS_SETTLE_ROUND_CAP]:
        report = _settle_one_group(group, round_num)
        page_reports.append(report)
        total_txt += report.get("txt_windows", 0)
        if report.get("fallback"):
            fallback_pages += 1

    WEEKEND_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_json(out_path, {
        "round": round_num,
        "generated_at": now_utc(),
        "leads": all_leads,
        "pages": page_reports,
        "unmatched_skipped": [{"name": u.get("name", "")} for u in unmatched[:20]],
        "cap": METHODS_SETTLE_ROUND_CAP,
        "overflow_groups": max(0, len(groups) - METHODS_SETTLE_ROUND_CAP),
    })

    return {
        "success": True,
        "round": round_num,
        "leads": all_leads,
        "pages": len(page_reports),
        "txt_windows": total_txt,
        "fallback_pages": fallback_pages,
        "unmatched": len(unmatched),
    }


def _settle_one_group(group: Dict[str, Any], round_num: int) -> Dict[str, Any]:
    """融合单组 leads 进对应方法页，返回产物条目。"""
    page_file = group["page"]
    create = bool(group.get("create")) or not _methods_page_abs(page_file).exists()
    page = read_method_page(page_file)
    fm = dict(page["frontmatter"])
    old_body = page["body"]

    if create:
        display = group.get("display") or (group["entry"] or {}).get("slug") or page_file
        fm.setdefault("title", str(display))
        fm.setdefault("type", "methods")
        fm.setdefault("tags", ["方法学", f"#type/method"])
        fm.setdefault("related", [])
        fm.setdefault("source_raw", "")
        fm.setdefault("growth_stage", "seedling")
        fm.setdefault("confidence", 0.5)

    evidence, txt_hits = _evidence_for_group(group)
    old_block, _rest = _split_settle_block(old_body)
    log_lines = _parse_settle_log(old_block)

    digest = None
    fallback = False
    from llm_gateway import is_llm_available
    if is_llm_available():
        digest = _llm_merge_digest(fm.get("title", page_file), old_block, evidence)
    if digest is None:
        # 降级：附录式追加——以 lead 名/笔记撑起最小专区，日志标 fallback
        fallback = True
        digest = _minimal_digest_from_leads(group, old_block)

    today = now_utc()[:10]
    for lead in group["leads"]:
        src_txt = "回原文" if txt_cache_path(lead.get("source_id", "")) is not None else "仅简报"
        tag = "（fallback：LLM 融合失败，附录式追加）" if fallback else ""
        log_lines.append(
            f"- {today}｜r{round_num}｜{src_txt}｜[{lead.get('source_id', '')}] "
            f"{lead.get('name', '')}：{lead.get('note', '')}{tag}"
        )
    # 日志裁剪：保留最近 30 条（页面防膨胀）
    log_lines = log_lines[-30:]

    new_body = _build_page_body(digest, log_lines, old_body)

    settled_count = int(fm.get("settled_count", 0) or 0) + 1
    new_stage = promote_growth_stage(
        str(fm.get("growth_stage", "seedling")), settled_count, len(new_body))
    new_conf = fm.get("confidence", 0.5)
    try:
        new_conf = float(new_conf)
    except (TypeError, ValueError):
        new_conf = 0.5
    if txt_hits > 0:
        new_conf = min(CONFIDENCE_CAP, round(new_conf + CONFIDENCE_STEP, 2))

    meta = {
        "title": fm.get("title", page_file),
        "type": "methods",
        "updated_at": now_utc(),
        "growth_stage": new_stage,
        "settled_count": settled_count,
        "confidence": new_conf,
    }
    # 词条别名并入 frontmatter aliases（利于检索/注入端反向匹配）
    aliases = [a for a in (fm.get("aliases") or []) if isinstance(a, str)]
    entry = group.get("entry") or {}
    for a in list(entry.get("aliases", []) or []) + list(entry.get("zh", []) or []):
        if a and a not in aliases:
            aliases.append(a)
    if aliases:
        meta["aliases"] = aliases
    # 保留既有 frontmatter 字段（tags/related/created 等由门面合并）
    meta.update({k: v for k, v in fm.items() if k not in meta})

    written = save_method_page(page_file, new_body, meta)
    if _log:
        icon = "✓" if written else "✗"
        _log.info(
            f"{icon} [methods_settle] {page_file}: 融合 {len(group['leads'])} 条线索，"
            f"回原文 {txt_hits} 次，{'fallback' if fallback else 'llm'}，"
            f"stage={new_stage} settled={settled_count}"
        )

    return {
        "page": page_file,
        "created": create,
        "merged_leads": len(group["leads"]),
        "txt_windows": txt_hits,
        "fallback": fallback,
        "growth_stage": new_stage,
        "settled_count": settled_count,
        "confidence": new_conf,
        "written": written,
    }


def _minimal_digest_from_leads(group: Dict[str, Any], old_block: str) -> Dict[str, Any]:
    """LLM 失败时的最小结构化摘要：保留旧专区内容，补 lead 概要。"""
    digest: Dict[str, Any] = {"params": [], "works": []}
    if old_block:
        # 复用旧专区文本作为 principle 的载体（原样保留旧知识）
        digest["principle"] = old_block.split("\n## 参数表")[0].replace("## 原理", "").strip()
        digest["principle"] = digest["principle"] or None
    notes = [f"{l.get('name', '')}：{l.get('note', '')}" for l in group["leads"][:3]]
    lead_summary = "；".join(n for n in notes if n.strip())
    if digest.get("principle"):
        digest["principle"] = f"{digest['principle']}\n（{today_note()}待融合线索：{lead_summary}）"
    else:
        digest["principle"] = f"（{today_note()}待融合线索：{lead_summary}）"
    return digest


def today_note() -> str:
    return now_utc()[:10]


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------


def _self_check() -> None:
    """自检：纯函数层（归组 / txt 定位 / 晋升 / 窗口边界）。"""
    print("=== weekend_pipeline.methods_jobs 自检 ===")

    # 1) 词表匹配
    lex = [
        {"slug": "tdse", "page": "TDSE求解器.md",
         "aliases": ["TDSE", "split-operator"], "zh": ["含时薛定谔"]},
        {"slug": "rabbitt", "page": "RABBITT.md",
         "aliases": ["RABBITT"], "zh": []},
    ]
    assert match_entry("TDSE solver", lex)["page"] == "TDSE求解器.md"
    assert match_entry("含时薛定谔方程求解", lex)["page"] == "TDSE求解器.md"
    assert match_entry("RABBITT measurement", lex)["page"] == "RABBITT.md"
    assert match_entry("绝热拖曳", lex) is None
    print("✓ 词表匹配（slug/英文词界/中文子串）")

    # 2) 归组 + 新建页门槛
    summaries = [
        {"source_id": "paper:2007-0707.4192-x", "title": "A", "tier": 1,
         "method_leads": [{"name": "TDSE", "note": "n1"}]},
        {"source_id": "paper:2008-0808.1111-y", "title": "B", "tier": 1,
         "method_leads": [{"name": "TDSE 求解", "note": "n2"},
                           {"name": "海森堡不确定", "note": "散条1"}]},
        {"source_id": "paper:2009-0909.2222-z", "title": "C", "tier": 1,
         "method_leads": [{"name": "海森堡不确定原理", "note": "散条2"}]},
    ]
    groups, unmatched = group_leads(summaries, lex)
    by_page = {g["page"]: g for g in groups}
    assert len(by_page["TDSE求解器.md"]["leads"]) == 2, "词表组应聚 2 条"
    assert by_page["TDSE求解器.md"]["create"] is False
    assert "海森堡不确定.md" in by_page or any(
        g["create"] for g in groups), "同类 ≥2 条跨 2 源应建新页组"
    print("✓ 归组（词表优先 / 同类 ≥2 建页 / 散条 unmatched）")

    # 3) arxiv 提取 + txt 路径
    assert arxiv_id_from_source("paper:2007-0707.4192-improved") == "0707.4192"
    assert arxiv_id_from_source("paper:2506.22860") == "2506.22860"
    assert arxiv_id_from_source("briefing:knowledge/x.md") == ""
    print("✓ arxiv id 提取（含 year- 前缀长 stem / 无 id 场景）")

    # 4) txt 定位窗口（命中 + 边界对齐）
    filler = "背景介绍行 " * 200
    txt = (filler + "\n## Methods\nWe solve the TDSE with split-operator method.\n"
           + "参数行 intensity 1e14 W/cm2.\n" + filler)
    win = locate_txt_window(txt, ["TDSE"])
    assert "TDSE" in win and "split-operator" in win, "窗口应含命中行"
    assert len(win) <= TXT_WINDOW_CHARS * 2 + 16, "窗口长度应受封顶"
    for line in win.split("\n"):
        assert not line or line in txt or line == "……", f"窗口行应来自原文：{line[:30]}"
    # 章节标题行独立触发（Methods 章节即方法段落的定位锚）
    win2 = locate_txt_window(txt, ["不存在的词xyz"])
    assert "## Methods" in win2, "无方法词命中时章节标题仍应定位 Methods 段"
    # 无方法词且无章节标题 → 空串
    plain = "纯背景介绍 " * 100
    assert locate_txt_window(plain, ["不存在的词xyz"]) == "", "无任何命中返回空串"
    print("✓ txt 定位窗口（方法名命中 / 章节标题 / 无命中空串）")

    # 5) growth 晋升
    assert promote_growth_stage("seedling", 1, 100) == "seedling"
    assert promote_growth_stage("seedling", 2, 100) == "growing"
    assert promote_growth_stage("growing", 3, 100) == "growing"
    assert promote_growth_stage("growing", 4, 100) == "mature"
    assert promote_growth_stage("seedling", 1, 2000) == "mature", "内容 >1500 字直接 mature"
    assert promote_growth_stage("mature", 99, 10) == "mature", "mature 不降级"
    assert promote_growth_stage("", 2, 100) == "growing", "空值缺省 seedling"
    print("✓ growth_stage 晋升（次数门槛 / 内容门槛 / 不降级）")

    # 6) 专区拆装幂等
    body = f"{SETTLE_BLOCK_BEGIN}\n\n## 原理\n\np1\n\n{SETTLE_BLOCK_END}\n\n旧正文"
    block, rest = _split_settle_block(body)
    assert "p1" in block and rest == "旧正文"
    rebuilt = _build_page_body({"principle": "p2"}, ["- log"], body)
    assert "p2" in rebuilt and "旧正文" in rebuilt and "p1" not in rebuilt.split("旧正文")[0].split("## 原理")[-1]
    print("✓ 结构化专区拆装（旧专区替换 / 区外正文保留）")

    print("✓ methods_jobs 自检通过")


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        _self_check()
