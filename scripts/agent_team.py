#!/usr/bin/env python3
"""研究管线智能体团队管理系统 — v6.2 研究管线

用途：
    管理研究管线的智能体团队，提供名单管理、实时状态追踪、性能指标统计、
    团队结构可视化数据与团队成长管理。本模块为**管理层**，不执行业务逻辑，
    仅追踪与可视化执行业务逻辑的智能体。

智能体分层：
    - 核心管线智能体（6，每阶段一个）：方向校准 / 文献调研 / 课题凝练 /
      问题架构 / 申请书撰写 / 质量审查
    - 支撑智能体（4）：品味顾问 / 血缘记录员 / 产物管理员 / 引文管理员
    - 成长槽位（2，未激活）：审稿模拟员 / 实验方案设计师

智能体状态机：
    idle → working → idle（任务完成）
    idle → working → blocked → idle（阻塞解除）
    idle → working → blocked → offline（智能体故障）
    offline → idle（智能体重新激活）

数据存储：
    {PIPELINE_CONFIG_DIR}/agent-team.json
    线程安全：file_lock("agent-team") + 原子写入

边界合规（AGENTS.md §6）：
    - 仅导入共享基础设施：common, paths
    - 不导入 CoPilot 核心模块，不导入其他管线模块
    - 文件写入仅限 PIPELINE_CONFIG_DIR
    - delegate_module 为字符串引用，不做实际导入

用法示例：
    >>> from agent_team import AgentTeam
    >>> team = AgentTeam()
    >>> team.get_team_overview()
    {'total': 12, 'active': 0, 'idle': 10, 'blocked': 0, 'offline': 2, ...}
    >>> team.assign_task("agent_001", "分析用户研究方向")
    >>> team.complete_task("agent_001", success=True, duration_s=12.5)
    >>> team.get_agent_performance("agent_001")
    {'tasks_completed': 1, 'tasks_failed': 0, 'success_rate': 1.0, ...}

命令行自检：
    python3 scripts/agent_team.py --self-check
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock
from paths import PIPELINE_CONFIG_DIR

__all__ = [
    "AgentTeam",
    "AGENT_STATUS_FLOW",
    "AGENT_STATUS_LABELS",
    "DEFAULT_AGENTS",
]

# ---------------------------------------------------------------------------
# 智能体状态机
# ---------------------------------------------------------------------------
# idle → working → idle（任务完成）
# idle → working → blocked → idle（阻塞解除）
# idle → working → blocked → offline（智能体故障）
# offline → idle（智能体重新激活）
AGENT_STATUS_FLOW: Dict[str, set] = {
    "idle": {"working"},
    "working": {"idle", "blocked"},
    "blocked": {"idle", "offline"},
    "offline": {"idle"},
}

AGENT_STATUS_LABELS: Dict[str, str] = {
    "idle": "空闲",
    "working": "工作中",
    "blocked": "阻塞",
    "offline": "离线",
}

_VALID_STATUSES = ("idle", "working", "blocked", "offline")
_VALID_TIERS = ("core", "support", "growth")
_MAX_RECENT_TASKS = 10  # recent_tasks 最大保留数量

# ---------------------------------------------------------------------------
# 默认智能体名单（6 核心 + 4 支撑 + 2 成长槽 = 12）
# ---------------------------------------------------------------------------
DEFAULT_AGENTS: List[Dict[str, Any]] = [
    # --- 核心管线智能体（6，每阶段一个）---
    {
        "agent_id": "agent_001",
        "name": "方向校准官",
        "name_en": "Direction Calibrator",
        "role": "direction_calibration",
        "stage": 0,
        "delegate_module": "research_profiler",
        "description": "分析用户研究方向，校准管线目标与用户画像的对齐度",
        "capabilities": ["研究方向关键词提取", "用户画像读取", "方向对齐评估", "TF-IDF分析"],
        "icon": "🧭",
        "status": "idle",
        "tier": "core",
    },
    {
        "agent_id": "agent_002",
        "name": "文献调研员",
        "name_en": "Literature Researcher",
        "role": "literature_research",
        "stage": 1,
        "delegate_module": "external_fetcher",
        "description": "多源文献检索、评分排序、全文下载与简报生成",
        "capabilities": ["arXiv检索", "联网搜索", "论文评分", "简报生成", "全文下载"],
        "icon": "📚",
        "status": "idle",
        "tier": "core",
    },
    {
        "agent_id": "agent_003",
        "name": "课题凝练师",
        "name_en": "Topic Refiner",
        "role": "topic_refinement",
        "stage": 2,
        "delegate_module": "gap_analyzer",
        "description": "知识库覆盖度扫描、研究缺口识别、课题生成与评分",
        "capabilities": ["覆盖度分析", "缺口识别", "课题生成", "品味评分", "课题演化"],
        "icon": "🔬",
        "status": "idle",
        "tier": "core",
    },
    {
        "agent_id": "agent_004",
        "name": "问题架构师",
        "name_en": "Question Architect",
        "role": "question_construction",
        "stage": 3,
        "delegate_module": "question_architect",
        "description": "五要素体系构建、科学问题分解与验证",
        "capabilities": ["五要素框架构建", "问题分解", "五维验证", "证据链接"],
        "icon": "🏗️",
        "status": "idle",
        "tier": "core",
    },
    {
        "agent_id": "agent_005",
        "name": "申请书撰写员",
        "name_en": "Proposal Writer",
        "role": "proposal_writing",
        "stage": 4,
        "delegate_module": "proposal_writer",
        "description": "NSFC格式申请书章节撰写、引文注入、风格调整",
        "capabilities": ["章节模板组装", "引文占位符注入", "品味风格调整", "章节版本管理"],
        "icon": "✍️",
        "status": "idle",
        "tier": "core",
    },
    {
        "agent_id": "agent_006",
        "name": "质量审查官",
        "name_en": "Quality Inspector",
        "role": "self_check_optimization",
        "stage": 5,
        "delegate_module": "proposal_inspector",
        "description": "六维自检、问题识别、优化策略生成与迭代追踪",
        "capabilities": ["六维检查", "问题分级", "策略生成", "迭代追踪", "引文验证"],
        "icon": "🔍",
        "status": "idle",
        "tier": "core",
    },
    # --- 支撑智能体（4）---
    {
        "agent_id": "agent_007",
        "name": "品味顾问",
        "name_en": "Taste Advisor",
        "role": "taste_advisor",
        "stage": None,
        "delegate_module": "taste_engine",
        "description": "五维学术品味建模、课题评分、写作风格调整",
        "capabilities": ["品味模型更新", "相似度计算", "舒适区分析", "风格推荐"],
        "icon": "🎯",
        "status": "idle",
        "tier": "support",
    },
    {
        "agent_id": "agent_008",
        "name": "血缘记录员",
        "name_en": "Lineage Tracker",
        "role": "lineage_tracker",
        "stage": None,
        "delegate_module": "lineage_tracker",
        "description": "产物血缘关系维护、双向溯源、影响分析",
        "capabilities": ["血缘注册", "上游溯源", "下游溯源", "影响分析", "DOT导出"],
        "icon": "🔗",
        "status": "idle",
        "tier": "support",
    },
    {
        "agent_id": "agent_009",
        "name": "产物管理员",
        "name_en": "Artifact Manager",
        "role": "artifact_manager",
        "stage": None,
        "delegate_module": "artifact_manager",
        "description": "产物版本管理、生命周期状态机、diff与回滚",
        "capabilities": ["产物创建", "版本锁定", "产物作废", "diff对比", "版本回滚"],
        "icon": "📦",
        "status": "idle",
        "tier": "support",
    },
    {
        "agent_id": "agent_010",
        "name": "引文管理员",
        "name_en": "Citation Manager",
        "role": "citation_manager",
        "stage": None,
        "delegate_module": "citation_manager",
        "description": "参考文献库管理、NSFC格式化、引文扫描与验证",
        "capabilities": ["文献查重", "引文扫描", "格式化", "BibTeX导出", "引文验证"],
        "icon": "📑",
        "status": "idle",
        "tier": "support",
    },
    # --- 成长槽位（2，未激活）---
    {
        "agent_id": "agent_011",
        "name": "审稿模拟员",
        "name_en": "Review Simulator",
        "role": "review_simulator",
        "stage": None,
        "delegate_module": None,
        "description": "模拟NSFC评审专家视角，提供评审意见预判",
        "capabilities": [],
        "icon": "👨‍⚖️",
        "status": "offline",
        "tier": "growth",
    },
    {
        "agent_id": "agent_012",
        "name": "实验方案设计师",
        "name_en": "Experiment Designer",
        "role": "experiment_designer",
        "stage": None,
        "delegate_module": None,
        "description": "基于研究方案自动设计实验参数与光路配置",
        "capabilities": [],
        "icon": "⚙️",
        "status": "offline",
        "tier": "growth",
    },
]

_TIER_LABELS: Dict[str, str] = {
    "core": "核心管线",
    "support": "支撑团队",
    "growth": "成长槽位",
}


class AgentTeam:
    """研究管线智能体团队管理器。

    管理研究管线的智能体名单、状态、性能与团队结构。状态持久化到
    `{storage_dir}/agent-team.json`，通过 file_lock 保证线程/进程安全。

    本模块为管理层，不执行业务逻辑——delegate_module 字段为字符串引用，
    不做实际模块导入。
    """

    TEAM_ID = "linsai-research-team"
    TEAM_NAME = "林赛研究管线团队"
    STATE_FILENAME = "agent-team.json"

    def __init__(self, storage_dir: Path | str = PIPELINE_CONFIG_DIR) -> None:
        """初始化智能体团队管理器。

        Args:
            storage_dir: 状态文件存储目录，默认为 PIPELINE_CONFIG_DIR。
        """
        self.storage_dir = Path(storage_dir)
        self.state_path = self.storage_dir / self.STATE_FILENAME
        self._lock_name = "agent-team"
        # 确保目录与初始状态文件存在
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            with file_lock(self._lock_name):
                if not self.state_path.exists():  # double-check，防并发重复初始化
                    save_json(self.state_path, self._initial_state())

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _initial_state(self) -> Dict[str, Any]:
        """构造初始状态字典。"""
        ts = now_utc()
        agents: Dict[str, Any] = {}
        for a in DEFAULT_AGENTS:
            agent = dict(a)
            agent["performance"] = self._empty_performance()
            agent["current_task"] = None
            agent["updated_at"] = ts
            agents[agent["agent_id"]] = agent
        return {
            "team_id": self.TEAM_ID,
            "name": self.TEAM_NAME,
            "agents": agents,
            "created_at": ts,
            "last_updated": ts,
        }

    @staticmethod
    def _empty_performance() -> Dict[str, Any]:
        """返回空的性能指标字典。"""
        return {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "success_rate": 1.0,
            "avg_duration_s": 0.0,
            "total_duration_s": 0.0,
            "last_task_at": None,
            "recent_tasks": [],
        }

    def _load_state(self) -> Dict[str, Any]:
        """加载状态文件（纯读，不加锁）。状态缺失时返回初始状态但不写盘。

        自动补全缺失的默认智能体（版本升级兼容）。
        """
        data = load_json(self.state_path, default=None)
        if not isinstance(data, dict) or "agents" not in data:
            return self._initial_state()
        # 兜底字段
        if not isinstance(data.get("agents"), dict):
            data["agents"] = {}
        data.setdefault("team_id", self.TEAM_ID)
        data.setdefault("name", self.TEAM_NAME)
        data.setdefault("last_updated", now_utc())
        # 合并：补全缺失的默认智能体（版本升级兼容）
        ts = now_utc()
        for default_agent in DEFAULT_AGENTS:
            aid = default_agent["agent_id"]
            if aid not in data["agents"]:
                agent = dict(default_agent)
                agent["performance"] = self._empty_performance()
                agent["current_task"] = None
                agent["updated_at"] = ts
                data["agents"][aid] = agent
        return data

    def _save_state(self, data: Dict[str, Any]) -> None:
        """保存状态文件（原子写入，应在锁内调用）。"""
        data["last_updated"] = now_utc()
        save_json(self.state_path, data)

    def _recompute_performance(self, perf: Dict[str, Any]) -> None:
        """根据 tasks_completed/failed/total_duration 重算派生指标。"""
        completed = perf["tasks_completed"]
        failed = perf["tasks_failed"]
        total = completed + failed
        perf["success_rate"] = round(completed / total, 4) if total > 0 else 1.0
        perf["avg_duration_s"] = round(perf["total_duration_s"] / total, 4) if total > 0 else 0.0

    def _next_agent_id(self, data: Dict[str, Any]) -> str:
        """生成下一个 agent_id（agent_013, agent_014, ...）。"""
        existing = data.get("agents", {})
        max_num = 0
        for aid in existing:
            if aid.startswith("agent_"):
                try:
                    num = int(aid[6:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue
        return f"agent_{max_num + 1:03d}"

    @staticmethod
    def _validate_status_transition(old: str, new: str) -> None:
        """校验状态流转是否合法。

        允许同状态（幂等）；非法流转抛出 ValueError。
        """
        if new == old:
            return  # 幂等
        if new not in AGENT_STATUS_FLOW.get(old, set()):
            raise ValueError(
                f"非法状态流转: {old}({AGENT_STATUS_LABELS.get(old, old)})"
                f" → {new}({AGENT_STATUS_LABELS.get(new, new)})"
            )

    # ------------------------------------------------------------------
    # 团队检索
    # ------------------------------------------------------------------

    def get_team(self) -> Dict[str, Any]:
        """返回完整团队结构（前端渲染优化格式）。

        Returns:
            含 team_id / name / tiers(core/support/growth) / stats / last_updated
        """
        data = self._load_state()
        agents = list(data["agents"].values())
        # 核心智能体按 stage 排序，支撑与成长按 agent_id 排序
        core = sorted(
            [a for a in agents if a.get("tier") == "core"],
            key=lambda x: (x.get("stage", 0), x.get("agent_id", "")),
        )
        support = sorted(
            [a for a in agents if a.get("tier") == "support"],
            key=lambda x: x.get("agent_id", ""),
        )
        growth = sorted(
            [a for a in agents if a.get("tier") == "growth"],
            key=lambda x: x.get("agent_id", ""),
        )
        # 统计
        counts = self._count_statuses(agents)
        return {
            "team_id": data.get("team_id", self.TEAM_ID),
            "name": data.get("name", self.TEAM_NAME),
            "tiers": {
                "core": {
                    "label": _TIER_LABELS["core"],
                    "agents": [copy.deepcopy(a) for a in core],
                    "count": len(core),
                },
                "support": {
                    "label": _TIER_LABELS["support"],
                    "agents": [copy.deepcopy(a) for a in support],
                    "count": len(support),
                },
                "growth": {
                    "label": _TIER_LABELS["growth"],
                    "agents": [copy.deepcopy(a) for a in growth],
                    "count": len(growth),
                },
            },
            "stats": {
                "total": len(agents),
                "active": counts["working"],
                "idle": counts["idle"],
                "blocked": counts["blocked"],
                "offline": counts["offline"],
            },
            "last_updated": data.get("last_updated", now_utc()),
        }

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取单个智能体详情（深拷贝）；不存在返回 None。"""
        data = self._load_state()
        agent = data["agents"].get(agent_id)
        return copy.deepcopy(agent) if agent else None

    def get_team_overview(self) -> Dict[str, Any]:
        """返回仪表盘概要：总数 / 各状态计数 / 分层分布。"""
        data = self._load_state()
        agents = list(data["agents"].values())
        counts = self._count_statuses(agents)
        tier_dist: Dict[str, int] = {"core": 0, "support": 0, "growth": 0}
        for a in agents:
            t = a.get("tier", "core")
            if t in tier_dist:
                tier_dist[t] += 1
        return {
            "team_id": data.get("team_id", self.TEAM_ID),
            "name": data.get("name", self.TEAM_NAME),
            "total": len(agents),
            "active": counts["working"],
            "idle": counts["idle"],
            "blocked": counts["blocked"],
            "offline": counts["offline"],
            "tier_distribution": tier_dist,
            "last_updated": data.get("last_updated", now_utc()),
        }

    def get_core_agents(self) -> List[Dict[str, Any]]:
        """返回核心管线智能体列表（按 stage 排序）。"""
        data = self._load_state()
        agents = [a for a in data["agents"].values() if a.get("tier") == "core"]
        agents.sort(key=lambda x: (x.get("stage", 0), x.get("agent_id", "")))
        return [copy.deepcopy(a) for a in agents]

    def get_support_agents(self) -> List[Dict[str, Any]]:
        """返回支撑智能体列表（按 agent_id 排序）。"""
        data = self._load_state()
        agents = [a for a in data["agents"].values() if a.get("tier") == "support"]
        agents.sort(key=lambda x: x.get("agent_id", ""))
        return [copy.deepcopy(a) for a in agents]

    def get_growth_slots(self) -> List[Dict[str, Any]]:
        """返回成长槽位列表（按 agent_id 排序）。"""
        data = self._load_state()
        agents = [a for a in data["agents"].values() if a.get("tier") == "growth"]
        agents.sort(key=lambda x: x.get("agent_id", ""))
        return [copy.deepcopy(a) for a in agents]

    # ------------------------------------------------------------------
    # 状态与任务管理
    # ------------------------------------------------------------------

    def update_agent_status(
        self,
        agent_id: str,
        status: str,
        current_task: Optional[str] = None,
    ) -> Dict[str, Any]:
        """更新智能体状态。

        Args:
            agent_id: 智能体 ID。
            status: 新状态（idle/working/blocked/offline）。
            current_task: 可选，当前任务描述。设为 idle 时自动清空。

        Returns:
            更新后的智能体详情（深拷贝）。

        Raises:
            KeyError: 智能体不存在。
            ValueError: 非法状态或非法流转。
        """
        if status not in _VALID_STATUSES:
            raise ValueError(f"非法状态: {status}（合法值: {_VALID_STATUSES}）")
        with file_lock(self._lock_name):
            data = self._load_state()
            agent = data["agents"].get(agent_id)
            if agent is None:
                raise KeyError(f"智能体不存在: {agent_id}")
            old_status = agent.get("status", "idle")
            self._validate_status_transition(old_status, status)
            agent["status"] = status
            if current_task is not None:
                agent["current_task"] = current_task
            if status == "idle":
                agent["current_task"] = None
            agent["updated_at"] = now_utc()
            self._save_state(data)
            return copy.deepcopy(agent)

    def assign_task(self, agent_id: str, task: str) -> Dict[str, Any]:
        """向智能体分配任务（状态置为 working）。

        仅空闲（idle）智能体可分配任务。阻塞或离线智能体需先解除状态。

        Args:
            agent_id: 智能体 ID。
            task: 任务描述。

        Returns:
            更新后的智能体详情（深拷贝）。

        Raises:
            KeyError: 智能体不存在。
            ValueError: 智能体非空闲状态，无法分配任务。
        """
        if not task:
            raise ValueError("任务描述不能为空")
        with file_lock(self._lock_name):
            data = self._load_state()
            agent = data["agents"].get(agent_id)
            if agent is None:
                raise KeyError(f"智能体不存在: {agent_id}")
            old_status = agent.get("status", "idle")
            if old_status != "idle":
                raise ValueError(
                    f"智能体 {agent_id} 当前状态为 {old_status}"
                    f"（{AGENT_STATUS_LABELS.get(old_status, old_status)}），"
                    f"仅空闲状态可分配任务"
                )
            agent["status"] = "working"
            agent["current_task"] = task
            agent["updated_at"] = now_utc()
            self._save_state(data)
            return copy.deepcopy(agent)

    def complete_task(
        self,
        agent_id: str,
        success: bool,
        duration_s: float,
    ) -> Dict[str, Any]:
        """完成智能体当前任务，记录性能指标，状态置为 idle。

        Args:
            agent_id: 智能体 ID。
            success: 任务是否成功。
            duration_s: 任务耗时（秒）。

        Returns:
            更新后的智能体详情（深拷贝）。

        Raises:
            KeyError: 智能体不存在。
            ValueError: 智能体非工作状态，无任务可完成。
        """
        with file_lock(self._lock_name):
            data = self._load_state()
            agent = data["agents"].get(agent_id)
            if agent is None:
                raise KeyError(f"智能体不存在: {agent_id}")
            old_status = agent.get("status", "idle")
            if old_status != "working":
                raise ValueError(
                    f"智能体 {agent_id} 当前状态为 {old_status}"
                    f"（{AGENT_STATUS_LABELS.get(old_status, old_status)}），"
                    f"仅工作状态可完成任务"
                )
            # 记录性能
            perf = agent.setdefault("performance", self._empty_performance())
            task_desc = agent.get("current_task", "")
            if success:
                perf["tasks_completed"] += 1
            else:
                perf["tasks_failed"] += 1
            perf["total_duration_s"] = round(
                perf["total_duration_s"] + max(0.0, float(duration_s)), 4
            )
            self._recompute_performance(perf)
            ts = now_utc()
            perf["last_task_at"] = ts
            perf["recent_tasks"].append({
                "task": task_desc,
                "success": success,
                "duration_s": round(max(0.0, float(duration_s)), 4),
                "timestamp": ts,
            })
            if len(perf["recent_tasks"]) > _MAX_RECENT_TASKS:
                perf["recent_tasks"] = perf["recent_tasks"][-_MAX_RECENT_TASKS:]
            # 状态置为 idle，清空当前任务
            agent["status"] = "idle"
            agent["current_task"] = None
            agent["updated_at"] = ts
            self._save_state(data)
            return copy.deepcopy(agent)

    def record_performance(
        self,
        agent_id: str,
        success: bool,
        duration_s: float,
    ) -> Dict[str, Any]:
        """记录智能体性能指标（不改变状态，不要求 working）。

        用于手动记录任务结果，与 complete_task 不同——本方法仅更新指标。

        Args:
            agent_id: 智能体 ID。
            success: 任务是否成功。
            duration_s: 任务耗时（秒）。

        Returns:
            更新后的智能体详情（深拷贝）。

        Raises:
            KeyError: 智能体不存在。
        """
        with file_lock(self._lock_name):
            data = self._load_state()
            agent = data["agents"].get(agent_id)
            if agent is None:
                raise KeyError(f"智能体不存在: {agent_id}")
            perf = agent.setdefault("performance", self._empty_performance())
            if success:
                perf["tasks_completed"] += 1
            else:
                perf["tasks_failed"] += 1
            perf["total_duration_s"] = round(
                perf["total_duration_s"] + max(0.0, float(duration_s)), 4
            )
            self._recompute_performance(perf)
            ts = now_utc()
            perf["last_task_at"] = ts
            perf["recent_tasks"].append({
                "task": agent.get("current_task", ""),
                "success": success,
                "duration_s": round(max(0.0, float(duration_s)), 4),
                "timestamp": ts,
            })
            if len(perf["recent_tasks"]) > _MAX_RECENT_TASKS:
                perf["recent_tasks"] = perf["recent_tasks"][-_MAX_RECENT_TASKS:]
            agent["updated_at"] = ts
            self._save_state(data)
            return copy.deepcopy(agent)

    # ------------------------------------------------------------------
    # 团队成长管理
    # ------------------------------------------------------------------

    def add_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加新智能体（团队成长）。

        Args:
            agent_data: 智能体定义字典，至少含 name 和 role。
                agent_id 未提供时自动生成。

        Returns:
            新建的智能体详情（深拷贝）。

        Raises:
            ValueError: name 或 role 为空，或 agent_id 已存在。
        """
        if not agent_data.get("name"):
            raise ValueError("agent_data.name 不能为空")
        if not agent_data.get("role"):
            raise ValueError("agent_data.role 不能为空")
        with file_lock(self._lock_name):
            data = self._load_state()
            agent_id = agent_data.get("agent_id") or self._next_agent_id(data)
            if agent_id in data["agents"]:
                raise ValueError(f"智能体ID已存在: {agent_id}")
            tier = agent_data.get("tier", "growth")
            if tier not in _VALID_TIERS:
                raise ValueError(f"非法 tier: {tier}（合法值: {_VALID_TIERS}）")
            ts = now_utc()
            agent: Dict[str, Any] = {
                "agent_id": agent_id,
                "name": agent_data["name"],
                "name_en": agent_data.get("name_en", agent_data["name"]),
                "role": agent_data["role"],
                "stage": agent_data.get("stage"),
                "delegate_module": agent_data.get("delegate_module"),
                "description": agent_data.get("description", ""),
                "capabilities": list(agent_data.get("capabilities", [])),
                "icon": agent_data.get("icon", "🤖"),
                "status": agent_data.get("status", "idle"),
                "tier": tier,
                "performance": self._empty_performance(),
                "current_task": None,
                "updated_at": ts,
            }
            data["agents"][agent_id] = agent
            self._save_state(data)
            return copy.deepcopy(agent)

    def upgrade_agent(
        self,
        agent_id: str,
        new_capabilities: List[str],
        new_delegate_module: Optional[str] = None,
    ) -> Dict[str, Any]:
        """升级智能体：添加新能力，可选更新委派模块。

        Args:
            agent_id: 智能体 ID。
            new_capabilities: 新增能力列表（自动去重，保留已有能力）。
            new_delegate_module: 可选，新的委派模块名。

        Returns:
            更新后的智能体详情（深拷贝）。

        Raises:
            KeyError: 智能体不存在。
        """
        if not isinstance(new_capabilities, list):
            raise ValueError("new_capabilities 必须为列表")
        with file_lock(self._lock_name):
            data = self._load_state()
            agent = data["agents"].get(agent_id)
            if agent is None:
                raise KeyError(f"智能体不存在: {agent_id}")
            existing_caps = agent.get("capabilities", [])
            for cap in new_capabilities:
                if cap not in existing_caps:
                    existing_caps.append(cap)
            agent["capabilities"] = existing_caps
            if new_delegate_module is not None:
                agent["delegate_module"] = new_delegate_module
            agent["updated_at"] = now_utc()
            self._save_state(data)
            return copy.deepcopy(agent)

    def activate_growth_slot(
        self,
        slot_id: str,
        delegate_module: str,
        capabilities: List[str],
    ) -> Dict[str, Any]:
        """激活成长槽位：绑定委派模块、注入能力、状态从 offline 切换到 idle。

        Args:
            slot_id: 成长槽位智能体 ID。
            delegate_module: 委派模块名。
            capabilities: 能力列表。

        Returns:
            激活后的智能体详情（深拷贝）。

        Raises:
            KeyError: 智能体不存在。
            ValueError: 智能体非成长槽位或非离线状态。
        """
        if not delegate_module:
            raise ValueError("delegate_module 不能为空")
        if not isinstance(capabilities, list):
            raise ValueError("capabilities 必须为列表")
        with file_lock(self._lock_name):
            data = self._load_state()
            agent = data["agents"].get(slot_id)
            if agent is None:
                raise KeyError(f"智能体不存在: {slot_id}")
            if agent.get("tier") != "growth":
                raise ValueError(
                    f"智能体 {slot_id} 非成长槽位（tier={agent.get('tier')}），无法激活"
                )
            if agent.get("status") != "offline":
                raise ValueError(
                    f"智能体 {slot_id} 当前状态为 {agent.get('status')}，仅离线状态可激活"
                )
            agent["delegate_module"] = delegate_module
            agent["capabilities"] = list(capabilities)
            agent["status"] = "idle"
            agent["updated_at"] = now_utc()
            self._save_state(data)
            return copy.deepcopy(agent)

    # ------------------------------------------------------------------
    # 性能统计
    # ------------------------------------------------------------------

    def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """获取智能体详细性能指标。

        Args:
            agent_id: 智能体 ID。

        Returns:
            性能指标字典（含 tasks_completed/failed/success_rate/avg_duration_s/
            total_duration_s/last_task_at/recent_tasks）。

        Raises:
            KeyError: 智能体不存在。
        """
        data = self._load_state()
        agent = data["agents"].get(agent_id)
        if agent is None:
            raise KeyError(f"智能体不存在: {agent_id}")
        perf = agent.get("performance", self._empty_performance())
        return copy.deepcopy(perf)

    def get_team_performance(self) -> Dict[str, Any]:
        """返回团队整体性能汇总。

        Returns:
            含 total_tasks_completed/failed/overall_success_rate/
            overall_avg_duration_s/agent_count/active_agents/by_agent。
        """
        data = self._load_state()
        agents = data["agents"]
        total_completed = 0
        total_failed = 0
        total_duration = 0.0
        active_agents = 0  # 有任务记录的智能体数
        by_agent: Dict[str, Any] = {}
        for aid, agent in agents.items():
            perf = agent.get("performance", self._empty_performance())
            tc = perf.get("tasks_completed", 0)
            tf = perf.get("tasks_failed", 0)
            td = perf.get("total_duration_s", 0.0)
            total_completed += tc
            total_failed += tf
            total_duration += td
            if tc + tf > 0:
                active_agents += 1
            by_agent[aid] = {
                "name": agent.get("name", aid),
                "tier": agent.get("tier", "core"),
                "tasks_completed": tc,
                "tasks_failed": tf,
                "success_rate": perf.get("success_rate", 1.0),
                "avg_duration_s": perf.get("avg_duration_s", 0.0),
                "last_task_at": perf.get("last_task_at"),
            }
        total_tasks = total_completed + total_failed
        return {
            "total_tasks_completed": total_completed,
            "total_tasks_failed": total_failed,
            "total_tasks": total_tasks,
            "overall_success_rate": round(total_completed / total_tasks, 4) if total_tasks > 0 else 1.0,
            "overall_avg_duration_s": round(total_duration / total_tasks, 4) if total_tasks > 0 else 0.0,
            "total_duration_s": round(total_duration, 4),
            "agent_count": len(agents),
            "active_agents": active_agents,
            "by_agent": by_agent,
        }

    # ------------------------------------------------------------------
    # 导出
    # ------------------------------------------------------------------

    def export_team(self, format: str = "json") -> str:
        """导出团队数据。

        Args:
            format: 导出格式，当前仅支持 "json"。

        Returns:
            JSON 格式字符串。

        Raises:
            ValueError: 不支持的格式。
        """
        if format != "json":
            raise ValueError(f"不支持的导出格式: {format}（当前仅支持 json）")
        import json
        data = self._load_state()
        return json.dumps(data, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # 内部统计工具
    # ------------------------------------------------------------------

    @staticmethod
    def _count_statuses(agents: List[Dict[str, Any]]) -> Dict[str, int]:
        """统计各状态智能体数量。"""
        counts = {"idle": 0, "working": 0, "blocked": 0, "offline": 0}
        for a in agents:
            s = a.get("status", "idle")
            if s in counts:
                counts[s] += 1
        return counts


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def _self_check() -> None:
    """自检：覆盖初始化、检索、状态流转、任务管理、性能统计、团队成长、
    持久化、原子写入+文件锁等检查点。使用临时目录隔离，结束后自动清理。
    """
    import json
    import tempfile

    print("=" * 60)
    print("◐ agent_team 自检")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp:
        storage = Path(tmp) / "config"

        # [1/16] 团队初始化（12 个智能体：6 核心 + 4 支撑 + 2 成长）
        print("\n[1/16] 团队初始化...")
        team = AgentTeam(storage_dir=storage)
        assert storage.exists(), "存储目录应已创建"
        assert (storage / "agent-team.json").exists(), "状态文件应已创建"
        raw = (storage / "agent-team.json").read_text(encoding="utf-8")
        parsed = json.loads(raw)  # 合法 JSON
        assert parsed["team_id"] == "linsai-research-team"
        assert parsed["name"] == "林赛研究管线团队"
        agent_count = len(parsed["agents"])
        print(f"  智能体总数: {agent_count}")
        assert agent_count == 12, f"应有 12 个智能体，实际 {agent_count}"
        # 验证分层分布
        tiers = [a["tier"] for a in parsed["agents"].values()]
        assert tiers.count("core") == 6, f"核心智能体应为 6，实际 {tiers.count('core')}"
        assert tiers.count("support") == 4, f"支撑智能体应为 4，实际 {tiers.count('support')}"
        assert tiers.count("growth") == 2, f"成长槽位应为 2，实际 {tiers.count('growth')}"
        # 验证成长槽位为 offline
        growth_statuses = [a["status"] for a in parsed["agents"].values() if a["tier"] == "growth"]
        assert all(s == "offline" for s in growth_statuses), "成长槽位应为 offline"
        print("  ✓ 12 个智能体初始化正确（6 核心 + 4 支撑 + 2 成长，成长槽位 offline）")

        # [2/16] 团队结构检索（tiers 结构正确）
        print("\n[2/16] 团队结构检索...")
        team_data = team.get_team()
        assert team_data["team_id"] == "linsai-research-team"
        assert team_data["name"] == "林赛研究管线团队"
        assert "tiers" in team_data
        assert team_data["tiers"]["core"]["label"] == "核心管线"
        assert team_data["tiers"]["support"]["label"] == "支撑团队"
        assert team_data["tiers"]["growth"]["label"] == "成长槽位"
        assert team_data["tiers"]["core"]["count"] == 6
        assert team_data["tiers"]["support"]["count"] == 4
        assert team_data["tiers"]["growth"]["count"] == 2
        # 核心智能体按 stage 排序
        core_agents = team_data["tiers"]["core"]["agents"]
        stages = [a["stage"] for a in core_agents]
        assert stages == [0, 1, 2, 3, 4, 5], f"核心智能体应按 stage 排序，实际 {stages}"
        # stats 结构
        assert team_data["stats"]["total"] == 12
        assert team_data["stats"]["idle"] == 10  # 6 核心 + 4 支撑
        assert team_data["stats"]["offline"] == 2  # 2 成长槽位
        assert team_data["stats"]["active"] == 0
        assert team_data["stats"]["blocked"] == 0
        print(f"  stats: {team_data['stats']}")
        print("  ✓ tiers 结构与 stats 计数正确")

        # [3/16] 单个智能体检索
        print("\n[3/16] 单个智能体检索...")
        agent = team.get_agent("agent_001")
        assert agent is not None, "agent_001 应存在"
        assert agent["name"] == "方向校准官"
        assert agent["name_en"] == "Direction Calibrator"
        assert agent["role"] == "direction_calibration"
        assert agent["stage"] == 0
        assert agent["delegate_module"] == "research_profiler"
        assert agent["tier"] == "core"
        assert agent["status"] == "idle"
        assert "performance" in agent
        assert agent["current_task"] is None
        # 不存在的智能体返回 None
        assert team.get_agent("agent_999") is None
        # 返回的是深拷贝（修改不影响内部状态）
        agent["name"] = "被篡改"
        agent2 = team.get_agent("agent_001")
        assert agent2["name"] == "方向校准官", "深拷贝应防止外部修改影响内部状态"
        print(f"  agent_001: {agent2['name']}({agent2['name_en']}), stage={agent2['stage']}")
        print("  ✓ 单个智能体检索 + 深拷贝隔离")

        # [4/16] 团队概览统计
        print("\n[4/16] 团队概览统计...")
        overview = team.get_team_overview()
        assert overview["total"] == 12
        assert overview["active"] == 0
        assert overview["idle"] == 10
        assert overview["blocked"] == 0
        assert overview["offline"] == 2
        assert overview["tier_distribution"] == {"core": 6, "support": 4, "growth": 2}
        print(f"  overview: total={overview['total']}, idle={overview['idle']}, "
              f"offline={overview['offline']}, tier_dist={overview['tier_distribution']}")
        print("  ✓ 概览统计正确")

        # [5/16] 核心智能体过滤
        print("\n[5/16] 核心智能体过滤...")
        core = team.get_core_agents()
        assert len(core) == 6, f"核心智能体应为 6，实际 {len(core)}"
        assert all(a["tier"] == "core" for a in core)
        # 验证按 stage 排序
        assert [a["stage"] for a in core] == [0, 1, 2, 3, 4, 5]
        # 验证 delegate_module 与 STAGES 一致
        assert core[0]["delegate_module"] == "research_profiler"
        assert core[1]["delegate_module"] == "external_fetcher"
        assert core[2]["delegate_module"] == "gap_analyzer"
        assert core[3]["delegate_module"] == "question_architect"
        assert core[4]["delegate_module"] == "proposal_writer"
        assert core[5]["delegate_module"] == "proposal_inspector"
        print(f"  核心智能体: {len(core)} 个，delegate_modules 正确")
        print("  ✓ 核心智能体过滤 + 排序 + delegate_module 一致")

        # [6/16] 支撑智能体过滤
        print("\n[6/16] 支撑智能体过滤...")
        support = team.get_support_agents()
        assert len(support) == 4, f"支撑智能体应为 4，实际 {len(support)}"
        assert all(a["tier"] == "support" for a in support)
        support_ids = [a["agent_id"] for a in support]
        assert support_ids == ["agent_007", "agent_008", "agent_009", "agent_010"]
        assert all(a["stage"] is None for a in support), "支撑智能体 stage 应为 None"
        print(f"  支撑智能体: {len(support)} 个")
        print("  ✓ 支撑智能体过滤正确")

        # [7/16] 成长槽位过滤
        print("\n[7/16] 成长槽位过滤...")
        growth = team.get_growth_slots()
        assert len(growth) == 2, f"成长槽位应为 2，实际 {len(growth)}"
        assert all(a["tier"] == "growth" for a in growth)
        assert all(a["status"] == "offline" for a in growth)
        assert all(a["delegate_module"] is None for a in growth), "成长槽位 delegate_module 应为 None"
        assert all(a["capabilities"] == [] for a in growth), "成长槽位 capabilities 应为空"
        print(f"  成长槽位: {len(growth)} 个（均未激活）")
        print("  ✓ 成长槽位过滤正确")

        # [8/16] 状态更新（idle → working → idle）
        print("\n[8/16] 状态更新（idle → working → idle）...")
        updated = team.update_agent_status("agent_002", "working", current_task="检索 arXiv 论文")
        assert updated["status"] == "working"
        assert updated["current_task"] == "检索 arXiv 论文"
        # idle → blocked 应失败（必须先经过 working）
        try:
            team.update_agent_status("agent_003", "blocked")
            raise AssertionError("idle → blocked 应被拒绝")
        except ValueError as e:
            print(f"  ✓ 拒绝非法流转 idle → blocked: {e}")
        # working → idle
        updated2 = team.update_agent_status("agent_002", "idle")
        assert updated2["status"] == "idle"
        assert updated2["current_task"] is None, "idle 状态应清空 current_task"
        # 幂等：idle → idle
        updated3 = team.update_agent_status("agent_002", "idle")
        assert updated3["status"] == "idle"
        # 非法状态
        try:
            team.update_agent_status("agent_002", "running")
            raise AssertionError("非法状态应被拒绝")
        except ValueError as e:
            print(f"  ✓ 拒绝非法状态 running: {e}")
        print("  ✓ 状态流转 idle → working → idle + 幂等 + 非法流转拒绝")

        # [9/16] 任务分配
        print("\n[9/16] 任务分配...")
        assigned = team.assign_task("agent_003", "扫描知识库覆盖度")
        assert assigned["status"] == "working"
        assert assigned["current_task"] == "扫描知识库覆盖度"
        # 工作中的智能体不能再分配任务
        try:
            team.assign_task("agent_003", "另一个任务")
            raise AssertionError("工作中的智能体不应再分配任务")
        except ValueError as e:
            print(f"  ✓ 拒绝为工作中的智能体分配任务: {e}")
        # 空任务描述
        try:
            team.assign_task("agent_004", "")
            raise AssertionError("空任务描述应被拒绝")
        except ValueError as e:
            print(f"  ✓ 拒绝空任务描述: {e}")
        # 离线智能体不能分配任务
        try:
            team.assign_task("agent_011", "模拟审稿")
            raise AssertionError("离线智能体不应分配任务")
        except ValueError as e:
            print(f"  ✓ 拒绝为离线智能体分配任务: {e}")
        print("  ✓ 任务分配 + 边界保护")

        # [10/16] 任务完成 + 性能记录
        print("\n[10/16] 任务完成 + 性能记录...")
        completed = team.complete_task("agent_003", success=True, duration_s=15.5)
        assert completed["status"] == "idle", "完成后应为 idle"
        assert completed["current_task"] is None, "完成后应清空 current_task"
        perf = completed["performance"]
        assert perf["tasks_completed"] == 1
        assert perf["tasks_failed"] == 0
        assert perf["total_duration_s"] == 15.5
        assert perf["last_task_at"] is not None
        assert len(perf["recent_tasks"]) == 1
        assert perf["recent_tasks"][0]["task"] == "扫描知识库覆盖度"
        assert perf["recent_tasks"][0]["success"] is True
        assert perf["recent_tasks"][0]["duration_s"] == 15.5
        # 非工作状态完成任务应失败
        try:
            team.complete_task("agent_004", success=True, duration_s=1.0)
            raise AssertionError("非工作状态不应完成任务")
        except ValueError as e:
            print(f"  ✓ 拒绝非工作状态完成任务: {e}")
        print(f"  完成后性能: completed={perf['tasks_completed']}, duration={perf['total_duration_s']}s")
        print("  ✓ 任务完成 + 性能记录 + 状态重置")

        # [11/16] 性能指标计算（success_rate, avg_duration）
        print("\n[11/16] 性能指标计算...")
        # 再做 2 成功 1 失败
        team.assign_task("agent_003", "任务A")
        team.complete_task("agent_003", success=True, duration_s=10.0)
        team.assign_task("agent_003", "任务B")
        team.complete_task("agent_003", success=True, duration_s=20.0)
        team.assign_task("agent_003", "任务C")
        team.complete_task("agent_003", success=False, duration_s=5.0)
        perf = team.get_agent_performance("agent_003")
        assert perf["tasks_completed"] == 3, f"应完成 3 个，实际 {perf['tasks_completed']}"
        assert perf["tasks_failed"] == 1, f"应失败 1 个，实际 {perf['tasks_failed']}"
        # success_rate = 3 / (3+1) = 0.75
        assert perf["success_rate"] == 0.75, f"success_rate 应为 0.75，实际 {perf['success_rate']}"
        # avg_duration = (15.5+10+20+5) / 4 = 12.625
        expected_avg = round((15.5 + 10.0 + 20.0 + 5.0) / 4, 4)
        assert perf["avg_duration_s"] == expected_avg, \
            f"avg_duration_s 应为 {expected_avg}，实际 {perf['avg_duration_s']}"
        # recent_tasks 保留最近 10 条
        assert len(perf["recent_tasks"]) == 4
        print(f"  completed={perf['tasks_completed']}, failed={perf['tasks_failed']}")
        print(f"  success_rate={perf['success_rate']}, avg_duration={perf['avg_duration_s']}s")
        print("  ✓ success_rate 与 avg_duration_s 计算正确")

        # [12/16] 智能体新增（团队成长）
        print("\n[12/16] 智能体新增...")
        new_agent = team.add_agent({
            "name": "数据可视化员",
            "name_en": "Data Visualizer",
            "role": "data_visualization",
            "description": "研究数据可视化与图表生成",
            "capabilities": ["图表生成", "数据清洗"],
            "icon": "📊",
            "tier": "growth",
        })
        new_id = new_agent["agent_id"]
        assert new_id == "agent_013", f"新智能体 ID 应为 agent_013，实际 {new_id}"
        assert new_agent["name"] == "数据可视化员"
        assert new_agent["tier"] == "growth"
        assert new_agent["status"] == "idle"
        assert new_agent["performance"]["tasks_completed"] == 0
        assert len(new_agent["capabilities"]) == 2
        # ID 重复应失败
        try:
            team.add_agent({"agent_id": "agent_001", "name": "重复", "role": "dup"})
            raise AssertionError("ID 重复应被拒绝")
        except ValueError as e:
            print(f"  ✓ 拒绝重复 ID: {e}")
        # name 为空应失败
        try:
            team.add_agent({"name": "", "role": "test"})
            raise AssertionError("空 name 应被拒绝")
        except ValueError as e:
            print(f"  ✓ 拒绝空 name: {e}")
        assert team.get_team_overview()["total"] == 13, "新增后总数应为 13"
        print(f"  新增智能体: {new_id}({new_agent['name']})")
        print("  ✓ 智能体新增 + ID 生成 + 校验")

        # [13/16] 智能体升级（添加能力）
        print("\n[13/16] 智能体升级...")
        upgraded = team.upgrade_agent("agent_004", ["新能力A", "新能力B"])
        assert "新能力A" in upgraded["capabilities"]
        assert "新能力B" in upgraded["capabilities"]
        # 原有能力保留
        assert "五要素框架构建" in upgraded["capabilities"]
        # 重复能力不重复添加
        upgraded2 = team.upgrade_agent("agent_004", ["新能力A", "五要素框架构建"])
        caps = team.get_agent("agent_004")["capabilities"]
        assert caps.count("新能力A") == 1, "重复能力不应重复添加"
        assert caps.count("五要素框架构建") == 1
        # 更新 delegate_module
        upgraded3 = team.upgrade_agent("agent_004", ["额外能力"], new_delegate_module="new_module")
        assert upgraded3["delegate_module"] == "new_module"
        # 不存在的智能体
        try:
            team.upgrade_agent("agent_999", ["x"])
            raise AssertionError("不存在的智能体应报错")
        except KeyError as e:
            print(f"  ✓ 拒绝不存在的智能体: {e}")
        print(f"  升级后能力数: {len(team.get_agent('agent_004')['capabilities'])}")
        print("  ✓ 智能体升级 + 去重 + delegate_module 更新")

        # [14/16] 成长槽位激活
        print("\n[14/16] 成长槽位激活...")
        activated = team.activate_growth_slot(
            "agent_011",
            delegate_module="review_simulator",
            capabilities=["评审意见生成", "评分预测", "竞争分析"],
        )
        assert activated["status"] == "idle", "激活后应为 idle"
        assert activated["delegate_module"] == "review_simulator"
        assert len(activated["capabilities"]) == 3
        assert "评审意见生成" in activated["capabilities"]
        # 非成长槽位激活应失败
        try:
            team.activate_growth_slot("agent_001", "mod", ["cap"])
            raise AssertionError("核心智能体不应激活")
        except ValueError as e:
            print(f"  ✓ 拒绝非成长槽位激活: {e}")
        # 已激活的槽位再次激活应失败（非 offline）
        try:
            team.activate_growth_slot("agent_011", "mod", ["cap"])
            raise AssertionError("非离线状态不应激活")
        except ValueError as e:
            print(f"  ✓ 拒绝非离线状态激活: {e}")
        # 激活后可正常分配任务
        assigned = team.assign_task("agent_011", "模拟 NSFC 评审")
        assert assigned["status"] == "working"
        team.complete_task("agent_011", success=True, duration_s=8.0)
        perf = team.get_agent_performance("agent_011")
        assert perf["tasks_completed"] == 1
        print(f"  激活 agent_011: delegate={activated['delegate_module']}, caps={len(activated['capabilities'])}")
        print("  ✓ 成长槽位激活 + 状态切换 + 任务执行")

        # [15/16] 团队性能汇总
        print("\n[15/16] 团队性能汇总...")
        team_perf = team.get_team_performance()
        assert team_perf["agent_count"] == 13, f"应有 13 个智能体，实际 {team_perf['agent_count']}"
        assert team_perf["total_tasks_completed"] >= 4, \
            f"应至少完成 4 个任务，实际 {team_perf['total_tasks_completed']}"
        assert team_perf["total_tasks_failed"] >= 1, \
            f"应至少失败 1 个任务，实际 {team_perf['total_tasks_failed']}"
        assert team_perf["active_agents"] >= 2, \
            f"应至少 2 个活跃智能体，实际 {team_perf['active_agents']}"
        assert "by_agent" in team_perf
        assert "agent_003" in team_perf["by_agent"]
        assert team_perf["by_agent"]["agent_003"]["tasks_completed"] == 3
        # overall_success_rate = 3_success / (3+1+1_other) 取决于总数
        assert 0.0 < team_perf["overall_success_rate"] <= 1.0
        print(f"  total_completed={team_perf['total_tasks_completed']}, "
              f"total_failed={team_perf['total_tasks_failed']}")
        print(f"  overall_success_rate={team_perf['overall_success_rate']}, "
              f"active_agents={team_perf['active_agents']}")
        print("  ✓ 团队性能汇总正确")

        # [16/16] 状态持久化（保存 + 重载）
        print("\n[16/16] 状态持久化（保存 + 重载）...")
        team2 = AgentTeam(storage_dir=storage)
        agent_003_reloaded = team2.get_agent("agent_003")
        assert agent_003_reloaded is not None
        assert agent_003_reloaded["performance"]["tasks_completed"] == 3, \
            "重载后 tasks_completed 应为 3"
        assert agent_003_reloaded["performance"]["tasks_failed"] == 1
        assert agent_003_reloaded["performance"]["success_rate"] == 0.75
        agent_011_reloaded = team2.get_agent("agent_011")
        assert agent_011_reloaded["status"] == "idle", "重载后 agent_011 应为 idle（已激活）"
        assert agent_011_reloaded["delegate_module"] == "review_simulator"
        new_agent_reloaded = team2.get_agent("agent_013")
        assert new_agent_reloaded is not None
        assert new_agent_reloaded["name"] == "数据可视化员"
        overview_reloaded = team2.get_team_overview()
        assert overview_reloaded["total"] == 13
        print(f"  重载后: total={overview_reloaded['total']}, "
              f"idle={overview_reloaded['idle']}, offline={overview_reloaded['offline']}")
        print("  ✓ 状态持久化 + 重载一致")

        # [附加] 原子写入 + 文件锁
        print("\n[附加] 原子写入 + 文件锁...")
        # 验证状态文件始终为合法 JSON
        raw = (storage / "agent-team.json").read_text(encoding="utf-8")
        json.loads(raw)  # 不抛异常即合法
        # 两实例交错操作不死锁
        team_a = AgentTeam(storage_dir=storage)
        team_b = AgentTeam(storage_dir=storage)
        for _ in range(3):
            team_a.assign_task("agent_005", "交错任务A")
            team_b.complete_task("agent_005", success=True, duration_s=1.0)
            team_a.update_agent_status("agent_006", "working", current_task="交错任务B")
            team_b.update_agent_status("agent_006", "idle")
        raw2 = (storage / "agent-team.json").read_text(encoding="utf-8")
        json.loads(raw2)  # 仍合法
        final_perf = team_a.get_agent_performance("agent_005")
        assert final_perf["tasks_completed"] >= 3, "交错操作后任务数应正确"
        print(f"  两实例交错 6 次操作，agent_005 完成 {final_perf['tasks_completed']} 个任务")
        print("  ✓ 原子写入 + 文件锁（无死锁、无损坏）")

        # [附加] 离线智能体重新激活（完整流转链）
        print("\n[附加] 离线智能体重新激活（完整流转链）...")
        # 完整流转: idle → working → blocked → offline → idle
        team_c = AgentTeam(storage_dir=storage)
        team_c.assign_task("agent_006", "自检任务")
        assert team_c.get_agent("agent_006")["status"] == "working"
        team_c.update_agent_status("agent_006", "blocked")
        assert team_c.get_agent("agent_006")["status"] == "blocked"
        team_c.update_agent_status("agent_006", "offline")
        assert team_c.get_agent("agent_006")["status"] == "offline"
        # offline → idle 重新激活
        team_c.update_agent_status("agent_006", "idle")
        assert team_c.get_agent("agent_006")["status"] == "idle"
        # blocked → offline 是合法的
        # 但 idle → offline 不合法
        try:
            team_c.update_agent_status("agent_006", "offline")
            raise AssertionError("idle → offline 应被拒绝")
        except ValueError as e:
            print(f"  ✓ 拒绝非法流转 idle → offline: {e}")
        print("  ✓ 完整流转链 idle → working → blocked → offline → idle")

        # [附加] 导出团队数据
        print("\n[附加] 导出团队数据...")
        exported = team.export_team(format="json")
        assert isinstance(exported, str)
        exported_data = json.loads(exported)
        assert exported_data["team_id"] == "linsai-research-team"
        assert len(exported_data["agents"]) == 13
        # 不支持的格式
        try:
            team.export_team(format="yaml")
            raise AssertionError("不支持的格式应报错")
        except ValueError as e:
            print(f"  ✓ 拒绝不支持的格式 yaml: {e}")
        print(f"  导出 JSON 字符串大小: {len(exported)} 字节")
        print("  ✓ 导出团队数据正确")

        # [附加] record_performance 独立记录
        print("\n[附加] record_performance 独立记录...")
        before = team.get_agent_performance("agent_007")
        team.record_performance("agent_007", success=True, duration_s=3.2)
        after = team.get_agent_performance("agent_007")
        assert after["tasks_completed"] == before["tasks_completed"] + 1
        assert after["total_duration_s"] == round(before["total_duration_s"] + 3.2, 4)
        assert len(after["recent_tasks"]) == len(before["recent_tasks"]) + 1
        # 不存在的智能体
        try:
            team.record_performance("agent_999", True, 1.0)
            raise AssertionError("不存在的智能体应报错")
        except KeyError as e:
            print(f"  ✓ 拒绝不存在的智能体: {e}")
        print(f"  agent_007: completed {before['tasks_completed']} → {after['tasks_completed']}")
        print("  ✓ record_performance 独立记录正确")

    print("\n" + "=" * 60)
    print("✓ agent_team 自检全部通过")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="研究管线智能体团队管理系统")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
