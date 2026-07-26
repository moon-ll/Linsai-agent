#!/usr/bin/env python3
"""提案生命周期管理 — 四阶段流转 + 对抗优化循环（v6.5.0）

用途：
    管理申请书从初稿→优化中→待校验→归档的完整生命周期，
    驱动 writer-critic 对抗优化循环，处理人工审核反馈。

架构关系：
    CoPilot 操作台
      ├── ProposalLifecycle（状态管理 + 流转控制）
      │   ├── transition()      → 四阶段间流转
      │   ├── optimize_cycle()  → writer-critic 对抗循环
      │   ├── check_done()      → 达标判定
      │   ├── archive()         → 归档 + 知识库
      │   └── submit_feedback() → 人工意见结构化处理
      │
    hermes 执行端
      ├── writer profile   → 撰写申请书（蓝队）
      ├── critic profile   → 对抗评审（红队）
      └── reviewer profile → 终审（独立于critic）

四阶段：
    drafts/        → 初稿（等待人工确认思路）
    optimizing/    → 优化中（自动对抗循环）
    pending_review/→ 待校验（等待人工核验）
    archived/      → 归档（通过人工审核，纳入知识库）

用法示例：
    >>> from proposal_lifecycle import ProposalLifecycle
    >>> lc = ProposalLifecycle()
    >>> lc.list_by_status("optimizing")
    >>> lc.transition("nsfc-2026-hhg", "drafts", "optimizing")
    >>> lc.optimize_cycle("nsfc-2026-hhg")
    >>> lc.submit_feedback("nsfc-2026-hhg", "意见文本")

命令行：
    python3 scripts/proposal_lifecycle.py --dashboard
    python3 scripts/proposal_lifecycle.py --transition nsfc-2026-hhg drafts optimizing
    python3 scripts/proposal_lifecycle.py --optimize nsfc-2026-hhg
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock
from paths import PROJECT_ROOT

__all__ = [
    "ProposalLifecycle",
    "LIFECYCLE_STAGES",
]

try:
    from logger import get_logger
    _log = get_logger("proposal_lifecycle")
except Exception:
    _log = None


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

PROPOSALS_ROOT = PROJECT_ROOT / "research_proposals"

# 四阶段目录名
LIFECYCLE_STAGES = ["drafts", "optimizing", "pending_review", "archived"]

# 项目类型
PROJECT_TYPES = ["general", "key", "major"]

# 优化循环默认参数
DEFAULT_MAX_ROUNDS = 10
DEFAULT_SCORE_THRESHOLD = 0.80  # 默认达标分数（会被项目类型标准覆盖）
DEFAULT_NO_IMPROVEMENT_LIMIT = 3  # 连续3轮无提升则判定无法提升


class ProposalLifecycle:
    """提案生命周期管理器。"""

    def __init__(self) -> None:
        self.root = PROPOSALS_ROOT
        self.lifecycle_path = self.root / "_lifecycle.json"
        self.standards_path = PROJECT_ROOT / "memory" / "nsfc-standards.json"
        self.root.mkdir(parents=True, exist_ok=True)
        for stage in LIFECYCLE_STAGES:
            (self.root / stage).mkdir(parents=True, exist_ok=True)
        self._ensure_lifecycle_state()

    # ------------------------------------------------------------------
    # 状态管理
    # ------------------------------------------------------------------

    def _ensure_lifecycle_state(self) -> None:
        """确保全局生命周期状态文件存在。"""
        if not self.lifecycle_path.exists():
            default = {
                "proposals": {},  # {proposal_id: {status, project_type, ...}}
                "updated_at": now_utc(),
            }
            save_json(self.lifecycle_path, default)

    def _load_state(self) -> Dict[str, Any]:
        return load_json(self.lifecycle_path, default={"proposals": {}})

    def _save_state(self, state: Dict[str, Any]) -> None:
        state["updated_at"] = now_utc()
        save_json(self.lifecycle_path, state)

    def _get_proposal_state(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        state = self._load_state()
        return state["proposals"].get(proposal_id)

    def _set_proposal_state(self, proposal_id: str, data: Dict[str, Any]) -> None:
        with file_lock("proposal-lifecycle"):
            state = self._load_state()
            state["proposals"][proposal_id] = data
            self._save_state(state)

    def _find_proposal_dir(self, proposal_id: str) -> Optional[Path]:
        """在四个阶段目录中查找 proposal 目录。"""
        for stage in LIFECYCLE_STAGES:
            d = self.root / stage / proposal_id
            if d.exists():
                return d
        return None

    # ------------------------------------------------------------------
    # 注册新 proposal
    # ------------------------------------------------------------------

    def register(
        self,
        proposal_id: str,
        project_type: str = "general",
        source: str = "new",
        source_detail: str = "",
    ) -> Dict[str, Any]:
        """注册新 proposal 到初稿区。

        Args:
            proposal_id: 课题 ID
            project_type: 项目类型（general/key/major）
            source: 来源（new=全新/expansion=扩展归档课题）
            source_detail: 来源详情

        Returns:
            {success, proposal_id, status, path}
        """
        if project_type not in PROJECT_TYPES:
            return {"success": False, "error": f"非法项目类型: {project_type}"}

        # 如果已存在，不重复注册
        existing = self._get_proposal_state(proposal_id)
        if existing:
            return {
                "success": False,
                "error": f"proposal 已存在，当前状态: {existing.get('status')}",
            }

        target_dir = self.root / "drafts" / proposal_id
        target_dir.mkdir(parents=True, exist_ok=True)

        state_data = {
            "status": "drafts",
            "project_type": project_type,
            "source": source,
            "source_detail": source_detail,
            "created_at": now_utc(),
            "updated_at": now_utc(),
            "optimization_rounds": 0,
            "last_score": 0.0,
            "score_history": [],
            "human_feedback_count": 0,
            "transition_history": [
                {"to": "drafts", "at": now_utc(), "reason": "注册新 proposal"}
            ],
        }
        self._set_proposal_state(proposal_id, state_data)

        if _log:
            _log.info(f"注册 proposal: {proposal_id} type={project_type} → drafts")

        return {
            "success": True,
            "proposal_id": proposal_id,
            "status": "drafts",
            "project_type": project_type,
            "path": str(target_dir.relative_to(PROJECT_ROOT)),
        }

    # ------------------------------------------------------------------
    # 状态流转
    # ------------------------------------------------------------------

    def transition(
        self,
        proposal_id: str,
        to_stage: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """流转 proposal 到指定阶段。

        Args:
            proposal_id: 课题 ID
            to_stage: 目标阶段（drafts/optimizing/pending_review/archived）
            reason: 流转原因

        Returns:
            {success, from_stage, to_stage, path}
        """
        if to_stage not in LIFECYCLE_STAGES:
            return {"success": False, "error": f"非法阶段: {to_stage}"}

        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": f"proposal 未注册: {proposal_id}"}

        from_stage = prop_state["status"]
        if from_stage == to_stage:
            return {"success": False, "error": f"已在 {to_stage} 阶段"}

        # 移动目录
        from_dir = self.root / from_stage / proposal_id
        to_dir = self.root / to_stage / proposal_id
        if not from_dir.exists():
            return {"success": False, "error": f"源目录不存在: {from_dir}"}

        to_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(from_dir), str(to_dir))

        # 更新状态
        prop_state["status"] = to_stage
        prop_state["updated_at"] = now_utc()
        prop_state["transition_history"].append({
            "from": from_stage, "to": to_stage, "at": now_utc(), "reason": reason
        })
        self._set_proposal_state(proposal_id, prop_state)

        if _log:
            _log.info(f"流转 {proposal_id}: {from_stage} → {to_stage} ({reason})")

        return {
            "success": True,
            "proposal_id": proposal_id,
            "from_stage": from_stage,
            "to_stage": to_stage,
            "path": str(to_dir.relative_to(PROJECT_ROOT)),
        }

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    def list_by_status(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """按状态列出 proposal。"""
        state = self._load_state()
        proposals = []
        for pid, data in state["proposals"].items():
            if status and data.get("status") != status:
                continue
            proposals.append({
                "proposal_id": pid,
                "status": data.get("status"),
                "project_type": data.get("project_type", "general"),
                "optimization_rounds": data.get("optimization_rounds", 0),
                "last_score": data.get("last_score", 0.0),
                "updated_at": data.get("updated_at", ""),
            })
        return proposals

    def get_dashboard(self) -> Dict[str, Any]:
        """获取仪表盘数据。"""
        state = self._load_state()
        dashboard = {
            "total": len(state["proposals"]),
            "by_status": {},
            "by_type": {},
            "proposals": state["proposals"],
        }
        for stage in LIFECYCLE_STAGES:
            dashboard["by_status"][stage] = sum(
                1 for d in state["proposals"].values() if d.get("status") == stage
            )
        for ptype in PROJECT_TYPES:
            dashboard["by_type"][ptype] = sum(
                1 for d in state["proposals"].values() if d.get("project_type") == ptype
            )
        return dashboard

    # ------------------------------------------------------------------
    # 对抗优化循环
    # ------------------------------------------------------------------

    def _get_quality_threshold(self, project_type: str) -> Dict[str, Any]:
        """从 nsfc-standards.json 读取项目类型的质量阈值。"""
        standards = load_json(self.standards_path, default={})
        types = standards.get("project_types", {})
        return types.get(project_type, {}).get("quality_threshold", {
            "min_overall_score": DEFAULT_SCORE_THRESHOLD,
            "max_high_issues": 0,
            "max_medium_issues": 3,
        })

    def optimize_cycle(
        self,
        proposal_id: str,
        max_rounds: int = DEFAULT_MAX_ROUNDS,
        critic_timeout: int = 300,
        writer_timeout: int = 600,
    ) -> Dict[str, Any]:
        """执行一轮 writer-critic 对抗优化循环。

        流程：critic 评审 → writer 根据评审意见优化 → 记录分数变化

        Args:
            proposal_id: 课题 ID
            max_rounds: 最大对抗轮数
            critic_timeout: critic profile 超时
            writer_timeout: writer profile 超时

        Returns:
            {round, score_before, score_after, issues_found, done, reason}
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal 未注册"}

        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}

        project_type = prop_state.get("project_type", "general")
        threshold = self._get_quality_threshold(project_type)
        current_round = prop_state.get("optimization_rounds", 0)

        if current_round >= max_rounds:
            return {"success": False, "error": f"已达最大轮数 {max_rounds}"}

        # 读取当前申请书
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        if not proposal_path.exists():
            return {"success": False, "error": "申请书不存在，请先执行管线生成初稿"}

        score_before = prop_state.get("last_score", 0.0)

        # 1. critic 评审
        if _log:
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: critic 评审")
        critic_result = self._run_critic(
            proposal_id, prop_dir, project_type, current_round + 1, critic_timeout
        )

        # 2. writer 根据评审意见优化
        if _log:
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: writer 优化")
        writer_result = self._run_writer_optimize(
            proposal_id, prop_dir, project_type, critic_result, writer_timeout
        )

        # 3. 解析新分数
        score_after = self._extract_score(critic_result)
        issues = self._extract_issues(critic_result)

        # 4. 更新状态
        with file_lock(f"proposal-{proposal_id}"):
            prop_state = self._get_proposal_state(proposal_id)
            prop_state["optimization_rounds"] = current_round + 1
            prop_state["last_score"] = score_after
            prop_state["score_history"].append({
                "round": current_round + 1,
                "score": score_after,
                "issues_count": len(issues),
                "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
                "at": now_utc(),
            })
            prop_state["updated_at"] = now_utc()
            self._set_proposal_state(proposal_id, prop_state)

        # 5. 判定是否达标
        done_result = self._check_done(proposal_id, threshold)

        return {
            "success": True,
            "round": current_round + 1,
            "score_before": score_before,
            "score_after": score_after,
            "score_delta": round(score_after - score_before, 4),
            "issues_found": len(issues),
            "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
            "done": done_result["done"],
            "reason": done_result["reason"],
            "threshold": threshold,
        }

    def _run_critic(
        self,
        proposal_id: str,
        prop_dir: Path,
        project_type: str,
        round_num: int,
        timeout: int,
    ) -> Dict[str, Any]:
        """派活给 critic profile 做对抗评审。"""
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        standards_path = str(self.standards_path.relative_to(PROJECT_ROOT))
        report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        prompt = (
            f"请对以下 NSFC 申请书做第 {round_num} 轮对抗评审。\n\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path} 中 project_types.{project_type} 的标准\n\n"
            f"【申请书文件】{proposal_path}\n\n"
            f"请执行：\n"
            f"1. 读取申请书全文\n"
            f"2. 读取质量标准配置文件\n"
            f"3. 按项目类型标准做红队评审，尽可能找出问题\n"
            f"4. 每个问题给出具体、可执行的修改建议\n"
            f"5. 按严重程度分级（critical/high/medium/low）\n"
            f"6. 给出加权综合评分（0-1）\n\n"
            f"将评审报告写入：{report_path}\n"
        )

        return self._run_hermes("critic", prompt, timeout)

    def _run_writer_optimize(
        self,
        proposal_id: str,
        prop_dir: Path,
        project_type: str,
        critic_result: Dict[str, Any],
        timeout: int,
    ) -> Dict[str, Any]:
        """派活给 writer profile 根据评审意见优化申请书。"""
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        standards_path = str(self.standards_path.relative_to(PROJECT_ROOT))
        # 找最新的 critic 报告
        review_dir = prop_dir / "05_review"
        critic_reports = sorted(review_dir.glob("critic-round-*.md"), reverse=True)
        latest_critic = str(critic_reports[0]) if critic_reports else ""

        prompt = (
            f"请根据对抗评审意见优化申请书。\n\n"
            f"【申请书文件】{proposal_path}\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path}\n"
            f"【评审报告】{latest_critic}\n\n"
            f"请执行：\n"
            f"1. 读取申请书当前版本\n"
            f"2. 读取评审报告中的所有问题\n"
            f"3. 逐条解决每个问题（按严重程度优先）\n"
            f"4. 保持已有内容的优势，只修改有问题的部分（增量优化）\n"
            f"5. 优化后覆盖写入原文件：{proposal_path}\n"
            f"6. 同时生成/更新方法学手册：{prop_dir}/04_proposal/methodology-manual.md\n"
            f"   （申请书重思路，方法学手册重细节：公式推导/参数表/技术路线图）\n"
        )

        return self._run_hermes("writer", prompt, timeout)

    def _run_hermes(self, profile: str, prompt: str, timeout: int) -> Dict[str, Any]:
        """执行 hermes oneshot。"""
        env = dict(os.environ)
        env.pop("PYTHONHOME", None)
        env.pop("PYTHONPATH", None)

        import time
        cmd = ["hermes", "--profile", profile, "-z", prompt]
        t0 = time.time()
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                env=env, cwd=str(PROJECT_ROOT),
            )
            elapsed = round(time.time() - t0, 2)
            if result.returncode == 0:
                output = result.stdout.strip()
                if len(output) > 8000:
                    output = output[:8000] + f"\n... (截断，共{len(output)}字符)"
                return {"success": True, "output": output, "elapsed_s": elapsed}
            return {
                "success": False, "output": result.stdout[:2000],
                "error": result.stderr[:500], "elapsed_s": elapsed,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": f"超时({timeout}s)", "elapsed_s": timeout}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e), "elapsed_s": 0}

    def _extract_score(self, critic_result: Dict[str, Any]) -> float:
        """从 critic 输出中提取评分。"""
        output = critic_result.get("output", "")
        # 尝试匹配 "综合评分：0.85" 或 "score: 0.85"
        import re
        patterns = [
            r"综合评分[：:]\s*(0\.\d+)",
            r"score[：:]\s*(0\.\d+)",
            r"评分[：:]\s*(0\.\d+)",
            r"(0\.\d+)\s*/\s*1",
        ]
        for pattern in patterns:
            match = re.search(pattern, output)
            if match:
                return float(match.group(1))
        return 0.0

    def _extract_issues(self, critic_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从 critic 输出中提取问题列表（简化版，只提取严重程度）。"""
        output = critic_result.get("output", "")
        issues = []
        for line in output.split("\n"):
            for sev in ["critical", "high", "medium", "low"]:
                if f"[{sev}]" in line or f"（{sev}）" in line:
                    issues.append({"severity": sev, "line": line.strip()[:100]})
        return issues

    # ------------------------------------------------------------------
    # 达标判定
    # ------------------------------------------------------------------

    def _check_done(self, proposal_id: str, threshold: Dict[str, Any]) -> Dict[str, Any]:
        """判定 proposal 是否达到输出标准或无法继续提升。"""
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"done": False, "reason": "状态不存在"}

        last_score = prop_state.get("last_score", 0.0)
        score_history = prop_state.get("score_history", [])
        min_score = threshold.get("min_overall_score", DEFAULT_SCORE_THRESHOLD)
        max_high = threshold.get("max_high_issues", 0)
        rounds = prop_state.get("optimization_rounds", 0)

        # 条件1：分数达标
        if last_score >= min_score:
            recent = score_history[-1] if score_history else {}
            if recent.get("high_issues", 99) <= max_high:
                return {"done": True, "reason": f"达标：分数{last_score:.2f}≥{min_score}，high问题≤{max_high}"}

        # 条件2：连续N轮无提升
        no_improve_limit = DEFAULT_NO_IMPROVEMENT_LIMIT
        if len(score_history) >= no_improve_limit + 1:
            recent_scores = [h["score"] for h in score_history[-(no_improve_limit + 1):]]
            deltas = [recent_scores[i + 1] - recent_scores[i] for i in range(len(recent_scores) - 1)]
            if all(d < 0.02 for d in deltas):
                return {"done": True, "reason": f"连续{no_improve_limit}轮无显著提升（Δ<0.02）"}

        # 条件3：达到最大轮数
        if rounds >= DEFAULT_MAX_ROUNDS:
            return {"done": True, "reason": f"达到最大轮数{DEFAULT_MAX_ROUNDS}"}

        return {"done": False, "reason": f"未达标：分数{last_score:.2f}<{min_score}，已优化{rounds}轮"}

    def auto_optimize_and_advance(self, proposal_id: str) -> Dict[str, Any]:
        """自动优化循环：反复执行对抗直到达标或无法提升，然后移入待校验。

        适用于 cron 自动驱动。
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal 未注册"}

        if prop_state["status"] != "optimizing":
            return {"success": False, "error": f"proposal 不在优化中（当前: {prop_state['status']}）"}

        threshold = self._get_quality_threshold(prop_state.get("project_type", "general"))
        rounds_done = 0
        last_result = {}

        while rounds_done < DEFAULT_MAX_ROUNDS:
            result = self.optimize_cycle(proposal_id)
            if not result.get("success"):
                break
            rounds_done += 1
            last_result = result

            if result.get("done"):
                # 达标或无法提升，移入待校验
                transition_result = self.transition(
                    proposal_id, "pending_review", reason=result["reason"]
                )
                return {
                    "success": True,
                    "advanced": True,
                    "rounds": rounds_done,
                    "final_score": result.get("score_after", 0),
                    "reason": result["reason"],
                    "transition": transition_result,
                }

        # 达到最大轮数
        transition_result = self.transition(
            proposal_id, "pending_review",
            reason=f"达到最大轮数{DEFAULT_MAX_ROUNDS}，当前分数{last_result.get('score_after', 0):.2f}"
        )
        return {
            "success": True,
            "advanced": True,
            "rounds": rounds_done,
            "final_score": last_result.get("score_after", 0),
            "reason": "达到最大轮数",
            "transition": transition_result,
        }

    # ------------------------------------------------------------------
    # 人工反馈处理
    # ------------------------------------------------------------------

    def submit_feedback(
        self,
        proposal_id: str,
        feedback_text: str,
        verdict: str = "major_revision",
    ) -> Dict[str, Any]:
        """提交人工审核反馈。

        如果 verdict 是 approve，移入归档。
        否则派活给 writer 整理结构化意见，返回优化中。

        Args:
            proposal_id: 课题 ID
            feedback_text: 人工意见（自由文本）
            verdict: 审核结论（approve/minor_revision/major_revision/reject/redirect）

        Returns:
            {success, verdict, structured_feedback, transition}
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal 未注册"}

        if prop_state["status"] != "pending_review":
            return {"success": False, "error": f"proposal 不在待校验（当前: {prop_state['status']}）"}

        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}

        # 保存原始反馈
        feedback_dir = prop_dir / "06_feedback"
        feedback_dir.mkdir(parents=True, exist_ok=True)
        feedback_num = prop_state.get("human_feedback_count", 0) + 1
        raw_path = feedback_dir / f"feedback-{feedback_num}-raw.md"
        raw_path.write_text(
            f"# 人工审核反馈（第{feedback_num}次）\n\n"
            f"**时间**: {now_utc()}\n**结论**: {verdict}\n\n---\n\n{feedback_text}",
            encoding="utf-8",
        )

        if verdict == "approve":
            # 通过 → 归档
            archive_result = self._archive_proposal(proposal_id, feedback_text, verdict)
            return {
                "success": True,
                "verdict": "approve",
                "archived": True,
                "transition": archive_result,
            }

        # 不通过 → writer 整理结构化意见 → 返回优化中
        structured = self._structure_feedback(
            proposal_id, prop_dir, feedback_text, verdict, feedback_num
        )

        # 更新反馈计数
        with file_lock(f"proposal-{proposal_id}"):
            prop_state = self._get_proposal_state(proposal_id)
            prop_state["human_feedback_count"] = feedback_num
            prop_state["updated_at"] = now_utc()
            self._set_proposal_state(proposal_id, prop_state)

        # 返回优化中
        transition_result = self.transition(
            proposal_id, "optimizing",
            reason=f"人工审核退回({verdict})，携带结构化意见"
        )

        return {
            "success": True,
            "verdict": verdict,
            "archived": False,
            "structured_feedback": structured,
            "transition": transition_result,
        }

    def _structure_feedback(
        self,
        proposal_id: str,
        prop_dir: Path,
        feedback_text: str,
        verdict: str,
        feedback_num: int,
    ) -> Dict[str, Any]:
        """派活给 writer profile 将人工意见结构化。"""
        feedback_standards_path = str(
            (PROJECT_ROOT / "memory" / "feedback-standards.json").relative_to(PROJECT_ROOT)
        )
        structured_path = prop_dir / "06_feedback" / f"feedback-{feedback_num}-structured.json"

        prompt = (
            f"请将以下人工审核意见整理为结构化JSON格式。\n\n"
            f"【标准化配置】请读取 {feedback_standards_path}\n"
            f"【审核结论】{verdict}\n"
            f"【人工意见原文】\n{feedback_text}\n\n"
            f"请执行：\n"
            f"1. 读取标准化配置，了解 issue 结构和 action 类型\n"
            f"2. 将人工意见拆解为独立的 issue\n"
            f"3. 为每个 issue 补充 instruction（可执行指令）和 action\n"
            f"4. 严重程度按 critical/high/medium/low 分级\n"
            f"5. 模糊意见标注为 low 并保留原话\n\n"
            f"输出格式（写入 {structured_path}）：\n"
            f"{{\n"
            f'  "verdict": "{verdict}",\n'
            f'  "overall_comment": "总体评价",\n'
            f'  "issues": [\n'
            f'    {{"section":"","severity":"","issue_type":"","description":"","instruction":"","action":"","target_passage":""}}\n'
            f"  ]\n"
            f"}}\n"
        )

        result = self._run_hermes("writer", prompt, timeout=120)

        # 尝试读取结构化文件
        if structured_path.exists():
            try:
                structured = json.loads(structured_path.read_text(encoding="utf-8"))
                return {"success": True, "structured": structured, "path": str(structured_path)}
            except Exception:
                pass

        return {
            "success": result.get("success", False),
            "raw_output": result.get("output", "")[:500],
            "path": str(structured_path),
        }

    # ------------------------------------------------------------------
    # 归档
    # ------------------------------------------------------------------

    def _archive_proposal(
        self,
        proposal_id: str,
        approval_comment: str,
        verdict: str,
    ) -> Dict[str, Any]:
        """归档 proposal：移入归档区 + 写入元信息。"""
        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "目录不存在"}

        # 移动到归档区
        transition = self.transition(proposal_id, "archived", reason=f"人工审核通过: {verdict}")
        if not transition.get("success"):
            return transition

        archived_dir = self.root / "archived" / proposal_id

        # 写入归档元信息
        meta = {
            "proposal_id": proposal_id,
            "archived_at": now_utc(),
            "verdict": verdict,
            "approval_comment": approval_comment,
            "final_files": [str(f.relative_to(archived_dir)) for f in archived_dir.rglob("*.md")],
        }
        meta_path = archived_dir / "_archive-meta.json"
        save_json(meta_path, meta)

        if _log:
            _log.info(f"归档 {proposal_id}: {len(meta['final_files'])} 个文件")

        return {"success": True, "archived_dir": str(archived_dir), "meta": meta}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="提案生命周期管理")
    parser.add_argument("--dashboard", action="store_true", help="显示仪表盘")
    parser.add_argument("--list", metavar="STATUS", help="按状态列出 proposal")
    parser.add_argument("--register", nargs="+", metavar=("ID", "TYPE"),
                        help="注册新 proposal（--register ID [general|key|major]）")
    parser.add_argument("--transition", nargs=3, metavar=("ID", "FROM", "TO"),
                        help="流转 proposal（阶段可不填FROM，填auto）")
    parser.add_argument("--optimize", metavar="ID", help="执行一轮对抗优化")
    parser.add_argument("--auto-optimize", metavar="ID", help="自动优化直到达标")
    parser.add_argument("--feedback", nargs=2, metavar=("ID", "FILE"),
                        help="提交人工反馈（--feedback ID 意见文件路径）")
    parser.add_argument("--verdict", default="major_revision",
                        help="审核结论（approve/minor_revision/major_revision/reject/redirect）")
    args = parser.parse_args(argv)

    lc = ProposalLifecycle()

    if args.dashboard:
        dashboard = lc.get_dashboard()
        print("=== 提案生命周期仪表盘 ===")
        print(f"总数: {dashboard['total']}")
        print("\n按状态:")
        for stage in LIFECYCLE_STAGES:
            count = dashboard["by_status"].get(stage, 0)
            label = {"drafts": "初稿", "optimizing": "优化中",
                     "pending_review": "待校验", "archived": "归档"}[stage]
            print(f"  {label}({stage}): {count}")
        print("\n按类型:")
        for ptype in PROJECT_TYPES:
            count = dashboard["by_type"].get(ptype, 0)
            print(f"  {ptype}: {count}")
        if dashboard["total"] > 0:
            print("\n提案列表:")
            for pid, data in dashboard["proposals"].items():
                print(f"  [{data['status']:14s}] {pid:30s} "
                      f"type={data.get('project_type', '?'):8s} "
                      f"rounds={data.get('optimization_rounds', 0):2d} "
                      f"score={data.get('last_score', 0):.2f}")
        return 0

    if args.list:
        proposals = lc.list_by_status(args.list)
        print(f"=== {args.list} 区（{len(proposals)} 个）===")
        for p in proposals:
            print(f"  {p['proposal_id']:30s} type={p['project_type']:8s} "
                  f"rounds={p['optimization_rounds']:2d} score={p['last_score']:.2f}")
        return 0

    if args.register:
        pid = args.register[0]
        ptype = args.register[1] if len(args.register) > 1 else "general"
        result = lc.register(pid, project_type=ptype)
        print(f"注册: {result}")
        return 0 if result.get("success") else 1

    if args.transition:
        pid, _from, to = args.transition
        result = lc.transition(pid, to)
        print(f"流转: {result}")
        return 0 if result.get("success") else 1

    if args.optimize:
        result = lc.optimize_cycle(args.optimize)
        print(f"优化轮 {result.get('round', '?')}: "
              f"score {result.get('score_before', 0):.2f} → {result.get('score_after', 0):.2f} "
              f"(Δ{result.get('score_delta', 0):+.4f})")
        print(f"问题: {result.get('issues_found', 0)}个 "
              f"(high: {result.get('high_issues', 0)})")
        print(f"完成: {'是' if result.get('done') else '否'} - {result.get('reason', '')}")
        return 0 if result.get("success") else 1

    if args.auto_optimize:
        result = lc.auto_optimize_and_advance(args.auto_optimize)
        print(f"自动优化完成: {result.get('rounds', 0)} 轮, "
              f"最终分数 {result.get('final_score', 0):.2f}")
        print(f"移入待校验: {'是' if result.get('advanced') else '否'} - {result.get('reason', '')}")
        return 0 if result.get("success") else 1

    if args.feedback:
        pid, filepath = args.feedback
        feedback_text = Path(filepath).read_text(encoding="utf-8")
        result = lc.submit_feedback(pid, feedback_text, verdict=args.verdict)
        print(f"反馈处理: verdict={result.get('verdict')}")
        print(f"归档: {'是' if result.get('archived') else '否'}")
        if result.get("structured_feedback"):
            sf = result["structured_feedback"]
            if sf.get("structured"):
                issues = sf["structured"].get("issues", [])
                print(f"结构化: {len(issues)} 个 issue")
        return 0 if result.get("success") else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
