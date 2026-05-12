#!/usr/bin/env python3
"""
quality_evaluator.py — 质量评估引擎

用途：
    对自主学习生成的 wiki 页面进行多维质量评估，
    支持规则评估、LLM 评估、对抗性蒸馏、用户反馈闭环。

用法示例：
    >>> from quality_evaluator import evaluate_wiki, adversarial_distill
    >>> result = evaluate_wiki("wiki/papers/2604.19814.md")
    >>> print(result["overall"], result["decision"])  # 0.82, "accept"
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
MEMORY_DIR = PROJECT_ROOT / "memory"
QUALITY_LOG_PATH = MEMORY_DIR / "learning-quality-log.json"
PENDING_QUEUE_PATH = MEMORY_DIR / "learning-pending-queue.json"
USER_EDIT_LOG_PATH = MEMORY_DIR / "learning-user-edits.json"

# 动态导入 knowledge_base
_kb = None

def _import_kb():
    global _kb
    if _kb is not None:
        return _kb
    try:
        import importlib.util
        kb_path = Path(__file__).parent / "knowledge_base.py"
        spec = importlib.util.spec_from_file_location("knowledge_base", kb_path)
        _kb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_kb)
        return _kb
    except Exception as e:
        print(f"✗ 无法导入 knowledge_base: {e}")
        raise


# 动态导入 llm_router
_router = None

def _import_router():
    global _router
    if _router is not None:
        return _router
    try:
        import importlib.util
        lr_path = Path(__file__).parent / "llm_router.py"
        spec = importlib.util.spec_from_file_location("llm_router", lr_path)
        lr_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lr_mod)
        _router = lr_mod.router
        return _router
    except Exception as e:
        print(f"✗ 无法导入 llm_router: {e}")
        raise


# 动态导入 learning_engine（复用 _call_llm_for_learning）
_le = None

def _import_le():
    global _le
    if _le is not None:
        return _le
    try:
        import importlib.util
        le_path = Path(__file__).parent / "learning_engine.py"
        spec = importlib.util.spec_from_file_location("learning_engine", le_path)
        _le = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_le)
        return _le
    except Exception as e:
        print(f"✗ 无法导入 learning_engine: {e}")
        raise


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any = None) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default if default is not None else {}


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _file_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 规则评估器
# ---------------------------------------------------------------------------

def _rule_evaluate(wiki_text: str, source_meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """基于规则的评估。

    检查项：
    1. 引用充分性：是否包含来源引用
    2. 增量价值：与现有知识库的对比
    3. 格式合规：frontmatter 完整性
    4. 长度合规：内容长度
    """
    kb = _import_kb()
    scores = {}
    issues = []

    # 解析 frontmatter
    try:
        fm, body = kb.parse_frontmatter(wiki_text)
    except Exception:
        fm, body = {}, wiki_text

    # 1. 引用充分性 (0-1)
    has_source = bool(
        fm.get("source_arxiv") or fm.get("source_wikipedia") or fm.get("source_raw")
    )
    scores["citation"] = 1.0 if has_source else 0.0
    if not has_source:
        issues.append("缺少来源引用（source_arxiv / source_wikipedia / source_raw）")

    # 2. 格式合规 (0-1)
    required_fields = ["title", "type", "created", "tags", "growth_stage", "confidence"]
    missing_fields = [f for f in required_fields if not fm.get(f)]
    format_score = 1.0 - (len(missing_fields) * 0.15)
    scores["format"] = max(0.0, format_score)
    if missing_fields:
        issues.append(f"frontmatter 缺少字段: {', '.join(missing_fields)}")

    # auto_grown 标记检查
    if not fm.get("auto_grown"):
        issues.append("缺少 auto_grown: true 标记")
        scores["format"] -= 0.1

    # growth_stage 合法性
    valid_stages = {"seedling", "growing", "mature"}
    if fm.get("growth_stage") not in valid_stages:
        issues.append(f"growth_stage 不合法: {fm.get('growth_stage')}")
        scores["format"] -= 0.1

    # 3. 长度合规 (0-1)
    body_len = len(body.strip())
    if body_len >= 1000:
        scores["length"] = 1.0
    elif body_len >= 500:
        scores["length"] = 0.7
    elif body_len >= 300:
        scores["length"] = 0.4
    else:
        scores["length"] = 0.1
        issues.append(f"正文太短 ({body_len} 字符)，期望 ≥300")

    # 4. 增量价值 (0-1)：简化版——检查标题是否已存在 + 内容独特性
    novelty_score = 0.8  # 默认较高
    title = fm.get("title", "")
    if title:
        try:
            similar = kb.check_similar_concepts(title, threshold=0.95)
            if similar:
                novelty_score = 0.3
                issues.append(f"与现有内容高度相似: {similar[0]['title']}")
        except Exception:
            pass
    scores["novelty"] = novelty_score

    # 加权综合
    weights = {"citation": 0.25, "format": 0.3, "length": 0.25, "novelty": 0.2}
    overall = sum(scores.get(k, 0) * w for k, w in weights.items())

    return {
        "overall": round(min(overall, 1.0), 3),
        "scores": {k: round(v, 3) for k, v in scores.items()},
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# LLM 评估器
# ---------------------------------------------------------------------------

def _llm_evaluate(wiki_text: str, source_type: str = "unknown") -> Dict[str, Any]:
    """基于 LLM 的评估。

    维度：
    1. 逻辑一致性
    2. 人格一致性（林赛第一人称）
    3. 学术严谨性
    """
    le = _import_le()

    system_prompt = """你是一位严格的质量审查员，负责评估一篇科研笔记的质量。

请从以下三个维度评分（0-1，保留两位小数），并给出具体意见：

1. 逻辑一致性：内容内部是否有矛盾、数据是否自洽、推理是否连贯
2. 人格一致性：是否保持了"林赛"（强场超快光学 PI）的第一人称视角，是否有第三人称或客观 Wikipedia 风格的表述
3. 学术严谨性：概念表述是否准确、是否有编造的内容、引用是否充分

输出格式必须是 JSON：
{"logic": 0.85, "persona": 0.90, "rigor": 0.75, "issues": ["问题1", "问题2"]}
"""

    messages = [{"role": "user", "content": f"请评估以下笔记（来源：{source_type}）：\n\n{wiki_text[:4000]}"}]

    try:
        result = le._call_llm_for_learning(system_prompt, messages)
        # 从结果中提取 JSON
        json_match = re.search(r"\{[\s\S]*?\}", result)
        if json_match:
            data = json.loads(json_match.group(0))
            scores = {
                "logic": float(data.get("logic", 0.5)),
                "persona": float(data.get("persona", 0.5)),
                "rigor": float(data.get("rigor", 0.5)),
            }
            issues = data.get("issues", [])
            overall = (scores["logic"] + scores["persona"] + scores["rigor"]) / 3
            return {
                "overall": round(min(overall, 1.0), 3),
                "scores": {k: round(v, 3) for k, v in scores.items()},
                "issues": issues if isinstance(issues, list) else [str(issues)],
            }
    except Exception as e:
        print(f"⚠ LLM 评估失败: {e}")

    # fallback：返回中性评分
    return {
        "overall": 0.5,
        "scores": {"logic": 0.5, "persona": 0.5, "rigor": 0.5},
        "issues": ["LLM 评估失败，使用默认评分"],
    }


# ---------------------------------------------------------------------------
# 综合评分与决策
# ---------------------------------------------------------------------------

def evaluate_wiki(wiki_path: str,
                  use_llm: bool = True,
                  cost_tracker: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """对 wiki 页面进行综合评估。

    Args:
        wiki_path: wiki 页面相对路径（相对 knowledge/）
        use_llm: 是否启用 LLM 评估（增加成本）
        cost_tracker: 成本追踪字典

    Returns:
        {
            "overall": 0.82,
            "rule": {"overall": 0.9, "scores": {...}, "issues": [...]},
            "llm": {"overall": 0.75, "scores": {...}, "issues": [...]},
            "decision": "accept",  # accept / pending / reject
            "wiki_path": "wiki/papers/xxx.md"
        }
    """
    kb = _import_kb()
    full_path = KNOWLEDGE_DIR / wiki_path
    if not full_path.exists():
        return {
            "overall": 0.0,
            "decision": "reject",
            "issues": ["文件不存在"],
            "wiki_path": wiki_path,
        }

    wiki_text = full_path.read_text(encoding="utf-8")

    # 规则评估
    rule_result = _rule_evaluate(wiki_text)

    # LLM 评估
    llm_result = None
    if use_llm:
        # 解析 source_type
        fm, _ = kb.parse_frontmatter(wiki_text)
        source_type = "arxiv" if fm.get("source_arxiv") else ("wikipedia" if fm.get("source_wikipedia") else "raw")
        llm_result = _llm_evaluate(wiki_text, source_type)
        if cost_tracker is not None:
            cost_tracker["calls"] = cost_tracker.get("calls", 0) + 1

    # 综合评分
    if llm_result:
        overall = rule_result["overall"] * 0.6 + llm_result["overall"] * 0.4
    else:
        overall = rule_result["overall"]

    overall = round(min(overall, 1.0), 3)

    # 决策
    if overall > 0.7:
        decision = "accept"
    elif overall >= 0.5:
        decision = "pending"
    else:
        decision = "reject"

    result = {
        "overall": overall,
        "rule": rule_result,
        "llm": llm_result,
        "decision": decision,
        "wiki_path": wiki_path,
        "evaluated_at": _now_utc(),
    }

    # 记录到质量日志
    _log_quality(result)

    # 如果 pending，加入待审队列
    if decision == "pending":
        _add_to_pending_queue(result)

    return result


def _log_quality(result: Dict[str, Any]) -> None:
    """记录质量评估结果。"""
    log = _load_json(QUALITY_LOG_PATH, [])
    log.append({
        "wiki_path": result.get("wiki_path"),
        "overall": result.get("overall"),
        "decision": result.get("decision"),
        "evaluated_at": result.get("evaluated_at", _now_utc()),
    })
    # 保留最近 100 条
    log = log[-100:]
    _save_json(QUALITY_LOG_PATH, log)


def _add_to_pending_queue(result: Dict[str, Any]) -> None:
    """将 pending 的 wiki 加入待审队列。"""
    queue = _load_json(PENDING_QUEUE_PATH, [])
    kb = _import_kb()
    fm, _ = kb.parse_frontmatter((KNOWLEDGE_DIR / result["wiki_path"]).read_text(encoding="utf-8"))

    queue.append({
        "path": result["wiki_path"],
        "title": fm.get("title", result["wiki_path"]),
        "score": result.get("overall", 0),
        "created_at": _now_utc(),
        "source_type": "arxiv" if fm.get("source_arxiv") else ("wikipedia" if fm.get("source_wikipedia") else "raw"),
        "source_id": fm.get("source_arxiv", fm.get("source_wikipedia", fm.get("source_raw", ""))),
        "preview": (KNOWLEDGE_DIR / result["wiki_path"]).read_text(encoding="utf-8")[:300],
    })

    _save_json(PENDING_QUEUE_PATH, queue)


# ---------------------------------------------------------------------------
# 对抗性多轮蒸馏
# ---------------------------------------------------------------------------

def adversarial_distill(source_content: str, source_type: str,
                        cost_tracker: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """对抗性多轮蒸馏：Generator → Critic → Defender → Synthesizer。

    仅对已有初稿的内容进行深度打磨。如果输入是原始材料，先用 Generator 生成初稿。

    Args:
        source_content: 原始材料或初稿
        source_type: 来源类型
        cost_tracker: 成本追踪

    Returns:
        {"final_wiki": "...", "rounds": [...], "improved": bool}
    """
    le = _import_le()
    rounds = []

    # Round 1: Generator — 生成初稿（如果输入已经是 wiki 格式则跳过）
    if "---" in source_content and "frontmatter" not in source_content.lower():
        # 已经是 wiki 格式
        draft = source_content
        rounds.append({"role": "generator", "output": "[输入已是初稿，跳过生成]"})
    else:
        system = "你是一位科研笔记撰写专家。请将以下材料转化为林赛（强场超快光学 PI）视角的研究笔记。"
        messages = [{"role": "user", "content": source_content[:6000]}]
        draft = le._call_llm_for_learning(system, messages, cost_tracker)
        rounds.append({"role": "generator", "output": draft[:200] + "..."})

    # Round 2: Critic — 审查问题
    critic_prompt = """你是一位严格的同行评审员。请审查以下研究笔记，指出至少 2 个实质性问题：

1. 逻辑漏洞或事实错误
2. 人格一致性偏差（是否保持了林赛的第一人称视角）
3. 学术不严谨之处（概念模糊、过度推断、缺少引用）

请列出具体问题，每条问题附带简要说明。"""
    messages = [{"role": "user", "content": draft[:5000]}]
    critic_output = le._call_llm_for_learning(critic_prompt, messages, cost_tracker)
    rounds.append({"role": "critic", "output": critic_output[:300] + "..."})

    # Round 3: Defender — 反驳 Critic
    defender_prompt = f"""你是林赛本人。以下是你的研究笔记和一位评审员的批评意见。

【你的笔记】
{draft[:3000]}

【评审意见】
{critic_output[:2000]}

请逐条反驳评审意见。对于合理的批评，承认并解释；对于不合理的批评，用事实和逻辑反驳。保持第一人称。"""
    messages = [{"role": "user", "content": defender_prompt}]
    defender_output = le._call_llm_for_learning("", messages, cost_tracker)
    rounds.append({"role": "defender", "output": defender_output[:300] + "..."})

    # Round 4: Synthesizer — 综合各方意见
    synthesizer_prompt = f"""你是林赛的学术合作者。请综合以下三方意见，生成最终版研究笔记：

【初稿】
{draft[:2000]}

【评审意见】
{critic_output[:1500]}

【林赛的回应】
{defender_output[:1500]}

请输出完整的、改进后的研究笔记（含 frontmatter），保留初稿中正确的部分，修正被指出的问题，融入林赛的回应。"""
    messages = [{"role": "user", "content": synthesizer_prompt}]
    final_wiki = le._call_llm_for_learning("", messages, cost_tracker)
    rounds.append({"role": "synthesizer", "output": final_wiki[:200] + "..."})

    # 评估是否改进
    initial_score = _quick_score(draft)
    final_score = _quick_score(final_wiki)
    improved = final_score > initial_score

    return {
        "final_wiki": final_wiki,
        "rounds": rounds,
        "improved": improved,
        "initial_score": initial_score,
        "final_score": final_score,
    }


def _quick_score(wiki_text: str) -> float:
    """快速评分（用于对抗性蒸馏的内部对比）。"""
    result = _rule_evaluate(wiki_text)
    return result["overall"]


# ---------------------------------------------------------------------------
# 用户反馈闭环
# ---------------------------------------------------------------------------

def detect_user_edits() -> Dict[str, Any]:
    """检测用户对 auto-grown wiki 页面的编辑。

    Returns:
        {
            "edited": [{"path", "old_hash", "new_hash", "diff_summary"}],
            "unchanged": [...],
            "total_scanned": N
        }
    """
    kb = _import_kb()
    edit_log = _load_json(USER_EDIT_LOG_PATH, {})
    edited = []
    unchanged = []

    wiki_pages = kb.list_wiki_pages()
    for page in wiki_pages:
        path = page.get("path", "")
        if not path:
            continue

        full_path = KNOWLEDGE_DIR / path
        if not full_path.exists():
            continue

        try:
            text = full_path.read_text(encoding="utf-8")
            fm, body = kb.parse_frontmatter(text)
        except Exception:
            continue

        # 只关注 auto_grown 的页面
        if not fm.get("auto_grown"):
            continue

        current_hash = _file_sha256(text)
        old_hash = edit_log.get(path, {}).get("hash", "")

        if old_hash and old_hash != current_hash:
            # 用户编辑过
            diff_summary = _summarize_edit(path, old_hash, current_hash)
            edited.append({
                "path": path,
                "title": fm.get("title", path),
                "old_hash": old_hash,
                "new_hash": current_hash,
                "diff_summary": diff_summary,
                "detected_at": _now_utc(),
            })
            print(f"  📎 检测到用户编辑: {path}")

        # 更新记录
        edit_log[path] = {
            "hash": current_hash,
            "last_checked": _now_utc(),
        }
        unchanged.append(path)

    _save_json(USER_EDIT_LOG_PATH, edit_log)

    return {
        "edited": edited,
        "unchanged": unchanged,
        "total_scanned": len(wiki_pages),
    }


def _summarize_edit(path: str, old_hash: str, new_hash: str) -> str:
    """简化版编辑摘要。"""
    # 实际 diff 分析较复杂，这里返回简化描述
    return "用户已编辑（详细 diff 分析需手动查看）"


# ---------------------------------------------------------------------------
# 待审队列操作
# ---------------------------------------------------------------------------

def get_pending_queue() -> List[Dict[str, Any]]:
    """获取待审队列。"""
    return _load_json(PENDING_QUEUE_PATH, [])


def approve_pending(wiki_path: str) -> bool:
    """审批通过 pending 的 wiki 页面。

    将 review_status 改为 accepted，移除 auto_grown 标记（保留历史记录）。
    """
    kb = _import_kb()
    full_path = KNOWLEDGE_DIR / wiki_path
    if not full_path.exists():
        return False

    try:
        text = full_path.read_text(encoding="utf-8")
        fm, body = kb.parse_frontmatter(text)
        fm["review_status"] = "accepted"
        # 可选：移除 auto_grown 标记，表示已人工确认
        # fm.pop("auto_grown", None)

        new_text = kb.build_frontmatter(fm) + "\n" + body
        full_path.write_text(new_text, encoding="utf-8")

        # 从待审队列移除
        queue = _load_json(PENDING_QUEUE_PATH, [])
        queue = [q for q in queue if q.get("path") != wiki_path]
        _save_json(PENDING_QUEUE_PATH, queue)

        kb.log_growth("review", wiki_path, "user", "用户审批通过")
        return True
    except Exception as e:
        print(f"✗ 审批失败: {e}")
        return False


def reject_pending(wiki_path: str) -> bool:
    """拒绝 pending 的 wiki 页面，删除文件。"""
    kb = _import_kb()
    full_path = KNOWLEDGE_DIR / wiki_path
    if full_path.exists():
        try:
            full_path.unlink()
        except Exception:
            pass

    # 从图谱移除
    try:
        fm, _ = kb.parse_frontmatter(full_path.read_text(encoding="utf-8")) if full_path.exists() else ({}, "")
        title = fm.get("title", "")
        if title:
            kb._remove_graph_node(title)
    except Exception:
        pass

    # 从待审队列移除
    queue = _load_json(PENDING_QUEUE_PATH, [])
    queue = [q for q in queue if q.get("path") != wiki_path]
    _save_json(PENDING_QUEUE_PATH, queue)

    kb.log_growth("review", wiki_path, "user", "用户拒绝并删除")
    return True


# ---------------------------------------------------------------------------
# 批量评估
# ---------------------------------------------------------------------------

def batch_evaluate_all_auto_grown(use_llm: bool = False) -> Dict[str, Any]:
    """批量评估所有 auto-grown 的 wiki 页面。"""
    kb = _import_kb()
    results = {"accept": [], "pending": [], "reject": [], "errors": []}

    for page in kb.list_wiki_pages():
        path = page.get("path", "")
        if not path:
            continue

        try:
            text = (KNOWLEDGE_DIR / path).read_text(encoding="utf-8")
            fm, _ = kb.parse_frontmatter(text)
            if not fm.get("auto_grown"):
                continue

            result = evaluate_wiki(path, use_llm=use_llm)
            decision = result.get("decision", "reject")
            results[decision].append({
                "path": path,
                "title": fm.get("title", path),
                "score": result.get("overall", 0),
            })
        except Exception as e:
            results["errors"].append({"path": path, "error": str(e)})

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="林赛质量评估引擎")
    parser.add_argument("--evaluate", type=str, help="评估指定 wiki 页面路径")
    parser.add_argument("--batch", action="store_true", help="批量评估所有 auto-grown 页面")
    parser.add_argument("--pending", action="store_true", help="显示待审队列")
    parser.add_argument("--approve", type=str, help="审批通过指定路径")
    parser.add_argument("--reject", type=str, help="拒绝并删除指定路径")
    parser.add_argument("--detect-edits", action="store_true", help="检测用户编辑")
    parser.add_argument("--llm", action="store_true", help="启用 LLM 评估（增加成本）")
    args = parser.parse_args()

    if args.evaluate:
        result = evaluate_wiki(args.evaluate, use_llm=args.llm)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.batch:
        results = batch_evaluate_all_auto_grown(use_llm=args.llm)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.pending:
        queue = get_pending_queue()
        print(f"待审队列 ({len(queue)} 项):")
        for item in queue:
            print(f"  ○ {item.get('title', 'N/A')} [{item.get('source_type', '?')}] 评分: {item.get('score', 0)}")
    elif args.approve:
        success = approve_pending(args.approve)
        print("✓ 审批通过" if success else "✗ 审批失败")
    elif args.reject:
        success = reject_pending(args.reject)
        print("✓ 已拒绝并删除" if success else "✗ 操作失败")
    elif args.detect_edits:
        result = detect_user_edits()
        print(f"扫描 {result['total_scanned']} 个页面，发现 {len(result['edited'])} 个编辑")
        for e in result["edited"]:
            print(f"  📎 {e['path']}: {e['diff_summary']}")
    else:
        parser.print_help()


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1:
        main()
    else:
        print("=" * 50)
        print("◐ 开始 quality_evaluator 自检")
        print("=" * 50)

        print("\n[1/5] 测试 _rule_evaluate...")
        good_wiki = """---
title: "测试论文"
type: papers
created: "2026-05-12T10:00:00Z"
tags: ["test"]
related: ["阿秒科学"]
source_arxiv: "1234.56789"
growth_stage: "growing"
confidence: 0.7
auto_grown: true
---

# 测试论文

## 林赛的理解
我认为这项工作非常重要，因为它直接关联到我正在搭建的固体 HHG 实验系统。

## 核心发现
- 发现 1
- 发现 2

## 方法亮点
使用了先进的泵浦-探测技术。

## 实验参数备忘
波长：800nm，脉宽：30fs

## 开放问题
还需要验证在更短波长下的表现。
"""
        rule = _rule_evaluate(good_wiki)
        print(f"   规则评分: {rule['overall']}, 问题: {rule['issues']}")
        assert rule["overall"] > 0.6, f"好 wiki 应得高分，实际 {rule['overall']}"

        bad_wiki = "无 frontmatter 的短文本。"
        rule_bad = _rule_evaluate(bad_wiki)
        print(f"   差 wiki 规则评分: {rule_bad['overall']}, 问题: {rule_bad['issues']}")
        assert rule_bad["overall"] < 0.5, f"差 wiki 应得低分，实际 {rule_bad['overall']}"
        print("   ✓ 规则评估通过")

        print("\n[2/5] 测试 evaluate_wiki（不启用 LLM）...")
        # 创建一个临时 wiki 文件
        test_wiki_path = KNOWLEDGE_DIR / "wiki" / "concepts" / "_test_eval.md"
        test_wiki_path.parent.mkdir(parents=True, exist_ok=True)
        test_wiki_path.write_text(good_wiki, encoding="utf-8")
        result = evaluate_wiki("wiki/concepts/_test_eval.md", use_llm=False)
        print(f"   综合评分: {result['overall']}, 决策: {result['decision']}")
        assert result["decision"] in ("accept", "pending")
        test_wiki_path.unlink()
        print("   ✓ 综合评估通过")

        print("\n[3/5] 测试待审队列...")
        queue = get_pending_queue()
        assert isinstance(queue, list)
        print(f"   当前队列长度: {len(queue)}")
        print("   ✓ 待审队列读取通过")

        print("\n[4/5] 测试 detect_user_edits...")
        edits = detect_user_edits()
        assert "edited" in edits
        assert "total_scanned" in edits
        print(f"   扫描: {edits['total_scanned']} 个, 编辑: {len(edits['edited'])} 个")
        print("   ✓ 编辑检测通过")

        print("\n[5/5] 测试对抗性蒸馏骨架...")
        # 为避免 LLM 网络超时，使用 mock 测试骨架逻辑
        original_call = None
        try:
            le = _import_le()
            original_call = le._call_llm_for_learning
            def _mock_call(system, messages, ct=None):
                return "---\ntitle: Mock\nauto_grown: true\n---\n\n# Mock\n\n## 林赛的理解\nMock content."
            le._call_llm_for_learning = _mock_call
            adv = adversarial_distill("测试材料：阿秒脉冲是一种极短的光脉冲。", "wikipedia")
            assert "final_wiki" in adv
            assert "rounds" in adv
            print(f"   轮次: {[r['role'] for r in adv['rounds']]}")
            print("   ✓ 对抗性蒸馏骨架通过")
        finally:
            if original_call and _le is not None:
                _le._call_llm_for_learning = original_call

        print("\n" + "=" * 50)
        print("✓ 所有自检项目通过")
        print("=" * 50)
