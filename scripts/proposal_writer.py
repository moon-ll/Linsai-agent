#!/usr/bin/env python3
"""申请书撰写引擎 — 研究管线"申请书撰写"阶段核心模块。

从科学问题框架（question_architect 产物）出发，按 NSFC 面上项目格式
生成申请书内容章节。采用基于规则的模板组装（v1，不依赖 LLM），
将问题框架的问答、知识库证据、文献引文组装为结构化的 markdown 段落。

位于研究管线"申请书撰写"阶段：
    ... → 03_question（科学问题构建） → 04_proposal（申请书撰写） → 05_review ...

六章节结构（面上项目内容部分，不含研究基础/工作条件/研究人员）：
    1. 立项依据  — 研究背景、文献综述、科学意义、研究缺口
    2. 研究内容  — 研究目标、关键科学问题、研究范围
    3. 研究方案  — 研究方法、技术路线、可行性分析
    4. 特色与创新 — 创新点、与现有工作对比
    5. 年度研究计划 — 三年计划
    6. 预期研究成果 — 论文、方法、数据集

章节内容组装流程：
    1. 从问题框架按要素类型提取相关问题
    2. 将问题 + 假设转换为陈述性内容段落
    3. 插入引文占位符 [CITE:ref_key] 供后续注入
    4. 按 NSFC 格式添加结构标记（标题、列表）
    5. 统计字数与段落数

状态持久化：
    {proposal_dir}/04_proposal/sections/{section_id}.md  — 各章节 markdown 内容
    {proposal_dir}/04_proposal/proposal-state.json       — 章节元数据
    使用 common.save_json 原子写入 + common.file_lock("proposal-{hash}") 跨进程锁。

用法:
    >>> from pathlib import Path
    >>> from proposal_writer import ProposalWriter
    >>> writer = ProposalWriter(Path("/data/proposals/T1"))
    >>> framework = {
    ...     "framework_id": "fw_001",
    ...     "topic_title": "量子度规对固体HHG光谱的调制机制研究",
    ...     "elements": {"立项依据": ["q_001"], ...},
    ...     "main_questions": ["q_001", ...],
    ...     "all_questions": {"q_001": {"text": "...", "hypothesis": "..."}, ...},
    ...     "_placeholders": {"concept": "量子度规", "phenomenon": "固体HHG", ...},
    ... }
    >>> result = writer.write_proposal(framework, gap_report=None, taste_profile=None)
    >>> sec = writer.get_section("立项依据")
    >>> md = writer.export_proposal("markdown")
    >>> progress = writer.get_writing_progress()

命令行自检:
    python3 scripts/proposal_writer.py --self-check

规范：仅 Python 标准库，pathlib.Path 路径处理，JSON ensure_ascii=False，时间戳 UTC ISO。
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock, lazy_load

# v6.3.2 接入 LLM 网关（共享基础设施层），让申请书撰写具备"大脑"
try:
    from llm_gateway import is_llm_available, safe_llm_complete
    _LLM_OK = is_llm_available()
except Exception:
    _LLM_OK = False
    def safe_llm_complete(*a, **kw):  # type: ignore
        return kw.get("fallback", "")

__all__ = [
    "ProposalWriter",
    "SECTION_DEFINITIONS",
    "SECTION_ORDER",
    "SECTION_TEMPLATES",
    "WRITING_STYLE_PROFILES",
    "SECTION_STATUS_FLOW",
]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 章节顺序（NSFC 面上项目内容部分排列顺序）
SECTION_ORDER = (
    "立项依据",
    "研究内容",
    "研究方案",
    "特色与创新",
    "年度研究计划",
    "预期研究成果",
)

# 章节定义：名称 → {section_id, order, description, source_elements, min_word_count}
SECTION_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "立项依据": {
        "section_id": "sec_01",
        "order": 1,
        "description": "项目立项依据：研究背景、文献综述、科学意义、研究缺口",
        "source_elements": ["立项依据"],
        "min_word_count": 2000,
    },
    "研究内容": {
        "section_id": "sec_02",
        "order": 2,
        "description": "研究内容：研究目标、关键科学问题、研究范围",
        "source_elements": ["科学问题", "研究内容"],
        "min_word_count": 1500,
    },
    "研究方案": {
        "section_id": "sec_03",
        "order": 3,
        "description": "研究方案：研究方法、技术路线、可行性分析",
        "source_elements": ["研究方案"],
        "min_word_count": 1500,
    },
    "特色与创新": {
        "section_id": "sec_04",
        "order": 4,
        "description": "特色与创新：创新点、与现有工作对比",
        "source_elements": ["特色与创新"],
        "min_word_count": 800,
    },
    "年度研究计划": {
        "section_id": "sec_05",
        "order": 5,
        "description": "年度研究计划：三年研究进度安排",
        "source_elements": [],
        "min_word_count": 600,
    },
    "预期研究成果": {
        "section_id": "sec_06",
        "order": 6,
        "description": "预期研究成果：论文、方法、数据集",
        "source_elements": [],
        "min_word_count": 500,
    },
}

# 章节模板说明（用于文档化各章节的组装逻辑）
SECTION_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "立项依据": {
        "subsections": ["研究背景", "国内外研究现状", "科学意义", "拟解决的关键科学问题"],
        "content_sources": ["立项依据问题", "gap_report覆盖率", "taste_profile方向", "gap_report缺口"],
    },
    "研究内容": {
        "subsections": ["研究目标", "关键科学问题", "研究内容"],
        "content_sources": ["科学问题问题", "研究内容问题"],
    },
    "研究方案": {
        "subsections": ["研究方法", "技术路线", "可行性分析"],
        "content_sources": ["研究方案问题", "gap_report方法"],
    },
    "特色与创新": {
        "subsections": ["创新点", "与现有工作的比较"],
        "content_sources": ["特色与创新问题"],
    },
    "年度研究计划": {
        "subsections": ["第一年", "第二年", "第三年"],
        "content_sources": ["研究内容推导"],
    },
    "预期研究成果": {
        "subsections": ["论文发表", "方法与技术", "数据集"],
        "content_sources": ["研究范围推导"],
    },
}

# 写作风格画像（基于 taste_profile 维度调整写作风格）
WRITING_STYLE_PROFILES: Dict[str, Dict[str, Any]] = {
    "theoretical_depth": {
        "thresholds": {"high": 0.7, "medium": 0.4},
        "profiles": {
            "high": {
                "intro_prefix": "从理论框架出发，",
                "background_style": "强调理论体系与物理图像",
                "tone": "formal",
            },
            "medium": {
                "intro_prefix": "",
                "background_style": "理论与实验并重",
                "tone": "balanced",
            },
            "low": {
                "intro_prefix": "从实验现象出发，",
                "background_style": "以实验现象为切入点",
                "tone": "accessible",
            },
        },
    },
    "novelty": {
        "thresholds": {"high": 0.7, "medium": 0.4},
        "profiles": {
            "high": {
                "innovation_emphasis": True,
                "innovation_keywords": ["首次", "原创", "新颖", "突破"],
                "innovation_intro": "本研究在以下方面具有显著的创新性贡献：",
            },
            "medium": {
                "innovation_emphasis": False,
                "innovation_keywords": ["新"],
                "innovation_intro": "本研究的主要特色与创新点包括：",
            },
            "low": {
                "innovation_emphasis": False,
                "innovation_keywords": [],
                "innovation_intro": "本研究的主要特色包括：",
            },
        },
    },
    "interdisciplinarity": {
        "thresholds": {"high": 0.7, "medium": 0.4},
        "profiles": {
            "high": {
                "background_detail": "extensive",
                "extra_background": True,
                "extra_background_text": "本研究涉及多个学科领域的交叉融合，需要综合运用多学科方法与视角。",
            },
            "medium": {
                "background_detail": "standard",
                "extra_background": False,
                "extra_background_text": "",
            },
            "low": {
                "background_detail": "concise",
                "extra_background": False,
                "extra_background_text": "",
            },
        },
    },
    "rigor": {
        "thresholds": {"high": 0.7, "medium": 0.4},
        "profiles": {
            "high": {
                "citation_density_boost": 1.5,
                "claim_hedging": "在表述论断时严格标注引用来源",
            },
            "medium": {
                "citation_density_boost": 1.0,
                "claim_hedging": "",
            },
            "low": {
                "citation_density_boost": 0.5,
                "claim_hedging": "",
            },
        },
    },
}

# 章节状态机
SECTION_STATUS_FLOW: Dict[str, set] = {
    "draft": {"reviewed", "final"},
    "reviewed": {"final", "draft"},
    "final": set(),  # 终态
}

# 引文占位符正则：匹配 [CITE:ref_key]
CITE_PLACEHOLDER_PATTERN = re.compile(r'\[CITE:([^\]]+)\]')

# 年度计划模板（三年）
YEAR_PLAN_TEMPLATE = [
    {
        "year": 1,
        "title": "第一年",
        "focus": "理论基础构建与前期实验",
        "activities": [
            "完成文献调研与理论框架搭建",
            "开展初步实验/计算，验证方法可行性",
            "确定关键技术参数与实验方案",
        ],
    },
    {
        "year": 2,
        "title": "第二年",
        "focus": "核心实验与数据分析",
        "activities": [
            "开展系统性实验/计算，获取核心数据",
            "进行数据分析与理论对比",
            "发表阶段性研究成果",
        ],
    },
    {
        "year": 3,
        "title": "第三年",
        "focus": "深入验证与成果总结",
        "activities": [
            "补充验证性实验/计算",
            "完善理论模型与物理解释",
            "整理研究成果，撰写总结报告",
        ],
    },
]


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _count_words(text: str) -> int:
    """统计字数（中文字符按字计，英文按词计，标点不计）。"""
    if not text:
        return 0
    # 中文字符数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 去掉中文字符后的英文单词数
    no_chinese = re.sub(r'[\u4e00-\u9fff]', ' ', text)
    no_punct = re.sub(r'[#\*\-\[\]\(\)<>|`~!@#$%^&+=/\\.,;:\'"!?，。；：""''（）、…—\n\r\t ]', ' ', no_chinese)
    english_words = len([w for w in no_punct.split() if len(w) > 1])
    return chinese_chars + english_words


def _count_paragraphs(text: str) -> int:
    """统计段落数（按空行分割，仅计非空段落）。"""
    if not text:
        return 0
    paras = re.split(r'\n\s*\n', text)
    return len([p for p in paras if p.strip()])


def _classify_taste(value: float, thresholds: Dict[str, float]) -> str:
    """将 taste 维度值分类为 high/medium/low。"""
    if value >= thresholds["high"]:
        return "high"
    elif value >= thresholds["medium"]:
        return "medium"
    else:
        return "low"


def _extract_questions_by_element(
    framework: Dict[str, Any], element: str
) -> List[Dict[str, Any]]:
    """从问题框架按要素类型提取问题列表（按 level 排序）。"""
    all_questions = framework.get("all_questions", {})
    if not isinstance(all_questions, dict):
        return []
    result: List[Dict[str, Any]] = []
    for q in all_questions.values():
        if isinstance(q, dict) and q.get("element") == element:
            result.append(q)
    result.sort(key=lambda x: (x.get("level", 0), x.get("question_id", "")))
    return result


def _question_to_statement(question: Dict[str, Any]) -> str:
    """将问题转换为陈述性内容段落。

    优先使用假设；退化时去掉问号补句号；最差兜底。
    """
    hypothesis = question.get("hypothesis", "")
    text = question.get("text", "")
    if hypothesis:
        return hypothesis + "。"
    if text:
        return text.rstrip("？?") + "。"
    return f"本研究将探讨相关问题。"


def _format_cite_placeholder(ref_key: str) -> str:
    """格式化引文占位符。"""
    return f"[CITE:{ref_key}]"


def _insert_citations_for_literature(literature: List[str]) -> str:
    """为文献列表生成引文占位符字符串。"""
    if not literature:
        return ""
    parts = [_format_cite_placeholder(r) for r in literature if r]
    return "".join(parts)


def _extract_placeholders(framework: Dict[str, Any]) -> Dict[str, str]:
    """从框架提取占位符（含默认值兜底）。"""
    placeholders = framework.get("_placeholders", {})
    if not isinstance(placeholders, dict):
        placeholders = {}
    defaults = {
        "concept": "核心概念",
        "phenomenon": "目标现象",
        "aspect": "关键特性",
        "method": "理论分析",
        "quantity": "相关物理量",
        "condition": "不同实验条件",
        "field": "强场超快光学",
        "theory": "所选理论",
        "observation": "实验观测",
        "alternative": "现有理论",
        "system_A": "本系统",
        "system_B": "对比体系",
    }
    for k, v in defaults.items():
        if k not in placeholders or not placeholders[k]:
            placeholders[k] = v
    return placeholders


def _apply_taste_style(
    content: str, section_name: str, taste_profile: Optional[Dict[str, Any]]
) -> str:
    """根据 taste_profile 调整写作风格。

    调整维度：
    - theoretical_depth：高 → 添加理论框架引导语
    - novelty：高 → 在创新部分添加强调语与创新关键词
    - interdisciplinarity：高 → 添加跨学科背景说明
    """
    if not taste_profile or not content:
        return content

    # theoretical_depth
    td_value = float(taste_profile.get("theoretical_depth", 0.5))
    td_profile = WRITING_STYLE_PROFILES["theoretical_depth"]
    td_level = _classify_taste(td_value, td_profile["thresholds"])
    td_style = td_profile["profiles"][td_level]
    if section_name == "立项依据" and td_style.get("intro_prefix"):
        marker = "## 研究背景\n\n"
        if marker in content:
            content = content.replace(
                marker, f"{marker}{td_style['intro_prefix']}", 1
            )

    # novelty
    nov_value = float(taste_profile.get("novelty", 0.5))
    nov_profile = WRITING_STYLE_PROFILES["novelty"]
    nov_level = _classify_taste(nov_value, nov_profile["thresholds"])
    nov_style = nov_profile["profiles"][nov_level]
    if section_name == "特色与创新" and nov_style.get("innovation_intro"):
        marker = "## 创新点\n\n"
        if marker in content and nov_style["innovation_intro"] not in content:
            content = content.replace(
                marker, f"{marker}{nov_style['innovation_intro']}\n\n", 1
            )

    # interdisciplinarity
    inter_value = float(taste_profile.get("interdisciplinarity", 0.5))
    inter_profile = WRITING_STYLE_PROFILES["interdisciplinarity"]
    inter_level = _classify_taste(inter_value, inter_profile["thresholds"])
    inter_style = inter_profile["profiles"][inter_level]
    if section_name == "立项依据" and inter_style.get("extra_background"):
        extra = inter_style.get("extra_background_text", "")
        if extra and extra not in content:
            # 在科学意义前插入跨学科说明
            marker = "## 科学意义"
            if marker in content:
                content = content.replace(
                    marker, f"{extra}\n\n{marker}", 1
                )

    return content


# ---------------------------------------------------------------------------
# 各章节内容组装函数
# ---------------------------------------------------------------------------

def _assemble_rationale(
    framework: Dict[str, Any],
    gap_report: Optional[Dict[str, Any]],
    placeholders: Dict[str, str],
) -> str:
    """组装立项依据章节内容。"""
    concept = placeholders.get("concept", "")
    field = placeholders.get("field", "")
    phenomenon = placeholders.get("phenomenon", "")
    aspect = placeholders.get("aspect", "")
    topic_title = framework.get("topic_title", "")

    questions = _extract_questions_by_element(framework, "立项依据")
    main_q = questions[0] if questions else {}
    hypothesis = main_q.get("hypothesis", "")

    # 研究背景
    bg_lines: List[str] = []
    bg_lines.append(f"{concept}作为{field}领域的核心研究对象，其{aspect}的研究具有重要的科学意义。")
    bg_lines.append(
        f"近年来，{phenomenon}的{aspect}引起了学术界的广泛关注"
        + _insert_citations_for_literature(main_q.get("evidence", {}).get("literature", []))
        + "。"
    )
    bg_lines.append(
        f"当前，{concept}如何调制{phenomenon}的{aspect}已成为该领域亟待解决的关键问题。"
    )
    if hypothesis:
        bg_lines.append(f"{hypothesis}。")

    # 国内外研究现状
    review_lines: List[str] = []
    sub_questions = [q for q in questions if q.get("level", 0) > 0]
    for sq in sub_questions[:4]:
        review_lines.append(f"- {_question_to_statement(sq)}")
    if not review_lines:
        review_lines.append(f"- 围绕{concept}与{phenomenon}的关系，国内外学者已开展大量研究。")

    # 研究缺口
    gap_lines: List[str] = []
    if gap_report and isinstance(gap_report, dict):
        gaps = gap_report.get("gaps", [])
        if isinstance(gaps, list):
            for g in gaps[:5]:
                if isinstance(g, dict):
                    desc = g.get("description") or g.get("gap_id", "未知缺口")
                    gap_lines.append(f"- {desc}")
    if not gap_lines:
        gap_lines.append(f"- 现有研究对{concept}在{phenomenon}中的作用机制认识尚不充分。")
        gap_lines.append(f"- 缺乏系统性的{aspect}实验/理论分析。")

    # 科学意义
    significance_lines: List[str] = []
    significance_lines.append(f"本研究的开展将{hypothesis or f'深入揭示{concept}对{phenomenon}的调制机制'}，"
                              f"对于推动{field}领域的发展具有重要意义。")
    significance_lines.append(f"1. 在理论层面，将建立{concept}与{phenomenon}之间的定量关系。")
    significance_lines.append(f"2. 在方法层面，将发展基于{placeholders.get('method', '理论分析')}的研究手段。")
    significance_lines.append(f"3. 在应用层面，将为{phenomenon}的调控提供新思路。")

    # 拟解决的关键科学问题
    problem_lines: List[str] = []
    main_text = main_q.get("text", f"{concept}如何调制{phenomenon}的{aspect}？")
    problem_lines.append(f"基于上述分析，本项目拟解决的核心科学问题是：{main_text}")

    content = (
        f"# 立项依据\n\n"
        f"## 研究背景\n\n"
        + "\n".join(bg_lines)
        + "\n\n"
        f"## 国内外研究现状\n\n"
        + "\n".join(review_lines)
        + "\n\n"
        f"然而，现有研究仍存在以下不足：\n\n"
        + "\n".join(gap_lines)
        + "\n\n"
        f"## 科学意义\n\n"
        + "\n".join(significance_lines)
        + "\n\n"
        f"## 拟解决的关键科学问题\n\n"
        + "\n".join(problem_lines)
        + "\n"
    )
    if topic_title:
        content += f"\n> 课题：{topic_title}\n"
    return content


def _assemble_content_section(
    framework: Dict[str, Any],
    gap_report: Optional[Dict[str, Any]],
    placeholders: Dict[str, str],
) -> str:
    """组装研究内容章节。"""
    concept = placeholders.get("concept", "")
    phenomenon = placeholders.get("phenomenon", "")
    aspect = placeholders.get("aspect", "")

    science_questions = _extract_questions_by_element(framework, "科学问题")
    content_questions = _extract_questions_by_element(framework, "研究内容")

    main_science_q = science_questions[0] if science_questions else {}
    hypothesis = main_science_q.get("hypothesis", "")

    # 研究目标
    goal_lines: List[str] = []
    goal_lines.append(
        f"本项目旨在{hypothesis or f'揭示{concept}对{phenomenon}的{aspect}调制机制'}，"
        f"建立完整的理论框架与实验验证体系。"
    )

    # 关键科学问题
    problem_lines: List[str] = []
    for i, q in enumerate(science_questions[:3], 1):
        problem_lines.append(f"{i}. {_question_to_statement(q)}")
    if not problem_lines:
        problem_lines.append(f"1. {concept}如何调制{phenomenon}的{aspect}？")

    # 研究内容
    content_lines: List[str] = []
    for i, q in enumerate(content_questions[:4], 1):
        content_lines.append(f"{i}. {_question_to_statement(q)}")
    if not content_lines:
        content_lines.append(f"1. {concept}在不同条件下的{aspect}变化规律。")
        content_lines.append(f"2. {phenomenon}的关键参数测量与表征。")

    return (
        f"# 研究内容\n\n"
        f"## 研究目标\n\n"
        + "\n".join(goal_lines)
        + "\n\n"
        f"## 关键科学问题\n\n"
        + "\n".join(problem_lines)
        + "\n\n"
        f"## 研究内容\n\n"
        + "\n".join(content_lines)
        + "\n"
    )


def _assemble_plan(
    framework: Dict[str, Any],
    gap_report: Optional[Dict[str, Any]],
    placeholders: Dict[str, str],
) -> str:
    """组装研究方案章节。"""
    concept = placeholders.get("concept", "")
    phenomenon = placeholders.get("phenomenon", "")
    method = placeholders.get("method", "理论分析")
    quantity = placeholders.get("quantity", "相关物理量")

    plan_questions = _extract_questions_by_element(framework, "研究方案")
    main_q = plan_questions[0] if plan_questions else {}
    evidence = main_q.get("evidence", {})
    methods = evidence.get("methods", [])
    literature = evidence.get("literature", [])

    # 研究方法
    method_lines: List[str] = []
    if methods:
        method_lines.append(f"本研究将综合运用以下研究方法：")
        for i, m in enumerate(methods[:5], 1):
            method_lines.append(f"{i}. {m}")
    else:
        method_lines.append(f"本研究将采用{method}作为核心研究方法。")

    # 技术路线
    route_lines: List[str] = []
    sub_questions = [q for q in plan_questions if q.get("level", 0) > 0]
    for i, sq in enumerate(sub_questions[:4], 1):
        route_lines.append(f"{i}. {_question_to_statement(sq)}")
    if not route_lines:
        route_lines.append(f"1. 利用{method}计算/测量{concept}对{phenomenon}的影响。")
        route_lines.append(f"2. 系统改变实验条件，获取{quantity}的变化规律。")
        route_lines.append(f"3. 建立理论模型，与实验/计算结果对比验证。")

    # 可行性分析
    feasibility_lines: List[str] = []
    cite_str = _insert_citations_for_literature(literature)
    feasibility_lines.append(
        f"（1）方法可行性：所选{method}已在相关研究中得到验证{cite_str}，"
        f"可有效刻画{concept}对{phenomenon}的影响。"
    )
    feasibility_lines.append(
        f"（2）技术可行性：所需计算/实验条件在现有平台上可满足，"
        f"关键{quantity}的测量/计算精度有保障。"
    )
    feasibility_lines.append(
        f"（3）团队可行性：研究团队在{method}与{phenomenon}领域"
        f"具有扎实的前期工作基础。"
    )

    # gap_report 方法补充
    if gap_report and isinstance(gap_report, dict):
        gap_methods = gap_report.get("methods", [])
        if isinstance(gap_methods, list) and gap_methods:
            feasibility_lines.append(
                f"（4）方法补充：结合缺口分析，将引入{', '.join(str(m) for m in gap_methods[:3])}等方法。"
            )

    return (
        f"# 研究方案\n\n"
        f"## 研究方法\n\n"
        + "\n".join(method_lines)
        + "\n\n"
        f"## 技术路线\n\n"
        + "\n".join(route_lines)
        + "\n\n"
        f"## 可行性分析\n\n"
        + "\n".join(feasibility_lines)
        + "\n"
    )


def _assemble_innovation(
    framework: Dict[str, Any],
    gap_report: Optional[Dict[str, Any]],
    placeholders: Dict[str, str],
) -> str:
    """组装特色与创新章节。"""
    concept = placeholders.get("concept", "")
    phenomenon = placeholders.get("phenomenon", "")
    aspect = placeholders.get("aspect", "")

    innov_questions = _extract_questions_by_element(framework, "特色与创新")
    main_q = innov_questions[0] if innov_questions else {}
    hypothesis = main_q.get("hypothesis", "")

    # 创新点
    innov_lines: List[str] = []
    sub_questions = [q for q in innov_questions if q.get("level", 0) > 0]
    for i, sq in enumerate(sub_questions[:3], 1):
        innov_lines.append(f"{i}. {_question_to_statement(sq)}")
    if not innov_lines:
        innov_lines.append(f"1. 首次系统研究{concept}对{phenomenon}的{aspect}调制机制。")
        innov_lines.append(f"2. 提出基于{concept}的新方法/新模型。")
    if hypothesis:
        innov_lines.append(f"{len(innov_lines) + 1}. {hypothesis}。")

    # 与现有工作的比较
    compare_lines: List[str] = []
    if gap_report and isinstance(gap_report, dict):
        gaps = gap_report.get("gaps", [])
        if isinstance(gaps, list):
            for g in gaps[:3]:
                if isinstance(g, dict):
                    gtype = g.get("type", "未知")
                    desc = g.get("description", g.get("gap_id", ""))
                    compare_lines.append(f"- 针对现有研究中{gtype}层面的缺口（{desc}），本研究提供了新的解决方案。")
    if not compare_lines:
        compare_lines.append(f"- 相比现有工作，本研究在{aspect}上具有更系统的分析。")
        compare_lines.append(f"- 本研究将{concept}与{phenomenon}的研究推进到定量层面。")

    return (
        f"# 特色与创新\n\n"
        f"## 创新点\n\n"
        + "\n".join(innov_lines)
        + "\n\n"
        f"## 与现有工作的比较\n\n"
        + "\n".join(compare_lines)
        + "\n"
    )


def _assemble_year_plan(
    framework: Dict[str, Any],
    gap_report: Optional[Dict[str, Any]],
    placeholders: Dict[str, str],
) -> str:
    """组装年度研究计划章节。"""
    concept = placeholders.get("concept", "")
    phenomenon = placeholders.get("phenomenon", "")

    lines: List[str] = ["# 年度研究计划\n"]
    for plan in YEAR_PLAN_TEMPLATE:
        lines.append(f"\n## {plan['title']}\n")
        lines.append(f"\n**研究重点**：{plan['focus']}\n")
        lines.append("\n主要工作：\n")
        for act in plan["activities"]:
            # 将模板活动与课题上下文结合
            adapted = act.replace("实验/计算", f"针对{concept}与{phenomenon}的实验/计算")
            lines.append(f"- {adapted}")

    return "\n".join(lines) + "\n"


def _assemble_expected_results(
    framework: Dict[str, Any],
    gap_report: Optional[Dict[str, Any]],
    placeholders: Dict[str, str],
) -> str:
    """组装预期研究成果章节。"""
    concept = placeholders.get("concept", "")
    phenomenon = placeholders.get("phenomenon", "")
    method = placeholders.get("method", "理论分析")

    # 论文发表
    pub_lines: List[str] = [
        f"- 预计在国内外核心学术期刊发表学术论文 3-5 篇，其中 SCI 收录不少于 3 篇。",
        f"- 论文主题涵盖{concept}对{phenomenon}的调制机制、{method}方法发展等方向。",
    ]

    # 方法与技术
    method_lines: List[str] = [
        f"- 建立基于{method}的{concept}研究方法体系。",
        f"- 发展{phenomenon}的{placeholders.get('aspect', '关键特性')}分析技术。",
    ]

    # 数据集
    data_lines: List[str] = [
        f"- 构建包含{concept}在不同条件下{phenomenon}数据的实验/计算数据集。",
        "- 形成可共享的研究数据与开源代码。",
    ]

    return (
        f"# 预期研究成果\n\n"
        f"## 论文发表\n\n"
        + "\n".join(pub_lines)
        + "\n\n"
        f"## 方法与技术\n\n"
        + "\n".join(method_lines)
        + "\n\n"
        f"## 数据集\n\n"
        + "\n".join(data_lines)
        + "\n"
    )


# 章节组装器映射表
_SECTION_ASSEMBLERS = {
    "立项依据": _assemble_rationale,
    "研究内容": _assemble_content_section,
    "研究方案": _assemble_plan,
    "特色与创新": _assemble_innovation,
    "年度研究计划": _assemble_year_plan,
    "预期研究成果": _assemble_expected_results,
}


# ---------------------------------------------------------------------------
# v6.3.2 LLM 章节增强 — 让申请书具备学术深度与实质论述
# ---------------------------------------------------------------------------

# 各章节的 LLM 增强指令（角色 + 任务 + 约束）
_LLM_SECTION_PROMPTS: Dict[str, Dict[str, str]] = {
    "立项依据": {
        "role": (
            "你是资深的 NSFC 面上项目评审专家与学术写作导师，深耕强场超快光学/"
            "阿秒科学/固体高次谐波领域。你擅长将零散的研究缺口与问题框架，"
            "凝练为逻辑严密、论证充分、符合国家自然科学基金规范的立项依据。"
        ),
        "task": (
            "请基于下方「模板草稿」，重写一份高质量的「立项依据」章节。\n"
            "要求：\n"
            "1. 保留原草稿的结构骨架（研究背景/国内外研究现状/科学意义/拟解决的关键科学问题）\n"
            "2. 将占位式表述替换为实质性的学术论述，补充物理机制解释与因果逻辑\n"
            "3. 国内外研究现状部分要体现领域发展脉络，而非简单罗列\n"
            "4. 保留所有 [CITE:xxx] 引文占位符原样不动\n"
            "5. 字数 800-1500 字，段落分明，避免空话套话\n"
            "6. 直接输出 Markdown 正文，不要加 ``` 代码块"
        ),
    },
    "研究内容": {
        "role": (
            "你是 NSFC 项目研究内容设计专家，擅长将科学问题分解为具体、可操作、"
            "层次分明的研究内容模块。"
        ),
        "task": (
            "请基于下方「模板草稿」，重写「研究内容」章节。\n"
            "要求：\n"
            "1. 明确研究目标（1 段）\n"
            "2. 将研究内容拆分为 3-4 个递进的子内容，每个子内容含目标与方法要点\n"
            "3. 阐述各子内容之间的逻辑关系\n"
            "4. 保留 [CITE:xxx] 占位符\n"
            "5. 字数 600-1000 字，直接输出 Markdown"
        ),
    },
    "研究方案": {
        "role": (
            "你是实验物理与方法学设计专家，擅长设计严谨可行的技术路线与实验方案。"
        ),
        "task": (
            "请基于下方「模板草稿」，重写「研究方案」章节。\n"
            "要求：\n"
            "1. 总体技术路线（含逻辑框图描述）\n"
            "2. 关键技术与方法（3-4 项，每项含原理简述）\n"
            "3. 可行性分析（理论/技术/设备三方面）\n"
            "4. 保留 [CITE:xxx] 占位符\n"
            "5. 字数 800-1200 字，直接输出 Markdown"
        ),
    },
    "特色与创新": {
        "role": "你是学术创新点提炼专家，擅长从研究内容中凝练出鲜明、可信的创新点。",
        "task": (
            "请基于下方「模板草稿」，重写「特色与创新之处」章节。\n"
            "要求：\n"
            "1. 提炼 2-3 个创新点，每个创新点含：创新内容 + 与现有工作的区别\n"
            "2. 避免空泛的\"首次\"\"填补空白\"，要具体说明新在哪里\n"
            "3. 保留 [CITE:xxx] 占位符\n"
            "4. 字数 400-600 字，直接输出 Markdown"
        ),
    },
}


def _llm_enhance_section(
    section_name: str,
    draft_content: str,
    framework: Dict[str, Any],
    placeholders: Dict[str, str],
    gap_report: Optional[Dict[str, Any]],
) -> tuple:
    """用 LLM 增强章节内容（锦上添花模式：失败则返回模板草稿）。

    Returns:
        (enhanced_content, meta) 其中 meta = {enhanced, provider, reason}
    """
    # LLM 不可用时直接降级
    if not _LLM_OK:
        return draft_content, {"enhanced": False, "reason": "LLM 不可用"}

    prompt_cfg = _LLM_SECTION_PROMPTS.get(section_name)
    if not prompt_cfg:
        # 无增强指令的章节（年度计划/预期成果）保留模板
        return draft_content, {"enhanced": False, "reason": "该章节无需 LLM 增强"}

    # 构建上下文：课题、缺口、关键概念
    topic_title = framework.get("topic_title", "")
    concept = placeholders.get("concept", "")
    phenomenon = placeholders.get("phenomenon", "")

    gap_summary = ""
    if gap_report and isinstance(gap_report, dict):
        gaps = gap_report.get("gaps", [])
        if isinstance(gaps, list):
            gap_lines = []
            for g in gaps[:5]:
                if isinstance(g, dict):
                    desc = g.get("description") or g.get("gap_id", "")
                    if desc:
                        gap_lines.append(f"- {desc}")
            gap_summary = "\n".join(gap_lines)

    context_block = f"【课题】{topic_title}\n【核心概念】{concept}\n【关键现象】{phenomenon}\n"
    if gap_summary:
        context_block += f"【已知研究缺口】\n{gap_summary}\n"

    user_prompt = (
        f"{prompt_cfg['task']}\n\n"
        f"=== 课题上下文 ===\n{context_block}\n"
        f"=== 模板草稿（请在此基础上重写）===\n{draft_content}\n"
    )

    fallback = draft_content
    enhanced = safe_llm_complete(
        prompt_cfg["role"],
        user_prompt,
        fallback=fallback,
        timeout=120,
    )

    # 校验：LLM 输出必须保留原草稿中的引文占位符（防止 LLM 删掉引用）
    if enhanced and enhanced != fallback:
        original_cites = set(re.findall(r"\[CITE:[^\]]+\]", draft_content))
        if original_cites:
            new_cites = set(re.findall(r"\[CITE:[^\]]+\]", enhanced))
            missing = original_cites - new_cites
            if missing:
                # 引文丢失，降级回模板（保证引用完整性）
                return fallback, {
                    "enhanced": False,
                    "reason": f"LLM 输出丢失引文占位符: {missing}",
                }
        return enhanced, {"enhanced": True, "provider": "llm"}

    return fallback, {"enhanced": False, "reason": "LLM 返回空或未变化"}


# ---------------------------------------------------------------------------
# ProposalWriter 类
# ---------------------------------------------------------------------------

class ProposalWriter:
    """申请书撰写引擎。

    从科学问题框架生成 NSFC 面上项目申请书内容章节。基于规则的模板组装
    （v1，不依赖 LLM），支持章节版本管理、增量更新、引文注入与全文导出。

    线程安全：所有写操作通过 common.file_lock（fcntl.flock 跨进程锁）保护
    read-modify-write 临界区，锁键基于 proposal_dir 路径哈希，不同 proposal 互不阻塞。
    """

    def __init__(self, proposal_dir: Path | str) -> None:
        """初始化申请书撰写引擎。

        Args:
            proposal_dir: proposal 根目录（Path 或字符串），
                          章节文件保存于其下的 04_proposal/。
        """
        self.proposal_dir = Path(proposal_dir)
        self.proposal_content_dir = self.proposal_dir / "04_proposal"
        self.sections_dir = self.proposal_content_dir / "sections"
        self.state_path = self.proposal_content_dir / "proposal-state.json"

        # 跨进程锁键：基于 proposal_dir 绝对路径哈希，避免不同 proposal 互相阻塞
        digest = hashlib.md5(
            str(self.proposal_dir.resolve()).encode("utf-8")
        ).hexdigest()[:12]
        self._lock_name = f"proposal-{digest}"

        # 确保目录结构存在
        self.proposal_content_dir.mkdir(parents=True, exist_ok=True)
        self.sections_dir.mkdir(parents=True, exist_ok=True)

        # 内存缓存
        self._state: Optional[Dict[str, Any]] = None
        self._lineage_tracker = None
        self._artifact_manager = None
        self._question_architect_module = None

    # ------------------------------------------------------------------
    # 模块懒加载
    # ------------------------------------------------------------------

    def _load_lineage_tracker(self):
        """懒加载 lineage_tracker 模块，返回模块对象或 None。"""
        if self._lineage_tracker is None:
            self._lineage_tracker = lazy_load("lineage_tracker")
        return self._lineage_tracker

    def _load_artifact_manager(self):
        """懒加载 artifact_manager 模块，返回模块对象或 None。"""
        if self._artifact_manager is None:
            self._artifact_manager = lazy_load("artifact_manager")
        return self._artifact_manager

    def _load_question_architect(self):
        """懒加载 question_architect 模块，返回模块对象或 None。"""
        if self._question_architect_module is None:
            self._question_architect_module = lazy_load("question_architect")
        return self._question_architect_module

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------

    def _load_state(self) -> Dict[str, Any]:
        """加载申请书状态（纯读，不加锁）。"""
        data = load_json(self.state_path, default=None)
        if not isinstance(data, dict) or "sections" not in data:
            return {
                "proposal_id": "prop_000",
                "sections": {},
                "created_at": now_utc(),
                "updated_at": now_utc(),
                "total_word_count": 0,
            }
        if not isinstance(data["sections"], dict):
            data["sections"] = {}
        return data

    def _save_state(self, data: Dict[str, Any]) -> None:
        """保存申请书状态（原子写入，应在锁内调用）。"""
        # 更新总字数
        total = 0
        for section in data.get("sections", {}).values():
            total += section.get("word_count", 0)
        data["total_word_count"] = total
        data["updated_at"] = now_utc()
        save_json(self.state_path, data)

    def _write_section_file(self, section: Dict[str, Any]) -> None:
        """将章节内容写入 markdown 文件。"""
        section_id = section.get("section_id", "sec_00")
        content = section.get("content", "")
        file_path = self.sections_dir / f"{section_id}.md"
        file_path.write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # 核心接口
    # ------------------------------------------------------------------

    def write_proposal(
        self,
        question_framework: Dict[str, Any],
        gap_report: Optional[Dict[str, Any]] = None,
        taste_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """撰写完整申请书（全部 6 章节）。

        Args:
            question_framework: 科学问题框架（question_architect.construct_questions 产物）
            gap_report: 可选缺口报告，用于文献综述与可行性分析
            taste_profile: 可选写作风格画像，用于调整写作风格

        Returns:
            撰写结果摘要 {"sections": {...}, "total_word_count": int, "section_count": int}
        """
        if not isinstance(question_framework, dict):
            raise ValueError("question_framework 必须为字典")

        placeholders = _extract_placeholders(question_framework)
        written_sections: Dict[str, Dict[str, Any]] = {}

        context: Dict[str, Any] = {
            "gap_report": gap_report,
            "taste_profile": taste_profile,
        }

        with file_lock(self._lock_name):
            state = self._load_state()
            # 首次撰写时初始化 proposal_id
            if state.get("proposal_id", "prop_000") == "prop_000":
                state["proposal_id"] = f"prop_{hashlib.md5(now_utc().encode()).hexdigest()[:8]}"

            for section_name in SECTION_ORDER:
                section = self._write_section_internal(
                    section_name, question_framework, context,
                    placeholders, state,
                )
                written_sections[section_name] = dict(section)

            self._save_state(state)

        self._state = state

        # 注册血缘与产物（失败不阻塞）
        self._register_lineage_batch(written_sections, question_framework)
        self._register_artifacts_batch(written_sections)

        total = sum(s.get("word_count", 0) for s in written_sections.values())
        return {
            "sections": {k: {"section_id": v["section_id"], "word_count": v["word_count"],
                              "version": v["version"], "status": v["status"]}
                          for k, v in written_sections.items()},
            "total_word_count": total,
            "section_count": len(written_sections),
        }

    def write_section(
        self,
        section_name: str,
        framework: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """撰写单个章节。

        Args:
            section_name: 章节名称（须在 SECTION_ORDER 中）
            framework: 科学问题框架
            context: 可选上下文，含 gap_report / taste_profile

        Returns:
            章节字典
        """
        if section_name not in SECTION_DEFINITIONS:
            raise ValueError(f"未知章节: {section_name}（支持: {list(SECTION_ORDER)}）")
        if not isinstance(framework, dict):
            raise ValueError("framework 必须为字典")

        if context is None:
            context = {}
        placeholders = _extract_placeholders(framework)

        with file_lock(self._lock_name):
            state = self._load_state()
            section = self._write_section_internal(
                section_name, framework, context, placeholders, state,
            )
            self._save_state(state)

        self._state = state

        # 注册血缘与产物
        self._register_lineage_single(section, framework)
        self._register_artifact_single(section)

        return dict(section)

    def _write_section_internal(
        self,
        section_name: str,
        framework: Dict[str, Any],
        context: Dict[str, Any],
        placeholders: Dict[str, str],
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """内部撰写逻辑（须在锁内调用）。

        组装章节内容 → 应用 taste 风格 → 统计指标 → 写入文件与状态。
        """
        section_def = SECTION_DEFINITIONS[section_name]
        section_id = section_def["section_id"]
        gap_report = context.get("gap_report")
        taste_profile = context.get("taste_profile")

        # 组装内容
        assembler = _SECTION_ASSEMBLERS.get(section_name)
        if assembler:
            content = assembler(framework, gap_report, placeholders)
        else:
            content = f"# {section_name}\n\n（待填充）\n"

        # 应用 taste 风格
        content = _apply_taste_style(content, section_name, taste_profile)

        # v6.3.2 LLM 增强：让章节内容具备学术深度与实质论述
        content, llm_meta = _llm_enhance_section(
            section_name, content, framework, placeholders, gap_report
        )

        # 提取关联问题 ID
        question_ids: List[str] = []
        for element in section_def.get("source_elements", []):
            for q in _extract_questions_by_element(framework, element):
                qid = q.get("question_id")
                if qid and qid not in question_ids:
                    question_ids.append(qid)

        # 统计
        word_count = _count_words(content)
        paragraph_count = _count_paragraphs(content)
        citations = self._scan_placeholders(content)

        # 版本号
        existing = state["sections"].get(section_name)
        if existing:
            version = existing.get("version", "v0.1")
        else:
            version = "v0.1"

        timestamp = now_utc()
        section: Dict[str, Any] = {
            "section_name": section_name,
            "section_id": section_id,
            "content": content,
            "word_count": word_count,
            "paragraph_count": paragraph_count,
            "citations": citations,
            "version": version,
            "status": "draft",
            "question_ids": question_ids,
            "llm_enhanced": llm_meta.get("enhanced", False),
            "llm_provider": llm_meta.get("provider", ""),
            "created_at": existing.get("created_at", timestamp) if existing else timestamp,
            "updated_at": timestamp,
            "update_history": existing.get("update_history", []) if existing else [],
        }

        # 写入 markdown 文件
        self._write_section_file(section)
        # 更新状态
        state["sections"][section_name] = section

        return section

    def _scan_placeholders(self, content: str) -> List[int]:
        """扫描内容中的引文占位符，返回占位符数量。

        注意：占位符 [CITE:ref_key] 在注入前尚未编号，
        此处返回占位符个数作为 citations 字段值（注入后由 inject_citations 更新为编号列表）。
        """
        matches = CITE_PLACEHOLDER_PATTERN.findall(content)
        return list(range(1, len(matches) + 1))

    # ------------------------------------------------------------------
    # 查询接口
    # ------------------------------------------------------------------

    def get_sections(self) -> Dict[str, Dict[str, Any]]:
        """获取所有已撰写章节。"""
        state = self._load_state()
        return {k: dict(v) for k, v in state.get("sections", {}).items()}

    def get_section(self, section_name: str) -> Optional[Dict[str, Any]]:
        """获取单个章节；不存在返回 None。"""
        state = self._load_state()
        section = state.get("sections", {}).get(section_name)
        return dict(section) if section else None

    # ------------------------------------------------------------------
    # 更新接口
    # ------------------------------------------------------------------

    def update_section(
        self,
        section_name: str,
        content: str,
        reason: str,
    ) -> Dict[str, Any]:
        """更新章节内容（创建新版本）。

        Args:
            section_name: 章节名称
            content: 新的章节内容
            reason: 更新原因（记入 update_history）

        Returns:
            更新后的章节字典

        Raises:
            KeyError: 章节不存在
        """
        if section_name not in SECTION_DEFINITIONS:
            raise ValueError(f"未知章节: {section_name}")

        with file_lock(self._lock_name):
            state = self._load_state()
            existing = state["sections"].get(section_name)
            if not existing:
                raise KeyError(f"章节不存在: {section_name}（请先 write_section 撰写）")

            # 版本递增
            old_version = existing.get("version", "v0.1")
            new_version = self._next_version(old_version)

            # 记录更新历史
            history = existing.get("update_history", [])
            history.append({
                "version": old_version,
                "reason": reason,
                "word_count": existing.get("word_count", 0),
                "updated_at": now_utc(),
            })

            # 统计新内容
            word_count = _count_words(content)
            paragraph_count = _count_paragraphs(content)
            citations = self._scan_placeholders(content)

            updated: Dict[str, Any] = {
                "section_name": section_name,
                "section_id": existing.get("section_id", SECTION_DEFINITIONS[section_name]["section_id"]),
                "content": content,
                "word_count": word_count,
                "paragraph_count": paragraph_count,
                "citations": citations,
                "version": new_version,
                "status": existing.get("status", "draft"),
                "question_ids": existing.get("question_ids", []),
                "created_at": existing.get("created_at", now_utc()),
                "updated_at": now_utc(),
                "update_history": history,
            }

            self._write_section_file(updated)
            state["sections"][section_name] = updated
            self._save_state(state)

        self._state = state
        return dict(updated)

    def _next_version(self, current: str) -> str:
        """版本号递增：v0.1 → v0.2 → v0.3 ..."""
        match = re.match(r'^v(\d+)\.(\d+)$', current)
        if not match:
            return "v0.1"
        major = int(match.group(1))
        minor = int(match.group(2))
        return f"v{major}.{minor + 1}"

    # ------------------------------------------------------------------
    # 合并与导出
    # ------------------------------------------------------------------

    def merge_sections(self) -> str:
        """合并所有章节为完整的申请书文档（markdown）。"""
        state = self._load_state()
        parts: List[str] = []
        for section_name in SECTION_ORDER:
            section = state.get("sections", {}).get(section_name)
            if section:
                parts.append(section.get("content", ""))
        return "\n\n---\n\n".join(parts)

    def export_proposal(self, format: str = "markdown") -> str:
        """导出完整申请书。

        Args:
            format: 导出格式，目前支持 "markdown"

        Returns:
            格式化后的申请书字符串
        """
        if format == "markdown":
            return self.merge_sections()
        raise ValueError(f"不支持的格式: {format}（目前支持 markdown）")

    # ------------------------------------------------------------------
    # 进度
    # ------------------------------------------------------------------

    def get_writing_progress(self) -> Dict[str, Any]:
        """获取撰写进度摘要。"""
        state = self._load_state()
        sections = state.get("sections", {})
        total_sections = len(SECTION_ORDER)
        written_sections = len(sections)
        total_word_count = sum(s.get("word_count", 0) for s in sections.values())

        section_status: Dict[str, str] = {}
        for name in SECTION_ORDER:
            if name in sections:
                section_status[name] = sections[name].get("status", "draft")
            else:
                section_status[name] = "未撰写"

        return {
            "total_sections": total_sections,
            "written_sections": written_sections,
            "completion_rate": round(written_sections / total_sections, 2) if total_sections else 0.0,
            "total_word_count": total_word_count,
            "section_status": section_status,
            "section_word_counts": {
                name: sections[name].get("word_count", 0)
                for name in SECTION_ORDER if name in sections
            },
        }

    # ------------------------------------------------------------------
    # 引文注入
    # ------------------------------------------------------------------

    def inject_citations(
        self,
        sections: Dict[str, Any],
        citation_manager: Any,
    ) -> Dict[str, Any]:
        """将所有章节中的引文占位符替换为编号引文。

        将 [CITE:ref_key] 转换为 {{cite:ref_key}} 后调用
        citation_manager.inject_citations 完成注入。
        同时更新各章节的 citations 字段为实际引文编号列表。

        Args:
            sections: 章节字典（section_name → section dict 或 content 字符串）
            citation_manager: CitationManager 实例

        Returns:
            更新后的章节字典
        """
        for section_name, section in sections.items():
            if isinstance(section, dict):
                content = section.get("content", "")
            else:
                content = str(section)

            # 转换 [CITE:ref_key] → {{cite:ref_key}}
            converted = CITE_PLACEHOLDER_PATTERN.sub(
                lambda m: f"{{{{cite:{m.group(1)}}}}}", content
            )

            # 调用 citation_manager 注入
            if hasattr(citation_manager, "inject_citations"):
                injected = citation_manager.inject_citations(converted)
            else:
                injected = converted

            # 扫描实际引文编号
            cited_numbers: List[int] = []
            if hasattr(citation_manager, "scan_text_citations"):
                cited_numbers = citation_manager.scan_text_citations(injected)

            if isinstance(section, dict):
                section["content"] = injected
                section["citations"] = cited_numbers
            else:
                sections[section_name] = injected

        return sections

    # ------------------------------------------------------------------
    # 血缘与产物注册
    # ------------------------------------------------------------------

    def _register_lineage_batch(
        self,
        sections: Dict[str, Dict[str, Any]],
        framework: Dict[str, Any],
    ) -> None:
        """批量注册章节 → 问题的血缘关系（失败不阻塞）。"""
        for section in sections.values():
            self._register_lineage_single(section, framework)

    def _register_lineage_single(
        self,
        section: Dict[str, Any],
        framework: Dict[str, Any],
    ) -> None:
        """注册单个章节的血缘关系（失败不阻塞）。"""
        lt_module = self._load_lineage_tracker()
        if lt_module is None or not hasattr(lt_module, "LineageTracker"):
            return
        try:
            tracker = lt_module.LineageTracker(self.proposal_dir)
            section_id = section.get("section_id", "")
            section_name = section.get("section_name", "")
            # 注册章节节点
            tracker.register_node(section_id, "proposal_section", section_name, stage=4)
            # 注册章节 → 问题的 derived_from 边
            for qid in section.get("question_ids", []):
                tracker.register_node(qid, "scientific_question", qid, stage=3)
                tracker.add_edge(section_id, qid, "derived_from", "章节基于科学问题构建")
        except Exception:
            pass

    def _register_artifacts_batch(
        self,
        sections: Dict[str, Dict[str, Any]],
    ) -> None:
        """批量注册章节产物（失败不阻塞）。"""
        for section in sections.values():
            self._register_artifact_single(section)

    def _register_artifact_single(self, section: Dict[str, Any]) -> None:
        """注册单个章节为产物（失败不阻塞）。"""
        am_module = self._load_artifact_manager()
        if am_module is None or not hasattr(am_module, "ArtifactManager"):
            return
        try:
            mgr = am_module.ArtifactManager(self.proposal_dir)
            section_id = section.get("section_id", "")
            version = section.get("version", "v0.1")
            artifact_id = f"{section_id}_{version}"
            file_path = f"04_proposal/sections/{section_id}.md"
            content = section.get("content", "")
            # 若产物已存在则跳过
            if mgr.get_artifact(artifact_id) is None:
                mgr.create_artifact(
                    artifact_id=artifact_id,
                    artifact_type="proposal_section",
                    stage=4,
                    content=content,
                    file_path=file_path,
                    author="proposal_writer",
                    version=version,
                )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _make_mock_framework() -> Dict[str, Any]:
    """构造模拟问题框架用于自检。"""
    return {
        "framework_id": "fw_001",
        "topic_id": "topic_001",
        "topic_title": "量子度规对固体HHG光谱的调制机制研究",
        "elements": {
            "立项依据": ["q_001", "q_002", "q_003"],
            "科学问题": ["q_004", "q_005", "q_006"],
            "研究内容": ["q_007", "q_008", "q_009"],
            "研究方案": ["q_010", "q_011", "q_012"],
            "特色与创新": ["q_013", "q_014", "q_015"],
        },
        "main_questions": ["q_001", "q_004", "q_007", "q_010", "q_013"],
        "all_questions": {
            "q_001": {
                "question_id": "q_001", "level": 0, "parent_id": None,
                "text": "量子度规为何成为固体HHG领域亟待解决的关键问题？",
                "type": "theoretical", "element": "立项依据",
                "hypothesis": "量子度规的研究将揭示固体HHG的新机制",
                "evidence": {"gaps": ["gap_001"], "literature": ["ref_001", "ref_002"], "methods": ["TDDFT"]},
            },
            "q_002": {
                "question_id": "q_002", "level": 1, "parent_id": "q_001",
                "text": "量子度规能否定量解释固体HHG的偏振特性？",
                "type": "theoretical", "element": "立项依据",
                "hypothesis": "量子度规可定量解释偏振特性",
                "evidence": {"gaps": [], "literature": ["ref_003"], "methods": []},
            },
            "q_003": {
                "question_id": "q_003", "level": 2, "parent_id": "q_002",
                "text": "量子度规的预测在何种参数区间失效？",
                "type": "theoretical", "element": "立项依据",
                "hypothesis": "在高频区域量子度规预测失效",
                "evidence": {"gaps": [], "literature": [], "methods": []},
            },
            "q_004": {
                "question_id": "q_004", "level": 0, "parent_id": None,
                "text": "量子度规如何调制固体HHG的偏振特性？",
                "type": "mechanism", "element": "科学问题",
                "hypothesis": "量子度规主导偏振特性变化",
                "evidence": {"gaps": ["gap_002"], "literature": ["ref_004"], "methods": ["TDDFT", "SBE"]},
            },
            "q_005": {
                "question_id": "q_005", "level": 1, "parent_id": "q_004",
                "text": "量子度规影响固体HHG的关键路径是什么？",
                "type": "mechanism", "element": "科学问题",
                "hypothesis": "通过带间跃迁路径调制",
                "evidence": {"gaps": [], "literature": [], "methods": []},
            },
            "q_006": {
                "question_id": "q_006", "level": 1, "parent_id": "q_004",
                "text": "量子度规的偏振特性在不同晶体取向下的变化？",
                "type": "mechanism", "element": "科学问题",
                "hypothesis": "随晶体取向系统变化",
                "evidence": {"gaps": [], "literature": [], "methods": []},
            },
            "q_007": {
                "question_id": "q_007", "level": 0, "parent_id": None,
                "text": "不同晶体取向下固体HHG表现为何种偏振特征？",
                "type": "empirical", "element": "研究内容",
                "hypothesis": "呈现可表征的偏振特征",
                "evidence": {"gaps": [], "literature": ["ref_005"], "methods": ["泵浦-探测"]},
            },
            "q_008": {
                "question_id": "q_008", "level": 1, "parent_id": "q_007",
                "text": "不同晶体取向下偏振特性的关键参数取值范围是什么？",
                "type": "empirical", "element": "研究内容",
                "hypothesis": "参数在特定范围内系统变化",
                "evidence": {"gaps": [], "literature": [], "methods": []},
            },
            "q_009": {
                "question_id": "q_009", "level": 1, "parent_id": "q_007",
                "text": "偏振特性在不同晶体取向间有何系统差异？",
                "type": "empirical", "element": "研究内容",
                "hypothesis": "存在显著系统差异",
                "evidence": {"gaps": [], "literature": [], "methods": []},
            },
            "q_010": {
                "question_id": "q_010", "level": 0, "parent_id": None,
                "text": "如何利用TDDFT测量/计算量子度规对HHG的影响？",
                "type": "methodology", "element": "研究方案",
                "hypothesis": "TDDFT可定量刻画量子度规的影响",
                "evidence": {"gaps": ["gap_003"], "literature": ["ref_006"], "methods": ["TDDFT", "SBE"]},
            },
            "q_011": {
                "question_id": "q_011", "level": 1, "parent_id": "q_010",
                "text": "TDDFT测量/计算量子度规的精度与适用范围如何？",
                "type": "methodology", "element": "研究方案",
                "hypothesis": "在特定参数范围内精度满足要求",
                "evidence": {"gaps": [], "literature": [], "methods": []},
            },
            "q_012": {
                "question_id": "q_012", "level": 1, "parent_id": "q_010",
                "text": "TDDFT在不同条件下的鲁棒性如何？",
                "type": "methodology", "element": "研究方案",
                "hypothesis": "具有良好鲁棒性",
                "evidence": {"gaps": [], "literature": [], "methods": []},
            },
            "q_013": {
                "question_id": "q_013", "level": 0, "parent_id": None,
                "text": "本研究相比现有工作在偏振特性分析上有何独特贡献？",
                "type": "comparative", "element": "特色与创新",
                "hypothesis": "本研究在偏振特性上相比现有工作有显著突破",
                "evidence": {"gaps": ["gap_004"], "literature": ["ref_007"], "methods": []},
            },
            "q_014": {
                "question_id": "q_014", "level": 1, "parent_id": "q_013",
                "text": "本研究与现有方法在偏振特性分析上的定量差异是多少？",
                "type": "comparative", "element": "特色与创新",
                "hypothesis": "存在显著定量差异",
                "evidence": {"gaps": [], "literature": [], "methods": []},
            },
            "q_015": {
                "question_id": "q_015", "level": 1, "parent_id": "q_013",
                "text": "造成差异的物理根源是什么？",
                "type": "comparative", "element": "特色与创新",
                "hypothesis": "源于量子度规的不同处理方式",
                "evidence": {"gaps": [], "literature": [], "methods": []},
            },
        },
        "validation_summary": {"total_questions": 15},
        "_placeholders": {
            "concept": "量子度规",
            "phenomenon": "固体HHG",
            "aspect": "偏振特性",
            "method": "TDDFT",
            "quantity": "偏振参数",
            "condition": "不同晶体取向",
            "field": "强场超快光学",
            "theory": "量子度规理论",
            "observation": "HHG光谱偏振",
            "alternative": "经典模型",
            "system_A": "量子度规框架",
            "system_B": "经典模型",
        },
    }


def _make_mock_gap_report() -> Dict[str, Any]:
    """构造模拟缺口报告用于自检。"""
    return {
        "gaps": [
            {"gap_id": "gap_001", "type": "conceptual", "description": "量子度规对HHG偏振的物理机制尚不清楚", "novelty_score": 0.9},
            {"gap_id": "gap_002", "type": "conceptual", "description": "缺乏量子度规与偏振特性的定量关系", "novelty_score": 0.85},
            {"gap_id": "gap_003", "type": "methodological", "description": "现有计算方法难以精确处理量子度规效应", "novelty_score": 0.8},
            {"gap_id": "gap_004", "type": "empirical", "description": "缺乏系统性的偏振特性实验数据", "novelty_score": 0.7},
        ],
        "methods": ["改进TDDFT", "机器学习辅助分析"],
        "coverage": 0.6,
    }


def _make_mock_taste_profile() -> Dict[str, Any]:
    """构造模拟 taste_profile 用于自检。"""
    return {
        "theoretical_depth": 0.85,
        "novelty": 0.80,
        "interdisciplinarity": 0.70,
        "rigor": 0.90,
    }


def _make_mock_citation_manager(proposal_dir: Path):
    """构造模拟 CitationManager 用于引文注入测试。

    使用真实的 CitationManager 实例并预填几条参考文献。
    """
    cm_module = lazy_load("citation_manager")
    if cm_module is None or not hasattr(cm_module, "CitationManager"):
        return None
    mgr = cm_module.CitationManager(proposal_dir)
    # 预填参考文献
    refs = [
        {"type": "journal", "title": "Quantum Metric in Solids", "authors": ["Zhang, Y."], "year": 2024, "venue": "Nature Physics"},
        {"type": "journal", "title": "HHG from Topological Insulators", "authors": ["Wang, Z."], "year": 2025, "venue": "PRL"},
        {"type": "preprint", "title": "Polarization in Solid HHG", "authors": ["Li, X."], "year": 2025, "arxiv_id": "2501.67890"},
        {"type": "journal", "title": "TDDFT for HHG", "authors": ["Chen, L."], "year": 2023, "venue": "PRB"},
    ]
    for r in refs:
        mgr.add_reference(r)
    return mgr


def _self_check() -> None:
    """自检：在临时目录中隔离测试全部核心场景。

    检查点（14 项）：
        1.  ProposalWriter 初始化
        2.  完整申请书撰写（全部 6 章节）
        3.  单章节撰写
        4.  章节查询（get_sections / get_section）
        5.  章节更新（版本递增、历史记录）
        6.  章节合并（完整文档）
        7.  Markdown 导出
        8.  撰写进度计算
        9.  引文占位符注入
        10. taste_profile 风格调整
        11. 空框架处理
        12. 原子写入 + 文件锁
        13. 章节内容结构验证
        14. 辅助函数单元测试
    """
    import shutil
    import tempfile

    print("=" * 50)
    print("◐ proposal_writer 自检")
    print("=" * 50)

    tmp = Path(tempfile.mkdtemp(prefix="proposal_writer_test_"))
    try:
        proposal_dir = tmp / "T1_proposal"
        framework = _make_mock_framework()
        gap_report = _make_mock_gap_report()
        taste_profile = _make_mock_taste_profile()

        # [1/14] ProposalWriter 初始化
        print("\n[1/14] ProposalWriter 初始化...")
        writer = ProposalWriter(proposal_dir)
        assert writer.proposal_dir == proposal_dir
        assert writer.proposal_content_dir.exists(), "04_proposal 目录应已创建"
        assert writer.sections_dir.exists(), "sections 目录应已创建"
        assert "proposal-" in writer._lock_name, "锁名应含 proposal- 前缀"
        # 空状态查询
        assert writer.get_sections() == {}, "初始化后应无章节"
        assert writer.get_section("立项依据") is None, "初始化后查询单章节应为 None"
        progress = writer.get_writing_progress()
        assert progress["written_sections"] == 0
        assert progress["total_sections"] == 6
        print(f"  目录: {writer.proposal_content_dir}")
        print(f"  锁名: {writer._lock_name}")
        print(f"  初始进度: {progress['written_sections']}/{progress['total_sections']}")
        print("  ✓ 初始化成功，目录与锁就绪")

        # [2/14] 完整申请书撰写（全部 6 章节）
        print("\n[2/14] 完整申请书撰写（全部 6 章节）...")
        result = writer.write_proposal(framework, gap_report=gap_report, taste_profile=taste_profile)
        assert result["section_count"] == 6, f"应撰写 6 章节，实际 {result['section_count']}"
        assert result["total_word_count"] > 0, "总字数应大于 0"
        sections = writer.get_sections()
        assert len(sections) == 6, f"应有 6 个章节，实际 {len(sections)}"
        for name in SECTION_ORDER:
            assert name in sections, f"缺少章节: {name}"
            sec = sections[name]
            assert sec["content"], f"章节 {name} 内容不应为空"
            assert sec["word_count"] > 0, f"章节 {name} 字数应大于 0"
            assert sec["paragraph_count"] > 0, f"章节 {name} 段落数应大于 0"
            assert sec["status"] == "draft", f"章节 {name} 状态应为 draft"
            assert sec["version"] == "v0.1", f"章节 {name} 版本应为 v0.1"
            assert sec["section_id"].startswith("sec_"), f"章节 {name} section_id 格式错误"
        print(f"  章节数: {result['section_count']}")
        print(f"  总字数: {result['total_word_count']}")
        for name in SECTION_ORDER:
            sec = sections[name]
            print(f"  {sec['section_id']} {name}: {sec['word_count']}字, {sec['paragraph_count']}段, v={sec['version']}")
        print("  ✓ 全部 6 章节撰写成功")

        # [3/14] 单章节撰写
        print("\n[3/14] 单章节撰写...")
        proposal_dir2 = tmp / "T2_proposal"
        writer2 = ProposalWriter(proposal_dir2)
        context = {"gap_report": gap_report, "taste_profile": taste_profile}
        sec = writer2.write_section("立项依据", framework, context)
        assert sec["section_name"] == "立项依据"
        assert sec["section_id"] == "sec_01"
        assert sec["content"], "内容不应为空"
        assert sec["word_count"] > 0
        assert "# 立项依据" in sec["content"], "内容应含标题"
        assert "## 研究背景" in sec["content"], "内容应含研究背景子标题"
        assert "## 国内外研究现状" in sec["content"], "内容应含文献综述子标题"
        assert sec["question_ids"], "应有关联问题ID"
        assert "q_001" in sec["question_ids"], "应关联 q_001"
        # 验证文件已写入
        md_file = proposal_dir2 / "04_proposal" / "sections" / "sec_01.md"
        assert md_file.exists(), "markdown 文件应已写入"
        assert md_file.read_text(encoding="utf-8") == sec["content"], "文件内容应与状态一致"
        print(f"  章节: {sec['section_name']} ({sec['section_id']})")
        print(f"  字数: {sec['word_count']}, 段落: {sec['paragraph_count']}")
        print(f"  关联问题: {sec['question_ids']}")
        print(f"  文件: {md_file.name}")
        print("  ✓ 单章节撰写成功，内容结构正确")

        # [4/14] 章节查询（get_sections / get_section）
        print("\n[4/14] 章节查询（get_sections / get_section）...")
        all_secs = writer.get_sections()
        assert len(all_secs) == 6, f"应返回 6 章节，实际 {len(all_secs)}"
        single = writer.get_section("研究方案")
        assert single is not None, "查询研究方案应返回结果"
        assert single["section_name"] == "研究方案"
        assert single["section_id"] == "sec_03"
        assert "## 研究方法" in single["content"]
        assert "## 技术路线" in single["content"]
        assert "## 可行性分析" in single["content"]
        # 查询不存在的章节
        none_result = writer.get_section("不存在的章节")
        assert none_result is None, "查询不存在章节应返回 None"
        # 验证返回的是副本（修改不影响内部状态）
        single["content"] = "modified"
        single2 = writer.get_section("研究方案")
        assert single2["content"] != "modified", "返回应为副本"
        print(f"  get_sections: {len(all_secs)} 章节")
        print(f"  get_section('研究方案'): {single['section_id']}, {single['word_count']}字")
        print(f"  get_section('不存在'): None")
        print("  ✓ 章节查询正确，返回副本")

        # [5/14] 章节更新（版本递增、历史记录）
        print("\n[5/14] 章节更新（版本递增、历史记录）...")
        original = writer.get_section("特色与创新")
        assert original["version"] == "v0.1"
        new_content = "# 特色与创新\n\n## 创新点\n\n1. 首次提出量子度规调制HHG偏振的新机制。\n2. 发展了基于TDDFT的新方法。\n\n## 与现有工作的比较\n\n- 相比现有工作，本研究在偏振分析上更系统。\n"
        updated = writer.update_section("特色与创新", new_content, "补充创新点细节")
        assert updated["version"] == "v0.2", f"版本应递增为 v0.2，实际 {updated['version']}"
        assert updated["content"] == new_content, "内容应已更新"
        assert updated["word_count"] > 0
        assert len(updated["update_history"]) == 1, "应有一条更新历史"
        assert updated["update_history"][0]["version"] == "v0.1", "历史应记录旧版本"
        assert updated["update_history"][0]["reason"] == "补充创新点细节"
        # 再次更新
        updated2 = writer.update_section("特色与创新", new_content + "\n额外段落。\n", "二次修订")
        assert updated2["version"] == "v0.3", f"版本应递增为 v0.3，实际 {updated2['version']}"
        assert len(updated2["update_history"]) == 2, "应有两条更新历史"
        # 验证文件已更新
        md_file = proposal_dir / "04_proposal" / "sections" / "sec_04.md"
        assert md_file.read_text(encoding="utf-8") == updated2["content"], "文件应已更新"
        print(f"  原版本: {original['version']} → 新版本: {updated2['version']}")
        print(f"  更新历史: {len(updated2['update_history'])} 条")
        for h in updated2["update_history"]:
            print(f"    {h['version']}: {h['reason']}")
        # 更新未撰写的章节应报错（使用有效章节名但尚未撰写）
        try:
            writer2.update_section("研究内容", "x", "y")
            raise AssertionError("应抛出 KeyError")
        except KeyError:
            pass
        # 更新无效章节名应报错
        try:
            writer.update_section("不存在的章节", "x", "y")
            raise AssertionError("应抛出 ValueError")
        except ValueError:
            pass
        print("  ✓ 版本递增 + 历史记录 + 错误处理正确")

        # [6/14] 章节合并（完整文档）
        print("\n[6/14] 章节合并（完整文档）...")
        merged = writer.merge_sections()
        assert merged, "合并内容不应为空"
        assert "# 立项依据" in merged, "应含立项依据"
        assert "# 研究内容" in merged, "应含研究内容"
        assert "# 研究方案" in merged, "应含研究方案"
        assert "# 特色与创新" in merged, "应含特色与创新"
        assert "# 年度研究计划" in merged, "应含年度研究计划"
        assert "# 预期研究成果" in merged, "应含预期研究成果"
        # 验证章节顺序（立项依据在研究内容之前）
        idx_1 = merged.index("# 立项依据")
        idx_2 = merged.index("# 研究内容")
        assert idx_1 < idx_2, "立项依据应在研究内容之前"
        idx_5 = merged.index("# 年度研究计划")
        idx_6 = merged.index("# 预期研究成果")
        assert idx_5 < idx_6, "年度研究计划应在预期研究成果之前"
        # 验证分隔符
        assert "---" in merged, "章节间应有分隔符"
        merged_words = _count_words(merged)
        print(f"  合并字数: {merged_words}")
        print(f"  含全部 6 章节标题: ✓")
        print(f"  章节顺序正确: ✓")
        print("  ✓ 章节合并为完整文档")

        # [7/14] Markdown 导出
        print("\n[7/14] Markdown 导出...")
        exported = writer.export_proposal("markdown")
        assert exported == merged, "markdown 导出应与 merge_sections 一致"
        assert exported.startswith("# 立项依据"), "应以立项依据开头"
        assert "# 预期研究成果" in exported[-500:], "末尾应含预期研究成果章节"
        # 不支持的格式
        try:
            writer.export_proposal("pdf")
            raise AssertionError("应抛出 ValueError")
        except ValueError as e:
            assert "pdf" in str(e)
        print(f"  markdown 导出: {len(exported)} 字符")
        print(f"  不支持格式 'pdf' → ValueError: ✓")
        print("  ✓ Markdown 导出正确")

        # [8/14] 撰写进度计算
        print("\n[8/14] 撰写进度计算...")
        progress = writer.get_writing_progress()
        assert progress["total_sections"] == 6
        assert progress["written_sections"] == 6
        assert progress["completion_rate"] == 1.0, f"完成率应为 1.0，实际 {progress['completion_rate']}"
        assert progress["total_word_count"] > 0
        assert len(progress["section_status"]) == 6
        assert len(progress["section_word_counts"]) == 6
        for name in SECTION_ORDER:
            assert name in progress["section_status"]
            assert progress["section_status"][name] == "draft"
        # 部分撰写进度
        writer_partial = ProposalWriter(tmp / "T3_proposal")
        prog0 = writer_partial.get_writing_progress()
        assert prog0["written_sections"] == 0
        assert prog0["completion_rate"] == 0.0
        writer_partial.write_section("研究方案", framework)
        prog1 = writer_partial.get_writing_progress()
        assert prog1["written_sections"] == 1
        assert prog1["completion_rate"] == round(1 / 6, 2)
        print(f"  全部撰写: {progress['written_sections']}/{progress['total_sections']} ({progress['completion_rate']})")
        print(f"  部分撰写: {prog1['written_sections']}/{prog1['total_sections']} ({prog1['completion_rate']})")
        print(f"  总字数: {progress['total_word_count']}")
        print("  ✓ 进度计算正确（全部/部分/空）")

        # [9/14] 引文占位符注入
        print("\n[9/14] 引文占位符注入...")
        cm = _make_mock_citation_manager(proposal_dir)
        assert cm is not None, "CitationManager 应可用"
        # 获取含占位符的章节
        rationale = writer.get_section("立项依据")
        original_content = rationale["content"]
        assert "[CITE:" in original_content, "立项依据应含引文占位符 [CITE:...]"
        # 注入引文
        sections_to_inject = {"立项依据": rationale}
        injected = writer.inject_citations(sections_to_inject, cm)
        injected_content = injected["立项依据"]["content"]
        # 占位符应被替换为 [N] 或 [?]
        assert "[CITE:" not in injected_content, "注入后不应再有占位符"
        # 应有编号引文 [1] [2] 等
        has_numbered = bool(re.search(r'\[\d+\]', injected_content))
        assert has_numbered, "注入后应有编号引文 [N]"
        # citations 字段应更新为编号列表
        cited_nums = injected["立项依据"]["citations"]
        assert isinstance(cited_nums, list), "citations 应为列表"
        print(f"  原始占位符数: {len(CITE_PLACEHOLDER_PATTERN.findall(original_content))}")
        print(f"  注入后引文编号: {cited_nums}")
        print(f"  占位符替换为编号: ✓")
        print("  ✓ 引文占位符注入成功")

        # [10/14] taste_profile 风格调整
        print("\n[10/14] taste_profile 风格调整...")
        # 高 theoretical_depth 应添加理论引导语
        high_td_profile = {"theoretical_depth": 0.9, "novelty": 0.5, "interdisciplinarity": 0.3, "rigor": 0.5}
        writer_td = ProposalWriter(tmp / "T4_proposal")
        td_result = writer_td.write_proposal(framework, taste_profile=high_td_profile)
        td_sec = writer_td.get_section("立项依据")
        assert "从理论框架出发" in td_sec["content"], "高 theoretical_depth 应添加理论引导语"
        # 低 theoretical_depth
        low_td_profile = {"theoretical_depth": 0.2, "novelty": 0.5, "interdisciplinarity": 0.3, "rigor": 0.5}
        writer_td2 = ProposalWriter(tmp / "T5_proposal")
        writer_td2.write_proposal(framework, taste_profile=low_td_profile)
        td2_sec = writer_td2.get_section("立项依据")
        assert "从实验现象出发" in td2_sec["content"], "低 theoretical_depth 应添加实验引导语"
        # 高 novelty 应在创新部分添加强调语
        high_nov_profile = {"theoretical_depth": 0.5, "novelty": 0.9, "interdisciplinarity": 0.3, "rigor": 0.5}
        writer_nov = ProposalWriter(tmp / "T6_proposal")
        writer_nov.write_proposal(framework, taste_profile=high_nov_profile)
        nov_sec = writer_nov.get_section("特色与创新")
        assert "创新性贡献" in nov_sec["content"], "高 novelty 应添加创新强调语"
        # 高 interdisciplinarity 应添加跨学科背景
        high_inter_profile = {"theoretical_depth": 0.5, "novelty": 0.5, "interdisciplinarity": 0.9, "rigor": 0.5}
        writer_inter = ProposalWriter(tmp / "T7_proposal")
        writer_inter.write_proposal(framework, taste_profile=high_inter_profile)
        inter_sec = writer_inter.get_section("立项依据")
        assert "多学科" in inter_sec["content"] or "交叉" in inter_sec["content"], "高 interdisciplinarity 应添加跨学科说明"
        # 无 taste_profile 不应有调整
        writer_none = ProposalWriter(tmp / "T8_proposal")
        writer_none.write_proposal(framework, taste_profile=None)
        none_sec = writer_none.get_section("立项依据")
        assert "从理论框架出发" not in none_sec["content"], "无 taste_profile 不应添加引导语"
        print(f"  高 theoretical_depth → '从理论框架出发': ✓")
        print(f"  低 theoretical_depth → '从实验现象出发': ✓")
        print(f"  高 novelty → '创新性贡献': ✓")
        print(f"  高 interdisciplinarity → '多学科交叉': ✓")
        print(f"  无 taste_profile → 无调整: ✓")
        print("  ✓ taste_profile 风格调整正确")

        # [11/14] 空框架处理
        print("\n[11/14] 空框架处理...")
        empty_framework: Dict[str, Any] = {
            "framework_id": "fw_empty",
            "topic_id": "topic_empty",
            "topic_title": "",
            "elements": {e: [] for e in ("立项依据", "科学问题", "研究内容", "研究方案", "特色与创新")},
            "main_questions": [],
            "all_questions": {},
            "_placeholders": {},
        }
        writer_empty = ProposalWriter(tmp / "T9_proposal")
        empty_result = writer_empty.write_proposal(empty_framework)
        assert empty_result["section_count"] == 6, "空框架仍应生成 6 章节"
        empty_secs = writer_empty.get_sections()
        for name in SECTION_ORDER:
            sec = empty_secs[name]
            assert sec["content"], f"空框架章节 {name} 内容不应为空（应使用兜底内容）"
            assert sec["word_count"] > 0, f"空框架章节 {name} 字数应大于 0"
            assert "# " in sec["content"], f"空框架章节 {name} 应有标题"
        # 空框架的占位符应使用默认值
        empty_rationale = empty_secs["立项依据"]["content"]
        assert "核心概念" in empty_rationale or "强场超快光学" in empty_rationale, "空框架应使用默认占位符"
        print(f"  空框架章节数: {empty_result['section_count']}")
        print(f"  各章节均有兜底内容: ✓")
        print(f"  默认占位符: '核心概念' / '强场超快光学' ✓")
        print("  ✓ 空框架处理安全（兜底内容 + 默认占位符）")

        # [12/14] 原子写入 + 文件锁
        print("\n[12/14] 原子写入 + 文件锁...")
        # 状态文件存在且格式正确
        assert writer.state_path.exists(), "状态文件应存在"
        raw = load_json(writer.state_path, {})
        assert "sections" in raw, "状态文件应含 sections"
        assert "total_word_count" in raw, "状态文件应含 total_word_count"
        assert "updated_at" in raw, "状态文件应含 updated_at"
        assert raw["total_word_count"] > 0
        # JSON 格式（ensure_ascii=False, indent=2）
        raw_text = writer.state_path.read_text(encoding="utf-8")
        assert '  "sections"' in raw_text, "应为缩进格式"
        # 中文不被转义
        assert "立项依据" in raw_text, "中文不应被转义"
        # markdown 文件存在
        for name in SECTION_ORDER:
            sec_def = SECTION_DEFINITIONS[name]
            md_path = writer.sections_dir / f"{sec_def['section_id']}.md"
            assert md_path.exists(), f"章节 {name} 的 markdown 文件应存在"
        # 重新加载确保数据一致
        writer_reload = ProposalWriter(proposal_dir)
        reloaded = writer_reload.get_sections()
        assert len(reloaded) == 6, "重新加载后章节数应一致"
        for name in SECTION_ORDER:
            assert reloaded[name]["content"] == sections[name]["content"] or name == "特色与创新"
        # 锁名唯一性
        writer_other = ProposalWriter(tmp / "T_other")
        assert writer._lock_name != writer_other._lock_name, "不同 proposal 锁名应不同"
        print(f"  状态文件: {raw['total_word_count']} 字, {len(raw['sections'])} 章节")
        print(f"  JSON 格式: indent=2, 中文不转义: ✓")
        print(f"  markdown 文件: 6 个全部存在")
        print(f"  重新加载: 数据一致")
        print(f"  锁名唯一: {writer._lock_name[:25]}... ≠ {writer_other._lock_name[:25]}...")
        print("  ✓ 原子写入 + 文件锁 + 数据一致性验证通过")

        # [13/14] 章节内容结构验证
        print("\n[13/14] 章节内容结构验证...")
        secs = writer.get_sections()
        # 立项依据
        r = secs["立项依据"]["content"]
        assert "## 研究背景" in r
        assert "## 国内外研究现状" in r
        assert "## 科学意义" in r
        assert "## 拟解决的关键科学问题" in r
        assert "量子度规" in r, "应含课题关键词"
        # 研究内容
        c = secs["研究内容"]["content"]
        assert "## 研究目标" in c
        assert "## 关键科学问题" in c
        assert "## 研究内容" in c
        # 研究方案
        p = secs["研究方案"]["content"]
        assert "## 研究方法" in p
        assert "## 技术路线" in p
        assert "## 可行性分析" in p
        assert "TDDFT" in p, "应含方法关键词"
        # 特色与创新
        i = secs["特色与创新"]["content"]  # 注意：此章节在 [5/14] 中被更新
        assert "## 创新点" in i
        assert "## 与现有工作的比较" in i
        # 年度研究计划
        y = secs["年度研究计划"]["content"]
        assert "## 第一年" in y
        assert "## 第二年" in y
        assert "## 第三年" in y
        # 预期研究成果
        e = secs["预期研究成果"]["content"]
        assert "## 论文发表" in e
        assert "## 方法与技术" in e
        assert "## 数据集" in e
        print(f"  立项依据: 4 个子标题 ✓")
        print(f"  研究内容: 3 个子标题 ✓")
        print(f"  研究方案: 3 个子标题 + 方法关键词 ✓")
        print(f"  特色与创新: 2 个子标题 ✓")
        print(f"  年度研究计划: 3 年计划 ✓")
        print(f"  预期研究成果: 3 类成果 ✓")
        print("  ✓ 全部章节内容结构符合 NSFC 格式")

        # [14/14] 辅助函数单元测试
        print("\n[14/14] 辅助函数单元测试...")
        # _count_words
        assert _count_words("") == 0
        assert _count_words("量子度规") == 4
        assert _count_words("hello world") == 2
        assert _count_words("量子度规对HHG的影响") == 9, f"实际 {_count_words('量子度规对HHG的影响')}"
        # _count_paragraphs
        assert _count_paragraphs("") == 0
        assert _count_paragraphs("一段") == 1
        assert _count_paragraphs("第一段\n\n第二段") == 2
        assert _count_paragraphs("第一段\n\n\n第二段") == 2
        # _classify_taste
        assert _classify_taste(0.8, {"high": 0.7, "medium": 0.4}) == "high"
        assert _classify_taste(0.5, {"high": 0.7, "medium": 0.4}) == "medium"
        assert _classify_taste(0.2, {"high": 0.7, "medium": 0.4}) == "low"
        # _question_to_statement
        q = {"hypothesis": "量子度规主导偏振变化", "text": "如何调制？"}
        assert _question_to_statement(q) == "量子度规主导偏振变化。"
        q2 = {"hypothesis": "", "text": "如何调制？"}
        assert _question_to_statement(q2) == "如何调制。"
        q3 = {"hypothesis": "", "text": ""}
        assert _question_to_statement(q3) == "本研究将探讨相关问题。"
        # _format_cite_placeholder
        assert _format_cite_placeholder("ref_001") == "[CITE:ref_001]"
        # _insert_citations_for_literature
        assert _insert_citations_for_literature(["ref_001", "ref_002"]) == "[CITE:ref_001][CITE:ref_002]"
        assert _insert_citations_for_literature([]) == ""
        # _next_version
        pw = writer
        assert pw._next_version("v0.1") == "v0.2"
        assert pw._next_version("v0.9") == "v0.10"
        assert pw._next_version("v1.0") == "v1.1"
        assert pw._next_version("invalid") == "v0.1"
        # _scan_placeholders
        assert pw._scan_placeholders("无占位符") == []
        assert pw._scan_placeholders("[CITE:ref_001]") == [1]
        assert pw._scan_placeholders("[CITE:ref_001] 和 [CITE:ref_002]") == [1, 2]
        # _extract_placeholders
        ph = _extract_placeholders({"_placeholders": {"concept": "量子度规"}})
        assert ph["concept"] == "量子度规"
        assert ph["phenomenon"] == "目标现象", "缺失字段应使用默认值"
        ph2 = _extract_placeholders({})
        assert ph2["concept"] == "核心概念"
        print(f"  _count_words: ✓ (中文按字 + 英文按词)")
        print(f"  _count_paragraphs: ✓ (空行分割)")
        print(f"  _classify_taste: ✓ (high/medium/low)")
        print(f"  _question_to_statement: ✓ (假设优先 + 退化)")
        print(f"  _format_cite_placeholder / _insert_citations_for_literature: ✓")
        print(f"  _next_version: ✓ (v0.1→v0.2, v0.9→v0.10)")
        print(f"  _scan_placeholders: ✓")
        print(f"  _extract_placeholders: ✓ (含默认值兜底)")
        print("  ✓ 全部辅助函数测试通过")

        print("\n" + "=" * 50)
        print("✓ proposal_writer 自检全部通过")
        print("=" * 50)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print("(已清理临时目录)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="申请书撰写引擎")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
