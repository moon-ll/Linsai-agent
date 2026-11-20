#!/usr/bin/env python3
"""研究设想生成器（v6.7.7）。

输入端核心：从文献简报、文献池、归档讨论和可靠知识库中识别研究缺口，
生成结构化研究设想，并与现有/已归档课题对比，决定：
- 注册为新 proposal（进入 drafts，等待人工确认）
- 融合到现有 optimizing/pending_review proposal（追加不覆盖，去重）
- 作为已归档课题的扩展建议（进入 memory/expansion-candidates.json）

两种入口：
    1. 周末自动：python3 scripts/idea_generator.py --auto
    2. 手动辅助：python3 scripts/idea_generator.py --manual "用量子光场驱动固体HHG"

产物：
    - research_proposals/_incoming/ideas-{date}.json
    - research_proposals/_incoming/weekly-ideas-review.md
    - memory/expansion-candidates.json（扩展建议）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import load_json, now_utc, save_json, safe_filename
from paths import PROJECT_ROOT

# 共享 LLM 网关
from llm_gateway import llm_complete, is_llm_available

try:
    from logger import get_logger
    _log = get_logger("idea_generator")
except Exception:
    _log = None

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

INCOMING_DIR = PROJECT_ROOT / "research_proposals" / "_incoming"
EXPANSION_CANDIDATES_PATH = PROJECT_ROOT / "memory" / "expansion-candidates.json"
PAPER_POOL_PATH = PROJECT_ROOT / "memory" / "paper-pool.json"
BRIEFING_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "reviews"
CAPTURES_DIR = PROJECT_ROOT / "knowledge" / "captures"
RAW_PAPERS_DIR = PROJECT_ROOT / "knowledge" / "raw" / "papers"
REFERENCES_NOTES_DIR = PROJECT_ROOT / "references" / "notes"
WIKI_CONCEPTS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "concepts"
WIKI_METHODS_DIR = PROJECT_ROOT / "knowledge" / "wiki" / "methods"

# 去重阈值
SIMILARITY_NEW_THRESHOLD = 0.35
DUPLICATE_THRESHOLD = 0.70

# 可靠性标签
RELIABILITY_RELIABLE = "reliable"
RELIABILITY_DERIVED = "derived"


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _log_info(msg: str) -> None:
    if _log:
        _log.info(msg)


def _log_warn(msg: str) -> None:
    if _log:
        _log.warning(msg)


def _ensure_dirs() -> None:
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    EXPANSION_CANDIDATES_PATH.parent.mkdir(parents=True, exist_ok=True)


def _read_text(path: Path, max_chars: int = 8000) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except Exception:
        return ""


def _tokenize(text: str) -> set:
    """简单中文/英文分词，用于相似度计算。"""
    if not text:
        return set()
    # 英文单词
    words = set(re.findall(r"[a-zA-Z]{3,}", text.lower()))
    # 中文字符（连续 2-8 个）
    words.update(re.findall(r"[\u4e00-\u9fff]{2,8}", text))
    return words


def _jaccard_similarity(a: str, b: str) -> float:
    """计算两段文本的 Jaccard 相似度。"""
    set_a = _tokenize(a)
    set_b = _tokenize(b)
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def _sentence_similarity(paragraph: str, existing_text: str) -> float:
    """计算段落与现有文本中各句子的最大相似度。"""
    if not existing_text:
        return 0.0
    # 简单按句号/换行分句
    sentences = re.split(r"[。\n]", existing_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if not sentences:
        return 0.0
    return max(_jaccard_similarity(paragraph, s) for s in sentences)


def _deduplicate_paragraphs(paragraphs: List[str], existing_text: str) -> List[str]:
    """过滤掉与现有文本重复的段落。"""
    result = []
    for p in paragraphs:
        if len(p.strip()) < 20:
            continue
        if _sentence_similarity(p, existing_text) < DUPLICATE_THRESHOLD:
            result.append(p)
    return result


# ---------------------------------------------------------------------------
# 源材料收集
# ---------------------------------------------------------------------------


def collect_source_materials(days: int = 7) -> Dict[str, Any]:
    """收集最近 N 天的源材料。"""
    cutoff = (datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)).isoformat()

    materials = {
        "briefings": [],
        "papers": [],
        "captures": [],
        "reference_notes": [],
        "wiki_concepts": [],
        "wiki_methods": [],
    }

    # 1. 文献简报
    if BRIEFING_DIR.exists():
        for f in sorted(BRIEFING_DIR.glob("briefing-*.md"), reverse=True):
            text = _read_text(f, 6000)
            if text:
                materials["briefings"].append({"path": str(f.relative_to(PROJECT_ROOT)), "text": text})

    # 2. 文献池
    if PAPER_POOL_PATH.exists():
        pool = load_json(PAPER_POOL_PATH, default={})
        for pid, info in list(pool.get("papers", {}).items())[:20]:
            materials["papers"].append({
                "title": info.get("title", ""),
                "abstract": info.get("abstract", "")[:800],
                "tags": info.get("tags", []),
            })

    # 3. 归档讨论
    if CAPTURES_DIR.exists():
        for f in sorted(CAPTURES_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]:
            text = _read_text(f, 3000)
            if text:
                materials["captures"].append({"path": str(f.relative_to(PROJECT_ROOT)), "text": text})

    # 4. 用户参考笔记
    if REFERENCES_NOTES_DIR.exists():
        for f in REFERENCES_NOTES_DIR.glob("*.md"):
            text = _read_text(f, 3000)
            if text:
                materials["reference_notes"].append({"path": str(f.relative_to(PROJECT_ROOT)), "text": text})

    # 5. 可靠知识库
    for d, key in [(WIKI_CONCEPTS_DIR, "wiki_concepts"), (WIKI_METHODS_DIR, "wiki_methods")]:
        if d.exists():
            for f in d.glob("*.md"):
                text = _read_text(f, 2000)
                if text:
                    materials[key].append({"path": str(f.relative_to(PROJECT_ROOT)), "text": text})

    return materials


# ---------------------------------------------------------------------------
# 缺口识别（轻量版）
# ---------------------------------------------------------------------------


def identify_gaps(materials: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从源材料中提取潜在研究缺口。

    当前实现：基于关键词模式匹配 + LLM 精炼。
    未来可接入 gap_analyzer.GapAnalyzer 做更系统的覆盖图分析。
    """
    gaps = []
    gap_keywords = [
        "缺口", "空白", "尚未", "unknown", "unclear", "unexplored", "bottleneck",
        "挑战", "局限", "不足", "缺乏", "待解决", "open question", "争议",
    ]

    # 从简报中提取含缺口信号的段落
    for b in materials.get("briefings", []):
        for line in b["text"].split("\n"):
            line = line.strip()
            if len(line) < 20:
                continue
            if any(kw in line.lower() for kw in gap_keywords):
                gaps.append({
                    "source": b["path"],
                    "text": line,
                    "reliability": RELIABILITY_RELIABLE,
                })

    # 从论文摘要中提取
    for p in materials.get("papers", []):
        abstract = p.get("abstract", "")
        if any(kw in abstract.lower() for kw in gap_keywords):
            gaps.append({
                "source": f"paper:{p.get('title', '')}",
                "text": abstract[:300],
                "reliability": RELIABILITY_RELIABLE,
            })

    # 去重
    seen = set()
    unique_gaps = []
    for g in gaps:
        key = g["text"][:60]
        if key not in seen:
            seen.add(key)
            unique_gaps.append(g)

    return unique_gaps[:30]


# ---------------------------------------------------------------------------
# 研究设想生成
# ---------------------------------------------------------------------------


def _build_idea_prompt(materials: Dict[str, Any], gaps: List[Dict[str, Any]]) -> str:
    """构建生成研究设想的 prompt。

    v6.10.31: 注入 research-proposal 技能六模块模板——新增 route
    （技术路线分步）/ validation（验证方案）/ comparison（与参考工作
    的区别）三个字段，content 强制方法具体化（禁止模糊表述），
    comparison 强制增量贡献/边界界定/依赖关系，防"换皮课题"。
    v7.0.0: 六模块方法论（背景动机/核心科学问题/route/validation/
    comparison/feasibility 的字段质量定义）收敛至 .hermes/skills/
    research-proposal/SKILL.md 三节，经 skill_loader 按节裁剪注入
    （fail-open：skill 缺失返回空串不阻塞）；prompt 只保留 JSON
    输出契约（字段名 + comparison 子结构，_coerce_idea_fields 的
    解析口径）与 defer 门槛等编排逻辑。
    """
    briefing_text = "\n\n".join(b["text"][:800] for b in materials.get("briefings", [])[:2])
    paper_text = "\n\n".join(
        f"- {p.get('title', '')}: {p.get('abstract', '')[:200]}"
        for p in materials.get("papers", [])[:5]
    )
    gap_text = "\n".join(f"- {g['text']}" for g in gaps[:5])

    # v7.0.0: 六模块方法论经 skill_loader 注入（fail-open 返回空串）
    try:
        from skill_loader import inject_block
        _rp_skill = inject_block(
            "research-proposal", ["三、课题设想六模块"], note="六模块齐备，缺一不可"
        )
    except Exception:
        _rp_skill = ""

    user_prompt = f"""请基于以下近期文献和讨论，生成 1-3 个高质量研究设想。

【近期文献简报】
{briefing_text}

【关键论文摘要】
{paper_text}

【识别到的研究缺口】
{gap_text}

{_rp_skill}
要求每个设想包含以下字段，输出为 JSON 数组（字段名与结构为输出契约，
各字段内容质量按上述 skill 六模块标准执行）：
- title: 课题标题（具体、准确）
- background: 研究背景和动机
- gap: 现存研究空白或瓶颈
- content: 拟开展研究内容（2-4 条）
- route: 技术路线分步（2-4 条）
- validation: 验证方案
- approach: 拟采用技术路线（一句话概述，与 route 一致）
- innovations: 创新点（2-3 条）
- comparison: 与参考工作的区别（核心模块，JSON 对象）：
{{
    "core_refs": ["具体文献标题（必须来自上述输入材料，作者/期刊真实可查）"],
    "table": [{{"dimension": "体系/物理量/调控手段/理论深度",
               "existing": "已有工作做法", "ours": "本设想做法"}}],
    "increment": ["增量贡献 2-3 条（相对已有工作新在哪里）"],
    "boundary": ["不涉及什么/研究限制（避免过度承诺）"],
    "depends": ["实现依赖哪些已有工作"]
}}
- sources: 来源文献/简报列表（每条含 title 和 source_type: briefing/paper/capture/wiki）
- keywords: 用于与现有课题对比的关键词列表（中英文术语）

注意：
1. 只生成基于上述材料可支撑的研究设想，不要杜撰。
2. 每个设想的 sources 必须具体对应到输入材料中的文献或简报，
   comparison.core_refs 同样只能引用输入材料中出现过的文献。
3. 增量贡献必须清晰：如果与已有工作区别只在换材料/换体系而科学问题
   相同，就不算新课题，宁可不生成。
4. 如果近期材料不足以支撑新课题，返回空数组 []。
"""
    return user_prompt


def _coerce_idea_fields(idea: Dict[str, Any]) -> Dict[str, Any]:
    """v6.10.31: 清洗六模块模板新增字段（route/validation/comparison）。

    LLM 输出形状不可信：route 可能是整段字符串（拆分为条目）、
    comparison 可能缺子键或形状错误。清洗后缺失字段置空值，下游
    （dossier 生成/人读 brief）按"字段存在但可能为空"处理。
    """
    route = idea.get("route")
    if isinstance(route, str):
        # v6.10.34: 最小长度 6→4——"对比验证""数值模拟"等 4 字合法步骤
        # 曾被误滤（实测"步骤三：对比验证"整步丢失）。4 仍可滤掉拆分
        # 碎屑与空串。
        route = [s.strip() for s in re.split(r"[\n；;]|步骤[一二三四1-4]：", route) if len(s.strip()) >= 4]
    elif not isinstance(route, list):
        route = []
    idea["route"] = [str(r)[:300] for r in route if r][:6]

    validation = idea.get("validation")
    idea["validation"] = str(validation)[:800] if isinstance(validation, str) else ""

    comp = idea.get("comparison")
    if not isinstance(comp, dict):
        comp = {}
    table = [
        {"dimension": str(t.get("dimension", ""))[:60],
         "existing": str(t.get("existing", ""))[:300],
         "ours": str(t.get("ours", ""))[:300]}
        for t in (comp.get("table") or []) if isinstance(t, dict) and t.get("dimension")
    ][:6]
    idea["comparison"] = {
        "core_refs": [str(r)[:200] for r in (comp.get("core_refs") or []) if r][:6],
        "table": table,
        "increment": [str(i)[:300] for i in (comp.get("increment") or []) if i][:5],
        "boundary": [str(b)[:200] for b in (comp.get("boundary") or []) if b][:5],
        "depends": [str(d)[:200] for d in (comp.get("depends") or []) if d][:5],
    }
    return idea


def generate_research_ideas(materials: Dict[str, Any], gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """调用 LLM 生成研究设想。"""
    if not is_llm_available():
        _log_warn("LLM 不可用，跳过研究设想生成")
        return []

    # v7.0.0: 六模块方法论浓缩句收敛至 skill（_build_idea_prompt 内经
    # skill_loader 注入），system prompt 只保留角色设定与真实性约束；
    # "只换材料不换科学问题的不算新课题"为 defer 门槛判定语义，保留。
    system_prompt = (
        "你是林赛（Lin Sai），一位擅长从文献和讨论中提炼研究方向的物理学家。"
        "你的任务是基于可靠来源生成结构化研究设想，不杜撰、不夸大。"
        "每个设想按 research-proposal skill 六模块标准组织"
        "（已注入用户消息），只换材料不换科学问题的不算新课题。"
    )
    user_prompt = _build_idea_prompt(materials, gaps)

    ok, text, meta = llm_complete(system_prompt, user_prompt, timeout=120)
    if not ok:
        _log_warn(f"LLM 生成设想失败: {meta.get('error', 'unknown')}")
        return []

    # 提取 JSON——v7.3.57: 共享容错提取器（llm_json_lib）统一收敛，取代
    # 此前仅围栏正则无降级通道的实现（G2-C 后续批次债务清偿）
    from llm_json_lib import extract_json
    value, reason = extract_json(text)
    if value is None:
        _log_warn(f"解析 LLM 输出失败: {reason}")
        return []
    ideas = value if isinstance(value, list) else [value]

    # 清洗和补充元信息
    cleaned = []
    for idea in ideas:
        if not isinstance(idea, dict):
            continue
        idea["generated_at"] = now_utc()
        idea["reliability"] = RELIABILITY_DERIVED
        idea["sources"] = idea.get("sources", [])
        idea = _coerce_idea_fields(idea)
        cleaned.append(idea)

    return cleaned


# ---------------------------------------------------------------------------
# 与现有课题对比
# ---------------------------------------------------------------------------


def _load_existing_proposals() -> List[Dict[str, Any]]:
    """读取所有现有 proposal 的状态。"""
    from proposal_lifecycle import ProposalLifecycle
    lc = ProposalLifecycle()
    state = lc._load_state()
    proposals = []
    for pid, data in state.get("proposals", {}).items():
        prop_dir = lc._find_proposal_dir(pid)
        brief = ""
        if prop_dir:
            brief_path = prop_dir / "00_proposal-brief.md"
            brief = _read_text(brief_path, 3000)
        proposals.append({
            "proposal_id": pid,
            "status": data.get("status"),
            "project_type": data.get("project_type", "general"),
            "brief": brief,
            "title": lc._extract_proposal_title(prop_dir) if prop_dir else "",
        })
    return proposals


def compare_with_existing(idea: Dict[str, Any], proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """计算设想与每个现有 proposal 的相似度，返回排序列表。"""
    idea_text = " ".join([
        idea.get("title", ""),
        idea.get("background", ""),
        " ".join(idea.get("keywords", [])),
    ])

    scored = []
    for p in proposals:
        prop_text = " ".join([p.get("title", ""), p.get("brief", "")])
        score = _jaccard_similarity(idea_text, prop_text)
        scored.append({**p, "similarity": score})

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored


def decide_action(idea: Dict[str, Any], comparisons: List[Dict[str, Any]]) -> Dict[str, Any]:
    """根据相似度决定：新注册 / 融合到现有 / 扩展建议。"""
    if not comparisons:
        return {"action": "new", "target_id": None, "reason": "无现有课题"}

    top = comparisons[0]
    if top["similarity"] < SIMILARITY_NEW_THRESHOLD:
        return {
            "action": "new",
            "target_id": None,
            "reason": f"与最相似课题 {top['proposal_id']} 相似度 {top['similarity']:.2f} < {SIMILARITY_NEW_THRESHOLD}",
        }

    if top["status"] in ("optimizing", "pending_review"):
        return {
            "action": "merge",
            "target_id": top["proposal_id"],
            "reason": f"与现有课题 {top['proposal_id']} 相似度 {top['similarity']:.2f}，建议融合",
        }

    # archived 或 drafts → 扩展建议
    return {
        "action": "expansion",
        "target_id": top["proposal_id"],
        "reason": f"与已归档/初稿课题 {top['proposal_id']} 相似度 {top['similarity']:.2f}，建议作为扩展候选",
    }


# ---------------------------------------------------------------------------
# 执行动作：新注册 / 融合 / 扩展建议
# ---------------------------------------------------------------------------


def _generate_proposal_id(idea: Dict[str, Any]) -> str:
    """根据标题生成 proposal_id。"""
    from proposal_lifecycle import ProposalLifecycle
    lc = ProposalLifecycle()
    # 从标题提取英文名
    title = idea.get("title", "")
    # 简单拼音化/英文化
    name = safe_filename(title)[:40].strip("-").lower()
    # v6.9.39: 名称段须字母开头（同 register_from_idea），数字开头必被校验拒绝
    name = re.sub(r"^[0-9-]+", "", name).strip("-")
    if not name:
        name = "new-idea"
    return lc.generate_proposal_id(name=name, project_type="general")


def register_new_idea(idea: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """将设想注册为新 proposal（进入 drafts）。"""
    from proposal_lifecycle import ProposalLifecycle
    lc = ProposalLifecycle()

    if dry_run:
        # 仅预览生成的 proposal_id
        title = idea.get("title", "")
        name = safe_filename(title)[:40].strip("-").lower()
        name = re.sub(r"[^a-z0-9-]+", "-", name).strip("-")
        # v6.9.39: 名称段须字母开头（同 register_from_idea），数字开头必被校验拒绝
        name = re.sub(r"^[0-9-]+", "", name).strip("-")
        if not name:
            name = "new-idea"
        proposal_id = lc.generate_proposal_id(name=name, project_type="general")
        return {"action": "new", "proposal_id": proposal_id, "dry_run": True}

    result = lc.register_from_idea(idea, project_type="general")
    if result.get("success"):
        _log_info(f"新设想注册为 drafts: {result['proposal_id']}")
        # v6.9.0 R4: 生成立项决策包（新颖性/重叠度/可行性 + 建议）
        try:
            existing = [
                p
                for p in _load_existing_proposals()
                if p.get("proposal_id") != result["proposal_id"]
            ]
            comparisons = compare_with_existing(idea, existing)
            generate_idea_dossier(idea, comparisons, result["proposal_id"])
        except Exception as exc:
            _log_warn(f"立项决策包生成失败（不影响注册）: {exc}")
    return result


# ---------------------------------------------------------------------------
# v6.9.0 R4: 立项决策包
# ---------------------------------------------------------------------------

IDEA_HOLD_SIMILARITY = 0.50
"""建议搁置线：与现有课题相似度达到该值的设想建议 hold（高度重叠）。"""

_EXPERIMENT_HINTS = ("实验", "测量", "激光", "样品", "装置", "搭建", "观测", "制备")
_THEORY_HINTS = ("理论", "解析", "模拟", "数值", "推导", "建模", "计算")


def _feasibility_hint(text: str) -> Dict[str, Any]:
    """基于关键词的可行性启发式（零成本，不依赖 LLM）。"""
    has_exp = any(k in text for k in _EXPERIMENT_HINTS)
    has_thy = any(k in text for k in _THEORY_HINTS)
    if has_exp and has_thy:
        mode, note = "理实结合", "需兼顾实验资源与理论推导，建议先做理论预研降低试错成本"
    elif has_exp:
        mode, note = "实验导向", "依赖仪器与样品资源，建议核对现有实验条件后再激活"
    elif has_thy:
        mode, note = "理论导向", "以推导/模拟为主，资源需求低，可快速进入优化"
    else:
        mode, note = "未识别", "设想文本未显式标注研究范式，激活前建议人工确认研究路径"
    return {"mode": mode, "note": note}


def recommend_activation(
    top_similarity: float,
    hold_line: float = IDEA_HOLD_SIMILARITY,
    novel_line: float = SIMILARITY_NEW_THRESHOLD,
) -> Tuple[str, str]:
    """根据与现有课题的最高相似度给出激活建议（纯函数，供回归测试）。

    返回 (recommendation, reason)：hold / merge考察 / activate。
    """
    if top_similarity >= hold_line:
        return (
            "hold",
            f"与现有课题相似度 {top_similarity:.2f} ≥ {hold_line}，高度重叠",
        )
    if top_similarity >= novel_line:
        return (
            "merge考察",
            f"与现有课题相似度 {top_similarity:.2f}，建议先考察融合可能性",
        )
    return (
        "activate",
        f"最相似课题相似度 {top_similarity:.2f} < {novel_line}，新颖性达标",
    )


def recommend_activation_tournament(
    idea: Dict[str, Any],
    comparisons: List[Dict[str, Any]],
    hold_line: float = IDEA_HOLD_SIMILARITY,
    novel_line: float = SIMILARITY_NEW_THRESHOLD,
) -> Tuple[str, str, Optional[str]]:
    """v7.2.67 锦标赛制新颖性核查（recommend_activation 的 LLM 终审版）。

    三档语义（hold/merge考察/activate）与 recommend_activation 对齐：
    - top 相似度 ≥ hold 线 → hold（数值硬线，不调 LLM）；
    - hold 线以下进入锦标赛：top-5 Jaccard 候选逐对 pairwise LLM 仲裁
      （引擎复用 weekend_pipeline.input_jobs，与 topic_match 的 new 动作
      闸门同一套三判口径），任一判「同质」→ activate 降级 merge考察
      （tournament_target=该课题）；全部「正交/互补」→ 维持数值档
      （novel 线以上 merge考察 / 以下 activate）；
    - LLM 失败 fail-open 回退纯数值判定（recommend_activation）。

    Returns:
        (recommendation, reason, tournament_target)。tournament_target
        为判同质的课题 id，未降级时为 None。
    """
    if not comparisons:
        return "activate", "当前无现有课题，天然新颖", None
    top = comparisons[0]
    top_sim = float(top.get("similarity", 0.0))
    if top_sim >= hold_line:
        return (
            "hold",
            f"与现有课题相似度 {top_sim:.2f} ≥ {hold_line}，高度重叠",
            None,
        )
    # 锦标赛终审（< hold 线才做）。pairwise 引擎来自 weekend_pipeline.
    # input_jobs，函数内延迟导入——input_jobs 对本模块也是函数内导入
    # （IDEA_HOLD_SIMILARITY），双向延迟避免顶层循环导入。
    action, target_id, t_reason = "new", None, ""
    try:
        from weekend_pipeline.input_jobs import _tournament_novelty_gate_for_texts
        idea_text = " ".join(
            [idea.get("title", ""), idea.get("background", ""), " ".join(idea.get("keywords", []))]
        )
        shaped = [
            {
                "proposal_id": c.get("proposal_id", ""),
                "status": c.get("status", ""),
                "text": f"{c.get('title', '')} {c.get('brief', '')}",
            }
            for c in comparisons
        ]
        action, target_id, t_reason = _tournament_novelty_gate_for_texts(idea_text, shaped)
    except Exception as exc:
        _log_warn(f"锦标赛新颖性核查异常，回退数值判定: {exc}")
    if action == "merge" and target_id:
        return (
            "merge考察",
            f"锦标赛 pairwise 仲裁判同质（vs {target_id}）：{t_reason}，建议先考察融合",
            target_id,
        )
    # 全正交/互补或 fail-open 回退：维持纯数值档
    recommendation, reason = recommend_activation(
        top_sim, hold_line=hold_line, novel_line=novel_line
    )
    return recommendation, reason, None


def generate_idea_dossier(
    idea: Dict[str, Any],
    comparisons: List[Dict[str, Any]],
    proposal_id: str,
) -> Dict[str, Any]:
    """为新注册设想生成立项决策包（00_idea-dossier.md）。

    人从"读设想全文"变成"看一页摘要"：新颖性 vs 现有课题、组合重叠度、
    可行性启发式与激活建议（activate / merge考察 / hold）。
    """
    from proposal_lifecycle import ProposalLifecycle
    from common import file_lock

    idea_text = " ".join(
        [idea.get("title", ""), idea.get("background", ""), " ".join(idea.get("keywords", []))]
    )
    top = comparisons[0] if comparisons else None
    top_sim = float(top["similarity"]) if top else 0.0

    # v7.2.67: 锦标赛制新颖性核查——Jaccard 词袋分数无区分度（同题不同
    # 术语 65-70% 未检出），activate 判定前插 pairwise LLM 锦标赛终审
    # （任一同质 → activate 降级 merge考察）；异常回退纯数值判定。
    tournament_target = None
    try:
        recommendation, rec_reason, tournament_target = recommend_activation_tournament(idea, comparisons)
    except Exception as exc:
        _log_warn(f"锦标赛新颖性核查失败，回退数值判定: {exc}")
        recommendation, rec_reason = recommend_activation(top_sim)
    if top and recommendation != "activate":
        rec_reason = f"与现有课题 {top['proposal_id']}：{rec_reason}"

    feasibility = _feasibility_hint(idea_text)
    overlaps = [c for c in comparisons if float(c.get("similarity", 0)) >= 0.30]
    keywords = idea.get("keywords") or []

    dossier = {
        "proposal_id": proposal_id,
        "title": idea.get("title", ""),
        "generated_at": now_utc(),
        "novelty_top_similarity": top_sim,
        "overlap_count": len(overlaps),
        "feasibility": feasibility["mode"],
        "recommendation": recommendation,
        "recommendation_reason": rec_reason,
    }
    # v7.2.67: 锦标赛判同质降级时记录目标课题（观测/回溯用）
    if tournament_target:
        dossier["tournament_merge_target"] = tournament_target

    # 写入决策包文件
    lc = ProposalLifecycle()
    prop_dir = lc._find_proposal_dir(proposal_id)
    if prop_dir:
        lines = [
            f"# 立项决策包 · {idea.get('title', proposal_id)}",
            "",
            f"- 生成时间：{dossier['generated_at']}",
            f"- 关键词：{'、'.join(keywords[:8]) or '（无）'}",
            "",
            "## 激活建议",
            "",
            f"**{recommendation}** — {rec_reason}",
            "",
        ]
        if tournament_target:
            lines += [
                f"- 锦标赛终审（v7.2.67）：与现有课题 {tournament_target} 判同质，"
                "activate 已降级 merge考察",
                "",
            ]
        lines += [
            "## 新颖性（vs 现有课题）",
            "",
        ]
        if comparisons[:3]:
            for c in comparisons[:3]:
                lines.append(
                    f"- {c.get('proposal_id')}（{c.get('status', '?')}，"
                    f"{c.get('title', '')[:24]}）：相似度 {float(c['similarity']):.2f}"
                )
        else:
            lines.append("- 当前无其他课题，天然新颖")
        lines += [
            "",
            f"组合重叠度：{len(overlaps)} 个课题相似度 ≥ 0.30",
            "",
            "## 可行性启发",
            "",
            f"- 研究范式：{feasibility['mode']}",
            f"- {feasibility['note']}",
            "",
        ]
        # v6.10.31: 六模块模板增量展示——技术路线/验证方案/与参考工作的区别
        route = idea.get("route") or []
        if route:
            lines += ["## 技术路线", ""]
            lines += [f"{i+1}. {r}" for i, r in enumerate(route[:6])]
            lines.append("")
        validation = idea.get("validation") or ""
        if validation:
            lines += ["## 验证方案", "", validation[:500], ""]
        comp = idea.get("comparison") or {}
        if comp.get("table") or comp.get("increment"):
            lines += ["## 与参考工作的区别", ""]
            if comp.get("core_refs"):
                lines.append("核心对比文献：")
                lines += [f"- {r}" for r in comp["core_refs"][:6]]
                lines.append("")
            if comp.get("table"):
                lines += ["| 维度 | 已有工作 | 本设想 |", "|------|---------|--------|"]
                lines += [
                    f"| {t['dimension']} | {t['existing']} | {t['ours']} |"
                    for t in comp["table"]
                ]
                lines.append("")
            if comp.get("increment"):
                lines.append("增量贡献：")
                lines += [f"- {i}" for i in comp["increment"][:5]]
                lines.append("")
            if comp.get("boundary"):
                lines.append("边界界定：")
                lines += [f"- {b}" for b in comp["boundary"][:5]]
                lines.append("")
        lines += [
            "## 背景（节选）",
            "",
            (idea.get("background", "") or "")[:600] or "（无背景文本）",
            "",
        ]
        (prop_dir / "00_idea-dossier.md").write_text("\n".join(lines), encoding="utf-8")

    # 摘要写回 prop_state（锁保护 + 重读合并）
    with file_lock("proposal-lifecycle"):
        state = lc._load_state()
        prop = state.get("proposals", {}).get(proposal_id)
        if prop:
            prop["idea_dossier"] = dossier
            lc._save_state(state)
    return dossier


def merge_into_existing(idea: Dict[str, Any], target_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """将设想融合到现有 proposal。"""
    from proposal_lifecycle import ProposalLifecycle
    lc = ProposalLifecycle()

    if dry_run:
        return {"action": "merge", "target_id": target_id, "dry_run": True}

    result = lc.enrich_from_idea(target_id, idea)
    if result.get("success"):
        _log_info(f"设想融合到现有课题: {target_id}")
    return result


def add_expansion_candidate(idea: Dict[str, Any], target_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """将扩展建议写入 memory/expansion-candidates.json。"""
    candidates = load_json(EXPANSION_CANDIDATES_PATH, default={"candidates": []})
    candidate = {
        "id": f"exp-{now_utc().replace(':', '-').replace('.', '-')}",
        "target_proposal_id": target_id,
        "idea": idea,
        "created_at": now_utc(),
        "status": "pending_review",
    }
    if dry_run:
        return {"action": "expansion", "target_id": target_id, "dry_run": True, "candidate": candidate}

    candidates["candidates"].append(candidate)
    _ensure_dirs()
    save_json(EXPANSION_CANDIDATES_PATH, candidates)

    _log_info(f"扩展建议已记录: {target_id}")
    return {"action": "expansion", "target_id": target_id, "candidate_id": candidate["id"]}


# ---------------------------------------------------------------------------
# 主流程：自动运行
# ---------------------------------------------------------------------------


def run_auto_idea_generation(dry_run: bool = False, max_ideas: int = 3) -> Dict[str, Any]:
    """周末自动研究设想生成入口。

    v6.7.7: 委托给 WeekendPipeline 的 input 阶段，保留旧函数签名以兼容 CLI/Web。
    """
    from weekend_pipeline import WeekendPipeline
    pipeline = WeekendPipeline()
    pipeline.sync_stage_jobs("input")
    result = pipeline.run_stage("input", dry_run=dry_run)

    # 兼容旧返回结构
    ideas_file = INCOMING_DIR / f"ideas-{now_utc()[:10]}.json"
    ideas_data = load_json(ideas_file, default={"actions": []}) if ideas_file.exists() else {"actions": []}
    return {
        "success": result.get("success", True),
        "ideas_count": len(ideas_data.get("actions", [])),
        "actions": ideas_data.get("actions", []),
        "pipeline_result": result,
    }


def _write_weekly_review(date_str: str, ideas: List[Dict[str, Any]], actions: List[Dict[str, Any]]) -> None:
    """生成 weekly-ideas-review.md 供人工核查。"""
    lines = [f"# 周末研究设想摘要（{date_str}）", ""]
    for i, (idea, action) in enumerate(zip(ideas, actions), 1):
        lines.append(f"## {i}. {idea.get('title', '未命名')}")
        lines.append(f"- **背景**：{idea.get('background', '')}")
        lines.append(f"- **缺口**：{idea.get('gap', '')}")
        lines.append(f"- **创新点**：{', '.join(idea.get('innovations', []))}")
        lines.append(f"- **决策**：{action['decision']['action']} — {action['decision']['reason']}")
        if action["decision"]["target_id"]:
            lines.append(f"- **目标课题**：{action['decision']['target_id']}")
        lines.append("")

    review_path = INCOMING_DIR / "weekly-ideas-review.md"
    review_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# 手动输入路径
# ---------------------------------------------------------------------------


def expand_manual_idea(title: str, sketch: str, dry_run: bool = False) -> Dict[str, Any]:
    """用户提交一句话思路，LLM 补全为结构化设想。"""
    if not is_llm_available():
        return {"success": False, "error": "LLM 不可用"}

    system_prompt = (
        "你是林赛（Lin Sai），一位擅长把初步思路扩展为完整研究设想的物理学家。"
        "请基于用户给出的标题和粗略想法，补全研究设想的各个字段。"
        "要求方法具体到名称（禁止'利用先进光学技术'类模糊表述）、技术路线分步、"
        "给出验证方案，并明确与领域内已有工作的区别（增量贡献/边界界定/依赖关系）。"
    )
    user_prompt = f"""用户初步思路：
标题：{title}
概述：{sketch}

请将其扩展为结构化研究设想，输出 JSON：
{{
  "title": "...",
  "background": "...（点明核心科学问题）",
  "gap": "...",
  "content": ["...（具体到方法/材料/体系）"],
  "route": ["步骤一：...（具体方法）", "步骤二：...", "步骤三：...（验证）"],
  "validation": "...（验证判据 + 替代解释排除）",
  "approach": "...（一句话概述）",
  "innovations": ["..."],
  "comparison": {{
    "core_refs": ["领域内代表性工作（真实存在，不确定则留空数组）"],
    "table": [{{"dimension": "体系/物理量/调控手段", "existing": "已有做法", "ours": "本设想做法"}}],
    "increment": ["增量贡献"],
    "boundary": ["不涉及/限制"],
    "depends": ["依赖的已有工作"]
  }},
  "sources": [{{"title": "", "source_type": "user_input"}}],
  "keywords": ["..."]
}}

注意：
1. 基于用户思路合理推演，但不要杜撰具体文献——comparison.core_refs
   只列你确信真实存在的代表作，不确定就给空数组。
2. sources 中第一条必须是 {{"title": "{title}", "source_type": "user_input"}}。
3. 增量贡献必须相对已有工作说清"新在哪里"，只换材料不换科学问题
   的要在 boundary 中如实说明。
"""

    ok, text, meta = llm_complete(system_prompt, user_prompt, timeout=120)
    if not ok:
        return {"success": False, "error": meta.get("error", "LLM 调用失败")}

    try:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        json_str = m.group(1) if m else text
        idea = json.loads(json_str)
    except Exception as e:
        return {"success": False, "error": f"解析失败: {e}", "raw": text[:500]}

    idea["generated_at"] = now_utc()
    idea["reliability"] = RELIABILITY_DERIVED
    idea = _coerce_idea_fields(idea)

    # 对比现有课题
    proposals = _load_existing_proposals()
    comparisons = compare_with_existing(idea, proposals)
    decision = decide_action(idea, comparisons)

    if dry_run:
        return {
            "success": True,
            "idea": idea,
            "decision": decision,
            "top_comparisons": comparisons[:3],
            "dry_run": True,
        }

    # 手动输入默认不自动执行，只返回决策建议
    return {
        "success": True,
        "idea": idea,
        "decision": decision,
        "top_comparisons": comparisons[:3],
        "next_step": "请确认：注册新课题 / 融合到现有课题 / 作为扩展建议",
    }


def apply_manual_idea(idea: Dict[str, Any], action: str, target_id: Optional[str] = None) -> Dict[str, Any]:
    """用户确认后执行手动设想的注册/融合/扩展。"""
    if action == "new":
        return register_new_idea(idea)
    elif action == "merge" and target_id:
        return merge_into_existing(idea, target_id)
    elif action == "expansion" and target_id:
        return add_expansion_candidate(idea, target_id)
    return {"success": False, "error": f"未知动作: {action}"}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _self_check() -> None:
    """自检。"""
    print("=== idea_generator._self_check ===")
    print(f"LLM 可用: {is_llm_available()}")
    print(f"INCOMING_DIR: {INCOMING_DIR}")
    print("✓ 通过")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="研究设想生成器")
    parser.add_argument("--auto", action="store_true", help="周末自动模式")
    parser.add_argument("--manual", metavar="TITLE", help="手动模式：提供标题")
    parser.add_argument("--sketch", default="", help="手动模式：初步思路")
    parser.add_argument("--dry-run", action="store_true", help="只预览不写入")
    parser.add_argument("--self-check", action="store_true", help="自检")
    parser.add_argument("--max-ideas", type=int, default=3, help="最多生成设想数")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
        sys.exit(0)

    if args.auto:
        result = run_auto_idea_generation(dry_run=args.dry_run, max_ideas=args.max_ideas)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    if args.manual:
        result = expand_manual_idea(args.manual, args.sketch, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    parser.print_help()
