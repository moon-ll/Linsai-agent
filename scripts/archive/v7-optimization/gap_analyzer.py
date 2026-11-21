#!/usr/bin/env python3
"""研究缺口分析器 — 课题凝练阶段的核心模块。

用途：
    从积累的文献与知识库内容中识别研究缺口，分析"已知 vs 未知"，
    产出结构化缺口报告，为 Wave 3 课题生成提供输入。

    位于研究管线"课题凝练"阶段：
        ... → 01_review（文献调研） → 02_topic（课题凝练） → 03_design ...
    本模块的产物 gap-report.json 保存在 {proposal_dir}/02_topic/ 下。

核心流程：
    1. scan_coverage()   扫描知识库（wiki 概念/方法）与文献池，构建覆盖图
    2. identify_gaps()   从覆盖图识别缺口（概念/方法/理论/实验四类）
    3. score_gaps()      按新颖性、可行性、方向对齐度评分排序
    4. analyze()         编排上述步骤，持久化报告，注册血缘

缺口评分公式：
    priority = 0.4 * novelty + 0.3 * feasibility + 0.3 * direction_alignment
    （各分项 0-1，priority 越高越重要）

研究方向维度（来自用户画像 T1-T5）：
    T1 量子几何：8 维（Berry曲率、量子度规、拓扑、简并性、维度、材料类别、探测方法、温度）
    T2 能谷电子学：9 维（能谷极化、选择定则、扭曲角等）
    T3 能带动力学：7 维（Floquet准能带、能带动力学等）
    T4 多序参量：6 维（超导、CDW、磁性、Mott、激子、铁电）
    T5 反演方法学：4 维（贝叶斯反演、神经网络反演、参数估计、不确定性量化）

用法示例：
    >>> from pathlib import Path
    >>> from gap_analyzer import GapAnalyzer
    >>> directions = [{"id": "T1", "name": "量子几何"}]
    >>> analyzer = GapAnalyzer(Path("/data/proposals/T1"), research_directions=directions)
    >>> report = analyzer.analyze()
    >>> print(report["summary"]["total_gaps"])
    >>> md = analyzer.export_gap_report("markdown")

命令行自检：
    python3 scripts/gap_analyzer.py --self-check

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

__all__ = [
    "GapAnalyzer",
    "GAP_TYPES",
    "GAP_TYPE_LABELS",
    "DIRECTION_DIMENSIONS",
    "METHOD_KEYWORDS",
]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 缺口类型
GAP_TYPES = ("conceptual", "methodological", "empirical", "theoretical")

GAP_TYPE_LABELS: Dict[str, str] = {
    "conceptual": "概念缺口",
    "methodological": "方法缺口",
    "empirical": "实验缺口",
    "theoretical": "理论缺口",
}

# 研究方向维度定义（T1-T5）
# 每个维度含 name（中文名）与 keywords（用于知识库检索匹配的关键词列表）
DIRECTION_DIMENSIONS: Dict[str, Dict[str, Any]] = {
    "T1": {
        "name": "量子几何",
        "dimensions": [
            {"name": "Berry曲率", "keywords": ["Berry曲率", "Berry curvature", "几何相位"]},
            {"name": "量子度规", "keywords": ["量子度规", "quantum metric", "Fubini-Study"]},
            {"name": "拓扑", "keywords": ["拓扑", "topology", "拓扑不变量", "Chern"]},
            {"name": "简并性", "keywords": ["简并", "degeneracy", "能带简并"]},
            {"name": "维度", "keywords": ["维度", "dimensionality", "二维", "三维"]},
            {"name": "材料类别", "keywords": ["材料", "material", "拓扑绝缘体", "Weyl"]},
            {"name": "探测方法", "keywords": ["探测", "probe", "HHG", "光电"]},
            {"name": "温度", "keywords": ["温度", "temperature", "低温", "室温"]},
        ],
    },
    "T2": {
        "name": "能谷电子学",
        "dimensions": [
            {"name": "能谷极化", "keywords": ["能谷极化", "valley polarization"]},
            {"name": "选择定则", "keywords": ["选择定则", "selection rules", "光学选择"]},
            {"name": "扭曲角", "keywords": ["扭曲角", "twist angle", "莫尔"]},
            {"name": "能谷-声子耦合", "keywords": ["能谷声子", "valley phonon", "声子"]},
            {"name": "能谷霍尔效应", "keywords": ["能谷霍尔", "valley Hall"]},
            {"name": "Berry曲率(能谷)", "keywords": ["Berry曲率", "Berry curvature", "能谷"]},
            {"name": "光极化", "keywords": ["光极化", "light polarization", "圆偏振"]},
            {"name": "能谷寿命", "keywords": ["能谷寿命", "valley lifetime", "弛豫"]},
            {"name": "层间耦合", "keywords": ["层间耦合", "interlayer coupling"]},
        ],
    },
    "T3": {
        "name": "能带动力学",
        "dimensions": [
            {"name": "Floquet准能带", "keywords": ["Floquet", "准能带", "quasi-energy"]},
            {"name": "能带动力学", "keywords": ["能带动力学", "band dynamics"]},
            {"name": "准能量", "keywords": ["准能量", "quasienergy"]},
            {"name": "光子修饰", "keywords": ["光子修饰", "photon dressing", "缀饰"]},
            {"name": "拓扑变化", "keywords": ["拓扑变化", "topology change"]},
            {"name": "驱动相变", "keywords": ["驱动相变", "driven phase transition"]},
            {"name": "非平衡分布", "keywords": ["非平衡", "non-equilibrium", "分布"]},
        ],
    },
    "T4": {
        "name": "多序参量",
        "dimensions": [
            {"name": "超导", "keywords": ["超导", "superconductivity", "SC"]},
            {"name": "电荷密度波", "keywords": ["电荷密度波", "CDW", "charge density wave"]},
            {"name": "磁性", "keywords": ["磁性", "magnetism", "反铁磁"]},
            {"name": "Mott绝缘体", "keywords": ["Mott", "绝缘体", "Hubbard"]},
            {"name": "激子", "keywords": ["激子", "exciton"]},
            {"name": "铁电", "keywords": ["铁电", "ferroelectric"]},
        ],
    },
    "T5": {
        "name": "反演方法学",
        "dimensions": [
            {"name": "贝叶斯反演", "keywords": ["贝叶斯", "Bayesian", "反演"]},
            {"name": "神经网络反演", "keywords": ["神经网络", "neural network", "NN", "深度学习"]},
            {"name": "参数估计", "keywords": ["参数估计", "parameter estimation"]},
            {"name": "不确定性量化", "keywords": ["不确定性", "uncertainty quantification"]},
        ],
    },
}

# 方法关键词：用于从论文标题/tldr 中检测方法覆盖
METHOD_KEYWORDS: Dict[str, List[str]] = {
    "TDDFT": ["TDDFT", "含时密度泛函"],
    "Floquet理论": ["Floquet", "弗洛凯"],
    "半导体布洛赫方程": ["semiconductor Bloch", "SBE", "布洛赫方程"],
    "非平衡Green函数": ["NEGF", "non-equilibrium Green", "Keldysh"],
    "密度泛函理论": ["DFT", "密度泛函"],
    "紧束缚模型": ["tight-binding", "紧束缚"],
    "k·p理论": ["k.p", "k·p"],
    "贝叶斯推断": ["Bayesian", "贝叶斯"],
    "神经网络": ["neural network", "神经网络", "deep learning"],
    "群速度重建": ["group velocity", "群速度"],
    "量子主方程": ["master equation", "主方程"],
    "Wigner分布": ["Wigner", "维格纳"],
}

# 各研究方向期望具备的理论方法（用于检测理论缺口）
_EXPECTED_METHODS: Dict[str, List[str]] = {
    "T1": ["TDDFT", "紧束缚模型", "密度泛函理论"],
    "T2": ["紧束缚模型", "k·p理论", "半导体布洛赫方程"],
    "T3": ["Floquet理论", "半导体布洛赫方程", "非平衡Green函数"],
    "T4": ["密度泛函理论", "紧束缚模型", "量子主方程"],
    "T5": ["贝叶斯推断", "神经网络"],
}


# ---------------------------------------------------------------------------
# GapAnalyzer
# ---------------------------------------------------------------------------

class GapAnalyzer:
    """研究缺口分析器。

    扫描知识库与文献池，识别"已知 vs 未知"的研究缺口，
    产出结构化缺口报告，为课题生成（Wave 3）提供输入。

    线程安全：所有写操作通过 common.file_lock（fcntl.flock 跨进程锁）保护，
    锁键基于 proposal_dir 路径哈希，不同 proposal 互不阻塞。
    """

    def __init__(
        self,
        proposal_dir: Path | str,
        research_directions: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """初始化缺口分析器。

        Args:
            proposal_dir: proposal 根目录（Path 或字符串），
                          缺口报告保存于其下的 02_topic/gap-report.json。
            research_directions: 研究方向列表，每项为 {"id": "T1", "name": "量子几何"}。
                                 为 None 时视为空列表（仅检测方法/实验缺口）。
        """
        self.proposal_dir = Path(proposal_dir)
        self.topic_dir = self.proposal_dir / "02_topic"
        self.report_path = self.topic_dir / "gap-report.json"
        self.research_directions: List[Dict[str, Any]] = research_directions or []

        # 跨进程锁键：基于 proposal_dir 绝对路径哈希，避免不同 proposal 互相阻塞
        digest = hashlib.md5(
            str(self.proposal_dir.resolve()).encode("utf-8")
        ).hexdigest()[:12]
        self._lock_name = f"gap-{digest}"

        # 懒加载的模块缓存（None = 尚未加载）
        self._kb_wiki = None
        self._kb_index = None
        self._paper_pool = None
        self._lineage_tracker = None

    # ------------------------------------------------------------------
    # 模块懒加载
    # ------------------------------------------------------------------

    def _load_kb_wiki(self):
        """懒加载 kb_wiki 模块，返回模块对象或 None。"""
        if self._kb_wiki is None:
            mod = lazy_load("kb_wiki")
            self._kb_wiki = mod
        return self._kb_wiki

    def _load_kb_index(self):
        """懒加载 kb_index 模块，注入桩依赖（门面可能未加载），返回模块对象或 None。"""
        if self._kb_index is None:
            mod = lazy_load("kb_index")
            if mod is not None:
                # 门面 knowledge_base 未加载时，注入桩依赖使 search() 可正常调用
                if getattr(mod, "_load_aliases", None) is None:
                    mod._load_aliases = lambda: {}
                if getattr(mod, "_ensure_dirs", None) is None:
                    mod._ensure_dirs = lambda: None
                if getattr(mod, "log_growth", None) is None:
                    mod.log_growth = lambda *a, **kw: None
                if getattr(mod, "_log", None) is None:
                    mod._log = None
            self._kb_index = mod
        return self._kb_index

    def _load_paper_pool(self):
        """懒加载 paper_pool 模块，返回模块对象或 None。"""
        if self._paper_pool is None:
            self._paper_pool = lazy_load("paper_pool")
        return self._paper_pool

    def _load_lineage_tracker(self):
        """懒加载 lineage_tracker 模块，返回模块对象或 None。"""
        if self._lineage_tracker is None:
            self._lineage_tracker = lazy_load("lineage_tracker")
        return self._lineage_tracker

    # ------------------------------------------------------------------
    # 覆盖度扫描
    # ------------------------------------------------------------------

    def scan_coverage(self) -> Dict[str, Any]:
        """扫描知识库与文献池，构建覆盖图。

        Returns:
            覆盖图字典，结构：
            {
              "concepts_covered": [{"name", "wiki_path", "confidence", "growth_stage"}, ...],
              "concepts_missing": ["拓扑", "简并性", ...],
              "methods_established": [{"name", "papers", "maturity"}, ...],
              "methods_emerging": [{"name", "papers", "maturity"}, ...],
              "papers_analyzed": int,
              "last_updated": "2026-07-26T..."
            }
        """
        concepts_covered: List[Dict[str, Any]] = []
        concepts_missing: List[str] = []
        methods_established: List[Dict[str, Any]] = []
        methods_emerging: List[Dict[str, Any]] = []
        papers_analyzed = 0

        # 1. 扫描 wiki 概念页面
        kb_wiki = self._load_kb_wiki()
        if kb_wiki is not None:
            try:
                for page in kb_wiki.list_wiki_pages("concepts"):
                    concepts_covered.append({
                        "name": page.get("title", ""),
                        "wiki_path": page.get("path", ""),
                        "confidence": page.get("confidence", 0.0),
                        "growth_stage": page.get("growth_stage", ""),
                    })
            except Exception:
                pass

            # 2. 扫描 wiki 方法页面
            try:
                for page in kb_wiki.list_wiki_pages("methods"):
                    stage = page.get("growth_stage", "")
                    entry = {
                        "name": page.get("title", ""),
                        "wiki_path": page.get("path", ""),
                        "papers": [],
                        "maturity": "high" if stage == "mature" else "low",
                        "growth_stage": stage,
                    }
                    if entry["maturity"] == "high":
                        methods_established.append(entry)
                    else:
                        methods_emerging.append(entry)
            except Exception:
                pass

        # 3. 扫描论文池
        pp = self._load_paper_pool()
        if pp is not None:
            try:
                pool_data = pp.get_pool()
                papers_analyzed = pool_data.get("total", 0)

                # 从论文标题/tldr 检测方法关键词
                method_paper_map: Dict[str, List[str]] = {}
                for paper in pool_data.get("papers", []):
                    text = (paper.get("title", "") + " " + paper.get("tldr", "")).lower()
                    pid = paper.get("arxiv_id", paper.get("title", ""))
                    for method_name, keywords in METHOD_KEYWORDS.items():
                        if any(kw.lower() in text for kw in keywords):
                            method_paper_map.setdefault(method_name, []).append(pid)

                # 合并论文检测到的方法（与 wiki 方法去重）
                existing_names = {m["name"] for m in methods_established + methods_emerging}
                for method_name, paper_ids in method_paper_map.items():
                    if not self._method_exists(method_name, methods_established, methods_emerging):
                        maturity = "high" if len(paper_ids) >= 3 else "low"
                        entry = {
                            "name": method_name,
                            "papers": paper_ids,
                            "maturity": maturity,
                        }
                        if maturity == "high":
                            methods_established.append(entry)
                        else:
                            methods_emerging.append(entry)
            except Exception:
                pass

        # 4. 检测缺失概念（对照研究方向维度）
        covered_names_lower = {c["name"].lower() for c in concepts_covered}
        kb_index = self._load_kb_index()

        for direction in self.research_directions:
            dir_id = direction.get("id", "")
            dims = DIRECTION_DIMENSIONS.get(dir_id, {}).get("dimensions", [])
            for dim in dims:
                found = False
                for kw in dim["keywords"]:
                    # 检查已覆盖概念名
                    if any(kw.lower() in cn for cn in covered_names_lower):
                        found = True
                        break
                    # 检查知识库全文检索
                    if kb_index is not None:
                        try:
                            results = kb_index.search(kw, top_k=1)
                            if results.get("total", 0) > 0:
                                found = True
                                break
                        except Exception:
                            pass
                if not found and dim["name"] not in concepts_missing:
                    concepts_missing.append(dim["name"])

        return {
            "concepts_covered": concepts_covered,
            "concepts_missing": concepts_missing,
            "methods_established": methods_established,
            "methods_emerging": methods_emerging,
            "papers_analyzed": papers_analyzed,
            "last_updated": now_utc(),
        }

    # ------------------------------------------------------------------
    # 缺口识别
    # ------------------------------------------------------------------

    def identify_gaps(self, coverage: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从覆盖图识别研究缺口。

        四类缺口：
          - conceptual（概念缺口）：研究方向维度在知识库中未覆盖
          - methodological（方法缺口）：新兴方法成熟度不足
          - theoretical（理论缺口）：研究方向缺少期望的理论方法
          - empirical（实验缺口）：文献池为空，缺少实证基础

        Args:
            coverage: scan_coverage() 返回的覆盖图

        Returns:
            缺口列表（未评分，priority_score 等字段为 0.0 占位）
        """
        gaps: List[Dict[str, Any]] = []
        gap_counter = 0

        missing_concepts = coverage.get("concepts_missing", [])
        covered_names_lower = {
            c["name"].lower() for c in coverage.get("concepts_covered", [])
        }

        # 1. 概念缺口：研究方向维度在知识库中未覆盖
        for direction in self.research_directions:
            dir_id = direction.get("id", "")
            dir_info = DIRECTION_DIMENSIONS.get(dir_id, {})
            dir_name = dir_info.get("name", dir_id)
            dims = dir_info.get("dimensions", [])
            for dim in dims:
                if dim["name"] in missing_concepts:
                    gap_counter += 1
                    gaps.append({
                        "gap_id": f"gap_{gap_counter:03d}",
                        "type": "conceptual",
                        "description": (
                            f"现有知识库未充分覆盖{dir_name}方向的关键维度：{dim['name']}"
                        ),
                        "evidence": [{
                            "source": "知识库扫描",
                            "note": (
                                f"未在 wiki/concepts 中找到与"
                                f"'{dim['name']}'"
                                f"（{', '.join(dim['keywords'][:3])}）相关的成熟概念页面"
                            ),
                        }],
                        "related_direction": dir_id,
                        "priority_score": 0.0,
                        "novelty_score": 0.0,
                        "feasibility_score": 0.0,
                        "direction_alignment": 0.0,
                        "suggested_approach": (
                            f"系统梳理{dim['name']}在{dir_name}中的作用，"
                            f"建立 wiki 概念页面并关联已有知识"
                        ),
                    })

        # 2. 方法缺口：新兴方法成熟度不足
        for method in coverage.get("methods_emerging", []):
            gap_counter += 1
            gaps.append({
                "gap_id": f"gap_{gap_counter:03d}",
                "type": "methodological",
                "description": f"方法'{method['name']}'尚处于新兴阶段，成熟度不足",
                "evidence": [{
                    "source": method.get("wiki_path", "论文池扫描"),
                    "note": (
                        f"该方法关联论文 {len(method.get('papers', []))} 篇，"
                        f"成熟度评级为低"
                    ),
                }],
                "related_direction": "",
                "priority_score": 0.0,
                "novelty_score": 0.0,
                "feasibility_score": 0.0,
                "direction_alignment": 0.0,
                "suggested_approach": (
                    f"深化对{method['name']}的研究，"
                    f"补充理论推导与数值验证，提升至成熟方法"
                ),
            })

        # 3. 理论缺口：研究方向缺少期望的理论方法
        for direction in self.research_directions:
            dir_id = direction.get("id", "")
            dir_name = DIRECTION_DIMENSIONS.get(dir_id, {}).get("name", dir_id)
            expected = _EXPECTED_METHODS.get(dir_id, [])
            for method_name in expected:
                if not self._method_exists(
                    method_name,
                    coverage.get("methods_established", []),
                    coverage.get("methods_emerging", []),
                ):
                    gap_counter += 1
                    gaps.append({
                        "gap_id": f"gap_{gap_counter:03d}",
                        "type": "theoretical",
                        "description": f"{dir_name}方向缺少成熟的理论方法：{method_name}",
                        "evidence": [{
                            "source": "方法库扫描",
                            "note": f"既无成熟方法也无新兴方法记录涉及'{method_name}'",
                        }],
                        "related_direction": dir_id,
                        "priority_score": 0.0,
                        "novelty_score": 0.0,
                        "feasibility_score": 0.0,
                        "direction_alignment": 0.0,
                        "suggested_approach": (
                            f"引入{method_name}用于{dir_name}方向的理论分析，"
                            f"建立方法 wiki 页面"
                        ),
                    })

        # 4. 实验缺口：文献池为空
        if coverage.get("papers_analyzed", 0) == 0 and self.research_directions:
            gap_counter += 1
            gaps.append({
                "gap_id": f"gap_{gap_counter:03d}",
                "type": "empirical",
                "description": "文献池为空，缺少实证基础",
                "evidence": [{
                    "source": "论文池扫描",
                    "note": "paper-pool 中无任何候选论文",
                }],
                "related_direction": "",
                "priority_score": 0.0,
                "novelty_score": 0.0,
                "feasibility_score": 0.0,
                "direction_alignment": 0.0,
                "suggested_approach": "从 arXiv 等来源导入研究方向相关的候选论文",
            })

        return gaps

    # ------------------------------------------------------------------
    # 缺口评分
    # ------------------------------------------------------------------

    def score_gaps(self, gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对缺口评分并排序。

        评分公式：
            priority = 0.4 * novelty + 0.3 * feasibility + 0.3 * direction_alignment

        - novelty（新颖性）：概念缺口 0.9 / 理论缺口 0.7 / 方法缺口 0.6 / 实验缺口 0.4
        - feasibility（可行性）：实验缺口 0.8 / 概念缺口 0.7 / 理论缺口 0.6 / 方法缺口 0.5
        - direction_alignment（方向对齐）：关联方向在用户画像中 0.9 / 关联但不在 0.5 / 无关联 0.4

        Args:
            gaps: identify_gaps() 返回的缺口列表

        Returns:
            评分后的缺口列表，按 priority_score 降序排列，gap_id 重新编号
        """
        scored: List[Dict[str, Any]] = []
        direction_ids = {d.get("id", "") for d in self.research_directions}

        for gap in gaps:
            g = dict(gap)

            # 新颖性评分
            if g["type"] == "conceptual":
                g["novelty_score"] = 0.9
            elif g["type"] == "theoretical":
                g["novelty_score"] = 0.7
            elif g["type"] == "methodological":
                g["novelty_score"] = 0.6
            else:  # empirical
                g["novelty_score"] = 0.4

            # 可行性评分
            if g["type"] == "empirical":
                g["feasibility_score"] = 0.8
            elif g["type"] == "conceptual":
                g["feasibility_score"] = 0.7
            elif g["type"] == "theoretical":
                g["feasibility_score"] = 0.6
            else:  # methodological
                g["feasibility_score"] = 0.5

            # 方向对齐评分
            dir_id = g.get("related_direction", "")
            if dir_id and dir_id in direction_ids:
                g["direction_alignment"] = 0.9
            elif dir_id:
                g["direction_alignment"] = 0.5
            else:
                g["direction_alignment"] = 0.4

            # 优先级 = 0.4*novelty + 0.3*feasibility + 0.3*direction_alignment
            g["priority_score"] = round(
                0.4 * g["novelty_score"]
                + 0.3 * g["feasibility_score"]
                + 0.3 * g["direction_alignment"],
                4,
            )

            scored.append(g)

        # 按 priority_score 降序排列
        scored.sort(key=lambda x: x["priority_score"], reverse=True)

        # 重新编号 gap_id
        for i, g in enumerate(scored, 1):
            g["gap_id"] = f"gap_{i:03d}"

        return scored

    # ------------------------------------------------------------------
    # 方向对比
    # ------------------------------------------------------------------

    def compare_with_direction(
        self, gaps: List[Dict[str, Any]], direction: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """按研究方向过滤并重新排序缺口。

        过滤逻辑：
          - related_direction 匹配该方向的缺口 → 保留，方向对齐度提升至 1.0
          - related_direction 为空的通用缺口 → 保留，方向对齐度 0.5
          - related_direction 指向其他方向的缺口 → 排除

        重新评分后按 priority_score 降序排列。

        Args:
            gaps: 已评分的缺口列表
            direction: {"id": "T1", "name": "量子几何"}

        Returns:
            过滤并重新排序后的缺口列表
        """
        dir_id = direction.get("id", "")

        filtered: List[Dict[str, Any]] = []
        for gap in gaps:
            g = dict(gap)
            related = g.get("related_direction", "")

            if related == dir_id:
                # 直接关联：方向对齐度提升至 1.0
                g["direction_alignment"] = 1.0
                g["priority_score"] = round(
                    0.4 * g.get("novelty_score", 0.5)
                    + 0.3 * g.get("feasibility_score", 0.5)
                    + 0.3 * 1.0,
                    4,
                )
                filtered.append(g)
            elif not related:
                # 通用缺口：方向对齐度 0.5
                g["direction_alignment"] = 0.5
                g["priority_score"] = round(
                    0.4 * g.get("novelty_score", 0.5)
                    + 0.3 * g.get("feasibility_score", 0.5)
                    + 0.3 * 0.5,
                    4,
                )
                filtered.append(g)
            # related 指向其他方向 → 排除

        # 按优先级降序
        filtered.sort(key=lambda x: x["priority_score"], reverse=True)

        # 重新编号
        for i, g in enumerate(filtered, 1):
            g["gap_id"] = f"gap_{i:03d}"

        return filtered

    # ------------------------------------------------------------------
    # 完整分析
    # ------------------------------------------------------------------

    def analyze(self) -> Dict[str, Any]:
        """执行完整缺口分析，返回结构化报告。

        流程：scan_coverage → identify_gaps → score_gaps → 持久化 → 注册血缘

        Returns:
            缺口报告字典，包含 coverage、gaps、summary
        """
        coverage = self.scan_coverage()
        gaps = self.identify_gaps(coverage)
        gaps = self.score_gaps(gaps)

        # 按类型统计
        by_type: Dict[str, int] = {t: 0 for t in GAP_TYPES}
        for g in gaps:
            t = g.get("type", "")
            if t in by_type:
                by_type[t] += 1

        # 按方向统计
        by_direction: Dict[str, int] = {}
        for d in self.research_directions:
            did = d.get("id", "")
            by_direction[did] = sum(
                1 for g in gaps if g.get("related_direction") == did
            )

        avg_priority = (
            round(sum(g["priority_score"] for g in gaps) / len(gaps), 4)
            if gaps
            else 0.0
        )

        report: Dict[str, Any] = {
            "proposal_dir": str(self.proposal_dir),
            "generated_at": now_utc(),
            "coverage": coverage,
            "gaps": gaps,
            "summary": {
                "total_gaps": len(gaps),
                "by_type": by_type,
                "by_direction": by_direction,
                "avg_priority": avg_priority,
            },
        }

        self._save_report(report)
        self._register_lineage(report)
        return report

    # ------------------------------------------------------------------
    # 报告读取与导出
    # ------------------------------------------------------------------

    def get_gap_report(self) -> Optional[Dict[str, Any]]:
        """加载已保存的缺口报告；不存在返回 None。"""
        if not self.report_path.exists():
            return None
        return load_json(self.report_path, None)

    def export_gap_report(self, format: str = "markdown") -> str:
        """导出缺口报告为 Markdown 或 JSON 字符串。

        Args:
            format: "markdown" 或 "json"

        Returns:
            格式化的报告字符串
        """
        report = self.get_gap_report()

        if report is None:
            if format == "json":
                return "{}"
            return "# 研究缺口报告\n\n（暂无报告，请先运行 analyze()）\n"

        if format == "json":
            return json.dumps(report, ensure_ascii=False, indent=2)

        # Markdown 格式
        lines: List[str] = []
        lines.append("# 研究缺口报告\n")
        lines.append(f"**生成时间**：{report.get('generated_at', '')}\n")
        lines.append(f"**Proposal 目录**：{report.get('proposal_dir', '')}\n")

        # 摘要
        summary = report.get("summary", {})
        lines.append("## 摘要\n")
        lines.append(f"- 缺口总数：{summary.get('total_gaps', 0)}")
        by_type = summary.get("by_type", {})
        type_parts = [
            f"{GAP_TYPE_LABELS.get(t, t)} {by_type.get(t, 0)}"
            for t in GAP_TYPES
            if by_type.get(t, 0) > 0
        ]
        if type_parts:
            lines.append(f"- 按类型：{('、').join(type_parts)}")
        lines.append(f"- 平均优先级：{summary.get('avg_priority', 0)}\n")

        # 知识覆盖
        coverage = report.get("coverage", {})
        lines.append("## 知识覆盖\n")
        lines.append(f"- 已覆盖概念：{len(coverage.get('concepts_covered', []))} 个")
        lines.append(f"- 缺失概念：{len(coverage.get('concepts_missing', []))} 个")
        lines.append(f"- 成熟方法：{len(coverage.get('methods_established', []))} 个")
        lines.append(f"- 新兴方法：{len(coverage.get('methods_emerging', []))} 个")
        lines.append(f"- 已分析论文：{coverage.get('papers_analyzed', 0)} 篇\n")

        if coverage.get("concepts_missing"):
            lines.append("### 缺失概念\n")
            for c in coverage["concepts_missing"]:
                lines.append(f"- {c}")
            lines.append("")

        # 缺口列表
        lines.append("## 缺口列表\n")
        for gap in report.get("gaps", []):
            lines.append(
                f"### {gap['gap_id']}：{GAP_TYPE_LABELS.get(gap['type'], gap['type'])}"
            )
            lines.append(f"\n{gap['description']}\n")
            lines.append(f"- **优先级**：{gap['priority_score']}")
            lines.append(f"- **新颖性**：{gap['novelty_score']}")
            lines.append(f"- **可行性**：{gap['feasibility_score']}")
            if gap.get("related_direction"):
                lines.append(f"- **关联方向**：{gap['related_direction']}")
            lines.append(f"- **建议路径**：{gap.get('suggested_approach', '')}")
            if gap.get("evidence"):
                lines.append("- **证据**：")
                for ev in gap["evidence"]:
                    lines.append(f"  - [{ev.get('source', '')}] {ev.get('note', '')}")
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _save_report(self, report: Dict[str, Any]) -> None:
        """保存缺口报告到 02_topic/gap-report.json（原子写入 + 文件锁）。"""
        self.topic_dir.mkdir(parents=True, exist_ok=True)
        with file_lock(self._lock_name):
            save_json(self.report_path, report)

    def _register_lineage(self, report: Dict[str, Any]) -> None:
        """向血缘追踪器注册缺口分析产物（可选，失败不阻塞）。"""
        tracker_mod = self._load_lineage_tracker()
        if tracker_mod is None:
            return
        try:
            tracker = tracker_mod.LineageTracker(self.proposal_dir)
            tracker.register_node(
                "gap_report",
                "gap_analysis",
                "研究缺口报告",
                stage=2,
            )
            for direction in self.research_directions:
                dir_id = direction.get("id", "")
                if dir_id:
                    tracker.register_node(
                        dir_id,
                        "research_direction",
                        direction.get("name", dir_id),
                    )
                    tracker.add_edge(
                        "gap_report", dir_id, "belongs_to",
                        f"缺口分析覆盖{dir_id}方向",
                    )
        except Exception:
            pass

    @staticmethod
    def _method_exists(
        method_name: str,
        established: List[Dict[str, Any]],
        emerging: List[Dict[str, Any]],
    ) -> bool:
        """检查方法是否已存在（含模糊匹配：子串包含即视为匹配）。"""
        all_names = [m.get("name", "") for m in established + emerging]
        for name in all_names:
            if not name:
                continue
            if (
                method_name == name
                or method_name in name
                or name in method_name
            ):
                return True
        return False


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """自检：11 个检查点，使用临时目录与 mock 数据隔离测试。

    覆盖：
      1. 初始化
      2. 覆盖度扫描
      3. 缺口识别
      4. 缺口评分（验证公式）
      5. 方向对比
      6. 报告持久化（保存 + 重新加载）
      7. Markdown 导出
      8. JSON 导出
      9. 空知识库处理
      10. 缺失方向处理
      11. 原子写入 + 文件锁
    """
    import shutil
    import tempfile

    print("=" * 50)
    print("◐ gap_analyzer 自检")
    print("=" * 50)

    tmp = Path(tempfile.mkdtemp(prefix="gap_analyzer_test_"))
    try:
        # ── 准备 mock 知识库 ──
        tmp_kb = tmp / "knowledge"
        (tmp_kb / "wiki" / "concepts").mkdir(parents=True, exist_ok=True)
        (tmp_kb / "wiki" / "methods").mkdir(parents=True, exist_ok=True)

        # 概念页面：Berry曲率（mature）、量子度规（growing）
        (tmp_kb / "wiki" / "concepts" / "Berry曲率.md").write_text(
            '---\ntitle: "Berry曲率"\ntype: "concepts"\n'
            'growth_stage: "mature"\nconfidence: 0.9\ntags: ["Berry"]\n---\n'
            "# Berry曲率\n几何相位核心概念。\n",
            encoding="utf-8",
        )
        (tmp_kb / "wiki" / "concepts" / "量子度规.md").write_text(
            '---\ntitle: "量子度规"\ntype: "concepts"\n'
            'growth_stage: "growing"\nconfidence: 0.6\ntags: ["metric"]\n---\n'
            "# 量子度规\nFubini-Study度规。\n",
            encoding="utf-8",
        )
        # 方法页面：TDDFT（mature）、神经网络反演（seedling）
        (tmp_kb / "wiki" / "methods" / "TDDFT.md").write_text(
            '---\ntitle: "TDDFT"\ntype: "methods"\n'
            'growth_stage: "mature"\nconfidence: 0.9\ntags: ["DFT"]\n---\n'
            "# TDDFT\n含时密度泛函理论。\n",
            encoding="utf-8",
        )
        (tmp_kb / "wiki" / "methods" / "神经网络反演.md").write_text(
            '---\ntitle: "神经网络反演"\ntype: "methods"\n'
            'growth_stage: "seedling"\nconfidence: 0.3\ntags: ["NN"]\n---\n'
            "# 神经网络反演\n深度学习反演方法。\n",
            encoding="utf-8",
        )

        directions = [
            {"id": "T1", "name": "量子几何"},
            {"id": "T5", "name": "反演方法学"},
        ]
        proposal_dir = tmp / "T1_proposal"
        analyzer = GapAnalyzer(proposal_dir, research_directions=directions)

        # Patch kb_wiki 指向临时目录
        kb_wiki_mod = analyzer._load_kb_wiki()
        assert kb_wiki_mod is not None, "kb_wiki 模块应加载成功"
        _orig_kb_wiki = {
            "KNOWLEDGE_DIR": kb_wiki_mod.KNOWLEDGE_DIR,
            "WIKI_DIR": kb_wiki_mod.WIKI_DIR,
        }
        kb_wiki_mod.KNOWLEDGE_DIR = tmp_kb
        kb_wiki_mod.WIKI_DIR = tmp_kb / "wiki"

        # Mock kb_index（返回空搜索结果，使缺失检测仅依赖概念名匹配）
        class _MockKbIndex:
            def search(self, query, **kwargs):
                return {"results": [], "total": 0, "offset": 0, "limit": kwargs.get("top_k", 3)}

        analyzer._kb_index = _MockKbIndex()

        # Mock paper_pool
        class _MockPaperPool:
            def get_pool(self):
                return {
                    "total": 3,
                    "by_status": {"unseen": 1, "viewed": 1, "archived": 1},
                    "papers": [
                        {"arxiv_id": "2401.001", "title": "TDDFT simulation of HHG",
                         "tldr": "", "score": 0.9},
                        {"arxiv_id": "2401.002", "title": "Bayesian approach to band",
                         "tldr": "贝叶斯反演方法", "score": 0.7},
                        {"arxiv_id": "2401.003", "title": "Floquet topology in solids",
                         "tldr": "", "score": 0.5},
                    ],
                }

        analyzer._paper_pool = _MockPaperPool()

        # ── [1/11] 初始化 ──
        print("\n[1/11] 初始化...")
        assert analyzer.proposal_dir == proposal_dir
        assert analyzer.topic_dir == proposal_dir / "02_topic"
        assert analyzer.report_path == proposal_dir / "02_topic" / "gap-report.json"
        assert analyzer._lock_name.startswith("gap-")
        assert len(analyzer.research_directions) == 2
        print(f"  proposal_dir: {analyzer.proposal_dir}")
        print(f"  report_path: {analyzer.report_path}")
        print(f"  lock_name: {analyzer._lock_name}")
        print(f"  directions: {[d['id'] for d in analyzer.research_directions]}")
        print("  ✓ 初始化字段完整")

        # ── [2/11] 覆盖度扫描 ──
        print("\n[2/11] 覆盖度扫描...")
        coverage = analyzer.scan_coverage()
        print(f"  已覆盖概念: {len(coverage['concepts_covered'])} 个")
        print(f"  缺失概念: {len(coverage['concepts_missing'])} 个")
        print(f"  成熟方法: {len(coverage['methods_established'])} 个")
        print(f"  新兴方法: {len(coverage['methods_emerging'])} 个")
        print(f"  已分析论文: {coverage['papers_analyzed']} 篇")
        # 2 个 wiki 概念
        assert len(coverage["concepts_covered"]) == 2, (
            f"期望 2 个已覆盖概念，实际 {len(coverage['concepts_covered'])}"
        )
        covered_names = {c["name"] for c in coverage["concepts_covered"]}
        assert "Berry曲率" in covered_names
        assert "量子度规" in covered_names
        # TDDFT 来自 wiki（mature → established），贝叶斯推断和 Floquet理论 来自论文检测
        # 神经网络反演 来自 wiki（seedling → emerging）
        assert len(coverage["methods_established"]) >= 1, "应有至少 1 个成熟方法"
        established_names = {m["name"] for m in coverage["methods_established"]}
        assert "TDDFT" in established_names, "TDDFT 应为成熟方法"
        assert coverage["papers_analyzed"] == 3, (
            f"期望 3 篇论文，实际 {coverage['papers_analyzed']}"
        )
        # 缺失概念应包含 T1 中未覆盖的维度（拓扑、简并性等）
        assert len(coverage["concepts_missing"]) > 0, "应有缺失概念"
        print(f"  缺失概念列表: {coverage['concepts_missing'][:5]}...")
        print("  ✓ 覆盖图构建正确")

        # ── [3/11] 缺口识别 ──
        print("\n[3/11] 缺口识别...")
        gaps = analyzer.identify_gaps(coverage)
        print(f"  识别到 {len(gaps)} 个缺口")
        type_counts: Dict[str, int] = {}
        for g in gaps:
            type_counts[g["type"]] = type_counts.get(g["type"], 0) + 1
        print(f"  类型分布: {type_counts}")
        assert len(gaps) > 0, "应识别到缺口"
        # 应有概念缺口（T1 有未覆盖维度）
        assert type_counts.get("conceptual", 0) > 0, "应有概念缺口"
        # 应有方法缺口（神经网络反演为 seedling）
        assert type_counts.get("methodological", 0) > 0, "应有方法缺口"
        # 每个缺口应有必要字段
        for g in gaps:
            assert "gap_id" in g
            assert "type" in g and g["type"] in GAP_TYPES
            assert "description" in g
            assert "evidence" in g and isinstance(g["evidence"], list)
            assert "suggested_approach" in g
        print("  ✓ 缺口识别正确（概念/方法/理论三类）")

        # ── [4/11] 缺口评分 ──
        print("\n[4/11] 缺口评分...")
        scored = analyzer.score_gaps(gaps)
        assert len(scored) == len(gaps)
        # 验证公式：priority = 0.4*novelty + 0.3*feasibility + 0.3*alignment
        for g in scored:
            expected = round(
                0.4 * g["novelty_score"]
                + 0.3 * g["feasibility_score"]
                + 0.3 * g["direction_alignment"],
                4,
            )
            assert abs(g["priority_score"] - expected) < 1e-6, (
                f"评分公式错误: gap={g['gap_id']} "
                f"expected={expected} actual={g['priority_score']}"
            )
        # 验证降序排列
        priorities = [g["priority_score"] for g in scored]
        assert priorities == sorted(priorities, reverse=True), "应按优先级降序排列"
        # 验证 gap_id 重新编号
        for i, g in enumerate(scored, 1):
            assert g["gap_id"] == f"gap_{i:03d}", (
                f"gap_id 编号错误: expected gap_{i:03d}, got {g['gap_id']}"
            )
        print(f"  最高优先级: {scored[0]['priority_score']} ({scored[0]['gap_id']})")
        print(f"  最低优先级: {scored[-1]['priority_score']} ({scored[-1]['gap_id']})")
        print("  ✓ 评分公式正确，降序排列，编号连续")

        # ── [5/11] 方向对比 ──
        print("\n[5/11] 方向对比...")
        t1_gaps = analyzer.compare_with_direction(scored, {"id": "T1", "name": "量子几何"})
        print(f"  T1 方向相关缺口: {len(t1_gaps)} 个")
        # T1 相关缺口 + 通用缺口（无 related_direction）
        for g in t1_gaps:
            assert g["related_direction"] == "T1" or g["related_direction"] == ""
        # T1 直接关联的缺口方向对齐度应为 1.0
        for g in t1_gaps:
            if g["related_direction"] == "T1":
                assert g["direction_alignment"] == 1.0, (
                    f"T1 缺口方向对齐度应为 1.0，实际 {g['direction_alignment']}"
                )
        # 验证 T5 相关缺口被排除
        t5_count = sum(1 for g in t1_gaps if g["related_direction"] == "T5")
        assert t5_count == 0, "T5 缺口应被排除"
        print("  ✓ 方向过滤正确，T5 缺口已排除，T1 对齐度提升至 1.0")

        # ── [6/11] 报告持久化 ──
        print("\n[6/11] 报告持久化...")
        report = analyzer.analyze()
        assert analyzer.report_path.exists(), "报告文件应已保存"
        print(f"  报告路径: {analyzer.report_path}")
        print(f"  缺口总数: {report['summary']['total_gaps']}")
        print(f"  平均优先级: {report['summary']['avg_priority']}")
        # 重新加载
        loaded = analyzer.get_gap_report()
        assert loaded is not None, "get_gap_report 应返回已保存报告"
        assert loaded["summary"]["total_gaps"] == report["summary"]["total_gaps"]
        assert len(loaded["gaps"]) == len(report["gaps"])
        print("  ✓ 保存 + 重新加载一致")

        # ── [7/11] Markdown 导出 ──
        print("\n[7/11] Markdown 导出...")
        md = analyzer.export_gap_report("markdown")
        assert "# 研究缺口报告" in md
        assert "## 摘要" in md
        assert "## 知识覆盖" in md
        assert "## 缺口列表" in md
        assert "优先级" in md
        print(f"  Markdown 长度: {len(md)} 字符")
        print(f"  前 80 字符: {md[:80]}...")
        print("  ✓ Markdown 格式正确")

        # ── [8/11] JSON 导出 ──
        print("\n[8/11] JSON 导出...")
        json_str = analyzer.export_gap_report("json")
        parsed = json.loads(json_str)
        assert "coverage" in parsed
        assert "gaps" in parsed
        assert "summary" in parsed
        assert parsed["summary"]["total_gaps"] == report["summary"]["total_gaps"]
        print(f"  JSON 长度: {len(json_str)} 字符")
        print("  ✓ JSON 格式正确，可正常解析")

        # ── [9/11] 空知识库处理 ──
        print("\n[9/11] 空知识库处理...")
        empty_proposal = tmp / "empty_proposal"
        empty_analyzer = GapAnalyzer(empty_proposal, research_directions=directions)

        # 使用返回空数据的 mock 模拟空知识库（设 None 会触发重载真实模块）
        class _EmptyKbWiki:
            def list_wiki_pages(self, wiki_type=None):
                return []

        class _EmptyPaperPool:
            def get_pool(self):
                return {"total": 0, "by_status": {}, "papers": []}

        empty_analyzer._kb_wiki = _EmptyKbWiki()
        empty_analyzer._kb_index = _MockKbIndex()
        empty_analyzer._paper_pool = _EmptyPaperPool()
        empty_coverage = empty_analyzer.scan_coverage()
        assert empty_coverage["concepts_covered"] == []
        assert empty_coverage["methods_established"] == []
        assert empty_coverage["papers_analyzed"] == 0
        # 所有方向维度均缺失
        assert len(empty_coverage["concepts_missing"]) > 0
        print(f"  空知识库缺失概念数: {len(empty_coverage['concepts_missing'])}")
        empty_gaps = empty_analyzer.identify_gaps(empty_coverage)
        # 应有概念缺口 + 实验缺口（论文池为空）
        empty_types = {g["type"] for g in empty_gaps}
        assert "conceptual" in empty_types
        assert "empirical" in empty_types, "空论文池应产生实验缺口"
        print("  ✓ 空知识库优雅降级，产生概念+实验缺口")

        # ── [10/11] 缺失方向处理 ──
        print("\n[10/11] 缺失方向处理...")
        no_dir_proposal = tmp / "no_dir_proposal"
        no_dir_analyzer = GapAnalyzer(no_dir_proposal)  # 无研究方向
        assert no_dir_analyzer.research_directions == []
        # Mock paper_pool 仍可用
        no_dir_analyzer._paper_pool = _MockPaperPool()
        no_dir_analyzer._kb_wiki = kb_wiki_mod  # 复用 patched 模块
        no_dir_analyzer._kb_index = _MockKbIndex()
        no_dir_coverage = no_dir_analyzer.scan_coverage()
        # 无研究方向 → 不检测缺失概念
        assert no_dir_coverage["concepts_missing"] == [], "无研究方向时不应检测缺失概念"
        no_dir_gaps = no_dir_analyzer.identify_gaps(no_dir_coverage)
        # 无研究方向 → 无概念缺口、无理论缺口，但有方法缺口
        no_dir_types = {g["type"] for g in no_dir_gaps}
        assert "conceptual" not in no_dir_types, "无研究方向时不应有概念缺口"
        assert "theoretical" not in no_dir_types, "无研究方向时不应有理论缺口"
        assert "methodological" in no_dir_types, "应有方法缺口"
        print(f"  无方向时缺口类型: {no_dir_types}")
        print("  ✓ 无研究方向时仅产生方法缺口")

        # ── [11/11] 原子写入 + 文件锁 ──
        print("\n[11/11] 原子写入 + 文件锁...")
        # 验证报告文件是有效 JSON（原子写入不会产生半写状态）
        raw_content = analyzer.report_path.read_text(encoding="utf-8")
        parsed_again = json.loads(raw_content)
        assert parsed_again["summary"]["total_gaps"] > 0
        # 验证锁名唯一性（不同 proposal 不同锁）
        analyzer2 = GapAnalyzer(tmp / "another_proposal")
        assert analyzer2._lock_name != analyzer._lock_name, (
            "不同 proposal 应有不同锁名"
        )
        print(f"  锁名1: {analyzer._lock_name}")
        print(f"  锁名2: {analyzer2._lock_name}")
        # 验证多次写入不损坏
        report2 = analyzer.analyze()
        raw2 = analyzer.report_path.read_text(encoding="utf-8")
        parsed2 = json.loads(raw2)
        assert parsed2["summary"]["total_gaps"] == report2["summary"]["total_gaps"]
        print("  ✓ 原子写入有效，文件锁按 proposal 隔离，多次写入不损坏")

        # ── 附加：恢复 kb_wiki 全局 ──
        kb_wiki_mod.KNOWLEDGE_DIR = _orig_kb_wiki["KNOWLEDGE_DIR"]
        kb_wiki_mod.WIKI_DIR = _orig_kb_wiki["WIKI_DIR"]

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print("\n(已清理临时目录)")

    print("\n" + "=" * 50)
    print("✓ gap_analyzer 自检全部通过（11/11）")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="研究缺口分析器")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
