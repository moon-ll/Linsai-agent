#!/usr/bin/env python3
"""科学问题架构师 — 课题研究管线"科学问题构建"阶段的核心模块。

用途：
    从选定的研究课题（topic_generator 产物）出发，按"五要素体系"
    （立项依据 + 科学问题 + 研究内容 + 研究方案 + 特色与创新）
    构建结构化科学问题框架，为后续申请书撰写提供问题骨架。

    位于研究管线"科学问题构建"阶段：
        ... → 02_topic（课题凝练） → 03_question（科学问题构建） → 04_design ...

核心流程：
    1. construct_questions()   从课题构建五要素问题框架
    2. decompose_question()    将主问题分解为子问题（多层级）
    3. validate_question()     按清晰度/可检验性/新颖性/可行性/范畴五维评分
    4. validate_framework()    整体框架验证（汇总摘要）
    5. refine_question()       基于反馈精修问题
    6. export_framework()      导出 markdown / json

五要素体系：
    - 立项依据：为什么研究重要（why this matters）
    - 科学问题：核心待回答问题（core questions）
    - 研究内容：研究什么（what to investigate）
    - 研究方案：如何做（how to do it）
    - 特色与创新：新在哪里（what's new）

验证评分公式：
    overall = 0.20*clarity + 0.25*testability + 0.25*novelty
            + 0.20*feasibility + 0.10*scope
    （各分项 [0,1]，overall 越高越优）

状态持久化：
    {proposal_dir}/03_question/question-framework.json
    使用 common.save_json 原子写入 + common.file_lock("questions-{hash}") 跨进程锁。

用法示例：
    >>> from pathlib import Path
    >>> from question_architect import QuestionArchitect
    >>> architect = QuestionArchitect(Path("/data/proposals/T1"))
    >>> topic = {
    ...     "topic_id": "topic_001",
    ...     "title": "量子度规对固体HHG光谱的调制机制研究",
    ...     "keywords": ["量子度规", "固体HHG", "偏振特性"],
    ...     "methods": ["TDDFT", "SBE"],
    ...     "literature": ["ref_001", "ref_003"],
    ... }
    >>> gap_report = {"gaps": [{"gap_id": "gap_001", "type": "conceptual",
    ...                          "novelty_score": 0.9}]}
    >>> framework = architect.construct_questions(topic, gap_report=gap_report)
    >>> print(framework["validation_summary"]["total_questions"])
    >>> q0 = architect.get_question(framework["main_questions"][0])
    >>> subs = architect.decompose_question(q0, depth=2)
    >>> md = architect.export_framework("markdown")

命令行自检：
    python3 scripts/question_architect.py --self-check

规范：仅 Python 标准库，pathlib.Path 路径处理，JSON ensure_ascii=False，时间戳 UTC ISO。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock, lazy_load

__all__ = [
    "QuestionArchitect",
    "QUESTION_TYPES",
    "QUESTION_TYPE_LABELS",
    "QUESTION_ELEMENTS",
    "VALIDATION_WEIGHTS",
    "QUESTION_TEMPLATES",
    "DECOMPOSE_TEMPLATES",
    "DETAIL_TEMPLATES",
    "QUESTION_STATUS_FLOW",
]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 问题类型
QUESTION_TYPES = ("mechanism", "methodology", "empirical", "theoretical", "comparative")

QUESTION_TYPE_LABELS: Dict[str, str] = {
    "mechanism": "机制型",
    "methodology": "方法论型",
    "empirical": "经验型",
    "theoretical": "理论型",
    "comparative": "比较型",
}

# 五要素体系
QUESTION_ELEMENTS = (
    "立项依据",
    "科学问题",
    "研究内容",
    "研究方案",
    "特色与创新",
)

# 验证五维权重（之和为 1.0）
VALIDATION_WEIGHTS: Dict[str, float] = {
    "clarity": 0.20,
    "testability": 0.25,
    "novelty": 0.25,
    "feasibility": 0.20,
    "scope": 0.10,
}

# 主问题模板：按要素映射到问题类型与文本模板
QUESTION_TEMPLATES: Dict[str, Dict[str, str]] = {
    "立项依据": {
        "type": "theoretical",
        "template": "{concept}为何成为{field}领域亟待解决的关键问题？",
    },
    "科学问题": {
        "type": "mechanism",
        "template": "{concept}如何调制{phenomenon}的{aspect}？",
    },
    "研究内容": {
        "type": "empirical",
        "template": "{condition}下{phenomenon}表现为何种特征？",
    },
    "研究方案": {
        "type": "methodology",
        "template": "如何利用{method}测量/计算{quantity}？",
    },
    "特色与创新": {
        "type": "comparative",
        "template": "本研究相比现有工作在{aspect}上有何独特贡献？",
    },
}

# 子问题分解模板：按主问题类型映射到 2-3 个子问题模板
DECOMPOSE_TEMPLATES: Dict[str, List[str]] = {
    "mechanism": [
        "{concept}影响{phenomenon}的关键路径是什么？",
        "{concept}的{aspect}在不同{condition}下如何变化？",
        "{concept}与其他因素在{aspect}上的相对贡献如何？",
    ],
    "methodology": [
        "{method}测量/计算{quantity}的精度与适用范围如何？",
        "{method}在{condition}下的鲁棒性如何？",
        "如何标定与验证{method}的结果？",
    ],
    "empirical": [
        "{condition}下{phenomenon}的关键参数取值范围是什么？",
        "{phenomenon}在不同{condition}间有何系统差异？",
        "{phenomenon}的统计特征是否稳健？",
    ],
    "theoretical": [
        "{theory}能否定量解释{observation}？",
        "{theory}的适用边界在何处？",
        "{theory}与{alternative}相比孰优孰劣？",
    ],
    "comparative": [
        "{system_A}与{system_B}在{aspect}上的定量差异是多少？",
        "造成{system_A}与{system_B}差异的物理根源是什么？",
        "{system_A}相比{system_B}有何独特优势？",
    ],
}

# 细节问题模板（level 2）：按主问题类型各 1 条
DETAIL_TEMPLATES: Dict[str, List[str]] = {
    "mechanism": [
        "在{condition}下{concept}对{phenomenon}的影响幅度是多少？",
    ],
    "methodology": [
        "{method}的误差来源与不确定性如何量化？",
    ],
    "empirical": [
        "{phenomenon}的{aspect}是否随{condition}系统变化？",
    ],
    "theoretical": [
        "{theory}的预测在何种参数区间失效？",
    ],
    "comparative": [
        "{system_A}与{system_B}差异的统计显著性如何？",
    ],
}

# 问题状态机
QUESTION_STATUS_FLOW: Dict[str, set] = {
    "draft": {"validated", "refined", "rejected"},
    "validated": {"refined", "rejected"},
    "refined": {"validated", "rejected"},
    "rejected": set(),  # 终态
}

# 问题类型 → 关联缺口类型（用于证据链接）
_QUESTION_TYPE_TO_GAP_TYPE: Dict[str, str] = {
    "mechanism": "conceptual",
    "methodology": "methodological",
    "empirical": "empirical",
    "theoretical": "theoretical",
    "comparative": "conceptual",
}

# 中文疑问词（用于清晰度评分）
_INTERROGATIVES = ("如何", "为何", "为什么", "是什么", "有哪些", "有何",
                   "是否", "能否", "怎样", "孰", "多少", "哪种")


# ---------------------------------------------------------------------------
# QuestionArchitect
# ---------------------------------------------------------------------------

class QuestionArchitect:
    """科学问题架构师。

    从选定课题构建结构化科学问题框架（五要素体系），提供分解、验证、
    精修、导出能力，为申请书撰写奠定问题骨架。

    线程安全：所有写操作通过 common.file_lock（fcntl.flock 跨进程锁）保护
    read-modify-write 临界区，锁键基于 proposal_dir 路径哈希，不同 proposal 互不阻塞。
    """

    def __init__(self, proposal_dir: Path | str) -> None:
        """初始化科学问题架构师。

        Args:
            proposal_dir: proposal 根目录（Path 或字符串），
                          问题框架保存于其下的 03_question/question-framework.json。
        """
        self.proposal_dir = Path(proposal_dir)
        self.question_dir = self.proposal_dir / "03_question"
        self.framework_path = self.question_dir / "question-framework.json"
        self.gap_report_path = self.proposal_dir / "02_topic" / "gap-report.json"

        # 跨进程锁键：基于 proposal_dir 绝对路径哈希，避免不同 proposal 互相阻塞
        digest = hashlib.md5(
            str(self.proposal_dir.resolve()).encode("utf-8")
        ).hexdigest()[:12]
        self._lock_name = f"questions-{digest}"

        # 内存缓存
        self.framework: Optional[Dict[str, Any]] = None
        self._gap_map: Dict[str, Dict[str, Any]] = {}
        self._last_placeholders: Dict[str, str] = {}
        self._lineage_tracker = None
        self._artifact_manager = None

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

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------

    def _load_framework(self) -> Optional[Dict[str, Any]]:
        """加载已保存的问题框架；不存在或格式错误返回 None。"""
        if not self.framework_path.exists():
            return None
        data = load_json(self.framework_path, None)
        if not isinstance(data, dict):
            return None
        if "all_questions" not in data:
            return None
        return data

    def _save_framework(self, framework: Dict[str, Any]) -> None:
        """保存问题框架（原子写入 + 文件锁）。"""
        self.question_dir.mkdir(parents=True, exist_ok=True)
        with file_lock(self._lock_name):
            save_json(self.framework_path, framework)

    def _save_framework_locked(self, framework: Dict[str, Any]) -> None:
        """保存问题框架（原子写入，不获取锁；供已持锁的调用方使用）。

        注意：fcntl.flock 不可重入，已持锁的临界区内不得再次 file_lock 同名锁，
        否则会自死锁。此方法仅做目录创建 + 原子写入，由调用方保证锁。
        """
        self.question_dir.mkdir(parents=True, exist_ok=True)
        save_json(self.framework_path, framework)

    def _load_gap_report(self) -> Optional[Dict[str, Any]]:
        """加载已保存的缺口报告；不存在返回 None。"""
        if not self.gap_report_path.exists():
            return None
        return load_json(self.gap_report_path, None)

    # ------------------------------------------------------------------
    # 框架 ID 与占位符
    # ------------------------------------------------------------------

    def _next_framework_id(self) -> str:
        """生成下一个框架ID（递增编号：fw_001、fw_002 ...）。"""
        existing = self._load_framework()
        if existing:
            prev = existing.get("framework_id", "fw_000")
            try:
                num = int(prev.split("_")[-1]) + 1
                return f"fw_{num:03d}"
            except (ValueError, IndexError):
                pass
        return "fw_001"

    def _extract_placeholders(self, topic: Dict[str, Any]) -> Dict[str, str]:
        """从课题字典提取模板占位符（含默认值兜底）。"""
        keywords = topic.get("keywords", []) or []
        title = topic.get("title", "") or ""

        concept = (keywords[0] if keywords else
                   (title.split("的")[0] if "的" in title else "核心概念"))
        phenomenon = (topic.get("phenomenon") or
                      (keywords[1] if len(keywords) > 1 else "目标现象"))
        aspect = topic.get("aspect", "关键特性")
        methods = topic.get("methods", []) or []
        method = methods[0] if methods else "理论分析"
        quantity = topic.get("quantity", "相关物理量")
        condition = topic.get("condition", "不同实验条件")
        field = topic.get("field", "强场超快光学")
        theory = topic.get("theory") or concept
        observation = topic.get("observation", "实验观测")
        alternative = topic.get("alternative", "现有理论")
        system_a = topic.get("system_A") or concept
        system_b = topic.get("system_B", "对比体系")

        return {
            "concept": concept,
            "phenomenon": phenomenon,
            "aspect": aspect,
            "method": method,
            "quantity": quantity,
            "condition": condition,
            "field": field,
            "theory": theory,
            "observation": observation,
            "alternative": alternative,
            "system_A": system_a,
            "system_B": system_b,
        }

    def _default_placeholders(self) -> Dict[str, str]:
        """默认占位符（无课题上下文时的兜底）。"""
        return {
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

    def _placeholders_for_question(self, question: Dict[str, Any]) -> Dict[str, str]:
        """获取问题的模板占位符（优先用缓存，其次从框架读取，最后兜底）。"""
        if self._last_placeholders:
            return dict(self._last_placeholders)
        framework = self._load_framework()
        if framework and isinstance(framework.get("_placeholders"), dict):
            return dict(framework["_placeholders"])
        return self._default_placeholders()

    def _derive_hypothesis(self, element: str, p: Dict[str, str]) -> str:
        """从要素与占位符推导假设。"""
        concept = p.get("concept", "")
        phenomenon = p.get("phenomenon", "")
        aspect = p.get("aspect", "")
        if element == "立项依据":
            return f"{concept}的研究将揭示{phenomenon}的新机制"
        if element == "科学问题":
            return f"{concept}主导{phenomenon}的{aspect}变化"
        if element == "研究内容":
            return f"{phenomenon}在不同条件下呈现可表征的{aspect}特征"
        if element == "研究方案":
            return f"所选方法可定量刻画{concept}对{phenomenon}的影响"
        if element == "特色与创新":
            return f"本研究在{aspect}上相比现有工作有显著突破"
        return ""

    # ------------------------------------------------------------------
    # 证据链接
    # ------------------------------------------------------------------

    def _build_gap_map(
        self, gap_report: Optional[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """从缺口报告构建 gap_id → gap 字典。"""
        if not gap_report:
            return {}
        gaps = gap_report.get("gaps", []) or []
        return {g.get("gap_id", ""): g for g in gaps if g.get("gap_id")}

    def _link_evidence(
        self,
        q_type: str,
        element: str,
        topic: Dict[str, Any],
        gap_map: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """为问题链接证据（缺口/文献/方法）。"""
        target_gap_type = _QUESTION_TYPE_TO_GAP_TYPE.get(q_type, "")

        linked_gaps: List[str] = []
        # 优先链接同类型缺口
        for gid, g in gap_map.items():
            if g.get("type") == target_gap_type:
                linked_gaps.append(gid)
                if len(linked_gaps) >= 3:
                    break
        # 兜底：若无同类型缺口，取前 2 个
        if not linked_gaps and gap_map:
            linked_gaps = list(gap_map.keys())[:2]

        methods = list(topic.get("methods", []) or [])[:3]
        literature = list(topic.get("literature", []) or [])[:3]

        return {
            "gaps": linked_gaps,
            "literature": literature,
            "methods": methods,
        }

    # ------------------------------------------------------------------
    # 评分函数
    # ------------------------------------------------------------------

    def _score_clarity(self, text: str) -> float:
        """清晰度评分：基于问题结构（问号 + 疑问词 + 长度）。"""
        if not text:
            return 0.1
        score = 0.3  # 基础分
        # 问号
        if "？" in text or "?" in text:
            score += 0.2
        # 疑问词
        if any(w in text for w in _INTERROGATIVES):
            score += 0.25
        # 长度区间
        length = len(text)
        if 10 <= length <= 60:
            score += 0.25
        elif 5 <= length < 10 or 60 < length <= 100:
            score += 0.1
        # 含未填充占位符 → 重罚
        if "{" in text and "}" in text:
            score -= 0.3
        return max(0.0, min(1.0, score))

    def _score_testability(self, q_type: str, evidence: Dict[str, Any]) -> float:
        """可检验性评分：基于可用方法 + 问题类型。"""
        methods = evidence.get("methods", []) or []
        score = 0.4  # 基础分
        if methods:
            score += 0.15 * min(len(methods), 4)
        if q_type in ("empirical", "methodology"):
            score += 0.1
        elif q_type == "mechanism":
            score += 0.05
        return min(1.0, score)

    def _score_novelty(
        self, evidence: Dict[str, Any], hypothesis: str = ""
    ) -> float:
        """新颖性评分：基于缺口新颖性 + 假设存在。"""
        gaps = evidence.get("gaps", []) or []
        novelty_scores: List[float] = []
        for gid in gaps:
            gap = self._gap_map.get(gid, {})
            if "novelty_score" in gap:
                try:
                    novelty_scores.append(float(gap["novelty_score"]))
                except (TypeError, ValueError):
                    pass
        if novelty_scores:
            score = sum(novelty_scores) / len(novelty_scores)
        else:
            score = 0.5
        if hypothesis:
            score = min(1.0, score + 0.05)
        return max(0.0, min(1.0, score))

    def _score_feasibility(self, evidence: Dict[str, Any]) -> float:
        """可行性评分：基于方法可用性 + 文献支撑。"""
        methods = evidence.get("methods", []) or []
        literature = evidence.get("literature", []) or []
        score = 0.4
        if methods:
            score += 0.15 * min(len(methods), 3)
        if literature:
            score += 0.1 * min(len(literature), 3)
        return min(1.0, score)

    def _score_scope(self, text: str) -> float:
        """范畴评分：基于问题长度与具体性。"""
        if not text:
            return 0.2
        length = len(text)
        if 15 <= length <= 50:
            score = 0.9  # focused
        elif 10 <= length < 15 or 50 < length <= 80:
            score = 0.7  # moderate
        elif 5 <= length < 10 or 80 < length <= 120:
            score = 0.5  # broad or narrow
        else:
            score = 0.3  # too broad or too narrow
        return score

    @staticmethod
    def _score_to_level(score: float) -> str:
        """分数到 high/medium/low 档位。"""
        if score >= 0.7:
            return "high"
        if score >= 0.4:
            return "medium"
        return "low"

    @staticmethod
    def _score_to_scope(score: float) -> str:
        """分数到 focused/moderate/broad 档位。"""
        if score >= 0.75:
            return "focused"
        if score >= 0.5:
            return "moderate"
        return "broad"

    # ------------------------------------------------------------------
    # 核心接口：构建 / 分解 / 验证
    # ------------------------------------------------------------------

    def construct_questions(
        self,
        topic: Dict[str, Any],
        gap_report: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """从选定课题构建科学问题框架（五要素体系）。

        流程：
          1. 为五要素各生成 1 个主问题（level 0）
          2. 为每个主问题分解出 2 个子问题 + 1 个细节问题（level 1/2）
          3. 链接证据（缺口/文献/方法）
          4. 逐个验证（5 维评分）
          5. 汇总验证摘要，持久化，注册血缘与产物

        Args:
            topic: 课题字典，含 topic_id / title / keywords / methods / literature 等
            gap_report: 可选缺口报告，用于证据链接与新颖性评分

        Returns:
            完整的问题框架字典
        """
        if not isinstance(topic, dict):
            raise ValueError("topic 必须为字典")

        topic_id = topic.get("topic_id", "") or "topic_unknown"
        topic_title = topic.get("title", "") or "未命名课题"

        placeholders = self._extract_placeholders(topic)
        self._last_placeholders = dict(placeholders)

        # 构建缺口索引
        gap_map = self._build_gap_map(gap_report)
        # 合并已存盘的缺口报告（覆盖传入参数，避免重复）
        if not gap_map:
            stored = self._load_gap_report()
            if stored:
                gap_map = self._build_gap_map(stored)
        self._gap_map = gap_map

        framework_id = self._next_framework_id()
        all_questions: Dict[str, Dict[str, Any]] = {}
        elements: Dict[str, List[str]] = {e: [] for e in QUESTION_ELEMENTS}
        main_questions: List[str] = []
        qid_counter = 0

        for element in QUESTION_ELEMENTS:
            qid_counter += 1
            qid = f"q_{qid_counter:03d}"
            tmpl_info = QUESTION_TEMPLATES[element]
            q_type = tmpl_info["type"]
            try:
                text = tmpl_info["template"].format(**placeholders)
            except (KeyError, IndexError):
                text = tmpl_info["template"]

            evidence = self._link_evidence(q_type, element, topic, gap_map)
            hypothesis = self._derive_hypothesis(element, placeholders)

            question: Dict[str, Any] = {
                "question_id": qid,
                "level": 0,
                "parent_id": None,
                "text": text,
                "type": q_type,
                "element": element,
                "hypothesis": hypothesis,
                "testability": "medium",
                "novelty": "medium",
                "feasibility": "medium",
                "scope": "moderate",
                "evidence": evidence,
                "validation": {},
                "status": "draft",
                "created_at": now_utc(),
                "updated_at": now_utc(),
            }
            # 验证主问题
            validation = self.validate_question(question)
            question["validation"] = validation
            question["testability"] = self._score_to_level(validation["testability_score"])
            question["novelty"] = self._score_to_level(validation["novelty_score"])
            question["feasibility"] = self._score_to_level(validation["feasibility_score"])
            question["scope"] = self._score_to_scope(validation["scope_score"])

            all_questions[qid] = question
            elements[element].append(qid)
            main_questions.append(qid)

            # 分解子问题
            sub_qs = self.decompose_question(question, depth=2)
            last_level1_qid: Optional[str] = None
            for sq in sub_qs:
                qid_counter += 1
                sqid = f"q_{qid_counter:03d}"
                level = sq.get("level", 1)
                if level == 1:
                    parent_id = qid
                    last_level1_qid = sqid
                elif level == 2:
                    parent_id = last_level1_qid or qid
                else:
                    parent_id = qid

                sq["question_id"] = sqid
                sq["parent_id"] = parent_id
                sq_validation = self.validate_question(sq)
                sq["validation"] = sq_validation
                sq["testability"] = self._score_to_level(sq_validation["testability_score"])
                sq["novelty"] = self._score_to_level(sq_validation["novelty_score"])
                sq["feasibility"] = self._score_to_level(sq_validation["feasibility_score"])
                sq["scope"] = self._score_to_scope(sq_validation["scope_score"])
                sq["status"] = "draft"
                sq["created_at"] = now_utc()
                sq["updated_at"] = now_utc()

                all_questions[sqid] = sq
                elements[element].append(sqid)

        framework: Dict[str, Any] = {
            "framework_id": framework_id,
            "topic_id": topic_id,
            "topic_title": topic_title,
            "elements": elements,
            "main_questions": main_questions,
            "all_questions": all_questions,
            "validation_summary": {},
            "created_at": now_utc(),
            "updated_at": now_utc(),
            "_placeholders": placeholders,  # 内部元数据，供后续 decompose 复用
        }
        framework["validation_summary"] = self._compute_validation_summary(framework)

        self._save_framework(framework)
        self.framework = framework

        # 注册血缘与产物（失败不阻塞）
        self._register_lineage(framework, topic)
        self._register_artifact(framework)

        return framework

    def decompose_question(
        self, question: Dict[str, Any], depth: int = 2
    ) -> List[Dict[str, Any]]:
        """将主问题分解为子问题（支持多层级）。

        Args:
            question: 主问题字典（level=0）
            depth: 分解深度
                1 = 仅生成 level-1 子问题（2 个）
                2 = level-1 子问题（2 个）+ level-2 细节问题（每子问题 1 个）= 4 个

        Returns:
            子问题字典列表（不含 question_id；parent_id 由调用方在层级装配时填充）
        """
        if depth < 1:
            depth = 1

        q_type = question.get("type", "mechanism")
        element = question.get("element", "科学问题")
        evidence = question.get("evidence", {"gaps": [], "literature": [], "methods": []})
        placeholders = self._placeholders_for_question(question)

        sub_templates = DECOMPOSE_TEMPLATES.get(q_type, DECOMPOSE_TEMPLATES["mechanism"])
        detail_templates = DETAIL_TEMPLATES.get(q_type, [])

        sub_questions: List[Dict[str, Any]] = []
        n_level1 = 2

        for i in range(n_level1):
            template = sub_templates[i % len(sub_templates)]
            try:
                sub_text = template.format(**placeholders)
            except (KeyError, IndexError):
                sub_text = template

            sub_q: Dict[str, Any] = {
                "level": 1,
                "parent_id": None,
                "text": sub_text,
                "type": q_type,
                "element": element,
                "hypothesis": "",
                "testability": "medium",
                "novelty": "medium",
                "feasibility": "medium",
                "scope": "moderate",
                "evidence": {
                    "gaps": list(evidence.get("gaps", [])),
                    "literature": list(evidence.get("literature", [])),
                    "methods": list(evidence.get("methods", [])),
                },
                "validation": {},
                "status": "draft",
            }
            sub_questions.append(sub_q)

            # level 2 细节问题
            if depth >= 2 and detail_templates:
                dt = detail_templates[0]
                try:
                    detail_text = dt.format(**placeholders)
                except (KeyError, IndexError):
                    detail_text = dt
                detail_q: Dict[str, Any] = {
                    "level": 2,
                    "parent_id": None,
                    "text": detail_text,
                    "type": q_type,
                    "element": element,
                    "hypothesis": "",
                    "testability": "medium",
                    "novelty": "medium",
                    "feasibility": "medium",
                    "scope": "moderate",
                    "evidence": {
                        "gaps": list(evidence.get("gaps", [])),
                        "literature": list(evidence.get("literature", [])),
                        "methods": list(evidence.get("methods", [])),
                    },
                    "validation": {},
                    "status": "draft",
                }
                sub_questions.append(detail_q)

        return sub_questions

    def validate_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """验证单个问题，返回 validation 字典。

        评分维度（各 [0,1]）：
            - clarity       清晰度（结构、问号、疑问词、长度）
            - testability   可检验性（方法可用性 + 问题类型）
            - novelty       新颖性（关联缺口新颖性 + 假设）
            - feasibility   可行性（方法 + 文献支撑）
            - scope         范畴（长度区间）

        overall = 0.20*clarity + 0.25*testability + 0.25*novelty
                + 0.20*feasibility + 0.10*scope
        """
        text = question.get("text", "")
        q_type = question.get("type", "mechanism")
        evidence = question.get("evidence", {}) or {}
        hypothesis = question.get("hypothesis", "")

        clarity = self._score_clarity(text)
        testability = self._score_testability(q_type, evidence)
        novelty = self._score_novelty(evidence, hypothesis)
        feasibility = self._score_feasibility(evidence)
        scope = self._score_scope(text)

        overall = round(
            VALIDATION_WEIGHTS["clarity"] * clarity
            + VALIDATION_WEIGHTS["testability"] * testability
            + VALIDATION_WEIGHTS["novelty"] * novelty
            + VALIDATION_WEIGHTS["feasibility"] * feasibility
            + VALIDATION_WEIGHTS["scope"] * scope,
            4,
        )

        issues: List[str] = []
        if clarity < 0.5:
            issues.append("问题表述不够清晰，建议补充主语/谓语/宾语与疑问词")
        if testability < 0.5:
            issues.append("可检验性不足，缺少明确的实验/计算方法支撑")
        if novelty < 0.5:
            issues.append("新颖性偏弱，建议关联更多研究缺口或强化假设")
        if feasibility < 0.5:
            issues.append("可行性偏低，方法或文献支撑不足")
        if scope < 0.5:
            issues.append("范畴不当（过宽或过窄），建议聚焦核心变量")

        return {
            "clarity_score": round(clarity, 4),
            "testability_score": round(testability, 4),
            "novelty_score": round(novelty, 4),
            "feasibility_score": round(feasibility, 4),
            "scope_score": round(scope, 4),
            "overall": overall,
            "issues": issues,
        }

    def validate_framework(
        self, framework: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """验证整个问题框架，返回验证摘要。

        Args:
            framework: 待验证框架；为 None 时使用当前框架（先内存后磁盘）。

        Returns:
            验证摘要字典（含 total_questions、avg_overall、by_element、by_type 等）
        """
        if framework is None:
            framework = self.get_framework()
        return self._compute_validation_summary(framework)

    def _compute_validation_summary(
        self, framework: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算框架的验证摘要。"""
        all_qs = framework.get("all_questions", {}) or {}
        if not all_qs:
            return {
                "total_questions": 0,
                "avg_overall": 0.0,
                "avg_clarity": 0.0,
                "avg_testability": 0.0,
                "avg_novelty": 0.0,
                "avg_feasibility": 0.0,
                "avg_scope": 0.0,
                "high_quality_count": 0,
                "low_quality_count": 0,
                "issues_count": 0,
                "by_element": {},
                "by_type": {},
            }

        totals = {
            "clarity": 0.0, "testability": 0.0, "novelty": 0.0,
            "feasibility": 0.0, "scope": 0.0, "overall": 0.0,
        }
        high_count = 0
        low_count = 0
        issues_count = 0
        by_element: Dict[str, List[float]] = {}
        by_type: Dict[str, List[float]] = {}

        for q in all_qs.values():
            v = q.get("validation", {}) or {}
            totals["clarity"] += float(v.get("clarity_score", 0.0))
            totals["testability"] += float(v.get("testability_score", 0.0))
            totals["novelty"] += float(v.get("novelty_score", 0.0))
            totals["feasibility"] += float(v.get("feasibility_score", 0.0))
            totals["scope"] += float(v.get("scope_score", 0.0))
            totals["overall"] += float(v.get("overall", 0.0))

            overall = float(v.get("overall", 0.0))
            if overall >= 0.7:
                high_count += 1
            elif overall < 0.5:
                low_count += 1

            issues_count += len(v.get("issues", []) or [])

            element = q.get("element", "")
            by_element.setdefault(element, []).append(overall)
            q_type = q.get("type", "")
            by_type.setdefault(q_type, []).append(overall)

        n = len(all_qs)

        def avg(lst: List[float]) -> float:
            return round(sum(lst) / len(lst), 4) if lst else 0.0

        return {
            "total_questions": n,
            "avg_overall": round(totals["overall"] / n, 4),
            "avg_clarity": round(totals["clarity"] / n, 4),
            "avg_testability": round(totals["testability"] / n, 4),
            "avg_novelty": round(totals["novelty"] / n, 4),
            "avg_feasibility": round(totals["feasibility"] / n, 4),
            "avg_scope": round(totals["scope"] / n, 4),
            "high_quality_count": high_count,
            "low_quality_count": low_count,
            "issues_count": issues_count,
            "by_element": {
                k: {"count": len(v), "avg_overall": avg(v)}
                for k, v in by_element.items()
            },
            "by_type": {
                k: {"count": len(v), "avg_overall": avg(v)}
                for k, v in by_type.items()
            },
        }

    # ------------------------------------------------------------------
    # 读取与精修
    # ------------------------------------------------------------------

    def get_framework(self) -> Dict[str, Any]:
        """获取当前问题框架（先内存，再磁盘；都没有则返回空框架）。"""
        if self.framework is not None:
            return self.framework
        framework = self._load_framework()
        if framework is not None:
            self.framework = framework
            # 恢复占位符与缺口索引缓存
            if isinstance(framework.get("_placeholders"), dict):
                self._last_placeholders = dict(framework["_placeholders"])
            self._gap_map = self._build_gap_map(self._load_gap_report())
            return framework
        return {
            "framework_id": "",
            "topic_id": "",
            "topic_title": "",
            "elements": {e: [] for e in QUESTION_ELEMENTS},
            "main_questions": [],
            "all_questions": {},
            "validation_summary": {},
            "created_at": "",
            "updated_at": "",
        }

    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """获取单个问题；不存在返回 None。"""
        framework = self.get_framework()
        q = framework.get("all_questions", {}).get(question_id)
        return dict(q) if q else None

    def refine_question(
        self, question_id: str, feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """基于反馈精修问题。

        feedback 字典可包含任意组合：
            - text: 新的问题文本
            - hypothesis: 新的假设
            - element: 调整要素归属
            - type: 调整问题类型
            - evidence_add: 追加证据 {"gaps": [...], "literature": [...], "methods": [...]}
            - status: 显式设置状态（validated/refined/rejected）

        Returns:
            精修后的问题字典（副本）

        Raises:
            ValueError: 框架未初始化
            KeyError: 问题不存在
        """
        if not isinstance(feedback, dict):
            raise ValueError("feedback 必须为字典")

        with file_lock(self._lock_name):
            framework = self._load_framework()
            if framework is None:
                raise ValueError("问题框架未初始化，请先 construct_questions()")
            all_qs = framework.get("all_questions", {})
            if question_id not in all_qs:
                raise KeyError(f"问题不存在: {question_id}")

            q = all_qs[question_id]

            if "text" in feedback and feedback["text"]:
                q["text"] = feedback["text"]
            if "hypothesis" in feedback:
                q["hypothesis"] = feedback["hypothesis"]
            if "element" in feedback and feedback["element"] in QUESTION_ELEMENTS:
                q["element"] = feedback["element"]
            if "type" in feedback and feedback["type"] in QUESTION_TYPES:
                q["type"] = feedback["type"]
            if "evidence_add" in feedback and isinstance(feedback["evidence_add"], dict):
                ev = q.setdefault("evidence", {"gaps": [], "literature": [], "methods": []})
                for k in ("gaps", "literature", "methods"):
                    for item in feedback["evidence_add"].get(k, []) or []:
                        if item not in ev.get(k, []):
                            ev.setdefault(k, []).append(item)

            # 重新验证
            validation = self.validate_question(q)
            q["validation"] = validation
            q["testability"] = self._score_to_level(validation["testability_score"])
            q["novelty"] = self._score_to_level(validation["novelty_score"])
            q["feasibility"] = self._score_to_level(validation["feasibility_score"])
            q["scope"] = self._score_to_scope(validation["scope_score"])

            # 状态流转
            new_status = feedback.get("status")
            if new_status and new_status in QUESTION_STATUS_FLOW:
                q["status"] = new_status
            elif q.get("status") == "draft":
                q["status"] = "refined"
            else:
                q["status"] = "refined"

            q["updated_at"] = now_utc()
            framework["updated_at"] = now_utc()
            framework["validation_summary"] = self._compute_validation_summary(framework)

            # 已在 file_lock 临界区内，使用 _save_framework_locked 避免重入死锁
            self._save_framework_locked(framework)
            self.framework = framework
            return dict(q)

    def get_question_evidence(self, question_id: str) -> Dict[str, Any]:
        """获取支撑某问题的证据（含缺口详情）。

        Returns:
            {"gaps": [...], "literature": [...], "methods": [...], "gap_details": [...]}
            问题不存在时各字段为空。
        """
        framework = self.get_framework()
        q = framework.get("all_questions", {}).get(question_id)
        if q is None:
            return {"gaps": [], "literature": [], "methods": [], "gap_details": []}
        evidence = q.get("evidence", {}) or {}

        # 查找缺口详情（先内存缓存，再磁盘 gap-report.json）
        gap_map = self._gap_map
        if not gap_map:
            gap_map = self._build_gap_map(self._load_gap_report())
            self._gap_map = gap_map

        gap_details: List[Dict[str, Any]] = []
        for gid in evidence.get("gaps", []) or []:
            if gid in gap_map:
                gap_details.append(dict(gap_map[gid]))

        return {
            "gaps": list(evidence.get("gaps", []) or []),
            "literature": list(evidence.get("literature", []) or []),
            "methods": list(evidence.get("methods", []) or []),
            "gap_details": gap_details,
        }

    # ------------------------------------------------------------------
    # 导出
    # ------------------------------------------------------------------

    def export_framework(self, format: str = "markdown") -> str:
        """导出问题框架为 Markdown 或 JSON 字符串。

        Args:
            format: "markdown" 或 "json"

        Returns:
            格式化的框架字符串；无框架时返回占位提示。
        """
        framework = self._load_framework()
        if framework is None:
            if format == "json":
                return "{}"
            return "# 科学问题框架\n\n（暂无框架，请先运行 construct_questions()）\n"

        if format == "json":
            return json.dumps(framework, ensure_ascii=False, indent=2)

        return self._framework_to_markdown(framework)

    def _framework_to_markdown(self, framework: Dict[str, Any]) -> str:
        """将框架字典渲染为 Markdown 文本。"""
        lines: List[str] = []
        lines.append("# 科学问题框架\n")
        lines.append(f"**框架ID**：{framework.get('framework_id', '')}")
        lines.append(f"**课题**：{framework.get('topic_title', '')}")
        lines.append(f"**课题ID**：{framework.get('topic_id', '')}")
        lines.append(f"**创建时间**：{framework.get('created_at', '')}")
        lines.append(f"**更新时间**：{framework.get('updated_at', '')}\n")

        vs = framework.get("validation_summary", {}) or {}
        lines.append("## 验证摘要\n")
        lines.append(f"- 问题总数：{vs.get('total_questions', 0)}")
        lines.append(f"- 平均综合分：{vs.get('avg_overall', 0)}")
        lines.append(f"- 平均清晰度：{vs.get('avg_clarity', 0)}")
        lines.append(f"- 平均可检验性：{vs.get('avg_testability', 0)}")
        lines.append(f"- 平均新颖性：{vs.get('avg_novelty', 0)}")
        lines.append(f"- 平均可行性：{vs.get('avg_feasibility', 0)}")
        lines.append(f"- 平均范畴：{vs.get('avg_scope', 0)}")
        lines.append(f"- 高质量问题数（≥0.7）：{vs.get('high_quality_count', 0)}")
        lines.append(f"- 低质量问题数（<0.5）：{vs.get('low_quality_count', 0)}")
        lines.append(f"- 待改进问题项数：{vs.get('issues_count', 0)}\n")

        lines.append("## 按要素分布\n")
        for element in QUESTION_ELEMENTS:
            qids = framework.get("elements", {}).get(element, []) or []
            lines.append(f"- **{element}**：{len(qids)} 个问题")
        lines.append("")

        all_qs = framework.get("all_questions", {}) or {}
        for element in QUESTION_ELEMENTS:
            lines.append(f"## {element}\n")
            qids = framework.get("elements", {}).get(element, []) or []
            main_qs = [qid for qid in qids
                       if all_qs.get(qid, {}).get("level") == 0]
            for qid in main_qs:
                q = all_qs.get(qid, {})
                type_label = QUESTION_TYPE_LABELS.get(q.get("type", ""), q.get("type", ""))
                lines.append(
                    f"### {qid}（{type_label}）"
                )
                lines.append(f"\n{q.get('text', '')}\n")
                v = q.get("validation", {}) or {}
                lines.append(f"- 综合分：{v.get('overall', 0)}")
                lines.append(
                    f"- 清晰度 {v.get('clarity_score', 0)} | "
                    f"可检验性 {v.get('testability_score', 0)} | "
                    f"新颖性 {v.get('novelty_score', 0)} | "
                    f"可行性 {v.get('feasibility_score', 0)} | "
                    f"范畴 {v.get('scope_score', 0)}"
                )
                if q.get("hypothesis"):
                    lines.append(f"- **假设**：{q['hypothesis']}")
                ev = q.get("evidence", {}) or {}
                if ev.get("gaps") or ev.get("literature") or ev.get("methods"):
                    lines.append(
                        f"- **证据**：缺口 {ev.get('gaps', [])} / "
                        f"文献 {ev.get('literature', [])} / "
                        f"方法 {ev.get('methods', [])}"
                    )
                if q.get("status"):
                    lines.append(f"- **状态**：{q['status']}")
                if v.get("issues"):
                    lines.append(f"- **待改进**：{'；'.join(v['issues'])}")
                lines.append("")

                # 子问题与细节问题
                subs = [qid2 for qid2 in qids
                        if all_qs.get(qid2, {}).get("parent_id") == qid]
                for sid in subs:
                    sq = all_qs.get(sid, {})
                    level = sq.get("level", 1)
                    if level == 1:
                        prefix = "  - "
                    else:
                        prefix = "    * "
                    sv = sq.get("validation", {}) or {}
                    lines.append(
                        f"{prefix}{sid}: {sq.get('text', '')} "
                        f"(综合分: {sv.get('overall', 0)})"
                    )
                lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 血缘与产物注册
    # ------------------------------------------------------------------

    def _register_lineage(
        self, framework: Dict[str, Any], topic: Dict[str, Any]
    ) -> None:
        """向血缘追踪器注册问题框架与各问题（可选，失败不阻塞）。"""
        tracker_mod = self._load_lineage_tracker()
        if tracker_mod is None:
            return
        try:
            tracker = tracker_mod.LineageTracker(self.proposal_dir)
            fw_id = framework.get("framework_id", "")
            topic_title = framework.get("topic_title", "")
            tracker.register_node(
                fw_id, "question_framework",
                f"科学问题框架: {topic_title}",
                stage=3,
            )
            topic_id = topic.get("topic_id", "")
            if topic_id:
                try:
                    tracker.add_edge(
                        fw_id, topic_id, "derived_from",
                        "问题框架从课题推导而来",
                    )
                except Exception:
                    pass
            for qid, q in framework.get("all_questions", {}).items():
                try:
                    tracker.register_node(
                        qid, "scientific_question",
                        q.get("text", "")[:60],
                        stage=3,
                    )
                    tracker.add_edge(
                        qid, fw_id, "belongs_to",
                        f"问题属于{fw_id}",
                    )
                except Exception:
                    pass
        except Exception:
            pass

    def _register_artifact(self, framework: Dict[str, Any]) -> None:
        """注册问题框架为产物（可选，失败不阻塞）。"""
        am_mod = self._load_artifact_manager()
        if am_mod is None:
            return
        try:
            mgr = am_mod.ArtifactManager(self.proposal_dir)
            content = self._framework_to_markdown(framework)
            artifact_id = f"qf_{framework.get('framework_id', '')}"
            if mgr.get_artifact(artifact_id) is None:
                mgr.create_artifact(
                    artifact_id, "question_framework", 3,
                    content, "03_question/question-framework.md",
                    author="pipeline_stage3",
                )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """自检：14 个检查点，使用临时目录与 mock 数据隔离测试。

    覆盖：
      1.  初始化（路径、锁名）
      2.  框架构建（五要素、主问题、子问题）
      3.  问题分解（子问题数量、深度、层级）
      4.  问题验证（5 维分数在 [0,1]、overall 公式、issues 检测）
      5.  框架验证（汇总摘要、按要素/类型分布）
      6.  框架获取（get_framework）
      7.  问题获取（get_question）
      8.  问题精修（refine_question）
      9.  证据链接（get_question_evidence + gap_details）
      10. Markdown 导出
      11. JSON 导出
      12. 空课题处理
      13. 原子写入 + 文件锁
      14. 持久化往返（保存 → 重新加载 → 一致）
    """
    import shutil
    import tempfile

    print("=" * 50)
    print("◐ question_architect 自检")
    print("=" * 50)

    tmp = Path(tempfile.mkdtemp(prefix="question_architect_test_"))
    try:
        proposal_dir = tmp / "T1_proposal"
        architect = QuestionArchitect(proposal_dir)

        # ── mock 数据 ──
        topic = {
            "topic_id": "topic_001",
            "title": "量子度规对固体HHG光谱的调制机制研究",
            "keywords": ["量子度规", "固体HHG", "偏振特性"],
            "direction": "T1",
            "methods": ["TDDFT", "SBE"],
            "literature": ["ref_001", "ref_003"],
            "phenomenon": "固体HHG",
            "aspect": "偏振特性",
        }
        gap_report = {
            "gaps": [
                {"gap_id": "gap_001", "type": "conceptual",
                 "novelty_score": 0.9, "description": "量子度规概念缺口"},
                {"gap_id": "gap_002", "type": "methodological",
                 "novelty_score": 0.6, "description": "SBE 方法缺口"},
                {"gap_id": "gap_003", "type": "theoretical",
                 "novelty_score": 0.7, "description": "拓扑理论缺口"},
                {"gap_id": "gap_004", "type": "empirical",
                 "novelty_score": 0.4, "description": "实验数据缺口"},
            ]
        }

        # ── [1/14] 初始化 ──
        print("\n[1/14] 初始化...")
        assert architect.proposal_dir == proposal_dir
        assert architect.question_dir == proposal_dir / "03_question"
        assert architect.framework_path == proposal_dir / "03_question" / "question-framework.json"
        assert architect._lock_name.startswith("questions-")
        print(f"  proposal_dir: {architect.proposal_dir}")
        print(f"  framework_path: {architect.framework_path}")
        print(f"  lock_name: {architect._lock_name}")
        print("  ✓ 初始化字段完整，锁名按 proposal 隔离")

        # ── [2/14] 框架构建 ──
        print("\n[2/14] 框架构建...")
        framework = architect.construct_questions(topic, gap_report=gap_report)
        print(f"  framework_id: {framework['framework_id']}")
        print(f"  topic_title: {framework['topic_title']}")
        print(f"  主问题数: {len(framework['main_questions'])}")
        print(f"  全部问题数: {len(framework['all_questions'])}")
        # 五要素各 1 主问题
        assert len(framework["main_questions"]) == 5, (
            f"期望 5 个主问题，实际 {len(framework['main_questions'])}"
        )
        # 每个要素都有问题
        for element in QUESTION_ELEMENTS:
            assert element in framework["elements"], f"缺少要素：{element}"
            assert len(framework["elements"][element]) > 0, f"要素 {element} 无问题"
        # 每个主问题 level=0、parent_id=None
        for qid in framework["main_questions"]:
            q = framework["all_questions"][qid]
            assert q["level"] == 0, f"主问题 {qid} level 应为 0"
            assert q["parent_id"] is None, f"主问题 {qid} parent_id 应为 None"
            assert q["element"] in QUESTION_ELEMENTS
            assert q["type"] in QUESTION_TYPES
        # 每个主问题应有 2 子问题 + 2 细节问题 = 4 个后代
        # 总问题数 = 5 主 + 5*4 后代 = 25
        expected_total = 5 + 5 * 4
        assert len(framework["all_questions"]) == expected_total, (
            f"期望 {expected_total} 个问题，实际 {len(framework['all_questions'])}"
        )
        print(f"  每要素问题数: {[len(framework['elements'][e]) for e in QUESTION_ELEMENTS]}")
        print("  ✓ 五要素各 1 主问题 + 子问题，层级正确")

        # ── [3/14] 问题分解 ──
        print("\n[3/14] 问题分解...")
        main_q = architect.get_question(framework["main_questions"][0])
        assert main_q is not None
        # depth=1：仅 2 个 level-1 子问题
        subs_d1 = architect.decompose_question(main_q, depth=1)
        assert len(subs_d1) == 2, f"depth=1 应有 2 个子问题，实际 {len(subs_d1)}"
        assert all(sq["level"] == 1 for sq in subs_d1), "depth=1 应全部为 level 1"
        # depth=2：2 个 level-1 + 2 个 level-2 = 4 个
        subs_d2 = architect.decompose_question(main_q, depth=2)
        assert len(subs_d2) == 4, f"depth=2 应有 4 个子问题，实际 {len(subs_d2)}"
        level_counts = {1: 0, 2: 0}
        for sq in subs_d2:
            level_counts[sq["level"]] = level_counts.get(sq["level"], 0) + 1
        assert level_counts[1] == 2, f"level-1 应为 2 个，实际 {level_counts[1]}"
        assert level_counts[2] == 2, f"level-2 应为 2 个，实际 {level_counts[2]}"
        # 验证子问题文本非空且含疑问词或问号
        for sq in subs_d2:
            assert sq["text"], "子问题文本不应为空"
            assert "？" in sq["text"] or "?" in sq["text"], "子问题应含问号"
        print(f"  depth=1: {len(subs_d1)} 个子问题")
        print(f"  depth=2: {len(subs_d2)} 个子问题（{level_counts[1]} level-1 + {level_counts[2]} level-2）")
        print(f"  示例子问题: {subs_d1[0]['text']}")
        print("  ✓ 分解数量与层级随 depth 变化")

        # ── [4/14] 问题验证 ──
        print("\n[4/14] 问题验证...")
        # 取一个有方法+缺口证据的主问题（科学问题，类型 mechanism）
        sci_qid = framework["elements"]["科学问题"][0]
        sci_q = framework["all_questions"][sci_qid]
        v = sci_q["validation"]
        print(f"  问题: {sci_q['text']}")
        print(f"  清晰度: {v['clarity_score']} | 可检验性: {v['testability_score']} | "
              f"新颖性: {v['novelty_score']} | 可行性: {v['feasibility_score']} | "
              f"范畴: {v['scope_score']}")
        print(f"  综合分: {v['overall']}")
        print(f"  待改进: {v['issues']}")
        # 5 维分数均在 [0, 1]
        for key in ("clarity_score", "testability_score", "novelty_score",
                    "feasibility_score", "scope_score", "overall"):
            assert 0.0 <= v[key] <= 1.0, f"{key} 应在 [0,1]，实际 {v[key]}"
        # 验证 overall 公式
        expected_overall = round(
            VALIDATION_WEIGHTS["clarity"] * v["clarity_score"]
            + VALIDATION_WEIGHTS["testability"] * v["testability_score"]
            + VALIDATION_WEIGHTS["novelty"] * v["novelty_score"]
            + VALIDATION_WEIGHTS["feasibility"] * v["feasibility_score"]
            + VALIDATION_WEIGHTS["scope"] * v["scope_score"],
            4,
        )
        assert abs(v["overall"] - expected_overall) < 1e-6, (
            f"overall 公式错误: expected={expected_overall} actual={v['overall']}"
        )
        # 档位字段与分数一致
        assert sci_q["testability"] == architect._score_to_level(v["testability_score"])
        assert sci_q["scope"] == architect._score_to_scope(v["scope_score"])
        # 对一个低分问题触发 issues 检测（无问号、无疑问词、过短、无证据）
        bad_q = {"text": "abc", "type": "mechanism",
                 "evidence": {"gaps": [], "literature": [], "methods": []}}
        bad_v = architect.validate_question(bad_q)
        assert bad_v["clarity_score"] < 0.5, (
            f"劣质问题清晰度应 < 0.5，实际 {bad_v['clarity_score']}"
        )
        assert bad_v["testability_score"] < 0.5, "劣质问题可检验性应 < 0.5"
        assert bad_v["feasibility_score"] < 0.5, "劣质问题可行性应 < 0.5"
        assert bad_v["scope_score"] < 0.5, "劣质问题范畴应 < 0.5"
        assert len(bad_v["issues"]) >= 4, (
            f"劣质问题应至少检测出 4 个 issues，实际 {len(bad_v['issues'])}"
        )
        print("  ✓ 5 维分数在 [0,1]，overall 公式正确，issues 检测有效")

        # ── [5/14] 框架验证 ──
        print("\n[5/14] 框架验证...")
        summary = architect.validate_framework(framework)
        print(f"  问题总数: {summary['total_questions']}")
        print(f"  平均综合分: {summary['avg_overall']}")
        print(f"  高质量: {summary['high_quality_count']} / 低质量: {summary['low_quality_count']}")
        print(f"  待改进项: {summary['issues_count']}")
        assert summary["total_questions"] == len(framework["all_questions"])
        assert 0.0 <= summary["avg_overall"] <= 1.0
        assert summary["high_quality_count"] + summary["low_quality_count"] <= summary["total_questions"]
        # by_element 覆盖五要素
        for element in QUESTION_ELEMENTS:
            assert element in summary["by_element"], f"by_element 缺少 {element}"
            assert summary["by_element"][element]["count"] > 0
        # by_type 覆盖至少 3 种类型
        assert len(summary["by_type"]) >= 3, (
            f"by_type 应至少 3 种，实际 {len(summary['by_type'])}"
        )
        print(f"  by_element: {dict((k, v['count']) for k, v in summary['by_element'].items())}")
        print(f"  by_type: {dict((k, v['count']) for k, v in summary['by_type'].items())}")
        print("  ✓ 框架验证摘要完整，按要素/类型分布正确")

        # ── [6/14] 框架获取 ──
        print("\n[6/14] 框架获取...")
        # 新实例从磁盘加载
        arch2 = QuestionArchitect(proposal_dir)
        loaded = arch2.get_framework()
        assert loaded["framework_id"] == framework["framework_id"]
        assert loaded["topic_id"] == framework["topic_id"]
        assert len(loaded["all_questions"]) == len(framework["all_questions"])
        assert loaded["validation_summary"]["total_questions"] == summary["total_questions"]
        print(f"  重新加载 framework_id: {loaded['framework_id']}")
        print(f"  重新加载问题数: {len(loaded['all_questions'])}")
        print("  ✓ get_framework 内存/磁盘一致")

        # ── [7/14] 问题获取 ──
        print("\n[7/14] 问题获取...")
        q0 = architect.get_question(framework["main_questions"][0])
        assert q0 is not None
        assert q0["question_id"] == framework["main_questions"][0]
        assert q0["level"] == 0
        # 不存在的问题返回 None
        assert architect.get_question("q_nonexist") is None
        # 返回的是副本（修改不影响内部）
        q0_copy = architect.get_question(framework["main_questions"][0])
        q0_copy["text"] = "modified"
        q0_again = architect.get_question(framework["main_questions"][0])
        assert q0_again["text"] != "modified", "get_question 应返回副本"
        print(f"  获取主问题: {q0['question_id']} - {q0['text'][:30]}...")
        print("  ✓ 问题获取返回副本，不存在返回 None")

        # ── [8/14] 问题精修 ──
        print("\n[8/14] 问题精修...")
        target_qid = framework["main_questions"][1]
        before = architect.get_question(target_qid)
        before_overall = before["validation"]["overall"]
        refined = architect.refine_question(target_qid, {
            "text": "量子度规的非对角分量如何主导固体HHG椭圆率的变化？",
            "hypothesis": "量子度规非对角分量与HHG椭圆率存在定量映射关系",
            "evidence_add": {
                "methods": ["紧束缚模型"],
                "literature": ["ref_007"],
            },
        })
        print(f"  原文本: {before['text'][:40]}...")
        print(f"  新文本: {refined['text'][:40]}...")
        print(f"  原综合分: {before_overall} → 新综合分: {refined['validation']['overall']}")
        assert refined["text"] == "量子度规的非对角分量如何主导固体HHG椭圆率的变化？"
        assert refined["hypothesis"] != ""
        assert refined["status"] == "refined"
        assert "紧束缚模型" in refined["evidence"]["methods"]
        assert "ref_007" in refined["evidence"]["literature"]
        # 重新加载验证持久化
        arch3 = QuestionArchitect(proposal_dir)
        reloaded = arch3.get_question(target_qid)
        assert reloaded["text"] == refined["text"], "精修结果应已持久化"
        assert reloaded["status"] == "refined"
        # 不存在的问题报 KeyError
        try:
            architect.refine_question("q_nonexist", {"text": "x"})
            raise AssertionError("应拒绝不存在的问题")
        except KeyError as e:
            print(f"  ✓ 拒绝不存在的问题: {e}")
        print("  ✓ 精修应用反馈、重验证、持久化、状态流转")

        # ── [9/14] 证据链接 ──
        print("\n[9/14] 证据链接...")
        evidence_qid = framework["main_questions"][0]  # 立项依据（theoretical）
        evidence = architect.get_question_evidence(evidence_qid)
        print(f"  缺口: {evidence['gaps']}")
        print(f"  文献: {evidence['literature']}")
        print(f"  方法: {evidence['methods']}")
        print(f"  缺口详情数: {len(evidence['gap_details'])}")
        # 立项依据是 theoretical 类型 → 应链接 gap_003（theoretical）
        assert "gap_003" in evidence["gaps"], "theoretical 问题应链接 theoretical 缺口"
        # 缺口详情应可解析
        for gd in evidence["gap_details"]:
            assert "gap_id" in gd
            assert "type" in gd
        # 方法来自 topic
        assert "TDDFT" in evidence["methods"]
        assert "SBE" in evidence["methods"]
        # 文献来自 topic
        assert "ref_001" in evidence["literature"]
        # 不存在问题返回空
        empty_ev = architect.get_question_evidence("q_nonexist")
        assert empty_ev == {"gaps": [], "literature": [], "methods": [], "gap_details": []}
        print("  ✓ 证据链接按类型匹配，缺口详情可解析")

        # ── [10/14] Markdown 导出 ──
        print("\n[10/14] Markdown 导出...")
        md = architect.export_framework("markdown")
        assert "# 科学问题框架" in md
        assert "## 验证摘要" in md
        assert "## 按要素分布" in md
        assert "立项依据" in md
        assert "科学问题" in md
        assert "研究内容" in md
        assert "研究方案" in md
        assert "特色与创新" in md
        assert "综合分" in md
        print(f"  Markdown 长度: {len(md)} 字符")
        # 打印前 8 行预览
        for line in md.splitlines()[:8]:
            print(f"    {line}")
        print("  ✓ Markdown 含五要素、验证摘要、综合分")

        # ── [11/14] JSON 导出 ──
        print("\n[11/14] JSON 导出...")
        json_str = architect.export_framework("json")
        parsed = json.loads(json_str)
        assert "framework_id" in parsed
        assert "elements" in parsed
        assert "all_questions" in parsed
        assert "validation_summary" in parsed
        assert parsed["framework_id"] == framework["framework_id"]
        assert len(parsed["all_questions"]) == len(framework["all_questions"])
        # 验证 ensure_ascii=False（中文不转义）
        assert "立项依据" in json_str, "JSON 应保留中文（ensure_ascii=False）"
        print(f"  JSON 长度: {len(json_str)} 字符")
        print(f"  解析后 framework_id: {parsed['framework_id']}")
        print("  ✓ JSON 可解析，中文不转义，结构与框架一致")

        # ── [12/14] 空课题处理 ──
        print("\n[12/14] 空课题处理...")
        empty_proposal = tmp / "empty_proposal"
        empty_arch = QuestionArchitect(empty_proposal)
        empty_fw = empty_arch.construct_questions({})
        assert empty_fw["framework_id"].startswith("fw_")
        assert empty_fw["topic_title"] == "未命名课题"
        assert len(empty_fw["main_questions"]) == 5, "空课题仍应生成 5 个主问题"
        # 每个主问题文本不应包含未填充占位符
        for qid in empty_fw["main_questions"]:
            q = empty_fw["all_questions"][qid]
            assert "{" not in q["text"], f"空课题问题 {qid} 不应含占位符: {q['text']}"
        print(f"  空课题 framework_id: {empty_fw['framework_id']}")
        print(f"  空课题主问题示例: {empty_fw['all_questions'][empty_fw['main_questions'][0]]['text']}")
        print("  ✓ 空课题优雅降级，使用默认占位符")

        # ── [13/14] 原子写入 + 文件锁 ──
        print("\n[13/14] 原子写入 + 文件锁...")
        # 验证文件是有效 JSON（原子写入不会产生半写状态）
        raw_content = architect.framework_path.read_text(encoding="utf-8")
        parsed_raw = json.loads(raw_content)
        assert parsed_raw["framework_id"] == framework["framework_id"]
        # 不同 proposal 应有不同锁名
        arch_other = QuestionArchitect(tmp / "another_proposal")
        assert arch_other._lock_name != architect._lock_name, (
            "不同 proposal 应有不同锁名"
        )
        print(f"  锁名1: {architect._lock_name}")
        print(f"  锁名2: {arch_other._lock_name}")
        # 多次写入不损坏
        fw_again = architect.construct_questions(topic, gap_report=gap_report)
        raw_again = architect.framework_path.read_text(encoding="utf-8")
        parsed_again = json.loads(raw_again)
        assert parsed_again["framework_id"] == fw_again["framework_id"]
        # 确保文件锁可重入不阻塞（同 proposal 顺序写）
        arch_seq = QuestionArchitect(proposal_dir)
        seq_fw = arch_seq.get_framework()
        assert seq_fw["framework_id"] == fw_again["framework_id"]
        print("  ✓ 原子写入有效，锁按 proposal 隔离，多次写入不损坏")

        # ── [14/14] 持久化往返 ──
        print("\n[14/14] 持久化往返...")
        # 全新实例加载
        arch_final = QuestionArchitect(proposal_dir)
        final_fw = arch_final.get_framework()
        assert final_fw["framework_id"] == fw_again["framework_id"]
        assert final_fw["topic_id"] == fw_again["topic_id"]
        assert len(final_fw["all_questions"]) == len(fw_again["all_questions"])
        # 每个问题字段完整
        for qid, q in final_fw["all_questions"].items():
            assert "question_id" in q
            assert "level" in q
            assert "text" in q
            assert "type" in q
            assert "element" in q
            assert "validation" in q
            assert "status" in q
            assert q["validation"].get("overall") is not None
        # 占位符已恢复
        assert arch_final._last_placeholders.get("concept") == "量子度规"
        # 之前精修的问题在重新加载后仍然保留
        refined_qid = fw_again["main_questions"][1]  # 注意：第二次 construct 后 ID 可能不同
        # 第二次 construct_questions 会生成新框架（fw_002），main_questions[1] 是新的
        # 所以这里验证的是当前框架的问题状态
        cur_q1 = arch_final.get_question(fw_again["main_questions"][1])
        assert cur_q1 is not None
        assert cur_q1["level"] == 0
        print(f"  最终 framework_id: {final_fw['framework_id']}")
        print(f"  最终问题数: {len(final_fw['all_questions'])}")
        print(f"  占位符 concept: {arch_final._last_placeholders.get('concept')}")
        print("  ✓ 持久化往返一致，字段完整，占位符恢复")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print("\n(已清理临时目录)")

    print("\n" + "=" * 50)
    print("✓ question_architect 自检全部通过（14/14）")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="科学问题架构师")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
