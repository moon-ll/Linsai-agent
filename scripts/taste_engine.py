#!/usr/bin/env python3
"""
taste_engine.py — 学术品味引擎

用途：
    维护五维学术品味模型，从用户反馈中持续学习（WMA 加权移动平均），
    为课题评估、申请书撰写和质量自检提供个性化偏好锚点。

五维品味模型：
    1. novelty（创新性偏好）       — [0, 1] 连续值，0=极保守，1=极激进
    2. methodology（方法论严谨性） — 三维向量 (理论, 实验, 计算)，各分量 [0, 1]
    3. theoretical_depth（理论深度）— [0, 1] 连续值，0=纯应用，1=纯基础
    4. interdisciplinarity（跨学科性）— [0, 1] 连续值 + comfort_zones 领域集合
    5. risk_appetite（风险偏好）    — [0, 1] 连续值 + risk_threshold

反馈信号类型：
    - explicit（显式）：用户直接标注"好/差"或输入评语
    - implicit（隐式）：用户编辑 diff 分析（删减=负，保留=正，新增=偏好样本）
    - selection（选择）：用户选择某候选课题/段落（选中=正，未选=负）

用法示例：
    >>> from taste_engine import TasteEngine
    >>> engine = TasteEngine()
    >>> model = engine.load_model()
    >>> engine.update_from_feedback("explicit", {
    ...     "sentiment": "positive",
    ...     "topic_features": {"novelty": 0.9, "methodology": [0.8, 0.5, 0.7],
    ...                         "theoretical_depth": 0.8, "interdisciplinarity": 0.6,
    ...                         "risk_appetite": 0.7},
    ...     "example_id": "topic_20260615_003",
    ... })
    >>> score = engine.get_similarity_score({"novelty": 0.85, "methodology": [0.7, 0.5, 0.6],
    ...                                      "theoretical_depth": 0.7, "interdisciplinarity": 0.5,
    ...                                      "risk_appetite": 0.6})
    >>> print(engine.export_profile())
"""

from __future__ import annotations

import math
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import now_utc, load_json, save_json, file_lock
from paths import PIPELINE_CONFIG_DIR

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 品味模型存储文件名
MODEL_FILENAME = "taste-model.json"

# 模型版本
MODEL_VERSION = "v1.0"

# 维度名称常量
DIM_NOVELTY = "novelty"
DIM_METHODOLOGY = "methodology"
DIM_THEORETICAL_DEPTH = "theoretical_depth"
DIM_INTERDISCIPLINARITY = "interdisciplinarity"
DIM_RISK_APPETITE = "risk_appetite"

# 五维顺序（用于向量化与相似度计算）
DIM_ORDER: List[str] = [
    DIM_NOVELTY,
    DIM_METHODOLOGY,
    DIM_THEORETICAL_DEPTH,
    DIM_INTERDISCIPLINARITY,
    DIM_RISK_APPETITE,
]

# 快速学习期阈值（前 N 次反馈学习率翻倍）
FAST_LEARNING_THRESHOLD = 10

# 单次更新限幅
MAX_DELTA = 0.1

# 置信度档位
CONFIDENCE_LOW = "low"      # sample_count < 10
CONFIDENCE_MEDIUM = "medium"  # 10 <= sample_count < 30
CONFIDENCE_HIGH = "high"    # sample_count >= 30


# ---------------------------------------------------------------------------
# WMA 更新算法
# ---------------------------------------------------------------------------

def update_taste_dimension(current_value: float, feedback_signal: float,
                           sample_count: int) -> float:
    """WMA（加权移动平均）更新单个标量维度。

    学习率 = 1/(sample_count+1)，前 10 次翻倍，单次变化限幅 ±0.1。

    Args:
        current_value: 当前值 [0, 1]
        feedback_signal: 反馈信号值 [0, 1]
        sample_count: 已累积样本数

    Returns:
        更新后的值（夹紧到 [0, 1]）
    """
    learning_rate = 1.0 / (sample_count + 1)
    if sample_count < FAST_LEARNING_THRESHOLD:
        learning_rate *= 2.0
    delta = (feedback_signal - current_value) * learning_rate
    delta = max(-MAX_DELTA, min(MAX_DELTA, delta))  # 限幅 ±0.1
    new_value = current_value + delta
    # 夹紧到 [0, 1]
    return max(0.0, min(1.0, new_value))


def update_taste_vector(current_vector: List[float], feedback_vector: List[float],
                        sample_count: int) -> List[float]:
    """WMA 更新向量维度（逐分量应用 update_taste_dimension）。

    Args:
        current_vector: 当前向量，各分量 [0, 1]
        feedback_vector: 反馈信号向量，各分量 [0, 1]
        sample_count: 已累积样本数

    Returns:
        更新后的向量
    """
    if len(feedback_vector) != len(current_vector):
        # 长度不匹配时按当前向量长度截断或补齐
        fb = feedback_vector[:len(current_vector)]
        while len(fb) < len(current_vector):
            fb.append(current_vector[len(fb)])
    else:
        fb = feedback_vector
    return [
        update_taste_dimension(current_vector[i], fb[i], sample_count)
        for i in range(len(current_vector))
    ]


# ---------------------------------------------------------------------------
# TasteEngine 类
# ---------------------------------------------------------------------------

class TasteEngine:
    """学术品味引擎。

    维护五维学术品味模型，从用户反馈中持续学习，
    为课题评估、申请书撰写和质量自检提供个性化偏好锚点。

    Attributes:
        storage_dir: 模型存储目录（默认 MEMORY_DIR）
        model_path: 模型文件完整路径
        model: 当前加载的品味模型字典
    """

    def __init__(self, storage_dir: Path = PIPELINE_CONFIG_DIR) -> None:
        """初始化品味引擎。

        Args:
            storage_dir: 模型存储目录，默认为 MEMORY_DIR
        """
        self.storage_dir = Path(storage_dir)
        self.model_path = self.storage_dir / MODEL_FILENAME
        self.model: Dict[str, Any] = self.get_cold_start_model()

    # ------------------------------------------------------------------
    # 模型加载与保存
    # ------------------------------------------------------------------

    def load_model(self) -> Dict[str, Any]:
        """加载品味模型。

        文件不存在时返回冷启动默认值。

        Returns:
            品味模型字典
        """
        data = load_json(self.model_path, default=None)
        if data and isinstance(data, dict) and "dimensions" in data:
            self.model = data
            return data
        # 冷启动
        cold = self.get_cold_start_model()
        self.model = cold
        return cold

    def save_model(self, model: Optional[Dict[str, Any]] = None) -> None:
        """保存品味模型（使用 file_lock 保证线程/进程安全）。

        Args:
            model: 待保存的模型，默认保存当前 self.model
        """
        if model is None:
            model = self.model
        model["updated_at"] = now_utc()
        with file_lock("taste-model"):
            save_json(self.model_path, model)

    # ------------------------------------------------------------------
    # 冷启动与置信度
    # ------------------------------------------------------------------

    def get_cold_start_model(self) -> Dict[str, Any]:
        """返回冷启动默认模型。

        初始值：
            - novelty: 0.7（偏激进）
            - methodology: [0.7, 0.5, 0.6]（偏理论）
            - theoretical_depth: 0.7（偏基础）
            - interdisciplinarity: 0.5（中值）, comfort_zones: ["凝聚态", "光学", "拓扑"]
            - risk_appetite: 0.5（中值）, risk_threshold: 0.5

        Returns:
            冷启动模型字典
        """
        return {
            "version": MODEL_VERSION,
            "updated_at": now_utc(),
            "confidence": 0.1,
            "sample_count": 0,
            "dimensions": {
                DIM_NOVELTY: {"value": 0.7, "benchmark_papers": []},
                DIM_METHODOLOGY: {
                    "vector": [0.7, 0.5, 0.6],
                    "preferred_methods": [],
                },
                DIM_THEORETICAL_DEPTH: {"value": 0.7, "depth_threshold": 0.6},
                DIM_INTERDISCIPLINARITY: {
                    "value": 0.5,
                    "comfort_zones": ["凝聚态", "光学", "拓扑"],
                },
                DIM_RISK_APPETITE: {"value": 0.5, "risk_threshold": 0.5},
            },
            "positive_examples": [],
            "negative_examples": [],
            "evolution_log": [],
        }

    def get_confidence(self) -> float:
        """返回模型置信度（基于 sample_count）。

        档位：
            - <10：低（0.1 → 0.37）
            - 10-30：中（0.3 → 0.7）
            - >30：高（0.7 → 0.95）

        Returns:
            置信度 [0, 1]
        """
        n = self.model.get("sample_count", 0)
        if n < 10:
            return round(0.1 + n * 0.03, 3)
        elif n < 30:
            return round(0.3 + (n - 10) * 0.02, 3)
        else:
            return round(min(0.95, 0.7 + (n - 30) * 0.005), 3)

    def get_confidence_level(self) -> str:
        """返回置信度档位字符串（low/medium/high）。"""
        n = self.model.get("sample_count", 0)
        if n < 10:
            return CONFIDENCE_LOW
        elif n < 30:
            return CONFIDENCE_MEDIUM
        else:
            return CONFIDENCE_HIGH

    # ------------------------------------------------------------------
    # 维度读取
    # ------------------------------------------------------------------

    def get_dimension(self, dim_name: str) -> Any:
        """获取某维度当前值。

        Args:
            dim_name: 维度名称（novelty/methodology/theoretical_depth/
                      interdisciplinarity/risk_appetite）

        Returns:
            标量维度返回 value（float），methodology 返回 vector（list）。
            维度不存在时返回 None。
        """
        dims = self.model.get("dimensions", {})
        if dim_name not in dims:
            return None
        if dim_name == DIM_METHODOLOGY:
            return dims[dim_name].get("vector")
        return dims[dim_name].get("value")

    # ------------------------------------------------------------------
    # 相似度计算
    # ------------------------------------------------------------------

    def _model_to_vector(self) -> List[float]:
        """将品味模型展平为 7 维向量。

        顺序：[novelty, method[0], method[1], method[2],
              theoretical_depth, interdisciplinarity, risk_appetite]
        """
        d = self.model["dimensions"]
        return [
            d[DIM_NOVELTY]["value"],
            d[DIM_METHODOLOGY]["vector"][0],
            d[DIM_METHODOLOGY]["vector"][1],
            d[DIM_METHODOLOGY]["vector"][2],
            d[DIM_THEORETICAL_DEPTH]["value"],
            d[DIM_INTERDISCIPLINARITY]["value"],
            d[DIM_RISK_APPETITE]["value"],
        ]

    def _features_to_vector(self, topic_features: Dict[str, Any]) -> List[float]:
        """将课题特征字典展平为 7 维向量（与模型向量对齐）。"""
        method = topic_features.get(DIM_METHODOLOGY, [0.5, 0.5, 0.5])
        if not isinstance(method, list) or len(method) < 3:
            method = [0.5, 0.5, 0.5]
        return [
            float(topic_features.get(DIM_NOVELTY, 0.5)),
            float(method[0]),
            float(method[1]),
            float(method[2]),
            float(topic_features.get(DIM_THEORETICAL_DEPTH, 0.5)),
            float(topic_features.get(DIM_INTERDISCIPLINARITY, 0.5)),
            float(topic_features.get(DIM_RISK_APPETITE, 0.5)),
        ]

    def get_similarity_score(self, topic_features: Dict[str, Any]) -> float:
        """计算课题特征与品味模型的余弦相似度。

        Args:
            topic_features: 课题特征字典，含 novelty/methodology/
                           theoretical_depth/interdisciplinarity/risk_appetite

        Returns:
            余弦相似度 [0, 1]（归一化后，原始余弦相似度范围 [-1, 1] 映射到 [0, 1]）
        """
        model_vec = self._model_to_vector()
        topic_vec = self._features_to_vector(topic_features)

        dot = sum(a * b for a, b in zip(model_vec, topic_vec))
        norm_a = math.sqrt(sum(a * a for a in model_vec))
        norm_b = math.sqrt(sum(b * b for b in topic_vec))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        cosine = dot / (norm_a * norm_b)
        # 归一化到 [0, 1]
        return round(max(0.0, min(1.0, (cosine + 1) / 2)), 4)

    # ------------------------------------------------------------------
    # 反馈解析
    # ------------------------------------------------------------------

    def _extract_signal_vector(self, feedback_data: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """从反馈数据中提取五维信号向量与触发描述。

        解析逻辑：
            - explicit positive: 信号 = 课题特征本身
            - explicit negative: 信号 = 反转（1 - 特征）
            - selection selected: 正样本，信号 = 课题特征
            - selection unselected: 负样本，信号 = 反转
            - implicit: 基于 diff（保留=正，删减=负，新增=偏好）

        Args:
            feedback_data: 反馈数据字典

        Returns:
            (信号字典, 触发描述字符串)
        """
        sentiment = feedback_data.get("sentiment", "neutral")
        topic_features = feedback_data.get("topic_features", {})
        comment = feedback_data.get("comment", "")
        example_id = feedback_data.get("example_id", "unknown")

        # 默认中性信号
        signal: Dict[str, Any] = {
            DIM_NOVELTY: 0.5,
            DIM_METHODOLOGY: [0.5, 0.5, 0.5],
            DIM_THEORETICAL_DEPTH: 0.5,
            DIM_INTERDISCIPLINARITY: 0.5,
            DIM_RISK_APPETITE: 0.5,
        }

        trigger = feedback_data.get("trigger", "")

        if topic_features:
            # 有课题特征：根据情感决定正/负信号
            if sentiment == "negative":
                # 负反馈：反转信号（1 - value）
                signal[DIM_NOVELTY] = 1.0 - float(topic_features.get(DIM_NOVELTY, 0.5))
                m = topic_features.get(DIM_METHODOLOGY, [0.5, 0.5, 0.5])
                signal[DIM_METHODOLOGY] = [1.0 - float(x) for x in m]
                signal[DIM_THEORETICAL_DEPTH] = 1.0 - float(
                    topic_features.get(DIM_THEORETICAL_DEPTH, 0.5))
                signal[DIM_INTERDISCIPLINARITY] = 1.0 - float(
                    topic_features.get(DIM_INTERDISCIPLINARITY, 0.5))
                signal[DIM_RISK_APPETITE] = 1.0 - float(
                    topic_features.get(DIM_RISK_APPETITE, 0.5))
                if not trigger:
                    trigger = f"rejected {example_id}"
            else:
                # 正反馈或中性：信号 = 特征本身
                signal[DIM_NOVELTY] = float(topic_features.get(DIM_NOVELTY, 0.5))
                m = topic_features.get(DIM_METHODOLOGY, [0.5, 0.5, 0.5])
                signal[DIM_METHODOLOGY] = [float(x) for x in m]
                signal[DIM_THEORETICAL_DEPTH] = float(
                    topic_features.get(DIM_THEORETICAL_DEPTH, 0.5))
                signal[DIM_INTERDISCIPLINARITY] = float(
                    topic_features.get(DIM_INTERDISCIPLINARITY, 0.5))
                signal[DIM_RISK_APPETITE] = float(
                    topic_features.get(DIM_RISK_APPETITE, 0.5))
                if not trigger:
                    trigger = f"accepted {example_id}" if sentiment == "positive" else f"neutral {example_id}"
        else:
            # 无课题特征：基于评语关键词推断
            if comment:
                lowered = comment.lower()
                positive_words = ["好", "喜欢", "赞", "good", "great", "excellent", "nice"]
                negative_words = ["差", "不喜欢", "糟", "bad", "poor", "reject", "weak"]
                if any(w in lowered for w in positive_words):
                    signal[DIM_NOVELTY] = 0.8
                    signal[DIM_THEORETICAL_DEPTH] = 0.7
                    if not trigger:
                        trigger = f"comment-positive {example_id}"
                elif any(w in lowered for w in negative_words):
                    signal[DIM_NOVELTY] = 0.3
                    signal[DIM_THEORETICAL_DEPTH] = 0.3
                    if not trigger:
                        trigger = f"comment-negative {example_id}"

        return signal, trigger

    # ------------------------------------------------------------------
    # 核心学习函数
    # ------------------------------------------------------------------

    def update_from_feedback(self, feedback_type: str,
                             feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """核心学习函数：解析反馈信号 → 提取五维信号向量 → WMA 更新模型。

        Args:
            feedback_type: 反馈类型（explicit/implicit/selection）
            feedback_data: 反馈数据字典，可包含：
                - sentiment: positive/negative/neutral
                - topic_features: 课题特征字典
                - example_id: 样本 ID
                - comment: 评语文本（explicit）
                - diff: 编辑差异（implicit）
                - selected: 是否选中（selection）
                - comfort_zone: 舒适领域（可选）
                - trigger: 自定义触发描述（可选）

        Returns:
            更新摘要字典，包含 changes（各维度变化）、new_sample_count、confidence
        """
        # 确保模型已加载
        if "dimensions" not in self.model:
            self.model = self.get_cold_start_model()

        sample_count = self.model.get("sample_count", 0)
        dims = self.model["dimensions"]

        # 隐式反馈：基于 diff 调整 sentiment
        if feedback_type == "implicit":
            diff = feedback_data.get("diff", {})
            added = diff.get("added", 0)
            deleted = diff.get("deleted", 0)
            if deleted > added:
                feedback_data.setdefault("sentiment", "negative")
            elif added > 0:
                feedback_data.setdefault("sentiment", "positive")

        # 选择反馈：基于 selected 标志
        if feedback_type == "selection":
            if feedback_data.get("selected", False):
                feedback_data.setdefault("sentiment", "positive")
            else:
                feedback_data.setdefault("sentiment", "negative")

        # 提取信号向量
        signal, trigger = self._extract_signal_vector(feedback_data)

        # 记录更新前的值（用于 evolution_log）
        old_novelty = dims[DIM_NOVELTY]["value"]
        old_method = list(dims[DIM_METHODOLOGY]["vector"])
        old_depth = dims[DIM_THEORETICAL_DEPTH]["value"]
        old_inter = dims[DIM_INTERDISCIPLINARITY]["value"]
        old_risk = dims[DIM_RISK_APPETITE]["value"]

        # 五维更新
        new_novelty = self.update_novelty(signal[DIM_NOVELTY], sample_count)
        new_method = self.update_methodology(signal[DIM_METHODOLOGY], sample_count)
        new_depth = self.update_theoretical_depth(signal[DIM_THEORETICAL_DEPTH], sample_count)
        comfort_zone = feedback_data.get("comfort_zone")
        new_inter = self.update_interdisciplinarity(
            signal[DIM_INTERDISCIPLINARITY], comfort_zone, sample_count)
        new_risk = self.update_risk_appetite(signal[DIM_RISK_APPETITE], sample_count)

        # 样本计数 +1
        self.model["sample_count"] = sample_count + 1

        # 更新置信度
        self.model["confidence"] = self.get_confidence()

        # 记录正/负样本
        example_id = feedback_data.get("example_id")
        sentiment = feedback_data.get("sentiment", "neutral")
        if example_id and sentiment == "positive":
            self.add_positive_example(example_id)
        elif example_id and sentiment == "negative":
            self.add_negative_example(example_id)

        # 记录 evolution_log
        changes: List[str] = []
        if abs(new_novelty - old_novelty) > 1e-6:
            changes.append(
                f"novelty: {old_novelty:.3f} → {new_novelty:.3f}")
        if any(abs(new_method[i] - old_method[i]) > 1e-6 for i in range(3)):
            changes.append(
                f"methodology: {old_method} → {new_method}")
        if abs(new_depth - old_depth) > 1e-6:
            changes.append(
                f"theoretical_depth: {old_depth:.3f} → {new_depth:.3f}")
        if abs(new_inter - old_inter) > 1e-6:
            changes.append(
                f"interdisciplinarity: {old_inter:.3f} → {new_inter:.3f}")
        if abs(new_risk - old_risk) > 1e-6:
            changes.append(
                f"risk_appetite: {old_risk:.3f} → {new_risk:.3f}")

        if changes:
            log_entry = {
                "date": now_utc()[:10],
                "change": "; ".join(changes),
                "trigger": trigger or f"{feedback_type} feedback",
            }
            self.model["evolution_log"].append(log_entry)
            # evolution_log 保留最近 200 条，避免无限增长
            if len(self.model["evolution_log"]) > 200:
                self.model["evolution_log"] = self.model["evolution_log"][-200:]

        return {
            "changes": changes,
            "new_sample_count": self.model["sample_count"],
            "confidence": self.model["confidence"],
            "trigger": trigger,
        }

    # ------------------------------------------------------------------
    # 五维更新函数
    # ------------------------------------------------------------------

    def update_novelty(self, signal: float, sample_count: int) -> float:
        """更新创新性维度。

        Args:
            signal: 反馈信号值 [0, 1]
            sample_count: 已累积样本数

        Returns:
            更新后的 novelty 值
        """
        dims = self.model["dimensions"]
        current = dims[DIM_NOVELTY]["value"]
        new_value = update_taste_dimension(current, signal, sample_count)
        dims[DIM_NOVELTY]["value"] = new_value
        return new_value

    def update_methodology(self, signal_vector: List[float],
                           sample_count: int) -> List[float]:
        """更新方法论维度（三维向量）。

        Args:
            signal_vector: 反馈信号向量 (理论, 实验, 计算)，各分量 [0, 1]
            sample_count: 已累积样本数

        Returns:
            更新后的方法论向量
        """
        dims = self.model["dimensions"]
        current = dims[DIM_METHODOLOGY]["vector"]
        new_vector = update_taste_vector(current, signal_vector, sample_count)
        dims[DIM_METHODOLOGY]["vector"] = new_vector
        return new_vector

    def update_theoretical_depth(self, signal: float,
                                 sample_count: int) -> float:
        """更新理论深度维度。

        Args:
            signal: 反馈信号值 [0, 1]
            sample_count: 已累积样本数

        Returns:
            更新后的 theoretical_depth 值
        """
        dims = self.model["dimensions"]
        current = dims[DIM_THEORETICAL_DEPTH]["value"]
        new_value = update_taste_dimension(current, signal, sample_count)
        dims[DIM_THEORETICAL_DEPTH]["value"] = new_value
        return new_value

    def update_interdisciplinarity(self, signal: float,
                                   comfort_zone: Optional[str],
                                   sample_count: int) -> float:
        """更新跨学科性维度。

        Args:
            signal: 反馈信号值 [0, 1]
            comfort_zone: 舒适领域名称（如"凝聚态"），若提供则加入 comfort_zones
            sample_count: 已累积样本数

        Returns:
            更新后的 interdisciplinarity 值
        """
        dims = self.model["dimensions"]
        current = dims[DIM_INTERDISCIPLINARITY]["value"]
        new_value = update_taste_dimension(current, signal, sample_count)
        dims[DIM_INTERDISCIPLINARITY]["value"] = new_value
        if comfort_zone:
            zones = dims[DIM_INTERDISCIPLINARITY]["comfort_zones"]
            if comfort_zone not in zones:
                zones.append(comfort_zone)
                # 保留最近 15 个舒适领域
                if len(zones) > 15:
                    dims[DIM_INTERDISCIPLINARITY]["comfort_zones"] = zones[-15:]
        return new_value

    def update_risk_appetite(self, signal: float,
                             sample_count: int) -> float:
        """更新风险偏好维度。

        Args:
            signal: 反馈信号值 [0, 1]
            sample_count: 已累积样本数

        Returns:
            更新后的 risk_appetite 值
        """
        dims = self.model["dimensions"]
        current = dims[DIM_RISK_APPETITE]["value"]
        new_value = update_taste_dimension(current, signal, sample_count)
        dims[DIM_RISK_APPETITE]["value"] = new_value
        return new_value

    # ------------------------------------------------------------------
    # 正/负样本管理
    # ------------------------------------------------------------------

    def add_positive_example(self, example_id: str) -> None:
        """添加正样本。

        Args:
            example_id: 样本 ID（如 topic_20260615_003）
        """
        examples = self.model["positive_examples"]
        if example_id not in examples:
            examples.append(example_id)
            # 保留最近 100 个
            if len(examples) > 100:
                self.model["positive_examples"] = examples[-100:]

    def add_negative_example(self, example_id: str) -> None:
        """添加负样本。

        Args:
            example_id: 样本 ID（如 topic_20260620_002）
        """
        examples = self.model["negative_examples"]
        if example_id not in examples:
            examples.append(example_id)
            # 保留最近 100 个
            if len(examples) > 100:
                self.model["negative_examples"] = examples[-100:]

    # ------------------------------------------------------------------
    # 画像导出
    # ------------------------------------------------------------------

    def export_profile(self) -> str:
        """导出人类可读的品味画像文本。

        Returns:
            多行字符串，包含五维品味画像、置信度、样本数、正/负样本统计
        """
        d = self.model["dimensions"]
        conf = self.get_confidence()
        level = self.get_confidence_level()
        sample_count = self.model.get("sample_count", 0)
        pos = len(self.model.get("positive_examples", []))
        neg = len(self.model.get("negative_examples", []))

        # 方法论分量描述
        method_vec = d[DIM_METHODOLOGY]["vector"]
        method_labels = ["理论", "实验", "计算"]
        method_desc = "、".join(
            f"{label} {v:.2f}" for label, v in zip(method_labels, method_vec))

        # novelty 描述
        novelty_val = d[DIM_NOVELTY]["value"]
        if novelty_val >= 0.7:
            novelty_desc = "偏激进（追求前沿创新）"
        elif novelty_val >= 0.4:
            novelty_desc = "平衡（兼顾创新与稳健）"
        else:
            novelty_desc = "偏保守（重视成熟方向）"

        # 理论深度描述
        depth_val = d[DIM_THEORETICAL_DEPTH]["value"]
        if depth_val >= 0.7:
            depth_desc = "偏基础（重视物理机制）"
        elif depth_val >= 0.4:
            depth_desc = "平衡（基础与应用并重）"
        else:
            depth_desc = "偏应用（重视实用价值）"

        # 跨学科描述
        inter_val = d[DIM_INTERDISCIPLINARITY]["value"]
        zones = d[DIM_INTERDISCIPLINARITY]["comfort_zones"]
        if inter_val >= 0.7:
            inter_desc = "高（乐于跨界探索）"
        elif inter_val >= 0.4:
            inter_desc = "中（适度跨学科）"
        else:
            inter_desc = "低（专注核心领域）"

        # 风险偏好描述
        risk_val = d[DIM_RISK_APPETITE]["value"]
        if risk_val >= 0.7:
            risk_desc = "高风险偏好（敢啃硬骨头）"
        elif risk_val >= 0.4:
            risk_desc = "中风险偏好（权衡收益与代价）"
        else:
            risk_desc = "低风险偏好（规避不确定性）"

        lines = [
            "=" * 60,
            "学术品味画像（LinSai-CoPilot Taste Engine）",
            "=" * 60,
            f"置信度：{conf:.2f}（{level}） | 样本数：{sample_count} | 正样本：{pos} | 负样本：{neg}",
            "-" * 60,
            "【五维品味模型】",
            f"1. 创新性偏好（novelty）：{novelty_val:.2f} — {novelty_desc}",
            f"2. 方法论严谨性（methodology）：{method_desc}",
            f"3. 理论深度（theoretical_depth）：{depth_val:.2f} — {depth_desc}",
            f"4. 跨学科性（interdisciplinarity）：{inter_val:.2f} — {inter_desc}",
            f"   舒适领域：{', '.join(zones) if zones else '（暂无）'}",
            f"5. 风险偏好（risk_appetite）：{risk_val:.2f} — {risk_desc}",
            "-" * 60,
        ]

        # 最近演化记录
        log = self.model.get("evolution_log", [])
        if log:
            lines.append("【近期演化】")
            for entry in log[-5:]:
                lines.append(f"  [{entry.get('date', '?')}] {entry.get('change', '?')}")
                if entry.get("trigger"):
                    lines.append(f"    触发：{entry['trigger']}")
        else:
            lines.append("【近期演化】暂无记录（冷启动阶段）")

        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> bool:
    """taste_engine 自检。

    测试场景：
        1. 冷启动 → 验证默认值正确
        2. 显式反馈更新 → 验证 WMA 更新和 evolution_log
        3. 选择反馈 → 验证正/负样本记录
        4. 连续多次反馈 → 验证学习率衰减
        5. 限幅验证 → 单次变化不超过 0.1
        6. 相似度计算 → 验证余弦相似度
        7. 置信度变化 → 验证随 sample_count 变化
        8. 导出画像 → 验证人类可读输出

    使用临时目录隔离测试，不污染真实数据。

    Returns:
        True 表示全部通过，False 表示有失败项
    """
    import tempfile
    import shutil as _shutil

    results: List[Tuple[str, bool, str]] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        results.append((name, cond, detail))

    # 使用临时目录隔离（根目录），每个需要冷启动的场景使用独立子目录，
    # 避免场景间通过持久化文件相互污染。
    tmp_root = Path(tempfile.mkdtemp(prefix="taste_engine_test_"))
    _subdir_counter = [0]

    def fresh_dir() -> Path:
        """创建一个独立的空子目录，保证每次调用返回的目录无模型文件。"""
        _subdir_counter[0] += 1
        d = tmp_root / f"scenario_{_subdir_counter[0]}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    try:
        # ------------------------------------------------------------------
        # 场景 1：冷启动 → 验证默认值正确
        # ------------------------------------------------------------------
        engine = TasteEngine(storage_dir=fresh_dir())
        model = engine.load_model()
        check("1.1 冷启动返回模型", "dimensions" in model, "应含 dimensions")
        check("1.2 novelty 默认 0.7",
              abs(model["dimensions"][DIM_NOVELTY]["value"] - 0.7) < 1e-6,
              f"实际：{model['dimensions'][DIM_NOVELTY]['value']}")
        check("1.3 methodology 默认 [0.7, 0.5, 0.6]",
              model["dimensions"][DIM_METHODOLOGY]["vector"] == [0.7, 0.5, 0.6],
              f"实际：{model['dimensions'][DIM_METHODOLOGY]['vector']}")
        check("1.4 theoretical_depth 默认 0.7",
              abs(model["dimensions"][DIM_THEORETICAL_DEPTH]["value"] - 0.7) < 1e-6,
              f"实际：{model['dimensions'][DIM_THEORETICAL_DEPTH]['value']}")
        check("1.5 interdisciplinarity 默认 0.5",
              abs(model["dimensions"][DIM_INTERDISCIPLINARITY]["value"] - 0.5) < 1e-6,
              f"实际：{model['dimensions'][DIM_INTERDISCIPLINARITY]['value']}")
        check("1.6 risk_appetite 默认 0.5",
              abs(model["dimensions"][DIM_RISK_APPETITE]["value"] - 0.5) < 1e-6,
              f"实际：{model['dimensions'][DIM_RISK_APPETITE]['value']}")
        check("1.7 comfort_zones 含凝聚态/光学/拓扑",
              set(model["dimensions"][DIM_INTERDISCIPLINARITY]["comfort_zones"]) ==
              {"凝聚态", "光学", "拓扑"},
              f"实际：{model['dimensions'][DIM_INTERDISCIPLINARITY]['comfort_zones']}")
        check("1.8 sample_count 初始 0",
              model["sample_count"] == 0,
              f"实际：{model['sample_count']}")
        check("1.9 version 为 v1.0",
              model["version"] == MODEL_VERSION,
              f"实际：{model['version']}")

        # ------------------------------------------------------------------
        # 场景 2：显式反馈更新 → 验证 WMA 更新和 evolution_log
        # ------------------------------------------------------------------
        dir2 = fresh_dir()
        engine2 = TasteEngine(storage_dir=dir2)
        engine2.load_model()
        old_novelty = engine2.model["dimensions"][DIM_NOVELTY]["value"]
        # 正反馈，novelty=0.9
        summary = engine2.update_from_feedback("explicit", {
            "sentiment": "positive",
            "topic_features": {
                DIM_NOVELTY: 0.9,
                DIM_METHODOLOGY: [0.8, 0.5, 0.7],
                DIM_THEORETICAL_DEPTH: 0.8,
                DIM_INTERDISCIPLINARITY: 0.6,
                DIM_RISK_APPETITE: 0.7,
            },
            "example_id": "topic_20260615_003",
        })
        new_novelty = engine2.model["dimensions"][DIM_NOVELTY]["value"]
        # sample_count=0，学习率 = 1/(0+1)*2 = 2.0，delta = (0.9-0.7)*2 = 0.4，限幅 0.1
        check("2.1 显式反馈后 novelty 增加",
              new_novelty > old_novelty,
              f"old={old_novelty}, new={new_novelty}")
        check("2.2 限幅生效（变化 ≤ 0.1）",
              abs(new_novelty - old_novelty) <= 0.1 + 1e-6,
              f"变化={abs(new_novelty - old_novelty)}")
        check("2.3 sample_count 递增",
              engine2.model["sample_count"] == 1,
              f"实际：{engine2.model['sample_count']}")
        check("2.4 evolution_log 有记录",
              len(engine2.model["evolution_log"]) >= 1,
              f"实际记录数：{len(engine2.model['evolution_log'])}")
        check("2.5 evolution_log 含 change 字段",
              "change" in engine2.model["evolution_log"][0],
              f"实际：{engine2.model['evolution_log'][0]}")
        check("2.6 正样本已记录",
              "topic_20260615_003" in engine2.model["positive_examples"],
              f"实际：{engine2.model['positive_examples']}")
        check("2.7 summary 含 changes 列表",
              isinstance(summary.get("changes"), list) and len(summary["changes"]) > 0,
              f"实际：{summary}")
        check("2.8 保存后可重新加载",
              True, "")
        engine2.save_model()
        engine3 = TasteEngine(storage_dir=dir2)
        loaded = engine3.load_model()
        check("2.9 重新加载后 sample_count=1",
              loaded["sample_count"] == 1,
              f"实际：{loaded['sample_count']}")
        check("2.10 重新加载后 novelty 一致",
              abs(loaded["dimensions"][DIM_NOVELTY]["value"] - new_novelty) < 1e-6,
              f"loaded={loaded['dimensions'][DIM_NOVELTY]['value']}, saved={new_novelty}")

        # ------------------------------------------------------------------
        # 场景 3：选择反馈 → 验证正/负样本记录
        # ------------------------------------------------------------------
        engine4 = TasteEngine(storage_dir=fresh_dir())
        engine4.load_model()
        # 选中 → 正样本
        engine4.update_from_feedback("selection", {
            "selected": True,
            "topic_features": {
                DIM_NOVELTY: 0.8, DIM_METHODOLOGY: [0.7, 0.5, 0.6],
                DIM_THEORETICAL_DEPTH: 0.7, DIM_INTERDISCIPLINARITY: 0.5,
                DIM_RISK_APPETITE: 0.6,
            },
            "example_id": "topic_sel_001",
        })
        check("3.1 选中反馈记录正样本",
              "topic_sel_001" in engine4.model["positive_examples"],
              f"实际：{engine4.model['positive_examples']}")
        # 未选 → 负样本
        engine4.update_from_feedback("selection", {
            "selected": False,
            "topic_features": {
                DIM_NOVELTY: 0.3, DIM_METHODOLOGY: [0.4, 0.5, 0.5],
                DIM_THEORETICAL_DEPTH: 0.3, DIM_INTERDISCIPLINARITY: 0.5,
                DIM_RISK_APPETITE: 0.4,
            },
            "example_id": "topic_sel_002",
        })
        check("3.2 未选反馈记录负样本",
              "topic_sel_002" in engine4.model["negative_examples"],
              f"实际：{engine4.model['negative_examples']}")
        check("3.3 正样本数=1",
              len(engine4.model["positive_examples"]) == 1,
              f"实际：{len(engine4.model['positive_examples'])}")
        check("3.4 负样本数=1",
              len(engine4.model["negative_examples"]) == 1,
              f"实际：{len(engine4.model['negative_examples'])}")

        # ------------------------------------------------------------------
        # 场景 4：连续多次反馈 → 验证学习率衰减
        # ------------------------------------------------------------------
        engine5 = TasteEngine(storage_dir=fresh_dir())
        engine5.load_model()
        # 第 1 次：sample_count=0，学习率=2.0
        first_novelty_before = engine5.model["dimensions"][DIM_NOVELTY]["value"]
        engine5.update_from_feedback("explicit", {
            "sentiment": "positive",
            "topic_features": {DIM_NOVELTY: 0.9, DIM_METHODOLOGY: [0.7, 0.5, 0.6],
                                DIM_THEORETICAL_DEPTH: 0.7, DIM_INTERDISCIPLINARITY: 0.5,
                                DIM_RISK_APPETITE: 0.5},
            "example_id": "t1",
        })
        first_delta = abs(engine5.model["dimensions"][DIM_NOVELTY]["value"] - first_novelty_before)

        # 连续 15 次反馈
        for i in range(15):
            engine5.update_from_feedback("explicit", {
                "sentiment": "positive",
                "topic_features": {DIM_NOVELTY: 0.9, DIM_METHODOLOGY: [0.7, 0.5, 0.6],
                                    DIM_THEORETICAL_DEPTH: 0.7, DIM_INTERDISCIPLINARITY: 0.5,
                                    DIM_RISK_APPETITE: 0.5},
                "example_id": f"t_loop_{i}",
            })

        # 第 17 次：sample_count=16，学习率 = 1/17 ≈ 0.059
        late_novelty_before = engine5.model["dimensions"][DIM_NOVELTY]["value"]
        engine5.update_from_feedback("explicit", {
            "sentiment": "positive",
            "topic_features": {DIM_NOVELTY: 0.95, DIM_METHODOLOGY: [0.7, 0.5, 0.6],
                                DIM_THEORETICAL_DEPTH: 0.7, DIM_INTERDISCIPLINARITY: 0.5,
                                DIM_RISK_APPETITE: 0.5},
            "example_id": "t_late",
        })
        late_delta = abs(engine5.model["dimensions"][DIM_NOVELTY]["value"] - late_novelty_before)
        check("4.1 学习率衰减：后期变化 < 前期变化",
              late_delta <= first_delta + 1e-6,
              f"first_delta={first_delta}, late_delta={late_delta}")
        check("4.2 sample_count=17",
              engine5.model["sample_count"] == 17,
              f"实际：{engine5.model['sample_count']}")

        # ------------------------------------------------------------------
        # 场景 5：限幅验证 → 单次变化不超过 0.1
        # ------------------------------------------------------------------
        engine6 = TasteEngine(storage_dir=fresh_dir())
        engine6.load_model()
        # 极端信号 1.0，与当前 0.7 差 0.3，学习率 2.0，理论 delta=0.6，应限幅到 0.1
        before = engine6.model["dimensions"][DIM_NOVELTY]["value"]
        engine6.update_novelty(1.0, 0)
        after = engine6.model["dimensions"][DIM_NOVELTY]["value"]
        check("5.1 单次更新限幅 ≤ 0.1",
              abs(after - before) <= 0.1 + 1e-6,
              f"before={before}, after={after}, delta={abs(after - before)}")

        # 测试向量限幅
        engine7 = TasteEngine(storage_dir=fresh_dir())
        engine7.load_model()
        before_vec = list(engine7.model["dimensions"][DIM_METHODOLOGY]["vector"])
        engine7.update_methodology([1.0, 0.0, 1.0], 0)
        after_vec = engine7.model["dimensions"][DIM_METHODOLOGY]["vector"]
        max_component_delta = max(abs(after_vec[i] - before_vec[i]) for i in range(3))
        check("5.2 向量各分量限幅 ≤ 0.1",
              max_component_delta <= 0.1 + 1e-6,
              f"before={before_vec}, after={after_vec}, max_delta={max_component_delta}")

        # ------------------------------------------------------------------
        # 场景 6：相似度计算 → 验证余弦相似度
        # ------------------------------------------------------------------
        engine8 = TasteEngine(storage_dir=fresh_dir())
        engine8.load_model()
        # 与冷启动模型完全一致的特征 → 相似度应为 1.0
        identical_features = {
            DIM_NOVELTY: 0.7,
            DIM_METHODOLOGY: [0.7, 0.5, 0.6],
            DIM_THEORETICAL_DEPTH: 0.7,
            DIM_INTERDISCIPLINARITY: 0.5,
            DIM_RISK_APPETITE: 0.5,
        }
        score_identical = engine8.get_similarity_score(identical_features)
        check("6.1 与自身相似度=1.0",
              abs(score_identical - 1.0) < 1e-3,
              f"实际：{score_identical}")

        # 完全相反特征 → 相似度应较低
        opposite_features = {
            DIM_NOVELTY: 0.1,
            DIM_METHODOLOGY: [0.1, 0.9, 0.1],
            DIM_THEORETICAL_DEPTH: 0.1,
            DIM_INTERDISCIPLINARITY: 0.9,
            DIM_RISK_APPETITE: 0.9,
        }
        score_opposite = engine8.get_similarity_score(opposite_features)
        check("6.2 相反特征相似度 < 一致特征相似度",
              score_opposite < score_identical,
              f"opposite={score_opposite}, identical={score_identical}")
        check("6.3 相似度在 [0, 1] 范围内",
              0.0 <= score_opposite <= 1.0,
              f"实际：{score_opposite}")

        # 零向量处理
        zero_score = engine8.get_similarity_score({
            DIM_NOVELTY: 0.0, DIM_METHODOLOGY: [0.0, 0.0, 0.0],
            DIM_THEORETICAL_DEPTH: 0.0, DIM_INTERDISCIPLINARITY: 0.0,
            DIM_RISK_APPETITE: 0.0,
        })
        check("6.4 零向量不报错", isinstance(zero_score, float), f"实际：{zero_score}")

        # ------------------------------------------------------------------
        # 场景 7：置信度变化 → 验证随 sample_count 变化
        # ------------------------------------------------------------------
        engine9 = TasteEngine(storage_dir=fresh_dir())
        engine9.load_model()
        conf_0 = engine9.get_confidence()
        level_0 = engine9.get_confidence_level()
        engine9.model["sample_count"] = 5
        conf_5 = engine9.get_confidence()
        engine9.model["sample_count"] = 20
        conf_20 = engine9.get_confidence()
        engine9.model["sample_count"] = 50
        conf_50 = engine9.get_confidence()
        check("7.1 置信度随样本数递增",
              conf_0 <= conf_5 <= conf_20 <= conf_50,
              f"conf: 0→{conf_0}, 5→{conf_5}, 20→{conf_20}, 50→{conf_50}")
        check("7.2 sample_count=0 为低置信度",
              level_0 == CONFIDENCE_LOW,
              f"实际：{level_0}")
        engine9.model["sample_count"] = 15
        check("7.3 sample_count=15 为中置信度",
              engine9.get_confidence_level() == CONFIDENCE_MEDIUM,
              f"实际：{engine9.get_confidence_level()}")
        engine9.model["sample_count"] = 35
        check("7.4 sample_count=35 为高置信度",
              engine9.get_confidence_level() == CONFIDENCE_HIGH,
              f"实际：{engine9.get_confidence_level()}")
        check("7.5 置信度 ≤ 0.95",
              conf_50 <= 0.95 + 1e-6,
              f"实际：{conf_50}")

        # ------------------------------------------------------------------
        # 场景 8：导出画像 → 验证人类可读输出
        # ------------------------------------------------------------------
        engine10 = TasteEngine(storage_dir=fresh_dir())
        engine10.load_model()
        # 做几次反馈让画像有内容
        engine10.update_from_feedback("explicit", {
            "sentiment": "positive",
            "topic_features": {DIM_NOVELTY: 0.9, DIM_METHODOLOGY: [0.8, 0.5, 0.7],
                                DIM_THEORETICAL_DEPTH: 0.8, DIM_INTERDISCIPLINARITY: 0.6,
                                DIM_RISK_APPETITE: 0.7},
            "example_id": "profile_test_001",
        })
        profile = engine10.export_profile()
        check("8.1 画像是字符串", isinstance(profile, str), f"类型：{type(profile)}")
        check("8.2 画像含标题", "学术品味画像" in profile, "")
        check("8.3 画像含创新性", "novelty" in profile, "")
        check("8.4 画像含方法论", "methodology" in profile, "")
        check("8.5 画像含理论深度", "theoretical_depth" in profile, "")
        check("8.6 画像含跨学科性", "interdisciplinarity" in profile, "")
        check("8.7 画像含风险偏好", "risk_appetite" in profile, "")
        check("8.8 画像含置信度", "置信度" in profile, "")
        check("8.9 画像含演化记录", "演化" in profile, "")
        check("8.10 画像含舒适领域", "舒适领域" in profile, "")

        # ------------------------------------------------------------------
        # 附加：get_dimension / 隐式反馈 / comfort_zone
        # ------------------------------------------------------------------
        engine11 = TasteEngine(storage_dir=fresh_dir())
        engine11.load_model()
        check("附加.1 get_dimension(novelty) 返回 0.7",
              abs(engine11.get_dimension(DIM_NOVELTY) - 0.7) < 1e-6,
              f"实际：{engine11.get_dimension(DIM_NOVELTY)}")
        check("附加.2 get_dimension(methodology) 返回向量",
              engine11.get_dimension(DIM_METHODOLOGY) == [0.7, 0.5, 0.6],
              f"实际：{engine11.get_dimension(DIM_METHODOLOGY)}")
        check("附加.3 get_dimension(unknown) 返回 None",
              engine11.get_dimension("unknown") is None,
              f"实际：{engine11.get_dimension('unknown')}")

        # 隐式反馈：删减 > 新增 → 负信号
        engine12 = TasteEngine(storage_dir=fresh_dir())
        engine12.load_model()
        engine12.update_from_feedback("implicit", {
            "diff": {"added": 10, "deleted": 50},
            "topic_features": {DIM_NOVELTY: 0.8, DIM_METHODOLOGY: [0.7, 0.5, 0.6],
                                DIM_THEORETICAL_DEPTH: 0.7, DIM_INTERDISCIPLINARITY: 0.5,
                                DIM_RISK_APPETITE: 0.5},
            "example_id": "implicit_001",
        })
        check("附加.4 隐式负反馈记录负样本",
              "implicit_001" in engine12.model["negative_examples"],
              f"实际：{engine12.model['negative_examples']}")

        # comfort_zone 添加
        engine13 = TasteEngine(storage_dir=fresh_dir())
        engine13.load_model()
        engine13.update_interdisciplinarity(0.6, "量子信息", 0)
        check("附加.5 comfort_zone 已添加",
              "量子信息" in engine13.model["dimensions"][DIM_INTERDISCIPLINARITY]["comfort_zones"],
              f"实际：{engine13.model['dimensions'][DIM_INTERDISCIPLINARITY]['comfort_zones']}")

    finally:
        # 清理临时目录
        _shutil.rmtree(tmp_root, ignore_errors=True)

    # ------------------------------------------------------------------
    # 输出结果
    # ------------------------------------------------------------------
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    total = len(results)

    print(f"\n{'=' * 60}")
    print(f"taste_engine 自检：{passed}/{total} 通过" +
          (f"，{failed} 失败" if failed else ""))
    print(f"{'=' * 60}")

    for name, ok, detail in results:
        icon = "✓" if ok else "✗"
        line = f"  {icon} {name}"
        if detail and not ok:
            line += f" — {detail}"
        print(line)

    if failed:
        print(f"\n⚠ {failed} 项失败")
    else:
        print(f"\n✓ 全部通过（{total} 项）")

    return failed == 0


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--export":
        # 导出当前品味画像
        engine = TasteEngine()
        engine.load_model()
        print(engine.export_profile())
    elif len(sys.argv) > 1 and sys.argv[1] == "--show":
        # 显示模型 JSON
        engine = TasteEngine()
        model = engine.load_model()
        import json
        print(json.dumps(model, ensure_ascii=False, indent=2))
    else:
        # 默认运行自检
        ok = _self_check()
        sys.exit(0 if ok else 1)
