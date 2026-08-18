from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict

from common import now_utc, save_json, file_lock

import proposal_lifecycle as _pl

from proposal_lifecycle.constants import (
    _log,
    LIFECYCLE_STAGES,
    PROPOSALS_ROOT,
)

from paths import RAW_PROJECTS_DIR


class FeedbackArchiveMixin:
    # ------------------------------------------------------------------
    # 人工反馈处理
    # ------------------------------------------------------------------

    def submit_feedback(
        self,
        proposal_id: str,
        feedback_text: str,
        verdict: str = "major_revision",
        structured_feedback: Dict[str, Any] = None,
        session_id: str = "",
    ) -> Dict[str, Any]:
        """提交人工审核反馈。

        如果 verdict 是 approve，移入归档。
        否则派活给 writer 整理结构化意见，返回优化中。

        Args:
            proposal_id: 课题 ID
            feedback_text: 人工意见（自由文本）
            verdict: 审核结论（approve/minor_revision/major_revision/reject/redirect）
            structured_feedback: 外部已提供结构化意见
            session_id: 审核会话 ID（v6.8.17 反馈闭环——用于提取对话摘要）

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
            archive_result = self.archive_proposal(proposal_id, feedback_text, verdict)
            return {
                "success": True,
                "verdict": "approve",
                "archived": True,
                "transition": archive_result,
            }

        # 不通过 → writer 整理结构化意见 → 返回优化中
        if structured_feedback and isinstance(structured_feedback, dict):
            # v6.7.12: 外部已提供结构化意见（如对话式审核自动整理），直接落盘
            structured_path = prop_dir / "06_feedback" / f"feedback-{feedback_num}-structured.json"
            save_json(structured_path, structured_feedback)
            structured = structured_feedback
        else:
            structured = self._structure_feedback(
                proposal_id, prop_dir, feedback_text, verdict, feedback_num
            )

        # 更新反馈计数
        with file_lock(f"proposal-{proposal_id}"):
            prop_state = self._get_proposal_state(proposal_id)
            prop_state["human_feedback_count"] = feedback_num
            prop_state["updated_at"] = now_utc()
            # v6.8.17: 记录审核会话引用，供后续优化轮次注入
            if session_id:
                review_history = prop_state.setdefault("review_history", [])
                review_history.append({
                    "session_id": session_id,
                    "feedback_num": feedback_num,
                    "verdict": verdict,
                    "at": now_utc(),
                })
            self._set_proposal_state(proposal_id, prop_state)

        # v6.8.17: 将审核对话摘要追加到反馈文件
        if session_id:
            _append_session_summary_to_feedback(feedback_dir / f"feedback-{feedback_num}-raw.md", session_id)

        # 返回优化中
        transition_result = self.transition(
            proposal_id, "optimizing",
            reason=f"人工审核退回({verdict})，携带结构化意见"
            + (f"，会话={session_id}" if session_id else "")
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
            (_pl.PROJECT_ROOT / "memory" / "feedback-standards.json").relative_to(_pl.PROJECT_ROOT)
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

        # v6.9.26: writer 实测平均 350s+，旧 timeout=120 必超时——结构化
        # 文件永远写不出来，每次反馈提交白派一次 writer。
        result = self._run_hermes("writer", prompt, timeout=480)

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

    def archive_proposal(
        self,
        proposal_id: str,
        approval_comment: str,
        verdict: str,
    ) -> Dict[str, Any]:
        """归档 proposal：移入归档区 + 写入元信息 + 纳入知识库。"""
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

        v6.7.11 规范：
        1. 在 knowledge/raw/projects/{proposal_id}/ 保存完整课题源文件（raw 模块）。
        2. 在 knowledge/wiki/projects/ 下创建课题索引（wiki 模块，AI 整理）。
        提取核心信息（科学问题/创新点/方法）供新课题发现和引用。
        """
        try:
            # 1. 写入 raw/projects（源模块，完整归档）
            kb_project_dir = RAW_PROJECTS_DIR / proposal_id
            kb_project_dir.mkdir(parents=True, exist_ok=True)
            if kb_project_dir.exists() and any(kb_project_dir.iterdir()):
                # 已存在则先清空，避免旧文件残留
                for child in kb_project_dir.iterdir():
                    if child.is_dir():
                        shutil.rmtree(child)
                    else:
                        child.unlink()
            shutil.copytree(archived_dir, kb_project_dir, dirs_exist_ok=True)

            # 写入结构说明
            readme_path = kb_project_dir / "_README.md"
            readme_path.write_text(
                f"# {proposal_id}\n\n"
                f"本目录为该课题的归档源文件，属于知识库 **raw（源模块）**。\n\n"
                f"- 归档时间：{meta.get('archived_at', '')}\n"
                f"- 最终评分：{meta.get('final_score', 0)}\n"
                f"- 优化轮次：{meta.get('optimization_rounds', 0)}\n"
                f"- 原始归档路径：`{str(archived_dir.relative_to(_pl.PROJECT_ROOT))}`\n\n"
                f"> 注意：raw 模块原则上只读，如需修改请通过前端/对话由 agent 协助处理。\n",
                encoding="utf-8",
            )

            # 2. 写入 wiki/projects（智能整理模块，索引卡片）
            kb_dir = _pl.PROJECT_ROOT / "knowledge" / "wiki" / "projects"
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
                "optimization_rounds": meta.get("optimization_rounds", 0),
                "core_questions": core_questions,
                "innovations": innovations,
                "archived_path": str(archived_dir.relative_to(_pl.PROJECT_ROOT)),
                "kb_project_path": str(kb_project_dir.relative_to(_pl.PROJECT_ROOT)),
            }
            kb_path = kb_dir / f"{proposal_id}.json"
            save_json(kb_path, kb_entry)

            if _log:
                _log.info(f"知识库索引: {kb_path.name}, raw 归档: {kb_project_dir.name}")

            return {
                "success": True,
                "kb_path": str(kb_path.relative_to(_pl.PROJECT_ROOT)),
                "kb_project_path": str(kb_project_dir.relative_to(_pl.PROJECT_ROOT)),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# v6.8.17: 审核对话摘要提取（模块级函数）
# ---------------------------------------------------------------------------

def _append_session_summary_to_feedback(feedback_path: Path, session_id: str) -> None:
    """将审核会话的用户消息摘要追加到反馈文件。

    不调用 LLM——直接提取审核对话中用户提出的问题和意见，
    作为结构化反馈的补充上下文。
    """
    try:
        import session_manager as sm
        messages, _state = sm.load_session(session_id)

        # 提取用户消息（跳过初始审核上下文）
        user_messages = []
        for m in messages:
            if m.get("role") == "user" and m.get("mode") == "review":
                content = m.get("content", "").strip()
                if content and len(content) > 5:
                    user_messages.append(content)

        if not user_messages:
            return

        # 追加到反馈文件
        summary_lines = [
            "\n\n---\n\n",
            "## 审核对话摘要（自动提取）\n\n",
            f"会话 ID: `{session_id}`\n\n",
        ]
        for i, msg in enumerate(user_messages[-10:], 1):
            summary_lines.append(f"**用户意见 {i}**: {msg[:500]}\n\n")

        with open(feedback_path, "a", encoding="utf-8") as f:
            f.writelines(summary_lines)
    except Exception:
        pass


def load_review_feedback_for_optimization(prop_state: Dict[str, Any]) -> str:
    """v6.8.17: 为优化轮次加载历史人工审核反馈。

    从 06_feedback/ 中提取之前的审核意见，供 critic/writer prompt
    注入，避免重蹈覆辙。
    """
    # v6.9.26: 旧实现以 review_history 为门闩，但该字段仅在带 session_id
    # 的 Web 审核提交时写入——CLI/脚本提交（无 session）不写，导致退回
    # 反馈永远不注入 critic/writer prompt（闭环断裂）。函数体实际只依赖
    # feedback_count 与 raw 文件，门闩改为 feedback_count。
    feedback_count = prop_state.get("human_feedback_count", 0)
    if feedback_count == 0:
        return ""

    lines = [
        "\n\n【历史人工审核反馈（请避免同类问题）】\n",
    ]

    # 读取最近一次反馈文件
    proposal_id = prop_state.get("proposal_id", "")
    from proposal_lifecycle.constants import PROPOSALS_ROOT
    for stage in ["optimizing"]:
        feedback_dir = PROPOSALS_ROOT / stage / proposal_id / "06_feedback"
        if not feedback_dir.exists():
            continue
        raw_file = feedback_dir / f"feedback-{feedback_count}-raw.md"
        if raw_file.exists():
            text = raw_file.read_text(encoding="utf-8")
            # 提取审核对话摘要部分
            if "## 审核对话摘要" in text:
                summary_part = text[text.find("## 审核对话摘要"):]
                lines.append(summary_part[:2000])
                break
            else:
                # 使用完整反馈（截断）
                lines.append(text[:1500])
                break

    # v6.9.26: 旧判断 len(lines) > 2 永假（lines 最多含 header+1 个反馈
    # 共 2 个元素），函数自引入起恒返回空串——"审核反馈闭环"从未生效。
    if len(lines) > 1:
        return "\n".join(lines)
    return ""
