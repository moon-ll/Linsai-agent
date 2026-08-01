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

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 确保可从 scripts/ 目录直接导入
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock, clean_subprocess_env
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
# pipeline-runner 是管线编排 profile，负责协调；具体执行委派给专业 profile
STAGE_PROFILE_MAP: Dict[int, str] = {
    0: "pipeline-runner",   # 方向校准：编排器自己读取画像执行
    1: "researcher",        # 文献调研：专业检索 profile
    2: "analyst",           # 缺口分析：专业分析 profile
    3: "analyst",           # 科学问题：专业分析 profile
    4: "writer",            # 申请书撰写：专业写作 profile
    5: "reviewer",          # 质量自检：专业审阅 profile
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
        "3. 按「项目类型标准」中的章节结构撰写申请书（见下方项目类型标准）\n"
        "4. 要求：学术论述充实、逻辑严密、引文用 [CITE:ref_key] 标注\n"
        "5. 输出申请书正文，写入：{proposal_dir}/04_proposal/proposal-draft.md\n"
        "6. 同时生成方法学手册，写入：{proposal_dir}/04_proposal/methodology-manual.md\n"
        "   （申请书重思路，方法学手册重细节：公式推导/参数表/技术路线图/收敛性分析）\n"
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
            proposal_id: 课题 ID（如 "general-quantum-geometry-inversion-20260726"）
        """
        self.proposal_id = proposal_id
        # 兼容：proposal 可能在 lifecycle 管理的 drafts/optimizing/... 目录下
        proposals_root = PROJECT_ROOT / "research_proposals"
        self.proposal_dir = proposals_root / proposal_id
        # 如果根目录没有，在 lifecycle 各阶段目录中查找
        if not self.proposal_dir.exists():
            for stage in ["drafts", "optimizing", "pending_review", "archived"]:
                candidate = proposals_root / stage / proposal_id
                if candidate.exists():
                    self.proposal_dir = candidate
                    break
        self.state_path = self.proposal_dir / "00_pipeline" / "hermes-pipeline-state.json"
        self.proposal_dir.mkdir(parents=True, exist_ok=True)
        (self.proposal_dir / "00_pipeline").mkdir(parents=True, exist_ok=True)
        # 已有 proposal 来源（hermes_workspace 下的历史项目）
        self._hermes_proposals = Path.home() / "Desktop" / "hermes_workspace" / "research_proposals"

        # 从命名规则解析项目类型（general/key/major）
        self.project_type = self._detect_project_type()

    def _detect_project_type(self) -> str:
        """从课题 ID 命名规则解析项目类型。

        命名规则：{项目类型}-{课题名称}-{日期}
        """
        # 优先从 lifecycle 状态读取
        lifecycle_path = proposals_root_lifecycle = (
            PROJECT_ROOT / "research_proposals" / "_lifecycle.json"
        )
        if lifecycle_path.exists():
            try:
                lc_state = json.loads(lifecycle_path.read_text(encoding="utf-8"))
                prop = lc_state.get("proposals", {}).get(self.proposal_id, {})
                if prop.get("project_type"):
                    return prop["project_type"]
            except Exception:
                pass
        # 从 ID 前缀解析
        for ptype in ["general", "key", "major"]:
            if self.proposal_id.startswith(ptype + "-"):
                return ptype
        return "general"

    # ------------------------------------------------------------------
    # 已有 proposal 导入（增量优化模式）
    # ------------------------------------------------------------------

    def list_importable_proposals(self) -> List[Dict[str, Any]]:
        """列出 hermes_workspace 中可导入的已有 proposal。

        Returns:
            [{id, name, file_count, latest_mtime, has_drafts, has_reports}]
        """
        results = []
        if not self._hermes_proposals.exists():
            return results
        for d in sorted(self._hermes_proposals.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            files = list(d.rglob("*.md"))
            has_drafts = any("draft" in str(f).lower() or "nsfc" in f.name.lower() for f in files)
            has_reports = any("report" in f.name.lower() or "精读" in f.name for f in files)
            latest_mtime = max((f.stat().st_mtime for f in files), default=0)
            results.append({
                "id": d.name,
                "name": d.name,
                "file_count": len(files),
                "latest_mtime": latest_mtime,
                "has_drafts": has_drafts,
                "has_reports": has_reports,
            })
        return results

    def import_existing_proposal(
        self,
        source_name: str,
        max_files: int = 50,
    ) -> Dict[str, Any]:
        """从 hermes_workspace 导入已有 proposal 作为管线初始内容。

        选择性导入最有价值的文件（申请书草稿、精读报告、立项依据、课题方向），
        避免全量复制（日报等历史文件意义不大）。

        Args:
            source_name: hermes_workspace/research_proposals/ 下的目录名
            max_files: 最大导入文件数

        Returns:
            {imported, skipped, detail}
        """
        source_dir = self._hermes_proposals / source_name
        if not source_dir.exists():
            return {"imported": 0, "skipped": 0, "error": f"源目录不存在: {source_dir}"}

        # 导入策略：按价值优先级选择文件
        priority_patterns = [
            ("drafts/", "申请书草稿"),
            ("reports/", "精读报告"),
            ("立项依据", "立项依据"),
            ("candidate_directions", "候选方向"),
            ("candidate_pool", "候选池"),
            ("topics/", "课题方向"),
            ("knowledge_base/", "知识库"),
            ("references/notes/", "论文笔记"),
        ]

        imported_files = []
        for pattern, label in priority_patterns:
            matches = list(source_dir.rglob(f"*{pattern}*"))
            for f in matches:
                if f.is_file() and f.suffix == ".md":
                    if len(imported_files) >= max_files:
                        break
                    # 计算目标路径：保留相对结构
                    rel = f.relative_to(source_dir)
                    target = self.proposal_dir / "00_imported" / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        target.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
                        imported_files.append({
                            "source": str(rel),
                            "target": str(target.relative_to(self.proposal_dir)),
                            "label": label,
                        })
                    except Exception:
                        pass

        # 记录导入元信息
        import_meta = {
            "source": source_name,
            "source_path": str(source_dir),
            "imported_at": now_utc(),
            "file_count": len(imported_files),
            "files": imported_files[:20],  # 保留前 20 条记录
        }
        meta_path = self.proposal_dir / "00_imported" / "import-meta.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        save_json(meta_path, import_meta)

        if _log:
            _log.info(f"导入 {source_name}: {len(imported_files)} 个文件")

        return {
            "imported": len(imported_files),
            "skipped": max(0, max_files - len(imported_files)),
            "detail": import_meta,
        }

    def _build_incremental_context(self, stage: int) -> str:
        """为指定阶段构建增量优化上下文（读取已有产物 + 导入内容）。

        如果该阶段产物已存在，提示 agent 做增量优化而非从零生成。
        如果有导入内容，提供相关文件路径供 agent 参考。

        Returns:
            附加到 prompt 的上下文字符串
        """
        context_parts = []

        # 检查当前阶段是否已有产物（增量优化模式）
        artifacts = STAGE_ARTIFACTS.get(stage, [])
        existing_artifacts = []
        for rel_path in artifacts:
            full = self.proposal_dir / rel_path
            if full.exists() and full.stat().st_size >= 50:
                existing_artifacts.append(rel_path)

        if existing_artifacts:
            context_parts.append(
                "⚠ 增量优化模式：以下产物已存在，请先读取理解，再融合最新信息优化，不要推倒重来：\n"
                + "\n".join(f"  - {p}" for p in existing_artifacts)
            )

        # 检查导入的历史内容
        import_dir = self.proposal_dir / "00_imported"
        if import_dir.exists():
            imported_files = list(import_dir.rglob("*.md"))
            if imported_files:
                # 按阶段相关性筛选
                stage_keywords = {
                    0: ["方向", "direction", "candidate_directions"],
                    1: ["论文", "paper", "精读", "references"],
                    2: ["缺口", "gap", "竞争", "landscape"],
                    3: ["问题", "question", "topics"],
                    4: ["申请书", "draft", "nsfc", "立项依据"],
                    5: ["验收", "review", "检查"],
                }
                keywords = stage_keywords.get(stage, [])
                relevant = [
                    f for f in imported_files
                    if any(kw in str(f).lower() or kw in f.name.lower() for kw in keywords)
                ][:10]  # 最多 10 个相关文件
                if relevant:
                    context_parts.append(
                        "📁 已有历史内容可供参考（来自之前的工作积累）：\n"
                        + "\n".join(
                            f"  - {f.relative_to(self.proposal_dir)}"
                            for f in relevant
                        )
                    )

        # 检查上游阶段产物（链路依赖）
        if stage > 0:
            upstream_artifacts = STAGE_ARTIFACTS.get(stage - 1, [])
            existing_upstream = []
            for rel_path in upstream_artifacts:
                full = self.proposal_dir / rel_path
                if full.exists() and full.stat().st_size >= 50:
                    existing_upstream.append(rel_path)
            if existing_upstream:
                context_parts.append(
                    "📋 上游阶段产物（本阶段的输入）：\n"
                    + "\n".join(f"  - {p}" for p in existing_upstream)
                )

        if context_parts:
            return "\n\n=== 增量上下文 ===\n\n" + "\n\n".join(context_parts) + "\n"
        return ""

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
        # v6.7.7 修复：统一使用 hermes_subprocess_env，自动读取 .env 并透传 ZAI_API_KEY
        from common import hermes_subprocess_env
        env = hermes_subprocess_env()

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
        # 改造：stage 1（文献调研）注入已处理论文 ID，避免重复检索
        if stage == 1:
            try:
                import state_sync as _ss
                processed_ids = _ss.get_processed_ids()
                if processed_ids:
                    exclude_str = (
                        f"\n\n【请跳过以下已处理论文（共 {len(processed_ids)} 篇）】\n"
                        + "\n".join(sorted(processed_ids))
                    )
                    prompt += exclude_str
            except Exception:
                pass
        # v6.4.1 增量优化：自动追加已有产物 + 导入内容 + 上游依赖的上下文
        incremental_ctx = self._build_incremental_context(stage)
        if incremental_ctx:
            prompt += incremental_ctx
        # v6.4.2 针对性检索：撰写环节自动引用已有检索报告
        if stage in (4, 5):  # 申请书撰写 + 质量自检
            research_ctx = self._build_research_context_for_writing()
            if research_ctx:
                prompt += research_ctx
            # v6.6.0 按项目类型注入撰写模板和质量标准
            type_ctx = self._build_project_type_context()
            if type_ctx:
                prompt += type_ctx
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
    # 针对性检索（撰写时按需检索）
    # ------------------------------------------------------------------

    def targeted_research(
        self,
        topic: str,
        context: str = "",
        depth: str = "standard",
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """针对性检索：撰写申请书/方法学手册时，对特定主题做精准文献检索。

        与文献简报（广撒网被动积累）不同，针对性检索是"精准打击"——
        基于当前撰写需求，检索最新、最相关的论文和资料。

        派活给 researcher profile（具备 web_search + DeepXiv 能力），
        结果写入 proposal 目录供撰写环节引用。

        Args:
            topic: 检索主题（如"BSV 驱动 HHG 的量子几何修正"）
            context: 撰写上下文（如"正在写立项依据，需要 BSV-HHG 实验证据"）
            depth: 检索深度（quick=3篇/standard=8篇/deep=15篇）
            timeout: hermes agent loop 超时

        Returns:
            {success, report_path, paper_count, output_preview, error}
        """
        max_papers = {"quick": 3, "standard": 8, "deep": 15}.get(depth, 8)

        # 生成检索报告路径
        import hashlib
        topic_hash = hashlib.md5(topic.encode()).hexdigest()[:8]
        report_dir = self.proposal_dir / "02_literature" / "targeted-research"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"research_{topic_hash}.md"

        prompt = (
            f"你是专业文献调研员。请针对以下主题做精准检索：\n\n"
            f"【检索主题】{topic}\n"
            f"【撰写上下文】{context or '（无额外上下文）'}\n"
            f"【检索深度】{depth}（需 {max_papers} 篇核心论文）\n\n"
            f"请执行以下步骤：\n"
            f"1. 使用 web_search 和 DeepXiv 工具检索该主题的最新论文（2023-2026）\n"
            f"2. 对每篇论文评分（相关性/新颖性/可靠性/时效性，各 0-1 分）\n"
            f"3. 提取每篇论文的关键发现（与检索主题的相关性）\n"
            f"4. 总结该主题的当前研究现状和关键争议\n\n"
            f"输出格式：\n"
            f"# 针对性检索报告：{topic}\n"
            f"## 检索策略\n- 关键词组合：...\n- 数据源：...\n\n"
            f"## 论文清单（按相关性排序）\n"
            f"| arxiv_id/DOI | 标题 | 相关性 | 关键发现 |\n"
            f"|-------------|------|--------|---------|\n\n"
            f"## 研究现状总结\n...\n\n"
            f"## 关键争议/未解决问题\n...\n\n"
            f"## 对撰写的建议\n哪些论文应该引用、引用在哪一章\n\n"
            f"将报告写入文件：{report_path}\n"
        )

        # 追加上游产物上下文（如果已有缺口分析/问题框架）
        incremental_ctx = self._build_incremental_context(2)  # 参考缺口分析阶段
        if incremental_ctx:
            prompt += incremental_ctx

        if _log:
            _log.info(f"针对性检索: topic={topic[:40]} depth={depth}")

        result = self._run_hermes("researcher", prompt, timeout=timeout)

        # 检查产物
        artifacts_ok = report_path.exists() and report_path.stat().st_size >= 50

        return {
            "success": result["success"],
            "report_path": str(report_path.relative_to(self.proposal_dir)) if artifacts_ok else "",
            "artifacts_ok": artifacts_ok,
            "paper_count": max_papers,
            "output_preview": (result.get("output", "") or "")[:500],
            "elapsed_s": result.get("elapsed_s", 0),
            "error": result.get("error", ""),
        }

    def list_targeted_research(self) -> List[Dict[str, Any]]:
        """列出已有的针对性检索报告。"""
        research_dir = self.proposal_dir / "02_literature" / "targeted-research"
        if not research_dir.exists():
            return []
        results = []
        for f in sorted(research_dir.glob("*.md")):
            size = f.stat().st_size
            # 从文件第一行提取主题
            topic = ""
            try:
                first_line = f.read_text(encoding="utf-8").split("\n", 1)[0]
                topic = first_line.replace("#", "").replace("针对性检索报告：", "").strip()
            except Exception:
                pass
            results.append({
                "file": f.name,
                "topic": topic,
                "size": size,
                "path": str(f.relative_to(self.proposal_dir)),
            })
        return results

    def _build_research_context_for_writing(self) -> str:
        """为撰写环节构建针对性检索结果的上下文。

        如果已有针对性检索报告，在撰写 prompt 中引用它们，
        让 writer profile 能基于最新检索结果撰写。

        Returns:
            附加到撰写 prompt 的上下文字符串
        """
        research_reports = self.list_targeted_research()
        if not research_reports:
            return ""

        lines = ["📚 已有针对性检索报告（撰写时请参考这些最新检索结果）："]
        for r in research_reports:
            lines.append(f"  - {r['path']}（{r['size']} 字节，主题：{r['topic'][:50]}）")
        lines.append("\n请在撰写时引用这些报告中的论文，确保引文准确、时效性强。")

        return "\n\n=== 针对性检索参考 ===\n\n" + "\n".join(lines) + "\n"

    def _build_project_type_context(self) -> str:
        """按项目类型构建撰写模板和质量标准上下文（v6.6.0）。

        从 memory/nsfc-standards.json 读取对应项目类型的：
        - 撰写模板（章节结构、子节、写作提示）
        - 质量标准（评审维度权重、质量阈值）
        - 评审清单

        让 writer/critic 按项目类型标准工作。
        """
        standards_path = PROJECT_ROOT / "memory" / "nsfc-standards.json"
        if not standards_path.exists():
            return ""

        try:
            standards = json.loads(standards_path.read_text(encoding="utf-8"))
        except Exception as e:
            if _log:
                _log.error(f"_build_project_type_context 读取标准失败: {e}")
            return ""

        ptype = self.project_type
        templates = standards.get("proposal_templates", {})
        template = templates.get(ptype, {})
        project_types_cfg = standards.get("project_types", {})
        type_cfg = project_types_cfg.get(ptype, {})

        if not template and not type_cfg:
            return ""

        lines = [f"\n📋 项目类型：{ptype}（{type_cfg.get('name_cn', '')}）"]

        # 撰写模板
        if template:
            lines.append(f"正文结构：{template.get('_structure', '')}")
            lines.append(f"页数限制：{template.get('_page_limit', '不限')}")
            lines.append("\n章节结构：")
            for sec in template.get("sections", []):
                lines.append(f"  {sec['title']}")
                lines.append(f"    要求：{sec.get('requirement', '')}")
                for sub in sec.get("subsections", []):
                    lines.append(f"    - {sub}")
                if sec.get("writing_tips"):
                    lines.append(f"    写作提示：{sec['writing_tips']}")

        # 评审维度权重
        eval_focus = type_cfg.get("evaluation_focus", {})
        if eval_focus:
            lines.append("\n评审维度权重：")
            for dim, weight in eval_focus.items():
                lines.append(f"  {dim}: {weight}")

        # 质量阈值
        threshold = type_cfg.get("quality_threshold", {})
        if threshold:
            lines.append(f"\n质量阈值：综合分≥{threshold.get('min_overall_score', '?')}, "
                         f"high问题≤{threshold.get('max_high_issues', '?')}, "
                         f"medium问题≤{threshold.get('max_medium_issues', '?')}")

        # 方法手册要求
        lines.append("\n同时生成方法学手册（methodology-manual.md）：申请书重思路，"
                     "公式推导/参数表/技术路线图等细节放方法学手册。")

        return "\n\n=== 项目类型标准 ===\n" + "\n".join(lines) + "\n"

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

        env = clean_subprocess_env()

        cmd = [
            "hermes", "--profile", "pipeline-runner", "cron", "create",
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
        assert STAGE_PROFILE_MAP[i] in ("pipeline-runner", "linsai", "researcher", "analyst", "writer", "reviewer")
        assert "{proposal_dir}" in STAGE_PROMPTS[i]
    print("✓")

    # 2. profile 映射合理性
    print("[2] profile 映射...", end=" ")
    assert STAGE_PROFILE_MAP[0] == "pipeline-runner"  # 方向校准 → 编排器
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
    parser.add_argument("--list-importable", action="store_true",
                        help="列出可导入的已有 proposal")
    parser.add_argument("--import", nargs=2, metavar=("PROPOSAL_ID", "SOURCE_NAME"),
                        dest="import_proposal",
                        help="从 hermes_workspace 导入已有 proposal 作为初始内容")
    parser.add_argument("--research", nargs="+", metavar=("PROPOSAL_ID", "TOPIC"),
                        help="针对性检索（--research PROPOSAL_ID TOPIC [--depth standard] [--context '正在写立项依据']）")
    parser.add_argument("--list-research", metavar="PROPOSAL_ID",
                        help="列出已有的针对性检索报告")
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

    if args.list_importable:
        pipe = HermesPipeline("__tmp__")
        proposals = pipe.list_importable_proposals()
        print(f"=== 可导入的已有 proposal（{len(proposals)} 个）===")
        for p in proposals:
            drafts = "✓草稿" if p["has_drafts"] else ""
            reports = "✓报告" if p["has_reports"] else ""
            print(f"  {p['name']:40s} {p['file_count']:4d} 文件  {drafts} {reports}")
        # 清理临时目录
        import shutil
        shutil.rmtree(pipe.proposal_dir, ignore_errors=True)
        return 0

    if args.import_proposal:
        proposal_id, source_name = args.import_proposal
        pipe = HermesPipeline(proposal_id)
        result = pipe.import_existing_proposal(source_name)
        print(f"导入结果: 导入 {result.get('imported', 0)} 个文件")
        if result.get("error"):
            print(f"错误: {result['error']}")
        return 0 if result.get("imported", 0) > 0 else 1

    if args.research:
        # --research PROPOSAL_ID TOPIC [--depth X] [--context Y]
        research_args = args.research
        if len(research_args) < 2:
            print("用法: --research PROPOSAL_ID TOPIC [--depth standard] [--context '正在写立项依据']")
            return 1
        proposal_id = research_args[0]
        topic = research_args[1]
        depth = "standard"
        context = ""
        i = 2
        while i < len(research_args):
            if research_args[i] == "--depth" and i + 1 < len(research_args):
                depth = research_args[i + 1]
                i += 2
            elif research_args[i] == "--context" and i + 1 < len(research_args):
                context = research_args[i + 1]
                i += 2
            else:
                topic += " " + research_args[i]
                i += 1
        pipe = HermesPipeline(proposal_id)
        result = pipe.targeted_research(topic, context=context, depth=depth)
        print(f"针对性检索: {'✓' if result.get('artifacts_ok') else '✗'}")
        print(f"报告: {result.get('report_path', '(未生成)')}")
        print(f"耗时: {result.get('elapsed_s', 0)}s")
        if result.get("error"):
            print(f"错误: {result['error']}")
        return 0 if result.get("artifacts_ok") else 1

    if args.list_research:
        pipe = HermesPipeline(args.list_research)
        reports = pipe.list_targeted_research()
        print(f"=== 针对性检索报告（{len(reports)} 个）===")
        for r in reports:
            print(f"  {r['size']:6d} 字节  {r['topic'][:50]}")
            print(f"           路径: {r['path']}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
