#!/usr/bin/env python3
"""Hermes 驱动的研究管线 — CoPilot 作为操作台，hermes 作为执行端（v6.4.0）

用途：
    将研究管线的执行从 CoPilot 进程内调用，改为派活给 hermes 的 agent profiles。
    CoPilot 只负责：派活、产物检查、状态追踪、可视化。

架构关系：
    CoPilot 操作台（本模块）
      ├── dispatch_to_profile()  → 派活给 hermes profile（agent loop 自主执行）
      ├── check_artifacts()      → 检查 hermes 产出是否到位
      ├── get_pipeline_status()  → 读取各阶段状态
      └── setup_cron()           → 配置 hermes cron 实现自动化

    hermes 执行端（5 个 profile）
      ├── linsai      → 方向校准/总控（读取用户画像，校准研究方向）
      ├── researcher  → 文献调研（检索 arXiv/联网，评分排序）
      ├── analyst     → 缺口分析/问题架构（综合调研，识别缺口，构建问题）
      ├── writer      → 申请书撰写（按 NSFC 格式撰写章节）
      └── reviewer    → 质量自检（六维审查，给出修改建议）

管线六阶段 → profile 映射：
    阶段0 方向校准 → linsai
    阶段1 文献调研 → researcher
    阶段2 缺口分析 → analyst
    阶段3 科学问题 → analyst
    阶段4 申请书撰写 → writer
    阶段5 质量自检 → reviewer

产物约定（hermes 执行后写入的文件，CoPilot 检查这些文件）：
    {proposal_dir}/01_direction/direction-calibration.md
    {proposal_dir}/02_literature/literature-report.md
    {proposal_dir}/02_topic/gap-report.md
    {proposal_dir}/03_question/question-framework.md
    {proposal_dir}/04_proposal/proposal-draft.md
    {proposal_dir}/05_review/review-report.md

边界合规（AGENTS.md §6）：
    - 本模块归入「共享基础设施」层（同 hermes_bridge.py 的定位）
    - 通过 subprocess 调用 hermes CLI，不直接导入管线模块
    - 产物检查只读文件，不修改管线模块状态

用法示例：
    >>> from hermes_pipeline import HermesPipeline
    >>> pipe = HermesPipeline("nsfc-2026-001")
    >>> pipe.dispatch_stage(0)       # 派活：方向校准 → linsai profile
    >>> pipe.check_stage(0)          # 检查：产物是否到位
    >>> pipe.dispatch_stage(1)       # 派活：文献调研 → researcher profile
    >>> pipe.run_pipeline()          # 一键执行全链路

命令行自检：
    python3 scripts/hermes_pipeline.py --self-check
    python3 scripts/hermes_pipeline.py --status nsfc-2026-001
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 确保可从 scripts/ 目录直接导入
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock
from paths import PROJECT_ROOT

__all__ = [
    "HermesPipeline",
    "STAGE_PROFILE_MAP",
    "STAGE_ARTIFACTS",
    "STAGE_PROMPTS",
]

# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------
try:
    from logger import get_logger
    _log = get_logger("hermes_pipeline")
except Exception:
    _log = None


# ---------------------------------------------------------------------------
# 管线阶段 → hermes profile 映射
# ---------------------------------------------------------------------------

STAGES = [
    {"id": 0, "name": "方向校准", "name_en": "Direction Calibration"},
    {"id": 1, "name": "文献调研", "name_en": "Literature Research"},
    {"id": 2, "name": "缺口分析", "name_en": "Gap Analysis"},
    {"id": 3, "name": "科学问题", "name_en": "Question Architecture"},
    {"id": 4, "name": "申请书撰写", "name_en": "Proposal Writing"},
    {"id": 5, "name": "质量自检", "name_en": "Quality Review"},
]

# 阶段 → hermes profile 映射
STAGE_PROFILE_MAP: Dict[int, str] = {
    0: "linsai",
    1: "researcher",
    2: "analyst",
    3: "analyst",
    4: "writer",
    5: "reviewer",
}

# 阶段 → 预期产物文件（相对于 proposal_dir）
STAGE_ARTIFACTS: Dict[int, List[str]] = {
    0: ["01_direction/direction-calibration.md"],
    1: ["02_literature/literature-report.md"],
    2: ["02_topic/gap-report.md"],
    3: ["03_question/question-framework.md"],
    4: ["04_proposal/proposal-draft.md"],
    5: ["05_review/review-report.md"],
}

# 阶段 → 派活 prompt 模板
# {proposal_dir} 会被替换为实际路径
STAGE_PROMPTS: Dict[int, str] = {
    0: (
        "你是研究方向校准官。请完成以下任务：\n\n"
        "1. 读取用户研究方向画像（memory/research-profile.json 和 memory/user-profile.json）\n"
        "2. 读取知识库（knowledge/wiki/）中的核心概念\n"
        "3. 基于以上信息，校准当前研究方向的 3-5 个关键词\n"
        "4. 输出方向校准报告，写入：{proposal_dir}/01_direction/direction-calibration.md\n\n"
        "报告格式：\n"
        "# 方向校准报告\n"
        "## 研究方向关键词\n- ...\n"
        "## 用户画像摘要\n- ...\n"
        "## 方向对齐评估\n- ...\n"
        "## 建议聚焦的课题方向\n- ...\n"
    ),
    1: (
        "你是文献调研员。请完成以下任务：\n\n"
        "1. 基于方向校准报告（{proposal_dir}/01_direction/direction-calibration.md），"
        "确定 3-5 个检索关键词\n"
        "2. 使用 web_search 和 DeepXiv 工具检索最新论文（近 2 年）\n"
        "3. 对每篇论文评分（相关性/新颖性/可靠性/时效性，各 0-1 分）\n"
        "4. 输出文献调研报告，写入：{proposal_dir}/02_literature/literature-report.md\n\n"
        "报告格式：\n"
        "# 文献调研报告\n"
        "## 检索关键词\n- ...\n"
        "## 论文清单（按总分排序）\n"
        "| arxiv_id | 标题 | 相关性 | 新颖性 | 可靠性 | 时效性 | 总分 |\n"
        "|----------|------|--------|--------|--------|--------|------|\n"
        "## 领域发展脉络\n...\n"
        "## 关键发现\n...\n"
    ),
    2: (
        "你是研究缺口分析师。请完成以下任务：\n\n"
        "1. 读取文献调研报告（{proposal_dir}/02_literature/literature-report.md）\n"
        "2. 读取知识库（knowledge/wiki/）的已有概念覆盖\n"
        "3. 识别 5-10 个研究缺口（理论/方法/实验/数据四类）\n"
        "4. 对每个缺口评分（新颖性/可行性/优先级）\n"
        "5. 输出缺口分析报告，写入：{proposal_dir}/02_topic/gap-report.md\n\n"
        "报告格式：\n"
        "# 研究缺口报告\n## 缺口清单\n"
        "### gap_001：[类型] 缺口\n- 描述：...\n- 优先级：...\n- 建议路径：...\n"
    ),
    3: (
        "你是科学问题架构师。请完成以下任务：\n\n"
        "1. 读取缺口分析报告（{proposal_dir}/02_topic/gap-report.md）\n"
        "2. 选择 1-2 个高优先级缺口，构建五要素科学问题框架：\n"
        "   立项依据 / 科学问题 / 研究内容 / 研究方案 / 特色与创新\n"
        "3. 为每个要素构建 1 个主问题 + 2 个子问题\n"
        "4. 输出问题框架，写入：{proposal_dir}/03_question/question-framework.md\n\n"
        "报告格式：\n"
        "# 科学问题框架\n## 课题标题\n...\n"
        "## 五要素问题\n### 立项依据\n- 主问题：...\n- 子问题：...\n"
        "## 核心假设\n...\n"
    ),
    4: (
        "你是 NSFC 申请书撰写专家。请完成以下任务：\n\n"
        "1. 读取科学问题框架（{proposal_dir}/03_question/question-framework.md）\n"
        "2. 读取缺口分析报告（{proposal_dir}/02_topic/gap-report.md）\n"
        "3. 按 NSFC 面上项目格式撰写六章节申请书：\n"
        "   立项依据 / 研究内容 / 研究方案 / 特色与创新 / 年度计划 / 预期成果\n"
        "4. 要求：学术论述充实、逻辑严密、引文用 [CITE:ref_key] 标注\n"
        "5. 输出申请书草稿，写入：{proposal_dir}/04_proposal/proposal-draft.md\n"
    ),
    5: (
        "你是 NSFC 项目评审专家。请完成以下任务：\n\n"
        "1. 读取申请书草稿（{proposal_dir}/04_proposal/proposal-draft.md）\n"
        "2. 从六个维度审查：逻辑一致性 / 证据充分性 / 创新性 / 可行性 / 学术规范 / 表达质量\n"
        "3. 每个维度评分（0-1）并指出具体问题\n"
        "4. 给出优化策略和修改建议\n"
        "5. 输出评审报告，写入：{proposal_dir}/05_review/review-report.md\n\n"
        "报告格式：\n"
        "# 评审报告\n## 总分\n...\n## 六维评分\n| 维度 | 分数 | 问题数 |\n"
        "## 问题清单\n### [严重程度] 问题\n- 位置：...\n- 建议：...\n"
        "## 优化策略\n...\n"
    ),
}


# ---------------------------------------------------------------------------
# HermesPipeline 核心类
# ---------------------------------------------------------------------------

class HermesPipeline:
    """Hermes 驱动的研究管线操作台。

    CoPilot 通过本类将管线各阶段任务派给 hermes 的 agent profiles，
    并通过产物文件检查来追踪执行进度。
    """

    def __init__(self, proposal_id: str) -> None:
        """初始化管线操作台。

        Args:
            proposal_id: 课题 ID（如 "nsfc-2026-001"）
        """
        self.proposal_id = proposal_id
        self.proposal_dir = PROJECT_ROOT / "research_proposals" / proposal_id
        self.state_path = self.proposal_dir / "00_pipeline" / "hermes-pipeline-state.json"
        self.proposal_dir.mkdir(parents=True, exist_ok=True)
        (self.proposal_dir / "00_pipeline").mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 状态管理
    # ------------------------------------------------------------------

    def _default_state(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "current_stage": 0,
            "status": "idle",  # idle / running / completed / paused
            "stages": {
                str(i): {
                    "name": s["name"],
                    "profile": STAGE_PROFILE_MAP[i],
                    "status": "pending",  # pending / dispatched / completed / failed
                    "dispatched_at": None,
                    "completed_at": None,
                    "output_preview": "",
                    "error": "",
                }
                for i, s in enumerate(STAGES)
            },
            "history": [],
            "created_at": now_utc(),
            "updated_at": now_utc(),
        }

    def _load_state(self) -> Dict[str, Any]:
        data = load_json(self.state_path, default=None)
        if not data:
            data = self._default_state()
            self._save_state(data)
        return data

    def _save_state(self, state: Dict[str, Any]) -> None:
        state["updated_at"] = now_utc()
        save_json(self.state_path, state)

    def get_status(self) -> Dict[str, Any]:
        """获取管线当前状态。"""
        state = self._load_state()
        # 实时检查各阶段产物
        for i in range(len(STAGES)):
            stage_key = str(i)
            stage_state = state["stages"].get(stage_key, {})
            artifacts_ok = self._check_artifacts(i)
            if artifacts_ok and stage_state.get("status") not in ("completed",):
                stage_state["status"] = "completed"
                if not stage_state.get("completed_at"):
                    stage_state["completed_at"] = now_utc()
            state["stages"][stage_key] = stage_state
        self._save_state(state)
        return state

    # ------------------------------------------------------------------
    # 产物检查
    # ------------------------------------------------------------------

    def _check_artifacts(self, stage: int) -> bool:
        """检查指定阶段的产物文件是否全部存在且非空。

        Args:
            stage: 阶段编号

        Returns:
            True 如果所有预期产物都存在且非空
        """
        artifacts = STAGE_ARTIFACTS.get(stage, [])
        if not artifacts:
            return False
        for rel_path in artifacts:
            full_path = self.proposal_dir / rel_path
            if not full_path.exists():
                return False
            if full_path.stat().st_size < 50:  # 至少 50 字节
                return False
        return True

    def check_stage(self, stage: int) -> Dict[str, Any]:
        """检查指定阶段的产物状态。

        Returns:
            {stage, artifacts_ok, artifacts_detail, status}
        """
        artifacts = STAGE_ARTIFACTS.get(stage, [])
        detail = []
        all_ok = True
        for rel_path in artifacts:
            full_path = self.proposal_dir / rel_path
            exists = full_path.exists()
            size = full_path.stat().st_size if exists else 0
            ok = exists and size >= 50
            if not ok:
                all_ok = False
            detail.append({
                "path": rel_path,
                "exists": exists,
                "size": size,
                "ok": ok,
            })
        return {
            "stage": stage,
            "name": STAGES[stage]["name"] if stage < len(STAGES) else "?",
            "artifacts_ok": all_ok,
            "artifacts_detail": detail,
        }

    # ------------------------------------------------------------------
    # 派活给 hermes profile
    # ------------------------------------------------------------------

    def _build_hermes_cmd(
        self,
        profile: str,
        prompt: str,
        workdir: Optional[str] = None,
    ) -> List[str]:
        """构建 hermes CLI 命令（清除 PYTHONHOME/PYTHONPATH 冲突）。"""
        cmd = ["hermes", "--profile", profile, "-z", prompt]
        return cmd

    def _run_hermes(
        self,
        profile: str,
        prompt: str,
        timeout: int = 600,
    ) -> Dict[str, Any]:
        """执行 hermes oneshot（agent loop 自主执行）。

        清除 PYTHONHOME/PYTHONPATH 环境变量以避免 Python 冲突。

        Returns:
            {success, output, error, elapsed_s}
        """
        import time
        env = dict(os.environ)
        # 清除可能导致 hermes venv 冲突的环境变量
        env.pop("PYTHONHOME", None)
        env.pop("PYTHONPATH", None)

        cmd = self._build_hermes_cmd(profile, prompt)
        t0 = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=str(PROJECT_ROOT),  # 以项目根为工作目录
            )
            elapsed = round(time.time() - t0, 2)
            if result.returncode == 0:
                output = result.stdout.strip()
                if len(output) > 8000:
                    output = output[:8000] + f"\n\n... (已截断，共 {len(output)} 字符)"
                if _log:
                    _log.info(f"hermes oneshot 成功 profile={profile} elapsed={elapsed}s")
                return {"success": True, "output": output, "error": "", "elapsed_s": elapsed}
            return {
                "success": False,
                "output": result.stdout.strip()[:2000],
                "error": result.stderr.strip()[:500] or f"退出码 {result.returncode}",
                "elapsed_s": elapsed,
            }
        except subprocess.TimeoutExpired:
            elapsed = round(time.time() - t0, 2)
            return {
                "success": False,
                "output": "",
                "error": f"hermes agent 超时（{timeout}s）——任务可能仍在后台执行",
                "elapsed_s": elapsed,
            }
        except FileNotFoundError:
            return {"success": False, "output": "", "error": "未找到 hermes 命令", "elapsed_s": 0}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e), "elapsed_s": 0}

    def dispatch_stage(
        self,
        stage: int,
        extra_context: str = "",
        timeout: int = 600,
    ) -> Dict[str, Any]:
        """将指定阶段派活给对应的 hermes profile。

        Args:
            stage: 阶段编号（0-5）
            extra_context: 额外上下文信息（附加到 prompt）
            timeout: hermes agent loop 超时秒数

        Returns:
            {dispatched, stage, profile, output_preview, artifacts_ok, error}
        """
        if stage < 0 or stage >= len(STAGES):
            return {"dispatched": False, "error": f"非法阶段: {stage}"}

        profile = STAGE_PROFILE_MAP[stage]
        prompt_template = STAGE_PROMPTS.get(stage, "")
        prompt = prompt_template.format(proposal_dir=str(self.proposal_dir))
        if extra_context:
            prompt += f"\n\n=== 额外上下文 ===\n{extra_context}\n"

        # 确保产物目录存在
        for rel_path in STAGE_ARTIFACTS.get(stage, []):
            full = self.proposal_dir / rel_path
            full.parent.mkdir(parents=True, exist_ok=True)

        # 更新状态
        with file_lock(f"hermes-pipe-{self.proposal_id}"):
            state = self._load_state()
            state["stages"][str(stage)]["status"] = "dispatched"
            state["stages"][str(stage)]["dispatched_at"] = now_utc()
            state["stages"][str(stage)]["error"] = ""
            self._save_state(state)

        # 派活给 hermes
        if _log:
            _log.info(f"派活 阶段{stage}({STAGES[stage]['name']}) → profile={profile}")
        result = self._run_hermes(profile, prompt, timeout=timeout)

        # 检查产物
        artifacts_ok = self._check_artifacts(stage)
        output_preview = (result.get("output", "") or "")[:500]

        # 更新状态
        with file_lock(f"hermes-pipe-{self.proposal_id}"):
            state = self._load_state()
            stage_state = state["stages"][str(stage)]
            if result["success"] and artifacts_ok:
                stage_state["status"] = "completed"
                stage_state["completed_at"] = now_utc()
            elif result["success"]:
                stage_state["status"] = "dispatched"  # 成功但产物未到位
            else:
                stage_state["status"] = "failed"
                stage_state["error"] = result.get("error", "")
            stage_state["output_preview"] = output_preview
            self._save_state(state)

        return {
            "dispatched": result["success"],
            "stage": stage,
            "name": STAGES[stage]["name"],
            "profile": profile,
            "output_preview": output_preview,
            "artifacts_ok": artifacts_ok,
            "elapsed_s": result.get("elapsed_s", 0),
            "error": result.get("error", ""),
        }

    def dispatch_to_profile(
        self,
        profile: str,
        prompt: str,
        timeout: int = 600,
    ) -> Dict[str, Any]:
        """直接派活给指定 profile（不限于管线预定义的阶段）。

        Args:
            profile: hermes profile 名（linsai/researcher/analyst/writer/reviewer）
            prompt: 任务描述
            timeout: 超时秒数

        Returns:
            {success, output, error, elapsed_s}
        """
        return self._run_hermes(profile, prompt, timeout=timeout)

    # ------------------------------------------------------------------
    # 一键执行全链路
    # ------------------------------------------------------------------

    def run_pipeline(self, timeout_per_stage: int = 600) -> Dict[str, Any]:
        """一键执行全部六阶段：依次派活给各 profile。

        每阶段派活后检查产物，产物到位才推进下一阶段。

        Args:
            timeout_per_stage: 每阶段 hermes agent 超时秒数

        Returns:
            {completed, stages_executed, final_stage, results}
        """
        results: List[Dict[str, Any]] = []

        for stage in range(len(STAGES)):
            state = self._load_state()
            state["current_stage"] = stage
            state["status"] = "running"
            self._save_state(state)

            if _log:
                _log.info(f"=== 执行阶段 {stage}/{len(STAGES)-1}: {STAGES[stage]['name']} ===")

            result = self.dispatch_stage(stage, timeout=timeout_per_stage)
            results.append(result)

            # 产物检查未通过则停止
            if not result.get("artifacts_ok"):
                state = self._load_state()
                state["status"] = "paused"
                self._save_state(state)
                return {
                    "completed": False,
                    "stages_executed": len(results),
                    "final_stage": stage,
                    "results": results,
                    "reason": f"阶段{stage}({STAGES[stage]['name']})产物未到位: "
                              f"{result.get('error', 'hermes 已执行但产物文件缺失')}",
                }

        # 全部完成
        state = self._load_state()
        state["status"] = "completed"
        state["current_stage"] = len(STAGES)
        self._save_state(state)

        return {
            "completed": True,
            "stages_executed": len(results),
            "final_stage": len(STAGES) - 1,
            "results": results,
            "reason": "管线全部完成",
        }

    # ------------------------------------------------------------------
    # 自动化 cron 配置
    # ------------------------------------------------------------------

    def setup_cron(
        self,
        schedule: str = "0 9 * * 1",
        deliver: str = "local",
    ) -> Dict[str, Any]:
        """配置 hermes cron 自动触发管线。

        在指定 profile（linsai）上创建一个 cron job，定时触发管线执行。

        Args:
            schedule: cron 表达式（默认每周一 09:00）
            deliver: 结果投递方式

        Returns:
            {success, job_id, message}
        """
        prompt = (
            f"请执行研究管线全链路（课题：{self.proposal_id}）。\n"
            f"依次完成六阶段：方向校准→文献调研→缺口分析→科学问题→申请书撰写→质量自检。\n"
            f"每阶段产出写入 {self.proposal_dir}/ 对应目录。\n"
            f"如果某阶段产物已存在且非空，可跳过该阶段。\n"
        )

        env = dict(os.environ)
        env.pop("PYTHONHOME", None)
        env.pop("PYTHONPATH", None)

        cmd = [
            "hermes", "--profile", "linsai", "cron", "create",
            schedule,
            prompt,
            "--name", f"研究管线自动执行-{self.proposal_id}",
            "--deliver", deliver,
            "--workdir", str(PROJECT_ROOT),
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, env=env,
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                # 尝试提取 job_id
                job_id = ""
                for line in output.split("\n"):
                    if "id:" in line.lower() or "created" in line.lower():
                        job_id = line.strip()
                        break
                return {
                    "success": True,
                    "output": output[:500],
                    "job_id": job_id,
                    "message": f"✓ cron 已创建: {schedule}",
                }
            return {
                "success": False,
                "message": f"✗ hermes 返回错误: {result.stderr.strip()[:200]}",
            }
        except Exception as e:
            return {"success": False, "message": f"✗ 创建 cron 失败: {e}"}


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_check() -> None:
    """模块自检。"""
    print("=== hermes_pipeline 自检 ===")

    # 1. 常量完整性
    print("[1] 常量完整性...", end=" ")
    assert len(STAGES) == 6
    assert len(STAGE_PROFILE_MAP) == 6
    assert len(STAGE_ARTIFACTS) == 6
    assert len(STAGE_PROMPTS) == 6
    for i in range(6):
        assert STAGE_PROFILE_MAP[i] in ("linsai", "researcher", "analyst", "writer", "reviewer")
        assert "{proposal_dir}" in STAGE_PROMPTS[i]
    print("✓")

    # 2. profile 映射合理性
    print("[2] profile 映射...", end=" ")
    assert STAGE_PROFILE_MAP[0] == "linsai"       # 方向校准 → 总控
    assert STAGE_PROFILE_MAP[1] == "researcher"   # 文献调研 → researcher
    assert STAGE_PROFILE_MAP[4] == "writer"       # 申请书 → writer
    assert STAGE_PROFILE_MAP[5] == "reviewer"     # 自检 → reviewer
    print("✓")

    # 3. HermesPipeline 初始化
    print("[3] HermesPipeline 初始化...", end=" ")
    pipe = HermesPipeline("__self_check__")
    assert pipe.proposal_id == "__self_check__"
    assert pipe.proposal_dir.exists()
    print("✓")

    # 4. 状态管理
    print("[4] 状态管理...", end=" ")
    state = pipe._load_state()
    assert state["current_stage"] == 0
    assert state["status"] == "idle"
    assert len(state["stages"]) == 6
    print("✓")

    # 5. 产物检查（空目录应返回 False）
    print("[5] 产物检查...", end=" ")
    assert pipe._check_artifacts(0) is False  # 无产物
    check_result = pipe.check_stage(0)
    assert check_result["artifacts_ok"] is False
    print("✓")

    # 6. get_status
    print("[6] get_status...", end=" ")
    status = pipe.get_status()
    assert "stages" in status
    assert "current_stage" in status
    print("✓")

    # 清理自检目录
    import shutil
    shutil.rmtree(pipe.proposal_dir, ignore_errors=True)

    print("\n✓ hermes_pipeline 自检全部通过")


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Hermes 驱动的研究管线")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    parser.add_argument("--status", metavar="PROPOSAL_ID", help="查看管线状态")
    parser.add_argument("--dispatch", nargs=2, metavar=("PROPOSAL_ID", "STAGE"),
                        help="派活指定阶段")
    parser.add_argument("--run", metavar="PROPOSAL_ID", help="一键执行全链路")
    parser.add_argument("--setup-cron", nargs=2, metavar=("PROPOSAL_ID", "SCHEDULE"),
                        help="配置 cron 自动触发")
    args = parser.parse_args(argv)

    if args.self_check:
        _self_check()
        return 0

    if args.status:
        pipe = HermesPipeline(args.status)
        status = pipe.get_status()
        print(f"=== 管线状态: {args.status} ===")
        print(f"当前阶段: {status['current_stage']}  状态: {status['status']}")
        for i in range(6):
            s = status["stages"].get(str(i), {})
            icon = {"pending": "○", "dispatched": "◐", "completed": "✓", "failed": "✗"}.get(
                s.get("status", "?"), "?")
            print(f"  [{icon}] 阶段{i} {s.get('name', '?')} → {s.get('profile', '?')} : {s.get('status', '?')}")
        return 0

    if args.dispatch:
        proposal_id, stage_str = args.dispatch
        stage = int(stage_str)
        pipe = HermesPipeline(proposal_id)
        result = pipe.dispatch_stage(stage)
        print(f"派活结果: {result}")
        return 0 if result.get("dispatched") else 1

    if args.run:
        pipe = HermesPipeline(args.run)
        result = pipe.run_pipeline()
        print(f"管线执行结果: completed={result['completed']}")
        for r in result["results"]:
            icon = "✓" if r.get("artifacts_ok") else "✗"
            print(f"  [{icon}] 阶段{r['stage']} {r['name']} → {r['profile']}: "
                  f"{'产物到位' if r.get('artifacts_ok') else r.get('error', '产物缺失')}")
        return 0 if result["completed"] else 1

    if args.setup_cron:
        proposal_id, schedule = args.setup_cron
        pipe = HermesPipeline(proposal_id)
        result = pipe.setup_cron(schedule=schedule)
        print(f"cron 配置: {result}")
        return 0 if result.get("success") else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
