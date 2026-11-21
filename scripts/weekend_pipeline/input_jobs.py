#!/usr/bin/env python3
"""输入阶段 job 执行器。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import load_json, now_utc, save_json, safe_filename
from llm_gateway import is_llm_available, llm_complete
from paths import PROJECT_ROOT

from .constants import (
    CLUSTER_DISTILL_ROUND_CAP,
    DIGEST_BATCH_LIMIT,
    RELIABILITY_DERIVED,
    RELIABILITY_RELIABLE,
    WEEKEND_INPUT_DIR,
)
from .sources import (
    collect_all_sources,
    list_kb_paper_pages,
    new_paper_sources,
    search_kb_for_query,
)
from .state import mark_source_processed

try:
    from logger import get_logger
    _log = get_logger("weekend_pipeline")
except Exception:
    _log = None

# v7.3.83: 周深读配额（用户裁决 2026-11-15 token 治理②）——deep_digest
# 原无总量上限，实测周末 3 天深读 ~130 篇烧 1.39M tokens（占窗口 67%）。
# 每周封顶 50 篇：超出部分来源保持"未处理"自然滚动（processed_sources
# 保留 28 天，下周继续消化），空产物落盘不变式（v6.9.7）保证阶段可完成。
DEEP_DIGEST_WEEKLY_QUOTA = 50


def _iso_week_key(ts: str) -> str:
    """UTC ISO 时间戳 → "YYYY-Www" 周键（配额按自然周滚动）。"""
    from datetime import datetime
    d = datetime.strptime(ts[:10], "%Y-%m-%d")
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _digest_quota_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """读/滚动周深读配额计数器（state 持久化，随 job 执行落盘）。"""
    week = _iso_week_key(now_utc())
    dd = state.get("deep_digest_quota")
    if not isinstance(dd, dict) or dd.get("week") != week:
        dd = {"week": week, "digested": 0}
        state["deep_digest_quota"] = dd
    return dd


def _ensure_input_dir() -> None:
    WEEKEND_INPUT_DIR.mkdir(parents=True, exist_ok=True)


def _read_text(path: Path, max_chars: int = 8000) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except Exception:
        return ""


def _llm_json(system: str, user: str, timeout: int = 120, prefer: str = "weekend_input") -> Any:
    """调用 LLM 并解析 JSON。

    v6.9.14: 默认 prefer="weekend_input"——本模块三个 LLM 调用点
    （summarize 摘要 / cluster_distill 知识卡 / topic_match 仲裁）
    统一走 GLM 最新（glm-5.3）为主模型，失败回落全局链。调用方
    可显式传 prefer=None 恢复全局策略。
    """
    if not is_llm_available():
        return None
    ok, text, meta = llm_complete(system, user, timeout=timeout, prefer=prefer)
    if not ok:
        if _log:
            _log.warning(f"LLM 调用失败: {meta.get('error', 'unknown')}")
        return None
    # v7.3.57: 共享容错提取器统一收敛（llm_json_lib）——围栏剥离/字符串态
    # 平衡扫描/CJK 内引号修复链，取代本地 v6.10.1/v6.10.9 降级实现。
    # 实测背景：11-07 00:26/00:29 deep_digest 单批 8 败 2，中文值内含未转义
    # ASCII 引号（"Expecting ',' delimiter" 落在中文字符串中段），旧 brace
    # 切片无法修复结构性错误，共享提取器的修复通道确定性覆盖该失败类。
    from llm_json_lib import extract_json
    value, reason = extract_json(text)
    if value is not None:
        return value
    if _log:
        _log.warning(
            f"解析 LLM 输出失败（{reason}）；原始响应前200字符: {repr(text[:200])}"
        )
    return None


def _tokenize(text: str) -> set:
    if not text:
        return set()
    words = set(re.findall(r"[a-zA-Z]{3,}", text.lower()))
    words.update(re.findall(r"[\u4e00-\u9fff]{2,8}", text))
    return words


def _jaccard_similarity(a: str, b: str) -> float:
    set_a = _tokenize(a)
    set_b = _tokenize(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


# ---------------------------------------------------------------------------
# Job handlers
# ---------------------------------------------------------------------------


def run_input_collect(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """收集来源并记录 processed_sources。

    v6.8.13: 前置调用 sync_engine.sync_hermes_outputs() 确保 hermes 产出已汇聚。
    """
    if not dry_run:
        try:
            import sync_engine
            sync_engine.sync_hermes_outputs()
            if _log:
                _log.info("输入端：hermes outputs 已同步")
        except Exception as e:
            if _log:
                _log.warning(f"输入端：sync_hermes_outputs 失败（继续）: {e}")

    sources = collect_all_sources(state=state, days=7, paper_limit=20, capture_limit=10,
                                  persist_scope=not dry_run)
    _ensure_input_dir()
    if not dry_run:
        save_json(WEEKEND_INPUT_DIR / f"sources-{now_utc()[:10]}.json", sources)
    # v6.9.12: distilled_excluded 是 int 计数，跳过 len()；kb 是 dict，
    # len 取子类型数
    source_counts = {
        k: (len(v) if isinstance(v, (list, dict)) else v)
        for k, v in sources.items()
        if k != "collected_at"
    }
    return {"success": True, "source_counts": source_counts}


def _normalize_keywords(raw: Any, cap: int = 15) -> List[str]:
    """关键词摄取归一化（v6.9.14 口径，v6.9.98 抽出复用）。

    去尾部括注（"高次谐波产生 (HHG)" → "高次谐波产生"）、去空、去重、
    截断到 cap。同义不同形会让聚类集合成员永不相等。
    """
    from .clusters import norm_keyword
    kws: List[str] = []
    seen: set = set()
    for kw in (raw or [])[:20]:
        nk = norm_keyword(kw)
        if nk and nk not in seen:
            kws.append(nk)
            seen.add(nk)
        if len(kws) >= cap:
            break
    return kws


def _coerce_named_notes(items: Any, keys: tuple, cap: int = 8) -> List[Dict[str, str]]:
    """v6.9.98: 把 method_leads / proposal_links 收敛为 {key0, key1} dict 数组。

    LLM 输出形状不可控：字符串项转 {key0: 原文, key1: ""}，dict 项取
    keys[0] 为必填主键（缺失则丢弃），keys[1] 为说明。截断到 cap 控成本。
    """
    out: List[Dict[str, str]] = []
    if not isinstance(items, list):
        return out
    for it in items:
        if isinstance(it, dict):
            name = str(it.get(keys[0]) or "").strip()
            if not name:
                continue
            out.append({keys[0]: name, keys[1]: str(it.get(keys[1]) or "").strip()})
        elif isinstance(it, str) and it.strip():
            out.append({keys[0]: it.strip(), keys[1]: ""})
        if len(out) >= cap:
            break
    return out


def _coerce_digest_data(data: Any, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """v6.9.98: 把 LLM 深读输出收敛为带溯源字段的 dict；无法收敛返回 None。

    形状防御沿用 v6.9.13（模型可能返回数组形状）；关键词归一化沿用
    v6.9.14。summary 字段由 core 回填——下游归簇（assign_summaries）
    与信息源挂载（member_summaries）读 summary，保持零改动兼容。
    """
    if isinstance(data, list):
        data = next((x for x in data if isinstance(x, dict)), None)
    if not isinstance(data, dict):
        return None
    data.setdefault("title", paper.get("title", ""))
    data["source_id"] = paper.get("source_id", "")
    data["path"] = paper.get("path", "")
    data["tier"] = paper.get("tier", 2)
    core = str(data.get("core") or "").strip()
    data["core"] = core
    data["mechanism"] = str(data.get("mechanism") or "").strip()
    if not str(data.get("summary") or "").strip():
        data["summary"] = core
    else:
        data["summary"] = str(data.get("summary")).strip()
    data["method_leads"] = _coerce_named_notes(data.get("method_leads"), ("name", "note"), cap=8)
    data["proposal_links"] = _coerce_named_notes(data.get("proposal_links"), ("topic", "note"), cap=6)
    data["keywords"] = _normalize_keywords(data.get("keywords"))
    return data


# v6.9.14: 关键词要求 10-15 个且强制含 2-4 个领域级标签。
# 08-15 实测：5 个论文特定关键词的集合太稀疏（30 篇中仅 2 对共享
# ≥2 词，435 对最高 Jaccard 0.161），聚类的共享词表必须由领域级
# 标签（如 固态高次谐波/强场物理/二维材料/阿秒动力学）提供。
KW_SPEC = (
    "。其中 keywords 为 10-15 个关键词：2-4 个领域级标签"
    "（如：固态高次谐波、强场物理、非线性光学、二维材料、阿秒动力学、"
    "拓扑材料、量子光学 等，标注本文所属大方向），其余为本文具体贡献关键词"
)


def _proposal_lines_for_prompt(limit: int = 40) -> str:
    """在跑课题清单（deep_digest 的 proposal_links 判断参考，仅 id+标题）。"""
    try:
        proposals = _load_all_stage_proposals()
    except Exception:
        proposals = []
    if not proposals:
        return "（当前无在跑课题）"
    return "\n".join(
        f"- {p.get('proposal_id', '')}: {str(p.get('title', ''))[:50]}"
        for p in proposals[:limit]
    )


def _current_round(state: Dict[str, Any]) -> int:
    """当前输入链轮次（state.input_round.round，缺省 1）。"""
    from .rounds import current_round
    return current_round(state)


def _record_round_artifact(state: Dict[str, Any], round_num: int, path: Path) -> None:
    """在 state 中记录本轮 summaries 产物路径（下游按此读取，防跨天错位）。"""
    ir = state.setdefault("input_round", {})
    ir["round"] = round_num
    try:
        ir["last_summaries_path"] = str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        ir["last_summaries_path"] = str(path)


def _load_round_summaries(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """读取最近一轮 deep_digest 产物摘要列表。

    v6.9.98 多轮化：优先读 state.input_round.last_summaries_path（deep_digest
    写产物时记录的真实路径，跨天轮次不错位）；回退当日轮次文件与旧名
    文件（兼容 v6.9.98 之前的 state / 人工排查场景）。
    """
    ir = state.get("input_round") or {}
    candidates: List[Path] = []
    rel = str(ir.get("last_summaries_path", "") or "")
    if rel:
        candidates.append(PROJECT_ROOT / rel)
    date_str = now_utc()[:10]
    round_num = ir.get("round", 1)
    candidates.append(WEEKEND_INPUT_DIR / f"summaries-{date_str}-r{round_num}.json")
    candidates.append(WEEKEND_INPUT_DIR / f"summaries-{date_str}.json")
    for c in candidates:
        if c.exists():
            data = load_json(c, default={})
            return [s for s in data.get("summaries", []) if isinstance(s, dict)]
    return []


def run_input_deep_digest(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """对新增论文/简报做结构化深读（v6.9.98 取代 summarize 浅摘要）。

    升级点（用户裁决定稿 T1）：
    - 输入改为简报卡全文（去掉旧 [:1200] 截断），单轮批量 30→10 篇
      （吞吐由轮次接力补回，见 weekend_pipeline/rounds.py）；
    - prompt 升级为结构化深读 JSON：core（核心贡献 2-3 句）、
      mechanism（物理机制要点）、method_leads（方法线索数组：理论
      方法/实验技术名称 + 一句话新信息）、proposal_links（与在跑课题
      的关联点：方向词 + 关联说明）、keywords（10-15 个，保留 2-4 个
      领域级标签要求）；
    - 产物带轮次号 summaries-{date}-r{round}.json（round 从 1 起）；
      首轮同时写旧名 summaries-{date}.json（下游/人工工具兼容，
      避免断裂的最小改动方案——链内下游已同步改为按 state 记录路径
      读取，旧名仅为外部兼容快照）。

    保留的故障防线：
    - v6.9.7 空产物落盘不变式：无新料也写空产物（防产物校验反复重置）；
    - v6.9.12 全失败防线：有新料但全部 LLM 失败 → success=False，
      未 mark 的来源保持"未处理"，等待重试。
    """
    round_num = _current_round(state)
    sources = collect_all_sources(state=state, days=7,
                                  paper_limit=DIGEST_BATCH_LIMIT, capture_limit=10,
                                  persist_scope=not dry_run)
    papers = new_paper_sources(sources, state)
    date_str = now_utc()[:10]
    round_path = WEEKEND_INPUT_DIR / f"summaries-{date_str}-r{round_num}.json"
    legacy_path = WEEKEND_INPUT_DIR / f"summaries-{date_str}.json"

    # v7.3.83: 周配额三闸——① 配额尽：空产物落盘（阶段可完成）+ 来源
    # 保持未处理滚动下周；② 尾轮截断：batch 只补到配额余额，不 overshoot；
    # ③ 计数：成功深读篇数入 state（deep_digest_quota）。
    quota = _digest_quota_state(state)
    quota_left = max(0, DEEP_DIGEST_WEEKLY_QUOTA - int(quota.get("digested") or 0))
    batch = papers[:min(DIGEST_BATCH_LIMIT, quota_left)]

    if papers and quota_left <= 0 and not dry_run:
        _ensure_input_dir()
        save_json(round_path, {"summaries": [], "round": round_num,
                               "generated_at": now_utc()})
        _record_round_artifact(state, round_num, round_path)
        return {"success": True, "digested": 0, "remaining_sources": len(papers),
                "round": round_num,
                "message": f"本周深读配额已用尽（{DEEP_DIGEST_WEEKLY_QUOTA} 篇），"
                           f"{len(papers)} 篇来源滚动下周"}

    if not papers:
        if not dry_run:
            _ensure_input_dir()
            save_json(round_path, {"summaries": [], "round": round_num,
                                   "generated_at": now_utc()})
            if round_num == 1:
                save_json(legacy_path, {"summaries": []})
            _record_round_artifact(state, round_num, round_path)
        return {"success": True, "digested": 0, "remaining_sources": 0,
                "round": round_num, "message": "无新增论文/简报"}

    if dry_run:
        return {"success": True, "digested": len(batch),
                "remaining_sources": max(0, len(papers) - len(batch)),
                "round": round_num, "dry_run": True,
                "message": "dry-run 跳过 LLM 深读"}

    if not is_llm_available():
        return {"success": False, "error": "LLM 不可用"}

    proposal_lines = _proposal_lines_for_prompt()
    system = (
        "你是林赛（强场超快光学方向研究者），对单篇学术文献做结构化深读。"
        "输出合法 JSON 对象，字段定义：\n"
        '  "core": 核心贡献，2-3 句；\n'
        '  "mechanism": 物理机制要点（关键物理图像/近似适用条件/参数依赖，一段）；\n'
        '  "method_leads": 方法线索数组——本文涉及的理论方法或实验技术，'
        '每项 {"name": 方法/技术名称, "note": 该方法在本文中带来的新信息（一句话）}，'
        "无则给空数组 []；\n"
        '  "proposal_links": 与在跑课题的关联点数组，每项 '
        '{"topic": 课题方向词, "note": 关联说明（一句话）}，'
        "确无关联给空数组 []，不要生造；\n"
        '  "keywords": 关键词数组。'
        f"{KW_SPEC}。"
        "summary（即 core 摘要正文）只写论文本身的科学内容，不得包含编辑注、"
        "相关性声明或审读意见（如“注意：…”“与某某主题无关联”“仅供内部参考”等）。"
    )

    digests = []
    failed_llm = 0
    for p in batch:
        # v6.9.98: 全文输入（去掉旧 [:1200] 截断）——深读需要机制细节，
        # 截断版只够支撑一句话摘要。收集层本身的读取上限
        # （papers 2000 / briefings 6000 字符）不动。
        user = (
            f"文献标题：{p.get('title', '')}\n"
            f"文献全文（简报卡）：\n{p.get('text', '')}\n\n"
            f"在跑课题清单（仅用于判断 proposal_links，无关联给空数组）：\n"
            f"{proposal_lines}\n\n"
            f"输出 JSON："
        )
        data = _llm_json(system, user, timeout=120)
        normalized = _coerce_digest_data(data, p) if data else None
        if normalized is not None:
            digests.append(normalized)
            mark_source_processed(p["source_id"], p["text"], state)
        else:
            failed_llm += 1

    remaining = max(0, len(papers) - len(digests))

    # v6.9.12 故障防线（对齐 v6.8.46 hermes 429 防线语义）：有新料但
    # 全部深读失败（LLM 限额/故障）时返回 success=False 而非空转标
    # done——否则空 digests 向下游传播，整链空跑，熔断只能事后报。
    if digests or failed_llm == 0:
        _ensure_input_dir()
        save_json(round_path, {"summaries": digests, "round": round_num,
                               "generated_at": now_utc()})
        if round_num == 1:
            # 首轮兼容旧名（外部工具/人工查阅；链内下游已按 state 路径读）
            save_json(legacy_path, {"summaries": digests})
        _record_round_artifact(state, round_num, round_path)
        # v7.3.83: 周配额计数入 state（持久化随 save_pipeline_state）
        quota["digested"] = int(quota.get("digested") or 0) + len(digests)
        return {"success": True, "digested": len(digests),
                "remaining_sources": remaining, "round": round_num,
                "quota_digested": quota["digested"],
                "quota_left": max(0, DEEP_DIGEST_WEEKLY_QUOTA - quota["digested"])}
    return {
        "success": False,
        "error": f"LLM 故障：{failed_llm} 篇新料全部深读失败（未标记已处理，等待重试）",
        "digested": 0,
        "remaining_sources": len(papers),
        "round": round_num,
    }


# ---------------------------------------------------------------------------
# v6.9.12: 知识簇链路（cluster_assign → cluster_distill → topic_match）
# ---------------------------------------------------------------------------


def _llm_assign_arbiter(item: Dict[str, Any], cluster: Dict[str, Any], score: float) -> bool:
    """v6.10.12: borderline 归簇的 LLM 语义仲裁。

    纯 Jaccard 对跨术语同主题文献系统性失配（如"量子度规反演"摘要 vs
    "Berry 曲率谱学"簇，关键词重叠低但研究问题同源）。仲裁仅判断
    语义归属，不做主题评价。失败/不可用返回 False（保守 orphan）。
    """
    summary_text = f"{item.get('title', '')} {item.get('summary', '')}"[:500]
    cluster_text = f"{cluster.get('title', '')} {cluster.get('summary', '')}"[:300]
    system = (
        "你是文献分类助手。判断一篇文献摘要是否属于某个研究主题簇"
        "（同一研究问题/物理机制/方法体系的更细或更粗表述均算同属）。"
        '只输出 JSON：{"belong": true/false, "reason": "≤40字"}'
    )
    user = (
        f"【文献摘要】{summary_text}\n\n"
        f"【主题簇】{cluster_text}\n\n"
        f"（词面相似度 {score:.2f} 偏低，请做概念级判断：该文献是否在研究"
        f"同一类问题？仅在确信同属时返回 true，边缘情况返回 false。）"
    )
    try:
        r = _llm_json(system, user, timeout=90)
        return bool(isinstance(r, dict) and r.get("belong") is True)
    except Exception:
        return False


def _is_core_theme_orphan(o: Dict[str, Any]) -> bool:
    """孤儿是否命中强场/超快核心范式（v6.10.29 清理豁免判据）。"""
    from .sources import core_theme_hit

    text = (o.get("title", "") + " " + o.get("summary", ""))[:3000]
    return core_theme_hit(text) is not None


def _collect_proposal_texts(max_chars: int = 4000) -> Dict[str, str]:
    """v7.2.4: 收集活跃课题的设想文本（orphan 直连路由的靶）。

    覆盖 optimizing + pending_review；文本取 00_research_idea.md 优先、
    00_proposal-brief.md 回退（与 kb_methods_pack._idea_text 同源逻辑），
    截断 max_chars（相似度 2-gram 通道无需全文）。
    """
    from proposal_lifecycle import ProposalLifecycle

    texts: Dict[str, str] = {}
    try:
        lc = ProposalLifecycle()
        pids = [p["proposal_id"] for s in ("optimizing", "pending_review")
                for p in lc.list_by_status(s)]
        for pid in pids:
            prop_dir = lc._find_proposal_dir(pid)
            if not prop_dir:
                continue
            text = ""
            for name in ("00_research_idea.md", "00_proposal-brief.md"):
                f = prop_dir / name
                if f.exists():
                    try:
                        text = f.read_text(encoding="utf-8", errors="ignore")
                        break
                    except Exception:
                        continue
            if text.strip():
                texts[pid] = text[:max_chars]
    except Exception as e:
        if _log:
            _log.warning(f"[orphan-route] 课题文本收集失败: {e}")
    return texts


def run_input_cluster_assign(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """增量归簇：本周摘要沿已有 open 簇融入，孤篇挂 orphans 等凑簇。

    取代旧 gap_analysis 的"每周无状态重猜 5 个方向"——簇注册表跨周
    持久化，新知识优先融入已有类（防冗余核心），单篇不成簇。
    全程零 LLM（关键词 Jaccard，确定性可回归）。
    v6.9.98: 摘要输入改读最近一轮 deep_digest 产物（state 记录路径，
    多轮/跨天不错位），不再按当日文件名猜测。
    """
    from .clusters import (
        assign_summaries,
        close_stale_clusters,
        form_new_clusters,
        load_clusters,
        prune_orphans,
        recycle_orphans,
        save_clusters,
    )

    summaries = _load_round_summaries(state)

    if dry_run:
        return {
            "success": True,
            "assigned": 0,
            "new_clusters": 0,
            "dry_run": True,
            "message": f"dry-run 跳过归簇（{len(summaries)} 条待归）",
        }

    registry = load_clusters()
    result = assign_summaries(summaries, registry, llm_arbiter=_llm_assign_arbiter)
    llm_assigned = sum(1 for a in result["assigned"] if a.get("method") == "llm")
    # v6.10.38: linked 簇影子吸收的新成员直接挂载为课题补充信息源
    # （expansion 语义，不重新路由不注入知识卡——簇已路由过，新成员
    # 只是增量文献，挂载后进入课题 references 校验与 writer 视野）
    linked_absorbed = [
        a for a in result["assigned"] if a.get("cluster_status") == "linked"
    ]
    linked_mounted = 0
    for a in linked_absorbed:
        c = next((x for x in registry.get("clusters", [])
                  if x.get("cluster_id") == a.get("cluster_id")), None)
        target = (c or {}).get("linked_proposal_id") or ""
        if c and target:
            try:
                if _write_supplementary_sources(target, c, {}):
                    linked_mounted += 1
            except Exception as e:
                if _log:
                    _log.warning(f"[cluster_assign] linked 簇挂载失败（{a.get('cluster_id')}）: {e}")
    # v7.3.25（用户裁决 决定 8 第一段）：孤儿存活天数回写（orphan_age_days），
    # >60 天在聚团中按权重递减降权（form_new_clusters 内部读取）。
    from .clusters import archive_aged_orphans, stamp_orphan_ages
    orphan_downweighted = stamp_orphan_ages(registry)
    # v7.3.25（决定 8 第二段）：存活 >180 天先移出聚团候选、归档到
    # registry.supplementary_pool（不删除，仍可 search_supplementary_pool
    # 按需检索）；归档段不再进入成团/回收/42 天清理判定。
    orphan_archived = archive_aged_orphans(registry)
    formed = form_new_clusters(registry)
    # v6.10.29: 孤儿回收——聚团后剩余孤儿与（含新簇的）全部 open 簇
    # 二次匹配，旧孤儿获得沿已有类融入的机会（否则 42 天清理=知识流失）
    recycled = recycle_orphans(registry)
    # v7.3.23（用户裁决 5b-1）：孤儿池身份去重——同一论文的 arXiv 页/
    # 期刊页/简报转述会在孤儿池留下多条记录，按 DOI/arXiv/归一标题归并
    # 成 1 条（保留信息最丰代表），避免重复记录占用池容量与清理预算。
    from .clusters import dedup_orphans
    deduped = dedup_orphans(registry)
    # v6.10.29: 强场相关孤儿豁免 42 天清理（keep_fn 真 → theme_protected）
    pruned = prune_orphans(registry, keep_fn=_is_core_theme_orphan)
    theme_protected = sum(
        1 for o in registry.get("orphans", []) if o.get("theme_protected")
    )
    stale = close_stale_clusters(registry)

    # v7.2.4: orphan → 现有课题直连路由——簇池 linked 化后 open 常态清零
    # （09-28 实测 62 簇 0 open），recycle_orphans 无对象可回收；单篇
    # 不成簇的新文献只剩 42 天清理＝知识流失。以课题设想文本为靶匹配，
    # 超线挂载 supplementary 并移出池；挂载失败回池（不丢数据）。
    orphan_route = {"routed": [], "candidates": 0, "remaining": 0, "mounted": 0}
    try:
        from .clusters import SUMMARY_TEXT_LIMIT, route_orphans_to_proposals
        proposal_texts = _collect_proposal_texts()
        if proposal_texts:
            # v7.2.57: 方向前置闸——阈值 0.25（v7.2.57 标定）只保证与某课题
            # 文本相似，不保证方向在射程内（实测过线 135 条中 14% 双命中
            # 不过）。与 _new_gates 同口径（scope_hit 方向词表 + core_theme_hit
            # 核心范式），被拒条目留池继续积累，不入路由。
            from .sources import core_theme_hit, load_scope_terms, scope_hit

            _scope_terms = load_scope_terms()

            def _orphan_direction_gate(o: Dict[str, Any]) -> bool:
                text = " ".join([
                    str(o.get("title") or ""),
                    str(o.get("summary") or "")[:SUMMARY_TEXT_LIMIT],
                    " ".join(o.get("keywords") or []),
                ])
                return (scope_hit(text, _scope_terms) is not None
                        and core_theme_hit(text) is not None)

            orphan_route = route_orphans_to_proposals(
                registry, proposal_texts, route_filter=_orphan_direction_gate,
            )
            orphan_route["mounted"] = 0
            for r in orphan_route.get("routed", []):
                entry = r.get("entry") or {}
                if not entry:
                    continue
                pseudo = {
                    "cluster_id": f"orphan-route-{now_utc()[:10]}",
                    "member_summaries": [{
                        "source_id": entry.get("source_id", ""),
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "path": entry.get("path", ""),
                    }],
                }
                try:
                    if _write_supplementary_sources(r["proposal_id"], pseudo, {}):
                        orphan_route["mounted"] += 1
                    else:
                        # 挂载失败回池防丢（下轮可重试）
                        registry.setdefault("orphans", []).append(entry)
                except Exception as e:
                    if _log:
                        _log.warning(f"[orphan-route] 挂载失败回池（{r.get('source_id')}）: {e}")
                    registry.setdefault("orphans", []).append(entry)
            if orphan_route.get("mounted") and _log:
                _log.info(
                    f"[orphan-route] {orphan_route['mounted']} 篇孤儿文献"
                    f"直连挂载到课题 supplementary"
                )
    except Exception as e:
        if _log:
            _log.warning(f"[orphan-route] 路由异常（跳过，不影响归簇）: {e}")

    save_clusters(registry)

    # v6.10.7: 高相关待积累簇被 stale 保护时，落盘人工裁决清单 + 日志
    if stale.get("protected"):
        _ensure_input_dir()
        save_json(WEEKEND_INPUT_DIR / f"stale-protected-{now_utc()[:10]}.json", {
            "generated_at": now_utc(),
            "protected_clusters": [
                {
                    "cluster_id": c.get("cluster_id", ""),
                    "title": c.get("title", ""),
                    "members": len(c.get("member_source_ids", [])),
                    "suggestion": "定向补检索凑第 3 篇触发 new 评估，或人工关闭",
                }
                for c in registry.get("clusters", [])
                if c.get("pending_human_review") and c.get("status") == "open"
            ],
        })
        if _log:
            _log.warning(
                f"[cluster_assign] {stale['protected']} 个高相关簇超 4 周未满员，"
                f"已保护不自动关闭，转人工裁决（stale-protected-{now_utc()[:10]}.json）"
            )

    _ensure_input_dir()
    save_json(WEEKEND_INPUT_DIR / f"clusters-week-{now_utc()[:10]}.json", {
        "assigned": result["assigned"],
        "orphaned": result["orphaned"],
        "new_clusters": [
            {"cluster_id": c["cluster_id"], "title": c["title"], "members": len(c["member_source_ids"])}
            for c in formed
        ],
        "orphan_recycled": recycled,
        "orphan_deduped": deduped,
        "orphan_archived": orphan_archived,
        "orphan_downweighted": orphan_downweighted,
        "linked_absorbed": len(linked_absorbed),
        "linked_mounted": linked_mounted,
        # v7.2.4: orphan 直连课题路由结果（candidates/routed/mounted/remaining）
        "orphan_route": {
            "candidates": orphan_route.get("candidates", 0),
            "routed": len(orphan_route.get("routed", [])),
            "mounted": orphan_route.get("mounted", 0),
            "remaining": orphan_route.get("remaining", 0),
        },
    })

    return {
        "success": True,
        "assigned": len(result["assigned"]),
        "assigned_via_llm": llm_assigned,
        "orphaned": len(result["orphaned"]),
        "new_clusters": len(formed),
        "orphan_recycled": recycled,
        "orphan_deduped": deduped,
        "orphan_archived": orphan_archived,
        "orphan_downweighted": orphan_downweighted,
        "linked_absorbed": len(linked_absorbed),
        "linked_mounted": linked_mounted,
        "orphan_routed": len(orphan_route.get("routed", [])),
        "orphan_mounted": orphan_route.get("mounted", 0),
        "orphan_pruned": pruned,
        "orphan_theme_protected": theme_protected,
        "stale_closed": stale["closed"],
        "stale_protected": stale["protected"],
        "total_open_clusters": sum(
            1 for c in registry.get("clusters", []) if c.get("status") == "open"
        ),
    }


# v6.10.28: 知识卡质量门槛（提炼闭环）——LLM 提炼结果过短/无开放问题
# 视为不合格，标记 pending_redistill 下轮重试，不污染 distilled_by=llm。
DISTILL_MIN_SUMMARY_CHARS = 50
DISTILL_MIN_QUESTIONS = 1


def run_input_cluster_distill(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """簇内提炼：对待提炼 open 簇生成结构化知识卡（LLM）。

    知识卡 = 簇级摘要（150-300 字）+ 开放问题 + 研究缺口，是
    topic_match 判断簇与课题关系的主要依据。LLM 不可用时簇沿用成员
    摘要拼接（降级不阻塞链路）。
    v6.10.28: 提炼闭环——① 待提炼范围扩大为"本周有新成员 或 上次
    提炼不合格"（pending_redistill），fallback/不合格簇下轮自动重试；
    ② 质量校验：summary < 50 字或无 open_questions 判不合格重提炼；
    ③ 知识卡新增 research_gap（研究缺口）字段辅助 new 决策。
    """
    from .clusters import (
        load_clusters, mark_pending_first_distill,
        open_clusters_needing_distill, save_clusters,
    )

    if dry_run:
        return {"success": True, "distilled": 0, "dry_run": True, "message": "dry-run 跳过簇提炼"}

    # 本周窗口：7 天前起有更新的簇
    from datetime import datetime, timedelta, timezone
    week_start = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    registry = load_clusters()
    # v7.3.62（修 1）：先给"从未尝试且仍 open"的簇打持久标记，再算队列。
    # 标记不受 7 天新鲜度窗口限制，避免第 4 位以后的新簇永久饥饿。
    marked = mark_pending_first_distill(registry)
    targets = open_clusters_needing_distill(registry, week_start)
    if not targets:
        if marked:
            save_clusters(registry)
        _ensure_input_dir()
        save_json(WEEKEND_INPUT_DIR / f"distilled-clusters-{now_utc()[:10]}.json", {"clusters": []})
        return {"success": True, "distilled": 0, "pending_first_distill_marked": marked,
                "message": "本周无待提炼簇"}

    system = (
        "你是林赛，擅长综合多篇文献摘要提炼主题级知识卡。"
        "输出合法 JSON 对象：{\"title\": \"主题名\", \"summary\": \"150-300字综合摘要\", "
        "\"open_questions\": [\"开放问题...\"], "
        "\"research_gap\": \"该方向相对已有研究的关键缺口（≤100字）\"}。"
    )
    distilled_out = []
    # v6.9.98: 每轮簇上限 8→3（原"周限 8 簇"语义改为"每轮 ≤3 簇"）——
    # 多轮化下一个周末约 7 轮接力，总吞吐 21 簇/周高于旧 8 簇，且
    # 单轮 LLM 成本受控（3 簇 × 120s << stale 阈值 3600s）
    for c in targets[:CLUSTER_DISTILL_ROUND_CAP]:
        members = c.get("member_summaries", [])[:12]
        user = (
            f"簇主题：{c.get('title', '')}\n"
            f"簇关键词：{', '.join(c.get('keywords', []))}\n\n"
            f"成员文献摘要：\n{json.dumps(members, ensure_ascii=False, indent=1)}\n\n"
            f"输出 JSON："
        )
        card = _llm_json(system, user, timeout=120)
        summary = (card or {}).get("summary", "") if isinstance(card, dict) else ""
        questions = (card or {}).get("open_questions", []) if isinstance(card, dict) else []
        if (
            isinstance(card, dict)
            and isinstance(summary, str)
            and len(summary.strip()) >= DISTILL_MIN_SUMMARY_CHARS
            and isinstance(questions, list)
            and len(questions) >= DISTILL_MIN_QUESTIONS
        ):
            c["summary"] = summary.strip()
            c["title"] = card.get("title", "") or c.get("title", "")
            c["open_questions"] = [str(q) for q in questions[:6]] or []
            c["research_gap"] = str(card.get("research_gap", "") or "")[:200]
            # v6.9.18: 知识卡来源标记——topic_match 的 new 门槛仅认
            # LLM 提炼卡（降级拼接的弱卡不足以支撑开新课题）
            c["distilled_by"] = "llm"
            c.pop("pending_redistill", None)
        else:
            # 不合格/失败：已有知识卡保留原样；无卡则降级拼接保链路
            c["pending_redistill"] = True
            if not c.get("summary"):
                joined = "；".join(m.get("summary", "") for m in members[:6])
                c["summary"] = joined[:500]
                c.setdefault("distilled_by", "fallback")
        # v7.3.62：本轮已尝试（不论成败），清除"从未尝试"标记；
        # 失败路径由 pending_redistill 接管重试。
        c.pop("pending_first_distill", None)
        c["distilled_at"] = now_utc()
        distilled_out.append({
            "cluster_id": c["cluster_id"],
            "title": c["title"],
            "members": len(c.get("member_source_ids", [])),
            "distilled_by": c.get("distilled_by", ""),
            "pending_redistill": c.get("pending_redistill", False),
        })

    save_clusters(registry)
    _ensure_input_dir()
    save_json(WEEKEND_INPUT_DIR / f"distilled-clusters-{now_utc()[:10]}.json", {"clusters": distilled_out})

    return {"success": True, "distilled": len(distilled_out), "pending_redistill": sum(
        1 for c in targets[:CLUSTER_DISTILL_ROUND_CAP] if c.get("pending_redistill")
    )}


def _load_all_stage_proposals() -> List[Dict[str, Any]]:
    """读取全阶段课题清单（drafts/optimizing/pending_review/archived）。

    v6.9.12: 取代旧 direction_select 只读 KB 静态页（3000 字截断、
    status 靠中文行解析）的弱数据源。直接读 research_proposals/
    目录 + 各课题 00 号 brief，覆盖全部生命周期阶段且实时。
    v8.0.0（2026-11-16）：改读 research_topics 新域（weekend_bridge 统一
    两域视图），迁移完成后 legacy 域自然为空对照。
    """
    from topic_pipeline.weekend_bridge import all_topics_and_legacy

    proposals: List[Dict[str, Any]] = []
    try:
        proposals = all_topics_and_legacy()
        if proposals:
            return proposals
    except Exception as e:
        if _log:
            _log.warning(f"读取 v8 topics 清单失败，回退 legacy: {e}")
    from proposal_lifecycle import ProposalLifecycle
    try:
        lc = ProposalLifecycle()
        for status in ("drafts", "optimizing", "pending_review", "archived"):
            for p in lc.list_by_status(status):
                prop_dir = lc._find_proposal_dir(p["proposal_id"])
                brief_text = ""
                if prop_dir:
                    for f in sorted(prop_dir.glob("00_*.md")):
                        brief_text = _read_text(f, 2000)
                        break
                proposals.append({
                    "proposal_id": p["proposal_id"],
                    "title": p.get("title", p["proposal_id"]),
                    "status": status,
                    "text": brief_text or p.get("title", ""),
                })
    except Exception as e:
        if _log:
            _log.warning(f"读取全阶段课题清单失败: {e}")
    return proposals


# v6.9.18: new 动作周配额——08-16 实测 141 簇无差别路由产出 72 new
# （54 个弱簇课题泛滥成灾，46 个 new-idea-NN 占位名）。宁缺毋滥。
# v7.3.22 裁决 3 + v7.3.76 quota_review_1109 执行：输入端去重/拆分/方向过滤
# 落地且当周候选簇 27≥10，复核通过后由 2 提至 3（一次性有据放开，非默认放宽）。
NEW_WEEKLY_QUOTA = 3
# new 门槛成员数（与 clusters.MIN_CLUSTER_MEMBERS 对齐，弱簇只允许
# merge/expansion 信息注入，不满足则 defer 继续积累）
NEW_MIN_MEMBERS = 3

# v7.2.67: 锦标赛制新颖性终审参数。Jaccard 词袋相似度无区分度实证
# （「结构压缩调控 HHG」vs「MoS₂ HHG 调控」= 0.01、order↔new 同题
# 65-70% 未检出），词袋分数不配做同质性终审。对标 Google AI
# co-scientist 的 Elo 锦标赛：Jaccard 只做预筛（省调用），同质性
# 终审交给 pairwise LLM 对比仲裁（一次调用裁一个课题对）。
TOURNAMENT_TOP_K = 5
TOURNAMENT_VERDICTS = ("同质", "正交", "互补")

# v6.9.18 补：运维簇识别词（路由前置过滤）。08-16 复跑实测运维简报
# 簇（"每日简报/hermes-briefing"）知识卡含个别领域词可过方向关，
# LLM 仲裁无 reject 选项只能判 new——注册了运维课题。
_OPS_CLUSTER_MARKERS = (
    "每日简报", "hermes-briefing", "对话记忆", "知识管理", "运维",
    "自动化系统", "cron",
)


def _is_ops_cluster(cluster: Dict[str, Any]) -> bool:
    """识别运维内容簇：标题命中运维标记，或关键词命中 ≥2 个运维词。"""
    title = cluster.get("title", "") or ""
    if any(m in title for m in _OPS_CLUSTER_MARKERS[:6]):
        return True
    kws = [str(k).lower() for k in (cluster.get("keywords") or [])]
    hits = sum(1 for m in _OPS_CLUSTER_MARKERS if any(m in k for k in kws))
    return hits >= 2


# v6.10.37: 主线体系词表——研究主线是"凝聚态/材料体系的强场超快光学探测"。
# 范式词表（CORE_THEME_TERMS）只约束"手段"（强场/HHG/超快/阿秒），不约束
# "研究对象"——09-21 用户裁决退回 6 课题中，"少阿秒电子脉冲串""孤立阿秒
# 时空光学涡旋"两簇字面命中范式词（阿秒/强场）但研究对象是自由电子束/
# 气体介质光源，完全在主线外。体系词与范式词双命中才是主线课题
# （10 个 optimizing 课题全部满足：固体 HHG/拓扑物态/莫尔/磁性/铁电…）。
MATERIAL_SYSTEM_TERMS = [
    # 中文
    "固体", "固态", "晶体", "二维", "材料", "绝缘体", "半导体", "金属",
    "半金属", "磁性", "磁化", "磁序", "反铁磁", "铁磁", "铁电", "交变磁",
    "拓扑", "莫尔", "转角", "扭转", "层间", "滑移", "堆叠", "能带", "能谷",
    "激子", "声子", "莫特", "异质结", "超晶格", "量子几何",
    # 英文
    "solid", "crystal", "material", "insulator", "semiconductor",
    "semimetal", "moire", "twisted bilayer", "bilayer", "ferroelectric",
    "altermagnet", "antiferromag", "topological", "valley", "exciton",
    "magnon", "wigner crystal", "heterostructure", "mott", "weyl",
    "dirac", "superlattice", "quantum geometry", "2d material",
    "two-dimensional",
]


def _gate_member_count(cluster: Dict[str, Any]) -> int:
    """new 门槛的「独立成员数」口径（v7.3.29 抽出，供门控与 compose 共用）。

    v7.3.21（决定 2）口径：优先用成团时按 DOI/arXiv/归一化标题算好的
    唯一论文数（unique_paper_count），注册与成团同一口径；老簇无该
    字段时回退标题去重口径（再退 source_ids 计数）。

    v7.3.29：原先该口径只内联在 _new_gates 内，compose 的 new 分支另用
    evidence_paper_count（_unique_papers 身份归并）二次判定，两套口径
    不同 → 同一簇门控放行、compose 判不足而被静默丢弃（生产实测
    cl_20260816_a21e61：门控 3 ≥ 3，compose 计 2 < 3）。抽出后两处
    共用同一判定，杜绝结论相反。
    """
    up = cluster.get("unique_paper_count")
    if isinstance(up, int) and up > 0:
        return up
    titles = set()
    for m in cluster.get("member_summaries") or []:
        t = re.sub(r"\s+", " ", str(m.get("title", "")).strip().lower())[:80]
        if t:
            titles.add(t)
    return len(titles) or len(cluster.get("member_source_ids", []))


def _new_gates(
    cluster: Dict[str, Any],
    proposals: List[Dict[str, Any]],
    scope_terms: List[str],
    quota_left: int,
) -> tuple:
    """new 动作门槛（v6.9.18 四重 → v6.10.37 七重）。

    Returns:
        (ok, reason)。ok=False 时簇路由为 defer（保持 open 继续积累）。
    """
    # 关 1：成员独立性（v6.10.37 从"source_ids 计数"升级）——同标题双
    # 版本（arXiv 预印本 + 期刊发表版）不算两篇独立文献。09-21 退回的
    # 6 簇中 5 个的"3 篇成员"去重后仅 2 篇独立（凑数虚增满足门槛）。
    # v7.3.21（决定 2）：优先用成团时按 DOI/arXiv/归一化标题算好的唯一
    # 论文数，注册与成团同一口径；老簇无该字段时回退标题去重口径。
    # v7.3.29：口径抽成 _gate_member_count()，供 compose 复用同一判定，
    # 避免门控/compose 两套口径导致同一簇在两处结论相反。
    members = _gate_member_count(cluster)
    if members < NEW_MIN_MEMBERS:
        return False, f"独立成员 {members} < {NEW_MIN_MEMBERS}，继续积累"
    # v7.3.22（用户裁决 1）：跨领域簇在立题取料时按成员级核心范式过滤
    # （core_theme_hit），金融/保险/量子计算算法/通用 ML 等成员不得进入
    # 设想证据链；过滤后不足 3 篇唯一论文 → 降级补充文献池，不立题
    # （成员仍可经 merge/expansion 挂载到已有课题）。
    if cluster.get("cross_domain"):
        from .clusters import evidence_paper_count
        core_n = evidence_paper_count(cluster)
        if core_n < NEW_MIN_MEMBERS:
            return False, (f"跨领域簇核心范式成员 {core_n} < {NEW_MIN_MEMBERS}，"
                           "降级补充文献池（不立题）")
    if cluster.get("distilled_by") != "llm":
        return False, "知识卡非 LLM 提炼（缺失或降级拼接）"
    if quota_left <= 0:
        return False, f"本周 new 配额已用尽（上限 {NEW_WEEKLY_QUOTA}）"
    cluster_text = " ".join([
        cluster.get("title", ""), cluster.get("summary", ""),
        " ".join(cluster.get("keywords", [])),
    ])
    from .sources import scope_hit, core_theme_hit
    if scope_hit(cluster_text, scope_terms) is None:
        return False, "簇主题与方向词表无交集"
    # v6.9.22: 核心范式强制关——开新课题必须命中"强场操控"或
    # "HHG/超快光谱测量"范式词。仅命中材料/物态语境词（自旋/能谷/
    # 激子/交变磁等）的纯静态凝聚态簇不够格注册新课题，只能通过
    # merge/expansion 注入现有课题。08-16 实测：berry-mnps3 准静态
    # 滑移器件化课题即从此漏洞注册。
    if core_theme_hit(cluster_text) is None:
        return False, "仅语境词命中，未命中强场操控/超快测量核心范式"
    # v6.10.37 关 6：主线体系关——研究对象须为凝聚态/材料体系。
    # 范式词只约束手段不约束对象，自由电子束/气体介质光源/激光技术
    # 类簇字面命中"阿秒/强场"但主线外（09-21 用户裁决 6 退 1 接受，
    # 2 个主线外簇均栽在此关）。
    # v7.3.62 决策留档（2026-11-07 用户裁决）：cl_20261106_191cbc
    # （OPCPA 水窗 HHG 光源/阿秒表征，5 篇）继续排除，不改本关白名单。
    # 项目定位是"以 HHG 为探针研究材料量子性质"，自建光源选题相关度
    # 不足，用户对课题相关度要求从严；如需转向光源方向须显式升级裁决。
    if scope_hit(cluster_text, MATERIAL_SYSTEM_TERMS) is None:
        return False, "研究对象非凝聚态/材料体系（光源/束流/激光技术类，主线外）"
    # v6.10.37 关 7：知识卡完整关——research_gap 为空说明知识卡缺字段
    # 或降级拼接（09-21 退回 6 簇中 4 个 gap 为空；被接受的 ssh-weyl
    # 簇 gap 完整且具体）。研究缺口说不清的簇不足以支撑开题。
    if not str(cluster.get("research_gap") or "").strip():
        return False, "知识卡缺 research_gap（研究缺口不明，不足以支撑开题）"
    # v7.2.67: 重叠关前移至 _tournament_novelty_gate（Jaccard 预筛 +
    # pairwise LLM 锦标赛终审）——词袋 ≥0.50 直接判同质降级 merge（旧
    # 口径是 defer 闷着），其余交给 LLM 三判仲裁；在 run_input_topic_match
    # 的 new 分支先于本门槛执行，走到这里时同质性已被终审排除。
    return True, "成员/知识卡/方向/范式/体系/缺口/配额七关全过（重叠关已前移锦标赛终审）"


def _defer_signal(reason: str) -> str:
    """v6.10.7: 从 defer 理由提取信号——区分"高相关待积累"与"主题不对齐"。

    accumulate（继续积累）= 成员不足但方向相关（"成员 N < 3"），
    是 stale 清理的保护对象。注意 off_topic 理由也常含"继续积累"
    字样（实测 09-12："主题不对齐，应继续积累等待范式嫁接"、"判
    defer 继续积累"），关键词判定会把 3 个不对齐簇误标 accumulate——
    必须用成员数正则精确匹配。其余 defer（含配额尽/知识卡缺失/
    方向不相关）一律 off_topic 保守处理，不确定的不保护，避免
    僵尸簇借信号逃逸清理。

    v7.3.29 修复（2026-11-05 00h 健康检查实测）：v7.3.22 新增的
    跨领域降级理由「跨领域簇核心范式成员 N < 3，降级补充文献池
    （不立题）」结构上同样是"成员 N < 3"，被原正则误判为
    accumulate → 簇拿到 stale 清理保护 → 超期不被 close_stale_clusters
    关闭、反而打 pending_human_review 进人工队列（cluster_stale），
    与"降级补充文献池、不立题"的处置语义相反：这类簇本就不该
    立题，攒成员也无意义（补的是跨领域成员，不是核心范式成员）。
    生产实测 3 个 open 跨领域簇（cl_20261029_5cb557/f7b6a8/53498e）
    过滤后核心范式唯一论文数 = 2/0/0，三者信号全部误标 accumulate。
    修复 = 降级补充文献池语义优先判定，不落入 accumulate 保护。
    """
    import re as _re
    text = reason or ""
    # v7.3.29：跨领域簇降级补充文献池 = 方向明确不对齐，不享受
    # accumulate 的 stale 保护（该语义优先级高于成员数正则）。
    if "降级补充文献池" in text:
        return "off_topic"
    if _re.search(r"成员\s*\d+\s*<\s*3", text):
        return "accumulate"
    return "off_topic"


def run_input_topic_match(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """课题判断：open 簇 vs 全阶段课题，产出路由决策（merge/new/expansion/defer）。

    两级判断：Jaccard 预筛 top-3 候选 → LLM 仲裁（概念级重合判断，
    词袋测不出的同机制不同术语场景）。LLM 不可用时回退纯 Jaccard
    阈值（0.35，与旧口径一致）。
    v6.9.18: new 动作加四重门槛（成员数/LLM 知识卡/方向相关/不与
    现有课题重叠）+ 周配额；不达标的簇路由 defer（保持 open 继续
    积累，不丢失），取代旧版"低置信一律按新课题处理"的泛滥路径。
    """
    from .clusters import load_clusters, save_clusters
    from .sources import load_scope_terms

    if dry_run:
        return {"success": True, "routes": 0, "dry_run": True, "message": "dry-run 跳过课题匹配"}

    registry = load_clusters()
    open_c = [c for c in registry.get("clusters", []) if c.get("status") == "open"]
    if not open_c:
        _ensure_input_dir()
        save_json(WEEKEND_INPUT_DIR / f"routes-{now_utc()[:10]}.json", {"routes": []})
        return {"success": True, "routes": 0, "message": "无待路由簇"}

    proposals = _load_all_stage_proposals()
    scope_terms = load_scope_terms()
    quota_left = NEW_WEEKLY_QUOTA
    # 配额优先给成员最多的簇：先按成员数降序处理，先到先得
    open_c.sort(key=lambda c: len(c.get("member_source_ids", [])), reverse=True)
    pool_marked = False

    routes = []
    for c in open_c:
        # v6.9.18 补：运维簇前置 defer（不进课题路由，保持 open 无害积累）
        if _is_ops_cluster(c):
            routes.append({
                "cluster_id": c["cluster_id"],
                "cluster_title": c.get("title", ""),
                "action": "defer",
                "target_id": None,
                "reason": "运维内容簇（简报/cron/系统元数据），不参与课题路由",
                "members": len(c.get("member_source_ids", [])),
                "candidates": [],
            })
            continue

        cluster_text = " ".join([c.get("title", ""), c.get("summary", ""), " ".join(c.get("keywords", []))])
        scored = sorted(
            (
                {"proposal": p, "score": _jaccard_similarity(cluster_text, p["title"] + " " + p["text"])}
                for p in proposals
            ),
            key=lambda x: x["score"],
            reverse=True,
        )[:8]  # v6.9.58: top-3→top-8——08-22 实测交变磁体簇的语义相关课题
        # （berry-mnps3，标题字面重叠低）被 top-3 截断排除在 LLM 仲裁视野外，
        # LLM 据"三个不相关课题"误判 new，与 idea_generator 路径重复立项
        # （general-new-idea-20260822 vs berry-mnps3 同方向）。仲裁候选多
        # 几行成本可忽略，截断漏检代价是整个重复课题。

        action, target_id, reason = None, None, ""
        merge_target = None  # v7.2.67: 锦标赛降级时的同质课题标注
        best = scored[0] if scored else None
        if best and best["score"] >= 0.35:
            # 高置信重合：archived 课题 → expansion（文献挂载），
            # 活跃课题 → merge（信息注入）
            if best["proposal"]["status"] == "archived":
                action, target_id = "expansion", best["proposal"]["proposal_id"]
            else:
                action, target_id = "merge", best["proposal"]["proposal_id"]
            reason = f"Jaccard {best['score']:.2f}"
        else:
            # 中低置信：LLM 仲裁（top-3 候选一起判断，概念级重合）
            action, target_id, reason = _llm_arbitrate_cluster(c, scored)
            if action == "new":
                # v7.2.67 锦标赛制新颖性终审：Jaccard 词袋分数测不出
                # 同机制不同术语的同质题（order↔new 同题 65-70% 未检
                # 出），pairwise LLM 仲裁做终审。任一判「同质」→ new
                # 降级走既有 merge 路径（archived 同质课题挂文献为
                # expansion），不占 new 配额。
                t_action, t_target, t_reason = _tournament_novelty_gate(c, proposals)
                if t_action == "merge":
                    t_status = next(
                        (p["status"] for p in proposals if p.get("proposal_id") == t_target),
                        None,
                    )
                    if t_status == "archived":
                        action, target_id = "expansion", t_target
                    else:
                        action, target_id = "merge", t_target
                    merge_target = t_target
                    reason = f"锦标赛终审判同质，new 降级：{t_reason}"
                else:
                    # LLM 判新也要过门槛（弱簇/离题/配额尽 → defer）
                    ok, gate_reason = _new_gates(c, proposals, scope_terms, quota_left)
                    if ok:
                        quota_left -= 1
                        # t_reason 并入 reason：锦标赛结论（N 对全部正交/
                        # 互补 或 fail-open 回退）随路由落盘，可观测
                        reason = f"{reason}；{gate_reason}；{t_reason}"
                    else:
                        action, target_id = "defer", None
                        reason = f"new 门槛未过：{gate_reason}"
                        # v7.3.22（用户裁决 1）：跨领域簇核心范式过滤后
                        # 不足 3 篇唯一 → 标记补充文献池（不立题，保留簇与
                        # 成员供 merge/expansion 使用）
                        if "降级补充文献池" in gate_reason:
                            c["supplementary_pool"] = True
                            c["supplementary_pool_at"] = now_utc()
                            pool_marked = True

        routes.append({
            "cluster_id": c["cluster_id"],
            "cluster_title": c.get("title", ""),
            "action": action or "new",
            "target_id": target_id,
            # v7.2.67: 锦标赛判同质降级时标注 merge_target（观测用，
            # compose 仍按 action/target_id 走既有落地路径）
            "merge_target": merge_target,
            "reason": reason,
            "signal": _defer_signal(reason) if (action or "new") == "defer" else None,
            "members": len(c.get("member_source_ids", [])),
            "candidates": [
                {"proposal_id": s["proposal"]["proposal_id"], "score": round(s["score"], 3)}
                for s in scored
            ],
        })

    # v6.10.7: defer 信号回写簇注册表——accumulate（高相关等第 3 篇）
    # 是 stale 清理的保护依据（close_stale_clusters），不回写则保护分支
    # 永远拿不到信号，窄方向簇会在 4 周 stale 线被饿死（积累作废）。
    _signal_map = {r["cluster_id"]: r.get("signal") for r in routes if r.get("signal")}
    if _signal_map or pool_marked:
        for c in registry.get("clusters", []):
            sig = _signal_map.get(c.get("cluster_id", ""))
            if sig:
                c["route_signal"] = sig
                c["route_signal_at"] = now_utc()
        save_clusters(registry)

    _ensure_input_dir()
    routes_path = WEEKEND_INPUT_DIR / f"routes-{now_utc()[:10]}.json"
    save_json(routes_path, {"routes": routes})
    # v6.10.30: 记录产物路径到 state——compose 与 topic_match 可能跨 UTC
    # 午夜执行（20 分钟 worker 间隔），compose 按当日日期读 routes 会读
    # 到不存在的文件（09-19 实测：topic_match 23:41 写 routes-09-19，
    # compose 00:00 读 routes-09-20 落空，CrSb expansion 路由滞留未消费、
    # ideas actions=0）。与 v6.9.98 deep_digest 的 last_summaries_path
    # 同款修复：下游按 state 记录路径读取，跨天不错位。
    ir = state.setdefault("input_round", {})
    try:
        ir["last_routes_path"] = str(routes_path.relative_to(PROJECT_ROOT))
    except ValueError:
        ir["last_routes_path"] = str(routes_path)
    from collections import Counter
    return {
        "success": True,
        "routes": len(routes),
        "actions": dict(Counter(r.get("action") for r in routes)),
    }


def _llm_arbitrate_cluster(
    cluster: Dict[str, Any],
    scored: List[Dict[str, Any]],
) -> tuple:
    """LLM 仲裁簇与课题的关系（Jaccard 中低置信时）。

    v6.9.18 补：仲裁选项加 defer（非研究内容/质量不足不路由），
    并向 LLM 说明 new 的实际后果（注册新研究课题进人工立项队列）
    ——08-16 复跑实测旧三选项下运维簇只能被塞给 new。

    Returns:
        (action, target_id, reason)。LLM 不可用/失败 → ("new", None, "无匹配")。
    """
    if not is_llm_available():
        return "new", None, "Jaccard 低置信且 LLM 不可用，按新课题处理"

    cands = "\n".join(
        f"- [{s['proposal']['status']}] {s['proposal']['proposal_id']}: "
        f"{s['proposal']['title']}（相似度 {s['score']:.2f}）摘要：{s['proposal']['text'][:300]}"
        for s in scored
    ) or "（无候选课题）"

    system = (
        "你是林赛，判断一个知识簇与候选课题的关系。merge=信息属于该课题应融合；"
        "expansion=主题相邻应把文献挂为补充信息源；new=值得开创新研究课题"
        "（将注册为新课题并进入人工立项队列，需具备明确科学问题）；"
        "defer=非研究内容（系统运维/流程记录）或科学含量不足，不应路由。"
        "【核心主题约束（v6.9.22）】课题组核心范式是强场超快光学："
        "要么通过强场/THz 光场实现物性操控（强场驱动、Floquet 工程），"
        "要么用高次谐波光谱/超快光谱实现超快测量（HHG 谱学、泵浦-探测）。"
        "若知识簇不含任何强场操控或超快测量维度（纯准静态凝聚态物性、"
        "器件工程、静态第一性原理计算），不得判 new——可判 defer（主题"
        "不对齐，继续积累等待范式嫁接）或 merge/expansion（注入现有课题）。"
        '输出 JSON：{"action": "merge|expansion|new|defer", '
        '"target_id": "课题id或null", "reason": "一句话"}。'
    )
    user = (
        f"知识簇：{cluster.get('title', '')}\n"
        f"簇摘要：{cluster.get('summary', '')[:600]}\n"
        f"关键词：{', '.join(cluster.get('keywords', []))}\n\n"
        f"候选课题：\n{cands}"
    )
    verdict = _llm_json(system, user, timeout=90)
    if isinstance(verdict, dict) and verdict.get("action") in ("merge", "expansion", "new", "defer"):
        action = verdict["action"]
        target = verdict.get("target_id")
        if action in ("merge", "expansion") and not target:
            # action 指向课题但未给 id：回退最高分候选
            if scored:
                target = scored[0]["proposal"]["proposal_id"]
            else:
                action = "new"
                target = None
        if action == "defer":
            target = None
        return action, target, verdict.get("reason", "LLM 仲裁")
    return "new", None, "LLM 仲裁失败，按新课题处理"


# ---------------------------------------------------------------------------
# v7.2.67: 锦标赛制新颖性终审（new 动作闸门）
# ---------------------------------------------------------------------------


def _tournament_pairwise_verdict(
    candidate_text: str,
    proposal_id: str,
    proposal_text: str,
    timeout: int = 90,
) -> Optional[Dict[str, str]]:
    """单课题对 pairwise 仲裁（一次调用只裁一对，控制成本）。

    通过 llm_gateway（_llm_json → llm_complete，prefer="weekend_input"）
    调 LLM，要求输出三判 JSON。本函数不做任何判定兜底——LLM 不可用/
    调用失败/输出不合法一律返回 None，fail-open 决策交给调用方。

    Returns:
        {"verdict": "同质|正交|互补", "reason": "..."}；失败 → None。
    """
    if not is_llm_available():
        return None
    system = (
        "你是林赛，负责新研究课题立项前的新颖性终审（锦标赛制 pairwise 对比仲裁）。\n"
        "给定候选新课题与一个现有课题的核心设想文本，从科学问题、研究方法、"
        "材料体系三个维度判断二者关系，三选一：\n"
        "同质 = 研究问题/方法/材料体系实质重叠，二者都立项会在评审时自撞"
        "（同一创新点撞车）；\n"
        "正交 = 研究问题与方法均不重叠，相互独立；\n"
        "互补 = 有可挂靠的信息源交集（同领域文献/共用技术），但科学问题"
        "独立成立，不构成评审自撞。\n"
        "判定纪律：词面相似不等于同质——不同术语可指同一机制，相同术语"
        "可指不同问题，以三个维度的实质重叠为准。\n"
        '只输出 JSON：{"verdict": "同质|正交|互补", "reason": "一句话依据"}，'
        "verdict 必须是三值之一。"
    )
    user = (
        f"【候选新课题（知识簇设想）】\n{(candidate_text or '')[:600]}\n\n"
        f"【现有课题 {proposal_id}】\n{(proposal_text or '')[:600]}\n\n"
        "判断两个设想的关系并输出 JSON。"
    )
    verdict = _llm_json(system, user, timeout=timeout)
    if isinstance(verdict, dict) and verdict.get("verdict") in TOURNAMENT_VERDICTS:
        return {"verdict": verdict["verdict"], "reason": str(verdict.get("reason", ""))[:200]}
    return None


def _tournament_novelty_gate_for_texts(
    candidate_text: str,
    proposals: List[Dict[str, Any]],
) -> tuple:
    """锦标赛制新颖性闸门（通用引擎，v7.2.67）。

    流程：
        1. Jaccard 预筛：与全部现有课题打分取 top-TOURNAMENT_TOP_K 最相
           似候选（预筛省调用）；最高分 ≥ 0.50（IDEA_HOLD_SIMILARITY 口
           径）→ 直接判同质，不调 LLM。
        2. 锦标赛：对每个候选做 pairwise LLM 仲裁（三判：同质/正交/互
           补），任一「同质」→ new 降级 merge（目标=该课题）；全部
           「正交/互补」→ 放行 new。
        3. fail-open：LLM 不可用/单对仲裁失败 → 记 warning 并按旧
           Jaccard 判定该对（预筛已保证 < 0.50 → 不重叠），不阻塞周末
           流水线。

    Args:
        candidate_text: 候选新课题的核心设想文本。
        proposals: [{"proposal_id", "status", "text"}] 形式的现有课题。

    Returns:
        (action, merge_target_id, reason)：action ∈ ("new", "merge")。
    """
    if not proposals:
        return "new", None, "无现有课题，天然新颖"
    try:
        from idea_generator import IDEA_HOLD_SIMILARITY
    except Exception:
        IDEA_HOLD_SIMILARITY = 0.50
    scored = sorted(
        (
            {"proposal": p, "score": _jaccard_similarity(candidate_text, p.get("text", ""))}
            for p in proposals
        ),
        key=lambda x: x["score"],
        reverse=True,
    )[:TOURNAMENT_TOP_K]
    best = scored[0]
    # 预筛硬线：≥ hold 线无需 LLM，直接同质（省调用 + 保留旧口径阈值）
    if best["score"] >= IDEA_HOLD_SIMILARITY:
        return "merge", best["proposal"].get("proposal_id"), (
            f"Jaccard {best['score']:.2f} ≥ {IDEA_HOLD_SIMILARITY}，"
            f"预筛直接判同质（未调 LLM）"
        )
    # 锦标赛：逐对 pairwise 仲裁（一次调用只裁一对）
    if not is_llm_available():
        if _log:
            _log.warning("锦标赛仲裁 LLM 不可用，回退旧 Jaccard 判定（fail-open 不阻塞流水线）")
        return "new", None, "锦标赛 LLM 不可用，回退旧 Jaccard 判定（top 候选全部 < 0.50，放行）"
    judged = 0
    for s in scored:
        verdict = _tournament_pairwise_verdict(candidate_text, s["proposal"].get("proposal_id", "?"), s["proposal"].get("text", ""))
        if verdict is None:
            if _log:
                _log.warning(
                    f"锦标赛 pairwise 仲裁失败（vs {s['proposal'].get('proposal_id')}），"
                    f"该对回退 Jaccard {s['score']:.2f} 判定（fail-open）"
                )
            continue
        judged += 1
        if verdict["verdict"] == "同质":
            return "merge", s["proposal"].get("proposal_id"), (
                f"pairwise 仲裁判同质（vs {s['proposal'].get('proposal_id')}，"
                f"Jaccard {s['score']:.2f}）：{verdict['reason']}"
            )
    if judged == 0:
        return "new", None, "锦标赛仲裁全部失败，回退旧 Jaccard 判定（top 候选全部 < 0.50，放行）"
    return "new", None, f"锦标赛 {judged} 对全部正交/互补，新颖性终审通过"


def _tournament_novelty_gate(
    cluster: Dict[str, Any],
    proposals: List[Dict[str, Any]],
) -> tuple:
    """簇版锦标赛闸门（topic_match 的 new 动作终审入口，v7.2.67）。

    组装知识簇设想文本（title+summary+keywords）与全阶段课题清单
    （text = title + 简报文本），交通用引擎 _tournament_novelty_gate_for_texts。

    Returns:
        (action, merge_target_id, reason)：action ∈ ("new", "merge")。
    """
    cluster_text = " ".join([
        cluster.get("title", ""), cluster.get("summary", ""),
        " ".join(cluster.get("keywords", [])),
    ])
    shaped = [
        {
            "proposal_id": p.get("proposal_id", ""),
            "status": p.get("status", ""),
            "text": f"{p.get('title', '')} {p.get('text', '')}",
        }
        for p in proposals
    ]
    return _tournament_novelty_gate_for_texts(cluster_text, shaped)


def _group_merge_routes(
    merge_routes: List[Dict[str, Any]],
    cluster_index: Dict[str, Dict[str, Any]],
    threshold: float = 0.30,
) -> Dict[str, str]:
    """同目标课题的 merge 簇连通分组（v6.9.18）。

    按目标课题分组后，组内只保留一个"主簇"（成员最多）走 enrich
    知识卡注入，其余簇只挂信息源——根治 08-16 实测 BSV 课题被 6
    个同主题变体簇重复注入（enrich 句级去重对同义不同措辞的知识
    卡无能为力）。

    Returns:
        {cluster_id: 同组主簇 id}——非主簇映射到主簇 id。
    """
    from .clusters import cluster_similarity

    leader: Dict[str, str] = {}
    groups_by_target: Dict[str, List[Dict[str, Any]]] = {}
    for r in merge_routes:
        c = cluster_index.get(r.get("cluster_id", ""))
        target = r.get("target_id", "")
        if not c or not target:
            continue
        groups = groups_by_target.setdefault(target, [])
        placed = False
        for g in groups:
            if cluster_similarity(c, g["leader"]) >= threshold:
                leader[c["cluster_id"]] = g["leader"]["cluster_id"]
                # 主簇取成员更多者（组内重组时更新 follower 映射）
                if len(c.get("member_source_ids", [])) > len(g["leader"].get("member_source_ids", [])):
                    leader[g["leader"]["cluster_id"]] = c["cluster_id"]
                    g["leader"] = c
                placed = True
                break
        if not placed:
            leader[c["cluster_id"]] = c["cluster_id"]
            groups.append({"leader": c})
    return leader


def _routes_path_for_compose(state: Dict[str, Any]) -> Path:
    """compose 读取 routes 的路径选择（v6.10.30）。

    优先读 topic_match 写入 state 的 last_routes_path，回退当日文件名——
    topic_match 与 compose 跨 UTC 午夜执行时按各自当日日期拼接文件名
    会错位（compose 读不到刚写出的 routes，空路由落空：09-19 实测
    ideas actions=0）。与 v6.9.98 deep_digest 的 last_summaries_path
    同款修复。
    """
    ir = state.get("input_round") or {}
    rel = str(ir.get("last_routes_path", "") or "")
    if rel:
        return PROJECT_ROOT / rel
    return WEEKEND_INPUT_DIR / f"routes-{now_utc()[:10]}.json"


def _enrich_idea_six_modules(idea: Dict[str, Any], cluster: Dict[str, Any]) -> Dict[str, Any]:
    """v6.10.34: compose new 路由的六模块补全（research-proposal 模板注入）。

    背景：v6.10.31 把六模块模板注入 idea_generator 的自动/手动 prompt，
    但当前全自动链路的设想主路径是知识簇链路（topic_match → compose
    new → register_from_idea），不经过 _build_idea_prompt——自动注册的
    新课题只有 title/background/gap 等基础字段，立项决策包（dossier）
    的新章节（技术路线/验证方案/与参考工作的区别）永远为空。本函数在
    compose new 落地前按模板补全三个增量字段：
      - route：技术路线分步（含最后一步验证）
      - validation：验证判据 + 替代解释排除
      - comparison：与参考工作的区别（core_refs/table/increment/
        boundary/depends）——增量贡献必须说清，防"换皮课题"
    约束：LLM 不可用/失败 → 返回原 idea（降级不阻塞链路）；只补增量
    字段不重写既有 title/background（防漂移）；清洗复用
    idea_generator._coerce_idea_fields（研究管线内复用，导入失败降级）。
    """
    if not is_llm_available():
        return idea
    payload = _llm_json(
        "你是林赛，为即将注册的新研究课题补全结构化字段。"
        "只输出 JSON 对象，不要重写已有字段；增量贡献必须相对参考工作"
        "说清'新在哪里'，只换材料不换科学问题不算贡献。",
        "课题标题：" + idea.get("title", "")
        + "\n知识卡综合：" + (cluster.get("summary", "") or "")[:500]
        + "\n研究缺口：" + (cluster.get("research_gap", "") or "")[:200]
        + "\n开放问题：" + "；".join(cluster.get("open_questions", []) or [])[:300]
        + "\n成员文献：" + "、".join(
            m.get("title", "") for m in (cluster.get("member_summaries") or [])[:8])
        + '\n\n输出 JSON（仅三个字段）：{"route": ["步骤一：...（具体方法）", '
        '"步骤二：...", "步骤三：...（验证）"], "validation": "验证判据+替代解释排除", '
        '"comparison": {"core_refs": ["真实存在的核心文献（成员列表里的，'
        '不确定给空数组）"], "table": [{"dimension": "体系/物理量/调控手段", '
        '"existing": "已有做法", "ours": "本课题做法"}], '
        '"increment": ["增量贡献"], "boundary": ["不涉及/限制"], '
        '"depends": ["依赖的已有工作"]}}',
        timeout=120,
    )
    if not isinstance(payload, dict):
        return idea
    # 只取三字段（防 LLM 越权重写 title 等）
    for k in ("route", "validation", "comparison"):
        if k in payload:
            idea[k] = payload[k]
    try:
        from idea_generator import _coerce_idea_fields
        idea = _coerce_idea_fields(idea)
    except Exception:
        pass
    return idea


def run_input_compose(state: Dict[str, Any], job: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """路由落地：簇融入课题/注册新课题/挂载补充信息源（进下周工作流）。

    v6.9.12 三条路由落地（取代旧 compose 依赖 decisions 且 expansion
    空转）：
    - new：register_from_idea 注册 drafts 新课题
    - merge：enrich_from_idea 注入活跃课题 + 文献挂载到 02_literature
    - expansion：文献挂载到课题 02_literature/supplementary-sources-{date}.json
      （references 校验步骤与下周 writer 可读）
    全部路由完成后簇标 linked，不再吸收新成员。
    v6.9.18:
    - defer 路由不落地（簇保持 open 继续积累，等待成员/知识卡成熟）；
    - 同目标课题的多个 merge 簇先连通分组，组内只有主簇注入知识卡，
      其余簇只挂信息源（防同主题变体簇重复注入）；
    - 信息源挂载改用簇内 member_summaries（跨周可用），修复旧实现
      依赖当天 summaries 文件导致跨周成员挂载必失败（08-16 实测
      expansion 成功率 12/58）。
    """
    from proposal_lifecycle import ProposalLifecycle
    from .clusters import load_clusters, mark_linked, save_clusters

    # v6.10.30: 优先读 topic_match 记录的 routes 路径（state 记录），
    # 回退当日文件名——跨 UTC 午夜执行时按各自当日日期拼接会错位。
    routes_path = _routes_path_for_compose(state)
    routes = load_json(routes_path, default={}).get("routes", [])

    # 摘要索引：source_id → 摘要条目（member_summaries 缺 path 的旧簇回退用）
    # v6.9.98: 改读最近一轮 deep_digest 产物（state 记录路径，多轮/跨天不错位）
    summaries = _load_round_summaries(state)
    summary_index = {s.get("source_id", ""): s for s in summaries if isinstance(s, dict)}

    registry = load_clusters()
    cluster_index = {c.get("cluster_id"): c for c in registry.get("clusters", [])}

    # 同目标 merge 簇分组：非主簇只挂信息源不重复注入
    merge_routes = [r for r in routes if r.get("action") == "merge" and r.get("target_id")]
    leader_map = _group_merge_routes(merge_routes, cluster_index)

    lc = ProposalLifecycle()
    # v8.0.0: topics 模式下 new/merge 落地到 research_topics（legacy 仅回滚用）
    use_topics = False
    try:
        from topic_pipeline.weekend_bridge import (
            enrich_from_idea_v8,
            register_from_idea_v8,
            weekend_register_mode,
        )
        use_topics = weekend_register_mode() == "topics"
    except Exception:
        use_topics = False
    actions = []
    for r in routes:
        cid = r.get("cluster_id", "")
        cluster = cluster_index.get(cid)
        if not cluster:
            continue
        action = r.get("action", "new")
        target_id = r.get("target_id")

        if action == "defer":
            # v6.9.18: 暂缓路由——簇保持 open 继续积累，不落地不标 linked
            actions.append({
                "cluster_id": cid, "cluster_title": cluster.get("title", ""),
                "action": "defer", "result": {"success": True, "action": "defer",
                                              "message": r.get("reason", "门槛未过，继续积累")},
            })
            continue

        is_merge_follower = (
            action == "merge"
            and leader_map.get(cid, cid) != cid
        )
        if is_merge_follower:
            # 同组非主簇：只挂信息源，不重复注入知识卡
            if dry_run:
                result = {"action": "merge_follower", "target_id": target_id, "dry_run": True}
            else:
                written = _write_supplementary_sources(target_id, cluster, summary_index)
                result = {"success": written, "action": "merge_follower", "target_id": target_id,
                          "message": "同组非主簇：仅挂载信息源（知识卡由主簇注入）"}
                if written:
                    mark_linked(registry, cid, target_id or "")
            actions.append({
                "cluster_id": cid, "cluster_title": cluster.get("title", ""),
                "action": "merge_follower", "result": result,
            })
            continue

        idea = {
            "title": cluster.get("title", ""),
            "background": f"知识簇综合：{cluster.get('summary', '')}",
            "gap": "；".join(cluster.get("open_questions", []) or []) or cluster.get("summary", "")[:200],
            "content": cluster.get("member_source_ids", []),
            "approach": "待进一步细化",
            "innovations": cluster.get("open_questions", []) or [cluster.get("summary", "")[:120]],
            "sources": [
                {"title": m.get("title", sid), "source_type": "weekend_cluster"}
                for sid, m in ((ms.get("source_id", ""), ms) for ms in cluster.get("member_summaries", []))
            ],
            "keywords": cluster.get("keywords", []),
            "cluster_id": cid,  # v6.9.18: enrich 注入标题带簇 ID 防去重误删
            "generated_at": now_utc(),
            "reliability": RELIABILITY_DERIVED,
        }

        if dry_run:
            result = {"action": action, "target_id": target_id, "dry_run": True}
        elif action == "new":
            # v7.3.22（用户裁决 1）：立题证据链按成员级核心范式过滤
            # （cross_domain 簇剔除金融/保险/量子算法/通用 ML 等成员；
            # 正常簇原样）。过滤后不足 3 篇唯一 → 降级补充文献池不立题。
            #
            # v7.3.29 修复（2026-11-05 00h 健康检查实测）：原实现对
            # **所有**簇（不只 cross_domain）用 evidence_paper_count 判
            # 降级，而该口径是 _unique_papers 身份归并（DOI/arXiv/归一标题
            # 任一相同即同篇），门控 _new_gates 用的却是 unique_paper_count
            # 或标题去重——两套口径不同 → 同一簇在门控判定"成员够"、
            # 到 compose 却判"不足 3 篇"而被静默丢弃（success=False，
            # 不注册、不可见）。生产实测 cl_20260816_a21e61（非跨领域，
            # 3 条成员中 2 条同 arXiv 2403.02188）：门控 3 ≥ 3 放行，
            # compose 计 2 < 3 → 静默丢弃，理由串还误写成"跨领域簇…
            # 降级补充文献池"（该簇 cross_domain=None，语义与事实均错）。
            # 修复 = compose 与门控同口径（先应用门控已判定的计数），
            # 且降级语义只对 cross_domain 簇成立。
            from .clusters import evidence_paper_count, idea_evidence_members
            evidence_members = idea_evidence_members(cluster)
            gate_members = _gate_member_count(cluster)
            if cluster.get("cross_domain"):
                core_n = evidence_paper_count(cluster)
                gate_members = core_n
            else:
                # 正常簇：门控口径为准（成团时算好的 unique_paper_count，
                # 或标题去重回退），不再用身份归并口径二次否决。
                core_n = gate_members
            if core_n < NEW_MIN_MEMBERS:
                cluster["supplementary_pool"] = True
                cluster["supplementary_pool_at"] = now_utc()
                msg = (f"跨领域簇核心范式成员 {core_n} < {NEW_MIN_MEMBERS}，"
                       "降级补充文献池（不立题）") if cluster.get("cross_domain") else (
                       f"簇成员 {core_n} < {NEW_MIN_MEMBERS}，"
                       "成员唯一论文去重后不足，不立题")
                result = {
                    "success": False, "action": "supplementary_pool",
                    "message": msg,
                }
            else:
                enriched = cluster
                if cluster.get("cross_domain"):
                    # 仅 cross_domain 簇改写证据链；正常簇保持原 content/sources
                    idea["content"] = [m.get("source_id", "") for m in evidence_members]
                    idea["sources"] = [
                        {"title": m.get("title", m.get("source_id", "")),
                         "source_type": "weekend_cluster"}
                        for m in evidence_members
                    ]
                    enriched = dict(cluster, member_summaries=evidence_members)
                # v6.10.34: new 落地前六模块补全——注册进人工立项队列的课题
                # 带技术路线/验证方案/与参考工作的区别，dossier 新章节有内容
                idea = _enrich_idea_six_modules(idea, enriched)
                if use_topics:
                    # v8.0.0: 注册为问题候选（research_topics/questions/，A2 新颖性硬门）
                    result = register_from_idea_v8(idea)
                else:
                    result = lc.register_from_idea(idea, project_type="general")
        elif action == "merge" and target_id:
            if use_topics:
                result = enrich_from_idea_v8(target_id, idea)
            else:
                result = lc.enrich_from_idea(target_id, idea)
            result = dict(result) if isinstance(result, dict) else {"success": False}
            result["supplementary_written"] = _write_supplementary_sources(target_id, cluster, summary_index)
        elif action == "expansion" and target_id:
            written = _write_supplementary_sources(target_id, cluster, summary_index)
            result = {"success": written, "action": "expansion", "target_id": target_id,
                      "message": "补充信息源已挂载到课题文献目录"}
        else:
            result = {"action": action, "target_id": target_id, "message": "路由目标缺失，跳过"}

        if not dry_run and result.get("success") and action != "new":
            mark_linked(registry, cid, result.get("proposal_id") or target_id or "")
        elif not dry_run and action == "new" and result.get("success"):
            mark_linked(registry, cid, result.get("proposal_id", ""))

        actions.append({"cluster_id": cid, "cluster_title": cluster.get("title", ""), "action": action, "result": result})

    if not dry_run:
        save_clusters(registry)
        save_json(WEEKEND_INPUT_DIR / f"ideas-{now_utc()[:10]}.json", {"generated_at": now_utc(), "actions": actions})

    return {"success": True, "ideas_count": len(actions)}


def _write_supplementary_sources(
    proposal_id: str,
    cluster: Dict[str, Any],
    summary_index: Dict[str, Dict[str, Any]],
) -> bool:
    """把簇成员文献挂载为课题补充信息源（02_literature/ 下）。

    融入下周工作流的机制：references 校验步骤与 writer 以课题目录
    为输入域，补充清单落盘后即进入下一轮优化的可见范围。
    v6.9.18: 条目改从簇自身 member_summaries 构建（含跨周成员），
    当天 summaries 索引仅作旧簇（无 member_summaries）的回退——
    旧实现只用当天索引，跨周积累的簇成员全部查不到，08-16 实测
    expansion 挂载成功率 12/58。
    """
    from proposal_lifecycle import ProposalLifecycle

    # v8.0.0: 课题在 topics 域 → 挂载到 01_background/（新旧域统一按目标所在地）
    try:
        from topic_pipeline import state as _tp_state
        from topic_pipeline.weekend_bridge import write_supplementary_sources_v8
        if _tp_state.topic_dir(proposal_id):
            return write_supplementary_sources_v8(proposal_id, cluster, summary_index)
    except Exception:
        pass
    try:
        lc = ProposalLifecycle()
        prop_dir = lc._find_proposal_dir(proposal_id)
        if not prop_dir:
            return False
        lit_dir = prop_dir / "02_literature"
        lit_dir.mkdir(parents=True, exist_ok=True)

        entries = []
        seen_sids = set()
        for ms in cluster.get("member_summaries", []):
            sid = ms.get("source_id", "")
            if not sid or sid in seen_sids:
                continue
            seen_sids.add(sid)
            entries.append({
                "source_id": sid,
                "title": ms.get("title", ""),
                "summary": ms.get("summary", ""),
                "path": ms.get("path", "") or summary_index.get(sid, {}).get("path", ""),
                "added_via": f"cluster:{cluster.get('cluster_id', '')}",
                "added_at": now_utc(),
            })
        # 旧簇回退：member_summaries 缺失时从当天摘要索引补
        if not entries:
            for sid in cluster.get("member_source_ids", []):
                s = summary_index.get(sid)
                if s:
                    entries.append({
                        "source_id": sid,
                        "title": s.get("title", ""),
                        "summary": s.get("summary", ""),
                        "path": s.get("path", ""),
                        "added_via": f"cluster:{cluster.get('cluster_id', '')}",
                        "added_at": now_utc(),
                    })
        if not entries:
            return False
        out = lit_dir / f"supplementary-sources-{now_utc()[:10]}.json"
        # v7.2.58 BUG-22 修复：同日多簇/多 orphan 挂载同一课题时，
        # 旧实现整文件覆盖（同日同名文件 → 后写覆盖先写），实测
        # orphan-route 单次路由 30 条只剩 1 条（29 条静默丢失）。
        # 改为「读旧文件 → 按 source_id 去重合并 → 整文件回写」，
        # 保留旧 entries 的 cluster_id 来源信息（clusters 列表）。
        existing = load_json(out, default={}) or {}
        merged: List[Dict[str, Any]] = []
        merged_sids = set()
        merged_fps = set()
        for e in (existing.get("entries") or []) + entries:
            if not isinstance(e, dict):
                continue
            sid = e.get("source_id", "")
            if sid:
                if sid in merged_sids:
                    continue
                merged_sids.add(sid)
            else:
                # v7.2.59 BUG-23 修复：无 source_id 的条目来自**其它写方**
                # （writer 的「引用回录」口径：ref_number/doi/arxiv/
                # bibliographic_entry），既不能按 source_id 去重，也不能
                # 丢弃——丢弃即静默丢失检索池元数据（10-30 实测 ssh-weyl
                # 14 条回录含 16 个 DOI 标识符被吞，其中 14 条参考文献
                # 失去溯源依据）。退化为按内容指纹去重以保幂等。
                fp = json.dumps(e, ensure_ascii=False, sort_keys=True)
                if fp in merged_fps:
                    continue
                merged_fps.add(fp)
            merged.append(e)
        cluster_ids = list(existing.get("clusters") or [])
        # 既有 cluster_id 保留为来源记录（旧文件无 clusters 字段时）
        prev_cid = existing.get("cluster_id", "")
        if prev_cid and prev_cid not in cluster_ids:
            cluster_ids.insert(0, prev_cid)
        cid = cluster.get("cluster_id", "")
        if cid and cid not in cluster_ids:
            cluster_ids.append(cid)
        payload = {
            "proposal_id": proposal_id,
            "cluster_id": cluster_ids[0] if cluster_ids else "",
            "clusters": cluster_ids,
            "entries": merged,
        }
        # 保留其它写方的顶层字段（如 description 溯源说明）
        for k, v in existing.items():
            if k not in payload and k not in ("entries", "cluster_id", "clusters"):
                payload[k] = v
        save_json(out, payload)
        return True
    except Exception as e:
        if _log:
            _log.warning(f"补充信息源挂载失败（{proposal_id}）: {e}")
        return False
