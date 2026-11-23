#!/usr/bin/env python3
"""申请书自检与优化引擎 — 研究管线"自检优化"阶段核心模块。

对生成的申请书段落进行六维自检，识别段落级问题并产出分级优化策略，
跟踪迭代历史（最多 5 次），生成可执行的自检报告。

位于研究管线"自检优化"阶段：
    ... → 04_proposal（申请书生成） → 05_review（自检优化） → 完成
本模块的产物 inspection-report.json 保存在 {proposal_dir}/05_review/ 下。

六维检查：
    1. logical_consistency  逻辑一致性 — 矛盾、循环论证、无支撑论断
    2. evidence_sufficiency  证据充分性 — 论断是否有引用/数据支撑
    3. innovation            创新性    — 是否有新颖贡献表述
    4. feasibility           可行性    — 方法是否可得、时间安排是否合理
    5. academic_norms        学术规范  — 引文格式、术语、结构合规
    6. expression_quality    表达质量  — 清晰度、简洁性、学术语体

优化策略（四级，逐级升级）：
    targeted_repair        定向修复      严重=0 且 重要≤2
    paragraph_rewrite      段落重写      重要>2 或 表达分数<0.6
    structural_adjustment  结构调整      逻辑分数<0.6 或 多个结构问题
    rollback_regeneration  回滚重生成    总分<0.5 或 严重>3

迭代追踪：最多 5 次。连续 2 次分数无提升则建议人工复审。

用法:
    >>> from pathlib import Path
    >>> from proposal_inspector import ProposalInspector
    >>> inspector = ProposalInspector(Path("/data/proposals/T1"))
    >>> sections = {"立项依据": "# 立项依据\\n\\n固体HHG是前沿[1]。"}
    >>> report = inspector.inspect(sections)
    >>> print(report["overall_score"], report["passed"])
    >>> strategy = inspector.generate_strategy(inspector.identify_issues(report["dimensions"]))
    >>> new_sections = inspector.apply_optimization(sections, strategy)
    >>> md = inspector.export_report("markdown")

命令行自检:
    python3 scripts/proposal_inspector.py --self-check

规范：仅 Python 标准库，pathlib.Path 路径处理，JSON ensure_ascii=False，时间戳 UTC ISO。
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock, lazy_load

# v6.3.2 接入 LLM 网关（共享基础设施层），让自检具备语义评估能力
try:
    from llm_gateway import is_llm_available, llm_json
    _LLM_OK = is_llm_available()
except Exception:
    _LLM_OK = False
    def llm_json(*a, **kw):  # type: ignore
        return False, None, {}

__all__ = [
    "ProposalInspector",
    "DIMENSIONS",
    "SEVERITY_LEVELS",
    "STRATEGY_LEVELS",
    "SCORE_THRESHOLDS",
    "DIMENSION_WEIGHTS",
    "MAX_ITERATIONS",
]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 六维检查维度（key → 中文标签）
DIMENSIONS: Dict[str, str] = {
    "logical_consistency": "逻辑一致性",
    "evidence_sufficiency": "证据充分性",
    "innovation": "创新性",
    "feasibility": "可行性",
    "academic_norms": "学术规范",
    "expression_quality": "表达质量",
}

# 问题严重性级别
SEVERITY_LEVELS: Dict[str, str] = {
    "critical": "严重",
    "major": "重要",
    "minor": "次要",
    "suggestion": "建议",
}

# 优化策略级别（key → 中文标签）
STRATEGY_LEVELS: Dict[str, str] = {
    "targeted_repair": "定向修复",
    "paragraph_rewrite": "段落重写",
    "structural_adjustment": "结构调整",
    "rollback_regeneration": "回滚重生成",
}

# 分数阈值
SCORE_THRESHOLDS: Dict[str, float] = {
    "pass": 0.80,        # 总分 >= 0.80 且 严重=0 → 通过
    "rewrite": 0.60,     # 表达分数 < 0.60 → 段落重写
    "structural": 0.60,  # 逻辑分数 < 0.60 → 结构调整
    "rollback": 0.50,    # 总分 < 0.50 → 回滚重生成
}

# 维度权重（总和为 1.0）
DIMENSION_WEIGHTS: Dict[str, float] = {
    "logical_consistency": 0.20,
    "evidence_sufficiency": 0.20,
    "innovation": 0.15,
    "feasibility": 0.15,
    "academic_norms": 0.15,
    "expression_quality": 0.15,
}

# 迭代次数上限与停滞阈值
MAX_ITERATIONS = 5
STAGNATION_THRESHOLD = 2

# ---------------------------------------------------------------------------
# 规则检查关键词表
# ---------------------------------------------------------------------------

# 论断句标记（出现即视为论断，需引用支撑）
_CLAIM_MARKERS = ["表明", "证明", "证实", "显示", "提出", "认为", "发现", "揭示",
                  "导致", "使得", "可见", "可知", "说明", "反映"]

# 自指陈述前缀（定义性表述，不计为需引用的论断）
_SELF_REF_PREFIXES = ["本研究", "本工作", "本方法", "本文", "本课题", "本项目", "我们"]

# 创新性关键词
_NOVELTY_KEYWORDS = ["首次", "新方法", "新机制", "新理论", "创新", "新颖", "首次提出",
                     "前所未有", "新现象", "新效应", "新方案", "新模型", "原创"]

# 方法/技术关键词
_METHOD_KEYWORDS = ["方法", "技术", "实验", "计算", "模拟", "测量", "TDDFT", "DFT",
                     "第一性原理", "泵浦-探测", "理论计算", "数值模拟", "光谱", "观测"]

# 时间安排关键词
_TIMELINE_KEYWORDS = ["年", "月", "周", "阶段", "第一步", "第二步", "第三步",
                      "前期", "中期", "后期", "时间表", "进度", "计划"]

# 非学术表述
_INFORMAL_MARKERS = ["我觉得", "应该是", "可能吧", "大概", "好像", "感觉", "差不多"]

# 转折词（段落起始出现视为潜在矛盾，缺少前置论断）
_CONTRADICTION_MARKERS = ["然而", "但是", "不过", "可是"]

# 循环论证模式
_CIRCULAR_PATTERN = re.compile(r"之所以.{0,30}是因为|因此.{0,30}因为")

# 引文标记 [1], [1,2], [1-3]
_CITATION_PATTERN = re.compile(r'\[(\d+(?:[,-]\d+)*)\]')

# 异常引文标记 [?] 或 [!]
_MALFORMED_CITATION = re.compile(r'\[\?\]|\[!\]')

# 阈值
_LONG_SENTENCE_THRESHOLD = 80   # 单句超过此字符数视为过长
_LONG_PARAGRAPH_THRESHOLD = 300  # 单段超过此字符数视为过长


# ---------------------------------------------------------------------------
# 文本工具函数
# ---------------------------------------------------------------------------

def _split_paragraphs(text: str) -> List[str]:
    """按空行分割段落，返回非空段落列表（已 strip）。"""
    if not text:
        return []
    paras = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paras if p.strip()]


def _split_sentences(text: str) -> List[str]:
    """按中英文句末标点分割句子，返回非空句子列表。"""
    if not text:
        return []
    parts = re.split(r'[。！？!?]', text)
    return [p.strip() for p in parts if p.strip()]


def _is_claim(sentence: str) -> bool:
    """判断句子是否为论断句（含论断标记且非自指定义）。"""
    if any(sentence.startswith(p) for p in _SELF_REF_PREFIXES):
        # 自指定义句不计为需引用的论断
        return False
    return any(m in sentence for m in _CLAIM_MARKERS)


def _clamp_score(x: float) -> float:
    """将分数钳制到 [0.0, 1.0]。"""
    return max(0.0, min(1.0, x))


def _hash_content(content: str) -> str:
    """计算内容的 SHA-256 哈希前 16 位，用于段落指纹。"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _make_issue(
    dimension: str,
    section: str,
    paragraph_index: int,
    severity: str,
    description: str,
    suggestion: str,
    auto_fixable: bool,
) -> Dict[str, Any]:
    """构造一个问题对象（issue_id 由 identify_issues 统一赋值）。"""
    return {
        "issue_id": "",
        "dimension": dimension,
        "section": section,
        "paragraph_index": paragraph_index,
        "severity": severity,
        "description": description,
        "suggestion": suggestion,
        "auto_fixable": auto_fixable,
    }


# ---------------------------------------------------------------------------
# 六维规则检查器（纯函数，无 LLM）
# ---------------------------------------------------------------------------

def _check_logical_consistency(sections: Dict[str, str]) -> Dict[str, Any]:
    """逻辑一致性检查：转折词开头、无支撑论断、循环论证。"""
    issues: List[Dict[str, Any]] = []
    contradictions = 0
    unsupported = 0
    circular = 0

    for section_name, text in sections.items():
        paras = _split_paragraphs(text)
        for pi, para in enumerate(paras):
            # 转折词开头（缺少前置论断）
            para_head = para.lstrip()[:4]
            if any(para_head.startswith(m) for m in _CONTRADICTION_MARKERS):
                contradictions += 1
                issues.append(_make_issue(
                    dimension="logical_consistency",
                    section=section_name,
                    paragraph_index=pi,
                    severity="major",
                    description=f"第{pi+1}段以转折词开头，缺少前置论断支撑",
                    suggestion="补充前置论断或将转折表述移至段落内部",
                    auto_fixable=False,
                ))
            # 无支撑论断（每段最多记一条，避免泛滥）
            para_has_unsupported = False
            for sent in _split_sentences(para):
                if _is_claim(sent) and not _CITATION_PATTERN.search(sent):
                    unsupported += 1
                    para_has_unsupported = True
            if para_has_unsupported:
                issues.append(_make_issue(
                    dimension="logical_consistency",
                    section=section_name,
                    paragraph_index=pi,
                    severity="minor",
                    description=f"第{pi+1}段含无引用支撑的论断句",
                    suggestion="补充文献引用 [N] 或理论推导依据",
                    auto_fixable=True,
                ))
            # 循环论证
            if _CIRCULAR_PATTERN.search(para):
                circular += 1
                issues.append(_make_issue(
                    dimension="logical_consistency",
                    section=section_name,
                    paragraph_index=pi,
                    severity="major",
                    description="检测到循环论证模式（之所以…是因为 / 因此…因为）",
                    suggestion="拆解因果链，提供独立证据支撑",
                    auto_fixable=False,
                ))

    score = _clamp_score(1.0 - 0.15 * contradictions - 0.08 * unsupported - 0.20 * circular)
    return {
        "dimension": "logical_consistency",
        "score": score,
        "issues": issues,
        "details": {
            "contradictions_found": contradictions,
            "unsupported_claims": unsupported,
            "circular_reasoning": circular,
        },
    }


def _check_evidence_sufficiency(sections: Dict[str, str]) -> Dict[str, Any]:
    """证据充分性检查：论断段落是否有引用支撑。"""
    issues: List[Dict[str, Any]] = []
    total_claim_paras = 0
    paras_with_cit = 0
    paras_without_cit = 0

    for section_name, text in sections.items():
        paras = _split_paragraphs(text)
        for pi, para in enumerate(paras):
            claims = [s for s in _split_sentences(para) if _is_claim(s)]
            has_citation = bool(_CITATION_PATTERN.search(para))
            if claims:
                total_claim_paras += 1
                if has_citation:
                    paras_with_cit += 1
                else:
                    paras_without_cit += 1
                    issues.append(_make_issue(
                        dimension="evidence_sufficiency",
                        section=section_name,
                        paragraph_index=pi,
                        severity="major",
                        description=f"第{pi+1}段含论断但无任何文献引用支撑",
                        suggestion="补充相关文献引用 [N]",
                        auto_fixable=True,
                    ))

    score = _clamp_score(paras_with_cit / total_claim_paras) if total_claim_paras else 1.0
    return {
        "dimension": "evidence_sufficiency",
        "score": score,
        "issues": issues,
        "details": {
            "total_claim_paragraphs": total_claim_paras,
            "paragraphs_with_citations": paras_with_cit,
            "paragraphs_without_citations": paras_without_cit,
        },
    }


def _check_innovation(sections: Dict[str, str]) -> Dict[str, Any]:
    """创新性检查：是否检测到创新性表述关键词。"""
    issues: List[Dict[str, Any]] = []
    full_text = "\n".join(str(v) for v in sections.values())
    found = []
    for kw in _NOVELTY_KEYWORDS:
        if kw in full_text and kw not in found:
            found.append(kw)

    if not found:
        issues.append(_make_issue(
            dimension="innovation",
            section="全文",
            paragraph_index=0,
            severity="major",
            description="未检测到创新性表述关键词（首次/新方法/创新等）",
            suggestion="明确标注本研究的创新点与新贡献",
            auto_fixable=False,
        ))
    elif len(found) < 2:
        issues.append(_make_issue(
            dimension="innovation",
            section="全文",
            paragraph_index=0,
            severity="minor",
            description=f"创新性表述不足（仅检测到 {len(found)} 个关键词：{found}）",
            suggestion="补充创新点阐述，使用多种创新性表述",
            auto_fixable=False,
        ))

    score = _clamp_score(len(found) / 3.0)
    return {
        "dimension": "innovation",
        "score": score,
        "issues": issues,
        "details": {
            "novelty_keywords_found": len(found),
            "novelty_keywords_list": found,
        },
    }


def _check_feasibility(sections: Dict[str, str]) -> Dict[str, Any]:
    """可行性检查：方法/技术描述与时间安排。"""
    issues: List[Dict[str, Any]] = []
    full_text = "\n".join(str(v) for v in sections.values())
    methods_found = []
    for kw in _METHOD_KEYWORDS:
        if kw in full_text and kw not in methods_found:
            methods_found.append(kw)
    timeline_found = []
    for kw in _TIMELINE_KEYWORDS:
        if kw in full_text and kw not in timeline_found:
            timeline_found.append(kw)

    if not methods_found:
        issues.append(_make_issue(
            dimension="feasibility",
            section="全文",
            paragraph_index=0,
            severity="major",
            description="未检测到具体研究方法/技术/实验手段的描述",
            suggestion="补充研究方法、技术路线与实验手段",
            auto_fixable=False,
        ))
    if not timeline_found:
        issues.append(_make_issue(
            dimension="feasibility",
            section="全文",
            paragraph_index=0,
            severity="minor",
            description="未检测到时间安排/进度指标",
            suggestion="补充研究计划与时间节点",
            auto_fixable=False,
        ))

    has_methods = 1.0 if methods_found else 0.0
    has_timeline = 1.0 if timeline_found else 0.0
    score = _clamp_score(0.6 * has_methods + 0.4 * has_timeline)
    return {
        "dimension": "feasibility",
        "score": score,
        "issues": issues,
        "details": {
            "method_mentions": len(methods_found),
            "methods_found": methods_found,
            "timeline_indicators": len(timeline_found),
            "has_timeline": bool(timeline_found),
        },
    }


def _check_academic_norms(sections: Dict[str, str]) -> Dict[str, Any]:
    """学术规范检查：引文格式、标题结构。"""
    issues: List[Dict[str, Any]] = []
    total_citations = 0
    malformed = 0
    headers = 0
    missing_header_sections: List[str] = []

    for section_name, text in sections.items():
        cites = _CITATION_PATTERN.findall(text)
        total_citations += len(cites)
        bad = _MALFORMED_CITATION.findall(text)
        malformed += len(bad)
        if bad:
            issues.append(_make_issue(
                dimension="academic_norms",
                section=section_name,
                paragraph_index=0,
                severity="major",
                description=f"检测到 {len(bad)} 处格式异常的引文标记（[?]或[!]）",
                suggestion="修正或补全引文标记为 [N] 格式",
                auto_fixable=True,
            ))
        section_headers = re.findall(r'^#+\s+.+', text, re.MULTILINE)
        headers += len(section_headers)
        if not section_headers and text.strip():
            missing_header_sections.append(section_name)
            issues.append(_make_issue(
                dimension="academic_norms",
                section=section_name,
                paragraph_index=0,
                severity="minor",
                description=f"章节「{section_name}」缺少 Markdown 标题行（# 开头）",
                suggestion="补充章节标题行",
                auto_fixable=False,
            ))

    score = 1.0
    if malformed > 0:
        score -= 0.2 * min(malformed, 3) / 3
    if missing_header_sections:
        score -= 0.1 * min(len(missing_header_sections), 3) / 3
    score = _clamp_score(score)
    return {
        "dimension": "academic_norms",
        "score": score,
        "issues": issues,
        "details": {
            "citation_markers": total_citations,
            "malformed_citations": malformed,
            "section_headers": headers,
            "missing_headers_sections": missing_header_sections,
        },
    }


def _check_expression_quality(sections: Dict[str, str]) -> Dict[str, Any]:
    """表达质量检查：句长、段长、学术语体。"""
    issues: List[Dict[str, Any]] = []
    total_sentences = 0
    long_sentences = 0
    total_paragraphs = 0
    long_paragraphs = 0
    informal = 0

    for section_name, text in sections.items():
        paras = _split_paragraphs(text)
        for pi, para in enumerate(paras):
            total_paragraphs += 1
            if len(para) > _LONG_PARAGRAPH_THRESHOLD:
                long_paragraphs += 1
                issues.append(_make_issue(
                    dimension="expression_quality",
                    section=section_name,
                    paragraph_index=pi,
                    severity="minor",
                    description=f"第{pi+1}段过长（{len(para)}字符），建议拆分",
                    suggestion="将长段落拆分为 2-3 个短段落",
                    auto_fixable=False,
                ))
            for sent in _split_sentences(para):
                total_sentences += 1
                if len(sent) > _LONG_SENTENCE_THRESHOLD:
                    long_sentences += 1
            # 非学术表述（每段最多记一条）
            for m in _INFORMAL_MARKERS:
                if m in para:
                    informal += 1
                    issues.append(_make_issue(
                        dimension="expression_quality",
                        section=section_name,
                        paragraph_index=pi,
                        severity="major",
                        description=f"检测到非学术表述：\"{m}\"",
                        suggestion="替换为正式学术表述",
                        auto_fixable=False,
                    ))
                    break

    long_sent_ratio = (long_sentences / total_sentences) if total_sentences else 0
    long_para_ratio = (long_paragraphs / total_paragraphs) if total_paragraphs else 0
    score = _clamp_score(1.0 - 0.15 * long_sent_ratio - 0.15 * long_para_ratio - 0.3 * informal)
    return {
        "dimension": "expression_quality",
        "score": score,
        "issues": issues,
        "details": {
            "total_sentences": total_sentences,
            "long_sentences": long_sentences,
            "total_paragraphs": total_paragraphs,
            "long_paragraphs": long_paragraphs,
            "informal_markers": informal,
        },
    }


# 维度 → 检查器映射
_DIMENSION_CHECKERS = {
    "logical_consistency": _check_logical_consistency,
    "evidence_sufficiency": _check_evidence_sufficiency,
    "innovation": _check_innovation,
    "feasibility": _check_feasibility,
    "academic_norms": _check_academic_norms,
    "expression_quality": _check_expression_quality,
}


# ---------------------------------------------------------------------------
# ProposalInspector 类
# ---------------------------------------------------------------------------

class ProposalInspector:
    """申请书自检与优化引擎。

    每个 proposal 目录对应一个 ProposalInspector 实例，管理该 proposal 下
    `05_review/inspection-report.json` 自检状态文件（含最新报告与迭代历史）。

    线程安全：所有写操作通过 common.file_lock（fcntl.flock 跨进程锁）保护
    read-modify-write 临界区，锁键基于 proposal_dir 路径哈希，不同 proposal 互不阻塞。
    """

    def __init__(self, proposal_dir: Path | str) -> None:
        """初始化自检引擎。

        Args:
            proposal_dir: proposal 根目录，自检状态文件位于其下的 05_review/。
        """
        self.proposal_dir = Path(proposal_dir)
        self.review_dir = self.proposal_dir / "05_review"
        self.state_path = self.review_dir / "inspection-report.json"
        # 跨进程锁键：基于 proposal_dir 绝对路径哈希
        digest = hashlib.md5(str(self.proposal_dir.resolve()).encode("utf-8")).hexdigest()[:12]
        self._lock_name = f"inspection-{digest}"
        self.review_dir.mkdir(parents=True, exist_ok=True)
        # 上下文缓存（供 generate_strategy 复用）
        self._last_dimension_scores: Dict[str, float] = {}
        self._last_overall_score: Optional[float] = None
        self._last_question_framework: Optional[dict] = None

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------

    def _empty_state(self) -> Dict[str, Any]:
        """返回空状态结构。"""
        return {
            "proposal_dir": str(self.proposal_dir),
            "created_at": now_utc(),
            "updated_at": now_utc(),
            "report_seq": 0,
            "stagnation_count": 0,
            "latest_report": {},
            "iterations": [],
        }

    def _load_state(self) -> Dict[str, Any]:
        """加载自检状态（纯读，不加锁）。"""
        data = load_json(self.state_path, default=None)
        if not isinstance(data, dict):
            return self._empty_state()
        data.setdefault("iterations", [])
        data.setdefault("latest_report", {})
        data.setdefault("stagnation_count", 0)
        data.setdefault("report_seq", 0)
        if not isinstance(data["iterations"], list):
            data["iterations"] = []
        return data

    def _save_state(self, state: Dict[str, Any]) -> None:
        """保存自检状态（原子写入，应在锁内调用）。"""
        state["updated_at"] = now_utc()
        save_json(self.state_path, state)

    # ------------------------------------------------------------------
    # v6.3.2 LLM 语义评估补充
    # ------------------------------------------------------------------

    def _llm_semantic_review(
        self,
        sections: Dict[str, str],
        rule_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """用 LLM 对申请书进行语义层面的深度评审。

        规则检查覆盖格式/结构，LLM 覆盖学术深度/逻辑/创新性等语义维度。
        失败时返回空 dict（调用方降级为纯规则结果）。
        """
        if not _LLM_OK:
            return {}

        # 拼接章节摘要（避免超长 prompt）
        parts = []
        total_chars = 0
        for name in ("立项依据", "研究内容", "研究方案", "特色与创新"):
            text = sections.get(name, "")
            if text:
                # 截取前 1500 字符
                snippet = text[:1500]
                parts.append(f"### {name}\n{snippet}")
                total_chars += len(snippet)
                if total_chars > 5000:
                    break
        if not parts:
            return {}
        proposal_text = "\n\n".join(parts)

        rule_score = rule_report.get("overall_score", 0.0)
        rule_issues = rule_report.get("total_issues", 0)

        sys_prompt = (
            "你是 NSFC 面上项目的会评专家，深耕强场超快光学/阿秒科学领域。"
            "你擅长从学术深度、逻辑严密性、创新性、可行性等语义层面评审申请书，"
            "并给出具体的、可操作的修改建议。"
        )
        user_prompt = (
            f"请对以下申请书内容进行语义层面的深度评审。\n\n"
            f"=== 申请书内容（节选）===\n{proposal_text}\n\n"
            f"=== 规则引擎检查结果 ===\n"
            f"规则总分：{rule_score:.2f}　问题数：{rule_issues}\n\n"
            f"请从以下五个语义维度评审，并输出严格 JSON：\n"
            f"{{\n"
            f'  "academic_depth_score": 0.0-1.0,  // 学术深度：论述是否有实质物理内容\n'
            f'  "logical_rigor_score": 0.0-1.0,    // 逻辑严密性：论证链条是否完整\n'
            f'  "innovation_clarity_score": 0.0-1.0, // 创新性：创新点是否具体可信\n'
            f'  "feasibility_score": 0.0-1.0,      // 可行性：方案是否可落地\n'
            f'  "overall_comment": "一句话总评",\n'
            f'  "key_strengths": ["优点1", "优点2"],\n'
            f'  "key_weaknesses": ["不足1", "不足2"],\n'
            f'  "improvement_suggestions": ["建议1", "建议2"]\n'
            f"}}\n"
            f"只输出 JSON，不要解释。"
        )

        try:
            ok, data, _ = llm_json(sys_prompt, user_prompt, timeout=120, prefer="governance")
            if ok and isinstance(data, dict):
                return data
        except Exception:
            pass
        return {}

    # ------------------------------------------------------------------
    # 核心检查接口
    # ------------------------------------------------------------------

    def check_dimension(self, dimension: str, sections: Dict[str, str]) -> Dict[str, Any]:
        """检查单个维度。

        Args:
            dimension: 维度 key（见 DIMENSIONS）
            sections: 章节名 → markdown 文本

        Returns:
            该维度的检查结果（score/issues/details）

        Raises:
            ValueError: 未知维度
        """
        if dimension not in _DIMENSION_CHECKERS:
            raise ValueError(f"未知维度: {dimension}（支持: {list(DIMENSIONS.keys())}）")
        result = _DIMENSION_CHECKERS[dimension](sections)
        # 缓存分数，供 generate_strategy 复用
        self._last_dimension_scores[dimension] = result["score"]
        return result

    def inspect(
        self,
        sections: Dict[str, str],
        question_framework: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """执行完整六维自检，生成报告并记录一次迭代。

        Args:
            sections: 章节名 → markdown 文本
            question_framework: 可选的问题框架（用于回滚重生成策略引用）

        Returns:
            自检报告（含 dimensions/overall_score/strategy/passed 等）
        """
        self._last_dimension_scores = {}
        self._last_question_framework = question_framework

        dimensions: Dict[str, Dict[str, Any]] = {}
        for dim in DIMENSIONS:
            result = self.check_dimension(dim, sections)
            dimensions[dim] = result

        overall = _clamp_score(
            sum(self._last_dimension_scores.get(d, 0.0) * w
                for d, w in DIMENSION_WEIGHTS.items())
            if DIMENSION_WEIGHTS else 0.0
        )
        self._last_overall_score = overall

        issues = self.identify_issues(dimensions)
        strategy = self.generate_strategy(issues)

        critical = sum(1 for i in issues if i["severity"] == "critical")
        major = sum(1 for i in issues if i["severity"] == "major")
        minor = sum(1 for i in issues if i["severity"] == "minor")
        suggestion = sum(1 for i in issues if i["severity"] == "suggestion")
        passed = (overall >= SCORE_THRESHOLDS["pass"]) and (critical == 0)

        report: Dict[str, Any] = {
            "report_id": "rpt_000",  # 由 _record_iteration 赋值
            "timestamp": now_utc(),
            "iteration": 0,  # 由 _record_iteration 赋值
            "sections_checked": list(sections.keys()),
            "dimensions": dimensions,
            "overall_score": overall,
            "total_issues": len(issues),
            "critical_count": critical,
            "major_count": major,
            "minor_count": minor,
            "suggestion_count": suggestion,
            "strategy": strategy,
            "passed": passed,
            "manual_review_recommended": False,
        }
        # v6.3.2 LLM 语义评审补充（锦上添花，失败不阻塞）
        llm_review = self._llm_semantic_review(sections, report)
        if llm_review:
            report["llm_review"] = llm_review
            # 若 LLM 给出语义分数，融合进总分（规则 0.6 + LLM 0.4）
            llm_scores = []
            for k in ("academic_depth_score", "logical_rigor_score",
                      "innovation_clarity_score", "feasibility_score"):
                v = llm_review.get(k)
                if isinstance(v, (int, float)) and 0.0 <= v <= 1.0:
                    llm_scores.append(float(v))
            if llm_scores:
                llm_avg = sum(llm_scores) / len(llm_scores)
                report["overall_score"] = round(overall * 0.6 + llm_avg * 0.4, 3)
                report["score_breakdown"] = {
                    "rule_score": round(overall, 3),
                    "llm_score": round(llm_avg, 3),
                    "fusion": "rule*0.6 + llm*0.4",
                }
                # 重新判定 passed
                report["passed"] = (
                    report["overall_score"] >= SCORE_THRESHOLDS["pass"]
                    and critical == 0
                )
        self._record_iteration(report, sections, issues)
        return report

    def identify_issues(self, check_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从检查结果中识别问题，统一赋 issue_id。

        Args:
            check_results: 维度 → 检查结果（即 inspect 返回的 dimensions 字段）

        Returns:
            扁平化的问题列表，issue_id 按维度顺序赋值（issue_001, issue_002, ...）
        """
        issues: List[Dict[str, Any]] = []
        counter = 1
        results = check_results.values() if isinstance(check_results, dict) else check_results
        for result in results:
            if not isinstance(result, dict):
                continue
            for issue in result.get("issues", []):
                issue["issue_id"] = f"issue_{counter:03d}"
                issues.append(issue)
                counter += 1
        return issues

    def generate_strategy(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """根据问题与缓存分数生成优化策略。

        策略级别判定（从重到轻，命中即止）：
            rollback_regeneration   总分 < 0.5 或 严重 > 3
            structural_adjustment   逻辑分数 < 0.6 或 结构类问题 ≥ 2
            paragraph_rewrite       重要 > 2 或 表达分数 < 0.6
            targeted_repair         默认（严重=0 且 重要≤2）

        Args:
            issues: identify_issues 返回的问题列表

        Returns:
            策略对象（level/level_label/reason/actions/estimated_improvement）
        """
        critical_count = sum(1 for i in issues if i["severity"] == "critical")
        major_count = sum(1 for i in issues if i["severity"] == "major")

        overall_score = self._last_overall_score
        dim_scores = self._last_dimension_scores or {}
        logical_score = dim_scores.get("logical_consistency", 1.0)
        expression_score = dim_scores.get("expression_quality", 1.0)

        # 结构类问题：逻辑/学术规范维度的严重或重要问题
        structural_issues = [
            i for i in issues
            if i["dimension"] in ("logical_consistency", "academic_norms")
            and i["severity"] in ("critical", "major")
        ]

        if (overall_score is not None and overall_score < SCORE_THRESHOLDS["rollback"]) \
                or critical_count > 3:
            level = "rollback_regeneration"
            reason = (f"总分 {overall_score:.2f} < {SCORE_THRESHOLDS['rollback']}"
                      if overall_score is not None and overall_score < SCORE_THRESHOLDS["rollback"]
                      else f"严重问题数 {critical_count} > 3")
        elif logical_score < SCORE_THRESHOLDS["structural"] or len(structural_issues) >= 2:
            level = "structural_adjustment"
            reason = (f"逻辑一致性分数 {logical_score:.2f} < {SCORE_THRESHOLDS['structural']}"
                      if logical_score < SCORE_THRESHOLDS["structural"]
                      else f"结构类问题 {len(structural_issues)} ≥ 2")
        elif major_count > 2 or expression_score < SCORE_THRESHOLDS["rewrite"]:
            level = "paragraph_rewrite"
            reason = (f"重要问题 {major_count} > 2"
                      if major_count > 2
                      else f"表达质量分数 {expression_score:.2f} < {SCORE_THRESHOLDS['rewrite']}")
        else:
            level = "targeted_repair"
            reason = f"严重问题 {critical_count}，重要问题 {major_count} ≤ 2"

        actions = self._build_actions(level, issues)
        estimated = self._estimate_improvement(level, issues)
        return {
            "level": level,
            "level_label": STRATEGY_LEVELS[level],
            "reason": reason,
            "actions": actions,
            "estimated_improvement": estimated,
        }

    def _build_actions(self, level: str, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为每个问题生成对应动作。"""
        actions: List[Dict[str, Any]] = []
        for issue in issues:
            actions.append({
                "issue_id": issue.get("issue_id", ""),
                "dimension": issue["dimension"],
                "section": issue["section"],
                "paragraph_index": issue.get("paragraph_index", 0),
                "severity": issue["severity"],
                "description": issue["description"],
                "suggestion": issue.get("suggestion", ""),
                "auto_fixable": issue.get("auto_fixable", False),
                "fix_type": self._fix_type_for(level, issue),
            })
        return actions

    def _fix_type_for(self, level: str, issue: Dict[str, Any]) -> str:
        """根据策略级别与问题维度映射修复类型。"""
        dim = issue.get("dimension", "")
        if level == "targeted_repair":
            if dim == "evidence_sufficiency":
                return "append_citation_marker"
            if dim == "academic_norms" and "格式异常" in issue.get("description", ""):
                return "fix_malformed_citation"
            return "manual_fix"
        if level == "paragraph_rewrite":
            return "rewrite_paragraph"
        if level == "structural_adjustment":
            return "structural_change"
        if level == "rollback_regeneration":
            return "regenerate_from_framework"
        return "manual_fix"

    def _estimate_improvement(self, level: str, issues: List[Dict[str, Any]]) -> float:
        """估算预期提升分数（粗略）。"""
        auto_fixable = sum(1 for i in issues if i.get("auto_fixable"))
        base = {
            "targeted_repair": 0.05 + 0.02 * auto_fixable,
            "paragraph_rewrite": 0.15,
            "structural_adjustment": 0.20,
            "rollback_regeneration": 0.30,
        }.get(level, 0.10)
        return round(min(0.40, base), 3)

    # ------------------------------------------------------------------
    # 优化应用
    # ------------------------------------------------------------------

    def apply_optimization(
        self,
        sections: Dict[str, str],
        strategy: Dict[str, Any],
    ) -> Dict[str, str]:
        """应用优化策略，返回新章节（不修改原 sections）。

        v1 为规则版，仅 targeted_repair 的可自动修复项会实际改写文本；
        其余级别在文本中插入待办注释，提示需 LLM 介入。

        Args:
            sections: 原章节
            strategy: generate_strategy 返回的策略

        Returns:
            优化后的新章节
        """
        new_sections: Dict[str, str] = dict(sections)
        level = strategy.get("level", "targeted_repair")

        if level == "targeted_repair":
            for action in strategy.get("actions", []):
                if not action.get("auto_fixable"):
                    continue
                section = action.get("section", "")
                if section not in new_sections:
                    continue
                para_idx = action.get("paragraph_index", 0)
                ft = action.get("fix_type", "")
                if ft == "append_citation_marker":
                    new_sections[section] = self._append_citation_marker(
                        new_sections[section], para_idx)
                elif ft == "fix_malformed_citation":
                    new_sections[section] = self._fix_malformed_citations(
                        new_sections[section])
        elif level == "paragraph_rewrite":
            for action in strategy.get("actions", []):
                section = action.get("section", "")
                if section in new_sections and action.get("fix_type") == "rewrite_paragraph":
                    new_sections[section] = self._mark_for_rewrite(
                        new_sections[section], action.get("paragraph_index", 0))
        elif level == "structural_adjustment":
            if new_sections:
                first_key = next(iter(new_sections))
                new_sections[first_key] = (
                    new_sections[first_key]
                    + "\n\n<!-- 结构调整建议：请重新组织章节顺序/合并拆分段落 -->"
                )
        elif level == "rollback_regeneration":
            if new_sections:
                first_key = next(iter(new_sections))
                new_sections[first_key] = (
                    new_sections[first_key]
                    + "\n\n<!-- 回滚重生成建议：基于问题框架重新生成内容，需 LLM 介入 -->"
                )

        self._record_optimization(new_sections)
        return new_sections

    def _append_citation_marker(self, text: str, para_idx: int) -> str:
        """在指定段落末尾追加[需补充引用]标记。"""
        paras = _split_paragraphs(text)
        if 0 <= para_idx < len(paras):
            paras[para_idx] = paras[para_idx].rstrip() + " [需补充引用]"
        return "\n\n".join(paras)

    def _fix_malformed_citations(self, text: str) -> str:
        """将异常引文标记 [?] [!] 替换为[需补全引用]。"""
        return _MALFORMED_CITATION.sub("[需补全引用]", text)

    def _mark_for_rewrite(self, text: str, para_idx: int) -> str:
        """在指定段落末尾插入待重写注释。"""
        paras = _split_paragraphs(text)
        if 0 <= para_idx < len(paras):
            paras[para_idx] = (
                paras[para_idx]
                + "\n<!-- 待重写：表达质量/逻辑需优化，建议 LLM 段落重写 -->"
            )
        return "\n\n".join(paras)

    def _record_optimization(self, new_sections: Dict[str, str]) -> None:
        """记录优化结果到最新迭代（sections_after/optimized）。"""
        with file_lock(self._lock_name):
            state = self._load_state()
            if state["iterations"]:
                latest = state["iterations"][-1]
                latest["sections_after"] = {
                    n: _hash_content(c) for n, c in new_sections.items()
                }
                latest["optimized"] = True
            self._save_state(state)

    # ------------------------------------------------------------------
    # 迭代记录
    # ------------------------------------------------------------------

    def _record_iteration(
        self,
        report: Dict[str, Any],
        sections: Dict[str, str],
        issues: List[Dict[str, Any]],
    ) -> None:
        """记录一次迭代，赋值 report_id/iteration，更新停滞计数。"""
        with file_lock(self._lock_name):
            state = self._load_state()
            iterations: List[Dict[str, Any]] = state["iterations"]

            prev_score = iterations[-1]["score"] if iterations else None
            iteration_no = len(iterations) + 1
            score_change = (
                round(report["overall_score"] - prev_score, 4)
                if prev_score is not None else 0.0
            )
            improved = score_change > 0

            state["report_seq"] = state.get("report_seq", 0) + 1
            report["report_id"] = f"rpt_{state['report_seq']:03d}"
            report["iteration"] = iteration_no

            # 停滞计数
            if len(iterations) >= 1 and iteration_no > 1:
                if improved:
                    state["stagnation_count"] = 0
                else:
                    state["stagnation_count"] = state.get("stagnation_count", 0) + 1
            else:
                state["stagnation_count"] = 0
            report["manual_review_recommended"] = (
                state["stagnation_count"] >= STAGNATION_THRESHOLD
            )

            entry = {
                "iteration": iteration_no,
                "timestamp": report["timestamp"],
                "sections_before": {
                    n: _hash_content(c) for n, c in sections.items()
                },
                "issues_found": [
                    {
                        "issue_id": i["issue_id"],
                        "dimension": i["dimension"],
                        "severity": i["severity"],
                        "section": i["section"],
                        "description": i["description"],
                    }
                    for i in issues
                ],
                "issue_count": len(issues),
                "strategy": report["strategy"],
                "score": report["overall_score"],
                "sections_after": None,
                "optimized": False,
                "score_change": score_change,
                "improved": improved,
            }
            iterations.append(entry)
            # 上限保护：仅保留最近 MAX_ITERATIONS 次
            if len(iterations) > MAX_ITERATIONS:
                state["iterations"] = iterations[-MAX_ITERATIONS:]
            state["latest_report"] = report
            self._save_state(state)

    # ------------------------------------------------------------------
    # 报告与历史查询
    # ------------------------------------------------------------------

    def get_inspection_report(self) -> Dict[str, Any]:
        """获取最新自检报告（副本）；无则返回空 dict。"""
        state = self._load_state()
        return dict(state.get("latest_report", {})) or {}

    def get_iteration_history(self) -> List[Dict[str, Any]]:
        """获取全部迭代记录（副本）。"""
        state = self._load_state()
        return [dict(it) for it in state.get("iterations", [])]

    def export_report(self, format: str = "markdown") -> str:
        """导出自检报告。

        Args:
            format: "markdown" 或 "json"

        Returns:
            格式化字符串

        Raises:
            ValueError: 不支持的格式
        """
        report = self.get_inspection_report()
        if not report:
            return "" if format == "markdown" else "{}"
        if format == "json":
            return json.dumps(report, ensure_ascii=False, indent=2)
        if format == "markdown":
            return self._render_markdown(report)
        raise ValueError(f"不支持的格式: {format}（支持 markdown/json）")

    def _render_markdown(self, report: Dict[str, Any]) -> str:
        """将报告渲染为 Markdown 文本。"""
        lines: List[str] = []
        lines.append("# 申请书自检报告")
        lines.append("")
        lines.append(f"- 报告ID: {report.get('report_id', '-')}")
        lines.append(f"- 时间: {report.get('timestamp', '-')}")
        lines.append(f"- 迭代: 第 {report.get('iteration', 0)} 次")
        lines.append(f"- 检查章节: {', '.join(report.get('sections_checked', [])) or '-'}")
        lines.append(f"- 总分: {report.get('overall_score', 0):.2f}")
        lines.append(f"- 问题总数: {report.get('total_issues', 0)}")
        lines.append(f"  - 严重: {report.get('critical_count', 0)}")
        lines.append(f"  - 重要: {report.get('major_count', 0)}")
        lines.append(f"  - 次要: {report.get('minor_count', 0)}")
        lines.append(f"  - 建议: {report.get('suggestion_count', 0)}")
        status = "通过 ✓" if report.get("passed") else "未通过 ✗"
        lines.append(f"- 状态: {status}")
        if report.get("manual_review_recommended"):
            lines.append("- ⚠ 建议人工复审（连续迭代分数无提升）")
        lines.append("")
        lines.append("## 六维检查结果")
        lines.append("")
        lines.append("| 维度 | 分数 | 问题数 |")
        lines.append("|------|------|--------|")
        for dim, result in report.get("dimensions", {}).items():
            label = DIMENSIONS.get(dim, dim)
            score = result.get("score", 0)
            cnt = len(result.get("issues", []))
            lines.append(f"| {label} | {score:.2f} | {cnt} |")
        lines.append("")
        lines.append("## 问题清单")
        lines.append("")
        for dim, result in report.get("dimensions", {}).items():
            label = DIMENSIONS.get(dim, dim)
            for issue in result.get("issues", []):
                sev = SEVERITY_LEVELS.get(issue["severity"], issue["severity"])
                lines.append(
                    f"- [{sev}] {label}/{issue.get('section', '-')} "
                    f"第{issue.get('paragraph_index', 0) + 1}段: {issue.get('description', '')}"
                )
                lines.append(f"  - 建议: {issue.get('suggestion', '')}")
        lines.append("")
        lines.append("## 优化策略")
        lines.append("")
        strat = report.get("strategy", {})
        level_label = strat.get("level_label", strat.get("level", "-"))
        lines.append(f"- 策略级别: {level_label}")
        lines.append(f"- 判定依据: {strat.get('reason', '-')}")
        lines.append(f"- 预期提升: +{strat.get('estimated_improvement', 0):.2f}")
        lines.append("- 动作清单:")
        for action in strat.get("actions", []):
            lines.append(
                f"  - [{action.get('severity', '-')}] {action.get('section', '-')} "
                f"第{action.get('paragraph_index', 0) + 1}段: {action.get('description', '-')}"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 引文检查集成
    # ------------------------------------------------------------------

    def check_citations(
        self,
        sections: Dict[str, str],
        citation_manager: Any,
    ) -> Dict[str, Any]:
        """使用 CitationManager 检查引文完整性。

        Args:
            sections: 章节文本
            citation_manager: CitationManager 实例（需实现 validate_citations）

        Returns:
            引文检查结果（dimension/score/issues/details）
        """
        full_text = "\n\n".join(str(v) for v in sections.values())
        if citation_manager is not None and hasattr(citation_manager, "validate_citations"):
            result = citation_manager.validate_citations(full_text)
        else:
            result = {
                "valid": True, "missing": [], "unused": [], "total_refs": 0,
                "cited_count": 0, "uncited_count": 0, "cited_numbers": [],
            }

        issues: List[Dict[str, Any]] = []
        for num in result.get("missing", []):
            issues.append(_make_issue(
                dimension="academic_norms",
                section="全文",
                paragraph_index=0,
                severity="critical",
                description=f"引用 [{num}] 缺少对应参考文献",
                suggestion=f"补充参考文献 [{num}] 的完整信息或修正引用编号",
                auto_fixable=False,
            ))
        for key in result.get("unused", [])[:5]:
            issues.append(_make_issue(
                dimension="academic_norms",
                section="全文",
                paragraph_index=0,
                severity="minor",
                description=f"参考文献 {key} 未被正文引用",
                suggestion="在正文相关论断处补充引用，或移除多余参考文献",
                auto_fixable=False,
            ))

        missing_count = len(result.get("missing", []))
        score = _clamp_score(1.0 - 0.15 * missing_count)
        return {
            "dimension": "citations",
            "score": score,
            "issues": issues,
            "details": {
                "valid": result.get("valid", True),
                "missing": result.get("missing", []),
                "unused": result.get("unused", []),
                "total_refs": result.get("total_refs", 0),
                "cited_count": result.get("cited_count", 0),
                "uncited_count": result.get("uncited_count", 0),
            },
        }

    # ------------------------------------------------------------------
    # 模块集成（懒加载）
    # ------------------------------------------------------------------

    def register_inspection_artifact(self, artifact_manager: Any = None) -> Optional[Dict[str, Any]]:
        """将自检报告注册为产物（懒加载 artifact_manager）。

        Args:
            artifact_manager: 可选的 ArtifactManager 实例；为 None 时自动创建

        Returns:
            产物元数据；失败返回 None
        """
        am = artifact_manager
        if am is None:
            am_mod = lazy_load("artifact_manager")
            if am_mod is None or not hasattr(am_mod, "ArtifactManager"):
                return None
            am = am_mod.ArtifactManager(self.proposal_dir)
        report = self.get_inspection_report()
        if not report:
            return None
        try:
            content = json.dumps(report, ensure_ascii=False, indent=2)
            return am.create_artifact(
                artifact_id=f"inspection_v{report.get('iteration', 1)}",
                artifact_type="self_check",
                stage=5,
                content=content,
                file_path="05_review/inspection-report.json",
                author="proposal_inspector",
            )
        except Exception:
            return None

    def register_lineage(self, tracker: Any = None) -> bool:
        """注册自检 → 申请书段落的血缘关系（懒加载 lineage_tracker）。

        Args:
            tracker: 可选的 LineageTracker 实例；为 None 时自动创建

        Returns:
            成功返回 True
        """
        lt = tracker
        if lt is None:
            lt_mod = lazy_load("lineage_tracker")
            if lt_mod is None or not hasattr(lt_mod, "LineageTracker"):
                return False
            lt = lt_mod.LineageTracker(self.proposal_dir)
        report = self.get_inspection_report()
        if not report:
            return False
        try:
            rid = report.get("report_id", "inspection")
            if hasattr(lt, "register_node"):
                lt.register_node(rid, "self_check", "自检报告", stage=5)
            if hasattr(lt, "add_edge"):
                for section in report.get("sections_checked", []):
                    lt.add_edge(rid, section, "derived_from", "自检基于申请书段落")
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """自检：在临时目录中隔离测试全部核心场景。

    检查点（21 项）：
        1.  初始化（创建空状态）
        2.  完整六维检查（优质章节，passed=True）
        3.  单维度检查 logical_consistency（结构正确）
        4.  单维度检查 evidence_sufficiency（结构正确）
        5.  问题识别与严重性分级（劣质章节，issue_id 顺序赋值）
        6.  策略生成 - targeted_repair
        7.  策略生成 - paragraph_rewrite（重要>2）
        8.  策略生成 - paragraph_rewrite（表达分数<0.6）
        9.  策略生成 - structural_adjustment（逻辑分数<0.6）
        10. 策略生成 - structural_adjustment（结构类问题≥2）
        11. 策略生成 - rollback_regeneration（总分<0.5）
        12. 策略生成 - rollback_regeneration（严重>3）
        13. 定向修复应用（targeted_repair 后含 [需补充引用]）
        14. 检查报告获取
        15. 迭代历史追踪（两次 inspect → 2 条迭代）
        16. 停滞检测与人工复审建议（3 次同 sections → manual_review）
        17. Markdown 导出
        18. JSON 导出
        19. 引文检查集成（mock CitationManager，缺失引文 critical）
        20. 分数阈值 / 通过判定（优质通过、劣质未通过）
        21. 原子写入 + 文件锁（文件可加载、锁名唯一）
    """
    import shutil
    import tempfile

    print("=" * 50)
    print("◐ proposal_inspector 自检")
    print("=" * 50)

    tmp = Path(tempfile.mkdtemp(prefix="inspector_test_"))
    try:
        proposal_dir = tmp / "T1_proposal"

        # 测试用章节
        sections_good = {
            "立项依据": (
                "# 立项依据\n\n"
                "固体HHG是超快光学前沿方向[1]。研究表明该机制具有新颖性[2]。\n\n"
                "本研究首次提出新方法解析偏振态。"
            ),
            "研究内容": (
                "# 研究内容\n\n"
                "采用TDDFT方法进行理论计算。分阶段实施：第一年建模，第二年实验测量。"
            ),
        }
        sections_targeted = {
            "立项依据": (
                "# 立项依据\n\n"
                "研究表明固体HHG是前沿方向。本研究首次提出新方法。采用TDDFT计算。分阶段实施。"
            ),
        }
        sections_bad = {
            "立项依据": "然而该方法存在问题。该现象导致结果异常。",
            "研究内容": "大概我们会做一些工作。",
        }

        # [1/21] 初始化
        print("\n[1/21] 初始化（创建空状态）...")
        inspector = ProposalInspector(proposal_dir)
        assert inspector.review_dir.exists(), "05_review 目录应已创建"
        assert inspector._lock_name.startswith("inspection-"), "锁名前缀应为 inspection-"
        assert inspector.get_inspection_report() == {}, "初始应无报告"
        assert inspector.get_iteration_history() == [], "初始应无迭代"
        print(f"  状态路径: {inspector.state_path}")
        print(f"  锁名: {inspector._lock_name}")
        print("  ✓ 空状态初始化成功")

        # [2/21] 完整六维检查（优质章节，passed=True）
        print("\n[2/21] 完整六维检查（优质章节，passed=True）...")
        report = inspector.inspect(sections_good)
        assert set(report["dimensions"].keys()) == set(DIMENSIONS.keys()), "六维齐全"
        assert report["overall_score"] >= SCORE_THRESHOLDS["pass"], \
            f"优质章节总分应≥{SCORE_THRESHOLDS['pass']}，实际 {report['overall_score']:.2f}"
        assert report["critical_count"] == 0, "优质章节不应有严重问题"
        assert report["passed"] is True, "优质章节应通过"
        assert report["iteration"] == 1, "首次 inspect 迭代号应为 1"
        assert report["report_id"].startswith("rpt_"), "report_id 应有前缀"
        print(f"  总分: {report['overall_score']:.2f}")
        print(f"  问题数: {report['total_issues']}")
        print(f"  通过: {report['passed']}")
        print("  ✓ 六维齐全、优质章节通过")

        # [3/21] 单维度检查 logical_consistency
        print("\n[3/21] 单维度检查 logical_consistency...")
        result = inspector.check_dimension("logical_consistency", sections_good)
        assert result["dimension"] == "logical_consistency"
        assert 0.0 <= result["score"] <= 1.0
        assert "issues" in result and isinstance(result["issues"], list)
        assert "details" in result and "contradictions_found" in result["details"]
        print(f"  分数: {result['score']:.2f}")
        print(f"  矛盾: {result['details']['contradictions_found']}")
        print("  ✓ 结构正确（dimension/score/issues/details）")

        # [4/21] 单维度检查 evidence_sufficiency
        print("\n[4/21] 单维度检查 evidence_sufficiency...")
        result = inspector.check_dimension("evidence_sufficiency", sections_good)
        assert result["dimension"] == "evidence_sufficiency"
        assert "total_claim_paragraphs" in result["details"]
        assert "paragraphs_with_citations" in result["details"]
        print(f"  分数: {result['score']:.2f}")
        print(f"  论断段: {result['details']['total_claim_paragraphs']}")
        print("  ✓ 结构正确")

        # [5/21] 问题识别与严重性分级
        print("\n[5/21] 问题识别与严重性分级（劣质章节）...")
        report_bad = inspector.inspect(sections_bad)
        issues_bad = inspector.identify_issues(report_bad["dimensions"])
        assert len(issues_bad) > 0, "劣质章节应识别出问题"
        # issue_id 顺序赋值
        for idx, issue in enumerate(issues_bad, start=1):
            assert issue["issue_id"] == f"issue_{idx:03d}", \
                f"issue_id 应为 issue_{idx:03d}，实际 {issue['issue_id']}"
        severities = {i["severity"] for i in issues_bad}
        assert severities.issubset(set(SEVERITY_LEVELS.keys())), "严重性级别合法"
        assert report_bad["overall_score"] < SCORE_THRESHOLDS["pass"], "劣质章节应未达通过线"
        print(f"  问题数: {len(issues_bad)}")
        print(f"  严重性分布: {sorted(severities)}")
        print(f"  首个 issue_id: {issues_bad[0]['issue_id']}")
        print("  ✓ issue_id 顺序赋值、严重性分级正确")

        # [6/21] 策略生成 - targeted_repair
        print("\n[6/21] 策略生成 - targeted_repair...")
        inspector._last_dimension_scores = {d: 0.9 for d in DIMENSIONS}
        inspector._last_overall_score = 0.85
        issues_t = [_mock_issue("evidence_sufficiency", "major")]
        strategy = inspector.generate_strategy(issues_t)
        assert strategy["level"] == "targeted_repair", f"期望 targeted_repair，实际 {strategy['level']}"
        assert "actions" in strategy and len(strategy["actions"]) == 1
        assert 0.0 <= strategy["estimated_improvement"] <= 0.4
        print(f"  级别: {strategy['level']} ({strategy['level_label']})")
        print(f"  依据: {strategy['reason']}")
        print(f"  预期提升: +{strategy['estimated_improvement']}")
        print("  ✓ targeted_repair 判定正确")

        # [7/21] 策略生成 - paragraph_rewrite（重要>2）
        print("\n[7/21] 策略生成 - paragraph_rewrite（重要>2）...")
        inspector._last_dimension_scores = {d: 0.9 for d in DIMENSIONS}
        inspector._last_overall_score = 0.70
        issues_rw = [_mock_issue("evidence_sufficiency", "major") for _ in range(3)]
        strategy = inspector.generate_strategy(issues_rw)
        assert strategy["level"] == "paragraph_rewrite", f"期望 paragraph_rewrite，实际 {strategy['level']}"
        print(f"  级别: {strategy['level']} ({strategy['level_label']})")
        print(f"  依据: {strategy['reason']}")
        print("  ✓ paragraph_rewrite（重要>2）判定正确")

        # [8/21] 策略生成 - paragraph_rewrite（表达分数<0.6）
        print("\n[8/21] 策略生成 - paragraph_rewrite（表达分数<0.6）...")
        inspector._last_dimension_scores = {d: 0.9 for d in DIMENSIONS}
        inspector._last_dimension_scores["expression_quality"] = 0.50
        inspector._last_overall_score = 0.75
        issues_rw2 = [_mock_issue("evidence_sufficiency", "major")]
        strategy = inspector.generate_strategy(issues_rw2)
        assert strategy["level"] == "paragraph_rewrite", f"期望 paragraph_rewrite，实际 {strategy['level']}"
        print(f"  级别: {strategy['level']} ({strategy['level_label']})")
        print(f"  依据: {strategy['reason']}")
        print("  ✓ paragraph_rewrite（表达<0.6）判定正确")

        # [9/21] 策略生成 - structural_adjustment（逻辑分数<0.6）
        print("\n[9/21] 策略生成 - structural_adjustment（逻辑分数<0.6）...")
        inspector._last_dimension_scores = {d: 0.9 for d in DIMENSIONS}
        inspector._last_dimension_scores["logical_consistency"] = 0.50
        inspector._last_overall_score = 0.70
        issues_st = [_mock_issue("logical_consistency", "major")]
        strategy = inspector.generate_strategy(issues_st)
        assert strategy["level"] == "structural_adjustment", f"期望 structural_adjustment，实际 {strategy['level']}"
        print(f"  级别: {strategy['level']} ({strategy['level_label']})")
        print(f"  依据: {strategy['reason']}")
        print("  ✓ structural_adjustment（逻辑<0.6）判定正确")

        # [10/21] 策略生成 - structural_adjustment（结构类问题≥2）
        print("\n[10/21] 策略生成 - structural_adjustment（结构类问题≥2）...")
        inspector._last_dimension_scores = {d: 0.9 for d in DIMENSIONS}
        inspector._last_overall_score = 0.70
        issues_st2 = [
            _mock_issue("logical_consistency", "major"),
            _mock_issue("academic_norms", "major"),
        ]
        strategy = inspector.generate_strategy(issues_st2)
        assert strategy["level"] == "structural_adjustment", f"期望 structural_adjustment，实际 {strategy['level']}"
        print(f"  级别: {strategy['level']} ({strategy['level_label']})")
        print(f"  依据: {strategy['reason']}")
        print("  ✓ structural_adjustment（结构类问题≥2）判定正确")

        # [11/21] 策略生成 - rollback_regeneration（总分<0.5）
        print("\n[11/21] 策略生成 - rollback_regeneration（总分<0.5）...")
        inspector._last_dimension_scores = {d: 0.9 for d in DIMENSIONS}
        inspector._last_overall_score = 0.40
        issues_rb = [_mock_issue("evidence_sufficiency", "major")]
        strategy = inspector.generate_strategy(issues_rb)
        assert strategy["level"] == "rollback_regeneration", f"期望 rollback_regeneration，实际 {strategy['level']}"
        print(f"  级别: {strategy['level']} ({strategy['level_label']})")
        print(f"  依据: {strategy['reason']}")
        print("  ✓ rollback_regeneration（总分<0.5）判定正确")

        # [12/21] 策略生成 - rollback_regeneration（严重>3）
        print("\n[12/21] 策略生成 - rollback_regeneration（严重>3）...")
        inspector._last_dimension_scores = {d: 0.9 for d in DIMENSIONS}
        inspector._last_overall_score = 0.85
        issues_rb2 = [_mock_issue("academic_norms", "critical") for _ in range(4)]
        strategy = inspector.generate_strategy(issues_rb2)
        assert strategy["level"] == "rollback_regeneration", f"期望 rollback_regeneration，实际 {strategy['level']}"
        print(f"  级别: {strategy['level']} ({strategy['level_label']})")
        print(f"  依据: {strategy['reason']}")
        print("  ✓ rollback_regeneration（严重>3）判定正确")

        # [13/21] 定向修复应用
        print("\n[13/21] 定向修复应用（targeted_repair）...")
        # 用独立 inspector 避免污染迭代历史
        td_dir = tmp / "T2_targeted"
        insp_t = ProposalInspector(td_dir)
        report_t = insp_t.inspect(sections_targeted)
        issues_t = insp_t.identify_issues(report_t["dimensions"])
        strategy_t = insp_t.generate_strategy(issues_t)
        assert strategy_t["level"] == "targeted_repair", \
            f"sections_targeted 应为 targeted_repair，实际 {strategy_t['level']}"
        new_sections = insp_t.apply_optimization(sections_targeted, strategy_t)
        # 至少一个 evidence 问题被标记需补充引用
        assert "需补充引用" in new_sections["立项依据"], "定向修复后应含 [需补充引用]"
        # 原章节未被修改
        assert "需补充引用" not in sections_targeted["立项依据"], "原章节不应被修改"
        print(f"  策略级别: {strategy_t['level']}")
        print(f"  修复后段落片段: ...{new_sections['立项依据'][-30:]}")
        print("  ✓ 定向修复应用成功，原章节未被修改")

        # [14/21] 检查报告获取
        print("\n[14/21] 检查报告获取...")
        latest = inspector.get_inspection_report()
        assert latest != {}, "应能获取最新报告"
        assert latest.get("report_id") == report_bad.get("report_id"), "应为最近一次 inspect 的报告"
        assert "dimensions" in latest and "strategy" in latest
        print(f"  报告ID: {latest['report_id']}")
        print(f"  迭代: 第 {latest['iteration']} 次")
        print(f"  总分: {latest['overall_score']:.2f}")
        print("  ✓ 最新报告获取正确")

        # [15/21] 迭代历史追踪
        print("\n[15/21] 迭代历史追踪（两次 inspect → 2 条迭代）...")
        hist_dir = tmp / "T3_history"
        insp_h = ProposalInspector(hist_dir)
        insp_h.inspect(sections_good)
        insp_h.inspect(sections_good)
        history = insp_h.get_iteration_history()
        assert len(history) == 2, f"应有 2 条迭代，实际 {len(history)}"
        assert history[0]["iteration"] == 1
        assert history[1]["iteration"] == 2
        # 第二次 score_change 应为 0（相同章节）
        assert history[1]["score_change"] == 0.0, "相同章节 score_change 应为 0"
        assert history[1]["improved"] is False, "相同章节 improved 应为 False"
        # sections_before 应为指纹
        assert isinstance(history[0]["sections_before"], dict)
        assert all(isinstance(v, str) for v in history[0]["sections_before"].values())
        print(f"  迭代数: {len(history)}")
        print(f"  迭代1分数: {history[0]['score']:.2f}")
        print(f"  迭代2 score_change: {history[1]['score_change']}")
        print("  ✓ 迭代历史记录正确")

        # [16/21] 停滞检测与人工复审建议
        print("\n[16/21] 停滞检测与人工复审建议（3 次同 sections）...")
        stag_dir = tmp / "T4_stagnation"
        insp_s = ProposalInspector(stag_dir)
        r1 = insp_s.inspect(sections_good)
        r2 = insp_s.inspect(sections_good)
        r3 = insp_s.inspect(sections_good)
        assert r1["manual_review_recommended"] is False, "首次不应建议复审"
        assert r2["manual_review_recommended"] is False, "第2次不应建议复审（stagnation=1）"
        assert r3["manual_review_recommended"] is True, "第3次应建议人工复审（stagnation>=2）"
        print(f"  迭代1复审建议: {r1['manual_review_recommended']}")
        print(f"  迭代2复审建议: {r2['manual_review_recommended']}")
        print(f"  迭代3复审建议: {r3['manual_review_recommended']}")
        print("  ✓ 停滞检测正确，连续 2 次无提升触发人工复审建议")

        # [17/21] Markdown 导出
        print("\n[17/21] Markdown 导出...")
        md = inspector.export_report("markdown")
        assert md.startswith("# 申请书自检报告"), "Markdown 应以标题开头"
        assert "六维检查结果" in md
        assert "优化策略" in md
        assert "问题清单" in md
        print(f"  Markdown 行数: {len(md.splitlines())}")
        print("-" * 40)
        print("\n".join(md.splitlines()[:12]))
        print("-" * 40)
        print("  ✓ Markdown 导出正确")

        # [18/21] JSON 导出
        print("\n[18/21] JSON 导出...")
        js = inspector.export_report("json")
        parsed = json.loads(js)
        assert parsed["report_id"] == inspector.get_inspection_report()["report_id"]
        assert "dimensions" in parsed
        assert "overall_score" in parsed
        # 中文不被转义
        assert "\\u" not in js, "JSON 中中文不应被转义"
        print(f"  JSON 字符数: {len(js)}")
        print("  ✓ JSON 导出正确（中文不转义）")

        # [19/21] 引文检查集成
        print("\n[19/21] 引文检查集成（mock CitationManager）...")
        mock_cm = _MockCitationManager()
        cit_result = inspector.check_citations(sections_good, mock_cm)
        assert cit_result["dimension"] == "citations"
        assert cit_result["score"] < 1.0, "有缺失引文时分数应<1.0"
        severities = [i["severity"] for i in cit_result["issues"]]
        assert "critical" in severities, "缺失引文应为 critical"
        assert cit_result["details"]["missing"] == [3]
        print(f"  分数: {cit_result['score']:.2f}")
        print(f"  缺失: {cit_result['details']['missing']}")
        print(f"  问题严重性: {sorted(set(severities))}")
        print("  ✓ 引文检查集成正确（缺失引文 → critical）")

        # [20/21] 分数阈值 / 通过判定
        print("\n[20/21] 分数阈值 / 通过判定...")
        # 优质通过
        pass_dir = tmp / "T5_pass"
        insp_p = ProposalInspector(pass_dir)
        rp = insp_p.inspect(sections_good)
        assert rp["passed"] is True, "优质章节应通过"
        assert rp["overall_score"] >= SCORE_THRESHOLDS["pass"]
        # 劣质未通过
        fail_dir = tmp / "T6_fail"
        insp_f = ProposalInspector(fail_dir)
        rf = insp_f.inspect(sections_bad)
        assert rf["passed"] is False, "劣质章节应未通过"
        assert rf["overall_score"] < SCORE_THRESHOLDS["pass"]
        print(f"  优质: 总分 {rp['overall_score']:.2f} → {'通过' if rp['passed'] else '未通过'}")
        print(f"  劣质: 总分 {rf['overall_score']:.2f} → {'通过' if rf['passed'] else '未通过'}")
        print(f"  通过阈值: {SCORE_THRESHOLDS['pass']}")
        print("  ✓ 通过判定逻辑正确")

        # [21/21] 原子写入 + 文件锁
        print("\n[21/21] 原子写入 + 文件锁...")
        assert inspector.state_path.exists(), "状态文件应存在"
        raw = load_json(inspector.state_path, {})
        assert "iterations" in raw
        assert "latest_report" in raw
        assert "report_seq" in raw
        assert raw["report_seq"] >= 2, "应有至少 2 次报告序号"
        # 重新加载一致性
        insp_reload = ProposalInspector(proposal_dir)
        assert insp_reload.get_inspection_report()["report_id"] == latest["report_id"], "重载后报告一致"
        assert len(insp_reload.get_iteration_history()) == len(inspector.get_iteration_history())
        # 锁名唯一性
        assert inspector._lock_name != insp_p._lock_name, "不同 proposal 锁名应不同"
        # JSON 格式
        raw_text = inspector.state_path.read_text(encoding="utf-8")
        assert "  \"iterations\"" in raw_text, "应为缩进格式"
        assert "\\u" not in raw_text, "中文不应被转义"
        print(f"  状态文件: {inspector.state_path}")
        print(f"  迭代数: {len(raw['iterations'])}")
        print(f"  report_seq: {raw['report_seq']}")
        print(f"  重载报告ID: {insp_reload.get_inspection_report()['report_id']}")
        print("  ✓ 原子写入 + 文件锁 + 数据一致性验证通过")

        # 附加：迭代上限保护
        print("\n[附加] 迭代上限保护（>5 次仅保留最近 5 条）...")
        cap_dir = tmp / "T7_cap"
        insp_c = ProposalInspector(cap_dir)
        for _ in range(7):
            insp_c.inspect(sections_good)
        cap_history = insp_c.get_iteration_history()
        assert len(cap_history) == MAX_ITERATIONS, \
            f"应仅保留 {MAX_ITERATIONS} 条，实际 {len(cap_history)}"
        print(f"  7 次 inspect 后保留: {len(cap_history)} 条")
        print("  ✓ 迭代上限保护正确")

        # 附加：未知维度拒绝
        print("\n[附加] 未知维度拒绝...")
        try:
            inspector.check_dimension("unknown_dim", sections_good)
            raise AssertionError("应拒绝未知维度")
        except ValueError as e:
            print(f"  ✓ 拒绝未知维度: {e}")

        # 附加：未知导出格式拒绝
        print("\n[附加] 未知导出格式拒绝...")
        try:
            inspector.export_report("xml")
            raise AssertionError("应拒绝未知格式")
        except ValueError as e:
            print(f"  ✓ 拒绝未知格式: {e}")

        print("\n" + "=" * 50)
        print("✓ proposal_inspector 自检全部通过")
        print("=" * 50)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print("(已清理临时目录)")


class _MockCitationManager:
    """自检用 mock 引文管理器。"""

    def validate_citations(self, text: str) -> Dict[str, Any]:
        return {
            "valid": False,
            "cited_numbers": [1, 2, 3],
            "missing": [3],
            "unused": ["ref_002"],
            "total_refs": 2,
            "cited_count": 1,
            "uncited_count": 1,
        }


def _mock_issue(dimension: str, severity: str) -> Dict[str, Any]:
    """构造测试用问题对象。"""
    return {
        "issue_id": "",
        "dimension": dimension,
        "section": "测试章节",
        "paragraph_index": 0,
        "severity": severity,
        "description": "测试问题描述",
        "suggestion": "测试建议",
        "auto_fixable": False,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="申请书自检与优化引擎")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
