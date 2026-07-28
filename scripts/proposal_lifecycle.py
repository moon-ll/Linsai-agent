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
import time as _time
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock, clean_subprocess_env
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
DEFAULT_STAGGER_SECONDS = 90  # 错峰间隔（秒），课题间留间隔避免扎堆（P0-1）

# 申请书章节定义（P1-1: 章节级对抗）
PROPOSAL_SECTIONS = [
    {"key": "rationale", "title": "（一）立项依据", "cn": "立项依据", "desc": "科学意义、前人研究局限性"},
    {"key": "content", "title": "（二）研究内容", "cn": "研究内容", "desc": "研究内容、特色与创新点"},
    {"key": "method", "title": "（三）研究方案", "cn": "研究方案", "desc": "技术路线、可行性"},
]


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

    def _set_proposal_state(self, proposal_id: str, data: Dict[str, Any]) -> bool:
        """持久化单个 proposal 状态，返回是否成功。

        v6.7.1 修复：
        - 写入后重新读取校验，避免并发覆盖导致的状态丢失
        - 校验失败时最多重试 2 次
        """
        for attempt in range(3):
            try:
                with file_lock("proposal-lifecycle"):
                    state = self._load_state()
                    state["proposals"][proposal_id] = data
                    self._save_state(state)

                    # 写入后校验：重新读取确认 proposal 数据已持久化
                    verify = self._load_state()
                    persisted = verify["proposals"].get(proposal_id, {})
                    if persisted.get("updated_at") == data.get("updated_at"):
                        return True
                    # 校验失败：可能被其他进程覆盖，重试
                    if _log:
                        _log.warning(
                            f"[_set_proposal_state] {proposal_id} 写入校验失败，"
                            f"第 {attempt + 1} 次重试"
                        )
            except Exception as e:
                if _log:
                    _log.error(f"[_set_proposal_state] {proposal_id} 写入异常: {e}")
        return False

    def _find_proposal_dir(self, proposal_id: str) -> Optional[Path]:
        """在四个阶段目录中查找 proposal 目录。"""
        for stage in LIFECYCLE_STAGES:
            d = self.root / stage / proposal_id
            if d.exists():
                return d
        return None

    # ------------------------------------------------------------------
    # 课题命名规则（v6.5.4）
    # ------------------------------------------------------------------

    # 命名规则：{项目类型}-{课题名称}-{启动日期}
    # 课题名称取自课题的具体科学问题或核心方法（而非大的研究领域）
    # 示例：general-quantum-geometry-inversion-20260726
    #       key-bsv-driven-hhg-20260726
    #       major-topological-photoresponse-mapping-20260726
    # 项目类型简称：general(面上) / key(重点) / major(重大)
    _NAMING_PATTERN = None  # 编译时初始化

    # 项目类型 → 简称映射
    PROJECT_TYPE_SHORT = {
        "general": "general",
        "key": "key",
        "major": "major",
    }

    @classmethod
    def _get_naming_pattern(cls):
        if cls._NAMING_PATTERN is None:
            import re
            # general-quantum-geometry-inversion-20260726
            # 项目类型-课题名称(基于科学问题/核心方法)-日期(YYYYMMDD)[-序号]
            cls._NAMING_PATTERN = re.compile(
                r"^(general|key|major)-([a-z][a-z0-9-]{1,40})-(\d{4})(\d{2})(\d{2})(?:-(\d{2}))?$"
            )
        return cls._NAMING_PATTERN

    def validate_proposal_id(self, proposal_id: str) -> Dict[str, Any]:
        """校验课题 ID 是否符合命名规则。

        规则：{项目类型}-{课题名称}-{启动日期}[-序号]
        - 项目类型：general(面上) / key(重点) / major(重大)
        - 课题名称：取自课题的具体科学问题或核心方法（非研究领域），
                    2-40位小写字母/数字/连字符
        - 启动日期：YYYYMMDD 格式
        - 序号：可选，同一天同名的第二个起加序号

        命名要点：
          ✓ quantum-geometry-inversion（量子几何反演——具体方法）
          ✓ bsv-driven-hhg（BSV驱动的高次谐波——具体问题）
          ✗ hhg（太泛，是研究领域不是课题内容）
          ✗ optics（太泛）

        Returns:
            {valid, reason, parsed: {project_type, name, date, seq}}
        """
        pattern = self._get_naming_pattern()
        match = pattern.match(proposal_id)
        if not match:
            return {
                "valid": False,
                "reason": (
                    f"命名不符合规则。正确格式：{{项目类型}}-{{课题名称}}-{{YYYYMMDD}}\n"
                    f"项目类型：general(面上) / key(重点) / major(重大)\n"
                    f"课题名称：取自具体科学问题/核心方法，非研究领域\n"
                    f"示例：general-quantum-geometry-inversion-20260726\n"
                    f"收到：{proposal_id}"
                ),
                "parsed": None,
            }
        return {
            "valid": True,
            "reason": "命名合规",
            "parsed": {
                "project_type": match.group(1),
                "name": match.group(2),
                "date": f"{match.group(3)}-{match.group(4)}-{match.group(5)}",
                "date_raw": match.group(3) + match.group(4) + match.group(5),
                "seq": match.group(6),
            },
        }

    def generate_proposal_id(
        self,
        name: str,
        project_type: str = "general",
        date_str: Optional[str] = None,
    ) -> str:
        """自动生成课题 ID。

        Args:
            name: 课题名称缩写（如 hhg, bsv, quantum-geometry）
            project_type: 项目类型（general/key/major）
            date_str: 启动日期 YYYYMMDD（默认今天）

        Returns:
            符合命名规则的课题 ID
        """
        if date_str is None:
            import datetime
            date_str = datetime.datetime.now().strftime("%Y%m%d")

        name = name.lower().strip()
        type_short = self.PROJECT_TYPE_SHORT.get(project_type, "general")
        base = f"{type_short}-{name}-{date_str}"

        # 如果已存在，加序号后缀（-02, -03...）
        state = self._load_state()
        existing_ids = set(state["proposals"].keys())

        if base not in existing_ids:
            for stage in LIFECYCLE_STAGES:
                if (self.root / stage / base).exists():
                    break
            else:
                return base

        # 同一天同名课题加序号
        for seq in range(2, 100):
            candidate = f"{base}-{seq:02d}"
            if candidate not in existing_ids:
                exists_in_dir = False
                for stage in LIFECYCLE_STAGES:
                    if (self.root / stage / candidate).exists():
                        exists_in_dir = True
                        break
                if not exists_in_dir:
                    return candidate

        return f"{base}-99"

    # ------------------------------------------------------------------
    # 注册新 proposal
    # ------------------------------------------------------------------

    def register(
        self,
        proposal_id: str = "",
        project_type: str = "general",
        source: str = "new",
        source_detail: str = "",
        name: str = "",
        date_str: Optional[str] = None,
        validate: bool = True,
    ) -> Dict[str, Any]:
        """注册新 proposal 到初稿区。

        命名规则：{项目类型}-{课题名称}-{启动日期}
        可通过 proposal_id 直接指定，或通过 name+project_type 自动生成。

        Args:
            proposal_id: 课题 ID（为空时从 name+project_type 自动生成）
            project_type: 项目类型（general/key/major）
            source: 来源（new=全新/expansion=扩展归档课题）
            source_detail: 来源详情
            name: 课题名称缩写（proposal_id 为空时使用，如 hhg/quantum-geometry）
            date_str: 启动日期 YYYYMMDD（默认今天）
            validate: 是否校验命名规则

        Returns:
            {success, proposal_id, status, path}
        """
        if project_type not in PROJECT_TYPES:
            return {"success": False, "error": f"非法项目类型: {project_type}"}

        # 自动生成 proposal_id
        if not proposal_id:
            if not name:
                return {"success": False, "error": "需要 proposal_id 或 name"}
            proposal_id = self.generate_proposal_id(name, project_type, date_str)

        # 校验命名规则
        if validate:
            validation = self.validate_proposal_id(proposal_id)
            if not validation["valid"]:
                return {"success": False, "error": validation["reason"]}

        # 如果已存在，不重复注册
        existing = self._get_proposal_state(proposal_id)
        if existing:
            return {
                "success": False,
                "error": f"proposal 已存在，当前状态: {existing.get('status')}",
            }

        target_dir = self.root / "drafts" / proposal_id
        target_dir.mkdir(parents=True, exist_ok=True)

        # 创建标准目录结构（v6.6.0 漏洞2修复）
        standard_dirs = [
            "01_direction",
            "02_literature/targeted-research",
            "02_topic",
            "03_question",
            "04_proposal",
            "05_review",
        ]
        for d in standard_dirs:
            (target_dir / d).mkdir(parents=True, exist_ok=True)

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
            "section_passes": {},  # P1-3: 各模块对抗胜利状态
            "human_feedback_count": 0,
            "transition_history": [
                {"to": "drafts", "at": now_utc(), "reason": "注册新 proposal"}
            ],
        }
        self._set_proposal_state(proposal_id, state_data)

        # 自动初始化 proposal-brief（v6.6.0 漏洞5修复）
        try:
            self.update_proposal_brief(proposal_id)
        except Exception:
            pass

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
    # proposal-brief 元信息文件（贯穿全生命周期）
    # ------------------------------------------------------------------

    def update_proposal_brief(self, proposal_id: str) -> Dict[str, Any]:
        """更新课题的 proposal-brief.md 元信息文件。

        贯穿全生命周期的"身份证"——从初稿到归档，
        打开课题目录第一眼就能看到课题全貌和当前状态。

        自动汇总：
        - 课题基本信息（ID/类型/状态/日期）
        - 核心问题与创新点（从已有产出中提取）
        - 优化历史（轮次/分数/问题数）
        - 人工审核记录
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": "proposal 未注册"}

        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}

        brief_path = prop_dir / "00_proposal-brief.md"

        # 提取课题标题和核心内容
        title = self._extract_proposal_title(prop_dir)
        core_questions = self._extract_core_questions(prop_dir)
        innovations = self._extract_innovations(prop_dir)

        # 状态映射
        status_map = {
            "drafts": "初稿（等待确认思路）",
            "optimizing": f"优化中（第{prop_state.get('optimization_rounds', 0)}轮，score {prop_state.get('last_score', 0):.2f}）",
            "pending_review": "待校验（等待人工核验）",
            "archived": "已归档",
        }
        type_map = {"general": "面上项目", "key": "重点项目", "major": "重大项目"}

        # 构建优化历史表
        score_history = prop_state.get("score_history", [])
        history_lines = []
        if score_history:
            history_lines.append("| 轮次 | 分数 | 问题数 | high问题 | 时间 |")
            history_lines.append("|------|------|--------|---------|------|")
            for h in score_history:
                history_lines.append(
                    f"| {h['round']} | {h['score']:.2f} | {h.get('issues_count', 0)} | "
                    f"{h.get('high_issues', 0)} | {h.get('at', '')[:10]} |"
                )
        else:
            history_lines.append("（尚未开始优化）")

        # 构建流转历史
        transition_history = prop_state.get("transition_history", [])
        transition_lines = []
        if transition_history:
            for t in transition_history:
                reason = t.get("reason", "")
                transition_lines.append(
                    f"- {t.get('at', '')[:10]}: {t.get('from', '—')} → {t.get('to', '?')} {f'({reason})' if reason else ''}"
                )

        # 构建人工反馈记录
        feedback_count = prop_state.get("human_feedback_count", 0)
        feedback_lines = []
        if feedback_count > 0:
            feedback_dir = prop_dir / "06_feedback"
            for i in range(1, feedback_count + 1):
                structured_path = feedback_dir / f"feedback-{i}-structured.json"
                if structured_path.exists():
                    try:
                        import json
                        sf = json.loads(structured_path.read_text(encoding="utf-8"))
                        verdict = sf.get("verdict", "?")
                        issues = sf.get("issues", [])
                        feedback_lines.append(
                            f"- 第{i}次审核: {verdict}（{len(issues)}个问题）"
                        )
                    except Exception:
                        feedback_lines.append(f"- 第{i}次审核: （详情见 06_feedback/）")
        else:
            feedback_lines.append("（尚未有人工审核）")

        # 组装 brief
        brief_content = f"""# 课题说明

**课题名称**：{title or "（待生成）"}
**项目类型**：{type_map.get(prop_state.get('project_type', 'general'), '?')}
**课题 ID**：`{proposal_id}`
**当前状态**：{status_map.get(prop_state.get('status', 'drafts'), '?')}
**启动日期**：{prop_state.get('created_at', '')[:10]}
**最后更新**：{prop_state.get('updated_at', '')[:10]}

---

## 核心问题
{core_questions or "（待管线生成）"}

## 创新点
{innovations or "（待管线生成）"}

---

## 优化历史
{chr(10).join(history_lines)}

## 状态流转
{chr(10).join(transition_lines) if transition_lines else "（无流转记录）"}

## 人工审核记录
{chr(10).join(feedback_lines)}

---

## 课题产物索引
- `01_direction/` — 方向校准
- `02_literature/` — 文献调研 + 针对性检索
- `02_topic/` — 缺口分析
- `03_question/` — 科学问题框架
- `04_proposal/proposal-draft.md` — 申请书正文
- `04_proposal/methodology-manual.md` — 方法学手册（细节）
- `05_review/` — 终审 + 对抗评审（critic-round-N.md）
- `06_feedback/` — 人工反馈记录
"""

        brief_path.write_text(brief_content, encoding="utf-8")

        if _log:
            _log.info(f"更新 proposal-brief: {proposal_id}")

        return {"success": True, "path": str(brief_path.relative_to(PROJECT_ROOT))}

    def _extract_proposal_title(self, prop_dir: Path) -> str:
        """从申请书或课题说明中提取标题。"""
        # 优先从申请书提取
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        if proposal_path.exists():
            try:
                content = proposal_path.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if line.strip().startswith("**") and "课题名称" not in line:
                        # 提取 **标题** 格式
                        title = line.strip().strip("*").strip()
                        if len(title) > 5 and len(title) < 200:
                            return title
                    if "## 课题名称" in line:
                        # 下一行可能是标题
                        continue
            except Exception:
                pass

        # 从 brief 提取
        brief_path = prop_dir / "00_proposal-brief.md"
        if brief_path.exists():
            try:
                content = brief_path.read_text(encoding="utf-8")
                for line in content.split("\n"):
                    if "课题名称" in line and "**" in line:
                        # 提取 **课题名称**：XXX
                        parts = line.split("：", 1)
                        if len(parts) > 1:
                            return parts[1].strip().strip("*").strip()
            except Exception:
                pass

        return ""

    def _extract_core_questions(self, prop_dir: Path) -> str:
        """从科学问题框架中提取核心问题。"""
        q_path = prop_dir / "03_question" / "question-framework.md"
        if q_path.exists():
            try:
                content = q_path.read_text(encoding="utf-8")
                lines = []
                for line in content.split("\n"):
                    stripped = line.strip()
                    # 匹配 Q1：/ Q1: / **Q1 等格式
                    if (stripped.startswith("Q") and 
                        (":" in stripped or "：" in stripped) and
                        len(stripped) > 5):
                        lines.append(stripped)
                    # 匹配 **主问题** 格式
                    elif "主问题" in stripped and ("**" in stripped or len(stripped) > 10):
                        lines.append(stripped)
                if lines:
                    return "\n".join(lines[:4])
                # 兜底：提取主攻方向
                for line in content.split("\n"):
                    if "主攻方向" in line:
                        return line.strip()
            except Exception:
                pass
        return ""

    def _extract_innovations(self, prop_dir: Path) -> str:
        """从申请书中提取创新点。"""
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        if proposal_path.exists():
            try:
                content = proposal_path.read_text(encoding="utf-8")
                in_innovation = False
                lines = []
                for line in content.split("\n"):
                    if "特色" in line and "创新" in line and "##" in line:
                        in_innovation = True
                        continue
                    if in_innovation:
                        # 遇到下一个 ## 章节停止
                        if line.strip().startswith("## ") and "创新" not in line and "特色" not in line:
                            break
                        # 匹配 ### 4.1 / 1. / - 等格式
                        stripped = line.strip()
                        if (stripped.startswith("###") or 
                            (len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in ".")):
                            # 清理格式
                            clean = stripped.lstrip("#").strip()
                            lines.append(clean)
                if lines:
                    return "\n".join(lines[:5])
            except Exception:
                pass
        return ""

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

        # 更新 proposal-brief（状态变更后）
        try:
            self.update_proposal_brief(proposal_id)
        except Exception:
            pass

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

        # P1-1: 确定本轮聚焦章节（轮转 + 每4轮整体审查）
        section_cycle = current_round % (len(PROPOSAL_SECTIONS) + 1)
        if section_cycle < len(PROPOSAL_SECTIONS):
            focus_section = PROPOSAL_SECTIONS[section_cycle]
            is_full_review = False
        else:
            focus_section = None  # 第4轮做整体一致性审查
            is_full_review = True

        # 读取当前申请书
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        if not proposal_path.exists():
            return {"success": False, "error": "申请书不存在，请先执行管线生成初稿"}

        score_before = prop_state.get("last_score", 0.0)

        # 1. critic 评审
        if _log:
            section_name = focus_section["cn"] if focus_section else "整体一致性"
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: critic 评审（聚焦：{section_name}）")
        critic_result = self._run_critic(
            proposal_id, prop_dir, project_type, current_round + 1, critic_timeout,
            focus_section=focus_section, is_full_review=is_full_review,  # P1-1
        )
        if _log:
            elapsed = critic_result.get("elapsed_s", 0)
            _log.info(
                f"[{proposal_id}] 对抗轮 {current_round + 1}: critic 完成 "
                f"success={critic_result.get('success')} elapsed={elapsed}s"
            )

        # v6.7.4 修复：critic 失败/超时（如 elapsed=300s success=False）时不应计入一轮，
        # 否则 lifecycle 的 optimization_rounds 与实际 critic 报告文件脱节，导致一致性检查失败。
        if not critic_result.get("success"):
            err = critic_result.get("error", "unknown")
            if _log:
                _log.warning(
                    f"[{proposal_id}] 对抗轮 {current_round + 1}: critic 失败（{err[:80]}），"
                    f"不计入本轮，跳过 writer"
                )
            return {
                "success": False,
                "round": current_round + 1,
                "score_before": score_before,
                "score_after": score_before,
                "score_delta": 0.0,
                "error": err,
                "reason": "critic 失败，未修改状态",
            }

        # 预解析维度分数，供 writer 聚焦（P0-2）
        pre_dims = self._extract_dimension_scores(critic_result)
        pre_weakest = self._get_weakest_dimension(pre_dims)

        # P1-2: 文献定向补充（严谨性不足时触发 researcher 检索）
        lit_supplement = ""
        if pre_dims.get("rigor", 1.0) < 0.70 or self._has_lit_gap(critic_result):
            if _log:
                _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: researcher 定向检索文献缺口")
            lit_supplement = self._run_researcher_targeted(
                proposal_id, prop_dir, critic_result, focus_section,
                timeout=300,
            )

        # 2. writer 根据评审意见优化
        if _log:
            _log.info(f"[{proposal_id}] 对抗轮 {current_round + 1}: writer 优化")
        writer_result = self._run_writer_optimize(
            proposal_id, prop_dir, project_type, critic_result, writer_timeout,
            weakest_dim=pre_weakest, dim_scores=pre_dims,  # P0-2
            focus_section=focus_section, is_full_review=is_full_review,  # P1-1
            lit_supplement=lit_supplement,  # P1-2
        )
        if _log:
            elapsed = writer_result.get("elapsed_s", 0)
            _log.info(
                f"[{proposal_id}] 对抗轮 {current_round + 1}: writer 完成 "
                f"success={writer_result.get('success')} elapsed={elapsed}s"
            )

        # 3. 解析新分数（v6.6.3：优先从 critic 写入的 report_path 文件读取，
        #    hermes stdout 摘要通常只截取前几行，遗漏末尾的"## 评分"代码块）
        report_path = prop_dir / "05_review" / f"critic-round-{current_round + 1}.md"

        # v6.7.1: critic 通过 hermes agent loop 异步写盘，等待文件生成且稳定
        if not (report_path.exists() and report_path.stat().st_size > 100):
            waited = self._wait_for_critic_report(report_path, timeout=30)
            if waited and _log:
                _log.info(f"[{proposal_id}] critic 报告已生成: {report_path.name}")

        if report_path.exists() and report_path.stat().st_size > 100:
            try:
                file_content = report_path.read_text(encoding="utf-8")
                file_result = {"output": file_content}
                score_after = self._extract_score(file_result)
                dim_scores = self._extract_dimension_scores(file_result)  # P0-2
                issues = self._extract_issues(file_result)
            except Exception as e:
                if _log:
                    _log.warning(f"[{proposal_id}] 读取 critic 报告失败: {e}，回退到 stdout")
                # 回退：使用 hermes stdout 摘要
                score_after = self._extract_score(critic_result)
                dim_scores = self._extract_dimension_scores(critic_result)
                issues = self._extract_issues(critic_result)
        else:
            # 文件未生成（critic 未写盘），用 stdout 摘要
            if _log:
                _log.warning(f"[{proposal_id}] critic 报告未生成，使用 stdout 摘要评分")
            score_after = self._extract_score(critic_result)
            dim_scores = self._extract_dimension_scores(critic_result)
            issues = self._extract_issues(critic_result)
        weakest_dim = self._get_weakest_dimension(dim_scores)

        # P1-1: 确定本轮模块 key
        section_key = focus_section["key"] if focus_section else "full_review"

        # P1-3: 判断该模块是否"对抗胜利"（分数达标 + 各维度无短板）
        min_score = threshold.get("min_overall_score", DEFAULT_SCORE_THRESHOLD)
        weak_dims = [
            k for k, floor in self.DIMENSION_FLOOR.items()
            if k in dim_scores and dim_scores[k] < floor
        ]
        section_passed = score_after >= min_score and len(weak_dims) == 0

        # 4. 更新状态
        # v6.7.1：_set_proposal_state 内部已加 file_lock("proposal-lifecycle")，
        # 不再外层包 file_lock(f"proposal-{proposal_id}")，避免嵌套锁和潜在竞态
        prop_state = self._get_proposal_state(proposal_id)
        prop_state["optimization_rounds"] = current_round + 1
        prop_state["last_score"] = score_after
        prop_state["last_dim_scores"] = dim_scores  # P0-2: 记录维度分数
        # P1-3: 记录各模块对抗胜利状态
        section_passes = prop_state.get("section_passes", {})
        section_passes[section_key] = section_passed
        prop_state["section_passes"] = section_passes
        prop_state["score_history"].append({
            "round": current_round + 1,
            "score": score_after,
            "dim_scores": dim_scores,  # P0-2
            "weakest_dim": weakest_dim,  # P0-2
            "focus_section": section_key,  # P1-1
            "section_passed": section_passed,  # P1-3
            "issues_count": len(issues),
            "high_issues": sum(1 for i in issues if i.get("severity") == "high"),
            "at": now_utc(),
        })
        prop_state["updated_at"] = now_utc()
        persisted = self._set_proposal_state(proposal_id, prop_state)
        if not persisted and _log:
            _log.error(f"[{proposal_id}] _lifecycle.json 状态更新失败")

        # 4.5 更新 proposal-brief（贯穿全生命周期的元信息）
        try:
            self.update_proposal_brief(proposal_id)
        except Exception:
            pass

        # 5. 判定是否达标
        done_result = self._check_done(proposal_id, threshold)

        return {
            "success": True,
            "round": current_round + 1,
            "score_before": score_before,
            "score_after": score_after,
            "score_delta": round(score_after - score_before, 4),
            "dim_scores": dim_scores,  # P0-2
            "weakest_dim": weakest_dim,  # P0-2
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
        focus_section: Optional[Dict[str, str]] = None,
        is_full_review: bool = False,
    ) -> Dict[str, Any]:
        """派活给 critic profile 做对抗评审。

        P1-1: 支持章节级评审（focus_section）和整体审查（is_full_review）。
        """
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        standards_path = str(self.standards_path.relative_to(PROJECT_ROOT))
        report_path = prop_dir / "05_review" / f"critic-round-{round_num}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # P1-1: 构建章节聚焦指令
        if focus_section:
            focus_text = (
                f"\n【本轮聚焦章节】{focus_section['title']}（{focus_section['desc']}）\n"
                f"请重点深入评审该章节，其他章节只做简要一致性检查。\n"
                f"对该章节的评审应细致到段落级别。\n\n"
            )
        elif is_full_review:
            focus_text = (
                f"\n【本轮为整体一致性审查】\n"
                f"请检查三个章节之间的逻辑衔接、术语一致性、内容冗余/矛盾。\n"
                f"不需要逐段细审，聚焦整体连贯性。\n\n"
            )
        else:
            focus_text = ""

        prompt = (
            f"请对以下 NSFC 申请书做第 {round_num} 轮对抗评审。\n\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path} 中 project_types.{project_type} 的标准\n\n"
            f"【申请书文件】{proposal_path}\n"
            f"{focus_text}"
            f"请执行：\n"
            f"1. 读取申请书全文\n"
            f"2. 读取质量标准配置文件\n"
            f"3. 按项目类型标准做红队评审，尽可能找出问题\n"
            f"4. 每个问题给出具体、可执行的修改建议\n"
            f"5. 按严重程度分级（critical/high/medium/low）\n\n"
            f"【多维度评分（必填）】\n"
            f"请从以下 4 个维度分别评分（0-1），并指出每个维度的主要短板：\n"
            f"  - 创新性（innovation）：科学问题是否新颖、方法是否有突破\n"
            f"  - 可行性（feasibility）：技术路线能否落地、是否有支撑\n"
            f"  - 严谨性（rigor）：逻辑链条、文献支撑是否充分\n"
            f"  - 完整性（completeness）：章节是否齐全、格式是否规范\n\n"
            f"在评审报告末尾，必须包含如下格式的评分块（供程序解析）：\n"
            f"```\n"
            f"## 评分\n"
            f"创新性：0.85\n"
            f"可行性：0.80\n"
            f"严谨性：0.75\n"
            f"完整性：0.90\n"
            f"综合评分：0.82\n"
            f"```\n"
            f"将评审报告写入：{report_path}\n"
        )

        return self._run_hermes("critic", prompt, timeout)

    # P1-2: 文献缺口检测和定向检索
    def _has_lit_gap(self, critic_result: Dict[str, Any]) -> bool:
        """检测 critic 是否指出了文献缺口。"""
        output = critic_result.get("output", "")
        gap_keywords = ["文献不足", "缺乏文献", "文献缺口", "缺少引用", "引用不足",
                        "支撑不足", "无文献", "需补充文献", "文献支撑", "缺乏近"]
        return any(kw in output for kw in gap_keywords)

    def _run_researcher_targeted(
        self,
        proposal_id: str,
        prop_dir: Path,
        critic_result: Dict[str, Any],
        focus_section: Optional[Dict[str, str]],
        timeout: int = 300,
    ) -> str:
        """派活给 researcher profile 做定向文献检索（P1-2）。

        根据 critic 指出的文献缺口，检索 3-5 篇相关论文，
        结果写入 targeted-research 目录供 writer 引用。
        """
        # 生成检索 prompt
        section_hint = f"聚焦章节：{focus_section['cn']}\n" if focus_section else ""
        critic_output = critic_result.get("output", "")[:2000]  # 限制长度

        # 结果保存路径
        target_dir = prop_dir / "02_literature" / "targeted-research"
        target_dir.mkdir(parents=True, exist_ok=True)
        import time as _t
        result_path = target_dir / f"lit-gap-{int(_t.time())}.md"

        prompt = (
            f"请做定向文献检索（补充评审指出的文献缺口）。\n\n"
            f"【课题】{proposal_id}\n"
            f"{section_hint}"
            f"【评审指出的文献缺口】\n{critic_output}\n\n"
            f"请执行：\n"
            f"1. 从评审报告中提取文献缺口（哪些论点缺支撑、哪些方向缺引用）\n"
            f"2. 针对每个缺口，检索 2-3 篇最相关的近2年论文\n"
            f"3. 每篇论文给出：标题、作者、年份、核心结论、如何支撑该论点\n"
            f"4. 将检索结果写入：{result_path}\n"
            f"5. 格式：每个缺口一段，列出推荐引用的论文\n"
        )

        result = self._run_hermes("researcher", prompt, timeout)
        if result.get("success"):
            if _log:
                _log.info(f"[{proposal_id}] 文献补充完成: {result_path.name}")
            return f"\n【文献补充（researcher 定向检索）】\n请参考 {result_path} 中的新文献，在修订时引用。\n"
        else:
            if _log:
                _log.warning(f"[{proposal_id}] 文献补充失败: {result.get('error', '')[:100]}")
            return ""

    def _run_writer_optimize(
        self,
        proposal_id: str,
        prop_dir: Path,
        project_type: str,
        critic_result: Dict[str, Any],
        timeout: int,
        weakest_dim: str = "",
        dim_scores: Optional[Dict[str, float]] = None,
        focus_section: Optional[Dict[str, str]] = None,
        is_full_review: bool = False,
        lit_supplement: str = "",
    ) -> Dict[str, Any]:
        """派活给 writer profile 根据评审意见优化申请书。

        P0-2: 聚焦最弱维度，针对性改进。
        P1-1: 支持章节级修订（focus_section）。
        """
        proposal_path = prop_dir / "04_proposal" / "proposal-draft.md"
        standards_path = str(self.standards_path.relative_to(PROJECT_ROOT))
        # 找最新的 critic 报告
        review_dir = prop_dir / "05_review"
        critic_reports = sorted(review_dir.glob("critic-round-*.md"), reverse=True)
        latest_critic = str(critic_reports[0]) if critic_reports else ""

        # P0-2: 构建维度聚焦提示
        dim_focus = ""
        if weakest_dim and dim_scores:
            dim_cn = {"innovation": "创新性", "feasibility": "可行性", "rigor": "严谨性", "completeness": "完整性"}
            weakest_cn = dim_cn.get(weakest_dim, weakest_dim)
            dim_scores_str = "、".join(f"{dim_cn.get(k,k)} {v:.2f}" for k, v in dim_scores.items())
            dim_focus = (
                f"\n【维度评分（本轮聚焦）】\n"
                f"各维度：{dim_scores_str}\n"
                f"⚠️ 最弱维度：{weakest_cn}（{dim_scores[weakest_dim]:.2f}）\n"
                f"请优先改进 {weakest_cn} 相关的问题，这是本轮的聚焦重点。\n"
            )

        # P1-1: 构建章节聚焦指令
        section_focus = ""
        if focus_section:
            section_focus = (
                f"\n【本轮聚焦章节】{focus_section['title']}\n"
                f"请只修改该章节相关的问题，不要改动其他章节的内容。\n"
                f"其他章节如有跨章节引用需要调整，才可微调。\n"
            )
        elif is_full_review:
            section_focus = (
                f"\n【本轮为整体一致性修订】\n"
                f"请只做章节间的衔接、术语统一、冗余删减，不要大幅改动内容。\n"
            )

        prompt = (
            f"请根据对抗评审意见优化申请书。\n\n"
            f"【申请书文件】{proposal_path}\n"
            f"【项目类型】{project_type}\n"
            f"【质量标准】请读取 {standards_path}\n"
            f"【评审报告】{latest_critic}\n"
            f"{dim_focus}"
            f"{section_focus}"
            f"{lit_supplement}\n"
            f"请执行：\n"
            f"1. 读取申请书当前版本\n"
            f"2. 读取评审报告中的所有问题\n"
            f"3. 逐条解决每个问题（按严重程度优先）\n"
            f"4. 重点改进最弱维度相关的问题\n"
            f"5. 只修改聚焦章节（或整体衔接），保持其他内容不变（增量优化）\n"
            f"6. 优化后覆盖写入原文件：{proposal_path}\n"
            f"7. 同步更新方法学手册：{prop_dir}/04_proposal/methodology-manual.md\n"
            f"   （申请书重思路，方法学手册重细节：公式推导/参数表/技术路线图）\n"
            f"   ⚠️ 方法学手册也按章节组织，只更新与聚焦章节对应的细节部分。\n"
        )

        return self._run_hermes("writer", prompt, timeout)

    def _run_hermes(self, profile: str, prompt: str, timeout: int) -> Dict[str, Any]:
        """执行 hermes oneshot。"""
        # v6.6.3 修复：TRAE/IDE 注入的 Python 环境变量会让 hermes 内部 Python 启动崩溃，
        # 必须清理全部 Python 相关变量（不只是 PYTHONHOME/PYTHONPATH）
        env = clean_subprocess_env()

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
                # v6.7.1: 提高截断阈值，避免 critic 评分代码块被截断
                # critic 报告通常 10-25KB，50KB 可保留完整评分
                if len(output) > 50000:
                    output = output[:50000] + f"\n... (截断，共{len(output)}字符)"
                return {"success": True, "output": output, "elapsed_s": elapsed}
            return {
                "success": False, "output": result.stdout[:2000],
                "error": result.stderr[:500], "elapsed_s": elapsed,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "", "error": f"超时({timeout}s)", "elapsed_s": timeout}
        except Exception as e:
            return {"success": False, "output": "", "error": str(e), "elapsed_s": 0}

    def _wait_for_critic_report(
        self,
        report_path: Path,
        timeout: int = 30,
        stable_interval: float = 1.0,
    ) -> bool:
        """等待 critic 报告文件生成并稳定。

        hermes critic profile 通过 agent loop 异步写盘，Python 进程返回时
        文件可能尚未生成或仍在写入。轮询等待文件存在且大小稳定。

        Args:
            report_path: 期望的 critic 报告路径
            timeout: 最大等待秒数
            stable_interval: 连续两次大小不变的间隔秒数

        Returns:
            True 表示文件已生成且稳定；False 表示超时
        """
        import time
        deadline = time.time() + timeout
        last_size = -1
        stable_since = None

        while time.time() < deadline:
            if report_path.exists():
                try:
                    current_size = report_path.stat().st_size
                except Exception:
                    current_size = -1
                if current_size > 100 and current_size == last_size:
                    if stable_since is None:
                        stable_since = time.time()
                    elif time.time() - stable_since >= stable_interval:
                        return True
                else:
                    stable_since = None
                last_size = current_size
            time.sleep(0.5)

        return False

    def _extract_score(self, critic_result: Dict[str, Any]) -> float:
        """从 critic 输出中提取综合评分。"""
        output = critic_result.get("output", "")
        import re
        # 优先匹配 "综合评分：0.85" / "综合分 0.85"（v6.6.3：兼容 GLM-5.2 的简化输出）
        patterns = [
            r"综合评分[：:]\s*(0\.\d+)",
            r"综合分[：:]?\s*(0\.\d+)",
            r"overall[\s_]*score[：:\s]+(0\.\d+)",
            r"score[：:]\s*(0\.\d+)",
            r"评分[：:]\s*(0\.\d+)",
            r"(0\.\d+)\s*/\s*1(?:\.0+)?\b",  # 0.07 / 1 或 0.07 / 1.00
        ]
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return float(match.group(1))

        # 回退：如果有维度分数，取加权平均
        dims = self._extract_dimension_scores(critic_result)
        if dims:
            weights = {"innovation": 0.30, "feasibility": 0.25, "rigor": 0.25, "completeness": 0.20}
            total = sum(dims.get(k, 0) * w for k, w in weights.items())
            return round(total, 4)
        return 0.0

    # 维度中英文映射
    _DIM_MAP = {
        "创新性": "innovation", "创新": "innovation", "innovation": "innovation",
        "可行性": "feasibility", "feasibility": "feasibility",
        "严谨性": "rigor", "rigor": "rigor",
        "完整性": "completeness", "completeness": "completeness",
    }
    # 各维度短板阈值（低于此值视为短板）
    DIMENSION_FLOOR = {"innovation": 0.65, "feasibility": 0.65, "rigor": 0.65, "completeness": 0.60}

    def _extract_dimension_scores(self, critic_result: Dict[str, Any]) -> Dict[str, float]:
        """从 critic 输出中提取 4 维度分数（P0-2）。

        兼容 v6.6.3 GLM-5.2 输出格式：
        - `| 创新性（innovation） | 0.05 |` （markdown 表格 + 括号别名）
        - `创新性：0.85` / `创新性 0.85` / `创新性（innovation） 0.85`
        - 表格对齐：`| 创新性（innovation） | 0.05 | 主要短板 |`

        Returns:
            {innovation, feasibility, rigor, completeness}
        """
        output = critic_result.get("output", "")
        import re
        dims: Dict[str, float] = {}
        # 收集所有"维度名+分数"对（去重，每个维度只取第一个匹配）
        for cn_name, en_key in self._DIM_MAP.items():
            if en_key in dims:
                continue
            # 多种格式：行内/表格都支持
            patterns = [
                rf"\|\s*{cn_name}[（(]?{en_key}[）)]?\s*\|\s*(0\.\d+)",  # | 创新性（innovation） | 0.05 |
                rf"{cn_name}[（(]{en_key}[）)]\s*[：:|]?\s*(0\.\d+)",   # 创新性（innovation） 0.05
                rf"{cn_name}[：:]\s*(0\.\d+)",                            # 创新性：0.05
                rf"{cn_name}\s+(0\.\d+)",                                 # 创新性 0.05
            ]
            for pat in patterns:
                m = re.search(pat, output, re.IGNORECASE)
                if m:
                    dims[en_key] = float(m.group(1))
                    break
        return dims

    def _get_weakest_dimension(self, dims: Dict[str, float]) -> str:
        """找出最弱的维度（P0-2，供 writer 聚焦改进）。"""
        if not dims:
            return ""
        return min(dims, key=dims.get)

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

    # 所有模块必须全部通过才算达标（P1-3）
    REQUIRED_SECTIONS = ["rationale", "content", "method", "full_review"]

    def _check_done(self, proposal_id: str, threshold: Dict[str, Any]) -> Dict[str, Any]:
        """判定 proposal 是否达到输出标准（P1-3: 所有模块对抗胜利才算达标）。

        达标条件：3个章节（立项依据/研究内容/研究方案）+ 整体审查，共4个模块全部通过。
        每个模块"通过"= 分数达标 + 各维度无短板。
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"done": False, "reason": "状态不存在"}

        last_score = prop_state.get("last_score", 0.0)
        score_history = prop_state.get("score_history", [])
        section_passes = prop_state.get("section_passes", {})  # P1-3
        min_score = threshold.get("min_overall_score", DEFAULT_SCORE_THRESHOLD)
        rounds = prop_state.get("optimization_rounds", 0)

        # 条件1（P1-3）：所有模块对抗胜利
        passed_sections = [s for s in self.REQUIRED_SECTIONS if section_passes.get(s)]
        all_passed = len(passed_sections) == len(self.REQUIRED_SECTIONS)
        if all_passed:
            return {"done": True, "reason": f"全部{len(self.REQUIRED_SECTIONS)}个模块对抗胜利（{','.join(passed_sections)}）"}

        # 条件2：连续N轮无提升（逃生阀）
        no_improve_limit = DEFAULT_NO_IMPROVEMENT_LIMIT
        if len(score_history) >= no_improve_limit + 1:
            recent_scores = [h["score"] for h in score_history[-(no_improve_limit + 1):]]
            deltas = [recent_scores[i + 1] - recent_scores[i] for i in range(len(recent_scores) - 1)]
            if all(d < 0.02 for d in deltas):
                passed_str = f"（已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块）"
                return {"done": True, "reason": f"连续{no_improve_limit}轮无显著提升{passed_str}"}

        # 条件3：达到最大轮数（逃生阀）
        if rounds >= DEFAULT_MAX_ROUNDS:
            passed_str = f"（已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块）"
            return {"done": True, "reason": f"达到最大轮数{DEFAULT_MAX_ROUNDS}{passed_str}"}

        # 未达标：报告进度
        missing = [s for s in self.REQUIRED_SECTIONS if not section_passes.get(s)]
        return {
            "done": False,
            "reason": f"已通过{len(passed_sections)}/{len(self.REQUIRED_SECTIONS)}模块，待通过: {','.join(missing)}",
        }

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
        prop_state = self._get_proposal_state(proposal_id) or {}
        meta = {
            "proposal_id": proposal_id,
            "project_type": prop_state.get("project_type", "general"),
            "archived_at": now_utc(),
            "verdict": verdict,
            "approval_comment": approval_comment,
            "final_score": prop_state.get("last_score", 0),
            "optimization_rounds": prop_state.get("optimization_rounds", 0),
            "final_files": [str(f.relative_to(archived_dir)) for f in archived_dir.rglob("*.md")],
        }
        meta_path = archived_dir / "_archive-meta.json"
        save_json(meta_path, meta)

        # 纳入知识库（v6.6.0 漏洞4修复）
        kb_result = self._integrate_into_knowledge_base(proposal_id, archived_dir, meta)

        if _log:
            _log.info(f"归档 {proposal_id}: {len(meta['final_files'])} 个文件, 知识库: {kb_result.get('success', False)}")

        return {"success": True, "archived_dir": str(archived_dir), "meta": meta, "knowledge_base": kb_result}

    def _integrate_into_knowledge_base(
        self, proposal_id: str, archived_dir: Path, meta: Dict[str, Any]
    ) -> Dict[str, Any]:
        """将归档课题纳入知识库，供后续新课题引用。

        在 knowledge/wiki/projects/ 下创建课题索引，
        提取核心信息（科学问题/创新点/方法）供新课题发现和引用。
        """
        try:
            kb_dir = PROJECT_ROOT / "knowledge" / "wiki" / "projects"
            kb_dir.mkdir(parents=True, exist_ok=True)

            # 提取课题核心信息
            title = self._extract_proposal_title(archived_dir)
            core_questions = self._extract_core_questions(archived_dir)
            innovations = self._extract_innovations(archived_dir)

            # 创建知识库索引文件
            kb_entry = {
                "proposal_id": proposal_id,
                "title": title,
                "project_type": meta.get("project_type", "general"),
                "archived_at": meta.get("archived_at", ""),
                "final_score": meta.get("final_score", 0),
                "core_questions": core_questions,
                "innovations": innovations,
                "archived_path": str(archived_dir.relative_to(PROJECT_ROOT)),
            }
            kb_path = kb_dir / f"{proposal_id}.json"
            save_json(kb_path, kb_entry)

            if _log:
                _log.info(f"知识库索引: {kb_path.name}")

            return {"success": True, "kb_path": str(kb_path.relative_to(PROJECT_ROOT))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # cron 自动驱动（多 cron 分解架构，v6.5.2）
    # ------------------------------------------------------------------

    def match_proposals_with_brief(
        self,
        brief_path: Optional[str] = None,
        brief_content: Optional[str] = None,
    ) -> List[str]:
        """文献-课题匹配（v6.6.2）：判断当天简报与哪些 optimizing 课题相关。

        匹配逻辑：提取简报关键词（子方向/related标签），与每个课题的
        proposal-brief（标题+核心问题+创新点）做关键词重叠匹配。

        Args:
            brief_path: 简报文件路径；为None时自动找最新简报
            brief_content: 直接传入简报文本（优先于 brief_path）

        Returns:
            命中的 proposal_id 列表；无命中则返回全部 optimizing 课题（fallback）
        """
        import re

        # 1. 获取简报内容
        if brief_content is None:
            if brief_path is None:
                brief_dir = PROJECT_ROOT / "knowledge" / "wiki" / "reviews"
                briefs = sorted(brief_dir.glob("briefing-*.md"), reverse=True)
                if not briefs:
                    if _log:
                        _log.warning("文献匹配: 未找到简报，返回全部 optimizing 课题")
                    return [p["proposal_id"] for p in self.list_by_status("optimizing")]
                brief_path = str(briefs[0])
            try:
                brief_content = Path(brief_path).read_text(encoding="utf-8")
            except Exception:
                return [p["proposal_id"] for p in self.list_by_status("optimizing")]

        # 2. 提取简报关键词（子方向 + related 标签 + 正文高频词）
        brief_keywords = set()
        # related 标签
        for m in re.finditer(r'related:\s*\[([^\]]*)\]', brief_content):
            for kw in m.group(1).split(","):
                kw = kw.strip().strip('"').strip("'").strip()
                if len(kw) > 1:
                    brief_keywords.add(kw.lower())
        # 覆盖子方向行
        for m in re.finditer(r'覆盖子方向[：:]\s*(.+)', brief_content):
            for kw in re.split(r'[、，,;；]', m.group(1)):
                kw = kw.strip()
                if len(kw) > 1:
                    brief_keywords.add(kw.lower())
        # 正文 ## 标题
        for m in re.finditer(r'^##\s+(.+)', brief_content, re.MULTILINE):
            for kw in re.split(r'[\s/]', m.group(1)):
                kw = kw.strip()
                if len(kw) > 2:
                    brief_keywords.add(kw.lower())

        if not brief_keywords:
            if _log:
                _log.info("文献匹配: 简报无关键词，返回全部 optimizing 课题")
            return [p["proposal_id"] for p in self.list_by_status("optimizing")]

        if _log:
            _log.info(f"文献匹配: 简报关键词({len(brief_keywords)}): {', '.join(list(brief_keywords)[:10])}...")

        # 3. 逐个课题匹配
        matched = []
        for prop in self.list_by_status("optimizing"):
            pid = prop["proposal_id"]
            # 读取 proposal-brief
            prop_dir = self._find_proposal_dir(pid)
            if not prop_dir:
                continue
            brief_file = prop_dir / "00_proposal-brief.md"
            if not brief_file.exists():
                continue
            try:
                prop_content = brief_file.read_text(encoding="utf-8").lower()
            except Exception:
                continue

            # 计算关键词命中数
            hits = sum(1 for kw in brief_keywords if kw in prop_content)
            hit_ratio = hits / len(brief_keywords) if brief_keywords else 0

            if hits >= 2 or hit_ratio >= 0.1:  # 至少命中2个关键词 或 10%覆盖率
                matched.append(pid)
                if _log:
                    _log.info(f"文献匹配: {pid} 命中({hits}个关键词, {hit_ratio:.0%})")

        # fallback：如果无命中，返回全部（保证不空转）
        if not matched:
            if _log:
                _log.info("文献匹配: 无课题命中今日简报，fallback 返回全部 optimizing 课题")
            return [p["proposal_id"] for p in self.list_by_status("optimizing")]

        return matched

    def run_cron_sweep(
        self,
        stagger_seconds: int = DEFAULT_STAGGER_SECONDS,
        target_proposals: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """cron 扫描：对 optimizing 区的 proposal 做每日一轮全模块对抗。

        模式（v6.6.2）：文献驱动筛选 + 每课题每天4轮（3模块各1轮+整体审查1轮）。
        不做深度连续对抗（避免触顶模型限额），每天迭代一轮即可。
        容错设计：单个 proposal 失败不影响其他 proposal。
        错峰调度：课题间留间隔，避免模型同时阻塞。

        Args:
            stagger_seconds: 课题间错峰间隔（秒）
            target_proposals: 文献匹配命中的课题ID列表；为None则全量扫描
        """
        optimizing = self.list_by_status("optimizing")
        if not optimizing:
            if _log:
                _log.info("cron 扫描: optimizing 区为空")
            return {"success": True, "swept": 0, "results": [], "empty": True}

        # 文献驱动筛选：只优化命中的课题
        if target_proposals is not None:
            optimizing = [p for p in optimizing if p["proposal_id"] in target_proposals]
            if not optimizing:
                if _log:
                    _log.info("cron 扫描: 今日无文献匹配的课题，跳过优化")
                return {"success": True, "swept": 0, "results": [], "empty": True, "reason": "无文献匹配"}

        results = []
        success_count = 0
        fail_count = 0
        advanced_count = 0

        total = len(optimizing)
        for idx, prop in enumerate(optimizing):
            pid = prop["proposal_id"]
            if _log:
                _log.info(f"cron 扫描: 每日全模块对抗 {pid} ({idx + 1}/{total})")
            try:
                # 每课题4轮：立项依据→研究内容→研究方案→整体审查
                section_results = []
                for section_idx in range(len(PROPOSAL_SECTIONS) + 1):
                    result = self.optimize_cycle(pid)
                    if result.get("success"):
                        section_results.append(result)
                    else:
                        if _log:
                            _log.warning(f"cron 扫描: {pid} 第{section_idx+1}轮失败: {result.get('error','')[:80]}")
                        break
                    # 如果中途达标，提前结束
                    if result.get("done"):
                        break

                last_result = section_results[-1] if section_results else {"success": False, "error": "所有轮次失败"}

                results.append({"proposal_id": pid, "result": last_result, "rounds_done": len(section_results)})
                if last_result.get("success"):
                    success_count += 1
                    # 达标则自动移入待校验
                    if last_result.get("done"):
                        transition = self.transition(
                            pid, "pending_review", reason=last_result.get("reason", "达标")
                        )
                        advanced_count += 1
                        if _log:
                            _log.info(f"cron 扫描: {pid} 达标 → pending_review（{len(section_results)}轮）")
            except Exception as e:
                if _log:
                    _log.error(f"cron 扫描 {pid} 失败: {e}")
                results.append({"proposal_id": pid, "error": str(e)})
                fail_count += 1
                self._record_cron_failure(pid, str(e))

            # 错峰调度：非最后一个课题时，等待间隔再处理下一个
            if idx < total - 1 and stagger_seconds > 0:
                if _log:
                    _log.info(f"cron 扫描: 错峰等待 {stagger_seconds}s 后处理下一个课题")
                _time.sleep(stagger_seconds)

        return {
            "success": fail_count < success_count,
            "swept": len(results),
            "success_count": success_count,
            "fail_count": fail_count,
            "advanced_count": advanced_count,
            "results": results,
            "empty": False,
        }

    def _record_cron_failure(self, proposal_id: str, error: str) -> None:
        """记录 cron 失败到 proposal 状态（不中断循环）。"""
        try:
            with file_lock(f"proposal-{proposal_id}"):
                prop_state = self._get_proposal_state(proposal_id)
                if prop_state:
                    failures = prop_state.get("cron_failures", [])
                    failures.append({"at": now_utc(), "error": error[:200]})
                    # 只保留最近 5 次失败记录
                    prop_state["cron_failures"] = failures[-5:]
                    prop_state["updated_at"] = now_utc()
                    self._set_proposal_state(proposal_id, prop_state)
        except Exception:
            pass

    def run_health_check(self) -> Dict[str, Any]:
        """健康检查：扫描整个生命周期系统状态，检测异常并报警。

        检查项：
        1. optimizing 区空了 → 需要新课题或人工确认初稿
        2. proposal 卡在某个状态太久 → 需要关注
        3. pending_review 有 proposal → 提醒人工核验
        4. cron 失败累积 → 需要排查
        """
        state = self._load_state()
        alerts = []
        stats = {
            "total": len(state["proposals"]),
            "by_status": {},
            "stuck_proposals": [],
            "pending_human_action": [],
        }

        for stage in LIFECYCLE_STAGES:
            count = sum(
                1 for d in state["proposals"].values() if d.get("status") == stage
            )
            stats["by_status"][stage] = count

        # 检查1：optimizing 区为空但 drafts 有 proposal → 需要人工确认
        if stats["by_status"]["optimizing"] == 0 and stats["by_status"]["drafts"] > 0:
            drafts = self.list_by_status("drafts")
            alerts.append({
                "level": "info",
                "type": "awaiting_confirmation",
                "message": f"{len(drafts)} 个初稿等待人工确认思路后进入优化",
                "proposals": [p["proposal_id"] for p in drafts],
            })

        # 检查2：整个系统完全空转（没有任何活跃 proposal）
        active_count = sum(stats["by_status"][s] for s in ["drafts", "optimizing", "pending_review"])
        if active_count == 0:
            alerts.append({
                "level": "warning",
                "type": "system_idle",
                "message": "系统完全空转：没有任何活跃 proposal。需要启动新课题或从文献简报中发现方向。",
            })

        # 检查3：pending_review 有 proposal → 提醒人工核验
        if stats["by_status"]["pending_review"] > 0:
            pending = self.list_by_status("pending_review")
            alerts.append({
                "level": "info",
                "type": "pending_review",
                "message": f"{len(pending)} 个 proposal 等待人工核验",
                "proposals": [
                    {"id": p["proposal_id"], "score": p["last_score"],
                     "rounds": p["optimization_rounds"]}
                    for p in pending
                ],
            })

        # 检查4：proposal 卡在 optimizing 超过阈值
        for pid, data in state["proposals"].items():
            if data.get("status") == "optimizing":
                updated = data.get("updated_at", "")
                cron_failures = data.get("cron_failures", [])
                if len(cron_failures) >= 3:
                    alerts.append({
                        "level": "error",
                        "type": "repeated_cron_failure",
                        "message": f"{pid} 连续失败 {len(cron_failures)} 次，需要人工排查",
                        "proposal_id": pid,
                        "last_error": cron_failures[-1].get("error", ""),
                    })

        # 检查5：v6.7.6 负反馈告警（writer-critic 进入负反馈循环）
        for pid, data in state["proposals"].items():
            if data.get("status") == "optimizing" and data.get("negative_feedback_alert"):
                reasons = data.get("negative_feedback_reasons", [])
                alerts.append({
                    "level": "error",
                    "type": "negative_feedback",
                    "message": f"{pid} 触发负反馈告警，需人工介入后清除",
                    "proposal_id": pid,
                    "reasons": reasons,
                    "local_writer_score": data.get("monitor_history", [])[-1].get("local_writer_score") if data.get("monitor_history") else None,
                    "local_critic_score": data.get("monitor_history", [])[-1].get("local_critic_score") if data.get("monitor_history") else None,
                })

        return {
            "healthy": len([a for a in alerts if a["level"] == "error"]) == 0,
            "alerts": alerts,
            "stats": stats,
            "checked_at": now_utc(),
        }

    def clear_negative_feedback(self, proposal_id: str, reason: str = "") -> Dict[str, Any]:
        """清除指定 proposal 的负反馈告警，允许链路继续运转。

        人工确认问题已修复后调用，会重置 negative_feedback_alert 并记录清除历史。
        """
        prop_state = self._get_proposal_state(proposal_id)
        if not prop_state:
            return {"success": False, "error": f"proposal 未注册: {proposal_id}"}

        if not prop_state.get("negative_feedback_alert"):
            return {"success": True, "message": "无负反馈告警需清除", "proposal_id": proposal_id}

        cleared_entry = {
            "cleared_at": now_utc(),
            "previous_reasons": prop_state.get("negative_feedback_reasons", []),
            "reason": reason,
        }
        cleared_history = prop_state.get("negative_feedback_cleared", [])
        cleared_history.append(cleared_entry)

        prop_state["negative_feedback_alert"] = False
        prop_state["negative_feedback_reasons"] = []
        prop_state["negative_feedback_cleared"] = cleared_history[-10:]
        prop_state["updated_at"] = now_utc()
        self._set_proposal_state(proposal_id, prop_state)

        if _log:
            _log.info(f"清除负反馈告警: {proposal_id} ({reason})")

        return {"success": True, "proposal_id": proposal_id, "cleared_at": cleared_entry["cleared_at"]}

    def run_daily_orchestrator(self) -> Dict[str, Any]:
        """每日编排器：一个入口执行全部 cron 任务，各环节独立、容错。

        这是系统的心跳——每天执行一次，确保持续流转。
        即使某个环节失败，其他环节照常运行。

        执行顺序：
        1. 健康检查（先发现问题）
        2. 优化扫描（处理 optimizing 区）
        3. 再次健康检查（确认结果）
        """
        if _log:
            _log.info("=== 每日编排器启动 ===")

        # 1. 初始健康检查
        health_before = self.run_health_check()

        # 2. 文献-课题匹配（v6.6.2：只优化与当天文献相关的课题）
        target_proposals = self.match_proposals_with_brief()
        if _log:
            _log.info(f"每日编排: 文献匹配命中 {len(target_proposals)} 个课题")

        # 3. 优化扫描（文献驱动）
        sweep_result = self.run_cron_sweep(target_proposals=target_proposals)

        # 4. 最终健康检查
        health_after = self.run_health_check()

        # 汇总
        summary = {
            "orchestrated_at": now_utc(),
            "health_before": {
                "healthy": health_before["healthy"],
                "alert_count": len(health_before["alerts"]),
            },
            "sweep": {
                "swept": sweep_result.get("swept", 0),
                "success": sweep_result.get("success_count", 0),
                "failed": sweep_result.get("fail_count", 0),
                "advanced": sweep_result.get("advanced_count", 0),
                "empty": sweep_result.get("empty", False),
            },
            "health_after": {
                "healthy": health_after["healthy"],
                "alert_count": len(health_after["alerts"]),
                "alerts": health_after["alerts"],
            },
        }

        if _log:
            _log.info(
                f"每日编排器完成: "
                f"扫描{sweep_result.get('swept', 0)}个 "
                f"成功{sweep_result.get('success_count', 0)} "
                f"达标{sweep_result.get('advanced_count', 0)} "
                f"告警{len(health_after['alerts'])}个"
            )

        return summary

    def setup_optimization_cron(self, schedule: str = "0 9 * * *") -> Dict[str, Any]:
        """在 pipeline-runner 上配置每日编排 cron。

        采用单一编排器入口（run_daily_orchestrator），内部分解为
        健康检查 + 优化扫描 + 结果确认，各环节独立容错。

        Args:
            schedule: cron 表达式（默认每天 09:00）

        Returns:
            {success, message}
        """
        prompt = (
            "请执行每日提案系统编排：\n\n"
            "1. 运行 `python3 scripts/proposal_lifecycle.py --daily-orchestrate`\n"
            "2. 该命令会：\n"
            "   a. 健康检查（检测异常和空转）\n"
            "   b. 深度对抗（逐个聚焦优化 optimizing 区 proposal，每个连续多轮直到达标）\n"
            "   c. 达标的自动移入待校验\n"
            "   d. 最终健康检查（确认结果和告警）\n"
            "3. 输出编排摘要\n\n"
            "执行说明：\n"
            "- 每个课题会连续执行多轮深度对抗（章节轮转+整体审查）\n"
            "- 课题间有90秒错峰间隔，避免模型阻塞\n"
            "- 整个过程可能耗时1-4小时，请耐心等待\n\n"
            "容错说明：单个 proposal 失败不影响其他 proposal。\n"
            "如果 optimizing 区为空，输出健康检查结果和告警即可。\n"
            "如果有 pending_review 的 proposal，提醒人工核验。"
        )

        env = clean_subprocess_env()

        cmd = [
            "hermes", "--profile", "pipeline-runner", "cron", "create",
            schedule, prompt,
            "--name", "每日提案系统编排",
            "--deliver", "local",
            "--workdir", str(PROJECT_ROOT),
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, env=env,
            )
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"✓ 编排 cron 已创建: {schedule}",
                    "output": result.stdout.strip()[:300],
                }
            return {"success": False, "message": f"✗ {result.stderr.strip()[:200]}"}
        except Exception as e:
            return {"success": False, "message": f"✗ {e}"}


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
    parser.add_argument("--cron-sweep", action="store_true",
                        help="执行 cron 扫描（扫描 optimizing 区，各执行一轮优化）")
    parser.add_argument("--health-check", action="store_true",
                        help="执行健康检查（检测异常和空转）")
    parser.add_argument("--daily-orchestrate", action="store_true",
                        help="每日编排（健康检查+优化扫描+结果确认，容错）")
    parser.add_argument("--setup-cron", nargs="?", const="0 9 * * *", metavar="SCHEDULE",
                        help="配置每日编排 cron（默认 0 9 * * *）")
    # v6.7.6: 负反馈告警清除
    parser.add_argument("--clear-negative-feedback", metavar="ID",
                        help="清除指定 proposal 的负反馈告警（需人工确认后使用）")
    # v6.7.5: 小型化 cron 框架 CLI
    parser.add_argument("--worker-step", metavar="ID",
                        help="worker 入口：执行指定 proposal 的下一个 pending checkpoint job")
    parser.add_argument("--orchestrate", action="store_true",
                        help="手动触发每日编排（v2：生成 checkpoint + 确保 worker cron）")
    parser.add_argument("--repair", action="store_true",
                        help="手动触发修复扫描（处理 stuck/failed checkpoint 与缺失 worker）")
    parser.add_argument("--dry-run", action="store_true",
                        help="与 --repair 联用：只预览不修改")
    parser.add_argument("--setup-cron-v2", action="store_true",
                        help="安装 v2 cron 框架（orchestrate + repair + per-proposal workers）")
    parser.add_argument("--worker-schedule", default="", metavar="CRON",
                        help="强制统一 worker cron 调度表达式（默认留空，自动按 6 分钟间隔错开）")
    parser.add_argument("--teardown-cron-v2", action="store_true",
                        help="卸载所有 v2 lifecycle cron")
    args = parser.parse_args(argv)

    lc = ProposalLifecycle()

    # v6.7.5: 新 cron 框架命令使用 LifecycleCronController
    if any([args.worker_step, args.orchestrate, args.repair, args.setup_cron_v2, args.teardown_cron_v2]):
        # 延迟导入避免循环依赖
        from lifecycle_cron_framework import LifecycleCronController
        ctrl = LifecycleCronController()

        if args.worker_step:
            result = ctrl.execute_next_job(args.worker_step)
            print(f"worker {args.worker_step}: executed={result.get('executed')} "
                  f"success={result.get('success')} job={result.get('job_id', '-')}")
            if result.get('error'):
                print(f"  error: {result['error']}")
            return 0 if result.get('success') else 1

        if args.orchestrate:
            result = ctrl.run_orchestrator()
            print(f"=== 每日编排完成 (v2) ===")
            print(f"optimizing: {result.get('optimizing_count')} "
                  f"workers_created: {result.get('workers_created')} "
                  f"checkpoints_added: {result.get('checkpoints_added')}")
            print(f"health_after: {'🟢' if result['health_after']['healthy'] else '🔴'} "
                  f"({result['health_after']['alerts']} alerts)")
            return 0

        if args.repair:
            result = ctrl.run_repair(dry_run=args.dry_run)
            print(f"=== 修复扫描完成 (dry_run={result.get('dry_run')}) ===")
            for item in result.get("repaired", []):
                actions = item.get("actions", [])
                print(f"  {item['proposal_id']}: {actions if actions else 'ok'}")
            return 0

        if args.setup_cron_v2:
            result = ctrl.setup_cron_framework(worker_interval=args.worker_schedule)
            print("=== v2 cron 框架安装结果 ===")
            print(f"worker schedule: {args.worker_schedule}")
            print(f"removed_old: {result.get('removed_old', [])}")
            print(f"orchestrate: {result.get('orchestrate', {}).get('message')}")
            print(f"repair: {result.get('repair', {}).get('message')}")
            print(f"first_orchestrate: optimizing={result.get('first_orchestrate', {}).get('optimizing_count')}")
            return 0 if result.get("success") else 1

        if args.teardown_cron_v2:
            result = ctrl.teardown_cron_framework()
            print(f"=== 已卸载 v2 cron: {result.get('removed', [])} ===")
            return 0

    # 原有命令继续走 ProposalLifecycle

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

    if args.cron_sweep:
        result = lc.run_cron_sweep()
        print(f"=== cron 扫描完成: {result.get('swept', 0)} 个 proposal ===")
        if result.get("empty"):
            print("  optimizing 区为空")
        for r in result.get("results", []):
            pid = r["proposal_id"]
            if "error" in r:
                print(f"  ✗ {pid}: {r['error']}")
            else:
                res = r["result"]
                print(f"  {'✓' if res.get('done') else '◐'} {pid}: "
                      f"轮{res.get('round', '?')} score={res.get('score_after', 0):.2f} "
                      f"{'→ 待校验' if res.get('done') else '继续优化'}")
        return 0

    if args.health_check:
        result = lc.run_health_check()
        status_icon = "🟢" if result["healthy"] else "🔴"
        print(f"{status_icon} 健康检查: {'健康' if result['healthy'] else '有告警'}")
        print(f"告警数: {len(result['alerts'])}")
        for alert in result["alerts"]:
            level_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(alert["level"], "⚪")
            print(f"  {level_icon} [{alert['type']}] {alert['message']}")
            if "proposals" in alert:
                for p in alert["proposals"]:
                    if isinstance(p, dict):
                        print(f"      - {p.get('id', '?')} score={p.get('score', 0):.2f}")
                    else:
                        print(f"      - {p}")
        print(f"\n状态统计:")
        for stage, count in result["stats"]["by_status"].items():
            print(f"  {stage}: {count}")
        return 0 if result["healthy"] else 1

    if args.daily_orchestrate:
        result = lc.run_daily_orchestrator()
        print("=== 每日编排完成 ===")
        sweep = result.get("sweep", {})
        print(f"优化扫描: {sweep.get('swept', 0)}个 "
              f"(成功{sweep.get('success', 0)} 失败{sweep.get('failed', 0)} "
              f"达标{sweep.get('advanced', 0)})")
        if sweep.get("empty"):
            print("  optimizing 区为空")
        health = result.get("health_after", {})
        status = "🟢" if health.get("healthy") else "🔴"
        print(f"{status} 最终健康: {'健康' if health.get('healthy') else '有告警'} "
              f"({health.get('alert_count', 0)}个告警)")
        for alert in health.get("alerts", []):
            level_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(alert["level"], "⚪")
            print(f"  {level_icon} {alert['message']}")
        return 0

    if args.setup_cron is not None:
        result = lc.setup_optimization_cron(schedule=args.setup_cron)
        print(result.get("message", ""))
        return 0 if result.get("success") else 1

    if args.clear_negative_feedback:
        result = lc.clear_negative_feedback(args.clear_negative_feedback, reason="人工确认后清除")
        if result.get("success"):
            print(f"✓ 已清除 {args.clear_negative_feedback} 的负反馈告警")
            if result.get("cleared_at"):
                print(f"  清除时间: {result['cleared_at']}")
        else:
            print(f"✗ 清除失败: {result.get('error', '')}")
        return 0 if result.get("success") else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
