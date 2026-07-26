#!/usr/bin/env python3
"""研究课题生成器 — 课题凝练阶段的核心模块。

用途：
    从缺口分析结果（gap_analyzer 产出）生成候选研究课题，结合用户学术品味模型
    进行过滤与排序，产出优先级课题列表，为后续申请书撰写提供输入。

    位于研究管线"课题凝练"阶段：
        ... → 01_review（文献调研） → 02_topic（课题凝练） → 03_design ...
    本模块的产物 topics.json 保存在 {proposal_dir}/02_topic/ 下。

核心流程：
    1. generate_topics()   从缺口报告生成候选课题（缺口 → 研究问题 → 课题）
    2. score_topic()       用品味引擎相似度 + 启发式规则评分
    3. rank_topics()       按总分降序排列
    4. select_topic()      选定课题进入下一阶段
    5. refine_topic()      根据用户反馈精炼课题
    6. evolve_topics()     新缺口出现时演化课题列表（合并/新增/丢弃）

课题评分公式：
    total = 0.35 * taste_score + 0.25 * novelty_score
          + 0.20 * feasibility_score + 0.20 * direction_alignment
    （各分项 0-1，total 越高越优先）

课题生成算法（v1 规则驱动，无 LLM）：
    - 每个 gap 生成 1-2 个候选课题（概念/理论缺口生成 2 个，方法/实验缺口生成 1 个）
    - 课题标题模板："{concept}在{direction}中的调制机制研究" 等
    - novelty_score / feasibility_score 继承自缺口
    - taste_score 由 TasteEngine.get_similarity_score() 计算
    - direction_alignment 统计课题文本覆盖的方向维度比例

用法示例：
    >>> from pathlib import Path
    >>> from topic_generator import TopicGenerator
    >>> from gap_analyzer import GapAnalyzer
    >>> generator = TopicGenerator(Path("/data/proposals/T1"))
    >>> analyzer = GapAnalyzer(Path("/data/proposals/T1"), research_directions=directions)
    >>> gap_report = analyzer.analyze()
    >>> topics = generator.generate_topics(gap_report,
    ...                                    direction={"id": "T1", "name": "量子几何"})
    >>> selected = generator.select_topic(topics[0]["topic_id"])
    >>> md = generator.export_topics("markdown")

命令行自检：
    python3 scripts/topic_generator.py --self-check

规范：仅 Python 标准库，pathlib.Path 路径处理，JSON ensure_ascii=False，时间戳 UTC ISO。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock, lazy_load

# 从 gap_analyzer 导入方向维度定义与缺口类型标签
from gap_analyzer import DIRECTION_DIMENSIONS, GAP_TYPE_LABELS

# v6.3.2 接入 LLM 网关（共享基础设施层），让选题具备"大脑"
try:
    from llm_gateway import is_llm_available, safe_llm_complete, llm_json
    _LLM_OK = is_llm_available()
except Exception:
    _LLM_OK = False
    def safe_llm_complete(*a, **kw):  # type: ignore
        return kw.get("fallback", "")
    def llm_json(*a, **kw):  # type: ignore
        return False, None, {}

__all__ = [
    "TopicGenerator",
    "TOPIC_STATUS",
    "TOPIC_STATUS_LABELS",
    "SCORE_WEIGHTS",
    "TITLE_TEMPLATES",
]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 课题状态机
# candidate → selected / refined → dropped
TOPIC_STATUS = ("candidate", "selected", "refined", "dropped")

TOPIC_STATUS_LABELS: Dict[str, str] = {
    "candidate": "候选",
    "selected": "已选定",
    "refined": "已精炼",
    "dropped": "已丢弃",
}

# 评分权重
SCORE_WEIGHTS: Dict[str, float] = {
    "taste": 0.35,        # 品味匹配度
    "novelty": 0.25,      # 新颖性
    "feasibility": 0.20,  # 可行性
    "direction": 0.20,    # 方向对齐度
}

# 课题标题模板（按缺口类型分类，每类提供 1-2 个模板）
TITLE_TEMPLATES: Dict[str, List[str]] = {
    "conceptual": [
        "{concept}在{direction}中的调制机制研究",
        "{concept}的物理内涵与实验探测研究",
    ],
    "methodological": [
        "{concept}在{direction}中的应用可行性研究",
        "基于{concept}的{direction}方法研究",
    ],
    "theoretical": [
        "基于{concept}的{direction}理论框架研究",
        "{concept}用于{direction}的理论分析研究",
    ],
    "empirical": [
        "{direction}方向的实验验证与数据支撑研究",
        "{concept}的实证基础研究",
    ],
}

# 不同缺口类型对应的方法论特征向量 [理论, 实验, 计算]
_METHODOLOGY_PROFILES: Dict[str, List[float]] = {
    "conceptual": [0.8, 0.5, 0.5],
    "methodological": [0.6, 0.4, 0.8],
    "theoretical": [0.9, 0.3, 0.6],
    "empirical": [0.4, 0.9, 0.4],
}

# 不同缺口类型对应的理论深度
_THEORETICAL_DEPTH_PROFILES: Dict[str, float] = {
    "conceptual": 0.8,
    "methodological": 0.6,
    "theoretical": 0.9,
    "empirical": 0.4,
}


# ---------------------------------------------------------------------------
# TopicGenerator 类
# ---------------------------------------------------------------------------

class TopicGenerator:
    """研究课题生成器。

    从缺口分析结果生成候选研究课题，用品味引擎过滤排序，
    产出优先级课题列表，支持课题演化与精炼。

    线程安全：所有写操作通过 common.file_lock（fcntl.flock 跨进程锁）保护
    read-modify-write 临界区，锁键基于 proposal_dir 路径哈希，不同 proposal 互不阻塞。
    """

    def __init__(
        self,
        proposal_dir: Path | str,
        taste_engine: Optional[Any] = None,
    ) -> None:
        """初始化课题生成器。

        Args:
            proposal_dir: proposal 根目录（Path 或字符串），
                          课题文件保存于其下的 02_topic/topics.json。
            taste_engine: TasteEngine 实例；为 None 时懒加载默认引擎。
        """
        self.proposal_dir = Path(proposal_dir)
        self.topic_dir = self.proposal_dir / "02_topic"
        self.topics_path = self.topic_dir / "topics.json"
        self._taste_engine = taste_engine

        # 跨进程锁键：基于 proposal_dir 绝对路径哈希，避免不同 proposal 互相阻塞
        digest = hashlib.md5(
            str(self.proposal_dir.resolve()).encode("utf-8")
        ).hexdigest()[:12]
        self._lock_name = f"topics-{digest}"

        # 确保目录结构存在
        self.topic_dir.mkdir(parents=True, exist_ok=True)

        # 懒加载的模块缓存（None = 尚未加载）
        self._artifact_manager_mod = None
        self._lineage_tracker_mod = None

    # ------------------------------------------------------------------
    # 模块懒加载
    # ------------------------------------------------------------------

    def _get_taste_engine(self) -> Optional[Any]:
        """获取品味引擎实例（懒加载）。

        构造函数传入的实例优先；否则尝试懒加载 taste_engine 模块。
        加载失败返回 None，调用方需处理 None 情况。
        """
        if self._taste_engine is None:
            mod = lazy_load("taste_engine")
            if mod is not None:
                try:
                    self._taste_engine = mod.TasteEngine()
                except Exception:
                    self._taste_engine = None
        return self._taste_engine

    def _load_lineage_tracker(self):
        """懒加载 lineage_tracker 模块，返回模块对象或 None。"""
        if self._lineage_tracker_mod is None:
            self._lineage_tracker_mod = lazy_load("lineage_tracker")
        return self._lineage_tracker_mod

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------

    def _load_topics(self) -> Dict[str, Any]:
        """加载 topics.json（纯读，不加锁）。

        Returns:
            课题存储字典，结构：
            {"topics": {topic_id: {...}}, "next_seq": int, "updated_at": str}
        """
        data = load_json(self.topics_path, default=None)
        if not isinstance(data, dict) or "topics" not in data:
            return {"topics": {}, "next_seq": 1, "updated_at": now_utc()}
        if not isinstance(data["topics"], dict):
            data["topics"] = {}
        if "next_seq" not in data or not isinstance(data["next_seq"], int):
            data["next_seq"] = len(data["topics"]) + 1
        return data

    def _save_topics(self, data: Dict[str, Any]) -> None:
        """保存 topics.json（原子写入，应在锁内调用）。"""
        data["updated_at"] = now_utc()
        save_json(self.topics_path, data)

    # ------------------------------------------------------------------
    # 课题生成（规则驱动）
    # ------------------------------------------------------------------

    def generate_topics(
        self,
        gap_report: Dict[str, Any],
        direction: Optional[Dict[str, Any]] = None,
        max_topics: int = 10,
    ) -> List[Dict[str, Any]]:
        """从缺口报告生成候选课题。

        流程：
          1. 提取缺口列表，按方向过滤（可选）
          2. 每个 gap 生成 1-2 个候选课题
          3. 对每个课题评分（品味引擎 + 启发式规则）
          4. 按总分排序，取前 max_topics 个
          5. 分配 topic_id 并持久化
          6. 注册课题 → 缺口血缘关系

        Args:
            gap_report: gap_analyzer.analyze() 返回的缺口报告。
            direction: 研究方向 {"id": "T1", "name": "量子几何"}；
                       为 None 时使用缺口自身的 related_direction。
            max_topics: 最多生成的课题数。

        Returns:
            生成的课题列表（按总分降序），每个课题含完整字段。
        """
        gaps: List[Dict[str, Any]] = gap_report.get("gaps", [])
        if not gaps:
            return []

        # 按方向过滤缺口（保留直接关联 + 通用缺口）
        if direction:
            dir_id = direction.get("id", "")
            gaps = [
                g for g in gaps
                if g.get("related_direction") == dir_id
                or not g.get("related_direction")
            ]

        # 生成候选课题
        candidates: List[Dict[str, Any]] = []
        for gap in gaps:
            candidates.extend(self._gap_to_topics(gap, direction))

        if not candidates:
            return []

        # 评分
        scored = [self.score_topic(t) for t in candidates]

        # 排序并截断
        ranked = self.rank_topics(scored)[:max_topics]

        # 分配 ID 并持久化
        with file_lock(self._lock_name):
            data = self._load_topics()
            for t in ranked:
                seq = data["next_seq"]
                t["topic_id"] = f"topic_{seq:03d}"
                data["next_seq"] = seq + 1
                data["topics"][t["topic_id"]] = t
            self._save_topics(data)

        # 注册血缘
        self._register_lineage(ranked)

        return ranked

    def _llm_enrich_topic(
        self,
        gap: Dict[str, Any],
        concept: str,
        direction_name: str,
        template_title: str,
        template_rq: str,
    ) -> Dict[str, str]:
        """v6.3.2 用 LLM 生成更具学术价值的课题标题与研究问题。

        Returns:
            {"title": ..., "research_question": ...}，失败时回退模板。
        """
        if not _LLM_OK:
            return {"title": template_title, "research_question": template_rq}

        gap_desc = gap.get("description", "")
        gap_type = gap.get("type", "conceptual")
        dir_label = direction_name or "强场超快光学"

        sys_prompt = (
            "你是强场超快光学/阿秒科学/固体高次谐波领域的资深 PI，"
            "擅长从研究缺口中凝练出科学价值高、可行性强、新颖度好的课题。"
            "你熟悉 NSFC 面上项目课题标题的表述规范。"
        )
        user_prompt = (
            f"请基于以下研究缺口，优化课题标题与研究问题。\n\n"
            f"【缺口类型】{gap_type}\n"
            f"【缺口描述】{gap_desc}\n"
            f"【关键概念】{concept}\n"
            f"【研究方向】{dir_label}\n"
            f"【模板标题】{template_title}\n"
            f"【模板研究问题】{template_rq}\n\n"
            f"要求：\n"
            f"1. 标题要体现\"现象+机制+方法\"，避免泛化\n"
            f"2. 研究问题要具体、可检验\n"
            f"3. 输出严格 JSON：{{\"title\": \"...\", \"research_question\": \"...\"}}\n"
            f"4. 只输出 JSON"
        )

        try:
            ok, data, _ = llm_json(sys_prompt, user_prompt, timeout=90)
            if ok and isinstance(data, dict):
                title = data.get("title", "")
                rq = data.get("research_question", "")
                if isinstance(title, str) and title.strip() and len(title) <= 80:
                    if isinstance(rq, str) and rq.strip():
                        return {"title": title.strip(), "research_question": rq.strip()}
        except Exception:
            pass
        return {"title": template_title, "research_question": template_rq}

    def _gap_to_topics(
        self,
        gap: Dict[str, Any],
        direction: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """从单个缺口生成 1-2 个候选课题。

        概念/理论缺口生成 2 个（不同视角），方法/实验缺口生成 1 个。
        """
        topics: List[Dict[str, Any]] = []
        gap_type = gap.get("type", "conceptual")
        gap_id = gap.get("gap_id", "")
        gap_desc = gap.get("description", "")
        gap_type_label = GAP_TYPE_LABELS.get(gap_type, gap_type)

        # 提取关键概念/方法名称
        concept = self._extract_key_concept(gap)

        # 确定研究方向
        dir_id = ""
        dir_name = ""
        if direction:
            dir_id = direction.get("id", "")
            dir_name = direction.get("name", "")
        elif gap.get("related_direction"):
            dir_id = gap["related_direction"]
            dir_name = DIRECTION_DIMENSIONS.get(dir_id, {}).get("name", dir_id)

        # 生成主课题
        title1 = self._generate_title(gap_type, concept, dir_name, 0)
        rq1 = self._generate_research_question(gap_type, concept, dir_name, 0)
        # v6.3.2 LLM 增强课题标题与研究问题
        enriched1 = self._llm_enrich_topic(gap, concept, dir_name, title1, rq1)
        title1, rq1 = enriched1["title"], enriched1["research_question"]
        alignment1 = self._compute_direction_alignment(
            gap, direction, title1, rq1)
        topic1: Dict[str, Any] = {
            "topic_id": "",  # 由 generate_topics 分配
            "title": title1,
            "title_en": "",  # v1 暂不生成英文标题
            "direction": dir_id,
            "gap_ids": [gap_id],
            "gap_types": [gap_type],
            "research_question": rq1,
            "novelty_score": float(gap.get("novelty_score", 0.5)),
            "feasibility_score": float(gap.get("feasibility_score", 0.5)),
            "taste_score": 0.0,  # 由 score_topic 填充
            "direction_alignment": alignment1,
            "total_score": 0.0,  # 由 score_topic 填充
            "status": "candidate",
            "rationale": f"基于{gap_id}的{gap_type_label}：{gap_desc}",
            "key_references": [],
            "created_at": now_utc(),
            "updated_at": now_utc(),
            "refinement_history": [],
        }
        topics.append(topic1)

        # 概念/理论缺口生成备选课题（不同视角）
        if gap_type in ("conceptual", "theoretical"):
            title2 = self._generate_title(gap_type, concept, dir_name, 1)
            rq2 = self._generate_research_question(gap_type, concept, dir_name, 1)
            # v6.3.2 LLM 增强备选课题
            enriched2 = self._llm_enrich_topic(gap, concept, dir_name, title2, rq2)
            title2, rq2 = enriched2["title"], enriched2["research_question"]
            alignment2 = self._compute_direction_alignment(
                gap, direction, title2, rq2)
            topic2 = dict(topic1)
            topic2["title"] = title2
            topic2["research_question"] = rq2
            topic2["direction_alignment"] = alignment2
            topic2["rationale"] = (
                f"基于{gap_id}的{gap_type_label}（备选视角）：{gap_desc}"
            )
            topics.append(topic2)

        return topics

    def _extract_key_concept(self, gap: Dict[str, Any]) -> str:
        """从缺口信息中提取关键概念/方法名称。

        解析策略（按优先级）：
          1. 描述中冒号后的内容（如 "...关键维度：量子度规"）
          2. 描述中引号内的内容（如 "方法'神经网络反演'..."）
          3. 建议路径中去掉动词前缀后的内容
          4. 基于缺口类型的回退值
        """
        desc = gap.get("description", "")
        suggested = gap.get("suggested_approach", "")
        gap_type = gap.get("type", "")

        # 策略 1：冒号后的内容
        for sep in ["：", ":"]:
            if sep in desc:
                parts = desc.split(sep, 1)
                if len(parts) > 1:
                    concept = parts[1].strip().rstrip("。.，,")
                    if concept and 1 < len(concept) < 50:
                        return concept

        # 策略 2：引号内的内容
        for open_q, close_q in [("'", "'"), ('"', '"'), ("「", "」"), ("『", "』")]:
            if open_q in desc:
                start = desc.find(open_q)
                end = desc.find(close_q, start + 1)
                if end > start:
                    concept = desc[start + 1:end].strip()
                    if concept:
                        return concept

        # 策略 3：建议路径中去掉动词前缀
        if suggested:
            cleaned = suggested
            for verb in ["系统梳理", "深化对", "引入", "建立", "从"]:
                if cleaned.startswith(verb):
                    rest = cleaned[len(verb):]
                    for delim in ["在", "的", "用于", "，", ","]:
                        if delim in rest:
                            concept = rest.split(delim, 1)[0].strip()
                            if concept:
                                return concept
                    return rest.strip().rstrip("。.")

        # 策略 4：回退
        fallbacks = {
            "conceptual": "关键概念",
            "methodological": "新兴方法",
            "theoretical": "理论方法",
            "empirical": "实证基础",
        }
        return fallbacks.get(gap_type, "研究课题")

    def _generate_title(
        self,
        gap_type: str,
        concept: str,
        direction_name: str,
        template_idx: int = 0,
    ) -> str:
        """根据缺口类型和模板生成课题标题。"""
        templates = TITLE_TEMPLATES.get(gap_type, TITLE_TEMPLATES["conceptual"])
        idx = min(template_idx, len(templates) - 1)
        template = templates[idx]
        dir_label = direction_name or "强场超快光学"
        return template.format(concept=concept, direction=dir_label)

    def _generate_research_question(
        self,
        gap_type: str,
        concept: str,
        direction_name: str,
        variant: int = 0,
    ) -> str:
        """根据缺口类型生成研究问题。"""
        dir_label = direction_name or "相关体系"
        if gap_type == "conceptual":
            if variant == 0:
                return f"{concept}如何影响{dir_label}中的物理过程与可观测量？"
            return f"{concept}的关键参数如何调控{dir_label}体系的实验信号？"
        elif gap_type == "methodological":
            if variant == 0:
                return f"{concept}能否有效描述{dir_label}中的超快动力学过程？"
            return f"如何将{concept}应用于{dir_label}以提高分析精度？"
        elif gap_type == "theoretical":
            if variant == 0:
                return f"如何用{concept}系统描述{dir_label}的核心物理现象？"
            return f"{concept}在{dir_label}中的适用范围与局限性是什么？"
        else:  # empirical
            return f"{dir_label}方向有哪些关键实验数据缺口需要填补？"

    def _compute_direction_alignment(
        self,
        gap: Dict[str, Any],
        direction: Optional[Dict[str, Any]],
        title: str,
        research_question: str,
    ) -> float:
        """计算课题与研究方向的对齐度。

        - 无方向时：继承 gap 的 direction_alignment
        - 有方向时：统计课题文本覆盖的方向维度比例
          - 直接关联（gap.related_direction == direction.id）：
            基础 0.7 + 覆盖率 * 0.3（上限 1.0）
          - 非直接关联：取 base 和 coverage 的较大值
        """
        base = float(gap.get("direction_alignment", 0.5))
        if direction is None:
            return round(base, 4)

        dir_id = direction.get("id", "")
        dir_dims = DIRECTION_DIMENSIONS.get(dir_id, {}).get("dimensions", [])
        total_dims = len(dir_dims)
        if total_dims == 0:
            return round(base, 4)

        # 统计课题文本覆盖的方向维度数
        text = (title + " " + research_question).lower()
        addressed = 0
        for dim in dir_dims:
            for kw in dim["keywords"]:
                if kw.lower() in text:
                    addressed += 1
                    break
        # 至少覆盖 1 个维度（缺口自身的维度）
        addressed = max(1, addressed)
        coverage = addressed / total_dims

        if gap.get("related_direction") == dir_id:
            # 直接关联：基础 0.7 + 覆盖率 * 0.3
            return round(min(1.0, 0.7 + 0.3 * coverage), 4)
        # 非直接关联：取 base 和 coverage 的较大值
        return round(min(1.0, max(base, coverage)), 4)

    # ------------------------------------------------------------------
    # 课题评分
    # ------------------------------------------------------------------

    def _topic_to_features(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """将课题转换为品味引擎特征字典。

        将课题的缺口类型映射为五维品味特征：
          - novelty: 课题新颖性
          - methodology: [理论, 实验, 计算] 三维向量
            （对应 requirement 中的 methodology_theory/experiment/computation）
          - theoretical_depth: 理论深度
          - interdisciplinarity: 跨学科性
          - risk_appetite: 风险偏好（与新颖性正相关）
        """
        gap_types = topic.get("gap_types", [])
        primary_type = gap_types[0] if gap_types else "conceptual"

        novelty = float(topic.get("novelty_score", 0.5))

        # 方法论三维向量 [理论, 实验, 计算]
        methodology = _METHODOLOGY_PROFILES.get(primary_type, [0.5, 0.5, 0.5])

        # 理论深度
        theoretical_depth = _THEORETICAL_DEPTH_PROFILES.get(primary_type, 0.5)

        # 跨学科性：有明确方向的课题偏专注（0.4），无方向偏跨界（0.6）
        interdisciplinarity = 0.4 if topic.get("direction") else 0.6

        # 风险偏好：与新颖性正相关（0.3-0.8）
        risk_appetite = round(0.3 + 0.5 * novelty, 4)

        return {
            "novelty": novelty,
            "methodology": methodology,
            "theoretical_depth": theoretical_depth,
            "interdisciplinarity": interdisciplinarity,
            "risk_appetite": risk_appetite,
        }

    def score_topic(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """评分单个课题。

        评分公式：
            total = 0.35 * taste_score + 0.25 * novelty_score
                  + 0.20 * feasibility_score + 0.20 * direction_alignment

        Args:
            topic: 课题字典（需含 novelty_score / feasibility_score / direction_alignment）。

        Returns:
            带有 taste_score / total_score 的课题字典（原地修改并返回）。
        """
        # 构建品味特征
        features = self._topic_to_features(topic)

        # 品味匹配度（来自 TasteEngine）
        engine = self._get_taste_engine()
        if engine is not None:
            try:
                taste_score = float(engine.get_similarity_score(features))
            except Exception:
                taste_score = 0.5
        else:
            taste_score = 0.5

        # 方向对齐度（已在生成时计算，此处取值）
        direction_alignment = float(topic.get("direction_alignment", 0.5))

        # 总分
        total = (
            SCORE_WEIGHTS["taste"] * taste_score
            + SCORE_WEIGHTS["novelty"] * float(topic.get("novelty_score", 0.5))
            + SCORE_WEIGHTS["feasibility"] * float(topic.get("feasibility_score", 0.5))
            + SCORE_WEIGHTS["direction"] * direction_alignment
        )

        topic["taste_score"] = round(taste_score, 4)
        topic["direction_alignment"] = round(direction_alignment, 4)
        topic["total_score"] = round(total, 4)
        return topic

    def rank_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按总分降序排列课题。

        Args:
            topics: 课题列表。

        Returns:
            排序后的课题列表（新列表，不修改原列表）。
        """
        return sorted(
            topics,
            key=lambda t: t.get("total_score", 0.0),
            reverse=True,
        )

    # ------------------------------------------------------------------
    # 课题检索与管理
    # ------------------------------------------------------------------

    def get_topics(self) -> List[Dict[str, Any]]:
        """获取所有课题（按总分降序排列）。"""
        data = self._load_topics()
        topics = list(data["topics"].values())
        topics.sort(key=lambda t: t.get("total_score", 0.0), reverse=True)
        return topics

    def get_topic(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """获取单个课题；不存在返回 None。"""
        data = self._load_topics()
        topic = data["topics"].get(topic_id)
        return dict(topic) if topic else None

    def select_topic(self, topic_id: str) -> Dict[str, Any]:
        """标记课题为已选定（进入下一阶段）。

        Args:
            topic_id: 课题 ID。

        Returns:
            更新后的课题字典。

        Raises:
            KeyError: 课题不存在。
        """
        with file_lock(self._lock_name):
            data = self._load_topics()
            topics = data["topics"]
            if topic_id not in topics:
                raise KeyError(f"课题不存在: {topic_id}")
            topic = topics[topic_id]
            topic["status"] = "selected"
            topic["updated_at"] = now_utc()
            topic.setdefault("refinement_history", []).append({
                "action": "selected",
                "timestamp": now_utc(),
            })
            self._save_topics(data)
            return dict(topic)

    def refine_topic(
        self,
        topic_id: str,
        feedback: Dict[str, Any],
    ) -> Dict[str, Any]:
        """根据用户反馈精炼课题。

        支持的反馈字段：
          - title / title_en / research_question / rationale: 文本更新
          - novelty_score / feasibility_score: 分数调整
          - status: 状态变更（默认置为 refined）

        Args:
            topic_id: 课题 ID。
            feedback: 反馈字典。

        Returns:
            精炼后的课题字典。

        Raises:
            KeyError: 课题不存在。
        """
        with file_lock(self._lock_name):
            data = self._load_topics()
            topics = data["topics"]
            if topic_id not in topics:
                raise KeyError(f"课题不存在: {topic_id}")
            topic = topics[topic_id]

            # 记录精炼历史
            history_entry: Dict[str, Any] = {
                "action": "refined",
                "feedback": dict(feedback),
                "timestamp": now_utc(),
                "previous_status": topic.get("status", "candidate"),
            }
            topic.setdefault("refinement_history", []).append(history_entry)

            # 应用文本更新
            for field in ("title", "title_en", "research_question", "rationale"):
                if field in feedback:
                    topic[field] = feedback[field]

            # 应用分数调整
            for field in ("novelty_score", "feasibility_score"):
                if field in feedback:
                    topic[field] = float(feedback[field])

            # 状态变更
            new_status = feedback.get("status")
            if new_status and new_status in TOPIC_STATUS:
                topic["status"] = new_status
            else:
                topic["status"] = "refined"

            # 重新评分
            self.score_topic(topic)
            topic["updated_at"] = now_utc()

            self._save_topics(data)
            return dict(topic)

    # ------------------------------------------------------------------
    # 课题演化
    # ------------------------------------------------------------------

    def evolve_topics(self, new_gap_report: Dict[str, Any]) -> Dict[str, Any]:
        """当发现新缺口时演化课题列表。

        策略：
          - merge: 新缺口与已有课题同方向同类型 → 关联新 gap_id 到已有课题
          - update: 新缺口无法合并 → 生成新课题并添加
          - drop: 已有课题的 gap 全部不在新报告中 → 标记为 dropped

        Args:
            new_gap_report: 新的缺口报告。

        Returns:
            演化摘要 {"merged": int, "added": int, "dropped": int, "topics": [...]}
        """
        new_gaps: List[Dict[str, Any]] = new_gap_report.get("gaps", [])
        new_gap_ids = {g.get("gap_id") for g in new_gaps}

        with file_lock(self._lock_name):
            data = self._load_topics()
            topics: Dict[str, Any] = data["topics"]

            merged_count = 0
            dropped_count = 0

            # 1. 检查已有课题：gap 全不在新报告中 → 丢弃
            for tid, topic in topics.items():
                if topic.get("status") == "dropped":
                    continue
                topic_gap_ids = set(topic.get("gap_ids", []))
                if topic_gap_ids and not topic_gap_ids & new_gap_ids:
                    topic["status"] = "dropped"
                    topic["updated_at"] = now_utc()
                    topic.setdefault("refinement_history", []).append({
                        "action": "dropped",
                        "reason": "关联缺口已不在最新报告中",
                        "timestamp": now_utc(),
                    })
                    dropped_count += 1

            # 2. 统计已被课题覆盖的 gap_id
            covered_gap_ids: set = set()
            for topic in topics.values():
                covered_gap_ids.update(topic.get("gap_ids", []))

            # 3. 处理新缺口：尝试合并或生成新课题
            added_topics: List[Dict[str, Any]] = []
            for gap in new_gaps:
                gap_id = gap.get("gap_id", "")
                if gap_id in covered_gap_ids:
                    continue  # 已被覆盖

                # 尝试合并到已有课题（同方向 + 同类型）
                merged = False
                gap_dir = gap.get("related_direction", "")
                gap_type = gap.get("type", "")
                for tid, topic in topics.items():
                    if topic.get("status") == "dropped":
                        continue
                    topic_dir = topic.get("direction", "")
                    topic_types = topic.get("gap_types", [])
                    # 同方向 + 同类型 → 合并
                    if (topic_dir and topic_dir == gap_dir
                            and topic_types and topic_types[0] == gap_type):
                        if gap_id not in topic.get("gap_ids", []):
                            topic["gap_ids"].append(gap_id)
                            topic["gap_types"].append(gap_type)
                            topic["updated_at"] = now_utc()
                            topic.setdefault("refinement_history", []).append({
                                "action": "merged",
                                "gap_id": gap_id,
                                "reason": "新缺口关联到已有课题",
                                "timestamp": now_utc(),
                            })
                            merged_count += 1
                            covered_gap_ids.add(gap_id)
                            merged = True
                            break

                # 无法合并 → 生成新课题
                if not merged:
                    new_candidates = self._gap_to_topics(gap, None)
                    for t in new_candidates:
                        self.score_topic(t)
                        seq = data["next_seq"]
                        t["topic_id"] = f"topic_{seq:03d}"
                        data["next_seq"] = seq + 1
                        topics[t["topic_id"]] = t
                        added_topics.append(t)
                        covered_gap_ids.update(t.get("gap_ids", []))

            self._save_topics(data)

        # 注册新课题血缘
        if added_topics:
            self._register_lineage(added_topics)

        return {
            "merged": merged_count,
            "added": len(added_topics),
            "dropped": dropped_count,
            "topics": added_topics,
        }

    # ------------------------------------------------------------------
    # 导出
    # ------------------------------------------------------------------

    def export_topics(self, format: str = "markdown") -> str:
        """导出课题列表为 Markdown 或 JSON 字符串。

        Args:
            format: "markdown" 或 "json"。

        Returns:
            格式化的课题列表字符串。
        """
        topics = self.get_topics()

        if format == "json":
            return json.dumps(
                {"topics": topics, "exported_at": now_utc()},
                ensure_ascii=False,
                indent=2,
            )

        # Markdown 格式
        lines: List[str] = ["# 研究课题列表\n"]
        lines.append(f"**导出时间**：{now_utc()}\n")
        lines.append(f"**课题总数**：{len(topics)}\n")

        if not topics:
            lines.append("（暂无课题，请先运行 generate_topics()）\n")
            return "\n".join(lines)

        # 摘要
        lines.append("## 摘要\n")
        status_counts: Dict[str, int] = {}
        for t in topics:
            s = t.get("status", "candidate")
            status_counts[s] = status_counts.get(s, 0) + 1
        for status in TOPIC_STATUS:
            count = status_counts.get(status, 0)
            if count > 0:
                lines.append(
                    f"- {TOPIC_STATUS_LABELS.get(status, status)}：{count} 个"
                )
        lines.append("")

        # 课题列表
        lines.append("## 课题列表\n")
        for i, topic in enumerate(topics, 1):
            lines.append(f"### {i}. {topic.get('title', '未命名')}\n")
            lines.append(f"- **课题ID**：{topic.get('topic_id', '')}")
            lines.append(
                f"- **研究方向**：{topic.get('direction', '未指定')}"
            )
            lines.append(
                f"- **研究问题**：{topic.get('research_question', '')}"
            )
            lines.append(
                f"- **状态**："
                f"{TOPIC_STATUS_LABELS.get(topic.get('status', ''), '')}"
            )
            lines.append(f"- **总分**：{topic.get('total_score', 0)}")
            lines.append(
                f"  - 品味匹配：{topic.get('taste_score', 0)}"
            )
            lines.append(
                f"  - 新颖性：{topic.get('novelty_score', 0)}"
            )
            lines.append(
                f"  - 可行性：{topic.get('feasibility_score', 0)}"
            )
            lines.append(
                f"  - 方向对齐：{topic.get('direction_alignment', 0)}"
            )
            if topic.get("gap_ids"):
                lines.append(
                    f"- **关联缺口**：{', '.join(topic['gap_ids'])}"
                )
            lines.append(
                f"- **理由**：{topic.get('rationale', '')}"
            )
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 血缘注册
    # ------------------------------------------------------------------

    def _register_lineage(self, topics: List[Dict[str, Any]]) -> None:
        """向血缘追踪器注册课题 → 缺口血缘关系（可选，失败不阻塞）。

        每个课题注册为 research_topic 类型节点（stage=2），
        并对每个关联缺口添加 derived_from 边。
        """
        tracker_mod = self._load_lineage_tracker()
        if tracker_mod is None:
            return
        try:
            tracker = tracker_mod.LineageTracker(self.proposal_dir)
            for topic in topics:
                topic_id = topic.get("topic_id", "")
                if not topic_id:
                    continue
                tracker.register_node(
                    topic_id,
                    "research_topic",
                    topic.get("title", topic_id),
                    stage=2,
                )
                for gap_id in topic.get("gap_ids", []):
                    tracker.add_edge(
                        topic_id,
                        gap_id,
                        "derived_from",
                        f"课题基于缺口{gap_id}生成",
                    )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """自检：13 个检查点，使用临时目录与 mock 数据隔离测试。

    覆盖：
      1.  初始化（创建空课题文件）
      2.  课题生成（验证数量、结构）
      3.  课题评分（验证公式、分数范围）
      4.  课题排序（验证降序）
      5.  课题检索（get_topics / get_topic）
      6.  课题选定（状态变更）
      7.  课题精炼（反馈应用、历史记录）
      8.  课题演化（合并/新增/丢弃）
      9.  Markdown 导出
      10. JSON 导出
      11. 空缺口报告处理
      12. 品味引擎集成（mock TasteEngine）
      13. 原子写入 + 文件锁
    """
    import shutil
    import tempfile

    print("=" * 50)
    print("◐ topic_generator 自检")
    print("=" * 50)

    tmp = Path(tempfile.mkdtemp(prefix="topic_generator_test_"))

    # ── 准备 mock 缺口报告 ──
    def make_gap_report() -> Dict[str, Any]:
        """构造测试用缺口报告。"""
        return {
            "proposal_dir": str(tmp / "proposal"),
            "generated_at": "2026-07-26T00:00:00Z",
            "coverage": {
                "concepts_covered": [],
                "concepts_missing": ["量子度规"],
                "methods_established": [],
                "methods_emerging": [],
                "papers_analyzed": 0,
            },
            "gaps": [
                {
                    "gap_id": "gap_001",
                    "type": "conceptual",
                    "description": "现有知识库未充分覆盖量子几何方向的关键维度：量子度规",
                    "evidence": [{"source": "知识库扫描", "note": "未找到量子度规概念页面"}],
                    "related_direction": "T1",
                    "priority_score": 0.84,
                    "novelty_score": 0.9,
                    "feasibility_score": 0.7,
                    "direction_alignment": 0.9,
                    "suggested_approach": "系统梳理量子度规在量子几何中的作用，建立 wiki 概念页面",
                },
                {
                    "gap_id": "gap_002",
                    "type": "methodological",
                    "description": "方法'神经网络反演'尚处于新兴阶段，成熟度不足",
                    "evidence": [{"source": "wiki 扫描", "note": "成熟度低"}],
                    "related_direction": "T5",
                    "priority_score": 0.57,
                    "novelty_score": 0.6,
                    "feasibility_score": 0.5,
                    "direction_alignment": 0.9,
                    "suggested_approach": "深化对神经网络反演的研究，补充理论推导与数值验证",
                },
                {
                    "gap_id": "gap_003",
                    "type": "empirical",
                    "description": "文献池为空，缺少实证基础",
                    "evidence": [{"source": "论文池扫描", "note": "无候选论文"}],
                    "related_direction": "",
                    "priority_score": 0.53,
                    "novelty_score": 0.4,
                    "feasibility_score": 0.8,
                    "direction_alignment": 0.4,
                    "suggested_approach": "从 arXiv 等来源导入研究方向相关的候选论文",
                },
            ],
            "summary": {
                "total_gaps": 3,
                "by_type": {"conceptual": 1, "methodological": 1, "empirical": 1},
                "by_direction": {"T1": 1, "T5": 1},
                "avg_priority": 0.6467,
            },
        }

    try:
        # ── [1/13] 初始化 ──
        print("\n[1/13] 初始化...")
        proposal_dir = tmp / "proposal_1"
        generator = TopicGenerator(proposal_dir)
        assert generator.proposal_dir == proposal_dir
        assert generator.topic_dir == proposal_dir / "02_topic"
        assert generator.topics_path == proposal_dir / "02_topic" / "topics.json"
        assert generator._lock_name.startswith("topics-")
        assert generator.topic_dir.exists(), "02_topic 目录应已创建"
        assert generator._taste_engine is None  # 懒加载，尚未初始化
        print(f"  proposal_dir: {generator.proposal_dir}")
        print(f"  topics_path: {generator.topics_path}")
        print(f"  lock_name: {generator._lock_name}")
        print("  ✓ 初始化字段完整，目录已创建")

        # ── [2/13] 课题生成 ──
        print("\n[2/13] 课题生成...")
        gap_report = make_gap_report()
        direction = {"id": "T1", "name": "量子几何"}
        topics = generator.generate_topics(
            gap_report, direction=direction, max_topics=10
        )
        print(f"  生成课题数: {len(topics)}")
        assert len(topics) > 0, "应生成至少 1 个课题"
        # gap_001(conceptual→2) + gap_003(empirical→1, 通用缺口保留) = 3
        # gap_002(T5) 被方向过滤排除
        assert len(topics) == 3, f"期望 3 个课题（T1+通用），实际 {len(topics)}"
        for t in topics:
            assert "topic_id" in t and t["topic_id"].startswith("topic_")
            assert "title" in t and len(t["title"]) > 0
            assert "research_question" in t
            assert "novelty_score" in t
            assert "feasibility_score" in t
            assert "taste_score" in t
            assert "total_score" in t
            assert "direction_alignment" in t
            assert "status" in t and t["status"] == "candidate"
            assert "gap_ids" in t and len(t["gap_ids"]) > 0
            assert "gap_types" in t and len(t["gap_types"]) > 0
            assert "rationale" in t
            assert "created_at" in t
            assert "updated_at" in t
            assert "refinement_history" in t
        print(f"  课题ID: {[t['topic_id'] for t in topics]}")
        print(f"  首个课题标题: {topics[0]['title']}")
        print("  ✓ 课题生成正确（数量、结构、字段完整）")

        # ── [3/13] 课题评分 ──
        print("\n[3/13] 课题评分...")
        for t in topics:
            # 验证公式
            expected = round(
                SCORE_WEIGHTS["taste"] * t["taste_score"]
                + SCORE_WEIGHTS["novelty"] * t["novelty_score"]
                + SCORE_WEIGHTS["feasibility"] * t["feasibility_score"]
                + SCORE_WEIGHTS["direction"] * t["direction_alignment"],
                4,
            )
            assert abs(t["total_score"] - expected) < 1e-4, (
                f"评分公式错误: topic={t['topic_id']} "
                f"expected={expected} actual={t['total_score']}"
            )
            # 验证分数范围
            for field in ("taste_score", "novelty_score", "feasibility_score",
                          "direction_alignment", "total_score"):
                val = t[field]
                assert 0.0 <= val <= 1.0, (
                    f"{field} 超出 [0,1]: {val} (topic={t['topic_id']})"
                )
        print(f"  首个课题总分: {topics[0]['total_score']}")
        print(f"  品味匹配: {topics[0]['taste_score']}")
        print(f"  方向对齐: {topics[0]['direction_alignment']}")
        print("  ✓ 评分公式正确，所有分数在 [0,1] 范围内")

        # ── [4/13] 课题排序 ──
        print("\n[4/13] 课题排序...")
        # 重新打乱后排序
        shuffled = list(reversed(topics))
        ranked = generator.rank_topics(shuffled)
        scores = [t["total_score"] for t in ranked]
        assert scores == sorted(scores, reverse=True), "应按总分降序排列"
        # get_topics 也应返回降序
        all_topics = generator.get_topics()
        all_scores = [t["total_score"] for t in all_topics]
        assert all_scores == sorted(all_scores, reverse=True), (
            "get_topics 应返回降序排列"
        )
        print(f"  排序后分数: {[round(s, 3) for s in all_scores]}")
        print("  ✓ 排序正确（降序）")

        # ── [5/13] 课题检索 ──
        print("\n[5/13] 课题检索...")
        first_id = topics[0]["topic_id"]
        topic = generator.get_topic(first_id)
        assert topic is not None
        assert topic["topic_id"] == first_id
        assert topic["title"] == topics[0]["title"]
        assert generator.get_topic("nonexistent") is None
        all_count = len(generator.get_topics())
        assert all_count == len(topics), (
            f"get_topics 应返回 {len(topics)} 个，实际 {all_count}"
        )
        print(f"  get_topic('{first_id}'): {topic['title'][:30]}...")
        print(f"  get_topic('nonexistent'): None")
        print(f"  get_topics(): {all_count} 个")
        print("  ✓ 检索正确（单个 + 全量 + 不存在）")

        # ── [6/13] 课题选定 ──
        print("\n[6/13] 课题选定...")
        select_id = topics[0]["topic_id"]
        selected = generator.select_topic(select_id)
        assert selected["status"] == "selected"
        assert selected["topic_id"] == select_id
        # 验证已持久化
        loaded = generator.get_topic(select_id)
        assert loaded is not None
        assert loaded["status"] == "selected"
        assert len(loaded.get("refinement_history", [])) >= 1
        hist = loaded["refinement_history"][-1]
        assert hist["action"] == "selected"
        print(f"  选定课题: {select_id}")
        print(f"  状态: {selected['status']}")
        print(f"  历史记录: {len(loaded['refinement_history'])} 条")
        print("  ✓ 选定状态变更 + 持久化 + 历史记录")

        # ── [7/13] 课题精炼 ──
        print("\n[7/13] 课题精炼...")
        refine_id = topics[1]["topic_id"] if len(topics) > 1 else topics[0]["topic_id"]
        old_novelty = generator.get_topic(refine_id)["novelty_score"]
        old_total = generator.get_topic(refine_id)["total_score"]
        refined = generator.refine_topic(refine_id, {
            "title": "精炼后的课题标题",
            "research_question": "精炼后的研究问题？",
            "novelty_score": 0.95,
        })
        assert refined["title"] == "精炼后的课题标题"
        assert refined["research_question"] == "精炼后的研究问题？"
        assert refined["novelty_score"] == 0.95
        assert refined["status"] == "refined"
        assert len(refined["refinement_history"]) >= 1
        hist = refined["refinement_history"][-1]
        assert hist["action"] == "refined"
        assert hist["previous_status"] == "candidate"
        # 总分应因 novelty 变化而重新计算
        assert refined["total_score"] != old_total or old_novelty == 0.95
        # 验证持久化
        loaded = generator.get_topic(refine_id)
        assert loaded["title"] == "精炼后的课题标题"
        assert loaded["status"] == "refined"
        print(f"  精炼课题: {refine_id}")
        print(f"  新标题: {refined['title']}")
        print(f"  新状态: {refined['status']}")
        print(f"  历史记录: {len(refined['refinement_history'])} 条")
        print("  ✓ 反馈应用 + 重新评分 + 历史记录 + 持久化")

        # ── [8/13] 课题演化 ──
        print("\n[8/13] 课题演化...")
        # 新报告：gap_001 保留，gap_002/gap_003 消失，gap_004 新增
        new_gap_report = {
            "gaps": [
                gap_report["gaps"][0],  # gap_001 保留
                {
                    "gap_id": "gap_004",
                    "type": "theoretical",
                    "description": "量子几何方向缺少成熟的理论方法：紧束缚模型",
                    "evidence": [{"source": "方法库扫描", "note": "无紧束缚模型"}],
                    "related_direction": "T1",
                    "priority_score": 0.75,
                    "novelty_score": 0.7,
                    "feasibility_score": 0.6,
                    "direction_alignment": 0.9,
                    "suggested_approach": "引入紧束缚模型用于量子几何方向的理论分析",
                },
            ],
            "summary": {"total_gaps": 2},
        }
        result = generator.evolve_topics(new_gap_report)
        print(f"  合并: {result['merged']} 个")
        print(f"  新增: {result['added']} 个")
        print(f"  丢弃: {result['dropped']} 个")
        # gap_003(empirical, 无方向) 的课题应被丢弃（gap_003 不在新报告中）
        assert result["dropped"] >= 1, "应丢弃 gap_003 相关的课题"
        # gap_004(theoretical, T1) 是新缺口，应生成新课题
        assert result["added"] >= 1, "应为 gap_004 生成新课题"
        # gap_001 保留，其课题不应被丢弃
        all_topics_after = generator.get_topics()
        dropped_topics = [t for t in all_topics_after if t["status"] == "dropped"]
        kept_topics = [t for t in all_topics_after if t["status"] != "dropped"]
        assert len(dropped_topics) >= 1, "应有被丢弃的课题"
        # 验证被丢弃课题有历史记录
        for dt in dropped_topics:
            assert any(h["action"] == "dropped" for h in dt.get("refinement_history", []))
        print(f"  丢弃课题: {len(dropped_topics)} 个")
        print(f"  保留课题: {len(kept_topics)} 个")
        print("  ✓ 演化正确（丢弃过期 + 新增缺口 + 历史记录）")

        # ── [9/13] Markdown 导出 ──
        print("\n[9/13] Markdown 导出...")
        md = generator.export_topics("markdown")
        assert "# 研究课题列表" in md
        assert "## 摘要" in md
        assert "## 课题列表" in md
        assert "课题ID" in md
        assert "总分" in md
        assert "品味匹配" in md
        assert "方向对齐" in md
        print(f"  Markdown 长度: {len(md)} 字符")
        print(f"  前 60 字符: {md[:60]}...")
        print("  ✓ Markdown 格式正确（含标题/摘要/课题列表/评分明细）")

        # ── [10/13] JSON 导出 ──
        print("\n[10/13] JSON 导出...")
        json_str = generator.export_topics("json")
        parsed = json.loads(json_str)
        assert "topics" in parsed
        assert "exported_at" in parsed
        assert isinstance(parsed["topics"], list)
        assert len(parsed["topics"]) > 0
        for t in parsed["topics"]:
            assert "topic_id" in t
            assert "title" in t
            assert "total_score" in t
        print(f"  JSON 长度: {len(json_str)} 字符")
        print(f"  课题数: {len(parsed['topics'])}")
        print("  ✓ JSON 格式正确，可正常解析")

        # ── [11/13] 空缺口报告处理 ──
        print("\n[11/13] 空缺口报告处理...")
        empty_gen = TopicGenerator(tmp / "empty_proposal")
        empty_topics = empty_gen.generate_topics({"gaps": [], "summary": {"total_gaps": 0}})
        assert empty_topics == [], "空缺口报告应返回空列表"
        # 空导出
        empty_md = empty_gen.export_topics("markdown")
        assert "暂无课题" in empty_md
        empty_json = empty_gen.export_topics("json")
        assert json.loads(empty_json)["topics"] == []
        print(f"  空报告生成结果: {empty_topics}")
        print(f"  空报告 Markdown: 含'暂无课题'提示")
        print("  ✓ 空缺口报告优雅处理")

        # ── [12/13] 品味引擎集成（mock TasteEngine） ──
        print("\n[12/13] 品味引擎集成...")

        class MockTasteEngine:
            """模拟品味引擎，返回特征平均值作为相似度。"""

            def get_similarity_score(self, features: Dict[str, Any]) -> float:
                novelty = features.get("novelty", 0.5)
                method = features.get("methodology", [0.5, 0.5, 0.5])
                depth = features.get("theoretical_depth", 0.5)
                inter = features.get("interdisciplinarity", 0.5)
                risk = features.get("risk_appetite", 0.5)
                avg = (novelty + sum(method) / 3 + depth + inter + risk) / 5
                return round(min(1.0, max(0.0, avg)), 4)

        mock_engine = MockTasteEngine()
        mock_gen = TopicGenerator(tmp / "mock_proposal", taste_engine=mock_engine)
        mock_topics = mock_gen.generate_topics(
            make_gap_report(), direction=direction, max_topics=10
        )
        assert len(mock_topics) > 0
        for t in mock_topics:
            # 验证 taste_score 来自 mock 引擎
            features = mock_gen._topic_to_features(t)
            expected_taste = mock_engine.get_similarity_score(features)
            assert abs(t["taste_score"] - expected_taste) < 1e-4, (
                f"taste_score 应来自 mock 引擎: "
                f"expected={expected_taste} actual={t['taste_score']}"
            )
            # 验证特征字典格式正确
            assert "novelty" in features
            assert "methodology" in features and isinstance(features["methodology"], list)
            assert len(features["methodology"]) == 3
            assert "theoretical_depth" in features
            assert "interdisciplinarity" in features
            assert "risk_appetite" in features
        print(f"  mock 引擎课题数: {len(mock_topics)}")
        print(f"  首个 taste_score: {mock_topics[0]['taste_score']}")
        print(f"  特征 methodology: {mock_gen._topic_to_features(mock_topics[0])['methodology']}")
        print("  ✓ 品味引擎集成正确（特征转换 + 相似度计算）")

        # ── [13/13] 原子写入 + 文件锁 ──
        print("\n[13/13] 原子写入 + 文件锁...")
        # 验证 topics.json 是有效 JSON（原子写入不会产生半写状态）
        raw_content = generator.topics_path.read_text(encoding="utf-8")
        parsed_again = json.loads(raw_content)
        assert "topics" in parsed_again
        assert "next_seq" in parsed_again
        assert "updated_at" in parsed_again
        assert len(parsed_again["topics"]) > 0
        # 验证锁名唯一性（不同 proposal 不同锁）
        gen2 = TopicGenerator(tmp / "another_proposal")
        assert gen2._lock_name != generator._lock_name, (
            "不同 proposal 应有不同锁名"
        )
        print(f"  锁名1: {generator._lock_name}")
        print(f"  锁名2: {gen2._lock_name}")
        # 验证多次写入不损坏
        gen3 = TopicGenerator(tmp / "multi_write_proposal")
        gen3.generate_topics(make_gap_report(), direction=direction)
        first_count = len(gen3.get_topics())
        gen3.generate_topics(make_gap_report(), direction=direction)
        second_count = len(gen3.get_topics())
        assert second_count == first_count * 2, (
            f"第二次生成应追加课题: first={first_count} second={second_count}"
        )
        raw2 = gen3.topics_path.read_text(encoding="utf-8")
        parsed2 = json.loads(raw2)
        assert len(parsed2["topics"]) == second_count
        print(f"  多次写入: first={first_count}, second={second_count}")
        print("  ✓ 原子写入有效，文件锁按 proposal 隔离，多次写入不损坏")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print("\n(已清理临时目录)")

    print("\n" + "=" * 50)
    print("✓ topic_generator 自检全部通过（13/13）")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="研究课题生成器")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
