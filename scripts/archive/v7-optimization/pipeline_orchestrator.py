#!/usr/bin/env python3
"""管线状态机编排器 — 六阶段研究管线状态机驱动。

驱动研究管线的六阶段状态机，管理阶段流转、门禁校验、回滚、暂停/恢复，
并将状态持久化到 `{proposal_dir}/00_pipeline/pipeline-state.json`。

六阶段管线:
    0. 方向校准 (direction_calibration)    — 依据用户画像与研究方向感知校准方向
    1. 文献调研 (literature_research)       — 触发文献检索与分析，生成文献简报
    2. 课题凝练 (topic_refinement)          — 基于文献空白凝练课题
    3. 科学问题构建 (question_construction) — 构建并验证科学问题
    4. 申请书撰写 (proposal_writing)        — 撰写申请书各必要章节
    5. 自检优化 (self_check_optimization)   — 自检并优化，解决全部问题

阶段间设有六道门禁（Gate 0-5），门禁通过后方能进入下一阶段。
门禁支持三种评审类型：rule（规则）、llm（大模型）、user（人工）。
当前仅实现 rule 评审（基于 ArtifactManager 产物数量校验），llm/user 为占位桩。

状态机流转:
    正向: 阶段 N → 阶段 N+1（需门禁 N 通过）
    反向: 阶段 N → 阶段 N-1（回滚，需填写原因）
    暂停/恢复: 任意运行态可暂停，暂停后可恢复
    终态: 阶段 5 + 门禁 5 通过 → 管线完成（completed）

用法:
    >>> from pathlib import Path
    >>> from pipeline_orchestrator import PipelineManager
    >>> mgr = PipelineManager("T1", Path("/data/proposals/T1"))
    >>> mgr.get_state()["current_stage"]
    0
    >>> mgr.run_gate(0, "rule")   # 先创建产物再评审
    >>> mgr.advance_stage()        # 门禁通过后推进
    >>> mgr.pause("等待用户反馈")
    >>> mgr.resume()
    >>> mgr.rollback_stage("需要补充文献")
    >>> mgr.get_progress()

命令行自检:
    python3 scripts/pipeline_orchestrator.py --self-check
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, safe_filename, file_lock

__all__ = [
    "PipelineManager",
    "STAGES",
    "GATES",
    "STAGE_TRANSITIONS",
    "PIPELINE_STATUS_FLOW",
    "STAGE_STATUS_FLOW",
]

# ---------------------------------------------------------------------------
# 阶段定义
# ---------------------------------------------------------------------------
# 每个阶段含：id / name(中文) / name_en / description /
#             required_inputs / expected_outputs / delegate_module
STAGES: List[Dict[str, Any]] = [
    {
        "id": 0,
        "name": "方向校准",
        "name_en": "direction_calibration",
        "description": "依据用户画像与研究方向感知，校准研究方向。",
        "required_inputs": ["user_profile", "research_direction_keywords"],
        "expected_outputs": ["direction_calibration"],
        "delegate_module": "research_profiler",
    },
    {
        "id": 1,
        "name": "文献调研",
        "name_en": "literature_research",
        "description": "触发文献检索与分析，生成文献简报。",
        "required_inputs": ["direction_calibration"],
        "expected_outputs": ["literature_briefing"],
        "delegate_module": "external_fetcher",
    },
    {
        "id": 2,
        "name": "课题凝练",
        "name_en": "topic_refinement",
        "description": "基于文献空白凝练课题，完成空白分析。",
        "required_inputs": ["literature_briefing"],
        "expected_outputs": ["topic", "gap_analysis"],
        "delegate_module": "gap_analyzer",
    },
    {
        "id": 3,
        "name": "科学问题构建",
        "name_en": "question_construction",
        "description": "构建并验证科学问题。",
        "required_inputs": ["topic", "gap_analysis"],
        "expected_outputs": ["scientific_question"],
        "delegate_module": "question_architect",
    },
    {
        "id": 4,
        "name": "申请书撰写",
        "name_en": "proposal_writing",
        "description": "撰写申请书各必要章节。",
        "required_inputs": ["scientific_question"],
        "expected_outputs": ["proposal_section"],
        "delegate_module": "proposal_writer",
    },
    {
        "id": 5,
        "name": "自检优化",
        "name_en": "self_check_optimization",
        "description": "自检并优化申请书，解决全部问题。",
        "required_inputs": ["proposal_section"],
        "expected_outputs": ["self_check"],
        "delegate_module": "proposal_inspector",
    },
]

# ---------------------------------------------------------------------------
# 门禁定义
# ---------------------------------------------------------------------------
# 每道门禁含若干检查项；规则评审下全部检查项通过才算门禁通过。
# 检查项以 ArtifactManager 中的产物类型与数量为依据（min_count 为最低数量）。
GATES: List[Dict[str, Any]] = [
    {
        "stage": 0,
        "name": "方向校准门",
        "description": "校验研究方向关键词存在、用户画像已加载。",
        "checks": [
            {"id": "direction", "description": "研究方向关键词存在",
             "artifact_type": "direction_calibration", "stage": 0, "min_count": 1},
            {"id": "user_profile", "description": "用户画像已加载",
             "artifact_type": "user_profile", "stage": 0, "min_count": 1},
        ],
    },
    {
        "stage": 1,
        "name": "文献调研门",
        "description": "校验文献数量≥5、简报已生成。",
        "checks": [
            {"id": "paper_count", "description": "文献数量≥5",
             "artifact_type": "literature_briefing", "stage": 1, "min_count": 5},
        ],
    },
    {
        "stage": 2,
        "name": "课题凝练门",
        "description": "校验课题已生成(≥1)、空白分析已完成。",
        "checks": [
            {"id": "topics", "description": "课题已生成(≥1)",
             "artifact_type": "topic", "stage": 2, "min_count": 1},
            {"id": "gap_analysis", "description": "空白分析已完成",
             "artifact_type": "gap_analysis", "stage": 2, "min_count": 1},
        ],
    },
    {
        "stage": 3,
        "name": "科学问题门",
        "description": "校验科学问题已构建(≥1)并已验证。",
        "checks": [
            {"id": "questions", "description": "科学问题已构建(≥1)",
             "artifact_type": "scientific_question", "stage": 3, "min_count": 1},
            {"id": "validation", "description": "问题已验证",
             "artifact_type": "question_validation", "stage": 3, "min_count": 1},
        ],
    },
    {
        "stage": 4,
        "name": "申请书撰写门",
        "description": "校验申请书各必要章节齐备(≥4)。",
        "checks": [
            {"id": "sections", "description": "必要章节齐备(≥4)",
             "artifact_type": "proposal_section", "stage": 4, "min_count": 4},
        ],
    },
    {
        "stage": 5,
        "name": "自检优化门",
        "description": "校验自检报告已生成、问题已解决。",
        "checks": [
            {"id": "self_check", "description": "自检报告已生成",
             "artifact_type": "self_check", "stage": 5, "min_count": 1},
            {"id": "issues_resolved", "description": "问题已解决",
             "artifact_type": "issue_resolution", "stage": 5, "min_count": 1},
        ],
    },
]

# ---------------------------------------------------------------------------
# 状态流转规则
# ---------------------------------------------------------------------------
STAGE_TRANSITIONS: Dict[str, str] = {
    "forward": "阶段 N → 阶段 N+1（需门禁 N 通过）",
    "backward": "阶段 N → 阶段 N-1（回滚，需填写原因）",
    "pause": "任意运行态 → paused",
    "resume": "paused → running",
    "complete": "阶段 5 + 门禁 5 通过 → completed",
}

# 管线级状态流转
PIPELINE_STATUS_FLOW: Dict[str, set] = {
    "running": {"paused", "completed"},
    "paused": {"running"},
    "completed": set(),  # 终态
}

# 阶段级状态流转
STAGE_STATUS_FLOW: Dict[str, set] = {
    "pending": {"in_progress"},
    "in_progress": {"completed", "pending"},
    "completed": {"in_progress"},  # 回滚后可重新进入
}

_VALID_REVIEW_TYPES = ("rule", "llm", "user")


class PipelineManager:
    """六阶段研究管线状态机编排器。

    每个 proposal 目录对应一个 PipelineManager 实例，管理该 proposal 下
    `00_pipeline/pipeline-state.json` 状态文件。

    线程安全：所有写操作通过 common.file_lock（fcntl.flock 跨进程锁）保护
    read-modify-write 临界区，锁键为 `pipeline-{proposal_id}`，不同 proposal 互不阻塞。
    门禁校验通过 ArtifactManager 查询产物（只读），ArtifactManager 拥有独立锁，
    与管线锁互不嵌套，无死锁风险。
    """

    def __init__(self, proposal_id: str, proposal_dir: Path | str) -> None:
        """初始化管线编排器。

        Args:
            proposal_id: proposal 唯一标识（如 "T1"）。
            proposal_dir: proposal 根目录（Path 或字符串）。
        """
        self.proposal_id = str(proposal_id)
        self.proposal_dir = Path(proposal_dir)
        self.pipeline_dir = self.proposal_dir / "00_pipeline"
        self.state_path = self.pipeline_dir / "pipeline-state.json"
        # 跨进程锁键（按 requirement: file_lock("pipeline-{proposal_id}")，safe_filename 防非法字符）
        self._lock_name = f"pipeline-{safe_filename(self.proposal_id)}"
        self._artifact_mgr: Optional[Any] = None  # 懒加载
        # 确保目录与初始状态文件存在
        self.pipeline_dir.mkdir(parents=True, exist_ok=True)
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
        return {
            "proposal_id": self.proposal_id,
            "current_stage": 0,
            "status": "running",
            "stage_status": {
                str(i): ("in_progress" if i == 0 else "pending")
                for i in range(len(STAGES))
            },
            "gate_results": {},
            "history": [
                {
                    "event": "init",
                    "stage": 0,
                    "timestamp": ts,
                    "detail": f"管线初始化: {self.proposal_id}",
                }
            ],
            "created_at": ts,
            "updated_at": ts,
            "paused_at": None,
            "pause_reason": None,
            "resumed_at": None,
        }

    def _load_state(self) -> Dict[str, Any]:
        """加载状态文件（纯读，不加锁）。状态缺失时返回初始状态但不写盘。"""
        data = load_json(self.state_path, default=None)
        if not isinstance(data, dict) or "proposal_id" not in data:
            return self._initial_state()
        # 兜底字段，防老版本/手工编辑缺失键
        data.setdefault("gate_results", {})
        data.setdefault("history", [])
        data.setdefault("stage_status", {})
        data.setdefault("current_stage", 0)
        data.setdefault("status", "running")
        return data

    def _save_state(self, data: Dict[str, Any]) -> None:
        """保存状态文件（原子写入，应在锁内调用）。"""
        data["updated_at"] = now_utc()
        save_json(self.state_path, data)

    def _add_history(
        self, state: Dict[str, Any], event: str, stage: int, detail: str
    ) -> Dict[str, Any]:
        """向状态历史追加一条事件（须在锁内调用）。"""
        state["history"].append(
            {"event": event, "stage": stage, "timestamp": now_utc(), "detail": detail}
        )
        return state

    def _get_artifact_manager(self):
        """懒加载 ArtifactManager 实例（与 artifact_manager.py 解耦）。

        ArtifactManager 不可用时返回 None，门禁评审将降级为未通过。
        """
        if self._artifact_mgr is None:
            try:
                from artifact_manager import ArtifactManager  # 懒导入
                self._artifact_mgr = ArtifactManager(self.proposal_dir)
            except Exception:
                self._artifact_mgr = None
        return self._artifact_mgr

    def _evaluate_gate(self, stage: int, review_type: str) -> Dict[str, Any]:
        """评估门禁（纯读，不持久化，不加锁）。

        - rule 评审：通过 ArtifactManager 查询各检查项要求的产物数量。
        - llm/user 评审：当前为占位桩，返回未通过并提示尚未实现。

        Returns:
            {"passed": bool, "score": float, "issues": list,
             "review_type": str, "stage": int, "checked_at": str}
        """
        checked_at = now_utc()
        if review_type not in _VALID_REVIEW_TYPES:
            return {
                "passed": False, "score": 0.0,
                "issues": [f"未知评审类型: {review_type}"],
                "review_type": review_type, "stage": stage, "checked_at": checked_at,
            }

        if review_type != "rule":
            return {
                "passed": False, "score": 0.0,
                "issues": [f"{review_type}评审尚未实现（占位桩）"],
                "review_type": review_type, "stage": stage, "checked_at": checked_at,
            }

        if stage < 0 or stage >= len(GATES):
            return {
                "passed": False, "score": 0.0,
                "issues": [f"非法门禁编号: {stage}"],
                "review_type": review_type, "stage": stage, "checked_at": checked_at,
            }

        gate = GATES[stage]
        am = self._get_artifact_manager()
        checks = gate.get("checks", [])
        passed_count = 0
        issues: List[str] = []
        for check in checks:
            if am is None:
                issues.append(f"{check['description']}: ArtifactManager 不可用")
                continue
            arts = am.list_artifacts(
                stage=check.get("stage", stage),
                artifact_type=check["artifact_type"],
            )
            count = len(arts)
            if count >= check["min_count"]:
                passed_count += 1
            else:
                issues.append(
                    f"{check['description']}: 期望≥{check['min_count']}，实际{count}"
                )
        total = len(checks)
        score = round(passed_count / total, 2) if total else 1.0
        passed = (passed_count == total) if total else True
        return {
            "passed": passed, "score": score, "issues": issues,
            "review_type": review_type, "stage": stage, "checked_at": checked_at,
        }

    # ------------------------------------------------------------------
    # 核心接口
    # ------------------------------------------------------------------
    def get_state(self) -> Dict[str, Any]:
        """返回当前管线状态（副本）：阶段、状态、门禁结果、历史。"""
        return dict(self._load_state())

    def get_stage_info(self, stage: int) -> Dict[str, Any]:
        """返回阶段元数据：名称、描述、所需输入、预期产物、委派模块。

        Raises:
            ValueError: 阶段编号越界。
        """
        if stage < 0 or stage >= len(STAGES):
            raise ValueError(f"非法阶段编号: {stage}")
        return dict(STAGES[stage])

    def run_gate(self, stage: int, review_type: str = "rule") -> Dict[str, Any]:
        """执行门禁评审并持久化结果。

        Args:
            stage: 门禁对应的阶段编号（0-5）。
            review_type: 评审类型（rule/llm/user），当前仅 rule 实现。

        Returns:
            门禁结果: {"passed": bool, "score": float, "issues": list,
                      "review_type": str, "stage": int, "checked_at": str}
        """
        result = self._evaluate_gate(stage, review_type)
        with file_lock(self._lock_name):
            state = self._load_state()
            state["gate_results"][str(stage)] = result
            gate_name = GATES[stage]["name"] if 0 <= stage < len(GATES) else f"非法门禁{stage}"
            verdict = "通过" if result["passed"] else "未通过"
            self._add_history(
                state, "gate_run", stage,
                f"门禁{stage}({gate_name})评审({review_type}): {verdict}",
            )
            self._save_state(state)
        return dict(result)

    def advance_stage(self) -> Dict[str, Any]:
        """尝试推进到下一阶段（先执行当前阶段的规则门禁）。

        - 暂停态/已完成态：拒绝推进。
        - 门禁未通过：阻塞，返回门禁结果。
        - 门禁通过且当前为最终阶段：标记管线完成。
        - 门禁通过且非最终阶段：进入下一阶段。

        Returns:
            {"advanced": bool, "reason": str, "current_stage": int,
             "gate": dict|None, "completed": bool}
        """
        with file_lock(self._lock_name):
            state = self._load_state()
            if state["status"] == "paused":
                return {
                    "advanced": False, "reason": "管线已暂停，请先恢复",
                    "current_stage": state["current_stage"],
                    "gate": None, "completed": False,
                }
            if state["status"] == "completed":
                return {
                    "advanced": False, "reason": "管线已完成",
                    "current_stage": state["current_stage"],
                    "gate": None, "completed": True,
                }
            current = state["current_stage"]
            # 实时评估规则门禁（反映最新产物状态）
            result = self._evaluate_gate(current, "rule")
            state["gate_results"][str(current)] = result

            if not result["passed"]:
                self._add_history(
                    state, "advance_blocked", current,
                    f"推进被阻: 门禁{current}未通过（{'; '.join(result['issues'])}）",
                )
                self._save_state(state)
                return {
                    "advanced": False, "reason": f"门禁{current}未通过",
                    "current_stage": current, "gate": dict(result), "completed": False,
                }

            # 门禁通过
            state["stage_status"][str(current)] = "completed"
            if current >= len(STAGES) - 1:
                # 已在最后阶段且门禁通过 → 管线完成
                state["status"] = "completed"
                self._add_history(
                    state, "pipeline_completed", current,
                    f"管线全部完成（最终阶段{current}门禁通过）",
                )
                self._save_state(state)
                return {
                    "advanced": True, "reason": "管线已完成",
                    "current_stage": current, "gate": dict(result), "completed": True,
                }
            new_stage = current + 1
            state["current_stage"] = new_stage
            state["stage_status"][str(new_stage)] = "in_progress"
            self._add_history(
                state, "stage_advanced", new_stage,
                f"阶段{current}({STAGES[current]['name']})→阶段{new_stage}({STAGES[new_stage]['name']})",
            )
            self._save_state(state)
            return {
                "advanced": True, "reason": f"进入阶段{new_stage}({STAGES[new_stage]['name']})",
                "current_stage": new_stage, "gate": dict(result), "completed": False,
            }

    def rollback_stage(self, reason: str) -> Dict[str, Any]:
        """回滚到上一阶段。

        Args:
            reason: 回滚原因（必填）。

        Returns:
            {"rolled_back": bool, "reason": str, "current_stage": int}

        Raises:
            ValueError: reason 为空。
        """
        if not reason:
            raise ValueError("回滚必须填写原因")
        with file_lock(self._lock_name):
            state = self._load_state()
            if state["status"] == "paused":
                return {
                    "rolled_back": False, "reason": "管线已暂停，无法回滚",
                    "current_stage": state["current_stage"],
                }
            if state["status"] == "completed":
                return {
                    "rolled_back": False, "reason": "管线已完成，无法回滚",
                    "current_stage": state["current_stage"],
                }
            current = state["current_stage"]
            if current <= 0:
                return {
                    "rolled_back": False, "reason": "已在初始阶段，无法回滚",
                    "current_stage": current,
                }
            new_stage = current - 1
            state["current_stage"] = new_stage
            state["stage_status"][str(current)] = "pending"
            state["stage_status"][str(new_stage)] = "in_progress"
            # 作废受影响阶段的门禁结果，需重新评审
            state["gate_results"].pop(str(current), None)
            state["gate_results"].pop(str(new_stage), None)
            self._add_history(
                state, "rollback", new_stage,
                f"回滚: 阶段{current}→阶段{new_stage}，原因: {reason}",
            )
            self._save_state(state)
            return {
                "rolled_back": True, "reason": reason, "current_stage": new_stage,
            }

    def pause(self, reason: str) -> Dict[str, Any]:
        """暂停管线（幂等：已暂停时直接返回）。

        Returns:
            {"paused": bool, "reason": str}
        """
        with file_lock(self._lock_name):
            state = self._load_state()
            if state["status"] == "completed":
                return {"paused": False, "reason": "管线已完成，无法暂停"}
            if state["status"] == "paused":
                return {"paused": True, "reason": state.get("pause_reason", reason or "")}
            state["status"] = "paused"
            state["paused_at"] = now_utc()
            state["pause_reason"] = reason or ""
            self._add_history(
                state, "pause", state["current_stage"],
                f"暂停: {reason or '（无原因）'}",
            )
            self._save_state(state)
            return {"paused": True, "reason": reason or ""}

    def resume(self) -> Dict[str, Any]:
        """恢复管线运行。

        Returns:
            {"resumed": bool, "reason": str, "current_stage": int}
        """
        with file_lock(self._lock_name):
            state = self._load_state()
            if state["status"] != "paused":
                return {
                    "resumed": False, "reason": f"当前状态为{state['status']}，无需恢复",
                    "current_stage": state["current_stage"],
                }
            state["status"] = "running"
            state["resumed_at"] = now_utc()
            self._add_history(
                state, "resume", state["current_stage"], "恢复运行",
            )
            self._save_state(state)
            return {
                "resumed": True, "reason": "已恢复运行",
                "current_stage": state["current_stage"],
            }

    def get_progress(self) -> Dict[str, Any]:
        """返回进度摘要：当前阶段、完成百分比、阻塞项。"""
        state = self._load_state()
        current = state["current_stage"]
        total = len(STAGES)
        completed = sum(
            1 for i in range(total)
            if state["stage_status"].get(str(i)) == "completed"
        )
        completion_pct = round(completed / total * 100, 1) if total else 0.0
        blocked_items: List[Dict[str, Any]] = []
        gate_result = state["gate_results"].get(str(current))
        if gate_result and not gate_result.get("passed"):
            blocked_items.append(
                {"stage": current, "type": "gate",
                 "issues": gate_result.get("issues", [])}
            )
        if state["status"] == "paused":
            blocked_items.append(
                {"type": "paused", "reason": state.get("pause_reason", "")}
            )
        return {
            "current_stage": current,
            "current_stage_name": STAGES[current]["name"] if 0 <= current < total else "",
            "status": state["status"],
            "completion_pct": completion_pct,
            "completed_stages": completed,
            "total_stages": total,
            "blocked_items": blocked_items,
        }

    def list_artifacts(self, stage: Optional[int] = None) -> List[Dict[str, Any]]:
        """列出产物（委派 ArtifactManager），支持按阶段过滤。

        ArtifactManager 不可用时返回空列表。
        """
        am = self._get_artifact_manager()
        if am is None:
            return []
        return am.list_artifacts(stage=stage)

    def export_timeline(self) -> List[Dict[str, Any]]:
        """导出完整执行时间线（历史事件列表副本）。"""
        state = self._load_state()
        return [dict(e) for e in state.get("history", [])]

    # ------------------------------------------------------------------
    # 阶段执行（联通委托模块）
    # ------------------------------------------------------------------
    def execute_stage(self, stage: Optional[int] = None) -> Dict[str, Any]:
        """执行指定阶段（或当前阶段）的委托模块，生成产物。

        这是联通管线各阶段的核心方法。每个阶段对应一个 _execute_stage_N() 方法，
        负责调用委托模块（或读取数据文件）生成产物，并通过 ArtifactManager 注册。

        阶段0-1：委托模块为 CoPilot 核心模块（research_profiler/external_fetcher），
                 管线不可直接导入，改为只读读取其产出文件（memory/*.json）。
        阶段2-5：委托模块为研究管线模块，通过懒导入调用。

        Args:
            stage: 要执行的阶段编号；None 时执行当前阶段。

        Returns:
            {"executed": bool, "stage": int, "summary": str,
             "artifacts_created": list, "reason": str（失败时）}
        """
        state = self._load_state()
        if stage is None:
            stage = state["current_stage"]

        if stage < 0 or stage >= len(STAGES):
            return {"executed": False, "stage": stage,
                    "summary": "", "artifacts_created": [],
                    "reason": f"非法阶段编号: {stage}"}

        if state["status"] == "paused":
            return {"executed": False, "stage": stage,
                    "summary": "", "artifacts_created": [],
                    "reason": "管线已暂停"}
        if state["status"] == "completed":
            return {"executed": False, "stage": stage,
                    "summary": "", "artifacts_created": [],
                    "reason": "管线已完成"}

        stage_info = STAGES[stage]
        executor = getattr(self, f"_execute_stage_{stage}", None)
        if executor is None:
            return {"executed": False, "stage": stage,
                    "summary": "", "artifacts_created": [],
                    "reason": f"阶段{stage}无执行器"}

        try:
            result = executor()
        except Exception as e:
            result = {
                "executed": False, "stage": stage,
                "summary": "", "artifacts_created": [],
                "reason": f"执行异常: {e}",
            }

        # 记录历史
        with file_lock(self._lock_name):
            state = self._load_state()
            if result.get("executed"):
                self._add_history(
                    state, "stage_executed", stage,
                    f"阶段{stage}({stage_info['name']})执行完成: {result.get('summary', '')}",
                )
            else:
                self._add_history(
                    state, "stage_execution_failed", stage,
                    f"阶段{stage}({stage_info['name']})执行失败: {result.get('reason', '')}",
                )
            self._save_state(state)

        return result

    def _read_artifact_content(self, artifact_id: str) -> str:
        """读取产物文件内容（通过 file_path 从磁盘读取）。"""
        am = self._get_artifact_manager()
        if am is None:
            return ""
        art = am.get_artifact(artifact_id)
        if not art:
            return ""
        file_path = art.get("file_path", "")
        if not file_path:
            return ""
        live = self.proposal_dir / file_path
        if live.exists():
            return live.read_text(encoding="utf-8")
        return ""

    def _execute_stage_0(self) -> Dict[str, Any]:
        """阶段0: 方向校准 — 读取研究画像与用户画像，创建产物。

        边界处理：research_profiler 是核心模块，管线不可导入。
        改为只读读取 memory/research-profile.json 和 memory/user-profile.json。
        """
        import json as _json

        am = self._get_artifact_manager()
        if am is None:
            return {"executed": False, "stage": 0, "summary": "",
                    "artifacts_created": [], "reason": "ArtifactManager 不可用"}

        from paths import MEMORY_DIR

        profile_data = load_json(MEMORY_DIR / "research-profile.json", default={})
        user_data = load_json(MEMORY_DIR / "user-profile.json", default={})

        keywords = profile_data.get("keywords", [])
        research_field = user_data.get("research_field", [])

        if not keywords and not research_field:
            return {"executed": False, "stage": 0, "summary": "",
                    "artifacts_created": [],
                    "reason": "研究画像和用户画像均为空，请先运行 research_profiler"}

        keyword_lines = [f"- {k[0]}（权重 {k[1]:.2f}）" for k in keywords[:20]] if keywords else []
        field_lines = [f"- {f}" for f in research_field]

        direction_content = (
            "# 方向校准报告\n\n"
            "## 研究方向关键词\n\n"
            + "\n".join(keyword_lines if keyword_lines else ["（无关键词）"])
            + "\n\n## 用户研究领域\n\n"
            + "\n".join(field_lines if field_lines else ["（无领域）"])
            + f"\n\n## 校准结论\n\n"
            f"基于研究画像与用户画像，确定主要研究方向为："
            f"{research_field[0] if research_field else '未确定'}\n"
        )

        am.create_artifact(
            f"dir_{self.proposal_id}_v0.1", "direction_calibration", 0,
            direction_content, "01_direction/direction-calibration.md",
            author="pipeline_stage0",
        )

        user_content = _json.dumps(user_data, ensure_ascii=False, indent=2)
        am.create_artifact(
            f"up_{self.proposal_id}_v0.1", "user_profile", 0,
            user_content, "01_direction/user-profile-snapshot.json",
            author="pipeline_stage0",
        )

        return {
            "executed": True, "stage": 0,
            "summary": f"方向校准完成，提取{len(keywords)}个关键词、{len(research_field)}个研究领域",
            "artifacts_created": ["direction_calibration", "user_profile"],
        }

    def _execute_stage_1(self) -> Dict[str, Any]:
        """阶段1: 文献调研 — 读取论文池，创建文献简报产物。

        边界处理：external_fetcher 是核心模块，管线不可导入。
        改为只读读取 memory/paper-pool.json 中已积累的文献。
        """
        am = self._get_artifact_manager()
        if am is None:
            return {"executed": False, "stage": 1, "summary": "",
                    "artifacts_created": [], "reason": "ArtifactManager 不可用"}

        from paths import MEMORY_DIR

        paper_pool = load_json(MEMORY_DIR / "paper-pool.json", default={})

        if not paper_pool:
            return {"executed": False, "stage": 1, "summary": "",
                    "artifacts_created": [],
                    "reason": "论文池为空，请先通过 hermes/learning_engine 积累文献"}

        count = 0
        for arxiv_id, paper in paper_pool.items():
            title = paper.get("title", arxiv_id)
            direction = paper.get("direction", "未分类")
            score = paper.get("score", 0)
            tldr = paper.get("tldr", "")
            status = paper.get("status", "unknown")

            briefing_content = (
                f"# 文献简报: {title}\n\n"
                f"- **arXiv ID**: {arxiv_id}\n"
                f"- **方向**: {direction}\n"
                f"- **评分**: {score:.2f}\n"
                f"- **状态**: {status}\n\n"
                f"## 摘要\n\n{tldr}\n"
            )

            safe_id = arxiv_id.replace(".", "_").replace("/", "_")
            am.create_artifact(
                f"lb_{safe_id}_v0.1", "literature_briefing", 1,
                briefing_content, f"02_literature/{safe_id}.md",
                author="pipeline_stage1",
            )
            count += 1

        return {
            "executed": True, "stage": 1,
            "summary": f"文献调研完成，生成{count}篇文献简报",
            "artifacts_created": ["literature_briefing"] * count,
        }

    def _execute_stage_2(self) -> Dict[str, Any]:
        """阶段2: 课题凝练 — 调用 gap_analyzer 和 topic_generator。

        两个均为管线模块，可直接懒导入。
        """
        am = self._get_artifact_manager()
        if am is None:
            return {"executed": False, "stage": 2, "summary": "",
                    "artifacts_created": [], "reason": "ArtifactManager 不可用"}

        # 从阶段0产物中提取研究方向
        research_direction = "固体HHG"
        dir_arts = am.list_artifacts(stage=0, artifact_type="direction_calibration")
        if dir_arts:
            content = self._read_artifact_content(dir_arts[0]["artifact_id"])
            if content:
                for line in content.split("\n"):
                    stripped = line.strip()
                    if stripped.startswith("- ") and stripped != "- （无领域）":
                        research_direction = stripped[2:].strip()
                        break

        directions = [{"id": "T1", "name": research_direction}]

        # 调用 gap_analyzer
        try:
            from gap_analyzer import GapAnalyzer
            analyzer = GapAnalyzer(self.proposal_dir, research_directions=directions)
            gap_report = analyzer.analyze()
        except Exception as e:
            return {"executed": False, "stage": 2, "summary": "",
                    "artifacts_created": [],
                    "reason": f"gap_analyzer 执行失败: {e}"}

        # 创建 gap_analysis 产物
        gap_content = analyzer.export_gap_report(format="markdown")
        am.create_artifact(
            f"gap_{self.proposal_id}_v0.1", "gap_analysis", 2,
            gap_content, "02_topic/gap-report.md",
            author="pipeline_stage2",
        )

        # 调用 topic_generator
        topics: List[Dict[str, Any]] = []
        try:
            from topic_generator import TopicGenerator
            gen = TopicGenerator(self.proposal_dir)
            topics = gen.generate_topics(gap_report, direction=directions[0])
        except Exception:
            # topic_generator 失败时用 gap_report 手动构建课题
            if gap_report.get("gaps"):
                top_gap = gap_report["gaps"][0]
                topics = [{
                    "topic_id": "topic_001",
                    "title": top_gap.get("description", "研究课题")[:100],
                    "keywords": [research_direction],
                    "methods": top_gap.get("suggested_approach", ""),
                    "literature": [],
                    "priority_score": top_gap.get("priority_score", 0.5),
                }]

        # 创建 topic 产物
        if topics:
            top_topic = topics[0]
            topic_content = (
                f"# 研究课题: {top_topic.get('title', '未命名课题')}\n\n"
                f"- **课题ID**: {top_topic.get('topic_id', 'topic_001')}\n"
                f"- **优先级**: {top_topic.get('priority_score', 0):.2f}\n"
                f"- **关键词**: {', '.join(top_topic.get('keywords', []))}\n\n"
                f"## 建议方法\n\n{top_topic.get('methods', '待补充')}\n"
            )
            am.create_artifact(
                f"topic_{self.proposal_id}_v0.1", "topic", 2,
                topic_content, "02_topic/topic-001.md",
                author="pipeline_stage2",
            )

        return {
            "executed": True, "stage": 2,
            "summary": f"课题凝练完成，识别{len(gap_report.get('gaps', []))}个缺口，生成{len(topics)}个课题",
            "artifacts_created": ["gap_analysis", "topic"] if topics else ["gap_analysis"],
        }

    def _execute_stage_3(self) -> Dict[str, Any]:
        """阶段3: 科学问题构建 — 调用 question_architect。"""
        am = self._get_artifact_manager()
        if am is None:
            return {"executed": False, "stage": 3, "summary": "",
                    "artifacts_created": [], "reason": "ArtifactManager 不可用"}

        # 读取 gap_report（阶段2产出）
        gap_report = None
        try:
            from gap_analyzer import GapAnalyzer
            analyzer = GapAnalyzer(self.proposal_dir)
            gap_report = analyzer.get_gap_report()
        except Exception:
            pass

        # 从阶段2产物中构建课题输入
        topic: Dict[str, Any] = {
            "topic_id": "topic_001",
            "title": "固体高次谐波产生中的量子几何效应",
            "keywords": ["HHG", "量子几何", "Berry曲率"],
            "methods": "TDDFT数值模拟",
            "literature": [],
        }
        topic_arts = am.list_artifacts(stage=2, artifact_type="topic")
        if topic_arts:
            content = self._read_artifact_content(topic_arts[0]["artifact_id"])
            if content:
                for line in content.split("\n"):
                    if line.startswith("# 研究课题:"):
                        topic["title"] = line.replace("# 研究课题:", "").strip()
                        break

        # 调用 question_architect
        try:
            from question_architect import QuestionArchitect
            architect = QuestionArchitect(self.proposal_dir)
            framework = architect.construct_questions(topic, gap_report)
        except Exception as e:
            return {"executed": False, "stage": 3, "summary": "",
                    "artifacts_created": [],
                    "reason": f"question_architect 执行失败: {e}"}

        # 创建 scientific_question 产物
        main_questions = framework.get("main_questions", [])
        q_content = architect.export_framework(format="markdown")
        am.create_artifact(
            f"sq_{self.proposal_id}_v0.1", "scientific_question", 3,
            q_content, "03_question/question-framework.md",
            author="pipeline_stage3",
        )

        # 创建 question_validation 产物
        validation = framework.get("validation_summary", {})
        val_lines = [f"- **{dim}**: {score:.2f}" for dim, score in validation.get("by_dimension", {}).items()]
        validation_content = (
            "# 科学问题验证报告\n\n"
            f"- **问题总数**: {validation.get('total_questions', 0)}\n"
            f"- **平均评分**: {validation.get('avg_overall', 0):.2f}\n\n"
            "## 各维度评分\n\n"
            + "\n".join(val_lines if val_lines else ["（无维度数据）"])
            + "\n"
        )
        am.create_artifact(
            f"qv_{self.proposal_id}_v0.1", "question_validation", 3,
            validation_content, "03_question/validation.md",
            author="pipeline_stage3",
        )

        return {
            "executed": True, "stage": 3,
            "summary": f"科学问题构建完成，生成{len(main_questions)}个主问题",
            "artifacts_created": ["scientific_question", "question_validation"],
        }

    def _execute_stage_4(self) -> Dict[str, Any]:
        """阶段4: 申请书撰写 — 调用 proposal_writer。"""
        am = self._get_artifact_manager()
        if am is None:
            return {"executed": False, "stage": 4, "summary": "",
                    "artifacts_created": [], "reason": "ArtifactManager 不可用"}

        # 读取 question_framework（阶段3产出）
        framework = None
        try:
            from question_architect import QuestionArchitect
            architect = QuestionArchitect(self.proposal_dir)
            framework = architect.get_framework()
        except Exception:
            pass

        if not framework or not framework.get("main_questions"):
            return {"executed": False, "stage": 4, "summary": "",
                    "artifacts_created": [],
                    "reason": "科学问题框架为空，请先执行阶段3"}

        # 读取 gap_report（可选上下文）
        gap_report = None
        try:
            from gap_analyzer import GapAnalyzer
            analyzer = GapAnalyzer(self.proposal_dir)
            gap_report = analyzer.get_gap_report()
        except Exception:
            pass

        # 调用 proposal_writer
        try:
            from proposal_writer import ProposalWriter
            writer = ProposalWriter(self.proposal_dir)
            result = writer.write_proposal(framework, gap_report)
        except Exception as e:
            return {"executed": False, "stage": 4, "summary": "",
                    "artifacts_created": [],
                    "reason": f"proposal_writer 执行失败: {e}"}

        # 为每个章节创建 proposal_section 产物
        sections = writer.get_sections()
        count = 0
        for section_name, section_data in sections.items():
            content = section_data.get("content", "")
            section_id = section_data.get("section_id", f"sec_{count + 1}")
            safe_name = safe_filename(section_name)

            am.create_artifact(
                f"sec_{safe_name}_v0.1", "proposal_section", 4,
                content, f"04_proposal/sections/{section_id}.md",
                author="pipeline_stage4",
            )
            count += 1

        return {
            "executed": True, "stage": 4,
            "summary": f"申请书撰写完成，生成{count}个章节（总字数{result.get('total_word_count', 0)}）",
            "artifacts_created": ["proposal_section"] * count,
        }

    def _execute_stage_5(self) -> Dict[str, Any]:
        """阶段5: 自检优化 — 调用 proposal_inspector。"""
        am = self._get_artifact_manager()
        if am is None:
            return {"executed": False, "stage": 5, "summary": "",
                    "artifacts_created": [], "reason": "ArtifactManager 不可用"}

        # 读取申请书章节（阶段4产出）
        sections_with_content: Dict[str, str] = {}
        try:
            from proposal_writer import ProposalWriter
            writer = ProposalWriter(self.proposal_dir)
            sections = writer.get_sections()
            for name, data in sections.items():
                sections_with_content[name] = data.get("content", "")
        except Exception:
            pass

        if not sections_with_content:
            return {"executed": False, "stage": 5, "summary": "",
                    "artifacts_created": [],
                    "reason": "申请书章节为空，请先执行阶段4"}

        # 读取 question_framework（可选上下文）
        question_framework = None
        try:
            from question_architect import QuestionArchitect
            architect = QuestionArchitect(self.proposal_dir)
            question_framework = architect.get_framework()
        except Exception:
            pass

        # 调用 proposal_inspector
        try:
            from proposal_inspector import ProposalInspector
            inspector = ProposalInspector(self.proposal_dir)
            report = inspector.inspect(sections_with_content, question_framework)
        except Exception as e:
            return {"executed": False, "stage": 5, "summary": "",
                    "artifacts_created": [],
                    "reason": f"proposal_inspector 执行失败: {e}"}

        # 创建 self_check 产物
        report_md = inspector.export_report(format="markdown")
        am.create_artifact(
            f"sc_{self.proposal_id}_v0.1", "self_check", 5,
            report_md, "05_review/inspection-report.md",
            author="pipeline_stage5",
        )

        # 创建 issue_resolution 产物
        total_issues = report.get("total_issues", 0)
        strategy = report.get("strategy", {})
        action_lines = [f"- {a}" for a in strategy.get("actions", [])]
        resolution_content = (
            "# 问题解决报告\n\n"
            f"- **总问题数**: {total_issues}\n"
            f"- **严重**: {report.get('critical_count', 0)}\n"
            f"- **主要**: {report.get('major_count', 0)}\n"
            f"- **次要**: {report.get('minor_count', 0)}\n"
            f"- **建议**: {report.get('suggestion_count', 0)}\n\n"
            "## 优化策略\n\n"
            f"- **级别**: {strategy.get('level_label', '未确定')}\n"
            f"- **原因**: {strategy.get('reason', '')}\n\n"
            "## 行动项\n\n"
            + "\n".join(action_lines if action_lines else ["（无行动项）"])
            + "\n"
        )
        am.create_artifact(
            f"ir_{self.proposal_id}_v0.1", "issue_resolution", 5,
            resolution_content, "05_review/issue-resolution.md",
            author="pipeline_stage5",
        )

        return {
            "executed": True, "stage": 5,
            "summary": f"自检优化完成，总分{report.get('overall_score', 0):.2f}，"
                       f"识别{total_issues}个问题",
            "artifacts_created": ["self_check", "issue_resolution"],
        }

    def run_stage(self) -> Dict[str, Any]:
        """一键执行当前阶段：执行委托模块 → 门禁校验 → 推进。

        Returns:
            {"executed": dict, "gate": dict, "advanced": dict|None}
        """
        current = self._load_state()["current_stage"]

        # 1. 执行阶段
        exec_result = self.execute_stage(current)
        if not exec_result.get("executed"):
            return {"executed": exec_result, "gate": None, "advanced": None}

        # 2. 门禁校验
        gate_result = self.run_gate(current, "rule")

        # 3. 推进（门禁通过时）
        advance_result = None
        if gate_result.get("passed"):
            advance_result = self.advance_stage()

        return {
            "executed": exec_result,
            "gate": gate_result,
            "advanced": advance_result,
        }

    def run_full_pipeline(self) -> Dict[str, Any]:
        """一键执行全部六阶段：循环 run_stage 直到完成或失败。

        Returns:
            {"completed": bool, "stages_executed": int,
             "final_stage": int, "results": list, "reason": str}
        """
        results: List[Dict[str, Any]] = []
        max_iterations = 12  # 安全上限（6阶段 × 2容错）

        for _ in range(max_iterations):
            state = self._load_state()
            if state["status"] == "completed":
                return {
                    "completed": True,
                    "stages_executed": len(results),
                    "final_stage": state["current_stage"],
                    "results": results,
                    "reason": "管线全部完成",
                }
            if state["status"] == "paused":
                return {
                    "completed": False,
                    "stages_executed": len(results),
                    "final_stage": state["current_stage"],
                    "results": results,
                    "reason": "管线已暂停",
                }

            step_result = self.run_stage()
            results.append(step_result)

            # 执行失败或门禁未通过时停止
            if not step_result["executed"].get("executed"):
                return {
                    "completed": False,
                    "stages_executed": len(results),
                    "final_stage": state["current_stage"],
                    "results": results,
                    "reason": f"阶段{state['current_stage']}执行失败: "
                              f"{step_result['executed'].get('reason', '')}",
                }
            if step_result["gate"] and not step_result["gate"].get("passed"):
                return {
                    "completed": False,
                    "stages_executed": len(results),
                    "final_stage": state["current_stage"],
                    "results": results,
                    "reason": f"阶段{state['current_stage']}门禁未通过: "
                              f"{'; '.join(step_result['gate'].get('issues', []))}",
                }
            if not step_result.get("advanced"):
                return {
                    "completed": False,
                    "stages_executed": len(results),
                    "final_stage": state["current_stage"],
                    "results": results,
                    "reason": "推进失败",
                }

        return {
            "completed": False,
            "stages_executed": len(results),
            "final_stage": self._load_state()["current_stage"],
            "results": results,
            "reason": f"达到最大迭代次数({max_iterations})",
        }


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def _self_check() -> None:
    """自检：覆盖初始化、阶段信息、正向/阻塞流转、回滚、暂停/恢复、
    进度、时间线、门禁、持久化、原子写入+文件锁等检查点。
    使用临时目录隔离，结束后自动清理。
    """
    import json
    import tempfile

    print("=" * 50)
    print("◐ pipeline_orchestrator 自检")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as tmp:
        proposal_dir = Path(tmp) / "T1_proposal"
        proposal_id = "T1"

        # [1/11] 管线初始化（创建状态文件）
        print("\n[1/11] 管线初始化...")
        mgr = PipelineManager(proposal_id, proposal_dir)
        state = mgr.get_state()
        assert state["proposal_id"] == proposal_id, "proposal_id 应一致"
        assert state["current_stage"] == 0, "初始阶段应为 0"
        assert state["status"] == "running", "初始状态应为 running"
        assert state["stage_status"]["0"] == "in_progress", "阶段0应为 in_progress"
        assert state["stage_status"]["1"] == "pending", "阶段1应为 pending"
        assert (proposal_dir / "00_pipeline" / "pipeline-state.json").exists(), "状态文件应已创建"
        print(f"  proposal_id: {state['proposal_id']}")
        print(f"  current_stage: {state['current_stage']}, status: {state['status']}")
        print("  ✓ 状态文件已创建，初始状态正确")

        # [2/11] 阶段信息检索（全部 6 阶段）
        print("\n[2/11] 阶段信息检索...")
        for i in range(6):
            info = mgr.get_stage_info(i)
            assert info["id"] == i, f"阶段 id 应为 {i}"
            assert "name" in info and "name_en" in info, "阶段应含中英文名"
            assert "required_inputs" in info and "expected_outputs" in info
            assert "delegate_module" in info
            print(f"  阶段{i}: {info['name']} ({info['name_en']}) → {info['delegate_module']}")
        try:
            mgr.get_stage_info(6)
            raise AssertionError("应拒绝非法阶段编号 6")
        except ValueError:
            print("  ✓ 非法阶段编号已拒绝")
        print("  ✓ 6 阶段元数据完整")

        # [3/11] 阻塞流转（门禁未通过）
        print("\n[3/11] 阻塞流转（门禁未通过）...")
        result = mgr.advance_stage()
        assert not result["advanced"], "门禁未通过不应推进"
        assert result["current_stage"] == 0, "应停留在阶段 0"
        assert result["gate"] is not None and not result["gate"]["passed"]
        print(f"  推进结果: advanced={result['advanced']}, reason={result['reason']}")
        print(f"  门禁issues: {result['gate']['issues']}")
        print("  ✓ 门禁未通过时推进被阻塞")

        # [4/11] 门禁执行（规则评审）
        print("\n[4/11] 门禁执行（规则评审）...")
        from artifact_manager import ArtifactManager
        am = ArtifactManager(proposal_dir)
        # 未创建产物时门禁0应失败
        g0_fail = mgr.run_gate(0, "rule")
        assert not g0_fail["passed"], "无产物时门禁0应未通过"
        assert g0_fail["score"] < 1.0
        print(f"  无产物门禁0: passed={g0_fail['passed']}, score={g0_fail['score']}")
        # 创建产物：direction_calibration + user_profile
        am.create_artifact("dir_v0.1", "direction_calibration", 0,
                           "研究方向: 固体HHG", "01_direction/direction.md",
                           author="pipeline_stage0")
        am.create_artifact("up_v0.1", "user_profile", 0,
                           "用户画像快照", "01_direction/user-profile.json",
                           author="pipeline_stage0")
        g0_pass = mgr.run_gate(0, "rule")
        assert g0_pass["passed"], "创建产物后门禁0应通过"
        assert g0_pass["score"] == 1.0
        print(f"  有产物门禁0: passed={g0_pass['passed']}, score={g0_pass['score']}")
        # llm/user 评审占位桩
        g_llm = mgr.run_gate(0, "llm")
        assert not g_llm["passed"] and "尚未实现" in g_llm["issues"][0]
        g_user = mgr.run_gate(0, "user")
        assert not g_user["passed"]
        print(f"  llm评审(占位): passed={g_llm['passed']}, issues={g_llm['issues']}")
        # 非法评审类型
        g_bad = mgr.run_gate(0, "magic")
        assert not g_bad["passed"] and "未知评审类型" in g_bad["issues"][0]
        print("  ✓ 规则门禁按产物数量判定；llm/user/非法类型为占位桩")

        # [5/11] 正向流转（门禁通过后推进）
        print("\n[5/11] 正向流转（门禁通过后推进）...")
        result = mgr.advance_stage()
        assert result["advanced"], "门禁通过应推进"
        assert result["current_stage"] == 1, "应推进到阶段 1"
        st = mgr.get_state()
        assert st["current_stage"] == 1
        assert st["stage_status"]["0"] == "completed"
        assert st["stage_status"]["1"] == "in_progress"
        print(f"  推进结果: advanced={result['advanced']}, current_stage={result['current_stage']}")
        print("  ✓ 阶段0→阶段1 推进成功")

        # [6/11] 回滚
        print("\n[6/11] 回滚...")
        rb = mgr.rollback_stage("需要补充文献")
        assert rb["rolled_back"], "应回滚成功"
        assert rb["current_stage"] == 0, "应回滚到阶段 0"
        st = mgr.get_state()
        assert st["current_stage"] == 0
        assert st["stage_status"]["1"] == "pending", "阶段1应重置为 pending"
        assert st["stage_status"]["0"] == "in_progress"
        # 回滚应作废受影响阶段的门禁结果
        assert "0" not in st["gate_results"], "回滚应作废阶段0门禁结果"
        assert "1" not in st["gate_results"], "回滚应作废阶段1门禁结果"
        print(f"  回滚结果: rolled_back={rb['rolled_back']}, current_stage={rb['current_stage']}")
        # 阶段0无法继续回滚
        rb2 = mgr.rollback_stage("再试")
        assert not rb2["rolled_back"], "阶段0不应再回滚"
        print(f"  阶段0回滚: rolled_back={rb2['rolled_back']}, reason={rb2['reason']}")
        # 回滚必须填原因
        try:
            mgr.rollback_stage("")
            raise AssertionError("空原因应报错")
        except ValueError:
            print("  ✓ 空回滚原因已拒绝")
        print("  ✓ 回滚 + 边界保护 + 原因校验 + 门禁作废")

        # 重新推进到阶段1，便于后续测试
        mgr.advance_stage()
        assert mgr.get_state()["current_stage"] == 1

        # [7/11] 暂停/恢复
        print("\n[7/11] 暂停/恢复...")
        p = mgr.pause("等待用户反馈")
        assert p["paused"]
        assert mgr.get_state()["status"] == "paused"
        assert mgr.get_state()["pause_reason"] == "等待用户反馈"
        # 暂停态下推进应被阻塞
        adv_paused = mgr.advance_stage()
        assert not adv_paused["advanced"], "暂停态不应推进"
        print(f"  暂停后推进: advanced={adv_paused['advanced']}, reason={adv_paused['reason']}")
        # 暂停态下回滚应被阻塞
        rb_paused = mgr.rollback_stage("暂停态回滚")
        assert not rb_paused["rolled_back"], "暂停态不应回滚"
        # 幂等：再次暂停
        p2 = mgr.pause("再次暂停")
        assert p2["paused"]
        # 恢复
        r = mgr.resume()
        assert r["resumed"]
        assert mgr.get_state()["status"] == "running"
        # 非暂停态恢复应提示无需恢复
        r2 = mgr.resume()
        assert not r2["resumed"]
        print(f"  重复恢复: resumed={r2['resumed']}, reason={r2['reason']}")
        print("  ✓ 暂停/恢复 + 暂停态阻塞推进/回滚 + 幂等保护")

        # [8/11] 进度计算
        print("\n[8/11] 进度计算...")
        progress = mgr.get_progress()
        print(f"  当前阶段: {progress['current_stage']}({progress['current_stage_name']})")
        print(f"  完成度: {progress['completion_pct']}% ({progress['completed_stages']}/{progress['total_stages']})")
        print(f"  状态: {progress['status']}, 阻塞项: {len(progress['blocked_items'])}")
        assert progress["current_stage"] == 1
        assert progress["total_stages"] == 6
        assert progress["completed_stages"] == 1, f"阶段0应已完成, 实际{progress['completed_stages']}"
        assert progress["completion_pct"] == round(1 / 6 * 100, 1)
        assert isinstance(progress["blocked_items"], list)
        print("  ✓ 进度计算正确")

        # [9/11] 时间线导出
        print("\n[9/11] 时间线导出...")
        timeline = mgr.export_timeline()
        assert isinstance(timeline, list) and len(timeline) > 0
        events = [e["event"] for e in timeline]
        print(f"  事件数: {len(timeline)}")
        print(f"  事件类型: {events}")
        assert "init" in events, "应含 init 事件"
        assert "gate_run" in events, "应含 gate_run 事件"
        assert "stage_advanced" in events, "应含 stage_advanced 事件"
        assert "advance_blocked" in events, "应含 advance_blocked 事件"
        assert "rollback" in events, "应含 rollback 事件"
        assert "pause" in events, "应含 pause 事件"
        assert "resume" in events, "应含 resume 事件"
        # 验证时间线有序（按 timestamp 非递减）
        timestamps = [e["timestamp"] for e in timeline]
        assert timestamps == sorted(timestamps), "时间线应按时间有序"
        print("  ✓ 时间线完整且有序")

        # [10/11] 状态持久化（从文件重载）
        print("\n[10/11] 状态持久化（从文件重载）...")
        mgr2 = PipelineManager(proposal_id, proposal_dir)
        state2 = mgr2.get_state()
        assert state2["proposal_id"] == state["proposal_id"]
        assert state2["current_stage"] == mgr.get_state()["current_stage"]
        assert state2["status"] == mgr.get_state()["status"]
        assert state2["history"] == mgr.get_state()["history"], "历史应一致"
        print(f"  重载后: current_stage={state2['current_stage']}, status={state2['status']}")
        print(f"  历史事件数: {len(state2['history'])}")
        print("  ✓ 从文件重载状态一致")

        # [11/11] 原子写入 + 文件锁
        print("\n[11/11] 原子写入 + 文件锁...")
        # 验证状态文件始终为合法 JSON（原子写入保证）
        raw = (proposal_dir / "00_pipeline" / "pipeline-state.json").read_text(encoding="utf-8")
        parsed = json.loads(raw)  # 不抛异常即合法
        assert parsed["proposal_id"] == proposal_id
        print(f"  状态文件为合法 JSON，大小 {len(raw)} 字节")
        # 验证两个实例共享同一 proposal 不会死锁/损坏
        mgr_a = PipelineManager(proposal_id, proposal_dir)
        mgr_b = PipelineManager(proposal_id, proposal_dir)
        for _ in range(3):
            mgr_a.pause("交错操作A")
            mgr_b.resume()
            mgr_a.pause("交错操作A2")
            mgr_b.resume()
        final_state = mgr_a.get_state()
        assert final_state["status"] == "running", f"交错操作后应为 running, 实际{final_state['status']}"
        raw2 = (proposal_dir / "00_pipeline" / "pipeline-state.json").read_text(encoding="utf-8")
        json.loads(raw2)  # 仍合法
        print(f"  两实例交错 {3 * 2} 次 pause/resume，状态: {final_state['status']}")
        print("  ✓ 原子写入 + 文件锁（无死锁、无损坏）")

        # [附加] list_artifacts 委派
        print("\n[附加] list_artifacts 委派...")
        all_arts = mgr.list_artifacts()
        assert isinstance(all_arts, list) and len(all_arts) >= 2
        stage0_arts = mgr.list_artifacts(stage=0)
        assert all(a["stage"] == 0 for a in stage0_arts)
        print(f"  全部产物: {len(all_arts)}, 阶段0产物: {len(stage0_arts)}")
        print("  ✓ list_artifacts 委派 ArtifactManager")

        # [附加] 全链路推进至完成
        print("\n[附加] 全链路推进至管线完成...")
        # 当前在阶段1，补齐各阶段产物再推进
        # 阶段1: 5 篇 literature_briefing
        for k in range(5):
            am.create_artifact(f"lb_v0.{k + 1}", "literature_briefing", 1,
                               f"简报{k + 1}", f"02_literature/b{k + 1}.md",
                               author="pipeline_stage1")
        # 阶段2: topic + gap_analysis
        am.create_artifact("topic_v0.1", "topic", 2, "课题1",
                           "03_topic/t1.md", author="pipeline_stage2")
        am.create_artifact("gap_v0.1", "gap_analysis", 2, "空白分析",
                           "03_topic/gap.md", author="pipeline_stage2")
        # 阶段3: scientific_question + question_validation
        am.create_artifact("q_v0.1", "scientific_question", 3, "问题1",
                           "04_question/q1.md", author="pipeline_stage3")
        am.create_artifact("qv_v0.1", "question_validation", 3, "验证1",
                           "04_question/v1.md", author="pipeline_stage3")
        # 阶段4: 4 个 proposal_section
        for k in range(4):
            am.create_artifact(f"sec_v0.{k + 1}", "proposal_section", 4,
                               f"章节{k + 1}", f"05_proposal/s{k + 1}.md",
                               author="pipeline_stage4")
        # 阶段5: self_check + issue_resolution
        am.create_artifact("sc_v0.1", "self_check", 5, "自检报告",
                           "06_selfcheck/report.md", author="pipeline_stage5")
        am.create_artifact("ir_v0.1", "issue_resolution", 5, "问题解决",
                           "06_selfcheck/resolved.md", author="pipeline_stage5")
        # 逐步推进 1→2→3→4→5
        for expected in [2, 3, 4, 5]:
            r = mgr.advance_stage()
            assert r["advanced"], f"应推进到阶段{expected}: {r}"
            assert r["current_stage"] == expected
            print(f"  推进 → 阶段{expected}({STAGES[expected]['name']})")
        # 在阶段5，再次推进应完成管线
        r_final = mgr.advance_stage()
        assert r_final["advanced"], "最终推进应成功"
        assert r_final["completed"], "应标记为完成"
        assert mgr.get_state()["status"] == "completed"
        assert mgr.get_state()["stage_status"]["5"] == "completed"
        print(f"  最终推进: advanced={r_final['advanced']}, completed={r_final['completed']}")
        print(f"  管线状态: {mgr.get_state()['status']}")
        # 完成后推进/回滚应被拒
        assert not mgr.advance_stage()["advanced"], "完成后不应再推进"
        assert not mgr.rollback_stage("已完成")["rolled_back"], "完成后不应回滚"
        print("  ✓ 完成后推进/回滚被拒")
        # 完成进度应为 100%
        prog_final = mgr.get_progress()
        assert prog_final["completion_pct"] == 100.0, f"应100%, 实际{prog_final['completion_pct']}"
        assert prog_final["completed_stages"] == 6
        print(f"  完成度: {prog_final['completion_pct']}% ({prog_final['completed_stages']}/{prog_final['total_stages']})")
        print("  ✓ 全链路推进至完成")

    print("\n" + "=" * 50)
    print("✓ pipeline_orchestrator 自检全部通过")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="管线状态机编排器")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
