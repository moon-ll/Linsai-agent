#!/usr/bin/env python3
"""web_routes_pipeline.py — 研究管线路由 Mixin。

提供 PipelineRoutesMixin，封装研究管线六阶段状态机及各阶段子模块的 HTTP 路由（54 条）。
整体设计遵循 web_routes_research.py 的独立分派器模式（_dispatch_pipeline_routes），
在 do_GET/do_POST/do_PUT 中优先于统一路由表调用。

覆盖的子模块与路由前缀：
    - Agent 团队 /api/pipeline/agents/...                (10 条，无 proposal_id，团队全局)
    - 管线编排   /api/pipeline/{proposal_id}/...        (10 条)
    - 缺口分析   /api/pipeline/{proposal_id}/gaps/...    (3 条)
    - 课题生成   /api/pipeline/{proposal_id}/topics/...  (6 条)
    - 问题构建   /api/pipeline/{proposal_id}/questions/...(5 条)
    - 申请书撰写 /api/pipeline/{proposal_id}/proposal/...(7 条)
    - 自检优化   /api/pipeline/{proposal_id}/inspection/...(4 条)
    - 引文管理   /api/pipeline/{proposal_id}/citations/...(4 条)
    - 方法学手册 /api/pipeline/{proposal_id}/methodology/...(5 条)

路由表 _PIPELINE_ROUTES 使用预编译正则，handler 签名为
    GET/DELETE  → (self, path, parsed, match)
    POST/PUT    → (self, path, parsed, body, match)
其中 match 为 re.match 返回的 Match 对象，通过 match.group(N) 提取路径参数。

安全要点：
    - proposal_id 经 _validate_proposal_id 校验（防路径遍历）
    - 所有文件操作经 _safe_join 约束在 proposal 目录内
    - 状态修改操作使用 file_lock 跨进程锁
    - 管线子模块懒加载，容忍模块缺失（返回 501 提示）

仅使用 Python 标准库。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, file_lock, safe_filename
import web_base
from web_base import _log, _safe_join

__all__ = ["PipelineRoutesMixin"]

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 申请书预期章节（用于进度计算）
_EXPECTED_SECTIONS: List[str] = [
    "立项依据", "研究内容", "研究方案", "特色与创新", "研究基础",
]

# proposal 根目录名（位于项目根下）
_PROPOSALS_DIR_NAME = "proposals"


def _proposals_root() -> Path:
    """获取 proposals 根目录（通过 web_base._PROJECT_ROOT 动态引用，支持 --root 覆盖）。"""
    return web_base._PROJECT_ROOT / _PROPOSALS_DIR_NAME


# ---------------------------------------------------------------------------
# 路由表（更具体的路由放在前面，避免被通用模式抢先匹配）
# ---------------------------------------------------------------------------
_PIPELINE_ROUTES_RAW = [
    # ---- GET ----
    # 静态路由（无 proposal_id）放最前
    ("GET", r"^/api/pipeline/stages$", "_pl_get_stages"),
    # Agent 团队管理（无 proposal_id，团队全局；必须在 {proposal_id} 路由之前）
    ("GET", r"^/api/pipeline/agents$", "_pl_get_agents"),
    ("GET", r"^/api/pipeline/agents/overview$", "_pl_get_agents_overview"),
    ("GET", r"^/api/pipeline/agents/performance$", "_pl_get_agents_performance"),
    ("GET", r"^/api/pipeline/agents/([^/]+)$", "_pl_get_agent"),
    # 管线编排
    ("GET", r"^/api/pipeline/([^/]+)/state$", "_pl_get_state"),
    ("GET", r"^/api/pipeline/([^/]+)/progress$", "_pl_get_progress"),
    ("GET", r"^/api/pipeline/([^/]+)/timeline$", "_pl_get_timeline"),
    ("GET", r"^/api/pipeline/([^/]+)/artifacts$", "_pl_get_artifacts"),
    # 缺口分析
    ("GET", r"^/api/pipeline/([^/]+)/gaps$", "_pl_get_gaps"),
    ("GET", r"^/api/pipeline/([^/]+)/gaps/export$", "_pl_get_gaps_export"),
    # 课题生成（export 必须在 {topic_id} 之前）
    ("GET", r"^/api/pipeline/([^/]+)/topics$", "_pl_get_topics"),
    ("GET", r"^/api/pipeline/([^/]+)/topics/export$", "_pl_get_topics_export"),
    ("GET", r"^/api/pipeline/([^/]+)/topics/([^/]+)$", "_pl_get_topic"),
    # 问题构建（export 必须在 {question_id} 之前）
    ("GET", r"^/api/pipeline/([^/]+)/questions$", "_pl_get_questions"),
    ("GET", r"^/api/pipeline/([^/]+)/questions/export$", "_pl_get_questions_export"),
    ("GET", r"^/api/pipeline/([^/]+)/questions/([^/]+)$", "_pl_get_question"),
    # 申请书（sections 列表/export/progress 必须在 {section_name} 之前）
    ("GET", r"^/api/pipeline/([^/]+)/proposal/sections$", "_pl_get_sections"),
    ("GET", r"^/api/pipeline/([^/]+)/proposal/export$", "_pl_get_proposal_export"),
    ("GET", r"^/api/pipeline/([^/]+)/proposal/progress$", "_pl_get_proposal_progress"),
    ("GET", r"^/api/pipeline/([^/]+)/proposal/sections/([^/]+)$", "_pl_get_section"),
    # 自检优化
    ("GET", r"^/api/pipeline/([^/]+)/inspection/report$", "_pl_get_inspection_report"),
    ("GET", r"^/api/pipeline/([^/]+)/inspection/history$", "_pl_get_inspection_history"),
    ("GET", r"^/api/pipeline/([^/]+)/inspection/export$", "_pl_get_inspection_export"),
    # 引文管理（export/stats 是精确路径，但统一放前以保持风格一致）
    ("GET", r"^/api/pipeline/([^/]+)/citations$", "_pl_get_citations"),
    ("GET", r"^/api/pipeline/([^/]+)/citations/export$", "_pl_get_citations_export"),
    ("GET", r"^/api/pipeline/([^/]+)/citations/stats$", "_pl_get_citations_stats"),
    # 方法学手册（export/stats 是精确路径，放前以保持风格一致）
    ("GET", r"^/api/pipeline/([^/]+)/methodology$", "_pl_get_methodology"),
    ("GET", r"^/api/pipeline/([^/]+)/methodology/export$", "_pl_get_methodology_export"),
    ("GET", r"^/api/pipeline/([^/]+)/methodology/stats$", "_pl_get_methodology_stats"),

    # ---- POST ----
    # Agent 团队管理（无 proposal_id，团队全局；必须在 {proposal_id} 路由之前）
    ("POST", r"^/api/pipeline/agents/add$", "_pl_post_agent_add"),
    ("POST", r"^/api/pipeline/agents/([^/]+)/status$", "_pl_post_agent_status"),
    ("POST", r"^/api/pipeline/agents/([^/]+)/assign$", "_pl_post_agent_assign"),
    ("POST", r"^/api/pipeline/agents/([^/]+)/complete$", "_pl_post_agent_complete"),
    ("POST", r"^/api/pipeline/agents/([^/]+)/upgrade$", "_pl_post_agent_upgrade"),
    ("POST", r"^/api/pipeline/agents/([^/]+)/activate$", "_pl_post_agent_activate"),
    # 管线编排
    ("POST", r"^/api/pipeline/([^/]+)/advance$", "_pl_post_advance"),
    ("POST", r"^/api/pipeline/([^/]+)/gate/([^/]+)$", "_pl_post_gate"),
    ("POST", r"^/api/pipeline/([^/]+)/rollback$", "_pl_post_rollback"),
    ("POST", r"^/api/pipeline/([^/]+)/pause$", "_pl_post_pause"),
    ("POST", r"^/api/pipeline/([^/]+)/resume$", "_pl_post_resume"),
    # 缺口分析
    ("POST", r"^/api/pipeline/([^/]+)/gaps/analyze$", "_pl_post_gaps_analyze"),
    # 课题生成（generate 必须在 {topic_id}/action 之前）
    ("POST", r"^/api/pipeline/([^/]+)/topics/generate$", "_pl_post_topics_generate"),
    ("POST", r"^/api/pipeline/([^/]+)/topics/([^/]+)/select$", "_pl_post_topic_select"),
    ("POST", r"^/api/pipeline/([^/]+)/topics/([^/]+)/refine$", "_pl_post_topic_refine"),
    # 问题构建
    ("POST", r"^/api/pipeline/([^/]+)/questions/construct$", "_pl_post_questions_construct"),
    ("POST", r"^/api/pipeline/([^/]+)/questions/([^/]+)/refine$", "_pl_post_question_refine"),
    # 申请书
    ("POST", r"^/api/pipeline/([^/]+)/proposal/write$", "_pl_post_proposal_write"),
    ("POST", r"^/api/pipeline/([^/]+)/proposal/sections/([^/]+)$", "_pl_post_section"),
    # 自检优化
    ("POST", r"^/api/pipeline/([^/]+)/inspection/run$", "_pl_post_inspection_run"),
    # 引文管理
    ("POST", r"^/api/pipeline/([^/]+)/citations$", "_pl_post_citation"),
    # 方法学手册
    ("POST", r"^/api/pipeline/([^/]+)/methodology/generate$", "_pl_post_methodology_generate"),

    # ---- PUT ----
    ("PUT", r"^/api/pipeline/([^/]+)/proposal/sections/([^/]+)$", "_pl_put_section"),
    ("PUT", r"^/api/pipeline/([^/]+)/methodology/([^/]+)$", "_pl_put_methodology_update"),

    # ---- Hermes 驱动管线（v6.4.1）----
    ("GET", r"^/api/pipeline/hermes/proposals$", "_pl_hermes_list_importable"),
    ("GET", r"^/api/pipeline/hermes/([^/]+)/status$", "_pl_hermes_status"),
    ("GET", r"^/api/pipeline/hermes/([^/]+)/check/([^/]+)$", "_pl_hermes_check_stage"),
    ("POST", r"^/api/pipeline/hermes/([^/]+)/import$", "_pl_hermes_import"),
    ("POST", r"^/api/pipeline/hermes/([^/]+)/dispatch/([^/]+)$", "_pl_hermes_dispatch"),
    ("POST", r"^/api/pipeline/hermes/([^/]+)/run$", "_pl_hermes_run"),
    ("POST", r"^/api/pipeline/hermes/([^/]+)/cron$", "_pl_hermes_setup_cron"),
    # 针对性检索（撰写时按需检索）
    ("GET", r"^/api/pipeline/hermes/([^/]+)/research$", "_pl_hermes_list_research"),
    ("POST", r"^/api/pipeline/hermes/([^/]+)/research$", "_pl_hermes_research"),
]

# 预编译正则
_PIPELINE_ROUTES = [(m, re.compile(p), h) for m, p, h in _PIPELINE_ROUTES_RAW]


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------
class PipelineRoutesMixin:
    """研究管线路由 Mixin。

    提供 54 条 HTTP 路由，覆盖研究管线六阶段状态机编排、Agent 团队管理、
    缺口分析、课题生成、科学问题构建、申请书撰写、自检优化、引文管理、方法学手册。

    self 在运行时是最终 RequestHandler 实例（继承 BaseRequestHandler），
    可直接调用 _send_json / _read_json_body 等方法。
    """

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    def _validate_proposal_id(self, proposal_id: str) -> str:
        """校验 proposal_id 安全性，防止路径遍历。

        proposal_id 必须非空，只含字母/数字/横杠/下划线/中文/点号（非连续点）。
        返回校验后的 proposal_id，不合法则抛 ValueError。
        """
        if not proposal_id or not isinstance(proposal_id, str):
            raise ValueError("proposal_id 不能为空")
        if "/" in proposal_id or "\\" in proposal_id or ".." in proposal_id:
            raise ValueError(f"非法 proposal_id: {proposal_id}")
        if not re.match(r'^[\w\u4e00-\u9fff.\-]+$', proposal_id):
            raise ValueError(f"非法 proposal_id 字符: {proposal_id}")
        return proposal_id

    def _pipeline_proposal_dir(self, proposal_id: str) -> Path:
        """获取 proposal 目录绝对路径（校验后拼接，确保在 proposals 根目录内）。"""
        self._validate_proposal_id(proposal_id)
        root = _proposals_root()
        root.mkdir(parents=True, exist_ok=True)
        # 使用 _safe_join 防止路径遍历（二次防护）
        return _safe_join(root, proposal_id)

    def _pipeline_read_dir(self, proposal_id: str) -> Path:
        """获取用于读取的 proposal 目录。

        优先使用 pipeline 原生 proposals/ 目录；若该目录不存在或为空，
        则回退到 lifecycle 管理的 research_proposals/{status}/{proposal_id} 目录，
        使用户能在 pipeline 面板查看已通过 lifecycle 生成的课题内容。
        """
        self._validate_proposal_id(proposal_id)
        native = self._pipeline_proposal_dir(proposal_id)
        if native.exists() and any(native.iterdir()):
            return native

        lc_root = web_base._PROJECT_ROOT / "research_proposals"
        # 优先根据 lifecycle 状态定位
        lifecycle_state_path = lc_root / "_lifecycle.json"
        if lifecycle_state_path.exists():
            try:
                lc_state = json.loads(lifecycle_state_path.read_text(encoding="utf-8"))
                prop = lc_state.get("proposals", {}).get(proposal_id, {})
                status = prop.get("status")
                if status:
                    candidate = lc_root / status / proposal_id
                    if candidate.exists():
                        return candidate
            except Exception:
                pass

        # 兜底：扫描各阶段目录
        if lc_root.exists():
            for stage in ("drafts", "optimizing", "pending_review", "archived", "_incoming"):
                candidate = lc_root / stage / proposal_id
                if candidate.exists():
                    return candidate

        return native

    def _pipeline_ensure_dirs(self, proposal_id: str) -> Path:
        """确保 proposal 目录结构存在，返回 proposal 根目录。"""
        pdir = self._pipeline_proposal_dir(proposal_id)
        for sub in ("00_pipeline", "01_direction", "02_topic", "03_question",
                     "04_proposal", "05_review"):
            (pdir / sub).mkdir(parents=True, exist_ok=True)
        # v6.7.8: 若当前 proposals/ 下无实质内容，从 lifecycle 目录自动同步，
        # 使 pipeline 面板能查看已生成的课题内容
        self._pipeline_sync_from_lifecycle_if_empty(proposal_id, pdir)
        return pdir

    def _pipeline_sync_from_lifecycle_if_empty(self, proposal_id: str, pdir: Path) -> None:
        """当 proposals/ 目录为空时，从 research_proposals 对应状态目录同步内容。"""
        proposal_file = pdir / "04_proposal" / "sections.json"
        draft_file = pdir / "04_proposal" / "proposal-draft.md"
        if proposal_file.exists() or draft_file.exists():
            return

        source_dir = self._pipeline_read_dir(proposal_id)
        if source_dir == pdir or not source_dir.exists():
            return

        try:
            import shutil
            for sub in ("00_pipeline", "01_direction", "02_topic", "03_question",
                        "04_proposal", "05_review", "06_feedback"):
                src = source_dir / sub
                dst = pdir / sub
                if src.exists():
                    if not dst.exists():
                        shutil.copytree(src, dst)
                    else:
                        for f in src.iterdir():
                            if f.is_file() and not (dst / f.name).exists():
                                shutil.copy2(f, dst / f.name)
            if _log:
                _log.info(f"[pipeline] 已从 lifecycle 同步 {proposal_id}: {source_dir}")
        except Exception as e:
            if _log:
                _log.warning(f"[pipeline] 同步 {proposal_id} 失败: {e}")

    def _pipeline_load_module(self, name: str):
        """懒加载管线子模块，返回模块对象或 None。

        使用 importlib 动态加载，容忍模块缺失或导入失败。
        """
        try:
            import importlib
            mod_path = _SCRIPT_DIR / f"{name}.py"
            if not mod_path.exists():
                return None
            spec = importlib.util.spec_from_file_location(name, mod_path)
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        except Exception as e:
            if _log:
                _log.debug("懒加载模块 %s 失败: %s", name, e)
            return None

    def _pipeline_get_manager(self, proposal_id: str):
        """获取或创建 PipelineManager 实例。

        Returns:
            PipelineManager 实例；模块不可用时返回 None。
        """
        pdir = self._pipeline_ensure_dirs(proposal_id)
        mod = self._pipeline_load_module("pipeline_orchestrator")
        if mod is None:
            return None
        return mod.PipelineManager(proposal_id, pdir)

    def _pipeline_get_gap_analyzer(self, proposal_id: str, directions=None):
        """获取 GapAnalyzer 实例。"""
        pdir = self._pipeline_ensure_dirs(proposal_id)
        mod = self._pipeline_load_module("gap_analyzer")
        if mod is None:
            return None
        return mod.GapAnalyzer(pdir, research_directions=directions or [])

    def _pipeline_get_topic_generator(self, proposal_id: str):
        """获取 TopicGenerator 实例。"""
        pdir = self._pipeline_ensure_dirs(proposal_id)
        mod = self._pipeline_load_module("topic_generator")
        if mod is None:
            return None
        return mod.TopicGenerator(pdir)

    def _pipeline_get_question_architect(self, proposal_id: str):
        """获取 QuestionArchitect 实例。"""
        pdir = self._pipeline_ensure_dirs(proposal_id)
        mod = self._pipeline_load_module("question_architect")
        if mod is None:
            return None
        return mod.QuestionArchitect(pdir)

    def _pipeline_get_inspector(self, proposal_id: str):
        """获取 ProposalInspector 实例。"""
        pdir = self._pipeline_ensure_dirs(proposal_id)
        mod = self._pipeline_load_module("proposal_inspector")
        if mod is None:
            return None
        return mod.ProposalInspector(pdir)

    def _pipeline_get_citation_manager(self, proposal_id: str):
        """获取 CitationManager 实例。"""
        pdir = self._pipeline_ensure_dirs(proposal_id)
        mod = self._pipeline_load_module("citation_manager")
        if mod is None:
            return None
        return mod.CitationManager(pdir)

    def _pipeline_sections_path(self, proposal_id: str) -> Path:
        """获取申请书章节存储文件路径。"""
        pdir = self._pipeline_ensure_dirs(proposal_id)
        return pdir / "04_proposal" / "sections.json"

    def _pipeline_load_sections(self, proposal_id: str) -> Dict[str, Any]:
        """加载申请书章节（纯读，不加锁）。"""
        # v6.7.8: 读取时支持 lifecycle 目录回退
        pdir = self._pipeline_read_dir(proposal_id)
        path = pdir / "04_proposal" / "sections.json"
        data = load_json(path, default=None)
        if not isinstance(data, dict) or "sections" not in data:
            # 兼容旧格式：如果没有 sections.json，尝试从 proposal-draft.md 解析
            draft_path = pdir / "04_proposal" / "proposal-draft.md"
            if draft_path.exists():
                return self._pipeline_parse_draft_to_sections(proposal_id, draft_path)
            return {"sections": {}, "updated_at": ""}
        return data

    def _pipeline_parse_draft_to_sections(
        self, proposal_id: str, draft_path: Path
    ) -> Dict[str, Any]:
        """将 proposal-draft.md 解析为 sections.json 兼容结构。"""
        try:
            text = draft_path.read_text(encoding="utf-8")
        except Exception:
            return {"sections": {}, "updated_at": ""}
        sections: Dict[str, Any] = {}
        current_name = None
        current_lines: List[str] = []
        for line in text.splitlines():
            if line.startswith("# ") and not line.startswith("## "):
                if current_name is not None:
                    sections[current_name] = {
                        "content": "\n".join(current_lines).strip(),
                        "updated_at": "",
                    }
                current_name = line[2:].strip()
                current_lines = []
            elif current_name is not None:
                current_lines.append(line)
        if current_name is not None:
            sections[current_name] = {
                "content": "\n".join(current_lines).strip(),
                "updated_at": "",
            }
        return {"sections": sections, "updated_at": ""}

    def _pipeline_save_sections(self, proposal_id: str, data: Dict[str, Any]) -> None:
        """保存申请书章节（原子写入 + 文件锁）。"""
        path = self._pipeline_sections_path(proposal_id)
        lock_key = f"pipeline-sections-{safe_filename(proposal_id)}"
        with file_lock(lock_key):
            data["updated_at"] = now_utc()
            save_json(path, data)

    def _pipeline_module_unavailable(self, module_name: str) -> None:
        """返回模块不可用的 501 响应。"""
        self._send_json({"error": f"{module_name} 模块尚未实现或加载失败"}, 501)

    def _get_agent_team(self):
        """懒加载 AgentTeam 实例。

        AgentTeam 为全局单例（状态存于 PIPELINE_CONFIG_DIR/agent-team.json），
        不依赖 proposal_id。模块不可用时发送 501 并返回 None。
        """
        try:
            from agent_team import AgentTeam
            return AgentTeam()
        except Exception as e:
            self._send_json({"error": f"Agent 团队模块不可用: {e}"}, status=501)
            return None

    def _get_methodology_manual(self, proposal_id: str):
        """懒加载 MethodologyManual 实例。

        proposal_id 经 _pipeline_proposal_dir 校验（防路径遍历），
        非法时抛 ValueError 由分派器捕获返回 400。
        模块不可用时发送 501 并返回 None。
        """
        proposal_dir = self._pipeline_proposal_dir(proposal_id)
        try:
            from methodology_manual import MethodologyManual
            return MethodologyManual(proposal_dir)
        except Exception as e:
            self._send_json({"error": f"方法学手册模块不可用: {e}"}, status=501)
            return None

    # ------------------------------------------------------------------
    # 路由分发
    # ------------------------------------------------------------------
    def _dispatch_pipeline_routes(self, method, path, parsed, body=None):
        """研究管线路由表分发。返回 True 表示已处理。"""
        for m, compiled_re, handler_name in _PIPELINE_ROUTES:
            if m != method:
                continue
            match = compiled_re.match(path)
            if match:
                handler = getattr(self, handler_name, None)
                if handler:
                    try:
                        if body is not None:
                            handler(path, parsed, body, match)
                        else:
                            handler(path, parsed, match)
                    except ValueError as e:
                        # 路径遍历等安全校验失败
                        self._send_json({"error": str(e)}, 400)
                    return True
        return False

    # ==================================================================
    # GET handlers — 管线编排
    # ==================================================================

    def _pl_get_stages(self, path, parsed, match):
        """获取所有阶段定义（静态，无需 proposal_id）"""
        mod = self._pipeline_load_module("pipeline_orchestrator")
        if mod is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        stages = mod.STAGES
        gates = mod.GATES
        self._send_json({"stages": stages, "gates": gates})

    def _pl_get_state(self, path, parsed, match):
        """获取管线状态"""
        proposal_id = match.group(1)
        mgr = self._pipeline_get_manager(proposal_id)
        if mgr is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        self._send_json({"status": "ok", "data": mgr.get_state()})

    def _pl_get_progress(self, path, parsed, match):
        """获取进度摘要"""
        proposal_id = match.group(1)
        mgr = self._pipeline_get_manager(proposal_id)
        if mgr is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        self._send_json({"status": "ok", "data": mgr.get_progress()})

    def _pl_get_timeline(self, path, parsed, match):
        """获取执行时间线"""
        proposal_id = match.group(1)
        mgr = self._pipeline_get_manager(proposal_id)
        if mgr is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        self._send_json({"status": "ok", "data": mgr.export_timeline()})

    def _pl_get_artifacts(self, path, parsed, match):
        """列出产物（可选 ?stage=N 过滤）"""
        proposal_id = match.group(1)
        qs = parse_qs(parsed.query)
        stage = None
        if "stage" in qs:
            try:
                stage = int(qs["stage"][0])
            except (ValueError, IndexError):
                self._send_json({"error": "stage 参数必须为整数"}, 400)
                return
        mgr = self._pipeline_get_manager(proposal_id)
        if mgr is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        self._send_json({"status": "ok", "data": mgr.list_artifacts(stage=stage)})

    # ==================================================================
    # GET handlers — 缺口分析
    # ==================================================================

    def _pl_get_gaps(self, path, parsed, match):
        """获取缺口报告"""
        proposal_id = match.group(1)
        analyzer = self._pipeline_get_gap_analyzer(proposal_id)
        if analyzer is None:
            self._pipeline_module_unavailable("gap_analyzer")
            return
        report = analyzer.get_gap_report()
        if report is None:
            self._send_json({"error": "缺口报告不存在，请先执行分析"}, 404)
            return
        self._send_json({"status": "ok", "data": report})

    def _pl_get_gaps_export(self, path, parsed, match):
        """导出缺口报告（?format=markdown|json）"""
        proposal_id = match.group(1)
        qs = parse_qs(parsed.query)
        fmt = qs.get("format", ["markdown"])[0]
        if fmt not in ("markdown", "json"):
            self._send_json({"error": "format 仅支持 markdown 或 json"}, 400)
            return
        analyzer = self._pipeline_get_gap_analyzer(proposal_id)
        if analyzer is None:
            self._pipeline_module_unavailable("gap_analyzer")
            return
        content = analyzer.export_gap_report(fmt)
        self._send_json({"status": "ok", "format": fmt, "content": content})

    # ==================================================================
    # GET handlers — 课题生成
    # ==================================================================

    def _pl_get_topics(self, path, parsed, match):
        """列出所有课题"""
        proposal_id = match.group(1)
        gen = self._pipeline_get_topic_generator(proposal_id)
        if gen is None:
            self._pipeline_module_unavailable("topic_generator")
            return
        self._send_json({"status": "ok", "data": gen.get_topics()})

    def _pl_get_topics_export(self, path, parsed, match):
        """导出课题列表（?format=markdown|json）"""
        proposal_id = match.group(1)
        qs = parse_qs(parsed.query)
        fmt = qs.get("format", ["markdown"])[0]
        if fmt not in ("markdown", "json"):
            self._send_json({"error": "format 仅支持 markdown 或 json"}, 400)
            return
        gen = self._pipeline_get_topic_generator(proposal_id)
        if gen is None:
            self._pipeline_module_unavailable("topic_generator")
            return
        content = gen.export_topics(fmt)
        self._send_json({"status": "ok", "format": fmt, "content": content})

    def _pl_get_topic(self, path, parsed, match):
        """获取单个课题"""
        proposal_id, topic_id = match.group(1), match.group(2)
        gen = self._pipeline_get_topic_generator(proposal_id)
        if gen is None:
            self._pipeline_module_unavailable("topic_generator")
            return
        topic = gen.get_topic(topic_id)
        if topic is None:
            self._send_json({"error": f"课题不存在: {topic_id}"}, 404)
            return
        self._send_json({"status": "ok", "data": topic})

    # ==================================================================
    # GET handlers — 问题构建
    # ==================================================================

    def _pl_get_questions(self, path, parsed, match):
        """获取问题框架"""
        proposal_id = match.group(1)
        arch = self._pipeline_get_question_architect(proposal_id)
        if arch is None:
            self._pipeline_module_unavailable("question_architect")
            return
        self._send_json({"status": "ok", "data": arch.get_framework()})

    def _pl_get_questions_export(self, path, parsed, match):
        """导出问题框架（?format=markdown|json）"""
        proposal_id = match.group(1)
        qs = parse_qs(parsed.query)
        fmt = qs.get("format", ["markdown"])[0]
        if fmt not in ("markdown", "json"):
            self._send_json({"error": "format 仅支持 markdown 或 json"}, 400)
            return
        arch = self._pipeline_get_question_architect(proposal_id)
        if arch is None:
            self._pipeline_module_unavailable("question_architect")
            return
        content = arch.export_framework(fmt)
        self._send_json({"status": "ok", "format": fmt, "content": content})

    def _pl_get_question(self, path, parsed, match):
        """获取单个问题"""
        proposal_id, question_id = match.group(1), match.group(2)
        arch = self._pipeline_get_question_architect(proposal_id)
        if arch is None:
            self._pipeline_module_unavailable("question_architect")
            return
        question = arch.get_question(question_id)
        if question is None:
            self._send_json({"error": f"问题不存在: {question_id}"}, 404)
            return
        self._send_json({"status": "ok", "data": question})

    # ==================================================================
    # GET handlers — 申请书
    # ==================================================================

    def _pl_get_sections(self, path, parsed, match):
        """列出所有章节"""
        proposal_id = match.group(1)
        data = self._pipeline_load_sections(proposal_id)
        sections = data.get("sections", {})
        # 返回章节名 + 元信息（不含正文，减少传输量）
        summary = [
            {
                "name": name,
                "updated_at": info.get("updated_at", "") if isinstance(info, dict) else "",
                "char_count": len(info.get("content", "")) if isinstance(info, dict) else len(str(info)),
            }
            for name, info in sections.items()
        ]
        self._send_json({"status": "ok", "data": summary, "updated_at": data.get("updated_at", "")})

    def _pl_get_section(self, path, parsed, match):
        """获取单个章节"""
        proposal_id, section_name = match.group(1), match.group(2)
        data = self._pipeline_load_sections(proposal_id)
        sections = data.get("sections", {})
        if section_name not in sections:
            self._send_json({"error": f"章节不存在: {section_name}"}, 404)
            return
        self._send_json({"status": "ok", "data": sections[section_name]})

    def _pl_get_proposal_export(self, path, parsed, match):
        """导出申请书（?format=markdown|json）"""
        proposal_id = match.group(1)
        qs = parse_qs(parsed.query)
        fmt = qs.get("format", ["markdown"])[0]
        if fmt not in ("markdown", "json"):
            self._send_json({"error": "format 仅支持 markdown 或 json"}, 400)
            return
        data = self._pipeline_load_sections(proposal_id)
        sections = data.get("sections", {})
        if fmt == "json":
            import json
            content = json.dumps(sections, ensure_ascii=False, indent=2)
        else:
            lines: List[str] = []
            for name, info in sections.items():
                content_text = info.get("content", "") if isinstance(info, dict) else str(info)
                lines.append(f"# {name}\n")
                lines.append(content_text)
                lines.append("")
            content = "\n".join(lines)
        self._send_json({"status": "ok", "format": fmt, "content": content})

    def _pl_get_proposal_progress(self, path, parsed, match):
        """获取撰写进度"""
        proposal_id = match.group(1)
        data = self._pipeline_load_sections(proposal_id)
        sections = data.get("sections", {})
        completed = [name for name in _EXPECTED_SECTIONS if name in sections]
        missing = [name for name in _EXPECTED_SECTIONS if name not in sections]
        total = len(_EXPECTED_SECTIONS)
        pct = round(len(completed) / total * 100, 1) if total else 0.0
        self._send_json({
            "status": "ok",
            "data": {
                "completed_sections": completed,
                "missing_sections": missing,
                "completion_pct": pct,
                "total_expected": total,
                "total_completed": len(completed),
            },
        })

    # ==================================================================
    # GET handlers — 自检优化
    # ==================================================================

    def _pl_get_inspection_report(self, path, parsed, match):
        """获取最新自检报告"""
        proposal_id = match.group(1)
        inspector = self._pipeline_get_inspector(proposal_id)
        if inspector is None:
            self._pipeline_module_unavailable("proposal_inspector")
            return
        report = inspector.get_inspection_report()
        if not report:
            self._send_json({"error": "自检报告不存在，请先执行自检"}, 404)
            return
        self._send_json({"status": "ok", "data": report})

    def _pl_get_inspection_history(self, path, parsed, match):
        """获取迭代历史"""
        proposal_id = match.group(1)
        inspector = self._pipeline_get_inspector(proposal_id)
        if inspector is None:
            self._pipeline_module_unavailable("proposal_inspector")
            return
        self._send_json({"status": "ok", "data": inspector.get_iteration_history()})

    def _pl_get_inspection_export(self, path, parsed, match):
        """导出自检报告（?format=markdown|json）"""
        proposal_id = match.group(1)
        qs = parse_qs(parsed.query)
        fmt = qs.get("format", ["markdown"])[0]
        if fmt not in ("markdown", "json"):
            self._send_json({"error": "format 仅支持 markdown 或 json"}, 400)
            return
        inspector = self._pipeline_get_inspector(proposal_id)
        if inspector is None:
            self._pipeline_module_unavailable("proposal_inspector")
            return
        content = inspector.export_report(fmt)
        self._send_json({"status": "ok", "format": fmt, "content": content})

    # ==================================================================
    # GET handlers — 引文管理
    # ==================================================================

    def _pl_get_citations(self, path, parsed, match):
        """列出所有参考文献"""
        proposal_id = match.group(1)
        cm = self._pipeline_get_citation_manager(proposal_id)
        if cm is None:
            self._pipeline_module_unavailable("citation_manager")
            return
        self._send_json({"status": "ok", "data": cm.list_references()})

    def _pl_get_citations_export(self, path, parsed, match):
        """导出参考文献目录（?format=json|markdown|bibtex）"""
        proposal_id = match.group(1)
        qs = parse_qs(parsed.query)
        fmt = qs.get("format", ["json"])[0]
        if fmt not in ("json", "markdown", "bibtex"):
            self._send_json({"error": "format 仅支持 json、markdown 或 bibtex"}, 400)
            return
        cm = self._pipeline_get_citation_manager(proposal_id)
        if cm is None:
            self._pipeline_module_unavailable("citation_manager")
            return
        content = cm.export_bibliography(fmt)
        self._send_json({"status": "ok", "format": fmt, "content": content})

    def _pl_get_citations_stats(self, path, parsed, match):
        """获取引文统计"""
        proposal_id = match.group(1)
        cm = self._pipeline_get_citation_manager(proposal_id)
        if cm is None:
            self._pipeline_module_unavailable("citation_manager")
            return
        self._send_json({"status": "ok", "data": cm.get_stats()})

    # ==================================================================
    # POST handlers — 管线编排
    # ==================================================================

    def _pl_post_advance(self, path, parsed, body, match):
        """推进到下一阶段"""
        proposal_id = match.group(1)
        mgr = self._pipeline_get_manager(proposal_id)
        if mgr is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        result = mgr.advance_stage()
        if not result.get("advanced"):
            # 推进被阻塞（暂停态/已完成/门禁未通过）→ 409 冲突
            self._send_json({"status": "ok", "data": result}, 409)
            return
        self._send_json({"status": "ok", "data": result})

    def _pl_post_gate(self, path, parsed, body, match):
        """执行门禁评审"""
        proposal_id, stage_str = match.group(1), match.group(2)
        try:
            stage = int(stage_str)
        except ValueError:
            self._send_json({"error": f"门禁编号必须为整数: {stage_str}"}, 400)
            return
        review_type = body.get("review_type", "rule") if body else "rule"
        mgr = self._pipeline_get_manager(proposal_id)
        if mgr is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        result = mgr.run_gate(stage, review_type)
        self._send_json({"status": "ok", "data": result})

    def _pl_post_rollback(self, path, parsed, body, match):
        """回滚到上一阶段"""
        proposal_id = match.group(1)
        reason = (body.get("reason", "") if body else "").strip()
        if not reason:
            self._send_json({"error": "回滚必须填写原因"}, 400)
            return
        mgr = self._pipeline_get_manager(proposal_id)
        if mgr is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        result = mgr.rollback_stage(reason)
        if not result.get("rolled_back"):
            self._send_json({"status": "ok", "data": result}, 409)
            return
        self._send_json({"status": "ok", "data": result})

    def _pl_post_pause(self, path, parsed, body, match):
        """暂停管线"""
        proposal_id = match.group(1)
        reason = (body.get("reason", "") if body else "").strip()
        mgr = self._pipeline_get_manager(proposal_id)
        if mgr is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        result = mgr.pause(reason)
        self._send_json({"status": "ok", "data": result})

    def _pl_post_resume(self, path, parsed, body, match):
        """恢复管线"""
        proposal_id = match.group(1)
        mgr = self._pipeline_get_manager(proposal_id)
        if mgr is None:
            self._pipeline_module_unavailable("pipeline_orchestrator")
            return
        result = mgr.resume()
        self._send_json({"status": "ok", "data": result})

    # ==================================================================
    # POST handlers — 缺口分析
    # ==================================================================

    def _pl_post_gaps_analyze(self, path, parsed, body, match):
        """执行缺口分析

        body 可选字段：
            research_directions: [{"id": "T1", "name": "量子几何"}, ...]
        """
        proposal_id = match.group(1)
        directions = []
        if body and isinstance(body.get("research_directions"), list):
            directions = body["research_directions"]
        analyzer = self._pipeline_get_gap_analyzer(proposal_id, directions)
        if analyzer is None:
            self._pipeline_module_unavailable("gap_analyzer")
            return
        report = analyzer.analyze()
        self._send_json({"status": "ok", "data": report})

    # ==================================================================
    # POST handlers — 课题生成
    # ==================================================================

    def _pl_post_topics_generate(self, path, parsed, body, match):
        """从缺口生成课题

        body 可选字段：
            direction: {"id": "T1", "name": "量子几何"}
            max_topics: int (默认 10)
        """
        proposal_id = match.group(1)
        direction = body.get("direction") if body else None
        max_topics = body.get("max_topics", 10) if body else 10
        gen = self._pipeline_get_topic_generator(proposal_id)
        if gen is None:
            self._pipeline_module_unavailable("topic_generator")
            return
        # 从已保存的缺口报告加载
        analyzer = self._pipeline_get_gap_analyzer(proposal_id)
        if analyzer is None:
            self._pipeline_module_unavailable("gap_analyzer")
            return
        gap_report = analyzer.get_gap_report()
        if gap_report is None:
            self._send_json({"error": "缺口报告不存在，请先执行缺口分析"}, 404)
            return
        topics = gen.generate_topics(gap_report, direction=direction, max_topics=max_topics)
        self._send_json({"status": "ok", "data": topics})

    def _pl_post_topic_select(self, path, parsed, body, match):
        """选定课题"""
        proposal_id, topic_id = match.group(1), match.group(2)
        gen = self._pipeline_get_topic_generator(proposal_id)
        if gen is None:
            self._pipeline_module_unavailable("topic_generator")
            return
        try:
            topic = gen.select_topic(topic_id)
            self._send_json({"status": "ok", "data": topic})
        except KeyError:
            self._send_json({"error": f"课题不存在: {topic_id}"}, 404)

    def _pl_post_topic_refine(self, path, parsed, body, match):
        """精炼课题

        body 字段：title / title_en / research_question / rationale /
                   novelty_score / feasibility_score / status
        """
        proposal_id, topic_id = match.group(1), match.group(2)
        gen = self._pipeline_get_topic_generator(proposal_id)
        if gen is None:
            self._pipeline_module_unavailable("topic_generator")
            return
        try:
            topic = gen.refine_topic(topic_id, body or {})
            self._send_json({"status": "ok", "data": topic})
        except KeyError:
            self._send_json({"error": f"课题不存在: {topic_id}"}, 404)

    # ==================================================================
    # POST handlers — 问题构建
    # ==================================================================

    def _pl_post_questions_construct(self, path, parsed, body, match):
        """构建科学问题框架

        body 必填：topic（课题字典）
        body 可选：gap_report（缺口报告字典）
        """
        proposal_id = match.group(1)
        topic = body.get("topic") if body else None
        if not topic or not isinstance(topic, dict):
            self._send_json({"error": "缺少 topic 字段或格式错误"}, 400)
            return
        gap_report = body.get("gap_report")
        arch = self._pipeline_get_question_architect(proposal_id)
        if arch is None:
            self._pipeline_module_unavailable("question_architect")
            return
        try:
            framework = arch.construct_questions(topic, gap_report=gap_report)
            self._send_json({"status": "ok", "data": framework})
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    def _pl_post_question_refine(self, path, parsed, body, match):
        """精修问题

        body 字段：text / hypothesis / element / type / evidence_add / status
        """
        proposal_id, question_id = match.group(1), match.group(2)
        arch = self._pipeline_get_question_architect(proposal_id)
        if arch is None:
            self._pipeline_module_unavailable("question_architect")
            return
        try:
            question = arch.refine_question(question_id, body or {})
            self._send_json({"status": "ok", "data": question})
        except KeyError:
            self._send_json({"error": f"问题不存在: {question_id}"}, 404)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    # ==================================================================
    # POST handlers — 申请书
    # ==================================================================

    def _pl_post_proposal_write(self, path, parsed, body, match):
        """撰写完整申请书（委派 proposal_writer 模块）

        body 可选：question_framework / sections / options
        """
        proposal_id = match.group(1)
        mod = self._pipeline_load_module("proposal_writer")
        if mod is None:
            self._pipeline_module_unavailable("proposal_writer")
            return
        pdir = self._pipeline_ensure_dirs(proposal_id)
        try:
            writer = mod.ProposalWriter(pdir)
            result = writer.write_proposal(
                question_framework=body.get("question_framework") if body else None,
                sections=body.get("sections") if body else None,
                options=body.get("options") if body else None,
            )
            self._send_json({"status": "ok", "data": result})
        except Exception as e:
            self._send_json({"error": f"撰写申请书失败: {e}"}, 500)

    def _pl_post_section(self, path, parsed, body, match):
        """写入单个章节

        body 必填：content（章节正文）
        """
        proposal_id, section_name = match.group(1), match.group(2)
        if not body or "content" not in body:
            self._send_json({"error": "缺少 content 字段"}, 400)
            return
        content = body["content"]
        if not isinstance(content, str):
            self._send_json({"error": "content 必须为字符串"}, 400)
            return
        data = self._pipeline_load_sections(proposal_id)
        sections = data.setdefault("sections", {})
        sections[section_name] = {
            "content": content,
            "updated_at": now_utc(),
        }
        self._pipeline_save_sections(proposal_id, data)
        self._send_json({"status": "ok", "data": sections[section_name]})

    # ==================================================================
    # GET handlers — Agent 团队管理
    # ==================================================================

    def _pl_get_agents(self, path, parsed, match):
        """获取完整团队结构（含分层 core/support/growth）"""
        team = self._get_agent_team()
        if team is None:
            return
        self._send_json({"status": "ok", "data": team.get_team()})

    def _pl_get_agents_overview(self, path, parsed, match):
        """获取团队概览统计（总数/各状态计数/分层分布）"""
        team = self._get_agent_team()
        if team is None:
            return
        self._send_json({"status": "ok", "data": team.get_team_overview()})

    def _pl_get_agents_performance(self, path, parsed, match):
        """获取团队整体性能汇总"""
        team = self._get_agent_team()
        if team is None:
            return
        self._send_json({"status": "ok", "data": team.get_team_performance()})

    def _pl_get_agent(self, path, parsed, match):
        """获取单个智能体详情"""
        agent_id = match.group(1)
        team = self._get_agent_team()
        if team is None:
            return
        agent = team.get_agent(agent_id)
        if agent is None:
            self._send_json({"error": f"智能体不存在: {agent_id}"}, 404)
            return
        self._send_json({"status": "ok", "data": agent})

    # ==================================================================
    # POST handlers — Agent 团队管理
    # ==================================================================

    def _pl_post_agent_add(self, path, parsed, body, match):
        """添加新智能体（团队成长）

        body 必填：name、role
        body 可选：name_en、description、capabilities、icon、tier、
                   delegate_module、stage、status
        """
        if not body:
            self._send_json({"error": "请求体不能为空"}, 400)
            return
        team = self._get_agent_team()
        if team is None:
            return
        try:
            agent = team.add_agent(body)
            self._send_json({"status": "ok", "data": agent})
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    def _pl_post_agent_status(self, path, parsed, body, match):
        """更新智能体状态

        body 必填：status（idle/working/blocked/offline）
        body 可选：current_task（任务描述）
        """
        agent_id = match.group(1)
        if not body or "status" not in body:
            self._send_json({"error": "缺少 status 字段"}, 400)
            return
        status = body["status"]
        current_task = body.get("current_task")
        team = self._get_agent_team()
        if team is None:
            return
        try:
            agent = team.update_agent_status(
                agent_id, status, current_task=current_task
            )
            self._send_json({"status": "ok", "data": agent})
        except KeyError:
            self._send_json({"error": f"智能体不存在: {agent_id}"}, 404)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    def _pl_post_agent_assign(self, path, parsed, body, match):
        """向智能体分配任务（状态置为 working）

        body 必填：task（任务描述）
        """
        agent_id = match.group(1)
        if not body or "task" not in body:
            self._send_json({"error": "缺少 task 字段"}, 400)
            return
        task = body["task"]
        team = self._get_agent_team()
        if team is None:
            return
        try:
            agent = team.assign_task(agent_id, task)
            self._send_json({"status": "ok", "data": agent})
        except KeyError:
            self._send_json({"error": f"智能体不存在: {agent_id}"}, 404)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    def _pl_post_agent_complete(self, path, parsed, body, match):
        """完成智能体当前任务，记录性能指标，状态置为 idle

        body 必填：success（bool）、duration_s（float，秒）
        """
        agent_id = match.group(1)
        if not body or "success" not in body or "duration_s" not in body:
            self._send_json({"error": "缺少 success 或 duration_s 字段"}, 400)
            return
        success = body["success"]
        try:
            duration_s = float(body["duration_s"])
        except (TypeError, ValueError):
            self._send_json({"error": "duration_s 必须为数字"}, 400)
            return
        team = self._get_agent_team()
        if team is None:
            return
        try:
            agent = team.complete_task(
                agent_id, success=success, duration_s=duration_s
            )
            self._send_json({"status": "ok", "data": agent})
        except KeyError:
            self._send_json({"error": f"智能体不存在: {agent_id}"}, 404)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    def _pl_post_agent_upgrade(self, path, parsed, body, match):
        """升级智能体（添加新能力，可选更新委派模块）

        body 必填：capabilities（能力列表）
        body 可选：delegate_module（新委派模块名）
        """
        agent_id = match.group(1)
        if not body or "capabilities" not in body:
            self._send_json({"error": "缺少 capabilities 字段"}, 400)
            return
        capabilities = body["capabilities"]
        delegate_module = body.get("delegate_module")
        team = self._get_agent_team()
        if team is None:
            return
        try:
            agent = team.upgrade_agent(
                agent_id, capabilities, new_delegate_module=delegate_module
            )
            self._send_json({"status": "ok", "data": agent})
        except KeyError:
            self._send_json({"error": f"智能体不存在: {agent_id}"}, 404)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    def _pl_post_agent_activate(self, path, parsed, body, match):
        """激活成长槽位（绑定委派模块、注入能力、offline→idle）

        body 必填：delegate_module、capabilities
        """
        agent_id = match.group(1)
        if not body or "delegate_module" not in body or "capabilities" not in body:
            self._send_json(
                {"error": "缺少 delegate_module 或 capabilities 字段"}, 400
            )
            return
        delegate_module = body["delegate_module"]
        capabilities = body["capabilities"]
        team = self._get_agent_team()
        if team is None:
            return
        try:
            agent = team.activate_growth_slot(
                agent_id, delegate_module, capabilities
            )
            self._send_json({"status": "ok", "data": agent})
        except KeyError:
            self._send_json({"error": f"智能体不存在: {agent_id}"}, 404)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    # ==================================================================
    # GET handlers — 方法学手册
    # ==================================================================

    def _pl_get_methodology(self, path, parsed, match):
        """获取方法学手册"""
        proposal_id = match.group(1)
        manual = self._get_methodology_manual(proposal_id)
        if manual is None:
            return
        handbook = manual.get_handbook()
        if handbook is None:
            self._send_json({"error": "方法学手册不存在，请先生成"}, 404)
            return
        self._send_json({"status": "ok", "data": handbook})

    def _pl_get_methodology_export(self, path, parsed, match):
        """导出方法学手册（?format=markdown|json）"""
        proposal_id = match.group(1)
        qs = parse_qs(parsed.query)
        fmt = qs.get("format", ["markdown"])[0]
        if fmt not in ("markdown", "json"):
            self._send_json({"error": "format 仅支持 markdown 或 json"}, 400)
            return
        manual = self._get_methodology_manual(proposal_id)
        if manual is None:
            return
        content = manual.export_handbook(fmt)
        self._send_json({"status": "ok", "format": fmt, "content": content})

    def _pl_get_methodology_stats(self, path, parsed, match):
        """获取方法学手册统计信息"""
        proposal_id = match.group(1)
        manual = self._get_methodology_manual(proposal_id)
        if manual is None:
            return
        self._send_json({"status": "ok", "data": manual.get_handbook_stats()})

    # ==================================================================
    # POST handlers — 方法学手册
    # ==================================================================

    def _pl_post_methodology_generate(self, path, parsed, body, match):
        """从申请书章节生成方法学手册

        body 必填：proposal_sections（章节字典，
                   {section_name: {"content": "..."}} 或 {section_name: "..."}）
        body 可选：gap_report（缺口报告字典，用于补充方法缺口）
        """
        proposal_id = match.group(1)
        if not body or "proposal_sections" not in body:
            self._send_json({"error": "缺少 proposal_sections 字段"}, 400)
            return
        proposal_sections = body["proposal_sections"]
        gap_report = body.get("gap_report")
        manual = self._get_methodology_manual(proposal_id)
        if manual is None:
            return
        try:
            handbook = manual.generate_handbook(
                proposal_sections, gap_report=gap_report
            )
            self._send_json({"status": "ok", "data": handbook})
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)
        except Exception as e:
            self._send_json({"error": f"生成方法学手册失败: {e}"}, 500)

    # ==================================================================
    # PUT handlers — 方法学手册
    # ==================================================================

    def _pl_put_methodology_update(self, path, parsed, body, match):
        """更新方法条目

        body 必填：updates（更新字段字典，可含 theoretical_background、
                   implementation_details、data_analysis、limitations、
                   key_references、status 等）
        URL 参数：method_name（方法名称，中文名或英文名）
        """
        proposal_id, method_name = match.group(1), match.group(2)
        if not body or "updates" not in body:
            self._send_json({"error": "缺少 updates 字段"}, 400)
            return
        updates = body["updates"]
        if not isinstance(updates, dict):
            self._send_json({"error": "updates 必须为字典"}, 400)
            return
        manual = self._get_methodology_manual(proposal_id)
        if manual is None:
            return
        try:
            entry = manual.update_method_entry(method_name, updates)
            self._send_json({"status": "ok", "data": entry})
        except KeyError:
            self._send_json({"error": f"方法条目不存在: {method_name}"}, 404)
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    # ==================================================================
    # POST handlers — 自检优化
    # ==================================================================

    def _pl_post_inspection_run(self, path, parsed, body, match):
        """执行自检

        body 可选：
            sections: {章节名: markdown 文本}（不提供时从已保存章节加载）
            question_framework: 问题框架字典
        """
        proposal_id = match.group(1)
        sections = body.get("sections") if body else None
        if not sections:
            # 从已保存章节加载
            data = self._pipeline_load_sections(proposal_id)
            stored = data.get("sections", {})
            sections = {
                name: (info.get("content", "") if isinstance(info, dict) else str(info))
                for name, info in stored.items()
            }
        if not sections:
            self._send_json({"error": "无章节可检查，请先撰写申请书章节"}, 400)
            return
        question_framework = body.get("question_framework") if body else None
        inspector = self._pipeline_get_inspector(proposal_id)
        if inspector is None:
            self._pipeline_module_unavailable("proposal_inspector")
            return
        report = inspector.inspect(sections, question_framework=question_framework)
        self._send_json({"status": "ok", "data": report})

    # ==================================================================
    # POST handlers — 引文管理
    # ==================================================================

    def _pl_post_citation(self, path, parsed, body, match):
        """添加参考文献

        body 必填：type, title
        body 可选：authors, year, venue, doi, arxiv_id, abstract, source ...
        """
        proposal_id = match.group(1)
        if not body:
            self._send_json({"error": "请求体不能为空"}, 400)
            return
        cm = self._pipeline_get_citation_manager(proposal_id)
        if cm is None:
            self._pipeline_module_unavailable("citation_manager")
            return
        try:
            cite_key = cm.add_reference(body)
            self._send_json({"status": "ok", "cite_key": cite_key})
        except ValueError as e:
            self._send_json({"error": str(e)}, 400)

    # ==================================================================
    # PUT handlers — 申请书
    # ==================================================================

    def _pl_put_section(self, path, parsed, body, match):
        """更新单个章节

        body 必填：content（章节正文）
        """
        proposal_id, section_name = match.group(1), match.group(2)
        if not body or "content" not in body:
            self._send_json({"error": "缺少 content 字段"}, 400)
            return
        content = body["content"]
        if not isinstance(content, str):
            self._send_json({"error": "content 必须为字符串"}, 400)
            return
        data = self._pipeline_load_sections(proposal_id)
        sections = data.setdefault("sections", {})
        sections[section_name] = {
            "content": content,
            "updated_at": now_utc(),
        }
        self._pipeline_save_sections(proposal_id, data)
        self._send_json({"status": "ok", "data": sections[section_name]})

    # ==================================================================
    # Hermes 驱动管线 handlers（v6.4.1）
    # ==================================================================

    def _pl_hermes_list_importable(self, path, parsed, match):
        """列出可导入的已有 proposal（hermes_workspace）"""
        try:
            from hermes_pipeline import HermesPipeline
            pipe = HermesPipeline("__tmp__")
            proposals = pipe.list_importable_proposals()
            import shutil
            shutil.rmtree(pipe.proposal_dir, ignore_errors=True)
            self._send_json({"status": "ok", "proposals": proposals})
        except ImportError:
            self._send_json({"error": "hermes_pipeline 模块不可用"}, 500)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _pl_hermes_status(self, path, parsed, match):
        """获取 hermes 管线状态"""
        proposal_id = match.group(1)
        try:
            from hermes_pipeline import HermesPipeline
            pipe = HermesPipeline(proposal_id)
            status = pipe.get_status()
            self._send_json({"status": "ok", "data": status})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _pl_hermes_check_stage(self, path, parsed, match):
        """检查指定阶段的产物状态"""
        proposal_id, stage_str = match.group(1), match.group(2)
        try:
            stage = int(stage_str)
            from hermes_pipeline import HermesPipeline
            pipe = HermesPipeline(proposal_id)
            result = pipe.check_stage(stage)
            self._send_json({"status": "ok", "data": result})
        except ValueError:
            self._send_json({"error": f"非法阶段编号: {stage_str}"}, 400)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _pl_hermes_import(self, path, parsed, body, match):
        """从 hermes_workspace 导入已有 proposal

        body 必填：source_name（hermes_workspace/research_proposals/ 下的目录名）
        body 可选：max_files（最大导入文件数，默认 50）
        """
        proposal_id = match.group(1)
        if not body or "source_name" not in body:
            self._send_json({"error": "缺少 source_name 字段"}, 400)
            return
        source_name = body["source_name"]
        max_files = body.get("max_files", 50)
        try:
            from hermes_pipeline import HermesPipeline
            pipe = HermesPipeline(proposal_id)
            result = pipe.import_existing_proposal(source_name, max_files=max_files)
            self._send_json({"status": "ok", "data": result})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _pl_hermes_dispatch(self, path, parsed, body, match):
        """派活指定阶段给 hermes profile

        body 可选：extra_context, timeout
        """
        proposal_id, stage_str = match.group(1), match.group(2)
        try:
            stage = int(stage_str)
            extra_context = (body or {}).get("extra_context", "")
            timeout = (body or {}).get("timeout", 600)
            from hermes_pipeline import HermesPipeline
            pipe = HermesPipeline(proposal_id)
            result = pipe.dispatch_stage(stage, extra_context=extra_context, timeout=timeout)
            self._send_json({"status": "ok", "data": result})
        except ValueError:
            self._send_json({"error": f"非法阶段编号: {stage_str}"}, 400)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _pl_hermes_run(self, path, parsed, body, match):
        """一键执行 hermes 全链路

        body 可选：timeout_per_stage（每阶段超时，默认 600s）
        """
        proposal_id = match.group(1)
        timeout_per_stage = (body or {}).get("timeout_per_stage", 600)
        try:
            from hermes_pipeline import HermesPipeline
            pipe = HermesPipeline(proposal_id)
            result = pipe.run_pipeline(timeout_per_stage=timeout_per_stage)
            self._send_json({"status": "ok", "data": result})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _pl_hermes_setup_cron(self, path, parsed, body, match):
        """配置 hermes cron 自动触发

        body 可选：schedule（cron 表达式，默认每周一 09:00）, deliver
        """
        proposal_id = match.group(1)
        schedule = (body or {}).get("schedule", "0 9 * * 1")
        deliver = (body or {}).get("deliver", "local")
        try:
            from hermes_pipeline import HermesPipeline
            pipe = HermesPipeline(proposal_id)
            result = pipe.setup_cron(schedule=schedule, deliver=deliver)
            self._send_json({"status": "ok", "data": result})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _pl_hermes_list_research(self, path, parsed, match):
        """列出已有的针对性检索报告"""
        proposal_id = match.group(1)
        try:
            from hermes_pipeline import HermesPipeline
            pipe = HermesPipeline(proposal_id)
            reports = pipe.list_targeted_research()
            self._send_json({"status": "ok", "reports": reports})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _pl_hermes_research(self, path, parsed, body, match):
        """针对性检索（撰写时按需检索）

        body 必填：topic（检索主题）
        body 可选：context（撰写上下文）, depth（quick/standard/deep）, timeout
        """
        proposal_id = match.group(1)
        if not body or "topic" not in body:
            self._send_json({"error": "缺少 topic 字段"}, 400)
            return
        topic = body["topic"]
        context = body.get("context", "")
        depth = body.get("depth", "standard")
        timeout = body.get("timeout", 300)
        try:
            from hermes_pipeline import HermesPipeline
            pipe = HermesPipeline(proposal_id)
            result = pipe.targeted_research(topic, context=context, depth=depth, timeout=timeout)
            self._send_json({"status": "ok", "data": result})
        except Exception as e:
            self._send_json({"error": str(e)}, 500)


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def _self_check() -> bool:
    """自检：验证路由表完整性、路由匹配、路径参数提取、proposal_id 校验。

    不依赖真实管线模块，仅测试路由层逻辑。
    """
    import tempfile

    print("=" * 50)
    print("◐ web_routes_pipeline 自检")
    print("=" * 50)

    passed = 0
    total = 0
    tmp_dir = tempfile.mkdtemp(prefix="web_routes_pipeline_test_")

    # 构造一个最小 Mixin 实例用于测试（模拟 BaseRequestHandler 方法）
    class _FakeHandler(PipelineRoutesMixin):
        def __init__(self):
            self.last_response = None
            self.last_status = None

        def _send_json(self, data, status=200):
            self.last_response = data
            self.last_status = status

    try:
        handler = _FakeHandler()

        # [1/8] 路由表条目数
        total += 1
        route_count = len(_PIPELINE_ROUTES)
        if 50 <= route_count <= 60:
            passed += 1
            print(f"  [1/{8}] ✓ 路由数: {route_count}（期望 50-60）")
        else:
            print(f"  [1/{8}] ✗ 路由数: {route_count}（期望 50-60）")

        # [2/8] GET 路由数
        total += 1
        get_count = sum(1 for m, _, _ in _PIPELINE_ROUTES if m == "GET")
        if get_count >= 28:
            passed += 1
            print(f"  [2/{8}] ✓ GET 路由: {get_count} 条")
        else:
            print(f"  [2/{8}] ✗ GET 路由: {get_count} 条（期望 >= 28）")

        # [3/8] POST 路由数
        total += 1
        post_count = sum(1 for m, _, _ in _PIPELINE_ROUTES if m == "POST")
        if post_count >= 18:
            passed += 1
            print(f"  [3/{8}] ✓ POST 路由: {post_count} 条")
        else:
            print(f"  [3/{8}] ✗ POST 路由: {post_count} 条（期望 >= 18）")

        # [4/8] PUT 路由数
        total += 1
        put_count = sum(1 for m, _, _ in _PIPELINE_ROUTES if m == "PUT")
        if put_count >= 2:
            passed += 1
            print(f"  [4/{8}] ✓ PUT 路由: {put_count} 条")
        else:
            print(f"  [4/{8}] ✗ PUT 路由: {put_count} 条")

        # [5/8] 静态路由匹配（/api/pipeline/stages）
        total += 1
        matched = False
        for m, compiled_re, _ in _PIPELINE_ROUTES:
            if m == "GET" and compiled_re.match("/api/pipeline/stages"):
                matched = True
                break
        if matched:
            passed += 1
            print(f"  [5/{8}] ✓ 静态路由 /api/pipeline/stages 可匹配")
        else:
            print(f"  [5/{8}] ✗ 静态路由 /api/pipeline/stages 不可匹配")

        # [6/8] topics/export 不被 topics/{topic_id} 抢先匹配
        total += 1
        export_matched_handler = None
        for m, compiled_re, h_name in _PIPELINE_ROUTES:
            if m == "GET" and compiled_re.match("/api/pipeline/T1/topics/export"):
                export_matched_handler = h_name
                break
        if export_matched_handler == "_pl_get_topics_export":
            passed += 1
            print(f"  [6/{8}] ✓ /topics/export 路由优先匹配（handler={export_matched_handler}）")
        else:
            print(f"  [6/{8}] ✗ /topics/export 被错误匹配到 {export_matched_handler}")

        # [7/8] proposal_id 校验（路径遍历拦截）
        total += 1
        try:
            handler._validate_proposal_id("../etc/passwd")
            print(f"  [7/{8}] ✗ 路径遍历 proposal_id 未被拦截")
        except ValueError:
            passed += 1
            print(f"  [7/{8}] ✓ 路径遍历 proposal_id 已拦截")
        # 正常 ID 应通过
        total += 1
        try:
            handler._validate_proposal_id("T1")
            handler._validate_proposal_id("PRJ-20260726-测试")
            passed += 1
        except ValueError:
            print(f"  [7/{8}] ✗ 正常 proposal_id 被误拒")
        # 补充检查
        total += 1
        bad_count = 0
        for bad_id in ["", None, "a/b", "a\\b", "a..b"]:
            try:
                handler._validate_proposal_id(bad_id)
                bad_count += 1
            except (ValueError, TypeError):
                pass
        if bad_count == 0:
            passed += 1
            print(f"  [7/{8}] ✓ 正常 ID 通过，非法 ID 拦截")
        else:
            print(f"  [7/{8}] ✗ {bad_count} 个非法 ID 未被拦截")

        # [8/8] 分派器对未知路径返回 False
        total += 1
        from urllib.parse import urlparse
        parsed = urlparse("/api/pipeline/T1/nonexistent")
        result = handler._dispatch_pipeline_routes("GET", "/api/pipeline/T1/nonexistent", parsed)
        if result is False:
            passed += 1
            print(f"  [8/{8}] ✓ 未知路径正确返回 False")
        else:
            print(f"  [8/{8}] ✗ 未知路径应返回 False，实际 {result}")

        # [附加] 已知路径正确分发
        total += 1
        parsed2 = urlparse("/api/pipeline/T1/state")
        result2 = handler._dispatch_pipeline_routes("GET", "/api/pipeline/T1/state", parsed2)
        if result2 is True:
            passed += 1
            print(f"  [附加] ✓ /api/pipeline/T1/state 正确分发")
        else:
            print(f"  [附加] ✗ /api/pipeline/T1/state 未被分发")

        # [附加] Mixin 可被继承且方法存在
        total += 1
        required_methods = [
            "_dispatch_pipeline_routes", "_validate_proposal_id",
            "_pipeline_ensure_dirs", "_pipeline_get_manager",
            "_pl_get_state", "_pl_post_advance", "_pl_put_section",
            # Agent 团队管理
            "_get_agent_team", "_pl_get_agents", "_pl_get_agents_overview",
            "_pl_get_agents_performance", "_pl_get_agent",
            "_pl_post_agent_add", "_pl_post_agent_status", "_pl_post_agent_assign",
            "_pl_post_agent_complete", "_pl_post_agent_upgrade", "_pl_post_agent_activate",
            # 方法学手册
            "_get_methodology_manual", "_pl_get_methodology", "_pl_get_methodology_export",
            "_pl_get_methodology_stats", "_pl_post_methodology_generate",
            "_pl_put_methodology_update",
        ]
        all_present = all(hasattr(handler, m) for m in required_methods)
        if all_present:
            passed += 1
            print(f"  [附加] ✓ Mixin 方法完整（{len(required_methods)} 个核心方法）")
        else:
            missing = [m for m in required_methods if not hasattr(handler, m)]
            print(f"  [附加] ✗ 缺失方法: {missing}")

        # [附加] Agent 团队路由不被 proposal_id 路由抢先匹配
        total += 1
        agents_matched = None
        for m, compiled_re, h_name in _PIPELINE_ROUTES:
            if m == "GET" and compiled_re.match("/api/pipeline/agents"):
                agents_matched = h_name
                break
        if agents_matched == "_pl_get_agents":
            passed += 1
            print(f"  [附加] ✓ /api/pipeline/agents 正确匹配（handler={agents_matched}）")
        else:
            print(f"  [附加] ✗ /api/pipeline/agents 被错误匹配到 {agents_matched}")

        # [附加] /api/pipeline/agents/overview 不被 agents/{agent_id} 抢先匹配
        total += 1
        overview_matched = None
        for m, compiled_re, h_name in _PIPELINE_ROUTES:
            if m == "GET" and compiled_re.match("/api/pipeline/agents/overview"):
                overview_matched = h_name
                break
        if overview_matched == "_pl_get_agents_overview":
            passed += 1
            print(f"  [附加] ✓ /agents/overview 优先匹配（handler={overview_matched}）")
        else:
            print(f"  [附加] ✗ /agents/overview 被错误匹配到 {overview_matched}")

        # [附加] 方法学手册路由正确匹配
        total += 1
        methodology_matched = None
        for m, compiled_re, h_name in _PIPELINE_ROUTES:
            if m == "GET" and compiled_re.match("/api/pipeline/T1/methodology"):
                methodology_matched = h_name
                break
        if methodology_matched == "_pl_get_methodology":
            passed += 1
            print(f"  [附加] ✓ /T1/methodology 正确匹配（handler={methodology_matched}）")
        else:
            print(f"  [附加] ✗ /T1/methodology 被错误匹配到 {methodology_matched}")

        # [附加] 方法学手册 generate POST 路由正确匹配
        total += 1
        gen_matched = None
        for m, compiled_re, h_name in _PIPELINE_ROUTES:
            if m == "POST" and compiled_re.match("/api/pipeline/T1/methodology/generate"):
                gen_matched = h_name
                break
        if gen_matched == "_pl_post_methodology_generate":
            passed += 1
            print(f"  [附加] ✓ /T1/methodology/generate POST 正确匹配（handler={gen_matched}）")
        else:
            print(f"  [附加] ✗ /T1/methodology/generate POST 被错误匹配到 {gen_matched}")

        # [附加] 方法学手册 PUT 路由正确匹配
        total += 1
        put_matched = None
        for m, compiled_re, h_name in _PIPELINE_ROUTES:
            if m == "PUT" and compiled_re.match("/api/pipeline/T1/methodology/TDDFT"):
                put_matched = h_name
                break
        if put_matched == "_pl_put_methodology_update":
            passed += 1
            print(f"  [附加] ✓ /T1/methodology/TDDFT PUT 正确匹配（handler={put_matched}）")
        else:
            print(f"  [附加] ✗ /T1/methodology/TDDFT PUT 被错误匹配到 {put_matched}")

    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    ok = passed == total
    print(f"\n{'✓' if ok else '✗'} web_routes_pipeline: {passed}/{total} 通过")
    return ok


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="研究管线路由 Mixin")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        import sys
        sys.exit(0 if _self_check() else 1)
    else:
        parser.print_help()
