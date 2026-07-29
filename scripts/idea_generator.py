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
    """构建生成研究设想的 prompt。"""
    briefing_text = "\n\n".join(b["text"][:800] for b in materials.get("briefings", [])[:2])
    paper_text = "\n\n".join(
        f"- {p.get('title', '')}: {p.get('abstract', '')[:200]}"
        for p in materials.get("papers", [])[:5]
    )
    gap_text = "\n".join(f"- {g['text']}" for g in gaps[:5])

    user_prompt = f"""请基于以下近期文献和讨论，生成 1-3 个高质量研究设想。

【近期文献简报】
{briefing_text}

【关键论文摘要】
{paper_text}

【识别到的研究缺口】
{gap_text}

要求每个设想包含以下字段，输出为 JSON 数组：
- title: 课题标题（具体、准确）
- background: 研究背景和动机（100-200 字）
- gap: 现存研究空白或瓶颈（100 字以内）
- content: 拟开展研究内容（2-4 条）
- approach: 拟采用技术路线（简明）
- innovations: 创新点（2-3 条）
- sources: 来源文献/简报列表（每条含 title 和 source_type: briefing/paper/capture/wiki）
- keywords: 用于与现有课题对比的关键词列表（中英文术语）

注意：
1. 只生成基于上述材料可支撑的研究设想，不要杜撰。
2. 每个设想的 sources 必须具体对应到输入材料中的文献或简报。
3. 如果近期材料不足以支撑新课题，返回空数组 []。
"""
    return user_prompt


def generate_research_ideas(materials: Dict[str, Any], gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """调用 LLM 生成研究设想。"""
    if not is_llm_available():
        _log_warn("LLM 不可用，跳过研究设想生成")
        return []

    system_prompt = (
        "你是林赛（Lin Sai），一位擅长从文献和讨论中提炼研究方向的物理学家。"
        "你的任务是基于可靠来源生成结构化研究设想，不杜撰、不夸大。"
    )
    user_prompt = _build_idea_prompt(materials, gaps)

    ok, text, meta = llm_complete(system_prompt, user_prompt, timeout=120)
    if not ok:
        _log_warn(f"LLM 生成设想失败: {meta.get('error', 'unknown')}")
        return []

    # 提取 JSON
    try:
        # 优先匹配 ```json ... ```
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if m:
            json_str = m.group(1)
        else:
            json_str = text
        ideas = json.loads(json_str)
        if not isinstance(ideas, list):
            ideas = [ideas]
    except Exception as e:
        _log_warn(f"解析 LLM 输出失败: {e}")
        return []

    # 清洗和补充元信息
    cleaned = []
    for idea in ideas:
        if not isinstance(idea, dict):
            continue
        idea["generated_at"] = now_utc()
        idea["reliability"] = RELIABILITY_DERIVED
        idea["sources"] = idea.get("sources", [])
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
        if not name:
            name = "new-idea"
        proposal_id = lc.generate_proposal_id(name=name, project_type="general")
        return {"action": "new", "proposal_id": proposal_id, "dry_run": True}

    result = lc.register_from_idea(idea, project_type="general")
    if result.get("success"):
        _log_info(f"新设想注册为 drafts: {result['proposal_id']}")
    return result


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
    )
    user_prompt = f"""用户初步思路：
标题：{title}
概述：{sketch}

请将其扩展为结构化研究设想，输出 JSON：
{{
  "title": "...",
  "background": "...",
  "gap": "...",
  "content": ["...", "..."],
  "approach": "...",
  "innovations": ["...", "..."],
  "sources": [{{"title": "", "source_type": "user_input"}}],
  "keywords": ["..."]
}}

注意：
1. 基于用户思路合理推演，但不要杜撰具体文献。
2. sources 中第一条必须是 {{"title": "{title}", "source_type": "user_input"}}。
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
