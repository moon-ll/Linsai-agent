from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from common import now_utc

import proposal_lifecycle as _pl

from proposal_lifecycle.constants import _log


class MetadataMixin:
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

        return {"success": True, "path": str(brief_path.relative_to(_pl.PROJECT_ROOT))}

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
