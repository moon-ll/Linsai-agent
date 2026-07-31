from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from common import now_utc, safe_filename

import proposal_lifecycle as _pl

from proposal_lifecycle.constants import (
    _log,
    LIFECYCLE_STAGES,
    PROJECT_TYPES,
    PROPOSALS_ROOT,
)


class RegistrationMixin:
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

        # 创建标准目录结构（v6.8.0: 5 模块 + 研究设想 + 方法学手册 + 阅读笔记）
        standard_dirs = [
            "01_direction",
            "02_literature/targeted-research",
            "02_topic",
            "03_question",
            "03_method",
            "04_proposal",
            "05_review",
        ]
        for d in standard_dirs:
            (target_dir / d).mkdir(parents=True, exist_ok=True)

        # v6.8.0: 初始化核心产物占位
        (target_dir / "00_proposal-brief.md").write_text(
            f"# {proposal_id}\n\n> 项目类型：{project_type}\n\n## 研究设想\n\n待补充。\n",
            encoding="utf-8",
        )
        (target_dir / "03_method" / "method-manual.md").write_text(
            "# 方法学手册\n\n待课题进入优化环节后，根据申请书研究方案补充具体方法细节。\n",
            encoding="utf-8",
        )
        (target_dir / "02_literature" / "reading-notes.md").write_text(
            "# 文献阅读笔记\n\n记录课题优化过程中补充阅读的文献。\n",
            encoding="utf-8",
        )

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
            # v6.7.6: 对抗评审奖惩与监察相关字段
            "monitor_history": [],
            "negative_feedback_alert": False,
            "negative_feedback_reasons": [],
            "negative_feedback_cleared": [],
            "worker_minute": None,
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
            "path": str(target_dir.relative_to(_pl.PROJECT_ROOT)),
        }

    def register_from_idea(
        self,
        idea: Dict[str, Any],
        project_type: str = "general",
    ) -> Dict[str, Any]:
        """从研究设想注册新 proposal（进入 drafts）。

        v6.7.7: 输入端自动/手动生成的研究设想，经对比判定为新课题后调用。
        """
        import re
        from common import safe_filename

        title = idea.get("title", "")
        # 生成 proposal_id：从标题提取 safe name
        name = safe_filename(title)[:40].strip("-").lower()
        name = re.sub(r"[^a-z0-9-]+", "-", name).strip("-")
        if not name:
            name = "new-idea"

        proposal_id = self.generate_proposal_id(name=name, project_type=project_type)
        reg = self.register(
            proposal_id=proposal_id,
            project_type=project_type,
            source="auto_idea",
            source_detail=f"来自研究设想生成: {title}",
        )
        if not reg.get("success"):
            return reg

        self.enrich_from_idea(proposal_id, idea)
        return {
            "success": True,
            "proposal_id": proposal_id,
            "status": "drafts",
            "action": "new",
        }

    def enrich_from_idea(
        self,
        proposal_id: str,
        idea: Dict[str, Any],
        duplicate_threshold: float = 0.70,
    ) -> Dict[str, Any]:
        """将研究设想追加到现有 proposal，追加前做句子级去重。

        v6.7.7: 保证每个课题任何时刻都具备独立完整结构，且避免过度冗余。
        """
        prop_dir = self._find_proposal_dir(proposal_id)
        if not prop_dir:
            return {"success": False, "error": "proposal 目录不存在"}

        def _tokenize(text: str) -> set:
            words = set(re.findall(r"[a-zA-Z]{3,}", text.lower()))
            words.update(re.findall(r"[\u4e00-\u9fff]{2,8}", text))
            return words

        def _sentence_similarity(paragraph: str, existing_text: str) -> float:
            if not existing_text:
                return 0.0
            sentences = [s.strip() for s in re.split(r"[。\n]", existing_text) if len(s.strip()) > 10]
            if not sentences:
                return 0.0
            set_p = _tokenize(paragraph)
            return max(
                len(set_p & _tokenize(s)) / len(set_p | _tokenize(s))
                if set_p or _tokenize(s) else 0.0
                for s in sentences
            )

        def _deduplicate_append(path: Path, new_section: str) -> bool:
            existing = ""
            if path.exists():
                existing = path.read_text(encoding="utf-8")
            paragraphs = [p for p in new_section.split("\n\n") if p.strip()]
            unique = []
            for p in paragraphs:
                if len(p.strip()) < 20:
                    continue
                if _sentence_similarity(p, existing) < duplicate_threshold:
                    unique.append(p)
            if not unique:
                return False
            new_content = "\n\n".join(unique) + "\n"
            with path.open("a", encoding="utf-8") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write("\n" + new_content)
            return True

        date_str = now_utc()[:10]

        # 方向校准
        direction_section = f"""## 周末输入补充（{date_str}）

**来源**：研究设想生成
**可靠性**：{idea.get('reliability', 'derived')}

### 研究背景与动机
{idea.get('background', '')}

### 现存研究空白
{idea.get('gap', '')}
"""
        _deduplicate_append(prop_dir / "01_direction" / "direction-calibration.md", direction_section)

        # 缺口分析
        gap_section = f"""## 周末输入补充（{date_str}）

**拟解决空白**：{idea.get('gap', '')}

**相关创新方向**：{', '.join(idea.get('innovations', []))}
"""
        _deduplicate_append(prop_dir / "02_topic" / "gap-report.md", gap_section)

        # 科学问题框架
        question_items = "\n".join(f"- {q}" for q in idea.get("content", []))
        question_section = f"""## 周末输入补充（{date_str}）

{question_items}
"""
        _deduplicate_append(prop_dir / "03_question" / "question-framework.md", question_section)

        # 申请书草稿
        sources_str = "\n".join(
            f"- [{s.get('source_type', 'unknown')}] {s.get('title', '')}"
            for s in idea.get("sources", [])
        )
        proposal_section = f"""## 周末输入补充（{date_str}）

### 拟开展研究内容
{chr(10).join(f"- {c}" for c in idea.get('content', []))}

### 拟采用技术路线
{idea.get('approach', '')}

### 创新点
{chr(10).join(f"- {inv}" for inv in idea.get('innovations', []))}

### 来源
{sources_str}
"""
        _deduplicate_append(prop_dir / "04_proposal" / "proposal-draft.md", proposal_section)

        # v6.8.0: 确保按新 5 模块结构拆分
        try:
            from proposal_sections import ProposalSections
            ps = ProposalSections(prop_dir / "04_proposal")
            ps.ensure_split()
        except Exception:
            pass

        # 更新 brief
        try:
            self.update_proposal_brief(proposal_id)
        except Exception:
            pass

        return {"success": True, "proposal_id": proposal_id, "action": "merge"}
